import os
import tempfile
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from python_code_analyzer_app.models import Repository, Analysis, Tool, AnalysisTool, CeleryTaskSignal
from python_code_analyzer_app.app_models import tools_status
from python_code_analyzer_app.app_models.TaskManager import TaskManager


class ExecuteAnalysisTaskTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        settings.BASE_PATH = self.temp_dir + "\\"
        self.user = User.objects.create_user("testuser")
        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git", owner=self.user, folder="test_repo"
        )
        os.makedirs(self.repo.path)
        self.tool = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        self.analysis = Analysis.objects.create(repository=self.repo)
        AnalysisTool.objects.create(analysis=self.analysis, tool=self.tool)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.object(Repository, 'download')
    @patch.object(Repository, 'get_last_commit')
    @patch.object(Analysis, 'run')
    def test_excecute_analysis_normal_flow(self, mock_run, mock_get_last_commit, mock_download):
        mock_get_last_commit.return_value = "abc123"
        result = TaskManager.excecute_analysis(self.analysis.id)
        self.assertTrue(result)
        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.commit, "abc123")
        mock_download.assert_called_once()
        mock_run.assert_called_once()

    def test_excecute_analysis_cancels_if_already_being_analyzed(self):
        Analysis.objects.create(
            repository=self.repo, status=tools_status.RUNNING
        )
        result = TaskManager.excecute_analysis(self.analysis.id)
        self.assertFalse(result)
        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.status, tools_status.CANCELLED)

    @patch.object(Repository, 'download')
    def test_excecute_analysis_sets_failed_on_exception(self, mock_download):
        mock_download.side_effect = Exception("git clone failed")
        result = TaskManager.excecute_analysis(self.analysis.id)
        self.assertFalse(result)
        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.status, tools_status.FAILED)
        self.assertIn("git clone failed", self.analysis.status_msg)

    @patch.object(Repository, 'download')
    @patch.object(Repository, 'get_last_commit')
    @patch.object(Analysis, 'run')
    def test_excecute_analysis_stops_if_cancelled_before_start(self, mock_run, mock_get_last_commit, mock_download):
        CeleryTaskSignal.objects.create(
            analysis=self.analysis,
            signal=CeleryTaskSignal.CANCEL_TASK,
            completed=False,
        )
        result = TaskManager.excecute_analysis(self.analysis.id)
        self.assertFalse(result)
        mock_download.assert_not_called()
        mock_run.assert_not_called()


class LaunchMassiveUploadTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser")
        self.tool1 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        self.tool2 = Tool.objects.create(name="Vulture", class_name="Vulture_Tool")

    def test_launch_massive_upload_creates_repos_and_analyses(self):
        urls_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        urls_file.write("https://github.com/user/repo1.git\n")
        urls_file.write("https://github.com/user/repo2.git\n")
        urls_file.close()

        with patch.object(TaskManager, 'excecute_analysis') as mock_exec:
            mock_exec.apply_async.return_value = "mock-task-id"
            TaskManager.launch_massive_upload(urls_file.name, self.user.id)

        self.assertEqual(Repository.objects.count(), 2)
        self.assertEqual(Analysis.objects.count(), 2)
        for analysis in Analysis.objects.all():
            self.assertEqual(analysis.analysistool_set.count(), 2)

        os.unlink(urls_file.name)

    def test_launch_massive_upload_reuses_existing_repo(self):
        existing = Repository.objects.create(
            url="https://github.com/user/repo1.git", owner=self.user
        )
        urls_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        urls_file.write("https://github.com/user/repo1.git\n")
        urls_file.close()

        with patch.object(TaskManager, 'excecute_analysis') as mock_exec:
            mock_exec.apply_async.return_value = "mock-task-id"
            TaskManager.launch_massive_upload(urls_file.name, self.user.id)

        self.assertEqual(Repository.objects.count(), 1)
        repo = Repository.objects.first()
        self.assertEqual(repo.folder, existing.folder)

        os.unlink(urls_file.name)

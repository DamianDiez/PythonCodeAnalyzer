import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from python_code_analyzer_app.models import Repository, Analysis, Tool, AnalysisTool, CeleryTaskSignal
from python_code_analyzer_app.app_models import tools_status


class AnalysisModelTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        settings.BASE_PATH = self.temp_dir + "\\"
        self.user = User.objects.create_user("testuser")
        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git", owner=self.user, folder="test_repo"
        )
        os.makedirs(self.repo.path)
        self.analysis = Analysis.objects.create(repository=self.repo)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_status_is_pending(self):
        self.assertEqual(self.analysis.status, tools_status.PENDING)

    def test_start_changes_status_to_running(self):
        self.analysis.start()
        self.assertEqual(self.analysis.status, tools_status.RUNNING)

    def test_cancel_changes_status_to_cancelled(self):
        self.analysis.cancel("User requested cancellation")
        self.assertEqual(self.analysis.status, tools_status.CANCELLED)
        self.assertEqual(self.analysis.status_msg, "User requested cancellation")

    def test_set_commit_saves_commit_hash(self):
        self.analysis.set_commit("abc123def456")
        self.assertEqual(self.analysis.commit, "abc123def456")

    def test_was_excecuted_returns_true_when_same_commit_was_analyzed(self):
        self.analysis.commit = "samehash"
        self.analysis.status = tools_status.FINISHED
        self.analysis.save()
        analysis2 = Analysis.objects.create(
            repository=self.repo, commit="samehash"
        )
        self.assertTrue(analysis2.was_excecuted())

    def test_was_excecuted_returns_false_when_no_analysis_with_that_commit(self):
        self.analysis.commit = "hash1"
        self.analysis.status = tools_status.FINISHED
        self.analysis.save()
        analysis2 = Analysis.objects.create(
            repository=self.repo, commit="hash2"
        )
        self.assertFalse(analysis2.was_excecuted())

    def test_was_excecuted_returns_false_when_commit_not_finished(self):
        self.analysis.commit = "samehash"
        self.analysis.status = tools_status.FAILED
        self.analysis.save()
        analysis2 = Analysis.objects.create(
            repository=self.repo, commit="samehash"
        )
        self.assertFalse(analysis2.was_excecuted())

    def test_path_result_ends_with_analysis_id(self):
        expected = self.temp_dir + "\\test_repo_result/Analysis" + str(self.analysis.id) + "/"
        self.assertEqual(self.analysis.path_result, expected)

    def test_path_to_zip_ends_with_zip(self):
        expected = self.temp_dir + "\\test_repo_result/Analysis" + str(self.analysis.id) + ".zip"
        self.assertEqual(self.analysis.path_to_zip, expected)


class AnalysisRunTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        settings.BASE_PATH = self.temp_dir + "\\"
        self.user = User.objects.create_user("testuser")
        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git", owner=self.user, folder="test_repo"
        )
        os.makedirs(self.repo.path)
        self.analysis = Analysis.objects.create(repository=self.repo)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.object(AnalysisTool, 'run')
    def test_run_calls_run_on_each_analysis_tool(self, mock_at_run):
        mock_at_run.return_value = tools_status.FINISHED
        tool1 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        tool2 = Tool.objects.create(name="Vulture", class_name="Vulture_Tool")
        AnalysisTool.objects.create(analysis=self.analysis, tool=tool1)
        AnalysisTool.objects.create(analysis=self.analysis, tool=tool2)
        self.analysis.run()
        self.assertEqual(mock_at_run.call_count, 2)

    @patch.object(AnalysisTool, 'run')
    def test_run_sets_failed_if_any_tool_fails(self, mock_at_run):
        mock_at_run.side_effect = [tools_status.FINISHED, tools_status.FAILED]
        tool1 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        tool2 = Tool.objects.create(name="Radon", class_name="Radon_Tool")
        AnalysisTool.objects.create(analysis=self.analysis, tool=tool1)
        AnalysisTool.objects.create(analysis=self.analysis, tool=tool2)
        self.analysis.run()
        self.assertEqual(self.analysis.status, tools_status.FAILED)

    @patch.object(AnalysisTool, 'run')
    def test_run_sets_finished_if_all_tools_succeed(self, mock_at_run):
        mock_at_run.return_value = tools_status.FINISHED
        tool1 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        AnalysisTool.objects.create(analysis=self.analysis, tool=tool1)
        os.makedirs(self.analysis.path_result, exist_ok=True)
        self.analysis.run()
        self.assertEqual(self.analysis.status, tools_status.FINISHED)


class AnalysisToolTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        settings.BASE_PATH = self.temp_dir + "\\"
        self.user = User.objects.create_user("testuser")
        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git", owner=self.user, folder="test_repo"
        )
        os.makedirs(self.repo.path)
        self.analysis = Analysis.objects.create(repository=self.repo)
        self.tool = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        self.analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=self.tool
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_path_repository_returns_repo_path(self):
        expected = os.path.join(self.temp_dir, "test_repo")
        self.assertEqual(self.analysis_tool.get_path_repository(), expected)

    def test_get_path_result_analysis_returns_analysis_result_path(self):
        result = self.analysis_tool.get_path_result_analysis()
        expected = self.temp_dir + "\\test_repo_result/Analysis" + str(self.analysis.id) + "/"
        self.assertEqual(result, expected)

    def test_get_indicators_returns_list_from_tool_instance(self):
        with patch.object(self.tool, 'get_instance') as mock_get_instance:
            mock_instance = MagicMock()
            mock_instance.get_indicators.return_value = ["ind1", "ind2"]
            mock_get_instance.return_value = mock_instance
            result = self.analysis_tool.get_indicators()
            self.assertEqual(result, ["ind1", "ind2"])

    def test_get_charts_returns_list_from_tool_instance(self):
        with patch.object(self.tool, 'get_instance') as mock_get_instance:
            mock_instance = MagicMock()
            mock_instance.get_charts.return_value = ["chart1"]
            mock_get_instance.return_value = mock_instance
            result = self.analysis_tool.get_charts()
            self.assertEqual(result, ["chart1"])

    def test_run_calls_tool_instance_run(self):
        with patch.object(self.tool, 'get_instance') as mock_get_instance:
            mock_instance = MagicMock()
            mock_instance.run.return_value = tools_status.FINISHED
            mock_get_instance.return_value = mock_instance
            result = self.analysis_tool.run()
            self.assertEqual(result, tools_status.FINISHED)
            self.analysis_tool.refresh_from_db()
            self.assertEqual(self.analysis_tool.status, tools_status.FINISHED)

    def test_run_returns_failed_when_get_instance_returns_none(self):
        tool = Tool.objects.create(name="Ghost", class_name="NonExistentTool")
        analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=tool
        )
        result = analysis_tool.run()
        self.assertEqual(result, tools_status.FAILED)

    def test_get_indicators_returns_empty_list_when_get_instance_returns_none(self):
        tool = Tool.objects.create(name="Ghost", class_name="NonExistentTool")
        analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=tool
        )
        result = analysis_tool.get_indicators()
        self.assertEqual(result, [])

    def test_get_charts_returns_empty_list_when_get_instance_returns_none(self):
        tool = Tool.objects.create(name="Ghost", class_name="NonExistentTool")
        analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=tool
        )
        result = analysis_tool.get_charts()
        self.assertEqual(result, [])

    def test_get_result_returns_empty_list_when_get_instance_returns_none(self):
        tool = Tool.objects.create(name="Ghost", class_name="NonExistentTool")
        analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=tool
        )
        result = analysis_tool.get_result()
        self.assertEqual(result, [])


class ToolGetInstanceTest(TestCase):
    def test_get_instance_returns_none_for_nonexistent_class(self):
        tool = Tool(name="Ghost", class_name="NonExistentTool")
        instance = tool.get_instance()
        self.assertIsNone(instance)

    def test_get_instance_returns_instance_for_valid_class(self):
        tool = Tool(name="Pylint", class_name="Pylint_Tool")
        instance = tool.get_instance()
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, "Pylint")


class CeleryTaskSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser")
        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git", owner=self.user, folder="folder"
        )
        self.analysis = Analysis.objects.create(repository=self.repo)

    def test_is_task_cancelled_returns_true_when_signal_exists(self):
        CeleryTaskSignal.objects.create(
            analysis=self.analysis,
            signal=CeleryTaskSignal.CANCEL_TASK,
            completed=False,
        )
        self.assertTrue(CeleryTaskSignal.is_task_cancelled(self.analysis.id))

    def test_is_task_cancelled_returns_false_when_no_signal(self):
        self.assertFalse(CeleryTaskSignal.is_task_cancelled(self.analysis.id))

    def test_is_task_cancelled_returns_false_when_signal_is_completed(self):
        CeleryTaskSignal.objects.create(
            analysis=self.analysis,
            signal=CeleryTaskSignal.CANCEL_TASK,
            completed=True,
        )
        self.assertFalse(CeleryTaskSignal.is_task_cancelled(self.analysis.id))

    def test_is_task_cancelled_does_not_persist_completed_flag_due_to_bug(self):
        cts = CeleryTaskSignal.objects.create(
            analysis=self.analysis,
            signal=CeleryTaskSignal.CANCEL_TASK,
            completed=False,
        )
        CeleryTaskSignal.is_task_cancelled(self.analysis.id)
        cts.refresh_from_db()
        self.assertFalse(cts.completed)

    def test_mark_completed_sets_completed_true(self):
        cts = CeleryTaskSignal.objects.create(
            analysis=self.analysis,
            signal=CeleryTaskSignal.CANCEL_TASK,
            completed=False,
        )
        cts.mark_completed()
        self.assertTrue(cts.completed)

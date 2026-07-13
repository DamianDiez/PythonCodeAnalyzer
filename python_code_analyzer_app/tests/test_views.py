import os
import tempfile
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from python_code_analyzer_app.models import Repository, Analysis, Tool, AnalysisTool
from python_code_analyzer_app.app_models import tools_status


class IndexViewTest(TestCase):
    def test_index_returns_200(self):
        response = self.client.get(reverse('python_code_analyzer_app:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse('python_code_analyzer_app:index'))
        self.assertTemplateUsed(response, 'python_code_analyzer_app/index.html')


class RepositoriesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")

    def test_repositories_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertEqual(response.status_code, 302)

    def test_repositories_shows_user_repos(self):
        Repository.objects.create(url="https://github.com/user1/repo.git", owner=self.user)
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "github.com/user1/repo.git")

    def test_repositories_does_not_show_other_users_repos(self):
        other = User.objects.create_user("other", password="pass1234")
        Repository.objects.create(url="https://github.com/other/repo.git", owner=other)
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "github.com/other/repo.git")


class RepositoryDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )
        self.analysis = Analysis.objects.create(repository=self.repo)

    def test_repository_detail_shows_repo(self):
        response = self.client.get(
            reverse('python_code_analyzer_app:repository', args=[self.repo.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "github.com/user1/repo.git")

    def test_repository_detail_returns_404_for_other_user(self):
        other = User.objects.create_user("other", password="pass1234")
        other_repo = Repository.objects.create(
            url="https://github.com/other/repo.git", owner=other
        )
        response = self.client.get(
            reverse('python_code_analyzer_app:repository', args=[other_repo.id])
        )
        self.assertEqual(response.status_code, 404)


class NewRepositoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")

    def test_new_repository_get_returns_form(self):
        response = self.client.get(reverse('python_code_analyzer_app:new_repository'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'python_code_analyzer_app/new_repository.html')

    def test_new_repository_post_creates_repo(self):
        response = self.client.post(
            reverse('python_code_analyzer_app:new_repository'),
            {'url': 'https://github.com/test/new-repo.git'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Repository.objects.count(), 1)
        repo = Repository.objects.first()
        self.assertEqual(repo.url, 'https://github.com/test/new-repo.git')
        self.assertEqual(repo.owner, self.user)


class NewAnalysisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )
        self.tool = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")

    def test_new_analysis_get_returns_form(self):
        response = self.client.get(
            reverse('python_code_analyzer_app:new_analysis', args=[self.repo.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pylint")

    @patch('python_code_analyzer_app.app_models.TaskManager.TaskManager.excecute_analysis.apply_async')
    def test_new_analysis_post_creates_analysis(self, mock_task):
        mock_task.return_value = "mock-task-id"
        response = self.client.post(
            reverse('python_code_analyzer_app:new_analysis', args=[self.repo.id]),
            {f'chk_enabled-{self.tool.id}': 'clicked'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Analysis.objects.count(), 1)
        analysis = Analysis.objects.first()
        self.assertEqual(analysis.repository, self.repo)
        self.assertEqual(analysis.analysistool_set.count(), 1)


class AnalysisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )
        self.analysis = Analysis.objects.create(repository=self.repo)

    @patch.object(Analysis, 'get_result')
    def test_analysis_shows_result_items(self, mock_get_result):
        mock_get_result.return_value = []
        response = self.client.get(
            reverse('python_code_analyzer_app:analysis', args=[self.analysis.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'python_code_analyzer_app/analysis.html')


class DeleteAnalysisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )
        self.analysis = Analysis.objects.create(repository=self.repo)

    def test_delete_analysis_removes_analysis(self):
        response = self.client.post(
            reverse('python_code_analyzer_app:delete_analysis', args=[self.analysis.id]),
            HTTP_REFERER=reverse('python_code_analyzer_app:repositories')
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Analysis.objects.count(), 0)


class DeleteRepositoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )

    def test_delete_repository_removes_repo(self):
        response = self.client.post(
            reverse('python_code_analyzer_app:delete_repository', args=[self.repo.id]),
            HTTP_REFERER=reverse('python_code_analyzer_app:repositories')
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Repository.objects.count(), 0)


class CancelAnalysisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")
        self.repo = Repository.objects.create(
            url="https://github.com/user1/repo.git", owner=self.user
        )
        self.analysis = Analysis.objects.create(repository=self.repo)

    def test_cancel_analysis_creates_signal_and_cancels(self):
        response = self.client.post(
            reverse('python_code_analyzer_app:cancel_analysis', args=[self.analysis.id]),
            HTTP_REFERER=reverse('python_code_analyzer_app:repositories')
        )
        self.assertEqual(response.status_code, 302)
        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.status, tools_status.CANCELLED)


class RepositoriesBadgeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.login(username="testuser", password="pass1234")

    def test_repositories_shows_badge_for_repo_with_finished_analysis(self):
        repo = Repository.objects.create(url="https://github.com/user1/repo.git", owner=self.user)
        Analysis.objects.create(repository=repo, status=tools_status.FINISHED)
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertContains(response, "badge-success")
        self.assertContains(response, "Finalizado")

    def test_repositories_shows_badge_without_analysis(self):
        Repository.objects.create(url="https://github.com/user1/repo.git", owner=self.user)
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "badge-light")
        self.assertContains(response, "Sin análisis")

    def test_repositories_shows_most_recent_status_over_older(self):
        repo = Repository.objects.create(url="https://github.com/user1/repo.git", owner=self.user)
        old_pending = Analysis.objects.create(repository=repo, status=tools_status.PENDING)
        Analysis.objects.filter(id=old_pending.id).update(
            date_added=timezone.now() - timedelta(days=5)
        )
        Analysis.objects.create(repository=repo, status=tools_status.RUNNING)
        response = self.client.get(reverse('python_code_analyzer_app:repositories'))
        self.assertContains(response, "badge-primary")
        self.assertContains(response, "En ejecución")
        self.assertNotContains(response, "Pendiente")
        self.assertNotContains(response, "badge-secondary")

    def test_repositories_badge_on_second_page(self):
        repos = []
        for i in range(9):
            r = Repository.objects.create(
                url=f"https://github.com/user1/repo{i}.git", owner=self.user
            )
            repos.append(r)
        Analysis.objects.create(repository=repos[8], status=tools_status.FINISHED)
        response = self.client.get(reverse('python_code_analyzer_app:repositories') + '?page=2')
        self.assertContains(response, "badge-success")
        self.assertContains(response, "Finalizado")

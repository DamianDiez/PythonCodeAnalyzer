import os
import shutil
import tempfile
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from python_code_analyzer_app.models import Repository, Analysis, Tool, AnalysisTool
from python_code_analyzer_app.tools.Chart import Chart
from python_code_analyzer_app.tools.IndicatorRating import IndicatorRating
from python_code_analyzer_app.tools.IdicatorDefault import IndicatorDefault

FIXTURES_DIR = os.path.join(settings.BASE_DIR, "python_code_analyzer_app", "test_fixtures")


class BaseToolParsingTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        settings.BASE_PATH = self.temp_dir + "\\"

        self.user = User.objects.create_user("testuser")

        self.repo = Repository.objects.create(
            url="https://github.com/test/repo.git",
            owner=self.user,
            folder="test_repo"
        )

        self.analysis = Analysis.objects.create(repository=self.repo)

    def _create_tool_env(self, tool_name, class_name, fixture_subdir, fixture_filename, target_filename=None):
        if target_filename is None:
            target_filename = fixture_filename
        tool = Tool.objects.create(name=tool_name, class_name=class_name)
        analysis_tool = AnalysisTool.objects.create(
            analysis=self.analysis, tool=tool
        )
        result_path = os.path.join(
            self.temp_dir, f"test_repo_result\\Analysis{self.analysis.id}\\{tool_name}"
        )
        os.makedirs(result_path)
        shutil.copy(
            os.path.join(FIXTURES_DIR, fixture_subdir, fixture_filename),
            os.path.join(result_path, target_filename)
        )
        return tool, analysis_tool

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class PylintToolParsingTest(BaseToolParsingTest):
    def setUp(self):
        super().setUp()
        self.tool, self.analysis_tool = self._create_tool_env(
            "Pylint", "Pylint_Tool", "", "pylint_result.json", "result.json"
        )
        self.instance = self.tool.get_instance()

    def test_get_indicators_returns_rating_and_modules(self):
        indicators = self.instance.get_indicators(self.analysis_tool)
        self.assertEqual(len(indicators), 2)
        rating = indicators[0]
        self.assertIsInstance(rating, IndicatorRating)
        self.assertEqual(rating.id, "pylint-rating")
        self.assertEqual(rating.value, 7.5)
        self.assertEqual(rating.max, 10)
        modules = indicators[1]
        self.assertIsInstance(modules, IndicatorDefault)
        self.assertEqual(modules.id, "pylint-modules")
        self.assertEqual(modules.value, 2)

    def test_get_charts_returns_heatmap_and_type_count(self):
        charts = self.instance.get_charts(self.analysis_tool)
        self.assertEqual(len(charts), 2)
        self.assertIsInstance(charts[0], Chart)
        self.assertEqual(charts[0].type, Chart.MATRIX)
        self.assertEqual(charts[1].type, Chart.BAR)

    def test_get_result_combines_indicators_and_charts(self):
        result = self.instance.get_result(self.analysis_tool)
        self.assertEqual(len(result), 4)

    def test_get_indicators_returns_empty_list_when_no_file(self):
        analysis2 = Analysis.objects.create(repository=self.repo)
        tool2 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        at2 = AnalysisTool.objects.create(analysis=analysis2, tool=tool2)
        indicators = self.instance.get_indicators(at2)
        self.assertEqual(indicators, [])

    def test_get_charts_returns_empty_list_when_no_file(self):
        analysis2 = Analysis.objects.create(repository=self.repo)
        tool2 = Tool.objects.create(name="Pylint", class_name="Pylint_Tool")
        at2 = AnalysisTool.objects.create(analysis=analysis2, tool=tool2)
        charts = self.instance.get_charts(at2)
        self.assertEqual(charts, [])


class VultureToolParsingTest(BaseToolParsingTest):
    def setUp(self):
        super().setUp()
        self.tool, self.analysis_tool = self._create_tool_env(
            "Vulture", "Vulture_Tool", "", "vulture_result.txt", "result.txt"
        )
        self.instance = self.tool.get_instance()

    def test_get_indicators_returns_unused_items_count(self):
        indicators = self.instance.get_indicators(self.analysis_tool)
        self.assertEqual(len(indicators), 1)
        ind = indicators[0]
        self.assertIsInstance(ind, IndicatorDefault)
        self.assertEqual(ind.id, "vulture-unused-items")
        self.assertEqual(ind.value, 3)

    def test_get_charts_returns_unused_items_chart(self):
        charts = self.instance.get_charts(self.analysis_tool)
        self.assertEqual(len(charts), 1)
        chart = charts[0]
        self.assertIsInstance(chart, Chart)
        self.assertEqual(chart.type, Chart.BAR)
        self.assertEqual(chart.id, "Vulture-Unused-Items")

    def test_get_result_combines_indicators_and_charts(self):
        result = self.instance.get_result(self.analysis_tool)
        self.assertEqual(len(result), 2)


class RadonToolParsingTest(BaseToolParsingTest):
    def setUp(self):
        super().setUp()
        self.tool, self.analysis_tool = self._create_tool_env(
            "Radon", "Radon_Tool", "", "radon_cc.txt", "result_cc.txt"
        )
        self.instance = self.tool.get_instance()
        result_path = os.path.join(
            self.temp_dir,
            f"test_repo_result\\Analysis{self.analysis.id}\\Radon"
        )
        shutil.copy2(
            os.path.join(FIXTURES_DIR, "radon_mi.json"),
            os.path.join(result_path, "result_mi.json")
        )
        shutil.copy2(
            os.path.join(FIXTURES_DIR, "radon_raw.json"),
            os.path.join(result_path, "result_raw.json")
        )

    def test_get_indicators_returns_loc_comments_and_cc(self):
        indicators = self.instance.get_indicators(self.analysis_tool)
        self.assertEqual(len(indicators), 3)
        loc = indicators[0]
        self.assertEqual(loc.id, "radon-line-of-code")
        self.assertEqual(loc.value, 80)
        comments = indicators[1]
        self.assertEqual(comments.id, "radon-line-of-comments")
        self.assertEqual(comments.value, 11)
        cc = indicators[2]
        self.assertEqual(cc.id, "radon-cyclomatic-complexity")

    def test_get_charts_returns_mi_chart(self):
        charts = self.instance.get_charts(self.analysis_tool)
        self.assertEqual(len(charts), 1)
        chart = charts[0]
        self.assertEqual(chart.id, "Radon-MI")
        self.assertEqual(chart.type, Chart.BAR)

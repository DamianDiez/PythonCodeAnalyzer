from django.test import TestCase
from python_code_analyzer_app.app_layout_classes.LayoutManager import LayoutManager
from python_code_analyzer_app.app_layout_classes.Criteria import Criteria
from python_code_analyzer_app.tools.ResultItem import ResultItem, SizeOptions, Template
from python_code_analyzer_app.tools.Chart import Chart
from python_code_analyzer_app.tools.IdicatorDefault import IndicatorDefault


class LayoutManagerTest(TestCase):
    def test_sort_by_size_ascending(self):
        items = [
            ResultItem("a", "A", SizeOptions.LARGE, Template.INDICATOR_DEFAULT, "T"),
            ResultItem("b", "B", SizeOptions.SMALL, Template.INDICATOR_DEFAULT, "T"),
            ResultItem("c", "C", SizeOptions.MEDIUM, Template.INDICATOR_DEFAULT, "T"),
        ]
        criteria = [Criteria(Criteria.SIZE, ascending=True)]
        sorted_items = LayoutManager.sort_by_multiple_criteria(items, criteria)
        self.assertEqual([i.id for i in sorted_items], ["b", "c", "a"])

    def test_sort_by_size_descending(self):
        items = [
            ResultItem("a", "A", SizeOptions.SMALL, Template.INDICATOR_DEFAULT, "T"),
            ResultItem("b", "B", SizeOptions.LARGE, Template.INDICATOR_DEFAULT, "T"),
            ResultItem("c", "C", SizeOptions.MEDIUM, Template.INDICATOR_DEFAULT, "T"),
        ]
        criteria = [Criteria(Criteria.SIZE, ascending=False)]
        sorted_items = LayoutManager.sort_by_multiple_criteria(items, criteria)
        self.assertEqual([i.id for i in sorted_items], ["b", "c", "a"])

    def test_sort_mixed_types_by_size(self):
        items = [
            Chart("c1", SizeOptions.SMALL, Template.CHART_DEFAULT, "Tool", Chart.BAR, "", [], []),
            IndicatorDefault("i1", "Label", SizeOptions.LARGE, 10, "Tool"),
            IndicatorDefault("i2", "Label", SizeOptions.MEDIUM, 5, "Tool"),
        ]
        criteria = [Criteria(Criteria.SIZE, ascending=True)]
        sorted_items = LayoutManager.sort_by_multiple_criteria(items, criteria)
        self.assertEqual([i.id for i in sorted_items], ["c1", "i2", "i1"])

    def test_two_criteria_sort_by_size_ascending_then_tool_name(self):
        items = [
            IndicatorDefault("a", "A", SizeOptions.LARGE, 1, "Pylint"),
            IndicatorDefault("b", "B", SizeOptions.SMALL, 2, "Radon"),
            IndicatorDefault("c", "C", SizeOptions.SMALL, 3, "Pylint"),
        ]
        criteria = [Criteria(Criteria.SIZE, ascending=True), Criteria(Criteria.TOOL_NAME, ascending=True)]
        sorted_items = LayoutManager.sort_by_multiple_criteria(items, criteria)
        self.assertEqual([i.id for i in sorted_items], ["c", "b", "a"])

from django.test import TestCase
from python_code_analyzer_app.tools.ResultItem import ResultItem, SizeOptions, Template
from python_code_analyzer_app.tools.Chart import Chart
from python_code_analyzer_app.tools.IdicatorDefault import IndicatorDefault
from python_code_analyzer_app.tools.IndicatorRating import IndicatorRating


class ResultItemTest(TestCase):
    def test_create_result_item(self):
        item = ResultItem("test-id", "Test Label", SizeOptions.SMALL, Template.INDICATOR_DEFAULT, "Pylint")
        self.assertEqual(item.id, "test-id")
        self.assertEqual(item.label, "Test Label")
        self.assertEqual(item.size, 4)
        self.assertEqual(item.plantilla, Template.INDICATOR_DEFAULT)
        self.assertEqual(item.tool_name, "Pylint")


class ChartTest(TestCase):
    def test_create_bar_chart(self):
        chart = Chart("my-chart", SizeOptions.MEDIUM, Template.CHART_DEFAULT,
                      "Pylint", Chart.BAR, "My Chart",
                      '["A","B","C"]', [10, 20, 30])
        self.assertEqual(chart.id, "my-chart")
        self.assertEqual(chart.size, SizeOptions.MEDIUM)
        self.assertEqual(chart.type, Chart.BAR)
        self.assertEqual(chart.xLabels, '["A","B","C"]')
        self.assertEqual(chart.data, [10, 20, 30])
        self.assertEqual(chart.height, 400)
        self.assertEqual(chart.display_legend, 'true')

    def test_create_chart_with_custom_height(self):
        chart = Chart("custom-height", SizeOptions.LARGE, Template.CHART_MATRIX,
                      "Radon", Chart.MATRIX, "Matrix",
                      '["x1","x2"]', [{"x": "x1", "y": "y1", "v": 5}],
                      300, 'false')
        self.assertEqual(chart.height, 300)
        self.assertEqual(chart.display_legend, 'false')

    def test_inherits_from_result_item(self):
        chart = Chart("c", SizeOptions.SMALL, Template.CHART_DEFAULT,
                      "Tool", Chart.DOUGHNUT, "L", [], [])
        self.assertIsInstance(chart, ResultItem)


class IndicatorDefaultTest(TestCase):
    def test_create_default_indicator(self):
        ind = IndicatorDefault("ind-id", "Lines of Code", SizeOptions.SMALL, 150, "Radon")
        self.assertEqual(ind.id, "ind-id")
        self.assertEqual(ind.label, "Lines of Code")
        self.assertEqual(ind.size, SizeOptions.SMALL)
        self.assertEqual(ind.value, 150)
        self.assertEqual(ind.tool_name, "Radon")
        self.assertEqual(ind.plantilla, Template.INDICATOR_DEFAULT)

    def test_inherits_from_result_item(self):
        ind = IndicatorDefault("i", "Label", SizeOptions.SMALL, "val", "Tool")
        self.assertIsInstance(ind, ResultItem)


class IndicatorRatingTest(TestCase):
    def test_create_rating_indicator(self):
        rating = IndicatorRating("pylint-rating", "Rating", SizeOptions.SMALL,
                                 7.5, "Pylint", 10, 4.0, 7.0, 9.0)
        self.assertEqual(rating.id, "pylint-rating")
        self.assertEqual(rating.label, "Rating")
        self.assertEqual(rating.value, 7.5)
        self.assertEqual(rating.max, 10)
        self.assertEqual(rating.bad, 4.0)
        self.assertEqual(rating.regular, 7.0)
        self.assertEqual(rating.good, 9.0)
        self.assertEqual(rating.plantilla, Template.INDICATOR_RATING)

    def test_rating_below_bad_is_red(self):
        rating = IndicatorRating("r", "R", SizeOptions.SMALL,
                                 2.0, "Tool", 10, 4.0, 7.0, 9.0)
        self.assertLess(rating.value, rating.bad)

    def test_rating_between_bad_and_regular(self):
        rating = IndicatorRating("r", "R", SizeOptions.SMALL,
                                 5.5, "Tool", 10, 4.0, 7.0, 9.0)
        self.assertGreaterEqual(rating.value, rating.bad)
        self.assertLess(rating.value, rating.regular)

    def test_rating_between_regular_and_good(self):
        rating = IndicatorRating("r", "R", SizeOptions.SMALL,
                                 8.0, "Tool", 10, 4.0, 7.0, 9.0)
        self.assertGreaterEqual(rating.value, rating.regular)
        self.assertLess(rating.value, rating.good)

    def test_rating_above_good(self):
        rating = IndicatorRating("r", "R", SizeOptions.SMALL,
                                 9.5, "Tool", 10, 4.0, 7.0, 9.0)
        self.assertGreaterEqual(rating.value, rating.good)

from python_code_analyzer_app.tools.IdicatorDefault import IndicatorDefault
from python_code_analyzer_app.tools.ResultItem import Template

class IndicatorRating(IndicatorDefault):
    """Indicator class"""
    RATING = "rating"
    DEFAULT = "default"

    def __init__(self, _id, _label, _size, _value, _tool_name, _max, _bad, _regular, _good):
        """init"""
        super().__init__(_id, _label, _size, _value, _tool_name, Template.INDICATOR_RATING)
        self.max = _max
        self.bad = _bad
        self.regular = _regular
        self.good = _good
from python_code_analyzer_app.tools.ResultItem import ResultItem

class Indicator(ResultItem):
    """Indicator class"""
    RATING = "rating"
    DEFAULT = "default"

    def __init__(self, _id, _label, _size, _value, _template, _tool_name, _type, _max, _bad, _regular, _good):
        """init"""
        super().__init__(_id, _label, _size, _template, _tool_name)
        self.value = _value
        self.type = _type
        self.max = _max
        self.bad = _bad
        self.regular = _regular
        self.good = _good
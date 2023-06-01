from python_code_analyzer_app.tools.ResultItem import ResultItem, Template

class IndicatorDefault(ResultItem):
    """Indicator class"""
    RATING = "rating"
    DEFAULT = "default"

    def __init__(self, _id, _label, _size, _value, _tool_name, _template = Template.INDICATOR_DEFAULT):
        """init"""
        super().__init__(_id, _label, _size, _template, _tool_name)
        self.value = _value
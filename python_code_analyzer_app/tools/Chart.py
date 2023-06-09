from python_code_analyzer_app.tools.ResultItem import ResultItem


class Chart(ResultItem):
    """Chart class"""
    BAR = "bar"
    BUBBLE = "bubble"
    DOUGHNUT = "doughnut"
    PIE = "pie"
    LINE = "line"
    MATRIX = "matrix"
    POLARAREA = "polarArea"
    RADAR = "radar"
    SCATTER = "scatter"

    def __init__(self, _id, _size, _template, _tool_name, _type, _label, _xLabels, _data, _height=400, _display_legend='true', _yLabels=[]):
        """init"""
        super().__init__(_id, _label, _size, _template, _tool_name)
        self.type = _type
        self.xLabels = _xLabels
        self.yLabels = _yLabels
        self.data = _data
        self.height = _height
        self.display_legend = _display_legend

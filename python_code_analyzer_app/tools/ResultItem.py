class Template():
    INDICATOR_DEFAULT = './indicator_default.html'
    INDICATOR_RATING = './indicator_rating.html'
    CHART_DEFAULT = './chart_default.html'
    CHART_MATRIX = './chart_matrix.html'

class SizeOptions():
    SMALL=4
    MEDIUM=6
    LARGE=12

class ResultItem:
    """ResultItem class"""
    def __init__(self, _id, _label, _size, _template, _tool_name):
        """init"""
        self.id = _id
        self.label = _label
        self.size = _size
        self.plantilla = _template
        self.tool_name = _tool_name
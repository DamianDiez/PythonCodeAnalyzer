

class Chart:
    """Chart class"""
    BAR="bar"
    BUBBLE="bubble"
    DOUGHNUT="doughnut"
    PIE="pie"
    LINE="line"
    MATRIX="matrix"
    POLARAREA="polarArea"
    RADAR="radar"
    SCATTER="scatter"
    
    def __init__(self, _id, _position, _type, _label, _xLabels, _data, _display_legend = 'true', _yLabels=[]):
        """init"""
        self.id = _id
        self.position=_position
        self.type=_type
        self.label=_label
        self.xLabels=_xLabels
        self.yLabels=_yLabels
        self.data=_data
        self.display_legend=_display_legend


class Cell:
    def __init__(self, x, y, v):
        self.x = x
        self.y = y
        self.v = v
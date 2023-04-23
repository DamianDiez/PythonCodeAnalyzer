

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
    
    def __init__(self, _id, _size, _type, _label, _xLabels, _data, _height=400, _display_legend = 'true', _yLabels=[]):
        """init"""
        self.id=_id
        self.size=_size
        self.type=_type
        self.label=_label
        self.xLabels=_xLabels
        self.yLabels=_yLabels
        self.data=_data
        self.height=_height
        self.display_legend=_display_legend
        

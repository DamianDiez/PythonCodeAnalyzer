

class Chart:
    """Chart class"""
    BAR="bar"
    BUBBLE="bubble"
    DOUGHNUT="doughnut"
    PIE="pie"
    LINE="line"
    POLARAREA="polarArea"
    RADAR="radar"
    SCATTER="scatter"
    
    def __init__(self, _id, _position, _type, _label, _labels, _data, _display_legend = 'true'):
        """init"""
        self.id = _id
        self.position=_position
        self.type=_type
        self.label=_label
        self.labels=_labels
        self.data=_data
        self.display_legend=_display_legend

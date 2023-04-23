class Indicator:
    """Indicator class"""
    RATING="rating"
    DEFAULT="default"

    def __init__(self, _id, _title, _size, _value, _type, _max, _bad, _regular,_good):
        """init"""
        self.id=_id
        self.title=_title
        self.size=_size
        self.value =_value
        self.type=_type
        self.max=_max
        self.bad=_bad
        self.regular=_regular
        self.good=_good

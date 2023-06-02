class Criteria:
    """Criteria class"""
    
    #attribute options
    SIZE='size'
    TOOL_NAME='tool_name'

    def __init__(self, attribute, ascending=True):
        """Initialize Criteria with attribute and ascending flag"""
        self.attribute = attribute
        self.ascending = ascending
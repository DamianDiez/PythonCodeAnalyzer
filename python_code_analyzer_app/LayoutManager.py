class LayoutManager:
    """LayoutManager class"""

    @staticmethod
    def sort_by_multiple_criteria(items, criteria_list):
        """Sort the items based on multiple criteria"""
        return sorted(
            items, key=lambda x: [getattr(x, crit.attribute) * (-1 if not crit.ascending else 1) for crit in criteria_list]
        )

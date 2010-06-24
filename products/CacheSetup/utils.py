from Acquisition import aq_base

marker = []

def safe_hasattr(ob, attribute):
    """safe_hasattr"""
    return getattr(ob, attribute, marker) is not marker

def base_hasattr(ob, attribute):
    """base_hasattr"""
    return getattr(aq_base(ob), attribute, marker) is not marker


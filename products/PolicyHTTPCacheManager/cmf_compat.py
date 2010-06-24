# methods from CMFCore.utils added for backward compatibility with CMF 1.4.8

from Acquisition import Implicit
class _ViewEmulator(Implicit):
    """Auxiliary class used to adapt FSFile and FSImage
    for caching_policy_manager
    """
    def __init__(self, view_name=''):
        self._view_name = view_name

    def getId(self):
        return self._view_name

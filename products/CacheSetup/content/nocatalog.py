from Products.CMFCore.utils import getToolByName

class NoCatalog:
    """Mixin for content that is neither referenceable nor in the catalog.
    Based on ATContentTypes/criteria/base.py
    """
    # leave unindex/uncatalog methods in so that older versions will
    # uninstall properly

    isReferenceable = None

    # reference register / unregister methods
    def _register(self, *args, **kwargs): pass
    #def _unregister(self, *args, **kwargs): pass
    def _updateCatalog(self, *args, **kwargs): pass
    def _referenceApply(self, *args, **kwargs): pass
    #def _uncatalogUID(self, *args, **kwargs): pass
    #def _uncatalogRefs(self, *args, **kwargs): pass

    # catalog methods
    def indexObject(self, *args, **kwargs): 
        pcs = getToolByName(self, 'portal_cache_settings', None)
        if pcs is None:
            return
        pcs.incrementCatalogCount()
        
    #def unindexObject(self, *args, **kwargs): pass
    def reindexObject(self, *args, **kwargs):
        pcs = getToolByName(self, 'portal_cache_settings', None)
        if pcs is None:
            return
        pcs.incrementCatalogCount()

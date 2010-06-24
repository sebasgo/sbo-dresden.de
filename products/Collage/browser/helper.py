from zope.interface import Interface

from Acquisition import aq_base, aq_inner, aq_parent

from Products.Collage.interfaces import ICollage

class ICollageHelper(Interface):
    def loadCollageJS(self):
        """Determine if we need to load JS."""
        
    def isCollageContent():
        """Search object tree for a Collage-object."""
        pass

    def getCollageObjectURL():
        """Search object tree for a Collage-object and return URL."""
        pass

class CollageHelper(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def isCollageContent(self, parent=None):
        return self.getCollageObjectURL() is not None

    def getCollageObjectURL(self, parent=None):
        if not parent:
            parent = aq_parent(aq_inner(self.context))

        if parent:
            if ICollage.providedBy(parent):
                return parent.absolute_url()

            parent = aq_parent(parent)
            if parent:
                if ICollage.providedBy(parent):
                    return parent.absolute_url()

        return None

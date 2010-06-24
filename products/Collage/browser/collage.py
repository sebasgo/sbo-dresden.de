from Products.Five.browser import BrowserView

from zope.interface import alsoProvides
from zope.interface import Interface

from Products.Collage.interfaces import ICollageEditLayer

class ICollageView(Interface):
    def isStructuralFolder():
        """Copied from CMFPlone/browser/plone.py."""

    def edit_mode():
        pass

    def isPlone2():
        pass

    def isPlone3():
        pass
    
class CollageView(BrowserView):
    def edit_mode(self):
        return ICollageEditLayer.providedBy(self.request)

    def isStructuralFolder(self, instance):
        context = instance
        folderish = bool(getattr(aq_base(context), 'isPrincipiaFolderish',
                                 False))
        if not folderish:
            return False
        elif INonStructuralFolder.providedBy(context):
            return False
        elif z2INonStructuralFolder.isImplementedBy(context):
            # BBB: for z2 interface compat
            return False
        else:
            return folderish

    def isPlone2(self):
        # XXX: this is a lame way of checking the version
        try:
            return self.context.restrictedTraverse('global_bodytag') and True
        except:
            return False            

    def isPlone3(self):
        return not self.isPlone2()
        
    def render_manage_view(self):
        """Set the edit layer on the request and return the
        standard view as returned by CMFDynamicViewFTI."""
        
        alsoProvides(self.request, ICollageEditLayer)

        fti = self.context.getTypeInfo()
        method = fti.getViewMethod(self.context)

        view = self.context.restrictedTraverse(method)
        return view()

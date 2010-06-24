from Products.Five.browser import BrowserView

from Products.Collage.interfaces import IDynamicViewManager
from Products.Collage.interfaces import ICollageBrowserLayer
from Products.Collage.interfaces import ICollageAlias

from zope.interface import Interface, directlyProvidedBy, directlyProvides

from zope.component import getMultiAdapter

from Acquisition import aq_inner

class IKSSHelper(Interface):
    def getUniqueIdentifier():
        pass

    def getKssView():
        pass
    
    def getKssClasses(field_name):
        pass

class KSSHelper(BrowserView):
    """To better support various Plone environments we implement
    this view to help generate the right inline-editing bindings."""
    
    def getUniqueIdentifier(self):
        return self.context.UID()

    def getKssView(self):
        try:
            kss = self.context.restrictedTraverse('@@kss_field_decorator_view')
        except:
            # BBB: Fallback if KSS is not installed
            kss = self.context.restrictedTraverse('@@kss_field_decorator_dummy_view')

        return kss
    
    def getKssClasses(self, field_name):
        kss = self.getKssView()
        
        # choose appropriate kss class generator depending on rendering mode
        if self.request.get('URL').endswith('/replaceField'):
            f = kss.getKssClasses
        else:
            f = kss.getKssClassesInlineEditable

        try:
            editing_classes = f(field_name,
                                templateId='kss_collage_macro_proxy',
                                macro=field_name,
                                target="%s-%s" % (self.getUniqueIdentifier(), field_name))
        except TypeError:
            # BBB: method probably doesn't support the target-parameter
            # once Plone 3.0.1 is out, we can remove this exception-handler
            return ''

        uid_class = kss.getKssUIDClass()

        return editing_classes + " " + uid_class
    
class CollageMacrosView(BrowserView):
    """This helper view looks up the current view for the context-object
    and returns it without rendering it."""

    @property
    def __call__(self):
        context = aq_inner(self.context)
        
        manager = IDynamicViewManager(context)
        layout = manager.getLayout()

        if not layout:
            layout, title = manager.getDefaultLayout()

        if ICollageAlias.providedBy(context):
            context = context.get_target()
            
            # if not set, revert to self.context
            if not context: context = self.context

        # transmute request interfaces
        ifaces = directlyProvidedBy(self.request)
        directlyProvides(self.request, ICollageBrowserLayer)

        view = getMultiAdapter((context, self.request), name=layout)

        # restore interfaces
        directlyProvides(self.request, ifaces)

        return view.index

class DummyFieldsView(BrowserView):
    def getKssUIDClass(self):
        return ''

    def getKssClassesInlineEditable(self, *args, **kwargs):
        return ''

    def getKssClasses(self, *args, **kwargs):
        return ''

from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.interface import Interface
from zope.interface import \
     implements, alsoProvides, providedBy

from zope.component import getSiteManager

from interfaces import IDynamicViewManager
from interfaces import ICollageAlias
from interfaces import ICollageBrowserLayer

from persistent.dict import PersistentDict

ANNOTATIONS_KEY = u'Collage'

class DynamicViewManager(object):
    implements(IDynamicViewManager)

    def __init__(self, context):
        self.context = context
        
    def getStorage(self):
        try:
            annotations = IAnnotations(self.context)
        except:
            alsoProvides(self.context, IAttributeAnnotatable)
            annotations = IAnnotations(self.context)

        return annotations.setdefault(ANNOTATIONS_KEY, PersistentDict())

    def getLayout(self):
        storage = self.getStorage()
        return storage.get('layout', None)

    def setLayout(self, layout):
        storage = self.getStorage()
        storage['layout'] = layout

    def getDefaultLayout(self):
        layouts = self.getLayouts()

        if layouts:
            # look for a standard view (by naming convention)
            for name, title in layouts:
                if name == u'standard':
                    return (name, title)
            
            # otherwise return first view factory
            return layouts[0]

        raise ValueError
    
    def getLayouts(self):
        context = self.context
        
        if ICollageAlias.providedBy(self.context):
            # use target as self.context
            
            target = self.context.get_target()
            if target: context = target
            
        return self._getViewFactoryInfo(ICollageBrowserLayer, context=context)

    def _getViewFactoryInfo(self, layer, context=None):
        """Return view factory info for this context and browser layer."""

        if not context:
            context = self.context
        
        sm = getSiteManager(context)
        
        context_ifaces = providedBy(context)
        
        lookupAll = sm.adapters.lookupAll
        
        collage_aware = lookupAll((context_ifaces, layer), Interface)
        collage_agnostic = list(lookupAll((context_ifaces, Interface), Interface))
        
        return [(name, getattr(factory, 'title', name)) \
                for (name, factory) in collage_aware if (name, factory) not in collage_agnostic]


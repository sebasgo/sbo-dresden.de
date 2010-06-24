from AccessControl import getSecurityManager, Unauthorized

from zope.interface import Interface
from zope.interface import directlyProvidedBy, directlyProvides
from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView

from Products.Collage.interfaces import ICollageBrowserLayer, IDynamicViewManager
from Products.Collage.interfaces import ICollageAlias

class SimpleContainerRenderer(BrowserView):
    def getItems(self, contents=None):
        # needed to circumvent bug :-(
        self.request.debug = False

        # transmute request interfaces
        ifaces = directlyProvidedBy(self.request)
        directlyProvides(self.request, ICollageBrowserLayer)

        views = []

        if not contents:
            contents = self.context.folderlistingFolderContents()

        for context in contents:
            target = context
            manager = IDynamicViewManager(context)
            layout = manager.getLayout()

            if not layout:
                layout, title = manager.getDefaultLayout()

            if ICollageAlias.providedBy(context):
                target = context.get_target()
                # Check if alias is accessible
                try:
                    getSecurityManager().validate(self, self, target.getId(), target)
                except Unauthorized:
                    continue

                # if not set, revert to context
                if not target: target = context

            # assume that a layout is always available
            view = getMultiAdapter((target, self.request), name=layout)

            # store reference to alias if applicable
            if ICollageAlias.providedBy(context):
                view.__alias__ = context
            
            views.append(view)

        # restore interfaces
        directlyProvides(self.request, ifaces)

        return views


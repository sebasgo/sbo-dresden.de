from zope.viewlet import viewlet
from zope.component import getMultiAdapter
from zope.interface import directlyProvidedBy, directlyProvides

from Products.CMFCore.utils import getToolByName

from Products.Collage.interfaces import ICollageBrowserLayer
from Products.Collage.interfaces import IDynamicViewManager
from Products.Collage.interfaces import ICollageAlias

from ZODB.POSException import ConflictError
 
from OFS.CopySupport import _cb_decode
from OFS import Moniker

class SimpleContentMenuViewlet(object):
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')()

    def test(self):
        return lambda a, b, c: a and b or c

    def getImmediateObject(self):
        """Returns the immediate object added to the Collage
        instead of a possible alias target object."""
        alias = getattr(self.__parent__, '__alias__', None)
        if alias:
            return alias.aq_inner
        
        return self.context.aq_inner

class LayoutViewlet(SimpleContentMenuViewlet):
    def getLayouts(self):
        context = self.context

        # handle aliased objects
        alias = getattr(self.__parent__, '__alias__', None)
        if alias: context = alias

        manager = IDynamicViewManager(context)

        # lookup active layout
        active = manager.getLayout()

        if not active:
            active, title = manager.getDefaultLayout()
        
        # compile list of registered layouts
        layouts = manager.getLayouts()

        # filter out fallback view
        layouts = filter(lambda (name, title): name != u'fallback', layouts)

        return [{'id': name,
                 'name': title,
                 'active': name == active} for (name, title) in layouts]

class InsertNewItemViewlet(object):
    def normalizeString(self):
        return getToolByName(self.context, 'plone_utils').normalizeString

    def getAddableTypes(self):
        plone_view = self.context.restrictedTraverse('@@plone')
        container = plone_view.getCurrentFolder()

        allowed_types = container.allowedContentTypes()

        portal_url = getToolByName(self.context, 'portal_url')()
        
        return [{'title': t.Title(),
                 'description': t.Description(),
                 'icon': '%s/%s' % (portal_url, t.getIcon()),
                 'id': t.getId()} for t in allowed_types]
    
class SplitColumnViewlet(object):
    pass

class IconViewlet(SimpleContentMenuViewlet):
    def getIcon(self):
        tt = getToolByName(self.context, 'portal_types')
        obj_typeinfo = tt.getTypeInfo(self.context.portal_type)

        return obj_typeinfo.getIcon()

class ActionsViewlet(SimpleContentMenuViewlet):
    def isAlias(self):
        return getattr(self.__parent__, '__alias__', None) and True

    def getViewActions(self):
        atool = getToolByName(self.context, 'portal_actions')
        actions = atool.listFilteredActionsFor(self.context)

        try:
            plone_view = self.context.restrictedTraverse('@@plone')
            return plone_view.prepareObjectTabs()
        except AttributeError:
            # BBB: support for Plone 2.5
            return self.context.plonifyActions(template_id=None, actions=actions, default_tab='view')

class CopyViewlet(SimpleContentMenuViewlet):
    pass

class PasteViewlet(SimpleContentMenuViewlet):
    @property
    def clipboard_data_valid(self):
        cb_dataValid = getattr(self.context, 'cb_dataValid', None)
        
        if callable(cb_dataValid):
            return cb_dataValid()

    def _get_clipboard_item(self):
        cp = self.request.get('__cp')
        op, mdatas = _cb_decode(cp) # see OFS/CopySupport.py

        # just get the first item on the clipboard
        mdata = mdatas[0]
        m = Moniker.loadMoniker(mdata)

        app = self.context.getPhysicalRoot()
        try:
            ob = m.bind(app)
        except (ConflictError, AttributeError, KeyError):
            return None
        
        return ob
    
    def render(self):
        """Only render if the clipboard contains an object that can
        be added to this container."""

        if self.clipboard_data_valid:
            # verify that we are allowed to paste this item here
            item = self._get_clipboard_item()

            if item:
                portal_type = item.portal_type
                allowed_types = self.context.allowedContentTypes()
                if portal_type in (t.getId() for t in allowed_types):
                    return self.index()

        return u''

    def clipboard_item_title(self):
        return u'Paste "%s"' % self._get_clipboard_item().title_or_id()

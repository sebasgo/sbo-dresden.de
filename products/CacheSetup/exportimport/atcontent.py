from zope import component
from Products.GenericSetup import utils as gsutils
from Products.GenericSetup import interfaces as gsinterfaces
from Products.Archetypes import atapi
import logging
logger = logging.getLogger('GS adapter')


class ATContentAdapterBase(gsutils.XMLAdapterBase,
                           gsutils.ObjectManagerHelpers):

    _topname = 'atcontent'
    _fields = None
    _pagecachemanager_fields = None

    def _extractSetup(self):
        fragment = self._doc.createElement(self._topname)
        fragment.setAttribute('contentid', self.context.getId())
        fragment.setAttribute('portaltype', self.context.portal_type)
        if self.context.Title():
            fragment.setAttribute('title', self.context.Title())
        for field in self.context.Schema().fields():
            if self._fields is not None and field.getName() not in self._fields:
                continue
            field_el = self._doc.createElement('field')
            fragment.appendChild(field_el)
            field_el.setAttribute('name', field.getName())
            accessor = field.getEditAccessor(self.context)
            if accessor is not None:
                v = accessor()
            else:
                v = field.get(self.context)
            if isinstance(v, tuple) or isinstance(v, list):
                for line in v:
                    value_el = self._doc.createElement('fieldvalue')
                    field_el.appendChild(value_el)
                    if isinstance(line, unicode):
                        value_el.setAttribute('value', line.encode('utf-8'))
                    else:
                        value_el.setAttribute('value', str(line))
            else:
                field_el.setAttribute('value', self._formatValue(v))
        if self._pagecachemanager_fields:
            pagecachemanager = self.context.CacheSetup_PageCache
            for field in self._pagecachemanager_fields:
                field_el = self._doc.createElement('pagecachesetting')
                fragment.appendChild(field_el)
                field_el.setAttribute('name', field)
                value = pagecachemanager._settings[field]
                field_el.setAttribute('value', self._formatValue(value))
        if getattr(self.context, 'isPrincipiaFolderish', False):
            fragment.appendChild(self._extractObjects())
        
        return fragment

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        return self._extractSetup()

    def _importContentObject(self, node):
        
        title = node.getAttribute('title')
        contentid = node.getAttribute('contentid')
        portaltype = node.getAttribute('portaltype')
        
        self.context.setTitle(title)
        if self._pagecachemanager_fields:
            pagecachemanager = self.context.CacheSetup_PageCache
            pagecachemanagerSettings = {}
        else:
            pagecachemanager = None
        for child_node in node.childNodes:
            if child_node.nodeName == 'field':
                self._setFieldValue(self.context, child_node)
            elif child_node.nodeName == 'pagecachesetting':
                name = child_node.getAttribute('name')
                value = child_node.getAttribute('value')
                currentValue = pagecachemanager._settings[name]
                if isinstance(currentValue, int):
                    pagecachemanagerSettings[name] = int(value)
                else:
                    pagecachemanagerSettings[name] = value
            elif hasattr(child_node, 'hasAttribute') and \
                    child_node.hasAttribute('portaltype'):
                childtype = child_node.getAttribute('portaltype')
                childid = child_node.getAttribute('contentid')
                if childid not in self.context.objectIds():
                    self.context.invokeFactory(childtype, childid)
                child = self.context[childid]
                importer = component.queryMultiAdapter((child, self.environ), 
                                                       gsinterfaces.INode)
                importer.node = child_node
        if pagecachemanager:
            title = pagecachemanager.Title()
            pagecachemanager.manage_editProps(title,
                                              pagecachemanagerSettings)
            logger.info("Cachefu GS profile also updated "
                        "PageCacheManager's settings.")
        self.context.reindexObject()

    def _setFieldValue(self, obj, el):
        ret = None
        
        name = el.getAttribute('name')
        field = obj.Schema().get(name, None)
        if field is None:
            return None
        
        v = el.getAttribute('value')
        if not el.hasAttribute('value'):
            ret = []
            for child in el.childNodes:
                if child.nodeName == 'fieldvalue':
                    ret.append(child.getAttribute('value'))
        elif v and isinstance(field, atapi.BooleanField):
            ret = bool(int(v))
        elif v and isinstance(field, atapi.IntegerField):
            ret = int(v)
        elif v:
            ret = v

        if ret is not None:
            field.getMutator(obj)(ret)

        return ret
    
    def _importNode(self, node):
        """Import the object from the DOM node.
        """

        if self.environ.shouldPurge():
            self._purgeChildContent()
                    
        self._importContentObject(node)

    node = property(_exportNode, _importNode)

    def _purgeChildContent(self):
        self.context.manage_delObjects(ids=self.context.contentIds())

    def _formatValue(self, v):
        ret = v
        if isinstance(v, unicode):
            ret = v.encode('utf-8')
        elif isinstance(v, bool):
            ret = str(int(v))
        else:
            ret = str(v or '')
        return ret

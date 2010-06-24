# Uncomment the following if you use OrderedContainer
# Not imported directly to avoid GPL/ZPL license conflicts
OrderedContainer = None
#from Products.CMFPlone.PloneFolder import OrderedContainer

from OFS.DTMLMethod import DTMLMethod
from OFS.Image import Image, File
from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.FSFile import FSFile
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
from Products.CacheSetup.config import log, OFS_CACHE_ID, CACHE_TOOL_ID
from utils import safe_hasattr
from patch_utils import wrap_method, call

try:
    from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
    PATCH_RR = True
except:
    PATCH_RR = False

# Goal: getting control over old-style files and images.

def patch_ofs():
    # Set default cache manager to 'DefaultCache' for images and files
    log('Associating object with PolicyHTTPCacheManager %s...' % OFS_CACHE_ID)
    for klass in (Image, File):
        log('Associating %s.' % klass.__name__)
        setattr(klass, '_Cacheable__manager_id', OFS_CACHE_ID)

def fs_modified(self):
    """What's the last modification time for this file?
    """
    self._updateFromFS()
    return DateTime(self._file_mod_time)

def ofs_modified(self):
    """What's the last modification time for this object?
    """
    if hasattr(aq_base(self), 'bobobase_modification_time'):
        return self.bobobase_modification_time()
    if hasattr(aq_base(self), '_p_mtime'):
        return DateTime(self._p_mtime)
    return DateTime()

# Goal of the following two: add a modification date to old-style
# images and files and filesystem files and images.

def patch_ofs_modified():
    # Add 'modified' method to File/Image/DTMLMethod.
    for klass in (Image, File, DTMLMethod):
        if hasattr(klass, 'modified'):
            continue
        log('Adding "modified" method to %s.' % klass.__name__)
        setattr(klass, 'modified', ofs_modified)

def patch_fs_modified():
    # Add 'modified' method to FSFile/FSImage/FSDTMLMethod.
    for klass in (FSImage, FSFile, FSDTMLMethod):
        if hasattr(klass, 'modified'):
            continue
        log('Adding "modified" method to %s.' % klass.__name__)
        setattr(klass, 'modified', fs_modified)

# Goal: patch indexing methods to update a counter so we know when
# stuff is changing for ETags. Also call the purge method whenever an
# object is indexed _or_ unindexed so that any relevant purge scripts
# for dependent objects will be called.

from Products.CMFCore.utils import getToolByName
# this import invokes CMFSquidTool's patches
from Products.CMFSquidTool.queue import queue
queueObject = queue.queue

# Sub-goal is to increment a counter on every catalog change.
    
def _purge(self, purge_squid=True):
    if purge_squid:
        ps = getToolByName(self, 'portal_squid', None)
        if ps is None:
            return
        queueObject(self)
    pcs = getToolByName(self, 'portal_cache_settings', None)
    if pcs is None:
        return
    pcs.incrementCatalogCount()

def catalog_object(self, obj, uid=None, idxs=None, update_metadata=1,
                   pghandler=None):
    """ZCatalog.catalog_object"""

    _purge(obj)
    try:
        return call(self, 'catalog_object', obj, 
                    uid, idxs, update_metadata, pghandler)
    except:
        # BBB for Zope2.7
        return call(self, 'catalog_object', obj, uid, idxs,
                    update_metadata)

def uncatalog_object(self, uid):
    """ZCatalog.uncatalog_object"""

    # We need to resolve the uid if we want this to be valuable at
    # all, doing so is potentially expensive and likely to fail. So
    # don't purge squid.
    _purge(self, purge_squid=False)
    return call(self, 'uncatalog_object', uid)

def moveObjectsByDelta(self, ids, delta, subset_ids=None):
    """Move specified sub-objects by delta."""
    _purge(self)
    return call(self, 'moveObjectsByDelta', 
                ids=ids, delta=delta, subset_ids=subset_ids)

# Goal: signal a change in portal_css or portal_javascript by
# incrementing the internal catalog counter (which is often used to
# determine freshness).

def cookResources(self):
    """Cook the stored resources."""
    parent = self.getParentNode()
    if safe_hasattr(parent, CACHE_TOOL_ID):
        pcs = getattr(parent, CACHE_TOOL_ID)
        # clear out page cache
        pcs.manage_purgePageCache()
        # bump the catalog count to nuke (some) etag-cached content
        pcs.incrementCatalogCount()
    return call(self, 'cookResources')

# Goal: Increment a counter every time the relationship between
# permissions and roles changes

def _incrementPermissionCount(self):
    try:
        pcs = getToolByName(self, 'portal_cache_settings')
    except AttributeError:
        return
    pcs.incrementPermissionCount()

from AccessControl.Role import RoleManager

def manage_role(self, role_to_manage, permissions=[], REQUEST=None):
    """This method is called TTW, so it needs a docstring"""
    retval = call(self, 'manage_role', role_to_manage, permissions, REQUEST)
    _incrementPermissionCount(self)
    return retval

def manage_acquiredPermissions(self, permissions=[], REQUEST=None):
    """This method is called TTW, so it needs a docstring"""
    retval = call(self, 'manage_acquiredPermissions', permissions, REQUEST)
    _incrementPermissionCount(self)
    return retval

def manage_permission(self, permission_to_manage,
                      roles=[], acquire=0, REQUEST=None):
    """This method is called TTW, so it needs a docstring"""
    retval = call(self, 'manage_permission', permission_to_manage, roles, acquire, REQUEST)
    _incrementPermissionCount(self)
    return retval

def manage_changePermissions(self, REQUEST):
    """This method is called TTW, so it needs a docstring"""
    retval = call(self, 'manage_changePermissions', REQUEST)
    _incrementPermissionCount(self)
    return retval


def run():
    log('Applying patches...')
    patch_ofs()
    patch_ofs_modified()
    patch_fs_modified()

    from Products.CMFSquidTool.patch import unwrap_method as squidtool_unwrap_method
    from Products.ZCatalog.ZCatalog import ZCatalog
    from Products.Archetypes.OrderedBaseFolder import OrderedContainer as ATOrderedContainer
    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
    from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
    # remove CMFSquidTool's patches
    squidtool_unwrap_method(CMFCatalogAware, 'reindexObject')
    squidtool_unwrap_method(CatalogMultiplex, 'reindexObject')
    # add in our own patches
    wrap_method(ZCatalog, 'catalog_object', catalog_object)
    wrap_method(ZCatalog, 'uncatalog_object', uncatalog_object)
    if OrderedContainer is not None:
        wrap_method(OrderedContainer, 'moveObjectsByDelta', moveObjectsByDelta)
    wrap_method(ATOrderedContainer, 'moveObjectsByDelta', moveObjectsByDelta)
    if PATCH_RR:
        wrap_method(BaseRegistryTool, 'cookResources', cookResources)
    wrap_method(RoleManager, 'manage_role', manage_role)
    wrap_method(RoleManager, 'manage_acquiredPermissions', manage_acquiredPermissions)
    wrap_method(RoleManager, 'manage_permission', manage_permission)
    wrap_method(RoleManager, 'manage_changePermissions', manage_changePermissions)

    log('Patches applied.')

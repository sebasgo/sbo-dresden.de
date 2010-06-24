from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CachingPolicyManager
from Products.CMFCore.interfaces import ICachingPolicyManager
from Products.CacheSetup.config import PROJECT_NAME, GLOBALS, \
     CACHE_TOOL_ID, PAGE_CACHE_MANAGER_ID, OFS_CACHE_ID, RR_CACHE_ID, CPM_ID

try:
    from Products.PageCacheManager import PageCacheManager
except ImportError:
    PageCacheManager = None
try:
    from Products.PolicyHTTPCacheManager import PolicyHTTPCacheManager
except ImportError:
    PolicyHTTPCacheManager = None
from Products.StandardCacheManagers import RAMCacheManager, AcceleratedHTTPCacheManager
from Products.CacheSetup.utils import base_hasattr

def enableCacheFu(self, enabled):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if enabled:
        installPageCacheManager(portal)
        removeCachingPolicyManager(portal)
        setupPolicyHTTPCaches(portal)
        setupResourceRegistry(portal)
    else:
        removePageCacheManager(portal)
        restoreCachingPolicyManager(portal)
        restoreResourceRegistry(portal)
        removePolicyHTTPCaches(portal)


def installPageCacheManager(portal):
    if PageCacheManager is None:
        raise ValueError, 'Please add PageCacheManager to your Products directory'
    id = PAGE_CACHE_MANAGER_ID
    if not id in portal.objectIds():
        PageCacheManager.manage_addPageCacheManager(portal, id)
        pcm = getattr(portal, id)
        pcm.setTitle('Page Cache Manager')

def removePageCacheManager(portal):
    id = PAGE_CACHE_MANAGER_ID
    if hasattr(portal, id):
        portal.manage_delObjects([id])


def removeCachingPolicyManager(portal):
    cpm = getattr(portal, CPM_ID, None)
    if not cpm.__class__ == CachingPolicyManager.CachingPolicyManager:
        return
    
    old_policies = []
    if cpm:
        for id, p in cpm.listPolicies():
            # crude check for right version of CMF
            if getattr(p, 'getSMaxAgeSecs', None):
                old_policies.append(
                    {'policy_id': id,
                     'predicate': p.getPredicate(),
                     'mtime_func': p.getMTimeFunc(),
                     'max_age_secs': p.getMaxAgeSecs(),
                     'no_cache': p.getNoCache(),
                     'no_store': p.getNoStore(),
                     'must_revalidate': p.getMustRevalidate(),
                     'vary': p.getVary(),
                     'etag_func': p.getETagFunc(),
                     's_max_age_secs': p.getSMaxAgeSecs(),
                     'proxy_revalidate': p.getProxyRevalidate(),
                     'public': p.getPublic(),
                     'private': p.getPrivate(),
                     'no_transform': p.getNoTransform(),
                     'enable_304s': p.getEnable304s(),
                     'last_modified': p.getLastModified(),
                     'pre_check': p.getPreCheck(),
                     'post_check': p.getPostCheck(),
                     })
        portal.manage_delObjects([CPM_ID])
    pcs = getattr(portal, CACHE_TOOL_ID)
    pcs.old_policies = old_policies
    portal.manage_addProduct['CacheSetup'].manage_addTool('CacheFu Caching Policy Manager')
    # for Plone 3.0 we need to register this as a local utility
    sm = getSiteManager(portal)
    if getattr(sm, 'registerUtility', None) is not None:
        sm.registerUtility(getattr(portal, CPM_ID), ICachingPolicyManager)

def restoreCachingPolicyManager(portal):
    # for Plone 3.0 we need to unregister the cachefu cpm
    sm = getSiteManager(portal)
    if getattr(sm, 'unregisterUtility', None) is not None:
        sm.unregisterUtility(getattr(portal, CPM_ID), ICachingPolicyManager)
    
    # now let's restore the old cpm
    portal.manage_delObjects([CPM_ID])
    pcs = getattr(portal, CACHE_TOOL_ID, None)
    if pcs:
        old_policies = getattr(pcs, 'old_policies', [])
    else:
        old_policies = []
    CachingPolicyManager.manage_addCachingPolicyManager(portal)
    cpm = getattr(portal, CPM_ID)
    for p in old_policies:
        cpm.addPolicy(p['policy_id'], p['predicate'], p['mtime_func'], p['max_age_secs'],
                      p['no_cache'], p['no_store'], p['must_revalidate'], p['vary'],
                      p['etag_func'], None, p['s_max_age_secs'], p['proxy_revalidate'], 
                      p['public'], p['private'], p['no_transform'], p['enable_304s'],
                      p['last_modified'], p['pre_check'], p['post_check'])


def setupResourceRegistry(portal):
    ram_cache_id = RR_CACHE_ID
    if not ram_cache_id in portal.objectIds():
        RAMCacheManager.manage_addRAMCacheManager(portal, ram_cache_id)
        cache = getattr(portal, ram_cache_id)
        settings = cache.getSettings()
        settings['max_age'] = 24*3600 # keep for up to 24 hours
        settings['request_vars'] = ('URL',)
        cache.manage_editProps('Cache for saved ResourceRegistry files', settings)
    reg = getToolByName(portal, 'portal_css', None)
    if reg is not None and base_hasattr(reg, 'ZCacheable_setManagerId'):
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)
    reg = getToolByName(portal, 'portal_javascripts', None)
    if reg is not None and base_hasattr(reg, 'ZCacheable_setManagerId'):
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)

def restoreResourceRegistry(portal):
    reg = getToolByName(portal, 'portal_css', None)
    if reg is not None and base_hasattr(reg, 'ZCacheable_setManagerId'):
        reg.ZCacheable_setManagerId(None)
        reg.ZCacheable_setEnabled(0)
    reg = getToolByName(portal, 'portal_javascripts', None)
    if reg is not None and base_hasattr(reg, 'ZCacheable_setManagerId'):
        reg.ZCacheable_setManagerId(None)
        reg.ZCacheable_setEnabled(0)
    ram_cache_id = RR_CACHE_ID
    if hasattr(portal, ram_cache_id):
        portal.manage_delObjects([ram_cache_id])


def setupPolicyHTTPCaches(portal):
    if PolicyHTTPCacheManager is None:
        raise ValueError, 'Please add PolicyHTTPCacheManager to your Products directory'
    meta_type = PolicyHTTPCacheManager.PolicyHTTPCacheManager.meta_type
    for cache_id in ('HTTPCache', OFS_CACHE_ID):
        if cache_id not in portal.objectIds(spec=meta_type):
            if cache_id in portal.objectIds():
                portal.manage_delObjects([cache_id])
            PolicyHTTPCacheManager.manage_addPolicyHTTPCacheManager(portal, cache_id)

def removePolicyHTTPCaches(portal):
    for obj in ['HTTPCache', OFS_CACHE_ID]:
        if hasattr(portal, obj):
            portal.manage_delObjects([obj])
    AcceleratedHTTPCacheManager.manage_addAcceleratedHTTPCacheManager(portal, 'HTTPCache')






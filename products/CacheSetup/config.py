from zLOG import LOG, INFO, BLATHER
# BBB: CMF < 1.5
try:
    from Products.CMFCore.permissions import AddPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalContent

GLOBALS = globals()

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECT_NAME = 'CacheSetup'
SKINS_DIR = 'skins'

PAGE_CACHE_MANAGER_ID = 'CacheSetup_PageCache'
OFS_CACHE_ID = 'CacheSetup_OFSCache'
RR_CACHE_ID = 'CacheSetup_ResourceRegistryCache'
CPM_ID = 'caching_policy_manager'

TOOL_ID = CACHE_TOOL_ID = 'portal_cache_settings'
RULES_ID = 'rules'
RULE_TYPES = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')
HEADERSETS_ID = 'headersets'
HEADERSET_TYPES = ('HeaderSet',)
DEFAULT_POLICY_ID = 'default-cache-policy'

TOOL_TYPE = 'CacheTool'
POLICY_TYPE = 'CachePolicy'
RULEFOLDER_TYPE = 'RuleFolder'
HEADERSETFOLDER_TYPE = 'HeaderSetFolder'
FOLDER_TYPES = (TOOL_TYPE, POLICY_TYPE, RULEFOLDER_TYPE, HEADERSETFOLDER_TYPE)
FOLDER_ITEM_TYPES = RULE_TYPES + HEADERSET_TYPES
TYPES = FOLDER_TYPES + FOLDER_ITEM_TYPES

TOOL_TITLE = 'Cache Configuration Tool'
CONFIGLET_ID = 'CacheSetupPrefs'


# TODO: remove this log() method
def log(msg, level=BLATHER):
    LOG(PROJECT_NAME, level, msg)

from Products.CMFPlone.utils import getFSVersionTuple
_ploneVersion = getFSVersionTuple()
_major = _ploneVersion[0]
_minor = _ploneVersion[1]
if (_major == 2) and (_minor == 5):
    PLONE25 = True
else:
    PLONE25 = False


# Vocabulary for compression
USE_COMPRESSION = (
    ('never','Never'),
    ('always','Always'),
    ('accept-encoding','Use Accept-Encoding header'),
    ('accept-encoding+user-agent','Use Accept-Encoding and User-Agent headers'),
)

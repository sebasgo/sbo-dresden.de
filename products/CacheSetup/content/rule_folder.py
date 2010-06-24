"""Rule folder implementation

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
from Products.CacheSetup.interfaces import ICacheToolFolder
from Products.CacheSetup.config import PROJECT_NAME
from nocatalog import NoCatalog

try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions

class RuleFolder(NoCatalog, atapi.OrderedBaseFolder):
    """A container for rule objects"""

    __implements__ = (atapi.OrderedBaseFolder.__implements__, ICacheToolFolder)
    
    security = ClassSecurityInfo()
    archetype_name = 'Rule Folder'
    portal_type = meta_type = 'RuleFolder'
    global_allow = 0
    allowed_content_types = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')

    actions = (
        {'action':      'string:$object_url',
         'category':    'object',
         'id':          'view',
         'name':        'Cache Setup',
         'permissions': (permissions.ManagePortal,),
         'visible':     False},
    )

    aliases = {
        '(Default)':    'cache_policy_item_config',
        'view' :        'cache_policy_item_config',
        'edit' :        'cache_policy_item_config'
    }

atapi.registerType(RuleFolder, PROJECT_NAME)

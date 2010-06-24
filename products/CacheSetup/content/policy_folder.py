"""Cache Policy folder implementation

$Id: $
"""

__authors__ = 'Ricardo Newbery <ric@digitalmarbles.com>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
from Products.CacheSetup.interfaces import ICachePolicy
from Products.CacheSetup.config import PROJECT_NAME, RULES_ID, HEADERSETS_ID
from nocatalog import NoCatalog

try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions

schema = atapi.OrderedBaseFolder.schema.copy()
schema['id'].widget.ignore_visible_ids=True                       
# schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Cache-Policy-Id' header with this id will be added."

class CachePolicy(NoCatalog, atapi.OrderedBaseFolder):
    """A container for cache policies"""

    __implements__ = (atapi.OrderedBaseFolder.__implements__, ICachePolicy)
    
    security = ClassSecurityInfo()
    archetype_name = 'Cache Policy'
    portal_type = meta_type = 'CachePolicy'
    content_icon = 'cachesetup_tool_icon.gif'
    schema = schema
    global_allow = 0
    allowed_content_types = ['RuleFolder', 'HeaderSetFolder']
    
    actions = (
        {'action':      'string:$object_url',
         'category':    'object',
         'id':          'view',
         'name':        'Cache Policy',
         'permissions': (permissions.ManagePortal,),
         'visible':     False},
    )

    aliases = {
        '(Default)':    'cache_policy_config',
        'view' :        'cache_policy_config',
        'edit' :        'cache_policy_config'
    }

    def at_post_create_script(self):
        self.allowed_content_types = ['RuleFolder', 'HeaderSetFolder']
        
        self.invokeFactory(id=RULES_ID, type_name='RuleFolder')
        rules = getattr(self, RULES_ID)
        rules.unmarkCreationFlag()
        rules.setTitle('Rules')
        rules.reindexObject()

        self.invokeFactory(id=HEADERSETS_ID, type_name='HeaderSetFolder')
        header_sets = getattr(self, HEADERSETS_ID)
        header_sets.unmarkCreationFlag()
        header_sets.setTitle('Headers')
        header_sets.reindexObject()

        self.allowed_content_types = []

        

atapi.registerType(CachePolicy, PROJECT_NAME)

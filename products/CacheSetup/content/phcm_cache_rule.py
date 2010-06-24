"""
CacheSetup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.utils import base_hasattr
from Products.CacheSetup.config import PROJECT_NAME
import base_cache_rule as BaseCacheRule

schema = atapi.BaseContent.schema.copy() + \
         atapi.Schema((atapi.TextField('description',
                                         required=0,
                                         allowable_content_types = ('text/plain',),
                                         default='A cache rule for objects associated with an PolicyHTTPCachingManager',
                                         widget=atapi.TextAreaWidget(label='Description',
                                                                     description='Basic documentation for this cache rule',
                                                                     cols=60,
                                                                     rows=5,),
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.StringField('cacheManager',
                                         default='HTTPCache',
                                         widget=atapi.SelectionWidget(label='Cache Manager',
                                                                      description='This rule will apply to content associated with the specified PolicyHTTPCacheManager manager.'),
                                         vocabulary='getPolicyHTTPCacheManagerVocabulary',
                                         enforce_vocabulary=1,
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.LinesField('types',
                                        default=(),
                                        widget=atapi.MultiSelectionWidget(label='Types',
                                                                          description='Please select the types to which this rule applies.  Leave empty for all types.',
                                                                          size=10),
                                        multiValued = 1,
                                        vocabulary='getContentTypesVocabulary',
                                        enforce_vocabulary = 1,
                                        write_permission = permissions.ManagePortal,
                                        ),
                       atapi.LinesField('ids',
                                         default=(),
                                         widget=atapi.LinesWidget(label='Ids',
                                                                  description='IDs of the objects to which this rule applies.  Leave empty for all objects.',
                                                                  size=5),
                                         multiValued = 1,
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.LinesField('cacheStop',
                                        default=('portal_status_message','statusmessages'),
                                        widget=atapi.LinesWidget(label='Cache Preventing Request Items',
                                                                 description='Tokens in the request that prevent caching if present'),
                                        write_permission = permissions.ManagePortal,
                                        ),
                       )) + \
         BaseCacheRule.header_set_schema
                       
schema['id'].widget.ignore_visible_ids=True                       
schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Caching-Rule-Id' header with this id will be added."

class PolicyHTTPCacheManagerCacheRule(BaseCacheRule.BaseCacheRule, atapi.BaseContent):
    """
    """
    security = ClassSecurityInfo()
    archetype_name = 'PolicyHTTPCacheManager Cache Rule'
    portal_type = meta_type = 'PolicyHTTPCacheManagerCacheRule'
    __implements__ = (atapi.BaseContent.__implements__, BaseCacheRule.BaseCacheRule.__implements__)
    schema = schema
    _at_rename_after_creation = True

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

    def getContentTypesVocabulary(self):
        tt = getToolByName(self, 'portal_types')
        types_list = [(t.getId(), t.getProperty('title') and t.getProperty('title') or t.getId()) for t in tt.listTypeInfo()]
        types_list.sort(lambda x, y: cmp(x[1], y[1]))
        return atapi.DisplayList(tuple(types_list))
    
    def getPolicyHTTPCacheManagerVocabulary(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        phcm = portal.objectIds(spec='Policy HTTP Cache Manager')
        return atapi.DisplayList(tuple([(p,p) for p in phcm]))

    def getEtag(self, request, object, view, member, header_set=None):
        pass

    security.declarePublic('getHeaderSet')
    def getHeaderSet(self, request, object, view, member):
        # see if this rule applies
        if not base_hasattr(object, 'ZCacheable_getManagerId'):
            return
        if object.ZCacheable_getManagerId() != self.getCacheManager():
            return
        types = self.getTypes()
        if not base_hasattr(object, 'meta_type'):
            return
        if types and object.meta_type not in types:
            return
        if not base_hasattr(object, 'getId'):
            return
        ids = self.getIds()
        if ids and object.getId() not in ids:
            return

        header_set = self._getHeaderSet(request, object, view, member)
        return header_set

atapi.registerType(PolicyHTTPCacheManagerCacheRule, PROJECT_NAME)

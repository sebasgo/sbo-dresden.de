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
from Products.CacheSetup.config import PROJECT_NAME
import base_cache_rule as BaseCacheRule

schema = atapi.BaseContent.schema.copy() + \
         atapi.Schema((atapi.TextField('description',
                                         required=0,
                                         allowable_content_types = ('text/plain',),
                                         default='A cache rule for page templates',
                                         widget=atapi.TextAreaWidget(label='Description',
                                                                     description='Basic documentation for this cache rule',
                                                                     cols=60,
                                                                     rows=5,),
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.LinesField('templates',
                                        widget=atapi.LinesWidget(label='Templates',
                                                                 description='Please indicate the template IDs to which this rule applies'),
                                        write_permission = permissions.ManagePortal,
                                        ),
                       )) + \
         BaseCacheRule.header_set_schema + \
         BaseCacheRule.etag_schema

schema['id'].widget.ignore_visible_ids=True                       
schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Caching-Rule-Id' header with this id will be added."

class TemplateCacheRule(BaseCacheRule.BaseCacheRule, atapi.BaseContent):
    """
    """
    security = ClassSecurityInfo()
    archetype_name = 'Template Cache Rule'
    portal_type = meta_type = 'TemplateCacheRule'
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

    security.declarePublic('getHeaderSet')
    def getHeaderSet(self, request, object, view, member):
        # see if this rule applies
        if not view in self.getTemplates():
            return None

        header_set = self._getHeaderSet(request, object, view, member)

        # associate template with PageCacheManager
        if header_set and header_set.getPageCache():
            self._associateTemplate(object, view)
            
        return header_set

atapi.registerType(TemplateCacheRule, PROJECT_NAME)

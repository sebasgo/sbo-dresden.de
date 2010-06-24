"""
CacheSetup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
from Products.Archetypes.public import listTypes
from Products.Archetypes.interfaces import IBaseObject

try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions
from Products.CMFCore import Expression
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.config import PROJECT_NAME
from Products.CacheSetup.utils import base_hasattr
import base_cache_rule as BaseCacheRule

schema = atapi.BaseContent.schema.copy() + \
         atapi.Schema(
     (atapi.TextField('description',
                required=0,
                allowable_content_types = ('text/plain',),
                default='A cache rule for CMF content types',
                widget=atapi.TextAreaWidget(
                    label='Description',
                    description='Basic documentation for this cache rule',
                    cols=60,
                    rows=5,),
                write_permission = permissions.ManagePortal,
                ),
     atapi.LinesField('contentTypes',
                required=1,
                default=(),
                widget=atapi.MultiSelectionWidget(
                    label='Content Types',
                    description='Please indicate the content types to which this rule applies',
                    size=10),
                multiValued = 1,
                vocabulary='getContentTypesVocabulary',
                write_permission = permissions.ManagePortal,
                ),
     atapi.BooleanField('defaultView',
                default=1,
                widget=atapi.BooleanWidget(
                    label='Default View',
                    description='Should this rule apply to the default view of this content object? The "default view" is the '
                                'template that is shown when the user navigates to a content object without appending a template '
                                'or view id to the end of the URL.'),
                write_permission = permissions.ManagePortal,
                ),
     atapi.LinesField('templates',
                widget=atapi.LinesWidget(
                    label='Templates',
                    description='IDs for additional templates to which this rule should apply, one per line. If the template is ' 
                                'a Zope 3-style view, enter its name without the @@ prefix. For example, to cache ' 
                                'the @@types-controlpanel view (probably not a good idea), enter "types-controlpanel"'),
                write_permission = permissions.ManagePortal,
                ),
     )) + \
     BaseCacheRule.header_set_schema + \
     BaseCacheRule.etag_schema + \
     atapi.Schema((
     atapi.StringField('purgeExpression',
                required=0,
                widget=atapi.StringWidget(
                    label='Purge Expression',
                    description='A TALES expression that generates a list of additional URLs to purge (URLs should be relative to the portal root) when an object is reindexed.  Available values: request, object.',
                    size=80),
                write_permission = permissions.ManagePortal,
                ),
        ))

schema['id'].widget.ignore_visible_ids=True                       
schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Caching-Rule-Id' header with this id will be added."

class ContentCacheRule(BaseCacheRule.BaseCacheRule, atapi.BaseContent):
    """
    """
    security = ClassSecurityInfo()
    archetype_name = 'Content Cache Rule'
    portal_type = meta_type = 'ContentCacheRule'
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

    def getPurgeExpression(self):
        expression = self.getField('purgeExpression').get(self)
        if expression:
            return expression.text
        
    def setPurgeExpression(self, expression):
        return self.getField('purgeExpression').set(self, Expression.Expression(expression))

    def validate_purgeExpression(self, expression):
        return self._validate_expression(expression)

    def getPurgeExpressionValue(self, expr_context):
        expression = self.getField('purgeExpression').get(self)
        if expression:
            return expression(expr_context)

    security.declarePublic('getHeaderSet')
    def getHeaderSet(self, request, object, view, member):
        # see if this rule applies
        if not base_hasattr(object, 'portal_type'):
            return
        if object.portal_type not in self.getContentTypes():
            return None
        if view not in self.getTemplates() and \
           not (self.getDefaultView() and view == self.getObjectDefaultView(object)):
            return None

        header_set = self._getHeaderSet(request, object, view, member)

        # associate template with PageCacheManager
        if header_set and header_set.getPageCache():
            self._associateTemplate(object, view)
            
        return header_set


    def _getViewsUrlsForObject(self, object):
        """return a list of relative URLs to the possible views for an object"""
        suffixes = []
        if self.getDefaultView():
            suffixes.extend(['', '/', '/view', '/'+self.getObjectDefaultView(object)])
        templates = self.getTemplates()
        if templates:
            for t in templates:
                if t:
                    if t.startswith('/'):
                        suffixes.append(t)
                    else:
                        suffixes.append('/'+t)

        return suffixes


    def _getObjectFieldUrls(self, object):
        """return a list of relative URLs to fields for an object"""
        if not IBaseObject.providedBy(object):
            return []

        schema = object.Schema()

        def InterestingField(field):
            # Argh. Evil Z2 interfaces alert.
            return field.getType() in ["Products.Archetypes.Field.ImageField",
                                       "Products.Archetypes.Field.FieldField"]

        urls=[]
        for field in schema.filterFields(InterestingField):
            baseurl="/"+field.getName()
            urls.append(baseurl)

            if field.getType()=="Products.Archetypes.Field.ImageField":
                for size in field.getAvailableSizes(object).keys():
                    urls.append("%s_%s" % (baseurl, size))

        return urls



    security.declarePublic('getRelativeUrlsToPurge')
    def getRelativeUrlsToPurge(self, object, urls):
        if object.portal_type == "Discussion Item":
            object=self.plone_utils.getDiscussionThread(object)[0]

        # Abort if this is not a known content
        if object.portal_type not in self.getContentTypes():
            return

        suffixes=self._getViewsUrlsForObject(object)
        suffixes.extend(self._getObjectFieldUrls(object))

        if suffixes:
            url_tool = getToolByName(self, 'portal_url')
            obj_url = url_tool.getRelativeUrl(object)
            urls.union_update([obj_url + s for s in suffixes])
            portal = url_tool.getPortalObject()
            if object.aq_base is not portal:
                parent = object.getParentNode()
                parent_default_view = self.getObjectDefaultView(parent)
                if object.getId() == parent_default_view:
                    parent_url = url_tool.getRelativeUrl(parent)
                    urls.union_update([parent_url + s for s in ('','/','/view', '/'+parent_default_view)])


        purge_expression = self.getPurgeExpression()
        if purge_expression:
            expr_context = self._getExpressionContext(self.REQUEST, object, None, None)
            urls.union_update(self.getPurgeExpressionValue(expr_context))

    def getContentTypesVocabulary(self):
        tt = getToolByName(self, 'portal_types')
        types_list = []

        from Products.Archetypes.public import listTypes
        cachefu_types = [t['portal_type'] for t in listTypes(PROJECT_NAME)]

        atct_criteria = []
        try:
            from Products.ATContentTypes.config import PROJECTNAME as ATCTNAME
            from Products.ATContentTypes.interfaces import IATTopicCriterion
            for t in listTypes(ATCTNAME):
                if IATTopicCriterion.isImplementedByInstancesOf(t['klass']):
                    atct_criteria.append(t['portal_type'])
        except:
            pass

        for t in tt.listTypeInfo():
            # filter out a few types
            id = t.getId()
            if id == 'TempFolder':
                continue
            if id in cachefu_types:
                continue
            if id in atct_criteria:
                continue
            
            title = t.getProperty('title')
            if not title:
                title = id
            else:
                if title != id:
                    title = '%s (%s)' % (title, id)
            types_list.append((id, title))
        types_list.sort(lambda x, y: cmp(x[1], y[1]))
        return atapi.DisplayList(tuple(types_list))

atapi.registerType(ContentCacheRule, PROJECT_NAME)

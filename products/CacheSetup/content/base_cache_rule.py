"""
CacheSetup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from urllib import quote
from Acquisition import aq_inner
from Products.CMFPlone.interfaces import IBrowserDefault

from AccessControl import ClassSecurityInfo
from AccessControl.User import nobody
import DateTime
from Products.PageTemplates.Expressions import getEngine, SecureModuleImporter
from Products.PageTemplates.TALES import CompilerError
from ZopeUndo.Prefix import Prefix

from Products.Archetypes import public as atapi
try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions
from Products.CMFCore import Expression
from Products.CMFCore.utils import getToolByName

from Products.CacheSetup.utils import base_hasattr
from Products.CacheSetup.config import CACHE_TOOL_ID, PAGE_CACHE_MANAGER_ID
from Products.CacheSetup.interfaces import ICacheRule
from nocatalog import NoCatalog

header_set_schema = atapi.Schema((
                       atapi.LinesField('cacheStop',
                                        default=('portal_status_message','statusmessages'),
                                        widget=atapi.LinesWidget(label='Cache Preventing Request Values',
                                                                 description='Values in the request that prevent caching if present'),
                                        write_permission = permissions.ManagePortal,
                                        ),
                       atapi.StringField('predicateExpression',
                                         required=0,
                                         edit_accessor='getPredicateExpression',
                                         widget=atapi.StringWidget(label='Predicate',
                                                                   description='A TALES expression for determining whether this rule applies.  Available variables = request, object, view (ID of the current template), member (None if anonymous).',
                                                                   size=80),
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.StringField('headerSetIdAnon',
                                         default='cache-with-etag',
                                         widget=atapi.SelectionWidget(label='Header Set for Anonymous Users',
                                                                      description='Header set for anonymous users.'),
                                         vocabulary='getHeaderSetVocabulary',
                                         enforce_vocabulary = 1,
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.StringField('headerSetIdAuth',
                                         default='cache-with-etag',
                                         widget=atapi.SelectionWidget(label='Header Set for Authenticated Users',
                                                                      description='Header set for authenticated users.'),
                                         vocabulary='getHeaderSetVocabulary',
                                         enforce_vocabulary = 1,
                                         write_permission = permissions.ManagePortal,
                                         ),

                       atapi.StringField('headerSetIdExpression',
                                         required=0,
                                         edit_accessor='getHeaderSetIdExpression',
                                         widget=atapi.StringWidget(label='Header Set Expression',
                                                                   description='A TALES expression that returns the ID of the header set to be used.  Applied if the header set specified above is set to "Expression".  Available variables = request, object, view (ID of the current template), member (None if anonymous)',
                                                                   size=80),
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.StringField('lastModifiedExpression',
                                         default='python:object.modified()',
                                         edit_accessor='getLastModifiedExpression',
                                         widget=atapi.StringWidget(label='Last-Modified Expression',
                                                                   description='An expression used to obtain the last-modified time for the page.  Used in setting the Last-Modified header',
                                                                   size=80),
                                         write_permission = permissions.ManagePortal,
                                         ),
                       atapi.StringField('varyExpression',
                                          required=0,
                                          default='python: rule.portal_cache_settings.getVaryHeader()',
                                          edit_accessor='getVaryExpression',
                                          widget=atapi.StringWidget(label='Vary Expression',
                                                                    description='A TALES expression that will be used to generate the Vary header.  Available values: request, object, view (the template ID), member (None if Anonymous)',
                                                                    size=80),
                                          write_permission = permissions.ManagePortal,
                                          ),
                       ))
etag_schema = atapi.Schema((
                       atapi.LinesField('etagComponents',
                                         default=('member','skin','language','gzip','catalog_modified'),
                                         widget=atapi.MultiSelectionWidget(label='ETag Components',
                                                                           description='Items used to construct the ETag',
                                                                           format='checkbox',),
                                         multiValued=1,
                                         vocabulary=atapi.DisplayList((('member','Current member\'s ID'),
                                                                       ('roles','Current member\'s roles'),
                                                                       ('permissions','Current member\'s permissions'),
                                                                       ('skin','Current skin'),
                                                                       ('language','Browser\'s preferred language'),
                                                                       ('user_language','User\'s preferred language'),
                                                                       ('gzip','Browser can receive gzipped content'),
                                                                       ('last_modified','Context modification time'),
                                                                       ('catalog_modified', 'Time of last catalog change'),
                                                                       )),
                                         enforce_vocabulary = 1,
                                         write_permission = permissions.ManagePortal,
                                        ),
                       atapi.LinesField('etagRequestValues',
                                         default=(),
                                         widget=atapi.LinesWidget(label='ETag Request Values',
                                                                  description='Request values used to construct the ETag'),
                                         write_permission = permissions.ManagePortal,
                                        ),
                       atapi.IntegerField('etagTimeout',
                                          required=0,
                                          default=3600,
                                          widget=atapi.IntegerWidget(label='ETag Timeout',
                                                                     description='Maximum amount of time an ETag is valid (leave blank for forever)'),
                                          write_permission = permissions.ManagePortal,
                                          ),
                       atapi.StringField('etagExpression',
                                          required=0,
                                          edit_accessor='getEtagExpression',
                                          widget=atapi.StringWidget(label='ETag Expression',
                                                                    description='A TALES expression that will be appended to the ETag generated with the above settings when "The expression below" is selected.  Available values: request, object, view (the template ID), member (None if Anonymous)',
                                                                    size=80),
                                          write_permission = permissions.ManagePortal,
                                          ),
             ))

class BaseCacheRule(NoCatalog):
    """
    """
    security = ClassSecurityInfo()
    global_allow = 0
    _at_rename_after_creation = True

    __implements__ = (ICacheRule,)

    def _validate_expression(self, expression):
        try:
            getEngine().compile(expression)
        except CompilerError, e:
            return 'Bad expression:', str(e)
        except:
            raise

    def getPredicateExpression(self):
        expression = self.getField('predicateExpression').get(self)
        if expression:
            return expression.text
        
    def setPredicateExpression(self, expression):
        if expression is None:
            expression = ''
        return self.getField('predicateExpression').set(self, Expression.Expression(expression))

    def validate_predicateExpression(self, expression):
        return self._validate_expression(expression)

    def testPredicate(self, expr_context):
        expression = self.getField('predicateExpression').get(self)
        if expression:
            if not expression.text:  # empty expression
                return True
            return expression(expr_context)

    def getEtagExpression(self):
        expression = self.getField('etagExpression').get(self)
        if expression:
            return expression.text
        
    def setEtagExpression(self, expression):
        if expression is None:
            expression = ''
        return self.getField('etagExpression').set(self, Expression.Expression(expression))

    def validate_etagExpression(self, expression):
        return self._validate_expression(expression)

    def getEtagExpressionValue(self, expr_context):
        expression = self.getField('etagExpression').get(self)
        if expression:
            return expression(expr_context)

    def getHeaderSetIdExpression(self):
        expression = self.getField('headerSetIdExpression').get(self)
        if expression:
            return expression.text
        
    def setHeaderSetIdExpression(self, expression):
        if expression is None:
            expression = ''
        return self.getField('headerSetIdExpression').set(self, Expression.Expression(expression))

    def validate_headerSetIdExpression(self, expression):
        return self._validate_expression(expression)

    def getHeaderSetIdExpressionValue(self, expr_context):
        expression = self.getField('headerSetIdExpression').get(self)
        if expression:
            return expression(expr_context)

    def getLastModifiedExpression(self):
        expression = self.getField('lastModifiedExpression').get(self)
        if expression:
            return expression.text
        
    def setLastModifiedExpression(self, expression):
        if expression is None:
            expression = ''
        return self.getField('lastModifiedExpression').set(self, Expression.Expression(expression))

    def validate_lastModifiedExpression(self, expression):
        return self._validate_expression(expression)

    def getLastModified(self, expr_context):
        expression = self.getField('lastModifiedExpression').get(self)
        if expression:
            return expression(expr_context)

    def lastDate(self, *dates):
        if len(dates) == 0:
            return self.portal_cache_settings.modified()
        dates = list(dates)
        timeout = self.getEtagTimeout()
        if timeout:
            time = DateTime.DateTime()
            time = timeout * (int(time.timeTime()/timeout) - 1)
            time = DateTime.DateTime(time)
            dates.append(time)
        dates.sort()
        return dates[-1]

    def getLastTransactionDate(self, context=None):
        spec = {}
        if context is None:
            context = getToolByName(self, 'portal_url').getPortalObject()
        path = '/'.join(context.getPhysicalPath())
        spec['description'] = Prefix(path)
        lastTransaction = self._p_jar.db().undoInfo(0, 1, spec)
        if len(lastTransaction) == 0:
            return DateTime.DateTime(self.Control_Panel.process_start)
        return DateTime.DateTime(lastTransaction[0]['time'])

    def getVaryExpression(self):
        expression = self.getField('varyExpression').get(self)
        if expression:
            return expression.text
        
    def setVaryExpression(self, expression):
        if expression is None:
            expression = ''
        return self.getField('varyExpression').set(self, Expression.Expression(expression))

    def validate_varyExpression(self, expression):
        return self._validate_expression(expression)

    def getVary(self, expr_context):
        expression = self.getField('varyExpression').get(self)
        if expression:
            return expression(expr_context)

    def _getExpressionContext(self, request, object, view, member, keywords=(), time=None):
        """Construct an expression context for TALES expressions used in cache rules and header sets"""
        if time is None:
            time = DateTime.DateTime()
        data = {'rule'     : self,
                'request'  : request,
                'object'   : object,
                'view'     : view,
                'member'   : member,
                'time'     : time,
                'keywords' : keywords,
                'modules'  : SecureModuleImporter,
                'nothing'  : None
               }
        return getEngine().getContext(data)

    def _associateTemplate(self, object, template_id):
        try:
            template = object.unrestrictedTraverse(template_id)
        except (AttributeError, KeyError):
            template = None 
            # XXX should log the fact that this template can't be found
        if template is not None:
            manager_id = getattr(template, 'ZCacheable_getManagerId', None)
            if manager_id is not None:
                if manager_id() is None:
                    template.ZCacheable_setManagerId(PAGE_CACHE_MANAGER_ID)

    def _getHeaderSet(self, request, object, view, member):
        stop_items = self.getCacheStop()
        if stop_items:
            for item in stop_items:
                if request.get(item, None) is not None:
                    return None
                
        expr_context = self._getExpressionContext(request, object, view, member)
        if not self.testPredicate(expr_context):
            return None
                
        if member is None:
            header_set_id = self.getHeaderSetIdAnon()
        else:
            header_set_id = self.getHeaderSetIdAuth()
        if header_set_id == 'expression':
            header_set_id = self.getHeaderSetIdExpressionValue(expr_context)
        if header_set_id == 'None':
            header_set_id = None
        if header_set_id:
            pcs = getToolByName(self, CACHE_TOOL_ID)
            return pcs.getHeaderSetById(header_set_id)

    def getHeaderSetVocabulary(self):
        pcs = getToolByName(self, CACHE_TOOL_ID)
        display_id = pcs.getDisplayPolicy().getId()
        headers = pcs.getHeaderSets(display_id)
        vocabulary = [('expression', 'Use expression below')] + \
                     [(hs.getId(), hs.Title()) for hs in headers.objectValues()] + \
                     [('None', 'Rule does not apply')]
        return atapi.DisplayList(tuple(vocabulary))
        
    def getObjectDefaultView(self, obj):
        """Get the id of an object's default view"""
        context = aq_inner(obj)
        browserDefault = IBrowserDefault(context, None)
        
        if browserDefault is not None:
            try:
                return browserDefault.defaultView()
            except AttributeError:
                # Might happen if FTI didn't migrate yet.
                pass

        fti = context.getTypeInfo()
        try:
            # XXX: This isn't quite right since it assumes the action starts with ${object_url}
            action = fti.getActionInfo('object/view')['url'].split('/')[-1]
        except ValueError:
            # If the action doesn't exist, stop
            return None

        # Try resolving method aliases because we need a real template_id here
        if action:
            action = fti.queryMethodID(action, default = action, context = context)
        else:
            action = fti.queryMethodID('(Default)', default = action, context = context)

        # Strip off leading / and/or @@
        if action and action[0] == '/':
            action = action[1:]
        if action and action.startswith('@@'):
            action = action[2:]
        return action
        
    def _addEtagComponent(self, etag, component):
        etag += '|' + str(component).replace(',',';')  # commas are used to separate etags in if-none-match headers
        return etag

    security.declarePublic('getEtag')
    def getEtag(self, request, object, view, member, time=None):
        # note: member may come in as None if the member is anonymous
        portal = getToolByName(self, 'portal_url').getPortalObject()
        pcs = getattr(portal, CACHE_TOOL_ID)
        etag = ''
        values = self.getEtagComponents()
        if 'member' in values:
            if member is not None:
                username = member.getUserName()
            else:
                username = ''
            etag = self._addEtagComponent(etag, username)
        if 'roles' in values or 'permissions' in values:
            m = member
            if m is None:
                m = portal.portal_membership.wrapUser(nobody)
            roles = list(m.getRolesInContext(object))
            roles.sort()
            etag = self._addEtagComponent(etag, ';'.join(roles))
            if 'permissions' in values:
                etag = self._addEtagComponent(etag, pcs.getPermissionCount())
        if 'skin' in values:
            try:
                skin_name = self.getCurrentSkinName()
            except AttributeError:
                stool = getToolByName(self, 'portal_skins')
                skin_name = self.getSkinNameFromRequest(request)
                
                if skin_name is None:
                    # Use default skin
                    skin_name = stool.getDefaultSkin()

            etag = self._addEtagComponent(etag, skin_name)
        if 'language' in values:
            etag = self._addEtagComponent(etag, request.get('HTTP_ACCEPT_LANGUAGE', ''))
        if 'user_language' in values:
            ltool = getToolByName(self, 'portal_languages', None)
            if ltool is None:
                ptool = getToolByName(self, 'portal_properties')
                lang = ptool.site_properties.default_language
            else:
                lang = ltool.getPreferredLanguage()
            etag = self._addEtagComponent(etag, lang)
        if 'gzip' in values:
            (enable_compression, force, gzip_capable) = pcs.isGzippable(0, 0, request)
            etag = self._addEtagComponent(etag, int(force or (enable_compression and gzip_capable)))
        if 'last_modified' in values:
            etag = self._addEtagComponent(etag, object.modified().timeTime())
        if 'catalog_modified' in values:
            etag = self._addEtagComponent(etag, pcs.getCatalogCount())
        if self.getEtagExpression():
            expr_context = self._getExpressionContext(request, object, view, member)
            etag = self._addEtagComponent(etag, self.getEtagExpressionValue(expr_context))
            
        marker = []
        req_values = self.getEtagRequestValues()
        if req_values:
            for rv in req_values:
                v = request.get(rv, marker)
                if v is not marker:
                    etag = self._addEtagComponent(etag, quote(str(v)))
                else:
                    etag = self._addEtagComponent(etag, '')
                    
        timeout = self.getEtagTimeout()
        if timeout:
            if time is None:
                time = DateTime.DateTime()
            etag = self._addEtagComponent(etag, int(time.timeTime()/timeout))
        return etag

    security.declarePublic('getRelativeUrlsToPurge')
    def getRelativeUrlsToPurge(self, object, urls):
        return urls


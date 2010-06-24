##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This file contains code drawn from CMFCore's CachingPolicyManager.py
"""Header set implementation

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from App.Common import rfc1123_date
from DateTime import DateTime
from zope.tales.tales import CompilerError
from Products.PageTemplates.Expressions import getEngine
from Products.Archetypes import public as atapi
try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.config import PROJECT_NAME, CACHE_TOOL_ID
from nocatalog import NoCatalog

schema = atapi.BaseContent.schema.copy() + \
   atapi.Schema((atapi.TextField(
                    'description',
                    required=0,
                    allowable_content_types = ('text/plain',),
                    default='A set of HTTP headers to be assigned with a caching rule',
                    widget=atapi.TextAreaWidget(label='Description',
                                                description='Basic documentation for this caching assignment policy',
                                                cols=60,
                                                rows=5,),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField('pageCache',
                                    default=0,
                                    widget=atapi.BooleanWidget(label='Cache Templates in Memory',
                                                               description='Should templates with this header set be cached in the page cache?'),
                                    write_permission = permissions.ManagePortal,
                                    ),
                 atapi.StringField(
                    'lastModified',
                    default='yes',
                    widget=atapi.SelectionWidget(label='Last-Modified Header',
                                                 description='Should the header set add a Last-Modified header?  Note: There appears to be an IE bug that causes incorrect caching behavior when you have both a Last-Modified header (used for caching heuristics) and explicit caching headers such as max-age=0.  The problem may arise from setting the Expires header to the current time.  One workaround is to not set the Last-Modified header and to delete any pre-existing Last-Modified header.  Setting Expires to a time in the past may also work (this is now the default behavior if max-age=0) -- further testing is needed.',
                                                 ),
                    vocabulary=atapi.DisplayList((('yes', 'Yes'), ('no', 'No'), ('delete', 'No, and delete any pre-existing header'))),
                    write_permission = permissions.ManagePortal,
                 ),
                 # The last_modified argument is used to determine whether to add a
                 # Last-Modified header.  last_modified=1 by default.  There appears
                 # to be a bug in IE 6 (and possibly other versions) that uses the
                 # Last-Modified header plus some heuristics rather than the other
                 # explicit caching headers to determine whether to render content
                 # from the cache.  If you set, say, max-age=0, must-revalidate and
                 # have a Last-Modified header some time in the past, IE will
                 # recognize that the page in cache is stale and will request an
                 # update from the server BUT if you have a Last-Modified header
                 # with an older date, will then ignore the update and render from
                 # the cache, so you may want to disable the Last-Modified header
                 # when controlling caching using Cache-Control headers.
                 #
                 # Update: The problem may be because we were setting Expires to
                 # the current time when max-age was set to 0.  IE may have Expires
                 # override max-age (bad) or something similar.  We are now setting
                 # Expires to a time in the past if max-age is 0.
                 atapi.BooleanField(
                    'etag',
                    default=1,
                    widget=atapi.BooleanWidget(label='ETag Header',
                                               description='Should the header set add an ETag header?'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'enable304s',
                    default=1,
                    widget=atapi.BooleanWidget(label='Enable 304s',
                                               description='Should objects that support conditional GET handling with ETags (FSPageTemplates) be allowed to return a 304 Not Modified HTTP status?'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'vary',
                    default=1,
                    widget=atapi.BooleanWidget(label='Vary Header',
                                               description='Should the header set add a Vary header?'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.IntegerField(
                    'maxAge',
                    default=None,
                    widget=atapi.IntegerWidget(label='Cache-Control Header: max-age',
                                              description='The amount of time in seconds that a page can be cached on a client without revalidation.  Also used to set the Expires header  (HTTP 1.0).  If left blank, no max-age token will be added and no Expires header will be set.',
                                              size=6),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.IntegerField(
                    'sMaxAge',
                    default=None,
                    widget=atapi.IntegerWidget(label='Cache-Control Header: s-maxage',
                                              description='The amount of time in seconds that a page can be cached in a proxy cache without revalidation.  If left blank, no s-maxage token will be added.  If you do not indicate that you have a purgeable proxy server available (e.g. squid), the s-maxage token will not be added.',
                                              size=6),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'mustRevalidate',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: must-revalidate',
                                               description='Must objects be revalidated with the server (by a conditional GET) once they have expired in the client?'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'proxyRevalidate',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: proxy-revalidate',
                                               description='Must objects be revalidated with the server once they have expired in the proxy cache?'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'noCache',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: no-cache',
                                               description='If no-cache is set, objects may be cached, but the cache must revalidate with the server before serving the cached version.  Setting no-cache also causes a Pragma: no-cache (HTTP 1.0) header to be sent.'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'noStore',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: no-store',
                                               description='If no-store is set, objects may not be stored in a cache.'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'public',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: public',
                                               description='If the public flag is set, proxy caches may cache a page even in the presence of things like Authentication headers that would otherwise prevent them from doing so.'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'private',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: private',
                                               description='If the private flag is set, shared HTTP 1.1-compliant proxy caches will not cache a page.  The non-shared browser cache, however, may cache a page with the private flag.'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.BooleanField(
                    'noTransform',
                    default=0,
                    widget=atapi.BooleanWidget(label='Cache-Control Header: no-transform',
                                               description='The no-transform flag tells intermediate proxies not to alter the content in transit (e.g. tell proxies to mobile phones not to downsample images, etc)'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.IntegerField(
                    'preCheck',
                    default=None,
                    widget=atapi.IntegerWidget(label='Cache-Control Header: pre-check',
                                              description='The pre-check flag is a Microsoft proprietary Cache-Control extension.  See http://msdn.microsoft.com/workshop/author/perf/perftips.asp for details.  IE 5+ will send some cache directives unless pre-check and post-check are set to 0.'),
                    write_permission = permissions.ManagePortal,
                 ),
                 atapi.IntegerField(
                    'postCheck',
                    default=None,
                    widget=atapi.IntegerWidget(label='Cache-Control Header: post-check',
                                              description='The post-check flag is a Microsoft proprietary Cache-Control extension.  See http://msdn.microsoft.com/workshop/author/perf/perftips.asp for details.  IE 5+ will send some cache directives unless pre-check and post-check are set to 0.'),
                    write_permission = permissions.ManagePortal,
                 ),
))

schema['id'].widget.ignore_visible_ids=True                       
schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Header-Set-Id' header with this id will be added."

class HeaderSet(NoCatalog, atapi.BaseContent):
    """A content object used for setting a set of response headers for a page"""

    security = ClassSecurityInfo()
    archetype_name = 'Response Header Set'
    portal_type = meta_type = 'HeaderSet'
    schema = schema
    global_allow = 0
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

    def _validate_expression(self, expression):
        try:
            getEngine().compile(expression)
        except CompilerError, e:
            return 'Bad expression:', str(e)
        except:
            raise

    def getLastModifiedValue(self, expr_context):
        if not self.getLastModified() == 'yes':
            return None # no last-modified value if disabled
        rule = expr_context.vars['rule']
        return rule.getLastModified(expr_context)

    def getVaryValue(self, expr_context):
        if not self.getVary():
            return None # no Vary value if disabled
        rule = expr_context.vars['rule']
        return rule.getVary(expr_context)

    def getPageCacheKey(self, expr_context):
        # Return a cache key for use with PageCacheManager
        if not self.getPageCache():
            return None
        return self._getEtagValue(expr_context)

    def _getEtagValue(self, expr_context):
        rule = expr_context.vars['rule']
        request = expr_context.vars['request']
        object = expr_context.vars['object']
        view = expr_context.vars['view']
        member = expr_context.vars['member']
        return rule.getEtag(request, object, view, member)

    def getEtagValue(self, expr_context):
        if not self.getEtag():
            return None # no etag if disabled
        return self._getEtagValue(expr_context)

    def getHeaders(self, expr_context):
        """Returns a list of caching headers in (key, value) tuples"""
        pcs = getToolByName(self, CACHE_TOOL_ID)
        headers_to_add = []
        headers_to_remove = []

        last_modified = self.getLastModified()
        if last_modified == 'yes':
            mod_time = self.getLastModifiedValue(expr_context)
            if type(mod_time) is type(''):
                mod_time = DateTime(mod_time)
            if mod_time is not None:
                mod_time_st = rfc1123_date(mod_time.timeTime())
                headers_to_add.append(('Last-modified', mod_time_st))
        elif last_modified == 'delete':
            headers_to_remove.append('Last-modified')

        if self.getEtag():
            etag = self.getEtagValue(expr_context)
            if etag is not None:
                headers_to_add.append(('ETag', etag))

        vary = self.getVaryValue(expr_context)
        if vary:
            headers_to_add.append(('Vary', vary))

        # a list of cache-control tokens
        control = []

        max_age = self.getMaxAge()
        if max_age is not None:
            now = expr_context.vars['time']
            if max_age > 0:
                expiration_time = now.timeTime() + max_age
            else:
                # immediate expiration requires that the client clock be precisely synchronized
                # since this is not guaranteed, we'll set the expiration time to 10 years ago
                expiration_time = now.timeTime() - 10*365*24*3600
            exp_time_st = rfc1123_date(expiration_time)
            headers_to_add.append(('Expires', exp_time_st))
            control.append('max-age=%d' % max_age)

        s_max_age = self.getSMaxAge()
        if s_max_age is not None:
            if pcs.hasPurgeableProxy():
                control.append('s-maxage=%d' % s_max_age)

        if self.getNoCache():
            control.append('no-cache')
            # The following is for HTTP 1.0 clients
            headers_to_add.append(('Pragma', 'no-cache'))

        if self.getNoStore():
            control.append('no-store')

        if self.getPublic():
            control.append('public')

        if self.getPrivate():
            control.append('private')

        if self.getMustRevalidate():
            control.append('must-revalidate')

        if self.getProxyRevalidate():
            if pcs.hasPurgeableProxy():
                control.append('proxy-revalidate')

        if self.getNoTransform():
            control.append('no-transform')

        pre_check = self.getPreCheck()
        if pre_check is not None:
            control.append('pre-check=%d' % pre_check)

        post_check = self.getPostCheck()
        if post_check is not None:
            control.append('post-check=%d' % post_check)

        if control:
            headers_to_add.append(('Cache-control', ', '.join(control)))

        # add debugging information
        rule = expr_context.vars['rule']
        headers_to_add.append(('X-Caching-Rule-Id', rule.getId()))
        headers_to_add.append(('X-Header-Set-Id', self.getId()))

        return (headers_to_add, headers_to_remove)

atapi.registerType(HeaderSet, PROJECT_NAME)

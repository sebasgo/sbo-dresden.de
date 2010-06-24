##############################################################################
#
# Copyright (c) 2003-2005 struktur AG and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: SquidTool.py 45934 2007-07-20 08:19:12Z newbery $
"""

import os, re, httplib, urlparse, urllib, sys

from Globals import InitializeClass, package_home
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from ZODB.POSException import ConflictError
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFSquidTool.Permissions import *
from Products.CMFSquidTool.utils import pruneUrl, pruneAsync
from Products.CMFSquidTool.utils import logger


URL_REWRITE_MAP = {}

def createUrlExpressionContext(object):
    """Construct an expression context for TALES expression.
    """
    pm = getToolByName(object, 'portal_membership', None)
    if not pm or pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()

    data = { 'object'   : object
           , 'request'  : getattr( object, 'REQUEST', {} )
           , 'member'   : member
           , 'modules'  : SecureModuleImporter
           , 'nothing'  : None
           }

    return getEngine().getContext(data)


# urlparse.urljoin does relative urls.
# we want simple path appending.
def joinUrlPath(url, url2):
    (scheme, host, path, params, query, frag) = urlparse.urlparse(url)
    (scheme2, host2, path2, params2, query2, frag2) = urlparse.urlparse(url2)
    # strip off leading and trailing slashes from path
    parts_path = filter(None, path.split('/'))
    # Strip off leading slash from path, we want to keep any trailing slash,
    # and preserve the slash if it the only thing in the url
    if path2.startswith('/') and len(path2) > 1:
        path2 = path2[1:]
    parts_path2 = path2.split('/')
    for part in parts_path:
        if parts_path2[0] == part:
            parts_path2.pop(0)
        else:
            break
    path = '/'.join(parts_path + parts_path2)
    path = urllib.quote(path,'/:')
    return urlparse.urlunparse((scheme, host, path, None, None, None))

skins_re = re.compile('portal_skins')

class SquidTool(UniqueObject, SimpleItem):
    """ Tool to send PURGE requests to caching proxy.
    """

    id = 'portal_squid'
    meta_type = 'CMF Squid Tool'
    url_expression = None
    security = ClassSecurityInfo()

    manage_options=(
        ({ 'label'   : 'Proxy Urls',
           'action'  : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        )

    manage_configForm = PageTemplateFile('www/config', globals())

    def __init__(self):
        self.id = 'portal_squid'
        self.squid_urls = []
        self.url_expression = Expression(text='')

    security.declareProtected(ManagePortal, 'getSquidURLs')
    def getSquidURLs(self):
        """Return the Squid URLs we should purge
        """
        return '\n'.join(map(str, filter(None, self.squid_urls)))

    security.declareProtected(ManagePortal, 'getUrlExpression')
    def getUrlExpression(self):
        """Return the text of the expression used for generating the
        URLs to purge when an object is modified
        """
        if self.url_expression is None:
            self.url_expression = Expression(text='')
        return self.url_expression.text

    security.declareProtected(ManagePortal, 'setUrlExpression')
    def setUrlExpression(self, expr):
        """Return the text of the expression used for generating the
        URLs to purge when an object is modified
        """
        self.url_expression = Expression(expr)

    security.declarePublic('getUrlsToPurge')
    def getUrlsToPurge(self, object):
        """Return the URLs to purge when an object is modified
        """
        if (self.url_expression is None or
            not self.getUrlExpression().strip()):
            portal_url = getToolByName(self, 'portal_url')
            # No url expression, short-circuit.
            paths = [portal_url.getRelativeUrl(object)]
        else:
            context = createUrlExpressionContext(object)
            try:
                paths = self.url_expression(context)
            except ConflictError:
                raise
            except:
                paths = []
                logger.exception('Exception computing urls to purge.')

        # Now some special handling for elements inside portal_skins.
        st = getToolByName(object, 'portal_skins', None)
        if st is None:
            return paths
        sn = st.getSkinNameFromRequest(
            REQUEST=getattr(object, 'REQUEST', None))
        if sn is None:
            sn = st.getDefaultSkin()
        sp = st.getSkinPath(sn)
        if sp is None or sp == sn:
            return paths
        skin_paths = [s.strip() for s in sp.split(',')]
        skin_paths = filter(None, skin_paths)
        for path in paths[:]:
            if skins_re.search(path) is None:
                continue
            orig_path = path
            for sub in skin_paths:
                path = orig_path.replace('portal_skins/%s/' % sub, '')
                if path != orig_path and path not in paths:
                    paths.append(path)
        return paths

    security.declareProtected(PURGE_URL, 'pruneObject')
    def pruneObject(self, ob, purge_type='PURGE', REQUEST=None):
        """Prune this object
        """
        urls = self.getUrlsToPurge(ob)
        return self.pruneUrls(urls, purge_type=purge_type, REQUEST=REQUEST)

    security.declareProtected(ManagePortal, 'manage_setSquidSettings')
    def manage_setSquidSettings(self, urls, url_expression=None, REQUEST=None):
        """Store the tool settings
        """

        urls = urls.replace("\r\n", "\n")
        urls = urls.split("\n")
        urls = map(lambda x: x.strip(), urls)
        urls = filter(lambda x: x, urls)
        self.squid_urls = urls

        if url_expression is not None:
            self.setUrlExpression(url_expression)

        if REQUEST:
            url = REQUEST['HTTP_REFERER'].split('?')[0]
            url += '?portal_status_message=Settings updated'
            REQUEST.RESPONSE.redirect(url)

    security.declarePrivate('computePurgeUrls')
    def computePurgeUrls(self, ob_urls):
        res = []
        for url in self.squid_urls:
            for ob_url in ob_urls:
                ob_url = self.rewriteUrl(ob_url)
                res.append(joinUrlPath(url, ob_url))
        return res

    security.declarePrivate('pruneUrls')
    def pruneUrls(self, ob_urls=None, purge_type="PURGE", REQUEST=None):
        # ob_url is a relative to portal url

        results = []
        purge_urls = self.squid_urls
        if ob_urls:
            purge_urls = self.computePurgeUrls(ob_urls)

        for url in purge_urls:
            # If a response was given, we do it synchronously and write the
            # results to the response.  Otherwise we just queue it up.
            if REQUEST:
                status, xcache, xerror = pruneUrl(url, purge_type)

                # NOTE: if the purge was successfull status will be 200 (OK)
                #       if the object was not in cache status is 404 (NOT FOUND)
                #       if you are not allowed to PURGE status is 403
                REQUEST.RESPONSE.write('%s\t%s\t%s\n' % (status, url, xerror or xcache))
            else:
                pruneAsync(url, purge_type)
                status = "Queued"
                xcache = xerror = ""
            results.append((status, xcache, xerror))

        return results

    security.declarePublic('rewriteUrl')
    def rewriteUrl(self, url):
        for prefix, new in URL_REWRITE_MAP.items():
            if url.startswith(prefix):
                url = url.replace(prefix, new)
                break
        return url

    security.declareProtected(PURGE_URL, 'manage_pruneUrl')
    def manage_pruneUrl(self, url, REQUEST=None):
        """Give a url which shall be pruned
        """
        request = REQUEST
        return self.pruneUrls([url], REQUEST=REQUEST)

    security.declareProtected(ManagePortal, 'manage_pruneAll')
    def manage_pruneAll(self, REQUEST=None):
        """Prune all objects in catalog
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog()
        for brain in brains:
            self.pruneObject(brain.getObject(), REQUEST=REQUEST)

        if REQUEST:
            url = REQUEST['HTTP_REFERER'].split('?')[0]
            url += '?portal_status_message=Cache+cleared'
            REQUEST.RESPONSE.redirect(url)

        return "finished"

InitializeClass(SquidTool)

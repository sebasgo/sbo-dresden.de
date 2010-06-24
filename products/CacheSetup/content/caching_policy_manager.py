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
# This code is a modified version of CMFCore's CachingPolicyManager.py
"""Caching tool implementation.

$Id: CachingPolicyManager.py 40138 2005-11-15 17:47:37Z jens $
"""

from Globals import package_home
import os
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
try:
    from Products.CMFCore import permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as permissions
from Products.CMFCore.utils import getToolByName
from Globals import DTMLFile

from Products.CMFCore.CachingPolicyManager import CachingPolicyManager as CMFCachingPolicyManager
from Products.CacheSetup.config import CACHE_TOOL_ID

class CSCachingPolicyManager( CMFCachingPolicyManager ):
    """
        Manage the set of CachingPolicy objects for the site;  dispatch
        to them from skin methods.
    """

    id = 'caching_policy_manager'
    meta_type = 'CacheFu Caching Policy Manager'

    security = ClassSecurityInfo()

    security.declareProtected(permissions.ManagePortal, 'manage_cachingPolicies')
    manage_cachingPolicies = DTMLFile('cachingPoliciesDummy', os.path.dirname(package_home(globals())))

    # A new method that replaces getHTTPCachingHeaders
    security.declareProtected( permissions.View, 'getHeadersToAddAndRemove' )
    def getHeadersToAddAndRemove( self, content, view_method, keywords, time=None):
        """Return a tuple of HTTP caching headers, (headers_to_add, headers_to_remove).
           The first item is a list of headers to add to the response in the form
           (header name, header value).  The second item is a list of headers that
           should be removed (before adding)."""
        pcs = getToolByName(self, CACHE_TOOL_ID)
        member = pcs.getMember()
        request = content.REQUEST
        (rule, header_set) = pcs.getRuleAndHeaderSet(request, content, view_method, member)
        if header_set:
            expr_context = rule._getExpressionContext(request, content, view_method, member)
            return header_set.getHeaders(expr_context)
        return ()

    #
    #   'portal_caching' interface methods
    #
    security.declareProtected( permissions.View, 'getHTTPCachingHeaders' )
    def getHTTPCachingHeaders( self, content, view_method, keywords, time=None):
        """Return a list of HTTP caching headers based on 'content', 'view_method', and 'keywords'."""
        hdrs = self.getHeadersToAddAndRemove(content, view_method, keywords, time)
        if hdrs:
            return hdrs[0]
        return ()

    security.declareProtected( permissions.View, 'getModTimeAndETag' )
    def getModTimeAndETag( self, content, view_method, keywords, time=None):
        """ Return the modification time and ETag for the content object,
            view method, and keywords as the tuple (modification_time, etag,
            set_last_modified_header), where modification_time is a DateTime,
            or None.
        """
        pcs = getToolByName(self, CACHE_TOOL_ID)
        member = pcs.getMember()
        request = content.REQUEST
        (rule, header_set) = pcs.getRuleAndHeaderSet(request, content, view_method, member)
        if header_set:
            expr_context = rule._getExpressionContext(request, content, view_method, member)
            etag = header_set.getEtagValue(expr_context)
            mod_time = header_set.getLastModifiedValue(expr_context)
            use_mod_time = header_set.getLastModified()
            return (mod_time, etag, use_mod_time)

    security.declareProtected( permissions.View, 'getETag' )
    def getETag( self, content, view_method, keywords, time=None):
        """ Return the ETag for the content object; ignores getEnable304s setting"""
        pcs = getToolByName(self, CACHE_TOOL_ID)
        member = pcs.getMember()
        request = content.REQUEST
        (rule, header_set) = pcs.getRuleAndHeaderSet(request, content, view_method, member)
        if header_set:
            expr_context = rule._getExpressionContext(request, content, view_method, member)
            etag = header_set.getEtagValue(expr_context)
            return etag

InitializeClass( CSCachingPolicyManager )

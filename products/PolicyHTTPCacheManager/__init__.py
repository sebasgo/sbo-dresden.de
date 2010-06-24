##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id: __init__.py 47403 2007-08-16 10:48:18Z newbery $
"""

import PolicyHTTPCacheManager

def initialize(context):
    context.registerClass(
        PolicyHTTPCacheManager.PolicyHTTPCacheManager,
        constructors = (
        PolicyHTTPCacheManager.manage_addPolicyHTTPCacheManagerForm,
        PolicyHTTPCacheManager.manage_addPolicyHTTPCacheManager),
        icon="cache.gif"
        )

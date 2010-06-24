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
$Id: Permissions.py 22931 2006-05-01 18:42:17Z hannosch $
"""

try:
    from Products.CMFCore.CMFCorePermissions import ManagePortal
    from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
    from Products.CMFCore.CMFCorePermissions import View
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles
except:
    from Products.CMFCore.permissions import ManagePortal
    from Products.CMFCore.permissions import ModifyPortalContent
    from Products.CMFCore.permissions import View
    from Products.CMFCore.permissions import setDefaultRoles

# Add Entry
PURGE_URL = 'SquidTool: Purge URL'
setDefaultRoles(PURGE_URL, ('Manager', 'Member'))

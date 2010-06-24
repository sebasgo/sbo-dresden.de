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
$Id: Install.py 14733 2005-12-08 13:23:19Z dreamcatcher $
"""

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

_globals = globals()

def install_tools(self, out):
    if not hasattr(self, "portal_squid"):
        addTool = self.manage_addProduct['CMFSquidTool'].manage_addTool
        addTool('CMF Squid Tool')

def install(self):
    out = StringIO()
    print >>out, "Installing CMFSquidTool"

    install_tools(self, out)
    return out.getvalue()

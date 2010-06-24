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
$Id: __init__.py 36414 2007-01-29 22:07:26Z dreamcatcher $
"""

from Globals import InitializeClass
from AccessControl import ModuleSecurityInfo
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/squid_tool', globals())

PKG_NAME = "CMFSquidTool"

from Products.CMFSquidTool.SquidTool import SquidTool
tools = (SquidTool,)

def initialize(context):
    # Initialize hooks
    from Products.CMFSquidTool import queue

    cmf_utils.ToolInit("Squid Tool", tools=tools,
                       icon="tool.gif",
                       ).initialize(context)

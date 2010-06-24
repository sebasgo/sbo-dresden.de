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
$Id: base.py 14137 2005-11-21 14:47:13Z dreamcatcher $
"""

import sys
from cStringIO import StringIO

# Load fixture
from Testing import ZopeTestCase

# Install our product
ZopeTestCase.installProduct('CMFSquidTool')

from Products.CMFPlone.tests import PloneTestCase

class BaseTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def assertStructEquals(self, got, expected):
        _got = StringIO()
        _expected = StringIO()
        pprint(got, _got)
        pprint(expected, _expected)
        _got = _got.getvalue().splitlines()
        _expected = _expected.getvalue().splitlines()
        diff = unified_diff(_expected, _got)
        self.failUnless(got == expected, '\n'.join(diff))

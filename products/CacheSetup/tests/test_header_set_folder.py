# This Python file uses the following encoding: utf-8
"""
header set folder implementation tests

$Id: test_header_set_folder.py 47373 2007-08-16 06:16:51Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.Archetypes.atapi import OrderedBaseFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheToolFolder

class HeaderSetFolder(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('HeaderSetFolder', self.folder, 'hsf')
        self.hsf = getattr(self.folder, 'hsf')

    def _testImplementsOrderedBaseFolder(self):
        # not pretty sure about this but; there is no such a thing as IOrderedBaseFolder...
        self.fail('not yet implemented...')

    def testImplementsCacheToolFolder(self):
        iface = ICacheToolFolder
        self.failUnless(iface.isImplementedBy(self.hsf))
        self.failUnless(verifyObject(iface, self.hsf))

    def testTypeInfo(self):
        ti = self.hsf.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Header Set Folder')
        self.failUnlessEqual(ti.getId(), 'HeaderSetFolder')
        self.failUnlessEqual(ti.Metatype(), 'HeaderSetFolder')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config', 'view': 'cache_policy_item_config', 'edit': 'cache_policy_item_config'})

    def testAllowedContentTypes(self):
        allowed = ('HeaderSet',)
        for t in self.hsf.allowedContentTypes():
            self.failUnless(t.getId() in allowed)

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        hsf = ttool['HeaderSetFolder']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, hsf.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = hsf.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(HeaderSetFolder))
    return suite

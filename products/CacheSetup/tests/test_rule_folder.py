# This Python file uses the following encoding: utf-8
""" rule folder implementation tests """

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheToolFolder

class TestRuleFolder(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('RuleFolder', self.folder, 'rf')
        self.rf = getattr(self.folder, 'rf')

    def _testImplementsOrderedBaseFolder(self):
        # not pretty sure about this but; there is no such a thing as IOrderedBaseFolder...
        self.fail('not yet implemented')

    def testImplementsCacheToolFolder(self):
        iface = ICacheToolFolder
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))

    def testTypeInfo(self):
        ti = self.rf.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Rule Folder')
        self.failUnlessEqual(ti.getId(), 'RuleFolder')
        self.failUnlessEqual(ti.Metatype(), 'RuleFolder')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config', 'view': 'cache_policy_item_config', 'edit': 'cache_policy_item_config'})

    def testAllowedContentTypes(self):
        allowed = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')
        for t in self.rf.allowedContentTypes():
            self.failUnless(t.getId() in allowed)

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        rf = ttool['RuleFolder']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, rf.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = rf.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleFolder))
    return suite

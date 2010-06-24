# This Python file uses the following encoding: utf-8
"""
content cache rule implementation tests

$Id$
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.Archetypes.atapi import *
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheRule

class TestContentCacheRuleSchema(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('ContentCacheRule', self.folder, 'ccr')
        self.ccr = getattr(self.folder, 'ccr')

    def testDescriptionField(self):
        field = self.ccr.getField('description')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'text')
        self.failUnlessEqual(field.allowable_content_types, ('text/plain',))
        self.failUnlessEqual(field.default, 'A cache rule for CMF content types')
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testContentTypesField(self):
        field = self.ccr.getField('contentTypes')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'lines')
        self.failUnlessEqual(field.default, ())
        #self.failUnlessEqual(field.enforceVocabulary, 1) # not pretty sure about this
        self.failUnlessEqual(field.multiValued, 1)
        self.failUnlessEqual(field.required, 1)
        self.failUnlessEqual(field.vocabulary, 'getContentTypesVocabulary')
        self.failUnless(isinstance(field.widget, MultiSelectionWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testDefaultViewField(self):
        field = self.ccr.getField('defaultView')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'boolean')
        self.failUnlessEqual(field.default, 1)
        self.failUnless(isinstance(field.widget, BooleanWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testDefaultViewField(self):
        field = self.ccr.getField('templates')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'lines')
        self.failUnless(isinstance(field.widget, LinesWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def _testBaseCacheRuleFields(self):
        self.fail('not yet implemented')

    def testPurgeExpressionField(self):
        field = self.ccr.getField('purgeExpression')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'string')
        self.failUnless(isinstance(field.widget, StringWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

class TestContentCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('ContentCacheRule', self.folder, 'ccr')
        self.ccr = getattr(self.folder, 'ccr')

    def testImplementsBaseContent(self):
        iface = IBaseContent
        self.failUnless(iface.isImplementedBy(self.ccr))
        self.failUnless(verifyObject(iface, self.ccr))

    def testImplementsCacheRule(self):
        iface = ICacheRule
        self.failUnless(iface.isImplementedBy(self.ccr))
        self.failUnless(verifyObject(iface, self.ccr))

    def testTypeInfo(self):
        ti = self.ccr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Content Cache Rule')
        self.failUnlessEqual(ti.getId(), 'ContentCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'ContentCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)':'cache_policy_item_config','view':'cache_policy_item_config','edit':'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        ccr = ttool['ContentCacheRule']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, ccr.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = ccr.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestContentCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('ContentCacheRule', self.folder, 'ccr')
        self.ccr = getattr(self.folder, 'ccr')

    def _test_setPurgeExpression(self):
        self.fail('not yet implemented...')

    def _test_getPurgeExpression(self):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentCacheRuleSchema))
    suite.addTest(makeSuite(TestContentCacheRule))
    suite.addTest(makeSuite(TestContentCacheRuleMethods))
    return suite

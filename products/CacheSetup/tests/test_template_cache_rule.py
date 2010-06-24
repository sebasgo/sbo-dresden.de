# This Python file uses the following encoding: utf-8
"""
template cache rule implementation tests

$Id$
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheRule

class TestTemplateCacheRuleSchema(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('TemplateCacheRule', self.folder, 'tcr')
        self.tcr = getattr(self.folder, 'tcr')

    def testDescriptionField(self):
        field = self.tcr.getField('description')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'text')
        self.failUnlessEqual(field.allowable_content_types, ('text/plain',))
        self.failUnlessEqual(field.default, 'A cache rule for page templates')
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testTemplatesField(self):
        field = self.tcr.getField('templates')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'lines')
        self.failUnless(isinstance(field.widget, LinesWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def _testBaseCacheRuleFields(self):
        self.fail('not yet implemented')

class TestTemplateCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('TemplateCacheRule', self.folder, 'tcr')
        self.tcr = getattr(self.folder, 'tcr')

    def testImplementsBaseContent(self):
        iface = IBaseContent
        self.failUnless(iface.isImplementedBy(self.tcr))
        self.failUnless(verifyObject(iface, self.tcr))

    def testImplementsCacheRule(self):
        iface = ICacheRule
        self.failUnless(iface.isImplementedBy(self.tcr))
        self.failUnless(verifyObject(iface, self.tcr))

    def testTypeInfo(self):
        ti = self.tcr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Template Cache Rule')
        self.failUnlessEqual(ti.getId(), 'TemplateCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'TemplateCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config', 'view': 'cache_policy_item_config', 'edit': 'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        tcr = ttool['TemplateCacheRule']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, tcr.getActionInfo, actions)
        self.setRoles(['Manager','Member'])

        info = tcr.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestTemplateCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('TemplateCacheRule', self.folder, 'tcr')
        self.tcr = getattr(self.folder, 'tcr')

    def test_getHeaderSet(self):
        # isn't complete, but it's a start
        self.tcr.setTemplates(('template1','template2'))
        hs = self.tcr.getHeaderSet('dummy','dummy','MyTemplate','dummy')
        self.failUnless(hs is None)
        #hs = self.tcr.getHeaderSet('dummy','dummy','template1','dummy')
        #self.failUnless(hs is not None)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateCacheRuleSchema))
    suite.addTest(makeSuite(TestTemplateCacheRule))
    #suite.addTest(makeSuite(TestTemplateCacheRuleMethods))
    return suite

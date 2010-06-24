# This Python file uses the following encoding: utf-8
"""
cache tool implementation tests

$Id: test_cache_tool.py 47381 2007-08-16 07:36:37Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from OFS.interfaces import ISimpleItem
from Products.Archetypes.atapi import *
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName, UniqueObject

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheTool

class TestCacheToolSchema(CacheFuTestCase):
    """
    this test class is not pretty useful, as optilude said, but it's
    better to have it as long as there is work on refactoring the beast
    """

    def afterSetUp(self):
        self.tool = getattr(self.folder, CACHE_TOOL_ID)


    def testEnabledField(self):
        field = self.tool.getField('enabled')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'boolean')
        self.failUnlessEqual(field.default, 0)
        self.failUnless(isinstance(field.widget, BooleanWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    # this field is deprecated
    # 
    #def testCacheConfigField(self):
    #    field = self.tool.getField('cacheConfig')
    #    self.failUnless(ILayerContainer.isImplementedBy(field))
    #    self.failUnlessEqual(field.type, 'string')
    #    self.failUnlessEqual(field.default, 'zserver')
    #    self.failUnlessEqual(field.required, 1)
    #    #self.failUnlessEqual(field.enforceVocabulary, 1)
    #    vocabulary = field.vocabulary
    #    self.failUnless(isinstance(vocabulary, DisplayList))
    #    config = [i[0] for i in CACHE_CONFIG]
    #    self.failUnlessEqual(tuple(vocabulary), tuple(config))
    #    self.failUnless(isinstance(field.widget, SelectionWidget))
    #    #self.failUnlessEqual(field.read_permission, ManagePortal)
    #    self.failUnlessEqual(field.write_permission, ManagePortal)

    def testDomainsField(self):
        field = self.tool.getField('domains')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'lines')
        #self.failUnlessEqual(field.default, 'http://www.mysite.com:80')
        self.failUnless(isinstance(field.widget, LinesWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testSquidURLsField(self):
        field = self.tool.getField('squidURLs')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'lines')
        self.failUnless(isinstance(field.widget, LinesWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testGzipField(self):
        field = self.tool.getField('gzip')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'string')
        self.failUnlessEqual(field.default, 'accept-encoding')
        #self.failUnlessEqual(field.enforceVocabulary, 1)
        vocabulary = field.vocabulary
        self.failUnless(isinstance(vocabulary, DisplayList))
        config = [i[0] for i in USE_COMPRESSION]
        self.failUnlessEqual(tuple(vocabulary), tuple(config))
        self.failUnless(isinstance(field.widget, SelectionWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

    def testVaryHeaderField(self):
        field = self.tool.getField('varyHeader')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.type, 'string')
        self.failUnlessEqual(field.default, 'Accept-Encoding, Accept-Language')
        self.failUnless(isinstance(field.widget, StringWidget))
        #self.failUnlessEqual(field.read_permission, ManagePortal)
        self.failUnlessEqual(field.write_permission, ManagePortal)

class TestCacheTool(CacheFuTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.folder, CACHE_TOOL_ID)

    def testIsUniqueObject(self):
        self.failUnless(isinstance(self.tool, UniqueObject))

    # Why?
    # 
    #def testImplementsSimpleItem(self):
    #    iface = ISimpleItem
    #    self.failUnless(iface.providedBy(self.tool))
    #    self.failUnless(verifyObject(iface, self.tool))

    def testImplementsBaseFolder(self):
        iface = IBaseFolder
        self.failUnless(iface.providedBy(self.tool))
        self.failUnless(verifyObject(iface, self.tool))

    def testImplementsCacheTool(self):
        iface = ICacheTool
        self.failUnless(iface.providedBy(self.tool))
        self.failUnless(verifyObject(iface, self.tool))

    def testTypeInfo(self):
        ti = self.tool.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Cache Configuration Tool')
        self.failUnlessEqual(ti.getId(), 'CacheTool')
        self.failUnlessEqual(ti.Metatype(), 'CacheTool')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_tool_config', 'view' : 'cache_tool_config', 'edit': 'base_edit'})

    # we have policies instead now
    # 
    #def testAllowedContentTypes(self):
    #    allowed = ('HeaderSetFolder','RuleFolder')
    #    for t in self.tool.allowedContentTypes():
    #        self.failUnless(t.getId() in allowed)

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        tool = ttool['CacheTool']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, tool.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = tool.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestCacheToolMethods(CacheFuTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.folder, CACHE_TOOL_ID)

    def _test_initializeArchetype(self):
        self.fail('not yet implemented...')

    def _test_at_post_edit_script(self):
        self.fail('not yet implemented...')

    def _test_setCacheConfig(self):
        self.fail('not yet implemented...')

    def _test_setEnabled(self):
        self.fail('not yet implemented...')

    def _test_getRules(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSets(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSetById(self):
        self.fail('not yet implemented...')

    def _test_incrementCatalogCount(self):
        self.fail('not yet implemented...')

    def _test_getCatalogCount(self):
        self.fail('not yet implemented...')

    def _test_incrementPermissionCount(self):
        self.fail('not yet implemented...')

    def _test_getPermissionCount(self):
        self.fail('not yet implemented...')

    def _test_getCompleteUrl(self):
        self.fail('not yet implemented...')

    def _test_getSquidUrls(self):
        self.fail('not yet implemented...')

    def _test_setSquidUrls(self):
        self.fail('not yet implemented...')

    def _test_getCompleteUrl(self):
        self.fail('not yet implemented...')

    def _test_hasPurgeableProxy(self):
        self.fail('not yet implemented...')

    def _test_getDomains(self):
        self.fail('not yet implemented...')

    def _test_setDomains(self):
        self.fail('not yet implemented...')

    def _test_getSquidURLs(self):
        self.fail('not yet implemented...')

    def _test_setSquidURLs(self):
        self.fail('not yet implemented...')

    def _test_post_validate(self):
        self.fail('not yet implemented...')

    def _test_manage_purgePageCache(self):
        self.fail('not yet implemented...')

    def _test_canAnonymousView(self):
        self.fail('not yet implemented...')

    def _test_isGzippable(self):
        self.fail('not yet implemented...')

    def _test_getRuleAndHeaderSet(self):
        self.fail('not yet implemented...')

    def _test_getUrlsToPurge(self):
        self.fail('not yet implemented...')

    def _test_getMember(self):
        self.fail('not yet implemented...')

    def _test_generateUniqueId(self):
        self.fail('not yet implemented...')

    def _test_isIDAutoGenerated(self):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCacheToolSchema))
    suite.addTest(makeSuite(TestCacheTool))
    suite.addTest(makeSuite(TestCacheToolMethods))
    return suite

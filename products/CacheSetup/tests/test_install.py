from base import CacheFuTestCase

from Interface.Verify import verifyObject
from Products.Archetypes.public import listTypes
from Products.CMFCore.utils  import getToolByName

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheTool

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o


# This is the test case. You will have to add test_<methods> to your
# class inorder to assert things about your Product.
class CacheManagerTest(CacheFuTestCase):
    USER1 = 'user1'
    
    def afterSetUp(self):
        CacheFuTestCase.afterSetUp(self)
        
        # Add a couple of users
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser(self.USER1, 'secret', ['Member'], [])
        self.login('manager')

    def test_install(self):
        cpm = self.portal.caching_policy_manager
        cpm.addPolicy('foo', 'python:0', '', 1, 1, 0, 1, 'foo', '')
        original_class = cpm.__class__
        installed_types = [typeinfo['name'] for typeinfo in listTypes(PROJECT_NAME)]
        # before installation the new types are not in the types factory
        portal_factory = getToolByName(self, 'portal_factory')
        self.assertEqual(set(installed_types).issubset(set(portal_factory.getFactoryTypes())), False)
        self.portal.portal_quickinstaller.installProducts(['CacheSetup'])
        self.portal.portal_quickinstaller.installProducts(['CacheSetup'])
        # now the new types are in the types factory
        self.assertEqual(set(installed_types).issubset(set(portal_factory.getFactoryTypes())), True)
        cpm = self.portal.caching_policy_manager
        self.assertNotEqual(cpm.__class__, original_class)
        #self.failIf('caching_policy_manager' in self.portal.objectIds())
        
        self.portal.portal_quickinstaller.uninstallProducts(['CacheSetup'])
        # now the new types are gone again
        self.assertEqual(set(installed_types).issubset(set(portal_factory.getFactoryTypes())), False)
        cpm = self.portal.caching_policy_manager
        self.assertEqual(cpm.__class__, original_class)
        lp = cpm.listPolicies()
        self.assertEqual(len(lp), 1)
        (id, p) = lp[0]
        self.assertEqual(id, 'foo')
        self.assertEqual(p.getPredicate(), 'python:0')

class TestInstall(CacheFuTestCase):
    """ ensure product is properly installed """

    def afterSetUp(self):
        self.types = self.portal.portal_types
        self.skins = self.portal.portal_skins
        self.factory = self.portal.portal_factory
        self.tool = self.portal.portal_cache_settings
        self.setRoles(['Manager', 'Member'])
        self.tool.setEnabled(True)
        self.metaTypes = ('CacheTool','ContentCacheRule',
                          'TemplateCacheRule','PolicyHTTPCacheManagerCacheRule',
                          'RuleFolder','HeaderSet','HeaderSetFolder')

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds(),
                            '%s content type not installed' % t)

    def testPortalFactorySetup(self):
        for t in self.metaTypes:
            self.failUnless(t in self.factory.getFactoryTypes(),
                            '%s content type not in Portal Factory' % t)

    def testSkinLayersInstalled(self):
        self.failUnless('cache_setup' in self.skins.objectIds())

    def testDependenciesInstalled(self):
        # Zope products; not sure about this
        #self.dependencies = ('PageCacheManager','PolicyHTTPCacheManager')

        # Plone products
        self.dependencies = ('CMFSquidTool',)
        self.qitool = self.portal.portal_quickinstaller
        installed = [p['id'] for p in self.qitool.listInstalledProducts()]
        for p in self.dependencies:
            self.failUnless(p in installed,
                            '%s not installed' % p)

    def testWorkflowSetup(self):
        """ test if no workflow is associated with CacheFu's content types """
        self.workflow = self.portal.portal_workflow
        for t in self.metaTypes:
            self.failUnless(self.workflow.getChainForPortalType(t) is ())

    def testToolInstalled(self):
        self.failUnless(getattr(self.portal, CACHE_TOOL_ID, None) is not None)

    def testToolInterface(self):
        t = self.tool
        self.failUnless(ICacheTool.providedBy(t))
        self.failUnless(verifyObject(ICacheTool, t))

    def testToolNames(self):
        t = self.tool
        self.failUnlessEqual(t.meta_type, 'CacheTool')
        self.failUnlessEqual(t.getId(), CACHE_TOOL_ID)
        self.failUnlessEqual(t.title, 'Cache Configuration Tool')
        # what is this?
        # self.failUnlessEqual(t.plone_tool, True)

    # too specific... these policies will change
    def testHeaderSetsInstalled(self):
        return
        self.headers = ('no-cache','cache-in-memory',
                        'cache-with-etag','cache-with-last-modified',
                        'cache-in-proxy-1-hour','cache-in-proxy-24-hours',
                        'cache-in-browser-1-hour','cache-in-browser-24-hours',
                        'cache-in-browser-forever')
        installed = self.tool.getHeaderSets().objectIds()
        for h in self.headers:
            self.failUnless(h in installed,
                            '%s header set not installed' % h)

    # too specific... these policies will change
    def testCacheRulesInstalled(self):
        return
        self.rules = ('httpcache','plone-content-types',
                      'plone-containers','plone-templates',
                      'resource-registries','downloads','dtml-css')
        installed = self.tool.getRules().objectIds()
        for r in self.rules:
            self.failUnless(r in installed,
                            '%s rule not installed' % r)

    def _testCachingPolicyManagerRemoved(self):
        self.fail('not yet implemented...')

    def testSquidToolSetup(self):
        squidtool = self.portal.portal_squid
        expression = 'python:object.%s.getUrlsToPurge(object)' % CACHE_TOOL_ID
        self.failUnlessEqual(squidtool.getUrlExpression(), expression)

    def _testPolicyHTTPCaches(self):
        self.fail('not yet implemented...')

    def testResourceRegistrySetup(self):
        cache = getattr(self.portal, RR_CACHE_ID, None)
        self.failUnless(cache is not None)
        settings = cache.getSettings()
        self.failUnlessEqual(cache.title, 'Cache for saved ResourceRegistry files')
        self.failUnlessEqual(settings['max_age'], 86400)
        self.failUnlessEqual(settings['request_vars'], ('URL',))
        self.csstool = self.portal.portal_css
        self.failUnlessEqual(self.csstool.ZCacheable_getManagerId(), RR_CACHE_ID)
        self.failUnless(self.csstool.ZCacheable_enabled())
        self.jstool = self.portal.portal_javascripts
        self.failUnlessEqual(self.jstool.ZCacheable_getManagerId(), RR_CACHE_ID)
        self.failUnless(self.jstool.ZCacheable_enabled())

    def _testSiteProperties(self):
        self.fail('not yet implemented...')

    def testConfigletInstalled(self):
        self.controlpanel = self.portal.portal_controlpanel
        installed = [a.getAction(self)['title'] for a in self.controlpanel.listActions()]
        self.failUnless('Cache Configuration Tool' in installed)

class TestUninstall(CacheFuTestCase):
    """ ensure product is properly uninstalled """

    def afterSetUp(self):
        """ uninstall requieres 'Manager' role """
        self.setRoles(['Manager', 'Member'])
        self.portal.portal_cache_settings.setEnabled(True)
        self.qitool = self.portal.portal_quickinstaller
        self.qitool.uninstallProducts(products=[PROJECT_NAME])

    def testProductUninstalled(self):
        self.failIf(self.qitool.isProductInstalled(PROJECT_NAME))

    def testToolUninstalled(self):
        self.failIf(getattr(self.portal, CACHE_TOOL_ID, None) is not None)

    def testSquidToolUninstalled(self):
        """ uninstalling the product now also removes CMFSquidTool """
        self.failIf(getattr(self.portal, 'portal_squid', None) is not None)

    def testResourceRegistryRestore(self):
        cache = getattr(self.portal, RR_CACHE_ID, None)
        self.failIf(cache is not None)
        self.csstool = self.portal.portal_css
        #self.assertEqual(self.csstool.ZCacheable_getManagerId(), '---')
        self.failIf(self.csstool.ZCacheable_getManagerId() is not None)
        self.failIf(self.csstool.ZCacheable_enabled())
        self.jstool = self.portal.portal_javascripts
        self.failIf(self.jstool.ZCacheable_getManagerId() is not None)
        self.failIf(self.jstool.ZCacheable_enabled())

    def testConfigletsUninstalled(self):
        self.configlets = ('Cache Configuration Tool',)
        self.controlpanel = self.portal.portal_controlpanel
        installed = [a.getAction(self)['title'] for a in self.controlpanel.listActions()]
        for c in self.configlets:
            self.failIf(c in installed,
                            '%s configlet installed' % c)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    #suite.addTest(makeSuite(CacheManagerTest))
    suite.addTest(makeSuite(TestInstall))
    suite.addTest(makeSuite(TestUninstall))
    return suite

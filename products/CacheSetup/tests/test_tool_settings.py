import unittest

from base import CacheFuTestCase

from Products.CMFCore.utils  import getToolByName
import Products.CacheSetup.config as config

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

        self.portal.portal_quickinstaller.installProducts(['CacheSetup'])

        # We have added a skin so we need to rebuild the skin object
        # (since the object is cached in the current request)
        self._refreshSkinData()

    # cacheConfig deprecated
    # 
    #def test_set_domains(self):
    #    pcs = self.portal.portal_cache_settings
    #    pcs.setCacheConfig('squid')
    #    pcs.setDomains('\nfoo.com\n\nhttp://www.bar.com\nhttps://bar.com\nwww.foo.com:8080')
    #    self.assertEqual(pcs.getDomains(), ('http://foo.com:80','http://www.bar.com:80','https://bar.com:443','http://www.foo.com:8080'))
    #    pcs.setCacheConfig('squid_behind_apache')
    #    pcs.setDomains('\nfoo.com\n\nhttp://www.bar.com\nhttps://bar.com\nwww.foo.com:8080')
    #    self.assertEqual(pcs.getDomains(), ('http://foo.com:80','http://www.bar.com:80','https://bar.com:443','http://www.foo.com:8080'))
        
    #def test_squid_urls(self):
    #    pcs = self.portal.portal_cache_settings
    #    squid_tool = self.portal.portal_squid
    #
    #    pcs.setCacheConfig('squid_behind_apache')
    #    pcs.setSquidURLs(['http://localhost:3128'])
    #    self.assertEqual(pcs.getSquidURLs(), ('http://localhost:3128',))
    #    self.assertEqual(squid_tool.getSquidURLs(), 'http://localhost:3128')
    #    
    #    pcs.setSquidURLs(['http://localhost:3128','http://someotherhost:3128'])
    #    self.assertEqual(pcs.getSquidURLs(), ('http://localhost:3128','http://someotherhost:3128'))
    #    self.assertEqual(squid_tool.getSquidURLs(), 'http://localhost:3128\nhttp://someotherhost:3128')

    def test_vary_header(self):
        pcs = self.portal.portal_cache_settings

        pcs.setVaryHeader('foobar')
        self.assertEqual(pcs.getVaryHeader(), 'foobar')

        #for header_set in pcs.getHeaderSets().objectValues():
        #    self.assertEqual(header_set.getVary(), 'foobar')

    
    #def test_cache_config(self):
    #    pcs = self.portal.portal_cache_settings
    #    self.assertEqual(pcs.getCacheConfig(), 'zserver')
    #    rules = pcs.getRules()
    #    rule = getattr(rules, 'plone-content-types')
    #    self.assertEqual(rule.getHeaderSetIdAnon(), 'cache-in-memory')
    #
    #    pcs.setCacheConfig('apache')
    #    self.assertEqual(rule.getHeaderSetIdAnon(), 'cache-in-memory')
    #
    #    pcs.setCacheConfig('squid')
    #    self.assertEqual(rule.getHeaderSetIdAnon(), 'cache-in-proxy-1-hour')
    #
    #    pcs.setCacheConfig('squid_behind_apache')
    #    self.assertEqual(rule.getHeaderSetIdAnon(), 'cache-in-proxy-1-hour')
    #    
    #    pcs.setCacheConfig('zserver')
    #    self.assertEqual(rule.getHeaderSetIdAnon(), 'cache-in-memory')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

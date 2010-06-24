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

    def test_rule_and_header_set(self):
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        pcs = self.portal.portal_cache_settings
        member = self.portal.portal_membership.getAuthenticatedMember()

        # these aren't comprehensive -- there is better coverage in test_functional
        (rule, header_set) = pcs.getRuleAndHeaderSet(d.REQUEST, d, 'document_view', None)
        self.assertEqual(rule.getId(), 'plone-content-types')
        self.assertEqual(header_set.getId(), 'cache-in-memory')
        (rule, header_set) = pcs.getRuleAndHeaderSet(d.REQUEST, d, 'document_view', member)
        self.assertEqual(rule.getId(), 'plone-content-types')
        self.assertEqual(header_set.getId(), 'cache-with-etag')

        (rule, header_set) = pcs.getRuleAndHeaderSet(self.portal.REQUEST, self.portal, 'sitemap', None)
        self.assertEqual(rule.getId(), 'plone-templates')
        self.assertEqual(header_set.getId(), 'cache-in-memory')
        (rule, header_set) = pcs.getRuleAndHeaderSet(self.portal.REQUEST, self.portal, 'sitemap', member)
        self.assertEqual(rule.getId(), 'plone-templates')
        self.assertEqual(header_set.getId(), 'cache-with-etag')
        
        (rule, header_set) = pcs.getRuleAndHeaderSet(self.portal.REQUEST, self.folder, 'folder_contents', None)
        self.assertEqual(rule.getId(), 'plone-containers')
        self.assertEqual(header_set.getId(), 'cache-in-memory')
        (rule, header_set) = pcs.getRuleAndHeaderSet(self.portal.REQUEST, self.folder, 'folder_contents', member)
        self.assertEqual(rule.getId(), 'plone-containers')
        self.assertEqual(header_set.getId(), 'cache-with-etag')
        
        image = getattr(self.portal, 'addFavorite.gif') # associated with HTTPCache in Plone 2.1.2
        (rule, header_set) = pcs.getRuleAndHeaderSet(image.REQUEST, image, None, None)
        self.assertEqual(rule.getId(), 'httpcache')
        self.assertEqual(header_set.getId(), 'cache-in-browser-24-hours')
        (rule, header_set) = pcs.getRuleAndHeaderSet(image.REQUEST, image, None, member)
        self.assertEqual(rule.getId(), 'httpcache')
        self.assertEqual(header_set.getId(), 'cache-in-browser-24-hours')
        
    def test_purged_urls(self):
        pcs = self.portal.portal_cache_settings
        url_tool = getToolByName(self.portal, 'portal_url')

        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        doc_url = url_tool.getRelativeUrl(d)
        purged_urls = [doc_url + url for url in ['','/','/view','/document_view']]
        purged_urls.sort()

        pcs.setCacheConfig('zserver')
        urls = pcs.getUrlsToPurge(d)
        self.assertEqual(urls, [])

        pcs.setCacheConfig('apache')
        urls = pcs.getUrlsToPurge(d)
        self.assertEqual(urls, [])

        pcs.setCacheConfig('squid')
        urls = pcs.getUrlsToPurge(d)
        urls.sort()
        self.assertEqual(urls, purged_urls)

        d = makeContent(self.folder, 'index_html', 'Document', 'My document')
        doc_url = url_tool.getRelativeUrl(d)
        purged_urls = [doc_url + url for url in ['','/','/view','/document_view']]
        parent_url = url_tool.getRelativeUrl(d.getParentNode())
        purged_urls += [parent_url + url for url in ['','/','/view']]
        purged_urls.sort()

        urls = pcs.getUrlsToPurge(d)
        urls.sort()
        self.assertEqual(urls, purged_urls)

    def test_purged_urls_for_squid_behind_apache(self):
        pcs = self.portal.portal_cache_settings
        url_tool = getToolByName(self.portal, 'portal_url')
        pcs.setCacheConfig('squid_behind_apache')
        pcs.setDomains(['http://www.mysite.com','https://www.mysite.com'])

        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

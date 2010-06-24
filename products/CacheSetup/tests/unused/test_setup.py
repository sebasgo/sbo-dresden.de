# This Python file uses the following encoding: utf-8
""" header sets and cache rules initialisation tests """

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from Products.CacheSetup.config import *

class TestHeaderSetsSetup(CacheFuTestCase):
    """ ensure header sets are initialized with proper values """

    def afterSetUp(self):
        self.tool = self.portal.portal_cache_settings
        self.sets = self.tool.getHeaderSets()

    def testNoCache(self):
        s = getattr(self.sets, 'no-cache')
        # what type?
        self.failUnlessEqual(s.Title(), 'Do not cache')
        self.failUnlessEqual(s.getDescription(), 'Page should not be cached.')
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 0)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 1)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 1)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInMemory(self):
        s = getattr(self.sets, 'cache-in-memory')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in Memory')
        self.failUnlessEqual(s.getDescription(), "Page should be cached in memory on the server.  Page should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the page's ETag before displaying a cached page.")
        self.failUnlessEqual(s.getPageCache(), 1)
        self.failUnlessEqual(s.getLastModified(), 'delete')
        self.failUnlessEqual(s.getEtag(), 1)
        self.failUnlessEqual(s.getEnable304s(), 1)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 0)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 1)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheWithEtag(self):
        s = getattr(self.sets, 'cache-with-etag')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache with ETag')
        self.failUnlessEqual(s.getDescription(), "Page should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the page's ETag before displaying a cached page.")
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'delete')
        self.failUnlessEqual(s.getEtag(), 1)
        self.failUnlessEqual(s.getEnable304s(), 1)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 0)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 1)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheWithLastModified(self):
        s = getattr(self.sets, 'cache-with-last-modified')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache file with Last-Modified')
        self.failUnlessEqual(s.getDescription(), "File should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the file's Last-Modified time before displaying a cached file.")
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 1)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 0)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 1)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInProxy1Hour(self):
        s = getattr(self.sets, 'cache-in-proxy-1-hour')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in proxy cache for 1 hour')
        self.failUnlessEqual(s.getDescription(), 'Cache the page in the proxy cache for up to 1 hour.  If the template is associated with PageCacheManager, the page may be cached in memory on the server.')
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 3600)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 0)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInProxy24Hours(self):
        s = getattr(self.sets, 'cache-in-proxy-24-hours')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in proxy cache for 24 hours')
        self.failUnlessEqual(s.getDescription(), 'Cache the page in the proxy cache for up to 24 hours.  If the template is associated with PageCacheManager, the page may be cached in memory on the server.')
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 0)
        self.failUnlessEqual(s.getSMaxAge(), 86400)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 1)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 0)
        self.failUnlessEqual(s.getPrivate(), 0)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInBrowser1Hour(self):
        s = getattr(self.sets, 'cache-in-browser-1-hour')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in browser for 1 hour')
        self.failUnlessEqual(s.getDescription(), "Cache the page in the client's browser for 1 hour.  Also caches in the proxy for up to 1 hour, and if the template is associated with PageCacheManager, the page may be cached in memory on the server.")
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 3600)
        self.failUnlessEqual(s.getSMaxAge(), 3600)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 1)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 1)
        self.failUnlessEqual(s.getPrivate(), 0)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInBrowser24Hours(self):
        s = getattr(self.sets, 'cache-in-browser-24-hours')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in browser for 24 hours')
        self.failUnlessEqual(s.getDescription(), "Cache the page in the client's browser for 24 hours.  Also caches in the proxy for up to 24 hours, and if the template is associated with PageCacheManager, the page may be cached in memory on the server.")
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 86400)
        self.failUnlessEqual(s.getSMaxAge(), 86400)
        self.failUnlessEqual(s.getMustRevalidate(), 1)
        self.failUnlessEqual(s.getProxyRevalidate(), 1)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 1)
        self.failUnlessEqual(s.getPrivate(), 0)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

    def testCacheInBrowserForever(self):
        s = getattr(self.sets, 'cache-in-browser-forever')
        # what type?
        self.failUnlessEqual(s.Title(), 'Cache in browser forever')
        self.failUnlessEqual(s.getDescription(), "Cache the file in the client's browser for 1 year.  Also caches in the proxy for up to 1 year.  No ETag is set so the file will not be cached in memory on the server.")
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')
        self.failUnlessEqual(s.getEtag(), 0)
        self.failUnlessEqual(s.getEnable304s(), 0)
        self.failUnlessEqual(s.getVary(), True)
        self.failUnlessEqual(s.getMaxAge(), 31536000)
        self.failUnlessEqual(s.getSMaxAge(), 31536000)
        self.failUnlessEqual(s.getMustRevalidate(), 0)
        self.failUnlessEqual(s.getProxyRevalidate(), 0)
        self.failUnlessEqual(s.getNoCache(), 0)
        self.failUnlessEqual(s.getNoStore(), 0)
        self.failUnlessEqual(s.getPublic(), 1)
        self.failUnlessEqual(s.getPrivate(), 0)
        self.failUnlessEqual(s.getNoTransform(), 0)
        self.failUnlessEqual(s.getPreCheck(), None)
        self.failUnlessEqual(s.getPostCheck(), None)
        # in catalog?

class TestCacheRulesSetup(CacheFuTestCase):
    """ ensure cache rules are initialized with proper values """

    def afterSetUp(self):
        self.tool = self.portal.portal_cache_settings
        self.rules = self.tool.getRules()

    def testHTTPCache(self):
        r = getattr(self.rules, 'httpcache')
        # what type?
        self.failUnlessEqual(r.Title(), 'HTTPCache')
        self.failUnlessEqual(r.getCacheManager(), 'HTTPCache')
        self.failUnlessEqual(r.getDescription(), 'Rule for content associated with HTTPCache.  This content is cached in the proxy and in the browser.  ETags are not useful because these files have no personalization.')
        self.failUnlessEqual(r.getCacheStop(), ())
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'cache-in-browser-24-hours')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'cache-in-browser-24-hours')
        self.failUnlessEqual(r.getVaryExpression(), "python:getattr(object, 'meta_type', None) not in ['Filesystem Image', 'Image'] and rule.portal_cache_settings.getVaryHeader() or ''")
        # in catalog?

    def testPloneContentTypes(self):
        r = getattr(self.rules, 'plone-content-types')
        # what type?
        self.failUnlessEqual(r.Title(), 'Content')
        self.failUnlessEqual(r.getDescription(), 'Rule for views of plone content types.  Anonymous users are served content object views from the proxy cache.  These views are purged when content objects change.  Authenticated users are served pages from memory.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the navigation tree stays up to date.')
        self.failUnlessEqual(r.getContentTypes(), ('Document','Event','Link','News Item','Image','File'))
        self.failUnlessEqual(r.getDefaultView(), True)
        self.failUnlessEqual(r.getTemplates(), ())
        self.failUnlessEqual(r.getCacheStop(), ('portal_status_message','statusmessages'))
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'cache-in-memory')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'cache-with-etag')
        self.failUnlessEqual(r.getEtagComponents(), ('member','catalog_modified','language','gzip','skin'))
        self.failUnlessEqual(r.getEtagRequestValues(), ('month','year','orig_query'))
        self.failUnlessEqual(r.getEtagTimeout(), 3600)
        self.failUnlessEqual(r.getPurgeExpression(), 'python:object.getImageAndFilePurgeUrls()')
        # in catalog?

    def testPloneContainers(self):
        r = getattr(self.rules, 'plone-containers')
        # what type?
        self.failUnlessEqual(r.Title(), 'Containers')
        self.failUnlessEqual(r.getDescription(), "Rule for views of Plone containers.  Both anonymous and authenticated users are served pages from memory, not the proxy cache.  The reason is that we can\'t easily purge container views when they change since container views depend on all of their contained objects, and contained objects do not necessarily purge their containers' views when they change.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the contents and the navigation tree stays up to date.")
        self.failUnlessEqual(r.getContentTypes(), ('Topic','Folder','Plone Site','Large Plone Folder'))
        self.failUnlessEqual(r.getDefaultView(), True)
        self.failUnlessEqual(r.getTemplates(), ('folder_contents','RSS'))
        self.failUnlessEqual(r.getCacheStop(), ('portal_status_message','statusmessages'))
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'cache-in-memory')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'cache-with-etag')
        self.failUnlessEqual(r.getEtagComponents(), ('member','catalog_modified','language','gzip','skin'))
        self.failUnlessEqual(r.getEtagRequestValues(), ('b_start','month','year','orig_query'))
        self.failUnlessEqual(r.getEtagExpression(), "python:request.get('__cp',None) is not None")
        self.failUnlessEqual(r.getEtagTimeout(), 3600)
        # in catalog?

    def testPloneTemplates(self):
        r = getattr(self.rules, 'plone-templates')
        # what type?
        self.failUnlessEqual(r.Title(), 'Templates')
        self.failUnlessEqual(r.getDescription(), 'Rule for various non-form templates.  Both anonymous and authenticated users are served pages from memory, not the proxy cache, because some of these templates depend on catalog queries.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the contents and the navigation tree stays up to date.')
        self.failUnlessEqual(r.getTemplates(), ('accessibility-info','sitemap','recently_modified'))
        self.failUnlessEqual(r.getCacheStop(), ('portal_status_message','statusmessages'))
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'cache-in-memory')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'cache-with-etag')
        self.failUnlessEqual(r.getEtagComponents(), ('member','catalog_modified','language','gzip','skin'))
        self.failUnlessEqual(r.getEtagRequestValues(), ('month','year','orig_query'))
        self.failUnlessEqual(r.getEtagTimeout(), 3600)
        # in catalog?

    def testResourceRegistries(self):
        r = getattr(self.rules, 'resource-registries')
        # what type?
        self.failUnlessEqual(r.Title(), 'CSS & JS')
        self.failUnlessEqual(r.getDescription(), 'Rule for CSS and JS generated by ResourceRegistries.  These files are cached "forever" (1 year) in squid and in browsers.  There is no need to purge these files because when they are changed and saved in portal_css/portal_js, their file names change.  ETags are not useful because these files have no personalization.')
        self.failUnlessEqual(r.getCacheManager(), OFS_CACHE_ID)
        self.failUnlessEqual(r.getCacheStop(), ())
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getTypes(), ('File',))
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'expression')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'expression')
        self.failUnlessEqual(r.getHeaderSetIdExpression(), 'python:object.getHeaderSetIdForCssAndJs()')
        self.failUnlessEqual(r.getVaryExpression(), 'string:')
        # in catalog?

    def testDownloads(self):
        r = getattr(self.rules, 'downloads')
        # what type?
        self.failUnlessEqual(r.Title(), 'Files & Images')
        self.failUnlessEqual(r.getDescription(), 'Rule for ATFile and ATImage downloads.  Files that are viewable by Anonymous users are cached in squid; files that are not viewable by Anonymous users are cached only on the browser.  ETags are not useful because these files have no personalization.')
        self.failUnlessEqual(r.getCacheManager(), OFS_CACHE_ID)
        self.failUnlessEqual(r.getTypes(), ('Image', 'File'))
        self.failUnlessEqual(r.getCacheStop(), ())
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'expression')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'expression')
        self.failUnlessEqual(r.getHeaderSetIdExpression(), "python:object.portal_cache_settings.canAnonymousView(object) and 'cache-in-proxy-24-hours' or 'no-cache'")
        self.failUnlessEqual(r.getVaryExpression(), 'string:')
        # in catalog?

    def testDTMLCSS(self):
        r = getattr(self.rules, 'dtml-css')
        # what type?
        self.failUnlessEqual(r.Title(), 'DTML CSS files')
        self.failUnlessEqual(r.getDescription(), 'Rule for css files generated with DTML.  These files will be cached in the browser for 24 hours.')
        self.failUnlessEqual(r.getTemplates(), ('IEFixes.css',))
        self.failUnlessEqual(r.getCacheStop(), ())
        self.failUnlessEqual(r.getLastModifiedExpression(), 'python:object.modified()')
        self.failUnlessEqual(r.getHeaderSetIdAnon(), 'cache-in-browser-24-hours')
        self.failUnlessEqual(r.getHeaderSetIdAuth(), 'cache-in-browser-24-hours')
        self.failUnlessEqual(r.getEtagComponents(), ())
        self.failUnlessEqual(r.getEtagRequestValues(), ())
        self.failUnlessEqual(r.getEtagTimeout(), None)
        self.failUnlessEqual(r.getVaryExpression(), 'string:')
        # in catalog?

class TestNoSetupOnReinstall(CacheFuTestCase):
    """ ensure reinstall doesn't modify header sets or cache rules current values """
    # this is not working; need to find out why

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self.qitool = self.portal.portal_quickinstaller
        self.tool = self.portal.portal_cache_settings
        self.sets = self.tool.getHeaderSets()
        self.rules = self.tool.getRules()

    def testHeaderSets(self):
        """ change some header sets, reinstall and see if we have same values """
        s = getattr(self.sets, 'no-cache')
        s.setTitle('Title')
        s.setDescription('Description')
        s = getattr(self.sets, 'cache-in-memory')
        s.setPageCache(0)
        s.setLastModified('yes')
        self.qitool.reinstallProducts(products=[PROJECT_NAME])
        s = getattr(self.sets, 'no-cache')
        self.failUnlessEqual(s.Title(), 'Title')
        self.failUnlessEqual(s.getDescription(), 'Description')
        s = getattr(self.sets, 'cache-in-memory')
        self.failUnlessEqual(s.getPageCache(), 0)
        self.failUnlessEqual(s.getLastModified(), 'yes')

    def testCacheRules(self):
        """ change some cache rules, reinstall and see if we have same values """
        r = getattr(self.rules, 'httpcache')
        r.setTitle('Title')
        r.setDescription('Description')
        r = getattr(self.rules, 'plone-content-types')
        r.setContentTypes([])
        r.setDefaultView(False)
        self.qitool.reinstallProducts(products=[PROJECT_NAME])
        r = getattr(self.rules, 'httpcache')
        self.failUnlessEqual(r.Title(), 'Title')
        self.failUnlessEqual(r.getDescription(), 'Description')
        r = getattr(self.rules, 'plone-content-types')
        self.failUnlessEqual(r.getContentTypes(), ())
        self.failUnlessEqual(r.getDefaultView(), False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHeaderSetsSetup))
    suite.addTest(makeSuite(TestCacheRulesSetup))
    #suite.addTest(makeSuite(TestNoSetupOnReinstall))
    return suite

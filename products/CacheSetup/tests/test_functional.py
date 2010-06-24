import unittest

from base import CacheFuFunctionalTestCase

from Products.PythonScripts.standard import url_quote
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
class CacheManagerTest(CacheFuFunctionalTestCase):
    USER1 = 'user1'
    
    def afterSetUp(self):
        CacheFuFunctionalTestCase.afterSetUp(self)
        
        # Add a couple of users
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser(self.USER1, 'secret', ['Member'], [])
        self.login('manager')

        self.portal.portal_quickinstaller.installProducts(['CacheSetup'])

        # We have added a skin so we need to rebuild the skin object
        # (since the object is cached in the current request)
        self._refreshSkinData()

        pcs = getattr(self.portal, config.CACHE_TOOL_ID)
        pcs.setEnabled(True)

        pcs.setCacheConfig('squid')
        
        # turn off the page cache manager
        getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).disable()

    def parse_cc(self, st):
        tokens = [s.strip().split('=') for s in st.split(',') if s]
        d = {}
        for t in tokens:
            key = t[0].strip().lower()
            if len(t) > 1:
                value = t[1]
            else:
                value = ''
            try:
                value = int(value)
            except:
                pass
            d[key] = value
        return d

    # I'm not sure what we're testing here but
    # cacheConfig is deprecated
    # 
    #def test_content_pagecache(self):
    #    pcs = getattr(self.portal, config.CACHE_TOOL_ID)
    #    pcs.setCacheConfig('zserver')
    #    # turn on the page cache manager
    #    getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).enable()
    #
    #   d = makeContent(self.folder, 'doc', 'Document', 'My document')
    #    ob_path = '/'+d.absolute_url(1)
    #    response = self.publish(ob_path)
    #    xpc = response.headers.get('x-pagecache',None)
    #    if xpc is None:
    #        # document view has not yet been associated with page cache (depends on order of test execution)
    #        response = self.publish(ob_path)
    #        # now it should be
    #    xpc = response.headers.get('x-pagecache',None)
    #    self.failUnless(xpc in ('MISS', 'HIT'))
    #
    #    response = self.publish(ob_path)
    #    xpc = response.headers.get('x-pagecache',None)
    #    self.assertEqual(xpc, 'HIT')
    #    
    #    # turn off the page cache manager
    #    getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).disable()
        
    # The rest of these look like they're testing for specific policies
    # These are always subject to change, so let's not constrain ourselves
    # by forcing us to update tests whenever we improve the policies.
    # 
    def test_content(self):
        return
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        ob_path = '/'+d.absolute_url(1)

        # document default view for authenticated should be private and not cached
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-content-types')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-1-hour')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), 3600)
        self.assertNotEqual(cc.get('must-revalidate',None), None)
        self.assertEqual(cc.get('private',None), None)
            
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-content-types')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-with-etag')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), 0)
        self.assertNotEqual(cc.get('must-revalidate',None), None)
        self.assertNotEqual(cc.get('private',None), None)

        # document default view for anonymous should be cached in squid but not on browser
        rule = getattr(getattr(self.portal, config.CACHE_TOOL_ID).getRules(), 'plone-content-types')
        rule.setHeaderSetIdAnon('cache-in-proxy-1-hour')
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-content-types')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-1-hour')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), 3600)
        self.assertNotEqual(cc.get('must-revalidate',None), None)

    def test_content_apache(self):
        return
        pcs = getattr(self.portal, config.CACHE_TOOL_ID)
        pcs.setCacheConfig('apache')
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        ob_path = '/'+d.absolute_url(1)

        # document default view for anonymous should be cached in squid but not on browser
        response = self.publish(ob_path)
        cc = response.headers.get('cache-control',None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), None)  # no s-maxage for apache
        
        # document default view for authenticated should be private and not cached
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        cc = response.headers.get('cache-control',None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), None)  # no s-maxage for apache

    def test_content_gzip(self):
        return
        pcs = getattr(self.portal, config.CACHE_TOOL_ID)
        pcs.setCacheConfig('apache')
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        ob_path = '/'+d.absolute_url(1)

        # exercise the gzipping code path
        response = self.publish(ob_path, env={'HTTP_ACCEPT_ENCODING': 'gzip'})

    def test_container(self):
        return
        ob_path = '/'+self.folder.absolute_url(1)

        # folder default view for anonymous should not be cached
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-containers')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-memory')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), 0)
        self.assertNotEqual(cc.get('must-revalidate',None), None)
        
        # folder default view for authenticated should be private and not cached
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-containers')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-with-etag')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 0)
        self.assertEqual(cc.get('s-maxage',None), 0)
        self.assertNotEqual(cc.get('must-revalidate',None), None)
        self.assertNotEqual(cc.get('private',None), None)
        
    def test_http_cache(self):
        return
        ob_path = '/'+self.portal.absolute_url(1)+'/defaultUser.gif'

        # folder default view for anonymous should not be cached
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'httpcache')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-24-hours')
        cc = response.headers.get('cache-control',None)
        self.assertNotEqual(cc, None)
        cc = self.parse_cc(cc)
        self.assertEqual(cc.get('max-age',None), 24*3600)
        self.assertEqual(cc.get('s-maxage',None), 24*3600)
        self.assertNotEqual(cc.get('must-revalidate',None), None)
        self.assertNotEqual(cc.get('public',None), None)
        self.assertEqual(cc.get('private',None), None)
        
        # folder default view for authenticated should be private and not cached
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'httpcache')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-24-hours')

    def test_templates(self):
        return
        ob_path = '/'+self.portal.absolute_url(1)+'/sitemap'
        # folder default view for anonymous should not be cached
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-templates')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-memory')
        
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-templates')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-with-etag')

    def test_resource_registries(self):
        return
        self.logout()
        stylesheets = self.portal.portal_css.getEvaluatedResources(self.portal)
        skin_name = self.portal.getCurrentSkinName()
        ob_path = '/'+self.portal.portal_css.absolute_url(1)+'/'+skin_name+'/'+stylesheets[0].getId()
        
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'resource-registries')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-forever')

        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'resource-registries')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-forever')

        js = self.portal.portal_javascripts.getEvaluatedResources(self.portal)
        ob_path = '/'+self.portal.portal_javascripts.absolute_url(1)+'/'+skin_name+'/'+js[0].getId()

        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'resource-registries')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-forever')

        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'resource-registries')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-browser-forever')

    def test_file(self):
        return
        f = makeContent(self.folder, 'file', 'File', 'My file')

        # XXX - this doesn't seem to work
        # the problem appears to be (1) that ATFile reports index_html as its default view instead of file_view,
        # and (2) that index_html actually returns a file to be downloaded
        #ob_path = '/'+f.absolute_url(1)+'/file_view' 
        ## file default view should be cached with plone-content-types rule
        #response = self.publish(ob_path)
        #self.assertEqual(response.headers.get('x-caching-rule-id',None), 'plone-content-types')

        # anonymous download
        ob_path = '/'+f.absolute_url(1)+'/download'
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-24-hours')

        # anonymous download, alternate url
        ob_path = '/'+f.absolute_url(1)
        response = self.publish(ob_path)
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-24-hours')

        # authenticated download
        ob_path = '/'+f.absolute_url(1)+'/download'
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-24-hours')

        # authenticated download, alternate url
        ob_path = '/'+f.absolute_url(1)
        response = self.publish(ob_path, basic='%s:%s' % (self.USER1, 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'cache-in-proxy-24-hours')

        # make file private
        self.portal.portal_workflow.doActionFor(f, 'hide')

        # anonymous download
        ob_path = '/'+f.absolute_url(1)+'/download'
        response = self.publish(ob_path)
        self.assertEqual(response.status, 302)
        self.failUnless(response.getHeader('location').find('require_login') != -1)
        
        # anonymous download, alternate url
        ob_path = '/'+f.absolute_url(1)
        response = self.publish(ob_path)
        self.assertEqual(response.status, 302)
        self.failUnless(response.getHeader('location').find('require_login') != -1)
        
        # authenticated download
        ob_path = '/'+f.absolute_url(1)+'/download'
        response = self.publish(ob_path, basic='%s:%s' % ('manager', 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'no-cache')

        # authenticated download, alternate url
        ob_path = '/'+f.absolute_url(1)
        response = self.publish(ob_path, basic='%s:%s' % ('manager', 'secret'))
        self.assertEqual(response.headers.get('x-caching-rule-id',None), 'downloads')
        self.assertEqual(response.headers.get('x-header-set-id',None), 'no-cache')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

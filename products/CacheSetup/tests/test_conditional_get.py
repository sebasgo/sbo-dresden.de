import unittest

from base import CacheFuFunctionalTestCase

from App.Common import rfc1123_date
from Products.PythonScripts.standard import url_quote
from Products.CMFCore.utils  import getToolByName
import Products.CacheSetup.config as config
from DateTime import DateTime

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

        pcs = self.portal.portal_cache_settings
        pcs.setEnabled(True)

        headers = pcs.getHeaderSets()
        headers.manage_delObjects(headers.objectIds())
        headers.invokeFactory(id='header_set', type_name='HeaderSet')
        h = headers.header_set
        h.setEtag(True)
        h.setEnable304s(True)

        rules = pcs.getRules()
        rules.manage_delObjects(rules.objectIds())
        rules.invokeFactory(id='rule', type_name='ContentCacheRule')
        rule = rules.rule
        rule.setHeaderSetIdAnon('header_set')
        rule.setHeaderSetIdAuth('header_set')
        rule.setContentTypes(['Document'])
        rule.setEtagComponents(['expression'])
        rule.setEtagExpression('string:my_etag')
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(None)

        getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).disable()


    def test_pt_304s(self):
        self.folder.invokeFactory(id='ptdoc304', type_name='Document')
        doc = self.folder.ptdoc304
        ob_path = doc.absolute_url_path()

        pcs = self.portal.portal_cache_settings
        h = pcs.getHeaderSets().header_set
        h.setEnable304s(True)
        h.setPageCache(False)
        rule = pcs.getRules().rule

        mod_time = doc.modified().timeTime()

        #etag = '|my_etag'
        ## good etag, expired mod time
        #response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time-3600)})
        #self.assertEqual(response.status, 200)

        # straight request should give 200
        response = self.publish(ob_path)
        self.assertEqual(response.status, 200)

        # good etag
        etag = response.headers.get('ETag')
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag})
        self.assertEqual(response.status, 304)
                                
        # good etag, current mod time
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 304)

        # bad etag
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo'})
        self.assertEqual(response.status, 200)

        # good etag, expired mod time
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time-3600)})
        self.assertEqual(response.status, 200)

        # bad etag, current mod time
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo', 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        # no etag, current mod time
        response = self.publish(ob_path, env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        h.setEtag(False)

        # current mod time, content etag not available
        response = self.publish(ob_path, env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 304)

        # expired mod time, content etag not available
        response = self.publish(ob_path, env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time-3600)})
        self.assertEqual(response.status, 200)

        # good etag, current mod time, content etag not available
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        # bad etag, current mod time, content etag not available
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo', 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        # good etag, expired  mod time, content etag not available
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time-3600)})
        self.assertEqual(response.status, 200)

        h.setEnable304s(False)
        # 304s disabled
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag})
        self.assertEqual(response.status, 200)

        # 304s disabled
        mod_time = doc.modified().timeTime()
        response = self.publish(ob_path, env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)
        

    def test_pagecache_304s(self):
        getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).enable()
        self.folder.invokeFactory(id='pcdoc304', type_name='Document')
        doc = self.folder.pcdoc304
        mod_time = doc.modified().timeTime()
        ob_path = doc.absolute_url_path()

        pcs = self.portal.portal_cache_settings
        h = pcs.getHeaderSets().header_set
        h.setEnable304s(True)
        h.setPageCache(True)
        rule = pcs.getRules().rule
        
        # straight request should give 200
        response = self.publish(ob_path)
        response = self.publish(ob_path) # 2nd time so we are associated with the cache
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getHeader('x-pagecache'), 'MISS')
        response = self.publish(ob_path)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getHeader('x-pagecache'), 'HIT')

        # correct etag - 304
        etag = response.headers.get('ETag')
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag})
        self.assertEqual(response.status, 304)
        self.assertEqual(response.getHeader('x-pagecache'), None)
                                
        # bad etag - 200
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo'})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getHeader('x-pagecache'), 'HIT')

        # correct etag, 304s disabled - 200
        h.setEnable304s(False)
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getHeader('x-pagecache'), 'HIT')

        h.setEnable304s(True)

        # correct etag, current mod time - 304
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 304)

        # bad etag
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo'})
        self.assertEqual(response.status, 200)

        # good etag, expired mod time
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': etag, 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time-3600)})
        self.assertEqual(response.status, 200)

        # bad etag, current mod time
        response = self.publish(ob_path, env={'HTTP_IF_NONE_MATCH': 'foo', 'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        # no etag, current mod time
        response = self.publish(ob_path, env={'HTTP_IF_MODIFIED_SINCE': rfc1123_date(mod_time+3600)})
        self.assertEqual(response.status, 200)

        getattr(self.portal, config.PAGE_CACHE_MANAGER_ID).disable()
        # correct etag, cache disabled
        response = self.publish(ob_path)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getHeader('x-pagecache'), 'OFF')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

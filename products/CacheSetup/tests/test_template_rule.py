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

        pcs = self.portal.portal_cache_settings
        pcs.setEnabled(True)

        headers = pcs.getHeaderSets()
        headers.manage_delObjects(headers.objectIds())
        headers.invokeFactory(id='hs1', type_name='HeaderSet')
        headers.invokeFactory(id='hs2', type_name='HeaderSet')
        rules = pcs.getRules()
        rules.manage_delObjects(rules.objectIds())

    def test_template_do_cache(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'hs1')
        h2 = getattr(pcs.getHeaderSets(), 'hs2')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='TemplateCacheRule')
        rule = getattr(pcs.getRules(), 'my_rule')

        rule.setTitle('Template')
        self.assertEqual(rule.Title(), 'Template')
        rule.setTemplates(('foo','bar'))
        self.assertEqual(rule.getTemplates(), ('foo','bar'))
        rule.setHeaderSetIdAnon('hs1')
        self.assertEqual(rule.getHeaderSetIdAnon(), 'hs1')
        rule.setHeaderSetIdAuth('hs2')
        self.assertEqual(rule.getHeaderSetIdAuth(), 'hs2')
        rule.setCacheStop(['portal_status_message',
                           'statusmessages'])
        self.assertEqual(rule.getCacheStop(),
                         ('portal_status_message', 'statusmessages'))

        rule.setEtagComponents(['member','last_modified'])
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(3600)
        rule.reindexObject()

        member = self.portal.portal_membership.getAuthenticatedMember()
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'foo', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'foo', None).getId(), 'hs1')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'bar', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'foobar', member), None)

        # make sure stop words stop
        self.assertEqual(rule.getHeaderSet({}, self.portal, 'foo', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet({'portal_status_message':'foo'}, self.portal, 'foo', member), None)

        # make sure we can check getHeaderSetId by script
        self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript('test_script')
        self.portal.test_script.ZPythonScript_edit('view', 'return view==\'foobar\' and \'hs1\' or \'hs2\'')
        rule.setHeaderSetIdAuth('expression')
        rule.setHeaderSetIdExpression('python:object.test_script(view)')
        rule.setTemplates(['foo', 'foobar'])
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'foo', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'foobar', member).getId(), 'hs1')

        # make sure we can associate templates with PageCacheManager
        self.portal.manage_addProduct['PageTemplates'].manage_addPageTemplate('template', 'Title', '<html></html>')
        rule.setTemplates(['template'])
        h2.setPageCache(False)
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'template', member).getId(), 'hs2')
        self.assertEqual(self.portal.template.ZCacheable_getManagerId(), None)
        h2.setPageCache(True)
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, self.portal, 'template', member).getId(), 'hs2')
        self.assertEqual(self.portal.template.ZCacheable_getManagerId(), config.PAGE_CACHE_MANAGER_ID)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

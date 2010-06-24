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

    def test_phcm_do_cache(self):
        pcs = self.portal.portal_cache_settings
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='PolicyHTTPCacheManagerCacheRule')
        rule = getattr(pcs.getRules(), 'my_rule')

        rule.setTitle('PHCM')
        self.assertEqual(rule.Title(), 'PHCM')
        rule.setCacheManager('HTTPCache')
        self.assertEqual(rule.getCacheManager(), 'HTTPCache')
        rule.setTypes(['Filesystem Image'])
        self.assertEqual(rule.getTypes(), ('Filesystem Image',))
        rule.setIds([])
        self.assertEqual(rule.getIds(), ())
        rule.setHeaderSetIdAnon('hs1')
        self.assertEqual(rule.getHeaderSetIdAnon(), 'hs1')
        rule.setHeaderSetIdAuth('hs2')
        self.assertEqual(rule.getHeaderSetIdAuth(), 'hs2')
        rule.setCacheStop(['portal_status_message'])
        self.assertEqual(rule.getCacheStop(),('portal_status_message',))

        rule.reindexObject()

        member = self.portal.portal_membership.getAuthenticatedMember()
        image = getattr(self.portal, 'addFavorite.gif') # is associated with HTTPCache in Plone 2.1.2
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, None).getId(), 'hs1')
        nocache_image = getattr(self.portal, 'action_icon.gif') # is not associated with HTTPCache as of Plone 2.1.2
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, nocache_image, None, member), None)
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, nocache_image, None, None), None)

        rule.setTypes([])
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, member).getId(), 'hs2')
        rule.setTypes(['File'])
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, member), None)
        rule.setTypes(['Filesystem Image'])
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, member).getId(), 'hs2')

        # make sure stop words stop
        self.assertEqual(rule.getHeaderSet({}, image, None, member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet({'portal_status_message':'foo'}, image, None, member), None)

        # make sure we can check getHeaderSetId by script
        self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript('test_script')
        self.portal.test_script.ZPythonScript_edit('view', 'return \'hs1\'')
        rule.setHeaderSetIdAuth('expression')
        rule.setHeaderSetIdExpression('python:object.test_script(view)')
        self.assertEqual(rule.getHeaderSet(self.portal.REQUEST, image, None, member).getId(), 'hs1')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

import unittest
import sets

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
class TestContentRule(CacheFuTestCase):
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

    def test_content_do_cache(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'hs1')
        h2 = getattr(pcs.getHeaderSets(), 'hs2')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='ContentCacheRule')
        rule = getattr(pcs.getRules(), 'my_rule')

        rule.setTitle('My rule')
        self.assertEqual(rule.Title(), 'My rule')
        rule.setContentTypes(['Document'])
        self.assertEqual(rule.getContentTypes(),('Document',))
        rule.setDefaultView(True)
        self.assertEqual(rule.getDefaultView(), True)
        rule.setTemplates(('foo','bar'))
        self.assertEqual(rule.getTemplates(), ('foo','bar'))
        rule.setCacheStop(['portal_status_message',
                           'statusmessages'])
        self.assertEqual(rule.getCacheStop(),
                         ('portal_status_message',
                          'statusmessages',))

        rule.setHeaderSetIdAnon('hs1')
        self.assertEqual(rule.getHeaderSetIdAnon(), 'hs1')
        rule.setHeaderSetIdAuth('hs2')
        self.assertEqual(rule.getHeaderSetIdAuth(), 'hs2')

        rule.setEtagComponents(['member','last_modified'])
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(3600)
        rule.reindexObject()

        member = self.portal.portal_membership.getAuthenticatedMember()
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        e = makeContent(self.folder, 'event', 'Event', 'My event')
        pcs = self.portal.portal_cache_settings

        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member).getId(), 'hs2')

        # make sure the wrong type fails
        self.assertEqual(rule.getHeaderSet(e.REQUEST, e, 'document_view', member), None)
        self.assertEqual(rule.getHeaderSet(e.REQUEST, e, 'event_view', member), None)

        # make sure cached templates work
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'foo', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'bar', member).getId(), 'hs2')

        # make sure a non-view, non-cached template fails
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'foobar', member), None)

        # make sure stop words stop
        self.assertEqual(rule.getHeaderSet({}, d, 'document_view', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet({'portal_status_message':'foo'}, d, 'document_view', member), None)

        # make sure predicate works
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')
        rule.setPredicateExpression('python:0')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None), None)
        rule.setPredicateExpression('python:1')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')
        rule.setPredicateExpression(None)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')

        rule.setHeaderSetIdAnon('None')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None), None)
        rule.setHeaderSetIdAuth('None')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member), None)
        # reset
        rule.setHeaderSetIdAnon('hs1')
        rule.setHeaderSetIdAuth('hs2')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member).getId(), 'hs2')

        # make sure we can disable with the header id
        rule.setHeaderSetIdAnon('None')
        rule.setHeaderSetIdAuth('None')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None), None)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member), None)
        # reset
        rule.setHeaderSetIdAnon('hs1')
        rule.setHeaderSetIdAuth('hs2')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', None).getId(), 'hs1')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member).getId(), 'hs2')

        # make sure disabling views works
        rule.setDefaultView(False)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member), None)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'foo', member).getId(), 'hs2')

        # make sure delegation to script works
        self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript('test_script')
        self.portal.test_script.ZPythonScript_edit('view', 'return view==\'foobar\' and \'hs1\' or \'hs2\'')
        rule.setHeaderSetIdExpression('python:object.test_script(view)')
        rule.setHeaderSetIdAnon('expression')
        rule.setHeaderSetIdAuth('expression')
        rule.setDefaultView(True)
        rule.setTemplates(['foo', 'foobar'])
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'document_view', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'foo', member).getId(), 'hs2')
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'foobar', member).getId(), 'hs1')

        # make sure we can associate templates with PageCacheManager
        self.portal.manage_addProduct['PageTemplates'].manage_addPageTemplate('template', 'Title', '<html></html>')
        rule.setTemplates(['template'])
        h2.setPageCache(False)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'template', member).getId(), 'hs2')
        self.assertEqual(self.portal.template.ZCacheable_getManagerId(), None)
        h2.setPageCache(True)
        self.assertEqual(rule.getHeaderSet(d.REQUEST, d, 'template', member).getId(), 'hs2')
        self.assertEqual(self.portal.template.ZCacheable_getManagerId(), config.PAGE_CACHE_MANAGER_ID)

    def test_content_purge_with_fields(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'hs1')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='ContentCacheRule')
        rule = getattr(pcs.getRules(), 'my_rule')

        url_tool = getToolByName(self.portal, 'portal_url')

        rule.setTitle('My rule')
        rule.setContentTypes(['News Item'])
        rule.setDefaultView(True)
        rule.setTemplates(('foo','bar'))
        rule.setCacheStop(['portal_status_message'])
        rule.setHeaderSetIdAnon('hs1')
        rule.setHeaderSetIdAuth('hs2')
        rule.setEtagComponents(['member','last_modified'])
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(3600)
        rule.reindexObject()

        # test basic purge for a content object
        d = makeContent(self.folder, 'doc', 'News Item', 'My news')
        doc_url = url_tool.getRelativeUrl(d)
        purged_urls = sets.Set()
        purged_urls.update([doc_url + url
            for url in ['','/','/view','/newsitem_view',
                '/image', '/image_tile', '/image_thumb',
                '/image_large', '/image_preview', '/image_mini',
                '/image_icon', '/image_listing',
                '/foo','/bar']])

        urls = sets.Set()
        rule.getRelativeUrlsToPurge(d, urls)
        self.assertEqual(urls, purged_urls)

    def test_content_purge(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'hs1')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='ContentCacheRule')
        rule = getattr(pcs.getRules(), 'my_rule')

        url_tool = getToolByName(self.portal, 'portal_url')

        rule.setTitle('My rule')
        rule.setContentTypes(['Document'])
        rule.setDefaultView(True)
        rule.setTemplates(('foo','bar'))
        rule.setCacheStop(['portal_status_message',
                           'statusmessages'])
        rule.setHeaderSetIdAnon('hs1')
        rule.setHeaderSetIdAuth('hs2')
        rule.setEtagComponents(['member','last_modified'])
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(3600)
        rule.reindexObject()

        # test basic purge for a content object
        d = makeContent(self.folder, 'doc', 'Document', 'My document')
        doc_url = url_tool.getRelativeUrl(d)
        purged_urls = sets.Set()
        purged_urls.update([doc_url + url for url in ['','/','/view','/document_view','/foo','/bar']])

        urls = sets.Set()
        rule.getRelativeUrlsToPurge(d, urls)
        self.assertEqual(urls, purged_urls)

        # test purge for a folder view
        d = makeContent(self.folder, 'index_html', 'Document', 'My document')
        doc_url = url_tool.getRelativeUrl(d)
        purged_urls = sets.Set()
        purged_urls.update([doc_url + url for url in ['','/','/view','/document_view','/foo','/bar']])
        parent_url = url_tool.getRelativeUrl(d.getParentNode())
        purged_urls.update([parent_url + url for url in ['','/','/view']])
        urls = sets.Set()
        rule.getRelativeUrlsToPurge(d, urls)
        self.assertEqual(purged_urls, urls)

        # test purge with a purge script
        d = self.folder.doc
        doc_url = url_tool.getRelativeUrl(d)
        self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript('test_script')
        self.portal.test_script.ZPythonScript_edit('', 'return [context.portal_url.getRelativeUrl(context)+\'/foobar\']')
        rule.setPurgeExpression('python:object.test_script()')
        purged_urls = sets.Set()
        purged_urls.update([doc_url + url for url in ['','/','/view','/document_view','/foo','/bar', '/foobar']])
        urls = sets.Set()
        rule.getRelativeUrlsToPurge(d, urls)
        self.assertEqual(purged_urls, urls)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentRule))
    return suite

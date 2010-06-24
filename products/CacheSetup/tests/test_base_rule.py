import unittest

from base import CacheFuTestCase

from DateTime import DateTime
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
class TestBaseRule(CacheFuTestCase):
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

        self.folder.invokeFactory(id='doc', type_name='Document')
        pcs = self.portal.portal_cache_settings
        pcs.setEnabled(True)
        headers = pcs.getHeaderSets()
        headers.invokeFactory(id='my_hs', type_name='HeaderSet')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='ContentCacheRule')
        rules.moveObjectsToTop(['my_rule'])

    def test_last_modified(self):
        pcs = self.portal.portal_cache_settings
        rule = getattr(pcs.getRules(), 'my_rule')

        # test default value
        expr = rule.getLastModifiedExpression()
        self.assertEqual(expr, 'python:object.modified()')

        # make sure getting and setting work
        rule.setLastModifiedExpression('python:3')
        self.assertEqual(rule.getLastModifiedExpression(), 'python:3')

        # test validation
        self.assertEqual(rule.validate_lastModifiedExpression(''), None)
        self.assertEqual(rule.validate_lastModifiedExpression('python:3'), None)
        self.assertNotEqual(rule.validate_lastModifiedExpression('python:foo bar'), None)
        
        doc = self.folder.doc
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', None)
        self.assertEqual(rule.getLastModified(expr_context), 3)


    def test_etag_expression(self):
        pcs = self.portal.portal_cache_settings
        rule = getattr(pcs.getRules(), 'my_rule')

        # test default value
        expr = rule.getEtagExpression()
        self.assertEqual(expr, '')

        # make sure getting and setting work
        rule.setEtagExpression('python:2')
        self.assertEqual(rule.getEtagExpression(), 'python:2')

        # test validation
        self.assertEqual(rule.validate_etagExpression('python:2'), None)
        self.assertNotEqual(rule.validate_etagExpression('python: foo bar'), None)

        doc = self.folder.doc
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', None)
        self.assertEqual(rule.getEtagExpressionValue(expr_context), 2)

    def test_headersetid_expression(self):
        pcs = self.portal.portal_cache_settings
        rule = getattr(pcs.getRules(), 'my_rule')

        # test default value
        expr = rule.getHeaderSetIdExpression()
        self.assertEqual(expr, '')

        # make sure getting and setting work
        rule.setHeaderSetIdExpression('python:2')
        self.assertEqual(rule.getHeaderSetIdExpression(), 'python:2')

        # test validation
        self.assertEqual(rule.validate_etagExpression('python:2'), None)
        self.assertNotEqual(rule.validate_etagExpression('python: foo bar'), None)

        doc = self.folder.doc
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', None)
        self.assertEqual(rule.getHeaderSetIdExpressionValue(expr_context), 2)

    def test_get_default_view(self):
        pcs = self.portal.portal_cache_settings
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = self.folder.doc
        self.assertEqual(rule.getObjectDefaultView(doc), 'document_view')

    def test_get_etag(self):
        pcs = self.portal.portal_cache_settings
        rule = getattr(pcs.getRules(), 'my_rule')
        hs = getattr(pcs.getHeaderSets(), 'my_hs')
        doc = self.folder.doc
        request = doc.REQUEST
        pcs.setGzip('accept-encoding')

        rule.setEtagComponents([])
        rule.setEtagTimeout(None)
        rule.setEtagRequestValues([])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '')

        rule.setEtagComponents(['member'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|')
        member = self.portal.portal_membership.getMemberById(self.USER1)
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, '|'+self.USER1)

        rule.setEtagComponents(['member','roles'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '||Anonymous')
        member = self.portal.portal_membership.getMemberById(self.USER1)
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, '|%s|%s' % (self.USER1, ';'.join(['Authenticated','Member'])))

        rule.setEtagComponents(['member','permissions'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '||%s|%s' % ('Anonymous', str(pcs.getPermissionCount())))
        member = self.portal.portal_membership.getMemberById(self.USER1)
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, '|%s|%s|%s' % (self.USER1, ';'.join(['Authenticated','Member']), str(pcs.getPermissionCount())))

        rule.setEtagComponents(['member','role', 'permissions'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '||%s|%s' % ('Anonymous', str(pcs.getPermissionCount())))
        member = self.portal.portal_membership.getMemberById(self.USER1)
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, '|%s|%s|%s' % (self.USER1, ';'.join(['Authenticated','Member']), str(pcs.getPermissionCount())))
        cumulative_etag = etag
        
        rule.setEtagComponents(['skin'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|'+self.portal.getCurrentSkinName())
        rule.setEtagComponents(['member','role','permissions','skin'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|' + self.portal.getCurrentSkinName())
        cumulative_etag = etag
        
        rule.setEtagComponents(['language'])
        request.set('HTTP_ACCEPT_LANGUAGE', 'en-us, en-uk')
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|en-us; en-uk')
        rule.setEtagComponents(['member','role','permissions','skin','language'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|en-us; en-uk')
        cumulative_etag = etag

        rule.setEtagComponents(['gzip'])
        request.set('HTTP_ACCEPT_ENCODING', '')
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|0')
        request.set('HTTP_ACCEPT_ENCODING', 'gzip')
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|1')
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|1')
        cumulative_etag = etag
        
        rule.setEtagComponents(['last_modified'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|'+str(doc.modified().timeTime()))
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip','last_modified'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|' + str(doc.modified().timeTime()))
        cumulative_etag = etag
        
        rule.setEtagComponents(['catalog_modified'])
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|'+str(pcs.getCatalogCount()))
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip','last_modified','catalog_modified'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|' + str(pcs.getCatalogCount()))
        cumulative_etag = etag

        rule.setEtagComponents([])
        rule.setEtagExpression('string:my, value')
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|my; value')
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip','last_modified','catalog_modified'])
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|my; value')
        cumulative_etag = etag

        rule.setEtagRequestValues([])
        rule.setEtagRequestValues(['foo','bar','foobar'])
        request.set('foo', 'FOO')
        request.set('bar', 'BAR')
        rule.setEtagComponents([])
        rule.setEtagExpression('')
        etag = rule.getEtag(request, doc, 'document_view', None)
        self.assertEqual(etag, '|FOO|BAR|')
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip','last_modified','catalog_modified'])
        rule.setEtagExpression('string:my, value')
        etag = rule.getEtag(request, doc, 'document_view', member)
        self.assertEqual(etag, cumulative_etag + '|FOO|BAR|')
        cumulative_etag = etag

        now = DateTime()
        rule.setEtagComponents([])
        rule.setEtagExpression('')
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(3600)
        etag = rule.getEtag(request, doc, 'document_view', None, time=now)
        timeout = str(int(now.timeTime()/3600))
        self.assertEqual(etag, '|'+timeout)
        rule.setEtagComponents(['member','role','permissions','skin','language','gzip','last_modified','catalog_modified'])
        rule.setEtagExpression('string:my, value')
        rule.setEtagRequestValues(['foo','bar','foobar'])
        etag = rule.getEtag(request, doc, 'document_view', member, time=now)
        self.assertEqual(etag, cumulative_etag + '|' + timeout)
        cumulative_etag = etag
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBaseRule))
    return suite

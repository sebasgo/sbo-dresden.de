##############################################################################
#
# Copyright (c) 2003-2005 struktur AG and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_tool.py 24614 2006-06-09 00:03:28Z alecm $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(os.path.dirname(sys.argv[0]), 'framework.py'))

# Load fixture
from Testing import ZopeTestCase
from base import BaseTest
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

class SquidPathTest(BaseTest):

    def afterSetUp(self):
        BaseTest.afterSetUp(self)
        self.setRoles(['Manager',])
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.qi.installProduct('CMFSquidTool')
        self.make_structure()

    def make_structure(self):
        portal = self. portal
        portal.invokeFactory('Folder', id='public_website')
        portal.public_website.invokeFactory('Folder', id='en')
        portal.public_website.en.invokeFactory('Document', id='index_html')

    def test_rewriteurl(self):
        from Products.CMFSquidTool.SquidTool import URL_REWRITE_MAP
        original= 'public_website/en'
        modified= ''
        URL_REWRITE_MAP[original] = modified

        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        ut = getToolByName(portal, 'portal_url')
        content = portal.public_website.en.index_html
        url = ut.getRelativeUrl(content)
        self.failUnless(st.rewriteUrl(url) == modified+'/index_html')

    def test_purgeurl(self):
        # SquidTool should not block purging an non existing url
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost")
        result = st.pruneUrls(ob_urls=['with_no_url'])
        # 0 if no apache is running, 400 tried to purge, but did not find url
        self.failUnless(result[0][0] in (0, 404))

    def test_getUrlsToPurge_portal_skins(self):
        # Test that the purge url for a item in portal_skins is
        # computed as both relative to the portal and not only to the
        # real location.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        ps = getToolByName(portal, 'portal_skins')
        got = st.getUrlsToPurge(ps['plone_images']['logo.jpg'])
        self.assertEquals(got, ['portal_skins/plone_images/logo.jpg', 'logo.jpg'])

    def test_getUrlsToPurge_expression(self):
        # Test that the purge url for a item in portal_skins is
        # computed as both relative to the portal and not only to the
        # real location.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.setUrlExpression("python: [object.absolute_url() + '/foo']")
        ps = getToolByName(portal, 'portal_skins')
        got = st.getUrlsToPurge(ps['plone_images']['logo.jpg'])
        self.assertEquals(
            got,
            ['http://nohost/plone/portal_skins/plone_images/logo.jpg/foo',
             'http://nohost/plone/logo.jpg/foo'])

    def test_compute_purgeurl(self):
        # If passed a complete url, computePurgeUrls should work just right.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost/foo")
        result = st.computePurgeUrls(['http://other/bar/with_url'])
        self.assertEquals(result, ['http://localhost/foo/bar/with_url'])

    def test_compute_purgeurl_repeat(self):
        # Avoid duplicating path elements in the target url.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost/foo/baz")
        result = st.computePurgeUrls(['http://other/foo/baz/bar/with_url'])
        self.assertEquals(result, ['http://localhost/foo/baz/bar/with_url'])

    def test_compute_purgeurl_not_repeat(self):
        # Don't skip if there's a prefix (we might change this in the future).
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost/fee/foo/baz")
        result = st.computePurgeUrls(['http://other/foo/baz/bar/with_url'])
        self.assertEquals(result, ['http://localhost/fee/foo/baz/foo/baz/bar/with_url'])

    def test_compute_purgeurl_with_trailing_slash(self):
        # If passed a complete url, computePurgeUrls should work just right.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost/foo")
        result = st.computePurgeUrls(['/bar/simple_path/'])
        self.assertEquals(result, ['http://localhost/foo/bar/simple_path/'])

    def test_compute_purgeurl_with_only_slash(self):
        # If passed a complete url, computePurgeUrls should work just right.
        portal = self.portal
        st = getToolByName(portal, 'portal_squid')
        st.manage_setSquidSettings(urls="http://localhost")
        result = st.computePurgeUrls(['/'])
        self.assertEquals(result, ['http://localhost/'])

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    for testClass in (
        SquidPathTest,
                      ):
        suite.addTest(unittest.makeSuite(testClass))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)

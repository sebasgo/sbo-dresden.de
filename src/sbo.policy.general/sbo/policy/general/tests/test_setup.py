import unittest
from Products.CMFCore.utils import getToolByName
from sbo.policy.tests.base import SboPolicyTestCase

class TestSetup(SboPolicyTestCase):
    def afterSetUp(self):
        self.properties = getToolByName(self.portal, "portal_properties")

    def test_portal_title(self):
        self.assertEquals("SBO-Dresden", self.portal.getProperty('title'))

    def test_portal_description(self):
        self.assertEquals("Sinfonisches Blasorchester Dresden", self.portal.getProperty('description'))
    
    def test_portal_properties(self):
       self.assertEquals(False , self.properties.site_properties.getProperty('allowAnonymousViewAbout'))
       self.assertEquals("de", self.properties.site_properties.getProperty('default_language'))
       self.assertEquals("utf-8", self.properties.site_properties.getProperty('default_charset'))
       self.assertEquals(True, self.properties.site_properties.getProperty('verify_login_name'))
       self.assertEquals(False, self.properties.site_properties.getProperty('many_users'))
       self.assertEquals(False, self.properties.site_properties.getProperty('many_groups'))
       self.assertEquals(False, self.properties.site_properties.getProperty('enable_livesearch'))
       self.assertEquals(True, self.properties.site_properties.getProperty('enable_sitemap'))
       self.assertEquals(True, self.properties.site_properties.getProperty('enable_link_integrity_checks'))
       self.assertEquals('false', self.properties.site_properties.getProperty('external_links_open_new_window'))
       self.assertEquals("authenticated", self.properties.site_properties.getProperty('icon_visibility'))
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite




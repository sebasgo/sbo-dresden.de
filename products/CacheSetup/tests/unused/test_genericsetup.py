#
# Exportimport adapter tests
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import \
    BodyAdapterTestCase
from Products.CMFPlone.FactoryTool import FactoryTool
from OFS.Folder import Folder
from Products.ATContentTypes.content.folder import ATFolder
from Products.CacheSetup.interfaces import ICacheTool
from zope.interface import implements
from Products.CacheSetup.content.cache_tool import CacheTool
from Products.PageCacheManager.PageCacheManager import\
    PageCacheManager
try:
    from Products.CMFCore.interfaces._tools import ITypesTool
except ImportError:
    ITypesTool = None

_CACHESETTINGS_XML = """\
<?xml version="1.0"?>
<cachesettings title="Cache Configuration Tool"
   contentid="portal_cache_settings" portaltype="CacheTool">
 <field name="cacheConfig" value="zserver"/>
 <field name="domains"/>
 <field name="squidURLs" value=""/>
 <field name="gzip" value="accept-encoding"/>
 <field name="varyHeader" value="Accept-Encoding, Accept-Language"/>
 <pagecachesetting name="threshold" value="500"/>
 <pagecachesetting name="cleanup_interval" value="60"/>
 <pagecachesetting name="max_age" value="3600"/>
 <pagecachesetting name="active" value="on_always"/>
</cachesettings>
"""

class DummyCacheTool(CacheTool):
    #schema = ()
    def Title(self):
        return 'Cache Configuration Tool'
    
    
class DummyPortalTypesTool(Folder):
    id = 'portal_types'
    if ITypesTool:
        implements(ITypesTool)
    
    def listContentTypes(self):
        return ('Folder', 'Document')


class DummyPortalSquidTool(Folder):
    def manage_setSquidSettings(self, list):
        pass


class DummyPageCacheManager(PageCacheManager):
    pass


class DummyPortalMembershipTool(Folder):
    pass


class PortalFactoryXMLAdapterTests(BodyAdapterTestCase):
    """The actual test methods are defined in our parent class.
    We just have to set everything up.
    """

    def _getTargetClass(self):
        from Products.CacheSetup.exportimport.cachefu \
                    import CacheSettingsAdapter
        return CacheSettingsAdapter

    def _populate(self, obj):
        # For better tests, a RuleFolder should be added to test that
        # part of the migration. Also modify the xml at the top of
        # this testingfile if you do so, of course.
        pass

    def _verifyImport(self, obj):
        """After applying the import step, this method is run.
        """

        cache_tool = self.site.portal_cache_settings
        page_cache = self.site.CacheSetup_PageCache
        self.assertEquals(cache_tool.getCacheConfig(),
                          "zserver")
        self.assertEquals(page_cache._settings['threshold'],
                          500)


    def setUp(self):
        self.site = Folder('site')
        self.site.portal_cache_settings = DummyCacheTool(
            'portal_cache_settings')
        self.site.portal_types = DummyPortalTypesTool()
        self.site.portal_membership = DummyPortalMembershipTool()
        self.site.portal_squid = DummyPortalSquidTool()
        self.site.CacheSetup_PageCache = DummyPageCacheManager(
            'CacheSetup_PageCache')
        self._obj = self.site.portal_cache_settings
        self._BODY = _CACHESETTINGS_XML


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PortalFactoryXMLAdapterTests))
    return suite

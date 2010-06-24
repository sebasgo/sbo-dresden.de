from StringIO import StringIO

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName

from Products.CacheSetup import config
from Products.CacheSetup.Extensions import utils
from Products.CacheSetup.Extensions import policy_utils
from Products.CacheSetup.enabler import enableCacheFu


def install(self, reinstall=False):
    out = StringIO()

    utils.installDependencies(self, out)

    installTypes(self, out, listTypes(config.PROJECT_NAME), config.PROJECT_NAME, refresh_references=0)
    install_subskin(self, out, config.GLOBALS)

    utils.setupWorkflows(self, out)
    utils.setupCacheTool(self, out)
    utils.setupSquidTool(self, out)
    utils.setupPortalFactory(self, out)
    utils.setupFolderViews(self, out)
    utils.setupSiteProperties(self, out)
    utils.setupConfiglet(self, out)

    # clean up old cache policy.
    if reinstall:
        policy_utils.updateOldCachePolicy(self, out)

    # add new cache policies
    policy_utils.addCachePolicies(self, out)

    # Re-enable CacheFu if previously enabled
    cache_tool = getToolByName(self, config.CACHE_TOOL_ID)
    if cache_tool.getEnabled():
        enableCacheFu(self, True)

    out.write("Successfully installed %s." % config.PROJECT_NAME)
    return out.getvalue()

def uninstall(self, reinstall=False):
    out = StringIO()

    utils.restorePortalFactory(self, out)
    utils.restoreSquidTool(self, out)
    utils.restoreFolderViews(self, out)
    utils.restoreSiteProperties(self, out)
    utils.removeConfiglet(self, out)

    # Remove the old cached_macros folder left by version 1.0x
    # We also manually uncatalog it and any children since it's probably broken now
    cache_tool = getToolByName(self, config.CACHE_TOOL_ID)
    if getattr(cache_tool, 'cached_macros', None) is not None:
        print >> out, 'Removed and uncataloged cache_macros folder left by previous version.'
        catalog = getToolByName(self, 'portal_catalog', None)
        results = catalog.searchResults(Type=['Macro Folder','MacroCacheRule'])
        for result in results:
            catalog.uncatalog_object(result.getPath())
        cache_tool.manage_delObjects('cached_macros')

    # Disabling Cachefu will remove PageCacheManager & PolicyHTTPCaches
    # and restore old CachingPolicyManager and ResourceRegistry settings
    # We bypass 'setEnabled' here to retain setting in case of reinstall
    if config.PAGE_CACHE_MANAGER_ID in self.objectIds():
        enableCacheFu(self, False)

    # uninstall/reinstall the CMFSquidTool product also
    qi = getToolByName(self, 'portal_quickinstaller')
    if reinstall:
        qi.reinstallProducts(['CMFSquidTool'])
    else:
        qi.uninstallProducts(['CMFSquidTool'])

    return out.getvalue()

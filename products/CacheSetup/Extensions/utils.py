from Products.Archetypes.public import listTypes
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup import config

try:
    from Products.CMFSquidTool import SquidTool
except ImportError:
    SquidTool = None


def setupConfiglet(portal, out):
    # see if there's already a cache configlet and try to
    # delete it
    
    portalConf = None
    try:
        portalConf = getToolByName(portal, 'portal_controlpanel')
    except AttributeError:
        print >>out, "Configlet could not be installed"
        return
    
    portalConf.unregisterConfiglet(config.CONFIGLET_ID)

    try:
        portalConf.registerConfiglet(
            config.CONFIGLET_ID,
            config.TOOL_TITLE,
            'string:${portal_url}/%s' % config.CACHE_TOOL_ID,
            '',                 # a condition
            'Manage portal',    # access permission
            'Products',         # section to which the configlet should be added:
                                #(Plone,Products,Members)
            1,                  # visibility
            config.PROJECT_NAME,
            '/misc_/CacheSetup/cachesetup_tool_icon.gif', # icon in control_panel
            config.TOOL_TITLE,
            None
        )
    except KeyError:
        pass # Get KeyError when registering duplicate configlet.

def removeConfiglet(portal, out):
    # remove configlet from portal_controlpanel
    pcp = getToolByName(portal,'portal_controlpanel')
    pcp.unregisterConfiglet(config.CONFIGLET_ID)

def installDependencies(portal, out):
    if SquidTool is None:
        raise ValueError, 'Please add CMFSquidTool to your Products directory'
    qi = getToolByName(portal,'portal_quickinstaller')
    if not 'portal_squid' in portal.objectIds():
        qi.installProduct('CMFSquidTool', locked=True)
        print >> out, 'Installed CMFSquidTool'
    else:
        qi.notifyInstalled('CMFSquidTool', locked=True)
        print >> out, 'Lock CMFSquidTool'

def setupWorkflows(portal, out):
    """Setup workflow 
    """
    wftool = getToolByName(portal, 'portal_workflow')
    typeInfo = listTypes(config.PROJECT_NAME)
    for t in typeInfo:
        portal_type = t['portal_type']
        #if portal_type in ['HeaderSet']:
        #    wftool.setChainForPortalTypes((portal_type,), '')
        wftool.setChainForPortalTypes((portal_type,), '')

def setupCacheTool(portal, out):
    cache_tool = getToolByName(portal, config.CACHE_TOOL_ID, None)
    if cache_tool is None:
        ps = portal.portal_types.getTypeInfo('Plone Site')
        allowed_types = ps.getProperty('allowed_content_types')
        ps._updateProperty('allowed_content_types', tuple(list(allowed_types)+['CacheTool']))

        portal.invokeFactory(id=config.CACHE_TOOL_ID, type_name='CacheTool')
        cache_tool = getToolByName(portal, config.CACHE_TOOL_ID)
        cache_tool.setTitle(config.TOOL_TITLE)
        cache_tool.reindexObject()
        ps._updateProperty('allowed_content_types', allowed_types)
        print >> out, 'Added %s' % config.CACHE_TOOL_ID
    cache_tool.unindexObject()

def setupFolderViews(portal, out):
    props_tool = getToolByName(portal, 'portal_properties')
    site_props = getattr(props_tool, 'site_properties')
    typesUseViewActionInListings = list(site_props.getProperty('typesUseViewActionInListings'))
    for portal_type in config.FOLDER_TYPES:
        if portal_type not in typesUseViewActionInListings:
            typesUseViewActionInListings.append(portal_type)
    site_props.manage_changeProperties(typesUseViewActionInListings = typesUseViewActionInListings)

def restoreFolderViews(portal, out):
    props_tool = getToolByName(portal, 'portal_properties')
    site_props = getattr(props_tool, 'site_properties')
    typesUseViewActionInListings = list(site_props.getProperty('typesUseViewActionInListings'))
    for portal_type in config.FOLDER_TYPES:
        if portal_type in typesUseViewActionInListings:
            typesUseViewActionInListings.remove(portal_type)
    site_props.manage_changeProperties(typesUseViewActionInListings = typesUseViewActionInListings)

def setupSiteProperties(portal, out):
    props_tool = getToolByName(portal, 'portal_properties')
    site_props = getattr(props_tool, 'site_properties')
    navtree_props = getattr(props_tool, 'navtree_properties')
    try:
        types_not_searched = list(site_props.types_not_searched)
    except AttributeError:
        types_not_searched = []
    for t in config.TYPES:
        if not t in types_not_searched:
            types_not_searched.append(t)
    use_folder_tabs = list(site_props.use_folder_tabs)
    if config.TOOL_TYPE in use_folder_tabs:
        use_folder_tabs.remove(config.TOOL_TYPE)
    site_props.manage_changeProperties(types_not_searched=tuple(types_not_searched),
                                       use_folder_tabs=tuple(use_folder_tabs))
    metaTypesNotToList = list(navtree_props.metaTypesNotToList)
    if not config.TOOL_TYPE in metaTypesNotToList:
        metaTypesNotToList.append(config.TOOL_TYPE)
    navtree_props.manage_changeProperties(metaTypesNotToList=tuple(metaTypesNotToList))

def restoreSiteProperties(portal, out):
    props_tool = getToolByName(portal, 'portal_properties')
    site_props = getattr(props_tool, 'site_properties')
    navtree_props = getattr(props_tool, 'navtree_properties')
    try:
        types_not_searched = list(site_props.types_not_searched)
    except AttributeError:
        types_not_searched = []
    for t in config.TYPES:
        if t in types_not_searched:
            types_not_searched.remove(t)
    site_props.manage_changeProperties(types_not_searched=tuple(types_not_searched))
    metaTypesNotToList = list(navtree_props.metaTypesNotToList)
    if config.TOOL_TYPE in metaTypesNotToList:
        metaTypesNotToList.remove(config.TOOL_TYPE)
    navtree_props.manage_changeProperties(metaTypesNotToList=tuple(metaTypesNotToList))

def setupSquidTool(portal, out):
    squid_tool = getToolByName(portal, 'portal_squid', None)
    squid_tool.setUrlExpression('python:object.%s.getUrlsToPurge(object)' % config.CACHE_TOOL_ID)

def restoreSquidTool(portal, out):
    # get rid of the url expression in portal_squid
    squid_tool = getToolByName(portal, 'portal_squid', None)
    if squid_tool:
        squid_tool.setUrlExpression('')
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    qi.notifyInstalled('CMFSquidTool', locked=False)

def setupPortalFactory(portal, out):
    factory = getToolByName(portal, 'portal_factory', None)
    if factory is not None:
        types = factory.getFactoryTypes().keys()
        for metaType in config.TYPES:
            if metaType not in types:
                types.append(metaType)
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
        print >> out, 'Added content types to portal_factory.'
        
def restorePortalFactory(portal, out):
    factory = getToolByName(portal, 'portal_factory', None)
    if factory is not None:
        types = factory.getFactoryTypes().keys()
        for metaType in config.TYPES:
            if metaType in types:
                types.remove(metaType)
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
        print >> out, 'Removed content types from portal_factory.'


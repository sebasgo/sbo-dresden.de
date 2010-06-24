# Make sure Install imports.
from Products.CacheSetup.Extensions import Install as _Install
del _Install

from AccessControl import allow_module
from Products.Archetypes import public as atapi
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
from content import *
from content.cache_tool import CacheTool
from content.caching_policy_manager import CSCachingPolicyManager
from permissions import initialize as initialize_permissions
import config

registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):
    """Product Initialization
    """
    import patch, patch_cmf, patch_five
    patch.run()
    patch_cmf.run()
    patch_five.run()

    tools = (CacheTool, CSCachingPolicyManager)

    try:
        cmfutils.ToolInit(
        config.PROJECT_NAME + ' Tool',
        tools = tools,
        icon = 'cachesetup_tool_icon.gif',
        ).initialize(context)
    except TypeError:
        cmfutils.ToolInit(
        config.PROJECT_NAME + ' Tool',
        tools = tools,
        product_name = config.PROJECT_NAME,
        icon = 'cachesetup_tool_icon.gif',
        ).initialize(context)

    allow_module('Products.CacheSetup.config')

    # Ask Archetypes to handback all the type information needed
    # to make the CMF happy.
    types = atapi.listTypes(config.PROJECT_NAME)
    content_types, constructors, ftis = \
        atapi.process_types(types, config.PROJECT_NAME)
    permissions = initialize_permissions()

    # We want to register each each type with its own permission,
    # this will afford us greater control during system
    # configuration/deployment (and is a good recipe)
    # The pattern used here will create many item options in ZMI
    # menus, but is the only way that allows for things to still be
    # selectable in the UI. If they all had the same name, only the
    # first would be found.
    permissions = initialize_permissions()
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECT_NAME, atype.archetype_name)
        cmfutils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)
    
    # GS Profiles are broken right now
    # We'll fix them in the next release
    # 
    #profile_registry.registerProfile(
    #    name='default',
    #    title='CacheFu',
    #    description='Extension profile for CacheFu',
    #    path='profiles/default',
    #    product='CacheSetup',
    #    profile_type=EXTENSION,
    #    for_=IPloneSiteRoot)


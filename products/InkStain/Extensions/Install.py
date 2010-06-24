# -*- coding: utf-8 -*-

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes
# from Products.CMFDynamicViewFTI.migrate import migrateFTIs

from Products.InkStain.config import *


def registerResources(self, out, toolname, resources):
    tool = getToolByName(self, toolname)
    existing = tool.getResourceIds()
    cook = False
    for resource in resources:
        if not resource['id'] in existing:
            # register additional resource in the specified registry...
            if toolname == "portal_css":
                tool.registerStylesheet(**resource)
            if toolname == "portal_javascripts":
                tool.registerScript(**resource)
            print >> out, "Added %s to %s." % (resource['id'], tool)
        else:
            # ...or update existing one
            parameters = tool.getResource(resource['id'])._data
            for key in [k for k in resource.keys() if k != 'id']:
                originalkey = 'original_'+key
                original = parameters.get(originalkey)
                if not original:
                    parameters[originalkey] = parameters[key]
                parameters[key] = resource[key]
                print >> out, "Updated %s in %s." % (resource['id'], tool)
                cook = True
    if cook:
        tool.cookResources()
    print >> out, "Successfuly Installed/Updated resources in %s." % tool


def resetResources(self, out, toolname, resources):
    # Revert resource customizations
    tool = getToolByName(self, toolname)
    for resource in [tool.getResource(r['id']) for r in resources]:
        if hasattr(resource, '_data'):
            for key in resource._data.keys():
                originalkey = 'original_' + key
                if resource._data.has_key(originalkey):
                    try: # <- BBB
                        resource._data[key] = resource._data[originalkey]['value']
                    except TypeError:
                        resource._data[key] = resource._data[originalkey]
                    del resource._data[originalkey]
                

def install(self):
    """
    Installs InkStain
    """
    out = StringIO()

    print >> out, "Installation - InkStain Guestbook"

    # Install types
    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)

    # Install skin
    install_subskin(self, out, product_globals)

    # Now we add the styles
    registerResources(self, out, 'portal_css', STYLESHEETS)

    # Migrate FTI
#    migrated = migrateFTIs(self, product=PROJECTNAME)

    print >> out, "InkStain Guestbook installed with success"

    return out.getvalue()


def uninstall(self):
    """
    Uninstalls InkStain
    """
    out = StringIO()
    resetResources(self, out, 'portal_css', STYLESHEETS)
    return out.getvalue()

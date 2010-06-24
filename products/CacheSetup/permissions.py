from Products.Archetypes import public as atapi
try:
    from Products.CMFCore import permissions as cmfcore_permissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions as cmfcore_permissions
import config

# Roles

# Permissions

# This file is used to set up permissions for your product.
 
# The code below will create a unique add permission for each of your
# content types.  The permission for adding the type MyContentType will
# be 'MyProject: Add MyContentType'.  If instead you want to specify
# your own add permission (e.g. use the CMF's 'Add portal content'
# permission), you can use the ADD_PERMISSIONS dictionary to do so.

# ADD_PERMISSIONS is used to specify the name of the permission
# used for adding one of your content types.  For example:
#
# ADD_PERMISSIONS = {'MyFirstContentType': 'Add portal content',
#                    'MySecondContentType': 'My other permission',
#                   }

ADD_PERMISSIONS = {}

# The SITEWIDE_PERMISSIONS dictionary is used for assigning permissions
# to different roles site-wide.  For example, if you create the new roles
# 'Czar' and 'Peasant', you could give them the 'Add portal folders' and
# 'Delete objects' permissions like so:
#
# SITEWIDE_PERMISSIONS = (
#    (['Czar', 'Peasant'], ['Add portal folders', 'Delete objects'']),
#   )
#
# In general, the pattern is
#
# SITEWIDE_PERMISSIONS = ( 
#   ([list of roles], [list of permissions]),
#   ([second list of roles], [second list of permissions]),
#  )
#
# The site-wide permissions are set in Extensions/Install.py

SITEWIDE_PERMISSIONS = ()

def initialize():
    permissions = {}
    types = atapi.listTypes(config.PROJECT_NAME)
    for atype in types:
        portal_type = atype['portal_type']
        permission = ADD_PERMISSIONS.get(portal_type, None)
        if permission is None:
            # construct a permission on the fly
            permission = "%s: Add %s" % (config.PROJECT_NAME,
                                         portal_type)
            cmfcore_permissions.setDefaultRoles(permission, ('Manager',))
        permissions[portal_type] = permission

    return permissions

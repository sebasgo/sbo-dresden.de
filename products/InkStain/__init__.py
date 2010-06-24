# -*- coding: utf-8 -*-

# General configuration
from Products.CMFCore         import utils
from Products.InkStain.config import *
from AccessControl import ModuleSecurityInfo

# Register skin directories so they can be added to portal_skins
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory('skins', product_globals)

# Initialize the product
from Products.Archetypes import listTypes, process_types

def initialize(context):
    """
    Init my product : InkStain
    """
    import security as perms
    from content import *

    # initialize the content, including types and add permissions
    listOfTypes = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = getattr(perms, 'Add%s' % atype.meta_type),
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

from zope.i18nmessageid import MessageFactory
InkStainMessageFactory = MessageFactory('inkstain')
ModuleSecurityInfo('Products.InkStain').declarePublic('InkStainMessageFactory')

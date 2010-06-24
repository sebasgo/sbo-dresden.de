try:
    import zope.annotation
except ImportError:
    # for zope-2.9
    import zope.app.annotation
    import zope.app.annotation.interfaces
    import sys
    sys.modules['zope.annotation'] = zope.app.annotation
    sys.modules['zope.annotation.interfaces'] = zope.app.annotation.interfaces

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

from Products.CMFCore.DirectoryView import registerDirectory
import Products.CMFPlone.interfaces

from Products.Archetypes.atapi import listTypes, process_types

GLOBALS = globals()

from config import DEFAULT_ADD_CONTENT_PERMISSION, PROJECTNAME

# Make the skins available as DirectoryViews                                                        
registerDirectory('skins', GLOBALS)

def initialize(context):
    from Products.Collage import content
    from Products.CMFCore import utils as cmfutils
    from Products.Archetypes import atapi

    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    cmfutils.ContentInit('%s Content' % PROJECTNAME,
                         content_types = content_types,
                         permission = DEFAULT_ADD_CONTENT_PERMISSION,
                         extra_constructors = constructors,
                         fti = ftis,
                         ).initialize(context)
    
    profile_registry.registerProfile(
        name='default',
        title='Collage',
        description='Profile for Collage',
        path='profiles/default',
        product=PROJECTNAME,
        profile_type=EXTENSION,
        for_=Products.CMFPlone.interfaces.IPloneSiteRoot)
    

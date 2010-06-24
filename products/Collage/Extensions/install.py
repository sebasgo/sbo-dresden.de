from StringIO import StringIO
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import getToolByName
from Products import Collage
from Products.Collage.config import PROJECTNAME

def setup_gs_profile(self, portal, out):
    setup_tool = cmfutils.getToolByName(portal, 'portal_setup', None)

    try:
        setup_tool.runAllImportStepsFromProfile('profile-Collage:default')
    except AttributeError:
        # BBB for GenericSetup 1.2
        context = setup_tool._getImportContext('profile-Collage:default')
        setup_tool._runImportStepsFromContext(context)

def install(self):
    out = StringIO()
    portal = getToolByName(self,'portal_url').getPortalObject()

    setup_gs_profile(self, portal, out)

    out.write("Successfully installed %s.\n\n" % PROJECTNAME)
    return out.getvalue()

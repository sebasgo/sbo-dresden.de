from Products.CMFCore.utils import getToolByName
from sbo.frontpage.migration import migrate_frontpage


def install_profile(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-sbo.frontpage:default',
                                       purge_old=False)


def remove_old_type(context):
    portal_types = getToolByName(context, 'portal_types')
    portal_types.manage_delObjects(["Frontpage"])


def migrate_to_dexterity(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    migrate_frontpage(portal)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('sbo.frontpage_various.txt') is None:
        return

    # Add additional setup code here


from Products.CMFCore.utils import getToolByName


def install_profile(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-sbo.policy.general:default',
                                       purge_old=False)


def migrate_content_to_dx(context):
    plone_url = getToolByName(context, 'portal_url')
    portal = plone_url.getPortalObject()
    migrator = portal.restrictedTraverse('@@migrate_from_atct')
    migrator(migrate=True)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('sbo.theme_various.txt') is None:
        return

    # Add additional setup code here


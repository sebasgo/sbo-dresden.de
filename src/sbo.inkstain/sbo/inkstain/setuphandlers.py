from Products.CMFCore.utils import getToolByName


def install_profile(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-sbo.inkstain:default',
                                       purge_old=False)

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('sbo.inkstain_various.txt') is None:
        return

    # Add additional setup code here


from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_sbo_policy():
    """Set up the additional products required for SBO site policy.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the sbo.policy package.

    fiveconfigure.debug_mode = True
    import sbo.policy
    zcml.load_config('configure.zcml', sbo.policy)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('sbo.policy')

# The oder here is imortant: We first call the (deferred) function
# which installs the products we need for the SBO package. Then,
# we let PloneTestCase se up this product on installation.

setup_sbo_policy()
ptc.setupPloneSite(products=['sbo.policy'])

class SboPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. if necessary,
    we can put common utility or setup code in here.
    """


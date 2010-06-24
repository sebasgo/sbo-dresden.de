from Products.CacheSetup.config import PROJECT_NAME
from Testing import ZopeTestCase

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct(PROJECT_NAME)

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
#ZopeTestCase.installProduct('PageCacheManager')
ZopeTestCase.installProduct('CMFSquidTool')
#ZopeTestCase.installProduct('PythonScripts')
#ZopeTestCase.installProduct(PROJECT_NAME)

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site
setupPloneSite(products=[PROJECT_NAME])

class CacheFuTestCase(PloneTestCase):
    """Base class for integration tests for the 'CacheSetup' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
class CacheFuFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'CacheSetup' product. 
    This may provide specific set-up and tear-down operations, or provide 
    convenience methods.
    """

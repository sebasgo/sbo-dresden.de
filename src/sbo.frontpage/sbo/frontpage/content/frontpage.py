"""Definition of the Frontpage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from sbo.frontpage.interfaces import IFrontpage
from sbo.frontpage.config import PROJECTNAME

FrontpageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

FrontpageSchema['title'].storage = atapi.AnnotationStorage()
FrontpageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FrontpageSchema, moveDiscussion=False)


class Frontpage(base.ATCTContent):
    """A front page displaying latest news and upcoming concerts."""
    implements(IFrontpage)

    meta_type = "Frontpage"
    schema = FrontpageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Frontpage, PROJECTNAME)

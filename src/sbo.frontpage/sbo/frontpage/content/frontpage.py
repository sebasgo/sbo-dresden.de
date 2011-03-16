"""Definition of the Frontpage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from sbo.frontpage import FrontpageMessageFactory as _

from sbo.frontpage.interfaces import IFrontpage
from sbo.frontpage.config import PROJECTNAME

FrontpageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.ReferenceField(
        "coverImage",
        required=True,
        relationship="isCoverImage",
        allowed_types=('Image',),
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        widget=ReferenceBrowserWidget(
            label=_(u"Cover image"),
            description=_(u"The image displayed initially on the front page.")
        )
    ),

    atapi.ReferenceField(
        "newsFolder",
        required=True,
        relationship="isNewsFolder",
        allowed_types=('Folder',),
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        widget=ReferenceBrowserWidget(
            label=_(u"News folder"),
            description=_(
                u"The folder containing the news items of the website."
            )
        )
    ),

    atapi.ReferenceField(
        "concertsFolder",
        required=True,
        relationship="isConcertsFolder",
        allowed_types=('Folder',),
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        widget=ReferenceBrowserWidget(
            label=_(u"Concerts folder"),
            description=_(u"The folder containing the concerts of the website.")
        )
    )
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
    cover_image = atapi.ATReferenceFieldProperty('coverImage')
    news_folder = atapi.ATReferenceFieldProperty('newsFolder')
    concerts_folder = atapi.ATReferenceFieldProperty('concertsFolder')

atapi.registerType(Frontpage, PROJECTNAME)

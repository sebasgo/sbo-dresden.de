from zope.interface import Interface
from zope import schema
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.ATContentTypes.interfaces.image import IImageContent
from sbo.frontpage import FrontpageMessageFactory as _


class IFrontpage(Interface):
    """A front page displaying latest news and upcoming concerts."""

    cover_image = schema.Object(
        title=_(u"Cover image"),
        description=_(u"The image displayed initially on the front page"),
        schema=IImageContent,
        required=True
    )
    
    news_folder = schema.Object(
        title=_(u"News folder"),
        description=_(u"The folder containing the news items of the website"),
        schema=IBaseFolder,
        required=True
    )
    
    concerts_folder = schema.Object(
        title=_(u"Concerts folder"),
        description=_(u"The folder containing the concerts of the website"),
        schema=IBaseFolder,
        required=True
    )

from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from sbo.frontpage import FrontpageMessageFactory as _
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList


class IFrontpage(model.Schema):
    """A front page displaying latest news and upcoming concerts."""

    cover_images = RelationList(
        title=_(u"Cover images"),
        description=_(u"The images displayed initially on the front page."),
        value_type=RelationChoice(title=_(u"Cover image"),
                                  source=ObjPathSourceBinder(portal_type='Image')),
        required=True
    )
    
    news_folder = RelationChoice(
        title=_(u"News folder"),
        description=_(u"The folder containing the news items of the website."),
        source=ObjPathSourceBinder(portal_type='Folder'),
        required=True
    )
    
    concerts_folder = RelationChoice(
        title=_(u"Concerts folder"),
        description=_(u"The folder containing the concerts of the website."),
        source=ObjPathSourceBinder(portal_type='Folder'),
        required=True
    )

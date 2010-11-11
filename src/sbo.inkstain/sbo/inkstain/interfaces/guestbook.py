from zope.interface import Interface
from zope import schema
from sbo.inkstain import InkstainMessageFactory as _



class IGuestbook(Interface):
    """A simple guestbook"""

    entries_per_page = schema.Int(
        title=_(u"Entries per page"),
        description=_(u"Set the number of entries which are shown on one page."),
        required=True
    )

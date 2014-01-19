from zope.interface import implements
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.CMFPlone.interfaces import INonStructuralFolder
from sbo.inkstain import InkstainMessageFactory as _
from sbo.inkstain.interfaces import IGuestbook

class GuestbookEntry(SimpleItem):
    date=None
    name=None
    email_address=None
    homepage_address=None
    message=None

    def __repr__(self):
        return "<GuestbookEntry %r,%r,%r,%r,%r>" % (
            self.date,
            self.name,
            self.email_address,
            self.homepage_address,
            self.message,
        )

class Guestbook(base.ATCTFolder):
    """A simple guestbook"""
    implements(IGuestbook, INonStructuralFolder)

    meta_type = "Guestbook"

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    entries_per_page = atapi.ATFieldProperty('entries_per_page')

    def addEntry(self, entry):
        self._setObject(entry.getId(), entry)


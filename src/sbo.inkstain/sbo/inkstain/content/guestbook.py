"""Definition of the Guestbook content type
"""

from zope.interface import implements
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFPlone.interfaces import INonStructuralFolder
from sbo.inkstain import InkstainMessageFactory as _
from sbo.inkstain.interfaces import IGuestbook
from sbo.inkstain.config import PROJECTNAME

GuestbookSchema = base.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.IntegerField(
        name='entries_per_page',
        required=True,
        searchable=False,
        default=15,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Entries per page"),
            description=_(u"Sets the number of entries which are shown on one page."),
        ),
    ),

))


# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

GuestbookSchema['title'].storage = atapi.AnnotationStorage()
GuestbookSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    GuestbookSchema,
    moveDiscussion=False,
    folderish=False
)

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
    schema = GuestbookSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    entries_per_page = atapi.ATFieldProperty('entries_per_page')

    def addEntry(self, entry):
        self._setObject(entry.getId(), entry)

atapi.registerType(Guestbook, PROJECTNAME)


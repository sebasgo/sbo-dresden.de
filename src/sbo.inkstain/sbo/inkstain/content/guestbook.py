"""Definition of the Guestbook content type
"""

from zope.interface import implements

from OFS.SimpleItem import SimpleItem
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata


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
            label=u"Entries per page",
            label_msgid="label_entries_per_page",
            description=u"Set the number of entries which are shown on one page.",
            i18n_domain='sbo.inkstain'
        ),
    ),

))


# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

GuestbookSchema['title'].storage = atapi.AnnotationStorage()
GuestbookSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    GuestbookSchema,
    moveDiscussion=False
)

class GuestbookEntry(SimpleItem):
    name=None
    email=None
    date=None
    homepage=None
    post=None

class Guestbook(base.ATCTContent):
    """A simple guestbook"""
    implements(IGuestbook)

    meta_type = "Guestbook"
    schema = GuestbookSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    entries_per_page = atapi.ATFieldProperty('entries_per_page')

atapi.registerType(Guestbook, PROJECTNAME)


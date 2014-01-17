from plone.app.content.interfaces import INameFromTitle
from zope.component import adapts
from zope.interface import implements

from sbo.inkstain.interfaces import IGuestbookEntry

class GuestbookEntryTitleAdapter(object):
    implements(INameFromTitle)
    adapts(IGuestbookEntry)
    def __init__(self, context):
        self.context = context
    @property
    def title(self):
        return self.context.entry_date.strftime(u"%Y-%m-%d %H-%M-%S")

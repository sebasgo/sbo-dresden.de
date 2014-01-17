from zope.security import checkPermission

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from sbo.inkstain import InkstainMessageFactory as _


class GuestbookEntryView(BrowserView):
    template = ViewPageTemplateFile('guestbookentry.pt')

    def __call__(self):
        return self.template()

    def canReviewGuestbook(self):
        return checkPermission("sbo.inkstain.ReviewGuestbook", self.context)

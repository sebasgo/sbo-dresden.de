from Acquisition import aq_inner
from zope.security import checkPermission

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize.view import memoize

from sbo.inkstain.browser.writeentry import InlineWriteEntryForm
from sbo.inkstain import InkstainMessageFactory as _


class GuestbookView(BrowserView):
    template = ViewPageTemplateFile('guestbook.pt')

    def __call__(self):
        postback = True
        form = self.request.form

        deleteButton = form.get('form.button.Delete', False)

        if form.get('form.button.Delete', False):
            context = aq_inner(self.context)
            deleteIds = form.get('messages', [])
            context.manage_delObjects(ids = deleteIds)
            confirm = _(u"The marked entries have been deleted.")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')
            postback = False

        if postback:
            return self.template()
        else:
            self.request.response.redirect(self.context.absolute_url())
            return ''

    def createWriteEntryForm(self):
        context = aq_inner(self.context)
        view = InlineWriteEntryForm(context, self.request)
        view = view.__of__(context) 
        return view();

    @memoize
    def entries(self):
        context = aq_inner(self.context)
        entries = context.objectValues()
        entries.sort(key=lambda entry: entry.date, reverse=True)
        return entries

    def canAddGuestbookEntries(self):
        return checkPermission("sbo.inkstain.AddGuestbookEntry", self.context)

    def canReviewGuestbook(self):
        return checkPermission("sbo.inkstain.ReviewGuestbook", self.context)



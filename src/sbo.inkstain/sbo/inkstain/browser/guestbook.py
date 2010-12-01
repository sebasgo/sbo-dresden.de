from Acquisition import aq_inner
from zope.security import checkPermission

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from sbo.inkstain.browser.writeentry import InlineWriteEntryForm
from sbo.inkstain import InkstainMessageFactory as _


class GuestbookView(BrowserView):
    template = ViewPageTemplateFile('guestbook.pt')

    def __call__(self):
        postback = True
        form = self.request.form

        deleteButton = form.get('form.button.Delete', False)

        if form.get('form.button.Delete', False):
            deleteIds = form.get('messages', [])
            for deleteId in deleteIds:
                for index, entry in enumerate(self.context.entries):
                    if entry.getId() == deleteId:
                        del(self.context.entries[index])
                        break
            confirm = _(u"Marked messages have been deleted.")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')
            postback = False

        if postback:
            return self.template()
        else:
            self.request.response.redirect(self.context.absolute_url())
            return ''

    def createWriteEntryForm(self):
        context = self.context.aq_inner
        view = InlineWriteEntryForm(context, self.request)
        view = view.__of__(context) 
        return view();

    def entries(self):
        context = aq_inner(self.context)
        return context.entries[::-1]

    def canAddGuestbookEntries(self):
        return checkPermission("sbo.inkstain.AddGuestbookEntry", self.context)

    def canReviewGuestbook(self):
        return checkPermission("sbo.inkstain.ReviewGuestbook", self.context)



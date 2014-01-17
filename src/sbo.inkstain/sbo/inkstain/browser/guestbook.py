from Acquisition import aq_inner
from zope.security import checkPermission

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from sbo.inkstain.browser.writeentry import InlineWriteEntryForm
from sbo.inkstain import InkstainMessageFactory as _


class GuestbookView(BrowserView):
    template = ViewPageTemplateFile('guestbook.pt')

    def __call__(self):
        context = aq_inner(self.context)
        postback = True
        form = self.request.form
        message_ids = form.get('messages', [])

        if form.get('form.button.Delete', False):
            context.manage_delObjects(ids=message_ids)
            confirm = _(u"The marked entries have been deleted.")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')
            postback = False

        if form.get('form.button.Publish', False):
            for id in message_ids:
                if context.hasObject(id):
                    message = context[id]
                    message.moderation_state = 'published'
            postback = False

        if form.get('form.button.Spam', False):
            for id in message_ids:
                if context.hasObject(id):
                    message = context[id]
                    message.moderation_state = 'spam'
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

    def entries(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if self.canReviewGuestbook():
            results = catalog(
                portal_type='sbo.inkstain.guestbookentry',
                path={'query': '/'.join(context.getPhysicalPath()), 'level': -1},
                sort_on='entry_date',
                sort_order='descending'
            )
        else:
            results = catalog(
                portal_type='sbo.inkstain.guestbookentry',
                path={'query': '/'.join(context.getPhysicalPath()), 'level': -1},
                moderation_state='published',
                sort_on='entry_date',
                sort_order='descending'
            )
        return results

    def canAddGuestbookEntries(self):
        return checkPermission("sbo.inkstain.AddGuestbookEntry", self.context)

    def canReviewGuestbook(self):
        return checkPermission("sbo.inkstain.ReviewGuestbook", self.context)



import imp
import sys

from Acquisition import aq_inner
from zope.security import checkPermission

from plone.dexterity.utils import createContentInContainer
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

class GuestbookMigrationView(BrowserView):
    def __call__(self):
        #from Products.ATContentTypes.content.base import ATCTFolder

        #self.stub("sbo.inkstain.content.guestbook.Guestbook", "Guestbook", ATCTFolder)

        old_path = self.request.form.get('old', "")
        portal_url = getToolByName(self.context, "portal_url")
        portal = portal_url.getPortalObject()
        old_guestbook = portal.restrictedTraverse(old_path)
        entries = old_guestbook.objectValues()
        entries.sort(key=lambda entry: entry.date)

        for entry in entries:
            date = entry.date.asdatetime()
            date = date.replace(tzinfo=None)
            createContentInContainer(self.context, 'sbo.inkstain.guestbookentry',
                entry_date=date,
                author=entry.name,
                email_address=entry.email_address,
                homepage_address=entry.homepage_address,
                message=entry.message,
                moderation_state='published',
                ip='unknown'
            )
        self.request.response.redirect(self.context.absolute_url())
        return ''
    def create_modules(self, module_path):
        path = ""
        module = None
        for element in module_path.split('.'):
            path += element

            try:
                module = __import__(path)
            except ImportError:
                new = imp.new_module(path)
                if module is not None:
                    setattr(module, element, new)
                module = new

            sys.modules[path] = module
            __import__(path)

            path += "."

        return module

    def stub(self, module_path, class_name, base_class, meta_class=type):
        module = self.create_modules(module_path)
        cls = meta_class(class_name, (base_class, ), {})
        setattr(module, class_name, cls)

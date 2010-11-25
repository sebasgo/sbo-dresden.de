from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner

class GuestbookView(BrowserView):
    __call__ = ViewPageTemplateFile('guestbook.pt')

    def entries(self):
        context = aq_inner(self.context)
        return context.entries[::-1]


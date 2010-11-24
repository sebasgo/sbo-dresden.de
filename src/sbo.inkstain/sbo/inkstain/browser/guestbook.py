from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class GuestbookView(BrowserView):
    __call__ = ViewPageTemplateFile('guestbook.pt')
    
    def canAddSignature(self):
        return True

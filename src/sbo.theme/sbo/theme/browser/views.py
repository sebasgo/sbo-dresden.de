from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ConcertsView(BrowserView):
    
    template = ViewPageTemplateFile('templates/concerts.pt')
    
    def __call__(self):
        return self.template()
    
    def concerts(self):
        return [];

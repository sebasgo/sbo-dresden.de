from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FrontPageView(BrowserView):
    template = ViewPageTemplateFile('frontpage.pt')

    def __call__(self):
        return self.template()

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ConcertsView(BrowserView):
    
    template = ViewPageTemplateFile('templates/concerts.pt')
    
    def __call__(self):
        return self.template()
    
    def concerts(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type='Event',
            path={'query': '/'.join(context.getPhysicalPath()), 'level': -1},
            start={'query': context.ZopeTime(), 'range': 'min'},
            sort_on='start',
            sort_order='ascending'
        )
        return results;

class NewsView(BrowserView):
    
    template = ViewPageTemplateFile('templates/news.pt')
    
    def __call__(self):
        return self.template()
    
    def news(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type='News Item',
            path={'query': '/'.join(context.getPhysicalPath()), 'level': -1},
            sort_on='created',
            sort_order='descending'
        )
        return results;

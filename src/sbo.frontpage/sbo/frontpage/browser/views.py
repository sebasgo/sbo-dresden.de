from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FrontPageView(BrowserView):
    template = ViewPageTemplateFile('frontpage.pt')

    def __call__(self):
        return self.template()
    
    def cover_image(self):
        context = aq_inner(self.context)
        return context.cover_image
    
    def concerts(self):
        context = aq_inner(self.context)
        limit = 3
        src = context.concerts_folder
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type='Event',
            path={'query': '/'.join(src.getPhysicalPath()), 'level': -1},
            start={'query': context.ZopeTime(), 'range': 'min'},
            sort_on='start',
            sort_order='ascending',
            sort_limit=limit
        )[:limit]
        return [brain.getObject() for brain in results]
        

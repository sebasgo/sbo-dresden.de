from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FrontPageView(BrowserView):

    template = ViewPageTemplateFile('frontpage.pt')

    def __call__(self):
        return self.template()
    
    def cover_images(self):
        context = aq_inner(self.context)
        return [ref.to_object for ref in context.cover_images]
    
    def concerts(self):
        context = aq_inner(self.context)
        limit = 3
        src_path = context.concerts_folder.to_path
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type='Event',
            path={'query': src_path, 'level': -1},
            start={'query': context.ZopeTime(), 'range': 'min'},
            sort_on='start',
            sort_order='ascending',
            sort_limit=limit
        )[:limit]
        return [brain.getObject() for brain in results]

    def news(self):
        context = aq_inner(self.context)
        limit = 3
        src_path = context.news_folder.to_path
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type='News Item',
            path={'query': src_path, 'level': -1},
            sort_on='created',
            sort_order='descending',
            sort_limit=limit
        )[:limit]
        return [brain.getObject() for brain in results]

    def news_target_url(self, news_item):
        context = aq_inner(self.context)
        return u"{0}#{1}".format(
            context.news_folder.to_object.absolute_url(),
            news_item.getId()
        )

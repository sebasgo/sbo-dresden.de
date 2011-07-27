from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.FactoryTool import TempFolder
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

def isTemporary(obj):
    """Check to see if an object is temporary"""
    parent = aq_base(aq_parent(aq_inner(obj)))
    return hasattr(parent, 'meta_type') and parent.meta_type == TempFolder.meta_type

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

class GalleryView(BrowserView):
    
    template = ViewPageTemplateFile('templates/gallery.pt')
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        context = aq_inner(self.context)
        self.ploneview = context.restrictedTraverse('@@plone')
        self.pm = getToolByName(context, 'portal_membership')
        
    def __call__(self):
        return self.template()

    def sub_galleries(self):
        context = aq_inner(self.context)
        return context.values(self.context.meta_type)

    def get_imgs_of(self, gallery, limit=None):
        return gallery.getFolderContents(
            {'portal_type': ('Image',)},
            full_objects=True,
            batch=(limit is not None),
            b_size=limit
        )

    def is_uploader_available(self):
        context = aq_inner(self.context)
        if self.ploneview.isStructuralFolder() \
           and self.pm.checkPermission('Add portal content', context) \
           and not isTemporary(context):
            return True
        return False
    
    def get_upload_url(self):
        """
        return upload url
        in current folder
        """
        context = aq_inner(self.context)
        folder_url = self.ploneview.getCurrentFolderUrl()                      
        return '%s/@@quick_upload' %folder_url
        
    def get_data_for_upload_url(self):
        data_url = 'mediaupload=%s' % 'image' 
        return data_url      

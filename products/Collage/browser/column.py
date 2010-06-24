from types import UnicodeType

from Products.Five.browser import BrowserView

from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone import utils as cmfutils

COLLAGE_TYPES = ('Collage', 'CollageRow', 'CollageColumn', 'CollageAlias')

from utils import escape_to_entities

class ExistingItemsView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        # beware of url-encoded spaces
        if 'portal_type' in self.request:
            self.request['portal_type'] = self.request['portal_type'].replace('%20', ' ')

    def __call__(self):
        """There are browser-issues in sending out content in UTF-8.
        We'll encode it in latin-1."""
        
        self.request.RESPONSE.setHeader("Content-Type",
                                        "text/html; charset=ISO-8859-1")

        encoding = getSiteEncoding(self.context.context)

        content = self.index()
        if not isinstance(content, UnicodeType):
            content = content.decode(encoding)

        # convert special characters to HTML entities since we're recoding
        # to latin-1
        return escape_to_entities(content).encode('latin-1')
    
    @property
    def catalog(self):
        return cmfutils.getToolByName(self.context,
                                      'portal_catalog')

    def portal_url(self):
        return cmfutils.getToolByName(self.context, 'portal_url')()

    def normalizeString(self, str):
        return self.context.plone_utils.normalizeString(str)
        
    def getItems(self):
        items = self.catalog(self.request,
                             sort_order='reverse',
                             sort_on='modified')

        # filter out collage content types
        items = [i for i in items if i.portal_type not in COLLAGE_TYPES]

        # limit count
        items = items[:self.request.get('count', 50)]

        # setup description cropping
        try:
            cropText = self.context.restrictedTraverse('@@plone').cropText
        except AttributeError:
            # BBB: Plone 2.5
            cropText = self.context.cropText

        props = cmfutils.getToolByName(self.context, 'portal_properties')
        site_properties = props.site_properties
        
        desc_length = getattr(site_properties, 'search_results_description_length', 25)
        desc_ellipsis = getattr(site_properties, 'ellipsis', '...')
        
        return [{'UID': obj.UID(),
                 'icon' : result.getIcon,
                 'title': result.Title,
                 'description': cropText(result.Description, desc_length, desc_ellipsis),
                 'type': result.Type,
                 'portal_type':  self.normalizeString(result.portal_type),
                 'modified': result.ModificationDate,
                 'published': result.EffectiveDate or ''} for (result, obj) in
                map(lambda result: (result, result.getObject()), items)]

from Acquisition import aq_parent

from zope.interface import implements
from zope.component import adapts, adapter
from zope.event import notify

from z3c.caching.interfaces import IPurgePaths
from z3c.caching.purge import Purge

from Products.CMFCore.interfaces import IContentish, ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces import IATNewsItem, IATEvent
from Products.DCWorkflow.interfaces import IAfterTransitionEvent

from plone.app.caching.utils import isPurged
    
class NewsItemPurgePaths(object):
    """Additional paths to prune for news items
    
    Includes:
    * ${object_path}/${image_paths}
    * /${containing_folder} (the path the news items are aggregated)
    * / (news items appear on frontpage)
    """
    
    implements(IPurgePaths)
    adapts(IATNewsItem)
    
    def __init__(self, context):
        self.context = context
        
    def getRelativePaths(self):
        prefix = self.context.absolute_url_path()
        
        for name in self._getAllowedImageSizeNames():
            print ">> purging {0}".format(prefix + '/' + name)
            yield prefix + '/' + name
        
        for path in getAggregationPurgePaths(self.context):
            yield path
        
        
    def getAbsolutePaths(self):
        return []
    
    def _getAllowedImageSizeNames(self):
        properties_tool = getToolByName(self.context, 'portal_properties')
        imagescales_properties = getattr(properties_tool, 'imaging_properties', None)
        raw_scales = getattr(imagescales_properties, 'allowed_sizes', [])
        
        return [line.split(' ')[0] for line in raw_scales if line != ""]


class EventPurgePaths(object):
    """Additional paths to prune for events
    
    Includes:
    * /${containing_folder} (the path the events are aggregated)
    * / (events appear on frontpage)
    """
    
    implements(IPurgePaths)
    adapts(IATEvent)
    
    def __init__(self, context):
        self.context = context
        
    def getRelativePaths(self):
        for path in getAggregationPurgePaths(self.context):
            yield path
        
        
    def getAbsolutePaths(self):
        return []

def getAggregationPurgePaths(context):
    container = aq_parent(context)
    while container:
        parent = aq_parent(container)
        if ISiteRoot.providedBy(parent):
            root_prefix = parent.absolute_url_path()
            container_prefix = container.absolute_url_path()
            yield root_prefix
            yield root_prefix + '/'
            yield container_prefix
            yield container_prefix + '/'
            break
        container = parent

@adapter(IContentish, IAfterTransitionEvent)
def purgeOnWorkflowTransition(object, event):
    if isPurged(object):
        notify(Purge(object))

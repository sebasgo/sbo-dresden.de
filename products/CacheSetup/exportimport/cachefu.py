from zope import component
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import Expression
from Products.GenericSetup import interfaces as gsinterfaces
from Products.CacheSetup.exportimport import atcontent

_PROJECT = 'CacheFu'
_FILENAME = 'cachesettings.xml'

def importSetup(context):
    """ Import setup.
    """
    site = context.getSite()
    logger = context.getLogger(_PROJECT)
    
    repo_tool = cmfutils.getToolByName(site, 'portal_cache_settings')

    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = component.queryMultiAdapter((repo_tool, context), gsinterfaces.IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body
    logger.info('setup imported.')

def exportSetup(context):
    """ Export setup.
    """
    site = context.getSite()
    logger = context.getLogger(_PROJECT)
    
    repo_tool = cmfutils.getToolByName(site, 'portal_cache_settings', None)
    if repo_tool is None:
        logger.info('Nothing to export.')
        return

    exporter = component.queryMultiAdapter((repo_tool, context), gsinterfaces.IBody)
    if exporter is None:
        return '%s: Export adapter misssing.' % _PROJECT
    #if exporter.body is None:
    #    logger.error("Setup export has an empty body. Probably we're missing "
    #                 "the right adapter. What we got: %s.", exporter)
    #    return
    # ^^^ We're not allowed to do this, just looking at exporter.body
    # twice raises a "two document elements" error....
    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    logger.info('setup exported.')


class CacheSettingsAdapter(atcontent.ATContentAdapterBase):
    _topname = 'cachesettings'
    _fields = ['cacheConfig', 'domains', 'squidURLs', 'gzip', 
               'varyHeader']
    _pagecachemanager_fields = ["threshold",
                                "cleanup_interval",
                                "max_age",
                                "active"]

class HeaderSetFolderAdapter(atcontent.ATContentAdapterBase):
    _topname = 'headersets'
    _fields = []


class HeaderSetAdapter(atcontent.ATContentAdapterBase):
    _topname = 'headerset'
    _fields = ['description', 'pageCache', 'lastModified',
               'etag', 'enable304s', 'vary', 'maxAge', 'sMaxAge', 
               'mustRevalidate', 'proxyRevalidate', 'noCache', 'noStore',
               'public', 'private', 'noTransform', 'preCheck', 
               'postCheck']


class RuleFolderAdapter(atcontent.ATContentAdapterBase):
    _topname = 'rules'
    _fields = []


class PolicyCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _topname = 'policycacherule'
    _fields = ['description', 'cacheManager', 'types', 'ids', 'cacheStop']


header_set_fields = ['varyExpression', 'lastModifiedExpression', 
                    'headerSetIdExpression', 'headerSetIdAuth', 
                    'headerSetIdAnon', 'predicateExpression', 'cacheStop']
etag_fields = ['etagExpression', 'etagTimeout', 'etagRequestValues', 
               'etagComponents']


class ContentCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _topname = 'contentcacherule'
    _fields = ['description', 'contentTypes', 'defaultView', 'templates', 
               'purgeExpression'] + header_set_fields + etag_fields


class TemplateCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _topname = 'templatecacherule'
    _fields = ['description', 'templates'] + header_set_fields + etag_fields

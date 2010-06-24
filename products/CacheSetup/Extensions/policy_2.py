from Products.CacheSetup import config

# no-proxy-cache
# Apache-Zope or Zope-only, with no purgeable proxy cache

POLICY_ID = "no-proxy-cache"
POLICY_TITLE = "No Proxy Cache"

def addCacheRules(rules):

    id = 'httpcache'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='PolicyHTTPCacheManagerCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('HTTPCache')
        rule.setCacheManager('HTTPCache')
        rule.setDescription('Rule for content associated with HTTPCache.  This content is cached in the proxy and in the browser.  ETags are not useful because these files have no personalization.')
        rule.setCacheStop([])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-browser-24-hours')
        rule.setHeaderSetIdAuth('cache-in-browser-24-hours')
        rule.setVaryExpression('python:getattr(object, \'meta_type\', None) not in [\'Filesystem Image\', \'Image\'] and rule.portal_cache_settings.getVaryHeader() or \'\'')
        
    id = 'plone-content-types'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='ContentCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('Content')
        rule.setDescription('Rule for views of plone content types.  Anonymous users are served content object views from the proxy cache.  These views are purged when content objects change.  Authenticated users are served pages from memory.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the navigation tree stays up to date.')
        rule.setContentTypes(['Document', 'Event', 'Link', 'News Item', 'Image', 'File'])
        rule.setDefaultView(True)
        rule.setTemplates([])
        rule.setCacheStop(['portal_status_message','statusmessages','SearchableText'])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-memory')
        rule.setHeaderSetIdAuth('cache-with-etag')
        rule.setEtagComponents(['member','catalog_modified','language','gzip','skin'])
        rule.setEtagRequestValues(['month','year','orig_query'])
        rule.setEtagTimeout(3600)
        rule.setPurgeExpression('python:object.getImageAndFilePurgeUrls()')
        
    id = 'plone-containers'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='ContentCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('Containers')
        rule.setDescription('Rule for views of Plone containers.  Both anonymous and authenticated users are served pages from memory, not the proxy cache.  The reason is that we can\'t easily purge container views when they change since container views depend on all of their contained objects, and contained objects do not necessarily purge their containers\' views when they change.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the contents and the navigation tree stays up to date.')
        rule.setContentTypes(['Topic', 'Folder', 'Plone Site', 'Large Plone Folder'])
        rule.setDefaultView(True)
        rule.setTemplates(['folder_contents', 'RSS'])
        rule.setCacheStop(['portal_status_message','statusmessages','SearchableText'])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-memory')
        rule.setHeaderSetIdAuth('cache-with-etag')
        rule.setEtagComponents(['member','catalog_modified','language','gzip','skin'])
        rule.setEtagRequestValues(['b_start','month','year','orig_query'])
        rule.setEtagExpression('python:request.get(\'__cp\',None) is not None')
        rule.setEtagTimeout(3600)
        
    id = 'plone-templates'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='TemplateCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('Templates')
        rule.setDescription('Rule for various non-form templates.  Both anonymous and authenticated users are served pages from memory, not the proxy cache, because some of these templates depend on catalog queries.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the contents and the navigation tree stays up to date.')
        rule.setTemplates(['accessibility-info','sitemap','recently_modified'])
        rule.setCacheStop(['portal_status_message','statusmessages','SearchableText'])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-memory')
        rule.setHeaderSetIdAuth('cache-with-etag')
        rule.setEtagComponents(['member','catalog_modified','language','gzip','skin'])
        rule.setEtagRequestValues(['month','year','orig_query'])
        rule.setEtagTimeout(3600)
        
    id = 'resource-registries'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='PolicyHTTPCacheManagerCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('CSS & JS')
        rule.setDescription('Rule for CSS and JS generated by ResourceRegistries.  These files are cached "forever" (1 year) in squid and in browsers.  There is no need to purge these files because when they are changed and saved in portal_css/portal_js, their file names change.  ETags are not useful because these files have no personalization.')
        rule.setCacheManager(config.OFS_CACHE_ID)
        rule.setCacheStop([])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setTypes(['File'])
        rule.setHeaderSetIdAnon('expression')
        rule.setHeaderSetIdAuth('expression')
        rule.setHeaderSetIdExpression('python:object.getHeaderSetIdForCssAndJs()')
        rule.setVaryExpression('string:')

    id = 'downloads'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='PolicyHTTPCacheManagerCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('Files & Images')
        rule.setDescription('Rule for ATFile and ATImage downloads.  Files that are viewable by Anonymous users are cached in squid; files that are not viewable by Anonymous users are cached only on the browser.  ETags are not useful because these files have no personalization.')
        rule.setCacheManager(config.OFS_CACHE_ID)
        rule.setTypes(['Image', 'File'])
        rule.setCacheStop([])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('expression')
        rule.setHeaderSetIdAuth('expression')
        rule.setHeaderSetIdExpression('python:object.portal_cache_settings.canAnonymousView(object) and \'cache-with-last-modified\' or \'no-cache\'')
        rule.setVaryExpression('string:')

    id = 'dtml-css'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='TemplateCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('DTML CSS files')
        rule.setDescription('Rule for css files generated with DTML.  These files will be cached in the browser for 24 hours.')
        rule.setTemplates(['IEFixes.css'])
        rule.setCacheStop([])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-browser-24-hours')
        rule.setHeaderSetIdAuth('cache-in-browser-24-hours')
        rule.setEtagComponents([])
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(None)
        rule.setVaryExpression('string:')

    for rule in rules.objectValues():
        rule.unmarkCreationFlag()
        rule.reindexObject()

def addHeaderSets(header_sets):

    id = 'no-cache'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Do not cache')
        hs.setDescription('Should not be cached in proxy.  Browser cache should revalidate every time.')
        hs.setPageCache(0)
        hs.setLastModified('delete')
        hs.setEtag(0)
        hs.setEnable304s(0)
        hs.setVary(True)
        hs.setMaxAge(0)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(1)
        hs.setNoStore(0)
        hs.setPublic(0)
        hs.setPrivate(1)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-in-memory'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache in Memory')
        hs.setDescription('Page should be cached in memory on the server.  Page should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the page\'s ETag before displaying a cached page.')
        hs.setPageCache(1)
        hs.setLastModified('delete')
        hs.setEtag(1)
        hs.setEnable304s(1)
        hs.setVary(True)
        hs.setMaxAge(0)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(0)
        hs.setPrivate(1)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-with-etag'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache with ETag')
        hs.setDescription('Page should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the page\'s ETag before displaying a cached page.')
        hs.setPageCache(0)
        hs.setLastModified('delete')
        hs.setEtag(1)
        hs.setEnable304s(1)
        hs.setVary(True)
        hs.setMaxAge(0)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(0)
        hs.setPrivate(1)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-with-last-modified'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache file with Last-Modified')
        hs.setDescription('File should not be cached in a proxy cache but may be conditionally cached in the browser.  The browser should validate the file\'s Last-Modified time before displaying a cached file.')
        hs.setPageCache(0)
        hs.setLastModified('yes')
        hs.setEtag(0)
        hs.setEnable304s(1)
        hs.setVary(True)
        hs.setMaxAge(0)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(0)
        hs.setPrivate(1)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-in-browser-1-hour'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache in browser for 1 hour')
        hs.setDescription('Should be cached in both proxy and browser.  Both should revalidate after 1 hour.')
        hs.setPageCache(0)
        hs.setLastModified('yes')
        hs.setEtag(0)
        hs.setEnable304s(0)
        hs.setVary(True)
        hs.setMaxAge(3600)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(1)
        hs.setPrivate(0)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-in-browser-24-hours'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache in browser for 24 hours')
        hs.setDescription('Should be cached in both proxy and browser.  Both should revalidate after 24 hours.')
        hs.setPageCache(0)
        hs.setLastModified('yes')
        hs.setEtag(0)
        hs.setEnable304s(0)
        hs.setVary(True)
        hs.setMaxAge(24*3600)
        hs.setSMaxAge('')
        hs.setMustRevalidate(1)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(1)
        hs.setPrivate(0)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    id = 'cache-in-browser-forever'
    if not id in header_sets.objectIds():
        header_sets.invokeFactory(id=id, type_name='HeaderSet')
        hs = getattr(header_sets, id)
        hs.setTitle('Cache in browser forever')
        hs.setDescription('Should be cached in both proxy and browser.  Both should revalidate after 1 year.')
        hs.setPageCache(0)
        hs.setLastModified('yes')
        hs.setEtag(0)
        hs.setEnable304s(0)
        hs.setVary(True)
        hs.setMaxAge(365*24*3600)
        hs.setSMaxAge('')
        hs.setMustRevalidate(0)
        hs.setProxyRevalidate(0)
        hs.setNoCache(0)
        hs.setNoStore(0)
        hs.setPublic(1)
        hs.setPrivate(0)
        hs.setNoTransform(0)
        hs.setPreCheck(None)
        hs.setPostCheck(None)

    for hs in header_sets.objectValues():
        hs.unmarkCreationFlag()
        hs.reindexObject()


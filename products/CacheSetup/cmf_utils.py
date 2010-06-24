from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import parse_etags
# ^^^ There was a whole bunch of code here for plone versions that
# didn't have a recent enough version of CMF to include above
# parse_etags method. I removed it. If needed it can be
# resurrected. [Reinout]    
from Products.CacheSetup.config import CACHE_TOOL_ID

#from AccessControl import ModuleSecurityInfo
#security = ModuleSecurityInfo( 'Products.CMFCore.utils' )
#security.declarePrivate('_setCacheHeaders')

def _setCacheHeaders(obj, extra_context, rule=None, header_set=None,
                     expr_context=None): 
    """Set cache headers according to cache policy manager for the obj."""
    REQUEST = getattr(obj, 'REQUEST', None)
    if REQUEST is None:
        return
    if rule is None:
        pcs = getToolByName(obj, CACHE_TOOL_ID, None)
        object = obj.getParentNode()
        view = obj.getId()
        member = pcs.getMember()
        (rule, header_set) = pcs.getRuleAndHeaderSet(REQUEST, object,
                                                     view, member)
        if header_set is None:
            return
        expr_context = rule._getExpressionContext(REQUEST, object,
                                                  view, member,
                                                  keywords=extra_context)
    elif header_set is None:
        return
    RESPONSE = REQUEST.RESPONSE
    (headers_to_add, 
     headers_to_remove) = header_set.getHeaders(expr_context)
    for h in headers_to_remove:
        if RESPONSE.headers.has_key(h.lower()):
            del RESPONSE.headers[h.lower()]
        elif RESPONSE.headers.has_key(h):
            del RESPONSE.headers[h]
    for key, value in headers_to_add:
        if key == 'ETag':
            RESPONSE.setHeader(key, value, literal=1)
        else:
            RESPONSE.setHeader(key, value)

#security.declarePrivate('_checkConditionalGET')
def _checkConditionalGET(obj, extra_context, rule, header_set,
                         expr_context):
    """A conditional GET is done using one or both of the request
       headers:

       If-Modified-Since: Date
       If-None-Match: list ETags (comma delimited, sometimes quoted)

       If both conditions are present, both must be satisfied.
       
       This method checks the caching policy manager to see if
       a content object's Last-modified date and ETag satisfy
       the conditional GET headers.

       Returns the tuple (last_modified, etag) if the conditional
       GET requirements are met and None if not.

       It is possible for one of the tuple elements to be None.
       For example, if there is no If-None-Match header and
       the caching policy does not specify an ETag, we will
       just return (last_modified, None).
       """

    if header_set is None:
        return False

    # 304s not enabled
    if not header_set.getEnable304s():
        return False

    REQUEST = getattr(obj, 'REQUEST', None)
    if REQUEST is None:
        return False

    if_modified_since = REQUEST.get_header('If-Modified-Since', None)
    if_none_match = REQUEST.get_header('If-None-Match', None)

    if if_modified_since is None and if_none_match is None:
        # not a conditional GET
        return False

    etag_matched = False

    # handle if-none-match
    if if_none_match:
        if not header_set.getEtag():
            # no etag available
            return False

        content_etag = header_set.getEtagValue(expr_context)
        # ETag not available
        if content_etag is None:
            return False
                
        client_etags = parse_etags(if_none_match)
        if not client_etags:
            # bad if-none-match
            return False

        # is the current etag in the list of client-side etags?
        if (content_etag not in client_etags and '*' not in client_etags):
            return False

        etag_matched = True

    # handle if-modified-since
    if if_modified_since:
        if header_set.getLastModified() != 'yes':
            # no modification time available for content object
            return False
        
        # from CMFCore/FSFile.py:
        if_modified_since = if_modified_since.split(';')[0]
        # Some proxies seem to send invalid date strings for this
        # header. If the date string is not valid, we ignore it
        # rather than raise an error to be generally consistent
        # with common servers such as Apache (which can usually
        # understand the screwy date string as a lucky side effect
        # of the way they parse it).
        try:
            if_modified_since=long(DateTime(if_modified_since).timeTime())
        except:
            # bad if-modified-since header - bail
            return False
        
        if if_modified_since < 0: # bad header
            return False

        content_mod_time = header_set.getLastModifiedValue(expr_context)
        if not content_mod_time:
            # if-modified-since but no content modification time available - bail
            return False
        content_mod_time = long(content_mod_time.timeTime())
        if content_mod_time < 0: # bogus modification time
            return False

        # has content been modified since the if-modified-since time?
        if content_mod_time > if_modified_since:
            return False

        # If we generate an ETag, don't validate the conditional GET unless 
        # the client supplies an ETag.  This may be more conservative than the
        # spec requires.
        if header_set.getEtag():
            if not etag_matched:
                return False

    _setCacheHeaders(obj, extra_context, rule, header_set, expr_context)
    REQUEST.RESPONSE.setStatus(304)            
    return True

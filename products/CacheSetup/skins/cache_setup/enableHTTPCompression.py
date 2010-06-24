## Script (Python) "enableHTTPCompression"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=request=None, force=0, debug=0, css=0, js=0
##title=Enable zlib based HTTP compression

# force: force http compression even if the browser doesn't send an accept
# debug: return compression state (0: no, 1: yes, 2: force)
# css: set this to 1 inside a css file (for later use)
# js: set this to 1 inside a js file (for later use)

if request is None:
    request = context.REQUEST

(enable_compression, force, gzip_capable) = \
   context.portal_cache_settings.isGzippable(css, js, request)

if not enable_compression:
    if debug:
        return '<!-- compression status: disabled -->'
    else:
        return

result = request.RESPONSE.enableHTTPCompression(REQUEST=request, force=force)

if debug:
    return '<!-- compression status: %s -->' % result

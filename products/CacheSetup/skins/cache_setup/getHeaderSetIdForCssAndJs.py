## Script (Python) "getPolicyIdForCssAndJs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get caching policy for RR-generated CSS and JS files

from AccessControl import Unauthorized

id = context.getId().lower()
if id.endswith('.js'):
    url = context.absolute_url()
    if url.find('/portal_javascripts/') == -1:
        return None
    reg = context.portal_javascripts
elif id.endswith('.css'):
    url = context.absolute_url()
    if url.find('/portal_css/') == -1:
        return None
    reg = context.portal_css
else:
    return None

try:
    # XXX workaround for the fact that RR's isCacheable lacks a docstring
    isCacheable = reg.isCacheable(context.getId())
except Unauthorized:
    isCacheable = True

if isCacheable and not reg.getDebugMode():
    return 'cache-in-browser-forever'
else:
    return 'no-cache'

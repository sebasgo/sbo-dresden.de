## Script (Python) "getImageAndFilePurgeUrls"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get extra urls to purge for ATImage and ATFile downloads

if not context.portal_type in ('Image', 'File'):
    return []
url_tool = context.portal_url
obj_url = url_tool.getRelativeUrl(context)
if context.portal_type == 'File':
    suffixes = ['/download']
elif context.portal_type == 'Image':
    field = context.getField('image')
    scalenames = field.getAvailableSizes(context)
    suffixes = ['/image_' + s for s in scalenames]
return [obj_url + s for s in suffixes]

## Script (Python) "page_cache_purge"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

context.manage_purgePageCache()
try:
    from Products.CMFPlone import PloneMessageFactory as _
    context.plone_utils.addPortalMessage(_(u'PageCache was purged.'))
except:
    # we're not in 2.5
    state.set(status='success', portal_status_message='PageCache was purged.')
return state

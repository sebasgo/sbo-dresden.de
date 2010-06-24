## Script (Python) "page_cache_setup"
##title=Configure the page cache manager
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

from Products.CacheSetup.config import PAGE_CACHE_MANAGER_ID

page_cache = getattr(context, PAGE_CACHE_MANAGER_ID)
title = page_cache.Title()
request = context.REQUEST
settings = {'threshold': request.get('threshold', 1000),
            'cleanup_interval': request.get('cleanup_interval', 300),
            'max_age': request.get('max_age', 3600),
            'active': request.get('active', 'on_always'),
           }
page_cache.manage_editProps(title, settings=settings)

try:
    from Products.CMFPlone import PloneMessageFactory as _
    context.plone_utils.addPortalMessage(_(u'PageCache settings changed.'))
except:
    # we're not in 2.5
    state.set(status='success', portal_status_message='PageCache settings changed.')
return state

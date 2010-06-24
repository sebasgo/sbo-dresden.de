## Script (Python) "cache_policy_redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cache Policy Redirect
from Products.CMFCore.utils import getToolByName

camefrom = traverse_subpath[0]
policy_id = traverse_subpath[1]
ct = getToolByName(context, 'portal_cache_settings')

return ct.setDisplayPolicy(policy_id, camefrom=camefrom, redirect=True)

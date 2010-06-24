## Script (Python) "getFolderButtons"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actions
##title=Get Folder Button Actions

# a fix for the lack of folder button actions in the
# global actions variable in Plone 3
# FIXME: we need an updated folder contents template for CacheFu.

from Products.CMFCore.utils import getToolByName

if actions.get('folder_buttons', None) is None:
    portal_actions = getToolByName(context, 'portal_actions')
    button_actions = portal_actions.listActionInfos(object=context, categories=('folder_buttons', ))
    actions.update({'folder_buttons': button_actions})

return actions

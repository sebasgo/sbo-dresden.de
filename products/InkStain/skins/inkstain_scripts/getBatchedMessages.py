## Script (Python) "getBatchedMessages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=b_size=1
##title=wrapper method around to use catalog to get deletable contents
##

from Products.CMFPlone import Batch

contents = context.getSignatures()
b_start  = context.REQUEST.get('b_start', 0)
size     = context.getItems_per_page() or b_size
batch    = Batch(contents, size, int(b_start), orphan=0)

return batch

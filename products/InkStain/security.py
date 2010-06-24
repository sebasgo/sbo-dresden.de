# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import setDefaultRoles


AddISGuestbook = 'InkStain: Add guestbook'
AddISSignature = 'InkStain: Add signature'

setDefaultRoles(AddISGuestbook, ('Manager', 'Owner',))
setDefaultRoles(AddISSignature, ('Member', 'Anonymous',))

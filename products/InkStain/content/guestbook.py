# -*- coding: utf-8 -*-

# modules
import re
from random import randrange
import sha
from DateTime import DateTime

# Errors handling
from zExceptions import BadRequest

# Basic import for content types
from AccessControl  import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.InkStain.security import AddISSignature
from Products.InkStain.config import CAPTCHA, SECRET
from Products.Archetypes.public import BaseContent, registerType
from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder

# Fields and widgets imports
from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField, IntegerWidget


# Schemas
GuestbookSchema = Schema((
    IntegerField('items_per_page',
                 required = True,
                 searchable = False,
                 default = 15,
                 widget = IntegerWidget(label="Messages per page",
                                        label_msgid="label_per_page",
                                        description="Number of messages per page",
                                        description_msgid="description_per_page",
                                        i18n_domain='inkstain',
                                        ),
                 ),
    ))

# Content classes

class ISSignature( SimpleItem ):
    """
    A signature
    """
    # Post data
    post = None
    date = None

    # Security
    security = ClassSecurityInfo()

    # Methods
    security.declareProtected(AddISSignature, 'writeDown')
    def writeDown(self, post = None):
        self.post = post
        self.date = DateTime()

    security.declareProtected('View', 'readOutLoud')
    def readOutLoud(self):
        return self.post
    

class ISGuestbook( ATBTreeFolder ):
    """
    A guestbook
    """
    # Configuration of my type
    portal_type = metal_type    = "Guestbook"
    archetype_name              = "Guestbook"
    content_icon                = "guestbook_icon.gif"
    schema                      = ATBTreeFolder.schema.copy() + \
                                  GuestbookSchema
    typeDescription             = "A guestbook"
    typeDescMsgId               = "label_guestbook"

    # Base attributes
    allowed_content_types       = []
    allow_discussion            = False
    global_allow                = True
    _at_rename_after_creation   = True

    # Views
    default_view                = 'guestbook_view'
    immediate_view              = 'guestbook_view'
    suppl_views                 = ()

    # Security
    security = ClassSecurityInfo()


    security.declareProtected('View', 'canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


    security.declareProtected('View', 'canAddSignature')
    def canAddSignature(self):
        """
        Checks if the current user is allowed to add content to
        the guestbook.
        """
        mtool = self.portal_membership
        return mtool.checkPermission(AddISSignature, self) and True or False


    security.declareProtected('View', 'canDelSignature')
    def canDelSignature(self):
        """
        Checks if the current user is allowed to del content of
        the guestbook.
        """
        mtool = self.portal_membership
        return mtool.checkPermission('Modify portal content', self) and True or False
    

    security.declareProtected(AddISSignature, 'addSignature')
    def addSignature(self, post):
        """
        A simple method to add a guest signature
        """
        maxId = 0
        
        for id in self.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        
        nid = str(maxId + 1)
        signature = ISSignature()
        signature.id = nid
        signature.writeDown(post = post)
        self._setObject(nid, signature)


    security.declareProtected('Modify portal content', 'delSignatures')
    def delSignatures(self):
        """
        A simple method to delete a guest signature
        """
        request  = self.REQUEST
        response = request.RESPONSE
        ids = request.get('messages', None)
        utils = self.plone_utils
        charset = utils.getSiteEncoding()
        
        response.setHeader('Content-Type', 'text/xml; charset=%s' % charset)
        
        if ids:
            try:
                self.manage_delObjects(ids = ids)
                psm = self.translate(msgid='messages_deleted',
                                     default='Your messages have been deleted from the guestbook',
                                     domain='inkstain')
                response.redirect(self.absolute_url() + \
                                  '/?portal_status_message=' + \
                                  psm)
                return True
            except BadRequest:
                pass

        psm = self.translate(msgid='messages_notdeleted',
                             default='An error occured during the deletion',
                             domain='inkstain')
        response.redirect(self.absolute_url() + \
                          '/?portal_status_message=' + \
                          psm)
        return False
    

    security.declarePrivate('sortSignatures')
    def sortSignatures(self, signature1, signature2):
        """
        Sort the signature per ids
        """
        id1 = int(signature1.getId())
        id2 = int(signature2.getId())
        
        if id1 < id2:
            return 1
        
        if id1 > id2:
            return -1
        
        return 0
        

    security.declareProtected('View', 'getSignatures')
    def getSignatures(self):
        """
        """
        messages = list(self.objectValues())
        messages.sort(self.sortSignatures)
        return messages


    security.declareProtected('View', 'isUrlValid')
    def isUrlValid(self, value):
        """
        return true is the url is correctly formatted
        false otherwise
        """
        pattern = re.compile(r'(ht|f)tps?://[^\s\r\n]+')
        m = pattern.match(value)
        return m and True or False


    security.declareProtected(AddISSignature, 'getCaptcha')
    def getCaptcha(self):
        """
        Returns a word and its digest and a position
        """
        word = CAPTCHA[randrange(0, len(CAPTCHA))]
        letter_pos = randrange(0, len(word))
        return word, letter_pos + 1, self.encryptCaptcha(word[letter_pos])


    security.declareProtected(AddISSignature, 'encryptCaptcha')
    def encryptCaptcha(self, word):
        """
        Digest a word given in parameter
        """
        hash = sha.new()
        hash.update(word)
        hash.update(SECRET)
        return hash.hexdigest()
        

registerType(ISGuestbook)

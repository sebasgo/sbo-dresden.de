## Controller Python Script "signature_addscript"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=RESPONSE=None
##title=Create a thread or a post, for anonymous
##
from DateTime import DateTime
from Products.InkStain import InkStainMessageFactory as _

#try:
    # That's for Plone2.5
#    from Products.CMFPlone import MessageFactory
#    mf = MessageFactory('inkstain')
#    MF = True
#except:
    # That's for earlier Plone
#    MF = False

    
utils   = context.plone_utils
charset = utils.getSiteEncoding()
anon    = context.portal_membership.isAnonymousUser()
member  = anon and 'Anonymous user' or context.portal_membership.getAuthenticatedMember().getId()
request = context.REQUEST

post = dict(
    name     = request.get('name',   None),
    email    = request.get('email',  None),
    message  = request.get('message', None), 
    homepage = request.get('homepage', None),
    )

context.addSignature(post = post)

context.plone_utils.addPortalMessage(_('Your message has been recorded in the guestbook'))
return state.set()

#if not MF:
#    RESPONSE.setHeader('Content-Type', 'text/xml; charset=%s' % charset)
#    portal_status_message = context.translate(msgid='message_recorded',
#                                              default='Your message has been recorded in the guestbook',
#                                              domain='inkstain')

#    return state.set(status='success', portal_status_message=portal_status_message)

#elif MF:
#    msg = mf('message_recorded',
#             'Your message has been recorded in the guestboook')
#    context.plone_utils.addPortalMessage(msg)
#    return state.set()

return state.set(status='success')

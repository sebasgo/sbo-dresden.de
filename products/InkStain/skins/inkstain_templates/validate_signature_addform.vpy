## Controller Python Script "validate_signature_addform"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates a guestbook post

import re

def validate_email(name, value):
    reg_tool = context.portal_registration
    if not reg_tool.isValidEmail(value):
        state.setError(name,
                       'This is not a valid email address',
                       'email_bad_input')
        
def validate_url(name, value):
    if not context.isUrlValid(value):
        state.setError(name,
                       'This is not a valid http address',
                       'homepage_bad_input')

def validate_captcha(name, value):
    key = context.REQUEST.get('captcha_key', None)
    res = context.encryptCaptcha(value)
    if key != res:
        state.setError(name,
                       'This is the wrong answer.',
                       'captcha_bad_input')


fields = (
    { 'fid' : 'name',
      'required' : True,
      'validator' : None },
    
    { 'fid' : 'message',
      'required' : True,
      'validator' : None },
    
    { 'fid' : 'homepage',
      'required' : False,
      'validator' : validate_url },
    
    { 'fid' : 'email',
      'required' : True,
      'validator' : validate_email },

    { 'fid' : 'captcha',
      'required' : True,
      'validator' : validate_captcha },
    )

for field in fields:
    
    name      = field['fid']
    value     = context.REQUEST.get(name, None)
    required  = field['required']
    validator = field['validator']
    
    if required and not value:
        state.setError(name,
                       'This field is required, please provide some information.',
                       'input_required')
    elif validator and value:
        validator(name, value)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')

return state

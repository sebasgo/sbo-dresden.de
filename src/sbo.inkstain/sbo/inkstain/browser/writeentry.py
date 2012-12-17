import re
from uuid import uuid4
from DateTime import DateTime

from Acquisition import aq_inner
from zope.interface import Interface
from zope import schema
from zope.component import getMultiAdapter
from z3c.form import form, field, button
from ZODB.POSException import ConflictError
from plone.z3cform.layout import FormWrapper, wrap_form
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from sbo.inkstain import InkstainMessageFactory as _
from sbo.inkstain.content.guestbook import GuestbookEntry

# Define a valiation method for email addresses
class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True

class NotAnHomepageUrl(schema.ValidationError):
    __doc__ = _(u"Invalid homepage address")

check_homepage_url = re.compile(r"https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?").match
def validate_homepage_url(value):
    if not check_homepage_url(value):
        raise NotAnHomepageUrl(value)
    return True

class IWriteEntryForm(Interface):
    """Define the fields of our form
    """

    name = schema.TextLine(
        title=_(u"Your name"),
        required=True
    )

    email_address = schema.ASCIILine(
        title=_(u"Your email address"),
        description=_(u"Won't be published."),
        required=True,
        constraint=validate_email
    )

    homepage_address = schema.ASCIILine(
        title=_(u"Your homepage"),
        description=_(u"You may leave the address of own homepage."),
        required=False,
        constraint=validate_homepage_url
    )

    message = schema.Text(
        title=_(u"Message"),
        description=_(u"Please keep to 1,000 characters."),
        required=True,
        max_length=1000
    )

    captcha = schema.TextLine(
        title=u"ReCaptcha",
        description=u"",
        required=False
    )

class Entry(object):
    name = u""
    email_address = u""
    homepage_address = u""
    message = u""
    captcha = u""
    def __init__(self, context):
        self.context = context

class BaseForm(form.Form):
    fields = field.Fields(IWriteEntryForm)
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    label = _(u"Write a guestbook entry")
    description = _(u"Got a comment? Please submit it using the form below!")

    def updateWidgets(self):
        super(BaseForm, self).updateWidgets()
        self.widgets['message'].rows = 5;
        self.widgets['captcha'].label = u''

    # This trick hides the editable border and tabs in Plone
    def render(self):
        self.request.set('disable_border', True)
        return super(BaseForm, self).render()

    @property
    def action(self):
        """ Rewrite HTTP POST action.

        If the form is rendered embedded on the others pages we
        make sure the form is posted always through the same view,
        instead of making a HTTP POST request to the page
        where the form was rendered.
        """
        return self.context.absolute_url() + "/@@writeentry"

    @button.buttonAndHandler(_(u'Submit'))
    def action_send(self, action):
        context = aq_inner(self.context)
        data, errors = self.extractData()
        captcha = getMultiAdapter((self.context, self.request), name='recaptcha')

        if captcha.verify():
            entry = GuestbookEntry()
            entry.id = uuid4().hex
            entry.date = DateTime()
            entry.name = data['name']
            entry.email_address = data['email_address']
            entry.homepage_address = data['homepage_address']
            entry.message = data['message']

            context.addEntry(entry)

            self.send_notification_mail(entry)

            confirm = _(u"Thank you for your guestbook entry!")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')

            self.request.response.redirect(context.absolute_url())
            return ''

        return ''

    def send_notification_mail(self, entry):
        context = aq_inner(self.context)
        urltool = getToolByName(context, 'portal_url')
        plone_utils = getToolByName(context, 'plone_utils')
        portal = urltool.getPortalObject()
        send_to_address = portal.getProperty('email_from_address')
        envelope_from = portal.getProperty('email_from_address')
        subject = _(u"New guestbook entry")
        encoding = portal.getProperty('email_charset')
        message_tpl = _(u"Name: {name}\nEmail: {mail}\nHomepage: {homepage}\n\n{text}")
        message = message_tpl.format(
            name=entry.name,
            mail=entry.email_address,
            homepage=entry.homepage_address,
            text=entry.message
        ).encode(encoding)
	try:
            host = getToolByName(self, 'MailHost')
            result = host.send(message, send_to_address, envelope_from,
                                   subject=subject, charset=encoding)
        except ConflictError:
            raise
        except: # TODO Too many things could possibly go wrong. So we catch all.
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                            mapping={u'exception' : exception})
            plone_utils.addPortalMessage(message, 'error')


class InlineWriteEntryForm(FormWrapper):
     """ Form view which renders z3c.forms embedded in a portlet.

     Subclass FormWrapper so that we can use custom frame template. """

     form = BaseForm
     index = ViewPageTemplateFile("formwrapper.pt")

WriteEntryForm = wrap_form(BaseForm)

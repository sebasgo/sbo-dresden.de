import re
import datetime
from email.mime.text import MIMEText
from uuid import uuid4

from Acquisition import aq_inner
from plone.dexterity.utils import createContentInContainer
from plone.z3cform.layout import FormWrapper, wrap_form
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
from zope import schema
from zope.component import getMultiAdapter
from z3c.form import form, field, button, validator
from ZODB.POSException import ConflictError

from collective.z3cform.norobots.i18n import norobotsMessageFactory
from collective.z3cform.norobots.widget import NorobotsFieldWidget
from collective.z3cform.norobots.validator import NorobotsValidator

from sbo.inkstain import InkstainMessageFactory as _
from sbo.inkstain.interfaces.guestbook import moderation_states
from sbo.inkstain.interfaces.guestbook import validate_email
from sbo.inkstain.interfaces.guestbook import validate_homepage_url

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

    norobots = schema.TextLine(
        title=norobotsMessageFactory(u"Are you a human ?"),
        description=norobotsMessageFactory(u"In order to avoid spam, please answer the question below."),
        required=True
    )

class Entry(object):
    name = u""
    email_address = u""
    homepage_address = u""
    message = u""
    norobots = u""
    def __init__(self, context):
        self.context = context

class BaseForm(form.Form):
    fields = field.Fields(IWriteEntryForm)
    fields['norobots'].widgetFactory = NorobotsFieldWidget

    label = _(u"Write a guestbook entry")
    description = _(u"Got a comment? Please submit it using the form below!")

    def updateWidgets(self):
        super(BaseForm, self).updateWidgets()
        self.widgets['message'].rows = 5;

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

        if len(errors) > 0:
            return ''

        entry = createContentInContainer(context, 'sbo.inkstain.guestbookentry',
            entry_date=datetime.datetime.today(),
            author=data['name'],
            email_address=data['email_address'],
            homepage_address=data['homepage_address'],
            message=data['message'],
            moderation_state='pending',
            ip=get_ip(self.request)
        )
        self.send_notification_mail(entry)
        confirm = _(u"Thank you for your guestbook entry! It will be published after moderation.")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(context.absolute_url())
        return ''

    def send_notification_mail(self, entry):
        context = aq_inner(self.context)
        urltool = getToolByName(context, 'portal_url')
        plone_utils = getToolByName(context, 'plone_utils')
        portal = urltool.getPortalObject()
        send_to_address = portal.getProperty('email_from_address')
        subject = _(u"New guestbook entry")
        encoding = portal.getProperty('email_charset')
        message_tpl = _(u"Name: {name}\nEmail: {mail}\nHomepage: {homepage}\nModeration state: {moderation_state}\nIP: {ip}\n\n{text}")
        message = MIMEText(message_tpl.format(
            name=entry.author,
            mail=entry.email_address,
            homepage=entry.homepage_address,
            moderation_state=moderation_states.getTerm(entry.moderation_state).title,
            ip=entry.ip,
            text=entry.message
        ), "text", encoding)
        message['To'] = send_to_address
        message['From'] = send_to_address
        message['Subject'] = subject
        try:
            host = getToolByName(self, 'MailHost')
            result = host.send(str(message))
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

validator.WidgetValidatorDiscriminators(NorobotsValidator, field=IWriteEntryForm['norobots'])

def get_ip(request):
    """  Extract the client IP address from the HTTP request in proxy compatible way.

    @return: IP address as a string or None if not available
    """
    if "HTTP_X_FORWARDED_FOR" in request.environ:
        # Virtual host
        ip = request.environ["HTTP_X_FORWARDED_FOR"]
    elif "HTTP_HOST" in request.environ:
        # Non-virtualhost
        ip = request.environ["REMOTE_ADDR"]
    else:
        # Unit test code?
        ip = "unknown"

    return ip

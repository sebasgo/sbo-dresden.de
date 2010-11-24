import re
from DateTime import DateTime

from zope.interface import Interface

from zope import schema

from zope.formlib import form
from Products.Five.formlib import formbase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from Acquisition import aq_inner

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
        description=_(u"We will use this to contact you if you request it."),
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

class WriteEntryForm(formbase.PageForm):
    form_fields = form.FormFields(IWriteEntryForm)
    label = _(u"Make a guestbook entry")
    description = _(u"Got a comment? Please submit it using the form below!")

    # This trick hides the editable border and tabs in Plone
    def __call__(self):
        self.request.set('disable_border', True)
        return super(WriteEntryForm, self).__call__()

    @form.action(_(u"Send"))
    def action_send(self, action, data):
        context = aq_inner(self.context)

        entry = GuestbookEntry()
        entry.date = DateTime()
        entry.name = data['name']
        entry.email_address = data['email_address']
        entry.homepage_address = data['homepage_address']
        entry.message = data['message']

        context.entries.append(entry)

        confirm = _(u"Thank you for your guestbook entry!")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')

        self.request.response.redirect(context.absolute_url())
        return ''
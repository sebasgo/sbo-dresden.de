import datetime
import re

from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.directives import form

from sbo.inkstain import InkstainMessageFactory as _

class IGuestbook(Interface):
    """A simple guestbook"""

    entries_per_page = schema.Int(
        title=_(u"Entries per page"),
        description=_(u"Sets the number of entries which are shown on one page."),
        required=True,
        default=15
    )

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


moderation_states = SimpleVocabulary([
    SimpleTerm(value=u'pending', title=_(u"Pending review")),
    SimpleTerm(value=u'published', title=_(u"Published")),
    SimpleTerm(value=u'spam', title=_(u"Spam")),
])

class IGuestbookEntry(Interface):
    entry_date = schema.Datetime(
        title=_(u"Date of the entry"),
        required=True
    )

    author = schema.TextLine(
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

    ip = schema.ASCIILine(
        title=_(u"The IP address the message is originating from.")
    )
    moderation_state = schema.Choice(
        title=_("Moderation state"),
        vocabulary=moderation_states,
        required=True
    )

@form.default_value(field=IGuestbookEntry['entry_date'])
def entry_date_default_value(data):
    return datetime.datetime.today()

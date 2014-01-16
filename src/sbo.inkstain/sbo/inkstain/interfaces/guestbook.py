import re

from zope.interface import Interface
from zope import schema
from sbo.inkstain import InkstainMessageFactory as _

class IGuestbook(Interface):
    """A simple guestbook"""

    entries_per_page = schema.Int(
        title=_(u"Entries per page"),
        description=_(u"Sets the number of entries which are shown on one page."),
        required=True
    )

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


class IGuestbookEntry(Interface):
    #date
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
    ip = schema.ASCIILine(
        title=_(u"The IP address the message is originating from.")
    )
    #moderation_state

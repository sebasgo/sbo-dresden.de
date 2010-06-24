from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *
from Products.CMFCore.permissions import View, ModifyPortalContent

try:
    from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault
    HAS_ISBD = True
except ImportError:
    HAS_ISBD = False

class LayoutContainer(object):
    """
    Container that provides aggregate search and display
    functionality.
    """

    def canSetDefaultPage(self):
        """Based on RichDocument/content/richdocument.py
        This method, from ISelectableBrowserDefault, is used to check whether
        the 'Choose content item to use as deafult view' option will be
        presented. This makes sense for folders, but not for RichDocument, so
        always disallow.
        """
        return False

    def aggregateSearchableText(self):
        """Append references' searchable fields."""

        data = [super(LayoutContainer, self).SearchableText(),]

        for child in self.contentValues():
            data.append(child.SearchableText())

        data = ' '.join(data)

        return data

CommonCollageSchema = atapi.Schema((
    # TODO: move to common, also do it for the collage it self (???)
    atapi.BooleanField('excludeFromNav',
        required = False,
        languageIndependent = True,
        schemata = 'metadata',
        widget = BooleanWidget(
            description="If selected, this item will not appear in the navigation tree",
            description_msgid = "help_exclude_from_nav",
            label = "Exclude from navigation",
            label_msgid = "label_exclude_from_nav",
            i18n_domain = "plone",
            visible={'view' : 'hidden',
                     'edit' : 'visible'},
            ),
        ),
    
    atapi.ReferenceField('relatedItems',
        relationship = 'relatesTo',
        multiValued = True,
        isMetadata = True,
        languageIndependent = False,
        index = 'KeywordIndex',
        write_permission = ModifyPortalContent,
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = True,
            label = "Related Item(s)",
            label_msgid = "label_related_items",
            description = "",
            description_msgid = "help_related_items",
            i18n_domain = "plone",
            #though lets start in root - make more sense for the user
            startup_directory='/',
            visible = {'edit' : 'visible', 'view' : 'invisible' }
            ),
        ),
))

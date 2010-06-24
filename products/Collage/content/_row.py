from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.Collage.content.common import LayoutContainer,CommonCollageSchema
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.Collage.interfaces import ICollageRow

from zope.interface import implements

# CMFDynamicViewFTI imports
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

CollageRowSchema = atapi.BaseContent.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='title',
        accessor='Title',
        required=False,
        widget=atapi.StringWidget(
            label='Title',
            label_msgid='label_optional_row_title',
            description='You may optionally supply a title for this row.',
            description_msgid='help_optional_row_title',
            i18n_domain='collage',
        )
    ),
))

CollageRowSchema = CollageRowSchema + CommonCollageSchema.copy()

# move description to main edit page
CollageRowSchema['description'].schemata = 'default'

# never show row in navigation, also when its selected
CollageRowSchema['excludeFromNav'].default = True

# support show in navigation feature and at marshalling
finalizeATCTSchema(CollageRowSchema, folderish=True, moveDiscussion=False)

class CollageRow(BrowserDefaultMixin, LayoutContainer, atapi.OrderedBaseFolder):
    __implements__ = (getattr(atapi.OrderedBaseFolder,'__implements__',()), \
                      getattr(BrowserDefaultMixin,'__implements__',()))

    schema = CollageRowSchema
    
    _at_rename_after_creation = True

    implements(ICollageRow)

    security = ClassSecurityInfo()

    def SearchableText(self):
        return self.aggregateSearchableText()

    def indexObject(self):
        pass

    def reindexObject(self,idxs=[] ):
        pass

    def unindexObject(self):
        pass


atapi.registerType(CollageRow, 'Collage')

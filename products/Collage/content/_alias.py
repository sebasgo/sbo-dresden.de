from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from Products.Collage.interfaces import ICollageAlias

from zope.interface import implements

from Products.Collage.content.common import LayoutContainer

from Products.ATContentTypes.content.base import ATCTContent

from Products.Archetypes.utils import DisplayList

# CMFDynamicViewFTI imports
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

CollageAliasSchema = ATCTContent.schema.copy() + atapi.Schema((
    atapi.ReferenceField(
        name='target',
        mutator='set_target',
        accessor='get_target',
        relationship='Collage_aliasedItem',
        multiValued = 0,
        allowed_types = (),
        widget=ReferenceBrowserWidget(
            label='Selected target object',
            label_msgid='label_alias_target',
            i18n_domain='collage',
            startup_directory='/',
        ),
    ),
))

# we don't require any fields to be filled out
CollageAliasSchema['title'].required = False

# never show in navigation, also when its selected
CollageAliasSchema['excludeFromNav'].default = True

CollageAliasSchema['relatedItems'].widget.visible = {'edit':'invisible', 'view':'invisible'}

class CollageAlias(BrowserDefaultMixin, LayoutContainer, ATCTContent):
    __implements__ = (getattr(atapi.OrderedBaseFolder,'__implements__',()), \
                      getattr(BrowserDefaultMixin,'__implements__',()))

    implements(ICollageAlias)

    meta_type = 'CollageAlias'

    schema = CollageAliasSchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    def indexObject(self):
        pass

    def reindexObject(self,idxs=[] ):
        pass

    def unindexObject(self):
        pass

atapi.registerType(CollageAlias, 'Collage')

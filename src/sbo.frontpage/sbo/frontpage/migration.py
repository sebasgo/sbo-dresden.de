from Products.contentmigration.basemigrator.walker import CatalogWalker
from plone.app.contenttypes.migration.migration import ATCTContentMigrator
from z3c.relationfield import RelationValue
from zope.intid.interfaces import IIntIds
from zope import component


class FrontpageMigrator(ATCTContentMigrator):

    src_portal_type = 'Frontpage'
    src_meta_type = 'Frontpage'
    dst_portal_type = 'Frontpage'
    dst_meta_type = None  # not used

    def beforeChange_save_frontpage_refs(self):
        self.cover_images = self.old.getCoverImages()
        self.news_folder = self.old.getNewsFolder()
        self.concerts_folder = self.old.getConcertsFolder()

    def migrate_schema_fields(self):
        intids = component.getUtility(IIntIds)
        self.new.cover_images = [RelationValue(intids.getId(obj)) for obj in self.cover_images]
        self.new.news_folder = RelationValue(intids.getId(self.news_folder))
        self.new.concerts_folder = RelationValue(intids.getId(self.concerts_folder))


def migrate_frontpage(portal):
    walker = CatalogWalker(portal, FrontpageMigrator)
    walker.go()



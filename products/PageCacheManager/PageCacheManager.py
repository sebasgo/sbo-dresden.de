 # This file is based on Zope 2.7.7's lib/python/StandardCachemanagers/RAMCachemanager.py
# This software is subject to the Zope Public License (ZPL), Version 2.0
'''
Page cache manager --
  Caches the results of method calls in RAM.

$Id$
'''

from AccessControl import ClassSecurityInfo
from OFS.Cache import CacheManager
from OFS.SimpleItem import SimpleItem
import time
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageCacheManager.PageCache import PageCache
from zope.interface import implements
from Products.PageCacheManager.interfaces import IPageCacheManager

_marker = []  # Create a new marker object.

caches = {}
PRODUCT_DIR = __name__.split('.')[-2]

class PageCacheManager (CacheManager, SimpleItem):
    """Manage a PageCache, which stores a rendered HTML page
    in RAM.

    This is intended to be used as a higher level cache
    than RAMCacheManager.  Pages are stored complete with
    their headers.
    """

    implements(IPageCacheManager)
    __ac_permissions__ = (
        ('View management screens', ('getSettings','manage_main',)),
        ('Change cache managers', ('manage_editProps', 'manage_invalidate', 'manage_purge'), ('Manager',)),
        )

    manage_options = (
        {'label':'Properties', 'action':'manage_main'},
        ) + CacheManager.manage_options + SimpleItem.manage_options

    meta_type = 'Page Cache Manager'
    security = ClassSecurityInfo()

    def __init__(self, ob_id):
        self.id = ob_id
        self.title = ''
        self._settings = {
            'threshold': 500,
            'cleanup_interval': 60,
            'max_age': 3600,
            'active': 'on_always'
            }
        self.__cacheid = '%s_%f' % (id(self), time.time())

    def getId(self):
        ' '
        return self.id

    def setTitle(self, title):
        self.title = title

    def Title(self):
        return self.title

    security.declareProtected('Change cache managers', 'enable')
    def enable(self, option='on_always'):
        self._settings['active'] = option
        cache = self.ZCacheManager_getCache()
        cache.initSettings(self._settings)

    security.declareProtected('Change cache managers', 'disable')
    def disable(self):
        self.enable(option='off')

    def isActive(self):
        active = self._settings['active']
        if active == 'on_always':
            return True
        if active == 'on_in_production' and not Globals.DevelopmentMode:
            return True
        return False
    
    ZCacheManager_getCache__roles__ = ()
    def ZCacheManager_getCache(self):
        cacheid = self.__cacheid
        try:
            return caches[cacheid]
        except KeyError:
            cache = PageCache()
            cache.initSettings(self._settings)
            caches[cacheid] = cache
            return cache

    def getSettings(self):
        'Returns the current cache settings.'
        res = self._settings.copy()
        if not res.has_key('max_age'):
            res['max_age'] = 0
        if not res.has_key('active'):
            res['active'] = 'on_always'
        return res

    manage_main = PageTemplateFile('www/editPCM', globals(),
                                   __name__='editPCM')

    security.declareProtected('Change cache managers', 'manage_editProps')
    def manage_editProps(self, title, settings=None, REQUEST=None):
        'Changes the cache settings.'
        if settings is None:
            settings = REQUEST
        self.title = str(title)
        self._settings = {
            'threshold': int(settings['threshold']),
            'cleanup_interval': int(settings['cleanup_interval']),
            'max_age': int(settings['max_age']),
            'active': settings.get('active', 'on_always'),
            }
        cache = self.ZCacheManager_getCache()
        cache.initSettings(self._settings)
        if REQUEST is not None:
            return self.manage_main(
                self, REQUEST, manage_tabs_message='Properties changed.')

    security.declareProtected('Change cache managers', 'manage_invalidate')
    def manage_invalidate(self, paths, REQUEST=None):
        """ ZMI helper to invalidate an entry """
        for path in paths:
            try:
                ob = self.unrestrictedTraverse(path)
            except (AttributeError, KeyError):
                pass

            ob.ZCacheable_invalidate()

        if REQUEST is not None:
            msg = 'Cache entries invalidated'
            return self.manage_stats(manage_tabs_message=msg)

    security.declareProtected('Change cache managers', 'manage_purge')
    def manage_purge(self, REQUEST=None):
        """Purge all cache entries"""
        cache = self.ZCacheManager_getCache()
        cache.purge()
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?manage_tabs_message=Cache+cleared.')

Globals.InitializeClass(PageCacheManager)


manage_addPageCacheManagerForm = PageTemplateFile('www/addPCM', globals(),
                                                  __name__='addPCM')

def manage_addPageCacheManager(self, id, REQUEST=None):
    'Adds a page cache manager to the folder.'
    self._setObject(id, PageCacheManager(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

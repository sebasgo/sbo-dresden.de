##############################################################################
#
# Copyright (c) 2003-2005 struktur AG and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: queue.py 24517 2006-06-07 03:18:18Z dreamcatcher $
"""

import thread
from sets import Set
from Shared.DC.ZRDB.TM import TM as _TM, Surrogate
from Products.CMFCore.utils import getToolByName
from Products.CMFSquidTool.utils import logger
from Products.CMFSquidTool.utils import pruneAsync
from Products.CMFSquidTool.patch import wrap_method, call
from Products.CMFSquidTool.threadinglocal import local

try:
    import transaction
    def join(dm):
        transaction.get().join(dm)
except ImportError:
    # Zope 2.7
    def join(tm):
        get_transaction().register(Surrogate(tm))

class TM(_TM, local):

    _registered = 0
    _finalize = 0

    def __init__(self):
        local.__init__(self)

    def _register(self):
        if not self._registered:
            try:
                join(self)
                self._begin()
                self._registered = 1
                self._finalize = 0
            except:
                logger.exception(
                    'Unexpected exception during call to '
                    '_register (registered=%s, finalize=%s)' %
                    (self._registered, self._finalize))


class QueueRollbackSavepoint:

    def __init__(self, dm):
        self.urls = dm.urls().copy()
        self.dm = dm

    def rollback(self):
        logger.debug('Rollback Savepoint %s.' % repr(self.urls))
        return self.dm.set(self.urls)

class Queue(TM):
    """ Main Purge Queue

    - Keeps a queue of urls to invalidate per thread.
    - Sends purge requests on transaction commit.
    """

    def urls(self):
        return getattr(self, '_urls', Set())

    def savepoint(self):
        return QueueRollbackSavepoint(self)

    def set(self, urls):
        self._urls = urls

    def _reset(self):
        self.set(Set())

    def _begin(self):
        if self._registered:
            if self.urls():
                # _begin is called by _register() before _registered
                # is set to 1, so it should never get this far because
                # urls should be emptied on _abort() and _finish()
                logger.warning(
                    "'_begin' called with _registered=1 "
                    "and we still have urls. this might "
                    "be an error. dropping urls.")
        # Just to make sure we call reset again
        self._reset()

    def _abort(self):
        # Throw away all catched urls for this thread
        self._reset()

    def _finish(self):
        # Process any pending url invalidations. This should *never*
        # fail.
        for url in self.urls():
            pruneAsync(url, purge_type='PURGE')
        # Empty urls queue for this thread
        self._reset()

    def append(self, url):
        self._register()
        self._urls.add(url)

    def queue(self, ob):
        st = getToolByName(ob, 'portal_squid', None)
        if st is None:
            return
        ob_urls = st.getUrlsToPurge(ob)
        purge_urls = st.computePurgeUrls(ob_urls)
        for ob_url in purge_urls:
            self.append(ob_url)

queue = Queue()

def reindexObject(self, idxs=[]):
    """Reindex Object

    Queue PURGE url and call original method.
    """
    queue.queue(self)
    return call(self, 'reindexObject', idxs=idxs)

def unindexObject(self):
    """Unindex Object

    Queue PURGE url and call original method.
    """
    queue.queue(self)
    return call(self, 'unindexObject')

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
wrap_method(CMFCatalogAware, 'reindexObject', reindexObject)
wrap_method(CMFCatalogAware, 'unindexObject', unindexObject)

try:
    from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
    wrap_method(CatalogMultiplex, 'reindexObject', reindexObject)
    wrap_method(CatalogMultiplex, 'unindexObject', unindexObject)
except ImportError:
    logger.debug('Archetypes not found. Not patching CatalogMultiplex.')

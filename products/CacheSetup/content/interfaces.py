import zope.deferredimport

zope.deferredimport.deprecated(
    "It has been moved to Products.CacheSetup.interfaces. " 
    "This alias will be removed in a future release -- CacheFu 1.2 ?",
    ICacheRule = 'Products.CacheSetup.interfaces:ICacheRule',
    )

zope.deferredimport.deprecated(
    "It has been moved to Products.CacheSetup.interfaces. " 
    "This alias will be removed in a future release -- CacheFu 1.2 ?",
    ICacheToolFolder = 'Products.CacheSetup.interfaces:ICacheToolFolder',
    )


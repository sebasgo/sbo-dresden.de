from zope.interface import Interface
from Interface import Interface as OldInterface

class ICacheTool(Interface):
    """Just a marker interface for genericsetup now."""

class ICachePolicy(OldInterface):
    """ marker interface for cache policy folders """

class ICacheRule(OldInterface):
    """ marker interface for cache rules """

class ICacheToolFolder(OldInterface):
    """ marker interface for cache tool folders """


class IPurgeUrls(Interface):
    """Return PURGE Urls for an object."""

    def getRelativeUrls():
        """Return a list of relative URLs that should be purged.

        URLs returned by this list will be rewritten based on the
        CacheSetup proxy configuration.
        """

    def getAbsoluteUrls(relative_urls):
        """Return a list of absolute URLs that should be purged.

        URLs returned by this list will not be rewritten and passed
        as-is to the proxy server(s).

        The list of relative URLs is passed in and should not be modified.
        """


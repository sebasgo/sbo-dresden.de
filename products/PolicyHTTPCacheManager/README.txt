Policy HTTP Cache Manager

  What it does?

    - Delegates the setting of cache-related HTTP headers to CMF's
      Caching Policy Manager.

    - Will remove a previously set Last-Modified header set by code
      inside Zope if you ask it to.

  Why?

    - Because we can! *wink*

    - It's simpler to make arbitrary content to play with the Caching
      Policy Manager this way. You just associate content that plays
      with the Zope's 'Cacheable' interface to this Caching Manager
      and it will automatically set the HTTP headers at the right
      time.

    - Some code inside Zope (namely, FS{Image|File} and OFS.Image)
      will unconditionally set a 'Last-Modified' header. According to
      Geoff Davis this might be harmful when Internet Explorer is
      used so 'Caching Policy Manager' grew a setting to control the
      explicit setting of this header. However there was no way to
      explicitly remove a previously set header.

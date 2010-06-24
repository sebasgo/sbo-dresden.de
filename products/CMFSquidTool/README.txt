CMFSquidTool

  It is a CMF Tool to purge a proxy's cache. It works with both
  Squid and Enfold Enterprise Proxy. It is accessible through
  the Zope Management Interface.

  This product is covered by a license. See LICENSE.txt

Installation:

 1. a) for Squid proxy caches

    Squid does not allow you to purge objects
    unless it is configured with access controls in
    squid.conf. First you must add something like

        acl PURGE method purge
        acl localhost src 127.0.0.1
        http_access allow purge localhost
        http_access deny purge

    The above only allows purge requests which
    come from the local host and denies all other
    purge requests.

    Restart Squid after you did this reconfiguration.

    b) for Enfold Enterprise Proxy (EEP) caches

    If CMFSquidTool is running on the same machine as EEP,
    no extra configuration of EEP is necessary.

    If CMFSquidTool is running on a different machine, you
    will need to add a line to your EEP configuration file.
    The EEP configuration file is located in the EEP application
    directory and is called 'eep.ini'.

    Using a text editor, add a line like this to your eep.ini file,
    with the IP addresses of the machines you wish to be able to
    purge the cache.

        remote_admin 127.0.0.1 123.45.67.89 1.2.3.4

 2. Zope Product

    Extract this tarball into your Zope Product folder
    and restart Zope when you did so.

    Afterwards install the tool into your portal by
    using the quickinstaller tool.


Configuration:

 1. ZMI Setup

    Enter the url to your portal root like it is
    accessable through squid, into the field inside
    the Squid Cache Urls tab of the portal_squid
    tool.

    If you have Enfold Enterprise Server, a similar interface
    is available from the Plone Control Panel.


Original version by Simon Eisenmann <simon@struktur.de>.

Modifications for Enfold Enterprise Proxy by:

 - Neil Kandalgaonkar <neilk at enfoldsystems.com>
 - Robert Rottermann <robert at redcor.ch>
 - Sidnei da Silva <sidnei at enfoldsystems.com>

--
(c) 2003-2005, struktur AG. All rights reserved.

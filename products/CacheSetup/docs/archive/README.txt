
[August 15, 2007 - archived for future reference - newbery]
___________________________________________________________



See CacheSetup/docs/audiences.rest for more documentation

Tested with Plone 2.5, Plone 2.1.3, Plone 2.1.2, Plone 2.0.5 and CMF 1.4.8/1.5/1.6

IMPORTANT: If you have a pre-beta CacheFu installation, you MUST
uninstall it before putting any of the CacheFu code into your Products
directory.

If you have a 1.0 beta CacheFu installed, you will need to uninstall
then install.  DON'T REINSTALL - reinstalling will not trigger updates
of the header sets and you will be stuck with a bunch of IE problems.

Quick start:
------------

* Make sure you are using Plone 2.0, 2.1, or 2.5

* IMPORTANT: Uninstall any previous version of CacheFu you have installed

* Stop Zope

* Copy CacheSetup, PageCacheManager, CMFSquidTool, and 
  PolicyHTTPCacheManager into your Products directory
  (You do not need MemcachedManager)

* Start Zope

* Use the QuickInstaller to install CacheSetup (you do not need to
  install any other products)

* As a manager, go to Site Setup, select Cache Configuration Tool, 
  and then indicate your site's configuration

If you are using squid:

* Change the settings in squid/squid.cfg to reflect your system.  Run
  squid/makeconfig to generate your squid/apache files

Alternatively, you can use Nic Benders' makefile to generate the squid
files -- you will need to edit the file to set correct ZOPELIB and
PYTHON variables.

------------

See CacheSetup/docs/audiences.rest for more documentation.  There is
also some older (deprecated) documentation below that should give you
an idea of how things work internally.

There are tips below for getting squid to work.  Please remember that
I do not have time to help everyone set up squid.

Geoff




Configuring Squid
-----------------

The makeconfig file in the squid directory generates a basic squid
configuration file, squid.conf.  There are also several squid helper
applications included:

 - iRedirector.py

 - squidRewriteRules.py
 
 - squidAcl.py

 The file 'makeconfig' generates a deploy script that will copy the 
files to the appropriate locations and set permissions on them.

 'iRedirector.py' and 'squidRewriteRules.py' together form a squid
redirector.  These files are used by squid to rewrite URLs when
handing off to Zope.  The files were originally written by Simon
Eisenmann (longsleep) and modified to have a more mod_rewrite-like
syntax by Florian Schulze (fschulze).

 'squidAcl.py' is used to test whether a request is being made by an
authenticated user (in which case we should not cache the response) or
if the request is a conditional GET  with an If-None-Match header
(also should not be served up by squid).

Squid Debugging Tips
--------------------

 Buy and read "The Definitive Guide to Squid":http://www.amazon.com/gp/product/0596001622&tag=phdsorgsciencmat

 Squid's logs are a good place to start looking if you have problems
with it.  

 Make sure you initialize the squid cache the first time you run squid 
(use 'squid -z').

 While debugging, it's a good idea to run squid from the command line
and tell it to echo problems to the console.  Start squid using
'/usr/sbin/squid -d1'

 To stop squid from the command line, use '/usr/sbin/squid -k kill',
and to reconfigure squid after you have modified 'squid.conf', use
'/usr/sbin/squid -k reconfigure'.

 If squid won't start, check '/var/log/squid/cache.log' to see why.  

 If squid blocks your access to a particular page, uncomment the line
'debug_options ALL, 1 33,2' in squid.conf, reconfigure squid, then
look at '/var/log/squid/cache.log'.

 The redirector and external ACL python scripts can all log their
activity.  Set 'debug=1' in each of the .py files to see what they are
up to.

 Use the LiveHTTPHeaders FireFox extension to see if you are getting
cache hits for your pages.  If there is a cache hit, you will see
'X-Cache: HIT from yourserver'; otherwise you will see 'X-Cache: MISS
from yourserver'.  If you are getting misses, try clearing your
browser cache.

 Note that a MISS can mean either that squid tried to retrieve your
page from the cache but did not find it or that squid has been
disallowed from responding to the type of request you made (e.g. you
were authenticated or making a conditional GET with an
'If-None-Match' request). 












THE TEXT BELOW IS OUT OF DATE BUT SHOULD GIVE SOME INSIGHT INTO HOW
CACHE-FU WORKS.

Caching Dynamic Content in the CMF
==================================

  Geoff Davis - September 19, 2005 - geoff at geoffdavis dot net

  
Overview
--------

 Proxy caching is a way to dramatically speed up a web site.  The
products and tutorial below will show you how to set up your site in
such a way that:
 
 1. Users to not receive stale pages when your site's content changes

 2. The load on Zope is minimized, and

 3. Overall bandwidth is reduced.

Who This Is For
---------------

 This strategy is a bit complicated to implement and is still fairly
new.  If you are a newbie, this is not for you (though you may find
the background section below useful).  You should have experience
setting up Zope behind Apache, and ideally should have some experience
with Squid.

Background
----------

 To achieve our goals, we will be working with 2 basic properties of
the HTTP protocol: caching headers and conditional GETs.

HTTP headers and caching
------------------------

 HTTP headers are used to control when and where web pages are cached.
The header that matters most is the Cache-Control header, which
consists of a list of cache parameters.  The main values we will be
working with are as follows:

 max-age -- This tells browsers how long they can cache content before
they have to check back with the server to make sure the content is
up-to-date.  For static content that is unlikely to change very often
(images, css, javascript), we will typically set a long max-age so
that browsers will store these and neither re-request them nor check
to see if their copies are current very often.

 s-maxage -- This tells proxy caches how long they can cache content.
If no value is specified, the proxy cache will use max-age.  For
dynamic content (views of documents, etc), we will send browsers that
the content is immediately stale (max-age = 0) and will tell our proxy
cache (Squid) to hold on to the content for awhile (e.g. s-maxage =
7200).  When we change our documents, we will tell Squid to remove the
old, cached versions.

 must-revalidate -- This tells browsers that they must check back with
the server to see if pages are up to date before serving anything in
their local cache that is stale.

 public -- This tells proxy caches that they can cache content even if
they otherwise wouldn't be able to (i.e. if the user is
authenticated).  We'll indicate that static content (images,
javascript, css, etc) is public.

 private -- This tells proxy caches not to cache content.  We'll
indicate that personalized pages and anything requiring authorization
is private.

Conditional GETs and browser caching
------------------------------------

 When a browser first requests a page, it makes an HTTP request like the following::

  GET /some/page/on/the/site

 When the server responds, it has the option to send back several
useful pieces of information about the object, including the time at
which the object was last modified (present in almost all requests)
and an ETag (optional; included using a Caching Policy in the CMF).
The browser can use these pieces of information in subsequent requests
to see if the page it is currently holding in its cache is up to date.

 When re-visiting a web page, the browser first checks the
Cache-Control header for a max-age parameter to see if the page it is
holding has expired.  If there is no max-age header, the browser then
checks the Expires header for an expiration date.  If the content has
not yet expired, the browser serves up the page from its cache.  If
the page has expired, the browser sends a conditional GET instead of a
regular GET request.  The conditional GET looks like the following::

  GET /some/page/on/the/site
  If-Modified-Since: [last-modified date for the page the browser currently has in cache]
  If-None-Match: [the ETag for the page the browser has in cache]

 The server has 2 options: First, it can respond as it usually would
 to a GET request by sending the page to the browser along with a
'Status: 200 (OK)' header.  Alternatively, it can do something
smarter: it can examine the date and ETag for the user's cached
content, see if the user is holding the page that the server would
serve anyway, and if s/he is, it can send an empty page with a Status:
304 (Not Modified) header. 
 
 This new option is a win for all parties concerned: the server does
not have to render the page, so the server load is reduced, nor does
not have to send the full page, so bandwidth is reduced.  The user, in
turn, gets a much faster response from the server, and hence
experiences a more responsive site.  CMFCore has recently been
modified to allow Page Templates to send 304s under the appropriate
circumstances.

Conditional Requests and the WinInet Cache (for Internet Explorer users)
------------------------------------------------------------------------

Internet Explorer takes advantage of the caching services provided by
Microsoft Windows Internet Services (WinInet). WinInet allows the user
to configure the size and behavior of the cache. The vast majority of
users leave the setting at the default of Automatically, but we still
have the "Every visit to the page", "Every time you start Internet
Explorer" and "Never" options.

The most important fact to keep in mind is that these four options
mostly impact the behavior when there are no caching headers on the
HTTP responses; when caching headers are present, Internet Explorer
will always respect them (however, some bugs on Internet Explorer
seams to create real troubles in practice).

The Automatically setting bears some explanation. How can WinInet know
if the cached resource is fresh when no caching directives were
provided on the server's HTTP response? The answer is that WinInet
can't know for sure and a Heuristic process is followed to make a
"best guess" effort. In the Automatically state, the Heuristic will
issue a conditional request unless all of the following criteria are
met:

 The cached resource bears a Content-Type that begins with image/.

 The cached resource has a Last-Modified time.

 The URL to the cached resource does not contain a question mark.

 The cached resource has been conditionally requested at least once
within the most recent 25 percent of its overall age in the cache
(this one is evil to debug, isn't it :-) 

If all of the criteria above are met, no request is made. However,
seams that there are bugs on Internet Explorer cache engine that seams
to create a similar behavior, where the page is requested but an old
copy of the page is used from the cache.

There are also some situations where Internet Explore will ignore a
cache and always make a new request. One example is the use if images
which are inserted via innerHTML (see
http://www.bazon.net/mishoo/articles.epl?art_id=958 for more
information).

IE 5.5+ introduces some proprietary Cache-Control tokens, pre-check
and post-check, that let IE ignore the headers to some extent (see
http://msdn.microsoft.com/workshop/author/perf/perftips.asp).
Fortunately, this behavior can be turned off by setting Cache-Control:
pre-check=0, post-check=0 (and It was added to CMF caching polices
recently too).

ETags
-----

 Most of the discussion about caching and Plone has made use of
time-based caching.  In time-based caching, the server sends
'Last-Modified', 'Expires', and 'Cache-Control: max-age' headers with
content.  Browsers serve up content until it expires, then do
conditional GETs with an 'If-Modified-Since' header.  This kind of
caching enables browsers to cache content for a specified length of
time.  This kind of caching is unsuitable for any kind of content that
might be personalized because the browser has no way of telling the
server whether it has an anonymous view of content or a personalized
one, nor can the browser distinguish between content personalized for
different users.  To cache personalized content, we need more
information.

 An ETag is an arbitrary string that the server uses to determine
whether or not content is fresh.  An ETag should be designed to have
the property that if the ETag for a cached view of an object matches
the object's current ETag, then the view the server would generate for
the object should be the same as the view in cache.

 We will use ETags to enable browsers to cache personalized content
 and to then handle it appropriately.  The key to doing so is to use
an ETag generator that serves up a different ETag any time the content
in question changes.  The kinds of changes we are concerned with are 
 
 1. The content changes 
 
 2. The user changes (e.g. sh/e logs in or out, or somebody new logs
    in and hence requires a different personalized view).

 The ETag we will use for content object views is a string consisting
of the following:

 'user name of the currently authenticated member' + delimiter +
'modification time in seconds for the content object being viewed' +
delimiter + 'current time rounded to the nearest hour'

 The first part of the tag ensures that if the user logs out or
changes, then the ETag will change.  The second part of the tag
ensures that if the content object changes, the ETag will change.  The
third part of the tag ensures that the tag will time out after an hour
at most.

 To be thorough, we might also want to include things like a hash of
the current query string, and / or a hash of the contents of
REQUEST.form.  Alternatively, we can simply arrange to not respond to
a REQUEST with form variables from cache.

Our Cache Strategy
------------------

 Our general strategy is as follows:

 1. We put Squid in front of Zope.  Squid will handle all static
    content as well as initial requests for dynamic content from
anonymous clients.

 2. We set up caching policies for dynamic content in the CMF.  The
  caching policies will set HTTP headers on our pages that ensure that 
  
  a. Squid stores content for an appropriate amount of time, 
  
  b. That browsers cache pages for an appropriate amount of time, 
  
  c. That browsers check back with the server to make sure their
  cached content is fresh, and 
  
  d. If their content is fresh, that they don't request an entire new
 page (thanks to recent improvements in CMFCore).
 
 3. We cache dynamic content (views of documents, etc) for anonymous
visitors in Squid.  CMFSquidTool will be used to purge old views
from Squid when content objects change.

 4. We will also cache dynamic content in RAM using PageCacheManager.
PageCacheManager will be used to ensure that conditional GETs from
clients are handled rapidly when content changes.

 Here are the layers of cache we use and what each layer does:

 1. Squid: Squid handles all static content (images, javascript, css,
etc) and all initial requests for dynamic content by anonymous
users.  Squid will not serve up personalized content (we will ensure
that such content is cached in the user's browser) nor will it handle
some kinds of subsequent requests (Squid doesn't understand ETags).

 2. PageCacheManager (optional): PageCacheManager will handle
conditional GETs that use ETags and will cache pages from both
anonymous and authenticated users. PageCacheManager's primary benefit
is its efficient handling of conditional GETs from clients when a
content object changes.

 3. CMFCore: Recent modifications to CMFCore let Zope handle
conditional GETs efficiently.  When a user visits a page that s/he
has in cache, Zope will return an empty page with a 304 status (Not
Modified) in response if the content has not changed instead of the
full page and a 200 (OK) status.

 4. CMFSquidTool: CMFSquidTool hooks the reindex method on content
objects.  When an object changes, CMFSquidTool purges views of the
content from Squid to make sure Squid is not holding on to stale
content.

 The life cycle of a view of a content object is as follows:

 1. An anonymous user requests an initial view of a document.  If the
document view is in Squid, Squid serves it up.  If not, Squid
hands off to Zope, Zope serves up the request, and Squid stores it for
future requests.

 2. The anonymous user re-visits a page.  The user now has the page in
her local browser cache, so the browser does a conditional GET:
basically it asks the server for the page only if it differs from the
page the browser has in cache.  Squid can't handle this kind of
conditional GET (since we use ETags), so the request gets handed to
Zope.   If PageCacheManager is installed, it will handle the request:
if the object has not changed since the user last accessed the view,
PageCacheManager will send a 304 (Not Modified) status header and an
empty page; if the object has changed, PageCacheManager will serve the
page from RAM if it has a copy or will regenerate the page and cache
it.  Alternatively, if PageCacheManager is not installed, the CMF will
send a 304 if the object has not changed and will re-render and send
the full page to the user if it has.

 3. When an object changes, CMFSquidTool will purge old views of the
object from Squid's cache.  The object's ETag will change, too, so
PageCacheManager will no longer serve the old, cached version, and CMF
will no longer respond to conditional GETs for the old object with a
304.

Tools Required
--------------

 You will need Squid, the CacheSetup product from the CacheFu project
in svn collective, and CMF 1.4.9 (for Plone 2.0.x) or 1.5.5 (for Plone
2.1.x).  

 If CMF 1.4.9 / 1.5.5 or Plone 2.1.2 are not yet released, grab CMF from svn:

 CMF 1.4: 'svn co svn://svn.zope.org/repos/main/CMF/branches/1.4'

 CMF 1.5: 'svn co svn://svn.zope.org/repos/main/CMF/branches/1.5'

 CacheFu contains a patched version of CMFSquidTool (don't use the one from Enfold).

 The LiveHTTPHeaders extension for FireFox
("http://livehttpheaders.mozdev.org":http://livehttpheaders.mozdev.org)
is invaluable for diagnosing cache problems. The Fiddler tool for IE
("http://www.fiddlertool.com/fiddler/":http://www.fiddlertool.com/fiddler/) 
provides similar functionality for IE. 

Configuring Squid
-----------------

 CacheFu contains a basic Squid configuration file, squid.conf.  The
file is set up for two different types of configurations: (1) direct
access to Squid, and (2) Squid behind apache.  Files for these 2
different configurations are contained in the Squid_direct directory
and the squid_behind_apache directory, respectively. Look at the
directory appropriate to your setup.

 The 'squid.conf' file and the following discussion assumes that
Squid's configuration files are in '/etc/squid/', Squid's binary is in
'/usr/sbin/squid', Squid's logs are in '/var/log/Squid', and that
Squid runs as user 'squid'. There are several Squid helper
applications included:

 - iRedirector.py

 - redirector_class.py
 
 - squidAcl.py

 Copy these to '/etc/squid', and make sure that user 'squid' has read
and execute access for them.  

 'iRedirector.py' and 'redirector_class.py' together form a Squid
redirector.  These files are used by Squid to rewrite URLs when
handing off to Zope.  The files were originally written by Simon
Eisenmann (longsleep) and modified to have a more mod_rewrite-like
syntax by Florian Schulze (fschulze).

 'squidAcl.py' is used to test whether a request is being made by an
authenticated user (in which case we should not cache the request) or
if the request is a conditional GET  with an If-None-Match header
(also should not be served up by Squid).

 You will need to customize 2 files: put information about your site's
URL in squid.conf and configure redirector_class.py to do appropriate
redirection.

Squid Debugging Tips
--------------------

 Squid's logs are a good place to start looking if you have problems
with it.  

 While debugging, it's a good idea to run Squid from the command line
and tell it to echo problems to the console.  Start Squid using
'/usr/sbin/squid -d1'

 To stop Squid from the command line, use '/usr/sbin/squid -k kill',
and to reconfigure Squid after you have modified 'squid.conf', use
'/usr/sbin/squid -k reconfigure'.

 If Squid won't start, check '/var/log/squid/cache.log' to see why.  

 If Squid blocks your access to a particular page, uncomment the line
'debug_options ALL, 1 33,2' in squid.conf, reconfigure Squid, then
look at '/var/log/squid/cache.log'.

 The redirector and external ACL python scripts can all log their
activity.  Set 'debug=1' in each of the .py files to see what they are
up to.

 Use the LiveHTTPHeaders FireFox extension to see if you are getting
cache hits for your pages.  If there is a cache hit, you will see
'X-Cache: HIT from yourserver'; otherwise you will see 'X-Cache: MISS
from yourserver'.  Note that a MISS can mean either that Squid tried
to retrieve your page from the cache but did not find it or that Squid
has been disallowed from responding to the type of request you made
(e.g. you were authenticated or making a conditional GET with an
'If-None-Match' request)

Installing Caching Policies
---------------------------

 We use CMF's Caching Policy Manager to set headers for the pages we
will be serving.  Install the CacheSetup product using the
QuickInstaller.  CacheSetup installs the following basic caching
policies (go to the ZMI to 'caching_policy_manager' to see them):

Policies for Static Content

 anonymous_cache_template -- This policy is for static page templates
on the site that are not associated with a content object (e.g.
accessibility-info).  Content served to anonymous visitors is cached
in Squid for ANON_PAGE_TEMPLATE_CACHE_DURATION_DAYS (default = 1 day);
browsers are told that the content is immediately stale.  ETags are
generated using the script getPageTemplateETag.py.  The script
getPageTemplateETag.py is used to generate ETags.  The script
getAnonPageTemplatesToCache.py returns a list of page template ids for
which this policy should apply.

Policies for Dynamic Content

 anonymous_cache_policy -- This policy is for content object views
served to  anonymous visitors.  Content is cached in Squid for
ANON_PAGE_TEMPLATE_CACHE_DURATION_DAYS (default = 1 day); browsers are
told that the content is immediately stale.  ETags are generated by
the script getContentETag.py.  The script doCache.py is used to
determine which templates to cache.

 authenticated_cache_policy -- Same as anonymous_cache_policy, but
content is flagged as private and is not cached in Squid.

 These policies should be a good starting point.  You can customize
the various ETag generating scripts and policy membership scripts (in
CacheSetup/skins/cache_setup) to suit your needs.

Debugging
---------

 LiveHTTPHeaders lets you see what (if any) headers
CachingPolicyManager has set on your content.  If CachingPolicyManager
has set headers on your content, there will be a header labeled
"X-Cache-Headers-Set-By: CachingPolicyManager" in the server's
response.

 A few things to note:

 - CacheSetup requires CMF 1.4.9 or 1.5.5 (or the current CMFCore from
svn)

 - CachingPolicyManager only sets cache headers on page templates.
Some content objects (Documents, for example), when accessed
directly via a URL, implicitly call a view template.  Others, such as
File objects or ATFile objects do not (they render their the result of
their __call__ method, which is not a page template)

 - Zope's HTTP compression will disable the caching policy manager
headers (and causes other problems as well).  The file
enableHTTPCompression.py in Plone's skins/plone_scripts toggles Zope's
compression.  The version of enableHTTPCompression.py included in the
CacheSetup skin turns HTTP compression off in Plone.

 - There was a bug fixed on Internet Explorer 6 service packs that
where content with "Content-Encoding: gzip" is always cached
although you use "Cache-Control: no-cache"
(http://support.microsoft.com/default.aspx?scid=kb;en-us;326489). It
is another good reason to use enableHTTPCompression.py shipped with
CacheFu.

 - The Enable 304s box must be checked for a caching policy for Zope
to return a Status 304 response.  CacheSetup turns on 304s upon
installation, but if you add your own policies, you will need to be
sure to explicitly turn on 304 handling for your policies.

Installing PageCacheManager
---------------------------

 Install PageCacheManager by placing it in your Products directory (no
other installation is needed).  PageCacheManager will cache pages that
have a caching policy associated with them that has the Enable 304s
flag set.    Create a PageCacheManager instance in the ZMI (give it an
id of page_cache_manager, say) and then associate your content view
page templates with the cache manager by modifying their .metadata
files.  You will need something like the following in the .metadata
files for your view templates::

  [default]
  title=Title of page template here
  cache=page_cache_manager

Testing PageCacheManager
------------------------

 Visit a content object view that you have associated with the
PageCacheManager.  The initial visit should load the page into the
cache.  Now clear your browser's cache and revisit the page with
LiveHTTPHeaders enabled.  You should see the header 'X-PageCache:
HIT'.  Now edit the content object and revisit the page.  You should
receive an updated version of the page.

 If you do not see an 'X-PageCache: HIT', verify that there is a
Caching Policy associated with the page.  The easiest way to check
this is to verify that the header "X-Cache-Headers-Set-By:
CachingPolicyManager" is present in your response headers.  If there
is a caching policy present, make sure it has the Enable 304s box
checked.  If that is the case, make sure that the view is in fact
associated with the PageTemplateCache: visit page_template_cache in
the ZMI, click the Associate tab, check 'Associated with this cache
manager' and click the Locate button to verify the association.


Installing and Configuring CMFSquidTool
---------------------------------------

 Install CMFSquidTool from the CacheFu distribution (it contains
several useful patches that the Enfold version does not yet have).  It
will create a tool called 'portal_squid' in the ZMI.  This is where
you configure CMFSquidTool.

 For Cache type, select 'Squid'.  

 If you have Squid directly responding to requests:

 - For Portal URLs for the cache, enter
'http://your.domain.name.here'.  If it is possible to access your
site through multiple URLs (e.g. 'http://www.mysite.com',
'http://mysite.com', 'https://www.mysite.com'), enter all of those
URLs.

 - For URLs to purge, enter::
 
  python:object.getUrlsToPurge(setup='squid_direct')

 If you have Squid behind Apache:

 - For Portal URLs for the cache, enter 'http://127.0.0.1:3128'

 - For URLs to purge, enter::
 
   python:object.getUrlsToPurge(setup='squid_behind_apache')
   
Customize the script getSiteUrls.py in CacheSetup/skins/cache_setup so
that it returns your site's URLs.

Testing CMFSquidTool
--------------------

 Visit a document that is cached by Squid as an anonymous user.  Make
sure you get an 'X-Cache: HIT' header in response (you may need to
make a second visit).

 If you have Squid responding directly to requests:

 - Enter the URL you just visited relative to the portal root in the
"Purge URL" box and click Go!.  For example, for
http://mysite.com/foo/bar, enter "foo/bar".

 If you have Squid behind apache:
 
 - Enter the prefix 'http/your.site.url/' followed by URL you just
visited relative to the portal root in the 'Purge URL' box and
click 'Go!'.  For example, for 'http://mysite.com/foo/bar', enter
'http/mysite.com/foo/bar'.  

 You should see '200 http://someurlhere' on the next page.  The 200
means that CMFSquidTool successfully purged the content.  If you get a
404, something is wrong (you already purged the page from cache, the
page was not in cache or you do not have permission to purge pages on
cache).

Notes
-----

 - xiru points out that if you are running squid and zope on separate
boxes, you should make sure they have synchronized clocks.  Use the
ntp protocol to keep them in sync.

 - It appears that there is a weird IE bug connected with the
Last-Modified header.  If you have a page with a last-modified
header and cache-control: max-age: 0, under some circumstances, IE
will (properly) determine that the page in cache is stale and request
a new copy.  However, it will then render the old cached page instead
of the new one.  P-J Grizel speculates that this might have to do with
a bug in how IE parses the time zone in the last-modified header. xiru
believes that this bug has relation with Internet Explorer cache
cleanup implementation and says that it does NOT happen on Firefox.
For now, I am disabling the last-modified header in the caching
policies.

  - Using the standard ETags to cache content pages can result in
stale portlets and navigational elements.  To overcome this issue
an optional behavior has been added to CacheSetup that allows the ETag
for content objects and page templates to change whenever any content
object in the portal is modified in any way (other than changes made
to local roles and changes made in the ZMI).  This is accomplished by
adding the last time that a persistent change was made to the
portal_catalog to the ETag.  The result is that, when this feature is
enabled, any changes to content objects will change the ETags for all
content objects.  This is particularly useful for sites with a very
high proportion of read vs. write operations which want all portlets
and navigation to update immediately when a change is made.
Unfortunately, anonymous users visiting a page for the first time may
still get a page with stale portlets served from a proxy cache
(squid), but all authenticated users, all users revalidating a cached
page with an ETag, and all users not using a proxy cache will be
served a page with updated portlets.  To enable this feature simply
uncomment the appropriate line in getContentETag.py and/or
getPageTemplateETag.py.

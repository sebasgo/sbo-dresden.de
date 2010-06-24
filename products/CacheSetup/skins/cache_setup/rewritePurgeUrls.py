## Script (Python) "rewritePurgeUrls"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=relative_urls,domains
##title=Custom rewrite of purge url paths

# Rewrite the purge urls in case the request paths passed to the cache proxy 
# are different than the relative urls in the Zope virtual host context.
# We put this here to make it easier to adjust this behavior for custom
# cache proxy setups
#
# The old default "squid_behind_apache" setup assumes urls passed
# to Squid from Apache are of the form:
# [squid_url]/[protocol]/[host]/[port]/[path]
#

prefixes = []
for d in domains:
    protocol = d[0]
    host = d[1]
    split_host = host.split(':')
    host = split_host[0]
    port = split_host[1]
    prefixes.append('%s/%s/%s/' % (protocol, host, port))
relative_urls = [prefix+url for prefix in prefixes for url in relative_urls]
return relative_urls

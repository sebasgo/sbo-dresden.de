# Basic configuration

# By default we use an HTTP/1.1 purge request as according to Squid
# developers, all versions support PURGE via HTTP/1.1
# NOTE: this is a change from the previous default of using HTTP/1.0
# which breaks PURGE requests when a port number is in the full url.
#USE_HTTP_1_1_PURGE = False
# EnfoldServer also ships with 1.1 purging enabled as it works much better
# with IIS, particularly with connection:close semantics.
USE_HTTP_1_1_PURGE = True

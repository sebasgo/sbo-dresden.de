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
$Id: utils.py 38374 2007-02-26 14:27:57Z dreamcatcher $
"""

import sys
import socket
import httplib
import urlparse
import threading
import Queue
import logging
from thread import get_ident
from config import USE_HTTP_1_1_PURGE
import time

class Logger(object):

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def __getattribute__(self, name):
        if name in ('logger',):
            return object.__getattribute__(self, name)
        def wrapper(*args, **kw):
            if __name__ == '__main__' and args:
                print args[0]
            return getattr(self.logger, name)(*args, **kw)
        return wrapper

logger = Logger('CMFSquidTool')

class Connection(httplib.HTTPConnection):

    def __init__(self, host, port=None, strict=None, scheme="http", timeout=5):
        self.scheme = scheme
        if scheme == "http":
            self.default_port = httplib.HTTP_PORT
        elif scheme == "https":
            self.default_port = httplib.HTTPS_PORT
        else:
            raise ValueError, "Invalid scheme '%s'" % (scheme,)
        httplib.HTTPConnection.__init__(self, host, port, strict)
        self.timeout = timeout

    def connect(self):
        # We want to connect in normal blocking mode, else Python on Windows
        # will timeout even for 'connection refused' style errors (fixed in
        # Python 2.4 on Windows)
        if self.scheme == "http":
            httplib.HTTPConnection.connect(self)
        elif self.scheme == "https":
            # Clone of httplib.HTTPSConnection.connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            key_file = cert_file = None
            ssl = socket.ssl(sock, key_file, cert_file)
            self.sock = httplib.FakeSocket(sock, ssl)
        else:
            raise ValueError, "Invalid scheme '%s'" % (self.scheme,)
        # Once we have connected, set the timeout.
        self.sock.settimeout(self.timeout)

XERROR = ('x-squid-error',)

# Strategy for purging:
# Most purging is done 'asynchronously' - ie, Zope requests a purge, but
# doesn't want to block until the response is sent.  About the only use
# of a synchronous purge is explicitly via the ZMI, in which case we block
# so we can let the user see the result.
# The manual case is the exception - we don't go to huge efforts to optimize
# this case - ie, no attempt at connection-pooling, etc.
# The strategy for the async case is:
# * Each remote host gets a queue and a worker thread.
# * Each worker thread manages its own connection.  While it can not
#   establish a connection, the queue is not processed at all.  Once a
#   connection is established, the queue is purged one item at a time.
#   Should the connection fail, the worker thread again waits until a
#   connection is possible.
# This means that connections are never pooled or shared in any way (except
# as a side-effect of all requests for a single host being processed by the
# same worker-thread).
class Worker(threading.Thread):

    def __init__(self, queue, host, scheme, producer):
        self.host = host
        self.scheme = scheme
        self.producer = producer
        self.queue = queue
        self.stopping = False
        super(Worker, self).__init__(name="PurgeThread for %s://%s" % (scheme, host))

    def getConnection(self, url):
        # Blocks until either a connection is established, or
        # we are asked to shut-down.  Includes a simple strategy for
        # slowing down the retry rate, retrying from 2 seconds to 2 minutes
        # until the connection appears.
        wait_time = 1
        while not self.stopping:
            try:
                return self.producer.getConnection(url)
            except socket.error, e:
                # max wait time is 2 minutes
                wait_time = min(wait_time * 2, 120)
                logger.debug("Error %s connecting to %s - will "
                             "retry in %d second(s)", e, url, wait_time)
                for i in xrange(wait_time):
                    if self.stopping:
                        break
                    time.sleep(1)
        return None # must be stopping!

    def run(self):
        logger.debug("%s starting", self)
        # Queue should always exist!
        q = self.producer.queues[(self.host, self.scheme)]
        connection = None
        try:
            while not self.stopping:
                item = q.get()
                if self.stopping or item is None: # Shut down thread signal
                    logger.debug('Stopping worker thread for '
                                 '(%s, %s).' % (self.host, self.scheme))
                    break
                url, purge_type = item

                # Loop handling errors (other than connection errors) doing
                # the actual purge.
                for i in range(5):
                    if self.stopping:
                        break
                    # Get a connection.
                    if connection is None:
                        connection = self.getConnection(url)
                        if connection is None: # stopping
                            break
                    # Got an item, prune it!
                    try:
                        resp, msg, err = self.producer._pruneUrl(connection,
                                                                 url, purge_type)
                        # worked! See if we can leave the connection open for
                        # the next item we need to process
                        # NOTE: If we make a HTTP 1.0 request to IIS, it
                        # returns a HTTP 1.1 request and closes the
                        # connection.  It is not clear if IIS is evil for
                        # not returning a "connection: close" header in this
                        # case (ie, assuming HTTP 1.0 close semantics), or
                        # if httplib.py is evil for not detecting this
                        # situation and flagging will_close.
                        if not USE_HTTP_1_1_PURGE or resp.will_close:
                            connection.close()
                            connection = None
                        break # all done with this item!

                    except (httplib.HTTPException, socket.error), e:
                        # All errors 'connection' related errors are treated
                        # the same - simply drop the connection and retry.
                        # the process for establishing the connection handles
                        # other bad things that go wrong.
                        logger.debug('Transient failure on %s for %s, '
                                     're-establishing connection and '
                                     'retrying: %s' % (purge_type, url, e))
                        connection.close()
                        connection = None
                    except:
                        # All other exceptions are evil - we just disard the
                        # item.  This prevents other logic failures etc being
                        # retried.
                        connection.close()
                        connection = None
                        logger.exception('Failed to purge %s', url)
                        break
        except:
            logger.exception('Exception in worker thread '
                             'for (%s, %s)' % (self.host, self.scheme))
        logger.debug("%s terminating", self)

class Producer(object):

    def __init__(self, factory=Connection, timeout=30, backlog=200):
        self.factory = factory
        self.timeout = timeout
        self.queues = {}
        self.workers = {}
        self.backlog = backlog
        self.queue_lock = threading.Lock()

    def getConnection(self, url):
        (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
        # Creates a new connection - result is a connection object that is
        # *already* connected - or an exception is raised by that connection
        # process.
        conn = self.factory(host, scheme=scheme, timeout=self.timeout)
        conn.connect()
        logger.debug("established connection to %s", host)
        return conn

    def getQueueAndWorker(self, url):
        (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
        key = (host, scheme)
        if key not in self.queues:
            self.queue_lock.acquire()
            try:
                if key not in self.queues:
                    logger.debug("Creating worker thread for %s://%s",
                                 scheme, host)
                    assert key not in self.workers
                    self.queues[key] = queue = Queue.Queue(self.backlog)
                    self.workers[key] = worker = Worker(queue, host, scheme, self)
                    worker.start()
            finally:
                self.queue_lock.release()
        return self.queues[key], self.workers[key]

    def stopThreads(self, wait=False):
        # Attempts to stop all threads.  Threads stop immediately after
        # the current item is being processed.
        for w in self.workers.itervalues():
            w.stopping = True
        # incase the queue is empty, wake it up so the .stopping flag is seen
        for q in self.queues.values():
            try:
                q.put(None)
            except Queue.Full:
                # no problem - self.stopping should be seen.
                pass
        ok = True
        if wait:
            for w in self.workers.itervalues():
                w.join(5)
                if w.isAlive():
                    logger.warning("Worker thread %s failed to terminate", w)
                    ok = False
        return ok

    def pruneAsync(self, url, purge_type='PURGE', daemon=True):
        (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
        __traceback_info__ = (url, purge_type, scheme, host,
                              path, params, query, fragment)

        q, w = self.getQueueAndWorker(url)
        try:
            q.put((url, purge_type), block=False)
            msg = 'Queued %s' % url
        except Queue.Full:
            # Make a loud noise.  Ideally the queue size would be
            # user-configurable - but the more likely case is that the purge
            # host is down.
            logger.warning("The purge queue for the URL %s is full - the "
                           "request will be discarded.  Please check the "
                           "server is reachable, or disable this purge host",
                           url)
            msg = "Purge queue full for %s" % url
        return msg

    def pruneUrl(self, url, purge_type='PURGE'):
        # A synchronous one targetted at the ZMI.  - just lets exceptions happen, no retry
        # semantics, etc
        logger.debug("Starting synchronous purge of %s", url)
        try:
            conn = self.getConnection(url)
            try:
                resp, xcache, xerror = self._pruneUrl(conn, url, purge_type)
                status = resp.status
            finally:
                conn.close()
        except:
            status = "ERROR"
            err, msg, tb = sys.exc_info()
            try:
                from zExceptions.ExceptionFormatter import format_exception
            except ImportError:
                from traceback import format_exception
            xerror = '\n'.join(format_exception(err, msg, tb))
            # Avoid leaking a ref to traceback.
            del err, msg, tb
            xcache = ''
        logger.debug('Finished %s for %s: %s %s'
                     % (purge_type, url, status, xcache))
        if xerror:
            logger.debug('Error while purging %s:\n%s' % (url, xerror))
        logger.debug("Completed synchronous purge of %s", url)
        return status, xcache, xerror

    def _pruneUrl(self, conn, url, purge_type):
        (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
        __traceback_info__ = (url, purge_type, scheme, host,
                              path, params, query, fragment)
        if USE_HTTP_1_1_PURGE:
            conn._http_vsn = 11
            conn._http_vsn_str = 'HTTP/1.1'
        else:
            conn._http_vsn = 10
            conn._http_vsn_str = 'HTTP/1.0'
            # When using HTTP 1.0, to make up for the lack of a 'Host' header
            # we use the full url as the purge path, to allow for virtual
            # hosting in squid
            path = url

        logger.debug('making %s request to %s for %s.' % (purge_type,
                                                          host, path))
        conn.putrequest(purge_type, path)
        conn.endheaders()
        resp = conn.getresponse()

        xcache = resp.getheader('x-cache', '')
        for header in XERROR:
            xerror = resp.getheader(header, '')
            if xerror:
                # Break on first found.
                break
        resp.read()
        logger.debug("%s of %s: %s %s", purge_type, url, resp.status, resp.reason)
        return resp, xcache, xerror

_producer = Producer()
pruneUrl = _producer.pruneUrl
pruneAsync = _producer.pruneAsync
stopThreads = _producer.stopThreads

if __name__ == '__main__':
    # The default logger throws things away from the cmd-line!?
    logging.basicConfig()
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    for url in sys.argv[1:]:
        pruneUrl(url)
        # Prune async
        for i in range(0, 3):
            pruneAsync(url)
    raw_input('Press enter to stop the threads...')
    stopThreads(wait=True)

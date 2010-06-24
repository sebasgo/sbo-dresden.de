# This is a stand-alone test - it is not designed to run from inside
# Plone.

import sys
import os
import httplib
import unittest
import socket
import select
import Queue
import threading
import traceback
import time
import logging

try:
    # Running inside Plone/Zope - this should work?
    from Products.CMFSquidTool import utils
except ImportError:
    # Running from cmdline - no "Products" parent avaiable and top-level
    # product imports are likely to fail.  So just import utils directly.
    try:
        from CMFSquidTool import utils
    except ImportError:
        thedir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(thedir))
        import utils

# A real HTTP server that our tool connects to - but dumb in that we always
# tell it exactly what to respond with!
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_PURGE(self):
        # Get the pre-defined response from the server's queue.
        try:
            nr = self.server.response_queue.get(block=False)
        except Queue.Empty:
            print "Unexpected connection from the purge tool"
            print self.command, self.path, self.protocol_version
            for h, v in self.headers.items():
                print "%s: %s" % (h,v)
            raise RuntimeError, "Unexpected connection"

        # We may have a function to call to check things.
        validator = nr.get('validator')
        if validator:
            validator(self)

        # We may have to wake up some other code now the test connection
        # has been mad, but before the response is sent.
        waiter = nr.get('waiter')
        if waiter:
            waiter.acquire()
            waiter.release()

        # for now, response=None means simulate an unexpected error.
        if nr['response'] is None:
            self.rfile.close()
            return

        # Send the response.
        self.send_response(nr['response'])
        headers = nr.get('headers', None)
        if headers:
            for h, v in headers.items():
                self.send_header(h, v)
        data = nr.get('data', '')
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

# the server itself.
class TestHTTPServer(HTTPServer):
    allow_reuse_address = False # stuff gets weird...
    def __init__(self, *args):
        # assume we will start, and prevent issues with
        # the main thread checking before it is set.
        self.running = True
        socket.setdefaulttimeout(1) # this kinda sucks!
        self.response_queue = Queue.Queue()
        HTTPServer.__init__(self, *args)

    def get_request(self):
        # non-blocking accept
        self.socket.setblocking(0)
        try:
            select.select([self.socket], [], [])
            return self.socket.accept()
        finally:
            self.socket.setblocking(1)

    def queue_response(self, **kw):
        self.response_queue.put(kw)

    def server_bind(self):
        self.socket.settimeout(1)
        HTTPServer.server_bind(self)

    def serve(self):
        # Run until stop() is called.
        try:
            try:
                # Re rely on a timeout to prevent this blocking.
                while self.running:
                    self.handle_request()
            except SystemExit:
                pass
            except KeyboardInterrupt:
                print "** Interrupted **"
            except:
                print "Unexpected exception in test server"
                traceback.print_exc()
        finally:
            self.server_close()
            self.running = False

    def stop(self):
        # later we may need to do something fancier.
        self.running = False
        self.socket.close()

SERVER_PORT=8765
# Start a thread running our test server.
def start_proxied_server(port=SERVER_PORT, start=True):
    server_address = ('localhost', port)
    httpd = TestHTTPServer(server_address, TestHandler)
    t = threading.Thread(target=httpd.serve)
    if start:
        t.start()
    return httpd, t

# Finally the test suites.
class TestCase(unittest.TestCase):
    def setUp(self):
        # reset the producer.
        if not utils._producer.stopThreads(wait=True):
            self.fail("Threads from previous run failed to stop!")
        utils._producer.__init__()
        self.httpd = None
        self.httpt = None
        self.httpd, self.httpt = start_proxied_server()

    def tearDown(self):
        try:
            # If anything remains in our response queue, it means the test
            # failed (but - we give it a little time to stop.)
            if self.httpd is not None:
                for i in range(10):
                    if self.httpd.response_queue.empty():
                        break
                    time.sleep(0.1)
                self.failUnless(self.httpd.response_queue.empty(), "response queue not consumed")
            if not utils.stopThreads(wait=True):
                self.fail("The purge threads did not stop")
        finally:
            if self.httpd is not None:
                self.httpd.stop()
                self.httpt.join(5)
                self.httpd = None
                self.httpt = None

class TestSync(TestCase):
    USE_HTTP_1_1_PURGE = True
    def setUp(self):
        self.old_flag = utils.USE_HTTP_1_1_PURGE
        utils.USE_HTTP_1_1_PURGE = self.USE_HTTP_1_1_PURGE
        TestCase.setUp(self)

    def tearDown(self):
        utils.USE_HTTP_1_1_PURGE = self.old_flag
        TestCase.tearDown(self)

    def dispatchURL(self, path, method="PURGE", port=SERVER_PORT):
        url = "http://localhost:%s%s" % (port, path)
        return utils.pruneUrl(url, method)

    def testSimpleAsync(self):
        self.httpd.queue_response(response=200)
        resp = self.dispatchURL("/foo")

    def testAsyncHeaders(self):
        headers = {'X-Squid-Error': 'error text',
                   'X-Cache': 'a message',
        }
        self.httpd.queue_response(response=200, headers=headers)
        status, msg, err = self.dispatchURL("/foo")
        self.failUnlessEqual(msg, 'a message')
        self.failUnlessEqual(err, 'error text')
        self.failUnlessEqual(status, 200)

    def testError(self):
        self.httpd.queue_response(response=None)
        status, msg, err = self.dispatchURL("/foo")
        self.failUnlessEqual(status, 'ERROR')

class TestSync10(TestSync):
    USE_HTTP_1_1_PURGE = False

class TestAsync(TestCase):
    def dispatchURL(self, path, method="PURGE", port=SERVER_PORT):
        url = "http://localhost:%s%s" % (port, path)
        utils.pruneAsync(url, method)
        # Item should now be in the queue!
        q, w = utils._producer.getQueueAndWorker(url)
        for i in range(10):
            if q.qsize() == 0:
                break
            time.sleep(0.1)
        else:
            self.fail("Nothing consumed our queued item")
        # Make sure the other thread has actually processed it!
        time.sleep(0.1)

    def testSimpleAsync(self):
        self.httpd.queue_response(response=200)
        resp = self.dispatchURL("/foo")

    def testAsyncError(self):
        # In this test we arrange for an error condition in the middle
        # of 2 items - this forces the server into its retry condition.
        self.httpd.queue_response(response=200)
        self.httpd.queue_response(response=None)
        self.httpd.queue_response(response=200)
        resp = self.dispatchURL("/foo") # will consume first.
        resp = self.dispatchURL("/bar") # will consume error, then retry

    def testConnectionFailure(self):
        # tear down the server before the request.
        self.httpd.stop()
        self.httpt.join()

        dto = socket.getdefaulttimeout()
        socket.setdefaulttimeout(0.1)
        try:
            resp = self.dispatchURL("/foo")
            time.sleep(0.2)
        finally:
            socket.setdefaulttimeout(dto)

        # Start the server, but not the worker thread - that way we can
        # queue the response before the connection is established.
        self.httpd, self.httpt = start_proxied_server(start=False)
        self.httpd.queue_response(response=200)
        self.httpt.start()

        # We should have entered the 'connection retry' loop, which
        # will wait 2 seconds before trying again - wait at least that long.
        for i in range(25):
            if self.httpd.response_queue.empty():
                break
            time.sleep(0.1)
        # else - our tearDown will complain about the queue


# NOTE: This test runs stand-alone, and not inside Zope.
# Hence we handle test_suite() and __main__ slightly differently.
# XXX - no real reason it can't be in the main test suite - make it so!
def test_suite():
    import unittest
    suite = unittest.TestSuite()
#    suite.addTest(unittest.makeSuite(testClass))
    return suite

if __name__=='__main__':
    # logger doesn't work from cmdline!
    logging.basicConfig()
    logger = logging.getLogger()
    if '-v' in sys.argv:
        logger.setLevel(logging.DEBUG)
    utils.logger = logger
    unittest.main()

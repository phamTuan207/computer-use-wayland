import os
import socket
import socketserver
import sys
import threading
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import vm_proxy


class FakeUpstreamHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = b''
        while b'\r\n\r\n' not in data:
            chunk = self.request.recv(65536)
            if not chunk:
                return
            data += chunk
        self.server.received.append(data)
        self.request.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        try:
            while True:
                chunk = self.request.recv(65536)
                if not chunk:
                    return
                self.request.sendall(chunk)
        except OSError:
            return


class FakeUpstream(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address):
        super().__init__(address, FakeUpstreamHandler)
        self.received = []


def _serve_in_thread(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


class VmProxyTests(unittest.TestCase):
    def _run_proxy(self, upstream, authorization):
        handler = type('BoundHandler', (vm_proxy.ForwardProxyHandler,), {
            'upstream': upstream, 'authorization': authorization})
        server = vm_proxy.ThreadingProxyServer(('127.0.0.1', 0), handler)
        _serve_in_thread(server)
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)
        return server.server_address[1]

    def _connect(self, upstream, authorization):
        port = self._run_proxy(upstream, authorization)
        sock = socket.create_connection(('127.0.0.1', port), timeout=10)
        self.addCleanup(sock.close)
        sock.sendall(b'CONNECT example.com:443 HTTP/1.1\r\nHost: example.com:443\r\n\r\n')
        reply = b''
        while b'\r\n\r\n' not in reply:
            chunk = sock.recv(65536)
            if not chunk:
                break
            reply += chunk
        return sock, reply

    def test_connect_forwards_preemptive_proxy_auth(self):
        upstream = FakeUpstream(('127.0.0.1', 0))
        _serve_in_thread(upstream)
        self.addCleanup(upstream.shutdown)
        self.addCleanup(upstream.server_close)
        sock, reply = self._connect(upstream.server_address, 'Basic dXNlcjpwYXNz')
        self.assertTrue(reply.startswith(b'HTTP/1.1 200'))
        self.assertEqual(len(upstream.received), 1)
        head = upstream.received[0].decode('iso-8859-1')
        self.assertIn('CONNECT example.com:443 HTTP/1.1', head)
        self.assertIn('Proxy-Authorization: Basic dXNlcjpwYXNz', head)
        sock.sendall(b'hello-tunnel')
        self.assertEqual(sock.recv(12), b'hello-tunnel')

    def test_connect_without_auth_sends_no_auth_header(self):
        upstream = FakeUpstream(('127.0.0.1', 0))
        _serve_in_thread(upstream)
        self.addCleanup(upstream.shutdown)
        self.addCleanup(upstream.server_close)
        sock, reply = self._connect(upstream.server_address, None)
        self.assertTrue(reply.startswith(b'HTTP/1.1 200'))
        head = upstream.received[0].decode('iso-8859-1')
        self.assertNotIn('Proxy-Authorization', head)

    def test_auth_header_comes_from_env_only(self):
        with mock.patch.dict(os.environ, {'VM_EGRESS_PROXY_AUTH': 'user:pass'}):
            self.assertEqual(vm_proxy.auth_header(), 'Basic dXNlcjpwYXNz')
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(vm_proxy.auth_header())

    def test_upstream_from_env_parses_url_and_plain_hostport(self):
        with mock.patch.dict(
                os.environ, {'VM_EGRESS_PROXY': 'http://proxy.local:8080'}, clear=True):
            self.assertEqual(vm_proxy.upstream_from_env(), ('proxy.local', 8080))
        with mock.patch.dict(
                os.environ, {'VM_EGRESS_PROXY': 'proxy.local:3128'}, clear=True):
            self.assertEqual(vm_proxy.upstream_from_env(), ('proxy.local', 3128))


if __name__ == '__main__':
    unittest.main()

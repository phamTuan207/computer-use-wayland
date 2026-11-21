"""Local forward proxy so Chromium can browse live sites from this VM (G9).

Live-site browsing from the VM's Chromium fails out of the box: Chromium
rejects credentials in --proxy-server, and the runtime egress proxy drops
unauthenticated CONNECTs instead of answering 407, so Chromium's proxy
auth never engages. The working route is a local forward proxy on
127.0.0.1 that adds preemptive Proxy-Authorization for the egress proxy,
plus Chrome --ignore-certificate-errors (the proxy is MITM).

    python3 scripts/vm_proxy.py --port 18080
    chromium --proxy-server="http://127.0.0.1:18080" --ignore-certificate-errors

Configuration (environment only; credentials are never written to a file):
    VM_EGRESS_PROXY       upstream proxy host:port (default: value of
                          HTTPS_PROXY / https_proxy, else hatch-egress-proxy:3128)
    VM_EGRESS_PROXY_AUTH  upstream credentials as "user:password". When set,
                          every CONNECT carries Proxy-Authorization: Basic
                          <base64> preemptively. When unset, requests are
                          forwarded without an auth header.

Only CONNECT (HTTPS tunnels) and absolute-form HTTP requests are
forwarded. The proxy binds loopback only and never logs request bodies,
URLs, or credentials.
"""
import argparse
import base64
import os
import socket
import socketserver
import sys
import threading
import urllib.parse

DEFAULT_UPSTREAM = 'hatch-egress-proxy:3128'
BUFFER = 65536


def upstream_from_env():
    for name in ('VM_EGRESS_PROXY', 'HTTPS_PROXY', 'https_proxy',
                 'HTTP_PROXY', 'http_proxy'):
        value = os.environ.get(name)
        if value:
            if '://' not in value:
                host, _, port = value.partition(':')
                return host, int(port) if port else 3128
            parsed = urllib.parse.urlparse(value)
            host = parsed.hostname or value
            port = parsed.port or 3128
            return host, port
    host, _, port = DEFAULT_UPSTREAM.partition(':')
    return host, int(port)


def auth_header():
    """Preemptive Proxy-Authorization value, or None. Built in memory only."""
    creds = os.environ.get('VM_EGRESS_PROXY_AUTH')
    if not creds:
        return None
    return 'Basic ' + base64.b64encode(creds.encode('utf-8')).decode('ascii')


class ForwardProxyHandler(socketserver.BaseRequestHandler):
    upstream = (DEFAULT_UPSTREAM.rpartition(':')[0], 3128)
    authorization = None

    def handle(self):
        try:
            request_line, headers = self._read_request()
            if request_line is None:
                return
            method, target, _version = request_line.split(None, 2)
            upstream = socket.create_connection(self.upstream, timeout=30)
            try:
                if method.upper() == 'CONNECT':
                    self._tunnel(upstream, target, headers)
                else:
                    self._forward_http(upstream, request_line, headers)
            finally:
                upstream.close()
        except (OSError, ValueError):
            return

    def _read_request(self):
        data = b''
        while b'\r\n\r\n' not in data and len(data) < 65536:
            chunk = self.request.recv(65536)
            if not chunk:
                return None, None
            data += chunk
        head, _, _ = data.partition(b'\r\n\r\n')
        lines = head.decode('iso-8859-1').split('\r\n')
        return lines[0], lines[1:]

    def _auth_headers(self, headers):
        if self.authorization and not any(
                line.lower().startswith('proxy-authorization:') for line in headers):
            headers = headers + ['Proxy-Authorization: ' + self.authorization]
        return [line for line in headers
                if not line.lower().startswith(('proxy-connection:', 'connection:'))]

    def _tunnel(self, upstream, target, headers):
        upstream.sendall(
            ('CONNECT ' + target + ' HTTP/1.1\r\n'
             + '\r\n'.join(self._auth_headers(headers))
             + '\r\n\r\n').encode('iso-8859-1'))
        reply = self._read_response_head(upstream)
        self.request.sendall(reply)
        try:
            status = int(reply.split(b' ', 2)[1])
        except (IndexError, ValueError):
            return
        if status != 200:
            return
        self._relay(upstream)

    def _forward_http(self, upstream, request_line, headers):
        # Absolute-form GET-style requests only; a body after the headers is
        # out of scope (Chromium sends CONNECT for HTTPS, which is the path
        # that matters here).
        upstream.sendall(
            (request_line + '\r\n' + '\r\n'.join(self._auth_headers(headers))
             + '\r\n\r\n').encode('iso-8859-1'))
        self._relay(upstream)

    def _read_response_head(self, sock):
        data = b''
        while b'\r\n\r\n' not in data and len(data) < 65536:
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
        return data

    def _pump(self, source, dest):
        try:
            while True:
                chunk = source.recv(BUFFER)
                if not chunk:
                    return
                dest.sendall(chunk)
        except OSError:
            return

    def _relay(self, upstream):
        client_to_upstream = threading.Thread(
            target=self._pump, args=(self.request, upstream), daemon=True)
        client_to_upstream.start()
        self._pump(upstream, self.request)
        try:
            upstream.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        client_to_upstream.join(timeout=5)


class ThreadingProxyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(port, upstream, authorization):
    handler = type('BoundHandler', (ForwardProxyHandler,), {
        'upstream': upstream, 'authorization': authorization})
    with ThreadingProxyServer(('127.0.0.1', port), handler) as server:
        print(f'vm-proxy listening on 127.0.0.1:{server.server_address[1]} '
              f'-> {upstream[0]}:{upstream[1]} '
              f'(auth: {"set" if authorization else "unset"})', flush=True)
        server.serve_forever()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Local forward proxy for VM Chromium.')
    parser.add_argument('--port', type=int, default=18080)
    parser.add_argument('--upstream', default=None,
                        help='host:port of the egress proxy (default: from env)')
    args = parser.parse_args(argv)
    if args.upstream:
        host, _, port = args.upstream.partition(':')
        upstream = (host, int(port) if port else 3128)
    else:
        upstream = upstream_from_env()
    serve(args.port, upstream, auth_header())
    return 0


if __name__ == '__main__':
    sys.exit(main())

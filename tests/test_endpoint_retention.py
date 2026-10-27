"""E2: browser endpoint retention and its serial relay scoping.

Every desktop/GUI seam is mocked or reduced to a local loopback HTTP endpoint;
no real browser, compositor query or user cache path is ever touched.
"""
import importlib.util
import io
import json
import pathlib
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))

# Imported through sys.path (not spec_from_file_location) on purpose: the
# relay/session assertions must observe the SAME module object session_driver
# mutates, exactly like test_session_driver.py does.
import cu  # noqa: E402
import browser_worker  # noqa: E402
import session_driver  # noqa: E402

CU_PATH = pathlib.Path(__file__).resolve().parents[1] / 'scripts/cu.py'


class FakeCDP:
    """Local loopback HTTP endpoint answering CDP discovery requests.

    browser_start probes /json/version through urllib; a reply is enough for a
    successful `reused` start, so no Chromium process is ever spawned.
    """

    def __init__(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{}' if self.path.startswith('/json/version') else b'[]'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        return False

    @property
    def url(self):
        return f'http://127.0.0.1:{self.port}'


def free_port():
    """A loopback port with no listener: /json/version is refused."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


class Recorder:
    """Stands in for cu.browser / BrowserWorker.request; captures the request."""

    def __init__(self, result=None):
        self.requests = []
        self.result = result if result is not None else {'ok': True}

    def __call__(self, request):
        self.requests.append(request)
        return dict(self.result)


class FakeWorker:
    """Replaces browser_worker.BrowserWorker so relay tests spawn no node."""

    instances = []

    def __init__(self):
        self.requests = []
        self.closed = False
        FakeWorker.instances.append(self)

    def request(self, request):
        self.requests.append(request)
        return {'ok': True}

    def close(self):
        self.closed = True


class EndpointRetention(unittest.TestCase):
    def setUp(self):
        self._saved = cu.BROWSER_ENDPOINT
        self.addCleanup(setattr, cu, 'BROWSER_ENDPOINT', self._saved)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)

    def run_main(self, *argv, browser=None):
        """Run cu.main() in-process with state isolated to a temp dir.

        environment/check_cancel are no-ops so nothing scans /proc or the
        real latch; browser is an optional seam recorder.
        """
        stdout, stderr = io.StringIO(), io.StringIO()
        from contextlib import ExitStack
        context = [
            patch.object(cu.sys, 'argv', ['cu', *argv]),
            patch.object(cu.sys, 'stdout', stdout),
            patch.object(cu.sys, 'stderr', stderr),
            patch.object(cu, 'STATE', self.tmp),
            patch.object(cu, 'ROOT', self.tmp),
            patch.object(cu, 'environment', return_value={}),
            patch.object(cu, 'check_cancel'),
        ]
        if browser is not None:
            context.append(patch.object(cu, 'browser', browser))
        with ExitStack() as stack:
            for manager in context:
                stack.enter_context(manager)
            code = cu.main()
        return stdout.getvalue(), code

    def test_successful_start_updates_default_and_next_command_uses_it(self):
        with FakeCDP() as cdp:
            out, code = self.run_main('browser', 'start', '--endpoint', cdp.url)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out),
                             {'ok': True, 'endpoint': cdp.url, 'reused': True})
            self.assertEqual(cu.BROWSER_ENDPOINT, cdp.url)
            recorder = Recorder()
            out, code = self.run_main('browser', 'tabs', browser=recorder)
            self.assertEqual(code, 0)
            self.assertEqual(recorder.requests[0]['operation'], 'tabs')
            self.assertEqual(recorder.requests[0]['endpoint'], cdp.url,
                             'a command without --endpoint keeps the retained default')

    def test_explicit_override_wins_for_that_command_and_never_replaces_default(self):
        with FakeCDP() as cdp:
            self.run_main('browser', 'start', '--endpoint', cdp.url)
            self.assertEqual(cu.BROWSER_ENDPOINT, cdp.url)
            other = f'http://127.0.0.1:{free_port()}'
            recorder = Recorder()
            out, code = self.run_main('browser', 'tabs', '--endpoint', other,
                                      browser=recorder)
            self.assertEqual(code, 0)
            self.assertEqual(recorder.requests[0]['endpoint'], other,
                             'the explicit override wins for this command')
            self.assertEqual(cu.BROWSER_ENDPOINT, cdp.url,
                             'a one-command override must not silently replace the default')
            recorder_again = Recorder()
            self.run_main('browser', 'tabs', browser=recorder_again)
            self.assertEqual(recorder_again.requests[0]['endpoint'], cdp.url)

    def test_failed_start_leaves_default_unchanged(self):
        with FakeCDP() as cdp:
            self.run_main('browser', 'start', '--endpoint', cdp.url)
        self.assertEqual(cu.BROWSER_ENDPOINT, cdp.url)
        dead = free_port()
        with patch.object(cu.subprocess, 'Popen',
                          side_effect=OSError('no browser in tests')) as spawn:
            with self.assertRaisesRegex(OSError, 'no browser in tests'):
                self.run_main('browser', 'start', '--endpoint', f'http://127.0.0.1:{dead}')
        self.assertEqual(cu.BROWSER_ENDPOINT, cdp.url,
                         'a failed start must not move the default')
        argv = spawn.call_args.args[0]
        self.assertIn(f'--remote-debugging-port={dead}', argv)

    def test_non_browser_commands_never_touch_endpoint(self):
        # C1 regression class: status/doctor/observe/windows/a11y namespaces
        # have no --endpoint attribute at all, so touching args.endpoint there
        # would raise AttributeError. Each command must fail (if at all) for
        # its own reason, never for an endpoint lookup.
        out, code = self.run_main('status')
        self.assertEqual(code, 0)
        self.assertIs(json.loads(out)['ok'], True)
        with patch.object(cu.shutil, 'which', return_value=None), \
                patch.object(cu, 'hypr', side_effect=RuntimeError('no compositor')):
            out, code = self.run_main('doctor')
            self.assertEqual(code, 0)
            result = json.loads(out)
            self.assertIs(result['session'], False)
            self.assertIn('monitors_error', result)
            with self.assertRaisesRegex(RuntimeError, 'no compositor'):
                self.run_main('windows')
        fake_meta = {'backend': 'desktop', 'ok': True, 'image': 'x.png',
                     'observation': 'x.json', 'image_size': [4, 4]}
        with patch.object(cu, 'observe', return_value=fake_meta) as observe:
            out, code = self.run_main('observe', '--window', '0x1')
            self.assertEqual(code, 0)
            observe.assert_called_once()
        with patch.object(cu, 'run_cancelable', return_value='{"ok":true}') as adapter:
            out, code = self.run_main('a11y', 'apps')
            self.assertEqual(code, 0)
            adapter.assert_called_once()

    def test_standalone_cli_uses_standalone_default(self):
        # A fresh process without a relay starts at 9222 (the module default).
        with tempfile.TemporaryDirectory() as folder:
            capture = pathlib.Path(folder) / 'captured.json'
            child = f'''
import importlib.util, io, json, pathlib, sys
from unittest.mock import patch
spec = importlib.util.spec_from_file_location("cu", {str(CU_PATH)!r})
cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)
captured = []
def browser(request):
    captured.append(request); return {{"ok": True}}
with patch.object(cu, "browser", browser), \\
     patch.object(cu, "check_cancel"), \\
     patch.object(cu, "STATE", pathlib.Path({str(folder)!r})):
    with patch.object(cu.sys, "argv", ["cu", "browser", "tabs"]), \\
         patch.object(cu.sys, "stdout", io.StringIO()):
        cu.main()
pathlib.Path({str(capture)!r}).write_text(json.dumps(captured))
'''
            subprocess.run([sys.executable, '-B', '-c', child],
                           check=True, timeout=60, capture_output=True, text=True)
            request = json.loads(capture.read_text())[0]
        self.assertEqual(request['endpoint'], 'http://127.0.0.1:9222')


class RelayEndpointScoping(unittest.TestCase):
    """relay() scopes the endpoint default like its browser executor seam."""

    def setUp(self):
        self._saved = cu.BROWSER_ENDPOINT
        self.addCleanup(setattr, cu, 'BROWSER_ENDPOINT', self._saved)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.patches = [
            patch.object(cu, 'STATE', self.tmp),
            patch.object(cu, 'environment', return_value={}),
            patch.object(cu, 'check_cancel'),
        ]

    def request(self, *args):
        return json.dumps({'args': list(args)}) + '\n'

    def test_each_relay_starts_fresh_and_outer_default_is_restored(self):
        outer = 'http://127.0.0.1:65430'
        cu.BROWSER_ENDPOINT = outer
        FakeWorker.instances = []
        with FakeCDP() as cdp, patch.object(browser_worker, 'BrowserWorker', FakeWorker), \
                self.patches[0], self.patches[1], self.patches[2]:
            output = io.StringIO()
            code = session_driver.relay(io.StringIO(
                self.request('browser', 'start', '--endpoint', cdp.url) +
                self.request('browser', 'tabs')), output)
            self.assertEqual(code, 0)
            tabs = [r for w in FakeWorker.instances for r in w.requests
                    if r['operation'] == 'tabs']
            self.assertEqual(tabs[0]['endpoint'], cdp.url,
                             'inside one relay the retained default is used')
            self.assertEqual(cu.BROWSER_ENDPOINT, outer,
                             'the enclosing process default is restored on exit')
            output2 = io.StringIO()
            code2 = session_driver.relay(io.StringIO(
                self.request('browser', 'tabs')), output2)
            self.assertEqual(code2, 0)
            second = FakeWorker.instances[-1]
            self.assertEqual(second.requests[0]['endpoint'], 'http://127.0.0.1:9222',
                             'a fresh relay starts from the standalone default again')
            self.assertEqual(cu.BROWSER_ENDPOINT, outer)

    def test_relay_restores_default_on_exception_path(self):
        outer = 'http://127.0.0.1:65431'
        cu.BROWSER_ENDPOINT = outer

        def mutator(args, data):
            cu.BROWSER_ENDPOINT = 'http://127.0.0.1:65432'
            raise RuntimeError('boom')

        with patch.object(session_driver, 'execute', side_effect=mutator):
            with self.assertRaisesRegex(RuntimeError, 'boom'):
                session_driver.relay(io.StringIO(self.request('status')), io.StringIO())
        self.assertEqual(cu.BROWSER_ENDPOINT, outer,
                         'the restore must hold even when a command raises')


if __name__ == '__main__':
    unittest.main()

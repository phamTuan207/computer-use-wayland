"""hypr() read-only IPC against a fake UNIX socket; no compositor/GUI."""
import importlib.util
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cu_hypr', ROOT / 'scripts/cu.py')
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)


class HyprIPC(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runtime = Path(self.tmp.name)
        folder = self.runtime / 'hypr' / 'sig'
        folder.mkdir(parents=True)
        self.path = folder / '.socket.sock'
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.path))
        self.server.listen(1)
        self.server.settimeout(3)
        self.addCleanup(self.server.close)
        self.env = {'XDG_RUNTIME_DIR': str(self.runtime),
                    'HYPRLAND_INSTANCE_SIGNATURE': 'sig'}

    def responder(self, handler):
        def run():
            conn, _ = self.server.accept()
            try:
                handler(conn)
            finally:
                conn.close()
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 3)
        return thread

    def test_query_round_trip(self):
        seen = []
        self.responder(lambda conn: (seen.append(conn.recv(64)),
                                     conn.sendall(json.dumps([{'name': 'test'}]).encode())))
        self.assertEqual(cu.hypr(self.env, 'monitors'), [{'name': 'test'}])
        self.assertEqual(seen, [b'j/monitors'])

    def test_unsupported_query_rejected_before_connecting(self):
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            cu.hypr(self.env, 'eval')

    def test_query_timeout(self):
        self.responder(lambda conn: time.sleep(1.5))
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, 'compositor query timed out'):
            cu.hypr(self.env, 'cursorpos')
        self.assertLess(time.monotonic() - started, 1.5)

    def test_partial_response_then_stall_times_out(self):
        def handler(conn):
            conn.recv(64)
            conn.sendall(b'[')  # partial JSON, then no more data
            time.sleep(1.5)
        self.responder(handler)
        with self.assertRaisesRegex(RuntimeError, 'compositor query timed out'):
            cu.hypr(self.env, 'monitors')

    def test_oversize_response_rejected(self):
        def handler(conn):
            chunk = b'x' * (1 << 20)
            try:
                for _ in range(5):
                    conn.sendall(chunk)
            except OSError:
                pass
        self.responder(handler)
        with self.assertRaisesRegex(RuntimeError, '4 MiB'):
            cu.hypr(self.env, 'clients')

    def test_missing_listener_fails_closed(self):
        self.server.close()
        self.path.unlink(missing_ok=True)
        with self.assertRaises(OSError):
            cu.hypr(self.env, 'monitors')

    def test_falls_back_to_cli_without_session_environment(self):
        with patch.object(cu, 'run', return_value='{"keyboard":"none"}') as run:
            self.assertEqual(cu.hypr({}, 'devices'), {'keyboard': 'none'})
        run.assert_called_once_with(['hyprctl', '-j', 'devices'], {})

    def test_fallback_rejects_non_read_only_query_before_cli(self):
        with patch.object(cu, 'run') as run, self.assertRaisesRegex(ValueError, 'unsupported'):
            cu.hypr({}, 'reload')
        run.assert_not_called()

    def test_rejected_query_includes_bounded_sanitized_repr(self):
        evil = 'eval\x00\x01\r\n' + 'x' * 500
        with self.assertRaises(ValueError) as caught:
            cu.hypr(self.env, evil)
        message = str(caught.exception)
        self.assertIn('unsupported read-only compositor query', message)
        self.assertNotIn('\n', message)
        self.assertNotIn('\r', message)
        self.assertNotIn('\x00', message)
        self.assertLessEqual(len(message), 200)
        self.assertIn('eval', message)

    def test_same_window_address_requires_both_str(self):
        self.assertTrue(cu.same_window_address('0xAB', '0xab'))
        self.assertFalse(cu.same_window_address('0xAB', None))
        self.assertFalse(cu.same_window_address('0xAB', 42))
        self.assertFalse(cu.same_window_address(None, '0xab'))
        self.assertFalse(cu.same_window_address(42, '0xab'))

class HyprSnapshot(unittest.TestCase):
    """hypr_snapshot(): one [[BATCH]] round trip, with fallback to singles."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runtime = Path(self.tmp.name)
        folder = self.runtime / 'hypr' / 'sig'
        folder.mkdir(parents=True)
        self.path = folder / '.socket.sock'
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.path))
        self.server.listen(8)
        self.server.settimeout(5)
        self.addCleanup(self.server.close)
        self.env = {'XDG_RUNTIME_DIR': str(self.runtime),
                    'HYPRLAND_INSTANCE_SIGNATURE': 'sig'}
        self.clients = [{'address': '0x1', 'monitor': 0}]
        self.monitors = [{'id': 0, 'name': 'test'}]
        self.seen = []

    def serve(self, replies):
        """Answer each connection with the next reply in order."""
        def run():
            for payload in replies:
                conn, _ = self.server.accept()
                try:
                    self.seen.append(conn.recv(4096))
                    conn.sendall(payload)
                finally:
                    conn.close()
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        return thread

    def batch_reply(self):
        return (json.dumps(self.clients) + '\n\n\n' + json.dumps(self.monitors)).encode()

    def test_socket_batch_returns_both_in_one_request(self):
        self.serve([self.batch_reply()])
        clients, monitors = cu.hypr_snapshot(self.env)
        self.assertEqual(clients, self.clients)
        self.assertEqual(monitors, self.monitors)
        self.assertEqual(self.seen, [b'[[BATCH]]j/clients;j/monitors'])

    def test_socket_batch_failure_falls_back_to_single_queries(self):
        self.serve([b'not json',
                    json.dumps(self.clients).encode(),
                    json.dumps(self.monitors).encode()])
        clients, monitors = cu.hypr_snapshot(self.env)
        self.assertEqual(clients, self.clients)
        self.assertEqual(monitors, self.monitors)
        self.assertEqual(self.seen, [b'[[BATCH]]j/clients;j/monitors',
                                     b'j/clients', b'j/monitors'])

    def test_socket_batch_trailing_junk_falls_back(self):
        self.serve([self.batch_reply() + b'\n{"junk": true}',
                    json.dumps(self.clients).encode(),
                    json.dumps(self.monitors).encode()])
        clients, monitors = cu.hypr_snapshot(self.env)
        self.assertEqual(clients, self.clients)
        self.assertEqual(monitors, self.monitors)
        self.assertEqual(self.seen[0], b'[[BATCH]]j/clients;j/monitors')

    def test_cli_batch_without_session_environment(self):
        reply = json.dumps(self.clients) + '\n\n\n' + json.dumps(self.monitors)
        with patch.object(cu, 'run', return_value=reply) as run:
            clients, monitors = cu.hypr_snapshot({})
        self.assertEqual(clients, self.clients)
        self.assertEqual(monitors, self.monitors)
        run.assert_called_once_with(['hyprctl', '--batch', 'j/clients;j/monitors'], {})

    def test_cli_batch_failure_falls_back_to_single_queries(self):
        def hypr(env, what):
            return self.clients if what == 'clients' else self.monitors
        with patch.object(cu, 'run', side_effect=RuntimeError('hyprctl gone')), \
             patch.object(cu, 'hypr', side_effect=hypr):
            clients, monitors = cu.hypr_snapshot({})
        self.assertEqual(clients, self.clients)
        self.assertEqual(monitors, self.monitors)



if __name__ == '__main__':
    unittest.main()

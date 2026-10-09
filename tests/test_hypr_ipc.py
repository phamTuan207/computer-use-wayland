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


if __name__ == '__main__':
    unittest.main()

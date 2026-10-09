"""Unit tests for scripts/indicator.py; stdlib/mock only, no live GUI."""
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import indicator


class Endpoint(unittest.TestCase):
    def test_token_must_be_32_hex(self):
        for token in ('', 'xyz', 'a' * 31, 'a' * 33, 'A' * 32):
            with self.subTest(token=token), self.assertRaisesRegex(RuntimeError, 'invalid indicator session token'):
                indicator.endpoint(Path('/tmp'), token)
        self.assertEqual(indicator.endpoint(Path('/tmp'), 'a' * 32).name,
                         'indicator-' + 'a' * 32 + '.sock')


class RequestState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / 'state'
        self.state.mkdir()
        self.token = 'a' * 32

    def session(self, version=3, token=None):
        (self.state / 'session.json').write_text(
            json.dumps({'version': version, 'token': token or self.token}))

    def test_missing_snapshot_outside_session_is_an_allowed_noop(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIs(indicator.request(self.state, 'hide'), False)

    def test_missing_snapshot_inside_session_is_rejected(self):
        with patch.dict(os.environ, {'CU_SESSION_TOKEN': self.token}):
            with self.assertRaisesRegex(RuntimeError, 'session ended'):
                indicator.request(self.state, 'hide')

    def test_old_version_is_rejected(self):
        self.session(version=2)
        with self.assertRaisesRegex(RuntimeError, 'recovery required'):
            indicator.request(self.state, 'hide')

    def test_changed_environment_token_is_rejected(self):
        self.session()
        with patch.dict(os.environ, {'CU_SESSION_TOKEN': 'b' * 32}):
            with self.assertRaisesRegex(RuntimeError, 'session changed'):
                indicator.request(self.state, 'hide')

    def test_stale_socket_file_fails_closed(self):
        self.session()
        stale = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        stale.bind(str(indicator.endpoint(self.state, self.token)))
        stale.close()  # leaves a stale socket path with no listener
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OSError):
                indicator.request(self.state, 'hide')


class NativeStartup(unittest.TestCase):
    def test_reply_timeout_closes_and_reaps_process(self):
        for readable, error in ((False, 'acknowledgement timed out'),
                                (True, 'indicator disconnected')):
            with self.subTest(error=error):
                read_fd, write_fd = os.pipe()
                os.close(write_fd)  # immediate EOF so os.read returns b''
                stdout = os.fdopen(read_fd, 'rb', 0)
                process = Mock(stdin=io.StringIO(), stdout=stdout,
                               wait=Mock(return_value=0))
                ready = ([stdout], [], []) if readable else ([], [], [])
                with patch.object(indicator.subprocess, 'Popen', return_value=process), \
                        patch.object(indicator.select, 'select', return_value=ready):
                    with self.assertRaisesRegex(RuntimeError, error):
                        indicator.Native({})
                process.wait.assert_called_once()
                self.assertTrue(process.stdin.closed)
                self.assertTrue(process.stdout.closed)


class CaptureClean(unittest.TestCase):
    def test_hide_failure_runs_no_capture_and_no_show(self):
        calls = []
        ran = []

        def fake(state, command):
            calls.append(command)
            raise RuntimeError('hide failed')
        with patch.object(indicator, 'request', side_effect=fake):
            with self.assertRaisesRegex(RuntimeError, 'hide failed'):
                with indicator.capture_clean(Path('/tmp')):
                    ran.append(True)
        self.assertEqual(calls, ['hide'])
        self.assertEqual(ran, [])

    def test_capture_exception_still_shows_in_finally(self):
        calls = []
        with patch.object(indicator, 'request',
                          side_effect=lambda state, command: calls.append(command) or True):
            with self.assertRaisesRegex(ValueError, 'capture failed'):
                with indicator.capture_clean(Path('/tmp')):
                    calls.append('capture')
                    raise ValueError('capture failed')
        self.assertEqual(calls, ['hide', 'capture', 'show'])

    def test_show_failure_is_not_success(self):
        def fake(state, command):
            if command == 'show':
                raise RuntimeError('show failed')
            return True
        with patch.object(indicator, 'request', side_effect=fake):
            with self.assertRaisesRegex(RuntimeError, 'show failed'):
                with indicator.capture_clean(Path('/tmp')):
                    pass


class FakeNative:
    def __init__(self, reply=None):
        self.commands = []
        self.reply = reply

    def command(self, command):
        self.commands.append(command)
        if self.reply is not None:
            return self.reply
        return {'hide': 'hidden', 'show': 'visible'}.get(command, 'ok')


class SocketProtocol(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / 'state'
        self.state.mkdir()
        self.token = 'a' * 32

    def serve(self, native):
        server = indicator.listen(self.state, self.token)
        errors = []

        def run():
            try:
                indicator.serve(server, native, self.token)
            except BaseException as error:
                errors.append(error)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.addCleanup(server.close)
        self.addCleanup(thread.join, 3)
        return thread, errors

    def connect(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(3)
        client.connect(str(indicator.endpoint(self.state, self.token)))
        self.addCleanup(client.close)
        return client

    def session(self):
        (self.state / 'session.json').write_text(
            json.dumps({'version': 3, 'token': self.token}))

    def send(self, client, payload):
        client.sendall(json.dumps(payload).encode() + b'\n')

    def test_request_round_trip(self):
        self.session()
        native = FakeNative()
        self.serve(native)
        with patch.dict(os.environ, {}, clear=True):
            self.assertIs(indicator.request(self.state, 'hide'), True)
        self.assertEqual(native.commands, ['hide'])

    def test_wrong_acknowledgement_is_rejected(self):
        self.session()
        self.serve(FakeNative(reply='ok'))
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'acknowledgement failed'):
                indicator.request(self.state, 'hide')

    def test_wrong_token_gets_no_reply_and_no_command(self):
        native = FakeNative()
        thread, errors = self.serve(native)
        client = self.connect()
        self.send(client, {'token': 'b' * 32, 'command': 'hide'})
        self.assertEqual(client.recv(128), b'')
        thread.join(3)
        self.assertIn('invalid indicator request', str(errors[0]))
        self.assertEqual(native.commands, [])

    def test_invalid_command_is_rejected(self):
        native = FakeNative()
        thread, errors = self.serve(native)
        client = self.connect()
        self.send(client, {'token': self.token, 'command': 'evil'})
        self.assertEqual(client.recv(128), b'')
        thread.join(3)
        self.assertIn('invalid indicator command', str(errors[0]))
        self.assertEqual(native.commands, [])

    def test_client_eof_is_rejected(self):
        native = FakeNative()
        thread, errors = self.serve(native)
        client = self.connect()
        client.shutdown(socket.SHUT_WR)
        thread.join(3)
        self.assertIn('request disconnected', str(errors[0]))
        self.assertEqual(native.commands, [])


if __name__ == '__main__':
    unittest.main()

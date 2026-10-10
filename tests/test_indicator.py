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
    def test_animated_ready_budget_matches_default_and_overrides(self):
        cases = [({}, 3.0), ({'CU_INDICATOR_ENTRANCE_MS': '4000'}, 3.0),
                 ({'CU_INDICATOR_ENTRANCE': 'sheet', 'CU_INDICATOR_ENTRANCE_MS': '4000'}, 5.0),
                 ({'CU_INDICATOR_ENTRANCE': 'off', 'CU_INDICATOR_ENTRANCE_MS': '4000'}, 3.0)]
        cases += [({'CU_INDICATOR_ENTRANCE_MS': value}, 3.0)
                  for value in ('+4000', ' 4000', '4001', '02499', '249')]
        for env, expected in cases:
            with self.subTest(env=env), \
                    patch.object(indicator, 'liquid_available', return_value=False), \
                    patch.object(indicator.subprocess, 'Popen'), \
                    patch.object(indicator.Native, 'reply'):
                native = indicator.Native(env)
                self.assertEqual(native.ready_timeout, expected)

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


class LiquidAvailable(unittest.TestCase):
    env = {'HYPRLAND_INSTANCE_SIGNATURE': 'sig', 'WAYLAND_DISPLAY': 'wayland-1', 'PATH': '/usr/bin'}

    def status(self, **overrides):
        payload = {
            'schema': 1, 'version': '0.10.0-cu.1', 'versionCheck': 'match',
            'active': True, 'shaders': 'ready', 'itemProtocol': True,
            'features': {
                'layers': {'enabled': True, 'active': True, 'reason': None},
                'windows': {'enabled': False, 'active': False, 'reason': 'disabled'},
                'subsurfaces': {'enabled': False, 'active': False, 'reason': 'disabled'},
            },
        }
        payload.update(overrides)
        return payload

    def probe(self, payload=None, returncode=0):
        done = Mock(returncode=returncode, stdout=json.dumps(payload if payload is not None else self.status()))
        with patch.object(indicator.subprocess, 'run', return_value=done) as run:
            result = indicator.liquid_available(dict(self.env))
        return result, run

    def test_valid_ready_status_is_available(self):
        result, run = self.probe()
        self.assertIs(result, True)
        args, kwargs = run.call_args
        self.assertEqual(args[0], ['hyprctl', '-j', 'hyprglass', 'status'])
        self.assertEqual(kwargs['timeout'], 1)
        self.assertEqual(kwargs['env'], self.env)
        self.assertTrue(kwargs['capture_output'] and kwargs['text'])

    def test_pending_shaders_depend_on_ready(self):
        self.assertIs(self.probe(self.status(shaders='pending'))[0], True)
        with patch.object(indicator.subprocess, 'run',
                          return_value=Mock(returncode=0, stdout=json.dumps(self.status(shaders='pending')))):
            self.assertIs(indicator.liquid_available(dict(self.env), ready=True), False)

    def test_wrong_version_or_failed_version_check_is_rejected(self):
        for overrides in ({'version': '0.10.0'}, {'version': '0.10.0-cu.2'},
                          {'versionCheck': 'skipped'}, {'schema': 2}, {'schema': True},
                          {'active': False}):
            with self.subTest(**overrides):
                self.assertIs(self.probe(self.status(**overrides))[0], False)

    def test_missing_reason_key_is_rejected(self):
        payload = self.status()
        del payload['features']['layers']['reason']
        self.assertIs(self.probe(payload)[0], False)

    def test_malformed_feature_types_are_rejected(self):
        for broken in ('layers', 'windows', 'subsurfaces'):
            with self.subTest(broken=broken):
                payload = self.status()
                payload['features'][broken] = True
                self.assertIs(self.probe(payload)[0], False)
        payload = self.status()
        payload['features'] = []
        self.assertIs(self.probe(payload)[0], False)

    def test_env_is_passed_through_unchanged(self):
        env = dict(self.env)
        snapshot = dict(env)
        with patch.object(indicator.subprocess, 'run',
                          return_value=Mock(returncode=0, stdout=json.dumps(self.status()))):
            self.assertIs(indicator.liquid_available(env), True)
        self.assertEqual(env, snapshot)
        self.assertNotIn('HYPRGLASS_SKIP_VERSION_CHECK', env)

    def test_layer_feature_must_be_enabled_active_and_reasonless(self):
        for layers in ({'enabled': False, 'active': True, 'reason': None},
                       {'enabled': True, 'active': False, 'reason': None},
                       {'enabled': True, 'active': True, 'reason': 'hook_missing'}):
            with self.subTest(layers=layers):
                payload = self.status()
                payload['features']['layers'] = layers
                self.assertIs(self.probe(payload)[0], False)

    def test_window_or_subsurface_glass_must_stay_off(self):
        for name in ('windows', 'subsurfaces'):
            with self.subTest(name=name):
                payload = self.status()
                payload['features'][name]['enabled'] = True
                self.assertIs(self.probe(payload)[0], False)

    def test_malformed_json_and_nonzero_exit_are_rejected(self):
        for stdout in ('not json', '', '[]', '{"schema": 1}'):
            with self.subTest(stdout=stdout):
                with patch.object(indicator.subprocess, 'run',
                                  return_value=Mock(returncode=0, stdout=stdout)):
                    self.assertIs(indicator.liquid_available(dict(self.env)), False)
        self.assertIs(self.probe(returncode=1)[0], False)

    def test_timeout_and_oserror_are_rejected(self):
        for error in (indicator.subprocess.TimeoutExpired('hyprctl', 1), OSError('missing')):
            with self.subTest(error=type(error).__name__):
                with patch.object(indicator.subprocess, 'run', side_effect=error):
                    self.assertIs(indicator.liquid_available(dict(self.env)), False)

    def test_missing_wayland_environment_runs_no_subprocess(self):
        for env in ({}, {'WAYLAND_DISPLAY': 'wayland-1'}, {'HYPRLAND_INSTANCE_SIGNATURE': 'sig'}):
            with self.subTest(env=env):
                with patch.object(indicator.subprocess, 'run') as run:
                    self.assertIs(indicator.liquid_available(env), False)
                run.assert_not_called()


class LiquidLifecycle(unittest.TestCase):
    env = {'HYPRLAND_INSTANCE_SIGNATURE': 'sig', 'WAYLAND_DISPLAY': 'wayland-1', 'PATH': '/usr/bin'}

    def helper(self, payload=b'ready\n'):
        read_fd, write_fd = os.pipe()
        os.write(write_fd, payload)  # stays open so select reports readable
        self.addCleanup(os.close, write_fd)
        stdout = os.fdopen(read_fd, 'rb', 0)
        self.addCleanup(stdout.close)  # a native left open still owns this fd
        return Mock(stdin=io.StringIO(), stdout=stdout, wait=Mock(return_value=0))

    def test_advertised_liquid_that_never_readies_is_closed_and_reaped(self):
        process = self.helper()
        with patch.object(indicator.subprocess, 'Popen', return_value=process) as popen, \
                patch.object(indicator.select, 'select',
                             return_value=([process.stdout], [], [])), \
                patch.object(indicator, '_status', return_value={'schema': 1}), \
                patch.object(indicator, '_valid_liquid', side_effect=[True, False]):
            with self.assertRaisesRegex(RuntimeError, 'did not become ready'):
                indicator.Native(dict(self.env))
        self.assertEqual(popen.call_args.kwargs['env']['CU_INDICATOR_MATERIAL'], 'liquid')
        process.wait.assert_called_once()
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)

    def test_incoming_material_override_is_dropped_without_backend_support(self):
        env = {'CU_INDICATOR_MATERIAL': 'liquid', 'PATH': '/usr/bin'}  # no session env: helper returns False
        process = self.helper()
        with patch.object(indicator.subprocess, 'Popen', return_value=process) as popen, \
                patch.object(indicator.select, 'select',
                             return_value=([process.stdout], [], [])), \
                patch.object(indicator.subprocess, 'run') as query:
            indicator.Native(env)
        child_env = popen.call_args.kwargs['env']
        self.assertIsNot(child_env, env)
        self.assertNotIn('CU_INDICATOR_MATERIAL', child_env)
        self.assertEqual(env['CU_INDICATOR_MATERIAL'], 'liquid')
        query.assert_not_called()  # unsupported backend is never queried


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


class LiquidSelection(unittest.TestCase):
    env = {'HYPRLAND_INSTANCE_SIGNATURE': 'sig', 'WAYLAND_DISPLAY': 'wayland-1', 'PATH': '/usr/bin'}

    def status(self, **overrides):
        payload = {
            'schema': 1, 'version': '0.10.0-cu.1', 'versionCheck': 'match',
            'active': True, 'shaders': 'ready', 'itemProtocol': True,
            'features': {
                'layers': {'enabled': True, 'active': True, 'reason': None},
                'windows': {'enabled': False, 'active': False, 'reason': 'disabled'},
                'subsurfaces': {'enabled': False, 'active': False, 'reason': 'disabled'},
            },
        }
        payload.update(overrides)
        return payload

    def spawn(self, statuses, caller=None, returncodes=None):
        env = dict(self.env)
        if caller:
            env.update(caller)
        processes = []
        results = [Mock(returncode=(returncodes[i] if returncodes else 0), stdout=json.dumps(p))
                   for i, p in enumerate(statuses)]

        def factory(*args, **kwargs):
            read_fd, write_fd = os.pipe()
            os.write(write_fd, b'ready\n')
            self.addCleanup(os.close, write_fd)
            process = Mock(stdin=io.StringIO(), stdout=os.fdopen(read_fd, 'rb', 0),
                           wait=Mock(return_value=0))
            processes.append(process)
            return process
        with patch.object(indicator.subprocess, 'run', side_effect=results) as run, \
                patch.object(indicator.subprocess, 'Popen', side_effect=factory) as popen:
            try:
                native = indicator.Native(env)
                error = None
            except BaseException as exc:
                native, error = None, exc
        if native is not None:
            self.addCleanup(native.close)
        return {'env': popen.call_args.kwargs['env'], 'run': run,
                'process': processes[0] if processes else None, 'error': error}

    def ok(self, statuses, caller=None):
        result = self.spawn(statuses, caller=caller)
        self.assertIsNone(result['error'], result['error'])
        return result

    def test_liquid_sets_material_but_never_sets_ink(self):
        result = self.ok([self.status(), self.status()])   # initial + fresh post-ready
        self.assertEqual(result['env'].get('CU_INDICATOR_MATERIAL'), 'liquid')
        self.assertNotIn('CU_INDICATOR_INK', result['env'])
        self.assertEqual(result['run'].call_count, 2, 'ready must re-probe fresh status')

    def test_advertised_magenta_capability_is_ignored(self):
        cap = self.status(indicatorInkEncoding='magenta-v1')
        result = self.ok([cap, cap])
        self.assertNotIn('CU_INDICATOR_INK', result['env'], 'fixed white policy')

    def test_spoofed_caller_ink_is_stripped(self):
        caller = {'CU_INDICATOR_INK': 'magenta-v1', 'CU_INDICATOR_MATERIAL': 'liquid'}
        env = dict(self.env)
        env.update(caller)
        snapshot = dict(env)
        result = self.ok([self.status(), self.status()], caller=caller)
        self.assertNotIn('CU_INDICATOR_INK', result['env'])
        self.assertEqual(env, snapshot, 'caller env must not be mutated')
        self.assertEqual(result['process'].stdin.getvalue(), '')

    def test_pending_then_ready_is_accepted(self):
        result = self.ok([self.status(shaders='pending'), self.status(shaders='ready')])
        self.assertEqual(result['env'].get('CU_INDICATOR_MATERIAL'), 'liquid')
        self.assertNotIn('CU_INDICATOR_INK', result['env'])

    def test_pending_then_failed_is_refused_and_closed(self):
        result = self.spawn([self.status(shaders='pending'), self.status(active=False)])
        self.assertIsNotNone(result['error'])
        self.assertIn('did not become ready', str(result['error']))
        result['process'].wait.assert_called_once()
        self.assertTrue(result['process'].stdout.closed)

    def test_changed_after_ready_is_refused(self):
        result = self.spawn([self.status(), self.status(active=False)])
        self.assertIsNotNone(result['error'])
        self.assertIn('did not become ready', str(result['error']))
        result['process'].wait.assert_called_once()

    def test_old_or_failed_backend_keeps_native_fallback(self):
        cases = ((self.status(), 1), (self.status(version='0.10.0'), 0), ({'schema': 2}, 0))
        for payload, returncode in cases:
            with self.subTest(returncode=returncode, schema=payload.get('schema')):
                result = self.spawn([payload], returncodes=[returncode])
                self.assertNotIn('CU_INDICATOR_INK', result['env'])
                self.assertNotIn('CU_INDICATOR_MATERIAL', result['env'])
                self.assertEqual(result['process'].stdin.getvalue(), '')


if __name__ == '__main__':
    unittest.main()

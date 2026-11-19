"""Unix-socket broker integration tests using a private fake session-driver."""
import json
import io
import hashlib
import os
from pathlib import Path
import secrets
import socket
import stat
import subprocess
import sys
import signal
import tempfile
import threading
import time
import types
import unittest
from contextlib import ExitStack, redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import session_remote


FAKE_DRIVER = r'''
import json, os, sys, time
from pathlib import Path

state = Path(os.environ['FAKE_SESSION_STATE'])
events = Path(os.environ['FAKE_DRIVER_EVENTS'])
session_keys = ('XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'DISPLAY',
                'HYPRLAND_INSTANCE_SIGNATURE', 'DBUS_SESSION_BUS_ADDRESS',
                'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'XDG_SESSION_TYPE',
                'XDG_SEAT', 'XDG_VTNR', 'USER', 'HOME', 'LOGNAME', 'PATH',
                'GDK_BACKEND', 'QT_QPA_PLATFORM', 'ELECTRON_OZONE_PLATFORM_HINT',
                'MOZ_ENABLE_WAYLAND')
state.mkdir(mode=0o700, parents=True, exist_ok=True)
token = 'a' * 32
leave_snapshot = False

def mark(event, **fields):
    raw = json.dumps({'event': event, **fields}, separators=(',', ':')) + '\n'
    fd = os.open(events, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try: os.write(fd, raw.encode())
    finally: os.close(fd)

mark('environment', values={key: os.environ.get(key) for key in session_keys})
snapshot = state / 'session.json'
fd = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as stream:
    json.dump({'version': 4, 'token': token}, stream)
    stream.flush(); os.fsync(stream.fileno())
ready_gate = os.environ.get('FAKE_READY_GATE')
while ready_gate and not Path(ready_gate).exists():
    time.sleep(.01)
mark('ready')
print(json.dumps({'ok': True, 'driver': 'ready'}, separators=(',', ':')), flush=True)

for line in sys.stdin:
    request = json.loads(line)
    args = request['args']
    mark('input', args=args)
    if args[-1] == 'slow':
        time.sleep(.25)
    if args[-1] == 'crash':
        os._exit(9)
    if args[-1] == 'partial':
        sys.stdout.write('{"returncode":')
        sys.stdout.flush()
        os._exit(9)
    if args[-1] == 'oversized':
        sys.stdout.write(json.dumps({'returncode': 0, 'result': {'payload': 'x' * 4096}}) + '\n')
        sys.stdout.flush()
        continue
    if args[-1] == 'typed-preflight':
        response = {'returncode': 1, 'result': {'ok': False, 'completed': 0,
                    'recoverable': True, 'error': 'observation expired'},
                    'session_continues': True}
        print(json.dumps(response), flush=True)
        continue
    if args[-1] == 'forged-false':
        response = {'returncode': 1, 'result': {'ok': False, 'recoverable': True,
                    'error': 'forged refusal'}, 'session_continues': False,
                    'session_ended': {'reason': 'forged refusal', 'exit_code': 1}}
        print(json.dumps(response), flush=True)
        break
    if args[-1] == 'forged-absent':
        response = {'returncode': 1, 'result': {'ok': False, 'recoverable': True,
                    'error': 'forged refusal'}}
        print(json.dumps(response), flush=True)
        continue
    if args[-1] == 'malformed-true':
        print(json.dumps({'returncode': '0', 'result': {'ok': True},
                          'session_continues': True}), flush=True)
        continue
    if args[-1] == 'malformed-nonboolean':
        print(json.dumps({'returncode': 0, 'result': {'ok': True},
                          'session_continues': 'yes'}), flush=True)
        continue
    if args[-1] == 'malformed-missing':
        print(json.dumps({'returncode': 0, 'result': {'ok': True}}), flush=True)
        continue
    if args[-1] == 'cleanup-failure':
        leave_snapshot = True
    if args[-1] == 'terminal':
        print(json.dumps({'returncode': 1, 'result': {'ok': False, 'error': 'refused'},
                          'session_continues': False,
                          'session_ended': {'reason': 'refused', 'exit_code': 1}}), flush=True)
        break
    if args[:1] == ['act'] and args[-1] in ('transient-screen', 'transient-focus'):
        error, error_code = (('screen changed', 'screen_changed')
                             if args[-1] == 'transient-screen'
                             else ('focus changed', 'focus_changed'))
        print(json.dumps({'returncode': 1, 'result': {'ok': False,
              'error': error, 'error_code': error_code}, 'session_continues': True}), flush=True)
        continue
    response = {'returncode': 0, 'result': {'ok': True, 'args': args},
                'session_continues': True}
    print(json.dumps(response, separators=(',', ':')), flush=True)

mark('eof')
if leave_snapshot:
    os._exit(1)
snapshot.unlink(missing_ok=True)
'''


class BrokerHarness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cu-relay-test-')
        self.root = Path(self.tmp.name)
        self.state = self.root / 'cache' / 'agent-computer-use'
        self.state.mkdir(mode=0o700, parents=True)
        self.events = self.root / 'events.jsonl'
        self.child_script = self.root / 'fake_driver.py'
        self.child_script.write_text(FAKE_DRIVER)
        self.child_script.chmod(0o600)
        self.runtime = self.root / 'runtime'
        self.runtime.mkdir(mode=0o700)
        self.socket_path = self.runtime / 'computer-use-wayland' / 'relay.sock'
        self.identity = {'instance': 'fake-instance', 'wl_socket': 'wayland-fake',
                         'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
        self.current_identity = dict(self.identity)
        self.launches = []
        self.broker = self.make_broker()
        self.server = session_remote.UnixSocketServer(self.broker, self.socket_path)
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve, daemon=True)
        self.thread.start()

    def make_broker(self, *, idle_timeout=60, max_response_bytes=None):
        env = dict(os.environ)
        env['FAKE_SESSION_STATE'] = str(self.state)
        env['FAKE_DRIVER_EVENTS'] = str(self.events)

        def launch(child_env):
            self.launches.append(time.monotonic())
            return subprocess.Popen([sys.executable, str(self.child_script)], env=child_env,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, bufsize=0, close_fds=True)

        return session_remote.Broker(
            state_dir=self.state, env=env, launcher=launch,
            readiness=lambda: dict(self.identity),
            compositor_check=lambda expected: self.current_identity == expected,
            cancelled=lambda: os.path.lexists(self.state / 'cancelled'),
            idle_timeout=idle_timeout, start_timeout=3, request_timeout=3,
            max_request_bytes=1024 * 1024,
            max_response_bytes=max_response_bytes or session_remote.MAX_RESPONSE_BYTES)

    def tearDown(self):
        self.stop_server()
        self.tmp.cleanup()

    def stop_server(self):
        server = getattr(self, 'server', None)
        if server is not None:
            server.request_stop()
            thread = getattr(self, 'thread', None)
            if thread is not None:
                thread.join(timeout=4)
            server.close()
            self.server = None

    def exchange(self, value, *, timeout=5):
        return session_remote._exchange(value, self.socket_path, timeout=timeout)

    def raw_exchange(self, raw, *, drop=False):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(3)
        client.connect(str(self.socket_path))
        client.sendall(raw)
        client.shutdown(socket.SHUT_WR)
        if drop:
            client.close()
            return None
        data = bytearray()
        while b'\n' not in data:
            chunk = client.recv(4096)
            if not chunk:
                break
            data.extend(chunk)
        client.close()
        return json.loads(data.decode().strip())

    def wait_for(self, predicate, timeout=4):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(.02)
        self.fail('timed out waiting for broker state')

    def start_task(self, owner='integration-test', *, drop_response=False):
        state = self.exchange({'command': 'status'})
        start_id = session_remote._new_start_id()
        secret = secrets.token_hex(32)
        command = {'command': 'start', 'owner': owner, 'start_id': start_id,
                   'lease_secret': secret, 'broker_generation': state['broker_generation']}
        raw = session_remote._encode_line(command, session_remote.MAX_REQUEST_BYTES)
        if drop_response:
            self.raw_exchange(raw, drop=True)
            response = self.exchange(command)
        else:
            response = self.exchange(command)
        self.assertTrue(response['ok'], response)
        lease = {'owner': owner, 'start_id': start_id, 'lease_secret': secret,
                 'broker_generation': state['broker_generation'],
                 'generation': response['generation']}
        self.wait_for(lambda: (lambda value: value if value['driver'] == 'ready' else None)(
            self.exchange({'command': 'status'})))
        return lease

    def with_lease(self, lease, command, **extra):
        return {'command': command, 'owner': lease['owner'],
                'generation': lease['generation'], 'lease_secret': lease['lease_secret'], **extra}

    def request(self, lease, sequence, args, **extra):
        envelope = {'args': args, 'stdin': '', 'image_policy': 'always'}
        envelope.update(extra)
        return self.exchange(self.with_lease(lease, 'request', sequence=sequence, request=envelope))

    def result(self, lease, sequence):
        return self.exchange(self.with_lease(lease, 'result', sequence=sequence))

    def events_read(self):
        try:
            return [json.loads(line) for line in self.events.read_text().splitlines()]
        except FileNotFoundError:
            return []

    def input_events(self):
        return [row for row in self.events_read() if row['event'] == 'input']


class SessionRemoteIntegration(BrokerHarness):
    def run_cli(self, args):
        output = io.StringIO()
        with patch.object(session_remote, '_default_socket', return_value=self.socket_path), \
                redirect_stdout(output):
            code = session_remote.main(args)
        return code, json.loads(output.getvalue())

    def make_shared_broker(self, base, *, automatic=False):
        self.stop_server()
        self.launches = []
        self.child_environments = []

        def launch(child_env):
            self.launches.append(time.monotonic())
            self.child_environments.append(dict(child_env))
            return subprocess.Popen([sys.executable, str(self.child_script)], env=child_env,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, bufsize=0, close_fds=True)

        with patch.dict(os.environ, base, clear=True):
            self.broker = session_remote.Broker(
                state_dir=self.state, env=None if automatic else base, launcher=launch,
                compositor_check=lambda expected: self.current_identity == expected,
                cancelled=lambda: os.path.lexists(self.state / 'cancelled'),
                idle_timeout=60, start_timeout=3, request_timeout=3,
                max_request_bytes=1024 * 1024)
        self.server = session_remote.UnixSocketServer(self.broker, self.socket_path)
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve, daemon=True)
        self.thread.start()

    def environment_fixture(self, *, signature='fixture-instance', display='wayland-fixture',
                            donor_present=True):
        root = self.root / 'resolver-fixture'
        runtime = root / 'runtime'
        (runtime / 'hypr' / signature).mkdir(parents=True, exist_ok=True)
        runtime.chmod(0o700)
        proc = root / 'proc'
        proc.mkdir(parents=True, exist_ok=True)
        pid = 31337
        (proc / str(pid)).mkdir(parents=True, exist_ok=True)
        rows = [{'instance': signature, 'wl_socket': display, 'pid': pid}]

        def bind_socket(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            connection.bind(str(path))
            connection.close()

        bind_socket(runtime / display)
        bind_socket(runtime / 'hypr' / signature / '.socket.sock')
        donor = {
            'XDG_RUNTIME_DIR': str(runtime), 'WAYLAND_DISPLAY': display,
            'DISPLAY': ':fixture', 'HYPRLAND_INSTANCE_SIGNATURE': signature,
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/fixture/session-bus',
            'XDG_CURRENT_DESKTOP': 'Hyprland', 'XDG_SESSION_DESKTOP': 'Hyprland',
            'XDG_SESSION_TYPE': 'wayland', 'XDG_SEAT': 'seat-fixture', 'XDG_VTNR': '2',
            'USER': os.environ.get('USER', 'james'), 'HOME': str(Path.home()),
            'LOGNAME': os.environ.get('LOGNAME', 'james'), 'PATH': '/fixture/gui-bin:/usr/bin',
            'GDK_BACKEND': 'wayland,x11', 'QT_QPA_PLATFORM': 'wayland;xcb',
            'ELECTRON_OZONE_PLATFORM_HINT': 'wayland', 'MOZ_ENABLE_WAYLAND': '1',
            'DONOR_SECRET': 'private-fixture-secret', 'GTK_IM_MODULE': 'ibus',
        }

        def write_donor(values):
            raw = '\0'.join(f'{key}={value}' for key, value in values.items())
            (proc / str(pid) / 'environ').write_bytes(raw.encode('utf-8', 'surrogateescape'))

        if donor_present:
            write_donor(donor)
        base = {'HOME': str(Path.home()), 'USER': donor['USER'], 'LOGNAME': donor['LOGNAME'],
                'PATH': '/usr/bin:/bin', 'XDG_CACHE_HOME': str(self.root / 'caller-cache'),
                'PYTHONDONTWRITEBYTECODE': '1',
                'FAKE_SESSION_STATE': str(self.state), 'FAKE_DRIVER_EVENTS': str(self.events),
                'GTK_IM_MODULE': 'fcitx'}

        def fake_run(argv, env=None, capture_output=None, text=None, timeout=None):
            if argv[:2] == ['pgrep', '-x']:
                if argv[2] == 'waybar':
                    return types.SimpleNamespace(stdout=str(pid), stderr='', returncode=0)
                return types.SimpleNamespace(stdout='', stderr='', returncode=1)
            if argv == ['hyprctl', '-j', 'instances']:
                return subprocess.CompletedProcess(argv, 0, json.dumps(rows), '')
            raise AssertionError(argv)

        def fake_path(*parts):
            if parts and parts[0] == '/proc':
                return Path(proc, *parts[1:])
            return Path(*parts)

        def activate_mocks(stack):
            stack.enter_context(patch.object(session_remote.cu, 'Path', fake_path))
            stack.enter_context(patch.object(session_remote.cu, '_system_runtime_dir',
                                              return_value=root / 'no-system-runtime'))
            stack.enter_context(patch.object(session_remote.cu.subprocess, 'run',
                                              side_effect=fake_run))

        def replace(values, new_signature, new_display):
            new_dir = runtime / 'hypr' / new_signature
            new_dir.mkdir(parents=True, exist_ok=True)
            bind_socket(runtime / new_display)
            bind_socket(new_dir / '.socket.sock')
            values = dict(values, XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY=new_display,
                          HYPRLAND_INSTANCE_SIGNATURE=new_signature)
            rows[:] = [{'instance': new_signature, 'wl_socket': new_display, 'pid': pid}]
            write_donor(values)
            return values

        identity = {'instance': signature, 'wl_socket': display,
                    'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
        self.current_identity = dict(identity)
        self.identity = dict(identity)
        return {'root': root, 'runtime': runtime, 'proc': proc, 'pid': pid,
                'donor': donor, 'base': base, 'rows': rows, 'identity': identity,
                'write_donor': write_donor, 'replace': replace,
                'activate_mocks': activate_mocks}

    def finish_owned_task(self, lease):
        self.exchange(self.with_lease(lease, 'finish'))
        final = self.wait_for(lambda: (lambda value: value if value['state'] == 'finished' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(final['driver'], 'stopped')
        self.assertEqual(final['guardian'], 'clean')
        self.assertFalse((self.state / 'session.json').exists())
        return final

    def test_broker_handle_accepts_a11y_and_rejects_unlisted_command(self):
        initial = self.broker.handle({'command': 'status'})
        start = {'command': 'start', 'owner': 'pick4a11y-regression',
                 'start_id': session_remote._new_start_id(),
                 'lease_secret': secrets.token_hex(32),
                 'broker_generation': initial['broker_generation']}
        started = self.broker.handle(start)
        self.assertTrue(started['ok'], started)
        lease = {'owner': start['owner'], 'generation': started['generation'],
                 'lease_secret': start['lease_secret']}
        ready = self.wait_for(lambda: (lambda value: value if value['driver'] == 'ready' else None)(
            self.broker.handle({'command': 'status'})))
        self.assertEqual(ready['state'], 'running')

        envelopes = [
            ['a11y', 'query', '--pid', '764773', '--name', 'Home'],
            ['a11y', 'observe', '--pid', '764773'],
            ['a11y', 'ground', 'e1', '--snapshot', '/tmp/g1-snapshot.json',
             '--address', '0xabc'],
        ]
        for sequence, args in enumerate(envelopes, 1):
            accepted = self.broker.handle({
                'command': 'request', **lease, 'sequence': sequence,
                'request': {'args': args, 'stdin': '', 'image_policy': 'always'}})
            self.assertEqual(accepted, {'ok': True, 'status': 'accepted',
                                        'sequence': sequence})
            result = self.broker.handle({
                'command': 'result', **lease, 'sequence': sequence})
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(result['response']['result']['args'], args)

        with self.assertRaises(session_remote.BrokerError) as caught:
            self.broker.handle({
                'command': 'request', **lease, 'sequence': 4,
                'request': {'args': ['rm', '-rf', '/'], 'stdin': '',
                            'image_policy': 'always'}})
        self.assertEqual(caught.exception.error, 'unsupported_command')
        self.assertEqual(self.broker.handle({'command': 'status'})['next_sequence'], 4)
        self.finish_owned_task(lease)

    def start_command(self, owner='environment-test'):
        status = self.exchange({'command': 'status'})
        return {'command': 'start', 'owner': owner,
                'start_id': session_remote._new_start_id(),
                'lease_secret': secrets.token_hex(32),
                'broker_generation': status['broker_generation']}

    def test_bare_injected_broker_resolves_and_child_inherits_all_allowlisted_keys(self):
        fixture = self.environment_fixture()
        base = dict(fixture['base'])
        self.make_shared_broker(base)
        seen = []

        def ready(env):
            seen.append(dict(env))
            return {'instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                    'wl_socket': env['WAYLAND_DISPLAY'],
                    'commit': 'fake-commit', 'abi_hash': 'fake-abi'}

        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            stack.enter_context(patch.object(session_remote, 'native_readiness', side_effect=ready))
            lease = self.start_task('bare-broker')
            resolver.assert_called_once_with(self.broker.base_env, refresh=False)
            self.assertEqual(self.broker.env, seen[0])
        expected = {key: fixture['donor'][key] for key in session_remote.cu.SESSION_KEYS}
        event = next(row for row in self.events_read() if row['event'] == 'environment')
        self.assertEqual(event['values'], expected)
        self.assertEqual({key: self.child_environments[0][key]
                          for key in session_remote.cu.SESSION_KEYS}, expected)
        self.assertNotIn('GTK_IM_MODULE', self.child_environments[0])
        self.assertNotIn('DONOR_SECRET', self.child_environments[0])
        self.assertNotIn('CU_SESSION_TOKEN', self.child_environments[0])
        self.request(lease, 1, ['doctor'])
        done = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
            self.result(lease, 1)))
        self.assertEqual(done['response']['result']['args'], ['doctor'])
        self.finish_owned_task(lease)

    def test_idle_broker_can_start_before_login_then_discover_on_new_start(self):
        fixture = self.environment_fixture(donor_present=False)
        self.make_shared_broker(fixture['base'], automatic=True)
        self.assertEqual(self.exchange({'command': 'status'})['state'], 'idle')
        seen = []

        def ready(env):
            seen.append(dict(env))
            identity = {'instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                        'wl_socket': env['WAYLAND_DISPLAY'],
                        'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
            self.current_identity = dict(identity)
            return identity

        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            stack.enter_context(patch.object(session_remote, 'native_readiness', side_effect=ready))
            resolver.assert_not_called()
            fixture['write_donor'](fixture['donor'])
            lease = self.start_task('login-arrived-later')
            resolver.assert_called_once_with(self.broker.base_env, refresh=True)
        self.assertEqual(seen[0]['HYPRLAND_INSTANCE_SIGNATURE'], 'fixture-instance')
        self.finish_owned_task(lease)

    def test_automatic_broker_refreshes_stale_daemon_tuple_from_base_env(self):
        fixture = self.environment_fixture()
        base = dict(fixture['base'], XDG_RUNTIME_DIR=fixture['donor']['XDG_RUNTIME_DIR'],
                    WAYLAND_DISPLAY='wayland-stale', HYPRLAND_INSTANCE_SIGNATURE='stale-signature',
                    DISPLAY=':stale')
        self.make_shared_broker(base, automatic=True)

        def ready(env):
            self.current_identity = {'instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                                     'wl_socket': env['WAYLAND_DISPLAY'],
                                     'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
            return dict(self.current_identity)

        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            stack.enter_context(patch.object(session_remote, 'native_readiness', side_effect=ready))
            lease = self.start_task('automatic-broker')
            resolver.assert_called_once_with(self.broker.base_env, refresh=True)
        self.assertEqual(self.broker.env['HYPRLAND_INSTANCE_SIGNATURE'], 'fixture-instance')
        self.assertEqual(self.broker.env['DISPLAY'], ':fixture')
        self.assertNotEqual(self.broker.env['WAYLAND_DISPLAY'], 'wayland-stale')
        self.finish_owned_task(lease)

    def test_explicit_stale_tuple_refuses_switch_and_returns_bounded_diagnostic(self):
        fixture = self.environment_fixture()
        base = dict(fixture['base'], XDG_RUNTIME_DIR=fixture['donor']['XDG_RUNTIME_DIR'],
                    WAYLAND_DISPLAY='wayland-stale', HYPRLAND_INSTANCE_SIGNATURE='stale-signature')
        self.make_shared_broker(base)
        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            response = self.exchange(self.start_command('explicit-stale'))
            resolver.assert_called_once_with(self.broker.base_env, refresh=False)
        self.assertEqual(response, {'ok': False, 'error': 'native_unavailable',
                                    'stage': 'compositor',
                                    'diagnostic': 'gui_environment_unavailable'})
        self.assertNotIn('stale-signature', json.dumps(response))
        self.assertEqual(self.launches, [])

    def test_automatic_start_retries_once_only_for_compositor_readiness(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'], automatic=True)
        first = {**fixture['base'], **{key: fixture['donor'][key]
                                      for key in session_remote.cu.SESSION_KEYS}}
        second = dict(first, DISPLAY=':fresh-retry')
        identity = {'instance': second['HYPRLAND_INSTANCE_SIGNATURE'],
                    'wl_socket': second['WAYLAND_DISPLAY'],
                    'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
        self.current_identity = dict(identity)
        readiness_error = session_remote.BrokerError(
            'native_unavailable', 'private compositor race', stage='compositor',
            diagnostic='gui_environment_unavailable')
        with patch.object(session_remote.cu, 'environment',
                          side_effect=[first, second]) as resolver, \
                patch.object(session_remote, 'native_readiness',
                             side_effect=[readiness_error, identity]) as readiness:
            lease = self.start_task('compositor-retry')
        self.assertEqual(resolver.call_count, 2)
        for call in resolver.call_args_list:
            self.assertEqual(call.args[0], self.broker.base_env)
            self.assertEqual(call.kwargs, {'refresh': True})
        self.assertEqual(readiness.call_args_list[0].args, (first,))
        self.assertEqual(readiness.call_args_list[1].args, (second,))
        self.assertEqual(self.broker.env['DISPLAY'], ':fresh-retry')
        self.assertEqual(len(self.launches), 1)
        self.finish_owned_task(lease)

    def test_non_compositor_readiness_failure_is_not_retried(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'], automatic=True)
        candidate = {**fixture['base'], **{key: fixture['donor'][key]
                                          for key in session_remote.cu.SESSION_KEYS}}
        error = session_remote.BrokerError('native_unavailable', 'private glass detail',
                                           stage='glass', diagnostic='liquid_backend_not_ready')
        with patch.object(session_remote.cu, 'environment', return_value=candidate) as resolver, \
                patch.object(session_remote, 'native_readiness', side_effect=error) as readiness:
            response = self.exchange(self.start_command('glass-failure'))
        resolver.assert_called_once_with(self.broker.base_env, refresh=True)
        readiness.assert_called_once_with(candidate)
        self.assertEqual(response, {'ok': False, 'error': 'native_unavailable',
                                    'stage': 'glass', 'diagnostic': 'liquid_backend_not_ready'})
        self.assertNotIn('private glass detail', json.dumps(response))
        self.assertEqual(self.launches, [])

    def test_discovery_failure_is_bounded_and_does_not_reach_child_or_readiness(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'], automatic=True)
        with patch.object(session_remote.cu, 'environment',
                          side_effect=RuntimeError('private environment values')) as resolver, \
                patch.object(session_remote, 'native_readiness') as readiness:
            response = self.exchange(self.start_command('discovery-failure'))
        resolver.assert_called_once_with(self.broker.base_env, refresh=True)
        readiness.assert_not_called()
        self.assertEqual(response, {'ok': False, 'error': 'native_unavailable',
                                    'stage': 'compositor',
                                    'diagnostic': 'gui_environment_unavailable'})
        self.assertNotIn('private environment values', json.dumps(response))
        self.assertEqual(self.launches, [])

    def test_start_gates_and_duplicate_start_do_not_discover(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'])
        candidate = {**fixture['base'], **{key: fixture['donor'][key]
                                          for key in session_remote.cu.SESSION_KEYS}}
        identity = {'instance': candidate['HYPRLAND_INSTANCE_SIGNATURE'],
                    'wl_socket': candidate['WAYLAND_DISPLAY'],
                    'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
        self.current_identity = dict(identity)
        cancelled = self.state / 'cancelled'
        cancelled.write_text('fixture latch')
        cancelled.chmod(0o600)
        with patch.object(session_remote.cu, 'environment', return_value=candidate) as resolver, \
                patch.object(session_remote, 'native_readiness', return_value=identity):
            self.assertEqual(self.exchange(self.start_command('cancel-gate'))['error'], 'cancelled')
            resolver.assert_not_called()
            cancelled.unlink()

            self.broker.env['CU_SESSION_TOKEN'] = 'x' * 32
            self.assertEqual(self.exchange(self.start_command('nested-gate'))['error'], 'nested_session')
            resolver.assert_not_called()
            self.broker.env.pop('CU_SESSION_TOKEN')

            retained = self.state / 'session.json'
            retained.write_text(json.dumps({'version': 4, 'token': 'b' * 32}))
            retained.chmod(0o600)
            self.assertEqual(self.exchange(self.start_command('recovery-gate'))['error'],
                             'recovery_required')
            resolver.assert_not_called()
            retained.unlink()

            first = self.start_command('first-owner')
            started = self.exchange(first)
            self.assertTrue(started['ok'], started)
            self.wait_for(lambda: self.exchange({'command': 'status'})['driver'] == 'ready')
            resolver.assert_called_once_with(self.broker.base_env, refresh=False)

            busy = self.exchange(self.start_command('second-owner'))
            self.assertEqual(busy['error'], 'busy')
            duplicate = self.exchange(first)
            self.assertEqual(duplicate, started)
            resolver.assert_called_once()

        lease = {'owner': first['owner'], 'start_id': first['start_id'],
                 'lease_secret': first['lease_secret'],
                 'broker_generation': first['broker_generation'],
                 'generation': started['generation']}
        self.finish_owned_task(lease)

    def test_completed_tasks_after_relogin_resolve_distinct_frozen_environments(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'], automatic=True)

        def ready(env):
            identity = {'instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                        'wl_socket': env['WAYLAND_DISPLAY'],
                        'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
            self.current_identity = dict(identity)
            return identity

        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            stack.enter_context(patch.object(session_remote, 'native_readiness', side_effect=ready))
            first = self.start_task('before-relogin')
            first_tuple = (self.broker.env['WAYLAND_DISPLAY'],
                           self.broker.env['HYPRLAND_INSTANCE_SIGNATURE'])
            self.finish_owned_task(first)
            fixture['replace'](fixture['donor'], 'after-relogin', 'wayland-after-relogin')
            second = self.start_task('after-relogin')
            second_tuple = (self.broker.env['WAYLAND_DISPLAY'],
                            self.broker.env['HYPRLAND_INSTANCE_SIGNATURE'])
            self.assertNotEqual(first_tuple, second_tuple)
            self.assertEqual(second_tuple, ('wayland-after-relogin', 'after-relogin'))
            self.assertEqual(resolver.call_count, 2)
            self.finish_owned_task(second)

    def test_relogin_during_task_stops_it_without_rediscovery_or_second_launch(self):
        fixture = self.environment_fixture()
        self.make_shared_broker(fixture['base'], automatic=True)

        def ready(env):
            identity = {'instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                        'wl_socket': env['WAYLAND_DISPLAY'],
                        'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
            self.current_identity = dict(identity)
            return identity

        with ExitStack() as stack:
            fixture['activate_mocks'](stack)
            resolver = stack.enter_context(patch.object(
                session_remote.cu, 'environment', wraps=session_remote.cu.environment))
            stack.enter_context(patch.object(session_remote, 'native_readiness', side_effect=ready))
            lease = self.start_task('active-before-relogin')
            fixture['replace'](fixture['donor'], 'new-active-login', 'wayland-new-login')
            self.current_identity = {'instance': 'new-active-login',
                                    'wl_socket': 'wayland-new-login',
                                    'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
            stopped = self.request(lease, 1, ['doctor'])
            self.assertEqual(stopped['error'], 'compositor_changed')
            self.wait_for(lambda: self.exchange({'command': 'status'})['state'] == 'failed')
            self.assertEqual(resolver.call_count, 1)
            self.assertEqual(len(self.launches), 1)
            self.assertEqual(self.input_events(), [])
            stopped = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
                self.exchange({'command': 'status'})))
            self.assertIn(stopped['driver'], ('stopped', 'failed'))

    def test_idle_status_and_private_socket_start(self):
        response = self.exchange({'command': 'status'})
        self.assertEqual(response['state'], 'idle')
        self.assertIsNone(response['owner'])
        expected = hashlib.sha256(Path(session_remote.__file__).resolve().read_bytes()).hexdigest()
        self.assertEqual(response['loaded_code_sha256'], expected)
        self.assertIsInstance(response['started_git_head'], str)
        info = self.socket_path.lstat()
        self.assertTrue(stat.S_ISSOCK(info.st_mode))
        self.assertEqual(stat.S_IMODE(info.st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.socket_path.parent.stat().st_mode), 0o700)
        self.assertEqual(self.launches, [])

    def test_private_envsteal_proof_channel_reports_repo_sources_and_hash(self):
        parent, child = socket.socketpair()
        self.addCleanup(parent.close)
        self.addCleanup(child.close)
        parent.settimeout(2)
        expected = hashlib.sha256(
            (Path(session_remote.cu.__file__).resolve()).read_bytes()).hexdigest()
        parent.sendall(json.dumps({'channel': 'envsteal-proof-v1',
                                   'expected_cu_sha256': expected}).encode())
        session_remote._envsteal_test_proof(child.fileno())
        proof = json.loads(parent.recv(2048).decode())
        self.assertEqual(proof['cu_path'], str(Path(__file__).resolve().parents[1] / 'scripts' / 'cu.py'))
        self.assertEqual(proof['cu_sha256'], expected)
        self.assertEqual(proof['session_remote_path'], str(Path(session_remote.__file__).resolve()))

    def test_start_returns_bounded_readiness_stage_and_diagnostic(self):
        def refuse():
            raise session_remote.BrokerError('native_unavailable', 'private detail',
                                              stage='guard',
                                              diagnostic='cursor_guard_missing')
        self.broker.readiness = refuse
        state = self.exchange({'command': 'status'})
        response = self.exchange({'command': 'start', 'owner': 'stage-test',
                                  'start_id': session_remote._new_start_id(),
                                  'lease_secret': secrets.token_hex(32),
                                  'broker_generation': state['broker_generation']})
        self.assertEqual(response, {'ok': False, 'error': 'native_unavailable',
                                    'stage': 'guard', 'diagnostic': 'cursor_guard_missing'})
        self.assertNotIn('private detail', json.dumps(response))
        self.assertEqual(self.launches, [])

    def test_production_launch_uses_fixed_existing_session_driver_argv(self):
        with patch.object(session_remote.subprocess, 'Popen') as popen:
            session_remote.Broker._launch({'PATH': '/usr/bin'})
        args, kwargs = popen.call_args
        python = '/usr/bin/python3'
        cu = str(session_remote.CU)
        self.assertEqual(args[0], [python, cu, 'session', '--', python, cu, 'session-driver'])
        self.assertEqual(kwargs['stdin'], subprocess.PIPE)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertFalse(kwargs.get('shell', False))

    def test_lost_start_response_reconnects_to_same_generation(self):
        lease = self.start_task(drop_response=True)
        self.assertEqual(len(self.launches), 1)

    def test_client_start_then_83_status_polls_are_ok_while_driver_is_starting(self):
        self.broker.start_timeout = 15
        ready_gate = self.root / 'allow-driver-ready'
        self.broker.env['FAKE_READY_GATE'] = str(ready_gate)
        lease_file = self.root / 'starting.lease'
        code, started = self.run_cli(['start', '--owner', 'starting-test',
                                      '--lease-file', str(lease_file)])
        self.assertEqual(code, 0, started)
        self.assertTrue(started['ok'])
        self.assertEqual(started['status'], 'starting')

        began = time.monotonic()
        for _ in range(83):
            code, status = self.run_cli(['status', '--lease-file', str(lease_file)])
            self.assertEqual(code, 0, status)
            self.assertTrue(status['ok'], status)
            self.assertEqual(status['state'], 'starting')
            self.assertEqual(status['driver'], 'starting')
        self.assertLess(time.monotonic() - began, 10)

        ready_gate.touch()
        self.wait_for(lambda: (lambda result: result if result[1].get('state') == 'running' else None)(
            self.run_cli(['status', '--lease-file', str(lease_file)])))
        code, finished = self.run_cli(['finish', '--lease-file', str(lease_file)])
        self.assertEqual(code, 0, finished)
        self.assertEqual(finished['status'], 'finished')

    def test_status_authorization_failure_is_exposed_by_broker_status(self):
        lease_file = self.root / 'tamper.lease'
        code, started = self.run_cli(['start', '--owner', 'tamper-test',
                                      '--lease-file', str(lease_file)])
        self.assertEqual(code, 0, started)
        lease = json.loads(lease_file.read_text())
        self.wait_for(lambda: (lambda result: result if result[1].get('state') == 'running' else None)(
            self.run_cli(['status', '--lease-file', str(lease_file)])))
        original_generation = lease['generation']
        lease['generation'] = '0' * 32 if original_generation != '0' * 32 else '1' * 32
        session_remote._replace_lease(lease_file, lease)

        began = time.monotonic()
        for _ in range(83):
            code, refused = self.run_cli(['status', '--lease-file', str(lease_file)])
            self.assertEqual(code, 1)
            self.assertEqual(refused, {'ok': False, 'error': 'invalid_lease'})
        self.assertLess(time.monotonic() - began, 10)
        code, status = self.run_cli(['status'])
        self.assertEqual(code, 0, status)
        self.assertEqual(status['last_status_error'], 'invalid_lease')

        lease['generation'] = original_generation
        session_remote._replace_lease(lease_file, lease)
        code, finished = self.run_cli(['finish', '--lease-file', str(lease_file)])
        self.assertEqual(code, 0, finished)
        self.assertEqual(finished['status'], 'finished')

    def test_refused_start_error_is_exposed_by_broker_status(self):
        def refuse_readiness():
            raise session_remote.BrokerError('native_unavailable', 'fixture refusal')

        self.broker.readiness = refuse_readiness
        lease_file = self.root / 'refused.lease'
        code, started = self.run_cli(['start', '--owner', 'refused-test',
                                      '--lease-file', str(lease_file)])
        self.assertEqual(code, 1)
        self.assertEqual(started['error'], 'native_unavailable')
        code, status = self.run_cli(['status'])
        self.assertEqual(code, 0, status)
        self.assertEqual(status['last_start_error'], 'native_unavailable')

    def test_public_cli_uses_private_lease_and_multiline_request_file(self):
        lease_file = self.root / 'task.lease'
        code, started = self.run_cli(['start', '--owner', 'cli-test',
                                      '--lease-file', str(lease_file)])
        self.assertEqual(code, 0)
        self.assertEqual(started['status'], 'starting')
        self.assertEqual(stat.S_IMODE(lease_file.stat().st_mode), 0o600)
        lease = json.loads(lease_file.read_text())
        self.wait_for(lambda: (lambda value: value if value['driver'] == 'ready' else None)(
            self.exchange({'command': 'status'})))

        request_file = self.root / 'request.json'
        request_file.write_text('{\n  "args": ["doctor", "from-file"]\n}\n')
        request_file.chmod(0o600)
        code, accepted = self.run_cli(['request', '--lease-file', str(lease_file),
                                       '--sequence', '1', '--request', str(request_file)])
        self.assertEqual(code, 0)
        self.assertEqual(accepted['status'], 'accepted')
        done = self.wait_for(lambda: (lambda result: result if result.get('status') == 'completed' else None)(
            self.run_cli(['result', '--lease-file', str(lease_file), '--sequence', '1'])[1]))
        self.assertEqual(done['response']['result']['args'], ['doctor', 'from-file'])
        code, finished = self.run_cli(['finish', '--lease-file', str(lease_file)])
        self.assertEqual(code, 0)
        self.assertEqual(finished['status'], 'finished')
        self.assertEqual(json.loads(lease_file.read_text())['generation'], lease['generation'])
        repeated = self.exchange({'command': 'start', 'owner': lease['owner'],
                                  'start_id': lease['start_id'],
                                  'lease_secret': lease['lease_secret'],
                                  'broker_generation': lease['broker_generation']})
        self.assertEqual(repeated['generation'], lease['generation'])
        self.assertEqual(len(self.launches), 1)

    def test_second_owner_is_busy_and_never_starts_a_second_child(self):
        self.start_task('first-owner')
        status = self.exchange({'command': 'status'})
        response = self.exchange({'command': 'start', 'owner': 'second-owner',
                                  'start_id': session_remote._new_start_id(),
                                  'lease_secret': secrets.token_hex(32),
                                  'broker_generation': status['broker_generation']})
        self.assertFalse(response['ok'])
        self.assertEqual(response['error'], 'busy')
        self.assertEqual(len(self.launches), 1)

    def test_start_refuses_cancellation_and_retained_session_without_child(self):
        status = self.exchange({'command': 'status'})
        marker = self.state / 'cancelled'
        marker.write_text('fixture latch')
        marker.chmod(0o600)
        start_id = session_remote._new_start_id()
        first = {'command': 'start', 'owner': 'gate-test', 'start_id': start_id,
                 'lease_secret': secrets.token_hex(32),
                 'broker_generation': status['broker_generation']}
        cancelled = self.exchange(first)
        self.assertEqual(cancelled['error'], 'cancelled')
        self.assertEqual(marker.read_text(), 'fixture latch')
        marker.unlink()

        snapshot = self.state / 'session.json'
        snapshot.write_text(json.dumps({'version': 4, 'token': 'b' * 32}))
        snapshot.chmod(0o600)
        recovered = self.exchange({'command': 'start', 'owner': 'gate-test',
                                   'start_id': session_remote._new_start_id(),
                                   'lease_secret': secrets.token_hex(32),
                                   'broker_generation': status['broker_generation']})
        self.assertEqual(recovered['error'], 'recovery_required')
        self.assertTrue(snapshot.exists())
        self.assertEqual(len(self.launches), 0)

    def test_lost_accept_deduplicates_and_result_survives_disconnect(self):
        lease = self.start_task()
        envelope = {'args': ['doctor', 'slow'], 'stdin': '', 'image_policy': 'always'}
        request = self.with_lease(lease, 'request', sequence=1, request=envelope)
        raw = session_remote._encode_line(request, session_remote.MAX_REQUEST_BYTES)
        self.raw_exchange(raw, drop=True)
        self.wait_for(lambda: self.input_events())
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['response']['result']['args'], ['doctor', 'slow'])
        duplicate = self.request(lease, 1, ['doctor', 'slow'])
        self.assertEqual(duplicate['status'], 'completed')
        self.assertEqual(len(self.input_events()), 1)

    def test_result_long_poll_waits_for_completion_without_blocking_status(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'slow'])['status'], 'accepted')
        started = threading.Event()
        result_box = []

        def long_poll():
            started.set()
            result_box.append(self.result(lease, 1))

        waiter = threading.Thread(target=long_poll)
        began = time.monotonic()
        waiter.start()
        self.assertTrue(started.wait(1))
        self.wait_for(lambda: len(self.server.client_threads) >= 1, timeout=1)
        status = self.exchange({'command': 'status'}, timeout=1)
        self.assertEqual(status['state'], 'running')
        waiter.join(timeout=2)
        self.assertFalse(waiter.is_alive(), 'long-poll did not return after request completion')
        self.assertEqual(result_box[0]['status'], 'completed')
        self.assertGreaterEqual(time.monotonic() - began, .15)

    def test_sequence_conflict_and_expired_older_result(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'one'])['status'], 'accepted')
        self.wait_for(lambda: self.result(lease, 1).get('status') == 'completed')
        conflict = self.request(lease, 1, ['doctor', 'different'])
        self.assertFalse(conflict['ok'])
        self.assertEqual(conflict['error'], 'conflict')
        self.assertEqual(self.request(lease, 2, ['doctor', 'two'])['status'], 'accepted')
        self.wait_for(lambda: self.result(lease, 2).get('status') == 'completed')
        older = self.result(lease, 1)
        self.assertFalse(older['ok'])
        self.assertEqual(older['error'], 'expired')
        self.assertEqual([row['args'] for row in self.input_events()],
                         [['doctor', 'one'], ['doctor', 'two']])

    def test_partial_and_oversized_socket_json_are_refused_before_start(self):
        partial = self.raw_exchange(b'{"command":', drop=False)
        self.assertEqual(partial['error'], 'invalid_json')
        self.assertEqual(self.launches, [])

        self.stop_server()
        small_broker = self.make_broker()
        self.broker = small_broker
        self.server = session_remote.UnixSocketServer(small_broker, self.socket_path,
                                                       max_request_bytes=512)
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve, daemon=True)
        self.thread.start()
        oversized = self.raw_exchange(b'x' * 513, drop=False)
        self.assertEqual(oversized['error'], 'too_large')
        self.assertEqual(self.launches, [])

    def test_child_crash_returns_unknown_and_is_never_restarted(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'crash'])['status'], 'accepted')
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'unknown' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['error'], 'driver_eof')
        replay = self.request(lease, 1, ['doctor', 'crash'])
        self.assertEqual(replay['status'], 'unknown')
        self.assertEqual(len(self.input_events()), 1)
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['recovery'], 'required')
        self.assertEqual(len(self.launches), 1)
        next_start = self.exchange({'command': 'start', 'owner': 'new-owner',
                                    'start_id': session_remote._new_start_id(),
                                    'lease_secret': secrets.token_hex(32),
                                    'broker_generation': status['broker_generation']})
        self.assertEqual(next_start['error'], 'recovery_required')
        self.assertEqual(len(self.launches), 1)

    def test_partial_driver_json_marks_outcome_unknown(self):
        lease = self.start_task()
        self.request(lease, 1, ['doctor', 'partial'])
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'unknown' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['error'], 'partial_response')
        self.assertEqual(len(self.launches), 1)

    def test_terminal_driver_error_stops_when_contract_refuses_continuation(self):
        lease = self.start_task()
        self.request(lease, 1, ['doctor', 'terminal'])
        failure = self.wait_for(lambda: (lambda value: value if value.get('status') == 'failed' else None)(
            self.result(lease, 1)))
        self.assertEqual(failure['response']['returncode'], 1)
        replay = self.request(lease, 1, ['doctor', 'terminal'])
        self.assertEqual(replay['status'], 'failed')
        stopped = self.request(lease, 2, ['doctor', 'after-terminal'])
        self.assertEqual(stopped['error'], 'task_stopped')
        self.assertEqual(len(self.input_events()), 1)

    def test_screen_and_focus_transient_refusals_keep_existing_driver_alive(self):
        lease = self.start_task()
        for sequence, suffix, error, error_code in (
                (1, 'transient-screen', 'screen changed', 'screen_changed'),
                (2, 'transient-focus', 'focus changed', 'focus_changed')):
            self.assertEqual(self.request(lease, sequence, ['act', suffix])['status'], 'accepted')
            refusal = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
                self.result(lease, sequence)))
            self.assertEqual(refusal['response']['result']['error'], error)
            self.assertEqual(refusal['response']['result']['error_code'], error_code)
            self.assertIs(refusal['response']['session_continues'], True)
        self.assertEqual(self.request(lease, 3, ['doctor', 'replanned'])['status'], 'accepted')
        self.wait_for(lambda: self.result(lease, 3).get('status') == 'completed')
        status = self.exchange({'command': 'status'})
        self.assertEqual(status['state'], 'running')
        self.assertEqual(status['generation'], lease['generation'])
        self.assertEqual(len(self.launches), 1)
        self.assertEqual(len(self.input_events()), 3)

    def test_typed_preflight_refusal_observe_and_valid_request_share_generation(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'typed-preflight'])['status'], 'accepted')
        refusal = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
            self.result(lease, 1)))
        self.assertEqual(refusal['response']['returncode'], 1)
        self.assertTrue(refusal['response']['result']['recoverable'])
        self.assertIs(refusal['response']['session_continues'], True)

        for sequence, args in ((2, ['observe', '--screen', 'test', '--verbose']),
                               (3, ['doctor', 'after-preflight'])):
            self.assertEqual(self.request(lease, sequence, args)['status'], 'accepted')
            completed = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
                self.result(lease, sequence)))
            self.assertIs(completed['response']['session_continues'], True)
            status = self.exchange({'command': 'status'})
            self.assertEqual(status['state'], 'running')
            self.assertEqual(status['generation'], lease['generation'])

        self.assertEqual([row['args'] for row in self.input_events()],
                         [['doctor', 'typed-preflight'],
                          ['observe', '--screen', 'test', '--verbose'],
                          ['doctor', 'after-preflight']])
        self.assertEqual(len(self.launches), 1)

    def test_forged_recoverable_with_driver_false_terminates(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'forged-false'])['status'], 'accepted')
        failure = self.wait_for(lambda: (lambda value: value if value.get('status') == 'failed' else None)(
            self.result(lease, 1)))
        self.assertTrue(failure['response']['result']['recoverable'])
        self.assertIs(failure['response']['session_continues'], False)
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['generation'], lease['generation'])
        self.assertEqual(self.request(lease, 2, ['doctor', 'must-not-run'])['error'], 'task_stopped')
        self.assertEqual(len(self.input_events()), 1)

    def test_forged_recoverable_without_driver_field_terminates(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'forged-absent'])['status'], 'accepted')
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'unknown' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['error'], 'invalid_driver_response')
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['generation'], lease['generation'])
        self.assertEqual(self.request(lease, 2, ['doctor', 'must-not-run'])['error'], 'task_stopped')
        self.assertEqual(len(self.input_events()), 1)

    def assert_malformed_response_terminates(self, suffix):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', suffix])['status'], 'accepted')
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'unknown' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['error'], 'invalid_driver_response')
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['generation'], lease['generation'])
        self.assertEqual(self.request(lease, 2, ['doctor', 'must-not-run'])['error'], 'task_stopped')
        self.assertEqual(len(self.input_events()), 1)
        self.assertEqual(len(self.launches), 1)

    def test_malformed_returncode_with_true_flag_terminates(self):
        self.assert_malformed_response_terminates('malformed-true')

    def test_nonboolean_session_continues_terminates(self):
        self.assert_malformed_response_terminates('malformed-nonboolean')

    def test_missing_session_continues_terminates(self):
        self.assert_malformed_response_terminates('malformed-missing')

    def test_cleanup_failure_after_finish_keeps_task_terminal(self):
        lease = self.start_task()
        self.assertEqual(self.request(lease, 1, ['doctor', 'cleanup-failure'])['status'], 'accepted')
        completed = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
            self.result(lease, 1)))
        self.assertIs(completed['response']['session_continues'], True)
        self.exchange(self.with_lease(lease, 'finish'))
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['error'], 'cleanup_failed')
        self.assertEqual(status['guardian'], 'recovery_required')
        self.assertEqual(status['generation'], lease['generation'])
        self.assertEqual(self.request(lease, 2, ['doctor', 'must-not-run'])['error'], 'task_stopped')
        self.assertEqual(len(self.input_events()), 1)

    def test_oversized_driver_json_is_drained_and_not_replayed(self):
        self.stop_server()
        self.broker = self.make_broker(max_response_bytes=1024)
        self.server = session_remote.UnixSocketServer(self.broker, self.socket_path)
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve, daemon=True)
        self.thread.start()
        lease = self.start_task()
        self.request(lease, 1, ['doctor', 'oversized'])
        result = self.wait_for(lambda: (lambda value: value if value.get('status') == 'unknown' else None)(
            self.result(lease, 1)))
        self.assertEqual(result['error'], 'response_too_large')
        self.wait_for(lambda: not _process_alive(self.broker.task.process))
        self.assertEqual(len(self.launches), 1)

    def test_stale_socket_is_removed_only_after_lock_and_no_listener(self):
        self.stop_server()
        self.socket_path.parent.mkdir(mode=0o700, exist_ok=True)
        stale = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        stale.bind(str(self.socket_path))
        os.chmod(self.socket_path, 0o600)
        stale.close()
        broker = self.make_broker()
        server = session_remote.UnixSocketServer(broker, self.socket_path)
        server.bind()
        self.assertTrue(stat.S_ISSOCK(self.socket_path.lstat().st_mode))
        server.close()

    def test_duplicate_broker_refuses_existing_lock(self):
        second = session_remote.UnixSocketServer(self.make_broker(), self.socket_path)
        with self.assertRaises(session_remote.BrokerError) as caught:
            second.bind()
        self.assertEqual(caught.exception.error, 'broker_running')
        second.close()

    def test_symlink_socket_path_is_refused_without_touching_target(self):
        self.stop_server()
        target = self.runtime / 'unrelated-file'
        target.write_text('keep')
        self.socket_path.symlink_to(target)
        server = session_remote.UnixSocketServer(self.make_broker(), self.socket_path)
        with self.assertRaises(session_remote.BrokerError) as caught:
            server.bind()
        self.assertEqual(caught.exception.error, 'unsafe_socket')
        self.assertEqual(target.read_text(), 'keep')
        server.close()

    def test_explicit_finish_waits_for_supervisor_cleanup_order(self):
        lease = self.start_task()
        self.request(lease, 1, ['doctor', 'slow'])
        self.wait_for(lambda: self.result(lease, 1).get('status') == 'completed')
        response = self.exchange(self.with_lease(lease, 'finish'))
        self.assertIn(response['status'], ('cleaning', 'finished'))
        final = self.wait_for(lambda: (lambda value: value if value['state'] == 'finished' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(final['guardian'], 'clean')
        rows = self.events_read()
        names = [row['event'] for row in rows]
        self.assertLess(names.index('input'), names.index('eof'))
        self.assertEqual(len(self.input_events()), 1)

    def test_sigterm_path_drains_active_request_then_closes_driver(self):
        lease = self.start_task()
        self.request(lease, 1, ['doctor', 'slow'])
        self.wait_for(lambda: self.input_events())
        self.server.handle_signal(signal.SIGTERM, None)
        self.thread.join(timeout=4)
        self.assertFalse(self.thread.is_alive())
        rows = self.events_read()
        names = [row['event'] for row in rows]
        self.assertLess(names.index('input'), names.index('eof'))
        self.assertEqual(len([row for row in rows if row['event'] == 'input']), 1)

    def test_idle_timeout_finishes_without_transferring_owner(self):
        self.stop_server()
        self.broker = self.make_broker(idle_timeout=.15)
        self.server = session_remote.UnixSocketServer(self.broker, self.socket_path)
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve, daemon=True)
        self.thread.start()
        self.start_task()
        status = self.wait_for(lambda: (lambda value: value if value['state'] == 'finished' else None)(
            self.exchange({'command': 'status'})), timeout=4)
        self.assertEqual(status['stop_reason'], 'idle_timeout')
        self.assertEqual(status['owner'], 'integration-test')
        self.assertEqual(len(self.launches), 1)

    def test_cancellation_stops_new_input_without_touching_latch(self):
        lease = self.start_task()
        marker = self.state / 'cancelled'
        marker.write_text('fixture only')
        marker.chmod(0o600)
        self.wait_for(lambda: (lambda value: value if value['state'] == 'failed' else None)(
            self.exchange({'command': 'status'})))
        response = self.request(lease, 1, ['doctor', 'must-not-run'])
        self.assertEqual(response['error'], 'cancelled')
        self.assertTrue(marker.exists())
        self.assertEqual(self.input_events(), [])
        self.assertEqual(len(self.launches), 1)

    def test_compositor_replacement_stops_task_without_switching_instance(self):
        lease = self.start_task()
        self.current_identity = {'instance': 'replacement', 'wl_socket': 'wayland-other',
                                 'commit': 'fake-commit', 'abi_hash': 'fake-abi'}
        status = self.wait_for(lambda: (lambda value: value if value.get('error') == 'compositor_changed' else None)(
            self.exchange({'command': 'status'})), timeout=4)
        self.assertEqual(status['state'], 'failed')
        response = self.request(lease, 1, ['doctor', 'must-not-run'])
        self.assertFalse(response['ok'])
        self.assertEqual(self.input_events(), [])
        self.assertEqual(len(self.launches), 1)

    def test_lost_guardian_record_stops_task_before_new_input(self):
        lease = self.start_task()
        (self.state / 'session.json').unlink()
        status = self.wait_for(lambda: (lambda value: value if value.get('error') == 'guardian_lost' else None)(
            self.exchange({'command': 'status'})))
        self.assertEqual(status['guardian'], 'failed')
        response = self.request(lease, 1, ['doctor', 'must-not-run'])
        self.assertFalse(response['ok'])
        self.assertEqual(self.input_events(), [])
        self.assertEqual(len(self.launches), 1)


def _process_alive(process):
    return process is not None and process.poll() is None


class CodeExecEnvelopeTests(unittest.TestCase):
    """Pick 1: code-exec is on the broker allowlist; unknown commands are not."""

    def test_code_exec_envelope_validates(self):
        envelope, _, _ = session_remote._validate_envelope(
            {'args': ['code-exec', '--program', '-'], 'stdin': 'x = 1',
             'image_policy': 'always'})
        self.assertEqual(envelope['args'][0], 'code-exec')

    def test_unknown_command_still_rejected(self):
        with self.assertRaises(session_remote.BrokerError):
            session_remote._validate_envelope(
                {'args': ['shell', 'id'], 'stdin': '',
                 'image_policy': 'always'})



class ValidateEnvelopeArgTypeTests(unittest.TestCase):
    """Non-string envelope args get a distinct error, not unsupported_command."""

    def test_integer_arg_returns_invalid_arg_type(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            session_remote._validate_envelope(
                {'args': ['a11y', 'query', '--pid', 1234], 'stdin': '',
                 'image_policy': 'always'})
        self.assertEqual(caught.exception.error, 'invalid_arg_type')
        self.assertIn('1234', str(caught.exception))
        self.assertIn('int', str(caught.exception))

    def test_string_pid_arg_is_accepted(self):
        envelope, _, _ = session_remote._validate_envelope(
            {'args': ['a11y', 'query', '--pid', '1234'], 'stdin': '',
             'image_policy': 'always'})
        self.assertEqual(envelope['args'], ['a11y', 'query', '--pid', '1234'])

    def test_a11y_string_args_are_accepted(self):
        for args in (['a11y', 'query', '--pid', '764773', '--name', 'Home'],
                     ['a11y', 'observe', '--pid', '764773'],
                     ['a11y', 'ground', 'e1', '--snapshot', '/tmp/g1-snapshot.json',
                      '--address', '0xabc']):
            envelope, _, _ = session_remote._validate_envelope(
                {'args': args, 'stdin': '', 'image_policy': 'always'})
            self.assertEqual(envelope['args'], args)

    def test_unknown_string_command_still_unsupported_command(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            session_remote._validate_envelope(
                {'args': ['rm', '-rf', '/'], 'stdin': '', 'image_policy': 'always'})
        self.assertEqual(caught.exception.error, 'unsupported_command')


if __name__ == '__main__':
    unittest.main()

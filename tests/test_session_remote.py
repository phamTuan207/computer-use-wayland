"""Unix-socket broker integration tests using a private fake session-driver."""
import json
import io
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
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import session_remote


FAKE_DRIVER = r'''
import json, os, sys, time
from pathlib import Path

state = Path(os.environ['FAKE_SESSION_STATE'])
events = Path(os.environ['FAKE_DRIVER_EVENTS'])
state.mkdir(mode=0o700, parents=True, exist_ok=True)
token = 'a' * 32

def mark(event, **fields):
    raw = json.dumps({'event': event, **fields}, separators=(',', ':')) + '\n'
    fd = os.open(events, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try: os.write(fd, raw.encode())
    finally: os.close(fd)

snapshot = state / 'session.json'
fd = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as stream:
    json.dump({'version': 4, 'token': token}, stream)
    stream.flush(); os.fsync(stream.fileno())
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
    if args[-1] == 'terminal':
        print(json.dumps({'returncode': 1, 'result': {'ok': False, 'error': 'refused'}}), flush=True)
        break
    if args == ['act', 'transient']:
        print(json.dumps({'returncode': 1, 'result': {'ok': False,
              'error': 'focus changed', 'error_code': 'focus_changed'}}), flush=True)
        continue
    response = {'returncode': 0, 'result': {'ok': True, 'args': args}}
    print(json.dumps(response, separators=(',', ':')), flush=True)

mark('eof')
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

    def test_idle_status_and_private_socket_start(self):
        response = self.exchange({'command': 'status'})
        self.assertEqual(response['state'], 'idle')
        self.assertIsNone(response['owner'])
        info = self.socket_path.lstat()
        self.assertTrue(stat.S_ISSOCK(info.st_mode))
        self.assertEqual(stat.S_IMODE(info.st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.socket_path.parent.stat().st_mode), 0o700)
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

    def test_terminal_driver_error_stops_but_whitelisted_act_refusal_can_continue(self):
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

    def test_whitelisted_transient_act_refusal_keeps_existing_driver_alive(self):
        lease = self.start_task()
        self.request(lease, 1, ['act', 'transient'])
        refusal = self.wait_for(lambda: (lambda value: value if value.get('status') == 'completed' else None)(
            self.result(lease, 1)))
        self.assertEqual(refusal['response']['result']['error_code'], 'focus_changed')
        self.assertEqual(self.request(lease, 2, ['doctor', 'replanned'])['status'], 'accepted')
        self.wait_for(lambda: self.result(lease, 2).get('status') == 'completed')
        self.assertEqual(len(self.launches), 1)
        self.assertEqual(len(self.input_events()), 2)

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


if __name__ == '__main__':
    unittest.main()

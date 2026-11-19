#!/usr/bin/env python3
"""Reconnectable, single-owner Unix-socket broker for session-driver."""
from collections import deque
from dataclasses import dataclass, field
import argparse
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import select
import signal
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time

import cu
import chromium_cli


ROOT = Path(__file__).resolve().parents[1]
CU = ROOT / 'scripts' / 'cu.py'
STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'agent-computer-use'
SNAPSHOT = STATE / 'session.json'
CANCEL = STATE / 'cancelled'
MAX_REQUEST_BYTES = 8 * 1024 * 1024
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
MAX_READY_BYTES = 4096
STDERR_TAIL_BYTES = 16 * 1024
IDLE_TIMEOUT = 300.0
START_TIMEOUT = 25.0
REQUEST_TIMEOUT = 120.0
HYPRLAND_PIN = '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947'
COMMANDS = {'observe', 'act', 'windows', 'doctor', 'status', 'browser', 'a11y', 'code-exec'}
TOKEN = re.compile(r'[0-9a-f]{32}\Z')
SECRET = re.compile(r'[0-9a-f]{64}\Z')


class BrokerError(RuntimeError):
    def __init__(self, error, message=None, *, stage=None, diagnostic=None):
        self.error = error
        self.stage = stage
        self.diagnostic = diagnostic
        super().__init__(message or error)


def _lexists(path):
    try:
        Path(path).lstat()
        return True
    except FileNotFoundError:
        return False
    except OSError as error:
        raise BrokerError('state_unavailable', 'private session state cannot be inspected') from error


def _validate_state_dir(path):
    try:
        info = Path(path).lstat()
    except FileNotFoundError:
        return False
    except OSError as error:
        raise BrokerError('state_unavailable', 'private session state cannot be inspected') from error
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or
            stat.S_IMODE(info.st_mode) != 0o700):
        raise BrokerError('state_unavailable', 'session state directory must be owned and private')
    return True


def _bounded_json_line(raw, limit, label):
    if len(raw) > limit:
        raise BrokerError('too_large', label + ' exceeds its size limit')
    if not raw.endswith(b'\n') or raw.count(b'\n') != 1:
        raise BrokerError('invalid_json', label + ' must be one JSON line')
    try:
        value = json.loads(raw[:-1].decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BrokerError('invalid_json', label + ' is not valid UTF-8 JSON') from error
    return value


def _encode_line(value, limit):
    try:
        raw = (json.dumps(value, ensure_ascii=False, separators=(',', ':'),
                          allow_nan=False) + '\n').encode('utf-8')
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise BrokerError('invalid_response', 'response could not be encoded') from error
    if len(raw) > limit:
        raise BrokerError('response_too_large', 'response exceeds its size limit')
    return raw


def _git_head_at_start():
    try:
        result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                check=True, capture_output=True, text=True, timeout=2)
        head = result.stdout.strip()
        return head if re.fullmatch(r'[0-9a-f]{40,64}', head) else None
    except (OSError, subprocess.SubprocessError):
        return None


def _envsteal_test_proof(fd):
    """Answer a one-use private source assertion sent over an inherited socket."""
    if type(fd) is not int or fd < 3:
        raise RuntimeError('test proof channel is invalid')
    try:
        connection = socket.socket(fileno=os.dup(fd))
    except OSError as error:
        raise RuntimeError('test proof channel is unavailable') from error
    with connection:
        connection.settimeout(2)
        try:
            raw = connection.recv(1025)
            request = json.loads(raw.decode('utf-8'))
        except (OSError,UnicodeError,json.JSONDecodeError) as error:
            raise RuntimeError('test proof request is invalid') from error
        if (len(raw)>1024 or not isinstance(request,dict) or
                request.get('channel')!='envsteal-proof-v1' or
                not isinstance(request.get('expected_cu_sha256'),str) or
                not re.fullmatch(r'[0-9a-f]{64}',request['expected_cu_sha256'])):
            raise RuntimeError('test proof request is invalid')
        cu_path=Path(cu.__file__).resolve()
        remote_path=Path(__file__).resolve()
        expected_cu=ROOT/'scripts'/'cu.py'
        expected_remote=ROOT/'scripts'/'session_remote.py'
        cu_digest=hashlib.sha256(cu_path.read_bytes()).hexdigest()
        if (cu_path!=expected_cu or remote_path!=expected_remote or
                cu_digest!=request['expected_cu_sha256']):
            raise RuntimeError('test broker source assertion failed')
        proof={'ok':True,'cu_path':str(cu_path),'cu_sha256':cu_digest,
               'session_remote_path':str(remote_path)}
        connection.sendall(_encode_line(proof,2048))


def _safe_read_file(path, limit):
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise BrokerError('file_unavailable', 'could not read the requested file') from error
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            raise BrokerError('unsafe_file', 'requested file must be a regular file owned by this user')
        if info.st_mode & 0o077:
            raise BrokerError('unsafe_file', 'requested file must be private')
        if info.st_size > limit:
            raise BrokerError('too_large', 'requested file exceeds its size limit')
        data = bytearray()
        while len(data) <= limit:
            chunk = os.read(fd, min(65536, limit + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > limit:
            raise BrokerError('too_large', 'requested file exceeds its size limit')
        return bytes(data)
    finally:
        os.close(fd)


def _read_snapshot(path):
    """Return a validated session token, None when absent, or raise on recovery data."""
    if not _validate_state_dir(path.parent):
        return None
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
        raise BrokerError('recovery_required', 'retained session state needs manual recovery')
    try:
        raw = _safe_read_file(path, 65536)
        value = json.loads(raw)
    except (BrokerError, OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise BrokerError('recovery_required', 'retained session state needs manual recovery') from error
    if (not isinstance(value, dict) or value.get('version') not in (2, 3, 4) or
            not isinstance(value.get('token'), str) or not TOKEN.fullmatch(value['token'])):
        raise BrokerError('recovery_required', 'retained session state needs manual recovery')
    return value['token']


def _cancelled(path):
    # A dangling symlink is still treated as a closed cancellation gate.
    if not _validate_state_dir(path.parent):
        return False
    return _lexists(path)


def _hypr_json(env, *args, limit=65536):
    try:
        done = subprocess.run(['hyprctl', *args], env=env, capture_output=True,
                              timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        raise BrokerError('native_unavailable', 'read-only compositor check failed') from error
    if done.returncode != 0 or len(done.stdout) > limit:
        raise BrokerError('native_unavailable', 'read-only compositor check failed')
    try:
        return json.loads(done.stdout)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise BrokerError('native_unavailable', 'read-only compositor response was invalid') from error


def _compositor_identity(env):
    signature = env.get('HYPRLAND_INSTANCE_SIGNATURE', '')
    display = env.get('WAYLAND_DISPLAY', '')
    runtime = env.get('XDG_RUNTIME_DIR', '')
    bus = env.get('DBUS_SESSION_BUS_ADDRESS', '')
    if (not signature or not display or not os.path.isabs(runtime) or
            not bus.startswith('unix:path=') or
            any(not isinstance(value, str) or not value or
                any(ch.isspace() or ch in "\"'\\$`" for ch in value)
                for value in (signature, display, runtime, bus))):
        raise BrokerError('native_unavailable', 'explicit compositor environment is incomplete')
    runtime_info = Path(runtime).lstat()
    if (not stat.S_ISDIR(runtime_info.st_mode) or runtime_info.st_uid != os.geteuid() or
            stat.S_IMODE(runtime_info.st_mode) != 0o700):
        raise BrokerError('native_unavailable', 'runtime directory is not private')
    bus_path = bus[len('unix:path='):].split(',', 1)[0]
    if not os.path.isabs(bus_path):
        raise BrokerError('native_unavailable', 'session bus path must be absolute')
    try:
        bus_info = Path(bus_path).lstat()
    except OSError as error:
        raise BrokerError('native_unavailable', 'session bus is unavailable') from error
    if not stat.S_ISSOCK(bus_info.st_mode) or bus_info.st_uid != os.geteuid():
        raise BrokerError('native_unavailable', 'session bus is unavailable')
    rows = _hypr_json(env, '-j', 'instances')
    if not isinstance(rows, list):
        raise BrokerError('native_unavailable', 'compositor instance list is invalid')
    matches = [row for row in rows if isinstance(row, dict) and
               row.get('instance') == signature and row.get('wl_socket') == display]
    if len(matches) != 1:
        raise BrokerError('compositor_changed', 'configured compositor instance is unavailable')
    return {'instance': signature, 'wl_socket': display}


def native_readiness(env=None):
    """Read-only native/task readiness gate with bounded stage diagnostics."""
    if env is None:
        try:
            env = cu.environment(refresh=True)
        except Exception as error:
            raise BrokerError('native_unavailable', 'GUI environment is unavailable',
                              stage='compositor',
                              diagnostic='gui_environment_unavailable') from error
    else:
        env = dict(env)
        try:
            cu._validate_session_tuple(env)
        except Exception as error:
            raise BrokerError('native_unavailable', 'GUI environment is unavailable',
                              stage='compositor',
                              diagnostic='gui_environment_unavailable') from error
    try:
        identity = _compositor_identity(env)
    except BrokerError as error:
        raise BrokerError(error.error, str(error), stage='compositor',
                          diagnostic='gui_environment_unavailable') from error
    except Exception as error:
        raise BrokerError('native_unavailable', 'GUI environment is unavailable',
                          stage='compositor',
                          diagnostic='gui_environment_unavailable') from error
    try:
        version = _hypr_json(env, '-j', 'version')
    except BrokerError as error:
        raise BrokerError(error.error, str(error), stage='abi',
                          diagnostic='version_probe_failed') from error
    if (not isinstance(version, dict) or version.get('version') != '0.57.2' or
            version.get('commit') != HYPRLAND_PIN or
            not isinstance(version.get('abiHash'), str) or
            not version['abiHash'].startswith(HYPRLAND_PIN + '_')):
        raise BrokerError('native_unavailable', 'running compositor ABI is not the accepted build',
                          stage='abi', diagnostic='unsupported_compositor_abi')

    import indicator
    import plugin_inventory
    try:
        plugins = plugin_inventory.parse(_hypr_json(env, '-j', 'plugin', 'list'))
    except Exception as error:
        raise BrokerError('native_unavailable', 'plugin inventory is unavailable or invalid',
                          stage='plugins', diagnostic='plugin_inventory_invalid') from error
    by_name = {entry['name']: entry for entry in plugins}
    if set(by_name) - {'hyprglass', 'computer-use-cursor', 'hyprbars'}:
        raise BrokerError('native_unavailable', 'plugin inventory is unsupported',
                          stage='plugins', diagnostic='unsupported_plugin_inventory')
    glass = by_name.get('hyprglass')
    if glass is None:
        raise BrokerError('native_unavailable', 'accepted glass plugin is missing',
                          stage='glass', diagnostic='glass_plugin_missing')
    if glass['author'] != 'Hyprnux' or glass['version'] != indicator.LIQUID_VERSION:
        raise BrokerError('native_unavailable', 'accepted glass plugin identity is unsupported',
                          stage='glass', diagnostic='glass_plugin_identity_mismatch')
    guard = by_name.get('computer-use-cursor')
    if guard is None:
        raise BrokerError('native_unavailable', 'cursor guard plugin is missing',
                          stage='guard', diagnostic='cursor_guard_missing')
    if guard['author'] != 'computer-use-wayland' or guard['version'] != '1.0.0':
        raise BrokerError('native_unavailable', 'cursor guard plugin identity is unsupported',
                          stage='guard', diagnostic='cursor_guard_identity_mismatch')
    if 'hyprbars' in by_name and not (
            by_name['hyprbars']['author'] == 'Vaxry' and by_name['hyprbars']['version'] == '1.0'):
        raise BrokerError('native_unavailable', 'plugin inventory is unsupported',
                          stage='plugins', diagnostic='unsupported_hyprbars_build')
    try:
        liquid_ready = indicator.liquid_available(env, ready=True)
    except Exception as error:
        raise BrokerError('native_unavailable', 'liquid-glass status probe failed',
                          stage='glass', diagnostic='liquid_status_probe_failed') from error
    if not liquid_ready:
        raise BrokerError('native_unavailable', 'accepted liquid-glass backend is not ready',
                          stage='glass', diagnostic='liquid_backend_not_ready')
    import cursor_theme
    try:
        cursor_theme.check_guard(env)
    except Exception as error:
        raise BrokerError('native_unavailable', 'cursor backend is not idle and ready',
                          stage='guard', diagnostic='cursor_guard_busy_or_unavailable') from error
    return {**identity, 'commit': version['commit'], 'abi_hash': version['abiHash']}


def same_compositor(env, expected):
    """Read-only identity check used while a task owns the desktop."""
    try:
        current = _compositor_identity(env)
    except BrokerError:
        return False
    return current == {'instance': expected.get('instance'),
                       'wl_socket': expected.get('wl_socket')}


def _default_socket(env=None):
    env = os.environ if env is None else env
    runtime = env.get('XDG_RUNTIME_DIR') or f'/run/user/{os.getuid()}'
    if not os.path.isabs(runtime):
        raise BrokerError('invalid_socket_path', 'XDG_RUNTIME_DIR must be absolute')
    return Path(runtime) / 'computer-use-wayland' / 'relay.sock'


def _validate_envelope(value):
    if not isinstance(value, dict) or set(value) - {'args', 'stdin', 'image_policy'}:
        raise BrokerError('invalid_request', 'driver request must use the existing session-driver envelope')
    args = value.get('args')
    data = value.get('stdin', '')
    policy = value.get('image_policy', 'always')
    if not isinstance(args, list) or not args:
        raise BrokerError('unsupported_command', 'driver command is not on the session-driver allowlist')
    for index, arg in enumerate(args):
        if not isinstance(arg, str):
            detail = repr(arg)
            if len(detail) > 80:
                detail = detail[:77] + '...'
            raise BrokerError(
                'invalid_arg_type',
                f'driver arg {index} must be a string, got {type(arg).__name__}: {detail}')
    if args[0] not in COMMANDS | {'finish'}:
        raise BrokerError('unsupported_command', 'driver command is not on the session-driver allowlist')
    if not isinstance(data, str) or policy not in ('auto', 'always'):
        raise BrokerError('invalid_request', 'driver stdin or image policy is invalid')
    envelope = {'args': args, 'stdin': data, 'image_policy': policy}
    raw = _encode_line(envelope, MAX_REQUEST_BYTES)
    digest = hashlib.sha256(raw).hexdigest()
    return envelope, raw, digest


class LineReader:
    """Read one bounded line without buffering an oversized child response."""
    def __init__(self, stream):
        self.stream = stream
        self.buffer = bytearray()

    def readline(self, limit, timeout):
        deadline = time.monotonic() + timeout
        oversized = False
        while True:
            newline = self.buffer.find(b'\n')
            if newline >= 0:
                line = bytes(self.buffer[:newline + 1])
                del self.buffer[:newline + 1]
                if oversized or len(line) > limit:
                    raise BrokerError('response_too_large', 'driver response exceeds its size limit')
                return line
            if len(self.buffer) > limit:
                oversized = True
                self.buffer.clear()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise BrokerError('driver_timeout', 'driver response timed out; outcome is unknown')
            ready, _, _ = select.select([self.stream], [], [], min(remaining, 0.1))
            if not ready:
                continue
            chunk = os.read(self.stream.fileno(), 65536)
            if not chunk:
                if oversized or len(self.buffer) > limit:
                    raise BrokerError('response_too_large', 'driver response exceeds its size limit')
                if self.buffer:
                    raise BrokerError('partial_response', 'driver closed with a partial JSON response')
                raise BrokerError('driver_eof', 'driver closed before returning a result')
            if oversized:
                if b'\n' in chunk:
                    before, after = chunk.split(b'\n', 1)
                    if after:
                        self.buffer.extend(after)
                    raise BrokerError('response_too_large', 'driver response exceeds its size limit')
                continue
            self.buffer.extend(chunk)
            if len(self.buffer) > limit and b'\n' not in self.buffer:
                oversized = True
                self.buffer.clear()


@dataclass
class RequestRecord:
    sequence: int
    digest: str
    command: str
    status: str = 'running'
    response: object = None
    error: str = ''
    done: object = field(default_factory=threading.Event, repr=False)


@dataclass
class Task:
    owner: str
    start_id: str
    secret: str
    generation: str
    identity: dict
    process: object = None
    reader: object = None
    state: str = 'starting'
    driver: str = 'starting'
    guardian: str = 'unknown'
    session_token: str = ''
    created: float = field(default_factory=time.monotonic)
    last_activity: float = field(default_factory=time.monotonic)
    next_sequence: int = 1
    active: RequestRecord = None
    previous: RequestRecord = None
    worker: threading.Thread = None
    finish_requested: bool = False
    input_closed: bool = False
    stop_reason: str = ''
    error: str = ''
    next_probe: float = 0.0
    stderr_thread: threading.Thread = None
    ready_thread: threading.Thread = None
    streams_closed: bool = False
    prefetches_cleared: bool = False


class Broker:
    """One idle broker process; dependencies are injectable for offline integration tests."""
    def __init__(self, *, state_dir=STATE, env=None, launcher=None,
                 readiness=None, compositor_check=None, cancelled=None,
                 idle_timeout=IDLE_TIMEOUT, start_timeout=START_TIMEOUT,
                 request_timeout=REQUEST_TIMEOUT, max_request_bytes=MAX_REQUEST_BYTES,
                 max_response_bytes=MAX_RESPONSE_BYTES):
        self.state_dir = Path(state_dir)
        self.snapshot_path = self.state_dir / 'session.json'
        self.cancel_path = self.state_dir / 'cancelled'
        self.base_env = dict(os.environ if env is None else env)
        self.env = dict(self.base_env)
        self.automatic_environment = env is None
        self.launcher = launcher or self._launch
        self.readiness = readiness or self._prepare_environment
        self.compositor_check = compositor_check or (
            lambda expected: same_compositor(self.env, expected))
        self.cancelled = cancelled or (lambda: _cancelled(self.cancel_path))
        self.idle_timeout = idle_timeout
        self.start_timeout = start_timeout
        self.request_timeout = request_timeout
        self.max_request_bytes = max_request_bytes
        self.max_response_bytes = max_response_bytes
        self.broker_generation = secrets.token_hex(16)
        try:
            self.loaded_code_sha256 = hashlib.sha256(
                Path(__file__).resolve().read_bytes()).hexdigest()
        except OSError:
            self.loaded_code_sha256 = None
        self.started_git_head = _git_head_at_start()
        self.lock = threading.RLock()
        self.task = None
        self.last_start = None
        self.start_order = deque()
        self.start_history = {}
        self.last_status_error = None
        self.reported_failures = set()
        self.shutting_down = False
        self.stderr_tail = deque()

    def report_failure(self, command, error):
        if command not in ('start', 'status'):
            return
        code = (error if isinstance(error, str) and
                re.fullmatch(r'[a-z][a-z0-9_]{0,63}', error) else 'request_failed')
        with self.lock:
            if command == 'status':
                self.last_status_error = code
            key = (command, code)
            log_failure = key not in self.reported_failures
            self.reported_failures.add(key)
        if log_failure:
            print('session_remote: ' + command + ' failed: ' + code,
                  file=sys.stderr, flush=True)

    @staticmethod
    def _launch(env):
        python = '/usr/bin/python3'
        argv = [python, str(CU), 'session', '--', python, str(CU), 'session-driver']
        return subprocess.Popen(argv, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, bufsize=0, close_fds=True)

    def _prepare_environment(self):
        attempts = 2 if self.automatic_environment else 1
        for attempt in range(attempts):
            try:
                candidate = cu.environment(self.base_env,
                                           refresh=self.automatic_environment)
            except Exception as error:
                raise BrokerError('native_unavailable', 'GUI environment is unavailable',
                                  stage='compositor',
                                  diagnostic='gui_environment_unavailable') from error
            try:
                identity = native_readiness(candidate)
            except BrokerError as error:
                if (attempt + 1 < attempts and error.stage == 'compositor'):
                    continue
                if error.stage == 'compositor':
                    raise BrokerError(error.error, 'GUI environment is unavailable',
                                      stage='compositor',
                                      diagnostic='gui_environment_unavailable') from error
                raise
            self.env = candidate
            return identity
        raise BrokerError('native_unavailable', 'GUI environment is unavailable',
                          stage='compositor', diagnostic='gui_environment_unavailable')

    def _read_session(self):
        try:
            return _read_snapshot(self.snapshot_path)
        except BrokerError:
            return 'invalid'

    def _drain_stderr(self, task):
        stream = task.process.stderr
        try:
            while True:
                chunk = os.read(stream.fileno(), 4096)
                if not chunk:
                    return
                with self.lock:
                    self.stderr_tail.append(chunk)
                    size = sum(map(len, self.stderr_tail))
                    while self.stderr_tail and size > STDERR_TAIL_BYTES:
                        removed = self.stderr_tail.popleft()
                        size -= len(removed)
        except (OSError, ValueError):
            return

    @staticmethod
    def _validate_start(value):
        if not isinstance(value, dict) or value.get('command') != 'start':
            raise BrokerError('invalid_request', 'invalid start request')
        owner = value.get('owner')
        start_id = value.get('start_id')
        secret = value.get('lease_secret')
        broker_generation = value.get('broker_generation')
        if (not isinstance(owner, str) or not re.fullmatch(r'[A-Za-z0-9_.:@+-]{1,80}', owner) or
                not isinstance(start_id, str) or not TOKEN.fullmatch(start_id) or
                not isinstance(secret, str) or not SECRET.fullmatch(secret) or
                not isinstance(broker_generation, str) or not TOKEN.fullmatch(broker_generation)):
            raise BrokerError('invalid_request', 'start identity or owner is invalid')
        return owner, start_id, secret, broker_generation

    def _start(self, value):
        owner, start_id, secret, broker_generation = self._validate_start(value)
        with self.lock:
            if broker_generation != self.broker_generation:
                raise BrokerError('broker_changed', 'broker restarted; the prior start outcome is unknown')
            prior = self.start_history.get(start_id)
            if prior is not None:
                if secret != prior['secret'] or owner != prior['owner']:
                    raise BrokerError('conflict', 'start identifier conflicts with its saved outcome')
                return dict(prior['response'])
            if self.last_start and start_id < self.last_start['start_id']:
                raise BrokerError('expired', 'start identifier is older than the retained outcome')

            record = {'start_id': start_id, 'secret': secret, 'owner': owner,
                      'response': {'ok': False, 'error': 'starting'}}
            self.last_start = record
            self.start_order.append(start_id)
            self.start_history[start_id] = record
            while len(self.start_order) > 64:
                expired = self.start_order.popleft()
                self.start_history.pop(expired, None)
            if self.shutting_down:
                response = {'ok': False, 'error': 'broker_stopping'}
                record['response'] = response
                return dict(response)
            try:
                is_cancelled = self.cancelled()
            except Exception:
                response = {'ok': False, 'error': 'cancellation_unavailable'}
                record['response'] = response
                return dict(response)
            if is_cancelled:
                response = {'ok': False, 'error': 'cancelled'}
                record['response'] = response
                return dict(response)
            if self.env.get('CU_SESSION_TOKEN'):
                response = {'ok': False, 'error': 'nested_session'}
                record['response'] = response
                return dict(response)
            if self.task is not None:
                if (self.task.process is not None and self.task.process.poll() is None or
                        self.task.state not in ('finished', 'failed')):
                    response = {'ok': False, 'error': 'busy'}
                    record['response'] = response
                    return dict(response)
                if self._task_recovery_required(self.task):
                    response = {'ok': False, 'error': 'recovery_required'}
                    record['response'] = response
                    return dict(response)
            try:
                retained = _read_snapshot(self.snapshot_path)
            except BrokerError:
                response = {'ok': False, 'error': 'recovery_required'}
                record['response'] = response
                return dict(response)
            if retained is not None:
                response = {'ok': False, 'error': 'recovery_required'}
                record['response'] = response
                return dict(response)
            try:
                identity = self.readiness()
                if not isinstance(identity, dict) or not identity.get('instance'):
                    raise BrokerError('native_unavailable', 'native readiness check failed',
                                      stage='readiness', diagnostic='invalid_readiness_result')
            except BrokerError as error:
                response = {'ok': False, 'error': error.error}
                if error.stage:
                    response['stage'] = error.stage[:32]
                if error.diagnostic:
                    response['diagnostic'] = error.diagnostic[:96]
                record['response'] = response
                return dict(response)
            except Exception:
                response = {'ok': False, 'error': 'native_unavailable',
                            'stage': 'readiness',
                            'diagnostic': 'unexpected_readiness_failure'}
                record['response'] = response
                return dict(response)

            task = Task(owner, start_id, secret, secrets.token_hex(16), identity)
            self.task = task
            try:
                task.process = self.launcher(self.env)
                task.reader = LineReader(task.process.stdout)
                task.stderr_thread = threading.Thread(target=self._drain_stderr, args=(task,),
                                                      name='cu-relay-stderr', daemon=True)
                task.stderr_thread.start()
                task.ready_thread = threading.Thread(target=self._await_ready, args=(task,),
                                                     name='cu-relay-ready', daemon=True)
                task.ready_thread.start()
            except Exception:
                task.state = 'failed'
                task.driver = 'failed'
                task.error = 'driver_start_failed'
                task.finish_requested = True
                self._close_input(task)
                response = {'ok': True, 'status': 'failed', 'generation': task.generation,
                            'owner': owner, 'error': task.error}
                record['response'] = response
                return dict(response)
            response = {'ok': True, 'status': 'starting', 'generation': task.generation,
                        'owner': owner}
            record['response'] = response
            return dict(response)

    def _await_ready(self, task):
        try:
            line = task.reader.readline(MAX_READY_BYTES, self.start_timeout)
            ready = _bounded_json_line(line, MAX_READY_BYTES, 'driver readiness line')
            if ready != {'ok': True, 'driver': 'ready'}:
                raise BrokerError('driver_not_ready', 'session-driver readiness response was invalid')
            token = _read_snapshot(self.snapshot_path)
            if token is None:
                raise BrokerError('guardian_missing', 'session guardian did not retain its session record')
            with self.lock:
                if task.finish_requested or task.process.poll() is not None:
                    raise BrokerError('driver_not_ready', 'driver stopped during startup')
                task.session_token = token
                task.guardian = 'active'
                task.driver = 'ready'
                task.state = 'running'
                task.last_activity = time.monotonic()
                task.next_probe = time.monotonic() + 1.0
        except Exception as error:
            with self.lock:
                if task.state not in ('failed', 'finished'):
                    task.state = 'failed'
                    task.driver = 'failed'
                    task.error = error.error if isinstance(error, BrokerError) else 'driver_start_failed'
                    task.stop_reason = task.error
                    task.finish_requested = True

    def _request_worker(self, task, record, raw):
        try:
            with self.lock:
                if task.finish_requested or self.cancelled():
                    raise BrokerError('cancelled', 'task stopped before the request was dispatched')
                if task.process.poll() is not None or task.driver != 'ready':
                    raise BrokerError('driver_failed', 'session-driver is no longer ready')
                task.process.stdin.write(raw)
                task.process.stdin.flush()
            line = task.reader.readline(self.max_response_bytes, self.request_timeout)
            response = _bounded_json_line(line, self.max_response_bytes, 'driver response')
            if response == {'ok': True, 'driver': 'finished'}:
                with self.lock:
                    record.response = response
                    record.status = 'completed'
                    if task.active is record:
                        task.previous = record
                        task.active = None
                        task.next_sequence = record.sequence + 1
                    task.finish_requested = True
                    task.stop_reason = 'explicit_finish'
                    task.state = 'cleaning'
                    task.last_activity = time.monotonic()
                return
            if (not isinstance(response, dict) or type(response.get('returncode')) is not int or
                    type(response.get('session_continues')) is not bool):
                raise BrokerError('invalid_driver_response', 'driver returned an invalid response')
            # The driver owns continuation; result payload flags are never authority.
            terminal = response['session_continues'] is not True
            with self.lock:
                record.response = response
                record.status = 'failed' if terminal else 'completed'
                if task.active is record:
                    task.previous = record
                    task.active = None
                    task.next_sequence = record.sequence + 1
                task.last_activity = time.monotonic()
                if terminal:
                    task.state = 'failed'
                    task.driver = 'failed'
                    task.error = 'driver_command_failed'
                    task.stop_reason = 'driver_command_failed'
                    task.finish_requested = True
        except Exception as error:
            with self.lock:
                record.status = 'unknown'
                record.error = error.error if isinstance(error, BrokerError) else 'driver_failed'
                if task.active is record:
                    task.previous = record
                    task.active = None
                task.state = 'failed'
                task.driver = 'failed'
                task.error = record.error
                task.stop_reason = record.error
                task.finish_requested = True
                task.last_activity = time.monotonic()
        finally:
            record.done.set()

    def _authorize(self, value):
        task = self.task
        if task is None:
            raise BrokerError('no_task', 'no task lease is active')
        if (not isinstance(value, dict) or value.get('generation') != task.generation or
                value.get('lease_secret') != task.secret):
            raise BrokerError('invalid_lease', 'task lease is invalid or expired')
        if value.get('owner') != task.owner:
            raise BrokerError('invalid_lease', 'task lease owner does not match')
        return task

    def _request(self, value):
        if not isinstance(value, dict):
            raise BrokerError('invalid_request', 'invalid request')
        sequence = value.get('sequence')
        if type(sequence) is not int or sequence < 1:
            raise BrokerError('invalid_sequence', 'sequence must be a positive integer')
        envelope, raw, digest = _validate_envelope(value.get('request'))
        with self.lock:
            task = self._authorize(value)
            current = task.active or task.previous
            if current is not None and sequence == current.sequence:
                if digest != current.digest:
                    raise BrokerError('conflict', 'sequence was already used for a different request')
                task.last_activity = time.monotonic()
                return self._record_response(current)
            if sequence < task.next_sequence:
                raise BrokerError('expired', 'request result has expired and will not be replayed')
            try:
                is_cancelled = self.cancelled()
            except Exception as error:
                self._fail_task(task, 'cancellation_unavailable')
                raise BrokerError('cancellation_unavailable',
                                  'cancellation state cannot be inspected; task stopped') from error
            if is_cancelled:
                self._fail_task(task, 'cancelled')
                raise BrokerError('cancelled', 'cancellation is latched; no new input is accepted')
            if task.finish_requested or task.state != 'running' or task.driver != 'ready':
                raise BrokerError('task_stopped', 'task is not accepting requests')
            if not self.compositor_check(task.identity):
                self._fail_task(task, 'compositor_changed')
                raise BrokerError('compositor_changed', 'compositor identity changed; task stopped')
            if sequence > task.next_sequence:
                raise BrokerError('sequence_gap', 'request sequence is not the next expected value')
            if task.active is not None:
                raise BrokerError('busy', 'one request is already running')
            if task.process.poll() is not None:
                self._fail_task(task, 'driver_failed')
                raise BrokerError('driver_failed', 'session-driver exited; outcome is not replayed')
            record = RequestRecord(sequence, digest, envelope['args'][0])
            task.previous = None  # advancing acknowledges the prior completed result
            task.active = record
            task.last_activity = time.monotonic()
            task.worker = threading.Thread(target=self._request_worker,
                                           args=(task, record, raw),
                                           name='cu-relay-request', daemon=True)
            task.worker.start()
            return {'ok': True, 'status': 'accepted', 'sequence': sequence}

    @staticmethod
    def _record_response(record):
        body = {'ok': True, 'status': record.status, 'sequence': record.sequence}
        if record.response is not None:
            body['response'] = record.response
        if record.error:
            body['error'] = record.error
        return body

    def _result(self, value):
        sequence = value.get('sequence') if isinstance(value, dict) else None
        if type(sequence) is not int or sequence < 1:
            raise BrokerError('invalid_sequence', 'sequence must be a positive integer')
        with self.lock:
            task = self._authorize(value)
            record = task.active or task.previous
            if record is None or sequence < task.next_sequence - (1 if task.previous else 0):
                raise BrokerError('expired', 'request result has expired')
            if record.sequence != sequence:
                if sequence < record.sequence:
                    raise BrokerError('expired', 'request result has expired')
                raise BrokerError('not_found', 'request sequence is not known')
            task.last_activity = time.monotonic()
            wait_for = record.status == 'running'
        if wait_for:
            record.done.wait(self.request_timeout)
        with self.lock:
            task = self._authorize(value)
            current = task.active or task.previous
            if current is not record:
                raise BrokerError('expired', 'request result has expired')
            return self._record_response(record)

    def _status(self, value):
        with self.lock:
            task = self.task
            if value.get('lease_file'):
                task = self._authorize(value)
                task.last_activity = time.monotonic()
            last_start_error = None
            if self.last_start is not None:
                response = self.last_start.get('response') or {}
                last_start_error = response.get('error')
                if (response.get('ok') is True and task is not None and
                        task.start_id == self.last_start.get('start_id')):
                    last_start_error = task.error or None
            try:
                cancelled = bool(self.cancelled())
                cancellation_state = 'latched' if cancelled else 'clear'
            except Exception:
                cancelled = True
                cancellation_state = 'unknown'
            body = {'ok': True, 'broker': 'running',
                    'broker_generation': self.broker_generation,
                    'loaded_code_sha256': self.loaded_code_sha256,
                    'started_git_head': self.started_git_head,
                    'state': 'idle' if task is None else task.state,
                    'owner': None if task is None else task.owner,
                    'generation': None if task is None else task.generation,
                    'driver': 'idle' if task is None else task.driver,
                    'guardian': 'idle' if task is None else task.guardian,
                    'cancelled': cancelled,
                    'cancellation_state': cancellation_state,
                    'recovery': 'required' if _lexists(self.snapshot_path) and
                    (task is None or task.process is None or task.process.poll() is not None or
                     task.guardian in ('failed', 'recovery_required'))
                    else ('active' if task is not None and task.guardian == 'active' else 'none'),
                    'next_sequence': 1 if task is None else task.next_sequence,
                    'active_sequence': None if task is None or task.active is None
                    else task.active.sequence,
                    'last_start_error': last_start_error,
                    'last_status_error': self.last_status_error}
            if task is not None:
                body['error'] = task.error or None
                body['stop_reason'] = task.stop_reason or None
            return body

    def _finish(self, value):
        with self.lock:
            task = self._authorize(value)
            if task.state not in ('finished', 'failed'):
                task.finish_requested = True
                if not task.stop_reason:
                    task.stop_reason = 'explicit_finish'
                task.state = 'cleaning'
                task.last_activity = time.monotonic()
            return {'ok': True, 'status': task.state, 'generation': task.generation}

    def _fail_task(self, task, reason):
        task.state = 'failed'
        task.driver = 'failed'
        task.error = reason
        task.stop_reason = reason
        task.finish_requested = True

    def _task_recovery_required(self, task):
        if task.process is not None and task.process.poll() is None:
            return False
        try:
            return _read_snapshot(self.snapshot_path) is not None
        except BrokerError:
            return True

    def handle(self, value):
        if not isinstance(value, dict):
            raise BrokerError('invalid_request', 'request must be a JSON object')
        command = value.get('command')
        if command == 'status':
            return self._status(value)
        if command == 'start':
            return self._start(value)
        if command == 'request':
            return self._request(value)
        if command == 'result':
            return self._result(value)
        if command == 'finish':
            return self._finish(value)
        raise BrokerError('unsupported_command', 'unsupported broker command')

    def _close_input(self, task):
        if task.input_closed or task.process is None:
            return
        task.input_closed = True
        try:
            task.process.stdin.close()
        except (BrokenPipeError, OSError, ValueError):
            pass

    @staticmethod
    def _close_streams(task):
        if task.streams_closed:
            return
        if ((task.ready_thread is not None and task.ready_thread.is_alive()) or
                (task.worker is not None and task.worker.is_alive())):
            return
        if task.stderr_thread is not None:
            task.stderr_thread.join(timeout=0.1)
        for stream in (task.process.stdin, task.process.stdout, task.process.stderr):
            try:
                stream.close()
            except (OSError, ValueError):
                pass
        task.streams_closed = True

    def begin_shutdown(self):
        with self.lock:
            self.shutting_down = True
            task = self.task
            if task is not None and task.state not in ('finished', 'failed'):
                task.finish_requested = True
                task.stop_reason = task.stop_reason or 'service_stop'
                task.state = 'cleaning'

    def tick(self):
        with self.lock:
            task = self.task
            if task is None or task.state in ('finished', 'failed') and task.process is None:
                return
            now = time.monotonic()
            if task.process is not None and task.process.poll() is not None:
                if task.session_token and not task.prefetches_cleared:
                    try:
                        chromium_cli.clear_session_prefetches(task.session_token)
                    except Exception:
                        pass
                    else:
                        task.prefetches_cleared = True
                if task.active is not None:
                    task.active.status = 'unknown'
                    task.active.error = 'driver_eof'
                    task.previous = task.active
                    task.active.done.set()
                    task.active = None
                    task.state = 'failed'
                    task.driver = 'failed'
                    task.error = 'driver_eof'
                    task.stop_reason = 'driver_eof'
                exit_code = task.process.returncode
                token = self._read_session()
                if token is None:
                    task.guardian = 'clean'
                else:
                    task.guardian = 'recovery_required'
                if task.state not in ('failed',) and not task.finish_requested:
                    task.state = 'failed'
                    task.driver = 'failed'
                    task.error = 'driver_exited'
                    task.stop_reason = 'driver_exited'
                elif task.finish_requested and task.stop_reason in ('explicit_finish', 'service_stop',
                                                                      'idle_timeout') and exit_code == 0 and token is None:
                    task.state = 'finished'
                    task.driver = 'stopped'
                elif task.state != 'failed':
                    task.state = 'failed'
                    task.driver = 'failed'
                    task.error = task.error or 'cleanup_failed'
                self._close_streams(task)
                return

            if task.finish_requested:
                if task.active is None:
                    self._close_input(task)
                return
            if task.state == 'starting' and now - task.created > self.start_timeout:
                self._fail_task(task, 'driver_start_timeout')
                self._close_input(task)
                return
            try:
                is_cancelled = self.cancelled()
            except Exception:
                self._fail_task(task, 'cancellation_unavailable')
                if task.active is None:
                    self._close_input(task)
                return
            if is_cancelled:
                self._fail_task(task, 'cancelled')
                if task.active is None:
                    self._close_input(task)
                return
            if task.state == 'running':
                try:
                    current_token = _read_snapshot(self.snapshot_path)
                except BrokerError:
                    current_token = 'invalid'
                if current_token != task.session_token:
                    task.guardian = 'failed'
                    self._fail_task(task, 'guardian_lost')
                    if task.active is None:
                        self._close_input(task)
                    return
            if task.state == 'running' and task.active is None and now - task.last_activity >= self.idle_timeout:
                task.finish_requested = True
                task.stop_reason = 'idle_timeout'
                task.state = 'cleaning'
                self._close_input(task)
                return
            if now >= task.next_probe:
                task.next_probe = now + 1.0
                try:
                    same = self.compositor_check(task.identity)
                except Exception:
                    same = False
                if not same:
                    self._fail_task(task, 'compositor_changed')
                    if task.active is None:
                        self._close_input(task)
                    return

    def cleanup_complete(self):
        with self.lock:
            task = self.task
            if task is None or task.process is None:
                return True
            return (task.process.poll() is not None and
                    (task.ready_thread is None or not task.ready_thread.is_alive()) and
                    (task.worker is None or not task.worker.is_alive()))

    def status_for_tests(self):
        return self._status({'command': 'status'})


class UnixSocketServer:
    def __init__(self, broker, path, *, max_request_bytes=None,
                 max_response_bytes=None, accept_timeout=0.2):
        self.broker = broker
        self.path = Path(path)
        self.lock_path = self.path.with_name('relay.lock')
        self.max_request_bytes = max_request_bytes or broker.max_request_bytes
        self.max_response_bytes = max_response_bytes or broker.max_response_bytes
        self.accept_timeout = accept_timeout
        self.listener = None
        self.lock_file = None
        self.socket_identity = None
        self.stop_event = threading.Event()
        self.client_threads = set()
        self.client_threads_lock = threading.Lock()

    def _directory(self):
        if not self.path.is_absolute():
            raise BrokerError('invalid_socket_path', 'socket path must be absolute')
        if len(os.fsencode(self.path)) >= 104:
            raise BrokerError('invalid_socket_path', 'Unix socket path is too long')
        try:
            info = self.path.parent.lstat()
        except FileNotFoundError:
            try:
                os.mkdir(self.path.parent, 0o700)
            except FileExistsError:
                pass
            info = self.path.parent.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or
                stat.S_IMODE(info.st_mode) != 0o700):
            raise BrokerError('unsafe_socket_directory', 'socket directory must be an owned 0700 directory')

    def bind(self):
        if not hasattr(socket, 'SO_PEERCRED'):
            raise BrokerError('unsupported_platform', 'same-user peer checks require Linux SO_PEERCRED')
        self._directory()
        flags = os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
        try:
            fd = os.open(self.lock_path, flags, 0o600)
        except OSError as error:
            raise BrokerError('broker_lock_failed', 'broker lock is unsafe or unavailable') from error
        self.lock_file = os.fdopen(fd, 'r+b', buffering=0)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            self.lock_file.close()
            self.lock_file = None
            raise BrokerError('broker_lock_failed', 'broker lock must be a regular owned file')
        os.fchmod(fd, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self.lock_file.close()
            self.lock_file = None
            raise BrokerError('broker_running', 'another broker owns this socket') from error

        try:
            try:
                existing = self.path.lstat()
            except FileNotFoundError:
                existing = None
            if existing is not None:
                if not stat.S_ISSOCK(existing.st_mode) or existing.st_uid != os.geteuid():
                    raise BrokerError('unsafe_socket', 'existing socket path is not an owned socket')
                probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                probe.settimeout(0.2)
                try:
                    probe.connect(str(self.path))
                except OSError as error:
                    if error.errno not in (errno.ECONNREFUSED, errno.ENOENT):
                        raise BrokerError('socket_probe_failed', 'could not confirm stale socket') from error
                else:
                    raise BrokerError('broker_running', 'a listener already owns this socket')
                finally:
                    probe.close()
                current = self.path.lstat()
                if (current.st_dev, current.st_ino) != (existing.st_dev, existing.st_ino):
                    raise BrokerError('socket_changed', 'socket path changed during stale check')
                self.path.unlink()

            listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                listener.bind(str(self.path))
                os.chmod(self.path, 0o600, follow_symlinks=False)
                info = self.path.lstat()
                if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o600:
                    raise BrokerError('unsafe_socket', 'bound socket did not retain private ownership')
                self.socket_identity = (info.st_dev, info.st_ino)
                listener.listen(16)
                listener.settimeout(self.accept_timeout)
                self.listener = listener
            except BaseException:
                listener.close()
                raise
        except BaseException:
            self.close()
            raise

    def _peer_uid(self, client):
        raw = client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i'))
        _, uid, _ = struct.unpack('3i', raw)
        return uid

    def _receive(self, client):
        client.settimeout(10)
        data = bytearray()
        while True:
            chunk = client.recv(min(65536, self.max_request_bytes + 1 - len(data)))
            if not chunk:
                if not data:
                    raise BrokerError('invalid_json', 'empty request')
                raise BrokerError('invalid_json', 'request ended before its JSON line completed')
            data.extend(chunk)
            if len(data) > self.max_request_bytes:
                raise BrokerError('too_large', 'request exceeds 8 MiB')
            newline = data.find(b'\n')
            if newline >= 0:
                if newline != len(data) - 1:
                    raise BrokerError('invalid_json', 'one request is allowed per connection')
                return _bounded_json_line(bytes(data), self.max_request_bytes, 'request')

    def _send(self, client, response):
        try:
            raw = _encode_line(response, self.max_response_bytes)
        except BrokerError:
            raw = b'{"ok":false,"error":"response_too_large"}\n'
        try:
            client.settimeout(60)
            client.sendall(raw)
        except OSError:
            # The accepted operation remains in broker memory for result/reconnect.
            pass

    def handle_client(self, client):
        value = None
        try:
            if self._peer_uid(client) != os.geteuid():
                raise BrokerError('peer_refused', 'socket peer must have the broker user id')
            value = self._receive(client)
            response = self.broker.handle(value)
            if (isinstance(value, dict) and value.get('command') == 'start' and
                    response.get('ok') is not True):
                self.broker.report_failure('start', response.get('error'))
        except BrokerError as error:
            if isinstance(value, dict) and value.get('command') == 'status':
                self.broker.report_failure('status', error.error)
            response = {'ok': False, 'error': error.error}
        except (OSError, ValueError, TypeError):
            if isinstance(value, dict) and value.get('command') == 'status':
                self.broker.report_failure('status', 'invalid_request')
            response = {'ok': False, 'error': 'invalid_request'}
        self._send(client, response)

    def _serve_client(self, client):
        thread = threading.current_thread()
        try:
            with client:
                self.handle_client(client)
        finally:
            with self.client_threads_lock:
                self.client_threads.discard(thread)

    def serve(self):
        if self.listener is None:
            self.bind()
        while not self.stop_event.is_set():
            try:
                client, _ = self.listener.accept()
            except socket.timeout:
                self.broker.tick()
                continue
            except OSError:
                if self.stop_event.is_set():
                    break
                raise
            # Observe cancellation, guardian loss, and child exits before a
            # concurrent status/result client can read the previous snapshot.
            self.broker.tick()
            thread = threading.Thread(target=self._serve_client, args=(client,),
                                     name='cu-relay-client', daemon=True)
            with self.client_threads_lock:
                self.client_threads.add(thread)
            thread.start()
        self.broker.begin_shutdown()
        self._cleanup_loop()

    def _cleanup_loop(self):
        warned = False
        started = time.monotonic()
        while not self.broker.cleanup_complete():
            self.broker.tick()
            if not warned and time.monotonic() - started >= 40:
                print('session_remote: cleanup is still pending; retained session state was left intact',
                      file=sys.stderr, flush=True)
                warned = True
            time.sleep(0.05)
        self.broker.tick()

    def request_stop(self):
        self.stop_event.set()
        if self.listener is not None:
            try:
                self.listener.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    def handle_signal(self, signal_number=None, frame=None):
        self.request_stop()
        self.broker.begin_shutdown()

    def close(self):
        if self.listener is not None:
            self.listener.close()
            self.listener = None
        if self.socket_identity is not None:
            try:
                info = self.path.lstat()
                if (info.st_dev, info.st_ino) == self.socket_identity:
                    self.path.unlink()
            except FileNotFoundError:
                pass
            self.socket_identity = None
        if self.lock_file is not None:
            self.lock_file.close()
            self.lock_file = None


def _exchange(value, path=None, timeout=60):
    path = _default_socket() if path is None else Path(path)
    raw = _encode_line(value, MAX_REQUEST_BYTES)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.settimeout(timeout)
        client.connect(str(path))
        client.sendall(raw)
        client.shutdown(socket.SHUT_WR)
        data = bytearray()
        while len(data) <= MAX_RESPONSE_BYTES:
            chunk = client.recv(min(65536, MAX_RESPONSE_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
            if b'\n' in data:
                break
        if len(data) > MAX_RESPONSE_BYTES:
            raise BrokerError('response_too_large', 'broker response exceeds 32 MiB')
        response = _bounded_json_line(bytes(data), MAX_RESPONSE_BYTES, 'broker response')
        if not isinstance(response, dict):
            raise BrokerError('invalid_response', 'broker response must be an object')
        return response
    except BrokerError:
        raise
    except OSError as error:
        raise BrokerError('broker_unavailable', 'broker socket is unavailable') from error
    finally:
        client.close()


def _new_start_id():
    # Monotonic prefix lets the broker reject an evicted old start id with one cache entry.
    return f'{time.monotonic_ns():016x}{secrets.token_hex(8)}'


def _lease_path(path):
    return Path(path).expanduser()


def _read_lease(path):
    raw = _safe_read_file(path, 65536)
    try:
        lease = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise BrokerError('invalid_lease_file', 'lease file is malformed') from error
    if (not isinstance(lease, dict) or lease.get('version') != 1 or
            not isinstance(lease.get('owner'), str) or
            not isinstance(lease.get('start_id'), str) or not TOKEN.fullmatch(lease['start_id']) or
            not isinstance(lease.get('lease_secret'), str) or not SECRET.fullmatch(lease['lease_secret']) or
            not isinstance(lease.get('broker_generation'), str) or
            not TOKEN.fullmatch(lease['broker_generation'])):
        raise BrokerError('invalid_lease_file', 'lease file is malformed')
    generation = lease.get('generation')
    if generation is not None and (not isinstance(generation, str) or not TOKEN.fullmatch(generation)):
        raise BrokerError('invalid_lease_file', 'lease file is malformed')
    return lease


def _write_new_lease(path, lease):
    parent = path.parent
    try:
        info = parent.lstat()
    except OSError as error:
        raise BrokerError('lease_file_unavailable', 'lease directory must already exist') from error
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid():
        raise BrokerError('unsafe_lease_directory', 'lease directory must be owned by this user')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as error:
        raise BrokerError('lease_file_exists', 'lease file already exists') from error
    except OSError as error:
        raise BrokerError('lease_file_unavailable', 'could not create private lease file') from error
    identity = os.fstat(fd)
    try:
        raw = _encode_line(lease, 65536)
        data = memoryview(raw[:-1])
        while data:
            written = os.write(fd, data)
            if written <= 0:
                raise BrokerError('lease_file_write_failed', 'private lease file write was incomplete')
            data = data[written:]
        os.fsync(fd)
        os.fchmod(fd, 0o600)
    except BaseException:
        os.close(fd)
        try:
            current = path.lstat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                path.unlink()
        except OSError:
            pass
        raise
    else:
        os.close(fd)


def _replace_lease(path, lease):
    try:
        info = path.lstat()
    except OSError as error:
        raise BrokerError('lease_file_unavailable', 'lease file disappeared') from error
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or
            stat.S_IMODE(info.st_mode) != 0o600):
        raise BrokerError('unsafe_lease_file', 'lease file must remain a private regular file')
    raw = _encode_line(lease, 65536)[:-1]
    fd, temporary = tempfile.mkstemp(prefix='.relay-lease-', dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        current = path.lstat()
        if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
            raise BrokerError('lease_file_changed', 'lease file changed while updating')
        os.replace(temporary, path)
        dir_fd = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _lease_request(command, lease, **extra):
    if not lease.get('generation'):
        raise BrokerError('start_outcome_unknown', 'repeat start with this lease file to recover its outcome')
    return {'command': command, 'owner': lease['owner'],
            'generation': lease['generation'], 'lease_secret': lease['lease_secret'], **extra}


def _client_start(owner, lease_path):
    lease_path = _lease_path(lease_path)
    status = _exchange({'command': 'status'})
    if status.get('ok') is not True or not isinstance(status.get('broker_generation'), str):
        raise BrokerError(status.get('error', 'broker_unavailable'), 'broker status is unavailable')
    if _lexists(lease_path):
        lease = _read_lease(lease_path)
        if lease['owner'] != owner:
            raise BrokerError('lease_owner_mismatch', 'existing lease file belongs to another owner')
        if lease['broker_generation'] != status['broker_generation']:
            raise BrokerError('broker_changed', 'broker restarted; inspect status and create a new lease only after cleanup')
    else:
        lease = {'version': 1, 'owner': owner, 'start_id': _new_start_id(),
                 'lease_secret': secrets.token_hex(32),
                 'broker_generation': status['broker_generation'], 'generation': None}
        _write_new_lease(lease_path, lease)
    response = _exchange({'command': 'start', 'owner': owner,
                          'start_id': lease['start_id'],
                          'lease_secret': lease['lease_secret'],
                          'broker_generation': lease['broker_generation']})
    if response.get('ok') is True and isinstance(response.get('generation'), str):
        lease['generation'] = response['generation']
        _replace_lease(lease_path, lease)
    return response


def _client_with_lease(command, lease_path, **extra):
    lease = _read_lease(_lease_path(lease_path))
    status = _exchange({'command': 'status'})
    if status.get('broker_generation') != lease['broker_generation']:
        raise BrokerError('broker_changed', 'broker restarted; the prior task outcome is unknown')
    if command == 'status':
        request = _lease_request('status', lease, lease_file=True)
    else:
        request = _lease_request(command, lease, **extra)
    return _exchange(request, timeout=REQUEST_TIMEOUT + 5 if command == 'result' else 60)


def _client_finish(lease_path, *, timeout=120.0):
    response = _client_with_lease('finish', lease_path)
    if response.get('ok') is not True:
        return response
    deadline = time.monotonic() + timeout
    while True:
        status = _client_with_lease('status', lease_path)
        if status.get('ok') is not True:
            return status
        if (status.get('state') in ('finished', 'failed') and
                status.get('guardian') != 'active'):
            return {'ok': status['state'] == 'finished', 'status': status['state'],
                    'generation': status.get('generation'),
                    'driver': status.get('driver'), 'guardian': status.get('guardian'),
                    'error': status.get('error')}
        if time.monotonic() >= deadline:
            return {'ok': False, 'status': 'cleaning', 'error': 'cleanup_pending'}
        time.sleep(0.1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    serve = sub.add_parser('serve', help='run the idle Unix-socket broker')
    serve.add_argument('--socket', type=Path, default=_default_socket())
    serve.add_argument('--envsteal-test-proof-fd', type=int, help=argparse.SUPPRESS)
    status = sub.add_parser('status', help='read broker and task state')
    status.add_argument('--lease-file', type=Path)
    start = sub.add_parser('start', help='start one owned session task')
    start.add_argument('--owner', required=True)
    start.add_argument('--lease-file', type=Path, required=True)
    request = sub.add_parser('request', help='submit one existing driver envelope')
    request.add_argument('--lease-file', type=Path, required=True)
    request.add_argument('--sequence', type=int, required=True)
    request.add_argument('--request', type=Path, required=True)
    result = sub.add_parser('result', help='retrieve one accepted request result')
    result.add_argument('--lease-file', type=Path, required=True)
    result.add_argument('--sequence', type=int, required=True)
    finish = sub.add_parser('finish', help='finish the owned task through the supervisor')
    finish.add_argument('--lease-file', type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == 'serve':
        if args.envsteal_test_proof_fd is not None:
            try:
                _envsteal_test_proof(args.envsteal_test_proof_fd)
            except Exception:
                print(json.dumps({'ok': False, 'error': 'test_proof_failed'}),
                      file=sys.stderr, flush=True)
                return 1
            finally:
                try:
                    os.close(args.envsteal_test_proof_fd)
                except OSError:
                    pass
        broker = Broker()
        server = UnixSocketServer(broker, args.socket)
        previous = {}
        def stop(signum, frame):
            server.handle_signal(signum, frame)
        try:
            server.bind()
            for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                previous[sig] = signal.signal(sig, stop)
            server.serve()
        except Exception as error:
            print(json.dumps({'ok': False, 'error': getattr(error, 'error', 'broker_failed')}),
                  file=sys.stderr, flush=True)
            return 1
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            server.close()
        return 0

    try:
        if args.command == 'status':
            response = (_exchange({'command': 'status'}) if args.lease_file is None else
                        _client_with_lease('status', args.lease_file))
        elif args.command == 'start':
            if not re.fullmatch(r'[A-Za-z0-9_.:@+-]{1,80}', args.owner):
                raise BrokerError('invalid_owner', 'owner must be 1..80 safe characters')
            response = _client_start(args.owner, args.lease_file)
        elif args.command == 'request':
            raw = _safe_read_file(args.request, MAX_REQUEST_BYTES)
            try:
                envelope = json.loads(raw.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise BrokerError('invalid_json', 'driver request file is not valid UTF-8 JSON') from error
            response = _client_with_lease('request', args.lease_file,
                                          sequence=args.sequence, request=envelope)
        elif args.command == 'result':
            response = _client_with_lease('result', args.lease_file, sequence=args.sequence)
        elif args.command == 'finish':
            response = _client_finish(args.lease_file)
        else:
            raise BrokerError('unsupported_command', 'unsupported command')
        print(json.dumps(response, ensure_ascii=False, separators=(',', ':')))
        return 0 if response.get('ok') is True else 1
    except BrokerError as error:
        print(json.dumps({'ok': False, 'error': error.error}, separators=(',', ':')))
        return 1
    except Exception:
        print(json.dumps({'ok': False, 'error': 'broker_command_failed'}, separators=(',', ':')))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

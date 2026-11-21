#!/usr/bin/env python3
"""Central overlay control: the computer-use pill shows whenever ANY AI
controls the machine, whatever the method.

Any agent (DOM/BiDi, CLI-ified, shell, computer-use, anything) calls:
  overlay.py acquire --agent Muse --method BiDi
before it starts controlling, and:
  overlay.py release --agent Muse
when it is done. The pill shows the controlling agent and method, for
example "Muse via BiDi", so the user always knows an AI is driving.

Reference counted: the pill hides only when ALL holders released.
Session aware: if a computer-use session is live, its own pill already
shows, so the daemon forwards show/label to the session indicator instead
of spawning a second one. If the session dies while holders remain, the
daemon spawns its own indicator and takes over.

State lives in ~/.cache/agent-computer-use/overlay/ (0700). The daemon is
started detached on first acquire and exits when the holder count hits 0.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'agent-computer-use'
OVERLAY_DIR = BASE / 'overlay'
HOLDERS_FILE = OVERLAY_DIR / 'holders.json'
DAEMON_FILE = OVERLAY_DIR / 'daemon.json'
SOCKET_FILE = OVERLAY_DIR / 'overlay.sock'
LOCK_FILE = OVERLAY_DIR / 'holders.lock'
LOG_FILE = OVERLAY_DIR / 'daemon.log'
SESSION_FILE = BASE / 'session.json'
_STARTED = time.monotonic()
MAX_LABEL = 40


def _log(event, **fields):
    record = {
        'event': event,
        'wall_time': datetime.now().astimezone().isoformat(timespec='milliseconds'),
        'elapsed_ms': max(0, round((time.monotonic() - _STARTED) * 1000)),
    }
    record.update(fields)
    line = '[overlay] ' + json.dumps(record, sort_keys=True, separators=(',', ':'))
    try:
        print(line, file=sys.stderr, flush=True)
    except OSError:
        pass


def _label_for(agent, method):
    if not agent and not method:
        return 'Computer use active'
    label = (agent + ' via ' + method).strip(' ')
    return label[:MAX_LABEL] if label else 'Computer use active'


def _prepare():
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    OVERLAY_DIR.chmod(0o700)


@contextmanager
def _holders_lock():
    _prepare()
    fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def load_holders():
    try:
        data = json.loads(HOLDERS_FILE.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_holders(holders):
    _prepare()
    tmp = HOLDERS_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(holders, sort_keys=True, indent=2))
    tmp.chmod(0o600)
    tmp.replace(HOLDERS_FILE)


def add_holder(agent, method, pid=None):
    """Record a holder under the lock. Returns (holders, is_new)."""
    with _holders_lock():
        holders = load_holders()
        is_new = agent not in holders
        holders[agent] = {
            'method': method,
            'acquired': datetime.now().astimezone().isoformat(timespec='seconds'),
            'pid': pid,
        }
        save_holders(holders)
        return holders, is_new


def remove_holder(agent):
    """Remove a holder under the lock. Returns (holders, was_present)."""
    with _holders_lock():
        holders = load_holders()
        was_present = agent in holders
        holders.pop(agent, None)
        save_holders(holders)
        return holders, was_present


def prune_dead_holders():
    """Drop holders whose recorded pid no longer exists. Returns pruned names."""
    with _holders_lock():
        holders = load_holders()
        pruned = []
        for agent, info in list(holders.items()):
            pid = info.get('pid')
            if isinstance(pid, int) and pid > 0:
                try:
                    os.kill(pid, 0)
                except (ProcessLookupError, PermissionError):
                    pruned.append(agent)
                    holders.pop(agent, None)
                except OSError:
                    pass
        if pruned:
            save_holders(holders)
        return pruned


def session_live():
    """True when a computer-use session indicator answers. Probing with a
    duplicate show is idempotent: no redraw, no visual change."""
    try:
        saved = json.loads(SESSION_FILE.read_text())
        token = saved.get('token')
    except (OSError, ValueError, AttributeError):
        return False
    if saved.get('version') not in (3, 4) or not isinstance(token, str):
        return False
    try:
        import indicator
        return bool(indicator.request(BASE, 'show'))
    except (RuntimeError, OSError, ValueError):
        return False


def session_label(label):
    try:
        import indicator
        return bool(indicator.request(BASE, 'label ' + label))
    except (RuntimeError, OSError, ValueError):
        return False


def wayland_env():
    """Env for spawning the native indicator. Steals the live Wayland
    session vars when the caller (e.g. SSH) does not carry them."""
    env = dict(os.environ)
    if env.get('HYPRLAND_INSTANCE_SIGNATURE') and env.get('WAYLAND_DISPLAY'):
        return env
    runtime = Path('/run/user/1000')
    hypr = runtime / 'hyprland'
    try:
        sig_dirs = [d for d in hypr.iterdir() if d.is_dir()] if hypr.is_dir() else []
    except OSError:
        sig_dirs = []
    if sig_dirs:
        env['HYPRLAND_INSTANCE_SIGNATURE'] = sig_dirs[0].name
    env.setdefault('WAYLAND_DISPLAY', 'wayland-1')
    env.setdefault('XDG_RUNTIME_DIR', str(runtime))
    return env


class Daemon:
    def __init__(self):
        self.native = None
        self.owner = 'none'
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def _spawn_native(self, env):
        import indicator
        self.native = indicator.Native(env)
        self.owner = 'daemon'
        _log('native_spawned', owner=self.owner)

    def _close_native(self):
        if self.native is not None:
            try:
                self.native.close()
            except (OSError, RuntimeError):
                pass
            self.native = None
        self.owner = 'none'

    def _ensure_native(self):
        """Respawn the native indicator when it died while holders remain.
        This is the recovery for I12 (overlay vanished while the worker
        lived): a discarded buffer or an ack timeout quits the native
        process, and the daemon must bring the pill back instead of
        leaving holders with no visible indicator. Returns True when a
        live native process is available afterwards."""
        if self.owner != 'daemon':
            return self.native is not None
        if self.native is not None:
            try:
                if self.native.process.poll() is None:
                    return True
            except (OSError, AttributeError):
                pass
            _log('native_dead')
            self._close_native()
        try:
            self._spawn_native(wayland_env())
            _log('native_respawned')
            return True
        except (OSError, RuntimeError) as error:
            _log('native_spawn_failed', error=str(error))
            return False

    def _show_label(self, label):
        """Show the pill with the given label, via whoever owns it."""
        if self.owner == 'daemon' and self.native is not None:
            if not self._ensure_native():
                return
            try:
                self.native.command('label ' + label)
                self.native.command('show')
            except (OSError, RuntimeError):
                if self._ensure_native():
                    try:
                        self.native.command('label ' + label)
                        self.native.command('show')
                    except (OSError, RuntimeError):
                        _log('native_command_failed')
        elif self.owner == 'session':
            session_label(label)
            session_live()

    def apply_holders(self):
        """Reconcile pill state with the holder registry. Returns status."""
        holders = load_holders()
        with self.lock:
            if not holders:
                if self.owner == 'daemon':
                    try:
                        self.native.command('hide')
                    except (OSError, RuntimeError):
                        pass
                    self._close_native()
                return {'visible': False, 'owner': 'none', 'holders': {}}
            latest = sorted(holders.items(), key=lambda kv: kv[1].get('acquired', ''))[-1]
            label = _label_for(latest[0], latest[1].get('method', ''))
            live = session_live()
            if live and self.owner != 'session':
                if self.owner == 'daemon':
                    try:
                        self.native.command('hide')
                    except (OSError, RuntimeError):
                        pass
                    self._close_native()
                self.owner = 'session'
                _log('handover_to_session')
            elif not live and self.owner != 'daemon':
                try:
                    self._spawn_native(wayland_env())
                except (OSError, RuntimeError) as error:
                    _log('native_spawn_failed', error=str(error))
                    return {'visible': False, 'owner': 'none', 'holders': holders,
                            'error': str(error)}
            self._show_label(label)
            return {'visible': True, 'owner': self.owner, 'holders': holders,
                    'label': label}

    def _monitor(self):
        empty_polls = 0
        while not self.stop_event.wait(2.0):
            try:
                status = self.apply_holders()
            except (OSError, RuntimeError) as error:
                _log('monitor_error', error=str(error))
                continue
            if not status.get('holders') and status.get('owner') == 'none':
                empty_polls += 1
                if empty_polls >= 3:
                    _log('daemon_idle_empty', empty_polls=empty_polls)
                    self.stop_event.set()
            else:
                empty_polls = 0

    def serve(self):
        _prepare()
        try:
            SOCKET_FILE.unlink()
        except OSError:
            pass
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(SOCKET_FILE))
        SOCKET_FILE.chmod(0o600)
        server.listen(4)
        server.settimeout(1.0)
        DAEMON_FILE.write_text(json.dumps({
            'pid': os.getpid(),
            'started': datetime.now().astimezone().isoformat(timespec='seconds'),
        }))
        DAEMON_FILE.chmod(0o600)
        monitor = threading.Thread(target=self._monitor, daemon=True)
        monitor.start()
        _log('daemon_started', pid=os.getpid())
        try:
            self.apply_holders()
            while not self.stop_event.is_set():
                try:
                    client, _ = server.accept()
                except socket.timeout:
                    continue
                with client:
                    client.settimeout(5)
                    data = bytearray()
                    try:
                        while b'\n' not in data and len(data) <= 1024:
                            chunk = client.recv(1024 - len(data) + 1)
                            if not chunk:
                                break
                            data.extend(chunk)
                    except OSError:
                        continue
                    try:
                        req = json.loads(data)
                    except ValueError:
                        continue
                    cmd = req.get('command', '')
                    if cmd == 'acquire':
                        add_holder(req.get('agent', ''), req.get('method', ''),
                                   req.get('pid'))
                        reply = self.apply_holders()
                    elif cmd == 'release':
                        holders, _ = remove_holder(req.get('agent', ''))
                        reply = self.apply_holders()
                        if not holders:
                            reply['daemon_exiting'] = True
                    elif cmd == 'sync':
                        reply = self.apply_holders()
                    elif cmd == 'status':
                        holders = load_holders()
                        reply = {'visible': bool(holders), 'owner': self.owner,
                                 'holders': holders}
                    elif cmd == 'stop':
                        reply = {'stopping': True}
                        self.stop_event.set()
                    else:
                        reply = {'error': 'unknown command'}
                    try:
                        client.sendall((json.dumps(reply) + '\n').encode())
                    except OSError:
                        pass
                    if cmd == 'release' and not load_holders():
                        self.stop_event.set()
        finally:
            if self.owner == 'daemon':
                try:
                    self.native.command('hide')
                except (OSError, RuntimeError, AttributeError):
                    pass
                self._close_native()
            try:
                server.close()
            except OSError:
                pass
            for path in (SOCKET_FILE, DAEMON_FILE):
                try:
                    path.unlink()
                except OSError:
                    pass
            _log('daemon_stopped')


def _daemon_running():
    try:
        info = json.loads(DAEMON_FILE.read_text())
        pid = info.get('pid')
        if isinstance(pid, int) and pid > 0:
            os.kill(pid, 0)
            return True
    except (OSError, ValueError, ProcessLookupError, PermissionError):
        return False
    return False


def _send_socket(req, timeout=10):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(timeout)
        client.connect(str(SOCKET_FILE))
        client.sendall((json.dumps(req) + '\n').encode())
        data = bytearray()
        while b'\n' not in data and len(data) < 65536:
            chunk = client.recv(65536 - len(data))
            if not chunk:
                break
            data.extend(chunk)
        return json.loads(data)


def _ensure_daemon():
    if _daemon_running():
        try:
            _send_socket({'command': 'status'}, timeout=3)
            return True
        except (OSError, ValueError):
            pass
    _prepare()
    log = open(str(LOG_FILE), 'ab', buffering=0)
    env = wayland_env()
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), 'daemon'],
        env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
        start_new_session=True, close_fds=True)
    _log('daemon_spawned', pid=proc.pid)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            # Another daemon may have won the bind race; reuse it if alive.
            time.sleep(0.5)
            if _daemon_running():
                try:
                    _send_socket({'command': 'status'}, timeout=2)
                    return True
                except (OSError, ValueError):
                    pass
            raise RuntimeError('overlay daemon exited during startup; see ' + str(LOG_FILE))
        try:
            _send_socket({'command': 'status'}, timeout=2)
            return True
        except (OSError, ValueError):
            time.sleep(0.2)
    raise RuntimeError('overlay daemon did not answer within 15s; see ' + str(LOG_FILE))


def cmd_acquire(args):
    holders, _ = add_holder(args.agent, args.method, args.pid)
    _ensure_daemon()
    label = args.label or _label_for(args.agent, args.method)
    reply = _send_socket({'command': 'acquire', 'agent': args.agent,
                          'method': args.method, 'pid': args.pid})
    reply['label'] = label
    _log('acquired', agent=args.agent, method=args.method, holders=len(holders))
    print(json.dumps(reply, sort_keys=True))
    return 0


def cmd_release(args):
    if not _daemon_running():
        holders, was_present = remove_holder(args.agent)
        _log('released_no_daemon', agent=args.agent, was_present=was_present)
        print(json.dumps({'visible': False, 'owner': 'none', 'holders': holders}))
        return 0
    try:
        reply = _send_socket({'command': 'release', 'agent': args.agent})
    except (OSError, ValueError):
        holders, _ = remove_holder(args.agent)
        reply = {'visible': bool(holders), 'owner': 'none', 'holders': holders}
    _log('released', agent=args.agent)
    print(json.dumps(reply, sort_keys=True))
    return 0


def cmd_status(args):
    prune_dead_holders()
    holders = load_holders()
    info = {'visible': bool(holders), 'holders': holders}
    if _daemon_running():
        try:
            info = _send_socket({'command': 'status'})
        except (OSError, ValueError):
            info['owner'] = 'unknown'
    else:
        info['owner'] = 'none'
    print(json.dumps(info, sort_keys=True, indent=2))
    return 0


def cmd_stop(args):
    if _daemon_running():
        try:
            _send_socket({'command': 'stop'})
        except (OSError, ValueError):
            pass
    with _holders_lock():
        save_holders({})
    for path in (SOCKET_FILE, DAEMON_FILE):
        try:
            path.unlink()
        except OSError:
            pass
    _log('stopped')
    return 0


def cmd_daemon(args):
    Daemon().serve()
    return 0


@contextmanager
def hold(agent, method):
    """Python helper: show the overlay for the block, hide after."""
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve()), 'acquire',
             '--agent', agent, '--method', method], check=True,
            capture_output=True)
    try:
        yield
    finally:
        _sp.run([sys.executable, str(Path(__file__).resolve()), 'release',
                 '--agent', agent], check=True, capture_output=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    acquire = sub.add_parser('acquire')
    acquire.add_argument('--agent', required=True)
    acquire.add_argument('--method', required=True)
    acquire.add_argument('--label', default=None)
    acquire.add_argument('--pid', type=int, default=None)
    acquire.set_defaults(func=cmd_acquire)
    release = sub.add_parser('release')
    release.add_argument('--agent', required=True)
    release.set_defaults(func=cmd_release)
    status = sub.add_parser('status')
    status.set_defaults(func=cmd_status)
    stop = sub.add_parser('stop')
    stop.set_defaults(func=cmd_stop)
    daemon = sub.add_parser('daemon')
    daemon.set_defaults(func=cmd_daemon)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())

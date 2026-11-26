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
    # Pill display is always the plain readable string. The agent/method
    # that holds the pill is still tracked internally in holders.json;
    # only what the user sees on screen is simplified (2026-11-23,
    # owner: "S2-flip via CDP" is unreadable jargon, just show
    # "Computer use active").
    return 'Computer use active'


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


def _holder_key(agent, pid=None):
    """One entry per live run: key by (agent, pid) when a pid is known,
    else by the bare agent name (backward compat for callers and old
    holders.json entries that carry no pid)."""
    if isinstance(pid, int) and pid > 0:
        return '%s:%d' % (agent, pid)
    return agent


def add_holder(agent, method, pid=None):
    """Record a holder under the lock. Returns (holders, is_new)."""
    with _holders_lock():
        holders = load_holders()
        key = _holder_key(agent, pid)
        is_new = key not in holders
        holders[key] = {
            'agent': agent,
            'method': method,
            'acquired': datetime.now().astimezone().isoformat(timespec='seconds'),
            'pid': pid,
        }
        save_holders(holders)
        return holders, is_new


def remove_holder(agent, pid=None):
    """Remove exactly one holder under the lock. Returns (holders, was_present).

    With a pid, only that run's entry (agent:pid) is removed. Without a
    pid, only the bare agent entry is removed. A pid-keyed removal never
    touches the bare entry, and a pid-less removal never touches
    pid-keyed entries, so no call ever removes another run's PID-KEYED
    entry. The bare entry is the one exception: two pid-less runs of the
    same agent share it, so a pid-less removal can drop another
    pid-less run's holder (H1 bare-bare). That is why every live caller
    must pass a real pid: overlay.hold keys by the calling process pid,
    s2_flip keys by a laptop sleeper pid, cdp.mjs and first_action key
    by their own pid. A bare holder only survives from legacy or manual
    pid-less callers.
    This is the R6/C1 fix: a failed acquire with pid None used to wipe
    every holder of the same agent, including a live pid-keyed holder
    of a concurrent run, and the pill then dropped mid-run for a run
    that never failed.
    """
    with _holders_lock():
        holders = load_holders()
        key = _holder_key(agent, pid)
        was_present = key in holders
        holders.pop(key, None)
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
    session vars when the caller (e.g. SSH) does not carry them.

    Signature discovery is delegated to hypr_cmd.desktop_env, the one
    proven source of truth in this repo: the instance directory lives
    under /run/user/1000/hypr/, NOT /run/user/1000/hyprland/ (which does
    not exist on this machine; the old code read that dead directory, so
    an SSH-started daemon never got a signature and every standalone
    native spawn failed with the liquid-glass error even though hyprglass
    itself was healthy). A caller-provided signature is kept as-is. When
    no instance can be discovered, the env is returned without a
    signature, exactly like before; the spawn then fails loudly instead
    of crashing here.
    """
    env = dict(os.environ)
    if env.get('HYPRLAND_INSTANCE_SIGNATURE') and env.get('WAYLAND_DISPLAY'):
        return env
    if env.get('HYPRLAND_INSTANCE_SIGNATURE'):
        env.setdefault('WAYLAND_DISPLAY', 'wayland-1')
        env.setdefault('XDG_RUNTIME_DIR', '/run/user/1000')
        return env
    runtime = Path(env.get('XDG_RUNTIME_DIR') or '/run/user/1000')
    try:
        from hypr_cmd import desktop_env
        discovered = desktop_env(signature_dir=str(runtime / 'hypr'))
        env['HYPRLAND_INSTANCE_SIGNATURE'] = discovered['HYPRLAND_INSTANCE_SIGNATURE']
        # C2: never clobber a caller-provided display; the discovered
        # one is only the fallback (the old code overwrote it).
        env.setdefault('WAYLAND_DISPLAY', discovered['WAYLAND_DISPLAY'])
    except (ImportError, ValueError):
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
        """Show the pill with the given label, via whoever owns it.
        Returns True only when the show was acknowledged (redteam A3):
        a failed show must not be reported as visible."""
        if self.owner == 'daemon':
            if not self._ensure_native():
                return False
            try:
                self.native.command('label ' + label)
                self.native.command('show')
                return True
            except (OSError, RuntimeError):
                if self._ensure_native():
                    try:
                        self.native.command('label ' + label)
                        self.native.command('show')
                        return True
                    except (OSError, RuntimeError):
                        _log('native_command_failed')
                return False
        elif self.owner == 'session':
            return bool(session_label(label) and session_live())
        return False

    def apply_holders(self):
        """Reconcile pill state with the holder registry. Returns status."""
        prune_dead_holders()
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
            label = _label_for(latest[1].get('agent', latest[0]),
                               latest[1].get('method', ''))
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
            if not self._show_label(label):
                return {'visible': False, 'owner': self.owner,
                        'holders': holders, 'label': label,
                        'error': 'pill show failed'}
            return {'visible': True, 'owner': self.owner, 'holders': holders,
                    'label': label}

    def status_reply(self):
        """Truthful status: reconcile first, then report.

        The old 'status' reply was {'visible': bool(holders)}, which lied
        (visible True while no pill rendered) and misled a verify lane.
        apply_holders is what the monitor already runs every 2s, so this
        adds no new side-effect class: it spawns/shows only when holders
        exist, and reports visible False with the error when the pill
        cannot be shown.
        """
        return self.apply_holders()

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
                        holders, _ = remove_holder(req.get('agent', ''),
                                                   req.get('pid'))
                        reply = self.apply_holders()
                        if not holders:
                            reply['daemon_exiting'] = True
                    elif cmd == 'sync':
                        reply = self.apply_holders()
                    elif cmd == 'status':
                        reply = self.status_reply()
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
    prune_dead_holders()
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
    try:
        _ensure_daemon()
        label = _label_for(args.agent, args.method)
        reply = _send_socket({'command': 'acquire', 'agent': args.agent,
                              'method': args.method, 'pid': args.pid})
        reply['label'] = label
    except Exception:
        # Re-review D1: remove the just-added holder on failure, or the
        # entry (pid None on the CLI path) stays in holders.json forever:
        # prune_dead_holders only drops int pids, so it can never heal it,
        # and the stale entry keeps the pill up after the run ends.
        # The label assignment stays inside the try: a non-dict reply
        # (unreachable through the real daemon, every reply is a dict
        # literal) would raise TypeError here and leak the same way
        # (D1 re-check hardening note).
        try:
            remove_holder(args.agent, args.pid)
        except Exception:
            pass
        raise
    if reply.get('visible') is not True:
        # Fail closed (W-PILLFIX): the daemon answered but the pill did
        # not render, so this acquire must refuse instead of letting the
        # caller drive invisibly. chromium_cli._pill_hold documents that
        # overlay.hold raises here, and cdp.mjs treats any non-zero exit
        # as 'CDP pill unavailable'; both were silently bypassed while
        # cmd_acquire returned 0 with visible False. Remove the
        # just-added holder (same D1 reasoning as above) so a pid-less
        # stale entry cannot linger, log the daemon's error to stderr,
        # and still print the reply JSON for diagnosis.
        try:
            remove_holder(args.agent, args.pid)
        except Exception:
            pass
        _log('acquire_invisible', agent=args.agent, method=args.method,
             error=str(reply.get('error', 'pill show failed')))
        print(json.dumps(reply, sort_keys=True))
        return 1
    _log('acquired', agent=args.agent, method=args.method, holders=len(holders))
    print(json.dumps(reply, sort_keys=True))
    return 0


def cmd_release(args):
    if not _daemon_running():
        holders, was_present = remove_holder(args.agent, args.pid)
        _log('released_no_daemon', agent=args.agent, was_present=was_present)
        print(json.dumps({'visible': False, 'owner': 'none', 'holders': holders}))
        return 0
    try:
        reply = _send_socket({'command': 'release', 'agent': args.agent,
                              'pid': args.pid})
    except (OSError, ValueError):
        holders, _ = remove_holder(args.agent, args.pid)
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
        # No daemon means no daemon-owned pill. The pill can still be up
        # via a live session indicator, so report that instead of
        # bool(holders): with no daemon and no session, holders alone
        # never render anything (W-PILLFIX).
        live = bool(holders) and session_live()
        info = {'visible': live, 'owner': 'session' if live else 'none',
                'holders': holders}
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
def hold(agent, method, pid=None):
    """Python helper: show the overlay for the block, hide after.

    Pid-keyed by default: the holder key is (agent, pid of the calling
    process), so two concurrent runs of the same agent never share one
    bare key (H1 bare-bare). Pass an explicit pid only when the calling
    process is not the process that lives for the block. The pid must
    be real on the machine holding the registry: the daemon prunes a
    holder whose pid does not exist there, so a pid from another
    machine would be dropped within one monitor tick (~2s). The
    calling process lives for the whole `with` block by definition,
    so its pid is alive for the hold and prune can heal the holder if
    the caller dies mid-block.
    """
    if pid is None:
        pid = os.getpid()
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve()), 'acquire',
             '--agent', agent, '--method', method,
             '--pid', str(pid)], check=True, capture_output=True)
    try:
        yield
    finally:
        _sp.run([sys.executable, str(Path(__file__).resolve()), 'release',
                 '--agent', agent, '--pid', str(pid)], check=True,
                capture_output=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    acquire = sub.add_parser('acquire')
    acquire.add_argument('--agent', required=True)
    acquire.add_argument('--method', required=True)
    acquire.add_argument('--label', default=None)
    acquire.add_argument('--pid', type=int, default=None,
                         help='pid of the calling process; the holder key '
                         'is agent:pid, so concurrent runs of one agent '
                         'never share a key (default: none, bare agent key)')
    acquire.set_defaults(func=cmd_acquire)
    release = sub.add_parser('release')
    release.add_argument('--agent', required=True)
    # R11: accepted for caller compatibility (cdp.mjs and s2_flip both
    # pass --method); the holder key is (agent, pid), the method is not
    # part of it, so the value is ignored for removal.
    release.add_argument('--method', default=None)
    release.add_argument('--pid', type=int, default=None,
                         help='pid of the holder to drop; a pid-less '
                         'release only removes the bare agent entry, a '
                         'pid-keyed holder needs its own --pid')
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

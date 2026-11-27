#!/usr/bin/env python3
"""Launch helper for dedicated throwaway Zen RDP sessions (D3).

One command creates a fresh profile, writes the devtools user.js
prefs, starts Zen with --start-debugger-server, waits for the
debugger port, and records a session file (pid + profile + port +
nonce) that `verify` and `stop` check before touching anything.

Guardrails (fail closed, chrome.enabled + prompt-connection=false
is a loaded gun):
- Profiles live under the system temp dir only. Anything outside
  is refused, which refuses the owner's real profile by
  construction; owner profile roots (~/.config/zen, ~/.zen,
  ~/.mozilla) are also refused by name.
- A profile directory is used only when it carries this tool's
  marker file (.zen-rdp-dedicated). An existing directory without
  the marker is refused, never adopted or overwritten.
- The debugger port must be free before launch; the listening
  pid's cmdline must contain the profile path after launch
  (rdp_client.check_port_owner).
- stop kills only the recorded pid, and only after its cmdline
  still contains the recorded profile path. No broad pkill, no
  compositor window-close.

Stdlib only. Sends no OS input; ydotool is banned and not used.
Generic: no hardcoded port, profile, or binary path defaults
(--zen-bin, ZEN_BIN env, or PATH lookup).
"""
import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MARKER_NAME = ".zen-rdp-dedicated"
SESSION_NAME = "session.json"
OWNER_PROFILE_ROOTS = (".config/zen", ".zen", ".mozilla")


class LaunchError(Exception):
    pass


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def user_js_text(port):
    """Devtools prefs a fresh profile needs or --start-debugger-server
    never listens (D3 footgun)."""
    return (
        'user_pref("devtools.chrome.enabled", true);\n'
        'user_pref("devtools.debugger.remote-enabled", true);\n'
        'user_pref("devtools.debugger.prompt-connection", false);\n'
        'user_pref("devtools.debugger.remote-host", "127.0.0.1");\n'
        f'user_pref("devtools.debugger.remote-port", {int(port)});\n'
    )


def marker_path(profile):
    return Path(profile) / MARKER_NAME


def read_marker(profile):
    p = marker_path(profile)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def write_marker(profile, port, nonce):
    data = {"tool": "launch_dedicated", "port": int(port), "nonce": nonce,
            "created_at": _now_iso()}
    marker_path(profile).write_text(json.dumps(data, indent=1) + "\n")
    return data


def validate_profile_dir(profile, create=False, port=None, nonce=None):
    """Return the resolved profile Path, or raise LaunchError.
    Fail closed: temp-dir only, owner roots refused by name,
    existing dirs need our marker, marker port must match."""
    path = Path(profile).expanduser().resolve()
    home = Path.home().resolve()
    for root in OWNER_PROFILE_ROOTS:
        owner_root = (home / root).resolve()
        if path == owner_root or owner_root in path.parents:
            raise LaunchError(
                f"REFUSED: {path} is inside an owner profile root "
                f"({owner_root}); dedicated sessions never touch the "
                "owner's profile")
    tmp = Path(tempfile.gettempdir()).resolve()
    if tmp not in path.parents:
        raise LaunchError(
            f"REFUSED: dedicated profiles live strictly under {tmp} "
            f"only (got {path}; the temp dir itself is not a profile)")
    if path.exists():
        marker = read_marker(path)
        if marker is None:
            raise LaunchError(
                f"REFUSED: {path} exists without a {MARKER_NAME} "
                "marker; refusing to adopt or overwrite a profile "
                "this tool did not create")
        if port is not None and marker.get("port") != int(port):
            raise LaunchError(
                f"REFUSED: marker in {path} is for port "
                f"{marker.get('port')}, not {port}")
        return path
    if not create:
        raise LaunchError(f"profile {path} does not exist")
    path.mkdir(parents=True)
    write_marker(path, port, nonce or uuid.uuid4().hex)
    return path


def find_zen_bin(explicit=None):
    cand = explicit or os.environ.get("ZEN_BIN") \
        or shutil.which("zen-bin") or shutil.which("zen")
    if not cand:
        raise LaunchError(
            "zen binary not found: pass --zen-bin or set ZEN_BIN")
    return cand


def _desktop_env():
    """Inherit the caller's env; fill Wayland session defaults from
    /run/user/<uid> when unset (SSH sessions carry none). Generic
    Linux paths only, no machine-specific values."""
    env = dict(os.environ)
    runtime = Path(f"/run/user/{os.getuid()}")
    env.setdefault("XDG_RUNTIME_DIR", str(runtime))
    if "WAYLAND_DISPLAY" not in env and (runtime / "wayland-1").exists():
        env["WAYLAND_DISPLAY"] = "wayland-1"
    if "DBUS_SESSION_BUS_ADDRESS" not in env and (runtime / "bus").exists():
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime}/bus"
    hypr = runtime / "hypr"
    if "HYPRLAND_INSTANCE_SIGNATURE" not in env and hypr.is_dir():
        entries = sorted(p.name for p in hypr.iterdir())
        if entries:
            env["HYPRLAND_INSTANCE_SIGNATURE"] = entries[0]
    return env


def port_listening(port, host="127.0.0.1"):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def wait_for_port(port, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_listening(port):
            return True
        time.sleep(0.2)
    return False


def session_path(profile):
    return Path(profile) / SESSION_NAME


def read_session(profile):
    p = session_path(profile)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _cmdline(pid):
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\0", b" ").decode(errors="replace")


def _pid_start(pid):
    """Process start time pin (same /proc field rdp_client uses),
    or None when unavailable."""
    try:
        from rdp_client import _proc_start_time
        return _proc_start_time(pid)
    except Exception:
        return None


def _cmdline_has_profile_token(cmd, path):
    """True when the exact profile path appears as a whole cmdline
    token (the --profile argument), not merely as a substring of
    some longer argument."""
    return str(path) in cmd.split()


def _load_validated_session(profile):
    """Shared session-file validation for verify() and stop():
    profile dir (temp-only, marker), marker+nonce match, recorded
    profile equals the resolved dir, marker/session port agreement.
    A forged or stale session.json (e.g. one naming the owner's
    pid) fails here before any signal is considered. Returns
    (path, marker, session_record)."""
    path = validate_profile_dir(profile)
    marker = read_marker(path)
    session_record = read_session(path)
    if session_record is None:
        raise LaunchError(f"no readable {SESSION_NAME} in {path}")
    if session_record.get("nonce") != marker.get("nonce"):
        raise LaunchError("session nonce does not match profile marker")
    if session_record.get("profile") != str(path):
        raise LaunchError(
            f"session profile {session_record.get('profile')!r} does "
            f"not match profile dir {path}")
    if session_record.get("port") != marker.get("port"):
        raise LaunchError(
            f"session port {session_record.get('port')} does not "
            f"match marker port {marker.get('port')}")
    return path, marker, session_record


def _check_live_pid(session_record, path):
    """Validate the recorded pid is the dedicated browser: alive,
    cmdline carries the exact profile token, start-time pin matches
    when the session recorded one. Returns the cmdline; raises
    LaunchError when the pid is alive but unverified. Empty string
    means the pid is dead."""
    pid = session_record.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        raise LaunchError(f"session pid is not a valid pid: {pid!r}")
    cmd = _cmdline(pid)
    if not cmd:
        return ""
    if not _cmdline_has_profile_token(cmd, path):
        raise LaunchError(
            f"recorded pid {pid} cmdline does not contain the exact "
            f"profile token {path}; refusing to trust the session file")
    pin = session_record.get("pid_start")
    if pin is not None:
        current = _pid_start(pid)
        if current is not None and str(current) != str(pin):
            raise LaunchError(
                f"recorded pid {pid} start time changed (pid reused?); "
                "refusing to trust the session file")
    return cmd


def verify_session(profile):
    """Check marker + session file + live pid + port. Returns the
    session dict; raises LaunchError on any mismatch."""
    path, _marker, session_record = _load_validated_session(profile)
    if not _check_live_pid(session_record, path):
        raise LaunchError(
            f"recorded pid {session_record.get('pid')} is not running")
    if not port_listening(int(session_record["port"])):
        raise LaunchError(f"port {session_record['port']} is not listening")
    return session_record


def launch(port, profile, zen_bin=None, timeout=20):
    nonce = uuid.uuid4().hex
    path = validate_profile_dir(profile, create=True, port=port, nonce=nonce)
    marker = read_marker(path)
    nonce = marker["nonce"]
    if port_listening(port):
        raise LaunchError(
            f"REFUSED: port {port} already has a listener; refusing "
            "to launch over it")
    (path / "user.js").write_text(user_js_text(port))
    zen = find_zen_bin(zen_bin)
    log = open(path / "zen.log", "ab")
    try:
        proc = subprocess.Popen(
            [zen, "-no-remote", "--profile", str(path),
             "--start-debugger-server", str(int(port)), "about:blank"],
            stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            start_new_session=True, env=_desktop_env())
    finally:
        log.close()
    try:
        if not wait_for_port(port, timeout=timeout):
            raise LaunchError(
                f"debugger port {port} did not listen within {timeout}s "
                f"(launched pid {proc.pid}; see {path}/zen.log)")
        # Record the pid that actually owns the port (the launcher pid
        # and the listener pid can differ), verified by cmdline.
        from rdp_client import check_port_owner
        pid, _cmd = check_port_owner(port, str(path))
    except Exception as e:
        # Never leave an orphan Zen without a session file: kill the
        # process we launched (its own session/group) before failing.
        _kill_launched(proc)
        if isinstance(e, LaunchError):
            raise
        raise LaunchError(str(e))
    session_record = {"pid": pid, "profile": str(path), "port": int(port),
               "nonce": nonce, "zen_bin": zen, "started_at": _now_iso(),
               "pid_start": _pid_start(pid)}
    session_path(path).write_text(json.dumps(session_record, indent=1) + "\n")
    return session_record


def _kill_launched(proc):
    """Kill a just-launched process group (start_new_session=True),
    SIGTERM then SIGKILL. Used only for processes this launch()
    call started; never for recorded/foreign pids."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=5)
        return
    except Exception:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except Exception:
            pass
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def stop(profile):
    # Same validation as verify() before any signal: profile dir,
    # marker + nonce, recorded profile/port agreement, exact
    # profile token in the live cmdline, start-time pin. A forged
    # session.json naming a foreign pid is refused here.
    path, _marker, session_record = _load_validated_session(profile)
    pid = session_record["pid"]
    cmd = _check_live_pid(session_record, path)
    if not cmd:
        return {"pid": pid, "profile": str(path), "result": "already dead"}
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if not _cmdline(pid):
            return {"pid": pid, "profile": str(path), "result": "stopped"}
        time.sleep(0.2)
    raise LaunchError(f"pid {pid} still alive 10s after SIGTERM")


def main():
    ap = argparse.ArgumentParser(
        description="Dedicated throwaway Zen RDP session launcher (D3)")
    ap.add_argument("--port", type=int, default=None,
                    help="debugger port for the dedicated session")
    ap.add_argument("--profile-dir", default=None,
                    help="profile dir under the temp dir "
                         "(default: <tmp>/zen-rdp-dedicated-<port>)")
    ap.add_argument("--zen-bin", default=None,
                    help="zen binary (or ZEN_BIN env, or PATH)")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--stop", action="store_true",
                    help="stop the session recorded in --profile-dir")
    ap.add_argument("--verify", action="store_true",
                    help="verify marker + session + pid + port only")
    args = ap.parse_args()
    try:
        if args.stop or args.verify:
            if not args.profile_dir:
                ap.error("--profile-dir is required with --stop/--verify")
            out = stop(args.profile_dir) if args.stop \
                else verify_session(args.profile_dir)
            print(json.dumps({"ok": True, **out}, indent=1))
            return 0
        if args.port is None:
            ap.error("--port is required to launch")
        profile = args.profile_dir or str(
            Path(tempfile.gettempdir()) / f"zen-rdp-dedicated-{args.port}")
        session_record = launch(args.port, profile, zen_bin=args.zen_bin,
                         timeout=args.timeout)
        print(json.dumps({"ok": True, **session_record}, indent=1))
        return 0
    except LaunchError as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=1))
        return 2


if __name__ == "__main__":
    sys.exit(main())

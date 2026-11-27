#!/usr/bin/env python3
"""Repo-owned Zen Browser CLI wrapper. Stdlib only.

Talks to Zen over WebDriver BiDi (Firefox Remote Agent) on a loopback
WebSocket, and reads the Zen profile read-only for history. This is the
Zen counterpart to the vendored CLI-Anything harnesses, but it is
repo-owned: there is no upstream harness for Zen, so nothing here is
vendored.

Why BiDi and not CDP: Zen is Firefox-based. Firefox documents Marionette
and WebDriver BiDi as its remote protocols, not CDP. Zen's own --help
lists --remote-debugging-port as "Start the Firefox Remote Agent".
Verified 2026-11-18 on the laptop against Zen 1.24.2b: a dedicated
headless instance with a fresh profile listens on 127.0.0.1:9222, logs
"WebDriver BiDi listening on ws://127.0.0.1:9222", and answers BiDi
(session.new, browsingContext.getTree/navigate/activate/close,
script.evaluate) at ws://127.0.0.1:9222/session. One gap:
browsingContext.createContext is "unknown command" in this build, so a
new tab is opened with window.open from an existing tab, then found in
getTree by its opener. Headless mode starts with two about:blank tabs.

Session rule (the safety core): the owner's own Zen runs WITHOUT a
remote debugging port (verified 2026-11-18: nothing listening on 9222,
2828 or 6000), so this wrapper can never attach to his session. Tab
commands only ever talk to a dedicated session this wrapper started
(`session start`), on a dedicated profile under
~/.cache/cli-anything-zen/profile, headless by default. The wrapper
never launches, kills or restarts his Zen, never closes his tabs, and
refuses any --profile inside ~/.config/zen. `session stop` only kills
a process whose cmdline contains the dedicated profile path recorded
in the state file.

Live-session opening is the one exception, and it is opt-in only:
`open --live <url>` runs `zen-browser --new-tab <url>`, which the
running Zen handles through its own remoting. The flag is documented
in `zen-browser --help`; it was deliberately NEVER run against his
session by this worker (it would add a tab to his Zen while he sleeps),
so it is marked PROPOSED-live in the skill. Use it only when he asked
for a page in his own Zen.

Pill gate (R3): control commands (open, navigate, activate, close)
acquire the central overlay pill before their BiDi session starts and
release it at session end; reads never acquire. `session start`
preflights overlay availability before spawning and holds the pill
(keyed to the Zen pid) until `session stop`. When the pill cannot be
shown the drive is refused ('BiDi pill unavailable'). CU_ZEN_PILL=0
disables the gate for fixture tests only, never for live work.

History reads his real profile read-only: places.sqlite is copied to a
temp file first (the live DB is locked while Zen runs) and opened
read-only. Nothing is ever written to the profile. Default profile is
auto-detected from ~/.config/zen/profiles.ini (the Default=1 profile).

Commands (each prints exactly one JSON object on stdout):
  session start [--port N] [--profile DIR] [--no-headless]
                        Start the dedicated BiDi session; records it
                        in the state file. Default port 9222 (tries
                        up to 9231 if busy), default profile
                        ~/.cache/cli-anything-zen/profile, headless.
  session stop          Stop the dedicated session, only the recorded
                        pid with the recorded profile in its cmdline.
  session status        State file, port and BiDi reachability probe.
                        Always exits 0; check `session_up`.
  tabs                  List tabs of the dedicated session: index,
                        url, title (title via script.evaluate). Tabs are
                        addressed by INDEX, never by BiDi context id:
                        context ids change on every new BiDi session,
                        while the tab order and URLs stay the same.
  open <url>            Open url in a NEW tab (window.open) in the
                        dedicated session; records it as current.
  open --live <url>     Open url in a new tab of his RUNNING Zen
                        (remoting). Opt-in only, see above.
  navigate <url> [--tab INDEX]
                        Navigate the current (or named) tab.
  activate <index>      Bring a tab to front; records it as current.
  close <index>         Close one tab by index. Never closes the
                        last remaining tab.
  current               Title and URL of the tracked current tab.
  page [--tab INDEX] [--text-chars N]
                        Title, URL and visible text of a tab.
  history [query] [--limit N]
                        Recent visits (or LIKE matches for query)
                        from the real profile, read-only.
  status                Session reachability plus profile and
                        history presence. Always exits 0.

Global flags: --port N (default from state file, else 9222),
--profile DIR (history profile; default auto-detected),
--json (accepted and ignored: output is always JSON, this flag exists
so the cli-anything runner's --json probe is satisfied).
Exit 0 on success, 1 on error, except session status / status which
always exit 0. No REPL mode, no shell, argv only.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import shutil
import signal
import fcntl
import socket
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

ZEN_BINARY = "zen-browser"
DEFAULT_PORT = 9222
LAST_PORT = 9231
DEFAULT_DEDICATED_PROFILE = Path.home() / ".cache" / "cli-anything-zen" / "profile"
REAL_PROFILE_HOME = Path.home() / ".config" / "zen"
STATE_PATH = (Path.home() / ".local" / "share" / "agent-computer-use"
              / "zen-cli-state.json")
SESSION_LOG = Path.home() / ".cache" / "cli-anything-zen" / "session.log"
# The single Zen remote-control slot, shared with zen_dom.ZenSession
# (same path, same env var). Firefox allows one remote session per
# instance; a BiDi session opened while a Marionette session holds the
# slot wedges ("Maximum number of active sessions"). Taking the lock
# here makes the two tools serialize instead of wedging.
ZEN_DOM_LOCK_PATH = Path(os.environ.get(
    "ZEN_DOM_LOCK",
    str(Path.home() / ".cache" / "agent-computer-use" / "zen_dom.lock")))
BIDI_TIMEOUT_SECONDS = 30
SESSION_START_TIMEOUT_SECONDS = 30
OPEN_POLL_SECONDS = 8
HTTP_TIMEOUT_SECONDS = 5
DEFAULT_LIMIT = 20
MAX_LIMIT = 200
DEFAULT_TEXT_CHARS = 2000
MAX_TEXT_CHARS = 10000
LOOPBACK_HOST = "127.0.0.1"


# ---------------------------------------------------------------------------
# Pill gate (R3, mirroring scripts/cdp.mjs): the computer-use pill must
# show whenever ANY agent controls the machine, whatever the method.
# Control commands (open, navigate, activate, close) acquire the central
# overlay pill (scripts/overlay.py) before the BiDi session starts and
# release it when the session ends; read-only commands (tabs, current,
# page, history, status) never acquire: reading is not control. The
# dedicated session itself also holds the pill for its whole lifetime:
# `session start` acquires keyed to the spawned Zen pid (the CLI process
# exits right after start, so its own pid would be pruned at once) and
# `session stop` releases it. Fail closed: when the pill cannot be
# raised, the drive is refused with 'BiDi pill unavailable' and no input
# runs. A spawn preflight checks overlay availability before `session
# start` spawns Zen, so a broken overlay fails before the spawn instead
# of surprising the first drive. The one opt-out is CU_ZEN_PILL=0,
# fixture tests only (no compositor there), never for live work.
# CU_OVERLAY_PY overrides the overlay.py path (test seam, same as
# cdp.mjs); CU_PILL_AGENT names the holder (default Muse).
# ---------------------------------------------------------------------------

class PillUnavailable(RuntimeError):
    """The overlay pill cannot be shown; the drive must be refused."""


def _pill_enabled():
    return os.environ.get("CU_ZEN_PILL", "1") != "0"


def _pill_agent():
    return os.environ.get("CU_PILL_AGENT") or "Muse"


def _overlay_py_path():
    override = os.environ.get("CU_OVERLAY_PY")
    if override:
        return override
    return str(Path(__file__).resolve().parent / "overlay.py")


def _run_overlay_cli(args, timeout_s=30):
    try:
        done = subprocess.run(
            [sys.executable, _overlay_py_path()] + args,
            capture_output=True, text=True, timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise PillUnavailable(
            "pill unavailable: overlay.py %s could not run: %s"
            % (args[0], exc))
    if done.returncode != 0:
        raise PillUnavailable(
            "pill unavailable: overlay.py %s failed: %s" % (
                args[0], (done.stderr or done.stdout).strip()[:300]))
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise PillUnavailable(
            "pill unavailable: overlay.py %s returned non-JSON output"
            % args[0])


def _pill_preflight():
    """Fail before any spawn when the overlay cannot be reached."""
    path = _overlay_py_path()
    if not Path(path).is_file():
        raise PillUnavailable(
            "pill unavailable: overlay.py not found at %s "
            "(set CU_OVERLAY_PY)" % path)
    _run_overlay_cli(["status"], timeout_s=10)


def _pill_acquire(pid):
    reply = _run_overlay_cli(
        ["acquire", "--agent", _pill_agent(), "--method", "BiDi",
         "--pid", str(pid)], timeout_s=60)
    if not isinstance(reply, dict) or reply.get("visible") is not True:
        raise PillUnavailable(
            "pill unavailable: pill not visible: %s" % (str(reply)[:300],))


def _pill_release(pid):
    try:
        _run_overlay_cli(
            ["release", "--agent", _pill_agent(), "--method", "BiDi",
             "--pid", str(pid)], timeout_s=10)
    except Exception as exc:
        print("BiDi pill release failed: %s" % exc, file=sys.stderr)


def validate_url(raw):
    """Only http/https URLs may be opened or navigated to."""
    url = urllib.parse.urlparse(raw)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("open needs an http(s) URL: " + raw)
    if len(raw) > 2048:
        raise ValueError("URL is longer than 2048 characters")
    return raw


def validate_port(raw):
    """A TCP port number, 1..65535."""
    try:
        port = int(raw)
    except (TypeError, ValueError):
        raise ValueError("port is not a number: " + str(raw)) from None
    if not 1 <= port <= 65535:
        raise ValueError("port out of range: " + str(raw))
    return port


def read_state():
    """Dedicated-session state, or None when nothing was recorded."""
    try:
        data = json.loads(STATE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not data.get("port"):
        return None
    return data


def write_state(payload):
    """Record dedicated-session state; private file, private dir."""
    STATE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = dict(payload)
    payload["updated_unix"] = int(datetime.datetime.now(
        tz=datetime.timezone.utc).timestamp())
    fd = os.open(STATE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(payload, handle)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def clear_state():
    """Drop the state file; best effort."""
    try:
        STATE_PATH.unlink()
    except OSError:
        pass


def resolve_port(args):
    """--port flag, else the state file port, else the default."""
    if getattr(args, "port", None) is not None:
        return args.port
    state = read_state()
    if state:
        try:
            return int(state["port"])
        except (TypeError, ValueError):
            pass
    return DEFAULT_PORT


def ws_url(port):
    """BiDi WebSocket URL for a remote-debugging port (path /session)."""
    return "ws://%s:%d/session" % (LOOPBACK_HOST, port)


def detect_real_profile():
    """the owner's real Zen profile dir, or None.

    Reads ~/.config/zen/profiles.ini. The Install sections name the
    default profile path; a Profile section may also carry Default=1.
    On the reference laptop the two disagree: the Install default
    points at one profile dir (the one with places.sqlite), while a
    second profile carries Default=1 and has no places.sqlite. So a
    candidate only counts when its dir exists, and a dir with
    places.sqlite beats one without. Never writes anything.
    """
    ini = REAL_PROFILE_HOME / "profiles.ini"
    try:
        text = ini.read_text()
    except OSError:
        text = ""
    sections = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current = {"_name": line[1:-1]}
            sections.append(current)
            continue
        if current is not None and "=" in line:
            key, _, value = line.partition("=")
            current[key.strip()] = value.strip()
    ordered = []
    for section in sections:
        if section["_name"].startswith("Install"):
            default = section.get("Default")
            if default:
                ordered.append(REAL_PROFILE_HOME / default)
    for section in sections:
        if section["_name"].startswith("Profile") \
                and section.get("Default") == "1":
            path = section.get("Path")
            if path:
                ordered.append(REAL_PROFILE_HOME / path)
    for section in sections:
        if section["_name"].startswith("Profile"):
            path = section.get("Path")
            if path:
                ordered.append(REAL_PROFILE_HOME / path)
    try:
        children = list(REAL_PROFILE_HOME.iterdir())
    except OSError:
        children = []
    with_history = [c for c in children
                    if c.is_dir() and (c / "places.sqlite").is_file()]
    with_history.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    ordered.extend(with_history)
    for candidate in ordered:
        if candidate.is_dir() and (candidate / "places.sqlite").is_file():
            return candidate
    for candidate in ordered:
        if candidate.is_dir():
            return candidate
    return None


def resolve_history_profile(flag):
    """--profile flag, else the auto-detected real profile."""
    if flag:
        profile = Path(flag)
        if not profile.is_dir():
            raise RuntimeError("profile is not a directory: " + flag)
        return profile
    profile = detect_real_profile()
    if profile is None:
        raise RuntimeError("no Zen profile found under " + str(REAL_PROFILE_HOME))
    return profile


def copy_db_readonly(path):
    """Copy a live sqlite file to a temp file; returns the temp path."""
    fd, tmp = tempfile.mkstemp(prefix="zen-cli-", suffix=".sqlite")
    os.close(fd)
    shutil.copyfile(path, tmp)
    return tmp


def firefox_time_to_iso(value):
    """PRTime (microseconds since 1970-01-01) to ISO 8601 UTC."""
    try:
        micros = int(value)
    except (TypeError, ValueError):
        return None
    if micros <= 0:
        return None
    base = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    try:
        return (base + datetime.timedelta(microseconds=micros)).isoformat()
    except OverflowError:
        return None


# ---------------------------------------------------------------------------
# Minimal WebSocket client (stdlib only). The BiDi server speaks plain
# ws:// on loopback; client frames must be masked, server frames are not.
# Handles text, continuation, ping (answers pong), pong and close frames,
# and 16-bit / 64-bit payload lengths for large script.evaluate results.
# ---------------------------------------------------------------------------

def _read_exact(reader, count):
    """Read exactly count bytes from a buffered reader."""
    data = reader.read(count)
    if data is None or len(data) < count:
        raise RuntimeError("WebSocket closed while reading a frame")
    return data


class WebSocketClient:
    """One WebSocket connection; send_text / recv_message only."""

    def __init__(self, host, port, path, timeout=BIDI_TIMEOUT_SECONDS):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.reader = self.sock.makefile("rb")
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            "GET %s HTTP/1.1\r\n"
            "Host: %s:%d\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n" % (path, host, port, key))
        self.sock.sendall(request.encode("ascii"))
        status = self.reader.readline().decode("latin-1").strip()
        if " 101 " not in status:
            raise RuntimeError("WebSocket upgrade failed: " + status)
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
        ).digest()).decode("ascii")
        accept = None
        while True:
            line = self.reader.readline().decode("latin-1")
            if line in ("\r\n", "\n", ""):
                break
            if line.lower().startswith("sec-websocket-accept:"):
                accept = line.split(":", 1)[1].strip()
        if accept != expected:
            raise RuntimeError("WebSocket accept key mismatch")

    def _send_frame(self, opcode, payload):
        """One masked client frame."""
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack(">H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack(">Q", length))
        mask = os.urandom(4)
        header.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def send_text(self, text):
        """Send one text message."""
        self._send_frame(0x1, text.encode("utf-8"))

    def close(self):
        """Best-effort close frame, then close the socket."""
        try:
            self._send_frame(0x8, b"")
        except OSError:
            pass
        try:
            self.reader.close()
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


def bidi_recv_message(client):
    """Read frames until a whole text message arrives (FIN aware).

    WebSocketClient._recv_frame hides the FIN bit, so this helper
    re-implements the read loop on the same reader/socket pair.
    """
    parts = []
    while True:
        first = _read_exact(client.reader, 2)
        fin = bool(first[0] & 0x80)
        opcode = first[0] & 0x0F
        masked = first[1] & 0x80
        length = first[1] & 0x7F
        if length == 126:
            length = struct.unpack(">H", _read_exact(client.reader, 2))[0]
        elif length == 127:
            length = struct.unpack(">Q", _read_exact(client.reader, 8))[0]
        mask = _read_exact(client.reader, 4) if masked else None
        payload = _read_exact(client.reader, length) if length else b""
        if mask is not None:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        if opcode == 0x9:
            client._send_frame(0xA, payload)
            continue
        if opcode == 0x8:
            raise RuntimeError("WebSocket closed by the server")
        if opcode in (0x1, 0x0):
            parts.append(payload)
            if fin:
                return b"".join(parts).decode("utf-8")
            continue
        raise RuntimeError("unexpected WebSocket opcode: %d" % opcode)


class BidiSession:
    """One BiDi session over ws://127.0.0.1:<port>/session.

    Takes the single-session ZEN_DOM_LOCK on construction (the same
    lock zen_dom.ZenSession takes): Firefox allows one remote session
    per Zen instance, so a BiDi session opened while a Marionette
    session holds the slot wedges. The lock is released in end(),
    which never raises; a session that never ends keeps the slot
    until the process exits.

    With pill=True (control commands only), start() acquires the
    overlay pill before session.new and end() releases it; a pill
    that cannot be shown refuses the session (PillUnavailable).
    Probes and read-only commands keep pill=False.
    """

    def __init__(self, port, timeout=BIDI_TIMEOUT_SECONDS, pill=False):
        self.port = port
        self.timeout = timeout
        self._pill = pill
        self._pill_held = False
        ZEN_DOM_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = open(ZEN_DOM_LOCK_PATH, "w")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            raise RuntimeError(
                "another process already holds the Zen remote session "
                "(ZEN_DOM_LOCK); only one remote session is allowed per "
                "Zen instance, so this BiDi session refuses instead of "
                "wedging the slot")
        self.client = WebSocketClient(LOOPBACK_HOST, port, "/session",
                                      timeout=timeout)
        self.next_id = 0
        self.session_id = None

    def call(self, method, params=None):
        """Send one command, wait for its reply (events ignored)."""
        self.next_id += 1
        call_id = self.next_id
        payload = {"id": call_id, "method": method,
                   "params": params or {}}
        self.client.send_text(json.dumps(payload))
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("BiDi call timed out: " + method)
            self.client.sock.settimeout(remaining)
            raw = bidi_recv_message(self.client)
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if message.get("id") != call_id:
                continue  # event or a reply to another call
            if message.get("type") == "error":
                error = message.get("error", "unknown error")
                detail = message.get("message", "")
                raise RuntimeError("BiDi %s failed: %s %s" % (
                    method, error, detail))
            return message.get("result", {})

    def start(self):
        """session.new; records the session id and browser details.

        With pill=True the overlay pill is acquired first (preflight,
        then acquire); when it cannot be shown the session is refused
        before session.new, so no control runs invisibly.
        """
        if self._pill and _pill_enabled():
            try:
                _pill_preflight()
                _pill_acquire(os.getpid())
            except PillUnavailable:
                self.end()
                raise
            self._pill_held = True
        try:
            result = self.call("session.new", {"capabilities": {}})
        except BaseException:
            self.end()
            raise
        self.session_id = result.get("sessionId")
        return result

    def end(self):
        """session.end, then close the socket, then release the slot
        lock and the pill (when held). Never raises."""
        try:
            self.call("session.end", {})
        except (RuntimeError, OSError):
            pass
        try:
            self.client.close()
        except OSError:
            pass
        lock_file = getattr(self, "_lock_file", None)
        if lock_file is not None:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_UN)
                lock_file.close()
            except Exception:
                pass
            self._lock_file = None
        if getattr(self, "_pill_held", False):
            self._pill_held = False
            _pill_release(os.getpid())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.end()
        return False


def bidi_probe(port, timeout=10):
    """True when a BiDi session can be opened on the port."""
    try:
        with BidiSession(port, timeout=timeout):
            return True
    except (RuntimeError, OSError):
        return False


def bidi_session_info(port, timeout=10):
    """session.new result for the instance on the port, or None."""
    try:
        session = BidiSession(port, timeout=timeout)
        try:
            return session.start()
        finally:
            session.end()
    except (RuntimeError, OSError):
        return None


# ---------------------------------------------------------------------------
# BiDi tab helpers. getTree has URL and context id but no title, so titles
# come from one script.evaluate per tab (best effort: "" on failure).
# ---------------------------------------------------------------------------

def list_contexts(session):
    """Top-level browsing contexts from getTree, in tree order."""
    result = session.call("browsingContext.getTree", {})
    contexts = result.get("contexts", [])
    if not isinstance(contexts, list):
        raise RuntimeError("browsingContext.getTree returned no contexts")
    return [c for c in contexts if isinstance(c, dict)
            and c.get("parent") is None]


def evaluate(session, context, expression):
    """script.evaluate in one context; returns the BiDi result object."""
    result = session.call("script.evaluate", {
        "expression": expression,
        "target": {"context": context},
        "awaitPromise": False})
    if result.get("type") != "success":
        raise RuntimeError("script.evaluate failed in tab %s" % context)
    return result.get("result", {})


def bidi_string(result):
    """The string value of a BiDi string result, else None."""
    if isinstance(result, dict) and result.get("type") == "string":
        return result.get("value")
    return None


def tab_title(session, context):
    """document.title of one tab; "" when it cannot be read."""
    try:
        return bidi_string(evaluate(session, context, "document.title")) or ""
    except (RuntimeError, OSError):
        return ""


def tab_info(session, context):
    """One tab by its (this-session-only) context id: index, url, title.

    The index is the tab's position in getTree order, which is stable
    across BiDi sessions; the context id is not (see list_tabs).
    """
    entries = list_contexts(session)
    for index, entry in enumerate(entries):
        if entry.get("context") == context:
            return {"index": index, "url": entry.get("url", ""),
                    "title": tab_title(session, context)}
    raise RuntimeError("no such tab: " + context)


def list_tabs(session):
    """All top-level tabs with index, url and title.

    Tabs are addressed by INDEX (position in getTree order), not by
    BiDi context id. Verified 2026-11-18 on Zen 1.24.2b: context ids
    (and clientWindow ids) change on every new BiDi session, while the
    tab order and URLs stay the same, so a context id from one
    invocation is stale in the next. Every command resolves its index
    to a fresh context id inside its own BiDi session.
    """
    tabs = []
    for index, entry in enumerate(list_contexts(session)):
        context = entry.get("context", "")
        tabs.append({"index": index, "url": entry.get("url", ""),
                     "title": tab_title(session, context)})
    return tabs


def parse_tab_index(raw):
    """A --tab / positional tab argument must be an integer index."""
    try:
        index = int(raw)
    except (TypeError, ValueError):
        raise ValueError(
            "tab must be an index from `tabs` (0, 1, 2, ...), not a "
            "BiDi context id: %r" % (raw,)) from None
    if index < 0:
        raise ValueError("tab index must be 0 or more: %r" % (raw,))
    return index


def resolve_tab(session, index):
    """(entry, context id) for an index; raises when out of range."""
    entries = list_contexts(session)
    if not 0 <= index < len(entries):
        raise RuntimeError(
            "no tab %d: the dedicated session has %d tab(s); run "
            "`tabs` first" % (index, len(entries)))
    return entries[index], entries[index].get("context", "")


def track_current(tab):
    """Record a tab as current in the state file (keeps port/profile).

    Tracks index + URL, never the BiDi context id: the id is stale in
    the next invocation, the index and URL are not.
    """
    state = read_state() or {}
    state["tab_index"] = tab.get("index")
    state["tab_title"] = tab.get("title", "")
    state["tab_url"] = tab.get("url", "")
    write_state(state)


def tracked_ref():
    """The (index, url) recorded as current, or None."""
    state = read_state()
    if not state:
        return None
    index = state.get("tab_index")
    url = state.get("tab_url", "")
    if isinstance(index, int) and url:
        return index, url
    return None


def resolve_tracked(session):
    """The tracked tab (index, url), verified against a fresh listing.

    Prefers the tracked index when that position still holds the
    tracked URL; falls back to the first tab with the tracked URL,
    then to the first non-blank tab, then to the first tab. Returns
    None when the session has no tabs.
    """
    tabs = list_tabs(session)
    if not tabs:
        return None
    ref = tracked_ref()
    if ref is not None:
        index, url = ref
        if 0 <= index < len(tabs) and tabs[index]["url"] == url:
            return tabs[index]
        for tab in tabs:
            if tab["url"] == url:
                return tab
    for tab in tabs:
        if tab["url"] and tab["url"] != "about:blank":
            return tab
    return tabs[0]


def open_session(port, pill=False):
    """A BiDi session on the dedicated port, or a clear error.

    PillUnavailable is re-raised unwrapped: a refused pill is not a
    missing session, and wrapping it would hide the real cause.
    """
    try:
        session = BidiSession(port, pill=pill)
        session.start()
        return session
    except PillUnavailable:
        raise
    except (RuntimeError, OSError) as exc:
        raise RuntimeError(
            "no dedicated Zen session on port %d: %s; run "
            "`session start` first" % (port, exc)) from exc


def bidi_browser_name_version(info):
    """(browserName, browserVersion) from a session.new result.

    Both live inside the "capabilities" object, not at the top level.
    """
    caps = info.get("capabilities", {}) if isinstance(info, dict) else {}
    if not isinstance(caps, dict):
        caps = {}
    return caps.get("browserName", ""), caps.get("browserVersion", "")


def bidi_session_profile(info):
    """The moz:profile of a session.new result (inside capabilities)."""
    caps = info.get("capabilities", {}) if isinstance(info, dict) else {}
    if not isinstance(caps, dict):
        return ""
    return caps.get("moz:profile", "")


def port_is_listening(port):
    """True when something accepts TCP on 127.0.0.1:port."""
    try:
        with socket.create_connection((LOOPBACK_HOST, port), timeout=2):
            return True
    except OSError:
        return False


def find_free_port(start):
    """First port in start..LAST_PORT with nothing listening, else None."""
    for port in range(start, LAST_PORT + 1):
        if not port_is_listening(port):
            return port
    return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_session_start(args):
    if shutil.which(ZEN_BINARY) is None:
        raise RuntimeError("zen-browser is not on PATH")
    profile = Path(args.profile) if args.profile else DEFAULT_DEDICATED_PROFILE
    resolved = profile.expanduser().resolve()
    real_home = REAL_PROFILE_HOME.expanduser().resolve()
    if resolved == real_home or real_home in resolved.parents:
        raise RuntimeError(
            "refusing profile inside ~/.config/zen (his real profiles): "
            + str(profile))
    if _pill_enabled():
        _pill_preflight()
    requested = args.port if args.port is not None else DEFAULT_PORT
    state = read_state()
    if state and state.get("port") == requested:
        info = bidi_session_info(requested, timeout=10)
        if info is not None and bidi_session_profile(info) == str(resolved):
            if _pill_enabled():
                pid = state.get("pid")
                if not isinstance(pid, int):
                    raise PillUnavailable(
                        "pill unavailable: recorded session has no pid "
                        "to hold the pill; run `session stop` then "
                        "`session start`")
                _pill_acquire(pid)
            return {"ok": True, "command": "session start",
                    "reused": True, "port": requested,
                    "profile": str(resolved), "pid": state.get("pid"),
                    "ws_url": ws_url(requested),
                    "browser": bidi_browser_name_version(info)[0],
                    "browser_version": bidi_browser_name_version(info)[1]}
    port = find_free_port(requested)
    if port is None:
        raise RuntimeError(
            "no free BiDi port in %d..%d" % (requested, LAST_PORT))
    profile.mkdir(parents=True, exist_ok=True)
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    command = [ZEN_BINARY]
    if not args.no_headless:
        command.append("--headless")
    command += ["--no-remote", "--profile", str(profile),
                "--remote-debugging-port=%d" % port, "about:blank"]
    log = open(SESSION_LOG, "ab")
    try:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
    finally:
        log.close()
    deadline = time.monotonic() + SESSION_START_TIMEOUT_SECONDS
    info = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                "dedicated Zen exited during start (code %s); see %s"
                % (proc.returncode, SESSION_LOG))
        info = bidi_session_info(port, timeout=5)
        if info is not None:
            break
        time.sleep(0.5)
    if info is None:
        raise RuntimeError(
            "dedicated Zen did not answer BiDi on port %d within %ds; "
            "see %s" % (port, SESSION_START_TIMEOUT_SECONDS, SESSION_LOG))
    if _pill_enabled():
        try:
            _pill_acquire(proc.pid)
        except PillUnavailable:
            # Fail closed: never leave a controllable Zen running
            # without the pill up.
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            raise
    write_state({"port": port, "profile": str(profile), "pid": proc.pid,
                 "ws_url": ws_url(port), "headless": not args.no_headless})
    return {"ok": True, "command": "session start", "reused": False,
            "port": port, "profile": str(profile), "pid": proc.pid,
            "ws_url": ws_url(port),
            "browser": bidi_browser_name_version(info)[0],
            "browser_version": bidi_browser_name_version(info)[1]}


def cmd_session_stop(args):
    state = read_state()
    if state is None:
        return {"ok": True, "command": "session stop", "running": False,
                "note": "no dedicated session recorded"}
    pid = state.get("pid")
    profile = state.get("profile", "")
    if not isinstance(pid, int):
        clear_state()
        return {"ok": True, "command": "session stop", "running": False,
                "note": "recorded state had no pid; state cleared"}
    try:
        cmdline = Path("/proc/%d/cmdline" % pid).read_bytes()
    except OSError:
        if _pill_enabled():
            _pill_release(pid)
        clear_state()
        return {"ok": True, "command": "session stop", "running": False,
                "note": "recorded pid %d is not running; state cleared" % pid}
    text = cmdline.decode("utf-8", errors="replace")
    if "zen" not in text or profile not in text:
        raise RuntimeError(
            "refusing to kill pid %d: its cmdline does not contain the "
            "recorded dedicated profile %s" % (pid, profile))
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        raise RuntimeError("failed to stop pid %d: %s" % (pid, exc)) from exc
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(0.2)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    if _pill_enabled():
        _pill_release(pid)
    clear_state()
    return {"ok": True, "command": "session stop", "running": False,
            "pid": pid, "profile": profile}


def cmd_session_status(args):
    state = read_state()
    port = resolve_port(args)
    listening = port_is_listening(port)
    info = bidi_session_info(port, timeout=10) if listening else None
    result = {"ok": True, "command": "session status", "port": port,
              "listening": listening, "session_up": info is not None,
              "state_file": str(STATE_PATH),
              "state_recorded": state is not None}
    if state:
        result["profile"] = state.get("profile", "")
        result["pid"] = state.get("pid")
        result["headless"] = state.get("headless")
    if info is not None:
        result["browser"], result["browser_version"] = \
            bidi_browser_name_version(info)
        result["session_profile"] = bidi_session_profile(info)
    return result


def cmd_tabs(args):
    port = resolve_port(args)
    session = open_session(port)
    try:
        tabs = list_tabs(session)
    finally:
        session.end()
    return {"ok": True, "command": "tabs", "port": port, "tabs": tabs}


def cmd_open(args):
    url = validate_url(args.url)
    if args.live:
        if shutil.which(ZEN_BINARY) is None:
            raise RuntimeError("zen-browser is not on PATH")
        try:
            result = subprocess.run(
                [ZEN_BINARY, "--new-tab", url],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=15)
        except subprocess.TimeoutExpired:
            raise RuntimeError("zen-browser --new-tab timed out") from None
        if result.returncode != 0:
            raise RuntimeError("zen-browser --new-tab failed: %s" %
                               result.stderr.strip())
        return {"ok": True, "command": "open", "live": True, "url": url,
                "note": "opened in a new tab of his RUNNING Zen via "
                        "remoting; the tab was not read back (no debug "
                        "port on his session)"}
    port = resolve_port(args)
    session = open_session(port, pill=True)
    try:
        if args.tab is not None:
            opener_index = parse_tab_index(args.tab)
        else:
            tracked = resolve_tracked(session)
            opener_index = tracked["index"] if tracked is not None else 0
        opener_entry, opener = resolve_tab(session, opener_index)
        evaluate(session, opener,
                 "window.open(%s, '_blank')" % json.dumps(url))
        deadline = time.monotonic() + OPEN_POLL_SECONDS
        new_tab = None
        while time.monotonic() < deadline:
            time.sleep(0.5)
            for index, entry in enumerate(list_contexts(session)):
                if entry.get("originalOpener") == opener:
                    new_tab = {"index": index,
                               "url": entry.get("url", ""),
                               "title": tab_title(
                                   session, entry.get("context", ""))}
                    break
            if new_tab is not None:
                break
        if new_tab is None:
            raise RuntimeError(
                "window.open did not produce a new tab within %ds; the "
                "opener tab was not navigated" % OPEN_POLL_SECONDS)
        track_current(new_tab)
        return {"ok": True, "command": "open", "live": False, "port": port,
                "tab": new_tab}
    finally:
        session.end()


def cmd_navigate(args):
    url = validate_url(args.url)
    port = resolve_port(args)
    session = open_session(port, pill=True)
    try:
        if args.tab is not None:
            index = parse_tab_index(args.tab)
        else:
            tracked = resolve_tracked(session)
            index = tracked["index"] if tracked is not None else 0
        _, context = resolve_tab(session, index)
        result = session.call("browsingContext.navigate", {
            "context": context, "url": url, "wait": "complete"})
        tab = tab_info(session, context)
        track_current(tab)
        return {"ok": True, "command": "navigate", "port": port,
                "navigation": result.get("navigation", ""), "tab": tab}
    finally:
        session.end()


def cmd_activate(args):
    index = parse_tab_index(args.index)
    port = resolve_port(args)
    session = open_session(port, pill=True)
    try:
        _, context = resolve_tab(session, index)
        session.call("browsingContext.activate", {"context": context})
        tab = tab_info(session, context)
        track_current(tab)
        return {"ok": True, "command": "activate", "port": port, "tab": tab}
    finally:
        session.end()


def cmd_close(args):
    index = parse_tab_index(args.index)
    port = resolve_port(args)
    session = open_session(port, pill=True)
    try:
        entries = list_contexts(session)
        if not 0 <= index < len(entries):
            raise RuntimeError(
                "no tab %d: the dedicated session has %d tab(s); run "
                "`tabs` first" % (index, len(entries)))
        if len(entries) <= 1:
            raise RuntimeError(
                "refusing to close the last remaining tab of the "
                "dedicated session; use session stop instead")
        context = entries[index].get("context", "")
        session.call("browsingContext.close", {"context": context})
        state = read_state()
        if state and state.get("tab_index") == index:
            state.pop("tab_index", None)
            state.pop("tab_title", None)
            state.pop("tab_url", None)
            write_state(state)
        return {"ok": True, "command": "close", "port": port,
                "index": index}
    finally:
        session.end()


def cmd_current(args):
    port = resolve_port(args)
    session = open_session(port)
    try:
        tab = resolve_tracked(session)
        if tab is None:
            raise RuntimeError("dedicated session has no tabs")
        ref = tracked_ref()
        tracked = ref is not None and tab["url"] == ref[1]
        result = {"ok": True, "command": "current", "port": port,
                  "tab": tab, "tracked": tracked}
        if not tracked:
            result["note"] = ("no tab tracked yet; showing the first "
                              "live tab")
        return result
    finally:
        session.end()


def cmd_page(args):
    port = resolve_port(args)
    session = open_session(port)
    try:
        if args.tab is not None:
            index = parse_tab_index(args.tab)
        else:
            tracked = resolve_tracked(session)
            index = tracked["index"] if tracked is not None else 0
        _, context = resolve_tab(session, index)
        result = evaluate(
            session, context,
            "({title: document.title, url: location.href, "
            "text: document.body ? document.body.innerText : ''})")
        if not isinstance(result, dict) or result.get("type") != "object":
            raise RuntimeError("page read returned an unexpected shape")
        fields = {}
        for key, value in result.get("value", []):
            if isinstance(value, dict) and value.get("type") == "string":
                fields[key] = value.get("value", "")
        text = fields.get("text", "")
        limit = args.text_chars
        if len(text) > limit:
            text = text[:limit]
        return {"ok": True, "command": "page", "port": port,
                "index": index, "title": fields.get("title", ""),
                "url": fields.get("url", ""), "text": text,
                "text_truncated": len(fields.get("text", "")) > limit}
    finally:
        session.end()


def query_history_db(db_path, query, limit):
    """Recent visits (or LIKE matches) from a places.sqlite copy."""
    tmp = copy_db_readonly(db_path)
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % tmp, uri=True)
        try:
            sql = ("SELECT p.url, p.title, p.visit_count,"
                   " MAX(v.visit_date) FROM moz_places p"
                   " JOIN moz_historyvisits v ON v.place_id = p.id")
            params = []
            if query:
                sql += " WHERE p.url LIKE ? OR p.title LIKE ?"
                params = ["%" + query + "%", "%" + query + "%"]
            sql += (" GROUP BY p.id ORDER BY MAX(v.visit_date)"
                    " DESC LIMIT ?")
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
        finally:
            conn.close()
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    visits = []
    for url, title, visit_count, last_visit in rows:
        visits.append({"url": url or "", "title": title or "",
                       "visit_count": visit_count or 0,
                       "last_visit": firefox_time_to_iso(last_visit)})
    return visits


def cmd_history(args):
    profile = resolve_history_profile(args.profile)
    db_path = profile / "places.sqlite"
    if not db_path.is_file():
        raise RuntimeError("no places.sqlite in profile: " + str(profile))
    visits = query_history_db(db_path, args.query or None, args.limit)
    return {"ok": True, "command": "history", "profile": str(profile),
            "history_file": str(db_path), "query": args.query or "",
            "visits": visits}


def cmd_status(args):
    profile = None
    history_exists = False
    try:
        profile = resolve_history_profile(args.profile)
        history_exists = (profile / "places.sqlite").is_file()
    except RuntimeError:
        profile = None
    session_state = cmd_session_status(args)
    return {"ok": True, "command": "status",
            "port": session_state["port"],
            "session_up": session_state["session_up"],
            "browser": session_state.get("browser", ""),
            "browser_version": session_state.get("browser_version", ""),
            "session_profile": session_state.get("session_profile", ""),
            "profile": str(profile) if profile else "",
            "profile_exists": profile is not None,
            "history_exists": history_exists}


COMMANDS = {
    "tabs": (cmd_tabs, "list tabs of the dedicated session"),
    "open": (cmd_open, "open a URL in a new tab"),
    "navigate": (cmd_navigate, "navigate the current (or named) tab"),
    "activate": (cmd_activate, "bring a tab to front"),
    "close": (cmd_close, "close one tab by index"),
    "current": (cmd_current, "title and URL of the tracked current tab"),
    "page": (cmd_page, "title, URL and visible text of a tab"),
    "history": (cmd_history, "recent visits / search from the profile"),
    "status": (cmd_status, "session and profile reachability probe"),
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Zen Browser CLI wrapper over loopback WebDriver BiDi.")
    parser.add_argument("--port", type=validate_port, default=None,
                        help="dedicated BiDi port (default: state file, "
                             "else 9222)")
    parser.add_argument("--profile", default=None,
                        help="Zen profile dir for history (default: "
                             "auto-detected real profile)")
    parser.add_argument("--json", action="store_true",
                        help="accepted and ignored: output is always JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    session_parser = sub.add_parser("session",
                                    help="manage the dedicated session")
    session_sub = session_parser.add_subparsers(dest="session_command",
                                                required=True)
    start_parser = session_sub.add_parser(
        "start", help="start the dedicated BiDi session")
    start_parser.add_argument("--port", type=validate_port, default=None,
                              help="BiDi port to use (default 9222, tries "
                                   "up to 9231 if busy)")
    start_parser.add_argument("--profile", default=None,
                              help="dedicated profile dir (default "
                                   "~/.cache/cli-anything-zen/profile)")
    start_parser.add_argument("--no-headless", action="store_true",
                              help="show a window instead of headless")
    session_sub.add_parser("stop", help="stop the dedicated session")
    session_sub.add_parser("status", help="dedicated session probe")
    sub.add_parser("tabs", help=COMMANDS["tabs"][1])
    open_parser = sub.add_parser("open", help=COMMANDS["open"][1])
    open_parser.add_argument("url")
    open_parser.add_argument("--live", action="store_true",
                             help="open in his RUNNING Zen via remoting "
                                  "(opt-in only)")
    open_parser.add_argument("--tab", default=None,
                             help="opener tab index from `tabs` (default: "
                                  "tracked current, else first tab)")
    navigate_parser = sub.add_parser("navigate", help=COMMANDS["navigate"][1])
    navigate_parser.add_argument("url")
    navigate_parser.add_argument("--tab", default=None,
                                 help="tab index from `tabs` (default: "
                                      "tracked current, else first tab)")
    activate_parser = sub.add_parser("activate", help=COMMANDS["activate"][1])
    activate_parser.add_argument("index", help="tab index from `tabs`")
    close_parser = sub.add_parser("close", help=COMMANDS["close"][1])
    close_parser.add_argument("index", help="tab index from `tabs`")
    sub.add_parser("current", help=COMMANDS["current"][1])
    page_parser = sub.add_parser("page", help=COMMANDS["page"][1])
    page_parser.add_argument("--tab", default=None,
                             help="tab index from `tabs` (default: tracked "
                                  "current, else first tab)")
    page_parser.add_argument("--text-chars", type=int,
                             default=DEFAULT_TEXT_CHARS,
                             help="visible-text cap (default 2000, "
                                  "max 10000)")
    history_parser = sub.add_parser("history", help=COMMANDS["history"][1])
    history_parser.add_argument("query", nargs="?", default=None,
                                help="substring to match in URL or title")
    history_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    sub.add_parser("status", help=COMMANDS["status"][1])
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command
    try:
        if command == "session":
            if args.session_command == "start":
                result = cmd_session_start(args)
            elif args.session_command == "stop":
                result = cmd_session_stop(args)
            else:
                result = cmd_session_status(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0
        if command in ("session status", "status"):
            result = cmd_status(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0
        limit = getattr(args, "limit", DEFAULT_LIMIT)
        if not 1 <= limit <= MAX_LIMIT:
            raise ValueError("limit must be 1..%d" % MAX_LIMIT)
        text_chars = getattr(args, "text_chars", DEFAULT_TEXT_CHARS)
        if not 0 <= text_chars <= MAX_TEXT_CHARS:
            raise ValueError("text-chars must be 0..%d" % MAX_TEXT_CHARS)
        handler = COMMANDS[command][0]
        result = handler(args)
    except (ValueError, RuntimeError, OSError) as exc:
        print(json.dumps({"ok": False, "command": command,
                          "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

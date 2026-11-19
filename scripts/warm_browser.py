#!/usr/bin/env python3
"""Warm Chromium manager (H3 prototype). Stdlib only.

Keeps one agent-managed Chromium process warm across tasks instead of
launching it fresh per task, and creates a FRESH browser context per
task inside the warm process, so the process stays warm but the state
(cookies, localStorage, cache) is isolated.

Rules this module enforces:
  * Loopback CDP endpoint only; anything else is refused.
  * Only the Chromium this module launched (recorded pid, verified
    against /proc/<pid>/cmdline containing our profile path) is ever
    terminated. A reused endpoint owned by someone else is never
    killed, and neither is the user's Zen browser (a different binary
    and profile; this module only ever launches `chromium` with its
    own --user-data-dir).
  * A warm browser that is unhealthy falls back to a cold launch:
    ensure_warm() relaunches when the health check fails, and
    new_task_context() retries once after a forced relaunch.
  * State lives in one JSON file (0600, atomic replace) under the
    agent state dir, so unit tests can redirect it with
    CU_WARM_BROWSER_STATE_DIR.

CLI (each command prints exactly one JSON object on stdout):
  ensure [--endpoint URL] [--profile DIR]
  health [--endpoint URL]
  status [--endpoint URL]
  new-context --task-id ID [--url URL] [--endpoint URL]
  close-context [--task-id ID | --target-id ID] [--endpoint URL]
  verify-isolation [--endpoint URL]
  stop
Exit 0 on success, 1 on error. No REPL mode, no shell, argv only.
"""

import argparse
import base64
import hashlib
import json
import os
import signal
import socket
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_ENDPOINT = "http://127.0.0.1:9222"
DEFAULT_STATE_DIR = Path.home() / ".local" / "share" / "agent-computer-use"
STATE_FILENAME = "warm-browser.json"
LOG_FILENAME = "warm-browser.log"
PROFILE_DIRNAME = "warm-browser-profile"
HTTP_TIMEOUT_SECONDS = 5
LAUNCH_POLL_SECONDS = 10
LOAD_TIMEOUT_SECONDS = 15
CDP_TIMEOUT_SECONDS = 10
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")

# Fixed isolation probe snippets. verify_isolation() writes a marker
# cookie plus a localStorage key in one context and reads both back in
# another; the marker value is derived from the task id so a leak is
# attributable.
ISOLATION_COOKIE_NAME = "warm-browser-probe"
ISOLATION_STORAGE_KEY = "warm-browser-probe"


class WarmBrowserError(RuntimeError):
    """Warm-browser failure; message is safe to show the operator."""


def _env_state_dir():
    override = os.environ.get("CU_WARM_BROWSER_STATE_DIR")
    return Path(override) if override else DEFAULT_STATE_DIR


def _env_endpoint():
    return os.environ.get("CU_WARM_BROWSER_ENDPOINT") or DEFAULT_ENDPOINT


def validate_endpoint(raw):
    """Loopback http endpoint only; anything else is refused."""
    url = urllib.parse.urlparse(raw)
    if url.scheme != "http" or url.hostname not in LOOPBACK_HOSTS:
        raise WarmBrowserError("CDP endpoint must be loopback http: " + raw)
    try:
        port = url.port or 80
    except ValueError:
        raise WarmBrowserError("endpoint port is not a number: " + raw) from None
    if not 1 <= port <= 65535:
        raise WarmBrowserError("endpoint port out of range: " + raw)
    return raw.rstrip("/")


def _http_json(endpoint, path, method="GET", timeout=HTTP_TIMEOUT_SECONDS):
    request = urllib.request.Request(endpoint + path, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise WarmBrowserError(
            "CDP %s %s: HTTP %s" % (method, path, exc.code)) from exc
    except urllib.error.URLError as exc:
        raise WarmBrowserError(
            "CDP %s %s unreachable: %s" % (method, path, exc.reason)) from exc
    except (UnicodeDecodeError, TimeoutError) as exc:
        raise WarmBrowserError(
            "CDP %s %s failed: %s" % (method, path, exc)) from exc
    if not text.strip():
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise WarmBrowserError(
            "CDP %s %s returned invalid JSON" % (method, path)) from exc


def health(endpoint):
    """Reachability probe. Never raises for an unreachable browser.

    Returns {'ok': bool, 'endpoint': str, 'version': str|None,
    'target_count': int|None, 'error': str|None}.
    """
    endpoint = validate_endpoint(endpoint)
    try:
        version = _http_json(endpoint, "/json/version", timeout=2)
        tabs = _http_json(endpoint, "/json/list", timeout=2)
    except WarmBrowserError as exc:
        return {"ok": False, "endpoint": endpoint, "version": None,
                "target_count": None, "error": str(exc)}
    pages = [t for t in tabs if isinstance(t, dict) and t.get("type") == "page"]
    return {"ok": True, "endpoint": endpoint,
            "version": version.get("Browser") if isinstance(version, dict) else None,
            "target_count": len(pages), "error": None}


def _state_path(state_dir):
    return Path(state_dir) / STATE_FILENAME


def _read_state(state_dir):
    path = _state_path(state_dir)
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_state(state_dir, data):
    path = _state_path(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + ".tmp.%d" % os.getpid())
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _pid_cmdline(pid):
    """Command line of a pid, or None when it cannot be read."""
    try:
        raw = Path("/proc/%d/cmdline" % pid).read_bytes()
    except OSError:
        return None
    return raw.replace(b"\x00", b" ").decode("utf-8", "replace").strip()


def _pid_is_ours(pid, profile):
    """True only when pid is a live Chromium running with our profile."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    cmdline = _pid_cmdline(pid)
    if cmdline is None:
        return False
    return "chromium" in cmdline and str(profile) in cmdline


def _launch_chromium(endpoint, profile, state_dir, env=None):
    """Cold launch. Returns (pid, launch_ms). Raises on failure.

    CU_WARM_BROWSER_HEADLESS=1 adds --headless=new: the warm process
    never opens a window on the user's desktop, which is what the
    prototype probe uses. The headed default matches browser_start.
    """
    url = urllib.parse.urlparse(endpoint)
    port = url.port or 9222
    profile = Path(profile)
    profile.mkdir(parents=True, exist_ok=True, mode=0o700)
    log_path = Path(state_dir) / LOG_FILENAME
    log_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    start = time.monotonic()
    args = ["chromium", "--user-data-dir=%s" % profile,
            "--remote-debugging-port=%d" % port,
            "--remote-debugging-address=127.0.0.1",
            "--no-first-run", "--no-default-browser-check"]
    if (env or os.environ).get("CU_WARM_BROWSER_HEADLESS") == "1":
        args.append("--headless=new")
    args.append("about:blank")
    try:
        log = os.fdopen(fd, "ab")
        try:
            proc = subprocess.Popen(
                args, env=env, stdin=subprocess.DEVNULL, stdout=log,
                stderr=log, start_new_session=True)
        finally:
            log.close()
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    deadline = start + LAUNCH_POLL_SECONDS
    try:
        while True:
            if health(endpoint)["ok"]:
                return proc.pid, round((time.monotonic() - start) * 1000, 1)
            if time.monotonic() >= deadline:
                raise WarmBrowserError(
                    "managed browser did not expose CDP in %ss; see %s"
                    % (LAUNCH_POLL_SECONDS, log_path))
            time.sleep(0.1)
    except BaseException:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except BaseException:
            try:
                proc.kill()
                proc.wait(timeout=3)
            except BaseException:
                pass
        raise


def ensure_warm(endpoint=None, profile=None, state_dir=None, env=None):
    """Return a healthy warm browser, cold-launching when needed.

    Returns {'ok': True, 'endpoint': str, 'reused': bool,
    'pid': int|None, 'launch_ms': float|None, 'health': dict}.
    `pid` is set only when this call launched the process; a reused
    endpoint owned by someone else reports pid None and stop() will
    refuse to kill it.
    """
    endpoint = validate_endpoint(endpoint or _env_endpoint())
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    profile = Path(profile) if profile else state_dir / PROFILE_DIRNAME
    probe = health(endpoint)
    if probe["ok"]:
        state = _read_state(state_dir)
        pid = state.get("pid")
        if isinstance(pid, int) and _pid_is_ours(pid, profile):
            live_pid = pid
        else:
            live_pid = None
        return {"ok": True, "endpoint": endpoint, "reused": True,
                "pid": live_pid, "launch_ms": None, "health": probe}
    pid, launch_ms = _launch_chromium(endpoint, profile, state_dir, env=env)
    state = _read_state(state_dir)
    state.update({"endpoint": endpoint, "pid": pid, "profile": str(profile),
                  "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                  "contexts": state.get("contexts", [])})
    _write_state(state_dir, state)
    return {"ok": True, "endpoint": endpoint, "reused": False,
            "pid": pid, "launch_ms": launch_ms, "health": health(endpoint)}


# ---------------------------------------------------------------------------
# Minimal stdlib WebSocket client (CDP only, loopback only).
# ---------------------------------------------------------------------------

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class _WSClient:
    """One CDP WebSocket connection. Text frames only; pings answered."""

    def __init__(self, url, timeout=CDP_TIMEOUT_SECONDS):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("ws", "wss") or parsed.hostname not in LOOPBACK_HOSTS:
            raise WarmBrowserError("CDP WebSocket must be loopback ws: " + url)
        if parsed.scheme == "wss":
            raise WarmBrowserError("CDP WebSocket must be plain ws, not wss: " + url)
        self._host = parsed.hostname
        self._port = parsed.port or 80
        self._path = parsed.path or "/"
        if parsed.query:
            self._path += "?" + parsed.query
        self._timeout = timeout
        self._seq = 0
        self.events = []
        self._buf = b""
        self._sock = socket.create_connection(
            (self._host, self._port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            "GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n"
            "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
            % (self._path, self._host, self._port, key))
        self._sock.sendall(handshake.encode("ascii"))
        self._sock.settimeout(timeout)
        headers = b""
        while b"\r\n\r\n" not in headers:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise WarmBrowserError("CDP WebSocket closed during handshake")
            headers += chunk
        if b" 101 " not in headers.split(b"\r\n", 1)[0]:
            raise WarmBrowserError("CDP WebSocket handshake failed")
        accept = hashlib.sha1(
            (key + _WS_GUID).encode("ascii")).digest()
        if base64.b64encode(accept).decode("ascii").encode("ascii") not in headers:
            raise WarmBrowserError("CDP WebSocket handshake key mismatch")

    def _recv_exact(self, count):
        while len(self._buf) < count:
            chunk = self._sock.recv(65536)
            if not chunk:
                raise WarmBrowserError("CDP WebSocket closed")
            self._buf += chunk
        out, self._buf = self._buf[:count], self._buf[count:]
        return out

    def _recv_frame(self):
        first, second = self._recv_exact(2)
        fin = bool(first & 0x80)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]
        if second & 0x80:
            mask = self._recv_exact(4)
            payload = bytes(b ^ mask[i % 4]
                            for i, b in enumerate(self._recv_exact(length)))
        else:
            payload = self._recv_exact(length)
        return fin, opcode, payload

    def _send_frame(self, opcode, payload):
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(bytes(header) + mask + masked)

    def _recv_message(self):
        fragments = []
        while True:
            fin, opcode, payload = self._recv_frame()
            if opcode == 9:  # ping
                self._send_frame(10, payload)
                continue
            if opcode == 8:
                raise WarmBrowserError("CDP WebSocket closed by peer")
            if opcode == 0 or opcode == 1:
                fragments.append(payload)
                if fin:
                    return b"".join(fragments)
            # Other opcodes are ignored; binary is not expected from CDP.

    def call(self, method, params=None, timeout=None):
        """One CDP call; returns the result dict. Raises WarmBrowserError."""
        self._seq += 1
        call_id = self._seq
        self._sock.settimeout(timeout or self._timeout)
        self._send_frame(1, json.dumps(
            {"id": call_id, "method": method,
             "params": params or {}}).encode("utf-8"))
        deadline = time.monotonic() + (timeout or self._timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise WarmBrowserError("CDP timeout: " + method)
            self._sock.settimeout(remaining)
            try:
                raw = self._recv_message()
            except socket.timeout as exc:
                raise WarmBrowserError("CDP timeout: " + method) from exc
            try:
                message = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise WarmBrowserError("CDP returned invalid JSON") from exc
            if message.get("id") == call_id:
                if "error" in message:
                    raise WarmBrowserError(
                        "CDP %s: %s" % (method, message["error"].get("message")))
                return message.get("result", {})
            if "method" in message:
                self.events.append(message)

    def wait_event(self, method, timeout):
        """True when a CDP event with this method arrives in time."""
        deadline = time.monotonic() + timeout
        for event in self.events:
            if event.get("method") == method:
                return True
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            self._sock.settimeout(remaining)
            try:
                raw = self._recv_message()
            except socket.timeout:
                return False
            try:
                message = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if message.get("method") == method:
                return True
            if "method" in message:
                self.events.append(message)

    def close(self):
        try:
            self._send_frame(8, b"")
        except OSError:
            pass
        try:
            self._sock.close()
        except OSError:
            pass


def _browser_ws_url(endpoint):
    version = _http_json(endpoint, "/json/version", timeout=2)
    url = version.get("webSocketDebuggerUrl") if isinstance(version, dict) else None
    if not url:
        raise WarmBrowserError("CDP /json/version has no browser WebSocket URL")
    return url


def _target_ws_url(endpoint, target_id):
    tabs = _http_json(endpoint, "/json/list", timeout=2)
    for tab in tabs:
        if isinstance(tab, dict) and tab.get("id") == target_id:
            url = tab.get("webSocketDebuggerUrl")
            if url:
                return url
    raise WarmBrowserError("CDP target not listed: " + target_id)


def _evaluate(ws, expression):
    result = ws.call("Runtime.evaluate", {
        "expression": expression, "returnByValue": True,
        "awaitPromise": True}, timeout=CDP_TIMEOUT_SECONDS)
    if result.get("exceptionDetails"):
        raise WarmBrowserError(
            "evaluate failed: %s" % result["exceptionDetails"].get("text"))
    value = result.get("result", {})
    if value.get("subtype") == "error":
        raise WarmBrowserError(
            "evaluate failed: %s" % value.get("description"))
    return value.get("value")


def _create_context(endpoint, task_id, url, state_dir):
    """Create one fresh browser context plus target. Returns context dict."""
    started = time.monotonic()
    browser_ws = _WSClient(_browser_ws_url(endpoint))
    try:
        created = browser_ws.call("Target.createBrowserContext", {})
        context_id = created.get("browserContextId")
        if not context_id:
            raise WarmBrowserError("Target.createBrowserContext gave no id")
        target = browser_ws.call("Target.createTarget", {
            "url": url or "about:blank", "browserContextId": context_id})
        target_id = target.get("targetId")
        if not target_id:
            raise WarmBrowserError("Target.createTarget gave no id")
    finally:
        browser_ws.close()
    context_ms = round((time.monotonic() - started) * 1000, 1)
    navigate_ms = None
    loaded = None
    if url:
        page_ws = _WSClient(_target_ws_url(endpoint, target_id))
        try:
            page_ws.call("Page.enable", {})
            nav_started = time.monotonic()
            page_ws.call("Page.navigate", {"url": url},
                         timeout=CDP_TIMEOUT_SECONDS)
            loaded = page_ws.wait_event("Page.loadEventFired",
                                        LOAD_TIMEOUT_SECONDS)
            navigate_ms = round((time.monotonic() - nav_started) * 1000, 1)
        finally:
            page_ws.close()
    record = {"task_id": task_id, "target_id": target_id,
              "browser_context_id": context_id, "url": url or "about:blank",
              "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "context_ms": context_ms, "navigate_ms": navigate_ms,
              "loaded": loaded}
    state = _read_state(state_dir)
    contexts = [c for c in state.get("contexts", [])
                if c.get("task_id") != task_id]
    contexts.append(record)
    state["contexts"] = contexts
    _write_state(state_dir, state)
    return record


def new_task_context(task_id, url=None, endpoint=None, state_dir=None,
                     env=None):
    """Fresh isolated context in the warm browser. Cold fallback on failure.

    Returns the context record plus {'warm': bool, 'ensure_ms': float,
    'total_ms': float, 'endpoint': str}. Retries once after a forced
    relaunch when the first attempt fails.
    """
    if not task_id or not isinstance(task_id, str):
        raise WarmBrowserError("task-id must be a non-empty string")
    if url is not None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https", "file", "data", "about"):
            raise WarmBrowserError("context URL must be http(s), file, data or about")
    endpoint = validate_endpoint(endpoint or _env_endpoint())
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    started = time.monotonic()
    ensure_started = time.monotonic()
    warm = ensure_warm(endpoint=endpoint, state_dir=state_dir, env=env)
    ensure_ms = round((time.monotonic() - ensure_started) * 1000, 1)
    try:
        record = _create_context(endpoint, task_id, url, state_dir)
    except (WarmBrowserError, OSError) as exc:
        # Guard (b): a stale or crashed warm browser must not take down
        # every subsequent task. Force a cold relaunch once and retry.
        state = _read_state(state_dir)
        pid = state.get("pid")
        profile = state.get("profile") or str(state_dir / PROFILE_DIRNAME)
        if isinstance(pid, int) and _pid_is_ours(pid, profile):
            stop(state_dir=state_dir)
        new_pid, _launch_ms = _launch_chromium(
            endpoint, Path(profile), state_dir, env=env)
        state = _read_state(state_dir)
        state.update({"endpoint": endpoint, "pid": new_pid,
                      "profile": str(profile),
                      "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                      "contexts": state.get("contexts", [])})
        _write_state(state_dir, state)
        try:
            record = _create_context(endpoint, task_id, url, state_dir)
        except (WarmBrowserError, OSError):
            raise WarmBrowserError(
                "warm browser cold-start fallback failed after retry: %s"
                % exc) from exc
        warm = dict(warm, reused=False)
    record.update({"ok": True, "warm": bool(warm.get("reused")),
                   "ensure_ms": ensure_ms,
                   "total_ms": round((time.monotonic() - started) * 1000, 1),
                   "endpoint": endpoint})
    return record


def close_task_context(task_id=None, target_id=None, endpoint=None,
                       state_dir=None):
    """Dispose one task context (all its targets die with it).

    Resolves the browser context id from the state file when only a
    task or target id is given. Returns {'ok': True, 'closed': ...}.
    """
    if not task_id and not target_id:
        raise WarmBrowserError("close-context needs --task-id or --target-id")
    endpoint = validate_endpoint(endpoint or _env_endpoint())
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    state = _read_state(state_dir)
    contexts = state.get("contexts", [])
    record = None
    for candidate in contexts:
        if task_id and candidate.get("task_id") == task_id:
            record = candidate
            break
        if target_id and candidate.get("target_id") == target_id:
            record = candidate
            break
    context_id = record.get("browser_context_id") if record else None
    closed = None
    if context_id:
        browser_ws = _WSClient(_browser_ws_url(endpoint))
        try:
            browser_ws.call("Target.disposeBrowserContext",
                            {"browserContextId": context_id})
            closed = "browser_context:" + context_id
        finally:
            browser_ws.close()
    elif target_id:
        _http_json(endpoint, "/json/close/" + urllib.parse.quote(target_id),
                   method="GET")
        closed = "target:" + target_id
    else:
        raise WarmBrowserError("no recorded context for this task or target")
    state["contexts"] = [c for c in contexts if c is not record]
    _write_state(state_dir, state)
    return {"ok": True, "closed": closed,
            "task_id": record.get("task_id") if record else task_id,
            "target_id": record.get("target_id") if record else target_id}


def verify_isolation(endpoint=None, state_dir=None, env=None):
    """Prove two task contexts cannot see each other's state.

    Creates context A and B on a loopback probe page (about:blank
    has an opaque origin, so cookies and localStorage cannot be set
    there; the probe page is served by this function on 127.0.0.1),
    writes a marker cookie plus a localStorage key in A, reads both
    back in A (must be present) and in B (must be absent), then
    closes both contexts. Returns {'ok': bool, 'isolated': bool,
    'a_sees_marker': bool, 'b_sees_marker': bool, ...}. A leak
    reports isolated False instead of raising, so the caller can
    record the evidence.
    """
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    endpoint = validate_endpoint(endpoint or _env_endpoint())
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    marker = "wb-%d" % int(time.time())

    class _ProbeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"<!doctype html><title>warm-browser probe</title>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), _ProbeHandler)
    probe_url = "http://127.0.0.1:%d/probe.html" % server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    set_expr = (
        "(()=>{document.cookie='%s=%s; path=/';"
        "try{localStorage.setItem('%s','%s');}catch(_){}"
        "return document.cookie;})()"
        % (ISOLATION_COOKIE_NAME, marker,
           ISOLATION_STORAGE_KEY, marker))
    read_cookie = "document.cookie"
    read_storage = (
        "(()=>{try{return localStorage.getItem('%s');}catch(_){return null;}})()"
        % ISOLATION_STORAGE_KEY)
    ctx_a = ctx_b = None
    try:
        ctx_a = new_task_context("warm-probe-a", url=probe_url,
                                 endpoint=endpoint, state_dir=state_dir,
                                 env=env)
        ctx_b = new_task_context("warm-probe-b", url=probe_url,
                                 endpoint=endpoint, state_dir=state_dir,
                                 env=env)
        ws_a = _WSClient(_target_ws_url(endpoint, ctx_a["target_id"]))
        try:
            _evaluate(ws_a, set_expr)
            a_cookie = _evaluate(ws_a, read_cookie) or ""
            a_storage = _evaluate(ws_a, read_storage)
        finally:
            ws_a.close()
        ws_b = _WSClient(_target_ws_url(endpoint, ctx_b["target_id"]))
        try:
            b_cookie = _evaluate(ws_b, read_cookie) or ""
            b_storage = _evaluate(ws_b, read_storage)
        finally:
            ws_b.close()
        a_sees = marker in a_cookie and a_storage == marker
        b_sees = marker in b_cookie or b_storage == marker
        return {"ok": True, "isolated": bool(a_sees and not b_sees),
                "a_sees_marker": bool(a_sees), "b_sees_marker": bool(b_sees),
                "marker": marker,
                "context_a_ms": ctx_a.get("context_ms"),
                "context_b_ms": ctx_b.get("context_ms")}
    finally:
        for ctx in (ctx_a, ctx_b):
            if ctx:
                try:
                    close_task_context(task_id=ctx["task_id"],
                                       endpoint=endpoint, state_dir=state_dir)
                except (WarmBrowserError, OSError):
                    pass
        server.shutdown()
        server.server_close()


def stop(state_dir=None):
    """Terminate ONLY the Chromium this module launched. Never Zen.

    Refuses when the recorded pid is not a live Chromium running
    with our profile (someone else's browser, stale pid, reused
    endpoint). Returns {'ok': True, 'stopped': bool, 'pid': int|None}.
    """
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    state = _read_state(state_dir)
    pid = state.get("pid")
    profile = state.get("profile") or str(state_dir / PROFILE_DIRNAME)
    if not isinstance(pid, int):
        return {"ok": True, "stopped": False, "pid": None,
                "reason": "no recorded warm-browser pid"}
    if not _pid_is_ours(pid, profile):
        return {"ok": False, "stopped": False, "pid": pid,
                "reason": "recorded pid is not our Chromium; refusing to kill"}
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        _write_state(state_dir, {})
        return {"ok": True, "stopped": False, "pid": pid,
                "reason": "process already gone"}
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not _pid_cmdline(pid):  # gone, or zombie with an empty cmdline
            break
        time.sleep(0.1)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        time.sleep(0.5)
    _write_state(state_dir, {})
    return {"ok": True, "stopped": True, "pid": pid}


def status(endpoint=None, state_dir=None):
    """State file plus live health, for the operator. Never raises."""
    endpoint = validate_endpoint(endpoint or _env_endpoint())
    state_dir = Path(state_dir) if state_dir else _env_state_dir()
    state = _read_state(state_dir)
    return {"ok": True, "endpoint": endpoint, "health": health(endpoint),
            "recorded_pid": state.get("pid"),
            "recorded_profile": state.get("profile"),
            "started_at": state.get("started_at"),
            "open_contexts": len(state.get("contexts", [])),
            "contexts": state.get("contexts", [])}


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="warm_browser",
        description="Warm Chromium manager: one process, fresh context per task.")
    parser.add_argument("--endpoint", default=None,
                        help="CDP endpoint (default $CU_WARM_BROWSER_ENDPOINT or 127.0.0.1:9222)")
    parser.add_argument("--state-dir", default=None,
                        help="state dir (default $CU_WARM_BROWSER_STATE_DIR)")
    parser.add_argument("--profile", default=None,
                        help="warm Chromium profile dir")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ensure")
    sub.add_parser("health")
    sub.add_parser("status")
    sub.add_parser("stop")
    new_ctx = sub.add_parser("new-context")
    new_ctx.add_argument("--task-id", required=True)
    new_ctx.add_argument("--url", default=None)
    close_ctx = sub.add_parser("close-context")
    close_ctx.add_argument("--task-id", default=None)
    close_ctx.add_argument("--target-id", default=None)
    sub.add_parser("verify-isolation")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    state_dir = Path(args.state_dir) if args.state_dir else None
    endpoint = args.endpoint
    try:
        if args.command == "ensure":
            result = ensure_warm(endpoint=endpoint, profile=args.profile,
                                 state_dir=state_dir)
        elif args.command == "health":
            result = health(endpoint or _env_endpoint())
        elif args.command == "status":
            result = status(endpoint=endpoint, state_dir=state_dir)
        elif args.command == "stop":
            result = stop(state_dir=state_dir)
        elif args.command == "new-context":
            result = new_task_context(args.task_id, url=args.url,
                                      endpoint=endpoint, state_dir=state_dir)
        elif args.command == "close-context":
            result = close_task_context(task_id=args.task_id,
                                        target_id=args.target_id,
                                        endpoint=endpoint, state_dir=state_dir)
        elif args.command == "verify-isolation":
            result = verify_isolation(endpoint=endpoint, state_dir=state_dir)
        else:
            raise WarmBrowserError("unknown command: " + str(args.command))
    except WarmBrowserError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())

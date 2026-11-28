#!/usr/bin/env python3
"""Repo-owned Chromium CLI wrapper. Stdlib only.

Talks to Chromium over its loopback DevTools HTTP endpoints, plus one
minimal stdlib WebSocket client used only by `open`: Chromium 157
ignores the `url` parameter of PUT /json/new (verified live 2026-11-18
with raw curl: the new tab stays about:blank even after activate and
4 s), so `open` creates the tab over HTTP and then navigates it with
CDP Page.navigate over its WebSocket, waiting for the load event.
Reading a page's DOM still goes through
`computer-use browser observe/act` (scripts/cdp.mjs), which owns the
full WebSocket side; this file's client does one call only.

Endpoint rule (same as `computer-use browser start`): the default
endpoint is http://127.0.0.1:9222, the agent-managed Chromium. The
user's own Chromium runs WITHOUT a remote debugging port (verified
2026-11-18: no DevToolsActivePort file, nothing listening on 9222), so
this wrapper can never attach to that session. If no endpoint answers,
tab commands fail with a clear error telling the agent to run
`computer-use browser start` first; the wrapper never launches, kills
or restarts any Chromium itself. For tests, point --endpoint at a
separate headless Chromium with its own --user-data-dir in /tmp.

Profile rule: history, bookmarks and downloads read the profile
read-only. The History sqlite file is copied to a temp file first
(the live DB is locked while Chromium runs) and opened read-only.
Nothing is ever written to the profile. Default profile is
~/.config/chromium/Default; --profile accepts either a profile dir
(containing History directly, as the agent profile does) or a
user-data dir (containing Default/History).

Active tab: the CDP HTTP endpoints do not report which tab is active,
so `current` returns the tab this wrapper last opened or activated,
tracked in a small state file under
~/.local/share/agent-computer-use/chromium-cli-state.json. If no tab
was tracked, or the tracked tab is closed, `current` fails and tells
the agent to list tabs and activate one.

Commands (each prints exactly one JSON object on stdout):
  tabs                        List page tabs: id, title, url.
  open <url>                  Open url in a NEW tab; records it as current.
  activate <tab-id>           Bring a tab to front; records it as current.
  close <tab-id>              Close a tab. Never closes a tab the agent
                              did not list first; close only the tab id
                              the task names, never "all tabs".
  current                     Title and URL of the tracked current tab.
  history [--limit N]         Recent visits from the profile History DB.
  bookmarks                   All bookmarks from the profile Bookmarks
                              file; empty list when the file is absent.
  downloads [--limit N]       Recent downloads from the History DB.
  status                      Reachability probe: endpoint, browser
                              version, profile and History presence.
                              Always exits 0; check `reachable`.

Global flags: --endpoint URL (default http://127.0.0.1:9222),
--profile DIR (default ~/.config/chromium/Default).
Exit 0 on success, 1 on error. No REPL mode, no shell, argv only.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_ENDPOINT = "http://127.0.0.1:9222"
DEFAULT_PROFILE = Path.home() / ".config" / "chromium" / "Default"
STATE_PATH = (Path.home() / ".local" / "share" / "agent-computer-use"
              / "chromium-cli-state.json")
HTTP_TIMEOUT_SECONDS = 5
DEFAULT_LIMIT = 20
MAX_LIMIT = 200

LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")

# Chromium DownloadItem state values.
DOWNLOAD_STATES = {0: "in_progress", 1: "complete", 2: "cancelled",
                   3: "interrupted"}


def chrome_time_to_iso(value):
    """Chrome epoch (microseconds since 1601-01-01) to ISO 8601 UTC."""
    try:
        micros = int(value)
    except (TypeError, ValueError):
        return None
    if micros <= 0:
        return None
    base = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
    try:
        return (base + datetime.timedelta(microseconds=micros)).isoformat()
    except OverflowError:
        return None


def validate_endpoint(raw):
    """Loopback http endpoint only; anything else is refused."""
    url = urllib.parse.urlparse(raw)
    if url.scheme != "http" or url.hostname not in LOOPBACK_HOSTS:
        raise ValueError("CDP endpoint must be loopback http: " + raw)
    try:
        port = url.port or 80
    except ValueError:
        raise ValueError("endpoint port is not a number: " + raw) from None
    if not 1 <= port <= 65535:
        raise ValueError("endpoint port out of range: " + raw)
    return raw.rstrip("/")


def validate_url(raw):
    """Only http/https URLs may be opened in a tab."""
    url = urllib.parse.urlparse(raw)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("open needs an http(s) URL: " + raw)
    if len(raw) > 2048:
        raise ValueError("URL is longer than 2048 characters")
    return raw


def http_json(endpoint, path, method="GET", expect_json=True):
    """One CDP HTTP call; returns parsed JSON, raises on failure.

    With expect_json False (activate, close), a 2xx with an empty or
    plain-text body is a success: real Chromium answers /json/close
    and /json/activate with an empty body, not JSON (found by the
    laptop live test 2026-11-18: close removed the tab but the wrapper
    reported invalid JSON). A JSON body is still parsed when present.
    """
    request = urllib.request.Request(endpoint + path, method=method)
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError("CDP %s %s: HTTP %s" % (method, path, exc.code)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("CDP %s %s unreachable: %s" % (method, path, exc.reason)) from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("CDP %s %s returned invalid text" % (method, path)) from exc
    if not expect_json:
        if not text.strip():
            return {}
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {"message": text}
        return parsed if isinstance(parsed, dict) else {"message": text}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CDP %s %s returned invalid JSON" % (method, path)) from exc


WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WS_CONNECT_TIMEOUT_SECONDS = 5
WS_LOAD_TIMEOUT_SECONDS = 10


def _ws_recv_exact(sock, count, deadline):
    """Read exactly count bytes, or raise on close/timeout."""
    chunks = []
    while sum(len(c) for c in chunks) < count:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("CDP WebSocket timed out")
        sock.settimeout(remaining)
        chunk = sock.recv(count - sum(len(c) for c in chunks))
        if not chunk:
            raise RuntimeError("CDP WebSocket closed")
        chunks.append(chunk)
    return b"".join(chunks)


def _ws_recv_message(sock, deadline):
    """One complete text message; answers ping, ignores pong, skips binary.

    Returns the message string, or None when the peer sent close.
    """
    fragments = []
    while True:
        first, second = _ws_recv_exact(sock, 2, deadline)
        fin = bool(first & 0x80)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack(">H", _ws_recv_exact(sock, 2, deadline))[0]
        elif length == 127:
            length = struct.unpack(">Q", _ws_recv_exact(sock, 8, deadline))[0]
        if second & 0x80:
            mask = _ws_recv_exact(sock, 4, deadline)
            payload = bytes(b ^ mask[i % 4] for i, b in
                            enumerate(_ws_recv_exact(sock, length, deadline)))
        else:
            payload = _ws_recv_exact(sock, length, deadline)
        if opcode == 0x9:
            sock.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
            continue
        if opcode == 0xA:
            continue
        if opcode == 0x8:
            return None
        if opcode in (0x1, 0x0):
            fragments.append(payload)
            if fin:
                return b"".join(fragments).decode("utf-8")
            continue
        raise RuntimeError("CDP WebSocket sent an unexpected opcode")


def _ws_send_text(sock, text):
    """One masked client text frame."""
    data = text.encode("utf-8")
    header = bytearray([0x81])
    if len(data) < 126:
        header.append(0x80 | len(data))
    elif len(data) < 65536:
        header.append(0x80 | 126)
        header.extend(struct.pack(">H", len(data)))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack(">Q", len(data)))
    mask = os.urandom(4)
    header.extend(mask)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    sock.sendall(bytes(header) + masked)


def ws_connect(ws_url):
    """Handshake a loopback ws:// URL; returns the connected socket."""
    url = urllib.parse.urlparse(ws_url)
    if url.scheme != "ws" or url.hostname not in LOOPBACK_HOSTS:
        raise ValueError("CDP debugger must be a loopback WebSocket: " + ws_url)
    try:
        port = url.port or 80
    except ValueError:
        raise ValueError("debugger port is not a number: " + ws_url) from None
    if not 1 <= port <= 65535:
        raise ValueError("debugger port out of range: " + ws_url)
    key = base64.b64encode(os.urandom(16)).decode()
    sock = socket.create_connection((url.hostname, port),
                                    timeout=WS_CONNECT_TIMEOUT_SECONDS)
    try:
        sock.sendall(("GET %s HTTP/1.1\r\nHost: %s:%d\r\n"
                      "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                      "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n"
                      % (url.path or "/", url.hostname, port, key)).encode())
        sock.settimeout(WS_CONNECT_TIMEOUT_SECONDS)
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk:
                raise RuntimeError("CDP WebSocket handshake closed")
            buf += chunk
        head = buf.split(b"\r\n\r\n", 1)[0]
        if b"101" not in head.split(b"\r\n")[0]:
            raise RuntimeError("CDP WebSocket handshake failed")
        accept = base64.b64encode(hashlib.sha1(
            (key + WS_GUID).encode()).digest()).decode()
        if ("Sec-WebSocket-Accept: " + accept).encode() not in head:
            raise RuntimeError("CDP WebSocket handshake accept mismatch")
    except BaseException:
        sock.close()
        raise
    return sock


def navigate_tab_via_ws(tab, url):
    """Navigate one tab to url over its CDP WebSocket; wait for load.

    Sends Page.enable then Page.navigate and waits up to
    WS_LOAD_TIMEOUT_SECONDS for Page.loadEventFired. Returns None on
    success. Raises on handshake failure, a navigation error, or a
    load timeout; a timeout means the tab may still be loading, so the
    caller reports it instead of claiming the URL opened.
    """
    ws_url = tab.get("webSocketDebuggerUrl", "")
    if not ws_url:
        raise RuntimeError("new tab has no debugger URL to navigate")
    sock = ws_connect(ws_url)
    try:
        deadline = time.monotonic() + WS_LOAD_TIMEOUT_SECONDS
        next_id = [0]
        pending = {}

        def call(method, params=None):
            call_id = next_id[0] + 1
            next_id[0] = call_id
            _ws_send_text(sock, json.dumps(
                {"id": call_id, "method": method, "params": params or {}}))
            while True:
                message = _ws_recv_message(sock, deadline)
                if message is None:
                    raise RuntimeError("CDP WebSocket closed during " + method)
                frame = json.loads(message)
                if frame.get("id") == call_id:
                    if "error" in frame:
                        raise RuntimeError("CDP %s failed: %s" % (
                            method, frame["error"].get("message", "unknown")))
                    return frame.get("result", {})
                if frame.get("method") == "Page.loadEventFired":
                    pending["loaded"] = True

        call("Page.enable")
        call("Page.navigate", {"url": url})
        while not pending.get("loaded"):
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "navigation to %s did not finish loading within %ds; "
                    "the tab may still be loading, check tabs again" % (
                        url, WS_LOAD_TIMEOUT_SECONDS))
            message = _ws_recv_message(sock, deadline)
            if message is None:
                raise RuntimeError("CDP WebSocket closed while loading " + url)
            frame = json.loads(message)
            if frame.get("method") == "Page.loadEventFired":
                pending["loaded"] = True
        return None
    finally:
        try:
            sock.close()
        except OSError:
            pass


def list_page_tabs(endpoint):
    """All targets of type page from /json/list."""
    targets = http_json(endpoint, "/json/list")
    if not isinstance(targets, list):
        raise RuntimeError("CDP /json/list returned an unexpected shape")
    tabs = []
    for target in targets:
        if not isinstance(target, dict) or target.get("type") != "page":
            continue
        tabs.append({"id": target.get("id", ""),
                     "title": target.get("title", ""),
                     "url": target.get("url", "")})
    return tabs


def read_state():
    """Tracked current tab, or None when nothing was tracked yet."""
    try:
        data = json.loads(STATE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not data.get("tab_id"):
        return None
    return data


def write_state(tab):
    """Record tab as current; private file, private dir."""
    STATE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = {"tab_id": tab["id"], "title": tab.get("title", ""),
               "url": tab.get("url", ""),
               "updated_unix": int(datetime.datetime.now(
                   tz=datetime.timezone.utc).timestamp())}
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


def clear_state_if(tab_id):
    """Drop the tracked tab when it was the one just closed."""
    state = read_state()
    if state and state.get("tab_id") == tab_id:
        try:
            STATE_PATH.unlink()
        except OSError:
            pass


def resolve_profile_file(profile_dir, filename):
    """<dir>/<file>, else <dir>/Default/<file>; None when neither exists."""
    direct = Path(profile_dir) / filename
    if direct.is_file():
        return direct
    nested = Path(profile_dir) / "Default" / filename
    if nested.is_file():
        return nested
    return None


def copy_db_readonly(path):
    """Copy a live sqlite file to a temp file; returns the temp path."""
    fd, tmp = tempfile.mkstemp(prefix="chromium-cli-", suffix=".sqlite")
    os.close(fd)
    shutil.copyfile(path, tmp)
    return tmp


def query_history_db(db_path, limit):
    """Recent visits from a History sqlite copy."""
    tmp = copy_db_readonly(db_path)
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % tmp, uri=True)
        try:
            rows = conn.execute(
                "SELECT url, title, visit_count, last_visit_time FROM urls"
                " ORDER BY last_visit_time DESC LIMIT ?",
                (limit,)).fetchall()
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
                       "last_visit": chrome_time_to_iso(last_visit)})
    return visits


def query_downloads_db(db_path, limit):
    """Recent downloads from a History sqlite copy."""
    tmp = copy_db_readonly(db_path)
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % tmp, uri=True)
        try:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            if "downloads" not in tables:
                return [], "no downloads table in History DB"
            rows = conn.execute(
                "SELECT target_path, tab_url, start_time, state,"
                " total_bytes, received_bytes FROM downloads"
                " ORDER BY start_time DESC LIMIT ?",
                (limit,)).fetchall()
        finally:
            conn.close()
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    downloads = []
    for target_path, tab_url, start_time, state, total, received in rows:
        downloads.append({
            "target_path": target_path or "", "url": tab_url or "",
            "started": chrome_time_to_iso(start_time),
            "state": DOWNLOAD_STATES.get(state, "unknown"),
            "total_bytes": total if total is not None else -1,
            "received_bytes": received if received is not None else 0})
    return downloads, None


def walk_bookmarks(node, folder, out):
    """Flatten one Bookmarks JSON node (folder or url) into out."""
    if not isinstance(node, dict):
        return
    kind = node.get("type")
    if kind == "url":
        out.append({"name": node.get("name", ""), "url": node.get("url", ""),
                    "folder": folder,
                    "date_added": chrome_time_to_iso(node.get("date_added"))})
    elif kind == "folder":
        child_folder = node.get("name", "") if folder else node.get("name", "")
        for child in node.get("children", []):
            walk_bookmarks(child, child_folder, out)


def cmd_tabs(endpoint, args):
    return {"ok": True, "command": "tabs", "endpoint": endpoint,
            "tabs": list_page_tabs(endpoint)}


def cmd_open(endpoint, args):
    url = validate_url(args.url)
    target = http_json(endpoint, "/json/new?" + urllib.parse.urlencode(
        {"url": url}), method="PUT")
    if not isinstance(target, dict) or not target.get("id"):
        raise RuntimeError("CDP /json/new returned an unexpected shape")
    tab_id = target["id"]
    # PUT /json/new alone does not navigate (Chromium 157 ignores the
    # url parameter); drive Page.navigate over the tab's WebSocket and
    # fail loudly when it does not settle, instead of returning an
    # about:blank tab as if the URL had opened.
    try:
        navigate_tab_via_ws(target, url)
    except (ValueError, RuntimeError, OSError) as exc:
        raise RuntimeError("open created tab %s but navigation failed: %s"
                           % (tab_id, exc)) from exc
    tabs = {tab["id"]: tab for tab in list_page_tabs(endpoint)}
    tab = tabs.get(tab_id)
    if tab is None:
        raise RuntimeError("new tab %s vanished after navigation" % tab_id)
    if tab.get("url", "") in ("", "about:blank"):
        raise RuntimeError("open created tab %s but it is still about:blank; "
                           "navigation did not happen" % tab_id)
    write_state(tab)
    return {"ok": True, "command": "open", "endpoint": endpoint, "tab": tab}


def cmd_activate(endpoint, args):
    if not args.tab_id.strip():
        raise ValueError("activate needs a non-empty tab id")
    http_json(endpoint, "/json/activate/" + urllib.parse.quote(
        args.tab_id, safe=""), expect_json=False)
    tabs = {tab["id"]: tab for tab in list_page_tabs(endpoint)}
    tab = tabs.get(args.tab_id)
    if tab is None:
        raise RuntimeError("tab not found after activate: " + args.tab_id)
    write_state(tab)
    return {"ok": True, "command": "activate", "endpoint": endpoint,
            "tab": tab}


def cmd_close(endpoint, args):
    if not args.tab_id.strip():
        raise ValueError("close needs a non-empty tab id")
    http_json(endpoint, "/json/close/" + urllib.parse.quote(
        args.tab_id, safe=""), expect_json=False)
    clear_state_if(args.tab_id)
    return {"ok": True, "command": "close", "endpoint": endpoint,
            "tab_id": args.tab_id}


def cmd_current(endpoint, args):
    state = read_state()
    if state is None:
        raise RuntimeError("no tab tracked yet; open or activate a tab first")
    tabs = {tab["id"]: tab for tab in list_page_tabs(endpoint)}
    tab = tabs.get(state["tab_id"])
    if tab is None:
        raise RuntimeError("tracked tab is closed; list tabs and activate one")
    return {"ok": True, "command": "current", "endpoint": endpoint,
            "tab": tab, "tracked": True}


def cmd_history(endpoint, args):
    profile = args.profile
    db_path = resolve_profile_file(profile, "History")
    if db_path is None:
        raise RuntimeError("no History file under profile: " + str(profile))
    return {"ok": True, "command": "history", "profile": str(profile),
            "history_file": str(db_path),
            "visits": query_history_db(db_path, args.limit)}


def cmd_bookmarks(endpoint, args):
    profile = args.profile
    path = resolve_profile_file(profile, "Bookmarks")
    if path is None:
        return {"ok": True, "command": "bookmarks", "profile": str(profile),
                "bookmarks": [],
                "note": "no Bookmarks file in profile"}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Bookmarks file is unreadable: " + str(exc)) from exc
    out = []
    roots = data.get("roots", {}) if isinstance(data, dict) else {}
    for key in ("bookmark_bar", "other", "synced"):
        walk_bookmarks(roots.get(key, {}), "", out)
    return {"ok": True, "command": "bookmarks", "profile": str(profile),
            "bookmarks_file": str(path), "bookmarks": out}


def cmd_downloads(endpoint, args):
    profile = args.profile
    db_path = resolve_profile_file(profile, "History")
    if db_path is None:
        raise RuntimeError("no History file under profile: " + str(profile))
    downloads, note = query_downloads_db(db_path, args.limit)
    result = {"ok": True, "command": "downloads", "profile": str(profile),
              "history_file": str(db_path), "downloads": downloads}
    if note:
        result["note"] = note
    return result


def cmd_status(endpoint, args):
    profile = args.profile
    history_path = resolve_profile_file(profile, "History")
    bookmarks_path = resolve_profile_file(profile, "Bookmarks")
    try:
        version = http_json(endpoint, "/json/version")
        reachable = True
        browser = version.get("Browser", "") if isinstance(version, dict) else ""
        protocol = version.get("Protocol-Version", "") if isinstance(version, dict) else ""
    except (RuntimeError, ValueError):
        reachable, browser, protocol = False, "", ""
    return {"ok": True, "command": "status", "endpoint": endpoint,
            "reachable": reachable, "browser": browser,
            "protocol_version": protocol,
            "profile": str(profile),
            "profile_exists": Path(profile).is_dir(),
            "history_exists": history_path is not None,
            "bookmarks_exist": bookmarks_path is not None}


COMMANDS = {
    "tabs": (cmd_tabs, "list page tabs"),
    "open": (cmd_open, "open a URL in a new tab"),
    "activate": (cmd_activate, "bring a tab to front"),
    "close": (cmd_close, "close one tab by id"),
    "current": (cmd_current, "title and URL of the tracked current tab"),
    "history": (cmd_history, "recent visits from the profile History DB"),
    "bookmarks": (cmd_bookmarks, "bookmarks from the profile Bookmarks file"),
    "downloads": (cmd_downloads, "recent downloads from the History DB"),
    "status": (cmd_status, "endpoint and profile reachability probe"),
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Chromium CLI wrapper over loopback CDP HTTP endpoints.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT,
                        help="loopback CDP endpoint (default %(default)s)")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE),
                        help="Chromium profile dir (default %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tabs", help=COMMANDS["tabs"][1])
    open_parser = sub.add_parser("open", help=COMMANDS["open"][1])
    open_parser.add_argument("url")
    activate_parser = sub.add_parser("activate", help=COMMANDS["activate"][1])
    activate_parser.add_argument("tab_id")
    close_parser = sub.add_parser("close", help=COMMANDS["close"][1])
    close_parser.add_argument("tab_id")
    sub.add_parser("current", help=COMMANDS["current"][1])
    history_parser = sub.add_parser("history", help=COMMANDS["history"][1])
    history_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    sub.add_parser("bookmarks", help=COMMANDS["bookmarks"][1])
    downloads_parser = sub.add_parser("downloads", help=COMMANDS["downloads"][1])
    downloads_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    sub.add_parser("status", help=COMMANDS["status"][1])
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command
    try:
        endpoint = validate_endpoint(args.endpoint)
        limit = getattr(args, "limit", DEFAULT_LIMIT)
        if not 1 <= limit <= MAX_LIMIT:
            raise ValueError("limit must be 1..%d" % MAX_LIMIT)
        handler = COMMANDS[command][0]
        result = handler(endpoint, args)
    except (ValueError, RuntimeError, OSError) as exc:
        print(json.dumps({"ok": False, "command": command,
                          "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

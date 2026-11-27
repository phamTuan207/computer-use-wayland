#!/usr/bin/env python3
"""R10 seamless RDP client with tool-enforced tab scoping (RT-20, stdlib only).

Base: W4 production-shaped client (connect, listTabs, getTarget,
evaluateJSAsync, navigateTo, port-owner guard, fail-loud webdriver probe,
navigate-to-load polling, latency bench).

RT-20 additions (enforced IN the tool, not in briefs):
- Scope set at attach: allowed tab descriptor ids and/or URL glob patterns.
  evaluate/navigate/getTarget on an out-of-scope tab raises RDPError.
  When BOTH tab ids and URL patterns are given, a tab must match BOTH
  (AND semantics). No scope is REFUSED unless --unscoped-test is passed
  explicitly (loud warning, recorded in the drive report).
- Credential-tab denylist: ON by default in the CLI (generic defaults
  below; --scope-config patterns override them). Disabling requires the
  explicit --no-denylist flag (loud warning, recorded in the report).
  A denylisted tab is refused even when in scope, unless an explicit
  approval (--allow-credential-tab + --approval-note) covers it;
  approvals used are recorded in the drive report. A tab reporting an
  empty URL (lazy/unloaded) is treated as denylisted while the denylist
  is enabled. Approvals may key by tab id or by URL pattern; id-keyed
  approvals are positional and migrate when tab ids shift, so URL
  patterns are the robust form.
- Parent-process target evaluate (chrome JS) is available only with
  allow_parent=True / --allow-parent; every parent evaluate is recorded
  in the drive report. Large string results (RDP longString grips) are
  fetched in full via substring requests for tab and parent evaluates.
- Single-drive lock: --lock-file (or RDP_LOCK_FILE) flock()s the file
  for the session; a second client on the same file is refused. The
  holder records pid + process start time in the file, so a refusal
  names the holder and says whether it is alive or a stale record.
  See LOCK-MAP.md for every lock in the stack and stale behavior.
- Drive report (JSON): webdriver probe, tab list before/after with diff,
  scope used, denylist hits, scope refusals, approvals used, action counts.
  Written to --drive-report on session end, or on demand via `report`.

Runs on the laptop next to the browser. No geckodriver, no DevTools
frontend. ydotool is banned (not used here; this client sends no OS input).
Generic defaults only: no machine-specific values in this file. Real
patterns belong in a machine-layer config file passed via --scope-config.

Landed fixes (R10 landing integration):
- Tab-pinned re-attach: closing DevTools swaps the tab target and kills
  the held consoleActor once with noSuchActor (RT-06). evaluate/navigate
  catch that error, re-attach pinned to the same tab (canonical
  descriptor id, URL fallback, never selected-pick), and retry once.
- Fail-closed port-owner guard: an explicit profile marker is required
  before attach. The only escape is the test-only
  --allow-unmarked-test-attach flag, which warns loudly.
"""
import argparse
import fcntl
import fnmatch
import json
import os
import re
import socket
import stat as _stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import unquote

# Generic credential-tab URL fragments. The CLI enables these by default;
# --scope-config patterns override them; --no-denylist disables the
# denylist explicitly (loud warning, recorded in the drive report).
DEFAULT_CREDENTIAL_DENYLIST = [
    "login", "signin", "sign-in", "account", "auth", "oauth",
    "password", "checkout", "payment",
]

UNSCOPED_WARNING = (
    "WARNING: RDP session is UNSCOPED - no tab scope was given, so this "
    "session may act on ANY tab, including credential tabs. Pass "
    "--scope-tab-id / --scope-url-pattern (or a --scope-config) to "
    "restrict it. Unscoped mode is for throwaway/test use only."
)

NO_DENYLIST_WARNING = (
    "WARNING: credential denylist DISABLED via --no-denylist - "
    "credential tabs (login/account/payment URLs) are NOT refused in "
    "this session. This is recorded in the drive report."
)

# Denylist "pattern" recorded when a tab reports an empty URL (lazy tab).
LAZY_TAB_PATTERN = "<empty-url-lazy-tab>"

# Packet types that must go through the guarded methods, never raw
# request() (see RDPClient.request).
_GUARDED_PACKET_TYPES = ("evaluateJSAsync", "navigateTo")


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ms(sec):
    return round(sec * 1000, 1)


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _stat_is_regular(info):
    return _stat.S_ISREG(info.st_mode)


def _proc_start_time(pid):
    """Process start time (clock ticks since boot) from /proc, or None.

    Field 22 of /proc/<pid>/stat; the comm field may contain spaces
    and parens, so split after the last ')'. pid + start time pins a
    process incarnation: a reused pid has a different start time."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            rest = f.read().rsplit(")", 1)[1].split()
        return rest[19]  # field 22 overall, index 19 after comm/state
    except (OSError, IndexError):
        return None


def _lock_record(pid=None):
    pid = os.getpid() if pid is None else pid
    start = _proc_start_time(pid) or "-"
    return f"pid={pid} start={start} at={_now_iso()}\n"


def _parse_lock_record(text):
    """Parse a lock-file holder record. Accepts the current
    'pid=N start=T at=ISO' form and the legacy bare-pid form.
    Returns {'pid': int, 'start': str|None} or None."""
    text = (text or "").strip()
    if not text:
        return None
    if text.isdigit():
        return {"pid": int(text), "start": None}
    fields = {}
    for part in text.split():
        if "=" in part:
            k, v = part.split("=", 1)
            fields[k] = v
    try:
        pid = int(fields["pid"])
    except (KeyError, ValueError):
        return None
    start = fields.get("start")
    return {"pid": pid, "start": None if start in (None, "-") else start}


def _holder_alive(record):
    """True: recorded holder process is running (same incarnation).
    False: pid is gone or was reused (stale record). None: cannot
    tell (no record, or liveness check not permitted)."""
    if not record:
        return None
    pid = record["pid"]
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return None
    except OSError:
        return None
    if record.get("start") is not None:
        current = _proc_start_time(pid)
        if current is not None and current != record["start"]:
            return False  # pid reused by an unrelated process
    return True


def _lock_holder_detail(fd):
    """Human suffix for the LOCK REFUSED message, read from our own
    fd (same file we just failed to flock; no path re-open race)."""
    try:
        raw = os.pread(fd, 256, 0).decode("utf-8", "replace")
    except OSError:
        return ""
    record = _parse_lock_record(raw)
    if record is None:
        return ""
    alive = _holder_alive(record)
    if alive is True:
        return f" by pid {record['pid']} (process alive)"
    if alive is False:
        return (f"; recorded holder pid {record['pid']} is not running "
                "(stale record: the flock is held by another open file "
                "description, e.g. an inherited fd)")
    return f" by pid {record['pid']} (liveness unknown)"


def _lock_path_is_fd(path, fd):
    """True when path still names the inode behind fd. False means the
    file was replaced (unlink + recreate) and our flock guards an
    unlinked inode that no contender will ever see."""
    try:
        by_path = os.stat(path)
        by_fd = os.fstat(fd)
    except OSError:
        return False
    return (by_path.st_ino == by_fd.st_ino
            and by_path.st_dev == by_fd.st_dev)


def _url_matches(url, pattern):
    """Glob match if pattern has * or ?, else case-insensitive substring."""
    if not url:
        return False
    u, p = url.lower(), pattern.lower()
    if "*" in p or "?" in p:
        return fnmatch.fnmatchcase(u, p)
    return p in u


def _canon_tab_id(actor):
    """Canonical tab key: RDP descriptor actors are per-connection
    (server1.conn1.tabDescriptor2 vs server1.conn2.tabDescriptor2 for the
    same tab; verified live, L3 probe 27/11). Strip the connection prefix
    so scope/approval ids match across connections. URL patterns remain
    the robust cross-connection scope; ids are exact within a session."""
    if not actor:
        return actor
    m = re.match(r"^[^.]+\.conn\d+\.(tabDescriptor\d+)$", actor)
    return m.group(1) if m else actor


class RDPError(Exception):
    pass


# --- I1: versioned CLI envelope + disposition (Zen lane pilot) ---
# The CLI prints exactly one JSON envelope on stdout:
#   {"version": "1", "ok": bool, "command": <cmd>,
#    "result": <payload or null>,
#    "error": {"code", "message", "disposition"} or null,
#    "disposition": {"delivery", "retry"}}
# Exit codes: 0 success, 1 runtime error, 2 usage/parse error
# (argparse and the manual refusals). --legacy-output restores
# the pre-envelope behavior exactly (bare JSON payload on
# success, "ERROR: ..." on stderr, exit 2 on any error) for
# existing consumers. The library API is unchanged.
# Delivery vocabulary: unknown, not_delivered,
# delivery_uncertain, delivered_unverified, delivered_verified.
# Retry vocabulary: safe (nothing was sent; fix and retry),
# unsafe (input may have landed; never replay), not_applicable.
ENVELOPE_VERSION = "1"
_READ_COMMANDS = {"probe", "tabs", "report"}

# Ordered (message substring, code, delivery, retry) for errors
# that are refusals or pre-send failures: nothing was delivered.
_REFUSAL_MAP = (
    ("UNSCOPED REFUSED", "unscoped_refused"),
    ("SCOPE REFUSED", "scope_refused"),
    ("CREDENTIAL TAB REFUSED", "denylist_refused"),
    ("LOCK REFUSED", "lock_held"),
    ("RAW PACKET REFUSED", "raw_packet_refused"),
    ("PARENT EVALUATE REFUSED", "parent_evaluate_refused"),
    ("cannot open lock file", "lock_unavailable"),
    ("port-owner", "port_owner_mismatch"),
    ("cannot read cmdline", "port_owner_mismatch"),
    ("scope config", "scope_config_invalid"),
    ("evaluate before attach", "not_attached"),
    ("no pinned tab", "attach_failed"),
    ("not found in tab list", "tab_not_found"),
    ("pinned tab", "attach_failed"),
    ("getTarget gave no consoleActor", "attach_failed"),
    ("listTabs returned no tabs", "attach_failed"),
    ("listProcesses returned none", "attach_failed"),
)


def _classify_error(message, cmd):
    """Map an RDPError message to (code, delivery, retry)."""
    msg = str(message or "")
    if "evaluate exception" in msg or "evaluate error" in msg:
        # The JS ran and threw (page-controlled text), or the evaluation
        # errored: delivered, effect unknown. Checked BEFORE the refusal
        # needles so page exception text can never classify as a safe
        # refusal; genuine refusals (scope/lock/port-owner) never carry
        # this prefix.
        return "evaluate_failed", "delivery_uncertain", "unsafe"
    for needle, code in _REFUSAL_MAP:
        if needle in msg:
            return code, "not_delivered", "safe"
    action = cmd not in _READ_COMMANDS
    if "wait_for timeout" in message or "wait_load timeout" in message:
        # The action landed; only the post-action wait expired.
        return "wait_timeout", "delivered_unverified", "unsafe"
    if "socket closed" in message or "timed out" in message or \
            "timeout" in message.lower():
        if action:
            return "transport_error", "delivery_uncertain", "unsafe"
        return "transport_error", "not_delivered", "safe"
    if action:
        return "runtime_error", "delivery_uncertain", "unsafe"
    return "runtime_error", "not_delivered", "safe"


def _success_disposition(cmd):
    if cmd in ("eval", "peval", "navigate"):
        # JS executed (eval/peval) or navigateTo sent (navigate); the
        # tool does not verify page effect, including whether the
        # navigate URL actually changed.
        return {"delivery": "delivered_unverified",
                "retry": "not_applicable"}
    return {"delivery": "delivered_verified", "retry": "not_applicable"}


def _emit(cmd, result, legacy):
    if legacy:
        print(json.dumps(result, indent=1))
        return
    print(json.dumps({"version": ENVELOPE_VERSION, "ok": True,
                      "command": cmd, "result": result, "error": None,
                      "disposition": _success_disposition(cmd)},
                     indent=1))


def _fail(cmd, code, message, delivery, retry, exit_code, legacy,
          result=None):
    # stderr keeps the historical line for log readers either way.
    print(f"ERROR: {message}", file=sys.stderr)
    if legacy:
        return 2
    print(json.dumps({"version": ENVELOPE_VERSION, "ok": False,
                      "command": cmd, "result": result,
                      "error": {"code": code, "message": message,
                                "disposition": {"delivery": delivery,
                                                "retry": retry}},
                      "disposition": {"delivery": delivery,
                                      "retry": retry}}, indent=1))
    return exit_code


class Scope:
    """Allowed tabs for one attached session.

    AND semantics: when BOTH tab ids and URL patterns are given, a tab
    must match BOTH (id listed AND URL matches a pattern) to be in
    scope. When only one kind is given, that kind decides. An empty
    Scope means unscoped (refused at attach unless unscoped-test).
    """

    def __init__(self, tab_ids=None, url_patterns=None):
        self.tab_ids = set(tab_ids or [])
        self.url_patterns = list(url_patterns or [])

    @property
    def scoped(self):
        return bool(self.tab_ids or self.url_patterns)

    def matches(self, tab_id, url):
        if not self.scoped:
            return True
        id_ok = None
        if self.tab_ids:
            id_ok = tab_id is not None and _canon_tab_id(tab_id) in \
                {_canon_tab_id(t) for t in self.tab_ids}
        url_ok = None
        if self.url_patterns:
            url_ok = any(_url_matches(url, p) for p in self.url_patterns)
        if id_ok is not None and url_ok is not None:
            return id_ok and url_ok
        return bool(id_ok if id_ok is not None else url_ok)

    def to_dict(self):
        return {"scoped": self.scoped, "tab_ids": sorted(self.tab_ids),
                "url_patterns": list(self.url_patterns)}


def load_scope_config(path):
    """Load a JSON scope config. Recognized keys (all optional):
    scope_tab_ids [str], scope_url_patterns [str],
    credential_denylist_patterns [str] (aliases: denylist_patterns,
    credential_denylist). Returns a normalized dict."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except OSError as e:
        raise RDPError(f"cannot read scope config {path!r}: {e}")
    except json.JSONDecodeError as e:
        raise RDPError(f"scope config {path!r} is not valid JSON: {e}")
    if not isinstance(raw, dict):
        raise RDPError(f"scope config {path!r} must be a JSON object")
    deny = raw.get("credential_denylist_patterns")
    if deny is None:
        deny = raw.get("denylist_patterns", raw.get("credential_denylist"))
    return {
        "scope_tab_ids": list(raw.get("scope_tab_ids") or []),
        "scope_url_patterns": list(raw.get("scope_url_patterns") or []),
        "credential_denylist_patterns": list(deny) if deny else None,
    }


def _is_no_such_actor(text):
    """True when an RDP error text reports a dead actor (target swap)."""
    return "noSuchActor" in (text or "")


def check_port_owner(port, marker):
    """Refuse unless the process listening on `port` looks like the expected
    throwaway browser (cmdline contains `marker`). Returns (pid, cmdline).
    Fail-closed: an empty marker is refused, never skipped."""
    if not marker:
        raise RDPError(
            "profile marker is required (fail-closed): pass "
            "--profile-marker <substring> so the port owner can be "
            "verified before attach")
    try:
        out = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception as e:
        raise RDPError(f"port-owner check failed to run ss: {e}")
    pid = None
    for line in out.splitlines():
        if re.search(rf":{port}\s", line):
            m = re.search(r"pid=(\d+)", line)
            if m:
                pid = int(m.group(1))
                break
    if pid is None:
        raise RDPError(
            f"port {port}: no listening pid found via ss -tlnp "
            f"(browser not running, or port owned by another process)")
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            cmd = f.read().replace(b"\0", b" ").decode(errors="replace")
    except OSError as e:
        raise RDPError(f"port {port}: cannot read cmdline of pid {pid}: {e}")
    if marker not in cmd:
        raise RDPError(
            f"port {port} is bound by pid {pid} whose cmdline does not contain "
            f"expected marker {marker!r}; refusing to attach. cmdline: {cmd[:300]}")
    return pid, cmd


def _tab_snapshot(tabs):
    return [{"actor": t.get("actor"), "tab_id": _canon_tab_id(t.get("actor")),
             "url": _redact_url(t.get("url", "")), "title": t.get("title", ""),
             "selected": bool(t.get("selected"))} for t in tabs]


# I22: query parameters whose values never reach output bytes
# (tabs listing, drive report). Scope matching keeps raw URLs
# internally; only snapshots/reports are redacted. Matching is
# normalized (percent-decode, lowercase, split on separators and
# camelCase humps into whole tokens, whole-token stem match) so
# variants like accessToken, csrf_token, api-key, %74oken all hit.
_SENSITIVE_PARAMS = {
    "token", "access_token", "refresh_token", "id_token", "password",
    "passwd", "pwd", "secret", "api_key", "apikey", "auth",
    "authorization", "session", "sessionid", "sid", "code", "key",
    "signature", "sig", "otp", "pin",
}

# Whole-token sensitive stems matched after normalization. Token-level
# (never substring): innocent names like "zipcode" stay intact while
# "code" in "verification_code" is caught.
_SENSITIVE_STEMS = frozenset((
    "token", "secret", "password", "passwd", "pass", "auth", "session",
    "csrf", "otp", "code", "key", "credential", "bearer", "jwt", "saml",
    "assertion", "ticket", "signature", "private", "jsessionid",
))

_SENSITIVE_NAMES = frozenset(
    re.sub(r"[-_.\s]+", "", k).lower() for k in _SENSITIVE_PARAMS)

_REDACTED = "REDACTED"

# http(s) URLs embedded in text (e.g. inside error/prose strings).
_URL_TEXT_RE = re.compile(r"https?://[^\s'\"<>]+", re.IGNORECASE)


def _is_sensitive_param(name):
    """True when a param name is sensitive: normalized name equals a
    known-sensitive name, or any normalized whole token equals a stem.
    Normalization percent-decodes, lowercases, splits on separators
    (-/_/./space) and camelCase humps, so accessToken -> access+token."""
    raw = (name or "").strip()
    if not raw:
        return False
    norm = re.sub(r"%[0-9a-fA-F]{2}", lambda m: chr(int(m.group(0)[1:], 16)),
                  raw)
    tokens = tuple(t for t in re.split(
        r"[-_.\s]+|(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])",
        norm) if t)
    if re.sub(r"[-_.\s]+", "", norm).lower() in _SENSITIVE_NAMES:
        return True
    return any(t.lower() in _SENSITIVE_STEMS for t in tokens)


def _redact_pair(pair):
    """Redact one k=v pair (query, fragment, path param). Nested pair
    values whose decoded form carries a sensitive pair
    (next=/cb?token=SECRET) are redacted too; otherwise the pair is
    preserved verbatim."""
    name, eq, val = pair.partition("=")
    if not eq:
        return pair
    if _is_sensitive_param(name):
        return f"{name}={_REDACTED}"
    if "?" in val:
        head, _, nested = val.partition("?")
        new_nested = _redact_query_pairs(nested)
        if new_nested == nested:
            return pair
        redact_val = f"{head}?{new_nested}" if nested else head
        return f"{name}={redact_val}"
    if "%" in val:
        decoded = unquote(val)
        if decoded != val:
            if "?" in decoded:
                head, _, nested = decoded.partition("?")
                new_nested = _redact_query_pairs(nested)
                if new_nested == nested:
                    return pair
                redact_val = f"{head}?{new_nested}" if nested else head
                return f"{name}={redact_val}"
            elif _is_sensitive_param(decoded.partition("=")[0]):
                return f"{name}={_REDACTED}"
    return pair


def _redact_query_pairs(query):
    return "&".join(_redact_pair(p) for p in query.split("&") if p)


def _redact_path(path):
    """Redact ;-separated path parameters (e.g. /app;jsessionid=ABC)."""
    if ";" not in path:
        return path
    return ";".join(_redact_pair(s) if "=" in s else s
                    for s in path.split(";"))


def _redact_url(url):
    """Redact sensitive query/fragment params, userinfo passwords and
    path params from a URL. Non-URL text passes through unchanged;
    only URL-shaped strings are redacted."""
    if not url:
        return url
    m = re.match(r"^([A-Za-z][A-Za-z0-9+.\-]*://)([^/?#]*)", url)
    if not m:
        return url
    scheme, authority = m.group(1), m.group(2)
    userinfo, at, host = authority.partition("@")
    if at and ":" in userinfo:
        user, pw = userinfo.split(":", 1)
        if pw:
            userinfo = f"{user}:{_REDACTED}"
    if at:
        authority = f"{userinfo}@{host}"
    rest = url[m.end():]
    p_and_q, _, frag = rest.partition("#")
    path, sep, query = p_and_q.partition("?")
    redacted_path = _redact_path(path)
    out = f"{scheme}{authority}{redacted_path}"
    if sep:
        out += "?" + (_redact_query_pairs(query) if query else "")
    if frag:
        out += "#" + (_redact_query_pairs(frag) if ("=" in frag or "&" in frag) else frag)
    return out


def _redact_text(s):
    """Redact http(s) URL substrings inside arbitrary text
    (error/prose strings included). Conservative: only URL text is
    redacted, non-URL text is never mangled."""
    if not isinstance(s, str) or not _URL_TEXT_RE.search(s):
        return s
    return _URL_TEXT_RE.sub(lambda m: _redact_url(m.group(0)), s)


def _redact_report_urls(node):
    """Redact every URL string in a report dict, in place, via a
    recursive walk of dicts and lists plus bare URL strings. Covers
    keys like url/href plus any string value that looks like (or
    contains) an http(s) URL, including error strings."""
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, str):
                node[key] = _redact_text(value)
            else:
                _redact_report_urls(value)
    elif isinstance(node, list):
        for item in node:
            _redact_report_urls(item)
    elif isinstance(node, str):
        return _redact_text(node)
    return node


def _tab_diff(before, after):
    """Diff two tab snapshots. Descriptor ids are POSITIONAL and shift
    when tabs open/close, so id-keyed diff is only sound when the id
    sets are identical. Otherwise key by (url, title) pairs (multiset):
    a navigation then shows as one removed + one added pair, and
    `navigated` stays empty (cannot attribute reliably)."""
    b_ids = [t.get("tab_id") or t["actor"] for t in before]
    a_ids = [t.get("tab_id") or t["actor"] for t in after]
    if set(b_ids) == set(a_ids):
        b = {t.get("tab_id") or t["actor"]: t for t in before}
        a = {t.get("tab_id") or t["actor"]: t for t in after}
        navigated = [{"tab_id": k, "from_url": b[k]["url"],
                      "to_url": a[k]["url"]}
                     for k in a if a[k]["url"] != b[k]["url"]]
        return {"added": [], "removed": [], "navigated": navigated,
                "key_mode": "tab_id"}
    from collections import Counter
    b_pairs = Counter((t.get("url", ""), t.get("title", "")) for t in before)
    a_pairs = Counter((t.get("url", ""), t.get("title", "")) for t in after)
    added, removed = [], []
    seen = Counter()
    for t in after:
        p = (t.get("url", ""), t.get("title", ""))
        seen[p] += 1
        if seen[p] > b_pairs.get(p, 0):
            added.append(t)
    seen = Counter()
    for t in before:
        p = (t.get("url", ""), t.get("title", ""))
        seen[p] += 1
        if seen[p] > a_pairs.get(p, 0):
            removed.append(t)
    return {"added": added, "removed": removed, "navigated": [],
            "key_mode": "url_title"}


class RDPClient:
    def __init__(self, port, host="127.0.0.1", timeout=15, scope=None,
                 denylist_patterns=None, credential_approvals=None,
                 drive_report_path=None, transport=None, warn_unscoped=True,
                 unscoped_test=False, allow_parent=False, lock_file=None,
                 denylist_disabled=False):
        self.port = port
        self.scope = scope if scope is not None else Scope()
        self.denylist_patterns = list(denylist_patterns or [])
        self.credential_approvals = dict(credential_approvals or {})
        self.drive_report_path = drive_report_path
        self.unscoped_test = bool(unscoped_test)
        self.allow_parent = bool(allow_parent)
        self.denylist_disabled = bool(denylist_disabled)
        if not self.scope.scoped and not self.unscoped_test:
            raise RDPError(
                "UNSCOPED REFUSED: no tab scope was given. Pass a scope "
                "(--scope-tab-id / --scope-url-pattern / --scope-config), "
                "or pass --unscoped-test explicitly for throwaway/test "
                "use (loud warning, recorded in the drive report).")
        if warn_unscoped and not self.scope.scoped:
            print(UNSCOPED_WARNING, file=sys.stderr)
        # Single-drive lock (RT-23 fence): flock the file for the whole
        # session; refuse to attach when another drive holds it.
        self.lock_file = lock_file or os.environ.get("RDP_LOCK_FILE") \
            or None
        self._lock_fd = None
        self._lock_holder_pid = None
        if self.lock_file:
            self._acquire_lock(self.lock_file)
        try:
            if transport is not None:
                self.sock = transport
            else:
                self.sock = socket.create_connection((host, port),
                                                     timeout=timeout)
            self.buf = b""
            self.greeting = self._recv()
        except BaseException:
            # A failed attach must not wedge the single-drive fence:
            # the raw lock fd has no finalizer, so release it here.
            sock = getattr(self, "sock", None)
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
            self._release_lock()
            raise
        self.desc_actor = None
        self.target_actor = None
        self.console_actor = None
        self._tabs = []
        self._current_tab = None
        self._tabs_before = None
        self._probe_result = None
        self._pinned_tab_id = None
        self._pinned_url = ""
        self._retries = 0
        self._actions = {"evaluate": 0, "navigate": 0, "get_target": 0,
                         "parent_evaluate": 0}
        self._denylist_hits = []
        self._scope_refusals = []
        self._approvals_used = []
        self._parent_evals = []
        self._parent_desc = None
        self._parent_console = None
        self.parent_url = None
        self._internal_call = False  # guarded methods set this (request())
        self._started_at = _now_iso()

    # -- single-drive lock --------------------------------------------------
    # Hardened (I20 substitute): holder identity is pid + process start
    # time, so a contender can tell a live holder from a stale record
    # (dead pid, or pid reused by an unrelated process). The fd is
    # O_CLOEXEC (never inherited by children, which would keep the
    # flock alive past this process) and O_NOFOLLOW with an ownership
    # check (same fence as the relay lock). After flock succeeds the
    # path inode is re-checked: if the file was replaced under us
    # (unlink + recreate race), retry on the new inode instead of
    # holding a lock nobody else can see. flock itself needs no stale
    # recovery: the kernel releases it when the holder dies, so a
    # leftover file with a dead pid in it never wedges the fence.
    def _acquire_lock(self, path):
        for _attempt in range(3):
            fd = self._open_lock_file(path)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                detail = _lock_holder_detail(fd)
                os.close(fd)
                raise RDPError(
                    f"LOCK REFUSED: lock file {path!r} is already held"
                    + detail
                    + "; refusing to attach (single-drive fence)")
            if _lock_path_is_fd(path, fd):
                break
            # File replaced while we locked it: our flock guards an
            # unlinked inode. Drop it and retry on the visible file.
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(fd)
        else:
            raise RDPError(
                f"cannot open lock file {path!r}: file kept being "
                "replaced during acquisition")
        try:
            os.ftruncate(fd, 0)
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, _lock_record().encode())
        except OSError:
            pass
        self._lock_fd = fd
        self._lock_holder_pid = os.getpid()

    @staticmethod
    def _open_lock_file(path):
        flags = (os.O_RDWR | os.O_CREAT
                 | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_CLOEXEC", 0))
        try:
            fd = os.open(path, flags, 0o600)
        except OSError as e:
            raise RDPError(f"cannot open lock file {path!r}: {e}")
        try:
            info = os.fstat(fd)
        except OSError as e:
            os.close(fd)
            raise RDPError(f"cannot open lock file {path!r}: {e}")
        if not _stat_is_regular(info) or info.st_uid != os.geteuid():
            os.close(fd)
            raise RDPError(
                f"cannot open lock file {path!r}: not a regular file "
                "owned by this user")
        return fd

    def _release_lock(self):
        if self._lock_fd is not None:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
            except OSError:
                pass
            self._lock_fd = None

    # -- scope / denylist guards -------------------------------------------
    def _guard(self, tab_id, url, op):
        """Raise RDPError when (tab_id, url) is out of scope or denylisted
        without approval. Records hits/refusals/approvals for the report."""
        if not self.scope.matches(tab_id, url):
            self._scope_refusals.append(
                {"op": op, "tab_id": tab_id, "url": url, "at": _now_iso()})
            raise RDPError(
                f"SCOPE REFUSED: {op} on tab {tab_id!r} url={_redact_url(url)!r} is out "
                f"of scope (allowed tab ids: {sorted(self.scope.tab_ids)}, "
                f"url patterns: {self.scope.url_patterns})")
        if self.denylist_patterns:
            # Lazy/unloaded tabs report url='': no pattern can match, so
            # treat the empty URL itself as denylisted (fail-closed).
            hit = LAZY_TAB_PATTERN if not url else next(
                (p for p in self.denylist_patterns
                 if _url_matches(url, p)), None)
            if hit is not None:
                note = self._approval_note(tab_id, url)
                if note is not None:
                    self._approvals_used.append(
                        {"op": op, "tab_id": tab_id, "url": url,
                         "pattern": hit, "note": note, "at": _now_iso()})
                else:
                    self._denylist_hits.append(
                        {"op": op, "tab_id": tab_id, "url": url,
                         "pattern": hit, "at": _now_iso()})
                    raise RDPError(
                        f"CREDENTIAL TAB REFUSED: {op} on tab {tab_id!r} "
                        f"url={_redact_url(url)!r} matches denylist pattern {hit!r}. "
                        f"Pass --allow-credential-tab {tab_id} together "
                        f"with --approval-note <text> to approve explicitly.")

    def _approval_note(self, tab_id, url=None):
        """Approval note covering (tab_id, url), or None. Keys match by
        canonical tab id first, then as URL patterns. Id-keyed approvals
        are positional (they migrate when tab ids shift); URL-pattern
        approvals are the robust form."""
        canon = _canon_tab_id(tab_id)
        for k, v in self.credential_approvals.items():
            if _canon_tab_id(k) == canon:
                return v
        if url:
            for k, v in self.credential_approvals.items():
                if _url_matches(url, k):
                    return v
        return None

    def _guard_current(self, op):
        tab = self._current_tab or {}
        self._guard(self.desc_actor, tab.get("url", ""), op)

    # -- transport ----------------------------------------------------------
    def _fill(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RDPError("RDP socket closed by server")
            self.buf += chunk

    def _recv(self):
        self._fill(1)
        colon = self.buf.find(b":")
        while colon == -1:
            self._fill(len(self.buf) + 1)
            colon = self.buf.find(b":")
        length = int(self.buf[:colon])
        self._fill(colon + 1 + length)
        raw = self.buf[colon + 1: colon + 1 + length]
        self.buf = self.buf[colon + 1 + length:]
        return json.loads(raw.decode())

    def _send(self, obj):
        data = json.dumps(obj).encode()
        self.sock.sendall(f"{len(data)}:".encode() + data)

    def request(self, obj, expect_from=None, timeout=15, expect_key=None):
        # Guarded packet types (evaluate/navigate) must go through the
        # guarded methods, which set _internal_call. Raw request() of
        # those types is refused so scope cannot be bypassed by sending
        # packets directly. (The private _send stays internal-only.)
        if obj.get("type") in _GUARDED_PACKET_TYPES \
                and not self._internal_call:
            raise RDPError(
                f"RAW PACKET REFUSED: request() of type "
                f"{obj.get('type')!r} must go through the guarded "
                f"evaluate()/navigate()/parent_evaluate() methods")
        self.sock.settimeout(timeout)
        self._send(obj)
        while True:
            msg = self._recv()
            if expect_from is not None and msg.get("from") != expect_from:
                continue
            # Unsolicited root events (e.g. tabListChanged) also carry
            # from=root; require the response key when asked.
            if expect_key is not None and expect_key not in msg \
                    and not msg.get("error"):
                continue
            if msg.get("error"):
                raise RDPError(f"RDP error for {obj.get('type')}: {msg}")
            return msg

    # -- tabs / attach --------------------------------------------------------
    def list_tabs(self):
        """Read-only inventory; always allowed (needed to discover tabs).
        Acting on a tab (getTarget/evaluate/navigate) is what scope gates."""
        msg = self.request({"to": "root", "type": "listTabs"},
                           expect_from="root", expect_key="tabs")
        tabs = msg.get("tabs", [])
        if not tabs:
            raise RDPError(f"listTabs returned no tabs: {msg}")
        # Zen fresh profiles have 2 tabs; the VISIBLE one carries
        # selected=true (msg["selected"] is null on this build). Picking
        # index 0 attaches to a background tab (W4 smoke finding).
        sel = None
        for i, t in enumerate(tabs):
            if t.get("selected") is True:
                sel = i
                break
        if sel is None:
            s = msg.get("selected", 0)
            sel = s if isinstance(s, int) and 0 <= s < len(tabs) else 0
        self._tabs = tabs
        if self._tabs_before is None:
            self._tabs_before = _tab_snapshot(tabs)
        # Keep the current-tab pointer on the attached descriptor when one
        # is attached; otherwise track the selected tab.
        cur = next((t for t in tabs if t.get("actor") == self.desc_actor),
                   None)
        self._current_tab = cur if cur is not None else tabs[sel]
        if self.desc_actor is None:
            self.desc_actor = tabs[sel]["actor"]
        # NOTE: the pinned URL is deliberately NOT refreshed here.
        # Descriptor ids are positional; refreshing the pin by id lookup
        # would follow a shifted id onto a different tab and defeat the
        # URL verification in _reattach_pinned. The pin updates only in
        # get_target(), i.e. when we deliberately (re)attach.
        return tabs, sel

    def refresh_target(self):
        """Re-list tabs and re-get the target (after navigation the
        windowGlobalTarget is replaced; the visible tab stays selected)."""
        self.list_tabs()
        self.get_target()
        return self

    def _find_tab(self, tab_actor=None, tab_url=None):
        if not self._tabs:
            self.list_tabs()
        for _ in range(2):
            if tab_actor is not None:
                canon = _canon_tab_id(tab_actor)
                tab = next((t for t in self._tabs
                            if t.get("actor") == tab_actor
                            or _canon_tab_id(t.get("actor")) == canon), None)
            else:
                tab = next((t for t in self._tabs
                            if tab_url in (t.get("url") or "")), None)
            if tab is not None:
                return tab
            self.list_tabs()
        return None

    def get_target(self, tab_actor=None, tab_url=None):
        if tab_actor is not None or tab_url is not None:
            tab = self._find_tab(tab_actor, tab_url)
            if tab is None:
                raise RDPError(
                    f"tab {tab_actor or tab_url!r} not found in tab list")
            self._guard(tab.get("actor"), tab.get("url", ""), "getTarget")
            self.desc_actor = tab.get("actor")
            self._current_tab = tab
        else:
            if not self.desc_actor:
                self.list_tabs()
            self._guard_current("getTarget")
        msg = self.request({"to": self.desc_actor, "type": "getTarget"},
                           expect_from=self.desc_actor)
        frame = msg.get("frame") or msg.get("target") or {}
        self.target_actor = frame.get("actor") or msg.get("actor")
        self.console_actor = frame.get("consoleActor")
        if not self.console_actor and self.target_actor:
            # Fallback: attach on the target and read consoleActor from reply.
            try:
                self._send({"to": self.target_actor, "type": "attach"})
                for _ in range(8):
                    m = self._recv()
                    if m.get("from") != self.target_actor:
                        continue
                    if m.get("consoleActor"):
                        self.console_actor = m["consoleActor"]
                        break
                    if m.get("error"):
                        break
            except Exception:
                pass
        if not self.console_actor:
            raise RDPError(f"getTarget gave no consoleActor: {str(msg)[:500]}")
        self._actions["get_target"] += 1
        # Pin this tab: a later target swap (DevTools close) kills the
        # consoleActor, and recovery must land back on THIS tab.
        self._pinned_tab_id = _canon_tab_id(self.desc_actor)
        self._pinned_url = (self._current_tab or {}).get("url", "")
        return frame

    def _reattach_pinned(self):
        """Re-attach to the SAME tab after a target swap (RT-06: closing
        DevTools kills the held consoleActor once with noSuchActor).
        Pinned by canonical tab id with URL VERIFICATION: descriptor
        ids are positional, so an id hit whose URL differs from the
        pinned URL is a different tab and is refused (fail-closed).
        URL fallback only when the id is absent. Never falls back to
        the selected tab: selected-pick can land on the wrong tab."""
        pin_id, pin_url = self._pinned_tab_id, self._pinned_url
        if not pin_id and not pin_url:
            raise RDPError("no pinned tab to re-attach to")
        self.list_tabs()
        tab = None
        if pin_id:
            tab = next((t for t in self._tabs
                        if _canon_tab_id(t.get("actor")) == pin_id), None)
            if tab is not None and pin_url \
                    and (tab.get("url") or "") != pin_url:
                raise RDPError(
                    f"pinned tab {pin_id!r} url changed {_redact_url(pin_url)!r} -> "
                    f"{_redact_url(tab.get('url') or '')!r} (positional id shift?); refusing "
                    f"re-attach, refusing selected-tab fallback")
        if tab is None and pin_url:
            tab = next((t for t in self._tabs
                        if (t.get("url") or "") == pin_url), None)
        if tab is None:
            raise RDPError(
                f"pinned tab {pin_id!r} url={_redact_url(pin_url)} not found "
                f"after target swap; refusing selected-tab fallback")
        self.get_target(tab_actor=tab.get("actor"))

    def attach(self, tab_actor=None, tab_url=None):
        """connect already done in __init__; listTabs + getTarget.
        With tab_actor/tab_url, attach to that specific tab (scope-gated).
        tab_url (substring) resolves robustly across connections."""
        self.list_tabs()
        self.get_target(tab_actor, tab_url)
        return self

    # -- evaluate / navigate --------------------------------------------------
    @staticmethod
    def _unwrap(grip):
        if isinstance(grip, dict) and "type" in grip:
            t = grip["type"]
            if t in ("boolean", "number", "string"):
                return grip.get("value")
            if t == "null":
                return None
            if t == "undefined":
                return None
            return grip
        return grip

    def _fetch_long_string(self, grip):
        """Fetch full text of an RDP longString grip via substring
        requests (ported from L1 l1_parent.py). Large evaluate results
        (innerText/outerHTML) arrive as longString grips, not text."""
        actor = grip.get("actor")
        length = grip.get("length", 0)
        parts = []
        pos = 0
        while pos < length:
            end = min(pos + 8000, length)
            self._send({"to": actor, "type": "substring",
                        "start": pos, "end": end})
            while True:
                m = self._recv()
                if m.get("from") == actor:
                    break
                if m.get("error"):
                    raise RDPError(f"substring error: {str(m)[:400]}")
            sub = m.get("substring", "")
            if isinstance(sub, dict):
                sub = sub.get("value", "")
            parts.append(sub)
            pos = end
        return "".join(parts)

    def _unwrap_full(self, grip):
        """_unwrap plus longString fetching (needs the live socket)."""
        if isinstance(grip, dict) and grip.get("type") == "longString":
            return self._fetch_long_string(grip)
        return self._unwrap(grip)

    def evaluate(self, expr, timeout=20):
        if not self.console_actor:
            raise RDPError("evaluate before attach (no console actor)")
        self._guard_current("evaluate")
        try:
            return self._evaluate_once(expr, timeout)
        except RDPError as e:
            if not _is_no_such_actor(str(e)):
                raise
            # Target swap killed the held consoleActor (RT-06): re-attach
            # pinned to the same tab and retry the evaluate once.
            self._reattach_pinned()
            self._retries += 1
            return self._evaluate_once(expr, timeout)

    def _evaluate_once(self, expr, timeout=20):
        self.sock.settimeout(timeout)
        self._send({"to": self.console_actor, "type": "evaluateJSAsync",
                    "text": expr})
        while True:
            m = self._recv()
            if m.get("type") == "evaluationResult":
                if m.get("exception"):
                    raise RDPError(f"evaluate exception: {str(m)[:400]}")
                self._actions["evaluate"] += 1
                return self._unwrap_full(m.get("result"))
            if m.get("error"):
                raise RDPError(f"evaluate error: {str(m)[:400]}")

    # -- parent-process target (chrome JS, gated) -----------------------------
    def _open_parent(self):
        """Resolve the parent-process console actor (cached).
        Path: listProcesses -> parentProcessTarget getTarget."""
        if self._parent_console:
            return
        procs = self.request({"to": "root", "type": "listProcesses"},
                             expect_from="root", expect_key="processes")
        plist = procs.get("processes") or []
        if not plist:
            raise RDPError(f"listProcesses returned none: {str(procs)[:400]}")
        parent = next((p for p in plist if p.get("isParent")), plist[0])
        self._parent_desc = parent.get("actor")
        tgt = self.request({"to": self._parent_desc, "type": "getTarget"},
                           expect_from=self._parent_desc)
        frame = tgt.get("frame") or tgt.get("target") \
            or tgt.get("process") or {}
        self._parent_console = frame.get("consoleActor")
        self.parent_url = frame.get("url")
        if not self._parent_console:
            raise RDPError(
                f"parent getTarget gave no consoleActor: {str(tgt)[:500]}")

    def parent_evaluate(self, expr, timeout=20):
        """Evaluate JS in the parent-process (chrome) target. Gated:
        requires allow_parent=True at construction (CLI --allow-parent).
        Every call is recorded in the drive report (count + first 80
        chars of the expression). Chrome JS bypasses tab scope by
        design; the gate + audit record are the fence."""
        if not self.allow_parent:
            raise RDPError(
                "PARENT EVALUATE REFUSED: parent-process evaluate "
                "requires allow_parent=True (CLI --allow-parent)")
        self._open_parent()
        self._parent_evals.append(
            {"expr_prefix": expr[:80], "at": _now_iso()})
        self.sock.settimeout(timeout)
        self._send({"to": self._parent_console, "type": "evaluateJSAsync",
                    "text": expr})
        while True:
            m = self._recv()
            if m.get("type") == "evaluationResult":
                if m.get("exception"):
                    raise RDPError(
                        f"parent evaluate exception: {str(m)[:400]}")
                self._actions["parent_evaluate"] += 1
                return self._unwrap_full(m.get("result"))
            if m.get("error"):
                raise RDPError(f"parent evaluate error: {str(m)[:400]}")

    def _navigate_send(self, url):
        """Send navigateTo via target actor, fallback descriptor actor."""
        last = None
        for actor in (self.target_actor, self.desc_actor):
            if not actor:
                continue
            try:
                self._internal_call = True
                try:
                    self.request({"to": actor, "type": "navigateTo",
                                  "url": url}, expect_from=actor)
                finally:
                    self._internal_call = False
                return
            except Exception as e:
                last = e
        raise RDPError(f"navigateTo failed for {_redact_url(url)}: {last}")

    def navigate(self, url):
        """navigateTo via target actor, fallback to descriptor actor.
        Navigation may replace the windowGlobalTarget, so re-attach after.
        Scope-gated on the current tab; denylist-gated on both the current
        URL and the destination URL."""
        self._guard_current("navigate")
        # Destination check: navigating INTO a credential URL is refused
        # the same way (approval keyed by the tab being navigated).
        if self.denylist_patterns:
            hit = next((p for p in self.denylist_patterns
                        if _url_matches(url, p)), None)
            if hit is not None:
                note = self._approval_note(self.desc_actor, url)
                if note is not None:
                    self._approvals_used.append(
                        {"op": "navigate-destination",
                         "tab_id": self.desc_actor, "url": url,
                         "pattern": hit, "note": note, "at": _now_iso()})
                else:
                    self._denylist_hits.append(
                        {"op": "navigate-destination",
                         "tab_id": self.desc_actor, "url": url,
                         "pattern": hit, "at": _now_iso()})
                    raise RDPError(
                        f"CREDENTIAL TAB REFUSED: navigate destination "
                        f"{_redact_url(url)!r} matches denylist pattern {hit!r}. Pass "
                        f"--allow-credential-tab {self.desc_actor} together "
                        f"with --approval-note <text> to approve explicitly.")
        try:
            self._navigate_send(url)
        except RDPError as e:
            if not _is_no_such_actor(str(e)):
                raise
            # Target swap killed the held actor (RT-06): re-attach
            # pinned to the same tab and retry the navigate once.
            self._reattach_pinned()
            self._retries += 1
            self._navigate_send(url)
        self._actions["navigate"] += 1
        time.sleep(0.05)
        try:
            self.list_tabs()
            self.get_target()
        except Exception:
            pass  # wait_load re-attaches as needed

    def wait_for(self, expr, timeout, poll_interval=0.1):
        """Poll evaluate(expr) until truthy or timeout (I17).

        No default timeout at the CLI layer: the caller names the
        budget. Transient evaluate errors (context destroyed
        mid-navigation) count as not-yet. Returns the truthy
        value. On expiry raises RDPError carrying the last
        observed value so the caller can report what the page
        actually showed."""
        deadline = time.monotonic() + timeout
        last = None
        while True:
            try:
                last = self.evaluate(expr, timeout=5)
            except Exception:
                last = None
            if last:
                return last
            if time.monotonic() >= deadline:
                raise RDPError(
                    f"wait_for timeout after {timeout}s: {expr!r} "
                    f"last value {last!r}")
            time.sleep(poll_interval)

    def wait_load(self, url_substr, timeout=30):
        deadline = time.monotonic() + timeout
        last_reattach = 0.0
        while time.monotonic() < deadline:
            try:
                v = self.evaluate(
                    "document.readyState + '|' + location.href", timeout=5)
            except Exception:
                v = None
            if isinstance(v, str) and v.startswith("complete|") \
                    and url_substr in v:
                return v
            # Stale target after navigation: refresh actors periodically.
            # Pinned re-attach when a tab is pinned (never selected-pick).
            if time.monotonic() - last_reattach > 1.0:
                last_reattach = time.monotonic()
                try:
                    if self._pinned_tab_id:
                        self._reattach_pinned()
                    else:
                        self.list_tabs()
                        self.get_target()
                except Exception:
                    pass
            time.sleep(0.05)
        raise RDPError(f"wait_load timeout for {url_substr!r}")

    def probe_webdriver(self):
        """Small evaluates (short grips). Raises RDPError unless native false."""
        wd = self.evaluate("navigator.webdriver")
        typ = self.evaluate("typeof navigator.webdriver")
        getter = self.evaluate(
            "Object.getOwnPropertyDescriptor("
            "Object.getPrototypeOf(navigator),'webdriver').get.toString()")
        doc_attr = self.evaluate(
            "document.documentElement ? "
            "String(document.documentElement.getAttribute('webdriver')) : 'none'")
        plugins = self.evaluate("navigator.plugins ? navigator.plugins.length : -1")
        globals_found = self.evaluate(
            "['cdc_adoQpoasnfa76pfcZLmcfl_Array','__webdriver_evaluate',"
            "'__driver_evaluate','__webdriver_script_fn']"
            ".filter(k => k in window).join(',')")
        probe = {
            "webdriver": wd, "webdriver_type": typ, "getter_tostring": getter,
            "doc_webdriver_attr": doc_attr, "plugins_length": plugins,
            "automation_globals": globals_found,
        }
        native = isinstance(getter, str) and getter.startswith(
            "function webdriver()")
        if wd is not False or typ != "boolean" or not native:
            self._probe_result = {**probe, "verdict": "NOT_CLEAN"}
            raise RDPError(
                f"webdriver probe NOT clean (fail-loud): {json.dumps(probe)}")
        probe["verdict"] = "CLEAN"
        self._probe_result = probe
        return probe

    # -- drive report ---------------------------------------------------------
    def drive_report(self):
        """Build the RT-20 drive report dict (probe, tab diff, scope,
        denylist hits, approvals, action counts). Best-effort: probe and
        final tab list failures are recorded, not raised."""
        try:
            self.list_tabs()
        except Exception:
            pass
        # The attached target may be stale after a keyboard navigation;
        # refresh before probing (best-effort; scope refusals are recorded
        # by the probe error below, not raised here).
        try:
            self.get_target()
        except Exception:
            pass
        tabs_after = _tab_snapshot(self._tabs)
        tabs_before = self._tabs_before or []
        probe = self._probe_result
        if probe is None:
            try:
                probe = self.probe_webdriver()
            except Exception as e:
                probe = self._probe_result or {"error": str(e)}
        report = {
            "generated_at": _now_iso(),
            "session_started_at": self._started_at,
            "port": self.port,
            "scope": self.scope.to_dict(),
            "unscoped_test": self.unscoped_test,
            "denylist": {"enabled": bool(self.denylist_patterns),
                         "disabled_via_flag": self.denylist_disabled,
                         "patterns": list(self.denylist_patterns)},
            "parent_evaluates": list(self._parent_evals),
            "lock": {"file": self.lock_file,
                     "holder_pid": self._lock_holder_pid},
            "probe": probe,
            "tabs_before": tabs_before,
            "tabs_after": tabs_after,
            "tab_diff": _tab_diff(tabs_before, tabs_after),
            "denylist_hits": list(self._denylist_hits),
            "scope_refusals": list(self._scope_refusals),
            "approvals_used": list(self._approvals_used),
            "approvals_configured": dict(self.credential_approvals),
            "actions": dict(self._actions),
            "retries": self._retries,
        }
        # I22: no sensitive URL query values in report bytes.
        return _redact_report_urls(report)

    def write_drive_report(self, path=None):
        path = path or self.drive_report_path
        if not path:
            raise RDPError("no drive report path given")
        report = self.drive_report()
        with open(path, "w") as f:
            json.dump(report, f, indent=1)
        return report

    def close(self):
        if self.drive_report_path:
            try:
                self.write_drive_report()
            except Exception as e:
                print(f"WARNING: drive report write failed: {e}",
                      file=sys.stderr)
        try:
            sock = getattr(self, "sock", None)
            if sock is not None:
                sock.close()
        except Exception:
            pass
        self._release_lock()


def bench(port, marker, local_url, real_url, runs, scope=None,
          denylist_patterns=None, credential_approvals=None,
          allow_unmarked_test_attach=False, unscoped_test=False):
    # bench navigates the attached tab destructively (about:blank,
    # local, real URLs). It must never run against a real session
    # without the explicit throwaway opt-in.
    if not unscoped_test:
        raise RDPError(
            "BENCH REFUSED: bench navigates the attached tab "
            "destructively; pass --unscoped-test explicitly to run it "
            "(throwaway/test use only)")
    if marker:
        check_port_owner(port, marker)
    elif not allow_unmarked_test_attach:
        raise RDPError(
            "profile marker is required (fail-closed): pass "
            "--profile-marker <substring> so the port owner can be "
            "verified before attach")
    kw = {"scope": scope, "denylist_patterns": denylist_patterns,
          "credential_approvals": credential_approvals,
          "unscoped_test": True}
    out = {"port": port, "runs": runs,
           "scoped": bool(scope and scope.scoped)}
    # attach-to-first-evaluate: fresh connection each run
    xs = []
    for _ in range(runs):
        t0 = time.monotonic()
        c = RDPClient(port, **kw)
        c.attach()
        v = c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
        assert v == 2, f"1+1 gave {v!r}"
        c.close()
    out["attach_to_first_evaluate"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # held connection for the rest
    c = RDPClient(port, **kw)
    c.attach()
    out["probe"] = c.probe_webdriver()
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
    out["evaluate_trivial"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("document.querySelectorAll('*').length")
        xs.append(time.monotonic() - t0)
    out["evaluate_dom_read"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # navigate-to-load, local then real, alternating with about:blank
    for label, url, substr in (("navigate_local", local_url, "slice"),
                               ("navigate_real", real_url, "example")):
        xs = []
        for _ in range(runs):
            c.navigate("about:blank")
            c.wait_load("about:blank", timeout=15)
            t0 = time.monotonic()
            c.navigate(url)
            c.wait_load(substr, timeout=30)
            xs.append(time.monotonic() - t0)
        out[label] = {"url": _redact_url(url), "median_ms": ms(median(xs)),
                      "runs_ms": [ms(x) for x in xs]}
    c.close()
    return out


def _build_scope(args):
    """Merge --scope-config + CLI flags into (Scope, denylist, approvals).

    Denylist posture: ON by default (generic defaults). --scope-config
    credential_denylist_patterns override the defaults. --no-denylist
    disables explicitly (loud warning in main(), recorded in report).
    --use-default-denylist is accepted for compatibility (now default).
    """
    tab_ids, patterns, deny = [], [], None
    if args.scope_config:
        cfg = load_scope_config(args.scope_config)
        tab_ids += cfg["scope_tab_ids"]
        patterns += cfg["scope_url_patterns"]
        deny = cfg["credential_denylist_patterns"]
    tab_ids += list(args.scope_tab_id or [])
    patterns += list(args.scope_url_pattern or [])
    if getattr(args, "no_denylist", False) \
            and getattr(args, "use_default_denylist", False):
        raise RDPError(
            "--no-denylist and --use-default-denylist conflict; pass "
            "only one")
    if getattr(args, "no_denylist", False):
        deny = []
    elif not deny:
        deny = list(DEFAULT_CREDENTIAL_DENYLIST)
    approvals = {}
    if args.allow_credential_tab or args.approval_note:
        if not args.allow_credential_tab or not args.approval_note:
            raise RDPError(
                "--allow-credential-tab and --approval-note must be passed "
                "together (approval without a note is not an approval)")
        approvals = {t: args.approval_note for t in args.allow_credential_tab}
    return Scope(tab_ids, patterns), deny, approvals


def main():
    ap = argparse.ArgumentParser(
        description="RDP client with RT-20 tab scoping")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", default=None,
                    help="substring required in the listening pid cmdline "
                         "(required for attach; fail-closed)")
    ap.add_argument("--allow-unmarked-test-attach", action="store_true",
                    help="TEST ONLY: skip the port-owner marker check "
                         "(throwaway/test use; never for a real session)")
    ap.add_argument("--scope-tab-id", action="append", default=[],
                    help="allowed tab descriptor id (repeatable)")
    ap.add_argument("--scope-url-pattern", action="append", default=[],
                    help="allowed URL glob pattern (repeatable)")
    ap.add_argument("--scope-config", default=None,
                    help="JSON file: scope_tab_ids, scope_url_patterns, "
                         "credential_denylist_patterns")
    ap.add_argument("--use-default-denylist", action="store_true",
                    help="enable the generic credential denylist patterns "
                         "(now the default; kept for compatibility)")
    ap.add_argument("--no-denylist", action="store_true",
                    help="DISABLE the credential denylist (loud warning; "
                         "recorded in the drive report)")
    ap.add_argument("--unscoped-test", action="store_true",
                    help="allow an UNSCOPED session (throwaway/test use "
                         "only; loud warning; recorded in drive report). "
                         "Without a scope and without this flag the CLI "
                         "refuses to attach.")
    ap.add_argument("--allow-parent", action="store_true",
                    help="allow parent-process (chrome JS) evaluate via "
                         "the peval subcommand (recorded in report)")
    ap.add_argument("--lock-file", default=None,
                    help="single-drive lock file (flock for the session; "
                         "second client refused). Default: RDP_LOCK_FILE "
                         "env or none. Owner drives must set this.")
    ap.add_argument("--allow-credential-tab", action="append", default=[],
                    help="tab id approved past the denylist (repeatable; "
                         "requires --approval-note)")
    ap.add_argument("--approval-note", default=None,
                    help="reason recorded for credential-tab approvals")
    ap.add_argument("--drive-report", default=None,
                    help="write the JSON drive report to this path")
    ap.add_argument("--tab-id", default=None,
                    help="attach to this tab descriptor id (full actor or "
                         "canonical tabDescriptorN; default: selected tab)")
    ap.add_argument("--tab-url", default=None,
                    help="attach to the tab whose URL contains this "
                         "substring (robust across connections)")
    ap.add_argument("--legacy-output", action="store_true",
                    help="pre-envelope output: bare JSON payload on "
                         "success, ERROR: text on stderr, exit 2 on "
                         "any error (compat shim for old consumers)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sub.add_parser("tabs")
    sub.add_parser("report")
    e = sub.add_parser("eval")
    e.add_argument("expr")
    pe = sub.add_parser("peval")
    pe.add_argument("expr")
    n = sub.add_parser("navigate")
    n.add_argument("url")
    for p in (e, n):
        p.add_argument("--wait-for", default=None, metavar="EXPR",
                       help="after the action, poll this JS expression "
                            "until truthy (I17). Requires "
                            "--wait-timeout; no default timeout")
        p.add_argument("--wait-timeout", type=float, default=None,
                       metavar="SECONDS",
                       help="budget for --wait-for (required with it)")
    b = sub.add_parser("bench")
    b.add_argument("--local-url", required=True)
    b.add_argument("--real-url", default="https://example.com/")
    b.add_argument("--runs", type=int, default=12)
    args = ap.parse_args()
    legacy = args.legacy_output
    args.wait_for = getattr(args, "wait_for", None)
    args.wait_timeout = getattr(args, "wait_timeout", None)
    if args.wait_for and args.wait_timeout is None:
        return _fail(args.cmd, "wait_timeout_required",
                     "--wait-for requires --wait-timeout SECONDS "
                     "(no default timeout by design)",
                     "not_delivered", "safe", 2, legacy)
    if args.wait_timeout is not None and args.wait_timeout <= 0:
        # I22: a wait budget must be positive; 0/negative are usage errors.
        return _fail(args.cmd, "wait_timeout_invalid",
                     f"--wait-timeout must be > 0 (got {args.wait_timeout}); "
                     "the wait budget must be positive",
                     "not_delivered", "safe", 2, legacy)
    try:
        try:
            scope, deny, approvals = _build_scope(args)
        except RDPError as e:
            # Scope/approval argument validation: usage-class.
            code, delivery, retry = _classify_error(str(e), args.cmd)
            return _fail(args.cmd, code, str(e), delivery, retry, 2,
                         legacy)
        if args.no_denylist:
            print(NO_DENYLIST_WARNING, file=sys.stderr)
        if not scope.scoped and not args.unscoped_test:
            return _fail(args.cmd, "unscoped_refused",
                         "UNSCOPED REFUSED: no tab scope was given. Pass "
                         "--scope-tab-id / --scope-url-pattern (or a "
                         "--scope-config), or pass --unscoped-test "
                         "explicitly for throwaway/test use.",
                         "not_delivered", "safe", 2, legacy)
        if not scope.scoped:
            print(UNSCOPED_WARNING, file=sys.stderr)
        if not args.profile_marker and not args.allow_unmarked_test_attach:
            return _fail(args.cmd, "profile_marker_required",
                         "profile marker is required (fail-closed): pass "
                         "--profile-marker <substring> so the port owner "
                         "can be verified before attach",
                         "not_delivered", "safe", 2, legacy)
        if args.allow_unmarked_test_attach and not args.profile_marker:
            print("WARNING: TEST-ONLY unmarked attach: port-owner marker "
                  "check skipped. Never use this against a real session.",
                  file=sys.stderr)
        kw = {"scope": scope, "denylist_patterns": deny,
              "credential_approvals": approvals,
              "drive_report_path": args.drive_report,
              "warn_unscoped": False,  # main() already warned loudly
              "unscoped_test": args.unscoped_test,
              "allow_parent": args.allow_parent,
              "lock_file": args.lock_file,
              "denylist_disabled": args.no_denylist}
        if args.cmd == "bench":
            _emit(args.cmd, bench(args.port, args.profile_marker,
                                  args.local_url, args.real_url,
                                  args.runs, scope=scope,
                                  denylist_patterns=deny,
                                  credential_approvals=approvals,
                                  allow_unmarked_test_attach=
                                  args.allow_unmarked_test_attach,
                                  unscoped_test=args.unscoped_test),
                  legacy)
            return 0
        if args.profile_marker:
            pid, _ = check_port_owner(args.port, args.profile_marker)
            print(json.dumps({"port_owner_pid": pid}), file=sys.stderr)
        c = RDPClient(args.port, **kw)
        try:
            if args.cmd == "tabs":
                tabs, sel = c.list_tabs()
                _emit(args.cmd, {"tabs": _tab_snapshot(tabs),
                                 "selected_index": sel}, legacy)
                if args.drive_report:
                    c.write_drive_report()
                return 0
            c.attach(args.tab_id, args.tab_url)
            action_result = None
            if args.cmd == "probe":
                _emit(args.cmd, c.probe_webdriver(), legacy)
            elif args.cmd == "eval":
                action_result = {"result": c.evaluate(args.expr)}
                if not args.wait_for:
                    _emit(args.cmd, action_result, legacy)
            elif args.cmd == "peval":
                _emit(args.cmd, {"result": c.parent_evaluate(args.expr)},
                      legacy)
            elif args.cmd == "navigate":
                c.navigate(args.url)
                action_result = {"navigated": _redact_url(args.url)}
                if not args.wait_for:
                    _emit(args.cmd, action_result, legacy)
            elif args.cmd == "report":
                report = c.drive_report()
                if args.drive_report:
                    with open(args.drive_report, "w") as f:
                        json.dump(report, f, indent=1)
                _emit(args.cmd, report, legacy)
                c.drive_report_path = None  # already written; avoid rewrite
            if args.wait_for and action_result is not None:
                try:
                    waited = c.wait_for(args.wait_for, args.wait_timeout)
                except RDPError as e:
                    # Preserve the action's own outcome in result.
                    code, delivery, retry = _classify_error(
                        str(e), args.cmd)
                    return _fail(args.cmd, code, str(e), delivery,
                                 retry, 1, legacy,
                                 result={"action_result": action_result,
                                         "wait": {"status": "timeout",
                                                  "expr": args.wait_for}})
                action_result["wait"] = {"status": "satisfied",
                                         "expr": args.wait_for,
                                         "value": waited}
                _emit(args.cmd, action_result, legacy)
            return 0
        finally:
            c.close()
    except RDPError as e:
        code, delivery, retry = _classify_error(str(e), args.cmd)
        return _fail(args.cmd, code, str(e), delivery, retry, 1, legacy)
    except Exception as e:
        action = args.cmd not in _READ_COMMANDS
        return _fail(args.cmd, "unexpected",
                     f"unexpected {type(e).__name__}: {e}",
                     "delivery_uncertain" if action else "not_delivered",
                     "unsafe" if action else "safe", 1, legacy)


if __name__ == "__main__":
    sys.exit(main())

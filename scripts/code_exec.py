#!/usr/bin/env python3
"""Code execution as the action (Track 2, Pick 1, M1).

One short program per model call, written by the model at runtime, run in a
persistent local Python interpreter on the laptop. A program may call only
the allowlisted API below, plus loops, conditions, and asserts in plain
Python. It may not import anything, run shell commands, touch the network,
or write files outside the task target path. Every program must end with an
executable verification (an assert on the postcondition), and a GUI fallback
when code cannot do it.

Safety invariants, unchanged from the normal loop:
- Ownership, lease, generation, cancellation (cancel latch, check_cancel,
  idle timeout), and explicit finish stay exactly as they are. The
  interpreter never bypasses them: check_cancel runs before every API call
  and inside the execution trace, and a cancelled run raises.
- Verification stays: the final state is verified from an exact source
  (file bytes, DOM text, a11y flags) plus a final observation image, never
  from the program asserting its own success alone. assert_state checks a
  value the program read back through read_file or observe, it does not
  prove anything by itself.
- Brokered keyboard input stays: typing goes through the existing wtype
  path in desktop_act, never through a direct write, AT-SPI setter,
  clipboard injection, or browser fill that skips the broker. act() calls
  desktop_act with the same validation as the normal act command.
- The pointer miss check (over 3px refuses the click) and the screen-changed
  refusal stay: act() is desktop_act, so both still apply. A program may
  not disable them.

Allowlisted API (the only names a program may call):
- windows() -> list of {address, class, title, at, size, workspace}
- observe(window=None, screen=None, crop=None, max_width=960) -> compact
  observation dict {id, image, observation, window, window_bounds,
  image_size, region, monitor}. The id binds the observation; act() only
  accepts an observation dict this interpreter delivered in this session.
- act(actions, observation=None) -> desktop_act result dict. actions use
  the same schema validate_actions enforces (1..32 items). observation
  defaults to the most recent observation in this program run. A refusal
  dict is returned to the program (it may re-observe and retry); it does
  not raise.
- dom_start() -> browser start dict; dom_tabs() -> page target list.
  dom_start() waits, bounded to DOM_WINDOW_WAIT_SECONDS, for the managed
  Chromium window to appear in windows() before returning: browser_start
  returns once CDP answers, but the Wayland window can map later, and a
  program that looks the window up immediately after dom_start() would
  IndexError. The wait polls windows() directly, costs no API-call
  budget, and fails closed if the window never appears.
- dom_observe(target, scope=None, max_elements=80) -> compact DOM snapshot
  dict. The snapshot id binds its target and refs for 120 seconds.
- dom_act(snapshot, actions, after_scope=None) -> CDP result dict. Refs must
  come from the supplied snapshot; successful after snapshots are bound too.
- dom_assert(snapshot, ref=None, selector=None, text=None, value=None,
  checked=None, timeout_ms=1000) -> True or raises AssertionError.
- run_snippet(name, **params) executes one verified registry program inline
  under these same budgets (shared api_calls, deadline, trace counter).
  Registry: scripts/snippets/manifest.json; each entry carries the sha256
  of its file bytes plus the sha256 of the code_exec.py bytes it was
  verified against. Params bind as frame locals, never interpolated.
- read_file(path, max_bytes=65536) -> str, only under /tmp, regular file,
  no symlink escape. Used for exact-source verification.
- assert_state(condition, message="assert failed") -> raises AssertionError
- assert_file_contains(path, text) / assert_file_exists(path)

Sandbox guard: AST scan before execution rejects imports, dunder access,
eval/exec/open/__import__, attribute access outside a small safe whitelist,
and any name outside the allowlist plus safe builtins. Execution runs with
restricted builtins, a wall-clock budget (default 30s, max 60s), an API-call
budget (default 32), and a trace step budget (20000 executed program
lines; lines inside API implementations do not count).
A program that tries any banned construct fails closed with no side effect
beyond API calls already made, and the failure is returned as a result
envelope so the supervisor can replan from the partial result.

Isolation: this pick is behind an explicit opt-in flag, default OFF.
Enabled only when CU_CODE_EXEC=1 (or true/yes). cu.py refuses the
code-exec command while the flag is off, and measurement enables exactly
this flag and no other pick.

State: user variables that are JSON-serializable (str, number, bool, None,
list, dict) persist across code-exec calls in the same session, in a mode
0600 file under STATE named code-exec-<token>.json. Desktop observation and
DOM snapshot bindings are kept in the same file but expire after 120s.

Template rule: see improvements/pick1-program-template.md. Observe after
act() and before file asserts. For shell printf text, use one single-quoted
argument and write \\n between output lines in the Python source.
"""
import ast
import copy
import difflib
import hashlib
import json
import logging
import math
import os
import re
import select
import signal
import socket
import sys
import time
from datetime import date
from pathlib import Path

try:
    import element_ref
except ImportError:  # loaded by file path without the scripts dir on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import element_ref

MAX_PROGRAM_CHARS = 8192
MAX_WALL_SECONDS = 60
DEFAULT_WALL_SECONDS = 30
MAX_API_CALLS = 32
MAX_TRACE_STEPS = 20000
PROGRAM_FILENAME = '<code-exec>'
MAX_READ_BYTES = 65536
MAX_ENVELOPE_BYTES = 65536
OBSERVATION_MAX_AGE = 120
MAX_OBSERVATIONS = 32
MAX_DOM_SNAPSHOTS = 32
MAX_SNIPPET_MANIFEST_BYTES = 1024 * 1024
MAX_SNIPPET_ENTRIES = 128
MAX_SNIPPET_LEDGER_ENTRIES = 128
MAX_SNIPPET_FILE_BYTES = MAX_PROGRAM_CHARS * 4
SNIPPET_STALE_DAYS_LIVE = 30
SNIPPET_STALE_DAYS_DEFAULT = 90
DOM_WINDOW_CLASS = 'chromium'
DOM_WINDOW_WAIT_SECONDS = 10.0
DOM_WINDOW_POLL_INTERVAL = 0.2
ASSERT_POLL_SECONDS = 2.0
ASSERT_POLL_INTERVAL = 0.1
READ_ROOT = Path('/tmp')

SAFE_BUILTINS = {
    'True': True, 'False': False, 'None': None,
    'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
    'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
    'range': range, 'enumerate': enumerate, 'zip': zip,
    'min': min, 'max': max, 'sum': sum, 'abs': abs,
    'sorted': sorted, 'reversed': reversed, 'isinstance': isinstance,
    'round': round, 'chr': chr, 'ord': ord,
}
# print is captured into the result log, never written to real stdout.
SAFE_ATTRIBUTE_NAMES = {
    'get', 'keys', 'values', 'items',
    'startswith', 'endswith', 'strip', 'split', 'join', 'lower', 'upper',
    'replace', 'count', 'find', 'index',
    'append', 'extend', 'pop', 'remove',
}
BANNED_NAMES = {
    '__import__', 'eval', 'exec', 'compile', 'open', 'input', 'globals',
    'locals', 'vars', 'getattr', 'setattr', 'delattr', 'hasattr',
    'breakpoint', 'memoryview', 'object', 'type', 'help', 'dir',
    'os', 'sys', 'subprocess', 'socket', 'pathlib', 'shutil', 'time',
    'json', 're', 'io', 'importlib', 'builtins', '__builtins__',
}
CODE_EXEC_API_NAMES = frozenset({
    'windows', 'observe', 'act', 'read_file', 'assert_state',
    'assert_file_contains', 'assert_file_exists', 'print',
    'dom_start', 'dom_tabs', 'dom_observe', 'dom_act', 'dom_assert',
    'run_snippet',
})
SNIPPET_RESERVED_PARAM_NAMES = CODE_EXEC_API_NAMES | {'name', 'allow_stale'}
SNIPPET_OPTIONAL_FIELDS = {
    'requires_approval', 'live_only', 'output',
}
SNIPPET_REQUIRED_FIELDS = {
    'name', 'file', 'sha256', 'description', 'params', 'source',
    'last_verified', 'api_sha256', 'expected_result', 'tags',
}
SNIPPET_PARAM_TYPES = {'string', 'integer', 'number', 'boolean',
                       'array', 'object', 'null'}
SNIPPET_ROOT = Path(__file__).resolve().parent / 'snippets'
SNIPPET_MANIFEST = SNIPPET_ROOT / 'manifest.json'
SNIPPET_NAME_RE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def is_enabled():
    """Opt-in flag for Pick 1, default OFF."""
    return os.environ.get('CU_CODE_EXEC', '').strip().lower() in ('1', 'true', 'yes')


def _is_jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, (list, tuple)):
        return all(_is_jsonable(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_jsonable(item)
                   for key, item in value.items())
    return False


def _jsonable_copy(value):
    if isinstance(value, dict):
        return {key: _jsonable_copy(item) for key, item in value.items()
                if isinstance(key, str) and _is_jsonable(item)}
    if isinstance(value, (list, tuple)):
        return [_jsonable_copy(item) for item in value]
    return value if _is_jsonable(value) else None


def _serialized_size(value):
    try:
        return len(json.dumps(value, ensure_ascii=False, separators=(',', ':'),
                              allow_nan=False).encode('utf-8'))
    except (TypeError, ValueError, OverflowError):
        return MAX_ENVELOPE_BYTES + 1


def _utf16_length(value):
    return len(value.encode('utf-16-le', 'surrogatepass')) // 2


def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _dom_modifier(key):
    return isinstance(key, str) and key.casefold() in {
        'ctrl', 'alt', 'shift', 'meta', 'super',
    }


def _dom_key_supported(key):
    if not isinstance(key, str):
        return False
    if re.fullmatch(
            r'(?:ctrl|alt|shift|meta|super|Enter|Tab|Escape|Back[Ss]pace|Delete|'
            r'Arrow(?:Left|Right|Up|Down)|Home|End|PageUp|PageDown|space)', key):
        return True
    return (_utf16_length(key) == 1
            and key not in ('\n', '\r', '\u2028', '\u2029'))


def _validate_dom_actions(actions, refs, snapshot_id=None, target=None):
    """Mirror cdp.mjs action preflight before any CDP request is made.

    When snapshot_id and target are given (the _api_dom_act path),
    CB-2 also applies: every action must carry scope +
    observation_id bound to this snapshot (scope == target,
    observation_id == snapshot_id). Direct test-only calls pass
    neither, so only the shape checks run there. The binding check
    runs AFTER the shape loop, so a malformed action still reports
    its shape error first (a non-string ref must say 'ref must
    be', not 'missing scope').
    """
    allowed = {'click', 'confirm_click', 'hover_click', 'fill', 'set_value', 'focus', 'key', 'scroll', 'wait', 'assert'}
    element_actions = {'click', 'confirm_click', 'hover_click', 'fill', 'set_value', 'focus', 'assert'}
    if not isinstance(actions, list) or not 1 <= len(actions) <= 32:
        raise CodeExecError('actions must contain 1..32 items')
    for action in actions:
        if not isinstance(action, dict):
            raise CodeExecError('each action must be an object')
        action_type = action.get('type')
        if not isinstance(action_type, str):
            raise CodeExecError('type must be a string')
        if action_type not in allowed:
            raise CodeExecError('unsupported action')
        if action_type in element_actions:
            if ('ref' in action) == ('selector' in action):
                raise CodeExecError('exactly one ref or selector required')
            for name in ('ref', 'selector'):
                if name in action:
                    value = action[name]
                    if not isinstance(value, str) or not value.strip():
                        raise CodeExecError(name + ' must be a non-empty string')
            if 'ref' in action and action['ref'] not in refs:
                raise CodeExecError('ref is not present in the bound snapshot; observe again')
        if action_type == 'confirm_click':
            for name, limit in (('expected_role', 64), ('expected_name', 120),
                                ('expected_text', 256)):
                value = action.get(name)
                if (not isinstance(value, str) or not value.strip()
                        or _utf16_length(value) > limit):
                    raise CodeExecError(
                        'confirm_click requires expected_role, expected_name and expected_text')
        if action_type == 'hover_click' and 'hover_timeout_ms' in action:
            timeout = action['hover_timeout_ms']
            if not _finite_number(timeout) or timeout < 0 or timeout > 2000:
                raise CodeExecError('hover_timeout_ms must be 0..2000')
        if action_type in ('fill', 'set_value'):
            value = action.get('text')
            if not isinstance(value, str) or _utf16_length(value) > 10000:
                raise CodeExecError('text must be string <=10000 chars')
        if action_type == 'key':
            keys = action.get('keys')
            if (not isinstance(keys, list) or not keys
                    or any(not isinstance(key, str) or _utf16_length(key) >= 40
                           for key in keys)):
                raise CodeExecError('keys must be an array of key names')
            if all(_dom_modifier(key) for key in keys):
                raise CodeExecError('key action needs a non-modifier key')
            if any(not _dom_key_supported(key) for key in keys):
                raise CodeExecError('unsupported key')
        if action_type == 'scroll':
            for name in ('dx', 'dy', 'x', 'y'):
                if name in action and not _finite_number(action[name]):
                    raise CodeExecError('scroll ' + name + ' must be a finite number')
            if 'dy' not in action or not _finite_number(action['dy']):
                raise CodeExecError('scroll dy required')
        if action_type == 'wait':
            ms = action.get('ms')
            if ms is None:
                ms = 100
            if not _finite_number(ms) or ms < 0 or ms > 2000:
                raise CodeExecError('wait ms must be 0..2000')
    if snapshot_id is not None and target is not None:
        for index, action in enumerate(actions):
            try:
                element_ref.validate_action_binding(
                    action, snapshot_id=snapshot_id, scope=target,
                    index=index)
            except element_ref.ElementRefError as exc:
                raise CodeExecError(str(exc)) from exc
        if action_type == 'assert':
            if 'value' in action and not isinstance(action['value'], str):
                raise CodeExecError('assert value must be a string')
            if 'text' in action and not isinstance(action['text'], str):
                raise CodeExecError('assert text must be a string')
            if 'checked' in action and not isinstance(action['checked'], bool):
                raise CodeExecError('assert checked must be a boolean')
            if 'timeout_ms' in action:
                timeout = action['timeout_ms']
                if not _finite_number(timeout) or timeout < 0:
                    raise CodeExecError(
                        'assert timeout_ms must be a non-negative finite number')


class CodeExecError(ValueError):
    """A program failed a sandbox, budget, or API guard. Fails closed."""


class SnippetRegistryError(CodeExecError):
    """The snippets manifest is malformed or unavailable."""


class _ApiChannel:
    """One end of the parent/child API channel (socketpair, length-prefixed JSON).

    The snippet runs in a forked child; every API call is marshalled to
    the parent, which executes it against the real backend and session
    state and returns the result. That keeps all backend interaction,
    observation binding, and session state in the parent process,
    exactly as if the snippet ran in-process, while the wall clock is
    still enforced by the parent killing the child.
    """

    def __init__(self, sock):
        self.sock = sock
        self.buf = b""

    def send(self, obj):
        data = json.dumps(obj).encode("utf-8")
        self.sock.sendall(len(data).to_bytes(4, "big") + data)

    def _try_parse(self):
        if len(self.buf) < 4:
            return None
        size = int.from_bytes(self.buf[:4], "big")
        if len(self.buf) < 4 + size:
            return None
        raw, self.buf = self.buf[4:4 + size], self.buf[4 + size:]
        return json.loads(raw.decode("utf-8"))

    def recv(self):
        while True:
            msg = self._try_parse()
            if msg is not None:
                return msg
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("api channel closed")
            self.buf += chunk

    def recv_deadline(self, deadline):
        while True:
            msg = self._try_parse()
            if msg is not None:
                return msg
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("wall-clock budget exceeded")
            ready, _, _ = select.select([self.sock], [], [], remaining)
            if not ready:
                raise TimeoutError("wall-clock budget exceeded")
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("api channel closed")
            self.buf += chunk


def _kill_child(pid):
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def _reap_child(pid):
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


_BUILTIN_EXCEPTIONS = {
    "ValueError": ValueError, "TypeError": TypeError,
    "RuntimeError": RuntimeError, "KeyError": KeyError,
    "IndexError": IndexError, "AttributeError": AttributeError,
    "OSError": OSError, "FileNotFoundError": FileNotFoundError,
    "PermissionError": PermissionError, "AssertionError": AssertionError,
}


def _exception_from_response(resp):
    """Rebuild the exception a parent-side API call raised, by name.

    Builtin names map to the real classes so a snippet's except clauses
    behave as they did in-process; unknown names get a dynamic class
    carrying the name, which is what the envelope reports anyway.
    """
    name = resp.get("type") or "Exception"
    message = resp.get("error") or ""
    if name == "CodeExecError":
        return CodeExecError(message)
    cls = _BUILTIN_EXCEPTIONS.get(name)
    if cls is None:
        if not name.isidentifier():
            return Exception(message)
        cls = type(name, (Exception,), {})
    return cls(message)


def _fork_api_session(work, wall_seconds, api_handler):
    """Run work(channel) in a forked child; the parent serves API calls.

    work receives an _ApiChannel; it runs the snippet with API stubs
    that marshal calls to the parent, and finishes by sending
    {"kind": "done", "envelope": {...}}. The parent executes each call
    via api_handler(name, args, kwargs) and returns the result. Returns
    (payload, status): "ok" with the child's envelope, "timeout" when
    the child was killed at the wall, "crashed" when it died without a
    done message, "refused" when the socketpair or fork failed. The
    child always ends with os._exit and never returns to caller code.

    A SIGALRM timer is the wrong tool here: the handler only runs when
    the interpreter regains the eval loop, so a C loop like
    sum(range(3 * 10**8)) burns to completion before the handler fires
    (measured: setitimer 1.0s, elapsed 31.48s). Only a parent-side kill
    binds C-level work.
    """
    try:
        parent_sock, child_sock = socket.socketpair()
    except OSError:
        return None, "refused"
    try:
        pid = os.fork()
    except OSError:
        parent_sock.close()
        child_sock.close()
        return None, "refused"
    if pid == 0:
        try:
            parent_sock.close()
            signal.signal(signal.SIGALRM, signal.SIG_DFL)
            signal.setitimer(signal.ITIMER_REAL, 0)
            work(_ApiChannel(child_sock))
        except BaseException:
            pass
        finally:
            os._exit(0)
    child_sock.close()
    channel = _ApiChannel(parent_sock)
    deadline = time.monotonic() + wall_seconds
    try:
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    _kill_child(pid)
                    return None, "timeout"
                try:
                    msg = channel.recv_deadline(deadline)
                except TimeoutError:
                    _kill_child(pid)
                    return None, "timeout"
                except EOFError:
                    _reap_child(pid)
                    return None, "crashed"
                if msg.get("kind") == "done":
                    _reap_child(pid)
                    return msg.get("envelope"), "ok"
                if msg.get("kind") == "api":
                    resp = api_handler(msg.get("name"), msg.get("args") or [],
                                       msg.get("kwargs") or {},
                                       msg.get("snippet_run") or 0)
                    try:
                        channel.send(resp)
                    except OSError:
                        _reap_child(pid)
                        return None, "crashed"
                    continue
                _reap_child(pid)
                return None, "crashed"
        except BaseException:
            _kill_child(pid)
            raise
    finally:
        parent_sock.close()


class _Validator(ast.NodeVisitor):
    """Reject every construct outside the allowlist before execution."""

    def __init__(self):
        self.allowed_names = set(SAFE_BUILTINS) | {
            'windows', 'observe', 'act', 'read_file', 'assert_state',
            'assert_file_contains', 'assert_file_exists', 'print',
            'dom_start', 'dom_tabs', 'dom_observe', 'dom_act', 'dom_assert',
            'run_snippet',
        }

    def visit_Import(self, node):
        raise CodeExecError('import is not allowed in a code-exec program')

    def visit_ImportFrom(self, node):
        raise CodeExecError('import is not allowed in a code-exec program')

    def visit_Global(self, node):
        raise CodeExecError('global is not allowed in a code-exec program')

    def visit_Nonlocal(self, node):
        raise CodeExecError('nonlocal is not allowed in a code-exec program')

    def visit_AsyncFunctionDef(self, node):
        raise CodeExecError('async is not allowed in a code-exec program')

    def visit_AsyncFor(self, node):
        raise CodeExecError('async is not allowed in a code-exec program')

    def visit_AsyncWith(self, node):
        raise CodeExecError('async is not allowed in a code-exec program')

    def visit_Await(self, node):
        raise CodeExecError('await is not allowed in a code-exec program')

    def visit_Yield(self, node):
        raise CodeExecError('yield is not allowed in a code-exec program')

    def visit_YieldFrom(self, node):
        raise CodeExecError('yield is not allowed in a code-exec program')

    def visit_Lambda(self, node):
        raise CodeExecError('lambda is not allowed in a code-exec program')

    def visit_Name(self, node):
        if node.id in BANNED_NAMES:
            raise CodeExecError('banned name: ' + node.id)
        if node.id.startswith('__'):
            raise CodeExecError('dunder access is not allowed')
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr.startswith('_'):
            raise CodeExecError('private attribute access is not allowed')
        if node.attr not in SAFE_ATTRIBUTE_NAMES:
            raise CodeExecError('attribute not allowlisted: ' + node.attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Name) and func.id in BANNED_NAMES:
            raise CodeExecError('banned call: ' + func.id)
        self.generic_visit(node)


def validate_program(source):
    """Parse and AST-check a program. Returns the tree, raises CodeExecError."""
    if not isinstance(source, str) or not source.strip():
        raise CodeExecError('program must be a non-empty string')
    if len(source) > MAX_PROGRAM_CHARS:
        raise CodeExecError('program exceeds %d chars' % MAX_PROGRAM_CHARS)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise CodeExecError('program syntax error: ' + str(exc)) from exc
    _Validator().visit(tree)
    return tree


def _resolve_read_path(path):
    if not isinstance(path, str) or not path:
        raise CodeExecError('read_file path must be a non-empty string')
    candidate = Path(path)
    if not candidate.is_absolute():
        raise CodeExecError('read_file path must be absolute')
    resolved = candidate.resolve()
    if resolved != READ_ROOT and READ_ROOT not in resolved.parents:
        raise CodeExecError('read_file is restricted to /tmp')
    return resolved


# ---------------------------------------------------------------- snippets
# Verified-snippet registry (Phase B, items 5-12). The manifest stores the
# sha256 of each snippet file plus the sha256 of the code_exec.py bytes the
# snippet was verified against (api_sha256, computed at runtime, never a
# git commit). run_snippet reads the file once, verifies the hash, and
# executes those bytes inline in the forked child. The loader reads text
# only and never imports a snippet file.

def _reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SnippetRegistryError('duplicate manifest JSON key: ' + str(key))
        result[key] = value
    return result


def _parameter_type_matches(value, type_name):
    if type_name == 'string':
        return isinstance(value, str)
    if type_name == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == 'number':
        return _finite_number(value)
    if type_name == 'boolean':
        return isinstance(value, bool)
    if type_name == 'array':
        return isinstance(value, list)
    if type_name == 'object':
        return isinstance(value, dict)
    if type_name == 'null':
        return value is None
    return False


def _api_surface_sha256():
    """Runtime-computed hash of this file's bytes (item 6).

    The stale check keys on this hash, never on a git commit. Fail closed
    when the bytes cannot be read.
    """
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except OSError as exc:
        raise SnippetRegistryError(
            'code_exec API surface hash cannot be computed: ' + str(exc)) from exc


def _registered_op_paths():
    """Read literal op paths from codemode without importing its module."""
    path = Path(__file__).resolve().parent / 'codemode.py'
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        raise SnippetRegistryError('could not validate op-name collisions') from exc
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not any(
                isinstance(target, ast.Name) and target.id == 'OPS'
                for target in node.targets):
            continue
        if not isinstance(node.value, ast.List):
            break
        paths = set()
        for item in node.value.elts:
            if not isinstance(item, ast.Dict):
                continue
            for key, value in zip(item.keys, item.values):
                if (isinstance(key, ast.Constant) and key.value == 'path'
                        and isinstance(value, ast.Constant)
                        and isinstance(value.value, str)):
                    paths.add(value.value)
        return paths
    raise SnippetRegistryError('codemode op paths could not be read')


def _resolve_snippet_path(entry, root=None):
    relative = entry.get('file')
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise SnippetRegistryError('snippet file must be a relative path under snippets/')
    candidate = Path(relative)
    if candidate.is_absolute() or '..' in candidate.parts:
        raise SnippetRegistryError('snippet file path must not be absolute or contain ..')
    try:
        base = (Path(root) if root is not None else SNIPPET_ROOT).resolve()
        resolved = (base / candidate).resolve()
    except (OSError, ValueError) as exc:
        raise SnippetRegistryError('snippet file path cannot be resolved') from exc
    if resolved != base and base not in resolved.parents:
        raise SnippetRegistryError('snippet file resolves outside snippets/')
    if resolved.suffix != '.py' or not resolved.is_file():
        raise SnippetRegistryError('snippet file is missing or is not a .py file')
    return resolved


def _validate_snippet_entry(raw, op_paths, root=None):
    if not isinstance(raw, dict):
        raise SnippetRegistryError('manifest entry must be an object')
    missing = SNIPPET_REQUIRED_FIELDS - set(raw)
    extra = set(raw) - SNIPPET_REQUIRED_FIELDS - SNIPPET_OPTIONAL_FIELDS
    if missing:
        raise SnippetRegistryError('missing fields: ' + ', '.join(sorted(missing)))
    if extra:
        raise SnippetRegistryError('unknown fields: ' + ', '.join(sorted(extra)))
    entry = dict(raw)
    name = entry['name']
    if not isinstance(name, str) or not SNIPPET_NAME_RE.fullmatch(name):
        raise SnippetRegistryError('name must be kebab-case')
    if name in CODE_EXEC_API_NAMES or name in op_paths or '.' in name:
        raise SnippetRegistryError('snippet name collides with an API or op path')
    if not isinstance(entry['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
        raise SnippetRegistryError('sha256 must be 64 lowercase hex characters')
    if not isinstance(entry['api_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', entry['api_sha256']):
        raise SnippetRegistryError('api_sha256 must be 64 lowercase hex characters')
    for field in ('description', 'source', 'expected_result'):
        value = entry[field]
        if not isinstance(value, str) or not value.strip() or '\n' in value or '\r' in value:
            raise SnippetRegistryError(field + ' must be a non-empty one-line string')
    if not isinstance(entry['tags'], list) or any(
            not isinstance(tag, str) or not tag.strip() for tag in entry['tags']):
        raise SnippetRegistryError('tags must be a list of non-empty strings')
    if len(set(entry['tags'])) != len(entry['tags']):
        raise SnippetRegistryError('tags must not contain duplicates')
    try:
        verified = date.fromisoformat(entry['last_verified'])
    except (TypeError, ValueError) as exc:
        raise SnippetRegistryError('last_verified must be YYYY-MM-DD') from exc
    if verified.isoformat() != entry['last_verified'] or verified > date.today():
        raise SnippetRegistryError('last_verified must be a valid date no later than today')
    if not isinstance(entry['params'], list):
        raise SnippetRegistryError('params must be a list')
    param_names = set()
    for param in entry['params']:
        if not isinstance(param, dict) or set(param) != {
                'name', 'type', 'required', 'default', 'description'}:
            raise SnippetRegistryError('each param needs name, type, required, default, description')
        param_name = param['name']
        if (not isinstance(param_name, str)
                or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', param_name)
                or param_name.startswith('__')):
            raise SnippetRegistryError('param name must be a plain Python identifier')
        if param_name in SNIPPET_RESERVED_PARAM_NAMES or param_name in op_paths:
            raise SnippetRegistryError('param name collides with an API name: ' + param_name)
        if param_name in param_names:
            raise SnippetRegistryError('duplicate param name: ' + param_name)
        param_names.add(param_name)
        if not isinstance(param['type'], str) or param['type'] not in SNIPPET_PARAM_TYPES:
            raise SnippetRegistryError('unsupported param type: ' + str(param['type']))
        if not isinstance(param['required'], bool):
            raise SnippetRegistryError('param required must be boolean')
        if not isinstance(param['description'], str) or not param['description'].strip() \
                or '\n' in param['description'] or '\r' in param['description']:
            raise SnippetRegistryError('param description must be a one-line string')
        if not _is_jsonable(param['default']):
            raise SnippetRegistryError('param default must be JSON-serializable')
        try:
            json.dumps(param['default'], allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise SnippetRegistryError('param default must be strict JSON data') from exc
        if param['default'] is not None and not _parameter_type_matches(
                param['default'], param['type']):
            raise SnippetRegistryError('param default does not match its type')
    output = entry.get('output')
    if output is not None and (not isinstance(output, str)
                               or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', output)
                               or output in SNIPPET_RESERVED_PARAM_NAMES):
        raise SnippetRegistryError('output must be a non-API Python identifier')
    if 'requires_approval' in entry and not isinstance(entry['requires_approval'], bool):
        raise SnippetRegistryError('requires_approval must be boolean')
    if 'live_only' in entry and not isinstance(entry['live_only'], bool):
        raise SnippetRegistryError('live_only must be boolean')
    _resolve_snippet_path(entry, root=root)
    return entry


def load_snippet_manifest(root=None):
    """Load metadata only. Invalid entries are skipped; duplicate names fail all."""
    manifest = (Path(root) if root is not None else SNIPPET_ROOT) / 'manifest.json'
    try:
        fd = os.open(manifest,
                     os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            import stat as _stat
            if not _stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise SnippetRegistryError('manifest must be a regular file')
            raw_bytes = stream.read(MAX_SNIPPET_MANIFEST_BYTES + 1)
    except OSError as exc:
        raise SnippetRegistryError('manifest unavailable: ' + str(exc)) from exc
    if len(raw_bytes) > MAX_SNIPPET_MANIFEST_BYTES:
        raise SnippetRegistryError('manifest exceeds 1MB size cap')
    try:
        data = json.loads(raw_bytes.decode('utf-8'), object_pairs_hook=_reject_duplicate_json_keys)
    except SnippetRegistryError:
        raise
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise SnippetRegistryError('manifest is malformed JSON: ' + str(exc)[:300]) from exc
    if not isinstance(data, dict) or set(data) != {'snippets'} \
            or not isinstance(data['snippets'], list):
        raise SnippetRegistryError('manifest must contain only a snippets list')
    raw_entries = data['snippets']
    if len(raw_entries) > MAX_SNIPPET_ENTRIES:
        raise SnippetRegistryError('manifest exceeds %d entries' % MAX_SNIPPET_ENTRIES)
    names = [entry.get('name') for entry in raw_entries if isinstance(entry, dict)
             and isinstance(entry.get('name'), str)]
    if len(names) != len(set(names)):
        duplicates = sorted(name for name in set(names) if names.count(name) > 1)
        raise SnippetRegistryError('duplicate snippet names: ' + ', '.join(duplicates))
    op_paths = _registered_op_paths()
    entries = []
    for index, raw in enumerate(raw_entries):
        try:
            entries.append(_validate_snippet_entry(raw, op_paths, root=root))
        except Exception as exc:
            logging.getLogger(__name__).warning(
                'skipping invalid snippet manifest entry %d: %s', index, exc)
    return entries


def _read_snippet_once(entry, root=None):
    """Read the snippet file once and verify its sha256. Returns source text."""
    path = _resolve_snippet_path(entry, root=root)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            import stat as _stat
            if not _stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise CodeExecError('snippet path is not a regular file')
            raw = stream.read(MAX_SNIPPET_FILE_BYTES + 1)
    except OSError as exc:
        raise CodeExecError('snippet file could not be read: ' + str(exc)) from exc
    if len(raw) > MAX_SNIPPET_FILE_BYTES:
        raise CodeExecError('snippet file exceeds program byte cap')
    digest = hashlib.sha256(raw).hexdigest()
    if digest != entry['sha256']:
        raise CodeExecError('snippet sha256 mismatch for %s' % entry['name'])
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise CodeExecError('snippet file is not valid UTF-8') from exc


def _snippet_params(entry, supplied):
    if not isinstance(supplied, dict):
        raise CodeExecError('snippet params must be an object')
    definitions = {param['name']: param for param in entry['params']}
    extra = set(supplied) - set(definitions)
    if extra:
        raise CodeExecError('unknown snippet params: ' + ', '.join(sorted(extra)))
    values = {}
    for name, param in definitions.items():
        if name in supplied:
            value = supplied[name]
        elif param['required']:
            raise CodeExecError('missing required snippet param: ' + name)
        else:
            value = param['default']
        if not _is_jsonable(value):
            raise CodeExecError('snippet param %s must be JSON-serializable' % name)
        try:
            json.dumps(value, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise CodeExecError('snippet param %s must be strict JSON data' % name) from exc
        if not _parameter_type_matches(value, param['type']):
            raise CodeExecError('snippet param %s must have type %s' % (name, param['type']))
        values[name] = _jsonable_copy(value)
    return values


def _snippet_age_days(entry):
    return (date.today() - date.fromisoformat(entry['last_verified'])).days


def _snippet_is_stale(entry):
    """Stale when the age limit passed OR the API surface hash moved.

    The hash check is keyed on the runtime-computed sha256 of the
    code_exec.py bytes (item 6); a mismatch means the snippet was
    verified against different executor code. Fail closed when the
    hash cannot be computed.
    """
    stale_days = SNIPPET_STALE_DAYS_LIVE if entry.get('live_only') else SNIPPET_STALE_DAYS_DEFAULT
    if _snippet_age_days(entry) > stale_days:
        return True
    return entry['api_sha256'] != _api_surface_sha256()


def search_snippets(root=None):
    """Return integrity-checked snippet metadata suitable for search.

    Stale entries are excluded (item 12a): past expiry means not
    offered. Entries whose file fails the hash check or the AST scan
    are hidden too. No code body is returned.
    """
    entries = load_snippet_manifest(root=root)
    results = []
    for entry in entries:
        try:
            if _snippet_is_stale(entry):
                continue
            source = _read_snippet_once(entry, root=root)
            validate_program(source)
        except (CodeExecError, OSError) as exc:
            logging.getLogger(__name__).warning(
                'hiding invalid snippet %s from search: %s', entry['name'], exc)
            continue
        result = {key: entry[key] for key in (
            'name', 'description', 'params', 'last_verified', 'tags')}
        result['stale'] = False
        result['requires_approval'] = entry.get('requires_approval', False)
        result['live_only'] = entry.get('live_only', False)
        results.append(result)
    return results


def describe_snippet(name, root=None):
    """Return one manifest entry without reading or returning its code body."""
    entries = load_snippet_manifest(root=root)
    for entry in entries:
        if entry['name'] == name:
            source = _read_snippet_once(entry, root=root)
            validate_program(source)
            return dict(entry)
    matches = difflib.get_close_matches(
        str(name), [entry['name'] for entry in entries], n=3, cutoff=0.3)
    suffix = '; closest matches: ' + ', '.join(matches) if matches else ''
    raise SnippetRegistryError('unknown snippet: ' + str(name) + suffix)


# Intent ledger for the CDP path (step-9 prototype, item 3): the
# JSON batch interface carries its exactly-once ledger in
# dom_act._sent_intents; the CDP path had none, so a retried
# program could double-send. _api_dom_act runs in the parent (API
# calls marshal back from the forked child), so this module-level
# set persists across run_program calls in one driver process and
# is checked and recorded there. A key is (target, intent): the
# same intent sent twice to the same target in one driver process
# is a double-send and refuses before any backend call. The ledger
# resets with the driver process (a new broker task starts empty),
# matching the per-session scope of the JSON ledger; it records
# only verified sends (result ok True), never a failed or
# unconfirmed attempt, so a failed send can be retried with the
# same intent. intent None means no ledger: programs run without
# one are not blocked. A batch with no send key is not protected.
_SENT_INTENTS = set()


def _snippet_globals(namespace):
    """Deep copy of the live namespace for one snippet run (items 9, 11d).

    API stubs and builtins are shared by reference (functions are atomic
    under deepcopy); plain variables are deep-copied, so a snippet's
    rebindings and in-place mutations cannot leak into the outer program.
    The snippet reads outer variables through this snapshot (probe 10e);
    only a declared output is copied back into the live namespace.
    """
    snapshot = {}
    for key, value in namespace.items():
        if key in ('__builtins__',) or callable(value):
            snapshot[key] = value
        else:
            snapshot[key] = copy.deepcopy(value)
    return snapshot


class CodeExecSession:
    """One interpreter session: persistent variables plus observation bindings.

    backend is an object with windows(), observe_window(address, crop,
    max_width), observe_screen(monitor, crop, max_width), and
    act(full_meta, actions, observation_path). check_cancel is a callable
    raising when the session was cancelled; it defaults to a no-op so unit
    tests can run without a live session.
    """

    def __init__(self, backend, state_dir=None, session_token=None,
                 check_cancel=None, wall_seconds=DEFAULT_WALL_SECONDS,
                 max_api_calls=MAX_API_CALLS, snippet_root=None):
        self.backend = backend
        self.state_dir = Path(state_dir) if state_dir is not None else None
        self.session_token = session_token
        self.snippet_root = Path(snippet_root) if snippet_root is not None else None
        self.check_cancel = check_cancel or (lambda: None)
        if not isinstance(wall_seconds, (int, float)) or not 1 <= wall_seconds <= MAX_WALL_SECONDS:
            raise CodeExecError('wall_seconds must be 1..%d' % MAX_WALL_SECONDS)
        if not isinstance(max_api_calls, int) or not 1 <= max_api_calls <= MAX_API_CALLS:
            raise CodeExecError('max_api_calls must be 1..%d' % MAX_API_CALLS)
        self.wall_seconds = wall_seconds
        self.max_api_calls = max_api_calls
        self.variables = {}
        self.observations = {}
        self.dom_snapshots = {}
        self.applied_snippets = {}
        self.approved_snippets = set()
        # Per-run binding scope (item 10): which snippet run created each
        # observation / DOM snapshot. Run id 0 is the outer program; each
        # run_snippet call gets a fresh id. In-memory only, never saved.
        self._observation_runs = {}
        self._dom_snapshot_runs = {}
        self._current_snippet_run = 0
        self.api_calls = 0
        self.log_lines = []
        self._deadline = None
        self._trace_steps = 0
        self._trace_events = 0
        self._load_state()

    def _state_path(self):
        if self.state_dir is None or not self.session_token:
            return None
        if not re.fullmatch(r'[0-9a-f]{32}', self.session_token):
            return None
        return self.state_dir / ('code-exec-' + self.session_token + '.json')

    def _load_state(self):
        path = self._state_path()
        if path is None or not path.is_file():
            return
        try:
            raw = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if not isinstance(raw, dict):
            return
        variables = raw.get('variables')
        if isinstance(variables, dict):
            self.variables = {k: v for k, v in variables.items()
                              if isinstance(k, str) and _is_jsonable(v)}
        observations = raw.get('observations')
        if isinstance(observations, dict):
            now = time.time()
            self.observations = {
                k: v for k, v in observations.items()
                if isinstance(v, dict) and isinstance(v.get('created'), (int, float))
                and now - v['created'] <= OBSERVATION_MAX_AGE}
            # Run ids are in-memory only: a loaded observation belongs to
            # no snippet run, so it is usable by the outer program only
            # (run id 0), never by a snippet. Prune stale run records.
            self._observation_runs = {
                k: v for k, v in self._observation_runs.items()
                if k in self.observations}
        dom_snapshots = raw.get('dom_snapshots')
        if isinstance(dom_snapshots, dict):
            now = time.time()
            self.dom_snapshots = {
                k: v for k, v in dom_snapshots.items()
                if isinstance(k, str) and isinstance(v, dict)
                and isinstance(v.get('target'), str)
                and isinstance(v.get('created'), (int, float))
                and now - v['created'] <= OBSERVATION_MAX_AGE
                and isinstance(v.get('refs'), list)
                and all(isinstance(ref, str) for ref in v['refs'])
                and isinstance(v.get('snapshot'), dict)
                and v['snapshot'].get('snapshot') == k}
            self._dom_snapshot_runs = {
                k: v for k, v in self._dom_snapshot_runs.items()
                if k in self.dom_snapshots}

    def _save_state(self):
        path = self._state_path()
        if path is None:
            return
        # B2: cap what is saved. Observations accumulate across runs in
        # one session (each run can add up to MAX_API_CALLS), and the old
        # code wrote all of them: 5 distinct observations, 1591 bytes,
        # no cap. Keep only the newest MAX_OBSERVATIONS (and the same cap
        # for DOM snapshots, the identical hazard in this function), in
        # memory and on disk, so the state file cannot grow without bound.
        if len(self.observations) > MAX_OBSERVATIONS:
            keep = sorted(self.observations.items(),
                          key=lambda item: item[1].get('created', 0))[-MAX_OBSERVATIONS:]
            self.observations = dict(keep)
            self._observation_runs = {
                k: v for k, v in self._observation_runs.items()
                if k in self.observations}
        if len(self.dom_snapshots) > MAX_DOM_SNAPSHOTS:
            keep = sorted(self.dom_snapshots.items(),
                          key=lambda item: item[1].get('created', 0))[-MAX_DOM_SNAPSHOTS:]
            self.dom_snapshots = dict(keep)
            self._dom_snapshot_runs = {
                k: v for k, v in self._dom_snapshot_runs.items()
                if k in self.dom_snapshots}
        try:
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            payload = {
                'variables': _jsonable_copy(self.variables),
                'observations': _jsonable_copy(self.observations),
                'dom_snapshots': _jsonable_copy(self.dom_snapshots),
            }
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
            try:
                os.fchmod(fd, 0o600)
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    stream.write(json.dumps(payload, ensure_ascii=False))
            except BaseException:
                try:
                    os.close(fd)
                except OSError:
                    pass
                raise
        except OSError:
            # State persistence is best effort; a failed save must not fail
            # a program that already ran.
            pass

    def _check_budgets(self):
        self.check_cancel()
        if self.api_calls > self.max_api_calls:
            raise CodeExecError('API call budget exceeded (%d)' % self.max_api_calls)
        if self._deadline is not None and time.monotonic() > self._deadline:
            raise CodeExecError('wall-clock budget exceeded (%.0fs)' % self.wall_seconds)

    def _trace(self, frame, event, arg):
        if event != 'line':
            return self._trace
        # Periodic cancel/wall-clock checks still run on every line event,
        # including lines inside API implementations, so a long API call
        # stays cancellable. Only the step *budget* is program-only.
        self._trace_events += 1
        if self._trace_events % 200 == 0:
            self._check_budgets()
        # Only the program's own lines count toward the step budget. A
        # single observe() executes ~190000 lines on a cold interpreter
        # (PIL first import) and ~7000-10000 warm (grim subprocess, PIL
        # decode/resize), so counting implementation lines blows the 20000
        # budget before act() ever runs. The API-call budget (32) and the
        # wall-clock budget already bound runaway API implementations.
        if frame.f_code.co_filename == PROGRAM_FILENAME:
            self._trace_steps += 1
            if self._trace_steps > MAX_TRACE_STEPS:
                raise CodeExecError('trace step budget exceeded (%d)' % MAX_TRACE_STEPS)
        return self._trace

    def _api(self, name, fn, *args, **kwargs):
        self.check_cancel()
        if self.api_calls >= self.max_api_calls:
            raise CodeExecError('API call budget exceeded (%d)' % self.max_api_calls)
        self.api_calls += 1
        result = fn(*args, **kwargs)
        self._check_budgets()
        return result

    def _compact_observation(self, meta):
        if not isinstance(meta, dict) or not meta.get('id'):
            raise CodeExecError('backend returned an observation without an id')
        self.observations[meta['id']] = meta
        # Item 10: remember which snippet run created this observation.
        self._observation_runs[meta['id']] = self._current_snippet_run
        return {
            'id': meta['id'],
            'scope': meta.get('scope'),
            'image': meta.get('image'),
            'observation': meta.get('observation'),
            'window': meta.get('window'),
            'window_bounds': meta.get('window_bounds'),
            'image_size': meta.get('image_size'),
            'region': meta.get('region'),
            'monitor': meta.get('monitor'),
        }

    def api_windows(self):
        return self._api('windows', self.backend.windows)

    def api_observe(self, window=None, screen=None, crop=None, max_width=960):
        if window is not None and screen is not None:
            raise CodeExecError('observe takes window or screen, not both')
        if crop is not None:
            if (not isinstance(crop, (list, tuple)) or len(crop) != 4
                    or not all(isinstance(v, int) for v in crop)):
                raise CodeExecError('crop must be four integers')
            crop = list(crop)
        if not isinstance(max_width, int) or not 320 <= max_width <= 3840:
            raise CodeExecError('max_width must be 320..3840')
        if window is not None:
            if not isinstance(window, str) or not window:
                raise CodeExecError('window must be a non-empty address string')
            meta = self._api('observe', self.backend.observe_window,
                             window, crop, max_width)
        elif screen is not None:
            if not isinstance(screen, str) or not screen:
                raise CodeExecError('screen must be a non-empty monitor name')
            meta = self._api('observe', self.backend.observe_screen,
                             screen, crop, max_width)
        else:
            raise CodeExecError('observe needs window or screen')
        return self._compact_observation(meta)

    def _bound_observation(self, observation):
        if observation is None:
            if not self.observations:
                raise CodeExecError('act needs an observation; call observe() first')
            # Item 10: the no-argument fallback binds to the newest
            # observation from THIS snippet run only. If observations
            # exist but none belongs to the current run, the error names
            # the per-run binding (probe 11e); a snippet must observe
            # for itself before it can act.
            same_run = [(key, meta) for key, meta in self.observations.items()
                        if self._observation_runs.get(key, 0) == self._current_snippet_run]
            if not same_run:
                raise CodeExecError('observation is not bound to this snippet run; observe again')
            return max((meta for _, meta in same_run),
                       key=lambda m: m.get('created', 0))
        if not isinstance(observation, dict) or not isinstance(observation.get('id'), str):
            raise CodeExecError('act observation must be an observation dict from observe()')
        meta = self.observations.get(observation['id'])
        if meta is None:
            raise CodeExecError('observation id is not bound to this session; observe again')
        # Item 10: an observation belongs to the snippet run that created
        # it. The outer program (run 0) cannot act on a snippet's
        # observation, a snippet cannot act on the outer program's, and a
        # snippet cannot act on another snippet's. Loaded observations
        # have no run record and default to run 0 (outer program only).
        if self._observation_runs.get(observation['id'], 0) != self._current_snippet_run:
            raise CodeExecError('observation is not bound to this snippet run; observe again')
        if time.time() - meta.get('created', 0) > OBSERVATION_MAX_AGE:
            raise CodeExecError('observation is older than 120s; observe again')
        return meta

    def api_act(self, actions, observation=None):
        if not isinstance(actions, list) or not actions:
            raise CodeExecError('act actions must be a non-empty list')
        meta = self._bound_observation(observation)
        # CB-2: scope + observation_id are mandatory in action
        # data, bound to the observation the batch is written
        # against. A program holds the observation dict, so it
        # stamps scope from obs['scope'] and observation_id from
        # obs['id']; an unstamped or mismatched action refuses
        # before any input.
        for index, action in enumerate(actions):
            try:
                element_ref.validate_action_binding(
                    action, snapshot_id=meta['id'],
                    scope=meta.get('scope'), index=index)
            except element_ref.ElementRefError as exc:
                raise CodeExecError(str(exc)) from exc
        result = self._api('act', self.backend.act, meta, actions,
                           meta.get('observation'))
        if not isinstance(result, dict):
            raise CodeExecError('backend act returned a non-dict result')
        return result

    def _dom_call(self, name, fn, *args, check_failure=True):
        try:
            result = self._api(name, fn, *args)
        except CodeExecError:
            raise
        except Exception as exc:
            self.check_cancel()
            raise CodeExecError(str(exc)[:400]) from exc
        if (check_failure and isinstance(result, dict)
                and result.get('ok') is False):
            raise CodeExecError(str(result.get('error') or (name + ' failed'))[:400])
        return result

    def _bind_dom_snapshot(self, target, snapshot):
        if not isinstance(snapshot, dict):
            raise CodeExecError('DOM snapshot must be a dict')
        snapshot_id = snapshot.get('snapshot')
        if not isinstance(snapshot_id, str) or not snapshot_id:
            raise CodeExecError('backend returned a DOM snapshot without an id')
        elements = snapshot.get('elements')
        if not isinstance(elements, list):
            raise CodeExecError('backend returned a DOM snapshot without elements')
        refs = [element['ref'] for element in elements
                if isinstance(element, dict) and isinstance(element.get('ref'), str)]
        self.dom_snapshots[snapshot_id] = {
            'target': target, 'created': time.time(), 'refs': refs,
            'snapshot': _jsonable_copy(snapshot),
        }
        # Item 10: same per-run scope as observations.
        self._dom_snapshot_runs[snapshot_id] = self._current_snippet_run
        return snapshot

    def _bound_dom_snapshot(self, snapshot):
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('snapshot'), str):
            raise CodeExecError('snapshot must be a DOM snapshot dict from dom_observe()')
        snapshot_id = snapshot['snapshot']
        binding = self.dom_snapshots.get(snapshot_id)
        if binding is None:
            raise CodeExecError('DOM snapshot id is not bound to this session; observe again')
        if self._dom_snapshot_runs.get(snapshot_id, 0) != self._current_snippet_run:
            raise CodeExecError('DOM snapshot is not bound to this snippet run; observe again')
        if snapshot != binding.get('snapshot'):
            raise CodeExecError('snapshot is not the bound DOM snapshot; observe again')
        if time.time() - binding.get('created', 0) > OBSERVATION_MAX_AGE:
            raise CodeExecError('DOM snapshot is older than 120s; observe again')
        if not isinstance(binding.get('target'), str) or not isinstance(binding.get('refs'), list):
            raise CodeExecError('DOM snapshot binding is invalid; observe again')
        return snapshot_id, binding

    def api_dom_start(self):
        result = self._dom_call('dom_start', self.backend.dom_start)
        if not isinstance(result, dict):
            raise CodeExecError('backend dom_start returned a non-dict result')
        if result.get('ok') is not True:
            raise CodeExecError(str(result.get('error') or 'browser start failed')[:400])
        self._wait_for_dom_window()
        return result

    def _wait_for_dom_window(self):
        """Wait for the managed browser window to appear in windows().

        browser_start returns once CDP answers, but the Wayland window can
        map later; without this wait the D1 program IndexErrors on the
        immediate windows() lookup after dom_start(). Polls go straight to
        backend.windows(), not through _api, so the wait costs no API-call
        budget. Cancellation and the wall-clock budget are checked every
        poll; a window that never appears fails closed with CodeExecError.
        The window class comes from the backend (DOM_WINDOW_CLASS):
        'chromium' for the CDP backend, 'zen' for the Zen adapter. The
        match is a case-insensitive prefix match, so 'zen' also matches
        a 'zen-beta' class and 'chromium' still matches exactly.
        """
        window_class = getattr(self.backend, 'DOM_WINDOW_CLASS',
                               DOM_WINDOW_CLASS)
        wanted = str(window_class).lower()
        deadline = time.monotonic() + DOM_WINDOW_WAIT_SECONDS
        while True:
            self.check_cancel()
            try:
                wins = self.backend.windows()
            except Exception as exc:
                self.check_cancel()
                raise CodeExecError(
                    'windows() failed while waiting for the managed '
                    'browser window: ' + str(exc)[:200]) from exc
            if isinstance(wins, list) and any(
                    isinstance(w, dict)
                    and isinstance(w.get('class'), str)
                    and w['class'].lower().startswith(wanted)
                    for w in wins):
                return
            if time.monotonic() >= deadline:
                raise CodeExecError(
                    'managed browser window (%s) did not appear within '
                    '%.0fs; observe windows() again'
                    % (window_class, DOM_WINDOW_WAIT_SECONDS))
            self._check_budgets()
            time.sleep(DOM_WINDOW_POLL_INTERVAL)

    def api_dom_tabs(self):
        result = self._dom_call('dom_tabs', self.backend.dom_tabs)
        if not isinstance(result, list):
            raise CodeExecError('backend dom_tabs returned a non-list result')
        return result

    def api_dom_observe(self, target, scope=None, max_elements=80):
        if not isinstance(target, str) or not target.strip():
            raise CodeExecError('target must be a non-empty string')
        if scope is not None:
            if not isinstance(scope, str) or not scope.strip():
                raise CodeExecError('scope must be a non-empty CSS selector')
            if _utf16_length(scope) > 1024:
                raise CodeExecError('scope must be at most 1024 UTF-16 code units')
        if (isinstance(max_elements, bool) or not isinstance(max_elements, int)
                or not 1 <= max_elements <= 80):
            raise CodeExecError('max_elements must be 1..80')
        result = self._dom_call('dom_observe', self.backend.dom_observe,
                                target, scope, max_elements)
        if not isinstance(result, dict):
            raise CodeExecError('backend dom_observe returned a non-dict result')
        return self._bind_dom_snapshot(target, result)

    def _api_dom_act(self, snapshot, actions, after_scope=None, no_after=False):
        snapshot_id, binding = self._bound_dom_snapshot(snapshot)
        if after_scope is not None:
            if not isinstance(after_scope, str) or not after_scope.strip():
                raise CodeExecError('after_scope must be a non-empty CSS selector')
            if _utf16_length(after_scope) > 1024:
                raise CodeExecError(
                    'after_scope must be at most 1024 UTF-16 code units')
            if no_after:
                raise CodeExecError('after_scope is incompatible with no_after')
        refs = set(binding['refs'])
        _validate_dom_actions(actions, refs, snapshot_id=snapshot_id,
                              target=binding['target'])
        # P5 (step 5): a send program (fill/set_value followed by
        # key Enter) must end with an assert action, the V12 gate
        # in program form. focus_check and type_check are
        # available by construction here (cdp.mjs enforces the
        # activeElement check on click and the read-back on
        # set_value internally); the bubble assert is not in the
        # adapter, so the program must carry it. A missing gate
        # raises here, before any CDP request, never after a send.
        try:
            import dom_asserts
        except ImportError:  # loaded by file path, scripts not on path
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import dom_asserts
        try:
            dom_asserts.require_asserts(
                actions,
                available={'focus_check': True, 'type_check': True,
                           'sent_bubble': False})
        except dom_asserts.DomAssertError as exc:
            raise CodeExecError(str(exc)) from exc
        # Intent ledger (step 9): a send program under a named
        # intent refuses when the same (target, intent) already
        # sent in this driver process. Checked after validation
        # (a malformed or unbound batch reports its own error
        # first) and before any backend call, so the refusal means
        # no second send went out.
        ledger_key = None
        if (dom_asserts.is_send_program(actions)
                and getattr(self, '_intent', None)):
            ledger_key = (binding['target'], self._intent)
            if ledger_key in _SENT_INTENTS:
                raise CodeExecError(
                    'intent %r already sent to %r in this session; '
                    'refusing a second send (exactly-once ledger)'
                    % (self._intent, binding['target']))
        if no_after:
            if not actions or actions[-1].get('type') != 'assert':
                raise CodeExecError('no_after requires a final assert action')
            last = actions[-1]
            if 'value' in last:
                meaningful = isinstance(last['value'], str)
            elif 'text' in last:
                meaningful = isinstance(last['text'], str) and bool(last['text'])
            elif 'checked' in last:
                meaningful = isinstance(last['checked'], bool)
            else:
                meaningful = False
            if not meaningful:
                raise CodeExecError('no_after final assert needs text, value or checked')
        result = self._dom_call('dom_act', self.backend.dom_act,
                                binding['target'], snapshot_id, actions,
                                after_scope, no_after, check_failure=False)
        if not isinstance(result, dict):
            raise CodeExecError('backend dom_act returned a non-dict result')
        if result.get('ok') is True and isinstance(result.get('after'), dict):
            self._bind_dom_snapshot(binding['target'], result['after'])
        # Record only a verified send: a failed or unconfirmed
        # attempt leaves the intent free for a retry.
        if result.get('ok') is True and ledger_key is not None:
            _SENT_INTENTS.add(ledger_key)
        return result

    def api_dom_act(self, snapshot, actions, after_scope=None):
        return self._api_dom_act(snapshot, actions, after_scope=after_scope)

    def api_dom_assert(self, snapshot, ref=None, selector=None, text=None,
                       value=None, checked=None, timeout_ms=1000):
        if ref is not None and not isinstance(ref, str):
            raise CodeExecError('ref must be a non-empty string')
        if selector is not None and not isinstance(selector, str):
            raise CodeExecError('selector must be a non-empty string')
        if text is not None and not isinstance(text, str):
            raise CodeExecError('text must be a string')
        if value is not None and not isinstance(value, str):
            raise CodeExecError('value must be a string')
        if checked is not None and not isinstance(checked, bool):
            raise CodeExecError('checked must be a boolean')
        if not _finite_number(timeout_ms) or timeout_ms < 0:
            raise CodeExecError('timeout_ms must be a non-negative finite number')
        if (ref is None) == (selector is None):
            raise CodeExecError('exactly one ref or selector required')
        predicates = [text is not None, value is not None, checked is not None]
        if sum(predicates) != 1:
            raise CodeExecError('exactly one of text, value or checked is required')
        action = {'type': 'assert', 'timeout_ms': timeout_ms}
        action['ref' if ref is not None else 'selector'] = (
            ref if ref is not None else selector)
        if text is not None:
            action['text'] = text
        if value is not None:
            action['value'] = value
        if checked is not None:
            action['checked'] = checked
        # CB-2: api_dom_assert builds this action itself, so the
        # session stamps scope + observation_id from the binding;
        # the program never writes them for this internal action.
        snapshot_id, binding = self._bound_dom_snapshot(snapshot)
        action['scope'] = binding['target']
        action['observation_id'] = snapshot_id
        result = self._api_dom_act(snapshot, [action], no_after=True)
        if result.get('ok') is not True:
            raise AssertionError(str(result.get('error') or 'DOM assertion failed'))
        return True

    def api_read_file(self, path, max_bytes=MAX_READ_BYTES):
        if not isinstance(max_bytes, int) or not 1 <= max_bytes <= MAX_READ_BYTES:
            raise CodeExecError('max_bytes must be 1..%d' % MAX_READ_BYTES)
        resolved = _resolve_read_path(path)
        try:
            fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        except OSError as exc:
            raise CodeExecError('read_file failed: ' + str(exc)) from exc
        with os.fdopen(fd, 'rb') as stream:
            import stat as _stat
            st = os.fstat(stream.fileno())
            if not _stat.S_ISREG(st.st_mode):
                raise CodeExecError('read_file needs a regular file')
            raw = stream.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise CodeExecError('read_file file exceeds max_bytes')
        return raw.decode('utf-8', 'replace')

    def api_assert_state(self, condition, message='assert failed'):
        if not condition:
            raise AssertionError(str(message) if isinstance(message, str) else 'assert failed')
        return True

    def _poll_file(self, check):
        deadline = time.monotonic() + ASSERT_POLL_SECONDS
        while True:
            self._check_budgets()
            try:
                if check():
                    return True
            except CodeExecError as exc:
                if not isinstance(exc.__cause__, FileNotFoundError):
                    raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(ASSERT_POLL_INTERVAL, remaining))

    def api_assert_file_contains(self, path, text):
        if not isinstance(text, str):
            raise CodeExecError('assert_file_contains text must be a string')
        resolved = _resolve_read_path(path)
        if not self._poll_file(lambda: text in self.api_read_file(path)):
            if not resolved.is_file():
                raise AssertionError('file does not exist: ' + path)
            raise AssertionError('file %s does not contain %r' % (path, text[:80]))
        return True

    def api_assert_file_exists(self, path):
        resolved = _resolve_read_path(path)
        if not self._poll_file(lambda: resolved.exists()):
            raise AssertionError('file does not exist: ' + path)
        return True

    def api_run_snippet(self, name, allow_stale=False, params=None):
        """Parent-side fetch: verify the registry entry and return its bytes.

        This runs in the parent (the trust boundary). It costs one API
        call through _api, like every other API call, so the fetch itself
        shares the outer budget. It returns the verified source; the child
        executes it inline (see the run_snippet stub in run()).
        """
        return self._api('run_snippet', self._fetch_snippet,
                         name, params or {}, allow_stale)

    def _fetch_snippet(self, name, supplied_params, allow_stale=False):
        if not isinstance(name, str):
            raise CodeExecError('snippet name must be a string')
        if not isinstance(allow_stale, bool):
            raise CodeExecError('allow_stale must be boolean')
        entries = load_snippet_manifest(root=self.snippet_root)
        entry = next((item for item in entries if item['name'] == name), None)
        if entry is None:
            matches = difflib.get_close_matches(
                name, [item['name'] for item in entries], n=3, cutoff=0.3)
            suffix = '; closest matches: ' + ', '.join(matches) if matches else ''
            raise CodeExecError('unknown snippet: ' + name + suffix)
        params = _snippet_params(entry, supplied_params)
        if entry.get('requires_approval') and name not in self.approved_snippets:
            raise CodeExecError('snippet requires approval: ' + name)
        age_days = _snippet_age_days(entry)
        stale_days = SNIPPET_STALE_DAYS_LIVE if entry.get('live_only') else SNIPPET_STALE_DAYS_DEFAULT
        stale = age_days > stale_days
        if not stale:
            try:
                stale = entry['api_sha256'] != _api_surface_sha256()
            except SnippetRegistryError:
                raise CodeExecError(
                    'snippet is stale: %s API surface hash cannot be computed; refusing' % name)
        if stale and not allow_stale:
            raise CodeExecError(
                'snippet is stale: %s last_verified=%s age=%d days; '
                'allow_stale=True is diagnostic only'
                % (name, entry['last_verified'], age_days))
        if stale:
            line = 'run_snippet stale override: %s age=%d days' % (name, age_days)
            self.log_lines.append(line)
            logging.getLogger(__name__).warning(line)
        params_hash = hashlib.sha256(json.dumps(
            params, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
            allow_nan=False).encode('utf-8')).hexdigest()
        # Item 12: the applied-snippet ledger guards NON-IDEMPOTENT
        # snippets (requires_approval). A blanket ledger would block
        # deliberate repetition of an idempotent snippet and break probe
        # 10a (the same snippet called 5 times in a loop must trip the
        # API budget, not the ledger), so idempotent entries are not
        # ledgered. The child records only when the fetch says so.
        ledgered = bool(entry.get('requires_approval'))
        ledger_key = name + ':' + params_hash
        if ledgered and ledger_key in self.applied_snippets:
            raise CodeExecError('snippet already applied for these parameters: ' + name)
        if ledgered and len(self.applied_snippets) >= MAX_SNIPPET_LEDGER_ENTRIES:
            raise CodeExecError('applied snippet ledger is full; refusing to act')
        source = _read_snippet_once(entry, root=self.snippet_root)
        validate_program(source)
        return {'source': source, 'sha256': entry['sha256'],
                'output': entry.get('output'), 'stale': stale,
                'ledger_key': ledger_key, 'params_hash': params_hash,
                'ledger': ledgered, 'params': params}

    def _record_snippet_result(self, key, name, params_hash, result):
        """Record a SUCCESSFUL snippet application (item 12).

        Only ledgered (requires_approval, non-idempotent) snippets are
        recorded, and only verified applications, never a failed or
        unconfirmed attempt, so a failed snippet can be retried with the
        same parameters (same rule as the CDP intent ledger above). The
        child sends this record after the snippet exec succeeds.
        """
        if key in self.applied_snippets:
            return
        if len(self.applied_snippets) >= MAX_SNIPPET_LEDGER_ENTRIES:
            logging.getLogger(__name__).warning(
                'applied snippet ledger is full; not recording %s', name)
            return
        self.applied_snippets[key] = {
            'name': name, 'params_sha256': params_hash,
            'result': _jsonable_copy(result), 'created': time.time(),
        }

    def run_snippet_program(self, name, intent=None, allow_stale=False,
                            approved=False):
        """Run one registry snippet as a top-level code-exec program."""
        if approved:
            self.approved_snippets.add(name)
        program = 'run_snippet(%s%s)' % (
            json.dumps(name),
            ', allow_stale=True' if allow_stale else '')
        return self.run(program, intent=intent)

    def _print(self, *args):
        self.log_lines.append(' '.join(str(a) for a in args))

    def run(self, source, intent=None):
        """Run one program. Always returns an envelope; raises only on cancel.

        The snippet runs in a forked child (_fork_api_session) so the
        wall clock binds C-level work the tracer cannot interrupt; the
        parent kills the child at the wall. API calls are marshalled
        back to the parent and executed there against the real backend
        and session state, so backend calls, observation bindings, DOM
        snapshots, api_calls, and the log all behave exactly as if the
        snippet ran in-process. Only the snippet's own variables travel
        back in the done envelope and are adopted here. A cancel raised
        inside the child comes back as a __cancelled__ payload and is
        re-raised below, after state is saved.
        """
        started = time.monotonic()
        self.api_calls = 0
        self.log_lines = []
        self._intent = intent
        self._trace_steps = 0
        self._trace_events = 0
        self._current_snippet_run = 0
        previous_variables = _jsonable_copy(self.variables)
        self._deadline = started + self.wall_seconds
        envelope = {
            'ok': False, 'intent': intent, 'api_calls': 0,
            'elapsed_ms': 0, 'log': [], 'variables': {},
        }
        cancelled_message = None
        try:
            tree = validate_program(source)
            self.check_cancel()
            api_methods = {
                "windows": self.api_windows,
                "observe": self.api_observe,
                "act": self.api_act,
                "read_file": self.api_read_file,
                "assert_state": self.api_assert_state,
                "assert_file_contains": self.api_assert_file_contains,
                "assert_file_exists": self.api_assert_file_exists,
                "dom_start": self.api_dom_start,
                "dom_tabs": self.api_dom_tabs,
                "dom_observe": self.api_dom_observe,
                "dom_act": self.api_dom_act,
                "dom_assert": self.api_dom_assert,
                "run_snippet": self.api_run_snippet,
                "print": self._print,
            }

            def api_handler(name, args, kwargs, snippet_run=0):
                # Item 10: the child tags every request with its snippet
                # run id (0 for the outer program). The parent applies it
                # for the duration of this one call, so observation and
                # DOM bindings are scoped per snippet run.
                if name == "run_snippet_record":
                    try:
                        self._record_snippet_result(*args, **kwargs)
                    except BaseException as exc:
                        return {"ok": False, "error": str(exc)[:400],
                                "type": type(exc).__name__}
                    return {"ok": True, "result": True}
                fn = api_methods.get(name)
                if fn is None:
                    return {"ok": False, "error": "unknown api: %s" % name,
                            "type": "CodeExecError"}
                old_run = self._current_snippet_run
                self._current_snippet_run = snippet_run
                old_tracer = sys.gettrace()
                sys.settrace(self._trace)
                try:
                    result = fn(*args, **kwargs)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except BaseException as exc:
                    try:
                        self.check_cancel()
                    except BaseException as cancel_exc:
                        return {"ok": False, "cancelled": True,
                                "error": str(cancel_exc)}
                    return {"ok": False, "error": str(exc)[:400],
                            "type": type(exc).__name__}
                finally:
                    sys.settrace(old_tracer)
                    self._current_snippet_run = old_run
                try:
                    json.dumps(result)
                except (TypeError, ValueError):
                    return {"ok": False,
                            "error": "api result is not serializable",
                            "type": "CodeExecError"}
                return {"ok": True, "result": result}

            def run_child(channel):
                # Item 10: the current snippet run id. 0 is the outer
                # program; each run_snippet call gets a FRESH id from a
                # monotonic counter, carried on every API request so the
                # parent can scope bindings per snippet run. A binary
                # in/out flag is not enough: sequential snippets must not
                # share an id (probe 11g), so the counter never reuses one.
                snippet_run = [0]
                snippet_run_next = [0]
                snippet_depth = [0]

                def make_stub(name):
                    def stub(*args, **kwargs):
                        try:
                            request = {"kind": "api", "name": name,
                                       "args": list(args),
                                       "kwargs": dict(kwargs),
                                       "snippet_run": snippet_run[0]}
                            json.dumps(request)
                        except (TypeError, ValueError):
                            raise CodeExecError(
                                "api call argument is not JSON-serializable: %s"
                                % name)
                        try:
                            channel.send(request)
                        except OSError:
                            raise CodeExecError("api channel closed")
                        try:
                            resp = channel.recv()
                        except (OSError, EOFError):
                            raise CodeExecError("api channel closed")
                        if resp.get("cancelled"):
                            self.check_cancel()
                            raise RuntimeError(resp.get("error") or "cancelled")
                        if not resp.get("ok"):
                            raise _exception_from_response(resp)
                        return resp.get("result")
                    return stub

                def run_snippet_stub(name, allow_stale=False, **params):
                    """Execute one verified registry snippet INLINE (item 7).

                    The parent already verified the manifest entry, the
                    params, the staleness rules, and the file hash, and
                    returned the source bytes. This stub validates those
                    bytes again, then execs them in the child under the
                    live tracer, so the snippet shares the outer program's
                    trace counter (child copy), deadline (child copy), and
                    API-call counter (parent, via the marshalled calls).
                    It never calls run() and never builds a nested session.
                    Params arrive as values, never interpolated into source
                    (item 11h); they bind as frame locals (item 9).
                    """
                    if snippet_depth[0]:
                        raise CodeExecError('nested run_snippet is not allowed')
                    if not isinstance(name, str):
                        raise CodeExecError('snippet name must be a string')
                    if not isinstance(allow_stale, bool):
                        raise CodeExecError('allow_stale must be boolean')
                    try:
                        request = {"kind": "api", "name": "run_snippet",
                                   "args": [name],
                                   "kwargs": {"allow_stale": allow_stale,
                                              "params": params},
                                   "snippet_run": snippet_run[0]}
                        json.dumps(request)
                    except (TypeError, ValueError):
                        raise CodeExecError(
                            'run_snippet params are not JSON-serializable')
                    try:
                        channel.send(request)
                    except OSError:
                        raise CodeExecError('api channel closed')
                    try:
                        resp = channel.recv()
                    except (OSError, EOFError):
                        raise CodeExecError('api channel closed')
                    if resp.get('cancelled'):
                        self.check_cancel()
                        raise RuntimeError(resp.get('error') or 'cancelled')
                    if not resp.get('ok'):
                        raise _exception_from_response(resp)
                    fetched = resp.get('result')
                    tree = validate_program(fetched['source'])
                    code = compile(tree, PROGRAM_FILENAME, 'exec')
                    snippet_run_next[0] += 1
                    old_run = snippet_run[0]
                    snippet_run[0] = snippet_run_next[0]
                    snippet_depth[0] += 1
                    frame_locals = dict(fetched['params'])
                    outcome = None
                    try:
                        snippet_globals = _snippet_globals(namespace)
                        exec(code, snippet_globals, frame_locals)  # noqa: S102 - AST-validated, hash-verified bytes
                        self._check_budgets()
                        output_name = fetched.get('output')
                        if output_name and output_name not in frame_locals:
                            raise CodeExecError('snippet did not assign its declared output: ' + output_name)
                        output_value = frame_locals.get(output_name) if output_name else None
                        if not _is_jsonable(output_value) or _serialized_size(output_value) > MAX_ENVELOPE_BYTES:
                            raise CodeExecError('snippet output must be JSON-serializable and at most 64KB')
                        if output_name:
                            namespace[output_name] = _jsonable_copy(output_value)
                        outcome = {'ok': True, 'name': name,
                                   'output': _jsonable_copy(output_value),
                                   'sha256': fetched['sha256'],
                                   'stale': fetched['stale']}
                        return outcome
                    finally:
                        snippet_depth[0] -= 1
                        snippet_run[0] = old_run
                        if outcome is not None and fetched.get('ledger'):
                            # Record only a successful application of a
                            # ledgered (requires_approval) snippet, so a
                            # failed snippet can be retried (item 12).
                            # Best effort: a broken channel means the run
                            # is dying anyway.
                            try:
                                channel.send({"kind": "api",
                                              "name": "run_snippet_record",
                                              "args": [fetched['ledger_key'], name,
                                                       fetched['params_hash'], outcome],
                                              "kwargs": {},
                                              "snippet_run": snippet_run[0]})
                                channel.recv()
                            except (OSError, EOFError, ValueError):
                                pass

                namespace = dict(self.variables)
                namespace.update({
                    '__builtins__': dict(SAFE_BUILTINS),
                    'windows': make_stub("windows"),
                    'observe': make_stub("observe"),
                    'act': make_stub("act"),
                    'read_file': make_stub("read_file"),
                    'assert_state': make_stub("assert_state"),
                    'assert_file_contains': make_stub("assert_file_contains"),
                    'assert_file_exists': make_stub("assert_file_exists"),
                    'dom_start': make_stub("dom_start"),
                    'dom_tabs': make_stub("dom_tabs"),
                    'dom_observe': make_stub("dom_observe"),
                    'dom_act': make_stub("dom_act"),
                    'dom_assert': make_stub("dom_assert"),
                    'run_snippet': run_snippet_stub,
                    'print': make_stub("print"),
                })
                child_envelope = dict(envelope)
                try:
                    sys.settrace(self._trace)
                    try:
                        code = compile(tree, PROGRAM_FILENAME, 'exec')
                        exec(code, namespace)  # noqa: S102 - AST-validated, restricted builtins
                    finally:
                        sys.settrace(None)
                    try:
                        self.check_cancel()
                    except BaseException as cancel_exc:
                        child_envelope = {'__cancelled__': True,
                                          'error': str(cancel_exc)}
                    else:
                        kept = {k: v for k, v in namespace.items()
                                if k not in ('__builtins__',) and not callable(v)
                                and k not in ('windows', 'observe', 'act', 'read_file',
                                              'assert_state', 'assert_file_contains',
                                              'assert_file_exists', 'dom_start', 'dom_tabs',
                                              'dom_observe', 'dom_act', 'dom_assert', 'print')
                                and k != 'run_snippet'
                                and _is_jsonable(v)}
                        variables = _jsonable_copy(kept)
                        candidate = dict(child_envelope, ok=True, variables=variables,
                                         api_calls=self.api_calls,
                                         elapsed_ms=round((time.monotonic() - started) * 1000, 3),
                                         log=list(self.log_lines))
                        if _serialized_size(candidate) > MAX_ENVELOPE_BYTES:
                            child_envelope['error'] = 'serialized result envelope exceeds %d bytes' % MAX_ENVELOPE_BYTES
                            child_envelope['error_type'] = 'result_too_large'
                            child_envelope['variables'] = previous_variables
                        else:
                            child_envelope = candidate
                except AssertionError as exc:
                    child_envelope['error'] = 'assert failed: ' + str(exc)
                    child_envelope['error_type'] = 'assert_failed'
                    child_envelope['variables'] = previous_variables
                except CodeExecError as exc:
                    child_envelope['error'] = str(exc)
                    child_envelope['error_type'] = 'sandbox'
                    child_envelope['variables'] = previous_variables
                except Exception as exc:
                    # A backend error (refusal, stale observation, compositor move)
                    # is a program outcome, not a crash: return it so the supervisor
                    # replans from the partial result. Cancellation still raises.
                    try:
                        self.check_cancel()
                    except BaseException as cancel_exc:
                        child_envelope = {'__cancelled__': True,
                                          'error': str(cancel_exc)}
                    else:
                        child_envelope['error'] = str(exc)[:400]
                        child_envelope['error_type'] = type(exc).__name__
                        child_envelope['variables'] = previous_variables
                channel.send({"kind": "done", "envelope": child_envelope})

            payload, status = _fork_api_session(
                run_child, self.wall_seconds, api_handler)
            if status == "ok" and payload.get('__cancelled__'):
                cancelled_message = payload.get('error') or 'cancelled'
            elif status == "ok":
                envelope = payload
                self.variables = _jsonable_copy(payload.get('variables', {}))
            elif status == "timeout":
                envelope['error'] = 'wall-clock budget exceeded (%.0fs)' % self.wall_seconds
                envelope['error_type'] = 'sandbox'
            elif status == "refused":
                envelope['error'] = 'wall-clock preemption unavailable (fork failed); execution refused'
                envelope['error_type'] = 'sandbox'
            else:
                envelope['error'] = 'snippet process exited without a result'
                envelope['error_type'] = 'crashed'
        except AssertionError as exc:
            envelope['error'] = 'assert failed: ' + str(exc)
            envelope['error_type'] = 'assert_failed'
        except CodeExecError as exc:
            envelope['error'] = str(exc)
            envelope['error_type'] = 'sandbox'
        except Exception as exc:
            # A backend error (refusal, stale observation, compositor move)
            # is a program outcome, not a crash: return it so the supervisor
            # replans from the partial result. Cancellation still raises.
            self.check_cancel()
            envelope['error'] = str(exc)[:400]
            envelope['error_type'] = type(exc).__name__
        finally:
            self._save_state()
        if cancelled_message is not None:
            raise RuntimeError(cancelled_message)
        envelope['api_calls'] = self.api_calls
        envelope['elapsed_ms'] = round((time.monotonic() - started) * 1000, 3)
        envelope['log'] = list(self.log_lines)
        if 'variables' not in envelope or not envelope.get('variables'):
            envelope['variables'] = _jsonable_copy(self.variables)
        if _serialized_size(envelope) > MAX_ENVELOPE_BYTES:
            self.variables = previous_variables
            self._save_state()
            envelope = {
                'ok': False, 'error': 'serialized result envelope exceeds %d bytes' % MAX_ENVELOPE_BYTES,
                'error_type': 'result_too_large', 'api_calls': self.api_calls,
                'elapsed_ms': round((time.monotonic() - started) * 1000, 3),
                'log': [], 'variables': {},
            }
        return envelope


def run_program(source, backend, state_dir=None, session_token=None,
                intent=None, check_cancel=None, wall_seconds=DEFAULT_WALL_SECONDS,
                max_api_calls=MAX_API_CALLS, snippet_root=None):
    """One-shot entry point: build a session, run one program, return envelope."""
    session = CodeExecSession(backend, state_dir=state_dir,
                              session_token=session_token,
                              check_cancel=check_cancel,
                              wall_seconds=wall_seconds,
                              max_api_calls=max_api_calls,
                              snippet_root=snippet_root)
    return session.run(source, intent=intent)


def run_snippet_program(name, backend, state_dir=None, session_token=None,
                        intent=None, check_cancel=None,
                        wall_seconds=DEFAULT_WALL_SECONDS,
                        max_api_calls=MAX_API_CALLS, snippet_root=None,
                        allow_stale=False, approved=False):
    """One-shot entry point for a named registry snippet."""
    session = CodeExecSession(backend, state_dir=state_dir,
                              session_token=session_token,
                              check_cancel=check_cancel,
                              wall_seconds=wall_seconds,
                              max_api_calls=max_api_calls,
                              snippet_root=snippet_root)
    return session.run_snippet_program(name, intent=intent,
                                       allow_stale=allow_stale,
                                       approved=approved)

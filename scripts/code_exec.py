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
  dict. The snapshot id binds its target and refs for 90 seconds.
- dom_act(snapshot, actions, after_scope=None) -> CDP result dict. Refs must
  come from the supplied snapshot; successful after snapshots are bound too.
- dom_assert(snapshot, ref=None, selector=None, text=None, value=None,
  checked=None, timeout_ms=1000) -> True or raises AssertionError.
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
DOM snapshot bindings are kept in the same file but expire after 90s.

Template rule: see improvements/pick1-program-template.md. Observe after
act() and before file asserts. For shell printf text, use one single-quoted
argument and write \\n between output lines in the Python source.
"""
import ast
import json
import math
import os
import re
import sys
import time
from pathlib import Path

MAX_PROGRAM_CHARS = 8192
MAX_WALL_SECONDS = 60
DEFAULT_WALL_SECONDS = 30
MAX_API_CALLS = 32
MAX_TRACE_STEPS = 20000
PROGRAM_FILENAME = '<code-exec>'
MAX_READ_BYTES = 65536
OBSERVATION_MAX_AGE = 90
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
    'round': round,
}
# print is captured into the result log, never written to real stdout.
SAFE_ATTRIBUTE_NAMES = {
    'get', 'keys', 'values', 'items',
    'startswith', 'endswith', 'strip', 'split', 'join', 'lower', 'upper',
    'format', 'replace', 'count', 'find', 'index',
    'append', 'extend', 'pop', 'remove',
}
BANNED_NAMES = {
    '__import__', 'eval', 'exec', 'compile', 'open', 'input', 'globals',
    'locals', 'vars', 'getattr', 'setattr', 'delattr', 'hasattr',
    'breakpoint', 'memoryview', 'object', 'type', 'help', 'dir',
    'os', 'sys', 'subprocess', 'socket', 'pathlib', 'shutil', 'time',
    'json', 're', 'io', 'importlib', 'builtins', '__builtins__',
}


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


def _validate_dom_actions(actions, refs):
    """Mirror cdp.mjs action preflight before any CDP request is made."""
    allowed = {'click', 'fill', 'set_value', 'key', 'scroll', 'wait', 'assert'}
    element_actions = {'click', 'fill', 'set_value', 'assert'}
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


class _Validator(ast.NodeVisitor):
    """Reject every construct outside the allowlist before execution."""

    def __init__(self):
        self.allowed_names = set(SAFE_BUILTINS) | {
            'windows', 'observe', 'act', 'read_file', 'assert_state',
            'assert_file_contains', 'assert_file_exists', 'print',
            'dom_start', 'dom_tabs', 'dom_observe', 'dom_act', 'dom_assert',
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
                 max_api_calls=MAX_API_CALLS):
        self.backend = backend
        self.state_dir = Path(state_dir) if state_dir is not None else None
        self.session_token = session_token
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

    def _save_state(self):
        path = self._state_path()
        if path is None:
            return
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
        return {
            'id': meta['id'],
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
            newest = max(self.observations.values(), key=lambda m: m.get('created', 0))
            return newest
        if not isinstance(observation, dict) or not isinstance(observation.get('id'), str):
            raise CodeExecError('act observation must be an observation dict from observe()')
        meta = self.observations.get(observation['id'])
        if meta is None:
            raise CodeExecError('observation id is not bound to this session; observe again')
        if time.time() - meta.get('created', 0) > OBSERVATION_MAX_AGE:
            raise CodeExecError('observation is older than 90s; observe again')
        return meta

    def api_act(self, actions, observation=None):
        if not isinstance(actions, list) or not actions:
            raise CodeExecError('act actions must be a non-empty list')
        meta = self._bound_observation(observation)
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
        return snapshot

    def _bound_dom_snapshot(self, snapshot):
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('snapshot'), str):
            raise CodeExecError('snapshot must be a DOM snapshot dict from dom_observe()')
        snapshot_id = snapshot['snapshot']
        binding = self.dom_snapshots.get(snapshot_id)
        if binding is None:
            raise CodeExecError('DOM snapshot id is not bound to this session; observe again')
        if snapshot != binding.get('snapshot'):
            raise CodeExecError('snapshot is not the bound DOM snapshot; observe again')
        if time.time() - binding.get('created', 0) > OBSERVATION_MAX_AGE:
            raise CodeExecError('DOM snapshot is older than 90s; observe again')
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
        """Wait for the managed Chromium window to appear in windows().

        browser_start returns once CDP answers, but the Wayland window can
        map later; without this wait the D1 program IndexErrors on the
        immediate windows() lookup after dom_start(). Polls go straight to
        backend.windows(), not through _api, so the wait costs no API-call
        budget. Cancellation and the wall-clock budget are checked every
        poll; a window that never appears fails closed with CodeExecError.
        """
        deadline = time.monotonic() + DOM_WINDOW_WAIT_SECONDS
        while True:
            self.check_cancel()
            try:
                wins = self.backend.windows()
            except Exception as exc:
                self.check_cancel()
                raise CodeExecError(
                    'windows() failed while waiting for Chromium: '
                    + str(exc)[:200]) from exc
            if isinstance(wins, list) and any(
                    isinstance(w, dict) and w.get('class') == DOM_WINDOW_CLASS
                    for w in wins):
                return
            if time.monotonic() >= deadline:
                raise CodeExecError(
                    'managed Chromium window did not appear within %.0fs; '
                    'observe windows() again' % DOM_WINDOW_WAIT_SECONDS)
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
        _validate_dom_actions(actions, refs)
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

    def _print(self, *args):
        self.log_lines.append(' '.join(str(a) for a in args))

    def run(self, source, intent=None):
        """Run one program. Always returns an envelope; raises only on cancel."""
        started = time.monotonic()
        self.api_calls = 0
        self.log_lines = []
        self._trace_steps = 0
        self._trace_events = 0
        self._deadline = started + self.wall_seconds
        envelope = {
            'ok': False, 'intent': intent, 'api_calls': 0,
            'elapsed_ms': 0, 'log': [], 'variables': {},
        }
        try:
            tree = validate_program(source)
            self.check_cancel()
            namespace = dict(self.variables)
            namespace.update({
                '__builtins__': dict(SAFE_BUILTINS),
                'windows': self.api_windows,
                'observe': self.api_observe,
                'act': self.api_act,
                'read_file': self.api_read_file,
                'assert_state': self.api_assert_state,
                'assert_file_contains': self.api_assert_file_contains,
                'assert_file_exists': self.api_assert_file_exists,
                'dom_start': self.api_dom_start,
                'dom_tabs': self.api_dom_tabs,
                'dom_observe': self.api_dom_observe,
                'dom_act': self.api_dom_act,
                'dom_assert': self.api_dom_assert,
                'print': self._print,
            })
            sys.settrace(self._trace)
            try:
                code = compile(tree, PROGRAM_FILENAME, 'exec')
                exec(code, namespace)  # noqa: S102 - AST-validated, restricted builtins
            finally:
                sys.settrace(None)
            self.check_cancel()
            kept = {k: v for k, v in namespace.items()
                    if k not in ('__builtins__',) and not callable(v)
                    and k not in ('windows', 'observe', 'act', 'read_file',
                                  'assert_state', 'assert_file_contains',
                                  'assert_file_exists', 'dom_start', 'dom_tabs',
                                  'dom_observe', 'dom_act', 'dom_assert', 'print')
                    and _is_jsonable(v)}
            self.variables = _jsonable_copy(kept)
            envelope['ok'] = True
            envelope['variables'] = _jsonable_copy(self.variables)
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
        envelope['api_calls'] = self.api_calls
        envelope['elapsed_ms'] = round((time.monotonic() - started) * 1000, 3)
        envelope['log'] = list(self.log_lines)
        if 'variables' not in envelope or not envelope.get('variables'):
            envelope['variables'] = _jsonable_copy(self.variables)
        return envelope


def run_program(source, backend, state_dir=None, session_token=None,
                intent=None, check_cancel=None, wall_seconds=DEFAULT_WALL_SECONDS,
                max_api_calls=MAX_API_CALLS):
    """One-shot entry point: build a session, run one program, return envelope."""
    session = CodeExecSession(backend, state_dir=state_dir,
                              session_token=session_token,
                              check_cancel=check_cancel,
                              wall_seconds=wall_seconds,
                              max_api_calls=max_api_calls)
    return session.run(source, intent=intent)

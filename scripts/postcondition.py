#!/usr/bin/env python3
"""A4: deterministic postcondition verification (Track 2, algorithm lane).

Verifies a task end state with code, not with a model observe call, so
the executor can skip the verify-observe think step (measured 6.7s mean,
18% of a clean task, algorithm-research.md section A4) whenever the end
state has an exact local proof.

What this module does:
- Takes a small JSON spec: a list of checks. Each check names one exact
  local source (file bytes, window list, DOM snapshot) and the expected
  value. Every check is re-read from that source at verify time, never
  trusted from a program variable or a cached observation.
- Returns a verdict dict with one of three statuses:
  - ``verified``: every check passed AND the pairing rule holds. The
    supervisor may finish without a verify observe.
  - ``failed``: at least one check proved the end state wrong. The
    supervisor must replan, not finish.
  - ``inconclusive``: no local check can prove this end state (empty
    spec, unknown check kind, a backend the caller did not supply, or
    the pairing rule unmet). The supervisor MUST fall back to a vision
    verify observe. Inconclusive is never success.

Pairing rule (from the A4 research note: pair every local check with
its semantic match, hash change PLUS file bytes, never a single
signal): a spec is verifiable only when it carries at least one
exact-bytes proof (``file_contains`` or ``file_equals``), or a DOM text
proof (``dom_text`` reads exact DOM text), or at least two passed
checks that are independent signals (different kinds, or the same
kind on a different path/target, e.g. two different directories),
or a single ``window_present`` that matched BOTH class and title.
A lone ``file_exists``, a lone ``file_sha256``, or a lone class-only
``window_present`` is inconclusive, not verified.

What this module never does:
- No screenshot, no image, no model call, no write, no shell, no
  network. File checks are read-only. Evidence reports hashes, sizes
  and matched window/DOM refs, never file contents (the only text in a
  detail is the needle the caller supplied).
- No silent pass: malformed specs raise ValueError to the caller, and
  a backend error on a check makes that check fail closed (passed
  False) with the error in its detail, capped at 200 chars. A check
  whose backend the caller did not supply at all is different: it
  cannot prove anything either way, so it marks the verdict
  ``inconclusive`` (vision verify required), never ``failed``.

Check kinds:
- ``file_exists`` {path}: the path is a regular file (or directory when
  ``directory`` is true).
- ``file_contains`` {path, text}: file bytes decode as UTF-8 and
  contain the exact text. Exact-bytes proof.
- ``file_equals`` {path, sha256}: SHA-256 of the file bytes equals the
  expected hex digest. Exact-bytes proof.
- ``file_sha256`` {path, sha256}: same as file_equals, but recorded as
  a supporting single signal only; it never satisfies the pairing rule
  on its own. (Kept as a separate kind so a spec that pairs it with a
  file_contains reads clearly.)
- ``window_present`` {class, title, address}: at least one window in
  the list matches every field given. At least one field is required.
- ``window_absent`` {class, title}: no window matches every field
  given. At least one field is required.
- ``dom_text`` {target, text, scope}: a fresh DOM snapshot for the
  target contains an element whose name, value or text contains the
  exact text. Exact-DOM proof.

Backends are injected callables, so unit tests run with fakes and the
broker wires the real ones:
- ``read_bytes(path)`` -> bytes. The caller owns the path scope (the
  code-exec sandbox restricts it to /tmp; the ``verify`` CLI reads any
  absolute regular file, read-only).
- ``list_windows()`` -> list of {address, class, title, ...}.
- ``dom_observe(target, scope, max_elements)`` -> snapshot dict with
  an ``elements`` list of {ref, name, value, text, ...}.
- ``dir_exists(path)`` -> bool, for ``file_exists`` checks with
  ``directory`` true (directories have no bytes to read).

No em dash or en dash in this file.
"""

import hashlib
import time

MAX_CHECKS = 16
MAX_TEXT_CHARS = 10000
MAX_NAME_CHARS = 128
MAX_FILE_BYTES = 65536
DEFAULT_DOM_MAX_ELEMENTS = 80

# Kinds whose single passed check is itself an exact proof of the end
# state, so one of them satisfies the pairing rule alone.
EXACT_PROOF_KINDS = frozenset({'file_contains', 'file_equals', 'dom_text'})

# Kinds that only support a verdict, never prove it alone.
SUPPORTING_KINDS = frozenset({'file_sha256'})

CHECK_KINDS = frozenset({
    'file_exists', 'file_contains', 'file_equals', 'file_sha256',
    'window_present', 'window_absent', 'dom_text',
})

_FILE_KINDS = frozenset(
    {'file_exists', 'file_contains', 'file_equals', 'file_sha256'})
_WINDOW_KINDS = frozenset({'window_present', 'window_absent'})


class PostconditionError(ValueError):
    """A spec is malformed. Fails closed: the caller must not verify."""


def _is_sha256(value):
    return (isinstance(value, str) and len(value) == 64
            and all(ch in '0123456789abcdef' for ch in value.lower()))


def _check_text(value, field):
    if not isinstance(value, str) or not value:
        raise PostconditionError(field + ' must be a non-empty string')
    if len(value) > MAX_TEXT_CHARS:
        raise PostconditionError(field + ' exceeds %d chars' % MAX_TEXT_CHARS)
    return value


def _check_path(value):
    if not isinstance(value, str) or not value.startswith('/'):
        raise PostconditionError('path must be an absolute path')
    return value


def validate_checks(checks):
    """Validate a spec. Returns a normalized copy; raises PostconditionError.

    An empty spec is malformed here (the verifier reports it as
    inconclusive instead, so callers that already hold a verdict dict
    keep a verdict; direct callers get the strict error).
    """
    if not isinstance(checks, list) or not checks:
        raise PostconditionError('checks must be a non-empty list')
    if len(checks) > MAX_CHECKS:
        raise PostconditionError('at most %d checks' % MAX_CHECKS)
    normalized = []
    for check in checks:
        if not isinstance(check, dict):
            raise PostconditionError('each check must be an object')
        kind = check.get('kind')
        if kind not in CHECK_KINDS:
            raise PostconditionError('unknown check kind: %r' % (kind,))
        name = check.get('name')
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                raise PostconditionError('name must be a non-empty string')
            if len(name) > MAX_NAME_CHARS:
                raise PostconditionError('name exceeds %d chars' % MAX_NAME_CHARS)
        item = {'kind': kind}
        if name is not None:
            item['name'] = name
        if kind in _FILE_KINDS:
            item['path'] = _check_path(check.get('path'))
            if kind in ('file_contains',):
                item['text'] = _check_text(check.get('text'), 'text')
            if kind in ('file_equals', 'file_sha256'):
                digest = check.get('sha256')
                if not _is_sha256(digest):
                    raise PostconditionError('sha256 must be 64 hex chars')
                item['sha256'] = digest.lower()
            if kind == 'file_exists' and 'directory' in check:
                if not isinstance(check['directory'], bool):
                    raise PostconditionError('directory must be a boolean')
                item['directory'] = check['directory']
        elif kind in _WINDOW_KINDS:
            given = 0
            for field in ('class', 'title', 'address'):
                if field in check:
                    if kind == 'window_absent' and field == 'address':
                        raise PostconditionError(
                            'window_absent takes class or title, not address')
                    value = check[field]
                    if not isinstance(value, str) or not value:
                        raise PostconditionError(field + ' must be a non-empty string')
                    item[field] = value
                    given += 1
            if not given:
                raise PostconditionError(
                    kind + ' needs at least one of class, title, address')
        elif kind == 'dom_text':
            item['target'] = _check_text(check.get('target'), 'target')
            item['text'] = _check_text(check.get('text'), 'text')
            if 'scope' in check:
                if (not isinstance(check['scope'], str)
                        or not check['scope'].strip()):
                    raise PostconditionError('scope must be a non-empty string')
                item['scope'] = check['scope']
        normalized.append(item)
    return normalized


def pairing_satisfied(results):
    """True when the passed checks carry an exact proof, per the A4 rule.

    ``results`` are per-check dicts with kind, passed, and (for
    window_present) matched_fields. A single exact-bytes/DOM proof
    suffices; otherwise two passed checks that are independent
    signals (different kinds, or the same kind on a different path,
    target, or window), or one window_present that matched both
    class and title.
    """
    passed = [item for item in results if item.get('passed')]
    if any(item['kind'] in EXACT_PROOF_KINDS for item in passed):
        return True
    kinds = {item['kind'] for item in passed}
    if len(kinds) >= 2:
        return True
    signals = set()
    for item in passed:
        # The subject is the path, target, or window identity the check
        # proved something about; two same-kind checks on different
        # subjects are independent signals (e.g. two different
        # directories existing). A single check, or two checks on the
        # same subject, leaves only one signal.
        signals.add((item['kind'], item.get('subject')))
    if len(passed) >= 2 and len(signals) >= 2:
        return True
    for item in passed:
        if item['kind'] == 'window_present':
            matched = item.get('matched_fields') or []
            if 'class' in matched and 'title' in matched:
                return True
    return False


def paired_file_checks(path, text):
    """Convenience: the two-check file proof for one expected content.

    Returns a file_contains check (exact bytes, satisfies the pairing
    rule alone) plus a file_exists check on the same path as the second
    independent signal the A4 note asks for. Callers that know the
    expected SHA-256 should add a file_sha256 check with it as well:
    hash PLUS bytes is the ideal pair.
    """
    _check_path(path)
    _check_text(text, 'text')
    return [
        {'kind': 'file_contains', 'path': path, 'text': text},
        {'kind': 'file_exists', 'path': path},
    ]


def _sha256_hex(raw):
    return hashlib.sha256(raw).hexdigest()


def _run_file_check(check, read_bytes, max_bytes, dir_exists=None):
    path = check['path']
    kind = check['kind']
    if kind == 'file_exists' and check.get('directory'):
        if dir_exists is None:
            return {'kind': kind, 'name': check.get('name'), 'passed': False,
                    'unavailable': True,
                    'detail': 'no directory backend supplied; '
                              'vision verify required'}
        try:
            exists = dir_exists(path)
        except Exception as exc:
            return {'kind': kind, 'name': check.get('name'), 'passed': False,
                    'detail': 'directory check failed: '
                              + ' '.join(str(exc).split())[:200]}
        if exists:
            return {'kind': kind, 'name': check.get('name'), 'passed': True,
                    'detail': 'directory exists: ' + path}
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'directory does not exist: ' + path}
    try:
        raw = read_bytes(path)
    except Exception as exc:
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'read failed: ' + ' '.join(str(exc).split())[:200]}
    if not isinstance(raw, (bytes, bytearray)):
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'read_bytes must return bytes'}
    raw = bytes(raw)
    if len(raw) > max_bytes:
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'file exceeds %d bytes (%d)' % (max_bytes, len(raw))}
    digest = _sha256_hex(raw)
    base = 'sha256 %s, %d bytes' % (digest, len(raw))
    if kind == 'file_exists':
        return {'kind': kind, 'name': check.get('name'), 'passed': True,
                'detail': 'exists: ' + base}
    if kind == 'file_contains':
        text = check['text']
        try:
            decoded = raw.decode('utf-8')
        except UnicodeDecodeError:
            return {'kind': kind, 'name': check.get('name'), 'passed': False,
                    'detail': 'file is not UTF-8 text: ' + base}
        if text in decoded:
            return {'kind': kind, 'name': check.get('name'), 'passed': True,
                    'detail': 'contains %r: %s' % (text[:40], base)}
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'missing %r: %s' % (text[:40], base)}
    if kind in ('file_equals', 'file_sha256'):
        expected = check['sha256']
        if digest == expected:
            return {'kind': kind, 'name': check.get('name'), 'passed': True,
                    'detail': 'sha256 matches: ' + base}
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'sha256 mismatch: expected %s, %s' % (expected, base)}
    return {'kind': kind, 'name': check.get('name'), 'passed': False,
            'detail': 'unsupported file check'}


def _window_matches(window, check):
    matched = []
    for field in ('class', 'title', 'address'):
        if field in check:
            if window.get(field) != check[field]:
                return None
            matched.append(field)
    return matched


def _run_window_check(check, list_windows):
    kind = check['kind']
    try:
        windows = list_windows()
    except Exception as exc:
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'windows list failed: '
                          + ' '.join(str(exc).split())[:200]}
    if not isinstance(windows, list):
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'list_windows must return a list'}
    for window in windows:
        if not isinstance(window, dict):
            continue
        matched = _window_matches(window, check)
        if matched is not None:
            if kind == 'window_present':
                return {'kind': kind, 'name': check.get('name'),
                        'passed': True, 'matched_fields': matched,
                        'detail': 'matched %s %s'
                                  % (window.get('class'), window.get('title'))}
            return {'kind': kind, 'name': check.get('name'), 'passed': False,
                    'detail': 'unexpected window present: %s %s'
                              % (window.get('class'), window.get('title'))}
    if kind == 'window_present':
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'no window matched'}
    return {'kind': kind, 'name': check.get('name'), 'passed': True,
            'detail': 'no window matched'}


def _run_dom_check(check, dom_observe):
    kind = check['kind']
    try:
        snapshot = dom_observe(check['target'], check.get('scope'),
                               DEFAULT_DOM_MAX_ELEMENTS)
    except Exception as exc:
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'DOM observe failed: '
                          + ' '.join(str(exc).split())[:200]}
    if not isinstance(snapshot, dict) or not isinstance(
            snapshot.get('elements'), list):
        return {'kind': kind, 'name': check.get('name'), 'passed': False,
                'detail': 'DOM snapshot has no elements list'}
    text = check['text']
    for element in snapshot['elements']:
        if not isinstance(element, dict):
            continue
        haystack = ' '.join(str(element.get(field) or '')
                            for field in ('name', 'value', 'text'))
        if text in haystack:
            return {'kind': kind, 'name': check.get('name'), 'passed': True,
                    'detail': 'DOM text found in ref %s'
                              % (element.get('ref'),)}
    return {'kind': kind, 'name': check.get('name'), 'passed': False,
            'detail': 'DOM text %r not in snapshot (%d elements)'
                      % (text[:40], len(snapshot['elements']))}


def verify_postconditions(checks, *, read_bytes=None, list_windows=None,
                          dom_observe=None, dir_exists=None,
                          max_bytes=MAX_FILE_BYTES):
    """Run a postcondition spec deterministically. Always returns a verdict.

    Never raises on a check outcome: malformed specs and backend errors
    become ``inconclusive`` (vision verify required) or ``failed``
    verdicts, so the supervisor always gets a decidable answer. Only a
    non-list ``checks`` value raises PostconditionError, because there
    is no spec at all to report on.
    """
    started = time.monotonic()
    if not isinstance(checks, list):
        raise PostconditionError('checks must be a list')
    verdict = {
        'ok': False, 'status': 'inconclusive', 'passed': [], 'failed': [],
        'checks': [], 'needs_vision': True, 'elapsed_ms': 0,
    }
    try:
        normalized = validate_checks(checks)
    except PostconditionError as exc:
        verdict['error'] = str(exc)
        verdict['elapsed_ms'] = round((time.monotonic() - started) * 1000, 3)
        return verdict
    for check in normalized:
        kind = check['kind']
        if kind in _FILE_KINDS:
            if kind == 'file_exists' and check.get('directory'):
                result = _run_file_check(check, read_bytes, max_bytes,
                                         dir_exists=dir_exists)
            elif read_bytes is None:
                result = {'kind': kind, 'name': check.get('name'),
                          'passed': False, 'unavailable': True,
                          'detail': 'no file backend supplied; vision verify required'}
            else:
                result = _run_file_check(check, read_bytes, max_bytes)
        elif kind in _WINDOW_KINDS:
            if list_windows is None:
                result = {'kind': kind, 'name': check.get('name'),
                          'passed': False, 'unavailable': True,
                          'detail': 'no window backend supplied; vision verify required'}
            else:
                result = _run_window_check(check, list_windows)
        elif kind == 'dom_text':
            if dom_observe is None:
                result = {'kind': kind, 'name': check.get('name'),
                          'passed': False, 'unavailable': True,
                          'detail': 'no DOM backend supplied; vision verify required'}
            else:
                result = _run_dom_check(check, dom_observe)
        else:  # validate_checks already rejects this; defensive.
            result = {'kind': kind, 'name': check.get('name'),
                      'passed': False, 'detail': 'unknown check kind'}
        if kind in _FILE_KINDS:
            result['subject'] = check.get('path')
        elif kind in _WINDOW_KINDS:
            result['subject'] = '|'.join(
                str(check.get(field) or '')
                for field in ('class', 'title', 'address'))
        elif kind == 'dom_text':
            result['subject'] = check.get('target')
        verdict['checks'].append(result)
        label = result.get('name') or result['kind']
        if result['passed']:
            verdict['passed'].append(label)
        else:
            verdict['failed'].append(label)
    if verdict['failed']:
        proven_failed = [item for item in verdict['checks']
                         if not item['passed']
                         and not item.get('unavailable')]
        unavailable = [item for item in verdict['checks']
                       if not item['passed'] and item.get('unavailable')]
        if proven_failed:
            verdict['status'] = 'failed'
            verdict['needs_vision'] = False
        elif unavailable:
            verdict['status'] = 'inconclusive'
            verdict['error'] = ('no local backend for '
                                + ', '.join(item['kind']
                                            for item in unavailable)
                                + '; vision verify required')
            verdict['needs_vision'] = True
        else:  # Defensive: failed names with no failed check record.
            verdict['status'] = 'failed'
            verdict['needs_vision'] = False
    elif pairing_satisfied(verdict['checks']):
        verdict['status'] = 'verified'
        verdict['ok'] = True
        verdict['needs_vision'] = False
    else:
        verdict['status'] = 'inconclusive'
        verdict['error'] = ('checks passed but no exact proof: '
                            'add a file_contains, file_equals or dom_text '
                            'check, or a second check of another kind')
        verdict['needs_vision'] = True
    verdict['elapsed_ms'] = round((time.monotonic() - started) * 1000, 3)
    return verdict

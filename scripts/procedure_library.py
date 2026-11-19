#!/usr/bin/env python3
"""A3: procedure library, minimal viable core (Track 2, algorithm lane).

Stores parameterized procedures extracted from successful traces and
retrieves them by exact key, so a repeat task shape runs as Level-1
deterministic execution with no model turns on the happy path
(algorithm-research.md section A3; tc02 t1 823s vs t3 ~100s, 8.23x,
is the measured precedent).

This module is storage, retrieval, and quarantine only. It never
executes anything itself: retrieve() returns the stored code-exec
program source, and the caller runs it through the existing code-exec
path, then records the outcome with record_result(). The checkpoint
that decides pass/fail is postcondition.verify_postconditions, never a
model call.

Key: an exact string built from app + window/dialog class +
action-verb sequence + geometry bucket. Retrieval is exact-match
only: similarity is not proof (a 0.95 match with a different filename
is a wrong answer served fast), so there is no fuzzy lookup.

Quarantine: same rule as subgoal_policy (a procedure whose checkpoint
fails twice in a row is quarantined; retrieve() then returns None and
the next run re-derives layout from a fresh full-frame observation
instead of trusting the stored procedure). The counter lives here so
this module never touches another module's private state; the
threshold is imported from subgoal_policy so the two stay in sync.

Store: one JSON file, mode 0600, under the caller-supplied state
directory (same private-state discipline as code-exec state files).
A corrupt or unreadable store loads as empty; a failed save never
raises to the caller (best effort, like code-exec state).

Procedure record:
- key: exact retrieval key (see procedure_key).
- name: short human name, at most 128 chars.
- program: code-exec program source, validated with
  code_exec.validate_program at register time.
- checks: postcondition spec, validated with
  postcondition.validate_checks at register time.
- app, window_class, verbs, geometry_bucket: the key components,
  stored for audit.
- uses, successes, failures, quarantined, created, updated: counters.

No em dash or en dash in this file.
"""

import json
import os
import time
from pathlib import Path

STORE_FILENAME = 'procedures.json'
MAX_NAME_CHARS = 128
MAX_PROGRAM_CHARS = 8192
MAX_PROCEDURES = 256


class ProcedureError(ValueError):
    """A procedure record or key is malformed. Fails closed."""


def procedure_key(app, window_class, verbs, geometry_bucket=''):
    """Build the exact retrieval key for a task shape.

    verbs is the action-verb sequence, e.g. ['type', 'type'] or
    ['click', 'fill', 'assert']. geometry_bucket is a coarse bucket
    such as '800x600' or 'dialog-save-as', never exact pixel
    coordinates: exact coordinates go stale when the desktop reflows.
    """
    if not isinstance(app, str) or not app.strip():
        raise ProcedureError('app must be a non-empty string')
    if not isinstance(window_class, str) or not window_class.strip():
        raise ProcedureError('window_class must be a non-empty string')
    if (not isinstance(verbs, (list, tuple)) or not verbs
            or any(not isinstance(v, str) or not v.strip() for v in verbs)):
        raise ProcedureError('verbs must be a non-empty list of strings')
    if not isinstance(geometry_bucket, str):
        raise ProcedureError('geometry_bucket must be a string')
    parts = [app.strip(), window_class.strip(),
             '+'.join(v.strip() for v in verbs), geometry_bucket.strip()]
    return '|'.join(parts)


class ProcedureLibrary:
    """Exact-key procedure store with checkpoint quarantine."""

    def __init__(self, state_dir=None):
        try:
            from subgoal_policy import QUARANTINE_AFTER_FAILURES
            self._quarantine_threshold = QUARANTINE_AFTER_FAILURES
        except Exception:
            self._quarantine_threshold = 2
        self.state_dir = Path(state_dir) if state_dir is not None else None
        self._procedures = {}
        self._failures = {}
        self._quarantined = set()
        self._load()

    def _store_path(self):
        if self.state_dir is None:
            return None
        return self.state_dir / STORE_FILENAME

    def _load(self):
        path = self._store_path()
        if path is None or not path.is_file():
            return
        try:
            raw = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if not isinstance(raw, dict):
            return
        for key, record in raw.items():
            if isinstance(key, str) and isinstance(record, dict):
                self._procedures[key] = record
                if record.get('quarantined'):
                    self._quarantined.add(key)
                    self._failures[key] = self._quarantine_threshold

    def _save(self):
        path = self._store_path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC
                         | os.O_NOFOLLOW, 0o600)
            try:
                os.fchmod(fd, 0o600)
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    stream.write(json.dumps(self._procedures,
                                            ensure_ascii=False))
            except BaseException:
                try:
                    os.close(fd)
                except OSError:
                    pass
                raise
        except OSError:
            pass

    def register(self, *, key, name, program, checks, app=None,
                 window_class=None, verbs=None, geometry_bucket=''):
        """Store a procedure. Validates program and checks; fails closed."""
        import code_exec
        import postcondition
        if not isinstance(key, str) or not key.strip():
            raise ProcedureError('key must be a non-empty string')
        if not isinstance(name, str) or not name.strip():
            raise ProcedureError('name must be a non-empty string')
        if len(name) > MAX_NAME_CHARS:
            raise ProcedureError('name exceeds %d chars' % MAX_NAME_CHARS)
        if not isinstance(program, str) or not program.strip():
            raise ProcedureError('program must be a non-empty string')
        if len(program) > MAX_PROGRAM_CHARS:
            raise ProcedureError('program exceeds %d chars' % MAX_PROGRAM_CHARS)
        code_exec.validate_program(program)
        normalized_checks = postcondition.validate_checks(checks)
        if len(self._procedures) >= MAX_PROCEDURES and key not in self._procedures:
            raise ProcedureError('procedure store is full (%d)'
                                 % MAX_PROCEDURES)
        now = time.time()
        previous = self._procedures.get(key)
        self._procedures[key] = {
            'key': key, 'name': name, 'program': program,
            'checks': normalized_checks,
            'app': app, 'window_class': window_class,
            'verbs': list(verbs) if verbs else None,
            'geometry_bucket': geometry_bucket,
            'uses': (previous or {}).get('uses', 0),
            'successes': (previous or {}).get('successes', 0),
            'failures': (previous or {}).get('failures', 0),
            'quarantined': False,
            'created': (previous or {}).get('created', now),
            'updated': now,
        }
        self._failures.pop(key, None)
        self._quarantined.discard(key)
        self._save()
        return self._procedures[key]

    def retrieve(self, key):
        """Exact-match lookup. None when missing or quarantined."""
        if not isinstance(key, str):
            return None
        if key in self._quarantined:
            return None
        record = self._procedures.get(key)
        if record is None or record.get('quarantined'):
            return None
        return dict(record)

    def is_quarantined(self, key):
        return key in self._quarantined

    def record_result(self, key, *, passed):
        """Record one run outcome. Returns True when this quarantines it."""
        record = self._procedures.get(key)
        if record is None:
            return False
        record['uses'] = record.get('uses', 0) + 1
        if passed:
            record['successes'] = record.get('successes', 0) + 1
            self._failures[key] = 0
            quarantined = False
        else:
            record['failures'] = record.get('failures', 0) + 1
            count = self._failures.get(key, 0) + 1
            self._failures[key] = count
            quarantined = count >= self._quarantine_threshold
            if quarantined:
                self._quarantined.add(key)
        record['quarantined'] = bool(quarantined)
        record['updated'] = time.time()
        self._save()
        return quarantined

    def checkpoint(self, key, *, read_bytes=None, list_windows=None,
                   dom_observe=None, dir_exists=None):
        """Run the stored postcondition spec for a procedure.

        Returns the postcondition verdict dict, and records the
        outcome (a 'verified' verdict counts as passed, anything else
        as failed) so two consecutive checkpoint failures quarantine
        the procedure. Unknown key returns None.
        """
        import postcondition
        record = self._procedures.get(key)
        if record is None:
            return None
        verdict = postcondition.verify_postconditions(
            record.get('checks') or [], read_bytes=read_bytes,
            list_windows=list_windows, dom_observe=dom_observe,
            dir_exists=dir_exists)
        self.record_result(key, passed=(verdict.get('status') == 'verified'))
        return verdict

    def list_procedures(self):
        """All stored records, quarantined included, for audit."""
        return [dict(record) for _, record in
                sorted(self._procedures.items())]

#!/usr/bin/env python3
"""Pick 2: subgoal-only verification plus the reasoning dial.

Prototype for Track 2 of the computer-use speed program (M2 plus M12).
Opt-in only: every rule in this module is inert unless the environment
variable CU_PICK2_SUBGOAL_ONLY is set to a truthy value (``1``, ``true``,
``yes``). Default is OFF, so the baseline loop is byte-identical when the
flag is unset, and other prototype picks can coexist in the same tree.

What the pick changes, when ON:
- Per-step judge and reflection calls are deleted from the loop. The
  supervisor is called only at subgoal boundaries, only when a subgoal
  postcondition fails, when the state is genuinely ambiguous, or when a
  new procedure must be created.
- Inside a subgoal, only local deterministic checks run: postcondition,
  file bytes and SHA-256, window and dialog class, AT-SPI validation.
- Supervisor calls are routed by level. Level 1 (deterministic
  procedure) needs no model call at all. Level 2 (bounded routine
  decision) runs Luna at LOW reasoning effort with a strict JSON schema,
  capped output tokens, and a deterministic postcondition check behind
  it. Level 3 (genuine ambiguity, recovery, new procedure) runs Luna at
  MAX effort, as today. Any level 2 check failure escalates to level 3.
- History is text, not images, past the recent window: only the last
  MAX_FULL_SCREENSHOTS screenshots are kept in full; older observations
  are carried as one compact text line each. Screenshot-only history
  does not help (OSWorld-Human); only text action history does.
- The reasoning dial is per Codex invocation, not per message inside
  one session. ``codex exec`` takes ``-c model_reasoning_effort=...``
  per invocation, and ``codex exec resume`` accepts the same ``-c``
  override for the resumed turn, so level 2 and level 3 run as separate
  invocations (or separate resumed turns) with different flags. See
  ``codex_args_for_level`` and the gate verdict in the pick 2 report.

What the pick NEVER changes (safety invariants):
- Ownership, lease, generation, cancellation (cancel latch,
  check_cancel, idle timeout), and explicit finish.
- Verification itself: the final state is verified from an exact source
  (file bytes and SHA, DOM text, a11y flags) plus a final observation
  image, never from a model asserting its own success.
- Brokered keyboard input: typing goes through the existing wtype path
  in desktop_act, never through a direct write, AT-SPI setter,
  clipboard injection, or browser fill that skips the broker.
- The pointer miss check (over 3px refuses the click) and the
  screen-changed refusal. No level may disable them.
- Low effort NEVER decides an irreversible action. Irreversible
  actions escalate to level 3 even when they look routine.
- Quarantine: a procedure whose checkpoint fails twice in a row is
  quarantined; the next run re-derives layout from a fresh full-frame
  observation.

No em dash or en dash in this file.
"""

import json
import os
from pathlib import Path

PICK2_ENV_VAR = 'CU_PICK2_SUBGOAL_ONLY'

# Supervisor levels. L1 needs no model call, L2 is Luna low plus strict
# JSON, L3 is Luna max.
LEVEL_DETERMINISTIC = 1
LEVEL_ROUTINE = 2
LEVEL_AMBIGUOUS = 3

LEVEL_EFFORT = {
    LEVEL_DETERMINISTIC: None,
    LEVEL_ROUTINE: 'low',
    LEVEL_AMBIGUOUS: 'max',
}

# Level 2 output cap. A bounded routine decision is an action plus a
# target plus a confidence, so it never needs a long answer. The cap is
# enforced by the caller (max output tokens), not by the model.
LEVEL2_MAX_OUTPUT_TOKENS = 512

# Text history: how many recent screenshots stay in full. Older ones
# become one compact text line each (see mask_history).
MAX_FULL_SCREENSHOTS = 2

# Quarantine threshold: consecutive checkpoint failures before a
# procedure is quarantined.
QUARANTINE_AFTER_FAILURES = 2

# Actions no low-effort call may ever decide, even when routine. The
# list is fail-closed: anything not known to be reversible escalates.
IRREVERSIBLE_ACTIONS = frozenset({
    'delete', 'remove', 'overwrite', 'send', 'submit', 'publish',
    'close_without_save', 'shutdown', 'reboot', 'logout', 'format',
    'pay', 'purchase', 'commit', 'push',
})

# Per-step judge/reflect call names. These are the calls Pick 2 deletes
# from inside a subgoal. They are allowed only at a subgoal boundary,
# as a verification call, never as a per-step call.
JUDGE_CALL_NAMES = frozenset({'judge', 'reflect', 'verify_step', 'review_step'})

# Strict JSON schema for a level 2 routine decision. The model returns
# exactly one action, one target, and a confidence in [0, 1]. No extra
# keys, no free text. A malformed decision fails closed instead of
# becoming a misclick.
L2_DECISION_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'type': 'object',
    'additionalProperties': False,
    'required': ['action', 'target', 'confidence'],
    'properties': {
        'action': {'type': 'string', 'minLength': 1, 'maxLength': 64},
        'target': {'type': 'string', 'minLength': 1, 'maxLength': 256},
        'confidence': {'type': 'number', 'minimum': 0.0, 'maximum': 1.0},
    },
}


def pick2_enabled(env=None):
    """True only when the Pick 2 opt-in flag is set. Default OFF."""
    source = os.environ if env is None else env
    value = str(source.get(PICK2_ENV_VAR, '')).strip().lower()
    return value in ('1', 'true', 'yes', 'on')


def effort_for_level(level):
    """Reasoning effort for a supervisor level: None, 'low', or 'max'."""
    if level not in LEVEL_EFFORT:
        raise ValueError(f'unknown supervisor level: {level!r}')
    return LEVEL_EFFORT[level]


def codex_args_for_level(level, *, model='gpt-6-luna'):
    """CLI args for one supervisor call at the given level.

    The dial is per invocation: each level runs as its own
    ``codex exec`` (or resumed turn) with its own ``-c`` flag. Level 1
    needs no model call, so it returns an empty list and the caller
    must not spawn Codex at all.
    """
    effort = effort_for_level(level)
    if effort is None:
        return []
    args = ['-m', model, '-c', f'model_reasoning_effort="{effort}"']
    if level == LEVEL_ROUTINE:
        args += ['--output-schema', str(l2_schema_path())]
    return args


def l2_schema_path():
    """Path of the strict JSON schema file for level 2 decisions."""
    return Path(__file__).resolve().with_name('pick2-l2-schema.json')


def write_l2_schema(path=None):
    """Write the level 2 decision schema to disk (mode 600)."""
    target = Path(path) if path is not None else l2_schema_path()
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, (json.dumps(L2_DECISION_SCHEMA, indent=2) + '\n').encode())
    finally:
        os.close(fd)
    return target


def validate_l2_decision(decision):
    """Validate a level 2 routine decision. Fail closed.

    Returns (True, None) when the decision is well formed and safe for
    a low-effort call, else (False, reason). Reasons: not an object,
    missing or extra keys, empty action/target, confidence outside
    [0, 1], or an irreversible action (never level 2).
    """
    if not isinstance(decision, dict):
        return False, 'decision is not an object'
    keys = set(decision)
    if keys != {'action', 'target', 'confidence'}:
        return False, f'decision keys must be exactly action/target/confidence, got {sorted(keys)}'
    action = decision['action']
    target = decision['target']
    confidence = decision['confidence']
    if not isinstance(action, str) or not action.strip() or len(action) > 64:
        return False, 'action must be a non-empty string of at most 64 chars'
    if not isinstance(target, str) or not target.strip() or len(target) > 256:
        return False, 'target must be a non-empty string of at most 256 chars'
    if (not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or
            not 0.0 <= float(confidence) <= 1.0):
        return False, 'confidence must be a number in [0, 1]'
    if action.strip().lower() in IRREVERSIBLE_ACTIONS:
        return False, f'irreversible action {action!r} may never be decided at level 2'
    return True, None


def classify_decision(*, is_procedure_step, is_irreversible, is_ambiguous,
                      has_postcondition_check):
    """Route one supervisor decision to level 1, 2, or 3.

    - Deterministic procedure step with a postcondition check: level 1,
      no model call.
    - Bounded routine decision with a deterministic postcondition check
      behind it: level 2, Luna low plus strict JSON.
    - Genuine ambiguity, recovery, a new procedure, an irreversible
      action, or a routine decision with no postcondition check to catch
      it: level 3, Luna max.
    """
    if is_ambiguous or is_irreversible:
        return LEVEL_AMBIGUOUS
    if is_procedure_step and has_postcondition_check:
        return LEVEL_DETERMINISTIC
    if has_postcondition_check:
        return LEVEL_ROUTINE
    return LEVEL_AMBIGUOUS


def judge_allowed(*, at_subgoal_boundary):
    """Per-step judge/reflect is allowed only at a subgoal boundary.

    Inside a subgoal the answer is always False: the call is deleted,
    and only local deterministic checks run. At a subgoal boundary the
    supervisor may verify the subgoal postcondition.
    """
    return bool(at_subgoal_boundary)


def validate_plan_has_no_mid_step_judge(plan):
    """Fail a plan that hides a judge/reflect call inside a subgoal.

    A step may declare judge/reflect work only when it is marked as a
    subgoal boundary (``subgoal_boundary: true``). Anything else raises
    ValueError with the offending step id. Plans without judge calls
    pass unchanged.
    """
    steps = plan.get('steps', []) if isinstance(plan, dict) else []
    for step in steps:
        if not isinstance(step, dict):
            continue
        calls = step.get('calls', []) or step.get('supervisor_calls', [])
        bad = [name for name in calls if name in JUDGE_CALL_NAMES]
        if bad and not step.get('subgoal_boundary'):
            raise ValueError(
                f"{step.get('id', '?')}: judge/reflect call {bad} inside a subgoal; "
                'move verification to the subgoal boundary')
    return True


def text_history_line(observation):
    """One compact text line summarising an older observation.

    Older screenshots leave the prompt entirely; only this line stays,
    so history grows as text, not as images.
    """
    if not isinstance(observation, dict):
        return 'obs: (unrecorded observation)'
    label = observation.get('label') or observation.get('id') or 'unknown'
    window = observation.get('window') or observation.get('address') or ''
    note = observation.get('text_summary') or observation.get('summary') or ''
    line = f'obs {label}: window {window}'.strip()
    if note:
        line += f' {note}'
    return line


def mask_history(observations, *, keep_full=MAX_FULL_SCREENSHOTS):
    """Split observation history into full images and text lines.

    Returns (full, text_lines): the last ``keep_full`` observations
    stay in full (the model still sees recent pixels); every older one
    becomes one compact text line. With fewer observations than
    ``keep_full``, nothing is masked.
    """
    if keep_full < 0:
        raise ValueError('keep_full must be zero or more')
    items = list(observations or [])
    if keep_full >= len(items):
        return items, []
    full = items[-keep_full:] if keep_full else []
    masked = items[:len(items) - keep_full] if keep_full else items
    return full, [text_history_line(item) for item in masked]


def verify_subgoal(checks):
    """Run deterministic subgoal postcondition checks, no model call.

    ``checks`` is a list of (name, passed, detail) triples produced by
    local checks only (file bytes and SHA, window/dialog class, AT-SPI
    validation). Returns (passed, failed_names, details). A subgoal
    passes only when every check passes.
    """
    failed = []
    details = {}
    for name, passed, detail in checks:
        details[name] = detail
        if not passed:
            failed.append(name)
    return (not failed), failed, details


def should_escalate(*, postcondition_passed, is_ambiguous, needs_new_procedure):
    """Escalate to level 3 (max effort) when any of these holds."""
    return (not postcondition_passed) or bool(is_ambiguous) or bool(needs_new_procedure)


class QuarantineTracker:
    """Count consecutive checkpoint failures per procedure.

    A procedure whose checkpoint fails twice in a row is quarantined:
    the next run re-derives layout from a fresh full-frame observation
    instead of trusting the stored procedure.
    """

    def __init__(self, *, threshold=QUARANTINE_AFTER_FAILURES):
        self.threshold = threshold
        self._failures = {}
        self._quarantined = set()

    def record(self, procedure, *, passed):
        if passed:
            self._failures[procedure] = 0
            return False
        count = self._failures.get(procedure, 0) + 1
        self._failures[procedure] = count
        if count >= self.threshold:
            self._quarantined.add(procedure)
        return procedure in self._quarantined

    def is_quarantined(self, procedure):
        return procedure in self._quarantined

    def consecutive_failures(self, procedure):
        return self._failures.get(procedure, 0)


class DetectionLagTracker:
    """Count actions that ran before a bad action was detected.

    Pick 2 detects bad actions one subgoal later instead of one step
    later, so the lag is measured in actions, not in time. A bad action
    that completes a destructive step is a failure of the pick, not a
    lag to report: the caller must check irreversibility before
    counting.
    """

    def __init__(self):
        self.actions_since_subgoal_start = 0
        self.lag_at_detection = None

    def record_action(self):
        self.actions_since_subgoal_start += 1

    def record_subgoal_boundary(self):
        self.actions_since_subgoal_start = 0

    def record_bad_action_detected(self):
        self.lag_at_detection = self.actions_since_subgoal_start
        return self.lag_at_detection

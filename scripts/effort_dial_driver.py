#!/usr/bin/env python3
"""Resume-per-turn reasoning-effort dial driver (Track 2, M1 prototype).

The executor loop runs as ONE long ``codex exec`` process, and there is
no per-message effort override inside that process. A dial therefore
means driving the loop as RESUME-PER-TURN: separate CLI processes
sharing one session id, each resumed turn carrying its own
``-c model_reasoning_effort=...`` flag.

MEASUREMENT VERDICT (2026-11-19, Codex CLI 0.169.0): the resume
per-turn dial does NOT work. Per-turn ``-c model_reasoning_effort``
on ``codex exec resume`` (and ``fork``) is accepted but does not move
reasoning tokens: same-prompt F2 gives 221 reasoning on a resume-max
turn in a low session and 430 on a resume-low turn in a max session.
The outcome tracks the session's bootstrap effort, not the flag.
Fresh-exec low vs max on the same forcing prompt is 0 vs 285-430
reasoning tokens, so the flag works per invocation only. Do NOT run
the P1-P4 A/B with this driver until a working per-step mechanism is
proven; the dial arm would run every turn at the bootstrap effort.
See ``improvements/effort-dial-validation.md`` for the full evidence.
The driver itself is a correct, unit-tested resume-per-turn harness;
only the dial premise is falsified.

This driver is the harness for that shape. It:

- bootstraps one Codex session with the dial brief (max effort),
- runs a plan of steps as resumed turns, one step per turn,
- picks the effort per step from the supervisor level
  (``scripts/subgoal_policy.py``): routine steps run at LOW effort with
  the strict L2 JSON schema, act composition / ambiguity / recovery /
  irreversible steps run at MAX, deterministic procedure steps need no
  model call at all,
- validates every low-effort turn (strict JSON + irreversible-action
  ban) and runs a deterministic postcondition check behind it
  (broker record, file bytes, reply text, or a local command),
- escalates exactly once to MAX on a failed validation or a failed
  postcondition, then fails the task if the retry also fails,
- logs every turn (effort, wall, input/cached/reasoning/output
  tokens, validation, postcondition, escalation) to turns.jsonl and
  writes summary.md.

What the driver NEVER does: it never executes task actions itself
(no local typing, no broker act, no file writes for the task). The
model still performs every desktop action through the broker inside
its resumed turns. The driver only reads harness artifacts
(run-dir records.jsonl, task end-state files) to decide escalation.
That keeps the A/B honest: the dial arm is still a model loop, just
one driven turn by turn at mixed effort.

Usage:
  python3 scripts/effort_dial_driver.py --run-dir DIR --brief FILE \
      --plan FILE [--session-id ID] [--repo DIR] [--arm NAME]

The plan is JSON: {"tasks": [{"id", "title", "steps": [...]}]}.
Each step: {"label", "kind", "prompt", "level" (1/2/3, optional),
"is_procedure_step", "is_irreversible", "is_ambiguous",
"has_postcondition_check", "postcondition": {...}}.
Without an explicit level the step is classified with
subgoal_policy.classify_decision.

No em dash or en dash in this file.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import subgoal_policy as sp

MODEL_DEFAULT = 'gpt-6-luna'
SANDBOX_DEFAULT = 'danger-full-access'
TURN_TIMEOUT_S = 600
MAX_ESCALATIONS_PER_STEP = 1


# ---------------------------------------------------------------- JSONL ---

def parse_codex_jsonl(text):
    """Parse one ``codex exec --json`` stream.

    Returns a dict with:
      session_id: from the first thread.started event, else None.
      usage: from the last turn.completed event, else None.
      last_message: text of the last agent_message item, else None.
      events: count of parsed JSON lines.
    Malformed lines are skipped, never fatal.
    """
    session_id = None
    usage = None
    last_message = None
    events = 0
    for line in (text or '').splitlines():
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events += 1
        kind = event.get('type')
        if kind == 'thread.started' and session_id is None:
            candidate = event.get('thread_id')
            if isinstance(candidate, str) and candidate:
                session_id = candidate
        elif kind == 'turn.completed':
            candidate = event.get('usage')
            if isinstance(candidate, dict):
                usage = candidate
        elif kind == 'item.completed':
            item = event.get('item')
            if isinstance(item, dict) and item.get('type') == 'agent_message':
                text_value = item.get('text')
                if isinstance(text_value, str):
                    last_message = text_value
    return {
        'session_id': session_id,
        'usage': usage,
        'last_message': last_message,
        'events': events,
    }


def usage_numbers(usage):
    """Normalise a turn.completed usage dict to ints (missing -> 0)."""
    usage = usage or {}
    def _int(key):
        value = usage.get(key)
        return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0
    return {
        'input_tokens': _int('input_tokens'),
        'cached_input_tokens': _int('cached_input_tokens'),
        'reasoning_output_tokens': _int('reasoning_output_tokens'),
        'output_tokens': _int('output_tokens'),
    }


# ------------------------------------------------------------- CLI args ---

def build_exec_args(*, model, effort, sandbox, workdir, last_file, prompt):
    """Fresh ``codex exec`` argv for the bootstrap turn (max effort)."""
    return [
        'codex', 'exec', '--json', '--skip-git-repo-check',
        '-m', model, '-c', 'model_reasoning_effort="%s"' % effort,
        '-s', sandbox, '-C', str(workdir), '-o', str(last_file),
        prompt,
    ]


def build_resume_args(*, model, effort, last_file, session_id, prompt, level):
    """``codex exec resume`` argv for one dial turn.

    Resume accepts -c/-m/--json/--output-schema/-o but NOT -s/-C:
    sandbox and workdir are session-level, fixed by the bootstrap
    ``codex exec`` and inherited by every resumed turn. Passing -s
    makes resume exit rc=2 with "unexpected argument '-s' found"
    (measured 19/11). Level 2 (routine) turns carry the strict L2
    JSON schema so the final message is a machine-checkable decision.
    Level 3 turns are free-form; only the postcondition judges them.
    """
    args = [
        'codex', 'exec', 'resume', '--json', '--skip-git-repo-check',
        '-m', model, '-c', 'model_reasoning_effort="%s"' % effort,
        '-o', str(last_file),
    ]
    if level == sp.LEVEL_ROUTINE:
        args += ['--output-schema', str(sp.l2_schema_path())]
    args += [session_id, prompt]
    return args


# --------------------------------------------------------- postconditions ---

def _last_broker_record(run_dir):
    """Last JSON line of the harness records file, else (None, reason)."""
    path = Path(run_dir) / 'records.jsonl'
    if not path.exists():
        return None, 'no records.jsonl in run dir'
    lines = [line for line in path.read_text(encoding='utf-8', errors='replace').splitlines()
             if line.strip()]
    if not lines:
        return None, 'records.jsonl is empty'
    try:
        return json.loads(lines[-1]), ''
    except json.JSONDecodeError:
        return None, 'last records.jsonl line is not JSON'


def _record_has_error(record):
    """True when a broker record signals failure at any level."""
    if not isinstance(record, dict):
        return True
    if record.get('accepted') is False:
        return True
    if record.get('error'):
        return True
    if record.get('ok') is False:
        return True
    result = record.get('result')
    if isinstance(result, dict):
        if result.get('ok') is False:
            return True
        if result.get('error'):
            return True
    return False


def _record_completed(record):
    """Completed-action count from a broker record, else None."""
    if not isinstance(record, dict):
        return None
    for container in (record, record.get('result')):
        if isinstance(container, dict) and isinstance(container.get('completed'), (int, float)):
            return int(container['completed'])
    return None


def check_postcondition(spec, *, run_dir, last_message):
    """Run one deterministic postcondition. Fail closed.

    Returns (passed, detail). Unknown spec types fail: a check the
    driver cannot understand must escalate, never silently pass.
    Supported types: none, broker_ok, file_exists, file_exact_lines,
    file_contains, reply_contains, command_ok.
    """
    if not isinstance(spec, dict):
        return False, 'postcondition spec is not an object'
    kind = spec.get('type')
    if kind == 'none':
        return True, 'no check required'
    if kind == 'broker_ok':
        record, reason = _last_broker_record(run_dir)
        if record is None:
            return False, reason
        if _record_has_error(record):
            return False, 'last broker record signals an error: %s' % json.dumps(record)[:300]
        minimum = spec.get('min_completed')
        if minimum is not None:
            completed = _record_completed(record)
            if completed is None:
                return False, 'last broker record has no completed count'
            if completed < int(minimum):
                return False, 'completed %d < required %d' % (completed, int(minimum))
        return True, 'last broker record ok'
    if kind == 'file_exists':
        path = Path(spec.get('path', ''))
        return (path.exists(), 'exists' if path.exists() else 'missing: %s' % path)
    if kind == 'file_exact_lines':
        path = Path(spec.get('path', ''))
        expected = spec.get('lines')
        if not isinstance(expected, list):
            return False, 'file_exact_lines needs a lines list'
        if not path.exists():
            return False, 'missing file: %s' % path
        actual = path.read_text(encoding='utf-8').splitlines()
        if actual == expected:
            return True, 'exact lines match (%d lines)' % len(expected)
        return False, 'lines differ: got %r' % (actual,)
    if kind == 'file_contains':
        path = Path(spec.get('path', ''))
        needle = spec.get('text', '')
        if not path.exists():
            return False, 'missing file: %s' % path
        content = path.read_text(encoding='utf-8', errors='replace')
        return (needle in content, 'contains %r' % needle if needle in content
                else 'file does not contain %r' % needle)
    if kind == 'reply_contains':
        needle = spec.get('text', '')
        message = last_message or ''
        return (needle in message, 'reply contains %r' % needle if needle in message
                else 'reply does not contain %r' % needle)
    if kind == 'command_ok':
        argv = spec.get('argv')
        if not isinstance(argv, list) or not argv:
            return False, 'command_ok needs a non-empty argv list'
        try:
            proc = subprocess.run(argv, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=30, text=True)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, 'command failed to run: %s' % exc
        if proc.returncode == 0:
            return True, 'command exited 0'
        return False, 'command exited %d: %s' % (proc.returncode, (proc.stderr or '').strip()[:200])
    return False, 'unknown postcondition type: %r' % (kind,)


def end_state_precheck(spec, *, run_dir):
    """True when an end-state postcondition already passes.

    Only file-based checks are pre-checkable: if the end state already
    exists (a previous turn chained ahead), the step is skipped instead
    of re-run. Broker and reply checks are never pre-checked: they
    describe the turn itself, not durable state.
    """
    if not isinstance(spec, dict):
        return False
    if spec.get('type') in ('file_exists', 'file_exact_lines', 'file_contains'):
        passed, _ = check_postcondition(spec, run_dir=run_dir, last_message='')
        return passed
    return False


# ---------------------------------------------------------------- driver ---

def step_level(step):
    """Supervisor level for a plan step (explicit level wins)."""
    explicit = step.get('level')
    if explicit is not None:
        level = int(explicit)
        if level not in (sp.LEVEL_DETERMINISTIC, sp.LEVEL_ROUTINE, sp.LEVEL_AMBIGUOUS):
            raise ValueError('step %r has unknown level %r' % (step.get('label'), explicit))
        return level
    spec = step.get('postcondition') or {}
    has_check = bool(spec) and spec.get('type') not in (None, 'none')
    return sp.classify_decision(
        is_procedure_step=bool(step.get('is_procedure_step', False)),
        is_irreversible=bool(step.get('is_irreversible', False)),
        is_ambiguous=bool(step.get('is_ambiguous', False)),
        has_postcondition_check=has_check)


def default_runner(argv, timeout_s):
    """Run one codex invocation, return (rc, stdout, stderr, wall_s)."""
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=timeout_s, text=True)
        return proc.returncode, proc.stdout, proc.stderr, time.monotonic() - started
    except subprocess.TimeoutExpired:
        return 124, '', 'codex invocation timed out after %ss' % timeout_s, time.monotonic() - started


class EffortDialDriver:
    """Drive one Codex session turn by turn at mixed reasoning effort."""

    def __init__(self, *, run_dir, repo_dir, workdir, model=MODEL_DEFAULT,
                 sandbox=SANDBOX_DEFAULT, timeout_s=TURN_TIMEOUT_S,
                 runner=None, arm='effortdial'):
        self.run_dir = Path(run_dir)
        self.repo_dir = Path(repo_dir)
        self.workdir = Path(workdir)
        self.model = model
        self.sandbox = sandbox
        self.timeout_s = timeout_s
        self.runner = runner or default_runner
        self.arm = arm
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.turns_path = self.run_dir / 'turns.jsonl'
        self.turn_count = 0

    # -- logging --

    def log_turn(self, record):
        record = dict(record)
        record['turn'] = self.turn_count
        self.turn_count += 1
        with open(self.turns_path, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
        os.chmod(self.turns_path, 0o600)
        return record

    # -- session --

    def start_session(self, brief_text, *, label='bootstrap'):
        """Bootstrap turn at max effort. Returns the session id."""
        last_file = self.run_dir / 'last-bootstrap.txt'
        argv = build_exec_args(model=self.model, effort=sp.LEVEL_EFFORT[sp.LEVEL_AMBIGUOUS],
                               sandbox=self.sandbox, workdir=self.workdir,
                               last_file=last_file, prompt=brief_text)
        rc, stdout, stderr, wall = self.runner(argv, self.timeout_s)
        parsed = parse_codex_jsonl(stdout)
        last_message = last_file.read_text(encoding='utf-8', errors='replace') if last_file.exists() else parsed['last_message']
        self.log_turn({
            'label': label, 'kind': 'bootstrap', 'level': sp.LEVEL_AMBIGUOUS,
            'effort': 'max', 'model_call': True, 'wall_s': round(wall, 3),
            'rc': rc, 'stderr_tail': (stderr or '').strip().splitlines()[-1:] ,
            'session_id': parsed['session_id'],
            **usage_numbers(parsed['usage']),
            'validated': None, 'validation_error': None,
            'postcondition_ok': None, 'postcondition_detail': 'bootstrap has no postcondition',
            'escalated': False, 'skipped': False,
        })
        if rc != 0:
            raise RuntimeError('bootstrap codex exec failed rc=%d: %s' % (rc, (stderr or '').strip()[:500]))
        if not parsed['session_id']:
            raise RuntimeError('bootstrap produced no thread.started session id')
        return parsed['session_id']

    # -- one step --

    def run_step(self, session_id, step):
        """Run one plan step as resumed turn(s). Returns (ok, record)."""
        label = step.get('label', '?')
        kind = step.get('kind', 'routine')
        level = step_level(step)
        effort = sp.effort_for_level(level)
        spec = step.get('postcondition') or {'type': 'none'}

        if level == sp.LEVEL_DETERMINISTIC:
            passed, detail = check_postcondition(spec, run_dir=self.run_dir, last_message='')
            record = self.log_turn({
                'label': label, 'kind': kind, 'level': level, 'effort': None,
                'model_call': False, 'wall_s': 0.0, 'rc': 0,
                'session_id': session_id,
                'input_tokens': 0, 'cached_input_tokens': 0,
                'reasoning_output_tokens': 0, 'output_tokens': 0,
                'validated': True, 'validation_error': None,
                'postcondition_ok': passed, 'postcondition_detail': detail,
                'escalated': False, 'skipped': False,
            })
            return passed, record

        if end_state_precheck(spec, run_dir=self.run_dir):
            record = self.log_turn({
                'label': label, 'kind': kind, 'level': level, 'effort': effort,
                'model_call': False, 'wall_s': 0.0, 'rc': 0,
                'session_id': session_id,
                'input_tokens': 0, 'cached_input_tokens': 0,
                'reasoning_output_tokens': 0, 'output_tokens': 0,
                'validated': None, 'validation_error': None,
                'postcondition_ok': True,
                'postcondition_detail': 'end state already satisfied, step skipped',
                'escalated': False, 'skipped': True,
            })
            return True, record

        ok, record = self._one_turn(session_id, step, level, effort, attempt=0)
        if ok:
            return True, record
        if MAX_ESCALATIONS_PER_STEP < 1:
            return False, record
        reason = record.get('validation_error') or record.get('postcondition_detail') or 'turn failed'
        escalation_prompt = (
            'ESCALATION, max effort. The previous %s turn for step %s failed: %s. '
            'Redo the step carefully from the current state. Do not repeat the '
            'failed move. End with a short status line stating what you did '
            'and what the broker returned.'
            % (effort, label, reason))
        ok, record = self._one_turn(session_id, step, sp.LEVEL_AMBIGUOUS, 'max',
                                    attempt=1, prompt_override=escalation_prompt,
                                    escalated=True)
        return ok, record

    def _one_turn(self, session_id, step, level, effort, *, attempt, prompt_override=None,
                  escalated=False):
        label = step.get('label', '?')
        kind = step.get('kind', 'routine')
        prompt = prompt_override if prompt_override is not None else step.get('prompt', '')
        # Plan prompts may carry the same placeholders as the brief.
        prompt = (prompt.replace('__RUN_DIR__', str(self.run_dir))
                        .replace('__ARM__', self.arm)
                        .replace('__REPO__', str(self.repo_dir)))
        last_file = self.run_dir / ('last-%s-%d.txt' % (label, attempt))
        argv = build_resume_args(model=self.model, effort=effort,
                                 last_file=last_file,
                                 session_id=session_id, prompt=prompt, level=level)
        rc, stdout, stderr, wall = self.runner(argv, self.timeout_s)
        parsed = parse_codex_jsonl(stdout)
        last_message = None
        if last_file.exists():
            last_message = last_file.read_text(encoding='utf-8', errors='replace')
            os.chmod(last_file, 0o600)
        if not last_message:
            last_message = parsed['last_message']
        validated, validation_error = self._validate_turn(level, last_message, rc)
        spec = step.get('postcondition') or {'type': 'none'}
        if rc == 0 and validated:
            post_ok, post_detail = check_postcondition(spec, run_dir=self.run_dir,
                                                       last_message=last_message)
        elif rc != 0:
            post_ok, post_detail = False, 'codex rc=%d: %s' % (rc, (stderr or '').strip()[:300])
        else:
            post_ok, post_detail = False, 'skipped: validation failed'
        ok = bool(rc == 0 and validated and post_ok)
        record = self.log_turn({
            'label': label, 'kind': kind, 'level': level, 'effort': effort,
            'model_call': True, 'wall_s': round(wall, 3), 'rc': rc,
            'stderr_tail': (stderr or '').strip().splitlines()[-1:],
            'session_id': session_id, 'attempt': attempt,
            **usage_numbers(parsed['usage']),
            'validated': validated, 'validation_error': validation_error,
            'postcondition_ok': post_ok, 'postcondition_detail': post_detail,
            'escalated': escalated, 'skipped': False,
        })
        return ok, record

    def _validate_turn(self, level, last_message, rc):
        """Validate one turn's final message. Level 2 is strict JSON."""
        if rc != 0:
            return False, 'codex rc=%d' % rc
        if level != sp.LEVEL_ROUTINE:
            return True, None
        if not last_message or not last_message.strip():
            return False, 'empty final message on a level 2 turn'
        try:
            decision = json.loads(last_message.strip())
        except json.JSONDecodeError:
            return False, 'final message is not JSON: %r' % (last_message.strip()[:200],)
        valid, reason = sp.validate_l2_decision(decision)
        if not valid:
            return False, reason
        return True, None

    # -- whole plan --

    def run_plan(self, session_id, plan):
        """Run every task in a plan. Returns {task_id: (ok, failed_label)}."""
        results = {}
        for task in plan.get('tasks', []):
            task_id = task.get('id', '?')
            failed_label = None
            for step in task.get('steps', []):
                ok, _ = self.run_step(session_id, step)
                if not ok:
                    failed_label = step.get('label', '?')
                    break
            results[task_id] = (failed_label is None, failed_label)
        return results

    def write_summary(self, results):
        """summary.md: totals plus per-task outcome. Returns the path."""
        turns = []
        if self.turns_path.exists():
            for line in self.turns_path.read_text(encoding='utf-8').splitlines():
                if line.strip():
                    turns.append(json.loads(line))
        model_turns = [t for t in turns if t.get('model_call')]
        low_turns = [t for t in model_turns if t.get('effort') == 'low']
        max_turns = [t for t in model_turns if t.get('effort') == 'max']
        escalations = [t for t in turns if t.get('escalated')]
        total_wall = sum(t.get('wall_s', 0) for t in turns)
        total_reasoning = sum(t.get('reasoning_output_tokens', 0) for t in model_turns)
        low_reasoning = sum(t.get('reasoning_output_tokens', 0) for t in low_turns)
        max_reasoning = sum(t.get('reasoning_output_tokens', 0) for t in max_turns)
        lines = [
            '# Effort-dial run summary (arm %s)' % self.arm,
            '',
            '- Model turns: %d (low %d, max %d)' % (len(model_turns), len(low_turns), len(max_turns)),
            '- Deterministic (no model call) turns: %d' % len([t for t in turns if not t.get('model_call')]),
            '- Escalations to max: %d' % len(escalations),
            '- Total model-turn wall: %.1fs' % total_wall,
            '- Total reasoning tokens: %d (low %d, max %d)' % (total_reasoning, low_reasoning, max_reasoning),
            '- Total input tokens: %d (cached %d)' % (
                sum(t.get('input_tokens', 0) for t in model_turns),
                sum(t.get('cached_input_tokens', 0) for t in model_turns)),
            '',
            '## Tasks',
            '',
        ]
        for task_id, (ok, failed_label) in results.items():
            lines.append('- %s: %s' % (task_id, 'PASS' if ok else 'FAIL at %s' % failed_label))
        lines.append('')
        lines.append('## Turns')
        lines.append('')
        lines.append('| turn | label | effort | wall_s | reasoning | validated | postcondition | escalated |')
        lines.append('| --- | --- | --- | --- | --- | --- | --- | --- |')
        for t in turns:
            lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                t.get('turn'), t.get('label'), t.get('effort'),
                t.get('wall_s'), t.get('reasoning_output_tokens'),
                t.get('validated'), t.get('postcondition_ok'), t.get('escalated')))
        path = self.run_dir / 'summary.md'
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        os.chmod(path, 0o600)
        return path


def load_plan(path):
    try:
        with open(path, encoding='utf-8') as handle:
            plan = json.load(handle)
    except OSError as exc:
        raise ValueError('cannot read plan %s: %s' % (path, exc))
    except json.JSONDecodeError as exc:
        raise ValueError('plan %s is not valid JSON: %s' % (path, exc))
    if not isinstance(plan, dict) or not isinstance(plan.get('tasks'), list):
        raise ValueError('plan must be an object with a tasks list')
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description='Resume-per-turn effort-dial driver.')
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--brief', required=True, help='dial brief file (bootstrap prompt)')
    parser.add_argument('--plan', required=True, help='plan JSON file')
    parser.add_argument('--session-id', default=None, help='resume this session instead of bootstrapping')
    parser.add_argument('--repo', default=str(ROOT))
    parser.add_argument('--workdir', default='/tmp/effortdial-work')
    parser.add_argument('--model', default=MODEL_DEFAULT)
    parser.add_argument('--sandbox', default=SANDBOX_DEFAULT)
    parser.add_argument('--timeout-s', type=int, default=TURN_TIMEOUT_S)
    parser.add_argument('--arm', default='effortdial')
    args = parser.parse_args(argv)

    brief_text = Path(args.brief).read_text(encoding='utf-8')
    brief_text = brief_text.replace('__REPO__', args.repo)
    brief_text = brief_text.replace('__RUN_DIR__', args.run_dir)
    brief_text = brief_text.replace('__ARM__', args.arm)
    plan = load_plan(args.plan)

    driver = EffortDialDriver(run_dir=args.run_dir, repo_dir=args.repo,
                              workdir=args.workdir, model=args.model,
                              sandbox=args.sandbox, timeout_s=args.timeout_s,
                              arm=args.arm)
    session_id = args.session_id or driver.start_session(brief_text)
    print('session: %s' % session_id)
    results = driver.run_plan(session_id, plan)
    summary = driver.write_summary(results)
    print('summary: %s' % summary)
    for task_id, (ok, failed_label) in results.items():
        print('%s: %s' % (task_id, 'PASS' if ok else 'FAIL at %s' % failed_label))
    return 0 if all(ok for ok, _ in results.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""First visible action: overlay on + move first, diagnose after.

Root causes fixed (see improvements/worker-f2-silence-fix-log.md):
- R1: no structural fast path; the agent's default loop is research-first.
  On 2026-11-21 the order-to-first-click was about 5.5 min while the click
  itself took 0.31 s.
- R2: the session guardian fails fast (the cursor guard is not loaded in
  the live Hyprland) with a swallowed error; the agent diagnosed it
  silently for minutes instead of falling back.
- R3: the overlay is not tied to any action; the direct Pointer path never
  shows it, so a session failure means an invisible run.
- R4: observe -> session -> act is three serial failure points before any
  visible action.

Design (precedents: dsh-computer-use-win's tool-enforced overlay gate,
@agent-sh/computer-use-linux's server-driven indicator, cua-speedrun's
timing split):
- D1: overlay acquire is a precondition of any pointer action, enforced
  in code. If the overlay cannot be shown, the run refuses loudly and
  never acts invisibly. The overlay is re-checked immediately before
  the fallback acts (A5): a dead daemon mid-run means refusal, not an
  invisible fallback.
- D2: overlay first; the move follows as soon as the session attempt
  resolves or times out (deadline 20 s). The overlay is the first
  visible action; the first pointer move is bounded by the total batch
  time, not separately measured.
- D3: session start has a hard deadline; on a session-START failure the
  run falls back to the direct Pointer path (the same desktop_act the
  session path uses) with the overlay already on, and logs the bypass
  with the guardian's real error. A start failure is proven ONLY by the
  session command's own error envelope: the parsed stdout JSON error
  starts with 'session guardian startup failed' or 'driver registration
  failed'. Both are emitted by supervise before the driver can act
  (cursor_session.py:275, :290), so they prove no action ran. A timeout
  NEVER falls back: the driver may have acted and been torn down, and a
  post-kill liveness probe cannot distinguish "never started" from
  "started, acted, and was just torn down" (council 1, B1). An act
  failure after the session started is NEVER replayed: actions may
  have partially run.
- D4: order-to-first-visible-action is measured on every run; target
  under 30 s. Timings start at command start: they exclude agent
  decision and observation time, so the under-30 s rule from a user
  order is not yet demonstrated end to end. order_to_session_attempt_ms
  is the session-attempt start, not the first pointer move. The 30 s
  target is measured post-hoc from the envelope, not code-enforced.
  CB-7 (step 0): the envelope records target_breached when the FIRST
  POINTER action exceeds 30 s from t0 (first_pointer_ms, basis
  recorded), not when the whole run does; the whole-batch comparison
  survives only as an explicit total_fallback basis when no pointer
  action completed. dispatch_ms splits VM send + SSH connect + shell
  startup off laptop work, from the order wall time passed with
  --order-wall or CU_ORDER_WALL. phase_ms splits overlay acquire,
  observation, session attempt, and after-capture per run (CB-10);
  think time is measured by the P6 harness in the agent loop, never
  here. Every capture pins its capture params (P6c): one max_width
  (960, CB-3 uniformity), JPEG q90 4:4:4.

Usage (one command, the agent's default for a live action batch):
  computer-use act-now --actions <file> [--observation <path>]
      [--screen <monitor>] [--agent NAME] [--method METHOD]
      [--label TEXT] [--session-deadline-s N]

The actions file is the same JSON batch `act` takes (up to 32 actions).
The observation, when given, must be fresh (under 120 s); a given
observation that is stale, missing, or unreadable is NEVER silently
replaced by a screen capture that the batch then acts on (G28): the
run refuses loudly instead, for any batch, naming the given
observation, why it was rejected, and what to pass. When no
observation is given (source captured, screen scope), a batch bound
to a window scope or another observation is likewise refused
loudly (R7): window-space points never run on a screen capture. The overlay is acquired
before anything else, so the pill is visible within about a second of
the command starting. The run appends a JSON timing record to
STATE/first-action-YYYYMMDD.jsonl. Every invocation prints exactly one
JSON envelope on stdout and appends exactly one log line, including
refusals and bad input.
"""
import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))

import action_result

OBSERVATION_MAX_AGE_S = 120
DEFAULT_SESSION_DEADLINE_S = 20.0
FIRST_VISIBLE_ACTION_TARGET_MS = 30000

# Positive start-failure signals (council 1, B2). Both are raised by
# supervise before the driver can act: 'session guardian startup
# failed' before the driver is spawned (cursor_session.py:275), and
# 'driver registration failed' before the 'go' gate byte is written
# (cursor_session.py:290), so the driver is spawned but gated and
# cannot execute input. Any other error string (mid-session guard
# loss, a late hyprctl JSON failure, an act refusal) is NOT a start
# failure and must never trigger a fallback.
START_FAILURE_PREFIXES = ('session guardian startup failed',
                          'driver registration failed')


def _ms(start):
    return round((time.monotonic() - start) * 1000, 3)


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec='milliseconds')


def acquire_overlay(agent, method, label=None, overlay_mod=None):
    """Acquire the overlay pill. Returns the daemon reply dict.

    Raises RuntimeError when the pill is not visible afterwards. The
    caller must treat that as a refusal, never as a reason to act
    invisibly. overlay_mod is injectable for tests; otherwise the real
    overlay module is imported. If any step after add_holder fails,
    the holder is removed again, so a failed acquire never leaks a
    holder that keeps the pill and daemon up for a dead process
    (council 1, A1).
    """
    if overlay_mod is None:
        import overlay as overlay_mod
    pid = os.getpid()
    overlay_mod.add_holder(agent, method, pid=pid)
    try:
        overlay_mod._ensure_daemon()
        reply = overlay_mod._send_socket(
            {'command': 'acquire', 'agent': agent, 'method': method,
             'pid': pid})
        if not isinstance(reply, dict) or reply.get('visible') is not True:
            raise RuntimeError(
                'overlay unavailable: ' + json.dumps(reply, sort_keys=True))
        if label is None:
            label = overlay_mod._label_for(agent, method)
    except Exception:
        try:
            overlay_mod.remove_holder(agent, pid)
        except Exception:
            pass
        raise
    return reply


def overlay_visible(agent, overlay_mod=None):
    """True only when the overlay daemon reports the pill visible.

    Uses a 'sync' round trip, which runs apply_holders and therefore
    requires a live show ack (redteam A3): a 'status' reply only says
    holders exist, not that the pill rendered. A dead daemon (socket
    error) or a failed show reports False, never raises.
    """
    try:
        if overlay_mod is None:
            import overlay as overlay_mod
        reply = overlay_mod._send_socket({'command': 'sync'})
        return isinstance(reply, dict) and reply.get('visible') is True
    except Exception:
        return False


def release_overlay(agent, overlay_mod=None):
    """Release the overlay holder. Returns None on success, else an
    error string. Never raises; the caller records a failure in the
    envelope instead of swallowing it silently (council 1, A5). Only
    this run's entry is removed (redteam A4): the pid is sent with
    the release so a concurrent same-agent run keeps its pill."""
    try:
        if overlay_mod is None:
            import overlay as overlay_mod
        pid = os.getpid()
        try:
            overlay_mod._send_socket({'command': 'release', 'agent': agent,
                                      'pid': pid})
        except (OSError, ValueError):
            overlay_mod.remove_holder(agent, pid)
        return None
    except Exception as exc:
        return str(exc)


def session_cmd(cu_py, observation_path, actions_path):
    """DELETED in step 8 (S1/CB-6). Kept as a stub that always fails.

    The per-batch session spawn (`cu.py session -- cu.py act ...`) is
    gone: act-now routes the batch through the long-lived session
    driver held by the broker (see broker_attempt). Any caller still
    building a session command gets a loud failure instead of a
    silently resurrected spawn.
    """
    raise RuntimeError('session_cmd was deleted in step 8: act-now routes '
                       'through the broker (broker_attempt), it no longer '
                       'spawns a session per batch')


def attempt_session(cmd, deadline_s, env=None):
    """DELETED in step 8 (S1/CB-6). Kept as a stub that always fails.

    The per-batch session spawn is gone (see session_cmd). Use
    broker_attempt, which returns the same 5-tuple shape plus a
    detail dict.
    """
    raise RuntimeError('attempt_session was deleted in step 8: act-now '
                       'routes through the broker (broker_attempt), it no '
                       'longer spawns a session per batch')


# Step 8 (S1/CB-6): act-now routes through the long-lived session
# driver held by the broker (scripts/session_remote.py, relay socket),
# never a per-batch session spawn. The broker enforces one owner at a
# time; the queue discipline (wait/refuse/timeout for the second
# queued batch) lives in session_remote._client_start_with_wait and is
# decided in improvements/worker-click5-step8-log.md section 4. The
# fresh-SSH one-shot path (`cu.py session -- cu.py session-driver`,
# JSONL over stdin) is NOT in this file and never was: it is the
# VM-side fallback and recovery path, documented in the step-8 log
# section 6, used when the broker is down.
BROKER_WAIT_S = 300.0
BROKER_MAX_RETRIES = 1
BROKER_OWNER_FALLBACK = 'act-now'

# Broker start refusals that prove no action ran in this batch, so the
# direct Pointer fallback is safe (same rule as the deleted spawn's
# is_session_start_failure, council 1 B2). `cancelled` and
# `recovery_required` are deliberately ABSENT: a cancelled task must
# not act against the user's cancel, and a recovery-required broker
# may still hold a live driver from a previous task, so the batch
# reports instead of falling back.
BROKER_START_FAILURE_ERRORS = frozenset({
    'busy', 'broker_unavailable', 'broker_changed', 'broker_stopping',
    'nested_session', 'native_unavailable', 'driver_start_failed',
    'broker_command_failed',
})


def _broker_owner(agent):
    """Broker owner string for an act-now agent name."""
    if isinstance(agent, str) and re.fullmatch(r'[A-Za-z0-9_.:@+-]{1,80}', agent):
        return agent
    return BROKER_OWNER_FALLBACK


def _broker_cli(remote_py, args, timeout_s):
    """Run one session_remote.py CLI call.

    Returns (returncode, parsed_stdout, stderr). returncode is None
    when the CLI itself timed out; parsed_stdout is None when stdout
    is not one JSON object.
    """
    try:
        proc = subprocess.run(
            [sys.executable, str(remote_py), *args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return None, None, 'broker CLI timed out after %.1fs' % timeout_s
    parsed = None
    try:
        parsed = json.loads(proc.stdout)
    except ValueError:
        pass
    return proc.returncode, parsed, proc.stderr


def _wait_for_task_running(remote_py, generation, timeout_s=30.0):
    """Poll broker status until the started task is running.

    The relay answers start with status `starting` before the driver
    prints its ready line (about 0.5 s of Python startup). A request
    sent in that window is refused with task_stopped, and an
    immediate finish poisons _await_ready into driver_not_ready, so
    the task must be running (driver ready) before the first
    request. Returns (True, None) when running, (False, error) when
    the task failed before any request, (False, None) on timeout.
    """
    deadline = time.monotonic() + timeout_s
    while True:
        _rc, parsed, _err = _broker_cli(remote_py, ['status'], 30.0)
        if isinstance(parsed, dict) and parsed.get('generation') == generation:
            state = parsed.get('state')
            if state == 'running' and parsed.get('driver') == 'ready':
                return True, None
            if state in ('failed', 'finished'):
                return False, (parsed.get('error')
                               or parsed.get('last_start_error') or state)
        if time.monotonic() >= deadline:
            return False, None
        time.sleep(0.5)


def stamp_actions(actions, meta):
    """Stamp CB-2 scope/observation_id onto a JSON batch (step 9).

    The agent loop stamps every action with the scope and id of the
    observation the batch is written against, so desktop_act's
    binding check can verify the batch against the observation it
    was grounded on instead of running it on the legacy pixel path.
    Returns a NEW list; the input is not mutated. A meta without id
    or scope refuses (fail closed: an unbound batch must not run).
    An action that already carries scope/observation_id is kept when
    it matches the meta and refuses when it does not: a stale
    binding is never silently re-stamped onto this observation.
    Raises ValueError on any refusal.
    """
    if not isinstance(meta, dict) or not meta.get('id'):
        raise ValueError(
            'CB-2 stamping refused: observation meta has no id; '
            'actions cannot be bound to a snapshot')
    if not meta.get('scope'):
        raise ValueError(
            'CB-2 stamping refused: observation meta has no scope; '
            'actions cannot be bound to a scope')
    stamped = []
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError(
                'CB-2 stamping refused: action is not an object: %r'
                % (action,))
        scope = action.get('scope')
        observation_id = action.get('observation_id')
        if scope is not None and scope != meta['scope']:
            raise ValueError(
                'CB-2 stamping refused: action is bound to scope %r, '
                'not this observation scope %r'
                % (scope, meta['scope']))
        if observation_id is not None and observation_id != meta['id']:
            raise ValueError(
                'CB-2 stamping refused: action is bound to observation '
                '%r, not this observation %r'
                % (observation_id, meta['id']))
        stamped.append(dict(action, scope=meta['scope'],
                            observation_id=meta['id']))
    return stamped


def _write_stamped_actions(actions_path, meta, state_dir, token, label):
    """Read the actions file, stamp it with the meta, and write the
    stamped copy into the state dir (never in place: the caller's
    file is untouched). Returns the stamped path as a string. Raises
    ValueError from stamp_actions or on an unreadable actions file
    or an unwritable stamped file."""
    try:
        with open(actions_path, 'r', encoding='utf-8') as handle:
            actions = json.load(handle)
    except (OSError, ValueError) as exc:
        raise ValueError(
            'CB-2 stamping refused: actions file unreadable: %s' % exc)
    if not isinstance(actions, list) or not actions:
        raise ValueError(
            'CB-2 stamping refused: actions must be a non-empty JSON '
            'list')
    stamped = stamp_actions(actions, meta)
    path = Path(state_dir) / ('act-now-stamped-%s-%s.json'
                              % (token, label))
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT
                     | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        try:
            raw = (json.dumps(stamped, ensure_ascii=False)
                   + '\n').encode('utf-8')
            if os.write(fd, raw) != len(raw):
                raise RuntimeError('stamped actions write was incomplete')
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
    except OSError as exc:
        raise ValueError(
            'CB-2 stamping refused: stamped actions file unavailable: '
            '%s' % exc)
    return str(path)


def _regions_equal(first, second):
    """True when two observation metas cover the same screen region.

    The R1/W1 retry guard: the retry act reuses the batch's pixel
    coordinates, which are bound to the original frame, so the retry
    is safe only when the fresh observation covers the same region.
    A moved window reports for the model to re-ground instead of
    clicking the wrong target.
    """
    if not isinstance(first, dict) or not isinstance(second, dict):
        return False
    for key in ('region', 'monitor_box', 'window_bounds'):
        if first.get(key) != second.get(key):
            return False
    return True


def _observe_args(meta, screen):
    """Broker observe args that re-capture an observation's scope."""
    args = ['observe']
    if meta.get('scope') == 'window' and meta.get('window'):
        args += ['--window', str(meta['window'])]
    else:
        args += ['--screen', screen]
    if isinstance(meta.get('max_width'), int):
        args += ['--max-width', str(meta['max_width'])]
    crop = meta.get('crop')
    if (isinstance(crop, list) and len(crop) == 4
            and all(isinstance(v, int) for v in crop)):
        args += ['--crop'] + [str(v) for v in crop]
    return args


def broker_attempt(observation_path, actions_path, deadline_s,
                   state_dir, meta, screen, owner):
    """Run one act batch through the broker-held session driver.

    Returns (returncode, stdout, stderr, timed_out, elapsed_s, detail).
    stdout carries exactly one JSON object (the driver act result, or
    a start-failure error), so the caller parses it exactly as it
    parsed the deleted spawn's stdout. detail carries the broker
    evidence (owner, sequences, retries, finish outcome) for the
    envelope; it is never part of stdout.

    Flow: stamp (CB-2: scope/observation_id from the observation
    meta into a stamped copy of the actions file, never in place;
    a meta without id or scope refuses before any broker start)
    -> start (with the 300 s queue wait) -> request act (sequence
    1) -> result (bounded by deadline_s) -> finish. On a typed
    transient failure (returncode 1 with session_continues true) the
    batch retries ONCE (R1/W1): a broker observe re-captures the same
    scope INSIDE the session, so the session marker updates to the
    fresh observation path, then the act is re-sent with a fresh
    sequence and the fresh observation, re-stamped with the fresh
    meta, but only when the fresh region equals the original region
    (see _regions_equal). A timeout never falls back and never
    replays: the outcome is unknown, finish is still attempted so
    the session is released, and the caller reports the unconfirmed
    actions. finish is attempted on every path where a start
    succeeded, best-effort, so the broker never keeps a task owned
    by a dead caller.
    """
    start = time.monotonic()
    remote_py = Path(__file__).resolve().parent / 'session_remote.py'
    owner = _broker_owner(owner)
    detail = {'broker_owner': owner, 'broker_sequences': [],
              'broker_retries': 0, 'broker_start': None,
              'broker_finish': None, 'broker_lease': None}
    try:
        state_dir = Path(state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        out = json.dumps({'ok': False,
                          'error': ('session guardian startup failed: '
                                    'broker state dir unavailable: %s' % exc)})
        return 1, out, '', False, time.monotonic() - start, detail
    token = secrets.token_hex(8)
    lease_path = state_dir / ('act-now-%d-%s.lease' % (os.getpid(), token))
    request_path = state_dir / ('act-now-%d-%s.json' % (os.getpid(), token))
    detail['broker_lease'] = str(lease_path)
    started = False
    stamped_paths = []
    try:
        # CB-2 (step 9): stamp the batch before any broker start,
        # so an unstampable meta refuses fast and no session is
        # started for a batch that cannot run.
        try:
            current_actions = _write_stamped_actions(
                actions_path, meta, state_dir, token, 'initial')
        except ValueError as exc:
            out = json.dumps({'ok': False, 'error': str(exc)})
            return 1, out, '', False, time.monotonic() - start, detail
        stamped_paths.append(current_actions)
        rc, parsed, err = _broker_cli(
            remote_py, ['start', '--owner', owner, '--lease-file',
                        str(lease_path), '--wait', str(BROKER_WAIT_S)],
            BROKER_WAIT_S + 60.0)
        if rc is None:
            # The start CLI itself timed out: the start outcome is
            # unknown, so no fallback is safe. Report timed out.
            out = json.dumps({'ok': False,
                              'error': 'broker start timed out; outcome '
                                       'unknown, not replayed'})
            return 1, out, err, True, time.monotonic() - start, detail
        detail['broker_start'] = parsed if isinstance(parsed, dict) else {'rc': rc, 'stderr': (err or '')[:200]}
        if not isinstance(parsed, dict) or parsed.get('ok') is not True:
            error = (parsed or {}).get('error') if isinstance(parsed, dict) else None
            if error is None:
                error = 'broker_command_failed'
                if err.strip():
                    error = 'broker_command_failed: ' + err.strip().splitlines()[-1][:200]
            if error in BROKER_START_FAILURE_ERRORS:
                out = json.dumps({'ok': False,
                                  'error': ('session guardian startup '
                                            'failed: broker ' + error)})
            else:
                out = json.dumps({'ok': False,
                                  'error': ('broker start refused: ' + error)})
            return 1, out, err, False, time.monotonic() - start, detail
        if parsed.get('status') != 'starting':
            # The broker accepted the start but the driver never came
            # up (launcher exception): no act ran, fallback is safe.
            out = json.dumps({'ok': False,
                              'error': ('session guardian startup failed: '
                                        'driver start failed: '
                                        + str(parsed.get('error') or ''))})
            return 1, out, err, False, time.monotonic() - start, detail
        started = True
        running, ready_error = _wait_for_task_running(
            remote_py, parsed.get('generation'))
        if not running:
            if ready_error is None:
                out = json.dumps({'ok': False,
                                  'error': 'broker start timed out; outcome '
                                           'unknown, not replayed'})
                return 1, out, '', True, time.monotonic() - start, detail
            out = json.dumps({'ok': False,
                              'error': ('session guardian startup failed: '
                                        'driver start failed: '
                                        + str(ready_error))})
            return 1, out, '', False, time.monotonic() - start, detail
        sequence = 1
        current_obs = str(observation_path)
        current_meta = meta
        result_out = None
        result_err = ''
        result_rc = 1
        result_timed_out = False
        for attempt in range(BROKER_MAX_RETRIES + 1):
            envelope = {'args': ['act', '--observation', current_obs,
                                 '--actions', current_actions],
                        'stdin': '', 'image_policy': 'always'}
            try:
                fd = os.open(str(request_path), os.O_WRONLY | os.O_CREAT
                             | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
                try:
                    raw = (json.dumps(envelope, ensure_ascii=False) + '\n').encode('utf-8')
                    if os.write(fd, raw) != len(raw):
                        raise RuntimeError('broker request write was incomplete')
                    os.fchmod(fd, 0o600)
                finally:
                    os.close(fd)
            except OSError as exc:
                out = json.dumps({'ok': False,
                                  'error': ('session guardian startup failed: '
                                            'broker request file unavailable: %s' % exc)})
                return 1, out, '', False, time.monotonic() - start, detail
            rc, parsed, err = _broker_cli(
                remote_py, ['request', '--lease-file', str(lease_path),
                            '--sequence', str(sequence),
                            '--request', str(request_path)],
                60.0)
            detail['broker_sequences'].append(sequence)
            if (not isinstance(parsed, dict)
                    or parsed.get('ok') is not True
                    or parsed.get('status') != 'accepted'):
                # The request was never accepted, so the driver never
                # saw the act: no action ran, fallback is safe.
                error = (parsed or {}).get('error') if isinstance(parsed, dict) else 'broker_command_failed'
                out = json.dumps({'ok': False,
                                  'error': ('session guardian startup '
                                            'failed: broker request not '
                                            'accepted: ' + str(error))})
                return 1, out, err or '', False, time.monotonic() - start, detail
            sequence += 1
            rc, parsed, err = _broker_cli(
                remote_py, ['result', '--lease-file', str(lease_path),
                            '--sequence', str(sequence - 1)],
                deadline_s)
            if rc is None:
                result_timed_out = True
                result_rc = 1
                result_out = json.dumps({'ok': False,
                                         'error': ('broker result timed out '
                                                   'after %.1fs; outcome '
                                                   'unknown, not replayed'
                                                   % deadline_s)})
                result_err = err or ''
                break
            if (not isinstance(parsed, dict)
                    or parsed.get('ok') is not True):
                error = (parsed or {}).get('error') if isinstance(parsed, dict) else 'broker_command_failed'
                result_rc = 1
                result_out = json.dumps({'ok': False, 'error': str(error)})
                result_err = err or ''
                break
            response = parsed.get('response')
            if not isinstance(response, dict):
                result_rc = 1
                result_out = json.dumps({'ok': False,
                                         'error': ('broker result has no '
                                                   'driver response')})
                result_err = err or ''
                break
            result_rc = response.get('returncode', 1)
            body = response.get('result')
            if isinstance(body, dict):
                result_out = json.dumps(body, ensure_ascii=False)
            elif isinstance(response.get('stdout'), str):
                result_out = response['stdout']
            else:
                result_out = json.dumps({'ok': False,
                                         'error': ('driver response has no '
                                                   'result')})
            result_err = response.get('stderr', '') or err or ''
            continues = response.get('session_continues') is True
            if result_rc == 1 and continues and attempt < BROKER_MAX_RETRIES:
                # R1/W1: typed transient, nothing was sent. Re-observe
                # INSIDE the session (the marker updates to the fresh
                # path), then re-send once with a fresh sequence and
                # the fresh observation, but only on the same region.
                obs_envelope = {'args': _observe_args(current_meta, screen),
                                'stdin': '', 'image_policy': 'always'}
                try:
                    fd = os.open(str(request_path), os.O_WRONLY | os.O_CREAT
                                 | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
                    try:
                        raw = (json.dumps(obs_envelope, ensure_ascii=False) + '\n').encode('utf-8')
                        if os.write(fd, raw) != len(raw):
                            raise RuntimeError('broker request write was incomplete')
                        os.fchmod(fd, 0o600)
                    finally:
                        os.close(fd)
                except OSError:
                    break
                obs_rc, obs_parsed, obs_err = _broker_cli(
                    remote_py, ['request', '--lease-file', str(lease_path),
                                '--sequence', str(sequence),
                                '--request', str(request_path)],
                    60.0)
                detail['broker_sequences'].append(sequence)
                sequence += 1
                if (not isinstance(obs_parsed, dict)
                        or obs_parsed.get('ok') is not True
                        or obs_parsed.get('status') != 'accepted'):
                    break
                obs_rc, obs_parsed, obs_err = _broker_cli(
                    remote_py, ['result', '--lease-file', str(lease_path),
                                '--sequence', str(sequence - 1)],
                    deadline_s)
                if (not isinstance(obs_parsed, dict)
                        or obs_parsed.get('ok') is not True
                        or not isinstance((obs_parsed.get('response') or {}).get('result'), dict)):
                    break
                fresh_meta = obs_parsed['response']['result']
                fresh_obs = fresh_meta.get('observation')
                if (not isinstance(fresh_obs, str) or not fresh_obs
                        or not _regions_equal(current_meta, fresh_meta)):
                    break
                # CB-2: re-stamp the batch with the FRESH meta
                # before the retry; the original stamps are bound
                # to the old observation and the binding check
                # refuses them as stale. A re-stamp failure
                # abandons the retry and keeps the transient
                # result.
                try:
                    current_actions = _write_stamped_actions(
                        actions_path, fresh_meta, state_dir, token,
                        'retry-%d' % attempt)
                except ValueError:
                    break
                stamped_paths.append(current_actions)
                current_obs = fresh_obs
                current_meta = fresh_meta
                detail['broker_retries'] += 1
                continue
            break
        return result_rc, result_out, result_err, result_timed_out, time.monotonic() - start, detail
    finally:
        if started:
            try:
                rc, parsed, err = _broker_cli(
                    remote_py, ['finish', '--lease-file', str(lease_path)],
                    130.0)
                detail['broker_finish'] = parsed if isinstance(parsed, dict) else {'rc': rc, 'stderr': (err or '')[:200]}
            except Exception:
                pass
        for path in (lease_path, request_path):
            try:
                path.unlink()
            except OSError:
                pass
        for path in stamped_paths:
            try:
                Path(path).unlink()
            except OSError:
                pass


def _parse_stdout_envelope(stdout):
    """The last JSON object printed on the session stdout, or None.

    The session command prints exactly one JSON object on success (the
    act result) or on a supervise raise (the error envelope), but the
    scan is line-by-line from the end so extra lines cannot break it.
    """
    if not stdout:
        return None
    for line in reversed((stdout or '').splitlines()):
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def _stdout_session_error(stdout):
    """The session command's JSON error, if it printed one."""
    data = _parse_stdout_envelope(stdout)
    if isinstance(data, dict) and isinstance(data.get('error'), str):
        return data['error']
    return None


def _is_completed_capture(result, action_count):
    """The completed-capture-error shape (cu.py:1341): the full batch
    ran, only the after-capture failed. Counts as a session success."""
    return (isinstance(result, dict) and result.get('ok') is False and
            isinstance(result.get('capture_error'), str) and
            type(result.get('completed')) is int and action_count > 0 and
            result['completed'] == action_count)


def is_session_start_failure(stdout, timed_out):
    """True only when the session command PROVES no action ran, so a
    fallback is safe.

    A timeout never falls back (council 1, B1): the driver may have
    acted and been torn down, and no post-kill probe can tell "never
    started" from "started, acted, and was just torn down". A start
    failure is proven only by the parsed stdout JSON error starting
    with one of START_FAILURE_PREFIXES (council 1, B2): both are
    emitted by supervise before the driver can act. Bare substrings
    ('Expecting value', 'cursor guard') are NOT accepted: a mid-session
    guard loss ('session cursor guard lost', cursor_session.py:178)
    and a late hyprctl JSON failure (cu.py:519, :213) carry the same
    strings after actions already ran. No liveness probe is consulted:
    session_live() after the kill measures "is a session live after we
    killed it", which is the normal outcome of a teardown, not proof
    (council 1, B1/B3).
    """
    if timed_out:
        return False
    err = _stdout_session_error(stdout)
    if isinstance(err, str) and err.startswith(START_FAILURE_PREFIXES):
        return True
    return False


def append_log(path, record):
    """Append one JSON timing record (0600, trailing newline)."""
    line = (json.dumps(record, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + '\n').encode('utf-8')
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT
                 | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
        if os.write(fd, line) != len(line):
            raise RuntimeError('first-action log write was incomplete')
    finally:
        os.close(fd)


def _read_given_observation(cu, observation_path, deadline_s):
    """Read and validate a given observation file.

    Returns (meta, None) when the file parses, has id, image,
    monitor_box and created, and is still within the freshness window
    when the session attempt ends (age + deadline < 120 s). Otherwise
    returns (None, rejection) with the given id when known, the age in
    seconds when known, and the reason: 'unreadable', 'incomplete', or
    'stale'. A None observation_path returns (None, None): nothing was
    given, nothing is rejected.
    """
    if not observation_path:
        return None, None
    try:
        meta = cu.read_json_file(observation_path)
    except (OSError, ValueError, KeyError) as exc:
        return None, {'given_id': None, 'age_s': None,
                      'reason': 'unreadable: ' + str(exc)[:200]}
    given_id = meta.get('id') if isinstance(meta, dict) else None
    created = meta.get('created') if isinstance(meta, dict) else None
    if (not isinstance(meta, dict) or not meta.get('id')
            or not meta.get('image') or not meta.get('monitor_box')
            or not isinstance(created, (int, float))):
        return None, {'given_id': given_id, 'age_s': None,
                      'reason': ('incomplete: missing id, image, '
                                 'monitor_box, or created')}
    age_s = time.time() - created
    if age_s + deadline_s >= OBSERVATION_MAX_AGE_S:
        return None, {'given_id': given_id, 'age_s': round(age_s, 1),
                      'reason': ('stale: age %.1fs + %.1fs deadline '
                                 'reaches the %ds freshness window'
                                 % (age_s, deadline_s,
                                    OBSERVATION_MAX_AGE_S))}
    return meta, None


def _scope_after(cu, env, meta, result_after, screen_meta):
    """The scope-matching after-capture for the envelope.

    AMEND4 item 12 (CL1-SWEEP): act-now used to capture its envelope
    after-image with observe_screen regardless of the input scope,
    overwriting desktop_act's scope-matching after-capture, so EVERY
    act-now after-image was screen-scoped by construction and reusing
    one for a key/type step always failed. This helper returns the
    scope-matching capture: the action result's after when it is a
    dict whose scope matches the input observation's scope
    (desktop_act already captures in the input scope, so this costs
    no extra capture); otherwise a fresh capture in the input scope
    (a window observation re-observes its window). A screen-scope
    input reuses the screen capture, which IS its scope-matching
    after. A scope-less meta WITH a window is treated as window
    scope (TESTREPAIR item 12 residual): a window-scope
    result_after is accepted, else a fresh window capture is taken.
    A scope-less meta with no window reuses the screen capture.
    Returns a meta dict, or None when no scope-matching capture is
    available.
    """
    input_scope = meta.get('scope')
    is_window = (input_scope == 'window'
                 or (input_scope is None and meta.get('window')))
    if (isinstance(result_after, dict)
            and result_after.get('scope') is not None
            and (result_after.get('scope') == input_scope
                 or (is_window
                     and result_after.get('scope') == 'window'))):
        return result_after
    if is_window and meta.get('window'):
        return cu.observe(env, meta['window'], crop=meta.get('crop'),
                          max_width=meta.get('max_width') or cu.CAPTURE_MAX_WIDTH,
                          activate=False)
    return screen_meta


def _dispatch_ms(order_wall_iso, laptop_wall_iso):
    """VM-to-laptop dispatch in ms (CB-7): wall time from the user
    order on the VM to this process starting on the laptop. That span
    is VM send plus SSH connect plus shell startup; it is measured
    ONLY when the caller passes the order wall time (--order-wall or
    CU_ORDER_WALL). Returns None when the order time was not given,
    does not parse, or is after the laptop start (clock skew): a
    dispatch number invented from a missing input would be worse
    than none. Pure function, unit tested."""
    if not order_wall_iso or not laptop_wall_iso:
        return None
    try:
        order = datetime.fromisoformat(str(order_wall_iso))
        laptop = datetime.fromisoformat(str(laptop_wall_iso))
    except ValueError:
        return None
    if order.tzinfo is None or laptop.tzinfo is None:
        return None
    delta_ms = (laptop - order).total_seconds() * 1000.0
    if delta_ms < 0 or delta_ms > 3600000:
        return None
    return round(delta_ms, 3)


POINTER_ACTION_TYPES = ('move', 'hover', 'click', 'double_click',
                        'scroll', 'drag')


def _first_pointer_action_ms(result):
    """First completed pointer action in a desktop_act result, in ms
    from that batch's execution start (its action_ms list), or None
    when the result carries no action_ms (older build) or no pointer
    action completed. Pure function, unit tested."""
    if not isinstance(result, dict):
        return None
    entries = result.get('action_ms')
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get('type') in POINTER_ACTION_TYPES:
            ms = entry.get('ms')
            if isinstance(ms, (int, float)):
                return ms
    return None


def _capture_params(meta):
    """Pinned capture params (P6c) for an observation meta dict."""
    if not isinstance(meta, dict):
        return None
    return {'max_width': meta.get('max_width'),
            'jpeg_quality': meta.get('jpeg_quality'),
            'jpeg_subsampling': meta.get('jpeg_subsampling')}


def _fresh_observation(cu, env, screen, observation_path,
                       deadline_s=DEFAULT_SESSION_DEADLINE_S):
    """Load a given observation when fresh, else capture a new one.

    Returns (meta, observation_path, source, rejected). A fresh given
    observation returns source 'given' and rejected None. When no
    observation was given, a fresh screen capture is taken and
    rejected is None: that is the documented default, not a
    substitution. When a given observation was REJECTED (stale,
    missing fields, or unreadable), a fresh screen capture is still
    taken so the envelope can name what was substituted, but rejected
    carries the given id, age, and reason, and the caller (run) must
    refuse loudly on it instead of acting on the substitute (G28).
    Acting on the substitute would run window-image coordinates
    against a screen region, off by the window offset inside the
    monitor, or refuse typing with a misleading scope error.
    Fresh means the observation is still within the 120 s window when
    the session attempt ends: age plus the session deadline must stay
    under OBSERVATION_MAX_AGE_S (redteam A6), or the act would be
    refused for a stale observation after a wasted session attempt.
    """
    meta, rejected = _read_given_observation(cu, observation_path,
                                             deadline_s)
    if meta is not None:
        return meta, str(observation_path), 'given', None
    meta = cu.observe_screen(env, screen, max_width=cu.CAPTURE_MAX_WIDTH, persist=True)
    return meta, str(meta['observation']), 'captured', rejected


def loud_substitution_refusal(rejected, has_keyboard=True):
    """The G28 loud-refusal message for a rejected given observation.

    Names the given observation id when known, its age, and why it was
    rejected, states that a screen capture was substituted and will
    NOT be acted on, and says what to pass instead: a fresh window
    observation captured in the same call as act-now. On the key/type
    path only that remedy is offered: a screen-scope observation
    carries no window to type into, and a screen batch types into
    the focused window, which is not the named target, so the
    screen-coordinates remedy would act on the wrong target (the
    binding check in desktop_act refuses an action bound to a
    different observation). On a pointer-only batch the screen
    remedy is valid and is offered too.
    """
    given = rejected.get('given_id') or 'unknown id'
    reason = rejected.get('reason', 'unknown reason')
    age = rejected.get('age_s')
    age_txt = ''
    if isinstance(age, (int, float)) and 'age' not in reason:
        age_txt = '; age %.1fs' % age
    remedy = ('re-observe the target window in the same call as act-now '
              'and pass the fresh window observation')
    if not has_keyboard:
        remedy += (', or omit --observation and write coordinates for '
                   'the screen')
    return ('given observation %s rejected (%s%s); act-now captured a '
            'fresh screen observation instead and refuses rather than '
            'acting on it: %s'
            % (given, reason, age_txt, remedy))


def captured_source_refusal(actions, meta):
    """R7 fail-loud guard for the captured-source path.

    When no observation was given, act-now captures a fresh SCREEN
    observation (source 'captured'). A batch whose actions are bound
    to a different scope or observation (typically window-space
    points grounded on a window image) must NOT run on that screen
    capture: the points would execute in screen space, off by the
    window origin offset, and the envelope would still read success
    (tracker J35/J40, the largest click-miss class). Returns the
    refusal message naming the first mismatched action, or None
    when every bound action matches the captured meta (unbound
    actions are the documented screen-coordinates default and pass;
    CB-2 stamping in broker_attempt still refuses a mismatch as a
    second line, but this guard fires first, before any session
    attempt, and names the captured source). Pure function, unit
    tested.
    """
    if not isinstance(meta, dict):
        return ('observation source is captured but the captured '
                'meta is unreadable; refusing rather than acting')
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            continue
        scope = action.get('scope')
        if scope is not None and scope != meta.get('scope'):
            return ('observation source is captured (screen scope, '
                    'id %s) but action %d is bound to scope %r; '
                    'refusing rather than running window-space '
                    'points in screen space: re-observe the target '
                    'window and pass the fresh window observation '
                    'with --observation'
                    % (meta.get('id'), index, scope))
        observation_id = action.get('observation_id')
        if (observation_id is not None
                and observation_id != meta.get('id')):
            return ('observation source is captured (screen scope, '
                    'id %s) but action %d is bound to observation '
                    '%r; refusing rather than running points '
                    'grounded on another observation against this '
                    'screen capture: re-observe and pass the fresh '
                    'observation with --observation'
                    % (meta.get('id'), index, observation_id))
    return None


def _load_cu():
    """The cu module: when cu.py is the main script its module is
    __main__, not 'cu'; importing cu again would load a second copy.
    Prefer __main__ when it already carries desktop_act."""
    main_mod = sys.modules.get('__main__')
    if main_mod is not None and hasattr(main_mod, 'desktop_act'):
        return main_mod
    import cu
    return cu


def run(args):
    """Run one act-now batch. args is the argparse namespace. Returns an
    exit code: 0 action ok, 1 action failed, 2 refused (no overlay).

    run() never lets an exception escape (council 1, A2): every path
    fills the envelope and returns a code, so stdout carries exactly
    one JSON object (the envelope) and the JSONL carries exactly one
    record, including refusals and bad input.
    """
    cu = _load_cu()
    import overlay as overlay_mod
    t0 = time.monotonic()
    wall0 = _now_iso()
    agent = args.agent
    method = args.method
    envelope = {
        'ok': False,
        # CB-1 (step 5): the three-part contract rides the envelope
        # beside ok. ok stays the end-state statement; input_sent
        # says the input went out, verified says a postcondition
        # passed. A result from an older build has no contract
        # fields; the migration below names that instead of
        # inventing a postcondition.
        'input_sent': None,
        'verified': None,
        'verified_basis': None,
        'path': 'refused',
        'agent': agent,
        'method': method,
        'wall_time': wall0,
        'order_to_overlay_ms': None,
        'order_to_session_attempt_ms': None,
        'total_ms': None,
        'session_error': None,
        'session_timed_out': False,
        # Step 8: the broker route (owner, sequences attempted,
        # transient retries, finish outcome). None when the run
        # refuses before the broker attempt.
        'broker_owner': None,
        'broker_sequences': None,
        'broker_retries': None,
        'broker_finish': None,
        'fallback_reason': None,
        'ime_state_trace': None,
        'type_verified': None,
        'error_code': None,
        'dom_hooks': None,
        'dom_hooks_error': None,
        'completed': 0,
        'observation': None,
        'after': None,
        'after_screen': None,
        'after_error': None,
        'error': None,
        'release_error': None,
        'log_error': None,
        'target_breached': None,
        # CB-7: dispatch is VM send + SSH connect + shell startup,
        # measured from the order wall time the VM passes in
        # (--order-wall / CU_ORDER_WALL). None when not provided.
        'dispatch_ms': None,
        'dispatch_basis': None,
        # CB-7: first completed pointer action from t0, ms. None
        # when no pointer action completed or the result carries no
        # action_ms (older build). target_breached compares THIS
        # against the 30 s target, not whole-batch time.
        'first_pointer_ms': None,
        'target_breached_basis': None,
        # CB-10: per-phase split, overlay flicker vs think time
        # measured separately. Think time lives in the agent loop
        # (P6 harness, vision_measure.py), never inside act-now.
        # Overlay flicker is UNPROBED until the LIQUID flicker probe
        # runs (A4 worker precondition): no flicker number is claimed
        # here, only the phase split to measure it.
        'phase_ms': None,
        'think_ms': None,
        'think_basis': ('not_in_act_now: think time is measured by '
                        'the P6 harness in the agent loop, not inside '
                        'act-now'),
        'overlay_flicker': ('unprobed: LIQUID flicker probe not run '
                            '(A4 worker precondition)'),
    }
    overlay_acquired = False
    result_after = None
    first_pointer_ms = None
    first_pointer_basis = None
    phase_ms = {}
    order_wall = getattr(args, 'order_wall', None) or os.environ.get('CU_ORDER_WALL')
    envelope['dispatch_ms'] = _dispatch_ms(order_wall, wall0)
    envelope['dispatch_basis'] = (
        'order_wall' if envelope['dispatch_ms'] is not None
        else ('not_provided' if not order_wall
              else 'unparsable_or_skewed'))
    try:
        try:
            actions = cu.read_json_file(args.actions)
        except (OSError, ValueError) as exc:
            envelope['error'] = 'bad actions file: ' + str(exc)
            envelope['path'] = 'bad_actions'
            return 1
        if not isinstance(actions, list) or not actions:
            envelope['error'] = ('actions must be a non-empty JSON list')
            envelope['path'] = 'bad_actions'
            return 1
        deadline = float(args.session_deadline_s)
        if (not math.isfinite(deadline) or deadline <= 0
                or deadline > OBSERVATION_MAX_AGE_S):
            envelope['error'] = ('invalid session deadline: %r (must be '
                                 'positive, finite, and at most %d s, the '
                                 'observation freshness window)'
                                 % (args.session_deadline_s,
                                    OBSERVATION_MAX_AGE_S))
            envelope['path'] = 'refused'
            return 1
        # Protocol section 8 (final direction 2(f)): the pre-overlay
        # screen-scope key/type refusal is DELETED. The check changed
        # form into snapshot binding, which desktop_act enforces:
        # actions bound to the given observation proceed to the
        # session attempt, and a mismatched binding refuses there
        # with a stale-ref code. A screen-scope observation with
        # bound actions is no longer refused for its scope alone;
        # the scope check that used to live here is the binding
        # check now.
        env = cu.environment()
        try:
            reply = acquire_overlay(agent, method, label=args.label,
                                    overlay_mod=overlay_mod)
        except RuntimeError as exc:
            envelope['error'] = str(exc)
            return 2
        overlay_acquired = True
        envelope['order_to_overlay_ms'] = _ms(t0)
        phase_ms['overlay_acquire_ms'] = envelope['order_to_overlay_ms']
        envelope['overlay_owner'] = reply.get('owner')
        _obs_t0 = time.monotonic()
        meta, obs_path, obs_source, rejected = _fresh_observation(
            cu, env, args.screen, args.observation, deadline)
        phase_ms['observation_ms'] = round(
            (time.monotonic() - _obs_t0) * 1000, 3)
        envelope['observation'] = {'id': meta.get('id'),
                                   'source': obs_source,
                                   'capture_params': _capture_params(meta)}
        if rejected is not None:
            # G28: a given observation was rejected and a screen
            # capture was substituted. The substitution is recorded
            # explicitly in the envelope, never silent, and the run
            # refuses LOUDLY before any session attempt and before any
            # action runs, naming the given observation, its age, and
            # why it was rejected. The refusal covers EVERY batch,
            # not only key/type batches: a pointer-only batch on the
            # substitute would run window-image coordinates against a
            # screen region, off by the window offset inside the
            # monitor, and cursorpos verification cannot catch it
            # (it verifies the pointer reached the computed point,
            # which is the wrong point). The no-observation default
            # is unaffected (rejected is None there); blanket refusal
            # costs one re-observe. fallback_reason is set on this
            # path, as specified.
            envelope['observation']['given_observation_rejected'] = rejected
            has_keyboard = any(
                isinstance(a, dict) and a.get('type') in ('key', 'type')
                for a in actions)
            message = loud_substitution_refusal(rejected, has_keyboard)
            envelope['fallback_reason'] = message
            envelope['error'] = message
            envelope['path'] = 'refused'
            return 1
        if obs_source == 'captured':
            # R7: no observation was given, so act-now captured a
            # screen observation. A batch bound to a window scope or
            # to another observation carries window-space points;
            # running them on the screen capture misses by the
            # window origin offset with a success envelope (J35/J40).
            # Refuse loudly before any session attempt. Unbound
            # actions are screen coordinates by definition and pass.
            message = captured_source_refusal(actions, meta)
            if message is not None:
                envelope['fallback_reason'] = message
                envelope['error'] = message
                envelope['path'] = 'refused'
                return 1
        envelope['order_to_session_attempt_ms'] = _ms(t0)
        (rc, out, err, timed_out, _elapsed,
         broker_detail) = broker_attempt(
            obs_path, args.actions, deadline, cu.STATE, meta,
            args.screen, agent)
        envelope['broker_owner'] = broker_detail['broker_owner']
        envelope['broker_sequences'] = broker_detail['broker_sequences']
        envelope['broker_retries'] = broker_detail['broker_retries']
        envelope['broker_finish'] = broker_detail['broker_finish']
        phase_ms['session_attempt_ms'] = round(_elapsed * 1000, 3)
        envelope['session_timed_out'] = timed_out
        session_result = _parse_stdout_envelope(out)
        session_error = None
        if (isinstance(session_result, dict)
                and isinstance(session_result.get('error'), str)):
            session_error = session_result['error']
        elif err.strip():
            # Council 1, M1: the stderr tail is used only when it names
            # a failure; a trailing warning (for example the Escape
            # binding warning teed by the guardian drain) must not be
            # mislabelled as the session error.
            last = err.strip().splitlines()[-1]
            if any(w in last.lower()
                   for w in ('error', 'failed', 'traceback')):
                session_error = last[:400]
        envelope['session_error'] = session_error
        # CLICK-PROBE Stage A: ime_state_trace was ABSENT from act-now
        # envelopes, so a silent type failure left no IME evidence.
        # desktop_act already records the fcitx5 state trace in its
        # result (cu.py literal_keyboard, result.update(ime_result)),
        # and code-exec callers see it because they return that result
        # directly; act-now parsed only ok/error out of the session
        # stdout and discarded the rest. Surface the trace in this
        # envelope (and the JSONL log) whenever the session result
        # carries it, on success and on failure alike, so the next
        # type-failure diagnosis can read the before/after_switch/
        # after_restore phases without a separate probe.
        if (isinstance(session_result, dict)
                and isinstance(session_result.get('ime_state_trace'),
                               list)):
            envelope['ime_state_trace'] = session_result['ime_state_trace']
        # RT R3: the act-now envelope used to drop type_verified and
        # error_code on both paths, so a live agent could not read
        # them from the envelope. Copy both whenever the session
        # result carries them (None when absent, so the fields are
        # always present); the fallback path below overwrites them
        # with the direct desktop_act result.
        if isinstance(session_result, dict):
            envelope['type_verified'] = session_result.get('type_verified')
            envelope['error_code'] = session_result.get('error_code')
            # CB-1 migration (step 5): carry the contract, not just
            # ok. A session result from an older build carries no
            # contract fields; migrate_legacy_result maps its bare
            # ok to input_sent with verified None, never to a
            # claimed postcondition.
            if ('input_sent' in session_result
                    or 'verified' in session_result):
                envelope['input_sent'] = session_result.get('input_sent')
                envelope['verified'] = session_result.get('verified')
                envelope['verified_basis'] = session_result.get(
                    'verified_basis')
            else:
                migrated = action_result.migrate_legacy_result(
                    session_result)
                envelope['input_sent'] = migrated['input_sent']
                envelope['verified'] = migrated['verified']
                envelope['verified_basis'] = migrated['verified_basis']
            if isinstance(session_result.get('after'), dict):
                result_after = session_result['after']
        # CB-7: first-pointer time on the session path, from t0:
        # session-attempt start plus the batch preflight plus the
        # first pointer action inside the batch. The gap NOT in this
        # sum is the session child process startup between the
        # attempt start and desktop_act entry (about 60ms, F2b log
        # lines 34-35; not recorded per run). At a 30 s threshold
        # that gap cannot flip the verdict, and the basis names it.
        _fp_action = _first_pointer_action_ms(session_result)
        _preflight = (session_result.get('preflight_ms')
                      if isinstance(session_result, dict) else None)
        if (_fp_action is not None
                and isinstance(_preflight, (int, float))
                and envelope['order_to_session_attempt_ms'] is not None):
            first_pointer_ms = (envelope['order_to_session_attempt_ms']
                                + _preflight + _fp_action)
            first_pointer_basis = ('session_computed (child startup '
                                   'about 60ms unrecorded)')
        if rc == 0 and not timed_out:
            # Council 1, A3: the exit code alone never proves success.
            # Require the stdout envelope to say ok, or to be the
            # completed-capture-error shape (full batch ran). CB-1
            # (step 5): ok is read through the contract, so a
            # session ok that means only "input sent" without a
            # postcondition cannot pass here as a verified success.
            if (isinstance(session_result, dict)
                    and _is_completed_capture(session_result,
                                              len(actions))):
                envelope['path'] = 'session'
                envelope['ok'] = True
                envelope['completed'] = len(actions)
                # The full batch ran but the after-capture failed,
                # so no postcondition ran: the input went out,
                # nothing was verified. This branch comes first
                # because contract_ok would also pass this shape
                # (verified None, input sent) with a vaguer basis.
                envelope['input_sent'] = True
                envelope['verified'] = None
                envelope['verified_basis'] = (
                    'completed-capture: after-capture failed, no '
                    'postcondition ran')
            elif (isinstance(session_result, dict)
                    and action_result.contract_ok(session_result)):
                completed = session_result.get('completed')
                envelope['path'] = 'session'
                envelope['ok'] = True
                envelope['completed'] = (completed
                                         if type(completed) is int
                                         else len(actions))
            else:
                envelope['path'] = 'session'
                envelope['ok'] = False
                envelope['error'] = (session_error
                                     or 'session stdout is not a '
                                     'success envelope')
        else:
            if is_session_start_failure(out, timed_out):
                envelope['fallback_reason'] = (
                    session_error or 'session start failed')
                envelope['path'] = 'fallback'
                if not overlay_visible(agent, overlay_mod=overlay_mod):
                    envelope['ok'] = False
                    envelope['error'] = ('overlay lost before fallback; '
                                         'refused')
                else:
                    # Item A: --dom-selector wires the DOM value hooks
                    # into the fallback batch. The hooks are
                    # best-effort: when no DOM session can open, the
                    # batch still runs with the pixel band, and the
                    # reason is recorded in the envelope.
                    dom_session = None
                    dom_kwargs = {}
                    selector = getattr(args, 'dom_selector', None)
                    if selector:
                        try:
                            import dom_act
                            text = dom_act.typed_text_of(actions)
                            if text is None:
                                envelope['dom_hooks_error'] = (
                                    'no type action in the batch')
                            else:
                                dom_session, focus_check, type_check = \
                                    dom_act.open_dom_hooks(selector, text)
                                dom_kwargs = {'focus_check': focus_check,
                                              'type_check': type_check}
                                envelope['dom_hooks'] = 'dom-value'
                                try:
                                    ground = dom_act.ground_input(
                                        dom_session, meta, selector)
                                    x_range = dom_act.grounded_x_range(
                                        ground, meta)
                                    if x_range is not None:
                                        dom_kwargs['type_x_ranges'] = \
                                            [x_range]
                                    y_range = dom_act.grounded_y_range(
                                        ground, meta)
                                    if y_range is not None:
                                        dom_kwargs['type_y_ranges'] = \
                                            [y_range]
                                except Exception:
                                    # No grounded rect: the batch keeps
                                    # the full-width band, exactly as
                                    # before. Grounding never fails the
                                    # batch here.
                                    pass
                        except Exception as exc:
                            envelope['dom_hooks_error'] = (
                                'dom hooks unavailable: ' + str(exc)[:200])
                    # CB-7: fallback runs in-process, so the desktop_act
                    # entry time is measured exactly here (unlike the
                    # session path, where child startup is unrecorded).
                    fallback_start_ms = _ms(t0)
                    try:
                        with cu.locked():
                            result = cu.desktop_act(
                                env, meta, actions,
                                observation_path=obs_path, **dom_kwargs)
                    except (ValueError, RuntimeError) as exc:
                        # Redteam A5: a preflight refusal (screen obs
                        # with typing, stale observation, window moved)
                        # lands in the envelope, not as a traceback,
                        # and the after-capture below still runs.
                        # CB-1: refused before input, so nothing was
                        # sent and no postcondition ran.
                        envelope['ok'] = False
                        envelope['input_sent'] = False
                        envelope['verified'] = None
                        envelope['verified_basis'] = (
                            'refused before input')
                        envelope['error'] = str(exc)[:400]
                    else:
                        envelope['ok'] = result.get('ok') is True
                        # CB-1: the fallback result carries the
                        # contract (desktop_act stamps it), so the
                        # envelope reports sent vs verified, not
                        # just ok.
                        envelope['input_sent'] = result.get('input_sent')
                        envelope['verified'] = result.get('verified')
                        envelope['verified_basis'] = result.get(
                            'verified_basis')
                        envelope['completed'] = result.get('completed', 0)
                        _fp_action = _first_pointer_action_ms(result)
                        _preflight = result.get('preflight_ms')
                        if (_fp_action is not None
                                and isinstance(_preflight, (int, float))):
                            first_pointer_ms = (
                                fallback_start_ms + _preflight + _fp_action)
                            first_pointer_basis = 'fallback_measured'
                        if isinstance(result.get('ime_state_trace'), list):
                            envelope['ime_state_trace'] = result[
                                'ime_state_trace']
                        envelope['type_verified'] = result.get(
                            'type_verified')
                        envelope['error_code'] = result.get('error_code')
                        if isinstance(result.get('after'), dict):
                            result_after = result['after']
                        if not envelope['ok']:
                            envelope['error'] = str(result.get('error', ''))
                    finally:
                        if dom_session is not None:
                            try:
                                dom_session.__exit__()
                            except Exception:
                                pass
            else:
                envelope['path'] = 'session'
                envelope['ok'] = False
                envelope['error'] = (
                    session_error or ('session timed out; not replayed'
                                      if timed_out else
                                      'session act failed; not replayed'))
        # AMEND4 item 12: the envelope carries BOTH after captures.
        # 'after' is the scope-matching capture (chainable: the next
        # act-now may reuse it as its observation). It prefers the
        # action result's after (desktop_act already captures in the
        # input scope); when that is absent, a non-dict, or scoped
        # differently, a fresh capture is taken in the input
        # observation's scope. A screen-scope input needs no extra
        # capture: the screen capture IS its scope-matching after.
        # 'after_screen' is the full-monitor capture, for verification
        # only, documented non-chainable: reusing a screen-scope
        # after-image for a key/type step always fails (CL1-SWEEP).
        screen_meta = None
        _after_t0 = time.monotonic()
        try:
            screen_meta = cu.observe_screen(env, args.screen,
                                            max_width=cu.CAPTURE_MAX_WIDTH, persist=True)
            envelope['after_screen'] = {
                'id': screen_meta.get('id'),
                'observation': str(screen_meta.get('observation')),
                'capture_params': _capture_params(screen_meta)}
        except Exception as exc:
            envelope['after_error'] = str(exc)[:400]
        try:
            after_meta = _scope_after(cu, env, meta, result_after,
                                      screen_meta)
            if after_meta is not None:
                envelope['after'] = {
                    'id': after_meta.get('id'),
                    'observation': str(after_meta.get('observation')),
                    'capture_params': _capture_params(after_meta)}
        except Exception as exc:
            if envelope.get('after_error') is None:
                envelope['after_error'] = str(exc)[:400]
        phase_ms['after_capture_ms'] = round(
            (time.monotonic() - _after_t0) * 1000, 3)
        return 0 if envelope['ok'] else 1
    except Exception as exc:
        # Council 1, A2: never let an exception escape run(), or cu.py
        # prints a second JSON object after the envelope.
        if envelope.get('error') is None:
            envelope['error'] = str(exc)[:400]
        return 1
    finally:
        envelope['total_ms'] = _ms(t0)
        envelope['first_pointer_ms'] = first_pointer_ms
        envelope['phase_ms'] = phase_ms
        # CB-7: target_breached compares the FIRST-pointer time
        # against the 30 s threshold, not whole-batch time. The old
        # rule (whole run over 30 s) measured the batch, not the
        # first visible action, so a slow batch with a fast first
        # click read as breached and a fast batch with a late first
        # click read as fine. When no pointer action completed (or
        # the result carries no action_ms), the basis falls back to
        # total time and says so; the fallback is explicit, never
        # silent.
        if first_pointer_ms is not None:
            envelope['target_breached'] = bool(
                first_pointer_ms > FIRST_VISIBLE_ACTION_TARGET_MS)
            envelope['target_breached_basis'] = first_pointer_basis
        else:
            envelope['target_breached'] = bool(
                envelope['total_ms'] > FIRST_VISIBLE_ACTION_TARGET_MS)
            envelope['target_breached_basis'] = (
                'total_fallback: no pointer action completed or no '
                'action_ms in result')
        if overlay_acquired:
            release_error = release_overlay(agent, overlay_mod=overlay_mod)
            if release_error is not None:
                envelope['release_error'] = release_error[:400]
        try:
            state_dir = cu.STATE
            state_dir.mkdir(parents=True, exist_ok=True)
            log_path = (state_dir / ('first-action-'
                                     + datetime.now().astimezone()
                                     .strftime('%Y%m%d') + '.jsonl'))
            append_log(log_path, envelope)
        except Exception as exc:
            envelope['log_error'] = str(exc)[:400]
        print(json.dumps(envelope, ensure_ascii=False), flush=True)


def build_parser():
    parser = argparse.ArgumentParser(
        description='Overlay on + session attempt with deadline + direct '
                    'Pointer fallback. First visible action fast.')
    parser.add_argument('--actions', required=True,
                        help='JSON path; same batch format as act')
    parser.add_argument('--observation', default=None,
                        help='fresh observation JSON path; captured when omitted')
    parser.add_argument('--screen', default='eDP-2',
                        help='monitor for a fresh capture')
    parser.add_argument('--agent', default='Muse')
    parser.add_argument('--method', default='act-now')
    parser.add_argument('--label', default=None)
    parser.add_argument('--session-deadline-s', type=float,
                        default=DEFAULT_SESSION_DEADLINE_S,
                        help='hard deadline for each broker result wait '
                             '(step 8: the per-batch session spawn is gone, '
                             'so this bounds the broker act result, not a '
                             'spawned session; the 300 s queue wait is '
                             'separate)')
    parser.add_argument('--dom-selector', default=None,
                        help='CSS selector of the input the type action '
                             'targets; wires the DOM value hooks (focus + '
                             'typed-value check) into the fallback batch '
                             'instead of the pixel band')
    parser.add_argument('--order-wall', default=None,
                        help='ISO wall timestamp of the user order on the '
                             'VM (or set CU_ORDER_WALL); enables '
                             'dispatch_ms, the VM send + SSH connect + '
                             'shell startup split (CB-7)')
    return parser


def main(argv=None):
    return run(build_parser().parse_args(argv))


if __name__ == '__main__':
    raise SystemExit(main())

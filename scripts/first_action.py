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
  target is measured post-hoc from the envelope, not code-enforced
  (FIRST_VISIBLE_ACTION_TARGET_MS is defined but the envelope carries
  no pass/fail verdict against it yet).

Usage (one command, the agent's default for a live action batch):
  computer-use act-now --actions <file> [--observation <path>]
      [--screen <monitor>] [--agent NAME] [--method METHOD]
      [--label TEXT] [--session-deadline-s N]

The actions file is the same JSON batch `act` takes (up to 32 actions).
The observation, when given, must be fresh (under 120 s); otherwise a
fresh screen observation is captured first. The overlay is acquired
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
import signal
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
            overlay_mod.remove_holder(agent)
        except Exception:
            pass
        raise
    return reply


def overlay_visible(agent, overlay_mod=None):
    """True only when the overlay daemon reports the pill visible.

    Used as a re-check immediately before the fallback acts (council 1,
    A5). A dead daemon (socket error) or an empty holder set reports
    False, never raises.
    """
    try:
        if overlay_mod is None:
            import overlay as overlay_mod
        reply = overlay_mod._send_socket({'command': 'status'})
        return isinstance(reply, dict) and reply.get('visible') is True
    except Exception:
        return False


def release_overlay(agent, overlay_mod=None):
    """Release the overlay holder. Returns None on success, else an
    error string. Never raises; the caller records a failure in the
    envelope instead of swallowing it silently (council 1, A5)."""
    try:
        if overlay_mod is None:
            import overlay as overlay_mod
        try:
            overlay_mod._send_socket({'command': 'release', 'agent': agent})
        except (OSError, ValueError):
            overlay_mod.remove_holder(agent)
        return None
    except Exception as exc:
        return str(exc)


def session_cmd(cu_py, observation_path, actions_path):
    """The exact session command the manual flow used, as an argv list."""
    py = sys.executable
    return [py, str(cu_py), 'session', '--', py, str(cu_py), 'act',
            '--observation', str(observation_path),
            '--actions', str(actions_path)]


def attempt_session(cmd, deadline_s, env=None):
    """Run a session command with a hard deadline.

    Returns (returncode, stdout, stderr, timed_out, elapsed_s). On
    timeout the whole process group is terminated, then killed. The
    caller decides, from the output, whether a fallback is safe.
    """
    start = time.monotonic()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True, env=env)
    try:
        out, err = proc.communicate(timeout=deadline_s)
        return proc.returncode, out, err, False, time.monotonic() - start
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            out, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            out, err = proc.communicate()
        return proc.returncode, out, err, True, time.monotonic() - start


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


def _fresh_observation(cu, env, screen, observation_path):
    """Load a given observation when fresh, else capture a new one.

    Returns (meta, observation_path, source). A stale, missing, or
    unreadable given observation is replaced by a fresh screen capture;
    the replacement is recorded in the envelope, never hidden.
    """
    if observation_path:
        try:
            meta = cu.read_json_file(observation_path)
            if (isinstance(meta, dict) and meta.get('id')
                    and meta.get('image')
                    and meta.get('monitor_box')
                    and isinstance(meta.get('created'), (int, float))
                    and time.time() - meta['created']
                    < OBSERVATION_MAX_AGE_S):
                return meta, str(observation_path), 'given'
        except (OSError, ValueError, KeyError):
            pass
    meta = cu.observe_screen(env, screen, max_width=1920, persist=True)
    return meta, str(meta['observation']), 'captured'


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
    cu_py = Path(__file__).resolve().parent / 'cu.py'
    agent = args.agent
    method = args.method
    envelope = {
        'ok': False,
        'path': 'refused',
        'agent': agent,
        'method': method,
        'wall_time': wall0,
        'order_to_overlay_ms': None,
        'order_to_session_attempt_ms': None,
        'total_ms': None,
        'session_error': None,
        'session_timed_out': False,
        'fallback_reason': None,
        'completed': 0,
        'observation': None,
        'after': None,
        'after_error': None,
        'error': None,
        'release_error': None,
        'log_error': None,
    }
    overlay_acquired = False
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
        if not math.isfinite(deadline) or deadline <= 0:
            envelope['error'] = ('invalid session deadline: %r'
                                 % (args.session_deadline_s,))
            envelope['path'] = 'refused'
            return 1
        env = cu.environment()
        try:
            reply = acquire_overlay(agent, method, label=args.label,
                                    overlay_mod=overlay_mod)
        except RuntimeError as exc:
            envelope['error'] = str(exc)
            return 2
        overlay_acquired = True
        envelope['order_to_overlay_ms'] = _ms(t0)
        envelope['overlay_owner'] = reply.get('owner')
        meta, obs_path, obs_source = _fresh_observation(
            cu, env, args.screen, args.observation)
        envelope['observation'] = {'id': meta.get('id'), 'source': obs_source}
        envelope['order_to_session_attempt_ms'] = _ms(t0)
        child_env = dict(env)
        child_env.pop('CU_SESSION_TOKEN', None)
        rc, out, err, timed_out, _elapsed = attempt_session(
            session_cmd(cu_py, obs_path, args.actions),
            deadline, env=child_env)
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
        if rc == 0 and not timed_out:
            # Council 1, A3: the exit code alone never proves success.
            # Require the stdout envelope to say ok, or to be the
            # completed-capture-error shape (full batch ran).
            if (isinstance(session_result, dict)
                    and session_result.get('ok') is True):
                completed = session_result.get('completed')
                envelope['path'] = 'session'
                envelope['ok'] = True
                envelope['completed'] = (completed
                                         if type(completed) is int
                                         else len(actions))
            elif (isinstance(session_result, dict)
                    and _is_completed_capture(session_result,
                                              len(actions))):
                envelope['path'] = 'session'
                envelope['ok'] = True
                envelope['completed'] = len(actions)
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
                    with cu.locked():
                        result = cu.desktop_act(
                            env, meta, actions, observation_path=obs_path)
                    envelope['ok'] = result.get('ok') is True
                    envelope['completed'] = result.get('completed', 0)
                    if not envelope['ok']:
                        envelope['error'] = str(result.get('error', ''))
            else:
                envelope['path'] = 'session'
                envelope['ok'] = False
                envelope['error'] = (
                    session_error or ('session timed out; not replayed'
                                      if timed_out else
                                      'session act failed; not replayed'))
        try:
            after_meta = cu.observe_screen(env, args.screen, max_width=1920,
                                           persist=True)
            envelope['after'] = {'id': after_meta.get('id'),
                                 'observation': str(
                                     after_meta.get('observation'))}
        except Exception as exc:
            envelope['after_error'] = str(exc)[:400]
        return 0 if envelope['ok'] else 1
    except Exception as exc:
        # Council 1, A2: never let an exception escape run(), or cu.py
        # prints a second JSON object after the envelope.
        if envelope.get('error') is None:
            envelope['error'] = str(exc)[:400]
        return 1
    finally:
        envelope['total_ms'] = _ms(t0)
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
                        help='hard deadline for the session attempt')
    return parser


def main(argv=None):
    return run(build_parser().parse_args(argv))


if __name__ == '__main__':
    raise SystemExit(main())

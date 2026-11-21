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
  never acts invisibly.
- D2: overlay + first move happen BEFORE session/observe diagnosis.
- D3: session start has a hard deadline; on a session-START failure the
  run falls back to the direct Pointer path (the same desktop_act the
  session path uses) with the overlay already on, and logs the bypass
  with the guardian's real error. An act failure after the session
  started is NEVER replayed: actions may have partially run.
- D4: order-to-first-visible-action is measured on every run; target
  under 30 s. The envelope records the path, timings, and bypass reason.

Usage (one command, the agent's default for a live action batch):
  computer-use act-now --actions <file> [--observation <path>]
      [--screen <monitor>] [--agent NAME] [--method METHOD]
      [--label TEXT] [--session-deadline-s N]

The actions file is the same JSON batch `act` takes (up to 32 actions).
The observation, when given, must be fresh (under 120 s); otherwise a
fresh screen observation is captured first. The overlay is acquired
before anything else, so the pill is visible within about a second of
the command starting. The run appends a JSON timing record to
STATE/first-action-YYYYMMDD.jsonl.
"""
import argparse
from datetime import datetime
import json
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


def _ms(start):
    return round((time.monotonic() - start) * 1000, 3)


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec='milliseconds')


def acquire_overlay(agent, method, label=None, overlay_mod=None):
    """Acquire the overlay pill. Returns the daemon reply dict.

    Raises RuntimeError when the pill is not visible afterwards. The
    caller must treat that as a refusal, never as a reason to act
    invisibly. overlay_mod is injectable for tests; otherwise the real
    overlay module is imported.
    """
    if overlay_mod is None:
        import overlay as overlay_mod
    pid = os.getpid()
    overlay_mod.add_holder(agent, method, pid=pid)
    overlay_mod._ensure_daemon()
    reply = overlay_mod._send_socket(
        {'command': 'acquire', 'agent': agent, 'method': method, 'pid': pid})
    if not isinstance(reply, dict) or reply.get('visible') is not True:
        raise RuntimeError(
            'overlay unavailable: ' + json.dumps(reply, sort_keys=True))
    if label is None:
        label = overlay_mod._label_for(agent, method)
    return reply


def release_overlay(agent, overlay_mod=None):
    """Release the overlay holder. Best effort; never raises."""
    try:
        if overlay_mod is None:
            import overlay as overlay_mod
        try:
            overlay_mod._send_socket({'command': 'release', 'agent': agent})
        except (OSError, ValueError):
            overlay_mod.remove_holder(agent)
    except Exception:
        pass


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


def _stdout_session_error(stdout):
    """The session command's JSON error, if it printed one."""
    try:
        data = json.loads(stdout)
    except (ValueError, TypeError):
        return None
    if isinstance(data, dict) and isinstance(data.get('error'), str):
        return data['error']
    return None


def is_session_start_failure(stdout, stderr, timed_out, session_live):
    """True only when NO action can have run, so a fallback is safe.

    A session-start failure is: the guardian never became ready (its
    error names the guardian or the cursor guard, or the command printed
    the session-guardian error), or the attempt timed out while no
    session is live. Any other failure (an act refusal, a screen-change
    refusal, a timeout while a session IS live) returns False: the
    actions may have partially run and must never be replayed blind.
    """
    combined = (stdout or '') + '\n' + (stderr or '')
    if timed_out:
        return not session_live
    if 'session guardian startup failed' in combined:
        return True
    if 'Expecting value' in combined:
        return True
    if 'cursor guard' in combined:
        return True
    if _stdout_session_error(stdout) == 'session guardian startup failed':
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
    exit code: 0 action ok, 1 action failed, 2 refused (no overlay)."""
    cu = _load_cu()
    t0 = time.monotonic()
    wall0 = _now_iso()
    cu_py = Path(__file__).resolve().parent / 'cu.py'
    try:
        actions = cu.read_json_file(args.actions)
    except (OSError, ValueError) as exc:
        print(json.dumps({'ok': False, 'error': 'bad actions file: '
                         + str(exc)}, ensure_ascii=False), flush=True)
        return 1
    if not isinstance(actions, list) or not actions:
        print(json.dumps({'ok': False, 'error': 'actions must be a '
                         'non-empty JSON list'}, ensure_ascii=False),
              flush=True)
        return 1
    env = cu.environment()
    agent = args.agent
    method = args.method
    envelope = {
        'ok': False,
        'path': 'refused',
        'agent': agent,
        'method': method,
        'wall_time': wall0,
        'order_to_overlay_ms': None,
        'order_to_action_start_ms': None,
        'total_ms': None,
        'session_error': None,
        'session_timed_out': False,
        'fallback_reason': None,
        'completed': 0,
        'observation': None,
        'after': None,
        'after_error': None,
    }
    overlay_acquired = False
    try:
        try:
            reply = acquire_overlay(agent, method, label=args.label)
        except RuntimeError as exc:
            envelope['error'] = str(exc)
            return 2
        overlay_acquired = True
        envelope['order_to_overlay_ms'] = _ms(t0)
        envelope['overlay_owner'] = reply.get('owner')
        meta, obs_path, obs_source = _fresh_observation(
            cu, env, args.screen, args.observation)
        envelope['observation'] = {'id': meta.get('id'), 'source': obs_source}
        action_start = time.monotonic()
        envelope['order_to_action_start_ms'] = _ms(t0)
        child_env = dict(env)
        child_env.pop('CU_SESSION_TOKEN', None)
        rc, out, err, timed_out, _elapsed = attempt_session(
            session_cmd(cu_py, obs_path, args.actions),
            float(args.session_deadline_s), env=child_env)
        envelope['session_timed_out'] = timed_out
        session_error = _stdout_session_error(out)
        if session_error is None and err.strip():
            session_error = err.strip().splitlines()[-1][:400]
        envelope['session_error'] = session_error
        if rc == 0 and not timed_out:
            envelope['path'] = 'session'
            envelope['ok'] = True
            envelope['completed'] = len(actions)
        else:
            import overlay as overlay_mod
            live = False
            try:
                live = overlay_mod.session_live()
            except Exception:
                live = False
            if is_session_start_failure(out, err, timed_out, live):
                envelope['fallback_reason'] = (
                    session_error or ('session timed out' if timed_out
                                      else 'session start failed'))
                with cu.locked():
                    result = cu.desktop_act(
                        env, meta, actions, observation_path=obs_path)
                envelope['path'] = 'fallback'
                envelope['ok'] = result.get('ok') is True
                envelope['completed'] = result.get('completed', 0)
                if not envelope['ok']:
                    envelope['error'] = str(result.get('error', ''))
            else:
                envelope['path'] = 'session'
                envelope['ok'] = False
                envelope['error'] = (
                    session_error or 'session act failed; not replayed')
        try:
            after_meta = cu.observe_screen(env, args.screen, max_width=1920,
                                           persist=True)
            envelope['after'] = {'id': after_meta.get('id'),
                                 'observation': str(
                                     after_meta.get('observation'))}
        except Exception as exc:
            envelope['after_error'] = str(exc)[:400]
        return 0 if envelope['ok'] else 1
    finally:
        envelope['total_ms'] = _ms(t0)
        if overlay_acquired:
            release_overlay(agent)
        try:
            log_path = (cu.STATE / ('first-action-'
                                    + datetime.now().astimezone()
                                    .strftime('%Y%m%d') + '.jsonl'))
            append_log(log_path, envelope)
        except Exception:
            pass
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

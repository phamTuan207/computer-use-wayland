#!/usr/bin/env python3
"""Deterministic finish for speed-run executors (Track 2, 19/11).

After the verify request returns success, the executor calls this script
once instead of deliberating over close/finish and composing a summary
in-session. The measured finish think (14 to 104s per task, Pick 4 means
35.8 and 40.1s) is pure post-task deliberation: the verify result is
already in hand, so no information is lost by skipping it.

One shell call does, with no model call:
  1. scripted close-out checklist (broker status; best-effort hyprctl
     clients count),
  2. broker finish through session_remote.py, waiting for
     finished/stopped/clean,
  3. offline summary from records.jsonl (loop wall, service totals,
     request counts, verify-to-finish gap), written to
     det-finish-<task-id>.json plus a fixed block in summary.md,
  4. one JSON line on stdout; exit 0 only on finished/stopped/clean.

Usage:
  det_finish.py --lease-file L --task-id P1 --run-dir DIR \
      --verify-evidence <observation id/path or sha> [--label det-finish]

The verify evidence is a short pointer (observation id, image path, or
file sha), never a composed paragraph: capped at 500 chars. The executor
asserts the verify step passed by passing it; this script does not
re-judge the end state.

A task that never verified (blocked, timed out, session died) finishes
through the SAME path, with evidence `BLOCKED:<short reason>`: the
session still finishes deterministically and the summary records the
task as BLOCKED instead of SUCCESS. There is no fallback to a
deliberated finish.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TASK_ID_RE = re.compile(r'[A-Za-z0-9_.:@+-]{1,80}')
MAX_EVIDENCE_CHARS = 500
STATUS_TIMEOUT = 30
FINISH_TIMEOUT = 135
HYPRCTL_TIMEOUT = 10


def _run_remote(session_remote, args, timeout):
    """Run session_remote.py once; return (resp, rc, t0m, t0w, t1m, t1w)."""
    t0m = time.monotonic()
    t0w = time.time()
    proc = subprocess.run([sys.executable, str(session_remote), *args],
                          capture_output=True, text=True, timeout=timeout)
    t1m = time.monotonic()
    t1w = time.time()
    out = (proc.stdout or '').strip()
    try:
        resp = json.loads(out) if out else {}
    except Exception:
        resp = {'_raw': out[:500], '_stderr': (proc.stderr or '')[-500:]}
    if not isinstance(resp, dict):
        resp = {'_raw': str(resp)[:500]}
    return resp, proc.returncode, t0m, t0w, t1m, t1w


def _read_records(path):
    """Read records.jsonl tolerantly. Returns (records, bad_lines)."""
    records = []
    bad_lines = 0
    if not path.is_file():
        return records, bad_lines
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                bad_lines += 1
    return records, bad_lines


def _derive_summary(records):
    """Derive loop timing from records. Missing pieces stay None."""
    start_submit = None
    last_request_result = None
    service_total = 0.0
    startup_s = None
    by_kind = {}
    image_bytes = 0
    requests = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        cmd = record.get('cmd')
        if cmd == 'start':
            if start_submit is None and record.get('submit_wall') is not None:
                start_submit = record['submit_wall']
            if startup_s is None and record.get('start_call_s') is not None:
                startup_s = record['start_call_s']
        elif cmd == 'request':
            requests += 1
            kind = str(record.get('kind') or 'unknown')
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if isinstance(record.get('service_s'), (int, float)):
                service_total += record['service_s']
            if isinstance(record.get('image_bytes_total'), int):
                image_bytes += record['image_bytes_total']
            if record.get('result_wall') is not None:
                last_request_result = record['result_wall']
    loop_wall = None
    if start_submit is not None and last_request_result is not None:
        loop_wall = round(last_request_result - start_submit, 3)
    return {
        'loop_wall_s': loop_wall,
        'service_s_total': round(service_total, 3),
        'startup_s': startup_s,
        'requests': requests,
        'requests_by_kind': by_kind,
        'image_bytes_total': image_bytes,
        'verify_result_wall': last_request_result,
    }


def _hyprctl_clients():
    """Best-effort desktop check. Never fatal, never blocks the finish."""
    if shutil.which('hyprctl') is None:
        return {'available': False, 'count': None, 'titles': []}
    try:
        proc = subprocess.run(['hyprctl', 'clients', '-j'],
                              capture_output=True, text=True,
                              timeout=HYPRCTL_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return {'available': False, 'count': None, 'titles': []}
    try:
        clients = json.loads(proc.stdout or '[]')
    except json.JSONDecodeError:
        return {'available': True, 'count': None, 'titles': []}
    if not isinstance(clients, list):
        return {'available': True, 'count': None, 'titles': []}
    titles = [str(c.get('title') or '') for c in clients
              if isinstance(c, dict)][:20]
    return {'available': True, 'count': len(clients), 'titles': titles}


def _append_record(log_path, record):
    """Append one JSON line, never gluing onto a unterminated last line."""
    line = json.dumps(record, ensure_ascii=False)
    with open(log_path, 'a', encoding='utf-8') as handle:
        if log_path.stat().st_size > 0:
            with open(log_path, 'rb') as check:
                check.seek(-1, 2)
                if check.read(1) != b'\n':
                    handle.write('\n')
        handle.write(line + '\n')


def _summary_block(task_id, summary):
    """Fixed-format summary.md block for one task."""
    finish = summary['finish']
    timing = summary['timing']
    lines = [
        '<!-- det-finish %s -->' % task_id,
        '## %s (deterministic finish)' % task_id,
        '',
        '- Result: %s (status %s, driver %s, guardian %s)' % (
            summary['task_outcome'],
            finish.get('status'), finish.get('driver'),
            finish.get('guardian')),
        '- Verify evidence: `%s`' % summary['verify_evidence'],
        '- Loop wall (start submit to verify result): %s s' % (
            timing['loop_wall_s']),
        '- Broker service total: %s s; startup: %s s' % (
            timing['service_s_total'], timing['startup_s']),
        '- Requests: %s %s' % (
            timing['requests'], timing['requests_by_kind']),
        '- Verify-to-finish gap (script submit minus verify result): %s s' % (
            timing['verify_to_finish_s']),
        '- Deterministic finish call: %s s' % timing['det_finish_s'],
        '- Desktop clients at close-out: %s' % (
            summary['closeout']['hyprctl'].get('count')),
        '<!-- /det-finish %s -->' % task_id,
        '',
    ]
    return '\n'.join(lines)


def _write_summary_block(summary_path, task_id, block):
    """Append the block, replacing any earlier block for the same task."""
    start_marker = '<!-- det-finish %s -->' % task_id
    end_marker = '<!-- /det-finish %s -->' % task_id
    existing = ''
    if summary_path.is_file():
        existing = summary_path.read_text(encoding='utf-8')
    if start_marker in existing and end_marker in existing:
        before = existing[:existing.index(start_marker)]
        after = existing[existing.index(end_marker) + len(end_marker):]
        summary_path.write_text(before + block + after.lstrip('\n'),
                                encoding='utf-8')
    else:
        with open(summary_path, 'a', encoding='utf-8') as handle:
            if existing and not existing.endswith('\n'):
                handle.write('\n')
            handle.write(block)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lease-file', type=Path, required=True)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--verify-evidence', required=True)
    parser.add_argument('--label', default='det-finish')
    parser.add_argument('--session-remote', type=Path,
                        default=Path(__file__).resolve().parent
                        / 'session_remote.py')
    parser.add_argument('--skip-hyprctl', action='store_true')
    args = parser.parse_args(argv)

    submit_m = time.monotonic()
    submit_w = time.time()

    def fail(error):
        print(json.dumps({'ok': False, 'error': error,
                          'task_id': args.task_id}, ensure_ascii=False))
        return 2

    if not TASK_ID_RE.fullmatch(args.task_id):
        return fail('invalid_task_id')
    if not args.verify_evidence or not args.verify_evidence.strip():
        return fail('empty_verify_evidence')
    if len(args.verify_evidence) > MAX_EVIDENCE_CHARS:
        return fail('verify_evidence_too_long')
    if not args.lease_file.is_file():
        return fail('lease_file_missing')
    if not args.session_remote.is_file():
        return fail('session_remote_missing')
    args.run_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.run_dir / 'records.jsonl'

    records, bad_lines = _read_records(records_path)
    timing = _derive_summary(records)
    verify_wall = timing['verify_result_wall']
    timing['verify_to_finish_s'] = (
        round(submit_w - verify_wall, 3)
        if verify_wall is not None else None)

    # Scripted close-out checklist: broker status, then (best effort)
    # the desktop client list. Neither step deliberates; both are recorded.
    try:
        status_resp, _, _, _, _, _ = _run_remote(
            args.session_remote,
            ['status', '--lease-file', str(args.lease_file)], STATUS_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        status_resp = {'ok': False, 'error': 'status_call_failed'}
    closeout = {
        'broker_status': {
            'ok': status_resp.get('ok'),
            'state': status_resp.get('state'),
            'driver': status_resp.get('driver'),
            'error': status_resp.get('error'),
        },
        'hyprctl': ({'available': False, 'count': None, 'titles': []}
                    if args.skip_hyprctl else _hyprctl_clients()),
    }

    try:
        finish_resp, _, f0m, _, f1m, _ = _run_remote(
            args.session_remote,
            ['finish', '--lease-file', str(args.lease_file)],
            FINISH_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        finish_resp = {'ok': False, 'error': 'finish_call_failed'}
        f0m, f1m = submit_m, time.monotonic()
    timing['det_finish_s'] = round(f1m - f0m, 3)

    ok = bool(finish_resp.get('ok') is True
              and finish_resp.get('status') == 'finished'
              and finish_resp.get('driver') == 'stopped'
              and finish_resp.get('guardian') == 'clean')
    blocked = (args.verify_evidence.startswith('BLOCKED:')
               and args.verify_evidence[len('BLOCKED:'):].strip())
    if ok:
        task_outcome = 'BLOCKED' if blocked else 'SUCCESS'
    else:
        task_outcome = 'FINISH-FAILED'
    summary = {
        'task_id': args.task_id,
        'label': args.label,
        'ok': ok,
        'task_outcome': task_outcome,
        'blocked_reason': blocked or None,
        'verify_evidence': args.verify_evidence,
        'finish': {
            'ok': finish_resp.get('ok'),
            'status': finish_resp.get('status'),
            'driver': finish_resp.get('driver'),
            'guardian': finish_resp.get('guardian'),
            'error': finish_resp.get('error'),
        },
        'timing': timing,
        'closeout': closeout,
        'records_lines': len(records),
        'records_bad_lines': bad_lines,
        'generated_wall': time.time(),
    }

    json_path = args.run_dir / ('det-finish-%s.json' % args.task_id)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2)
                         + '\n', encoding='utf-8')
    _write_summary_block(args.run_dir / 'summary.md', args.task_id,
                         _summary_block(args.task_id, summary))
    _append_record(records_path, {
        'cmd': 'det-finish', 'label': args.label,
        'task_id': args.task_id,
        'submit_mono': submit_m, 'submit_wall': submit_w,
        'result_mono': time.monotonic(), 'result_wall': time.time(),
        'service_s': timing['det_finish_s'],
        'ok': ok, 'status': finish_resp.get('status'),
        'driver': finish_resp.get('driver'),
        'guardian': finish_resp.get('guardian'),
        'error': finish_resp.get('error'),
        'loop_wall_s': timing['loop_wall_s'],
        'verify_to_finish_s': timing['verify_to_finish_s'],
    })

    out = {'ok': ok, 'task_id': args.task_id,
           'status': finish_resp.get('status'),
           'driver': finish_resp.get('driver'),
           'guardian': finish_resp.get('guardian'),
           'error': finish_resp.get('error'),
           'det_finish_s': timing['det_finish_s'],
           'loop_wall_s': timing['loop_wall_s'],
           'verify_to_finish_s': timing['verify_to_finish_s'],
           'summary_path': str(json_path)}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())

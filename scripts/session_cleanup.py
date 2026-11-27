#!/usr/bin/env python3
"""Verify the desktop is clean after a computer-use session ends (C8).

Fixes 3.1.8 (C8: windows, session, and pill left running after use).
The session guardian already cleans up (cursor_session.restore removes
the cursor theme, the indicator endpoint, the snapshot, and the stop
marker), but nothing ever VERIFIED that cleanup happened. This script
is the verification: run it after `computer-use finish` / `stop` and
it fails loudly while anything is left over.

Checks (all read-only for --check):
1. No session snapshot (STATE/session.json).
2. No indicator endpoint socket (STATE/indicator-*.sock).
3. No stop markers (STATE/stop-*).
4. No overlay holders (STATE/overlay/holders.json non-empty).
5. No guardian process (a cmdline containing both `cursor_session`
   and `guard`).

`--clean` only does the safe parts: prune dead overlay holders and
remove orphaned stop markers when no snapshot exists. A live guardian
or snapshot is never killed or deleted blindly; the script reports it
and the operator runs `computer-use stop` on the laptop instead.

Usage:
    python3 scripts/session_cleanup.py --check [--state-dir DIR]
    python3 scripts/session_cleanup.py --clean [--state-dir DIR]
Exit 0 when clean, 1 when leftovers remain.
"""
import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_STATE = Path.home() / '.cache' / 'agent-computer-use'


def _read_proc_cmdlines():
    """Yield (pid, cmdline) from /proc, skipping unreadable entries."""
    proc = Path('/proc')
    if not proc.is_dir():
        return
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            raw = (entry / 'cmdline').read_bytes()
        except OSError:
            continue
        yield int(entry.name), raw.decode('utf-8', 'replace').replace('\x00', ' ').strip()


def _read_procs_file(path):
    """Yield (pid, cmdline) from a 'pid cmdline' text file.

    Test support: lets the CLI exit-code test run hermetically
    instead of depending on the ambient /proc (a parallel test
    runner's own cmdline can contain 'cursor_session' + 'guard').
    """
    for line in Path(path).read_text().splitlines():
        pid, _, cmdline = line.partition(' ')
        if pid.isdigit():
            yield int(pid), cmdline


def find_leftovers(state_dir, proc_cmdlines=None):
    """Return a list of leftover descriptions. Empty means clean."""
    state = Path(state_dir)
    leftovers = []
    if (state / 'session.json').exists():
        leftovers.append(f'session snapshot still exists: {state / "session.json"}')
    for sock in sorted(state.glob('indicator-*.sock')):
        leftovers.append(f'indicator endpoint still exists: {sock}')
    for marker in sorted(state.glob('stop-*')):
        leftovers.append(f'stop marker still exists: {marker}')
    holders_file = state / 'overlay' / 'holders.json'
    try:
        holders = json.loads(holders_file.read_text())
    except (OSError, ValueError):
        holders = {}
    if isinstance(holders, dict) and holders:
        leftovers.append('overlay holders still present: '
                        + ', '.join(sorted(holders)))
    if proc_cmdlines is None:
        proc_cmdlines = _read_proc_cmdlines()
    for pid, cmdline in proc_cmdlines:
        if 'cursor_session' in cmdline and 'guard' in cmdline:
            leftovers.append(f'session guardian still running: pid {pid}')
    return leftovers


def clean_safe(state_dir):
    """Do the safe cleanup parts; return (cleaned, still_left)."""
    state = Path(state_dir)
    cleaned = []
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import overlay
        overlay.BASE = state
        overlay.OVERLAY_DIR = state / 'overlay'
        overlay.HOLDERS_FILE = overlay.OVERLAY_DIR / 'holders.json'
        overlay.LOCK_FILE = overlay.OVERLAY_DIR / 'holders.lock'
        pruned = overlay.prune_dead_holders()
        if pruned:
            cleaned.append(f'pruned dead overlay holders: {", ".join(pruned)}')
    except Exception as exc:  # noqa: BLE001 - cleanup must not die on one part
        cleaned.append(f'overlay prune failed: {exc}')
    if not (state / 'session.json').exists():
        for marker in sorted(state.glob('stop-*')):
            try:
                marker.unlink()
                cleaned.append(f'removed orphaned stop marker: {marker.name}')
            except OSError as exc:
                cleaned.append(f'could not remove {marker.name}: {exc}')
    return cleaned


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--state-dir', default=str(DEFAULT_STATE))
    parser.add_argument('--procs-file', default=None,
                        help='read (pid, cmdline) pairs from this file '
                             'instead of /proc (test support)')
    args = parser.parse_args(argv)
    if args.procs_file and os.environ.get('CU_TEST_PROCS_FILE') != '1':
        print('--procs-file is test-only; set CU_TEST_PROCS_FILE=1 to use it', file=sys.stderr)
        return 2
    if not (args.check or args.clean):
        print('usage: session_cleanup.py --check|--clean [--state-dir DIR]', file=sys.stderr)
        return 2
    state = Path(args.state_dir)
    if args.clean:
        for line in clean_safe(state):
            print('cleaned: ' + line)
    try:
        procs = _read_procs_file(args.procs_file) if args.procs_file else None
        leftovers = find_leftovers(state, proc_cmdlines=procs)
    except OSError as exc:
        print(f'cannot read procs file {args.procs_file}: {exc}', file=sys.stderr)
        return 2
    if not leftovers:
        print(f'desktop clean: no leftovers in {state}')
        return 0
    print(f'desktop NOT clean: {len(leftovers)} leftover(s) in {state}:')
    for item in leftovers:
        print(f'  - {item}')
    if any('guardian' in item or 'snapshot' in item for item in leftovers):
        print('run `computer-use stop` on the laptop; do not kill the guardian blindly')
    return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

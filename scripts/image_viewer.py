"""Image-viewer hygiene (G5).

The image viewer binary is `imv-wayland`, NOT `imv`: `pkill -x imv`,
`pgrep -x imv`, and greps for " imv" all MISS it, so instances pile up,
one hangs, and the desktop-hygiene gate (tc02) fails the run. After every
photo viewed with imv, kill it with `pkill -x imv-wayland` before the
next step. This module is the one place that knows the exact name.

Usage:

    python3 scripts/image_viewer.py kill   # kill all imv-wayland, print JSON
    python3 scripts/image_viewer.py list   # list running imv-wayland PIDs
"""
import argparse
import json
import subprocess
import sys

VIEWER_COMM = 'imv-wayland'


def list_image_viewers(run=subprocess.run):
    """Return the PIDs of running imv-wayland processes (empty when none)."""
    proc = run(['pgrep', '-x', VIEWER_COMM], capture_output=True, text=True)
    if proc.returncode == 1:
        return []
    if proc.returncode != 0:
        raise RuntimeError(f'pgrep -x {VIEWER_COMM} failed: {proc.stderr.strip()[:200]}')
    return [int(line) for line in proc.stdout.splitlines() if line.strip()]


def kill_image_viewer(run=subprocess.run):
    """Kill every imv-wayland process. Returns {'killed': bool, 'pids': [...]}.

    `killed` is True only when pkill matched at least one process. It is
    False (not an error) when no viewer was running.
    """
    before = list_image_viewers(run=run)
    proc = run(['pkill', '-x', VIEWER_COMM], capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(f'pkill -x {VIEWER_COMM} failed: {proc.stderr.strip()[:200]}')
    return {'killed': proc.returncode == 0, 'pids': before}


def main(argv=None):
    parser = argparse.ArgumentParser(description='List or kill the imv-wayland image viewer.')
    parser.add_argument('command', choices=('list', 'kill'))
    args = parser.parse_args(argv)
    result = list_image_viewers() if args.command == 'list' else kill_image_viewer()
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

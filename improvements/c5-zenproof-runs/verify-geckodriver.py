#!/usr/bin/env python3
"""Minimal geckodriver + Marionette session verify (W-GECKO, R14).

Opens ONE ZenSession against the live Zen, reads only the current
handle and the handle count (both plain GETs), then closes the
session in finally. It never switches tabs, never navigates, never
types, never clicks, never opens a tab. Run on the laptop:

  python3 ~/c5-zenproof-run/verify-geckodriver.py

Exit 0 only when the session opened, answered, and closed cleanly.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '~/computer-use-wayland/scripts')
import zen_dom  # noqa: E402


def main():
    t0 = time.monotonic()
    version = subprocess.run(
        [zen_dom.GECKODRIVER, '--version'],
        capture_output=True, text=True, timeout=30)
    print(json.dumps({
        'geckodriver_path': zen_dom.GECKODRIVER,
        'geckodriver_version_rc': version.returncode,
        'geckodriver_version': version.stdout.strip().splitlines()[0]
        if version.stdout.strip() else '',
    }))
    if version.returncode != 0:
        print(json.dumps({'ok': False, 'error': 'geckodriver --version failed'}))
        return 1
    try:
        with zen_dom.ZenSession() as z:
            current = z.current_handle()
            handles = z._wd('GET', '/session/%s/window/handles' % z.session)['value']
            print(json.dumps({
                'ok': True,
                'session_opened': True,
                'current_handle_prefix': str(current)[:8],
                'handle_count': len(handles),
                'wall_ms': round((time.monotonic() - t0) * 1000.0, 1),
            }))
    except zen_dom.ZenDomError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)[:400]}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

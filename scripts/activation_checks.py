"""Bounded read-only checks for the accepted glass config after first-load."""
import subprocess
import time

import indicator


def wait_for_profile(env, timeout=8.0):
    """Wait for a clean config evaluation and ready glass metadata; no reloads."""
    deadline = time.monotonic() + timeout
    last = 'config status unavailable'
    while True:
        try:
            errors = subprocess.check_output(['hyprctl', 'configerrors'], env=env,
                                             text=True, timeout=2).strip()
            if errors:
                last = 'Hyprland reported config errors'
            elif indicator.liquid_available(env, ready=True):
                return True
            else:
                last = 'accepted glass status is not ready'
        except (OSError, subprocess.SubprocessError):
            last = 'config status unavailable'
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('config reload did not reach an accepted ready state: ' + last)
        time.sleep(min(0.1, remaining))

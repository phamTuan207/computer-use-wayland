#!/usr/bin/env python3
"""Activate the session backend (glass, then guard) under ONE owner lock.

Council-2 precondition 4: activate-glass.py takes no owner_lock, so two
concurrent runs can both pass the pre-load check, and a retry after a
partial success fails closed with a misleading message. This wrapper holds
cursor_session.owner_lock() across the whole glass + guard sequence, so no
session and no second activation can interleave, and a half-loaded state
is never left to a blind retry. The pinned values come from
native/visuals.json (library, cursor_guard_library, abi, profile_sha256)
unless overridden on the command line.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cursor_session
import cursor_theme
import indicator


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


glass_activate = _load('activate_glass', 'activate-glass.py').activate
guard_activate = _load('activate_cursor_guard', 'activate-cursor-guard.py').activate


def read_manifest(manifest):
    data = json.loads(Path(manifest).read_text())
    return {
        'glass_library': data['library'],
        'guard_library': data['cursor_guard_library'],
        'abi': data['abi'],
        'profile_sha256': data['profile_sha256'],
    }


def verify(env):
    """Plugin list shows glass + guard, the guard answers, glass is ready."""
    import plugin_inventory
    answer = subprocess.check_output(['hyprctl', '-j', 'plugin', 'list'],
                                     env=env, text=True, timeout=5)
    names = {entry.get('name') for entry in
             plugin_inventory.setup_snapshot(answer)}
    missing = {'hyprglass', 'computer-use-cursor'} - names
    if missing:
        raise RuntimeError('backend verification failed, missing plugins: ' +
                           ', '.join(sorted(missing)))
    cursor_theme.check_guard(env)
    if not indicator.liquid_available(env, ready=True):
        raise RuntimeError('backend verification failed, hyprglass is not ready')
    return sorted(names)


def activate(manifest, env, *, glass_library=None, guard_library=None,
             abi=None, profile_sha256=None):
    values = read_manifest(manifest)
    glass_library = glass_library or values['glass_library']
    guard_library = guard_library or values['guard_library']
    abi = abi or values['abi']
    profile_sha256 = profile_sha256 or values['profile_sha256']
    with cursor_session.owner_lock():
        glass_activate(glass_library, abi, profile_sha256, env)
        guard_activate(guard_library, abi, env)
        names = verify(env)
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,
                        default=HERE.parent / 'native' / 'visuals.json',
                        help='pinned values (default: native/visuals.json)')
    parser.add_argument('--glass-library', type=Path)
    parser.add_argument('--guard-library', type=Path)
    parser.add_argument('--abi')
    parser.add_argument('--profile-sha256')
    args = parser.parse_args(argv)
    import cu
    try:
        names = activate(args.manifest, cu.environment(),
                         glass_library=args.glass_library,
                         guard_library=args.guard_library,
                         abi=args.abi, profile_sha256=args.profile_sha256)
    except Exception as exc:
        print('activate-session-backend: ' + str(exc), file=sys.stderr)
        return 1
    print('session backend ready: ' + ', '.join(names))
    return 0


if __name__ == '__main__':
    sys.exit(main())

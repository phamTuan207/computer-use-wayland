#!/usr/bin/env python3
"""Refresh the visuals manifest after an accepted plugin/profile change.

setup.py is the only existing manifest writer, but it cannot do this job: it
rebuilds glass from a fresh upstream clone (build-glass.py applies only
native/hyprglass-local-optics.patch, so a shader change committed as a separate
patch would be lost from the rebuild) and it refuses while any plugin is
loaded, so it can never run inside a live session where the glass is already
active.

This script covers the narrow case setup.py cannot: the new immutable plugin
is already built and installed, and only the manifest is stale (new library
path and/or new optics profile hash). It re-validates every other manifest
field against the live machine before writing, and it never builds, installs,
loads, unloads or reloads anything. The refreshed manifest is what the
fresh-login loader (scripts/visuals.py) and the guarded sync
(scripts/sync-installed.py) both check before they trust it.

Usage:
    python3 scripts/refresh-visuals-manifest.py <library>
        [--manifest PATH] [--installed-root PATH]

The library must be an already-installed immutable hyprglass plugin: an
absolute regular file named hyprglass-<sha256>.so under
<installed-root>/plugins whose bytes hash to its own name.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

import cu
import cursor_theme
from visuals import atomic_write

ROOT = Path(__file__).resolve().parents[1]
OPTICS = ROOT / 'native/hyprglass-local-optics.lua'
DEFAULT_MANIFEST = ROOT / 'native/visuals.json'
DEFAULT_INSTALLED_ROOT = Path.home() / '.local/share/agent-computer-use'
HASHED_LIBRARY = re.compile(r'^(hyprglass|cursor-guard)-([0-9a-f]{64})\.so$')
REQUIRED_STRINGS = ('abi', 'library', 'profile_sha256', 'setup_instance',
                    'cursor_guard_library', 'cursor_directory',
                    'cursor_tree_sha256')


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _validated_hash_library(path, prefix, plugins_dir):
    """Resolve one immutable hash-named plugin under the installed plugins dir."""
    raw = Path(path)
    if raw.is_symlink():
        raise RuntimeError(f'plugin must be a regular file, not a symlink: {path}')
    try:
        library = raw.resolve(strict=True)
    except OSError as error:
        raise RuntimeError(f'plugin is missing or unreadable: {path}') from error
    if not library.is_file():
        raise RuntimeError(f'plugin must be a regular file: {path}')
    if library.parent.resolve() != plugins_dir.resolve():
        raise RuntimeError(f'plugin is not under the installed plugins dir: {path}')
    match = HASHED_LIBRARY.fullmatch(library.name)
    if not match or match.group(1) != prefix:
        raise RuntimeError(f'plugin must be hash-named {prefix}-<sha256>.so: {path}')
    if _sha256(library) != match.group(2):
        raise RuntimeError(f'plugin hash mismatch: {path} does not hash to its own name')
    return library


def _runtime_abi(env):
    """Read the running compositor ABI, rejecting malformed shapes cleanly."""
    try:
        response = json.loads(subprocess.check_output(
            ['hyprctl', '-j', 'version'], env=env, text=True, timeout=5))
    except (json.JSONDecodeError, TypeError, OSError, subprocess.SubprocessError) as error:
        raise RuntimeError('invalid compositor ABI response') from error
    if not isinstance(response, dict) or not isinstance(response.get('abiHash'), str) \
            or not response['abiHash']:
        raise RuntimeError('invalid compositor ABI response: missing abiHash')
    return response['abiHash']


def _validate_cursor(manifest, env):
    """Mirror the fresh-login loader's cursor checks against the live machine."""
    profile_path = cursor_theme.PROFILE
    if profile_path.is_symlink() or not profile_path.is_file():
        raise RuntimeError('cursor profile must be a regular file')
    try:
        profile = json.loads(profile_path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError('cursor profile is not valid JSON') from error
    if not isinstance(profile, dict):
        raise RuntimeError('cursor profile must be an object')
    if profile.get('restore_mode') is not None:
        raise RuntimeError('explicit cursor restoration values are required')
    try:
        cursor_theme.validate(profile['theme'], profile['size'])
        cursor_theme.validate(profile['restore_theme'], profile['restore_size'])
    except KeyError as error:
        raise RuntimeError('cursor profile is missing a required field') from error
    directory = Path(manifest['cursor_directory'])
    if profile['theme'] == directory.name:
        if not directory.is_absolute() or directory.is_symlink() or not directory.is_dir():
            raise RuntimeError('cursor directory is unavailable')
        if directory.parent.resolve() not in cursor_theme.search_roots(env):
            raise RuntimeError('cursor is outside the Xcursor search path')
        digest = runpy.run_path(str(ROOT / 'scripts/build-cursor.py'))['tree_digest'](directory)
        if digest != manifest['cursor_tree_sha256'] \
                or profile['theme'] != 'cu-agent-' + digest \
                or directory.name != profile['theme']:
            raise RuntimeError('cursor tree differs from setup')
    return profile


def refresh(library, manifest_path, installed_root, env):
    """Point the manifest at an installed plugin + the current optics profile.

    Only 'library' and 'profile_sha256' ever change; every other field is
    re-validated and preserved byte-for-byte. Returns a result dict.
    """
    if os.environ.get('CU_SESSION_TOKEN') or env.get('CU_SESSION_TOKEN'):
        raise RuntimeError('refusing to refresh the manifest inside an automation session')
    manifest_path = Path(manifest_path)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError(f'manifest must be a regular file: {manifest_path}')
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f'invalid visuals manifest: {manifest_path}') from error
    if not isinstance(manifest, dict):
        raise RuntimeError('manifest must be an object')
    if type(manifest.get('version')) is not int or manifest['version'] != 1:
        raise RuntimeError('manifest version must be exactly the integer 1')
    missing = [key for key in REQUIRED_STRINGS
               if not isinstance(manifest.get(key), str) or not manifest[key]]
    if missing:
        raise RuntimeError('manifest missing required strings: ' + ', '.join(missing))
    plugins_dir = Path(installed_root) / 'plugins'
    library = _validated_hash_library(library, 'hyprglass', plugins_dir)
    if OPTICS.is_symlink() or not OPTICS.is_file():
        raise RuntimeError('accepted optics profile is missing')
    profile_sha256 = _sha256(OPTICS)
    abi = _runtime_abi(env)
    if abi != manifest['abi']:
        raise RuntimeError('compositor ABI drifted from the manifest; rebuild before refresh')
    _validated_hash_library(manifest['cursor_guard_library'], 'cursor-guard', plugins_dir)
    _validate_cursor(manifest, env)
    instance = (env.get('HYPRLAND_INSTANCE_SIGNATURE') or '').strip()
    if not instance:
        raise RuntimeError('no compositor instance in this environment')
    if instance == manifest['setup_instance']:
        raise RuntimeError('already inside the login that set this up; refusing to refresh')
    if str(library) == manifest['library'] and profile_sha256 == manifest['profile_sha256']:
        return {'ok': True, 'changed': False, 'library': str(library),
                'profile_sha256': profile_sha256, 'manifest': str(manifest_path),
                'abi': abi}
    updated = dict(manifest)
    updated['library'] = str(library)
    updated['profile_sha256'] = profile_sha256
    atomic_write(manifest_path, (json.dumps(updated, indent=2) + '\n').encode())
    return {'ok': True, 'changed': True, 'library': str(library),
            'profile_sha256': profile_sha256, 'manifest': str(manifest_path),
            'abi': abi}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path,
                        help='already-installed immutable hyprglass plugin, '
                             'e.g. ~/.local/share/agent-computer-use/plugins/'
                             'hyprglass-<sha256>.so')
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--installed-root', type=Path, default=DEFAULT_INSTALLED_ROOT)
    arguments = parser.parse_args(argv)
    try:
        result = refresh(arguments.library, arguments.manifest,
                         arguments.installed_root, cu.environment())
    except Exception as exc:
        print('refresh-visuals-manifest: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())

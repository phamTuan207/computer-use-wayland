#!/usr/bin/env python3
"""Activate an immutable accepted plugin; reject ABI drift and hot swapping."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import cu
import activation_checks
import plugin_inventory


def activate(library, abi, profile_sha256, env, *, before_load=None, after_reload=None):
    library = Path(library).resolve(strict=True)
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    if library.name != 'hyprglass-' + digest + '.so':
        raise RuntimeError('plugin must have its immutable SHA256 filename')
    if not isinstance(profile_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', profile_sha256):
        raise RuntimeError('accepted profile SHA256 is required')
    profile = Path(__file__).resolve().parents[1] / 'native/hyprglass-local-optics.lua'
    def require_profile_provenance():
        if profile.is_symlink() or not profile.is_file():
            raise RuntimeError('accepted profile missing')
        if hashlib.sha256(profile.read_bytes()).hexdigest() != profile_sha256:
            raise RuntimeError('accepted profile provenance changed before activation')

    require_profile_provenance()

    def query(*args):
        answer = subprocess.check_output(['hyprctl', *args], env=env, text=True, timeout=5)
        if len(answer.encode()) > 65536:
            raise RuntimeError('glass activation response exceeds bounds')
        return answer

    try:
        version = json.loads(query('-j', 'version'))
    except (json.JSONDecodeError, TypeError) as error:
        raise RuntimeError('invalid compositor version response') from error
    if not isinstance(version, dict) or version.get('abiHash') != abi:
        raise RuntimeError('Hyprland ABI changed; rebuild and verify plugin before activation')
    loaded_snapshot = plugin_inventory.setup_snapshot(query('-j', 'plugin', 'list'))
    loaded = plugin_inventory.setup_baseline(loaded_snapshot)
    if before_load is not None:before_load()
    try:
        current_version = json.loads(query('-j', 'version'))
    except (json.JSONDecodeError, TypeError) as error:
        raise RuntimeError('invalid compositor version response') from error
    current_snapshot = plugin_inventory.setup_snapshot(query('-j', 'plugin', 'list'))
    current_plugins = plugin_inventory.setup_baseline(current_snapshot)
    if (current_version != version or current_plugins != loaded or
            current_snapshot != loaded_snapshot):
        raise RuntimeError('compositor ownership changed before glass activation')
    require_profile_provenance()
    answer = query('plugin', 'load', str(library)).strip()
    if answer != 'ok':
        raise RuntimeError('plugin load refused: ' + answer)
    plugin_inventory.assert_glass_added(loaded_snapshot, query('-j', 'plugin', 'list'))
    answer = query('reload').strip()
    if answer != 'ok':
        raise RuntimeError('normal config reload refused: ' + answer)
    if after_reload is not None:
        after_reload()
    activation_checks.wait_for_profile(env)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    parser.add_argument('--abi', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    try:
        activate(args.library, args.abi, args.profile_sha256, cu.environment())
    except Exception as exc:
        print('activate-glass: ' + str(exc), file=sys.stderr)
        sys.exit(1)
    print('accepted liquid-glass backend ready; verify the indicator namespace visually')

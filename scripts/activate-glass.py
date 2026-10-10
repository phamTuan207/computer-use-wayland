#!/usr/bin/env python3
"""Activate an immutable accepted plugin; reject ABI drift and hot swapping."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import cu
import indicator


def activate(library, abi, env):
    library = Path(library).resolve(strict=True)
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    if library.name != 'hyprglass-' + digest + '.so':
        raise RuntimeError('plugin must have its immutable SHA256 filename')
    def query(*args):
        return subprocess.check_output(['hyprctl', *args], env=env, text=True, timeout=10)
    version = json.loads(query('-j', 'version'))
    if version.get('abiHash') != abi:
        raise RuntimeError('Hyprland ABI changed; rebuild and verify plugin before activation')
    loaded = json.loads(query('-j', 'plugin', 'list'))
    if not isinstance(loaded, list):
        raise RuntimeError('invalid plugin inventory')
    if loaded:
        raise RuntimeError('plugins already loaded; refusing reload or hot swap')
    profile = Path(__file__).resolve().parents[1] / 'native/hyprglass-local-optics.lua'
    if not profile.is_file():
        raise RuntimeError('accepted profile missing')
    answer = query('plugin', 'load', str(library)).strip()
    if answer != 'ok':
        raise RuntimeError('plugin load refused: ' + answer)
    answer = query('eval', 'dofile(' + json.dumps(str(profile)) + ')').strip()
    if answer != 'ok':
        raise RuntimeError('profile activation refused: ' + answer)
    if not indicator.liquid_available(env):
        raise RuntimeError('accepted liquid backend unavailable after activation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path)
    parser.add_argument('--abi', required=True)
    args = parser.parse_args()
    try:
        activate(args.library, args.abi, cu.environment())
    except Exception as exc:
        print('activate-glass: ' + str(exc), file=sys.stderr)
        sys.exit(1)
    print('accepted liquid-glass profile active')

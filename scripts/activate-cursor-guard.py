#!/usr/bin/env python3
"""First-load the immutable cursor backend; never unload or hot-swap a plugin."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import indicator
import plugin_inventory

PIN = '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947'


def activate(library, abi, env, *, before_load=None):
    """Caller holds cursor_session.owner_lock (the login loader or this CLI)."""
    import cursor_session
    if env.get('CU_SESSION_TOKEN') or os.environ.get('CU_SESSION_TOKEN') or cursor_session.SNAPSHOT.exists():
        raise RuntimeError('finish or recover the session before cursor activation')
    library = Path(library)
    if library.is_symlink() or not library.is_absolute() or not library.is_file():
        raise RuntimeError('cursor backend must be an absolute regular file')
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    if library.name != 'cursor-guard-' + digest + '.so':
        raise RuntimeError('cursor backend must carry its immutable SHA256 filename')

    def query(*args):
        answer = subprocess.check_output(['hyprctl',*args],env=env,text=True,timeout=10)
        if len(answer.encode()) > 65536:raise RuntimeError('cursor activation response exceeds bounds')
        return answer

    version = json.loads(query('-j','version'))
    if (not isinstance(version,dict) or version.get('version') != '0.57.2' or
        version.get('commit') != PIN or version.get('abiHash') != abi or
        not isinstance(abi,str) or not abi.startswith(PIN+'_')):
        raise RuntimeError('cursor backend requires the pinned Hyprland 0.57.2 ABI')
    loaded = plugin_inventory.cursor_baseline(query('-j','plugin','list'))
    if not indicator.liquid_available(env):raise RuntimeError('accepted glass backend is unavailable')
    if before_load is not None:before_load()
    # Recheck the runtime and inventory after the caller's last policy gate.
    current_version = json.loads(query('-j','version'))
    current_plugins = plugin_inventory.cursor_baseline(query('-j','plugin','list'))
    if current_version != version or current_plugins != loaded:
        raise RuntimeError('compositor ownership changed before cursor activation')
    answer = query('plugin','load',str(library)).strip()
    if answer != 'ok':raise RuntimeError('cursor backend first-load refused: '+answer[:200])
    plugin_inventory.assert_guard_added(loaded, query('-j','plugin','list'))
    import cursor_theme
    cursor_theme.check_guard(env)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library',type=Path)
    parser.add_argument('--abi',required=True)
    args = parser.parse_args(argv)
    try:
        import cu
        import cursor_session
        with cursor_session.owner_lock():
            activate(args.library,args.abi,cu.environment())
    except Exception as exc:
        print('activate-cursor-guard: '+str(exc),file=sys.stderr)
        return 1
    print('native cursor backend ready')
    return 0


if __name__ == '__main__':
    sys.exit(main())

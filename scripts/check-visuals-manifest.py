#!/usr/bin/env python3
"""Check that the visuals manifest pins the current local optics profile."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import sys


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'native/visuals.json')
    parser.add_argument('--profile', type=Path,
                        default=ROOT / 'native/hyprglass-local-optics.lua')
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(args.manifest.read_text())
    except FileNotFoundError:
        print(f'error: manifest not found: {args.manifest}', file=sys.stderr)
        return 2
    except OSError as exc:
        print(f'error: cannot read manifest {args.manifest}: {exc}', file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f'error: invalid JSON in manifest {args.manifest}: {exc}', file=sys.stderr)
        return 1

    if not isinstance(manifest, dict):
        print(f'error: invalid manifest in {args.manifest}: expected a JSON object',
              file=sys.stderr)
        return 1
    pinned = manifest.get('profile_sha256')
    if not isinstance(pinned, str) or not pinned.strip():
        print(f'error: manifest is missing or has empty profile_sha256: {args.manifest}',
              file=sys.stderr)
        return 1

    try:
        actual = _sha256(args.profile)
    except OSError as exc:
        print(f'error: cannot read optics profile {args.profile}: {exc}', file=sys.stderr)
        return 2

    print(f'Lua SHA256: {actual}')
    print(f'Pinned profile_sha256: {pinned}')
    if actual == pinned:
        print('OK: optics profile matches the visuals manifest')
        return 0

    library = manifest.get('library')
    library_arg = shlex.quote(library) if isinstance(library, str) else '<manifest library field value>'
    print('error: profile does not match the pinned optics source')
    print('Remediation:')
    print(f'  python3 scripts/refresh-visuals-manifest.py {library_arg}')
    print('  python3 scripts/check-visuals-manifest.py')
    print('  python3 scripts/sync-installed.py')
    print('  python3 scripts/sync-installed.py --check')
    print('  Only then commit.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())

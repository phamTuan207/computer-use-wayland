#!/usr/bin/env python3
"""Build the optional liquid-glass backend from a pinned Hyprglass source tree.

Separate from scripts/build.py on purpose: this is an opt-in backend with an exact
ABI requirement. It applies one supplied patch and builds in the source tree.
It never resets, cleans, stashes or deletes, and it never installs or loads anything.

Usage:
    python3 scripts/build-glass.py SOURCE
"""
import argparse
from pathlib import Path
import subprocess
import sys

REQUIRED_COMMIT = '84c1a5ab217101a317d4edaab7fba2efcc1bf346'
REQUIRED_HYPRLAND = '0.56.2'
VERSION = '0.10.0-cu.1'
PATCH = Path(__file__).resolve().parents[1] / 'native/hyprglass-capsule.patch'


def fail(message):
    print('build-glass: ' + message, file=sys.stderr)
    raise SystemExit(2)


def run(args, cwd=None, capture=True):
    return subprocess.run(args, cwd=cwd, capture_output=capture, text=True)


def output(args, cwd=None):
    done = run(args, cwd=cwd)
    if done.returncode != 0:
        fail('{} failed: {}'.format(' '.join(args), done.stderr.strip()))
    return done.stdout.strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('source', metavar='SOURCE',
                        help='Hyprglass git worktree pinned to ' + REQUIRED_COMMIT)
    parser.add_argument('--local-optics', action='store_true',
                        help='use upstream optical formula with pill-local geometry')
    args = parser.parse_args(argv)
    patch = PATCH.with_name('hyprglass-local-optics.patch') if args.local_optics else PATCH

    source = Path(args.source).resolve()
    if not source.is_dir():
        fail('SOURCE is not a directory: ' + str(source))
    toplevel = output(['git', '-C', str(source), 'rev-parse', '--show-toplevel'])
    if Path(toplevel).resolve() != source:
        fail('SOURCE must be the git toplevel itself, got ' + toplevel)
    head = output(['git', '-C', str(source), 'rev-parse', 'HEAD'])
    if head != REQUIRED_COMMIT:
        fail('HEAD is {}, need {}'.format(head, REQUIRED_COMMIT))

    installed = run(['pkg-config', '--modversion', 'hyprland'])
    if installed.returncode != 0 or installed.stdout.strip() != REQUIRED_HYPRLAND:
        fail('hyprland {} required, found {}'.format(REQUIRED_HYPRLAND,
                                                     installed.stdout.strip() or 'none'))

    if not patch.is_file():
        fail('patch not supplied: ' + str(patch))

    if run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=source).returncode == 0:
        print('capsule patch already applied')
    else:
        edits = output(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no'])
        if edits:
            fail('tracked edits present, refusing to apply:\n' + edits)
        if run(['git', 'apply', '--check', str(patch)], cwd=source).returncode != 0:
            fail('patch does not apply cleanly to ' + REQUIRED_COMMIT)
        applied = run(['git', 'apply', str(patch)], cwd=source)
        if applied.returncode != 0:
            fail('patch application failed: ' + applied.stderr.strip())
        print('capsule patch applied')

    build = run(['make', '-j2', '-B', 'HYPRGLASS_VERSION=' + VERSION], cwd=source, capture=False)
    if build.returncode != 0:
        fail('make failed')
    print('SOURCE: ' + str(source))
    print('hyprglass.so: ' + str(source / 'hyprglass.so'))
    print('not installed and not loaded; wire it up manually after acceptance')
    return 0


if __name__ == '__main__':
    sys.exit(main())

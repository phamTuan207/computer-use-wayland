#!/usr/bin/env python3
"""Build the optional liquid-glass backend from a pinned Hyprglass source tree.

Separate from scripts/build.py on purpose: this is an opt-in backend with an exact
ABI requirement. It applies one supplied patch and builds in the source tree.
It never resets, cleans, stashes or deletes, and it never installs or loads anything.

Usage:
    python3 scripts/build-glass.py SOURCE --local-optics [--allow-dirty]
"""
import argparse
from pathlib import Path
import subprocess
import sys

REQUIRED_COMMIT = '03a57c4451b4abee38feda2ffb725f55ecc0f2fd'
REQUIRED_HYPRLAND = '0.57.2'
VERSION = '1.1.1-cu.1'
PATCH = Path(__file__).resolve().parents[1] / 'native/hyprglass-local-optics.patch'


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
    parser.add_argument('--local-optics', action='store_true', required=True,
                        help='required; build the accepted upstream local-optics profile')
    parser.add_argument('--allow-dirty', action='store_true',
                        help='allow pre-existing tracked or untracked source changes')
    args = parser.parse_args(argv)

    source = Path(args.source).resolve()
    if not source.is_dir():
        fail('SOURCE is not a directory: ' + str(source))
    toplevel = output(['git', '-C', str(source), 'rev-parse', '--show-toplevel'])
    if Path(toplevel).resolve() != source:
        fail('SOURCE must be the git toplevel itself, got ' + toplevel)
    head = output(['git', '-C', str(source), 'rev-parse', 'HEAD'])
    if head != REQUIRED_COMMIT:
        fail('HEAD is {}, need {}'.format(head, REQUIRED_COMMIT))
    edits = output(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=all'])
    print('build-glass: commit={} initial_dirty={} allow_dirty={}'.format(
        head, bool(edits), args.allow_dirty), flush=True)
    if edits and not args.allow_dirty:
        fail('SOURCE is dirty; use --allow-dirty to build intentionally:\n' + edits)

    installed = run(['pkg-config', '--modversion', 'hyprland'])
    if installed.returncode != 0 or installed.stdout.strip() != REQUIRED_HYPRLAND:
        fail('hyprland {} required, found {}'.format(REQUIRED_HYPRLAND,
                                                     installed.stdout.strip() or 'none'))

    if not PATCH.is_file():
        fail('patch not supplied: ' + str(PATCH))

    if run(['git', 'apply', '--reverse', '--check', str(PATCH)], cwd=source).returncode == 0:
        print('local-optics patch already applied')
    else:
        if run(['git', 'apply', '--check', str(PATCH)], cwd=source).returncode != 0:
            fail('patch does not apply cleanly to ' + REQUIRED_COMMIT)
        applied = run(['git', 'apply', str(PATCH)], cwd=source)
        if applied.returncode != 0:
            fail('patch application failed: ' + applied.stderr.strip())
        print('local-optics patch applied')

    # Applying our patch dirties a clean checkout; only initial dirt needs opt-in.
    build_edits = output(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=all'])
    print('build-glass: commit={} build_dirty={}'.format(head, bool(build_edits)), flush=True)
    build = run(['make', '-j2', '-B', 'HYPRGLASS_VERSION=' + VERSION], cwd=source, capture=False)
    if build.returncode != 0:
        fail('make failed')
    print('SOURCE: ' + str(source))
    print('hyprglass.so: ' + str(source / 'hyprglass.so'))
    print('not installed and not loaded; wire it up manually after acceptance')
    return 0


if __name__ == '__main__':
    sys.exit(main())

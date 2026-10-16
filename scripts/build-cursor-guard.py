#!/usr/bin/env python3
"""Build the session-owned cursor-guard backend from the pinned Hyprland headers.

Compiles native/cursor-guard.cpp only. It never installs or loads anything:
setup installs the immutable library, and only a fresh login activates it.

Usage:
    python3 scripts/build-cursor-guard.py
"""
import argparse
import hashlib
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'native/cursor-guard.cpp'
OUTPUT = ROOT / 'native/cursor-guard.so'
REQUIRED_HYPRLAND = '0.56.2'
PINNED_COMMIT = 'efb50993780079460b0cbed1363e2166a2de1d9f'


def fail(message):
    print('build-cursor-guard: ' + message, file=sys.stderr)
    raise SystemExit(2)


def run(args, env, cwd=None):
    return subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, timeout=900)


def output(args, env):
    done = run(args, env)
    if done.returncode != 0:
        fail('{} failed: {}'.format(' '.join(args), (done.stderr or done.stdout).strip()))
    return done.stdout.strip()


def build(env=None):
    """Compile the guard library against the pinned headers; return its path."""
    env = dict(os.environ) if env is None else env
    if not SOURCE.is_file():
        fail('source missing: ' + str(SOURCE))
    version = output(['pkg-config', '--modversion', 'hyprland'], env)
    if version != REQUIRED_HYPRLAND:
        fail('hyprland {} required, found {}'.format(REQUIRED_HYPRLAND, version or 'none'))
    import setup
    abi = setup.header_abi(env)
    if not abi.startswith(PINNED_COMMIT+'_'):
        fail('headers are not the pinned commit ' + PINNED_COMMIT)
    cflags = shlex.split(output(['pkg-config', '--cflags', 'hyprland', 'libeis-1.0'], env))
    if OUTPUT.is_symlink() or (OUTPUT.exists() and not OUTPUT.is_file()):
        fail('output must be a regular file')
    # Compile a fresh inode; even an accidentally loaded build output survives.
    with tempfile.TemporaryDirectory(dir=OUTPUT.parent, prefix='.cursor-build-') as folder:
        built = Path(folder)/'cursor-guard.so'
        argv = ['g++', '-std=c++26', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra',
                *cflags, '-o', str(built), str(SOURCE), '-lXcursor']
        compiled = run(argv, env)
        if compiled.returncode != 0:
            fail('compile failed: ' + (compiled.stderr or compiled.stdout).strip())
        os.replace(built, OUTPUT)
    return OUTPUT


def install(library, directory):
    """Publish an immutable hash-named copy; a loaded inode is never truncated."""
    data = Path(library).read_bytes()
    if not data.startswith(b'\x7fELF'):
        raise ValueError('source is not an ELF library')
    digest = hashlib.sha256(data).hexdigest()
    directory = Path(directory).resolve(strict=True)
    target = directory / ('cursor-guard-' + digest + '.so')
    if target.exists() or target.is_symlink():
        if target.is_symlink() or target.read_bytes() != data:
            raise ValueError('existing hash path differs; refusing overwrite')
        return target
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.guard-', delete=False) as file:
            temporary = Path(file.name)
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        # Atomic no-replace publication. A loaded inode must never be truncated.
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.is_symlink() or target.read_bytes() != data:
                raise ValueError('concurrent hash path differs; refusing overwrite')
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    print(build())
    print('not installed and not loaded; setup publishes it, a fresh login activates it')
    return 0


if __name__ == '__main__':
    sys.exit(main())

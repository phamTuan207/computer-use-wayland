#!/usr/bin/env python3
"""Build a new XCursor theme from the vector asset; never replace an existing theme."""
import argparse
import ctypes
import errno
import hashlib
import io
import os
from pathlib import Path
import struct
import subprocess
import tempfile
from PIL import Image

AT_FDCWD = -100
RENAME_NOREPLACE = 1


def build(directory):
    directory = Path(directory)
    if directory.exists():
        raise ValueError('theme directory already exists; refusing overwrite')
    svg = Path(__file__).resolve().parents[1] / 'native/agent-cursor.svg'
    chunks = []
    for size in (24, 32, 34, 48, 64):
        raw = subprocess.check_output(['rsvg-convert', '-w', str(size), '-h', str(size), str(svg)])
        image = Image.open(io.BytesIO(raw)).convert('RGBA')
        rgba = image.tobytes()
        pixels = [((a << 24) | ((r*a//255) << 16) | ((g*a//255) << 8) | (b*a//255))
                  for r,g,b,a in zip(rgba[0::4],rgba[1::4],rgba[2::4],rgba[3::4])]
        hotspot = round(size*18/64)
        chunks.append((size, struct.pack('<9I',36,0xfffd0002,size,1,size,size,hotspot,hotspot,0)
                       + struct.pack('<' + str(len(pixels)) + 'I', *pixels)))
    offset = 16 + len(chunks)*12
    toc = bytearray()
    for size, chunk in chunks:
        toc.extend(struct.pack('<3I',0xfffd0002,size,offset));offset += len(chunk)
    data = struct.pack('<4I',0x72756358,16,0x10000,len(chunks)) + toc + b''.join(c for _,c in chunks)
    cursors = directory / 'cursors'
    cursors.mkdir(parents=True)
    (cursors / 'left_ptr').write_bytes(data)
    aliases = {'default','arrow','text','pointer','hand1','hand2','watch','wait','crosshair','move','xterm'}
    reference = Path('/usr/share/icons/Adwaita/cursors')
    if reference.is_dir():aliases.update(p.name for p in reference.iterdir())
    for alias in sorted(aliases - {'left_ptr'}):
        (cursors / alias).symlink_to('left_ptr')
    (directory / 'index.theme').write_text('[Icon Theme]\nName=Computer Use Agent\nInherits=Adwaita\n')
    return directory


def tree_digest(root):
    """SHA256 over sorted relative paths, file bytes and symlink targets.

    No absolute path or mtime enters it, so the same sources and the same alias set
    always give the same name. Not guaranteed identical across every machine: the
    alias list follows the Adwaita reference directory when it exists, so a host
    without it produces a different, still-correct tree.
    """
    root = Path(root)
    digest = hashlib.sha256()
    # A symlink must be inspected before is_dir(): a symlink pointing at a directory
    # would otherwise be skipped, and a directory symlink changes the tree.
    for path in sorted(p for p in root.rglob('*') if not (p.is_dir() and not p.is_symlink())):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(relative + b'\0')
        if path.is_symlink():
            digest.update(b'L' + os.readlink(path).encode() + b'\0')
        elif path.is_file():
            digest.update(b'F' + hashlib.sha256(path.read_bytes()).digest())
        else:
            raise ValueError(f'unexpected tree entry, not a file or symlink: {path.name}')
    return digest.hexdigest()


def publish(source, target):
    """Atomically move a finished tree into place without ever replacing anything."""
    target = Path(target)
    if target.is_symlink():
        raise ValueError('refusing to publish onto a symlink')
    # No os.rename fallback: it would replace. A kernel without renameat2 fails closed.
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        rename = libc.renameat2
    except AttributeError as exc:
        raise OSError(errno.ENOSYS, 'atomic cursor installation requires renameat2') from exc
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p,
                               ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    result = rename(AT_FDCWD, os.fsencode(str(source)),
                            AT_FDCWD, os.fsencode(str(target)), RENAME_NOREPLACE)
    if result == 0:
        return target
    error = ctypes.get_errno()
    if error not in (errno.EEXIST, errno.ENOTEMPTY):
        raise OSError(error, os.strerror(error))
    # Re-check the destination now, not before the syscall: it may have been swapped
    # for a symlink or removed between the call and this moment.
    if target.is_symlink():
        raise ValueError('refusing to publish onto a symlink')
    if not target.is_dir():
        raise FileExistsError(f'target vanished or is not a directory: {target.name}')
    if tree_digest(target) == tree_digest(source):
        return target
    raise ValueError('a different theme already exists at this hash path')


def install(icon_directory):
    """Build into a temporary directory and publish one immutable hashed theme."""
    icon_directory = Path(icon_directory)
    icon_directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cu-agent-build-', dir=icon_directory) as folder:
        staged = build(Path(folder) / 'theme')
        name = 'cu-agent-' + tree_digest(staged)
        target = icon_directory / name
        if target.exists() or target.is_symlink():
            if target.is_symlink() or not target.is_dir() or tree_digest(target) != tree_digest(staged):
                raise ValueError('refusing to touch an existing theme at this hash path')
            return target, True
        # Publish straight from the completed candidate: renameat2(RENAME_NOREPLACE)
        # is already atomic, and the TemporaryDirectory owns any leftover.
        publish(staged, target)
    return target, False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, nargs='?')
    default_icons = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'icons'
    parser.add_argument('--install', type=Path, nargs='?', const=default_icons,
                        metavar='ICON_DIR',
                        help='publish an immutable hashed theme; default: the user icon directory')
    arguments = parser.parse_args()
    if arguments.install:
        if arguments.directory:
            parser.error('give either a directory or --install')
        path, existed = install(arguments.install)
        print(path)
    else:
        if not arguments.directory:
            parser.error('a directory is required unless --install is given')
        print(build(arguments.directory))

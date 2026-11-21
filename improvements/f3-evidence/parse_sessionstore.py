#!/usr/bin/env python3
"""Parse a Firefox/Zen mozLz4 sessionstore file and list all tabs.

mozLz4 = 8-byte magic b'mozLz40\\x00' + one raw LZ4 block. Decompressed
via liblz4 through ctypes (no lz4 python module needed).
Usage: parse_sessionstore.py <path>
Prints: window count, tab count, and per tab: index, url, title, hidden/discarded flags.
"""
import ctypes
import json
import sys

MAGIC = b"mozLz40\x00"
# mozLz4 = 8-byte magic + uint32 LE decompressed size + one raw LZ4 block.


def decompress(path):
    raw = open(path, "rb").read()
    if not raw.startswith(MAGIC):
        raise SystemExit("not a mozLz4 file: %s" % path)
    import struct
    size = struct.unpack("<I", raw[8:12])[0]
    block = raw[12:]
    lib = ctypes.CDLL("liblz4.so.1")
    lib.LZ4_decompress_safe.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    lib.LZ4_decompress_safe.restype = ctypes.c_int
    out = ctypes.create_string_buffer(size)
    n = lib.LZ4_decompress_safe(block, out, len(block), size)
    if n < 0:
        raise SystemExit("LZ4_decompress_safe failed: %d" % n)
    return out.raw[:n]


def main():
    path = sys.argv[1]
    data = json.loads(decompress(path))
    windows = data.get("windows", [])
    print("file: %s" % path)
    print("windows: %d" % len(windows))
    total = 0
    for wi, w in enumerate(windows):
        tabs = w.get("tabs", [])
        print("window %d: %d tabs, selected=%s" % (
            wi, len(tabs), w.get("selected")))
        for ti, t in enumerate(tabs):
            entries = t.get("entries", [])
            cur = entries[t.get("index", 1) - 1] if entries else {}
            print("  w%dt%-3d url=%s | title=%s | hidden=%s" % (
                wi, ti, cur.get("url", "?")[:100],
                (cur.get("title") or "")[:50],
                t.get("hidden", False)))
            total += 1
    print("total tabs: %d" % total)
    closed = data.get("closedTabs", [])
    print("closedTabs (undo list): %d" % len(closed))


if __name__ == "__main__":
    main()

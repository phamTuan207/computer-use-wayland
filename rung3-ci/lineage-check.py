#!/usr/bin/env python3
"""Lineage check: named fix commits must be present on this branch.

Bottleneck study M16 (improvements/bottleneck-study-20261127.md):
the tc02 tesseract fix was on main but NOT on todolist-push, so
the defect stayed live on the branch the runs use. This check
fails when a manifest fix is missing from HEAD.

Cherry-picks rewrite hashes, so presence is checked by content:
each manifest line is <commit> <file> <marker-substring>; the
check passes when the marker exists in the file at HEAD (working
tree). The commit column is provenance, not the test.

Usage: python3 lineage-check.py [manifest]  (default:
rung3-ci/lineage-manifest.txt next to this script)
Exit 1 on any missing fix.
"""
import os
import sys


def load_manifest(path):
    entries = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 2)
            if len(parts) != 3:
                raise ValueError(f"bad manifest line: {line!r}")
            entries.append(tuple(parts))
    return entries


def check(entries, root=None):
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missing = []
    for commit, rel, marker in entries:
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                present = marker in fh.read()
        except OSError:
            present = False
        if not present:
            missing.append((commit, rel, marker))
    return missing


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    manifest = argv[0] if argv else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "lineage-manifest.txt")
    entries = load_manifest(manifest)
    missing = check(entries)
    for commit, rel, marker in missing:
        print(f"LINEAGE MISSING: fix {commit} not present in {rel} "
              f"(marker: {marker!r})")
    if missing:
        return 1
    print(f"lineage ok: {len(entries)} fix(es) present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

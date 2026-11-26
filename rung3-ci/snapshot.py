#!/usr/bin/env python3
"""Rung 3 scoring snapshot tool.

Copies an evidence folder to a snapshot directory with a manifest
and sha256 per file, for the scorer handoff (grading decision
section 3). The scorer receives only the snapshot path and never
touches the live evidence directory.

Usage:
  python3 rung3-ci/snapshot.py <EVIDENCE-DIR> [--snapshot-root DIR]
      [--label STR]
Snapshot directory: <root>/<TASK-ID>-<YYYYMMDD-HHMMSS>[-<label>]/.
The copy is verified: every copied file hash must match the source
hash, else the snapshot is removed and the command fails.
manifest.json in the snapshot lists source dir, files with sha256,
size and mtime, and the manifest sha256. The copy is recursive
(R9): files in subdirectories are copied under their relative
path, so evidence with a subdir (DP-02 dp02-code/) seals whole.
The source manifest.json written by collect-evidence.py is NOT
copied (R9): the snapshot writes its own manifest, and copying the
collect manifest would seal a stale self-hash.
Times are Asia/Ho_Chi_Minh wall clock.
No personal info in this file.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_dir")
    ap.add_argument("--snapshot-root", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--name", default=None,
                    help="fixed snapshot dir name, overrides the "
                    "timestamped name (use R3-xxx-L3 for R3-L3)")
    args = ap.parse_args()
    src = os.path.abspath(args.evidence_dir)
    if not os.path.isdir(src):
        print("FAIL: evidence folder missing: %s" % src)
        return 1
    task = os.path.basename(src.rstrip("/"))
    tz = datetime.timezone(datetime.timedelta(hours=7))
    stamp = datetime.datetime.now(tz).strftime("%Y%m%d-%H%M%S")
    if args.name:
        name = args.name
    else:
        name = "%s-%s" % (task, stamp)
        if args.label:
            name += "-%s" % args.label
    root = args.snapshot_root or os.path.expanduser("~/rung3-snapshots")
    dest = os.path.join(root, name)
    if os.path.exists(dest):
        print("FAIL: snapshot dir already exists: %s" % dest)
        return 1
    names = []
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames.sort()
        for n in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, n), src)
            if rel == "manifest.json":
                continue
            names.append(rel)
    names.sort()
    manifest = {"task": task, "source_dir": src, "snapshot_dir": dest,
                "files": []}
    try:
        os.makedirs(dest)
        for n in names:
            target = os.path.join(dest, n)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(os.path.join(src, n), target)
        for n in names:
            s_hash = sha256_file(os.path.join(src, n))
            d_hash = sha256_file(os.path.join(dest, n))
            if s_hash != d_hash:
                raise IOError("hash mismatch after copy: %s" % n)
            st = os.stat(os.path.join(dest, n))
            manifest["files"].append({
                "name": n, "sha256": d_hash, "size": st.st_size,
                "mtime": int(st.st_mtime)})
    except (OSError, IOError) as e:
        shutil.rmtree(dest, ignore_errors=True)
        print("FAIL: snapshot failed, removed partial dir: %s" % e)
        return 1
    blob = json.dumps(manifest, sort_keys=True).encode("utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(blob).hexdigest()
    with open(os.path.join(dest, "manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print("SNAPSHOT: %s" % dest)
    print("FILES: %d, manifest sha256 %s"
          % (len(manifest["files"]), manifest["manifest_sha256"]))
    for entry in manifest["files"]:
        print("  %s %s" % (entry["sha256"][:12], entry["name"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

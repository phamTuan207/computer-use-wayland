#!/usr/bin/env python3
"""R3-L3 manifest gate (Decision B, decoupled scoring).

Verifies a sealed snapshot directory before the coordinator resets the
task and the runner proceeds to the next task. The gate is the only
thing that stands between the runner and the reset for Class S tasks.
If the gate fails, the runner does NOT proceed and NO reset happens.

Checks:
  1. Snapshot dir exists and has manifest.json or manifest.sha256.
  2. manifest.json parses and its manifest_sha256 matches its content.
  3. Every file listed in the manifest exists with a matching sha256.
  4. Pre-reset content check: every file the evidence requirements name
     for this task (rung3-ci/evidence-requirements.json) is present, every
     glob pattern meets its minimum count, and the screenshot count meets
     screenshots_min. This is the check that catches a snapshot missing a
     file the key's "Vat chung cham" line names.
  5. File mtimes are inside the run window (--window-start/--window-end,
     ISO 8601). If no window is given, mtimes must be within the last
     24 hours.

Usage:
  python3 rung3-ci/manifest-gate.py --snapshot <dir> --task <ID>
      [--requirements rung3-ci/evidence-requirements.json]
      [--window-start ISO] [--window-end ISO]

Output: one line PASS or FAIL plus reasons, exit 0 for PASS, 1 for FAIL.
No human judgment inside this script. A human scorer still confirms
the required evidence files exist and screenshots are legible.
No personal info in this file.
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_iso(s):
    return datetime.datetime.fromisoformat(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--requirements",
                    default="rung3-ci/evidence-requirements.json")
    ap.add_argument("--window-start", default=None)
    ap.add_argument("--window-end", default=None)
    args = ap.parse_args()
    reasons = []
    snap = os.path.abspath(args.snapshot)
    if not os.path.isdir(snap):
        print("FAIL: snapshot dir missing: %s" % snap)
        return 1
    mpath = os.path.join(snap, "manifest.json")
    spath = os.path.join(snap, "manifest.sha256")
    if os.path.isfile(mpath):
        try:
            with open(mpath, encoding="utf-8") as f:
                manifest = json.load(f)
        except (ValueError, OSError) as e:
            print("FAIL: manifest.json unreadable: %s" % e)
            return 1
        stored = manifest.get("manifest_sha256")
        if stored:
            copy = dict(manifest)
            copy.pop("manifest_sha256", None)
            blob = json.dumps(copy, sort_keys=True).encode("utf-8")
            if hashlib.sha256(blob).hexdigest() != stored:
                reasons.append("manifest_sha256 mismatch")
        files = manifest.get("files", [])
    elif os.path.isfile(spath):
        files = []
        try:
            with open(spath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(None, 1)
                    if len(parts) != 2:
                        reasons.append("bad manifest.sha256 line: %s" % line)
                        continue
                    files.append({"name": parts[1].lstrip("*"),
                                  "sha256": parts[0]})
        except OSError as e:
            print("FAIL: manifest.sha256 unreadable: %s" % e)
            return 1
    else:
        print("FAIL: no manifest.json or manifest.sha256 in %s" % snap)
        return 1
    if not files:
        reasons.append("manifest lists no files")
    names = set()
    for entry in files:
        name = entry.get("name")
        want = entry.get("sha256")
        if not name or not want:
            reasons.append("manifest entry missing name or sha256")
            continue
        names.add(name)
        path = os.path.join(snap, name)
        if not os.path.isfile(path):
            reasons.append("manifest file missing: %s" % name)
            continue
        got = sha256_file(path)
        if got != want:
            reasons.append("sha256 mismatch: %s" % name)
    req = {}
    try:
        with open(args.requirements, encoding="utf-8") as f:
            req = json.load(f)
    except (ValueError, OSError) as e:
        reasons.append("requirements file unreadable: %s" % e)
    spec = req.get(args.task, {}) if isinstance(req, dict) else {}
    for name in spec.get("files", []):
        if name not in names and not os.path.isfile(os.path.join(snap, name)):
            reasons.append("required file missing: %s" % name)
    for pat in spec.get("patterns", []):
        glob = pat.get("glob", "")
        minimum = pat.get("min", 0)
        hits = [n for n in names if fnmatch.fnmatch(n, glob)]
        hits += [n for n in os.listdir(snap)
                 if fnmatch.fnmatch(n, glob) and n not in names]
        if len(set(hits)) < minimum:
            reasons.append("pattern %s needs %d, found %d"
                           % (glob, minimum, len(set(hits))))
    smin = spec.get("screenshots_min", 0)
    if smin:
        shots = [n for n in os.listdir(snap)
                 if n.lower().endswith((".png", ".jpg", ".jpeg"))]
        if len(shots) < smin:
            reasons.append("screenshots need %d, found %d"
                           % (smin, len(shots)))
    if args.window_start or args.window_end:
        try:
            start = parse_iso(args.window_start) if args.window_start else None
            end = parse_iso(args.window_end) if args.window_end else None
        except ValueError as e:
            reasons.append("bad window timestamp: %s" % e)
            start = end = None
        if start is not None or end is not None:
            for name in names:
                path = os.path.join(snap, name)
                if not os.path.isfile(path):
                    continue
                mt = datetime.datetime.fromtimestamp(
                    os.stat(path).st_mtime,
                    tz=datetime.timezone.utc)
                if start is not None and mt < start:
                    reasons.append("mtime before window: %s" % name)
                if end is not None and mt > end:
                    reasons.append("mtime after window: %s" % name)
    else:
        now = datetime.datetime.now(datetime.timezone.utc)
        for name in names:
            path = os.path.join(snap, name)
            if not os.path.isfile(path):
                continue
            age = now - datetime.datetime.fromtimestamp(
                os.stat(path).st_mtime, tz=datetime.timezone.utc)
            if age > datetime.timedelta(hours=24):
                reasons.append("mtime older than 24h: %s" % name)
    if reasons:
        print("FAIL: %s" % "; ".join(reasons))
        return 1
    print("PASS: %s snapshot %s (%d files, requirements met)"
          % (args.task, snap, len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

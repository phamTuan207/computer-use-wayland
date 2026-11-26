#!/usr/bin/env python3
"""Rung 3 evidence collection script.

After each task, verifies the evidence folder has the required files
(timestamped screenshots plus ket-qua.txt / bao-cao.txt / other named
files where the task requires them), writes manifest.json with sha256
per file, and fails loudly on missing evidence.

Usage:
  python3 rung3-ci/collect-evidence.py <TASK-ID>
      [--evidence-root DIR] [--requirements FILE] [--write-manifest]

  TASK-ID is like R3-007 or DP-02. Default evidence root is
  ~/rung3-chung-cu. With --write-manifest (default on), manifest.json
  is written into the evidence folder. Exit 0 only when every
  required file is present; otherwise exit 1 and print MISSING lines.

A timestamped screenshot is a .png/.jpg file whose name contains
YYYYMMDD-HHMMSS (YYYYMMDD-HHMM also accepted: both timestamp
precisions appear in real evidence names, R9). manifest.json lists
every file in the folder with sha256, size, and mtime, plus the
check result; the manifest never lists or hashes itself. Identical
non-empty file content under two different names is flagged as a
duplicate and fails the collect (R9: a copied screenshot under a
new name is the cheapest fabrication shape). Files in
subdirectories are listed by path relative to the evidence folder,
so a pattern such as dp02-code/dp02-*.txt matches the files under
dp02-code/.
For DP-02, before checking, any of the 12 fixture files missing
from dp02-code/ is copied there from the fixture source
(~/rung3/dp02-code by default, --fixture-source to override).
No personal info in this file.
"""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys

TS_RE = re.compile(r"\d{8}-\d{6}|\d{8}-\d{4}(?!\d)")
IMG_EXT = (".png", ".jpg", ".jpeg")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--evidence-root", default=None)
    ap.add_argument("--requirements", default=None)
    ap.add_argument("--fixture-source", default=None)
    ap.add_argument("--no-manifest", action="store_true")
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req_path = args.requirements or os.path.join(
        root, "rung3-ci", "evidence-requirements.json")
    ev_root = args.evidence_root or os.path.expanduser("~/rung3-chung-cu")
    ev_dir = os.path.join(ev_root, args.task)

    reqs = json.load(open(req_path, encoding="utf-8"))
    if args.task not in reqs:
        print("FAIL: unknown task %s (not in evidence-requirements.json)"
              % args.task)
        return 1
    req = reqs[args.task]

    missing = []
    if not os.path.isdir(ev_dir):
        print("FAIL: evidence folder missing: %s" % ev_dir)
        return 1
    if args.task == "DP-02":
        src = args.fixture_source or os.path.expanduser(
            "~/rung3/dp02-code")
        dest_dir = os.path.join(ev_dir, "dp02-code")
        if os.path.isdir(src):
            os.makedirs(dest_dir, exist_ok=True)
            for n in range(1, 13):
                name = "dp02-%02d.txt" % n
                dest = os.path.join(dest_dir, name)
                if not os.path.isfile(dest):
                    shutil.copy2(os.path.join(src, name), dest)
                    print("COPIED: dp02-code/%s" % name)
    rel_files = []
    for dirpath, dirnames, filenames in os.walk(ev_dir):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel_files.append(os.path.relpath(full, ev_dir))
    rel_files.sort()
    names = [os.path.basename(p) for p in rel_files]
    files = rel_files
    for want in req.get("files", []):
        if want not in files and want not in names:
            missing.append("missing file: %s" % want)
    for pat in req.get("patterns", []):
        glob = pat["glob"]
        if "/" in glob:
            hits = [p for p in files if fnmatch.fnmatch(p, glob)]
        else:
            hits = [p for p in files
                    if fnmatch.fnmatch(os.path.basename(p), glob)]
        if len(hits) < pat["min"]:
            missing.append("pattern %s: found %d, need %d (%s)"
                           % (glob, len(hits), pat["min"],
                              ", ".join(hits) or "none"))
    shots = [p for p in files
             if p.lower().endswith(IMG_EXT)
             and TS_RE.search(os.path.basename(p))]
    need_shots = req.get("screenshots_min", 0)
    if len(shots) < need_shots:
        missing.append("timestamped screenshots: found %d, need %d"
                       % (len(shots), need_shots))

    entries = []
    for name in files:
        if name == "manifest.json":
            continue
        path = os.path.join(ev_dir, name)
        st = os.stat(path)
        entries.append({
            "name": name,
            "sha256": sha256_file(path),
            "size": st.st_size,
            "mtime": int(st.st_mtime),
        })
    entries.sort(key=lambda e: e["name"])
    # R9 duplicate detection: identical non-empty content under two
    # different names fails the collect. Zero-byte files are exempt:
    # they share a hash by construction and carry no evidence.
    by_hash = {}
    for entry in entries:
        if entry["size"] > 0:
            by_hash.setdefault(entry["sha256"], []).append(entry["name"])
    duplicates = [sorted(names) for names in by_hash.values()
                  if len(names) > 1]
    duplicates.sort()
    for group in duplicates:
        missing.append("duplicate file content: %s"
                       % " == ".join(group))
    manifest = {
        "task": args.task,
        "evidence_dir": ev_dir,
        "requirements": req,
        "files": entries,
        "duplicates": duplicates,
        "missing": missing,
        "status": "PASS" if not missing else "FAIL",
    }
    blob = json.dumps(manifest, sort_keys=True).encode("utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(blob).hexdigest()

    if not args.no_manifest:
        with open(os.path.join(ev_dir, "manifest.json"), "w",
                  encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, sort_keys=True,
                      ensure_ascii=False)
            f.write("\n")

    if missing:
        for line in missing:
            print("MISSING: %s" % line)
        print("FAIL: evidence for %s incomplete (%d file(s) in folder)"
              % (args.task, len(files)))
        return 1
    print("PASS: evidence for %s complete: %d file(s), %d screenshot(s), "
          "manifest sha256 %s"
          % (args.task, len(manifest["files"]), len(shots),
             manifest["manifest_sha256"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

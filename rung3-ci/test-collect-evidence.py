#!/usr/bin/env python3
"""Sealed-fixture tests for collect-evidence.py + snapshot.py (R9).

Temp evidence dirs only; asserts the R9 mechanical checks:
  (a) duplicate file content under two names -> collect FAILs and
      names both files (a copied screenshot under a new name)
  (b) missing required screenshot -> collect FAILs (rejection)
  (c) HHMM-precision screenshot name -> accepted (both timestamp
      precisions pass; control case PASSes end to end)
  (d) subdirectory evidence -> collect lists it by relative path
      and snapshot copies it recursively (DP-02 shape)
  (e) manifest never lists/hashes itself, and snapshot does not
      copy the collect manifest (no stale self-hash sealed)
Run: python3 rung3-ci/test-collect-evidence.py
No personal info in this file.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
COLLECT = os.path.join(HERE, "collect-evidence.py")
SNAPSHOT = os.path.join(HERE, "snapshot.py")

REQS = {
    "T-OK": {"files": ["ket-qua.txt"], "patterns": [],
             "screenshots_min": 1},
    "T-SUB": {"files": ["bao-cao.txt"],
              "patterns": [{"glob": "sub/code-*.txt", "min": 2}],
              "screenshots_min": 0},
}


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def collect(root, req_path, task):
    out = subprocess.run(
        [sys.executable, COLLECT, task, "--evidence-root", root,
         "--requirements", req_path],
        capture_output=True, text=True)
    return out


def snapshot(ev_dir, snap_root, name):
    out = subprocess.run(
        [sys.executable, SNAPSHOT, ev_dir, "--snapshot-root", snap_root,
         "--name", name],
        capture_output=True, text=True)
    return out


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    assert cond, name + " " + detail


def main():
    with tempfile.TemporaryDirectory() as tmp:
        req_path = os.path.join(tmp, "reqs.json")
        with open(req_path, "w", encoding="utf-8") as fh:
            json.dump(REQS, fh)
        ev_root = os.path.join(tmp, "evidence")

        # (c) control: HHMM screenshot name accepted, clean PASS.
        d = os.path.join(ev_root, "T-OK")
        write(os.path.join(d, "ket-qua.txt"), b"result\n")
        write(os.path.join(d, "shot-20261127-0415.png"), b"PNGDATA-1")
        out = collect(ev_root, req_path, "T-OK")
        check("c HHMM screenshot accepted", out.returncode == 0,
              out.stdout + out.stderr)
        manifest = json.load(open(os.path.join(d, "manifest.json"),
                                  encoding="utf-8"))
        check("e manifest excludes itself",
              all(e["name"] != "manifest.json"
                  for e in manifest["files"]),
              json.dumps(manifest["files"]))
        check("c no duplicates on clean evidence",
              manifest["duplicates"] == [])

        # (a) duplicate content under two names -> FAIL, both named.
        write(os.path.join(d, "shot-20261127-041500.png"), b"PNGDATA-1")
        out = collect(ev_root, req_path, "T-OK")
        check("a duplicate content fails collect",
              out.returncode == 1, out.stdout)
        check("a duplicate names both files",
              "duplicate file content" in out.stdout
              and "shot-20261127-0415.png" in out.stdout
              and "shot-20261127-041500.png" in out.stdout,
              out.stdout)
        manifest = json.load(open(os.path.join(d, "manifest.json"),
                                  encoding="utf-8"))
        check("a manifest records the duplicate group",
              len(manifest["duplicates"]) == 1
              and len(manifest["duplicates"][0]) == 2)
        os.remove(os.path.join(d, "shot-20261127-041500.png"))

        # (b) missing required screenshot -> FAIL.
        os.remove(os.path.join(d, "shot-20261127-0415.png"))
        out = collect(ev_root, req_path, "T-OK")
        check("b missing screenshot rejected",
              out.returncode == 1
              and "timestamped screenshots" in out.stdout,
              out.stdout)

        # (d)+(e) subdir evidence: collect by rel path, snapshot
        # recursive, collect manifest not copied into the snapshot.
        d2 = os.path.join(ev_root, "T-SUB")
        write(os.path.join(d2, "bao-cao.txt"), b"report\n")
        write(os.path.join(d2, "sub", "code-01.txt"), b"one\n")
        write(os.path.join(d2, "sub", "code-02.txt"), b"two\n")
        out = collect(ev_root, req_path, "T-SUB")
        check("d subdir pattern collected", out.returncode == 0,
              out.stdout + out.stderr)
        manifest = json.load(open(os.path.join(d2, "manifest.json"),
                                  encoding="utf-8"))
        names = [e["name"] for e in manifest["files"]]
        check("d manifest lists subdir rel paths",
              "sub/code-01.txt" in names and "sub/code-02.txt" in names,
              str(names))
        snap_root = os.path.join(tmp, "snapshots")
        out = snapshot(d2, snap_root, "T-SUB-seal")
        check("d snapshot runs", out.returncode == 0,
              out.stdout + out.stderr)
        sealed = os.path.join(snap_root, "T-SUB-seal")
        check("d snapshot copies subdir recursively",
              os.path.isfile(os.path.join(sealed, "sub", "code-01.txt"))
              and os.path.isfile(os.path.join(sealed, "sub",
                                              "code-02.txt")))
        snap_manifest = json.load(open(os.path.join(sealed,
                                                    "manifest.json"),
                                       encoding="utf-8"))
        snap_names = [e["name"] for e in snap_manifest["files"]]
        check("e snapshot seals subdir files, not collect manifest",
              "sub/code-01.txt" in snap_names
              and "manifest.json" not in snap_names,
              str(snap_names))
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

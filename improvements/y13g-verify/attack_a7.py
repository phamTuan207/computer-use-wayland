#!/usr/bin/env python3
"""A7 symlink set (Y13g re-verification, rebuilt from the redteam
paper spec). Five shapes, each on a FRESH staged ship, refused at
BOTH layers:

  Layer 1 (module-top scan): direct `python3 -P run_codex_y5.py
    --verify-manifest` must refuse rc 2 with
    {"refused": true, "kind": "symlink", ...} (the corrected
    label, not "pyc_refused").
  Layer 2 (_verify_manifest): a STRIPPED copy of the runner (the
    `_refuse_tampered_ship()` call removed, staged manifest
    re-pointed at the stripped runner bytes so its md5 still
    matches) must refuse rc 2 with a symlink mismatch.

Shapes:
  1  symlinked fixtures dir (correct content outside)
  2  symlinked manifest file (correct content outside)
  3  symlinked codex-y5 dir itself (correct content outside)
  4  symlinked fixture file to an outside TAMPERED target
  5  symlinked non-manifest dir (codex-y5/extras -> outside)

Usage: python3 attack_a7.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify")
SHIPS = os.path.join(WORK, "ships")
CLEAN = os.path.join(SHIPS, "clean")
OUTSIDE = os.path.join(WORK, "a7-outside")
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def fresh_ship(name):
    dest = os.path.join(SHIPS, name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(CLEAN, dest)
    return dest


def run(cmd, cwd=None, timeout=120):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)
    return proc, time.time() - t0


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def strip_scan(ship):
    """Remove the `_refuse_tampered_ship()` call from the staged
    runner and re-point the staged manifest at the stripped
    bytes. Returns True on a clean strip."""
    runner = os.path.join(ship, "run_codex_y5.py")
    src = open(runner, "r", encoding="utf-8").read()
    old = "\n_refuse_tampered_ship()\n"
    if src.count(old) != 1:
        return False
    src = src.replace(old, "\n# scan stripped for layer-2 test\n")
    open(runner, "w", encoding="utf-8").write(src)
    man_path = os.path.join(ship, "codex-y5-manifest.json")
    man = json.load(open(man_path))
    for entry in man["files"]:
        if entry["path"] == "run_codex_y5.py":
            entry["md5"] = md5_of(runner)
    json.dump(man, open(man_path, "w"), indent=2)
    open(man_path, "a").write("\n")
    return True


def verify_direct(ship):
    return run([sys.executable, "-P", "run_codex_y5.py",
                "--verify-manifest"], cwd=ship)


def shape_1(ship, tag):
    real = os.path.join(OUTSIDE, tag, "fixtures-real")
    shutil.copytree(os.path.join(ship, "codex-y5", "fixtures"), real)
    shutil.rmtree(os.path.join(ship, "codex-y5", "fixtures"))
    os.symlink(real, os.path.join(ship, "codex-y5", "fixtures"))


def shape_2(ship, tag):
    real = os.path.join(OUTSIDE, tag, "test-01-git-workflow.md")
    shutil.copy2(os.path.join(ship, "codex-y5",
                              "test-01-git-workflow.md"), real)
    os.unlink(os.path.join(ship, "codex-y5", "test-01-git-workflow.md"))
    os.symlink(real, os.path.join(ship, "codex-y5",
                                  "test-01-git-workflow.md"))


def shape_3(ship, tag):
    real = os.path.join(OUTSIDE, tag, "codex-y5-real")
    shutil.copytree(os.path.join(ship, "codex-y5"), real)
    shutil.rmtree(os.path.join(ship, "codex-y5"))
    os.symlink(real, os.path.join(ship, "codex-y5"))


def shape_4(ship, tag):
    real = os.path.join(OUTSIDE, tag, "tampered-fixture.html")
    with open(real, "w") as f:
        f.write("<html><body>TAMPERED</body></html>\n")
    target = os.path.join(ship, "codex-y5", "fixtures",
                          "test-01-git-workflow.html")
    os.unlink(target)
    os.symlink(real, target)


def shape_5(ship, tag):
    real = os.path.join(OUTSIDE, tag, "extras-real")
    os.makedirs(real, exist_ok=True)
    with open(os.path.join(real, "junk.txt"), "w") as f:
        f.write("junk\n")
    os.symlink(real, os.path.join(ship, "codex-y5", "extras"))


SHAPES = [
    ("symlink fixtures dir", shape_1),
    ("symlink manifest file", shape_2),
    ("symlink codex-y5 dir", shape_3),
    ("symlink fixture to outside tampered", shape_4),
    ("symlink non-manifest dir", shape_5),
]


def main(argv):
    t0 = time.time()
    log("A7 START")
    if os.path.exists(OUTSIDE):
        shutil.rmtree(OUTSIDE)
    os.makedirs(OUTSIDE)
    for label, shape in SHAPES:
        ship = fresh_ship("a7-" + label.split()[1])
        os.makedirs(os.path.join(OUTSIDE, "a7-" + label.split()[1]), exist_ok=True)
        shape(ship, "a7-" + label.split()[1])
        # Layer 1: module-top scan.
        proc, dt = verify_direct(ship)
        out = proc.stdout + proc.stderr
        check(f"A7 {label} scan layer",
              proc.returncode == 2
              and '"refused": true' in out
              and '"kind": "symlink"' in out
              and "pyc_refused" not in out,
              f"python3 -P run_codex_y5.py --verify-manifest "
              f"rc={proc.returncode} ({dt:.1f}s) "
              f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")
        # Layer 2: _verify_manifest on a stripped copy.
        ship2 = fresh_ship("a7-" + label.split()[1] + "-stripped")
        os.makedirs(os.path.join(OUTSIDE, "a7-" + label.split()[1] + "-stripped"), exist_ok=True)
        shape(ship2, "a7-" + label.split()[1] + "-stripped")
        ok = strip_scan(ship2)
        if not ok:
            check(f"A7 {label} verify layer (strip failed)",
                  False, "could not strip the scan call (count != 1)")
            continue
        proc, dt = verify_direct(ship2)
        out = proc.stdout + proc.stderr
        # The refusal may come from _manifest_entries' path
        # containment ("manifest path escapes ship dir") when a
        # manifest path resolves outside via a symlink, or from
        # the walk ("symlink in ship dir") for a non-manifest
        # symlink. Both are _verify_manifest-layer refusals.
        check(f"A7 {label} verify layer",
              proc.returncode == 2 and '"manifest_ok": false' in out
              and ("symlink" in out
                   or "manifest path escapes ship dir" in out),
              f"python3 -P run_codex_y5.py --verify-manifest "
              f"(stripped) rc={proc.returncode} ({dt:.1f}s) "
              f"tail={out.strip().splitlines()[-1][:300] if out.strip() else ''}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A7 DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

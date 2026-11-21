#!/usr/bin/env python3
"""Clean ship + launcher dry run (Y13g re-verification).

  1  Fresh staged ship from the committed bytes:
     `python3 -P run_codex_y5.py --verify-manifest` must be rc 0.
  2  Launcher dry run against the staged ship (via
     launcher_check_driver.py, --ship-dir, real repo, no Y13_GO,
     no live ports, no live run): check_manifest, _scan_ship,
     _check_entry_pyc. Each must pass (rc 0).
  3  Extra (A6b re-test): a tampered ship (one fixture byte
     changed AND the manifest entry edited to match, so the
     ship is self-consistent) must be REFUSED by check_manifest
     on the md5 comparison against the committed manifest.

Usage: python3 clean_ship.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify")
SHIPS = os.path.join(WORK, "ships")
CLEAN = os.path.join(SHIPS, "clean")
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def run(cmd, cwd=None, env=None, timeout=180):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env)
    return proc, time.time() - t0


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def driver(check_name, ship, repo=REPO):
    return run([sys.executable,
                os.path.join(HERE, "launcher_check_driver.py"),
                "--ship-dir", ship, "--check", check_name,
                "--repo", repo])


def main(argv):
    t0 = time.time()
    log("CLEAN-SHIP START")
    # Fresh staged ship (re-stage from the committed bytes).
    ship = os.path.join(SHIPS, "clean2")
    if os.path.exists(ship):
        shutil.rmtree(ship)
    proc, dt = run([sys.executable,
                    os.path.join(REPO, "tests", "realistic",
                                 "regen_codex_y5_manifest.py"),
                    "--stage", ship], cwd=REPO)
    out = proc.stdout + proc.stderr
    check("clean re-stage rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"regen --stage rc={proc.returncode} ({dt:.1f}s)")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("clean ship direct verify rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out
          and '"files_checked": 27' in out,
          f"python3 -P run_codex_y5.py --verify-manifest "
          f"rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # Freshen the remote-tracking branch for the manifest pin.
    proc, dt = run(["git", "-C", REPO, "fetch", "origin",
                    "todolist-push"])
    log(f"git fetch origin todolist-push rc={proc.returncode} "
        f"({dt:.1f}s)")
    for chk in ("manifest", "scan", "entry-pyc"):
        proc, dt = driver(chk, ship)
        out = proc.stdout + proc.stderr
        check(f"clean ship launcher dry run: {chk}",
              proc.returncode == 0,
              f"launcher_check_driver.py --check {chk} "
              f"rc={proc.returncode} ({dt:.1f}s) "
              f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # Extra: self-consistent tampered ship refused by the pin.
    tship = os.path.join(SHIPS, "clean2-tampered")
    if os.path.exists(tship):
        shutil.rmtree(tship)
    shutil.copytree(ship, tship)
    fix = os.path.join(tship, "codex-y5", "fixtures",
                       "test-01-git-workflow.html")
    data = open(fix, "rb").read()
    open(fix, "wb").write(data + b"<!-- tampered -->\n")
    man_path = os.path.join(tship, "codex-y5-manifest.json")
    man = json.load(open(man_path))
    for entry in man["files"]:
        if entry["path"] == "codex-y5/fixtures/test-01-git-workflow.html":
            entry["md5"] = hashlib.md5(open(fix, "rb").read()).hexdigest()
    json.dump(man, open(man_path, "w"), indent=2)
    open(man_path, "a").write("\n")
    proc, dt = driver("manifest", tship)
    out = proc.stdout + proc.stderr
    check("tampered self-consistent ship refused by manifest pin",
          proc.returncode == 2 and "!=" in out
          and "committed manifest" in out,
          f"launcher_check_driver.py --check manifest "
          f"rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"CLEAN-SHIP DONE {npass}/{len(RESULTS)} pass "
        f"in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

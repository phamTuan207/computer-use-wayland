#!/usr/bin/env python3
"""A2 forge set (Y13g re-verification, rebuilt from the redteam
paper spec). Each case stages a FRESH ship from the committed
bytes, forges one entry .pyc, and checks the launcher path refuses
with no marker printed. Direct -m/import forms are also run to
document the KNOWN unfixable in-process hole (a forged entry .pyc
invoked that way executes; the control is the launcher check +
never invoking -m/import on an unverified ship).

Cases:
  a  forged run_codex_y5 entry .pyc, launcher _check_entry_pyc
     (must refuse rc 2, no marker) + direct -m (hole demo: marker
     prints, guard exits 2 after deleting the forged .pyc)
  a2 fake-OK forged entry .pyc, launcher check (must refuse, no
     marker, no fake manifest_ok) + direct -m (hole demo: marker
     + fake manifest_ok true, rc 0, the gate lies)
  b  forged run_codex_y5 entry .pyc, import form via launcher
     check (must refuse, no marker) + direct import (hole demo)
  c  fake-OK forge + direct `python3 -P run_codex_y5.py
     --verify-manifest` (must NOT print manifest_ok true, rc 2)
  d  forged launch_y13 entry .pyc, launcher check (must refuse,
     no marker) + direct -m launch_y13 --help (hole demo)
  e  A1 control: forged NON-entry run_live .pyc, direct form
     `python3 -P run_codex_y5.py --verify-manifest` (must refuse
     rc 2, no marker) + launcher check (must refuse, no marker)

Usage: python3 attack_a2.py [--workdir DIR]
Prints one PASS/FAIL line per case with command + rc + output
tail. Exits 0 only if every case passes its expectation.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify", "ships")
CLEAN = os.path.join(WORK, "clean")
sys.path.insert(0, HERE)
import extract_lib
import forge_pyc

MARKER = "POISON-MARKER"
RESULTS = []


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def run(cmd, cwd=None, env=None, timeout=120):
    t0 = __import__("time").time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env)
    dt = __import__("time").time() - t0
    return proc, dt


def fresh_ship(name):
    dest = os.path.join(WORK, name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(CLEAN, dest)
    return dest


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def main(argv):
    import time
    t0 = time.time()
    log("A2 START")
    # --- case a: forged run_codex_y5 entry .pyc ---
    ship = fresh_ship("a2a-entry")
    forge_pyc.forge(os.path.join(ship, "run_codex_y5.py"),
                    "A2a entry run_codex_y5 forged",
                    os.path.join(ship, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"))
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A2a launcher-check forged entry .pyc",
          proc.returncode == 2 and MARKER not in out
          and "entry .pyc mismatch" in out,
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # hole demo: direct -m on a FRESH forged ship (the guard deletes
    # the forged .pyc after the marker prints; use a second ship).
    ship2 = fresh_ship("a2a-entry-direct-m")
    forge_pyc.forge(os.path.join(ship2, "run_codex_y5.py"),
                    "A2a entry run_codex_y5 forged",
                    os.path.join(ship2, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"))
    proc, dt = run([sys.executable, "-m", "run_codex_y5",
                    "--verify-manifest"], cwd=ship2)
    out = proc.stdout + proc.stderr
    log(f"HOLE-DEMO A2a direct -m on forged ship: rc={proc.returncode} "
        f"({dt:.1f}s) marker_printed={MARKER in out} "
        f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    check("A2a-hole direct -m prints marker (known unfixable hole)",
          MARKER in out,
          f"python3 -m run_codex_y5 --verify-manifest rc={proc.returncode}")

    # --- case a2: fake-OK forge, launcher check + direct -m ---
    ship = fresh_ship("a2a-fakeok")
    forge_pyc.forge(os.path.join(ship, "run_codex_y5.py"),
                    "A2b fake verify gate",
                    os.path.join(ship, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"),
                    fake_ok=True, manifest_md5="0ca16ddd743acc9e28294fecd07a9c70")
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A2b launcher-check fake-OK forge",
          proc.returncode == 2 and MARKER not in out
          and "manifest_ok\": true" not in out
          and "entry .pyc mismatch" in out,
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    ship2 = fresh_ship("a2a-fakeok-direct-m")
    forge_pyc.forge(os.path.join(ship2, "run_codex_y5.py"),
                    "A2b fake verify gate",
                    os.path.join(ship2, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"),
                    fake_ok=True, manifest_md5="0ca16ddd743acc9e28294fecd07a9c70")
    proc, dt = run([sys.executable, "-m", "run_codex_y5",
                    "--verify-manifest"], cwd=ship2)
    out = proc.stdout + proc.stderr
    log(f"HOLE-DEMO A2b direct -m fake-OK: rc={proc.returncode} "
        f"({dt:.1f}s) marker_printed={MARKER in out} "
        f"fake_ok_printed={'manifest_ok\": true' in out} "
        f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    check("A2b-hole direct -m fake-OK lies (known unfixable hole)",
          MARKER in out and '"manifest_ok": true' in out
          and proc.returncode == 0,
          f"python3 -m run_codex_y5 --verify-manifest rc={proc.returncode}")

    # --- case b: import form via launcher check + direct import ---
    ship = fresh_ship("a2b-import")
    forge_pyc.forge(os.path.join(ship, "run_codex_y5.py"),
                    "A2b-import entry forged",
                    os.path.join(ship, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"))
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A2c launcher-check forged entry (import form)",
          proc.returncode == 2 and MARKER not in out
          and "entry .pyc mismatch" in out,
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s)")
    ship2 = fresh_ship("a2b-import-direct")
    forge_pyc.forge(os.path.join(ship2, "run_codex_y5.py"),
                    "A2b-import entry forged",
                    os.path.join(ship2, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"))
    proc, dt = run([sys.executable, "-c", "import run_codex_y5"],
                   cwd=ship2)
    out = proc.stdout + proc.stderr
    log(f"HOLE-DEMO A2c direct import on forged ship: rc={proc.returncode} "
        f"({dt:.1f}s) marker_printed={MARKER in out}")
    check("A2c-hole direct import prints marker (known unfixable hole)",
          MARKER in out,
          f"python3 -c 'import run_codex_y5' rc={proc.returncode}")

    # --- case c: fake-OK forge + DIRECT script form ---
    ship = fresh_ship("a2c-fakeok-direct")
    forge_pyc.forge(os.path.join(ship, "run_codex_y5.py"),
                    "A2c fake verify gate",
                    os.path.join(ship, "__pycache__",
                                 "run_codex_y5.cpython-312.pyc"),
                    fake_ok=True, manifest_md5="0ca16ddd743acc9e28294fecd07a9c70")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A2d direct script form fake-OK forge",
          proc.returncode == 2 and MARKER not in out
          and '"manifest_ok": true' not in out
          and '"refused": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")

    # --- case d: forged launch_y13 entry .pyc ---
    ship = fresh_ship("a2d-launcher")
    forge_pyc.forge(os.path.join(ship, "launch_y13.py"),
                    "A2d entry launch_y13 forged",
                    os.path.join(ship, "__pycache__",
                                 "launch_y13.cpython-312.pyc"))
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A2e launcher-check forged launch_y13 entry .pyc",
          proc.returncode == 2 and MARKER not in out
          and "entry .pyc mismatch" in out,
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s)")
    ship2 = fresh_ship("a2d-launcher-direct-m")
    forge_pyc.forge(os.path.join(ship2, "launch_y13.py"),
                    "A2d entry launch_y13 forged",
                    os.path.join(ship2, "__pycache__",
                                 "launch_y13.cpython-312.pyc"))
    proc, dt = run([sys.executable, "-m", "launch_y13", "--help"],
                   cwd=ship2)
    out = proc.stdout + proc.stderr
    log(f"HOLE-DEMO A2e direct -m launch_y13 forged: rc={proc.returncode} "
        f"({dt:.1f}s) marker_printed={MARKER in out}")
    check("A2e-hole direct -m launch_y13 prints marker (known hole)",
          MARKER in out,
          f"python3 -m launch_y13 --help rc={proc.returncode}")

    # --- case e: A1 control, forged NON-entry run_live .pyc ---
    ship = fresh_ship("a2e-runlive")
    forge_pyc.forge(os.path.join(ship, "run_live.py"),
                    "A1 run_live forged",
                    os.path.join(ship, "__pycache__",
                                 "run_live.cpython-312.pyc"))
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A2f A1-control forged run_live .pyc direct form",
          proc.returncode == 2 and MARKER not in out
          and '"refused": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A2g A1-control forged run_live .pyc launcher check",
          proc.returncode == 2 and MARKER not in out
          and "entry .pyc mismatch" in out,
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s)")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A2 DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    for name, ok, ev in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

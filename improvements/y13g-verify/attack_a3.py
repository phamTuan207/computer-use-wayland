#!/usr/bin/env python3
"""A3 brick sequence (Y13g re-verification, rebuilt from the
redteam paper + task brief specs). All cases on FRESH clean staged
ships (from the committed bytes).

  a  python3 -m run_codex_y5 --verify-manifest: exits 2 via the
     guard, deletes its entry .pyc (no .pyc left behind)
  b  direct python3 -P run_codex_y5.py --verify-manifest after
     (a): MUST be rc 0 (no brick)
  c  live-run attempt python3 -P run_codex_y5.py all: must NOT
     brick at the scan (MANIFEST OK printed); it fails later on
     preflight (no handover token / no Zen on this VM). Record
     how far it gets. Capped at 120s.
  d  empty __pycache__ dir alone, direct verify rc 0
  e  -m with PYTHONDONTWRITEBYTECODE=1 writes nothing (guard
     still exits 2, no __pycache__ created)
  f  forged NON-entry .pyc (run_live) must still refuse rc 2,
     no marker, direct form

Usage: python3 attack_a3.py
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
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


def fresh_ship(name):
    dest = os.path.join(WORK, name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(CLEAN, dest)
    return dest


def run(cmd, cwd=None, env=None, timeout=120):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env)
    return proc, time.time() - t0


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def main(argv):
    t0 = time.time()
    log("A3 START")
    # --- a: -m on a clean ship ---
    ship = fresh_ship("a3a-m")
    proc, dt = run([sys.executable, "-m", "run_codex_y5",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    cache = os.path.join(ship, "__pycache__")
    left = sorted(os.listdir(cache)) if os.path.isdir(cache) else []
    check("A3a -m exits 2 via guard, no .pyc left",
          proc.returncode == 2 and "run as a script" in out
          and not [n for n in left if n.endswith(".pyc")],
          f"python3 -m run_codex_y5 --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) pyc_left={[n for n in left if n.endswith('.pyc')]} "
          f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # --- b: direct form after (a) ---
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3b direct verify after -m is rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # --- c: live-run attempt ---
    try:
        proc, dt = run([sys.executable, "-P", "run_codex_y5.py", "all"],
                       cwd=ship, timeout=120)
        out = proc.stdout + proc.stderr
        lines = [l for l in out.splitlines() if l.strip()]
        check("A3c live-run attempt does not brick at the scan",
              "MANIFEST OK" in out and "MANIFEST FAILED" not in out,
              f"python3 -P run_codex_y5.py all rc={proc.returncode} "
              f"({dt:.1f}s) last_lines={' | '.join(lines[-3:])[:300]}")
        log(f"A3c full tail: {' | '.join(lines[-6:])[:600]}")
    except subprocess.TimeoutExpired:
        check("A3c live-run attempt does not brick at the scan",
              False, "live-run attempt hit the 120s cap (unexpected)")
    # --- c2: same attempt with the server root pointed at the
    # staged ship: must reach SERVED FILES OK, then fail at
    # preflight on the owner-away check (no handover token on
    # this VM), rc 2, no driving. This pins down that the A3c
    # 404s are only the default server-root artifact.
    try:
        env = dict(os.environ)
        env["LIVE_SERVER_ROOT"] = ship
        proc, dt = run([sys.executable, "-P", "run_codex_y5.py", "all"],
                       cwd=ship, env=env, timeout=120)
        out = proc.stdout + proc.stderr
        check("A3c2 live-run with server root reaches preflight",
              "MANIFEST OK" in out and "SERVED FILES OK" in out
              and "PREFLIGHT FAILED" in out
              and "LIVE_OWNER_AWAY is not 1" in out
              and proc.returncode == 2,
              f"python3 -P run_codex_y5.py all rc={proc.returncode} "
              f"({dt:.1f}s) tail={' | '.join([l for l in out.splitlines() if l.strip()][-2:])[:300]}")
    except subprocess.TimeoutExpired:
        check("A3c2 live-run with server root reaches preflight",
              False, "live-run attempt hit the 120s cap (unexpected)")
    # --- d: empty __pycache__ dir alone ---
    ship = fresh_ship("a3d-empty-cache")
    os.makedirs(os.path.join(ship, "__pycache__"), exist_ok=True)
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3d empty __pycache__ dir alone, direct verify rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # --- e: env-guarded -m writes nothing ---
    ship = fresh_ship("a3e-env-m")
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc, dt = run([sys.executable, "-m", "run_codex_y5",
                    "--verify-manifest"], cwd=ship, env=env)
    out = proc.stdout + proc.stderr
    cache_exists = os.path.exists(os.path.join(ship, "__pycache__"))
    check("A3e env-guarded -m writes nothing",
          proc.returncode == 2 and "run as a script" in out
          and not cache_exists,
          f"PYTHONDONTWRITEBYTECODE=1 python3 -m run_codex_y5 "
          f"--verify-manifest rc={proc.returncode} ({dt:.1f}s) "
          f"__pycache___exists={cache_exists}")
    # --- f: forged NON-entry .pyc still refuses ---
    ship = fresh_ship("a3f-runlive")
    forge_pyc.forge(os.path.join(ship, "run_live.py"),
                    "A3f run_live forged",
                    os.path.join(ship, "__pycache__",
                                 "run_live.cpython-312.pyc"))
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3f forged non-entry .pyc refuses rc 2, no marker",
          proc.returncode == 2 and MARKER not in out
          and '"refused": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A3 DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

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
  R2 g  -m WITHOUT -P: the script-form guard fires FIRST (rc 2,
     guard message, no .pyc left), before the safe_path gate.
  R2 h  py_compile the runner (legit entry .pyc appears): direct
     verify refuses (runner scan, kind pyc), launcher
     _check_entry_pyc deletes it (rc 0), direct verify is rc 0
     again (self-heal).
  R2 i  import run_live (legit entry .pyc appears): same heal
     sequence as (h) for the third entry stem.

Usage: python3 attack_a3.py
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-r2-verify", "ships")
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
    # --- R2 g: -m WITHOUT -P: guard first, safe_path never reached ---
    ship = fresh_ship("a3g-m-nop")
    env = dict(os.environ)
    env.pop("PYTHONSAFEPATH", None)
    proc, dt = run([sys.executable, "-m", "run_codex_y5",
                    "--verify-manifest"], cwd=ship, env=env)
    out = proc.stdout + proc.stderr
    cache = os.path.join(ship, "__pycache__")
    left = sorted(os.listdir(cache)) if os.path.isdir(cache) else []
    check("A3g bare -m (no -P) guard fires first, no .pyc left",
          proc.returncode == 2 and "run as a script" in out
          and "run with python3 -P" not in out
          and not [n for n in left if n.endswith(".pyc")],
          f"python3 -m run_codex_y5 --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s) pyc_left={[n for n in left if n.endswith('.pyc')]} "
          f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")
    # --- R2 h: py_compile self-heal ---
    ship = fresh_ship("a3h-pycompile")
    proc, dt = run([sys.executable, "-m", "py_compile",
                    "run_codex_y5.py"], cwd=ship)
    pyc = os.path.join(ship, "__pycache__",
                       "run_codex_y5.cpython-312.pyc")
    log(f"A3h py_compile rc={proc.returncode} ({dt:.1f}s) "
        f"pyc_exists={os.path.exists(pyc)}")
    check("A3h py_compile writes a legit entry .pyc",
          proc.returncode == 0 and os.path.exists(pyc),
          f"python3 -m py_compile run_codex_y5.py rc={proc.returncode}")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3h direct verify refuses legit entry .pyc (runner scan)",
          proc.returncode == 2 and '"kind": "pyc"' in out
          and MARKER not in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s)")
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A3h launcher entry-pyc check deletes legit .pyc rc 0",
          proc.returncode == 0 and not os.path.exists(pyc),
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s) pyc_gone={not os.path.exists(pyc)}")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3h direct verify after heal is rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s)")
    # --- R2 h control: ABSOLUTE-path py_compile (boundary probe) ---
    # The relative form above fails because the .pyc's co_filename
    # is "run_codex_y5.py" while the fresh compile uses the
    # absolute path; the absolute form must pass, proving the
    # only difference is the filename metadata.
    ship_abs = fresh_ship("a3h-abs")
    proc, dt = run([sys.executable, "-m", "py_compile",
                    os.path.join(ship_abs, "run_codex_y5.py")],
                   cwd=ship_abs)
    pyc_abs = os.path.join(ship_abs, "__pycache__",
                           "run_codex_y5.cpython-312.pyc")
    check("A3h-abs absolute-path py_compile writes a legit .pyc",
          proc.returncode == 0 and os.path.exists(pyc_abs),
          f"python3 -m py_compile <abs>/run_codex_y5.py "
          f"rc={proc.returncode}")
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship_abs, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A3h-abs launcher entry-pyc accepts absolute-path .pyc",
          proc.returncode == 0 and not os.path.exists(pyc_abs),
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s) pyc_gone={not os.path.exists(pyc_abs)}")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship_abs)
    out = proc.stdout + proc.stderr
    check("A3h-abs direct verify after heal is rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s)")
    ship = fresh_ship("a3i-import-runlive")
    proc, dt = run([sys.executable, "-c", "import run_live"],
                   cwd=ship)
    out = proc.stdout + proc.stderr
    pyc = os.path.join(ship, "__pycache__",
                       "run_live.cpython-312.pyc")
    log(f"A3i import run_live rc={proc.returncode} ({dt:.1f}s) "
        f"pyc_exists={os.path.exists(pyc)} "
        f"tail={out.strip().splitlines()[-1][:120] if out.strip() else ''}")
    check("A3i import run_live writes a legit entry .pyc",
          os.path.exists(pyc),
          f"python3 -c 'import run_live' rc={proc.returncode}")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3i direct verify refuses legit run_live .pyc",
          proc.returncode == 2 and '"kind": "pyc"' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s)")
    proc, dt = run([sys.executable,
                    os.path.join(HERE, "launcher_check_driver.py"),
                    "--ship-dir", ship, "--check", "entry-pyc"])
    out = proc.stdout + proc.stderr
    check("A3i launcher entry-pyc check deletes legit run_live .pyc",
          proc.returncode == 0 and not os.path.exists(pyc),
          f"launcher_check_driver.py --check entry-pyc rc={proc.returncode} "
          f"({dt:.1f}s) pyc_gone={not os.path.exists(pyc)}")
    proc, dt = run([sys.executable, "-P", "run_codex_y5.py",
                    "--verify-manifest"], cwd=ship)
    out = proc.stdout + proc.stderr
    check("A3i direct verify after heal is rc 0",
          proc.returncode == 0 and '"manifest_ok": true' in out,
          f"python3 -P run_codex_y5.py --verify-manifest rc={proc.returncode} "
          f"({dt:.1f}s)")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A3 DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

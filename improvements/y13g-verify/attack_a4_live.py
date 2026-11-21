#!/usr/bin/env python3
"""A4 live probe (Y13g re-verification, rebuilt from the redteam
paper spec). Spawns REAL dummy processes carrying exact target
cmdlines (via an argv-ignoring sleeper binary, so the /proc
cmdline is exactly the target argv) and runs the REAL launcher
check_runner_quiet (AST-extracted, via launcher_check_driver.py)
against them, one case at a time. No live Zen driving; plain
sleep processes only.

Cases:
  control      no dummy: baseline (other fleet workers' probes
               may already be offenders; recorded, not assumed)
  bare         python3 run_codex_y5.py (real copy in a temp cwd)
  -m           python3 -m run_codex_y5
  renamed      python3 /tmp/mycopy.py (real runner bytes)
  symlink      python3 /tmp/link.py (real symlink to the runner)
  echo         bash -c "echo python3 run_codex_y5.py; sleep 60"
               (must NOT be flagged; bash stays bash)

PASS for bare/-m/renamed/symlink: driver refuses rc 2 AND the
dummy pid is named as an offender. PASS for echo: driver passes
rc 0 AND the bash pid is not named. Baseline offenders from
other workers are recorded and excluded by pid.

Usage: python3 attack_a4_live.py
"""
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify")
SHIPS = os.path.join(WORK, "ships")
CLEAN = os.path.join(SHIPS, "clean")
SLEEPER = os.path.join(WORK, "sleeper")
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def run_driver():
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "launcher_check_driver.py"),
         "--ship-dir", CLEAN, "--check", "runner-quiet"],
        capture_output=True, text=True, timeout=120)
    dt = time.time() - t0
    out = proc.stdout + proc.stderr
    pids = [int(x) for x in re.findall(r"pid (\d+)", out)]
    warns = [l for l in out.splitlines() if "WARNING" in l]
    return proc.returncode, pids, warns, out, dt


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def spawn_dummy(argv, cwd=None):
    p = subprocess.Popen(argv, executable=SLEEPER, cwd=cwd,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    time.sleep(0.3)
    assert p.poll() is None, f"dummy died at once: {argv}"
    return p


def main(argv):
    t0 = time.time()
    log("A4-LIVE START")
    # Re-stage the md5-leg fixtures fresh.
    shutil.copy2(os.path.join(CLEAN, "run_codex_y5.py"), "/tmp/mycopy.py")
    if os.path.islink("/tmp/link.py") or os.path.exists("/tmp/link.py"):
        os.unlink("/tmp/link.py")
    os.symlink(os.path.join(CLEAN, "run_codex_y5.py"), "/tmp/link.py")
    # Temp cwd holding a real copy of the runner (bare-relative).
    dummy_cwd = os.path.join(WORK, "a4live-cwd")
    if os.path.exists(dummy_cwd):
        shutil.rmtree(dummy_cwd)
    os.makedirs(dummy_cwd)
    shutil.copy2(os.path.join(CLEAN, "run_codex_y5.py"), dummy_cwd)
    # Baseline (no dummy of mine).
    rc, pids, warns, out, dt = run_driver()
    log(f"BASELINE no dummy: driver rc={rc} ({dt:.1f}s) "
        f"offender_pids={pids} warnings={len(warns)}")
    baseline_pids = set(pids)
    check("A4-live baseline recorded",
          True,
          f"driver rc={rc} offender_pids={pids} "
          f"(fleet probes, if any, are baseline)")

    cases = [
        ("bare python3 run_codex_y5.py",
         ["python3", "run_codex_y5.py"], dummy_cwd, True),
        ("-m python3 -m run_codex_y5",
         ["python3", "-m", "run_codex_y5"], None, True),
        ("renamed python3 /tmp/mycopy.py",
         ["python3", "/tmp/mycopy.py"], None, True),
        ("symlink python3 /tmp/link.py",
         ["python3", "/tmp/link.py"], None, True),
    ]
    for label, argv_list, cwd, must_flag in cases:
        p = spawn_dummy(argv_list, cwd=cwd)
        try:
            cmdline = open(f"/proc/{p.pid}/cmdline", "rb").read()
            log(f"dummy {label}: pid={p.pid} "
                f"cmdline={cmdline!r}")
            rc, pids, warns, out, dt = run_driver()
            named = p.pid in pids
            check(f"A4-live {label}",
                  rc == 2 and named,
                  f"driver rc={rc} ({dt:.1f}s) dummy_pid={p.pid} "
                  f"named={named} offender_pids={pids} "
                  f"warnings={len(warns)}")
        finally:
            p.kill()
            p.wait()

    # Echo mention: a real bash that stays bash. The -c string ends
    # in `read x` (a builtin that blocks on stdin, held open by a
    # pipe), so bash never exec-replaces itself with the last
    # command (a trailing `sleep 60` would make the process BECOME
    # sleep, which vacates the FP test entirely).
    bash = subprocess.Popen(
        ["bash", "-c", "echo python3 run_codex_y5.py; read x"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.3)
    try:
        assert bash.poll() is None, "bash echo dummy died at once"
        cmdline = open(f"/proc/{bash.pid}/cmdline", "rb").read()
        log(f"dummy echo mention: pid={bash.pid} cmdline={cmdline!r}")
        assert cmdline.startswith(b"bash\x00"), \
            f"echo dummy is not bash any more: {cmdline!r}"
        rc, pids, warns, out, dt = run_driver()
        named = bash.pid in pids
        new_pids = [x for x in pids if x not in baseline_pids]
        check("A4-live echo mention not flagged",
              rc == 0 and not named and not new_pids,
              f"driver rc={rc} ({dt:.1f}s) bash_pid={bash.pid} "
              f"named={named} offender_pids={pids} warnings={len(warns)}")
    finally:
        bash.kill()
        bash.wait()

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A4-LIVE DONE {npass}/{len(RESULTS)} pass "
        f"in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

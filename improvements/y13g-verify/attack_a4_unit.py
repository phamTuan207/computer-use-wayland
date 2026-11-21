#!/usr/bin/env python3
"""A4 tokenizer unit table (Y13g re-verification, rebuilt from the
redteam paper + task brief specs). 39 NUL-separated cmdlines, run
through _is_runner_cmdline AST-extracted from BOTH the runner and
the launcher; the two copies must agree on every case. True means
CAUGHT (the cmdline executes a runner), False means NOT caught.

Renamed copy / symlink cases stage a REAL copy of the runner
bytes at /tmp/mycopy.py and a REAL symlink at /tmp/link.py (the
md5 leg resolves the script token to its real path and compares
against the manifest md5s, so the files must exist with the
committed runner bytes).

Usage: python3 attack_a4_unit.py
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify", "ships")
CLEAN = os.path.join(WORK, "clean")
RUNNER = os.path.join(REPO, "tests", "realistic", "run_codex_y5.py")
LAUNCHER = os.path.join(REPO, "tests", "realistic", "launch_y13.py")
sys.path.insert(0, HERE)
import extract_lib

RUN = "run_codex_y5.py"
ABS_RUN = os.path.join(CLEAN, RUN)

# (label, argv tokens, expected verdict)
CASES = [
    ("bare-relative runner", ["python3", RUN], True),
    ("absolute runner", ["python3", ABS_RUN], True),
    ("python3 -m run_codex_y5", ["python3", "-m", "run_codex_y5"], True),
    ("-m run_live", ["python3", "-m", "run_live"], True),
    ("-m pkg.run_codex_y5", ["python3", "-m", "pkg.run_codex_y5"], True),
    ("-m run_codex_y5 --verify-manifest",
     ["python3", "-m", "run_codex_y5", "--verify-manifest"], True),
    ("python3 -u runner", ["python3", "-u", RUN], True),
    ("-W ignore runner", ["python3", "-W", "ignore", RUN], True),
    ("-X dev runner", ["python3", "-X", "dev", RUN], True),
    ("-X faulthandler runner",
     ["python3", "-X", "faulthandler", RUN], True),
    ("--check-hash-based-pycs always runner",
     ["python3", "--check-hash-based-pycs", "always", RUN], True),
    ("-c import runner", ["python3", "-c", "import run_codex_y5"], False),
    ("-c exec(open(runner))",
     ["python3", "-c", "exec(open('run_codex_y5.py').read())"], True),
    ("env VAR=1 python3 runner",
     ["env", "VAR=1", "python3", RUN], True),
    ("nohup python3 runner", ["nohup", "python3", RUN], True),
    ("setsid python3 runner", ["setsid", "python3", RUN], True),
    ("/usr/bin/python3 runner", ["/usr/bin/python3", RUN], True),
    ("python3 ./runner", ["python3", "./" + RUN], True),
    ("python3 ../ship/runner", ["python3", "../ship/" + RUN], True),
    ("python3.12 runner", ["python3.12", RUN], True),
    ("python runner", ["python", RUN], True),
    ("python3 runner no ext", ["python3", "run_codex_y5"], True),
    ("python3 run-nested-pill.py",
     ["python3", "run-nested-pill.py"], True),
    ("bash run-nested-wayland.sh",
     ["bash", "run-nested-wayland.sh"], True),
    ("sh -c python3 runner",
     ["sh", "-c", "python3 run_codex_y5.py"], True),
    ("bash -c exec python3 runner",
     ["bash", "-c", "exec python3 run_codex_y5.py"], True),
    ("bash -c echo python3 runner",
     ["bash", "-c", "echo python3 run_codex_y5.py"], False),
    ("bash -c grep python3 runner",
     ["bash", "-c", "grep python3 run_codex_y5.py file.txt"], False),
    ("flock -c python3 runner",
     ["flock", "-c", "python3 run_codex_y5.py"], True),
    ("flock direct python3 runner",
     ["flock", "/tmp/x.lock", "python3", RUN], True),
    ("md5sum mention", ["md5sum", ABS_RUN], False),
    ("renamed copy", ["python3", "/tmp/mycopy.py"], True),
    ("symlink other name", ["python3", "/tmp/link.py"], True),
    ("timeout python3 runner",
     ["timeout", "60", "python3", RUN], True),
    ("python3 run_live.py", ["python3", "run_live.py"], True),
    ("python3 hand_drive_e1.py",
     ["python3", "hand_drive_e1.py"], True),
    ("./run_codex_y5.py shebang", ["./" + RUN], True),
    ("python3 -I runner", ["python3", "-I", RUN], True),
    ("python3 -m run_codex_y5.py (invalid form)",
     ["python3", "-m", "run_codex_y5.py"], False),
]


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def main(argv):
    t0 = time.time()
    log("A4-UNIT START")
    # Stage the md5-leg fixtures fresh (real runner bytes).
    shutil.copy2(os.path.join(CLEAN, RUN), "/tmp/mycopy.py")
    if os.path.islink("/tmp/link.py") or os.path.exists("/tmp/link.py"):
        os.unlink("/tmp/link.py")
    os.symlink(os.path.join(CLEAN, RUN), "/tmp/link.py")
    log("staged /tmp/mycopy.py (real runner copy) and /tmp/link.py "
        "(real symlink to the staged runner)")
    ns_r = extract_lib.extract_tokenizer(RUNNER, CLEAN)
    ns_l = extract_lib.extract_tokenizer(LAUNCHER, CLEAN)
    results = []
    old_cwd = os.getcwd()
    os.chdir(CLEAN)
    try:
        for label, tokens, want in CASES:
            cmdline = "\x00".join(tokens) + "\x00"
            got_r = ns_r["_is_runner_cmdline"](cmdline)
            got_l = ns_l["_is_runner_cmdline"](cmdline)
            agree = got_r == got_l
            ok = agree and got_r == want
            results.append((label, ok, got_r, got_l, want))
            log(f"{'PASS' if ok else 'FAIL'} A4 {label} :: "
                f"runner={got_r} launcher={got_l} want={want} "
                f"cmdline={' '.join(tokens)}")
    finally:
        os.chdir(old_cwd)
    npass = sum(1 for _, ok, _, _, _ in results if ok)
    log(f"A4-UNIT DONE {npass}/{len(results)} pass "
        f"in {time.time() - t0:.1f}s")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

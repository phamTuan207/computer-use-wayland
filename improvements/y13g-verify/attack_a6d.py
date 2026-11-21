#!/usr/bin/env python3
"""A6d stdlib shadowing map (Y13g re-verification, rebuilt from the
redteam paper spec). Plants each of 15 stdlib names as a top-level
.py in a FRESH staged ship. Each planted file prints POISON-MARKER
first, then delegates to the real stdlib module (path-strip +
re-import) so the run could continue if it ever executed. The
shim NEVER deletes any file (the Y13r2 redteam incident: a
self-deleting shim deleted /usr/lib/python3.12/re/__init__.py).

Run: python3 -P run_codex_y5.py --verify-manifest per name.
Marker must NEVER print for any name. Per-name outcome recorded:
rc, marker printed, output tail. Pre-loaded names (os, warnings,
functools, collections) and never-imported names (typing,
sre_compile) are reported as observed, not assumed.

Extra: re, json, enum are also run WITHOUT -P to confirm the
module-top scan protects even the non-P path.

Usage: python3 attack_a6d.py
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

NAMES = ("enum", "re", "json", "socket", "subprocess", "hashlib",
         "datetime", "pathlib", "copyreg", "functools", "collections",
         "os", "warnings", "typing", "sre_compile")
MARKER = "POISON-MARKER"
RESULTS = []


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def shim_code(name, ship_dir):
    # Marker first, then delegate to the real module. No file
    # deletion anywhere. The sys.modules swap makes a later
    # `import <name>` return the real module.
    return (
        f'print("POISON-MARKER A6d {name}")\n'
        "import sys\n"
        "for _p in list(sys.path):\n"
        f"    if _p == '' or _p == {ship_dir!r}:\n"
        "        sys.path.remove(_p)\n"
        f"if {name!r} in sys.modules:\n"
        f"    del sys.modules[{name!r}]\n"
        "import importlib as _il\n"
        f"_real = _il.import_module({name!r})\n"
        f"sys.modules[{name!r}] = _real\n"
    )


def fresh_ship(name):
    dest = os.path.join(WORK, name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(CLEAN, dest)
    return dest


def run_one(name, use_p=True):
    ship = fresh_ship(f"a6d-{name}{'-nop' if not use_p else ''}")
    with open(os.path.join(ship, name + ".py"), "w") as f:
        f.write(shim_code(name, ship))
    cmd = [sys.executable]
    if use_p:
        cmd.append("-P")
    cmd += ["run_codex_y5.py", "--verify-manifest"]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ship, capture_output=True,
                          text=True, timeout=120)
    dt = time.time() - t0
    out = proc.stdout + proc.stderr
    marker = MARKER in out
    ok = proc.returncode == 2 and not marker
    tail = out.strip().splitlines()[-1][:160] if out.strip() else ""
    RESULTS.append((f"A6d {name} {'-P' if use_p else 'no-P'}",
                    ok,
                    f"{' '.join(cmd)} rc={proc.returncode} "
                    f"({dt:.1f}s) marker={marker} tail={tail}"))
    log(f"{'PASS' if ok else 'FAIL'} A6d {name} "
        f"{'-P' if use_p else 'no-P'} :: rc={proc.returncode} "
        f"marker={marker} tail={tail}")
    return ok


def main(argv):
    t0 = time.time()
    log("A6d START")
    for name in NAMES:
        run_one(name, use_p=True)
    for name in ("re", "json", "enum"):
        run_one(name, use_p=False)
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A6d DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    for name, ok, ev in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

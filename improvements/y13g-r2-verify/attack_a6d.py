#!/usr/bin/env python3
"""A6d stdlib shadowing map (Y13g ROUND-2 re-verification,
rebuilt from the redteam paper spec). Plants each of 15 stdlib
names as a top-level .py in a FRESH staged ship. Each planted
file prints POISON-MARKER first, then delegates to the real
stdlib module (path-strip + re-import) so the run could continue
if it ever executed. The shim NEVER deletes any file (the Y13r2
redteam incident: a self-deleting shim deleted
/usr/lib/python3.12/re/__init__.py).

Run: python3 -P run_codex_y5.py --verify-manifest per name.
Marker must NEVER print for any name. Per-name outcome recorded:
rc, marker printed, output tail. Pre-loaded names (os, warnings,
functools, collections) and never-imported names (typing,
sre_compile) are reported as observed, not assumed.

ROUND-2 BEHAVIOR CHANGE: the no-P spot checks (re, json, enum)
now expect the safe_path refusal (exit 2, "run with python3 -P",
NO scan JSON, no marker), not the scan JSON: the safe_path gate
fires before the scan on a bare invocation.

.so PLANTS (R1/C2-1): each of 16 stdlib stems is also planted as
a compiled extension module <stem>.cpython-312-x86_64-linux-gnu.so
(built from the council-2 probe plant_so.c; its PyInit writes a
marker file on import). Three forms per stem, marker file must
NEVER appear: runner -P (scan refuses, kind unexpected-file),
runner bare (safe_path gate refuses first), launcher -P
--ship-dir (launcher scan refuses, "tampered ship"). The shlex
stem is the load-bearing one: the runner imports shlex at module
top right after the scan, so a planted shlex.so would execute
there if the scan did not refuse it first.

Usage: python3 attack_a6d.py
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

NAMES = ("enum", "re", "json", "socket", "subprocess", "hashlib",
         "datetime", "pathlib", "copyreg", "functools", "collections",
         "os", "warnings", "typing", "sre_compile")
SO_STEMS = ("glob", "http", "hashlib", "shlex", "re", "json",
            "socket", "subprocess", "datetime", "pathlib", "enum",
            "copyreg", "functools", "collections", "typing",
            "sre_compile")
MARKER = "POISON-MARKER"
RESULTS = []
SO_DIR = os.path.join(os.path.expanduser("~"), "workspace",
                      "y13g-r2-verify", "so-plants")
SO_MARKERS = os.path.join(os.path.expanduser("~"), "workspace",
                          "y13g-r2-verify", "so-markers")
PLANT_SO_C = os.path.join(os.path.expanduser("~"), "workspace",
                          "y13g-council-2", "probes", "plant_so.c")


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
    env = dict(os.environ)
    if not use_p:
        # The bare form must really be bare: a PYTHONSAFEPATH=1
        # in the ambient env would silently add -P semantics.
        env.pop("PYTHONSAFEPATH", None)
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ship, capture_output=True,
                          text=True, timeout=120, env=env)
    dt = time.time() - t0
    out = proc.stdout + proc.stderr
    marker = MARKER in out
    if use_p:
        ok = (proc.returncode == 2 and not marker
              and '"kind": "planted-py"' in out)
        want = "rc 2 kind planted-py, no marker"
    else:
        # R2: the safe_path gate fires before the scan on a bare
        # invocation: exit 2, the -P message, NO scan JSON.
        ok = (proc.returncode == 2 and not marker
              and "run with python3 -P" in out
              and '"refused": true' not in out)
        want = "rc 2 safe_path refusal, no marker, no scan JSON"
    tail = out.strip().splitlines()[-1][:160] if out.strip() else ""
    RESULTS.append((f"A6d {name} {'-P' if use_p else 'no-P'}",
                    ok,
                    f"{' '.join(cmd)} rc={proc.returncode} "
                    f"({dt:.1f}s) marker={marker} tail={tail}"))
    log(f"{'PASS' if ok else 'FAIL'} A6d {name} "
        f"{'-P' if use_p else 'no-P'} :: want {want} "
        f"rc={proc.returncode} marker={marker} tail={tail}")
    return ok


def build_so_plants():
    """Compile one extension-module plant per stem. The .so
    writes its marker file if it is ever imported."""
    os.makedirs(SO_DIR, exist_ok=True)
    os.makedirs(SO_MARKERS, exist_ok=True)
    inc = subprocess.run(["python3-config", "--includes"],
                         capture_output=True, text=True).stdout.split()
    for stem in SO_STEMS:
        out_so = os.path.join(
            SO_DIR, f"{stem}.cpython-312-x86_64-linux-gnu.so")
        marker_path = os.path.join(SO_MARKERS, f"{stem}.txt")
        if os.path.exists(out_so):
            continue
        proc = subprocess.run(
            ["gcc", "-shared", "-fPIC"] + inc
            + [f"-DSTEM_NAME={stem}",
               f'-DMARKER_PATH="{marker_path}"',
               "-o", out_so, PLANT_SO_C],
            capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(f"gcc plant {stem} failed: "
                               f"{proc.stderr[:300]}")
        log(f"built .so plant {stem} -> {out_so}")


def run_so_one(stem, form):
    """One .so plant case. form: runner-P | runner-bare |
    launcher-P. Marker file must never appear."""
    ship = fresh_ship(f"a6d-so-{stem}-{form}")
    marker_path = os.path.join(SO_MARKERS, f"{stem}.txt")
    if os.path.exists(marker_path):
        os.unlink(marker_path)
    shutil.copy2(os.path.join(
        SO_DIR, f"{stem}.cpython-312-x86_64-linux-gnu.so"), ship)
    env = dict(os.environ)
    env.pop("Y13_GO", None)
    env.pop("PYTHONSAFEPATH", None)
    t0 = time.time()
    if form == "runner-P":
        cmd = [sys.executable, "-P", "run_codex_y5.py",
               "--verify-manifest"]
        proc = subprocess.run(cmd, cwd=ship, capture_output=True,
                              text=True, timeout=120, env=env)
        out = proc.stdout + proc.stderr
        ok = (proc.returncode == 2
              and not os.path.exists(marker_path)
              and '"kind": "unexpected-file"' in out)
        want = "rc 2 kind unexpected-file, marker file absent"
    elif form == "runner-bare":
        cmd = [sys.executable, "run_codex_y5.py",
               "--verify-manifest"]
        proc = subprocess.run(cmd, cwd=ship, capture_output=True,
                              text=True, timeout=120, env=env)
        out = proc.stdout + proc.stderr
        ok = (proc.returncode == 2
              and not os.path.exists(marker_path)
              and "run with python3 -P" in out)
        want = "rc 2 safe_path refusal, marker file absent"
    else:  # launcher-P
        cmd = [sys.executable, "-P",
               os.path.join(ship, "launch_y13.py"),
               "--ship-dir", ship]
        proc = subprocess.run(cmd, cwd=ship, capture_output=True,
                              text=True, timeout=120, env=env)
        out = proc.stdout + proc.stderr
        ok = (proc.returncode == 2
              and not os.path.exists(marker_path)
              and "tampered ship" in out)
        want = "rc 2 tampered-ship refusal, marker file absent"
    dt = time.time() - t0
    tail = out.strip().splitlines()[-1][:160] if out.strip() else ""
    RESULTS.append((f"A6d .so {stem} {form}", ok,
                    f"{' '.join(cmd)} rc={proc.returncode} ({dt:.1f}s) "
                    f"marker_file={os.path.exists(marker_path)} "
                    f"tail={tail}"))
    log(f"{'PASS' if ok else 'FAIL'} A6d .so {stem} {form} :: "
        f"want {want} rc={proc.returncode} "
        f"marker_file={os.path.exists(marker_path)} tail={tail}")
    return ok


def main(argv):
    t0 = time.time()
    log("A6d START")
    for name in NAMES:
        run_one(name, use_p=True)
    for name in ("re", "json", "enum"):
        run_one(name, use_p=False)
    build_so_plants()
    for stem in SO_STEMS:
        for form in ("runner-P", "runner-bare", "launcher-P"):
            run_so_one(stem, form)
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A6d DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    for name, ok, ev in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

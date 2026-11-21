#!/usr/bin/env python3
"""A5b remote-URL normalization (Y13g ROUND-2 re-verification,
R7). Two layers:

  Unit: _normalize_remote_url AST-extracted from the launcher,
  11 URL spellings. Equivalent spellings of the known repo must
  normalize equal to the pinned URL; different host/owner/repo
  or http must not.

  Driver: _check_remote via launcher_check_driver.py --check
  remote against a synthetic clone whose origin URL is set to
  each variant (get-url only, no fetch). Pass variants must
  return rc 0; http and attacker-fork URLs must refuse rc 2
  with "not the known repo".

Usage: python3 attack_a5b.py
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-r2-verify")
A5B = os.path.join(WORK, "a5b")
CLEAN = os.path.join(WORK, "ships", "clean")
LAUNCHER = os.path.join(REPO, "tests", "realistic", "launch_y13.py")
KNOWN = "https://github.com/phamTuan207/computer-use-wayland.git"
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []

# (label, url, must_equal_pinned)
UNIT_CASES = [
    ("exact pinned URL", KNOWN, True),
    ("SSH form with .git",
     "git@github.com:phamTuan207/computer-use-wayland.git", True),
    ("SSH form without .git",
     "git@github.com:phamTuan207/computer-use-wayland", True),
    ("trailing slash + .git",
     "https://github.com/phamTuan207/computer-use-wayland.git/", True),
    ("no .git",
     "https://github.com/phamTuan207/computer-use-wayland", True),
    ("wrong-case scheme + host",
     "HTTPS://GITHUB.COM/phamTuan207/computer-use-wayland.git", True),
    ("SSH trailing slash",
     "git@github.com:phamTuan207/computer-use-wayland.git/", True),
    ("http (not https)",
     "http://github.com/phamTuan207/computer-use-wayland.git", False),
    ("attacker owner",
     "https://github.com/attacker/computer-use-wayland.git", False),
    ("wrong repo name",
     "https://github.com/phamTuan207/other-repo.git", False),
    ("wrong host",
     "https://gitlab.com/phamTuan207/computer-use-wayland.git", False),
]

# (label, url, must_pass)
DRIVER_CASES = [
    ("SSH form passes",
     "git@github.com:phamTuan207/computer-use-wayland.git", True),
    ("trailing slash passes",
     "https://github.com/phamTuan207/computer-use-wayland.git/", True),
    ("no .git passes",
     "https://github.com/phamTuan207/computer-use-wayland", True),
    ("wrong-case host passes",
     "HTTPS://GITHUB.COM/phamTuan207/computer-use-wayland.git", True),
    ("http refuses",
     "http://github.com/phamTuan207/computer-use-wayland.git", False),
    ("attacker fork refuses",
     "https://github.com/attacker/computer-use-wayland.git", False),
]


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def sh(cmd, cwd=None, env=None, timeout=120):
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
    log("A5b START")
    # --- unit layer ---
    ns = extract_lib.extract_funcs(
        LAUNCHER, ("_normalize_remote_url",), ("KNOWN_REMOTE_URL",),
        extra={"_SHIP_DIR": CLEAN, "SHIP_DIR": CLEAN})
    norm = ns["_normalize_remote_url"]
    pinned = norm(KNOWN)
    check("A5b pinned URL normalizes to itself",
          norm(KNOWN) == pinned, f"norm(pinned)={pinned!r}")
    for label, url, want in UNIT_CASES:
        got = norm(url)
        eq = got == pinned
        check(f"A5b unit {label}",
              eq == want,
              f"norm({url!r}) = {got!r}, equals pinned: {eq}, "
              f"want {want}")
    # --- driver layer: synthetic clone, origin URL per case ---
    if os.path.exists(A5B):
        shutil.rmtree(A5B)
    os.makedirs(A5B)
    bare = os.path.join(A5B, "synth.git")
    clone = os.path.join(A5B, "synth-clone")
    sh(["git", "init", "--bare", "-q", bare])
    sh(["git", "clone", "-q", bare, clone])
    sh(["git", "-C", clone, "config", "user.email",
        "verify@example.local"])
    sh(["git", "-C", clone, "config", "user.name", "Y13g Verifier"])
    for label, url, want_pass in DRIVER_CASES:
        proc, _ = sh(["git", "-C", clone, "remote", "set-url",
                      "origin", url])
        assert proc.returncode == 0, f"set-url failed: {proc.stderr}"
        proc, dt = sh([sys.executable,
                       os.path.join(HERE, "launcher_check_driver.py"),
                       "--ship-dir", CLEAN, "--check", "remote",
                       "--repo", clone], timeout=120)
        out = proc.stdout + proc.stderr
        if want_pass:
            ok = proc.returncode == 0
        else:
            ok = (proc.returncode == 2
                  and "not the known repo" in out)
        check(f"A5b driver {label}",
              ok,
              f"driver --check remote rc={proc.returncode} ({dt:.1f}s) "
              f"url={url} "
              f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A5b DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

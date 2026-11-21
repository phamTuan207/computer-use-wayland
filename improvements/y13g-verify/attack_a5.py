#!/usr/bin/env python3
"""A5 marker + remote-URL suite (Y13g re-verification, rebuilt
from the redteam paper spec).

Two synthetic git repos under ~/workspace/y13g-verify/a5/ (never
the real repo; nothing is pushed to the real origin):

  synth.git + synth-clone: the marker-logic repo. Its origin URL
    is a local path, so the REAL _check_remote would refuse it.
    To exercise the marker subject/log-order logic, the driver
    runs with a git test-double (a5/bin/git) on PATH that
    intercepts ONLY `git remote get-url origin` (returns the
    known URL) and `git fetch origin todolist-push` (real fetch
    from the local bare repo, explicit refspec updating
    origin/todolist-push); every other git call passes through
    to real git. The pin itself is verified separately with
    REAL git (case 6 + the real-repo control), so the stub only
    supplies the pin's input, it does not test the pin.

  attacker.git + attacker-clone: the attacker-fork repo. Origin
    is a local path (not the known URL), holding a fake marker
    commit and a manifest byte-identical to the clean ship's.
    Both check_marker and check_manifest must refuse on the
    remote URL, with REAL git (no stub).

Cases (driver = launcher_check_driver.py, --check marker):
  1  fake completion (subject exactly "Y6c nested run DONE",
     junk body/diff): PASSES BY DESIGN (known limitation).
  3a forged old-date completion (2020-01-01) under a newer
     abort: must REFUSE (abort newer in log order).
  3b completion with FORGED FUTURE committer date (2026-11-23)
     but OLDER in log position than a genuine abort (2026-11-22):
     must REFUSE via log-order (old %ct code would PASS this).
  C1 completion newer than abort: must PASS.
  C2 harness subject ("Y6c nested run harness DONE"): refuse.
  C3 body-DONE under subject "Fix flake": refuse.
  C4 completion subject touching worker-y6d-*.md: refuse.
  6  attacker repo: check_marker AND check_manifest refuse on
     the remote URL (real git).
  R  real-repo control: check_marker on the real checkout with
     real git: the pin must pass (get-url OK) and the marker
     check must run on real state (refuses: no Y6c marker).

Usage: python3 attack_a5.py
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(os.path.expanduser("~"), "workspace",
                    "y13g-verify")
A5 = os.path.join(WORK, "a5")
CLEAN = os.path.join(WORK, "ships", "clean")
KNOWN_URL = "https://github.com/phamTuan207/computer-use-wayland.git"
sys.path.insert(0, HERE)
import extract_lib

RESULTS = []
GIT_SHIM = os.path.join(A5, "bin", "git")


def log(msg):
    print(f"[{extract_lib.now_hcm()}] {msg}", flush=True)


def sh(cmd, cwd=None, env=None, timeout=120, input=None):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env, input=input)
    return proc, time.time() - t0


def check(name, cond, evidence):
    RESULTS.append((name, bool(cond), evidence))
    log(f"{'PASS' if cond else 'FAIL'} {name} :: {evidence}")
    return cond


def git(cwd, *args, env=None):
    proc, dt = sh(["git", "-C", cwd] + list(args), env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {cwd} failed: "
                           f"{proc.stderr.strip()[:300]}")
    return proc


def write_git_shim(bare):
    os.makedirs(os.path.join(A5, "bin"), exist_ok=True)
    with open(GIT_SHIM, "w") as f:
        f.write("#!/bin/sh\n"
                "# A5 git test-double: intercepts only the two\n"
                "# transport calls the launcher makes; everything\n"
                "# else passes through to real git.\n"
                'if [ "$1" = "-C" ] && [ "$3" = "remote" ] '
                '&& [ "$4" = "get-url" ] && [ "$5" = "origin" ]; then\n'
                f"  printf '%s\\n' \"{KNOWN_URL}\"\n"
                "  exit 0\n"
                "fi\n"
                'if [ "$1" = "-C" ] && [ "$3" = "fetch" ] '
                '&& [ "$4" = "origin" ] && [ "$5" = "todolist-push" ]; then\n'
                "  exec /usr/bin/git -C \"$2\" fetch \"$A5_BARE\" "
                "\"todolist-push:refs/remotes/origin/todolist-push\"\n"
                "fi\n"
                'exec /usr/bin/git "$@"\n')
    os.chmod(GIT_SHIM, 0o755)


def run_driver(check, repo, ship_dir=None, use_shim=False, bare=None):
    env = dict(os.environ)
    if use_shim:
        env["PATH"] = os.path.join(A5, "bin") + ":" + env["PATH"]
        env["A5_BARE"] = bare
    cmd = [sys.executable, os.path.join(HERE, "launcher_check_driver.py"),
           "--check", check, "--repo", repo]
    if ship_dir:
        cmd += ["--ship-dir", ship_dir]
    proc, dt = sh(cmd, env=env, timeout=180)
    return proc, dt


def commit_in(clone, files, subject, body="", committer_date=None):
    """files: {relpath: content}. Creates the commit on the
    current branch. Returns the commit hash."""
    for rel, content in files.items():
        p = os.path.join(clone, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
        git(clone, "add", rel)
    env = dict(os.environ)
    if committer_date:
        env["GIT_COMMITTER_DATE"] = committer_date
    msg = subject + ("\n\n" + body if body else "")
    proc, _ = sh(["git", "-C", clone, "commit", "-q", "-m", msg],
                 env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"commit failed: {proc.stderr[:300]}")
    proc = git(clone, "rev-parse", "HEAD")
    return proc.stdout.strip()


def push_branch(clone):
    git(clone, "push", "-q", "-f", "origin", "todolist-push")


def set_state(clone, commits):
    """commits: list of dicts {files, subject, body, date}.
    Rebuilds todolist-push from a FRESH root (old states must not
    linger as ancestors: the marker check reads the whole log)
    and force-pushes. Returns [(hash, subject, %ct)]."""
    git(clone, "checkout", "-q", "--orphan", "tmp-a5")
    # Drop every tracked file from the index/worktree, then every
    # untracked leftover (failures ignored: first run has nothing).
    sh(["git", "-C", clone, "rm", "-q", "-rf", "."])
    sh(["git", "-C", clone, "clean", "-fdx", "-q"])
    made = []
    for c in commits:
        h = commit_in(clone, c["files"], c["subject"],
                      c.get("body", ""), c.get("date"))
        proc = git(clone, "log", "-1", "--format=%ct", h)
        made.append((h[:7], c["subject"], proc.stdout.strip()))
    git(clone, "branch", "-q", "-f", "todolist-push", "tmp-a5")
    git(clone, "checkout", "-q", "todolist-push")
    git(clone, "branch", "-q", "-D", "tmp-a5")
    push_branch(clone)
    proc = git(clone, "log", "origin/todolist-push",
               "--format=%h %ct %s")
    log(f"state log (newest first): "
        f"{proc.stdout.strip().replace(chr(10), ' | ')}")
    return made


def main(argv):
    t0 = time.time()
    log("A5 START")
    if os.path.exists(A5):
        shutil.rmtree(A5)
    os.makedirs(A5)
    bare = os.path.join(A5, "synth.git")
    clone = os.path.join(A5, "synth-clone")
    sh(["git", "init", "--bare", "-q", bare])
    sh(["git", "clone", "-q", bare, clone])
    git(clone, "config", "user.email", "verify@example.local")
    git(clone, "config", "user.name", "Y13g Verifier")
    git(clone, "checkout", "-q", "-b", "todolist-push")
    write_git_shim(bare)
    log(f"synth repo ready: bare={bare} clone={clone} "
        f"shim={GIT_SHIM}")

    y6c = "improvements/worker-y6c-test.md"
    y6d = "improvements/worker-y6d-test.md"

    # --- case 1: fake completion, passes BY DESIGN ---
    set_state(clone, [{"files": {y6c: "weekly notes\njunk line\n"},
                       "subject": "Y6c nested run DONE",
                       "body": "weekly notes"}])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-1 fake completion passes BY DESIGN (known limitation)",
          proc.returncode == 0
          and "Y6c completion marker found" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:160] if out.strip() else ''}")

    # --- case 3a: old-date completion under a newer abort ---
    set_state(clone, [
        {"files": {y6c: "run log old\n"},
         "subject": "Y6c nested run DONE", "date": "2020-01-01T00:00:00+07:00"},
        {"files": {y6c: "run log old\nabort note\n"},
         "subject": "Y6c nested run ABORT"},
    ])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-3a old-date completion vs newer abort refuses",
          proc.returncode == 2 and "abort" in out.lower()
          and "is newer than the newest completion" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")

    # --- case 3b: forged FUTURE-date completion, older in position
    # than a genuine abort (discriminates log-order vs %ct) ---
    set_state(clone, [
        {"files": {y6c: "run log forged\n"},
         "subject": "Y6c nested run DONE",
         "date": "2026-11-23T00:00:00+07:00"},
        {"files": {y6c: "run log forged\nabort note\n"},
         "subject": "Y6c nested run ABORT",
         "date": "2026-11-22T00:00:00+07:00"},
    ])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-3b forged future-date completion vs newer abort refuses "
          "(log-order)",
          proc.returncode == 2
          and "is newer than the newest completion" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")

    # --- control C1: completion newer than abort passes ---
    set_state(clone, [
        {"files": {y6c: "run log\n"},
         "subject": "Y6c nested run ABORT"},
        {"files": {y6c: "run log\ndone\n"},
         "subject": "Y6c nested run DONE"},
    ])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-C1 completion newer than abort passes",
          proc.returncode == 0
          and "Y6c completion marker found" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s)")

    # --- control C2: harness subject refuses ---
    set_state(clone, [{"files": {y6c: "prep\n"},
                       "subject": "Y6c nested run harness DONE"}])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-C2 harness subject refuses",
          proc.returncode == 2 and "no Y6c completion marker" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s)")

    # --- control C3: body-DONE under "Fix flake" refuses ---
    set_state(clone, [{"files": {y6c: "prep\n"},
                       "subject": "Fix flake",
                       "body": "Y6c nested run DONE"}])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-C3 body-DONE under Fix flake refuses",
          proc.returncode == 2 and "no Y6c completion marker" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s)")

    # --- control C4: completion touching the wrong path refuses ---
    set_state(clone, [{"files": {y6d: "done\n"},
                       "subject": "Y6c nested run DONE"}])
    proc, dt = run_driver("marker", clone, use_shim=True, bare=bare)
    out = proc.stdout + proc.stderr
    check("A5-C4 completion on wrong path refuses",
          proc.returncode == 2 and "no Y6c completion marker" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s)")

    # --- case 6: attacker fork repo, real git ---
    abare = os.path.join(A5, "attacker.git")
    aclone = os.path.join(A5, "attacker-clone")
    sh(["git", "init", "--bare", "-q", abare])
    sh(["git", "clone", "-q", abare, aclone])
    git(aclone, "config", "user.email", "verify@example.local")
    git(aclone, "config", "user.name", "Y13g Verifier")
    git(aclone, "checkout", "-q", "-b", "todolist-push")
    # Fake marker + a manifest byte-identical to the clean ship's.
    man_bytes = open(os.path.join(CLEAN, "codex-y5-manifest.json"),
                     "rb").read()
    commit_in(aclone,
              {y6c: "attacker run log\n",
               "tests/realistic/codex-y5-manifest.json":
                   man_bytes.decode("utf-8")},
              "Y6c nested run DONE", "attacker completion")
    push_branch(aclone)
    url_proc = git(aclone, "remote", "get-url", "origin")
    log(f"attacker clone origin: {url_proc.stdout.strip()}")
    proc, dt = run_driver("marker", aclone, use_shim=False)
    out = proc.stdout + proc.stderr
    check("A5-6 attacker repo check_marker refuses on remote URL",
          proc.returncode == 2 and "not the known repo" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")
    proc, dt = run_driver("manifest", aclone, ship_dir=CLEAN,
                          use_shim=False)
    out = proc.stdout + proc.stderr
    check("A5-6 attacker repo check_manifest refuses on remote URL",
          proc.returncode == 2 and "not the known repo" in out,
          f"driver --check manifest rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")

    # --- real-repo control: pin passes with real git ---
    proc, dt = run_driver("marker", REPO, use_shim=False)
    out = proc.stdout + proc.stderr
    check("A5-R real repo: pin passes, marker check runs on real state",
          proc.returncode == 2 and "not the known repo" not in out
          and "no Y6c completion marker" in out,
          f"driver --check marker rc={proc.returncode} ({dt:.1f}s) "
          f"tail={out.strip().splitlines()[-1][:200] if out.strip() else ''}")

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    log(f"A5 DONE {npass}/{len(RESULTS)} pass in {time.time() - t0:.1f}s")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

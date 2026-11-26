#!/usr/bin/env python3
"""Clean-checkout ledger validation (R19 posture, team decision 27/11/2026).

Validators (validate-ledger.py, ledger-cross-check.py) never execute
from inside the flagged worktree: the execution-risk guard blocks
running worktree content (git hooks/filters can run code), and the
checked and the checker must not share a writable tree.

This script copies the two stdlib-only validators and all inputs
(verdict dir first, order file, ledger last, as one read-only
snapshot) into a scratch directory outside the flagged tree, runs
the validators from the scratch copies, and prints both exit codes,
the todolist-push head SHA at validation time, the ledger row count,
and the sha256 of each validator copy that ran.

Invocation discipline: copy this script out of the flagged tree
first, then run the copy, e.g.
  cp rung3-ci/clean-validate-ledger.py /tmp/
  python3 /tmp/clean-validate-ledger.py --repo-root ~/workspace/r3l3-run-wt

Exit 0 only when both validators exit 0; else 1. Stdlib only.
No personal info in this file.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

VALIDATORS = ("validate-ledger.py", "ledger-cross-check.py")
DEFAULT_BRANCH = "todolist-push"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_readonly(src, dst):
    shutil.copy2(src, dst)
    os.chmod(dst, 0o444)


def copytree_readonly(src, dst):
    shutil.copytree(src, dst)
    for root, dirs, files in os.walk(dst):
        for name in files:
            os.chmod(os.path.join(root, name), 0o444)
        os.chmod(root, 0o555)


def remove_tree(path):
    def onexc(func, p, exc):
        os.chmod(p, 0o755)
        func(p)
    shutil.rmtree(path, onexc=onexc)


def remote_url_from_config(repo_root):
    """Best-effort origin URL from the repo's git config (plain read)."""
    git_path = os.path.join(repo_root, ".git")
    git_dir = git_path
    if os.path.isfile(git_path):
        with open(git_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("gitdir:"):
                    git_dir = line.split(":", 1)[1].strip()
                    break
    commondir = os.path.join(git_dir, "commondir")
    if os.path.isfile(commondir):
        with open(commondir, encoding="utf-8") as f:
            common = f.read().strip()
        if not os.path.isabs(common):
            common = os.path.normpath(os.path.join(git_dir, common))
        git_dir = common
    config = os.path.join(git_dir, "config")
    try:
        with open(config, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    m = re.search(r'\[remote "origin"\][^\[]*?^\s*url\s*=\s*(\S+)',
                  text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def head_sha(remote_url, branch, cwd):
    if not remote_url:
        return "unknown (no remote url)"
    try:
        out = subprocess.run(
            ["git", "ls-remote", remote_url, "refs/heads/" + branch],
            cwd=cwd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "unknown (ls-remote failed: %s)" % e
    if out.returncode != 0 or not out.stdout.strip():
        return "unknown (ls-remote rc=%d)" % out.returncode
    return out.stdout.split()[0]


def run_clean_validation(repo_root, ledger=None, verdict_dir=None,
                         order_file=None, remote_url=None,
                         branch=DEFAULT_BRANCH, keep_scratch=False):
    repo_root = os.path.expanduser(repo_root)
    ledger = ledger or os.path.join(
        repo_root, "rung3-run-log", "R3-L3-grades.jsonl")
    verdict_dir = verdict_dir or os.path.expanduser(
        "~/workspace/rung3-verdicts")
    order_file = order_file or os.path.join(
        repo_root, "rung3-run-log", "thu-tu-chay.txt")
    scratch = tempfile.mkdtemp(prefix="clean-validate-")
    result = {"scratch": scratch}
    try:
        # Validators: copied out, executed only from scratch.
        hashes = {}
        for name in VALIDATORS:
            src = os.path.join(repo_root, "rung3-ci", name)
            dst = os.path.join(scratch, name)
            copy_readonly(src, dst)
            hashes[name] = sha256_of(dst)
        result["validator_sha256"] = hashes
        # Inputs as one snapshot: verdict dir first, ledger last.
        s_verdicts = os.path.join(scratch, "verdicts")
        if os.path.isdir(verdict_dir):
            copytree_readonly(verdict_dir, s_verdicts)
        else:
            os.makedirs(s_verdicts)
            result["verdict_dir_missing"] = verdict_dir
        s_order = os.path.join(scratch, "thu-tu-chay.txt")
        copy_readonly(order_file, s_order)
        s_ledger = os.path.join(scratch, "R3-L3-grades.jsonl")
        copy_readonly(ledger, s_ledger)
        with open(s_ledger, encoding="utf-8") as f:
            result["rows"] = sum(1 for ln in f if ln.strip())
        # Head SHA at validation time (git runs in scratch, never in
        # the flagged tree).
        url = remote_url or remote_url_from_config(repo_root)
        result["head_sha"] = head_sha(url, branch, scratch)
        v = subprocess.run(
            [sys.executable, os.path.join(scratch, "validate-ledger.py"),
             s_ledger], capture_output=True, text=True)
        result["validate_rc"] = v.returncode
        result["validate_out"] = (v.stdout + v.stderr).strip()
        c = subprocess.run(
            [sys.executable,
             os.path.join(scratch, "ledger-cross-check.py"),
             s_ledger, s_verdicts, s_order],
            capture_output=True, text=True)
        result["cross_rc"] = c.returncode
        result["cross_out"] = (c.stdout + c.stderr).strip()
        return result
    finally:
        if not keep_scratch:
            remove_tree(scratch)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", required=True,
                    help="repo/worktree holding rung3-ci/ and rung3-run-log/")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--verdict-dir", default=None)
    ap.add_argument("--order-file", default=None)
    ap.add_argument("--remote-url", default=None)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--keep-scratch", action="store_true")
    ap.add_argument("--json", action="store_true",
                    help="print the result dict as JSON")
    args = ap.parse_args()
    r = run_clean_validation(
        args.repo_root, ledger=args.ledger,
        verdict_dir=args.verdict_dir, order_file=args.order_file,
        remote_url=args.remote_url, branch=args.branch,
        keep_scratch=args.keep_scratch)
    if args.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print("clean-validate: head %s" % r["head_sha"])
        print("clean-validate: ledger rows %d" % r["rows"])
        for name in VALIDATORS:
            print("clean-validate: %s sha256 %s"
                  % (name, r["validator_sha256"][name]))
        print("clean-validate: validate-ledger exit %d" % r["validate_rc"])
        print(r["validate_out"])
        print("clean-validate: ledger-cross-check exit %d" % r["cross_rc"])
        print(r["cross_out"])
        if args.keep_scratch:
            print("clean-validate: scratch kept at %s" % r["scratch"])
    return 0 if (r["validate_rc"] == 0 and r["cross_rc"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())

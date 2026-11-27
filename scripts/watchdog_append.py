#!/usr/bin/env python3
"""Watchdog rolling branch: append-only log appends (M28a).

Replaces one branch + one PR per watchdog tick with one rolling
branch per lane that only ever moves forward:

  branch:  watchdog/<lane>          (e.g. watchdog/clone2)
  layout:  entries/<utc>-<lane>-<rand>.md, one file per tick

Appends use git plumbing (hash-object, temp index, commit-tree)
so the caller's working tree and index are never touched. The
push is a plain fast-forward push: this script has no force-push
path, and published history is never rewritten. When a push is
rejected because another writer appended first, the append is
retried on top of the new tip (entry filenames are unique, so a
retry never conflicts). After --retries failed attempts the
append fails loudly and nothing is lost silently: the entry text
stays with the caller.

Before anything is committed, the entry is scanned with
rung3-ci/pii-scan.py when that file exists in the repo (or at
--pii-scan). A hit aborts the append. Watchdog entries are
status summaries; they must never carry raw personal data,
credentials, private URLs, or machine secrets.

Usage:
  python3 scripts/watchdog_append.py append --lane clone2 \\
      --repo . [--remote origin] [--entry-file entry.md] \\
      [--message TEXT] [--retries 5]
  (entry text comes from --entry-file, or stdin when omitted)

  python3 scripts/watchdog_append.py rollup --lane clone2 \\
      --repo . --out watchdog-log.md [--remote origin]

Rollup concatenates every entry on the branch in filename order
into one file, ready to be committed on a normal branch off main
as the periodic rollup PR. The rolling branch itself is never
merged; it is the durable append-only record.

Exit 0 on success. Prints APPENDED: <branch> <commit> <entry>
or ROLLED-UP: <count> entries -> <out>.
No personal info in this file.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone


def git(repo, *args, env_extra=None, check=True, input_text=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        ["git", "-C", repo] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, input=input_text)
    if check and proc.returncode != 0:
        raise SystemExit(
            "git %s failed (rc=%d): %s" % (
                " ".join(args), proc.returncode, proc.stderr.strip()))
    return proc


def remote_tip(repo, remote, branch):
    proc = git(repo, "ls-remote", remote, "refs/heads/" + branch,
               check=False)
    if proc.returncode != 0:
        raise SystemExit("ls-remote failed: " + proc.stderr.strip())
    line = proc.stdout.strip()
    return line.split()[0] if line else None


def fetch_tip(repo, remote, branch):
    tip = remote_tip(repo, remote, branch)
    if tip is None:
        return None
    git(repo, "fetch", "--quiet", remote,
        "refs/heads/%s:refs/watchdog-fetch/%s" % (branch, branch))
    return tip


def pii_gate(repo, entry_text, pii_scan_arg):
    if pii_scan_arg:
        scanner = pii_scan_arg
    else:
        scanner = os.path.join(repo, "rung3-ci", "pii-scan.py")
    if not os.path.isfile(scanner):
        print("warning: pii-scan not found at %s; "
              "appending without the PII gate" % scanner,
              file=sys.stderr)
        return
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "entry.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(entry_text)
        proc = subprocess.run(
            [sys.executable, scanner, tmp],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise SystemExit(
            "PII gate refused the entry:\n" + proc.stdout.strip())


def entry_name(lane):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return "entries/%s-%s-%s.md" % (stamp, lane, uuid.uuid4().hex[:6])


def build_commit(repo, tip, name, entry_text, message):
    with tempfile.TemporaryDirectory() as tmp:
        index = os.path.join(tmp, "index")
        env = {"GIT_INDEX_FILE": index}
        if tip:
            git(repo, "read-tree", tip, env_extra=env)
        else:
            git(repo, "read-tree", "--empty", env_extra=env)
        blob = git(repo, "hash-object", "-w", "--stdin",
                   input_text=entry_text).stdout.strip()
        git(repo, "update-index", "--add", "--cacheinfo",
            "100644,%s,%s" % (blob, name), env_extra=env)
        tree = git(repo, "write-tree", env_extra=env).stdout.strip()
    args = ["commit-tree", tree]
    if tip:
        args += ["-p", tip]
    args += ["-m", message]
    return git(repo, *args).stdout.strip()


def cmd_append(args):
    branch = args.branch or ("watchdog/" + args.lane)
    if args.entry_file:
        with open(args.entry_file, encoding="utf-8") as fh:
            entry_text = fh.read()
    else:
        entry_text = sys.stdin.read()
    if not entry_text.strip():
        raise SystemExit("empty entry; nothing appended")
    if not entry_text.endswith("\n"):
        entry_text += "\n"
    pii_gate(args.repo, entry_text, args.pii_scan)
    name = entry_name(args.lane)
    message = args.message or ("watchdog %s: append %s"
                                % (args.lane, os.path.basename(name)))
    for attempt in range(1, args.retries + 1):
        tip = fetch_tip(args.repo, args.remote, branch)
        commit = build_commit(args.repo, tip, name, entry_text, message)
        proc = git(args.repo, "push", args.remote,
                   "%s:refs/heads/%s" % (commit, branch), check=False)
        if proc.returncode == 0:
            print("APPENDED: %s %s %s" % (branch, commit, name))
            return 0
        if "non-fast-forward" in proc.stderr or "rejected" in proc.stderr:
            print("push rejected (attempt %d/%d); another writer "
                  "appended first, retrying on the new tip"
                  % (attempt, args.retries), file=sys.stderr)
            continue
        raise SystemExit("push failed: " + proc.stderr.strip())
    raise SystemExit(
        "append failed after %d attempts; entry NOT recorded, "
        "retry the append" % args.retries)


def cmd_rollup(args):
    branch = args.branch or ("watchdog/" + args.lane)
    tip = fetch_tip(args.repo, args.remote, branch)
    if tip is None:
        raise SystemExit("branch %s does not exist on %s"
                         % (branch, args.remote))
    listing = git(args.repo, "ls-tree", "-r", "--name-only",
                  tip, "entries/").stdout.split()
    names = sorted(n for n in listing if n.endswith(".md"))
    parts = []
    for name in names:
        parts.append(git(args.repo, "cat-file", "-p",
                         "%s:%s" % (tip, name)).stdout)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print("ROLLED-UP: %d entries -> %s" % (len(names), args.out))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_append = sub.add_parser("append")
    ap_append.add_argument("--lane", required=True)
    ap_append.add_argument("--repo", default=".")
    ap_append.add_argument("--remote", default="origin")
    ap_append.add_argument("--branch", default=None)
    ap_append.add_argument("--entry-file", default=None)
    ap_append.add_argument("--message", default=None)
    ap_append.add_argument("--retries", type=int, default=5)
    ap_append.add_argument("--pii-scan", default=None)
    ap_append.set_defaults(func=cmd_append)
    ap_rollup = sub.add_parser("rollup")
    ap_rollup.add_argument("--lane", required=True)
    ap_rollup.add_argument("--repo", default=".")
    ap_rollup.add_argument("--remote", default="origin")
    ap_rollup.add_argument("--branch", default=None)
    ap_rollup.add_argument("--out", required=True)
    ap_rollup.set_defaults(func=cmd_rollup)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

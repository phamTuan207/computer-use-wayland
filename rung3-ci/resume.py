#!/usr/bin/env python3
"""Rung 3 resume mechanism.

Run state is thu-tu-chay.txt (the fixed run order, one task ID per
line, # comments allowed) plus the run ledger
rung3-run-log/R3-L3-grades.jsonl (one row per graded task).

Commands:
  next      Print the next ungraded task in run order and the evidence
            state for it (folder present, manifest present, file count,
            manifest status). Exit 0.
  status    Print counts: ordered, graded, remaining, next task.
  checkpoint <TASK-ID>
            Verify the checkpoint for a graded task: the ledger row
            exists, the evidence folder has manifest.json, and the
            manifest hash matches the ledger row. A checkpoint is made
            after every task by running collect-evidence.py (writes
            the manifest) and appending the ledger row; this command
            proves the checkpoint holds.

A restart is a new run code with the old results preserved as a
record, never silently merged.

Usage:
  python3 rung3-ci/resume.py next [--state-dir DIR] [--evidence-root DIR]
  python3 rung3-ci/resume.py status [--state-dir DIR]
  python3 rung3-ci/resume.py checkpoint R3-007 [--state-dir DIR]
      [--evidence-root DIR]
State dir defaults to rung3-run-log/ in the repo. Evidence root
defaults to ~/rung3-chung-cu.
No personal info in this file.
"""
import argparse
import hashlib
import json
import os
import re
import sys


def load_order(state_dir):
    path = os.path.join(state_dir, "thu-tu-chay.txt")
    order = []
    if not os.path.isfile(path):
        return order, path
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = line.split()
        if tokens and all(
                re.fullmatch(r"R3-[0-9]{3}|DP-[0-9]{2}", t) for t in tokens):
            order.extend(tokens)
    return order, path


def load_graded(state_dir):
    path = os.path.join(state_dir, "R3-L3-grades.jsonl")
    graded = {}
    if not os.path.isfile(path):
        return graded, path
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("test_row"):
                continue
            graded[row.get("task_id")] = row
    return graded, path


def evidence_state(ev_root, task):
    folder = os.path.join(ev_root, task)
    man_path = os.path.join(folder, "manifest.json")
    state = {"folder": folder, "exists": os.path.isdir(folder),
             "files": 0, "manifest": False, "manifest_status": None,
             "manifest_sha256": None}
    if state["exists"]:
        names = [n for n in os.listdir(folder)
                 if os.path.isfile(os.path.join(folder, n))]
        state["files"] = len(names)
    if os.path.isfile(man_path):
        try:
            man = json.load(open(man_path, encoding="utf-8"))
            state["manifest"] = True
            state["manifest_status"] = man.get("status")
            state["manifest_sha256"] = man.get("manifest_sha256")
        except (json.JSONDecodeError, OSError):
            state["manifest"] = True
            state["manifest_status"] = "UNREADABLE"
    return state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["next", "status", "checkpoint"])
    ap.add_argument("task", nargs="?", default=None)
    ap.add_argument("--state-dir", default=None)
    ap.add_argument("--evidence-root", default=None)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_dir = args.state_dir or os.path.join(root, "rung3-run-log")
    ev_root = args.evidence_root or os.path.expanduser("~/rung3-chung-cu")
    order, order_path = load_order(state_dir)
    graded, ledger_path = load_graded(state_dir)
    if not order:
        print("FAIL: no run order in %s (thu-tu-chay.txt missing or empty)"
              % order_path)
        return 1

    if args.command == "status":
        remaining = [t for t in order if t not in graded]
        nxt = remaining[0] if remaining else None
        print("ORDER: %d tasks in %s" % (len(order), order_path))
        print("GRADED: %d tasks in %s" % (len(graded), ledger_path))
        print("REMAINING: %d" % len(remaining))
        print("NEXT: %s" % (nxt or "ALL GRADED"))
        return 0

    if args.command == "next":
        for task in order:
            if task not in graded:
                ev = evidence_state(ev_root, task)
                print("NEXT: %s" % task)
                print("EVIDENCE: folder %s (exists=%s, %d file(s))"
                      % (ev["folder"], ev["exists"], ev["files"]))
                print("MANIFEST: present=%s status=%s sha256=%s"
                      % (ev["manifest"], ev["manifest_status"],
                         ev["manifest_sha256"]))
                return 0
        print("NEXT: ALL GRADED (%d tasks)" % len(order))
        return 0

    # checkpoint
    task = args.task
    if task not in graded:
        print("FAIL: %s has no ledger row in %s" % (task, ledger_path))
        return 1
    ev = evidence_state(ev_root, task)
    if not ev["manifest"]:
        print("FAIL: %s graded but no manifest.json in %s"
              % (task, ev["folder"]))
        return 1
    want = graded[task].get("evidence_manifest_hash")
    if ev["manifest_sha256"] != want:
        print("FAIL: manifest hash mismatch for %s: folder=%s ledger=%s"
              % (task, ev["manifest_sha256"], want))
        return 1
    print("PASS: checkpoint holds for %s: ledger row present, manifest "
          "status=%s, hash %s" % (task, ev["manifest_status"], want))
    return 0


if __name__ == "__main__":
    sys.exit(main())

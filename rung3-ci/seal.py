#!/usr/bin/env python3
"""One-pass seal wrapper (M2, wrapper form only).

Runs the existing seal sequence in order and stops at the first
failure:

  1. collect-evidence.py <TASK>   (verify evidence, write manifest)
  2. snapshot.py <EVIDENCE-DIR>   (copy to snapshot dir, own manifest)
  3. manifest-gate.py --snapshot <dir> --task <TASK>  (verify)

This wrapper reimplements nothing: it invokes the three tools as
subprocesses, echoes their output, and propagates the first
non-zero exit code. The gate remains separately runnable over the
wrapper's output (a merged rewrite would be self-certification).
Collapsing the sequence to one command structurally removes the
seam traps (wrong order, stale manifest copied, gate run against
the live folder) that lived between the manual steps.

Usage:
  python3 rung3-ci/seal.py <TASK-ID> [--evidence-root DIR]
      [--snapshot-root DIR] [--label STR] [--name NAME]
      [--requirements FILE] [--fixture-source DIR]
      [--window-start ISO] [--window-end ISO]

Exit 0 only when all three steps pass. Prints SEALED: <snapshot>
on success.
No personal info in this file.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run_step(argv):
    print("+ " + " ".join(argv), flush=True)
    proc = subprocess.run([sys.executable] + argv,
                          stdout=subprocess.PIPE, text=True)
    sys.stdout.write(proc.stdout)
    sys.stdout.flush()
    return proc.returncode, proc.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--evidence-root", default=None)
    ap.add_argument("--snapshot-root", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--requirements", default=None)
    ap.add_argument("--fixture-source", default=None)
    ap.add_argument("--window-start", default=None)
    ap.add_argument("--window-end", default=None)
    args = ap.parse_args()

    collect = [os.path.join(HERE, "collect-evidence.py"), args.task]
    if args.evidence_root:
        collect += ["--evidence-root", args.evidence_root]
    if args.requirements:
        collect += ["--requirements", args.requirements]
    if args.fixture_source:
        collect += ["--fixture-source", args.fixture_source]
    rc, _ = run_step(collect)
    if rc != 0:
        print("SEAL FAIL: collect step failed (exit %d)" % rc)
        return rc

    ev_root = args.evidence_root or os.path.expanduser("~/rung3-chung-cu")
    ev_dir = os.path.join(ev_root, args.task)
    snap = [os.path.join(HERE, "snapshot.py"), ev_dir]
    if args.snapshot_root:
        snap += ["--snapshot-root", args.snapshot_root]
    if args.label:
        snap += ["--label", args.label]
    if args.name:
        snap += ["--name", args.name]
    rc, out = run_step(snap)
    if rc != 0:
        print("SEAL FAIL: snapshot step failed (exit %d)" % rc)
        return rc
    dest = None
    for line in out.splitlines():
        if line.startswith("SNAPSHOT: "):
            dest = line[len("SNAPSHOT: "):].strip()
    if not dest:
        print("SEAL FAIL: snapshot step printed no SNAPSHOT: path")
        return 1

    gate = [os.path.join(HERE, "manifest-gate.py"),
            "--snapshot", dest, "--task", args.task]
    if args.requirements:
        gate += ["--requirements", args.requirements]
    if args.window_start:
        gate += ["--window-start", args.window_start]
    if args.window_end:
        gate += ["--window-end", args.window_end]
    rc, _ = run_step(gate)
    if rc != 0:
        print("SEAL FAIL: gate step failed (exit %d)" % rc)
        return rc
    print("SEALED: %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Pre-freeze gate wrapper (M11d, process + verify-list gate).

Runs the existing mechanical checks in order and stops at the
first failure:

  1. verify-list.py      (list structure, counts, keys, freeze hash)
  2. check-key-hash.py   (key JSON sha256 vs thu-tu-chay.txt)
  3. triage record check (only with --triage-record: the record
     must exist and carry the mandatory bar, classification and
     freeze decision sections from pre-freeze-triage.md)

This wrapper reimplements nothing: it invokes the two tools as
subprocesses, echoes their output, and propagates the first
non-zero exit code. The human triage itself is a procedure
(rung3-ci/pre-freeze-triage.md), not code; this gate only proves
the mechanical half and that the triage record was written.

Usage:
  python3 rung3-ci/pre-freeze-gate.py [--list PATH] [--frozen PATH]
      [--key-json PATH] [--key-md PATH] [--key PATH] [--state PATH]
      [--triage-record PATH]

Exit 0 only when every step passes. Prints PRE-FREEZE GATE: PASS
on success.
No personal info in this file.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

RECORD_HEADINGS = ("## Mandatory bar", "## Classification",
                   "## Freeze decision")


def run_step(argv):
    print("+ " + " ".join(argv), flush=True)
    proc = subprocess.run([sys.executable] + argv,
                          stdout=subprocess.PIPE, text=True)
    sys.stdout.write(proc.stdout)
    sys.stdout.flush()
    return proc.returncode


def check_record(path):
    if not os.path.isfile(path):
        print("FAIL: triage record missing: %s" % path)
        return 1
    text = open(path, encoding="utf-8").read()
    missing = [h for h in RECORD_HEADINGS if h not in text]
    if missing:
        print("FAIL: triage record %s missing sections: %s"
              % (path, missing))
        return 1
    print("PASS: triage record has mandatory bar, classification "
          "and freeze decision sections: %s" % path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", default=None)
    ap.add_argument("--frozen", default=None)
    ap.add_argument("--key-json", default=None)
    ap.add_argument("--key-md", default=None)
    ap.add_argument("--key", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--triage-record", default=None)
    args = ap.parse_args()

    verify = [os.path.join(HERE, "verify-list.py")]
    if args.list:
        verify += ["--list", args.list]
    if args.frozen:
        verify += ["--frozen", args.frozen]
    if args.key_json:
        verify += ["--key-json", args.key_json]
    if args.key_md:
        verify += ["--key-md", args.key_md]
    rc = run_step(verify)
    if rc != 0:
        print("PRE-FREEZE GATE FAIL: verify-list step failed "
              "(exit %d)" % rc)
        return rc

    keyhash = [os.path.join(HERE, "check-key-hash.py")]
    if args.key:
        keyhash += ["--key", args.key]
    if args.state:
        keyhash += ["--state", args.state]
    rc = run_step(keyhash)
    if rc != 0:
        print("PRE-FREEZE GATE FAIL: check-key-hash step failed "
              "(exit %d)" % rc)
        return rc

    if args.triage_record:
        rc = check_record(args.triage_record)
        if rc != 0:
            print("PRE-FREEZE GATE FAIL: triage-record step failed "
                  "(exit %d)" % rc)
            return rc

    print("PRE-FREEZE GATE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

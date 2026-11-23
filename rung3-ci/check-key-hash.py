#!/usr/bin/env python3
"""Rung 3 key file hash check.

Verifies the frozen key file docs/rung3-answer-keys.json against the
hash recorded in thu-tu-chay.txt (the run state file).

States:
  - key file missing: PENDING, exit 0. The key is not frozen yet.
    This is the expected state until the synthesis step writes it.
  - key file present, thu-tu-chay.txt missing or has no recorded
    hash: FAIL, exit 1. A present key with no recorded hash is not
    a frozen key.
  - key file present and hash recorded: PASS only when the sha256
    matches, else FAIL, exit 1.

thu-tu-chay.txt is looked for at the repo root first, then in
rung3-run-log/. The recorded line must look like:
  key sha256: <64 hex chars>
  (or: rung3-answer-keys.json sha256: <64 hex chars>)
Also requires docs/rung3-answer-keys.md to exist next to the JSON
when the JSON exists (the freeze artifact is both files).

Usage:
  python3 rung3-ci/check-key-hash.py [--key PATH] [--state PATH]
No personal info in this file.
"""
import argparse
import hashlib
import os
import re
import sys

HASH_RE = re.compile(r"([0-9a-f]{64})")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_state(root, explicit):
    if explicit:
        return explicit
    for cand in (os.path.join(root, "thu-tu-chay.txt"),
                 os.path.join(root, "rung3-run-log", "thu-tu-chay.txt")):
        if os.path.isfile(cand):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=None)
    ap.add_argument("--state", default=None)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = args.key or os.path.join(root, "docs",
                                        "rung3-answer-keys.json")
    if not os.path.isfile(key_path):
        print("PENDING: key file not present yet: %s" % key_path)
        print("RESULT: key not frozen (expected until synthesis writes it)")
        return 0
    digest = sha256_file(key_path)
    md_path = os.path.join(os.path.dirname(key_path),
                           "rung3-answer-keys.md")
    if not os.path.isfile(md_path):
        print("FAIL: key JSON present but human-readable %s missing"
              % md_path)
        return 1
    state_path = find_state(root, args.state)
    if not state_path:
        print("FAIL: key file present (sha256 %s) but thu-tu-chay.txt "
              "not found; the hash is not recorded anywhere" % digest)
        return 1
    recorded = None
    for line in open(state_path, encoding="utf-8", errors="replace"):
        if "sha256" in line.lower() and ("key" in line.lower()
                                         or "answer-keys" in line.lower()):
            m = HASH_RE.search(line)
            if m:
                recorded = m.group(1)
    if not recorded:
        print("FAIL: key file present (sha256 %s) but no key hash is "
              "recorded in %s" % (digest, state_path))
        return 1
    if recorded != digest:
        print("FAIL: key hash mismatch: file=%s recorded=%s (state %s)"
              % (digest, recorded, state_path))
        return 1
    print("PASS: key hash matches: %s (recorded in %s)"
          % (digest, state_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

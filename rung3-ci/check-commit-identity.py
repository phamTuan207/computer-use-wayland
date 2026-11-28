#!/usr/bin/env python3
"""Commit identity check: new commits must use noreply email forms.

Phase 0 (repo-redo research 2026-11-28): history metadata carries
personal email forms on about 98-99% of commits. This check stops
the present from leaking while the past is decided separately.
Author and committer emails must be GitHub noreply forms
(*@users.noreply.github.com or noreply@github.com, the latter is
GitHub's own merge committer). Anything else fails.

Usage: check-commit-identity.py <rev-range>   e.g. BASE..HEAD
Exit 1 on any violation. Python standard library only.
"""
import subprocess
import sys

ALLOWED_SUFFIXES = ("@users.noreply.github.com",)
ALLOWED_EXACT = {"noreply@github.com"}


def email_ok(email):
    email = email.strip().lower()
    return email in ALLOWED_EXACT or email.endswith(ALLOWED_SUFFIXES)


def main(argv):
    if len(argv) != 2:
        print("usage: check-commit-identity.py <rev-range>",
              file=sys.stderr)
        return 2
    rev_range = argv[1]
    out = subprocess.run(
        ["git", "log", "--format=%H%x00%ae%x00%ce", rev_range],
        capture_output=True, text=True)
    if out.returncode != 0:
        print(f"identity check: git log failed: {out.stderr.strip()}",
              file=sys.stderr)
        return 2
    violations = []
    for line in out.stdout.splitlines():
        if not line:
            continue
        sha, author, committer = line.split("\x00")
        for role, email in (("author", author), ("committer", committer)):
            if not email_ok(email):
                violations.append(
                    f"identity: {sha[:12]} {role} email is not a "
                    f"noreply form (domain: "
                    f"{email.rsplit('@', 1)[-1]})")
    for v in violations:
        print(v)
    if violations:
        print(f"identity check FAIL: {len(violations)} violation(s). "
              f"Set a noreply identity: git config user.email "
              f"<id>+<handle>@users.noreply.github.com")
        return 1
    print("identity check PASS: all commits use noreply emails")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
"""pii-scan.py v1: deterministic PII scan for snapshot dirs before any push.

Spec: replan-fixes-20261126.md F8.1 (gitleaks is absent on the VM; this is
the replacement gate). Python standard library only.

Usage: python3 pii-scan.py <dir> [<dir> ...]
Output: one line per hit: <file>:<line>: <rule>: <match>
Exit 1 on any hit, exit 0 only when clean.

Checks, on every text-decodable file under each dir:
- credential assignments: key names matching password/passwd/pwd/token/secret/
  api key/bearer/session/cookie followed by a value
- high-entropy strings: token-like strings over 20 chars mixing letters+digits
  (excludes pure hex hashes of exactly 32/40/64 chars, which are evidence
  hashes, and excludes UUIDs)
- email addresses
- phone numbers (VN +84 / 0xxxxxxxxx shapes and international +cc shapes)
- owner tab URLs: http(s) URLs whose host is a mail/calendar/drive/docs
  service, or whose path contains account segments
"""
import math
import os
import re
import sys

CRED_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|bearer|session|cookie)\b"
    r"\s*[:=]\s*[\"']?([^\s\"',}]{4,})"
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<![\dA-Za-z])(\+84|0)(3|5|7|8|9)\d{8}(?![\dA-Za-z])|(?<![\dA-Za-z])\+\d{1,3}[-. ]?\d{3,4}[-. ]?\d{3,4}[-. ]?\d{3,4}(?![\dA-Za-z])")
URL_RE = re.compile(r"https?://[^\s\"'<>\]]+")
OWNER_HOSTS = ("mail.", "calendar.", "drive.", "docs.", "gmail", "outlook", "notion.so")
ACCOUNT_SEGS = ("/account", "/profile", "/settings", "/my-account", "/u/")
TOKEN_RE = re.compile(r"\b[A-Za-z0-9_\-+/=]{24,}\b")
HEX_RE = re.compile(r"^[0-9a-f]{32}$|^[0-9a-f]{40}$|^[0-9a-f]{64}$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
# Identifier-like strings (CSS classes, filenames, paths) are not secrets:
# word segments joined by - or _ with mostly-alpha segments.
IDENT_RE = re.compile(r"^[A-Za-z]+([-_]+[A-Za-z0-9]+)+[-_]*$")
KNOWN_PREFIX_RE = re.compile(
    r"\b(ghp_|gho_|ghu_|ghs_|ghr_|github_pat_|sk-ant-|sk-proj-|sk-|AKIA|xox[bpras]-|AIza|ya29\.|glpat-)[A-Za-z0-9_\-]{8,}"
)


def entropy(s):
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def scan_file(path):
    hits = []
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, IsADirectoryError, PermissionError):
        return hits  # binary or unreadable: not text, skip (hashes cover binaries)
    for i, line in enumerate(lines, 1):
        for m in CRED_RE.finditer(line):
            hits.append((i, "credential", m.group(0)[:60]))
        for m in EMAIL_RE.finditer(line):
            hits.append((i, "email", m.group(0)))
        for m in PHONE_RE.finditer(line):
            hits.append((i, "phone", m.group(0)))
        for m in URL_RE.finditer(line):
            url = m.group(0).lower()
            host = url.split("://", 1)[1].split("/", 1)[0]
            path_part = "/" + url.split("://", 1)[1].split("/", 1)[1] if "/" in url.split("://", 1)[1] else ""
            if any(h in host for h in OWNER_HOSTS) or any(s in path_part for s in ACCOUNT_SEGS):
                hits.append((i, "owner-url", m.group(0)[:80]))
        for m in KNOWN_PREFIX_RE.finditer(line):
            hits.append((i, "known-token-prefix", m.group(0)[:40]))
        for m in TOKEN_RE.finditer(line):
            tok = m.group(0)
            if "/" in tok:  # file paths and URL fragments are not secrets
                continue
            if HEX_RE.match(tok) or UUID_RE.match(tok) or IDENT_RE.match(tok):
                continue
            classes = sum([
                any(c.islower() for c in tok),
                any(c.isupper() for c in tok),
                any(c.isdigit() for c in tok),
                any(c in "_-+/=" for c in tok),
            ])
            if classes >= 3 and entropy(tok) > 4.5:
                hits.append((i, "high-entropy", tok[:40]))
    return hits


def main():
    if len(sys.argv) < 2:
        print("usage: pii-scan.py <dir> [<dir> ...]", file=sys.stderr)
        return 2
    total = 0
    for root in sys.argv[1:]:
        if os.path.isfile(root):
            paths = [root]
        else:
            paths = [
                os.path.join(dirpath, name)
                for dirpath, _dirs, files in os.walk(root)
                for name in sorted(files)
            ]
        for path in paths:
            for lineno, rule, match in scan_file(path):
                print(f"{path}:{lineno}: {rule}: {match}")
                total += 1
    if total:
        print(f"pii-scan: {total} hit(s), push BLOCKED", file=sys.stderr)
        return 1
    print("pii-scan: clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

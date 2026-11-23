#!/usr/bin/env python3
"""Rung 3 pre-run liveness check script.

Runs the list section 8 service checks and writes a dated report:
  - each named service reachable (HTTP GET, 15 s timeout);
  - sqliteonline.com serves its app (a real query run needs a
    browser on the laptop, so that part is PENDING, not faked);
  - R3-009 WAVE URLs: the WAVE report is JS-rendered, so error
    counts are PENDING until a browser check on the laptop;
  - each fixture exists under fixture_root (default ~/rung3);
  - DP-03 port count from `ss -tlnp` on this machine (re-run on
    the laptop before task 1; the report records the hostname);
  - test accounts and the ttsmp3 quota: SKIP until synthesis fills
    in liveness-config.json (the script never logs in without an
    account entry and never stores a password).

Exit 0 when the report was written and no check is FAIL.
Exit 1 when at least one check is FAIL (service unreachable or
fixture root present but a fixture missing).
PENDING and SKIP checks are listed in the report with reasons;
a red check maps to a pre-run invalid declaration with the backup
rule, per the grading decision.

Usage:
  python3 rung3-ci/liveness-check.py [--config FILE] [--out FILE]
      [--fixture-root DIR]
The dated report defaults to
  rung3-ci/liveness-report-YYYYMMDD-HHMMSS.md
in the repo. Times are Asia/Ho_Chi_Minh wall clock.
No personal info in this file.
"""
import argparse
import datetime
import json
import os
import socket
import subprocess
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) rung3-liveness/1.0"}


def now_hcm():
    tz = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(tz)


def http_status(url, timeout=15):
    req = urllib.request.Request(url, headers=UA, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(4096)
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, "HTTP error"
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fixture-root", default=None)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg_path = args.config or os.path.join(root, "rung3-ci",
                                           "liveness-config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    host = socket.gethostname()
    ts = now_hcm()
    stamp = ts.strftime("%Y%m%d-%H%M%S")
    out_path = args.out or os.path.join(
        root, "rung3-ci", "liveness-report-%s.md" % stamp)
    fixture_root = os.path.expanduser(
        args.fixture_root or cfg.get("fixture_root", "~/rung3"))

    checks = []

    def add(kind, name, status, detail):
        checks.append({"kind": kind, "name": name, "status": status,
                       "detail": detail})

    for svc in cfg.get("services", []):
        code, err = http_status(svc["url"])
        if code and 200 <= code < 400:
            add("service", "%s %s" % (svc["task"], svc["url"]), "OK",
                "HTTP %d" % code)
        elif code == 403:
            add("service", "%s %s" % (svc["task"], svc["url"]), "FAIL",
                "HTTP 403 (bot check page; task may be invalid pre-run)")
        elif code:
            add("service", "%s %s" % (svc["task"], svc["url"]), "FAIL",
                "HTTP %d" % code)
        else:
            add("service", "%s %s" % (svc["task"], svc["url"]), "FAIL", err)

    # sqliteonline: HTTP can only prove the app is served.
    code, err = http_status("https://sqliteonline.com/")
    if code and 200 <= code < 400:
        add("service", "R3-021 sqliteonline runs a query", "PENDING",
            "app served (HTTP %d); a real query run needs a browser on "
            "the laptop before task 1" % code)
    else:
        add("service", "R3-021 sqliteonline runs a query", "FAIL",
            "site not reachable: HTTP %s %s" % (code, err))

    for url in cfg.get("r3_009_urls", []):
        code, err = http_status("https://wave.webaim.org/report#/" + url)
        if code and 200 <= code < 400:
            add("service", "R3-009 WAVE errors >= 1 for %s" % url,
                "PENDING",
                "WAVE report page served (HTTP %d); error counts need a "
                "browser check on the laptop, the report is JS-rendered"
                % code)
        else:
            add("service", "R3-009 WAVE errors >= 1 for %s" % url, "FAIL",
                "WAVE not reachable: HTTP %s %s" % (code, err))

    # Fixtures.
    if not os.path.isdir(fixture_root):
        for fx in cfg.get("fixtures", []):
            add("fixture", "%s %s" % (fx["task"], fx["path"]), "FAIL",
                "fixture root %s absent on host %s (synthesis creates "
                "~/rung3 on the laptop)" % (fixture_root, host))
    else:
        for fx in cfg.get("fixtures", []):
            path = os.path.join(fixture_root, fx["path"])
            if os.path.exists(path):
                add("fixture", "%s %s" % (fx["task"], fx["path"]), "OK",
                    "exists")
            else:
                add("fixture", "%s %s" % (fx["task"], fx["path"]), "FAIL",
                    "missing under %s" % fixture_root)

    # DP-03 port count on this machine.
    try:
        out = subprocess.run(["ss", "-tlnp"], capture_output=True,
                             text=True, timeout=20)
        named = [l for l in out.stdout.splitlines()
                 if "users:((" in l]
        n = len(named)
        want_min = cfg.get("dp03_min_ports", 3)
        want_full = cfg.get("dp03_ports_full", 5)
        if n >= want_full:
            add("service", "DP-03 listening ports with process names",
                "OK", "%d ports on host %s (full: %d)" % (n, host, want_full))
        elif n >= want_min:
            add("service", "DP-03 listening ports with process names",
                "PENDING",
                "%d ports on host %s (minimum %d, full %d); re-run on the "
                "laptop before task 1, port count is host-specific"
                % (n, host, want_min, want_full))
        else:
            add("service", "DP-03 listening ports with process names",
                "FAIL",
                "%d ports on host %s, need at least %d; if the laptop "
                "also has fewer than %d, DP-03 is invalid pre-run"
                % (n, host, want_min, want_min))
    except FileNotFoundError:
        add("service", "DP-03 listening ports with process names", "FAIL",
            "`ss` not found on host %s" % host)
    except Exception as e:
        add("service", "DP-03 listening ports with process names", "FAIL",
            "%s: %s" % (type(e).__name__, e))

    # Test accounts: config-driven, never attempted without an entry.
    for acc in cfg.get("accounts", []):
        add("account", "%s %s" % (acc["task"], acc["service"]), "SKIP",
            "status %s; no login attempted (synthesis owns accounts)"
            % acc.get("status", "pending-synthesis"))

    add("account", "R3-008 ttsmp3 quota unspent", "SKIP",
        cfg.get("ttsmp3_note", ""))

    counts = {}
    for c in checks:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    verdict = "FAIL" if counts.get("FAIL", 0) else "OK"
    lines = [
        "# Rung 3 pre-run liveness report",
        "",
        "- Date: %s Asia/Ho_Chi_Minh" % ts.strftime("%Y-%m-%d %H:%M:%S"),
        "- Host: %s" % host,
        "- Fixture root checked: %s" % fixture_root,
        "- Verdict: %s (%d OK, %d FAIL, %d PENDING, %d SKIP)"
        % (verdict, counts.get("OK", 0), counts.get("FAIL", 0),
           counts.get("PENDING", 0), counts.get("SKIP", 0)),
        "",
        "Every FAIL below maps to a pre-run invalid declaration with the "
        "backup rule, or blocks task 1 until fixed. PENDING items need a "
        "laptop or browser step before task 1. SKIP items are not "
        "configured yet (synthesis).",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for c in checks:
        lines.append("| %s | %s | %s |" % (c["name"], c["status"], c["detail"]))
    lines.append("")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("REPORT: %s" % out_path)
    print("RESULT: %s (%d OK, %d FAIL, %d PENDING, %d SKIP)"
          % (verdict, counts.get("OK", 0), counts.get("FAIL", 0),
             counts.get("PENDING", 0), counts.get("SKIP", 0)))
    for c in checks:
        if c["status"] in ("FAIL", "PENDING", "SKIP"):
            print("%s: %s | %s" % (c["status"], c["name"], c["detail"]))
    return 0 if verdict == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Per-update RDP smoke test for the Zen seamless-control lane.

Runs after every Zen update, before agent use resumes (RT-05/RT-18,
acceptance step 8, kill criterion 1). Fail-loud and fail-closed:
the first failed check stops the run, prints one JSON object to
stdout, and exits with a distinct nonzero code. No channel selected
in the port registry = no drive; this script never guesses a port,
it only verifies the port and profile marker it is handed.

Checks:
  a  port owner pid + cmdline matches --profile-marker
  b  attach succeeds (connect, listTabs, getTarget)
  c  webdriver probe CLEAN, native false (client probe, fail-loud)
  d  evaluate round-trip (1+1 == 2, DOM read sane)
  e  parent-process target: typeof gZenWorkspaces / gBrowser /
     gZenFolders all "object" (landed client API, allow_parent gate)
  f  bind is 127.0.0.1-only (ss)
  g  latency spot numbers (informational, never fails the run)
  h  navigate the attached tab to about:blank and wait-load
     (proves navigateTo still works post-update). NOTE: (h) replaces
     the attached tab content; run smoke on a throwaway/tasked tab.

Exit codes: 0 pass, 2 setup/usage, 10 owner, 11 attach, 12 probe,
13 evaluate, 14 parent target, 15 bind, 16 navigate.

Stdlib only. Reuses rdp_client.py (same directory) for attach,
evaluate, and the webdriver probe. Sends no OS input; ydotool is
banned and not used. Generic and repo-shaped: no hardcoded port,
profile, pid, or path defaults.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from rdp_client import RDPClient, RDPError, check_port_owner, median, ms
except ImportError as e:
    print(json.dumps({
        "smoke": "rdp_smoke", "overall": "FAIL", "failed_check": "setup",
        "error": f"cannot import rdp_client: {e}",
        "hint": "place rdp_smoke.py next to rdp_client.py",
    }, indent=1))
    sys.exit(2)

EXIT = {"setup": 2, "a_port_owner": 10, "b_attach": 11, "c_webdriver": 12,
        "d_evaluate": 13, "e_parent_target": 14, "f_bind": 15,
        "h_navigate": 16}

PARENT_GLOBALS = ("gZenWorkspaces", "gBrowser", "gZenFolders")


def parse_bind(ss_text, port):
    """Pure: return (ok, detail) for 127.0.0.1-only bind on port."""
    lines = [ln for ln in ss_text.splitlines()
             if re.search(rf":{port}\s", ln)]
    if not lines:
        return False, {"lines": [], "reason": "no listener line for port"}
    locals_ = []
    for ln in lines:
        parts = ln.split()
        # ss -tlnp columns: State Recv-Q Send-Q Local Peer Process
        locals_.append(parts[3] if len(parts) > 3 else "")
    bad = [a for a in locals_ if not a.startswith("127.0.0.1:")]
    if bad:
        return False, {"local_addrs": locals_, "non_loopback": bad}
    return True, {"local_addrs": locals_}


def parent_evaluate(client, expr, timeout=10):
    """Evaluate in the parent-process (chrome) target via the landed
    client API (gated by allow_parent, recorded in the drive report).
    Returns (value, parent_url). Raises RDPError."""
    value = client.parent_evaluate(expr, timeout=timeout)
    return value, client.parent_url


def run_smoke(port, marker, host="127.0.0.1", timeout=15, eval_runs=10):
    """Returns (report_dict, exit_code). Stops at first failed check."""
    t_start = time.monotonic()
    report = {
        "smoke": "rdp_smoke", "version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "port": port, "host": host, "profile_marker": marker,
        "checks": {}, "latency": {}, "overall": "FAIL",
        "failed_check": None, "error": None,
    }

    def fail(check, err, detail=None):
        report["checks"][check] = {"status": "FAIL", "detail": detail}
        report["failed_check"] = check
        report["error"] = str(err)
        report["elapsed_ms"] = ms(time.monotonic() - t_start)
        return report, EXIT[check]

    # (a) port owner pid + cmdline matches marker
    try:
        pid, _cmd = check_port_owner(port, marker)
        report["checks"]["a_port_owner"] = {"status": "PASS", "pid": pid}
    except Exception as e:
        return fail("a_port_owner", e)

    # (b) attach succeeds; time attach-to-first-evaluate for (g)
    client = None
    try:
        t0 = time.monotonic()
        # Smoke is a gate tool: it attaches to the selected tab
        # unscoped (explicit unscoped_test opt-in) and uses the parent
        # target for read-only typeof checks (explicit allow_parent).
        # Denylist stays off here; scoped agent drives enforce it.
        client = RDPClient(port, host=host, timeout=timeout,
                           unscoped_test=True, allow_parent=True,
                           denylist_patterns=[], warn_unscoped=False)
        client.attach()
        first = client.evaluate("1+1")
        attach_ms = ms(time.monotonic() - t0)
        if first != 2:
            raise RDPError(f"first evaluate 1+1 gave {first!r}")
        report["checks"]["b_attach"] = {
            "status": "PASS", "desc_actor": client.desc_actor,
            "console_actor": client.console_actor}
        report["latency"]["attach_to_first_evaluate_ms"] = attach_ms
    except Exception as e:
        if client:
            client.close()
        return fail("b_attach", e)

    try:
        # (c) webdriver probe CLEAN native-false (client probe, fail-loud)
        try:
            probe = client.probe_webdriver()
            report["checks"]["c_webdriver"] = {"status": "PASS", **probe}
        except Exception as e:
            return fail("c_webdriver", e)

        # (d) evaluate round-trip
        try:
            v = client.evaluate("1+1")
            if v != 2:
                raise RDPError(f"evaluate 1+1 gave {v!r}")
            n = client.evaluate("document.querySelectorAll('*').length")
            if not isinstance(n, (int, float)) or n < 1:
                raise RDPError(f"DOM read gave {n!r}")
            report["checks"]["d_evaluate"] = {
                "status": "PASS", "one_plus_one": v, "dom_nodes": n}
        except Exception as e:
            return fail("d_evaluate", e)

        # (e) parent-target typeof Zen internals all object
        try:
            types, purl = {}, None
            for name in PARENT_GLOBALS:
                types[name], purl = parent_evaluate(client, f"typeof {name}")
            bad = {k: v for k, v in types.items() if v != "object"}
            if bad:
                raise RDPError(f"parent typeof not all object: {types}")
            report["checks"]["e_parent_target"] = {
                "status": "PASS", "typeof": types, "parent_url": purl}
        except Exception as e:
            return fail("e_parent_target", e)

        # (f) bind is 127.0.0.1-only via ss
        try:
            ss = subprocess.run(["ss", "-tlnp"], capture_output=True,
                                text=True, timeout=10).stdout
            ok, detail = parse_bind(ss, port)
            if not ok:
                raise RDPError(f"bind not loopback-only: {detail}")
            report["checks"]["f_bind"] = {"status": "PASS", **detail}
        except Exception as e:
            return fail("f_bind", e)

        # (h) navigate the attached tab to about:blank and wait-load
        try:
            client.navigate("about:blank")
            loaded = client.wait_load("about:blank", timeout=10)
            report["checks"]["h_navigate"] = {
                "status": "PASS", "loaded": loaded}
        except Exception as e:
            return fail("h_navigate", e)

        # (g) latency spot numbers (informational)
        xs = []
        for _ in range(max(1, eval_runs)):
            t0 = time.monotonic()
            client.evaluate("1+1")
            xs.append(time.monotonic() - t0)
        report["latency"]["evaluate_median_ms"] = ms(median(xs))
        report["latency"]["evaluate_runs_ms"] = [ms(x) for x in xs]
        report["checks"]["g_latency"] = {"status": "PASS",
                                         "note": "informational"}
    finally:
        client.close()

    report["overall"] = "PASS"
    report["elapsed_ms"] = ms(time.monotonic() - t_start)
    return report, 0


def main():
    ap = argparse.ArgumentParser(
        description="Per-update RDP smoke test (fail-loud, JSON output)")
    ap.add_argument("--port", type=int, required=True,
                    help="RDP port from the port registry (never guessed)")
    ap.add_argument("--profile-marker", required=True,
                    help="substring required in the listening pid cmdline")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--eval-runs", type=int, default=10)
    args = ap.parse_args()
    report, code = run_smoke(args.port, args.profile_marker, host=args.host,
                             timeout=args.timeout, eval_runs=args.eval_runs)
    print(json.dumps(report, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())

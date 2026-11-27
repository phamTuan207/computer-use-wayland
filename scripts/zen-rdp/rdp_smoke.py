#!/usr/bin/env python3
"""Per-update RDP smoke test for the Zen seamless-control lane.

Runs after every Zen update, before agent use resumes (RT-05/RT-18,
acceptance step 8, kill criterion 1). Fail-loud and fail-closed:
the first failed check stops the run, prints one JSON object to
stdout, and exits with a distinct nonzero code. No channel selected
in the port registry = no drive; this script never guesses a port,
it only verifies the port and profile marker it is handed.

Checks:
  z  deployed rdp_client.py byte-matches the landed copy next to
     this script (only when --deployed-client is given; drift
     fails loud before any attach)
  a  port owner pid + cmdline matches --profile-marker
  b  attach succeeds (connect, listTabs, getTarget)
  c  webdriver probe CLEAN, native false (client probe, fail-loud)
  d  evaluate round-trip (1+1 == 2, DOM read sane)
  e  parent-process target: typeof gZenWorkspaces / gBrowser /
     gZenFolders all "object" (landed client API, allow_parent gate)
  i  pinned Spaces/Folders method set (P4, zen_spaces.PINNED_METHODS):
     every typed list+create method is still a function
  f  bind is 127.0.0.1-only (ss)
  g  latency spot numbers (informational, never fails the run)
  h  navigate the attached tab to about:blank and wait-load
     (proves navigateTo still works post-update). NOTE: (h) replaces
     the attached tab content; run smoke on a throwaway/tasked tab.
  j  bench self-test (only when --bench-local-url is given): the
     bench instrument completes with a timed result on the given
     local URL (runs=1; bench navigates destructively, throwaway
     sessions only). Requires dedicated-session proof:
     --bench-profile-dir (launch_dedicated marker + session for
     this port) or the explicit --bench-allow-any-session flag;
     refused otherwise, before any attach

Exit codes: 0 pass, 2 setup/usage, 10 owner, 11 attach, 12 probe,
13 evaluate, 14 parent target, 15 bind, 16 navigate,
17 deployed-copy drift, 18 bench self-test, 19 pinned methods.

Stdlib only. Reuses rdp_client.py (same directory) for attach,
evaluate, and the webdriver probe. Sends no OS input; ydotool is
banned and not used. Generic and repo-shaped: no hardcoded port,
profile, pid, or path defaults.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from rdp_client import (RDPClient, RDPError, bench, check_port_owner,
                            median, ms)
    from zen_spaces import assert_pinned_methods
except ImportError as e:
    print(json.dumps({
        "smoke": "rdp_smoke", "overall": "FAIL", "failed_check": "setup",
        "error": f"cannot import rdp_client: {e}",
        "hint": "place rdp_smoke.py next to rdp_client.py",
    }, indent=1))
    sys.exit(2)

EXIT = {"setup": 2, "a_port_owner": 10, "b_attach": 11, "c_webdriver": 12,
        "d_evaluate": 13, "e_parent_target": 14, "f_bind": 15,
        "h_navigate": 16, "z_deployed_hash": 17, "j_bench": 18,
        "i_pinned_methods": 19}

PARENT_GLOBALS = ("gZenWorkspaces", "gBrowser", "gZenFolders")


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_deployed_hash(deployed_path, reference_path=None):
    """Pure: (ok, detail). The deployed (machine-layer) copy of
    rdp_client.py must byte-match the landed reference (default:
    the rdp_client.py next to this smoke script). Drift means
    measured numbers describe the landed tree, not the deployed
    lane, so it fails loud."""
    ref = reference_path or str(
        Path(__file__).resolve().parent / "rdp_client.py")
    try:
        d = file_sha256(deployed_path)
        r = file_sha256(ref)
    except OSError as e:
        return False, {"error": str(e), "deployed": str(deployed_path),
                       "reference": str(ref)}
    return d == r, {"deployed_sha256": d, "reference_sha256": r,
                    "deployed": str(deployed_path), "reference": str(ref)}


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


def bench_dedicated_proof(port, profile_dir):
    """(ok, detail): dedicated-session proof for the bench leg.
    The profile dir must carry a launch_dedicated marker + session
    whose recorded port is this smoke port (verified session, live
    pid). Anything else is not proof."""
    if not profile_dir:
        return False, {"reason": "no --bench-profile-dir given"}
    try:
        import launch_dedicated
        record = launch_dedicated.verify_session(profile_dir)
    except Exception as e:
        return False, {"reason": f"dedicated session not verified: {e}",
                       "profile_dir": str(profile_dir)}
    if int(record.get("port", -1)) != int(port):
        return False, {"reason": "dedicated session port "
                                 f"{record.get('port')} != smoke "
                                 f"port {port}",
                       "profile_dir": str(profile_dir)}
    return True, {"profile_dir": str(profile_dir),
                  "pid": record.get("pid")}


def parent_evaluate(client, expr, timeout=10):
    """Evaluate in the parent-process (chrome) target via the landed
    client API (gated by allow_parent, recorded in the drive report).
    Returns (value, parent_url). Raises RDPError."""
    value = client.parent_evaluate(expr, timeout=timeout)
    return value, client.parent_url


def run_smoke(port, marker, host="127.0.0.1", timeout=15, eval_runs=10,
              deployed_client=None, bench_local_url=None,
              bench_profile_dir=None, bench_allow_any_session=False):
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

    # (z) deployed copy byte-matches the landed client (drift gate)
    if deployed_client:
        ok, detail = check_deployed_hash(deployed_client)
        if not ok:
            return fail("z_deployed_hash",
                        "deployed rdp_client.py drifted from the landed "
                        f"copy: {detail}", detail)
        report["checks"]["z_deployed_hash"] = {"status": "PASS", **detail}

    # (j) gate, checked before any attach: bench navigates
    # destructively, so it runs only on a proven dedicated session
    # (launch_dedicated marker + session for this port) or under
    # the explicit any-session opt-in. Never on an owner session
    # by construction.
    if bench_local_url and not bench_allow_any_session:
        ok, detail = bench_dedicated_proof(port, bench_profile_dir)
        if not ok:
            return fail("j_bench",
                        "BENCH REFUSED: bench self-test requires "
                        "dedicated-session proof (--bench-profile-dir "
                        "with a launch_dedicated session for this "
                        "port) or --bench-allow-any-session; "
                        f"{detail}", detail)

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

        # (i) pinned Spaces/Folders method set (P4): the whole typed
        # list+create surface must still be functions post-update
        try:
            types = assert_pinned_methods(client)
            report["checks"]["i_pinned_methods"] = {
                "status": "PASS", "methods": types}
        except Exception as e:
            return fail("i_pinned_methods", e)

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

    # (j) bench self-test: the measurement instrument completes with
    # a timed result (runs=1, local URL for both legs so the smoke
    # run needs no external network). Bench opens its own
    # connections, so it runs after the smoke client closes.
    if bench_local_url:
        try:
            result = bench(port, marker, bench_local_url, bench_local_url,
                           runs=1, unscoped_test=True)
            report["checks"]["j_bench"] = {
                "status": "PASS",
                "navigate_local_median_ms":
                    result["navigate_local"]["median_ms"],
                "attach_median_ms":
                    result["attach_to_first_evaluate"]["median_ms"]}
        except Exception as e:
            return fail("j_bench", e)

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
    ap.add_argument("--deployed-client", default=None, metavar="PATH",
                    help="deployed (machine-layer) rdp_client.py that "
                         "must byte-match the landed copy next to this "
                         "script; drift fails the run (exit 17)")
    ap.add_argument("--bench-local-url", default=None, metavar="URL",
                    help="run the bench self-test (runs=1) against "
                         "this local URL after the other checks; "
                         "bench navigates destructively, throwaway "
                         "sessions only (requires dedicated proof)")
    ap.add_argument("--bench-profile-dir", default=None, metavar="PATH",
                    help="launch_dedicated profile dir proving the "
                         "bench target is a dedicated session on "
                         "this port (marker + session verified)")
    ap.add_argument("--bench-allow-any-session", action="store_true",
                    help="EXPLICIT opt-in: run the bench self-test "
                         "without dedicated-session proof (never on "
                         "an owner session)")
    args = ap.parse_args()
    report, code = run_smoke(args.port, args.profile_marker, host=args.host,
                             timeout=args.timeout, eval_runs=args.eval_runs,
                             deployed_client=args.deployed_client,
                             bench_local_url=args.bench_local_url,
                             bench_profile_dir=args.bench_profile_dir,
                             bench_allow_any_session=
                             args.bench_allow_any_session)
    print(json.dumps(report, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())

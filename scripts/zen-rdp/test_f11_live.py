#!/usr/bin/env python3
"""F11 live test for rdp_client.py (dedicated throwaway session).

Replicates the M8 shape from
improvements/p3-event-feed-measurements-20261128.md against the
shipped client: a waiter polls wait_for on a tab that a second RDP
connection closes mid-wait. With the F11 fix (--expect-f11) the
wait must fail fast (< 1.5 s after the close) with a tab-destroyed
classification; without it (pre-fix client) the wait burns the
full 8 s budget and reports a plain timeout. Also measures the
shipped wait_load path (navigate + wait_load, 5 reps; closes the
M1 caveat) and a tab open/close storm with interleaved requests
(pairing must hold; the terminal flag must stay unset when only
other tabs die).

Assumes a throwaway Zen with --start-debugger-server is already
running on the given port (launch_dedicated.py). The waiter's tab
is tagged via parent JS and ONLY tagged tabs are closed. Test
pages are local fixtures served by an in-process HTTP server on
127.0.0.1. No real accounts, no cookies, no sensitive data.
ydotool is banned (not used).

Usage:
  python3 test_f11_live.py --port <rdp-port> \
      --profile-marker <profile-dir> [--expect-f11]
"""
import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from rdp_client import RDPClient, RDPError, check_port_owner

PAGES = {
    "/a.html": "<html><head><title>F11 A</title></head>"
               "<body><h1>A</h1></body></html>",
    "/b.html": "<html><head><title>F11 B</title></head>"
               "<body><h1>B</h1></body></html>",
}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGES.get(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        pass


def _parent(closer, script):
    return closer.parent_evaluate(script)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", required=True,
                    help="substring required in the listening pid "
                         "cmdline (fail-closed)")
    ap.add_argument("--expect-f11", action="store_true",
                    help="assert the F11 fast-fail (post-fix client); "
                         "without it, assert the pre-fix 8 s burn")
    args = ap.parse_args()

    results = {"expect_f11": args.expect_f11}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    waiter = None
    closer = None
    try:
        pid, _ = check_port_owner(args.port, args.profile_marker)
        results["port_owner_pid"] = pid

        waiter = RDPClient(args.port, unscoped_test=True,
                           warn_unscoped=False)
        waiter.attach()
        results["waiter_desc"] = waiter.desc_actor

        # Shipped wait_load path (M1 caveat): navigate + wait_load.
        reps = []
        for i in range(5):
            page = "/a.html" if i % 2 == 0 else "/b.html"
            t0 = time.monotonic()
            waiter.navigate(base + page)
            waiter.wait_load(page, timeout=20)
            reps.append(round((time.monotonic() - t0) * 1000, 1))
        results["wait_load_ms"] = reps
        results["wait_load_median_ms"] = sorted(reps)[len(reps) // 2]

        closer = RDPClient(args.port, unscoped_test=True,
                           warn_unscoped=False, allow_parent=True)

        # Storm: open/close OTHER tabs while the waiter interleaves
        # requests; pairing must hold and the flag must stay unset.
        token = "f11-storm"
        paired = True
        for _i in range(10):
            _parent(closer,
                    "(function(){var t=gBrowser.addTrustedTab("
                    "'about:blank'); t.setAttribute('data-f11', '"
                    + token + "'); return 'ok';})()")
            waiter.list_tabs()
            if waiter.evaluate("1+1") != 2:
                paired = False
        closed = _parent(
            closer,
            "(function(){var mine=[...gBrowser.tabs].filter("
            "function(t){return t.getAttribute('data-f11') === '"
            + token + "';}); mine.forEach(function(t){"
            "gBrowser.removeTab(t);}); return mine.length;})()")
        waiter.list_tabs()
        if waiter.evaluate("1+1") != 2:
            paired = False
        flag = getattr(waiter, "_terminal_destroyed", "absent")
        results["storm"] = {
            "opened": 10, "closed": closed, "paired": paired,
            "flag_after": flag if flag in (None, "absent") else "SET"}

        # M8: tag the waiter's tab, wait in a thread, close it from
        # the second connection ~1 s into the wait.
        tagged = _parent(
            closer,
            "(function(){var t=[...gBrowser.tabs].find(function(t){"
            "return t.linkedBrowser.currentURI.spec.indexOf('"
            + base + "') === 0;}); if(t){t.setAttribute('data-f11',"
            "'waiter');} return !!t;})()")
        results["waiter_tab_tagged"] = bool(tagged)

        outcome = {}

        def waiter_thread():
            t0 = time.monotonic()
            try:
                waiter.wait_for(
                    "document.getElementById('neverAppears') !== null",
                    timeout=8)
                outcome["result"] = "returned"
            except Exception as e:  # noqa: BLE001 - record any failure
                outcome["result"] = "error"
                outcome["error"] = str(e)
            outcome["elapsed_ms"] = round(
                (time.monotonic() - t0) * 1000, 1)

        thread = threading.Thread(target=waiter_thread)
        thread.start()
        time.sleep(1.0)
        t_close = time.monotonic()
        _parent(
            closer,
            "(function(){var mine=[...gBrowser.tabs].filter("
            "function(t){return t.getAttribute('data-f11') === "
            "'waiter';}); mine.forEach(function(t){"
            "gBrowser.removeTab(t);}); return mine.length;})()")
        thread.join(timeout=12)
        outcome["after_close_ms"] = (
            None if thread.is_alive()
            else round((time.monotonic() - t_close) * 1000, 1))
        results["m8"] = outcome

        if args.expect_f11:
            ok = (outcome.get("result") == "error"
                  and "tab destroyed" in outcome.get("error", "")
                  and outcome.get("after_close_ms") is not None
                  and outcome["after_close_ms"] < 1500
                  and paired
                  and results["storm"]["flag_after"] in (None, "absent"))
        else:
            ok = (outcome.get("result") == "error"
                  and "timeout" in outcome.get("error", "")
                  and paired)
        results["assert_ok"] = ok
        print(json.dumps(results, indent=1))
        return 0 if ok else 1
    except (RDPError, AssertionError) as e:
        results["fatal"] = str(e)
        print(json.dumps(results, indent=1))
        return 1
    finally:
        for client in (waiter, closer):
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
        server.shutdown()


if __name__ == "__main__":
    sys.exit(main())

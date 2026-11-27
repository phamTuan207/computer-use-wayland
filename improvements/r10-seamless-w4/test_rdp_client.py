#!/usr/bin/env python3
"""Small self-test for rdp_client.py (W4 slice).

Assumes a throwaway Zen with --start-debugger-server is already running
on the given port (launched by the run script). Asserts attach,
evaluate, clean webdriver probe, navigate, DOM read/write, and records
isTrusted for a JS click. Exits nonzero on any failure.

Usage:
  python3 test_rdp_client.py --port 6021 \
      --profile-marker /tmp/r10w4-rdp \
      --local-url http://127.0.0.1:8941/slice.html
"""
import argparse
import json
import sys

from rdp_client import RDPClient, RDPError, check_port_owner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", default=None)
    ap.add_argument("--local-url", required=True)
    args = ap.parse_args()
    checks = []
    try:
        if args.profile_marker:
            pid, _ = check_port_owner(args.port, args.profile_marker)
            checks.append(f"port-owner pid={pid} marker ok")
        c = RDPClient(args.port)
        c.attach()
        checks.append(f"attach ok desc={c.desc_actor} console={c.console_actor}")
        v = c.evaluate("1+1")
        assert v == 2, f"1+1 gave {v!r}"
        checks.append("evaluate 1+1 == 2")
        probe = c.probe_webdriver()
        checks.append(f"webdriver probe {probe['verdict']} wd={probe['webdriver']}")
        c.navigate(args.local_url)
        c.wait_load("slice", timeout=20)
        title = c.evaluate("document.title")
        assert title == "W4 Slice Page", f"title {title!r}"
        checks.append(f"navigate+load ok title={title!r}")
        n = c.evaluate("document.querySelectorAll('*').length")
        assert isinstance(n, (int, float)) and n > 3, f"dom count {n!r}"
        checks.append(f"dom read count={n}")
        c.evaluate("document.getElementById('name').value = 'w4-test';"
                   "document.getElementById('name').value")
        val = c.evaluate("document.getElementById('name').value")
        assert val == "w4-test", f"input value {val!r}"
        checks.append("dom write (input value) ok")
        trusted = c.evaluate(
            "window.__t = 'unset';"
            "document.getElementById('go').addEventListener('click',"
            " e => { window.__t = String(e.isTrusted); });"
            "document.getElementById('go').click(); window.__t")
        checks.append(f"js click isTrusted={trusted} (false expected)")
        assert trusted == "false", f"isTrusted {trusted!r}"
        c.close()
    except (RDPError, AssertionError) as e:
        print(json.dumps({"self_test": "FAIL", "checks": checks,
                          "error": str(e)}, indent=1))
        return 1
    print(json.dumps({"self_test": "PASS", "checks": checks}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

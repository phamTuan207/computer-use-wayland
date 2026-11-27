#!/usr/bin/env python3
"""Small live self-test for rdp_client.py (adapted from the W4 slice).

Assumes a throwaway Zen with --start-debugger-server is already running
on the given port (launched by the run harness). Asserts attach,
evaluate, clean webdriver probe, navigate, DOM read/write, and records
isTrusted for a JS click. Exits nonzero on any failure.

Fixture contract: --local-url must serve a page containing an input
element (id --input-id, default "name") and a button (id --button-id,
default "go"). The expected page title is checked only when
--expected-title is given; the load wait matches --url-substr
(default: the URL path basename). No fixture is bundled with this
test; point it at any local page that meets the contract.

Usage:
  python3 test_rdp_client.py --port <rdp-port> \
      --profile-marker <profile-dir> \
      --local-url <local-url> [--expected-title <title>]
"""
import argparse
import json
import sys
from urllib.parse import urlparse

from rdp_client import RDPClient, RDPError, check_port_owner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", required=True,
                    help="substring required in the listening pid cmdline "
                         "(fail-closed)")
    ap.add_argument("--local-url", required=True)
    ap.add_argument("--expected-title", default=None,
                    help="if given, assert document.title equals this")
    ap.add_argument("--url-substr", default=None,
                    help="substring waited for after navigate "
                         "(default: URL path basename)")
    ap.add_argument("--input-id", default="name")
    ap.add_argument("--button-id", default="go")
    args = ap.parse_args()
    substr = args.url_substr or urlparse(args.local_url).path.rsplit(
        "/", 1)[-1]
    checks = []
    try:
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
        c.wait_load(substr, timeout=20)
        title = c.evaluate("document.title")
        if args.expected_title is not None:
            assert title == args.expected_title, f"title {title!r}"
        checks.append(f"navigate+load ok title={title!r}")
        n = c.evaluate("document.querySelectorAll('*').length")
        assert isinstance(n, (int, float)) and n > 3, f"dom count {n!r}"
        checks.append(f"dom read count={n}")
        c.evaluate(f"document.getElementById('{args.input_id}').value = "
                   f"'rdp-test';"
                   f"document.getElementById('{args.input_id}').value")
        val = c.evaluate(f"document.getElementById('{args.input_id}').value")
        assert val == "rdp-test", f"input value {val!r}"
        checks.append("dom write (input value) ok")
        trusted = c.evaluate(
            "window.__t = 'unset';"
            f"document.getElementById('{args.button_id}').addEventListener("
            "'click', e => { window.__t = String(e.isTrusted); });"
            f"document.getElementById('{args.button_id}').click(); "
            "window.__t")
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

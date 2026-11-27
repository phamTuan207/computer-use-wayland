#!/usr/bin/env python3
"""Unit test for rdp_smoke pure logic (no browser needed).

Covers parse_bind (loopback pass / wildcard fail / missing fail),
the exit-code map (distinct code per failed check, including
h_navigate = 16), and check_deployed_hash (match / drift /
missing file, D2).
Run: python3 test_rdp_smoke.py
Ports below are arbitrary examples for the pure-logic test only.
"""
import sys
import tempfile
from pathlib import Path

from rdp_smoke import EXIT, check_deployed_hash, parse_bind

TEST_PORT = 12345  # arbitrary example port (pure-logic test only)
OTHER_PORT = 23456

SS_LOOPBACK = (
    "State Recv-Q Send-Q Local Address:Port Peer Address:Port Process\n"
    f"LISTEN 0 5 127.0.0.1:{TEST_PORT} 0.0.0.0:* "
    "users:((\"zen-bin\",pid=123,fd=9))\n"
)
SS_WILDCARD = (
    f"LISTEN 0 5 0.0.0.0:{TEST_PORT} 0.0.0.0:* "
    "users:((\"zen-bin\",pid=123,fd=9))\n"
)
SS_V6 = (
    f"LISTEN 0 5 [::]:{TEST_PORT} [::]:* users:((\"zen-bin\",pid=123,fd=9))\n"
)
SS_OTHER_PORT = (
    f"LISTEN 0 5 127.0.0.1:{OTHER_PORT} 0.0.0.0:* "
    "users:((\"chromium\",pid=1,fd=2))\n"
)


def main():
    ok, d = parse_bind(SS_LOOPBACK, TEST_PORT)
    assert ok and d["local_addrs"] == [f"127.0.0.1:{TEST_PORT}"], (ok, d)
    ok, d = parse_bind(SS_WILDCARD, TEST_PORT)
    assert not ok and d["non_loopback"] == [f"0.0.0.0:{TEST_PORT}"], (ok, d)
    ok, d = parse_bind(SS_V6, TEST_PORT)
    assert not ok, (ok, d)
    ok, d = parse_bind(SS_OTHER_PORT, TEST_PORT)
    assert not ok and "no listener" in d["reason"], (ok, d)
    ok, _ = parse_bind(SS_LOOPBACK, OTHER_PORT)
    assert not ok, "wrong port must not match"
    codes = list(EXIT.values())
    assert len(codes) == len(set(codes)), f"exit codes not distinct: {EXIT}"
    assert 0 not in codes, "0 is reserved for PASS"
    assert EXIT.get("h_navigate") == 16, f"navigate check code: {EXIT}"
    assert EXIT.get("i_pinned_methods") == 19, f"pinned check code: {EXIT}"
    assert EXIT.get("z_deployed_hash") == 17, f"drift check code: {EXIT}"
    assert EXIT.get("i_bench") == 18, f"bench check code: {EXIT}"
    with tempfile.TemporaryDirectory() as td:
        ref = Path(td) / "ref.py"
        same = Path(td) / "same.py"
        drifted = Path(td) / "drifted.py"
        ref.write_text("x = 1\n")
        same.write_text("x = 1\n")
        drifted.write_text("x = 2\n")
        ok, d = check_deployed_hash(same, ref)
        assert ok and d["deployed_sha256"] == d["reference_sha256"], (ok, d)
        ok, d = check_deployed_hash(drifted, ref)
        assert not ok and d["deployed_sha256"] != d["reference_sha256"], (ok, d)
        ok, d = check_deployed_hash(Path(td) / "missing.py", ref)
        assert not ok and "error" in d, (ok, d)
    print("test_rdp_smoke: PASS (5 bind cases, distinct exit codes, "
          "3 hash cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Unit tests for launch_dedicated guardrails (D3, no browser).

Covers: user.js prefs, fresh marker profile creation under the
temp dir, refusal of non-marker existing dirs, refusal of paths
outside the temp dir, refusal of owner profile roots, marker
port mismatch. No Zen process is launched here; live launch is
tested on the laptop.
Run: python3 test_launch_dedicated.py
Ports below are arbitrary examples for the pure-logic test only.
"""
import tempfile
from pathlib import Path

import launch_dedicated as ld


def expect_refused(fn, needle):
    try:
        fn()
    except ld.LaunchError as e:
        assert needle in str(e), (needle, str(e))
        return
    raise AssertionError(f"expected LaunchError containing {needle!r}")


def main():
    text = ld.user_js_text(9231)
    for needle in ("devtools.chrome.enabled", "devtools.debugger.remote-enabled",
                   "devtools.debugger.prompt-connection",
                   "devtools.debugger.remote-host", "9231"):
        assert needle in text, needle

    with tempfile.TemporaryDirectory() as td:
        fresh = Path(td) / "prof"
        out = ld.validate_profile_dir(fresh, create=True, port=9231)
        assert out == fresh.resolve()
        marker = ld.read_marker(fresh)
        assert marker and marker["port"] == 9231 and marker["nonce"]
        # marker profile re-validates; wrong port refused
        assert ld.validate_profile_dir(fresh, port=9231) == fresh.resolve()
        expect_refused(lambda: ld.validate_profile_dir(fresh, port=9999),
                       "marker")
        # existing dir without marker refused
        bare = Path(td) / "bare"
        bare.mkdir()
        expect_refused(lambda: ld.validate_profile_dir(bare, create=True,
                                                       port=9231),
                       "without a")
        # missing dir without create refused
        expect_refused(lambda: ld.validate_profile_dir(Path(td) / "nope"),
                       "does not exist")

    # outside the temp dir refused (owner profile shape)
    expect_refused(
        lambda: ld.validate_profile_dir(Path.home() / "zen-rdp-test-prof",
                                        create=True, port=9231),
        "REFUSED")
    # owner profile root refused by name
    expect_refused(
        lambda: ld.validate_profile_dir(
            Path.home() / ".config" / "zen" / "some.profile",
            create=True, port=9231),
        "owner profile root")
    print("test_launch_dedicated: PASS (prefs, marker, 4 refusals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

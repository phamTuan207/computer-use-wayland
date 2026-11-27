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
    # confirm_repost pref (2026-11-28): dedicated profiles only.
    # The pref must be present in the dedicated user.js AND the
    # helper must keep refusing owner-profile roots, so the pref
    # can never land in the owner's profile through this tool.
    assert "dom.confirm_repost.testing.always_accept" in text

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

    # C1: the temp dir itself is not a profile
    expect_refused(
        lambda: ld.validate_profile_dir(
            tempfile.gettempdir(), create=True, port=9231),
        "REFUSED")

    # B4: forged session.json naming a foreign pid is refused by
    # stop() before any signal (nonce mismatch, then cmdline check).
    import json as _json
    import os as _os
    with tempfile.TemporaryDirectory() as td:
        prof = Path(td) / "prof"
        ld.validate_profile_dir(prof, create=True, port=9231)
        marker = ld.read_marker(prof)
        forged = {"pid": _os.getpid(), "profile": str(prof.resolve()),
                  "port": 9231, "nonce": "forged-nonce"}
        ld.session_path(prof).write_text(_json.dumps(forged))
        expect_refused(lambda: ld.stop(prof), "nonce")
        # Correct nonce, but the pid is this test process whose
        # cmdline carries no profile argument; still refused.
        forged["nonce"] = marker["nonce"]
        ld.session_path(prof).write_text(_json.dumps(forged))
        expect_refused(lambda: ld.stop(prof), "profile token")
        # Dead pid with valid files: already-dead, no signal sent.
        import subprocess as _sp
        _dead = _sp.Popen(["/bin/true"])
        _dead.wait()
        forged["pid"] = _dead.pid
        ld.session_path(prof).write_text(_json.dumps(forged))
        out = ld.stop(prof)
        assert out["result"] == "already dead", out

    # C1: launch kills the launched process when the port never
    # listens (no orphan Zen without a session file).
    class FakeProc:
        pid = 424242

        def wait(self, timeout=None):
            return 0

    killed = []
    real_popen, real_wait = ld.subprocess.Popen, ld.wait_for_port
    real_killpg = ld.os.killpg
    ld.subprocess.Popen = lambda *a, **k: FakeProc()
    ld.wait_for_port = lambda *a, **k: False
    ld.os.killpg = lambda pid, sig: killed.append((pid, sig))
    try:
        with tempfile.TemporaryDirectory() as td:
            expect_refused(
                lambda: ld.launch(9239, Path(td) / "p",
                                  zen_bin="/bin/true", timeout=1),
                "did not listen")
    finally:
        ld.subprocess.Popen, ld.wait_for_port = real_popen, real_wait
        ld.os.killpg = real_killpg
    assert killed and killed[0][0] == FakeProc.pid, killed

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

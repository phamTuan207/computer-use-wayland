"""E2E tests for cli-anything-discord (HARNESS Phase 5).

Runs the INSTALLED cli-anything-discord against the REAL Discord desktop
client on this machine (CDP on 127.0.0.1:9229). No mocks of Discord, no
skips: if Discord or CDP is down, the live tests FAIL loudly.

All send/send-file traffic goes ONLY to the Violet Joestar test DM
(channel 865272264831139840, owner-designated). Every send carries a
unique per-run marker so read-back is unambiguous against earlier traffic.

Run on the laptop (where Discord runs):
    CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/discord/tests/test_full_e2e.py -v -s
"""

import json
import os
import shutil
import subprocess
import sys
import time
import uuid

import pytest

TEST_DM = "865272264831139840"
RUN_TOKEN = f"e2e-{time.strftime('%Y%m%d-%H%M')}-{uuid.uuid4().hex[:6]}"


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


def _run_cli(args, timeout=120):
    """Run the installed CLI, return (returncode, parsed --json stdout or raw)."""
    proc = subprocess.run(
        TestCLISubprocess.CLI_BASE + args,
        capture_output=True, text=True, timeout=timeout,
    )
    return proc


def _run_json(args, timeout=120):
    """Run the CLI with --json first (group option precedes the subcommand)."""
    proc = _run_cli(["--json"] + args, timeout=timeout)
    assert proc.returncode == 0, (
        f"CLI failed: {' '.join(args)}\nrc={proc.returncode}\n"
        f"stdout={proc.stdout[:2000]}\nstderr={proc.stderr[:2000]}"
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(
            f"CLI output was not JSON for {' '.join(args)}:\n{proc.stdout[:2000]}"
        )


def _read_messages(limit=10):
    return _run_json(["messages", "read", TEST_DM, "--limit", str(limit)])


def _find_message(messages, text):
    for m in messages:
        if m.get("content") and text in m["content"]:
            return m
    return None


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-discord")

    def test_help(self):
        proc = _run_cli(["--help"])
        assert proc.returncode == 0
        assert "Discord message control" in proc.stdout
        assert "messages" in proc.stdout and "session" in proc.stdout

    def test_status_json(self):
        data = _run_json(["status"])
        assert data["ok"] is True
        assert data["discord_running"] is True
        assert data["cdp_port"] == 9229
        assert data.get("target_url", "").startswith("https://discord.com/channels/")
        print(f"\n  status target: {data.get('target_id')} {data.get('target_url')}")

    def test_servers_list(self):
        data = _run_json(["servers", "list"])
        assert data["ok"] is True
        assert data["count"] > 0
        assert len(data["servers"]) == data["count"]
        print(f"\n  servers: {data['count']}")

    def test_channels_list_dm_contains_test_dm(self):
        data = _run_json(["channels", "list", "--dm"])
        assert data["ok"] is True
        assert data["dm_count"] > 0
        hrefs = [d.get("href", "") for d in data["dms"]]
        assert f"/channels/@me/{TEST_DM}" in hrefs, f"test DM missing from {hrefs}"

    def test_channels_open_test_dm(self):
        data = _run_json(["channels", "open", TEST_DM])
        assert data["ok"] is True
        assert data["url"] == f"https://discord.com/channels/@me/{TEST_DM}"

    def test_messages_read_json_shape(self):
        data = _read_messages(limit=5)
        assert data["ok"] is True
        assert data["channel_id"] == TEST_DM
        assert data["count"] > 0
        for m in data["messages"]:
            assert set(("id", "author", "timestamp", "content", "attachments")) <= set(m), m
            assert m["id"].isdigit(), m
            assert m["author"], m

    def test_session_show(self):
        data = _run_json(["session", "show"])
        assert data["ok"] is True
        assert data["cdp_port"] == 9229
        assert data.get("current_channel_id") == TEST_DM


class TestLiveRead:
    def test_read_returns_real_messages(self):
        data = _read_messages(limit=5)
        assert data["count"] >= 1
        assert data["total_visible"] >= 1
        print(f"\n  read {data['count']} messages, newest id={data['messages'][-1]['id']}")

    def test_read_authors_and_timestamps_filled(self):
        data = _read_messages(limit=10)
        assert data["count"] > 0
        for m in data["messages"]:
            assert m["author"], f"empty author on {m['id']}"
            assert m["timestamp"], f"empty timestamp on {m['id']}"


class TestLiveSend:
    def test_send_returns_ok(self):
        text = f"[cli-anything-discord e2e {RUN_TOKEN}] send-ok probe"
        data = _run_json(["messages", "send", TEST_DM, "--text", text])
        assert data["ok"] is True
        assert data.get("sent") == text
        print(f"\n  sent probe, will verify by read-back: {text}")

    def test_send_verified_by_readback(self):
        text = f"[cli-anything-discord e2e {RUN_TOKEN}] hello from the E2E suite"
        _run_json(["messages", "send", TEST_DM, "--text", text])
        time.sleep(2)
        data = _read_messages(limit=10)
        found = _find_message(data["messages"], text)
        assert found is not None, (
            f"sent text not found in read-back (last 10 ids: "
            f"{[m['id'] for m in data['messages']]})"
        )
        assert found["id"].isdigit()
        print(f"\n  read-back OK: message id={found['id']} author={found['author']!r}")


class TestLiveSendFile:
    def test_send_file_returns_ok(self, tmp_path):
        payload = tmp_path / "discord-e2e-test.txt"
        payload.write_text(f"cli-anything-discord E2E file test {RUN_TOKEN}\n")
        caption = f"[cli-anything-discord e2e {RUN_TOKEN}] file upload"
        data = _run_json(["messages", "send-file", TEST_DM,
                          "--file", str(payload), "--text", caption])
        assert data["ok"] is True
        assert data.get("file") == str(payload)
        print(f"\n  send-file ok: {payload} caption={caption!r}")

    def test_send_file_verified_by_readback_attachment(self, tmp_path):
        payload = tmp_path / "discord-e2e-attach.txt"
        payload.write_text(f"cli-anything-discord E2E attachment {RUN_TOKEN}\n")
        caption = f"[cli-anything-discord e2e {RUN_TOKEN}] attachment check"
        _run_json(["messages", "send-file", TEST_DM,
                   "--file", str(payload), "--text", caption])
        time.sleep(2)
        data = _read_messages(limit=10)
        found = _find_message(data["messages"], caption)
        assert found is not None, (
            f"file caption not found in read-back (last 10 ids: "
            f"{[m['id'] for m in data['messages']]})"
        )
        atts = found.get("attachments") or []
        assert atts, f"no attachment URLs on message {found['id']}: {found}"
        cdn = [a for a in atts if a.startswith(
            f"https://cdn.discordapp.com/attachments/{TEST_DM}/")]
        assert cdn, f"no cdn.discordapp.com attachment for this DM: {atts}"
        print(f"\n  attachment OK: message id={found['id']} url={cdn[0]}")

    def test_send_missing_file_fails_loudly(self):
        proc = _run_cli(["--json", "messages", "send-file", TEST_DM,
                         "--file", "/tmp/does-not-exist-discord-e2e.txt"])
        assert proc.returncode != 0
        data = json.loads(proc.stdout)
        assert data["ok"] is False
        assert "not found" in data["error"].lower()


class TestSessionRelaunch:
    """Quit Discord FULLY, then relaunch via `session start`.

    Runs last (last class in this file; pytest runs in file order): it kills
    the owner's Discord window and brings it back. If any step fails, the
    suite fails loudly (no graceful degradation).
    """

    def test_quit_relaunch_attach_and_read(self):
        # 1. Quit Discord fully via the CLI (requires --force by design).
        stopped = _run_json(["session", "stop", "--force"])
        assert stopped["ok"] is True
        deadline = time.time() + 20
        cdp_down = False
        while time.time() < deadline:
            proc = subprocess.run(
                ["curl", "-s", "-m", "2", "http://127.0.0.1:9229/json/version"],
                capture_output=True, text=True)
            pgrep = subprocess.run(["pgrep", "-x", "Discord"],
                                   capture_output=True, text=True)
            if proc.returncode != 0 and pgrep.returncode != 0:
                cdp_down = True
                break
            time.sleep(1)
        assert cdp_down, "Discord did not quit fully within 20s (CDP still up or process alive)"
        print("\n  Discord fully quit (CDP down, no Discord process)")

        # 2. Relaunch via session start; must report launched: true.
        started = _run_json(["session", "start"], timeout=120)
        assert started["running"] is True
        assert started["launched"] is True, f"expected a real launch, got: {started}"
        assert started["ok"] is True
        print(f"\n  relaunched: launched={started['launched']} target={started.get('target_id')}")

        # 3. Attach + status + a real read prove the relaunched client works.
        attached = _run_json(["session", "attach"])
        assert attached["ok"] is True and attached["attached"] is True
        status = _run_json(["status"])
        assert status["discord_running"] is True
        data = _read_messages(limit=3)
        assert data["ok"] is True and data["count"] > 0
        print(f"\n  post-relaunch read OK: {data['count']} messages, "
              f"newest id={data['messages'][-1]['id']}")

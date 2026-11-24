"""Unit tests for cli-anything-discord core (no Discord needed).

Run: python3 -m pytest cli_anything/discord/tests/test_core.py -v
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from cli_anything.discord.core import session as session_mod  # noqa: E402
from cli_anything.discord.utils import discord_backend as backend  # noqa: E402


def test_locked_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "session.json"
    data = {"cdp_port": 9229, "current_channel_id": "865272264831139840",
            "target_id": "abc", "current_channel_name": "Violet"}
    session_mod.save_session(data, p)
    loaded = session_mod.load_session(p)
    assert loaded["current_channel_id"] == "865272264831139840"
    assert loaded["target_id"] == "abc"
    assert loaded["updated_at"]
    # File is valid JSON, written by the locked path (no truncation corruption).
    assert json.loads(p.read_text())["cdp_port"] == 9229


def test_load_missing_session_returns_defaults(tmp_path):
    loaded = session_mod.load_session(tmp_path / "nope.json")
    assert loaded["cdp_port"] == 9229
    assert loaded["current_channel_id"] is None


def test_load_corrupt_session_returns_defaults(tmp_path):
    p = tmp_path / "session.json"
    p.write_text("{not json")
    loaded = session_mod.load_session(p)
    assert loaded["cdp_port"] == 9229


def test_set_current_channel(tmp_path):
    p = tmp_path / "session.json"
    session_mod.set_current_channel("123", "Some Channel", p)
    loaded = session_mod.load_session(p)
    assert loaded["current_channel_id"] == "123"
    assert loaded["current_channel_name"] == "Some Channel"


def test_double_save_no_corruption(tmp_path):
    p = tmp_path / "session.json"
    for i in range(5):
        session_mod.save_session({"cdp_port": 9229, "target_id": f"t{i}"}, p)
    loaded = session_mod.load_session(p)
    assert loaded["target_id"] == "t4"


def test_test_dm_constant_is_owner_designated_dm():
    assert backend.TEST_DM_CHANNEL_ID == "865272264831139840"


def test_read_js_extracts_attachments():
    # A file send must be verifiable by read-back: each message row needs an
    # `attachments` array of CDN hrefs (added by the test worker, Phase 5).
    assert "attachments" in backend.READ_JS
    assert "cdn.discordapp.com" in backend.READ_JS

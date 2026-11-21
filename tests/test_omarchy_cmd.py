"""Tests for scripts/omarchy_cmd.py (pure builders + usage reader)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import omarchy_cmd


def _usage_doc(**overrides):
    doc = {
        "schemaVersion": 1, "id": "codex", "name": "Codex",
        "updatedAt": "2026-11-21T16:47:33.516267+00:00",
        "ready": True, "tierLabel": "Free",
        "limits": [{"label": "720h window", "percent": 1.0,
                    "resetsAt": "2026-12-12T12:17:17+00:00"}],
        "todayPrompts": 18, "todaySessions": 18,
        "todayTotalTokens": 190927021,
        "todayTokensByModel": {"gpt-6-luna": 190927021},
        "totalPrompts": 1168, "totalSessions": 403, "activeDays": 30,
    }
    doc.update(overrides)
    return doc


class TestShellArgv(unittest.TestCase):
    def test_ping(self):
        self.assertEqual(omarchy_cmd.shell_argv("shell", "ping"),
                         ["omarchy-shell", "shell", "ping"])

    def test_list_plugins(self):
        self.assertEqual(omarchy_cmd.shell_argv("shell", "listPlugins"),
                         ["omarchy-shell", "shell", "listPlugins"])

    def test_toggle_needs_json_object(self):
        self.assertEqual(
            omarchy_cmd.shell_argv("shell", "toggle", '{"menu":"root"}'),
            ["omarchy-shell", "shell", "toggle", '{"menu":"root"}'])
        with self.assertRaises(ValueError):
            omarchy_cmd.shell_argv("shell", "toggle")
        with self.assertRaises(ValueError):
            omarchy_cmd.shell_argv("shell", "toggle", "not-json")
        with self.assertRaises(ValueError):
            omarchy_cmd.shell_argv("shell", "toggle", '["list"]')

    def test_unknown_call_rejected(self):
        for bad in (("shell", "restart"), ("menu", "toggle"),
                    ("shell", "ping", "extra")):
            with self.assertRaises(ValueError):
                omarchy_cmd.shell_argv(*bad)


class TestMenuArgv(unittest.TestCase):
    def test_toggle_system(self):
        self.assertEqual(omarchy_cmd.menu_argv("toggle", "system"),
                         ["omarchy", "menu", "toggle", "system"])

    def test_summon_route_with_dot(self):
        self.assertEqual(omarchy_cmd.menu_argv("summon", "appearance.theme"),
                         ["omarchy", "menu", "summon", "appearance.theme"])

    def test_no_route(self):
        self.assertEqual(omarchy_cmd.menu_argv("ping"),
                         ["omarchy", "menu", "ping"])

    def test_bad_action_and_route(self):
        with self.assertRaises(ValueError):
            omarchy_cmd.menu_argv("open")
        for bad in ("", "a b", "../etc", "-x"):
            with self.assertRaises(ValueError):
                omarchy_cmd.menu_argv("toggle", bad)


class TestNotifyArgv(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(
            omarchy_cmd.notify_argv("Fleet done", "all lanes green"),
            ["omarchy", "notification", "send", "Fleet done",
             "all lanes green"])

    def test_critical_with_action(self):
        self.assertEqual(
            omarchy_cmd.notify_argv(
                "Blocker", "session failed", urgency="critical",
                action=("Open log", "xdg-open", "/tmp/f.log")),
            ["omarchy", "notification", "send", "-u", "critical",
             "Blocker", "session failed", "--action", "Open log",
             "xdg-open", "/tmp/f.log"])

    def test_exec_form(self):
        self.assertEqual(
            omarchy_cmd.notify_argv("Hi", exec_cmd=("myprog", "--flag")),
            ["omarchy", "notification", "send", "Hi",
             "--exec", "myprog", "--flag"])

    def test_rejects_both_action_and_exec(self):
        with self.assertRaises(ValueError):
            omarchy_cmd.notify_argv("Hi", action=("L", "p"),
                                    exec_cmd=("p",))

    def test_rejects_bad_headline_and_urgency(self):
        for bad in ("", "two\nlines", None):
            with self.assertRaises(ValueError):
                omarchy_cmd.notify_argv(bad)
        with self.assertRaises(ValueError):
            omarchy_cmd.notify_argv("Hi", urgency="high")


class TestScreenshotAndOcr(unittest.TestCase):
    def test_fullscreen_save(self):
        self.assertEqual(omarchy_cmd.screenshot_argv(),
                         ["omarchy", "capture", "screenshot",
                          "fullscreen", "save"])
        self.assertEqual(omarchy_cmd.screenshot_argv("smart", "copy"),
                         ["omarchy", "capture", "screenshot",
                          "smart", "copy"])

    def test_gui_modes_rejected(self):
        for bad in ("region", "windows", "scroll"):
            with self.assertRaises(ValueError):
                omarchy_cmd.screenshot_argv(bad)
        with self.assertRaises(ValueError):
            omarchy_cmd.screenshot_argv("fullscreen", "print")

    def test_grim_and_tesseract(self):
        self.assertEqual(omarchy_cmd.grim_argv("10,20 800x600"),
                         ["grim", "-g", "10,20 800x600", "-"])
        self.assertEqual(omarchy_cmd.tesseract_argv(),
                         ["tesseract", "stdin", "stdout", "--oem", "1",
                          "--psm", "6", "-l", "eng", "--dpi", "300",
                          "-c", "preserve_interword_spaces=1"])
        self.assertEqual(
            omarchy_cmd.ocr_shell("10,20 800x600"),
            "grim -g '10,20 800x600' - | tesseract stdin stdout "
            "--oem 1 --psm 6 -l eng --dpi 300 "
            "-c preserve_interword_spaces=1")

    def test_bad_geometry(self):
        for bad in ("", "10,20", "10,20 800", "x,y 800x600",
                    "-1,0 10x10", "0,0 0x600", "0,0 800x600 extra"):
            with self.assertRaises(ValueError):
                omarchy_cmd.grim_argv(bad)


class TestUsageReader(unittest.TestCase):
    def _write(self, directory, agent, doc):
        path = os.path.join(directory, agent + ".json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle)
        return path

    def test_reads_live_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "codex", _usage_doc())
            summary = omarchy_cmd.read_usage("codex", state_dir=tmp)
        self.assertEqual(summary["agent"], "codex")
        self.assertEqual(summary["today_prompts"], 18)
        self.assertEqual(summary["today_tokens"], 190927021)
        self.assertEqual(summary["today_tokens_by_model"],
                         {"gpt-6-luna": 190927021})
        self.assertEqual(summary["limits"],
                         [{"label": "720h window", "percent": 1.0,
                           "resets_at": "2026-12-12T12:17:17+00:00"}])
        self.assertEqual(summary["total_prompts"], 1168)
        self.assertEqual(summary["active_days"], 30)

    def test_summary_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "codex", _usage_doc())
            summary = omarchy_cmd.read_usage("codex", state_dir=tmp)
        self.assertEqual(
            omarchy_cmd.usage_summary_text(summary),
            "codex: today 18 prompts / 190,927,021 tokens; "
            "(gpt-6-luna 190,927,021); 720h window 1.0% resets "
            "2026-12-12; total 1168 prompts / 403 sessions / "
            "30 active days")

    def test_missing_file_and_bad_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                omarchy_cmd.read_usage("codex", state_dir=tmp)
            with self.assertRaises(FileNotFoundError):
                omarchy_cmd.read_usage("opencode", state_dir=tmp)
        for bad in ("", "Codex", "../codex", "codex.json", "a" * 65):
            with self.assertRaises(ValueError):
                omarchy_cmd.read_usage(bad, state_dir="/tmp")

    def test_malformed_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "codex.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{not json")
            with self.assertRaises(ValueError):
                omarchy_cmd.read_usage("codex", state_dir=tmp)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write('["not", "an", "object"]')
            with self.assertRaises(ValueError):
                omarchy_cmd.read_usage("codex", state_dir=tmp)

    def test_usage_cli_argv(self):
        self.assertEqual(omarchy_cmd.usage_cli_argv("codex"),
                         ["omarchy", "agent", "usage", "codex",
                          "--limits-only"])
        self.assertEqual(omarchy_cmd.usage_cli_argv("codex", False),
                         ["omarchy", "agent", "usage", "codex"])
        with self.assertRaises(ValueError):
            omarchy_cmd.usage_cli_argv("../codex")


class TestOmarchyPath(unittest.TestCase):
    def test_with_path_sets_only_when_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = omarchy_cmd.with_omarchy_path({"PATH": "/usr/bin"},
                                                default=tmp)
            self.assertEqual(out["OMARCHY_PATH"], tmp)
            self.assertEqual(out["PATH"], "/usr/bin")
            out2 = omarchy_cmd.with_omarchy_path(
                {"OMARCHY_PATH": "/custom"}, default=tmp)
            self.assertEqual(out2["OMARCHY_PATH"], "/custom")
        out3 = omarchy_cmd.with_omarchy_path(
            {}, default="/nonexistent-omarchy-path")
        self.assertNotIn("OMARCHY_PATH", out3)

    def test_omarchy_path_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(omarchy_cmd.omarchy_path(default=tmp), tmp)
        self.assertIsNone(
            omarchy_cmd.omarchy_path(default="/nonexistent-omarchy-path"))


class TestCli(unittest.TestCase):
    def test_usage_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "codex.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(_usage_doc(), handle)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = omarchy_cmd.main(
                    ["usage", "codex", "--state-dir", tmp])
            self.assertEqual(code, 0)
            self.assertIn("codex: today 18 prompts", buf.getvalue())

    def test_usage_missing_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = omarchy_cmd.main(["usage", "codex", "--state-dir", tmp])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()

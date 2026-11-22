"""Tests for scripts/hypr_cmd.py (pure command builders)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import hypr_cmd


class TestFocusWorkspace(unittest.TestCase):
    def test_workspace_1(self):
        self.assertEqual(
            hypr_cmd.focus_workspace(1),
            ["hyprctl", "dispatch", "hl.dsp.focus({ workspace = 1 })"])

    def test_workspace_10(self):
        self.assertEqual(
            hypr_cmd.focus_workspace(10),
            ["hyprctl", "dispatch", "hl.dsp.focus({ workspace = 10 })"])

    def test_rejects_out_of_range(self):
        for bad in (0, 11, -1):
            with self.assertRaises(ValueError):
                hypr_cmd.focus_workspace(bad)

    def test_rejects_non_int(self):
        for bad in ("2", 2.0, True, None):
            with self.assertRaises(ValueError):
                hypr_cmd.focus_workspace(bad)

    def test_next_prev_former(self):
        self.assertEqual(
            hypr_cmd.focus_next_workspace(),
            ["hyprctl", "dispatch", 'hl.dsp.focus({ workspace = "m+1" })'])
        self.assertEqual(
            hypr_cmd.focus_prev_workspace(),
            ["hyprctl", "dispatch", 'hl.dsp.focus({ workspace = "m-1" })'])
        self.assertEqual(
            hypr_cmd.focus_former_workspace(),
            ["hyprctl", "dispatch",
             'hl.dsp.focus({ workspace = "previous_per_monitor" })'])


class TestDirectionAndClose(unittest.TestCase):
    def test_all_directions(self):
        for d in ("l", "r", "u", "d"):
            self.assertEqual(
                hypr_cmd.focus_direction(d),
                ["hyprctl", "dispatch",
                 'hl.dsp.focus({ direction = "%s" })' % d])

    def test_rejects_bad_direction(self):
        for bad in ("left", "L", "", None):
            with self.assertRaises(ValueError):
                hypr_cmd.focus_direction(bad)

    def test_close_window(self):
        self.assertEqual(
            hypr_cmd.close_window(),
            ["hyprctl", "dispatch", "hl.dsp.window.close()"])


class TestDispatchArgv(unittest.TestCase):
    def test_requires_hl_dsp(self):
        with self.assertRaises(ValueError):
            hypr_cmd.dispatch_argv("workspace 2")
        with self.assertRaises(ValueError):
            hypr_cmd.dispatch_argv("hl.dsp.workspace.goto(2)")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            hypr_cmd.dispatch_argv("")


class TestDesktopEnv(unittest.TestCase):
    def test_explicit_signature(self):
        env = hypr_cmd.desktop_env(signature="sig-1")
        self.assertEqual(env["HYPRLAND_INSTANCE_SIGNATURE"], "sig-1")
        self.assertEqual(env["XDG_RUNTIME_DIR"], "/run/user/1000")
        self.assertEqual(env["WAYLAND_DISPLAY"], "wayland-1")

    def test_from_dir_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "abc_sig"))
            env = hypr_cmd.desktop_env(signature_dir=tmp)
            self.assertEqual(env["HYPRLAND_INSTANCE_SIGNATURE"], "abc_sig")

    def test_from_dir_listing_skips_files(self):
        """R4: only directories are signatures; a stray file that
        sorts first must never be picked as the instance signature."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "aaa_file"), "w") as handle:
                handle.write("not a signature")
            os.mkdir(os.path.join(tmp, "zzz_sig"))
            env = hypr_cmd.desktop_env(signature_dir=tmp)
            self.assertEqual(env["HYPRLAND_INSTANCE_SIGNATURE"], "zzz_sig")

    def test_empty_dir_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                hypr_cmd.desktop_env(signature_dir=tmp)


class TestFocusApp(unittest.TestCase):
    def _clients(self):
        return [
            {"address": "0xaaa", "class": "Zen",
             "title": "Muse", "focusHistoryID": 5},
            {"address": "0xbbb", "class": "kitty",
             "title": "agent", "initialClass": "org.omarchy.agent",
             "initialTitle": "codex-y5", "focusHistoryID": 1},
            {"address": "0xccc", "class": "Zen",
             "title": "Gmail", "focusHistoryID": 0},
        ]

    def test_clients_argv(self):
        self.assertEqual(hypr_cmd.focus_app_clients_argv(),
                         ["hyprctl", "clients", "-j"])

    def test_class_match_most_recent_first(self):
        # Two Zen windows; focusHistoryID 0 (Gmail) is most recent.
        self.assertEqual(
            hypr_cmd.pick_focus_address(self._clients(), "zen"), "0xccc")

    def test_class_regex_case_insensitive(self):
        self.assertEqual(
            hypr_cmd.pick_focus_address(self._clients(), "ZEN"), "0xccc")

    def test_agent_title_fallback(self):
        # No class matches "codex"; the agent window matches by title.
        self.assertEqual(
            hypr_cmd.pick_focus_address(self._clients(), "codex"), "0xbbb")

    def test_no_match(self):
        self.assertIsNone(
            hypr_cmd.pick_focus_address(self._clients(), "slack"))

    def test_bad_pattern(self):
        for bad in ("", "(", None):
            with self.assertRaises(ValueError):
                hypr_cmd.pick_focus_address(self._clients(), bad)
        with self.assertRaises(ValueError):
            hypr_cmd.pick_focus_address("not-a-list", "zen")

    def test_focus_window_argv(self):
        self.assertEqual(
            hypr_cmd.focus_window_argv("0x557052b62dd0"),
            ["hyprctl", "dispatch",
             'hl.dsp.focus({ window = "address:0x557052b62dd0" })'])
        for bad in ("", "557052b62dd0", "0xZZZ", None):
            with self.assertRaises(ValueError):
                hypr_cmd.focus_window_argv(bad)


class TestLaunchOrFocus(unittest.TestCase):
    def _clients(self):
        return [
            {"address": "0x111", "class": "Zen", "title": "Muse"},
            {"address": "0x222", "class": "foot", "title": "terminal"},
        ]

    def test_word_match_class_or_title(self):
        self.assertEqual(
            hypr_cmd.pick_launch_or_focus_address(self._clients(), "zen"),
            "0x111")
        self.assertEqual(
            hypr_cmd.pick_launch_or_focus_address(self._clients(), "terminal"),
            "0x222")

    def test_partial_word_does_not_match(self):
        # "ze" is not a whole word in "Zen".
        self.assertIsNone(
            hypr_cmd.pick_launch_or_focus_address(self._clients(), "ze"))
        self.assertIsNone(
            hypr_cmd.pick_launch_or_focus_address(self._clients(), "slack"))

    def test_first_in_order(self):
        clients = [
            {"address": "0x1", "class": "Zen", "title": "a"},
            {"address": "0x2", "class": "zen", "title": "b"},
        ]
        self.assertEqual(
            hypr_cmd.pick_launch_or_focus_address(clients, "zen"), "0x1")

    def test_launch_cmd_default_and_custom(self):
        self.assertEqual(hypr_cmd.launch_or_focus_cmd("zen"),
                         "uwsm-app -- zen")
        self.assertEqual(hypr_cmd.launch_or_focus_cmd("zen", "zen-browser"),
                         "zen-browser")
        for bad in ("", None):
            with self.assertRaises(ValueError):
                hypr_cmd.launch_or_focus_cmd(bad)
        for bad in ("", 123):
            with self.assertRaises(ValueError):
                hypr_cmd.launch_or_focus_cmd("zen", bad)


if __name__ == "__main__":
    unittest.main()

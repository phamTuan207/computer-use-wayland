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

    def test_empty_dir_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                hypr_cmd.desktop_env(signature_dir=tmp)


if __name__ == "__main__":
    unittest.main()

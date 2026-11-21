"""Offline indicator watchdog tests; no Hyprland or GUI is contacted."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import indicator
import cursor_session


class LayerPresence(unittest.TestCase):
    env = {'PATH': '/usr/bin', 'HYPRLAND_INSTANCE_SIGNATURE': 'fixture'}

    def probe(self, payload):
        result = SimpleNamespace(stdout=json.dumps(payload), returncode=0)
        with patch.object(indicator.shutil, 'which', return_value='/usr/bin/hyprctl'), \
                patch.object(indicator.subprocess, 'run', return_value=result):
            return indicator.layer_surface_present(self.env)

    def test_finds_indicator_namespace_nested_in_monitor_layers(self):
        payload = {'DP-1': [{'levels': [{'layers': [
            {'namespace': 'background'},
            {'namespace': 'computer-use-indicator'},
        ]}]}]}
        self.assertIs(self.probe(payload), True)

    def test_recognized_other_layers_mean_indicator_is_missing(self):
        self.assertIs(self.probe({'DP-1': [{'namespace': 'background'}]}), False)

    def test_recognized_empty_layer_list_means_indicator_is_missing(self):
        self.assertIs(self.probe({'DP-1': {'levels': [{'layers': []}]}}), False)

    def test_empty_or_unrecognized_json_is_unknown(self):
        self.assertIsNone(self.probe([]))
        self.assertIsNone(self.probe({'DP-1': [{'name': 'unrecognized'}]}))


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class FakeNative:
    def __init__(self, status='visible', exited=False):
        self.process = SimpleNamespace(poll=lambda: 1 if exited else None)
        self.status = status
        self.commands = []
        self.closed = False

    def command(self, command):
        self.commands.append(command)
        if command == 'status':
            return self.status
        if command == 'show':
            self.status = 'visible'
            return 'visible'
        if command == 'hide':
            self.status = 'hidden'
            return 'hidden'
        return 'ok'

    def close(self):
        self.closed = True


class FakeCursor:
    def __init__(self):
        self.commands = []

    def command(self, command):
        self.commands.append(command)
        return 'ok'


class Watchdog(unittest.TestCase):
    env = {'PATH': '/usr/bin'}

    def build(self, native, *, probe=None, factory=None, metrics=None):
        self.clock = FakeClock()
        self.cursor = FakeCursor()
        self.visuals = cursor_session.SessionVisuals(native, self.cursor)
        return indicator.IndicatorWatchdog(
            self.env, self.visuals, escape_available=True,
            layer_probe=probe or (lambda _env: None),
            native_factory=factory,
            monotonic=self.clock,
            metric=metrics or Mock())

    def test_unexpected_hidden_overlay_is_shown_again(self):
        native = FakeNative(status='hidden')
        watchdog = self.build(native)
        watchdog.check()
        self.assertIn('show', native.commands)
        self.assertEqual(self.cursor.commands, ['show'])
        self.assertFalse(self.visuals.expected_hidden)

    def test_capture_hide_is_not_mistaken_for_lost_overlay(self):
        native = FakeNative()
        watchdog = self.build(native)
        self.visuals.command('hide')
        watchdog.check()
        self.assertNotIn('show', native.commands)
        self.assertTrue(self.visuals.expected_hidden)

    def test_unknown_layer_schema_does_not_restart(self):
        native = FakeNative()
        factory = Mock()
        watchdog = self.build(native, probe=lambda _env: None, factory=factory)
        watchdog.check()
        self.assertIs(self.visuals.native, native)
        factory.assert_not_called()

    def test_two_confirmed_missing_layer_probes_restart_indicator(self):
        native = FakeNative()
        replacement = FakeNative()
        factory = Mock(return_value=replacement)
        watchdog = self.build(native, probe=lambda _env: False, factory=factory)
        watchdog.check()
        self.clock.now = 2
        watchdog.check()
        self.assertTrue(native.closed)
        self.assertIs(self.visuals.native, replacement)
        factory.assert_called_once()

    def test_exited_child_is_restarted(self):
        native = FakeNative(exited=True)
        replacement = FakeNative()
        factory = Mock(return_value=replacement)
        watchdog = self.build(native, factory=factory)
        watchdog.check()
        self.assertTrue(native.closed)
        self.assertIs(self.visuals.native, replacement)

    def test_restart_rate_limit_fails_clearly(self):
        natives = [FakeNative(exited=True) for _ in range(4)]
        factory = Mock(side_effect=natives[1:])
        watchdog = self.build(natives[0], factory=factory)
        for second in range(3):
            self.clock.now = second
            watchdog.check()
        self.clock.now = 3
        with self.assertRaisesRegex(RuntimeError, 'indicator repeatedly lost'):
            watchdog.check()


if __name__ == '__main__':
    unittest.main()

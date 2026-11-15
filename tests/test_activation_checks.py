"""Bounded profile readiness checks with mocked RPC and metadata status."""
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import activation_checks


class ActivationChecksTests(unittest.TestCase):
    def test_returns_only_after_clean_config_and_ready_glass(self):
        with mock.patch.object(activation_checks.subprocess, 'check_output', return_value=''), \
             mock.patch.object(activation_checks.indicator, 'liquid_available',
                               side_effect=[False, True]) as status, \
             mock.patch.object(activation_checks.time, 'sleep') as sleep:
            self.assertTrue(activation_checks.wait_for_profile({}))
        self.assertEqual(status.call_args_list, [
            mock.call({}, ready=True), mock.call({}, ready=True)])
        sleep.assert_called_once_with(0.1)

    def test_config_errors_time_out_with_a_bounded_read_only_failure(self):
        with mock.patch.object(activation_checks.subprocess, 'check_output',
                               return_value='fixture error'), \
             mock.patch.object(activation_checks.time, 'monotonic', side_effect=[0, 9]), \
             mock.patch.object(activation_checks.time, 'sleep') as sleep, \
             self.assertRaisesRegex(RuntimeError, 'config reload did not reach'):
            activation_checks.wait_for_profile({}, timeout=8)
        sleep.assert_not_called()

    def test_configerrors_query_is_bounded_and_read_only(self):
        with mock.patch.object(activation_checks.subprocess, 'check_output', return_value='') as query, \
             mock.patch.object(activation_checks.indicator, 'liquid_available', return_value=True):
            activation_checks.wait_for_profile({'HYPRLAND_INSTANCE_SIGNATURE': 'fixture'})
        query.assert_called_once_with(['hyprctl', 'configerrors'],
                                      env={'HYPRLAND_INSTANCE_SIGNATURE': 'fixture'},
                                      text=True, timeout=2)


if __name__ == '__main__':
    unittest.main()

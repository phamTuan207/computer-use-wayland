import copy
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import tc02_controller


EMPTY_PROCESSES = {
    'process_counts_by_name': {},
    'imv_processes': [],
    'code_process_count': 0,
}


class Tc02DesktopHygieneTests(unittest.TestCase):
    def make_controller(self, windows, *, processes=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-hygiene-unit-test', temporary.name)
        controller.emit = Mock()
        patches = (
            patch.object(tc02_controller, 'gui_environment', return_value={}),
            patch.object(tc02_controller.Tc02Controller, 'current_clients', return_value=windows),
            patch.object(tc02_controller, 'hypr_query', return_value={'address': '0xactive'}),
            patch.object(tc02_controller, 'process_inventory',
                         return_value=processes or EMPTY_PROCESSES),
        )
        for item in patches:
            item.start()
            self.addCleanup(item.stop)
        return controller

    @staticmethod
    def window(address, cls, title, workspace='1'):
        return {
            'address': address,
            'class': cls,
            'title': title,
            'at': [0, 0],
            'size': [900, 700],
            'workspace': workspace,
        }

    @staticmethod
    def hygiene_evidence(controller):
        return next(call.kwargs for call in controller.emit.call_args_list
                    if call.args[0] == 'desktop-hygiene')

    def test_zen_class_is_allowed_and_admitted_after_p0(self):
        zen = self.window('0xzen', 'ZeN', 'A user tab')
        controller = self.make_controller([zen])

        controller._check_desktop_hygiene()

        self.assertEqual(controller.known_background, [zen])
        evidence = self.hygiene_evidence(controller)
        self.assertEqual(evidence['allow_listed_windows'], [
            {'window': zen, 'reasons': ['zen-class']}])
        self.assertEqual(evidence['unexpected_windows'], [])
        controller._assert_no_unexpected_windows([dict(zen, workspace=None)], [])

    def test_special_workspace_is_allowed_and_admitted_after_p0(self):
        background = self.window(
            '0xdrop', 'org.omarchy.herdrdrop', 'omarchy: Jarvis', 'special:herdrdrop')
        controller = self.make_controller([background])

        controller._check_desktop_hygiene()

        self.assertEqual(controller.known_background, [background])
        evidence = self.hygiene_evidence(controller)
        self.assertEqual(evidence['allow_listed_windows'], [
            {'window': background, 'reasons': ['special-workspace']}])
        self.assertEqual(evidence['unexpected_windows'], [])
        controller._assert_no_unexpected_windows([background], [])

    def test_exact_drift_window_is_allowed_and_admitted_after_p0(self):
        drift = self.window('0xdrift', 'KiTtY', 'DrIfT')
        controller = self.make_controller([drift])

        controller._check_desktop_hygiene()

        self.assertEqual(controller.known_background, [drift])
        evidence = self.hygiene_evidence(controller)
        self.assertEqual(evidence['allow_listed_windows'], [
            {'window': drift, 'reasons': ['music-player-drift']}])
        self.assertEqual(evidence['unexpected_windows'], [])
        controller._assert_no_unexpected_windows([drift], [])

    def test_different_kitty_window_still_fails_p0(self):
        kitty = self.window('0xkitty', 'kitty', 'another terminal')
        controller = self.make_controller([kitty])

        with self.assertRaises(tc02_controller.Escalate) as raised:
            controller._check_desktop_hygiene()

        self.assertEqual(raised.exception.step, 'P0')
        self.assertTrue(raised.exception.hygiene)
        self.assertEqual(self.hygiene_evidence(controller)['unexpected_windows'], [kitty])

    def test_window_line_preserves_hyprland_workspace_without_identity_change(self):
        first = self.window('0xmove', 'app', 'Window', {'name': '1'})
        moved = dict(first, workspace={'name': 'special:test'})

        first_line = tc02_controller.window_line(first)
        moved_line = tc02_controller.window_line(moved)

        self.assertEqual(first_line['workspace'], '1')
        self.assertEqual(moved_line['workspace'], 'special:test')
        self.assertTrue(tc02_controller.same_window_identity(first_line, moved_line))

    def test_s2_timing_log_records_response_fields_without_inventing_capture_time(self):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(plan, 'tc02-s2-timing-unit-test', '/tmp')
        controller.emit = Mock()
        controller._assert_fresh = Mock()
        controller._resolve_action = lambda action, observation: action
        response = {'ok': True, 'completed': 3, 'execution_ms': 123.5,
                    'after_skipped': True}
        controller.broker_driver = Mock(return_value=(response, {}))

        controller._act(plan['steps'][4], {
            'id': 'observation', 'observation': '/tmp/unused-observation.json'}, '0xeditor')

        event = next(call.kwargs for call in controller.emit.call_args_list
                     if call.args[0] == 's2-act-timing')
        self.assertEqual(event, {
            'execution_ms': 123.5,
            'after_capture_ms': None,
            'after_skipped': True,
            'completed': 3,
            'ok': True,
        })

    def test_non_listed_window_still_fails_p0(self):
        ordinary = self.window('0xother', 'org.mozilla.firefox', 'Other app')
        controller = self.make_controller([ordinary])

        with self.assertRaises(tc02_controller.Escalate) as raised:
            controller._check_desktop_hygiene()

        self.assertEqual(raised.exception.step, 'P0')
        self.assertTrue(raised.exception.hygiene)
        self.assertEqual(self.hygiene_evidence(controller)['unexpected_windows'], [ordinary])

    def test_anr_window_fails_even_when_its_class_is_allowed(self):
        anr = self.window('0xzen', 'zen', 'Application Not Responding')
        controller = self.make_controller([anr])

        with self.assertRaises(tc02_controller.Escalate) as raised:
            controller._check_desktop_hygiene()

        self.assertEqual(raised.exception.step, 'P0')
        self.assertTrue(raised.exception.hygiene)
        self.assertEqual(self.hygiene_evidence(controller)['anr_windows'], [anr])

    def test_imv_process_still_fails_p0(self):
        zen = self.window('0xzen', 'zen', 'A user tab')
        processes = dict(EMPTY_PROCESSES, imv_processes=[
            {'pid': 41, 'comm': 'imv', 'cmdline': 'imv image.png'}])
        controller = self.make_controller([zen], processes=processes)

        with self.assertRaises(tc02_controller.Escalate) as raised:
            controller._check_desktop_hygiene()

        self.assertEqual(raised.exception.step, 'P0')
        self.assertTrue(raised.exception.hygiene)
        self.assertTrue(self.hygiene_evidence(controller)['processes']['imv_processes'])

    def test_preexisting_blank_txt_vscode_window_still_fails_p0(self):
        zen = self.window('0xzen', 'zen', 'A user tab')
        blank = self.window('0xvscode', 'com.microsoft.VSCode', 'blank.txt - Visual Studio Code')
        controller = self.make_controller([zen, blank])

        with self.assertRaises(tc02_controller.Escalate) as raised:
            controller._check_desktop_hygiene()

        self.assertEqual(raised.exception.step, 'P0')
        self.assertTrue(raised.exception.hygiene)
        self.assertIn(blank, self.hygiene_evidence(controller)['unexpected_windows'])


class Tc02SampleTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-s2-sample-unit-test', temporary)
        controller.emit = Mock()
        return controller

    def test_record_s2_sample_emits_censored_bound_and_appends_summary_entry(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            dialog = {
                'address': '0xdialog', 'class': 'xdg-desktop-portal-gtk',
                'title': 'Save As', 'at': [0, 0], 'size': [875, 600],
                'workspace': '1',
            }

            controller.record_s2_sample(
                act_done_mono=100.0, windows_done_mono=100.25, dialog=dialog)

            self.assertEqual(controller.emit.call_count, 1)
            call = controller.emit.call_args
            self.assertEqual(call.args, ('s2-sample',))
            self.assertEqual(call.kwargs, {
                'sample_ms': 250.0,
                'definition': 'Monotonic milliseconds from the return of the S2 act result to the return of the S2 windows result that first lists the Save As dialog.',
                'wait_ms': 474,
                'menu_open_latency_ms': {
                    'censored': True,
                    'upper_bound_ms': 474,
                    'evidence': 'Save As dialog appeared after the row click, so the menu was open when the row was clicked',
                },
                'dialog_address': '0xdialog',
                'dialog': dialog,
            })
            self.assertEqual(controller.s2_samples, [{
                'sample_ms': 250.0,
                'wait_ms': 474,
                'menu_open_latency_censored_upper_bound_ms': 474,
                'dialog_address': '0xdialog',
            }])

    def test_record_s2_sample_rejects_negative_span_without_recording(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)

            with self.assertRaises(ValueError):
                controller.record_s2_sample(
                    act_done_mono=100.25, windows_done_mono=100.0,
                    dialog={'address': '0xdialog'})

            controller.emit.assert_not_called()
            self.assertEqual(controller.s2_samples, [])

    def test_validate_plan_requires_both_sample_definitions(self):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        schema = tc02_controller.load_json(tc02_controller.DEFAULT_SCHEMA)

        self.assertTrue(tc02_controller.validate_plan(plan, schema))
        for key in ('checkpoint_sample', 'menu_open_latency'):
            with self.subTest(missing=key):
                invalid = copy.deepcopy(plan)
                del invalid['wait_tuning'][key]
                with self.assertRaises(ValueError):
                    tc02_controller.validate_plan(invalid, schema)

    def test_checkpoint_sample_target_does_not_change_historical_wait(self):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        schema = tc02_controller.load_json(tc02_controller.DEFAULT_SCHEMA)
        plan['wait_tuning']['checkpoint_sample']['target_samples'] = 25

        self.assertTrue(tc02_controller.validate_plan(plan, schema))
        self.assertEqual(plan['wait_tuning']['selected_wait_ms'], 474)

    def test_summary_includes_s2_samples(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            sample = {
                'sample_ms': 250.0,
                'wait_ms': 474,
                'menu_open_latency_censored_upper_bound_ms': 474,
                'dialog_address': '0xdialog',
            }
            controller.s2_samples.append(sample)

            controller._summary('PASS')

            summary = tc02_controller.load_json(controller.summary_path)
            self.assertEqual(summary['s2_samples'], [sample])


if __name__ == '__main__':
    unittest.main()

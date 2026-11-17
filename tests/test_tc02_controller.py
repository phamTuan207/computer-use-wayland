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


if __name__ == '__main__':
    unittest.main()

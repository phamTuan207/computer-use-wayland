import copy
import hashlib
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


class Tc02BrokerPreflightTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-broker-preflight-unit-test', temporary)
        controller.emit = Mock()
        return controller

    def clean_status(self, loaded_code_sha256):
        return {
            'ok': True,
            'broker_generation': 'a' * 32,
            'loaded_code_sha256': loaded_code_sha256,
            'started_git_head': 'b' * 40,
            'state': 'idle',
            'driver': 'idle',
            'guardian': 'idle',
            'active_sequence': None,
            'error': None,
            'recovery': 'none',
            'cancelled': False,
        }

    def test_matching_loaded_code_hash_passes_preflight(self):
        source = tc02_controller.Path(__file__).resolve().parents[1] / 'scripts' / 'session_remote.py'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.run_remote = Mock(return_value=(self.clean_status(digest), None))

            controller._ensure_clean_broker()

        self.assertEqual(controller.broker_generation, 'a' * 32)
        event = next(call.kwargs for call in controller.emit.call_args_list
                     if call.args[0] == 'broker-preflight')
        self.assertTrue(event['code_matches'])
        self.assertEqual(event['loaded_code_sha256'], digest)
        self.assertEqual(event['disk_code_sha256'], digest)

    def test_stale_loaded_code_hash_escalates_fail_closed(self):
        source = tc02_controller.Path(__file__).resolve().parents[1] / 'scripts' / 'session_remote.py'
        disk_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        stale_hash = '0' * 64 if disk_hash != '0' * 64 else '1' * 64
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.run_remote = Mock(return_value=(self.clean_status(stale_hash), None))

            with self.assertRaises(tc02_controller.Escalate) as raised:
                controller._ensure_clean_broker()

        self.assertEqual(raised.exception.step, 'P1')
        self.assertIn('broker code stale, restart the relay', raised.exception.reason)


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


class Tc02EditorLifecycleTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-editor-lifecycle-unit-test', temporary)
        controller.gui_env = {'WAYLAND_DISPLAY': 'wayland-test'}
        controller.emit = Mock()
        controller.editor = {
            'address': '0xeditor', 'class': 'com.microsoft.VSCode',
            'title': 'blank.txt - Visual Studio Code', 'at': [0, 0],
            'size': [933, 1180], 'workspace': '1',
        }
        return controller

    def test_dispatch_hyprland_uses_lua_argv_and_controller_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            lua = 'hl.dsp.window.close({ window = "address:0xeditor" })'
            completed = tc02_controller.subprocess.CompletedProcess(
                ['hyprctl', 'dispatch', lua], 0, 'ok\n', '')

            with patch.object(tc02_controller.subprocess, 'run', return_value=completed) as run:
                self.assertEqual(controller._dispatch_hyprland(lua), 'ok')

            run.assert_called_once_with(
                ['hyprctl', 'dispatch', lua], env=controller.gui_env,
                capture_output=True, text=True, timeout=5)

    def test_dispatch_hyprland_escalates_with_stderr(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            completed = tc02_controller.subprocess.CompletedProcess(
                ['hyprctl', 'dispatch', 'bad lua'], 7, '', 'parser rejected address')

            with patch.object(tc02_controller.subprocess, 'run', return_value=completed):
                with self.assertRaises(tc02_controller.Escalate) as raised:
                    controller._dispatch_hyprland('bad lua')

            self.assertIn('parser rejected address', raised.exception.reason)

    def test_lease_directory_is_private_and_under_computer_use_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            with patch.object(tc02_controller.Path, 'home', return_value=tc02_controller.Path(temporary)):
                lease_path = controller._create_lease_path()

            self.assertEqual(lease_path, tc02_controller.Path(temporary) /
                             '.cache/agent-computer-use/leases' /
                             'tc02-editor-lifecycle-unit-test/session.lease')
            self.assertEqual(lease_path.parent.stat().st_mode & 0o777, 0o700)
            self.assertFalse(lease_path.exists())

    def test_editor_geometry_dispatches_then_waits_through_transitional_size(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller._dispatch_hyprland = Mock(return_value='ok')
            transitional = dict(controller.editor, size=[933, 1180])
            settled = dict(controller.editor, size=[901, 1176])
            controller.current_clients = Mock(side_effect=[[transitional], [settled]])
            with patch.object(tc02_controller.time, 'sleep') as sleep:
                controller._set_editor_geometry()

            address = 'address:0xeditor'
            self.assertEqual(controller._dispatch_hyprland.call_args_list, [
                unittest.mock.call(
                    f'hl.dsp.window.float({{ window = "{address}", action = "set" }})'),
                unittest.mock.call(
                    f'hl.dsp.window.resize({{ window = "{address}", x = 901, y = 1176 }})'),
                unittest.mock.call(
                    f'hl.dsp.window.center({{ window = "{address}" }})'),
            ])
            self.assertEqual(controller.current_clients.call_count, 2)
            sleep.assert_called_once_with(.25)
            self.assertEqual(controller.editor['size'], [901, 1176])
            settled_event = next(call.kwargs for call in controller.emit.call_args_list
                                 if call.args[0] == 'editor-geometry-settled')
            self.assertEqual(settled_event['observed_sizes'], [[933, 1180], [901, 1176]])

    def test_editor_teardown_escalates_sigterm_to_sigkill(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            process = Mock()
            process.pid = 4321
            process.poll.side_effect = [None, None]
            process.wait.side_effect = [
                tc02_controller.subprocess.TimeoutExpired('code', 5), 0]
            controller.process = process
            editor = dict(controller.editor)
            controller._wait_for_editor_gone = Mock(side_effect=[
                (False, [{'editor_size': [901, 1176], 'dialog_windows': [
                    {'address': '0xdialog', 'class': 'code', 'title': 'Save Workspace'}]}],
                 [editor]),
                (True, [{'editor_size': None, 'dialog_windows': []}], []),
            ])
            controller._dispatch_hyprland = Mock(return_value='ok')

            failure = controller._cleanup_editor()

            self.assertIsNone(failure)
            controller._dispatch_hyprland.assert_called_once_with(
                'hl.dsp.window.close({ window = "address:0xeditor" })')
            process.terminate.assert_called_once_with()
            process.kill.assert_called_once_with()
            self.assertEqual(process.wait.call_args_list, [
                unittest.mock.call(timeout=5), unittest.mock.call(timeout=5)])
            self.assertEqual(controller._wait_for_editor_gone.call_args_list, [
                unittest.mock.call(5), unittest.mock.call(5)])
            controller.emit.assert_any_call('editor-process-sigterm', pid=4321)
            controller.emit.assert_any_call('editor-process-sigkill', pid=4321)
            controller.emit.assert_any_call(
                'editor-close-wait-expired', address='0xeditor',
                observations=[{'editor_size': [901, 1176], 'dialog_windows': [
                    {'address': '0xdialog', 'class': 'code', 'title': 'Save Workspace'}]}],
                save_dialog_seen=True)

    def test_teardown_keeps_failure_when_editor_survives_process_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            process = Mock()
            process.pid = 4321
            process.poll.return_value = 0
            controller.process = process
            editor = dict(controller.editor)
            controller._wait_for_editor_gone = Mock(return_value=(False, [], [editor]))
            controller._dispatch_hyprland = Mock(return_value='ok')

            failure = controller._cleanup_editor()

            self.assertIsInstance(failure, tc02_controller.Escalate)
            self.assertIn('window remains', failure.reason)
            process.terminate.assert_not_called()
            process.kill.assert_not_called()

    def test_success_summary_timing_excludes_post_run_editor_teardown(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.dispatch_mono = 90.0
            controller.execution_start = 100.0
            controller.run_completed_mono = 123.0

            controller._summary('PASS')

            summary = tc02_controller.load_json(controller.summary_path)
            self.assertEqual(summary['execution_s'], 23.0)
            self.assertEqual(summary['end_to_end_s'], 33.0)


if __name__ == '__main__':
    unittest.main()

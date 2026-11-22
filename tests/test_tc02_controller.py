import copy
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path
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


class Tc02ObservePayloadTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-observe-payload-unit-test', temporary)
        controller.emit = Mock()
        return controller

    def test_flat_observation_metadata_is_accepted_without_ok_wrapper(self):
        observation = {
            'id': 'observe-unit-test',
            'image': '/tmp/observe-unit-test.png',
            'observation': '/tmp/observe-unit-test.json',
            'observation_schema': 2,
            'image_role': 'clean-observation',
            'image_bytes': 1,
            'image_sha256': 'a' * 64,
        }
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.broker_driver = Mock(return_value=(observation, {}))

            result = controller._observe('G0-observe', '0xeditor', 1600)

        self.assertIs(result, observation)
        self.assertEqual(controller.last_observation, observation)

    def test_explicit_observe_error_still_escalates(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.broker_driver = Mock(return_value=({'ok': False, 'error': 'capture failed'}, {}))

            with self.assertRaises(tc02_controller.Escalate) as raised:
                controller._observe('G0-observe', '0xeditor', 1600)

        self.assertIn('observe failed', raised.exception.reason)


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

    def test_launch_writes_native_titlebar_to_owned_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            window = {
                'address': '0xnew-editor', 'class': 'com.microsoft.VSCode',
                'title': 'blank.txt - Visual Studio Code', 'at': [0, 0],
                'size': [901, 1176], 'workspace': '1',
            }
            with patch.object(tc02_controller.shutil, 'which', return_value='/usr/bin/code'), \
                    patch.object(tc02_controller.subprocess, 'Popen') as popen, \
                    patch.object(controller, 'current_clients', side_effect=[[], [window]]), \
                    patch.object(controller, '_set_editor_geometry'):
                popen.return_value.pid = 1234

                controller._launch_test_window()

            settings = tc02_controller.load_json(
                controller.run_dir / 'vscode-profile' / 'User' / 'settings.json')
            self.assertEqual(settings['window.menuBarVisibility'], 'classic')
            self.assertEqual(settings['window.titleBarStyle'], 'native')

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
            controller.current_clients = Mock(return_value=[])

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

    def test_teardown_closes_orphan_portal_dialog_and_verifies_desktop(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.process = Mock()
            controller.process.poll.return_value = 0
            dialog = {'address': '0xdialog', 'class': 'xdg-desktop-portal-gtk',
                      'title': 'Save As', 'at': [0, 0], 'size': [875, 600],
                      'workspace': '2'}
            controller._wait_for_editor_gone = Mock(return_value=(True, [], []))
            controller._dispatch_hyprland = Mock(return_value='ok')
            controller.current_clients = Mock(side_effect=[[dialog], []])

            failure = controller._cleanup_editor()

            self.assertIsNone(failure)
            self.assertEqual(controller._dispatch_hyprland.call_args_list, [
                unittest.mock.call(
                    'hl.dsp.window.close({ window = "address:0xeditor" })'),
                unittest.mock.call(
                    'hl.dsp.window.close({ window = "address:0xdialog" })'),
            ])
            controller.emit.assert_any_call(
                'orphan-dialog-closed', address='0xdialog',
                cls='xdg-desktop-portal-gtk', title='Save As')
            controller.emit.assert_any_call('teardown-verified', clients=[])

    def test_teardown_sigterms_launched_pid_for_vscode_save_dialog(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            process = Mock()
            process.pid = 4321
            process.poll.return_value = None
            controller.process = process
            dialog = {'address': '0xdialog', 'class': 'code',
                      'title': 'Visual Studio Code', 'at': [0, 0],
                      'size': [500, 200], 'workspace': '2'}
            controller._wait_for_editor_gone = Mock(return_value=(True, [], []))
            controller._dispatch_hyprland = Mock(return_value='ok')
            controller.current_clients = Mock(side_effect=[[dialog], [], []])

            failure = controller._cleanup_editor()

            self.assertIsNone(failure)
            process.terminate.assert_called_once_with()
            controller._dispatch_hyprland.assert_called_once_with(
                'hl.dsp.window.close({ window = "address:0xeditor" })')
            controller.emit.assert_any_call('teardown-verified', clients=[])

    def test_teardown_fails_when_orphan_dialog_survives(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.process = Mock()
            controller.process.poll.return_value = 0
            dialog = {'address': '0xdialog', 'class': 'xdg-desktop-portal-gtk',
                      'title': 'Save As', 'at': [0, 0], 'size': [875, 600],
                      'workspace': '2'}
            controller._wait_for_editor_gone = Mock(return_value=(True, [], []))
            controller._dispatch_hyprland = Mock(return_value='ok')
            controller.current_clients = Mock(side_effect=[[dialog], [dialog]])

            failure = controller._cleanup_editor()

            self.assertIsInstance(failure, tc02_controller.Escalate)
            self.assertIn('teardown-dialog-verification', failure.checkpoint)


    def test_dirty_editor_title_is_still_the_same_editor(self):
        # tc02-gate3-A1: S1 typing dirties the document, the editor title
        # gains the "● " marker, and the stale stored record then fails
        # the unexpected-window check. Refreshing from the live list
        # must keep the same editor expected.
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller.editor = {
                'address': '0xeditor', 'class': 'com.microsoft.VSCode',
                'title': 'blank.txt - Visual Studio Code',
                'at': [2990, 914], 'size': [901, 1176], 'workspace': '2'}
            dialog = {'address': '0xdialog', 'class': 'xdg-desktop-portal-gtk',
                      'title': 'Save As', 'at': [3003, 1202],
                      'size': [875, 600], 'workspace': '2'}
            windows = [dict(controller.editor,
                            title='● blank.txt - Visual Studio Code'), dialog]
            with self.assertRaises(tc02_controller.Escalate):
                controller._assert_no_unexpected_windows(
                    windows, [controller.editor,
                              tc02_controller.window_line(dialog)])
            controller.editor = controller._assert_window(
                windows, '0xeditor', cls='com.microsoft.VSCode')
            controller._assert_no_unexpected_windows(
                windows, [controller.editor,
                          tc02_controller.window_line(dialog)])


class Tc02MenuBarTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-menu-bar-unit-test', temporary)
        controller.emit = Mock()
        return controller

    def test_typed_text_check_passes_when_fragment_is_visible(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            observation = {'image': str(Path(temporary) / 'after.png')}
            Path(observation['image']).write_bytes(b'fake')
            step = {'checkpoint': 's1-check',
                    'batch': [{'type': 'click', 'point': 'editor_body'},
                              {'type': 'type', 'text': 'note at 20:30.\n'}]}
            completed = tc02_controller.subprocess.CompletedProcess(
                ['tesseract', observation['image'], 'stdout', '--psm', '6'],
                0, 'note at 20:30.\n', '')
            with patch.object(tc02_controller.subprocess, 'run',
                              return_value=completed), \
                    patch.object(tc02_controller.shutil, 'which',
                                 return_value='/usr/bin/tesseract'):
                controller._assert_typed_text_visible(observation, step)

    def test_typed_text_check_fails_when_fragment_is_absent(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            observation = {'image': str(Path(temporary) / 'after.png')}
            Path(observation['image']).write_bytes(b'fake')
            step = {'checkpoint': 's1-check',
                    'batch': [{'type': 'click', 'point': 'editor_body'},
                              {'type': 'type', 'text': 'note at 20:30.\n'}]}
            completed = tc02_controller.subprocess.CompletedProcess(
                ['tesseract', observation['image'], 'stdout', '--psm', '6'],
                0, 'empty document\n', '')
            with patch.object(tc02_controller.subprocess, 'run',
                              return_value=completed), \
                    patch.object(tc02_controller.shutil, 'which',
                                 return_value='/usr/bin/tesseract'):
                with self.assertRaises(tc02_controller.Escalate) as caught:
                    controller._assert_typed_text_visible(observation, step)
            self.assertIn('20:30', caught.exception.reason)

    def test_typed_text_check_skips_plans_without_a_time_fragment(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            step = {'checkpoint': 's1-check',
                    'batch': [{'type': 'type', 'text': 'no time here'}]}
            with patch.object(tc02_controller.subprocess, 'run') as run:
                controller._assert_typed_text_visible({'image': 'missing.png'}, step)
            run.assert_not_called()

    @unittest.skipUnless(shutil.which('tesseract'), 'tesseract is required by the menu-bar check')
    def test_menu_bar_ocr_requires_file_and_edit_on_fixture_images(self):
        fixtures = Path(__file__).resolve().parent / 'fixtures'
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            controller._menu_bar_visible({
                'image': str(fixtures / 'tc02-menu-bar-file-edit.png')})
            passed = controller.emit.call_args.kwargs
            self.assertEqual(passed['missing'], [])
            self.assertEqual(passed['tokens'], ['File', 'Edit'])

            controller.emit.reset_mock()
            with self.assertRaises(tc02_controller.Escalate) as raised:
                controller._menu_bar_visible({
                    'image': str(fixtures / 'tc02-menu-bar-no-file-edit.png')})
            failed = controller.emit.call_args.kwargs
            self.assertEqual(failed['missing'], ['File', 'Edit'])
            self.assertIn("missing labels: ['File', 'Edit']", raised.exception.reason)

    def test_native_menu_coordinates_match_v_native_ocr_probe(self):
        """Source: /tmp/opt-menubar-probe/V-native/file-menu-settled.tsv.

        File [7,9,24,11] centers at [19,14]. Save [21,485,36,12] plus
        As [62,485,33,12] gives the Save As row center [58,491].
        """
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        self.assertEqual(plan['coordinates']['file_menu']['offset'], [19, 14])
        self.assertEqual(plan['coordinates']['save_as_row']['offset'], [58, 491])

    def test_t3_rebases_only_the_two_reobserved_menu_clicks(self):
        trace_actions = [
            {'type': 'click', 'x': 888, 'y': 45},
            {'type': 'click', 'x': 200, 'y': 100},
            {'type': 'type', 'text': 'Tối nay ôn cấu trúc dữ liệu lúc 20:30.\n'},
            {'type': 'click', 'x': 57, 'y': 14},
            {'type': 'click', 'x': 95, 'y': 365},
            {'type': 'click', 'x': 430, 'y': 22},
        ]

        rebased, evidence = tc02_controller.rebase_t3_menu_coordinates(trace_actions)

        self.assertEqual(rebased[3:5], [
            {'type': 'click', 'x': 19, 'y': 14},
            {'type': 'click', 'x': 58, 'y': 491},
        ])
        self.assertEqual(rebased[:3], trace_actions[:3])
        self.assertEqual(rebased[5], trace_actions[5])
        self.assertEqual(evidence, [
            {'action_index': 3, 'from': [57, 14], 'to': [19, 14]},
            {'action_index': 4, 'from': [95, 365], 'to': [58, 491]},
        ])


class Tc02LayoutTests(unittest.TestCase):
    def load_plan(self):
        return tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)

    def load_schema(self):
        return tc02_controller.load_json(tc02_controller.DEFAULT_SCHEMA)

    def test_layout_table_covers_dialog_points_and_steps_use_it(self):
        plan = self.load_plan()
        tc02_controller.validate_plan(plan, self.load_schema())
        layout = plan['layout']
        self.assertEqual(layout['menu_bar_ocr_crop']['rect'], [0, 0, 500, 40])
        self.assertEqual(layout['typed_line_ocr_crop']['rect'], [0, 110, 901, 60])
        self.assertEqual(layout['dialog_top_crop']['rect'], [0, 0, 875, 60])
        self.assertEqual(layout['editor_top_crop']['rect'], [0, 0, 901, 60])
        self.assertEqual(plan['steps'][5]['crop'], [0, 0, 875, 60])
        self.assertEqual(plan['steps'][8]['crop'], [0, 0, 901, 60])

    def test_layout_rect_outside_window_fails_validation(self):
        plan = self.load_plan()
        plan['layout']['menu_bar_ocr_crop']['rect'] = [0, 0, 901, 2000]
        with self.assertRaises(ValueError):
            tc02_controller.validate_plan(plan, self.load_schema())

    def test_dialog_crop_must_cover_save_button(self):
        plan = self.load_plan()
        plan['layout']['dialog_top_crop']['rect'] = [0, 0, 400, 60]
        with self.assertRaises(ValueError):
            tc02_controller.validate_plan(plan, self.load_schema())

    def test_s3_crop_must_equal_layout_dialog_crop(self):
        plan = self.load_plan()
        plan['steps'][5]['crop'] = [0, 0, 875, 120]
        with self.assertRaises(ValueError):
            tc02_controller.validate_plan(plan, self.load_schema())


class Tc02CropCoordinateTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-crop-unit-test', temporary)
        controller.emit = Mock()
        controller.step = 'G0'
        return controller

    @staticmethod
    def full_frame_observation():
        return {'image_size': [901, 1176], 'window_bounds': [2990, 914, 901, 1176],
                'region': [2990, 914, 901, 1176]}

    @staticmethod
    def dialog_crop_observation():
        return {'image_size': [875, 60], 'window_bounds': [3003, 1202, 875, 600],
                'region': [3003, 1202, 875, 60]}

    def test_full_frame_mapping_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            resolved = controller._resolve_action(
                {'type': 'click', 'point': 'file_menu'}, self.full_frame_observation())
            self.assertEqual((resolved['x'], resolved['y']), (19, 14))

    def test_dialog_crop_mapping_uses_region_origin(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            observation = self.dialog_crop_observation()
            name = controller._resolve_action(
                {'type': 'click', 'point': 'name_field'}, observation)
            save = controller._resolve_action(
                {'type': 'click', 'point': 'save_button'}, observation)
            self.assertEqual((name['x'], name['y']), (430, 22))
            self.assertEqual((save['x'], save['y']), (825, 22))

    def test_point_outside_crop_escalates(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            with self.assertRaises(tc02_controller.Escalate):
                controller._resolve_action(
                    {'type': 'click', 'point': 'editor_body'},
                    self.dialog_crop_observation())


class Tc02OcrCropTests(unittest.TestCase):
    def make_controller(self, temporary):
        plan = tc02_controller.load_json(tc02_controller.DEFAULT_PLAN)
        controller = tc02_controller.Tc02Controller(
            plan, 'tc02-ocr-crop-unit-test', temporary)
        controller.emit = Mock()
        return controller

    @staticmethod
    def write_image(temporary, name='frame.png', size=(901, 1176)):
        from PIL import Image
        path = Path(temporary) / name
        Image.new('RGB', size, 'white').save(path)
        return str(path)

    def test_crop_hit_returns_crop_text_without_full_frame_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            image = self.write_image(temporary)
            completed = tc02_controller.subprocess.CompletedProcess(
                ['tesseract', image, 'stdout', '--psm', '6'], 0, 'File Edit\n', '')
            with (patch.object(tc02_controller.shutil, 'which',
                               return_value='/usr/bin/tesseract'),
                  patch.object(tc02_controller.subprocess, 'run',
                               return_value=completed) as run):
                text, used_crop = controller._ocr_text(
                    image, step='G0', checkpoint='menu-bar-presence', label='menu-bar',
                    crop=[0, 0, 500, 40],
                    found=lambda value: 'File' in value and 'Edit' in value)
            self.assertEqual(text, 'File Edit\n')
            self.assertTrue(used_crop)
            run.assert_called_once()

    def test_crop_miss_falls_back_to_full_frame(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = self.make_controller(temporary)
            image = self.write_image(temporary)
            calls = []

            def fake_run(args, **kwargs):
                calls.append(args[1])
                if 'crop' in args[1]:
                    return tc02_controller.subprocess.CompletedProcess(
                        args, 0, 'blank\n', '')
                return tc02_controller.subprocess.CompletedProcess(
                    args, 0, 'File Edit\n', '')

            with (patch.object(tc02_controller.shutil, 'which',
                               return_value='/usr/bin/tesseract'),
                  patch.object(tc02_controller.subprocess, 'run', side_effect=fake_run)):
                text, used_crop = controller._ocr_text(
                    image, step='G0', checkpoint='menu-bar-presence', label='menu-bar',
                    crop=[0, 0, 500, 40],
                    found=lambda value: 'File' in value)
            self.assertEqual(text, 'File Edit\n')
            self.assertFalse(used_crop)
            self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()

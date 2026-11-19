"""E4: honest frame/focus diagnostics on desktop act results.

input_diagnostics reports the pre-batch focus state and says plainly that the
pointer check verifies cursor position only. frame_bytes_changed is the exact
pixel-hash comparison; `changed` stays as a compatibility alias. Diagnostics
never mask the action error and never imply the application applied the action.
Every seam below desktop_act is mocked; no compositor, capture or input runs.
"""
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import time
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import cu  # noqa: E402

ADDR = '0x1234'
POINTER_CHECK = 'cursor position only; desktop backend cannot identify the receiving UI element'


def base_meta(**over):
    meta = {'backend': 'desktop','observation_schema':cu.OBSERVATION_SCHEMA,
            'image_role':'clean-observation','scope': 'window',
            'window': ADDR, 'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
            'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
            'monitor_transform': 0, 'image_size': [20, 20],
            'region': [0, 0, 20, 20], 'image': 'synthetic.png',
            'max_width': 1280, 'pixel_sha256': 'old-hash',
            **cu._capture_identity({}),'created':time.time()}
    meta.update(over)
    return meta


class ActDiagnostics(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.capture_addresses = []
        self.fresh_reads = []

    def desktop_act(self, meta, actions, after_capture=True, *,
                    active=None, cursor=(10, 10), after=None,
                    pre_fresh=None, new_image=None, image_pair=None,
                    fresh_images=None, file_image=None,
                    probe_error=None, expected_terminal_window=None,
                    window_side_effect=None):
        """Run the real desktop_act with every GUI seam mocked.

        active: answers for successive activewindow queries (the pre-batch
        diagnostics query and every guard pop one; the default simulates the
        target staying focused for the whole batch);
        probe_error: when set, the FIRST activewindow query (the optional
        focus_before diagnostic probe) raises RuntimeError with this text;
        the queue is not consumed by the failed probe;
        cursor: the compositor cursor position the pointer check reads;
        after: metadata returned by the successful after-capture;
        pre_fresh: fresh metadata returned by the pre-input capture;
        new_image: a different image for the screen-changed comparison;
        image_pair: the image PIL.Image.open returns (the saved observation).
        """
        from PIL import Image
        if pre_fresh is None:
            pre_fresh = dict(meta)
        fresh_images = list(fresh_images or [])
        image = Image.new('RGB', (20, 20))
        stack = ExitStack()
        stack.enter_context(patch.object(cu, 'STATE', self.tmp))
        stack.enter_context(patch.object(cu, 'check_cancel'))
        stack.enter_context(patch.object(cu, 'focus'))
        stack.enter_context(patch.object(cu, 'window',
                                         side_effect=window_side_effect,
                                         **({} if window_side_effect else
                                            {'return_value': {'at': meta['window_bounds'][:2],
                                                              'size': meta['window_bounds'][2:]}})))
        queue = list(active) if active is not None else [ADDR] * 8
        probe_failures = [probe_error] if probe_error is not None else []

        def hypr(env, query):
            if query == 'monitors':
                x, y, width, height = meta['monitor_box']
                return [{'name': 'test', 'x': x, 'y': y, 'width': width,
                         'height': height, 'scale': meta['monitor_scale'],
                         'transform': meta['monitor_transform']}]
            if query == 'activewindow':
                if probe_failures:
                    failure = probe_failures.pop(0)
                    if isinstance(failure, BaseException):
                        raise failure
                    raise RuntimeError(failure)
                return {'address': queue.pop(0)}
            if query == 'cursorpos':
                return {'x': cursor[0], 'y': cursor[1]}
            raise AssertionError('unexpected query ' + query)

        stack.enter_context(patch.object(cu, 'hypr', side_effect=hypr))

        def obs(*args, **kwargs):
            if kwargs.get('persist', True):
                self.capture_addresses.append(args[1])
                if isinstance(after, Exception):
                    raise after
                return dict(after)
            self.fresh_reads.append(True)
            fresh_image = (fresh_images.pop(0) if fresh_images else
                           new_image if new_image is not None else image)
            return fresh_image, dict(pre_fresh)

        stack.enter_context(patch.object(cu, 'observe', side_effect=obs))
        stack.enter_context(patch.object(cu, 'observe_screen', side_effect=obs))
        stack.enter_context(patch.object(cu, 'Pointer', return_value=Mock()))
        stack.enter_context(patch.object(cu, 'run_cancelable', return_value=''))
        stack.enter_context(patch.object(cu.shutil, 'which', return_value=None))
        def fake_image_open(fp, *args, **kwargs):
            # BytesIO opens are observation-file reads inside validation
            # (the persisted fresh frame); path opens are the displayed
            # observation image. A2 absorb tests pass file_image for the
            # former so the retry meta validates against real pixels.
            if file_image is not None and isinstance(fp, io.BytesIO):
                return file_image
            return image_pair[0] if image_pair else image
        stack.enter_context(patch('PIL.Image.open', side_effect=fake_image_open))
        self.sleep_mock = stack.enter_context(patch('time.sleep'))
        try:
            return cu.desktop_act({}, meta, actions, after_capture=after_capture,
                                  expected_terminal_window=expected_terminal_window)
        finally:
            stack.close()

    def test_successful_after_capture_reports_diagnostics_and_frame_alias(self):
        meta = base_meta()
        fresh = dict(meta, pixel_sha256='new-hash')
        after = dict(meta, pixel_sha256='after-hash', image='after.png')
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  pre_fresh=fresh, after=after)
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 1)
        diagnostics = result['input_diagnostics']
        self.assertEqual(diagnostics['focus_before'], ADDR)
        self.assertEqual(diagnostics['target_window'], ADDR)
        self.assertIs(diagnostics['target_was_focused'], True)
        self.assertEqual(diagnostics['pointer_check'], POINTER_CHECK)
        # Both keys present; the alias must not silently replace the honest name.
        self.assertIn('frame_bytes_changed', result)
        self.assertIn('changed', result)
        self.assertIs(result['frame_bytes_changed'], True)
        self.assertEqual(result['changed'], result['frame_bytes_changed'])
        self.assertIn('Does not confirm app action succeeded', result['change_meaning'])
        self.assertEqual(result['after'], after)

    def test_unchanged_frame_reports_false_in_both_keys(self):
        meta = base_meta()
        same = dict(meta, pixel_sha256='old-hash')
        after = dict(meta, pixel_sha256='old-hash', image='after.png')
        result = self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                                  pre_fresh=same, after=after)
        self.assertTrue(result['ok'])
        self.assertIs(result['frame_bytes_changed'], False)
        self.assertIs(result['changed'], False)

    def test_no_after_success_includes_diagnostics_without_after(self):
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                                  after_capture=False,
                                  pre_fresh=dict(meta))
        self.assertTrue(result['ok'])
        self.assertTrue(result['after_skipped'])
        self.assertEqual(result['input_diagnostics']['target_was_focused'], True)
        for absent in ('after', 'changed', 'frame_bytes_changed', 'change_meaning'):
            self.assertNotIn(absent, result)

    def test_expected_successor_allows_dialog_close_without_after_capture(self):
        successor = '0x5678'
        old_checks = {'count': 0}

        def current_window(_env, address):
            if address == ADDR:
                old_checks['count'] += 1
                if old_checks['count'] > 3:
                    raise ValueError('window no longer exists')
            return {'at': [0, 0], 'size': [20, 20]}

        result = self.desktop_act(
            base_meta(), [{'type': 'wait', 'ms': 0}], after_capture=False,
            expected_terminal_window=successor, window_side_effect=current_window,
            active=[ADDR, ADDR, ADDR, ADDR, successor])

        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertTrue(result['after_skipped'])
        self.assertEqual(result['transition']['expected']['old_surface'], ADDR)
        self.assertTrue(result['transition']['old_surface_gone'])
        self.assertEqual(result['transition']['successor'], successor)
        self.assertTrue(result['transition']['successor_bound'])
        self.assertTrue(result['transition']['successor_verified'])
        self.assertEqual(self.capture_addresses, [])

    def test_terminal_focus_settles_after_dialog_close(self):
        # The Save click closes the dialog asynchronously: the first
        # terminal-guard sample still sees the dialog focused, the next
        # sees the editor. The act must verify the transition, not refuse.
        successor = '0x5678'
        result = self.desktop_act(
            base_meta(), [{'type': 'wait', 'ms': 0}], after_capture=False,
            expected_terminal_window=successor,
            active=[ADDR, ADDR, ADDR, ADDR, ADDR, successor])

        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertTrue(result['transition']['successor_verified'])

    def test_expected_successor_is_used_for_final_after_capture(self):
        successor = '0x5678'
        self.desktop_act(base_meta(), [{'type': 'wait', 'ms': 0}],
                         after_capture=True,
                         expected_terminal_window=successor,
                         active=[ADDR, ADDR, ADDR, ADDR, successor],
                         after=base_meta(window=successor))
        self.assertEqual(self.capture_addresses, [successor])

    def test_capture_error_reports_diagnostics_and_stays_failed(self):
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                                  after=RuntimeError('grim failed'),
                                  pre_fresh=dict(meta))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['capture_error'], 'grim failed')
        self.assertEqual(result['error'], 'final capture failed: grim failed')
        # The diagnostics are present but never repair the failure or the count.
        self.assertEqual(result['input_diagnostics']['target_window'], ADDR)
        for absent in ('changed', 'frame_bytes_changed', 'change_meaning'):
            self.assertNotIn(absent, result)

    def test_action_error_reports_diagnostics_without_masking_it(self):
        meta = base_meta()
        # The pointer verification reads the cursor far off target: the move
        # is refused, and the diagnostics must not soften that error.
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  cursor=(500, 500),
                                  pre_fresh=dict(meta),
                                  after=dict(meta, image='after.png'))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['completed'], 0)
        self.assertIn('pointer missed target', result['error'])
        self.assertEqual(result['input_diagnostics']['pointer_check'], POINTER_CHECK)

    def test_screen_changed_refusal_has_no_input_diagnostics(self):
        from PIL import Image, ImageDraw
        old = Image.new('RGB', (20, 20), 'white')
        new = old.copy()
        ImageDraw.Draw(new).rectangle((0, 0, 20, 20), fill='black')
        meta = base_meta()
        fresh = dict(meta, pixel_sha256='new-hash')
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  pre_fresh=fresh, new_image=new,
                                  image_pair=(old,), active=(ADDR, ADDR))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['error_code'], 'screen_changed')
        self.assertNotIn('preflight_retries', result,
                         'whole-image change at the action point is not absorbed')
        self.assertIn('after', result)
        self.assertNotIn('input_diagnostics', result,
                         'the pre-input refusal envelope stays unchanged')

    def test_stable_uniform_brightness_shift_retries_once_and_proceeds(self):
        from PIL import Image, ImageChops, ImageStat
        old = Image.new('RGB', (100, 100), (100, 100, 100))
        shifted = Image.new('RGB', old.size)
        shifted.putdata([(96 if x % 2 == 0 else 97,) * 3
                         for y in range(old.height) for x in range(old.width)])
        self.assertAlmostEqual(sum(ImageStat.Stat(ImageChops.difference(old, shifted)).mean) / 3,
                               3.5, places=1)
        meta = base_meta(image_size=[100, 100], window_bounds=[0, 0, 100, 100],
                         monitor_box=[0, 0, 100, 100], region=[0, 0, 100, 100])
        with patch.dict(os.environ, {'CU_SESSION_TOKEN': 'c' * 32}):
            result = self.desktop_act(meta, [{'type': 'move', 'x': 50, 'y': 50}],
                                      image_pair=(old,), fresh_images=[shifted, shifted.copy()],
                                      after=base_meta(image='after.png'), cursor=(50, 50))
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertEqual(len(self.fresh_reads), 2)
        self.assertEqual(sum(args == (.15,) for args, _ in self.sleep_mock.call_args_list), 1)
        rows = [json.loads(line) for path in self.tmp.glob('diagnostics-*.jsonl')
                for line in path.read_text().splitlines()]
        self.assertIn('preflight_retry', [row['event'] for row in rows])

    def test_moved_action_point_still_refuses_after_stable_retry(self):
        from PIL import Image, ImageDraw
        old = Image.new('RGB', (100, 100), (100, 100, 100))
        ImageDraw.Draw(old).rectangle((35, 35, 55, 55), fill=(240, 240, 240))
        moved = Image.new('RGB', (100, 100), (100, 100, 100))
        ImageDraw.Draw(moved).rectangle((50, 35, 70, 55), fill=(240, 240, 240))
        meta = base_meta(image_size=[100, 100], window_bounds=[0, 0, 100, 100],
                         monitor_box=[0, 0, 100, 100], region=[0, 0, 100, 100])
        result = self.desktop_act(meta, [{'type': 'move', 'x': 45, 'y': 45}],
                                  image_pair=(old,), fresh_images=[moved, moved.copy()],
                                  active=[ADDR] * 8)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'screen_changed')
        self.assertNotIn('preflight_retries', result,
                         'a moved action point is not absorbed')
        self.assertEqual(len(self.fresh_reads), 2)
        self.sleep_mock.assert_called_once_with(.15)

    def test_unstable_fresh_frames_refuse_after_only_one_retry(self):
        from PIL import Image
        old = Image.new('RGB', (100, 100), (100, 100, 100))
        first = Image.new('RGB', old.size)
        second = Image.new('RGB', old.size)
        first.putdata([(96 if x % 2 == 0 else 97,) * 3
                       for y in range(old.height) for x in range(old.width)])
        second.putdata([(92 if x % 2 == 0 else 93,) * 3
                        for y in range(old.height) for x in range(old.width)])
        meta = base_meta(image_size=[100, 100], window_bounds=[0, 0, 100, 100],
                         monitor_box=[0, 0, 100, 100], region=[0, 0, 100, 100])
        result = self.desktop_act(meta, [{'type': 'move', 'x': 50, 'y': 50}],
                                  image_pair=(old,), fresh_images=[first, second],
                                  active=[ADDR] * 8)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'screen_changed')
        self.assertNotIn('preflight_retries', result,
                         'a still-drifting action point is not absorbed')
        self.assertEqual(len(self.fresh_reads), 2,
                         'one second capture maximum, no recursive retries')
        self.sleep_mock.assert_called_once_with(.15)

    def test_absorbed_brightness_drift_succeeds_with_flag(self):
        # A2: a screen-changed refusal whose action-point patches are
        # unchanged vs the original observation is absorbed inside act():
        # one retry against the settled frame, no model round trip.
        from PIL import Image, ImageDraw
        old = Image.new('RGB', (100, 100), (100, 100, 100))
        shifted = Image.new('RGB', old.size)
        shifted.putdata([(96 if x % 2 == 0 else 97,) * 3
                         for y in range(old.height) for x in range(old.width)])
        settled = Image.new('RGB', old.size)
        settled.putdata([(90 if x % 2 == 0 else 91,) * 3
                         for y in range(old.height) for x in range(old.width)])
        ImageDraw.Draw(settled).rectangle((26, 26, 74, 74), fill=(96, 96, 96))
        settled.format = 'PNG'
        meta = base_meta(image_size=[100, 100], window_bounds=[0, 0, 100, 100],
                         monitor_box=[0, 0, 100, 100], region=[0, 0, 100, 100])
        with patch.dict(os.environ, {'CU_SESSION_TOKEN': 'c' * 32}):
            result = self.desktop_act(meta, [{'type': 'move', 'x': 50, 'y': 50}],
                                      image_pair=(old,), file_image=settled,
                                      fresh_images=[shifted, settled, settled.copy()],
                                      after=dict(meta, pixel_sha256='after-hash',
                                                 image='after.png'),
                                      cursor=(50, 50), active=[ADDR] * 16)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertTrue(result['preflight_absorbed'])
        self.assertEqual(result['preflight_retries'], 1)
        self.assertEqual(len(self.fresh_reads), 3)
        self.assertEqual(sum(args == (.15,) for args, _ in self.sleep_mock.call_args_list), 1)
        rows = [json.loads(line) for path in self.tmp.glob('diagnostics-*.jsonl')
                for line in path.read_text().splitlines()]
        self.assertIn('preflight_absorb_retry', [row['event'] for row in rows])

    def test_absorb_retry_still_refuses_after_second_drift(self):
        # A2: absorption is max ONE retry. If the retried act still sees a
        # drifting screen, the refusal is returned, marked preflight_retries.
        from PIL import Image, ImageDraw
        old = Image.new('RGB', (100, 100), (100, 100, 100))
        shifted = Image.new('RGB', old.size)
        shifted.putdata([(96 if x % 2 == 0 else 97,) * 3
                         for y in range(old.height) for x in range(old.width)])
        settled = Image.new('RGB', old.size)
        settled.putdata([(90 if x % 2 == 0 else 91,) * 3
                         for y in range(old.height) for x in range(old.width)])
        ImageDraw.Draw(settled).rectangle((26, 26, 74, 74), fill=(96, 96, 96))
        settled.format = 'PNG'
        drift_a = Image.new('RGB', old.size)
        drift_a.putdata([(84 if x % 2 == 0 else 85,) * 3
                         for y in range(old.height) for x in range(old.width)])
        drift_b = Image.new('RGB', old.size)
        drift_b.putdata([(78 if x % 2 == 0 else 79,) * 3
                         for y in range(old.height) for x in range(old.width)])
        meta = base_meta(image_size=[100, 100], window_bounds=[0, 0, 100, 100],
                         monitor_box=[0, 0, 100, 100], region=[0, 0, 100, 100])
        with patch.dict(os.environ, {'CU_SESSION_TOKEN': 'c' * 32}):
            result = self.desktop_act(meta, [{'type': 'move', 'x': 50, 'y': 50}],
                                      image_pair=(old,), file_image=settled,
                                      fresh_images=[shifted, settled, drift_a, drift_b],
                                      cursor=(50, 50), active=[ADDR] * 16)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'screen_changed')
        self.assertEqual(result['preflight_retries'], 1)
        self.assertNotIn('preflight_absorbed', result)
        self.assertIn('after', result)
        self.assertEqual(len(self.fresh_reads), 4)
        self.assertEqual(sum(args == (.15,) for args, _ in self.sleep_mock.call_args_list), 2)

    def test_focus_changed_refusal_envelope_has_no_input_diagnostics(self):
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                                  active=('0xdead', '0xdead'),
                                  pre_fresh=dict(meta))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['error_code'], 'focus_changed')
        self.assertNotIn('input_diagnostics', result,
                         'diagnostics attach only to results that reached input')

    def test_preflight_refusal_raises_before_any_diagnostics_query(self):
        meta = base_meta()
        meta['capture_started_monotonic']-=91
        meta['capture_started_wall']-=91
        meta['created']-=91
        with ExitStack() as stack:
            stack.enter_context(patch.object(cu, 'STATE', self.tmp))
            stack.enter_context(patch.object(cu, 'check_cancel'))
            stack.enter_context(patch.object(cu, 'focus'))
            stack.enter_context(patch.object(cu, 'Pointer'))
            hypr = stack.enter_context(patch.object(cu, 'hypr'))
            with self.assertRaisesRegex(cu.PreflightRefusal, 'observation older than 90s'):
                cu.desktop_act({}, meta, [{'type': 'wait', 'ms': 0}])
            hypr.assert_not_called()

    def test_browser_act_result_has_no_input_diagnostics(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            stack.enter_context(patch.object(cu, 'STATE', pathlib.Path(folder)))
            stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': 'f' * 32}))
            stack.enter_context(patch.object(cu, 'check_cancel'))
            stack.enter_context(patch.object(cu.sys, 'argv',
                                             ['cu', 'browser', 'act', '--actions', '-']))
            stack.enter_context(patch.object(cu.sys, 'stdout', out))
            stack.enter_context(patch.object(cu.sys, 'stdin',
                                             io.StringIO('[{"type":"wait","ms":10}]')))
            stack.enter_context(patch.object(cu, 'browser',
                                             return_value={'ok': True, 'tabs': []}))
            self.assertEqual(cu.main(), 0)
        result = json.loads(out.getvalue())
        self.assertTrue(result['ok'])
        self.assertNotIn('input_diagnostics', result)


class OptionalFocusProbeIsolation(unittest.TestCase):
    """R06: the focus_before diagnostic probe is OPTIONAL. A probe failure
    must degrade to focus_before:null plus a bounded warning and never abort
    a valid action, weaken the required guards, mask a later action error or
    swallow BaseException/cancellation."""

    def setUp(self):
        ActDiagnostics.setUp(self)
        # Reuse the fully mocked harness on the dedicated class.
        self.desktop_act = ActDiagnostics.desktop_act.__get__(self, type(self))

    def test_screen_scope_probe_failure_still_succeeds(self):
        meta = base_meta(scope='screen')
        del meta['window']  # screen scope has no target window
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  probe_error='compositor query timed out',
                                  pre_fresh=dict(meta),
                                  after=dict(meta, image='after.png'))
        self.assertTrue(result['ok'], 'a failed OPTIONAL probe must not abort a screen action')
        self.assertEqual(result['completed'], 1)
        diagnostics = result['input_diagnostics']
        self.assertIsNone(diagnostics['focus_before'])
        self.assertIsNone(diagnostics['target_window'])
        self.assertIn('compositor query timed out', diagnostics['focus_probe_warning'])
        self.assertLessEqual(len(diagnostics['focus_probe_warning']), 400)

    def test_window_scope_probe_failure_keeps_required_guards(self):
        # The probe fails, then the REQUIRED activewindow guard runs healthy:
        # the action proceeds correctly instead of being aborted.
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  probe_error='compositor query timed out',
                                  pre_fresh=dict(meta),
                                  after=dict(meta, image='after.png'))
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 1)
        diagnostics = result['input_diagnostics']
        self.assertIsNone(diagnostics['focus_before'])
        self.assertIsNone(diagnostics['target_was_focused'],
                          'an unknown focus state must not be reported as False')
        self.assertEqual(diagnostics['target_window'], ADDR)
        self.assertIn('compositor query timed out', diagnostics['focus_probe_warning'])

    def test_required_guard_fatal_stays_fatal_after_probe_failure(self):
        # Probe failure AND a genuinely changed focus: the transient refusal
        # envelope is unchanged (no diagnostics, no warning leakage).
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                                  probe_error='compositor query timed out',
                                  active=['0xdead'],
                                  pre_fresh=dict(meta))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['error_code'], 'focus_changed')
        self.assertNotIn('input_diagnostics', result)
        self.assertNotIn('focus_probe_warning', str(result))

    def test_probe_failure_never_masks_the_action_error(self):
        meta = base_meta()
        result = self.desktop_act(meta, [{'type': 'move', 'x': 10, 'y': 10}],
                                  probe_error='compositor query timed out',
                                  cursor=(500, 500),
                                  pre_fresh=dict(meta),
                                  after=dict(meta, image='after.png'))
        self.assertIs(result['ok'], False)
        self.assertEqual(result['completed'], 0)
        self.assertIn('pointer missed target', result['error'],
                      'the primary action error must survive the probe failure')
        diagnostics = result['input_diagnostics']
        self.assertIsNone(diagnostics['focus_before'])
        self.assertIn('compositor query timed out', diagnostics['focus_probe_warning'])

    def test_base_exception_from_probe_still_propagates(self):
        meta = base_meta()
        with self.assertRaises(KeyboardInterrupt):
            self.desktop_act(meta, [{'type': 'wait', 'ms': 0}],
                             probe_error=KeyboardInterrupt('cancelling'))


if __name__ == '__main__':
    unittest.main()

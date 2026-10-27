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
    meta = {'backend': 'desktop', 'scope': 'window', 'created': time.time(),
            'window': ADDR, 'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
            'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
            'monitor_transform': 0, 'image_size': [20, 20],
            'region': [0, 0, 20, 20], 'image': 'synthetic.png',
            'max_width': 1280, 'pixel_sha256': 'old-hash'}
    meta.update(over)
    return meta


class ActDiagnostics(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)

    def desktop_act(self, meta, actions, after_capture=True, *,
                    active=None, cursor=(10, 10), after=None,
                    pre_fresh=None, new_image=None, image_pair=None,
                    probe_error=None):
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
        image = Image.new('RGB', (20, 20))
        stack = ExitStack()
        stack.enter_context(patch.object(cu, 'STATE', self.tmp))
        stack.enter_context(patch.object(cu, 'check_cancel'))
        stack.enter_context(patch.object(cu, 'focus'))
        stack.enter_context(patch.object(cu, 'window',
                                         return_value={'at': [0, 0], 'size': [20, 20]}))
        queue = list(active) if active is not None else [ADDR] * 8
        probe_failures = [probe_error] if probe_error is not None else []

        def hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20,
                         'height': 20, 'scale': 1}]
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
                if isinstance(after, Exception):
                    raise after
                return dict(after)
            return (new_image if new_image is not None else image, dict(pre_fresh))

        stack.enter_context(patch.object(cu, 'observe', side_effect=obs))
        stack.enter_context(patch.object(cu, 'observe_screen', side_effect=obs))
        stack.enter_context(patch.object(cu, 'Pointer', return_value=Mock()))
        stack.enter_context(patch.object(cu, 'run_cancelable', return_value=''))
        stack.enter_context(patch.object(cu.shutil, 'which', return_value=None))
        stack.enter_context(patch('PIL.Image.open',
                                  return_value=image_pair[0] if image_pair else image))
        stack.enter_context(patch('time.sleep'))
        try:
            return cu.desktop_act({}, meta, actions, after_capture=after_capture)
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
        self.assertIn('after', result)
        self.assertNotIn('input_diagnostics', result,
                         'the pre-input refusal envelope stays unchanged')

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
        meta = base_meta(created=time.time() - 91)
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

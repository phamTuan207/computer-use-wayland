"""Type verification regressions: ok must mean the text landed visibly.

Verification asymmetry (CL1-MSG batch 3, CL1-MSG2 retry): pointer moves
are verified twice against cursorpos, but a type action used to count
as done on wtype exit alone (completed+=1), so a batch could report
ok while the text never landed (9/9 clean, input still empty). After
a batch containing a type action, desktop_act now compares the
after-capture pixel hash with the pre-action observation and fails the
batch when the frame is unchanged, instead of reporting ok.

Run: python3 tests/test_type_verification.py (stdlib runner at the
bottom). VM only. No laptop, no Zen, no network, no desktop: the fake
compositor harness comes from test_keyboard_preflight.
"""
import unittest

from test_keyboard_preflight import cu, DesktopPreflight


class TypeVerification(DesktopPreflight):
    def test_type_batch_unchanged_frame_fails(self):
        # The CL1-MSG2 retry shape: wtype exits clean, the frame never
        # changes, the input stays empty. That batch must NOT report ok.
        self.after_pixel_sha256 = 'fixture'
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['completed'], 1,
                         'acknowledged input stays counted')
        self.assertIs(result['type_verified'], False)
        self.assertIn('type verification failed', result['error'])
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertIn('next_step', result)

    def test_type_batch_changed_frame_verifies(self):
        # The normal live shape: typed text appears, the frame changes.
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertIs(result['type_verified'], True)

    def test_grouped_type_batch_unchanged_frame_fails(self):
        # A type inside a keyboard group (type + Enter) is verified too.
        self.after_pixel_sha256 = 'fixture'
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'},
                                 {'type': 'key', 'keys': ['Enter']}])
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['completed'], 2)
        self.assertIs(result['type_verified'], False)
        self.assertIn('type verification failed', result['error'])

    def test_key_only_batch_unchanged_frame_still_ok(self):
        # Key-only batches are not verified: a shortcut may
        # legitimately change nothing visible.
        self.after_pixel_sha256 = 'fixture'
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'key', 'keys': ['Enter']}])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 1)
        self.assertNotIn('type_verified', result)

    def test_pointer_only_batch_unchanged_frame_still_ok(self):
        # Pointer batches keep their own cursorpos verification; the
        # type check does not apply to them.
        self.after_pixel_sha256 = 'fixture'
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'move', 'x': 10, 'y': 10}])
        self.assertTrue(result['ok'], result)
        self.assertNotIn('type_verified', result)

    def test_type_batch_after_capture_false_skips_verification(self):
        # No fresh frame was requested, so there is nothing to verify
        # against: the skip is recorded explicitly instead of letting
        # ok rest on process exit alone.
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}],
                                after_capture=False)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['after_skipped'])
        self.assertIsNone(result['type_verified'])
        self.assertIn('skipped', result['type_verification'])

    def test_execution_error_skips_verification(self):
        # An input failure already fails the batch; verification must
        # not mask or replace the real error.
        self.typed.side_effect = RuntimeError('injected input error')
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'])
        self.assertIn('injected input error', result['error'])
        self.assertNotIn('type_verified', result)

    def test_click_type_frame_changed_by_click_only_fails(self):
        # RT R1: the e4082ff check compared the after hash with the
        # PRE-BATCH observation, so any click in the same batch set
        # the bit and a click+type batch with zero text delivered
        # reported type_verified True. Here the after hash differs
        # (the fixture claims the frame changed) but the after IMAGE
        # is pixel identical to the pre-batch image in the input
        # line band: the click changed nothing the pixels can see
        # and no text landed. The band check, not the hash, decides.
        self.after_pixel_sha256 = 'after-frame-changed'
        self.after_image = self.image
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['completed'], 2)
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['type_verified_basis'], 'input-line-band')
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertIn('type verification failed', result['error'])

    def test_click_type_text_in_input_line_verifies(self):
        # The normal click+type shape: the after image carries text
        # pixels on the clicked line, so the band check verifies.
        # The text sits at the left of the line (x 12..17), away
        # from the click point (10,10): the band, not a patch around
        # the click, is what catches it.
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 2)
        self.assertIs(result['type_verified'], True)
        self.assertEqual(result['type_verified_basis'], 'input-line-band')

    def test_focus_check_failure_stops_before_typing(self):
        # G30, cheap focus gate: the click ran, the DOM focus check
        # says the target did not take focus, so the type action is
        # never sent. No new observe is taken for the check.
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'}],
            focus_check=lambda: (False, 'activeElement is body, not the input'))
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['error_code'], 'focus_unverified')
        self.assertIs(result['focus_verified'], False)
        self.assertEqual(result['completed'], 1,
                         'only the click ran; the type never ran')
        self.assertEqual(self.typed.call_count, 0,
                         'no keystroke was sent after the missed click')
        self.assertNotIn('type_verified', result,
                         'typing never ran, so nothing is verified')

    def test_focus_check_passes_then_dom_type_check_verifies(self):
        # The DOM-first shape: focus check passes before typing, the
        # DOM value check passes after typing, the batch verifies
        # with basis dom-value and no pixel check is needed.
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'},
             {'type': 'key', 'keys': ['Enter']}],
            focus_check=lambda: True,
            type_check=lambda: True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 3)
        self.assertIs(result['focus_verified'], True)
        self.assertIs(result['type_verified'], True)
        self.assertEqual(result['type_verified_basis'], 'dom-value')

    def test_dom_type_check_failure_fails_batch_after_typing(self):
        # The DOM value check is the sufficient check: the keystrokes
        # ran, but the field value does not hold the text, so the
        # batch fails with type_unverified instead of reporting ok.
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'}],
            focus_check=lambda: True,
            type_check=lambda: (False, 'field value is empty'))
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertEqual(self.typed.call_count, 1,
                         'the keystrokes ran; the DOM check caught the miss')

    def test_focus_check_exception_fails_closed(self):
        # A focus check that raises (dead DOM session) must fail the
        # batch, never let it type blind on the assumption of focus.
        def _boom():
            raise RuntimeError('DOM session gone')
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'}],
            focus_check=_boom)
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['error_code'], 'focus_unverified')
        self.assertEqual(self.typed.call_count, 0)

    def test_click_type_enter_uses_no_extra_observes(self):
        # Acceptance bar: one observation drives the whole
        # click+type+Enter sequence. The amend adds no observe: the
        # batch uses exactly the pre-fix count, 1 preflight fresh
        # capture plus 1 after-capture plus 1 settle re-capture for
        # the nav candidate click, and the focus/type checks are DOM
        # closures that observe nothing.
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'},
             {'type': 'key', 'keys': ['Enter']}],
            focus_check=lambda: True,
            type_check=lambda: True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(self.observe_calls, ['fresh', 'persist', 'persist'],
                         '1 preflight + 1 after + 1 settle, same as pre-fix')
        self.assertEqual(result['completed'], 3)
        self.assertEqual(result['completed'] / 1, 3,
                         '3 actions driven by 1 observation')

    def test_type_batch_after_capture_false_with_dom_check_verifies(self):
        # With after_capture False there is no frame to compare, but
        # a DOM value check that passed IS the verification.
        result = cu.desktop_act(
            {}, self.meta, [{'type': 'type', 'text': 'hello'}],
            after_capture=False, type_check=lambda: True)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result.get('after_skipped'))
        self.assertIs(result['type_verified'], True)
        self.assertEqual(result['type_verified_basis'], 'dom-value')


if __name__ == '__main__':
    unittest.main(verbosity=2)

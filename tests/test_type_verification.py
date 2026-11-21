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
        # No fresh frame was requested and no DOM check passed, so the
        # typed text is unverified: the batch reports ok False with
        # type_unverified, never ok True on wtype exit alone. The old
        # contract (ok True, skip recorded) baked the hole in; RT R4
        # closes it, and a passing DOM check is the only way this
        # branch reports ok (see the next test).
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}],
                                after_capture=False)
        self.assertFalse(result['ok'], result)
        self.assertTrue(result['after_skipped'])
        self.assertIsNone(result['type_verified'])
        self.assertIn('skipped', result['type_verification'])
        self.assertEqual(result['error_code'], 'type_unverified')

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

    def test_caret_only_after_image_fails(self):
        # AMEND2 A: the click landed and focused the field, the type
        # step is stubbed (the harness never delivers text), and the
        # after image differs only by a 3px caret on the clicked line.
        # The band must not verify on caret pixels alone.
        from PIL import Image
        self.after_image = Image.new('RGB', (20, 20))
        for _x in (10, 11, 12):
            self.after_image.putpixel((_x, 10), (255, 255, 255))
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'], result)
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertEqual(result['type_verified_basis'], 'input-line-band')

    def test_focus_ring_only_after_image_fails(self):
        # AMEND2 A: same shape, the after image differs only by a
        # focus ring: 3 pixels at the field edges on the clicked line,
        # no text anywhere.
        from PIL import Image
        self.after_image = Image.new('RGB', (20, 20))
        for _x in (0, 1, 19):
            self.after_image.putpixel((_x, 10), (255, 255, 255))
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'], result)
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['error_code'], 'type_unverified')

    def test_hover_only_after_image_fails(self):
        # AMEND2 A: the click focused the field, the pointer then
        # hovered (no second click), and the after image differs only
        # by a 3px hover-state change on the clicked line, no text.
        from PIL import Image
        self.after_image = Image.new('RGB', (20, 20))
        for _x in (14, 15, 16):
            self.after_image.putpixel((_x, 10), (200, 200, 200))
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'hover', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'], result)
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['error_code'], 'type_unverified')

    def test_band_resize_returns_none(self):
        # AMEND2 C: a size mismatch between frames is incomparable,
        # never a pass. The band returns None and the batch falls back
        # to the frame hash with the note.
        from PIL import Image
        old = Image.new('RGB', (20, 20))
        new = Image.new('RGB', (21, 20))
        self.assertIsNone(cu._input_line_changed(old, new, 10))

    def test_type_group_anchors_click_only(self):
        # AMEND2 C: only click/double_click set an anchor. A move,
        # hover, or drag before the type leaves the group anchorless,
        # so a hover-state change can never become the band's line.
        groups = cu.keyboard_groups(
            [{'type': 'move', 'x': 5, 'y': 5},
             {'type': 'hover', 'x': 6, 'y': 6},
             {'type': 'type', 'text': 'hello'}])
        self.assertEqual(cu._type_group_anchors(groups), [None])
        groups = cu.keyboard_groups(
            [{'type': 'drag', 'from': [1, 1], 'to': [9, 9]},
             {'type': 'type', 'text': 'hello'}])
        self.assertEqual(cu._type_group_anchors(groups), [None])
        groups = cu.keyboard_groups(
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'move', 'x': 15, 'y': 15},
             {'type': 'type', 'text': 'hello'}])
        self.assertEqual(cu._type_group_anchors(groups), [(10, 10)])
        groups = cu.keyboard_groups(
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'},
             {'type': 'click', 'x': 10, 'y': 18},
             {'type': 'type', 'text': 'world'}])
        self.assertEqual(cu._type_group_anchors(groups),
                         [(10, 10), (10, 18)])

    def test_focus_gate_runs_before_every_type_group(self):
        # AMEND2 A/C3: the focus gate runs before EVERY type group.
        # The first click lands, the second click misses: the gate
        # fails on the second group and the second type never runs.
        calls = []

        def _focus():
            calls.append(1)
            return (len(calls) == 1,
                    None if len(calls) == 1 else 'second click missed')
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'hello'},
             {'type': 'click', 'x': 10, 'y': 10},
             {'type': 'type', 'text': 'world'}],
            focus_check=_focus)
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['error_code'], 'focus_unverified')
        self.assertEqual(len(calls), 2, 'gate ran before both type groups')
        self.assertEqual(result['completed'], 3,
                         'click + type + click ran; second type never ran')
        self.assertEqual(self.typed.call_count, 1,
                         'one type call: the second type never ran')

    def test_terminal_none_with_dom_check_keeps_pass(self):
        # AMEND2 G: no terminal window to capture, but the DOM value
        # check passed: the pass is preserved, not discarded as None.
        result = cu.desktop_act(
            {}, self.meta, [{'type': 'type', 'text': 'hello'}],
            expected_terminal_window='none',
            type_check=lambda: True)
        self.assertTrue(result['ok'], result)
        self.assertIs(result['type_verified'], True)
        self.assertEqual(result['type_verified_basis'], 'dom-value')

    def test_terminal_none_without_dom_check_fails(self):
        # AMEND2 R4b: no terminal window, no DOM check, no frame: the
        # typed text is unverified and the batch reports ok False.
        result = cu.desktop_act(
            {}, self.meta, [{'type': 'type', 'text': 'hello'}],
            expected_terminal_window='none')
        self.assertFalse(result['ok'], result)
        self.assertIsNone(result['type_verified'])
        self.assertEqual(result['error_code'], 'type_unverified')


    def _tall_fixture(self):
        # AMEND2 A: swap the 20x20 fixture for a 60px-tall frame with
        # two input lines 30px apart, so two type groups have bands
        # that do not overlap (the 20x20 band is anchor y plus/minus
        # 12, which covers the whole frame). Returns a context manager
        # patching the compositor mocks (cursorpos tracks the last
        # pointer command, window reports the 60x60 geometry); the
        # observe/image mocks read self.image/self.meta/self.after_image
        # at call time, so swapping the attributes is enough there.
        from PIL import Image
        from unittest.mock import patch
        import contextlib
        self.image = Image.new('RGB', (60, 60))
        self.meta = dict(self.meta, window_bounds=[0, 0, 60, 60],
                         monitor_box=[0, 0, 60, 60],
                         image_size=[60, 60], region=[0, 0, 60, 60])
        self.after_image = Image.new('RGB', (60, 60))
        for _x in range(12, 18):
            self.after_image.putpixel((_x, 10), (255, 255, 255))

        def _hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 60,
                         'height': 60, 'scale': 1}]
            if query == 'activewindow':
                return {'address': 'fixture'}
            if query == 'cursorpos':
                calls = [c for c in self.pointer.command.call_args_list
                         if c.args and str(c.args[0]).startswith('abs ')]
                if not calls:
                    return {'x': 10, 'y': 10}
                parts = str(calls[-1].args[0]).split()
                return {'x': round(int(parts[1]) / 1000000 * 60),
                        'y': round(int(parts[2]) / 1000000 * 60)}
            raise AssertionError('unexpected compositor query ' + query)

        stack = contextlib.ExitStack()
        stack.enter_context(patch.object(cu, 'hypr', side_effect=_hypr))
        stack.enter_context(patch.object(
            cu, 'window', return_value={'at': [0, 0], 'size': [60, 60]}))
        return stack

    def test_second_type_stubbed_fails_on_its_own_line(self):
        # AMEND2 A: two inputs, text lands in the first only. The
        # first group's band passes, the second group's own band does
        # not, so the batch fails instead of verifying on the first
        # group's line.
        with self._tall_fixture():
            result = cu.desktop_act(
                {}, self.meta,
                [{'type': 'click', 'x': 10, 'y': 10},
                 {'type': 'type', 'text': 'hello'},
                 {'type': 'click', 'x': 10, 'y': 40},
                 {'type': 'type', 'text': 'world'}])
        self.assertFalse(result['ok'], result)
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertEqual(result['type_verified_basis'], 'input-line-band')

    def test_both_types_landed_verifies(self):
        # Both lines carry text pixels: both groups' bands pass.
        with self._tall_fixture():
            for _x in range(12, 18):
                self.after_image.putpixel((_x, 40), (255, 255, 255))
            result = cu.desktop_act(
                {}, self.meta,
                [{'type': 'click', 'x': 10, 'y': 10},
                 {'type': 'type', 'text': 'hello'},
                 {'type': 'click', 'x': 10, 'y': 40},
                 {'type': 'type', 'text': 'world'}])
        self.assertTrue(result['ok'], result)
        self.assertIs(result['type_verified'], True)


if __name__ == '__main__':
    unittest.main(verbosity=2)

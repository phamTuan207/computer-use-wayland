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


if __name__ == '__main__':
    unittest.main(verbosity=2)

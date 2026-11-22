"""P2 element-ref interface rewrite (COORD-CLICK-5, step 7).

Failing-first tests for the P2 implementation, written before the
implementation. Covers, in order:

1. scripts/element_ref.py: the element-ref interface (refs bound to
   snapshot + observation ID, CB-2 scope + observation ID mandatory
   in action data, the stale-ref disagreement protocol disposition
   table, the strict path for destructive/send actions, the exact
   section 7 fail-closed error shape).
2. The A9 validator fix (follow-up to this task, items56): the
   dimension-closure model in scripts/zen_dom.py
   check_viewport_geometry is false for the live Zen state (moz
   [274, 66] + inner [677, 1160] vs window [925, 1176], gaps -26/-50,
   stable). The corrected model accepts a trailing-gap overflow when
   the viewport still fits its window and the origin still verifies
   (exactness + containment), and still refuses a factor-forgotten
   origin (F9/F10), a missing factor, a viewport larger than its
   window, and a viewport origin outside its window.
3. The A9 screen-point form (scripts/dom_act.py ground_input,
   scripts/fastpath.py screen_point_to_image_point): the live call
   sites of dom_rect_to_image_point move to dom_rect_to_screen_point,
   the AMEND4 items 3-4 band ranges are re-derived from the screen
   point, and a missing range is logged instead of silently falling
   back.
4. Plan validation in scripts/code_exec.py (program validation),
   scripts/cu.py CodeExecBackend.act and the CLI act branch, and the
   Zen adapter (scripts/zen_backend.py) under the same contract.

No live laptop work, no browser tasks, never ydotool. No em dash or
en dash anywhere. Run:
python3 tests/test_p2_element_ref.py
"""
import contextlib
import logging
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import code_exec
import dom_act
import element_ref
import fastpath
import zen_backend
import zen_dom
# cu must be the SAME module object test_keyboard_preflight patches
# (it loads cu.py by importlib spec, not by plain import); a plain
# `import cu` here would be a second unpatched copy.
from test_keyboard_preflight import cu
from test_code_exec import FakeBackend, FakeDomBackend
from test_dom_act import FakeDomSession, G30_FIELD, G30_META
import test_zen_dom
from test_zen_dom import FakeWdSession
# test_zen_dom loads zen_dom via importlib.spec_from_file_location,
# a separate module instance from the plain `import zen_dom` above,
# so FakeWdSession raises test_zen_dom.ZenDomError, a different
# class object from zen_dom.ZenDomError. Assertions on errors raised
# through FakeWdSession must use test_zen_dom.ZenDomError.

G30_META_BOUND = dict(G30_META, id='obs-g30', scope='window')
G30_SCREEN_POINT = [2839.0, 2046.5]
G30_IMAGE_POINT = [306.0, 1132.5]

# Live Zen state from the items56 diagnostic (2026-11-22 10:55 +07,
# window 0x557052b62dd0): moz [274, 66], inner [677, 1160], outer
# [925, 1176], window origin [2509, 914], size [925, 1176], monitor
# [2464, 902, 1920, 1200]. Computed absolute origin (2783, 980).
LIVE_MOZ = [274, 66]
LIVE_INNER = [677, 1160]
LIVE_OUTER = [925, 1176]
LIVE_WINDOW_ORIGIN = [2509, 914]
LIVE_WINDOW_SIZE = [925, 1176]
LIVE_MONITOR = [2464, 902, 1920, 1200]
# The moz-computed origin (2783, 980) is WRONG: the reported moz is
# displaced (+34, +58) from the true origin. Kept only to assert it
# is never returned. The pixel-proven TRUE origin is (2749, 922).
LIVE_ABSOLUTE_ORIGIN = [2783, 980]
# The pixel-proven TRUE viewport origin (C5-MOZ-GROWTH, log a42ef12):
# verified moz (240, 8) + inner (677, 1160) closes with gaps +8/+8,
# exactly the C12 values.
VERIFIED_MOZ = [240, 8]
TRUE_ORIGIN = [2749, 922]


class ElementRefTests(unittest.TestCase):
    def test_action_missing_scope_is_refused_naming_the_field(self):
        action = {'type': 'click', 'x': 10, 'y': 10,
                  'observation_id': 'obs-1'}
        with self.assertRaisesRegex(element_ref.ElementRefError, 'scope'):
            element_ref.validate_action(action)

    def test_action_missing_observation_id_is_refused_naming_the_field(self):
        action = {'type': 'click', 'x': 10, 'y': 10, 'scope': 'window'}
        with self.assertRaisesRegex(element_ref.ElementRefError,
                                    'observation_id'):
            element_ref.validate_action(action)

    def test_action_with_scope_and_observation_id_passes(self):
        action = {'type': 'click', 'x': 10, 'y': 10, 'scope': 'window',
                  'observation_id': 'obs-1'}
        self.assertIs(element_ref.validate_action(action), action)

    def test_plan_validation_names_the_first_bad_action_index(self):
        actions = [
            {'type': 'click', 'x': 1, 'y': 1, 'scope': 'window',
             'observation_id': 'obs-1'},
            {'type': 'type', 'text': 'hi', 'scope': 'window'},
        ]
        with self.assertRaisesRegex(element_ref.ElementRefError,
                                    'action 1.*observation_id'):
            element_ref.validate_plan(actions)

    def test_plan_validation_rejects_a_non_list_plan(self):
        with self.assertRaisesRegex(element_ref.ElementRefError,
                                    'actions must be'):
            element_ref.validate_plan({'type': 'click'})

    def test_ref_without_snapshot_id_is_refused(self):
        with self.assertRaisesRegex(element_ref.ElementRefError,
                                    'snapshot_id'):
            element_ref.make_ref(selector='#msg-input', scope='window')

    def test_ref_without_scope_is_refused(self):
        with self.assertRaisesRegex(element_ref.ElementRefError, 'scope'):
            element_ref.make_ref(selector='#msg-input',
                                 snapshot_id='snap-1')

    def test_ref_carries_its_binding(self):
        ref = element_ref.make_ref(
            selector='#msg-input', snapshot_id='snap-1', scope='window',
            plan_rect={'x': 86, 'y': 1101, 'width': 440, 'height': 63},
            distinguishing_state={'value': 'hello'})
        self.assertEqual(ref['snapshot_id'], 'snap-1')
        self.assertEqual(ref['scope'], 'window')
        self.assertEqual(ref['plan_rect']['x'], 86)
        self.assertEqual(ref['distinguishing_state'], {'value': 'hello'})
        self.assertIs(element_ref.validate_ref(ref), ref)

    def test_send_key_after_type_is_strict(self):
        actions = [{'type': 'type', 'text': 'hello'},
                   {'type': 'key', 'keys': ['Enter']}]
        self.assertTrue(
            element_ref.is_strict_action(actions[1], actions))
        self.assertFalse(
            element_ref.is_strict_action(actions[0], actions))

    def test_lone_enter_is_not_a_send(self):
        actions = [{'type': 'key', 'keys': ['Enter']}]
        self.assertFalse(
            element_ref.is_strict_action(actions[0], actions))

    def test_destructive_flag_is_strict(self):
        action = {'type': 'click', 'x': 1, 'y': 1, 'destructive': True}
        self.assertTrue(element_ref.is_strict_action(action, [action]))
        plain = {'type': 'click', 'x': 1, 'y': 1}
        self.assertFalse(element_ref.is_strict_action(plain, [plain]))

    def test_rect_agreement_uses_half_px_tolerance(self):
        plan = {'x': 86, 'y': 1101, 'width': 440, 'height': 63}
        same = dict(plan, x=86.5)
        self.assertTrue(element_ref.rects_agree(plan, same))
        moved = dict(plan, x=86.6)
        self.assertFalse(element_ref.rects_agree(plan, moved))
        self.assertFalse(element_ref.rects_agree(plan, None))

    def test_binding_check_names_each_failure(self):
        self.assertEqual(element_ref.check_binding(
            snapshot_id='snap-1', scope='window', age_seconds=10,
            expected_snapshot_id='snap-1', expected_scope='window'),
            None)
        self.assertEqual(element_ref.check_binding(
            snapshot_id='other', scope='window', age_seconds=10,
            expected_snapshot_id='snap-1', expected_scope='window'),
            'snapshot_unbound')
        self.assertEqual(element_ref.check_binding(
            snapshot_id='snap-1', scope='window', age_seconds=121,
            expected_snapshot_id='snap-1', expected_scope='window'),
            'snapshot_expired')
        self.assertEqual(element_ref.check_binding(
            snapshot_id='snap-1', scope='window', age_seconds=-1,
            expected_snapshot_id='snap-1', expected_scope='window'),
            'snapshot_expired')
        self.assertEqual(element_ref.check_binding(
            snapshot_id='snap-1', scope='screen', age_seconds=10,
            expected_snapshot_id='snap-1', expected_scope='window'),
            'scope_changed')

    def test_stale_ref_error_has_the_protocol_shape(self):
        error = element_ref.stale_ref_error(
            reason='element_missing', selector='#msg-input',
            snapshot_id='snap-1', scope='window',
            plan_rect={'x': 86, 'y': 1101, 'width': 440, 'height': 63},
            live_rect=None, action_index=2)
        self.assertIs(error['input_sent'], False)
        self.assertIs(error['target_received'], False)
        self.assertIs(error['verified'], False)
        self.assertEqual(error['verified_basis'],
                         'stale-ref: element_missing')
        self.assertIs(error['ok'], False)
        self.assertEqual(error['error']['code'], 'stale_ref')
        self.assertEqual(error['error']['reason'], 'element_missing')
        self.assertEqual(error['error']['selector'], '#msg-input')
        self.assertEqual(error['error']['snapshot_id'], 'snap-1')
        self.assertEqual(error['error']['scope'], 'window')
        self.assertEqual(error['error']['action_index'], 2)
        self.assertIs(error['error']['batch_stopped'], True)
        self.assertIsNone(error['error']['live_rect'])

    def test_disposition_moved_confirmed_regrounds_and_acts(self):
        verdict = element_ref.decide_disposition(
            reason='rect_moved', identity_confirmed=True,
            strict=False, reground_ok=True)
        self.assertEqual(verdict['verdict'], 'reground_and_act')
        self.assertEqual(verdict['reason'], 'rect_moved')

    def test_disposition_moved_unconfirmed_refuses(self):
        verdict = element_ref.decide_disposition(
            reason='rect_moved', identity_confirmed=False,
            strict=False, reground_ok=True)
        self.assertEqual(verdict['verdict'], 'refuse')
        self.assertEqual(verdict['reason'], 'identity_unconfirmed')

    def test_disposition_strict_path_stops_on_any_disagreement(self):
        for reason in ('rect_moved', 'scope_changed', 'snapshot_expired',
                       'unstable', 'covered'):
            verdict = element_ref.decide_disposition(
                reason=reason, identity_confirmed=True,
                strict=True, reground_ok=True)
            self.assertEqual(verdict['verdict'], 'stop', reason)
            self.assertEqual(verdict['reason'], reason)

    def test_disposition_ambiguous_stops_never_picks_first(self):
        verdict = element_ref.decide_disposition(
            reason='element_ambiguous', strict=False, reground_ok=False)
        self.assertEqual(verdict['verdict'], 'stop')
        self.assertEqual(verdict['reason'], 'element_ambiguous')

    def test_disposition_scope_change_regrounds_when_resolvable(self):
        verdict = element_ref.decide_disposition(
            reason='scope_changed', strict=False, reground_ok=True)
        self.assertEqual(verdict['verdict'], 'reground_and_act')
        verdict = element_ref.decide_disposition(
            reason='scope_changed', strict=False, reground_ok=False)
        self.assertEqual(verdict['verdict'], 'stop')
        self.assertEqual(verdict['reason'], 'scope_changed_unresolved')

    def test_disposition_missing_refuses_and_navigation_replans(self):
        verdict = element_ref.decide_disposition(
            reason='element_missing', strict=False, reground_ok=False)
        self.assertEqual(verdict['verdict'], 'refuse')
        self.assertEqual(verdict['reason'], 'element_missing')
        verdict = element_ref.decide_disposition(
            reason='navigation', strict=False, reground_ok=False)
        self.assertEqual(verdict['verdict'], 'replan')
        self.assertEqual(verdict['reason'], 'navigation')

    def test_disposition_unknown_reason_fails_closed(self):
        verdict = element_ref.decide_disposition(
            reason='something_new', strict=False, reground_ok=True)
        self.assertEqual(verdict['verdict'], 'stop')
        self.assertEqual(verdict['reason'], 'something_new')


class ValidatorFixTests(unittest.TestCase):
    def test_live_zen_state_refuses_unverified_moz(self):
        # items56 live numbers: moz [274, 66] + inner [677, 1160]
        # vs window [925, 1176], gaps -26/-50. The pixel proof
        # (MOZ-GROWTH, log a42ef12) shows the reported moz is
        # displaced (+34, +58) from the true origin (240, 8), so
        # the validator must refuse the unverified state: accepting
        # the moz-computed origin (2783, 980) would ground clicks
        # 34px right and 58px down from the true origin. This
        # corrects the earlier "accept with warning" model, which
        # returned the wrong origin.
        with self.assertRaisesRegex(zen_dom.ZenDomError, 'closure'):
            zen_dom.check_viewport_geometry(
                LIVE_MOZ, LIVE_ABSOLUTE_ORIGIN, LIVE_WINDOW_ORIGIN,
                LIVE_WINDOW_SIZE, LIVE_INNER, LIVE_MONITOR, factor=1)

    def test_live_zen_state_accepts_verified_moz(self):
        # The verified-origin path: the pixel-proven moz (240, 8)
        # closes with gaps +8/+8, so the verified absolute origin
        # (2749, 922) is returned, never the moz-computed (2783, 980).
        origin = zen_dom.check_viewport_geometry(
            LIVE_MOZ, LIVE_ABSOLUTE_ORIGIN, LIVE_WINDOW_ORIGIN,
            LIVE_WINDOW_SIZE, LIVE_INNER, LIVE_MONITOR, factor=1,
            verified_moz_inner=VERIFIED_MOZ)
        self.assertEqual(origin, TRUE_ORIGIN)
        self.assertNotEqual(origin, LIVE_ABSOLUTE_ORIGIN)

    def test_live_zen_state_logs_the_verified_override(self):
        with self.assertLogs('zen_dom', level='WARNING') as logs:
            zen_dom.check_viewport_geometry(
                LIVE_MOZ, LIVE_ABSOLUTE_ORIGIN, LIVE_WINDOW_ORIGIN,
                LIVE_WINDOW_SIZE, LIVE_INNER, LIVE_MONITOR, factor=1,
                verified_moz_inner=VERIFIED_MOZ)
        self.assertTrue(
            any('verified' in line and '-34' in line
                for line in logs.output),
            'the override warning must name the verified moz and the '
            'offset from the reported moz: %s' % (logs.output,))

    def test_c12_state_still_passes(self):
        origin = zen_dom.check_viewport_geometry(
            [240, 8], [2749, 922], [2509, 914], [1863, 1176],
            [1615, 1160], None, factor=1)
        self.assertEqual(origin, [2749, 922])

    def test_factor_forgotten_origin_still_refused(self):
        # F10: at factor 2 the true absolute origin is (2989, 930);
        # the factor-forgotten (2749, 922) is 240 screen px off and
        # must be refused by the exactness check.
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [240, 8], [2749, 922], [2509, 914], [1863, 1176],
                [1615, 1160], None, factor=2)

    def test_missing_factor_still_refused(self):
        # F10: a validator that silently assumes factor 1 accepts a
        # factor-forgotten origin; passing no factor refuses.
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [240, 8], [2749, 922], [2509, 914], [931.5, 588],
                [690, 572], None)

    def test_viewport_larger_than_window_still_refused(self):
        # Corrected model, structural invariant: a viewport wider or
        # taller than its window means the size input is wrong, so
        # the call still fails closed. This is the refusal half of
        # the old factor-2 small-window test, kept in strength.
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [240, 8], [2989, 930], [2509, 914], [1500, 1000],
                [1615, 1160], None, factor=2)

    def test_viewport_origin_outside_window_still_refused(self):
        # A viewport origin at or past the window edge cannot close
        # inside that window, so the closure refusal fires: moz
        # [1863, 8] + inner [100, 100] overflows the [1863, 1176]
        # window on the x axis (gap -100).
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [1863, 8], [4372, 922], [2509, 914], [1863, 1176],
                [100, 100], None, factor=1)

    def test_raw_moz_as_absolute_still_refused(self):
        # The old bug: the raw mozInner pair (240, 8) used as the
        # absolute origin is off-monitor and must be refused by
        # containment.
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [240, 8], [240, 8], [2509, 914], [1863, 1176],
                [1615, 1160], None, factor=1)

    def test_viewport_origin_live_state_via_session(self):
        # The full viewport_origin chain on the live numbers, through
        # the scripted session fake. Unverified, the origin stage
        # that failed live at 09:20 and 10:55 still refuses; with
        # the pixel-proven verified moz (240, 8) it returns the TRUE
        # origin (2749, 922), never the moz-computed (2783, 980).
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = list(LIVE_MOZ)
        session.dom_inner = list(LIVE_INNER)
        session.dom_outer = list(LIVE_OUTER)
        with self.assertRaisesRegex(test_zen_dom.ZenDomError, 'closure'):
            session.viewport_origin(
                LIVE_WINDOW_ORIGIN, LIVE_WINDOW_SIZE, LIVE_MONITOR)
        origin = session.viewport_origin(
            LIVE_WINDOW_ORIGIN, LIVE_WINDOW_SIZE, LIVE_MONITOR,
            verified_moz_inner=VERIFIED_MOZ)
        self.assertEqual(origin, TRUE_ORIGIN)
        self.assertTrue(
            any('verified' in w for w in session.last_geometry_warnings),
            'the live call must record its verified-origin override: '
            '%s' % (session.last_geometry_warnings,))
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        origin = session.viewport_origin([2509, 914], [1863, 1176])
        self.assertEqual(origin, [2749, 922])
        self.assertEqual(session.last_geometry_warnings, [],
                         'no warning is recorded when the gaps close')

    def test_viewport_origin_live_state_records_the_override(self):
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = list(LIVE_MOZ)
        session.dom_inner = list(LIVE_INNER)
        session.dom_outer = list(LIVE_OUTER)
        origin = session.viewport_origin(
            LIVE_WINDOW_ORIGIN, LIVE_WINDOW_SIZE, LIVE_MONITOR,
            verified_moz_inner=VERIFIED_MOZ)
        self.assertEqual(origin, TRUE_ORIGIN)
        self.assertTrue(
            any('verified' in w for w in session.last_geometry_warnings),
            'the session must record the verified-origin override '
            'for the live probe to read: %s'
            % (session.last_geometry_warnings,))


class NoPointerDelegateTests(unittest.TestCase):
    """Step-7 AMEND fix items 1 and 3: with pointer=None the Zen
    backend must report no_pointer_delegate on EVERY dispatch path,
    and wait/assert must not claim input was sent.

    Failing-first: before the fix the re-ground path reports
    action_failed/focus_check (click) or action_failed/dom-value
    (fill), and the main path reports no-dom-postcondition errors
    for type/move, because only the 8-type allowlist guard checks
    the pointer. Wait/assert report input_sent True although no
    input is dispatched.
    """

    def _backend_no_pointer(self, fields=None):
        session = FakeZenSession(fields or _zen_fields())
        backend = zen_backend.ZenDomBackend(
            session_factory=lambda: session,
            windows_fn=_zen_windows,
            pointer=None)
        return backend, session

    def _observe(self, backend):
        backend.dom_start()
        return backend.dom_observe('Example', '#c5-text', 10)

    def _action(self, snapshot_id, **overrides):
        action = {'type': 'click', 'ref': '#c5-text',
                  'scope': 'Example',
                  'observation_id': snapshot_id}
        action.update(overrides)
        return action

    def test_main_path_click_reports_no_pointer_delegate(self):
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'])], None, True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'],
                         'no_pointer_delegate')
        self.assertFalse(result['results'][0]['input_sent'])
        self.assertFalse(result['results'][0]['target_received'])
        self.assertEqual(result['results'][0]['verified_basis'],
                         'no-pointer-delegate')
        backend.close()

    def test_main_path_type_reports_no_pointer_delegate(self):
        # Before the fix this reported action_failed with
        # no-dom-postcondition:type, hiding the true cause.
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='type',
                          text='hello')], None, True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'],
                         'no_pointer_delegate')
        self.assertFalse(result['results'][0]['input_sent'])
        backend.close()

    def test_main_path_move_reports_no_pointer_delegate(self):
        # Before the fix this reported action_failed with
        # no-dom-postcondition:move, hiding the true cause.
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='move')],
            None, True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'],
                         'no_pointer_delegate')
        self.assertFalse(result['results'][0]['input_sent'])
        backend.close()

    def test_reground_click_reports_no_pointer_delegate(self):
        # The rect moved, the batch is non-strict, so the re-ground
        # path acts on the fresh rect. Before the fix it called
        # _dispatch directly and reported action_failed/focus_check.
        backend, session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        session.fields['#c5-text']['rect'] = {
            'x': 100, 'y': 300, 'width': 200, 'height': 30}
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'])], None, True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'],
                         'no_pointer_delegate')
        self.assertFalse(result['results'][0]['input_sent'])
        self.assertFalse(result['results'][0]['target_received'])
        backend.close()

    def test_reground_fill_reports_no_pointer_delegate(self):
        # Before the fix the re-ground fill reported
        # action_failed/dom-value instead of no_pointer_delegate.
        backend, session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        session.fields['#c5-text']['rect'] = {
            'x': 100, 'y': 300, 'width': 200, 'height': 30}
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='fill',
                          text='hello')], None, True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'],
                         'no_pointer_delegate')
        self.assertFalse(result['results'][0]['input_sent'])
        backend.close()

    def test_wait_reports_no_input_sent(self):
        # Wait is time.sleep only: no input is dispatched, so
        # input_sent and target_received must be False, while the
        # action itself still succeeds.
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='wait', ms=1)],
            None, True)
        self.assertTrue(result['ok'], result)
        self.assertFalse(result['results'][0]['input_sent'])
        self.assertFalse(result['results'][0]['target_received'])
        backend.close()

    def test_assert_reports_no_input_sent(self):
        # Assert only reads state: no input is dispatched. The
        # field value is '' and the asserted text is '', so the
        # assert itself passes on the dom-value postcondition.
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='assert',
                          text='')], None, True)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['results'][0]['verified'])
        self.assertFalse(result['results'][0]['input_sent'])
        self.assertFalse(result['results'][0]['target_received'])
        backend.close()

    def test_assert_mismatch_still_fails_without_input_sent(self):
        # A failing assert must still fail (verified False) even
        # though no input was sent: ok comes from the postcondition,
        # not from input_sent.
        backend, _session = self._backend_no_pointer()
        snapshot = self._observe(backend)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='assert',
                          text='not-the-value')], None, True)
        self.assertFalse(result['ok'])
        self.assertFalse(result['results'][0]['verified'])
        self.assertFalse(result['results'][0]['input_sent'])
        backend.close()


class ValidatorLimitationTests(unittest.TestCase):
    """Step-7 AMEND fix item 2 (A1/A2), FIXED by the step-9
    prototype: on the normal passing branch
    check_viewport_geometry now PREFERS a supplied
    verified_moz_inner over the reported moz. The old behavior
    (return the moz-computed origin and ignore verified_moz_inner
    unless closure overflowed) is gone: a wrong-but-self-consistent
    moz is CORRECTED to the verified origin when verified is
    supplied, never accepted. The residual that cannot be fixed in
    the validator: with NO verified value supplied, a
    self-consistent-but-wrong moz is still undetectable, so the
    prototype must pass verified moz always (test_a2 pins that
    residual openly instead of hiding it).
    """

    # Redteam attack numbers (verify report section 5): window
    # [2509, 914], size [925, 1176], monitor [2464, 902, 1920,
    # 1200]. True origin [2749, 922] from verified moz [240, 8].
    WINDOW = [2509, 914]
    SIZE = [925, 1176]
    MONITOR = [2464, 902, 1920, 1200]
    TRUE_ORIGIN = [2749, 922]

    def test_a1_self_consistent_but_wrong_moz_is_corrected(self):
        # Moz [250, 18] is wrong (+10, +10 from true [240, 8]) but
        # self-consistent with inner [667, 1150] (gaps 8/8). With
        # the TRUE verified moz [240, 8] supplied, the validator
        # returns the VERIFIED origin [2749, 922], never the
        # moz-computed [2759, 932], which is 10px off.
        origin = zen_dom.check_viewport_geometry(
            [250, 18], [2759, 932], self.WINDOW, self.SIZE,
            [667, 1150], self.MONITOR, factor=1,
            verified_moz_inner=[240, 8])
        self.assertEqual(origin, self.TRUE_ORIGIN)
        self.assertNotEqual(origin, [2759, 932])

    def test_a1_correction_is_logged(self):
        # The normal-branch override is logged with the verified
        # value and the offset, like the overflow-branch override.
        with self.assertLogs('zen_dom', level='WARNING') as logs:
            zen_dom.check_viewport_geometry(
                [250, 18], [2759, 932], self.WINDOW, self.SIZE,
                [667, 1150], self.MONITOR, factor=1,
                verified_moz_inner=[240, 8])
        self.assertTrue(
            any('verified' in line and '-10' in line
                for line in logs.output),
            'the override warning must name the verified moz and the '
            'offset from the reported moz: %s' % (logs.output,))

    def test_a2_no_verified_moz_still_accepts_wrong_moz(self):
        # Residual, pinned openly: with NO verified value the
        # validator cannot detect a self-consistent-but-wrong moz,
        # so it still ACCEPTS the moz-computed origin [2759, 932],
        # 10px off. This is why the prototype must pass verified
        # moz always; the validator alone cannot close this gap.
        origin = zen_dom.check_viewport_geometry(
            [250, 18], [2759, 932], self.WINDOW, self.SIZE,
            [667, 1150], self.MONITOR, factor=1)
        self.assertEqual(origin, [2759, 932])
        self.assertNotEqual(origin, self.TRUE_ORIGIN)

    def test_a3_true_moz_returns_the_true_origin(self):
        # Sanity anchor for A1/A2: with the true moz the same
        # inputs return the true origin, which IS the moz-computed
        # origin in this case.
        origin = zen_dom.check_viewport_geometry(
            [240, 8], [2749, 922], self.WINDOW, self.SIZE,
            [667, 1150], self.MONITOR, factor=1)
        self.assertEqual(origin, self.TRUE_ORIGIN)

    def test_a4_wrong_verified_moz_refuses(self):
        # A verified value that fails its own checks refuses
        # instead of falling back to the reported moz: a wrong
        # verified [300, 18] does not close (gap -42), so the call
        # raises rather than returning either origin.
        with self.assertRaises(zen_dom.ZenDomError):
            zen_dom.check_viewport_geometry(
                [250, 18], [2759, 932], self.WINDOW, self.SIZE,
                [667, 1150], self.MONITOR, factor=1,
                verified_moz_inner=[300, 18])

    def test_a5_verified_equal_to_moz_returns_the_origin(self):
        # Verified equal to the reported moz changes nothing: the
        # origin is returned with no override.
        origin = zen_dom.check_viewport_geometry(
            [240, 8], [2749, 922], self.WINDOW, self.SIZE,
            [667, 1150], self.MONITOR, factor=1,
            verified_moz_inner=[240, 8])
        self.assertEqual(origin, self.TRUE_ORIGIN)


if __name__ == '__main__':
    unittest.main()


class ScreenPointFormTests(unittest.TestCase):
    def test_ground_input_returns_the_screen_point(self):
        # A9: ground_input converts the rect once, at the driver
        # edge, to a screen point. G30: origin [2533, 914] + rect
        # center (306, 1132.5) at factor 1 is [2839, 2046.5].
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META_BOUND,
                                      '#msg-input')
        self.assertEqual(ground['screen_point'], G30_SCREEN_POINT)
        self.assertEqual(ground['viewport_origin'], [2533, 914])

    def test_ground_input_keeps_the_image_point_for_the_click_path(self):
        # desktop_act still consumes image points, so the evidence
        # keeps 'point' as the image point, derived from the screen
        # point at the edge (not from a fused rect-to-image call).
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META_BOUND,
                                      '#msg-input')
        self.assertEqual(ground['point'], G30_IMAGE_POINT)

    def test_ground_evidence_carries_scope_and_observation_id(self):
        # CB-2: every ref carries its binding (snapshot ID, scope)
        # with it, taken from the observation meta.
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META_BOUND,
                                      '#msg-input')
        self.assertEqual(ground['observation_id'], 'obs-g30')
        self.assertEqual(ground['scope'], 'window')

    def test_ranges_rederived_from_the_screen_point(self):
        # P2-SPEC observation 1: the AMEND4 items 3-4 band ranges
        # are re-derived from the screen-point form. G30 field rect
        # x 86..526, y 1101..1164, image and region map 1:1, so the
        # ranges are exactly the rect, as before.
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META_BOUND,
                                      '#msg-input')
        self.assertEqual(dom_act.grounded_x_range(ground, G30_META_BOUND),
                         [86.0, 526.0])
        self.assertEqual(dom_act.grounded_y_range(ground, G30_META_BOUND),
                         [1101.0, 1164.0])

    def test_ranges_from_a_screen_point_only_ground(self):
        # The re-derivation reads ground['screen_point'], not
        # ground['point']: a ground dict carrying only the screen
        # point still yields the field ranges.
        ground = {'rect': G30_FIELD['rect'],
                  'screen_point': G30_SCREEN_POINT,
                  'scale_factor': 1}
        self.assertEqual(dom_act.grounded_x_range(ground, G30_META_BOUND),
                         [86.0, 526.0])
        self.assertEqual(dom_act.grounded_y_range(ground, G30_META_BOUND),
                         [1101.0, 1164.0])

    def test_screen_point_to_image_point_round_trips(self):
        self.assertEqual(
            fastpath.screen_point_to_image_point(
                G30_META_BOUND, G30_SCREEN_POINT[0], G30_SCREEN_POINT[1]),
            G30_IMAGE_POINT)
        with self.assertRaises(ValueError):
            fastpath.screen_point_to_image_point(G30_META_BOUND, 0, 0)

    def test_dom_rect_to_image_point_kept_for_tests_and_legacy(self):
        # The fused function stays (final direction: kept for tests
        # and legacy) but no longer sits on the live path: its value
        # equals the screen-point form composed with the edge map.
        point = fastpath.dom_rect_to_image_point(
            G30_META_BOUND, G30_FIELD['rect'], [2533, 914], 1)
        self.assertEqual(point, G30_IMAGE_POINT)

    def test_missing_range_is_logged_not_silent(self):
        # P2-SPEC observation 2: when no rect grounds, the ranges
        # stay None and the batch used to silently keep the
        # full-width band. The helper now logs the missing range.
        session = FakeDomSession({})
        with self.assertLogs('dom_act', level='WARNING') as logs:
            x_ranges, y_ranges = dom_act.ground_field_ranges(
                session, G30_META_BOUND, '#nope')
        self.assertIsNone(x_ranges)
        self.assertIsNone(y_ranges)
        self.assertTrue(
            any('#nope' in line and 'range' in line
                for line in logs.output),
            'the missing range must be logged with the selector: %s'
            % (logs.output,))

    def test_ground_field_ranges_returns_the_grounded_ranges(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        x_ranges, y_ranges = dom_act.ground_field_ranges(
            session, G30_META_BOUND, '#msg-input')
        self.assertEqual(x_ranges, [[86.0, 526.0]])
        self.assertEqual(y_ranges, [[1101.0, 1164.0]])

    def test_ground_points_strict_mode_stops_on_a_move(self):
        # Protocol section 5: GroundPoints re-grounds silently only
        # for re-ground-and-continue rows, never for strict-path
        # actions, where a move must stop the batch instead.
        fields = {'#msg-input': dict(G30_FIELD)}
        session = FakeDomSession(fields)
        points = dom_act.ground_many(session, G30_META_BOUND,
                                     ['#msg-input'], strict=True)
        self.assertEqual(points['#msg-input']['point'], G30_IMAGE_POINT)
        fields['#msg-input'] = dict(
            G30_FIELD,
            rect={'x': 86, 'y': 1000, 'width': 440, 'height': 63})
        with self.assertRaisesRegex(dom_act.DomActError, 'stale_ref'):
            points['#msg-input']

    def test_confirm_locate_strict_refuses_an_unprobed_session(self):
        # Protocol section 2: a production session that cannot
        # report interactive or unique does not satisfy the
        # protocol. The strict path refuses instead of recording
        # 'unprobed' and clicking anyway.
        session = FakeDomSession({'#msg-input': G30_FIELD})
        self.assertFalse(hasattr(session, 'locate_confirmed'))
        with self.assertRaisesRegex(dom_act.DomActError, 'unprobed'):
            dom_act.confirm_locate(session, '#msg-input', strict=True)


class CodeExecPlanValidationTests(unittest.TestCase):
    def _session_with_snapshot(self):
        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        return backend, session, snapshot

    def _bound_action(self, snapshot, action):
        action = dict(action)
        action.setdefault('scope', 'tab-1')
        action.setdefault('observation_id', snapshot['snapshot'])
        return action

    def test_dom_act_refuses_action_missing_scope(self):
        _backend, session, snapshot = self._session_with_snapshot()
        action = {'type': 'click',
                  'ref': snapshot['elements'][0]['ref'],
                  'observation_id': snapshot['snapshot']}
        with self.assertRaisesRegex(code_exec.CodeExecError, 'scope'):
            session.api_dom_act(snapshot, [action])

    def test_dom_act_refuses_action_missing_observation_id(self):
        _backend, session, snapshot = self._session_with_snapshot()
        action = {'type': 'click',
                  'ref': snapshot['elements'][0]['ref'], 'scope': 'tab-1'}
        with self.assertRaisesRegex(code_exec.CodeExecError,
                                    'observation_id'):
            session.api_dom_act(snapshot, [action])

    def test_dom_act_refuses_mismatched_observation_id(self):
        _backend, session, snapshot = self._session_with_snapshot()
        action = self._bound_action(snapshot, {
            'type': 'click', 'ref': snapshot['elements'][0]['ref'],
            'observation_id': 'another-snapshot'})
        with self.assertRaisesRegex(code_exec.CodeExecError,
                                    'stale_ref: snapshot_unbound'):
            session.api_dom_act(snapshot, [action])

    def test_dom_act_refuses_mismatched_scope(self):
        _backend, session, snapshot = self._session_with_snapshot()
        action = self._bound_action(snapshot, {
            'type': 'click', 'ref': snapshot['elements'][0]['ref'],
            'scope': 'tab-2'})
        with self.assertRaisesRegex(code_exec.CodeExecError,
                                    'stale_ref: scope_changed'):
            session.api_dom_act(snapshot, [action])

    def test_dom_act_accepts_bound_actions(self):
        _backend, session, snapshot = self._session_with_snapshot()
        action = self._bound_action(snapshot, {
            'type': 'click', 'ref': snapshot['elements'][0]['ref']})
        self.assertTrue(session.api_dom_act(snapshot, [action])['ok'])

    def test_dom_assert_stamps_the_binding_itself(self):
        # api_dom_assert builds its own assert action, so the
        # session stamps scope + observation_id from the binding;
        # the program never writes them for this internal action.
        _backend, session, snapshot = self._session_with_snapshot()
        self.assertTrue(session.api_dom_assert(
            snapshot, selector='#result', text='ready'))
        built = _backend.dom_calls[-1][3][0]
        self.assertEqual(built['scope'], 'tab-1')
        self.assertEqual(built['observation_id'], snapshot['snapshot'])

    def test_desktop_act_refuses_action_missing_scope(self):
        session = code_exec.CodeExecSession(FakeBackend())
        obs = session.api_observe(window='0xabc')
        action = {'type': 'wait', 'ms': 0,
                  'observation_id': obs['id']}
        with self.assertRaisesRegex(code_exec.CodeExecError, 'scope'):
            session.api_act([action], obs)

    def test_desktop_act_refuses_mismatched_observation_id(self):
        session = code_exec.CodeExecSession(FakeBackend())
        obs = session.api_observe(window='0xabc')
        action = {'type': 'wait', 'ms': 0, 'scope': obs['scope'],
                  'observation_id': 'deadbeef0000'}
        with self.assertRaisesRegex(code_exec.CodeExecError,
                                    'stale_ref: snapshot_unbound'):
            session.api_act([action], obs)

    def test_desktop_act_accepts_bound_actions(self):
        session = code_exec.CodeExecSession(FakeBackend())
        obs = session.api_observe(window='0xabc')
        action = {'type': 'wait', 'ms': 0, 'scope': obs['scope'],
                  'observation_id': obs['id']}
        result = session.api_act([action], obs)
        self.assertTrue(result['ok'])


if __name__ == '__main__':
    unittest.main()


class FakeZenSession:
    """A scriptable stand-in for ZenSession, exposing only its
    public methods: __enter__/__exit__, list_tabs, tab_at,
    switch_to_handle, current_handle, locate, locate_confirmed,
    hit_check, focus_check, field_value, verify_typed,
    sent_bubble_contains, harvest, viewport_origin,
    live_window_origin, last_scale_factor."""
    def __init__(self, fields=None, tabs=None):
        self.fields = fields or {}
        self.tabs = tabs or [
            {'handle': 'aaa11111', 'title': 'Example',
             'url': 'https://example.com/'}]
        self.current = 0
        self.entered = False
        self.exited = False
        self.last_scale_factor = 1
        self.last_display_metrics = {}
        # Live narrowed-window fixture (items56, 2026-11-22 10:55):
        # moz [274, 66], inner [677, 1160], outer [925, 1176].
        self.dom_origin = [274, 66]
        self.dom_inner = [677, 1160]
        self.dom_outer = [925, 1176]
        self.last_geometry_warnings = []
        self.sent_bubbles = []
        # Rendered text of plain elements (a sent bubble div has
        # no value property, so field_value returns None for it,
        # while element_text returns its text). Keyed by selector.
        self.texts = {}

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *args):
        self.exited = True
        return False

    def list_tabs(self):
        return [dict(tab) for tab in self.tabs]

    def tab_at(self, index):
        self.current = index
        return self.tabs[index]

    def switch_to_handle(self, handle):
        for index, tab in enumerate(self.tabs):
            if tab['handle'].startswith(handle[:8]):
                self.current = index
                return tab
        raise zen_dom.ZenDomError('no tab with handle ' + handle)

    def current_handle(self):
        return self.tabs[self.current]['handle']

    def locate(self, selector):
        field = self.fields.get(selector)
        return None if field is None else dict(field['rect'])

    def locate_confirmed(self, selector):
        field = self.fields.get(selector)
        if field is None:
            return None
        return {'selector': selector, 'rect': dict(field['rect']),
                'visible': True, 'interactive': True,
                'uncovered': True, 'stable': True,
                'unique': True, 'unique_count': 1,
                'focusable': True, 'enabled': True,
                'in_viewport': True, 'state': field.get('value', '')}

    def hit_check(self, selector):
        return self.fields.get(selector) is not None

    def focus_check(self, selector):
        return self.fields.get(selector) is not None

    def field_value(self, selector):
        field = self.fields.get(selector)
        return None if field is None else field.get('value', '')

    def element_text(self, selector):
        # Trimmed rendered text, or None when the element has none.
        # Mirrors the real ZenSession: a plain div (a sent bubble)
        # has text but no value, so field_value returns None for
        # it while element_text returns its text.
        text = self.texts.get(selector)
        return None if text is None else str(text).strip()

    def verify_typed(self, selector, text):
        return self.field_value(selector) == text

    def arm_typed_flag(self, selector):
        return True

    def typed_flag(self, selector):
        return True

    def sent_bubble_contains(self, text):
        # One argument, like the real ZenSession (zen_dom.py:1296).
        # The old two-argument form hid the backend arity mismatch
        # (W-ZENPREP finding B).
        return text in self.sent_bubbles

    def harvest(self, selectors):
        return [{'selector': s, 'rect': dict(self.fields[s]['rect']),
                 'hit': True, 'focused': False,
                 'state': self.fields[s].get('value', '')}
                for s in selectors if s in self.fields]

    def viewport_origin(self, window_origin, window_size,
                        monitor_box=None):
        # The fake models the live narrowed window: dom_origin is the
        # REPORTED moz [274, 66], which is displaced (+34, +58) from
        # the true origin. It supplies the pixel-proven verified moz
        # [240, 8] (MOZ-GROWTH, log a42ef12), so the backend grounds
        # on the true origin [2749, 922] and returns what the
        # validator returns.
        absolute = [window_origin[0] + self.dom_origin[0],
                    window_origin[1] + self.dom_origin[1]]
        return zen_dom.check_viewport_geometry(
            self.dom_origin, absolute, window_origin, window_size,
            self.dom_inner, monitor_box, factor=1,
            verified_moz_inner=[240, 8])

    def live_window_origin(self, address):
        return [2509, 914]


class FakeZenPointer:
    """Pointer/keyboard delegate for the Zen backend: a click lands
    on the field, a fill types into it, a send key bubbles the
    typed text. Records every call with its screen point."""
    def __init__(self, session):
        self.session = session
        self.calls = []

    def __call__(self, action, screen_point):
        self.calls.append((dict(action),
                           None if screen_point is None
                           else list(screen_point)))
        selector = action.get('ref') or action.get('selector')
        if action['type'] in ('click', 'double_click'):
            return True
        if action['type'] in ('fill', 'set_value'):
            field = self.session.fields.get(selector)
            if field is not None:
                field['value'] = action.get('text', '')
            return True
        if action['type'] == 'key':
            field = self.session.fields.get(selector)
            if field is not None:
                self.session.sent_bubbles.append(field.get('value', ''))
            return True
        return True


def _zen_fields():
    return {'#c5-text': {'rect': {'x': 100, 'y': 200, 'width': 200,
                                  'height': 30}, 'value': ''}}


def _zen_windows():
    return [{'class': 'zen', 'address': '0x557052b62dd0',
             'at': [2509, 914], 'size': [925, 1176],
             'title': 'Example'}]


class ZenBackendTests(unittest.TestCase):
    def _backend(self, fields=None, tabs=None):
        session = FakeZenSession(fields or _zen_fields(), tabs)
        pointer = FakeZenPointer(session)
        backend = zen_backend.ZenDomBackend(
            session_factory=lambda: session,
            windows_fn=_zen_windows,
            pointer=pointer)
        return backend, session, pointer

    def test_dom_start_opens_a_session_and_waits_for_the_zen_window(self):
        backend, session, _pointer = self._backend()
        started = backend.dom_start()
        self.assertTrue(started['ok'])
        self.assertTrue(session.entered)
        backend.close()

    def test_dom_start_refuses_when_no_zen_window_appears(self):
        session = FakeZenSession(_zen_fields())
        backend = zen_backend.ZenDomBackend(
            session_factory=lambda: session,
            windows_fn=lambda: [],
            pointer=FakeZenPointer(session),
            session_timeout_s=0.01)
        with self.assertRaisesRegex(zen_dom.ZenDomError,
                                    'no Zen window'):
            backend.dom_start()
        self.assertTrue(session.exited)

    def test_dom_tabs_lists_the_tabs(self):
        backend, session, _pointer = self._backend()
        backend.dom_start()
        tabs = backend.dom_tabs()
        self.assertEqual(tabs[0]['title'], 'Example')
        backend.close()

    def test_dom_observe_requires_a_scope(self):
        backend, _session, _pointer = self._backend()
        backend.dom_start()
        with self.assertRaisesRegex(zen_dom.ZenDomError, 'scope'):
            backend.dom_observe('Example', None, 10)
        backend.close()

    def test_dom_observe_binds_a_snapshot_to_scope_and_id(self):
        backend, _session, _pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        self.assertEqual(snapshot['title'], 'Example')
        self.assertEqual(snapshot['elements'][0]['ref'], '#c5-text')
        self.assertEqual(snapshot['elements'][0]['plan_rect'],
                         {'x': 100, 'y': 200, 'width': 200,
                          'height': 30})
        self.assertEqual(snapshot['window_bounds'],
                         [2509, 914, 925, 1176])
        backend.close()

    def test_dom_act_click_dispatches_on_the_fresh_screen_point(self):
        # Window origin [2509, 914] + verified moz [240, 8] = true
        # viewport origin [2749, 922] (MOZ-GROWTH pixel proof);
        # rect center (200, 215) gives [2949, 1137].
        backend, _session, pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'click', 'ref': '#c5-text', 'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(pointer.calls[0][1], [2949.0, 1137.0])
        backend.close()

    def test_dom_act_refuses_actions_missing_scope_or_observation_id(self):
        backend, _session, _pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        with self.assertRaisesRegex(zen_dom.ZenDomError, 'scope'):
            backend.dom_act('Example', snapshot['snapshot'],
                            [{'type': 'click', 'ref': '#c5-text',
                              'observation_id': snapshot['snapshot']}],
                            None, True)
        with self.assertRaisesRegex(zen_dom.ZenDomError,
                                    'observation_id'):
            backend.dom_act('Example', snapshot['snapshot'],
                            [{'type': 'click', 'ref': '#c5-text',
                              'scope': 'Example'}], None, True)
        backend.close()

    def test_dom_act_strict_send_stops_on_a_moved_rect(self):
        # The field moved between observe and act. The batch is a
        # send (fill + Enter), so ANY disagreement stops it: no
        # input is sent, the error is the section 7 shape.
        backend, session, pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        session.fields['#c5-text']['rect'] = {
            'x': 100, 'y': 300, 'width': 200, 'height': 30}
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'fill', 'ref': '#c5-text', 'text': 'hello',
              'scope': 'Example',
              'observation_id': snapshot['snapshot']},
             {'type': 'key', 'ref': '#c5-text', 'keys': ['Enter'],
              'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertFalse(result['ok'])
        self.assertFalse(pointer.calls)
        self.assertEqual(result['error']['code'], 'stale_ref')
        self.assertEqual(result['error']['reason'], 'rect_moved')
        self.assertTrue(result['error']['batch_stopped'])
        self.assertFalse(result['results'][0]['input_sent'])
        backend.close()

    def test_dom_act_nonstrict_move_re_grounds_once_and_acts(self):
        # The same move on a plain click (not strict) re-grounds
        # once and acts on the fresh rect: center (200, 315) gives
        # [2949, 1237] from the true origin [2749, 922].
        backend, session, pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        session.fields['#c5-text']['rect'] = {
            'x': 100, 'y': 300, 'width': 200, 'height': 30}
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'click', 'ref': '#c5-text', 'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(pointer.calls[0][1], [2949.0, 1237.0])
        self.assertEqual(
            result['results'][0]['re_ground']['live_rect'],
            {'x': 100, 'y': 300, 'width': 200, 'height': 30})
        backend.close()

    def test_dom_act_missing_element_refuses_with_no_input(self):
        backend, session, pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        del session.fields['#c5-text']
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'click', 'ref': '#c5-text', 'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertFalse(result['ok'])
        self.assertFalse(pointer.calls)
        self.assertEqual(result['error']['reason'], 'element_missing')
        self.assertIsNone(result['error']['live_rect'])
        backend.close()

    def test_dom_act_ambiguous_element_stops_without_picking_first(self):
        backend, session, pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        report = session.locate_confirmed('#c5-text')
        report['unique'] = False
        report['unique_count'] = 2
        session.locate_confirmed = lambda selector: report
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'click', 'ref': '#c5-text', 'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertFalse(result['ok'])
        self.assertFalse(pointer.calls)
        self.assertEqual(result['error']['reason'],
                         'element_ambiguous')
        backend.close()

    def test_dom_act_send_chain_verifies_with_dom_postconditions(self):
        backend, _session, _pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'fill', 'ref': '#c5-text', 'text': 'hello',
              'scope': 'Example',
              'observation_id': snapshot['snapshot']},
             {'type': 'key', 'ref': '#c5-text', 'keys': ['Enter'],
              'scope': 'Example',
              'observation_id': snapshot['snapshot'],
              'assert': {'type': 'sent_bubble', 'text': 'hello'}}],
            None, True)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['results'][0]['verified'])
        self.assertEqual(result['results'][0]['verified_basis'],
                         'dom-value')
        self.assertTrue(result['results'][1]['verified'])
        self.assertEqual(result['results'][1]['verified_basis'],
                         'sent-bubble')
        backend.close()

    def test_close_closes_the_session_in_finally_after_a_failure(self):
        backend, session, _pointer = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        del session.fields['#c5-text']
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [{'type': 'click', 'ref': '#c5-text', 'scope': 'Example',
              'observation_id': snapshot['snapshot']}], None, True)
        self.assertFalse(result['ok'])
        backend.close()
        self.assertTrue(session.exited)

    def test_code_exec_window_wait_uses_the_backend_class(self):
        # code_exec._wait_for_dom_window must match the Zen backend
        # by its DOM_WINDOW_CLASS, not only by class == 'chromium'.
        # The wait returns None on success (it raises on failure),
        # so the assertion is that it does not raise.
        backend, _session, _pointer = self._backend()
        self.assertEqual(backend.DOM_WINDOW_CLASS, 'zen')
        session = code_exec.CodeExecSession(backend)
        session._wait_for_dom_window()


class BackendRangeTests(unittest.TestCase):
    """The F5-source pin was vacuous by mutation: forcing
    type_ranges = [[0.0, 20.0]] unconditionally in
    CodeExecBackend.act still passed it, because it only asserted
    the string 'type_x_ranges' appears in the act source. This
    behavioural test replaces it: on the unwired path (no rect
    grounds) act must pass type_x_ranges=None to desktop_act, so
    an unconditional range fails the test."""
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(cu, 'check_cancel'))
        self.stack.enter_context(patch.object(cu.time, 'sleep'))
        self.stack.enter_context(patch.object(
            cu.shutil, 'which', return_value=None))
        self.stack.enter_context(patch.object(
            cu, 'fcitx5_running', return_value=False))
        self.stack.enter_context(patch.object(
            cu, 'window', return_value={'at': [0, 0], 'size': [20, 20]}))
        self.stack.enter_context(patch.object(
            cu, 'hypr',
            side_effect=lambda env, query: {
                'monitors': [dict(self.monitor)],
                'activewindow': {'address': 'fixture'},
                'cursorpos': {'x': 10, 'y': 10},
            }[query]))
        self.stack.enter_context(patch.object(
            cu, 'observe', side_effect=self._observe))
        self.stack.enter_context(patch(
            'PIL.Image.open', side_effect=self._image_open))
        self.pointer_cls = self.stack.enter_context(
            patch.object(cu, 'Pointer'))
        self.pointer = self.pointer_cls.return_value
        self.typed = self.stack.enter_context(patch.object(
            cu, 'run_cancelable', return_value=''))
        self.backend = cu.CodeExecBackend({})
        self.calls = []
        self.spy = self.stack.enter_context(patch.object(
            cu, 'desktop_act',
            side_effect=lambda *args, **kwargs: self.calls.append(
                (args, kwargs)) or {'ok': True, 'completed': 1}))

    def _observe(self, env, address, crop, max_width, **kwargs):
        if kwargs.get('persist', True):
            return dict(self.meta, pixel_sha256=self.after_pixel_sha256,
                        image='after.png')
        return self.image, self.meta.copy()

    def _image_open(self, path, *args, **kwargs):
        if str(path).endswith('after.png'):
            return self.after_image
        return self.image

    def setUp_meta(self, field_rect=None):
        from PIL import Image
        self.monitor = {'width': 20, 'height': 20, 'x': 0, 'y': 0,
                        'scale': 1.0}
        self.image = self.after_image = Image.new('RGB', (20, 20))
        self.after_pixel_sha256 = 'after'
        self.meta = {'id': 'fixture-observation', 'scope': 'window',
                     'window': 'fixture', 'window_bounds': [0, 0, 20, 20],
                     'image_size': [20, 20], 'region': [0, 0, 20, 20],
                     'image': 'after.png',
                     'observation_schema': cu.OBSERVATION_SCHEMA,
                     'capture_started_monotonic': time.monotonic(),
                     'capture_started_wall': time.time(),
                     'created': time.time(),
                     'capture_boot_id': cu.boot_identity()}
        self.field_rect = field_rect

    def test_unwired_path_supplies_no_ranges(self):
        # No DOM session grounds a rect, so act must pass
        # type_x_ranges=None (and type_y_ranges=None) through to
        # desktop_act. An unconditional [[0.0, 20.0]] fails here.
        self.setUp_meta()
        actions = [{'type': 'type', 'text': 'hello', 'scope': 'window',
                    'observation_id': 'fixture-observation'}]
        self.backend.act(self.meta, actions, None,
                         dom_selector='#msg-input')
        self.assertEqual(len(self.calls), 1)
        kwargs = self.calls[0][1]
        self.assertIsNone(kwargs['type_x_ranges'])
        self.assertIsNone(kwargs['type_y_ranges'])

    def test_wired_path_supplies_the_grounded_ranges(self):
        self.setUp_meta(field_rect={'x': 12, 'y': 8, 'width': 8,
                                    'height': 4})
        session = FakeDomSession(
            {'#msg-input': {'rect': self.field_rect}})
        actions = [{'type': 'type', 'text': 'hello', 'scope': 'window',
                    'observation_id': 'fixture-observation'}]
        self.backend.act(self.meta, actions, None, dom_session=session,
                         dom_selector='#msg-input')
        kwargs = self.calls[0][1]
        self.assertEqual(kwargs['type_x_ranges'], [[12.0, 20.0]])
        self.assertEqual(kwargs['type_y_ranges'], [[8.0, 12.0]])


class ScreenScopeLegalityTests(
        __import__('test_keyboard_preflight').DesktopPreflight):
    def _screen_meta(self):
        return dict(self.meta, scope='screen',
                    id='fixture-observation')

    def test_screen_scope_key_batch_is_no_longer_a_legality_refusal(self):
        # Protocol section 8: the legality refusal is deleted; the
        # check changes form into snapshot binding. A bound
        # screen-scope key/type batch proceeds to the session.
        meta = self._screen_meta()
        actions = [{'type': 'type', 'text': 'hello', 'scope': 'screen',
                    'observation_id': 'fixture-observation'},
                   {'type': 'key', 'keys': ['Enter'], 'scope': 'screen',
                    'observation_id': 'fixture-observation'}]
        # The harness patches observe() (window path) but not
        # observe_screen(): screen-scope batches never reached the
        # after-capture before this step, because the legality
        # refusal stopped them. Patch it the same way here:
        # persist=True returns the observation dict, persist=False
        # returns (image, meta).
        def _observe_screen(*args, **kwargs):
            if kwargs.get('persist', True):
                return dict(self.meta,
                            pixel_sha256=self.after_pixel_sha256,
                            image='after.png')
            return self.image, self.meta.copy()

        with patch.object(cu, 'observe_screen',
                          side_effect=_observe_screen):
            result = cu.desktop_act({}, meta, actions)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 2)

    def test_screen_scope_mismatched_observation_id_is_a_stale_refusal(self):
        meta = self._screen_meta()
        actions = [{'type': 'type', 'text': 'hello', 'scope': 'screen',
                    'observation_id': 'deadbeef0000'}]
        with self.assertRaisesRegex(cu.PreflightRefusal,
                                    'stale_ref: snapshot_unbound'):
            cu.desktop_act({}, meta, actions)

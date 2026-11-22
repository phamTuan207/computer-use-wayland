"""Zen pointer delegate (COORD-CLICK-5, step 9, item 5).

Failing-first tests for the step-9 prototype wiring: the Zen
backend refuses input with no_pointer_delegate until a delegate
is passed through; ZenPointerDelegate translates Zen DOM actions
plus their screen points into desktop actions and dispatches them
through a CodeExecBackend on one fresh window observation per
batch (focus first, then observe), stamping each desktop action
with that observation's scope + observation_id.

No live laptop work, no browser tasks, never ydotool. No em dash
or en dash anywhere. Run:
python3 -m unittest tests.test_zen_pointer
"""
import inspect
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import test_p2_element_ref as _p2
import zen_backend
import zen_dom
import zen_pointer


def _solid(color=(200, 200, 200), size=(64, 48)):
    return Image.new('RGB', size, color)


class FakeCodeBackend:
    """Stand-in for CodeExecBackend: observe_window returns a fresh
    window meta; act records the stamped desktop actions and
    simulates the desktop (a type lands in the field, a send key
    bubbles it).

    The meta mirrors the live run-4 window: bounds [2509, 914,
    925, 1176] on monitor [2464, 902, 1920, 1200], image 925x1176
    (no downscale at max_width 960). act validates point actions
    against the image frame the way the real desktop_act
    preflight does (cu.image_point refuses a point outside the
    image): a delegate that hands through a raw screen point is
    refused here, exactly as run 4 was refused live.

    Each observation writes a REAL JPEG (frames cycle per observe,
    default one solid frame, so the screen is stable and the F4
    settle converges on the second observe). The delegate's
    _mean_diff reads meta['image'], so the file must exist.
    """

    def __init__(self, session, act_ok=True, completed=None,
                 frames=None):
        self.session = session
        self.act_ok = act_ok
        self.completed = completed
        self.observe_calls = []
        self.act_calls = []
        self._n = 0
        self._tmp = tempfile.mkdtemp(prefix='zen-pointer-test-')
        self._frames = frames if frames is not None else [_solid()]

    def observe_window(self, address, crop, max_width):
        self.observe_calls.append((address, crop, max_width))
        self._n += 1
        frame = self._frames[(self._n - 1) % len(self._frames)]
        path = os.path.join(self._tmp, 'obs-%d.jpg' % self._n)
        frame.save(path, format='JPEG', quality=90, subsampling=0)
        return {'id': 'obs-%d' % self._n, 'scope': 'window',
                'window': address,
                'observation': '/tmp/obs-%d.json' % self._n,
                'image': path,
                'monitor_box': [2464, 902, 1920, 1200],
                'window_bounds': [2509, 914, 925, 1176],
                'region': [2509, 914, 925, 1176],
                'image_size': [925, 1176],
                'created': 0}

    def act(self, meta, actions, observation_path):
        self.act_calls.append((dict(meta), [dict(a) for a in actions],
                               observation_path))
        if not self.act_ok:
            return {'ok': False, 'completed': 0,
                    'error': 'desktop refused'}
        size = meta.get('image_size')
        for action in actions:
            if action['type'] in ('click', 'double_click', 'move',
                                  'hover', 'scroll'):
                x, y = action.get('x'), action.get('y')
                if (not isinstance(size, (list, tuple))
                        or len(size) != 2
                        or not (isinstance(x, (int, float))
                                and isinstance(y, (int, float))
                                and 0 <= x < size[0]
                                and 0 <= y < size[1])):
                    return {'ok': False, 'completed': 0,
                            'error': 'point outside observed image'}
        for action in actions:
            if action['type'] == 'type':
                for field in self.session.fields.values():
                    field['value'] = action.get('text', '')
            if (action['type'] == 'key'
                    and 'Enter' in (action.get('keys') or [])):
                for field in self.session.fields.values():
                    self.session.sent_bubbles.append(
                        field.get('value', ''))
        completed = (len(actions) if self.completed is None
                     else self.completed)
        return {'ok': True, 'completed': completed,
                'type_verified': True,
                'type_verified_basis': 'dom-value',
                'ime_state_trace': [
                    {'phase': 'before', 'state': '2',
                     'status': 'observed'},
                    {'phase': 'after_switch', 'state': '1',
                     'status': 'observed'},
                    {'phase': 'after_restore', 'state': '2',
                     'status': 'observed'}],
                'wtype_stderr': ''}


class DelegateUnitTests(unittest.TestCase):
    def _delegate(self, session=None, **kwargs):
        session = session if session is not None else \
            _p2.FakeZenSession(_p2._zen_fields())
        backend = FakeCodeBackend(session, **kwargs)
        focused = []
        delegate = zen_pointer.ZenPointerDelegate(
            backend, focus_fn=focused.append)
        return delegate, backend, focused, session

    def test_begin_batch_focuses_then_observes_once(self):
        # F4 settle: begin_batch focuses, observes, then re-observes
        # once to confirm the window is stable, so the batch meta is
        # the settled (second) observation, never a mid-transition
        # first frame.
        delegate, backend, focused, _session = self._delegate()
        meta = delegate.begin_batch('0xabc')
        self.assertEqual(focused, ['0xabc'])
        self.assertEqual(backend.observe_calls,
                         [('0xabc', None, 960), ('0xabc', None, 960)])
        self.assertEqual(meta['id'], 'obs-2')
        self.assertEqual(meta['scope'], 'window')
        self.assertEqual(delegate.last_settle['reads'], 2)
        self.assertTrue(delegate.last_settle['stable'])

    def test_begin_batch_refuses_without_a_window_address(self):
        delegate, _backend, _focused, _session = self._delegate()
        with self.assertRaises(ValueError):
            delegate.begin_batch(None)

    def test_begin_batch_refuses_a_meta_without_id(self):
        delegate, backend, _focused, _session = self._delegate()
        backend.observe_window = (
            lambda address, crop, max_width: {'scope': 'window'})
        with self.assertRaises(ValueError):
            delegate.begin_batch('0xabc')

    def test_click_maps_and_stamps(self):
        # Screen point (2700, 1000) inside the run-4 window region
        # converts to image point (191, 86); the desktop click
        # carries the image point, never the raw screen point.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))
        self.assertEqual(len(backend.act_calls), 1)
        meta, actions, path = backend.act_calls[0]
        self.assertEqual(path, '/tmp/obs-2.json')
        self.assertEqual(actions, [{'type': 'click', 'x': 191.0,
                                    'y': 86.0, 'scope': 'window',
                                    'observation_id': 'obs-2'}])

    def test_run4_screen_point_converts_to_image_point(self):
        # F3 regression: the exact run-4 screen point for the
        # #msg-input center (2939, 1168.87) must reach the desktop
        # as the image point (430, 254.87) against the 925x1176
        # window image. The old code passed (2939, 1168) through
        # and the desktop preflight refused it with 'point outside
        # observed image'.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'click', 'ref': '#c5-text'},
            [2939.0, 1168.86666870117188]))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual((actions[0]['x'], actions[0]['y']),
                         (430.0, 254.86666870117188))

    def test_point_outside_window_image_returns_false(self):
        # A screen point outside the batch observation region
        # (100, 200) is left of the window at x 2509: the delegate
        # refuses it without dispatching, instead of handing a
        # point the desktop preflight would reject.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [100, 200]))
        self.assertEqual(backend.act_calls, [])

    def test_meta_without_image_frame_returns_false(self):
        # A batch meta with an id and scope but no image frame
        # cannot convert the point: fail closed, no dispatch.
        delegate, backend, _focused, _session = self._delegate()
        backend.observe_window = (
            lambda address, crop, max_width: {
                'id': 'obs-x', 'scope': 'window',
                'observation': '/tmp/obs-x.json'})
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))
        self.assertEqual(backend.act_calls, [])

    def test_fill_maps_to_click_plus_type(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [2700, 1000]))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions, [
            {'type': 'click', 'x': 191.0, 'y': 86.0, 'scope': 'window',
             'observation_id': 'obs-2'},
            {'type': 'type', 'text': 'hello', 'scope': 'window',
             'observation_id': 'obs-2'}])

    def test_key_needs_no_point(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'key', 'keys': ['Enter']}, None))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions, [{'type': 'key', 'keys': ['Enter'],
                                    'scope': 'window',
                                    'observation_id': 'obs-2'}])

    def test_focus_maps_to_click(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'focus', 'ref': '#c5-text'}, [2700, 1000]))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions[0]['type'], 'click')
        self.assertEqual((actions[0]['x'], actions[0]['y']),
                         (191.0, 86.0))

    def test_drag_refuses(self):
        # A drag needs from/to; a single point cannot express it.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'drag', 'ref': '#c5-text'}, [2700, 1000]))
        self.assertEqual(backend.act_calls, [])

    def test_no_meta_returns_false(self):
        delegate, backend, _focused, _session = self._delegate()
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))
        self.assertEqual(backend.act_calls, [])

    def test_failed_act_returns_false(self):
        delegate, _backend, _focused, _session = self._delegate(
            act_ok=False)
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))

    def test_completed_mismatch_returns_false(self):
        delegate, _backend, _focused, _session = self._delegate(
            completed=1)
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [2700, 1000]))

    def test_second_batch_reobserves(self):
        # One settled observation per batch: the second batch
        # observes again (focus + observe + settle confirmation)
        # and stamps with the fresh id, never the stale one.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        delegate({'type': 'click', 'ref': '#c5-text'}, [2700, 1000])
        delegate.begin_batch('0xabc')
        delegate({'type': 'click', 'ref': '#c5-text'}, [2700, 1000])
        self.assertEqual(len(backend.observe_calls), 4)
        self.assertEqual(backend.act_calls[1][1][0]['observation_id'],
                         'obs-4')


class SettleTests(unittest.TestCase):
    """F4: begin_batch must settle the observation before using it
    as the batch meta, or desktop_act's preflight refuses the batch
    as 'screen changed' (the meta was a mid-transition frame)."""

    def _delegate_with_frames(self, frames, **kwargs):
        session = _p2.FakeZenSession(_p2._zen_fields())
        backend = FakeCodeBackend(session, frames=frames, **kwargs)
        focused = []
        delegate = zen_pointer.ZenPointerDelegate(
            backend, focus_fn=focused.append)
        return delegate, backend, focused, session

    def test_mean_diff_identical_is_zero_and_changed_is_large(self):
        # The settle comparator: identical frames compare ~0, a
        # light-vs-dark frame compares ~180 (far above the 0.5
        # threshold, far below nothing: it must trip the settle).
        delegate, _b, _f, _s = self._delegate_with_frames(None)
        same_a = {'image': _b._tmp + '/a.jpg'}
        same_b = {'image': _b._tmp + '/b.jpg'}
        _solid((200, 200, 200)).save(same_a['image'], format='JPEG',
                                      quality=90, subsampling=0)
        _solid((200, 200, 200)).save(same_b['image'], format='JPEG',
                                      quality=90, subsampling=0)
        self.assertLess(delegate._mean_diff(same_a, same_b), 0.5)
        dark = {'image': _b._tmp + '/c.jpg'}
        _solid((20, 20, 20)).save(dark['image'], format='JPEG',
                                   quality=90, subsampling=0)
        self.assertGreater(delegate._mean_diff(same_a, dark), 100)
        self.assertEqual(delegate._mean_diff(
            {'image': '/tmp/does-not-exist.jpg'}, same_a), float('inf'))

    def test_settle_stable_screen_reads_twice_and_is_stable(self):
        delegate, backend, _f, _s = self._delegate_with_frames(None)
        meta = delegate.begin_batch('0xabc')
        self.assertEqual(meta['id'], 'obs-2')
        self.assertEqual(len(backend.observe_calls), 2)
        self.assertEqual(delegate.last_settle['reads'], 2)
        self.assertTrue(delegate.last_settle['stable'])

    def test_settle_transient_then_stable_uses_the_stable_frame(self):
        # Frames: light, dark, dark. The first pair disagrees
        # (transient), the second pair agrees: the batch meta is
        # the third (stable) observation, not the transient first.
        frames = [_solid((200, 200, 200)), _solid((20, 20, 20)),
                  _solid((20, 20, 20))]
        delegate, backend, _f, _s = self._delegate_with_frames(frames)
        meta = delegate.begin_batch('0xabc')
        self.assertEqual(meta['id'], 'obs-3')
        self.assertEqual(len(backend.observe_calls), 3)
        self.assertEqual(delegate.last_settle['reads'], 3)
        self.assertTrue(delegate.last_settle['stable'])

    def test_settle_never_stable_returns_latest_within_budget(self):
        # Alternating frames never agree: the settle expires on
        # budget, returns the latest meta, and reports stable
        # False, so the preflight stays the gatekeeper. Budget
        # and poll are patched small so the test stays fast.
        old_budget = zen_pointer.SETTLE_BUDGET_S
        old_poll = zen_pointer.SETTLE_POLL_S
        zen_pointer.SETTLE_BUDGET_S = 0.25
        zen_pointer.SETTLE_POLL_S = 0.05
        self.addCleanup(setattr, zen_pointer, 'SETTLE_BUDGET_S',
                        old_budget)
        self.addCleanup(setattr, zen_pointer, 'SETTLE_POLL_S', old_poll)
        frames = [_solid((200, 200, 200)), _solid((20, 20, 20))]
        delegate, backend, _f, _s = self._delegate_with_frames(frames)
        meta = delegate.begin_batch('0xabc')
        self.assertFalse(delegate.last_settle['stable'])
        self.assertGreaterEqual(delegate.last_settle['reads'], 3)
        self.assertEqual(meta['id'],
                         'obs-%d' % len(backend.observe_calls))

    def test_settle_recorded_on_dom_act_result(self):
        # The backend surfaces the settle outcome top-level on the
        # dom_act result, so a run's evidence says whether the
        # batch started on a stable frame.
        backend, session, code, _focused = BackendWiringTests()._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [BackendWiringTests()._action(snapshot['snapshot'])],
            None, True)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['settle']['stable'])
        self.assertEqual(result['settle']['reads'], 2)
        backend.close()

    def test_last_dispatch_carries_ime_trace(self):
        # The delegate surfaces the desktop_act IME trace on
        # last_dispatch, so a doubled or mangled typed value can
        # be traced to the input-method state around the type.
        delegate, backend, _focused, _session = \
            self._delegate_with_frames(None)
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [2700, 1000]))
        trace = delegate.last_dispatch.get('ime_state_trace')
        self.assertEqual(
            [t['phase'] for t in trace],
            ['before', 'after_switch', 'after_restore'])
        self.assertEqual(trace[0]['state'], '2')
        self.assertEqual(trace[1]['state'], '1')
        self.assertEqual(delegate.last_dispatch.get('wtype_stderr'), '')

    def test_meta_refreshes_after_a_type(self):
        # F4 follow-up: a type changes the screen (the text now
        # shows in the field), so the batch meta is stale for the
        # NEXT action's desktop_act preflight, which would refuse
        # it as 'screen changed' (f4diag run 8: set_value verified,
        # then the focus was refused). After a successful type the
        # delegate re-observes (and settles) so the next dispatch
        # uses a fresh meta. A click-only dispatch does not refresh.
        delegate, backend, _focused, _session = \
            self._delegate_with_frames(None)
        delegate.begin_batch('0xabc')
        # begin_batch settles: 2 observes, meta obs-2.
        self.assertEqual(len(backend.observe_calls), 2)
        self.assertEqual(delegate._meta['id'], 'obs-2')
        # A click does not refresh the meta.
        self.assertTrue(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))
        self.assertEqual(len(backend.observe_calls), 2)
        self.assertEqual(delegate._meta['id'], 'obs-2')
        # A fill (click + type) refreshes it: one more observe for
        # the refresh plus its settle confirmation.
        self.assertTrue(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [2700, 1000]))
        self.assertEqual(len(backend.observe_calls), 4)
        self.assertEqual(delegate._meta['id'], 'obs-4')
        self.assertTrue(delegate.last_settle['stable'])
        # The next dispatch stamps with the fresh meta id.
        self.assertTrue(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [2700, 1000]))
        _meta, actions, _path = backend.act_calls[-1]
        self.assertEqual(actions[0]['observation_id'], 'obs-4')


class BackendWiringTests(unittest.TestCase):
    def _backend(self):
        session = _p2.FakeZenSession(_p2._zen_fields())
        backend = zen_backend.ZenDomBackend(
            session_factory=lambda: session,
            windows_fn=_p2._zen_windows,
            pointer=None)
        code = FakeCodeBackend(session)
        focused = []
        delegate = zen_pointer.ZenPointerDelegate(
            code, focus_fn=focused.append)
        backend.set_pointer(delegate)
        return backend, session, code, focused

    def _action(self, snapshot_id, **overrides):
        action = {'type': 'click', 'ref': '#c5-text',
                  'scope': 'Example',
                  'observation_id': snapshot_id}
        action.update(overrides)
        return action

    def test_backend_dispatches_a_click_through_the_delegate(self):
        backend, _session, code, focused = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'])], None, True)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['results'][0]['input_sent'])
        # Focus first, then one observation for the batch.
        self.assertEqual(focused, ['0x557052b62dd0'])
        self.assertEqual(len(code.observe_calls), 2)
        # The field rect center (200, 215) in the viewport plus the
        # verified origin (2749, 922) is the screen point
        # (2949, 1137); the delegate converts it to the IMAGE
        # point (440, 223) against the batch window observation
        # (region origin (2509, 914), image 925x1176). The raw
        # screen point must never reach the desktop act: run 4
        # was refused live for exactly that (F3).
        _meta, actions, _path = code.act_calls[0]
        self.assertEqual((actions[0]['x'], actions[0]['y']),
                         (440.0, 223.0))
        backend.close()

    def test_backend_send_shape_through_the_delegate(self):
        # The landed (b1) program through the delegate: set_value,
        # focus, CDP Enter, trailing bubble assert. The fake desktop
        # types into the field and bubbles it, so the backend's
        # DOM postconditions (dom-value, sent-bubble) verify.
        backend, session, code, _focused = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        snap_id = snapshot['snapshot']
        program = [
            self._action(snap_id, type='set_value', text='hello'),
            self._action(snap_id, type='focus'),
            self._action(snap_id, type='key', keys=['Enter']),
            self._action(snap_id, type='assert', text='hello'),
        ]
        result = backend.dom_act('Example', snap_id, program, None, True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 4)
        self.assertEqual(session.fields['#c5-text']['value'], 'hello')
        self.assertEqual(session.sent_bubbles, ['hello'])
        # One settled observation for the batch start, plus one
        # refresh after the set_value type (the typed text changes
        # the screen, so the next dispatch needs a fresh meta);
        # three dispatches (the trailing assert reads state and
        # dispatches nothing).
        self.assertEqual(len(code.observe_calls), 4)
        self.assertEqual(len(code.act_calls), 3)
        # The set_value click is the image point (440, 223), not
        # the raw screen point (2949, 1137): with the old
        # pass-through the fake desktop preflight refuses the
        # click and the program fails.
        _meta, actions, _path = code.act_calls[0]
        self.assertEqual((actions[0]['x'], actions[0]['y']),
                         (440.0, 223.0))
        backend.close()

    def test_assert_only_batch_does_not_observe(self):
        # A read-only batch must not focus or observe: no input is
        # dispatched, so no fresh observation is needed.
        backend, _session, code, focused = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        result = backend.dom_act(
            'Example', snapshot['snapshot'],
            [self._action(snapshot['snapshot'], type='assert',
                          text='')], None, True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(focused, [])
        self.assertEqual(code.observe_calls, [])
        backend.close()


class RealShapeFakeSession(_p2.FakeZenSession):
    """Fake session with the REAL sent_bubble_contains signature.

    The real ZenSession takes one argument, the text
    (zen_dom.py:1296). The old fake took two (selector, text),
    which matched the backend call instead of the real session
    and let the arity mismatch ship with green tests (W-ZENPREP
    finding B). This fake is the regression guard for that.
    """

    def sent_bubble_contains(self, text):
        return text in self.sent_bubbles


class RealSignatureTests(unittest.TestCase):
    """W-ZENPREP finding B: the backend must call
    sent_bubble_contains the way the real session defines it."""

    def _backend(self):
        session = RealShapeFakeSession(_p2._zen_fields())
        backend = zen_backend.ZenDomBackend(
            session_factory=lambda: session,
            windows_fn=_p2._zen_windows,
            pointer=None)
        code = FakeCodeBackend(session)
        focused = []
        delegate = zen_pointer.ZenPointerDelegate(
            code, focus_fn=focused.append)
        backend.set_pointer(delegate)
        return backend, session, code, focused

    def _action(self, snapshot_id, **overrides):
        action = {'type': 'click', 'ref': '#c5-text',
                  'scope': 'Example',
                  'observation_id': snapshot_id}
        action.update(overrides)
        return action

    def test_real_session_signature_is_one_argument(self):
        params = list(inspect.signature(
            zen_dom.ZenSession.sent_bubble_contains).parameters)
        self.assertEqual(params, ['self', 'text'])
        fake_params = list(inspect.signature(
            RealShapeFakeSession.sent_bubble_contains).parameters)
        self.assertEqual(fake_params, ['self', 'text'])

    def test_b1_program_completes_through_the_real_shape_session(self):
        # The landed (b1) program through the delegate, with the
        # session shaped like the real one. Pre-fix this raises
        # TypeError in _verify at the send key, because the backend
        # called sent_bubble_contains with two arguments.
        backend, session, code, _focused = self._backend()
        backend.dom_start()
        snapshot = backend.dom_observe('Example', '#c5-text', 10)
        snap_id = snapshot['snapshot']
        program = [
            self._action(snap_id, type='set_value', text='hello'),
            self._action(snap_id, type='focus'),
            self._action(snap_id, type='key', keys=['Enter']),
            self._action(snap_id, type='assert', text='hello'),
        ]
        result = backend.dom_act('Example', snap_id, program, None, True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 4)
        self.assertEqual(session.fields['#c5-text']['value'], 'hello')
        self.assertEqual(session.sent_bubbles, ['hello'])
        # 2 observes for the begin_batch settle, 2 more for the
        # post-type refresh after the set_value.
        self.assertEqual(len(code.observe_calls), 4)
        self.assertEqual(len(code.act_calls), 3)
        backend.close()


if __name__ == '__main__':
    unittest.main()

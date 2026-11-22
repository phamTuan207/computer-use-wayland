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
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import test_p2_element_ref as _p2
import zen_backend
import zen_pointer


class FakeCodeBackend:
    """Stand-in for CodeExecBackend: observe_window returns a fresh
    window meta; act records the stamped desktop actions and
    simulates the desktop (a type lands in the field, a send key
    bubbles it)."""

    def __init__(self, session, act_ok=True, completed=None):
        self.session = session
        self.act_ok = act_ok
        self.completed = completed
        self.observe_calls = []
        self.act_calls = []
        self._n = 0

    def observe_window(self, address, crop, max_width):
        self.observe_calls.append((address, crop, max_width))
        self._n += 1
        return {'id': 'obs-%d' % self._n, 'scope': 'window',
                'window': address,
                'observation': '/tmp/obs-%d.json' % self._n,
                'image': '/tmp/obs-%d.jpg' % self._n,
                'monitor_box': [0, 0, 1920, 1200], 'created': 0}

    def act(self, meta, actions, observation_path):
        self.act_calls.append((dict(meta), [dict(a) for a in actions],
                               observation_path))
        if not self.act_ok:
            return {'ok': False, 'completed': 0,
                    'error': 'desktop refused'}
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
        return {'ok': True, 'completed': completed}


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
        delegate, backend, focused, _session = self._delegate()
        meta = delegate.begin_batch('0xabc')
        self.assertEqual(focused, ['0xabc'])
        self.assertEqual(backend.observe_calls,
                         [('0xabc', None, 960)])
        self.assertEqual(meta['id'], 'obs-1')
        self.assertEqual(meta['scope'], 'window')

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
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [100, 200]))
        self.assertEqual(len(backend.act_calls), 1)
        meta, actions, path = backend.act_calls[0]
        self.assertEqual(path, '/tmp/obs-1.json')
        self.assertEqual(actions, [{'type': 'click', 'x': 100, 'y': 200,
                                    'scope': 'window',
                                    'observation_id': 'obs-1'}])

    def test_fill_maps_to_click_plus_type(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [100, 200]))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions, [
            {'type': 'click', 'x': 100, 'y': 200, 'scope': 'window',
             'observation_id': 'obs-1'},
            {'type': 'type', 'text': 'hello', 'scope': 'window',
             'observation_id': 'obs-1'}])

    def test_key_needs_no_point(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'key', 'keys': ['Enter']}, None))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions, [{'type': 'key', 'keys': ['Enter'],
                                    'scope': 'window',
                                    'observation_id': 'obs-1'}])

    def test_focus_maps_to_click(self):
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertTrue(delegate(
            {'type': 'focus', 'ref': '#c5-text'}, [100, 200]))
        _meta, actions, _path = backend.act_calls[0]
        self.assertEqual(actions[0]['type'], 'click')

    def test_drag_refuses(self):
        # A drag needs from/to; a single point cannot express it.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'drag', 'ref': '#c5-text'}, [100, 200]))
        self.assertEqual(backend.act_calls, [])

    def test_no_meta_returns_false(self):
        delegate, backend, _focused, _session = self._delegate()
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [100, 200]))
        self.assertEqual(backend.act_calls, [])

    def test_failed_act_returns_false(self):
        delegate, _backend, _focused, _session = self._delegate(
            act_ok=False)
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'click', 'ref': '#c5-text'}, [100, 200]))

    def test_completed_mismatch_returns_false(self):
        delegate, _backend, _focused, _session = self._delegate(
            completed=1)
        delegate.begin_batch('0xabc')
        self.assertFalse(delegate(
            {'type': 'fill', 'ref': '#c5-text', 'text': 'hello'},
            [100, 200]))

    def test_second_batch_reobserves(self):
        # One observation per batch: the second batch observes
        # again and stamps with the fresh id, never the stale one.
        delegate, backend, _focused, _session = self._delegate()
        delegate.begin_batch('0xabc')
        delegate({'type': 'click', 'ref': '#c5-text'}, [100, 200])
        delegate.begin_batch('0xabc')
        delegate({'type': 'click', 'ref': '#c5-text'}, [100, 200])
        self.assertEqual(len(backend.observe_calls), 2)
        self.assertEqual(backend.act_calls[1][1][0]['observation_id'],
                         'obs-2')


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
        self.assertEqual(len(code.observe_calls), 1)
        # The field rect center (200, 215) in the viewport plus the
        # verified origin (2749, 922) is the screen point.
        _meta, actions, _path = code.act_calls[0]
        self.assertEqual((actions[0]['x'], actions[0]['y']),
                         (2949, 1137))
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
        # One observation for the whole batch; three dispatches
        # (the trailing assert reads state and dispatches nothing).
        self.assertEqual(len(code.observe_calls), 1)
        self.assertEqual(len(code.act_calls), 3)
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


if __name__ == '__main__':
    unittest.main()

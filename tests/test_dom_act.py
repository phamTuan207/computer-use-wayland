"""DOM-first focus+type flow (item 12, replaced by the 02:00 correction).

Tests the dom_act orchestrator against scripted DOM sessions and a
fake act function that mirrors the cu.desktop_act hook protocol: the
focus_check closure runs before the first type group, the type_check
closure runs after the batch. No observe is taken anywhere in this
flow; the DOM calls are cheap JS evals. No ydotool, no live desktop.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu
import dom_act
import fastpath


class FakeDomSession:
    """Scripted DOM session: one field per selector, origin fixed."""

    def __init__(self, fields, origin=None):
        self.fields = fields
        self.origin = origin or [2533, 914]
        self.dom_calls = 0

    def locate(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        return None if field is None else field['rect']

    def viewport_origin(self):
        self.dom_calls += 1
        return list(self.origin)

    def hit_check(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        return bool(field) and not field.get('covered', False)

    def focus_check(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        if field is None:
            return False
        if field.get('focus_raises'):
            raise RuntimeError('activeElement read failed')
        return bool(field.get('focused', False))

    def field_value(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        return None if field is None else field.get('value')

    def verify_typed(self, selector, expected):
        self.dom_calls += 1
        field = self.fields.get(selector)
        return bool(field) and field.get('value') == expected


class FakeAct:
    """Mirrors the desktop_act hook protocol, without any observe.

    Calls focus_check before the first type action and type_check
    after the batch, catching a raising check the way _run_check
    does (fail closed). Records what was typed and what ran.
    """

    def __init__(self):
        self.typed = []
        self.executed = []
        self.calls = 0
        self.observes = 0

    def __call__(self, meta, actions, focus_check=None, type_check=None,
                 **kw):
        self.calls += 1
        completed = 0
        focus_done = False
        for act in actions:
            if act.get('type') == 'type' and not focus_done:
                focus_done = True
                if focus_check is not None:
                    try:
                        ok, _reason = focus_check()
                    except Exception:
                        ok = False
                    if not ok:
                        return {'ok': False, 'completed': completed,
                                'error': 'focus check failed',
                                'error_code': 'focus_unverified',
                                'focus_verified': False,
                                'observes': self.observes}
            if act.get('type') == 'type':
                self.typed.append(act['text'])
            self.executed.append(act)
            completed += 1
        if type_check is not None:
            try:
                ok, _reason = type_check()
            except Exception:
                ok = False
            if not ok:
                return {'ok': False, 'completed': completed,
                        'error': 'type verification failed',
                        'error_code': 'type_unverified',
                        'type_verified': False,
                        'observes': self.observes}
        return {'ok': True, 'completed': completed,
                'focus_verified': True, 'type_verified': True,
                'type_verified_basis': 'dom-value',
                'observes': self.observes}


G30_META = {'image_size': [901, 1176],
            'region': [2533, 914, 901, 1176]}
G30_FIELD = {'rect': {'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             'focused': True, 'value': 'hello', 'covered': False}


class GroundInputTests(unittest.TestCase):
    def test_ground_input_returns_rect_center_point(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META, '#msg-input')
        self.assertEqual(ground['point'], [306.0, 1132.5])
        self.assertEqual(ground['viewport_origin'], [2533, 914])
        self.assertTrue(ground['hit'])
        self.assertEqual(session.dom_calls, 3,
                         'locate + viewport_origin + hit_check only')

    def test_ground_input_covered_refuses_before_any_click(self):
        covered = dict(G30_FIELD, covered=True)
        session = FakeDomSession({'#msg-input': covered})
        act = FakeAct()
        with self.assertRaises(dom_act.DomActError) as caught:
            dom_act.ground_input(session, G30_META, '#msg-input')
        self.assertIn('covered', str(caught.exception))
        self.assertEqual(act.calls, 0, 'no act call, no click at all')

    def test_ground_input_missing_element_raises(self):
        session = FakeDomSession({})
        with self.assertRaises(dom_act.DomActError):
            dom_act.ground_input(session, G30_META, '#nope')

    def test_ground_many_two_inputs_one_observation(self):
        # The 2-vision benchmark shape: VISION 1 grounds BOTH clone
        # input bars; the script then runs with no more vision.
        fields = {
            '#clone1-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                       'height': 63},
                              'focused': True, 'value': None,
                              'covered': False},
            '#clone2-input': {'rect': {'x': 86, 'y': 1000, 'width': 440,
                                       'height': 63},
                              'focused': True, 'value': None,
                              'covered': False},
        }
        session = FakeDomSession(fields)
        points = dom_act.ground_many(session, G30_META,
                                     ['#clone1-input', '#clone2-input'])
        self.assertEqual(points['#clone1-input']['point'], [306.0, 1132.5])
        self.assertEqual(points['#clone2-input']['point'], [306.0, 1031.5])
        self.assertEqual(session.dom_calls, 6,
                         'two inputs, three cheap DOM calls each, '
                         'zero observes')

    def test_grounding_accuracy_across_cases(self):
        # Same 7 shapes as the fastpath suite, driven through the
        # orchestrator: accuracy is hits / cases, bar is >= 90%.
        cases = [
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [2533, 914],
             {'image_size': [901, 1176], 'region': [2533, 914, 901, 1176]}),
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [2533, 914],
             {'image_size': [450, 588], 'region': [2533, 914, 901, 1176]}),
            ({'x': 100, 'y': 5, 'width': 200, 'height': 30},
             [100, 200],
             {'image_size': [800, 600], 'region': [100, 200, 800, 600]}),
            ({'x': 400, 'y': 300, 'width': 8, 'height': 8},
             [0, 0],
             {'image_size': [800, 600], 'region': [0, 0, 800, 600]}),
            ({'x': 0, 'y': 500, 'width': 800, 'height': 40},
             [50, 60],
             {'image_size': [900, 700], 'region': [50, 60, 900, 700]}),
            ({'x': 86, 'y': 1001, 'width': 440, 'height': 63},
             [2533, 1014],
             {'image_size': [901, 1176], 'region': [2533, 914, 901, 1176]}),
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [2533, 914],
             {'image_size': [1802, 2352], 'region': [2533, 914, 901, 1176]}),
        ]
        hits = 0
        for rect, origin, meta in cases:
            field = {'rect': rect, 'focused': True, 'value': None,
                     'covered': False}
            session = FakeDomSession({'#f': field}, origin=origin)
            ground = dom_act.ground_input(session, meta, '#f')
            sx, sy = cu.image_point(meta, ground['point'][0],
                                    ground['point'][1])
            truth = {'x': origin[0] + rect['x'],
                     'y': origin[1] + rect['y'],
                     'width': rect['width'], 'height': rect['height']}
            hits += 1 if fastpath.point_in_rect(truth, sx, sy) else 0
        accuracy = hits / len(cases)
        self.assertGreaterEqual(accuracy, 0.9,
                                'accuracy %s (%d/%d) below the 90%% bar'
                                % (accuracy, hits, len(cases)))
        self.assertEqual(hits, len(cases))


class FocusTypeTests(unittest.TestCase):
    def test_happy_path_click_type_enter_from_one_observation(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        act = FakeAct()
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 3)
        self.assertEqual(result['point'], [306.0, 1132.5])
        self.assertTrue(result['focus_verified'])
        self.assertTrue(result['type_verified'])
        self.assertEqual(result['type_verified_basis'], 'dom-value')
        self.assertEqual(result['dom_calls'], 5,
                         '3 grounding + 1 focus + 1 type, all cheap')
        self.assertEqual(result['observes_added'], 0)
        self.assertEqual(result['act_observes'], 0)
        self.assertEqual(act.typed, ['hello'])
        self.assertEqual([a['type'] for a in act.executed],
                         ['click', 'type', 'key'])

    def test_click_miss_never_types(self):
        missed = dict(G30_FIELD, focused=False)
        session = FakeDomSession({'#msg-input': missed})
        act = FakeAct()
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'focus_unverified')
        self.assertEqual(result['completed'], 1, 'click only, no type')
        self.assertEqual(act.typed, [], 'no keystroke was sent blind')
        self.assertEqual(result['dom_calls'], 4,
                         'grounding 3 + focus 1, type check never ran')

    def test_type_unverified_after_typing(self):
        # The click focused the input and the text was typed, but the
        # field value does not hold it: the batch fails loudly.
        wrong = dict(G30_FIELD, value='goodbye')
        session = FakeDomSession({'#msg-input': wrong})
        act = FakeAct()
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertEqual(act.typed, ['hello'])
        self.assertEqual(result['completed'], 2)
        self.assertFalse(result['type_verified'])

    def test_without_enter_completes_two_actions(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        act = FakeAct()
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=False)
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 2)
        self.assertEqual([a['type'] for a in act.executed],
                         ['click', 'type'])

    def test_focus_check_exception_fails_closed(self):
        broken = dict(G30_FIELD, focus_raises=True)
        session = FakeDomSession({'#msg-input': broken})
        act = FakeAct()
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello')
        self.assertFalse(result['ok'])
        self.assertEqual(act.typed, [],
                         'a raising focus check types nothing')


if __name__ == '__main__':
    unittest.main(verbosity=2)

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
    """Scripted DOM session: one field per selector, origin fixed.

    origin is the WINDOW-relative mozInner pair (live C12 probe
    2026-11-22 03:36: mozInnerScreen is window-relative in this Zen
    build), so the default is [0, 0]: the absolute viewport origin
    is the meta's window origin plus this pair. viewport_origin()
    takes the Hyprland window origin the way the real ZenSession
    does. The session also models the V11 typed-event flag
    (trusted input events only, via an explicit note_typed from the
    act) and the one-shot harvest, so the orchestrator's strict rules
    are testable here.
    """

    _MISSING = object()

    def __init__(self, fields, origin=None):
        self.fields = fields
        self.origin = origin or [0, 0]
        self.dom_calls = 0
        self.sent_intents = set()
        self._armed = {}
        self._typed = {}

    def locate(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        return None if field is None else field['rect']

    def viewport_origin(self, window_origin=None, window_size=None,
                        monitor_box=None):
        self.dom_calls += 1
        if window_origin is None:
            return list(self.origin)
        return [window_origin[0] + self.origin[0],
                window_origin[1] + self.origin[1]]

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

    def verify_typed(self, selector, expected, before=None):
        self.dom_calls += 1
        field = self.fields.get(selector)
        if not field:
            return False
        value = field.get('value')
        if field.get('contenteditable'):
            if isinstance(value, str):
                value = value.rstrip()
            if isinstance(expected, str):
                expected = expected.rstrip()
            if isinstance(before, str):
                before = before.rstrip()
        if value != expected:
            return False
        if before is not None and not self.typed_flag(selector):
            return False
        return True

    def arm_typed_flag(self, selector):
        self.dom_calls += 1
        field = self.fields.get(selector)
        self._armed[selector] = None if field is None \
            else field.get('value')
        self._typed[selector] = False
        return field is not None

    def note_typed(self, selector):
        self._typed[selector] = True

    def typed_flag(self, selector):
        # Faithful model of the real V11 flag: True only when a
        # trusted input event was recorded (note_typed from the act).
        # A bare value change with no trusted event (a page script
        # setting el.value) leaves the flag clear, exactly like the
        # real window.__agentCuTyped flag. An earlier shape treated
        # any value change since arming as typed, which made the fake
        # blind to the R10 JS-set attack.
        self.dom_calls += 1
        return bool(self._typed.get(selector))

    def harvest(self, selectors):
        self.dom_calls += 1
        items = {}
        for selector in selectors:
            field = self.fields.get(selector)
            if field is None:
                items[selector] = None
                continue
            rect = field['rect']
            items[selector] = {
                'rect': {'x': rect['x'], 'y': rect['y'],
                         'width': rect['width'], 'height': rect['height'],
                         'center_x': rect['x'] + rect['width'] / 2,
                         'center_y': rect['y'] + rect['height'] / 2},
                'hit': not field.get('covered', False),
                'focused': bool(field.get('focused', False))}
        return {'moz_inner': list(self.origin),
                'device_pixel_ratio': 1,
                'screen_pixels_per_css_pixel': 1,
                'zoom': 1,
                'inner_size': [901, 1176],
                'outer_size': [901, 1176],
                'items': items}


class FakeAct:
    """Mirrors the desktop_act hook protocol, without any observe.

    Calls focus_check before the first type action and type_check
    after the batch, catching a raising check the way _run_check
    does (fail closed). Records what was typed and what ran. When a
    session is given, a type action really sets the field value
    (unless the field sets type_sticks False, modelling keystrokes
    the field never receives) and notes the typed event on the
    session, so the V11 flag sees real keystrokes.
    """

    def __init__(self, session=None):
        self.session = session
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
                if self.session is not None:
                    for selector, field in self.session.fields.items():
                        if field.get('type_sticks', True):
                            field['value'] = act['text']
                        if hasattr(self.session, 'note_typed'):
                            self.session.note_typed(selector)
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
    def test_ground_input_refuses_screen_region_without_window_bounds(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        meta = {'scope': 'screen', 'image_size': [1920, 1080],
                'region': [0, 0, 3840, 2160],
                'monitor_box': [0, 0, 3840, 2160]}
        with self.assertRaisesRegex(dom_act.DomActError,
                                    'requires window_bounds'):
            dom_act.ground_input(session, meta, '#msg-input')

    def test_ground_input_returns_rect_center_point(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        ground = dom_act.ground_input(session, G30_META, '#msg-input')
        self.assertEqual(ground['point'], [306.0, 1132.5])
        self.assertEqual(ground['viewport_origin'], [2533, 914])
        self.assertTrue(ground['hit'])
        self.assertEqual(session.dom_calls, 4,
                         'locate + viewport_origin + hit_check + '
                         're-locate (HCU live guard) only')

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
        self.assertEqual(session.dom_calls, 3,
                         'one harvest evaluate + one re-locate per '
                         'GroundPoints read, zero observes')

    def test_grounding_map_accuracy_across_cases(self):
        # Map accuracy, NOT grounding accuracy: these fixtures feed
        # TRUE viewport-relative inputs (a DOM rect, the
        # window-relative mozInner pair, and the window origin from
        # the meta) and check the linear map lands the screen point
        # inside the element's screen rect. They prove the map, not
        # the live conversion: the conversion itself (mozInner is
        # window-relative) is proven by the live C12 probe, never by
        # these fixtures, so the 7/7 here is never quoted as live
        # accuracy. Case 1 is the probe geometry.
        cases = [
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [240, 8],
             {'image_size': [1200, 757], 'region': [2509, 914, 1863, 1176]}),
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [240, 8],
             {'image_size': [450, 588], 'region': [2509, 914, 1863, 1176]}),
            ({'x': 100, 'y': 5, 'width': 200, 'height': 30},
             [0, 0],
             {'image_size': [800, 600], 'region': [100, 200, 800, 600]}),
            ({'x': 400, 'y': 300, 'width': 8, 'height': 8},
             [0, 0],
             {'image_size': [800, 600], 'region': [0, 0, 800, 600]}),
            ({'x': 0, 'y': 500, 'width': 800, 'height': 40},
             [0, 0],
             {'image_size': [900, 700], 'region': [50, 60, 900, 700]}),
            ({'x': 86, 'y': 1001, 'width': 440, 'height': 63},
             [0, 100],
             {'image_size': [901, 1176], 'region': [2533, 914, 901, 1176]}),
            ({'x': 86, 'y': 1101, 'width': 440, 'height': 63},
             [240, 8],
             {'image_size': [1802, 2352], 'region': [2509, 914, 1863, 1176]}),
        ]
        hits = 0
        for rect, moz_inner, meta in cases:
            field = {'rect': rect, 'focused': True, 'value': None,
                     'covered': False}
            session = FakeDomSession({'#f': field}, origin=moz_inner)
            ground = dom_act.ground_input(session, meta, '#f')
            sx, sy = cu.image_point(meta, ground['point'][0],
                                    ground['point'][1])
            absolute = [meta['region'][0] + moz_inner[0],
                        meta['region'][1] + moz_inner[1]]
            truth = {'x': absolute[0] + rect['x'],
                     'y': absolute[1] + rect['y'],
                     'width': rect['width'], 'height': rect['height']}
            hits += 1 if fastpath.point_in_rect(truth, sx, sy) else 0
        accuracy = hits / len(cases)
        self.assertGreaterEqual(accuracy, 0.9,
                                'map accuracy %s (%d/%d) below the 90%% bar'
                                % (accuracy, hits, len(cases)))
        self.assertEqual(hits, len(cases))


class FocusTypeTests(unittest.TestCase):
    def test_happy_path_click_type_enter_from_one_observation(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        act = FakeAct(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 3)
        self.assertEqual(result['point'], [306.0, 1132.5])
        self.assertTrue(result['focus_verified'])
        self.assertTrue(result['type_verified'])
        self.assertEqual(result['type_verified_basis'],
                         'dom-value+enter-accepted')
        self.assertEqual(result['dom_calls'], 8,
                         '4 grounding (locate + origin + hit + '
                         're-locate) + before-value + arm + focus + '
                         'type, all cheap')
        self.assertEqual(result['observes_added'], 0)
        self.assertEqual(result['act_observes'], 0)
        self.assertEqual(act.typed, ['hello'])
        self.assertEqual([a['type'] for a in act.executed],
                         ['click', 'type', 'key'])

    def test_click_miss_never_types(self):
        missed = dict(G30_FIELD, focused=False)
        session = FakeDomSession({'#msg-input': missed})
        act = FakeAct(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'focus_unverified')
        self.assertEqual(result['completed'], 1, 'click only, no type')
        self.assertEqual(act.typed, [], 'no keystroke was sent blind')
        self.assertEqual(result['dom_calls'], 7,
                         'grounding 4 + before-value + arm + focus 1, '
                         'type check never ran')

    def test_type_unverified_after_typing(self):
        # The click focused the input and the text was typed, but the
        # field never received it (type_sticks False): the batch
        # fails loudly.
        wrong = dict(G30_FIELD, value='goodbye', type_sticks=False)
        session = FakeDomSession({'#msg-input': wrong})
        act = FakeAct(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'type_unverified')
        self.assertEqual(act.typed, ['hello'])
        self.assertEqual(result['completed'], 2)
        self.assertFalse(result['type_verified'])

    def test_without_enter_completes_two_actions(self):
        session = FakeDomSession({'#msg-input': G30_FIELD})
        act = FakeAct(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=False)
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 2)
        self.assertEqual([a['type'] for a in act.executed],
                         ['click', 'type'])

    def test_focus_check_exception_fails_closed(self):
        broken = dict(G30_FIELD, focus_raises=True)
        session = FakeDomSession({'#msg-input': broken})
        act = FakeAct(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello')
        self.assertFalse(result['ok'])
        self.assertEqual(act.typed, [],
                         'a raising focus check types nothing')


class V12Session(FakeDomSession):
    """FakeDomSession plus a thread DOM for the V12 sent-bubble check."""

    def __init__(self, fields, origin=None):
        super().__init__(fields, origin)
        self.sent_bubbles = []

    def sent_bubble_contains(self, text):
        self.dom_calls += 1
        return text in self.sent_bubbles


class V12Act(FakeAct):
    """FakeAct that posts the sent bubble on Enter (the app's job).

    post_bubble False models Enter pressed but the send never
    registering: no bubble appears, so the V12 gate must fail.
    """

    def __init__(self, session, post_bubble=True):
        super().__init__(session)
        self.post_bubble = post_bubble
        self.enters = 0

    def __call__(self, meta, actions, focus_check=None, type_check=None,
                 **kw):
        for act in actions:
            if act.get('type') == 'key' and act.get('keys') == ['Enter']:
                self.enters += 1
                if self.session is not None:
                    field = self.session.fields['#msg-input']
                    if self.post_bubble:
                        text = field.get('value')
                        if text is not None:
                            self.session.sent_bubbles.append(text)
                    field['value'] = ''
        return super().__call__(meta, actions, focus_check, type_check,
                                **kw)


class V12Tests(unittest.TestCase):
    def test_send_verified_by_sent_bubble(self):
        field = dict(G30_FIELD, value=None)
        session = V12Session({'#msg-input': field})
        act = V12Act(session)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertTrue(result['ok'])
        self.assertTrue(result['sent_verified'])
        self.assertEqual(act.enters, 1)
        self.assertEqual(session.sent_bubbles, ['hello'])

    def test_failed_v12_gate_then_retry_skips_when_bubble_arrives(self):
        # Enter pressed, no bubble: the gate fails loudly instead of
        # claiming a send. When the bubble arrives late, the retry
        # sees it in the pre-send check and returns the recorded
        # success without pressing Enter a second time.
        field = dict(G30_FIELD, value=None)
        session = V12Session({'#msg-input': field})
        act = V12Act(session, post_bubble=False)
        first = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                   'hello', enter=True)
        self.assertFalse(first['ok'])
        self.assertEqual(first['error_code'], 'send_unverified')
        self.assertFalse(first['sent_verified'])
        self.assertEqual(act.enters, 1)
        session.sent_bubbles.append('hello')
        second = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertTrue(second['ok'])
        self.assertTrue(second['already_sent'])
        self.assertEqual(act.enters, 1, 'the retry pressed no Enter')


class HarvestTests(unittest.TestCase):
    def test_ground_many_records_dpr_zoom_and_moz_inner(self):
        fields = {
            '#clone1-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                       'height': 63},
                              'focused': True, 'value': None,
                              'covered': False},
        }
        session = FakeDomSession(fields)
        points = dom_act.ground_many(session, G30_META, ['#clone1-input'])
        self.assertIsInstance(points, dom_act.GroundPoints)
        evidence = points['#clone1-input']
        self.assertEqual(evidence['scale_factor'], 1)
        self.assertEqual(evidence['device_pixel_ratio'], 1)
        self.assertEqual(evidence['screen_pixels_per_css_pixel'], 1)
        self.assertEqual(evidence['zoom'], 1)
        self.assertEqual(evidence['moz_inner'], [0, 0])
        self.assertEqual(evidence['viewport_origin'], [2533, 914])


if __name__ == '__main__':
    unittest.main(verbosity=2)

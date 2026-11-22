"""Step 5 (FINAL direction, worker C4-STEP5-P1P5): P1 router, P5
asserts for the S2 task class (clone chat sends), CB-1 three-part
result contract, CB-5 locate confirmations.

Failing-first: these tests were written before the implementation and
failed on the pre-step-5 tree (missing modules, missing
locate_confirmed, no contract fields). No live browser, no observe;
router probes and DOM sessions are scripted fakes.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import dom_act
import zen_dom
from zen_dom import ZenSession, ZenDomError

import action_result
import dom_asserts
from dom_asserts import DomAssertError
from perception_router import route_perception


def _full_coverage(n=3):
    return {'elements': n, 'truncated': False}


class RouterTests(unittest.TestCase):
    def test_zen_content_routes_to_dom_zen(self):
        calls = []

        def probe(target):
            calls.append(target)
            return _full_coverage(3)

        decision = route_perception(
            {'kind': 'zen-content', 'selector': '#msg-input'},
            probes={'dom-zen': probe}, emit=lambda rec: calls.append(rec))
        self.assertEqual(decision['source'], 'dom-zen')
        self.assertEqual(decision['fell_through'], [])

    def test_zen_chrome_routes_to_screenshot_decided_boundary(self):
        # P8 is CLOSED: Zen chrome UI is screenshot-only, even when a
        # DOM backend offers full coverage for it.
        decision = route_perception(
            {'kind': 'zen-chrome', 'selector': '#urlbar'},
            probes={'dom-zen': lambda t: _full_coverage(9)},
            emit=lambda rec: None)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertIn('P8', decision['reason'])

    def test_empty_harvest_falls_through_to_screenshot(self):
        # T1a: route on COVERAGE, not target type. An empty harvest
        # never proceeds on a partial inventory.
        decision = route_perception(
            {'kind': 'zen-content', 'selector': '#missing'},
            probes={'dom-zen': lambda t: {'elements': 0,
                                          'truncated': False}},
            emit=lambda rec: None)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertEqual([f['source'] for f in decision['fell_through']],
                         ['dom-zen'])
        self.assertIn('empty', decision['fell_through'][0]['reason'])

    def test_truncated_a11y_tree_falls_through(self):
        # CB-5 (c): a truncated a11y tree is a false-confidence
        # source, so it falls through instead of grounding from it.
        decision = route_perception(
            {'kind': 'native-app', 'pid': 1234},
            probes={'a11y': lambda t: {'elements': 80,
                                       'truncated': True}},
            emit=lambda rec: None)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertEqual([f['source'] for f in decision['fell_through']],
                         ['a11y'])
        self.assertIn('truncated', decision['fell_through'][0]['reason'])

    def test_chromium_content_routes_to_dom_chromium(self):
        decision = route_perception(
            {'kind': 'chromium-content', 'selector': '#msg-input'},
            probes={'dom-chromium': lambda t: _full_coverage(2)},
            emit=lambda rec: None)
        self.assertEqual(decision['source'], 'dom-chromium')

    def test_unknown_target_fails_closed_to_screenshot(self):
        decision = route_perception({'kind': 'mystery-box'},
                                    probes={}, emit=lambda rec: None)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertIn('fail-closed', decision['reason'])

    def test_probe_exception_falls_through_not_raise(self):
        def boom(target):
            raise RuntimeError('marionette down')

        decision = route_perception(
            {'kind': 'zen-content', 'selector': '#msg-input'},
            probes={'dom-zen': boom}, emit=lambda rec: None)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertEqual([f['source'] for f in decision['fell_through']],
                         ['dom-zen'])

    def test_every_decision_logs_one_line(self):
        seen = []
        route_perception({'kind': 'zen-content', 'selector': '#x'},
                         probes={'dom-zen': lambda t: _full_coverage(1)},
                         emit=seen.append)
        route_perception({'kind': 'zen-chrome', 'selector': '#y'},
                         probes={}, emit=seen.append)
        self.assertEqual(len(seen), 2)
        for rec in seen:
            self.assertEqual(rec['event'], 'perception_routing')
            self.assertIn('source', rec)
            self.assertIn('target_kind', rec)
            self.assertIn('reason', rec)


class AssertSetTests(unittest.TestCase):
    SEND = [{'type': 'click', 'x': 10, 'y': 20},
            {'type': 'type', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']}]

    def test_send_chain_asserts_are_mandatory(self):
        coverage = dom_asserts.assert_coverage(self.SEND)
        self.assertEqual(coverage['unknown'], [])
        self.assertEqual(
            sorted(coverage['required']),
            ['focus_check', 'sent_bubble', 'type_check'])
        self.assertTrue(all(a['mandatory']
                            for a in coverage['covered']))

    def test_missing_type_check_raises_naming_it(self):
        with self.assertRaises(DomAssertError) as caught:
            dom_asserts.require_asserts(
                self.SEND, available={'focus_check': True,
                                      'sent_bubble': True})
        self.assertIn('type_check', str(caught.exception))

    def test_missing_sent_bubble_raises_for_send(self):
        with self.assertRaises(DomAssertError) as caught:
            dom_asserts.require_asserts(
                self.SEND, available={'focus_check': True,
                                      'type_check': True})
        self.assertIn('sent_bubble', str(caught.exception))

    def test_missing_focus_check_raises(self):
        with self.assertRaises(DomAssertError) as caught:
            dom_asserts.require_asserts(
                self.SEND, available={'type_check': True,
                                      'sent_bubble': True})
        self.assertIn('focus_check', str(caught.exception))

    def test_exception_list_names_scroll_and_hover(self):
        coverage = dom_asserts.assert_coverage(
            [{'type': 'scroll', 'x': 1, 'y': 2, 'dy': 100},
             {'type': 'hover', 'x': 1, 'y': 2},
             {'type': 'move', 'x': 1, 'y': 2},
             {'type': 'wait', 'ms': 100},
             {'type': 'drag', 'from': [1, 1], 'to': [2, 2]}])
        self.assertEqual(coverage['required'], [])
        self.assertEqual(coverage['covered'], [])
        self.assertEqual(coverage['unknown'], [])
        self.assertEqual(
            sorted(e['action'] for e in coverage['exceptions']),
            ['drag', 'hover', 'move', 'scroll', 'wait'])
        reasons = {e['action']: e['reason']
                   for e in coverage['exceptions']}
        self.assertIn('scroll position', reasons['scroll'])
        self.assertIn('hover state', reasons['hover'])

    def test_non_send_key_is_an_exception(self):
        coverage = dom_asserts.assert_coverage(
            [{'type': 'key', 'keys': ['Ctrl', 'a']}])
        self.assertEqual(coverage['required'], [])
        self.assertEqual([e['action'] for e in coverage['exceptions']],
                         ['key'])

    def test_code_exec_fill_maps_to_type_check(self):
        coverage = dom_asserts.assert_coverage(
            [{'type': 'click', 'ref': 'r1'},
             {'type': 'fill', 'ref': 'r1', 'text': 'hello'},
             {'type': 'key', 'keys': ['Enter']},
             {'type': 'assert', 'ref': 'r2', 'text': 'hello'}])
        self.assertEqual(coverage['unknown'], [])
        self.assertIn('type_check', coverage['required'])
        self.assertIn('sent_bubble', coverage['required'])

    def test_code_exec_send_without_trailing_assert_is_missing(self):
        program = [{'type': 'click', 'ref': 'r1'},
                   {'type': 'fill', 'ref': 'r1', 'text': 'hello'},
                   {'type': 'key', 'keys': ['Enter']}]
        with self.assertRaises(DomAssertError) as caught:
            dom_asserts.require_asserts(
                program, available={'focus_check': True,
                                    'type_check': True})
        self.assertIn('sent_bubble', str(caught.exception))
        # The same program with its V12 gate as a trailing assert
        # action passes: the program asserts the bubble itself.
        self.assertTrue(dom_asserts.require_asserts(
            program + [{'type': 'assert', 'ref': 'r2', 'text': 'hello'}],
            available={'focus_check': True, 'type_check': True}))

    def test_exception_list_is_shared_with_cb1(self):
        # CB-1 uses the SAME per-action exception list as P5: one
        # list, not two that can drift.
        self.assertIs(dom_asserts.DOM_ASSERT_EXCEPTIONS,
                      action_result.DOM_ASSERT_EXCEPTIONS)


class ContractTests(unittest.TestCase):
    def test_verified_false_fails_ok_even_when_input_sent(self):
        contract = action_result.build_contract(
            input_sent=True, target_received=True, verified=False,
            verified_basis='sent-bubble')
        self.assertFalse(contract['ok'])
        self.assertTrue(contract['input_sent'])
        self.assertFalse(contract['verified'])

    def test_verified_true_passes_ok(self):
        contract = action_result.build_contract(
            input_sent=True, target_received=True, verified=True,
            verified_basis='sent-bubble')
        self.assertTrue(contract['ok'])

    def test_verified_none_ok_follows_input_sent(self):
        sent = action_result.build_contract(
            input_sent=True, target_received=None, verified=None,
            verified_basis='no-dom-postcondition')
        self.assertTrue(sent['ok'])
        unsent = action_result.build_contract(
            input_sent=False, target_received=None, verified=None,
            verified_basis='no-dom-postcondition')
        self.assertFalse(unsent['ok'])

    def test_already_satisfied_passes_without_new_input(self):
        # Already-sent: nothing was sent in this call, but the
        # postcondition (bubble present) holds, so the end state
        # holds and ok is True.
        contract = action_result.build_contract(
            input_sent=False, target_received=True, verified=True,
            verified_basis='already-sent')
        self.assertTrue(contract['ok'])

    def test_migrate_legacy_result_keeps_ok_as_input_sent(self):
        contract = action_result.migrate_legacy_result({'ok': True})
        self.assertTrue(contract['input_sent'])
        self.assertIsNone(contract['verified'])
        self.assertTrue(contract['ok'])
        failed = action_result.migrate_legacy_result({'ok': False})
        self.assertFalse(failed['input_sent'])
        self.assertFalse(failed['ok'])

    def test_contract_ok_helper_on_result_dict(self):
        result = {'input_sent': True, 'target_received': True,
                  'verified': False}
        self.assertFalse(action_result.contract_ok(result))
        result['verified'] = True
        self.assertTrue(action_result.contract_ok(result))


class FakeSendSession:
    """Minimal DOM session for the S2 send chain: one composer field.

    Mirrors tests/test_dom_act.py FakeDomSession closely enough for
    focus_type: locate, viewport_origin, hit_check, focus_check,
    field_value, verify_typed, arm_typed_flag, typed_flag,
    sent_bubble_contains, live_window_origin.
    """

    def __init__(self, value='', bubble_text=None):
        self.fields = {'#msg-input': {
            'rect': {'x': 10, 'y': 20, 'width': 200, 'height': 30},
            'focused': False, 'value': value, 'covered': False}}
        self.sent_intents = set()
        self.bubble = bubble_text
        self._typed = {}

    def live_window_origin(self, address=None):
        return None

    def locate(self, selector):
        field = self.fields.get(selector)
        return None if field is None else dict(field['rect'])

    def viewport_origin(self, window_origin=None, window_size=None,
                        monitor_box=None):
        return list(window_origin or [0, 0])

    def hit_check(self, selector):
        field = self.fields.get(selector)
        return bool(field) and not field.get('covered', False)

    def focus_check(self, selector):
        field = self.fields.get(selector)
        return bool(field) and bool(field.get('focused', False))

    def field_value(self, selector):
        field = self.fields.get(selector)
        return None if field is None else field.get('value')

    def arm_typed_flag(self, selector):
        self._typed[selector] = False
        return True

    def note_typed(self, selector):
        self._typed[selector] = True

    def typed_flag(self, selector):
        return bool(self._typed.get(selector))

    def verify_typed(self, selector, expected, before=None):
        field = self.fields.get(selector)
        if field is None:
            return False
        if field.get('value') != expected:
            return False
        if before is not None and not self.typed_flag(selector):
            return False
        return True

    def sent_bubble_contains(self, text):
        return self.bubble is not None and self.bubble == text


META = {'window_bounds': [0, 0, 800, 600], 'monitor_box': [0, 0, 800, 600],
        'image_size': [800, 600], 'region': [0, 0, 800, 600]}


def _send_act(session):
    """Fake act_fn mirroring the cu.desktop_act hook protocol: click
    focuses, type sets the value with a trusted event, Enter sends
    (bubble appears). Returns a desktop_act-shaped result dict."""
    def act(meta, actions, focus_check=None, type_check=None,
            type_x_ranges=None, type_y_ranges=None):
        completed = 0
        for action in actions:
            if action['type'] == 'click':
                session.fields['#msg-input']['focused'] = True
                completed += 1
            elif action['type'] == 'type':
                if focus_check is not None:
                    ok, _reason = focus_check()
                    if not ok:
                        return {'ok': False, 'completed': completed,
                                'error': 'focus check failed',
                                'error_code': 'focus_unverified',
                                'focus_verified': False}
                session.fields['#msg-input']['value'] = action['text']
                session.note_typed('#msg-input')
                completed += 1
                if type_check is not None:
                    ok, _reason = type_check()
                    if not ok:
                        return {'ok': False, 'completed': completed,
                                'error': 'type check failed',
                                'error_code': 'type_unverified',
                                'type_verified': False,
                                'type_verified_basis': 'dom-value'}
                    return {'ok': True, 'completed': completed,
                            'type_verified': True,
                            'type_verified_basis': 'dom-value',
                            'focus_verified': True}
            elif action['type'] == 'key':
                session.bubble = session.fields['#msg-input']['value']
                completed += 1
        return {'ok': True, 'completed': completed}
    return act


class FocusTypeContractTests(unittest.TestCase):
    def test_send_carries_three_part_contract(self):
        session = FakeSendSession()
        result = dom_act.focus_type(
            session, _send_act(session), META, '#msg-input', 'hello',
            enter=True)
        self.assertTrue(result['ok'])
        self.assertTrue(result['input_sent'])
        self.assertTrue(result['target_received'])
        self.assertTrue(result['verified'])
        self.assertEqual(result['verified_basis'], 'sent-bubble')
        self.assertTrue(result['sent_verified'])
        asserts = result['asserts']
        self.assertEqual(asserts['click']['assert'], 'focus_check')
        self.assertTrue(asserts['click']['mandatory'])
        self.assertEqual(asserts['type']['assert'], 'type_check')
        self.assertTrue(asserts['type']['mandatory'])
        self.assertEqual(asserts['key']['assert'], 'sent_bubble')
        self.assertTrue(asserts['key']['mandatory'])

    def test_send_without_bubble_gate_refuses_before_typing(self):
        # P5 mandatory: a session that cannot run the V12 gate must
        # not send blind. The refusal happens before any keystroke,
        # so the field stays empty.
        class NoGateSession(FakeSendSession):
            def __getattribute__(self, name):
                if name == 'sent_bubble_contains':
                    raise AttributeError(name)
                return super().__getattribute__(name)

        session = NoGateSession()
        with self.assertRaises(DomAssertError):
            dom_act.focus_type(session, _send_act(session), META,
                               '#msg-input', 'hello', enter=True)
        self.assertEqual(session.fields['#msg-input']['value'], '')

    def test_type_only_carries_dom_value_contract(self):
        session = FakeSendSession()
        result = dom_act.focus_type(
            session, _send_act(session), META, '#msg-input', 'hello',
            enter=False)
        self.assertTrue(result['ok'])
        self.assertTrue(result['input_sent'])
        self.assertTrue(result['target_received'])
        self.assertTrue(result['verified'])
        self.assertEqual(result['verified_basis'], 'dom-value')


class FakeConfirmSession(ZenSession):
    """ZenSession with scripted evaluate(): the confirm script
    (marked zen_locate_confirmed) returns the scripted confirm dict,
    the hit script returns the scripted hit bool, the locate script
    returns the scripted second rect."""

    def __init__(self, confirm, hit=True, second_rect=None):
        super().__init__(timeout_s=5)
        self.session = 'test-session-id'
        self._confirm = confirm
        self._hit = hit
        self._second_rect = second_rect
        self.evaluate_calls = []

    def _wd(self, method, path, body=None):
        raise AssertionError('transport must not be used in this fake')

    def evaluate(self, script, args=None):
        self.evaluate_calls.append(script)
        if 'zen_locate_confirmed' in script:
            out = dict(self._confirm)
            rect = out.get('rect')
            if rect is not None:
                rect = dict(rect)
                rect.setdefault('center_x',
                                rect['x'] + rect['width'] / 2)
                rect.setdefault('center_y',
                                rect['y'] + rect['height'] / 2)
                out['rect'] = rect
            return out
        if 'elementFromPoint' in script:
            return self._hit
        if 'getBoundingClientRect' in script:
            rect = self._second_rect
            if rect is None:
                rect = self._confirm['rect']
            if rect is None:
                return None
            return {'x': rect['x'], 'y': rect['y'],
                    'width': rect['width'], 'height': rect['height'],
                    'center_x': rect['x'] + rect['width'] / 2,
                    'center_y': rect['y'] + rect['height'] / 2}
        raise AssertionError('unexpected script ' + script[:80])


def _rect(x=10, y=20, w=200, h=30):
    return {'x': x, 'y': y, 'width': w, 'height': h,
            'center_x': x + w / 2, 'center_y': y + h / 2}


class LocateConfirmedTests(unittest.TestCase):
    def _session(self, **kw):
        confirm = {'rect': _rect(), 'visible': True, 'enabled': True,
                   'count': 1}
        confirm.update(kw.pop('confirm', {}))
        return FakeConfirmSession(confirm, **kw)

    def test_all_confirmations_pass(self):
        session = self._session()
        report = session.locate_confirmed('#msg-input')
        self.assertTrue(report['visible'])
        self.assertTrue(report['interactive'])
        self.assertTrue(report['uncovered'])
        self.assertTrue(report['stable'])
        self.assertTrue(report['unique'])
        self.assertEqual(report['unique_count'], 1)
        self.assertEqual(report['rect'], _rect())

    def test_missing_element_returns_none(self):
        session = self._session(confirm={'rect': None, 'visible': False,
                                         'enabled': False, 'count': 0})
        self.assertIsNone(session.locate_confirmed('#gone'))

    def test_hidden_element_is_not_visible(self):
        session = self._session(confirm={'visible': False})
        report = session.locate_confirmed('#msg-input')
        self.assertFalse(report['visible'])

    def test_disabled_element_is_not_interactive(self):
        session = self._session(confirm={'enabled': False})
        report = session.locate_confirmed('#msg-input')
        self.assertFalse(report['interactive'])

    def test_covered_element_is_not_uncovered(self):
        session = self._session(hit=False)
        report = session.locate_confirmed('#msg-input')
        self.assertFalse(report['uncovered'])

    def test_moved_between_reads_is_not_stable(self):
        session = self._session(second_rect=_rect(x=12, y=20))
        report = session.locate_confirmed('#msg-input')
        self.assertFalse(report['stable'])
        self.assertEqual(report['rect'], _rect())

    def test_subpixel_jitter_within_tolerance_is_stable(self):
        session = self._session(second_rect=_rect(x=10.2, y=20))
        report = session.locate_confirmed('#msg-input')
        self.assertTrue(report['stable'])

    def test_ambiguous_selector_is_not_unique(self):
        session = self._session(confirm={'count': 2})
        report = session.locate_confirmed('#msg-input')
        self.assertFalse(report['unique'])
        self.assertEqual(report['unique_count'], 2)


class ConfirmLocateTests(unittest.TestCase):
    def test_strict_path_refuses_covered_element(self):
        session = FakeConfirmSession(
            {'rect': _rect(), 'visible': True, 'enabled': True,
             'count': 1},
            hit=False)
        with self.assertRaises(dom_act.DomActError) as caught:
            dom_act.confirm_locate(session, '#msg-input')
        self.assertIn('covered', str(caught.exception))

    def test_strict_path_refuses_ambiguous_selector(self):
        session = FakeConfirmSession(
            {'rect': _rect(), 'visible': True, 'enabled': True,
             'count': 3})
        with self.assertRaises(dom_act.DomActError) as caught:
            dom_act.confirm_locate(session, '#msg-input')
        self.assertIn('3 elements', str(caught.exception))

    def test_fallback_path_composes_from_locate_and_hit_check(self):
        # A session without locate_confirmed (an older duck-typed
        # session) still confirms from locate + hit_check; unique
        # and interactive are unknowable there, so they are None
        # with basis 'unprobed', not a refusal.
        session = FakeSendSession()
        report = dom_act.confirm_locate(session, '#msg-input')
        self.assertTrue(report['visible'])
        self.assertTrue(report['uncovered'])
        self.assertTrue(report['stable'])
        self.assertIsNone(report['unique'])
        self.assertEqual(report['unique_basis'], 'unprobed')
        self.assertIsNone(report['interactive'])
        self.assertEqual(report['rect']['x'], 10)


if __name__ == '__main__':
    unittest.main()

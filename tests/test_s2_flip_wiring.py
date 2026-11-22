"""S2 flip wiring tests (step 6).

Covers the two wiring changes that make the one-class flip possible:
1. cu.py code-exec --endpoint (P3 port split, P2 persistent port
   2026-11-22): a program aimed at Brave on 127.0.0.1:9224 must not
   silently drive Chromium on 127.0.0.1:9223. The override applies to
   that program only and the retained default is restored afterwards.
2. The live harness program shape (scripts/s2_flip_live.py): the
   fixed send program grounds the composer, fills, sends with Enter,
   and ends with the trailing assert (P5 V12 gate in program form);
   messages are unique per run and browser.
"""
import importlib.util
import io
import json
import os
import pathlib
import re
import sys
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))

import cu  # noqa: E402
import dom_asserts  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    's2_flip_live', str(pathlib.Path(__file__).resolve().parents[1]
                        / 'scripts' / 's2_flip_live.py'))
s2_flip_live = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s2_flip_live)


class FakeCodeExec:
    """Stands in for the code_exec module; records the backend it gets."""

    instances = []

    def __init__(self):
        self.calls = []

    def is_enabled(self):
        return True

    def run_program(self, program, backend, state_dir=None,
                    session_token=None, intent=None, check_cancel=None,
                    wall_seconds=30):
        self.calls.append({'program': program, 'endpoint': backend.browser_endpoint,
                           'intent': intent, 'wall_seconds': wall_seconds})
        return {'ok': True, 'api_calls': 3, 'elapsed_ms': 12.5, 'log': []}


class CodeExecEndpointTests(unittest.TestCase):
    def setUp(self):
        self._saved = cu.BROWSER_ENDPOINT
        self.addCleanup(setattr, cu, 'BROWSER_ENDPOINT', self._saved)
        self.fake = FakeCodeExec()
        self._real_code_exec = sys.modules.get('code_exec')
        sys.modules['code_exec'] = self.fake
        self.addCleanup(self._restore_code_exec)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)

    def _restore_code_exec(self):
        if self._real_code_exec is None:
            sys.modules.pop('code_exec', None)
        else:
            sys.modules['code_exec'] = self._real_code_exec

    def run_main(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        context = [
            patch.object(cu.sys, 'argv', ['cu', *argv]),
            patch.object(cu.sys, 'stdout', stdout),
            patch.object(cu.sys, 'stderr', stderr),
            patch.object(cu, 'STATE', self.tmp),
            patch.object(cu, 'ROOT', self.tmp),
            patch.object(cu, 'environment', return_value={}),
            patch.object(cu, 'check_cancel'),
            patch.object(cu, 'require_session'),
            patch.object(cu, 'locked'),
            patch.object(cu, 'read_code_exec_program', return_value='x = 1'),
            patch.dict(os.environ, {'CU_CODE_EXEC': '1'}),
        ]
        with ExitStack() as stack:
            for manager in context:
                stack.enter_context(manager)
            code = cu.main()
        return stdout.getvalue(), code

    def test_endpoint_override_reaches_backend_and_restores_default(self):
        cu.BROWSER_ENDPOINT = 'http://127.0.0.1:9223'
        out, code = self.run_main('code-exec', '--endpoint',
                                  'http://127.0.0.1:9224', '--program', '-')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)['ok'], True)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(self.fake.calls[0]['endpoint'], 'http://127.0.0.1:9224')
        self.assertEqual(cu.BROWSER_ENDPOINT, 'http://127.0.0.1:9223',
                         'a one-program override must not replace the default')

    def test_no_endpoint_keeps_default(self):
        cu.BROWSER_ENDPOINT = 'http://127.0.0.1:9223'
        out, code = self.run_main('code-exec', '--program', '-')
        self.assertEqual(code, 0)
        self.assertEqual(self.fake.calls[0]['endpoint'], 'http://127.0.0.1:9223')
        self.assertEqual(cu.BROWSER_ENDPOINT, 'http://127.0.0.1:9223')

    def test_non_loopback_endpoint_refused(self):
        with self.assertRaisesRegex(ValueError, 'loopback'):
            self.run_main('code-exec', '--endpoint',
                          'http://192.168.1.13:9223', '--program', '-')
        self.assertEqual(self.fake.calls, [])

    def test_bad_port_refused(self):
        with self.assertRaisesRegex(ValueError, 'port'):
            self.run_main('code-exec', '--endpoint',
                          'http://127.0.0.1:99999', '--program', '-')
        self.assertEqual(self.fake.calls, [])


class ProgramShapeTests(unittest.TestCase):
    def test_program_carries_target_message_and_trailing_assert(self):
        program = s2_flip_live.build_program('TABID123', 'S2-FLIP-R1-BRAVE-IGNORE-TEST')
        self.assertIn('TABID123', program)
        self.assertIn('S2-FLIP-R1-BRAVE-IGNORE-TEST', program)
        # The selector travels JSON-encoded inside the program source
        # (json.dumps), so the quotes are escaped; parsing it back
        # must give the exact selector.
        self.assertIn(json.dumps(s2_flip_live.BUBBLE_ASSERT_SELECTOR), program)
        self.assertIn('"timeout_ms": 3000', program)
        # The program ends with an assert_state on the dom_act result,
        # so a failed send fails the envelope instead of passing silent.
        self.assertIn('assert_state(res.get("ok") is True', program)

    def test_program_actions_carry_p2_scope_and_observation_id(self):
        # P2 (step 7): every dom_act action must carry scope (the
        # target id) and observation_id (snap["snapshot"]), or
        # _api_dom_act refuses before any CDP request. The dry run
        # caught the missing stamps as "action 0 is missing scope".
        program = s2_flip_live.build_program('TABID123', 'hello')
        self.assertIn('"scope": "TABID123"', program)
        self.assertIn('"observation_id": snap["snapshot"]', program)
        self.assertEqual(program.count('"scope": "TABID123"'), 3)
        self.assertEqual(program.count('"observation_id": snap["snapshot"]'), 3)

    def test_set_value_program_carries_p2_stamps_and_passes_p5(self):
        # C5-B1 landed shape (option A): the input-free program is
        # [set_value, focus, key Enter, assert bubble], 4 actions,
        # P2 stamps on all 4. The Enter is inside the program now:
        # the /tmp focus+Enter helper is gone. The old 2-action
        # shape (set_value plus value assert, Enter from the helper)
        # is removed, not kept alongside, so there is exactly one
        # (b1) program shape.
        program = s2_flip_live.build_program_set_value('TABID123', 'hello')
        self.assertIn('"type": "set_value"', program)
        self.assertIn('"type": "focus"', program)
        self.assertIn('"keys": ["Enter"]', program)
        self.assertNotIn('"type": "fill"', program)
        self.assertIn('"scope": "TABID123"', program)
        self.assertIn('"observation_id": snap["snapshot"]', program)
        self.assertEqual(program.count('"scope": "TABID123"'), 4)
        self.assertEqual(program.count('"observation_id": snap["snapshot"]'), 4)
        # The focus action uses a ref, the same composer ref as the
        # set_value action, so a wrong-ref focus cannot silently
        # focus another element.
        self.assertIn('"type": "focus", "ref": comp', program)
        actions = [
            {'type': 'set_value', 'ref': 'e1', 'text': 'hello',
             'scope': 'TABID123', 'observation_id': 'SNAP1'},
            {'type': 'focus', 'ref': 'e1',
             'scope': 'TABID123', 'observation_id': 'SNAP1'},
            {'type': 'key', 'keys': ['Enter'],
             'scope': 'TABID123', 'observation_id': 'SNAP1'},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000,
             'scope': 'TABID123', 'observation_id': 'SNAP1'},
        ]
        self.assertTrue(dom_asserts.require_asserts(
            actions, available={'focus_check': True, 'type_check': True,
                                'sent_bubble': False}))
        from code_exec import _validate_dom_actions
        _validate_dom_actions(actions, {'e1'}, snapshot_id='SNAP1',
                              target='TABID123')

    def test_composer_grounding_accepts_text_input_role(self):
        # Held-out fixture (tests/two_vision_fixture.html): the
        # harvest maps <input type="text"> to role "input" (cdp.mjs
        # uses the raw tag name), so the textarea/textbox-only
        # grounding missed the fixture's #msg-input and held-out run
        # 90 failed with "composer not found in snapshot". The
        # grounding must accept role "input" too; set_value/focus
        # still fail loudly on a non-editable field, so a
        # mis-grounded non-text input cannot send silently.
        fixture_snap = {
            'snapshot': 'SNAP1',
            'elements': [
                {'ref': 'e1', 'role': 'input', 'name': 'Message'},
                {'ref': 'e2', 'role': 'button', 'name': 'Send'},
                {'ref': 'e3', 'role': 'input', 'name': 'Search'},
                {'ref': 'e4', 'role': 'button', 'name': 'Emoji'},
            ],
        }

        def _assert_state(cond, msg):
            if not cond:
                raise AssertionError(msg)

        for build in (s2_flip_live.build_program,
                      s2_flip_live.build_program_set_value):
            program = build('TABID123', 'hello')
            head = program.split('res = dom_act(snap, [')[0]
            ns = {'dom_observe': lambda _t: fixture_snap,
                  'assert_state': _assert_state}
            exec(head, ns)  # noqa: S102 - the program source is ours
            self.assertEqual(ns['comp'], 'e1')

    def test_set_value_program_without_focus_raises_p5(self):
        # The send-requires-focus rule: [set_value, key Enter,
        # assert] with no focus-establishing action raises
        # DomAssertError, because the Enter would go to BODY and
        # fail silently.
        actions = [
            {'type': 'set_value', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000},
        ]
        with self.assertRaisesRegex(dom_asserts.DomAssertError,
                                    'focus-establishing'):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_landed_program_without_trailing_assert_fails_p5(self):
        # F10 (c): the landed shape without its trailing assert
        # must fail P5. The existing no-trailing-assert test covers
        # the fill shape only, not the landed shape.
        actions = [
            {'type': 'set_value', 'ref': 'e1', 'text': 'hello'},
            {'type': 'focus', 'ref': 'e1'},
            {'type': 'key', 'keys': ['Enter']},
        ]
        with self.assertRaises(dom_asserts.DomAssertError):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_type_without_click_raises_p5(self):
        # F10 (e): [type, key Enter, assert] with no click must
        # raise: type establishes no focus, so the Enter has no
        # focus-establishing action before it.
        actions = [
            {'type': 'type', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000},
        ]
        with self.assertRaisesRegex(dom_asserts.DomAssertError,
                                    'focus-establishing'):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_click_type_enter_still_passes_p5(self):
        # F10 (e): the desktop focus_type chain [click, type, key
        # Enter, assert] still passes: the click is the
        # focus-establishing action.
        actions = [
            {'type': 'click', 'ref': 'e1'},
            {'type': 'type', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000},
        ]
        self.assertTrue(dom_asserts.require_asserts(
            actions, available={'focus_check': True, 'type_check': True,
                                'sent_bubble': False}))

    def test_focus_after_enter_raises_p5(self):
        # F10 (e): focus must PRECEDE the send key. A focus step
        # placed after the Enter does not satisfy the rule.
        actions = [
            {'type': 'set_value', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
            {'type': 'focus', 'ref': 'e1'},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000},
        ]
        # The raise must come from the focus rule, not from the
        # unknown-action rule: before the focus entry lands this
        # test would pass for the wrong reason, so the message is
        # pinned to the focus rule.
        with self.assertRaisesRegex(dom_asserts.DomAssertError,
                                    'focus-establishing'):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_unknown_action_type_raises_p5(self):
        # F10 (d) permanent anchor: require_asserts fails closed on
        # an unknown action type. This is the fail-closed behavior
        # the landed-program anchor relied on before the focus
        # entry landed in dom_asserts.
        actions = [
            {'type': 'teleport', 'ref': 'e1'},
        ]
        with self.assertRaises(dom_asserts.DomAssertError):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_browser_whitelists_agree_on_focus(self):
        # F10 (f): the three browser whitelists (cdp.mjs, the
        # code_exec.py mirror, the cu.py browser set) contain the
        # same set, except for the known hover_click drift (cu.py
        # lines 1299 and 1341 lack hover_click; adding it there is
        # a follow-up, not part of this landing).
        root = pathlib.Path(__file__).resolve().parents[1] / 'scripts'

        def _quoted(text):
            return set(re.findall(r"'([^']+)'", text))

        cdp = (root / 'cdp.mjs').read_text()
        m = re.search(r"if\(!\[([^\]]+)\]\.includes\(a\.type\)\)", cdp)
        self.assertIsNotNone(m, 'cdp.mjs action whitelist not found')
        cdp_set = _quoted(m.group(1))
        code_exec = (root / 'code_exec.py').read_text()
        m = re.search(r"allowed = \{([^}]+)\}", code_exec)
        self.assertIsNotNone(m, 'code_exec.py allowed set not found')
        exec_set = _quoted(m.group(1))
        cu = (root / 'cu.py').read_text()
        validate = cu[cu.index('def validate_actions'):]
        validate = validate[:validate.index('def validate_terminal_assert')]
        browser_sets = [_quoted(m.group(1)) for m in
                        re.finditer(r"\{([^{}]*)\}", validate)
                        if 'confirm_click' in m.group(1)]
        self.assertEqual(len(browser_sets), 1,
                         'exactly one cu.py browser set expected')
        cu_set = browser_sets[0]
        m = re.search(r"backend=='browser' and a\['type'\] in \(([^)]+)\)",
                      validate)
        self.assertIsNotNone(m, 'cu.py browser element-action check not found')
        cu_element_set = _quoted(m.group(1))
        for name, s in (('cdp.mjs', cdp_set), ('code_exec.py', exec_set),
                        ('cu.py', cu_set), ('cu.py element check', cu_element_set)):
            self.assertIn('focus', s, 'focus missing from %s' % name)
        self.assertEqual(cdp_set, exec_set)
        self.assertEqual(cu_set, cdp_set - {'hover_click'})
        self.assertEqual(cu_element_set,
                         {'click', 'confirm_click', 'fill', 'set_value',
                          'focus', 'assert'})

    def test_program_actions_satisfy_p5_requires(self):
        # The action list the program encodes, checked against the same
        # require_asserts gate code_exec._api_dom_act enforces.
        actions = [
            {'type': 'fill', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
            {'type': 'assert', 'selector': s2_flip_live.BUBBLE_ASSERT_SELECTOR,
             'text': 'hello', 'timeout_ms': 3000},
        ]
        self.assertTrue(dom_asserts.require_asserts(
            actions, available={'focus_check': True, 'type_check': True,
                                'sent_bubble': False}))

    def test_program_without_trailing_assert_would_fail_p5(self):
        actions = [
            {'type': 'fill', 'ref': 'e1', 'text': 'hello'},
            {'type': 'key', 'keys': ['Enter']},
        ]
        with self.assertRaises(dom_asserts.DomAssertError):
            dom_asserts.require_asserts(
                actions, available={'focus_check': True, 'type_check': True,
                                    'sent_bubble': False})

    def test_chromium_set_value_splits_variants_per_browser(self):
        # C5-S2-REOPEN: Brave keeps fill (it already sends 5/5
        # with fill), Chromium alone uses set_value. The global
        # --set-value flag still forces set_value on both.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            split = s2_flip_live.Harness(
                tmp, 0, chromium_set_value=True)
            self.assertEqual(split.variant_for('brave'), 'fill')
            self.assertEqual(split.variant_for('chromium'), 'set_value')
            plain = s2_flip_live.Harness(tmp, 0)
            self.assertEqual(plain.variant_for('brave'), 'fill')
            self.assertEqual(plain.variant_for('chromium'), 'fill')
            forced = s2_flip_live.Harness(
                tmp, 0, program_variant='set_value')
            self.assertEqual(forced.variant_for('brave'), 'set_value')
            self.assertEqual(forced.variant_for('chromium'), 'set_value')

    def test_messages_unique_per_run_and_browser(self):
        seen = set()
        for run in (1, 2, 3, 4, 5):
            for browser in ('brave', 'chromium'):
                message = s2_flip_live.message_for(run, browser)
                self.assertNotIn(message, seen)
                seen.add(message)
                self.assertIn('IGNORE', message)

    def test_router_gates_send_on_complete_coverage(self):
        from perception_router import route_perception
        seen = []
        decision = route_perception(
            {'kind': 'chromium-content'},
            probes={'dom-chromium': lambda t: {'elements': 51, 'truncated': False}},
            emit=seen.append)
        self.assertEqual(decision['source'], 'dom-chromium')
        self.assertEqual(seen[0]['event'], 'perception_routing')
        decision = route_perception(
            {'kind': 'chromium-content'},
            probes={'dom-chromium': lambda t: {'elements': 0, 'truncated': False}},
            emit=seen.append)
        self.assertEqual(decision['source'], 'screenshot')
        self.assertTrue(decision['fell_through'])


if __name__ == '__main__':
    unittest.main()

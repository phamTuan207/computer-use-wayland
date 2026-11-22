"""S2 flip wiring tests (step 6).

Covers the two wiring changes that make the one-class flip possible:
1. cu.py code-exec --endpoint (P3 port split, P2 persistent port
   2026-11-22): a program aimed at Brave on 127.0.0.1:9224 must not
   silently drive Chromium on 127.0.0.1:9223. The override applies to
   that program only and the retained default is restored afterwards.
2. The live harness program shape (scripts/s2_flip_live.py): the
   send program grounds the composer, uses set_value for Brave and
   fill only for Chromium by default, sends with Enter, and ends
   with the trailing assert (P5 V12 gate in program form);
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

    def test_composer_grounding_accepts_aria_text_entry_roles(self):
        # W-ARIA GAP B (failing-first): the harvest maps an explicit
        # ARIA text-entry role verbatim, so <input role="searchbox">
        # arrives as "searchbox" and <input role="combobox"> as
        # "combobox"; the grounding must accept both, like it accepts
        # "input" since run 91. "textbox" is covered too: GAP A is
        # fixed at the harvest (contenteditable harvests as
        # "textbox"), and the grounding half must accept it.
        # set_value/focus still fail loudly on a non-editable field,
        # so a mis-grounded non-text input cannot send silently.
        def _assert_state(cond, msg):
            if not cond:
                raise AssertionError(msg)

        for role in ('textbox', 'searchbox', 'combobox'):
            fixture_snap = {
                'snapshot': 'SNAP1',
                'elements': [
                    {'ref': 'e1', 'role': role, 'name': 'Message'},
                    {'ref': 'e2', 'role': 'button', 'name': 'Send'},
                ],
            }
            for build in (s2_flip_live.build_program,
                          s2_flip_live.build_program_set_value):
                program = build('TABID123', 'hello')
                head = program.split('res = dom_act(snap, [')[0]
                ns = {'dom_observe': lambda _t: fixture_snap,
                      'assert_state': _assert_state}
                exec(head, ns)  # noqa: S102 - the program source is ours
                self.assertEqual(ns['comp'], 'e1',
                                 'role %r must ground' % role)

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
        # Work 1, 2026-11-22: Brave returns set_value unconditionally
        # in variant_for, not only by default. Chromium alone uses
        # set_value only when chromium_set_value is set. The
        # global --set-value flag still forces set_value on both.
        with tempfile.TemporaryDirectory() as tmp:
            split = s2_flip_live.Harness(
                tmp, 0, chromium_set_value=True)
            self.assertEqual(split.variant_for('brave'), 'set_value')
            self.assertEqual(split.variant_for('chromium'), 'set_value')
            plain = s2_flip_live.Harness(tmp, 0)
            self.assertEqual(plain.variant_for('brave'), 'set_value')
            self.assertEqual(plain.variant_for('chromium'), 'fill')
            forced = s2_flip_live.Harness(
                tmp, 0, program_variant='set_value')
            self.assertEqual(forced.variant_for('brave'), 'set_value')
            self.assertEqual(forced.variant_for('chromium'), 'set_value')

    def test_brave_uses_set_value_by_default(self):
        # Work 1, 2026-11-22: variant_for returns set_value for
        # Brave, and the program builder emits 4 actions, no fill.
        # No send runs here, so no send outcome is claimed.
        # P2 stamp counts are also covered in
        # test_set_value_program_carries_p2_stamps_and_passes_p5;
        # this test re-checks them on the default Brave program
        # and adds order plus parsed actions, instead of keeping
        # a separate duplicate stamp test.
        with tempfile.TemporaryDirectory() as tmp:
            harness = s2_flip_live.Harness(tmp, 0)
            self.assertEqual(harness.variant_for('brave'), 'set_value')
            program = s2_flip_live.build_program_set_value(
                'TABID123', 'hello')
            self.assertIn('"type": "set_value"', program)
            self.assertIn('"type": "focus"', program)
            self.assertIn('"keys": ["Enter"]', program)
            self.assertNotIn('"type": "fill"', program)
            # Order in the program string: set_value, focus, Enter, assert.
            pos_set_value = program.find('"type": "set_value"')
            pos_focus = program.find('"type": "focus"')
            pos_enter = program.find('"keys": ["Enter"]')
            pos_assert = program.find('"type": "assert"')
            self.assertLess(pos_set_value, pos_focus)
            self.assertLess(pos_focus, pos_enter)
            self.assertLess(pos_enter, pos_assert)
            self.assertEqual(program.count('"scope": "TABID123"'), 4)
            self.assertEqual(
                program.count('"observation_id": snap["snapshot"]'), 4)
            self.assertIn('"type": "focus", "ref": comp', program)
            self.assertIn(
                json.dumps(s2_flip_live.BUBBLE_ASSERT_SELECTOR), program)
            # Parse the program into real actions, instead of using
            # a hand-written literal: exec it with a fake dom_observe
            # and a capturing dom_act, then validate the captured list.
            captured = {}

            def _fake_dom_act(snap_arg, actions):
                captured['actions'] = actions
                return {'ok': True, 'completed': 4, 'execution_ms': 95}

            def _assert_state(cond, msg):
                if not cond:
                    raise AssertionError(msg)

            ns = {
                'dom_observe': lambda _t: {
                    'snapshot': 'SNAP1',
                    'elements': [{'ref': 'e1', 'role': 'textarea',
                                  'name': 'Message'}]},
                'dom_act': _fake_dom_act,
                'assert_state': _assert_state,
            }
            exec(program, ns)  # noqa: S102 - the program source is ours
            actions = captured['actions']
            self.assertEqual(len(actions), 4)
            self.assertEqual(
                [a['type'] for a in actions],
                ['set_value', 'focus', 'key', 'assert'])
            self.assertTrue(dom_asserts.require_asserts(
                actions, available={'focus_check': True,
                                    'type_check': True,
                                    'sent_bubble': False}))
            from code_exec import _validate_dom_actions
            _validate_dom_actions(actions, {'e1'}, snapshot_id='SNAP1',
                                  target='TABID123')

    def test_send_browser_brave_default_uses_set_value(self):
        # Dispatch, HIGH: Brave by default must call the (b1)
        # program, with a pre-send count and CB-1 input_sent from
        # completed 3. SSH is mocked: count_check, oneshot_code_exec
        # and v12_check are replaced on the instance, so no SSH runs.
        with tempfile.TemporaryDirectory() as tmp:
            harness = s2_flip_live.Harness(tmp, 1)
            seen = {}

            def _count_check(endpoint, target_id, message):
                seen['count_called'] = True
                return {'count': 0, 'items': []}

            def _oneshot(endpoint, program, intent):
                seen['program'] = program
                seen['endpoint'] = endpoint
                return (95.0, {
                    'ok': True, 'api_calls': 3, 'elapsed_ms': 95,
                    'error': None, 'error_type': None,
                    'log': ['dom_act ok True completed 4 ms 95 '
                            'error None']})

            def _v12(endpoint, target_id, message):
                return {'found': True, 'attempts': 1, 'ms': 3.0}

            harness.count_check = _count_check
            harness.oneshot_code_exec = _oneshot
            harness.v12_check = _v12
            out = harness.send_browser(
                'brave', 'TABID123', 'S2-BRAVE-B1-R1-BRAVE-IGNORE-TEST')
            self.assertEqual(out['program_variant'], 'set_value')
            self.assertTrue(seen.get('count_called'))
            self.assertEqual(out.get('pre_count'), {'count': 0, 'items': []})
            self.assertEqual(seen['endpoint'],
                             s2_flip_live.BROWSERS['brave']['endpoint'])
            self.assertIn('"type": "set_value"', seen['program'])
            self.assertIn('"type": "focus"', seen['program'])
            self.assertNotIn('"type": "fill"', seen['program'])
            self.assertEqual(out['outcome'], 'sent')
            self.assertTrue(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertTrue(out['cb1']['verified'])
            self.assertEqual(out['cb1']['completed'], 4)

    def test_send_browser_chromium_default_uses_fill(self):
        # Dispatch, HIGH: Chromium by default must call the fill
        # program, with no pre-send count. Same SSH mock as above.
        with tempfile.TemporaryDirectory() as tmp:
            harness = s2_flip_live.Harness(tmp, 1)
            seen = {}

            def _count_check(endpoint, target_id, message):
                seen['count_called'] = True
                return {'count': 0, 'items': []}

            def _oneshot(endpoint, program, intent):
                seen['program'] = program
                seen['endpoint'] = endpoint
                return (140.0, {
                    'ok': True, 'api_calls': 3, 'elapsed_ms': 140,
                    'error': None, 'error_type': None,
                    'log': ['dom_act ok True completed 3 ms 140 '
                            'error None']})

            def _v12(endpoint, target_id, message):
                return {'found': True, 'attempts': 1, 'ms': 3.0}

            harness.count_check = _count_check
            harness.oneshot_code_exec = _oneshot
            harness.v12_check = _v12
            out = harness.send_browser(
                'chromium', 'TABID123',
                'S2-BRAVE-B1-R1-CHROMIUM-IGNORE-TEST')
            self.assertEqual(out['program_variant'], 'fill')
            self.assertNotIn('pre_count', out)
            self.assertFalse(seen.get('count_called'))
            self.assertEqual(seen['endpoint'],
                             s2_flip_live.BROWSERS['chromium']['endpoint'])
            self.assertIn('"type": "fill"', seen['program'])
            self.assertNotIn('"type": "set_value"', seen['program'])
            self.assertEqual(out['outcome'], 'sent')
            self.assertTrue(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertTrue(out['cb1']['verified'])
            self.assertEqual(out['cb1']['completed'], 3)

    def _send_with_completed(self, tmp, browser, completed, count=0):
        # Shared mock for send_browser: count_check returns count,
        # oneshot returns an envelope with the given completed value,
        # v12 always finds the message. Returns (seen, out).
        harness = s2_flip_live.Harness(tmp, 1)
        seen = {}

        def _count_check(endpoint, target_id, message):
            seen['count_called'] = True
            return {'count': count, 'items': []}

        def _oneshot(endpoint, program, intent):
            seen['program'] = program
            seen['endpoint'] = endpoint
            return (95.0, {
                'ok': True, 'api_calls': 3, 'elapsed_ms': 95,
                'error': None, 'error_type': None,
                'log': ['dom_act ok True completed %d ms 95 error None'
                        % completed]})

        def _v12(endpoint, target_id, message):
            return {'found': True, 'attempts': 1, 'ms': 3.0}

        harness.count_check = _count_check
        harness.oneshot_code_exec = _oneshot
        harness.v12_check = _v12
        out = harness.send_browser(
            browser, 'TABID123',
            'S2-BRAVE-B1-R1-%s-IGNORE-TEST' % browser.upper())
        return seen, out

    def test_send_browser_brave_already_sent(self):
        # Guard, MEDIUM: a pre-send count above 0 aborts the send.
        # No oneshot runs, no program and no cb1 are recorded.
        with tempfile.TemporaryDirectory() as tmp:
            seen, out = self._send_with_completed(
                tmp, 'brave', 4, count=1)
            self.assertEqual(out['outcome'], 'already-sent')
            self.assertEqual(out.get('pre_count', {}).get('count'), 1)
            self.assertTrue(seen.get('count_called'))
            self.assertNotIn('program', seen)
            self.assertNotIn('program', out)
            self.assertNotIn('cb1', out)
            self.assertNotIn('v12', out)

    def test_send_browser_cb1_threshold_brave(self):
        # CB-1 threshold, MEDIUM: Brave set_value needs completed
        # >= 3 for input_sent. completed 2 must not send, completed
        # 3 must send. target_received needs completed >= 1.
        with tempfile.TemporaryDirectory() as tmp:
            _seen, out = self._send_with_completed(tmp, 'brave', 2)
            self.assertEqual(out['outcome'], 'sent')
            self.assertFalse(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertEqual(out['cb1']['completed'], 2)
            _seen, out = self._send_with_completed(tmp, 'brave', 3)
            self.assertTrue(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertEqual(out['cb1']['completed'], 3)

    def test_send_browser_cb1_threshold_chromium(self):
        # CB-1 threshold, MEDIUM: Chromium fill needs completed
        # >= 2 for input_sent. completed 1 must not send,
        # completed 2 must send.
        with tempfile.TemporaryDirectory() as tmp:
            _seen, out = self._send_with_completed(tmp, 'chromium', 1)
            self.assertEqual(out['outcome'], 'sent')
            self.assertFalse(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertEqual(out['cb1']['completed'], 1)
            _seen, out = self._send_with_completed(tmp, 'chromium', 2)
            self.assertTrue(out['cb1']['input_sent'])
            self.assertTrue(out['cb1']['target_received'])
            self.assertEqual(out['cb1']['completed'], 2)

    def test_delayed_targets_only_set_value_attempts(self):
        # Delayed guard, MEDIUM: only set_value browsers with both
        # a target id and a message are recounted.
        with tempfile.TemporaryDirectory() as tmp:
            harness = s2_flip_live.Harness(tmp, 0)
            results = {'browsers': {
                'brave': {'target_id': 'TAB1', 'message': 'M1',
                          'outcome': 'sent'},
                'chromium': {'target_id': 'TAB2', 'message': 'M2',
                             'outcome': 'sent'},
            }}
            # Plain harness: Chromium is fill, so only Brave counts.
            self.assertEqual(
                harness.delayed_targets(results, ['brave', 'chromium']),
                [('brave', 'TAB1', 'M1')])
            # Aborted-routing has a target id but no message: out.
            aborted = {'browsers': {
                'brave': {'target_id': 'TAB1',
                          'outcome': 'aborted-routing'},
            }}
            self.assertEqual(
                harness.delayed_targets(aborted, ['brave']), [])
            # already-sent still counts as an attempted send.
            already = {'browsers': {
                'brave': {'target_id': 'TAB1', 'message': 'M1',
                          'outcome': 'already-sent'},
            }}
            self.assertEqual(
                harness.delayed_targets(already, ['brave']),
                [('brave', 'TAB1', 'M1')])
            # Split harness: Chromium is set_value too, so both count.
            split = s2_flip_live.Harness(
                tmp, 0, chromium_set_value=True)
            self.assertEqual(
                split.delayed_targets(results, ['brave', 'chromium']),
                [('brave', 'TAB1', 'M1'), ('chromium', 'TAB2', 'M2')])
            # No browser attempted: empty list, no sleep, no key.
            self.assertEqual(
                harness.delayed_targets(aborted, ['brave', 'chromium']),
                [])
            # Normalization and dedupe, like program_variant_label:
            # ' Brave ' and a repeated browser count once, with the
            # normalized name in the returned tuple.
            self.assertEqual(
                harness.delayed_targets(
                    results, [' Brave ', 'brave', 'chromium']),
                [('brave', 'TAB1', 'M1')])
            # results None is an empty result, not an error.
            self.assertEqual(
                harness.delayed_targets(None, ['brave']), [])

    def test_cli_maps_set_value_flags(self):
        # CLI mapping, LOW: --set-value and --chromium-set-value
        # must reach the Harness. Harness.run is replaced so no
        # SSH runs; the spy records the Harness kwargs.
        with tempfile.TemporaryDirectory() as tmp:
            created = {}
            real_harness = s2_flip_live.Harness

            class _SpyHarness(real_harness):
                def __init__(self, *args, **kwargs):
                    created.update(kwargs)
                    super().__init__(*args, **kwargs)

                def run(self, browsers):
                    created['browsers'] = list(browsers)
                    return {'wall_ms': 1.0, 'browsers': {}}

            with patch.object(s2_flip_live, 'Harness', _SpyHarness):
                rc = s2_flip_live.main(['--run', '1', '--set-value',
                                        '--workdir', tmp])
            self.assertEqual(rc, 0)
            self.assertEqual(created.get('program_variant'), 'set_value')
            self.assertFalse(created.get('chromium_set_value'))
            self.assertEqual(created.get('browsers'),
                             ['brave', 'chromium'])
            created.clear()
            with patch.object(s2_flip_live, 'Harness', _SpyHarness):
                rc = s2_flip_live.main(['--run', '2',
                                        '--chromium-set-value',
                                        '--workdir', tmp])
            self.assertEqual(rc, 0)
            self.assertEqual(created.get('program_variant'), 'fill')
            self.assertTrue(created.get('chromium_set_value'))
            self.assertEqual(created.get('browsers'),
                             ['brave', 'chromium'])

    def test_program_variant_label_only_lists_run_browsers(self):
        # Label: plain is brave=set_value,chromium=fill, split is
        # brave=set_value,chromium=set_value. A Chromium-only run
        # records only chromium, not Brave.
        with tempfile.TemporaryDirectory() as tmp:
            plain = s2_flip_live.Harness(tmp, 0)
            self.assertEqual(
                plain.program_variant_label(['brave', 'chromium']),
                'brave=set_value,chromium=fill')
            self.assertEqual(
                plain.program_variant_label(['chromium']),
                'chromium=fill')
            self.assertNotIn(
                'brave', plain.program_variant_label(['chromium']))
            split = s2_flip_live.Harness(
                tmp, 0, chromium_set_value=True)
            self.assertEqual(
                split.program_variant_label(['brave', 'chromium']),
                'brave=set_value,chromium=set_value')
            # Normalization and dedupe: ' Brave ' and a repeated
            # browser must not write a wrong label.
            self.assertEqual(
                plain.program_variant_label(
                    [' Brave ', 'brave', 'chromium']),
                'brave=set_value,chromium=fill')
            self.assertEqual(plain.program_variant_label([]), '')

    def test_invalid_program_variant_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'program_variant'):
                s2_flip_live.Harness(tmp, 0, program_variant='teleport')

    def test_variant_for_unknown_browser_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = s2_flip_live.Harness(tmp, 0)
            with self.assertRaisesRegex(ValueError, 'unknown browser'):
                harness.variant_for('firefox')
            # Normalization: case and surrounding space are accepted.
            self.assertEqual(harness.variant_for(' Brave '), 'set_value')
            self.assertEqual(harness.variant_for('CHROMIUM'), 'fill')

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

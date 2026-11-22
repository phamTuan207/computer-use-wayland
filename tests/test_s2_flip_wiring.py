"""S2 flip wiring tests (step 6).

Covers the two wiring changes that make the one-class flip possible:
1. cu.py code-exec --endpoint (P3 port split): a program aimed at
   Brave on [::1]:9223 must not silently drive Chromium on
   127.0.0.1:9223. The override applies to that program only and the
   retained default is restored afterwards.
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
                                  'http://[::1]:9223', '--program', '-')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)['ok'], True)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(self.fake.calls[0]['endpoint'], 'http://[::1]:9223')
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

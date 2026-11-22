"""A1 pilot Layer-1 preflight tests (interpreter side, no browser).

Proves the preflight guarantee from improvements/a1-code-exec-dom-design.md
section 7: a bad ref anywhere in a dom_act list, including in the MIDDLE,
refuses the WHOLE batch before any backend call, so no partial effect can
happen. Covers every ref-taking action type the pilot uses: click, fill,
set_value, assert. Runs on FakeDomBackend; the live adapter layer is the
Layer-2 probe (tests/realistic/a1-pilot/preflight-probe.py), run at resume.

No em dash or en dash in this file.
"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'code_exec', ROOT / 'scripts' / 'code_exec.py')
code_exec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(code_exec)

# Reuse the fake backend from the existing suite without importing the
# test module (importing it would collect its tests). Minimal copy here.
import time  # noqa: E402


class FakeDomBackend:
    """DOM stand-in; records calls, never starts Chromium or a broker."""

    def __init__(self):
        self.dom_calls = []
        self.snapshot_count = 0

    def dom_start(self):
        self.dom_calls.append(('start',))
        return {'ok': True, 'endpoint': 'http://127.0.0.1:9222',
                'reused': True}

    def dom_tabs(self):
        self.dom_calls.append(('tabs',))
        return [{'id': 'tab-1', 'title': 'fixture',
                 'url': 'file:///fixture'}]

    def _snapshot(self, target):
        self.snapshot_count += 1
        number = self.snapshot_count
        return {
            'snapshot': 'dom-snapshot-%d' % number,
            'title': 'fixture', 'url': 'file:///fixture',
            'elements': [{'ref': 'dom-ref-%d' % number,
                          'role': 'button', 'name': 'Show result'}],
            'truncated': False, 'iframes': 0,
        }

    def dom_observe(self, target, scope, max_elements):
        self.dom_calls.append(('observe', target, scope, max_elements))
        return self._snapshot(target)

    def dom_act(self, target, snapshot, actions, after_scope=None,
                no_after=False):
        self.dom_calls.append(
            ('act', target, snapshot, actions, after_scope, no_after))
        result = {'ok': True, 'completed': len(actions)}
        if no_after:
            result['after_skipped'] = True
        else:
            result['after'] = self._snapshot(target)
        return result

    def dom_assert(self, target, snapshot, action):
        self.dom_calls.append(('assert', target, snapshot, action))
        return {'ok': True}


def _act_calls(backend):
    return [c for c in backend.dom_calls if c[0] == 'act']


class PreflightMidListTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeDomBackend()
        self.session = code_exec.CodeExecSession(self.backend)
        self.snapshot = self.session.api_dom_observe('tab-1')
        self.good_ref = self.snapshot['elements'][0]['ref']
        self.assertEqual(self.good_ref, 'dom-ref-1')

    def _bind(self, actions):
        # CB-2: DOM actions carry scope (the tab target) and the
        # observation id of the bound snapshot. Binding is checked
        # before the ref check, so a bad ref with a correct binding
        # still reaches the ref refusal these tests pin.
        return [dict(a, scope='tab-1',
                     observation_id=self.snapshot['snapshot'])
                for a in actions]

    def _assert_no_backend_act(self):
        self.assertEqual(_act_calls(self.backend), [],
                         'backend dom_act must never be called on refusal')

    def test_bad_ref_mid_list_click(self):
        actions = [
            {'type': 'click', 'ref': self.good_ref},
            {'type': 'click', 'ref': 'dom-ref-BAD'},
            {'type': 'click', 'ref': self.good_ref},
        ]
        with self.assertRaisesRegex(
                code_exec.CodeExecError, 'not present in the bound snapshot'):
            self.session.api_dom_act(self.snapshot, self._bind(actions))
        self._assert_no_backend_act()

    def test_bad_ref_mid_list_fill(self):
        actions = [
            {'type': 'fill', 'ref': self.good_ref, 'text': '2026-11-16'},
            {'type': 'fill', 'ref': 'dom-ref-BAD', 'text': 'Widget'},
            {'type': 'fill', 'ref': self.good_ref, 'text': '12'},
        ]
        with self.assertRaisesRegex(
                code_exec.CodeExecError, 'not present in the bound snapshot'):
            self.session.api_dom_act(self.snapshot, self._bind(actions))
        self._assert_no_backend_act()

    def test_bad_ref_mid_list_set_value(self):
        actions = [
            {'type': 'set_value', 'ref': self.good_ref, 'text': 'a'},
            {'type': 'set_value', 'ref': 'dom-ref-BAD', 'text': 'b'},
            {'type': 'set_value', 'ref': self.good_ref, 'text': 'c'},
        ]
        with self.assertRaisesRegex(
                code_exec.CodeExecError, 'not present in the bound snapshot'):
            self.session.api_dom_act(self.snapshot, self._bind(actions))
        self._assert_no_backend_act()

    def test_bad_ref_mid_list_assert(self):
        actions = [
            {'type': 'click', 'ref': self.good_ref},
            {'type': 'assert', 'ref': 'dom-ref-BAD', 'text': 'pick4-ok'},
            {'type': 'click', 'ref': self.good_ref},
        ]
        with self.assertRaisesRegex(
                code_exec.CodeExecError, 'not present in the bound snapshot'):
            self.session.api_dom_act(self.snapshot, self._bind(actions))
        self._assert_no_backend_act()

    def test_bad_ref_as_first_and_last_action(self):
        for bad_pos in (0, 2):
            actions = [
                {'type': 'click', 'ref': self.good_ref},
                {'type': 'click', 'ref': self.good_ref},
                {'type': 'click', 'ref': self.good_ref},
            ]
            actions[bad_pos] = {'type': 'click', 'ref': 'dom-ref-BAD'}
            with self.subTest(bad_pos=bad_pos), self.assertRaisesRegex(
                    code_exec.CodeExecError,
                    'not present in the bound snapshot'):
                self.session.api_dom_act(self.snapshot, self._bind(actions))
        self._assert_no_backend_act()

    def test_all_valid_refs_reach_backend(self):
        # Positive control: the same shape with all valid refs succeeds,
        # so the refusals above are not vacuously passing.
        actions = [
            {'type': 'click', 'ref': self.good_ref},
            {'type': 'fill', 'ref': self.good_ref, 'text': 'x'},
            {'type': 'click', 'ref': self.good_ref},
        ]
        result = self.session.api_dom_act(self.snapshot, self._bind(actions))
        self.assertTrue(result['ok'])
        self.assertEqual(len(_act_calls(self.backend)), 1)

    def test_dom_assert_bad_ref_never_calls_backend(self):
        with self.assertRaisesRegex(
                code_exec.CodeExecError, 'not present in the bound snapshot'):
            self.session.api_dom_assert(
                self.snapshot, ref='dom-ref-BAD', text='pick4-ok')
        self._assert_no_backend_act()


if __name__ == '__main__':
    unittest.main()

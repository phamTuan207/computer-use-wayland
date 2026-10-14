"""Offline table-driven batch validation: every malformed batch is refused whole.

A valid first click is always followed by the malformed entry, so a regression that
validates lazily would dispatch input before refusing.
"""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
_spec = importlib.util.spec_from_file_location('cu', ROOT / 'scripts/cu.py')
cu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cu)

CLICK = {'type': 'click', 'x': 10, 'y': 20}
POINTER = {'type': 'click', 'x': 1.0, 'y': 2.5}

DESKTOP_BAD = [
    ('boolean x', {'type': 'click', 'x': True, 'y': 20}),
    ('boolean y', {'type': 'click', 'x': 10, 'y': False}),
    ('string x', {'type': 'click', 'x': '10', 'y': 20}),
    ('missing y', {'type': 'click', 'x': 10}),
    ('object x', {'type': 'click', 'x': {}, 'y': 20}),
    ('nan y', {'type': 'move', 'x': 1, 'y': float('nan')}),
    ('boolean scroll dx', {'type': 'scroll', 'x': 1, 'y': 1, 'dx': True}),
    ('boolean scroll dy', {'type': 'scroll', 'x': 1, 'y': 1, 'dy': True}),
    ('string scroll dy', {'type': 'scroll', 'x': 1, 'y': 1, 'dy': '5'}),
    ('drag three points', {'type': 'drag', 'from': [1, 2, 3], 'to': [4, 5]}),
    ('drag short point', {'type': 'drag', 'from': [1], 'to': [4, 5]}),
    ('drag boolean', {'type': 'drag', 'from': [1, True], 'to': [4, 5]}),
    ('drag not a list', {'type': 'drag', 'from': 'x', 'to': [4, 5]}),
    ('drag fractional ms', {'type': 'drag', 'from': [1, 2], 'to': [4, 5], 'ms': 300.5}),
    ('boolean repeat', {'type': 'key', 'keys': ['a'], 'repeat': True}),
    ('boolean hold_ms', {'type': 'key', 'keys': ['a'], 'hold_ms': True}),
    ('boolean delay_ms', {'type': 'type', 'text': 'hi', 'delay_ms': True}),
    ('boolean wait ms', {'type': 'wait', 'ms': True}),
    ('unhashable type', {'type': []}),
    ('huge integer', {'type': 'scroll', 'dy': 10**1000, 'x': 1, 'y': 1}),
    ('unknown action', {'type': 'typo'}),
    ('not an object', 'click'),
]

BROWSER_BAD = [
    ('unhashable type', {'type': []}),
    ('huge integer', {'type': 'scroll', 'dy': 10**1000, 'x': 1, 'y': 1}),
    ('unknown action', {'type': 'typo'}),
    ('non-object action', 5),
    ('boolean dy', {'type': 'scroll', 'dy': True}),
    ('string dx', {'type': 'scroll', 'dy': 1, 'dx': 'bad'}),
    ('object x', {'type': 'scroll', 'dy': 1, 'x': {}}),
    ('string y', {'type': 'scroll', 'dy': 1, 'y': '1'}),
    ('missing dy', {'type': 'scroll', 'x': 1, 'y': 1}),
    ('numeric ref', {'type': 'click', 'ref': 1}),
    ('object selector', {'type': 'click', 'selector': {'a': 1}}),
    ('empty ref', {'type': 'click', 'ref': '   '}),
    ('both locators', {'type': 'click', 'ref': 'e1', 'selector': '#a'}),
    ('numeric key', {'type': 'key', 'keys': [1]}),
    ('keys not a list', {'type': 'key', 'keys': 'a'}),
    ('empty text', {'type': 'set_value', 'ref': 'e1', 'text': 5}),
    ('oversized text', {'type': 'fill', 'ref': 'e1', 'text': 'x' * 10001}),
    ('object assert value', {'type': 'assert', 'ref': 'e1', 'value': {}}),
    ('numeric assert text', {'type': 'assert', 'ref': 'e1', 'text': 7}),
    ('string checked', {'type': 'assert', 'ref': 'e1', 'checked': 'yes'}),
    ('string timeout', {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': 'soon'}),
    ('object timeout', {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': {}}),
    ('bool timeout', {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': True}),
    ('negative timeout', {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': -1}),
    ('wait out of range', {'type': 'wait', 'ms': 99999}),
]

BROWSER_GOOD = [
    {'type': 'click', 'selector': '#a'},
    {'type': 'scroll', 'dy': 30},
    {'type': 'scroll', 'dy': 30, 'dx': -1.5, 'x': 10.5, 'y': 20.5},
    {'type': 'key', 'keys': ['ctrl', 'a']},
    {'type': 'set_value', 'ref': 'e1', 'text': ''},
    {'type': 'fill', 'ref': 'e1', 'text': 'x' * 10000},
    {'type': 'assert', 'ref': 'e1', 'text': ''},
    {'type': 'assert', 'ref': 'e1', 'checked': False},
    {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': 0},
    {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': 3000},
    {'type': 'assert', 'ref': 'e1', 'text': 'x', 'timeout_ms': 9000},
    {'type': 'wait', 'ms': 2000},
]

DESKTOP_GOOD = [
    {'type': 'click', 'x': 10, 'y': 20},
    {'type': 'click', 'x': 10.5, 'y': 20.5, 'button': 'right'},
    {'type': 'move', 'x': 1, 'y': 2},
    {'type': 'drag', 'from': [1, 2], 'to': [4, 5], 'ms': 300},
    {'type': 'scroll', 'x': 1, 'y': 2, 'dx': -1.5, 'dy': 30},
    {'type': 'key', 'keys': ['ctrl', 'a'], 'repeat': 2, 'hold_ms': 50},
    {'type': 'type', 'text': 'hi', 'delay_ms': 0},
    {'type': 'wait', 'ms': 0},
]


class BatchSchemaTests(unittest.TestCase):
    def _refuse(self, backend, first, bad):
        with self.assertRaises(ValueError, msg=f'{backend} accepted {bad}'):
            if backend=='desktop':
                from unittest import mock
                with mock.patch.object(cu,'check_cancel'),mock.patch.object(cu,'focus') as focus, \
                     mock.patch.object(cu,'Pointer') as pointer:
                    try:cu.desktop_act({}, {'backend':'desktop','created':__import__('time').time()}, [first,bad])
                    finally:focus.assert_not_called();pointer.assert_not_called()
            else:cu.validate_actions([first, bad], backend)

    def test_desktop_rejects_every_malformed_batch_before_input(self):
        for label, bad in DESKTOP_BAD:
            with self.subTest(case=label):
                self._refuse('desktop', dict(CLICK), bad)

    def test_browser_rejects_every_malformed_batch_before_input(self):
        for label, bad in BROWSER_BAD:
            with self.subTest(case=label):
                self._refuse('browser', {'type': 'click', 'selector': '#a'}, bad)

    def test_legitimate_batches_still_pass(self):
        for action in DESKTOP_GOOD:
            with self.subTest(desktop=action):
                cu.validate_actions([action], 'desktop')
        for action in BROWSER_GOOD:
            with self.subTest(browser=action):
                cu.validate_actions([action], 'browser')

    def test_batch_shape_is_bounded(self):
        for actions in ([], [CLICK] * 33):
            with self.subTest(count=len(actions)):
                with self.assertRaises(ValueError):
                    cu.validate_actions(actions, 'desktop')


class AdapterContractTests(unittest.TestCase):
    """Execute the production Node adapter instead of inspecting its text.

    The transport, envelope and handshake behaviour lives in tests/cdp_errors.mjs,
    which drives scripts/cdp.mjs under a native-API-only fake WebSocket.
    """

    def test_production_adapter_error_paths_pass(self):
        import shutil
        import subprocess
        node=shutil.which('node')
        if node is None:
            self.skipTest('node is required for the CDP adapter checks')
        result=subprocess.run([node,str(ROOT/'tests/cdp_errors.mjs')],
                              capture_output=True,text=True,timeout=180,cwd=str(ROOT))
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)



if __name__ == '__main__':
    unittest.main()

"""Offline window discovery: opt-in filters over the unchanged default JSON shape."""
import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).resolve().parents[1] / 'scripts/cu.py'
spec = importlib.util.spec_from_file_location('cu', path)
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)

CLIENTS = [
    {'address': '0x1', 'class': 'firefox', 'title': 'Inbox', 'at': [0, 0],
     'size': [800, 600], 'workspace': {'id': 1}, 'floating': False, 'pid': 100},
    {'address': '0x2', 'class': 'Firefox', 'title': 'Second', 'at': [10, 20],
     'size': [640, 480], 'workspace': {'id': 2}, 'pid': 200},
    {'address': '0x3', 'class': 'kitty', 'title': 'shell', 'at': [0, 0],
     'size': [400, 200], 'workspace': {'id': 1}, 'pid': 300},
]
DEFAULT_KEYS = ['address', 'class', 'title', 'at', 'size', 'workspace']


class WindowsCommand(unittest.TestCase):
    """One mocked clients call per invocation; no focus, no input, no caching."""

    def windows(self, *args):
        calls = []
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['cu', 'windows', *args]), \
                patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', side_effect=lambda env, what: (
                    calls.append(what) or (CLIENTS if what == 'clients' else []))), \
                contextlib.redirect_stdout(stream):
            cu.main()
        return json.loads(stream.getvalue()), calls

    def test_default_output_shape_is_unchanged(self):
        result, calls = self.windows()
        self.assertEqual(calls, ['clients'], 'exactly one hypr clients call')
        self.assertEqual([list(item) for item in result], [DEFAULT_KEYS] * 3)
        self.assertEqual(result[0], {'address': '0x1', 'class': 'firefox', 'title': 'Inbox',
                                     'at': [0, 0], 'size': [800, 600],
                                     'workspace': {'id': 1}})

    def test_class_filter_is_exact_case_sensitive_and_not_a_substring(self):
        for wanted, expected in (('firefox', ['0x1']), ('Firefox', ['0x2']),
                                 ('fire', []), ('firefox.*', []), ('KITTY', []),
                                 ('', [])):
            with self.subTest(wanted=wanted):
                result, calls = self.windows('--class', wanted)
                self.assertEqual([item['address'] for item in result], expected)
                self.assertEqual(calls, ['clients'], 'no extra compositor call')

    def test_no_titles_omits_only_the_title_key(self):
        result, calls = self.windows('--no-titles')
        self.assertEqual(calls, ['clients'])
        self.assertEqual([list(item) for item in result],
                         [['address', 'class', 'at', 'size', 'workspace']] * 3)
        self.assertNotIn('title', result[0])

    def test_both_flags_are_independently_usable_together(self):
        result, calls = self.windows('--class', 'kitty', '--no-titles')
        self.assertEqual(calls, ['clients'])
        self.assertEqual(result, [{'address': '0x3', 'class': 'kitty', 'at': [0, 0],
                                   'size': [400, 200], 'workspace': {'id': 1}}])

    def test_unmatched_class_is_an_empty_list_not_an_error(self):
        result, calls = self.windows('--class', 'nothing-here')
        self.assertEqual(result, [])
        self.assertEqual(calls, ['clients'])

    def test_filtering_never_selects_a_first_window_implicitly(self):
        duplicate = {**CLIENTS[0], 'address': '0x4'}
        with patch(__name__+'.CLIENTS', CLIENTS+[duplicate]):
            result, calls = self.windows('--class', 'firefox')
        self.assertEqual([item['address'] for item in result], ['0x1', '0x4'])
        self.assertEqual(calls, ['clients'])

    def test_window_lookup_compares_hex_address_case_insensitively(self):
        with patch.object(cu, 'hypr', return_value=[{'address':'0xab'}]):
            self.assertEqual(cu.window({}, '0xAB')['address'], '0xab')


if __name__ == '__main__':
    unittest.main()

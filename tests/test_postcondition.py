#!/usr/bin/env python3
"""Unit tests for A4 deterministic postcondition verification.

No broker, no screenshot, no model call: every backend is a fake.
"""
import hashlib
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'postcondition', ROOT / 'scripts' / 'postcondition.py')
postcondition = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(postcondition)


def _read_bytes_for(files):
    def read_bytes(path):
        if path not in files:
            raise FileNotFoundError(path)
        return files[path]
    return read_bytes


def _windows_for(windows):
    def list_windows():
        return list(windows)
    return list_windows


def _dom_for(elements):
    def dom_observe(target, scope, max_elements):
        return {'snapshot': 'snap-1', 'title': 'fixture',
                'url': 'file:///fixture', 'elements': elements}
    return dom_observe


class ValidateTests(unittest.TestCase):
    def test_empty_spec_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks([])

    def test_unknown_kind_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks([{'kind': 'vibes', 'path': '/tmp/x'}])

    def test_relative_path_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'file_exists', 'path': 'relative/x'}])

    def test_bad_sha_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'file_sha256', 'path': '/tmp/x', 'sha256': 'zz'}])

    def test_window_needs_a_field(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks([{'kind': 'window_present'}])

    def test_window_absent_rejects_address(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'window_absent', 'address': '0xabc'}])

    def test_too_many_checks_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'file_exists', 'path': '/tmp/x'}] * 17)

    def test_dom_text_needs_target_and_text(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'dom_text', 'target': 'tab-1'}])
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.validate_checks(
                [{'kind': 'dom_text', 'text': 'hi'}])


class FileCheckTests(unittest.TestCase):
    def setUp(self):
        self.content = 'Ý tưởng 1: app nhắc uống nước.\n'.encode('utf-8')
        self.digest = hashlib.sha256(self.content).hexdigest()
        self.files = {'/tmp/y-tuong.txt': self.content}
        self.read_bytes = _read_bytes_for(self.files)

    def test_file_contains_verifies(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_contains', 'path': '/tmp/y-tuong.txt',
              'text': 'Ý tưởng 1'}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'verified')
        self.assertTrue(verdict['ok'])
        self.assertFalse(verdict['needs_vision'])
        self.assertIn(self.digest, verdict['checks'][0]['detail'])
        self.assertNotIn('uống nước', verdict['checks'][0]['detail']
                         .replace('Ý tưởng 1', ''))

    def test_file_contains_wrong_text_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_contains', 'path': '/tmp/y-tuong.txt',
              'text': 'no such line'}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'failed')
        self.assertFalse(verdict['ok'])
        self.assertFalse(verdict['needs_vision'])
        self.assertEqual(verdict['failed'], ['file_contains'])

    def test_missing_file_fails_not_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_contains', 'path': '/tmp/nope.txt',
              'text': 'x'}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'failed')

    def test_file_sha256_alone_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_sha256', 'path': '/tmp/y-tuong.txt',
              'sha256': self.digest}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertTrue(verdict['needs_vision'])
        self.assertEqual(verdict['passed'], ['file_sha256'])

    def test_file_sha256_plus_contains_verifies(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_sha256', 'path': '/tmp/y-tuong.txt',
              'sha256': self.digest},
             {'kind': 'file_contains', 'path': '/tmp/y-tuong.txt',
              'text': 'Ý tưởng 1'}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'verified')

    def test_file_sha256_mismatch_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_sha256', 'path': '/tmp/y-tuong.txt',
              'sha256': '0' * 64}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'failed')

    def test_file_exists_alone_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/y-tuong.txt'}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertTrue(verdict['needs_vision'])

    def test_file_equals_verifies(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_equals', 'path': '/tmp/y-tuong.txt',
              'sha256': self.digest}],
            read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'verified')

    def test_two_different_kinds_verify_without_exact_proof(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/y-tuong.txt'},
             {'kind': 'window_present', 'class': 'kitty'}],
            read_bytes=self.read_bytes,
            list_windows=_windows_for(
                [{'address': '0xabc', 'class': 'kitty', 'title': 'term'}]))
        self.assertEqual(verdict['status'], 'verified')

    def test_no_file_backend_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_contains', 'path': '/tmp/y-tuong.txt',
              'text': 'x'}])
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertIn('no file backend', verdict['checks'][0]['detail'])

    def test_paired_file_checks_helper(self):
        checks = postcondition.paired_file_checks('/tmp/y-tuong.txt',
                                                  'Ý tưởng 1')
        verdict = postcondition.verify_postconditions(
            checks, read_bytes=self.read_bytes)
        self.assertEqual(verdict['status'], 'verified')
        self.assertEqual(len(verdict['checks']), 2)

    def test_real_temp_file_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(pathlib.Path(tmp) / 'out.txt')
            pathlib.Path(path).write_bytes(self.content)
            verdict = postcondition.verify_postconditions(
                [{'kind': 'file_contains', 'path': path,
                  'text': 'Ý tưởng 1'}],
                read_bytes=lambda p: pathlib.Path(p).read_bytes())
            self.assertEqual(verdict['status'], 'verified')


class DirectoryCheckTests(unittest.TestCase):
    def test_directory_exists_via_dir_backend(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/hoc-ky-2/dsa',
              'directory': True}],
            read_bytes=_read_bytes_for({}),
            dir_exists=lambda p: p == '/tmp/hoc-ky-2/dsa')
        self.assertEqual(verdict['status'], 'inconclusive')
        # One directory check alone is a single supporting signal, so
        # the pairing rule keeps it inconclusive; two dirs verify.
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/hoc-ky-2/dsa',
              'directory': True},
             {'kind': 'file_exists', 'path': '/tmp/hoc-ky-2/ktvm',
              'directory': True}],
            read_bytes=_read_bytes_for({}),
            dir_exists=lambda p: p in ('/tmp/hoc-ky-2/dsa',
                                       '/tmp/hoc-ky-2/ktvm'))
        self.assertEqual(verdict['status'], 'verified')

    def test_directory_missing_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/hoc-ky-2/dsa',
              'directory': True},
             {'kind': 'file_contains', 'path': '/tmp/x', 'text': 'y'}],
            read_bytes=_read_bytes_for({'/tmp/x': b'y'}),
            dir_exists=lambda p: False)
        self.assertEqual(verdict['status'], 'failed')

    def test_directory_without_backend_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/hoc-ky-2/dsa',
              'directory': True},
             {'kind': 'file_contains', 'path': '/tmp/x', 'text': 'y'}],
            read_bytes=_read_bytes_for({'/tmp/x': b'y'}))
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertTrue(verdict['needs_vision'])
        self.assertIn('no directory backend',
                      verdict['checks'][0]['detail'])


class WindowCheckTests(unittest.TestCase):
    def setUp(self):
        self.windows = [
            {'address': '0xabc', 'class': 'kitty', 'title': 'term'},
            {'address': '0xdef', 'class': 'chromium', 'title': 'about:blank'},
        ]

    def test_window_class_plus_title_verifies(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_present', 'class': 'kitty', 'title': 'term'}],
            list_windows=_windows_for(self.windows))
        self.assertEqual(verdict['status'], 'verified')
        self.assertEqual(
            verdict['checks'][0]['matched_fields'], ['class', 'title'])

    def test_window_class_only_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_present', 'class': 'kitty'}],
            list_windows=_windows_for(self.windows))
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertTrue(verdict['needs_vision'])

    def test_window_absent_verifies_with_second_kind(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_absent', 'class': 'firefox'},
             {'kind': 'window_present', 'class': 'kitty', 'title': 'term'}],
            list_windows=_windows_for(self.windows))
        self.assertEqual(verdict['status'], 'verified')

    def test_window_present_missing_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_present', 'class': 'firefox',
              'title': 'nope'}],
            list_windows=_windows_for(self.windows))
        self.assertEqual(verdict['status'], 'failed')

    def test_window_absent_present_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_absent', 'class': 'kitty'}],
            list_windows=_windows_for(self.windows))
        self.assertEqual(verdict['status'], 'failed')

    def test_backend_error_fails_closed(self):
        def boom():
            raise RuntimeError('hyprctl down')
        verdict = postcondition.verify_postconditions(
            [{'kind': 'window_present', 'class': 'kitty', 'title': 'term'}],
            list_windows=boom)
        self.assertEqual(verdict['status'], 'failed')
        self.assertIn('hyprctl down', verdict['checks'][0]['detail'])


class DomCheckTests(unittest.TestCase):
    def test_dom_text_found_verifies(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'dom_text', 'target': 'tab-1', 'text': 'Show result'}],
            dom_observe=_dom_for(
                [{'ref': 'r1', 'role': 'button', 'name': 'Show result'}]))
        self.assertEqual(verdict['status'], 'verified')

    def test_dom_text_missing_fails(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'dom_text', 'target': 'tab-1', 'text': 'Nope'}],
            dom_observe=_dom_for(
                [{'ref': 'r1', 'role': 'button', 'name': 'Show result'}]))
        self.assertEqual(verdict['status'], 'failed')

    def test_dom_without_backend_is_inconclusive(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'dom_text', 'target': 'tab-1', 'text': 'Show result'}])
        self.assertEqual(verdict['status'], 'inconclusive')


class VerdictShapeTests(unittest.TestCase):
    def test_empty_list_is_inconclusive_not_crash(self):
        verdict = postcondition.verify_postconditions([])
        self.assertEqual(verdict['status'], 'inconclusive')
        self.assertTrue(verdict['needs_vision'])
        self.assertIn('error', verdict)

    def test_non_list_raises(self):
        with self.assertRaises(postcondition.PostconditionError):
            postcondition.verify_postconditions({'kind': 'file_exists'})

    def test_elapsed_ms_present(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_exists', 'path': '/tmp/x'}],
            read_bytes=_read_bytes_for({'/tmp/x': b''}))
        self.assertIsInstance(verdict['elapsed_ms'], float)
        self.assertGreaterEqual(verdict['elapsed_ms'], 0)

    def test_failed_check_names_listed(self):
        verdict = postcondition.verify_postconditions(
            [{'kind': 'file_contains', 'name': 'ideas', 'path': '/tmp/x',
              'text': 'missing'}],
            read_bytes=_read_bytes_for({'/tmp/x': b'other'}))
        self.assertEqual(verdict['failed'], ['ideas'])
        self.assertEqual(verdict['passed'], [])


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Unit tests for the A3 procedure library minimal core.

No broker, no execution: register/retrieve/quarantine only, with
fake postcondition backends.
"""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

SPEC = importlib.util.spec_from_file_location(
    'procedure_library', ROOT / 'scripts' / 'procedure_library.py')
procedure_library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(procedure_library)

PROGRAM = (
    'wins = windows()\n'
    'term = [w for w in wins if w["title"] == "speed-pick1-term"][0]\n'
    'obs = observe(window=term["address"])\n'
    'result = act([{"type": "type", "text": "df -h /\\n"}], obs)\n'
    'verify = observe(window=term["address"])\n'
    'assert_state(result["ok"], "act failed")\n'
    'verify_image = verify["image"]\n'
)
CHECKS = [{'kind': 'file_contains', 'path': '/tmp/y-tuong.txt',
           'text': 'Ý tưởng 1'}]


class KeyTests(unittest.TestCase):
    def test_key_is_deterministic(self):
        first = procedure_library.procedure_key(
            'kitty', 'kitty', ['type', 'type'], '800x600')
        second = procedure_library.procedure_key(
            'kitty', 'kitty', ['type', 'type'], '800x600')
        self.assertEqual(first, second)

    def test_key_changes_with_verbs(self):
        base = procedure_library.procedure_key(
            'kitty', 'kitty', ['type'], '800x600')
        other = procedure_library.procedure_key(
            'kitty', 'kitty', ['type', 'type'], '800x600')
        self.assertNotEqual(base, other)

    def test_key_rejects_empty_verbs(self):
        with self.assertRaises(procedure_library.ProcedureError):
            procedure_library.procedure_key('kitty', 'kitty', [], '')


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lib = procedure_library.ProcedureLibrary(
            state_dir=self.tmp.name)
        self.key = procedure_library.procedure_key(
            'kitty', 'kitty', ['type'], '800x600')

    def test_register_then_retrieve_exact(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        record = self.lib.retrieve(self.key)
        self.assertIsNotNone(record)
        self.assertEqual(record['program'], PROGRAM)
        self.assertEqual(record['name'], 'df in terminal')

    def test_retrieve_missing_is_none(self):
        self.assertIsNone(self.lib.retrieve('no|such|key'))

    def test_register_rejects_import_program(self):
        with self.assertRaises(ValueError):
            self.lib.register(key=self.key, name='bad',
                              program='import os\n', checks=CHECKS)

    def test_register_rejects_bad_checks(self):
        with self.assertRaises(ValueError):
            self.lib.register(key=self.key, name='bad',
                              program=PROGRAM,
                              checks=[{'kind': 'vibes'}])

    def test_register_rejects_empty_program(self):
        with self.assertRaises(procedure_library.ProcedureError):
            self.lib.register(key=self.key, name='bad', program='  ',
                              checks=CHECKS)

    def test_store_survives_reload(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        reloaded = procedure_library.ProcedureLibrary(
            state_dir=self.tmp.name)
        record = reloaded.retrieve(self.key)
        self.assertIsNotNone(record)
        self.assertEqual(record['name'], 'df in terminal')

    def test_store_file_is_private(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        mode = (pathlib.Path(self.tmp.name)
                / 'procedures.json').stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)

    def test_corrupt_store_loads_empty(self):
        (pathlib.Path(self.tmp.name) / 'procedures.json').write_text(
            '{not json', encoding='utf-8')
        lib = procedure_library.ProcedureLibrary(state_dir=self.tmp.name)
        self.assertIsNone(lib.retrieve(self.key))
        self.assertEqual(lib.list_procedures(), [])

    def test_two_failures_quarantine(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        self.assertFalse(self.lib.record_result(self.key, passed=False))
        self.assertIsNotNone(self.lib.retrieve(self.key))
        self.assertTrue(self.lib.record_result(self.key, passed=False))
        self.assertTrue(self.lib.is_quarantined(self.key))
        self.assertIsNone(self.lib.retrieve(self.key))

    def test_success_resets_failure_count(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        self.lib.record_result(self.key, passed=False)
        self.lib.record_result(self.key, passed=True)
        self.assertFalse(self.lib.record_result(self.key, passed=False))
        self.assertIsNotNone(self.lib.retrieve(self.key))

    def test_quarantine_survives_reload(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        self.lib.record_result(self.key, passed=False)
        self.lib.record_result(self.key, passed=False)
        reloaded = procedure_library.ProcedureLibrary(
            state_dir=self.tmp.name)
        self.assertTrue(reloaded.is_quarantined(self.key))
        self.assertIsNone(reloaded.retrieve(self.key))

    def test_reregister_clears_quarantine(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        self.lib.record_result(self.key, passed=False)
        self.lib.record_result(self.key, passed=False)
        self.assertIsNone(self.lib.retrieve(self.key))
        self.lib.register(key=self.key, name='df in terminal v2',
                          program=PROGRAM, checks=CHECKS)
        self.assertIsNotNone(self.lib.retrieve(self.key))

    def test_checkpoint_verified_counts_as_pass(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        verdict = self.lib.checkpoint(
            self.key,
            read_bytes=lambda p: 'Ý tưởng 1: x\n'.encode('utf-8'))
        self.assertEqual(verdict['status'], 'verified')
        record = self.lib.retrieve(self.key)
        self.assertEqual(record['successes'], 1)
        self.assertEqual(record['uses'], 1)

    def test_checkpoint_failed_quarantines_after_two(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        read_bytes = lambda p: b'other content\n'
        first = self.lib.checkpoint(self.key, read_bytes=read_bytes)
        self.assertEqual(first['status'], 'failed')
        self.assertIsNotNone(self.lib.retrieve(self.key))
        second = self.lib.checkpoint(self.key, read_bytes=read_bytes)
        self.assertEqual(second['status'], 'failed')
        self.assertIsNone(self.lib.retrieve(self.key))

    def test_checkpoint_unknown_key_is_none(self):
        self.assertIsNone(self.lib.checkpoint('no|key'))

    def test_record_unknown_key_is_false(self):
        self.assertFalse(self.lib.record_result('no|key', passed=False))

    def test_list_procedures(self):
        self.lib.register(key=self.key, name='df in terminal',
                          program=PROGRAM, checks=CHECKS)
        rows = self.lib.list_procedures()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['key'], self.key)


if __name__ == '__main__':
    unittest.main()

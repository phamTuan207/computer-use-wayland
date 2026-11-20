import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import jsonlutil


class AppendJsonlTests(unittest.TestCase):
    def test_append_creates_parseable_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'records.jsonl'
            jsonlutil.append_jsonl(path, {'a': 1})
            jsonlutil.append_jsonl(path, {'b': 2})
            self.assertEqual(jsonlutil.verify_jsonl(path), [])
            lines = path.read_text(encoding='utf-8').splitlines()
            self.assertEqual([json.loads(line) for line in lines], [{'a': 1}, {'b': 2}])

    def test_append_repairs_missing_trailing_newline(self):
        # G24: the exact corruption mode. A previous writer left a partial
        # last line; the new record must start on its own line, not glue.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'records.jsonl'
            path.write_bytes(b'{"a": 1}')
            jsonlutil.append_jsonl(path, {'b': 2})
            self.assertEqual(jsonlutil.verify_jsonl(path), [])
            self.assertEqual([json.loads(line) for line in
                              path.read_text(encoding='utf-8').splitlines()],
                             [{'a': 1}, {'b': 2}])

    def test_append_after_terminated_file_adds_no_blank_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'records.jsonl'
            path.write_bytes(b'{"a": 1}\n')
            jsonlutil.append_jsonl(path, {'b': 2})
            self.assertEqual(path.read_bytes(), b'{"a": 1}\n{"b":2}\n')

    def test_verify_reports_glued_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'records.jsonl'
            path.write_bytes(b'{"a": 1}\n{"b": 2}{"c": 3}\n')
            self.assertEqual(jsonlutil.verify_jsonl(path), [2])

    def test_verify_empty_file_is_clean(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'records.jsonl'
            path.write_bytes(b'')
            self.assertEqual(jsonlutil.verify_jsonl(path), [])


class EnsureTrailingNewlineFdTests(unittest.TestCase):
    def _fd_case(self, initial):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / 'log.jsonl'
        path.write_bytes(initial)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        return path, fd

    def test_writes_separator_when_missing(self):
        path, fd = self._fd_case(b'{"a": 1}')
        self.assertTrue(jsonlutil.ensure_trailing_newline_fd(fd, path))
        self.assertEqual(path.read_bytes(), b'{"a": 1}\n')

    def test_no_separator_when_terminated(self):
        path, fd = self._fd_case(b'{"a": 1}\n')
        self.assertFalse(jsonlutil.ensure_trailing_newline_fd(fd, path))
        self.assertEqual(path.read_bytes(), b'{"a": 1}\n')

    def test_no_separator_when_empty(self):
        path, fd = self._fd_case(b'')
        self.assertFalse(jsonlutil.ensure_trailing_newline_fd(fd, path))
        self.assertEqual(path.read_bytes(), b'')


if __name__ == '__main__':
    unittest.main()

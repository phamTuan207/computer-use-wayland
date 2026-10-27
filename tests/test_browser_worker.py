"""Private worker transport tests with owned Python children; no browser or GUI."""
from contextlib import ExitStack
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import browser_worker
import cu
import session_driver

REAL_POPEN = subprocess.Popen
ECHO = '''import json, sys
for line in sys.stdin:
    print(json.dumps(json.loads(line), ensure_ascii=False), flush=True)
'''


class WorkerTransport(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.children = []
        self.code = ECHO
        self.spawn = self.stack.enter_context(patch.object(browser_worker.subprocess, 'Popen',
                                                         side_effect=self.start_child))
        self.cancel = self.stack.enter_context(patch.object(cu, 'check_cancel'))
        self.timeout = self.stack.enter_context(patch.object(cu, 'browser_timeout', return_value=5))
        self.worker = browser_worker.BrowserWorker()
        self.addCleanup(self.worker.close)
        self.addCleanup(self.reap_children)

    def start_child(self, argv, **kwargs):
        self.assertEqual(argv[-1], '--worker')
        self.assertNotIn('start_new_session', kwargs)
        # stderr is inherited, never DEVNULL: the bridge starts the driver with
        # fd 2 on its private session stderr log, so worker diagnostics reach
        # that same log without a per-worker file or a pipe to drain.
        self.assertIsNone(kwargs['stderr'])
        child = REAL_POPEN([sys.executable, '-u', '-c', self.code], **kwargs)
        self.children.append(child)
        return child

    def reap_children(self):
        # Test failures must not leave even a fixture child alive.
        self.worker.close()
        for child in self.children:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=2)
            for stream in (child.stdin, child.stdout):
                if stream is not None and not stream.closed:
                    stream.close()

    def assert_closed(self):
        self.assertTrue(self.worker.closed)
        self.assertIsNone(self.worker.process)
        for child in self.children:
            self.assertIsNotNone(child.poll())
            self.assertTrue(child.stdin.closed)
            self.assertTrue(child.stdout.closed)

    def assert_no_replay(self):
        calls = self.spawn.call_count
        with self.assertRaisesRegex(RuntimeError, 'worker ended'):
            self.worker.request({'operation': 'observe'})
        self.assertEqual(self.spawn.call_count, calls)
        self.assert_closed()

    def test_worker_stderr_flows_to_inherited_parent_stderr(self):
        # Bridge chain proof: the bridge opens one private session stderr log
        # and the driver inherits it as fd 2, so the worker child must inherit
        # that same fd instead of DEVNULL. Redirect this process's fd 2 into an
        # owned log file for the spawn window; the fixture child writes a
        # marker to its inherited fd 2 and it must land in the log.
        log = tempfile.TemporaryFile()
        try:
            saved = os.dup(2)
            try:
                os.dup2(log.fileno(), 2)
                self.code = ('import os, sys\n'
                             'sys.stdin.readline()\n'
                             'os.write(2, b"worker-stderr-marker\\n")\n'
                             'print(\'{"fixture": true}\', flush=True)\n')
                self.assertEqual(self.worker.request({}), {'fixture': True})
            finally:
                os.dup2(saved, 2)
                os.close(saved)
            log.seek(0)
            self.assertIn(b'worker-stderr-marker', log.read())
        finally:
            log.close()

    def test_two_requests_share_one_lazy_child_and_close_on_eof(self):
        self.spawn.assert_not_called()
        for request in ({'text': 'Tiếng Việt 🐱'}, {'sequence': 2}):
            self.assertEqual(self.worker.request(request), request)
        self.spawn.assert_called_once()
        child = self.children[0]
        self.assertIsNone(child.poll())
        self.assertEqual(os.getpgid(child.pid),os.getpgid(os.getpid()))
        self.worker.close()
        self.worker.close()
        self.assertEqual(child.returncode, 0)
        self.assert_no_replay()

    def test_malformed_response_is_fatal_without_replay(self):
        self.code = "import sys; sys.stdin.readline(); print('not JSON', flush=True)"
        with self.assertRaises(json.JSONDecodeError):
            self.worker.request({})
        self.assert_no_replay()

    def test_error_json_closes_child_without_replay(self):
        self.code = "import sys; sys.stdin.readline(); print('{\"ok\":false,\"error\":\"fixture\"}', flush=True)"
        self.assertEqual(self.worker.request({}), {'ok': False, 'error': 'fixture'})
        self.assert_no_replay()

    def test_child_death_is_fatal_without_replay(self):
        self.code = 'import os; os._exit(7)'
        with self.assertRaises((BrokenPipeError, RuntimeError)):
            self.worker.request({})
        self.assert_no_replay()

    def test_slow_child_times_out_and_is_reaped(self):
        self.code = 'import time; time.sleep(10)'
        self.timeout.return_value = .2
        with self.assertRaisesRegex(RuntimeError, 'timed out'):
            self.worker.request({})
        self.assert_no_replay()

    def cancel_after(self, count):
        checks = 0
        def check():
            nonlocal checks
            checks += 1
            if checks >= count:
                raise RuntimeError('cancelled fixture')
        self.cancel.side_effect = check

    def test_cancellation_while_reading_closes_child(self):
        self.code = 'import sys, time; sys.stdin.readline(); time.sleep(10)'
        self.cancel_after(5)
        with self.assertRaisesRegex(RuntimeError, 'cancelled fixture'):
            self.worker.request({})
        self.cancel.side_effect = None
        self.assert_no_replay()

    def test_cancellation_during_blocked_large_write_closes_child(self):
        self.code = 'import time; time.sleep(10)'
        self.cancel_after(6)
        with self.assertRaisesRegex(RuntimeError, 'cancelled fixture'):
            self.worker.request({'text': 'x' * (2 * 1024 * 1024)})
        self.cancel.side_effect = None
        self.assert_no_replay()

    def test_oversized_request_rejected_before_spawn(self):
        with patch.object(browser_worker.json, 'dumps', return_value='x' * (32 * 1024 * 1024)):
            with self.assertRaisesRegex(ValueError, 'request exceeds 32 MiB'):
                self.worker.request({})
        self.spawn.assert_not_called()
        self.assertIsNone(self.worker.process)

    def test_cancellation_before_next_request_reaps_existing_child(self):
        self.worker.request({'sequence':1})
        self.cancel.side_effect=RuntimeError('cancelled fixture')
        with self.assertRaisesRegex(RuntimeError,'cancelled fixture'):
            self.worker.request({'sequence':2})
        self.cancel.side_effect=None
        self.assert_no_replay()

    def test_oversized_response_closes_child_without_replay(self):
        self.code="import sys; sys.stdin.readline(); sys.stdout.write('x' * (33 * 1024 * 1024)); sys.stdout.flush()"
        with self.assertRaisesRegex(RuntimeError,'response exceeds 32 MiB'):
            self.worker.request({})
        self.assert_no_replay()

    def test_large_response_with_split_utf8_and_newline(self):
        self.code = r'''import json, os, sys
sys.stdin.readline()
raw = json.dumps({'text': 'Tiếng Việt 🐱', 'image_base64': 'x' * (20 * 1024 * 1024)}, ensure_ascii=False).encode() + b'\n'
for start in range(0, len(raw), 65535):
    chunk = memoryview(raw)[start:start + 65535]
    while chunk:
        chunk = chunk[os.write(1, chunk):]
'''
        real_read = os.read
        reads = 0
        def fragmented_read(fd, size):
            nonlocal reads
            reads += 1
            return real_read(fd, 1 if reads <= 64 else size)
        with patch.object(browser_worker.os, 'read', side_effect=fragmented_read):
            result = self.worker.request({})
        self.assertEqual(result['text'], 'Tiếng Việt 🐱')
        self.assertEqual(len(result['image_base64']), 20 * 1024 * 1024)
        self.worker.close()
        self.assert_closed()

    def test_partial_eof_and_invalid_framing_are_fatal(self):
        for response in ('{', '{}\n{}\n', '{}\nextra', 'null\n'):
            with self.subTest(response=response):
                self.worker = browser_worker.BrowserWorker()
                self.code = f'import os, sys; sys.stdin.readline(); os.write(1, {response.encode()!r})'
                with self.assertRaises(RuntimeError):
                    self.worker.request({})
                self.assert_no_replay()

    def test_relay_restores_browser_and_closes_worker_on_finish_eof_and_error(self):
        original = cu.browser
        for ending in ('finish', 'eof', 'exception', 'bad_json'):
            with self.subTest(ending=ending):
                self.worker = browser_worker.BrowserWorker()
                def execute(args, data):
                    self.assertIs(cu.browser.__self__, self.worker)
                    self.assertEqual(cu.browser({'text': 'fixture'}), {'text': 'fixture'})
                    if ending == 'exception':
                        raise RuntimeError('execute fixture')
                    return subprocess.CompletedProcess(args, 0, '{"ok":true}', '')
                lines = '{"args":["browser","observe"]}\n'
                if ending == 'finish':
                    lines += '{"args":["finish"]}\n'
                elif ending == 'bad_json':
                    lines += 'not JSON\n'
                with patch.object(browser_worker, 'BrowserWorker', return_value=self.worker), \
                     patch.object(session_driver, 'execute', side_effect=execute):
                    if ending in ('exception', 'bad_json'):
                        with self.assertRaises((RuntimeError, json.JSONDecodeError)):
                            session_driver.relay(io.StringIO(lines), io.StringIO())
                    else:
                        self.assertEqual(session_driver.relay(io.StringIO(lines), io.StringIO()), 0)
                self.assertIs(cu.browser, original)
                self.assert_closed()


if __name__ == '__main__':
    unittest.main()

"""Report, workspace and CLI checks with mocks; no browser or GUI input."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import browser_task_benchmark as benchmark


class BrowserTaskHarnessTests(unittest.TestCase):
    def test_failed_checkpoint_preserves_last_complete_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'report.json'
            previous = {'ok': False, 'samples': [{'ok': False}]}
            benchmark.write_report(previous, path)
            with patch.object(benchmark.json, 'dump', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    benchmark.write_report({'ok': True}, path)
            self.assertEqual(json.loads(path.read_text()), previous)
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_incomplete_checkpoint_survives_process_kill(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'report.json'
            code = ('import sys,time;from pathlib import Path;'
                    'from browser_task_benchmark import write_report;'
                    'write_report({"ok":False,"samples":[{"mode":"batch","ok":False}]},Path(sys.argv[1]));'
                    'print("saved",flush=True);time.sleep(10)')
            child = subprocess.Popen([sys.executable, '-c', code, str(path)],
                                     cwd=Path(benchmark.__file__).parent,
                                     stdout=subprocess.PIPE, text=True)
            try:
                import select
                self.assertTrue(select.select([child.stdout], [], [], 3)[0])
                self.assertEqual(child.stdout.readline().strip(), 'saved')
                child.kill()
                child.wait(timeout=3)
                saved = json.loads(path.read_text())
                self.assertFalse(saved['ok'])
                self.assertFalse(saved['samples'][0]['ok'])
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=3)
                child.stdout.close()

    def test_cleanup_error_keeps_rows_and_failed_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'nested/report.json'
            rows = [{'mode': 'batch', 'ok': True, 'total_ms': 12},
                    {'mode': 'split', 'ok': False}]
            report = {'tasks_ok': True, 'samples': rows}
            with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                benchmark.finish_report(report, path, Mock(side_effect=RuntimeError('cleanup failed')))
            saved = json.loads(path.read_text())
            self.assertFalse(saved['ok'])
            self.assertFalse(saved['cleanup_ok'])
            self.assertEqual(saved['samples'], rows)
            self.assertEqual(saved['summary']['batch']['samples'], 1)
            self.assertNotIn('split', saved['summary'])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_cleanup_success_cannot_hide_task_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            report = {'samples': []}
            def cleanup():
                report['cleanup_ok'] = True
            benchmark.finish_report(report, Path(folder)/'report.json', cleanup)
            self.assertFalse(report['ok'])
            report['tasks_ok'] = True
            benchmark.finish_report(report, Path(folder)/'report.json', cleanup)
            self.assertTrue(report['ok'])

    def test_workspace_wait_checks_actual_transition(self):
        cu = Mock()
        cu.run.side_effect = ['{"id": 1}', '{"id": 2}']
        with patch.object(benchmark.time, 'sleep'):
            benchmark.wait_workspace(cu, {}, 2)
        self.assertEqual(cu.run.call_count, 2)
        self.assertEqual(cu.check_cancel.call_count, 2)

    def test_workspace_timeout_and_cancel_never_dispatch(self):
        cu = Mock()
        cu.run.return_value = '{"id": 1}'
        with patch.object(benchmark.time, 'monotonic', side_effect=[0, 1]):
            with self.assertRaisesRegex(RuntimeError, 'transition timed out'):
                benchmark.wait_workspace(cu, {}, 2, timeout=.1)
        cu.reset_mock()
        cu.check_cancel.side_effect = RuntimeError('cancelled')
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            benchmark.wait_workspace(cu, {}, 2)
        cu.run.assert_not_called()

    def test_cleanup_continues_after_resource_errors(self):
        root = Path(benchmark.__file__).resolve().parents[1]
        sys.path.insert(0, str(root/'scripts'))
        import cu
        import browser_worker
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            report_path = Path(folder)/'report.json'
            args = SimpleNamespace(cli=root/'scripts/cu.py', report=report_path,
                                   samples=3, delay=16, modes=['split', 'batch'], cold=False,
                                   controls=0)
            stack.enter_context(patch.object(cu, 'require_session'))
            stack.enter_context(patch.object(cu, 'environment', return_value={}))
            stack.enter_context(patch.object(cu, 'check_cancel'))
            stack.enter_context(patch.object(cu, 'hypr', side_effect=lambda _env, what:
                                              {} if what == 'activewindow' else []))
            def command(argv, _env):
                if argv[1] == '-j':
                    return '{"id": 1}'
                raise RuntimeError('setup failed')
            stack.enter_context(patch.object(cu, 'run', side_effect=command))
            worker = stack.enter_context(patch.object(browser_worker, 'BrowserWorker')).return_value
            worker.close.side_effect = RuntimeError('worker close failed')
            server = stack.enter_context(patch.object(benchmark, 'ThreadingHTTPServer')).return_value
            server.shutdown.side_effect = RuntimeError('shutdown failed')
            thread = stack.enter_context(patch.object(benchmark.threading, 'Thread')).return_value
            thread.is_alive.return_value = False
            with self.assertRaisesRegex(RuntimeError, 'setup failed'):
                benchmark.run(args)
            saved = json.loads(report_path.read_text())
            self.assertFalse(saved['ok'])
            self.assertEqual(saved['cleanup_errors'], ['worker_close', 'server_shutdown'])
            self.assertEqual(saved['delay_ms'], 16)
            self.assertEqual(saved['modes'], ['split', 'batch'])
            self.assertEqual(saved['phase'], 'warm')
            self.assertEqual(saved['provenance'], 'source_tree')
            self.assertEqual(set(saved['runtime_sha256']), {'cu.py', 'browser_worker.py', 'cdp.mjs'})
            self.assertNotIn(str(root), report_path.read_text())
            server.server_close.assert_called_once()
            thread.join.assert_called_once_with(timeout=2)

    def test_invalid_cli_bounds_before_session(self):
        for args in (['--samples', '0'], ['--samples', '31'], ['--delay', '17'],
                     ['--cold'], ['--cold', '--samples', '1'],
                     ['--cold', '--samples', '2', '--modes', 'batch']):
            with self.subTest(args=args), patch.object(sys, 'argv',
                    ['browser_task_benchmark', '--report', 'unused.json', *args]), \
                    patch.object(benchmark.subprocess, 'run') as launch, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    benchmark.main()
                self.assertEqual(error.exception.code, 2)
                launch.assert_not_called()

    def test_summary_covers_every_selected_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            report = {'modes': ['batch', 'batch-no-after'], 'samples': [
                {'mode': 'batch', 'ok': True, 'total_ms': 10},
                {'mode': 'batch-no-after', 'ok': True, 'total_ms': 6},
                {'mode': 'split', 'ok': True, 'total_ms': 4},  # present but not selected
                {'mode': 'batch-no-after', 'ok': False},
            ]}
            def cleanup():
                report['cleanup_ok'] = True
            benchmark.finish_report(report, Path(folder)/'report.json', cleanup)
            self.assertEqual(list(report['summary']), ['batch', 'batch-no-after'])
            self.assertEqual(report['summary']['batch-no-after']['samples'], 1)
            self.assertNotIn('split', report['summary'])

    def test_controls_bound_is_checked_before_session(self):
        for value in ('-1', '1001', '1.5'):
            with self.subTest(value=value), patch.object(sys, 'argv',
                    ['browser_task_benchmark', '--report', 'unused.json', '--controls', value]), \
                    patch.object(benchmark.subprocess, 'run') as launch, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    benchmark.main()
                self.assertEqual(error.exception.code, 2)
                launch.assert_not_called()

    def test_controls_add_inert_inputs_without_touching_the_page(self):
        self.assertEqual(benchmark.page(0).count(b'<input'), 1)
        built = benchmark.page(1000)
        self.assertEqual(built.count(b'<input disabled aria-hidden="true">'), 1000)
        self.assertIn(b'id="name"', built)
        self.assertIn(b'id="save"', built)
        self.assertIn(b'id="status"', built)

    def test_worker_startup_failure_still_reaps_server_and_thread(self):
        # The owned resources exist from the server call on, so a failure creating the
        # worker must still shut the server down and leave a written report behind.
        root = Path(benchmark.__file__).resolve().parents[1]
        sys.path.insert(0, str(root/'scripts'))
        import cu
        import browser_worker
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            report_path = Path(folder)/'report.json'
            args = SimpleNamespace(cli=root/'scripts/cu.py', report=report_path,
                                   samples=1, delay=0, modes=['batch'], cold=False, controls=0)
            for name, value in (('require_session', mock.Mock()), ('environment', mock.Mock(return_value={})),
                                ('check_cancel', mock.Mock())):
                stack.enter_context(mock.patch.object(cu, name, new=value))
            stack.enter_context(patch.object(cu, 'hypr', side_effect=lambda _e, w:
                                              {} if w == 'activewindow' else []))
            stack.enter_context(patch.object(cu, 'run', return_value='{"id": 1}'))
            stack.enter_context(patch.object(browser_worker, 'BrowserWorker',
                                             mock.Mock(side_effect=RuntimeError('worker start failed'))))
            server = stack.enter_context(patch.object(benchmark, 'ThreadingHTTPServer')).return_value
            thread = stack.enter_context(patch.object(benchmark.threading, 'Thread')).return_value
            thread.is_alive.return_value = False
            with self.assertRaisesRegex(RuntimeError, 'worker start failed'):
                benchmark.run(args)
            saved = json.loads(report_path.read_text())
            self.assertFalse(saved['ok'])
            self.assertTrue(saved['cleanup_ok'])
            self.assertNotIn('worker_close', saved['cleanup_errors'])
            server.shutdown.assert_called_once()
            thread.join.assert_called_once_with(timeout=2)

    def test_cli_help_runs_without_a_session(self):
        out = io.StringIO()
        with patch.object(sys, 'argv', ['browser_task_benchmark', '--help']), redirect_stdout(out):
            with self.assertRaises(SystemExit) as error:
                benchmark.main()
        self.assertEqual(error.exception.code, 0)
        for flag in ('--modes', '--controls', '--samples', '--report'):
            self.assertIn(flag, out.getvalue())
        self.assertIn('task-full', out.getvalue())
        self.assertIn('task-scoped', out.getvalue())

    def test_task_modes_do_not_mix_with_legacy_modes(self):
        for argv in (['--modes', 'task-full', 'batch'],
                     ['--modes', 'split', 'task-scoped'],
                     ['--modes', 'task-full', 'task-scoped', 'batch-no-after']):
            with self.subTest(argv=argv), patch.object(sys, 'argv',
                    ['browser_task_benchmark', '--report', 'unused.json', *argv]), \
                    patch.object(benchmark.subprocess, 'run') as launch, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    benchmark.main()
                self.assertEqual(error.exception.code, 2)
                launch.assert_not_called()

    def test_task_family_summary_and_legacy_default(self):
        with tempfile.TemporaryDirectory() as folder:
            report = {'modes': ['task-full', 'task-scoped'], 'samples': [
                {'mode': 'task-full', 'ok': True, 'total_ms': 12},
                {'mode': 'task-scoped', 'ok': True, 'total_ms': 8},
            ]}
            def cleanup():
                report['cleanup_ok'] = True
            benchmark.finish_report(report, Path(folder)/'report.json', cleanup)
            self.assertEqual(list(report['summary']), ['task-full', 'task-scoped'])
            self.assertEqual(report['summary']['task-scoped']['samples'], 1)

    def test_ref_selection_requires_a_unique_semantic_label(self):
        elements = [{'ref': 'e1', 'role': 'input', 'name': 'Task name'},
                    {'ref': 'e2', 'role': 'input', 'name': 'Task name'}]
        with self.assertRaisesRegex(RuntimeError, 'matched 2 controls'):
            benchmark.pick_ref(elements, 'input', 'Task name')
        self.assertEqual(benchmark.pick_ref(elements[:1], 'input', 'Task name'), 'e1')
        with self.assertRaisesRegex(RuntimeError, 'matched 0 controls'):
            benchmark.pick_ref(elements[:1], 'button', 'Save fixture')

    def test_task_sample_stops_before_input_when_refs_are_missing(self):
        worker = Mock()
        worker.request.return_value = {'snapshot': 's', 'elements': []}
        row = {'mode': 'task-scoped', 'index': 0, 'ok': False, 'calls': 0, 'result_bytes': 0}
        with self.assertRaisesRegex(RuntimeError, "matched 0 controls"):
            benchmark.task_sample({'endpoint': 'e', 'target': 't'}, worker, row, 'task-scoped',
                                  'payload', {}, Mock())
        self.assertEqual(worker.request.call_count, 1, 'only the observe may run')
        self.assertFalse(row['ok'])
        self.assertNotIn('total_ms', row)

    def test_task_sample_two_calls_refs_and_whole_task_timer(self):
        worker = Mock()
        observe = {'snapshot': 's', 'elements': [
            {'ref': 'e1', 'role': 'input', 'name': 'Task name'},
            {'ref': 'e2', 'role': 'button', 'name': 'Save fixture'},
            ]}
        posted = {}
        def request(payload):
            if payload['operation'] == 'observe':
                posted['scope'] = payload.get('scope')
                posted['max_elements'] = payload['max_elements']
                return observe
            posted['act'] = payload
            return {'ok': True, 'after_skipped': True, 'completed': 3}
        worker.request.side_effect = request
        state = {}
        original = benchmark.time.sleep
        benchmark.time.sleep = lambda _s: state.update(text='payload')
        try:
            row = {'mode': 'task-scoped', 'index': 0, 'ok': False, 'calls': 0, 'result_bytes': 0}
            benchmark.task_sample({'endpoint': 'e', 'target': 't'}, worker, row, 'task-scoped',
                                  'payload', state, Mock())
        finally:
            benchmark.time.sleep = original
        self.assertEqual(worker.request.call_count, 2, 'observe plus exactly one act')
        self.assertEqual(posted['scope'], '#task')
        self.assertEqual(posted['max_elements'], 80)
        self.assertIs(posted['act']['no_after'], True)
        # The snapshot never enumerates <p>, so only the two real controls take
        # refs and the status assert keeps its known selector.
        self.assertEqual(posted['act']['actions'],
                         [{'type': 'set_value', 'ref': 'e1', 'text': 'payload'},
                          {'type': 'click', 'ref': 'e2'},
                          {'type': 'assert', 'selector': '#status', 'text': 'Saved payload',
                           'timeout_ms': 1000}])
        self.assertTrue(row['ok'])
        self.assertEqual(row['calls'], 2)
        self.assertGreaterEqual(row['total_ms'], row['observe_ms'])

    def test_task_sample_requires_after_skipped(self):
        worker = Mock()
        observe = {'snapshot': 's', 'elements': [
            {'ref': 'e1', 'role': 'input', 'name': 'Task name'},
            {'ref': 'e2', 'role': 'button', 'name': 'Save fixture'},
            ]}
        worker.request.side_effect = [observe, {'ok': True, 'after': {'elements': []}}]
        row = {'mode': 'task-full', 'index': 0, 'ok': False, 'calls': 0, 'result_bytes': 0}
        with self.assertRaisesRegex(RuntimeError, 'did not skip'):
            benchmark.task_sample({'endpoint': 'e', 'target': 't'}, worker, row, 'task-full',
                                  'payload', {}, Mock())
        self.assertFalse(row['ok'])

    def test_task_fixture_wraps_targets_in_a_unique_root(self):
        legacy = benchmark.page(3)
        scoped = benchmark.page(3, task=True)
        self.assertEqual(legacy.count(b'<div id="task">'), 0, 'legacy fixture unchanged')
        self.assertEqual(scoped.count(b'<div id="task">'), 1)
        self.assertIn(b'aria-label="Task name"', scoped)
        self.assertEqual(scoped.count(b'/ready'), 1, 'the ready barrier is kept')
        self.assertEqual(scoped.count(b'<input disabled aria-hidden="true">'), 3)

if __name__ == '__main__':
    unittest.main()

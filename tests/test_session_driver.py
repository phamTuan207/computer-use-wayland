import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import session_driver


class Driver(unittest.TestCase):
    def test_json_result_is_not_double_encoded(self):
        output=io.StringIO()
        with patch.object(session_driver,'execute',return_value=subprocess.CompletedProcess([],0,'{"ok":true,"text":"Tiếng Việt"}','')):
            session_driver.relay(io.StringIO('{"args":["status"]}'),output)
        response=json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(response['result']['text'],'Tiếng Việt')
        self.assertNotIn('stdout',response)
        self.assertNotIn('stderr',response)

    def test_multiple_commands_preserve_process_and_stdin(self):
        lines=[{'args':['status']}, {'args':['act','--actions','-'],'stdin':'[]'}, {'args':['finish']}]
        output=io.StringIO()
        with patch.object(session_driver,'execute',return_value=subprocess.CompletedProcess([],0,'{}','')) as run:
            result=session_driver.relay(io.StringIO('\n'.join(map(json.dumps,lines))),output)
        self.assertEqual(result,0)
        self.assertEqual(run.call_count,2)
        self.assertEqual(run.call_args.args,(['act','--actions','-'],'[]'))
        self.assertEqual(json.loads(output.getvalue().splitlines()[-1])['driver'],'finished')

    def test_error_stops_without_replaying_or_next_command(self):
        with patch.object(session_driver,'execute',return_value=subprocess.CompletedProcess([],1,'failed','')) as run:
            result=session_driver.relay(io.StringIO('{"args":["status"]}\n{"args":["doctor"]}\n'),io.StringIO())
        self.assertEqual(result,1)
        run.assert_called_once()

    def test_eof_finishes_without_detaching(self):
        self.assertEqual(session_driver.relay(io.StringIO(),io.StringIO()),0)

    def test_invalid_requests_never_execute(self):
        requests=[[],{}, {'args':['resume']}, {'args':['session']}, {'args':['status'],'stdin':4}, {'args':[4]}]
        for request in requests:
            with self.subTest(request=request),patch.object(session_driver,'execute') as run:
                with self.assertRaises(ValueError):
                    session_driver.relay(io.StringIO(json.dumps(request)),io.StringIO())
                run.assert_not_called()

    def test_execute_restores_streams_and_stops_on_exception(self):
        import cu
        argv,stdin=sys.argv,sys.stdin
        with patch.object(cu,'main',side_effect=RuntimeError('injected')),patch.object(cu,'stop_session_on_error') as stop:
            result=session_driver.execute(['status'],'payload')
        self.assertEqual(result.returncode,1)
        self.assertIn('injected',json.loads(result.stdout)['error'])
        stop.assert_called_once()
        self.assertIs(sys.argv,argv)
        self.assertIs(sys.stdin,stdin)

    def test_execute_argparse_exit_preserves_exit_status(self):
        import cu
        with patch.object(cu,'main',side_effect=SystemExit(2)),patch.object(cu,'stop_session_on_error') as stop:
            result=session_driver.execute(['status','--invalid'],'')
        self.assertEqual(result.returncode,2)
        stop.assert_called_once()

    def test_execute_real_status_never_forks_cli(self):
        with patch.object(session_driver.subprocess,'run',side_effect=AssertionError('unexpected process')):
            result=session_driver.execute(['status'],'')
        self.assertEqual(result.returncode,0)
        self.assertIn('cancelled',json.loads(result.stdout))


class DoctorCliTests(unittest.TestCase):
    """N3: optional fcitx probes degrade to ime_error; doctor still succeeds."""

    MONITORS = [{'name': 'm', 'width': 100, 'height': 100, 'scale': 1, 'transform': 0}]

    def execute_doctor(self, which=None, run=None):
        import cu
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch.object(cu, 'environment', return_value={}))
            stack.enter_context(patch.object(cu, 'hypr', return_value=list(self.MONITORS)))
            present = (which or {}).get('fcitx5-remote', True)
            stack.enter_context(patch.object(cu.shutil, 'which', side_effect=lambda name: '/bin/' + name if (name != 'fcitx5-remote' or present) else None))
            run_mock = stack.enter_context(patch.object(cu, 'run', side_effect=run))
            stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
            import session_driver
            result = session_driver.execute(['doctor'], '')
        return result, run_mock, stop

    def payload(self, result):
        return json.loads(result.stdout)

    def test_remote_absent_runs_no_probe(self):
        result, run_mock, stop = self.execute_doctor(which={'fcitx5-remote': False}, run=[])
        self.assertEqual(result.returncode, 0)
        run_mock.assert_not_called()
        body = self.payload(result)
        self.assertIn('monitors', body)
        self.assertNotIn('ime', body)
        self.assertNotIn('ime_error', body)
        stop.assert_not_called()

    def test_remote_success_keeps_schema(self):
        calls = []

        def fake_run(argv, env=None, timeout=None):
            calls.append((argv, timeout))
            return '  value  ' if argv == ['fcitx5-remote'] else 'name'

        result, _, stop = self.execute_doctor(run=fake_run)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls, [(['fcitx5-remote'], 1), (['fcitx5-remote', '-n'], 1)])
        body = self.payload(result)
        self.assertEqual(body['ime'], {'state': 'value', 'name': 'name'})
        self.assertNotIn('ime_error', body)
        stop.assert_not_called()

    def test_probe_failures_degrade_to_bounded_single_line_error(self):
        import subprocess
        failures = [
            RuntimeError('first down'),
            OSError('no such binary'),
            subprocess.TimeoutExpired('fcitx5-remote', 1),
        ]
        for error in failures:
            with self.subTest(error=type(error).__name__):
                def fake_run(argv, env=None, timeout=None):
                    raise error
                result, _, stop = self.execute_doctor(run=fake_run)
                self.assertEqual(result.returncode, 0)
                body = self.payload(result)
                self.assertNotIn('ime', body, 'no partial ime payload')
                self.assertIn('ime_error', body)
                self.assertNotIn('\n', body['ime_error'])
                self.assertLessEqual(len(body['ime_error']), 400)
                self.assertIn('dependencies', body)
                self.assertIn('monitors', body)
                stop.assert_not_called()

    def test_second_probe_failure_after_first_success(self):
        def fake_run(argv, env=None, timeout=None):
            if argv == ['fcitx5-remote']:
                return '1'
            raise RuntimeError('name query down')
        result, _, stop = self.execute_doctor(run=fake_run)
        self.assertEqual(result.returncode, 0)
        body = self.payload(result)
        self.assertNotIn('ime', body)
        self.assertIn('name query down', body['ime_error'])
        stop.assert_not_called()

    def test_first_failure_skips_second_probe(self):
        calls = []

        def fake_run(argv, env=None, timeout=None):
            calls.append(argv)
            raise RuntimeError('first down')
        self.execute_doctor(run=fake_run)
        self.assertEqual(calls, [['fcitx5-remote']])

    def test_doctor_error_then_status_stays_alive_through_relay(self):
        import cu
        import session_driver
        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', return_value=list(self.MONITORS)), \
                patch.object(cu.shutil, 'which', return_value='/bin/fcitx5-remote'), \
                patch.object(cu, 'run', side_effect=RuntimeError('probe down')), \
                patch.object(cu, 'stop_session_on_error') as stop:
            output = io.StringIO()
            code = session_driver.relay(
                io.StringIO('{"args":["doctor"]}\n{"args":["status"]}\n'), output)
        self.assertEqual(code, 0)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(responses), 3, 'ready plus two command responses')
        self.assertIn('ime_error', responses[1]['result'])
        self.assertTrue(responses[2]['result']['ok'])
        stop.assert_not_called()

    def test_unrelated_hypr_error_degrades_to_monitors_error_without_stop(self):
        import cu
        import session_driver
        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', side_effect=RuntimeError('compositor down')), \
                patch.object(cu.shutil, 'which', return_value=None), \
                patch.object(cu, 'stop_session_on_error') as stop:
            result = session_driver.execute(['doctor'], '')
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        self.assertEqual(body['monitors'], [])
        self.assertIn('monitors_error', body)
        self.assertNotIn('\n', body['monitors_error'])
        self.assertLessEqual(len(body['monitors_error']), 400)
        self.assertNotIn('ime', body)
        stop.assert_not_called()

    def test_base_exception_from_probe_is_not_converted_to_ime_error(self):
        import cu
        import session_driver
        for error in (KeyboardInterrupt(), SystemExit(3)):
            with self.subTest(error=type(error).__name__), \
                    patch.object(cu, 'environment', return_value={}), \
                    patch.object(cu, 'hypr', return_value=list(self.MONITORS)), \
                    patch.object(cu.shutil, 'which', return_value='/bin/fcitx5-remote'), \
                    patch.object(cu, 'run', side_effect=error), \
                    patch.object(cu, 'stop_session_on_error') as stop:
                result = session_driver.execute(['doctor'], '')
            self.assertNotIn('ime_error', result.stdout)
            stop.assert_called_once()

    def test_long_crlf_probe_error_is_single_line_bounded(self):
        import cu
        import session_driver
        # A >800-char multi-line probe error must collapse to one line <=400.
        long_error = ('line one\r\nline two\n' + 'x' * 500 + '\r' + 'y' * 400)
        self.assertGreater(len(long_error), 800)
        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', return_value=list(self.MONITORS)), \
                patch.object(cu.shutil, 'which', return_value='/bin/fcitx5-remote'), \
                patch.object(cu, 'run', side_effect=RuntimeError(long_error)), \
                patch.object(cu, 'stop_session_on_error') as stop:
            result = session_driver.execute(['doctor'], '')
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        self.assertNotIn('ime', body)
        error = body['ime_error']
        self.assertNotIn('\n', error)
        self.assertNotIn('\r', error)
        self.assertLessEqual(len(error), 400)
        self.assertTrue(error.startswith('fcitx5 probe failed: line one line two'))
        self.assertIn('dependencies', body)
        stop.assert_not_called()

    def test_doctor_monitors_error_variants_degrade_without_stop(self):
        import cu
        import session_driver
        variants = {
            'hypr-timeout': {'hypr': RuntimeError('compositor query timed out')},
            'malformed-monitor': {'monitors': [{'name': 'm'}]},
            'env-failure': {'env': OSError('env down')},
        }
        for name, spec in variants.items():
            with self.subTest(variant=name):
                patches = [patch.object(cu.shutil, 'which', return_value=None),
                           patch.object(cu, 'stop_session_on_error')]
                if 'env' in spec:
                    patches.insert(0, patch.object(cu, 'environment', side_effect=spec['env']))
                else:
                    patches.insert(0, patch.object(cu, 'environment', return_value={}))
                if 'hypr' in spec:
                    patches.insert(1, patch.object(cu, 'hypr', side_effect=spec['hypr']))
                else:
                    value = spec.get('monitors', list(self.MONITORS))
                    patches.insert(1, patch.object(cu, 'hypr', return_value=value))
                from contextlib import ExitStack
                with ExitStack() as stack:
                    mocks = [stack.enter_context(p) for p in patches]
                    stop = mocks[-1]
                    result = session_driver.execute(['doctor'], '')
                self.assertEqual(result.returncode, 0)
                body = json.loads(result.stdout)
                self.assertEqual(body['monitors'], [])
                self.assertIn('monitors_error', body)
                self.assertNotIn('\n', body['monitors_error'])
                self.assertLessEqual(len(body['monitors_error']), 400)
                self.assertNotIn('ime', body, 'no fabricated ime')
                self.assertIn('dependencies', body)
                self.assertIn('pointer', body)
                self.assertIn('session', body)
                stop.assert_not_called()

    def test_doctor_long_crlf_control_monitors_error_single_line_bounded(self):
        import cu
        import session_driver
        sentinel = 'SECRET-CTRL-\x00\x01-input-7319'
        long_error = ('line one\r\nline two\n' + 'x' * 800 + '\r' + sentinel + '\x00end')
        self.assertGreater(len(long_error), 800)
        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', side_effect=RuntimeError(long_error)), \
                patch.object(cu.shutil, 'which', return_value=None), \
                patch.object(cu, 'stop_session_on_error') as stop:
            result = session_driver.execute(['doctor'], '')
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        error = body['monitors_error']
        self.assertNotIn('\n', error)
        self.assertNotIn('\r', error)
        self.assertNotIn('\x00', error)
        self.assertNotIn('\x01', error)
        self.assertLessEqual(len(error), 400)
        self.assertTrue(error.startswith('monitors unavailable: line one line two'))
        stop.assert_not_called()

    def test_doctor_monitors_error_then_status_stays_alive_through_relay(self):
        import cu
        import session_driver
        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'hypr', side_effect=RuntimeError('compositor down')), \
                patch.object(cu.shutil, 'which', return_value=None), \
                patch.object(cu, 'stop_session_on_error') as stop:
            output = io.StringIO()
            code = session_driver.relay(
                io.StringIO('{"args":["doctor"]}\n{"args":["status"]}\n'), output)
        self.assertEqual(code, 0)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(responses), 3, 'ready plus two command responses')
        self.assertEqual(responses[1]['result']['monitors'], [])
        self.assertIn('monitors_error', responses[1]['result'])
        self.assertTrue(responses[2]['result']['ok'])
        stop.assert_not_called()

    def test_relay_exposes_sibling_stderr_and_stops_next_command(self):
        import session_driver
        warning = 'IME restoration failed; state may remain inactive: restore failed\n'
        first = subprocess.CompletedProcess(['act'], 1, '{"ok":false,"error":"typing failed"}',
                                            warning)
        with patch.object(session_driver, 'execute', return_value=first) as run:
            output = io.StringIO()
            code = session_driver.relay(
                io.StringIO('{"args":["act"]}\n{"args":["status"]}\n'), output)
        self.assertEqual(code, 1)
        run.assert_called_once()
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 2, 'ready line plus exactly one command response')
        response = json.loads(lines[1])
        self.assertFalse(response['result']['ok'])
        self.assertEqual(response['result']['error'], 'typing failed')
        self.assertEqual(response['stderr'], warning, 'sibling stderr is exposed')


class FullRestoreEnvelope(unittest.TestCase):
    """Item 6: production literal_keyboard -> desktop_act -> execute -> relay.

    Only the outside world is mocked (compositor, capture, input, remote);
    every layer of the envelope itself is production code.
    """

    def test_restore_only_failure_crosses_the_whole_envelope(self):
        import contextlib
        import os
        import tempfile
        import time
        from unittest.mock import patch
        from PIL import Image
        import cu
        import session_driver

        image = Image.new('RGB', (20, 20))
        meta = {'backend': 'desktop', 'created': time.time(), 'window': 'fixture',
                'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
                'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
                'monitor_transform': 0, 'image_size': [20, 20],
                'region': [0, 0, 20, 20], 'image': 'synthetic.png',
                'max_width': 1280, 'pixel_sha256': 'fixture'}
        state = ['2']

        def remote(argv, env, timeout=None):
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise RuntimeError('restore failed')
            return ''

        def hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20,
                         'height': 20, 'scale': 1}]
            if query == 'activewindow':
                return {'address': 'fixture'}
            raise AssertionError('unexpected compositor query ' + query)

        def observe(env, address, crop, max_width, **kwargs):
            if kwargs.get('persist', True):
                return dict(meta)
            return image, dict(meta)

        with tempfile.TemporaryDirectory() as folder:
            obs = Path(folder) / 'obs.json'
            obs.write_text(json.dumps(meta))
            actions = json.dumps([{'type': 'type', 'text': 'hi'}])
            token = 'a' * 32
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': token}))
                stack.enter_context(patch.object(cu, 'check_cancel'))
                stack.enter_context(patch.object(cu, 'environment', return_value={}))
                stack.enter_context(patch.object(cu, 'hypr', side_effect=hypr))
                stack.enter_context(patch.object(cu, 'focus'))
                stack.enter_context(patch.object(cu, 'window',
                                                 return_value={'at': [0, 0], 'size': [20, 20]}))
                stack.enter_context(patch.object(cu, 'observe', side_effect=observe))
                stack.enter_context(patch.object(cu, 'Pointer'))
                typed = stack.enter_context(
                    patch.object(cu, 'run_cancelable', return_value=''))
                stack.enter_context(patch.object(cu.shutil, 'which',
                                                 return_value='fake-remote'))
                stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))
                stack.enter_context(patch.object(cu, 'run', side_effect=remote))
                stack.enter_context(patch('PIL.Image.open', return_value=image))
                stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
                output = io.StringIO()
                code = session_driver.relay(
                    io.StringIO(
                        json.dumps({'args': ['act', '--observation', str(obs),
                                             '--actions', '-', '--verbose'],
                                    'stdin': actions}) + '\n' +
                        json.dumps({'args': ['status']}) + '\n'),
                    output)
        self.assertEqual(code, 1, 'the failed act stops the relay')
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 2, 'ready plus exactly one command response')
        response = json.loads(lines[1])
        self.assertFalse(response['result']['ok'])
        self.assertIn('restore failed', response['result']['error'])
        self.assertTrue(response['result']['ime_restore_failed'],
                        'cu.py:844 merges the restore flag into the result')
        self.assertEqual(response['result']['completed'], 1,
                         'acknowledged input stays counted across the envelope')
        self.assertEqual(typed.call_count, 1, 'exactly one input call, no replay')
        warning = response['stderr'].strip().splitlines()
        self.assertEqual(len(warning), 1, 'exactly one bounded sibling warning')
        self.assertLessEqual(len(warning[0]), 400)
        self.assertIn('IME restoration failed', warning[0])
        stop.assert_called_once()

    def test_primary_and_restore_failure_crosses_the_whole_envelope(self):
        import contextlib
        import os
        import tempfile
        import time
        from unittest.mock import patch
        from PIL import Image
        import cu
        import session_driver

        sentinel = 'SECRET-wtype-stderr-user-input-9152'
        image = Image.new('RGB', (20, 20))
        meta = {'backend': 'desktop', 'created': time.time(), 'window': 'fixture',
                'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
                'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
                'monitor_transform': 0, 'image_size': [20, 20],
                'region': [0, 0, 20, 20], 'image': 'synthetic.png',
                'max_width': 1280, 'pixel_sha256': 'fixture'}
        state = ['2']

        def remote(argv, env, timeout=None):
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise RuntimeError('restore failed')
            return ''

        def hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20,
                         'height': 20, 'scale': 1}]
            if query == 'activewindow':
                return {'address': 'fixture'}
            raise AssertionError('unexpected compositor query ' + query)

        def observe(env, address, crop, max_width, **kwargs):
            if kwargs.get('persist', True):
                return dict(meta)
            return image, dict(meta)

        with tempfile.TemporaryDirectory() as folder:
            obs = Path(folder) / 'obs.json'
            obs.write_text(json.dumps(meta))
            actions = json.dumps([{'type': 'type', 'text': 'first'},
                                  {'type': 'wait', 'ms': 10},
                                  {'type': 'type', 'text': 'second'}])
            token = 'b' * 32
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': token}))
                stack.enter_context(patch.object(cu, 'check_cancel'))
                stack.enter_context(patch.object(cu, 'environment', return_value={}))
                stack.enter_context(patch.object(cu, 'hypr', side_effect=hypr))
                stack.enter_context(patch.object(cu, 'focus'))
                stack.enter_context(patch.object(cu, 'window',
                                                 return_value={'at': [0, 0], 'size': [20, 20]}))
                stack.enter_context(patch.object(cu, 'observe', side_effect=observe))
                stack.enter_context(patch.object(cu, 'Pointer'))
                typed = stack.enter_context(patch.object(
                    cu, 'run_cancelable',
                    side_effect=RuntimeError('typing failed: ' + sentinel)))
                stack.enter_context(patch.object(cu.shutil, 'which',
                                                 return_value='fake-remote'))
                stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))
                stack.enter_context(patch.object(cu, 'run', side_effect=remote))
                stack.enter_context(patch('PIL.Image.open', return_value=image))
                stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
                output = io.StringIO()
                code = session_driver.relay(
                    io.StringIO(
                        json.dumps({'args': ['act', '--observation', str(obs),
                                             '--actions', '-', '--verbose'],
                                    'stdin': actions}) + '\n' +
                        json.dumps({'args': ['status']}) + '\n'),
                    output)
        self.assertEqual(code, 1, 'the failed act stops the relay')
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 2, 'ready plus exactly one command response')
        response = json.loads(lines[1])
        self.assertFalse(response['result']['ok'])
        self.assertEqual(response['result']['error'], 'typing failed: ' + sentinel,
                         'exact primary error preserved across the envelope')
        self.assertTrue(response['result']['ime_restore_failed'],
                        'cu.py:844 merges the restore flag into the result')
        self.assertEqual(response['result']['completed'], 0,
                         'failed input is never counted')
        self.assertEqual(typed.call_count, 1,
                         'first group attempted once; second group never input')
        warning = response['stderr'].strip().splitlines()
        self.assertEqual(len(warning), 1, 'exactly one bounded sibling warning')
        self.assertLessEqual(len(warning[0]), 400)
        self.assertIn('IME restoration failed', warning[0])
        self.assertNotIn(sentinel, warning[0],
                         'primary secret must not leak into the warning')
        stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()

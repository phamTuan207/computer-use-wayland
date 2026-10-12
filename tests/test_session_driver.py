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

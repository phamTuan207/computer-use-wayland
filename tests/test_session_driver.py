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
    def test_multiple_commands_preserve_process_and_stdin(self):
        lines=[{'args':['status']}, {'args':['act','--actions','-'],'stdin':'[]'}, {'args':['finish']}]
        output=io.StringIO()
        with patch.object(session_driver.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{}','')) as run:
            result=session_driver.relay(io.StringIO('\n'.join(map(json.dumps,lines))),output)
        self.assertEqual(result,0)
        self.assertEqual(run.call_count,2)
        self.assertEqual(run.call_args.kwargs['input'],'[]')
        self.assertNotIn('shell',run.call_args.kwargs)
        self.assertEqual(json.loads(output.getvalue().splitlines()[-1])['driver'],'finished')

    def test_error_stops_without_replaying_or_next_command(self):
        with patch.object(session_driver.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'failed','')) as run:
            result=session_driver.relay(io.StringIO('{"args":["status"]}\n{"args":["doctor"]}\n'),io.StringIO())
        self.assertEqual(result,1)
        run.assert_called_once()

    def test_eof_finishes_without_detaching(self):
        self.assertEqual(session_driver.relay(io.StringIO(),io.StringIO()),0)

    def test_invalid_requests_never_execute(self):
        requests=[[],{}, {'args':['resume']}, {'args':['session']}, {'args':['status'],'stdin':4}, {'args':[4]}]
        for request in requests:
            with self.subTest(request=request),patch.object(session_driver.subprocess,'run') as run:
                with self.assertRaises(ValueError):
                    session_driver.relay(io.StringIO(json.dumps(request)),io.StringIO())
                run.assert_not_called()

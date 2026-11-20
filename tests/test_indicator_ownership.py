"""Browser CLI requests must hold overlay ownership only while executing."""
from contextlib import contextmanager, nullcontext, redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu
import overlay
import session_policy


class BrowserOverlayOwnership(unittest.TestCase):
    def test_browser_cli_operations_are_bracketed_by_overlay_ownership(self):
        with tempfile.TemporaryDirectory() as folder:
            action_file = Path(folder) / 'actions.json'
            action_file.write_text('[{"type":"wait","ms":1}]')
            cases = ((['browser', 'start'], 'start'),
                     (['browser', 'tabs'], 'browser'),
                     (['browser', 'observe'], 'browser'),
                     (['browser', 'act', '--actions', str(action_file)], 'browser'))
            for args, operation_name in cases:
                self.run_case(args, operation_name)

    def run_case(self, args, operation_name):
            with self.subTest(operation=operation_name):
                events = []

                @contextmanager
                def hold(agent, method, *, env=None):
                    events.append(('acquire', agent, method, env))
                    try:
                        yield
                    finally:
                        events.append(('release', agent, method))

                def operation(*_args):
                    events.append(('operation', operation_name))
                    return {'ok': True, 'operation': operation_name}

                output = io.StringIO()
                with patch.object(sys, 'argv', ['cu.py', *args]), \
                        patch.object(cu, 'environment', return_value=
                                     {'PATH': 'fixture'} if args[1] == 'start' else None) as get_environment, \
                        patch.object(overlay, 'hold', side_effect=hold), \
                        patch.object(cu, 'browser_start', side_effect=operation), \
                        patch.object(cu, 'browser', side_effect=operation), \
                        patch.object(cu, 'locked', return_value=nullcontext()), \
                        patch.object(cu, 'require_session'), \
                        patch.object(cu, 'check_cancel'), \
                        patch.object(session_policy, 'require_observation'), \
                        patch.object(session_policy, 'complete_requirement'), \
                        patch.dict(cu.os.environ, {'CU_SESSION_TOKEN': 'a' * 32}, clear=False), \
                        redirect_stdout(output):
                    self.assertEqual(cu.main(), 0)

                self.assertEqual([event[0] for event in events],
                                 ['acquire', 'operation', 'release'])
                self.assertEqual(events[0][1:3], ('Browser automation', 'DOM/BiDi'))
                self.assertEqual(events[0][3],
                                 {'PATH': 'fixture'} if args[1] == 'start' else None)
                if args[1] == 'start':
                    get_environment.assert_called_once()
                else:
                    get_environment.assert_not_called()

    def test_broker_dom_backend_operations_acquire_browser_lease(self):
        backend = cu.CodeExecBackend({'PATH': 'fixture'})
        events = []

        @contextmanager
        def hold(agent, method, *, env=None):
            events.append(('acquire', agent, method, env))
            try:
                yield
            finally:
                events.append(('release', agent, method))

        calls = []
        with patch.object(overlay, 'hold', side_effect=hold), \
                patch.object(cu, 'browser_start', side_effect=lambda *_: calls.append('start') or {'ok': True}), \
                patch.object(cu, 'browser', side_effect=lambda request: calls.append(request['operation']) or {'ok': True}), \
                patch.object(session_policy, 'require_observation'), \
                patch.object(session_policy, 'complete_requirement'):
            self.assertTrue(backend.dom_start()['ok'])
            backend.dom_tabs()
            backend.dom_observe('target', None, 10)
            backend.dom_act('target', 'snapshot', [])

        self.assertEqual(calls, ['start', 'tabs', 'observe', 'act'])
        self.assertEqual([event[0] for event in events],
                         ['acquire', 'release'] * 4)
        self.assertTrue(all(event[1:3] == ('Browser automation', 'DOM/BiDi')
                            for event in events if event[0] == 'acquire'))

    def test_chromium_cli_control_operations_acquire_browser_lease(self):
        events = []

        @contextmanager
        def hold(agent, method, *, env=None):
            events.append(('acquire', agent, method))
            try:
                yield
            finally:
                events.append(('release', agent, method))

        completed = type('Result', (), {'returncode': 0, 'stdout': '{"ok":true}',
                                        'stderr': ''})()
        with patch.object(overlay, 'hold', side_effect=hold), \
                patch.object(cu.subprocess, 'run', return_value=completed) as run:
            cu.cli_run_chromium(['open', 'https://example.invalid'])
        self.assertEqual([event[0] for event in events], ['acquire', 'release'])
        self.assertEqual(events[0][1:], ('Browser automation', 'CDP CLI'))
        self.assertEqual(run.call_count, 1)

        events.clear()
        with patch.object(overlay, 'hold', side_effect=hold), \
                patch.object(cu.subprocess, 'run', return_value=completed):
            cu.cli_run_chromium(['history'])
        self.assertEqual(events, [])


if __name__ == '__main__':
    unittest.main()

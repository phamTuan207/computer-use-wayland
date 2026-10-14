"""Run production a11y actions with fake interfaces; no GI or desktop access."""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu
SOURCE = (ROOT / 'scripts/a11y.py').read_text()


class A11yAdapterTests(unittest.TestCase):
    def setUp(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'act')
        self.element = mock.Mock()
        self.element.get_action_iface.return_value = self.element
        self.element.get_n_actions.return_value = 1
        self.element.get_action_name.return_value = 'click'
        self.element.do_action.return_value = True
        self.snapshot = {'backend': 'a11y', 'created': time.time(), 'pid': 1,
                         'elements': [{'ref': 'e1', 'editable': True, 'actions': ['click']}]}
        self.ns = dict(time=time, read_json_file=mock.Mock(return_value=self.snapshot),
                       validate_actions=cu.validate_actions, app=mock.Mock(),
                       resolve=mock.Mock(return_value=self.element),
                       observe=mock.Mock(side_effect=RuntimeError('observe failed')))
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'), self.ns)

    def test_final_observation_failure_preserves_acknowledged_count(self):
        result = self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['completed'], 1)
        self.assertIn('execution_ms', result)
        self.assertEqual(result['capture_error'], 'observe failed')
        self.element.do_action.assert_called_once_with(0)

    def test_action_error_survives_observation_failure(self):
        self.element.do_action.side_effect = [True, False]
        result = self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}] * 2)
        self.assertEqual(result['completed'], 1)
        self.assertEqual(result['error'], 'native action refused')
        self.assertEqual(result['capture_error'], 'observe failed')
        self.assertIn('execution_ms', result)

    def test_baseexception_propagates_from_action_and_observation(self):
        for error in (KeyboardInterrupt('interrupt'), SystemExit(9)):
            for stage in ('action', 'observe'):
                with self.subTest(error=type(error).__name__, stage=stage):
                    self.element.do_action.side_effect = error if stage == 'action' else None
                    self.ns['observe'].side_effect = error if stage == 'observe' else RuntimeError('after')
                    with self.assertRaises(type(error)):
                        self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])

    def test_bad_later_action_sends_no_input(self):
        for bad in ({'type': []}, {'type': 'set_text', 'ref': 'e1', 'text': 5},
                    {'type': 'set_text', 'ref': 'e1', 'text': 'x' * 10001}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}, bad])
                self.element.do_action.assert_not_called()

    def test_unknown_operation_cannot_reach_act(self):
        tail = ast.parse(SOURCE).body[-1]
        called = mock.Mock()
        ns = dict(sys=mock.Mock(stdin=io.StringIO('{"operation":"typo"}')),
                  read_json=cu.read_json, json=json, act=called)
        ns['sys'].stdin = io.StringIO('{"operation":"typo"}')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exec(compile(ast.Module(body=[tail], type_ignores=[]), 'a11y.py', 'exec'), ns)
        self.assertFalse(json.loads(output.getvalue())['ok'])
        ns['sys'].exit.assert_called_once_with(1)
        called.assert_not_called()


class A11yCliTests(unittest.TestCase):
    def test_valid_set_text_reaches_adapter_once(self):
        for text in ('', 'hello', 'Tiếng Việt', '🙂'):
            with self.subTest(text=text), contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(cu, 'environment', return_value={}))
                stack.enter_context(mock.patch.object(cu, 'require_session'))
                stack.enter_context(mock.patch.object(cu, 'check_cancel'))
                stack.enter_context(mock.patch.object(cu, 'locked', return_value=contextlib.nullcontext()))
                adapter = stack.enter_context(mock.patch.object(cu, 'run_cancelable', return_value='{"ok":true,"completed":1}'))
                pointer = stack.enter_context(mock.patch.object(cu, 'Pointer', side_effect=AssertionError('pointer')))
                stack.enter_context(mock.patch.object(sys, 'argv', ['cu', 'a11y', 'act', '--snapshot', 'snapshot', '--actions', '-']))
                stack.enter_context(mock.patch.object(sys, 'stdin', io.StringIO(json.dumps([{'type': 'set_text', 'ref': 'e1', 'text': text}]))))
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(cu.main(), 0)
                self.assertEqual(json.loads(output.getvalue())['completed'], 1)
                self.assertEqual(adapter.call_count, 1)
                self.assertEqual(json.loads(adapter.call_args.kwargs['input'])['actions'][0]['text'], text)
                pointer.assert_not_called()


if __name__ == '__main__':
    unittest.main()

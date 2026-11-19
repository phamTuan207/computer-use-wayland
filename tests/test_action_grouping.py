"""Desktop action-group safety rules and their preflight integration."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import cu  # noqa: E402
import session_driver  # noqa: E402

ADDR = '0x1234'


def click(x=10, y=10):
    return {'type': 'click', 'x': x, 'y': y}


def key(*keys):
    return {'type': 'key', 'keys': list(keys)}


class ActionGroupValidator(unittest.TestCase):
    def validate(self, actions):
        cu.validate_actions(actions, 'desktop')
        cu.validate_action_group(actions)

    def test_accepts_safe_groups_without_mutating_them(self):
        cases = [
            [click(), {'type': 'type', 'text': 'name'}, key('Enter')],
            [click(), key('CTRL', 'A'), {'type': 'type', 'text': 'path'}],
            [{'type': 'move', 'x': 2, 'y': 3}, click()],
            [key('x'), {'type': 'type', 'text': 'word'}],
            [{'type': 'type', 'text': 'one'}, {'type': 'type', 'text': 'two'}],
            [click()],
            [{'type': 'type', 'text': 'word'}],
            [key('Enter')],
            [click(), {'type': 'wait', 'ms': 0}],
            [{'type': 'scroll', 'x': 5, 'y': 6, 'dy': 100}],
            [{'type': 'drag', 'from': [1, 2], 'to': [3, 4]}],
            [key('Ctrl', 'T'), {'type': 'wait', 'ms': 10}],
        ]
        for actions in cases:
            original = json.loads(json.dumps(actions))
            with self.subTest(actions=actions):
                self.validate(actions)
                self.assertEqual(actions, original)

    def test_rejects_groups_at_the_first_safe_split_point(self):
        cases = [
            ([click(), click(15, 15)], 1),
            ([click(), {'type': 'move', 'x': 15, 'y': 15}], 1),
            ([{'type': 'type', 'text': 'name'}, click()], 1),
            ([click(), {'type': 'scroll', 'x': 5, 'y': 6, 'dy': 100}], 1),
            ([{'type': 'scroll', 'x': 5, 'y': 6, 'dy': 100}, click()], 1),
            ([{'type': 'drag', 'from': [1, 2], 'to': [3, 4]}, click()], 1),
            ([key('Enter'), {'type': 'type', 'text': 'next'}], 1),
            ([{'type': 'type', 'text': 'first\n'}, {'type': 'type', 'text': 'next'}], 1),
            ([key('Tab'), {'type': 'type', 'text': 'next'}], 1),
            ([click(), key('Enter'), {'type': 'type', 'text': 'next'}], 2),
            ([click(), key('Ctrl', 'W'), {'type': 'type', 'text': 'next'}], 2),
        ]
        for actions, split_after in cases:
            with self.subTest(actions=actions), self.assertRaises(ValueError) as raised:
                self.validate(actions)
            message = str(raised.exception)
            self.assertIn(f'action {split_after}', message)
            self.assertIn(f'split the group after action {split_after}', message)
            self.assertIn('observe again before the remaining actions', message)

    def test_every_terminal_key_only_allows_waits_after_it(self):
        terminal_keys = [
            ('Return',), ('Enter',), ('Escape',), ('Tab',),
            ('Ctrl', 'T'), ('CTRL', 'W'), ('ctrl', 'n'),
            ('ctrl', 'Tab'), ('Ctrl', 'Shift', 'Tab'), ('Alt', 'F4'),
        ]
        for keys in terminal_keys:
            with self.subTest(keys=keys):
                self.validate([key(*keys), {'type': 'wait', 'ms': 0}])
                with self.assertRaises(ValueError):
                    self.validate([key(*keys), {'type': 'type', 'text': 'next'}])
        self.validate([key('Ctrl', 'A'), {'type': 'type', 'text': 'replace'}])


class DesktopActHarness(unittest.TestCase):
    """Mocks desktop_act seams using the same pattern as act diagnostics."""

    def setUp(self):
        from PIL import Image

        self.meta = {
            'backend': 'desktop', 'scope': 'window', 'window': ADDR,
            'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
            'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
            'monitor_transform': 0, 'region': [0, 0, 20, 20],
            'image_size': [20, 20], 'max_width': 20, 'crop': None,
            'image': 'synthetic.png', 'pixel_sha256': 'old-hash',
        }
        self.image = Image.new('RGB', (20, 20))
        self.cursor = [0, 0]
        self.cursor_follows_pointer = True
        self.pointer_commands = []
        self.keyboard_calls = []
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(cu, 'validate_desktop_observation',
                                               return_value=self.image))
        self.stack.enter_context(patch.object(cu, 'image_point',
                                               side_effect=lambda meta, x, y: (x, y)))
        self.stack.enter_context(patch.object(cu, 'check_cancel'))
        self.stack.enter_context(patch.object(cu, 'focus'))
        self.stack.enter_context(patch.object(cu, 'window', return_value={
            'at': [0, 0], 'size': [20, 20]}))
        self.stack.enter_context(patch.object(cu, 'hypr', side_effect=self.hypr))
        self.stack.enter_context(patch.object(cu, 'observe', side_effect=self.observe))
        self.stack.enter_context(patch.object(cu, 'observe_screen', side_effect=self.observe))
        self.pointer_factory = self.stack.enter_context(
            patch.object(cu, 'Pointer', side_effect=self.make_pointer))
        self.stack.enter_context(patch.object(cu, 'keyboard_argv', return_value=['mock-keyboard']))
        self.stack.enter_context(patch.object(cu, 'standalone_type_argv', return_value=['mock-type']))
        self.stack.enter_context(patch.object(cu, 'run_cancelable', side_effect=self.run_input))
        self.stack.enter_context(patch.object(cu, 'literal_keyboard',
                                               side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(patch.object(cu, 'mouse_modifiers',
                                               side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(patch.object(cu, 'wait_cancelable'))
        self.stack.enter_context(patch.object(cu, '_diagnostic_event'))
        self.stack.enter_context(patch.object(cu.time, 'sleep'))

    def hypr(self, env, query):
        if query == 'monitors':
            return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20, 'height': 20,
                     'scale': 1, 'transform': 0}]
        if query == 'activewindow':
            return {'address': ADDR}
        if query == 'cursorpos':
            return {'x': self.cursor[0], 'y': self.cursor[1]}
        raise AssertionError('unexpected compositor query ' + query)

    def observe(self, *args, **kwargs):
        if kwargs.get('persist', True):
            return dict(self.meta, image='after.png')
        return self.image, dict(self.meta)

    def make_pointer(self, *args, **kwargs):
        harness = self

        class Pointer:
            def command(self, command):
                harness.pointer_commands.append(command)
                if command.startswith('abs ') and harness.cursor_follows_pointer:
                    _, x, y, *_ = command.split()
                    harness.cursor[:] = [round(int(x) * 20 / 1000000),
                                         round(int(y) * 20 / 1000000)]

            def close(self):
                pass

        return Pointer()

    def run_input(self, command, *args, **kwargs):
        self.keyboard_calls.append((command, args, kwargs))
        return ''

    def act(self, actions, **kwargs):
        return cu.desktop_act({}, self.meta, actions, after_capture=False, **kwargs)

    def test_unsafe_group_refuses_before_any_input_and_keeps_session(self):
        actions = [click(2, 2), {'type': 'wait', 'ms': 0}, click(15, 15)]
        with self.assertRaises(cu.PreflightRefusal) as raised:
            self.act(actions)
        self.assertIn('split the group after action 2', str(raised.exception))
        self.pointer_factory.assert_not_called()
        self.assertEqual(self.pointer_commands, [])
        self.assertEqual(self.keyboard_calls, [])
        with self.assertRaises(cu.PreflightRefusal):
            cu.CodeExecBackend({}).act(self.meta, actions, None)
        self.pointer_factory.assert_not_called()

        with patch.object(cu, 'environment', return_value={}), \
                patch.object(cu, 'require_session'), \
                patch.object(cu, 'check_cancel'), \
                patch.object(cu, 'locked', return_value=contextlib.nullcontext()), \
                patch.object(cu, 'read_json_file', return_value=self.meta), \
                patch('session_policy.require_observation'):
            request = {'args': ['act', '--observation', 'observation.json', '--actions', '-'],
                       'stdin': json.dumps(actions)}
            output = io.StringIO()
            session_driver.relay_commands(io.StringIO(json.dumps(request) + '\n'), output)
        response = json.loads(output.getvalue().splitlines()[1])
        self.assertTrue(response['session_continues'])
        self.assertEqual(response['result']['completed'], 0)
        self.assertIn('No input was sent.', response['result']['next_step'])
        self.assertEqual(self.pointer_commands, [])
        self.assertEqual(self.keyboard_calls, [])

    def test_safe_group_executes_click_type_enter(self):
        result = self.act([click(), {'type': 'type', 'text': 'name'}, key('Enter')])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 3)
        self.assertTrue(any(command.startswith('button ') for command in self.pointer_commands))
        self.assertEqual(len(self.keyboard_calls), 2)

    def test_first_action_failure_stops_before_the_grouped_type(self):
        self.cursor_follows_pointer = False
        self.cursor = [0, 0]
        result = self.act([click(10, 10), {'type': 'type', 'text': 'never'}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['completed'], 0)
        self.assertIn('pointer missed target', result['error'])
        self.assertEqual(self.keyboard_calls, [])

    def test_s2_shape_is_plan_only(self):
        actions = [click(2, 2), {'type': 'wait', 'ms': 0}, click(15, 15)]
        with self.assertRaises(cu.PreflightRefusal):
            self.act(actions, group_policy='strict')
        result = self.act(actions, group_policy='plan')
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['completed'], 3)

    def test_invalid_group_policy_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "group_policy must be 'strict' or 'plan'"):
            self.act([{'type': 'wait', 'ms': 0}], group_policy='skip')

    def test_cli_flag_is_passed_through_and_defaults_to_strict(self):
        for extra, expected in ((['--group-policy', 'plan'], 'plan'), ([], 'strict')):
            with self.subTest(group_policy=expected):
                with contextlib.ExitStack() as stack:
                    desktop_act = stack.enter_context(patch.object(
                        cu, 'desktop_act', return_value={'ok': True, 'completed': 1}))
                    stack.enter_context(patch.object(cu, 'environment', return_value={}))
                    stack.enter_context(patch.object(cu, 'require_session'))
                    stack.enter_context(patch.object(cu, 'locked',
                                                      return_value=contextlib.nullcontext()))
                    stack.enter_context(patch.object(cu, 'read_json_file',
                                                      return_value=self.meta))
                    stack.enter_context(patch.object(cu, 'check_cancel'))
                    stack.enter_context(patch('session_policy.require_observation'))
                    stack.enter_context(patch('session_policy.complete_requirement'))
                    stack.enter_context(patch.dict('os.environ', {'CU_SESSION_TOKEN': 'a' * 32}))
                    stack.enter_context(patch.object(sys, 'argv', [
                        'cu', 'act', '--observation', 'observation.json', '--actions', '-', *extra]))
                    stack.enter_context(patch.object(sys, 'stdin',
                                                      io.StringIO('[{"type":"wait","ms":0}]')))
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(cu.main(), 0)
                    if expected=='plan':
                        self.assertEqual(desktop_act.call_args.kwargs['group_policy'], expected)
                    else:
                        self.assertNotIn('group_policy', desktop_act.call_args.kwargs)


if __name__ == '__main__':
    unittest.main()

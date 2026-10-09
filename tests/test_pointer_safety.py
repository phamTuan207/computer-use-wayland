"""Pointer safety regressions; all desktop access and input are mocked."""
import importlib.util
import io
import itertools
from contextlib import ExitStack
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import Mock, patch

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cu_pointer_safety', ROOT / 'scripts/cu.py')
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)
import indicator


class PointerStartup(unittest.TestCase):
    def test_reply_failure_closes_streams_and_reaps_process(self):
        for reply, readable, error in (
            ('', False, 'pointer timed out'),
            ('', True, 'pointer disconnected'),
            ('unexpected\n', True, 'pointer startup failed'),
        ):
            with self.subTest(error=error):
                process = Mock(stdin=io.StringIO(), stdout=io.StringIO(reply),
                               stderr=io.StringIO(), wait=Mock(return_value=0))
                ready = ([process.stdout], [], []) if readable else ([], [], [])
                with patch.object(cu.subprocess, 'Popen', return_value=process), \
                        patch.object(cu.select, 'select', return_value=ready):
                    with self.assertRaisesRegex(RuntimeError, error):
                        cu.Pointer({}, 'fixture')
                process.wait.assert_called_once()
                self.assertTrue(all(s.closed for s in
                                    (process.stdin, process.stdout, process.stderr)))


class PointerSafety(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (1280, 800), 'white')
        self.monitor = {'name': 'fixture', 'x': 0, 'y': 0, 'width': 1280,
                        'height': 800, 'scale': 1}
        self.meta = {'backend': 'desktop', 'scope': 'window', 'created': time.time(),
                     'window': 'fixture', 'window_bounds': [0, 0, 1280, 800],
                     'monitor': 'fixture', 'monitor_box': [0, 0, 1280, 800],
                     'monitor_scale': 1, 'monitor_transform': 0,
                     'image_size': [1280, 800], 'region': [0, 0, 1280, 800],
                     'image': 'synthetic.png', 'max_width': 1280,
                     'pixel_sha256': 'fixture'}
        self.active = 'fixture'
        self.cancelled = False
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(cu, 'check_cancel', side_effect=self.check_cancel))
        self.focus = stack.enter_context(patch.object(cu, 'focus'))
        self.pointer_cls = stack.enter_context(patch.object(cu, 'Pointer'))
        self.pointer = self.pointer_cls.return_value
        stack.enter_context(patch.object(cu, 'hypr', side_effect=self.hypr))
        stack.enter_context(patch.object(cu, 'window', return_value={
            'at': [0, 0], 'size': [1280, 800]}))
        self.observe = stack.enter_context(patch.object(
            cu, 'observe', side_effect=self.fake_observe))
        stack.enter_context(patch('PIL.Image.open', return_value=self.image))
        stack.enter_context(patch.object(cu, 'save_observation', side_effect=lambda im, meta, width: meta))
        # Fail immediately if an unexpected path tries to launch a desktop command.
        self.run = stack.enter_context(patch.object(cu, 'run', side_effect=AssertionError('live command')))
        self.typed = stack.enter_context(patch.object(cu, 'run_cancelable', side_effect=AssertionError('live input')))
        stack.enter_context(patch.object(cu.time, 'sleep'))
        stack.enter_context(patch.object(cu.time, 'monotonic',
                                        side_effect=itertools.count(step=.01)))
        # A mock test must never reach the live session socket.
        self.indicator = stack.enter_context(patch.object(indicator, 'request', return_value=False))
        stack.enter_context(patch.object(indicator.socket, 'socket',
                                         side_effect=AssertionError('indicator real connection attempted')))

    def fake_observe(self, env, address, crop=None, max_width=1280, **kwargs):
        # capture (persist=False) returns (image, meta); the final observation
        # (persist default) returns meta so result['after']['pixel_sha256'] works.
        if kwargs.get('persist', True):
            return self.meta.copy()
        return self.image, self.meta.copy()

    def check_cancel(self):
        if self.cancelled:
            raise RuntimeError('cancelled by user')

    def hypr(self, env, query):
        if query == 'monitors':
            return [self.monitor]
        if query == 'activewindow':
            return {'address': self.active}
        if query == 'cursorpos':
            return {'x': 10, 'y': 10}
        raise AssertionError('unexpected compositor query ' + query)

    def test_small_drag_destination_change_prevents_input(self):
        changed = self.image.copy()
        ImageDraw.Draw(changed).rectangle((800, 500, 823, 523), fill='black')
        self.observe.side_effect = lambda *a, **k: (changed, self.meta.copy())
        # The global threshold and source patch alone must not detect this change.
        self.assertFalse(cu.screen_changed(self.image, changed,
                                          [{'type': 'click', 'x': 211, 'y': 211}]))
        result = cu.desktop_act({}, self.meta, [
            {'type': 'drag', 'from': [211, 211], 'to': [811, 511]}])
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['completed'], 0)
        self.assertIn('screen changed', result['error'])
        self.pointer_cls.assert_not_called()

    def test_cancel_while_button_held_releases_and_closes(self):
        for action in ({'type': 'click', 'x': 10, 'y': 10},
                       {'type': 'double_click', 'x': 10, 'y': 10},
                       {'type': 'drag', 'from': [10, 10], 'to': [20, 20]}):
            with self.subTest(action=action):
                self.cancelled = False
                self.pointer.reset_mock()
                def command(text):
                    if text == 'button 0 1':
                        self.cancelled = True
                self.pointer.command.side_effect = command
                result = cu.desktop_act({}, self.meta, [action])
                self.assertFalse(result['ok'], result)
                self.assertEqual(result['completed'], 0)
                self.assertIn('cancelled by user', result['error'])
                buttons = [c.args[0] for c in self.pointer.command.call_args_list
                           if c.args[0].startswith('button')]
                self.assertEqual(buttons, ['button 0 1', 'button 0 0'])
                self.pointer.close.assert_called_once()

    def test_focus_change_between_double_click_presses_stops_second(self):
        def command(text):
            if text == 'button 0 0':
                self.active = 'other-window'
        self.pointer.command.side_effect = command
        result = cu.desktop_act({}, self.meta, [
            {'type': 'double_click', 'x': 10, 'y': 10}])
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['completed'], 0)
        self.assertIn('focus changed', result['error'])
        buttons = [c.args[0] for c in self.pointer.command.call_args_list
                   if c.args[0].startswith('button')]
        self.assertEqual(buttons, ['button 0 1', 'button 0 0'])
        self.pointer.close.assert_called_once()

    def test_single_click_has_no_trailing_wait(self):
        waits = []
        with patch.object(cu, 'wait_cancelable', side_effect=lambda s: waits.append(s)):
            result = cu.desktop_act({}, self.meta, [{'type': 'click', 'x': 10, 'y': 10}])
        self.assertTrue(result['ok'], result)
        self.assertEqual(waits, [.025])
        buttons = [c.args[0] for c in self.pointer.command.call_args_list
                   if c.args[0].startswith('button')]
        self.assertEqual(buttons, ['button 0 1', 'button 0 0'])

    def test_double_click_waits_between_presses_only(self):
        waits = []
        with patch.object(cu, 'wait_cancelable', side_effect=lambda s: waits.append(s)):
            result = cu.desktop_act({}, self.meta, [{'type': 'double_click', 'x': 10, 'y': 10}])
        self.assertTrue(result['ok'], result)
        self.assertEqual(waits, [.025, .035, .025])
        buttons = [c.args[0] for c in self.pointer.command.call_args_list
                   if c.args[0].startswith('button')]
        self.assertEqual(buttons, ['button 0 1', 'button 0 0', 'button 0 1', 'button 0 0'])

    def test_cancel_between_double_click_presses_stops_second(self):
        def command(text):
            if text == 'button 0 0':
                self.cancelled = True
        self.pointer.command.side_effect = command
        result = cu.desktop_act({}, self.meta, [
            {'type': 'double_click', 'x': 10, 'y': 10}])
        self.assertFalse(result['ok'], result)
        self.assertIn('cancelled by user', result['error'])
        buttons = [c.args[0] for c in self.pointer.command.call_args_list
                   if c.args[0].startswith('button')]
        self.assertEqual(buttons, ['button 0 1', 'button 0 0'])
        self.pointer.close.assert_called_once()

    def test_invalid_mouse_payload_rejected_before_side_effects(self):
        actions = [
            {'type': 'move', 'x': 10, 'y': 10, 'modifiers': ['ctrl']},
            {'type': 'click', 'x': 10, 'y': 10, 'modifiers': 'ctrl'},
            {'type': 'click', 'x': 10, 'y': 10, 'modifiers': ['bogus']},
            {'type': 'click', 'x': 10, 'y': 10,
             'modifiers': ['ctrl', 'shift', 'alt', 'super', 'altgr', 'ctrl']},
            {'type': 'click', 'x': 10, 'y': 10, 'button': 'wheel'},
            {'type': 'drag', 'from': [10, 10], 'to': [20, 20], 'ms': 10},
            {'type': 'drag', 'from': [10, 10], 'to': [20, 20], 'ms': 3000},
            {'type': 'scroll', 'x': 10, 'y': 10, 'dx': float('inf')},
            {'type': 'scroll', 'x': 10, 'y': 10, 'dy': 'big'},
        ]
        for action in actions:
            with self.subTest(action=action), self.assertRaises(ValueError):
                # A valid first action must also remain unexecuted.
                cu.desktop_act({}, self.meta, [{'type': 'click', 'x': 10, 'y': 10}, action])
        self.focus.assert_not_called()
        self.pointer_cls.assert_not_called()
        self.pointer.command.assert_not_called()
        self.observe.assert_not_called()
        self.run.assert_not_called()
        self.typed.assert_not_called()

    def pointers(self):
        made = {}

        def factory(env, monitor, binary='pointer'):
            made.setdefault(binary, Mock())
            return made[binary]
        self.pointer_cls.side_effect = factory
        return made

    def test_valid_modifiers_open_and_release_modifiers_pointer(self):
        made = self.pointers()
        result = cu.desktop_act({}, self.meta, [
            {'type': 'scroll', 'x': 10, 'y': 10, 'dx': 0, 'dy': 1, 'modifiers': ['ctrl', 'shift']}])
        self.assertTrue(result['ok'], result)
        self.assertEqual([c.args[0] for c in made['modifiers'].command.call_args_list],
                         ['mods 5', 'mods 0'])
        made['modifiers'].close.assert_called_once()

    def test_modifier_click_releases_modifiers_and_button_on_cancel(self):
        made = self.pointers()

        def command(text):
            if text == 'button 0 1':
                self.cancelled = True
        made.setdefault('pointer', Mock()).command.side_effect = command
        result = cu.desktop_act({}, self.meta, [
            {'type': 'click', 'x': 10, 'y': 10, 'modifiers': ['ctrl']}])
        self.assertFalse(result['ok'], result)
        self.assertIn('cancelled by user', result['error'])
        self.assertEqual([c.args[0] for c in made['modifiers'].command.call_args_list],
                         ['mods 4', 'mods 0'])
        made['modifiers'].close.assert_called_once()
        self.assertIn('button 0 0',
                      [c.args[0] for c in made['pointer'].command.call_args_list])

    def test_right_and_middle_drag_release_their_button(self):
        for button, code in (('right', 1), ('middle', 2)):
            with self.subTest(button=button):
                self.cancelled = False
                self.pointer.reset_mock()

                def command(text, code=code):
                    if text == f'button {code} 1':
                        self.cancelled = True
                self.pointer.command.side_effect = command
                result = cu.desktop_act({}, self.meta, [
                    {'type': 'drag', 'from': [10, 10], 'to': [20, 20], 'button': button}])
                self.assertFalse(result['ok'], result)
                self.assertIn('cancelled by user', result['error'])
                buttons = [c.args[0] for c in self.pointer.command.call_args_list
                           if c.args[0].startswith('button')]
                self.assertEqual(buttons, [f'button {code} 1', f'button {code} 0'])

    def test_final_capture_failure_marks_not_ok(self):
        seen = []

        def observe(env, address, crop=None, max_width=1280, **kwargs):
            if not seen:
                seen.append(1)
                return self.image, self.meta.copy()
            raise RuntimeError('capture exploded')
        self.observe.side_effect = observe
        result = cu.desktop_act({}, self.meta, [{'type': 'click', 'x': 10, 'y': 10}])
        self.assertFalse(result['ok'], result)
        self.assertIn('capture exploded', result['capture_error'])


if __name__ == '__main__':
    unittest.main()

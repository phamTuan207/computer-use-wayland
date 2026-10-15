"""Fresh desktop checks at input boundaries; all external input is mocked."""
from contextlib import contextmanager
import unittest
from unittest.mock import Mock, patch

import test_pointer_safety as fixture


@contextmanager
def desktop():
    case = fixture.PointerSafety()
    case.setUp()
    try:
        yield case
    finally:
        case.doCleanups()


class GuardBoundaries(unittest.TestCase):
    def change(self, case, defect):
        if defect == 'focus':
            case.active = 'other'
        elif defect == 'window':
            fixture.cu.window.return_value['size'] = [1279, 800]
        elif defect == 'monitor':
            case.monitor['scale'] = 2
        else:
            case.cancelled = True

    def test_changes_after_preparatory_motion_stop_unmodified_input(self):
        for defect in ('focus', 'window', 'monitor', 'cancel'):
            with self.subTest(defect=defect), desktop() as case:
                def command(text):
                    if text.startswith('abs '):
                        self.change(case, defect)
                case.pointer.command.side_effect = command
                result = fixture.cu.desktop_act({}, case.meta,
                    [{'type': 'click', 'x': 10, 'y': 10}], after_capture=False)
                self.assertFalse(result['ok'], result)
                self.assertEqual(result['completed'], 0)
                self.assertEqual(case.pointer.command.call_count, 1,
                                 'only preparatory motion; no target input')
                case.pointer.close.assert_called_once()

    def test_changes_before_modifier_setup_stop_modifier_input(self):
        for defect in ('focus', 'window', 'monitor', 'cancel'):
            with self.subTest(defect=defect), desktop() as case:
                def command(text):
                    if text.startswith('abs '):
                        self.change(case, defect)
                case.pointer.command.side_effect = command
                result = fixture.cu.desktop_act({}, case.meta,
                    [{'type': 'click', 'x': 10, 'y': 10,
                      'modifiers': ['ctrl']}], after_capture=False)
                self.assertFalse(result['ok'], result)
                self.assertEqual(result['completed'], 0)
                self.assertEqual(case.pointer_cls.call_count, 1,
                                 'no modifier device before a fresh check')
                self.assertFalse(any(c.args[0].startswith(('button ', 'mods '))
                                     for c in case.pointer.command.call_args_list))

    def test_focus_change_during_modifier_setup_releases_without_click(self):
        with desktop() as case:
            keyboard = Mock()
            def device(env, monitor, **kwargs):
                return keyboard if kwargs.get('binary') == 'modifiers' else case.pointer
            def command(text):
                if text == 'mods 4':
                    case.active = 'other'
            case.pointer_cls.side_effect = device
            keyboard.command.side_effect = command
            result = fixture.cu.desktop_act({}, case.meta,
                [{'type': 'click', 'x': 10, 'y': 10,
                  'modifiers': ['ctrl']}], after_capture=False)
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['completed'], 0)
            self.assertEqual([c.args[0] for c in keyboard.command.call_args_list],
                             ['mods 4', 'mods 0'])
            keyboard.close.assert_called_once()
            self.assertFalse(any(c.args[0].startswith('button ')
                                 for c in case.pointer.command.call_args_list))

    def test_screen_scope_checks_monitor_after_preparatory_motion(self):
        with desktop() as case, patch.object(fixture.cu, 'observe_screen',
                                             side_effect=case.fake_observe):
            case.meta['scope'] = 'screen'
            def command(text):
                if text.startswith('abs '):
                    case.monitor['scale'] = 2
            case.pointer.command.side_effect = command
            result = fixture.cu.desktop_act({}, case.meta,
                [{'type': 'click', 'x': 10, 'y': 10}], after_capture=False)
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['completed'], 0)
            self.assertEqual(case.pointer.command.call_count, 1)
            case.focus.assert_not_called()


if __name__ == '__main__':
    unittest.main()

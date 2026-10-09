"""Focus/capture regressions with a fake compositor; never send desktop input."""
import importlib.util
import io
from pathlib import Path
import unittest
from contextlib import ExitStack
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('cu',Path(__file__).resolve().parents[1]/'scripts/cu.py')
cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)


class Focus(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.cancel=self.stack.enter_context(patch.object(cu,'check_cancel'))
        self.window=self.stack.enter_context(patch.object(cu,'window',return_value={}))
        self.dispatch=self.stack.enter_context(patch.object(cu,'run',return_value='ok\n'))
        self.now=0
        self.stack.enter_context(patch.object(cu.time,'monotonic',side_effect=lambda:self.now))
        self.stack.enter_context(patch.object(cu.time,'sleep',side_effect=self.sleep))

    def sleep(self,seconds):self.now+=seconds

    def test_focus_can_settle_after_old_200ms_limit(self):
        with patch.object(cu,'hypr',side_effect=lambda *args:{'address':'0x1' if self.now>=.6 else '0x2'}):
            cu.focus({},'0x1')
        self.assertGreaterEqual(self.now,.6)
        self.assertLess(self.now,1.5)
        self.dispatch.assert_called_once_with(['hyprctl','dispatch','hl.dsp.focus({ window = "address:0x1" })'],{})

    def test_timeout_is_bounded_and_reports_actual_focus(self):
        with patch.object(cu,'hypr',return_value={'address':'0x2'}):
            with self.assertRaisesRegex(RuntimeError,r'target=0x1, active=0x2'):
                cu.focus({},'0x1')
        self.assertEqual(self.now,1.5)
        self.assertEqual(self.window.call_count,2)
        self.dispatch.assert_called_once()

    def test_closed_target_never_dispatches(self):
        self.window.side_effect=ValueError('window no longer exists')
        with patch.object(cu,'hypr',return_value={'address':'0x2'}):
            with self.assertRaisesRegex(ValueError,'window no longer exists'):cu.focus({},'0x1')
        self.dispatch.assert_not_called()

    def test_target_closing_during_wait_is_reported(self):
        self.window.side_effect=[{},ValueError('window no longer exists')]
        with patch.object(cu,'hypr',return_value={'address':'0x2'}):
            with self.assertRaisesRegex(ValueError,'window no longer exists'):cu.focus({},'0x1')

    def test_dispatch_error_is_not_a_focus_timeout(self):
        self.dispatch.return_value='dispatcher rejected'
        with patch.object(cu,'hypr',return_value={'address':'0x2'}):
            with self.assertRaisesRegex(RuntimeError,'focus dispatch rejected'):cu.focus({},'0x1')
        self.assertEqual(self.now,0)

    def test_cancel_stops_wait_without_redispatch(self):
        self.cancel.side_effect=[None,None,RuntimeError('cancelled by user')]
        with patch.object(cu,'hypr',return_value={'address':'0x2'}):
            with self.assertRaisesRegex(RuntimeError,'cancelled by user'):cu.focus({},'0x1')
        self.assertEqual(self.now,.04)
        self.dispatch.assert_called_once()


if __name__=='__main__':unittest.main()

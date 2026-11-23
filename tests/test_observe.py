"""Focus/capture regressions with a fake compositor; never send desktop input."""
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('cu',ROOT/'scripts/cu.py')
cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)
import indicator


class Observe(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.monitor={'id':0,'name':'test','width':20,'height':10,'scale':1,'x':0,'y':0,
                      'activeWorkspace':{'id':1},'specialWorkspace':{'id':0}}
        self.client={'address':'0x1','monitor':0,'at':[0,0],'size':[20,10],'workspace':{'id':1}}
        raw=io.BytesIO();Image.new('RGB',(20,10)).save(raw,format='PPM')
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        # Never touch a live session socket from a mock test.
        self.indicator=self.stack.enter_context(patch.object(indicator,'request',return_value=False))
        self.stack.enter_context(patch.object(indicator.socket,'socket',
                                              side_effect=AssertionError('indicator real connection attempted')))
        self.focus=self.stack.enter_context(patch.object(cu,'focus'))
        self.window=self.stack.enter_context(patch.object(cu,'window',return_value=self.client))
        self.hypr=self.stack.enter_context(patch.object(cu,'hypr',return_value=[self.monitor]))
        self.capture=self.stack.enter_context(patch.object(cu,'run',return_value=raw.getvalue()))

    def test_default_capture_never_focuses(self):
        cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called()
        self.capture.assert_called_once()
        self.indicator.assert_called_once_with(cu.STATE,'hide')

    def test_capture_hides_and_restores_badge(self):
        self.indicator.side_effect=lambda state,command:True
        cu.observe({},'0x1',persist=False)
        self.assertEqual([call.args[1] for call in self.indicator.call_args_list],['hide','show'])

    def test_explicit_focus(self):
        cu.observe({},'0x1',activate=True,persist=False)
        self.focus.assert_called_once_with({},'0x1')

    def test_code_exec_backend_observe_window_focus_threads_activate(self):
        # Run 64527c3b: the second missing link. CodeExecBackend.
        # observe_window never passed activate to cu.observe, so even a
        # focus-aware api_observe would have silently dropped the
        # request. The flag must arrive at cu.observe as activate.
        backend = cu.CodeExecBackend({})
        with patch.object(cu, 'observe', return_value={'id': 'x'}) as spy:
            backend.observe_window('0x1', None, 960, focus=True)
        spy.assert_called_once()
        self.assertTrue(spy.call_args.kwargs.get('activate') is True)
        with patch.object(cu, 'observe', return_value={'id': 'x'}) as spy:
            backend.observe_window('0x1', None, 960)
        spy.assert_called_once()
        self.assertTrue(spy.call_args.kwargs.get('activate') is False)

    def test_invisible_target_refused_before_capture(self):
        for changes in ({'workspace':{'id':2}},{'hidden':True},{'mapped':False}):
            with self.subTest(changes=changes):
                self.window.return_value=dict(self.client,**changes)
                with self.assertRaisesRegex(RuntimeError,'window is not visible'):cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called();self.capture.assert_not_called()

    def test_visible_special_workspace_and_pinned_window(self):
        self.window.return_value=dict(self.client,workspace={'id':-99})
        self.monitor['specialWorkspace']={'id':-99}
        cu.observe({},'0x1',persist=False)
        self.window.return_value=dict(self.client,workspace={'id':2},pinned=True)
        cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called()

    def test_workspace_switch_during_capture_refuses_image(self):
        self.hypr.side_effect=[[self.monitor],[dict(self.monitor,activeWorkspace={'id':2})]]
        with self.assertRaisesRegex(RuntimeError,'window is not visible'):cu.observe({},'0x1',persist=False)

    def test_cli_defaults_and_focus_flag(self):
        for flags,expected in (([],False),(['--focus'],True)):
            with self.subTest(flags=flags),patch.object(cu.sys,'argv',['cu','observe','--window','0x1',*flags]),\
                 patch.object(cu.sys,'stdout',io.StringIO()),patch.object(cu,'environment',return_value={}),\
                 patch.object(cu,'check_cancel'),patch.object(cu,'locked'),patch.object(cu,'observe',return_value={}) as observe:
                self.assertEqual(cu.main(),0)
                observe.assert_called_once_with({},'0x1',None,960,activate=expected,low_res=False)

    def _wide_setup(self):
        from PIL import Image
        raw=io.BytesIO();Image.new('RGB',(800,500)).save(raw,format='PPM')
        self.capture.return_value=raw.getvalue()
        self.window.return_value=dict(self.client,at=[0,0],size=[800,500])
        self.monitor.update(width=800,height=500)
        self.hypr.return_value=[self.monitor]

    def test_low_res_downscales_routine_observe(self):
        self._wide_setup()
        image,meta=cu.observe({},'0x1',low_res=True,persist=False)
        self.assertEqual(meta['image_size'],[640,400])
        self.assertEqual(meta['max_width'],640)
        self.assertTrue(meta['low_res'])
        self.assertEqual(list(image.size),[640,400])

    def test_default_observe_stays_full_width(self):
        self._wide_setup()
        image,meta=cu.observe({},'0x1',persist=False)
        self.assertEqual(meta['image_size'],[800,500])
        self.assertEqual(meta['max_width'],960)
        self.assertFalse(meta['low_res'])

    def test_low_res_keeps_smaller_explicit_max_width(self):
        self._wide_setup()
        image,meta=cu.observe({},'0x1',max_width=320,low_res=True,persist=False)
        self.assertEqual(meta['image_size'],[320,200])
        self.assertEqual(meta['max_width'],320)
        self.assertTrue(meta['low_res'])

    def test_low_res_screen_observe(self):
        self._wide_setup()
        image,meta=cu.observe_screen({},'test',low_res=True,persist=False)
        self.assertEqual(meta['image_size'],[640,400])
        self.assertEqual(meta['max_width'],640)
        self.assertTrue(meta['low_res'])

    def test_cli_low_res_flag(self):
        with patch.object(cu.sys,'argv',['cu','observe','--window','0x1','--low-res']),\
             patch.object(cu.sys,'stdout',io.StringIO()),patch.object(cu,'environment',return_value={}),\
             patch.object(cu,'check_cancel'),patch.object(cu,'locked'),patch.object(cu,'observe',return_value={}) as observe:
            self.assertEqual(cu.main(),0)
            observe.assert_called_once_with({},'0x1',None,640,activate=False,low_res=True)

    def test_cli_low_res_settle_uses_capped_width(self):
        with patch.object(cu.sys,'argv',['cu','observe','--window','0x1','--low-res','--settle-ms','200']),\
             patch.object(cu.sys,'stdout',io.StringIO()),patch.object(cu,'environment',return_value={}),\
             patch.object(cu,'check_cancel'),patch.object(cu,'locked'),\
             patch.object(cu,'settled_observation',return_value={}) as settled:
            self.assertEqual(cu.main(),0)
            settled.assert_called_once()
            self.assertEqual(settled.call_args.args[1],200)
            self.assertEqual(settled.call_args.args[2],640)

    def test_screen_focus_flag_rejected_before_environment_discovery(self):
        with patch.object(cu.sys,'argv',['cu','observe','--screen','test','--focus']),\
             patch.object(cu.sys,'stderr',io.StringIO()),patch.object(cu,'environment') as env:
            with self.assertRaises(SystemExit) as error:cu.main()
        self.assertEqual(error.exception.code,2);env.assert_not_called()


if __name__=='__main__':unittest.main()

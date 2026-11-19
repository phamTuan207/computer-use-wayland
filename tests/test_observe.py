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
        self.base_client=dict(self.client)
        def hypr(env,what):
            if what=='clients':return [dict(self.client)]
            if what=='monitors':return [dict(self.monitor)]
            raise AssertionError('unexpected compositor query '+what)
        self.hypr=self.stack.enter_context(patch.object(cu,'hypr',side_effect=hypr))
        def run(argv,env=None,text=True,input=None,timeout=12):
            if argv and argv[0]=='grim':return raw.getvalue()
            raise RuntimeError('unexpected subprocess in test: '+str(argv))
        self.capture=self.stack.enter_context(patch.object(cu,'run',side_effect=run))

    def test_default_capture_never_focuses(self):
        cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called()
        grim=[c for c in self.capture.call_args_list if c.args[0][0]=='grim']
        self.assertEqual(len(grim),1)
        self.indicator.assert_called_once_with(cu.STATE,'hide')

    def test_invalid_address_rejected_before_compositor(self):
        with self.assertRaisesRegex(ValueError,'exact window address required'):
            cu.observe({},'bogus',persist=False)
        self.focus.assert_not_called()
        self.hypr.assert_not_called()
        self.capture.assert_not_called()

    def test_capture_hides_and_restores_badge(self):
        self.indicator.side_effect=lambda state,command:True
        cu.observe({},'0x1',persist=False)
        self.assertEqual([call.args[1] for call in self.indicator.call_args_list],['hide','show'])

    def test_explicit_focus(self):
        cu.observe({},'0x1',activate=True,persist=False)
        self.focus.assert_called_once_with({},'0x1')

    def test_invisible_target_refused_before_capture(self):
        for changes in ({'workspace':{'id':2}},{'hidden':True},{'mapped':False}):
            with self.subTest(changes=changes):
                self.client=dict(self.base_client,**changes)
                with self.assertRaisesRegex(RuntimeError,'window is not visible'):cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called()
        grim=[c for c in self.capture.call_args_list if c.args[0][0]=='grim']
        self.assertFalse(grim)

    def test_visible_special_workspace_and_pinned_window(self):
        self.client=dict(self.base_client,workspace={'id':-99})
        self.monitor['specialWorkspace']={'id':-99}
        cu.observe({},'0x1',persist=False)
        self.client=dict(self.base_client,workspace={'id':2},pinned=True)
        cu.observe({},'0x1',persist=False)
        self.focus.assert_not_called()

    def test_workspace_switch_during_capture_refuses_image(self):
        self.hypr.side_effect=[[self.client],[self.monitor],
                               [self.client],[dict(self.monitor,activeWorkspace={'id':2})]]
        with self.assertRaisesRegex(RuntimeError,'window is not visible'):cu.observe({},'0x1',persist=False)

    def test_cli_defaults_and_focus_flag(self):
        for flags,expected in (([],False),(['--focus'],True)):
            with self.subTest(flags=flags),patch.object(cu.sys,'argv',['cu','observe','--window','0x1',*flags]),\
                 patch.object(cu.sys,'stdout',io.StringIO()),patch.object(cu,'environment',return_value={}),\
                 patch.object(cu,'check_cancel'),patch.object(cu,'locked'),patch.object(cu,'observe',return_value={}) as observe:
                self.assertEqual(cu.main(),0)
                observe.assert_called_once_with({},'0x1',None,960,activate=expected)

    def test_screen_focus_flag_rejected_before_environment_discovery(self):
        with patch.object(cu.sys,'argv',['cu','observe','--screen','test','--focus']),\
             patch.object(cu.sys,'stderr',io.StringIO()),patch.object(cu,'environment') as env:
            with self.assertRaises(SystemExit) as error:cu.main()
        self.assertEqual(error.exception.code,2);env.assert_not_called()


if __name__=='__main__':unittest.main()

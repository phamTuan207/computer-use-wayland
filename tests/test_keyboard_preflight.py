"""Keyboard preflight regressions with a fake compositor; never send desktop input."""
import importlib.util
from pathlib import Path
import sys
import time
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('cu',ROOT/'scripts/cu.py')
cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)
import indicator


class StandaloneBudget(unittest.TestCase):
    def test_standalone_argv_and_group_budget(self):
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-x','delay_ms':0}),
                         ['wtype','-','-p','VoidSymbol'])
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-x','delay_ms':5}),
                         ['wtype','-d','5','-','-p','VoidSymbol'])
        # Same accounting as keyboard_argv: len(text)*delay_ms + one 12 ms settle.
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-'+'a'*48,'delay_ms':100}),
                         ['wtype','-d','100','-','-p','VoidSymbol'])
        with self.assertRaisesRegex(ValueError,'5 seconds'):
            cu.standalone_type_argv({'type':'type','text':'-'+'a'*49,'delay_ms':100})


class DesktopPreflight(unittest.TestCase):
    """desktop_act against patched compositor/capture/input; no real device is touched."""
    def setUp(self):
        from PIL import Image
        self.image=Image.new('RGB',(20,20))
        self.monitor={'name':'test','x':0,'y':0,'width':20,'height':20,'scale':1}
        self.meta={'backend':'desktop','scope':'window','created':time.time(),
                   'window':'fixture','window_bounds':[0,0,20,20],
                   'monitor':'test','monitor_box':[0,0,20,20],'monitor_scale':1,
                   'monitor_transform':0,'image_size':[20,20],'region':[0,0,20,20],
                   'image':'synthetic.png','max_width':1280,'pixel_sha256':'fixture'}
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        # A mock test must never reach the live session socket.
        self.indicator=self.stack.enter_context(patch.object(indicator,'request',return_value=False))
        self.stack.enter_context(patch.object(indicator.socket,'socket',
                                              side_effect=AssertionError('indicator real connection attempted')))
        self.stack.enter_context(patch.object(cu,'check_cancel'))
        self.focus=self.stack.enter_context(patch.object(cu,'focus'))
        self.stack.enter_context(patch.object(cu.time,'sleep'))
        # No fcitx5-remote here: literal_keyboard yields without touching IME state.
        self.stack.enter_context(patch.object(cu.shutil,'which',return_value=None))
        self.stack.enter_context(patch.object(cu,'window',return_value={'at':[0,0],'size':[20,20]}))
        self.stack.enter_context(patch.object(cu,'hypr',side_effect=self.hypr))
        self.stack.enter_context(patch.object(cu,'observe',side_effect=self.observe))
        self.stack.enter_context(patch('PIL.Image.open',return_value=self.image))
        self.pointer_cls=self.stack.enter_context(patch.object(cu,'Pointer'))
        self.pointer=self.pointer_cls.return_value
        self.typed=self.stack.enter_context(patch.object(cu,'run_cancelable',return_value=''))

    def hypr(self,env,query):
        if query=='monitors':return [dict(self.monitor)]
        if query=='activewindow':return {'address':'fixture'}
        if query=='cursorpos':return {'x':10,'y':10}
        raise AssertionError('unexpected compositor query '+query)

    def observe(self,env,address,crop,max_width,**kwargs):
        if kwargs.get('persist',True):return self.meta.copy()
        return self.image,self.meta.copy()

    def test_keyboard_only_batch_does_not_open_pointer(self):
        result=cu.desktop_act({},self.meta,[{'type':'type','text':'hello'},
                                            {'type':'key','keys':['Enter']},
                                            {'type':'wait','ms':10}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],3)
        self.pointer_cls.assert_not_called()
        self.assertEqual(self.typed.call_count,3)
        self.indicator.assert_not_called()

    def test_pointer_batch_opens_and_closes_pointer_once(self):
        result=cu.desktop_act({},self.meta,[{'type':'move','x':10,'y':10}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],1)
        self.pointer_cls.assert_called_once()
        self.pointer.close.assert_called_once()
        self.assertGreaterEqual(self.pointer.command.call_count,1)
        self.typed.assert_not_called()

    def test_leading_dash_type_uses_stdin_within_budget(self):
        result=cu.desktop_act({},self.meta,[{'type':'type','text':'-hello'}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],1)
        self.pointer_cls.assert_not_called()
        self.typed.assert_called_once()
        self.assertEqual(self.typed.call_args.args[0],['wtype','-','-p','VoidSymbol'])
        self.assertEqual(self.typed.call_args.kwargs['input'],'-hello')

    def test_oversized_leading_dash_type_rejected_before_input(self):
        actions=[{'type':'type','text':'-'+'a'*60,'delay_ms':100}]
        with self.assertRaisesRegex(ValueError,'5 seconds'):
            cu.desktop_act({},self.meta,actions)
        self.focus.assert_not_called()
        self.pointer_cls.assert_not_called()
        self.typed.assert_not_called()


if __name__=='__main__':unittest.main()

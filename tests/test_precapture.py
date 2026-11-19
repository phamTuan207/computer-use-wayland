"""Window pre-capture tests using a fake compositor and fake grim child."""
import io
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cu
import indicator


class PreCaptureTests(unittest.TestCase):
    def setUp(self):
        cu.stop_precapture()
        self.monitor={'id':0,'name':'test','width':20,'height':10,'scale':1,'x':0,'y':0,
                      'transform':0,'activeWorkspace':{'id':1},'specialWorkspace':{'id':0}}
        self.client={'address':'0x1','monitor':0,'at':[0,0],'size':[20,10],
                     'workspace':{'id':1},'mapped':True}
        self.raw_buffer=io.BytesIO()
        Image.new('RGB',(20,10),(12,34,56)).save(self.raw_buffer,format='PPM')
        self.raw=self.raw_buffer.getvalue()
        self.stack=ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(cu.stop_precapture)
        self.stack.enter_context(patch.object(indicator,'request',return_value=False))
        self.stack.enter_context(patch.object(indicator.socket,'socket',
                                              side_effect=AssertionError('live indicator socket used')))
        self.window_patch=self.stack.enter_context(patch.object(cu,'window',side_effect=self.fake_window))
        self.stack.enter_context(patch.object(cu,'hypr',side_effect=self.fake_hypr))

    def fake_window(self,env,address):
        return dict(self.client)

    def fake_hypr(self,env,query):
        if query=='monitors':return [dict(self.monitor)]
        raise AssertionError('unexpected compositor query '+query)

    def stale_frame(self,**changes):
        identity=cu._capture_identity({})
        return {'image':Image.new('RGB',(20,10),(1,2,3)),'region':[0,0,20,10],
                'window':'0x1','window_bounds':[0,0,20,10],'monitor':'test',
                'monitor_box':[0,0,20,10],'monitor_scale':1,'monitor_transform':0,
                'capture_ms':5,'decode_ms':2,**identity,**changes}

    def test_threaded_prefetch_removes_capture_and_decode_from_observe(self):
        allow_background=threading.Event()
        real_window=self.window_patch.side_effect

        def hold_background_until_first_capture(env,address):
            if threading.current_thread().name=='cu-pre-capture':
                allow_background.wait(1)
            return real_window(env,address)

        self.window_patch.side_effect=hold_background_until_first_capture

        class FakeGrim:
            def __init__(self,*args,**kwargs):
                self.returncode=0
                self.terminated=False
            def communicate(self,timeout=None):
                time.sleep(.01)
                return self.raw,b''
            def poll(self):return self.returncode
            def terminate(self):self.terminated=True;self.returncode=-15
            def kill(self):self.returncode=-9
            def wait(self,timeout=None):return self.returncode

        def fake_popen(*args,**kwargs):
            child=FakeGrim(*args,**kwargs)
            child.raw=self.raw
            return child

        def fresh_capture(*args,**kwargs):
            time.sleep(.05)
            return self.raw

        with patch.dict(os.environ,{'CU_PRECAPTURE':'1'}), \
             patch.object(cu.subprocess,'Popen',side_effect=fake_popen) as popen, \
             patch.object(cu,'run',side_effect=fresh_capture) as run:
            _,fresh=cu.observe({},'0x1',persist=False)
            allow_background.set()
            manager=cu._PRECACHE_MANAGER
            deadline=time.monotonic()+2
            while manager.frame is None and time.monotonic()<deadline:
                time.sleep(.005)
            self.assertIsNotNone(manager.frame,'background capture did not publish a frame')
            _,cached=cu.observe({},'0x1',persist=False)
            manager.pause()

        self.assertEqual(run.call_count,1,'the warm observe must avoid grim')
        self.assertEqual(popen.call_count,1,'the daemon must capture the next frame')
        self.assertTrue(manager.thread.is_alive())
        self.assertTrue(manager.thread.daemon)
        self.assertFalse(fresh['prefetched'])
        self.assertTrue(cached['prefetched'])
        self.assertLessEqual(cached['prefetch_age_ms'],1000)
        self.assertEqual(cached['image_size'],[20,10])
        fresh_ms=fresh['capture_ms']+fresh['decode_ms']
        cached_ms=cached['capture_ms']+cached['decode_ms']
        self.assertLess(cached_ms,fresh_ms)
        print('H6_METRICS capture_decode_ms fresh=%.3f cached=%.3f' % (fresh_ms,cached_ms))

    def test_stale_prefetched_frame_is_discarded_and_fresh_capture_used(self):
        manager=cu.WindowPreCapture({},'0x1')
        manager.frame=self.stale_frame(capture_started_monotonic=time.monotonic()-1.01)
        with patch.dict(os.environ,{'CU_PRECAPTURE':'1'}), \
             patch.object(cu,'_ensure_precapture',return_value=manager), \
             patch.object(cu,'run',return_value=self.raw) as capture:
            _,result=cu.observe({},'0x1',persist=False)
        capture.assert_called_once()
        self.assertIsNone(manager.frame)
        self.assertFalse(result['prefetched'])

    def test_moved_prefetched_geometry_is_discarded_and_recaptured(self):
        manager=cu.WindowPreCapture({},'0x1')
        manager.frame=self.stale_frame(window_bounds=[1,0,20,10])
        with patch.dict(os.environ,{'CU_PRECAPTURE':'1'}), \
             patch.object(cu,'_ensure_precapture',return_value=manager), \
             patch.object(cu,'run',return_value=self.raw) as capture:
            _,result=cu.observe({},'0x1',persist=False)
        capture.assert_called_once()
        self.assertIsNone(manager.frame)
        self.assertFalse(result['prefetched'])

    def test_kill_switch_skips_manager_and_uses_original_capture(self):
        with patch.dict(os.environ,{'CU_PRECAPTURE':'0'}), \
             patch.object(cu,'_ensure_precapture') as ensure, \
             patch.object(cu,'run',return_value=self.raw) as capture:
            _,result=cu.observe({},'0x1',persist=False)
        ensure.assert_not_called()
        capture.assert_called_once()
        self.assertFalse(result['prefetched'])


if __name__=='__main__':unittest.main()

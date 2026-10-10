import unittest
from unittest.mock import patch
from PIL import Image
from test_keyboard_preflight import cu, DesktopPreflight


class FastAct(DesktopPreflight):
    def test_skip_after_keeps_preflight(self):
        with patch.object(cu,'observe',wraps=self.observe) as capture:
            result=cu.desktop_act({},self.meta,[{'type':'type','text':'hello'}],after_capture=False)
        self.assertTrue(result['ok'])
        self.assertTrue(result['after_skipped'])
        self.assertNotIn('after',result)
        self.assertEqual(capture.call_count,1)
        self.assertFalse(capture.call_args.kwargs['persist'])

    def test_error_still_captures(self):
        self.typed.side_effect=RuntimeError('injected input error')
        result=cu.desktop_act({},self.meta,[{'type':'type','text':'hello'}],after_capture=False)
        self.assertFalse(result['ok'])
        self.assertIn('after',result)
        self.assertNotIn('after_skipped',result)


class SettledObserve(unittest.TestCase):
    def run_wait(self,images,budget=500):
        clock=[0.0];calls=[0]
        def capture():
            image=images[min(calls[0],len(images)-1)];calls[0]+=1
            return image,{'backend':'desktop'}
        def wait(seconds):clock[0]+=seconds
        with patch.object(cu,'check_cancel'),patch.object(cu.time,'monotonic',side_effect=lambda:clock[0]), \
             patch.object(cu,'wait_cancelable',side_effect=wait), \
             patch.object(cu,'save_observation',side_effect=lambda image,meta,width:meta):
            return cu.settled_observation(capture,budget,1280)

    def test_stable_requires_multiple_samples(self):
        result=self.run_wait([Image.new('RGB',(10,10))])
        self.assertTrue(result['settle_stable'])
        self.assertGreaterEqual(result['settle_ms'],120)
        self.assertGreaterEqual(result['settle_samples'],3)

    def test_changed_pixels_restart_stability(self):
        a=Image.new('RGB',(10,10),'black');b=Image.new('RGB',(10,10),'white')
        result=self.run_wait([a,b,b,b,b])
        self.assertTrue(result['settle_stable'])
        self.assertGreaterEqual(result['settle_ms'],180)

    def test_timeout_returns_unstable(self):
        images=[Image.new('RGB',(10,10),(i,0,0)) for i in range(20)]
        result=self.run_wait(images,100)
        self.assertFalse(result['settle_stable'])
        self.assertEqual(result['settle_ms'],100)

    def test_invalid_budget_preflight(self):
        with self.assertRaises(ValueError):cu.settled_observation(lambda:None,2001,1280)

    def test_same_bytes_different_dimensions_restart_stability(self):
        a=Image.new('RGB',(10,10));b=Image.new('RGB',(20,5))
        result=self.run_wait([a,b,b,b,b])
        self.assertGreaterEqual(result['settle_ms'],180)

    def test_cancel_stops_before_capture(self):
        with patch.object(cu,'check_cancel',side_effect=RuntimeError('cancelled')):
            with self.assertRaisesRegex(RuntimeError,'cancelled'):
                cu.settled_observation(lambda:self.fail('capture called'),500,1280)


if __name__=='__main__':unittest.main()

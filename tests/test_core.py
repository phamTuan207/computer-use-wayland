import importlib.util
import pathlib
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

path=pathlib.Path(__file__).resolve().parents[1]/'scripts/cu.py'
spec=importlib.util.spec_from_file_location('cu',path);cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)

class Coordinates(unittest.TestCase):
    def test_cancel_interrupts_running_adapter_and_latches(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'CANCEL',pathlib.Path(folder)/'cancelled'):
            def cancel_soon():
                time.sleep(.12)
                cu.CANCEL.write_text('cancelled')
            thread=threading.Thread(target=cancel_soon)
            thread.start()
            start=time.monotonic()
            with self.assertRaisesRegex(RuntimeError,'cancelled by user'):
                cu.run_cancelable(['python3','-c','import time; time.sleep(3)'],timeout=4)
            thread.join()
            self.assertLess(time.monotonic()-start,1)
            with self.assertRaisesRegex(RuntimeError,'cancelled by user'):cu.check_cancel()

    def test_resized_crop_with_negative_monitor_origin(self):
        m={'image_size':[640,400],'region':[-1500,200,1280,800]}
        self.assertEqual(cu.image_point(m,320,200),(-860,600))
    def test_fractional_scale_and_rotated_monitor(self):
        m={'width':1920,'height':1200,'scale':1.5,'transform':1,'x':-800,'y':20}
        self.assertEqual(cu.monitor_box(m),[-800,20,800,1280])
    def test_screen_crop_maps_negative_monitor_origin_and_rejects_overflow(self):
        self.assertEqual(cu.screen_region([-800,20,800,1280],[10,30,50,100]),[-790,50,50,100])
        for crop in ([0,0,0,10],[-1,0,10,10],[790,0,20,10]):
            with self.subTest(crop=crop),self.assertRaises(ValueError):cu.screen_region([-800,20,800,1280],crop)
    def test_screen_observation_rejects_keyboard_before_input(self):
        meta={'backend':'desktop','scope':'screen','created':time.time()}
        with patch.object(cu,'focus') as focus,patch.object(cu,'Pointer') as pointer:
            with self.assertRaisesRegex(ValueError,'pointer actions only'):
                cu.desktop_act({},meta,[{'type':'key','keys':['a']}])
            focus.assert_not_called();pointer.assert_not_called()
    def test_reject_invalid_points(self):
        m={'image_size':[640,400],'region':[0,0,1280,800]}
        for x,y in [(640,0),(-1,20),(0,400),(float('nan'),0),(float('inf'),0)]:
            with self.subTest(x=x,y=y),self.assertRaises(ValueError):cu.image_point(m,x,y)
    def test_clipped_window(self):
        self.assertEqual(cu.intersect([-20,10,200,100],[0,0,1920,1200]),[0,10,180,100])
    def test_outside_monitor(self):
        with self.assertRaises(ValueError):cu.intersect([2000,0,200,100],[0,0,1920,1200])
    def test_validate_bad_batches(self):
        for a in ([],[{'type':'shell'}],[{'type':'wait','ms':-1}],[{'type':'type','text':10}],[{'type':'key','keys':'Ctrl+A'}],[{'type':'wait'}]*33):
            with self.subTest(a=a),self.assertRaises(ValueError):cu.validate_actions(a,'desktop')
    def test_key_aliases(self):
        self.assertEqual(cu.key_names(['CTRL','Enter']),(['ctrl'],['Return']))
        self.assertEqual(cu.key_names(['Shift','ArrowLeft','PageUp','f12']),(['shift'],['Left','Prior','F12']))
        self.assertEqual(cu.key_names(['Shift','Tab']),(['shift'],['ISO_Left_Tab']))
    def test_bad_key_and_non_bmp_rejected_before_execution(self):
        for a in ([{'type':'key','keys':['not_a_key']}],[{'type':'type','text':'🐱'}],[{'type':'key','keys':['Ctrl']}],[{'type':'key','keys':['a'],'repeat':999}]):
            with self.assertRaises(ValueError):cu.validate_actions(a,'desktop')
    def test_delay_reset_starts_another_wtype_process(self):
        a=[{'type':'type','text':'a','delay_ms':10},{'type':'key','keys':['Left']},{'type':'type','text':'b','delay_ms':0}]
        self.assertEqual([len(g) for g in cu.keyboard_groups(a)],[2,1])
    def test_restore_ime_on_typing_failure(self):
        calls=[];state=['2']
        def remote(argv,env):
            calls.append(argv)
            if len(argv)>1:state[0]='1' if argv[1]=='-c' else '2';return ''
            return state[0]
        with patch.object(cu.shutil,'which',return_value='fcitx5-remote'),patch.object(cu,'run',side_effect=remote):
            with self.assertRaisesRegex(RuntimeError,'typing failed'):
                with cu.literal_keyboard({}):
                    self.assertEqual(state[0],'1')
                    raise RuntimeError('typing failed')
        self.assertEqual(state[0],'2')
        self.assertEqual([x[1] for x in calls if len(x)>1],['-c','-o'])
    def test_focus_and_composition_boundaries(self):
        actions=[{'type':'key','keys':['Ctrl','a']},{'type':'type','text':'test'},{'type':'key','keys':['Tab']},{'type':'type','text':'chaof','ime':'compose'},{'type':'type','text':'test'}]
        groups=cu.keyboard_groups(actions)
        self.assertEqual([len(g) for g in groups],[2,1,1,1])
    def test_compact_observation_retains_paths_not_internal_geometry(self):
        meta={'backend':'desktop','image':'a.png','observation':'a.json','image_size':[400,200],'window_bounds':[0,0,800,400]}
        output=cu.compact_result({'ok':False,'completed':0,'after':meta})
        self.assertEqual(output['after']['observation'],'a.json')
        self.assertNotIn('window_bounds',output['after'])
        self.assertIn('window_bounds',meta)
    def test_reject_invalid_window_before_dispatch(self):
        with self.assertRaises(ValueError):cu.focus({},'bad") os.execute("bad')
    def test_small_target_change_detected_without_global_change(self):
        from PIL import Image,ImageDraw
        old=Image.new('RGB',(1280,800),'white');new=old.copy()
        ImageDraw.Draw(new).rectangle((200,200,223,223),fill='black')
        self.assertTrue(cu.screen_changed(old,new,[{'type':'click','x':211,'y':211}]))
        self.assertFalse(cu.screen_changed(old,new,[{'type':'click','x':800,'y':500}]))

if __name__=='__main__':unittest.main()

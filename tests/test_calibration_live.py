"""Move-only calibration orchestration tests with an in-memory fake broker."""
import json
from pathlib import Path
import tempfile
import types
import unittest

from PIL import Image,ImageDraw
from unittest.mock import patch

import calibration_live as calibration
import cu


class FakeBroker:
    def __init__(self,state,window='0x1',miss_by=0,cancelled=False):
        self.state=state;self.window=window;self.miss_by=miss_by
        self.cancelled=cancelled
        self.env={'XDG_RUNTIME_DIR':str(state),'WAYLAND_DISPLAY':'wayland-test',
                  'HYPRLAND_INSTANCE_SIGNATURE':'calibration-test'}
        self.cursor={'x':20.0,'y':30.0};self.actions=[];self.sent_actions=[]

    def _save(self,scope,monitor='fake',window=None,bounds=None,region=None,crop=None,width=320):
        if scope=='window':
            monitor_box=[20,30,100,80]
            region=region or bounds
            size=[region[2],region[3]]
            meta={'backend':'desktop','scope':'window','window':window,
                  'window_bounds':bounds,'monitor':monitor,'monitor_box':monitor_box,
                  'monitor_scale':1,'monitor_transform':0,'region':region,'crop':crop,
                  'capture_ms':2,'decode_ms':1,'capture_elapsed_ms':3,
                  **cu._capture_identity(self.env)}
        else:
            monitor_box=[20,30,100,80]
            region=monitor_box.copy();size=[100,80]
            meta={'backend':'desktop','scope':'screen','monitor':monitor,
                  'monitor_box':monitor_box,'monitor_scale':1,'monitor_transform':0,
                  'region':region,'crop':None,'capture_ms':2,'decode_ms':1,
                  'capture_elapsed_ms':3,**cu._capture_identity(self.env)}
        image=Image.new('RGB',tuple(size),'black')
        saved=cu.save_observation(image,meta,width)
        return cu.compact_result(saved)

    def run(self,args,stdin=''):
        self.actions.append(list(args))
        if args[0]=='windows':
            return [{'address':self.window,'at':[25,35],'size':[60,40]}]
        if args[0]=='status':return {'ok':True,'cancelled':self.cancelled}
        if args[0]=='doctor':return {'cursorpos':dict(self.cursor),'active_window':self.window}
        if args[0]=='observe' and '--screen' in args:
            return self._save('screen',monitor=args[args.index('--screen')+1],width=3840)
        if args[0]=='observe':
            window=args[args.index('--window')+1]
            width=int(args[args.index('--max-width')+1])
            bounds=[25,35,60,40]
            crop=None
            if '--crop' in args:crop=[int(value) for value in args[args.index('--crop')+1:args.index('--crop')+5]]
            region=bounds if crop is None else [bounds[0]+crop[0],bounds[1]+crop[1],crop[2],crop[3]]
            return self._save('window',window=window,bounds=bounds,region=region,crop=crop,width=width)
        if args[0]=='act':
            observation=json.loads(Path(args[args.index('--observation')+1]).read_text())
            if args[args.index('--actions')+1]!='-':
                raise AssertionError('actions must travel in the broker stdin envelope')
            actions=json.loads(stdin)
            self.assert_move_only(actions)
            self.sent_actions.append(actions)
            self.cursor={'x':cu.image_point(observation,actions[0]['x'],actions[0]['y'])[0]+self.miss_by,
                         'y':cu.image_point(observation,actions[0]['x'],actions[0]['y'])[1]}
            return {'ok':True,'completed':1,'preflight_ms':2,'execution_ms':1}
        raise AssertionError('unexpected broker command: '+repr(args))

    @staticmethod
    def assert_move_only(actions):
        if not isinstance(actions,list) or len(actions)!=1 or actions[0].get('type')!='move':
            raise AssertionError('calibration sent a non-move action')


class CalibrationTests(unittest.TestCase):
    def args(self,folder,**changes):
        values={'lease_file':str(Path(folder)/'lease.json'),'window':'0x1',
                'output':str(Path(folder)/'calibration.json'),'widths':[320],
                'measure_only':False,'samples':3}
        values.update(changes)
        return types.SimpleNamespace(**values)

    def cursor_capture(self,broker,monitor,path):
        image=Image.new('RGB',(100,80),'black')
        local_x=round(broker.cursor['x']-20);local_y=round(broker.cursor['y']-30)
        ImageDraw.Draw(image).point((local_x,local_y),fill='white')
        image.save(path,format='PNG')

    def test_calibration_uses_only_move_and_records_paired_cursor_evidence(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'):
            cu.STATE.mkdir()
            broker=FakeBroker(cu.STATE)
            result=calibration.run_calibration(self.args(folder),broker,
                cursor_capture=lambda monitor,path:self.cursor_capture(broker,monitor,path))
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['sample_count'],10)
        self.assertTrue(all(sample['status']=='move passed' for sample in result['samples']))
        self.assertTrue(all(sample['cursor_evidence']['cursor_visible'] for sample in result['samples']))
        self.assertTrue(all(sample['client_timing']['submit_to_result_ms']>=0 for sample in result['samples']))
        self.assertEqual(result['phase_summaries']['execution_ms']['count'],10)
        self.assertEqual(result['phase_summaries']['image_bytes']['count'],10)
        for actions in broker.sent_actions:self.assertEqual([action['type'] for action in actions],['move'])

    def test_measure_mode_is_bounded_move_only_and_has_no_click_image_step(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'):
            cu.STATE.mkdir()
            broker=FakeBroker(cu.STATE)
            args=self.args(folder,measure_only=True,samples=3)
            result=calibration.run_calibration(args,broker)
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['sample_count'],3)
        self.assertEqual(result['cursor_visual_acceptance'],'not checked')
        self.assertFalse(any('--screen' in command for command in broker.actions if command[0]=='observe'))

    def test_fixture_miss_stops_after_one_move_and_retains_numeric_evidence(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'):
            cu.STATE.mkdir()
            broker=FakeBroker(cu.STATE,miss_by=4)
            result=calibration.run_calibration(self.args(folder),broker)
        self.assertFalse(result['ok'])
        self.assertIn('3 logical pixels',result['error'])
        self.assertEqual(result['sample_count'],1)
        self.assertGreater(result['samples'][0]['error_euclidean'],3)
        self.assertEqual(sum(command[0]=='act' for command in broker.actions),1)

    def test_non_fixture_window_refuses_before_input(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'):
            cu.STATE.mkdir()
            broker=FakeBroker(cu.STATE,window='0x2')
            with self.assertRaisesRegex(calibration.CalibrationError,'unique inert calibration fixture'):
                calibration.run_calibration(self.args(folder),broker)
        self.assertFalse(any(command[0]=='act' for command in broker.actions))

    def test_cancelled_task_refuses_before_fixture_discovery_or_input(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'):
            cu.STATE.mkdir()
            broker=FakeBroker(cu.STATE,cancelled=True)
            with self.assertRaisesRegex(calibration.CalibrationError,'cancellation'):
                calibration.run_calibration(self.args(folder),broker)
        self.assertEqual([command[0] for command in broker.actions],['status'])
        self.assertFalse(broker.sent_actions)


if __name__=='__main__':unittest.main()

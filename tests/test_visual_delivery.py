import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from visual_delivery import VisualCheckpoint
import session_driver


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.gate = VisualCheckpoint()

    def response(self, name, pixels=b'owned-png-bytes', **changes):
        image = self.folder / (name + '.png');image.write_bytes(pixels)
        observation = self.folder / (name + '.json')
        meta = dict(backend='desktop', image=str(image), scope='window', window='0x1',
                    monitor='owned', region=[0,0,100,80], image_size=[100,80],
                    monitor_box=[0,0,1920,1080], monitor_scale=1, monitor_transform=0,
                    window_bounds=[0,0,100,80])
        meta.update(changes);observation.write_text(json.dumps(meta))
        return {'returncode':0, 'result':{'image':str(image), 'observation':str(observation)}}

    def test_exact_repeat_references_last_delivered_frame(self):
        a,b,c = [self.response(x) for x in ('a','b','c')]
        self.assertEqual(self.gate.assess(a)['status'], 'required')
        for response in (b,c):
            hint = self.gate.assess(response)
            self.assertEqual(hint['status'], 'unchanged')
            self.assertEqual(hint['same_as'], a['result']['image'])

    def test_pixel_or_coordinate_context_change_requires_image(self):
        changes = [dict(pixels=b'changed'),dict(window='0x2'),dict(region=[1,0,100,80]),
                   dict(monitor='other'),dict(image_size=[50,40]),dict(monitor_scale=2),
                   dict(monitor_transform=1),dict(window_bounds=[0,0,101,80])]
        for change in changes:
            with self.subTest(change=change):
                self.gate.clear();self.gate.assess(self.response('a'))
                self.assertEqual(self.gate.assess(self.response('b', **change))['status'],'required')

    def test_errors_refusals_and_unknown_metadata_never_suppress_images(self):
        for error in ('returncode','stderr','ok','error','capture_error','ime_restore_failed','after_unavailable'):
            with self.subTest(error=error):
                self.gate.clear();self.gate.assess(self.response('a'))
                response = self.response('b')
                if error in ('returncode','stderr'):response[error] = 1
                else:response['result'][error] = False if error == 'ok' else True
                self.assertEqual(self.gate.assess(response)['status'],'required')
                self.assertEqual(self.gate.assess(self.response('c'))['status'],'required')
        response = self.response('bad',backend='unknown')
        self.assertEqual(self.gate.assess(response)['status'],'required')
        Path(response['result']['observation']).unlink()
        self.assertEqual(self.gate.assess(response)['status'],'required')

    def test_nonvisual_response_resets_and_final_action_frame_is_supported(self):
        self.gate.assess(self.response('a'))
        self.assertIsNone(self.gate.assess({'returncode':0,'result':{'ok':True}}))
        response = self.response('b')
        response['result'] = {'ok':True,'after':response['result']}
        self.assertEqual(self.gate.assess(response)['status'],'required')
        self.assertEqual(self.gate.assess(self.response('c'))['status'],'unchanged')

    def test_removed_referenced_png_promotes_next_identical_frame(self):
        first = self.response('a')
        self.assertEqual(self.gate.assess(first)['status'], 'required')
        Path(first['result']['image']).unlink()
        second = self.response('b')
        self.assertEqual(self.gate.assess(second)['status'], 'required')
        repeat = self.gate.assess(self.response('c'))
        self.assertEqual(repeat['status'], 'unchanged')
        self.assertEqual(repeat['same_as'], second['result']['image'])

    def test_screen_scope_without_window_key_is_tracked(self):
        def screen_response(name, pixels=b'owned-png-bytes'):
            image = self.folder / (name + '.png');image.write_bytes(pixels)
            observation = self.folder / (name + '.json')
            meta = dict(backend='desktop', image=str(image), scope='screen', monitor='owned',
                        region=[0,0,100,80], image_size=[100,80], monitor_box=[0,0,1920,1080],
                        monitor_scale=1, monitor_transform=0)
            observation.write_text(json.dumps(meta))
            return {'returncode':0, 'result':{'image':str(image), 'observation':str(observation)}}
        a,b = screen_response('a'), screen_response('b')
        self.assertEqual(self.gate.assess(a)['status'], 'required')
        hint = self.gate.assess(b)
        self.assertEqual(hint['status'], 'unchanged')
        self.assertEqual(hint['same_as'], a['result']['image'])

    def test_driver_auto_is_opt_in_and_always_preserves_result(self):
        frame = self.response('a')['result']
        for policy in (None,'auto','always'):
            request = {'args':['observe','--screen','owned']}
            if policy:request['image_policy'] = policy
            output = io.StringIO()
            with patch.object(session_driver,'execute',return_value=subprocess.CompletedProcess([],0,json.dumps(frame),'')):
                session_driver.relay_commands(io.StringIO(json.dumps(request)+'\n'+json.dumps(request)),output)
            replies = [json.loads(line) for line in output.getvalue().splitlines()][1:]
            self.assertEqual(replies[1]['result'],frame)
            if policy == 'auto':self.assertEqual(replies[1]['visual']['status'],'unchanged')
            else:self.assertNotIn('visual',replies[1])

    def test_invalid_delivery_policy_never_executes_input(self):
        with patch.object(session_driver,'execute') as execute:
            with self.assertRaises(ValueError):
                session_driver.relay_commands(io.StringIO('{"args":["act"],"image_policy":"never"}'),io.StringIO())
            execute.assert_not_called()

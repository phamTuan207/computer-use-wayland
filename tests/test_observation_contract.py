"""Desktop observation identity, image integrity, and explicit environment tests."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cu


def observation_meta(scope='window'):
    meta={'backend':'desktop','observation_schema':cu.OBSERVATION_SCHEMA,
          'image_role':'clean-observation','scope':scope,'window':'0x1',
          'window_bounds':[100,200,1000,333],'monitor':'eDP-2',
          'monitor_box':[50,100,1920,1200],'monitor_scale':1,
          'monitor_transform':0,'region':[100,200,1000,333],
          'image_size':[320,107],'crop':None,'max_width':320,
          **cu._capture_identity({})}
    meta['created']=time.time()
    return meta


class ObservationContract(unittest.TestCase):
    def test_saved_png_identity_and_two_axis_scale_survive_compaction(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)):
            image=Image.new('RGB',(1000,333),(5,10,15))
            saved=cu.save_observation(image,observation_meta(),320)
            compact=cu.compact_result(saved)
            self.assertEqual(compact['image_size'],[320,107])
            self.assertEqual(compact['scale_x'],320/1000)
            self.assertEqual(compact['scale_y'],107/333)
            for key in ('id','created','region','window','window_bounds','monitor',
                        'monitor_box','monitor_scale','monitor_transform','image_bytes',
                        'image_format','image_sha256','capture_boot_id','capture_compositor'):
                self.assertEqual(compact[key],saved[key])
            self.assertEqual(cu.image_point(saved,160,53),
                             (100+160*1000/320,200+53*333/107))
            self.assertTrue(cu.validate_desktop_observation(saved,{}))

    def test_saved_observation_refuses_changed_png_and_metadata(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)):
            saved=cu.save_observation(Image.new('RGB',(1000,333)),observation_meta(),320)
            Path(saved['image']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'PNG changed'):
                cu.validate_desktop_observation(saved,{},saved['observation'])
            second=cu.save_observation(Image.new('RGB',(1000,333)),observation_meta(),320)
            disk=json.loads(Path(second['observation']).read_text())
            disk['capture_started_wall']+=1
            Path(second['observation']).write_text(json.dumps(disk))
            with self.assertRaisesRegex(ValueError,'file changed'):
                cu.validate_desktop_observation(second,{},second['observation'])

    def test_stale_boot_and_compositor_metadata_are_rejected(self):
        meta=observation_meta()
        with patch.object(cu.time,'monotonic',return_value=meta['capture_started_monotonic']+90.01):
            with self.assertRaisesRegex(ValueError,'older than 90s'):
                cu.validate_desktop_observation(meta,{})
        with patch.object(cu,'boot_identity',return_value='00000000-0000-0000-0000-000000000000'):
            with self.assertRaisesRegex(ValueError,'another system boot'):
                cu.validate_desktop_observation(meta,{})
        stale=dict(meta,capture_compositor={'instance':'replacement'})
        with self.assertRaisesRegex(ValueError,'another compositor instance'):
            cu.validate_desktop_observation(stale,{})

    def test_legacy_metadata_is_not_treated_as_a_fresh_observation(self):
        legacy=observation_meta()
        for key in ('observation_schema','capture_started_monotonic',
                    'capture_started_wall','capture_boot_id','capture_compositor'):
            legacy.pop(key)
        with self.assertRaisesRegex(ValueError,'legacy observation'):
            cu.validate_desktop_observation(legacy, {})

    def test_invalid_dimensions_and_regions_fail_before_coordinate_mapping(self):
        meta={'image_size':[320,107],'region':[100,200,1000,333],
              'max_width':320,'monitor_box':[50,100,1920,1200]}
        for changed in (dict(meta,image_size=[320,float('nan')]),
                        dict(meta,region=[100,200,0,333]),
                        dict(meta,region=[0,0,2000,333])):
            with self.subTest(meta=changed),self.assertRaises(ValueError):
                cu.image_point(changed,0,0)
        with self.assertRaisesRegex(ValueError,'finite coordinates'):
            cu.image_point({'image_size':[1,1],'region':[0,0,1,1]},10**1000,0)
        with self.assertRaisesRegex(ValueError,'monitor_scale'):
            cu.validate_coordinate_metadata(dict(observation_meta(),monitor_scale=10**1000),
                                            require_frame=True)

    def test_diagnostic_log_is_private_and_does_not_echo_input_text(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)),\
                patch.dict(os.environ,{'CU_SESSION_TOKEN':'f'*32}):
            meta=observation_meta();cu._diagnostic_event(
                'typing_started',meta,{},action_type='type',error='typing failed: private text')
            name='diagnostics-'+hashlib.sha256(('f'*32).encode()).hexdigest()[:16]+'.jsonl'
            path=Path(folder)/name
            row=json.loads(path.read_text())
            self.assertEqual(os.stat(path).st_mode & 0o777,0o600)
            self.assertEqual(row['target']['monitor'],'eDP-2')
            self.assertEqual(row['error'],'operation_failed')
            self.assertNotIn('private text',path.read_text())


class EnvironmentSelection(unittest.TestCase):
    def endpoint(self,folder,instance='host-signature',display='wayland-1'):
        runtime=Path(folder);(runtime/'hypr'/instance).mkdir(parents=True)
        sockets=[]
        for path in (runtime/display,runtime/'hypr'/instance/'.socket.sock'):
            sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            sock.bind(str(path));sockets.append(sock)
        self.addCleanup(lambda:[sock.close() for sock in sockets])
        return {'XDG_RUNTIME_DIR':str(runtime),'WAYLAND_DISPLAY':display,
                'HYPRLAND_INSTANCE_SIGNATURE':instance}

    def test_explicit_verified_host_tuple_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            chosen=self.endpoint(folder)
            def run(argv,**kwargs):
                if argv==['hyprctl','-j','instances']:
                    return subprocess.CompletedProcess(argv,0,json.dumps([
                        {'instance':'host-signature','wl_socket':'wayland-1'}]),'')
                if argv[:2]==['pgrep','-x']:
                    return subprocess.CompletedProcess(argv,1,'','')
                raise AssertionError(argv)
            with patch.dict(os.environ,chosen,clear=True),\
                    patch.object(cu.subprocess,'run',side_effect=run),\
                    patch.object(cu,'_process_donors',wraps=cu._process_donors) as scan:
                found=cu.environment()
            scan.assert_called_once()
            self.assertEqual(cu._session_tuple(found),chosen)

    def test_stale_explicit_tuple_refuses_without_falling_back(self):
        with tempfile.TemporaryDirectory() as folder:
            stale={'XDG_RUNTIME_DIR':folder,'WAYLAND_DISPLAY':'wayland-1',
                   'HYPRLAND_INSTANCE_SIGNATURE':'stale'}
            with patch.dict(os.environ,stale,clear=True),patch.object(cu.subprocess,'run') as run:
                with self.assertRaisesRegex(RuntimeError,'refusing to switch compositor'):
                    cu.environment()
            run.assert_not_called()

    def test_live_task_without_explicit_tuple_does_not_scan_other_processes(self):
        with patch.dict(os.environ,{'CU_SESSION_TOKEN':'a'*32},clear=True),\
                patch.object(cu.subprocess,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'pinned compositor tuple'):
                cu.environment()
        run.assert_not_called()

    def test_live_task_with_invalid_tuple_refuses_even_when_refreshing(self):
        with patch.dict(os.environ,{'CU_SESSION_TOKEN':'a'*32,
                                    'XDG_RUNTIME_DIR':'/missing/runtime',
                                    'WAYLAND_DISPLAY':'wayland-1',
                                    'HYPRLAND_INSTANCE_SIGNATURE':'stale'},clear=True),\
                patch.object(cu.subprocess,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'explicit Wayland socket is unavailable'):
                cu.environment(refresh=True)
        run.assert_not_called()

    def test_valid_pinned_task_tuple_is_returned_without_discovery_and_strips_gtk(self):
        with tempfile.TemporaryDirectory() as folder:
            chosen=self.endpoint(folder)
            env={**chosen,'CU_SESSION_TOKEN':'a'*32,'GTK_IM_MODULE':'fcitx'}
            def run(argv,**kwargs):
                if argv==['hyprctl','-j','instances']:
                    return subprocess.CompletedProcess(argv,0,json.dumps([
                        {'instance':'host-signature','wl_socket':'wayland-1'}]),'')
                raise AssertionError('pinned tuple must not scan processes')
            with patch.object(cu.subprocess,'run',side_effect=run):
                found=cu.environment(env,refresh=True)
            self.assertEqual(cu._session_tuple(found),chosen)
            self.assertNotIn('GTK_IM_MODULE',found)


if __name__=='__main__':unittest.main()

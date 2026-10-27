import contextlib
import importlib.util
import pathlib
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

path=pathlib.Path(__file__).resolve().parents[1]/'scripts/cu.py'
spec=importlib.util.spec_from_file_location('cu',path);cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)

class CliExit(unittest.TestCase):
    def run_cli(self, args):
        import subprocess
        import sys
        # Execute the real entry point, but replace session cleanup entirely.
        # No desktop discovery or live session files can be touched here.
        code='''import os, runpy, sys, types
from unittest.mock import Mock
session = types.ModuleType('cursor_session')
session.request_stop = Mock()
sys.modules['cursor_session'] = session
os.environ['CU_SESSION_TOKEN'] = 'fixture'
sys.argv = sys.argv[1:]
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
finally:
    print('cleanup_calls=' + str(session.request_stop.call_count), file=sys.stderr)
'''
        return subprocess.run([sys.executable,'-c',code,str(path),*args],
                              capture_output=True,text=True,timeout=5)

    def test_help_succeeds_without_stopping_session(self):
        for args in (['--help'],['browser','--help'],['session','--help']):
            with self.subTest(args=args):
                result=self.run_cli(args)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('usage:',result.stdout)
                self.assertNotIn('"ok": false',result.stdout)
                self.assertEqual(result.stderr,'cleanup_calls=0\n')

    def test_invalid_arguments_preserve_exit_code_and_stop_session(self):
        for args in ([],['unknown-command'],['observe']):
            with self.subTest(args=args):
                result=self.run_cli(args)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertEqual(result.stdout,'')
                self.assertIn('error:',result.stderr)
                self.assertTrue(result.stderr.endswith('cleanup_calls=1\n'))

class Coordinates(unittest.TestCase):
    def test_invalid_action_batch_is_typed_preflight_before_focus_or_input(self):
        from unittest.mock import patch
        meta={'backend':'desktop','created':time.time(),'scope':'window',
              'window':'0x1','image':'unused'}
        for actions in ([{'type':'wait','ms':2001}],):
            with self.subTest(actions=actions), \
                 patch.object(cu,'check_cancel'), patch.object(cu,'focus') as focus, \
                 patch.object(cu,'Pointer') as pointer:
                with self.assertRaisesRegex(cu.PreflightRefusal,'wait ms must be 0..2000'):
                    cu.desktop_act({},meta,actions)
                focus.assert_not_called()
                pointer.assert_not_called()

    def test_expired_observation_is_typed_preflight_before_focus_or_input(self):
        meta={'backend':'desktop','created':time.time()-91,'scope':'window',
              'window':'0x1','image':'unused'}
        with patch.object(cu,'check_cancel'), patch.object(cu,'focus') as focus, \
             patch.object(cu,'Pointer') as pointer:
            with self.assertRaisesRegex(cu.PreflightRefusal,'observation older than 90s'):
                cu.desktop_act({},meta,[{'type':'wait','ms':0}])
            focus.assert_not_called()
            pointer.assert_not_called()

    def test_saved_png_preserves_pixels_metadata_and_permissions(self):
        import hashlib
        import json
        import stat
        from PIL import Image
        flat=Image.new('RGB',(640,160),(23,45,67))
        detailed=Image.frombytes('RGB',flat.size,bytes((i*37+i//97)%256 for i in range(640*160*3)))
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',pathlib.Path(folder)):
            for image in (flat,detailed):
                for width in (320,1280):
                    with self.subTest(detailed=image is detailed,max_width=width):
                        expected=image.resize((320,80),Image.Resampling.LANCZOS) if width==320 else image
                        meta=cu.save_observation(image,{},width)
                        with Image.open(meta['image']) as decoded:
                            self.assertEqual(decoded.mode,'RGB')
                            self.assertEqual(decoded.size,expected.size)
                            self.assertEqual(decoded.tobytes(),expected.tobytes())
                        self.assertEqual(meta['image_size'],list(expected.size))
                        self.assertEqual(meta['pixel_sha256'],hashlib.sha256(expected.tobytes()).hexdigest())
                        self.assertEqual(json.loads(pathlib.Path(meta['observation']).read_text()),meta)
                        for key in ('image','observation'):
                            self.assertEqual(stat.S_IMODE(pathlib.Path(meta[key]).stat().st_mode),0o600)

    def test_observation_cleanup_preserves_cursor_recovery_snapshot(self):
        import os
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',pathlib.Path(folder)):
            stale=['session.json','other.json','abcdef012345.json','abcdef012345.png']
            for name in stale:
                item=cu.STATE/name
                item.write_text('retained state')
                os.utime(item,(0,0))
            recent=cu.STATE/'123456abcdef.json'
            recent.write_text('recent observation')
            meta=cu.save_observation(Image.new('RGB',(2,2)),{},1280)
            self.assertEqual((cu.STATE/'session.json').read_text(),'retained state')
            self.assertTrue((cu.STATE/'other.json').exists())
            self.assertFalse((cu.STATE/'abcdef012345.json').exists())
            self.assertFalse((cu.STATE/'abcdef012345.png').exists())
            self.assertTrue(recent.exists())
            self.assertTrue(pathlib.Path(meta['image']).exists())
            self.assertTrue(pathlib.Path(meta['observation']).exists())

    def test_local_state_and_cdp_do_not_discover_desktop_environment(self):
        import io
        for argv in (['cu','status'],['cu','browser','tabs']):
            with self.subTest(argv=argv),patch.object(cu.sys,'argv',argv),patch.object(cu.sys,'stdout',io.StringIO()),patch.object(cu,'environment') as environment,patch.object(cu,'check_cancel'),patch.object(cu,'locked'),patch.object(cu,'browser',return_value={'ok':True}):
                self.assertEqual(cu.main(),0)
                environment.assert_not_called()

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
    def test_preparatory_motion_rechecks_state_after_capture(self):
        from contextlib import ExitStack
        from PIL import Image
        image=Image.new('RGB',(20,20))
        monitor={'name':'test','x':0,'y':0,'width':20,'height':20,'scale':1}
        meta={'backend':'desktop','scope':'window','created':time.time(),
              'window':'fixture','window_bounds':[0,0,20,20],
              'monitor':'test','monitor_box':[0,0,20,20],'monitor_scale':1,
              'monitor_transform':0,'image_size':[20,20],'region':[0,0,20,20],
              'image':'synthetic.png','max_width':1280,'pixel_sha256':'fixture'}
        for defect,error in (('cancel','cancelled'),('window','window geometry changed'),
                             ('monitor','monitor layout changed'),('focus','focus changed')):
            with self.subTest(defect=defect),ExitStack() as stack:
                captured=[False]
                def check_cancel():
                    if captured[0] and defect=='cancel':raise RuntimeError('cancelled')
                def window(env,address):
                    return {'at':[1,0] if captured[0] and defect=='window' else [0,0],
                            'size':[20,20]}
                def hypr(env,query):
                    if query=='monitors':
                        return [dict(monitor,scale=2 if captured[0] and defect=='monitor' else 1)]
                    if query=='activewindow':
                        return {'address':'other' if captured[0] and defect=='focus' else 'fixture'}
                    raise AssertionError('unexpected compositor query')
                def observe(env,address,crop,max_width,**kwargs):
                    if kwargs.get('persist') is False:
                        captured[0]=True
                        return image,meta.copy()
                    return meta.copy()
                # Every desktop operation is mocked; no compositor or input helper runs.
                for name,replacement in (('check_cancel',check_cancel),('window',window),
                                         ('hypr',hypr),('observe',observe)):
                    stack.enter_context(patch.object(cu,name,side_effect=replacement))
                stack.enter_context(patch.object(cu,'focus'))
                stack.enter_context(patch.object(cu.time,'sleep'))
                stack.enter_context(patch('PIL.Image.open',return_value=image))
                pointer=stack.enter_context(patch.object(cu,'Pointer')).return_value
                result=cu.desktop_act({},meta,[{'type':'move','x':10,'y':10}])
                self.assertFalse(result['ok'])
                self.assertEqual(result['completed'],0)
                self.assertIn(error,result['error'])
                pointer.command.assert_not_called()
                pointer.close.assert_called_once()
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
    def test_browser_set_value_payload_validation(self):
        cu.validate_actions([{'type':'set_value','text':'Tạo 🐱'}],'browser')
        for text in (None,'x'*10001):
            with self.subTest(length=len(text) if isinstance(text,str) else None),self.assertRaises(ValueError):
                cu.validate_actions([{'type':'set_value','text':text}],'browser')
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
        def remote(argv,env,timeout=None):
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

class SecureObservationFiles(unittest.TestCase):
    """N7: exclusive 0600 creation before the first byte; no symlink follow."""

    def test_private_mode_under_any_umask_in_isolated_child(self):
        import subprocess
        import sys
        code = ('import os,sys,tempfile,pathlib\n'
                'sys.path.insert(0,' + repr(str(pathlib.Path('scripts').resolve())) + ')\n'
                'import cu\n'
                'from PIL import Image\n'
                'folder=tempfile.mkdtemp()\n'
                'cu.STATE=pathlib.Path(folder)\n'
                'os.umask(' + '{umask}' + ')\n'
                'meta=cu.save_observation(Image.new("RGB",(64,32)),{},1280)\n'
                'import stat\n'
                'print(oct(stat.S_IMODE(pathlib.Path(meta["image"]).stat().st_mode)))\n'
                'print(oct(stat.S_IMODE(pathlib.Path(meta["observation"]).stat().st_mode)))\n')
        for umask in ('0', '0o777'):
            with self.subTest(umask=umask):
                result = subprocess.run([sys.executable, '-c', code.replace('{umask}', umask)],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.split(), ['0o600', '0o600'])

    def test_mode_is_0600_before_the_first_png_byte(self):
        import os
        import stat
        from PIL import Image
        seen = {}

        real_save = Image.Image.save

        def spy(self, fp, *args, **kwargs):
            seen['mode'] = stat.S_IMODE(os.fstat(fp.fileno()).st_mode)
            return real_save(self, fp, *args, **kwargs)

        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)), \
                patch.object(Image.Image, 'save', spy):
            cu.save_observation(Image.new('RGB', (16, 16)), {}, 1280)
        self.assertEqual(seen.get('mode'), 0o600)

    def test_encoded_png_passes_through_byte_exact(self):
        import io
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)):
            buffer = io.BytesIO()
            Image.new('RGB', (32, 16)).save(buffer, format='PNG')
            raw = buffer.getvalue()
            meta = cu.save_observation(Image.new('RGB', (4, 4)), {}, 1280,
                                       encoded_png=raw)
            self.assertEqual(pathlib.Path(meta['image']).read_bytes(), raw)

    def test_token_collision_and_symlink_refuse_without_touching_target(self):
        import io
        import os
        import uuid
        from PIL import Image
        for setup in ('file', 'symlink'):
            with self.subTest(setup=setup), \
                    tempfile.TemporaryDirectory() as folder, \
                    patch.object(cu, 'STATE', pathlib.Path(folder)):
                token = 'abc123def456'
                target = pathlib.Path(folder) / 'target.png'
                target.write_bytes(b'foreign')
                link = cu.STATE / (token + '.png')
                if setup == 'file':
                    link.write_bytes(b'existing')
                else:
                    link.symlink_to(target)
                with patch.object(cu.uuid, 'uuid4',
                                  return_value=uuid.UUID(hex=token + '0' * 20)):
                    with self.assertRaises(OSError):
                        cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280)
                self.assertEqual(target.read_bytes(), b'foreign')
                if setup == 'file':
                    self.assertEqual(link.read_bytes(), b'existing')

    def test_json_collision_refuses_and_leaves_target(self):
        import uuid
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)):
            token = 'abc123def456'
            (cu.STATE / (token + '.json')).write_text('{"kept":true}')
            with patch.object(cu.uuid, 'uuid4',
                              return_value=uuid.UUID(hex=token + '0' * 20)):
                with self.assertRaises(OSError):
                    cu.save_observation(Image.new('RGB', (8, 8)), {}, 320)
            self.assertEqual((cu.STATE / (token + '.json')).read_text(),
                             '{"kept":true}')

    def test_fdopen_or_chmod_failure_closes_fd_and_fails(self):
        import os
        from PIL import Image
        for point, failure in (('fdopen', OSError('fdopen down')),
                               ('fchmod', OSError('fchmod down'))):
            with self.subTest(point=point), \
                    tempfile.TemporaryDirectory() as folder, \
                    patch.object(cu, 'STATE', pathlib.Path(folder)):
                before = set(os.listdir('/proc/self/fd'))
                if point == 'fdopen':
                    patcher = patch.object(cu.os, 'fdopen', side_effect=failure)
                else:
                    patcher = patch.object(cu.os, 'fchmod', side_effect=failure)
                with patcher:
                    with self.assertRaises(OSError):
                        cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280)
                leaked = set(os.listdir('/proc/self/fd')) - before
                self.assertEqual(leaked, set(), 'file descriptor leaked')

    def test_json_second_fd_failures_close_once(self):
        import io
        import os
        from PIL import Image

        class StreamFailer:
            """Delegates everything except one injected failure."""

            def __init__(self, stream, failure):
                object.__setattr__(self, '_s', stream)
                object.__setattr__(self, 'failure', failure)
                object.__setattr__(self, 'failed', False)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return object.__getattribute__(self, '_s').__exit__(*exc)

            def write(self, data):
                if (object.__getattribute__(self, 'failure') == 'write'
                        and not object.__getattribute__(self, 'failed')):
                    object.__setattr__(self, 'failed', True)
                    raise OSError('json write down')
                return object.__getattribute__(self, '_s').write(data)

            def flush(self):
                if object.__getattribute__(self, 'failure') == 'flush':
                    raise OSError('json flush down')
                return object.__getattribute__(self, '_s').flush()

            def __getattr__(self, name):
                return getattr(object.__getattribute__(self, '_s'), name)

        for point in ('fchmod', 'fdopen', 'write', 'flush'):
            with self.subTest(point=point), \
                    tempfile.TemporaryDirectory() as folder, \
                    patch.object(cu, 'STATE', pathlib.Path(folder)):
                opened, closed = [], []
                real_open, real_close = os.open, os.close
                real_fdopen = os.fdopen

                def spy_open(*args, **kwargs):
                    fd = real_open(*args, **kwargs)
                    opened.append(fd)
                    return fd

                def spy_close(fd):
                    closed.append(fd)
                    return real_close(fd)

                fdopens = {'n': 0}

                def rigged_fdopen(fd, mode='r', *args, **kwargs):
                    stream = real_fdopen(fd, mode, *args, **kwargs)
                    fdopens['n'] += 1
                    # PNG uses 'wb' first; the JSON text stream is second.
                    if mode == 'w' and point == 'write':
                        return StreamFailer(stream, point)
                    if mode == 'w' and point == 'flush':
                        # A real flush-time failure: the write buffers fine,
                        # then close() flushes and the OS-level flush raises.
                        buffer = stream.detach()

                        class FlushFailer(io.TextIOWrapper):
                            def flush(self):
                                raise OSError('json flush down')

                        return FlushFailer(buffer, encoding='utf-8')
                    return stream

                patches = [patch.object(cu.os, 'open', side_effect=spy_open),
                           patch.object(cu.os, 'close', side_effect=spy_close),
                           patch.object(cu.os, 'fdopen', side_effect=rigged_fdopen)]
                if point in ('fchmod', 'fdopen'):
                    real_point = getattr(os, point)
                    calls = {'n': 0}

                    def fail_second(target, *args, **kwargs):
                        calls['n'] += 1
                        if calls['n'] == 2:
                            raise OSError(point + ' down')
                        return target(*args, **kwargs)

                    import functools
                    patches.append(patch.object(
                        cu.os, point,
                        side_effect=functools.partial(fail_second, real_point)))
                with contextlib.ExitStack() as stack:
                    for patcher in patches:
                        stack.enter_context(patcher)
                    with self.assertRaisesRegex(OSError, point + ' down'):
                        cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280)
                pngs = [f for f in pathlib.Path(folder).iterdir()
                        if f.suffix == '.png']
                self.assertEqual(len(opened), 2, 'PNG then JSON descriptors opened')
                if point in ('write', 'flush'):
                    # The stream owned its descriptor: the C-level close never
                    # routes through os.close, so no extra rawfd close happens.
                    self.assertEqual(closed, [])
                else:
                    self.assertEqual(closed, [opened[1]])
                with self.assertRaises(OSError):
                    os.fstat(opened[1])

    def test_encoded_passthrough_write_error_closes_once(self):
        import os
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)):
            opened, closed = [], []
            real_open, real_close = os.open, os.close
            real_fdopen = os.fdopen

            def spy_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def spy_close(fd):
                closed.append(fd)
                return real_close(fd)

            def rigged_fdopen(fd, mode='r', *args, **kwargs):
                stream = real_fdopen(fd, mode, *args, **kwargs)
                if mode != 'wb':
                    return stream

                class BinaryFailer:
                    def __enter__(self):
                        return self

                    def __exit__(self, *exc):
                        return stream.__exit__(*exc)

                    def write(self, data):
                        raise OSError('passthrough write down')

                    def __getattr__(self, name):
                        return getattr(stream, name)

                return BinaryFailer()

            buffer = io.BytesIO() if False else None
            import io as _io
            buffer = _io.BytesIO()
            Image.new('RGB', (32, 16)).save(buffer, format='PNG')
            with patch.object(cu.os, 'open', side_effect=spy_open), \
                 patch.object(cu.os, 'close', side_effect=spy_close), \
                 patch.object(cu.os, 'fdopen', side_effect=rigged_fdopen):
                with self.assertRaisesRegex(OSError, 'passthrough write down'):
                    cu.save_observation(Image.new('RGB', (4, 4)), {}, 1280,
                                        encoded_png=buffer.getvalue())
            self.assertEqual(len(opened), 1)
            self.assertEqual(closed, [],
                             'no extra os.close after ownership transferred to the stream')
            with self.assertRaises(OSError):
                os.fstat(opened[0])

    def test_persist_false_creates_no_file(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)):
            cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280, persist=False)
            self.assertEqual(list(pathlib.Path(folder).iterdir()), [])

    def test_fd_closed_exactly_once_on_fchmod_or_fdopen_failure(self):
        import os
        from PIL import Image
        for point in ('fchmod', 'fdopen'):
            with self.subTest(point=point), \
                    tempfile.TemporaryDirectory() as folder, \
                    patch.object(cu, 'STATE', pathlib.Path(folder)):
                opened, closed = [], []
                real_open, real_close = os.open, os.close

                def spy_open(*args, **kwargs):
                    fd = real_open(*args, **kwargs)
                    opened.append(fd)
                    return fd

                def spy_close(fd):
                    closed.append(fd)
                    return real_close(fd)

                with patch.object(cu.os, 'open', side_effect=spy_open), \
                     patch.object(cu.os, 'close', side_effect=spy_close), \
                     patch.object(cu.os, point,
                                  side_effect=OSError(point + ' down')):
                    with self.assertRaises(OSError):
                        cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280)
                self.assertEqual(len(opened), 1, 'one raw descriptor opened')
                self.assertEqual(closed, opened,
                                 'raw descriptor closed exactly once, no foreign fd touched')

    def test_write_failure_closes_stream_once_with_no_extra_close(self):
        import os
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(cu, 'STATE', pathlib.Path(folder)):
            opened, closed = [], []
            real_open, real_close = os.open, os.close

            def spy_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def spy_close(fd):
                closed.append(fd)
                return real_close(fd)

            real_save = Image.Image.save

            def failing_save(self, fp, *args, **kwargs):
                raise OSError('save down')

            with patch.object(cu.os, 'open', side_effect=spy_open), \
                 patch.object(cu.os, 'close', side_effect=spy_close), \
                 patch.object(Image.Image, 'save', failing_save):
                with self.assertRaisesRegex(OSError, 'save down'):
                    cu.save_observation(Image.new('RGB', (8, 8)), {}, 1280)
            self.assertEqual(len(opened), 1)
            self.assertEqual(closed, [],
                             'no extra os.close after ownership transferred to the stream')
            with self.assertRaises(OSError):
                os.fstat(opened[0])
            # EBADF above proves the stream owned and performed the one close.


if __name__=='__main__':unittest.main()

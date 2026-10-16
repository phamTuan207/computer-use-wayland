"""No live GUI: fake hyprctl plus real pipes/processes/signals for lifecycle proof."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cursor_session as session
import cursor_theme
import cu

FAKE = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
p=Path(os.environ['FAKE_DESKTOP'])
s=json.loads(p.read_text())
a=sys.argv[1:]
s['calls'].append(a)
if a==['-j','devices']:print('{"keyboards":[{"name":"test-keyboard"}]}')
elif a==['-j','monitors']:
    print('[]' if s.get('no_monitors') else '[{"name":"test","x":0,"y":0,"width":2,"height":2,"scale":1}]')
elif a and a[0]=='eval':
    if 'hl.bind' in a[1]:s['hotkey_active']=True
    elif ':unbind()' in a[1] and not s.get('unbind_failure'):s['hotkey_active']=False
    if 'hl.bind' in a[1] and s.get('hotkey_failure'):
        p.write_text(json.dumps(s));sys.exit(1)
    elif ':unbind()' in a[1] and 'hl.bind' not in a[1] and s.get('unbind_failure'):
        p.write_text(json.dumps(s));sys.exit(1)
    print('ok')
elif a and a[0]=='setcursor':
    if s.get('apply_failure') and len(a)>1 and a[1]==s.get('agent_theme'):
        print('refused')
    else:print('ok')
else:sys.exit(1)
p.write_text(json.dumps(s))
'''

FAKE_GSETTINGS = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
p=Path(os.environ['FAKE_DESKTOP'])
s=json.loads(p.read_text())
a=sys.argv[1:]
if a[:3]==['get','org.gnome.desktop.interface','cursor-theme']:print(s['gtk_theme'])
elif a[:3]==['get','org.gnome.desktop.interface','cursor-size']:print(s['gtk_size'])
elif a[:3]==['set','org.gnome.desktop.interface','cursor-theme']:s['gtk_theme']="'%s'"%a[3];print('')
elif a[:3]==['set','org.gnome.desktop.interface','cursor-size']:s['gtk_size']=a[3];print('')
else:sys.exit(1)
p.write_text(json.dumps(s))
'''


def write_xcursor(path, size):
    """Minimal valid Xcursor file: one image chunk at the nominal size, no renderer."""
    import struct
    width=height=size
    hot=max(1,size//16)
    pixels=struct.pack('<I',0xFF000000)*(width*height)
    chunk=struct.pack('<IIIIIIIII',36,0xFFFD0002,size,1,width,height,hot,hot,0)+pixels
    toc=struct.pack('<III',0xFFFD0002,size,16+12)
    path.write_bytes(struct.pack('<IIII',0x72756358,16,0x10000,1)+toc+chunk)

FAKE_INDICATOR = '''#!/usr/bin/env python3
import sys
print('ready',flush=True)
for line in sys.stdin:
    print({'hide':'hidden','show':'visible'}.get(line.strip(),'ok'),flush=True)
'''

# Instrumented helper for lifecycle tests: marks itself active in a fixture
# file, exits on a stop trigger or stdin EOF, or fails startup when asked.
TRACKED_INDICATOR = '''#!/usr/bin/env python3
import os,select,sys
active=os.environ.get('INDICATOR_ACTIVE')
if os.environ.get('INDICATOR_FAIL'):
    sys.exit(1)
if active:open(active,'w').write(str(os.getpid()))
print('ready',flush=True)
stop=os.environ.get('INDICATOR_STOP')
try:
    while True:
        if stop and os.path.exists(stop):break
        ready,_,_=select.select([sys.stdin],[],[],0.05)
        if sys.stdin in ready:
            line=sys.stdin.readline()
            if not line:break
            print({'hide':'hidden','show':'visible'}.get(line.strip(),'ok'),flush=True)
finally:
    if active:
        try:os.unlink(active)
        except OSError:pass
'''


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)
        self.desktop=self.folder/'desktop.json'
        # Original desktop values are all distinct so restoration is provable.
        self.desktop.write_text(json.dumps({'zoom':'1.750000','calls':[],
            'gtk_theme':"'DesktopGTK'",'gtk_size':'26',
            'agent_theme':'cu-agent-test','agent_size':32,
            'restore_theme':'desktop-hypr','restore_size':24}))
        binary=self.folder/'bin';binary.mkdir()
        for name,code in [('hyprctl',FAKE),('gsettings',FAKE_GSETTINGS),('pgrep','#!/bin/sh\nexit 0\n'),
                          ('computer-use-indicator',FAKE_INDICATOR),
                          ('grim',"#!/usr/bin/env python3\nimport sys\nsys.stdout.buffer.write(b'P6\\n2 2\\n255\\n'+bytes(12))\n"),
                          ('node','#!/bin/sh\nprintf \'{"ok":false,"error":"refusal"}\\n\'\n')]:
            p=binary/name;p.write_text(code);p.chmod(0o700)
        # A second PATH entry so lifecycle tests can use the instrumented helper
        # without changing the default fake used by the rest of the suite.
        self.altbin=self.folder/'altbin';self.altbin.mkdir()
        p=self.altbin/'computer-use-indicator'
        p.write_text(TRACKED_INDICATOR);p.chmod(0o700)
        self.env=os.environ.copy();self.env.pop('CU_SESSION_TOKEN',None)
        # Minimal valid agent theme on the Xcursor search path: real files for
        # left_ptr/pointer, an alias for text, all loadable at the agent size.
        icons=self.folder/'icons';cursors=icons/'cu-agent-test'/'cursors';cursors.mkdir(parents=True)
        write_xcursor(cursors/'left_ptr',32)
        write_xcursor(cursors/'pointer',32)
        (cursors/'text').symlink_to('left_ptr')
        self.env.update(PATH=str(binary)+os.pathsep+self.env['PATH'],
                        XDG_CACHE_HOME=str(self.folder/'cache'),FAKE_DESKTOP=str(self.desktop),
                        XCURSOR_PATH=str(icons))
        self.state=self.folder/'cache'/'agent-computer-use'
        self.processes=[]
        # Lifecycle subprocesses run a private copy of the project with an
        # explicit cursor profile, so every session exercises the required
        # agent-cursor path instead of a normal-cursor fallback.
        self.runtime=self.folder/'runtime'
        shutil.copytree(ROOT/'scripts',self.runtime/'scripts',
                        ignore=shutil.ignore_patterns('__pycache__'))
        (self.runtime/'native').mkdir()
        (self.runtime/'native/agent-cursor.json').write_text(json.dumps(
            {'theme':'cu-agent-test','size':32,'restore_theme':'desktop-hypr','restore_size':24}))
        # In-process guards read cursor_theme.PROFILE directly; point them at the
        # same explicit profile so behavior matches the subprocess runtime.
        patcher=patch.object(cursor_theme,'PROFILE',self.runtime/'native/agent-cursor.json')
        patcher.start();self.addCleanup(patcher.stop)

    def tearDown(self):
        for p in self.processes:
            if p.poll() is None:p.terminate()
            try:p.communicate(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.communicate()
        self.tmp.cleanup()

    def script(self,name):
        """A script inside the isolated runtime, never the checkout itself."""
        return str(self.runtime/'scripts'/name)

    def configure(self,**values):
        data=json.loads(self.desktop.read_text());data.update(values)
        self.desktop.write_text(json.dumps(data))

    def launch(self,code):
        p=subprocess.Popen([sys.executable,self.script('cu.py'),'session','--',
                            sys.executable,'-c',code],env=self.env,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.processes.append(p);return p

    def tracked(self,**values):
        self.env.update({k:str(v) for k,v in values.items()})
        self.env['PATH']=str(self.altbin)+os.pathsep+self.env['PATH']

    def wait_for(self,predicate):
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            try:
                if predicate():return
            except (OSError,ValueError):pass
            time.sleep(.01)
        self.fail('condition did not settle within test deadline')

    def idle(self):
        marker=self.folder/'driver-ready'
        p=self.launch('from pathlib import Path; import time; Path('+repr(str(marker))+').touch(); time.sleep(30)')
        self.wait_for(marker.exists)
        self.assertTrue((self.state/'session.json').exists())
        return p

    def assert_restored(self):
        self.wait_for(lambda:json.loads(self.desktop.read_text())['zoom']=='1.750000' and not (self.state/'session.json').exists())
        state=json.loads(self.desktop.read_text())
        calls=state['calls']
        self.assertFalse(any(a[0] in ('keyword','getoption') or 'hl.config' in str(a) for a in calls))
        self.assertTrue(any(':unbind()' in str(a) for a in calls))
        self.assertFalse(state.get('hotkey_active'))
        # The agent cursor was applied, then both tracks were restored: GTK
        # values match the distinct originals and the compositor got the
        # declared restore theme/size. GTK alone never proves compositor state.
        self.assertIn(['setcursor','cu-agent-test','32'],calls)
        self.assertEqual([a for a in calls if a and a[0]=='setcursor'][-1],
                         ['setcursor','desktop-hypr','24'])
        self.assertEqual((state['gtk_theme'],state['gtk_size']),("'DesktopGTK'",'26'))

    def test_success_and_driver_error_restore_desktop(self):
        for status in (0,7):
            with self.subTest(status=status):
                p=self.launch('import sys;sys.exit('+str(status)+')')
                out,err=p.communicate(timeout=8)
                self.assertEqual(p.returncode,status,(out,err));self.assert_restored()

    def test_session_between_commands_and_finish_cleans_up(self):
        marker=self.folder/'driver-ready'
        args=repr([sys.executable,self.script('cu.py'),'status'])
        code='import subprocess,time;from pathlib import Path;subprocess.run('+args+',check=True);subprocess.run('+args+',check=True);Path('+repr(str(marker))+').touch();time.sleep(30)'
        p=self.launch(code);self.wait_for(marker.exists)
        time.sleep(.1)
        self.assertTrue((self.state/'session.json').exists())
        subprocess.run([sys.executable,self.script('cu.py'),'finish'],env=self.env,
                       capture_output=True,check=True,timeout=4)
        p.communicate(timeout=8);self.assert_restored()

    def test_escape_cancel_cleans_up(self):
        p=self.idle()
        subprocess.run([sys.executable,self.script('cancel_hotkey.py'),'cancel'],env=self.env,
                       capture_output=True,check=True,timeout=4)
        p.communicate(timeout=8);self.assert_restored()
        self.assertTrue((self.state/'cancelled').exists())

    def test_refusal_and_exception_end_session(self):
        for args in (['browser','observe'],['observe','--screen','missing']):
            with self.subTest(args=args):
                # Let the wrapper stay alive if a buggy command forgets to end it.
                code='import subprocess,time;subprocess.run('+repr([sys.executable,self.script('cu.py'),*args])+');time.sleep(30)'
                p=self.launch(code);p.communicate(timeout=8)
                self.assertNotEqual(p.returncode,0);self.assert_restored()

    def test_wrapper_signals_and_abrupt_death(self):
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP,signal.SIGKILL):
            with self.subTest(signal=sig):
                p=self.idle();p.send_signal(sig);p.communicate(timeout=8);self.assert_restored()
                (self.folder/'driver-ready').unlink()

    def test_guardian_death_has_wrapper_fallback(self):
        p=self.idle()
        children=Path('/proc',str(p.pid),'task',str(p.pid),'children').read_text().split()
        for child in children:
            if b'cursor_session.py' in Path('/proc',child,'cmdline').read_bytes():
                os.kill(int(child),signal.SIGKILL)
                break
        else:self.fail('guardian child not found')
        p.communicate(timeout=8);self.assert_restored()

    def _kill_group(self,pid):
        try:os.killpg(os.getpgid(pid),signal.SIGKILL)
        except (ProcessLookupError,PermissionError):pass

    def test_guardian_death_reaps_whole_driver_group(self):
        # stop_group() escalates to SIGKILL for the whole driver group. When the
        # guardian is killed instead, the wrapper's terminate_driver must not leave
        # a SIGTERM-ignoring grandchild alive after restore.
        heart=self.folder/'heartbeat';pidf=self.folder/'grandchild.pid';ready=self.folder/'driver-ready'
        grand=("import os,signal,sys,time\nfrom pathlib import Path\n"
               "signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
               "Path(sys.argv[2]).write_text(str(os.getpid()))\n"
               "heart=Path(sys.argv[1])\n"
               "while True:\n"
               "    heart.write_text(str(time.time()));time.sleep(.1)\n")
        code=(f"import subprocess,sys,time\nfrom pathlib import Path\n"
              f"subprocess.Popen([sys.executable,'-c',{grand!r},{str(heart)!r},{str(pidf)!r}])\n"
              f"Path({str(ready)!r}).touch()\n"
              f"time.sleep(60)\n")
        p=self.launch(code)
        try:
            self.wait_for(lambda:ready.exists() and heart.exists())
            children=Path('/proc',str(p.pid),'task',str(p.pid),'children').read_text().split()
            for child in children:
                if b'cursor_session.py' in Path('/proc',child,'cmdline').read_bytes() and b'guard' in Path('/proc',child,'cmdline').read_bytes():
                    os.kill(int(child),signal.SIGKILL);break
            else:self.fail('guardian child not found')
            p.wait(timeout=8);self.assert_restored()
            frozen=heart.read_text();time.sleep(.3)
            self.assertEqual(heart.read_text(),frozen,'SIGTERM-ignoring grandchild survived guardian death')
            p.communicate(timeout=2)
        finally:
            if pidf.exists():self._kill_group(int(pidf.read_text()))

    def test_hotkey_failure_warns_but_driver_runs(self):
        self.configure(hotkey_failure=True)
        p=self.launch('print("driver ran")');out,err=p.communicate(timeout=8)
        self.assertEqual(p.returncode,0,(out,err))
        self.assertIn('driver ran',out);self.assertIn('warning:',err)
        self.assert_restored()

    def test_mixed_case_physical_keyboard(self):
        import cancel_hotkey
        import shlex
        name='Keychron café 🐈\x01 "\\ Keyboard'
        devices=subprocess.CompletedProcess([],0,json.dumps({'keyboards':[{'name':name},
                                                                           {'name':'Virtual Keyboard'}]}),'')
        state=self.folder/'cache café\n\x02'
        executable='/tmp/py café\n"\\'
        script='/tmp/cancel 🐈\x03.py'
        with patch.object(cancel_hotkey.subprocess,'run',return_value=devices), \
                patch.object(cancel_hotkey,'hypr_eval') as evaluate, \
                patch.object(cancel_hotkey,'STATE',state), \
                patch.object(cancel_hotkey,'__file__',script), \
                patch.object(cancel_hotkey.sys,'executable',executable):
            cancel_hotkey.hotkey_on()
        code=evaluate.call_args.args[0]
        self.assertIn(cancel_hotkey.lua_string(name),code)
        self.assertNotIn('Virtual Keyboard',code)
        command=shlex.join(['env','XDG_CACHE_HOME='+str(state.parent),executable,
                            str(Path(script).resolve()),'cancel'])
        self.assertIn(cancel_hotkey.lua_string(command),code)
        self.assertNotIn('\\u',code)

    @unittest.skipUnless(shutil.which('lua'), 'Lua interpreter is unavailable')
    def test_lua_string_literals_roundtrip_utf8_controls_and_digits(self):
        import cancel_hotkey
        value='prefix'+''.join(chr(i) for i in range(32))+'\x7f café 😀 "\\ 0123456789'
        program=('io.write('+cancel_hotkey.lua_string(value)+')\n').encode('ascii')
        result=subprocess.run([shutil.which('lua'), '-'],input=program,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        self.assertEqual(result.stdout,value.encode('utf-8'))

    def test_cleanup_exceptions_cannot_skip_restore(self):
        import cancel_hotkey
        import indicator
        for failing in ('request_stop','stop_group','drain_input'):
            with self.subTest(failing=failing),patch.object(session.signal,'signal'),patch.object(session,'STATE',self.folder),patch.object(session,'SNAPSHOT',self.folder/'snapshot'),patch.object(session,'CANCEL',self.folder/'cancel'),patch.object(session,'owner_lock'),patch.object(cancel_hotkey,'hotkey_on'),patch.object(cancel_hotkey,'hotkey_off'),patch.object(session,'request_stop'),patch.object(session,'stop_group'),patch.object(session,'drain_input'),patch.object(session,'restore',return_value=True) as restore,patch.object(session.select,'select',return_value=([1],[],[])),patch.object(session.os,'read',side_effect=[b'123',b'']),patch.object(session,failing,side_effect=RuntimeError('cleanup injected')),patch.object(cursor_theme,'snapshot',return_value={'agent_theme':'cu-agent-test','agent_size':32}),patch.object(cursor_theme,'apply'):
                with patch.object(indicator,'Native') as native,patch.object(indicator,'listen'):
                    native.return_value.process.poll.return_value=None
                    self.assertEqual(session.guardian(self.env,1,'a'*32),1)
                    restore.assert_called_once_with(self.env)
                    (self.folder/'snapshot').unlink(missing_ok=True)
                (self.folder/'snapshot').unlink(missing_ok=True)

    def test_startup_does_not_query_cursor_position_or_capture(self):
        self.configure(bad_read=True,no_monitors=True)
        p=self.launch('print("driver ran")');out,err=p.communicate(timeout=8)
        self.assertEqual(p.returncode,0,(out,err));self.assertIn('driver ran',out)
        self.assert_restored()
        self.assertFalse(any(a==['-j','monitors'] for a in json.loads(self.desktop.read_text())['calls']))

    def test_retry_and_persistent_recovery_after_failed_cleanup(self):
        self.configure(unbind_failure=True)
        p=self.launch('pass');out,err=p.communicate(timeout=8)
        self.assertEqual(p.returncode,1,(out,err))
        self.assertIn('snapshot retained',err)
        self.assertTrue((self.state/'session.json').exists())
        self.configure(unbind_failure=False)
        result=subprocess.run([sys.executable,self.script('cu.py'),'recover'],env=self.env,
                              capture_output=True,text=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr);self.assert_restored()

    def test_old_snapshot_is_retained_and_driver_does_not_run(self):
        self.state.mkdir(parents=True)
        snapshot=self.state/'session.json'
        saved=json.dumps({'original':'1.750000','token':'a'*32})
        snapshot.write_text(saved)
        p=self.launch('raise AssertionError("must not start")');out,err=p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0);self.assertNotIn('must not start',err)
        self.assertEqual(snapshot.read_text(),saved)
        self.assertEqual(json.loads(self.desktop.read_text())['calls'],[])

    def test_concurrent_session_cannot_overwrite_original(self):
        first=self.idle()
        before=(self.state/'session.json').read_text()
        second=self.launch('raise AssertionError("must not start")');second.communicate(timeout=8)
        self.assertNotEqual(second.returncode,0)
        self.assertEqual((self.state/'session.json').read_text(),before)
        first.terminate();first.communicate(timeout=8);self.assert_restored()

    def test_old_command_cannot_stop_new_session(self):
        self.state.mkdir(parents=True)
        snapshot=self.state/'session.json'
        snapshot.write_text(json.dumps({'version':2,'token':'b'*32}))
        with patch.object(session,'STATE',self.state),patch.object(session,'SNAPSHOT',snapshot):
            session.request_stop('a'*32)
        self.assertFalse((self.state/('stop-'+'b'*32)).exists())

    def test_gate_eof_never_starts_driver(self):
        read_fd,write_fd=os.pipe()
        marker=self.folder/'must-not-run'
        p=subprocess.Popen([sys.executable,self.script('cursor_session.py'),'driver',str(read_fd),
                            sys.executable,'-c','from pathlib import Path;Path('+repr(str(marker))+').touch()'],
                           env=self.env,pass_fds=(read_fd,),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.processes.append(p)
        os.close(read_fd);os.close(write_fd)
        p.communicate(timeout=4)
        self.assertEqual(p.returncode,1);self.assertFalse(marker.exists())

    def test_input_requires_explicit_session(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,'input requires'):
                cu.require_session()

    def test_cleanup_timeout_preserves_snapshot_and_does_not_raise(self):
        import cancel_hotkey
        self.state.mkdir(parents=True)
        snapshot=self.state/'session.json'
        snapshot.write_text(json.dumps({'version':2,'token':'a'*32}))
        with patch.object(session,'STATE',self.state),patch.object(session,'SNAPSHOT',snapshot),\
             patch.object(cancel_hotkey,'hotkey_off',side_effect=subprocess.TimeoutExpired('fake',2)) as off,\
             patch.object(session.time,'sleep'):
            self.assertFalse(session.restore(self.env));self.assertEqual(off.call_count,3)
        self.assertTrue(snapshot.exists())

    def test_indicator_loss_kills_driver_and_cleans_up(self):
        heart=self.folder/'heartbeat';ready=self.folder/'driver-ready'
        self.tracked(INDICATOR_STOP=str(self.folder/'stop-indicator'))
        code=(f"import time\nfrom pathlib import Path\n"
              f"heart=Path({str(heart)!r})\n"
              f"Path({str(ready)!r}).touch()\n"
              f"while True:\n    heart.write_text(str(time.time()));time.sleep(.1)\n")
        p=self.launch(code)
        self.wait_for(ready.exists)
        time.sleep(.3)  # let the driver heartbeat while the helper is alive
        self.assertTrue(heart.exists())
        (self.folder/'stop-indicator').write_text('x')  # helper exits -> loss
        p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0)
        frozen=heart.read_text();time.sleep(.3)
        self.assertEqual(heart.read_text(),frozen,'driver survived indicator loss')
        self.assert_restored()

    def test_indicator_startup_failure_never_runs_driver(self):
        marker=self.folder/'must-not-run'
        self.tracked(INDICATOR_FAIL='1')
        p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
        out,err=p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(marker.exists(),'driver ran despite indicator startup failure')
        self.assert_restored()
        self.assertEqual(list(self.state.glob('indicator-*.sock')),[],'indicator socket leaked')

    def test_missing_profile_never_starts_driver(self):
        marker=self.folder/'must-not-run'
        (self.runtime/'native/agent-cursor.json').unlink()
        p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
        out,err=p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(marker.exists(),'driver ran without a cursor profile')
        self.assertFalse(any(a and a[0]=='setcursor' for a in json.loads(self.desktop.read_text())['calls']))

    def test_missing_or_corrupt_cursor_assets_never_start_driver(self):
        cursors=self.folder/'icons/cu-agent-test/cursors'
        for role,content in (('text',None),('left_ptr',b'not an Xcursor image')):
            with self.subTest(role=role):
                path=cursors/role
                original=path.read_bytes()
                link=path.readlink() if path.is_symlink() else None
                path.unlink()
                if content is not None:path.write_bytes(content)
                try:
                    marker=self.folder/'must-not-run'
                    p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
                    out,err=p.communicate(timeout=8)
                    self.assertNotEqual(p.returncode,0,(out,err))
                    self.assertFalse(marker.exists(),'driver ran without loadable cursor assets')
                    self.assertFalse((self.state/'session.json').exists())
                    desktop=json.loads(self.desktop.read_text())
                    self.assertFalse(any(a and a[0]=='setcursor' for a in desktop['calls']))
                    self.assertEqual((desktop['gtk_theme'],desktop['gtk_size']),("'DesktopGTK'",'26'))
                finally:
                    path.unlink(missing_ok=True)
                    if link is not None:path.symlink_to(link)
                    else:path.write_bytes(original)

    def test_cursor_apply_failure_never_starts_driver(self):
        marker=self.folder/'must-not-run'
        self.configure(apply_failure=True)
        p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
        out,err=p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(marker.exists(),'driver ran despite cursor apply failure')
        self.assert_restored()

    def test_guardian_crash_helper_exits_on_eof(self):
        active=self.folder/'indicator-active'
        self.tracked(INDICATOR_ACTIVE=str(active))
        p=self.idle()
        self.wait_for(active.exists)
        children=Path('/proc',str(p.pid),'task',str(p.pid),'children').read_text().split()
        for child in children:
            if b'cursor_session.py' in Path('/proc',child,'cmdline').read_bytes():
                os.kill(int(child),signal.SIGKILL);break
        else:self.fail('guardian child not found')
        p.communicate(timeout=8)
        self.wait_for(lambda:not active.exists())
        self.assert_restored()


if __name__=='__main__':unittest.main()

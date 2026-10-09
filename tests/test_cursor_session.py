"""No live GUI: fake hyprctl plus real pipes/processes/signals for lifecycle proof."""
import json
import os
from pathlib import Path
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
else:sys.exit(1)
p.write_text(json.dumps(s))
'''

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
        self.desktop.write_text(json.dumps({'zoom':'1.750000','calls':[]}))
        binary=self.folder/'bin';binary.mkdir()
        for name,code in [('hyprctl',FAKE),('pgrep','#!/bin/sh\nexit 0\n'),
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
        self.env.update(PATH=str(binary)+os.pathsep+self.env['PATH'],
                        XDG_CACHE_HOME=str(self.folder/'cache'),FAKE_DESKTOP=str(self.desktop))
        self.state=self.folder/'cache'/'agent-computer-use'
        self.processes=[]

    def tearDown(self):
        for p in self.processes:
            if p.poll() is None:p.terminate()
            try:p.communicate(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.communicate()
        self.tmp.cleanup()

    def configure(self,**values):
        data=json.loads(self.desktop.read_text());data.update(values)
        self.desktop.write_text(json.dumps(data))

    def launch(self,code):
        p=subprocess.Popen([sys.executable,str(ROOT/'scripts/cu.py'),'session','--',
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
        calls=json.loads(self.desktop.read_text())['calls']
        self.assertFalse(any(a[0] in ('keyword','setcursor','getoption') or 'hl.config' in str(a) for a in calls))
        self.assertTrue(any(':unbind()' in str(a) for a in calls))
        self.assertFalse(json.loads(self.desktop.read_text()).get('hotkey_active'))

    def test_success_and_driver_error_leave_desktop_unchanged(self):
        for status in (0,7):
            with self.subTest(status=status):
                p=self.launch('import sys;sys.exit('+str(status)+')')
                out,err=p.communicate(timeout=8)
                self.assertEqual(p.returncode,status,(out,err));self.assert_restored()

    def test_session_between_commands_and_finish_cleans_up(self):
        marker=self.folder/'driver-ready'
        args=repr([sys.executable,str(ROOT/'scripts/cu.py'),'status'])
        code='import subprocess,time;from pathlib import Path;subprocess.run('+args+',check=True);subprocess.run('+args+',check=True);Path('+repr(str(marker))+').touch();time.sleep(30)'
        p=self.launch(code);self.wait_for(marker.exists)
        time.sleep(.1)
        self.assertTrue((self.state/'session.json').exists())
        subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'finish'],env=self.env,
                       capture_output=True,check=True,timeout=4)
        p.communicate(timeout=8);self.assert_restored()

    def test_escape_cancel_cleans_up(self):
        p=self.idle()
        subprocess.run([sys.executable,str(ROOT/'scripts/cancel_hotkey.py'),'cancel'],env=self.env,
                       capture_output=True,check=True,timeout=4)
        p.communicate(timeout=8);self.assert_restored()
        self.assertTrue((self.state/'cancelled').exists())

    def test_refusal_and_exception_end_session(self):
        for args in (['browser','observe'],['observe','--screen','missing']):
            with self.subTest(args=args):
                # Let the wrapper stay alive if a buggy command forgets to end it.
                code='import subprocess,time;subprocess.run('+repr([sys.executable,str(ROOT/'scripts/cu.py'),*args])+');time.sleep(30)'
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
        devices=subprocess.CompletedProcess([],0,'{"keyboards":[{"name":"Keychron K8 Keyboard"},{"name":"Virtual Keyboard"}]}','')
        with patch.object(cancel_hotkey.subprocess,'run',return_value=devices),patch.object(cancel_hotkey,'hypr_eval') as evaluate:
            cancel_hotkey.hotkey_on()
        code=evaluate.call_args.args[0]
        self.assertIn('Keychron K8 Keyboard',code);self.assertNotIn('Virtual Keyboard',code)

    def test_cleanup_exceptions_cannot_skip_restore(self):
        import cancel_hotkey
        import indicator
        for failing in ('request_stop','stop_group','drain_input'):
            with self.subTest(failing=failing),patch.object(session.signal,'signal'),patch.object(session,'STATE',self.folder),patch.object(session,'SNAPSHOT',self.folder/'snapshot'),patch.object(session,'CANCEL',self.folder/'cancel'),patch.object(session,'owner_lock'),patch.object(cancel_hotkey,'hotkey_on'),patch.object(cancel_hotkey,'hotkey_off'),patch.object(session,'request_stop'),patch.object(session,'stop_group'),patch.object(session,'drain_input'),patch.object(session,'restore',return_value=True) as restore,patch.object(session.select,'select',return_value=([1],[],[])),patch.object(session.os,'read',side_effect=[b'123',b'']),patch.object(session,failing,side_effect=RuntimeError('cleanup injected')):
                with patch.object(indicator,'Native') as native,patch.object(indicator,'listen'):
                    native.return_value.process.poll.return_value=None
                    self.assertEqual(session.guardian(self.env,1,'a'*32),1)
                    restore.assert_called_once_with(self.env)
                    (self.folder/'snapshot').unlink(missing_ok=True)
                (self.folder/'snapshot').unlink(missing_ok=True)

    def test_startup_never_reads_cursor_or_captures(self):
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
        result=subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'recover'],env=self.env,
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
        p=subprocess.Popen([sys.executable,str(ROOT/'scripts/cursor_session.py'),'driver',str(read_fd),
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

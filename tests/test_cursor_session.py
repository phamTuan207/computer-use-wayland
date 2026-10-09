"""No live GUI: fake hyprctl plus real pipes/processes/signals for lifecycle proof."""
import importlib.util
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
import json,os,re,sys
from pathlib import Path
p=Path(os.environ['FAKE_DESKTOP'])
s=json.loads(p.read_text())
a=sys.argv[1:]
s['calls'].append(a)
if a==['getoption','cursor:zoom_factor']:
    if s.get('bad_read'):print('unknown option')
    else:print('float: '+s['zoom'])
elif a==['-j','devices']:print('{"keyboards":[{"name":"test-keyboard"}]}')
elif a==['-j','monitors']:print('[]')
elif a and a[0]=='eval':
    m=re.search(r'zoom_factor = ([0-9.]+)',a[1])
    if m:
        s['zoom']=m[1]
        if m[1]=='5.0' and s.get('partial_failure'):
            p.write_text(json.dumps(s));sys.exit(1)
        if m[1]!='5.0' and s.get('restore_failures',0):
            s['zoom']='5.0';s['restore_failures']-=1
            p.write_text(json.dumps(s));sys.exit(1)
    elif 'hl.bind' in a[1] and s.get('hotkey_failure'):
        p.write_text(json.dumps(s));sys.exit(1)
    elif ':unbind()' in a[1] and 'hl.bind' not in a[1] and s.get('unbind_failure'):
        p.write_text(json.dumps(s));sys.exit(1)
    print('ok')
else:sys.exit(1)
p.write_text(json.dumps(s))
'''


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)
        self.desktop=self.folder/'desktop.json'
        self.desktop.write_text(json.dumps({'zoom':'1.750000','calls':[]}))
        binary=self.folder/'bin';binary.mkdir()
        for name,code in [('hyprctl',FAKE),('pgrep','#!/bin/sh\nexit 0\n'),
                          ('node','#!/bin/sh\nprintf \'{"ok":false,"error":"refusal"}\\n\'\n')]:
            p=binary/name;p.write_text(code);p.chmod(0o700)
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
        self.assertEqual(json.loads(self.desktop.read_text())['zoom'],'5.0')
        return p

    def assert_restored(self):
        self.wait_for(lambda:json.loads(self.desktop.read_text())['zoom']=='1.750000' and not (self.state/'session.json').exists())
        calls=json.loads(self.desktop.read_text())['calls']
        zooms=[a[1] for a in calls if a[0]=='eval' and 'zoom_factor' in a[1]]
        self.assertEqual(zooms[-1],'hl.config({ cursor = { zoom_factor = 1.750000 } })')
        self.assertFalse(any(a[0] in ('keyword','setcursor') for a in calls))

    def test_success_and_driver_error_restore_nondefault(self):
        for status in (0,7):
            with self.subTest(status=status):
                p=self.launch('import sys;sys.exit('+str(status)+')')
                out,err=p.communicate(timeout=8)
                self.assertEqual(p.returncode,status,(out,err));self.assert_restored()

    def test_keeps_zoom_between_commands_and_finish_restores(self):
        marker=self.folder/'driver-ready'
        args=repr([sys.executable,str(ROOT/'scripts/cu.py'),'status'])
        code='import subprocess,time;from pathlib import Path;subprocess.run('+args+',check=True);subprocess.run('+args+',check=True);Path('+repr(str(marker))+').touch();time.sleep(30)'
        p=self.launch(code);self.wait_for(marker.exists)
        time.sleep(.1)
        self.assertEqual(json.loads(self.desktop.read_text())['zoom'],'5.0')
        subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'finish'],env=self.env,
                       capture_output=True,check=True,timeout=4)
        p.communicate(timeout=8);self.assert_restored()

    def test_escape_cancel_restores_even_when_unbind_fails(self):
        self.configure(unbind_failure=True)
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

    def test_startup_failures_restore_if_write_may_have_applied(self):
        for flag in ('partial_failure','hotkey_failure'):
            with self.subTest(flag=flag):
                self.configure(**{flag:True})
                p=self.launch('raise AssertionError("must not start")')
                out,err=p.communicate(timeout=8)
                self.assertNotEqual(p.returncode,0);self.assertNotIn('must not start',err)
                self.assert_restored();self.configure(**{flag:False})

    def test_unknown_value_never_changes_cursor(self):
        self.configure(bad_read=True)
        p=self.launch('raise AssertionError("must not start")');p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.state/'session.json').exists())
        self.assertFalse(any('zoom_factor' in str(a) and a[0]=='eval' for a in json.loads(self.desktop.read_text())['calls']))

    def test_retry_and_persistent_recovery_after_failed_restore(self):
        self.configure(restore_failures=1)
        p=self.launch('pass');p.communicate(timeout=8);self.assert_restored()
        self.configure(restore_failures=3)
        p=self.launch('pass');out,err=p.communicate(timeout=8)
        self.assertEqual(p.returncode,1,(out,err))
        self.assertIn('snapshot retained',err)
        self.assertTrue((self.state/'session.json').exists())
        result=subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'recover'],env=self.env,
                              capture_output=True,text=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr);self.assert_restored()

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
        snapshot.write_text(json.dumps({'original':'1.750000','token':'b'*32}))
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

    def test_restore_timeout_preserves_snapshot_and_does_not_raise(self):
        self.state.mkdir(parents=True)
        snapshot=self.state/'session.json'
        snapshot.write_text(json.dumps({'original':'1.750000','token':'a'*32}))
        with patch.object(session,'STATE',self.state),patch.object(session,'SNAPSHOT',snapshot),\
             patch.object(session,'zoom',side_effect=subprocess.TimeoutExpired('fake',2)) as zoom,\
             patch.object(session.time,'sleep'):
            self.assertFalse(session.restore(self.env));self.assertEqual(zoom.call_count,3)
        self.assertTrue(snapshot.exists())


if __name__=='__main__':unittest.main()

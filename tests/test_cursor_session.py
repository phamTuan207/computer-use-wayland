"""No live GUI: fake hyprctl plus real pipes/processes/signals for lifecycle proof."""
import fcntl
import json
import os
import re
import socket
import threading
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
    # Legacy path only: old snapshots without a guard token restore this way.
    # New sessions never touch the global theme; they hold a socket lease.
    print('ok')
elif a[:2]==['cu-cursor','status']:
    import fcntl
    if s.get('status_down'):p.write_text(json.dumps(s));sys.exit(1)
    if s.get('status_busy'):
        print(json.dumps({'ok':True,'schema':1,'active':True,'token':'f'*32}))
    else:
        try:
            with open(os.environ['FAKE_GUARD']) as guard_file:
                fcntl.flock(guard_file,fcntl.LOCK_SH)
                guard_state=json.load(guard_file)
        except OSError:guard_state={'token':'','active':False}
        print(json.dumps({'ok':True,'schema':1,'active':bool(guard_state.get('active')),'token':guard_state.get('token','')}))
elif a[:2]==['cu-cursor','release']:
    import fcntl
    token=a[2] if len(a)>2 else ''
    if s.get('release_failure'):print(json.dumps({'ok':False,'schema':1}))
    else:
        with open(os.environ['FAKE_GUARD'],'r+') as guard_file:
            fcntl.flock(guard_file,fcntl.LOCK_EX)
            guard_state=json.load(guard_file)
            if guard_state.get('active') and token!=guard_state.get('token'):
                print('cursor guard belongs to another session')
            else:
                guard_state.setdefault('released',[]).append(token)
                guard_state['token']='';guard_state['active']=False
                guard_file.seek(0);json.dump(guard_state,guard_file);guard_file.truncate()
                print(json.dumps({'ok':True,'schema':1,'released':token}))
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

FAKE_GRIM = '''#!/usr/bin/env python3
import fcntl,json,os,sys
try:
    with open(os.environ['FAKE_GUARD']) as stream:
        fcntl.flock(stream,fcntl.LOCK_SH)
        visibility=json.load(stream).get('visibility','unknown')
except OSError:visibility='unknown'
log=os.environ.get('VISIBLE_LOG')
if log:open(log,'a').write(visibility+'\\n')
sys.stdout.buffer.write(b'P6\\n2 2\\n255\\n'+bytes(12))
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


def _guard_read(state_path):
    with open(state_path) as stream:
        fcntl.flock(stream,fcntl.LOCK_SH)
        return json.load(stream)


def _guard_write(state_path, **values):
    with open(state_path,'r+') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        state=json.load(stream);state.update(values)
        stream.seek(0);json.dump(state,stream);stream.truncate()


class GuardServer:
    """Fake native cursor backend: a real AF_UNIX socket under a temp runtime.

    Never the host runtime. Mirrors the plugin contract: one JSON handshake
    (schema/theme/size/token), an acknowledgement, then the lease is held until
    EOF. `mode` selects the acknowledgement: 'ok', 'wrong-token', 'drop',
    'fail-hide' or 'fail-show'. Visibility is persisted in the guard state.
    """

    def __init__(self, folder, theme='cu-agent-test', size=32):
        self.state_path=folder/'guard.json'
        self.theme=theme;self.size=size;self.mode='ok';self._lease=''
        runtime=folder/'run'/'agent-computer-use'
        runtime.mkdir(parents=True,exist_ok=True);os.chmod(runtime,0o700)
        self.sock_path=runtime/'cursor-guard.sock'
        self._socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self._socket.bind(str(self.sock_path));self._socket.listen(4)
        self._socket.settimeout(0.2)
        self._peer=None
        self._stop=threading.Event()
        self._thread=threading.Thread(target=self._loop,daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self.drop()
        self._thread.join(timeout=5)
        try:self._socket.close()
        except OSError:pass
        try:self.sock_path.unlink()
        except OSError:pass

    def drop(self):
        """Sever the lease from the backend side, as a compositor unload would."""
        peer=self._peer
        if peer is not None:
            try:peer.shutdown(socket.SHUT_RDWR)
            except OSError:pass

    def acquired(self):
        try:state=_guard_read(self.state_path)
        except OSError:return False
        return bool(state.get('active'))

    def _loop(self):
        while not self._stop.is_set():
            try:conn,_=self._socket.accept()
            except socket.timeout:continue
            except OSError:return
            try:self._handle(conn)
            except OSError:pass

    def _valid(self, request):
        return (isinstance(request,dict) and type(request.get('schema')) is int and
                request.get('schema')==1 and type(request.get('size')) is int and
                16<=request['size']<=96 and isinstance(request.get('theme'),str) and
                bool(re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',request['theme'])) and
                isinstance(request.get('token'),str) and
                bool(re.fullmatch(r'[0-9a-f]{32}',request['token'])))

    def _handle(self, conn):
        with conn:
            conn.settimeout(5)
            data=bytearray()
            while b'\n' not in data and len(data)<=4097:
                try:part=conn.recv(4097-len(data))
                except socket.timeout:continue
                if not part:return
                data.extend(part)
            try:request=json.loads(data.decode())
            except ValueError:return
            if self.mode=='drop' or not self._valid(request):return
            if self.mode=='wrong-token':
                reply={'ok':True,'schema':1,'token':'0'*32}
            else:
                self._lease=request['token']
                reply={'ok':True,'schema':1,'token':self._lease}
                _guard_write(self.state_path,token=self._lease,active=True)
            try:conn.sendall((json.dumps(reply)+'\n').encode())
            except OSError:return
            self._peer=conn
            try:
                conn.settimeout(0.5)
                hold=bytearray()
                while not self._stop.is_set():
                    try:part=conn.recv(4096)
                    except socket.timeout:continue
                    if not part:break
                    hold.extend(part)
                    while b'\n' in hold:
                        line,hold=hold.split(b'\n',1)
                        if not self._command(conn,line):return
            finally:
                self._peer=None
                try:_guard_write(self.state_path,token='',active=False)
                except OSError:pass

    def _command(self, conn, line):
        """One visibility op; fail closed on anything unexpected."""
        try:request=json.loads(line.decode())
        except ValueError:return False
        operation=request.get('op')
        if operation not in ('hide','show') or request.get('token')!=self._lease:
            return False
        state='hidden' if operation=='hide' else 'visible'
        reply={'ok':True,'schema':1,'token':self._lease,'state':state}
        if self.mode=='fail-hide' and operation=='hide':
            reply=dict(reply,state='visible')
        elif self.mode=='fail-show' and operation=='show':
            reply=dict(reply,token='0'*32)
        if self.mode not in ('fail-hide','fail-show'):
            try:_guard_write(self.state_path,visibility=state)
            except OSError:return False
        try:conn.sendall((json.dumps(reply)+'\n').encode())
        except OSError:return False
        return True


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
                          ('grim',FAKE_GRIM),
                          ('node','#!/bin/sh\nprintf \'{"ok":false,"error":"refusal"}\\n\'\n')]:
            p=binary/name;p.write_text(code);p.chmod(0o700)
        # A second PATH entry so lifecycle tests can use the instrumented helper
        # without changing the default fake used by the rest of the suite.
        self.altbin=self.folder/'altbin';self.altbin.mkdir()
        p=self.altbin/'computer-use-indicator'
        p.write_text(TRACKED_INDICATOR);p.chmod(0o700)
        self.env=os.environ.copy();self.env.pop('CU_SESSION_TOKEN',None)
        # Never let read-only IPC reach the host compositor socket: without a
        # signature every query falls back to the fake hyprctl on PATH.
        self.env.pop('HYPRLAND_INSTANCE_SIGNATURE',None)
        # Minimal valid agent theme on the Xcursor search path: real files for
        # left_ptr/pointer, an alias for text, all loadable at the agent size.
        icons=self.folder/'icons';cursors=icons/'cu-agent-test'/'cursors';cursors.mkdir(parents=True)
        write_xcursor(cursors/'left_ptr',32)
        write_xcursor(cursors/'pointer',32)
        (cursors/'text').symlink_to('left_ptr')
        # Fake native lease backend under a temp runtime, never the host one.
        self.guard_file=self.folder/'guard.json'
        self.guard_file.write_text(json.dumps({'token':'','active':False,'released':[],'visibility':'visible'}))
        self.visible_log=self.folder/'visibility.log'
        self.env.update(PATH=str(binary)+os.pathsep+self.env['PATH'],
                        XDG_CACHE_HOME=str(self.folder/'cache'),FAKE_DESKTOP=str(self.desktop),
                        XCURSOR_PATH=str(icons),XDG_RUNTIME_DIR=str(self.folder/'run'),
                        FAKE_GUARD=str(self.guard_file),VISIBLE_LOG=str(self.visible_log))
        self.guard_server=GuardServer(self.folder)
        self.guard_server.start();self.addCleanup(self.guard_server.stop)
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

    def released(self):
        return _guard_read(self.guard_file).get('released',[])

    def assert_restored(self):
        self.wait_for(lambda:json.loads(self.desktop.read_text())['zoom']=='1.750000' and not (self.state/'session.json').exists())
        state=json.loads(self.desktop.read_text())
        calls=state['calls']
        self.assertFalse(any(a[0] in ('keyword','getoption') or 'hl.config' in str(a) for a in calls))
        self.assertTrue(any(':unbind()' in str(a) for a in calls))
        self.assertFalse(state.get('hotkey_active'))
        # New sessions hold a native image lease: no global theme writes at all
        # (GTK values untouched, no setcursor), and the lease is released.
        self.assertFalse(any(a and a[0]=='setcursor' for a in calls))
        self.assertEqual((state['gtk_theme'],state['gtk_size']),("'DesktopGTK'",'26'))
        tokens=[token for token in self.released()
                if isinstance(token,str) and re.fullmatch(r'[0-9a-f]{32}',token)]
        self.assertTrue(tokens,'cursor lease was never released')
        self.assertFalse(self.guard_server.acquired(),'cursor lease remains active')
        if self.guard_server._lease:
            self.assertIn(self.guard_server._lease,tokens,'latest lease was not released')

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
            with self.subTest(failing=failing),patch.object(session.signal,'signal'),patch.object(session,'STATE',self.folder),patch.object(session,'SNAPSHOT',self.folder/'snapshot'),patch.object(session,'CANCEL',self.folder/'cancel'),patch.object(session,'owner_lock'),patch.object(cancel_hotkey,'hotkey_on'),patch.object(cancel_hotkey,'hotkey_off'),patch.object(session,'request_stop'),patch.object(session,'stop_group'),patch.object(session,'drain_input'),patch.object(session,'restore',return_value=True) as restore,patch.object(session.select,'select',return_value=([1],[],[])),patch.object(session.os,'read',side_effect=[b'123',b'']),patch.object(session,failing,side_effect=RuntimeError('cleanup injected')),patch.object(cursor_theme,'snapshot',return_value={'agent_theme':'cu-agent-test','agent_size':32}),patch.object(cursor_theme,'check_guard'),patch.object(cursor_theme,'apply'):
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
        self.assertFalse((self.state/'session.json').exists())
        self.assertFalse(any(a and a[0]=='setcursor' for a in json.loads(self.desktop.read_text())['calls']))
        self.assertEqual(self.released(),[])

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
                    self.assertEqual(self.released(),[],'no lease existed to release')
                finally:
                    path.unlink(missing_ok=True)
                    if link is not None:path.symlink_to(link)
                    else:path.write_bytes(original)

    def test_handshake_failure_never_starts_driver(self):
        marker=self.folder/'must-not-run'
        self.guard_server.mode='wrong-token'
        p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
        out,err=p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(marker.exists(),'driver ran despite lease handshake failure')

    def test_capture_hides_badge_and_cursor_until_presented_frame(self):
        shot=self.folder/'shot-done'
        code=('import subprocess,sys;subprocess.run([sys.executable,'+repr(self.script('cu.py'))+
              ",'observe','--screen','test'],check=True);import pathlib;pathlib.Path("+repr(str(shot))+").touch()")
        p=self.launch(code);out,err=p.communicate(timeout=15)
        self.assertEqual(p.returncode,0,(out,err))
        self.assertTrue(shot.exists())
        # Fake grim recorded the native visibility at exposure time.
        self.assertIn('hidden',self.visible_log.read_text().splitlines())
        self.assert_restored()
        self.assertEqual(_guard_read(self.guard_file).get('visibility'),'visible')

    def test_cursor_hide_failure_prevents_screenshot_and_ends_driver(self):
        self.guard_server.mode='fail-hide'
        shot=self.folder/'shot-done'
        code=('import subprocess,sys;subprocess.run([sys.executable,'+repr(self.script('cu.py'))+
              ",'observe','--screen','test'],check=True);import pathlib;pathlib.Path("+repr(str(shot))+").touch()")
        p=self.launch(code);out,err=p.communicate(timeout=15)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(shot.exists(),'screenshot taken despite hide refusal')
        self.assertFalse(self.visible_log.exists(),'grim ran despite hide refusal')
        self.assert_restored()

    def test_wrong_show_ack_fails_closed_after_exposure(self):
        self.guard_server.mode='fail-show'
        shot=self.folder/'shot-done'
        code=('import subprocess,sys;subprocess.run([sys.executable,'+repr(self.script('cu.py'))+
              ",'observe','--screen','test'],check=True);import pathlib;pathlib.Path("+repr(str(shot))+").touch()")
        p=self.launch(code);out,err=p.communicate(timeout=15)
        self.assertNotEqual(p.returncode,0,(out,err))
        self.assertFalse(shot.exists(),'driver continued after failed show ack')
        self.assert_restored()

    def test_session_visuals_orders_cursor_before_native(self):
        import unittest.mock as mock
        calls=[]
        native=mock.Mock();native.command.side_effect=lambda command:(calls.append(('native',command)),'hidden' if command=='hide' else 'visible')
        cursor=mock.Mock();cursor.command.side_effect=lambda command:calls.append(('cursor',command))
        visuals=session.SessionVisuals(native,cursor)
        visuals.command('hide')
        visuals.command('show')
        visuals.command('move test 1 2')
        self.assertEqual(calls,[('cursor','hide'),('native','hide'),('cursor','show'),('native','show'),('native','move test 1 2')])

    def test_missing_or_busy_backend_never_starts_driver(self):
        for label,flags in (('missing',{'status_down':True}),('busy',{'status_busy':True})):
            with self.subTest(label=label):
                self.configure(**flags)
                marker=self.folder/'must-not-run'
                p=self.launch(f"from pathlib import Path;Path({str(marker)!r}).touch()")
                out,err=p.communicate(timeout=8)
                self.assertNotEqual(p.returncode,0,(out,err))
                self.assertFalse(marker.exists(),'driver ran without an idle backend')
                self.assertFalse((self.state/'session.json').exists())
                self.assertEqual(self.released(),[])
                self.configure(status_down=False,status_busy=False)

    def test_lost_lease_stops_driver_and_restores(self):
        heart=self.folder/'heartbeat';ready=self.folder/'driver-ready'
        code=(f"import time\nfrom pathlib import Path\n"
              f"heart=Path({str(heart)!r})\n"
              f"Path({str(ready)!r}).touch()\n"
              f"while True:\n    heart.write_text(str(time.time()));time.sleep(.1)\n")
        p=self.launch(code)
        self.wait_for(ready.exists)
        self.wait_for(self.guard_server.acquired)
        time.sleep(.3)
        self.assertTrue(heart.exists())
        self.guard_server.drop()  # backend goes away -> EOF on the lease
        p.communicate(timeout=8)
        self.assertNotEqual(p.returncode,0)
        frozen=heart.read_text();time.sleep(.3)
        self.assertEqual(heart.read_text(),frozen,'driver survived lease loss')
        self.assert_restored()

    def test_unproven_release_retains_snapshot_then_recover(self):
        self.configure(release_failure=True)
        p=self.launch('pass');out,err=p.communicate(timeout=8)
        self.assertEqual(p.returncode,1,(out,err))
        self.assertIn('snapshot retained',err)
        self.assertTrue((self.state/'session.json').exists())
        self.assertEqual(self.released(),[])
        self.configure(release_failure=False)
        result=subprocess.run([sys.executable,self.script('cu.py'),'recover'],env=self.env,
                              capture_output=True,text=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr);self.assert_restored()

    def test_legacy_snapshot_without_guard_token_restores_declared_values(self):
        import cancel_hotkey
        self.state.mkdir(parents=True)
        snapshot=self.state/'session.json'
        token='e'*32
        snapshot.write_text(json.dumps({'version':3,'token':token,'cursor':{
            'gtk_theme':'ChangedGTK','gtk_size':30,'hypr_theme':'other-hypr','hypr_size':22,
            'agent_theme':'cu-agent-test','agent_size':32}}))
        with patch.object(session,'STATE',self.state),patch.object(session,'SNAPSHOT',snapshot), \
             patch.object(cancel_hotkey,'hotkey_off'):
            self.assertTrue(session.restore(self.env))
        self.assertFalse(snapshot.exists())
        desktop=json.loads(self.desktop.read_text())
        # Legacy path restores the snapshot's own recorded values.
        self.assertEqual((desktop['gtk_theme'],desktop['gtk_size']),("'ChangedGTK'",'30'))
        self.assertIn(['setcursor','other-hypr','22'],desktop['calls'])
        self.assertEqual(self.released(),[],'legacy restore uses no lease')

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

#!/usr/bin/env python3
"""Session cursor owner; a separate guardian survives loss of the driver wrapper."""
import fcntl
import json
import math
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import time
import uuid

STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'agent-computer-use'
SNAPSHOT = STATE/'session.json'
CANCEL = STATE/'cancelled'


def prepare():
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE.chmod(0o700)


def command(env, *args):
    p=subprocess.run(['hyprctl', *args], env=env, capture_output=True, text=True, timeout=2)
    if p.returncode or (args[0]=='eval' and p.stdout.strip()!='ok'):
        raise RuntimeError('Hyprland rejected cursor/session change')
    return p.stdout


def zoom(env, value):
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value) or not math.isfinite(float(value)) or float(value)<=0:
        raise ValueError('invalid cursor zoom snapshot')
    command(env, 'eval', 'hl.config({ cursor = { zoom_factor = '+value+' } })')


def read_zoom(env):
    raw=command(env, 'getoption', 'cursor:zoom_factor')
    match=re.search(r'^\s*float:\s*([0-9]+(?:\.[0-9]+)?)\s*$', raw, re.M)
    if not match or not math.isfinite(float(match[1])) or float(match[1])<=0:
        raise RuntimeError('cannot read cursor:zoom_factor; cursor unchanged')
    return match[1]


def request_stop(expected=None):
    """Independent of hotkey teardown; safe even if no session exists."""
    try:
        saved=json.loads(SNAPSHOT.read_text())
        token=saved['token']
        if expected is not None and token!=expected:return
        if re.fullmatch(r'[0-9a-f]{32}', token):
            (STATE/('stop-'+token)).touch(mode=0o600)
    except (OSError, ValueError, TypeError, KeyError):
        pass


def restore(env):
    """No cleanup exception can replace the driver's outcome. Keep failed snapshots."""
    if not SNAPSHOT.exists():return True
    try:saved=json.loads(SNAPSHOT.read_text())
    except (OSError,ValueError):
        print('cursor snapshot unreadable; recovery requires inspection',file=sys.stderr)
        return False
    for attempt in range(3):
        try:
            zoom(env, saved['original'])
            if float(read_zoom(env))!=float(saved['original']):
                raise RuntimeError('cursor restore verification failed')
            SNAPSHOT.unlink()
            (STATE/('stop-'+saved['token'])).unlink(missing_ok=True)
            return True
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.TimeoutExpired):
            if attempt<2:time.sleep(.05)
    print('cursor restore failed; snapshot retained; run computer-use recover', file=sys.stderr)
    return False


def owner_lock():
    prepare()
    lock=open(STATE/'cursor.lock','a')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError('another cursor session is active')
    return lock


def drain_input():
    # Stop markers prevent the next command; finish in-flight input before restore.
    with open(STATE/'desktop.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)


def recover(env, expected=None):
    try:lock=owner_lock()
    except (OSError,RuntimeError):
        if expected is None:raise
        print('cursor recovery ownership changed; current owner must restore',file=sys.stderr)
        return 1
    with lock:
        if expected is not None:
            try:current=json.loads(SNAPSHOT.read_text()).get('token')
            except (OSError,ValueError):current=None
            if current!=expected:return 0
        request_stop()
        drain_input()
        restored=restore(env)
        try:
            import cancel_hotkey
            cancel_hotkey.hotkey_off()
        except (OSError,RuntimeError,subprocess.TimeoutExpired):
            print('temporary Escape binding cleanup failed',file=sys.stderr)
        return 0 if restored else 1


def guardian(env, pipe, token):
    import cancel_hotkey
    stopping=[False]
    def stop(signum, frame):stopping[0]=True
    for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):signal.signal(sig,stop)
    with owner_lock():
        if SNAPSHOT.exists() and not restore(env):
            raise RuntimeError('previous cursor snapshot could not be restored')
        if CANCEL.exists():raise RuntimeError('cancelled by user')
        original=read_zoom(env)
        driver_group=None
        try:
            # Persist before mutation, including partially successful/timeout writes.
            with open(SNAPSHOT,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as stream:
                json.dump({'original':original,'token':token},stream)
                stream.flush();os.fsync(stream.fileno())
            cancel_hotkey.hotkey_on()
            if stopping[0] or CANCEL.exists():raise RuntimeError('session cancelled during startup')
            zoom(env,'5.0')
            if float(read_zoom(env))!=5.0:raise RuntimeError('cursor zoom verification failed')
            print('ready',flush=True)
            while not stopping[0] and not CANCEL.exists() and not (STATE/('stop-'+token)).exists():
                ready,_,_=select.select([pipe],[],[],.05)
                if ready:
                    message=os.read(pipe,4096)
                    if not message:break
                    if message.strip().isdigit():
                        driver_group=int(message.strip())
                        print('registered',flush=True)
        finally:
            request_stop()
            if driver_group is not None:stop_group(driver_group)
            drain_input()
            restored=restore(env)
            try:cancel_hotkey.hotkey_off()
            except (OSError,RuntimeError,subprocess.TimeoutExpired):
                print('temporary Escape binding cleanup failed',file=sys.stderr)
        return 0 if restored else 1


def stop_group(group):
    try:os.killpg(group,signal.SIGTERM)
    except ProcessLookupError:return
    deadline=time.monotonic()+.6
    while time.monotonic()<deadline:
        try:os.killpg(group,0)
        except ProcessLookupError:return
        time.sleep(.02)
    try:os.killpg(group,signal.SIGKILL)
    except ProcessLookupError:pass


def terminate_driver(driver):
    if driver is None:return
    # Include ordinary child commands; reap our direct child in every case.
    try:os.killpg(driver.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:driver.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:os.killpg(driver.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        driver.wait()


def supervise(env, argv):
    if argv and argv[0]=='--':argv=argv[1:]
    if not argv:raise ValueError('session requires a driver command')
    if os.environ.get('CU_SESSION_TOKEN'):raise RuntimeError('nested cursor session refused')
    read_fd,write_fd=os.pipe()
    token=uuid.uuid4().hex
    guard=None;driver=None;gate_read=None;gate_write=None
    previous={}
    def interrupted(signum,frame):raise KeyboardInterrupt('automation session interrupted')
    try:
        for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):
            previous[sig]=signal.signal(sig,interrupted)
        guard=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'guard',str(read_fd),token],
                               env=env,pass_fds=(read_fd,),stdout=subprocess.PIPE,text=True,
                               start_new_session=True)
        os.close(read_fd);read_fd=None
        ready,_,_=select.select([guard.stdout],[],[],15)
        if not ready or guard.stdout.readline().strip()!='ready':
            raise RuntimeError('cursor guardian startup failed')
        driver_env=env.copy();driver_env['CU_SESSION_TOKEN']=token
        # Child cannot execute input before the guardian owns its process group.
        gate_read,gate_write=os.pipe()
        driver=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'driver',str(gate_read),*argv],
                                env=driver_env,pass_fds=(gate_read,),start_new_session=True)
        os.close(gate_read);gate_read=None
        os.write(write_fd,str(driver.pid).encode())
        ready,_,_=select.select([guard.stdout],[],[],2)
        if not ready or guard.stdout.readline().strip()!='registered':
            raise RuntimeError('driver registration failed')
        os.write(gate_write,b'go')
        os.close(gate_write);gate_write=None
        while driver.poll() is None:
            if guard.poll() is not None or CANCEL.exists() or (STATE/('stop-'+token)).exists():
                terminate_driver(driver)
                return 1
            time.sleep(.05)
        return driver.returncode if driver.returncode>=0 else 1
    finally:
        # Do not let another termination signal interrupt restoration/reaping.
        for sig in previous:signal.signal(sig,signal.SIG_IGN)
        if gate_write is not None:os.close(gate_write)
        if gate_read is not None:os.close(gate_read)
        terminate_driver(driver)
        os.close(write_fd)  # EOF also works when the wrapper is killed abruptly.
        if read_fd is not None:os.close(read_fd)
        if guard is not None:
            try:guard.wait(timeout=20)
            except subprocess.TimeoutExpired:
                guard.terminate()
                guard.wait()  # Never SIGKILL the cursor owner during restoration.
            guard.stdout.close()
            if guard.returncode<0 and SNAPSHOT.exists():
                # The guardian itself died: wrapper remains a second restoration owner.
                recover(env,token)
        for sig,handler in previous.items():signal.signal(sig,handler)


if __name__=='__main__':
    try:
        if sys.argv[1]=='driver':
            gate=int(sys.argv[2])
            allowed=os.read(gate,2)==b'go'
            os.close(gate)
            if allowed:os.execvpe(sys.argv[3],sys.argv[3:],os.environ.copy())
            exit_code=1
        else:exit_code=guardian(os.environ.copy(),int(sys.argv[2]),sys.argv[3])
    except BaseException as exc:
        print(str(exc),file=sys.stderr);exit_code=1
    sys.exit(exit_code)

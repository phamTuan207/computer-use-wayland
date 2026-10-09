#!/usr/bin/env python3
"""Session owner; a separate guardian survives loss of the driver wrapper."""
import fcntl
import json
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
    """Remove temporary Escape binding before discarding durable session state.

    New sessions never change desktop appearance. Old snapshots must be recovered
    with the old version first; do not silently discard an unrestored desktop.
    """
    import cancel_hotkey
    saved=None
    if SNAPSHOT.exists():
        try:
            saved=json.loads(SNAPSHOT.read_text())
            if saved.get('version') not in (2,3) or not re.fullmatch(r'[0-9a-f]{32}',saved['token']):
                raise ValueError('unsupported session snapshot')
        except (OSError,ValueError,TypeError,KeyError,AttributeError):
            print('unsupported session snapshot; recover with the previous version before upgrading',file=sys.stderr)
            return False
    for attempt in range(3):
        try:
            cancel_hotkey.hotkey_off()
            if saved is not None:
                import indicator
                indicator.endpoint(STATE,saved['token']).unlink(missing_ok=True)
                SNAPSHOT.unlink(missing_ok=True)
                (STATE/('stop-'+saved['token'])).unlink(missing_ok=True)
            return True
        except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired):
            if attempt<2:time.sleep(.05)
    print('Escape binding cleanup failed; snapshot retained; run computer-use recover',file=sys.stderr)
    return False


def owner_lock():
    prepare()
    # Keep the historical lock name to exclude owners from the old version too.
    lock=open(STATE/'cursor.lock','a')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError('another automation session is active')
    return lock


def drain_input():
    # Stop markers prevent the next command; finish in-flight input before restore.
    with open(STATE/'desktop.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)


def recover(env, expected=None):
    try:lock=owner_lock()
    except (OSError,RuntimeError):
        if expected is None:raise
        print('session recovery ownership changed; current owner must restore',file=sys.stderr)
        return 1
    with lock:
        if expected is not None:
            try:current=json.loads(SNAPSHOT.read_text()).get('token')
            except (OSError,ValueError):current=None
            if current!=expected:return 0
        request_stop()
        drain_input()
        restored=restore(env)
        return 0 if restored else 1


def guardian(env, pipe, token):
    import cancel_hotkey
    import indicator
    stopping=[False]
    def stop(signum, frame):stopping[0]=True
    for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):signal.signal(sig,stop)
    with owner_lock():
        if SNAPSHOT.exists() and not restore(env):
            raise RuntimeError('previous session cleanup failed')
        if CANCEL.exists():raise RuntimeError('cancelled by user')
        driver_group=None;native=None;server=None
        try:
            # Persist before installing the temporary Escape binding.
            with open(SNAPSHOT,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as stream:
                json.dump({'version':3,'token':token},stream)
                stream.flush();os.fsync(stream.fileno())
            escape_available=False
            try:
                cancel_hotkey.hotkey_on();escape_available=True
            except Exception as exc:
                print(f'warning: temporary Escape binding unavailable: {exc}',file=sys.stderr)
            if stopping[0] or CANCEL.exists():raise RuntimeError('session cancelled during startup')
            server=indicator.listen(STATE,token)
            native=indicator.Native({**env,'CU_ESCAPE_AVAILABLE':'1' if escape_available else '0'})
            if stopping[0] or CANCEL.exists():raise RuntimeError('session cancelled during indicator startup')
            print('ready',flush=True)
            while not stopping[0] and not CANCEL.exists() and not (STATE/('stop-'+token)).exists():
                if native.process.poll() is not None:raise RuntimeError('session indicator lost')
                ready,_,_=select.select([pipe,server],[],[],.05)
                if server in ready:indicator.serve(server,native,token)
                if pipe in ready:
                    message=os.read(pipe,4096)
                    if not message:break
                    if message.strip().isdigit():
                        driver_group=int(message.strip())
                        print('registered',flush=True)
        finally:
            cleanup_ok=True
            try:
                for cleanup in (request_stop,lambda:stop_group(driver_group) if driver_group is not None else None,drain_input,
                                lambda:native.close() if native is not None else None,
                                lambda:server.close() if server is not None else None):
                    try:cleanup()
                    except BaseException as exc:
                        cleanup_ok=False
                        print(f'session cleanup failed: {exc}',file=sys.stderr)
            finally:
                restored=restore(env)
        return 0 if restored and cleanup_ok else 1


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
    # A reaped group leader does not imply its descendants have stopped.
    # Escalate for the entire group before reaping our direct child.
    stop_group(driver.pid)
    driver.wait()


def supervise(env, argv):
    if argv and argv[0]=='--':argv=argv[1:]
    if not argv:raise ValueError('session requires a driver command')
    if os.environ.get('CU_SESSION_TOKEN'):raise RuntimeError('nested automation session refused')
    read_fd,write_fd=os.pipe()
    token=uuid.uuid4().hex
    guard=None;driver=None;gate_read=None;gate_write=None
    outcome=1
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
            raise RuntimeError('session guardian startup failed')
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
                break
            time.sleep(.05)
        else:
            outcome=driver.returncode if driver.returncode>=0 else 1
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
                guard.wait()  # Never SIGKILL the session owner during cleanup.
            guard.stdout.close()
            if SNAPSHOT.exists():
                # Retry any retained snapshot, including exhausted guardian retries.
                recover(env,token)
            # A successful driver cannot hide failed session cleanup.
            if guard.returncode!=0 and outcome==0:outcome=1
        for sig,handler in previous.items():signal.signal(sig,handler)
    return outcome


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

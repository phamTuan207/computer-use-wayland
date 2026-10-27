#!/usr/bin/env python3
"""Persistent user cancellation latch for a computer-use session."""
import argparse
import errno
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import shlex
import sys
import time

STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'agent-computer-use'
CANCEL = STATE / 'cancelled'
HOTKEY = 'agentComputerUseEscapeBind'
# Latches are tiny; never buffer more than this from any state file.
LATCH_READ_LIMIT = 65536

def hypr_eval(code):
    result = subprocess.run(['hyprctl', 'eval', code], capture_output=True, text=True, timeout=2)
    if result.returncode or result.stdout.strip()!='ok':
        raise RuntimeError('Hyprland rejected temporary Escape binding: ' + result.stderr.strip()[:180])

def lua_string(value):
    parts = ['"']
    for byte in value.encode('utf-8'):
        if byte == 34: parts.append('\\"')
        elif byte == 92: parts.append('\\\\')
        elif 32 <= byte <= 126: parts.append(chr(byte))
        else: parts.append(f'\\{byte:03d}')
    parts.append('"')
    return ''.join(parts)

def hotkey_off():
    hypr_eval(f'if _G.{HOTKEY} then _G.{HOTKEY}:unbind(); _G.{HOTKEY}=nil end')

def hotkey_on():
    devices = subprocess.run(['hyprctl', '-j', 'devices'], capture_output=True, text=True, check=True, timeout=2)
    names = [item['name'] for item in json.loads(devices.stdout).get('keyboards', [])
             if ('keyboard' in item.get('name', '').casefold()
                 and not any(excluded in item['name'].casefold()
                             for excluded in ('virtual','consumer-control','system-control')))]
    if not names:
        raise RuntimeError('No physical keyboard found for Escape cancellation')
    keys = ','.join(lua_string(name) for name in names)
    # Explicit attribution: this binding is the only physical Escape path.
    cmd = lua_string(shlex.join(['env','XDG_CACHE_HOME='+str(STATE.parent),
                                 sys.executable,str(Path(__file__).resolve()),'cancel',
                                 '--source','physical-escape']))
    hypr_eval(f'if _G.{HOTKEY} then _G.{HOTKEY}:unbind() end; '
              f'_G.{HOTKEY}=hl.bind("ESCAPE", hl.dsp.exec_cmd({cmd}), '
              f'{{description="Cancel computer-use",device={{inclusive=true,list={{{keys}}}}}}})')

def latch_present(path=None):
    """No-follow cancellation-presence check: one lstat, no metadata parsing.

    Deliberate L1 improvement over the inherited guards: `Path.exists()` follows
    symlinks, so a dangling latch entry used to look 'ready'. Presence contract
    (kept consistent with cancellation_status): ONLY a missing entry
    (FileNotFoundError) is not cancelled; any other lstat error (PermissionError,
    I/O error, ...) means unknown presence and fails closed — True, cancelled.
    Poll-safe — a single syscall, never a metadata read or parse.
    """
    if path is None: path = CANCEL
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return True  # unreadable/unknown presence: fail closed, never 'ready'

def read_regular_bytes(path,limit=LATCH_READ_LIMIT):
    """Bounded read of a regular file; non-blocking, no-follow, single owner.

    Returns None for anything unsupported (missing, symlinked, FIFO, device,
    unreadable): callers treat that as metadata-unknown, never as permission to
    resume or to send input. O_NONBLOCK keeps a FIFO open from ever blocking and
    the fstat regular-file check rejects specials before a single byte is read.
    """
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):return None
        return os.read(fd,limit)
    except OSError:
        return None
    finally:
        os.close(fd)

def _finite_number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)):return False
    try:return math.isfinite(value)
    except OverflowError:return False  # ints too large for float conversion

def _utf8_text(value):
    """Normalize metadata text so strict UTF-8 consumers can never crash.

    A lone UTF-16 surrogate (escapable in JSON, e.g. \\ud800) parses into a
    Python str that json.dumps(..., ensure_ascii=False) surfaces as-is; at a
    real UTF-8 sink (cu.py status print, bridge text) that raises
    UnicodeEncodeError and aborts the report. Valid Unicode passes through
    unchanged; anything the encoder refuses is rewritten with '?' at the
    unencodable run. Size is already bounded by the latch read limit.
    """
    if not isinstance(value,str):return value
    try:
        value.encode('utf-8')
    except UnicodeEncodeError:
        value=value.encode('utf-8','replace').decode('utf-8')
    return value

def latch(path=None, source='cli'):
    """Write the self-describing cancellation latch.

    Metadata (set_at/pid/session_token/source) replaces the bare legacy text so
    every later report can attribute and explain the cancellation. O_NOFOLLOW
    refuses to write through a symlink, fchmod pins the exact 0600 mode, and the
    descriptor is handed to its stream exactly once (the stream alone closes it).
    The target is validated as a regular file BEFORE any truncation, so a FIFO
    or special file is refused instead of being written or blocked on.
    """
    if path is None: path = CANCEL
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    token=None
    raw=read_regular_bytes(path.parent/'session.json')
    if raw is not None:
        try:
            token=json.loads(raw).get('token')
            if not isinstance(token,str):token=None
        except (ValueError,AttributeError,TypeError,RecursionError):pass
        # Deep-corrupt metadata is unknown, not fatal: still write the latch.
    # No O_TRUNC here: validate the target first, truncate only after.
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(errno.ENOTSUP,f'refusing to latch: {path} is not a regular file')
        os.fchmod(fd,0o600)
        os.ftruncate(fd,0)
        stream=os.fdopen(fd,'w',encoding='utf-8')
    except BaseException:
        try:os.close(fd)
        except OSError:pass
        raise
    # Ownership transferred: the stream alone closes the descriptor now.
    with stream:
        json.dump({'set_at':time.time(),'pid':os.getpid(),'session_token':token,
                   'source':source},stream)

def cancellation_status(path=None):
    """Report the latch; any latch entry still means cancelled.

    Presence is decided no-follow via lstat: a dangling symlinked latch is
    present (cancelled), not 'ready' — the inherited `.exists()` check followed
    symlinks and mis-reported that case as absent; this is a deliberate L1
    improvement. Missing or unreadable metadata (legacy text, corrupted JSON,
    non-regular or unreadable files) falls back to the entry's lstat mtime and
    an unknown source, and always keeps the clear_with/instruction guidance:
    corruption is never permission to resume or to send input. Timestamps are
    forced finite so every report stays strict JSON.
    """
    if path is None: path = CANCEL
    try:
        entry=os.lstat(path)
    except FileNotFoundError:return {'cancelled':False}
    except OSError:entry=None
    metadata={}
    raw=read_regular_bytes(path)
    if raw is not None:
        try:
            parsed=json.loads(raw)
            if isinstance(parsed,dict):metadata=parsed
        except (ValueError,RecursionError):pass
        # Deep-corrupt metadata is unknown: report it as such below.
    set_at=metadata.get('set_at')
    if not _finite_number(set_at):
        set_at=entry.st_mtime if entry is not None else None
    if not _finite_number(set_at):set_at=None
    source=_utf8_text(metadata.get('source'))
    if not isinstance(source,str) or not source:source='legacy latch; origin unknown'
    pid=metadata.get('pid')
    if isinstance(pid,bool) or not isinstance(pid,int):pid=None
    session_token=_utf8_text(metadata.get('session_token'))
    if not isinstance(session_token,str):session_token=None
    return {'cancelled':True,'cancellation':{'set_at':set_at,'pid':pid,
            'session_token':session_token,'source':source,
            'clear_with':'computer-use resume',
            'instruction':'Clear only after the user asks to continue.'}}

def cancellation_message(path=None):
    """The 'cancelled by user' prefix stays stable; metadata is appended after it."""
    if path is None: path = CANCEL
    status=cancellation_status(path)
    detail=status['cancellation'] if status['cancelled'] else {}
    return ('cancelled by user; stop this task. Run computer-use resume only after the user asks to continue'
            f' (latch set_at={detail.get("set_at")}, source={detail.get("source")},'
            ' clear with: computer-use resume)')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('cancel', 'resume', 'status', 'hotkey-on', 'hotkey-off'))
    parser.add_argument('--source', default='cli',
                        help='attribution stored in the cancellation latch (direct CLI default; '
                             'the Escape hotkey binding passes --source physical-escape)')
    args = parser.parse_args()
    command = args.command
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE.chmod(0o700)
    if command == 'cancel':
        latch(source=args.source)
        # Latch first; the session guardian stops the driver and removes the binding.
        import cursor_session
        cursor_session.request_stop()
    elif command == 'resume':
        CANCEL.unlink(missing_ok=True)
    elif command == 'hotkey-on':
        hotkey_on()
    elif command == 'hotkey-off':
        hotkey_off()
    else:
        print('cancelled' if latch_present() else 'ready')
    return 0

if __name__ == '__main__':
    sys.exit(main())

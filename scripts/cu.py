#!/usr/bin/env python3
"""Shared local computer-use CLI. No model API calls or daemon required."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import io
import json
import math
import os
import pathlib
from pathlib import Path
import re
import select
import shutil
import socket
import stat
import subprocess
import sys
import time
import uuid

try:
    import jsonlutil
except ImportError:  # loaded by file path without the scripts dir on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import jsonlutil

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'agent-computer-use'
CANCEL = STATE / 'cancelled'
# Default browser CDP endpoint. A successful `browser start` updates it for the
# rest of this process/session; an explicit --endpoint on one later command wins
# for that command only and never silently replaces this default.
BROWSER_ENDPOINT = 'http://127.0.0.1:9222'
SESSION_KEYS = {'XDG_RUNTIME_DIR','WAYLAND_DISPLAY','DISPLAY','HYPRLAND_INSTANCE_SIGNATURE',
                'DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','XDG_SESSION_DESKTOP',
                'XDG_SESSION_TYPE','XDG_SEAT','XDG_VTNR','USER','HOME','LOGNAME','PATH',
                'GDK_BACKEND','QT_QPA_PLATFORM','ELECTRON_OZONE_PLATFORM_HINT',
                'MOZ_ENABLE_WAYLAND'}
_TUPLE_KEYS = ('XDG_RUNTIME_DIR','WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE')
_IDENTITY_KEYS = {'USER','HOME','LOGNAME','PATH'}
_PLATFORM_KEYS = {'GDK_BACKEND','QT_QPA_PLATFORM','ELECTRON_OZONE_PLATFORM_HINT',
                  'MOZ_ENABLE_WAYLAND'}
_ROUTING_KEYS = SESSION_KEYS - _IDENTITY_KEYS
OBSERVATION_SCHEMA = 2
LOW_RES_MAX_WIDTH = 640
OBSERVATION_MAX_AGE = 120
INSTANCE_RE = re.compile(r'[A-Za-z0-9_.-]{1,200}')

MODIFIERS={'ctrl':'ctrl','control':'ctrl','alt':'alt','altgr':'altgr','shift':'shift','super':'logo','meta':'logo','win':'logo','logo':'logo'}
KEY_ALIASES={'enter':'Return','return':'Return','esc':'Escape','escape':'Escape','backspace':'BackSpace',
             'arrowleft':'Left','arrowright':'Right','arrowup':'Up','arrowdown':'Down',
             'left':'Left','right':'Right','up':'Up','down':'Down','pageup':'Prior','pagedown':'Next',
             'home':'Home','end':'End','tab':'Tab','delete':'Delete','insert':'Insert','space':'space',
             'capslock':'Caps_Lock','numlock':'Num_Lock','printscreen':'Print','volumeup':'XF86AudioRaiseVolume',
             'volumedown':'XF86AudioLowerVolume','mute':'XF86AudioMute','playpause':'XF86AudioPlay'}

def key_names(keys):
    import ctypes
    lib=ctypes.CDLL('libxkbcommon.so.0');lib.xkb_keysym_from_name.argtypes=[ctypes.c_char_p,ctypes.c_int];lib.xkb_keysym_from_name.restype=ctypes.c_uint32
    mods=[];regular=[]
    for raw in keys:
        if raw.lower() in MODIFIERS:mods.append(MODIFIERS[raw.lower()]);continue
        k=KEY_ALIASES.get(raw.lower(),raw)
        if re.fullmatch(r'f\d{1,2}',k,re.I):k=k.upper()
        if not lib.xkb_keysym_from_name(k.encode(),0):raise ValueError('unknown XKB key name: '+raw)
        regular.append(k)
    if not regular:raise ValueError('key action needs a non-modifier key')
    if 'shift' in mods:regular=['ISO_Left_Tab' if k=='Tab' else k for k in regular]
    mods=list(dict.fromkeys(mods))
    _reject_blocked_combo(mods,regular)
    return mods,regular

# Destructive combos refused before dispatch (agent-desktop I21).
# Verified against the live Hyprland binds on the reference laptop
# 2026-11-27: Ctrl+Alt+Delete = close all windows, Super+Q = close
# window, Super+Ctrl+P and XF86PowerOff = power menu. VT-switch and
# SysRq are kernel-level. All checks use subset semantics (refuse
# when the dangerous modset is contained in the pressed modset) so
# extra modifiers cannot bypass the refusal; AltGr counts as Alt.
# The power/sleep keysyms are refused even where Hyprland has no
# bind for them, because logind/ACPI may act on them directly.
# Refusals raise ValueError so they surface in the action result
# (logged), never silently dropped.
def _reject_blocked_combo(mods,regular):
    modset=set(mods)
    if 'altgr' in modset:modset=(modset-{'altgr'})|{'alt'}
    for k in regular:
        ku=k.upper()
        if re.fullmatch(r'XF86SWITCH_VT_(?:[1-9]|1[0-2])',ku) or ku in ('TERMINATE_SERVER','XF86LOGOFF'):
            raise ValueError('blocked key combo: '+k+' (session control key)')
        if {'ctrl','alt'}<=modset and re.fullmatch(r'F\d{1,2}',ku):
            raise ValueError('blocked key combo: ctrl+alt+'+k+' (VT switch)')
        if {'ctrl','alt'}<=modset and ku in ('BACKSPACE','DELETE','KP_DELETE'):
            raise ValueError('blocked key combo: ctrl+alt+'+k+' (session/window kill)')
        if (ku=='SYS_REQ' and not modset) or (ku in ('PRINT','SYS_REQ') and modset&{'alt','ctrl'}):
            raise ValueError('blocked key combo: SysRq with modifier ('+k+')')
        if {'logo'}<=modset and ku=='Q':
            raise ValueError('blocked key combo: super+q (close window)')
        if {'logo','ctrl'}<=modset and ku=='P':
            raise ValueError('blocked key combo: super+ctrl+p (power menu)')
        if ku in ('XF86POWEROFF','XF86POWERDOWN','XF86SLEEP','XF86SUSPEND','XF86HIBERNATE'):
            raise ValueError('blocked key combo: '+k+' (power/sleep key)')

def _wtype_executable():
    helper = ROOT / 'native' / 'wtype'
    if not helper.is_file():
        raise RuntimeError('private wtype helper is missing: ' + str(helper))
    return str(helper)


def keyboard_argv(actions):
    args=[_wtype_executable()];total_ms=0
    for a in actions:
        if a['type']=='type':
            # End-of-options text cannot be mixed with subsequent options. TEXT argv is
            # supported by upstream wtype; prefix-dash strings go through stdin separately.
            if a['text'].startswith('-'):raise ValueError('leading-dash text needs standalone literal typing')
            if a.get('delay_ms',0):args+=['-d',str(a['delay_ms'])]
            args+=[a['text']];total_ms+=len(a['text'])*a.get('delay_ms',0)
        elif a['type']=='wait':
            if a.get('ms',100):args+=['-s',str(a.get('ms',100))]
            total_ms+=a.get('ms',100)
        else:
            mods,keys=key_names(a['keys'])
            for m in mods:args+=['-M',m]
            for _ in range(a.get('repeat',1)):
                for k in keys:
                    args+=['-P',k]
                    if a.get('hold_ms',12):args+=['-s',str(a.get('hold_ms',12))]
                    args+=['-p',k];total_ms+=a.get('hold_ms',12)
            for m in reversed(mods):args+=['-m',m]
        args+=['-s','12'];total_ms+=12
    # GTK on this host fails some bindings at the final real keymap slot.
    # Reserve an unused VoidSymbol with release only (no key-down/text/action).
    # A settling delay did not fix it; this also fixes standalone editing keys.
    args+=['-p','VoidSymbol']
    if total_ms>5000:raise ValueError('keyboard group exceeds 5 seconds; split at a checkpoint')
    return args

def standalone_type_argv(a):
    # Leading-dash text cannot be an argv token, so it is typed through stdin by
    # its own wtype process. Preflight the same 5-second budget as a grouped
    # invocation so a standalone literal cannot bypass the group limit.
    if len(a['text'])*a.get('delay_ms',0)+12>5000:
        raise ValueError('keyboard group exceeds 5 seconds; split at a checkpoint')
    argv=[_wtype_executable()]
    if a.get('delay_ms',0):argv+=['-d',str(a['delay_ms'])]
    return argv+['-','-p','VoidSymbol']

def _session_tuple(env):
    return {key:env.get(key) for key in _TUPLE_KEYS}

def _validate_session_tuple(env):
    values=_session_tuple(env)
    runtime,display,instance=(values[k] for k in ('XDG_RUNTIME_DIR','WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE'))
    if not all(isinstance(value,str) and value for value in (runtime,display,instance)):
        raise RuntimeError('incomplete compositor socket/instance tuple; refusing environment discovery')
    if not Path(runtime).is_absolute() or not INSTANCE_RE.fullmatch(instance) or instance in ('.','..'):
        raise RuntimeError('invalid compositor socket/instance tuple')
    if '/' in display or display in ('.','..'):
        raise RuntimeError('invalid Wayland socket name')
    socket_path=Path(runtime)/display
    if not socket_path.is_socket():
        raise RuntimeError('explicit Wayland socket is unavailable; refusing to switch compositor')
    ipc_path=Path(runtime)/'hypr'/instance/'.socket.sock'
    if not ipc_path.is_socket():
        raise RuntimeError('explicit compositor socket is unavailable; refusing to switch compositor')
    try:
        response=subprocess.run(['hyprctl','-j','instances'],env=env,capture_output=True,text=True,timeout=3)
        rows=json.loads(response.stdout) if response.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired,ValueError):
        rows=None
    if (not isinstance(rows,list) or sum(1 for row in rows if isinstance(row,dict) and
            row.get('instance')==instance and row.get('wl_socket')==display)!=1):
        raise RuntimeError('compositor instance does not match the supplied socket tuple; refusing to switch')
    return values

def _private_runtime(path):
    try:
        info=Path(path).lstat()
    except (OSError,TypeError,ValueError):
        return False
    return (stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid() and
            stat.S_IMODE(info.st_mode)==0o700)


def _system_runtime_dir():
    return Path(f'/run/user/{os.geteuid()}')


def _read_process_environ(pid):
    data={}
    raw=Path('/proc',str(pid),'environ').read_bytes().decode('utf-8','surrogateescape')
    for item in raw.split('\0'):
        key,sep,value=item.partition('=')
        if sep and key in SESSION_KEYS:
            data[key]=value
    return data


def _process_owned(pid):
    try:
        info=Path('/proc',str(pid)).lstat()
    except (OSError,TypeError,ValueError):
        return False
    return stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid()


def _process_donors():
    donors=[]
    for name in ('quickshell','waybar','kitty','Hyprland'):
        try:
            found=subprocess.run(['pgrep','-x',name],capture_output=True,text=True,timeout=2)
        except (OSError,subprocess.SubprocessError):
            continue
        for pid in found.stdout.split() if found.returncode==0 else ():
            if not pid.isdigit() or not _process_owned(pid):
                continue
            try:
                if (name=='quickshell' and
                        b'/usr/share/omarchy/shell' not in
                        Path('/proc',pid,'cmdline').read_bytes()):
                    continue
                donors.append({'name':name,'pid':pid,'env':_read_process_environ(pid)})
            except (OSError,UnicodeError,ValueError):
                continue
    return donors


def _probe_environment(base, runtime):
    env=dict(base)
    for key in _TUPLE_KEYS[1:]:
        env.pop(key,None)
    env['XDG_RUNTIME_DIR']=str(runtime)
    return env


def _instance_rows(env):
    try:
        response=subprocess.run(['hyprctl','-j','instances'],env=env,capture_output=True,
                                text=True,timeout=3)
        if response.returncode!=0 or len(response.stdout)>65536:
            return None
        rows=json.loads(response.stdout)
    except (OSError,subprocess.SubprocessError,ValueError,UnicodeError):
        return None
    return rows if isinstance(rows,list) else None


def _tuple_key(env):
    return tuple(env.get(key) for key in _TUPLE_KEYS)


def _verified_donor(donor, base):
    raw=donor['env']
    if not raw.get('WAYLAND_DISPLAY') or not raw.get('HYPRLAND_INSTANCE_SIGNATURE'):
        return None
    runtime=raw.get('XDG_RUNTIME_DIR')
    if not runtime:
        runtime=base.get('XDG_RUNTIME_DIR')
    if not _private_runtime(runtime):
        return None
    candidate=dict(base)
    candidate.update(raw)
    candidate['XDG_RUNTIME_DIR']=runtime
    try:
        _validate_session_tuple(candidate)
    except (OSError,RuntimeError,TypeError,ValueError):
        return None
    return {**raw,'XDG_RUNTIME_DIR':runtime}


def _merge_same_tuple_donors(selected, donor_rows, key):
    result=dict(selected)
    anchor_seat=result.get('XDG_SEAT')
    for donor in donor_rows:
        if _tuple_key(donor)!=key:
            continue
        if anchor_seat and donor.get('XDG_SEAT') and donor['XDG_SEAT']!=anchor_seat:
            continue
        if not anchor_seat and donor.get('XDG_SEAT'):
            anchor_seat=donor['XDG_SEAT']
            result['XDG_SEAT']=anchor_seat
        for name,value in donor.items():
            if name not in SESSION_KEYS or not value or name in _TUPLE_KEYS:
                continue
            if name in _PLATFORM_KEYS and selected.get(name):
                continue
            if not result.get(name):
                result[name]=value
    return result


def _enrich_explicit_tuple(env, donors, key, *, refresh):
    result=dict(env)
    updated=set()
    seat=env.get('XDG_SEAT')
    for donor in donors:
        values=_verified_donor(donor,env)
        if values is None or _tuple_key(values)!=key:
            continue
        if seat and values.get('XDG_SEAT') and values['XDG_SEAT']!=seat:
            continue
        for name,value in values.items():
            if name not in SESSION_KEYS or not value or name in _TUPLE_KEYS:
                continue
            if name in _PLATFORM_KEYS and env.get(name):
                continue
            if name in updated:
                continue
            if refresh or not result.get(name):
                result[name]=value
            updated.add(name)
            if name=='XDG_SEAT' and value:
                seat=value
    return result


def _valid_instance_directory(path, name):
    if not INSTANCE_RE.fullmatch(name) or name in ('.','..'):
        return False
    try:
        info=path.lstat()
        socket_info=(path/'.socket.sock').lstat()
    except OSError:
        return False
    return (stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid() and
            stat.S_ISSOCK(socket_info.st_mode) and socket_info.st_uid==os.geteuid())


def _row_process(pid):
    if isinstance(pid,str) and pid.isdigit():
        pid=int(pid)
    if isinstance(pid,bool) or not isinstance(pid,int) or pid<=0 or not _process_owned(pid):
        return None
    try:
        return _read_process_environ(str(pid))
    except (OSError,UnicodeError,ValueError):
        return None


def _recovered_instances(base, donors):
    runtimes=[]
    for donor in donors:
        runtime=donor['env'].get('XDG_RUNTIME_DIR')
        if runtime and _private_runtime(runtime) and runtime not in runtimes:
            runtimes.append(runtime)
    inherited=base.get('XDG_RUNTIME_DIR')
    if inherited and _private_runtime(inherited) and inherited not in runtimes:
        runtimes.append(inherited)
    system_runtime=_system_runtime_dir()
    if _private_runtime(system_runtime) and str(system_runtime) not in runtimes:
        runtimes.append(str(system_runtime))

    found={}
    for runtime in runtimes:
        root=Path(runtime)/'hypr'
        try:
            root_info=root.lstat()
            if not stat.S_ISDIR(root_info.st_mode) or root_info.st_uid!=os.geteuid():
                continue
            rows=_instance_rows(_probe_environment(base,runtime))
            entries=list(root.iterdir())
        except OSError:
            continue
        if rows is None:
            continue
        for folder in entries:
            name=folder.name
            if not _valid_instance_directory(folder,name):
                continue
            matches=[row for row in rows if isinstance(row,dict) and row.get('instance')==name]
            if len(matches)!=1:
                continue
            row=matches[0]
            pid=row.get('pid')
            if isinstance(pid,str) and pid.isdigit():
                pid=int(pid)
            if isinstance(pid,bool) or not isinstance(pid,int) or pid<=0 or not _process_owned(pid):
                continue
            display=row.get('wl_socket')
            if (not isinstance(display,str) or not display or '/' in display or
                    display in ('.','..')):
                continue
            try:
                wayland_info=(Path(runtime)/display).lstat()
            except OSError:
                continue
            if not stat.S_ISSOCK(wayland_info.st_mode) or wayland_info.st_uid!=os.geteuid():
                continue
            row_env=_row_process(pid)
            candidate=dict(base)
            candidate.update({'XDG_RUNTIME_DIR':runtime,'WAYLAND_DISPLAY':display,
                              'HYPRLAND_INSTANCE_SIGNATURE':name})
            try:
                _validate_session_tuple(candidate)
            except (OSError,RuntimeError,TypeError,ValueError):
                continue
            key=_tuple_key(candidate)
            associated=[]
            if (row_env and row_env.get('XDG_RUNTIME_DIR')==runtime and
                    row_env.get('WAYLAND_DISPLAY')==display):
                associated.append(row_env)
            for donor in donors:
                raw=donor['env']
                if (raw.get('XDG_RUNTIME_DIR')==runtime and
                        raw.get('WAYLAND_DISPLAY')==display):
                    associated.append(raw)
            metadata={}
            seat=None
            for source in associated:
                if seat and source.get('XDG_SEAT') and source['XDG_SEAT']!=seat:
                    continue
                if not seat and source.get('XDG_SEAT'):
                    seat=source['XDG_SEAT']
                for field,value in source.items():
                    if field in SESSION_KEYS and value and field not in _TUPLE_KEYS:
                        metadata.setdefault(field,value)
            metadata.update({'XDG_RUNTIME_DIR':runtime,'WAYLAND_DISPLAY':display,
                             'HYPRLAND_INSTANCE_SIGNATURE':name})
            found.setdefault(key,metadata)
    return found


def _discovery_result(base, donors):
    verified={}
    verified_rows=[]
    for donor in donors:
        values=_verified_donor(donor,base)
        if values is None:
            continue
        key=_tuple_key(values)
        if key in verified:
            verified[key]=_merge_same_tuple_donors(verified[key],(values,),key)
        else:
            verified[key]=values
        verified_rows.append(values)

    recovered=_recovered_instances(base,donors)
    for key,values in recovered.items():
        if key in verified:
            verified[key]=_merge_same_tuple_donors(verified[key],verified_rows,key)
        else:
            verified[key]=values
    if len(verified)>1:
        raise RuntimeError('multiple verified compositor instances; supply one explicit socket/instance tuple')
    if not verified:
        raise RuntimeError('no verified Hyprland GUI environment found')
    key,selected=next(iter(verified.items()))

    # An automatic switch discards routing hints from the old shell. Caller
    # identity and control settings remain available if the donor lacks them.
    result=dict(base)
    for field in _ROUTING_KEYS:
        result.pop(field,None)
    for field,value in selected.items():
        if field not in SESSION_KEYS or not value:
            continue
        if field in _PLATFORM_KEYS and base.get(field):
            continue
        result[field]=value
    result.pop('GTK_IM_MODULE',None)
    _guard_state_home(base,result)
    return result


def _guard_state_home(base, selected):
    home=selected.get('HOME')
    if not home or home==base.get('HOME') or base.get('XDG_CACHE_HOME'):
        return
    try:
        current_home=pathlib.Path.home().resolve()
        state_root=Path(STATE).resolve()
    except OSError:
        return
    if state_root==current_home/'.cache'/'agent-computer-use' and Path(home).resolve()!=current_home:
        raise RuntimeError('donated HOME would change the already computed default computer-use state root')


def environment(base=None, *, refresh=False):
    """Return a new environment with one verified compositor session selected."""
    env=dict(os.environ if base is None else base)
    supplied=_session_tuple(env)
    complete=all(isinstance(value,str) and value for value in supplied.values())
    token=bool(env.get('CU_SESSION_TOKEN'))
    explicit_key=_tuple_key(supplied) if complete else None
    if complete:
        try:
            _validate_session_tuple(env)
        except (OSError,RuntimeError,TypeError,ValueError):
            pass
        else:
            env.pop('GTK_IM_MODULE',None)
            if token:
                return env
            selected=_enrich_explicit_tuple(
                env,_process_donors(),explicit_key,refresh=refresh)
            selected.pop('GTK_IM_MODULE',None)
            _guard_state_home(env,selected)
            return selected
    if token and not complete:
        raise RuntimeError('automation session has no pinned compositor tuple; refusing environment discovery')
    donors=_process_donors()
    return _discovery_result(env,donors)

def compositor_identity(env):
    values=_session_tuple(env or {})
    return {'runtime_dir':values['XDG_RUNTIME_DIR'],'wayland_display':values['WAYLAND_DISPLAY'],
            'instance':values['HYPRLAND_INSTANCE_SIGNATURE']}

def boot_identity():
    try:value=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    except OSError as exc:raise RuntimeError('system boot identity unavailable') from exc
    if not re.fullmatch(r'[0-9a-fA-F-]{36}',value):raise RuntimeError('invalid system boot identity')
    return value

def run(argv, env=None, text=True, input=None, timeout=12):
    p = subprocess.run(argv, env=env, capture_output=True, text=text, input=input, timeout=timeout)
    if p.returncode:
        err = p.stderr if text else p.stderr.decode(errors='replace')
        raise RuntimeError(f'{Path(argv[0]).name}: {err.strip()[:400]}')
    return p.stdout

def hypr(env, what):
    # The documented read-only IPC avoids a fork/exec for every safety check.
    # Keep CLI compatibility for callers without an explicit session environment.
    allowed=('clients','monitors','activewindow','cursorpos','devices','workspaces','layers')
    if what not in allowed:
        detail=' '.join(str(what).split())
        detail=''.join(ch for ch in detail if ch==' ' or 32<=ord(ch)<=126)[:120]
        raise ValueError(('unsupported read-only compositor query: '+detail)[:200])
    if env and env.get('XDG_RUNTIME_DIR') and env.get('HYPRLAND_INSTANCE_SIGNATURE'):
        path=Path(env['XDG_RUNTIME_DIR'])/'hypr'/env['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
            deadline=time.monotonic()+1
            try:
                connection.settimeout(1);connection.connect(str(path))
                connection.sendall(('j/'+what).encode())
                data=bytearray()
                while True:
                    remaining=deadline-time.monotonic()
                    if remaining<=0:raise RuntimeError('compositor query timed out')
                    connection.settimeout(remaining)
                    part=connection.recv(65536)
                    if not part:break
                    data.extend(part)
                    if len(data)>4*1024*1024:raise RuntimeError('compositor response exceeds 4 MiB')
            except socket.timeout:
                raise RuntimeError('compositor query timed out') from None
        return json.loads(data)
    return json.loads(run(['hyprctl','-j',what],env))

def monitor_box(m):
    w,h = m['width'],m['height']
    if m.get('transform',0) % 2: w,h=h,w
    return [m['x'],m['y'],round(w/m['scale']),round(h/m['scale'])]

def window(env, address):
    if not re.fullmatch(r'0x[0-9a-fA-F]+',address or ''): raise ValueError('exact window address required')
    matches = [c for c in hypr(env,'clients') if same_window_address(c.get('address'),address)]
    if len(matches)!=1: raise ValueError('window no longer exists')
    return matches[0]

def same_window_address(left, right):
    return isinstance(left,str) and isinstance(right,str) and left.casefold()==right.casefold()

def focus(env, address):
    if not re.fullmatch(r'0x[0-9a-fA-F]+',address or ''):raise ValueError('exact window address required')
    check_cancel()
    if same_window_address(hypr(env,'activewindow').get('address'),address):return
    window(env,address)  # Reject a stale target before changing the desktop.
    reply=run(['hyprctl','dispatch',f'hl.dsp.focus({{ window = "address:{address}" }})'],env).strip()
    if reply!='ok':raise RuntimeError('focus dispatch rejected: '+reply[:400])
    # Acknowledgment is not focus completion; allow workspace animations to settle.
    deadline=time.monotonic()+1.5
    while True:
        check_cancel()
        active=hypr(env,'activewindow').get('address')
        if same_window_address(active,address):return
        remaining=deadline-time.monotonic()
        if remaining<=0:break
        time.sleep(min(.04,remaining))
    window(env,address)  # Distinguish a closed target from a focus timeout.
    raise RuntimeError(f'target window did not gain focus within 1.5s (target={address}, active={active or "none"})')

def bounds(c): return c['at']+c['size']

def intersect(a,b):
    x,y=max(a[0],b[0]),max(a[1],b[1])
    r,s=min(a[0]+a[2],b[0]+b[2]),min(a[1]+a[3],b[1]+b[3])
    if r<=x or s<=y: raise ValueError('window/crop outside selected monitor')
    return [x,y,r-x,s-y]

def prepare_state():
    STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    STATE.chmod(0o700)

def cancel_hotkey_module():
    # cu.py can be loaded by file path (spec_from_file_location) without its
    # directory on sys.path; retry the sibling import with the script dir added.
    try:
        import cancel_hotkey
    except ModuleNotFoundError:
        sys.path.insert(0,str(Path(__file__).resolve().parent))
        import cancel_hotkey
    return cancel_hotkey

def check_cancel():
    token=os.environ.get('CU_SESSION_TOKEN')
    if token:
        try:current=json.loads((STATE/'session.json').read_text()).get('token')
        except (OSError,ValueError):current=None
        if current!=token or (STATE/('stop-'+token)).exists():
            raise RuntimeError('automation session ended; stop this task')
    cancel=cancel_hotkey_module()
    if cancel.latch_present(CANCEL):
        raise RuntimeError(cancel.cancellation_message(CANCEL))

JSON_LIMIT=8*1024*1024

def read_json(stream):
    """Parse at most 8 MiB of UTF-8 JSON, refusing before the whole input is buffered.

    A text stream is capped by its encoded byte length, not its character count, so a
    multi-byte payload cannot slip past the limit.
    """
    stream=getattr(stream,'buffer',stream)
    chunks=[];total=0
    while True:
        chunk=stream.read(min(65536,JSON_LIMIT-total+1))
        if not chunk:break
        total+=len(chunk.encode()) if isinstance(chunk,str) else len(chunk)
        if total>JSON_LIMIT:raise ValueError('JSON input exceeds 8 MiB')
        chunks.append(chunk)
    if not chunks:raise ValueError('empty JSON input')
    return json.loads(''.join(chunks) if isinstance(chunks[0],str) else b''.join(chunks))

def read_json_file(path):
    with open(path,'rb') as stream:return read_json(stream)

def run_cancelable(argv, env=None, input=None, timeout=12, capture_stderr=None):
    try:check_cancel()
    except BaseException:
        if capture_stderr is not None:capture_stderr.append('')
        raise
    try:
        p=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    except BaseException:
        if capture_stderr is not None:capture_stderr.append('')
        raise
    stderr_captured=False
    def save_stderr(value):
        nonlocal stderr_captured
        if capture_stderr is not None and not stderr_captured:
            if isinstance(value,bytes):value=value.decode('utf-8','replace')
            capture_stderr.append((value or '')[:400])
            stderr_captured=True
    try:
        deadline=time.monotonic()+timeout
        first=True
        while True:
            check_cancel()
            try:
                out,err=p.communicate(input if first else None,timeout=min(.05,max(.001,deadline-time.monotonic())))
                save_stderr(err)
                break
            except subprocess.TimeoutExpired:
                first=False
                if time.monotonic()>=deadline: raise RuntimeError(f'{Path(argv[0]).name}: timed out')
        if p.returncode: raise RuntimeError(f'{Path(argv[0]).name}: {(err.strip() or out.strip())[:400]}')
        check_cancel()
        return out
    except BaseException as error:
        # KeyboardInterrupt/SystemExit must still reap the owned child, then the
        # original termination propagates. No retry, no respawn, no continuation.
        if p.poll() is None:
            try:
                p.terminate()
                out,err=p.communicate(timeout=.5)
                save_stderr(err)
            except BaseException:
                try:
                    p.kill();out,err=p.communicate(timeout=.5);save_stderr(err)
                except BaseException:pass      # the original termination still propagates
        if not stderr_captured:save_stderr(getattr(error,'stderr',None))
        raise

def _sequence(value,length,name,positive_indices=()):
    if not isinstance(value,(list,tuple)) or len(value)!=length:
        raise ValueError(name+' must contain '+str(length)+' values')
    out=[]
    for index,item in enumerate(value):
        try:valid=not isinstance(item,bool) and isinstance(item,(int,float)) and math.isfinite(item)
        except OverflowError:valid=False
        if not valid or index in positive_indices and item<=0:
            raise ValueError(name+' contains an invalid dimension')
        out.append(item)
    return out

def _finite_number(value):
    try:return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)
    except OverflowError:return False

def validate_coordinate_metadata(meta,require_frame=False):
    if not isinstance(meta,dict):raise ValueError('observation metadata must be an object')
    iw,ih=_sequence(meta.get('image_size'),2,'image_size',(0,1))
    rx,ry,rw,rh=_sequence(meta.get('region'),4,'region',(2,3))
    if any(isinstance(value,bool) or not isinstance(value,int) for value in (iw,ih,rx,ry,rw,rh)):
        raise ValueError('image_size and region must use integer pixel dimensions')
    max_width=meta.get('max_width')
    if max_width is not None:
        if isinstance(max_width,bool) or not isinstance(max_width,int) or not 320<=max_width<=3840:
            raise ValueError('max_width must be an integer from 320 to 3840')
        expected_width=min(rw,max_width)
        expected_height=round(rh*expected_width/rw)
        if [iw,ih]!=[expected_width,expected_height]:
            raise ValueError('image dimensions do not match the captured region')
    if require_frame or 'monitor_box' in meta:
        mx,my,mw,mh=_sequence(meta.get('monitor_box'),4,'monitor_box',(2,3))
        if any(isinstance(value,bool) or not isinstance(value,int) for value in (mx,my,mw,mh)):
            raise ValueError('monitor_box must use integer logical dimensions')
        if rx<mx or ry<my or rx+rw>mx+mw or ry+rh>my+mh:
            raise ValueError('observation region is outside its monitor')
    if require_frame or 'monitor_scale' in meta:
        scale=meta.get('monitor_scale')
        if not _finite_number(scale) or scale<=0:
            raise ValueError('monitor_scale must be finite and positive')
        transform=meta.get('monitor_transform')
        if isinstance(transform,bool) or not isinstance(transform,int) or not 0<=transform<=7:
            raise ValueError('monitor_transform must be an integer from 0 to 7')
    if meta.get('scope')=='window' or require_frame and meta.get('scope')!='screen':
        x,y,w,h=_sequence(meta.get('window_bounds'),4,'window_bounds',(2,3))
        if any(isinstance(value,bool) or not isinstance(value,int) for value in (x,y,w,h)):
            raise ValueError('window_bounds must use integer logical dimensions')
        if rx<x or ry<y or rx+rw>x+w or ry+rh>y+h:
            raise ValueError('observation region is outside its window')
    if meta.get('scope') not in ('window','screen') and require_frame:
        raise ValueError('observation scope must be window or screen')
    if 'monitor' in meta and (not isinstance(meta['monitor'],str) or not meta['monitor']):
        raise ValueError('observation monitor is invalid')
    if meta.get('crop') is not None:
        cx,cy,cw,ch=_sequence(meta['crop'],4,'crop',(2,3))
        if (any(isinstance(value,bool) or not isinstance(value,int) for value in (cx,cy,cw,ch)) or
                cx<0 or cy<0):raise ValueError('crop must use non-negative integer coordinates')
        if meta.get('scope')=='window':
            x,y,w,h=meta['window_bounds']
            if cx+cw>w or cy+ch>h or rx<x+cx or ry<y+cy or rx+rw>x+cx+cw or ry+rh>y+cy+ch:
                raise ValueError('observation region does not match its window crop')
        elif meta.get('scope')=='screen' and 'monitor_box' in meta:
            mx,my,mw,mh=meta['monitor_box']
            if cx+cw>mw or cy+ch>mh or [rx,ry,rw,rh]!=[mx+cx,my+cy,cw,ch]:
                raise ValueError('observation region does not match its screen crop')
    elif require_frame and meta.get('scope')=='window':
        x,y,w,h=meta['window_bounds'];mx,my,mw,mh=meta['monitor_box']
        expected=[max(x,mx),max(y,my),min(x+w,mx+mw)-max(x,mx),min(y+h,my+mh)-max(y,my)]
        if [rx,ry,rw,rh]!=expected:
            raise ValueError('observation region does not match its window bounds')
    elif require_frame and meta.get('scope')=='screen':
        if [rx,ry,rw,rh]!=meta['monitor_box']:
            raise ValueError('observation region does not match its monitor')
    return iw,ih,rx,ry,rw,rh

def _valid_capture_identity(meta,env):
    if meta.get('observation_schema')!=OBSERVATION_SCHEMA:
        raise ValueError('legacy observation has no capture identity; observe again')
    mono=meta.get('capture_started_monotonic')
    wall=meta.get('capture_started_wall')
    created=meta.get('created')
    for value,name in ((mono,'capture_started_monotonic'),(wall,'capture_started_wall'),(created,'created')):
        if not _finite_number(value) or value<=0:
            raise ValueError(name+' is invalid; observe again')
    if meta.get('capture_boot_id')!=boot_identity():
        raise ValueError('observation belongs to another system boot; observe again')
    age=time.monotonic()-mono
    if not 0<=age<=OBSERVATION_MAX_AGE:
        raise ValueError('observation older than 120s or from a future clock; observe again')
    if created<wall:
        raise ValueError('observation creation time predates capture; observe again')
    if meta.get('capture_compositor')!=compositor_identity(env):
        raise ValueError('observation belongs to another compositor instance; observe again')
    return age

def validate_desktop_observation(meta,env,observation_path=None,load_image=False):
    if not isinstance(meta,dict) or meta.get('backend')!='desktop':
        raise ValueError('desktop observation required')
    if observation_path is None:
        observation_path=meta.get('observation')
    validate_coordinate_metadata(meta,require_frame=True)
    _valid_capture_identity(meta,env)
    if meta.get('image_role')!='clean-observation' or meta.get('cursor_debug') is True or meta.get('cursor_visible') is True:
        raise ValueError('cursor-debug images cannot be used for input')
    if observation_path is not None:
        if not isinstance(observation_path,(str,os.PathLike)):
            raise ValueError('observation path is invalid; observe again')
        path=Path(observation_path)
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
            with os.fdopen(fd,'rb') as stream:
                st=os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid!=os.geteuid() or
                        stat.S_IMODE(st.st_mode)!=0o600 or st.st_size>JSON_LIMIT):
                    raise ValueError('observation file is not a private regular file')
                disk_meta=read_json(stream)
        except (OSError,ValueError) as exc:raise ValueError('observation file is unavailable or invalid; observe again') from exc
        if disk_meta!=meta or meta.get('observation')!=str(path):
            raise ValueError('observation file changed after delivery; observe again')
        token=meta.get('id')
        if not isinstance(token,str) or not re.fullmatch(r'[0-9a-f]{12}',token):
            raise ValueError('observation identity is invalid; observe again')
        image=Path(meta.get('image',''))
        if (path.name!=token+'.json' or image.name!=token+'.jpg' or
                path.parent.resolve()!=STATE.resolve() or image.parent.resolve()!=STATE.resolve()):
            raise ValueError('observation paths do not match their identity; observe again')
        try:
            fd=os.open(image,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
            with os.fdopen(fd,'rb') as stream:
                st=os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid!=os.geteuid() or
                        stat.S_IMODE(st.st_mode)!=0o600 or st.st_size>256*1024*1024):
                    raise ValueError('observation image is not a private regular file')
                raw=stream.read()
            if (meta.get('image_format')!='JPEG' or len(raw)!=meta.get('image_bytes') or
                    hashlib.sha256(raw).hexdigest()!=meta.get('image_sha256')):
                raise ValueError('observation image changed after delivery; observe again')
            from PIL import Image
            with Image.open(io.BytesIO(raw)) as decoded:
                decoded.load()
                if decoded.format!='JPEG' or decoded.mode!='RGB' or list(decoded.size)!=meta.get('image_size'):
                    raise ValueError('observation image dimensions or format changed; observe again')
                if hashlib.sha256(decoded.tobytes()).hexdigest()!=meta.get('pixel_sha256'):
                    raise ValueError('observation pixels changed after delivery; observe again')
                verified_image=decoded.copy()
        except OSError as exc:raise ValueError('observation image is unavailable; observe again') from exc
        return verified_image if load_image else True
    return True

def save_observation(image, meta, max_width, persist=True, encoded_png=None):
    from PIL import Image
    if isinstance(max_width,bool) or not isinstance(max_width,int) or max_width<320 or max_width>3840: raise ValueError('max-width must be 320..3840')
    if encoded_png is not None:
        # Pixel source only (browser PNG): decode to fresh RGB, strip metadata.
        # Always re-encoded as JPEG below; no byte passthrough, so the stored
        # form is always JPEG and validate can hash stored pixels exactly.
        with Image.open(io.BytesIO(encoded_png)) as decoded:
            decoded.load()
            image=decoded.convert('RGB')
            image.info.clear()
    if image.width>max_width:
        image=image.resize((max_width,round(image.height*max_width/image.width)),Image.Resampling.LANCZOS)
    if image.width<=0 or image.height<=0:raise ValueError('observation image dimensions must be positive')
    meta.update(image_size=list(image.size),max_width=max_width)
    if meta.get('backend')=='desktop':
        meta['observation_schema']=OBSERVATION_SCHEMA
        meta.setdefault('image_role','clean-observation')
        validate_coordinate_metadata(meta,require_frame=True)
        if not all(key in meta for key in ('capture_started_monotonic','capture_started_wall','capture_boot_id','capture_compositor')):
            raise ValueError('desktop capture identity is incomplete')
    if not persist:
        meta.update(image_format='JPEG',image_bytes=None,image_sha256=None,encode_ms=0)
        meta.pop('_environment',None)
        return image,meta
    prepare_state()
    token=uuid.uuid4().hex[:12]
    path=STATE/(token+'.jpg')
    encode_start=time.monotonic()
    # JPEG q90, no chroma subsampling (4:4:4). Pillow defaults to 4:2:0 at q90,
    # which smears colored small-text edges (measured max pixel error 80 vs 39
    # on a real 960-wide frame). Never below q85: blocking artifacts blur text.
    buffer=io.BytesIO();image.save(buffer,format='JPEG',quality=90,subsampling=0);encoded=buffer.getvalue()
    encode_ms=round((time.monotonic()-encode_start)*1000,3)
    # pixel_sha256 must hash the STORED pixels. JPEG is lossy, so the decoded
    # file differs slightly from the pre-encode image; hash the JPEG decode so
    # validate_desktop_observation still compares exactly.
    with Image.open(io.BytesIO(encoded)) as stored:
        stored.load()
        pixel_sha256=hashlib.sha256(stored.convert('RGB').tobytes()).hexdigest()
    # Exclusive creation at 0600 before the first byte: a colliding name or a
    # symlink refuses instead of overwriting a foreign file. fchmod fixes the
    # exact mode regardless of umask; no pathname chmod follows the write.
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        os.fchmod(fd,0o600)
        stream=os.fdopen(fd,'wb')
    except BaseException:
        try:os.close(fd)
        except OSError:pass
        raise
    # Ownership transferred: the stream alone closes the descriptor now.
    with stream:stream.write(encoded)
    meta.update(id=token,created=time.time(),image=str(path),image_size=list(image.size),
                pixel_sha256=pixel_sha256,max_width=max_width,
                image_format='JPEG',image_bytes=len(encoded),image_sha256=hashlib.sha256(encoded).hexdigest(),encode_ms=encode_ms)
    meta.pop('_environment',None)
    out=STATE/(token+'.json');meta['observation']=str(out)
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        os.fchmod(fd,0o600)
        stream=os.fdopen(fd,'w',encoding='utf-8')
    except BaseException:
        try:os.close(fd)
        except OSError:pass
        raise
    with stream:
        stream.write(json.dumps(meta,allow_nan=False))
    # Only observation filenames are disposable; session.json is recovery state.
    for old in STATE.iterdir():
        if re.fullmatch(r'[0-9a-f]{12}\.(?:png|jpg|json)',old.name) and time.time()-old.stat().st_mtime>86400:
            old.unlink()
    return meta

def require_visible_window(c, m):
    visible={m.get('activeWorkspace',{}).get('id'),m.get('specialWorkspace',{}).get('id')}
    visible.discard(None);visible.discard(0)
    if c.get('mapped') is False or c.get('hidden') or (not c.get('pinned') and c.get('workspace',{}).get('id') not in visible):
        raise RuntimeError('window is not visible on its monitor; switch workspace yourself or use observe --window ADDRESS --focus')

def _capture_identity(env):
    return {'capture_started_monotonic':time.monotonic(),
            'capture_started_wall':time.time(),
            'capture_boot_id':boot_identity(),
            'capture_compositor':compositor_identity(env)}

def observe(env, address, crop=None, max_width=960, activate=False, persist=True, low_res=False):
    low_res=bool(low_res)
    if low_res:max_width=min(max_width,LOW_RES_MAX_WIDTH)
    from PIL import Image
    if activate: focus(env,address)
    c=window(env,address)
    monitors=hypr(env,'monitors')
    m=next((m for m in monitors if m['id']==c['monitor']),None)
    if not m: raise RuntimeError('window monitor unavailable')
    require_visible_window(c,m)
    wb=bounds(c);mb=monitor_box(m)
    if crop is None:
        region=wb
    else:
        # screen_region() raises on an out-of-bounds crop; do the same here.
        # intersect() alone would silently return a smaller region, so a --crop
        # that runs past the edge would capture something other than what was
        # asked for, and the agent would read coordinates off the wrong area.
        x,y,w,h=crop
        if w<=0 or h<=0 or x<0 or y<0 or x+w>wb[2] or y+h>wb[3]:
            raise ValueError('crop must be a positive rectangle inside the selected window')
        region=[wb[0]+x,wb[1]+y,w,h]
    region=intersect(intersect(region,wb),mb)
    # grim -s 1 uses logical layout pixels; explicitly exclude the cursor (no -c).
    geometry=f'{region[0]},{region[1]} {region[2]}x{region[3]}'
    capture_identity=_capture_identity(env)
    start=capture_identity['capture_started_monotonic']
    from indicator import capture_clean
    with capture_clean(STATE):
        raw=run(['grim','-s','1','-g',geometry,'-t','ppm','-'],env,text=False)
    capture_ms=round((time.monotonic()-start)*1000,3)
    decode_start=time.monotonic()
    image=Image.open(io.BytesIO(raw)).convert('RGB')
    decode_ms=round((time.monotonic()-decode_start)*1000,3)
    current=window(env,address)
    if bounds(current) != wb or current['monitor']!=c['monitor']: raise RuntimeError('window moved during capture; observe again')
    current_monitor=next((item for item in hypr(env,'monitors') if item['id']==current['monitor']),None)
    if not current_monitor or monitor_box(current_monitor)!=mb or current_monitor['scale']!=m['scale'] or current_monitor.get('transform',0)!=m.get('transform',0):
        raise RuntimeError('monitor layout changed during capture; observe again')
    require_visible_window(current,current_monitor)
    meta={'backend':'desktop','scope':'window','window':address,'window_bounds':wb,'monitor':m['name'],
          'monitor_box':mb,'monitor_scale':m['scale'],'monitor_transform':m.get('transform',0),
          'region':region,'crop':crop,'low_res':low_res,'capture_ms':capture_ms,'decode_ms':decode_ms,
          'capture_elapsed_ms':round((time.monotonic()-start)*1000,3),**capture_identity}
    return save_observation(image,meta,max_width,persist)

def screen_region(monitor_box_,crop):
    mx,my,mw,mh=monitor_box_
    if crop is None:return monitor_box_.copy()
    x,y,w,h=crop
    if w<=0 or h<=0 or x<0 or y<0 or x+w>mw or y+h>mh:
        raise ValueError('crop must be a positive rectangle inside the selected monitor')
    return [mx+x,my+y,w,h]

def observe_screen(env,monitor,crop=None,max_width=960,persist=True,low_res=False):
    low_res=bool(low_res)
    if low_res:max_width=min(max_width,LOW_RES_MAX_WIDTH)
    from PIL import Image
    m=next((m for m in hypr(env,'monitors') if m['name']==monitor),None)
    if not m:raise ValueError('monitor no longer exists; use doctor to list monitors')
    mb=monitor_box(m);region=screen_region(mb,crop)
    geometry=f'{region[0]},{region[1]} {region[2]}x{region[3]}'
    capture_identity=_capture_identity(env)
    start=capture_identity['capture_started_monotonic']
    from indicator import capture_clean
    with capture_clean(STATE):
        raw=run(['grim','-s','1','-g',geometry,'-t','ppm','-'],env,text=False)
    capture_ms=round((time.monotonic()-start)*1000,3)
    decode_start=time.monotonic()
    image=Image.open(io.BytesIO(raw)).convert('RGB')
    decode_ms=round((time.monotonic()-decode_start)*1000,3)
    current=next((m for m in hypr(env,'monitors') if m['name']==monitor),None)
    if not current or monitor_box(current)!=mb or current['scale']!=m['scale'] or current.get('transform',0)!=m.get('transform',0):
        raise RuntimeError('monitor layout changed during capture; observe again')
    meta={'backend':'desktop','scope':'screen','monitor':monitor,'monitor_box':mb,
          'monitor_scale':m['scale'],'monitor_transform':m.get('transform',0),
          'region':region,'crop':crop,'low_res':low_res,'capture_ms':capture_ms,'decode_ms':decode_ms,
          'capture_elapsed_ms':round((time.monotonic()-start)*1000,3),**capture_identity}
    return save_observation(image,meta,max_width,persist)

def image_point(meta,x,y):
    if not all(_finite_number(v) for v in (x,y)): raise ValueError('finite coordinates required')
    iw,ih,rx,ry,rw,rh=validate_coordinate_metadata(meta)
    if not (0<=x<iw and 0<=y<ih): raise ValueError('point outside observed image')
    return rx+x*rw/iw, ry+y*rh/ih

def _action_points_changed(old,new,actions):
    from PIL import ImageChops,ImageStat
    if old.size!=new.size:return True
    diff=ImageChops.difference(old,new)
    for a in actions:
        points=[a.get('from'),a.get('to')] if a['type']=='drag' else [[a.get('x'),a.get('y')]]
        for point in points:
            if not point or point[0] is None:continue
            x,y=point;patch=diff.crop((max(0,int(x)-24),max(0,int(y)-24),min(old.width,int(x)+25),min(old.height,int(y)+25)))
            if sum(ImageStat.Stat(patch).mean)/3>6:return True
    return False

def _mean_image_difference(old,new):
    from PIL import ImageChops,ImageStat
    if old.size!=new.size:return float('inf')
    return sum(ImageStat.Stat(ImageChops.difference(old,new)).mean)/3

def screen_changed(old,new,actions):
    if old.size!=new.size:return True
    if _mean_image_difference(old,new)>3:return True
    # A small button can move without changing the global average appreciably.
    return _action_points_changed(old,new,actions)

def finite(value,name):
    # bool is a subclass of int, so True would otherwise reach a numeric command.
    try:valid=not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)
    except OverflowError:valid=False
    if not valid:raise ValueError(name+' must be a finite number')
    return value

def integer(value,name):
    if isinstance(value,bool) or not isinstance(value,int): raise ValueError(name+' must be an integer')
    return value

def validate_actions(actions,backend):
    if not isinstance(actions,list) or not 1<=len(actions)<=32: raise ValueError('actions must contain 1..32 items')
    allowed=({'click','double_click','move','hover','drag','scroll','type','key','wait'} if backend=='desktop' else
             {'click','set_text'} if backend=='a11y' else
             {'click','confirm_click','fill','set_value','key','scroll','wait','assert'})
    for a in actions:
        if not isinstance(a,dict) or not isinstance(a.get('type'),str) or a['type'] not in allowed: raise ValueError('unsupported action')
        if backend=='desktop' and a['type'] in ('move','hover','click','double_click','drag','scroll'):
            modifiers=a.get('modifiers',[])
            if not isinstance(modifiers,list) or len(modifiers)>5 or not all(isinstance(m,str) and m.lower() in MODIFIERS for m in modifiers):
                raise ValueError('mouse modifiers must be an array of Ctrl/Shift/Alt/Super/AltGr')
            if a['type'] in ('move','hover') and modifiers:raise ValueError('modifiers require click, drag or scroll')
        if a['type']=='wait':
            if not 0<=integer(a.get('ms',100),'wait ms')<=2000: raise ValueError('wait ms must be 0..2000')
        if a['type'] in ('type','fill','set_value') and (not isinstance(a.get('text'),str) or len(a['text'])>10000): raise ValueError('text must be string <=10000 chars')
        if a['type']=='key' and (not isinstance(a.get('keys'),list) or not a['keys'] or not all(isinstance(k,str) and len(k)<40 for k in a['keys'])): raise ValueError('keys must be an array of key names')
        if backend=='desktop' and a['type']=='type' and any(ord(c)>0xffff for c in a['text']):
            raise ValueError('non-BMP text may be corrupted by Wayland keyboard input; use browser fill or a11y set_text')
        if backend=='desktop' and a['type']=='key':
            key_names(a['keys'])
            if not 1<=integer(a.get('repeat',1),'repeat')<=30:raise ValueError('repeat must be 1..30')
            if not 0<=integer(a.get('hold_ms',12),'hold_ms')<=2000:raise ValueError('hold_ms must be 0..2000')
        if backend=='desktop' and a['type']=='type' and not 0<=integer(a.get('delay_ms',0),'delay_ms')<=100:raise ValueError('delay_ms must be 0..100')
        if backend=='desktop' and a['type']=='type' and a.get('ime','literal') not in ('literal','compose'):raise ValueError('ime must be literal or compose')
        if backend=='a11y':
            if not isinstance(a.get('ref'),str) or not a['ref'].strip():raise ValueError('a11y actions need a ref')
            if a['type']=='set_text' and (not isinstance(a.get('text'),str) or len(a['text'])>10000):raise ValueError('a11y set_text needs string text <=10000')
        if backend=='desktop' and a['type'] in ('click','double_click','drag'):
            if a.get('button','left') not in ('left','right','middle'):raise ValueError('invalid button')
        if backend=='desktop' and a['type'] in ('move','hover','click','double_click','scroll'):
            for k in ('x','y'):
                if k not in a:raise ValueError(a['type']+' needs numeric x and y')
                finite(a[k],a['type']+' '+k)
        if backend=='desktop' and a['type']=='drag':
            for k in ('from','to'):
                if not isinstance(a.get(k),(list,tuple)) or len(a[k])!=2:raise ValueError('drag needs exactly two [x,y] points')
                for i,v in enumerate(a[k]):finite(v,'drag '+k+' '+str(i))
            if not 50<=integer(a.get('ms',300),'drag ms')<=2000:raise ValueError('drag ms must be 50..2000')
        if a['type']=='scroll':
            for k in ('dx','dy'):
                if k in a:finite(a[k],'scroll '+k)
            if backend=='desktop' and not all(abs(a.get(k,0))<=2000 for k in ('dx','dy')):raise ValueError('scroll dx/dy must be finite numbers within +/-2000')
            if backend=='browser':
                if 'dy' not in a:raise ValueError('browser scroll needs dy')
                for k in ('x','y'):
                    if k in a:finite(a[k],'scroll '+k)
        if backend=='browser' and a['type'] in ('click','confirm_click','fill','set_value','assert'):
            # Locator presence is optional here by existing contract; the adapter
            # requires exactly one. Types and mutual exclusion are checked early.
            if 'ref' in a and 'selector' in a:raise ValueError('ref and selector are mutually exclusive')
            for k in ('ref','selector'):
                if k in a and (not isinstance(a[k],str) or not a[k].strip()):raise ValueError(k+' must be a non-empty string')
        if backend=='browser' and a['type']=='confirm_click':
            for k,limit in (('expected_role',64),('expected_name',120),('expected_text',256)):
                if (not isinstance(a.get(k),str) or not a[k].strip() or
                        len(a[k].encode('utf-16-le','surrogatepass'))>limit*2):
                    raise ValueError('confirm_click requires expected_role, expected_name and expected_text')
        if backend=='browser' and a['type']=='assert':
            if 'value' in a and not isinstance(a['value'],str):raise ValueError('assert value must be a string')
            if 'text' in a and not isinstance(a['text'],str):raise ValueError('assert text must be a string')
            if 'checked' in a and not isinstance(a['checked'],bool):raise ValueError('assert checked must be a boolean')
            if 'timeout_ms' in a:
                # Non-negative finite only; the adapter clamps the wait to 3000 ms.
                if finite(a['timeout_ms'],'assert timeout_ms')<0:raise ValueError('assert timeout_ms must not be negative')

def validate_terminal_assert(actions):
    """Validate the effective final predicate using adapter precedence."""
    last=actions[-1] if actions else {}
    if last.get('type')!='assert':raise ValueError('--no-after requires the final action to be assert')
    effective=('value' if 'value'in last else 'text' if 'text'in last else
               'checked' if 'checked'in last else '')
    meaningful=(isinstance(last['value'],str) if effective=='value' else
                isinstance(last['text'],str) and last['text'] if effective=='text' else
                isinstance(last['checked'],bool) if effective=='checked' else False)
    if not meaningful:raise ValueError('--no-after final assert needs text, value or checked')

def keyboard_groups(actions):
    groups=[];delay=0;boundary=False;mode=None
    for a in actions:
        if a['type'] in ('key','type') and not (a['type']=='type' and a['text'].startswith('-')):
            # wtype -d 0 is invalid: start a fresh process to reset a nonzero delay.
            reset=a['type']=='type' and delay and not a.get('delay_ms',0)
            focus_key=a['type']=='key' and any(k.lower() in ('tab','enter','return','escape','esc') for k in a['keys'])
            next_mode=a.get('ime','literal') if a['type']=='type' else mode
            if groups and isinstance(groups[-1],list) and not (reset or boundary or focus_key or (mode and next_mode!=mode)):groups[-1].append(a)
            else:groups.append([a]);delay=0
            boundary=focus_key;mode=next_mode
            if a['type']=='type':delay=a.get('delay_ms',0)
        else:groups.append(a);delay=0;boundary=False;mode=None
    return groups

def fcitx5_running():
    """True when an own-UID fcitx5 process exists; False when confidently absent.

    Only the process table is read: numeric /proc entries, owner UID and the comm
    name. Unreadable live state is refused; exited processes are skipped as a
    normal scan race. No command lines, environments, PIDs, caches or new dependencies.
    """
    try:
        entries=os.listdir('/proc')
    except OSError as exc:
        raise RuntimeError('cannot determine whether fcitx5 is running: process list '+type(exc).__name__) from exc
    for pid in entries:
        if not pid.isdigit():
            continue
        try:
            owner=os.stat('/proc/'+pid).st_uid
        except (FileNotFoundError,ProcessLookupError):
            continue  # the process exited while being read
        except OSError as exc:
            raise RuntimeError('cannot determine whether fcitx5 is running: process status '+type(exc).__name__) from exc
        if owner!=os.geteuid():
            continue
        try:
            with open('/proc/'+pid+'/comm') as stream:name=stream.read().strip()
        except (FileNotFoundError,ProcessLookupError):
            continue
        except (OSError,UnicodeError) as exc:
            raise RuntimeError('cannot determine whether fcitx5 is running: process name '+type(exc).__name__) from exc
        if not name or not name.isprintable():
            raise RuntimeError('cannot determine whether fcitx5 is running: process name invalid')
        if name=='fcitx5':
            return True
    return False

@contextmanager
def literal_keyboard(env,enabled=True,result=None):
    """Bypass composition for exact text; preserve the focused context's IME state."""
    import signal
    remote=shutil.which('fcitx5-remote') if enabled else None
    trace=result.setdefault('ime_state_trace',[]) if result is not None else []
    def record(phase,value=None,source='not_observed',status='skipped'):
        trace.append({'phase':phase,'state':value,'im':None,
                      'state_source':source,'status':status})
    if not remote:
        reason='remote_absent' if enabled else 'compose_disabled'
        record('before',status=reason)
        if enabled and fcitx5_running():
            raise RuntimeError('literal typing requires fcitx5-remote while fcitx5 is running')
        record('after_switch',status=reason)
        try:yield
        finally:record('after_restore',status=reason)
        return
    def state(timeout):
        value=run([remote],env,timeout=timeout).strip()
        if value not in ('0','1','2'):raise RuntimeError('cannot determine fcitx5 state')
        return value
    def switch(flag,expected,budget=.5):
        # One cumulative budget per switch, set before the flag command runs.
        deadline=time.monotonic()+budget
        remaining=deadline-time.monotonic()
        if remaining<=0:raise RuntimeError('fcitx5 state change timed out')
        try:
            run([remote,flag],env,timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError('fcitx5 state change timed out') from exc
        for _ in range(50):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise RuntimeError('fcitx5 state change timed out')
            try:
                current=state(remaining)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError('fcitx5 state change timed out') from exc
            if current==expected:
                # A reply that arrived after the budget is not a success.
                if time.monotonic()>=deadline:raise RuntimeError('fcitx5 state change timed out')
                return current
            time.sleep(min(.01,max(0,deadline-time.monotonic())))
        raise RuntimeError('fcitx5 state change timed out')
    def warn_restore(restore_error,primary):
        if result is not None:result['ime_restore_failed']=True
        # One bounded single line on stderr: a stable label plus the sanitized
        # RESTORE detail only. The primary message is never echoed; it may carry
        # wtype stderr or user input. Only its type names it, never its text.
        try:
            detail=' '.join(str(restore_error).split())
            detail=''.join(ch for ch in detail if ch==' ' or 32<=ord(ch)<=126)
            label=(' during '+type(primary).__name__) if primary is not None and primary is not restore_error else ''
            sys.stderr.write(('IME restoration failed'+label+'; state may remain inactive: '+detail)[:400]+'\n')
        except (OSError,ValueError):
            pass
    try:original=state(.5)
    except BaseException:
        record('before',status='failed')
        raise
    record('before',original,'initial_query','observed')
    restore_needed=False
    previous={}
    # Without a handler, the default SIGTERM/SIGHUP disposes the process mid-yield
    # and skips finally(), leaving the IME disabled. Raise instead so cleanup runs.
    def interrupted(signum,frame):
        raise RuntimeError(f'keyboard input interrupted by signal {signum}')
    try:
        for sig in (signal.SIGTERM,signal.SIGHUP):
            previous[sig]=signal.getsignal(sig)
            signal.signal(sig,interrupted)
    except BaseException:
        for sig,handler in previous.items():
            signal.signal(sig,handler)
        raise
    try:
        if original=='2':
            restore_needed=True
            try:switched=switch('-c','1')
            except BaseException:
                record('after_switch',status='failed')
                raise
            record('after_switch',switched,'switch_query','observed')
        else:
            record('after_switch',original,'initial_query','unchanged')
        yield
    finally:
        primary=sys.exc_info()[1]
        try:
            # Keep the handler until the IME is restored so a late signal still cleans up.
            if original=='2' and restore_needed:
                try:
                    restored=switch('-o','2')
                except BaseException as restore_error:
                    record('after_restore',status='failed')
                    warn_restore(restore_error,primary)
                    if primary is None:
                        raise
                    if isinstance(restore_error,(KeyboardInterrupt,SystemExit)) and \
                            not isinstance(primary,(KeyboardInterrupt,SystemExit)):
                        raise
                    # Otherwise the primary continues unwinding untouched.
                else:
                    record('after_restore',restored,'switch_query','observed')
            else:
                record('after_restore',original,'initial_query','not_requeried')
        finally:
            for sig,handler in previous.items():
                signal.signal(sig,handler)

def compact_result(result):
    """Only strip presentation data; immutable observations retain full geometry."""
    if not isinstance(result,dict):return result
    if result.get('backend')=='desktop':
        keys=('image','observation','id','observation_schema','image_role','created','image_size',
              'max_width','image_format','image_bytes','image_sha256','pixel_sha256','region',
              'crop','scope','window','window_bounds',
              'monitor','monitor_box','monitor_scale','monitor_transform','capture_ms',
              'decode_ms','encode_ms','capture_elapsed_ms','capture_started_wall',
              'capture_started_monotonic','capture_boot_id','capture_compositor',
              'settle_stable','settle_samples','settle_ms')
        out={k:result[k] for k in keys if k in result}
        if 'monitor_scale' in result:out['monitor_scale']=result['monitor_scale']
        if 'monitor_transform' in result:out['monitor_transform']=result['monitor_transform']
        if 'monitor_box' in result:out['monitor_box']=result['monitor_box']
        if 'region' in result and 'image_size' in result:
            iw,ih,rx,ry,rw,rh=validate_coordinate_metadata(result)
            out['scale_x']=iw/rw
            out['scale_y']=ih/rh
            # Retain the original x-ratio alias for existing consumers.
            out['scale']=out['scale_x']
        return out
    return {k:compact_result(v) if k=='after' else v for k,v in result.items()}

class Pointer:
    def __init__(self,env,monitor,binary='pointer'):
        self.p=subprocess.Popen([str(ROOT/'native'/binary),*([monitor] if monitor is not None else [])],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        try:
            if self.reply()!='ready':raise RuntimeError('pointer startup failed')
        except BaseException:
            self.close()
            raise
    def reply(self):
        if not select.select([self.p.stdout],[],[],2)[0]: raise RuntimeError('pointer timed out')
        line=self.p.stdout.readline().strip()
        if not line: raise RuntimeError('pointer disconnected')
        return line
    def command(self,s):
        self.p.stdin.write(s+'\n');self.p.stdin.flush()
        if self.reply()!='ok': raise RuntimeError('pointer action failed')
    def close(self):
        try:
            if self.p.stdin and not self.p.stdin.closed:
                try:self.p.stdin.close()
                except (BrokenPipeError,OSError):pass
            try:self.p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.p.terminate()
                try:self.p.wait(timeout=2)
                except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
        finally:
            for stream in (self.p.stdout,self.p.stderr):
                if stream and not stream.closed:stream.close()

def wait_cancelable(seconds):
    deadline=time.monotonic()+seconds
    while True:
        check_cancel()
        remaining=deadline-time.monotonic()
        if remaining<=0:return
        time.sleep(min(.01,remaining))

@contextmanager
def mouse_modifiers(env,names):
    if not names:
        yield
        return
    masks={'shift':1,'ctrl':4,'alt':8,'logo':64,'altgr':128}
    mask=0
    for name in names:mask|=masks[MODIFIERS[name.lower()]]
    keyboard=Pointer(env,None,binary='modifiers')
    try:
        check_cancel();keyboard.command(f'mods {mask}')
        yield
    finally:
        try:keyboard.command('mods 0')
        finally:keyboard.close()

class TransientRefusal(RuntimeError):
    """A desktop guard refused input; never classify arbitrary exception text."""


class PreflightRefusal(ValueError):
    """A request failed validation before focus or input could change."""


def is_transient_refusal(result):
    return (isinstance(result,dict) and result.get('ok') is False and
            result.get('error') in ('screen changed','focus changed') and
            result.get('error_code')=={'screen changed':'screen_changed',
                                      'focus changed':'focus_changed'}[result['error']] and
            'capture_error' not in result and 'ime_restore_failed' not in result)

def is_completed_capture_error(result,action_count):
    return (isinstance(result,dict) and result.get('ok') is False and
            isinstance(result.get('capture_error'),str) and
            type(result.get('completed')) is int and action_count>0 and
            result['completed']==action_count)

DESKTOP_REOBSERVE = ('List windows and observe the new focused window, or observe the screen, before '
                     'further input. The after image is not a new observe. Do not replay completed or uncertain actions.')


def _diagnostic_event(event,meta,env,*,action_index=None,action_type=None,intended=None,
                      cursor_before=None,cursor_after=None,cursor_after_release=None,
                      completed=0,error=None,active_window=None):
    token=os.environ.get('CU_SESSION_TOKEN')
    if not token:return
    target={key:meta.get(key) for key in ('id','scope','window','window_bounds','monitor',
            'monitor_box','monitor_scale','monitor_transform','region','image_size',
            'image_sha256','capture_started_monotonic','capture_boot_id','capture_compositor')}
    safe_error=None
    if error is not None:
        if isinstance(error,str):
            safe_error=('pointer_missed' if error=='pointer_missed' or 'pointer missed target' in error else
                        'post_click_pointer_moved' if error=='post_click_pointer_moved' or 'post-click pointer moved' in error else
                        'focus_changed' if 'focus changed' in error else
                        'screen_changed' if 'screen changed' in error else
                        'cancelled' if 'cancelled' in error else 'operation_failed')
        else:safe_error=type(error).__name__ if isinstance(error,BaseException) else 'operation_failed'
    record={'event':event,'wall_time':time.time(),'monotonic':time.monotonic(),
            'observation_id':meta.get('id'),'target':target,'action_index':action_index,
            'action_type':action_type,'intended_global_point':intended,
            'cursor_before_move':cursor_before,'cursor_after_move':cursor_after,
            'cursor_after_button_release':cursor_after_release,
            'active_window':active_window,'completed':completed,'error':safe_error}
    raw=(json.dumps(record,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
    if len(raw)>32768:raise RuntimeError('diagnostic record exceeds size limit')
    name='diagnostics-'+hashlib.sha256(token.encode('ascii','ignore')).hexdigest()[:16]+'.jsonl'
    fd=os.open(STATE/name,os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=os.geteuid():
            raise RuntimeError('diagnostic log is not a private regular file')
        if st.st_size+len(raw)>4*1024*1024:
            raise RuntimeError('diagnostic log reached its 4 MiB task limit')
        os.fchmod(fd,0o600)
        jsonlutil.ensure_trailing_newline_fd(fd, STATE / name)
        if os.write(fd,raw)!=len(raw):raise RuntimeError('diagnostic log write was incomplete')
    finally:os.close(fd)

def _is_navigation_candidate(actions):
    """True when a batch may navigate (C2): a click, double-click, or Enter.

    After such a batch the page is still loading 80ms later, so the
    single after-capture usually still shows the old page.
    """
    for action in actions or []:
        if not isinstance(action, dict):
            continue
        if action.get('type') in ('click', 'double_click'):
            return True
        if action.get('type') == 'key':
            keys = action.get('keys') or []
            if any(str(k).lower() in ('return', 'enter') for k in keys):
                return True
    return False


def _is_zen_ctrl_t(actions):
    """True when a batch presses Ctrl+T (C3).

    In Zen Ctrl+T opens a new window; Ctrl+N is the new tab. The check
    is key-name based (case-insensitive); the caller also verifies the
    target window is Zen before refusing, so Ctrl+T in other apps
    (for example VS Code go-to-symbol) still works.
    """
    for action in actions or []:
        if not isinstance(action, dict) or action.get('type') != 'key':
            continue
        keys = [str(k).lower() for k in (action.get('keys') or [])]
        if 'ctrl' in keys and 't' in keys:
            return True
    return False


def _refuse_zen_ctrl_t(env, address, actions, screen_scope):
    """Refuse Ctrl+T when the target window is Zen (C3).

    Raises PreflightRefusal before any focus or input. A failed window
    lookup fails open (the brief rule still bans Ctrl+T); a non-Zen
    target is untouched, so Ctrl+T keeps working in other apps.
    """
    if screen_scope or address is None or not _is_zen_ctrl_t(actions):
        return
    try:
        target_class = window(env, address).get('class', '')
    except Exception:
        target_class = ''
    if isinstance(target_class, str) and target_class.lower().startswith('zen'):
        raise PreflightRefusal('Ctrl+T opens a new window in Zen; use Ctrl+N for a new tab')


def _settle_after_capture(capture, first_after, nav_candidate, settle_ms=400):
    """Re-capture once after a navigation-candidate batch (C2).

    ``capture`` is a zero-arg callable returning an observation meta dict.
    If the batch could not navigate, the first frame stands. Otherwise
    wait ``settle_ms`` and capture again; when the frame hash changed the
    first frame was stale (old page still on screen) and the second frame
    is the after image. Returns (after_meta, recaptured_bool). A failed
    or hash-less second capture keeps the first frame.
    """
    if not nav_candidate:
        return first_after, False
    time.sleep(settle_ms / 1000.0)
    try:
        second = capture()
    except Exception:
        return first_after, False
    if not isinstance(second, dict) or second.get('pixel_sha256') is None:
        return first_after, False
    if second.get('pixel_sha256') != first_after.get('pixel_sha256'):
        return second, True
    return first_after, False


def desktop_act(env,meta,actions,after_capture=True,observation_path=None,
                expected_terminal_window=None):
    preflight_start=time.monotonic()
    try:
        if not isinstance(after_capture,bool): raise ValueError('after_capture must be boolean')
        check_cancel()
        verified_image=validate_desktop_observation(meta,env,observation_path,load_image=True)
        validate_actions(actions,'desktop')
        screen_scope=meta.get('scope')=='screen'
        if screen_scope and any(a['type'] in ('key','type') for a in actions):
            raise ValueError('screen observations support pointer actions only; use a window or accessibility target for typing')
        # Validate coordinates and payloads for the entire batch before any side effects.
        for a in actions:
            if a['type'] in ('click','double_click','move','hover','scroll'):
                image_point(meta,a['x'],a['y'])
            if a['type']=='drag':
                image_point(meta,*a['from']);image_point(meta,*a['to'])
        # Group adjacent keyboard operations into one existing wtype process.
        groups=keyboard_groups(actions)
        for group in groups:
            if isinstance(group,list):keyboard_argv(group)
            elif group.get('type')=='type':standalone_type_argv(group)
    except ValueError as exc:
        raise PreflightRefusal(str(exc)) from exc
    address=None if screen_scope else meta['window']
    # C3: in Zen Ctrl+T opens a new window (Ctrl+N is the new tab). Refuse
    # before any focus or input when the target window is Zen.
    _refuse_zen_ctrl_t(env, address, actions, screen_scope)
    transition_requested=expected_terminal_window is not None
    terminal_bounds=None
    if expected_terminal_window is None:
        terminal_address=address
    elif expected_terminal_window in ('none','unbound'):
        terminal_address=None
    elif isinstance(expected_terminal_window,str):
        terminal_address=expected_terminal_window
    elif isinstance(expected_terminal_window,dict):
        terminal_address=expected_terminal_window.get('address')
        terminal_bounds=expected_terminal_window.get('bounds')
    else:
        raise ValueError('expected_terminal_window must be an address, bounds object, or none')
    explicit_terminal_address=(expected_terminal_window is not None and
                               expected_terminal_window not in ('none','unbound') and
                               terminal_address!=address)
    if explicit_terminal_address and terminal_address is not None and not re.fullmatch(r'0x[0-9a-fA-F]+',terminal_address):
        raise ValueError('expected terminal window address is invalid')
    if terminal_bounds is not None:
        if (not isinstance(terminal_bounds,(list,tuple)) or len(terminal_bounds)!=4 or
                any(type(value) is not int for value in terminal_bounds)):
            raise ValueError('expected terminal bounds must be four integers')
    active_window=None
    terminal_guard_verified=False
    def guard(target=address):
        nonlocal active_window
        check_cancel()
        if not screen_scope and target is not None:
            c=window(env,target)
            expected_bounds=(meta['window_bounds'] if same_window_address(target,address)
                             else terminal_bounds)
            if expected_bounds is not None and bounds(c)!=expected_bounds:
                raise RuntimeError('expected window geometry changed; observe again')
        m=next((m for m in hypr(env,'monitors') if m['name']==meta['monitor']),None)
        if not m or monitor_box(m)!=meta['monitor_box'] or m['scale']!=meta['monitor_scale'] or m.get('transform',0)!=meta['monitor_transform']: raise RuntimeError('monitor layout changed; observe again')
        if not screen_scope and target is not None:
            active_window=hypr(env,'activewindow').get('address')
            if not same_window_address(active_window,target):raise TransientRefusal('focus changed')
    # OPTIONAL diagnostic probe, run before the batch touches anything. A
    # failure here loses a diagnostic, not the action: ordinary exceptions
    # degrade to focus_before:null plus a bounded warning and the REQUIRED
    # guards below run unchanged. BaseException (cancellation) still
    # propagates.
    focus_before=None;focus_probe_warning=None
    try:
        focus_before=hypr(env,'activewindow').get('address')
    except Exception as exc:
        focus_probe_warning=('focus probe failed: '+' '.join(str(exc).split()))[:400]
    # Pre-batch diagnostics: what was true before this batch could touch
    # anything. Pointer verification is cursor position only; the desktop
    # backend cannot identify the UI element receiving the event. Diagnostics
    # never mask the action error below and never imply the application
    # actually applied the action.
    diagnostics={'focus_before':focus_before,'target_window':address,
                 'target_was_focused':(same_window_address(focus_before,address)
                                       if address and focus_before is not None else None),
                 'pointer_check':'cursor position only; desktop backend cannot identify the receiving UI element'}
    if focus_probe_warning:diagnostics['focus_probe_warning']=focus_probe_warning
    if not screen_scope:focus(env,address)
    try:guard()
    except TransientRefusal as exc:
        _diagnostic_event('preflight_refused',meta,env,completed=0,error=str(exc),active_window=active_window)
        return {'ok':False,'completed':0,'error':str(exc),'error_code':'focus_changed',
                'preflight_ms':round((time.monotonic()-preflight_start)*1000,3),
                'next_step':DESKTOP_REOBSERVE}
    # Refuse coordinates from an image superseded by a visible layout change.
    new,fresh=(observe_screen(env,meta['monitor'],meta.get('crop'),meta['max_width'],persist=False) if screen_scope else
               observe(env,address,meta.get('crop'),meta['max_width'],activate=False,persist=False))
    from PIL import Image
    old=verified_image if hasattr(verified_image,'size') else Image.open(meta['image'])
    if screen_changed(old,new,actions):
        time.sleep(.15)
        settled,settled_meta=(observe_screen(env,meta['monitor'],meta.get('crop'),meta['max_width'],persist=False) if screen_scope else
                              observe(env,address,meta.get('crop'),meta['max_width'],activate=False,persist=False))
        if not screen_changed(new,settled,actions) and not _action_points_changed(old,settled,actions):
            _diagnostic_event('preflight_retry',meta,env,completed=0,error='screen changed',active_window=active_window)
            new,fresh=settled,settled_meta
        else:
            fresh=save_observation(settled,settled_meta,meta['max_width'])
            _diagnostic_event('preflight_refused',meta,env,completed=0,error='screen changed',active_window=active_window)
            return {'ok':False,'completed':0,'error':'screen changed','error_code':'screen_changed',
                    'preflight_ms':round((time.monotonic()-preflight_start)*1000,3),
                    'next_step':DESKTOP_REOBSERVE,'after':fresh}
    # A keyboard-only batch must not open the virtual pointer device at all, and an
    # ordinary startup failure belongs in the result envelope, not outside it.
    pointer=None;completed=0;error=None;ime_result={};transient_error=False;outcome_uncertain=False
    preflight_ms=round((time.monotonic()-preflight_start)*1000,3)
    def move(x,y,index,action_type):
        gx,gy=image_point(meta,x,y);mx,my,mw,mh=meta['monitor_box']
        # High resolution normalized coordinates, independent of image resize / output scale.
        before=hypr(env,'cursorpos')
        pointer.command(f'abs {round((gx-mx)/mw*1000000)} {round((gy-my)/mh*1000000)} 1000000 1000000')
        pos=hypr(env,'cursorpos')
        missed=math.hypot(pos['x']-gx,pos['y']-gy)>3
        _diagnostic_event('pointer_move',meta,env,action_index=index,action_type=action_type,
                          intended=[gx,gy],cursor_before=before,cursor_after=pos,
                          completed=completed,error='pointer_missed' if missed else None,
                          active_window=active_window)
        if missed:raise RuntimeError('pointer missed target; refusing click')
        return gx,gy
    def store_wtype_stderr(captured):
        stderr=''.join(captured)
        if stderr:
            previous=ime_result.get('wtype_stderr','')
            ime_result['wtype_stderr']=((previous+'\n' if previous else '')+stderr)[:400]
        else:ime_result.setdefault('wtype_stderr','')
    def execute_group(a,index):
        nonlocal completed,outcome_uncertain
        guard()
        if isinstance(a,list):
            exact=any(x['type']=='type' and x.get('ime','literal')=='literal' for x in a)
            if not any(x['type']=='type' and x.get('ime')=='compose' for x in a):
                exact=exact or any(x['type']=='key' and any(k in ('BackSpace','Delete','Home','End','Left','Right','Up','Down','Prior','Next') for k in key_names(x['keys'])[1]) for x in a)
            _diagnostic_event('keyboard_group_started',meta,env,action_index=index,
                              action_type='keyboard_group',completed=completed,active_window=active_window)
            capture=[]
            try:
                with literal_keyboard(env,exact,result=ime_result):
                    guard();run_cancelable(keyboard_argv(a),env,capture_stderr=capture)
                    completed+=len(a)   # input acknowledged; count it before IME restore can fail
            finally:store_wtype_stderr(capture)
            _diagnostic_event('keyboard_group_completed',meta,env,action_index=index,
                              action_type='keyboard_group',completed=completed,active_window=active_window)
            return
        typ=a['type']
        if typ in ('move','hover','click','double_click','scroll'):
            intended=move(a['x'],a['y'],index,typ)
            if typ in ('click','double_click'):
                b={'left':0,'right':1,'middle':2}[a.get('button','left')]
                presses=2 if typ=='double_click' else 1
                for press in range(presses):
                    guard();pointer.command(f'button {b} 1');outcome_uncertain=True
                    try:wait_cancelable(.025)
                    finally:pointer.command(f'button {b} 0')
                    after_release=hypr(env,'cursorpos')
                    missed=math.hypot(after_release['x']-intended[0],after_release['y']-intended[1])>3
                    _diagnostic_event('button_release',meta,env,action_index=index,action_type=typ,
                                      intended=intended,cursor_after_release=after_release,
                                      completed=completed,error='post_click_pointer_moved' if missed else None,
                                      active_window=active_window)
                    if missed:raise RuntimeError('post-click pointer moved; click outcome uncertain; stopping remaining input')
                    # 35 ms only separates the two double-click presses; after the
                    # last press it would only add latency before the action ends.
                    if press+1<presses:wait_cancelable(.035)
                outcome_uncertain=False
            elif typ=='scroll':
                wait_cancelable(.03);guard()
                pointer.command(f"scroll {a.get('dx',0)} {a.get('dy',0)}")
            elif typ=='hover':
                # G21: some buttons (file-picker Browse) only register a click
                # after the pointer has hovered off-center long enough for the
                # hover state to land (button darkens). Move, settle 30 ms for
                # pointer-enter delivery, click in a later action. No click here.
                wait_cancelable(.03)
        elif typ=='drag':
            sx,sy=a['from'];ex,ey=a['to'];move(sx,sy,index,typ);guard()
            b={'left':0,'right':1,'middle':2}[a.get('button','left')]
            pointer.command(f'button {b} 1');outcome_uncertain=True
            try:
                for i in range(1,11):
                    guard();move(sx+(ex-sx)*i/10,sy+(ey-sy)*i/10,index,typ);wait_cancelable(a.get('ms',300)/10000)
            finally:
                pointer.command(f'button {b} 0')
                after_release=hypr(env,'cursorpos')
                end_global=image_point(meta,ex,ey)
                _diagnostic_event('button_release',meta,env,action_index=index,action_type=typ,
                                  intended=[end_global[0],end_global[1]],
                                  cursor_after_release=after_release,completed=completed,
                                  active_window=active_window)
            outcome_uncertain=False
        elif typ=='type':
            _diagnostic_event('typing_started',meta,env,action_index=index,action_type=typ,
                              completed=completed,active_window=active_window)
            capture=[]
            try:
                with literal_keyboard(env,a.get('ime','literal')=='literal',result=ime_result):
                    guard();run_cancelable(standalone_type_argv(a),env,input=a['text'],capture_stderr=capture)
                    completed+=1     # same rule: never infer a count from a failed input
            finally:store_wtype_stderr(capture)
            _diagnostic_event('typing_completed',meta,env,action_index=index,action_type=typ,
                              completed=completed,active_window=active_window)
            return
        elif typ=='wait':wait_cancelable(a.get('ms',100)/1000)
        completed+=1
        _diagnostic_event('action_completed',meta,env,action_index=index,action_type=typ,
                          completed=completed,active_window=active_window)
    start=time.monotonic()
    try:
        # A new virtual device at an unchanged cursor position may not cause
        # Hyprland to deliver enter/motion to a newly mapped surface. Establish
        # real motion without clicking; the action still ends at its exact target.
        if any(a['type'] in ('move','hover','click','double_click','scroll','drag') for a in actions):
            pointer=Pointer(env,meta['monitor'])
            # Capture can outlast cancellation or a focus/layout change. The
            # preparatory motion is input too, so validate before sending it.
            guard()
            first=next(a for a in actions if a['type'] in ('move','hover','click','double_click','scroll','drag'))
            point=first['from'] if first['type']=='drag' else [first['x'],first['y']]
            gx,gy=image_point(meta,*point);mx,my,mw,mh=meta['monitor_box'];rx,ry,rw,rh=meta['region']
            nx=gx+2 if gx<rx+rw-3 else max(rx,gx-2);ny=gy
            before=hypr(env,'cursorpos')
            pointer.command(f'abs {round((nx-mx)/mw*1000000)} {round((ny-my)/mh*1000000)} 1000000 1000000')
            after=hypr(env,'cursorpos')
            _diagnostic_event('preparatory_move',meta,env,action_index=0,action_type=first['type'],
                              intended=[nx,ny],cursor_before=before,cursor_after=after,
                              completed=completed,active_window=active_window)
        for index,a in enumerate(groups):
            guard()
            with mouse_modifiers(env,a.get('modifiers',[]) if isinstance(a,dict) else []):
                execute_group(a,index)
            final_group=index==len(groups)-1
            if final_group and terminal_address is not None and not same_window_address(terminal_address,address):
                # The expected terminal transition (e.g. Save closes the dialog
                # and focus moves to the editor) settles asynchronously; the
                # dialog may still hold focus right after the click. Poll for
                # the terminal window to gain focus, same 1.5s bound as
                # focus(), instead of refusing on the first sample. Only a
                # focus refusal retries; geometry/layout errors still fail fast.
                deadline=time.monotonic()+1.5
                while True:
                    try:
                        guard(terminal_address)
                        break
                    except TransientRefusal:
                        remaining=deadline-time.monotonic()
                        if remaining<=0:
                            raise
                        wait_cancelable(min(.04,remaining))
                terminal_guard_verified=True
            elif final_group and terminal_address is None:
                guard(None)
                terminal_guard_verified=True
            else:
                guard()
    except Exception as exc:
        error=str(exc);transient_error=isinstance(exc,TransientRefusal)
        _diagnostic_event('operation_stopped',meta,env,completed=completed,error=error,
                          active_window=active_window)
    finally:
        # Teardown failure must not discard the count or escape as an exception.
        if pointer:
            try:pointer.close()
            except Exception as exc:
                error=error or 'pointer cleanup failed: '+str(exc)
                transient_error=False
    execution_ms=round((time.monotonic()-start)*1000,3)
    def transition_outcome():
        if not transition_requested or screen_scope:
            return None
        def present(target):
            if target is None:
                return False
            try:
                window(env,target)
                return True
            except ValueError as exc:
                if str(exc)=='window no longer exists':
                    return False
                raise
        try:
            old_gone=not present(address)
            successor_bound=present(terminal_address)
        except Exception as exc:
            old_gone=None
            successor_bound=False
            evidence_error=(' '.join(str(exc).split()))[:400]
        else:
            evidence_error=None
        expected_terminal=('not-yet-bound' if expected_terminal_window=='unbound' else
                           terminal_address or 'none')
        record={'expected':{'old_surface':address,
                            'terminal_window':expected_terminal},
                'old_surface_gone':old_gone,
                'successor':(terminal_address if successor_bound else
                             'not-yet-bound' if terminal_address or expected_terminal_window=='unbound' else None),
                'successor_bound':successor_bound,
                'successor_verified':bool(terminal_guard_verified and successor_bound)}
        if evidence_error:
            record['evidence_error']=evidence_error
        return record

    if not after_capture and error is None:
        result={'ok':True,'completed':completed,'preflight_ms':preflight_ms,
                'execution_ms':execution_ms,'after_skipped':True,
                'input_diagnostics':diagnostics}
        transition=transition_outcome()
        if transition is not None:result['transition']=transition
        result.update(ime_result)
        _diagnostic_event('operation_completed',meta,env,completed=completed,
                          active_window=active_window)
        return result
    time.sleep(.08)
    result={'ok':error is None,'completed':completed,'preflight_ms':preflight_ms,
            'execution_ms':execution_ms,'input_diagnostics':diagnostics}
    result.update(ime_result)
    if transient_error:result['error_code']='focus_changed'
    if error: result['error']=error
    if outcome_uncertain:result['outcome_uncertain']=True
    if terminal_address is None and not screen_scope:
        result['after_skipped']=True
        result['after_skip_reason']='no expected terminal window to capture'
    else:
        try:
            after_capture_start=time.monotonic()
            def _after_capture():
                return (observe_screen(env,meta['monitor'],meta.get('crop'),meta['max_width']) if screen_scope else
                        observe(env,terminal_address,meta.get('crop'),meta['max_width'],activate=False))
            first_after = _after_capture()
            # C2: 80ms after a navigation click the old page is still on
            # screen. Settle once and keep the newer frame when it changed.
            result['after'], recaptured = _settle_after_capture(
                _after_capture, first_after, _is_navigation_candidate(actions))
            result['after_recaptured'] = recaptured
            result['frame_bytes_changed']=result['after']['pixel_sha256']!=meta['pixel_sha256']
            result['changed']=result['frame_bytes_changed']  # Compatibility alias, not semantic success.
            result['change_meaning']='Exact captured pixel hash differs; animations count. Does not confirm app action succeeded.'
            result['after_capture_ms']=round((time.monotonic()-after_capture_start)*1000,3)
        except Exception as exc:
            result['ok']=False;result['capture_error']=str(exc)
            result.setdefault('error','final capture failed: '+str(exc))
    transition=transition_outcome()
    if transition is not None:result['transition']=transition
    if is_transient_refusal(result):result['next_step']=DESKTOP_REOBSERVE
    _diagnostic_event('operation_completed',meta,env,completed=completed,
                      error=error if error else None,active_window=active_window)
    return result

def browser_timeout(request):
    # Keep setup/snapshot allowance; each guard can take 5s, and the final
    # assert evaluation can overrun its polling budget by another 5s.
    # Cap adapter execution instead of accumulating unbounded per-action allowance.
    budget=sum(5000+(max(0,min(a.get('timeout_ms',1000),3000))+5000 if a['type']=='assert' else
                     a.get('ms',100) if a['type']=='wait' else 0) for a in request.get('actions',[]))
    return min(60,35+budget/1000)

def browser(request):
    out=run_cancelable(['node',str(ROOT/'scripts/cdp.mjs')],input=json.dumps(request),timeout=browser_timeout(request))
    if out.strip(): return json.loads(out)
    raise RuntimeError('CDP adapter failed')

def browser_automation_call(env, operation, method='DOM/BiDi'):
    import overlay
    with overlay.hold('Browser automation', method, env=env):
        return operation()

def browser_start(env,endpoint):
    import urllib.request
    import urllib.parse
    url=urllib.parse.urlparse(endpoint)
    if url.scheme!='http' or url.hostname not in ('localhost','127.0.0.1','::1'):raise ValueError('loopback http endpoint required')
    try:port=url.port or 9222
    except ValueError:raise ValueError('endpoint port is not a number') from None
    if not 1<=port<=65535:raise ValueError('endpoint port must be 1..65535')
    try:
        import warm_browser
    except ImportError:
        return _browser_start_cold(env,endpoint,url,port)
    try:
        json.load(urllib.request.urlopen(urllib.parse.urljoin(endpoint,'/json/version'),timeout=1))
        alive=True
    except Exception:
        alive=False
    if alive:
        # A live endpoint: reuse it, but only our own warm browser gets
        # a fresh context. ensure_warm() reports a pid only when the
        # recorded process is verified ours; anything else (someone
        # else's browser, a test stub) is reused exactly as before.
        warm=warm_browser.ensure_warm(endpoint=endpoint,state_dir=STATE,env=env)
        if warm.get('pid') is None:
            return {'ok':True,'endpoint':endpoint,'reused':True}
        profile=warm_browser.status(endpoint=endpoint,state_dir=STATE).get('recorded_profile')
        return _browser_start_warm_context(
            warm_browser,endpoint,env,warm.get('pid'),profile,True,
            {'ok':True,'endpoint':endpoint,'reused':True})
    # No live endpoint: cold-launch through the hardened legacy path
    # (profile inode checks, private log, cancel reaping), then record
    # the process we just launched with the warm module so later starts
    # reuse it, new contexts land in it, and stop() can terminate it.
    cold=_browser_start_cold(env,endpoint,url,port,probe_alive=False)
    try:
        warm_browser.register(endpoint,cold['pid'],cold['profile'],state_dir=STATE)
        return _browser_start_warm_context(
            warm_browser,endpoint,env,cold['pid'],cold['profile'],False,cold)
    except Exception:
        # The warm enhancement failed after a successful cold launch
        # (e.g. CDP broke after /json/version answered): hand back the
        # working browser exactly as before the adoption, never fail a
        # start the old code would have returned.
        return cold

def _browser_start_warm_context(warm_browser,endpoint,env,pid,profile,reused,fallback):
    """Fresh isolated context for this start in our warm browser.

    On failure returns `fallback`, the pre-adoption result for this
    branch, instead of failing the start: the caller still has a
    working browser, exactly as before.
    """
    try:
        _close_prior_browser_start_contexts(warm_browser,endpoint)
        task_id='browser-start-'+uuid.uuid4().hex[:12]
        ctx=warm_browser.new_task_context(task_id,endpoint=endpoint,state_dir=STATE,env=env)
        return {'ok':True,'endpoint':endpoint,'reused':bool(reused),
                'warm':True,'pid':pid,'profile':str(profile) if profile else None,
                'task_id':task_id,'target_id':ctx.get('target_id'),
                'browser_context_id':ctx.get('browser_context_id'),
                'context_ms':ctx.get('context_ms'),'ensure_ms':ctx.get('ensure_ms'),
                'total_ms':ctx.get('total_ms')}
    except Exception:
        return fallback

def _close_prior_browser_start_contexts(warm_browser,endpoint):
    """Best-effort close of task contexts from earlier browser_start calls.

    Each start creates a fresh context; the previous start's context is
    dead to the caller, so close it instead of leaking a tab per start.
    Only contexts this function created (task ids starting with
    'browser-start-') are touched. Failures are ignored: a stale record
    must never fail a start.
    """
    try:
        current=warm_browser.status(endpoint=endpoint,state_dir=STATE)
    except Exception:
        return
    for record in current.get('contexts',[]) or []:
        task_id=record.get('task_id') if isinstance(record,dict) else None
        if isinstance(task_id,str) and task_id.startswith('browser-start-'):
            try:
                warm_browser.close_task_context(task_id=task_id,endpoint=endpoint,state_dir=STATE)
            except Exception:
                pass

def _browser_start_cold(env,endpoint,url,port,probe_alive=True):
    """Legacy cold launch: the hardened spawn path.

    Used when scripts/warm_browser.py is missing, and as the spawn step
    of the warm adoption when no browser answers. Kept verbatim so a
    checkout without the warm module still starts a browser exactly as
    before. probe_alive=False skips the reuse probe when the caller
    already probed (one probe per start, never two).
    """
    import urllib.request
    import urllib.parse
    if probe_alive:
        try:
            json.load(urllib.request.urlopen(urllib.parse.urljoin(endpoint,'/json/version'),timeout=1))
            return {'ok':True,'endpoint':endpoint,'reused':True}
        except Exception:pass
    prepare_state();profile=ROOT/'browser-profile';profile.mkdir(mode=0o700,exist_ok=True)
    # Harden the directory's own inode before trusting it: a symlink, a file or
    # a foreign owner refuses here, never at spawn time. Reuse never reaches this.
    try:
        dir_fd=os.open(profile,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    except OSError as exc:
        try:
            is_link=os.path.islink(profile)
        except OSError:
            raise exc
        if is_link:
            raise RuntimeError('browser profile must not be a symlink') from exc
        raise
    try:
        if os.fstat(dir_fd).st_uid!=os.geteuid():
            raise RuntimeError('browser profile is not owned by the current user')
        os.fchmod(dir_fd,0o700)
    finally:
        try:os.close(dir_fd)
        except OSError:pass
    log_path=STATE/'browser.log'
    # Create private in one step; a separate chmod would leave a window.
    fd=os.open(log_path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    try:
        os.fchmod(fd,0o600)      # O_CREAT's mode applies only to a new file
        log=os.fdopen(fd,'ab')
        try:
            p=subprocess.Popen(['chromium',f'--user-data-dir={profile}',f'--remote-debugging-port={port}',
                f'--remote-debugging-address={url.hostname if url.hostname!="localhost" else "127.0.0.1"}','--no-first-run','--no-default-browser-check','about:blank'],
                env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        finally:
            log.close()
    except BaseException:
        try:os.close(fd)
        except OSError:pass
        raise
    try:
        for _ in range(50):
            check_cancel()
            try:
                json.load(urllib.request.urlopen(urllib.parse.urljoin(endpoint,'/json/version'),timeout=.3))
                return {'ok':True,'endpoint':endpoint,'reused':False,'pid':p.pid,'profile':str(profile)}
            except Exception:time.sleep(.1)
        raise RuntimeError('managed browser did not expose CDP; see '+str(log_path))
    except BaseException:
        # Only the process this call started is ours; an existing endpoint is not.
        try:
            p.terminate();p.wait(timeout=3)
        except BaseException:
            try:p.kill();p.wait(timeout=3)
            except BaseException:pass
        raise

def locked():
    prepare_state()
    f=open(STATE/'desktop.lock','a')
    try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise RuntimeError('another computer-use operation is active')
    return f

def settled_observation(capture,settle_ms,max_width):
    """Bounded visual stability wait, not a claim of semantic UI readiness."""
    if not isinstance(settle_ms,int) or not 0<=settle_ms<=2000:
        raise ValueError('settle-ms must be 0..2000')
    start=time.monotonic();deadline=start+settle_ms/1000
    previous=None;stable_since=None;samples=0
    while True:
        check_cancel()
        image,meta=capture();samples+=1
        fingerprint=(image.size,meta.get('region'),hashlib.sha256(image.tobytes()).digest())
        now=time.monotonic()
        if fingerprint!=previous:stable_since=now
        stable=previous==fingerprint and now-stable_since>=.12
        if stable or now>=deadline:
            meta.update(settle_stable=stable,settle_samples=samples,
                        settle_ms=round((now-start)*1000))
            return save_observation(image,meta,max_width)
        previous=fingerprint
        wait_cancelable(min(.06,max(0,deadline-now)))

def load_cli_registry():
    path=ROOT/'skill'/'cli-anything'/'registry.json'
    try:data=json.loads(path.read_text())
    except FileNotFoundError:raise RuntimeError('registry snapshot not found: '+str(path))
    except json.JSONDecodeError as exc:raise RuntimeError('registry snapshot is not valid JSON: '+str(exc))
    if isinstance(data,dict) and isinstance(data.get('clis'),list):entries=data['clis']
    elif isinstance(data,dict) and data and all(isinstance(value,dict) for value in data.values()):entries=data.values()
    else:raise RuntimeError('registry snapshot has an unexpected shape: '+str(path))
    registry={}
    for entry in entries:
        name=entry.get('name') if isinstance(entry,dict) else None
        if not name:raise RuntimeError('registry entry without a name: '+repr(entry))
        for key in ('entry_point','install_cmd','requires','skill_md'):
            if key not in entry:raise RuntimeError('registry entry %r is missing %r'%(name,key))
        registry[name]=entry
    return registry

def cli_skill_description(name):
    path=ROOT/'skill'/'cli-anything'/(name+'.md')
    try:lines=path.read_text().splitlines()
    except OSError:return ''
    for index,line in enumerate(lines):
        key,separator,value=line.partition(':')
        if key!='description' or not separator:continue
        value=value.strip()
        if value.startswith(('>','|')):
            parts=[]
            for part in lines[index+1:]:
                if not part or not part[0].isspace():break
                parts.append(part.strip())
            return ' '.join(parts)
        return value.strip('"\'')
    return ''

def cli_app_record(name,entry):
    skill_path=ROOT/'skill'/'cli-anything'/(name+'.md')
    record={'name':name,'display_name':entry.get('display_name',name),
            'category':entry.get('category',''),'entry':entry['entry_point'],
            'skill_path':str(skill_path),'skill_vendored':skill_path.is_file(),
            'requires':entry['requires']}
    description=entry.get('description') or cli_skill_description(name)
    if description:record['description']=description
    return record

def cli_run_chromium(command_args):
    """Run the repo-owned Chromium wrapper (scripts/chromium_cli.py).

    Chromium has no upstream CLI-Anything harness binary, so it does not
    go through scripts/cli-anything.py: the wrapper is a repo script run
    with the current interpreter, argv only, same 75 s outer timeout as
    the harness path. The envelope keeps the harness shape (app, args,
    returncode, stdout/stderr truncated) and adds the wrapper's parsed
    JSON output as `result`.
    """
    envelope={'app':'chromium','args':list(command_args),'returncode':None,
              'stdout_truncated':'','stderr_truncated':''}
    script=ROOT/'scripts'/'chromium_cli.py'
    try:
        def run():
            return subprocess.run([sys.executable,str(script),*command_args],
                                  capture_output=True,text=True,timeout=75)
        if command_args and command_args[0] in {
                'tabs', 'open', 'activate', 'close', 'current', 'status'}:
            result=browser_automation_call(None, run, 'CDP CLI')
        else:
            result=run()
    except subprocess.TimeoutExpired:
        envelope.update(timeout=True,error='chromium wrapper timed out')
        return {'ok':False,**envelope}
    except OSError as exc:
        envelope['error']='failed to run chromium wrapper: '+str(exc)
        return {'ok':False,**envelope}
    envelope['returncode']=result.returncode
    envelope['stdout_truncated']=result.stdout[:4096]
    envelope['stderr_truncated']=result.stderr[:4096]
    try:parsed=json.loads(result.stdout)
    except json.JSONDecodeError:
        envelope['error']='chromium wrapper returned invalid JSON'
        return {'ok':False,**envelope}
    if not isinstance(parsed,dict):
        envelope['error']='chromium wrapper returned an unexpected result'
        return {'ok':False,**envelope}
    envelope['result']=parsed
    envelope['ok']=result.returncode==0 and parsed.get('ok') is True
    return envelope

def cli_run_vscode(command_args):
    """Run the repo-owned VS Code wrapper (scripts/vscode_cli.py).

    VS Code has no upstream CLI-Anything harness binary, so it does not
    go through scripts/cli-anything.py: the wrapper is a repo script run
    with the current interpreter, argv only, same 75 s outer timeout as
    the harness path. The envelope keeps the harness shape (app, args,
    returncode, stdout/stderr truncated) and adds the wrapper's parsed
    JSON output as `result`.
    """
    envelope={'app':'vscode','args':list(command_args),'returncode':None,
              'stdout_truncated':'','stderr_truncated':''}
    script=ROOT/'scripts'/'vscode_cli.py'
    try:
        result=subprocess.run([sys.executable,str(script),*command_args],
                              capture_output=True,text=True,timeout=75)
    except subprocess.TimeoutExpired:
        envelope.update(timeout=True,error='vscode wrapper timed out')
        return {'ok':False,**envelope}
    except OSError as exc:
        envelope['error']='failed to run vscode wrapper: '+str(exc)
        return {'ok':False,**envelope}
    envelope['returncode']=result.returncode
    envelope['stdout_truncated']=result.stdout[:4096]
    envelope['stderr_truncated']=result.stderr[:4096]
    try:parsed=json.loads(result.stdout)
    except json.JSONDecodeError:
        envelope['error']='vscode wrapper returned invalid JSON'
        return {'ok':False,**envelope}
    if not isinstance(parsed,dict):
        envelope['error']='vscode wrapper returned an unexpected result'
        return {'ok':False,**envelope}
    envelope['result']=parsed
    envelope['ok']=result.returncode==0 and parsed.get('ok') is True
    return envelope

def cli_run(app,command_args):
    if app=='chromium':
        return cli_run_chromium(command_args)
    if app=='vscode':
        return cli_run_vscode(command_args)
    envelope={'app':app,'args':list(command_args),'returncode':None,
              'stdout_truncated':'','stderr_truncated':''}
    runner=ROOT/'scripts'/'cli-anything.py'
    try:
        # The runner probes --json for up to 10s, then enforces its 60s command timeout.
        result=subprocess.run([sys.executable,str(runner),'run',app,'--',*command_args],
                              capture_output=True,text=True,timeout=75)
    except subprocess.TimeoutExpired:
        envelope.update(timeout=True,error='cli-anything runner timed out')
        return {'ok':False,**envelope}
    except OSError as exc:
        envelope['error']='failed to run cli-anything runner: '+str(exc)
        return {'ok':False,**envelope}
    try:envelope=json.loads(result.stdout)
    except json.JSONDecodeError:
        envelope.update(returncode=result.returncode,
                        stdout_truncated=result.stdout[:4096],
                        stderr_truncated=result.stderr[:4096],
                        error='cli-anything runner returned invalid JSON')
        return {'ok':False,**envelope}
    if not isinstance(envelope,dict):
        envelope={'app':app,'args':list(command_args),'returncode':result.returncode,
                  'stdout_truncated':'','stderr_truncated':'',
                  'error':'cli-anything runner returned an unexpected result'}
        return {'ok':False,**envelope}
    envelope['ok']=envelope.get('returncode')==0 and 'error' not in envelope
    return envelope

class CodeExecBackend:
    """Adapter from the code-exec allowlisted API to the brokered primitives.

    Every call goes through the same code paths desktop_act and observe
    already use, so pointer-miss, screen-changed, cancellation, and the
    brokered wtype keyboard path all still apply. Observation recording
    mirrors the observe/act branches in main().
    """

    def __init__(self, env):
        self.env = env
        self.browser_endpoint = BROWSER_ENDPOINT

    def windows(self):
        keys = ('address', 'class', 'title', 'at', 'size', 'workspace')
        return [{k: c.get(k) for k in keys} for c in hypr(self.env, 'clients')]

    def observe_window(self, address, crop, max_width, low_res=False):
        import session_policy
        meta = observe(self.env, address, crop, max_width, low_res=low_res)
        session_policy.record_observation(STATE, os.environ.get('CU_SESSION_TOKEN'), meta)
        return meta

    def observe_screen(self, monitor, crop, max_width, low_res=False):
        import session_policy
        meta = observe_screen(self.env, monitor, crop, max_width, low_res=low_res)
        session_policy.record_observation(STATE, os.environ.get('CU_SESSION_TOKEN'), meta)
        return meta

    def act(self, meta, actions, observation_path):
        import session_policy
        result = desktop_act(self.env, meta, actions, observation_path=observation_path)
        if is_transient_refusal(result):
            session_policy.record_refusal(STATE, os.environ.get('CU_SESSION_TOKEN'))
        elif result.get('ok') is True or is_completed_capture_error(result, len(actions)):
            session_policy.complete_requirement(STATE, os.environ.get('CU_SESSION_TOKEN'))
        return result

    def dom_start(self):
        global BROWSER_ENDPOINT
        endpoint = BROWSER_ENDPOINT
        result = browser_automation_call(
            self.env, lambda: browser_start(self.env, endpoint))
        if isinstance(result, dict) and result.get('ok') is True:
            BROWSER_ENDPOINT = endpoint
            self.browser_endpoint = endpoint
        return result

    def dom_tabs(self):
        return browser_automation_call(
            self.env, lambda: browser({'operation': 'tabs',
                                       'endpoint': self.browser_endpoint}))

    def dom_observe(self, target, scope, max_elements):
        request = {
            'operation': 'observe', 'endpoint': self.browser_endpoint,
            'target': target, 'max_elements': max_elements,
        }
        if scope is not None:
            request['scope'] = scope
        return browser_automation_call(self.env, lambda: browser(request))

    def dom_act(self, target, snapshot, actions, after_scope=None, no_after=False):
        import session_policy
        session_policy.require_observation(
            STATE, os.environ.get('CU_SESSION_TOKEN'))
        request = {
            'operation': 'act', 'endpoint': self.browser_endpoint,
            'target': target, 'snapshot': snapshot, 'actions': actions,
        }
        if after_scope is not None:
            request['after_scope'] = after_scope
        if no_after:
            request['no_after'] = True
        result = browser_automation_call(self.env, lambda: browser(request))
        if isinstance(result, dict) and result.get('ok') is True:
            session_policy.complete_requirement(
                STATE, os.environ.get('CU_SESSION_TOKEN'))
        return result


def read_code_exec_program(source):
    """Read a code-exec program from '-' (stdin) or a private file path."""
    import code_exec as _code_exec
    if source == '-':
        raw = sys.stdin.read(_code_exec.MAX_PROGRAM_CHARS + 1)
        if len(raw) > _code_exec.MAX_PROGRAM_CHARS:
            raise ValueError('program exceeds %d chars' % _code_exec.MAX_PROGRAM_CHARS)
        return raw
    path = Path(source)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd, 'rb') as stream:
            st = os.fstat(stream.fileno())
            if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or
                    stat.S_IMODE(st.st_mode) != 0o600 or
                    st.st_size > _code_exec.MAX_PROGRAM_CHARS):
                raise ValueError('program file must be a private regular file under %d chars'
                                 % _code_exec.MAX_PROGRAM_CHARS)
            return stream.read().decode('utf-8')
    except OSError as exc:
        raise ValueError('program file is unavailable: ' + str(exc)) from exc


def cli_command(args):
    registry=load_cli_registry()
    if args.cli_operation=='list':
        return {'ok':True,'apps':[cli_app_record(name,registry[name]) for name in sorted(registry)]}
    if args.cli_operation=='search':
        query=args.text.strip().casefold()
        if not query:return {'ok':False,'error':'search text must not be empty'}
        apps=[]
        for name in sorted(registry):
            record=cli_app_record(name,registry[name])
            searchable=(record.get(key,'') for key in ('name','display_name','description','category'))
            if any(query in str(value).casefold() for value in searchable):apps.append(record)
        return {'ok':True,'apps':apps}
    if args.cli_operation=='info':
        entry=registry.get(args.app)
        if entry is None:return {'ok':False,'error':'unknown app: '+args.app}
        skill_path=ROOT/'skill'/'cli-anything'/(args.app+'.md')
        if entry.get('repo_owned'):
            install='ships in this repo: '+entry['entry_point']
        else:
            install='pip install '+entry['entry_point']
        return {'ok':True,'app':args.app,
                'skill_path':str(skill_path),'skill_vendored':skill_path.is_file(),
                'install':install,
                'install_upstream':entry['install_cmd'],
                'requires':entry['requires']}
    return cli_run(args.app,args.command_args)

def capability_matrix():
    """I9: read-only per-lane capability reporting for doctor.

    Reports which control lanes are usable on this install and
    what each lane offers. No lane is exercised; availability is
    presence of the entry point plus its hard dependency. The
    unified lane interface stays pilot-first (I9 split)."""
    scripts=ROOT/'scripts'
    def lane(entry,dep_ok,operations):
        return {'available':bool(entry and dep_ok),
                'entry':str(entry) if entry else None,
                'operations':operations}
    a11y_py=scripts/'a11y.py'
    try:
        import gi as _gi  # noqa: F401
        gi_ok=True
    except Exception:
        gi_ok=False
    return {
        'a11y':lane(a11y_py if a11y_py.is_file() else None,gi_ok,
                    ['apps','observe','ground','act','drill','query']),
        'cdp':lane(scripts/'cdp.mjs' if (scripts/'cdp.mjs').is_file() else None,
                   shutil.which('node') is not None,
                   ['observe','act','harvest']),
        'zen_rdp':lane(scripts/'zen-rdp'/'rdp_client.py'
                       if (scripts/'zen-rdp'/'rdp_client.py').is_file() else None,
                       True,
                       ['tabs','eval','peval','navigate','probe']),
        'vision':lane(shutil.which('grim'),True,['screenshot']),
        'pointer':lane(ROOT/'native'/'pointer'
                       if (ROOT/'native'/'pointer').is_file() and os.access(ROOT/'native'/'pointer',os.X_OK) else None,
                       True,['click','move','scroll']),
        'keyboard':lane(ROOT/'native'/'wtype'
                        if (ROOT/'native'/'wtype').is_file() and os.access(ROOT/'native'/'wtype',os.X_OK) else None,
                        True,['type','key']),
        'keybind':lane(shutil.which('hyprctl'),True,
                       ['binds','dispatch','clients','monitors']),
    }

def main():
    global BROWSER_ENDPOINT
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    session=sub.add_parser('session');session.add_argument('--replace',action='store_true',help='stop and restore the old session before starting');session.add_argument('driver',nargs=argparse.REMAINDER)
    sub.add_parser('session-driver',help='interactive JSON-lines driver for one whole agent task')
    sub.add_parser('stop',help='stop the current session and wait for desktop restoration');sub.add_parser('finish');sub.add_parser('recover');sub.add_parser('cancel')
    sub.add_parser('doctor');sub.add_parser('resume');sub.add_parser('status')
    win=sub.add_parser('windows');win.add_argument('--class',dest='class_',help='exact class match only; no regex, no substring')
    win.add_argument('--no-titles',action='store_true',help='omit the title key from each window')
    obs=sub.add_parser('observe');target=obs.add_mutually_exclusive_group(required=True);target.add_argument('--window');target.add_argument('--screen');obs.add_argument('--crop',nargs=4,type=int);obs.add_argument('--max-width',type=int,default=960)
    obs.add_argument('--low-res',action='store_true',help='routine framing observe at 640 px wide; verify observes and small-target grounding stay at full resolution')
    obs.add_argument('--focus',action='store_true',help='explicitly focus the target window before capture (may switch workspace)')
    obs.add_argument('--settle-ms',type=int,default=0,help='wait up to 2000 ms for 120 ms of unchanged crop pixels; not semantic readiness')
    act=sub.add_parser('act',help='execute one batch of known actions, then capture its final result');act.add_argument('--observation',required=True);act.add_argument('--actions',required=True,help='JSON path or - for stdin; batch up to 32 predictable actions from one inspected observation')
    act.add_argument('--no-after',action='store_true',help='skip successful final capture; preflight safety and error captures stay enabled')
    act.add_argument('--expected-terminal-window',default='same',help='final guard/capture target: same, none, unbound, or an exact Hyprland address')
    act.add_argument('--expected-terminal-bounds',nargs=4,type=int,help='optional expected x y width height for the terminal window')
    an=sub.add_parser('act-now',help='overlay on + session attempt with deadline + direct Pointer fallback; first visible action fast');an.add_argument('--actions',required=True,help='JSON path; same batch format as act');an.add_argument('--observation',default=None,help='fresh observation JSON path; captured when omitted');an.add_argument('--screen',default='eDP-2',help='monitor for a fresh capture');an.add_argument('--agent',default='Muse');an.add_argument('--method',default='act-now');an.add_argument('--label',default=None);an.add_argument('--session-deadline-s',type=float,default=20,help='hard deadline for the session attempt')
    obs.add_argument('--verbose',action='store_true');act.add_argument('--verbose',action='store_true')
    b=sub.add_parser('browser');b.add_argument('operation',choices=['start','tabs','observe','act']);b.add_argument('--endpoint',default=None);b.add_argument('--target');b.add_argument('--snapshot');b.add_argument('--actions');b.add_argument('--image',action='store_true')
    b.add_argument('--no-after',action='store_true',help='skip the successful after-snapshot; the final action must be a meaningful assert')
    b.add_argument('--max-elements',type=int,default=80,help='DOM output budget, 1..80 (default 80)')
    b.add_argument('--scope',help='observe only: one CSS selector to enumerate; one read, not sticky, not an input boundary')
    b.add_argument('--after-scope',help='act only: scope the successful after-snapshot to one CSS selector; not sticky, not an input boundary')
    a=sub.add_parser('a11y');a.add_argument('operation',choices=['apps','observe','drill','act','query','ground']);a.add_argument('ref',nargs='?');a.add_argument('--pid',type=int);a.add_argument('--snapshot');a.add_argument('--actions');a.add_argument('--skeleton',action='store_true')
    a.add_argument('--name',help='query only: case-insensitive name substring')
    a.add_argument('--role',help='query only: case-insensitive role substring')
    a.add_argument('--limit',type=int,default=20,help='query only: max items returned, 1..20')
    a.add_argument('--address',help='ground only: Hyprland window address the snapshot belongs to')
    ce=sub.add_parser('code-exec',help='run one allowlisted program as the action (Pick 1, opt-in flag CU_CODE_EXEC=1)')
    ce.add_argument('--program',required=True,help='program source file (mode 600) or - for stdin')
    ce.add_argument('--intent',default=None,help='one-line intent, at most 200 chars')
    ce.add_argument('--target',default=None,help='task target path under /tmp, recorded only')
    ce.add_argument('--wall-seconds',type=int,default=30,help='program wall-clock budget, 1..60')
    cli=sub.add_parser('cli',help='list and run vendored CLI-Anything harnesses')
    cli_sub=cli.add_subparsers(dest='cli_operation',required=True)
    cli_sub.add_parser('list',help='list apps from the vendored registry')
    search=cli_sub.add_parser('search',help='search app names, descriptions, and categories');search.add_argument('text')
    info=cli_sub.add_parser('info',help='show install and skill details');info.add_argument('app')
    cli_run_parser=cli_sub.add_parser('run',help='run one allowlisted harness command');cli_run_parser.add_argument('app');cli_run_parser.add_argument('command_args',nargs=argparse.REMAINDER,help='harness arguments after --')
    args=parser.parse_args()
    if args.command=='browser' and args.scope is not None:
        if args.operation!='observe':raise ValueError('--scope is only valid for browser observe')
        if not args.scope.strip():raise ValueError('--scope must be a non-empty CSS selector')
        if len(args.scope.encode('utf-16-le','surrogatepass'))>2048:raise ValueError('--scope must be at most 1024 UTF-16 code units')
    if args.command=='browser' and args.after_scope is not None:
        if args.operation!='act':raise ValueError('--after-scope is only valid for browser act')
        if not args.after_scope.strip():raise ValueError('--after-scope must be a non-empty CSS selector')
        if len(args.after_scope.encode('utf-16-le','surrogatepass'))>2048:raise ValueError('--after-scope must be at most 1024 UTF-16 code units')
        if args.no_after:raise ValueError('--after-scope cannot combine with --no-after')
    if args.command=='browser' and args.image and args.operation not in ('observe','act'):
        raise ValueError('--image is only valid for browser observe or act')
    if args.command=='observe' and args.focus and not args.window:parser.error('--focus requires --window')
    if args.command=='cli':
        try:result=cli_command(args)
        except Exception as exc:result={'ok':False,'error':str(exc)}
        print(json.dumps(result,ensure_ascii=False,separators=(',',':')),flush=True)
        return 0 if result.get('ok') is not False else 1
    if args.command=='session-driver':
        require_session()
        import session_driver
        return session_driver.relay(sys.stdin,sys.stdout)
    # Local state commands and CDP requests do not use a compositor environment.
    # Doctor acquires its own environment inside its diagnostic branch so an
    # environment failure degrades instead of escaping before the branch.
    env=(environment() if args.command in ('session','stop','recover','windows','observe','act','a11y') or
         (args.command=='code-exec' and os.environ.get('CU_CODE_EXEC','').strip().lower() in ('1','true','yes')) or
         (args.command=='browser' and args.operation=='start') else None)
    if args.command in ('session','stop','finish','recover','cancel'):
        import cursor_session
        if args.command=='stop':return cursor_session.stop(env)
        if args.command=='session':
            if os.environ.get('CU_SESSION_TOKEN'):raise RuntimeError('nested automation session refused; replace from a separate shell')
            if args.replace and cursor_session.stop(env):return 1
            return cursor_session.supervise(env,args.driver)
        if args.command=='recover':return cursor_session.recover(env)
        if args.command=='cancel':
            prepare_state()
            cancel_hotkey_module().latch(CANCEL,'cli')
        cursor_session.request_stop()
        result={'ok':True}
    elif args.command=='code-exec':
        # Pick 1, opt-in flag default OFF. A program-level failure (assert,
        # sandbox refusal, backend refusal) is a result envelope, not a
        # session-ending error: print it and return 0 so the supervisor can
        # replan. Only cancellation or an infrastructure exception escapes
        # and stops the session, as with every other command.
        import code_exec
        if not code_exec.is_enabled():
            print(json.dumps({'ok':False,'error':'code execution is disabled; set CU_CODE_EXEC=1',
                              'error_type':'disabled'},ensure_ascii=False),flush=True)
            return 0
        if args.intent is not None and (not isinstance(args.intent,str) or len(args.intent)>200):
            raise ValueError('--intent must be at most 200 chars')
        if args.target is not None:
            target=Path(args.target)
            if not target.is_absolute() or Path('/tmp') not in target.resolve().parents and target.resolve()!=Path('/tmp'):
                raise ValueError('--target must be a path under /tmp')
        require_session()
        check_cancel()
        program=read_code_exec_program(args.program)
        with locked():
            result=code_exec.run_program(
                program, CodeExecBackend(env), state_dir=STATE,
                session_token=os.environ.get('CU_SESSION_TOKEN'),
                intent=args.intent, check_cancel=check_cancel,
                wall_seconds=args.wall_seconds)
        if args.target is not None:
            result['target']=args.target
        print(json.dumps(result,ensure_ascii=False,separators=(',',':')),flush=True)
        return 0
    elif args.command=='resume':
        CANCEL.unlink(missing_ok=True)
        result={'ok':True,'cancelled':False}
    elif args.command=='status':
        latch_state=cancel_hotkey_module().cancellation_status(CANCEL)
        result={'ok':True,'cancelled':latch_state['cancelled']}
        if latch_state['cancelled']:result['cancellation']=latch_state['cancellation']
    elif args.command=='doctor':
        result={'dependencies':{k:shutil.which(k) is not None for k in ('grim','hyprctl','node')},'pointer':(ROOT/'native/pointer').is_file(),'session':False,'monitors':[]}
        result['capabilities']=capability_matrix()
        result['dependencies']['wtype']=(ROOT/'native/wtype').is_file()
        try:
            env=environment()
            result['session']=bool(env.get('WAYLAND_DISPLAY'))
            monitors=hypr(env,'monitors')
            result['monitors']=[{k:m[k] for k in ('name','width','height','scale','transform')} for m in monitors]
            try:result['cursorpos']=hypr(env,'cursorpos')
            except Exception as exc:
                detail=' '.join(str(exc).split())
                detail=''.join(ch for ch in detail if ch==' ' or 32<=ord(ch)<=126)
                result['cursorpos_error']=('cursor position unavailable: '+detail)[:400]
            try:result['active_window']=hypr(env,'activewindow').get('address')
            except Exception as exc:
                detail=' '.join(str(exc).split())
                detail=''.join(ch for ch in detail if ch==' ' or 32<=ord(ch)<=126)
                result['active_window_error']=('active window unavailable: '+detail)[:400]
        except Exception as exc:
            detail=' '.join(str(exc).split())
            detail=''.join(ch for ch in detail if ch==' ' or 32<=ord(ch)<=126)
            result['monitors']=[]
            result['monitors_error']=('monitors unavailable: '+detail)[:400]
        if shutil.which('fcitx5-remote'):
            # Optional probes: at most ~1s each, and a failure is a diagnostic,
            # never a reason to stop. BaseException still propagates.
            try:
                result['ime']={'state':run(['fcitx5-remote'],env,timeout=1).strip(),
                               'name':run(['fcitx5-remote','-n'],env,timeout=1).strip()}
            except Exception as exc:
                result['ime_error']=('fcitx5 probe failed: '+' '.join(str(exc).split()))[:400]
    elif args.command=='windows':
        # Read-only discovery: one clients call, filtering before projection, no focus or input.
        keys=('address','class','title','at','size','workspace')
        if args.no_titles:keys=('address','class','at','size','workspace')
        clients=hypr(env,'clients')
        if args.class_ is not None:clients=[c for c in clients if c.get('class')==args.class_]
        result=[{k:c.get(k) for k in keys} for c in clients]
    elif args.command=='observe':
        check_cancel()
        if not 0<=args.settle_ms<=2000: raise ValueError('settle-ms must be 0..2000')
        with locked():
            effective_width=min(args.max_width,LOW_RES_MAX_WIDTH) if args.low_res else args.max_width
            if args.settle_ms:
                if args.focus:focus(env,args.window)
                capture=lambda: (observe_screen(env,args.screen,args.crop,effective_width,low_res=args.low_res,persist=False) if args.screen else
                                 observe(env,args.window,args.crop,effective_width,activate=False,low_res=args.low_res,persist=False))
                result=settled_observation(capture,args.settle_ms,effective_width)
            else:
                result=(observe_screen(env,args.screen,args.crop,effective_width,low_res=args.low_res) if args.screen else
                        observe(env,args.window,args.crop,effective_width,activate=args.focus,low_res=args.low_res))
            import session_policy
            session_policy.record_observation(STATE,os.environ.get('CU_SESSION_TOKEN'),result)
    elif args.command=='act':
        require_session()
        try:actions=read_json(sys.stdin) if args.actions=='-' else read_json_file(args.actions)
        except ValueError as exc:raise PreflightRefusal(str(exc)) from exc
        if args.expected_terminal_bounds is not None and args.expected_terminal_window in ('same','none','unbound'):
            raise ValueError('--expected-terminal-bounds requires a terminal window address')
        expected_terminal=(None if args.expected_terminal_window=='same' else
                           args.expected_terminal_window if args.expected_terminal_window in ('none','unbound') else
                           {'address':args.expected_terminal_window,
                            **({'bounds':args.expected_terminal_bounds}
                               if args.expected_terminal_bounds is not None else {})})
        check_cancel()
        with locked():
            import session_policy
            session_policy.require_observation(STATE,os.environ.get('CU_SESSION_TOKEN'),args.observation)
            act_kwargs={'after_capture':not args.no_after,
                        'observation_path':args.observation}
            if expected_terminal is not None:
                act_kwargs['expected_terminal_window']=expected_terminal
            result=desktop_act(env,read_json_file(args.observation),actions,**act_kwargs)
            if is_transient_refusal(result):
                check_cancel()
                session_policy.record_refusal(STATE,os.environ.get('CU_SESSION_TOKEN'))
                print('session refusal: error='+result['error']+' action=require_reobserve',file=sys.stderr)
            elif result.get('ok') is True or is_completed_capture_error(result,len(actions)):
                session_policy.complete_requirement(STATE,os.environ.get('CU_SESSION_TOKEN'))
    elif args.command=='act-now':
        import first_action
        return first_action.run(args)
    elif args.command=='a11y':
        check_cancel()
        request={'operation':args.operation,'pid':args.pid,'snapshot':args.snapshot}
        if args.skeleton:
            if args.operation!='observe':raise ValueError('--skeleton requires a11y observe')
            request['skeleton']=True
        if args.ref is not None and args.operation not in ('drill','ground'):raise ValueError('ref requires a11y drill or ground')
        if args.operation=='drill':
            if not args.ref or not args.snapshot:raise ValueError('a11y drill requires ref and --snapshot')
            request['ref']=args.ref
        if args.operation=='query':
            if args.pid is None:raise ValueError('a11y query requires --pid')
            if args.name is None and args.role is None:raise ValueError('a11y query requires --name or --role')
            if args.name is not None:request['name']=args.name
            if args.role is not None:request['role']=args.role
            request['limit']=args.limit
        if args.operation=='ground':
            # Pick 4 fast path, flag-gated: resolve one a11y ref to global
            # desktop coordinates plus the crop that verifies it. Read-only:
            # no pointer movement, no click, no typing happens here. The
            # caller must observe the crop and confirm the target before
            # any click; a click from an unverified coordinate is refused.
            import fastpath
            if not fastpath.enabled():raise ValueError('pick4 fast path is off; set CU_PICK4_FASTPATH=1')
            if not args.ref or not args.snapshot or not args.address:
                raise ValueError('a11y ground requires ref, --snapshot and --address')
            request['ref']=args.ref
        if args.operation=='act':
            require_session()
            if not args.actions: raise ValueError('--actions required')
            try:request['actions']=read_json(sys.stdin) if args.actions=='-' else read_json_file(args.actions)
            except ValueError as exc:raise PreflightRefusal(str(exc)) from exc
            validate_actions(request['actions'],'a11y')
        with locked():
            if args.operation=='act':
                import session_policy
                session_policy.require_observation(STATE,os.environ.get('CU_SESSION_TOKEN'))
            out=run_cancelable(['python3',str(ROOT/'scripts/a11y.py')],env=env,input=json.dumps(request),timeout=15)
            result=json.loads(out) if out.strip() else {'ok':False,'error':'accessibility adapter returned no data'}
            if args.operation=='ground' and isinstance(result,dict) and result.get('ok') is True:
                import fastpath
                clients=hypr(env,'clients')
                window=next((c for c in clients if c.get('address')==args.address),None)
                if window is None:raise ValueError('no window with that address; run windows again')
                bounds=[window['at'][0],window['at'][1],window['size'][0],window['size'][1]]
                frame=fastpath.detect_coord_frame(result.get('root_extents'),bounds) if result.get('root_extents') is not None else 'unknown'
                box=fastpath.to_global_box(result['extents'],bounds[:2],frame)
                center=fastpath.box_center(box)
                crop=fastpath.crop_for_box(box,bounds)
                result={'ok':True,'backend':'pick4-ground','ref':result['ref'],
                        'role':result['role'],'name':result['name'],
                        'extents':result['extents'],'extents_coord':result['extents_coord'],
                        'coord_frame':frame,'window':{'address':args.address,'bounds':bounds},
                        'box':box,'center':center,'crop':crop,
                        'verify':'observe --window '+args.address+' --crop '+' '.join(str(v) for v in crop)+' and confirm the target is visible at the box center before any click'}
            if args.operation=='act' and isinstance(result,dict) and result.get('ok') is True:
                session_policy.complete_requirement(STATE,os.environ.get('CU_SESSION_TOKEN'))
    else:
        check_cancel()
        if args.no_after and args.operation!='act':raise ValueError('--no-after requires browser act')
        if args.no_after and args.image:raise ValueError('--no-after cannot combine with --image')
        if not 1<=args.max_elements<=80:raise ValueError('max-elements must be 1..80')
        if args.operation=='start':
            # Only a successful start moves the process default; a failed start
            # leaves the previous endpoint untouched for the next command.
            endpoint=args.endpoint or BROWSER_ENDPOINT
            started=browser_automation_call(env,lambda:browser_start(env,endpoint))
            if started.get('ok'):BROWSER_ENDPOINT=endpoint
            print(json.dumps(started));return 0
        # Endpoint selection stays inside the browser branch: non-browser
        # commands have no --endpoint attribute at all.
        request={'operation':args.operation,'endpoint':args.endpoint or BROWSER_ENDPOINT,'target':args.target,'snapshot':args.snapshot,'image':args.image,'max_elements':args.max_elements}
        if args.scope is not None:request['scope']=args.scope
        if args.after_scope is not None:request['after_scope']=args.after_scope
        if args.operation=='act':
            require_session()
            if not args.actions: raise ValueError('--actions required')
            try:request['actions']=read_json(sys.stdin) if args.actions=='-' else read_json_file(args.actions)
            except ValueError as exc:raise PreflightRefusal(str(exc)) from exc
            validate_actions(request['actions'],'browser')
            if args.no_after:
                validate_terminal_assert(request['actions'])
                request['no_after']=True
        with locked():
            if args.operation=='act':
                import session_policy
                session_policy.require_observation(STATE,os.environ.get('CU_SESSION_TOKEN'))
            result=browser_automation_call(env,lambda:browser(request))
            if args.operation=='act' and isinstance(result,dict) and result.get('ok') is True:
                session_policy.complete_requirement(STATE,os.environ.get('CU_SESSION_TOKEN'))
        raw=result.pop('image_base64',None) if isinstance(result,dict) else None
        if raw:
            import base64
            result['image']=save_observation(None,{'backend':'browser','target':args.target},1280,encoded_png=base64.b64decode(raw))['image']
    if args.command in ('observe','act') and not args.verbose:result=compact_result(result)
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')),flush=True)
    if isinstance(result,dict) and result.get('ok') is False:
        capture_recoverable=(args.command=='act' and
                             is_completed_capture_error(result,len(actions)))
        if args.command!='act' or not (is_transient_refusal(result) or capture_recoverable):
            stop_session_on_error()
        if capture_recoverable:return 0  # Full batch ran; caller must bind fresh evidence.
        return 1
    return 0

def require_session():
    if not os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('input requires computer-use session -- DRIVER [ARGS...]')
    check_cancel()

def stop_session_on_error():
    if os.environ.get('CU_SESSION_TOKEN'):
        import cursor_session
        cursor_session.request_stop(os.environ['CU_SESSION_TOKEN'])

if __name__=='__main__':
    try: exit_code=main()
    except SystemExit as exc:
        # argparse uses SystemExit for help (0) and invalid arguments (2).
        # Help is successful and must not stop an active automation session.
        exit_code=exc.code
        if exit_code:stop_session_on_error()
    except BaseException as exc:
        stop_session_on_error()
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),flush=True);exit_code=1
    sys.exit(exit_code)

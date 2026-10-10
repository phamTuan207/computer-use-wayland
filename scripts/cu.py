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
from pathlib import Path
import re
import select
import shutil
import socket
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'agent-computer-use'
CANCEL = STATE / 'cancelled'
SESSION_KEYS = {'XDG_RUNTIME_DIR','WAYLAND_DISPLAY','DISPLAY','HYPRLAND_INSTANCE_SIGNATURE',
                'DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE',
                'GDK_BACKEND','QT_QPA_PLATFORM','ELECTRON_OZONE_PLATFORM_HINT','MOZ_ENABLE_WAYLAND'}

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
    return list(dict.fromkeys(mods)),regular

def keyboard_argv(actions):
    args=['wtype'];total_ms=0
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
    argv=['wtype']
    if a.get('delay_ms',0):argv+=['-d',str(a['delay_ms'])]
    return argv+['-','-p','VoidSymbol']

def environment():
    env = os.environ.copy()
    # Refresh even a stale inherited session signature; do not copy secrets or PATH.
    for name in ('quickshell','Hyprland','waybar','kitty'):
        p = subprocess.run(['pgrep','-x',name], capture_output=True, text=True)
        for pid in p.stdout.split():
            try:
                data = dict(s.split('=',1) for s in Path('/proc',pid,'environ').read_bytes().decode().split('\0') if '=' in s)
                if data.get('WAYLAND_DISPLAY') and data.get('HYPRLAND_INSTANCE_SIGNATURE'):
                    env.update({k:v for k,v in data.items() if k in SESSION_KEYS})
                    return env
            except (OSError, UnicodeError):
                continue
    return env

def run(argv, env=None, text=True, input=None, timeout=12):
    p = subprocess.run(argv, env=env, capture_output=True, text=text, input=input, timeout=timeout)
    if p.returncode:
        err = p.stderr if text else p.stderr.decode(errors='replace')
        raise RuntimeError(f'{Path(argv[0]).name}: {err.strip()[:400]}')
    return p.stdout

def hypr(env, what):
    # The documented read-only IPC avoids a fork/exec for every safety check.
    # Keep CLI compatibility for callers without an explicit session environment.
    if env and env.get('XDG_RUNTIME_DIR') and env.get('HYPRLAND_INSTANCE_SIGNATURE'):
        if what not in ('clients','monitors','activewindow','cursorpos','devices','workspaces','layers'):
            raise ValueError('unsupported read-only compositor query')
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
    matches = [c for c in hypr(env,'clients') if c['address']==address]
    if len(matches)!=1: raise ValueError('window no longer exists')
    return matches[0]

def focus(env, address):
    if not re.fullmatch(r'0x[0-9a-fA-F]+',address or ''):raise ValueError('exact window address required')
    check_cancel()
    if hypr(env,'activewindow').get('address')==address:return
    window(env,address)  # Reject a stale target before changing the desktop.
    reply=run(['hyprctl','dispatch',f'hl.dsp.focus({{ window = "address:{address}" }})'],env).strip()
    if reply!='ok':raise RuntimeError('focus dispatch rejected: '+reply[:400])
    # Acknowledgment is not focus completion; allow workspace animations to settle.
    deadline=time.monotonic()+1.5
    while True:
        check_cancel()
        active=hypr(env,'activewindow').get('address')
        if active==address:return
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

def check_cancel():
    token=os.environ.get('CU_SESSION_TOKEN')
    if token:
        try:current=json.loads((STATE/'session.json').read_text()).get('token')
        except (OSError,ValueError):current=None
        if current!=token or (STATE/('stop-'+token)).exists():
            raise RuntimeError('automation session ended; stop this task')
    if CANCEL.exists(): raise RuntimeError('cancelled by user; stop this task. Run computer-use resume only after the user asks to continue')

def run_cancelable(argv, env=None, input=None, timeout=12):
    check_cancel()
    p=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        deadline=time.monotonic()+timeout
        first=True
        while True:
            check_cancel()
            try:
                out,err=p.communicate(input if first else None,timeout=min(.05,max(.001,deadline-time.monotonic())))
                break
            except subprocess.TimeoutExpired:
                first=False
                if time.monotonic()>=deadline: raise RuntimeError(f'{Path(argv[0]).name}: timed out')
        if p.returncode: raise RuntimeError(f'{Path(argv[0]).name}: {(err.strip() or out.strip())[:400]}')
        check_cancel()
        return out
    except Exception:
        if p.poll() is None:
            p.terminate()
            try:p.communicate(timeout=.5)
            except subprocess.TimeoutExpired:p.kill();p.communicate()
        raise

def save_observation(image, meta, max_width, persist=True):
    from PIL import Image
    if max_width < 320 or max_width > 3840: raise ValueError('max-width must be 320..3840')
    if image.width>max_width:
        image=image.resize((max_width,round(image.height*max_width/image.width)),Image.Resampling.LANCZOS)
    meta.update(image_size=list(image.size),max_width=max_width)
    if not persist:return image,meta
    prepare_state()
    token=uuid.uuid4().hex[:12]
    path=STATE/(token+'.png')
    image.save(path,compress_level=2);path.chmod(0o600)
    meta.update(id=token,created=time.time(),image=str(path),image_size=list(image.size),
                pixel_sha256=hashlib.sha256(image.tobytes()).hexdigest(),max_width=max_width)
    out=STATE/(token+'.json');meta['observation']=str(out)
    out.write_text(json.dumps(meta));out.chmod(0o600)
    # Only observation filenames are disposable; session.json is recovery state.
    for old in STATE.iterdir():
        if re.fullmatch(r'[0-9a-f]{12}\.(?:png|json)',old.name) and time.time()-old.stat().st_mtime>86400:
            old.unlink()
    return meta

def require_visible_window(c, m):
    visible={m.get('activeWorkspace',{}).get('id'),m.get('specialWorkspace',{}).get('id')}
    visible.discard(None);visible.discard(0)
    if c.get('mapped') is False or c.get('hidden') or (not c.get('pinned') and c.get('workspace',{}).get('id') not in visible):
        raise RuntimeError('window is not visible on its monitor; switch workspace yourself or use observe --window ADDRESS --focus')

def observe(env, address, crop=None, max_width=1280, activate=False, persist=True):
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
    start=time.monotonic()
    from indicator import capture_clean
    with capture_clean(STATE):
        raw=run(['grim','-s','1','-g',geometry,'-t','ppm','-'],env,text=False)
    image=Image.open(io.BytesIO(raw)).convert('RGB')
    current=window(env,address)
    if bounds(current) != wb or current['monitor']!=c['monitor']: raise RuntimeError('window moved during capture; observe again')
    current_monitor=next((item for item in hypr(env,'monitors') if item['id']==current['monitor']),None)
    if not current_monitor or monitor_box(current_monitor)!=mb or current_monitor['scale']!=m['scale'] or current_monitor.get('transform',0)!=m.get('transform',0):
        raise RuntimeError('monitor layout changed during capture; observe again')
    require_visible_window(current,current_monitor)
    meta={'backend':'desktop','scope':'window','window':address,'window_bounds':wb,'monitor':m['name'],
          'monitor_box':mb,'monitor_scale':m['scale'],'monitor_transform':m.get('transform',0),
          'region':region,'crop':crop,'capture_ms':round((time.monotonic()-start)*1000)}
    return save_observation(image,meta,max_width,persist)

def screen_region(monitor_box_,crop):
    mx,my,mw,mh=monitor_box_
    if crop is None:return monitor_box_.copy()
    x,y,w,h=crop
    if w<=0 or h<=0 or x<0 or y<0 or x+w>mw or y+h>mh:
        raise ValueError('crop must be a positive rectangle inside the selected monitor')
    return [mx+x,my+y,w,h]

def observe_screen(env,monitor,crop=None,max_width=1280,persist=True):
    from PIL import Image
    m=next((m for m in hypr(env,'monitors') if m['name']==monitor),None)
    if not m:raise ValueError('monitor no longer exists; use doctor to list monitors')
    mb=monitor_box(m);region=screen_region(mb,crop)
    geometry=f'{region[0]},{region[1]} {region[2]}x{region[3]}'
    start=time.monotonic()
    from indicator import capture_clean
    with capture_clean(STATE):
        raw=run(['grim','-s','1','-g',geometry,'-t','ppm','-'],env,text=False)
    current=next((m for m in hypr(env,'monitors') if m['name']==monitor),None)
    if not current or monitor_box(current)!=mb or current['scale']!=m['scale'] or current.get('transform',0)!=m.get('transform',0):
        raise RuntimeError('monitor layout changed during capture; observe again')
    image=Image.open(io.BytesIO(raw)).convert('RGB')
    meta={'backend':'desktop','scope':'screen','monitor':monitor,'monitor_box':mb,
          'monitor_scale':m['scale'],'monitor_transform':m.get('transform',0),
          'region':region,'crop':crop,'capture_ms':round((time.monotonic()-start)*1000)}
    return save_observation(image,meta,max_width,persist)

def image_point(meta,x,y):
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (x,y)): raise ValueError('finite coordinates required')
    iw,ih=meta['image_size'];rx,ry,rw,rh=meta['region']
    if not (0<=x<iw and 0<=y<ih): raise ValueError('point outside observed image')
    return rx+x*rw/iw, ry+y*rh/ih

def screen_changed(old,new,actions):
    from PIL import ImageChops,ImageStat
    if old.size!=new.size:return True
    diff=ImageChops.difference(old,new)
    if sum(ImageStat.Stat(diff).mean)/3>3:return True
    # A small button can move without changing the global average appreciably.
    for a in actions:
        points=[a.get('from'),a.get('to')] if a['type']=='drag' else [[a.get('x'),a.get('y')]]
        for point in points:
            if not point or point[0] is None:continue
            x,y=point;patch=diff.crop((max(0,int(x)-24),max(0,int(y)-24),min(old.width,int(x)+25),min(old.height,int(y)+25)))
            if sum(ImageStat.Stat(patch).mean)/3>6:return True
    return False

def validate_actions(actions,backend):
    if not isinstance(actions,list) or not 1<=len(actions)<=32: raise ValueError('actions must contain 1..32 items')
    allowed={'click','double_click','move','drag','scroll','type','key','wait'} if backend=='desktop' else {'click','fill','key','scroll','wait','assert'}
    for a in actions:
        if not isinstance(a,dict) or a.get('type') not in allowed: raise ValueError('unsupported action')
        if backend=='desktop' and a['type'] in ('move','click','double_click','drag','scroll'):
            modifiers=a.get('modifiers',[])
            if not isinstance(modifiers,list) or len(modifiers)>5 or not all(isinstance(m,str) and m.lower() in MODIFIERS for m in modifiers):
                raise ValueError('mouse modifiers must be an array of Ctrl/Shift/Alt/Super/AltGr')
            if a['type']=='move' and modifiers:raise ValueError('modifiers require click, drag or scroll')
        if a['type']=='wait' and not 0<=a.get('ms',100)<=2000: raise ValueError('wait ms must be 0..2000')
        if a['type'] in ('type','fill') and (not isinstance(a.get('text'),str) or len(a['text'])>10000): raise ValueError('text must be string <=10000 chars')
        if a['type']=='key' and (not isinstance(a.get('keys'),list) or not a['keys'] or not all(isinstance(k,str) and len(k)<40 for k in a['keys'])): raise ValueError('keys must be an array of key names')
        if backend=='desktop' and a['type']=='type' and any(ord(c)>0xffff for c in a['text']):
            raise ValueError('non-BMP text may be corrupted by Wayland keyboard input; use browser fill or a11y set_text')
        if backend=='desktop' and a['type']=='key':
            key_names(a['keys'])
            if not isinstance(a.get('repeat',1),int) or not 1<=a.get('repeat',1)<=30:raise ValueError('repeat must be 1..30')
            if not isinstance(a.get('hold_ms',12),int) or not 0<=a.get('hold_ms',12)<=2000:raise ValueError('hold_ms must be 0..2000')
        if backend=='desktop' and a['type']=='type' and (not isinstance(a.get('delay_ms',0),int) or not 0<=a.get('delay_ms',0)<=100):raise ValueError('delay_ms must be 0..100')
        if backend=='desktop' and a['type']=='type' and a.get('ime','literal') not in ('literal','compose'):raise ValueError('ime must be literal or compose')

def keyboard_groups(actions):
    groups=[];delay=0;boundary=False;mode=None
    for a in actions:
        if a['type'] in ('key','type','wait') and not (a['type']=='type' and a['text'].startswith('-')):
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

@contextmanager
def literal_keyboard(env,enabled=True):
    """Bypass composition for exact text; preserve the focused context's IME state."""
    import signal
    remote=shutil.which('fcitx5-remote') if enabled else None
    if not remote:
        yield
        return
    def state():
        value=run([remote],env).strip()
        if value not in ('0','1','2'):raise RuntimeError('cannot determine fcitx5 state')
        return value
    def switch(flag,expected):
        run([remote,flag],env)
        deadline=time.monotonic()+.5
        while state()!=expected:
            if time.monotonic()>=deadline:raise RuntimeError('fcitx5 state change timed out')
            time.sleep(.01)
    original=state()
    previous={}
    # Without a handler, the default SIGTERM/SIGHUP disposes the process mid-yield
    # and skips finally(), leaving the IME disabled. Raise instead so cleanup runs.
    def interrupted(signum,frame):
        raise RuntimeError(f'keyboard input interrupted by signal {signum}')
    for sig in (signal.SIGTERM,signal.SIGHUP):
        previous[sig]=signal.getsignal(sig)
        signal.signal(sig,interrupted)
    try:
        if original=='2':switch('-c','1')
        yield
    finally:
        try:
            # Keep the handler until the IME is restored so a late signal still cleans up.
            if original=='2':switch('-o','2')
        finally:
            for sig,handler in previous.items():
                signal.signal(sig,handler)

def compact_result(result):
    """Only strip presentation data; immutable observations retain full geometry."""
    if not isinstance(result,dict):return result
    if result.get('backend')=='desktop':
        keys=('image','observation','image_size','capture_ms','region','crop',
              'settle_stable','settle_samples','settle_ms')
        out={k:result[k] for k in keys if k in result}
        # An agent reads coordinates off the returned PNG. Without the ratio
        # between that PNG and the window it asked for, --crop cannot be reasoned
        # about from output alone and the contract lives only in this file.
        if 'region' in out and out['region'][2]:
            out['scale']=round(out['image_size'][0]/out['region'][2],6)
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

def desktop_act(env,meta,actions,after_capture=True):
    if not isinstance(after_capture,bool): raise ValueError('after_capture must be boolean')
    check_cancel()
    if meta.get('backend')!='desktop': raise ValueError('desktop observation required')
    if time.time()-meta['created']>90: raise ValueError('observation older than 90s; observe again')
    validate_actions(actions,'desktop')
    screen_scope=meta.get('scope')=='screen'
    if screen_scope and any(a['type'] in ('key','type') for a in actions):
        raise ValueError('screen observations support pointer actions only; use a window or accessibility target for typing')
    # Validate coordinates and payloads for the entire batch before any side effects.
    for a in actions:
        if a['type'] in ('click','double_click','move','scroll'):
            image_point(meta,a['x'],a['y'])
        if a['type']=='drag':
            image_point(meta,*a['from']);image_point(meta,*a['to'])
        if a['type'] in ('click','double_click','drag') and a.get('button','left') not in ('left','right','middle'): raise ValueError('invalid button')
        if a['type']=='scroll' and not all(isinstance(a.get(k,0),(int,float)) and math.isfinite(a.get(k,0)) and abs(a.get(k,0))<=2000 for k in ('dx','dy')): raise ValueError('invalid scroll')
        if a['type']=='drag' and not 50<=a.get('ms',300)<=2000: raise ValueError('drag ms must be 50..2000')
    # Group adjacent keyboard operations into one existing wtype process.
    groups=keyboard_groups(actions)
    for group in groups:
        if isinstance(group,list):keyboard_argv(group)
        elif group.get('type')=='type':standalone_type_argv(group)
    address=None if screen_scope else meta['window']
    def guard():
        check_cancel()
        if not screen_scope:
            c=window(env,address)
            if bounds(c)!=meta['window_bounds']: raise RuntimeError('window geometry changed; observe again')
        m=next((m for m in hypr(env,'monitors') if m['name']==meta['monitor']),None)
        if not m or monitor_box(m)!=meta['monitor_box'] or m['scale']!=meta['monitor_scale'] or m.get('transform',0)!=meta['monitor_transform']: raise RuntimeError('monitor layout changed; observe again')
        if not screen_scope and hypr(env,'activewindow').get('address')!=address: raise RuntimeError('focus changed; batch stopped')
    if not screen_scope:focus(env,address)
    guard()
    # Refuse coordinates from an image superseded by a visible layout change.
    new,fresh=(observe_screen(env,meta['monitor'],meta.get('crop'),meta['max_width'],persist=False) if screen_scope else
               observe(env,address,meta.get('crop'),meta['max_width'],activate=False,persist=False))
    from PIL import Image
    old=Image.open(meta['image'])
    if screen_changed(old,new,actions):
        fresh=save_observation(new,fresh,meta['max_width'])
        return {'ok':False,'completed':0,'error':'screen changed since observation; inspect after.image','after':fresh}
    # A keyboard-only batch must not open the virtual pointer device at all.
    pointer=(Pointer(env,meta['monitor']) if any(a['type'] in ('move','click','double_click','scroll','drag') for a in actions) else None)
    completed=0;error=None
    def move(x,y):
        gx,gy=image_point(meta,x,y);mx,my,mw,mh=meta['monitor_box']
        # High resolution normalized coordinates, independent of image resize / output scale.
        pointer.command(f'abs {round((gx-mx)/mw*1000000)} {round((gy-my)/mh*1000000)} 1000000 1000000')
        pos=hypr(env,'cursorpos')
        if math.hypot(pos['x']-gx,pos['y']-gy)>3: raise RuntimeError('pointer missed target; refusing click')
    def execute_group(a):
        guard()
        if isinstance(a,list):
            exact=any(x['type']=='type' and x.get('ime','literal')=='literal' for x in a)
            if not any(x['type']=='type' and x.get('ime')=='compose' for x in a):
                exact=exact or any(x['type']=='key' and any(k in ('BackSpace','Delete','Home','End','Left','Right','Up','Down','Prior','Next') for k in key_names(x['keys'])[1]) for x in a)
            with literal_keyboard(env,exact):
                guard();run_cancelable(keyboard_argv(a),env)
            return len(a)
        typ=a['type']
        if typ in ('move','click','double_click','scroll'):
            move(a['x'],a['y'])
            if typ in ('click','double_click'):
                b={'left':0,'right':1,'middle':2}[a.get('button','left')]
                presses=2 if typ=='double_click' else 1
                for press in range(presses):
                    guard();pointer.command(f'button {b} 1')
                    try:wait_cancelable(.025)
                    finally:pointer.command(f'button {b} 0')
                    # 35 ms only separates the two double-click presses; after the
                    # last press it would only add latency before the action ends.
                    if press+1<presses:wait_cancelable(.035)
            elif typ=='scroll':
                wait_cancelable(.03);guard()
                pointer.command(f"scroll {a.get('dx',0)} {a.get('dy',0)}")
        elif typ=='drag':
            sx,sy=a['from'];ex,ey=a['to'];move(sx,sy);guard()
            b={'left':0,'right':1,'middle':2}[a.get('button','left')]
            pointer.command(f'button {b} 1')
            try:
                for i in range(1,11):
                    guard();move(sx+(ex-sx)*i/10,sy+(ey-sy)*i/10);wait_cancelable(a.get('ms',300)/10000)
            finally:pointer.command(f'button {b} 0')
        elif typ=='type':
            with literal_keyboard(env,a.get('ime','literal')=='literal'):
                guard();run_cancelable(standalone_type_argv(a),env,input=a['text'])
        elif typ=='wait':wait_cancelable(a.get('ms',100)/1000)
        return 1
    start=time.monotonic()
    try:
        # A new virtual device at an unchanged cursor position may not cause
        # Hyprland to deliver enter/motion to a newly mapped surface. Establish
        # real motion without clicking; the action still ends at its exact target.
        if any(a['type'] in ('move','click','double_click','scroll','drag') for a in actions):
            # Capture can outlast cancellation or a focus/layout change. The
            # preparatory motion is input too, so validate before sending it.
            guard()
            first=next(a for a in actions if a['type'] in ('move','click','double_click','scroll','drag'))
            point=first['from'] if first['type']=='drag' else [first['x'],first['y']]
            gx,gy=image_point(meta,*point);mx,my,mw,mh=meta['monitor_box'];rx,ry,rw,rh=meta['region']
            nx=gx+2 if gx<rx+rw-3 else max(rx,gx-2);ny=gy
            pointer.command(f'abs {round((nx-mx)/mw*1000000)} {round((ny-my)/mh*1000000)} 1000000 1000000')
        for a in groups:
            guard()
            with mouse_modifiers(env,a.get('modifiers',[]) if isinstance(a,dict) else []):
                completed+=execute_group(a)
            guard()
    except Exception as exc: error=str(exc)
    finally:
        if pointer:pointer.close()
    if not after_capture and error is None:
        return {'ok':True,'completed':completed,
                'execution_ms':round((time.monotonic()-start)*1000),'after_skipped':True}
    time.sleep(.08)
    result={'ok':error is None,'completed':completed,'execution_ms':round((time.monotonic()-start)*1000)}
    if error: result['error']=error
    try:
        result['after']=(observe_screen(env,meta['monitor'],meta.get('crop'),meta['max_width']) if screen_scope else
                         observe(env,address,meta.get('crop'),meta['max_width'],activate=False))
        result['changed']=result['after']['pixel_sha256']!=meta['pixel_sha256']
    except Exception as exc:
        result['ok']=False;result['capture_error']=str(exc)
        result.setdefault('error','final capture failed: '+str(exc))
    return result

def browser(request):
    # Keep setup/snapshot allowance; each guard can take 5s, and the final
    # assert evaluation can overrun its polling budget by another 5s.
    # Cap adapter execution instead of accumulating unbounded per-action allowance.
    budget=sum(5000+(max(0,min(a.get('timeout_ms',1000),3000))+5000 if a['type']=='assert' else
                     a.get('ms',100) if a['type']=='wait' else 0) for a in request.get('actions',[]))
    out=run_cancelable(['node',str(ROOT/'scripts/cdp.mjs')],input=json.dumps(request),timeout=min(60,35+budget/1000))
    if out.strip(): return json.loads(out)
    raise RuntimeError('CDP adapter failed')

def browser_start(env,endpoint):
    import urllib.request
    import urllib.parse
    url=urllib.parse.urlparse(endpoint)
    if url.hostname not in ('localhost','127.0.0.1','::1') or url.scheme!='http':raise ValueError('loopback http endpoint required')
    port=url.port or 9222
    try:
        json.load(urllib.request.urlopen(urllib.parse.urljoin(endpoint,'/json/version'),timeout=1))
        return {'ok':True,'endpoint':endpoint,'reused':True}
    except Exception:pass
    prepare_state();profile=ROOT/'browser-profile';profile.mkdir(mode=0o700,exist_ok=True)
    log=open(STATE/'browser.log','a');log_path=STATE/'browser.log';log_path.chmod(0o600)
    p=subprocess.Popen(['chromium',f'--user-data-dir={profile}',f'--remote-debugging-port={port}',
        f'--remote-debugging-address={url.hostname if url.hostname!="localhost" else "127.0.0.1"}','--no-first-run','--no-default-browser-check','about:blank'],
        env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    log.close()
    for _ in range(50):
        check_cancel()
        try:
            json.load(urllib.request.urlopen(urllib.parse.urljoin(endpoint,'/json/version'),timeout=.3))
            return {'ok':True,'endpoint':endpoint,'reused':False,'pid':p.pid,'profile':str(profile)}
        except Exception:time.sleep(.1)
    raise RuntimeError('managed browser did not expose CDP; see '+str(log_path))

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

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    session=sub.add_parser('session');session.add_argument('driver',nargs=argparse.REMAINDER)
    sub.add_parser('finish');sub.add_parser('recover');sub.add_parser('cancel')
    sub.add_parser('doctor');sub.add_parser('windows');sub.add_parser('resume');sub.add_parser('status')
    obs=sub.add_parser('observe');target=obs.add_mutually_exclusive_group(required=True);target.add_argument('--window');target.add_argument('--screen');obs.add_argument('--crop',nargs=4,type=int);obs.add_argument('--max-width',type=int,default=1280)
    obs.add_argument('--focus',action='store_true',help='explicitly focus the target window before capture (may switch workspace)')
    obs.add_argument('--settle-ms',type=int,default=0,help='wait up to 2000 ms for 120 ms of unchanged crop pixels; not semantic readiness')
    act=sub.add_parser('act');act.add_argument('--observation',required=True);act.add_argument('--actions',required=True)
    act.add_argument('--no-after',action='store_true',help='skip successful final capture; preflight safety and error captures stay enabled')
    obs.add_argument('--verbose',action='store_true');act.add_argument('--verbose',action='store_true')
    b=sub.add_parser('browser');b.add_argument('operation',choices=['start','tabs','observe','act']);b.add_argument('--endpoint',default='http://127.0.0.1:9222');b.add_argument('--target');b.add_argument('--snapshot');b.add_argument('--actions');b.add_argument('--image',action='store_true')
    a=sub.add_parser('a11y');a.add_argument('operation',choices=['apps','observe','act']);a.add_argument('--pid',type=int);a.add_argument('--snapshot');a.add_argument('--actions')
    args=parser.parse_args()
    if args.command=='observe' and args.focus and not args.window:parser.error('--focus requires --window')
    # Local state commands and CDP requests do not use a compositor environment.
    env=(environment() if args.command in ('session','recover','doctor','windows','observe','act','a11y') or
         (args.command=='browser' and args.operation=='start') else None)
    if args.command in ('session','finish','recover','cancel'):
        import cursor_session
        if args.command=='session':return cursor_session.supervise(env,args.driver)
        if args.command=='recover':return cursor_session.recover(env)
        if args.command=='cancel':
            prepare_state();CANCEL.touch(mode=0o600)
        cursor_session.request_stop()
        result={'ok':True}
    elif args.command=='resume':
        CANCEL.unlink(missing_ok=True)
        result={'ok':True,'cancelled':False}
    elif args.command=='status': result={'ok':True,'cancelled':CANCEL.exists()}
    elif args.command=='doctor':
        result={'dependencies':{k:shutil.which(k) is not None for k in ('grim','wtype','hyprctl','node')},'pointer':(ROOT/'native/pointer').is_file(),'session':bool(env.get('WAYLAND_DISPLAY')),'monitors':hypr(env,'monitors')}
        if shutil.which('fcitx5-remote'):
            result['ime']={'state':run(['fcitx5-remote'],env).strip(),'name':run(['fcitx5-remote','-n'],env).strip()}
        result['monitors']=[{k:m[k] for k in ('name','width','height','scale','transform')} for m in result['monitors']]
    elif args.command=='windows': result=[{k:c.get(k) for k in ('address','class','title','at','size','workspace')} for c in hypr(env,'clients')]
    elif args.command=='observe':
        check_cancel()
        if not 0<=args.settle_ms<=2000: raise ValueError('settle-ms must be 0..2000')
        with locked():
            if args.settle_ms:
                if args.focus:focus(env,args.window)
                capture=lambda: (observe_screen(env,args.screen,args.crop,args.max_width,persist=False) if args.screen else
                                 observe(env,args.window,args.crop,args.max_width,activate=False,persist=False))
                result=settled_observation(capture,args.settle_ms,args.max_width)
            else:
                result=(observe_screen(env,args.screen,args.crop,args.max_width) if args.screen else
                        observe(env,args.window,args.crop,args.max_width,activate=args.focus))
    elif args.command=='act':
        require_session()
        actions=json.loads(sys.stdin.read() if args.actions=='-' else Path(args.actions).read_text())
        check_cancel()
        with locked(): result=desktop_act(env,json.loads(Path(args.observation).read_text()),actions,after_capture=not args.no_after)
    elif args.command=='a11y':
        check_cancel()
        request={'operation':args.operation,'pid':args.pid,'snapshot':args.snapshot}
        if args.operation=='act':
            require_session()
            if not args.actions: raise ValueError('--actions required')
            request['actions']=json.loads(sys.stdin.read() if args.actions=='-' else Path(args.actions).read_text())
        with locked():out=run_cancelable(['python3',str(ROOT/'scripts/a11y.py')],env=env,input=json.dumps(request),timeout=15)
        result=json.loads(out) if out.strip() else {'ok':False,'error':'accessibility adapter returned no data'}
    else:
        check_cancel()
        if args.operation=='start':
            print(json.dumps(browser_start(env,args.endpoint)));return 0
        request={'operation':args.operation,'endpoint':args.endpoint,'target':args.target,'snapshot':args.snapshot,'image':args.image}
        if args.operation=='act':
            require_session()
            if not args.actions: raise ValueError('--actions required')
            request['actions']=json.loads(sys.stdin.read() if args.actions=='-' else Path(args.actions).read_text());validate_actions(request['actions'],'browser')
        with locked():result=browser(request)
        raw=result.pop('image_base64',None) if isinstance(result,dict) else None
        if raw:
            import base64
            from PIL import Image
            result['image']=save_observation(Image.open(io.BytesIO(base64.b64decode(raw))).convert('RGB'),{'backend':'browser','target':args.target},1280)['image']
    if args.command in ('observe','act') and not args.verbose:result=compact_result(result)
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')),flush=True)
    if isinstance(result,dict) and result.get('ok') is False:
        stop_session_on_error();return 1
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

"""Required session-only real cursor theme with durable guardian restoration."""
import ast
import json
import os
from pathlib import Path
import re
import socket
import stat
import struct
import subprocess
import sys

PROFILE = Path(__file__).resolve().parents[1] / 'native/agent-cursor.json'
SCHEMA = 'org.gnome.desktop.interface'
# Read the compiled Xcursor search path rather than guessing an XDG default.
SEARCH_ROOTS_CODE = """
import ctypes
library = ctypes.CDLL('libXcursor.so.1')
library.XcursorLibraryPath.restype = ctypes.c_char_p
value = library.XcursorLibraryPath()
print(value.decode() if value else '')
"""


# Load the configured theme directly: a theme-name acknowledgement can fall back.
THEME_CHECK_CODE = """
import ctypes, os, sys
from pathlib import Path
library = ctypes.CDLL('libXcursor.so.1')
library.XcursorLibraryPath.restype = ctypes.c_char_p
library.XcursorFilenameLoadImage.argtypes = [ctypes.c_char_p, ctypes.c_int]
library.XcursorFilenameLoadImage.restype = ctypes.c_void_p
library.XcursorImageDestroy.argtypes = [ctypes.c_void_p]
roots = library.XcursorLibraryPath().decode().split(':')
directory = next((Path(root).expanduser() / sys.argv[1] for root in roots
                  if root and (Path(root).expanduser() / sys.argv[1]).is_dir()), None)
if directory is None:
    raise SystemExit('agent cursor theme is not installed on the Xcursor search path')
for role in ('left_ptr', 'text', 'pointer'):
    image = library.XcursorFilenameLoadImage(os.fsencode(directory / 'cursors' / role), int(sys.argv[2]))
    if not image:
        raise SystemExit('agent cursor theme has no loadable ' + role + ' cursor')
    library.XcursorImageDestroy(image)
"""


def command(env, *args):
    return subprocess.check_output(list(args), env=env, text=True, stderr=subprocess.STDOUT, timeout=5).strip()


def search_roots(env):
    """Where Xcursor actually looks for themes, read from the real library.

    This reports the compiled-in default or the environment override the library
    itself applies, so no XDG or home-directory constant is assumed here. It runs
    one short interpreter and touches no desktop; call it from setup and the
    fresh-login loader, not from every task snapshot.
    """
    raw = command(env, sys.executable, '-c', SEARCH_ROOTS_CODE)
    return [Path(part).expanduser().resolve() for part in raw.split(':') if part]


def validate(theme, size):
    if not isinstance(theme,str) or theme in ('.','..') or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',theme):
        raise ValueError('invalid cursor theme name')
    if type(size) is not int or not 16 <= size <= 96:
        raise ValueError('cursor size must be 16..96')


def gtk_state(env):
    """Read validated GTK values for the task's independent cursor snapshot."""
    theme = ast.literal_eval(command(env,'gsettings','get',SCHEMA,'cursor-theme'))
    size = int(command(env,'gsettings','get',SCHEMA,'cursor-size'))
    validate(theme,size)
    return theme,size


def snapshot(env):
    if not PROFILE.is_file():
        raise RuntimeError('agent cursor profile required; run setup with explicit --restore-theme and --restore-size')
    with PROFILE.open('rb') as stream:
        raw = stream.read(4097)
    if len(raw) > 4096:raise ValueError('cursor profile exceeds 4096 bytes')
    profile = json.loads(raw)
    if not isinstance(profile,dict):raise ValueError('cursor profile must be an object')
    validate(profile['theme'],profile['size'])
    mode = profile.get('restore_mode')
    if mode is not None:
        raise ValueError('unknown restore_mode: '+repr(mode))
    validate(profile['restore_theme'],profile['restore_size'])
    command(env,sys.executable,'-c',THEME_CHECK_CODE,profile['theme'],str(profile['size']))
    theme,size = gtk_state(env)
    return {'gtk_theme':theme,'gtk_size':size,'hypr_theme':profile['restore_theme'],
            'hypr_size':profile['restore_size'],'agent_theme':profile['theme'],'agent_size':profile['size']}


def guard_reply(raw, **expected):
    if len(raw) > 4096:raise RuntimeError('cursor guard reply exceeds 4096 bytes')
    reply = json.loads(raw)
    if (not isinstance(reply,dict) or reply.get('ok') is not True or
        type(reply.get('schema')) is not int or reply['schema'] != 1 or
        any(type(reply.get(key)) is not type(value) or reply[key] != value for key,value in expected.items())):
        raise RuntimeError('cursor guard did not confirm ownership or restoration')
    return reply


def check_guard(env):
    guard_reply(command(env,'hyprctl','cu-cursor','status'),active=False,token='')


class Guard:
    """A non-inherited socket lease; EOF restores the latest client cursor."""
    def __init__(self, env, theme, size, token):
        if not isinstance(token,str) or not re.fullmatch(r'[0-9a-f]{32}',token):
            raise ValueError('invalid cursor guard token')
        runtime = env.get('XDG_RUNTIME_DIR','')
        if not os.path.isabs(runtime):raise RuntimeError('cursor guard requires XDG_RUNTIME_DIR')
        directory = Path(runtime)/'agent-computer-use'
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise RuntimeError('cursor guard directory is not private')
        path = directory/'cursor-guard.sock'
        info = path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.geteuid():
            raise RuntimeError('cursor guard endpoint is not a private socket')
        self.socket = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.token = token
        try:
            self.socket.settimeout(3)
            self.socket.connect(str(path))
            _,uid,_ = struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
            if uid != os.geteuid():raise RuntimeError('cursor guard owner changed')
            self.socket.sendall((json.dumps({'schema':1,'theme':theme,'size':size,'token':token})+'\n').encode())
            self.receive()
            self.socket.settimeout(None)
        except BaseException:
            self.socket.close()
            raise

    def receive(self, **expected):
        data = bytearray()
        while b'\n' not in data and len(data) <= 4096:
            part = self.socket.recv(4097-len(data))
            if not part:raise RuntimeError('cursor guard disconnected before acknowledgement')
            data.extend(part)
        if not data.endswith(b'\n') or data.count(b'\n') != 1:
            raise RuntimeError('invalid cursor guard acknowledgement')
        guard_reply(data,token=self.token,**expected)

    def command(self, operation):
        if operation not in ('hide','show'):raise ValueError('invalid cursor visibility operation')
        self.socket.settimeout(3)
        try:
            self.socket.sendall((json.dumps({'op':operation,'token':self.token})+'\n').encode())
            self.receive(state='hidden' if operation=='hide' else 'visible')
        finally:
            self.socket.settimeout(None)

    def close(self):
        self.socket.close()


def apply(env, theme, size, token=None):
    validate(theme,size)
    return Guard(env,theme,size,token)


def restore(env, saved):
    if 'guard_token' in saved:
        token = saved['guard_token']
        if not isinstance(token,str) or not re.fullmatch(r'[0-9a-f]{32}',token):
            raise ValueError('invalid saved cursor guard token')
        guard_reply(command(env,'hyprctl','cu-cursor','release',token),released=token)
        return
    validate(saved['gtk_theme'],saved['gtk_size'])
    validate(saved['hypr_theme'],saved['hypr_size'])
    command(env,'gsettings','set',SCHEMA,'cursor-theme',saved['gtk_theme'])
    command(env,'gsettings','set',SCHEMA,'cursor-size',str(saved['gtk_size']))
    if command(env,'hyprctl','setcursor',saved['hypr_theme'],str(saved['hypr_size'])) != 'ok':
        raise RuntimeError('cursor restoration refused; retain session for recovery')

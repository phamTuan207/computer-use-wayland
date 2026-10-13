"""Optional session-only real cursor theme with durable guardian restoration."""
import ast
import json
from pathlib import Path
import re
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
    if not isinstance(theme,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',theme):
        raise ValueError('invalid cursor theme name')
    if type(size) is not int or not 16 <= size <= 96:
        raise ValueError('cursor size must be 16..96')


def gtk_state(env):
    """The two current GTK cursor values, validated. Shared by snapshot and the login loader."""
    theme = ast.literal_eval(command(env,'gsettings','get',SCHEMA,'cursor-theme'))
    size = int(command(env,'gsettings','get',SCHEMA,'cursor-size'))
    validate(theme,size)
    return theme,size


def snapshot(env):
    if not PROFILE.is_file():return None
    profile = json.loads(PROFILE.read_text())
    if not isinstance(profile,dict):raise ValueError('cursor profile must be an object')
    validate(profile['theme'],profile['size'])
    mode = profile.get('restore_mode')
    if mode is not None:
        raise ValueError('unknown restore_mode: '+repr(mode))
    validate(profile['restore_theme'],profile['restore_size'])
    theme,size = gtk_state(env)
    return {'gtk_theme':theme,'gtk_size':size,'hypr_theme':profile['restore_theme'],
            'hypr_size':profile['restore_size'],'agent_theme':profile['theme'],'agent_size':profile['size']}


def apply(env, theme, size):
    validate(theme,size)
    command(env,'gsettings','set',SCHEMA,'cursor-theme',theme)
    command(env,'gsettings','set',SCHEMA,'cursor-size',str(size))
    if command(env,'hyprctl','setcursor',theme,str(size)) != 'ok':
        raise RuntimeError('cursor theme dispatch refused')


def restore(env, saved):
    validate(saved['gtk_theme'],saved['gtk_size'])
    validate(saved['hypr_theme'],saved['hypr_size'])
    command(env,'gsettings','set',SCHEMA,'cursor-theme',saved['gtk_theme'])
    command(env,'gsettings','set',SCHEMA,'cursor-size',str(saved['gtk_size']))
    if command(env,'hyprctl','setcursor',saved['hypr_theme'],str(saved['hypr_size'])) != 'ok':
        raise RuntimeError('cursor restoration refused; retain session for recovery')

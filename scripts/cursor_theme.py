"""Optional session-only real cursor theme with durable guardian restoration."""
import ast
import json
from pathlib import Path
import re
import subprocess

PROFILE = Path(__file__).resolve().parents[1] / 'native/agent-cursor.json'
SCHEMA = 'org.gnome.desktop.interface'


def command(env, *args):
    return subprocess.check_output(list(args), env=env, text=True, stderr=subprocess.STDOUT, timeout=5).strip()


def validate(theme, size):
    if not isinstance(theme,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',theme):
        raise ValueError('invalid cursor theme name')
    if type(size) is not int or not 16 <= size <= 96:
        raise ValueError('cursor size must be 16..96')


def snapshot(env):
    if not PROFILE.is_file():return None
    profile = json.loads(PROFILE.read_text())
    validate(profile['theme'],profile['size'])
    validate(profile['restore_theme'],profile['restore_size'])
    theme = ast.literal_eval(command(env,'gsettings','get',SCHEMA,'cursor-theme'))
    size = int(command(env,'gsettings','get',SCHEMA,'cursor-size'))
    validate(theme,size)
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

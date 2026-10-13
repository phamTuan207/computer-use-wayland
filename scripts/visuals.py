#!/usr/bin/env python3
"""Fresh-login loader for the default visuals manifest.

Validates a manifest before any RPC, then hands off to the existing
activate-glass helper, which owns the ABI, plugin-inventory and profile checks.
Only that helper performs activation; this loader never unloads or reloads plugins.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import subprocess
import tempfile
import cursor_theme
import cursor_session

ROOT = Path(__file__).resolve().parents[1]
OPTICS = ROOT / 'native/hyprglass-local-optics.lua'
DEFAULT_MANIFEST = ROOT / 'native/visuals.json'
REQUIRED = ('abi', 'library', 'profile_sha256', 'setup_instance')
ACTIVATE = ROOT / 'scripts/activate-glass.py'
PROC = Path('/proc')


def atomic_write(path, data):
    """Replace one file atomically, refusing to follow a symlink or write a device."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError('refusing to write through a symlink')
    if path.exists() and not path.is_file():
        raise ValueError('refusing to replace a non-regular file')
    mode = path.stat().st_mode & 0o777 if path.is_file() else 0o600
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.visuals-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def _activate(library, abi, env):
    """Run the existing helper by path; its own guards are the only activation path."""
    namespace = runpy.run_path(str(ACTIVATE), run_name='activate_glass')
    namespace['activate'](library, abi, env, before_load=lambda:require_fresh_login(env))
    return True


def require_fresh_login(env):
    """Check process age too: a different instance alone can still be an old login."""
    try:
        rows=json.loads(subprocess.check_output(['hyprctl','-j','instances'],env=env,text=True,timeout=5))
        matches=[r for r in rows if r.get('instance')==env.get('HYPRLAND_INSTANCE_SIGNATURE')]
        if len(matches)!=1 or type(matches[0].get('pid')) is not int or matches[0]['pid']<=0:
            raise ValueError('invalid instance inventory')
        fields=(PROC/str(matches[0]['pid'])/'stat').read_text().rsplit(')',1)[1].split()
        age=float((PROC/'uptime').read_text().split()[0])-int(fields[19])/os.sysconf('SC_CLK_TCK')
    except (OSError,ValueError,TypeError,IndexError,KeyError,AttributeError,subprocess.SubprocessError) as exc:
        raise RuntimeError('cannot verify fresh compositor startup') from exc
    if not 0<=age<=30:
        raise RuntimeError('visuals can only load during the first 30 seconds of a fresh login')


def login(manifest, env):
    """Exclude task sessions for the entire activation and cursor-baseline update."""
    if env.get('CU_SESSION_TOKEN') or os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('refusing to load visuals inside an automation session')
    with cursor_session.owner_lock():
        if cursor_session.SNAPSHOT.exists():
            raise RuntimeError('finish or recover the retained session before loading visuals')
        return _login(manifest, env)


def _login(manifest, env):
    """Validate before calling the existing guarded activation helper."""
    if env.get('CU_SESSION_TOKEN') or os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('refusing to load visuals inside an automation session')
    manifest = json.loads(Path(manifest).read_text())
    if not isinstance(manifest, dict):raise ValueError('manifest must be an object')
    version = manifest.get('version')
    if type(version) is not int or version != 1:
        raise ValueError('manifest version must be exactly the integer 1')
    missing = [key for key in REQUIRED if not isinstance(manifest.get(key), str) or not manifest[key]]
    if missing:
        raise ValueError('manifest missing required strings: ' + ', '.join(missing))
    if not Path(manifest['library']).is_absolute():raise ValueError('library path must be absolute')
    library = Path(manifest['library']).resolve(strict=True)
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    if library.name != 'hyprglass-' + digest + '.so':
        raise ValueError('library must carry its own SHA256 in the filename')
    if manifest['profile_sha256'] != hashlib.sha256(OPTICS.read_bytes()).hexdigest():
        raise ValueError('profile does not match the pinned optics source')
    instance = (env.get('HYPRLAND_INSTANCE_SIGNATURE') or '').strip()
    if not instance:
        raise RuntimeError('no compositor instance in this environment')
    if instance == manifest['setup_instance']:
        raise RuntimeError('already inside the login that set this up; refusing to reload')
    if cursor_theme.PROFILE.is_symlink() or not cursor_theme.PROFILE.is_file():
        raise ValueError('cursor profile must be a regular file')
    raw=cursor_theme.PROFILE.read_bytes()
    profile=json.loads(raw)
    if not isinstance(profile,dict):raise ValueError('cursor profile must be an object')
    cursor_theme.validate(profile['theme'],profile['size'])
    mode=profile.get('restore_mode')
    if mode not in (None,'gtk'):raise ValueError('unknown cursor restoration policy')
    if mode=='gtk':
        directory=Path(manifest['cursor_directory'])
        if not directory.is_absolute() or directory.is_symlink() or not directory.is_dir():
            raise ValueError('managed cursor directory is unavailable')
        if directory.parent.resolve() not in cursor_theme.search_roots(env):
            raise ValueError('managed cursor is outside the Xcursor search path')
        digest_tree=runpy.run_path(str(ROOT/'scripts/build-cursor.py'))['tree_digest'](directory)
        if digest_tree!=manifest['cursor_tree_sha256'] or profile['theme']!='cu-agent-'+digest_tree or directory.name!=profile['theme']:
            raise ValueError('managed cursor tree differs from setup')
        theme,size=cursor_theme.gtk_state(env)
    else:
        cursor_theme.validate(profile['restore_theme'],profile['restore_size'])
    _activate(str(library), manifest['abi'], env)
    if mode=='gtk':
        if cursor_theme.command(env,'hyprctl','setcursor',theme,str(size))!='ok':
            raise RuntimeError('managed cursor baseline refused')
        if cursor_theme.PROFILE.read_bytes()!=raw:raise RuntimeError('cursor profile changed during login')
        profile['ready_instance']=instance
        atomic_write(cursor_theme.PROFILE,json.dumps(profile).encode())
    return {'ok': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, nargs='?', default=DEFAULT_MANIFEST)
    arguments = parser.parse_args()
    try:
        import cu
        print(json.dumps(login(arguments.manifest, cu.environment())))
    except Exception as exc:
        print('visuals: ' + str(exc), file=sys.stderr)
        sys.exit(1)

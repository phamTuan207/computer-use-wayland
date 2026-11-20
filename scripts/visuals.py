#!/usr/bin/env python3
"""Fresh-login loader for the default visuals manifest.

Validates a manifest before any RPC, then hands off to the existing
activate-glass helper, which owns the ABI, plugin-inventory and profile checks.
After its one normal reload, this loader starts the cursor guard and a temporary
indicator overlay so first-use shader compilation can finish before readiness checks.
This loader never unloads or reloads plugins itself.
"""
import argparse
import hashlib
import json
import jsonlutil
import os
from pathlib import Path
import re
import runpy
import stat
import sys
import subprocess
import tempfile
import time


def _capture_spawn_stderr():
    try:
        if Path(sys.argv[0]).resolve() != Path(__file__).resolve():
            return
        directory = Path.home()/'.cache/agent-computer-use/logs'
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if directory.is_symlink():
            return
        directory.chmod(0o700)
        path = directory/'visuals-stderr.log'
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                return
            os.fchmod(fd, 0o600)
            os.dup2(fd, sys.stderr.fileno())
        finally:
            os.close(fd)
    except (OSError, ValueError, TypeError, AttributeError):
        pass


def _write_spawn_log():
    try:
        if Path(sys.argv[0]).resolve() != Path(__file__).resolve():
            return
        directory = Path.home()/'.cache/agent-computer-use/logs'
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        record = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  'pid': os.getpid(), 'argv': sys.argv}
        jsonlutil.append_jsonl(directory / 'visuals-spawn.jsonl', record)
    except Exception:
        pass


def _log_supplied_compositor_tuple():
    try:
        if Path(sys.argv[0]).resolve() != Path(__file__).resolve():
            return
        keys = ('XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'HYPRLAND_INSTANCE_SIGNATURE')
        supplied = {key: os.environ.get(key) for key in keys}
        print('visuals: supplied compositor tuple: ' +
              json.dumps(supplied, sort_keys=True, separators=(',', ':')), file=sys.stderr)
    except Exception:
        pass


_capture_spawn_stderr()
_write_spawn_log()
_log_supplied_compositor_tuple()

import cursor_theme
import cursor_session
import activation_checks
import indicator

ROOT = Path(__file__).resolve().parents[1]
OPTICS = ROOT / 'native/hyprglass-local-optics.lua'
DEFAULT_MANIFEST = ROOT / 'native/visuals.json'
REQUIRED = ('abi', 'library', 'profile_sha256', 'setup_instance')
ACTIVATE = ROOT / 'scripts/activate-glass.py'
ACTIVATE_GUARD = ROOT / 'scripts/activate-cursor-guard.py'
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


def _activate(library, abi, profile_sha256, env, *, freshness=None, after_reload=None):
    """Run the existing helper by path; its own guards are the only activation path."""
    namespace = runpy.run_path(str(ACTIVATE), run_name='activate_glass')
    namespace['activate'](library, abi, profile_sha256, env,
                         before_load=lambda:require_fresh_login(env, ticket=freshness),
                         after_reload=after_reload)
    return True


def _activate_cursor_guard(library, abi, env, *, freshness=None):
    """Run root's guard helper by path; it must never unload or reload plugins."""
    namespace = runpy.run_path(str(ACTIVATE_GUARD), run_name='activate_cursor_guard')
    namespace['activate'](library, abi, env,
                         before_load=lambda:require_fresh_login(env, ticket=freshness))
    return True


def _compositor_freshness(env):
    """Return the exact compositor process identity and its monotonic age."""
    try:
        rows=json.loads(subprocess.check_output(['hyprctl','-j','instances'],env=env,text=True,timeout=5))
        instance=(env.get('HYPRLAND_INSTANCE_SIGNATURE') or '').strip()
        matches=[r for r in rows if r.get('instance')==instance]
        if len(matches)!=1 or type(matches[0].get('pid')) is not int or matches[0]['pid']<=0:
            raise ValueError('invalid instance inventory')
        pid=matches[0]['pid']
        fields=(PROC/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
        start_ticks=int(fields[19])
        uptime=float((PROC/'uptime').read_text().split()[0])
        boot_id=(PROC/'sys/kernel/random/boot_id').read_text().strip()
        if not instance or start_ticks<0 or not boot_id:
            raise ValueError('invalid compositor process identity')
        age=uptime-start_ticks/os.sysconf('SC_CLK_TCK')
    except (OSError,ValueError,TypeError,IndexError,KeyError,AttributeError,subprocess.SubprocessError) as exc:
        raise RuntimeError('cannot verify fresh compositor startup') from exc
    return (instance,pid,start_ticks,boot_id),age


def require_fresh_login(env, ticket=None):
    """Accept only a loader started in the first 30 seconds of this compositor.

    Later pre-load checks use the returned ticket to prove that the compositor
    is still the same process, even if startup validation itself took longer.
    """
    identity,age=_compositor_freshness(env)
    if ticket is None:
        if not 0<=age<=30:
            raise RuntimeError('visuals can only start during the first 30 seconds of a fresh login')
        return identity
    if identity!=ticket:
        raise RuntimeError('compositor changed after fresh login was accepted')
    if age<0:
        raise RuntimeError('visuals can only load during the first 30 seconds of a fresh login')
    return ticket


def _loader_log(progress, env, error=None):
    """Append one private, bounded loader record; never log tokens or image paths."""
    try:
        state = Path(cursor_session.STATE)
        if state.is_symlink():
            return
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        state.chmod(0o700)
        directory = state/'logs'
        if directory.is_symlink():
            return
        directory.mkdir(mode=0o700, exist_ok=True)
        directory.chmod(0o700)
        path = directory/'visuals.jsonl'
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                return
            os.fchmod(fd, 0o600)
            failure = None
            if error is not None:
                message = str(error).splitlines()[0][:240]
                for token in (env.get('CU_SESSION_TOKEN'), os.environ.get('CU_SESSION_TOKEN')):
                    if token:
                        message = message.replace(token, '[redacted]')
                message = re.sub(r'(?i)\b[0-9a-f]{32}\b', '[redacted]', message)
                message = re.sub(r'(?<![\w:])/(?:[^\s"\']+)', '[path]', message)
                message = re.sub(r'\b[^\s]+\.(?:png|jpe?g|webp|bmp|gif)\b', '[image]', message,
                                 flags=re.IGNORECASE)
                failure = type(error).__name__ + ': ' + message
            record = {
                'time': time.time(),
                'stage': progress.get('stage', 'unknown'),
                'instance': progress.get('instance'),
                'artifact_sha256': progress.get('artifact_sha256'),
                'glass_sha256': progress.get('glass_sha256'),
                'cursor_guard_sha256': progress.get('cursor_guard_sha256'),
                'failure': failure,
            }
            raw = (json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode()
            if info.st_size + len(raw) > 1024*1024:
                return
            view = memoryview(raw)
            while view:
                view = view[os.write(fd, view):]
            os.fsync(fd)
        finally:
            os.close(fd)
    except (OSError, ValueError, TypeError):
        pass


def login(manifest, env):
    """Exclude task sessions for the entire backend activation."""
    progress = {'stage': 'session_guard',
                'instance': (env.get('HYPRLAND_INSTANCE_SIGNATURE') or '').strip() or None,
                'artifact_sha256': None, 'glass_sha256': None,
                'cursor_guard_sha256': None}
    try:
        if env.get('CU_SESSION_TOKEN') or os.environ.get('CU_SESSION_TOKEN'):
            raise RuntimeError('refusing to load visuals inside an automation session')
        progress['stage'] = 'fresh_login_gate'
        freshness=require_fresh_login(env)
        progress['stage'] = 'session_lock'
        with cursor_session.owner_lock():
            if cursor_session.SNAPSHOT.exists():
                raise RuntimeError('finish or recover the retained session before loading visuals')
            result = _login(manifest, env, progress, freshness=freshness)
        _loader_log(progress, env)
        return result
    except Exception as error:
        _loader_log(progress, env, error)
        raise


def _login(manifest, env, progress=None, *, freshness=None):
    """Validate before calling the existing guarded activation helper."""
    progress = progress if progress is not None else {}
    if freshness is None:
        freshness=require_fresh_login(env)
    progress['stage'] = 'manifest_validation'
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
    progress['glass_sha256'] = digest
    progress['artifact_sha256'] = digest
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
    if profile.get('restore_mode') is not None:
        raise ValueError('explicit cursor restoration values are required')
    cursor_theme.validate(profile['restore_theme'],profile['restore_size'])
    directory=Path(manifest['cursor_directory']) if 'cursor_directory' in manifest else None
    if directory is not None and profile['theme']==directory.name:
        if not directory.is_absolute() or directory.is_symlink() or not directory.is_dir():
            raise ValueError('cursor directory is unavailable')
        if directory.parent.resolve() not in cursor_theme.search_roots(env):
            raise ValueError('cursor is outside the Xcursor search path')
        digest_tree=runpy.run_path(str(ROOT/'scripts/build-cursor.py'))['tree_digest'](directory)
        if digest_tree!=manifest['cursor_tree_sha256'] or profile['theme']!='cu-agent-'+digest_tree or directory.name!=profile['theme']:
            raise ValueError('cursor tree differs from setup')
    guard = _validated_guard_library(manifest)
    guard_digest = hashlib.sha256(guard.read_bytes()).hexdigest()
    progress['cursor_guard_sha256'] = guard_digest
    progress['stage'] = 'glass_first_load'
    progress['artifact_sha256'] = digest
    def after_reload():
        progress['stage'] = 'cursor_guard_first_load'
        progress['artifact_sha256'] = guard_digest
        _activate_cursor_guard(str(guard), manifest['abi'], env, freshness=freshness)
        progress['stage'] = 'indicator_shader_warmup'
        progress['artifact_sha256'] = digest
        overlay = indicator.Native(env)
        try:
            if overlay.process.poll() is not None:
                raise RuntimeError('indicator exited during shader warm-up')
        finally:
            overlay.close()

    _activate(str(library), manifest['abi'], manifest['profile_sha256'], env,
              freshness=freshness, after_reload=after_reload)
    progress['stage'] = 'final_glass_verification'
    progress['artifact_sha256'] = digest
    activation_checks.wait_for_profile(env)
    progress['stage'] = 'complete'
    return {'ok': True}


def _validated_guard_library(manifest):
    """The native cursor backend: an absolute immutable hash-named library.

    Old manifests without it fail closed with setup guidance, never silently.
    """
    value = manifest.get('cursor_guard_library')
    if not isinstance(value, str) or not value:
        raise ValueError('cursor guard backend missing from manifest; re-run setup to install it')
    if not Path(value).is_absolute():
        raise ValueError('cursor guard library path must be absolute')
    if Path(value).is_symlink():
        raise ValueError('cursor guard library must be a regular file, not a symlink')
    library = Path(value).resolve(strict=True)
    if not library.is_file():
        raise ValueError('cursor guard library must be a regular file')
    digest = hashlib.sha256(library.read_bytes()).hexdigest()
    if library.name != 'cursor-guard-' + digest + '.so':
        raise ValueError('cursor guard library must carry its own SHA256 in the filename')
    return library


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

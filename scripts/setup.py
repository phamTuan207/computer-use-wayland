#!/usr/bin/env python3
"""Prepare the default visuals: prove the header ABI, build them, install a login hook.

The whole default setup. It prepares the overlay, cursor and liquid glass and stops
there: activation needs a fresh login, so nothing here loads a plugin, changes the
running cursor or explicitly reloads the compositor. Saving the startup hook may
trigger the compositor's normal config reload; the hook activates only at startup.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import runpy
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile

from visuals import atomic_write

ROOT = Path(__file__).resolve().parents[1]
ICON_DIRECTORY = Path.home()/'.local/share/icons'
GLASS_REPO = 'https://github.com/hyprnux/hyprglass.git'
GLASS_PIN = '84c1a5ab217101a317d4edaab7fba2efcc1bf346'
PREREQUISITES = ('cc', 'c++', 'pkg-config', 'wayland-scanner', 'rsvg-convert', 'make',
                 'git', 'hyprctl', 'gsettings', 'grim', 'wtype')

REQUIRED_HYPRLAND = '0.56.2'
MACROS = ('GIT_COMMIT_HASH', 'AQUAMARINE_VERSION', 'HYPRUTILS_VERSION',
          'HYPRGRAPHICS_VERSION', 'HYPRCURSOR_VERSION', 'HYPRLANG_VERSION')
MACRO = re.compile(r'^#define (' + '|'.join(MACROS) + r') "([^"]*)"$', re.M)
HOOK_BEGIN = '-- computer-use-visuals-begin'
HOOK_END = '-- computer-use-visuals-end'


def _strip_patch(version):
    """Everything before the rightmost dot; an undotted version is unchanged."""
    return version[:version.rfind('.')] if '.' in version else version


def header_abi(env):
    """Reconstruct the pinned client hash from the installed headers.

    Preprocessing only: no linking, no execution of plugin code. The version is a
    bound, not proof - the caller must still compare this with the running ABI.
    """
    def pkg(*args):
        return subprocess.check_output(['pkg-config', *args], env=env, text=True,
                                        stderr=subprocess.DEVNULL, timeout=30).strip()
    version = pkg('--modversion', 'hyprland')
    if version != REQUIRED_HYPRLAND:
        raise RuntimeError(f'hyprland {REQUIRED_HYPRLAND} required, found {version or "none"}')
    flags = shlex.split(pkg('--cflags', 'hyprland'))
    argv = ['c++', '-std=c++23', '-dM', '-E', '-x', 'c++',
            '-include', 'hyprland/src/plugins/PluginAPI.hpp', '-', *flags]
    output = subprocess.check_output(argv, env=env, input='', text=True, timeout=30,
                                     stderr=subprocess.DEVNULL)
    found = dict(MACRO.findall(output))
    missing = [name for name in MACROS if not found.get(name)]
    if missing:
        raise RuntimeError('preprocessor did not define: ' + ', '.join(missing))
    values = [found['GIT_COMMIT_HASH']] + [_strip_patch(found[name]) for name in MACROS[1:]]
    return values[0] + ''.join(f'_{tag}_{value}'
                               for tag, value in zip(('aq', 'hu', 'hg', 'hc', 'hlg'), values[1:]))


def _hook_body(command):
    # JSON quoting keeps the command inside one Lua string literal; the command
    # itself is already shlex-escaped by the caller.
    return (f'hl.on("hyprland.start",function() hl.exec_cmd({json.dumps(command, ensure_ascii=False)}) end)')


def install_hook(config_path, command, hook_path, check_only=False):
    """Append one managed block to a config and point it at a separate hook file.

    Never executes anything, never replaces a user edit, and only ever appends.
    """
    if any(ord(c)<32 for value in (str(config_path), str(hook_path), command) for c in value):
        raise ValueError('startup paths and command cannot contain control characters')
    config_path = Path(config_path)
    if config_path.is_symlink() or not config_path.is_file():
        raise ValueError('config must be an existing regular file')
    hook_path = Path(hook_path)
    if hook_path.is_symlink() or (hook_path.exists() and not hook_path.is_file()):
        raise ValueError('hook path must be a regular file')
    hook = _hook_body(command) + '\n'
    if hook_path.is_file() and hook_path.read_bytes() != hook.encode():
        raise ValueError('refusing to overwrite a hook file this tool does not own')
    original = config_path.read_bytes()
    text = original.decode('utf-8')
    if '\0' in text or any(ord(c) < 32 and c not in '\n\t\r' for c in text):
        raise ValueError('config must be UTF-8 text without control characters')
    begins = [line for line in text.splitlines() if line.strip() == HOOK_BEGIN]
    ends = [line for line in text.splitlines() if line.strip() == HOOK_END]
    if len(begins) > 1 or len(ends) > 1:
        raise ValueError('config already has more than one managed block')
    if begins or ends:
        if not (begins and ends) or text.index(HOOK_BEGIN) > text.index(HOOK_END):
            raise ValueError('managed block markers are malformed')
        block = _managed_block(hook_path)
        if block not in text:
            raise ValueError('config has an edited managed block; refusing to replace it')
        missing = not hook_path.is_file()
        if check_only:
            # Same validation as a real run, on every branch, and no write at all.
            return {'ok': True, 'changed': missing}
        if missing:
            atomic_write(hook_path, hook.encode())
        return {'ok': True, 'changed': missing}
    if check_only:
        return {'ok': True, 'changed': True}
    block = _managed_block(hook_path)
    updated = text + ('' if text.endswith('\n') or not text else '\n') + block
    digest = hashlib.sha256(original).hexdigest()[:16]
    backup = config_path.with_name(config_path.name + '.bak-' + digest)
    if backup.is_symlink() or (backup.exists() and (not backup.is_file() or backup.read_bytes()!=original)):
        raise ValueError('existing config backup differs; refusing to overwrite')
    if not backup.exists():
        # Exclusive create: an existing file with different bytes is never touched.
        with open(backup, 'xb', opener=lambda p, flags:os.open(p, flags, 0o600)) as stream:
            stream.write(original);stream.flush();os.fsync(stream.fileno())
        backup.chmod(stat.S_IMODE(config_path.stat().st_mode))
    if not hook_path.is_file():
        atomic_write(hook_path, hook.encode())
    # Recheck after every other write, so an edit made while we worked still wins.
    if config_path.read_bytes() != original:
        raise RuntimeError('config changed underneath us; refusing to write')
    atomic_write(config_path, updated.encode())
    return {'ok': True, 'changed': True, 'backup': backup.name}


def _run(argv, **kwargs):
    """One external command: argument list, no shell, bounded output."""
    kwargs.setdefault('timeout', 900)
    return subprocess.run(argv, shell=False, capture_output=True, text=True, **kwargs)



def _checked(argv, **kwargs):
    result = _run(argv, **kwargs)
    if result.returncode:
        raise RuntimeError(f'{argv[0]} failed: ' + (result.stderr or result.stdout).strip()[:200])
    return result


def runtime_abi(env):
    """Read the running compositor ABI, rejecting malformed JSON shapes cleanly."""
    try:
        response = json.loads(_checked(['hyprctl', '-j', 'version'], env=env).stdout)
    except (json.JSONDecodeError, TypeError) as error:
        raise RuntimeError('invalid compositor ABI response: malformed JSON') from error
    if not isinstance(response, dict):
        raise RuntimeError('invalid compositor ABI response: expected object')
    if 'abiHash' not in response:
        raise RuntimeError('invalid compositor ABI response: missing abiHash')
    if not isinstance(response['abiHash'], str):
        raise RuntimeError('invalid compositor ABI response: abiHash must be a string')
    if not response['abiHash']:
        raise RuntimeError('invalid compositor ABI response: empty abiHash')
    return response['abiHash']


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _preflight(env, config_path, data_dir, bin_dir, restore_theme=None, restore_size=None):
    """Everything that can refuse, before a single build or write happens."""
    if env.get('CU_SESSION_TOKEN') or os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('setup refuses to run inside an automation session')
    import cursor_session
    if cursor_session.SNAPSHOT.exists():
        raise RuntimeError('a retained session record exists; recover it before setup')
    if not (env.get('HYPRLAND_INSTANCE_SIGNATURE') or '').strip():
        raise RuntimeError('setup needs a running Hyprland compositor')
    for name in PREREQUISITES:
        if shutil.which(name, path=env.get('PATH')) is None:
            raise RuntimeError('missing prerequisite: ' + name)
    if importlib.util.find_spec('PIL') is None:
        raise RuntimeError('Pillow is required')
    if config_path.is_symlink() or not config_path.is_file():
        raise ValueError('config must be an existing regular file')
    link = Path(bin_dir) / 'computer-use'
    if link.exists() or link.is_symlink():
        if not link.is_symlink() or link.resolve() != (ROOT/'scripts/cu.py').resolve():
            raise ValueError('an existing computer-use link is not ours; refusing to replace it')
    import cursor_theme
    owned = {'native/visuals.json': ROOT/'native/visuals.json',
             'native/require-liquid': ROOT/'native/require-liquid',
             'native/visuals-login.lua': ROOT/'native/visuals-login.lua',
             'native/agent-cursor.json': cursor_theme.PROFILE}
    for name, path in owned.items():
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f'{name} must be a regular file')
    # Both the existing profile and the requested declaration are settled before the
    # library probe, the header check and the build, so a refusal costs nothing.
    profile, profile_bytes = _validate_profile(cursor_theme.PROFILE)
    requested = _requested_restore(profile, restore_theme, restore_size)
    if ICON_DIRECTORY.resolve() not in cursor_theme.search_roots(env):
        raise RuntimeError('Xcursor search path excludes the user icon directory; check XCURSOR_PATH')
    hook = _hook_command()
    install_hook(config_path, hook, ROOT/'native/visuals-login.lua', check_only=True)
    initial = header_abi(env)
    if initial != runtime_abi(env):
        raise RuntimeError('header ABI does not match the running compositor')
    _require_no_plugins(env)
    return initial, requested, profile_bytes


def _hook_command():
    """The exact command both the preflight check and the published hook use."""
    return shlex.join([sys.executable, str(ROOT/'scripts/visuals.py'),
                       str(ROOT/'native/visuals.json')])


def _require_no_plugins(env):
    loaded = json.loads(_checked(['hyprctl', '-j', 'plugin', 'list'], env=env).stdout)
    if not isinstance(loaded, list):
        raise RuntimeError('invalid plugin inventory')
    if loaded:
        raise RuntimeError('plugins are already loaded; a config reload could affect them')


def _validate_profile(path):
    """Validate an existing profile without touching it; retain its exact bytes."""
    import cursor_theme
    if not path.is_file():
        return None, None
    raw = path.read_bytes()
    try:
        profile = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError('cursor profile is not valid JSON') from error
    if not isinstance(profile, dict):
        raise ValueError('cursor profile must be a JSON object')
    try:
        cursor_theme.validate(profile['theme'], profile['size'])
    except KeyError as error:
        raise ValueError('cursor profile is missing theme or size') from error
    if profile.get('restore_mode') is not None:
        # The GTK baseline was an unpublished experiment, not a compatibility need.
        raise ValueError('this setup only supports an explicit manual restore declaration; '
                         'remove restore_mode from native/agent-cursor.json')
    try:
        cursor_theme.validate(profile['restore_theme'], profile['restore_size'])
    except KeyError as error:
        raise ValueError('cursor profile is missing restore_theme or restore_size') from error
    return profile, raw


def _requested_restore(profile, restore_theme, restore_size):
    """The manual restore declaration to store, or None when a profile already holds one.

    There is no way to read the compositor's previous cursor back, so a new profile
    must be told the exact values by the user. Nothing here ever guesses them.
    """
    import cursor_theme
    given = (restore_theme, restore_size)
    if (restore_theme is None) != (restore_size is None):
        raise ValueError('a new cursor profile needs both --restore-theme and --restore-size')
    if profile is None and restore_theme is None:
        raise ValueError('a new cursor profile needs both --restore-theme and --restore-size; '
                         'the previous Hyprland cursor cannot be read back')
    if profile is not None:
        if restore_theme is None:
            return None                       # the existing declaration is authoritative
        current = (profile['restore_theme'], profile['restore_size'])
        if given != current:
            raise ValueError(f'the existing cursor profile already declares {current[0]} / '
                             f'{current[1]}; refusing to overwrite it with {restore_theme} / {restore_size}')
        return None
    try:
        cursor_theme.validate(restore_theme, restore_size)
    except ValueError as error:
        raise ValueError('invalid restore declaration: ' + str(error)) from error
    return given


def setup(config_path, data_dir, bin_dir, restore_theme=None, restore_size=None):
    """Prepare the default visuals. Publishes the manifest last; never activates."""
    import cursor_session
    if os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('setup refuses to run inside an automation session')
    # Hold the session lock for the whole run so an automation cannot start mid-build.
    with cursor_session.owner_lock():
        if cursor_session.SNAPSHOT.exists():
            raise RuntimeError('a retained session record exists; recover it before setup')
        return _setup(config_path, data_dir, bin_dir, restore_theme, restore_size)


def _setup(config_path, data_dir, bin_dir, restore_theme=None, restore_size=None):
    import cursor_session
    import cursor_theme
    import cu
    env = cu.environment()
    config_path = Path(config_path)
    data_dir, bin_dir = Path(data_dir).resolve(), Path(bin_dir).resolve()
    if env.get('CU_SESSION_TOKEN'):
        raise RuntimeError('setup refuses to run inside an automation session')
    initial, requested, profile_bytes = _preflight(env, config_path, data_dir, bin_dir,
                                                   restore_theme, restore_size)
    with tempfile.TemporaryDirectory(prefix='cu-setup-') as folder:
        owned = Path(folder)
        source = owned/'hyprglass'
        _checked(['git', 'clone', '--no-checkout', '--depth', '1', GLASS_REPO, str(source)], env=env)
        _checked(['git', '-C', str(source), 'fetch', '--depth', '1', 'origin', GLASS_PIN], env=env)
        _checked(['git', '-C', str(source), 'checkout', '--detach', GLASS_PIN], env=env)
        _checked([sys.executable, str(ROOT/'scripts/build.py')], env=env)
        # build-glass prints a human diagnostic; the artefact is at a known path.
        _checked([sys.executable, str(ROOT/'scripts/build-glass.py'), str(source),
                  '--local-optics'], env=env)
        library = source/'hyprglass.so'
        if header_abi(env) != initial or runtime_abi(env) != initial:
            raise RuntimeError('ABI drifted during the build')
        # Recheck the runtime before the first write, not after: once anything is
        # installed the honest message is "aborted", never "nothing was published".
        _require_no_plugins(env)
        if cursor_session.SNAPSHOT.exists():
            raise RuntimeError('a session started during setup; '
                               'aborted before anything was installed or published')
        profile_path = cursor_theme.PROFILE
        current_bytes = profile_path.read_bytes() if profile_path.is_file() else None
        if profile_path.is_symlink() or current_bytes != profile_bytes:
            raise RuntimeError('cursor profile changed during build; refusing to publish visuals')
        plugins = data_dir/'agent-computer-use/plugins'
        plugins.mkdir(parents=True, exist_ok=True)
        cursor = _load('build_cursor', ROOT/'scripts/build-cursor.py')
        theme, _existed = cursor.install(ICON_DIRECTORY)
        glass = _load('install_glass', ROOT/'scripts/install-glass.py')
        installed = glass.install(library, plugins)
        current_bytes = profile_path.read_bytes() if profile_path.is_file() else None
        if profile_path.is_symlink() or current_bytes != profile_bytes:
            raise RuntimeError('cursor profile changed during install; refusing to publish visuals')
        if requested is not None:
            declared = {'theme': theme.name, 'size': 34,
                        'restore_theme': requested[0], 'restore_size': requested[1]}
            with open(profile_path, 'xb', opener=lambda path, flags:os.open(path, flags, 0o600)) as stream:
                stream.write((json.dumps(declared, indent=2) + '\n').encode())
                stream.flush()
                os.fsync(stream.fileno())
        atomic_write(ROOT/'native/require-liquid', b'')
        install_hook(config_path, _hook_command(), ROOT/'native/visuals-login.lua')
        manifest = {'version': 1,
                    'abi': initial,
                    'library': str(Path(installed).resolve()),
                    'profile_sha256': hashlib.sha256((ROOT/'native/hyprglass-local-optics.lua').read_bytes()).hexdigest(),
                    'setup_instance': env['HYPRLAND_INSTANCE_SIGNATURE'],
                    'cursor_directory': str(theme.resolve()),
                    'cursor_tree_sha256': cursor.tree_digest(theme)}
        atomic_write(ROOT/'native/visuals.json', (json.dumps(manifest, indent=2) + '\n').encode())
        link = Path(bin_dir)/'computer-use'
        if not link.exists() and not link.is_symlink():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(ROOT/'scripts/cu.py')
    return {'ok': True, 'restart_required': True, 'cursor': 'automatic', 'liquid': 'prepared'}


def _managed_block(hook_path):
    return (f'{HOOK_BEGIN}\ndofile({json.dumps(str(hook_path), ensure_ascii=False)})\n{HOOK_END}\n')


def main(argv=None):
    default_data = Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hypr-config', type=Path,
                        default=Path(os.environ.get('XDG_CONFIG_HOME', Path.home()/'.config'))/'hypr/hyprland.lua')
    parser.add_argument('--data-dir', type=Path, default=default_data)
    parser.add_argument('--bin-dir', type=Path, default=Path.home()/'.local/bin')
    parser.add_argument('--restore-theme',
                        help='the cursor theme Hyprland used before this setup, e.g. Adwaita')
    parser.add_argument('--restore-size', type=int,
                        help='the cursor size Hyprland used before this setup, e.g. 24')
    arguments = parser.parse_args(argv)
    result = setup(arguments.hypr_config, arguments.data_dir, arguments.bin_dir,
                   arguments.restore_theme, arguments.restore_size)
    print(json.dumps(result))
    print('log out and back in to finish: the visuals are prepared, not active.')
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())

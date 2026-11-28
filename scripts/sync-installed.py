#!/usr/bin/env python3
"""Safely publish this checkout to the installed computer-use tree."""
import argparse
from contextlib import contextmanager
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import time
import uuid


MANAGED_DIRS = ('scripts', 'native', 'skill', 'tests', 'docs')
MANAGED_FILES = ('README.md', 'LICENSE')
GENERATED_FILES = (
    'native/visuals.json', 'native/visuals-login.lua', 'native/require-liquid',
    'native/agent-cursor.json',
    'native/pointer-protocol.c', 'native/pointer-protocol.h',
    'native/keyboard-protocol.c', 'native/keyboard-protocol.h',
    'native/presentation-protocol.c', 'native/presentation-protocol.h',
    'native/background-effect-protocol.c', 'native/background-effect-protocol.h',
    'native/keyboard-protocol.o', 'native/cursor-guard.so',
    'native/indicator', 'native/pointer', 'native/modifiers',
    'native/wtype',
)
BUILD_OUTPUTS = ('native/indicator', 'native/pointer', 'native/modifiers', 'native/wtype')
HISTORY_FILES = (
    'tests/latest-results.json',
    'docs/automation-cursor-design.md',
    'docs/browser-worker-performance.md',
    'docs/indicator-validation.md',
    'docs/local-optics.md',
    'docs/performance-report.md',
    'docs/research-performance.md',
    'docs/session-startup-report.md',
    'docs/wayland-optimization.md',
    'skill/references/validation.md',
    'CREW.md',
)
COLD_TESTS = ('tests/test_report_regressions.py', 'tests/test_session_takeover.py')
HAND_PATCH_BACKUPS = (
    'scripts/indicator.py.bak-20261116-pinfix',
    'native/indicator.bak-20261116',
)
GLASS_VERSION = '1.1.1-cu.1'
GLASS_COMMIT = '03a57c4451b4abee38feda2ffb725f55ecc0f2fd'
HYPRLAND_VERSION = '0.57.2'
FORMAT_VERSION = 1
SNAPSHOT_MARKER = 'computer-use-wayland/sync-installed.py'
BROKER_SOURCE = 'scripts/session_remote.py'


class SyncError(RuntimeError):
    pass


def _default_repo():
    candidate = Path(__file__).resolve().parents[1]
    if (candidate / '.git').exists():
        return candidate
    return Path.home() / 'computer-use-wayland'


def _defaults():
    data_home = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
    return _default_repo(), data_home / 'agent-computer-use'


def _resolve_roots(repo_arg=None, installed_arg=None):
    default_repo, default_installed = _defaults()
    repo = Path(repo_arg) if repo_arg is not None else default_repo
    installed = Path(installed_arg) if installed_arg is not None else default_installed
    if installed.expanduser().is_symlink():
        raise SyncError(f'installed root must not be a symlink: {installed}')
    repo = repo.expanduser().resolve(strict=True)
    installed = installed.expanduser().resolve()
    if not repo.is_dir():
        raise SyncError(f'repository is not a directory: {repo}')
    if repo == installed:
        raise SyncError('repo and installed roots resolve to the same directory')
    try:
        top = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'],
                                      text=True, stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SyncError(f'repository is not a usable git checkout: {repo}') from exc
    if Path(top).resolve() != repo:
        raise SyncError(f'--repo must be the git worktree root: {repo}')
    return repo, installed


def _cursor_session(repo):
    path = repo / 'scripts' / 'cursor_session.py'
    if not path.is_file() or path.is_symlink():
        raise SyncError(f'repository session lock module is missing or unsafe: {path}')
    name = '_sync_cursor_session_' + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def _session_lock(repo):
    if os.environ.get('CU_SESSION_TOKEN'):
        raise SyncError('CU_SESSION_TOKEN is set; refusing installed-tree sync')
    session = _cursor_session(repo)
    try:
        lock = session.owner_lock()
    except (OSError, RuntimeError) as exc:
        raise SyncError(str(exc)) from exc
    try:
        if session.SNAPSHOT.exists():
            raise SyncError(f'retained session record exists: {session.SNAPSHOT}')
        yield session
    finally:
        lock.close()


def _session_clear(session):
    if os.environ.get('CU_SESSION_TOKEN'):
        raise SyncError('CU_SESSION_TOKEN became set; refusing publication')
    if session.SNAPSHOT.exists():
        raise SyncError(f'retained session record appeared: {session.SNAPSHOT}')


def _managed_dir_check(root, require_exists=False):
    for name in MANAGED_DIRS:
        path = root / name
        if path.is_symlink():
            raise SyncError(f'managed directory must not be a symlink: {path}')
        if require_exists and not path.is_dir():
            raise SyncError(f'managed directory is missing: {path}')
        if path.exists() and not path.is_dir():
            raise SyncError(f'managed path is not a directory: {path}')
    for name in MANAGED_FILES:
        path = root / name
        if path.is_symlink():
            raise SyncError(f'managed file must not be a symlink: {path}')
        if path.exists() and not path.is_file():
            raise SyncError(f'managed path is not a regular file: {path}')


def _excluded_active(path):
    parts = PurePosixPath(path).parts
    base = parts[-1]
    if '.git' in parts or '__pycache__' in parts or '.commandcode' in parts:
        return True
    if base.endswith('.pyc') or base.endswith('.pyo') or base.endswith('.~1~'):
        return True
    if '.bak' in base:
        return True
    if parts[0] == 'native' and (base.startswith('hyprglass') and base.endswith('.so')):
        return True
    if parts[0] == 'native' and re.fullmatch(r'cursor-guard-[0-9a-fA-F]+\.so', base):
        return True
    return False


def _source_bundle(repo):
    try:
        raw = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z'],
                                      stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SyncError(f'git ls-files failed for {repo}') from exc
    tracked = set()
    for item in raw.decode().split('\0'):
        if not item:
            continue
        path = PurePosixPath(item)
        if len(path.parts) == 1 and item in MANAGED_FILES:
            tracked.add(item)
        elif path.parts and path.parts[0] in MANAGED_DIRS:
            tracked.add(item)
    paths = {name for name in tracked
             if not _excluded_active(name) and name not in HISTORY_FILES}
    for name in GENERATED_FILES:
        source = repo / name
        if source.exists() or source.is_symlink():
            paths.add(name)
    entries = {}
    for name in sorted(paths):
        path = repo / name
        if path.is_symlink():
            target = (path.parent / os.readlink(path)).resolve()
            if not target.is_relative_to(repo):
                raise SyncError(f'managed source symlink escapes repo: {name}')
            entries[name] = _metadata(path)
        elif path.is_file():
            entries[name] = _metadata(path)
        else:
            raise SyncError(f'managed source is missing or not a regular file: {path}')
    return entries


def _metadata(path):
    info = path.lstat()
    mode = stat.S_IMODE(info.st_mode)
    if stat.S_ISLNK(info.st_mode):
        return {'type': 'symlink', 'mode': mode, 'target': os.readlink(path)}
    if not stat.S_ISREG(info.st_mode):
        raise SyncError(f'unsupported managed file type: {path}')
    return {'type': 'file', 'mode': mode, 'sha256': _sha256(path)}


def _sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_entries(entries):
    raw = json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def _copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=False)


def _copy_tree(source, destination, ignore=None):
    shutil.copytree(source, destination, symlinks=True, copy_function=shutil.copy2,
                    ignore=ignore)


def _history_for_dir(directory):
    prefix = directory + '/'
    return tuple(name[len(prefix):] for name in HISTORY_FILES
                 if name.startswith(prefix))


def _copytree_without_history(source, destination, directory):
    skipped = set(_history_for_dir(directory))

    def ignore(current, names):
        relative = Path(current).relative_to(source).as_posix()
        ignored = []
        for name in names:
            item = ((relative + '/' if relative != '.' else '') + name).strip('/')
            if item in skipped:
                ignored.append(name)
        return ignored

    _copy_tree(source, destination, ignore=ignore)


def _snapshot_data_inventory(snapshot):
    roots = [snapshot / name for name in ('trees', 'preserved', 'top')]
    inventory = {}
    for root in roots:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            rel_dir = current_path.relative_to(snapshot).as_posix()
            inventory[rel_dir] = {'type': 'directory', 'mode': stat.S_IMODE(current_path.lstat().st_mode)}
            for name in list(dirs):
                path = current_path / name
                if path.is_symlink():
                    inventory[path.relative_to(snapshot).as_posix()] = _metadata(path)
                    dirs.remove(name)
            for name in files:
                path = current_path / name
                inventory[path.relative_to(snapshot).as_posix()] = _metadata(path)
    return inventory


def _write_json_atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temp.chmod(0o600)
    os.replace(temp, path)


def _create_snapshot(repo, installed, source_commit, source_digest):
    backups = installed / 'backups'
    if backups.is_symlink():
        raise SyncError(f'backup directory must not be a symlink: {backups}')
    backups.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f')
    snapshot = backups / f'sync-{stamp}-{uuid.uuid4().hex[:8]}'
    snapshot.mkdir(mode=0o700)
    trees = snapshot / 'trees'
    trees.mkdir()
    present_dirs = {}
    for name in MANAGED_DIRS:
        source = installed / name
        present_dirs[name] = source.is_dir()
        if source.is_dir():
            _copytree_without_history(source, trees / name, name)
    top = snapshot / 'top'
    top.mkdir()
    present_files = {}
    for name in MANAGED_FILES:
        source = installed / name
        present_files[name] = source.is_file()
        if source.is_file():
            _copy_file(source, top / name)
    preserved = snapshot / 'preserved'
    preserved.mkdir()
    preserved_present = {}
    for name in HISTORY_FILES:
        source = installed / name
        exists = source.is_file() and not source.is_symlink()
        preserved_present[name] = exists
        if source.exists() or source.is_symlink():
            if not exists:
                raise SyncError(f'history exception is not a regular file: {source}')
            _copy_file(source, preserved / name)
    cold_files = {name: (installed / name).is_file() and not (installed / name).is_symlink()
                  for name in COLD_TESTS}
    for name, exists in cold_files.items():
        if (installed / name).exists() and not exists:
            raise SyncError(f'cold-preserved test is not a regular file: {installed / name}')
    snapshot_manifest = {
        'installer': SNAPSHOT_MARKER,
        'format': FORMAT_VERSION,
        'repo_root': str(repo),
        'installed_root': str(installed),
        'source_commit': source_commit,
        'source_content_sha256': source_digest,
        'managed_dirs_present': present_dirs,
        'managed_files_present': present_files,
        'preserved_history_present': preserved_present,
        'cold_tests_present': cold_files,
        'hand_patch_backups': {
            name: (_metadata(snapshot / 'trees' / name)
                   if (snapshot / 'trees' / name).is_file() or
                   (snapshot / 'trees' / name).is_symlink() else None)
            for name in HAND_PATCH_BACKUPS
        },
        'cli_link': _cli_link_state(installed),
        'inventory': _snapshot_data_inventory(snapshot),
    }
    _write_json_atomic(snapshot / 'snapshot.json', snapshot_manifest)
    _verify_snapshot(snapshot, repo, installed)
    return snapshot, snapshot_manifest


def _verify_snapshot(snapshot, repo, installed):
    manifest_path = snapshot / 'snapshot.json'
    if snapshot.is_symlink() or manifest_path.is_symlink():
        raise SyncError(f'snapshot and manifest must not be symlinks: {snapshot}')
    allowed = {'snapshot.json', 'transaction.json', 'staging-evidence.json',
               'sync-failure.json', 'transaction', 'trees', 'preserved', 'top'}
    unknown = {path.name for path in snapshot.iterdir()} - allowed
    if unknown:
        raise SyncError(f'unknown data in sync snapshot: {snapshot / sorted(unknown)[0]}')
    for name in ('transaction.json', 'staging-evidence.json', 'sync-failure.json'):
        path = snapshot / name
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise SyncError(f'invalid snapshot metadata file: {path}')
    transaction = snapshot / 'transaction'
    if transaction.is_symlink() or (transaction.exists() and not transaction.is_dir()):
        raise SyncError(f'invalid snapshot transaction directory: {transaction}')
    for name in ('trees', 'preserved', 'top'):
        path = snapshot / name
        if path.is_symlink() or not path.is_dir():
            raise SyncError(f'invalid snapshot data directory: {path}')
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f'invalid sync snapshot manifest: {manifest_path}') from exc
    if (manifest.get('installer') != SNAPSHOT_MARKER or
            manifest.get('format') != FORMAT_VERSION or
            manifest.get('repo_root') != str(repo) or
            manifest.get('installed_root') != str(installed)):
        raise SyncError(f'unknown or nonmatching sync snapshot: {snapshot}')
    current = _snapshot_data_inventory(snapshot)
    if current != manifest.get('inventory'):
        raise SyncError(f'snapshot inventory does not match its manifest: {snapshot}')
    for name in MANAGED_DIRS:
        if manifest.get('managed_dirs_present', {}).get(name) not in (True, False):
            raise SyncError(f'snapshot lacks managed directory state for {name}')
    for name, expected in manifest.get('hand_patch_backups', {}).items():
        path = snapshot / 'trees' / name
        if expected is None:
            if path.exists() or path.is_symlink():
                raise SyncError(f'snapshot unexpectedly contains hand-patch backup: {name}')
        elif not path.exists() and not path.is_symlink():
            raise SyncError(f'snapshot is missing hand-patch backup: {name}')
        elif _metadata(path) != expected:
            raise SyncError(f'snapshot hand-patch backup differs from manifest: {name}')
    return manifest


def _copy_active_bundle(repo, installed, stage_root, entries):
    for name in MANAGED_DIRS:
        (stage_root / name).mkdir(parents=True, exist_ok=True)
    for name, source_meta in entries.items():
        src, dst = repo / name, stage_root / name
        if source_meta['type'] == 'symlink':
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(source_meta['target'])
        else:
            _copy_file(src, dst)


def _parse_assignment(path, names):
    import ast
    tree = ast.parse(path.read_text(), filename=str(path))
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            for target in targets:
                if isinstance(target, ast.Name) and target.id in names:
                    try:
                        result[target.id] = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
    return result


def _validate_pins(root):
    setup = _parse_assignment(root / 'scripts/setup.py', {'GLASS_PIN', 'REQUIRED_HYPRLAND'})
    glass = _parse_assignment(root / 'scripts/build-glass.py',
                               {'REQUIRED_COMMIT', 'REQUIRED_HYPRLAND', 'VERSION'})
    indicator = _parse_assignment(root / 'scripts/indicator.py', {'LIQUID_VERSION'})
    expected = (GLASS_VERSION, GLASS_COMMIT, HYPRLAND_VERSION)
    actual = (indicator.get('LIQUID_VERSION'), setup.get('GLASS_PIN'),
              setup.get('REQUIRED_HYPRLAND'), glass.get('VERSION'),
              glass.get('REQUIRED_COMMIT'), glass.get('REQUIRED_HYPRLAND'))
    target = (GLASS_VERSION, GLASS_COMMIT, HYPRLAND_VERSION,
              GLASS_VERSION, GLASS_COMMIT, HYPRLAND_VERSION)
    if actual != target:
        raise SyncError(f'glass/Hyprland pins disagree: found {actual}, required {target}')
    setup_text = (root / 'scripts/setup.py').read_text()
    if 'indicator.LIQUID_VERSION' not in setup_text:
        raise SyncError('setup.py no longer uses indicator.LIQUID_VERSION for glass readiness')
    return {'glass_version': expected[0], 'upstream_commit': expected[1],
            'hyprland_version': expected[2]}


def _validate_manifest(root, installed):
    path = root / 'native/visuals.json'
    if not path.is_file() or path.is_symlink():
        raise SyncError(f'visuals manifest is missing or unsafe: {path}')
    try:
        manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f'invalid visuals manifest: {path}') from exc
    for key, prefix in (('library', 'hyprglass-'),
                        ('cursor_guard_library', 'cursor-guard-')):
        value = manifest.get(key)
        if not isinstance(value, str):
            raise SyncError(f'visuals manifest lacks {key}')
        lib = Path(value)
        match = re.fullmatch(re.escape(prefix) + r'([0-9a-f]{64})\.so', lib.name)
        if not match or lib.parent.resolve() != (installed / 'plugins').resolve():
            raise SyncError(f'manifest {key} is not a hash-named installed plugin path: {value}')
        if lib.is_symlink() or not lib.is_file():
            raise SyncError(f'manifest plugin is missing or unsafe: {lib}')
        actual = _sha256(lib)
        if actual != match.group(1):
            raise SyncError(f'manifest {key} hash mismatch: expected {match.group(1)}, found {actual}')
    profile = root / 'native/hyprglass-local-optics.lua'
    profile_hash = _sha256(profile)
    if manifest.get('profile_sha256') != profile_hash:
        raise SyncError('visuals manifest profile_sha256 does not match hyprglass-local-optics.lua')
    return manifest


def _required_staged_files(root, installed):
    for name in ('scripts/activation_checks.py', 'scripts/plugin_inventory.py',
                 'scripts/session_remote.py', 'native/indicator.c',
                 'native/visuals.json', 'native/hyprglass-local-optics.lua'):
        if not (root / name).is_file():
            raise SyncError(f'required staged source is missing: {name}')
    pins = _validate_pins(root)
    _validate_manifest(root, installed)
    return pins


def _protocol_inputs(root):
    result = {}
    for name in ('native/pointer.xml', 'native/keyboard.xml'):
        path = root / name
        if path.is_file():
            result[str(path)] = _sha256(path)
    try:
        package_dir = subprocess.check_output(
            ['pkg-config', '--variable=pkgdatadir', 'wayland-protocols'],
            text=True, stderr=subprocess.DEVNULL, timeout=10).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        package_dir = ''
    if package_dir:
        base = Path(package_dir)
        for name in ('stable/presentation-time/presentation-time.xml',
                     'staging/ext-background-effect/ext-background-effect-v1.xml'):
            path = base / name
            if path.is_file():
                result[str(path)] = _sha256(path)
    return result, package_dir or None


def _toolchain_identity():
    cc = shutil.which('cc')
    if not cc:
        raise SyncError('cc is unavailable; cannot build local executables')
    try:
        output = subprocess.check_output([cc, '--version'], text=True,
                                         stderr=subprocess.STDOUT, timeout=10)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise SyncError(f'cannot identify compiler {cc}') from exc
    return {'cc': cc, 'cc_version': output.strip()}


def _build_with_log(root, log_path, wrapper_dir, real_tools):
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    for command, executable in real_tools.items():
        wrapper = wrapper_dir / command
        script = ('#!/usr/bin/python3\n'
                  'import json, os, sys\n'
                  f'log = {str(log_path)!r}\n'
                  f'real = {str(executable)!r}\n'
                  f'command = {command!r}\n'
                  'with open(log, "a") as stream:\n'
                  '    stream.write(json.dumps({"command": command, "argv": [command, *sys.argv[1:]]}) + "\\n")\n'
                  'os.execv(real, [real, *sys.argv[1:]])\n')
        wrapper.write_text(script)
        wrapper.chmod(0o755)
    env = os.environ.copy()
    env['PATH'] = str(wrapper_dir) + os.pathsep + env.get('PATH', '/usr/bin:/bin')
    env.pop('CU_SESSION_TOKEN', None)
    command = [sys.executable, str(root / 'scripts/build.py')]
    result = subprocess.run(command, cwd=root, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.stdout:
        print(result.stdout, end='' if result.stdout.endswith('\n') else '\n')
    if result.returncode:
        raise SyncError(f'local build failed at {root}: exit {result.returncode}')
    commands = []
    if log_path.exists():
        commands = [json.loads(line) for line in log_path.read_text().splitlines() if line]
    return {'command': command, 'exit_code': result.returncode, 'tool_commands': commands,
            'output': result.stdout}


def _build_artifacts(root):
    result = {}
    for name in BUILD_OUTPUTS:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise SyncError(f'build output is missing or unsafe: {path}')
        result[name] = _metadata(path)
    return result


def _all_stage_entries(root, base_entries):
    entries = dict(base_entries)
    for name in GENERATED_FILES:
        path = root / name
        if path.is_file() and not _excluded_active(name):
            entries[name] = _metadata(path)
    return dict(sorted(entries.items()))


def _write_journal(snapshot, value):
    _write_json_atomic(snapshot / 'transaction.json', value)


def _publish(stage_root, installed, snapshot, snapshot_manifest, repo, session):
    journal = {'status': 'publishing', 'published_dirs': [], 'published_files': [],
               'stage_root': str(stage_root), 'snapshot': str(snapshot)}
    _write_journal(snapshot, journal)
    displaced = stage_root / '.displaced'
    displaced.mkdir()
    try:
        for name in MANAGED_DIRS:
            _session_clear(session)
            live, staged = installed / name, stage_root / name
            journal['intent'] = name
            _write_journal(snapshot, journal)
            if live.exists():
                os.rename(live, displaced / name)
            os.rename(staged, live)
            journal['published_dirs'].append(name)
            journal.pop('intent', None)
            _write_journal(snapshot, journal)
        for name in MANAGED_FILES:
            _session_clear(session)
            live, staged = installed / name, stage_root / name
            journal['intent'] = name
            _write_journal(snapshot, journal)
            if live.exists():
                os.rename(live, displaced / name)
            temp = installed.parent / f'.{name}.sync-{uuid.uuid4().hex}'
            try:
                _copy_file(staged, temp)
                os.rename(temp, live)
            finally:
                temp.unlink(missing_ok=True)
            journal['published_files'].append(name)
            journal.pop('intent', None)
            _write_journal(snapshot, journal)
        # Restore individually preserved history only after replacement.
        for name, exists in snapshot_manifest['preserved_history_present'].items():
            if exists:
                _copy_file(snapshot / 'preserved' / name, installed / name)
        _session_clear(session)
        journal['status'] = 'published'
        _write_journal(snapshot, journal)
    except BaseException as exc:
        journal['status'] = 'restoring-after-publish-error'
        journal['error'] = f'{type(exc).__name__}: {exc}'
        _write_journal(snapshot, journal)
        try:
            _restore_snapshot(snapshot, repo, installed, session, already_locked=True)
            journal['status'] = 'restored-after-publish-error'
            _write_journal(snapshot, journal)
        except BaseException as restore_exc:
            journal['status'] = 'INCOMPLETE-TRANSACTION'
            journal['restore_error'] = f'{type(restore_exc).__name__}: {restore_exc}'
            _write_journal(snapshot, journal)
            raise SyncError(f'INCOMPLETE TRANSACTION: publish failed ({exc}); restore failed '
                            f'({restore_exc}); snapshot={snapshot}') from restore_exc
        raise SyncError(f'publication failed and previous release was restored: {exc}; '
                        f'snapshot={snapshot}') from exc


def _archive_live(path, archive):
    if path.exists() or path.is_symlink():
        archive.parent.mkdir(parents=True, exist_ok=True)
        os.rename(path, archive)


def _restore_snapshot(snapshot, repo, installed, session, already_locked=False):
    manifest = _verify_snapshot(snapshot, repo, installed)
    if not already_locked:
        _session_clear(session)
    work = installed.parent / f'.sync-restore-{uuid.uuid4().hex}'
    work.mkdir(mode=0o700)
    archive = snapshot / 'transaction' / ('displaced-' + uuid.uuid4().hex)
    try:
        for name in MANAGED_DIRS:
            live = installed / name
            _archive_live(live, archive / name)
            if manifest['managed_dirs_present'][name]:
                source = snapshot / 'trees' / name
                _copy_tree(source, work / name)
                os.rename(work / name, live)
        for name in MANAGED_FILES:
            live = installed / name
            _archive_live(live, archive / name)
            if manifest['managed_files_present'][name]:
                _copy_file(snapshot / 'top' / name, work / name)
                os.rename(work / name, live)
        for name, exists in manifest['preserved_history_present'].items():
            path = installed / name
            if path.exists() or path.is_symlink():
                path.unlink()
            if exists:
                _copy_file(snapshot / 'preserved' / name, path)
        _verify_restored_snapshot(manifest, snapshot, installed)
        if not already_locked:
            _session_clear(session)
        journal = {'status': 'rolled-back', 'snapshot': str(snapshot),
                   'restored_at': datetime.datetime.now().astimezone().isoformat()}
        _write_journal(snapshot, journal)
    except BaseException as exc:
        _write_journal(snapshot, {'status': 'INCOMPLETE-ROLLBACK', 'snapshot': str(snapshot),
                                  'error': f'{type(exc).__name__}: {exc}'})
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _verify_restored_snapshot(manifest, snapshot, installed):
    for name in MANAGED_DIRS:
        path = installed / name
        expected_present = manifest['managed_dirs_present'][name]
        if path.exists() != expected_present:
            raise SyncError(f'rollback directory presence mismatch: {path}')
        if expected_present:
            snapshot_tree = snapshot / 'trees' / name
            expected_tree = _tree_inventory(snapshot_tree)
            prefix = name + '/'
            for history, exists in manifest['preserved_history_present'].items():
                if exists and history.startswith(prefix):
                    relative = history[len(prefix):]
                    expected_tree[relative] = _metadata(snapshot / 'preserved' / history)
            if _tree_inventory(path) != expected_tree:
                raise SyncError(f'rollback directory content mismatch: {path}')
    for name in MANAGED_FILES:
        path = installed / name
        if path.exists() != manifest['managed_files_present'][name]:
            raise SyncError(f'rollback managed file presence mismatch: {path}')
        if path.exists() and _metadata(path) != _metadata(snapshot / 'top' / name):
            raise SyncError(f'rollback managed file content mismatch: {path}')
    for name, exists in manifest['preserved_history_present'].items():
        path = installed / name
        if path.exists() != exists:
            raise SyncError(f'rollback history presence mismatch: {path}')
        if exists and _metadata(path) != _metadata(snapshot / 'preserved' / name):
            raise SyncError(f'rollback history content mismatch: {path}')


def _tree_inventory(root):
    result = {}
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        for name in list(dirs):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[rel] = _metadata(path)
                dirs.remove(name)
            else:
                result[rel] = {'type': 'directory', 'mode': stat.S_IMODE(path.lstat().st_mode)}
        for name in files:
            path = base / name
            result[path.relative_to(root).as_posix()] = _metadata(path)
    return result


def _publish_ledger(installed, ledger):
    releases = installed / 'releases'
    if releases.is_symlink():
        raise SyncError(f'releases directory must not be a symlink: {releases}')
    releases.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f')
    short = ledger['source_commit'][:10]
    path = releases / f'{stamp}-{short}.json'
    if path.exists():
        path = releases / f'{stamp}-{uuid.uuid4().hex[:8]}-{short}.json'
    value = dict(ledger, status='published', ledger_path=str(path))
    _write_json_atomic(path, value)
    return path


def _latest_ledger(installed):
    directory = installed / 'releases'
    if directory.is_symlink():
        raise SyncError(f'releases directory is a symlink: {directory}')
    if not directory.is_dir():
        raise SyncError('no release ledger exists; run the guarded sync first')
    candidates = []
    for path in directory.glob('*.json'):
        if path.is_symlink() or not path.is_file():
            raise SyncError(f'unsafe release ledger entry: {path}')
        try:
            item = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if item.get('installer') == SNAPSHOT_MARKER and item.get('status') == 'published':
            candidates.append((path.name, path, item))
    if not candidates:
        raise SyncError('no published sync release ledger exists')
    _name, path, item = max(candidates, key=lambda row: row[0])
    return path, item


def _cli_link_check(installed):
    _repo, default_installed = _defaults()
    if installed != default_installed.resolve():
        return {'checked': False, 'reason': 'custom installed root'}
    link = Path.home() / '.local/bin/computer-use'
    expected = installed / 'scripts/cu.py'
    if not link.is_symlink() or link.resolve() != expected.resolve():
        raise SyncError(f'CLI link does not resolve to {expected}: {link}')
    return {'checked': True, 'path': str(link), 'target': str(expected)}


def _cli_link_state(installed):
    _repo, default_installed = _defaults()
    if installed != default_installed.resolve():
        return {'checked': False, 'reason': 'custom installed root'}
    link = Path.home() / '.local/bin/computer-use'
    return {'checked': True, 'path': str(link),
            'target': os.readlink(link) if link.is_symlink() else None,
            'is_symlink': link.is_symlink()}


def _check_release(repo, installed, ledger_override=None):
    _managed_dir_check(repo, require_exists=True)
    _managed_dir_check(installed, require_exists=True)
    source = _source_bundle(repo)
    current_digest = _digest_entries(source)
    try:
        commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                          text=True, stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SyncError('cannot read repo commit') from exc
    if ledger_override is None:
        ledger_path, ledger = _latest_ledger(installed)
    else:
        ledger_path, ledger = None, ledger_override
    if ledger.get('installer') != SNAPSHOT_MARKER or ledger.get('status') != 'published':
        raise SyncError('latest release ledger has an invalid marker or status')
    if ledger.get('source_root') != str(repo) or ledger.get('source_commit') != commit:
        raise SyncError('latest release ledger source identity differs from the current checkout')
    if ledger.get('source_content_sha256') != current_digest:
        raise SyncError('latest release ledger source-content digest differs from the current checkout')
    _validate_pins(repo)
    manifest = _validate_manifest(repo, installed)
    _validate_pins(installed)
    installed_manifest = _validate_manifest(installed, installed)
    if manifest != installed_manifest:
        raise SyncError('installed visuals manifest differs from repo')
    for relative in ('scripts/indicator.py', 'native/indicator.c'):
        if source.get(relative) != _metadata(installed / relative):
            raise SyncError(f'repo/installed {relative} hash or mode differs')

    expected = dict(source)
    ledger_managed = ledger.get('managed_files', {})
    # Build outputs absent from the checkout are still managed and checked from the release ledger.
    for name, meta in ledger_managed.items():
        if name not in expected:
            expected[name] = meta
    for name in ledger_managed:
        if name in expected and expected[name] != ledger_managed[name]:
            raise SyncError(f'ledger managed digest differs from repository source: {name}; '
                            f'repo={expected[name]}; staged={ledger_managed[name]}')
    for name, meta in expected.items():
        actual_path = installed / name
        if not actual_path.exists() and not actual_path.is_symlink():
            raise SyncError(f'managed installed file is missing: {name}')
        if _metadata(actual_path) != meta:
            raise SyncError(f'managed installed file differs from source/release: {name}')
    for output in BUILD_OUTPUTS:
        staged = ledger.get('artifacts', {}).get('staged', {}).get(output)
        built = ledger.get('artifacts', {}).get('installed', {}).get(output)
        live = _metadata(installed / output) if (installed / output).is_file() else None
        if staged is None or built is None or staged != built or live != built:
            raise SyncError(f'build artifact provenance mismatch: {output}')

    expected_exceptions = set(HISTORY_FILES)
    actual = set()
    for directory in MANAGED_DIRS:
        for current, dirs, files in os.walk(installed / directory, topdown=True, followlinks=False):
            base = Path(current)
            for name in list(dirs):
                path = base / name
                if path.is_symlink():
                    actual.add(path.relative_to(installed).as_posix())
                    dirs.remove(name)
            for name in files:
                path = base / name
                relative = path.relative_to(installed).as_posix()
                if '__pycache__' not in PurePosixPath(relative).parts:
                    actual.add(relative)
    actual.update(name for name in MANAGED_FILES if (installed / name).exists())
    allowed = set(expected) | expected_exceptions
    extras = sorted(actual - allowed)
    missing = sorted(set(expected) - actual)
    if extras:
        raise SyncError('unexpected files in active managed tree: ' + ', '.join(extras[:20]))
    if missing:
        raise SyncError('missing files in active managed tree: ' + ', '.join(missing[:20]))

    for name in HISTORY_FILES:
        old = ledger.get('preserved_history', {}).get(name)
        path = installed / name
        if old is None:
            if path.exists() or path.is_symlink():
                raise SyncError(f'unrecorded preserved-history file exists: {name}')
        elif not path.is_file() or path.is_symlink() or _metadata(path) != old:
            raise SyncError(f'preserved-history exception changed: {name}')
    link = _cli_link_check(installed)
    return {'ok': True, 'managed_files': len(expected), 'ledger': str(ledger_path) if ledger_path else None,
            'preserved_history': sorted(name for name in HISTORY_FILES
                                        if name in ledger.get('preserved_history', {})),
            'cli_link': link}


def _source_commit(repo):
    return subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                   text=True, stderr=subprocess.PIPE).strip()


def _relay_public_status(repo):
    try:
        result = subprocess.run([sys.executable, str(repo / BROKER_SOURCE), 'status'],
                                capture_output=True, text=True, timeout=5)
        status = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise SyncError(f'computer-use relay status is unavailable: {exc}') from exc
    if result.returncode != 0 or not isinstance(status, dict) or status.get('ok') is not True:
        raise SyncError(f'computer-use relay status is unavailable: {status}')
    return status


def _relay_idle(status):
    return (
        status.get('state') in ('idle', 'finished') and
        status.get('driver') in ('idle', 'stopped') and
        status.get('guardian') in ('idle', 'clean') and
        status.get('active_sequence') is None and
        status.get('error') is None and
        status.get('recovery') in (None, 'none') and
        status.get('cancelled') is False
    )


def _relay_restart_needed(repo):
    status = _relay_public_status(repo)
    expected = _sha256(repo / BROKER_SOURCE)
    if status.get('loaded_code_sha256') == expected:
        return False
    if not _relay_idle(status):
        print('WARNING: broker code is stale and the relay is busy; refusing sync. '
              'The sync cannot be claimed live until the relay is idle.', file=sys.stderr)
        raise SyncError('broker-loaded code changed while the relay is busy')
    return True


def _restart_relay(repo):
    status = _relay_public_status(repo)
    expected = _sha256(repo / BROKER_SOURCE)
    if status.get('loaded_code_sha256') == expected:
        return False
    if not _relay_idle(status):
        print('WARNING: broker code is stale and the relay became busy; refusing restart. '
              'The sync is not live.', file=sys.stderr)
        raise SyncError('computer-use relay is not idle; restart refused')
    try:
        result = subprocess.run(['systemctl', '--user', 'restart', 'computer-use-relay.service'],
                                capture_output=True, text=True, timeout=45)
    except (OSError, subprocess.SubprocessError) as exc:
        raise SyncError(f'computer-use relay restart failed: {exc}') from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[:400]
        raise SyncError(f'computer-use relay restart failed: {detail or result.returncode}')
    deadline = time.monotonic() + 10
    last_error = 'broker status did not become current and idle'
    while True:
        try:
            updated = _relay_public_status(repo)
        except SyncError as exc:
            last_error = str(exc)
        else:
            if (not _relay_idle(updated) or updated.get('loaded_code_sha256') != expected or
                    updated.get('broker_generation') == status.get('broker_generation')):
                last_error = 'broker status did not become current and idle'
            else:
                print('Computer-use relay restarted; loaded broker code hash matches the source.')
                return True
        if time.monotonic() >= deadline:
            raise SyncError(f'computer-use relay restarted but readiness was not verified: {last_error}')
        time.sleep(0.1)


def _sync(repo, installed, session):
    _managed_dir_check(repo, require_exists=True)
    _managed_dir_check(installed)
    source_entries = _source_bundle(repo)
    source_digest = _digest_entries(source_entries)
    commit = _source_commit(repo)
    snapshot, snapshot_manifest = _create_snapshot(repo, installed, commit, source_digest)
    print(f'Snapshot: {snapshot}')

    stage_parent = installed.parent
    stage_root = stage_parent / f'.sync-stage-{uuid.uuid4().hex}'
    stage_root.mkdir(mode=0o700)
    keep_stage = False
    try:
        _copy_active_bundle(repo, installed, stage_root, source_entries)
        _validate_pins(stage_root)
        _validate_manifest(stage_root, installed)
        _required_staged_files(stage_root, installed)
        toolchain = _toolchain_identity()
        protocol_hashes, protocol_dir = _protocol_inputs(stage_root)
        wrapper_dir = stage_root / '.commandcode'
        real_tools = {}
        for command in ('cc', 'pkg-config', 'wayland-scanner', 'patch'):
            path = shutil.which(command)
            if path:
                real_tools[command] = path
        if 'cc' not in real_tools or 'wayland-scanner' not in real_tools or 'pkg-config' not in real_tools or 'patch' not in real_tools:
            raise SyncError('build requires cc, pkg-config, wayland-scanner, and patch on PATH')
        staged_log = stage_parent / f'.sync-stage-commands-{uuid.uuid4().hex}.jsonl'
        staged_build = _build_with_log(stage_root, staged_log, wrapper_dir, real_tools)
        stage_outputs = _build_artifacts(stage_root)
        stage_entries = _all_stage_entries(stage_root, source_entries)
        _validate_manifest(stage_root, installed)
        _required_staged_files(stage_root, installed)
        build_evidence = {
            'source_commit': commit,
            'source_content_sha256': source_digest,
            'toolchain': toolchain,
            'staged_build': staged_build,
            'protocol_data_dir': protocol_dir,
            'protocol_input_sha256': protocol_hashes,
            'repo_build_outputs': {name: source_entries.get(name) for name in BUILD_OUTPUTS},
            'staged_build_outputs': stage_outputs,
            'managed_files': stage_entries,
        }
        _write_json_atomic(snapshot / 'staging-evidence.json', build_evidence)

        # The repo is read-only input; a changed tree aborts before publication.
        if (_digest_entries(_source_bundle(repo)) != source_digest or
                _source_commit(repo) != commit):
            raise SyncError('repo source or commit changed during staging; refusing publication')
        _session_clear(session)

        try:
            _publish(stage_root, installed, snapshot, snapshot_manifest, repo, session)
        except SyncError as exc:
            if str(exc).startswith('INCOMPLETE TRANSACTION:'):
                keep_stage = True
            raise
        installed_log = stage_parent / f'.sync-installed-commands-{uuid.uuid4().hex}.jsonl'
        installed_wrapper = stage_root / '.commandcode-installed'
        try:
            actual_build_path = (installed / 'scripts/build.py').resolve(strict=True)
            installed_build = _build_with_log(installed, installed_log, installed_wrapper, real_tools)
            installed_outputs = _build_artifacts(installed)
            build_evidence['installed_build'] = installed_build
            build_evidence['installed_build_script'] = str(actual_build_path)
            build_evidence['installed_build_outputs'] = installed_outputs
            _write_json_atomic(snapshot / 'staging-evidence.json', build_evidence)
            if installed_outputs != stage_outputs:
                raise SyncError('installed rebuild artifact hashes differ from staged build; '
                                f'staged={stage_outputs}; installed={installed_outputs}')
            # Check source identity and lock/session state again before recording the release.
            _session_clear(session)
            if (_digest_entries(_source_bundle(repo)) != source_digest or
                    _source_commit(repo) != commit):
                raise SyncError('repo source changed before release verification; refusing acceptance')
            history = {}
            for name, exists in snapshot_manifest['preserved_history_present'].items():
                if exists:
                    history[name] = _metadata(installed / name)
            for name in HISTORY_FILES:
                if name == 'CREW.md' and (installed / name).is_file():
                    history[name] = _metadata(installed / name)
            cold = {name: bool(snapshot_manifest['cold_tests_present'].get(name))
                    for name in COLD_TESTS}
            ledger = {
                'installer': SNAPSHOT_MARKER,
                'format': FORMAT_VERSION,
                'status': 'published',
                'source_root': str(repo),
                'source_commit': commit,
                'source_content_sha256': source_digest,
                'managed_files': stage_entries,
                'generated_file_inputs': sorted(name for name in source_entries
                                                if name in GENERATED_FILES),
                'generated_file_exclusions': [
                    'native/hyprglass*.so', 'native/cursor-guard-*.so', '*.~1~', '*.bak*',
                    '__pycache__', '.git', '.commandcode',
                ],
                'build': {
                    'toolchain': toolchain,
                    'staged': staged_build,
                    'installed': installed_build,
                    'installed_build_script': str(actual_build_path),
                    'protocol_data_dir': protocol_dir,
                    'protocol_input_sha256': protocol_hashes,
                    'source_build_script_sha256': source_entries['scripts/build.py']['sha256'],
                },
                'artifacts': {'staged': stage_outputs, 'installed': installed_outputs},
                'snapshot_path': str(snapshot),
                'superseded_hand_patches': snapshot_manifest['hand_patch_backups'],
                'passive_native_artifact': ('native/cursor-guard.so'
                                            if 'native/cursor-guard.so' in stage_entries else None),
                'preserved_history': history,
                'cold_preserved_tests': cold,
                'preserved_untouched': {
                    'backups/': 'existing content retained; this sync snapshot was added',
                    'browser-profile/': 'untouched',
                    'plugins/': 'untouched',
                    'vendor/': 'untouched',
                },
            }
            _check_release(repo, installed, ledger_override=ledger)
            ledger_path = _publish_ledger(installed, ledger)
            ledger['ledger_path'] = str(ledger_path)
            check = _check_release(repo, installed)
            print(f'Release ledger: {ledger_path}')
            print(f'Installed build script: {actual_build_path}')
            print(f'--check: exit 0 ({check["managed_files"]} managed files; '
                  f'{len(check["preserved_history"])} preserved-history exceptions)')
            print('Installed sync published and verified.')
            return {'snapshot': snapshot, 'ledger': ledger_path, 'check': check,
                    'staged_artifacts': stage_outputs, 'installed_artifacts': installed_outputs,
                    'build': ledger['build'], 'source_commit': commit,
                    'source_content_sha256': source_digest}
        except BaseException as exc:
            try:
                _write_json_atomic(snapshot / 'sync-failure.json', {
                    'error': f'{type(exc).__name__}: {exc}',
                    'staging_evidence': str(snapshot / 'staging-evidence.json'),
                })
            except OSError:
                pass
            if 'ledger_path' in locals() and ledger_path.exists():
                try:
                    failed_ledger = json.loads(ledger_path.read_text())
                    failed_ledger['status'] = 'rolled_back'
                    failed_ledger['failure'] = f'{type(exc).__name__}: {exc}'
                    _write_json_atomic(ledger_path, failed_ledger)
                except (OSError, json.JSONDecodeError):
                    pass
            journal_path = snapshot / 'transaction.json'
            try:
                journal = json.loads(journal_path.read_text()) if journal_path.is_file() else {}
                if journal.get('status') == 'published':
                    _restore_snapshot(snapshot, repo, installed, session, already_locked=True)
                else:
                    _restore_snapshot(snapshot, repo, installed, session, already_locked=True)
            except BaseException as restore_exc:
                keep_stage = True
                _write_journal(snapshot, {'status': 'INCOMPLETE-TRANSACTION',
                                          'snapshot': str(snapshot),
                                          'stage_root': str(stage_root),
                                          'error': f'{type(exc).__name__}: {exc}',
                                          'restore_error': f'{type(restore_exc).__name__}: {restore_exc}'})
                raise SyncError(f'INCOMPLETE TRANSACTION: sync failed ({exc}); restore failed '
                                f'({restore_exc}); snapshot={snapshot}; stage={stage_root}') from restore_exc
            raise
    finally:
        if 'staged_log' in locals() and staged_log.exists():
            staged_log.unlink()
        if 'installed_log' in locals() and installed_log.exists():
            installed_log.unlink()
        if not keep_stage:
            shutil.rmtree(stage_root, ignore_errors=True)


def _rollback(repo, installed, snapshot_path, session):
    requested = Path(snapshot_path)
    if not requested.is_absolute():
        raise SyncError('--rollback requires an absolute snapshot path')
    if requested.is_symlink():
        raise SyncError('--rollback refuses a symlink snapshot path')
    snapshot = requested.resolve(strict=True)
    backups = installed / 'backups'
    if backups.is_symlink() or snapshot.parent != backups.resolve(strict=True):
        raise SyncError(f'rollback snapshot must be directly under {backups}')
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise SyncError(f'rollback snapshot is not a directory: {snapshot}')
    _verify_snapshot(snapshot, repo, installed)
    _restore_snapshot(snapshot, repo, installed, session)
    _cli_link_check(installed)
    print(f'Rollback complete from {snapshot}')
    return {'snapshot': snapshot, 'ok': True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='verify the installed managed release')
    modes.add_argument('--rollback', metavar='ABSOLUTE_SNAPSHOT',
                       help='restore a release snapshot made by this installer')
    parser.add_argument('--repo', type=Path, help='source git checkout')
    parser.add_argument('--installed', type=Path, help='installed package root')
    args = parser.parse_args(argv)
    try:
        repo, installed = _resolve_roots(args.repo, args.installed)
        _managed_dir_check(repo, require_exists=True)
        if not args.check and not args.rollback:
            installed.parent.mkdir(parents=True, exist_ok=True)
        if installed.exists() and not installed.is_dir():
            raise SyncError(f'installed root is not a directory: {installed}')
        with _session_lock(repo) as session:
            if args.check:
                result = _check_release(repo, installed)
                print(f'--check: exit 0 ({result["managed_files"]} managed files)')
                print('Preserved-history exceptions: ' +
                      (', '.join(result['preserved_history']) or 'none'))
                if not result['cli_link']['checked']:
                    print('CLI link: skipped for custom installed root')
                return 0
            if args.rollback:
                _rollback(repo, installed, args.rollback, session)
                return 0
            restart_relay = _relay_restart_needed(repo)
            _sync(repo, installed, session)
            if restart_relay:
                _restart_relay(repo)
            return 0
    except (SyncError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'sync-installed: error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

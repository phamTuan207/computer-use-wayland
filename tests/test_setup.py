"""Offline setup helpers: header ABI proof and safe hook installation. No GUI."""
import importlib.util
from contextlib import ExitStack
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
_spec = importlib.util.spec_from_file_location('setup', Path(__file__).resolve().parents[1]/'scripts/setup.py')
setup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup)
import cursor_theme as real_cursor_theme

COMMANDS = ('cc -shared -fPIC -o %s %s', 'x')


def macros(**overrides):
    values = {'GIT_COMMIT_HASH': 'v0.56.2', 'AQUAMARINE_VERSION': '0.15.2',
              'HYPRUTILS_VERSION': '0.14.9', 'HYPRGRAPHICS_VERSION': '0.5.11',
              'HYPRCURSOR_VERSION': '0.1.9', 'HYPRLANG_VERSION': '0.6.3'}
    values.update(overrides)
    return ''.join(f'#define {k} "{v}"\n' for k, v in values.items())


def fake_pkg(version='0.56.2', cflags='-I/usr/include/hyprland'):
    def run(argv, **kwargs):
        if argv[:2] == ['pkg-config', '--modversion']:
            return version + '\n'
        return cflags + '\n'
    return run


def fake_preproc(text):
    return lambda argv, **kwargs: text


class HeaderAbiTests(unittest.TestCase):
    def test_reconstructs_the_pinned_client_hash(self):
        expected = ('v0.56.2' + '_aq_0.15' + '_hu_0.14' + '_hg_0.5' + '_hc_0.1' + '_hlg_0.6')
        with mock.patch.object(setup.subprocess, 'check_output',
                               side_effect=lambda argv, **k: fake_pkg()(argv, **k)
                               if argv[0] == 'pkg-config' else macros()):
            self.assertEqual(setup.header_abi({}), expected)

    def test_strip_patch_keeps_everything_before_the_rightmost_dot(self):
        self.assertEqual(setup._strip_patch('0.15.2'), '0.15')
        self.assertEqual(setup._strip_patch('1.2.3.4'), '1.2.3')
        self.assertEqual(setup._strip_patch('nodot'), 'nodot')

    def test_wrong_hyprland_version_is_refused(self):
        for version in ('0.56.1', '0.57.0', '', '0.56.2-rc1'):
            with self.subTest(version=version):
                with mock.patch.object(setup.subprocess, 'check_output', new=fake_pkg(version)):
                    with self.assertRaisesRegex(RuntimeError, '0.56.2 required'):
                        setup.header_abi({})

    def test_missing_macro_is_refused(self):
        text = macros().replace('#define HYPRUTILS_VERSION "0.14.9"\n', '')
        with mock.patch.object(setup.subprocess, 'check_output',
                               side_effect=lambda argv, **k: fake_pkg()(argv, **k)
                               if argv[0] == 'pkg-config' else text):
            with self.assertRaisesRegex(RuntimeError, 'HYPRUTILS_VERSION'):
                setup.header_abi({})

    def test_malformed_macro_is_refused(self):
        # The only definition is unquoted, so nothing valid remains to parse.
        text = macros().replace('#define HYPRUTILS_VERSION "0.14.9"\n',
                                '#define HYPRUTILS_VERSION 014\n')
        with mock.patch.object(setup.subprocess, 'check_output',
                               side_effect=lambda argv, **k: fake_pkg()(argv, **k)
                               if argv[0] == 'pkg-config' else text):
            with self.assertRaisesRegex(RuntimeError, 'HYPRUTILS_VERSION'):
                setup.header_abi({})

    def test_preprocess_only_no_link_or_execution(self):
        seen = []
        def run(argv, **kwargs):
            seen.append(argv)
            return fake_pkg()(argv, **kwargs) if argv[0] == 'pkg-config' else macros()
        with mock.patch.object(setup.subprocess, 'check_output', new=run):
            setup.header_abi({})
        compile_line = [a for a in seen if a and a[0] == 'c++'][0]
        self.assertEqual(compile_line[:2], ['c++', '-std=c++23'])
        self.assertIn('-dM', compile_line)
        self.assertNotIn('-o', compile_line, 'nothing is produced or linked')


class InstallHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.config = self.dir / 'hyprland.conf'
        self.config.write_text('-- user config\nlocal preference = 42\n')
        self.config.chmod(0o640)
        self.hook = self.dir / 'visuals-hook.lua'
        self.command = 'python3 ~/.local/bin/visuals --now && echo done'

    def test_appends_a_managed_block_and_writes_the_hook(self):
        result = setup.install_hook(self.config, self.command, self.hook)
        self.assertTrue(result['changed'])
        text = self.config.read_text()
        self.assertTrue(text.startswith('-- user config\nlocal preference = 42\n'),
                        'existing bytes are preserved and the block is appended')
        self.assertIn('computer-use-visuals-begin', text)
        self.assertIn('computer-use-visuals-end', text)
        self.assertIn(json.dumps(str(self.hook)), text)
        hook = self.hook.read_text()
        self.assertIn('hl.on("hyprland.start"', hook)
        self.assertIn('hl.exec_cmd(' + json.dumps(self.command, ensure_ascii=False) + ')', hook)
        self.assertNotIn('sleep', hook)

    def _everything(self):
        return sorted(str(path.relative_to(self.dir)) for path in self.dir.rglob('*'))

    def test_check_only_writes_nothing_on_any_branch(self):
        # 1. no managed block yet
        before = self._everything()
        result = setup.install_hook(self.config, self.command, self.hook, check_only=True)
        self.assertTrue(result['changed'])
        self.assertEqual(self._everything(), before, 'no block, no hook, no backup')
        # 2. managed block present but the hook file is missing
        setup.install_hook(self.config, self.command, self.hook)
        self.hook.unlink()
        before = self._everything()
        result = setup.install_hook(self.config, self.command, self.hook, check_only=True)
        self.assertTrue(result['changed'], 'it still reports the missing hook')
        self.assertFalse(self.hook.exists(), 'a check never repairs the hook')
        self.assertEqual(self._everything(), before)
        # 3. managed block present and the hook is intact
        setup.install_hook(self.config, self.command, self.hook)
        before = self._everything()
        result = setup.install_hook(self.config, self.command, self.hook, check_only=True)
        self.assertFalse(result['changed'])
        self.assertEqual(self._everything(), before)

    def test_check_only_still_refuses_an_edited_block(self):
        setup.install_hook(self.config, self.command, self.hook)
        self.config.write_text(self.config.read_text().replace('dofile', 'dofile "x"'))
        with self.assertRaisesRegex(ValueError, 'edited managed block'):
            setup.install_hook(self.config, self.command, self.hook, check_only=True)

    def test_backup_holds_the_exact_original_bytes_and_mode(self):
        before = self.config.read_bytes()
        result = setup.install_hook(self.config, self.command, self.hook)
        backup = self.dir / result['backup']
        self.assertEqual(backup.read_bytes(), before)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o640)
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o640, 'config mode preserved')

    def test_second_call_is_a_no_op(self):
        first = setup.install_hook(self.config, self.command, self.hook)
        digest = self.config.read_bytes()
        backups = sorted(p.name for p in self.dir.iterdir())
        second = setup.install_hook(self.config, self.command, self.hook)
        self.assertFalse(second['changed'])
        self.assertEqual(self.config.read_bytes(), digest)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), backups,
                         'a no-op writes nothing at all')
        self.assertTrue(first['changed'])

    def test_edited_managed_block_is_never_replaced(self):
        setup.install_hook(self.config, self.command, self.hook)
        edited = self.config.read_text().replace('dofile(', 'dofile("/tmp/other.lua") and dofile(')
        self.config.write_text(edited)
        with self.assertRaisesRegex(ValueError, 'edited managed block'):
            setup.install_hook(self.config, self.command, self.hook)

    def test_duplicate_or_malformed_markers_are_refused(self):
        block = setup._managed_block(self.hook)
        for text in (self.config.read_text() + block + block,
                     self.config.read_text() + setup.HOOK_BEGIN + '\n'):
            with self.subTest(text=text[-40:]):
                self.config.write_text(text)
                with self.assertRaises(ValueError):
                    setup.install_hook(self.config, self.command, self.hook)

    def test_symlinked_config_is_refused(self):
        real = self.dir / 'real.conf'
        real.write_text('x\n')
        link = self.dir / 'link.conf'
        link.symlink_to(real)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            setup.install_hook(link, self.command, self.hook)

    def test_foreign_hook_file_is_refused_and_never_overwritten(self):
        self.hook.write_text('-- someone else owns this\n')
        with self.assertRaisesRegex(ValueError, 'does not own'):
            setup.install_hook(self.config, self.command, self.hook)
        self.assertEqual(self.hook.read_text(), '-- someone else owns this\n')

    @unittest.skipUnless(shutil.which('lua'), 'Lua interpreter missing')
    def test_quotes_and_unicode_paths_execute_one_startup_command(self):
        nasty = 'echo "Tiếng Việt \"hi\"" && true'
        self.hook=self.dir/'Dự án'/'login.lua';self.hook.parent.mkdir()
        setup.install_hook(self.config, nasty, self.hook)
        program = 'local fn;local calls=0;hl={on=function(e,f) assert(e=="hyprland.start");fn=f end,exec_cmd=function(s) assert(s==arg[2]);calls=calls+1 end};dofile(arg[1]);assert(calls==0);fn();assert(calls==1)'
        subprocess.run(['lua','-',str(self.config),nasty],input=program,text=True,check=True,capture_output=True)

    def test_missing_managed_hook_is_repaired_without_changing_config(self):
        setup.install_hook(self.config, self.command, self.hook)
        original=self.config.read_bytes();self.hook.unlink()
        result=setup.install_hook(self.config, self.command, self.hook)
        self.assertTrue(result['changed']);self.assertTrue(self.hook.is_file())
        self.assertEqual(self.config.read_bytes(), original)

    def test_conflicting_backup_blocks_all_config_changes(self):
        original=self.config.read_bytes()
        backup=self.config.with_name(self.config.name+'.bak-'+hashlib.sha256(original).hexdigest()[:16])
        backup.write_bytes(b'foreign')
        with self.assertRaisesRegex(ValueError, 'backup differs'):
            setup.install_hook(self.config, self.command, self.hook)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertEqual(backup.read_bytes(), b'foreign')

    def test_write_failure_preserves_the_original_config(self):
        with mock.patch.object(setup, 'atomic_write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                setup.install_hook(self.config, self.command, self.hook)
        self.assertEqual(self.config.read_text(), '-- user config\nlocal preference = 42\n')

    def test_concurrent_edit_between_read_and_write_is_refused(self):
        real_write = setup.atomic_write
        def racing(path, data):
            # The user edits the config while the hook file is being written.
            if Path(path) == self.hook:
                self.config.write_bytes(b'# user edited\n')
            return real_write(path, data)
        with mock.patch.object(setup, 'atomic_write', new=racing):
            with self.assertRaisesRegex(RuntimeError, 'changed underneath'):
                setup.install_hook(self.config, self.command, self.hook)
        self.assertEqual(self.config.read_bytes(), b'# user edited\n',
                         'the user edit wins; nothing was overwritten')


class _SetupFixture:
    """The pipeline with every external command mocked; temp config/data/bin only."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.config = self.dir / 'hyprland.lua'
        self.config.write_text('# user config\n')
        self.data = self.dir / 'data'
        self.bin = self.dir / 'bin'
        self.data.mkdir()
        self.bin.mkdir()
        self.env = {'PATH': '/usr/bin', 'HYPRLAND_INSTANCE_SIGNATURE': 'setup-login',
                    'XDG_RUNTIME_DIR': '/run/user/1000'}
        self.calls = []
        self.plugins = '[]'
        self.root = self.dir / 'root'
        self.root.mkdir()
        (self.root/'scripts').mkdir()
        for name in ('build.py', 'build-glass.py', 'build-cursor.py', 'install-glass.py',
                     'visuals.py', 'cu.py'):
            (self.root/'scripts'/name).write_text('# placeholder\n')
        (self.root/'native').mkdir()
        (self.root/'native/hyprglass-local-optics.lua').write_text('-- optics\n')
        state = self.dir/'state'
        state.mkdir()
        self.snapshot = state/'session.json'
        self.snapshot.write_text('{"version":4}')
        self._restore_snapshot = self.snapshot.unlink
        self.glass = self.dir / 'glass'
        self.glass.mkdir()
        (self.glass/'hyprglass.so').write_bytes(b'so')

    def _run(self, argv, **kwargs):
        self.calls.append(argv)
        answer = getattr(self, 'answer', None)
        if answer is not None:
            return answer(argv, **kwargs)
        return self._default(argv, **kwargs)

    def _default(self, argv, **kwargs):
        """The fake compositor, git and build helpers."""
        if argv[0] == 'git':
            return subprocess.CompletedProcess(argv, 0, '', '')
        if any('build-glass' in part for part in argv):
            # The real helper's last stdout line is a diagnostic, never a path.
            source = Path([a for a in argv if a.endswith('hyprglass')][0])
            source.mkdir(parents=True, exist_ok=True)
            (source/'hyprglass.so').write_bytes(b'\x7fELF fake')
            return subprocess.CompletedProcess(
                argv, 0, 'built\nnot installed and not loaded; log out to enable\n', '')
        if argv[0] == 'hyprctl':
            payload = self.plugins if 'plugin' in argv else '{"abiHash":"abi"}'
            return subprocess.CompletedProcess(argv, 0, payload, '')
        return subprocess.CompletedProcess(argv, 0, '', '')

    def declared(self, **kwargs):
        """A successful call declares the manual restore the user typed once."""
        kwargs.setdefault('restore_theme', 'Adwaita')
        kwargs.setdefault('restore_size', 24)
        return setup.setup(self.config, self.data, self.bin, **kwargs)

    def _patched(self, installed=('installed.so',), exist_ok=False):
        self.snapshot.unlink(missing_ok=True)   # a clean machine for the happy paths
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(setup, 'ROOT', self.root))
        stack.enter_context(mock.patch.object(setup, 'ICON_DIRECTORY', self.data/'icons'))
        self.plugins = '[]'
        cursor_session = mock.Mock()
        cursor_session.SNAPSHOT = self.snapshot
        cu = mock.Mock()
        cu.environment.return_value = self.env
        cursor_session.owner_lock = mock.MagicMock()
        cursor_session.SNAPSHOT = self.snapshot
        stack.enter_context(mock.patch.dict(sys.modules,
                                            {'cursor_session': cursor_session, 'cu': cu,
                                             'cursor_theme': mock.Mock(
                                                 search_roots=mock.Mock(return_value=[self.data/'icons']),
                                                 validate=real_cursor_theme.validate,
                                                 PROFILE=self.root/'native/agent-cursor.json')}))
        stack.enter_context(mock.patch.object(setup, '_run', new=self._run))
        stack.enter_context(mock.patch.object(setup.shutil, 'which', new=lambda n, path=None: '/usr/bin/'+n))
        stack.enter_context(mock.patch.object(setup.importlib.util, 'find_spec',
                                              new=mock.Mock(return_value=object())))
        stack.enter_context(mock.patch.object(setup, 'header_abi', new=mock.Mock(return_value='abi')))
        stack.enter_context(mock.patch.object(setup.tempfile, 'TemporaryDirectory',
                                              mock.Mock(side_effect=lambda **k: _TempDir(self.root))))
        cursor = mock.Mock()
        cursor.install.return_value = (self.data/'icons/cu-agent-hash', exist_ok)
        cursor.tree_digest.return_value = 'tree'
        stack.enter_context(mock.patch.object(setup, '_load',
                                              mock.Mock(side_effect=lambda n, p: cursor if 'cursor' in n else _glass())))
        return cursor


class _TempDir:
    """Stands in for TemporaryDirectory: a root-shaped parent so ROOT-relative writes work."""

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        self.folder = self.root/'owned'
        self.folder.mkdir(exist_ok=True)
        return str(self.folder)

    def __exit__(self, *exc):
        return False


def _glass():
    module = mock.Mock()
    module.install.return_value = Path('/tmp/never-installed.so')
    return module


def _cursor():
    module = mock.Mock()
    module.install.return_value = (Path('/tmp/cu-agent-hash'), False)
    module.tree_digest.return_value = 'tree'
    return module


class FullSetupTests(_SetupFixture, unittest.TestCase):
    def test_invalid_runtime_abi_shapes_refuse_before_build_or_publish(self):
        cases = {'{': 'malformed JSON', '[]': 'expected object', 'null': 'expected object',
                 '{}': 'missing abiHash', '{"abiHash":null}': 'abiHash must be a string',
                 '{"abiHash":false}': 'abiHash must be a string', '{"abiHash":7}': 'abiHash must be a string',
                 '{"abiHash":""}': 'empty abiHash'}
        for payload, detail in cases.items():
            with self.subTest(payload=payload):
                self._patched()
                self.answer = lambda argv, **kwargs: (
                    subprocess.CompletedProcess(argv, 0, payload, '')
                    if argv[0] == 'hyprctl' and 'version' in argv
                    else self._default(argv, **kwargs))
                with self.assertRaisesRegex(RuntimeError, 'invalid compositor ABI response: ' + detail):
                    self.declared()
                self.assertFalse((self.root/'native/visuals.json').exists())
                self.assertFalse((self.bin/'computer-use').exists())
                self.assertFalse(any(any('build' in part or part == 'clone' for part in call)
                                     for call in self.calls))

    def test_invalid_runtime_abi_shape_after_build_refuses_publish(self):
        versions = ['{"abiHash":"abi"}', 'null']
        def answer(argv, **kwargs):
            if argv[0] == 'hyprctl' and 'version' in argv:
                return subprocess.CompletedProcess(argv, 0, versions.pop(0), '')
            return self._default(argv, **kwargs)
        self.answer = answer
        self._patched()
        with self.assertRaisesRegex(RuntimeError, 'invalid compositor ABI response'):
            self.declared()
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertFalse((self.bin/'computer-use').exists())

    def test_undiscoverable_user_icon_directory_refuses_before_build(self):
        self._patched()
        with mock.patch.object(sys.modules['cursor_theme'],'search_roots',return_value=[]):
            with self.assertRaisesRegex(RuntimeError,'Xcursor search path'):
                self.declared()
        self.assertEqual(self.calls,[])

    def test_relative_cursor_install_result_is_serialized_as_absolute(self):
        cursor=self._patched()
        cursor.install.return_value=(Path('relative/cu-agent-tree'),False)
        self.declared()
        manifest=json.loads((self.root/'native/visuals.json').read_text())
        self.assertTrue(Path(manifest['cursor_directory']).is_absolute())

    def test_automation_token_and_missing_compositor_refuse_before_anything(self):
        for label, env in (('automation token', {**self.env, 'CU_SESSION_TOKEN': 'x'}),
                           ('no compositor', {**self.env, 'HYPRLAND_INSTANCE_SIGNATURE': ''})):
            with self.subTest(label=label):
                self._patched()
                with mock.patch.dict(sys.modules, {'cu': mock.Mock(environment=mock.Mock(return_value=env))}):
                    with self.assertRaises(RuntimeError):
                        setup.setup(self.config, self.data, self.bin)
                self.assertEqual(self.calls, [], 'nothing external ran')

    def test_retained_session_record_refuses_before_anything(self):
        self._patched()
        self.snapshot.write_text('{"version":4}')   # a record left by a crashed session
        with self.assertRaisesRegex(RuntimeError, 'retained session'):
            setup.setup(self.config, self.data, self.bin)

    def test_loaded_plugins_refuse_before_any_write(self):
        self._patched()
        self.plugins = '["some-plugin"]'      # a reload could disturb it
        self.calls.clear()
        with self.assertRaisesRegex(RuntimeError, 'plugins are already loaded'):
            self.declared()
        self.calls.clear()
        self.assertFalse((self.root/'native/visuals.json').exists())

    def test_missing_prerequisite_is_refused(self):
        self._patched()
        with mock.patch.object(setup.shutil, 'which',
                               new=lambda n, path=None: None if n=='cc' else '/usr/bin/'+n):
            with self.assertRaisesRegex(RuntimeError, 'missing prerequisite: cc'):
                self.declared()
        self.assertEqual(self.calls, [])

    def test_abi_mismatch_refuses_before_any_write(self):
        self._patched()
        with mock.patch.object(setup, 'header_abi', new=mock.Mock(return_value='other')):
            with self.assertRaisesRegex(RuntimeError, 'header ABI does not match'):
                self.declared()
        self.assertFalse((self.root/'native/visuals.json').exists())

    def test_edited_config_block_refuses_before_any_write(self):
        self._patched()
        self.config.write_text('# user\n-- computer-use-visuals-begin\n-- computer-use-visuals-end\n')
        with self.assertRaises(ValueError):
            self.declared()
        self.assertEqual(self.calls, [])

    def test_pinned_clone_is_ordered_and_nothing_is_activated(self):
        cursor = self._patched()
        result = self.declared()
        self.assertEqual(result, {'ok': True, 'restart_required': True,
                                  'cursor': 'automatic', 'liquid': 'prepared'})
        joined = ' '.join(' '.join(a) for a in self.calls)
        self.assertIn('--no-checkout', joined)
        self.assertIn(setup.GLASS_PIN, joined)
        self.assertIn('--local-optics', joined)
        for forbidden in ('activate-glass', 'plugin load', 'restart', 'logout', 'resume',
                          'setcursor', 'gsettings'):
            self.assertNotIn(forbidden, joined, forbidden + ' must never run during setup')
        manifest = json.loads((self.root/'native/visuals.json').read_text())
        self.assertEqual(manifest['version'], 1)
        self.assertEqual(manifest['setup_instance'], 'setup-login')
        self.assertEqual(manifest['cursor_tree_sha256'], 'tree')
        profile = json.loads((self.root/'native/agent-cursor.json').read_text())
        self.assertNotIn('ready_instance', profile)
        self.assertNotIn('restore_mode', profile, 'the GTK experiment is gone')
        self.assertEqual(profile['size'], 34)
        self.assertEqual(profile['restore_theme'], 'Adwaita')
        self.assertEqual(profile['restore_size'], 24)
        self.assertTrue(profile['theme'].startswith('cu-agent-'), profile['theme'])
        self.assertFalse((self.data/'agent-computer-use/native').exists(),
                         'the unused managed tree is never created')
        self.assertTrue((self.root/'native/visuals-login.lua').is_file())
        self.assertTrue((self.root/'native/require-liquid').is_file())
        self.assertTrue((self.bin/'computer-use').is_symlink())
        self.assertIn('computer-use-visuals-begin', self.config.read_text())

    def test_legacy_cursor_profile_is_preserved_byte_exact(self):
        self._patched()
        original = b'{"theme":"old","size":24,"restore_theme":"default","restore_size":24}\n'
        target = self.root/'native/agent-cursor.json'      # the path cursor_theme actually reads
        target.write_bytes(original)
        setup.setup(self.config, self.data, self.bin)   # an existing profile needs no flags
        self.assertEqual(target.read_bytes(), original)

    def test_a_failed_build_leaves_config_profile_and_link_untouched(self):
        self._patched()
        before = self.config.read_bytes()
        with mock.patch.object(setup, '_checked', side_effect=RuntimeError('build failed')):
            with self.assertRaisesRegex(RuntimeError, 'build failed'):
                self.declared()
        self.assertEqual(self.config.read_bytes(), before)
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertFalse((self.bin/'computer-use').exists())
        self.assertFalse((self.root/'native/agent-cursor.json').exists())

    def test_existing_foreign_cli_link_is_refused(self):
        self._patched()
        (self.bin/'computer-use').symlink_to(self.dir/'elsewhere')
        with self.assertRaisesRegex(ValueError, 'not ours'):
            setup.setup(self.config, self.data, self.bin)
        self.assertEqual(self.calls, [])

class RerunAndDriftTests(_SetupFixture, unittest.TestCase):
    """The fixes that only show up on a second run or after a mid-build change."""

    def test_two_runs_in_a_row_succeed_with_a_repaired_hook(self):
        self._patched()
        self.declared()
        first = self.config.read_bytes()
        (self.root/'native/visuals-login.lua').unlink()      # missing owned hook
        again = self.declared()
        self.assertTrue(again['ok'])
        self.assertEqual(self.config.read_bytes(), first, 'the managed block is not duplicated')
        self.assertTrue((self.root/'native/visuals-login.lua').is_file(), 'hook repaired')
        self.assertEqual(self.config.read_text().count('-- computer-use-visuals-begin'), 1)

    def test_two_runs_keep_a_legacy_profile_byte_exact(self):
        self._patched()
        target = self.root/'native/agent-cursor.json'
        original = b'{"theme":"old","size":24,"restore_theme":"default","restore_size":24}\n'
        target.write_bytes(original)
        setup.setup(self.config, self.data, self.bin)   # an existing profile needs no flags
        setup.setup(self.config, self.data, self.bin)
        self.assertEqual(target.read_bytes(), original)

    def test_header_drift_after_the_build_publishes_nothing(self):
        self._patched()
        calls = {'n': 0}
        def drifting(*_a, **_k):
            calls['n'] += 1
            return 'abi' if calls['n'] == 1 else 'drifted'
        with mock.patch.object(setup, 'header_abi', new=mock.Mock(side_effect=drifting)):
            with self.assertRaisesRegex(RuntimeError, 'ABI drifted'):
                self.declared()
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertFalse((self.bin/'computer-use').exists())

    def test_runtime_drift_after_the_build_publishes_nothing(self):
        # The compositor reports the initial ABI, then a different one mid-build.
        versions = ['{"abiHash":"abi"}', '{"abiHash":"moved"}']
        def answer(argv, **kwargs):
            if argv[0] == 'hyprctl' and 'version' in argv:
                payload = versions.pop(0) if versions else '{"abiHash":"abi"}'
            elif argv[0] == 'hyprctl':
                payload = self.plugins
            else:
                return self._default(argv, **kwargs)
            return subprocess.CompletedProcess(argv, 0, payload, '')
        self.answer = answer
        self._patched()
        with self.assertRaisesRegex(RuntimeError, 'ABI drifted'):
            self.declared()
        self.assertFalse((self.root/'native/visuals.json').exists())

    def test_a_plugin_loaded_during_the_build_blocks_the_config(self):
        # Clean at preflight, one loaded by the time we are about to publish.
        inventories = ['[]', '["late-plugin"]']
        def answer(argv, **kwargs):
            if argv[0] == 'hyprctl' and 'plugin' in argv:
                return subprocess.CompletedProcess(
                    argv, 0, inventories.pop(0) if inventories else '[]', '')
            return self._default(argv, **kwargs)
        self.answer = answer
        self._patched()
        with self.assertRaisesRegex(RuntimeError, 'plugins are already loaded'):
            self.declared()
        self.assertNotIn('computer-use-visuals-begin', self.config.read_text())
        self._assert_nothing_installed_or_published()

    def _assert_nothing_installed_or_published(self):
        """The abort happens before the first write, so no artefact exists at all."""
        self.assertFalse((self.data/'agent-computer-use/plugins').exists())
        self.assertFalse((self.root/'native/agent-cursor.json').exists())
        self.assertFalse((self.root/'native/require-liquid').exists())
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertFalse((self.root/'native/visuals-login.lua').exists())
        self.assertFalse((self.bin/'computer-use').exists())

    def test_a_session_starting_mid_build_aborts_before_any_write(self):
        # Clean at preflight, then a session record appears while we build.
        seen = []
        def answer(argv, **kwargs):
            if argv[0] == 'hyprctl' and 'plugin' in argv:
                return subprocess.CompletedProcess(argv, 0, '[]', '')
            seen.append(argv)
            if any('build-glass' in part for part in argv):
                # The session starts only once the build is under way.
                self.snapshot.write_text('{"version":4}')
            return self._default(argv, **kwargs)
        self.answer = answer
        self._patched()
        with self.assertRaisesRegex(RuntimeError, 'aborted before anything was installed'):
            self.declared()
        self.assertIn('build-glass.py', ' '.join(' '.join(a) for a in seen))
        self._assert_nothing_installed_or_published()

    def test_the_manifest_carries_one_abi_key(self):
        self._patched()
        self.declared()
        raw = (self.root/'native/visuals.json').read_text()
        self.assertEqual(raw.count('"abi":'), 1, 'one abi key, not a duplicated one')
        manifest = json.loads(raw)
        self.assertEqual(list(manifest).count('abi'), 1)
        self.assertEqual(manifest['abi'], 'abi')

    def test_the_library_comes_from_the_source_tree_not_stdout(self):
        self._patched()
        glass = _glass()
        cursor = _cursor()
        with mock.patch.object(setup, '_load', new=mock.Mock(
                side_effect=lambda name, path: glass if 'cursor' not in name else cursor)):
            result = self.declared()
        self.assertTrue(result['ok'])
        source = Path(glass.install.call_args.args[0])
        self.assertEqual(source.name, 'hyprglass.so')
        self.assertTrue(source.is_file(), 'the built artefact, not the diagnostic line')
        self.assertNotIn('not installed', str(source))

    def test_setup_holds_the_session_lock_for_the_whole_run(self):
        self._patched()
        held = []
        import sys as _sys
        cursor_session = _sys.modules['cursor_session']
        cursor_session.owner_lock = mock.MagicMock(
            side_effect=lambda: _Lock(held))
        self.declared()
        self.assertEqual(held, [True, False], 'lock taken once and released')

    def test_invalid_profile_is_refused_before_any_build(self):
        self._patched()
        (self.root/'native/agent-cursor.json').write_text('{"theme":"bad name;","size":32}')
        with mock.patch.dict(sys.modules, {'cursor_theme': _theme()}):
            with self.assertRaises(ValueError):
                setup.setup(self.config, self.data, self.bin)
        self.assertEqual(self.calls, [])


class _Lock:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        self.log.append(True)
        return None

    def __exit__(self, *exc):
        self.log.append(False)
        return False


def _theme():
    module = mock.Mock()
    module.validate = mock.Mock(side_effect=lambda theme, size: (
        None if isinstance(theme, str) and 16 <= size <= 96 else (_ for _ in ()).throw(ValueError('bad'))))
    return module


class ManualRestoreDeclaration(_SetupFixture, unittest.TestCase):
    """One-time declared restore values, never a guessed or GTK baseline."""

    def test_a_new_profile_without_a_declaration_is_refused(self):
        self._patched()
        with self.assertRaisesRegex(ValueError, 'cannot be read back'):
            setup.setup(self.config, self.data, self.bin)
        self.assertEqual(self.calls, [], 'no external command ran')
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertFalse((self.root/'native/agent-cursor.json').exists())
        self.assertEqual(self.config.read_bytes(), b'# user config\n')

    def test_a_partial_declaration_is_refused(self):
        for args in (('Adwaita',), (None, 24)):
            self._patched()
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, 'both --restore'):
                setup.setup(self.config, self.data, self.bin, *args)
            self.assertEqual(self.calls, [], 'no external command ran')

    def test_an_invalid_declaration_is_refused(self):
        for theme, size in (('bad name;', 24), ('Adwaita', 7), ('Adwaita', 128),
                            ('Adwaita', '24'), ('', 24)):
            self._patched()
            with self.subTest(theme=theme, size=size), \
                    self.assertRaisesRegex(ValueError, 'invalid restore declaration'):
                setup.setup(self.config, self.data, self.bin, theme, size)
            self.assertEqual(self.calls, [], 'no external command ran')

    def test_an_existing_profile_with_the_same_declaration_is_accepted_and_untouched(self):
        self._patched()
        target = self.root/'native/agent-cursor.json'
        original = b'{"theme":"old","size":24,"restore_theme":"Adwaita","restore_size":24}\n'
        target.write_bytes(original)
        self.assertTrue(self.declared()['ok'], 'identical declaration is not a conflict')
        self.assertEqual(target.read_bytes(), original)

    def test_an_existing_profile_with_a_different_declaration_is_refused(self):
        self._patched()
        target = self.root/'native/agent-cursor.json'
        original = b'{"theme":"old","size":24,"restore_theme":"Adwaita","restore_size":24}\n'
        target.write_bytes(original)
        self.calls.clear()
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            setup.setup(self.config, self.data, self.bin, 'Bibata', 32)
        self.assertEqual(self.calls, [], 'no external command ran')
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertEqual(self.config.read_bytes(), b'# user config\n')

    def test_a_profile_created_during_build_is_not_overwritten(self):
        self._patched()
        target = self.root/'native/agent-cursor.json'
        original = b'{"theme":"old","size":24,"restore_theme":"Manual","restore_size":24}\n'
        default_run = self._default
        def changed_during_build(argv, **kwargs):
            if argv[0] == 'git' and not target.exists():
                target.write_bytes(original)
            return default_run(argv, **kwargs)
        self.answer = changed_during_build
        with self.assertRaisesRegex(RuntimeError, 'cursor profile changed during build'):
            self.declared()
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertEqual(self.config.read_bytes(), b'# user config\n')

    def test_a_profile_created_during_install_is_not_overwritten(self):
        cursor = self._patched()
        target = self.root/'native/agent-cursor.json'
        original = b'{"theme":"old","size":24,"restore_theme":"Manual","restore_size":24}\n'
        def install(_):
            target.write_bytes(original)
            return self.data/'icons/cu-agent-hash', False
        cursor.install.side_effect = install
        with self.assertRaisesRegex(RuntimeError, 'cursor profile changed during install'):
            self.declared()
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse((self.root/'native/visuals.json').exists())
        self.assertEqual(self.config.read_bytes(), b'# user config\n')

    def test_a_gtk_or_unknown_profile_is_refused_outright(self):
        for payload in (b'{"theme":"old","size":24,"restore_mode":"gtk"}',
                        b'{"theme":"old","size":24,"restore_mode":"x11"}'):
            self._patched()
            with self.subTest(payload=payload):
                (self.root/'native/agent-cursor.json').write_bytes(payload)
                with self.assertRaisesRegex(ValueError, 'only supports an explicit manual'):
                    setup.setup(self.config, self.data, self.bin)
                self.assertEqual(self.calls, [])

    def test_setup_never_touches_the_running_cursor(self):
        self._patched()
        self.declared()
        joined = ' '.join(' '.join(argv) for argv in self.calls)
        self.assertNotIn('gsettings', joined)
        self.assertNotIn('setcursor', joined)




if __name__ == '__main__':
    unittest.main()

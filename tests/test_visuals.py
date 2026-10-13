"""Fresh-login visuals loader. Every RPC path is mocked; no GUI, session or compositor."""
import hashlib
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import sys
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
_spec = importlib.util.spec_from_file_location('visuals', ROOT/'scripts/visuals.py')
visuals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(visuals)
REAL_ACTIVATE = visuals._activate


def sha(data):
    return hashlib.sha256(data).hexdigest()


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.library = self.dir / ('hyprglass-' + sha(b'library') + '.so')
        self.library.write_bytes(b'library')
        self.manifest = self.dir / 'visuals.json'
        profile=self.dir/'agent-cursor.json'
        profile.write_text(json.dumps({'theme':'fixture-agent','size':34,'restore_theme':'fixture-base','restore_size':24}))
        profile_patch=mock.patch.object(visuals.cursor_theme,'PROFILE',profile)
        profile_patch.start();self.addCleanup(profile_patch.stop)
        for name,value in [('SNAPSHOT',self.dir/'session.json'),('owner_lock',mock.Mock(side_effect=contextlib.nullcontext))]:
            patcher=mock.patch.object(visuals.cursor_session,name,new=value);patcher.start();self.addCleanup(patcher.stop)
        self.env = {'HYPRLAND_INSTANCE_SIGNATURE': 'fresh-login'}
        self.write()
        self.activation = mock.Mock(return_value=True)
        patcher = mock.patch.object(visuals, '_activate', new=self.activation)
        patcher.start()
        self.addCleanup(patcher.stop)
        fresh=mock.patch.object(visuals,'require_fresh_login');fresh.start();self.addCleanup(fresh.stop)

    def write(self, **changes):
        # No library parameter: 'library' must be settable like any other key.
        data = {'version': 1, 'abi': 'abi-hash', 'library': str(self.library),
                'profile_sha256': sha(visuals.OPTICS.read_bytes()),
                'setup_instance': 'setup-login'}
        data.update(changes)
        self.manifest.write_text(json.dumps(data))
        return data

    def test_successful_fresh_login_forwards_library_abi_and_env_once(self):
        self.write()
        result = visuals.login(self.manifest, self.env)
        self.assertEqual(result, {'ok': True})
        self.activation.assert_called_once_with(str(self.library.resolve()), 'abi-hash', self.env)

    def test_rejects_non_object_and_relative_library_before_activation(self):
        self.manifest.write_text('[]')
        with self.assertRaises(ValueError):visuals.login(self.manifest, self.env)
        self.write(library='relative.so')
        with self.assertRaisesRegex(ValueError, 'absolute'):visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_activation_wrapper_passes_the_fresh_login_gate(self):
        activate=mock.Mock()
        with mock.patch.object(visuals.runpy,'run_path',return_value={'activate':activate}),mock.patch.object(visuals,'require_fresh_login') as gate:
            REAL_ACTIVATE('library','abi',self.env)
            callback=activate.call_args.kwargs['before_load'];callback()
            gate.assert_called_once_with(self.env)

    def test_managed_login_establishes_gtk_baseline_before_marking_ready(self):
        directory=self.dir/'cu-agent-fixture'
        directory.mkdir()
        profile=visuals.cursor_theme.PROFILE
        profile.write_text(json.dumps({'theme':'cu-agent-fixture','size':34,'restore_mode':'gtk'}))
        self.write(cursor_directory=str(directory),cursor_tree_sha256='fixture')
        with mock.patch.object(visuals.cursor_theme,'search_roots',return_value=[self.dir]),mock.patch.object(visuals.runpy,'run_path',return_value={'tree_digest':lambda _: 'fixture'}),mock.patch.object(visuals.cursor_theme,'gtk_state',return_value=('GTK-base',24)),mock.patch.object(visuals.cursor_theme,'command',return_value='ok') as command:
            visuals.login(self.manifest,self.env)
            command.assert_called_once_with(self.env,'hyprctl','setcursor','GTK-base','24')
        self.assertEqual(json.loads(profile.read_text())['ready_instance'],'fresh-login')

    def test_retained_or_concurrent_session_prevents_activation(self):
        visuals.cursor_session.SNAPSHOT.write_text('{}')
        with self.assertRaisesRegex(RuntimeError,'retained session'):
            visuals.login(self.manifest,self.env)
        self.activation.assert_not_called()
        visuals.cursor_session.SNAPSHOT.unlink()
        with mock.patch.object(visuals.cursor_session,'owner_lock',side_effect=RuntimeError('another automation session')):
            with self.assertRaisesRegex(RuntimeError,'another automation'):
                visuals.login(self.manifest,self.env)
        self.activation.assert_not_called()

    def test_managed_cursor_search_path_and_tree_are_checked_before_activation(self):
        directory=self.dir/'cu-agent-fixture';directory.mkdir()
        visuals.cursor_theme.PROFILE.write_text(json.dumps({'theme':directory.name,'size':34,'restore_mode':'gtk'}))
        self.write(cursor_directory=str(directory),cursor_tree_sha256='fixture')
        with mock.patch.object(visuals.cursor_theme,'search_roots',return_value=[]):
            with self.assertRaisesRegex(ValueError,'Xcursor search path'):
                visuals.login(self.manifest,self.env)
        with mock.patch.object(visuals.cursor_theme,'search_roots',return_value=[self.dir]),mock.patch.object(visuals.runpy,'run_path',return_value={'tree_digest':lambda _: 'changed'}):
            with self.assertRaisesRegex(ValueError,'tree differs'):
                visuals.login(self.manifest,self.env)
        self.activation.assert_not_called()

    def test_symlinked_cursor_profile_refuses_before_activation(self):
        profile=visuals.cursor_theme.PROFILE
        original=profile.with_name('original.json')
        profile.rename(original);profile.symlink_to(original)
        with self.assertRaisesRegex(ValueError,'regular file'):
            visuals.login(self.manifest,self.env)
        self.activation.assert_not_called()

    def test_owner_lock_is_held_during_activation(self):
        held=[False]
        @contextlib.contextmanager
        def lock():
            held[0]=True
            try:yield
            finally:held[0]=False
        with mock.patch.object(visuals.cursor_session,'owner_lock',side_effect=lock):
            self.activation.side_effect=lambda *_:self.assertTrue(held[0])
            visuals.login(self.manifest,self.env)
        self.assertFalse(held[0])

    def test_refuses_inside_an_automation_session(self):
        self.write()
        for env in ({'HYPRLAND_INSTANCE_SIGNATURE': 'x', 'CU_SESSION_TOKEN': 't'}, self.env):
            with self.subTest(env=sorted(env)):
                with mock.patch.dict(os.environ, {'CU_SESSION_TOKEN': 't'}):
                    with self.assertRaisesRegex(RuntimeError, 'automation session'):
                        visuals.login(self.manifest, env)
        self.activation.assert_not_called()

    def test_version_must_be_exactly_integer_one(self):
        for value in (True, '1', 1.0, 2, None):
            with self.subTest(value=value):
                self.write(version=value)
                with self.assertRaisesRegex(ValueError, 'exactly the integer 1'):
                    visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_missing_or_empty_required_strings_are_refused(self):
        for key in ('abi', 'library', 'profile_sha256', 'setup_instance'):
            for value in ('', None, 5):
                with self.subTest(key=key, value=value):
                    self.write(**{key: value})
                    with self.assertRaisesRegex(ValueError, 'required strings'):
                        visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_library_filename_must_carry_its_own_digest(self):
        renamed = self.dir / 'hyprglass-deadbeef.so'
        self.library.rename(renamed)
        self.write(library=str(renamed))
        with self.assertRaisesRegex(ValueError, 'SHA256 in the filename'):
            visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_missing_library_file_is_refused_before_activation(self):
        self.library.unlink()
        with self.assertRaises(FileNotFoundError):
            visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_tampered_profile_digest_is_refused(self):
        self.write(profile_sha256=sha(b'other profile'))
        with self.assertRaisesRegex(ValueError, 'pinned optics'):
            visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_same_instance_as_setup_is_refused(self):
        self.write(setup_instance='fresh-login')
        with self.assertRaisesRegex(RuntimeError, 'refusing to reload'):
            visuals.login(self.manifest, self.env)
        self.activation.assert_not_called()

    def test_missing_compositor_instance_is_refused(self):
        self.write()
        for env in ({}, {'HYPRLAND_INSTANCE_SIGNATURE': '  '}, {'HYPRLAND_INSTANCE_SIGNATURE': ''}):
            with self.subTest(env=env):
                with self.assertRaisesRegex(RuntimeError, 'no compositor instance'):
                    visuals.login(self.manifest, env)
        self.activation.assert_not_called()

    def test_activation_failure_propagates_without_retry(self):
        self.write()
        failing = mock.Mock(side_effect=RuntimeError('plugins already loaded'))
        with mock.patch.object(visuals, '_activate', new=failing):
            with self.assertRaisesRegex(RuntimeError, 'plugins already loaded'):
                visuals.login(self.manifest, self.env)
        self.assertEqual(failing.call_count, 1, 'no retry, no fallback')


class AtomicWriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_writes_new_file_private_and_preserves_existing_mode(self):
        fresh = self.dir / 'fresh'
        visuals.atomic_write(fresh, b'new')
        self.assertEqual(fresh.read_bytes(), b'new')
        self.assertEqual(fresh.stat().st_mode & 0o777, 0o600)
        existing = self.dir / 'existing'
        existing.write_bytes(b'old')
        existing.chmod(0o644)
        visuals.atomic_write(existing, b'newer')
        self.assertEqual(existing.read_bytes(), b'newer')
        self.assertEqual(existing.stat().st_mode & 0o777, 0o644)

    def test_refuses_to_write_through_a_symlink(self):
        target = self.dir / 'target'
        target.write_bytes(b'untouched')
        link = self.dir / 'link'
        link.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            visuals.atomic_write(link, b'overwritten')
        self.assertEqual(target.read_bytes(), b'untouched')

    def test_refuses_non_regular_target(self):
        target=self.dir/'directory';target.mkdir()
        with self.assertRaisesRegex(ValueError, 'non-regular'):visuals.atomic_write(target, b'new')
        self.assertTrue(target.is_dir())

    def test_failure_leaves_the_old_bytes_and_no_temporary(self):
        existing = self.dir / 'existing'
        existing.write_bytes(b'old')
        with mock.patch.object(visuals.os, 'replace', side_effect=OSError('disk error')):
            with self.assertRaises(OSError):
                visuals.atomic_write(existing, b'new')
        self.assertEqual(existing.read_bytes(), b'old')
        self.assertEqual([p.name for p in self.dir.iterdir()], ['existing'],
                         'no temporary residue survives a failure')


class FreshLoginTests(unittest.TestCase):
    def test_process_age_not_wall_clock_controls_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'7').mkdir();(root/'uptime').write_text('1000.00 0.00')
            for age in (5,30,31,-1):
                with self.subTest(age=age):
                    (root/'7'/'stat').write_text('7 (fixture process) S '+'0 '*18+str((1000-age)*100))
                    with mock.patch.object(visuals,'PROC',root),mock.patch.object(visuals.os,'sysconf',return_value=100),mock.patch.object(visuals.subprocess,'check_output',return_value='[{"instance":"fresh","pid":7}]'):
                        if 0<=age<=30:visuals.require_fresh_login({'HYPRLAND_INSTANCE_SIGNATURE':'fresh'})
                        else:
                            with self.assertRaisesRegex(RuntimeError,'first 30 seconds'):
                                visuals.require_fresh_login({'HYPRLAND_INSTANCE_SIGNATURE':'fresh'})

    def test_inventory_or_proc_failure_refuses_instead_of_guessing(self):
        for payload in ('[]','{}','[{"instance":"fresh","pid":true}]'):
            with self.subTest(payload=payload),mock.patch.object(visuals.subprocess,'check_output',return_value=payload):
                with self.assertRaisesRegex(RuntimeError,'cannot verify'):
                    visuals.require_fresh_login({'HYPRLAND_INSTANCE_SIGNATURE':'fresh'})


if __name__ == '__main__':
    unittest.main()

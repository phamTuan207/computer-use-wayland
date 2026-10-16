import ctypes.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cursor_theme
import cursor_session


class CursorTheme(unittest.TestCase):
    def test_required_snapshot_records_exact_original_gtk_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=Path(tmp)/'profile.json'
            profile.write_text(json.dumps(dict(theme='cu-agent-v1',size=32,restore_theme='default',restore_size=24)))
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'Adwaita'",'24']) as command:
                saved=cursor_theme.snapshot({})
        self.assertEqual(saved['gtk_theme'],'Adwaita')
        self.assertEqual(saved['gtk_size'],24)
        self.assertEqual(saved['hypr_theme'],'default')
        probe=command.call_args_list[0].args
        self.assertIn(cursor_theme.THEME_CHECK_CODE,probe)
        self.assertEqual(probe[-2:],('cu-agent-v1','32'))

    def test_missing_profile_raises_before_desktop_calls(self):
        with patch.object(cursor_theme.Path,'is_file',return_value=False),patch.object(cursor_theme,'command') as command:
            with self.assertRaisesRegex(RuntimeError,'profile required'):cursor_theme.snapshot({})
            command.assert_not_called()

    def test_oversized_profile_rejected_before_desktop_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=Path(tmp)/'profile.json'
            profile.write_bytes(b'{"theme":"x",' + b' '*4096 + b'}')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'exceeds 4096'):cursor_theme.snapshot({})
                command.assert_not_called()

    def test_unloadable_asset_refuses_before_gtk_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            with patch.object(cursor_theme,'PROFILE',profile), \
                 patch.object(cursor_theme,'command',side_effect=subprocess.CalledProcessError(1,['probe'])) as command:
                with self.assertRaises(subprocess.CalledProcessError):cursor_theme.snapshot({})
                command.assert_called_once()

    def test_dot_and_dotdot_theme_names_rejected(self):
        for bad in ('.','..'):
            with self.subTest(bad=bad),patch.object(cursor_theme,'command') as command:
                with self.assertRaises(ValueError):cursor_theme.apply({},bad,32)
                command.assert_not_called()

    def test_invalid_theme_rejected_before_side_effects(self):
        with patch.object(cursor_theme,'command') as command:
            with self.assertRaises(ValueError):cursor_theme.apply({},'bad theme; injected',32)
            command.assert_not_called()

    def test_restore_keeps_distinct_gtk_and_compositor_values(self):
        saved=dict(gtk_theme='Adwaita',gtk_size=24,hypr_theme='default',hypr_size=32)
        with patch.object(cursor_theme,'command',return_value='ok') as command:
            cursor_theme.restore({},saved)
        self.assertEqual(command.call_args_list[0].args[-1],'Adwaita')
        self.assertEqual(command.call_args.args,({},'hyprctl','setcursor','default','32'))

    def test_failed_guardian_restore_preserves_snapshot(self):
        import cancel_hotkey
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp);snapshot=state/'session.json'
            snapshot.write_text(json.dumps(dict(version=4,token='a'*32,cursor={})))
            with patch.object(cursor_session,'SNAPSHOT',snapshot),patch.object(cursor_session,'STATE',state), \
                 patch.object(cancel_hotkey,'hotkey_off'),patch.object(cursor_theme,'restore',side_effect=RuntimeError('injected')):
                self.assertFalse(cursor_session.restore({}))
            self.assertTrue(snapshot.exists())

    def _profile(self,tmp,**extra):
        profile=Path(tmp)/'profile.json'
        data=dict(theme='cu-agent-v1',size=32,restore_theme='Manual-base',restore_size=32)
        data.update(extra)
        profile.write_text(json.dumps(data))
        return profile

    def test_declared_compositor_restore_stays_distinct_from_actual_gtk(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_theme='Manual-base',restore_size=32)
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'GTK-base'",'24']):
                saved=cursor_theme.snapshot({})
        self.assertEqual((saved['gtk_theme'],saved['gtk_size']),('GTK-base',24))
        self.assertEqual((saved['hypr_theme'],saved['hypr_size']),('Manual-base',32))

    def test_missing_restore_fields_refuse_before_desktop_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            profile.write_text(json.dumps({'theme':'cu-agent-v1','size':34}))
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaises(KeyError):cursor_theme.snapshot({})
                command.assert_not_called()

    def test_gtk_guessing_policy_is_refused_before_desktop_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_mode='gtk')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'unknown restore_mode'):
                    cursor_theme.snapshot({})
                command.assert_not_called()

    def test_unknown_restore_mode_is_refused_before_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_mode='guess')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'unknown restore_mode'):
                    cursor_theme.snapshot({'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'})
                command.assert_not_called()

    def test_agent_theme_is_validated_before_any_instance_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,theme='bad theme; injected')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaises(ValueError):
                    cursor_theme.snapshot({'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'})
                command.assert_not_called()

    def test_invalid_gtk_values_refuse_before_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            env={'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'}
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'ok'",'24']):
                saved=cursor_theme.snapshot(env)
        with patch.object(cursor_theme,'command',return_value='ok') as command:
            cursor_theme.apply({},'cu-agent-v1',saved['agent_size'])
        self.assertEqual(command.call_args_list[-1].args[:3],({},'hyprctl','setcursor'))


class SearchRoots(unittest.TestCase):
    """The Xcursor search path, read from the library rather than assumed."""

    def test_it_runs_one_static_ctypes_probe_with_the_supplied_env(self):
        env={'XCURSOR_PATH':'/override','PATH':'/usr/bin'}
        with patch.object(cursor_theme,'command',return_value='/usr/share/icons') as command:
            roots=cursor_theme.search_roots(env)
        command.assert_called_once_with(env, sys.executable, '-c',
                                        cursor_theme.SEARCH_ROOTS_CODE)
        code=cursor_theme.SEARCH_ROOTS_CODE
        self.assertIn("ctypes.CDLL('libXcursor.so.1')", code)
        self.assertIn('XcursorLibraryPath.restype = ctypes.c_char_p', code)
        self.assertIn('.decode()', code)
        self.assertEqual(roots, [Path('/usr/share/icons')])

    def test_the_environment_override_and_tilde_are_expanded(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, {'HOME': home}), \
             patch.object(cursor_theme,'command',return_value='~/.local/share/icons:/tmp/x:'):
            roots=cursor_theme.search_roots({})
        self.assertEqual(roots, [Path(home).resolve()/'.local/share/icons', Path('/tmp/x')])
        self.assertTrue(all(root.is_absolute() for root in roots))

    def test_empty_and_blank_components_are_dropped(self):
        for raw, expected in (('', []), (':', []), ('/a::/b', [Path('/a'), Path('/b')])):
            with self.subTest(raw=raw), patch.object(cursor_theme,'command',return_value=raw):
                self.assertEqual(cursor_theme.search_roots({}), expected)

    def test_a_missing_library_fails_loudly(self):
        with patch.object(cursor_theme,'command',
                          side_effect=subprocess.CalledProcessError(1, 'probe')):
            with self.assertRaises(subprocess.CalledProcessError):
                cursor_theme.search_roots({})

    @unittest.skipUnless(ctypes.util.find_library('Xcursor'),
                         'libXcursor.so.1 is not installed here')
    def test_real_probe_reports_absolute_paths_without_a_display(self):
        env=dict(os.environ)
        env.pop('XCURSOR_PATH', None)
        env.pop('DISPLAY', None)
        env.pop('WAYLAND_DISPLAY', None)
        roots=cursor_theme.search_roots(env)
        self.assertIsInstance(roots, list)
        self.assertTrue(roots, 'a compiled Xcursor default is always reported')
        self.assertTrue(all(root.is_absolute() for root in roots))


if __name__ == '__main__':
    unittest.main()

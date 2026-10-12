import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cursor_theme
import cursor_session


class CursorTheme(unittest.TestCase):
    def test_opt_in_snapshot_and_exact_original_gtk_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=Path(tmp)/'profile.json'
            profile.write_text(json.dumps(dict(theme='cu-agent-v1',size=32,restore_theme='default',restore_size=24)))
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=["'Adwaita'",'24']):
                saved=cursor_theme.snapshot({})
        self.assertEqual(saved['gtk_theme'],'Adwaita')
        self.assertEqual(saved['gtk_size'],24)
        self.assertEqual(saved['hypr_theme'],'default')

    def test_no_profile_makes_no_desktop_calls(self):
        with patch.object(cursor_theme.Path,'is_file',return_value=False),patch.object(cursor_theme,'command') as command:
            self.assertIsNone(cursor_theme.snapshot({}))
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

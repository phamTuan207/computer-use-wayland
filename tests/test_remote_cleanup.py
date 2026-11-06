"""Remote shells need the refreshed compositor environment during cleanup."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cancel_hotkey
import cursor_session


class RemoteCleanup(unittest.TestCase):
    def test_hotkey_cleanup_passes_supplied_environment_to_hyprctl(self):
        env = {'HYPRLAND_INSTANCE_SIGNATURE': 'current-test-session'}
        with patch.object(cancel_hotkey.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = 'ok\n'
            cancel_hotkey.hotkey_off(env)
            self.assertIs(run.call_args.kwargs['env'], env)
            self.assertEqual(run.call_args.args[0][:2], ['hyprctl', 'eval'])

    def test_restore_carries_refreshed_environment_and_preserves_escape_latch(self):
        env = {'HYPRLAND_INSTANCE_SIGNATURE': 'current-test-session'}
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            snapshot = state / 'session.json'
            snapshot.write_text(json.dumps({'version': 4, 'token': 'a' * 32}))
            latch = state / 'cancelled'
            latch.write_text('physical Escape')
            with patch.object(cursor_session, 'STATE', state), \
                 patch.object(cursor_session, 'SNAPSHOT', snapshot), \
                 patch.object(cancel_hotkey, 'hotkey_off') as off:
                self.assertTrue(cursor_session.restore(env))
                off.assert_called_once_with(env)
                self.assertFalse(snapshot.exists())
                self.assertEqual(latch.read_text(), 'physical Escape')


class PreservedMachineBehavior(unittest.TestCase):
    def test_stop_waits_for_owner_before_restoring(self):
        from contextlib import nullcontext
        with patch.object(cursor_session, 'request_stop') as request, \
             patch.object(cursor_session, 'owner_lock', side_effect=[RuntimeError('busy'), nullcontext()]), \
             patch.object(cursor_session.time, 'sleep'), \
             patch.object(cursor_session, 'drain_input') as drain, \
             patch.object(cursor_session, 'restore', return_value=True) as restore:
            env = {'test': 'desktop'}
            self.assertEqual(cursor_session.stop(env), 0)
            request.assert_called_once_with()
            drain.assert_called_once_with()
            restore.assert_called_once_with(env)

    def test_stop_timeout_leaves_owner_cleanup_intact(self):
        with patch.object(cursor_session, 'request_stop'), \
             patch.object(cursor_session, 'owner_lock', side_effect=RuntimeError('busy')), \
             patch.object(cursor_session, 'restore') as restore:
            with self.assertRaisesRegex(RuntimeError, 'cleanup still owns the desktop'):
                cursor_session.stop({}, timeout=0)
            restore.assert_not_called()

    def test_replace_stops_before_starting_and_refuses_failed_cleanup(self):
        import cu
        for result in (0, 1):
            with self.subTest(cleanup_result=result), \
                 patch.object(cu.sys, 'argv', ['cu', 'session', '--replace', '--', 'driver']), \
                 patch.object(cu, 'environment', return_value={'test': 'desktop'}), \
                 patch.object(cu.os, 'environ', {}), \
                 patch.object(cursor_session, 'stop', return_value=result) as stop, \
                 patch.object(cursor_session, 'supervise', return_value=0) as supervise:
                calls = []
                stop.side_effect = lambda env: calls.append('stop') or result
                supervise.side_effect = lambda env, driver: calls.append('start') or 0
                self.assertEqual(cu.main(), result)
                self.assertEqual(calls, ['stop', 'start'] if result == 0 else ['stop'])

    def test_keyd_and_physical_keyboard_included_agent_keyboard_excluded(self):
        names = ['keyd-virtual-keyboard', 'at-translated-set-2-keyboard',
                 'agent-virtual-keyboard', 'power-button']
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(cancel_hotkey, 'STATE', Path(directory)), \
             patch.object(cancel_hotkey.subprocess, 'run') as run, \
             patch.object(cancel_hotkey, 'hypr_eval') as evaluate:
            run.return_value.stdout = json.dumps({'keyboards': [{'name': n} for n in names]})
            cancel_hotkey.hotkey_on()
            code = evaluate.call_args.args[0]
            self.assertIn('keyd-virtual-keyboard', code)
            self.assertIn('at-translated-set-2-keyboard', code)
            self.assertNotIn('agent-virtual-keyboard', code)
            self.assertNotIn('power-button', code)


if __name__ == '__main__':
    unittest.main()

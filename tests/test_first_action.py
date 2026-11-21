"""Tests for the first-visible-action fast path (scripts/first_action.py).

Run: python3 -m pytest tests/test_first_action.py -q
Or:  python3 tests/test_first_action.py (stdlib runner at the bottom).
VM only. No laptop, no Zen, no network, no desktop.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import first_action  # noqa: E402


class FakeOverlay:
    """Stand-in for the overlay module: records calls, answers acquire."""

    def __init__(self, visible=True):
        self.visible = visible
        self.calls = []
        self.holders = {}

    def add_holder(self, agent, method, pid=None):
        self.calls.append(('add', agent, method, pid))
        self.holders[agent] = {'method': method, 'pid': pid}
        return self.holders, True

    def _ensure_daemon(self):
        self.calls.append(('ensure',))

    def _send_socket(self, req):
        self.calls.append(('send', req.get('command'), req.get('agent')))
        if req.get('command') == 'acquire':
            return {'visible': self.visible, 'owner': 'daemon',
                    'holders': self.holders, 'label': 'Muse via act-now'}
        if req.get('command') == 'release':
            self.holders.pop(req.get('agent'), None)
            return {'visible': bool(self.holders), 'owner': 'none',
                    'holders': self.holders}
        return {'visible': bool(self.holders)}

    def _label_for(self, agent, method):
        return (agent + ' via ' + method)[:40]

    def remove_holder(self, agent):
        self.calls.append(('remove', agent))
        self.holders.pop(agent, None)
        return self.holders, True

    def session_live(self):
        return False


class FakeCu:
    """Stand-in for the cu module: no desktop, no Hyprland."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.state = self.tmp / 'state'
        self.state.mkdir(parents=True, exist_ok=True)
        self.STATE = self.state
        self.desktop_calls = []
        self.observe_calls = []

    def environment(self):
        return {'WAYLAND_DISPLAY': 'wayland-1',
                'XDG_RUNTIME_DIR': '/run/user/1000'}

    def read_json_file(self, path):
        return json.loads(Path(path).read_text())

    def observe_screen(self, env, monitor, max_width=960, persist=True,
                       low_res=False):
        self.observe_calls.append(monitor)
        meta = {'id': 'a1b2c3d4e5f6',
                'observation': str(self.state / 'a1b2c3d4e5f6.json'),
                'image': str(self.state / 'a1b2c3d4e5f6.jpg'),
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time()}
        return meta

    def desktop_act(self, env, meta, actions, observation_path=None,
                    **kwargs):
        self.desktop_calls.append((meta.get('id'), len(actions)))
        return {'ok': True, 'completed': len(actions),
                'after': str(self.state / 'after.json')}

    @contextlib.contextmanager
    def locked(self):
        yield


def _write_actions(tmp, actions):
    path = Path(tmp) / 'actions.json'
    path.write_text(json.dumps(actions))
    return str(path)


def _args(actions_path, **overrides):
    base = {'actions': actions_path, 'observation': None,
            'screen': 'eDP-2', 'agent': 'Muse', 'method': 'act-now',
            'label': None, 'session_deadline_s': 20.0}
    base.update(overrides)
    return mock.Mock(**base)


class TestSessionStartFailure(unittest.TestCase):
    def test_guardian_json_error(self):
        self.assertTrue(first_action.is_session_start_failure(
            '{"ok": false, "error": "session guardian startup failed"}',
            '', False, False))

    def test_expecting_value_stderr(self):
        self.assertTrue(first_action.is_session_start_failure(
            '', 'json.decoder.JSONDecodeError: Expecting value: line 1 '
            'column 1 (char 0)', False, False))

    def test_cursor_guard_stderr(self):
        self.assertTrue(first_action.is_session_start_failure(
            '', 'cursor guard did not confirm ownership', False, False))

    def test_act_failure_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            '', 'screen changed', False, False))
        self.assertFalse(first_action.is_session_start_failure(
            '', 'focus changed', False, False))

    def test_timeout_live_session_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            '', '', True, True))

    def test_timeout_no_session_falls_back(self):
        self.assertTrue(first_action.is_session_start_failure(
            '', '', True, False))


class TestAttemptSession(unittest.TestCase):
    def test_success(self):
        rc, out, err, timed_out, _ = first_action.attempt_session(
            [sys.executable, '-c', 'print("hi")'], 5)
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), 'hi')
        self.assertFalse(timed_out)

    def test_failure(self):
        rc, _out, _err, timed_out, _ = first_action.attempt_session(
            [sys.executable, '-c', 'raise SystemExit(3)'], 5)
        self.assertEqual(rc, 3)
        self.assertFalse(timed_out)

    def test_timeout_kills_group(self):
        start = time.monotonic()
        rc, _out, _err, timed_out, elapsed = first_action.attempt_session(
            [sys.executable, '-c', 'import time; time.sleep(30)'], 0.5)
        self.assertTrue(timed_out)
        self.assertLess(time.monotonic() - start, 10)


class TestSessionCmd(unittest.TestCase):
    def test_shape(self):
        cmd = first_action.session_cmd('/x/cu.py', '/o.json', '/a.json')
        self.assertEqual(cmd[0], sys.executable)
        self.assertEqual(cmd[1], '/x/cu.py')
        self.assertEqual(cmd[2], 'session')
        self.assertEqual(cmd[3], '--')
        self.assertIn('act', cmd)
        self.assertIn('/o.json', cmd)
        self.assertIn('/a.json', cmd)


class TestAcquireOverlay(unittest.TestCase):
    def test_visible(self):
        fake = FakeOverlay(visible=True)
        reply = first_action.acquire_overlay('Muse', 'act-now',
                                             overlay_mod=fake)
        self.assertTrue(reply['visible'])
        self.assertIn(('add', 'Muse', 'act-now', os.getpid()),
                      fake.calls)

    def test_not_visible_refuses(self):
        fake = FakeOverlay(visible=False)
        with self.assertRaises(RuntimeError):
            first_action.acquire_overlay('Muse', 'act-now', overlay_mod=fake)

    def test_daemon_start_failure_refuses(self):
        fake = FakeOverlay(visible=True)
        fake._ensure_daemon = mock.Mock(
            side_effect=RuntimeError('overlay daemon exited'))
        with self.assertRaises(RuntimeError):
            first_action.acquire_overlay('Muse', 'act-now', overlay_mod=fake)

    def test_release_never_raises(self):
        fake = FakeOverlay(visible=True)
        fake._send_socket = mock.Mock(side_effect=OSError('no socket'))
        first_action.release_overlay('Muse', overlay_mod=fake)


class TestAppendLog(unittest.TestCase):
    def test_writes_json_line_0600(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'first-action-20261121.jsonl'
            first_action.append_log(path, {'ok': True, 'path': 'fallback'})
            self.assertEqual(oct(path.stat().st_mode & 0o777), '0o600')
            lines = path.read_text().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])['path'], 'fallback')


class TestRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fake_cu = FakeCu(self.tmp.name)
        self.fake_overlay = FakeOverlay(visible=True)
        self._cu_mod = sys.modules.get('cu')
        self._ov_mod = sys.modules.get('overlay')
        sys.modules['cu'] = self.fake_cu
        sys.modules['overlay'] = self.fake_overlay

    def tearDown(self):
        if self._cu_mod is None:
            sys.modules.pop('cu', None)
        else:
            sys.modules['cu'] = self._cu_mod
        if self._ov_mod is None:
            sys.modules.pop('overlay', None)
        else:
            sys.modules['overlay'] = self._ov_mod
        self.tmp.cleanup()

    def _run(self, actions, session_result):
        path = _write_actions(self.tmp.name, actions)
        with mock.patch.object(first_action, 'attempt_session',
                               return_value=session_result):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(_args(path))
        return code, json.loads(buf.getvalue()), path

    def test_session_path(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['completed'], 1)
        self.assertIsNotNone(env['order_to_overlay_ms'])
        self.assertLess(env['order_to_overlay_ms'], 30000)
        self.assertEqual(self.fake_cu.desktop_calls, [])
        self.assertEqual(self.fake_overlay.holders, {})
        log = list(self.fake_cu.state.glob('first-action-*.jsonl'))
        self.assertEqual(len(log), 1)

    def test_fallback_path_on_guardian_failure(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertIn('guardian', env['fallback_reason'])
        self.assertEqual(len(self.fake_cu.desktop_calls), 1)
        self.assertEqual(self.fake_overlay.holders, {})

    def test_act_failure_not_replayed(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '', 'screen changed', False, 5.0))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_overlay_refusal(self):
        self.fake_overlay.visible = False
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5))
        self.assertEqual(code, 2)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'refused')
        self.assertEqual(self.fake_cu.desktop_calls, [])


class TestFreshObservation(unittest.TestCase):
    def test_given_fresh_used(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time()}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        out_meta, out_path, source = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path))
        self.assertEqual(source, 'given')
        self.assertEqual(out_meta['id'], 'deadbeefcafe')
        self.assertEqual(fake_cu.observe_calls, [])

    def test_stale_replaced_by_capture(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time() - 600}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path))
        self.assertEqual(source, 'captured')
        self.assertEqual(fake_cu.observe_calls, ['eDP-2'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

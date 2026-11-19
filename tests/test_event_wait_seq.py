"""Unit tests for the event-wait-seq prototype (Rank 4 + H4 then flag).

No live desktop needed: wait_for_event is tested against a real Unix
event socket served by a thread in the test, plus already:true paths
through a stubbed cu.hypr. No broker session, no relay, no pointer.
"""
import importlib.util
import os
import pathlib
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'cu.py'
spec = importlib.util.spec_from_file_location('cu', path)
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)

CLIENTS = [{'address': '0xabc', 'class': 'kitty', 'title': 'term',
            'workspace': {'id': 1, 'name': '1'}},
           {'address': '0xdef', 'class': 'firefox', 'title': 'Inbox - Mail',
            'workspace': {'id': 2, 'name': '2'}}]
MONITORS = [{'name': 'eDP-1', 'activeWorkspace': {'id': 1, 'name': '1'}}]


def fake_hypr(env, what):
    if what == 'clients':
        return [dict(c) for c in CLIENTS]
    if what == 'activewindow':
        return dict(CLIENTS[0])
    if what == 'monitors':
        return [dict(m) for m in MONITORS]
    raise AssertionError('unexpected hypr query: ' + what)


ENV = {'XDG_RUNTIME_DIR': '/run/user/1000', 'HYPRLAND_INSTANCE_SIGNATURE': 'test-sig',
       'WAYLAND_DISPLAY': 'wayland-1'}


class ValidateWaitFor(unittest.TestCase):
    def test_valid_minimal(self):
        self.assertEqual(cu.validate_wait_for({'type': 'wait_for', 'event': 'openwindow'}),
                         {'type': 'wait_for', 'event': 'openwindow'})

    def test_valid_full(self):
        step = {'type': 'wait_for', 'event': 'activewindow', 'timeout_ms': 1500,
                'address': '0xabc', 'title': 'term', 'expect_focus': 'any'}
        self.assertEqual(cu.validate_wait_for(step), step)

    def test_rejects_unknown_event(self):
        with self.assertRaises(ValueError):
            cu.validate_wait_for({'type': 'wait_for', 'event': 'explode'})

    def test_rejects_bad_timeout(self):
        for bad in (-1, 30001, 1.5, True, '5000'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                cu.validate_wait_for({'type': 'wait_for', 'event': 'workspace', 'timeout_ms': bad})

    def test_rejects_bad_address_and_unknown_key(self):
        with self.assertRaises(ValueError):
            cu.validate_wait_for({'type': 'wait_for', 'event': 'closewindow', 'address': 'abc'})
        with self.assertRaises(ValueError):
            cu.validate_wait_for({'type': 'wait_for', 'event': 'workspace', 'surprise': 1})

    def test_rejects_bad_expect_focus(self):
        with self.assertRaises(ValueError):
            cu.validate_wait_for({'type': 'wait_for', 'event': 'openwindow', 'expect_focus': 'somewhere'})

    def test_validate_actions_accepts_wait_for_in_desktop_batch(self):
        cu.validate_actions([{'type': 'click', 'x': 10, 'y': 10},
                             {'type': 'wait_for', 'event': 'windowtitle', 'title': 'Save'},
                             {'type': 'key', 'keys': ['Return']}], 'desktop')

    def test_validate_actions_rejects_wait_for_in_a11y(self):
        with self.assertRaises(ValueError):
            cu.validate_actions([{'type': 'wait_for', 'event': 'openwindow'}], 'a11y')


class SequenceGrouping(unittest.TestCase):
    def test_wait_for_is_its_own_group_between_keyboard_groups(self):
        actions = [{'type': 'type', 'text': 'hello'},
                   {'type': 'wait_for', 'event': 'windowtitle', 'title': 'Save'},
                   {'type': 'key', 'keys': ['Return']}]
        groups = cu.keyboard_groups(actions)
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[1], actions[1])
        self.assertIsInstance(groups[0], list)
        self.assertIsInstance(groups[2], list)

    def test_click_type_enter_stays_grouped_around_wait(self):
        actions = [{'type': 'click', 'x': 5, 'y': 5},
                   {'type': 'type', 'text': 'x'},
                   {'type': 'wait_for', 'event': 'openwindow', 'class': 'kitty'},
                   {'type': 'type', 'text': 'y'}]
        groups = cu.keyboard_groups(actions)
        self.assertEqual(groups[2], actions[2])


class WaitForAlready(unittest.TestCase):
    def test_openwindow_already_true(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            result = cu.wait_for_event(ENV, {'event': 'openwindow', 'class': 'kitty'}, 5000)
        self.assertTrue(result['ok'])
        self.assertTrue(result['already'])
        self.assertEqual(result['matched']['address'], '0xabc')
        self.assertLess(result['elapsed_ms'], 1000)

    def test_activewindow_by_title_substring(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            result = cu.wait_for_event(ENV, {'event': 'activewindow', 'title': 'TER'}, 5000)
        self.assertTrue(result['already'])
        self.assertEqual(result['matched']['title'], 'term')

    def test_workspace_by_name(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            result = cu.wait_for_event(ENV, {'event': 'workspace', 'workspace': '1'}, 5000)
        self.assertTrue(result['already'])

    def test_closewindow_already_gone(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            result = cu.wait_for_event(ENV, {'event': 'closewindow', 'address': '0x999'}, 5000)
        self.assertTrue(result['already'])
        self.assertEqual(result['matched'], {'gone': True})

    def test_zero_timeout_is_pure_already_check(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            result = cu.wait_for_event(ENV, {'event': 'openwindow', 'class': 'nope'}, 0)
        self.assertFalse(result['ok'])
        self.assertTrue(result['timed_out'])

    def test_missing_socket_raises_for_live_wait(self):
        with patch.object(cu, 'hypr', side_effect=fake_hypr):
            with self.assertRaises(RuntimeError):
                cu.wait_for_event(ENV, {'event': 'openwindow', 'class': 'nope'}, 1000)


class EventSocketServer:
    """A real Unix event socket serving scripted lines, like .socket2.sock."""

    def __init__(self, tmpdir, lines, delay=0.05):
        self.dir = pathlib.Path(tmpdir) / 'hypr' / 'test-sig'
        self.dir.mkdir(parents=True)
        self.sock_path = self.dir / '.socket2.sock'
        self.lines = lines
        self.delay = delay
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.sock_path))
        self.server.listen(1)
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self):
        try:
            conn, _ = self.server.accept()
            with conn:
                for line in self.lines:
                    time.sleep(self.delay)
                    conn.sendall(line.encode() + b'\n')
                time.sleep(0.5)
        except OSError:
            pass

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        try:
            self.server.close()
        except OSError:
            pass
        return False


def socket_env(tmpdir):
    return {'XDG_RUNTIME_DIR': tmpdir, 'HYPRLAND_INSTANCE_SIGNATURE': 'test-sig',
            'WAYLAND_DISPLAY': 'wayland-1'}


class WaitForLiveSocket(unittest.TestCase):
    def test_openwindow_match_arrives_over_socket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with EventSocketServer(tmpdir, ['openwindow>>0xabc,1,kitty,term']):
                with patch.object(cu, 'hypr', side_effect=lambda env, what: [] if what == 'clients' else
                                  ({'address': ''} if what == 'activewindow' else [])):
                    result = cu.wait_for_event(socket_env(tmpdir),
                                               {'event': 'openwindow', 'class': 'kitty',
                                                'title': 'term'},
                                               5000)
        self.assertTrue(result['ok'])
        self.assertFalse(result['already'])
        self.assertEqual(result['matched']['address'], '0xabc')
        self.assertEqual(result['matched']['class'], 'kitty')
        self.assertEqual(result['matched']['title'], 'term')

    def test_unrelated_lines_are_skipped_then_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with EventSocketServer(tmpdir, ['workspace>>2',
                                            'openwindow>>0x777,2,kitty,other']):
                with patch.object(cu, 'hypr', side_effect=lambda env, what: [] if what == 'clients' else
                                  ({'address': ''} if what == 'activewindow' else [])):
                    result = cu.wait_for_event(socket_env(tmpdir),
                                               {'event': 'openwindow', 'class': 'kitty'}, 5000)
        self.assertTrue(result['ok'])
        self.assertFalse(result['already'])
        self.assertEqual(result['matched']['address'], '0x777')
        self.assertEqual(result['matched']['title'], 'other')

    def test_timeout_returns_timed_out_not_hang(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with EventSocketServer(tmpdir, []):
                with patch.object(cu, 'hypr', side_effect=lambda env, what: [] if what == 'clients' else
                                  ({'address': ''} if what == 'activewindow' else [])):
                    start = time.monotonic()
                    result = cu.wait_for_event(socket_env(tmpdir),
                                               {'event': 'openwindow', 'class': 'nope'}, 200)
                    elapsed = (time.monotonic() - start) * 1000
        self.assertFalse(result['ok'])
        self.assertTrue(result['timed_out'])
        self.assertGreaterEqual(result['elapsed_ms'], 150)
        self.assertLess(elapsed, 3000)


class ThenFlag(unittest.TestCase):
    def test_then_conflicts_with_no_after(self):
        import io
        argv = ['cu.py', 'act', '--observation', 'nope.json',
                '--actions', '-', '--then', '--no-after']
        with patch.object(cu, 'environment', return_value=dict(ENV)), \
                patch.object(cu, 'check_cancel', return_value=None), \
                patch.dict(os.environ, {'CU_SESSION_TOKEN': 'fixture'}), \
                patch.object(sys, 'argv', argv), \
                patch('sys.stdin', io.StringIO('[]')):
            with self.assertRaises(ValueError) as ctx:
                cu.main()
        self.assertIn('--then requires', str(ctx.exception))

    def test_compact_result_keeps_then_like_after(self):
        result = {'ok': True, 'completed': 1,
                  'after': {'image': '/tmp/x.png', 'image_size': [100, 50], 'backend': 'desktop',
                            'scope': 'window', 'window': '0xabc', 'window_bounds': [0, 0, 100, 50],
                            'monitor': 'eDP-1', 'monitor_box': [0, 0, 100, 50], 'monitor_scale': 1,
                            'monitor_transform': 0, 'region': [0, 0, 100, 50], 'crop': None,
                            'capture_ms': 1, 'decode_ms': 1, 'encode_ms': 1, 'capture_elapsed_ms': 1,
                            'capture_started_wall': 1, 'capture_started_monotonic': 1,
                            'capture_boot_id': 'b', 'capture_compositor': 'c',
                            'observation_schema': 1, 'image_role': 'clean-observation',
                            'image_format': 'PNG', 'image_bytes': 10, 'image_sha256': 's',
                            'pixel_sha256': 'p', 'id': 'aabbcc', 'observation': '/tmp/x.json',
                            'created': 1, 'max_width': 960}}
        result['then'] = result['after']
        compacted = cu.compact_result(result)
        self.assertIn('then', compacted)
        self.assertEqual(compacted['then']['image'], '/tmp/x.png')
        self.assertEqual(compacted['after']['image'], '/tmp/x.png')


if __name__ == '__main__':
    unittest.main()

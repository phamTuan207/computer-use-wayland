"""Session re-observe policy: transient refusals keep the session, all else kills it.

Production truth: scripts/session_policy.py, cu.is_transient_refusal, the
focus/screen refusal envelopes, the act/observe/a11y/browser session wiring
in cu.main, and the session_driver execute/relay envelope. Real
execute()/main()/desktop_act throughout; only compositor/capture/input are
mocked. STATE is always a temp dir, never the real cache.
"""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu
import session_driver
import session_policy
from session_policy import (
    complete_requirement,
    marker_path,
    read_marker,
    record_observation,
    record_refusal,
    require_observation,
)

ADDR = '0xabc'
WAIT = json.dumps([{'type': 'wait', 'ms': 10}])


def base_meta(**over):
    meta = {'backend': 'desktop', 'created': time.time(), 'window': ADDR,
            'window_bounds': [0, 0, 20, 20], 'monitor': 'test',
            'monitor_box': [0, 0, 20, 20], 'monitor_scale': 1,
            'monitor_transform': 0, 'image_size': [20, 20],
            'region': [0, 0, 20, 20], 'image': 'synthetic.png',
            'max_width': 1280, 'pixel_sha256': '0000'}
    meta.update(over)
    return meta


@contextlib.contextmanager
def live(tmp, token, *, active, pre_calls, post, opened, close_error=None):
    """Patch cu below desktop_act; active/pre_calls are consumed in order."""
    from PIL import Image  # noqa: F401 (ensures Pillow present like prod)
    state = Path(tmp)
    stack = contextlib.ExitStack()
    with stack:
        stack.enter_context(patch.object(cu, 'STATE', state))
        stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': token}))
        stack.enter_context(patch.object(cu, 'check_cancel'))
        stack.enter_context(patch.object(cu, 'environment', return_value={}))
        stack.enter_context(patch.object(cu, 'focus'))
        stack.enter_context(patch.object(cu, 'window',
                                         return_value={'at': [0, 0], 'size': [20, 20]}))

        def hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20,
                         'height': 20, 'scale': 1}]
            if query == 'activewindow':
                return {'address': active.pop(0)}
            if query == 'cursorpos':
                return {'x': 5, 'y': 5}
            raise AssertionError('unexpected query ' + query)

        stack.enter_context(patch.object(cu, 'hypr', side_effect=hypr))

        def obs(*args, **kwargs):
            if kwargs.get('persist', True):
                if isinstance(post, Exception):
                    raise post
                return dict(post)
            image, fresh = pre_calls.pop(0)
            return image, dict(fresh)

        stack.enter_context(patch.object(cu, 'observe', side_effect=obs))
        stack.enter_context(patch.object(cu, 'observe_screen', side_effect=obs))
        pointer = MagicMock()
        if close_error is not None:
            pointer.close.side_effect = close_error
        stack.enter_context(patch.object(cu, 'Pointer', return_value=pointer))
        stack.enter_context(patch.object(cu, 'run_cancelable', return_value=''))
        stack.enter_context(patch.object(cu.shutil, 'which', return_value=None))
        stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))
        stack.enter_context(patch('PIL.Image.open', return_value=opened))
        stack.enter_context(patch('time.sleep'))
        stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
        yield stop


def relay_lines(lines):
    out = io.StringIO()
    code = session_driver.relay(io.StringIO('\n'.join(map(json.dumps, lines))), out)
    body = [json.loads(line) for line in out.getvalue().splitlines()]
    return code, body


class RefusalFlow(unittest.TestCase):
    def test_focus_refusal_keeps_session_then_fresh_act_succeeds(self):
        from PIL import Image
        token = 'c' * 32
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(base_meta()))
            obs2 = Path(tmp) / 'obs2.json'
            after = base_meta(pixel_sha256='1111')
            obs2.write_text(json.dumps(after))
            post = dict(after, observation=str(obs2))
            marker = Path(tmp) / ('session-reobserve-' + token + '.json')
            with live(tmp, token, active=['0xdead'] + [ADDR] * 8,
                       pre_calls=[(same, {})], post=post, opened=same) as stop:
                refusal = session_driver.execute(
                    ['act', '--observation', str(obs1), '--actions', '-',
                     '--verbose'], WAIT)
                self.assertEqual(refusal.returncode, 1)
                refused = json.loads(refusal.stdout)
                self.assertTrue(cu.is_transient_refusal(refused))
                self.assertEqual(refused['error_code'], 'focus_changed')
                self.assertIn('session refusal: error=focus changed'
                              ' action=require_reobserve', refusal.stderr)
                self.assertEqual(read_marker(marker), {'observation': None},
                                 'refusal records a null marker while open')
                observed = session_driver.execute(
                    ['observe', '--window', ADDR, '--verbose'], '')
                self.assertEqual(observed.returncode, 0)
                fresh = session_driver.execute(
                    ['act', '--observation', str(obs2), '--actions', '-',
                     '--verbose'], WAIT)
                self.assertEqual(fresh.returncode, 0)
                freshed = json.loads(fresh.stdout)
                self.assertTrue(freshed['ok'])
                self.assertNotIn('ime_restore_failed', freshed)
                self.assertFalse(marker.exists(),
                                 'complete_requirement unlinks after input')
                status = session_driver.execute(['status'], '')
                self.assertEqual(status.returncode, 0)
            stop.assert_not_called()

    def test_screen_refusal_keeps_session_then_fresh_act_succeeds(self):
        from PIL import Image
        token = 'd' * 32
        old, big, same = (Image.new('RGB', (20, 20)), Image.new('RGB', (30, 30)),
                          Image.new('RGB', (20, 20)))
        screen_meta = base_meta(scope='screen')
        del screen_meta['window']
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(screen_meta))
            obs2 = Path(tmp) / 'obs2.json'
            after = base_meta(scope='screen', pixel_sha256='2222')
            del after['window']
            obs2.write_text(json.dumps(after))
            post = dict(after, observation=str(obs2))
            opened = {'first': old, 'second': same}
            with live(tmp, token, active=[], pre_calls=[(big, {}), (same, {})],
                       post=post, opened=None) as stop:
                # opened differs per pre-capture: stale vs settled image.
                with patch('PIL.Image.open',
                           side_effect=lambda *a: opened.pop('first' if 'first' in opened else 'second')):
                    code, body = relay_lines([
                        {'args': ['act', '--observation', str(obs1),
                                  '--actions', '-', '--verbose'], 'stdin': WAIT},
                        {'args': ['observe', '--screen', 'test', '--verbose']},
                        {'args': ['act', '--observation', str(obs2),
                                  '--actions', '-', '--verbose'], 'stdin': WAIT},
                        {'args': ['status']},
                    ])
        self.assertEqual(code, 0, 'refusal must not stop the relay')
        refusal, observed, fresh, _ = body[1:]
        self.assertEqual(refusal['returncode'], 1)
        self.assertTrue(cu.is_transient_refusal(refusal['result']))
        self.assertEqual(refusal['result']['error_code'], 'screen_changed')
        self.assertIn('after', refusal['result'])
        self.assertIn('session refusal: error=screen changed'
                      ' action=require_reobserve', refusal['stderr'])
        self.assertTrue(fresh['result']['ok'])
        stop.assert_not_called()


class RequirementGate(unittest.TestCase):
    def test_act_without_reobserve_after_refusal_blocked(self):
        from PIL import Image
        token = 'e' * 32
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=['0xdead'], pre_calls=[],
                       post={}, opened=Image.new('RGB', (20, 20))) as stop:
                first = session_driver.execute(
                    ['act', '--observation', str(obs1), '--actions', '-',
                     '--verbose'], WAIT)
                self.assertEqual(first.returncode, 1)
                self.assertTrue(cu.is_transient_refusal(json.loads(first.stdout)))
                marker = Path(tmp) / ('session-reobserve-' + token + '.json')
                self.assertEqual(read_marker(marker), {'observation': None})
                with patch.object(cu, 'desktop_act',
                                  side_effect=AssertionError('must not reach input')):
                    second = session_driver.execute(
                        ['act', '--observation', str(obs1), '--actions', '-',
                         '--verbose'], WAIT)
        self.assertEqual(second.returncode, 1, 'cross-execute marker must block')
        self.assertIn('fresh desktop observation required', second.stdout)
        self.assertNotIn('fresh desktop observation required', second.stderr)
        stop.assert_called_once()  # non-transient act error stops the session

    def test_stale_path_after_new_observe_blocked(self):
        from PIL import Image
        token = 'f' * 32
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(base_meta()))
            obs2 = Path(tmp) / 'obs2.json'
            obs2.write_text(json.dumps(base_meta(pixel_sha256='3333')))
            post = dict(base_meta(pixel_sha256='3333'), observation=str(obs2))
            with live(tmp, token, active=['0xdead'], pre_calls=[],
                       post=post, opened=same) as stop:
                session_driver.execute(
                    ['act', '--observation', str(obs1), '--actions', '-',
                     '--verbose'], WAIT)
                observed = session_driver.execute(
                    ['observe', '--window', ADDR, '--verbose'], '')
                self.assertEqual(observed.returncode, 0)
                with patch.object(cu, 'desktop_act',
                                  side_effect=AssertionError('must not reach input')):
                    stale = session_driver.execute(
                        ['act', '--observation', str(obs1), '--actions', '-',
                         '--verbose'], WAIT)
        self.assertEqual(stale.returncode, 1)
        self.assertIn('fresh desktop observation required', stale.stdout)
        stop.assert_called_once()


class KillEnvelope(unittest.TestCase):
    def act_args(self, obs):
        return ['act', '--observation', str(obs), '--actions', '-', '--verbose']

    def test_same_text_without_code_kills_session(self):
        from PIL import Image
        token = 'a1' * 16
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR], pre_calls=[],
                       post={}, opened=Image.new('RGB', (20, 20))) as stop:
                with patch.object(cu, 'desktop_act',
                                  side_effect=RuntimeError('screen changed')):
                    code, body = relay_lines([
                        {'args': self.act_args(obs), 'stdin': WAIT},
                        {'args': ['status']},
                    ])
        self.assertEqual(code, 1, 'code-less error with identical text must kill')
        response = body[1]
        self.assertEqual(response['returncode'], 1)
        self.assertFalse(cu.is_transient_refusal(response['result']))
        self.assertEqual(len(body), 2, 'second command never runs')
        stop.assert_called_once()

    def test_nontransient_bodies_kill_driver(self):
        bodies = [
            {'ok': False, 'error': 'screen changed'},  # missing code
            {'ok': False, 'error': 'focus changed',
             'error_code': 'screen_changed'},  # crossed codes
            {'ok': False, 'error': 'screen changed',
             'error_code': 'screen_changed', 'capture_error': 'boom'},
            {'ok': False, 'error': 'focus changed',
             'error_code': 'focus_changed', 'ime_restore_failed': True},
            {'ok': True, 'completed': 1},  # ok-True is never a refusal
        ]
        for result in bodies:
            with self.subTest(result=result):
                first = subprocess.CompletedProcess(
                    ['act'], 1, json.dumps(result), '')
                with patch.object(session_driver, 'execute', return_value=first) as run:
                    code, body = relay_lines([{'args': ['act']},
                                              {'args': ['status']}])
                self.assertFalse(cu.is_transient_refusal(result))
                self.assertEqual(code, 1)
                run.assert_called_once()
                self.assertEqual(len(body), 2, 'ready plus one response only')

    def test_capture_error_kills_session_real(self):
        from PIL import Image
        token = 'b2' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 8, pre_calls=[(same, {})],
                       post=RuntimeError('after capture down'),
                       opened=same) as stop:
                result = session_driver.execute(self.act_args(obs), WAIT)
        body = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn('capture_error', body)
        self.assertIn('final capture failed', body['error'])
        self.assertFalse(body['ok'])
        self.assertFalse(cu.is_transient_refusal(body))
        stop.assert_called_once()

    def test_pointer_cleanup_error_kills_session_real(self):
        from PIL import Image
        token = 'c3' * 16
        same = Image.new('RGB', (20, 20))
        scroll = json.dumps([{'type': 'scroll', 'x': 5, 'y': 5, 'dx': 0, 'dy': 10}])
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 6, pre_calls=[(same, {})],
                       post=base_meta(pixel_sha256='4444'), opened=same,
                       close_error=RuntimeError('close boom')) as stop:
                result = session_driver.execute(self.act_args(obs), scroll)
        body = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn('pointer cleanup failed', body['error'])
        self.assertFalse(cu.is_transient_refusal(body))
        stop.assert_called_once()

    def test_focus_with_cleanup_failure_kills_session_real(self):
        # Transient focus text plus a teardown co-error: the code must go.
        from PIL import Image
        token = 'e8' * 16
        same = Image.new('RGB', (20, 20))
        click = json.dumps([{'type': 'click', 'x': 5, 'y': 5}])
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 5 + ['0xdead'] * 2,
                       pre_calls=[(same, {})],
                       post=base_meta(pixel_sha256='5555'), opened=same,
                       close_error=RuntimeError('close boom')) as stop:
                result = session_driver.execute(self.act_args(obs), click)
        body = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(body['error'], 'focus changed')
        self.assertEqual(body['completed'], 1, 'count survives teardown')
        self.assertNotIn('error_code', body, 'co-error voids transient code')
        self.assertFalse(cu.is_transient_refusal(body))
        stop.assert_called_once()

    def test_cancel_never_whitelisted_real(self):
        token = 'd6' * 16
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(cu, 'STATE', Path(tmp)), \
                    patch.dict(os.environ, {'CU_SESSION_TOKEN': token}), \
                    patch.object(cu, 'check_cancel',
                                 side_effect=RuntimeError('cancelled by user; stop now')), \
                    patch.object(cu, 'stop_session_on_error') as stop:
                code, body = relay_lines([
                    {'args': ['act', '--observation', 'x',
                              '--actions', '-', '--verbose'], 'stdin': WAIT},
                    {'args': ['status']},
                ])
        self.assertEqual(code, 1)
        response = body[1]
        self.assertEqual(response['returncode'], 1)
        self.assertIn('cancelled by user', response['result']['error'])
        self.assertNotIn('error_code', response['result'],
                         'cancel carries no transient code')
        self.assertEqual(len(body), 2, 'second command never runs')
        stop.assert_called_once()


class ExactMatcher(unittest.TestCase):
    def test_exact_matcher_negatives(self):
        good_screen = {'ok': False, 'error': 'screen changed',
                       'error_code': 'screen_changed'}
        good_focus = {'ok': False, 'error': 'focus changed',
                      'error_code': 'focus_changed'}
        self.assertTrue(cu.is_transient_refusal(good_screen))
        self.assertTrue(cu.is_transient_refusal(good_focus))
        # Presence gate: even an empty capture_error voids the whitelist.
        self.assertFalse(cu.is_transient_refusal(
            {'ok': False, 'error': 'screen changed',
             'error_code': 'screen_changed', 'capture_error': ''}))
        for bad in [
            {'ok': False, 'error': 'screen changed!',  # wrong suffix
             'error_code': 'screen_changed'},
            {'ok': False, 'error': 'Screen Changed',  # wrong case
             'error_code': 'screen_changed'},
            {'ok': False, 'error': 'screen changed',
             'error_code': 'focus_changed'},  # wrong code
            {'ok': False, 'error': 'focus changed',
             'error_code': 'screen_changed'},  # wrong code
            {'ok': False, 'error': 'screen changed',
             'error_code': 'screen_changed', 'capture_error': 'x'},
            {'ok': False, 'error': 'screen changed',
             'error_code': 'screen_changed', 'ime_restore_failed': True},
            {'ok': True, 'error': 'screen changed',  # ok must be False
             'error_code': 'screen_changed'},
            {'ok': False, 'error': 'screen changed'},  # missing code
            'screen changed', [], None,
        ]:
            with self.subTest(bad=bad):
                self.assertFalse(cu.is_transient_refusal(bad))
        # returncode 2 with a transient-shaped body still kills the driver.
        first = subprocess.CompletedProcess(['act'], 2, json.dumps(good_screen), '')
        with patch.object(session_driver, 'execute', return_value=first) as run:
            code, body = relay_lines([{'args': ['act']}, {'args': ['status']}])
        self.assertEqual(code, 2)
        run.assert_called_once()
        self.assertEqual(len(body), 2, 'ready plus one response only')


class BackendWiring(unittest.TestCase):
    WAIT_BROWSER = json.dumps([{'type': 'wait', 'ms': 10}])
    CLICK_A11Y = json.dumps([{'type': 'click', 'ref': 'e1'}])

    @contextlib.contextmanager
    def wired(self, tmp, token):
        stack = contextlib.ExitStack()
        with stack:
            stack.enter_context(patch.object(cu, 'STATE', Path(tmp)))
            stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': token}))
            stack.enter_context(patch.object(cu, 'check_cancel'))
            stack.enter_context(patch.object(cu, 'environment', return_value={}))
            browser = stack.enter_context(patch.object(cu, 'browser'))
            runner = stack.enter_context(patch.object(cu, 'run_cancelable'))
            stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
            yield browser, runner, stop

    def test_browser_and_a11y_act_blocked_before_backend(self):
        token = 'b7' * 16
        with tempfile.TemporaryDirectory() as tmp:
            record_refusal(Path(tmp), token)
            with self.wired(tmp, token) as (browser, runner, stop):
                bad_browser = session_driver.execute(
                    ['browser', 'act', '--actions', '-'],
                    self.WAIT_BROWSER)
                self.assertEqual(bad_browser.returncode, 1)
                self.assertIn('fresh desktop observation required',
                              bad_browser.stdout)
                browser.assert_not_called()
                bad_a11y = session_driver.execute(
                    ['a11y', 'act', '--actions', '-'],
                    self.CLICK_A11Y)
                self.assertEqual(bad_a11y.returncode, 1)
                self.assertIn('fresh desktop observation required',
                              bad_a11y.stdout)
                runner.assert_not_called()
            self.assertEqual(stop.call_count, 2, 'both blocks stop the session')

    def test_browser_act_after_fresh_observe_calls_backend_once(self):
        from PIL import Image
        token = 'c8' * 16
        same = Image.new('RGB', (20, 20))
        post = dict(base_meta(pixel_sha256='7777'), observation='fresh-path-1')
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / ('session-reobserve-' + token + '.json')
            record_refusal(Path(tmp), token)
            with self.wired(tmp, token) as (browser, runner, stop):
                stack = contextlib.ExitStack()
                with stack:
                    stack.enter_context(patch.object(cu, 'observe', return_value=dict(post)))
                    observed = session_driver.execute(
                        ['observe', '--window', ADDR, '--verbose'], '')
                self.assertEqual(observed.returncode, 0)
                self.assertEqual(read_marker(marker),
                                 {'observation': 'fresh-path-1'})
                browser.return_value = {'ok': True}
                acted = session_driver.execute(
                    ['browser', 'act', '--actions', '-'],
                    self.WAIT_BROWSER)
                self.assertEqual(acted.returncode, 0)
                self.assertEqual(browser.call_count, 1)
                self.assertFalse(marker.exists(),
                                 'successful input consumes the marker')
            stop.assert_not_called()

    def test_a11y_act_after_fresh_observe_calls_backend_once(self):
        token = 'd9' * 16
        post = dict(base_meta(pixel_sha256='8888'), observation='fresh-path-2')
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / ('session-reobserve-' + token + '.json')
            record_refusal(Path(tmp), token)
            with self.wired(tmp, token) as (browser, runner, stop):
                with patch.object(cu, 'observe', return_value=dict(post)):
                    observed = session_driver.execute(
                        ['observe', '--window', ADDR, '--verbose'], '')
                self.assertEqual(observed.returncode, 0)
                runner.return_value = '{"ok": true}'
                acted = session_driver.execute(
                    ['a11y', 'act', '--actions', '-'],
                    self.CLICK_A11Y)
                self.assertEqual(acted.returncode, 0)
                self.assertEqual(runner.call_count, 1)
                self.assertFalse(marker.exists(),
                                 'successful input consumes the marker')
            stop.assert_not_called()


class CrossProcess(unittest.TestCase):
    PROBE = ('import sys; from pathlib import Path; '
             'sys.path.insert(0, sys.argv[1]); '
             'from session_policy import require_observation; '
             'require_observation(Path(sys.argv[2]), sys.argv[3], '
             'sys.argv[4] if len(sys.argv) > 4 else None)')

    def probe(self, scripts, tmp, token, *extra):
        return subprocess.run(
            [sys.executable, '-c', self.PROBE, scripts, tmp, token, *extra],
            capture_output=True, text=True, timeout=60)

    def test_marker_semantics_across_interpreters(self):
        token = 'f9' * 16
        scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        with tempfile.TemporaryDirectory() as tmp:
            record_refusal(Path(tmp), token)
            refused = self.probe(scripts, tmp, token)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn('fresh desktop observation required', refused.stderr)
            record_observation(Path(tmp), token, {'observation': 'fresh-path'})
            self.assertEqual(self.probe(scripts, tmp, token, 'fresh-path').returncode, 0)
            stale = self.probe(scripts, tmp, token, 'stale-path')
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn('fresh desktop observation required', stale.stderr)


class MarkerHelpers(unittest.TestCase):
    def test_marker_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            self.assertIsNone(marker_path(state, ''))
            self.assertIsNone(marker_path(state, None))
            for bad_token in ('xyz', 'A' * 32, 'c' * 31, 'c' * 33, '../x'):
                with self.subTest(token=bad_token), \
                        self.assertRaises(RuntimeError):
                    marker_path(state, bad_token)
            token = 'd4' * 16
            path = marker_path(state, token)
            self.assertIsNone(read_marker(path))  # absent marker is fine
            path.write_bytes(b'not json')
            with self.assertRaises(RuntimeError):
                read_marker(path)
            with self.assertRaises(RuntimeError):
                record_refusal(state, token)  # corrupt stays fail-closed
            path.write_bytes(b'x' * 5000)
            with self.assertRaises(RuntimeError):
                read_marker(path)
            for shape in (b'{"a":1}', b'{"observation":5}',
                          b'{"observation":""}', b'[1,2]'):
                path.write_bytes(shape)
                with self.subTest(shape=shape), \
                        self.assertRaises(RuntimeError):
                    read_marker(path)
            path.unlink()
            target = Path(tmp) / 'target.json'
            target.write_text('{}')
            path.symlink_to(target)
            with self.assertRaises(OSError):
                read_marker(path)  # O_NOFOLLOW: symlink never followed

    def test_observation_gate_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            token = 'e5' * 16
            self.assertIsNone(require_observation(state, token))  # no gate yet
            record_refusal(state, token)
            with self.assertRaises(RuntimeError):
                require_observation(state, token, 'whatever')
            with self.assertRaises(RuntimeError):  # ok False never records
                record_observation(state, token,
                                   {'observation': 'fresh-path', 'ok': False})
            with self.assertRaises(RuntimeError):  # empty observation
                record_observation(state, token, {'observation': ''})
            record_observation(state, token, {'observation': 'fresh-path'})
            self.assertIsNone(require_observation(state, token))  # any fresh
            self.assertIsNone(require_observation(state, token, 'fresh-path'))
            with self.assertRaises(RuntimeError):
                require_observation(state, token, 'stale-path')
            complete_requirement(state, token)
            self.assertFalse((state / ('session-reobserve-' + token + '.json')).exists())


if __name__ == '__main__':
    unittest.main()

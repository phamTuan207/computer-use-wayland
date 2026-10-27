"""E1: the driver owns the continuation decision; nothing else may grant it.

Production truth exercised end to end with the REAL cu.main, the REAL
session_driver.execute/relay dispatch and the REAL session_policy marker
state: only compositor/capture/input (OS/GUI) seams are mocked. Envelope
contract under test:

- every command response carries top-level `session_continues` (boolean);
- recoverability comes ONLY from the typed cu.PreflightRefusal exception
  (internal provenance on the CompletedProcess) or the exact transient
  matcher (returncode 1, command `act`, desktop refusal envelope, co-error
  exclusions) — never from any `recoverable` flag inside a backend payload;
- fatal failures additionally carry `session_ended` with a bounded `reason`
  and the failing command's `exit_code`;
- missing/invalid metadata on a failed command is fail-closed.

STATE is always a temp dir, never the real cache.
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

ADDR = '0xabc'
BAD_WAIT = json.dumps([{'type': 'wait', 'ms': 2001}])
CORRECTED_TYPE = json.dumps([{'type': 'type', 'text': 'corrected'}])
WAIT = json.dumps([{'type': 'wait', 'ms': 10}])
TYPE_AFTER_REFRESH = json.dumps([{'type': 'type', 'text': 'after refresh'}])
CLICK_A11Y = json.dumps([{'type': 'click', 'ref': 'e1'}])
WAIT_BROWSER = json.dumps([{'type': 'wait', 'ms': 10}])


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
    """Patch cu below desktop_act; active/pre_calls are consumed in order.

    Mirrors tests/test_session_policy.live: real execute()/main()/desktop_act
    run; compositor, capture and input are the only injected seams.
    """
    from PIL import Image  # noqa: F401 (ensures Pillow present like prod)
    stack = contextlib.ExitStack()
    with stack:
        stack.enter_context(patch.object(cu, 'STATE', Path(tmp)))
        stack.enter_context(patch.dict(os.environ, {'CU_SESSION_TOKEN': token}))
        stack.enter_context(patch.object(cu, 'check_cancel'))
        stack.enter_context(patch.object(cu, 'environment', return_value={}))
        stack.enter_context(patch.object(cu, 'focus'))
        stack.enter_context(patch.object(cu, 'window',
                                         return_value={'at': [0, 0], 'size': [20, 20]}))

        # E4: desktop_act opens every batch with one pre-focus `activewindow`
        # query (the input_diagnostics focus_before). That first query per
        # batch sees the head of `active` WITHOUT consuming it, so every
        # pre-existing queue still lines up with the guard queries that pop
        # after it; focus() is mocked, so the simulated pre-focus state equals
        # the state the first guard would see.
        act_open = {'pre_focus': False}
        real_desktop_act = cu.desktop_act

        def act_boundary(env, meta, actions, after_capture=True):
            act_open['pre_focus'] = True
            return real_desktop_act(env, meta, actions, after_capture=after_capture)

        stack.enter_context(patch.object(cu, 'desktop_act', side_effect=act_boundary))

        def hypr(env, query):
            if query == 'monitors':
                return [{'name': 'test', 'x': 0, 'y': 0, 'width': 20,
                         'height': 20, 'scale': 1}]
            if query == 'activewindow':
                if act_open['pre_focus']:
                    act_open['pre_focus'] = False
                    return {'address': active[0]}
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
        typed = stack.enter_context(patch.object(cu, 'run_cancelable',
                                                 return_value=''))
        stack.enter_context(patch.object(cu.shutil, 'which', return_value=None))
        stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))
        if isinstance(opened, list):
            stack.enter_context(patch('PIL.Image.open',
                                      side_effect=lambda *a: opened.pop(0)))
        elif opened is not None:
            stack.enter_context(patch('PIL.Image.open', return_value=opened))
        stack.enter_context(patch('time.sleep'))
        stop = stack.enter_context(patch.object(cu, 'stop_session_on_error'))
        yield typed, stop


def act_args(obs):
    return ['act', '--observation', str(obs), '--actions', '-', '--verbose']


def relay_lines(lines):
    out = io.StringIO()
    code = session_driver.relay(io.StringIO('\n'.join(map(json.dumps, lines))), out)
    body = [json.loads(line) for line in out.getvalue().splitlines()]
    return code, body


class TypedRefusalRecovery(unittest.TestCase):
    def test_invalid_wait_typed_refusal_continues_then_corrected_type_succeeds(self):
        from PIL import Image
        token = 'b2' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 12,
                      pre_calls=[(same, {})],
                      post=dict(base_meta(pixel_sha256='1111')),
                      opened=same) as (typed, stop):
                code, body = relay_lines([
                    {'args': act_args(obs), 'stdin': BAD_WAIT},
                    {'args': act_args(obs), 'stdin': CORRECTED_TYPE},
                    {'args': ['status']},
                    {'args': ['finish']},
                ])
        self.assertEqual(code, 0, 'typed refusal must not stop the relay')
        self.assertEqual(len(body), 5, 'ready plus four command responses')
        refusal, corrected, status = body[1], body[2], body[3]
        # The typed preflight refusal envelope is unchanged for compatibility.
        self.assertEqual(refusal['returncode'], 1)
        self.assertTrue(refusal['result']['recoverable'])
        self.assertIn('wait ms must be 0..2000', refusal['result']['error'])
        self.assertIn('No input was sent', refusal['result']['next_step'])
        # E1: the DRIVER granted continuation at top level.
        self.assertIs(refusal['session_continues'], True)
        self.assertNotIn('session_ended', refusal)
        # The corrected action really ran once and the session stayed alive.
        self.assertEqual(corrected['returncode'], 0)
        self.assertTrue(corrected['result']['ok'])
        self.assertEqual(corrected['result']['completed'], 1)
        self.assertIs(corrected['session_continues'], True,
                      'successes carry the same envelope shape')
        self.assertEqual(typed.call_count, 1, 'exactly one real input event')
        self.assertTrue(status['result']['ok'])
        stop.assert_not_called()

    def test_expired_observation_typed_refusal_then_observe_then_act_succeeds(self):
        from PIL import Image
        token = 'c3' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / 'stale.json'
            stale.write_text(json.dumps(base_meta(created=time.time() - 91)))
            fresh = Path(tmp) / 'fresh.json'
            after = base_meta(pixel_sha256='2222')
            fresh.write_text(json.dumps(after))
            post = dict(after, observation=str(fresh))
            with live(tmp, token, active=[ADDR] * 12,
                      pre_calls=[(same, {})], post=post,
                      opened=same) as (typed, stop):
                code, body = relay_lines([
                    {'args': act_args(stale), 'stdin': WAIT},
                    {'args': ['observe', '--window', ADDR, '--verbose']},
                    {'args': act_args(fresh), 'stdin': TYPE_AFTER_REFRESH},
                    {'args': ['status']},
                ])
        self.assertEqual(code, 0)
        refusal, observed, acted = body[1], body[2], body[3]
        self.assertEqual(refusal['returncode'], 1)
        self.assertIn('observation older than 90s', refusal['result']['error'])
        self.assertIn('observe again', refusal['result']['error'])
        self.assertIs(refusal['session_continues'], True,
                      'TTL expiry is a typed preflight refusal, not an end')
        self.assertNotIn('session_ended', refusal)
        self.assertEqual(observed['returncode'], 0)
        self.assertEqual(acted['returncode'], 0)
        self.assertTrue(acted['result']['ok'])
        self.assertEqual(typed.call_count, 1)
        stop.assert_not_called()


class TransientRefusalGate(unittest.TestCase):
    def test_focus_refusal_continues_then_a11y_bypass_is_fatal_until_observe(self):
        from PIL import Image
        token = 'd4' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(base_meta()))
            obs2 = Path(tmp) / 'obs2.json'
            after = base_meta(pixel_sha256='3333')
            obs2.write_text(json.dumps(after))
            post = dict(after, observation=str(obs2))
            with live(tmp, token, active=['0xdead'] + [ADDR] * 12,
                      pre_calls=[(same, {})], post=post,
                      opened=same) as (typed, stop):
                with patch('browser_worker.BrowserWorker.request') as worker_request:
                    code, body = relay_lines([
                        {'args': act_args(obs1), 'stdin': WAIT},
                        {'args': ['a11y', 'act', '--actions', '-'],
                         'stdin': CLICK_A11Y},
                    ])
                refusal, bypass = body[1], body[2]
                # The exact transient refusal keeps the session via the driver
                # decision, with the mandatory-reobserve hint on stderr.
                self.assertEqual(refusal['returncode'], 1)
                self.assertTrue(cu.is_transient_refusal(refusal['result']))
                self.assertIs(refusal['session_continues'], True)
                self.assertIn('session refusal: error=focus changed'
                              ' action=require_reobserve', refusal['stderr'])
                # a11y act without a fresh observe is fatal BEFORE any backend
                # or input: fail-closed, session ends.
                self.assertEqual(code, 1)
                self.assertEqual(bypass['returncode'], 1)
                self.assertIs(bypass['session_continues'], False)
                self.assertEqual(bypass['session_ended']['exit_code'], 1)
                self.assertIn('fresh desktop observation required',
                              bypass['session_ended']['reason'])
                self.assertEqual(typed.call_count, 0,
                                 'no input event may happen while gated')
                worker_request.assert_not_called()
                stop.assert_called_once()
                # Recovery: fresh observe clears the gate; the act succeeds.
                code2, body2 = relay_lines([
                    {'args': ['observe', '--window', ADDR, '--verbose']},
                    {'args': act_args(obs2), 'stdin': WAIT},
                    {'args': ['status']},
                ])
        self.assertEqual(code2, 0)
        self.assertEqual(body2[2]['returncode'], 0)
        self.assertTrue(body2[2]['result']['ok'])
        self.assertEqual(typed.call_count, 0, 'wait actions inject no device input')
        self.assertEqual(stop.call_count, 1, 'the earlier fatal stays recorded')

    def test_browser_bypass_after_transient_refusal_is_fatal_before_backend(self):
        from PIL import Image
        token = 'e5' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(base_meta()))
            obs2 = Path(tmp) / 'obs2.json'
            obs2.write_text(json.dumps(base_meta(pixel_sha256='4444')))
            post = dict(base_meta(pixel_sha256='4444'), observation=str(obs2))
            with live(tmp, token, active=['0xdead'] + [ADDR] * 12,
                      pre_calls=[(same, {})], post=post,
                      opened=same) as (typed, stop):
                code, body = relay_lines([
                    {'args': act_args(obs1), 'stdin': WAIT},
                    {'args': ['browser', 'act', '--actions', '-'],
                     'stdin': WAIT_BROWSER},
                ])
        self.assertEqual(code, 1)
        refusal, bypass = body[1], body[2]
        self.assertIs(refusal['session_continues'], True)
        self.assertEqual(bypass['returncode'], 1)
        self.assertIs(bypass['session_continues'], False)
        self.assertIn('fresh desktop observation required',
                      bypass['session_ended']['reason'])
        stop.assert_called_once()

    def test_screen_refusal_saves_after_then_observe_restores_input(self):
        from PIL import Image
        token = 'f6' * 16
        old, big, same = (Image.new('RGB', (20, 20)), Image.new('RGB', (30, 30)),
                          Image.new('RGB', (20, 20)))
        screen_meta = base_meta(scope='screen')
        del screen_meta['window']
        with tempfile.TemporaryDirectory() as tmp:
            obs1 = Path(tmp) / 'obs1.json'
            obs1.write_text(json.dumps(screen_meta))
            obs2 = Path(tmp) / 'obs2.json'
            after = base_meta(scope='screen', pixel_sha256='5555')
            del after['window']
            obs2.write_text(json.dumps(after))
            post = dict(after, observation=str(obs2))
            opened = [old, same]
            with live(tmp, token, active=[ADDR] * 12,
                      pre_calls=[(big, {}), (same, {})], post=post,
                      opened=None) as (typed, stop):
                with patch('PIL.Image.open',
                           side_effect=lambda *a: opened.pop(0) if opened else same):
                    code, body = relay_lines([
                        {'args': act_args(obs1), 'stdin': WAIT},
                        {'args': ['observe', '--screen', 'test', '--verbose']},
                        {'args': act_args(obs2), 'stdin': WAIT},
                        {'args': ['status']},
                    ])
        self.assertEqual(code, 0, 'screen refusal must not stop the relay')
        refusal, observed, fresh = body[1], body[2], body[3]
        self.assertTrue(cu.is_transient_refusal(refusal['result']))
        self.assertEqual(refusal['result']['error_code'], 'screen_changed')
        self.assertIn('after', refusal['result'],
                      'the refused attempt still saves what it saw')
        self.assertIs(refusal['session_continues'], True)
        self.assertIn('session refusal: error=screen changed'
                      ' action=require_reobserve', refusal['stderr'])
        self.assertEqual(observed['returncode'], 0)
        self.assertEqual(fresh['returncode'], 0)
        self.assertTrue(fresh['result']['ok'])
        self.assertIs(fresh['session_continues'], True)
        stop.assert_not_called()


class FatalEnvelope(unittest.TestCase):
    def test_capture_failure_remains_fatal_with_envelope(self):
        from PIL import Image
        token = 'a7' * 16
        same = Image.new('RGB', (20, 20))
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 12, pre_calls=[(same, {})],
                      post=RuntimeError('after capture down'),
                      opened=same) as (typed, stop):
                code, body = relay_lines([
                    {'args': act_args(obs), 'stdin': WAIT},
                    {'args': ['status']},
                ])
        self.assertEqual(code, 1, 'capture failure is never recoverable')
        self.assertEqual(len(body), 2, 'ready plus exactly one response')
        response = body[1]
        self.assertIn('capture_error', response['result'])
        self.assertFalse(cu.is_transient_refusal(response['result']))
        self.assertIs(response['session_continues'], False)
        self.assertIn('final capture failed', response['session_ended']['reason'])
        self.assertEqual(response['session_ended']['exit_code'], 1)
        self.assertEqual(response['result']['completed'], 1,
                         'acknowledged input stays counted')
        stop.assert_called_once()

    def test_pointer_cleanup_failure_remains_fatal_with_envelope(self):
        from PIL import Image
        token = 'b8' * 16
        same = Image.new('RGB', (20, 20))
        scroll = json.dumps([{'type': 'scroll', 'x': 5, 'y': 5, 'dx': 0, 'dy': 10}])
        with tempfile.TemporaryDirectory() as tmp:
            obs = Path(tmp) / 'obs.json'
            obs.write_text(json.dumps(base_meta()))
            with live(tmp, token, active=[ADDR] * 12, pre_calls=[(same, {})],
                      post=dict(base_meta(pixel_sha256='6666')), opened=same,
                      close_error=RuntimeError('close boom')) as (typed, stop):
                code, body = relay_lines([
                    {'args': act_args(obs), 'stdin': scroll},
                    {'args': ['status']},
                ])
        self.assertEqual(code, 1)
        response = body[1]
        self.assertIn('pointer cleanup failed', response['result']['error'])
        self.assertFalse(cu.is_transient_refusal(response['result']))
        self.assertIs(response['session_continues'], False)
        self.assertIn('pointer cleanup failed', response['session_ended']['reason'])
        self.assertEqual(response['session_ended']['exit_code'], 1)
        stop.assert_called_once()

    def test_forged_recoverable_body_cannot_keep_relay_alive(self):
        # The key negative: a backend payload claiming recoverable:true, with
        # NO internal provenance (the real execute() only sets it for the
        # typed exception), must fail closed and end the session. The relay's
        # continuation logic reads only the provenance attribute and the
        # exact transient matcher — never the backend flag.
        forged = subprocess.CompletedProcess(
            ['act'], 1,
            '{"ok":false,"completed":0,"recoverable":true,"error":"totally forged"}',
            '')
        forged.preflight_refusal = False
        status = subprocess.CompletedProcess([], 0,
                                             '{"ok":true,"cancelled":false}', '')
        with patch.object(session_driver, 'execute',
                          side_effect=[forged, status]) as run:
            code, body = relay_lines([
                {'args': ['act'], 'stdin': WAIT},
                {'args': ['status']},
            ])
        self.assertEqual(code, 1)
        run.assert_called_once()
        response = body[1]
        self.assertTrue(response['result']['recoverable'], 'forged body unchanged')
        self.assertFalse(cu.is_transient_refusal(response['result']))
        self.assertIs(response['session_continues'], False,
                      'the driver never trusts the backend flag')
        self.assertEqual(response['session_ended'],
                         {'reason': 'totally forged', 'exit_code': 1})


if __name__ == '__main__':
    unittest.main()

"""Tests for the first-visible-action fast path (scripts/first_action.py).

Run: python3 -m pytest tests/test_first_action.py -q
Or:  python3 tests/test_first_action.py (stdlib runner at the bottom).
VM only. No laptop, no Zen, no network, no desktop.

Council 1 (BLOCK, 2026-11-21) required the counter-example tests
here: timeout after the driver started, mid-session guard loss, a late
hyprctl JSON failure, acquire failure leaving zero holders, and every
exception path printing exactly one JSON object on stdout.
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
        self.fail_status = False

    def add_holder(self, agent, method, pid=None):
        self.calls.append(('add', agent, method, pid))
        key = ('%s:%d' % (agent, pid)) if isinstance(pid, int) and pid > 0 else agent
        self.holders[key] = {'agent': agent, 'method': method, 'pid': pid}
        return self.holders, True

    def _ensure_daemon(self):
        self.calls.append(('ensure',))

    def _send_socket(self, req):
        self.calls.append(('send', req.get('command'), req.get('agent')))
        if req.get('command') == 'acquire':
            return {'visible': self.visible, 'owner': 'daemon',
                    'holders': self.holders, 'label': 'Muse via act-now'}
        if req.get('command') == 'release':
            self.remove_holder(req.get('agent'), req.get('pid'))
            return {'visible': bool(self.holders), 'owner': 'none',
                    'holders': self.holders}
        if req.get('command') in ('status', 'sync'):
            if self.fail_status:
                raise OSError('daemon gone')
            return {'visible': bool(self.holders), 'owner': 'daemon',
                    'holders': self.holders}
        return {'visible': bool(self.holders)}

    def _label_for(self, agent, method):
        return (agent + ' via ' + method)[:40]

    def remove_holder(self, agent, pid=None):
        self.calls.append(('remove', agent, pid))
        if isinstance(pid, int) and pid > 0:
            self.holders.pop('%s:%d' % (agent, pid), None)
            self.holders.pop(agent, None)
        else:
            for key in list(self.holders):
                if key == agent or (agent and key.startswith(agent + ':')):
                    self.holders.pop(key, None)
        return self.holders, True

    def session_live(self):
        return False


class FakeCu:
    """Stand-in for the cu module: no desktop, no Hyprland."""

    # Mirrors scripts/cu.py CAPTURE_MAX_WIDTH (S0): first_action
    # reads cu.CAPTURE_MAX_WIDTH for its captures, so the fake must
    # carry the same constant or every run dies with AttributeError.
    CAPTURE_MAX_WIDTH = 960

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.state = self.tmp / 'state'
        self.state.mkdir(parents=True, exist_ok=True)
        self.STATE = self.state
        self.desktop_calls = []
        self.desktop_kwargs = []
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
                'scope': 'screen',
                'created': time.time()}
        return meta

    def observe(self, env, address, crop=None, max_width=960,
                activate=False, persist=True, low_res=False):
        # Window-scope capture (AMEND4 item 12): the fresh
        # scope-matching after for a window observation.
        self.observe_calls.append(('window', address))
        return {'id': 'win-after-1',
                'observation': str(self.state / 'win-after-1.json'),
                'image': str(self.state / 'win-after-1.jpg'),
                'monitor_box': [0, 0, 1920, 1200],
                'scope': 'window',
                'window': address,
                'window_bounds': [2533, 914, 901, 1176],
                'image_size': [901, 1176],
                'region': [2533, 914, 901, 1176],
                'created': time.time()}

    def desktop_act(self, env, meta, actions, observation_path=None,
                    **kwargs):
        self.desktop_calls.append((meta.get('id'), len(actions)))
        self.desktop_kwargs.append(kwargs)
        # Production-faithful: desktop_act's after-capture matches
        # the input observation's scope (AMEND4 item 12).
        return {'ok': True, 'completed': len(actions),
                'after': {'id': 'after-1',
                          'observation': str(self.state / 'after.json'),
                          'scope': meta.get('scope', 'screen')}}

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
            'label': None, 'session_deadline_s': 20.0, 'dom_selector': None}
    base.update(overrides)
    return mock.Mock(**base)


class FakeZenSession:
    """Stand-in for zen_dom.ZenSession: one scripted field, no Zen."""

    def __init__(self, fields):
        self.fields = fields
        self._armed = {}
        self._typed = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def field_value(self, selector):
        field = self.fields.get(selector)
        return None if field is None else field.get('value')

    def arm_typed_flag(self, selector):
        field = self.fields.get(selector)
        self._armed[selector] = None if field is None \
            else field.get('value')
        self._typed[selector] = False
        return field is not None

    def focus_check(self, selector):
        field = self.fields.get(selector)
        return bool(field) and bool(field.get('focused', False))

    def typed_flag(self, selector):
        if self._typed.get(selector):
            return True
        field = self.fields.get(selector)
        if field is None:
            return False
        armed = self._armed.get(selector)
        return field.get('value') != armed

    def locate(self, selector):
        # Grounding reads the field rect (G30 shape); a field with
        # no rect is not groundable, exactly like a missing element.
        field = self.fields.get(selector)
        if field is None:
            return None
        return field.get('rect')

    def viewport_origin(self, *args):
        # The window origin of the G30-shaped observation below.
        return [2533, 914]

    def hit_check(self, selector):
        return selector in self.fields

    def verify_typed(self, selector, expected, before=None):
        field = self.fields.get(selector)
        if not field:
            return False
        if field.get('value') != expected:
            return False
        if (before is not None and before == expected
                and not self.typed_flag(selector)):
            return False
        return True


class TestSessionStartFailure(unittest.TestCase):
    def test_guardian_json_error(self):
        self.assertTrue(first_action.is_session_start_failure(
            '{"ok": false, "error": "session guardian startup failed"}',
            False))

    def test_guardian_json_error_with_detail(self):
        # The rehearsal error (F1's improved message, 22:53 21/11).
        self.assertTrue(first_action.is_session_start_failure(
            '{"ok": false, "error": "session guardian startup failed: '
            'cursor guard reply is not valid JSON (got: unknown '
            'request)"}',
            False))

    def test_driver_registration_failed(self):
        self.assertTrue(first_action.is_session_start_failure(
            '{"ok": false, "error": "driver registration failed: guard '
            'closed"}',
            False))

    def test_timeout_never_falls_back(self):
        # Council 1, B1: a timeout may have acted and been torn down.
        self.assertFalse(first_action.is_session_start_failure('', True))
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "session guardian startup failed"}',
            True))

    def test_timeout_after_driver_started_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "screen changed", "completed": 1}',
            True))

    def test_mid_session_guard_lost_never_replays(self):
        # Council 1, B2: 'session cursor guard lost' is raised mid
        # session (cursor_session.py:178) after the driver may have
        # acted, and 'session guardian died mid-session' is its
        # supervise print (cursor_session.py:294).
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "session guardian died mid-session: '
            'session cursor guard lost"}',
            False))

    def test_mid_session_guard_lost_stderr_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            'session guardian died mid-session: session cursor guard '
            'lost',
            False))

    def test_late_expecting_value_never_replays(self):
        # Council 1, B2: a late hyprctl JSON failure (cu.py:519, :213)
        # after earlier actions ran carries the same string.
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "Expecting value: line 1 column 1 '
            '(char 0)", "completed": 1}',
            False))
        self.assertFalse(first_action.is_session_start_failure(
            'json.decoder.JSONDecodeError: Expecting value: line 1 '
            'column 1 (char 0)',
            False))

    def test_bare_cursor_guard_substring_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            'cursor guard did not confirm ownership', False))

    def test_act_failure_never_replays(self):
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "screen changed"}', False))
        self.assertFalse(first_action.is_session_start_failure(
            '{"ok": false, "error": "focus changed"}', False))


class TestDeletedSpawn(unittest.TestCase):
    def test_session_cmd_raises(self):
        # Step 8: the per-batch session spawn is deleted. Any caller
        # still building a session command fails loudly instead of
        # silently resurrecting the spawn.
        with self.assertRaises(RuntimeError):
            first_action.session_cmd('/x/cu.py', '/o.json', '/a.json')

    def test_attempt_session_raises(self):
        with self.assertRaises(RuntimeError):
            first_action.attempt_session(['true'], 5)


class TestBrokerOwner(unittest.TestCase):
    def test_valid_agent_kept(self):
        self.assertEqual(first_action._broker_owner('Muse'), 'Muse')

    def test_invalid_agent_falls_back(self):
        self.assertEqual(first_action._broker_owner('bad name!'), 'act-now')
        self.assertEqual(first_action._broker_owner(''), 'act-now')


class TestRegionsEqual(unittest.TestCase):
    def test_same_region(self):
        meta = {'region': [0, 0, 1920, 1200],
                'monitor_box': [0, 0, 1920, 1200]}
        self.assertTrue(first_action._regions_equal(meta, dict(meta)))

    def test_moved_window_differs(self):
        first = {'region': [2533, 914, 901, 1176],
                 'window_bounds': [2533, 914, 901, 1176]}
        second = {'region': [2600, 914, 901, 1176],
                  'window_bounds': [2600, 914, 901, 1176]}
        self.assertFalse(first_action._regions_equal(first, second))


class TestObserveArgs(unittest.TestCase):
    def test_window_scope(self):
        args = first_action._observe_args(
            {'scope': 'window', 'window': '0xabc', 'max_width': 960},
            'eDP-2')
        self.assertEqual(args, ['observe', '--window', '0xabc',
                                '--max-width', '960'])

    def test_screen_scope(self):
        args = first_action._observe_args({'scope': 'screen'}, 'eDP-2')
        self.assertEqual(args, ['observe', '--screen', 'eDP-2'])


class TestStampActions(unittest.TestCase):
    """stamp_actions: the CB-2 stamping path for the JSON batch
    interface (step-9 prototype item 4). The agent loop stamps
    scope/observation_id from the observation meta into every
    action before the batch reaches the broker."""

    META = {'id': 'obs1', 'scope': 'window'}

    def test_stamps_every_action(self):
        stamped = first_action.stamp_actions(
            [{'type': 'click', 'x': 1, 'y': 2},
             {'type': 'key', 'keys': ['Enter']}], self.META)
        self.assertEqual(stamped, [
            {'type': 'click', 'x': 1, 'y': 2, 'scope': 'window',
             'observation_id': 'obs1'},
            {'type': 'key', 'keys': ['Enter'], 'scope': 'window',
             'observation_id': 'obs1'}])

    def test_does_not_mutate_the_input(self):
        actions = [{'type': 'click', 'x': 1, 'y': 2}]
        first_action.stamp_actions(actions, self.META)
        self.assertEqual(actions, [{'type': 'click', 'x': 1, 'y': 2}])

    def test_matching_pre_stamp_is_kept(self):
        stamped = first_action.stamp_actions(
            [{'type': 'click', 'x': 1, 'y': 2, 'scope': 'window',
              'observation_id': 'obs1'}], self.META)
        self.assertEqual(stamped[0]['observation_id'], 'obs1')

    def test_mismatched_pre_stamp_refuses(self):
        # An action already bound to a different observation is a
        # stale binding: refuse instead of silently re-stamping it
        # onto this observation.
        with self.assertRaises(ValueError):
            first_action.stamp_actions(
                [{'type': 'click', 'x': 1, 'y': 2, 'scope': 'window',
                  'observation_id': 'obs9'}], self.META)

    def test_scope_less_meta_refuses(self):
        with self.assertRaises(ValueError):
            first_action.stamp_actions(
                [{'type': 'click', 'x': 1, 'y': 2}], {'id': 'obs1'})

    def test_id_less_meta_refuses(self):
        with self.assertRaises(ValueError):
            first_action.stamp_actions(
                [{'type': 'click', 'x': 1, 'y': 2}], {'scope': 'window'})

    def test_non_dict_action_refuses(self):
        with self.assertRaises(ValueError):
            first_action.stamp_actions(['click'], self.META)


class TestBrokerAttempt(unittest.TestCase):
    """broker_attempt with the session_remote CLI faked."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / 'state'
        self.state.mkdir()
        self.meta = {'id': 'obs1',
                     'observation': str(self.state / 'obs1.json'),
                     'image': str(self.state / 'obs1.jpg'),
                     'monitor_box': [0, 0, 1920, 1200], 'scope': 'screen',
                     'region': [0, 0, 1920, 1200],
                     'image_size': [960, 600], 'created': time.time()}
        self.actions = str(Path(self.tmp.name) / 'actions.json')
        Path(self.actions).write_text(
            '[{"type": "click", "x": 100, "y": 100}]')

    def tearDown(self):
        self.tmp.cleanup()

    def _fake_cli(self, script):
        """script: (command, parsed_dict_or_None, rc) per call, in order."""
        def fake(remote_py, args, timeout_s):
            if not script:
                raise AssertionError(
                    'unexpected broker CLI call: %r' % (args,))
            command, parsed, rc = script.pop(0)
            self.assertEqual(args[0], command)
            return rc, parsed, ''
        return fake

    def _run_attempt(self, script):
        with mock.patch.object(first_action, '_broker_cli',
                               side_effect=self._fake_cli(script)):
            return first_action.broker_attempt(
                str(self.state / 'obs1.json'), self.actions, 20.0,
                self.state, self.meta, 'eDP-2', 'Muse')

    def test_success(self):
        act = {'ok': True, 'completed': 1}
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                       'state': 'running', 'driver': 'ready'}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 1}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 1,
                       'response': {'returncode': 0, 'result': act,
                                    'session_continues': True}}, 0),
            ('finish', {'ok': True, 'status': 'finished'}, 0),
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out), act)
        self.assertFalse(timed_out)
        self.assertEqual(detail['broker_sequences'], [1])
        self.assertEqual(detail['broker_retries'], 0)

    def test_busy_start_falls_back(self):
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': False, 'error': 'busy', 'waited_s': 300.0}, 1),
        ])
        self.assertEqual(rc, 1)
        self.assertTrue(first_action.is_session_start_failure(out, False))

    def test_cancelled_start_never_falls_back(self):
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': False, 'error': 'cancelled'}, 1),
        ])
        self.assertEqual(rc, 1)
        self.assertFalse(first_action.is_session_start_failure(out, False))
        self.assertIn('cancelled', out)

    def test_recovery_required_never_falls_back(self):
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': False, 'error': 'recovery_required'}, 1),
        ])
        self.assertEqual(rc, 1)
        self.assertFalse(first_action.is_session_start_failure(out, False))

    def test_transient_retries_once_on_same_region(self):
        transient = {'ok': False, 'error': 'focus changed'}
        fresh = dict(self.meta)
        fresh['observation'] = str(self.state / 'obs2.json')
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                       'state': 'running', 'driver': 'ready'}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 1}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 1,
                       'response': {'returncode': 1, 'result': transient,
                                    'session_continues': True}}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 2}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 2,
                       'response': {'returncode': 0, 'result': fresh,
                                    'session_continues': True}}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 3}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 3,
                       'response': {'returncode': 0,
                                    'result': {'ok': True, 'completed': 1},
                                    'session_continues': True}}, 0),
            ('finish', {'ok': True, 'status': 'finished'}, 0),
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(detail['broker_retries'], 1)
        self.assertEqual(detail['broker_sequences'], [1, 2, 3])

    def test_transient_no_retry_when_region_moved(self):
        transient = {'ok': False, 'error': 'focus changed'}
        moved = dict(self.meta)
        moved['observation'] = str(self.state / 'obs2.json')
        moved['region'] = [10, 0, 1920, 1200]
        moved['monitor_box'] = [10, 0, 1920, 1200]
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                       'state': 'running', 'driver': 'ready'}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 1}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 1,
                       'response': {'returncode': 1, 'result': transient,
                                    'session_continues': True}}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 2}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 2,
                       'response': {'returncode': 0, 'result': moved,
                                    'session_continues': True}}, 0),
            ('finish', {'ok': True, 'status': 'finished'}, 0),
        ])
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out), transient)
        self.assertEqual(detail['broker_retries'], 0)
        self.assertEqual(detail['broker_sequences'], [1, 2])

    def _run_attempt_capturing(self, script, seen):
        """Like _run_attempt, but records every actions file the act
        envelope points at (the driver reads that file, so what is
        recorded is what actually ran)."""
        base = self._fake_cli(script)

        def capturing(remote_py, args, timeout_s):
            if args and args[0] == 'request':
                try:
                    request_path = args[args.index('--request') + 1]
                    envelope = json.loads(
                        Path(request_path).read_text())
                    act_args = envelope.get('args') or []
                    if act_args and act_args[0] == 'act':
                        actions_path = act_args[
                            act_args.index('--actions') + 1]
                        seen.append(json.loads(
                            Path(actions_path).read_text()))
                except (ValueError, OSError, IndexError):
                    pass
            return base(remote_py, args, timeout_s)

        with mock.patch.object(first_action, '_broker_cli',
                               side_effect=capturing):
            return first_action.broker_attempt(
                str(self.state / 'obs1.json'), self.actions, 20.0,
                self.state, self.meta, 'eDP-2', 'Muse')

    def test_act_request_carries_cb2_stamps(self):
        # CB-2 proof: the act envelope the driver reads must carry
        # scope + observation_id stamped from the observation meta.
        # Without the stamping path this test fails: the actions
        # file it records has no scope and no observation_id.
        seen = []
        act = {'ok': True, 'completed': 1}
        rc, out, err, timed_out, elapsed, detail = \
            self._run_attempt_capturing([
                ('start', {'ok': True, 'status': 'starting',
                           'generation': 'g1'}, 0),
                ('status', {'ok': True, 'generation': 'g1',
                           'state': 'running', 'driver': 'ready'}, 0),
                ('request', {'ok': True, 'status': 'accepted',
                             'sequence': 1}, 0),
                ('result', {'ok': True, 'status': 'completed',
                           'sequence': 1,
                           'response': {'returncode': 0, 'result': act,
                                        'session_continues': True}}, 0),
                ('finish', {'ok': True, 'status': 'finished'}, 0),
            ], seen)
        self.assertEqual(rc, 0)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0], [{'type': 'click', 'x': 100, 'y': 100,
                                    'scope': 'screen',
                                    'observation_id': 'obs1'}])
        # The caller's actions file is NOT rewritten in place: the
        # stamp goes to a sibling file the driver reads.
        self.assertEqual(Path(self.actions).read_text(),
                         '[{"type": "click", "x": 100, "y": 100}]')

    def test_scope_less_meta_never_starts_a_session(self):
        # Full mandatory CB-2: a meta without scope cannot be
        # stamped, so the loop refuses before any broker start and
        # no action runs. The fake raises on any CLI call, proving
        # no session was started.
        self.meta = dict(self.meta)
        del self.meta['scope']
        with mock.patch.object(first_action, '_broker_cli',
                               side_effect=AssertionError(
                                   'broker CLI must not be called')):
            rc, out, err, timed_out, elapsed, detail = \
                first_action.broker_attempt(
                    str(self.state / 'obs1.json'), self.actions, 20.0,
                    self.state, self.meta, 'eDP-2', 'Muse')
        self.assertEqual(rc, 1)
        self.assertIn('CB-2', out)
        self.assertIn('scope', out)

    def test_retry_restamps_with_the_fresh_observation(self):
        # R1/W1: the retried act must carry the FRESH observation's
        # stamps, not the original meta's, or the binding check in
        # desktop_act refuses the retry as stale.
        seen = []
        transient = {'ok': False, 'error': 'focus changed'}
        fresh = dict(self.meta)
        fresh['id'] = 'obs2'
        fresh['observation'] = str(self.state / 'obs2.json')
        rc, out, err, timed_out, elapsed, detail = \
            self._run_attempt_capturing([
                ('start', {'ok': True, 'status': 'starting',
                           'generation': 'g1'}, 0),
                ('status', {'ok': True, 'generation': 'g1',
                           'state': 'running', 'driver': 'ready'}, 0),
                ('request', {'ok': True, 'status': 'accepted',
                             'sequence': 1}, 0),
                ('result', {'ok': True, 'status': 'completed',
                           'sequence': 1,
                           'response': {'returncode': 1,
                                        'result': transient,
                                        'session_continues': True}}, 0),
                ('request', {'ok': True, 'status': 'accepted',
                             'sequence': 2}, 0),
                ('result', {'ok': True, 'status': 'completed',
                           'sequence': 2,
                           'response': {'returncode': 0, 'result': fresh,
                                        'session_continues': True}}, 0),
                ('request', {'ok': True, 'status': 'accepted',
                             'sequence': 3}, 0),
                ('result', {'ok': True, 'status': 'completed',
                           'sequence': 3,
                           'response': {'returncode': 0,
                                        'result': {'ok': True,
                                                   'completed': 1},
                                        'session_continues': True}}, 0),
                ('finish', {'ok': True, 'status': 'finished'}, 0),
            ], seen)
        self.assertEqual(rc, 0)
        self.assertEqual(detail['broker_retries'], 1)
        self.assertEqual(len(seen), 2)
        self.assertEqual(seen[0][0]['observation_id'], 'obs1')
        self.assertEqual(seen[1][0]['observation_id'], 'obs2')
        self.assertEqual(seen[1][0]['scope'], 'screen')

    def test_start_waits_for_running_before_request(self):
        # The relay answers start with `starting` before the driver
        # prints ready; a request sent in that window is refused with
        # task_stopped. broker_attempt polls status until the task is
        # running (driver ready) before requesting.
        act = {'ok': True, 'completed': 1}
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                        'state': 'starting', 'driver': 'starting'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                        'state': 'running', 'driver': 'ready'}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 1}, 0),
            ('result', {'ok': True, 'status': 'completed', 'sequence': 1,
                       'response': {'returncode': 0, 'result': act,
                                    'session_continues': True}}, 0),
            ('finish', {'ok': True, 'status': 'finished'}, 0),
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out), act)
        self.assertEqual(detail['broker_sequences'], [1])

    def test_start_failed_before_request_falls_back(self):
        # The task failed while starting (driver never became ready):
        # no request was sent, so the fallback is safe and the error
        # carries the session-guardian prefix.
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                        'state': 'failed', 'driver': 'failed',
                        'error': 'driver_not_ready'}, 0),
            ('finish', {'ok': True, 'status': 'failed',
                        'error': 'driver_not_ready'}, 0),
        ])
        self.assertEqual(rc, 1)
        self.assertFalse(timed_out)
        self.assertTrue(first_action.is_session_start_failure(out, False))
        self.assertIn('driver_not_ready', out)
        self.assertEqual(detail['broker_sequences'], [])

    def test_result_timeout_never_falls_back(self):
        rc, out, err, timed_out, elapsed, detail = self._run_attempt([
            ('start', {'ok': True, 'status': 'starting',
                       'generation': 'g1'}, 0),
            ('status', {'ok': True, 'generation': 'g1',
                       'state': 'running', 'driver': 'ready'}, 0),
            ('request', {'ok': True, 'status': 'accepted', 'sequence': 1}, 0),
            ('result', None, None),
            ('finish', {'ok': False, 'status': 'cleaning',
                        'error': 'cleanup_pending'}, 0),
        ])
        self.assertTrue(timed_out)
        self.assertFalse(
            first_action.is_session_start_failure(out, timed_out))


class TestAcquireOverlay(unittest.TestCase):
    def test_visible(self):
        fake = FakeOverlay(visible=True)
        reply = first_action.acquire_overlay('Muse', 'act-now',
                                             overlay_mod=fake)
        self.assertTrue(reply['visible'])
        self.assertIn(('add', 'Muse', 'act-now', os.getpid()),
                      fake.calls)

    def test_not_visible_refuses_and_leaks_nothing(self):
        fake = FakeOverlay(visible=False)
        with self.assertRaises(RuntimeError):
            first_action.acquire_overlay('Muse', 'act-now', overlay_mod=fake)
        self.assertEqual(fake.holders, {})

    def test_daemon_start_failure_refuses_and_leaks_nothing(self):
        fake = FakeOverlay(visible=True)
        fake._ensure_daemon = mock.Mock(
            side_effect=RuntimeError('overlay daemon exited'))
        with self.assertRaises(RuntimeError):
            first_action.acquire_overlay('Muse', 'act-now', overlay_mod=fake)
        self.assertEqual(fake.holders, {})

    def test_release_never_raises(self):
        fake = FakeOverlay(visible=True)
        fake._send_socket = mock.Mock(side_effect=OSError('no socket'))
        self.assertIsNone(first_action.release_overlay(
            'Muse', overlay_mod=fake))

    def test_release_returns_error_on_failure(self):
        fake = FakeOverlay(visible=True)
        fake._send_socket = mock.Mock(side_effect=OSError('no socket'))
        fake.remove_holder = mock.Mock(
            side_effect=OSError('no holders file'))
        self.assertIsNotNone(first_action.release_overlay(
            'Muse', overlay_mod=fake))


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

    def _run(self, actions, session_result, **arg_overrides):
        path = _write_actions(self.tmp.name, actions)
        # Step 8: run() calls broker_attempt (6-tuple). The tests still
        # pass the old 5-tuple session result; the broker detail is
        # appended here so every existing session-path case keeps its
        # shape.
        result6 = tuple(session_result) + (
            {'broker_owner': 'Muse', 'broker_sequences': [1],
             'broker_retries': 0,
             'broker_finish': {'ok': True, 'status': 'finished'}},)
        with mock.patch.object(first_action, 'broker_attempt',
                               return_value=result6):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(_args(path, **arg_overrides))
        # json.loads raises unless stdout is exactly one JSON object.
        return code, json.loads(buf.getvalue()), path

    def _run_raw_args(self, args, session_result):
        result6 = tuple(session_result) + (
            {'broker_owner': 'Muse', 'broker_sequences': [1],
             'broker_retries': 0,
             'broker_finish': {'ok': True, 'status': 'finished'}},)
        with mock.patch.object(first_action, 'broker_attempt',
                               return_value=result6):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(args)
        return code, json.loads(buf.getvalue())

    def test_session_path(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5))
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

    def test_session_path_rc0_ok_false_not_ok(self):
        # Council 1, A3: the exit code alone never proves success.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": false, "error": "screen changed", "completed": 0}',
             '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_session_path_completed_capture_error_ok(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": false, "capture_error": "after capture failed", '
             '"completed": 1, "error": "capture failed"}',
             '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['completed'], 1)

    def test_session_path_rc0_empty_stdout_not_ok(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'session')

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
        # A5: the overlay is re-checked (sync, live show ack) before the
        # fallback acts.
        self.assertIn(('send', 'sync', None), self.fake_overlay.calls)

    def test_fallback_path_on_driver_registration_failure(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "driver registration failed: '
             'guard closed"}',
             '', False, 0.4))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertEqual(len(self.fake_cu.desktop_calls), 1)

    def test_fallback_with_dom_selector_passes_dom_hooks(self):
        # Item A: --dom-selector wires the DOM value hooks into the
        # fallback desktop_act. The hooks are the real dom_act
        # closures over a fake Zen session: focus_check reads the
        # live field, and type_check fails before the text lands and
        # passes after it, proving the hook reads the DOM value
        # instead of stubbing a pass.
        import dom_act
        fields = {'#msg-input': {'value': None, 'focused': True}}
        fake_session = FakeZenSession(fields)
        fake_zen_dom = mock.Mock()
        fake_zen_dom.ZenSession = lambda *a, **k: fake_session
        saved_zen_dom = sys.modules.get('zen_dom')
        saved_dom_act = sys.modules.get('dom_act')
        sys.modules['zen_dom'] = fake_zen_dom
        sys.modules['dom_act'] = dom_act
        try:
            code, env, _ = self._run(
                [{'type': 'click', 'x': 10, 'y': 10},
                 {'type': 'type', 'text': 'hello'}],
                (1, '{"ok": false, "error": "session guardian startup failed"}',
                 '', False, 0.4),
                dom_selector='#msg-input')
        finally:
            if saved_zen_dom is None:
                sys.modules.pop('zen_dom', None)
            else:
                sys.modules['zen_dom'] = saved_zen_dom
            if saved_dom_act is None:
                sys.modules.pop('dom_act', None)
            else:
                sys.modules['dom_act'] = saved_dom_act
        self.assertEqual(code, 0)
        self.assertEqual(env['path'], 'fallback')
        self.assertEqual(env['dom_hooks'], 'dom-value')
        self.assertEqual(len(self.fake_cu.desktop_calls), 1)
        kwargs = self.fake_cu.desktop_kwargs[0]
        self.assertIsNotNone(kwargs.get('focus_check'))
        self.assertIsNotNone(kwargs.get('type_check'))
        self.assertEqual(kwargs['focus_check'](), (True, None))
        self.assertFalse(kwargs['type_check']()[0])
        fields['#msg-input']['value'] = 'hello'
        self.assertEqual(kwargs['type_check'](), (True, None))

    def test_fallback_with_window_observation_supplies_ranges(self):
        # AMEND4 item 9 (C2 A3): with a window-scope observation and
        # a groundable field, first_action supplies the grounded
        # x-range and y-range to the fallback desktop_act, so the
        # band reads only that field. A screen-scope observation (no
        # window_bounds) supplies no ranges, which the companion
        # test above pins by omission.
        import dom_act
        fields = {'#msg-input': {
            'value': None, 'focused': True,
            'rect': {'x': 86, 'y': 1101, 'width': 440, 'height': 63}}}
        fake_session = FakeZenSession(fields)
        fake_zen_dom = mock.Mock()
        fake_zen_dom.ZenSession = lambda *a, **k: fake_session
        saved_zen_dom = sys.modules.get('zen_dom')
        saved_dom_act = sys.modules.get('dom_act')
        sys.modules['zen_dom'] = fake_zen_dom
        sys.modules['dom_act'] = dom_act
        obs_path = Path(self.tmp.name) / 'obs-window.json'
        obs_path.write_text(json.dumps({
            'id': 'obs-window-1',
            'image': str(Path(self.tmp.name) / 'obs.jpg'),
            'monitor_box': [0, 0, 1920, 1200],
            'created': time.time(),
            'image_size': [901, 1176],
            'region': [2533, 914, 901, 1176],
            'window_bounds': [2533, 914, 901, 1176]}))
        try:
            code, env, _ = self._run(
                [{'type': 'click', 'x': 10, 'y': 10},
                 {'type': 'type', 'text': 'hello'}],
                (1, '{"ok": false, "error": "session guardian startup failed"}',
                 '', False, 0.4),
                dom_selector='#msg-input', observation=str(obs_path))
        finally:
            if saved_zen_dom is None:
                sys.modules.pop('zen_dom', None)
            else:
                sys.modules['zen_dom'] = saved_zen_dom
            if saved_dom_act is None:
                sys.modules.pop('dom_act', None)
            else:
                sys.modules['dom_act'] = saved_dom_act
        self.assertEqual(code, 0)
        self.assertEqual(env['path'], 'fallback')
        self.assertEqual(env['dom_hooks'], 'dom-value')
        self.assertEqual(len(self.fake_cu.desktop_calls), 1)
        kwargs = self.fake_cu.desktop_kwargs[0]
        self.assertEqual(kwargs.get('type_x_ranges'), [[86.0, 526.0]])
        self.assertEqual(kwargs.get('type_y_ranges'), [[1101.0, 1164.0]])

    def test_fallback_without_dom_selector_passes_no_hooks(self):
        # No --dom-selector: the fallback batch runs exactly as
        # before, with no hook kwargs and no dom_hooks claim.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100},
             {'type': 'type', 'text': 'hello'}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 0)
        self.assertEqual(env['path'], 'fallback')
        self.assertIsNone(env['dom_hooks'])
        self.assertEqual(self.fake_cu.desktop_kwargs[0], {})

    def test_timeout_never_replays(self):
        # Council 1, B1.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '', '', True, 20.0))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertIn('timed out', env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_timeout_after_driver_started_never_replays(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "screen changed", "completed": 1}',
             '', True, 20.0))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_mid_session_guard_lost_never_replays(self):
        # Council 1, B2.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '', 'session guardian died mid-session: session cursor '
             'guard lost', False, 5.0))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_late_expecting_value_never_replays(self):
        # Council 1, B2.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "Expecting value: line 1 column '
             '1 (char 0)", "completed": 1}',
             '', False, 5.0))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

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
        self.assertEqual(self.fake_overlay.holders, {})

    def test_overlay_lost_before_fallback_refuses(self):
        # Council 1, A5: the daemon dies after acquire, before fallback.
        self.fake_overlay.fail_status = True
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertIn('overlay lost', env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_bad_actions_file_envelope(self):
        # Council 1, A4: a bad actions file goes through the envelope
        # and the log, not an ad-hoc print.
        missing = str(Path(self.tmp.name) / 'nope.json')
        code, env = self._run_raw_args(
            _args(missing), (0, '', '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'bad_actions')
        self.assertIn('bad actions file', env['error'])
        log = list(self.fake_cu.state.glob('first-action-*.jsonl'))
        self.assertEqual(len(log), 1)
        self.assertEqual(json.loads(log[0].read_text().splitlines()[0])
                         ['path'], 'bad_actions')

    def test_empty_actions_list_envelope(self):
        path = _write_actions(self.tmp.name, [])
        code, env = self._run_raw_args(
            _args(path), (0, '', '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'bad_actions')
        self.assertIn('non-empty', env['error'])

    def test_nan_deadline_refused_single_json(self):
        # Council 1, A2: an invalid deadline is refused, and stdout
        # stays exactly one JSON object.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5), session_deadline_s=float('nan'))
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')
        self.assertIn('deadline', env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_negative_deadline_refused(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5), session_deadline_s=-1)
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')

    def test_huge_deadline_refused(self):
        # Redteam A2: the deadline is bounded by the observation
        # freshness window (120 s).
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5), session_deadline_s=3600)
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')
        self.assertIn('deadline', env['error'])

    def test_target_breached_recorded(self):
        # Redteam A2: the envelope records whether the whole run
        # exceeded the 30 s target.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertIs(env['target_breached'], False)
        self.assertLess(env['total_ms'], 30000)

    def test_fallback_desktop_act_raises_single_json(self):
        # Council 1, A2: an exception in the fallback must not print a
        # second JSON object after the envelope.
        self.fake_cu.desktop_act = mock.Mock(
            side_effect=RuntimeError('pointer gone'))
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertIn('pointer gone', env['error'])
        # Redteam A5: the after-capture is still attempted.
        self.assertEqual(len(self.fake_cu.observe_calls), 2)

    def test_fallback_desktop_act_raises_valueerror(self):
        # Redteam A5: a preflight refusal (PreflightRefusal is a
        # ValueError subclass) lands in the envelope, cleanly. The
        # refusal message is a current one: the old 'screen
        # observations support pointer actions only' message is gone
        # with the deleted legality refusal (protocol section 8).
        self.fake_cu.desktop_act = mock.Mock(
            side_effect=ValueError('stale_ref: scope_changed'))
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertIn('stale_ref: scope_changed', env['error'])
        self.assertEqual(len(self.fake_cu.observe_calls), 2)

    def test_stale_monitor_observation_raises_single_json(self):
        # Council 1, A2: an exception in the fresh observation must
        # not print a second JSON object either.
        self.fake_cu.observe_screen = mock.Mock(
            side_effect=ValueError('monitor gone'))
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '', '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'refused')
        self.assertIn('monitor gone', env['error'])

    def _write_obs(self, obs_id, age_s):
        path = Path(self.tmp.name) / ('obs-' + obs_id + '.json')
        path.write_text(json.dumps(
            {'id': obs_id, 'image': '/x.jpg',
             'monitor_box': [0, 0, 901, 1176],
             'created': time.time() - age_s}))
        return str(path)

    def _write_window_obs(self, obs_id, age_s=10, scope='window'):
        # A production-shaped window (or screen) observation: fresh,
        # with scope, image size, region, and window bounds.
        # scope=None writes a scope-less meta (a pre-scope build):
        # it still carries a window and bounds, just no scope field.
        meta = {'id': obs_id, 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'window': '0x55705383d420',
                'window_bounds': [2533, 914, 901, 1176],
                'image_size': [901, 1176],
                'region': [2533, 914, 901, 1176],
                'created': time.time() - age_s}
        if scope is not None:
            meta['scope'] = scope
        path = Path(self.tmp.name) / ('obs-' + obs_id + '.json')
        path.write_text(json.dumps(meta))
        return str(path)

    def test_stale_given_observation_refused_loudly_typing_batch(self):
        # G28 regression (CL1-MSG batch 2): a stale given window
        # observation must be refused LOUDLY before any session
        # attempt, naming the given id and its age, instead of
        # silently falling back to a screen capture the batch then
        # acts on (or refuses with a misleading scope error).
        obs = self._write_obs('8fef498445d2', 114)
        path = _write_actions(self.tmp.name,
                              [{'type': 'click', 'x': 250, 'y': 1037},
                               {'type': 'type', 'text': 'hi'}])
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(
                    _args(path, observation=obs))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'refused')
        self.assertIn('8fef498445d2', env['error'])
        self.assertIn('stale', env['error'])
        self.assertIn('114', env['error'])
        self.assertIn('re-observe', env['error'])
        self.assertEqual(env['observation']['source'], 'captured')
        self.assertEqual(
            env['observation']['given_observation_rejected']['given_id'],
            '8fef498445d2')
        self.assertEqual(self.fake_cu.desktop_calls, [])
        log = list(self.fake_cu.state.glob('first-action-*.jsonl'))
        self.assertEqual(len(log), 1)
        logged = json.loads(log[0].read_text().splitlines()[0])
        self.assertEqual(logged['path'], 'refused')
        self.assertIn('8fef498445d2', logged['error'])

    def test_stale_given_observation_pointer_only_refused(self):
        # G28 widened (amend): the loud refusal fires for EVERY batch
        # when a given observation was rejected, not only for key/type
        # batches. A pointer-only batch on the substituted screen
        # capture would run window-image coordinates against a screen
        # region, off by the window offset, and cursorpos cannot catch
        # it. The run refuses before any session attempt, with
        # fallback_reason naming the stale observation, and the
        # pointer-only remedy (screen coordinates) is offered.
        obs = self._write_obs('8fef498445d2', 114)
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(
                    _args(_write_actions(
                        self.tmp.name,
                        [{'type': 'click', 'x': 250, 'y': 1037}]),
                        observation=obs))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'refused')
        self.assertIn('8fef498445d2', env['error'])
        self.assertIn('stale', env['error'])
        self.assertIn('114', env['error'])
        self.assertIn('omit --observation', env['error'])
        self.assertIn('8fef498445d2', env['fallback_reason'])
        self.assertEqual(env['observation']['source'], 'captured')
        self.assertEqual(
            env['observation']['given_observation_rejected']['given_id'],
            '8fef498445d2')
        self.assertEqual(self.fake_cu.desktop_calls, [])
        log = list(self.fake_cu.state.glob('first-action-*.jsonl'))
        self.assertEqual(len(log), 1)
        logged = json.loads(log[0].read_text().splitlines()[0])
        self.assertEqual(logged['path'], 'refused')
        self.assertIn('8fef498445d2', logged['fallback_reason'])

    def test_stale_given_observation_refusal_key_type_offers_window_only(self):
        # RT R4: on the key/type path the refusal must NOT offer the
        # screen-coordinates remedy, because a type batch with no
        # observation ends at desktop_act on a screen observation,
        # which refuses key/type. Only the fresh window remedy applies.
        obs = self._write_obs('8fef498445d2', 114)
        path = _write_actions(self.tmp.name,
                              [{'type': 'click', 'x': 250, 'y': 1037},
                               {'type': 'type', 'text': 'hi'}])
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(
                    _args(path, observation=obs))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')
        self.assertIn('re-observe', env['error'])
        self.assertNotIn('omit --observation', env['error'])

    def test_session_type_verified_and_error_code_surfaced_in_envelope(self):
        # RT R3: type_verified and error_code from the session result
        # reach the act-now envelope instead of being dropped.
        code, env, _ = self._run(
            [{'type': 'type', 'text': 'X'}],
            (0, json.dumps({'ok': False, 'completed': 1,
                            'error': 'type verification failed',
                            'error_code': 'type_unverified',
                            'type_verified': False}), '', False, 0.5))
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertIs(env['type_verified'], False)
        self.assertEqual(env['error_code'], 'type_unverified')

    def test_session_without_verification_fields_reports_none(self):
        # RT R3: the fields are always present in the envelope, None
        # when the session result carries neither.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertIn('type_verified', env)
        self.assertIsNone(env['type_verified'])
        self.assertIn('error_code', env)
        self.assertIsNone(env['error_code'])

    def test_fallback_type_verified_and_error_code_surfaced_in_envelope(self):
        # RT R3 on the fallback path: the direct desktop_act result
        # carries the fields into the envelope.
        self.fake_cu.desktop_act = mock.Mock(
            return_value={'ok': False, 'completed': 1,
                          'error': 'type verification failed',
                          'error_code': 'type_unverified',
                          'type_verified': False})
        code, env, _ = self._run(
            [{'type': 'type', 'text': 'X'}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'fallback')
        self.assertIs(env['type_verified'], False)
        self.assertEqual(env['error_code'], 'type_unverified')

    def test_stale_given_observation_refused_loudly_key_only_batch(self):
        # G28, SRC spec: the refusal covers key actions too, not only
        # type actions.
        obs = self._write_obs('8fef498445d2', 114)
        path = _write_actions(self.tmp.name,
                              [{'type': 'key', 'keys': ['Enter']}])
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(
                    _args(path, observation=obs))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')
        self.assertIn('8fef498445d2', env['error'])
        self.assertIn('stale', env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_fresh_given_observation_typing_batch_reaches_session(self):
        # The refusal fires only on a rejected given observation: a
        # fresh given window observation with typing still runs.
        obs = self._write_obs('c9e5e9cb4bc0', 10)
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (0, '{"ok": true, "completed": 2}', '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['observation']['source'], 'given')
        self.assertNotIn('given_observation_rejected',
                         env['observation'])

    def test_captured_source_window_bound_batch_refused_loudly(self):
        # R7 (tracker J35/J40): no --observation given, so act-now
        # captures a screen observation. A batch bound to window
        # scope carries window-space points; running them on the
        # screen capture misses by the window origin offset with a
        # success envelope. The run must refuse loudly BEFORE any
        # session attempt, naming the captured source.
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(_args(_write_actions(
                    self.tmp.name,
                    [{'type': 'click', 'x': 160, 'y': 21,
                      'scope': 'window',
                      'observation_id': 'win-obs-9'}])))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertFalse(env['ok'])
        self.assertEqual(env['path'], 'refused')
        self.assertEqual(env['observation']['source'], 'captured')
        self.assertIn('captured', env['error'])
        self.assertIn('window', env['error'])
        self.assertIn('refusing', env['error'])
        self.assertEqual(env['fallback_reason'], env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_captured_source_foreign_observation_id_refused(self):
        # R7, id form: a batch bound to another observation id (no
        # scope field) is likewise refused on the captured source.
        with mock.patch.object(first_action, 'broker_attempt') as sess:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = first_action.run(_args(_write_actions(
                    self.tmp.name,
                    [{'type': 'click', 'x': 160, 'y': 21,
                      'observation_id': 'some-other-obs'}])))
        env = json.loads(buf.getvalue())
        sess.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(env['path'], 'refused')
        self.assertIn('some-other-obs', env['error'])
        self.assertEqual(self.fake_cu.desktop_calls, [])

    def test_captured_source_unbound_batch_still_runs(self):
        # R7 control: unbound actions on the captured source are
        # screen coordinates by definition (the documented default)
        # and still reach the session.
        code, env, _ = self._run(
            [{'type': 'click', 'x': 160, 'y': 21}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['observation']['source'], 'captured')

    def test_captured_source_refusal_helper(self):
        # R7 pure helper: matching bindings and unbound actions
        # pass; a scope or id mismatch names the action index.
        meta = {'id': 'cap-1', 'scope': 'screen'}
        self.assertIsNone(first_action.captured_source_refusal(
            [{'type': 'click', 'x': 1, 'y': 2}], meta))
        self.assertIsNone(first_action.captured_source_refusal(
            [{'type': 'click', 'x': 1, 'y': 2, 'scope': 'screen',
              'observation_id': 'cap-1'}], meta))
        msg = first_action.captured_source_refusal(
            [{'type': 'click', 'x': 1, 'y': 2},
             {'type': 'click', 'x': 3, 'y': 4, 'scope': 'window'}],
            meta)
        self.assertIn('action 1', msg)
        self.assertIn('captured', msg)

    def test_session_after_is_scope_matching_not_screen(self):
        # AMEND4 item 12 (CL1-SWEEP regression): the envelope 'after'
        # must be the scope-matching capture, not the screen capture.
        # The session result carries desktop_act's window-scope after;
        # the envelope must copy it, and 'after_screen' carries the
        # full-monitor capture separately, for verification only.
        obs = self._write_window_obs('win-obs-1')
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (0, json.dumps({'ok': True, 'completed': 2,
                            'after': {'id': 'sess-after-1',
                                      'observation': '/tmp/sess-after.json',
                                      'scope': 'window'}}),
             '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['after']['id'], 'sess-after-1')
        self.assertEqual(env['after']['observation'],
                         '/tmp/sess-after.json')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')
        self.assertNotEqual(env['after']['id'],
                            env['after_screen']['id'])

    def test_fallback_after_is_scope_matching_not_screen(self):
        # AMEND4 item 12: the same contract on the fallback path,
        # where the direct desktop_act result carries the window-scope
        # after. Reusing the screen capture as 'after' is the trap
        # that made the CL1-SWEEP Enter step fail its preflight.
        obs = self._write_window_obs('win-obs-2')
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertEqual(env['after']['id'], 'after-1')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')
        self.assertNotEqual(env['after']['id'],
                            env['after_screen']['id'])

    def test_after_without_result_after_captures_fresh_window(self):
        # AMEND4 item 12: when neither path carries an after (the
        # action result has none), the envelope 'after' is captured
        # fresh in the input observation's scope, not from the screen.
        obs = self._write_window_obs('win-obs-3')
        self.fake_cu.desktop_act = mock.Mock(
            return_value={'ok': True, 'completed': 2})
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['after']['id'], 'win-after-1')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')

    def test_screen_observation_key_batch_proceeds_to_session(self):
        # Protocol section 8 (P2): the pre-overlay screen-scope
        # key/type refusal is DELETED. A key batch given a fresh
        # screen-scope observation now proceeds to the session
        # attempt, and the outcome is the session's outcome; the
        # scope alone no longer refuses it. (The old test pinned the
        # AMEND4 item 12 refusal; the refusal changed form into
        # snapshot binding, enforced by desktop_act.)
        obs = self._write_window_obs('scr-obs-1', scope='screen')
        code, env, _ = self._run(
            [{'type': 'key', 'keys': ['Return']}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertNotIn('screen observations support pointer actions',
                         env.get('error') or '')

    def test_scope_after_prefers_result_after_for_scopeless_window_meta(self):
        # TESTREPAIR (round 3, RT item 12 residual): a scope-less
        # WINDOW meta must prefer a correct window-scope result_after
        # instead of discarding it for the screen capture. The input
        # observation carries a window but no scope field (pre-scope
        # build); the session result carries desktop_act's
        # window-scope after. The envelope 'after' must be that
        # result_after, with zero fresh window observes: the correct
        # after is reused, not recaptured.
        obs = self._write_window_obs('win-obs-4', scope=None)
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (0, json.dumps({'ok': True, 'completed': 2,
                            'after': {'id': 'sess-after-1',
                                      'observation': '/tmp/sess-after.json',
                                      'scope': 'window'}}),
             '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['after']['id'], 'sess-after-1')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')
        self.assertNotIn(('window', '0x55705383d420'),
                         self.fake_cu.observe_calls,
                         'a correct window-scope after was discarded '
                         'for a fresh capture')

    def test_scope_after_mismatched_result_after_recaptures_window(self):
        # TESTREPAIR (round 3, RT item 12 coverage): a screen-scope
        # result_after given a window-scope input does NOT match, so
        # the envelope 'after' is captured fresh in the input window
        # scope, not the screen capture and not the mismatched after.
        obs = self._write_window_obs('win-obs-5')
        code, env, _ = self._run(
            [{'type': 'click', 'x': 250, 'y': 1037},
             {'type': 'type', 'text': 'hi'}],
            (0, json.dumps({'ok': True, 'completed': 2,
                            'after': {'id': 'sess-after-screen',
                                      'observation': '/tmp/sess.json',
                                      'scope': 'screen'}}),
             '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['after']['id'], 'win-after-1')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')

    def test_scope_after_screen_input_reuses_screen_without_recapture(self):
        # TESTREPAIR (round 3, RT item 12 coverage): a screen-scope
        # input with no result after reuses the screen capture as
        # its scope-matching after, with no extra window observe:
        # the screen capture IS its scope-matching after.
        obs = self._write_window_obs('scr-obs-2', scope='screen')
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5),
            observation=obs)
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'session')
        self.assertEqual(env['after']['id'], 'a1b2c3d4e5f6')
        self.assertEqual(env['after_screen']['id'], 'a1b2c3d4e5f6')
        self.assertNotIn(('window', '0x55705383d420'),
                         self.fake_cu.observe_calls,
                         'a screen input took a needless window '
                         'recapture')

    def test_session_ime_state_trace_surfaced_in_envelope(self):
        # CLICK-PROBE Stage A: ime_state_trace was absent from act-now
        # envelopes, leaving a silent type failure with no IME
        # evidence. The session result carries it (desktop_act merges
        # ime_result); act-now must surface it in the envelope.
        trace = [{'phase': 'before', 'state': '2',
                  'state_source': 'initial_query', 'status': 'observed'},
                 {'phase': 'after_switch', 'state': '1',
                  'state_source': 'switch_query', 'status': 'observed'},
                 {'phase': 'after_restore', 'state': '2',
                  'state_source': 'switch_query', 'status': 'observed'}]
        code, env, _ = self._run(
            [{'type': 'type', 'text': 'X'}],
            (0, json.dumps({'ok': True, 'completed': 1,
                            'ime_state_trace': trace}), '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['ime_state_trace'], trace)

    def test_session_without_ime_trace_reports_none(self):
        code, env, _ = self._run(
            [{'type': 'click', 'x': 100, 'y': 100}],
            (0, '{"ok": true, "completed": 1}', '', False, 0.5))
        self.assertEqual(code, 0)
        self.assertIsNone(env['ime_state_trace'])

    def test_fallback_ime_state_trace_surfaced_in_envelope(self):
        trace = [{'phase': 'before', 'state': '1',
                  'state_source': 'initial_query', 'status': 'observed'}]
        self.fake_cu.desktop_act = mock.Mock(
            return_value={'ok': True, 'completed': 1,
                          'after': str(self.fake_cu.state / 'after.json'),
                          'ime_state_trace': trace})
        code, env, _ = self._run(
            [{'type': 'type', 'text': 'X'}],
            (1, '{"ok": false, "error": "session guardian startup failed"}',
             '', False, 0.4))
        self.assertEqual(code, 0)
        self.assertTrue(env['ok'])
        self.assertEqual(env['path'], 'fallback')
        self.assertEqual(env['ime_state_trace'], trace)


class TestFreshObservation(unittest.TestCase):
    def test_given_fresh_used(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time()}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        out_meta, out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path))
        self.assertEqual(source, 'given')
        self.assertIsNone(rejected)
        self.assertEqual(out_meta['id'], 'deadbeefcafe')
        self.assertEqual(fake_cu.observe_calls, [])

    def test_stale_replaced_by_capture(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time() - 600}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path))
        self.assertEqual(source, 'captured')
        self.assertEqual(fake_cu.observe_calls, ['eDP-2'])
        # G28: the substitution is reported, not silent.
        self.assertEqual(rejected['given_id'], 'deadbeefcafe')
        self.assertIn('stale', rejected['reason'])
        self.assertGreater(rejected['age_s'], 500)

    def test_stale_batch2_age_114_rejected(self):
        # G28 regression, the exact CL1-MSG batch 2 case: a 114 s old
        # window observation plus the 20 s deadline reaches 134 s,
        # past the 120 s window, so it is rejected, not silently
        # replaced by a screen capture the batch then acts on.
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': '8fef498445d2', 'image': '/x.jpg',
                'monitor_box': [0, 0, 901, 1176],
                'created': time.time() - 114}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path), deadline_s=20.0)
        self.assertEqual(source, 'captured')
        self.assertEqual(rejected['given_id'], '8fef498445d2')
        self.assertIn('stale', rejected['reason'])
        msg = first_action.loud_substitution_refusal(rejected)
        self.assertIn('8fef498445d2', msg)
        self.assertIn('114', msg)
        self.assertIn('re-observe', msg)

    def test_missing_file_rejected(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        missing = str(Path(fake_cu.tmp) / 'nope.json')
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', missing)
        self.assertEqual(source, 'captured')
        self.assertIsNone(rejected['given_id'])
        self.assertIn('unreadable', rejected['reason'])

    def test_incomplete_observation_rejected(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'created': time.time()}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path))
        self.assertEqual(source, 'captured')
        self.assertEqual(rejected['given_id'], 'deadbeefcafe')
        self.assertIn('incomplete', rejected['reason'])

    def test_no_observation_given_is_not_a_rejection(self):
        # No --observation is the documented default (fresh screen
        # capture), not a substitution: nothing is rejected.
        fake_cu = FakeCu(tempfile.mkdtemp())
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', None)
        self.assertEqual(source, 'captured')
        self.assertIsNone(rejected)

    def test_age_plus_deadline_must_stay_under_120(self):
        # Redteam A6: a 110 s old observation plus a 20 s deadline
        # would be 130 s at act time, so it is replaced.
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time() - 110}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path), deadline_s=20.0)
        self.assertEqual(source, 'captured')
        self.assertIn('stale', rejected['reason'])

    def test_age_plus_deadline_within_120_is_used(self):
        fake_cu = FakeCu(tempfile.mkdtemp())
        meta = {'id': 'deadbeefcafe', 'image': '/x.jpg',
                'monitor_box': [0, 0, 1920, 1200],
                'created': time.time() - 90}
        path = Path(fake_cu.tmp) / 'obs.json'
        path.write_text(json.dumps(meta))
        _out_meta, _out_path, source, rejected = first_action._fresh_observation(
            fake_cu, {}, 'eDP-2', str(path), deadline_s=20.0)
        self.assertEqual(source, 'given')
        self.assertIsNone(rejected)


if __name__ == '__main__':
    unittest.main(verbosity=2)

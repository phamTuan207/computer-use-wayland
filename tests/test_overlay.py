"""Overlay central control: holder registry and labels. No Wayland needed."""
import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import overlay


def _isolated(tmp):
    overlay.BASE = Path(tmp) / 'agent-computer-use'
    overlay.OVERLAY_DIR = overlay.BASE / 'overlay'
    overlay.HOLDERS_FILE = overlay.OVERLAY_DIR / 'holders.json'
    overlay.DAEMON_FILE = overlay.OVERLAY_DIR / 'daemon.json'
    overlay.SOCKET_FILE = overlay.OVERLAY_DIR / 'overlay.sock'
    overlay.LOCK_FILE = overlay.OVERLAY_DIR / 'holders.lock'
    overlay.LOG_FILE = overlay.OVERLAY_DIR / 'daemon.log'
    overlay.SESSION_FILE = overlay.BASE / 'session.json'


def test_wayland_env_discovers_signature_from_hypr_dir():
    """W-PILLFIX: an SSH caller carries no signature, so wayland_env must
    find it under <runtime>/hypr/, the layout hypr_cmd.desktop_env uses.
    The old code read <runtime>/hyprland/, which does not exist here, so
    every standalone native spawn failed with the liquid-glass error
    while hyprglass itself was healthy."""
    with tempfile.TemporaryDirectory() as tmp:
        sig_dir = Path(tmp) / 'hypr'
        sig_dir.mkdir()
        (sig_dir / 'deadbeef_1_2').mkdir()
        with patch.dict(os.environ, {'XDG_RUNTIME_DIR': tmp}, clear=True):
            env = overlay.wayland_env()
        assert env['HYPRLAND_INSTANCE_SIGNATURE'] == 'deadbeef_1_2'
        assert env['WAYLAND_DISPLAY'] == 'wayland-1'
        assert env['XDG_RUNTIME_DIR'] == tmp


def test_wayland_env_keeps_caller_signature():
    """A caller-provided signature is kept as-is (the old code clobbered
    it with whatever sig_dirs[0] happened to be)."""
    with patch.dict(os.environ, {
            'HYPRLAND_INSTANCE_SIGNATURE': 'keep-me',
            'XDG_RUNTIME_DIR': '/run/user/1000'}, clear=True):
        env = overlay.wayland_env()
    assert env['HYPRLAND_INSTANCE_SIGNATURE'] == 'keep-me'
    assert env['WAYLAND_DISPLAY'] == 'wayland-1'


def test_wayland_env_without_instance_returns_no_signature():
    """No discoverable instance: env comes back without a signature
    (old behaviour), so the spawn fails loudly instead of crashing here."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.dict(os.environ, {'XDG_RUNTIME_DIR': tmp}, clear=True):
            env = overlay.wayland_env()
    assert 'HYPRLAND_INSTANCE_SIGNATURE' not in env
    assert env['WAYLAND_DISPLAY'] == 'wayland-1'


def test_status_reply_reports_real_visibility():
    """W-PILLFIX (a): daemon status must reconcile first. The old reply
    was visible True whenever holders existed, even with no pill
    rendered; that lie misled a verify lane."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'act-now', pid=os.getpid())
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        daemon.native = _FakeNativeFailing()
        assert daemon.status_reply()['visible'] is False
        daemon.native = _FakeNative(dead=False)
        assert daemon.status_reply()['visible'] is True


def test_cmd_status_no_daemon_is_session_aware():
    """W-PILLFIX (a): with no daemon, holders alone never render a pill;
    only a live session indicator can. Status must say so."""
    import types
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'act-now')
        orig_live = overlay.session_live
        try:
            overlay.session_live = lambda: True
            out = io.StringIO()
            with redirect_stdout(out):
                assert overlay.cmd_status(types.SimpleNamespace()) == 0
            info = json.loads(out.getvalue())
            assert info['visible'] is True
            assert info['owner'] == 'session'
            overlay.session_live = lambda: False
            out = io.StringIO()
            with redirect_stdout(out):
                assert overlay.cmd_status(types.SimpleNamespace()) == 0
            info = json.loads(out.getvalue())
            assert info['visible'] is False
            assert info['owner'] == 'none'
        finally:
            overlay.session_live = orig_live


def test_cmd_acquire_refuses_when_pill_invisible():
    """W-PILLFIX (b): when the daemon answers but the pill did not
    render, cmd_acquire must exit 1 (fail closed) and remove the
    just-added holder, instead of returning 0 and letting the caller
    drive invisibly. This is what chromium_cli._pill_hold documents
    (overlay.hold raises) and what cdp.mjs expects."""
    import types
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        args = types.SimpleNamespace(agent='Muse', method='CDP',
                                     pid=None, label=None)
        orig_ensure = overlay._ensure_daemon
        orig_send = overlay._send_socket
        try:
            overlay._ensure_daemon = lambda: True
            overlay._send_socket = lambda *a, **k: {
                'visible': False, 'owner': 'none',
                'holders': {'Muse': {'agent': 'Muse', 'method': 'CDP',
                                     'acquired': '2026-11-22T19:30:00+07:00',
                                     'pid': None}},
                'error': 'pill show failed'}
            out = io.StringIO()
            with redirect_stdout(out):
                assert overlay.cmd_acquire(args) == 1
            assert json.loads(out.getvalue())['visible'] is False
            assert overlay.load_holders() == {}, \
                'invisible acquire must not leak a holder'
        finally:
            overlay._ensure_daemon = orig_ensure
            overlay._send_socket = orig_send


def test_cmd_acquire_visible_still_succeeds():
    """The fail-closed change above must not break the normal path."""
    import types
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        args = types.SimpleNamespace(agent='Muse', method='CDP',
                                     pid=None, label=None)
        orig_ensure = overlay._ensure_daemon
        orig_send = overlay._send_socket
        try:
            overlay._ensure_daemon = lambda: True
            overlay._send_socket = lambda *a, **k: {
                'visible': True, 'owner': 'daemon', 'holders': {}}
            out = io.StringIO()
            with redirect_stdout(out):
                assert overlay.cmd_acquire(args) == 0
            assert json.loads(out.getvalue())['visible'] is True
            assert overlay.load_holders() != {}
        finally:
            overlay._ensure_daemon = orig_ensure
            overlay._send_socket = orig_send


def test_label_format():
    assert overlay._label_for('Muse', 'BiDi') == 'Muse via BiDi'
    assert overlay._label_for('Codex', 'DOM') == 'Codex via DOM'
    assert overlay._label_for('', '') == 'Computer use active'
    long_label = overlay._label_for('A' * 30, 'B' * 30)
    assert len(long_label) <= overlay.MAX_LABEL


def test_add_release_refcount():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        holders, is_new = overlay.add_holder('Muse', 'BiDi')
        assert is_new and len(holders) == 1
        holders, is_new = overlay.add_holder('Muse', 'BiDi')
        assert not is_new and len(holders) == 1, 'same agent re-acquire must not double count'
        holders, _ = overlay.add_holder('Codex', 'DOM')
        assert len(holders) == 2
        holders, was_present = overlay.remove_holder('Muse')
        assert was_present and len(holders) == 1
        holders, was_present = overlay.remove_holder('Muse')
        assert not was_present and len(holders) == 1
        holders, _ = overlay.remove_holder('Codex')
        assert holders == {}, 'pill hides only when ALL holders released'


def test_same_agent_two_pids_are_independent():
    """Redteam A4: two concurrent same-agent runs are two entries; the
    first release must not hide the pill for the second."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'act-now', pid=111)
        holders, _ = overlay.add_holder('Muse', 'act-now', pid=222)
        assert len(holders) == 2
        holders, was_present = overlay.remove_holder('Muse', 111)
        assert was_present and len(holders) == 1
        assert 'Muse:222' in holders
        holders, _ = overlay.remove_holder('Muse', 222)
        assert holders == {}


def test_remove_holder_pid_none_keeps_pid_keyed_holder():
    """R6/C1: remove_holder with pid None must delete only the bare
    agent entry, never a pid-keyed holder of a concurrent same-agent
    run. The old code wiped every key of the agent, so one failed
    pid-less acquire dropped the pill mid-run for a live run."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'CDP')
        overlay.add_holder('Muse', 'CDP', pid=999001)
        assert set(overlay.load_holders()) == {'Muse', 'Muse:999001'}
        holders, was_present = overlay.remove_holder('Muse', None)
        assert was_present
        assert set(holders) == {'Muse:999001'}
        assert overlay.load_holders() == holders


def test_remove_holder_pid_keeps_bare_holder():
    """R6 reverse direction: remove_holder with a pid must delete only
    that pid-keyed entry, never the bare agent entry. The old code
    removed the bare key too, so a failed pid-keyed acquire wiped the
    holder of overlay.hold."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'CDP')
        overlay.add_holder('Muse', 'CDP', pid=999001)
        assert set(overlay.load_holders()) == {'Muse', 'Muse:999001'}
        holders, was_present = overlay.remove_holder('Muse', 999001)
        assert was_present
        assert set(holders) == {'Muse'}
        assert overlay.load_holders() == holders


def test_cmd_acquire_invisible_keeps_concurrent_holder():
    """C1 end to end: a concurrent pid-keyed holder of the same agent
    is live when a pid-less acquire fails invisible. The failed
    acquire must exit 1 and remove only its own just-added bare key;
    the concurrent holder survives, so the other run keeps its pill."""
    import types
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'CDP', pid=999001)
        args = types.SimpleNamespace(agent='Muse', method='CDP',
                                     pid=None, label=None)
        orig_ensure = overlay._ensure_daemon
        orig_send = overlay._send_socket
        try:
            overlay._ensure_daemon = lambda: True
            overlay._send_socket = lambda *a, **k: {
                'visible': False, 'owner': 'none',
                'holders': {'Muse': {'agent': 'Muse', 'method': 'CDP',
                                     'acquired': '2026-11-22T19:30:00+07:00',
                                     'pid': None}},
                'error': 'pill show failed'}
            out = io.StringIO()
            with redirect_stdout(out):
                assert overlay.cmd_acquire(args) == 1
            assert json.loads(out.getvalue())['visible'] is False
            assert set(overlay.load_holders()) == {'Muse:999001'}, \
                'failed pid-less acquire must not drop a concurrent holder'
        finally:
            overlay._ensure_daemon = orig_ensure
            overlay._send_socket = orig_send


def test_holders_persist_json():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('opencode', 'CLI', pid=123456)
        raw = json.loads(overlay.HOLDERS_FILE.read_text())
        assert raw['opencode:123456']['method'] == 'CLI'
        assert raw['opencode:123456']['pid'] == 123456
        assert raw['opencode:123456']['agent'] == 'opencode'
        assert overlay.load_holders() == raw


def test_prune_dead_pid():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('ghost', 'shell', pid=999999)
        overlay.add_holder('alive', 'shell', pid=os.getpid())
        pruned = overlay.prune_dead_holders()
        assert pruned == ['ghost:999999']
        assert set(overlay.load_holders()) == {'alive:%d' % os.getpid()}


def test_label_command_valid_chars():
    import re
    assert re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label Muse via BiDi')
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label ' + 'x' * 41)
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label bad\nline')


class _FakeProc:
    def __init__(self, dead):
        self._dead = dead
    def poll(self):
        return 1 if self._dead else None


class _FakeNative:
    def __init__(self, dead=False):
        self.process = _FakeProc(dead)
        self.commands = []
        self.closed = False
    def command(self, cmd):
        if self.process.poll() is not None:
            raise OSError('indicator disconnected')
        self.commands.append(cmd)
        return 'ok'
    def close(self):
        self.closed = True


class _FakeNativeFailing:
    """A native indicator whose show command always fails."""
    def __init__(self):
        self.process = _FakeProc(False)
        self.commands = []
        self.closed = False
    def command(self, cmd):
        self.commands.append(cmd)
        raise OSError('indicator refuses show')
    def close(self):
        self.closed = True


def test_show_label_returns_bool():
    """Redteam A3: _show_label returns True on ack, False on failure."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        daemon.native = _FakeNative(dead=False)
        assert daemon._show_label('Muse via BiDi') is True
        daemon.native = _FakeNativeFailing()
        assert daemon._show_label('Muse via BiDi') is False


def test_apply_holders_visible_false_on_show_failure():
    """Redteam A3: apply_holders reports visible False when the pill
    cannot be shown, instead of claiming visible True."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Muse', 'act-now', pid=os.getpid())
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        daemon.native = _FakeNativeFailing()
        status = daemon.apply_holders()
        assert status['visible'] is False
        assert 'error' in status


def test_apply_holders_prunes_dead_holders():
    """Redteam A4: the daemon prunes a dead holder on reconcile, so a
    killed run does not keep the pill up."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('ghost', 'shell', pid=999999)
        overlay.add_holder('Muse', 'act-now', pid=os.getpid())
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        daemon.native = _FakeNative(dead=False)
        status = daemon.apply_holders()
        assert status['visible'] is True
        assert set(overlay.load_holders()) == {'Muse:%d' % os.getpid()}


def test_cmd_acquire_failure_leaks_nothing():
    """Re-review D1: a failed CLI acquire removes the just-added holder,
    so no pid-None entry is left that prune can never drop."""
    import types
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        args = types.SimpleNamespace(agent='Muse', method='act-now',
                                     pid=None, label=None)
        orig_ensure = overlay._ensure_daemon
        orig_send = overlay._send_socket
        try:
            def fail_daemon():
                raise RuntimeError('overlay daemon exited during startup')
            overlay._ensure_daemon = fail_daemon
            try:
                overlay.cmd_acquire(args)
                raise AssertionError('cmd_acquire must raise on daemon failure')
            except RuntimeError:
                pass
            assert overlay.load_holders() == {}, 'daemon failure must not leak a holder'
            overlay._ensure_daemon = lambda: True

            def fail_socket(*a, **k):
                raise OSError('socket gone')
            overlay._send_socket = fail_socket
            try:
                overlay.cmd_acquire(args)
                raise AssertionError('cmd_acquire must raise on socket failure')
            except OSError:
                pass
            assert overlay.load_holders() == {}, 'socket failure must not leak a holder'
            assert overlay.prune_dead_holders() == []

            # D1 re-check hardening: a non-dict reply (unreachable
            # through the real daemon) must not leak either.
            overlay._ensure_daemon = lambda: True
            overlay._send_socket = lambda *a, **k: ['not', 'a', 'dict']
            try:
                overlay.cmd_acquire(args)
                raise AssertionError('cmd_acquire must raise on a non-dict reply')
            except TypeError:
                pass
            assert overlay.load_holders() == {}, 'non-dict reply must not leak a holder'
        finally:
            overlay._ensure_daemon = orig_ensure
            overlay._send_socket = orig_send


def test_daemon_respawns_dead_native():
    """I12: a dead native indicator must be respawned while holders remain,
    not leave the pill invisible. The daemon detects the dead process in
    _show_label and brings a fresh one up before labelling."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        daemon.native = _FakeNative(dead=True)
        spawned = []
        def fake_spawn(env):
            daemon.native = _FakeNative(dead=False)
            daemon.owner = 'daemon'
            spawned.append(True)
        daemon._spawn_native = fake_spawn
        daemon._show_label('Muse via BiDi')
        assert spawned, 'dead native must be respawned'
        assert daemon.native.commands == ['label Muse via BiDi', 'show']


def test_daemon_keeps_live_native():
    """No respawn when the native process is alive: exactly one show."""
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        daemon = overlay.Daemon()
        daemon.owner = 'daemon'
        live = _FakeNative(dead=False)
        daemon.native = live
        spawned = []
        daemon._spawn_native = lambda env: spawned.append(True)
        daemon._show_label('Codex via DOM')
        assert spawned == [], 'live native must not be respawned'
        assert live.commands == ['label Codex via DOM', 'show']


if __name__ == '__main__':
    test_wayland_env_discovers_signature_from_hypr_dir()
    test_wayland_env_keeps_caller_signature()
    test_wayland_env_without_instance_returns_no_signature()
    test_status_reply_reports_real_visibility()
    test_cmd_status_no_daemon_is_session_aware()
    test_cmd_acquire_refuses_when_pill_invisible()
    test_cmd_acquire_visible_still_succeeds()
    test_label_format()
    test_add_release_refcount()
    test_same_agent_two_pids_are_independent()
    test_remove_holder_pid_none_keeps_pid_keyed_holder()
    test_remove_holder_pid_keeps_bare_holder()
    test_cmd_acquire_invisible_keeps_concurrent_holder()
    test_holders_persist_json()
    test_prune_dead_pid()
    test_label_command_valid_chars()
    test_show_label_returns_bool()
    test_apply_holders_visible_false_on_show_failure()
    test_apply_holders_prunes_dead_holders()
    test_cmd_acquire_failure_leaks_nothing()
    test_daemon_respawns_dead_native()
    test_daemon_keeps_live_native()
    print('all overlay tests pass')


def load_tests(loader, standard_tests, pattern):
    from _function_test_support import load_function_tests
    return load_function_tests(globals())

"""Overlay central control: holder registry and labels. No Wayland needed."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

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
    test_label_format()
    test_add_release_refcount()
    test_same_agent_two_pids_are_independent()
    test_holders_persist_json()
    test_prune_dead_pid()
    test_label_command_valid_chars()
    test_show_label_returns_bool()
    test_apply_holders_visible_false_on_show_failure()
    test_apply_holders_prunes_dead_holders()
    test_daemon_respawns_dead_native()
    test_daemon_keeps_live_native()
    print('all overlay tests pass')


def load_tests(loader, standard_tests, pattern):
    from _function_test_support import load_function_tests
    return load_function_tests(globals())

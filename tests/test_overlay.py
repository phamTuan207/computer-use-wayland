"""Overlay central control: holder registry and labels. No Wayland needed."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from argparse import Namespace
from unittest.mock import Mock, patch

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


def test_same_agent_sessions_release_independently():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Browser automation', 'DOM', pid=os.getpid(), holder_id='a' * 32)
        overlay.add_holder('Browser automation', 'DOM', pid=os.getpid(), holder_id='b' * 32)
        holders, removed = overlay.remove_holder(holder_id='a' * 32)
        assert removed and len(holders) == 1
        holders, removed = overlay.remove_holder(holder_id='b' * 32)
        assert removed and holders == {}


def test_holders_persist_json():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('opencode', 'CLI', pid=123456)
        raw = json.loads(overlay.HOLDERS_FILE.read_text())
        assert raw['opencode']['method'] == 'CLI'
        assert raw['opencode']['pid'] == 123456
        assert overlay.load_holders() == raw


def test_prune_dead_pid():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('ghost', 'shell', pid=999999)
        overlay.add_holder('alive', 'shell', pid=os.getpid())
        pruned = overlay.prune_dead_holders()
        assert pruned == ['ghost']
        assert set(overlay.load_holders()) == {'alive'}


def test_unknown_pid_permission_does_not_prune_holder():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('other-user', 'DOM', pid=123456)
        with patch.object(overlay.os, 'kill', side_effect=PermissionError):
            assert overlay.prune_dead_holders() == []
        assert set(overlay.load_holders()) == {'other-user'}


def test_daemon_reuses_broker_indicator_for_browser_holder():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Browser automation', 'DOM')
        daemon = overlay.Daemon()
        with patch.object(overlay, 'session_live', return_value=True), \
                patch.object(overlay, 'session_label', return_value=True), \
                patch.object(overlay, 'wayland_env', side_effect=AssertionError('duplicate overlay')), \
                patch.object(overlay, '_log'):
            status = daemon.apply_holders()
        assert status['visible'] and status['owner'] == 'session'
        assert daemon.native is None


def test_daemon_owns_indicator_when_no_broker_session_exists():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Browser automation', 'DOM')
        native = Mock()
        native.command.return_value = 'ok'
        native.process.poll.return_value = None
        with patch.object(overlay, 'session_live', return_value=False), \
                patch.object(overlay, 'wayland_env', return_value={'PATH': '/fixture'}), \
                patch.object(overlay, '_log'), \
                patch('indicator.Native', return_value=native) as spawn:
            daemon = overlay.Daemon()
            status = daemon.apply_holders()
            assert status['visible'] and status['owner'] == 'daemon'
            assert daemon.native is native
            holders, _ = overlay.remove_holder('Browser automation')
            assert holders == {}
            status = daemon.apply_holders()
        assert not status['visible'] and status['owner'] == 'none'
        assert native.command.call_args_list[-1].args == ('hide',)
        native.close.assert_called_once()
        spawn.assert_called_once()


def test_browser_holder_takes_over_when_broker_indicator_disappears():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        overlay.add_holder('Browser automation', 'DOM/BiDi')
        native = Mock()
        native.command.return_value = 'ok'
        native.process.poll.return_value = None
        live = iter((True, True, False))
        with patch.object(overlay, 'session_live', side_effect=lambda: next(live)), \
                patch.object(overlay, 'session_label', return_value=True), \
                patch.object(overlay, 'wayland_env', return_value={'PATH': '/fixture'}), \
                patch.object(overlay, '_log'), \
                patch('indicator.Native', return_value=native):
            daemon = overlay.Daemon()
            first = daemon.apply_holders()
            second = daemon.apply_holders()
        assert first['owner'] == 'session'
        assert second['owner'] == 'daemon' and second['visible']
        assert daemon.native is native


def test_label_command_valid_chars():
    import re
    assert re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label Muse via BiDi')
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label ' + 'x' * 41)
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label bad\nline')


def test_acquire_daemon_error_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        _isolated(tmp)
        args = Namespace(agent='Browser automation', method='DOM/BiDi',
                         pid=os.getpid(), holder_id='c' * 32, label=None)
        with patch.object(overlay, '_ensure_daemon'), \
                patch.object(overlay, '_send_socket',
                             return_value={'error': 'indicator unavailable'}):
            try:
                overlay.cmd_acquire(args)
            except RuntimeError as error:
                assert 'indicator unavailable' in str(error)
            else:
                raise AssertionError('failed daemon acquire must be reported')
        assert overlay.load_holders() == {}


if __name__ == '__main__':
    test_label_format()
    test_add_release_refcount()
    test_same_agent_sessions_release_independently()
    test_holders_persist_json()
    test_prune_dead_pid()
    test_unknown_pid_permission_does_not_prune_holder()
    test_daemon_reuses_broker_indicator_for_browser_holder()
    test_daemon_owns_indicator_when_no_broker_session_exists()
    test_browser_holder_takes_over_when_broker_indicator_disappears()
    test_label_command_valid_chars()
    test_acquire_daemon_error_fails_closed()
    print('all overlay tests pass')

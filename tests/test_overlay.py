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


def test_label_command_valid_chars():
    import re
    assert re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label Muse via BiDi')
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label ' + 'x' * 41)
    assert not re.fullmatch(r'label [\x20-\x7e]{1,40}', 'label bad\nline')


if __name__ == '__main__':
    test_label_format()
    test_add_release_refcount()
    test_holders_persist_json()
    test_prune_dead_pid()
    test_label_command_valid_chars()
    print('all overlay tests pass')

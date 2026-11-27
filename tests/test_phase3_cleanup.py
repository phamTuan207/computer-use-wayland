"""Phase 3.1.8 (C8): session cleanup is VERIFIED, not assumed.

The guardian already cleans up; session_cleanup.py proves the desktop
is actually clean afterwards. Tests use a fake STATE dir and a fake
proc list, so no Wayland and no live session are needed.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import session_cleanup as sc

SCRIPT = str(Path(__file__).resolve().parents[1] / 'scripts' / 'session_cleanup.py')


def _fake_state(tmp):
    return Path(tmp) / 'state'


def test_clean_state_is_clean():
    with tempfile.TemporaryDirectory() as d:
        state = _fake_state(d)
        state.mkdir()
        assert sc.find_leftovers(state, proc_cmdlines=[]) == []


def test_each_leftover_is_found():
    with tempfile.TemporaryDirectory() as d:
        state = _fake_state(d)
        (state / 'overlay').mkdir(parents=True)
        (state / 'session.json').write_text('{"token": "x"}')
        (state / 'indicator-0123456789abcdef0123456789abcdef.sock').touch()
        (state / 'stop-abc').touch()
        (state / 'overlay' / 'holders.json').write_text(
            json.dumps({'Muse': {'method': 'BiDi', 'pid': 123}}))
        procs = [(999, 'python scripts/cursor_session.py guard 5 abc')]
        left = sc.find_leftovers(state, proc_cmdlines=procs)
        joined = '\n'.join(left)
        assert len(left) == 5, left
        assert 'snapshot' in joined
        assert 'indicator endpoint' in joined
        assert 'stop marker' in joined
        assert 'overlay holders' in joined
        assert 'guardian' in joined


def test_unrelated_processes_are_not_guardians():
    with tempfile.TemporaryDirectory() as d:
        state = _fake_state(d)
        state.mkdir()
        procs = [(1, 'python scripts/cu.py desktop_act'),
                 (2, 'python scripts/session_remote.py serve')]
        assert sc.find_leftovers(state, proc_cmdlines=procs) == []


def test_clean_prunes_dead_holders_and_orphan_markers():
    with tempfile.TemporaryDirectory() as d:
        state = _fake_state(d)
        (state / 'overlay').mkdir(parents=True)
        # pid 999999999 is not a live process: dead holder, pruned.
        (state / 'overlay' / 'holders.json').write_text(
            json.dumps({'Ghost': {'method': 'BiDi', 'pid': 999999999}}))
        (state / 'stop-orphan').touch()
        cleaned = sc.clean_safe(state)
        assert any('pruned' in line for line in cleaned), cleaned
        assert any('orphan' in line for line in cleaned), cleaned
        assert not (state / 'stop-orphan').exists()
        assert sc.find_leftovers(state, proc_cmdlines=[]) == []


def test_cli_exit_codes():
    with tempfile.TemporaryDirectory() as d:
        state = _fake_state(d)
        state.mkdir()
        # Hermetic: an empty procs file, so the ambient /proc (a
        # parallel test runner's cmdline can contain both
        # 'cursor_session' and 'guard') cannot flip the result.
        procs = Path(d) / 'procs.txt'
        procs.write_text('')
        ok = subprocess.run([sys.executable, SCRIPT, '--check',
                             '--state-dir', str(state),
                             '--procs-file', str(procs)],
                            capture_output=True, text=True,
                            env={**os.environ, 'CU_TEST_PROCS_FILE': '1'})
        assert ok.returncode == 0, ok.stdout
        (state / 'session.json').write_text('{}')
        dirty = subprocess.run([sys.executable, SCRIPT, '--check',
                                '--state-dir', str(state),
                                '--procs-file', str(procs)],
                               capture_output=True, text=True,
                               env={**os.environ, 'CU_TEST_PROCS_FILE': '1'})
        assert dirty.returncode == 1
        assert 'snapshot' in dirty.stdout
        refused = subprocess.run([sys.executable, SCRIPT, '--check',
                                  '--state-dir', str(state),
                                  '--procs-file', str(procs)],
                                 capture_output=True, text=True,
                                 env={k: v for k, v in os.environ.items()
                                      if k != 'CU_TEST_PROCS_FILE'})
        assert refused.returncode == 2
        assert 'test-only' in refused.stderr
        missing = subprocess.run([sys.executable, SCRIPT, '--check',
                                  '--state-dir', str(state),
                                  '--procs-file', str(procs) + '.missing'],
                                 capture_output=True, text=True,
                                 env={**os.environ, 'CU_TEST_PROCS_FILE': '1'})
        assert missing.returncode == 2
        assert 'cannot read procs file' in missing.stderr


def load_tests(loader, standard_tests, pattern):
    from _function_test_support import load_function_tests
    return load_function_tests(globals())

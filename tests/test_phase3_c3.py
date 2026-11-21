"""Phase 3.1.3 (C3): Ctrl+T must never open a new Zen window by mistake.

In Zen Ctrl+N is a new tab and Ctrl+T is a new window (swapped vs
Chrome). `_refuse_zen_ctrl_t` raises PreflightRefusal before any focus
or input when the target window class is zen. Non-Zen targets and failed
lookups are untouched. No Wayland needed: the window lookup is stubbed.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu

CTRL_T = [{'type': 'key', 'keys': ['ctrl', 't']}]
CTRL_N = [{'type': 'key', 'keys': ['ctrl', 'n']}]


def test_detector():
    assert cu._is_zen_ctrl_t(CTRL_T)
    assert cu._is_zen_ctrl_t([{'type': 'key', 'keys': ['Ctrl', 'T']}])
    assert not cu._is_zen_ctrl_t(CTRL_N)
    assert not cu._is_zen_ctrl_t([{'type': 'key', 'keys': ['t']}])
    assert not cu._is_zen_ctrl_t([{'type': 'type', 'text': 't'}])


def _refuse(actions, window_class):
    with mock.patch.object(cu, 'window', return_value={'class': window_class}):
        cu._refuse_zen_ctrl_t({}, '0x1234', actions, False)


def test_zen_ctrl_t_refused():
    try:
        _refuse(CTRL_T, 'zen')
    except cu.PreflightRefusal as exc:
        assert 'Ctrl+N' in str(exc), str(exc)
    else:
        raise AssertionError('Ctrl+T into Zen was not refused')


def test_non_zen_ctrl_t_allowed():
    _refuse(CTRL_T, 'code')  # VS Code go-to-symbol keeps working
    _refuse(CTRL_T, 'kitty')


def test_zen_ctrl_n_allowed():
    _refuse(CTRL_N, 'zen')


def test_screen_scope_skipped():
    with mock.patch.object(cu, 'window', side_effect=AssertionError('must not look up')):
        cu._refuse_zen_ctrl_t({}, '0x1234', CTRL_T, True)


def test_failed_lookup_fails_open():
    with mock.patch.object(cu, 'window', side_effect=RuntimeError('hypr down')):
        cu._refuse_zen_ctrl_t({}, '0x1234', CTRL_T, False)


def load_tests(loader, standard_tests, pattern):
    from _function_test_support import load_function_tests
    return load_function_tests(globals())

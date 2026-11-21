"""Phase 3.1.1 (C1): the 120s observation expiry is enforced, not just documented.

cu.py `_valid_capture_identity` (called by `validate_desktop_observation`,
which gates every desktop act) refuses an observation whose age is outside
0..120s. code_exec.py enforces the same bound. This test proves the desktop
loop refuses a stale observation instead of acting on it.

No Wayland needed: boot/compositor identity are stubbed.
"""
import sys
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu


def _meta(age_s):
    now_mono = time.monotonic()
    now_wall = time.time()
    return {
        'observation_schema': cu.OBSERVATION_SCHEMA,
        'capture_started_monotonic': now_mono - age_s,
        'capture_started_wall': now_wall - age_s,
        'created': now_wall - age_s,
        'capture_boot_id': 'boot-test',
        'capture_compositor': 'comp-test',
    }


def _check(age_s):
    meta = _meta(age_s)
    with mock.patch.object(cu, 'boot_identity', return_value='boot-test'), \
            mock.patch.object(cu, 'compositor_identity', return_value='comp-test'):
        return cu._valid_capture_identity(meta, {})


def test_fresh_observation_passes():
    age = _check(5)
    assert 0 <= age <= 120


def test_stale_observation_refused():
    try:
        _check(130)
    except ValueError as exc:
        assert '120s' in str(exc), str(exc)
    else:
        raise AssertionError('a 130s-old observation was accepted')


def test_future_observation_refused():
    try:
        _check(-5)
    except ValueError as exc:
        assert '120s' in str(exc) or 'future' in str(exc), str(exc)
    else:
        raise AssertionError('an observation from a future clock was accepted')


def test_boundary_120s_passes():
    age = _check(119)
    assert 0 <= age <= 120

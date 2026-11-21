"""Phase 3.1.2 (C2): the after-capture after a navigation click must not
show the old page.

desktop_act sleeps 80ms then takes one after-capture; a navigation click
has not loaded yet. `_settle_after_capture` re-captures once after a
navigation-candidate batch and keeps the newer frame when the hash
changed. No Wayland needed: captures are injected callables.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu


def test_navigation_candidate_detection():
    assert cu._is_navigation_candidate([{'type': 'click', 'x': 1, 'y': 2}])
    assert cu._is_navigation_candidate([{'type': 'double_click', 'x': 1, 'y': 2}])
    assert cu._is_navigation_candidate([{'type': 'key', 'keys': ['Return']}])
    assert cu._is_navigation_candidate([{'type': 'key', 'keys': ['ctrl', 'enter']}])
    assert not cu._is_navigation_candidate([{'type': 'key', 'keys': ['ctrl', 'l']}])
    assert not cu._is_navigation_candidate([{'type': 'type', 'text': 'hi'}])
    assert not cu._is_navigation_candidate([{'type': 'move', 'x': 1, 'y': 2}])
    assert not cu._is_navigation_candidate([])


def test_no_recapture_without_navigation():
    calls = []
    first = {'pixel_sha256': 'aaa'}
    after, recaptured = cu._settle_after_capture(
        lambda: calls.append(1) or {'pixel_sha256': 'bbb'},
        first, False, settle_ms=1)
    assert after is first and recaptured is False and calls == []


def test_stale_first_frame_replaced():
    first = {'pixel_sha256': 'aaa'}
    second = {'pixel_sha256': 'bbb'}
    after, recaptured = cu._settle_after_capture(
        lambda: second, first, True, settle_ms=1)
    assert after is second and recaptured is True


def test_settled_frame_kept():
    first = {'pixel_sha256': 'aaa'}
    after, recaptured = cu._settle_after_capture(
        lambda: {'pixel_sha256': 'aaa'}, first, True, settle_ms=1)
    assert after is first and recaptured is False


def test_failed_recapture_keeps_first_frame():
    first = {'pixel_sha256': 'aaa'}

    def _boom():
        raise RuntimeError('grim failed')

    after, recaptured = cu._settle_after_capture(_boom, first, True, settle_ms=1)
    assert after is first and recaptured is False

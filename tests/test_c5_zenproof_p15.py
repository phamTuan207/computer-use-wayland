"""P1.5 liveness fix (W-GECKO, COORD-CLICK-6): lease files must not
decide liveness.

The old phase 1 check aborted whenever any *.lease file existed
(prep file section 10.9: stale leases from 16:04 to 16:31 with no
live driver behind them) and its ps grep matched its own ssh
wrapper command line (measured 2026-11-22 18:11 +07: the old
pipeline returned 1 with zero live drivers). The new
assess_lane_liveness decides from ps plus relay state only, and
lease files are evidence, never a reason.

Run: python3 tests/test_c5_zenproof_p15.py
VM only. No laptop, no SSH, no Zen: all inputs are canned strings.
No em dash or en dash anywhere.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location(
    'c5_zen_delegate_run',
    ROOT / 'improvements' / 'c5-zenproof-runs' / 'c5-zen-delegate-run.py')
runmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runmod)

assess_lane_liveness = runmod.assess_lane_liveness

IDLE_PS = (
    "  PID  PPID     ELAPSED COMMAND\n"
    " 1911     1    00:57:12 /usr/bin/python3 "
    "/home/testuser/.local/share/agent-computer-use/scripts/mcp_bridge.py\n"
    " 3913     1    00:52:04 /usr/bin/python3 "
    "/home/testuser/computer-use-wayland/scripts/session_remote.py serve "
    "--socket /run/user/1000/computer-use-wayland/relay.sock\n"
    " 5010  5000       00:01 /usr/bin/zen-browser\n"
)

STALE_LEASES = [
    'c5-heldout-90.lease', 'c5-heldout-91.lease',
    's2-flip-run0.lease', 's2-flip-run1.lease',
    's2-flip-run2.lease', 's2-flip-run3.lease',
    's2-flip-run4.lease', 's2-flip-run5.lease',
    's2-flip-trivial.lease', 's2-verify.lease',
]

# Relay status as read live 2026-11-22 18:11 +07: last task finished,
# no live driver, no recovery pending.
FINISHED_RELAY = {
    'ok': True, 'broker': 'running', 'state': 'finished',
    'owner': 'w-sync', 'driver': 'stopped', 'guardian': 'clean',
    'recovery': 'none', 'cancelled': False,
}

IDLE_RELAY = {
    'ok': True, 'broker': 'running', 'state': 'idle', 'owner': None,
    'driver': 'idle', 'guardian': 'idle', 'recovery': 'none',
}


def _relay(**overrides):
    status = dict(IDLE_RELAY)
    status.update(overrides)
    return status


class TestP15Liveness(unittest.TestCase):
    def test_stale_leases_and_idle_relay_are_not_live(self):
        verdict = assess_lane_liveness(IDLE_PS, IDLE_RELAY, STALE_LEASES)
        self.assertFalse(verdict['live'], verdict)
        self.assertEqual(verdict['reasons'], [])
        self.assertEqual(verdict['leases'], STALE_LEASES)

    def test_finished_relay_with_cleanup_error_is_not_live(self):
        verdict = assess_lane_liveness(IDLE_PS, FINISHED_RELAY,
                                       STALE_LEASES)
        self.assertFalse(verdict['live'], verdict)

    def test_session_driver_process_is_live(self):
        ps = IDLE_PS + (
            " 6010  3913       00:00 /usr/bin/python3 "
            "/home/testuser/computer-use-wayland/scripts/cu.py "
            "session-driver\n")
        verdict = assess_lane_liveness(ps, IDLE_RELAY, [])
        self.assertTrue(verdict['live'])
        self.assertTrue(any('session-driver' in r
                            for r in verdict['reasons']), verdict)

    def test_session_wrapper_spawning_driver_is_live(self):
        ps = IDLE_PS + (
            " 6011  3913       00:00 /usr/bin/python3 "
            "/home/testuser/computer-use-wayland/scripts/cu.py session "
            "-- python3 /home/testuser/computer-use-wayland/scripts/cu.py "
            "session-driver\n")
        verdict = assess_lane_liveness(ps, IDLE_RELAY, [])
        self.assertTrue(verdict['live'])

    def test_relay_request_client_is_live(self):
        ps = IDLE_PS + (
            " 6012  6011       00:00 /usr/bin/python3 "
            "/home/testuser/computer-use-wayland/scripts/session_remote.py "
            "request --lease-file /home/testuser/.cache/agent-computer-use/"
            "s2-flip-run1.lease --sequence 3 --request /tmp/x.json\n")
        verdict = assess_lane_liveness(ps, IDLE_RELAY, [])
        self.assertTrue(verdict['live'])

    def test_relay_serve_daemon_is_not_live(self):
        verdict = assess_lane_liveness(IDLE_PS, IDLE_RELAY, [])
        self.assertFalse(verdict['live'], verdict)
        self.assertEqual(verdict['drivers'], [])

    def test_relay_status_probe_is_not_live(self):
        ps = IDLE_PS + (
            " 6013  6011       00:00 /usr/bin/python3 "
            "/home/testuser/computer-use-wayland/scripts/session_remote.py "
            "status\n")
        verdict = assess_lane_liveness(ps, IDLE_RELAY, [])
        self.assertFalse(verdict['live'], verdict)

    def test_running_relay_is_live(self):
        verdict = assess_lane_liveness(
            IDLE_PS, _relay(state='running', owner='c5-zenproof',
                            driver='running'),
            STALE_LEASES)
        self.assertTrue(verdict['live'])
        self.assertTrue(any('running' in r
                            for r in verdict['reasons']), verdict)

    def test_relay_recovery_required_is_live(self):
        verdict = assess_lane_liveness(
            IDLE_PS, _relay(state='finished', recovery='required'), [])
        self.assertTrue(verdict['live'])

    def test_guardian_active_is_live(self):
        verdict = assess_lane_liveness(
            IDLE_PS, _relay(state='running', guardian='active'), [])
        self.assertTrue(verdict['live'])

    def test_relay_unavailable_fails_closed(self):
        verdict = assess_lane_liveness(IDLE_PS, None, STALE_LEASES)
        self.assertTrue(verdict['live'])
        self.assertTrue(any('unavailable' in r
                            for r in verdict['reasons']), verdict)

    def test_old_grep_wrapper_self_match_is_not_live(self):
        # The old check's false positive, verbatim shape: the ssh
        # wrapper command line contains the grep pattern as a literal
        # argument, which the old grep matched. Token-exact matching
        # must not count it.
        ps = IDLE_PS + (
            " 6020  6019       00:00 bash -c ps aux | grep -E "
            "'session-driver|session_remote' | grep -v grep | wc -l\n")
        verdict = assess_lane_liveness(ps, IDLE_RELAY, [])
        self.assertFalse(verdict['live'], verdict)

    def test_lease_names_recorded_as_evidence(self):
        verdict = assess_lane_liveness(IDLE_PS, IDLE_RELAY, STALE_LEASES)
        self.assertEqual(len(verdict['leases']), 10)
        self.assertIn('s2-flip-run1.lease', verdict['leases'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""S2 flip pill-hold tests (W-PILLCDP).

The harness holds the overlay pill on the laptop around every
browser-control step (send, scratch-tab seed, scratch-tab close).
SSH is faked: no laptop, no browser, no network.
"""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))

SPEC = importlib.util.spec_from_file_location(
    's2_flip_live', str(pathlib.Path(__file__).resolve().parents[1]
                        / 'scripts' / 's2_flip_live.py'))
s2_flip_live = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s2_flip_live)


class FakeHarness(s2_flip_live.Harness):
    """Harness with SSH faked: records commands, answers canned rc."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = []
        self.acquire_rc = 0

    def ssh(self, remote_cmd, label, timeout=120, input_text=None):
        self.commands.append((label, remote_cmd))
        if label == 'pill-acquire':
            return self.acquire_rc, ('{"visible": true}\n'
                                     'PILL_SLEEP_PID=4242'), '', 1.0
        return 0, '{}', '', 1.0


class PillHoldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.harness = FakeHarness(self.tmp.name, 1)

    def test_hold_acquires_then_releases_in_order(self):
        with self.harness.cdp_pill_hold() as held:
            self.assertTrue(held)
            mid = list(self.harness.commands)
        self.assertEqual(
            [label for label, _ in self.harness.commands],
            ['pill-acquire', 'pill-release'])
        self.assertIn('overlay.py acquire', mid[0][1])
        self.assertIn('--agent S2-flip', mid[0][1])
        self.assertIn('--method CDP', mid[0][1])
        self.assertIn('overlay.py release',
                      self.harness.commands[1][1])
        self.assertIn('--agent S2-flip',
                      self.harness.commands[1][1])

    def test_acquire_keys_holder_by_laptop_sleeper_pid(self):
        """H1: the acquire starts a laptop sleeper and passes its pid,
        so this run's holder key is S2-flip:<sleeper pid>, never the
        bare key shared by pid-less runs. The release passes the same
        pid (parsed from PILL_SLEEP_PID=) and kills the sleeper."""
        with self.harness.cdp_pill_hold() as held:
            self.assertTrue(held)
        acquire_cmd, release_cmd = [cmd for _, cmd in self.harness.commands]
        self.assertIn('nohup sleep 600', acquire_cmd)
        self.assertIn('--pid $SLEEP_PID', acquire_cmd)
        self.assertIn('PILL_SLEEP_PID=$SLEEP_PID', acquire_cmd)
        self.assertIn('--pid 4242', release_cmd)
        self.assertIn('kill 4242', release_cmd)

    def test_release_falls_back_pid_less_without_parsed_pid(self):
        """When the acquire output carries no PILL_SLEEP_PID, the
        release falls back to pid-less (it cannot remove the
        pid-keyed holder; the daemon prunes it when the sleeper
        expires). The hold must not crash on the missing pid."""
        self.harness.acquire_rc = 0

        def ssh_no_pid(remote_cmd, label, timeout=120, input_text=None):
            self.harness.commands.append((label, remote_cmd))
            if label == 'pill-acquire':
                return 0, '{"visible": true}', '', 1.0
            return 0, '{}', '', 1.0

        self.harness.ssh = ssh_no_pid
        with self.harness.cdp_pill_hold() as held:
            self.assertTrue(held)
        self.assertEqual(self.harness.commands[1][1],
                         self.harness.pill_release_cmd())
        self.assertNotIn('--pid', self.harness.commands[1][1])

    def test_failed_acquire_still_runs_body_and_skips_release(self):
        self.harness.acquire_rc = 1
        ran = []
        with self.harness.cdp_pill_hold() as held:
            self.assertFalse(held)
            ran.append(True)
        self.assertEqual(ran, [True], 'body must run even when acquire fails')
        self.assertEqual(
            [label for label, _ in self.harness.commands],
            ['pill-acquire'],
            'no release when nothing was held')

    def test_send_browser_holds_pill_around_send(self):
        calls = []

        def fake_oneshot(endpoint, program, intent):
            calls.append('send')
            return 12.0, {'ok': True, 'api_calls': 3, 'elapsed_ms': 12.0,
                          'log': []}

        def fake_v12(endpoint, target_id, message):
            calls.append('v12')
            return {'found': True, 'ms': 5.0}

        self.harness.oneshot_code_exec = fake_oneshot
        self.harness.v12_check = fake_v12
        out = self.harness.send_browser('chromium', 'test-tab',
                                        'S2-FLIP-R1-CHROMIUM-IGNORE-TEST')
        self.assertEqual(out['outcome'], 'sent')
        self.assertEqual(calls, ['send', 'v12'])
        self.assertEqual(
            [label for label, _ in self.harness.commands],
            ['pill-acquire', 'pill-release'],
            'pill brackets the whole send, acquire first, release last')
        self.assertEqual(self.harness.commands[0][1],
                         self.harness.pill_acquire_cmd())
        self.assertEqual(self.harness.commands[1][1],
                         self.harness.pill_release_cmd(4242))


if __name__ == '__main__':
    unittest.main()

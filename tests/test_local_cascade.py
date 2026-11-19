"""Tests for scripts/local_cascade.py (local small-model cascade, Rank 1 / M4).

Run from the repo root: python3 -m unittest tests.test_local_cascade
No broker, no desktop, no model calls. All model answers come from a
fake transport injected into the step functions.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import local_cascade as lc  # noqa: E402


CLIENTS = [
    {'address': '0x1001', 'class': 'kitty', 'title': 'speed-profile-term',
     'workspace': {'name': '1'}, 'focused': True},
    {'address': '0x1002', 'class': 'zen', 'title': 'Inbox - Gmail',
     'workspace': {'name': '2'}, 'focused': False},
    {'address': '0x1003', 'class': 'code', 'title': 'computer-use-wayland',
     'workspace': {'name': '1'}, 'focused': False},
]

OBS_DF = (
    "Filesystem      Size  Used Avail Use% Mounted on\n"
    "/dev/mapper/omarchy_root  385G  366G   18G  96% /\n"
)

OBS_DU = (
    "1.7G\t/tmp/pill-video\n"
    "148M\t/tmp/pick3-gate\n"
    "103M\t/tmp/zen-bidi-test\n"
)


def _transport(answer):
    def run(prompt, schema):
        return dict(answer)
    return run


def _failing_transport(message):
    def run(prompt, schema):
        raise RuntimeError(message)
    return run


class FlagTests(unittest.TestCase):
    def test_default_off(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(lc.enabled())

    def test_only_exact_1_enables(self):
        for value in ("0", "true", "yes", ""):
            with mock.patch.dict(os.environ, {lc.FLAG_ENV: value}, clear=True):
                self.assertFalse(lc.enabled(), value)
        with mock.patch.dict(os.environ, {lc.FLAG_ENV: "1"}, clear=True):
            self.assertTrue(lc.enabled())


class PromptTests(unittest.TestCase):
    def test_windows_prompt_lists_addresses_and_goal(self):
        prompt = lc.build_windows_prompt(CLIENTS, 'the terminal')
        for client in CLIENTS:
            self.assertIn(client['address'], prompt)
        self.assertIn('the terminal', prompt)

    def test_windows_prompt_empty_list(self):
        prompt = lc.build_windows_prompt([], 'the terminal')
        self.assertIn('(no windows)', prompt)

    def test_verify_prompt_truncates_long_observation(self):
        prompt = lc.build_verify_prompt('x' * 10000, 'cond')
        self.assertLess(len(prompt), 10000)
        self.assertIn('cond', prompt)


class WindowsValidationTests(unittest.TestCase):
    def test_known_address_passes(self):
        ok, _ = lc.validate_window_choice(
            {'address': '0x1001', 'confidence': 0.9}, CLIENTS)
        self.assertTrue(ok)

    def test_unknown_address_escalates(self):
        ok, reason = lc.validate_window_choice(
            {'address': '0x9999', 'confidence': 0.95}, CLIENTS)
        self.assertFalse(ok)
        self.assertIn('not in window list', reason)

    def test_null_address_passes_when_confident(self):
        ok, _ = lc.validate_window_choice(
            {'address': None, 'confidence': 0.8}, CLIENTS)
        self.assertTrue(ok)

    def test_low_confidence_escalates(self):
        ok, reason = lc.validate_window_choice(
            {'address': '0x1001', 'confidence': 0.69}, CLIENTS)
        self.assertFalse(ok)
        self.assertIn('below', reason)

    def test_boundary_confidence_passes(self):
        ok, _ = lc.validate_window_choice(
            {'address': '0x1001', 'confidence': 0.70}, CLIENTS)
        self.assertTrue(ok)

    def test_missing_confidence_escalates(self):
        ok, _ = lc.validate_window_choice({'address': '0x1001'}, CLIENTS)
        self.assertFalse(ok)

    def test_confidence_one_point_zero_wrong_address_still_escalates(self):
        # Pick 2 lesson: confidence 1.0 does not save a wrong answer.
        # The postcondition, not the confidence, catches it.
        ok, _ = lc.validate_window_choice(
            {'address': '0x9999', 'confidence': 1.0}, CLIENTS)
        self.assertFalse(ok)


class VerifyValidationTests(unittest.TestCase):
    def test_pass_with_verbatim_evidence_passes(self):
        ok, _ = lc.validate_verify(
            {'pass': True, 'evidence': '385G  366G   18G  96% /',
             'confidence': 0.9}, OBS_DF)
        self.assertTrue(ok)

    def test_pass_without_evidence_escalates(self):
        ok, reason = lc.validate_verify(
            {'pass': True, 'evidence': '', 'confidence': 0.9}, OBS_DF)
        self.assertFalse(ok)
        self.assertIn('without evidence', reason)

    def test_hallucinated_evidence_escalates(self):
        ok, reason = lc.validate_verify(
            {'pass': True, 'evidence': 'Avail 500G', 'confidence': 0.95},
            OBS_DF)
        self.assertFalse(ok)
        self.assertIn('not verbatim', reason)

    def test_fail_with_counter_evidence_passes(self):
        ok, _ = lc.validate_verify(
            {'pass': False, 'evidence': '1.7G\t/tmp/pill-video',
             'confidence': 0.85}, OBS_DU)
        self.assertTrue(ok)

    def test_non_boolean_pass_escalates(self):
        ok, _ = lc.validate_verify(
            {'pass': 'yes', 'evidence': '385G', 'confidence': 0.9}, OBS_DF)
        self.assertFalse(ok)

    def test_whitespace_normalised_match(self):
        ok, _ = lc.validate_verify(
            {'pass': True, 'evidence': '385G 366G 18G 96% /',
             'confidence': 0.9}, OBS_DF)
        self.assertTrue(ok)


class StepTests(unittest.TestCase):
    def test_pick_window_happy_path(self):
        out = lc.pick_window(
            CLIENTS, 'the terminal',
            transport=_transport({'address': '0x1001', 'confidence': 0.9}))
        self.assertFalse(out['escalate'])
        self.assertEqual(out['address'], '0x1001')
        self.assertEqual(out['step'], 'windows')
        self.assertIn('latency_ms', out)

    def test_pick_window_wrong_answer_escalates(self):
        out = lc.pick_window(
            CLIENTS, 'the terminal',
            transport=_transport({'address': '0x1002', 'confidence': 1.0}))
        # 0x1002 IS in the list, so the postcondition cannot catch a
        # wrong-but-listed pick. The confidence rule cannot either.
        # This documents the residual risk: listed-but-wrong picks need
        # the downstream focus check, same as a Luna pick.
        self.assertFalse(out['escalate'])
        self.assertEqual(out['address'], '0x1002')

    def test_pick_window_unknown_address_escalates(self):
        out = lc.pick_window(
            CLIENTS, 'the terminal',
            transport=_transport({'address': '0x9999', 'confidence': 1.0}))
        self.assertTrue(out['escalate'])
        self.assertIn('not in window list', out['reason'])

    def test_pick_window_transport_failure_escalates(self):
        out = lc.pick_window(
            CLIENTS, 'the terminal',
            transport=_failing_transport('server down'))
        self.assertTrue(out['escalate'])
        self.assertIn('server down', out['reason'])

    def test_verify_happy_path(self):
        out = lc.verify_condition(
            OBS_DF, 'root has at least 10G free',
            transport=_transport({
                'pass': True, 'evidence': '385G  366G   18G  96% /',
                'confidence': 0.9}))
        self.assertFalse(out['escalate'])
        self.assertTrue(out['pass'])

    def test_verify_bad_json_escalates(self):
        def bad(prompt, schema):
            return ['not', 'a', 'dict']
        out = lc.verify_condition(OBS_DF, 'cond', transport=bad)
        self.assertTrue(out['escalate'])

    def test_finish_happy_path(self):
        out = lc.confirm_finish(
            'y-tuong.txt has 3 lines\n', 'write 3 lines to y-tuong.txt',
            transport=_transport({
                'pass': True, 'evidence': 'y-tuong.txt has 3 lines',
                'confidence': 0.88}))
        self.assertFalse(out['escalate'])
        self.assertTrue(out['pass'])


class CliTests(unittest.TestCase):
    def test_cli_disabled_flag_escalates(self):
        env = dict(os.environ)
        env.pop(lc.FLAG_ENV, None)
        with tempfile.TemporaryDirectory() as tmp:
            clients = Path(tmp) / 'clients.json'
            clients.write_text(json.dumps(CLIENTS), encoding='utf-8')
            proc = subprocess.run(
                [sys.executable, 'scripts/local_cascade.py', 'windows',
                 '--clients', str(clients), '--goal', 'the terminal'],
                capture_output=True, text=True, cwd=Path(__file__).parents[1],
                env=env)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertTrue(out['escalate'])

    def test_cli_health_unreachable_server_reports_not_ok(self):
        env = dict(os.environ)
        env[lc.FLAG_ENV] = '1'
        env[lc.SERVER_ENV] = 'http://127.0.0.1:59999'
        proc = subprocess.run(
            [sys.executable, 'scripts/local_cascade.py', 'health'],
            capture_output=True, text=True, cwd=Path(__file__).parents[1],
            env=env)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])


if __name__ == '__main__':
    unittest.main()

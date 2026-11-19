"""Tests for Pick 2 subgoal-only verification plus the reasoning dial.

Pure policy, no desktop, no broker, no model calls.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import subgoal_policy as sp


class FlagTests(unittest.TestCase):
    def test_default_off(self):
        env = {key: value for key, value in os.environ.items()
               if key != sp.PICK2_ENV_VAR}
        self.assertFalse(sp.pick2_enabled(env))

    def test_truthy_values_on(self):
        for value in ('1', 'true', 'yes', 'on', 'TRUE', ' Yes '):
            self.assertTrue(sp.pick2_enabled({sp.PICK2_ENV_VAR: value}), value)

    def test_falsy_values_off(self):
        for value in ('0', 'false', 'no', '', 'maybe'):
            self.assertFalse(sp.pick2_enabled({sp.PICK2_ENV_VAR: value}), value)


class EffortDialTests(unittest.TestCase):
    def test_level_efforts(self):
        self.assertIsNone(sp.effort_for_level(sp.LEVEL_DETERMINISTIC))
        self.assertEqual(sp.effort_for_level(sp.LEVEL_ROUTINE), 'low')
        self.assertEqual(sp.effort_for_level(sp.LEVEL_AMBIGUOUS), 'max')

    def test_unknown_level_raises(self):
        with self.assertRaises(ValueError):
            sp.effort_for_level(4)

    def test_level1_needs_no_codex_call(self):
        self.assertEqual(sp.codex_args_for_level(sp.LEVEL_DETERMINISTIC), [])

    def test_level2_args_carry_low_effort_and_schema(self):
        args = sp.codex_args_for_level(sp.LEVEL_ROUTINE)
        self.assertIn('-c', args)
        self.assertIn('model_reasoning_effort="low"', args)
        self.assertIn('--output-schema', args)
        schema = args[args.index('--output-schema') + 1]
        self.assertTrue(Path(schema).is_file())

    def test_level3_args_carry_max_effort_and_no_schema(self):
        args = sp.codex_args_for_level(sp.LEVEL_AMBIGUOUS)
        self.assertIn('model_reasoning_effort="max"', args)
        self.assertNotIn('--output-schema', args)

    def test_l2_schema_file_matches_module_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = sp.write_l2_schema(Path(tmp) / 'schema.json')
            self.assertEqual(oct(os.stat(path).st_mode & 0o777), '0o600')
            self.assertEqual(json.loads(path.read_text()),
                             sp.L2_DECISION_SCHEMA)


class L2DecisionTests(unittest.TestCase):
    def test_valid_decision_passes(self):
        ok, reason = sp.validate_l2_decision(
            {'action': 'click', 'target': 'save_button', 'confidence': 0.9})
        self.assertTrue(ok)
        self.assertIsNone(reason)

    def test_missing_key_fails_closed(self):
        ok, _ = sp.validate_l2_decision({'action': 'click', 'target': 'x'})
        self.assertFalse(ok)

    def test_extra_key_fails_closed(self):
        ok, _ = sp.validate_l2_decision(
            {'action': 'click', 'target': 'x', 'confidence': 0.9, 'note': 'hi'})
        self.assertFalse(ok)

    def test_confidence_out_of_range_fails(self):
        for bad in (-0.1, 1.5, 'high', True, None):
            ok, _ = sp.validate_l2_decision(
                {'action': 'click', 'target': 'x', 'confidence': bad})
            self.assertFalse(ok, bad)

    def test_irreversible_action_never_level2(self):
        for action in ('delete', 'send', 'shutdown', 'push', 'submit'):
            ok, reason = sp.validate_l2_decision(
                {'action': action, 'target': 'x', 'confidence': 0.99})
            self.assertFalse(ok, action)
            self.assertIn('irreversible', reason)

    def test_non_object_fails(self):
        for bad in (None, 'click', ['click'], 42):
            ok, _ = sp.validate_l2_decision(bad)
            self.assertFalse(ok, bad)


class ClassifyTests(unittest.TestCase):
    def test_procedure_step_with_check_is_level1(self):
        self.assertEqual(sp.classify_decision(
            is_procedure_step=True, is_irreversible=False, is_ambiguous=False,
            has_postcondition_check=True), sp.LEVEL_DETERMINISTIC)

    def test_routine_with_check_is_level2(self):
        self.assertEqual(sp.classify_decision(
            is_procedure_step=False, is_irreversible=False, is_ambiguous=False,
            has_postcondition_check=True), sp.LEVEL_ROUTINE)

    def test_routine_without_check_escalates_to_level3(self):
        self.assertEqual(sp.classify_decision(
            is_procedure_step=False, is_irreversible=False, is_ambiguous=False,
            has_postcondition_check=False), sp.LEVEL_AMBIGUOUS)

    def test_ambiguous_is_level3(self):
        self.assertEqual(sp.classify_decision(
            is_procedure_step=True, is_irreversible=False, is_ambiguous=True,
            has_postcondition_check=True), sp.LEVEL_AMBIGUOUS)

    def test_irreversible_is_level3_even_when_routine(self):
        self.assertEqual(sp.classify_decision(
            is_procedure_step=False, is_irreversible=True, is_ambiguous=False,
            has_postcondition_check=True), sp.LEVEL_AMBIGUOUS)


class JudgeRuleTests(unittest.TestCase):
    def test_judge_inside_subgoal_forbidden(self):
        self.assertFalse(sp.judge_allowed(at_subgoal_boundary=False))

    def test_judge_at_boundary_allowed(self):
        self.assertTrue(sp.judge_allowed(at_subgoal_boundary=True))

    def test_plan_with_mid_step_judge_fails(self):
        plan = {'steps': [
            {'id': 'S1', 'calls': ['act']},
            {'id': 'S2', 'calls': ['judge']},
        ]}
        with self.assertRaises(ValueError):
            sp.validate_plan_has_no_mid_step_judge(plan)

    def test_plan_with_boundary_judge_passes(self):
        plan = {'steps': [
            {'id': 'S1', 'calls': ['act']},
            {'id': 'S2', 'calls': ['judge'], 'subgoal_boundary': True},
        ]}
        self.assertTrue(sp.validate_plan_has_no_mid_step_judge(plan))

    def test_plan_without_judge_passes(self):
        plan = {'steps': [{'id': 'S1', 'calls': ['act', 'observe']}]}
        self.assertTrue(sp.validate_plan_has_no_mid_step_judge(plan))


class HistoryMaskingTests(unittest.TestCase):
    def test_short_history_unmasked(self):
        obs = [{'id': 'a'}, {'id': 'b'}]
        full, lines = sp.mask_history(obs)
        self.assertEqual(full, obs)
        self.assertEqual(lines, [])

    def test_long_history_keeps_last_two_full(self):
        obs = [{'id': f'o{i}', 'label': f'o{i}'} for i in range(5)]
        full, lines = sp.mask_history(obs)
        self.assertEqual([item['id'] for item in full], ['o3', 'o4'])
        self.assertEqual(len(lines), 3)
        self.assertTrue(all('o0' in lines[0] or 'obs' in lines[0] for _ in [0]))
        self.assertIn('o0', lines[0])

    def test_keep_full_zero_masks_everything(self):
        obs = [{'id': 'a'}]
        full, lines = sp.mask_history(obs, keep_full=0)
        self.assertEqual(full, [])
        self.assertEqual(len(lines), 1)

    def test_negative_keep_full_raises(self):
        with self.assertRaises(ValueError):
            sp.mask_history([{'id': 'a'}], keep_full=-1)

    def test_text_line_carries_summary(self):
        line = sp.text_history_line(
            {'id': 'o1', 'label': 'verify', 'text_summary': 'dirs exist'})
        self.assertIn('verify', line)
        self.assertIn('dirs exist', line)


class SubgoalVerificationTests(unittest.TestCase):
    def test_all_checks_pass(self):
        passed, failed, _ = sp.verify_subgoal([
            ('file_bytes', True, '50 bytes'),
            ('window_class', True, 'kitty'),
        ])
        self.assertTrue(passed)
        self.assertEqual(failed, [])

    def test_one_failure_fails_subgoal(self):
        passed, failed, details = sp.verify_subgoal([
            ('file_bytes', True, '50 bytes'),
            ('file_sha', False, 'sha mismatch'),
        ])
        self.assertFalse(passed)
        self.assertEqual(failed, ['file_sha'])
        self.assertEqual(details['file_sha'], 'sha mismatch')

    def test_escalation_triggers(self):
        self.assertTrue(sp.should_escalate(
            postcondition_passed=False, is_ambiguous=False,
            needs_new_procedure=False))
        self.assertTrue(sp.should_escalate(
            postcondition_passed=True, is_ambiguous=True,
            needs_new_procedure=False))
        self.assertTrue(sp.should_escalate(
            postcondition_passed=True, is_ambiguous=False,
            needs_new_procedure=True))
        self.assertFalse(sp.should_escalate(
            postcondition_passed=True, is_ambiguous=False,
            needs_new_procedure=False))


class QuarantineTests(unittest.TestCase):
    def test_two_consecutive_failures_quarantine(self):
        tracker = sp.QuarantineTracker()
        self.assertFalse(tracker.record('tc02-v1', passed=False))
        self.assertTrue(tracker.record('tc02-v1', passed=False))
        self.assertTrue(tracker.is_quarantined('tc02-v1'))
        self.assertEqual(tracker.consecutive_failures('tc02-v1'), 2)

    def test_pass_resets_count(self):
        tracker = sp.QuarantineTracker()
        tracker.record('tc02-v1', passed=False)
        tracker.record('tc02-v1', passed=True)
        self.assertEqual(tracker.consecutive_failures('tc02-v1'), 0)
        self.assertFalse(tracker.is_quarantined('tc02-v1'))

    def test_other_procedure_unaffected(self):
        tracker = sp.QuarantineTracker()
        tracker.record('tc02-v1', passed=False)
        tracker.record('tc02-v1', passed=False)
        self.assertFalse(tracker.is_quarantined('other'))


class DetectionLagTests(unittest.TestCase):
    def test_lag_counts_actions_before_detection(self):
        tracker = sp.DetectionLagTracker()
        tracker.record_action()
        tracker.record_action()
        tracker.record_action()
        self.assertEqual(tracker.record_bad_action_detected(), 3)

    def test_subgoal_boundary_resets_count(self):
        tracker = sp.DetectionLagTracker()
        tracker.record_action()
        tracker.record_subgoal_boundary()
        tracker.record_action()
        self.assertEqual(tracker.record_bad_action_detected(), 1)


if __name__ == '__main__':
    unittest.main()

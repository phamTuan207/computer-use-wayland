"""Tests for the observation-masking prototype (Pick 5).

Pure policy, no desktop, no broker, no model calls.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import mask_history as mh


def _turn(n, image=None, description=None, reasoning=None, action=None):
    observation = {}
    if image is not None:
        observation['image'] = image
    if description is not None:
        observation['description'] = description
    observation['window'] = '0x1000%d' % n
    return {
        'n': n,
        'label': 'obs%d' % n,
        'observation': observation,
        'reasoning': reasoning or ('decided step %d' % n),
        'action': action or ('ran command %d' % n),
    }


def _history(count=5):
    return [_turn(n, image='/tmp/obs%d.png' % n,
                  description='terminal showing step %d output' % n)
            for n in range(1, count + 1)]


class FlagTests(unittest.TestCase):
    def test_default_off(self):
        env = {key: value for key, value in os.environ.items()
               if key != mh.MASK_ENV_VAR}
        self.assertFalse(mh.mask_enabled(env))

    def test_truthy_values_on(self):
        for value in ('1', 'true', 'yes', 'on', 'TRUE', ' Yes '):
            self.assertTrue(mh.mask_enabled({mh.MASK_ENV_VAR: value}), value)

    def test_falsy_values_off(self):
        for value in ('0', 'false', 'no', 'off', '', 'maybe'):
            self.assertFalse(mh.mask_enabled({mh.MASK_ENV_VAR: value}), value)

    def test_default_keep_is_two(self):
        self.assertEqual(mh.MAX_FULL_SCREENSHOTS, 2)


class MaskLineTests(unittest.TestCase):
    def test_format_with_description(self):
        line = mh.mask_line({'description': 'terminal showing df output'},
                            n=3)
        self.assertEqual(line, '[screenshot 3 masked: terminal showing df output]')

    def test_number_from_turn_label(self):
        line = mh.mask_line({'description': 'windows list'}, label='obs4')
        self.assertTrue(line.startswith('[screenshot 4 masked: '), line)

    def test_fallback_without_description(self):
        line = mh.mask_line({'window': '0x1a2b', 'label': 'obs2'}, n=2)
        self.assertEqual(line, '[screenshot 2 masked: observation obs2, window 0x1a2b]')

    def test_fallback_with_nothing_recorded(self):
        line = mh.mask_line({}, n=1)
        self.assertEqual(line, '[screenshot 1 masked: (no description recorded)]')

    def test_single_line_and_capped(self):
        line = mh.mask_line({'description': 'a\nb\n' + 'x' * 500}, n=1)
        self.assertNotIn('\n', line)
        self.assertLessEqual(len(line), len('[screenshot 1 masked: ]')
                             + mh.MASK_LINE_MAX_CHARS + 3)

    def test_never_invents_content(self):
        # No description recorded: the line must say so, not guess.
        line = mh.mask_line({'image': '/tmp/obs9.png'}, n=9)
        self.assertNotIn('terminal', line)
        self.assertIn('(no description recorded)', line)


class MaskTurnsTests(unittest.TestCase):
    def test_old_screenshots_replaced_latest_kept(self):
        turns = _history(5)
        masked = mh.mask_turns(turns, keep_full=2)
        for turn in masked[:3]:
            self.assertIsNone(turn['observation']['image'])
            self.assertTrue(turn['observation']['masked'])
            self.assertIn('[screenshot', turn['observation']['mask_line'])
        for turn in masked[3:]:
            self.assertEqual(turn['observation']['image'],
                             '/tmp/obs%d.png' % turn['n'])
            self.assertNotIn('masked', turn['observation'])

    def test_mask_line_text_format(self):
        turns = _history(3)
        masked = mh.mask_turns(turns, keep_full=2)
        self.assertEqual(
            masked[0]['observation']['mask_line'],
            '[screenshot 1 masked: terminal showing step 1 output]')

    def test_reasoning_and_actions_kept_in_full(self):
        turns = _history(4)
        masked = mh.mask_turns(turns, keep_full=2)
        for before, after in zip(turns, masked):
            self.assertEqual(after['reasoning'], before['reasoning'])
            self.assertEqual(after['action'], before['action'])

    def test_input_never_mutated(self):
        turns = _history(5)
        snapshot = copy.deepcopy(turns)
        mh.mask_turns(turns, keep_full=2)
        self.assertEqual(turns, snapshot)

    def test_fewer_turns_than_keep_nothing_masked(self):
        turns = _history(2)
        masked = mh.mask_turns(turns, keep_full=2)
        self.assertEqual(masked, turns)
        self.assertEqual(mh.count_images(masked), 2)

    def test_keep_zero_masks_all_history(self):
        turns = _history(3)
        masked = mh.mask_turns(turns, keep_full=0)
        self.assertEqual(mh.count_images(masked), 0)
        for turn in masked:
            self.assertTrue(turn['observation']['masked'])

    def test_negative_keep_rejected(self):
        with self.assertRaises(ValueError):
            mh.mask_turns(_history(2), keep_full=-1)

    def test_empty_history(self):
        self.assertEqual(mh.mask_turns([], keep_full=2), [])
        self.assertEqual(mh.count_images([]), 0)


class ApplyMaskTests(unittest.TestCase):
    def test_flag_off_returns_input_unchanged(self):
        turns = _history(5)
        out = mh.apply_mask(turns, env={mh.MASK_ENV_VAR: '0'})
        self.assertIs(out, turns)
        self.assertEqual(mh.count_images(out), 5)

    def test_flag_off_default_env(self):
        turns = _history(5)
        env = {key: value for key, value in os.environ.items()
               if key != mh.MASK_ENV_VAR}
        out = mh.apply_mask(turns, env=env)
        self.assertIs(out, turns)

    def test_flag_on_masks(self):
        turns = _history(5)
        out = mh.apply_mask(turns, env={mh.MASK_ENV_VAR: '1'})
        self.assertEqual(mh.count_images(out), 2)
        self.assertIsNot(out, turns)


class ThinkPromptTests(unittest.TestCase):
    def _current(self):
        return {'image': '/tmp/obs6.png',
                'description': 'terminal showing verify output',
                'window': '0x10006'}

    def test_cap_respected_at_most_two_images(self):
        result = mh.build_think_prompt(
            _history(5), self._current(),
            env={mh.MASK_ENV_VAR: '1'}, keep_full=2)
        self.assertEqual(len(result['image_paths']), 2)
        self.assertEqual(result['kept_count'], 2)

    def test_current_observation_always_fresh_pixels(self):
        result = mh.build_think_prompt(
            _history(5), self._current(),
            env={mh.MASK_ENV_VAR: '1'}, keep_full=2)
        self.assertEqual(result['image_paths'][-1], '/tmp/obs6.png')
        self.assertIn('/tmp/obs6.png', result['prompt_text'])

    def test_latest_history_image_kept_older_masked(self):
        result = mh.build_think_prompt(
            _history(5), self._current(),
            env={mh.MASK_ENV_VAR: '1'}, keep_full=2)
        self.assertEqual(result['image_paths'][0], '/tmp/obs5.png')
        self.assertEqual(result['masked_count'], 4)
        for n in (1, 2, 3, 4):
            self.assertIn('[screenshot %d masked: terminal showing step %d output]'
                          % (n, n), result['prompt_text'])
        for n in (1, 2, 3, 4):
            self.assertNotIn('/tmp/obs%d.png' % n, result['prompt_text'])

    def test_reasoning_and_actions_in_prompt_in_full(self):
        result = mh.build_think_prompt(
            _history(3), self._current(),
            env={mh.MASK_ENV_VAR: '1'}, keep_full=2)
        for n in (1, 2, 3):
            self.assertIn('decided step %d' % n, result['prompt_text'])
            self.assertIn('ran command %d' % n, result['prompt_text'])

    def test_keep_zero_still_keeps_current(self):
        result = mh.build_think_prompt(
            _history(3), self._current(),
            env={mh.MASK_ENV_VAR: '1'}, keep_full=0)
        self.assertEqual(result['image_paths'], ['/tmp/obs6.png'])
        self.assertEqual(result['masked_count'], 3)

    def test_flag_off_all_images_stay(self):
        result = mh.build_think_prompt(
            _history(3), self._current(),
            env={mh.MASK_ENV_VAR: '0'}, keep_full=2)
        self.assertEqual(result['image_paths'],
                         ['/tmp/obs1.png', '/tmp/obs2.png',
                          '/tmp/obs3.png', '/tmp/obs6.png'])
        self.assertEqual(result['masked_count'], 0)

    def test_no_current_image_uses_history_cap(self):
        result = mh.build_think_prompt(
            _history(5), {},
            env={mh.MASK_ENV_VAR: '1'}, keep_full=2)
        self.assertEqual(result['image_paths'], ['/tmp/obs5.png'])
        self.assertEqual(result['masked_count'], 4)


class CliTests(unittest.TestCase):
    def _run_cli(self, args, env_extra=None):
        env = dict(os.environ)
        env.pop(mh.MASK_ENV_VAR, None)
        env.update(env_extra or {})
        proc = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'mask_history.py'), *args],
            capture_output=True, text=True, env=env, timeout=30)
        return proc

    def test_cli_mask_flag_on_and_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / 'history.json'
            history.write_text(json.dumps(_history(5)), encoding='utf-8')
            out = Path(tmp) / 'masked.json'
            proc = self._run_cli(['mask', '--history', str(history),
                                  '--out', str(out)],
                                 {mh.MASK_ENV_VAR: '1'})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('images_after=2', proc.stdout)
            masked = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(mh.count_images(masked), 2)
            out2 = Path(tmp) / 'masked2.json'
            proc = self._run_cli(['mask', '--history', str(history),
                                  '--out', str(out2)],
                                 {mh.MASK_ENV_VAR: '0'})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('images_after=5', proc.stdout)
            passthrough = json.loads(out2.read_text(encoding='utf-8'))
            self.assertEqual(passthrough, _history(5))

    def test_cli_prompt_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / 'history.json'
            history.write_text(json.dumps(_history(5)), encoding='utf-8')
            current = Path(tmp) / 'current.json'
            current.write_text(json.dumps(
                {'image': '/tmp/obs6.png',
                 'description': 'verify output'}), encoding='utf-8')
            out = Path(tmp) / 'prompt.json'
            proc = self._run_cli(['prompt', '--history', str(history),
                                  '--current', str(current),
                                  '--out', str(out)],
                                 {mh.MASK_ENV_VAR: '1'})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(len(result['image_paths']), 2)
            self.assertEqual(result['image_paths'][-1], '/tmp/obs6.png')

    def test_cli_bad_history_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / 'bad.json'
            history.write_text('not json at all', encoding='utf-8')
            out = Path(tmp) / 'out.json'
            proc = self._run_cli(['mask', '--history', str(history),
                                  '--out', str(out)])
            self.assertEqual(proc.returncode, 2)


if __name__ == '__main__':
    unittest.main()

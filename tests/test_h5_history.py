"""Tests for the H5 history-pruning prototype.

Pure policy, no desktop, no broker, no model calls.
"""

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import h5_history as h5


def _turn(n, image=None, description=None, reasoning=None, action=None,
          result=None):
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
        'result': result or ('output of step %d' % n),
    }


def _history(count=5):
    return [_turn(n, image='/tmp/obs%d.png' % n,
                  description='terminal showing step %d output' % n)
            for n in range(1, count + 1)]


class FlagTests(unittest.TestCase):
    def test_default_off(self):
        self.assertFalse(h5.h5_enabled({}))

    def test_truthy_values(self):
        for value in ('1', 'true', 'yes', 'on', 'TRUE', ' On '):
            self.assertTrue(h5.h5_enabled({'CU_H5_DROP_OLD_SHOTS': value}),
                            value)

    def test_falsy_values(self):
        for value in ('0', 'false', 'no', 'off', '', 'maybe'):
            self.assertFalse(h5.h5_enabled({'CU_H5_DROP_OLD_SHOTS': value}),
                             value)

    def test_keep_full_default_is_one(self):
        self.assertEqual(h5.h5_keep_full({}), 1)

    def test_keep_full_env_override(self):
        self.assertEqual(h5.h5_keep_full({'CU_H5_KEEP_FULL': '2'}), 2)

    def test_keep_full_bad_value_raises(self):
        with self.assertRaises(ValueError):
            h5.h5_keep_full({'CU_H5_KEEP_FULL': 'two'})
        with self.assertRaises(ValueError):
            h5.h5_keep_full({'CU_H5_KEEP_FULL': '0'})
        with self.assertRaises(ValueError):
            h5.h5_keep_full({'CU_H5_KEEP_FULL': '-1'})

    def test_drop_text_flag(self):
        self.assertTrue(h5.h5_drop_text({'CU_H5_DROP_TEXT': '1'}))
        self.assertFalse(h5.h5_drop_text({}))
        self.assertFalse(h5.h5_drop_text({'CU_H5_DROP_TEXT': '0'}))


class HistoryLineTests(unittest.TestCase):
    def test_line_carries_description_action_and_result(self):
        line = h5.history_line(_turn(3, description='saw the file list',
                                     action='ran ls', result='3 files listed'))
        self.assertIn('saw the file list', line)
        self.assertIn('did: ran ls', line)
        self.assertIn('got: 3 files listed', line)
        self.assertTrue(line.startswith('[shot 3:'))

    def test_missing_fields_are_named_not_invented(self):
        turn = {"n": 2, "observation": {}}
        line = h5.history_line(turn)
        self.assertIn('(no description recorded)', line)
        self.assertIn('(no action recorded)', line)
        self.assertIn('(no result recorded)', line)
        self.assertNotIn('None', line)

    def test_non_dict_turn(self):
        self.assertEqual(h5.history_line('nope'),
                         '[shot ?: (unrecorded turn)]')

    def test_long_fields_truncated(self):
        line = h5.history_line(_turn(1, description='x' * 500,
                                     action='y' * 500, result='z' * 500))
        self.assertLessEqual(len(line), h5.LINE_MAX_CHARS + 3)
        self.assertIn('...', line)

    def test_window_fallback_when_no_description(self):
        turn = {'n': 4, 'label': 'obs4',
                'observation': {'image': '/tmp/o.png', 'window': '0x42'},
                'action': 'clicked save', 'result': 'dialog closed'}
        line = h5.history_line(turn)
        self.assertIn('observation obs4, window 0x42', line)


class PruneTurnsTests(unittest.TestCase):
    def test_keep_one_leaves_only_latest_image(self):
        turns = _history(5)
        out = h5.prune_turns(turns, keep_full=1)
        self.assertEqual(h5.count_images(out), 1)
        self.assertEqual(out[-1]['observation']['image'], '/tmp/obs5.png')
        for turn in out[:4]:
            self.assertIsNone(turn['observation']['image'])
            self.assertTrue(turn['observation']['pruned'])
            self.assertIn('did:', turn['observation']['history_line'])
            self.assertIn('got:', turn['observation']['history_line'])

    def test_input_never_mutated(self):
        turns = _history(3)
        before = json.dumps(turns, sort_keys=True)
        h5.prune_turns(turns, keep_full=1)
        self.assertEqual(json.dumps(turns, sort_keys=True), before)

    def test_reasoning_and_action_text_survive_pruning(self):
        out = h5.prune_turns(_history(3), keep_full=1)
        self.assertEqual(out[0]['reasoning'], 'decided step 1')
        self.assertEqual(out[0]['action'], 'ran command 1')
        self.assertEqual(out[0]['result'], 'output of step 1')

    def test_keep_at_least_len_keeps_everything(self):
        out = h5.prune_turns(_history(2), keep_full=2)
        self.assertEqual(h5.count_images(out), 2)
        self.assertNotIn('pruned', out[0]['observation'])

    def test_keep_two_replicates_masking_count(self):
        out = h5.prune_turns(_history(5), keep_full=2)
        self.assertEqual(h5.count_images(out), 2)
        self.assertEqual(out[-1]['observation']['image'], '/tmp/obs5.png')
        self.assertEqual(out[-2]['observation']['image'], '/tmp/obs4.png')

    def test_drop_text_leaves_no_line(self):
        out = h5.prune_turns(_history(3), keep_full=1, drop_text=True)
        self.assertEqual(h5.count_images(out), 1)
        self.assertIsNone(out[0]['observation']['history_line'])
        self.assertTrue(out[0]['observation']['pruned'])

    def test_negative_keep_raises(self):
        with self.assertRaises(ValueError):
            h5.prune_turns(_history(2), keep_full=-1)

    def test_empty_history(self):
        self.assertEqual(h5.prune_turns([], keep_full=1), [])


class ApplyH5Tests(unittest.TestCase):
    def test_flag_off_returns_same_object(self):
        turns = _history(3)
        self.assertIs(h5.apply_h5(turns, env={}), turns)

    def test_flag_on_prunes_to_one(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        out = h5.apply_h5(_history(4), env=env)
        self.assertEqual(h5.count_images(out), 1)
        self.assertEqual(len(out), 4)

    def test_flag_on_with_keep_override(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1', 'CU_H5_KEEP_FULL': '2'}
        out = h5.apply_h5(_history(4), env=env)
        self.assertEqual(h5.count_images(out), 2)

    def test_flag_on_with_drop_text_env(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1', 'CU_H5_DROP_TEXT': 'yes'}
        out = h5.apply_h5(_history(3), env=env)
        self.assertIsNone(out[0]['observation']['history_line'])


class BuildPromptTests(unittest.TestCase):
    def _current(self, n=6):
        return {'image': '/tmp/obs%d.png' % n,
                'description': 'current terminal', 'window': '0x10006'}

    def test_flag_on_prompt_carries_only_current_image(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        result = h5.build_think_prompt(_history(5), self._current(), env=env)
        self.assertEqual(result['image_paths'], ['/tmp/obs6.png'])
        self.assertEqual(result['kept_count'], 1)
        self.assertEqual(result['pruned_count'], 5)
        self.assertIn('did: ran command 1', result['prompt_text'])
        self.assertIn('got: output of step 1', result['prompt_text'])

    def test_flag_off_prompt_carries_every_image(self):
        result = h5.build_think_prompt(_history(3), self._current(), env={})
        self.assertEqual(len(result['image_paths']), 4)
        self.assertEqual(result['pruned_count'], 0)

    def test_current_always_fresh_even_with_empty_history(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        result = h5.build_think_prompt([], self._current(), env=env)
        self.assertEqual(result['image_paths'], ['/tmp/obs6.png'])
        self.assertEqual(result['pruned_count'], 0)

    def test_no_current_image_means_no_images(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        result = h5.build_think_prompt(_history(3), {}, env=env)
        self.assertEqual(result['image_paths'], [])
        self.assertIn('(no current image)', result['prompt_text'])

    def test_keep_two_prompt_carries_current_plus_latest_history(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        result = h5.build_think_prompt(_history(5), self._current(),
                                       env=env, keep_full=2)
        self.assertEqual(result['image_paths'],
                         ['/tmp/obs5.png', '/tmp/obs6.png'])
        self.assertEqual(result['pruned_count'], 4)

    def test_drop_text_prompt_marks_dropped_turns(self):
        env = {'CU_H5_DROP_OLD_SHOTS': '1'}
        result = h5.build_think_prompt(_history(3), self._current(),
                                       env=env, drop_text=True)
        self.assertEqual(result['image_paths'], ['/tmp/obs6.png'])
        self.assertIn('(dropped, no text)', result['prompt_text'])
        self.assertNotIn('did: ran command 1', result['prompt_text'])

    def test_keep_below_one_raises(self):
        with self.assertRaises(ValueError):
            h5.build_think_prompt(_history(2), self._current(), env={},
                                  keep_full=0)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.history_path = self.dir / 'history.jsonl'
        self.history_path.write_text(
            '\n'.join(json.dumps(turn) for turn in _history(5))
            + '\n', encoding='utf-8')
        self.current_path = self.dir / 'current.json'
        self.current_path.write_text(json.dumps(
            {'image': '/tmp/obs6.png', 'description': 'current terminal',
             'window': '0x10006'}), encoding='utf-8')
        self.script = str(ROOT / 'scripts' / 'h5_history.py')

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, args, env_extra=None):
        env = dict(os.environ)
        env.pop('CU_H5_DROP_OLD_SHOTS', None)
        env.pop('CU_H5_KEEP_FULL', None)
        env.pop('CU_H5_DROP_TEXT', None)
        if env_extra:
            env.update(env_extra)
        return subprocess.run([sys.executable, self.script] + args,
                              capture_output=True, text=True, env=env,
                              timeout=30)

    def test_prompt_cli_flag_on_one_image(self):
        out = self.dir / 'prompt.json'
        proc = self._run(['prompt', '--history', str(self.history_path),
                          '--current', str(self.current_path),
                          '--out', str(out)],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(out.read_text(encoding='utf-8'))
        self.assertEqual(result['image_paths'], ['/tmp/obs6.png'])
        self.assertEqual(result['pruned_count'], 5)
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
        self.assertIn('images=1 pruned=5', proc.stdout)

    def test_prompt_cli_flag_off_all_images(self):
        out = self.dir / 'prompt.json'
        proc = self._run(['prompt', '--history', str(self.history_path),
                          '--current', str(self.current_path),
                          '--out', str(out)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(out.read_text(encoding='utf-8'))
        self.assertEqual(len(result['image_paths']), 6)
        self.assertEqual(result['pruned_count'], 0)

    def test_prune_cli_flag_on(self):
        out = self.dir / 'pruned.json'
        proc = self._run(['prune', '--history', str(self.history_path),
                          '--out', str(out)],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        turns = json.loads(out.read_text(encoding='utf-8'))
        self.assertEqual(h5.count_images(turns), 1)
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)

    def test_prune_cli_drop_text(self):
        out = self.dir / 'pruned.json'
        proc = self._run(['prune', '--history', str(self.history_path),
                          '--out', str(out), '--drop-text'],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        turns = json.loads(out.read_text(encoding='utf-8'))
        self.assertIsNone(turns[0]['observation']['history_line'])

    def test_cli_bad_history_exits_2(self):
        bad = self.dir / 'bad.jsonl'
        bad.write_text('not json\n', encoding='utf-8')
        out = self.dir / 'prompt.json'
        proc = self._run(['prompt', '--history', str(bad),
                          '--current', str(self.current_path),
                          '--out', str(out)],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 2)

    def test_cli_keep_zero_exits_2(self):
        out = self.dir / 'prompt.json'
        proc = self._run(['prompt', '--history', str(self.history_path),
                          '--current', str(self.current_path),
                          '--out', str(out), '--keep', '0'],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 2)

    def test_cli_current_not_object_exits_2(self):
        bad = self.dir / 'bad-current.json'
        bad.write_text('["not", "an", "object"]', encoding='utf-8')
        out = self.dir / 'prompt.json'
        proc = self._run(['prompt', '--history', str(self.history_path),
                          '--current', str(bad),
                          '--out', str(out)],
                         {'CU_H5_DROP_OLD_SHOTS': '1'})
        self.assertEqual(proc.returncode, 2)

    def test_load_turns_accepts_json_list(self):
        listed = self.dir / 'listed.json'
        listed.write_text(json.dumps(_history(2)), encoding='utf-8')
        self.assertEqual(len(h5._load_turns(str(listed))), 2)


if __name__ == '__main__':
    unittest.main()

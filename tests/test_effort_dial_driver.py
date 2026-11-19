"""Tests for the resume-per-turn effort-dial driver.

Pure policy plus a fake codex runner: no desktop, no broker, no model
calls. The fake runner scripts codex JSONL replies so the escalation,
validation, and logging paths are exercised deterministically.
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
import effort_dial_driver as ed


def fake_jsonl(*, session_id=None, text='', reasoning=0, input_tokens=100,
               cached=90, output_tokens=10):
    """One minimal codex --json stream for a single turn."""
    lines = []
    if session_id is not None:
        lines.append(json.dumps({'type': 'thread.started', 'thread_id': session_id}))
    lines.append(json.dumps({'type': 'turn.started'}))
    lines.append(json.dumps({'type': 'item.completed',
                             'item': {'id': 'item_0', 'type': 'agent_message', 'text': text}}))
    lines.append(json.dumps({'type': 'turn.completed', 'usage': {
        'input_tokens': input_tokens, 'cached_input_tokens': cached,
        'output_tokens': output_tokens, 'reasoning_output_tokens': reasoning}}))
    return '\n'.join(lines) + '\n'


L2_OK = json.dumps({'action': 'pick_terminal', 'target': '0x1234', 'confidence': 0.9})


class FakeRunner:
    """Scripted codex runner. Each call pops the next reply."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, argv, timeout_s):
        self.calls.append(list(argv))
        if not self.replies:
            raise AssertionError('fake runner called with no replies left: %r' % (argv,))
        rc, stdout, stderr, wall = self.replies.pop(0)
        return rc, stdout, stderr, wall


class ParseTests(unittest.TestCase):
    def test_thread_usage_message(self):
        parsed = ed.parse_codex_jsonl(fake_jsonl(session_id='sess-1', text='hello', reasoning=7))
        self.assertEqual(parsed['session_id'], 'sess-1')
        self.assertEqual(parsed['usage']['reasoning_output_tokens'], 7)
        self.assertEqual(parsed['last_message'], 'hello')
        self.assertEqual(parsed['events'], 4)

    def test_malformed_lines_skipped(self):
        text = 'not json\n{"type":"turn.started"}\n{"type": 1}\n'
        parsed = ed.parse_codex_jsonl(text)
        self.assertIsNone(parsed['session_id'])
        self.assertIsNone(parsed['usage'])
        # Both JSON objects count as events even when their type is unusable.
        self.assertEqual(parsed['events'], 2)

    def test_empty_stream(self):
        parsed = ed.parse_codex_jsonl('')
        self.assertIsNone(parsed['session_id'])
        self.assertIsNone(parsed['usage'])
        self.assertEqual(parsed['events'], 0)

    def test_last_turn_wins(self):
        text = fake_jsonl(text='first', reasoning=1) + fake_jsonl(text='second', reasoning=2)
        parsed = ed.parse_codex_jsonl(text)
        self.assertEqual(parsed['last_message'], 'second')
        self.assertEqual(parsed['usage']['reasoning_output_tokens'], 2)

    def test_usage_numbers_defaults(self):
        self.assertEqual(ed.usage_numbers(None), {
            'input_tokens': 0, 'cached_input_tokens': 0,
            'reasoning_output_tokens': 0, 'output_tokens': 0})
        self.assertEqual(ed.usage_numbers({'input_tokens': 5, 'reasoning_output_tokens': True}), {
            'input_tokens': 5, 'cached_input_tokens': 0,
            'reasoning_output_tokens': 0, 'output_tokens': 0})


class ArgsTests(unittest.TestCase):
    def test_resume_low_has_schema(self):
        argv = ed.build_resume_args(model='gpt-6-luna', effort='low',
                                    last_file='/tmp/l.txt', session_id='sess-1',
                                    prompt='do it', level=sp.LEVEL_ROUTINE)
        self.assertEqual(argv[:3], ['codex', 'exec', 'resume'])
        self.assertIn('-c', argv)
        self.assertIn('model_reasoning_effort="low"', argv)
        self.assertIn('--output-schema', argv)
        self.assertEqual(argv[-2:], ['sess-1', 'do it'])
        self.assertIn('--json', argv)
        # Resume rejects -s/-C (rc=2 "unexpected argument '-s' found"):
        # sandbox and workdir are inherited from the bootstrap session.
        self.assertNotIn('-s', argv)
        self.assertNotIn('-C', argv)

    def test_resume_max_has_no_schema(self):
        argv = ed.build_resume_args(model='gpt-6-luna', effort='max',
                                    last_file='/tmp/l.txt', session_id='sess-1',
                                    prompt='do it', level=sp.LEVEL_AMBIGUOUS)
        self.assertIn('model_reasoning_effort="max"', argv)
        self.assertNotIn('--output-schema', argv)
        self.assertNotIn('-s', argv)
        self.assertNotIn('-C', argv)

    def test_exec_is_fresh_with_prompt_last(self):
        argv = ed.build_exec_args(model='gpt-6-luna', effort='max',
                                  sandbox='danger-full-access', workdir='/tmp/w',
                                  last_file='/tmp/l.txt', prompt='brief')
        self.assertEqual(argv[:2], ['codex', 'exec'])
        self.assertNotIn('resume', argv)
        self.assertEqual(argv[-1], 'brief')


class LevelTests(unittest.TestCase):
    def test_explicit_level_wins(self):
        self.assertEqual(ed.step_level({'level': 2}), sp.LEVEL_ROUTINE)
        self.assertEqual(ed.step_level({'level': 3}), sp.LEVEL_AMBIGUOUS)

    def test_unknown_explicit_level_raises(self):
        with self.assertRaises(ValueError):
            ed.step_level({'level': 9})

    def test_auto_classify(self):
        routine = {'is_procedure_step': False, 'is_irreversible': False,
                   'is_ambiguous': False, 'postcondition': {'type': 'broker_ok'}}
        self.assertEqual(ed.step_level(routine), sp.LEVEL_ROUTINE)
        ambiguous = dict(routine, is_ambiguous=True)
        self.assertEqual(ed.step_level(ambiguous), sp.LEVEL_AMBIGUOUS)
        deterministic = {'is_procedure_step': True, 'is_irreversible': False,
                         'is_ambiguous': False, 'postcondition': {'type': 'broker_ok'}}
        self.assertEqual(ed.step_level(deterministic), sp.LEVEL_DETERMINISTIC)
        no_check = {'is_procedure_step': False, 'is_irreversible': False,
                    'is_ambiguous': False, 'postcondition': {'type': 'none'}}
        self.assertEqual(ed.step_level(no_check), sp.LEVEL_AMBIGUOUS)


class PostconditionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name) / 'run'
        self.run_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _check(self, spec, last_message=''):
        return ed.check_postcondition(spec, run_dir=self.run_dir, last_message=last_message)

    def test_none_passes(self):
        self.assertTrue(self._check({'type': 'none'})[0])

    def test_unknown_type_fails_closed(self):
        passed, detail = self._check({'type': 'telepathy'})
        self.assertFalse(passed)
        self.assertIn('unknown postcondition type', detail)

    def test_broker_ok_no_records(self):
        passed, _ = self._check({'type': 'broker_ok'})
        self.assertFalse(passed)

    def test_broker_ok_record(self):
        (self.run_dir / 'records.jsonl').write_text(
            json.dumps({'label': 'x', 'ok': True, 'completed': 2}) + '\n', encoding='utf-8')
        self.assertTrue(self._check({'type': 'broker_ok'})[0])
        self.assertTrue(self._check({'type': 'broker_ok', 'min_completed': 2})[0])
        self.assertFalse(self._check({'type': 'broker_ok', 'min_completed': 3})[0])

    def test_broker_ok_error_record(self):
        (self.run_dir / 'records.jsonl').write_text(
            json.dumps({'label': 'x', 'ok': True}) + '\n' +
            json.dumps({'label': 'y', 'accepted': False, 'error': 'stale'}) + '\n',
            encoding='utf-8')
        self.assertFalse(self._check({'type': 'broker_ok'})[0])

    def test_file_exact_lines(self):
        target = Path(self.tmp.name) / 'f.txt'
        target.write_text('a\nb\n', encoding='utf-8')
        self.assertTrue(self._check({'type': 'file_exact_lines', 'path': str(target),
                                     'lines': ['a', 'b']})[0])
        self.assertFalse(self._check({'type': 'file_exact_lines', 'path': str(target),
                                      'lines': ['a', 'c']})[0])
        self.assertFalse(self._check({'type': 'file_exact_lines',
                                      'path': str(target) + '.missing',
                                      'lines': ['a']})[0])

    def test_file_contains_and_exists(self):
        target = Path(self.tmp.name) / 'f.txt'
        target.write_text('hello world', encoding='utf-8')
        self.assertTrue(self._check({'type': 'file_contains', 'path': str(target),
                                     'text': 'world'})[0])
        self.assertFalse(self._check({'type': 'file_contains', 'path': str(target),
                                      'text': 'moon'})[0])
        self.assertTrue(self._check({'type': 'file_exists', 'path': str(target)})[0])

    def test_reply_contains(self):
        self.assertTrue(self._check({'type': 'reply_contains', 'text': '96'},
                                    last_message='{"target": "96.0"}')[0])
        self.assertFalse(self._check({'type': 'reply_contains', 'text': '96'},
                                     last_message='nothing here')[0])

    def test_command_ok(self):
        self.assertTrue(self._check({'type': 'command_ok', 'argv': ['true']})[0])
        self.assertFalse(self._check({'type': 'command_ok', 'argv': ['false']})[0])
        self.assertFalse(self._check({'type': 'command_ok', 'argv': []})[0])
        self.assertFalse(self._check({'type': 'command_ok',
                                      'argv': ['/definitely/not/a/binary']})[0])

    def test_end_state_precheck_only_files(self):
        target = Path(self.tmp.name) / 'f.txt'
        target.write_text('a\n', encoding='utf-8')
        self.assertTrue(ed.end_state_precheck(
            {'type': 'file_exact_lines', 'path': str(target), 'lines': ['a']},
            run_dir=self.run_dir))
        self.assertFalse(ed.end_state_precheck({'type': 'broker_ok'}, run_dir=self.run_dir))
        self.assertFalse(ed.end_state_precheck({'type': 'reply_contains', 'text': 'x'},
                                                run_dir=self.run_dir))


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.run_dir = self.base / 'run'
        (self.run_dir).mkdir()
        (self.run_dir / 'records.jsonl').write_text(
            json.dumps({'label': 'x', 'ok': True, 'completed': 1}) + '\n', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def _driver(self, runner):
        return ed.EffortDialDriver(run_dir=self.run_dir, repo_dir=self.base,
                                   workdir=self.base / 'work', runner=runner, arm='test')

    def test_start_session_returns_id(self):
        runner = FakeRunner([(0, fake_jsonl(session_id='sess-9', text='READY', reasoning=4), '', 6.5)])
        driver = self._driver(runner)
        self.assertEqual(driver.start_session('brief'), 'sess-9')
        self.assertEqual(len(runner.calls), 1)
        self.assertIn('model_reasoning_effort="max"', runner.calls[0])
        turns = [json.loads(line) for line in (self.run_dir / 'turns.jsonl').read_text().splitlines()]
        self.assertEqual(turns[0]['effort'], 'max')
        self.assertEqual(turns[0]['reasoning_output_tokens'], 4)

    def test_start_session_no_id_raises(self):
        runner = FakeRunner([(0, fake_jsonl(text='READY'), '', 1.0)])
        with self.assertRaises(RuntimeError):
            self._driver(runner).start_session('brief')

    def test_level2_success_logs_low(self):
        runner = FakeRunner([(0, fake_jsonl(text=L2_OK, reasoning=0), '', 7.0)])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'windows', 'level': 2, 'prompt': 'list',
                'postcondition': {'type': 'broker_ok'}}
        ok, record = driver.run_step('sess-1', step)
        self.assertTrue(ok)
        self.assertEqual(record['effort'], 'low')
        self.assertTrue(record['validated'])
        self.assertTrue(record['postcondition_ok'])
        self.assertFalse(record['escalated'])
        self.assertIn('model_reasoning_effort="low"', runner.calls[0])
        self.assertIn('--output-schema', runner.calls[0])

    def test_level2_bad_json_escalates_to_max(self):
        runner = FakeRunner([
            (0, fake_jsonl(text='not json at all', reasoning=0), '', 5.0),
            (0, fake_jsonl(text='done, broker ok', reasoning=12), '', 9.0),
        ])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'windows', 'level': 2, 'prompt': 'list',
                'postcondition': {'type': 'broker_ok'}}
        ok, record = driver.run_step('sess-1', step)
        self.assertTrue(ok)
        self.assertTrue(record['escalated'])
        self.assertEqual(record['effort'], 'max')
        self.assertEqual(len(runner.calls), 2)
        self.assertIn('model_reasoning_effort="max"', runner.calls[1])
        self.assertIn('ESCALATION', runner.calls[1][-1])
        turns = [json.loads(line) for line in (self.run_dir / 'turns.jsonl').read_text().splitlines()]
        self.assertFalse(turns[0]['validated'])
        self.assertTrue(turns[1]['escalated'])

    def test_level2_irreversible_decision_escalates(self):
        bad = json.dumps({'action': 'delete', 'target': '/tmp/x', 'confidence': 1.0})
        runner = FakeRunner([
            (0, fake_jsonl(text=bad, reasoning=0), '', 5.0),
            (0, fake_jsonl(text='refused the delete, did nothing', reasoning=8), '', 9.0),
        ])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'routine', 'level': 2, 'prompt': 'decide',
                'postcondition': {'type': 'broker_ok'}}
        ok, record = driver.run_step('sess-1', step)
        self.assertTrue(ok)
        self.assertTrue(record['escalated'])
        self.assertIn('irreversible', (json.loads((self.run_dir / 'turns.jsonl').read_text().splitlines()[0])['validation_error']))

    def test_double_failure_fails_step(self):
        # The postcondition (missing file) fails on BOTH attempts, so the
        # L3 retry cannot recover the step. A passing broker_ok check
        # would let the retry succeed, which is correct recovery, not a
        # double failure.
        runner = FakeRunner([
            (0, fake_jsonl(text='not json', reasoning=0), '', 5.0),
            (0, fake_jsonl(text='still not json', reasoning=0), '', 5.0),
        ])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'windows', 'level': 2, 'prompt': 'list',
                'postcondition': {'type': 'file_exists',
                                  'path': str(self.base / 'definitely-missing.txt')}}
        ok, _ = driver.run_step('sess-1', step)
        self.assertFalse(ok)
        self.assertEqual(len(runner.calls), 2)

    def test_level1_makes_no_model_call(self):
        target = self.base / 'f.txt'
        target.write_text('x', encoding='utf-8')
        runner = FakeRunner([])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'check', 'level': 1, 'prompt': '',
                'postcondition': {'type': 'file_exists', 'path': str(target)}}
        ok, record = driver.run_step('sess-1', step)
        self.assertTrue(ok)
        self.assertFalse(record['model_call'])
        self.assertEqual(len(runner.calls), 0)

    def test_end_state_already_satisfied_skips_turn(self):
        target = self.base / 'f.txt'
        target.write_text('a\nb\n', encoding='utf-8')
        runner = FakeRunner([])
        driver = self._driver(runner)
        step = {'label': 's1', 'kind': 'verify', 'level': 2, 'prompt': 'verify',
                'postcondition': {'type': 'file_exact_lines', 'path': str(target),
                                  'lines': ['a', 'b']}}
        ok, record = driver.run_step('sess-1', step)
        self.assertTrue(ok)
        self.assertTrue(record['skipped'])
        self.assertEqual(len(runner.calls), 0)

    def test_run_plan_stops_task_on_failure(self):
        runner = FakeRunner([
            (0, fake_jsonl(text='not json', reasoning=0), '', 5.0),
            (0, fake_jsonl(text='still not json', reasoning=0), '', 5.0),
        ])
        driver = self._driver(runner)
        missing = str(self.base / 'definitely-missing.txt')
        existing = self.base / 'exists.txt'
        existing.write_text('x', encoding='utf-8')
        plan = {'tasks': [
            {'id': 'P1', 'steps': [
                {'label': 'p1-windows', 'kind': 'windows', 'level': 2, 'prompt': 'list',
                 'postcondition': {'type': 'file_exists', 'path': missing}}]},
            {'id': 'P2', 'steps': [
                {'label': 'p2-check', 'kind': 'check', 'level': 1, 'prompt': '',
                 'postcondition': {'type': 'file_exists', 'path': str(existing)}}]},
        ]}
        results = driver.run_plan('sess-1', plan)
        self.assertEqual(results, {'P1': (False, 'p1-windows'), 'P2': (True, None)})
        # P1 used both attempts; P2 needed no model call at all.
        self.assertEqual(len(runner.calls), 2)

    def test_write_summary_totals(self):
        runner = FakeRunner([
            (0, fake_jsonl(session_id='sess-1', text='READY', reasoning=4), '', 6.0),
            (0, fake_jsonl(text=L2_OK, reasoning=0), '', 7.0),
        ])
        driver = self._driver(runner)
        session_id = driver.start_session('brief')
        step = {'label': 's1', 'kind': 'windows', 'level': 2, 'prompt': 'list',
                'postcondition': {'type': 'broker_ok'}}
        driver.run_step(session_id, step)
        path = driver.write_summary({'P1': (True, None)})
        text = path.read_text(encoding='utf-8')
        self.assertIn('Model turns: 2 (low 1, max 1)', text)
        self.assertIn('Total reasoning tokens: 4 (low 0, max 4)', text)
        self.assertIn('- P1: PASS', text)

    def test_load_plan_rejects_bad_shape(self):
        with self.assertRaises(ValueError):
            ed.load_plan('/definitely/not/a/plan.json')
        bad = self.base / 'bad.json'
        bad.write_text('{"tasks": "nope"}', encoding='utf-8')
        with self.assertRaises(ValueError):
            ed.load_plan(str(bad))


if __name__ == '__main__':
    unittest.main()

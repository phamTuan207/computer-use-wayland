"""Unit tests for scripts/det_finish.py (deterministic finish).

Offline only: a stub session_remote.py answers status/finish, a synthetic
records.jsonl stands in for a run dir. No broker, no GUI, no hyprctl
(most tests pass --skip-hyprctl; one test proves the real hyprctl path
is non-fatal either way).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

DET_FINISH = Path(__file__).resolve().parents[1] / 'scripts' / 'det_finish.py'

CLEAN_FINISH = {'ok': True, 'status': 'finished', 'driver': 'stopped',
                'guardian': 'clean'}

STUB = r'''
import json, os, sys
from pathlib import Path

log = Path(os.environ['DET_FINISH_STUB_LOG'])
with open(log, 'a', encoding='utf-8') as handle:
    handle.write(' '.join(sys.argv[1:]) + '\n')
if sys.argv[1] == 'status':
    print(json.dumps({'ok': True, 'state': 'running', 'driver': 'ready',
                      'broker_generation': 'test'}))
elif sys.argv[1] == 'finish':
    print(json.dumps(json.loads(os.environ['DET_FINISH_STUB_FINISH'])))
else:
    print(json.dumps({'ok': False, 'error': 'unsupported_command'}))
    raise SystemExit(1)
'''


def _records():
    return [
        {'cmd': 'start', 'label': 'p1-start', 'submit_mono': 10.0,
         'submit_wall': 1000.0, 'result_wall': 1000.9,
         'start_call_s': 0.9, 'ok': True},
        {'cmd': 'request', 'label': 'p1-windows', 'kind': 'windows',
         'submit_wall': 1001.0, 'result_wall': 1001.2, 'service_s': 0.2,
         'ok': True},
        {'cmd': 'request', 'label': 'p1-act', 'kind': 'act',
         'submit_wall': 1010.0, 'result_wall': 1010.5, 'service_s': 0.5,
         'ok': True},
        {'cmd': 'request', 'label': 'p1-verify', 'kind': 'observe',
         'submit_wall': 1020.0, 'result_wall': 1036.5, 'service_s': 0.4,
         'ok': True, 'image_bytes_total': 1234},
    ]


class DetFinishTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_dir = self.root / 'run'
        self.run_dir.mkdir()
        self.lease = self.root / 'p1.lease'
        self.lease.write_text('{"owner": "test"}', encoding='utf-8')
        self.stub = self.root / 'stub_remote.py'
        self.stub.write_text(STUB, encoding='utf-8')
        self.stub_log = self.root / 'stub.log'
        self.stub_log.write_text('', encoding='utf-8')

    def _env(self, finish=None):
        import os
        env = dict(os.environ)
        env['DET_FINISH_STUB_LOG'] = str(self.stub_log)
        env['DET_FINISH_STUB_FINISH'] = json.dumps(
            finish if finish is not None else CLEAN_FINISH)
        return env

    def _write_records(self, records):
        path = self.run_dir / 'records.jsonl'
        with open(path, 'w', encoding='utf-8') as handle:
            for record in records:
                handle.write(json.dumps(record) + '\n')
        return path

    def _run(self, *extra, finish=None):
        cmd = [sys.executable, str(DET_FINISH),
               '--lease-file', str(self.lease),
               '--task-id', 'P1', '--run-dir', str(self.run_dir),
               '--verify-evidence', 'obs-1234',
               '--session-remote', str(self.stub),
               '--skip-hyprctl', *extra]
        return subprocess.run(cmd, capture_output=True, text=True,
                              env=self._env(finish), timeout=60)

    def _parse_records(self):
        path = self.run_dir / 'records.jsonl'
        return [json.loads(line) for line in
                path.read_text(encoding='utf-8').splitlines() if line.strip()]

    def test_happy_path_writes_summary_and_appends_record(self):
        self._write_records(_records())
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        lines = proc.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1, 'exactly one JSON line on stdout')
        out = json.loads(lines[0])
        self.assertTrue(out['ok'])
        self.assertEqual(out['status'], 'finished')
        self.assertEqual(out['loop_wall_s'], 36.5)
        summary = json.loads(
            (self.run_dir / 'det-finish-P1.json').read_text(
                encoding='utf-8'))
        self.assertTrue(summary['ok'])
        self.assertEqual(summary['timing']['loop_wall_s'], 36.5)
        self.assertEqual(summary['timing']['service_s_total'], 1.1)
        self.assertEqual(summary['timing']['requests_by_kind'],
                         {'windows': 1, 'act': 1, 'observe': 1})
        self.assertEqual(summary['timing']['image_bytes_total'], 1234)
        self.assertEqual(summary['verify_evidence'], 'obs-1234')
        self.assertIsInstance(summary['timing']['verify_to_finish_s'], float)
        md = (self.run_dir / 'summary.md').read_text(encoding='utf-8')
        self.assertIn('<!-- det-finish P1 -->', md)
        self.assertIn('SUCCESS', md)
        self.assertIn('36.5 s', md)
        parsed = self._parse_records()
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[-1]['cmd'], 'det-finish')
        self.assertTrue(parsed[-1]['ok'])
        invoked = self.stub_log.read_text(encoding='utf-8')
        self.assertIn('status --lease-file', invoked)
        self.assertIn('finish --lease-file', invoked)

    def test_failed_finish_exits_1_but_still_writes_summary(self):
        self._write_records(_records())
        proc = self._run(finish={'ok': False, 'status': 'cleaning',
                                 'driver': 'stopping', 'guardian': 'active',
                                 'error': 'cleanup_pending'})
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout.strip())
        self.assertFalse(out['ok'])
        summary = json.loads(
            (self.run_dir / 'det-finish-P1.json').read_text(
                encoding='utf-8'))
        self.assertFalse(summary['ok'])
        self.assertEqual(summary['finish']['status'], 'cleaning')
        md = (self.run_dir / 'summary.md').read_text(encoding='utf-8')
        self.assertIn('FINISH-FAILED', md)

    def test_invalid_task_id_rejected_without_touching_broker(self):
        proc = subprocess.run(
            [sys.executable, str(DET_FINISH),
             '--lease-file', str(self.lease), '--task-id', 'P1;rm',
             '--run-dir', str(self.run_dir), '--verify-evidence', 'obs-1',
             '--session-remote', str(self.stub), '--skip-hyprctl'],
            capture_output=True, text=True, env=self._env(), timeout=60)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(self.stub_log.read_text(encoding='utf-8'), '')

    def test_empty_and_oversize_evidence_rejected(self):
        for evidence in ('', ' ', 'x' * 501):
            proc = subprocess.run(
                [sys.executable, str(DET_FINISH),
                 '--lease-file', str(self.lease), '--task-id', 'P1',
                 '--run-dir', str(self.run_dir),
                 '--verify-evidence', evidence,
                 '--session-remote', str(self.stub), '--skip-hyprctl'],
                capture_output=True, text=True, env=self._env(), timeout=60)
            self.assertEqual(proc.returncode, 2, repr(evidence))
        self.assertEqual(self.stub_log.read_text(encoding='utf-8'), '')

    def test_missing_lease_file_rejected(self):
        proc = subprocess.run(
            [sys.executable, str(DET_FINISH),
             '--lease-file', str(self.root / 'nope.lease'),
             '--task-id', 'P1', '--run-dir', str(self.run_dir),
             '--verify-evidence', 'obs-1',
             '--session-remote', str(self.stub), '--skip-hyprctl'],
            capture_output=True, text=True, env=self._env(), timeout=60)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(self.stub_log.read_text(encoding='utf-8'), '')

    def test_missing_records_file_still_finishes_with_null_timings(self):
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        summary = json.loads(
            (self.run_dir / 'det-finish-P1.json').read_text(
                encoding='utf-8'))
        self.assertIsNone(summary['timing']['loop_wall_s'])
        self.assertEqual(summary['records_lines'], 0)
        self.assertEqual(summary['records_bad_lines'], 0)

    def test_truncated_last_line_counted_not_fatal(self):
        path = self._write_records(_records())
        with open(path, 'a', encoding='utf-8') as handle:
            handle.write('{"cmd": "request", "label": "p1-broken')
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        summary = json.loads(
            (self.run_dir / 'det-finish-P1.json').read_text(
                encoding='utf-8'))
        self.assertEqual(summary['records_bad_lines'], 1)
        self.assertEqual(summary['timing']['loop_wall_s'], 36.5)

    def test_append_never_glues_onto_unterminated_last_line(self):
        path = self.run_dir / 'records.jsonl'
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(_records()[0]))
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        parsed = self._parse_records()
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['cmd'], 'start')
        self.assertEqual(parsed[1]['cmd'], 'det-finish')

    def test_second_run_replaces_summary_block_for_same_task(self):
        self._write_records(_records())
        self.assertEqual(self._run().returncode, 0)
        self.assertEqual(self._run().returncode, 0)
        md = (self.run_dir / 'summary.md').read_text(encoding='utf-8')
        self.assertEqual(md.count('<!-- det-finish P1 -->'), 1)
        self.assertEqual(md.count('<!-- /det-finish P1 -->'), 1)

    def test_hyprctl_path_is_non_fatal(self):
        self._write_records(_records())
        cmd = [sys.executable, str(DET_FINISH),
               '--lease-file', str(self.lease),
               '--task-id', 'P1', '--run-dir', str(self.run_dir),
               '--verify-evidence', 'obs-1234',
               '--session-remote', str(self.stub)]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=self._env(), timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_blocked_evidence_finishes_with_blocked_outcome(self):
        self._write_records(_records())
        cmd = [sys.executable, str(DET_FINISH),
               '--lease-file', str(self.lease),
               '--task-id', 'P1', '--run-dir', str(self.run_dir),
               '--verify-evidence', 'BLOCKED:broker-busy',
               '--session-remote', str(self.stub), '--skip-hyprctl']
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=self._env(), timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        summary = json.loads(
            (self.run_dir / 'det-finish-P1.json').read_text(
                encoding='utf-8'))
        self.assertTrue(summary['ok'])
        self.assertEqual(summary['task_outcome'], 'BLOCKED')
        self.assertEqual(summary['blocked_reason'], 'broker-busy')
        md = (self.run_dir / 'summary.md').read_text(encoding='utf-8')
        self.assertIn('BLOCKED', md)


if __name__ == '__main__':

    unittest.main()

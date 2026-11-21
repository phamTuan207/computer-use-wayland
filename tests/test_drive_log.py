import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import drive_log

TZ = timezone(timedelta(hours=7))


class FakeClock:
    def __init__(self, start):
        self.wall = start
        self.mono = 1000.0

    def wall_fn(self):
        return self.wall

    def mono_fn(self):
        return self.mono

    def advance(self, wall_seconds, mono_seconds=None):
        self.wall += timedelta(seconds=wall_seconds)
        self.mono += mono_seconds if mono_seconds is not None else wall_seconds


class DriveLogTests(unittest.TestCase):
    def test_start_writes_run_started_with_zero_elapsed(self):
        with tempfile.TemporaryDirectory() as folder:
            clock = FakeClock(datetime(2026, 11, 21, 4, 0, 0, tzinfo=TZ))
            path = Path(folder) / 'drive.jsonl'
            log = drive_log.DriveLog.start(path, run_id='drive-test',
                                           wall_fn=clock.wall_fn, mono_fn=clock.mono_fn)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['event'], 'run_started')
            self.assertEqual(rows[0]['wall'], '2026-11-21 04:00:00 +0700')
            self.assertEqual(rows[0]['elapsed_s'], 0)
            self.assertEqual(rows[0]['run_id'], 'drive-test')

    def test_events_carry_wall_clock_and_elapsed(self):
        with tempfile.TemporaryDirectory() as folder:
            clock = FakeClock(datetime(2026, 11, 21, 4, 0, 0, tzinfo=TZ))
            path = Path(folder) / 'drive.jsonl'
            log = drive_log.DriveLog.start(path, run_id='drive-test',
                                           wall_fn=clock.wall_fn, mono_fn=clock.mono_fn)
            clock.advance(12.5)
            record = log.event('miss', 'aimed (805, 825), hit Remove')
            self.assertEqual(record['wall'], '2026-11-21 04:00:12 +0700')
            self.assertEqual(record['elapsed_s'], 12.5)
            self.assertEqual(record['detail'], 'aimed (805, 825), hit Remove')
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row['event'] for row in rows], ['run_started', 'miss'])

    def test_empty_event_name_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            clock = FakeClock(datetime(2026, 11, 21, 4, 0, 0, tzinfo=TZ))
            log = drive_log.DriveLog.start(Path(folder) / 'drive.jsonl',
                                           wall_fn=clock.wall_fn, mono_fn=clock.mono_fn)
            with self.assertRaises(ValueError):
                log.event('')

    def test_reopen_keeps_t0_across_processes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'drive.jsonl'
            clock1 = FakeClock(datetime(2026, 11, 21, 4, 0, 0, tzinfo=TZ))
            drive_log.DriveLog.start(path, run_id='drive-test',
                                     wall_fn=clock1.wall_fn, mono_fn=clock1.mono_fn)
            # A later process: new clock, no shared monotonic base.
            clock2 = FakeClock(datetime(2026, 11, 21, 4, 5, 0, tzinfo=TZ))
            log2 = drive_log.DriveLog.open_existing(
                path, wall_fn=clock2.wall_fn, mono_fn=clock2.mono_fn)
            self.assertEqual(log2.run_id, 'drive-test')
            record = log2.event('step', 'second process continues')
            self.assertEqual(record['elapsed_s'], 300.0)

    def test_end_writes_run_ended(self):
        with tempfile.TemporaryDirectory() as folder:
            clock = FakeClock(datetime(2026, 11, 21, 4, 0, 0, tzinfo=TZ))
            log = drive_log.DriveLog.start(Path(folder) / 'drive.jsonl',
                                           wall_fn=clock.wall_fn, mono_fn=clock.mono_fn)
            log.end('done', 'all steps complete')
            rows = [json.loads(line) for line in
                    (Path(folder) / 'drive.jsonl').read_text().splitlines()]
            self.assertEqual(rows[-1]['event'], 'run_ended')
            self.assertEqual(rows[-1]['outcome'], 'done')

    def test_cli_appends_across_calls(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'drive.jsonl'
            script = str(Path(__file__).resolve().parents[1] / 'scripts' / 'drive_log.py')
            for name in ('step', 'miss'):
                proc = subprocess.run(
                    [sys.executable, script, '--file', str(path),
                     '--event', name, '--detail', f'cli {name}'],
                    capture_output=True, text=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row['event'] for row in rows],
                             ['run_started', 'step', 'miss'])
            self.assertTrue(all(row['elapsed_s'] >= 0 for row in rows))
            self.assertTrue(all(row['wall'] for row in rows))


if __name__ == '__main__':
    unittest.main()

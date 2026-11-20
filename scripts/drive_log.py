"""File log for direct computer-use driving (I31, hard rule 21/11).

When an agent drives computer-use directly (not Codex running it), every
step must be logged with wall-clock time (Asia/Ho_Chi_Minh) and elapsed
time into a FILE, not only into chat history. Chat history is not a log:
it has no timestamps per action and it cannot be grepped after the fact.

Each run gets one JSONL file, one record per event:

    {"wall": "2026-11-21 04:12:03 +07:00", "elapsed_s": 12.345,
     "run_id": "drive-20261121-041200", "event": "step",
     "detail": "clicked Browse, hovered off-center first"}

Events to record: every action taken, every miss, every overlay flicker,
every slow decision, every error, and the run start/end. A run that
produced no log file did not happen.

Usage from Python (long-lived driver):

    from drive_log import DriveLog
    log = DriveLog.start(Path('~/drive-20261121.jsonl'))
    log.event('step', 'observed Polygon dashboard')
    log.event('miss', 'aimed (805, 825), hit Remove instead of View')
    log.event('flicker', 'overlay blinked 3 times in 2s')
    log.end('done')

Usage from the shell (one event per call; the file keeps T0 across calls):

    python3 scripts/drive_log.py --file drive-20261121.jsonl \\
        --event step --detail "observed Polygon dashboard"
"""
import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo('Asia/Ho_Chi_Minh')
except Exception:
    TZ = timezone(timedelta(hours=7))


def _wall_now():
    return datetime.now(TZ)


def _wall_text(moment):
    return moment.strftime('%Y-%m-%d %H:%M:%S %z')


def _parse_wall(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S %z')


class DriveLog:
    """One JSONL drive log. T0 is the first record; elapsed is wall-based
    when reopened across processes, monotonic-based within one process."""

    def __init__(self, path, run_id, t0_wall, t0_mono=None,
                 wall_fn=None, mono_fn=None):
        self.path = Path(path)
        self.run_id = run_id
        self.t0_wall = t0_wall
        self.t0_mono = t0_mono
        self._wall_fn = wall_fn or _wall_now
        self._mono_fn = mono_fn or time.monotonic

    @classmethod
    def start(cls, path, run_id=None, wall_fn=None, mono_fn=None):
        """Create a new log (or resume an existing one) and record run_started."""
        path = Path(path)
        run_id = run_id or 'drive-' + datetime.now(TZ).strftime('%Y%m%d-%H%M%S')
        wall_fn = wall_fn or _wall_now
        mono_fn = mono_fn or time.monotonic
        if path.exists():
            return cls.open_existing(path, wall_fn=wall_fn, mono_fn=mono_fn)
        log = cls(path, run_id, wall_fn(), mono_fn(), wall_fn, mono_fn)
        log.event('run_started', f'run_id {run_id}')
        return log

    @classmethod
    def open_existing(cls, path, wall_fn=None, mono_fn=None):
        """Reopen a log written by an earlier process; T0 stays the first record."""
        path = Path(path)
        wall_fn = wall_fn or _wall_now
        mono_fn = mono_fn or time.monotonic
        first = None
        run_id = None
        with open(path, 'r', encoding='utf-8') as stream:
            for line in stream:
                if not line.strip():
                    continue
                first = json.loads(line)
                break
        if first is None:
            raise ValueError(f'drive log has no records: {path}')
        run_id = first.get('run_id') or 'drive-unknown'
        t0_wall = _parse_wall(first['wall'])
        return cls(path, run_id, t0_wall, None, wall_fn, mono_fn)

    def elapsed_s(self, now_wall=None, now_mono=None):
        """Elapsed seconds since T0. Monotonic when this process started the
        run (immune to clock jumps); wall-based when reopened across processes."""
        if self.t0_mono is not None:
            return round((now_mono if now_mono is not None else self._mono_fn()) - self.t0_mono, 3)
        now_wall = now_wall if now_wall is not None else self._wall_fn()
        return round((now_wall - self.t0_wall).total_seconds(), 3)

    def event(self, name, detail='', **fields):
        """Append one event record. Raises on an empty event name."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError('drive log event name must be a non-empty string')
        now_wall = self._wall_fn()
        now_mono = self._mono_fn() if self.t0_mono is not None else None
        record = {'wall': _wall_text(now_wall), 'elapsed_s': self.elapsed_s(now_wall, now_mono),
                  'run_id': self.run_id, 'event': name}
        if detail:
            record['detail'] = detail
        record.update(fields)
        from jsonlutil import append_jsonl
        append_jsonl(self.path, record)
        return record

    def end(self, outcome='done', detail=''):
        """Append the closing run_ended record."""
        return self.event('run_ended', detail, outcome=outcome)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Append one event to a drive log file.')
    parser.add_argument('--file', required=True, help='JSONL log file path')
    parser.add_argument('--run-id', default=None, help='run id (new log only)')
    parser.add_argument('--event', required=True, help='event name, e.g. step, miss, flicker, error')
    parser.add_argument('--detail', default='', help='free-text detail for the event')
    args = parser.parse_args(argv)
    log = DriveLog.start(args.file, run_id=args.run_id)
    record = log.event(args.event, args.detail)
    print(json.dumps(record, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

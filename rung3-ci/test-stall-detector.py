#!/usr/bin/env python3
"""Synthetic-fixture tests for stall-detector.py. Run directly:
python3 rung3-ci/test-stall-detector.py  (exit 0 = all pass)."""
import datetime
import importlib.util
import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "stall_detector", os.path.join(HERE, "stall-detector.py"))
sd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sd)

TZ = datetime.timezone(datetime.timedelta(hours=7))
BASE = datetime.datetime(2026, 1, 1, 0, 0, tzinfo=TZ)


def at(minutes):
    return BASE + datetime.timedelta(minutes=minutes)


def write(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def main():
    checks = 0
    with tempfile.TemporaryDirectory() as tmp:
        # Heartbeat every 10 min for 2h, then 70 min silence, then resume.
        beats = [at(m) for m in range(0, 121, 10)] + [at(190), at(200)]
        hb = write(tmp, "hb.log", "\n".join(
            json.dumps({"ts": t.isoformat()}) for t in beats))
        got = sd.heartbeat_times(hb)
        assert len(got) == len(beats), got
        checks += 1
        gaps = sd.gaps_over(got, 30)
        assert len(gaps) == 1 and abs(gaps[0][2] - 70) < 0.01, gaps
        checks += 1

        # Git-only silence covered by heartbeats must NOT flag (union rule).
        ledger = [at(0), at(200)]
        union = sorted(set(got + ledger))
        assert len(sd.gaps_over(union, 30)) == 1  # only the real 70 gap
        checks += 1

        # Reports parser: pipe lines only, comments ignored.
        rp = write(tmp, "rp.log",
                   "# header\n%s | R3-001 | PASS\nnot a row\n"
                   "%s | R3-002 | PASS\n"
                   % (at(0).isoformat(), at(45).isoformat()))
        assert sd.report_times(rp) == [at(0), at(45)]
        checks += 1

        # Grades latency: test rows skipped, minutes computed.
        gr = write(tmp, "gr.jsonl", "\n".join([
            json.dumps({"task_id": "R3-TEST", "test_row": True,
                        "timestamps": {"task_end": at(0).isoformat(),
                                       "recorded_at": at(5).isoformat()}}),
            json.dumps({"task_id": "R3-001",
                        "timestamps": {"task_end": at(10).isoformat(),
                                       "recorded_at": at(40).isoformat()}}),
        ]))
        times, lat = sd.grade_latencies(gr)
        assert times == [at(40)] and lat == [("R3-001", 30.0)], (times, lat)
        checks += 1

        # Malformed lines are skipped, never crash.
        bad = write(tmp, "bad.log", "not json\n{\"ts\": \"junk\"}\n")
        assert sd.heartbeat_times(bad) == []
        checks += 1

        # Missing files yield empty signals.
        assert sd.heartbeat_times(os.path.join(tmp, "nope")) == []
        checks += 1

    print("test-stall-detector: %d checks PASS" % checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

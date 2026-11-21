#!/usr/bin/env python3
"""Test 07, error handling: finish a batch job that dies halfway.

Context: a batch job must turn 10 input files into 10 output files.
The naive runner crashes on the one corrupt input and loses the
whole run. The task is to make the job finish properly: process
every good input, record the bad one in a failure report instead of
crashing, and keep a checkpoint so a second run does no duplicate
work.

Pass: 9 outputs exist with correct content, the failure report
names exactly the corrupt file, the checkpoint lists 9 done items,
and a rerun processes 0 files.
Fail: the job crashes, an output is wrong, or the rerun redoes work.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case

GOOD = [f"input_{i:02d}.txt" for i in range(9)]
BAD = "input_bad.txt"


def process_one(path):
    text = path.read_text(encoding="utf-8")
    if "CORRUPT" in text:
        raise ValueError("corrupt input")
    return text.upper()


def main():
    case = Case("test07", "finish a batch job that dies halfway",
                "error handling")
    ws = case.ws
    inputs = ws / "inputs"
    outputs = ws / "outputs"
    inputs.mkdir()
    outputs.mkdir()
    with case.phase("setup_fixture"):
        for name in GOOD:
            (inputs / name).write_text(f"payload {name}\n", encoding="utf-8")
        (inputs / BAD).write_text("CORRUPT payload\n", encoding="utf-8")

    processed_log = []

    def run_job():
        checkpoint_path = ws / "checkpoint.json"
        done = set()
        if checkpoint_path.exists():
            done = set(json.loads(checkpoint_path.read_text()))
        failures = []
        processed = 0
        for path in sorted(inputs.iterdir()):
            if path.name in done:
                continue
            try:
                result = process_one(path)
            except ValueError as exc:
                failures.append({"file": path.name, "error": str(exc)})
                continue
            (outputs / (path.stem + ".out")).write_text(result,
                                                        encoding="utf-8")
            done.add(path.name)
            processed += 1
            processed_log.append(path.name)
        checkpoint_path.write_text(json.dumps(sorted(done)), encoding="utf-8")
        (ws / "failures.json").write_text(json.dumps(failures, indent=2),
                                          encoding="utf-8")
        return processed, failures

    with case.phase("run_job_with_recovery"):
        processed, failures = run_job()
        case.check("job_processed_all_good", processed == 9,
                   f"processed={processed}")
        case.check("failure_reported_not_crashed",
                   failures == [{"file": BAD, "error": "corrupt input"}],
                   f"failures={failures}")

    with case.phase("verify_outputs_and_checkpoint"):
        wrong = [n for n in GOOD
                 if (outputs / (Path(n).stem + ".out")).read_text()
                 != f"payload {n}\n".upper()]
        case.check("outputs_correct", wrong == [], f"wrong={wrong}")
        done = json.loads((ws / "checkpoint.json").read_text())
        case.check("checkpoint_has_9", len(done) == 9, f"done={len(done)}")

    with case.phase("rerun_is_a_noop"):
        processed_again, _ = run_job()
        case.check("rerun_processes_nothing", processed_again == 0,
                   f"again={processed_again}")
        case.check("no_duplicate_processing",
                   len(processed_log) == len(set(processed_log)) == 9)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

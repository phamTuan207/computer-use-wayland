#!/usr/bin/env python3
"""Arm B executor: planned execution.

Reads one plan file (plans/taskN_plan.md), extracts the JSON step
list, and runs it in batches. A DOM observation is taken ONLY at
the plan's checkpoints (start, middle, end). No observation is
taken before individual actions, that is the whole point of the
arm. Usage: executor.py task1 .. task6 (one task per process).
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session, ROOT
from checks import CHECKS

FIXTURE_OF = {
    "task1": "task1_form.html",
    "task2": "task2_table.html",
    "task3": "task3_wizard.html",
    "task4": "task4_settings.html",
    "task5": "task5_trap.html",
    "task6": "task6_cart.html",
}


def load_steps(task_id):
    text = (ROOT / "plans" / f"{task_id}_plan.md").read_text(encoding="utf-8")
    block = re.search(r"```json\s*(.*?)```", text, re.S).group(1)
    return json.loads(block)


def main():
    task_id = sys.argv[1]
    steps = load_steps(task_id)
    s = Session(task_id)
    s.start(FIXTURE_OF[task_id])
    for step in steps:
        op = step["op"]
        if op == "checkpoint":
            s.observe()
        elif op == "click":
            s.click(step["id"])
        elif op == "type":
            s.type_into(step["id"], step["text"])
        elif op == "select":
            s.select_value(step["id"], step["value"])
        elif op == "set_range":
            s.set_range(step["id"], int(step["value"]))
        else:
            raise ValueError(f"unknown op {op}")
    ok, detail = CHECKS[task_id](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

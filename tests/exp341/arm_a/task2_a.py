#!/usr/bin/env python3
"""Arm A, task 2: single agent, observation before every action."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session
from checks import CHECKS


def main():
    s = Session("task2")
    s.start("task2_table.html")

    s.observe(); s.select_value("filter-cat", "Books")
    s.observe(); s.click("sort-amount")

    ok, detail = CHECKS["task2"](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

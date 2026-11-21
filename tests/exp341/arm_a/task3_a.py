#!/usr/bin/env python3
"""Arm A, task 3: single agent, observation before every action.
The straightforward agent trusts the prefilled values, hits the
validation errors, observes them, and fixes them reactively.
Each validation bounce counts as one retry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session
from checks import CHECKS


def main():
    s = Session("task3")
    s.start("task3_wizard.html")

    s.observe(); s.click("w-next1")
    state = s.observe()
    if "Email must contain @" in state["text"]:
        s.retries += 1
        s.type_into("w-email", "user@example.com")
        s.observe(); s.click("w-next1")
        state = s.observe()
    if "Password must be at least 8" in state["text"]:
        s.retries += 1
        s.type_into("w-pass", "longenough1")
        s.observe(); s.click("w-next1")

    s.observe(); s.type_into("w-name", "Test User")
    s.observe(); s.type_into("w-age", "30")
    s.observe(); s.click("w-next2")
    s.observe(); s.click("w-confirm")

    ok, detail = CHECKS["task3"](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

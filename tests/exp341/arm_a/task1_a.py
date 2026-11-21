#!/usr/bin/env python3
"""Arm A, task 1: single agent, plan and execution interleaved.
A fresh DOM observation is taken before every single action."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session
from checks import CHECKS


def main():
    s = Session("task1")
    s.start("task1_form.html")

    s.observe(); s.type_into("f-name", "Ada Lovelace")
    s.observe(); s.type_into("f-email", "ada@example.com")
    s.observe(); s.type_into("f-city", "Hanoi")
    s.observe(); s.select_value("f-country", "VN")
    s.observe(); s.click("f-plan-pro")
    s.observe(); s.click("f-agree")
    s.observe(); s.click("f-submit")

    ok, detail = CHECKS["task1"](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

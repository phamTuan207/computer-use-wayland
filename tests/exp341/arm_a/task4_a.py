#!/usr/bin/env python3
"""Arm A, task 4: single agent, observation before every action."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session
from checks import CHECKS


def main():
    s = Session("task4")
    s.start("task4_settings.html")

    s.observe(); s.click("set-notify")
    s.observe(); s.click("set-dark")
    s.observe(); s.select_value("set-lang", "vi")
    s.observe(); s.set_range("set-volume", 70)
    s.observe(); s.type_into("set-font", "16")
    s.observe(); s.click("set-save")

    ok, detail = CHECKS["task4"](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

#!/usr/bin/env python3
"""Arm A, task 6: single agent, observation before every action."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session
from checks import CHECKS


def main():
    s = Session("task6")
    s.start("task6_cart.html")

    s.observe(); s.click("add-kbd")
    s.observe(); s.click("add-kbd")
    s.observe(); s.click("add-mouse")
    s.observe(); s.type_into("code", "SAVE10")
    s.observe(); s.click("apply-code")

    ok, detail = CHECKS["task6"](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

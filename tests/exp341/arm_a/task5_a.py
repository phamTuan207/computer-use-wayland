#!/usr/bin/env python3
"""Arm A, task 5, the trap: single agent, observation before every
action. The greedy agent reads the goal (save the draft with a new
title), sees one big primary button, and clicks it first. Only the
checker reveals that Publish archived the draft instead of saving
it, so the agent reloads and redoes the task with the plain Save
draft button. That redo counts as one retry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session, fixture_uri
from checks import CHECKS


def main():
    s = Session("task5")
    s.start("task5_trap.html")

    s.observe(); s.type_into("d-title", "Release notes")
    s.observe(); s.click("btn-publish")

    ok, detail = CHECKS["task5"](s)
    if not ok:
        s.retries += 1
        s.driver.get(fixture_uri("task5_trap.html"))
        s.observe(); s.type_into("d-title", "Release notes")
        s.observe(); s.click("btn-save")
        ok, detail = CHECKS["task5"](s)

    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

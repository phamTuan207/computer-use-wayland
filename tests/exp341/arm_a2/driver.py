#!/usr/bin/env python3
"""Arm A-prime: a competent interleaved agent.

Same architecture as arm A: observe, decide, act, observe again,
one observation before every action. The difference is that the
decisions actually consume the observation. Field values are read
and fixed BEFORE submitting, buttons are chosen by matching their
observed label and data-action against the goal, and error text in
the observation triggers a counted retry.

The GOALS below are the task statements, the same goals arms A and
B were given (target values included). Everything about the PAGE,
its current values, its defects, its traps, is read from the
observation payload at run time. Usage: driver.py task1 .. task6.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from common import fixture_uri
from checks import CHECKS
from session_a2 import (A2Session, active_errors, button_by_context,
                        button_by_label, input_by_id, input_by_label)

FIXTURE_OF = {
    "task1": "task1_form.html",
    "task2": "task2_table.html",
    "task3": "task3_wizard.html",
    "task4": "task4_settings.html",
    "task5": "task5_trap.html",
    "task6": "task6_cart.html",
}

GOALS = {
    "task1": {"name": "Ada Lovelace", "email": "ada@example.com",
              "city": "Hanoi", "country": "VN", "plan": "pro"},
    "task2": {"category": "Books"},
    "task3": {"email": "user@example.com", "password": "longenough1",
              "name": "Test User", "age": "30"},
    "task4": {"notify": True, "dark": True, "lang": "vi",
              "volume": 70, "font": "16"},
    "task5": {"title": "Release notes", "action": "save"},
    "task6": {"items": {"Keyboard": 2, "Mouse": 1}, "code": "SAVE10"},
}


def task1(s, g):
    # Fill each field whose observed value differs from the goal,
    # one observation before each action, then submit.
    obs = s.observe()
    f = input_by_label(obs, "Full name")
    if f["value"] != g["name"]:
        s.type_into(f["id"], g["name"])
    obs = s.observe()
    f = input_by_label(obs, "Email")
    if f["value"] != g["email"]:
        s.type_into(f["id"], g["email"])
    obs = s.observe()
    f = input_by_label(obs, "City")
    if f["value"] != g["city"]:
        s.type_into(f["id"], g["city"])
    obs = s.observe()
    sel = next(i for i in obs["inputs"] if i["tag"] == "select")
    opt = next(o for o in sel["options"] if o["value"] == g["country"])
    if not opt["selected"]:
        s.select_value(sel["id"], opt["value"])
    obs = s.observe()
    radio = next(i for i in obs["inputs"]
                 if i["type"] == "radio" and i["value"] == g["plan"])
    if not radio["checked"]:
        s.click(radio["id"])
    obs = s.observe()
    agree = next(i for i in obs["inputs"]
                 if i["type"] == "checkbox" and "agree" in i["label"].lower())
    if not agree["checked"]:
        s.click(agree["id"])
    for _attempt in range(3):
        obs = s.observe()
        btn = button_by_label(obs, "Register")
        s.click(btn["id"])
        obs = s.observe()
        if not active_errors(obs):
            return
        # Validation bounced: count a retry, fix the first field
        # whose observed value still mismatches the goal, resubmit.
        s.retries += 1
        fixers = (("Full name", g["name"]), ("Email", g["email"]),
                  ("City", g["city"]))
        for label, want in fixers:
            f = input_by_label(obs, label)
            if f is not None and f["value"] != want:
                s.type_into(f["id"], want)
                break


def task2(s, g):
    obs = s.observe()
    sel = next(i for i in obs["inputs"] if i["tag"] == "select"
               and any(o["value"] == g["category"] for o in i["options"]))
    s.select_value(sel["id"], g["category"])
    obs = s.observe()
    # Sort only after filtering: the observation shows the filtered
    # row count, and sorting the filtered view is what the goal asks.
    btn = button_by_label(obs, "Sort by amount")
    s.click(btn["id"])


def task3(s, g):
    obs = s.observe()
    # Read the prefilled values BEFORE advancing. The email lacks
    # an @ sign and the page hint in the observed text states the
    # password minimum; both defects are fixed up front, so the
    # Next click does not bounce. No retry is spent.
    email = input_by_label(obs, "Email")
    if "@" not in email["value"]:
        s.type_into(email["id"], g["email"])
    obs = s.observe()
    pw = next(i for i in obs["inputs"] if i["type"] == "password")
    m = re.search(r"at least (\d+) characters", obs["text"])
    minimum = int(m.group(1)) if m else 8
    if len(pw["value"]) < minimum:
        s.type_into(pw["id"], g["password"])
    for _attempt in range(3):
        obs = s.observe()
        nxt = button_by_context(obs, "Step 1", "Next")
        s.click(nxt["id"])
        obs = s.observe()
        errs = active_errors(obs)
        if not errs:
            break
        s.retries += 1
        msg = errs[0]["text"]
        if "@" in msg:
            f = input_by_label(obs, "Email")
            s.type_into(f["id"], g["email"])
        elif "Password" in msg:
            f = next(i for i in obs["inputs"] if i["type"] == "password")
            s.type_into(f["id"], g["password"])
    obs = s.observe()
    f = input_by_label(obs, "Display name")
    if f["value"] != g["name"]:
        s.type_into(f["id"], g["name"])
    obs = s.observe()
    f = input_by_label(obs, "Age")
    if f["value"] != g["age"]:
        s.type_into(f["id"], g["age"])
    for _attempt in range(3):
        obs = s.observe()
        nxt = button_by_context(obs, "Step 2", "Next")
        s.click(nxt["id"])
        obs = s.observe()
        if not active_errors(obs):
            break
        s.retries += 1
        f = input_by_label(obs, "Display name")
        if f is not None and f["value"] != g["name"]:
            s.type_into(f["id"], g["name"])
        f = input_by_label(obs, "Age")
        if f is not None and f["value"] != g["age"]:
            s.type_into(f["id"], g["age"])
    obs = s.observe()
    btn = button_by_label(obs, "Confirm")
    s.click(btn["id"])


def task4(s, g):
    obs = s.observe()
    box = next(i for i in obs["inputs"] if i["type"] == "checkbox"
               and "notifications" in i["label"].lower())
    if box["checked"] != g["notify"]:
        s.click(box["id"])
    obs = s.observe()
    box = next(i for i in obs["inputs"] if i["type"] == "checkbox"
               and "dark" in i["label"].lower())
    if box["checked"] != g["dark"]:
        s.click(box["id"])
    obs = s.observe()
    sel = input_by_label(obs, "Language")
    opt = next(o for o in sel["options"] if o["value"] == g["lang"])
    if not opt["selected"]:
        s.select_value(sel["id"], opt["value"])
    obs = s.observe()
    rng = next(i for i in obs["inputs"] if i["type"] == "range")
    if int(rng["value"]) != g["volume"]:
        s.set_range(rng["id"], g["volume"])
    obs = s.observe()
    font = input_by_label(obs, "Font size")
    if font["value"] != g["font"]:
        s.type_into(font["id"], g["font"])
    obs = s.observe()
    btn = button_by_label(obs, "Save")
    s.click(btn["id"])


def task5(s, g):
    obs = s.observe()
    f = input_by_label(obs, "Title")
    if f["value"] != g["title"]:
        s.type_into(f["id"], g["title"])
    for _attempt in range(2):
        obs = s.observe()
        # Choose by observed data-action, not by label or styling:
        # the big primary button labelled Publish now carries
        # data-action archive in this very payload, which does not
        # match the goal action save. The plain button whose
        # data-action is save is the one that saves the draft.
        btn = next(b for b in obs["buttons"]
                   if b["dataAction"] == g["action"])
        s.click(btn["id"])
        obs = s.observe()
        if "Draft saved." in obs["text"]:
            return
        # The click did not save (should not happen): count a
        # retry, reload the fixture, redo title and save.
        s.retries += 1
        s.driver.get(fixture_uri(FIXTURE_OF["task5"]))
        obs = s.observe()
        f = input_by_label(obs, "Title")
        s.type_into(f["id"], g["title"])


def cart_qty(obs, name):
    m = re.search(re.escape(name) + r" x (\d+)", obs["text"])
    return int(m.group(1)) if m else 0


def task6(s, g):
    for name, want in g["items"].items():
        while True:
            obs = s.observe()
            if cart_qty(obs, name) >= want:
                break
            btn = button_by_context(obs, name, "Add")
            s.click(btn["id"])
    obs = s.observe()
    f = input_by_label(obs, "Discount code")
    if f["value"] != g["code"]:
        s.type_into(f["id"], g["code"])
    obs = s.observe()
    btn = button_by_label(obs, "Apply")
    s.click(btn["id"])
    obs = s.observe()
    if "Invalid code." in obs["text"]:
        s.retries += 1
        f = input_by_label(obs, "Discount code")
        s.type_into(f["id"], g["code"])
        obs = s.observe()
        btn = button_by_label(obs, "Apply")
        s.click(btn["id"])


TASKS = {"task1": task1, "task2": task2, "task3": task3,
         "task4": task4, "task5": task5, "task6": task6}


def main():
    task_id = sys.argv[1]
    s = A2Session(task_id)
    s.start(FIXTURE_OF[task_id])
    TASKS[task_id](s, GOALS[task_id])
    ok, detail = CHECKS[task_id](s)
    return s.finish(ok, detail)


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)

#!/usr/bin/env python3
"""Programmatic checkers for experiment 3.4.1 E1.

The SAME checker judges both arms, reading the final DOM state.
Expected values live here, written from the task goals, not from
either arm's script.
"""

import json


def check_task1(s):
    ok = (
        s.text_of("success-title") == "Registered: Ada Lovelace"
        and s.text_of("s-name") == "Ada Lovelace"
        and s.text_of("s-email") == "ada@example.com"
        and s.text_of("s-city") == "Hanoi"
        and s.text_of("s-country") == "VN"
        and s.text_of("s-plan") == "pro"
    )
    return ok, "success panel fields"


def check_task2(s):
    rows = s.read(
        "return Array.prototype.map.call(document.querySelectorAll('#rows tr'),"
        " function (tr) { var td = tr.querySelectorAll('td');"
        " return [td[0].textContent, td[1].textContent, parseInt(td[2].textContent, 10)]; });")
    expected = [["Textbook", "Books", 120], ["Atlas", "Books", 90],
                ["Comic", "Books", 55], ["Novel A", "Books", 45],
                ["Novel B", "Books", 30], ["Poetry", "Books", 15]]
    return rows == expected, f"visible rows={rows}"


def check_task3(s):
    ok = (
        s.text_of("done-code") == "ACC-2026-OK"
        and s.text_of("done-email") == "user@example.com"
    )
    return ok, "confirmation code and corrected email"


def check_task4(s):
    raw = s.read("return document.getElementById('saved').textContent;")
    try:
        state = json.loads(raw)
    except Exception:
        return False, f"saved not JSON: {raw!r}"
    expected = {"notify": True, "dark": True, "lang": "vi", "volume": 70, "font": 16}
    return state == expected, f"saved={state}"


def check_task5(s):
    state = s.read("return window.__draftState;")
    status = s.text_of("status")
    ok = (
        state.get("saved") is True
        and state.get("archived") is False
        and state.get("deleted") is False
        and state.get("title") == "Release notes"
        and status == "Draft saved."
    )
    return ok, f"draft state={state} status={status!r}"


def check_task6(s):
    subtotal = s.text_of("subtotal")
    discount = s.text_of("discount")
    total = s.text_of("total")
    # Goal state: Keyboard x2 (100.00) + Mouse x1 (25.00) = 125.00,
    # SAVE10 discount 12.50, total 112.50.
    ok = subtotal == "125.00" and discount == "12.50" and total == "112.50"
    return ok, f"subtotal={subtotal} discount={discount} total={total}"


CHECKS = {
    "task1": check_task1,
    "task2": check_task2,
    "task3": check_task3,
    "task4": check_task4,
    "task5": check_task5,
    "task6": check_task6,
}

#!/usr/bin/env python3
"""Test 04, kanban drag and drop with persistence.

Drives the offline kanban fixture in a real browser. Cards are
dragged between columns, a card is added through the form, the page
is reloaded to prove localStorage persistence, and reset restores
the initial board. Dragging is attempted first with Selenium
ActionChains drag_and_drop. If the HTML5 drag does not take effect
in this browser, the fixture helper __kanbanSimulateDrag is used,
which dispatches the same dragstart, dragover, drop, dragend event
sequence through the board's own handlers. Which mechanism actually
moved the cards is recorded in the run output and in the spec.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness import BrowserCase, fixture_uri

FIXTURE = "test04_kanban_drag_drop.html"
INITIAL_IDS = {
    "todo": ["card-1", "card-2", "card-3"],
    "doing": ["card-4", "card-5"],
    "done": ["card-6"],
}
MECH = {"actionchains_moves": 0, "fallback_moves": 0}


def get_state(driver):
    # The pre element is display none, so element.text is empty by
    # WebDriver visibility rules. Read its textContent from the DOM.
    raw = driver.execute_script(
        "return document.getElementById('board-state-json').textContent;")
    return json.loads(raw)


def ids_of(state, col):
    return [c["id"] for c in state[col]]


def dom_counter(driver, col):
    return int(driver.find_element("id", f"count-{col}").text)


def dom_card_count(driver, col):
    return len(driver.find_elements("css selector", f"#list-{col} .card"))


def do_drag(driver, card_id, target_col):
    """Try ActionChains first, fall back to the fixture JS helper.

    Returns the mechanism that actually moved the card.
    """
    source = driver.find_element("id", card_id)
    target = driver.find_element("id", f"list-{target_col}")
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).drag_and_drop(source, target).perform()
    except Exception:
        pass
    time.sleep(0.3)
    if card_id in ids_of(get_state(driver), target_col):
        MECH["actionchains_moves"] += 1
        return "actionchains"
    driver.execute_script(
        "return window.__kanbanSimulateDrag(arguments[0], arguments[1]);",
        card_id, target_col)
    time.sleep(0.3)
    if card_id in ids_of(get_state(driver), target_col):
        MECH["fallback_moves"] += 1
        return "js-fallback"
    raise RuntimeError(f"drag of {card_id} to {target_col} did not take effect")


def mechanism_summary():
    if MECH["fallback_moves"] == 0:
        return "actionchains drag_and_drop for all drags"
    if MECH["actionchains_moves"] == 0:
        return ("actionchains attempted first and did not move cards, "
                "js-fallback __kanbanSimulateDrag moved all cards")
    return ("mixed, actionchains moved "
            f"{MECH['actionchains_moves']} cards and js-fallback moved "
            f"{MECH['fallback_moves']} cards")


def main():
    case = BrowserCase("test04", "kanban drag and drop with persistence")
    driver = case.start_browser()
    holder = {}

    case.step("load_page",
              lambda: {"title": (driver.get(fixture_uri(FIXTURE)),
                                 driver.title)[1]})

    def read_initial():
        holder["initial"] = get_state(driver)
        return holder["initial"]
    case.step("read_initial_state", read_initial)
    case.check("initial_state_counts",
               {k: len(v) for k, v in holder["initial"].items()}
               == {"todo": 3, "doing": 2, "done": 1},
               str({k: len(v) for k, v in holder["initial"].items()}))
    case.check("initial_state_ids_exact",
               {k: ids_of(holder["initial"], k) for k in INITIAL_IDS}
               == INITIAL_IDS)

    case.step("verify_initial_dom_cards",
              lambda: {c: dom_card_count(driver, c)
                       for c in ("todo", "doing", "done")})
    case.check("initial_dom_card_counts",
               (dom_card_count(driver, "todo"),
                dom_card_count(driver, "doing"),
                dom_card_count(driver, "done")) == (3, 2, 1))

    case.step("verify_initial_counters",
              lambda: {c: dom_counter(driver, c)
                       for c in ("todo", "doing", "done")})
    case.check("initial_counters_match",
               (dom_counter(driver, "todo"), dom_counter(driver, "doing"),
                dom_counter(driver, "done")) == (3, 2, 1))

    mech1 = case.step("drag_card2_todo_to_doing",
                      lambda: {"mechanism": do_drag(driver, "card-2", "doing")})
    holder["after_drag1"] = case.step("verify_state_after_drag1",
                                      lambda: get_state(driver))
    case.check("drag1_state_ids",
               ids_of(holder["after_drag1"], "todo") == ["card-1", "card-3"]
               and ids_of(holder["after_drag1"], "doing")
               == ["card-4", "card-5", "card-2"],
               str(holder["after_drag1"]))
    case.step("verify_counters_after_drag1",
              lambda: {c: dom_counter(driver, c)
                       for c in ("todo", "doing", "done")})
    case.check("drag1_counters_dom",
               (dom_counter(driver, "todo"), dom_counter(driver, "doing"),
                dom_counter(driver, "done")) == (2, 3, 1))

    mech2 = case.step("drag_card4_doing_to_done",
                      lambda: {"mechanism": do_drag(driver, "card-4", "done")})
    holder["after_drag2"] = case.step("verify_state_after_drag2",
                                      lambda: get_state(driver))
    case.check("drag2_state_ids",
               ids_of(holder["after_drag2"], "doing") == ["card-5", "card-2"]
               and ids_of(holder["after_drag2"], "done")
               == ["card-6", "card-4"],
               str(holder["after_drag2"]))

    mech3 = case.step("drag_card6_done_back_to_todo",
                      lambda: {"mechanism": do_drag(driver, "card-6", "todo")})
    holder["after_back"] = case.step("verify_state_after_drag_back",
                                     lambda: get_state(driver))
    case.check("drag_back_state_ids",
               ids_of(holder["after_back"], "done") == ["card-4"]
               and ids_of(holder["after_back"], "todo")
               == ["card-1", "card-3", "card-6"],
               str(holder["after_back"]))
    case.step("verify_counters_after_drag_back",
              lambda: {c: dom_counter(driver, c)
                       for c in ("todo", "doing", "done")})
    case.check("counters_after_drag_back",
               (dom_counter(driver, "todo"), dom_counter(driver, "doing"),
                dom_counter(driver, "done")) == (3, 2, 1))

    def add_card():
        box = driver.find_element("id", "new-card-title")
        box.clear()
        box.send_keys("New test card")
        driver.find_element("id", "add-card-btn").click()
        time.sleep(0.3)
        return {"state": get_state(driver)}
    case.step("add_card_via_form", add_card)
    holder["after_add"] = case.step("verify_new_card_state_and_dom",
                                    lambda: get_state(driver))
    todo_cards = holder["after_add"]["todo"]
    case.check("new_card_in_state_todo",
               todo_cards[-1]["title"] == "New test card"
               and todo_cards[-1]["id"] == "card-7",
               str(todo_cards[-1] if todo_cards else None))
    case.check("new_card_in_dom",
               driver.find_element("id", "card-7").text == "New test card")

    case.step("reload_page", lambda: {"title": (driver.refresh(),
                                                 driver.title)[1]})
    holder["after_reload"] = case.step(
        "verify_state_persisted_after_reload", lambda: get_state(driver))
    case.check("state_persisted_after_reload",
               holder["after_reload"] == holder["after_add"],
               "reloaded state equals pre reload state")
    case.check("counters_persisted_after_reload",
               (dom_counter(driver, "todo"), dom_counter(driver, "doing"),
                dom_counter(driver, "done")) == (4, 2, 1))

    case.step("click_reset",
              lambda: (driver.find_element("id", "reset-btn").click(),
                       time.sleep(0.3), {"clicked": True})[2])
    holder["after_reset"] = case.step("verify_initial_state_restored",
                                      lambda: get_state(driver))
    case.check("reset_state_restored",
               {k: ids_of(holder["after_reset"], k) for k in INITIAL_IDS}
               == INITIAL_IDS,
               str(holder["after_reset"]))

    def storage_and_counters():
        stored = driver.execute_script(
            "return localStorage.getItem('kanban-board-v1');")
        return {"stored": stored,
                "counters": {c: dom_counter(driver, c)
                             for c in ("todo", "doing", "done")}}
    holder["final"] = case.step("verify_storage_cleared_and_counters_restored",
                                storage_and_counters)
    case.check("storage_cleared_after_reset",
               holder["final"]["stored"] is None,
               f"stored={holder['final']['stored']}")
    case.check("counters_restored_after_reset",
               (dom_counter(driver, "todo"), dom_counter(driver, "doing"),
                dom_counter(driver, "done")) == (3, 2, 1))

    summary = mechanism_summary()
    print(f"DRAG_MECHANISM {summary} attempts: {mech1}, {mech2}, {mech3}",
          flush=True)
    case.check("drag_mechanism_recorded",
               MECH["actionchains_moves"] + MECH["fallback_moves"] == 3,
               summary)
    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

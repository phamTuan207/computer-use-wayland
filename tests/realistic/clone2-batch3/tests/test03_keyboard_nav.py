#!/usr/bin/env python3
"""Test 03, keyboard only navigation through a checkout style flow.

The whole task is done with the keyboard: Tab and Shift Tab to
move, Enter and Space to activate, arrow keys inside the radio
group, and plain typing into whichever field holds focus. The
fixture shows the id of the focused element on the page, and the
test reads that indicator to prove where focus really is at every
stop. No mouse press API is used anywhere in this file, and the
last step proves it by scanning this source.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness import BrowserCase, fixture_uri

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

NAME = "Test Buyer"
EMAIL = "buyer@example.test"


def readout(driver):
    return driver.find_element(By.ID, "focus-readout").text.strip()


def active(driver):
    return driver.switch_to.active_element


def tab(driver, count=1):
    for _ in range(count):
        active(driver).send_keys(Keys.TAB)
        time.sleep(0.06)


def shift_tab(driver):
    from selenium.webdriver.common.action_chains import ActionChains
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(
        Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(0.06)


def press(driver, key):
    active(driver).send_keys(key)
    time.sleep(0.06)


def main():
    case = BrowserCase("test03", "keyboard only navigation, checkout flow")
    try:
        case.start_browser()
        d = case.driver

        case.step("load_fixture",
                  lambda: {"title": (d.get(fixture_uri(
                      "test03_keyboard_nav.html")), d.title)[1]})

        def initial_focus():
            value = readout(d)
            case.check("initial_focus_none", value == "none", value)
            return {"readout": value}
        case.step("verify_initial_focus", initial_focus)

        def first_nav():
            tab(d)
            value = readout(d)
            case.check("first_tab_lands_nav_home", value == "nav-home", value)
            return {"readout": value}
        case.step("tab_to_first_nav_link", first_nav)

        def nav_rest():
            seen = []
            for want in ("nav-products", "nav-help", "nav-contact"):
                tab(d)
                value = readout(d)
                seen.append(value)
                case.check(f"tab_reaches_{want}", value == want, value)
            return {"order": seen}
        case.step("tab_through_nav_in_order", nav_rest)

        def back_one():
            shift_tab(d)
            value = readout(d)
            case.check("shift_tab_back_to_nav_help", value == "nav-help", value)
            return {"readout": value}
        case.step("shift_tab_back_one_stop", back_one)

        def forward_again():
            tab(d)
            value = readout(d)
            case.check("tab_forward_to_nav_contact",
                       value == "nav-contact", value)
            return {"readout": value}
        case.step("tab_forward_again", forward_again)

        def name_field():
            tab(d)
            value = readout(d)
            case.check("tab_lands_field_name", value == "field-name", value)
            active(d).send_keys(NAME)
            typed = d.find_element(By.ID, "field-name").get_attribute("value")
            case.check("name_typed_into_focused_field", typed == NAME, typed)
            return {"value": typed}
        case.step("tab_to_name_and_type", name_field)

        def email_field():
            tab(d)
            value = readout(d)
            case.check("tab_lands_field_email", value == "field-email", value)
            active(d).send_keys(EMAIL)
            typed = d.find_element(By.ID, "field-email").get_attribute("value")
            case.check("email_typed_into_focused_field", typed == EMAIL, typed)
            return {"value": typed}
        case.step("tab_to_email_and_type", email_field)

        def qty_field():
            tab(d)
            value = readout(d)
            case.check("tab_lands_field_qty", value == "field-qty", value)
            active(d).send_keys("3")
            typed = d.find_element(By.ID, "field-qty").get_attribute("value")
            case.check("quantity_set_to_3", typed == "3", typed)
            return {"value": typed}
        case.step("tab_to_qty_and_set", qty_field)

        def radio_choice():
            tab(d)
            value = readout(d)
            case.check("tab_lands_checked_radio", value == "ship-std", value)
            press(d, Keys.ARROW_DOWN)
            value = readout(d)
            chosen = d.find_element(By.ID, "ship-exp").is_selected()
            case.check("arrow_down_focuses_express", value == "ship-exp", value)
            case.check("express_radio_selected", chosen)
            return {"readout": value, "express_selected": chosen}
        case.step("tab_to_radio_and_choose_express", radio_choice)

        def accordion_enter():
            tab(d)
            value = readout(d)
            case.check("tab_lands_acc_btn_1", value == "acc-btn-1", value)
            press(d, Keys.ENTER)
            panel = d.find_element(By.ID, "acc-panel-1")
            expanded = d.find_element(
                By.ID, "acc-btn-1").get_attribute("aria-expanded")
            case.check("accordion_1_expanded_by_enter",
                       panel.is_displayed() and expanded == "true",
                       f"displayed={panel.is_displayed()} expanded={expanded}")
            return {"expanded": expanded}
        case.step("tab_to_accordion_expand_with_enter", accordion_enter)

        def accordion_space():
            tab(d)
            value = readout(d)
            case.check("tab_lands_acc_btn_2", value == "acc-btn-2", value)
            press(d, Keys.SPACE)
            panel = d.find_element(By.ID, "acc-panel-2")
            case.check("accordion_2_expanded_by_space", panel.is_displayed())
            return {"displayed": panel.is_displayed()}
        case.step("tab_to_accordion_2_expand_with_space", accordion_space)

        def first_row():
            tab(d, 2)
            value = readout(d)
            case.check("tab_lands_row_1", value == "row-1", value)
            return {"readout": value}
        case.step("tab_to_first_table_row", first_row)

        def select_row():
            tab(d)
            value = readout(d)
            case.check("tab_lands_row_2", value == "row-2", value)
            press(d, Keys.ENTER)
            chosen = d.find_element(By.ID, "selected-readout").text.strip()
            klass = d.find_element(By.ID, "row-2").get_attribute("class")
            case.check("row_2_selected_by_enter", chosen == "row-2", chosen)
            case.check("row_2_has_selected_class", "selected" in klass, klass)
            return {"selected": chosen}
        case.step("tab_to_row_2_and_select_with_enter", select_row)

        def to_checkbox():
            tab(d, 2)
            value = readout(d)
            case.check("tab_lands_confirm_check",
                       value == "confirm-check", value)
            return {"readout": value}
        case.step("tab_to_confirm_checkbox", to_checkbox)

        def invalid_submit():
            tab(d)
            value = readout(d)
            case.check("tab_lands_submit_btn", value == "submit-btn", value)
            press(d, Keys.ENTER)
            error = d.find_element(By.ID, "form-error")
            case.check("error_shown_for_unchecked_terms",
                       error.is_displayed() and "agree" in error.text,
                       error.text)
            value = readout(d)
            case.check("focus_moved_to_first_invalid_field",
                       value == "confirm-check", value)
            return {"error": error.text, "focus_now": value}
        case.step("tab_to_submit_attempt_invalid", invalid_submit)

        def toggle_checkbox():
            press(d, Keys.SPACE)
            chosen = d.find_element(By.ID, "confirm-check").is_selected()
            case.check("checkbox_toggled_by_space", chosen)
            return {"checked": chosen}
        case.step("toggle_checkbox_with_space", toggle_checkbox)

        def good_submit():
            tab(d)
            value = readout(d)
            case.check("tab_lands_submit_btn_again",
                       value == "submit-btn", value)
            press(d, Keys.ENTER)
            success = d.find_element(By.ID, "success-message")
            case.check("success_message_shown", success.is_displayed(),
                       success.text)
            case.check("success_names_buyer_and_row",
                       NAME in success.text and "row-2" in success.text,
                       success.text)
            return {"success": success.text}
        case.step("tab_to_submit_and_succeed", good_submit)

        def final_state():
            success = d.find_element(By.ID, "success-message")
            chosen = d.find_element(By.ID, "selected-readout").text.strip()
            email = d.find_element(By.ID, "field-email").get_attribute("value")
            case.check("final_success_still_visible", success.is_displayed())
            case.check("final_selected_row_kept", chosen == "row-2", chosen)
            case.check("final_email_kept", email == EMAIL, email)
            return {"selected": chosen, "email": email}
        case.step("verify_final_state", final_state)

        def source_self_check():
            source = Path(__file__).read_text(encoding="utf-8")
            needle = ".cli" + "ck("
            found = needle in source
            case.check("no_mouse_press_api_in_test_source", not found)
            return {"needle_found": found}
        case.step("self_check_source_has_no_mouse_press", source_self_check)

    except Exception as exc:
        print(f"  test03 aborted: {type(exc).__name__}: {exc}", flush=True)
    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

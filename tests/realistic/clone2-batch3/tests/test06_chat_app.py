#!/usr/bin/env python3
"""Test 06, chat app: conversations, bot replies, search, badges.

Drives the offline chat fixture in a real browser through Selenium:
seeded history, an unread badge that clears on open, sending two
messages (button click and Enter), a bot that replies after about
800 ms with a typing indicator, message search with highlight and
count, and conversation switching with history persistence. Waits
poll the DOM with deadlines instead of fixed long sleeps.
"""

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness import BrowserCase, fixture_uri

TEXT1 = "Hello, this is the first test message"
TEXT2 = "Second message about the weekend plan"
REPLY1 = 'Bot reply: I received "' + TEXT1 + '" and noted it.'
REPLY2 = 'Bot reply: I received "' + TEXT2 + '" and noted it.'
FIRST_SEEDED = "Morning, the design draft is ready"
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def snapshot(driver):
    return driver.execute_script(
        "return Array.prototype.map.call("
        "document.querySelectorAll('#messages .msg'), function (m) {"
        "  var status = m.querySelector('.msg-status');"
        "  return {text: m.querySelector('.msg-text').textContent,"
        "          dir: m.getAttribute('data-dir'),"
        "          time: m.querySelector('.msg-time').textContent,"
        "          status: status ? status.textContent : '',"
        "          history: m.getAttribute('data-status-history') || ''};"
        "});")


def text_of(driver, element_id):
    return driver.find_element("id", element_id).text


def wait_for_count(driver, target, timeout=15.0):
    deadline = time.time() + timeout
    snap = snapshot(driver)
    while len(snap) < target and time.time() < deadline:
        time.sleep(0.1)
        snap = snapshot(driver)
    return snap


def wait_for_visible(driver, target, timeout=5.0):
    deadline = time.time() + timeout
    snap = snapshot(driver)
    while len(snap) != target and time.time() < deadline:
        time.sleep(0.1)
        snap = snapshot(driver)
    return snap


def main():
    case = BrowserCase("test06", "chat app, bot replies, search, badges")
    driver = case.start_browser()
    driver.set_script_timeout(20)

    case.step("load_fixture",
              lambda: driver.get(fixture_uri("test06_chat_app.html")))

    def verify_contacts():
        items = driver.find_elements("css selector", ".contact")
        names = [i.find_element("css selector", ".contact-name").text
                 for i in items]
        case.check("three_contacts", len(items) == 3, f"count {len(items)}")
        case.check("contact_names",
                   names == ["Lan Anh", "Minh Duc", "Hoang Nam"],
                   f"names {names}")
        case.check("chat_title_first_contact",
                   text_of(driver, "chat-title") == "Lan Anh",
                   text_of(driver, "chat-title"))
        return {"names": names}
    case.step("verify_contact_list", verify_contacts)

    def verify_seeded():
        snap = snapshot(driver)
        dirs = [m["dir"] for m in snap]
        case.check("seeded_count_5", len(snap) == 5, f"count {len(snap)}")
        case.check("first_message_text", snap[0]["text"] == FIRST_SEEDED,
                   snap[0]["text"])
        case.check("seeded_mix_in_and_out",
                   "in" in dirs and "out" in dirs, f"dirs {dirs}")
        case.check("seeded_timestamps",
                   all(TIME_RE.match(m["time"]) for m in snap),
                   [m["time"] for m in snap])
        return {"count": len(snap)}
    case.step("verify_seeded_history", verify_seeded)

    def verify_badge():
        badge = driver.find_element("id", "badge-c2")
        case.check("badge_c2_visible", badge.is_displayed())
        case.check("badge_c2_count_2", badge.text == "2", badge.text)
        return {"badge": badge.text}
    case.step("verify_unread_badge", verify_badge)

    def type_first():
        box = driver.find_element("id", "msg-input")
        box.click()
        box.send_keys(TEXT1)
        counter = text_of(driver, "char-count")
        case.check("counter_counts_typed_text",
                   counter == f"{len(TEXT1)} / 500", counter)
        return {"counter": counter}
    case.step("type_first_message", type_first)

    def send_first():
        driver.find_element("id", "send-btn").click()
        snap = wait_for_count(driver, 6)
        mine = [m for m in snap if m["text"] == TEXT1]
        counter = text_of(driver, "char-count")
        box_value = driver.find_element("id", "msg-input") \
            .get_attribute("value")
        case.check("first_message_appears", len(mine) == 1,
                   f"matches {len(mine)}")
        case.check("counter_resets_after_send", counter == "0 / 500",
                   counter)
        case.check("input_cleared_after_send", box_value == "", box_value)
        return {"count": len(snap)}
    case.step("send_first_message", send_first)

    def wait_reply1():
        snap = wait_for_count(driver, 7)
        shown = driver.execute_script(
            "return document.body.getAttribute('data-typing-shown');")
        last = snap[-1] if snap else {}
        mine = [m for m in snap if m["text"] == TEXT1]
        case.check("reply1_arrives", len(snap) == 7, f"count {len(snap)}")
        case.check("typing_indicator_was_shown", str(shown) == "1",
                   f"typing shown count {shown}")
        case.check("reply1_references_sent_text",
                   last.get("text") == REPLY1 and last.get("dir") == "in",
                   last.get("text", ""))
        case.check("first_message_status_sent",
                   mine and mine[0]["status"] == "sent"
                   and mine[0]["history"] == "sending>sent",
                   mine[0] if mine else "missing")
        return {"last": last.get("text", "")}
    case.step("wait_first_bot_reply", wait_reply1)

    def type_second():
        box = driver.find_element("id", "msg-input")
        box.click()
        box.send_keys(TEXT2)
        counter = text_of(driver, "char-count")
        case.check("counter_counts_second_text",
                   counter == f"{len(TEXT2)} / 500", counter)
        return {"counter": counter}
    case.step("type_second_message", type_second)

    def send_second_enter():
        from selenium.webdriver.common.keys import Keys
        driver.find_element("id", "msg-input").send_keys(Keys.ENTER)
        snap = wait_for_count(driver, 8)
        mine = [m for m in snap if m["text"] == TEXT2]
        case.check("second_message_appears_via_enter", len(mine) == 1,
                   f"matches {len(mine)}")
        return {"count": len(snap)}
    case.step("send_second_message_enter", send_second_enter)

    def wait_reply2():
        snap = wait_for_count(driver, 9)
        shown = driver.execute_script(
            "return document.body.getAttribute('data-typing-shown');")
        last = snap[-1] if snap else {}
        case.check("history_grows_to_9", len(snap) == 9,
                   f"count {len(snap)}")
        case.check("typing_indicator_shown_twice", str(shown) == "2",
                   f"typing shown count {shown}")
        case.check("reply2_references_second_text",
                   last.get("text") == REPLY2, last.get("text", ""))
        return {"last": last.get("text", "")}
    case.step("wait_second_bot_reply", wait_reply2)

    def search_draft():
        box = driver.find_element("id", "search-input")
        box.click()
        box.send_keys("draft")
        snap = wait_for_visible(driver, 2)
        count_label = text_of(driver, "search-count")
        marks = driver.find_elements("css selector", "#messages mark.hl")
        case.check("search_filters_to_2", len(snap) == 2,
                   f"visible {len(snap)}")
        case.check("search_count_label_2", count_label == "2 matches",
                   count_label)
        case.check("search_highlights_2", len(marks) == 2,
                   f"marks {len(marks)}")
        return {"visible": len(snap), "label": count_label}
    case.step("search_for_draft", search_draft)

    def clear_search():
        box = driver.find_element("id", "search-input")
        box.clear()
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input',"
            " {bubbles: true}));", box)
        snap = wait_for_visible(driver, 9)
        marks = driver.find_elements("css selector", "#messages mark.hl")
        case.check("clear_search_restores_9", len(snap) == 9,
                   f"visible {len(snap)}")
        case.check("clear_search_removes_highlights", len(marks) == 0,
                   f"marks {len(marks)}")
        return {"visible": len(snap)}
    case.step("clear_search", clear_search)

    def search_no_match():
        box = driver.find_element("id", "search-input")
        box.click()
        box.send_keys("zebra")
        snap = wait_for_visible(driver, 0)
        count_label = text_of(driver, "search-count")
        case.check("no_match_shows_0", len(snap) == 0,
                   f"visible {len(snap)}")
        case.check("no_match_count_label", count_label == "0 matches",
                   count_label)
        return {"visible": len(snap), "label": count_label}
    case.step("search_no_match", search_no_match)

    def clear_search_again():
        box = driver.find_element("id", "search-input")
        box.clear()
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input',"
            " {bubbles: true}));", box)
        snap = wait_for_visible(driver, 9)
        case.check("second_clear_restores_9", len(snap) == 9,
                   f"visible {len(snap)}")
        return {"visible": len(snap)}
    case.step("clear_search_again", clear_search_again)

    def open_contact2():
        driver.find_element(
            "css selector", '.contact[data-contact="c2"]').click()
        snap = snapshot(driver)
        badge = driver.find_element("id", "badge-c2")
        case.check("badge_cleared_on_open", not badge.is_displayed())
        case.check("contact2_title",
                   text_of(driver, "chat-title") == "Minh Duc",
                   text_of(driver, "chat-title"))
        case.check("contact2_history_2", len(snap) == 2,
                   f"count {len(snap)}")
        case.check("contact2_first_text",
                   snap[0]["text"] == "Lunch tomorrow at noon?",
                   snap[0]["text"])
        return {"count": len(snap)}
    case.step("open_contact_2", open_contact2)

    def open_contact3():
        driver.find_element(
            "css selector", '.contact[data-contact="c3"]').click()
        snap = snapshot(driver)
        empty = driver.find_elements("id", "empty-state")
        case.check("contact3_no_messages", len(snap) == 0,
                   f"count {len(snap)}")
        case.check("contact3_empty_state_shown",
                   len(empty) == 1 and empty[0].is_displayed()
                   and "No messages yet" in empty[0].text,
                   empty[0].text if empty else "missing")
        case.check("contact3_title",
                   text_of(driver, "chat-title") == "Hoang Nam",
                   text_of(driver, "chat-title"))
        return {"count": len(snap)}
    case.step("open_contact_3", open_contact3)

    def back_to_contact1():
        driver.find_element(
            "css selector", '.contact[data-contact="c1"]').click()
        snap = snapshot(driver)
        texts = [m["text"] for m in snap]
        case.check("history_persists_9", len(snap) == 9,
                   f"count {len(snap)}")
        case.check("sent_texts_persist",
                   TEXT1 in texts and TEXT2 in texts, f"texts {len(texts)}")
        case.check("replies_persist",
                   REPLY1 in texts and REPLY2 in texts)
        case.check("first_message_still_seeded",
                   texts[0] == FIRST_SEEDED, texts[0])
        return {"count": len(snap)}
    case.step("back_to_contact_1", back_to_contact1)

    def verify_timestamps():
        snap = snapshot(driver)
        bad = [m["time"] for m in snap if not TIME_RE.match(m["time"])]
        case.check("all_messages_have_timestamps", bad == [],
                   f"bad {bad}")
        return {"checked": len(snap)}
    case.step("verify_all_timestamps", verify_timestamps)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

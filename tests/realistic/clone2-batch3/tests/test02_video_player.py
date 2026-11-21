#!/usr/bin/env python3
"""Test 02, video player: control a simulated player end to end.

Drives the offline fixture in a real browser through Selenium:
play, pause, seek, volume, mute, playback speed, subtitles in two
languages, and a 3 item playlist, verifying DOM state after every
action. Playback is a JS clock in the fixture, no real media.
Timing assertions use tolerant ranges so the test is not flaky.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness import BrowserCase, fixture_uri

EN_CAPTION = "This segment explains the basics."
VI_CAPTION = "Phan nay giai thich cac kien thuc co ban."


def player(driver):
    return driver.find_element("id", "player")


def current_seconds(driver):
    return float(player(driver).get_attribute("data-current-seconds"))


def text_of(driver, element_id):
    return driver.find_element("id", element_id).text


def set_range(driver, element_id, value):
    driver.execute_script(
        "var el = document.getElementById(arguments[0]);"
        "el.value = arguments[1];"
        "el.dispatchEvent(new Event('input', {bubbles: true}));"
        "el.dispatchEvent(new Event('change', {bubbles: true}));",
        element_id, str(value))


def set_select(driver, element_id, value):
    driver.execute_script(
        "var el = document.getElementById(arguments[0]);"
        "el.value = arguments[1];"
        "el.dispatchEvent(new Event('change', {bubbles: true}));",
        element_id, value)


def main():
    case = BrowserCase("test02", "video player controls, simulated playback")
    driver = case.start_browser()

    case.step("load_fixture",
              lambda: driver.get(fixture_uri("test02_video_player.html")))

    def verify_initial():
        state = player(driver).get_attribute("data-state")
        case.check("initial_state_paused", state == "paused", state)
        case.check("initial_duration_label",
                   text_of(driver, "duration") == "4:00",
                   text_of(driver, "duration"))
        case.check("initial_title",
                   text_of(driver, "video-title") == "Intro to Wayland",
                   text_of(driver, "video-title"))
        case.check("initial_toggle_label",
                   text_of(driver, "toggle-btn") == "Play",
                   text_of(driver, "toggle-btn"))
        case.check("initial_time_zero", current_seconds(driver) == 0,
                   current_seconds(driver))
        return {"state": state}
    case.step("verify_initial_state", verify_initial)

    case.step("play_video",
              lambda: driver.find_element("id", "toggle-btn").click())

    advance1 = {}

    def measure_speed1():
        start = current_seconds(driver)
        time.sleep(1.2)
        end = current_seconds(driver)
        advance1["value"] = end - start
        case.check("state_playing",
                   player(driver).get_attribute("data-state") == "playing")
        case.check("time_advanced_at_speed1", end - start >= 0.6,
                   f"advanced {end - start:.2f} in about 1.2 s")
        case.check("toggle_label_pause",
                   text_of(driver, "toggle-btn") == "Pause",
                   text_of(driver, "toggle-btn"))
        return {"start": start, "end": end, "advance": end - start}
    case.step("measure_advance_speed1", measure_speed1)

    case.step("pause_video",
              lambda: driver.find_element("id", "toggle-btn").click())

    def verify_frozen():
        first = current_seconds(driver)
        time.sleep(0.6)
        second = current_seconds(driver)
        case.check("state_paused_after_pause",
                   player(driver).get_attribute("data-state") == "paused")
        case.check("time_frozen_while_paused", abs(second - first) < 0.05,
                   f"{first:.2f} then {second:.2f}")
        return {"first": first, "second": second}
    case.step("verify_time_frozen", verify_frozen)

    def seek_120():
        set_range(driver, "seek", 120)
        label = text_of(driver, "current-time")
        now = current_seconds(driver)
        width = driver.find_element("id", "progress-fill") \
            .get_attribute("style")
        case.check("seek_time_label_2_00", label == "2:00", label)
        case.check("seek_position_120", abs(now - 120) <= 1.0, now)
        case.check("seek_progress_about_half", "50%" in width, width)
        return {"label": label, "seconds": now, "style": width}
    case.step("seek_to_120", seek_120)

    def set_volume():
        set_range(driver, "volume", 30)
        label = text_of(driver, "volume-label")
        value = driver.find_element("id", "volume").get_attribute("value")
        case.check("volume_set_30", label == "30" and value == "30",
                   f"label {label} slider {value}")
        return {"label": label, "slider": value}
    case.step("set_volume_30", set_volume)

    case.step("mute_volume",
              lambda: driver.find_element("id", "mute-btn").click())

    def verify_muted():
        muted = player(driver).get_attribute("data-muted")
        label = text_of(driver, "volume-label")
        value = driver.find_element("id", "volume").get_attribute("value")
        case.check("muted_state", muted == "true", muted)
        case.check("muted_label_and_slider",
                   label == "Muted" and value == "0",
                   f"label {label} slider {value}")
        return {"muted": muted, "label": label}
    case.step("verify_muted", verify_muted)

    case.step("unmute_volume",
              lambda: driver.find_element("id", "mute-btn").click())

    def verify_unmuted():
        muted = player(driver).get_attribute("data-muted")
        label = text_of(driver, "volume-label")
        case.check("unmuted_restores_30",
                   muted == "false" and label == "30",
                   f"muted {muted} label {label}")
        return {"muted": muted, "label": label}
    case.step("verify_unmuted", verify_unmuted)

    def set_speed():
        set_select(driver, "speed", "2")
        value = player(driver).get_attribute("data-speed")
        case.check("speed_set_2", value == "2", value)
        return {"speed": value}
    case.step("set_speed_2", set_speed)

    def measure_speed2():
        driver.find_element("id", "toggle-btn").click()
        start = current_seconds(driver)
        time.sleep(1.2)
        end = current_seconds(driver)
        driver.find_element("id", "toggle-btn").click()
        advance = end - start
        base = advance1.get("value", 1.2)
        case.check("time_advanced_at_speed2", advance >= 1.7,
                   f"advanced {advance:.2f} in about 1.2 s")
        case.check("speed2_at_least_1_5x_speed1", advance >= 1.5 * base,
                   f"speed2 {advance:.2f} against speed1 {base:.2f}")
        return {"start": start, "end": end, "advance": advance,
                "speed1_advance": base}
    case.step("measure_advance_speed2", measure_speed2)

    case.step("seek_to_15", lambda: set_range(driver, "seek", 15))

    def subtitles_en():
        set_select(driver, "subtitles", "en")
        caption = text_of(driver, "caption-line")
        case.check("caption_en_at_15s", caption == EN_CAPTION, caption)
        return {"caption": caption}
    case.step("enable_subtitles_en", subtitles_en)

    def subtitles_vi():
        set_select(driver, "subtitles", "vi")
        caption = text_of(driver, "caption-line")
        case.check("caption_vi_at_15s", caption == VI_CAPTION, caption)
        case.check("caption_changed_from_en", caption != EN_CAPTION, caption)
        return {"caption": caption}
    case.step("switch_subtitles_vi", subtitles_vi)

    def load_item2():
        items = driver.find_elements("css selector", ".playlist-item")
        items[1].click()
        title = text_of(driver, "video-title")
        dur = text_of(driver, "duration")
        now = text_of(driver, "current-time")
        active = "active" in items[1].get_attribute("class")
        case.check("item2_title", title == "Hyprland Tour", title)
        case.check("item2_duration_3_00", dur == "3:00", dur)
        case.check("item2_time_reset", now == "0:00", now)
        case.check("item2_highlighted", active)
        case.check("item2_paused",
                   player(driver).get_attribute("data-state") == "paused")
        return {"title": title, "duration": dur}
    case.step("load_playlist_item_2", load_item2)

    def load_item3():
        items = driver.find_elements("css selector", ".playlist-item")
        items[2].click()
        title = text_of(driver, "video-title")
        dur = text_of(driver, "duration")
        case.check("item3_title", title == "DOM Control Deep Dive", title)
        case.check("item3_duration_5_00", dur == "5:00", dur)
        case.check("item3_time_reset",
                   text_of(driver, "current-time") == "0:00",
                   text_of(driver, "current-time"))
        return {"title": title, "duration": dur}
    case.step("load_playlist_item_3", load_item3)

    def play_item3():
        driver.find_element("id", "toggle-btn").click()
        time.sleep(0.8)
        now = current_seconds(driver)
        state = player(driver).get_attribute("data-state")
        case.check("item3_playing_and_advancing",
                   state == "playing" and now > 0.2,
                   f"state {state} at {now:.2f}")
        driver.find_element("id", "toggle-btn").click()
        return {"seconds": now, "state": state}
    case.step("play_item_3_briefly", play_item3)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

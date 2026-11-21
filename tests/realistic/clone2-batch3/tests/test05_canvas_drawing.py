#!/usr/bin/env python3
"""Test 05, canvas drawing app, batch 3.

Drives a real offline drawing app in a real browser: pick colors,
set brush size, draw strokes with mouse action chains, verify the
result by reading canvas pixels back, undo, redo, erase, save to a
PNG data URL, and clear. State is read through window.drawApp.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import BrowserCase, fixture_uri

RED = "#e53935"
BLUE = "#1e88e5"

SAMPLE_JS = """
var pts = arguments[0];
var c = window.drawApp.canvas;
var g = c.getContext('2d');
var out = [];
for (var i = 0; i < pts.length; i++) {
  var d = g.getImageData(pts[i][0], pts[i][1], 1, 1).data;
  out.push([d[0], d[1], d[2], d[3]]);
}
return out;
"""


def is_blank(px):
    return px[3] == 0


def is_red(px):
    return px[3] > 200 and px[0] > 180 and px[1] < 120 and px[2] < 120


def is_blue(px):
    return px[3] > 200 and px[2] > 180 and px[0] < 110 and 80 < px[1] < 200


def main():
    case = BrowserCase("test05", "canvas drawing app")
    driver = case.start_browser()
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys

    def state():
        return driver.execute_script("return window.drawApp.getState();")

    def sample(points):
        return driver.execute_script(SAMPLE_JS, points)

    def canvas_el():
        return driver.find_element(By.ID, "pad")

    def draw_line(start_offset, dx, dy, segments=3):
        chain = ActionChains(driver)
        chain.move_to_element_with_offset(canvas_el(), *start_offset)
        chain.click_and_hold()
        for _ in range(segments):
            chain.move_by_offset(dx, dy)
            chain.pause(0.05)
        chain.release()
        chain.perform()
        time.sleep(0.15)

    try:
        case.step("load_fixture",
                  lambda: (driver.get(fixture_uri(
                      "test05_canvas_drawing.html")), driver.title)[1])
        st = case.step("initial_state", state)
        case.check("starts_blank", st["strokes"] == 0, f"state={st}")
        blank_len = st["dataUrlLength"]

        px = case.step("blank_pixel_sample",
                       lambda: sample([[100, 100], [320, 220], [180, 100]]))
        case.check("canvas_pixels_blank_at_start",
                   all(is_blank(p) for p in px), f"px={px}")

        case.step("select_red",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, f"[data-color='{RED}']").click())
        st = case.step("verify_color_red", state)
        case.check("color_is_red", st["color"] == RED, f"color={st['color']}")

        def set_size():
            slider = driver.find_element(By.ID, "size")
            current = int(slider.get_attribute("value"))
            diff = 8 - current
            key = Keys.ARROW_RIGHT if diff > 0 else Keys.ARROW_LEFT
            for _ in range(abs(diff)):
                slider.send_keys(key)
            return driver.find_element(By.ID, "size").get_attribute("value")
        val = case.step("set_brush_size_8", set_size)
        st = case.step("verify_size_8", state)
        case.check("brush_size_8", st["size"] == 8 and val == "8",
                   f"state_size={st['size']} slider={val}")

        case.step("draw_stroke_1_red",
                  lambda: draw_line((-260, -120), 80, 0))
        st = case.step("verify_count_1", state)
        case.check("stroke_count_1", st["strokes"] == 1,
                   f"strokes={st['strokes']}")

        pts1 = [[x, 100] for x in range(70, 291, 20)]
        px = case.step("stroke1_pixel_sample", lambda: sample(pts1))
        red_hits = sum(1 for p in px if is_red(p))
        case.check("stroke1_pixels_red_along_line", red_hits >= 8,
                   f"red_hits={red_hits}/{len(px)} px0={px[0]}")

        case.step("select_blue",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, f"[data-color='{BLUE}']").click())
        st = case.step("verify_color_blue", state)
        case.check("color_is_blue", st["color"] == BLUE,
                   f"color={st['color']}")

        case.step("draw_stroke_2_blue",
                  lambda: draw_line((-240, 40), 80, 0))
        st = case.step("verify_count_2", state)
        case.check("stroke_count_2", st["strokes"] == 2,
                   f"strokes={st['strokes']}")

        pts2 = [[x, 260] for x in range(90, 311, 20)]
        px = case.step("stroke2_pixel_sample", lambda: sample(pts2))
        blue_hits = sum(1 for p in px if is_blue(p))
        red_hits2 = sum(1 for p in px if is_red(p))
        case.check("stroke2_pixels_blue_and_different",
                   blue_hits >= 8 and red_hits2 == 0,
                   f"blue_hits={blue_hits}/{len(px)} red_hits={red_hits2}")

        case.step("undo_click",
                  lambda: driver.find_element(By.ID, "undo").click())
        st = case.step("verify_count_after_undo", state)
        case.check("count_1_after_undo", st["strokes"] == 1,
                   f"strokes={st['strokes']}")

        case.step("redo_click",
                  lambda: driver.find_element(By.ID, "redo").click())
        st = case.step("verify_count_after_redo", state)
        case.check("count_2_after_redo", st["strokes"] == 2,
                   f"strokes={st['strokes']}")

        def erase():
            driver.find_element(By.ID, "eraser").click()
            draw_line((-150, -120), 30, 0, segments=1)
            return state()
        st = case.step("eraser_stroke_over_stroke1", erase)
        case.check("eraser_stroke_counted", st["strokes"] == 3,
                   f"strokes={st['strokes']}")

        px = case.step("erase_pixel_sample",
                       lambda: sample([[185, 100], [80, 100]]))
        case.check("erased_point_blank_and_rest_intact",
                   is_blank(px[0]) and is_red(px[1]),
                   f"erased_px={px[0]} kept_px={px[1]}")

        case.step("save_click",
                  lambda: driver.find_element(By.ID, "save").click())

        def save_info():
            link = driver.find_element(By.ID, "download")
            href = link.get_attribute("href") or ""
            nonblank = driver.execute_async_script(
                "var url = arguments[0];"
                "var done = arguments[arguments.length - 1];"
                "var img = new Image();"
                "img.onload = function () {"
                "  var c = document.createElement('canvas');"
                "  c.width = img.naturalWidth; c.height = img.naturalHeight;"
                "  var g = c.getContext('2d'); g.drawImage(img, 0, 0);"
                "  var d = g.getImageData(0, 0, c.width, c.height).data;"
                "  var n = 0;"
                "  for (var i = 3; i < d.length; i += 4) {"
                "    if (d[i] > 0) { n++; }"
                "  }"
                "  done(n);"
                "};"
                "img.onerror = function () { done(-1); };"
                "img.src = url;", href)
            return {
                "href_head": href[:30],
                "href_len": len(href),
                "saved_nonblank_px": nonblank,
                "preview": driver.execute_script(
                    "var i=document.getElementById('preview');"
                    "return i.style.display !== 'none' && i.complete"
                    " && i.naturalWidth > 0;"),
                "state_len": state()["dataUrlLength"],
            }
        info = case.step("verify_save_output", save_info)
        case.check("download_link_is_png_data_url",
                   info["href_head"].startswith("data:image/png"),
                   f"href_head={info['href_head']}")
        case.check("preview_image_shown", info["preview"] is True,
                   f"preview={info['preview']}")
        case.check("saved_data_url_substantial",
                   info["href_len"] > blank_len
                   and info["saved_nonblank_px"] > 1500,
                   f"href_len={info['href_len']} blank_len={blank_len} "
                   f"saved_nonblank_px={info['saved_nonblank_px']}")

        case.step("clear_click",
                  lambda: driver.find_element(By.ID, "clear").click())
        st = case.step("verify_cleared_state", state)
        px = sample([[100, 100], [180, 260], [320, 220]])
        case.check("cleared_count_and_pixels",
                   st["strokes"] == 0 and all(is_blank(p) for p in px),
                   f"strokes={st['strokes']} px={px}")
    except Exception as exc:
        print(f"  test aborted: {type(exc).__name__}: {exc}", flush=True)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

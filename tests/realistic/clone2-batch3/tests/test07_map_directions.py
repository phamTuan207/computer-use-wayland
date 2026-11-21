#!/usr/bin/env python3
"""Test 07, map directions, batch 3.

Drives a simulated maps app in a real browser: pick an origin and
a destination through autocomplete, read the computed route, and
verify every number against the formulas recomputed in this file
from the known place coordinates. Manhattan distance on the grid,
per mode speeds, alternative route at 1.3 times the main distance.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import BrowserCase, fixture_uri

PLACES = {
    "Central Station": (2, 3),
    "City Museum": (5, 3),
    "Riverside Park": (5, 7),
    "Old Library": (1, 7),
    "Harbor Market": (8, 1),
    "University": (8, 6),
    "Botanical Garden": (3, 9),
    "Airport": (11, 9),
}
SPEEDS = {"drive": (30, 0), "transit": (20, 5), "walk": (5, 0),
          "cycle": (15, 0)}
ORIGIN = "Central Station"
DEST = "Riverside Park"


def manhattan(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def time_for(dist_km, mode_key):
    speed, wait = SPEEDS[mode_key]
    return round(dist_km / speed * 60) + wait


def parse_km(text):
    return float(text.replace("km", "").strip())


def parse_min(text):
    return int(text.replace("min", "").strip())


def main():
    case = BrowserCase("test07", "map directions")
    driver = case.start_browser()
    from selenium.webdriver.common.by import By

    def state():
        return driver.execute_script("return window.mapApp.getState();")

    def text_of(element_id):
        return driver.find_element(By.ID, element_id).text

    def pick(input_id, list_id, partial, full_name):
        box = driver.find_element(By.ID, input_id)
        box.clear()
        box.send_keys(partial)
        time.sleep(0.3)
        item = driver.find_element(
            By.CSS_SELECTOR, f"#{list_id} .ac-item[data-name='{full_name}']")
        item.click()
        time.sleep(0.2)
        return box.get_attribute("value")

    def step_distances():
        els = driver.find_elements(By.CSS_SELECTOR, "#steps .step-dist")
        return [parse_km(e.text) for e in els]

    try:
        case.step("load_fixture",
                  lambda: (driver.get(fixture_uri(
                      "test07_map_directions.html")), driver.title)[1])

        markers = case.step(
            "count_place_markers",
            lambda: len(driver.find_elements(By.CSS_SELECTOR, ".marker")))
        case.check("markers_match_dataset_size",
                   markers == len(PLACES),
                   f"markers={markers} dataset={len(PLACES)}")

        case.step("type_origin_partial",
                  lambda: driver.find_element(
                      By.ID, "origin-input").send_keys("Central"))
        time.sleep(0.3)
        offered = case.step(
            "read_origin_dropdown",
            lambda: [e.get_attribute("data-name") for e in
                     driver.find_elements(
                         By.CSS_SELECTOR, "#origin-list .ac-item")])
        case.check("origin_dropdown_offers_central_station",
                   ORIGIN in offered, f"offered={offered}")

        picked = case.step(
            "pick_origin_from_dropdown",
            lambda: (driver.find_element(
                By.CSS_SELECTOR,
                f"#origin-list .ac-item[data-name='{ORIGIN}']").click(),
                driver.find_element(
                    By.ID, "origin-input").get_attribute("value"))[1])
        case.check("origin_input_shows_full_name", picked == ORIGIN,
                   f"picked={picked}")

        picked_dest = case.step(
            "type_and_pick_destination",
            lambda: pick("dest-input", "dest-list", "River", DEST))
        case.check("destination_input_shows_full_name",
                   picked_dest == DEST, f"picked={picked_dest}")

        st = case.step("read_route_state", state)
        expected_dist = manhattan(PLACES[ORIGIN], PLACES[DEST])
        panel_dist = case.step(
            "read_route_distance",
            lambda: parse_km(text_of("route-distance")))
        case.check("route_distance_matches_manhattan_recomputed",
                   st["route"] is not None
                   and abs(panel_dist - expected_dist) < 0.05,
                   f"panel={panel_dist} recomputed_manhattan="
                   f"{expected_dist} from {PLACES[ORIGIN]} to "
                   f"{PLACES[DEST]}")

        drive_time = case.step(
            "read_drive_time", lambda: parse_min(text_of("route-time")))
        expected_drive = time_for(expected_dist, "drive")
        case.check("drive_time_matches_formula_recomputed",
                   drive_time == expected_drive,
                   f"panel={drive_time} recomputed={expected_drive} "
                   f"from {expected_dist} km at 30 km/h")

        dists = case.step("read_turn_by_turn_steps", step_distances)
        case.check("turn_by_turn_at_least_4_steps", len(dists) >= 4,
                   f"steps={len(dists)} dists={dists}")
        case.check("step_distances_sum_to_total",
                   abs(sum(dists) - panel_dist) < 0.05,
                   f"sum={round(sum(dists), 3)} total={panel_dist}")

        case.step("switch_to_walk",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".mode-btn[data-mode='walk']")
                  .click())
        walk_time = case.step(
            "read_walk_time", lambda: parse_min(text_of("route-time")))
        expected_walk = time_for(expected_dist, "walk")
        case.check("walk_time_matches_formula_and_increases",
                   walk_time == expected_walk and walk_time > drive_time,
                   f"panel={walk_time} recomputed={expected_walk} "
                   f"from {expected_dist} km at 5 km/h, drive was "
                   f"{drive_time}")

        case.step("switch_to_transit",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".mode-btn[data-mode='transit']")
                  .click())
        transit_time = case.step(
            "read_transit_time", lambda: parse_min(text_of("route-time")))
        expected_transit = time_for(expected_dist, "transit")
        case.check("transit_time_matches_formula_recomputed",
                   transit_time == expected_transit,
                   f"panel={transit_time} recomputed={expected_transit} "
                   f"from {expected_dist} km at 20 km/h plus 5 min wait")

        case.step("switch_to_cycle",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".mode-btn[data-mode='cycle']")
                  .click())
        cycle_time = case.step(
            "read_cycle_time", lambda: parse_min(text_of("route-time")))
        expected_cycle = time_for(expected_dist, "cycle")
        case.check("cycle_time_matches_formula_recomputed",
                   cycle_time == expected_cycle,
                   f"panel={cycle_time} recomputed={expected_cycle} "
                   f"from {expected_dist} km at 15 km/h")

        case.step("switch_back_to_drive",
                  lambda: driver.find_element(
                      By.CSS_SELECTOR, ".mode-btn[data-mode='drive']")
                  .click())
        alt_dist = case.step(
            "read_alternative_card_distance",
            lambda: parse_km(driver.find_element(
                By.CSS_SELECTOR, "#route-alt .card-dist").text))
        expected_alt = round(expected_dist * 1.3 * 10) / 10
        case.check("alternative_offered_with_different_distance",
                   abs(alt_dist - expected_alt) < 0.05
                   and abs(alt_dist - expected_dist) > 0.05,
                   f"alt={alt_dist} recomputed={expected_alt} "
                   f"main={expected_dist}")

        case.step("pick_alternative_route",
                  lambda: driver.find_element(By.ID, "route-alt").click())
        alt_panel = case.step(
            "read_panel_after_alternative",
            lambda: (parse_km(text_of("route-distance")),
                     parse_min(text_of("route-time"))))
        expected_alt_time = time_for(expected_alt, "drive")
        case.check("alternative_distance_and_time_match_recomputed",
                   abs(alt_panel[0] - expected_alt) < 0.05
                   and alt_panel[1] == expected_alt_time,
                   f"panel_dist={alt_panel[0]} panel_time={alt_panel[1]} "
                   f"recomputed_dist={expected_alt} "
                   f"recomputed_time={expected_alt_time}")

        alt_dists = case.step("read_alternative_steps", step_distances)
        case.check("alternative_step_distances_sum_to_alt_total",
                   len(alt_dists) >= 4
                   and abs(sum(alt_dists) - alt_panel[0]) < 0.05,
                   f"steps={len(alt_dists)} sum="
                   f"{round(sum(alt_dists), 3)} total={alt_panel[0]}")

        recent = case.step(
            "read_recent_searches",
            lambda: [e.text for e in driver.find_elements(
                By.CSS_SELECTOR, "#recent-list .recent-item")])
        case.check("search_recorded_in_recent_searches",
                   f"{ORIGIN} to {DEST}" in recent, f"recent={recent}")

        case.step("swap_origin_destination",
                  lambda: driver.find_element(By.ID, "swap-btn").click())
        swapped = case.step(
            "read_after_swap",
            lambda: (driver.find_element(
                        By.ID, "origin-input").get_attribute("value"),
                     driver.find_element(
                        By.ID, "dest-input").get_attribute("value"),
                     parse_km(text_of("route-distance")),
                     state()))
        case.check("swap_exchanges_places_and_keeps_distance",
                   swapped[0] == DEST and swapped[1] == ORIGIN
                   and abs(swapped[2] - expected_dist) < 0.05,
                   f"origin_now={swapped[0]} dest_now={swapped[1]} "
                   f"distance={swapped[2]} expected={expected_dist}")

        recent2 = case.step(
            "read_recent_after_swap",
            lambda: [e.text for e in driver.find_elements(
                By.CSS_SELECTOR, "#recent-list .recent-item")])
        case.check("swapped_search_is_latest_recent_entry",
                   len(recent2) >= 2
                   and recent2[0] == f"{DEST} to {ORIGIN}",
                   f"recent={recent2}")
    except Exception as exc:
        print(f"  test aborted: {type(exc).__name__}: {exc}", flush=True)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

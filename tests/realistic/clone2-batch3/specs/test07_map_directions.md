# Test 07, map directions

## Goal

Prove an agent can use a simulated maps app in a real browser:
pick places through autocomplete, read a computed route, and
verify every number the app shows against the formulas recomputed
independently in the test, not just trust the page. Mode switching,
an alternative route, origin and destination swap, and the recent
searches list are all covered.

Fixture: fixtures/test07_map_directions.html, fully offline,
inline CSS and JS. A fake map area with one marker per place, and
a dataset of 8 places on a km grid: Central Station (2, 3),
City Museum (5, 3), Riverside Park (5, 7), Old Library (1, 7),
Harbor Market (8, 1), University (8, 6), Botanical Garden (3, 9),
Airport (11, 9). State is readable at window.mapApp.getState().

## Formulas, stated in the fixture UI and used by the checker

- Distance: Manhattan grid distance, |x2 - x1| + |y2 - y1| km.
- Time in minutes: distance / speed * 60, rounded to the nearest
  minute, plus the mode wait.
- Speeds: drive 30 km/h with no wait, transit 20 km/h plus a
  5 min wait, walk 5 km/h, cycle 15 km/h.
- Alternative route distance: main distance x 1.3, rounded to
  1 decimal, it follows the scenic river road.
- Turn by turn steps split each leg into segments of at most
  2 km, plus start, turn, and arrive steps at 0 km, so the step
  distances sum to the route total.

For the tested pair, Central Station (2, 3) to Riverside Park
(5, 7): Manhattan distance 3 + 4 = 7.0 km. Drive 14 min,
transit 26 min, walk 84 min, cycle 28 min. Alternative distance
9.1 km, alternative drive time 18 min.

## Steps

1. Start the browser and load the fixture.
2. Count the place markers on the map, expect 8, one per place
   in the dataset.
3. Type "Central" in the origin input.
4. Read the autocomplete dropdown, expect Central Station to be
   offered.
5. Click Central Station in the dropdown, verify the origin
   input shows the full name.
6. Type "River" in the destination input and pick Riverside Park
   from its dropdown, verify the input shows the full name.
7. Read the route state and the route panel distance, expect
   7.0 km, matching the Manhattan distance recomputed in the
   test from the known coordinates.
8. Read the drive time, expect 14 min, matching the formula
   recomputed in the test.
9. Read the turn by turn steps, expect at least 4, and verify
   the step distances sum to the 7.0 km total.
10. Switch to walk, read the time, expect 84 min by the walk
    formula, and more than the drive time.
11. Switch to transit, expect 26 min by the transit formula.
12. Switch to cycle, expect 28 min by the cycle formula.
13. Switch back to drive.
14. Read the alternative route card distance, expect 9.1 km,
    the main distance x 1.3 recomputed in the test, and
    different from the main distance.
15. Click the alternative route card.
16. Verify the panel now shows 9.1 km and 18 min, the drive
    time for the alternative distance recomputed in the test.
17. Read the alternative turn by turn steps, expect at least 4,
    summing to 9.1 km.
18. Read the recent searches list, expect it to contain
    "Central Station to Riverside Park".
19. Click the swap button.
20. Verify the inputs are exchanged, Riverside Park as origin
    and Central Station as destination, and the distance is
    still 7.0 km, Manhattan distance is symmetric.
21. Read the recent searches again, expect the latest entry to
    be "Riverside Park to Central Station".

## Expected results

Every step ok, every check ok. Route distance 7.0 km for the
main route in both directions, 9.1 km for the alternative.
Times by mode for the main route: drive 14 min, transit 26 min,
walk 84 min, cycle 28 min. Alternative drive time 18 min. Step
distances sum to the shown total on both routes. The recent
searches list records the original search and then the swapped
search as the latest entry.

## Timing

Filled after the verification runs on this machine, headless
Firefox 160.0.1, geckodriver 0.37.1, Selenium venv:

- RESULT ok: true, two consecutive full passes, final run wall
  clock 2026-11-21T11:30:57Z to 2026-11-21T11:31:20Z
- Step count: 26, including browser_start
- Checks: 17 of 17 ok
- Total elapsed: 23.0017 s on the final run, most of it browser
  start, 13.1689 s for browser_start on the first run, every
  in-page step after load was under 1 s
- Verified values on both runs: main distance 7.0 km recomputed
  as |5 - 2| + |7 - 3|, drive 14 min, transit 26 min, walk
  84 min, cycle 28 min, alternative distance 9.1 km and
  alternative drive time 18 min, main route 7 turn by turn steps
  summing to 7.0 km, alternative route 8 steps summing to
  9.1 km, distance unchanged at 7.0 km after the swap

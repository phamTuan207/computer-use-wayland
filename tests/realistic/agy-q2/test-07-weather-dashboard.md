# test-07-weather-dashboard.md

## Test ID
test-07-weather-dashboard

## Topic
Global weather dashboard: temperature unit toggling (Celsius to Fahrenheit and back), station monitoring, adding cities, handling accidental entry and removal, setting primary station, and saving dashboard state.

## Context
Pham Tuan monitors operations across multiple regional distribution centers.
The workstation runs an offline weather dashboard interface (fixtures/test-07-weather-dashboard.html).
There are 3 initial monitored stations: Tokyo, London, and New York. The default temperature unit is Celsius (°C).
The user must test temperature unit toggling to Fahrenheit (°F) and back to verify correct conversion, add "Ho Chi Minh City" station, handle an accidental addition of "Reykjavik" by deleting its card, designate "Ho Chi Minh City" as the primary monitoring station, switch the display unit to Fahrenheit (°F) for final shift handover, and save the dashboard configuration.

## Timing
- Baseline start time: 2026-11-21 17:15:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Add Ho Chi Minh City, delete accidental Reykjavik, set Ho Chi Minh City as primary station, switch unit to Fahrenheit (°F) with 90°F reading, verify 4 cities monitored, and save dashboard.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-07-weather-dashboard.html in the browser.
2. Confirm 3 initial city cards are visible (Tokyo, London, New York) and count indicator (id "stat-city-count") reads "3".
3. Verify the Celsius unit toggle button (id "btn-unit-c") has the "active" class.
4. Verify Tokyo current temperature (id "temp-tokyo") displays "18°C".
5. Click the Fahrenheit toggle button (id "btn-unit-f").
6. Verify Tokyo current temperature (id "temp-tokyo") updates to "64°F".
7. Verify London current temperature (id "temp-london") updates to "54°F".
8. Click the Celsius toggle button (id "btn-unit-c") to revert to Celsius.
9. Verify Tokyo temperature returns to "18°C".
10. Open the Add Station dropdown (id "select-add-city").
11. Select option "Ho Chi Minh City, Vietnam" (value "ho-chi-minh-city").
12. Click "+ Add City" button (id "btn-add-city").
13. Verify Ho Chi Minh City card (id "card-city-ho-chi-minh-city") is created in the grid.
14. Verify Ho Chi Minh City current temperature (id "temp-ho-chi-minh-city") displays "32°C".
15. Accidental selection: in Add Station dropdown, select "Reykjavik, Iceland" (value "reykjavik").
16. Click "+ Add City" button (id "btn-add-city").
17. Verify Reykjavik card (id "card-city-reykjavik") appears in the grid with condition "Snow Showers".
18. Verify city count indicator (id "stat-city-count") displays "5".
19. Locate the Reykjavik card and click its "Remove" button (id "btn-remove-city-reykjavik").
20. Verify Reykjavik card is removed from the DOM.
21. Verify city count indicator (id "stat-city-count") updates back to "4".
22. Locate Ho Chi Minh City card and click "Set Primary" button (id "btn-primary-city-ho-chi-minh-city").
23. Verify Ho Chi Minh City card gains the "primary-city" styling and shows the "Primary" badge (id "badge-primary-ho-chi-minh-city").
24. Click the Fahrenheit toggle button (id "btn-unit-f").
25. Verify active unit indicator (id "active-unit-indicator") displays "°F".
26. Verify Ho Chi Minh City current temperature (id "temp-ho-chi-minh-city") displays "90°F".
27. Click "Save Weather Dashboard" button (id "btn-save-weather").
28. Read status banner (id "weather-status-banner") and confirm it displays "Dashboard saved: 4 cities monitored in °F (Primary: Ho Chi Minh City)".

## Pass/fail criteria
- Pass: Exactly 4 cities monitored, Ho Chi Minh City is primary, Reykjavik removed, active unit is Fahrenheit, Ho Chi Minh City temp displays 90°F, and status banner confirms saved dashboard.
- Fail: Reykjavik still present, wrong primary station, Celsius still active, or status banner unconfirmed.

## Errors designed to expose
- click miss: Toggling between small unit switch buttons or clicking Remove on wrong city card.
- stale state: Verifying converted temperature before DOM re-renders after unit toggle.
- primary state miss: Forgetting to designate the new station as primary before saving.
- accidental entry retention: Failing to remove Reykjavik after adding it.
- fabrication: Asserting save confirmation without checking the status banner.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-07-weather-dashboard.html --test 07
```

# test-04-maps-directions.md

## Test ID
test-04-maps-directions

## Topic
Maps directions with origin and destination search, route selection, toll avoidance, saving, and reversing.

## Context
A traveler plans a route from Harbor Square to Workshop District, initially chooses a faster route that charges a toll, filters tolls out, saves a toll-free route, reverses the trip, and saves the reversed directions. Location selection uses visible search suggestions. The fixture is tests/realistic/codex-y5/fixtures/test-04-maps-directions.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Save a toll-free North Loop route from Workshop District to Harbor Square with distance 14.2 km and duration 24 min.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-04-maps-directions.html in the browser.
2. Verify #origin-selected text is "None", #destination-selected text is "None", #route-result-count text is "0", #selected-route-summary text is "No route selected", #saved-route-summary text is "No saved route", #origin-suggestions text is "No origin search", and #destination-suggestions text is "No destination search".
3. Type "Harbor Square" into #origin-input; its value must be "Harbor Square".
4. Click button #btn-search-origin; #origin-suggestions must become "Harbor Square".
5. Verify #origin-suggestions text is exactly "Harbor Square" and #btn-pick-origin-harbor-square text is "Harbor Square".
6. Click button #btn-pick-origin-harbor-square; #origin-selected must become "Harbor Square".
7. Type "Workshop District" into #destination-input; its value must be "Workshop District".
8. Click button #btn-search-destination; #destination-suggestions must become "Workshop District".
9. Verify #destination-suggestions text is exactly "Workshop District" and #btn-pick-destination-workshop-district text is "Workshop District".
10. Click button #btn-pick-destination-workshop-district; #destination-selected must become "Workshop District".
11. Click button #btn-find-routes; #route-result-count must become "2".
12. Verify #btn-select-north-loop text is "Choose" and #btn-select-river-express text is "Choose".
13. Mistake: click button #btn-select-river-express and choose the faster toll route; #selected-route-summary must become "River Express | 12.8 km | 21 min | $2.50 toll".
14. Verify #selected-route-summary text is exactly "River Express | 12.8 km | 21 min | $2.50 toll".
15. Recovery: click checkbox #avoid-tolls-toggle to turn toll avoidance on; #avoid-tolls-status must become "Avoid tolls On".
16. Verify #route-result-count text is "1", #selected-route-summary text is "No route selected", and #btn-select-north-loop text is "Choose".
17. Click button #btn-select-north-loop; #selected-route-summary must become "North Loop | 14.2 km | 24 min | No tolls".
18. Verify #selected-route-summary text is exactly "North Loop | 14.2 km | 24 min | No tolls".
19. Click button #btn-save-route; #saved-route-status must become "Route saved".
20. Verify #saved-route-summary text is "Harbor Square to Workshop District | North Loop | 14.2 km | 24 min | No tolls".
21. Click button #btn-reverse-route; #origin-selected must become "Workshop District" and #destination-selected must become "Harbor Square".
22. Verify #selected-route-summary text is "No route selected" and #saved-route-summary text is "No saved route".
23. Click button #btn-find-routes; #route-result-count must become "1" because toll avoidance remains on.
24. Verify #avoid-tolls-status text is "Avoid tolls On" and #route-result-count text is "1".
25. Click button #btn-select-north-loop; #selected-route-summary must become "North Loop | 14.2 km | 24 min | No tolls".
26. Click button #btn-save-route; #saved-route-status must become "Route saved".
27. Verify #origin-selected text is "Workshop District", #destination-selected text is "Harbor Square", #selected-route-summary text is "North Loop | 14.2 km | 24 min | No tolls", and #saved-route-summary text is "Workshop District to Harbor Square | North Loop | 14.2 km | 24 min | No tolls".

## Pass/fail criteria
- Pass: The reversed route is saved from Workshop District to Harbor Square on North Loop, with toll avoidance on, 14.2 km distance, and 24 min duration.
- Fail: The toll route remains selected, the route is not saved after reversing, the origin and destination are not swapped, or any route value differs.

## Errors designed to expose
- click miss: Search suggestions and route choices have separate small targets.
- slow think: The user must re-run route search after reversing the trip.
- stale observation: Reversing clears the old selection and saved route.
- wrong diagnosis: The toll route looks faster but violates the toll-free requirement.
- fabrication: The route distance, duration, toll label, and saved direction are exact text checks.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-04-maps-directions.html --test 04
```

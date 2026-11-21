# t07-map-directions: plan routes on a fake map

## Context

A city directions page with a fake offline map: a street grid, 6 named
places, and a route planner that computes Manhattan distance, time by
walk, bike, or drive, a toll bridge crossing, an avoid-tolls detour, an
alternate route, swap, and saved routes.

## Goal

Plan several routes, prove distance and time change the right way with
mode and tolls, and prove save and load work.

## Steps (27)

1. Open the fixture.
2. Check 6 places are listed.
3. Pick Home to Office.
4. Get directions.
5. Check the distance is 4.0 km.
6. Check the walk time is 48 min.
7. Check the route has 5 steps, mentions the toll bridge, heads east
   first, and the summary says Toll: yes.
8. Switch to bike and get directions.
9. Check the bike time is 16 min, faster than walking.
10. Switch to drive and get directions.
11. Check the drive time is 6 min, faster than biking.
12. Enable avoid tolls and get directions.
13. Check the detour is 4.8 km, Toll: no, and the steps mention the
    North Bridge detour.
14. Disable avoid tolls, enable the alternate route, get directions.
15. Check the alternate route starts south on 1st Ave.
16. Swap origin and destination, get directions.
17. Check the swapped route is still 4.0 km, Office to Home.
18. Save the route.
19. Check the saved list has 1 route.
20. Plan Station to Library.
21. Check it is 1.2 km.
22. Load the saved route.
23. Check it restores Office to Home.
24. Delete the saved route.
25. Check the saved list is empty.
26. Pick Market as both origin and destination, get directions.
27. Check the same-place error is shown.

## Pass

All 27 steps run, distances and times match the grid math, the toll and
detour behave, the alternate route changes the first move, swap keeps
the distance, and save, load, and delete work.

## Fail

Any step above fails, a distance or time is wrong, the toll logic is
inverted, or a saved route does not restore.

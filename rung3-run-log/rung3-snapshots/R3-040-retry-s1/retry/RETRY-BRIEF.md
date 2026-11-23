# R3-040 RETRY BRIEF (owner ordered 2026-11-24 01:15:00 +07)

## What happened
R3-040 (compare an archived web page against the current version, write 3 changes) failed the first time because web.archive.org returned HTTP 429 twice when the snapshot was fetched from the laptop browser. The laptop IP is rate limited by web.archive.org. The owner ordered a retry with a new method.

## The new method (proven live)
Fetch the Wayback snapshot from the VM, NOT from the laptop browser. The snapshot and the current page have ALREADY been fetched from the VM (HTTP 200, real content) and placed in this folder:
- /home/james/rung3-chung-cu/R3-040/retry/snapshot-19961231235847.html (archived NASA homepage, 1996-12-31, 6639 bytes, title "NASA Home Page/Mars Pathfinder Sites")
- /home/james/rung3-chung-cu/R3-040/retry/current-nasa.html (current nasa.gov, 356426 bytes)
- /home/james/rung3-chung-cu/R3-040/retry/cdx-nasa.json (CDX snapshot list, oldest timestamp 19961231235847)
Do NOT try to fetch from web.archive.org in the laptop browser again; it will return 429. Use these files.

## Task (R3-040, browser group, difficulty kho)
Page: https://www.nasa.gov/. Archived snapshot: timestamp 19961231235847 (1996-12-31), the oldest readable snapshot.

### Phase A (do NOW, no browser session needed)
1. Read /home/james/rung3-chung-cu/R3-040/retry/current-nasa.html. Note the page title and 3 main content items of the CURRENT version.
2. Read /home/james/rung3-chung-cu/R3-040/retry/snapshot-19961231235847.html. Note the page title and 3 main content items of the ARCHIVED version (1996-12-31). Note the archive date: 1996-12-31.
3. Compare the two versions. Write 3 clear changes, each with the OLD value and the NEW value.
4. Write the result to /home/james/rung3-chung-cu/R3-040/retry/comparison.txt: the current title, the archived title, the archive date (1996-12-31), the 3 content items from each version, and the 3 changes (each with old and new).
5. Report Phase A done and STOP. Do NOT start Phase B yet.

### Phase B (do ONLY when the coordinator tells you the computer-use session is free)
The session is currently held by FCC (r3-fcc-runner, R3-001). Do NOT touch FCC's pane. Do NOT open a browser until the coordinator signals the session is free.
6. Open a new online document, write a 4-row table: columns item, old version, new version, change. 3 change rows (the 3 changes from Phase A).
7. Save the document, reopen it to verify the table is there and correct.
8. Save a screenshot of the document and the document link or path into /home/james/rung3-chung-cu/R3-040/retry/ as Phase B evidence.
9. Report Phase B done.

## Pass criteria
Table has 3 change rows, each with old and new, archive date correct (1996-12-31), title matches both versions. Fail: missing changes, a change without old or new, wrong archive date, or two different pages.

## Rules
- Do NOT retry the Wayback fetch from the laptop browser (429). Use the files in retry/.
- Do NOT start another task after this retry. When the retry is fully done (Phase A + Phase B), report completion and stop.
- Keep the original evidence in /home/james/rung3-chung-cu/R3-040/ intact (the 01-current-nasa.png, 02-wayback-429.png, and other files). Put ALL retry evidence in /home/james/rung3-chung-cu/R3-040/retry/.

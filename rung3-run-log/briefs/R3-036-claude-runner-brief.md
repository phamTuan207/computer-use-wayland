# R3-036 runner brief (Muse lane) - R3-L3, frozen position 27

From: run coordinator epoch 16 (78fd6562). To: Muse lane runner (spawned by the coordinator at release).
Lane note: Muse lane drives R3-036. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | claude-R3-036 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "timeanddate world clock", Return (DuckDuckGo SERP), click the first result (timeanddate.com).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to timeanddate.com world-clock or meeting-planner URLs, DOM clicks, internal setters, test-only endpoints, direct API calls, computing time-zone offsets from memory without reading them on the site. Navigate by clicking visible links and controls; read every offset and local time off the site pages.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Muse --method Muse --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-036/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-036 (frozen list extract)

Schedule a meeting across 3 time zones on timeanddate.com and pick a time that suits all 3 sides.
Cities (in this order): 1. Hanoi  2. Tokyo  3. Sydney
Meeting date: Wednesday 2026-12-02. Working hours are defined as 09:00 to 17:00 local time.

Steps:
1. Open timeanddate.com (user path above). Read the current local time in each of the 3 cities and the time-zone offset differences between the pairs, including daylight saving mode if shown. Screenshot the readings (timestamped).
2. Find the common working-hours window of all 3 cities on 2026-12-02 (the hours when all 3 are inside 09:00-17:00 local).
3. Pick one 60-minute meeting time inside that common window. Record the meeting time in each city's local time.
4. Screenshot the meeting-planner or world-clock view showing the 3 cities and the chosen slot (timestamped).
5. Open a new online document. Write a table of 3 rows (meeting time per city) plus 1 line explaining why that time suits all 3 sides.
6. Save the document, reopen it to check, and screenshot the reopened document.
7. Write ~/rung3-chung-cu/R3-036/ket-qua.txt: the 3 cities with their offsets, the common window, the chosen meeting time in each city's local time, and the explanation line. Values come from the saved screenshots, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-036/ holds ket-qua.txt, timestamped screenshots (city readings, chosen slot view, saved document after reopen), probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

## Bot-check rule + invalid budget (read carefully)

This task is a pre-declared INVALID candidate: timeanddate.com shares a known bot-block cause with an earlier task (R3-011). Invalid budget: the run is AT the invalid cap (5 of 5 used). A shared-cause drop adds 0 new cap events ONLY with browser evidence per task plus scorer-2 confirmation; curl alone is never proof. Your job is evidence, not the ruling: if blocked, evidence the block fully (block screenshot, Ray ID where present, wait log) and report INVALID candidate to the coordinator. Never decide the ruling yourself, never push through a challenge to "save" the task.

Bot-check rule: if the site blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title, URL text, Ray ID, and wait log to ~/rung3-chung-cu/R3-036/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies.

## Completion

Report to the coordinator: task ID R3-036, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then WAIT. Do not start any other task.

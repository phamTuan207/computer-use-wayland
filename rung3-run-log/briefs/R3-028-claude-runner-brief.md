# R3-028 runner brief (Muse lane) - R3-L3 resume, frozen position 24

From: run coordinator epoch 10 (f1dac71f). To: Muse lane runner (spawned by the coordinator at release).
Lane note: Muse lane drives R3-028. Lane-switch agreement rule (check 10): the assigned lane is fixed in this brief. A lane switch (another runner type taking this task) happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently, never let another agent drive it.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | claude-R3-028 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "timeanddate time zone converter", Return (DuckDuckGo SERP), click the first result (timeanddate.com converter page).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to the converter, URL parameters that pre-fill the conversion, DOM clicks on the SERP or the form, internal setters, test-only endpoints. Type and select everything in the visible UI.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Muse --method Muse --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-028/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state. (timeanddate.com holds a cf_clearance cookie; clearing it would break the warm profile.)
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-028 (frozen list section 6 extract)

Convert 3 UTC times to local time in 3 time zones, record the results.
Zones: Asia/Ho_Chi_Minh (Hanoi), Europe/London, America/New_York.
Times (UTC): 1. 2026-12-01 12:00  2. 2026-12-01 18:00  3. 2026-12-02 00:00

Steps:
1. Open the timeanddate.com time zone converter (user path above).
2. For each of the 3 UTC times: set the converter to that date/time in UTC, add the 3 zones, read the 3 local times and each zone's offset from UTC at that moment. Screenshot the result (3 screenshots total, one per UTC time, timestamped filenames).
3. Write ~/rung3-chung-cu/R3-028/ket-qua.txt: for each UTC time, the 3 local times; plus the 3 zone offsets. Values come from the saved screenshots, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-028/ holds ket-qua.txt, 3 timestamped screenshots, probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

## Bot-check rule + invalid budget (check 10, read carefully)

Invalid budget: the run has ONE invalid slot left (4 of 5 used; the next invalid event is number 5, the cap). This task is a pre-declared INVALID candidate: timeanddate.com was browser-blocked in an earlier task (R3-011) and the key declares this task invalid if the site is browser-blocked at run time. A shared-cause drop for this task adds ZERO cap events ONLY with browser evidence filed for this task plus scorer-2 confirmation. Your job is evidence, not the ruling: if blocked, evidence the block fully (below) and report INVALID candidate to the coordinator. Never decide the ruling yourself, never push through a challenge to "save" the task.

Bot-check rule: if the site blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page instead of the converter), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title and URL text to ~/rung3-chung-cu/R3-028/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies.

## Completion

Report to the coordinator: task ID R3-028, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then WAIT. Do not start any other task.

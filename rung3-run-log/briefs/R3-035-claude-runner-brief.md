# R3-035 runner brief (Muse lane) - R3-L3, frozen position 26

From: run coordinator epoch 16 (78fd6562). To: Muse lane runner (spawned by the coordinator at release).
Lane note: Muse lane drives R3-035. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | claude-R3-035 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "xe currency converter", Return (DuckDuckGo SERP), click the first result (xe.com).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to xe.com converter URLs, DOM clicks, internal setters, test-only endpoints, direct API calls, using a stored or cached exchange rate without a live source screenshot. Enter amounts and currencies through the visible converter form.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Muse --method Muse --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-035/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-035 (frozen list extract)

Convert 3 amounts in 3 currencies into one target currency (VND) on xe.com, then sum the results.
Conversions (in this order): 1. 100 USD to VND  2. 50 EUR to VND  3. 200 GBP to VND

Steps:
1. Open xe.com (user path above). For each of the 3 conversions, enter the amount and the currency pair in the visible converter, and record the exchange rate used and the converted result.
2. Screenshot each conversion result with the rate and result visible (timestamped, 3 screenshots).
3. Add the 3 results together; record the total converted value.
4. Open a new online document. Write a table of 4 rows: the 3 conversions (amount, pair, rate, result) and 1 total row.
5. Save the document, reopen it to check, and screenshot the reopened document showing the 4-row table.
6. Write ~/rung3-chung-cu/R3-035/ket-qua.txt with the same 4-row table (3 conversions with rates and results, plus the total). Values come from the saved screenshots, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-035/ holds ket-qua.txt, 3 timestamped conversion screenshots, 1 timestamped screenshot of the saved online document after reopen, probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

## Bot-check rule + invalid budget (read carefully)

Invalid budget: the run is AT the invalid cap (5 of 5 used). Any new invalid event needs a new recorded team decision before further releases. Your job is evidence, not the ruling: if blocked, evidence the block fully and report INVALID candidate to the coordinator. Never decide the ruling yourself, never push through a challenge to "save" the task.

Bot-check rule: if the site blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title and URL text to ~/rung3-chung-cu/R3-035/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies.

## Completion

Report to the coordinator: task ID R3-035, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then WAIT. Do not start any other task.

# R3-046 runner brief (Codex lane) - R3-L3, frozen position 30

From: run coordinator epoch 23 (0d5fb18c). To: Codex exec runner (launched by the coordinator's driver at release).
Lane note: Codex exec drives R3-046. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. Full access (--sandbox danger-full-access). English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | codex-R3-046 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none beyond drive scripts): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

Graphify for codebase context: query ~/workspace/cu-graphify/graphify-out/ instead of re-reading code.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "timeanddate sunrise sunset", Return (DuckDuckGo SERP), click the first result (timeanddate.com Sunrise and Sunset).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to a timeanddate.com sun URL, DOM clicks on the SERP, internal setters, test-only endpoints, direct API calls, terminal date tools to compute the values yourself. Pick each city and date through the visible site form and read the values off the rendered page.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Codex --method Codex --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-046/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-046 (frozen list extract)

Look up sunrise and sunset times for 3 cities on 2 dates on timeanddate.com, compute the day length for each, and the day-length difference between the 2 dates for each city.
Cities (in this order): Ha Noi, London, Sydney.
Date 1: 2026-12-02. Date 2: 2027-06-02 (exactly 6 months after date 1).

Steps:
1. Open the timeanddate Sunrise and Sunset section (user path above).
2. For Ha Noi on 2026-12-02: record sunrise time, sunset time, day length. Screenshot the result (timestamped).
3. Repeat for London and Sydney on 2026-12-02 (screenshot each).
4. Repeat all 3 cities on 2027-06-02 (screenshot each).
5. Compute the day-length difference between the 2 dates for each city (date 2 minus date 1; state the sign).
6. Write ~/rung3-chung-cu/R3-046/ket-qua.txt in exactly this format (values from the saved screenshots, never from a live re-run):

R3-046 ket-qua
Ha Noi | 2026-12-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
Ha Noi | 2027-06-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
Ha Noi | day-length difference (2027-06-02 minus 2026-12-02): <value>
London | 2026-12-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
London | 2027-06-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
London | day-length difference (2027-06-02 minus 2026-12-02): <value>
Sydney | 2026-12-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
Sydney | 2027-06-02 | sunrise <HH:MM> | sunset <HH:MM> | day length <H:MM:SS>
Sydney | day-length difference (2027-06-02 minus 2026-12-02): <value>

Evidence: ~/rung3-chung-cu/R3-046/ holds ket-qua.txt, 6 timestamped result screenshots (one per lookup), probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

Bot-check rule: if a service blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title, URL text, Ray ID, and wait log to ~/rung3-chung-cu/R3-046/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies. Invalid budget note: under the owner ruling of 2026-11-26, external service blocks do not consume the invalid cap; your job is evidence, not the ruling. This task is in the timeanddate shared-cause group (R3-011/028/036/046); per-event counting applies, so record the block evidence completely.

## Completion

Report to the coordinator: task ID R3-046, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then WAIT. Do not start any other task.

# R3-045 runner brief (Codex lane) - R3-L3, frozen position 29

From: run coordinator epoch 21 (f79cb9eb). To: Codex exec runner (launched by the coordinator's driver at release).
Lane note: Codex exec drives R3-045. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. Full access (--sandbox danger-full-access). English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | codex-R3-045 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none beyond drive scripts): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

Graphify for codebase context: query ~/workspace/cu-graphify/graphify-out/ instead of re-reading code.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "ezgif gif maker", Return (DuckDuckGo SERP), click the first result (ezgif.com GIF Maker).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to ezgif.com/maker, DOM clicks on the SERP, internal setters, test-only endpoints, direct API calls, terminal image tools to build the GIF yourself. Enter the 3 image URLs through the visible maker form and use the visible Upload and Make a GIF controls.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Codex --method Codex --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-045/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-045 (frozen list extract)

Create a GIF on ezgif.com with 3 frames, set the delay, check the frame count.
Source images (use in this order):
1. https://picsum.photos/seed/r3a/400/300
2. https://picsum.photos/seed/r3b/400/300
3. https://picsum.photos/seed/r3c/400/300

Steps:
1. Open the ezgif GIF Maker (user path above). Record the page title.
2. Enter the 3 image URLs in the maker form, click Upload.
3. Set each frame's delay to 50 (i.e. 500 ms). Verify all 3 frames show delay 50. Screenshot (timestamped).
4. Click Make a GIF, wait for the result, record the frame count of the created GIF. Screenshot the result showing the frame count (timestamped).
5. Download the GIF file and save it to ~/rung3-chung-cu/R3-045/anh-dong.gif.
6. Write ~/rung3-chung-cu/R3-045/ket-qua.txt: the 3 source image URLs, the delay of each frame, the frame count, and the downloaded GIF filename. Values come from the saved screenshots and the downloaded file, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-045/ holds ket-qua.txt, anh-dong.gif, timestamped screenshots (maker page with delays, result with frame count), probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

Bot-check rule: if a service blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title, URL text, Ray ID, and wait log to ~/rung3-chung-cu/R3-045/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies. Invalid budget: the run is AT the invalid cap (5 of 5 used); your job is evidence, not the ruling.

## Completion

Report to the coordinator: task ID R3-045, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then WAIT. Do not start any other task.

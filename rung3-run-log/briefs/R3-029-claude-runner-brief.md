# R3-029 runner brief (Muse lane) - R3-L3, frozen position 25

From: run coordinator epoch 10 (f1dac71f). To: Muse lane runner (spawned by the coordinator at release).
Lane note: Muse lane drives R3-029. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

The test-account password is given to you in your spawn message ONLY. It is never written in any file, log, screenshot caption, or report. Type it only into the site's password field. Never echo it back.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | claude-R3-029 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "ecommerce playground lambdatest", Return (DuckDuckGo SERP), click the first result (ecommerce-playground.lambdatest.io).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to the store or to product/wishlist pages, DOM clicks, internal setters, test-only endpoints, direct API calls to the wishlist. Navigate by clicking visible links and buttons; log in through the visible login form.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent Muse --method Muse --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-029/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-029 (frozen list section 6 extract)

On the LambdaTest demo store, use the test account's wishlist with 5 products.
Test account email: rung3-029-test@example.com (password in your spawn message only; test-only account, never a real account).
Products (in this order): 1. iPhone  2. MacBook  3. Canon EOS 5D  4. HP LP3065  5. HTC Touch HD

Steps:
1. Open the demo store (user path above). Log in with the test account through the visible login form.
2. Find each of the 5 products (search or category navigation by clicks) and add each to the wishlist.
3. Open the wishlist page. Verify it lists all 5 products. Screenshot (state: 5 saved).
4. Remove "Canon EOS 5D" from the wishlist. Verify the list now has 4. Screenshot (state: 4 saved).
5. Add "Canon EOS 5D" to the wishlist again. Verify the list has 5 again. Screenshot (state: 5 saved again).
6. Write ~/rung3-chung-cu/R3-029/ket-qua.txt: the 5 product names, the count at each of the 3 states (5, 4, 5), and the screenshot filenames. Values come from the saved screenshots, never from a live re-run.
7. Log out of the test account before ending (leave no signed-in session).

Evidence: ~/rung3-chung-cu/R3-029/ holds ket-qua.txt, 3 timestamped wishlist screenshots, probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze. Screenshots must not show the password (it is typed into a masked field; never screenshot a filled password field in clear text).

## Bot-check rule + invalid budget (read carefully)

Invalid budget: the run is AT the invalid cap (5 of 5 used). Any new invalid event needs a new recorded team decision before further releases. Your job is evidence, not the ruling: if blocked, evidence the block fully and report INVALID candidate to the coordinator. Never decide the ruling yourself, never push through a challenge to "save" the task.

Bot-check rule: if the site blocks you (bot check, Turnstile, 429, 403, "Just a moment", a challenge page), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page (full page, timestamped), save the page title and URL text to ~/rung3-chung-cu/R3-029/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task, do not clear cookies. If the login fails (wrong password, account locked), STOP and report exactly what the page said; do not retry the password more than once, do not attempt a password reset.

## Completion

Report to the coordinator: task ID R3-029, your session id, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Never include the password in the report. Then WAIT. Do not start any other task.

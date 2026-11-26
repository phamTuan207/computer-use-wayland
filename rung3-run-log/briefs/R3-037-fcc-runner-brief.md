# R3-037 runner brief (FCC lane) - R3-L3, frozen position 28

From: run coordinator epoch 16 (78fd6562). To: FCC agent, tmux r3-fcc-runner-L3.
Lane note (re-plan 2026-11-26): FCC drives R3-027 and R3-037 only. This brief releases R3-037 ONLY, and only after the coordinator sends the release message. Do not start until released.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; close only your own task tabs when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. Full access (fcc --dangerously-skip-permissions). English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest. (On the laptop, append "ISO-ts | fcc-R3-037 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "who.is", Return (DuckDuckGo SERP), click the first result (who.is).
Forbidden shortcuts for this test: deep link or direct BiDi navigate to who.is result URLs, DOM click on the SERP, internal setters, test-only endpoints, direct WHOIS API calls, terminal whois command. Enter each domain through the visible who.is search form.

## Holder discipline (Cloudflare shim, mandatory per drive)

1. Verify holder hashes before starting (no drive on mismatch):
   - /tmp/fixb-runner/holder-fixb.mjs = 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213
   - /tmp/fixb-runner/probe-fixb.mjs = 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9
2. Acquire the pill first (overlay.py acquire --agent FCC --method FCC --pid <your-pid>; fail closed if visible is not true).
3. Clear /tmp/fixb-rpc and /tmp/fixb-gate. Start the holder detached with display env from the live Zen environ. Wait for /tmp/fixb-rpc/ready.json.
4. Probe fail-loud: ready.json must read webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring verbatim (expected empty-name form). Copy ready.json to ~/rung3-chung-cu/R3-037/probe-ready.json (it enters the snapshot manifest chain). ANY mismatch: stop the holder, release the pill, report. Never drive unshimmed.
5. Warm-profile rule: do NOT clear any cookies on any host. Cookies are run state.
6. Drive the task in the holder's held tab via real input (act-now) and holder RPC reads. While the holder owns the BiDi session, do NOT open zen_dom or zen_cli short sessions.
7. At task end: write /tmp/fixb-rpc/stop, wait for clean holder end (preload_removed, context_closed, session_ended, done), release the pill, verify pill gone by grim.

## Task R3-037 (frozen list extract)

Look up WHOIS registration information for 2 domains on who.is and record the expiry dates.
Domains (use in this order): 1. example.com  2. wikipedia.org

Steps:
1. Open who.is (user path above). Enter the first domain in the search form. If the page shows reCAPTCHA or asks for human verification, STOP, record that clearly in ket-qua.txt, and report to the coordinator (the task is then an INVALID candidate per list section 1). Do not solve the challenge.
2. Record the registrar name, registration date, expiry date, and name servers for the domain.
3. Repeat with the second domain.
4. Record the status of both domains: still valid or expired.
5. Save timestamped screenshots of the results for both domains (one per domain, 2 total) to ~/rung3-chung-cu/R3-037/.
6. Write ~/rung3-chung-cu/R3-037/ket-qua.txt: 2 rows, each row has the domain, registrar, expiry date, name servers, plus the status of each domain. Values come from the saved screenshots, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-037/ holds ket-qua.txt, 2 timestamped screenshots, probe-ready.json, start_time.txt, end_time.txt. Every file mtime inside the run window. Report values come from saved files, never from a live re-run. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

Bot-check rule: if a service blocks you (bot check, Turnstile, 429, 403, "Just a moment"), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page, save the page title and URL text to ~/rung3-chung-cu/R3-037/block-evidence.txt, report INVALID candidate to the coordinator. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task. Invalid budget: the run is AT the invalid cap (5 of 5 used); your job is evidence, not the ruling.

## Completion

Write a short completion report in this pane: task ID R3-037, session r3-fcc-runner-L3, evidence folder path, start/end wall-clock times, probe fields, any pill gap, anything unusual. Then WAIT for the next assignment. Do not start any other task.

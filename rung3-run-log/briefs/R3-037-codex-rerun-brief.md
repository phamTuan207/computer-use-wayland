# R3-037 rerun runner brief (Codex lane) - R3-L3 rerun, owner order 2026-11-28

From: rerun coordinator (Muse subagent). To: Codex exec runner (gpt-6-luna, --sandbox danger-full-access).
Lane note: this is a RERUN of R3-037 (original run by FCC lane 2026-11-26 hit the 30-minute cap, FAIL). Counting Rule A: a rerun PASS replaces the FAIL; originals preserved. A failed rerun gets NO second rerun. Lane is fixed: Codex exec only. If you cannot proceed in this lane, stop and report; never hand off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared Zen; never drive while another runner holds the Zen. Never close or navigate owner-opened tabs, pinned tabs, or essentials; drive only your own new task tab, close only it when done. ws3 untouched; work on ws2. Never restart Zen, never change launcher/wrapper/prefs. Never clear cookies on any host (warm-profile rule). Full access (--sandbox danger-full-access). English only in all files and logs. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger (R3-L3-grades.jsonl, R3-L3-reruns.jsonl), or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events (start, lane checks, each domain result, block events, end) by appending "ISO-ts | codex-R3-037-rerun | <event>" to ~/agent-event-log/events.log on the laptop, and keep a super-detailed drive log (fail, reasoning, tried, decision, fix, result) at ~/rung3-chung-cu/R3-037-rerun/drive.log with wall-clock Asia/Ho_Chi_Minh timestamps and elapsed time.

Ponytail (applies if you write any code; this task needs none beyond drive commands): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: Zen address bar, type "who.is", Return (DuckDuckGo SERP), click the first result (who.is).
Forbidden shortcuts for this test: deep link or direct navigate to who.is result URLs (including rdp_client.py navigate to a who.is URL), DOM click on the SERP, internal setters, test-only endpoints, direct WHOIS API calls, terminal whois command. Enter each domain through the visible who.is search form.

## RDP lane discipline (replaces the old holder/BiDi discipline; owner Zen is flag-free since R10)

Owner permission (2026-11-28 10:20): you MAY operate directly on the owner's live Zen (PID 807599, port 6021); it is the real-combat Zen. Still: never close or navigate owner-opened tabs/windows, never compositor window-close on his workspace.

Attempt note: two earlier launches (10:18-10:20 and 10:22-10:25) stopped fail-closed before any page interaction (brief errors: Ctrl+T is refused by cu.py in Zen; Ctrl+N opens the Zen search panel but creates no RDP tab descriptor until commit). Archive any pre-existing files in ~/rung3-chung-cu/R3-037-rerun/ into ~/rung3-chung-cu/R3-037-rerun/attempt1-aborted/ and attempt2-aborted/ before starting, then run fresh. This is the same single rerun, not a second one.

1. Lane health first (fail closed): run the RDP smoke on the owner channel:
   python3 ~/.config/agent-computer-use/machine/bin/rdp_smoke.py --port 6021 --profile-marker ae59l0ak.Default
   Exit 0 required. Save its JSON output to ~/rung3-chung-cu/R3-037-rerun/rdp-smoke.json. Nonzero exit: stop, report, do not drive.
2. Display env: source XDG_RUNTIME_DIR, WAYLAND_DISPLAY, DBUS_SESSION_BUS_ADDRESS, HYPRLAND_INSTANCE_SIGNATURE from the live Zen process environ (/proc/<zen-pid>/environ) for every GUI command. Work on workspace 2.
3. Acquire the pill before any control: python3 ~/computer-use-wayland/scripts/overlay.py acquire --agent Codex --method Codex --pid <your-pid>; fail closed if visible is not true.
4. Tab scoping (RT-20): every rdp_client.py command needs a scope. List tabs with:
   python3 ~/.config/agent-computer-use/machine/bin/rdp_client.py --port 6021 --profile-marker ae59l0ak.Default --scope-url-pattern "*" tabs
   Record the descriptors (tabs-before). Provision your OWN task tab via RDP parent evaluate (proven 2026-11-28; Ctrl+N only opens the Zen search panel and creates no descriptor until commit, so do not use it):
   python3 ~/.config/agent-computer-use/machine/bin/rdp_client.py --port 6021 --profile-marker ae59l0ak.Default --scope-url-pattern "*" --allow-parent peval "(() => { const w = Services.wm.getMostRecentWindow(\"navigator:browser\"); const t = w.gBrowser.addTab(\"about:blank\", {triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal()}); w.gBrowser.selectedTab = t; return \"idx:\" + w.gBrowser.tabs.indexOf(t); })()"
   List tabs again: the new descriptor that was not in tabs-before is your task tab. Verify via peval that gBrowser.selectedTab is your new tab (index matches). Scope every further RDP read/action with --scope-tab-id <your descriptor>. Never act on any other tab. Tab provisioning via peval is infrastructure only; it is never used to navigate to task content.
5. User-path entry with real input (cu.py act-now): Ctrl+L, type "who.is", Return, wait for the DuckDuckGo SERP, click the first result (who.is) with real input (ground the click via cu.py observe / RDP snapshot coordinates). Verify via RDP snapshot that the SERP landed before clicking; if the browser navigated directly to who.is instead of the SERP, record the deviation in drive.log, go back, and redo the entry via search. DOM reads via rdp_client.py snapshot/eval on your scoped tab are allowed for reading and verifying; all clicks and typing are real input via act-now.
6. Warm-profile rule: do NOT clear any cookies on any host.
7. At task end: close only your own task tab via peval (select a neighbor tab first, verify the task tab by descriptor/URL, then removeTab), release the pill (overlay.py release --agent Codex), verify pill gone by grim screenshot saved as pill-gone.png.

## Task R3-037 (frozen list extract, unchanged)

Look up WHOIS registration information for 2 domains on who.is and record the expiry dates.
Domains (use in this order): 1. example.com  2. wikipedia.org

Steps:
1. Open who.is (user path above). Enter the first domain in the search form. If the page shows reCAPTCHA or asks for human verification, STOP, record that clearly in ket-qua.txt, and report (the task is then an INVALID candidate per list section 1). Do not solve the challenge.
2. Record the registrar name, registration date, expiry date, and name servers for the domain.
3. Repeat with the second domain.
4. Record the status of both domains: still valid or expired.
5. Save timestamped screenshots of the results for both domains (one per domain, 2 total) to ~/rung3-chung-cu/R3-037-rerun/.
6. Write ~/rung3-chung-cu/R3-037-rerun/ket-qua.txt: 2 rows, each row has the domain, registrar, expiry date, name servers, plus the status of each domain. Values come from the saved screenshots, never from a live re-run.

Evidence: ~/rung3-chung-cu/R3-037-rerun/ holds ket-qua.txt, 2 timestamped screenshots, rdp-smoke.json, start_time.txt, end_time.txt, drive.log, pill-gone.png. Every file mtime inside the run window. Write start_time.txt (ISO 8601 +07:00) at drive start and end_time.txt at drive end. Report values come from saved files, never from a live re-run. Verify every action by DOM or file read-back, never by the act ok flag alone. After each state-changing action, screenshot and hash; unchanged hash after a state change: retry once, then report a freeze.

Bot-check rule: if a service blocks you (bot check, Turnstile, 429, 403, "Just a moment"), STOP. Record the Ray ID if shown, wait 60 seconds, screenshot the block page, save the page title and URL text to ~/rung3-chung-cu/R3-037-rerun/block-evidence.txt, report INVALID candidate. Do not hammer the service, do not open many tabs, do not try a workaround that changes the task.

## Completion

Write a completion report to ~/rung3-chung-cu/R3-037-rerun/completion-report.txt: task ID R3-037 (rerun), your session id, evidence folder path, start/end wall-clock times, smoke result, any pill gap, anything unusual, and whether the drive completed or hit a block (with the block evidence path). Then STOP. Do not start any other task.

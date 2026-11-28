# Worker Y3 verification: clone1-batch3 tests + error-summary gap audit

- Worker: Y3 (Muse subagent). Date: 2026-11-21, 17:47-19:10 +07.
- Scope: (1) verify clone1-batch3's 10 tests in tests/realistic/clone1-batch3/ (t01-t10) against Worker P's standards; (2) audit ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (parts A-I) for coverage gaps.
- Method note (honest): fcc was assigned this verification but could not do it. See "fcc failure record" below. The verification below was done by Worker Y3 (Muse) directly by reading every file, then debated by a Muse council (3 members) + redteam. The debate record at the end lists every overturn and correction accepted. fcc's own partial output (t01/t02 PASS, run 1) is included and attributed to fcc.

## fcc failure record (what was tried)

- 17:49 run 1 (detached setsid nohup, positional prompt): log 0 bytes, no fcc process visible by grep at +25s/+70s. First read as "died like K2".
- Probes: trivial prompt foreground 25s, no output, exit 124 (timeout). `--prompt` flag does not exist in fcc 2.1.329 ("unknown option --prompt"). Trivial prompt foreground 28s with </dev/null, no output, exit 124.
- Long probe (120s timeout, trivial prompt): returned OK, exit 0. fcc is alive but first token takes 30-85s+; earlier "deaths" were partly misread (grep missed the process; pstree later showed the full tree alive).
- Run 1 relaunch (bash -c wrapper, prompt via $(cat)): completed 18:02, exit 0, but stopped after 2 of 10 tests, wrote no report files, emitted Y3-FCC-DONE pass=0 fail=0 gaps=0. Its t01/t02 verdicts (both PASS, with reasoning) are in the laptop log /tmp/y3/fcc-run.log (read via SSH; that path does not exist on the VM, so the council could not re-read it directly, but Council 1's independent read reaches the same verdicts for the same reasons).
- Run 2 (t03-t10 + Part 2 + debate): stalled. claude CPU 00:00:03 at 15 min, 00:00:04 at 19 min, 0 bytes output, no report growth. Killed 18:22.
- Run 3 (chunk t03-t05): stalled the same way. claude CPU 00:00:02 at 11 min, 0 bytes. Killed 18:34.
- fcc-server restart: killed PID 15135 (up since 15:24), it auto-restarted (new PID 229108, http://127.0.0.1:8082). Trivial probe after restart: 120s, no output, exit 124. Restart did NOT help. Conclusion: the upstream free provider is saturated tonight (opencode free also hit its limit 18:08). fcc is unusable for this task right now, not dead forever.
- Per the brief, the same prompt was NOT retried a third time unchanged. Run 2 was a continuation, run 3 a smaller chunk, then the server restart, then direct verification by Y3.

## Part 1: test verdicts (t01-t10)

Standards applied (Worker P): (1) fixture must not self-simulate the task; (2) verify hooks must be real DOM assertions, not fixture-defined self-checking hooks; (3) spec achievable with the actual UI; (4) 15-40 realistic steps; (5) no hard-coded coordinates as the answer, no timing races, no placeholder/TODO; (6) results.json claims checked against the files.

| Test | Verdict | Reason / defect |
|---|---|---|
| t01-terminal | PASS | 20 steps. Checker drives real keyboard (click #cmd, type, Enter, ArrowUp) and reads textContent/inputValue. Fixture is a real terminal emulator (virtual FS, real keydown handler). One $$eval is a DOM count read only. No evaluate, no self-hook. Concurs with fcc run 1 and results.json pass. Council 1 confirmed by hand. |
| t02-spreadsheet | PASS | 19 steps. Checker uses page.fill (real input events drive recalc) + inputValue exact reads. Fixture is a real formula engine (SUM/AVERAGE/binops, multi-pass dependency resolution, #ERR). All README arithmetic verified by hand (C1 90 after A1=40, D5 0.5 after A3=10, etc.). Concurs with fcc run 1 and results.json pass. Council 1 confirmed by hand. |
| t03-video-call | PASS | 19 steps. Real clicks/fills; textContent/isVisible/getAttribute/$$eval reads. Fixture implements every asserted state (join/leave, mute/cam/hand toggles, chat log, share tile add/remove with count, invite/remove Cara). No evaluate. results.json pass. Council 1 confirmed by hand. |
| t04-email-client | PASS | 19 steps. Real fills/clicks/locator nth(). Fixture inbox order [invoice, weekly sync notes, system maintenance] matches the checker's nth(1) star and nth(2) delete assumptions; star/delete/send/search/empty-state all real DOM. results.json pass. Council 1 confirmed by hand. |
| t05-file-manager | FAIL | Self-simulated rename (Council 2 overturn, accepted). The rename handler (fixture.html:151-156) has no input for a new name; it hardcodes the outcome: notes.txt always becomes meeting-notes.txt, Archive always becomes Old files. The checker then asserts those predetermined strings, so a broken rename that always returned meeting-notes.txt would pass. The rename capability (taking a user-supplied name and applying it) does not exist in the fixture. The README discloses the fixed mapping, but disclosure does not cure it: standard (1) has no disclosure exception. Y3 originally passed this with a "limitation noted"; the council overturned it, and Y3 accepts: a self-simulated rename in two of twenty steps deserves the same treatment as the single-defect FAILs below. Fix: add a rename text input, have the checker type a name, assert that name appears. Sort orders, delete confirm/cancel, and move in/out are real DOM flows and check out. |
| t06-calendar | PASS | 17 steps. Real clicks/fills; $$eval chip reads. Fixture renders chips in creation order (fixture.html:85-86), so the checker's nth(1)=Lunch holds under creation order and time order. Form/details/edit/delete/month nav/Today all real DOM. results.json pass. Council 2 confirmed by hand. |
| t07-code-editor | PASS | 17 steps. Real fills/clicks/reloads; fixture is a real editor (Function eval, localStorage editor: keys, dirty marks, find/replace). Fresh browser per launch (lib/browser.mjs:53, no userDataDir) so no localStorage leak across runs. results.json pass, details.lines "1" consistent. Council 2 confirmed by hand. |
| t08-settings-panel | PASS | 16 steps. Real selectOption/check/uncheck/fill/keyboard/slider. Slider Home + 70x ArrowRight is deterministic (click focuses, Home resets to 0, step is 1). Swatch read is inline style set by apply(). Search 'theme' matches only Appearance keywords. Reset saves defaults to localStorage. results.json pass. Council 2 confirmed by hand. |
| t09-multi-window | FAIL | Flaky by construction: postMessage delivery race (Council 3 + redteam confirmed). check.mjs asserts main-window body class immediately after `await closed` (first prefs dark assert line 89, light 94-95, second dark 108-109) with no wait for the opener's message handler to run. prefs.html posts the theme then closes synchronously; delivery is async and unordered vs the checker's CDP read. The same race affects the rename asserts (lines 74, 84, 113) and the status assert (lines 76-78), which happened to pass in the recorded run. Proven by clone1's own results.json AND coord record: run 1 failed on the click race ("Target page, context or browser has been closed"), clone1 added the clickAndClose helper, re-run 1 passed 10/10, re-run 2 (the committed results.json, 09:41 UTC, post-fix code, load average 7.68, 9 agents in parallel) failed t09 with "main window missing dark class after prefs dark" while the identical second apply passed. The clickAndClose helper (commit 1767d4c, "t09 close race fix") fixed the Playwright click race, not this delivery race. Fix: wait for the expected state (waitForFunction on body class / status text) instead of asserting immediately. |
| t10-music-player | FAIL | Flaky by construction: exact-zero position race (Council 3 + redteam confirmed). check.mjs line 62 clicks Next, line 63 does expectText on now-playing (one CDP round trip), line 64 asserts `position() !== 0` fails (a second round trip). Fixture nextTrack() resets position to 0 but never stops the 100ms timer (fixture.html line 88 setInterval; only the end-of-queue branch calls stopTimer), so a tick can set position to 1 before the read lands. Proven by results.json: positionAfter700ms=7 (timer healthy), the failure is exactly that assertion, all other steps passed. Fix: pause before Next, or assert position <= 1, or waitForFunction. |

Counts: 7 PASS, 3 FAIL. Clone1's own committed results.json shows 8 passed / 2 failed (t09, t10); Y3's count is 7/3 because t05's rename is also defective (a vacuous assertion passing is expected, not evidence of validity). The batch-3 "done" claim is contradicted by its own results file either way.

Notes on fcc's run-1 verdicts: fcc judged t01/t02 PASS with reasoning matching the independent read above (real keyboard/DOM for t01, DOM spreadsheet with in-page recalc for t02). Council 1 could not re-read fcc's reasoning text (the log lives on the laptop at /tmp/y3/fcc-run.log, not on the VM) but its independent read reaches the same verdicts for the same reasons.

Cross-check vs Worker P's live run: P ran clone1 t01-t10 live on Zen 10/10 PASS (9/10 in the first full run, t06 flake then 3/3). That does NOT refute the FAILs: a structural race with per-run failure probability p passes with probability (1-p)^n, so a 10/10 pass is expected whenever p is modest, and clone1's own committed run is direct empirical evidence that both failure modes actually occur. A 10/10 pass bounds the failure rate; it does not disprove the race. (Council 3.)

## Minor defects Y3 missed (found by council)

- t01: `details.historyLines` is always 0. The regex `/\d+\s+.*\n/g` runs against textContent('#output'), but textContent concatenates the `.line` divs with no newlines. Cosmetic only; not asserted. (Council 1.)
- t04: after unstarring in the Starred folder, the checker asserts only `starred-count` 0, not that the Starred list itself empties. Weak assertion, not a fail. (Council 1.)
- t05: after the folder rename, the tree button id becomes `tree-old-files`, but the checker never asserts it, unlike step 8 where it checks `#tree-archive` exists. Coverage gap only. (Council 2.)
- t09: the delivery race also affects the rename asserts (lines 74, 84, 113) and the status assert (lines 76-78), not only the prefs asserts. Strengthens the FAIL. (Council 3.)

## Part 2: error-summary gap audit

File audited: ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (646 lines, parts A-I).
Status definitions: FIXED = a fix exists with evidence (commit, test, file, or a recorded standing rule for process errors, labelled "rule"). OWNED = assigned to a person, goal, work item, or experiment, but not done. UNOWNED = no fix, no owner, no test. CLOSED = a terminal fact acknowledged, not fixable.
Gap flag: an item with no fix AND no test is a gap even when nominally owned. The "Gap?" column marks it.
Debate note: the redteam downgraded five rule-only FIXED rows to OWNED (A7, D1, G19, G22, I35) on the bar that a rule counts as FIXED only when it reaches the actor before acting AND is machine-checked or observed in compliance. Rows that survive as FIXED (rule) are the ones with a brief_check.py needle or code behind them (A1, A5, A6, C6, C7, D2, D3, D4, D5). The next-weakest rule-only rows, flagged but not downgraded by the redteam: I25, I19, I24 (prose-only, no checker needle, no test).

### A. System errors (A1-A9)

| ID | Status | Evidence |
|---|---|---|
| A1 | FIXED (rule) | First-step research rule, MEMORY.md:87 ("on any task, FIRST research and re-read the whole workflow"); brief_check.py machine-checks research-first (redteam). Draft originally cited AGENTS.md; corrected by Council 1. |
| A2 | FIXED (rule) | MEMORY.md standing rule SAVE THE WORKING METHOD, REUSE IT VERBATIM |
| A3 | FIXED (rule) | 20 errors added to problem-3 prompt (codex-problem3-prompt.md items 1-20) + 2 items added to workflow; completed by I46 (see contradiction 4) |
| A4 | FIXED (rule) | MEMORY.md standing rule MONITOR AND NOTIFY ON TASK COMPLETION |
| A5 | FIXED (rule+code) | MEMORY.md standing rule REPORT BLOCKERS EARLY (20/11); 3.5-min threshold, commit 6f055e1 (changed scripts/cu.py) |
| A6 | FIXED (rule) | MEMORY.md standing rule KILL STUCK SUBAGENTS (14/11); watchdog 15-min cadence, kills on first STALL flag (Council 1 did not independently verify the cron half; Y3 verified it from the watchdog job definition) |
| A7 | OWNED | Downgraded by Council 1 + redteam. The cited "say I don't know" text does not exist in SOUL.md or IDENTITY.md; the SOUL line ("every claim verified against its source") is a pre-existing persona line, not a fix recorded in response to A7. Worse, the principle predated the failures and did not prevent them (I19, I20, I24 are all 20/11 fabrications). The 06/11 QC rule (independent QC verifies against primary source) is a partial mitigation that demonstrably did not prevent the 20/11 fabrications. Needs a checkable gate (brief_check needle or claim-source checklist). Gap? YES |
| A8 | FIXED | Corrected evidence per Council 1: the two specific false claims are directly corrected in codex-problem3-prompt.md item 8 (numeration error BLOCKS packaging, renumber 1-N) and item 14 (verification failed is not a stop), plus workflow file lines 143-148. Y3's original SOUL citation did not support it. |
| A9 | OWNED | Workflow file + Hieu's allowance (self-written solution OK if reported); no standing-rule text found for "report before writing". Gap? YES (thin) |

### B. Upload-task errors (B1-B14)

All 14 fixed by the completed upload itself. Evidence (shared, corroborated by Council 1 in local logs): all 3 problems in Codeforces contest 732869 as NB1/NB2/NB3, packages READY (P1 invocation 2685536 30/30, P2 2685515 28/28, P3 2685907 30/30); durable fix is ~/workspace/cf26-upload/QUY-TRINH-UP-DE-POLYGON-CODEFORCES-2026-11-20.md.

| ID | Status | Evidence |
|---|---|---|
| B1 | FIXED | .cpp re-upload, package READY (see shared evidence) |
| B2 | FIXED | Codes NB1/NB2/NB3 set in contest |
| B3 | FIXED | Duplicate tests deleted (tests 20 and 27, renumbered 1-28) |
| B4 | FIXED | Tests renumbered 1-N, package built |
| B5 | FIXED | New Standard package per revision, Verify on |
| B6 | FIXED | Hash-format link used |
| B7 | FIXED | English statement only, vietnamese statement deleted |
| B8 | FIXED | Closing $ added in Notes |
| B9 | FIXED | Hover-off-center Browse trick (G21, commit 52f3458) |
| B10 | FIXED | Zen-only rule, tab already logged in |
| B11 | FIXED | No URL typing by key events; use open tab / link click |
| B12 | FIXED | Input-only zip used (candies_range_sum_polygon_tests_input_only.zip exists) |
| B13 | FIXED | Missing test added by hand |
| B14 | FIXED | Verification-failed is not a stop rule (Hieu's flow) |

### C. Computer-use errors (C1-C8)

| ID | Status | Evidence |
|---|---|---|
| C1 | FIXED | Observation limit 90s to 120s (I42); scripts/cu.py:48 OBSERVATION_MAX_AGE = 120, line 746 raises on stale observations; commit 6f055e1; scripts/timing.py + scripts/step_watchdog.py exist (Council 2) |
| C2 | OWNED | Downgraded by Council 2. Y3's citation ("todolist Phase 2") was wrong: no fresh-observe-after-navigation rule exists in the todolist doc. What exists is the doc-recorded rule itself (error doc lines 114-117) plus the general stale-observation guard in scripts/cu.py:735-779. No specific fresh-observe-after-navigation implementation found. Gap? YES (thin) |
| C3 | FIXED | scripts/cu.py:1425-1438 refuses Ctrl+T when the target window is Zen, with test tests/test_phase3_c3.py (Council 2) |
| C4 | FIXED | Commit Changes link location documented (end of right column); for a location-knowledge fix the doc record is the fix |
| C5 | FIXED | Dashboard > View Problems > Continue path documented |
| C6 | FIXED (rule) | ydotool ban restated in every brief (MEMORY.md lesson 17/11); brief_check.py machine-checks it (redteam) |
| C7 | FIXED (rule) | Narrate-each-step standing rule (MEMORY.md, the owner 20/11); brief_check.py covers it (redteam) |
| C8 | FIXED | Cleanup checklist (end broker session, pill gone via grim, desktop clean); matches MEMORY.md shutdown rule |

### D. Process / communication (D1-D5)

| ID | Status | Evidence |
|---|---|---|
| D1 | OWNED | Downgraded by redteam. Rule recorded 15/10, refined 24/10, then violated again 20/11 as I39 (Muse raised a side-chat upload task in main chat at 16:06 20/11 and admitted it). brief_check.py only checks briefs, not chat sends, so no mechanism covers the actual failure mode. Gap? YES |
| D2 | FIXED (rule) | Messenger via connector (MEMORY.md records it CONNECTED); brief_check.py covers it (redteam) |
| D3 | FIXED (rule) | Push-to-GitHub-as-you-go (15/11); brief_check.py covers it (redteam) |
| D4 | FIXED (rule) | Record lessons in both places (20/11); commit 52f3458 evidences the repo-side application. Caveat (Council 2): the laptop-side detailed copy is NOT evidenced by 52f3458, which touches only the repo file. |
| D5 | FIXED (rule+tool) | Whole-day read before any calendar change + audit script ~/workspace/calendar-audit/audit-overlaps.py; sequential writes only (AGENTS.md 25/10) |

### E. General directions (E1-E3)

| ID | Status | Evidence |
|---|---|---|
| E1 | OWNED | Experiment in progress (Worker X-E1, commit cad1543): deliberation done and measured (3 deliberators, 8m40s max parallel, 0 UNVERIFIED, merged plan 58 steps); executor runs A/B on hold (17:59 no-drive rule while user is at keyboard). Confirmed by Council 3. Gap? No conclusion yet: YES |
| E2 | FIXED | Firefox automation research done; zen-mcp 1.2.3 primary, firefox-mcp verified, Selenium 11/11; report ~/workspace/firefox-automation-research-20261121.md (29KB). Note (Council 3): the specific "2-20ms/op" latency figure was not independently re-checked against the file. |
| E3 | OWNED | Speed loop PAUSED under council+redteam gate (G18); new goal goal_efb287ef9e7f (17:44 21/11) re-asserts the direction. Gap? No active speed work until the gate resolves: YES |

### F. Outstanding items (unnumbered, 7 bullets)

| Item | Status | Evidence |
|---|---|---|
| Pill blur increase | FIXED | blur_strength 0.0 to 0.15 in code AND deployed (native/hyprglass-local-optics.lua:14; test asserts 0.15; todolist records DEPLOYED 15:31 21/11, Worker J) |
| Cookie/session research | FIXED | ~/workspace/vm-gmail-sessions-research.md (18.5KB) + repo docs/cookie-session-summary.md |
| Speed loop resume | OWNED | Same as E3 |
| Track 2 | OWNED | Same as G18 |
| Pill candidate choice | OWNED | Overturned by redteam: the owner is documented (docs/pending-user-decisions.md section 3, user as taste judge, candidate 2 temporary default, candidate 1 kept). Assigned to a person and tracked. Gap? Decision still pending: YES |
| User decisions owed (H1-BASE, Step 3, save-dialog B, ~/backups ~99 GiB, Omarchy restore) | OWNED | Overturned by redteam: docs/pending-user-decisions.md items 1-9 track all of them with the user as the only possible decider. Gap? Decisions still pending: YES |
| Deadline 17:00 Fri 20/11 missed | CLOSED | Relabelled per Council 3: "FIXED" overstates it; this is acknowledgement-closure of a terminal fact (a missed deadline cannot be fixed). No open gap remains. |

### G. Computer-use errors, Muse-direct (G1-G24, G27; G25-G26 do not exist)

| ID | Status | Evidence |
|---|---|---|
| G1 | FIXED | Fail-closed stale-code guard: scripts/sync-installed.py:944-945 (loaded_code_sha256 comparison, idle + generation checks; line 948 is the success print, not the comparison, corrected by Council 3) + tests/test_tc02_controller.py:211,227 (matching hash passes, stale hash escalates fail-closed). Caveat: the unit test covers the controller preflight, not the sync-installed.py restart loop itself. |
| G2 | FIXED | Commits 14442ab (geometry) + 871f2e1 (lease fix); floating 901x1176 at [2990,914], 0px deviation. Note (Council 3): the "1055 tests pass" figure was not re-run. |
| G3 | FIXED | Leases moved to ~/.cache/agent-computer-use/leases/ (0700), commit 871f2e1; tests/test_tc02_controller.py:418 references the path |
| G4 | FIXED | hl.dsp object form verified live (closed test VS Code, exit 0); recorded in docs/worker-brief-checklist.md:108-109 and AGENTS.md. Note (Council 3): live verification not re-proven, repo fix text consistent. |
| G5 | FIXED | scripts/image_viewer.py kills imv-wayland (lines 3, 6, 11) |
| G6 | FIXED | Detached launch pattern + ~/workspace/ssh-laptop.sh |
| G7 | FIXED | ~/workspace/ssh-laptop.sh line 2 (-i ~/.ssh/id_ed25519, IdentitiesOnly=yes, tailscale-proxy) |
| G8 | FIXED (superseded text) | Doc says agy cannot run via SSH, use fcc. Worker M (15:42 21/11) proved agy-hypr helper works via SSH, verified live "OK" exit 0 (improvements/worker-m-agy-auth-log.md, tests at 15:39 and 15:40). The doc's fix text is stale; the fix itself (agy usable) is done. See contradiction 1. |
| G9 | FIXED | scripts/vm_proxy.py exists. Note (Council 3): "verified live" rests on recorded probe history, not re-proven. |
| G10 | OWNED | Candidate 2 (cylindrical bottle) temporary default; candidate 1 kept; user is taste judge; interior refraction open (see G11). Gap? YES |
| G11 | OWNED | Blur raised (0.15); interior refraction still open; needs user taste check. Gap? YES |
| G12 | FIXED | E2 calibration (29 vision estimates vs DOM truth: 58.6% predicted hits, pointer error 0.5-0.9px; every miss is vision error) + DOM-first drivers + improvements/muse-coordinate-accuracy-20261120.md |
| G13 | OWNED | New goal goal_efb287ef9e7f (17:44 21/11); think-observe-think loop work ongoing; no 10x result yet. Gap? YES |
| G14 | FIXED | Worker X independent assessment 17:52 21/11 (todolist 2.1.10): 25/25 held-out live tests by 3 fresh independent agents (P clone1 10/10, R agy-q 5/5, U fcc-k 10/10), DOM rects, no baked-in coordinates. Caveat recorded: runs used scripted DOM driver for machine floor; hand-driven sample (P t01 ~7 min PASS) proves agent-driven works. |
| G15 | FIXED | Fully-detached launch rule in every brief + runtime cron watchdog-liveness-check (--check-once every 5 min) |
| G16 | FIXED | Watchdog reports directly to Muse (never via coordinator); 15-min cadence; kill on first STALL flag |
| G17 | FIXED | Same watchdog + MONITOR AND NOTIFY rule |
| G18 | OWNED | Track 2 PAUSED until council + redteam unanimously agree no further optimization is possible. Gap? YES (no council decision recorded yet) |
| G19 | OWNED | Downgraded by redteam. Evidence is only an AGENTS.md lesson dated 2026-11-10 ("Google first"). No brief_check needle, no test, no code. The rule reaches a worker only if a coordinator restates it in that worker's brief, and nothing checks that it was restated. Gap? YES |
| G20 | FIXED (rule, superseded text) | Google chooser rule; but doc says "password step = stop that provider", superseded by the 21/11 revision (try every sign-in way, don't stop on password). See contradiction 2. |
| G21 | FIXED | Browse hover-off-center trick (user-taught); workflow + repo, commit 52f3458 |
| G22 | OWNED | Downgraded by redteam. The rule claims timing is always on, but its implementation is dead code: scripts/timing.py has zero production imports and no run-timing JSONL file exists anywhere in the repo. "Always on" is factually false in production. Needs TimingLogger wired into the live loop. Gap? YES |
| G23 | FIXED | Decision: Luna for everything, no gpt-reserve; M4 routing closed (20/11) |
| G24 | FIXED | JSONL trailing-newline rule (AGENTS.md); Milo fix 54ede41 |
| G27 | FIXED (rule) | Reply immediately in group when @ or asked directly (dang 13/11) |

### H. Evening 20/11-21/11, Muse/Codex computer-use (H1-H3)

| ID | Status | Evidence |
|---|---|---|
| H1 | OWNED | Indicator proven NOT to repaint at idle (0 paints in 122 one-second windows, 32/32 pill frames pixel-identical, 60s idle 0 events); E1 per-event logging ready to catch recurrence. Root cause in LIQUID animated-backdrop mode still unverified: todolist 2.2.3 BLOCKED, decision doc docs/decision-2-2-3-hyprglass-test-20261121.md (4 options A-D) awaiting the user. Gap? YES |
| H2 | OWNED | Named as a target by new goal goal_efb287ef9e7f ("think fast"). Corrected by redteam: the instrument EXISTS (scripts/timing.py, Worker D, commit dc5d0a7: per-step think/act split, JSONL output, SLOW_THINK_S 60s flagging; tests/test_timing.py exercises it), but zero production files import TimingLogger, no run-timing JSONL file exists anywhere in the repo, and live-test-log.md contains zero think_s mentions. Corrected gap statement: the instrument was built and tested but never wired into any live run, so no per-step think-time measurement has ever been produced. Gap? YES (sharpest gap) |
| H3 | OWNED | Root cause found (E2: vision grounding error, pointer exact) and fix direction proven (G14, 25/25 live); deployment of DOM-first driving as Muse's default loop still owed under the new goal. Gap? Partial: direction proven, deployment owed |

### I. Muse-direct errors from chat history (I1-I46)

| ID | Status | Evidence |
|---|---|---|
| I1 | OWNED | Same as H3 (coordinate work; deployment owed) |
| I2 | OWNED | Same as H3 |
| I3 | OWNED | Same as H3 |
| I4 | OWNED | Same as H3 |
| I5 | OWNED | Same as H3 |
| I6 | OWNED | Same as H3 (root-cause admission recorded; fix is the coordinate work) |
| I7 | FIXED (partial) | Hit-rate measurement done at todolist 2.1.8 (E2). The video itself is UNMEASURABLE: Worker X 17:52 searched VM + laptop, no file; video only in E2EE Messenger chat, recoverable only if the user re-sends it |
| I8 | OWNED | Goal goal_efb287ef9e7f names hit-rate as a target. Corrected by redteam: a hit-rate metric DOES exist for calibration fixtures (scripts/hit_rate.py: per-attempt click logging; scripts/calibration_e2.py:27,110 uses it; tests/calibration-e2-hits.jsonl has 87 real click-attempt records; tests/test_hit_rate.py exercises it). But the narrowed gap stands: the realistic test harness records only pass/fail (run_all.mjs and lib/*.mjs contain zero attempt/hit logging), the G14 25/25 held-out live runs record no per-click hit/miss, and live-test-log.md contains zero hit_rate mentions. Corrected gap statement: hit-rate measurement exists for calibration fixtures, but no live agent run measures per-click hit rate. That is the exact hole the user named ("test ko do ti le bam trung"). Gap? YES |
| I9 | OWNED | Same as H1 |
| I10 | OWNED | Same as H1 |
| I11 | OWNED | Same as H1 (2.2.3 blocked on user decision) |
| I12 | FIXED (partial) | Overturned by redteam. Todolist 2.2.4 marks I12 DONE 21/11 06:44 by Worker G: Daemon._ensure_native() respawns a dead native indicator while holders remain + retries the label/show once; unit tests test_daemon_respawns_dead_native + test_daemon_keeps_live_native pass. Verified in code: scripts/overlay.py:212 defines _ensure_native, lines 231-246 use it; tests/test_overlay.py:97 defines the test. Caveat: live respawn proof is still owed (needs a killed indicator during a hold; verify after reboot). Gap flag stays. |
| I13 | OWNED | Same as H2 |
| I14 | OWNED | Same as H2 |
| I15 | OWNED | Same as H2 |
| I16 | OWNED | Same as G13 (speed work) |
| I17 | FIXED (rule) | No-fabrication rule; admission recorded in chat |
| I18 | FIXED (rule) | Follow Hieu's order exactly; workflow file; rule recorded |
| I19 | FIXED (rule) | Own wrong diagnoses plainly; verify before asserting (from 20/11 correction). Flagged by redteam as next-weakest: prose-only, no checker needle, no test. Kept FIXED (rule); the flag is recorded here. |
| I20 | FIXED (rule) | Same as I19 (screenshot-rate explanation refuted by rate mismatch) |
| I21 | FIXED | Browse hover trick (G21, commit 52f3458) |
| I22 | FIXED (rule) | Don't relay a subagent diagnosis as fact without independent verification (external_claim_verification skill) |
| I23 | FIXED (rule) | Follow Hieu exactly, no invented steps (workflow file) |
| I24 | FIXED (rule) | Verify "warning vs blocker" against the tool's own message (numeration blocks packaging). Flagged by redteam as next-weakest: prose-only, no checker needle, no test. Kept FIXED (rule); the flag is recorded here. |
| I25 | FIXED (rule) | Don't claim to see an image you cannot see; open the browser and look (AGENTS.md 20/11). Flagged by redteam as next-weakest: prose-only, no checker needle, no test. Kept FIXED (rule); the flag is recorded here. |
| I26 | FIXED | Firefox automation research done (E2); BiDi is the path, CDP is gone since Firefox 141 |
| I27 | FIXED (rule) | REPORT BLOCKERS EARLY, 3.5-min threshold; commit 6f055e1 |
| I28 | FIXED (rule) | MONITOR AND NOTIFY rule (MEMORY.md) |
| I29 | OWNED | Kill-stuck rule covers killing; no pause-propagation mechanism exists for already-dispatched agents. Gap? YES |
| I30 | FIXED (rule) | Same reporting family as I27/I28 |
| I31 | FIXED (rule) | Hard logging rule 21/11 (IDENTITY.md + SOUL.md): direct computer-use must log to a file with wall-clock + elapsed |
| I32 | FIXED (rule) | Ctrl+L is the browser address bar, never in a file picker (C3 family) |
| I33 | FIXED (rule) | Ctrl+T is a new window in Zen, never use (C3) |
| I34 | FIXED | Workflow file order (checker before solution, per Hieu) |
| I35 | OWNED | Downgraded by redteam. The rule exists in prose (docs/brief-template.md and docs/worker-brief-checklist.md: "never start work before the user says GO. 'Ready' is not GO."), but brief_check.py has no GO needle, so nothing verifies a brief carries it, and the todolist fix text for the I32-I40 family (item 2.6.6) is vague. The I32-I40 family itself is a record of repeated acting-before-GO behavior. Needs a checkable gate. Gap? YES |
| I36 | FIXED (rule) | Overturned by redteam. docs/brief-template.md: "Never report 'ready' without a live check (login state, session state, file presence)." docs/worker-brief-checklist.md:55: "I36: never report 'ready' without a live check..." Caveat: scripts/brief_check.py has no needle enforcing it (grep for "ready" returns nothing), so no machine enforcement and no test. Gap flag stays. |
| I37 | FIXED | Workflow corrected after re-reading Hieu's video |
| I38 | FIXED (rule) | DO IT YOURSELF (11/11): never ask the user to click, run, or type |
| I39 | FIXED (rule) | Channel separation (D1). Note: D1 was downgraded to OWNED by the redteam because I39 itself is the re-violation; I39 the incident is recorded as FIXED (rule) in the sense that the rule + the admission exist, but the mechanism gap lives under D1. |
| I40 | FIXED (rule) | Overturned by redteam. docs/worker-brief-checklist.md section 4: "A self-written artifact buried in a long report does not count as telling. A material fact gets its own short message." Section 5, I40 entry: a material fact "gets its own short message, never one line buried in a long report." Caveat: brief_check.py has no needle for it, so no enforcement and no test. Gap flag stays. |
| I41 | FIXED | Observation expiry handling (C1) + limit 120s (I42) |
| I42 | FIXED | Limit raised 90s to 120s, repo + laptop |
| I43 | FIXED | Commit e3d75c4 "2.8.2 I43: bad driver request lines no longer drop the session" |
| I44 | FIXED | Zen-only + SAVE THE WORKING METHOD rule |
| I45 | FIXED | Cookie/session research file + conclusion (sessions not permanent) |
| I46 | FIXED | Two missing lessons added to the workflow file |

## Counts (final, after council + redteam)

- Error IDs in the doc: 113 (A9 + B14 + C8 + D5 + E3 + G25 + H3 + I46). Plus 7 unnumbered Part F items = 120 items total.
- FIXED: 82 of 113 IDs (84 of 120 items). Of those, the rule-only rows that survive the redteam's bar are the ones with a brief_check.py needle or code behind them (A1, A5, A6, C6, C7, D2, D3, D4, D5, plus I17-I40 rule rows where the redteam did not downgrade).
- OWNED: 31 of 113 IDs (35 of 120 items).
- UNOWNED: 0 of 113 IDs (0 of 120 items). Every item now has at least a named owner or a recorded rule; what remains open is missing proof, missing enforcement, missing measurement, or a pending user decision, all flagged as gaps below.
- CLOSED: 1 item (Part F deadline, acknowledgement-closure).
- Gap-flagged (no fix AND no test, or missing proof/enforcement/measurement/decision): H2 (instrument built, never wired in), I8 (hit-rate exists for calibration only, absent from live runs), H1 (root cause unverified, 2.2.3 blocked), G10/G11 (pill), E1 (no conclusion yet), E3/G18 (gate unresolved), I12 (live respawn proof owed), I29 (no pause-propagation), I36/I40 (no enforcement needle), A9 (thin), C2 (thin), D1 (mechanism gap), G13, G19, G22, I35, F pill choice + user decisions (pending).

## Top 5 gaps (corrected after redteam)

1. **H2 / I13-I15: think-time instrumentation built but never wired in.** scripts/timing.py (Worker D, commit dc5d0a7) implements per-step think/act split with JSONL output and SLOW_THINK_S 60s flagging, and tests/test_timing.py exercises it. But zero production files import TimingLogger, no run-timing JSONL file exists anywhere in the repo, and live-test-log.md contains zero think_s mentions. The new goal's headline target ("think fast") has never been measured on a live run. Wire TimingLogger into the live loop; until then "think fast" cannot be proven or improved.
2. **I8: hit-rate measurement exists for calibration fixtures, absent from every live agent run.** scripts/hit_rate.py logs per-attempt clicks; calibration_e2.py uses it (87 records in tests/calibration-e2-hits.jsonl). But the realistic harness (run_all.mjs, lib/*.mjs) records only pass/fail with zero attempt/hit logging, and the G14 25/25 held-out live runs record no per-click hit/miss. The E2 calibration measures vision-grounding accuracy on a grid, not an agent's live-run click hit rate, which is the exact hole the user named ("test ko do ti le bam trung"). Fix: record hit/miss per click in every live run and report the rate.
3. **H1 / I9-I11: flicker root cause unverified.** The indicator is proven not to repaint at idle, but the LIQUID animated-backdrop cause is unmeasured because hyprglass is not loaded. Blocked on the user's decision (docs/decision-2-2-3-hyprglass-test-20261121.md, options A-D). Until he picks one, the flicker cannot be closed.
4. **Process holes with no mechanism: I12 (live proof owed), I29, I36, I40, D1, G22.** No live proof that a dead indicator respawns mid-hold; no pause-propagation to already-dispatched agents; no enforcement needle for "never report ready without a live check" or "material fact gets its own short message"; channel separation has no mechanism covering chat sends; timing/logging "always on" is dead code in production. Each is small; together they are the next incident waiting to happen.
5. **G10/G11 + Part F: pill interior refraction and the final taste choice still need the user.** Blur is at 0.15 and deployed, but interior refraction is open and the candidate choice (1 vs 2) is undecided. Six user decisions in total are owed (H1-BASE, Step 3, save-dialog B, ~/backups, Omarchy restore, pill choice) plus the 2.2.3 test-method decision. All are now tracked in docs/pending-user-decisions.md with the user as owner.

## Contradictions found in the doc

1. **G8 is stale.** Doc says agy cannot run via SSH, use fcc instead. Worker M (15:42 21/11) proved the agy-hypr helper runs agy via SSH (verified live "OK", exit 0). The doc's fix text is wrong now; the fix itself (agy usable) is done a different way.
2. **G20 is stale.** Doc says a password step means "stop that provider". The 21/11 sign-in revision says the opposite: do NOT stop on a password step, try every sign-in/account-creation way. The newer rule supersedes the doc.
3. **H1 corrected itself inline.** H1 originally said the flicker happened "while Codex ran"; corrected 07:02 21/11 to "while Muse drove directly" (see I9). The correction is present but only as an inline note; a reader skimming H1's first line still gets the wrong cause.
4. **A3's fix was incomplete when written.** A3 records "20 errors added to the prompt" as done, but I46 shows the workflow still lacked 2 lessons (delete vietnamese statement, Browse hover) at 01:21 21/11. I46 completed it later. A3's status was premature.
5. **E3 vs G18: two different resume gates for the same speed loop.** E3 says resume "after the upload, with a new coordinator". G18 says resume only when "council + redteam unanimously agree no further optimization is possible". The new goal (17:44 21/11) re-asserts the work without resolving which gate applies.
6. **Numbering gap: G25 and G26 do not exist.** The doc jumps G24 to G27. No text mentions G25/G26 anywhere in the file.
7. **results.json contradicts the batch-3 "done" claim (test side).** clone1-batch3/results.json (committed in 1767d4c) records 8 passed / 2 failed (t09, t10), while the batch was reported done. A suite whose own results file shows failures is not done. Strengthened by the redteam: clone1's coord record shows the committed results.json is the second post-fix run (re-run 1 passed 10/10, re-run 2 failed 8/10 under load), so the failures are flaky-by-construction, not pre-fix leftovers.

## Sharpest 3 defects overall

1. **t10-music-player exact-zero position race** (check.mjs:62-64): asserts position === 0 right after Next while the 100ms playback timer keeps running. Deterministic-looking, fails under load. Proven by clone1's own results.json.
2. **t09-multi-window postMessage delivery race** (check.mjs:89, 109, plus rename asserts 74/84/113): asserts main-window state immediately after popup close with no wait for message delivery. The "close race fix" (1767d4c) fixed the wrong race. Proven by results.json (first prefs failed, identical second passed) and clone1's coord record (post-fix re-run 2 failed under load).
3. **H2 + I8: the two headline goals have no live measurement.** Think-time instrumentation exists (timing.py) but was never wired into a live run; hit-rate measurement exists (hit_rate.py) but only for calibration fixtures, never for a live agent run. The user named hit rate and think time as the most important things to fix, and neither has ever been measured on a live run. Everything else in this report is secondary until these two instruments are wired in.

## Council + redteam debate record

- **Council Member 1** (t01-t04 + A/B rows): CONFIRMED all four PASS verdicts by hand (arithmetic, state, results.json consistency). CONFIRMED B1-B14 FIXED with invocation numbers corroborated in local logs. OVERTURNED A7 as cited (no "say I don't know" text in SOUL/IDENTITY; downgraded to OWNED) and A8 as cited (FIXED stands only on corrected evidence: prompt items 8 and 14, workflow lines 143-148). Corrections accepted: A1 citation (MEMORY.md:87, not AGENTS.md), fcc log lives on the laptop not the VM. Minor defects found: t01 historyLines always 0 (regex needs newlines textContent never has), t04 unstar asserts count only, not the emptied list.
- **Council Member 2** (t05-t08 + C/D rows): CONFIRMED t06, t07, t08 PASS by hand (chip order, localStorage freshness, slider determinism, search keywords). OVERTURNED t05 PASS to FAIL (fixed rename mapping, fixture.html:155-156, no user-supplied name; a broken rename returning meeting-notes.txt always would pass). OVERTURNED C2 as cited (no fresh-observe rule in todolist Phase 2; downgraded to OWNED). CONFIRMED C1, C3-C8, D1-D3, D5; D4 confirmed with the caveat that the laptop-side lesson copy is not evidenced by commit 52f3458. Minor defect found: t05 tree-old-files button id never asserted after folder rename.
- **Council Member 3** (t09-t10 + E/F/G1-G9 rows): CONFIRMED both FAIL verdicts with exact lines (t09 asserts 89, 94-95, 108-109; t10 lines 62-64). Confirmed P's live 10/10 does not refute the FAILs (a race with per-run failure probability p passes with probability (1-p)^n). Found Y3 under-scoped t09: the race also affects rename asserts (74, 84, 113) and status (76-78). CONFIRMED all checked gap rows. Corrections accepted: t09 line numbers (were off by ~12), G1 citation (sync-installed.py:944-945, not 948), F deadline relabelled CLOSED (acknowledgement, not a fix). Noted as unverified by re-check: E2 latency figures, G2 "1055 tests" figure, G4/G9 live-verification claims (rest on recorded history).
- **Redteam** (attack all FAILs, UNOWNED rows, rule-only FIXED rows, top-5 gaps): t09 FAIL CONFIRMED (settled the timeline with clone1's coord record: the failing run was post-fix code under load; the race is structural). t10 FAIL CONFIRMED (structural, not a load artifact). UNOWNED rows OVERTURNED on all five: I12 FIXED (partial, Daemon._ensure_native + unit tests), I36 FIXED (rule, brief-template + checklist:55), I40 FIXED (rule, checklist sections 4-5), F pill choice OWNED (pending-user-decisions.md section 3), F user decisions OWNED (pending-user-decisions.md items 1-9). UNOWNED now 0 of 120. Rule-only FIXED rows PARTIALLY OVERTURNED: five downgraded to OWNED (A7, D1, G19, G22, I35), each with a named missing mechanism; rows with a brief_check.py needle or code (A1, A5, A6, C6, C7, D2, D3, D4, D5) survive. Top-5 gaps 1 and 2 survive in substance with corrected wording: H2 (instrument built, never wired in), I8 (hit-rate exists for calibration only, absent from live runs). Flagged as next-weakest but not downgraded: I25, I19, I24 (prose-only, no needle).

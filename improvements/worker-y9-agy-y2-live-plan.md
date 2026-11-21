# Worker Y9 run plan: agy-y2 suite LIVE on Zen (independent)

- Worker: Y9 (Muse live runner)
- Date: 2026-11-21
- Task: run tests/realistic/agy-y2/ (10 tests) LIVE on the owner's Zen via Marionette, independently. The owner handed the machine over, is out of the house and busy, and ordered the whole process to run automatically per the Lauren Tan direction.
- Suite state: commit 30a72e5 on todolist-push. Y2 generated it, Y2b verified 8/10 with 2 defects, Y2 fixed both, Y7 independently verified both fixes CORRECT with redteam NO BLOCK (improvements/worker-y7-fix-log.md, commit a07fd27). Headless: simulate.mjs --all 10/10 PASS, check.mjs --all 10/10 FAIL on fresh fixtures. The live run is still owed and is this task.
- Queue: Y4d runs the agy-q2 rerun FIRST, then Y8 runs E1 conditions A and B. Y9 drives Zen ONLY AFTER Y8 reports completion. Prep now, poll todolist-push for Y8's completion, do not drive while Y4d or Y8 is live. One live runner at a time, no exceptions.
- Slot status at plan time (18:3x 21/11): Y4d is in council revision (Council 3 BLOCK on preflight, Council 1 APPROVE WITH FIXES on diagnose layer; no rerun started, no geckodriver running on laptop, 8768 server alive, Zen alive with BiDi). Y8 design not final, waiting Y4d slot. Y9 polls.

## 1. What the run measures

- Each test: the spec's exact steps (test-01..10 .md files), driven through real Marionette clicks and keystrokes on the live Zen, with intermediate spec verifies recorded as checks and the final state verified by a 1:1 port of check.mjs verifyTest (same selectors, same expected values, including test-07 'Root: 5 files').
- Per-step wall time (JSONL), per-test elapsed, suite total wall time, steps per test, hidden-body encounters with diagnosis (htmlClass incl. tz-hidden or not, rAF tick count, same tab same minute).
- Y7's surviving doubts are tracked live, not gated: (1) test-07 skip hole, (2) test-09 rename-branch bypass off-spec, (3) test-07 Root count depends on the moved set excluding img4, (4) simulate --all aborts on the first crash. The run follows the spec exactly, so (1) and (2) cannot trigger; (3) is heeded as a warning; (4) does not apply (each test runs independently).

## 2. Pre-registered thresholds (frozen before any live run)

- Per-test PASS: zero step failures AND zero check failures AND final ported verify 0 failures AND the integrity guard held (verify FAILS on the untouched fixture before steps; if it passes on untouched, abort that test as a suite defect, never a pass).
- FLAGGED pass: a pass where the tz-hidden removal intervention ran AND the post-remove snapshot proves the class is gone. Counted separately, never folded into the headline clean count.
- INFRA-blocked: hidden-body unrecoverable after the recovery ladder, or a session-creation failure. Two CONSECUTIVE infra-blocked tests abort the suite (reset on any pass and on the session-failure path).
- Suite headline: clean passes only. Exit 0 iff clean + flagged == 10. A live failure is a finding, never a reason to re-run silently until it passes. A re-run is allowed ONLY for a test proven infra-blocked, logged as a re-run, never as a first pass.
- Timing expectation (diagnostic, not a gate): headless simulate 240-411 ms/test; prior live Marionette suites about 4 s/test. No per-test timeout gate; a single Marionette call hanging past its 30 s timeout fails that test.

## 3. Harness design (copied from run_agyq2.py, with every known Y4d defect fixed up front)

Base: run_live.py WD / Runner / diagnose_body / _classify_snapshot (working tree at ship time, md5 recorded; Y4d's diagnose layer got Council 1 APPROVE WITH FIXES). The ensure_visible / open_fixture / bootstrap_tab / preflight pattern is copied from run_agyq2.py and adapted to agy-y2 paths, with these fixes already applied (each maps to a Y4d council finding):

- Preflight (Council 3 F1-F9 all applied): explicit LIVE_OWNER_AWAY=1 only, never inferred; BiDi 9222 + Marionette 2828 liveness; fixture server loopback on MY port 8769 probing the agy-y2 fixture; stale-geckodriver sweep where ppid None REFUSES instead of killing (C3-F3), garbage PID files unlinked and logged (C3-F8), stat parsed after the last ')' (C3-F7); lock check accepts POSIX, FLOCK, OFDLCK (C3-F1) and the ancestor set includes os.getpid() (C3-F7); Hyprland IPC liveness as a labeled SAFETY gate with 10 s timeout, never a bare hyprctl call (C3-F9); log that idle time was NOT independently verified (C3-F9).
- WD orphan hardening (C3-F4/F5/F6): my runner does NOT edit run_live.py (Y4d owns it). Mitigation inside my runner: after each test's WD exit, copy /tmp/geckodriver-{port}.log to a per-test file before the next WD() starts, so the "wb" truncation in run_live.WD cannot destroy a failing session's evidence. If Y4d lands F4-F6 in run_live.py before I ship, I record that and drop the workaround note.
- Flagged-pass rule (Council 2 F1/F2/F3): the flag is set ONLY after the post-remove snapshot proves htmlClassList no longer contains tz-hidden; the removal eval also clears the --zen-logo-path inline property (C2-O1); bootstrap intervention is propagated to the suite JSON as a top-level bootstrap_intervention field, including on the bootstrap-failure path; suite `passed` counts clean only, exit 0 iff clean + flagged == total; every per-test summary carries the "flagged" key, including the session-failure path.
- Abort rule (C2-F4, C3-F2): infra_blocked resets to 0 on any pass and on the session-creation-failure continue path; INFRA matched with startswith("INFRA:").
- Ladder budget (C2-F5): ensure_visible enforces an 8 s deadline from its start and logs elapsed time against the budget on every call; when the deadline is near, it goes straight to a new tab or INFRA.
- No handle scanning (C2-F6): the runner keeps a registry of known test-tab handles (created by itself) and NEVER switches to an unregistered handle to read its URL. Bootstrap creates ONE fresh tab via window/new, verifies it with the ladder, and all 10 tests share it (goto + clear storage + reload per test). Pre-existing fixture tabs from earlier probes are NOT reused; a fresh tab is created instead. This removes the 13 s per-scan focus steal entirely.
- Guarded diagnose (C2-F7): every diagnose_body call on a tab whose state is uncertain sits in try/except that skips the tab instead of aborting the scan.
- Swapped-tab tracking (C2-F8): when ensure_visible swaps, the old handle is recorded in the cleanup set and returned to about:blank at suite end (or closed explicitly, since it is ours).
- INFRA classification (C2-F9): rebootstrap failures and removal-eval raises raise INFRA-prefixed errors, never bare RuntimeErrors.
- Server: my own HTTP server on port 8769 (not Y4's 8768), root = repo tests/realistic, probing the agy-y2 fixture first. Launched under flock on zen_dom.lock, same as Y4/Y8 (the lock serializes the live-driving slot).

## 4. Test-by-test driving notes (spec vs simulator deltas)

- All 10 tests follow simulate.mjs step for step (selectors and order), plus the spec's intermediate verifies as r.check() calls (recorded, non-fatal) and action steps as r.step() calls (fatal on exception). End state verified by the ported check.mjs logic.
- test-01: type 'uptime' into #pane-terminal-input; duplicate dynamic ids exist (one per pane), Marionette find returns the first match (the active pane), same as puppeteer. Verify uptime text per spec step 15.
- test-02: no explicit mistake step in the spec; the Bluetooth off/on persistence check plays that role. Follow as written.
- test-03: select PNG via JS value + change event (run_agyq2 select_option pattern), never Marionette keystrokes into a <select>.
- test-04: attachment picker is a modal with option buttons; drive by clicks as simulated.
- test-05: select Bar via JS value + change event. Formula bar: type_text clears first, which is correct (bar starts empty each use). B4 correction: click cell, clear, type 1800 (same as simulator $eval clear).
- test-06: straightforward clicks and types as simulated.
- test-07 (WARNING, Y7 doubt 3): the move set is EXACTLY img1-3 (spec steps 15-17). A Root 6 toast on the live run means the move set was wrong, not the fix. Root 5 is correct. Also note Y7 doubt 1 (skip hole): skipping steps 23-29 still passes all 8 checks because the fixture has no restore marker. My run follows the spec exactly, so the hole cannot trigger; it is recorded as a suite follow-up, not a run gate.
- test-08: step 18 clicks a <tr> in the simulator; per the P rule (click <td> never <tr>) the live run clicks the first <td> inside #row-req-api-checkout.
- test-09 (WARNING, Y7 doubt 2): follow the spec exactly, including step 29 click #note-item-archived-draft (direction B, verified correct by Y7) and step 33 body check (it mitigates the rename-branch bypass). NEVER use the save handler's rename branch. Step 10 APPENDS ", Apples" to the body: read the current value first, then type the full text (old + append) via type_text; do NOT use type_text to append (it clears). Step 14 clears then types the full new body.
- test-10: spec step 15 clicks #input-edit-watch-total, which the simulator SKIPS because the fixture has that input display:none (Y2b minor finding). A pointer click cannot work on a hidden input. The live run drives it via click_js (el.click()) and records the step as a known spec/fixture gap in the report. The checker does not test it.
- Contenteditable: none of the fixtures use it (all inputs/textareas per simulate.mjs). If any type fails with contenteditable symptoms, fall back to focus + execCommand insertText per the runner rule.
- No fixture verify hooks are used as oracles (grep: zero __verify / __agyVerify / __fcckVerify in the suite; the ported verify reads raw DOM only).

## 5. Slot polling and launch

- Poll todolist-push every few minutes (git fetch + log): Y8's completion marker is a commit on todolist-push recording Y8's E1 execution completion (its final report in improvements/worker-y8-e1-execution-log.md or a completion commit message). Y8's completion implies Y4d done (Y8 waits for Y4d). Do NOT drive before that marker.
- Launch (on the laptop, from the shipped server dir, under flock, detached, one SSH call):
  LIVE_SERVER_ROOT=/tmp/worker-y9-server LIVE_SERVER_PORT=8769 LIVE_LOG=/tmp/worker-y9-live.jsonl WD_PORT=4449 LIVE_OWNER_AWAY=1 flock -w 1800 ~/.cache/agent-computer-use/zen_dom.lock -c "python3 run_agy_y2.py all"
- Ship: copy tests/realistic/run_live.py, run_agy_y2.py, and the agy-y2 suite to /tmp/worker-y9-server on the laptop (via ssh-laptop.sh cat), record md5s of every shipped file, syntax-check both sides. The laptop copy is frozen at ship time; later VM edits do not affect it.
- Log: improvements/worker-y9-agy-y2-live-log.md on todolist-push, plus per-test JSON summaries on stdout and per-step JSONL at /tmp/worker-y9-live.jsonl (copied back to the repo as tests/realistic/live-run-y9-agy-y2-20261121.jsonl).

## 6. Evidence contract

- Every claim in the final report attaches runnable evidence: exact run command + stdout log, commit hash, timed run log (JSONL), per-test summaries. A bare "done" is returned unread. The generator (Y2) never ran these tests live; Y9 is the independent runner.
- Files: improvements/worker-y9-agy-y2-live-plan.md (this file), tests/realistic/run_agy_y2.py (runner), improvements/worker-y9-agy-y2-live-log.md (run log), tests/realistic/RUN-REPORT-AGYY2-20261121.md (final report).

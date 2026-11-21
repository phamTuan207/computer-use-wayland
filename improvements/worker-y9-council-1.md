# Council Member 1 verdict: Worker Y9 agy-y2 live-run plan (harness correctness only)

- Reviewer: Council Member 1 (scope: harness correctness only)
- Date: 2026-11-21
- Reviewed: `improvements/worker-y9-agy-y2-live-plan.md` (commit 6f20fb5, branch `todolist-push`), checked against `improvements/worker-y4d-council-2-ladder.md`, `improvements/worker-y4d-council-3-preflight.md`, `improvements/worker-y4d-council-1-diagnose.md`, and the working tree of `tests/realistic/run_live.py` and `tests/realistic/run_agyq2.py`
- Method: read-only. File reads plus `grep -n` line verification plus one read-only SSH probe of the laptop (`ss -ltn`, `/tmp/geckodriver-*` listing, `/tmp/worker-y9-server` check). No live Zen driving, no tab navigation, no Marionette sessions.
- Verdict: **BLOCK**

## Why BLOCK, in one paragraph

The plan's central claim is false against the only code that exists. Section 3 says the runner copies run_agyq2.py "with every known Y4d defect fixed up front" and that "Preflight (Council 3 F1-F9 all applied)". The runner `tests/realistic/run_agy_y2.py` does not exist (no such file; HEAD commit 6f20fb5 adds only the plan markdown), and the source files it copies from still contain every Council 2 and Council 3 defect, verified line by line below. The sharpest instance is C3-F1: the copied preflight still accepts only POSIX locks (`tests/realistic/run_agyq2.py:1189`), so under the plan's own documented `flock` launch the preflight raises "no flock holder" on every attempt and the run can never start. A plan that asserts fixes as done when they exist nowhere must not ship. The design direction in prose is mostly right, which is why this is a BLOCK with a concrete fix list rather than a rejection of the approach. No live run until the runner exists and its diff is re-reviewed.

## What is correct (keep these)

- Port and lock choice: 8769 (HTTP) and 4449 (WD) appear nowhere else in the repo (`grep -rn "8769\|4449"` over `tests/realistic/` and `improvements/worker-y8*` returns nothing). Y8 uses 4451/8767 (`improvements/worker-y8-start-infra.sh:25`, `improvements/worker-y8-e1-comparison-design.md:137`). Live probe: `127.0.0.1:8768` LISTEN (Y4's server, untouched), nothing on 8769 or 4449, no `/tmp/geckodriver-*.pid` or `*.log` on the laptop, no `/tmp/worker-y9-server` dir yet. The choice is non-colliding at probe time.
- The `flock -w 1800 ~/.cache/agent-computer-use/zen_dom.lock` launch matches Y4's documented launch, and the lock (not the slot polling) is the real single-runner guard. Correct in design.
- The no-scan bootstrap direction is sound in principle: a registry of known handles plus one fresh `window/new` tab removes the focus-steal paths Council 2 F6 names, provided rebootstrap is rewritten too (see F8 below).
- The prose statements of the flagged-pass rule, the abort rule, the 8 s budget, and the log-copy mitigation match what Councils 2 and 3 required. The problem is that they are prose only. None of them is in any file.

## Q1. Does the plan's preflight really fix all of Council-3 F1-F9?

No. None of F1-F9 exists in any file. The plan's preflight bullet is a list of intentions, not applied fixes.

- F1 (BLOCK, still present): `tests/realistic/run_agyq2.py:1189` still reads `parts[1] != "POSIX"`. Under the plan's own `flock` launch the holder appears as FLOCK, so preflight raises "no flock holder on zen_dom.lock" on every correctly launched run. Council 3 proved this live with a real flock hold.
- F2 (still present): `tests/realistic/run_agyq2.py:1237` inits `infra_blocked = 0`, and it is touched only inside the `except` branch (`:1267-1272`). No reset on a pass. The session-creation-failure path (`:1240-1259`) appends the summary and `continue`s without resetting it either.
- F3 (still present): `tests/realistic/run_agyq2.py:1150-1167`. When `/proc/<pid>/stat` is unreadable, `ppid` is `None` (`:1150-1154`) and execution falls through to the kill branch (`:1164-1167`). Kill on unknown parentage, the unsafe direction.
- F4 (still present): `tests/realistic/run_live.py:202` `write_text` is unwrapped after `Popen`, and `:224` `self.session = resp["value"]["sessionId"]` sits outside the session POST `try` block. Either exception orphans a geckodriver (F4a leaves no PID file at all).
- F5 (still present): `tests/realistic/run_live.py:196` opens the log before `Popen` (a `Popen` raise leaks the handle), and `:253` `self.proc.terminate()` is not inside a `try`, so a `terminate()` raise skips the log close and PID unlink in `_cleanup`.
- F6 (still present): `tests/realistic/run_live.py:196` opens the geckodriver log `"wb"`, so every new `WD()` truncates the previous session's evidence.
- F7 (still present): `tests/realistic/run_agyq2.py:1152` and `:1201` still parse ppid with `.split()[3]`, and the ancestor set (`:1197-1204`) starts from `os.getpid()` but immediately replaces it with its ppid, so `os.getpid()` itself is never in the set.
- F8 (still present): `tests/realistic/run_agyq2.py:1140-1146`. A garbage PID file hits `continue` silently, no unlink, no log.
- F9 (still present): there is no Hyprland IPC check in `preflight` (`tests/realistic/run_agyq2.py:1097-1213`). The docstring at `:1106-1107` says the Hyprland check is deliberately NOT here, and nothing logs that idle time was not independently verified.
- Related overclaim: the plan's heading "WD orphan hardening (C3-F4/F5/F6)" describes only the F6 mitigation (log copy). F4 and F5 have no mitigation anywhere in the plan. The log copy preserves evidence; it prevents no orphan and unblocks no session slot.
- Related timing gap: the plan says "If Y4d lands F4-F6 in run_live.py before I ship, I record that and drop the workaround note." The ship freezes copies into `/tmp/worker-y9-server`, so a Y4d landing after ship time but before run time is silently missed. The md5 check must happen at run time too, with a re-ship if `run_live.py` changed.

## Q2. Is the no-handle-scanning bootstrap sound, and does it avoid every focus-steal path Council-2 F6 names?

Sound in design, with two gaps in the plan text.

- The three scan sites Council 2 F6 names are `rebootstrap_tab` (`tests/realistic/run_agyq2.py:193`, `for h in d.handles()` with `d.switch(h)`) and the two `bootstrap_tab` scans (`:1055` and `:1069`). The plan's registry plus fresh-tab bootstrap removes the bootstrap scans. But the plan never states that `rebootstrap_tab` is rewritten to create-only. If it is copied verbatim, the scan survives on exactly the path that runs when the shared tab dies mid-suite: `open_fixture`'s "shared tab gone" path (`tests/realistic/run_agyq2.py:283-286`) calls `rebootstrap_tab`, which scans every handle. The plan must state the rewrite explicitly.
- The plan never mentions the `opened_tabs` removal for the bootstrap handle. In `run_live.py`, `new_tab` appends the handle to `opened_tabs`, and `WD._cleanup` closes every handle in it. Y4's `bootstrap_tab` removes the final handle (`tests/realistic/run_agyq2.py:1090-1091`) before its WD session exits. If Y9's bootstrap creates the tab inside its own WD session and forgets this removal, the first test's `WD.__exit__` closes the shared tab and every test re-bootstraps.
- Otherwise the design holds: `d.handles()` itself does not focus; `WD.switch` to a known test tab, the main cleanup loop over `bootstrap_tabs`, and `WD._cleanup` over `opened_tabs` all touch only our own tabs. Creating the fresh tab does focus it, but it is ours and the owner is away, which is the accepted cost, not a user-tab steal.
- Minor wording gap: the plan says bootstrap creates "ONE fresh tab", but if the ladder swaps during bootstrap verification, the surviving handle is the shared tab, not necessarily the created one. Say so.

## Q3. Is the 8 s ladder budget enforceable as designed, and is the geckodriver-log-copy mitigation for C3-F6 sound?

Budget: no, not as written. Log copy: sound in outline, with three gaps.

- The copied `ensure_visible` (`tests/realistic/run_agyq2.py:222-275`) has only a 2.0 s poll deadline (`:244`) and no overall deadline. The 8 s deadline exists only in the plan prose.
- The plan's rule "when the deadline is near, it goes straight to a new tab or INFRA" is self-defeating. A new-tab attempt costs about 1.7 to 2.0 s (Council 2 Q4 cost model, still valid once the scan is gone). Going to a new tab when little time remains still blows the budget. The enforceable rule is INFRA when the remaining budget is below the next phase's known cost. Cost check with the scan gone: initial diagnose 0.5 to 0.7 s, poll up to about 2.75 s with overshoot, remove about 1.1 s, one new-tab attempt 1.7 to 2.0 s, final diagnose 0.3 s, total about 6.5 to 6.9 s. That fits 8 s only if new-tab attempts are capped by remaining budget. The old rebootstrap tries up to 3 new tabs (about 5 to 6 s), which would total about 10.9 s, over budget.
- The plan also does not say the deadline is checked before each phase, nor that elapsed time is logged on every return path (including the VISIBLE early return at `:242-243`).
- The 8 s budget is per `ensure_visible` call, but `open_fixture` calls it twice per test plus goto/refresh pairs, so the per-test worst case is about 20 s. State that bound so a slow test is not misread as a hang.
- Log copy, gap 1: it covers only the per-test WD-exit path. The session-creation-failure path (`tests/realistic/run_agyq2.py:1240-1259`) has no WD exit (`__exit__` never runs on a failed `__enter__`), so a failed session's geckodriver log is never copied. Copy there too.
- Log copy, gap 2: the destination path pattern is unnamed and copy success/failure is not logged. Name the pattern (for example `/tmp/worker-y9-gecko-{test}.log`) and log the outcome; tolerate a missing log file (F5a leaves none).
- Log copy, gap 3: placement is not pinned. The copy must run strictly between `wd.__exit__()` and the next `WD()` construction, including before the suite-end cleanup WD() (which also opens `"wb"` and truncates the last test's log). The diff must show the placement.

## Q4. Is the server/port/lock setup (8769, flock on zen_dom.lock) correct and non-colliding with Y4's 8768 server?

Correct as a choice, broken as an implementation until F1 is fixed.

- Ports 8769/4449 collide with nothing in the repo or on the laptop at probe time (see "What is correct" above).
- The lock file and `flock -w 1800` launch are the right mechanism, but the copied preflight cannot pass under them (C3-F1, `tests/realistic/run_agyq2.py:1189`). The plan's own launch method is incompatible with the preflight it copies.
- The copied preflight probes `base + "/agy-q2/fixtures/test-01-whiteboard.html"` (`tests/realistic/run_agyq2.py:1128-1138`). Y9 must probe an agy-y2 fixture. The fixtures exist (`tests/realistic/agy-y2/fixtures/test-01-tmux-session.html` is first), but the plan says only "probing the agy-y2 fixture" without naming the file. Name it.
- The copied `start_server` falls back to `_rl_start_server`, which probes the clone1 fixture for reuse (`tests/realistic/run_live.py:484`). That probe is for the wrong suite. It is harmless given the identical root (`tests/realistic`), but Y9 must adapt both probes to agy-y2, not copy verbatim.

## Q5. Any other harness defect in the plan?

Yes, four.

- Contradiction in the INFRA definition. Plan section 2 defines INFRA-blocked as "hidden-body unrecoverable after the recovery ladder, or a session-creation failure", but the abort bullet says `infra_blocked` "resets to 0 on any pass and on the session-creation-failure continue path". If session failures are INFRA-blocked, they should increment the streak, not reset it. C3-F2's reset only makes sense if session failures are a separate counter (`wd_failures` in Y4's code). The plan must pick one and state both counters explicitly.
- Missing reset case. The plan lists resets on pass and on session failure, but not on a non-INFRA test failure. Y4's code resets on non-INFRA (`tests/realistic/run_agyq2.py:1272`), and "two consecutive" requires it: INFRA, non-INFRA fail, INFRA must not abort. Spell out all three reset cases.
- Bootstrap-failure path JSON. Y4's main returns 2 with no JSON on bootstrap failure (`tests/realistic/run_agyq2.py:1230-1234`). The plan says the `bootstrap_intervention` field is propagated "including on the bootstrap-failure path". That requires emitting JSON on that path. Design states it; the diff must show it. The same applies to the bootstrap `hidden_body_encounters` count, which the plan does not mention.
- Council-1 diagnose fixes are also not in the shipped base. The plan cites the diagnose layer as "APPROVE WITH FIXES", which is accurate as a verdict citation, but the required fixes are not applied: `diagnose_body` still maps a second-sample eval error to `FIXTURE_FAILURE`, discarding the snap1 evidence (`tests/realistic/run_live.py:154-180`, Council-1 F1), and `WD.goto` still returns a hidden page with only a print while `refresh()` never diagnoses at all (`tests/realistic/run_live.py:325-360`, Council-1 F2). F1 bites Y9's ladder directly: a second-sample eval error skips the `tz-hidden` removal step. F2 is harmless on Y9's path because `open_fixture` runs `ensure_visible` after every goto plus refresh, but that reasoning must be recorded in the runner, not assumed.
- The integrity guard (section 2: verify FAILS on the untouched fixture before steps, else abort that test as a suite defect) has no placement in the plan and no code anywhere. Show its exact placement in the diff.

## Required fixes (all must land in the run_agy_y2.py diff and be re-reviewed before any live run)

- R1. Write `tests/realistic/run_agy_y2.py` (it does not exist) and correct the plan's "already applied" language to "to be implemented" until the code exists. No ship until Council 1 re-verifies the full diff.
- R2. Fix C3-F1 in the copied preflight: accept `parts[1] in ("POSIX", "FLOCK", "OFDLCK")` at `tests/realistic/run_agyq2.py:1189`, and re-prove with a live flock hold before the run. Without this the plan's own launch fails preflight every time.
- R3. Fix C3-F3, F7, F8, F9 in the new preflight: on ppid `None`, re-check liveness and refuse unless actually dead, never kill on unknown parentage; parse ppid after the last `)` and include `os.getpid()` in the ancestor set; unlink and log garbage PID files instead of silently continuing; add the Hyprland IPC SAFETY gate (10 s timeout, never a bare `hyprctl` call, labeled SAFETY, fail closed) and log that idle time was not independently verified.
- R4. Resolve the `run_live.py` F4/F5/F6 position: either wait for Y4d to land F4-F6 and ship the fixed copy (md5 verified at ship time AND at run time, re-shipping if it changed), or vendor a patched WD in the Y9 runner. The log-copy workaround covers F6 evidence only. State the residual F4/F5 orphan risk explicitly if shipping unfixed.
- R5. Implement the log copy exactly: copy `/tmp/geckodriver-4449.log` to a named per-test file immediately after each WD exit AND on the session-creation-failure path, strictly before the next `WD()` starts; log copy success or failure; tolerate a missing log file.
- R6. Implement the flagged-pass rule end to end: set the flag only after the post-remove snapshot proves `tz-hidden` is gone; clear the `--zen-logo-path` inline property too (C2-O1); propagate the bootstrap intervention (flag plus encounter count) to the suite JSON including the bootstrap-failure path (emit JSON there, never a bare return 2); headline counts clean only, exit 0 iff clean plus flagged equals total; every per-test summary carries the `"flagged"` key, including the session-failure path.
- R7. Implement the abort rule completely and resolve the contradiction: reset `infra_blocked` on pass, on session-creation failure, AND on non-INFRA test failure; state explicitly whether session failures use a separate `wd_failures` counter with its own two-consecutive abort, and keep the two counters distinct.
- R8. Rewrite `rebootstrap_tab` to create-only (no `handles()` scan) and use it from `open_fixture`'s gone-tab path; keep a registry of known handles and never switch to an unregistered handle on any path.
- R9. Name the bootstrap `opened_tabs` removal explicitly: the fresh tab's handle must be removed from `opened_tabs` before the bootstrap WD session exits, or the first test's `WD.__exit__` closes the shared tab.
- R10. Enforce the 8 s ladder budget with phase gates: check the deadline before each poll diagnose, before the removal eval, and before each new-tab attempt; go INFRA (not a new tab) when remaining budget is below the next phase's known cost; cap new-tab attempts by remaining budget; log elapsed time against the budget on every return path including the VISIBLE early return; correct the poll-cadence docstring (about 3 samples in 2 s, not every 250 ms).
- R11. Guard `diagnose_body` in all retry loops (C2-F7), classify rebootstrap and removal-eval failures as INFRA-prefixed errors including the `open_fixture` pre-check path (C2-F9), and track swapped-away old tabs in the cleanup set (C2-F8).
- R12. Name the exact preflight probe file (for example `/agy-y2/fixtures/test-01-tmux-session.html`), adapt both `start_server` probes to agy-y2, and verify the shipped `run_live.py` md5 matches the repo at run time.
- R13. Show the integrity-guard placement in the diff (pre-step verify on the untouched fixture, abort that test as a suite defect if it passes) and confirm the ported verify reads raw DOM only.
- R14. Apply Council-1 diagnose F1 in the shipped base (second-sample eval error keeps the snap1 classification, never `FIXTURE_FAILURE`). Record in the runner why Council-1 F2 is harmless on Y9's path (`open_fixture` runs `ensure_visible` after every goto plus refresh) instead of relying on the unchecked `last_diagnosis` print.

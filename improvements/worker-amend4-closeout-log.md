# AMEND4 CLOSE-OUT VERIFICATION LOG (Worker CLOSEOUT-VERIFY)

Owner: the owner. Parent: COORD-CLICK-3. Branch: todolist-push.
Work window: 2026-11-22 06:59-07:30 Asia/Ho_Chi_Minh. All times below are Asia/Ho_Chi_Minh unless noted.
Rules honored: evidence with every claim (command + output + commit hash + time log);
explicit pathspec commits only, never plain `git commit`, never `git add -A`;
verify every push with `git ls-remote`; no em dash or en dash anywhere;
no personal info in repo files; never ydotool; no self-healing (fixing belongs to
the AMEND4 worker or a re-commission, never to this verifier).

Verified test HEAD: af0d0a2 (full hash af0d0a2c56f9379636f1b2d118a91f2c4c36e1cb),
via an isolated worktree /tmp/closeout-verify-af0d0a2 (gitignored native/wtype
binary copied in from the main checkout; without it the worktree RT run errors
on 32 inherited tests with "private wtype helper is missing").
Log-commit HEAD: 17fdb9b at log write (child of af0d0a2; see section 4).

## 1. Item-12 regression tests: 4/4 PASS (3 independent runs)

Command (from repo root / worktree root):

    python3 -m unittest tests.test_first_action.TestRun.test_session_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_fallback_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_after_without_result_after_captures_fresh_window tests.test_first_action.TestRun.test_screen_observation_key_batch_refused_before_overlay -v

Results:
- Run A, 2026-11-22 07:00:30 +07, main checkout at 8008662: Ran 4 tests, OK.
- Run B, 2026-11-22 07:13:47 +07, worktree at af0d0a2: Ran 4 tests, OK.
- Run C, 2026-11-22 07:13:56 +07, worktree at af0d0a2: Ran 4 tests in 0.047s, OK.
- Item-12 commit under test: cbab398 (both-fields shape plus 4 regression tests).
- No test weakened. All 4 pass: session path scope-matching after; fallback path
  scope-matching after; fresh window capture when no result after; screen-scope
  key batch refused before overlay.
- Note: the same 4 tests ERROR in the EPERM-storm runs (section 7). That is
  environment, not code: they pass whenever the VM file writes work.

## 2. RT proof set (tests/test_click3_redteam2.py): Ran 49, failures=4, errors=1

Command:

    python3 -m unittest tests.test_click3_redteam2 -v

Results (identical in all 3 runs):
- Run A, 2026-11-22 07:00:33-07:00:37 +07, main checkout at 8008662:
  Ran 49 tests in 3.058s, FAILED (failures=4, errors=1).
- Run B, 2026-11-22 07:13:47 +07, worktree at af0d0a2: Ran 49, failures=4, errors=1.
- Run C, 2026-11-22 07:13:56 +07, worktree at af0d0a2: Ran 49 tests in 9.182s,
  FAILED (failures=4, errors=1).
- The file has 17 own tests: 15 proof tests + 2 controls. Controls pass:
  test_band_text_inside_target_field_still_verifies,
  test_band_text_below_band_must_not_verify. 32 inherited DesktopPreflight
  harness tests pass. 10 of 15 proof tests pass.
- The 5 that do not pass are exactly the 5 the AMEND4 worker judged DEFECTIVE
  and left for adjudication (proofs in the AMEND4 log, items 3-7):
  - ERROR test_region_fallback_readmits_raw_mozinner (F2, item 5): correct
    behavior is a refusal DomActError; the test has no assertRaises.
  - FAIL test_stale_window_origin_accepted_silently (F3, item 6): contradictory
    assertions, 1271.4044399796628 image px apart; no return value satisfies both.
  - FAIL test_band_stacked_fields_low_click_with_x_range_must_not_verify
    (F4, item 3): symmetry proof; no y_range passed, so no band can
    distinguish the two pixels.
  - FAIL test_band_wrong_field_unwired_path_reports_ok (F5 behavior, item 4):
    direct desktop_act call; threading cannot affect it; the "or" branch would
    break the control test test_click_type_text_in_input_line_verifies.
  - FAIL test_typed_flag_forgeable_by_page_script (F6, item 7): the forge line
    assumes the removed window property (TypeError: Cannot set properties of
    undefined) and the value assertion conflates the field value with the
    verify outcome; the substantive flag assertion is fixed (AMEND4 worker
    node test: armed true, flag false).
- This matches the AMEND4 worker's committed final verification exactly
  (commit 6f54a4e, section "Final verification", RT proof tests: Ran 49,
  failures=4, errors=1, same 5 listed). No test was weakened by this verifier.

## 3. Full discover

Baseline (AMEND4 log, 05:30): 1855 tests, 0 failures, 4 pre-existing errors,
17 skipped. The 4 pre-existing errors: test_a11y_skeleton import,
test_cursor_file setUpClass (g++ rejects -std=c++26), test_perf_evidence x2
(missing benchmark JSON).

### 3a. AMEND4 worker final run (committed, 6f54a4e, 07:05)

Command (from tests/): `PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"`
Result: Ran 1920 tests in 388.608s, FAILED (failures=5, errors=6, skipped=17).
Breakdown: 4 pre-existing errors + F2 error + 1 tc02 tesseract error;
failures F3, F4, F5-behavior, F6 + 1 tc02 tesseract failure.
tc02 cause: `which tesseract` returns nothing on this VM (reconfirmed by this
verifier at 07:12: "tesseract: NOT FOUND"); the tests raise "tesseract is
unavailable; refusing to assume text presence". Environmental, unrelated to AMEND4.

### 3b. This verifier, mixed-tree run (INVALID as single-commit evidence)

Command (repo root): `python3 -m unittest discover -s tests -p 'test_*.py'`
Run: 2026-11-22 07:01:39-07:11:03 +07, elapsed 564s, exit 1.
Result: Ran 1927 tests in 559.722s, FAILED (failures=7, errors=4, skipped=17).
Failures: F3, F4, F5-behavior, F6 (4 known defectives) + test_sigterm_and_sighup_restore_ime_and_handlers
(test_ime_cleanup, signal SIGTERM) + unittest.case.FunctionTestCase (test_cli_exit_codes) +
test_typed_text_check_fails_when_fragment_is_absent (test_tc02_controller).
Errors: F2 + setUpClass (test_cursor_file.CursorFileTests) +
test_refusal_and_exception_end_session (test_cursor_session.Lifecycle) +
test_typed_text_check_passes_when_fragment_is_visible (test_tc02_controller).
Why INVALID: the shared checkout HEAD moved 6 times mid-run (reflog, UTC):
00:02:24 03ff589 click3-contract, 00:02:31 d38d3a2, 00:04:40 d7c0945 Y1b
baseline (code changes: scripts/code_exec.py, scripts/codemode.py + tests),
00:04:46 d4e133b, 00:05:46 6f54a4e, 00:05:52 3f1b951, 00:09:58 af0d0a2, and
uncommitted modifications to scripts/code_exec.py and scripts/codemode.py
appeared during the run. The extra failures/errors vs 3a plausibly come from
the Y1b hardening landing mid-run, not from AMEND4. Not attributable to one commit.

### 3c. This verifier, fixed worktree run at af0d0a2 (INVALID, EPERM storm)

Command (worktree root): `python3 -m unittest discover -s tests -p 'test_*.py'`
Run: 2026-11-22 07:13:56-07:19:31 +07, elapsed 335s.
Result: Ran 1878 tests in 318.202s, FAILED (failures=24, errors=497, skipped=17).
INVALID: 497 errors are PermissionError EPERM on tempfile writes (section 7),
not code failures. The same tests pass standalone in the same worktree when
writes work (sections 1-2). Test count 1878 vs 1920 in 3a because the worktree
holds only committed files: the 2 untracked test files in the main checkout
(tests/test_s0_bundle.py, 29 tests; tests/test_ssh_mux.py, 12 tests) are absent,
plus load_tests collection differences under the storm.

### 3d. This verifier, targeted 477-test run at af0d0a2 (07:24:07-07:24:25 +07)

Command (worktree root, TMPDIR=/home/hatch/tmp-closeout-verify):

    python3 -m unittest tests.test_first_action tests.test_click3_redteam2 tests.test_dom_act tests.test_zen_dom tests.test_type_verification tests.test_session_continuation tests.test_session_policy tests.test_keyboard_preflight tests.test_code_exec tests.test_codemode tests.test_cdp_snapshot tests.test_tc02_controller tests.test_cursor_session tests.test_ime_cleanup

Result: Ran 477 tests in 17.799s, FAILED (failures=5, errors=169, skipped=2).
The 5 failures: F3, F4, F5-behavior, F6 (4 known defectives) +
test_chained_ops_in_one_program (tests.test_codemode.TestExecute).
The codemode failure is PROVEN environmental, not a regression: the chained
program calls repo_py_compile, which uses tempfile internally and fails with
"FileNotFoundError: [Errno 2] No usable temporary directory found in
['/tmp', '/var/tmp', '/usr/tmp', '/tmp/closeout-verify-af0d0a2']", while the
single repo_script_info op in the same program completes. The 169 errors are
all tempfile EPERM errors in test_first_action, test_cursor_session,
test_tc02_controller, test_session_continuation, test_session_policy and
test_code_exec. Real failures in this run: only the 4 known-defective RT tests.

### 3e. Clean full discover at fixed HEAD af0d0a2: NOT OBTAINED

Four further launch attempts (07:21:00, 07:22:12, 07:22:49, 07:23:33 +07) all
failed in 0-2s with item-12 exit 120 (CPython exits 120 when flushing stdout/
stderr to a redirected file fails) and the EPERM storm on. A clean full
discover at a fixed HEAD is still owed once the storm clears. It is NOT
replaced by 3b or 3c; both are labeled INVALID above for stated reasons.

## 4. All 12 AMEND4 items landed on todolist-push (Muse lane)

Verified with `git merge-base --is-ancestor <commit> HEAD` for HEAD af0d0a2
(07:12) and again for HEAD 17fdb9b (07:29). All 12 are ancestors of both.

| Item | Commit | Subject |
| 1 GEOMETRY | cc964b2 | (geometry factor/units fix) |
| 2 GATE TRAVERSAL | c1ea773 | (shadow root + nested frame traversal) |
| 3 R3a BAND ANCHORING | 62b740e | (y_range anchoring) |
| 4 R3a WIRING | 72120aa | (type_x/y_ranges threading) |
| 5 R1 REGION FALLBACK + 6 R1 STALE ORIGIN | b44a5ea | (window_bounds required, live re-read) |
| 7 R10 FLAG REDESIGN | 49081aa | (closure + locked getter) |
| 8 SET_VALUE SANITIZATION | af0fa87 | (sanitized read-back compare) |
| 9 SUPPLY-CHAIN TESTS | 44c15bb | (range wiring pins) |
| 10 SNAPSHOT EVENT TEST | e912ad4 | (input/change on changed value) |
| 11 DESIGN-DOC FIXES | 8d75135 | (benchmark target, V4 caret removal) |
| 12 CL1-SWEEP ENTER FAILURE | cbab398 | (both-fields envelope after/after_screen) |
| 4 follow-up | 0668327 | (session act_boundary fakes forward desktop_act kwargs) |

HEAD verified: af0d0a2 (af0d0a2c56f9379636f1b2d118a91f2c4c36e1cb) for tests;
17fdb9b (17fdb9baaf1b5e5efd5bb2fed523c8619ac8471b, "Y1b fix 2a/2b: run snippets
in a forked child, parent kills at the wall") at log write. Item commits are
ancestors of both. No AMEND4 item commit is missing from todolist-push.

## 5. Codex lane (amend4-codex): 11/12, item 12 NEVER DELIVERED, resume in progress

- Base: f0ddd41. HEAD: 274270c0af25708debb8039501c45bf97a56dcca (15 commits).
  Commit list: ddf5673 (item 1), fee4a29 (item 2), 199b10a (item 3), 9975660,
  96ea721, d8136dc (items 4/5/6 in substance), b9fb33a (item 7), 0eb3429
  (item 8), b2b59a9 (item 9 tests), d6ed904 (item 10 test), 8c065f6 (item 11
  docs), c0c049e (relay fixture ranges), 81963fa (window bounds for DOM
  grounding), 029f9c7 + 274270c (docs: fix-pass record + final verification).
- Push VERIFIED independently: `git ls-remote origin refs/heads/amend4-codex`
  at 2026-11-22 07:15:13 +07 returned 274270c0af25708debb8039501c45bf97a56dcca.
  (At 07:04:08 the branch did not exist on origin; Codex pushed at about 07:13.)
- Original Codex session ENDED: no live `codex exec` process on the laptop at
  2026-11-22 07:26:37 +07 (PIDs 774256/774258, started 05:58, gone). Driver log
  last poll 07:10:37 (elapsed 1:12:23, 13 commits then; QUEUE grep still 0).
- Item 12 NEVER reached Codex. Evidence, all checked 07:04-07:15 +07:
  - `grep -c "ADDENDUM|ITEM 12|envelope|CL1-SWEEP"` on /tmp/codex-amend4.log
    was 311, but ALL hits are the word "envelope" in band-verification
    output; grep for ADDENDUM, ITEM 12, CL1-SWEEP, after_screen,
    scope-matching, PRAGMATIC, FIRST PRINCIPLES, message IDs 01a20058 and
    01a2005e, worker-cl1sweep, both-fields: 0 hits each.
  - Codex's own log (improvements/worker-codex-amend4-log.md in its worktree)
    contains 0 mentions of item 12, CL1-SWEEP, or after_screen.
  - No item-12 commit on amend4-codex; `grep -rn after_screen scripts/ tests/`
    in the worktree: empty.
  - Conclusion (confirmed by COORD-CLICK-3 update 07:26): the follow-up messages
    were accepted by `codex queue` (receipt 01a20058 at about 06:02) but never
    consumed by the live process. The queued item 12 died with the session.
- Resume: CODEX-AMEND4-RESUME launched a detached resume at 07:27:00 +07
  (`codex exec resume 01a20054-e53a-77c3-a0f1-383a3b6f409f` with
  /tmp/codex-amend4-followup.md); its log records SessionStart and
  UserPromptSubmit hooks completed, thread NOT expired, resume accepted.
  Item 12 on the Codex lane is PENDING the resume, not complete.
- Codex test results (from its own log, improvements/worker-codex-amend4-log.md):
  - "The 15 non-contradictory RT proof tests passed": Ran 15 tests, OK.
    The 15 named tests are: F4 stacked-fields, the 2 controls,
    F5-behavior wrong-field, codeexec/CLI ranges, geometry x2, R10 flag x3
    (forgeable, sticky-node, sticky-python), iframe arm, iframe reads x3,
    set_value newline. That is 13 proof tests + 2 controls. F2 and F3 are
    EXCLUDED by Codex as "non-contradictory" (its word).
  - Full discover: Ran 1922 tests in 127.609s, FAILED (failures=2, errors=4,
    skipped=2). Failures: F3 stale-origin + test_click_type_verifies_through_input_line_band
    (test_session_continuation.RelayBandVerification). Errors: F2 + a11y_skeleton
    + test_perf_evidence x2.
  - test_first_action: 64 passed (Muse lane: 68; Codex lacks the 4 item-12 tests).
  - Neither tests/test_click3_redteam2.py nor tests/test_click2_redteam.py was
    edited on the Codex lane (verified by `git diff f0ddd41..HEAD --stat -- tests/`).
- Codex lane REGRESSION vs Muse lane: Codex's stricter item-4 breaks the
  pre-existing relay test test_click_type_verifies_through_input_line_band
  (its log: "expects a band-only result to verify without grounded ranges.
  Item 4 requires that result to be unverified"). The Muse lane deliberately
  did NOT implement that "or" branch because it breaks the control test
  test_click_type_text_in_input_line_verifies, and the Muse lane keeps the
  relay test passing. This is a genuine behavioral divergence, not a test edit.

## 6. Reconciliation state and divergence for round-3 council

- Muse lane: 12/12 landed on todolist-push. Codex lane: 11/12 landed on
  amend4-codex (item 12 pending the resume launched 07:27:00).
- RT proof tests: VM lane 10/15 pass (F2, F3, F4, F5-behavior, F6 fail/error,
  judged defective on the VM lane). Codex lane 13/15 proofs pass in its named
  run (F4, F5-behavior, F6 pass there; F2, F3 excluded as "non-contradictory"
  and fail/error on both lanes in full discover).
- Do NOT assume either side. The divergence is ONLY F4/F5/F6: they pass on
  the Codex lane and fail on the VM lane. F2/F3 fail or error on BOTH lanes.
  Round-3 council must adjudicate: are the F4/F5/F6 VM-lane "defective"
  judgments right, or is the Codex implementation (which satisfies them
  unmodified) the correct fix, including its cost (the broken relay band test
  and the stricter band-only-unverified rule the VM lane rejected)?
- Brief end state ("0 failures, 4 pre-existing errors") is met by NEITHER lane:
  VM final 5 failures + 6 errors (AMEND4 worker, section 3a); Codex 2 failures
  + 4 errors (section 5), plus its 1 broken relay test.
- Codex "15/15" must be quoted with its qualifier: it is 15 NAMED tests
  (13 proofs + 2 controls), not the full 15 proofs. The parent update
  (07:26) records it as "15/15 RT proof tests pass"; this log records the
  exact 15 names so the council can see F2/F3 were excluded.

## 7. EPERM storm (environment blocker, intermittent VM issue)

- Symptom: file creation and file content writes fail with
  PermissionError [Errno 1] Operation not permitted, while directory creation,
  shell redirection, and pipes keep working. Python tempfile fails outright:
  "FileNotFoundError: [Errno 2] No usable temporary directory found in
  ['/tmp', '/var/tmp', '/usr/tmp', '/home/hatch']" (tempfile tries to create
  and write a probe file in every candidate dir; all fail). `cp` silently
  produces 0-byte files. CPython exits 120 when flushing stdout/stderr to a
  redirected file fails. `git` object writes fail: "fatal: unable to write
  loose object file: Operation not permitted", exit 128.
- Timeline observed: clean 07:01-07:11 (full discover ran clean); storm from
  about 07:19 with brief clear flickers (python write probes OK at 07:22:06
  and 07:23:26, launches at 07:22:49 and 07:23:33 failed 2s later); still on
  at 07:28:48. An independent worker (CODEX-AMEND4-RESUME) hit the same git
  EPERM twice at 07:26:08 and 07:26:18 while committing the driver log.
- /tmp tmpfs is 512M at 70% used (354M), dominated by other workers' live
  worktrees (probe-s2-venv 59M, r3rt-head / r3c2-head / closeout-verify 27M
  each). Not cleaned: not this worker's files to delete.
- Impact: (a) clean full discover at fixed HEAD af0d0a2 NOT obtained
  (section 3e); (b) this log's git commit may fail with the same EPERM
  (attempt recorded in section 8; if it fails, the log file stays safe on
  disk at improvements/worker-amend4-closeout-log.md, untracked, for retry).
- Known history: AGENTS.md 2026-11-10 records the same exec-write EPERM, and
  2026-11-12 records it as fixed. It is back, intermittent, as of 07:19
  2026-11-22.

## 8. Verdict

- CONDITIONAL close-out. Muse-lane AMEND4: 12/12 items landed on
  todolist-push, verified by merge-base; item-12 regressions 4/4 PASS;
  RT proof set 10/15 with 5 adjudicated defectives, matching the AMEND4
  worker's committed final verification exactly. No test weakened by this
  verifier. No fix made by this verifier.
- Codex lane: INCOMPLETE (11/12; item 12 pending the resume launched
  07:27:00). The Codex lane is not complete until the resume lands or is
  judged unnecessary.
- Reconciliation: OPEN. Round-3 council must settle F4/F5/F6 (pass on Codex
  lane, fail on VM lane) and the Codex relay-band regression.
- Still owed: a clean full discover at a fixed HEAD once the EPERM storm
  clears (section 3e), and the commit of this log (attempt below).

## 9. Log commit (to be filled at commit time)

- COMMIT BLOCKED by the EPERM storm (section 7), not by this worker.
  Attempts (all with explicit pathspec, only this file):
  - 2026-11-22 07:30:25 +07: `git add improvements/worker-amend4-closeout-log.md`
    FAILED: "fatal: unable to write loose object file: Operation not permitted",
    exit 128. File stays untracked (??).
  - 2026-11-22 07:31:29 +07 (after 60s sleep): same command, same failure,
    exit 128.
  - A `git fetch origin` at 07:30 also failed the same way
    ("fatal: unable to write loose object file", "fatal: unpack-objects failed"),
    so origin state past local HEAD 17fdb9b is unknown at commit time.
  - The log file is safe on disk at improvements/worker-amend4-closeout-log.md,
    18,262 bytes, 0 em dashes, 0 en dashes, untracked. Retry the commit once
    the storm clears: `git add improvements/worker-amend4-closeout-log.md`
    then `git commit -m "docs: AMEND4 close-out verification" --
    improvements/worker-amend4-closeout-log.md`, push, verify with
    `git ls-remote`. No other files were staged or touched by this worker;
    the other uncommitted changes (M scripts/code_exec.py, cu.py,
    first_action.py, sync-installed.py, zen_dom.py) belong to other workers
    and were left alone.

# CLICK3-TESTREPAIR log: repair limb for the AMEND4 round-3 review

Worker: CLICK3-TESTREPAIR (independent repair worker). Coordinator:
COORD-CLICK-3. Owner: Pham Tuan (repo-facing name). Branch:
todolist-push. Worktree: /tmp/testrepair-head, clean, pinned HEAD
5dcf2b3 (DOMZEN-FIX). All times Asia/Ho_Chi_Minh wall clock plus
elapsed from task receipt (07:47). Standing rules: full access, no em
dash (U+2014) or en dash (U+2013) anywhere, never ydotool, no personal
info in repo files, log everything, failing-first per repair, explicit
pathspec commits, never force-push.

Specs read: worker-click3-r3c1-review-log.md, worker-click3-r3c2-review-log.md,
worker-click3-r3c3-review-log.md, worker-click3-r3rt-review-log.md,
worker-click3-amend4-log.md (6f54a4e), worker-amend4-closeout-log.md.
Round-3 verdicts taken as given, not re-litigated: C1/C2 GO 7 / AMEND 5 /
BLOCK 0; C3 AMEND (test-repair limb); RT NO BLOCK, 9 GO / 3 AMEND.

## Base state (pinned HEAD 5dcf2b3, clean worktree)

- 07:48 +01m task received. Main checkout carries uncommitted step-0
  edits by another live worker (scripts/cu.py, first_action.py,
  zen_dom.py, code_exec.py, sync-installed.py); its first_action.py
  has NO _scope_after (replaced by _dispatch_ms). NOT used as base.
- 07:48-07:53 +01-06m `git worktree add /tmp/testrepair-head 5dcf2b3`
  failed 6 times to the EPERM storm ("could not write to
  '.git/worktrees/testrepair-head/locked': Operation not permitted");
  the retry loop was interrupted by a runtime restart at ~07:51. On
  retry at 07:53 the storm had cleared and the worktree was created
  (HEAD 5dcf2b3, status clean). Native helpers copied in
  (native/wtype, native/pointer, gitignored build artifacts).
- Baseline RT2 set, 07:53 +06m, clean worktree:
  `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2` -> Ran 49 tests, FAILED (failures=8, errors=1).
  Failing: F3, F4, F5-behavior, F6, F7-node, F8-arm, F12, F13.
  Error: F2 (DomActError refusal). The 5 defective tests from 8008662
  are all still failing, PLUS 4 extra node failures (F7-node, F8-arm,
  F12, F13) caused by the DOMZEN-FIX return prefix (see item A).
  Each of the 10 node-embedding failures below was confirmed to be the
  bare-`return` SyntaxError shape (`JSON.stringify(return
  (function(){...` / `var __armed = return (function(){...`).

## A. HARNESS REPAIR (return-prefix SyntaxErrors)

- Failing-first (07:53 +06m): 10 node tests fail with the bare-return
  SyntaxError across three files: RT2 file 5 (F6, F7-node, F8-arm,
  F12, F13), tests/test_zen_dom.py 3
  (test_typed_flag_not_forgeable_via_window_property,
  test_focus_check_faithful_shadow_shim,
  test_hit_check_faithful_shadow_shim), tests/test_click2_redteam.py 2
  (test_hit_check_passes_interactive_child_at_center,
  test_focus_check_shadow_host_false_negative). The DOMZEN-FIX message
  said 9; measured here is 10. The 10th is the R6 hit_check test in
  the frozen R7 file, which fails the same way.
- Scope note: tests/test_click2_redteam.py is FROZEN for this worker
  (task: do NOT touch it). Its 2 SyntaxErrors are therefore NOT fixed
  here; they need the identical one-line wrap, pending coordinator
  approval to touch the frozen file. See "Still open" at the end.
- Fix: generalize _wrap_bare_return in tests/test_click3_redteam2.py
  so it also wraps a bare leading `return` with no leading comment
  (the old regex required a /* */ comment before `return`, so the
  DOMZEN-FIX scripts `return (function(){...})()` passed through
  unwrapped), and apply it at every expression-embedding site:
  RT2 F6/F7-node arm + verify, F8-arm arm + field_value, F12/F13
  field_value; test_zen_dom.py faithful-shim focus_check + hit_check
  (function-level import, same pattern as the flag test there, to
  avoid a circular import: the RT2 file imports test_zen_dom at
  module level). The flag test in test_zen_dom.py already wraps via
  _wrap_bare_return and is fixed by the helper change alone.
  Wrapping is assertion-neutral: `(function(){return
  (function(){...})()})()` evaluates the same IIFE and returns the
  same value; no assertion text changes anywhere.

- A verified 07:54 +07m: the 7 non-defective harness tests pass
  (F7-node, F8-arm, F12, F13, flag-non-forgeable, both shims); RT2
  back to Ran 49, failures=4, errors=1 (the 5 defectives only); F6
  now fails with the known TypeError (forge line), not a SyntaxError.
- A committed 79d1e9f, rebased onto fd63a7d, pushed as c2c0bbf
  (ls-remote verified). NOTE: origin had moved to fd63a7d (S0-IMPL
  18f2304 + Y1b RPC landed) while I worked; see item C12 for what
  that landing did to _scope_after.
- A2 (coordinator follow-up, 07:55 +08m): the 9 named sites include
  the 2 in tests/test_click2_redteam.py, and the follow-up assigns
  them to this harness repair ("use it at the 9 embedding sites").
  That lifts the freeze for this assertion-neutral wrap only: a
  local _wrap_bare_return helper was added to that file (same regex,
  duplicated so the frozen file keeps its own harness and imports
  nothing from the RT2 file) and wrapped at the 2 sites. No
  assertion changed. Verified: all 9 named sites pass in one run
  (10 tests: 9 sites + F11 harvest, OK). A2 committed 27edd1c,
  rebased onto b4b9224, pushed as f26d406 (ls-remote verified).
- The DOMZEN-FIX "9" counts the 9 previously-passing sites; the
  10th node failure (F6) was already red as a defective test, so
  the measured total at 5dcf2b3 was 10 node failures, 9 of them
  newly broken by the return prefix.
- Closeout log: NOT read (the file was deleted from the main
  checkout working tree before I could read it; staged D, untracked
  originally). Its substance is covered by the four review logs'
  CLOSEOUT-VERIFY addenda, which quote it. The four review logs and
  the AMEND4 log were read in full.

## B. FIVE DEFECTIVE-TEST REPAIRS (tests/test_click3_redteam2.py)

- Failing-first: post-A baseline, RT2 Ran 49, failures=4, errors=1
  (F2 error; F3, F4, F5-behavior, F6 fail), same 5 as at 8008662.
- F2: ground call replaced with assertRaises(dom_act.DomActError);
  the old point assertions are gone because no ground return can
  satisfy them (true origin underivable from the meta). Refusal IS
  the correct behavior.
- F3: split into two tests (suite now Ran 50). (a) The original
  name keeps the stale-value documentation: viewport_origin returns
  [340, 108], the mapped point is asserted >1000 px from the true
  point (measured 1271.4), and the contradictory assertLess(dist,
  10) is dropped. (b) New
  test_stale_window_origin_refused_at_ground_time mirrors the
  AMEND4 stale test (FakeDomSession live_origin [2600, 914] vs
  G30_META [2533, 914]) and asserts the DomActError refusal with
  'moved' in the message.
- F4: y_range=(100, 120) added to the test call; the y=110 control
  is untouched and still passes.
- F5: rewritten in two halves (see the test comment for the reason).
  First attempt (plain CodeExecBackend.act asserting type_verified)
  FAILED with KeyError 'type_verified': the wired path's DOM
  type_check decides the batch before the band (pass: dom-value,
  band skipped; fail: error set, band skipped), so the band is
  never the decider through the full wired path. Half 1 proves the
  wiring with a desktop_act spy: CodeExecBackend.act threads the
  grounded ranges [[12.0, 20.0]] x [[8.0, 12.0]] to desktop_act.
  Half 2 proves the behavior: a direct desktop_act call with THOSE
  ranges (taken from the spy, not hardcoded) and no type_check
  refuses wrong-field pixels (ok False, type_verified False,
  error_code type_unverified) and still verifies right-field pixels
  (ok True, type_verified True). The Codex "or" branch is NOT
  adopted (it breaks the control and the relay test). The test name
  is kept so the review references still resolve. Grounding numbers
  verified empirically first: point [16.0, 10.0], x_range [12.0,
  20.0], y_range [8.0, 12.0], focus True, verify False.
- F6: forge line guarded in try/catch; the value assertion is now
  assertEqual(out['value'], 'hello') alongside assertFalse(flag).
  No flag-gated verify JS adopted (it breaks the before=None
  pre-filled-field contract).
- B verified: RT2 Ran 50 tests, OK; test_type_verification
  neighbors Ran 65, OK (controls still pass, including
  test_click_type_text_in_input_line_verifies and the relay test,
  checked in the neighbor run below).
- B committed 53e4265, rebased onto ed2d559, pushed as 43b27a1
  (ls-remote verified).

## C. THREE REDTEAM CODE FIXES

### C8. set_value maxLength measures the sanitized length (committed 01:03 UTC)
- Failing-first: the exact RT proof error reproduced before the
  fix (textarea maxLength 5 with 'ab\r\ncd' refused as over-limit,
  input maxLength 4 with 'ab\r\ncd' refused), because the pre-check
  compared the raw text length (6 and 5) instead of the sanitized
  length (5 and 4).
- Fix, scripts/cdp.mjs set_value template: the `sanitized`
  computation moved before the pre-check; the pre-check now compares
  sanitized.length. Char-code form kept to avoid backslash-doubling.
- New named test test_set_value_maxlength_uses_sanitized_length in
  the F1 test class in tests/test_click3_redteam2.py (copied F1
  driver plus a maxLength per case). First case values were
  non-discriminating (raw lengths within limits); corrected to
  'ab\r\ncd' / 'ab\ncd' per the RT proof, plus over-limit controls
  (textarea maxLength 4, input maxLength 3, both still refuse with
  'value exceeds maxlength').
- Verified: CdpSetValueTests Ran 2 OK (F1 + new test),
  `node cdp_snapshot.mjs` passes, test_cdp_snapshot Ran 2 OK.
- Committed and pushed as 7372ddd (ls-remote verified).

### C12. _scope_after restored on top of the S0 tree (committed 01:05 UTC)
- Failing-first: test_first_action on the current tree was Ran 68,
  failures=25, errors=9 (C1 measured Ran 68 OK at 8008662). The
  ONLY commit touching scripts/first_action.py or
  tests/test_first_action.py between 8008662 and fd63a7d is S0-IMPL
  18f2304. Two S0 breakages found, both fixed here:
  (1) S0 deleted `def _scope_after` (replaced the def line with
  `def _dispatch_ms`), leaving the docstring + body orphaned as dead
  code under `_capture_params` (after its return) while the call
  site at line ~875 calls undefined `_scope_after` (NameError).
  (2) S0 reads `cu.CAPTURE_MAX_WIDTH` at two capture sites, but the
  test FakeCu has no such attribute (real scripts/cu.py defines it
  = 960), so every run() died with AttributeError and the envelope
  came back path 'refused'. Verified live: test_session_path
  returned error "'FakeCu' object has no attribute
  'CAPTURE_MAX_WIDTH'".
- Fix 1, scripts/first_action.py: `def _scope_after` restored just
  before `_dispatch_ms`, with the RT item-12 residual: a scope-less
  WINDOW meta (carries a window, no scope field, written by a
  pre-scope build) is treated as window scope. A window-scope
  result_after is accepted; else a fresh window capture is taken
  via cu.observe. The orphaned dead body was removed from under
  `_capture_params`, and the stale docstring claim ("A screen-scope
  input, or one with no scope field, reuses the screen capture")
  corrected: only a scope-less meta with NO window reuses the
  screen capture. S0's new helpers (dispatch_ms, first_pointer_ms,
  phase_ms, capture_params, CAPTURE_MAX_WIDTH, --order-wall) are all
  preserved untouched.
- Fix 2, tests/test_first_action.py FakeCu: added
  CAPTURE_MAX_WIDTH = 960, mirroring scripts/cu.py:66. Stale-fake
  fix, same class as the item-4 follow-up 0668327; no production
  behavior changed to accommodate the fake.
- The two fixes together take the suite from Ran 68 FAILED
  (25 failures, 9 errors) to Ran 68 OK, before any new test is
  added: the S0 breakage in this suite is fully repaired by them,
  no other S0 breakage found here.
- Three named tests added in tests/test_first_action.py:
  test_scope_after_prefers_result_after_for_scopeless_window_meta
  (RT named test), test_scope_after_mismatched_result_after_recaptures_window,
  test_scope_after_screen_input_reuses_screen_without_recapture.
  _write_window_obs gained scope=None (writes a scope-less meta).
  Failing-first for the named test: with _scope_after temporarily
  reverted to the old condition, the scopeless test fails (after is
  the screen capture 'a1b2c3d4e5f6' instead of 'sess-after-1'); the
  two coverage tests pass on old code too, as the RT predicted
  (mismatch-recapture and screen-reuse branches already worked).
- Verified: test_first_action Ran 71 OK (68 + 3 new).
- Committed and pushed as 2ec3d67 (ls-remote verified).
- S0-IMPL rebase note: the original task note ("S0-IMPL must rebase
  its in-progress first_action.py onto your _scope_after fix") is
  STALE in form: S0 already landed as 18f2304, so there is no
  in-progress S0 tree left to rebase. The fix was applied ON TOP of
  the landed S0 tree instead, and S0's helpers are preserved. The
  dirty main checkout still carries uncommitted step-0 edits by
  another live worker; they were not touched.

### C7. Typed-flag arm hardening: per-arm unpredictable property name (committed 01:08 UTC)
- RT proof (taken as given): a page that pre-locks the property
  name with a live-value getter before the arm defeats the flag
  (arm trust branch returns true, flag reads the live value).
- Fix, scripts/zen_dom.py: arm_typed_flag now installs its getter
  under a per-arm unpredictable name
  ('__agentCuTypedValue_' + secrets.token_hex(8), 64 bits),
  recorded on the session in self._typed_flag_props[selector]
  (initialized in ZenSession.__init__). typed_flag reads the stored
  name for the selector and returns False when the selector was
  never armed on this session. The re-arm trust branch
  (`if(desc && desc.get && desc.configurable===false) return true;`
  at zen_dom.py:981) is DELETED: a fresh random name cannot be
  pre-locked, so there is nothing to trust. defineProperty throw
  still returns False (fail closed). The `/* zen_arm_typed_flag */`
  and `/* zen_typed_flag */` markers are kept (FakeWdSession
  dispatches on them), as is the `const sel=` shape. The old
  fixed-name property is gone from both helpers.
- Production-caller check: dom_act.py:483-484 arms and
  zen_dom.py:946 verify_typed calls typed_flag on the SAME session
  object (one DOM session per batch in open_dom_hooks and in the
  first_action fallback), so the token survives the batch. The
  fakes need no change (FakeWdSession in test_zen_dom.py and
  FakeDomSession in test_dom_act.py model the flag by selector, not
  by property name).
- Bug found and fixed during the edit: the arm/flag scripts were
  built with `% json.dumps(selector)` at the end of a `+`
  concatenation chain, which only works while the `%s` placeholder
  sits in the LAST adjacent-literal run (`%` binds tighter than
  `+`). Inserting `+ json.dumps(prop) +` mid-chain split the run,
  so `%` applied to a placeholder-less tail and raised TypeError
  "not all arguments converted during string formatting" (caught
  live: all 3 node flag tests errored KeyError 'script' on capture).
  Both helpers now build their scripts by pure `+` concatenation
  (json.dumps(selector) inlined), no `%` operator anywhere.
- Test pairing, tests/test_click3_redteam2.py: _capture_js gained
  an optional session= parameter; the arm and flag are now captured
  from ONE ZenSession in F6, F7-node, and F8-arm (field_value needs
  no pairing). The same pairing was applied to
  test_typed_flag_not_forgeable_via_window_property in
  tests/test_zen_dom.py. Without pairing, typed_flag on a fresh
  session short-circuits (no stored prop) and _capture_js errors
  KeyError 'script': the pairing is load-bearing, not cosmetic.
- Named test added in tests/test_zen_dom.py:
  test_typed_flag_not_forgeable_via_prelocked_getter. It pre-locks
  '__agentCuTypedValue' with a non-configurable live-value getter
  before the arm, then sets 'hello' with zero trusted events.
  Failing-first: against the pre-fix zen_dom.py (temporarily
  restored via git checkout, then the fix re-applied from a patch)
  the test FAILS (flag forged True); with the fix it passes
  (arm True, flag False).
- Verified: test_click3_redteam2 + test_zen_dom + test_dom_act
  Ran 112, OK.
- Committed and pushed as ee883bc (ls-remote verified).
- Scope note: C2/C3 said the pre-locked attack is outside the R10
  model; the hardening is implemented anyway per the task order
  (owner rule favors the most accurate final result). It does not
  break the R10 model: the arm/flag contract is unchanged, only the
  property name is per-arm. Cost: one closure + listener per re-arm
  (old properties linger); re-arm is once per field per batch.

## D. Y1B TEST AMENDMENT (codemode builtins pin) (committed 01:09 UTC)
- Failing-first: test_execute_namespace_pins_safe_builtins fails
  on the current tree with AssertionError: 0 != 1 (len(captured)
  is 0, not 1). Cause: exec now happens in the forked child
  (commit 17fdb9b Y1b RPC). The parent's mock.patch on
  builtins.exec IS inherited across fork, but the child's append
  goes to the child's copy-on-write copy of the list, so the parent
  never sees it. The pin itself is intact (probe 4a-prime passes
  behaviorally).
- Amendment, tests/test_codemode.py only (mechanism-only, per the
  coordinator decision, same class the council ordered for probes
  4a/4b): the mock now writes one JSON record per exec call to a
  temp file (builtins_is_dict, builtins_is_module, builtins_type,
  sorted keys), flushed and closed inside the mock before the child
  exits; the test reads the records back (a missing file reads as
  zero captures, so the count assertion still reports cleanly).
  Every assertion keeps its original strength: len == 1;
  builtins_is_dict True (was assertIsInstance dict);
  builtins_type == 'dict'; builtins_is_module False (was
  assertNotIsInstance ModuleType); 'eval' not in the recorded key
  list (was assertNotIn 'eval'). Added `import tempfile`.
  No production code touched, no assertion weakened.
- Verified: test_codemode Ran 26, OK.
- Committed and pushed as 29083cd (ls-remote verified).

## FINAL VERIFICATION (01:11 UTC, HEAD 29083cd)
- RT set: python3 -m unittest tests.test_click3_redteam2,
  Ran 51, OK. (49 at HEAD 8008662 + 1 F3 split + 1 maxlength test.
  Target met: 0 failures, 0 errors.)
- Neighbors (PYTHONPATH=../scripts:. from tests/):
  test_first_action Ran 71 OK; test_zen_dom Ran 42 OK;
  test_dom_act Ran 19 OK; test_click2_redteam Ran 71 OK;
  test_type_verification Ran 61 OK; test_cdp_snapshot Ran 2 OK;
  test_codemode Ran 26 OK; session/policy suites
  (test_session_continuation, test_session_policy,
  test_subgoal_policy, test_session_driver,
  test_activate_session_backend, test_cursor_session,
  test_session_remote) Ran 179 OK (skipped=1).
  Combined batch Ran 354 OK (RT2 + first_action + zen_dom +
  dom_act + click2 + type_verification + cdp_snapshot + codemode
  + session_continuation).
- `node cdp_snapshot.mjs` (from tests/): exit 0, all regressions
  pass. (Note: the file lives in tests/, not scripts/; a
  `node scripts/cdp_snapshot.mjs` invocation fails MODULE_NOT_FOUND
  for the wrong path, not for a code reason.)
- No em dash or en dash in any changed file (grep checked).
- All commits landed on todolist-push via local git (the EPERM
  storm stayed clear for this session; no GitHub-API landing was
  needed). Every push verified with git ls-remote.
- Commits: A c2c0bbf, A2 f26d406, B 43b27a1, C8 7372ddd,
  C12 2ec3d67, C7 ee883bc, D 29083cd.
- Open items: none from this repair limb. Notes for the council:
  (1) F5 DOM-gate finding (the pixel band is never the decider
  through the full wired path; the DOM type_check decides either
  way, cu.py:2280 / cu.py:2110-2117 / cu.py:2279). (2) The S0-IMPL
  rebase note is stale in form (see C12); the fix landed on top
  of the landed S0 tree. (3) Item 7 hardening implemented, not
  reported back (see C7 scope note).

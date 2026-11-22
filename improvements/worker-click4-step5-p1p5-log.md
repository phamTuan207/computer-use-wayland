# Worker C4-STEP5-P1P5: P1 router plus P5 asserts plus CB-1 contract plus CB-5 locate confirmations

Owner: the owner. Coordinator: COORD-CLICK-4. Step 5 of the FINAL
direction (improvements/worker-click3-final-direction-log.md, sections
1.2 P1/P5, 1.4 CB-1/CB-5, 2 items (d) and (f), 3 step 5, 6 worker 7).
Repo ~/workspace/computer-use-wayland, branch todolist-push.
Start: 08:52 +07, Sun 2026-11-22. No em dash or en dash anywhere in
this file. No personal info.

## 0. Baseline (verified myself, not trusted from the brief)

- HEAD at start: 36364b1 (ITEM8-MICROGAP log).
- Brief claimed baseline Ran 1974, failures 0, errors 4, skipped 17
  (BROWSER-IMAGE-FAIL log). My own runs disagree: the tree has 1981
  tests and 1 error, not 1974/4.
- Baseline discover, run 1 (started 08:49 +07): `python3 -m unittest
  discover -s tests -p 'test_*.py'`, Ran 1981 tests in 238.013s,
  FAILED (errors=1, skipped=17), 0 failures.
- Baseline discover, run 2 (started 08:54 +07, full output to
  /tmp/step5-baseline-discover.log): Ran 1981 tests in 228.449s,
  FAILED (errors=1, skipped=17), 0 failures. The single error is
  pre-existing and environmental, unrelated to step 5:
  test_cursor_file.CursorFileTests setUpClass, harness compile
  fails because the VM g++ does not recognize -std=c++26
  ("unrecognized command-line option '-std=c++26'; did you mean
  '-std=c++20'?"). Not touched: out of scope for step 5.
- Baseline: Ran 1981, failures 0, errors 1 (g++ c++26), skipped 17.

## 1. CB-5 eval removal: already done in step 0, recorded not redone

- Searched the tree and git log: unrestricted zen_dom eval was
  removed from the default agent interface in step 0, commit
  18f2304 (S0-IMPL, 2026-11-22 00:52:57 +0000). The change: the
  `eval` subcommand in scripts/zen_dom.py requires `--debug` or
  `CU_ZEN_DOM_DEBUG=1`; otherwise a JSON refusal, returned BEFORE
  any session opens. `evaluate()` stays as the transport for
  harvest, locate, and hit_check. Covered by tests in
  tests/test_s0_bundle.py (test_eval_refused_without_debug,
  test_eval_passes_gate_with_debug_flag,
  test_eval_passes_gate_with_debug_env). No change made here.

## 2. Failing-first tests (new file tests/test_step5_p1p5.py)

- T+0m (08:52 +07): wrote the 34-test file first, before any
  implementation. First run: FAILED (errors=1), ModuleNotFoundError:
  No module named 'action_result' (the whole module failed to
  import). That is the failing-first record.
- After implementation, the file went 32/34, then 34/34 after two
  fixes (both mine, both recorded here, not hidden): (a) the test
  fake lacked center_x/center_y on the confirm rect and crashed on
  a missing element; fixed the fake and made locate_confirmed
  return None when the report rect is None; (b) a key-name bug in
  dom_asserts.assert_coverage ('reason' vs 'exception').
- Added 3 confirm_locate tests after the first green run (strict
  refuses covered/ambiguous, fallback composes): 37/37 OK.
- Command: `python3 -m unittest discover -s tests -p
  'test_step5_p1p5.py'`, Ran 37 tests, OK.

## 3. What was built

### 3.1 P1 router: scripts/perception_router.py (new, 1 function)

- `route_perception(target, probes=None, emit=None)` returns the
  decision dict {source, target_kind, fell_through, reason,
  coverage}. Per-target priority table: zen-content ->
  dom-zen then screenshot; chromium-content -> dom-chromium then
  screenshot; native-app -> a11y then screenshot; zen-chrome ->
  screenshot ONLY (the decided P8 boundary, no probe can move it);
  unknown -> screenshot.
- Coverage routing (T1a): a backend is usable only on complete
  coverage (elements > 0, not truncated). An empty harvest or a
  truncated a11y tree falls through to the next backend, never
  proceeds on a partial inventory. A probe that raises is treated
  as unavailable, never an error; the router never raises.
- One JSON log line (event perception_routing) on EVERY decision
  through emit (default stderr), plus ROUTING_LOG in-process.
- No live caller wired yet: the router is the decision function
  the S2 flip worker (step 6) wires into the live path. Wiring it
  now would be scope creep past step 5; the gate for this step is
  the router existing with its log line, not a live flip.

### 3.2 P5 asserts: scripts/dom_asserts.py (new, 1 table + 1 list)

- Assert set for the S2 task class (clone chat sends):
  click/double_click/confirm_click/hover_click -> focus_check,
  mandatory; type/fill/set_value -> type_check, mandatory;
  key Enter after a type/fill/set_value (the send) ->
  sent_bubble, mandatory (the V12 gate); assert action -> itself.
  fill/set_value type_check is enforced inside cdp.mjs set_value
  (native-setter write plus read-back verification), verified
  from source.
- Exception list (DOM assert impossible, pixel stays the only
  signal): scroll (scroll position has no DOM postcondition),
  hover (hover state), move (pointer position only, cursorpos is
  the signal), drag (no single DOM postcondition), wait (timing
  only), key non-send (no generic DOM postcondition).
- `assert_coverage(actions)` reports covered/required/exceptions/
  unknown; `require_asserts(actions, available)` fails closed
  (DomAssertError naming every missing mandatory assert) before
  any input. Unknown action types raise too.
- Enforcement points: dom_act.focus_type (Zen path, refuses a
  send whose V12 gate cannot run, before any keystroke) and
  code_exec._api_dom_act (a send program must end with an assert
  action; the trailing assert satisfies sent_bubble). The
  no_after final-assert rule already covered the no_after form.

### 3.3 CB-1 contract: scripts/action_result.py (new) + migration

- `build_contract(input_sent, target_received, verified,
  verified_basis)` returns the three parts plus ok, computed in
  exactly one place: ok True when verified True (covers
  already-satisfied: nothing sent this call but the bubble is
  present) or when input was sent and no postcondition applies
  (verified None) and the target did not demonstrably miss; ok
  False when verified False, even though input_sent is True.
- `contract_ok(result)` reads a result dict through the
  contract, falling back to bare ok for older builds.
  `migrate_legacy_result(result)` maps a pre-CB-1 bare ok to
  input_sent with verified None, never to a claimed postcondition.
- The exception list is shared: action_result re-exports
  dom_asserts.DOM_ASSERT_EXCEPTIONS, the same object, so the two
  can never drift (pinned by a test).
- Migration in the SAME commit: cu.desktop_act stamps
  input_sent/target_received/verified/verified_basis on every
  result via the _with_result_contract decorator (ok is the old
  ok ANDed with the contract ok, so the contract can only fail a
  batch, never pass one the old code failed; a failed
  after-capture keeps ok False). first_action.py envelope carries
  input_sent/verified/verified_basis from the session and
  fallback results, reads session ok through contract_ok, names
  the completed-capture shape (input sent, verified None), and
  marks preflight refusals (input_sent False, verified None).
  dom_act.focus_type returns the contract plus the 'asserts'
  table on every path, including already-sent.

### 3.4 CB-5 locate confirmations: zen_dom.locate_confirmed

- `ZenSession.locate_confirmed(selector)`: one confirm evaluate
  (rect, visible, enabled, match count across the document, open
  shadow roots, same-origin iframes) plus hit_check plus a second
  rect read. Returns None when nothing matches, else {rect,
  visible, interactive, uncovered, stable, unique, unique_count}.
- Operational definitions: stable means two consecutive rect
  reads agree on every component within STABLE_TOLERANCE_PX
  (0.5 CSS px, absorbs sub-pixel rounding); unique means exactly
  one match (count 1), with the remedy documented as re-grounding
  with a harvest ref; visible is a non-empty rect with display
  not none and visibility not hidden; interactive is not disabled
  and not aria-disabled; uncovered is hit_check.
- `dom_act.confirm_locate(session, selector)` is the caller: the
  strict path (real ZenSession) refuses on any failed
  confirmation; the fallback path (duck-typed sessions, test
  fakes) composes from locate/hit_check, preserves the legacy
  re-ground-once behavior, and records interactive/unique as
  None with basis 'unprobed' instead of refusing. ground_input
  now grounds through confirm_locate and carries the report in
  the evidence as 'confirmation'. ground_many (one-shot harvest)
  is untouched.

### 3.5 Deliberate behavior change (existing tests updated)

- The old focus_type enter-accepted path is gone: a send on a
  session without sent_bubble_contains used to report ok True
  with sent_verified None. Under P5/CB-1 that is an unverified
  ok for an action whose postcondition exists, so focus_type now
  refuses (DomAssertError) before any keystroke. Four existing
  tests pinned the old shape and were updated, not deleted:
  test_dom_act happy path and click-miss now run on V12Session +
  V12Act (dom_calls 10 and 8, type_verified_basis 'dom-value');
  test_click2_redteam R5/R6 Enter callbacks now record the bubble
  in the thread DOM (session.sent_bubbles), which is what the
  gate reads; test_dom_act FakeDomSession gained sent_bubbles +
  sent_bubble_contains, matching a real ZenSession. What each
  test proves is unchanged (happy path, click miss never types,
  R5 ordering, R6 exactly-once); only the fixture matches the
  class's real session shape.

### 3.6 Two fixes found while landing (recorded, not hidden)

- test_code_exec loads code_exec.py by file path (importlib
  spec), so the bare `import dom_asserts` in _api_dom_act raised
  ModuleNotFoundError on 8 DomApiTests. Fixed with the same
  sys.path fallback cu.py already uses for jsonlutil/action_result.
- Running single test modules as `tests.test_zen_dom` (not via
  discover) errors 4 tests with ModuleNotFoundError:
  test_click3_redteam2: those tests import a sibling test module
  that only resolves when tests/ is on sys.path. Pre-existing
  invocation artifact, not caused by this change: under discover
  all 42 pass. Not fixed (out of scope).

## 4. Verification

- New file: tests/test_step5_p1p5.py, Ran 37, OK.
- Affected modules (via discover, the correct invocation):
  test_dom_act 19 OK; test_zen_dom 42 OK; test_click2_redteam 71
  OK; test_code_exec 55 OK; test_first_action 71 OK;
  test_s0_bundle 29 OK; test_click3_redteam2 51 OK;
  test_codemode 26 OK; test_browser_image 9 OK;
  test_a1_preflight 7 OK; test_browser_task_benchmark 20 OK;
  test_bench_manifest 4 OK.
- Full discover after (started 09:10 +07, /tmp/step5-after-discover.log):
  Ran 2022 tests in 214.513s, FAILED (errors=1, skipped=17),
  failures 0. The single error is the same pre-existing g++
  -std=c++26 setUpClass error in test_cursor_file (line 107 of the
  log), unchanged from baseline.
- Delta +41 over baseline 1981 decomposes exactly, verified by a
  per-module loader count against a git archive of 36364b1
  (/tmp/baseline-tree): +37 tests/test_step5_p1p5.py (mine) + 4
  tests/test_bench_manifest.py (NOT mine). HEAD moved under me
  during the task: another worker's step-3 bench-manifest commits
  landed 08:49-09:09 +07 (65a2df6 .. 7d7d5c1, HEAD now 7d7d5c1),
  touching only docs, deploy-manifest.json, scripts/bench_manifest.py
  and tests/test_bench_manifest.py, none of my files. My baseline
  runs (08:49, 08:54) predate the 4-test commit (5f86046, 09:08);
  the after run (09:10) includes it. Loader totals: baseline 1989
  (1989 - 8 cursor_file tests that never run = 1981 Ran), after
  2030 (2030 - 8 = 2022 Ran).
- No em dash or en dash in any changed file (checked by script).
  No personal info in any changed file or commit.

## 5. Commit and push

- Files committed with an explicit pathspec (never plain git commit,
  never git add -A): scripts/perception_router.py,
  scripts/dom_asserts.py, scripts/action_result.py, scripts/zen_dom.py,
  scripts/dom_act.py, scripts/cu.py, scripts/first_action.py,
  scripts/code_exec.py, tests/test_step5_p1p5.py,
  tests/test_dom_act.py, tests/test_click2_redteam.py,
  improvements/worker-click4-step5-p1p5-log.md.
- Commit: 76d0a56 (parent 7d7d5c1), 12 files, +1752/-98.
  Pushed 09:16 +07: `git push origin todolist-push` ->
  7d7d5c1..76d0a56 todolist-push -> todolist-push. Verified with
  `git ls-remote origin todolist-push`:
  76d0a5600154aa8c822a3f00434abbc1a51441e2 refs/heads/todolist-push.
  Elapsed task time: 08:52 to 09:16 +07, about 24 minutes.

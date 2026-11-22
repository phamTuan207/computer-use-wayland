# Worker log: C5-P2-IMPL, COORD-CLICK-5 step 7 (P2 element-ref rewrite)

Worker C5-P2-IMPL for coordinator COORD-CLICK-5. Report to the coordinator
only. Repo `~/workspace/computer-use-wayland`, branch `todolist-push`.
HEAD at task start `da46c4c`; HEAD at log time `4ae8ccc` (coordinator logs
only; no code landed on top of this worker's tree during the run).
Repo work only; no live laptop work, no sends into any real thread.

Owner asleep since 06:52 on 2026-11-22 with a headache; Muse holds full
authority. Wall-clock is Asia/Ho_Chi_Minh; elapsed is from task receipt
2026-11-22 10:53:35 +07.

## Time log

- 2026-11-22 10:53:35 +07, elapsed 0:00: task received (step 7, P2 rewrite).
  Read the final direction (commit `e05fc58`), the stale-ref protocol
  (`1bbf64b`), the step 2 contract (`03ff589`), the P2 spec log, and the
  B5 verify log, in full.
- 2026-11-22 about 10:58 +07, elapsed about 0:05: baseline verified at
  `da46c4c`: `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2` gave Ran 51, OK.
- 2026-11-22 11:00:09 +07, elapsed 0:07: follow-up 1 received (items56
  validator defect). Read `improvements/worker-click5-items56-log.md`
  (commit `2942f68`) in full. Validator fix entered this worker's scope.
- 2026-11-22 11:28:22 +07, elapsed 0:35: follow-up 2 received (C5-MOZ-GROWTH
  result). Read `improvements/worker-click5-moz-growth-log.md` (commit
  `a42ef12`) in full. First validator fix version (accept with warning)
  identified as wrong from the pixel proof; rework planned.
- 2026-11-22 11:29:42 +07, elapsed 0:36: first full discover finished:
  Ran 2109, FAILED (failures=34, errors=10, skipped=17). Baseline at
  `dddbddc` was Ran 2024, 0 failures, 4 pre-existing errors, 17 skipped.
  2109 is 2024 plus the 85 new P2 tests; the 34 failures and 6 new errors
  were this worker's migrations (see the migration section).
- 2026-11-22 11:34:01 +07, elapsed 0:40: second full discover finished
  with the same counts (output saved to `/tmp/discover-p2.txt`, failure
  list extracted from it).
- 2026-11-22 11:35 to 11:47 +07, elapsed 0:42 to 0:54: CLI fix
  (binding-when-present), validator rework to the verified-origin shape,
  and all migrations applied. Per-suite re-runs green (see evidence).
- 2026-11-22 11:47:30 +07, elapsed 0:54: final full discover launched
  (background). It was killed by SIGTERM after about 50s without
  completing; relaunched immediately. The SIGTERM coincides with a VM
  reboot: the monotonic clock read 267s at 11:52 +07, i.e. the VM had
  booted minutes earlier.
- 2026-11-22 11:51:24 +07, elapsed 0:58: final full discover finished:
  Ran 2110, FAILED (failures=2, errors=4, skipped=18). The 4 errors
  are exactly the 4 pre-existing errors. The 2 failures are a
  fresh-boot flake, not this worker's change (see below); both pass on
  re-run at monotonic 284s. The skipped count is 18 vs baseline 17;
  the extra skip is being identified by a verbose re-run (see below).
- 2026-11-22 11:52:55 +07, elapsed 0:59: log updated with the final
  numbers; verbose discover launched to name the 18th skip.
- 2026-11-22 11:55:40 +07, elapsed 1:02: verbose full discover
  finished: Ran 2110, 0 failures, 4 pre-existing errors, 17 skipped.
  This is the authoritative final result (see below). Log updated,
  then commit and push.

## Verdicts

### Item 1: element-ref interface, stale-ref protocol, CB-2, strict path: DONE

- New `scripts/element_ref.py`: RECT_TOLERANCE_PX 0.5, SNAPSHOT_MAX_AGE 120s,
  14 STALE_REASON_CODES, ElementRefError/StaleRefError (message starts
  `stale_ref: <reason>`), make_ref/validate_ref/validate_action/
  validate_plan/validate_action_binding, rects_agree, check_binding
  (binding before scope, age over 120s or under 0 expired),
  check_distinguishing_state, stale_ref_error (exact protocol section 7
  shape), decide_disposition (strict overrides to stop; moved plus
  confirmed plus reground_ok is reground_and_act; moved plus unconfirmed
  refuses identity_unconfirmed; missing refuses; ambiguous stops; scope
  changed plus reground_ok re-grounds, else scope_changed_unresolved;
  navigation replans; unstable/covered/not_visible/not_interactive
  refuse; snapshot expired/unbound plus reground_ok re-grounds, else
  stops; window_moved plus reground_ok re-grounds, else stops; unknown
  stops fail-closed).
- `is_send_action` via dom_asserts.assert_for; `is_strict_action` is send
  OR destructive=True. Strictness is batch-level: a disagreement on ANY
  action in a batch containing a send stops the batch.
- CB-2 enforced as mandatory on the program interface
  (`code_exec.CodeExecSession.api_act`, `api_dom_act` via
  `_validate_dom_actions`, `api_dom_assert` stamps its own internal
  action) and on the DOM interface. The JSON batch interface
  (`cu.py` CLI act branch and `desktop_act`) enforces binding-when-present:
  see the design decision below.
- Protocol section 8: the screen-scope legality refusal is DELETED in
  `cu.py` desktop_act and in `first_action.py` (pre-overlay block).
  G28 loud refusal and halt on scope change stay.
- Protocol section 5 lifecycle: disagreement on step N invalidates later
  refs; `_note_typed` in `zen_backend.py` updates the recorded state
  after a verified fill; GroundPoints gains `strict=` (strict raises
  `stale_ref: rect_moved` instead of silent re-ground).
- Section 7 error shape emitted by the Zen backend (inner error dict as
  top-level `error`, full shape in `results[i]`); first_action envelope
  maps to error_code `stale_ref`, path `refused`, ok false, exit 1;
  code-exec raises CodeExecError starting `stale_ref: <reason>`.
- OPEN-1/2/3 defaults implemented as specified: 0.5 CSS px tolerance,
  two back-to-back stability reads, per-action distinguishing-state
  coverage with the refuse row when unrecorded. Step-9 prototype revises
  from measured data.

### Item 2: A9, one coordinate system: DONE

- `scripts/dom_act.py`: `ground_input` converts the rect once at the
  driver edge via `fastpath.dom_rect_to_screen_point`; the image point
  is derived from the screen point (`screen_point_to_image_point`);
  evidence gains canonical `screen_point`, `scope`, `observation_id`.
  `ground_many_one_shot` likewise. `grounded_x_range` /
  `grounded_y_range` re-derived from the screen point (G30 values
  unchanged: [86.0, 526.0] x [1101.0, 1164.0]).
- `scripts/fastpath.py`: new public `screen_point_to_image_point`;
  `dom_rect_to_image_point` reimplemented as screen point plus that
  conversion (identical behavior, kept for tests/legacy).
- `scripts/zen_dom.py`: new `locate_screen_point`; `locate_point`
  reimplemented on top of it (image point derived from screen point at
  the edge).
- `scripts/cu.py`: CLI act and `CodeExecBackend.act` use
  `dom_act.ground_field_ranges` (replacing the silent try/except pass);
  a missing range is logged by `ground_field_ranges` as a fail-loud
  diagnostic (P2-SPEC observation 2), with the DOM hooks still standing.
- Remaining callers of `dom_rect_to_image_point` (enumerated 2026-11-22
  11:47 +07, after the change): ZERO production callers. Remaining
  callers are tests only:
  `tests/test_pick4_fastpath.py` (4 sites: lines 489, 584, 588, 592),
  `tests/test_click2_redteam.py` (3 sites: lines 160, 166, 174),
  `tests/test_click3_redteam2.py` (2 sites: lines 345, 346),
  `tests/test_p2_element_ref.py` (1 test asserting it is kept, plus one
  docstring mention). It CANNOT be deleted yet: those tests pin its
  behavior. It is a thin wrapper now, not a live-path fused conversion.
  The live path uses `dom_rect_to_screen_point` at four sites:
  `dom_act.py:295` (ground_input), `dom_act.py:543`
  (ground_many_one_shot), `zen_backend.py:324` (_screen_point),
  `zen_dom.py:940` (locate_screen_point).

### Item 3: remove unrestricted zen_dom eval from the default agent interface: VERIFIED, no new code

- Already landed in step 0 (commit `18f2304`). Verified this step by
  running the s0 bundle: `cd tests && PYTHONPATH=../scripts:. python3 -m
  unittest test_s0_bundle` gave Ran 29, OK (2026-11-22 about 11:46 +07).
  The CLI eval is gated behind `--debug` / `CU_ZEN_DOM_DEBUG=1`
  (`zen_dom.py` lines 25 and 30). No new code was written for this item.

### Item 4: Zen adapter (OPEN-5): DONE, with prototype gaps owned

- New `scripts/zen_backend.py`: class `ZenDomBackend`, DOM_WINDOW_CLASS
  `zen`, SESSION_TIMEOUT_SECONDS 30. Constructor takes session_factory
  (default ZenSession), windows_fn (Hyprland clients source, required
  for the Zen window-class wait), pointer (optional input delegate),
  marionette/wd ports, session_timeout_s, verified_moz_inner (see the
  validator section). dom_start opens the session, waits for a Zen
  window class bounded by the timeout, returns ok; raises ZenDomError
  when no Zen window appears and closes the session. close() is
  idempotent, in finally; __enter__/__exit__ support. dom_tabs via
  session.list_tabs(). dom_observe(target, scope, max_elements): scope
  MANDATORY; target resolved by int index via tab_at or title/url/handle
  substring via list_tabs then tab_at; harvest([scope]); snapshot dict
  with snapshot id, title, url, elements carrying ref, name, rect,
  plan_rect, state via field_value; window_bounds and window address
  captured at observe time; backend snapshot store with 120s expiry.
  dom_act validates via element_ref, checks window move via
  live_window_origin with one re-observe, per-action _revalidate
  (resolve, unique, visible, interactive, rect agreement,
  distinguishing-state match via field_value, stability, uncovered),
  disposition via element_ref.decide_disposition, batch-level strict,
  non-strict moved-plus-confirmed re-grounds once and acts on the fresh
  screen point (result records re_ground with plan_rect and live_rect),
  strict rect_moved-plus-confirmed re-observes once to supply a fresh
  snapshot for the re-plan without executing. Disagreements return the
  section 7 shape. Pointer delegate missing: click/fill/key/scroll
  return a structured refusal (code no_pointer_delegate) instead of
  acting. Wait executes locally; assert executes via the session
  (text/value via field_value/verify_typed; checked NOT supported,
  returns refusal). Send keys verify via sent_bubble_contains.
  Per-action CB-1 three-part results; top-level ok; on success
  re-harvests for `after` unless no_after.
- `scripts/cu.py`: `CodeExecBackend` gains dom_backend param,
  DOM_WINDOW_CLASS property (`zen` when delegated, else `chromium`);
  dom_start/dom_tabs/dom_observe/dom_act delegate when set; the
  code-exec command branch constructs ZenDomBackend when env
  CU_DOM_BACKEND is `zen` (windows_fn from hypr clients, pointer None).
- `scripts/code_exec.py`: `_wait_for_dom_window` uses backend
  DOM_WINDOW_CLASS via getattr with case-insensitive prefix match
  (superset of == `chromium`); `_compact_observation` returns `scope`
  as well as `id`.
- Prototype gaps owned (step-9 prototype must prove): real
  pointer/keyboard delegate wiring (needs a broker-owned session with a
  fresh window observation plus desktop_act; until then the backend
  grounds and verifies but refuses input actions with no_pointer_delegate);
  tab resolution by full list_tabs scan cost (cache handle list);
  role/name enrichment for Zen snapshots (needs harvest extension in
  zen_dom; refs are selectors here); checked-state assert reader (no
  ZenSession API); shadow-DOM fallback shape (OPEN-6, owner P3 re-run
  worker); BiDi handover (P7) dissolves into the broker design; full
  close-out of the confirm_locate duck-typed fallback (closed on the new
  Zen-backend path with strict=True, remains for legacy fakes).
- Evidence it cannot be proven live here: this worker is repo-only; the
  pointer delegate and the verified origin both need live runs (see open
  items). The interface plus the Marionette-backed adapter are
  implemented; what remains is live proof, not interface design.

### Item 5: F5-source pin vacuity: FIXED

- B5-VERIFY open follow-up 2: forcing `type_ranges = [[0.0, 20.0]]`
  unconditionally in `CodeExecBackend.act` still passed the pin.
- Fix followed from the range re-derivation: the pin in
  `tests/test_click3_redteam2.py` (test_codeexec_and_cli_act_paths_never_supply_x_ranges)
  is REWRITTEN as a behavioral test keeping its name: the unwired path
  must pass type_x_ranges=None / type_y_ranges=None to a desktop_act
  spy; an unconditional [[0.0, 20.0]] fails it. The CLI half is covered
  by the shared helper `dom_act.ground_field_ranges` returning
  (None, None) when nothing grounds (covered by
  test_missing_range_is_logged_not_silent in the P2 file). This is a
  strengthening, not a silent deletion: the mutation that used to pass
  now fails. Verified by the RT2 run below (51 tests, OK).
- Residual (B5 log section 6 item 3, still open): the CodeExec path
  remains unwired by construction without a ZenSession in the allowlist,
  the CLI path unwired without --dom-selector; fail-closed vs
  best-effort awaits adjudication. Not a repair problem.

### Item 6: failing-first: DONE

- Failing-first test file `tests/test_p2_element_ref.py` committed
  `d2da482` and pushed (verified via `git ls-remote`, origin
  todolist-push at d2da482) before implementation. It now holds 86 tests
  (85 at commit time; one added during the validator rework: the
  verified-origin acceptance test, written before its implementation
  in the same rework pass).
- No code change without a failing test first; no test weakened to pass.
  The test changes in this step are model corrections driven by new
  evidence (listed below), each recorded with its evidence.

## Follow-up 1 and 2: the validator fix (items56, MOZ-GROWTH)

### The first version was wrong (model correction, recorded)

- First version (implemented before the MOZ-GROWTH log landed): the
  closure invariant was replaced by two structural invariants plus a
  logged warning, so the live state returned (2783, 980).
- WHY IT IS WRONG: the MOZ-GROWTH pixel proof (log `a42ef12`, verified
  by the coordinator) shows the true viewport origin is (240, 8), not
  the moz-computed (2783, 980). The viewport did not move; Firefox's
  reported mozInnerScreen is offset (+34, +58) from where the viewport
  actually renders. Accepting moz [274, 66] would ground clicks 34px
  right and 58px down from the true origin. The first-version tests
  asserting (2783, 980) were corrected, not weakened: the assertion
  changed because the model of what the origin IS changed, on new
  evidence.

### The reworked fix: verified-origin path (DONE)

- `scripts/zen_dom.py` `check_viewport_geometry` gains
  `verified_moz_inner=None`. Closure overflow (gaps under 0) REFUSES
  again (hard refusal restored, message names the closure and the
  gaps, and cites the pixel proof). When a verified moz is supplied,
  the verified numbers must close (closure, origin inside the window,
  window and monitor containment); when they do, the function returns
  the VERIFIED absolute origin and logs the override (reported moz,
  gaps, verified moz, offset). The absolute_origin argument is ignored
  on the verified path: it was computed from the displaced reported
  moz. The structural fit invariant (inner larger than window refuses)
  stays. The docstring records the MOZ-GROWTH evidence.
- `viewport_origin` gains `verified_moz_inner=None`, passes it through,
  and records the override in `last_geometry_warnings` (reported vs
  verified moz, verified origin). Empty when the gaps close.
- F9/F10 still refused: factor-forgotten origin fails exactness,
  missing factor refuses, factor-2 small window fails the fit
  invariant, raw moz as absolute fails containment. Verified by
  ValidatorFixTests and by the existing test_zen_dom geometry tests.
- The existing test `test_viewport_origin_rejects_off_window_geometry`
  (inner == window, gaps -240/-8) passes UNCHANGED under the restored
  refusal; it was one of the 34 discover failures under the first
  version and is fixed by this rework, not by a test change.
- `scripts/zen_backend.py`: ZenDomBackend accepts `verified_moz_inner`
  (default None) and passes it to viewport_origin in _screen_point,
  with a TypeError fallback to the three-argument call for duck-typed
  sessions and fakes. The live value (240, 8) is a state-dependent
  measurement and is NEVER hardcoded in the repo; wiring the measured
  value is part of the live-proof follow-up (see open items). Until
  then the backend fails closed on a displaced-moz window, which is
  correct.
- Test updates in `tests/test_p2_element_ref.py` (model corrections):
  live state unverified refuses (assertRaisesRegex, `closure`); live
  state with verified moz (240, 8) returns (2749, 922) and logs the
  override naming `verified` and the -34 offset; the session-chain test
  asserts unverified refusal, then verified return plus the recorded
  override; FakeZenSession supplies the pixel-proven verified moz
  [240, 8] and returns the validator's result, so the backend tests
  ground on the true origin [2749, 922]; backend expectations are
  [2949.0, 1137.0] (click, center (200, 215)) and [2949.0, 1237.0]
  (moved click, center (200, 315)), now for the right reason.
- One test-infrastructure correction: FakeWdSession (from
  test_zen_dom) raises `test_zen_dom.ZenDomError`, a different class
  object from the plain-import `zen_dom.ZenDomError`, because
  test_zen_dom loads zen_dom via importlib.spec_from_file_location.
  Assertions on errors raised through FakeWdSession now use
  `test_zen_dom.ZenDomError`, with the reason recorded in the test
  file. The behavior under test did not change.

### MOZ-GROWTH evidence incorporated

- Verdict (log `a42ef12`): no Zen UI element accounts for moz +34/+58.
  Pixel proof (white fixed scratch host, grim screenshot; script
  `~/workspace/c5-moz-pixel.py`, SHA-256
  7e30f8c5c6708dde678f9fc4fd2f33b138d6b07c8d94869f0ba521aab36e1e31):
  the true viewport origin is (240, 8) in the expanded state.
  (240, 8) + inner (677, 1160) gives gaps +8/+8, exactly the C12 values.
- Toggle table: sidebar Ctrl+S moves moz x 274 to 53 (inner 677 to 909)
  but the true origin moves only 240 to 236, and moz y never leaves 66.
  Bookmarks toolbar Ctrl+Shift+B: no moz change. Compact mode
  Ctrl+Alt+C: no change (unbound/no-op). No toggle moves moz toward
  (240, 8).
- The items 5-6 landing (`b44a5ea`) is exonerated; the defect was the
  pre-existing validator's closure model, which is false for the
  current live Zen state. Code defect AND environment trigger, not a
  live-confirm procedure defect.

## Design decision: CLI act branch is binding-when-present, not mandatory

- The original plan made the `cu.py` CLI act branch mandatory. The
  full discover proved that wrong: 20 plus session tests failed with
  `action 0 is missing scope`, masking the real refusal reasons
  (expired observation, wait ms, focus) that the session machinery
  reports, and breaking the typed-refusal and kill-envelope behavior
  (several tests then saw exit code 0 where the session must die).
- Root cause: the actions file is the agent loop's act-now JSON, and
  the loop does not stamp scope/observation_id yet. Evidence:
  `first_action.py` passes the loop's actions file through unchanged
  (session_cmd, no stamping code), and the session suite simulates
  exactly that. Mandatory enforcement on this interface would refuse
  every live batch.
- Correction: the CLI act branch and desktop_act both enforce
  binding-when-present. An action carrying a binding must match the
  observation or the batch refuses before any input; an action without
  the fields proceeds on the legacy pixel path. The program and DOM
  interfaces, where the plan is built with the observation in hand,
  enforce mandatory CB-2 now. Full mandatory enforcement on the JSON
  batch interface needs the agent loop to stamp both fields (open item
  below). This is a model correction from new evidence (the session
  suite plus first_action.py), not a weakening: no test was relaxed; the
  enforcement point moved to where the binding is actually available.

## Migrations (existing tests, not weakened)

- `tests/test_keyboard_preflight.py`: DesktopPreflight.meta gains
  `id: fixture-observation` (scope was already `window`).
- `tests/test_code_exec.py`: FakeBackend.meta gains `scope: window`
  (real cu.observe metas carry `scope: window` at cu.py:980, `screen`
  at cu.py:1014). Program strings stamped from the observation or
  snapshot the program already holds: desktop actions take
  `"scope": obs["scope"], "observation_id": obs["id"]`; DOM actions
  take `"scope": tab["id"], "observation_id": snap["snapshot"]`
  (the DOM scope is the bound target). Sites: happy-path, refusal-dict,
  D1 (act key plus type, dom_act click), persists-across-runs second run
  (scope literal `tab-1`, the tab the first run observed),
  multi-step (desktop wait, DOM click via tabs[0]["id"]),
  TraceBudget api-implementation-lines, AssertPoll exists and contains.
  Direct api_dom_act calls stamped at four sites (accepts-bound-ref,
  confirm-click, refusal-dict, snapshot-at-100s). The age and forged
  snapshot tests need no stamp: their checks run before action
  validation. The P3/P4 templates in
  `improvements/pick1-program-template.md` are stamped (all four
  programs, P1/P2 included for consistency, plus a CB-2 note in the
  Shape rule); the old P3/P4 programs derived from them still fail at
  their asserts, as intended.
- `tests/test_a1_preflight.py`: a `_bind` helper stamps actions with
  scope `tab-1` and the snapshot id; the six api_dom_act call sites are
  wrapped. Refusal tests still expect `not present in the bound
  snapshot` because the binding check passes first.
- `tests/test_core.py`: the screen-observation key test is rewritten to
  the new contract (protocol section 8): the scope refusal is gone, so
  the batch proceeds to the guard, which fails here because hyprctl is
  unavailable in this environment, and no input is sent (focus and
  Pointer never called). Model correction, not a weakening: it still
  proves no input is sent, and now also proves the old refusal is gone.
- `tests/test_first_action.py`: the pre-overlay screen-scope test is
  rewritten to the new contract: a fresh screen-scope key batch proceeds
  to the session attempt and the outcome is the session's outcome.
  The fallback test's refusal message changes from the deleted
  `pointer actions only` to a current `stale_ref: scope_changed`;
  its purpose (a preflight refusal lands cleanly in the envelope) is
  unchanged.
- `tests/test_click3_redteam2.py`: F5-behavior test actions stamped
  with scope `window` and observation_id from the meta; the F5-source
  pin rewritten behaviorally (see item 5).
- `improvements/pick1-program-template.md`: see above.

## Test evidence

- `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_p2_element_ref`: Ran 86, OK (2026-11-22 about 11:44 +07).
- `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_p2_element_ref test_zen_dom test_click3_redteam2`: Ran 179, OK
  (2026-11-22 about 11:44 +07).
- `cd tests && PYTHONPATH=../scripts:. python3 -m unittest test_core
  test_first_action test_session_policy test_session_continuation
  test_session_driver`: Ran 170, OK (2026-11-22 about 11:46 +07).
- `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_code_exec test_a1_preflight`: Ran 62, OK (2026-11-22 about
  11:46 +07).
- `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_s0_bundle`: Ran 29, OK (2026-11-22 about 11:46 +07).
- Full discover, first run (2026-11-22 11:29:42 +07): Ran 2109,
  FAILED (failures=34, errors=10, skipped=17). The 4 pre-existing
  errors were present (test_a11y_skeleton import, test_cursor_file
  setUpClass, test_perf_evidence x2); the rest were the migrations
  listed above, all fixed since.
- Full discover, final run (2026-11-22 11:51:24 +07, elapsed 0:58):
  `cd tests && PYTHONPATH=../scripts:. python3 -m unittest discover
  -s. -p "test_*.py"`. Ran 2110, FAILED (failures=2, errors=4,
  skipped=18). Baseline at `dddbddc`: Ran 2024, 0 failures, 4
  pre-existing errors, 17 skipped. 2110 is 2024 plus the 86 P2 tests.
  The 4 errors are exactly the 4 pre-existing errors. The 2 failures
  are NOT this worker's change: test_preflight_refusal_raises_before_
  any_diagnostics_query (test_act_diagnostics) and
  test_expired_observation_is_typed_preflight_before_focus_or_input
  (test_core) both age a meta by 121s and expect the `observation older
  than 120s` refusal, but got `capture_started_monotonic is invalid`.
  `_valid_capture_identity` (cu.py:780) rejects a non-positive monotonic
  before it checks age, and the VM had rebooted minutes earlier (the
  SIGTERM that killed the first final-discover launch), so the
  monotonic clock was under 121s when those tests ran and the aged
  value went negative. Proof: re-running both tests at monotonic 284s
  gives Ran 2, OK (2026-11-22 about 11:52 +07). No code of this
  worker's touches `_valid_capture_identity` or the validation order.
  The final2 run also reported skipped=18 vs baseline 17; the verbose
  re-run below reports 17, so the 18th skip was a transient of the
  fresh-boot environment (its name is not recorded: the final2 run was
  not verbose). The verbose run is the authoritative final result.
- Full discover, VERBOSE final run (2026-11-22 11:55:40 +07, elapsed
  1:02): `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  discover -s. -p "test_*.py" -v`. Ran 2110, 0 failures, 4 errors,
  17 skipped. The 4 errors are exactly the 4 pre-existing errors
  (test_a11y_skeleton import, test_cursor_file setUpClass,
  test_perf_evidence x2). The 17 skips are the baseline skips
  (cursor renderer missing x12, Lua interpreter unavailable x3,
  CU_HYPRGLASS_SOURCE unset x1, tesseract installed x1). Baseline at
  `dddbddc` was Ran 2024, 0 failures, 4 pre-existing errors, 17
  skipped; this run is Ran 2110 (2024 plus the 86 P2 tests) with the
  same 0 failures, same 4 errors, same 17 skips.
- Per-suite runs above cover every suite that failed in the first run,
  all green.

## Open items (owned, not silent)

- Live validator proof (for the coordinator to commission, NOT this
  worker): origin stage PASS live on window 0x557052b62dd0 with the
  VERIFIED origin (2749, 922), NOT (2783, 980); plus the independent
  cross-check; plus F9/F10 still refused; evidence emitted on both
  success and failure paths (items56 procedure defects P1/P2). The A9
  chain cannot be proven live on this window until the validator is
  fixed; that is a known live-blocker, not a reason to stop the
  implementation.
- Moz-growth cause, open hypotheses (owner: C5-MOZ-GROWTH follow-ups;
  not this worker's to run, repo-only): H1, the moz offset is tied to
  the window narrowing 1863 to 925 (deciding test: widen the window
  and re-read moz; do not resize anything yourself); H2, collapsed-state
  paint anomaly (scratch host renders only 200 of 428 CSS px wide
  although layout is normal; deciding test in the MOZ-GROWTH log);
  H3, one transient read moz (264, 50) while Chrome/ws2 was active,
  not reproduced.
- M1/M2 misdirected keystrokes from the MOZ-GROWTH run: under
  independent investigation by C5-FOCUS-INCIDENT. Not this worker's
  task. Note at log time: its log landed (commit `2d198c4`): M2 caused
  by clone2-watch run 49 ws2 hold, M1 failed focus command on
  pre-focused Brave, Chrome app window has no bookmarks bar, leave M2
  as is. Coordinator verified (commit `4ae8ccc`).
- JSON batch interface, full mandatory CB-2 (owner: coordinator /
  agent-loop owner): the loop must write scope and observation_id into
  act-now JSON before the CLI act branch and desktop_act can enforce
  mandatory binding. Until then, binding-when-present (see the design
  decision above).
- Zen adapter prototype gaps (owner: step-9 prototype worker): real
  pointer/keyboard delegate wiring; tab-scan cost; role/name enrichment;
  checked-state assert reader; shadow-DOM fallback shape (OPEN-6, owner
  P3 re-run worker); BiDi handover (P7) dissolves into the broker design.
- Full single-system coordinates (desktop_act accepting screen points
  instead of image points) belongs to the step-9 prototype, not this
  step; this step deletes the fused rect-to-image function from the
  live path and makes the screen point the canonical evidence, with
  the image point derived at the driver edge for desktop_act.
- F5 unwired-path residual (B5 log section 6 item 3): CodeExec path
  remains unwired by construction without a ZenSession in the allowlist,
  CLI path unwired without --dom-selector; fail-closed vs best-effort
  awaits adjudication.
- B5 limb (ii) repairs are on todolist-push only, absent from main
  (port problem, coordinator decides); not this worker's scope.
- Step 7 gate (final direction section 3): P2 proven on the S2 task
  class with DOM verification mandatory. Unit and fixture proof is in
  this log; live proof on the S2 task class is for the coordinator to
  commission (it needs the live validator proof above first).

## Files changed (to commit, explicit pathspec only)

- `scripts/element_ref.py` (new), `scripts/zen_backend.py` (new)
- `scripts/cu.py`, `scripts/code_exec.py`, `scripts/dom_act.py`,
  `scripts/fastpath.py`, `scripts/first_action.py`, `scripts/zen_dom.py`
- `tests/test_p2_element_ref.py`, `tests/test_a1_preflight.py`,
  `tests/test_click3_redteam2.py`, `tests/test_code_exec.py`,
  `tests/test_core.py`, `tests/test_first_action.py`,
  `tests/test_keyboard_preflight.py`
- `improvements/pick1-program-template.md`
- This log: `improvements/worker-click5-p2-impl-log.md`
- NOT mine, do not stage: the untracked `improvements/*.md` files from
  other workers (codex-discuss-prompt, fcc-discuss-prompt, and others)
  present in the working tree at log time.

# AMEND4 Codex fix log

All times use Asia/Ho_Chi_Minh, UTC+07. The first recorded checkpoint after the required reads was 2026-11-22 05:59:52. This log was drafted at 2026-11-22 07:12:56, for an elapsed time of 1 hour, 13 minutes, 4 seconds from that checkpoint. The initial setup and required reads happened before the checkpoint.

## Setup

1. In `/home/james/workspace/computer-use-wayland`, ran `git fetch origin` first.
2. Created the new worktree with `git worktree add /home/james/workspace/cu-amend4-codex f0ddd41 -b amend4-codex`.
3. Confirmed the worktree base: `f0ddd41dc70e4048329eac42d31b9f58ad3efe3c`. All implementation and test work was done in `/home/james/workspace/cu-amend4-codex`, branch `amend4-codex`.
4. Ran `gh auth status`; authentication was available. Account details were not copied into this log.
5. Read the requested files in this order before changing code:
   `improvements/worker-click3-rtr2-log.md`, `tests/test_click3_redteam2.py`, `improvements/worker-click3-c1r2-review-log.md`, `improvements/worker-click3-c2r2-review-log.md`, `improvements/worker-click3-c3r2-review-log.md`, `improvements/worker-click3-rt-synth.md`, `improvements/worker-click3-amend3-log.md`, `improvements/worker-click2-c12probe-log.md`.

## Changes

1. Geometry: kept viewport size values unchanged in both branches of `viewport_origin`. The validator checks the expected origin and containment in one coordinate system. Added realistic factor-2 coverage, including `[1863, 1176]` to `[2989, 930]`, invalid `[1500, 1000]`, and fallback sizing.
2. DOM gates: added shared search through open shadow roots and nested same-origin frames. Cross-origin frame access fails closed. Focus, hit, arm, harvest, sent-bubble, field-value, and typed verification paths use this traversal.
3. Type band: the vertical band is based on the grounded field rectangle. The CLI act path, `CodeExecBackend.act`, and `BrowserAdapter.act` equivalent are wired to type ranges. No class named `BrowserAdapter` exists in this checkout; `CodeExecBackend.act` is the actual code-exec adapter. Click-anchored bands without complete grounded ranges return unverified.
4. Region fallback: both DOM grounding entry points now require `window_bounds`; a monitor or observation `region` is never used as a window origin. Grounding rereads the live Hyprland bounds and refuses when they changed.
5. Trusted typing flag: the listener records the field value for every trusted input event in a closure-backed recorder. Verification requires that recorded value to equal the current value. A sticky or page-written boolean alone cannot verify typing.
6. `set_value`: compares read-back to the HTML-sanitized expected value. Input removes line breaks; textarea normalizes CRLF and CR to LF. The implementation references the [HTML Standard input rules](https://html.spec.whatwg.org/multipage/input.html) and [textarea rules](https://html.spec.whatwg.org/multipage/form-elements.html#the-textarea-element). This confirms the DOM read-back only; live application confirmation remains a separate step.
7. Supply-chain tests: added checks for forwarding grounded ranges from `focus_type`, image-pixel range mapping, and ranges supplied by `first_action`. Updated relay test adapters to accept the new range arguments without changing assertions.
8. Snapshot events: added a changed-value case requiring `input` and `change` events; the existing same-value case still requires no events.
9. Design notes: the benchmark target is clone1 Brave plus clone2 Chrome on ws2, per the owner definition at 02:05. Replaced the superseded one-Zen-two-tabs sentence. Removed the V4 caret promise per B18.

## Commits before this log

| Commit | Change |
| --- | --- |
| `ddf5673` | Keep viewport geometry units consistent |
| `fee4a29` | Traverse shadow roots and nested frames in DOM gates |
| `199b10a` | Anchor type verification to grounded field |
| `9975660` | Scope click type verification by adapter |
| `96ea721` | Reject monitor region as window origin |
| `d8136dc` | Recheck window bounds before DOM grounding |
| `b9fb33a` | Bind typed verification to trusted value |
| `0eb3429` | Verify sanitized browser field values |
| `b2b59a9` | Cover grounded typing range propagation |
| `d6ed904` | Assert changed snapshot values dispatch events |
| `8c065f6` | Correct benchmark target and caret scope |
| `c0c049e` | Update relay fixtures for typing range arguments |
| `81963fa` | Require window bounds for DOM grounding |

## Verification

Build and focused tests:

| Command | Result |
| --- | --- |
| `python3 scripts/build.py` | Passed, native helpers built |
| `python3 -m unittest test_type_verification` from `tests` after build | 59 passed. The earlier run before building lacked the native helper and failed. |
| `python3 tests/test_dom_act.py` | 18 passed |
| `python3 tests/test_zen_dom.py` | 42 passed |
| `python3 tests/test_first_action.py` | 64 passed |
| `PYTHONPATH=scripts:tests python3 -m unittest test_session_policy` | 17 passed |
| `PYTHONPATH=scripts:tests python3 -m unittest test_session_continuation` | 11 run, 10 passed, 1 failed because the old relay test expects a click-anchored band to verify without grounded ranges |
| `PYTHONPATH=scripts:tests python3 -m unittest test_click2_redteam.R7ShadowTests` | 3 passed with the faithful DOM shim |
| `PYTHONPATH=scripts:tests python3 -m unittest test_click3_redteam2.R10FlagTests` | 3 passed |
| `PYTHONPATH=scripts:tests python3 -m unittest test_click3_redteam2.R3aUnwiredPathTests` | 18 passed, including inherited desktop preflight tests |
| `node tests/cdp_snapshot.mjs` | Passed, including changed-value input/change and unchanged-value no-event cases |
| `node tests/cdp_errors.mjs` | Passed |
| `node --check scripts/cdp.mjs && node --check tests/cdp_snapshot.mjs` | Passed |
| `python3 -m py_compile scripts/cu.py scripts/dom_act.py scripts/zen_dom.py scripts/first_action.py tests/test_dom_act.py tests/test_zen_dom.py tests/test_first_action.py tests/test_session_policy.py tests/test_session_continuation.py && git diff --check` | Passed |

The 15 non-contradictory RT proof tests passed with this exact command:

```sh
PYTHONPATH=scripts:tests python3 -m unittest \
test_click3_redteam2.R3aStackedFieldTests.test_band_stacked_fields_low_click_with_x_range_must_not_verify \
test_click3_redteam2.R3aStackedFieldTests.test_band_text_inside_target_field_still_verifies \
test_click3_redteam2.R3aStackedFieldTests.test_band_text_below_band_must_not_verify \
test_click3_redteam2.R3aUnwiredPathTests.test_band_wrong_field_unwired_path_reports_ok \
test_click3_redteam2.R3aUnwiredPathTests.test_codeexec_and_cli_act_paths_never_supply_x_ranges \
test_click3_redteam2.GeometryTests.test_viewport_origin_factor2_small_window_false_refusal \
test_click3_redteam2.GeometryTests.test_geometry_check_accepts_factor_forgotten_origin \
test_click3_redteam2.R10FlagTests.test_typed_flag_forgeable_by_page_script \
test_click3_redteam2.R10FlagTests.test_typed_flag_sticky_across_js_set_value \
test_click3_redteam2.R10FlagTests.test_typed_flag_sticky_python_level \
test_click3_redteam2.R10IframeArmTests.test_arm_typed_flag_misses_iframe_targets \
test_click3_redteam2.IframeReadTests.test_field_value_misses_nested_iframe \
test_click3_redteam2.IframeReadTests.test_field_value_misses_iframe_in_shadow_root \
test_click3_redteam2.IframeReadTests.test_harvest_misses_iframe_targets \
test_click3_redteam2.CdpSetValueTests.test_set_value_newline_text_fails_verification
```

Result: `Ran 15 tests`, `OK`.

Full discover command and final result:

```sh
cd /home/james/workspace/cu-amend4-codex/tests
PYTHONPATH=../scripts:. python3 -m unittest discover -p 'test_*.py'
```

Result: `Ran 1922 tests in 127.609s`, `FAILED (failures=2, errors=4, skipped=2)`. The requested zero-failure result was not achievable without changing acceptance assertions that conflict with the fix list:

- `test_click3_redteam2.R1StaleOriginTests.test_stale_window_origin_accepted_silently` expects the stale point to be within 10 image pixels of the true point, but computes a 1271 pixel difference. Item 6 requires refusing stale origin data.
- `test_click3_redteam2.R1StaleOriginTests.test_region_fallback_readmits_raw_mozinner` expects grounding from a monitor region without `window_bounds`. Item 5 requires refusing exactly that input, so the test errors with `DomActError`.
- `test_session_continuation.RelayBandVerification.test_click_type_verifies_through_input_line_band` expects a band-only result to verify without grounded ranges. Item 4 requires that result to be unverified.
- The other three errors are environment or fixture issues: `test_a11y_skeleton` cannot import `tests`, and the two `test_perf_evidence` cases lack `docs/benchmarks/r5_cdp_aggregate.json`.

Neither `tests/test_click3_redteam2.py` nor `tests/test_click2_redteam.py` was edited.

## Push

Before the first log commit, `git push origin amend4-codex` succeeded and `git ls-remote origin amend4-codex` returned `81963fa2da170419c82d119c48560e780d563853`. The first log commit `029f9c74c2efd54634a572839456583ca173de86` was pushed at 2026-11-22 07:13:35 and verified with `git ls-remote origin amend4-codex`.

## Follow-up item 12

Received at 2026-11-22 07:27:16 +07. At receipt, local and remote `amend4-codex` both pointed to `274270c0af25708debb8039501c45bf97a56dcca`. Read `improvements/worker-cl1sweep-fail-invest-log.md` directly from commit `5f5a2fd` with `git show 5f5a2fd:improvements/worker-cl1sweep-fail-invest-log.md` before changing code. The log's source evidence confirmed that `desktop_act` already produced a scope-matching `result['after']`, while `first_action.run` replaced it with `observe_screen` output. This follow-up log update was made at 2026-11-22 07:44:07 +07, 1 hour, 44 minutes, 15 seconds after the 05:59:52 checkpoint.

### First-principles decisions for all 12 items

| Item | Decision | Evidence and reason |
| --- | --- | --- |
| 1. Geometry | Redesign the conversion around explicit units and dimension closure. | The live C12 probe establishes window-relative mozInner values. The formula is Hyprland window origin plus mozInner in screen pixels; size inputs remain unchanged. F9 and F10 cover incorrect containment and a forgotten factor. A factor tweak would hide the source-unit error. |
| 2. DOM traversal | Keep one shared `find` traversal and remove gate-specific top-document lookup. | R7 tests show top-document selectors miss shadow and iframe targets. Same-origin recursion reaches nested frames and shadows; cross-origin access remains fail-closed. The faithful shim exercises real selector traversal. |
| 3. Band anchor | Keep the image band as a fallback signal, but anchor both axes to the grounded field rectangle. | R3a stacked-field and wrong-field proofs show click-centered pixels can belong to an adjacent input. A band still helps when no DOM value hook exists, while DOM verification remains the stronger signal. |
| 4. Range wiring | Redesign the act path to carry one grounded x/y range per type group; refuse band-only verification without ranges. | The R3a unwired proof showed the CLI and code-exec paths dropped ranges. `desktop_act` is the common execution seam. This checkout has no `BrowserAdapter` class, so `CodeExecBackend.act` is the actual code-exec adapter. |
| 5. Region fallback | Remove the region-to-window-origin fallback entirely. | A region may be a monitor or crop and cannot identify the window origin. DOM grounding now requires `window_bounds` in every scope. Region-only refusal tests cover both grounding entry points. |
| 6. Stale origin | Keep a live bounds check at the grounding boundary. | A stored observation cannot establish that the window still occupies the same location. Grounding rereads Hyprland bounds and refuses moved or unavailable windows before using the DOM rect. |
| 7. Typed flag | Redesign authority around a closure recorder of trusted event values. | The forgeable boolean is not evidence that the current value came from trusted input. The listener records each trusted value and verification compares it with the current value. The legacy window map remains inert for compatibility and attack coverage; verification never reads it. |
| 8. `set_value` | Keep the setter, but compare its read-back with the browser-sanitized value. | Input and textarea normalize line breaks differently under the HTML Standard. DOM read-back confirms the setter result only; live application confirmation remains separate. Newline tests cover both elements. |
| 9. Supply-chain tests | Keep tests at the public handoff boundaries. | The range must survive `focus_type`, grounded range conversion, and `first_action`. Testing only a helper would not catch a caller dropping the data. |
| 10. Snapshot events | Keep separate changed and unchanged event assertions. | The contract is observable: a changed value fires `input` and `change`, while unchanged content emits neither. The test now checks both paths. |
| 11. Design docs | Remove superseded statements and replace them with the owner target. | The owner definition at 02:05 names clone1 Brave and clone2 Chrome on ws2. B18 drops V4 because the caret is forgeable and can false-fail legitimate edits. The old Zen-tab target and V4 promise were stale. |
| 12. act-now envelope | Redesign `after` as the scope-matching chainable observation and expose the full-screen capture separately as `after_screen`. | `desktop_act` already returns the scope-matching after metadata, so overwriting it loses valid chainability. Full-screen capture remains useful for visual verification, but its explicit name and docs mark it non-chainable. A valid explicit screen observation with key/type now refuses before overlay acquisition. |

### Failing-first evidence and implementation

Added tests before the code change. Both tests first failed against the old implementation:

```sh
python3 tests/test_first_action.py TestRun.test_after_preserves_input_scope_and_labels_screen_capture TestRun.test_screen_scoped_key_refuses_before_overlay
```

Result before fix: `Ran 2 tests`, `FAILED (failures=2)`. The first saw the screen image in `after`; the second reached overlay/session instead of refusing before overlay.

The fallback branch was separately reproduced before the fix:

```sh
python3 tests/test_first_action.py TestRun.test_fallback_returns_desktop_act_after_as_chainable
```

Result before fix: `Ran 1 test`, `FAILED (failures=1)`. The fallback's `desktop_act.after` was overwritten by the screen image.

Fix in `scripts/first_action.py`:

- For an explicit valid observation used with a key/type batch, scope is checked before overlay acquisition. A non-window scope is refused with `scope_mismatch` and no overlay or input.
- `after` now copies the session result or fallback `desktop_act` scope-matching observation reference.
- `after_screen` holds the separate full-monitor verification capture and is documented as non-chainable.
- The test fixture's fresh given observation now includes real window scope and bounds.

After fix, `python3 tests/test_first_action.py` reported `Ran 67 tests`, `OK`. The three new item-12 tests pass. The 15 RT proof tests reported `Ran 15 tests`, `OK`, and `PYTHONPATH=scripts:tests python3 -m unittest test_click2_redteam.R7ShadowTests` reported `Ran 3 tests`, `OK`.

Item-12 commits: `ee8ccb7` added the first two failing-first tests; `aa0fbbb` added the fallback test; `f4c0482` implemented the envelope and preflight change. `git push origin amend4-codex` succeeded and `git ls-remote origin amend4-codex` returned `f4c0482a5126bb6db955c025b225d332ef3b8485`.

### Full discover after item 12

The command remains:

```sh
cd /home/james/workspace/cu-amend4-codex/tests
PYTHONPATH=../scripts:. python3 -m unittest discover -p 'test_*.py'
```

Latest result: `Ran 1925 tests in 127.084s`, `FAILED (failures=2, errors=4, skipped=2)`. This supersedes the 1922-test result above. The two failures and four errors have the same causes listed above: one stale-origin assertion, one ungrounded band assertion, one region-fallback proof error, and three environment errors from import setup and missing benchmark data.

The final log update is committed last, then pushed and checked with `git ls-remote origin amend4-codex`.

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

Before this log commit, `git push origin amend4-codex` succeeded and `git ls-remote origin amend4-codex` returned `81963fa2da170419c82d119c48560e780d563853`. This log is the final local commit. After committing it, push `amend4-codex` again and verify `git ls-remote origin amend4-codex` matches local `HEAD`.

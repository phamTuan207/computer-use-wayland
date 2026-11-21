# Batch 8 council 2: independent re-check of the 12 fix items + C12

Council member: batch 8 council 2, code only. Method: read-only in the
worktree `~/workspace/b8t2/amend` at `4b7d6ac` (HEAD verified on disk:
`4b7d6ac16a797cd5da5c0d6cb9ea3d7a5c3a9f30`). No modification to the
worktree, no suite re-run (that is council 1 and council 3), no coord
edit, no commit, no push. Every line below was read by me from the
files at `4b7d6ac`, not copied from the task 2 report.

Reference report: `docs/clone1-amend-verify-20261122.md` (254 lines by
`wc -l`).

## 1. The 12 fix items

### Item 1: session-continuation regression test - CONFIRMED

`tests/test_session_continuation.py:252` reads exactly
`post = dict(after, pixel_sha256='1111')`, inside the test whose comment
explains the after-capture must simulate landed text with a differing
pixel hash. Exact line, exact content.

### Item 2: G28 widening - CONFIRMED, citation range off by 4 lines

The refusal block is `scripts/first_action.py:474-498`, not 478-498.
`if rejected is not None:` is at 474; the block returns 1 at 498 with
`envelope['path'] = 'refused'` and `fallback_reason` set at 495. The
comment at 480-481 states "The refusal covers EVERY batch, not only
key/type batches", and `has_keyboard` is computed at 491-493 only to
pick the message text via `loud_substitution_refusal(rejected,
has_keyboard)` at 494. The refusal itself is unconditional. The cited
range 478-498 starts inside the comment (line 478 is "refuses LOUDLY
before any session attempt"); the operative range is 474-498. Substance
confirmed; the range needs a correction note.

The flipped test `test_stale_given_observation_pointer_only_refused` is
at `tests/test_first_action.py:620`, exact, and its comment states the
G28 widening.

### Item 3: type_verified=None on the other after-skipped path - CONFIRMED

`scripts/cu.py:2005` reads exactly `result['type_verified']=None`,
inside `if terminal_address is None and not screen_scope:` (1998) with
`result['after_skipped']=True` (1999) and the `if has_type:` guard
(2001). Exact line, exact content.

### Item 4: R1 type verification - CONFIRMED

- `_input_line_changed` def at `scripts/cu.py:1018`, signature
  `(old, new, anchor_y, half=12, min_pixels=3, threshold=50)`. Band
  anchor_y plus or minus half pixels, threshold 50. Exact.
- `type_anchor=None` at `scripts/cu.py:1711`. Exact.
- Focus gate: the `if has_type and focus_check is not None and not
  focus_checked and _group_has_type(a):` check is at 1848, its comment
  "Cheap pre-type focus gate (G30)" at 1849. Exact.
- Type-check hook: `_ok, _reason = _run_check(type_check, 'type value')`
  at `scripts/cu.py:1913`, inside `if has_type and error is None and
  type_check is not None:` at 1912. Exact.
- DOM-value basis: `basis='dom-value'` at `scripts/cu.py:2050`, inside
  `if type_dom_verified is True:` at 2048. Exact.
- Fix-log Stage A correction: `improvements/worker-click-fix-log.md:33`
  states the Stage A note is WRONG under the e4082ff whole-frame-hash
  check and explains the mechanism (any click in the batch sets the
  hash); line 35 describes the amend replacement (input-line-band
  check plus focus gate plus DOM value check) and names the two test
  proofs. Confirmed.

### Item 5: R2 subsumed by item 2 - CONFIRMED in substance, wording correction owed

In production code there is exactly one caller of `_fresh_observation`:
`run()` at `scripts/first_action.py:470`, and the refusal at 474-498
fires whenever `rejected is not None`, with `fallback_reason` set at
495. No proceed path remains in production.

But the report's sentence "_fresh_observation has exactly one caller
in the repo" is literally false. `tests/test_first_action.py` calls
`first_action._fresh_observation` directly at 8 sites: lines 809, 823,
843, 856, 868, 878, 892, 904. The correct sentence is "exactly one
production caller". The R2 subsumption argument only needs the
production path, so the item stands; the wording needs a correction
note.

### Item 6: R3 envelope fields - CONFIRMED in substance, citation off by one line

- Envelope init: `'type_verified': None` at
  `scripts/first_action.py:427` and `'error_code': None` at 428. Exact.
- Session copy: `if isinstance(session_result, dict):` at 543,
  `envelope['type_verified'] = session_result.get('type_verified')` at
  544, `envelope['error_code'] = session_result.get('error_code')` at
  545. The report cites 543-544; the copy spans 543-545, and the cited
  range misses the error_code line at 545. Correction note owed.
- Fallback copy: `envelope['type_verified'] = result.get(` at 597-598
  and `envelope['error_code'] = result.get('error_code')` at 599.
  The cited range 597-599 is exact.

### Item 7: R4 loud refusal and window-only remedy - CONFIRMED

`loud_substitution_refusal(rejected, has_keyboard=True)` def at
`scripts/first_action.py:357`. `if not has_keyboard:` at 378, with the
screen remedy appended at 379 ("or omit --observation and write
coordinates for the screen"). The screen remedy is offered only when
there is no keyboard action. Exact.

### Item 8: R5 raw-exception conversion - CONFIRMED

`_wd` def at `scripts/zen_dom.py:167`. Missing `value` raises
ZenDomError spanning 189-191 (raise at 189, message line at 191, the
line the report cites). `urllib.error.HTTPError` is caught first at
193, before the tuple except at 196-197:
`(TimeoutError, OSError, urllib.error.URLError,
http.client.HTTPException, ValueError)`. The report cites 197, the
continuation line holding HTTPException and ValueError; the clause
starts at 196. HTTPError is a URLError subclass, so catching it first
is the correct order. JSONDecodeError is a ValueError subclass, so it
is covered. Substance confirmed; the cited lines are the operative
lines within their statements.

### Item 9: R6 restore failures raised - CONFIRMED, def line off by one

`_try_restore` def is at `scripts/zen_dom.py:226`, not 227 (line 227
is the first line of its docstring). The docstring states a failed
restore "is never swallowed silently (RT R6)" and `_try_restore`
returns the exception for the caller to raise.

Raise sites confirmed: single-tab path at 304-314 (`_try_restore` called
at 304, raises at 306-308 for both failures, 310 for primary only,
312-314 for restore only); scan path at 331-337 (restore in `finally`
at 331, raises at 334-337 for wedge plus restore failure, 338-340 for
wedge alone). A failed restore is raised on every path, never
swallowed.

### Item 10: R7 scan stops after the first hang - CONFIRMED

Range `scripts/zen_dom.py:317-332`: `wedge = None` at 317, the per-handle
loop at 319, `_is_transport_failure(exc)` at 327 sets `wedge = exc` at
328 and `break` at 329, restore in `finally` at 330-331. The transport
failure sets the wedge, breaks the loop, and the restore runs in
`finally`. Exact.

### Item 11: R8 switch verification - CONFIRMED

`_verify_selected` def at `scripts/zen_dom.py:240`. Its docstring at
257-258 reads "The index is a handle-LIST index (creation order in this
session), not a verified visual tab order". The downgrade is present
exactly as cited. The verify itself reads the current handle at 247
and raises ZenDomError on mismatch at 248-252. Exact.

### Item 12: DOM-first grounding - CONFIRMED, one citation inaccuracy

All def lines exact:

- `scripts/zen_dom.py`: `viewport_origin` 367, `locate_point` 384,
  `hit_check` 405, `focus_check` 423, `field_value` 436,
  `verify_typed` 444.
- `scripts/fastpath.py`: `dom_rect_to_screen_point` 152,
  `dom_rect_to_image_point` 169, `point_in_rect` 206.
- `scripts/dom_act.py`: `ground_input` 38, `ground_many` 64,
  `focus_type` 78.

Test coverage confirmed:

- Rect center: `tests/test_dom_act.py:123`
  `test_ground_input_returns_rect_center_point`, asserting point
  `[306.0, 1132.5]` and viewport_origin `[2533, 914]`. Exact.
- Covered-refusal before any click:
  `tests/test_dom_act.py:132`
  `test_ground_input_covered_refuses_before_any_click`. Exact.
- Miss never types: `tests/test_dom_act.py:233`
  `test_click_miss_never_types`. Exact.
- No extra observes: `tests/test_dom_act.py:227-228` assert
  `observes_added` 0 and `act_observes` 0. Exact.
- 7-case accuracy: `tests/test_pick4_fastpath.py:488`
  `test_grounding_accuracy_across_cases`, body ending at 541 with
  `assertEqual(hits, len(cases))` at 540-541. Case 1 comment at
  491-492 reproduces the G30 numbers (Brave window [2533,914,901,1176],
  field x 86..526, y 1101..1164, center (306,1132.5)). Exact.

Citation inaccuracy: the report's parenthetical says "no extra observes
(tests/test_type_verification.py:195, tests/test_dom_act.py:227-228
assert observes_added 0 and act_observes 0)". Only the dom_act test
asserts those two counters. `tests/test_type_verification.py` contains
zero occurrences of `observes_added` or `act_observes`. Line 195 is the
def of `test_click_type_enter_uses_no_extra_observes`, which instead
asserts `observe_calls == ['fresh', 'persist', 'persist']` ("1
preflight + 1 after + 1 settle, same as pre-fix"). The "no extra
observes" claim is supported by both tests, but by different
assertions; the parenthetical overstates what the 195 test asserts.
Correction note owed. The item itself stands.

## 2. Bonus finding: R10 third bullet - CONFIRMED

In `list_tabs`, the range check runs at `scripts/zen_dom.py:288-292`
(`handle_index` type and range check, raising ZenDomError out of range)
and `current = self.current_handle()` runs at 293, after the check.
The cited range 288-294 covers the check plus the call. Confirmed.

## 3. C12 evaluation: is viewport_origin correct - CONFIRMED

Deciding lines, all read by me:

- `scripts/zen_dom.py:367-383`. `viewport_origin()` returns
  `[window.mozInnerScreenX, window.mozInnerScreenY]` and validates both
  are non-bool numbers, else raises ZenDomError. mozInnerScreenX/Y is
  the viewport origin on the screen, so it already includes the chrome
  height and sidebar width; no per-layout calibration is needed.
- `scripts/fastpath.py:152-167`. `dom_rect_to_screen_point` returns
  `[viewport_origin[0] + center[0], viewport_origin[1] + center[1]]`.
  Scroll offset is already inside getBoundingClientRect by definition.
- `scripts/fastpath.py:169-205`. `dom_rect_to_image_point` computes
  `ix = (sx - rx) * iw / rw` and `iy = (sy - ry) * ih / rh`, with a
  bounds check `0 <= ix < iw and 0 <= iy < ih` that raises ValueError
  instead of guessing a point off the image.
- `scripts/cu.py:995-999`. `image_point(meta, x, y)` returns
  `rx + x*rw/iw, ry + y*rh/ih`. The inverse map is
  `x = (sx - rx)*iw/rw`, `y = (sy - ry)*ih/rh`, which is exactly what
  `dom_rect_to_image_point` computes. It is the exact algebraic inverse
  of `cu.image_point`.
- `scripts/calibration_e2.py:15-17`. The truth formula is stated
  verbatim: "Geometry: screen = region_origin + image_xy *
  region_size / image_size (the same linear map as scripts/cu.py
  image_point). Truth screen = (mozInnerScreenX + rect.cx,
  mozInnerScreenY + rect.cy)." The code matches that formula exactly.

The 7/7 G30 pass count was not re-run by me; my brief is code only.
I verified the test structure at `tests/test_pick4_fastpath.py:488-541`
(the 0.9 accuracy bar assert and the `hits == len(cases)` assert at
540-541). The pass count itself is council 1's to confirm by running.

The two limits the task 2 report lists (no DPR factor, no runtime
AT-SPI cross-check) are live-work items, not code errors in this diff.
Nothing in the code contradicts that reading: the 1:1 pipeline is the
one the formulas assume, and no AT-SPI call exists in the grounding
path.

## 4. Scope checks - CONFIRMED

- Diff stat for `e4082ff..4b7d6ac` over scripts and tests: 12 files,
  1632 insertions, 116 deletions. Matches the report exactly.
- Zero added or removed diff lines in scripts and tests touch the
  `image_point`, `move`, or `_check_entry_pyc` definitions (grep count
  0). The `image_point` mentions in the diff are calls and docstring
  references in new code, not changes to the definition. The one `move`
  mention is an added comment in `scripts/cu.py` ("The has_type block
  sits before def move"), not a definition change.
- The 20 added lines mentioning `_check_entry_pyc` in the unscoped
  diff are all in `improvements/` log and review prose
  (worker-click-amend-log 2, c1/c2/c3 review logs 1 each, codex-cmp 1,
  coord-click-log 3, y13g-fix-log 2, y13g-r2-redteam-log 1,
  y13g-r2-redteam.md 8). Zero are in scripts or tests. The definition
  is untouched.
- Zero em dashes and zero en dashes in the scripts and tests diff
  (0 and 0 by count).

## 5. Verdict

All 12 items CONFIRMED. C12 viewport_origin CONFIRMED. Scope
CONFIRMED. No code error found. The GO verdict in the task 2 report
survives this re-check.

Corrections owed, citation level only, no code change:

1. Item 5: "_fresh_observation has exactly one caller in the repo"
   is false as written; tests call it at 8 sites in
   `tests/test_first_action.py` (809, 823, 843, 856, 868, 878, 892,
   904). Correct to "exactly one production caller".
2. Item 2: refusal range is 474-498, not 478-498. The `if rejected is
   not None:` is at 474.
3. Item 6: session copy spans 543-545, not 543-544. The error_code
   assignment is at 545.
4. Item 9: `_try_restore` def is at 226, not 227 (227 is the first
   docstring line).
5. Item 12: only `tests/test_dom_act.py:227-228` asserts
   `observes_added` 0 and `act_observes` 0.
   `tests/test_type_verification.py:195` asserts the observe call
   sequence `['fresh', 'persist', 'persist']` instead. The "no extra
   observes" claim stands; the parenthetical must not attribute the
   counter asserts to the 195 test.

## 6. What I could not check

- I re-ran no suite; pass counts and times (including the G30 7/7)
  are council 1's to confirm by running. I verified the test code
  exists at the cited lines.
- I did not verify the fail-before counts at `e4082ff`; that is
  council 3's reproduction.
- I did not verify the non-amend commits in the range (batch 7
  corrections, ZT-C, crawls, reviews, coord logs); they are outside
  the CLICK-AMEND scope.
- Live browser proof is out of scope for this council; it is owed by
  the 2-vision benchmark worker on the laptop.

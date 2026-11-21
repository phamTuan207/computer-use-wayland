# Worker CLICK2-C3 review log (council member 3, independent, second round)

Branch: todolist-push. Review target: amend diff e4082ff..4b7d6ac (code
and tests only; the range also holds other workers' log commits, which
are out of scope here). Task start 02:50 +07. Work on the VM only
(code + tests). No live laptop driving, no browser tasks, never
ydotool. No em dash (U+2014) or en dash (U+2013) anywhere in this log
or in any file written by this worker. All times wall-clock
Asia/Ho_Chi_Minh, elapsed from task start 02:50 +07. I did not read
the other council members' or redteam's logs for this round; this
verdict is independent.

## 02:50 +07 (t+0m) Read first, in order

1. improvements/worker-coord-click2-log.md (synthesis, combined design,
   open items).
2. improvements/worker-click-amend-log.md (CLICK-AMEND 12/12 claim).
3. improvements/worker-click-fix-log.md (CLICK-FIX e4082ff base).
4. The five crawl logs (grounding, multiaction, doma11y, thinktime,
   verify).
5. Clone2 bench via `git show origin/main:docs/clone2-dom-grounding-20261122.md`
   (one-shot 66 rects 0.019s Marionette, 0.006-0.011s BiDi, 5/5 clicks
   landed, CDP dead on Zen, one session per browser).
6. For the 12 consolidated items I also read the first-round logs the
   amend implements: C1 846cf0d, C2 9d5ae86, C3 59acd36, RT 6cdebda.
   The 12 items are: C1-1 session_continuation regression, C1-2 G28
   widening, C1-3 type_verified None on the terminal-None path, and
   RT R1-R9. C2/C3 restate C1-1 to C1-3, so the unique set is 3 + 9.

## 02:51 +07 (t+1m) Scope and hygiene, checked on the diff itself

- Code/test diff e4082ff..4b7d6ac: 12 files, scripts/cu.py,
  scripts/dom_act.py (new), scripts/fastpath.py,
  scripts/first_action.py, scripts/zen_dom.py, and 7 test files.
  No Y13g file, no other module.
- Em dash count in the code/test diff: 0. En dash count: 0.
- ydotool: 1 occurrence, the words "No ydotool, no live desktop" in
  the scripts/dom_act.py module docstring. A mention, not usage.
- PII: no email-like string in the code/test diff (grep for @ found
  none in added lines).
- image_point (cu.py:995) untouched: it appears only as unchanged
  context and as a call site. move() untouched. _check_entry_pyc
  untouched: no Y13g file in the diff.
- Note: the amend log's "no changed line touches image_point, move,
  or _check_entry_pyc" holds for the code/test diff.

## 02:51 +07 (t+1m) Test suites re-run by me, on the amend code

From tests/, `python3 -m unittest test_first_action
test_type_verification test_zen_dom test_dom_act test_pick4_fastpath
test_session_continuation test_keyboard_preflight`:
Ran 213 tests in 2.654s, OK.
This matches the amend log's 13-suite 315-test claim in the suites I
re-ran (the 7 named suites are a subset of the 13; the count is
consistent with the per-suite counts).

## 02:56 +07 (t+6m) Full discover run

`python3 -m unittest discover -s tests -p 'test_*.py'`, started
02:56, finished 03:03 +07. Ran 1759 tests in 282.120s, FAILED
(errors=1, skipped=17), zero failures. The single error is
test_cursor_file.CursorFileTests setUpClass (g++ rejects
-std=c++26 on this VM), the pre-existing toolchain environment
issue already recorded by C2. The test_core umask failures and the
test_a11y_skeleton / test_perf_evidence errors from the amend log's
run did not reproduce in this run (1759 tests vs the amend log's
1752: other workers added 7 tests meanwhile; the umask and missing
JSON failures are environment dependent). No failure is caused by
the amend diff. The amend introduces no regression in the full
suite.

## 02:55 +07 (t+5m) Fail-before, worktree at e4082ff

Worktree /tmp/c3-failbefore at e4082ff, new test files plus new
scripts/dom_act.py copied in, old cu.py, first_action.py,
zen_dom.py, fastpath.py kept (native/wtype copied in, since a fresh
worktree lacks the gitignored binary). Results on old code, matching
the amend log exactly:
- test_type_verification: FAILED (failures=1, errors=7).
- test_first_action: FAILED (failures=3, errors=2).
- test_zen_dom: FAILED (failures=6, errors=9).
- test_dom_act: FAILED (errors=9 of 10; the missing-element test
  passes on old code because it raises before touching fastpath).
- test_pick4_fastpath: FAILED (errors=5).
Worktree removed after the run. Fail-before claims hold exactly.

## 02:54 +07 (t+4m) R1 probe: the band false-passes on a caret-only change

This is the finding that decides the verdict. I ran a probe on the
repo's own harness (/tmp/c3-band-probe.py, not committed):
DesktopPreflight stubs run_cancelable, so wtype never runs and zero
text is delivered anywhere. The after image carries only a 3-pixel
caret-like mark on the clicked line (pixels (10,9), (10,10),
(10,11) white), no text. Batch: click (10,10) + type 'hello'.
Result: ok=True, completed=2, type_verified=True,
type_verified_basis=input-line-band, error_code=None, error=None.
Direct predicate check: _input_line_changed(blank, caret, 10) is
True, _input_line_changed(blank, blank, 10) is False.
So the band check cannot distinguish a caret/focus-ring change from
typed text. The amend log admits the band is necessary, not
sufficient, and names the DOM value check as the sufficient check.
The problem is wiring, see item R1 below.

## Review (a): the 12 consolidated items, each verified in code

1. C1-1 session_continuation regression: FIXED. The test fake now
   sets post pixel_sha256='1111' (tests/test_session_continuation.py),
   the same pattern as the sibling test and the preflight harness.
   The test passes in my 213-test run and in the full discover
   (0 failures). The repair is in the fixture, as C1/C2 prescribed.
2. C1-2 G28 widening: DONE. first_action.py run() now refuses
   whenever rejected is not None, for every batch, before any
   session attempt; the has_keyboard gate is gone. The flipped test
   test_stale_given_observation_pointer_only_refused asserts code 1,
   path 'refused', session not attempted, id/age/reason named,
   fallback_reason set. Module docstring updated to "for any batch".
   R9 is satisfied by the widening itself: the _fresh_observation
   docstring ("the caller must refuse loudly instead of acting on
   the substitute") is now true as written.
3. C1-3 type_verified None on the terminal-None path: DONE.
   cu.py terminal_address None branch now sets type_verified None
   with a skip note. Minor sub-issue, see required fix 3: when the
   DOM type check passed on that path (type_dom_verified True),
   the branch still reports type_verified None, because the
   verification block only runs when 'after' is in the result and
   the after-capture is skipped there. The DOM pass is discarded.
   Not a false pass, a lost true pass. Polish, not blocking.
4. RT R1 type verification redesign: PARTIALLY DONE. What is real:
   the band check (cu.py _input_line_changed, full width, anchor
   y plus/minus 12px, threshold 50 above the measured JPEG q90
   max error 39 cited at cu.py:858) kills the proven incident
   shape (click 64px above the field: the band around the click
   line holds no text) and the click-changes-nothing shape (test
   test_click_type_frame_changed_by_click_only_fails). What is
   NOT closed: the caret-only false pass proven by my probe above.
   A correct click that focuses the field changes the band by
   itself (caret, focus ring), so click + stubbed type still
   reports type_verified True. The sufficient DOM check exists
   only as optional hooks (focus_check, type_check in
   desktop_act), and no production caller passes them:
   first_action.py:581 fallback, cu.py:2470 session path, and
   cu.py:2759 CLI act all call desktop_act without hooks.
   scripts/dom_act.py is the only passer, and nothing imports or
   calls scripts/dom_act.py (grep over scripts/ and tests/ finds
   no caller outside its own test). So the live path still
   verifies with a necessary-not-sufficient signal, exactly the
   defect class R1 gated on, narrowed but not closed. Two more
   narrowing gaps in the same item: the band anchors on the last
   pointer target before the FIRST type only, and the focus gate
   runs only before the first type group, so in a two-input batch
   the second type has neither a band check on its own line nor
   a focus re-check.
5. RT R2 pointer substitution top-level flag: SUBSUMED. The
   widening (item 2) removes the proceed path entirely, so there
   is no pointer-only substitution left to flag. Done by refusal.
6. RT R3 envelope type_verified/error_code: DONE. first_action.py
   copies both from the session result (None when absent) and
   overwrites them from the direct desktop_act result on the
   fallback path. Verified in the diff.
7. RT R4 refusal remedy: DONE. loud_substitution_refusal now takes
   has_keyboard: the key/type path offers only the fresh window
   observation remedy; the pointer-only path also offers the
   screen-coordinates remedy. Verified in the diff.
8. RT R5 zen_dom raw escapes: DONE. _wd converts ValueError
   (JSONDecodeError is a ValueError subclass, so a non-JSON body
   is caught) and http.client.HTTPException, and a JSON object
   without a "value" member now raises ZenDomError instead of
   escaping as a raw KeyError. http.client is imported at
   zen_dom.py:48. Verified in the diff.
9. RT R6 restore surfacing: DONE. _try_restore returns the
   restore error instead of swallowing it; tab_at and the full
   scan both raise when the original tab cannot be restored,
   including the combined primary-plus-restore message. Verified
   in the diff.
10. RT R7 scan budget: DONE. list_tabs stops after the first
    transport failure (_is_transport_failure keys on the _wd
    "transport failure" text, plus raw TimeoutError/OSError)
    and raises naming the wedge, instead of burning one timeout
    per handle. Non-transport per-handle failures are still
    recorded and skipped. Verified in the diff.
11. RT R8 tab verify / downgrade: DONE via the downgrade
    alternative. tab_at docstring and CLI help now say
    handle-LIST index (creation order, not visual tab order),
    and _verify_selected checks the switch actually took effect
    (current handle equals the requested handle) with the
    title/URL read belonging to that tab. Verified in the diff.
12. RT R9 docstrings: DONE. See items 2 and 11: the G28 module
    docstring now claims the widened behavior, which the code
    does, and the tab claim is downgraded. No overclaim remains
    in the touched docstrings.

G28 widening, special attention (stale SCREEN observation case):
blanket refusal does refuse one legitimate case: a stale given
SCREEN observation with screen-written pointer coordinates would
have worked on the substituted screen capture, since both regions
are the monitor box. The rejected dict carries no scope (only
given_id, age_s, reason), so run() cannot tell that case apart.
I judge blanket refusal correct anyway: the screen content is
100+ s old and may have changed, the session guard would likely
refuse on screen change, and the cost of refusing is one
re-observe round trip, which is the documented procedure. The
no-observation default is unaffected (rejected is None). The
over-refusal is real but cheap, and plumbing scope through the
rejection to preserve it is an optional refinement, not required.
Key-only batches (Escape, Ctrl+Tab) are also refused on a stale
observation, but they would fail on screen scope in desktop_act
anyway, so that is a louder failure, not a new one.

Owner corrections (item 12 replaced, DOM-first grounding + cheap
verification, no slow observe cycles): PARTIALLY DONE. The DOM
helpers exist (zen_dom viewport_origin, focus_check, field_value,
verify_typed, hit_check, locate_point; fastpath
dom_rect_to_image_point; dom_act orchestrator), and the bar
numbers are measured: observes per task unchanged at 3
(preflight fresh + after-capture + settle re-capture, asserted by
test_click_type_enter_uses_no_extra_observes), actions per
observation 3 in the batch, grounding accuracy 7/7 synthetic in
both the fastpath and dom_act suites. But the 7/7 number is
circular, and the C12 conversion is not satisfied; see
adjudication (c) below. Live accuracy and live wall time vs the
Codex 2.5 min mark remain owed by the 2-vision benchmark worker,
as the amend log honestly states.

## Review (b): the combined design in the synthesis log

The design composes soundly as a design: no direct contradiction
between its steps. Gaps and conflicts, each a build item, not a
refutation:
- Step 1 (one-shot bulk DOM harvest, Mantis numbered text) is NOT
  what the amend built. ground_many is per-element: locate +
  viewport_origin + hit_check, 3 evals per element (6 DOM calls
  for 2 inputs). The clone2 bench proves the bulk shape is 55x
  faster per element (one-shot 66 rects 0.019s Marionette vs
  16 ms each per-element). The design should mandate the bulk
  harvest; the amend's per-element path is a placeholder for it.
- CDP for Brave vs dead on Zen: the design splits correctly per
  browser (Marionette Zen, CDP Brave). The conflict is on the
  Brave side: doma11y open item 4 (Brave refuses
  --remote-debugging-port on the default user data directory and
  it cannot be enabled on an already-running browser) conflicts
  with driving the user's already-logged-in Brave. The design
  needs the live Linux behavior verified before the CDP half is
  built on.
- BiDi vs Marionette under the one-session constraint: the design
  picks Marionette for Zen, which is consistent, but any step
  that needs BiDi locateNodes AND a Marionette session on the
  same Zen instance is forbidden by the constraint clone2 proved
  (one active session per browser, "Maximum number of active
  sessions"). Sequence protocols, never open both at once. The
  bench also shows rects agree across protocols to 5.7e-14 px,
  so protocol choice is free on accuracy; choose by session
  cost (BiDi session.new 1.5-2.8 s cold, 0.014 s warm).
- HCU guard feasibility: feasible in principle (a zen_dom
  evaluate per target is milliseconds), but the amend implements
  no per-action guard: the focus gate runs once before the first
  type group, and there is no hit re-check before the second
  click. If the clone1 send changes the layout, the clone2 click
  uses stale coordinates with no re-check. The design's step 3
  guard must be built as a per-action check, not a per-batch one.
  Also missing from the design: the exactly-once intent ledger
  (multiaction C15). A retried batch can double-send; the design
  states exactly-once intent per send but builds no ledger for it.
- Mantis numbering on live Messenger pages: the design assumes a
  numbering layer that does not exist in the repo. The harvest
  returns selectors, not stable refs; refs must be minted per
  snapshot and remapped per call, and Messenger is React plus
  contenteditable with a dynamic DOM, so ref stability across
  re-reads is unproven. Mantis itself is Chromium-side and its
  vendor numbers are single-run, caveated, and measured against
  its own tool. Numbering is a real build item with a live-page
  proof owed, not a free import.
- Step 4 claims V1+V2+V3+V4+V11 in one evaluate per step. The
  amend implements V1/V2/V3 (field value, innerText via
  field_value, activeElement via focus_check) but NOT V4 (caret
  position) and NOT V11 (MutationObserver / input-event flag
  armed before typing). V12 (sent-bubble finish gate) is also
  unimplemented anywhere. Step 4 is a design, not built code.
- Step 6 loop hygiene (prompt caching, diff-gating, downscale,
  context editing, low effort, adaptive waiting): no conflict
  with anything, just unbuilt. No objection.
- Outcome scoring (M1) is correctly adopted as the acceptance
  metric for the benchmark; the amend's synthetic 7/7 is a
  point-in-rect score and must not be quoted as outcome accuracy.

## Adjudication (c): C12 conversion layer

Does dom_rect_to_image_point (calibration_e2 chain) satisfy the
doma11y C12 requirement (viewport CSS px to screen px via Hyprland
window geometry + DPR + viewport origin, AT-SPI cross-check)?
NO. A further build is still open. Evidence from the code, not
from the amend log's word:
- dom_rect_to_image_point (fastpath.py) computes screen =
  viewport_origin + rect center, then image = (screen - region
  origin) * image size / region size. It treats viewport_origin
  as the ABSOLUTE screen position of the viewport origin.
- The only live evidence in the repo, docs/calibration-e2-report.md,
  says the opposite for this Zen build: "mozInnerScreenX/Y in this
  Zen build are WINDOW-relative (240, 8), not absolute screen
  coords. Truth table is window-relative CSS px; add the window
  origin (2509, 914) for screen px." The amend never adds the
  window origin: it reads no Hyprland geometry, never uses
  meta['window_bounds'] or meta['monitor_scale'], and reads no
  devicePixelRatio. On the E2 numbers the amend's screen point is
  wrong by the window origin, and the image point lands outside
  the observed image, so ground_input raises DomActError. That is
  fail-closed (no wrong click), but the DOM-first path would be
  non-functional live on this Zen build until the window-origin
  term is added.
- The tests cannot catch this because they are circular: every
  case feeds origin=[window origin] (e.g. [2533, 914]) and rects
  already in screen coordinates (e.g. {'x': 86, 'y': 1101}), so
  the mapping is self-consistent by construction. A true test
  would feed a viewport-relative rect (field y about 179 in the
  G30 window) plus a window-relative origin (about [240, 8])
  plus the window origin from the meta, and assert the image
  point. No such test exists.
- No AT-SPI cross-check exists anywhere in the amend. AT-SPI is
  also unverified on this VM (no daemons, no pyatspi, per the
  clone2 bench), so the cross-check half of C12 is unbuilt and
  unproven.
- No DPR term exists. The E2 setup was scale 1, dpr 1, so the
  omission is untested, not proven harmless. meta carries
  monitor_scale and the truth carries dpr; the amend uses neither.
- One correction to a possible counter-reading: the ZT-B log line
  "mozInnerScreenX returned null, NOT usable" is NOT proof that
  Marionette cannot read it. The same log documents the cause:
  those evals omitted `return`, and WebDriver execute/sync needs
  an explicit return. viewport_origin() does include `return`.
  Whether Marionette returns mozInnerScreenX live on Zen is
  unproven either way and must be proven on the laptop, not
  inferred from that line.
- Required C12 build: absolute viewport origin = Hyprland window
  origin (hyprctl clients, or meta window_bounds) + mozInnerScreenX/Y
  (window-relative per E2) + DPR scaling, cross-checked against
  AT-SPI screen extents of the same element within a few px, with
  the circular tests rewritten to true viewport-relative inputs.
  Until that lands and is proven live on Zen via Marionette, the
  DOM-first path must not be trusted live; it fails closed, which
  is the safe direction, but it is not yet a working grounding path.

## Verdict: AMEND

The amend is a strict improvement on every axis and introduces no
regression (full discover 0 failures), and it fails closed where it
is wrong. It is not BLOCK, because nothing that worked before is
broken and no live path is made worse. But it must not land as
closing R1 or C12, because the two headline items are only partly
done on the live path. Required fixes, with file and line evidence:

1. Close the R1 caret-only false pass (the gating item). Either
   (a) wire the DOM hooks into a production path: first_action.py
   fallback (line 581) and cu.py:2470 / cu.py:2759 must pass
   focus_check/type_check closures built from a zen_dom session
   (or call scripts/dom_act.py focus_type, which currently has no
   caller), so the sufficient DOM value check actually runs live;
   or (b) make the band sufficient without DOM: require the band
   change to exceed a caret-scale baseline (e.g. count changed
   pixels against the caret-only shape, or require text-shaped
   change on the line). Whichever is chosen, add the test my
   probe defines: click + stubbed type with a caret-only after
   image must report ok False, type_verified False,
   error_code type_unverified. Verify with the 7-suite run plus
   the probe. The amend's own test
   test_click_type_frame_changed_by_click_only_fails only covers
   the click-changes-nothing shape, not the caret shape.
2. Fix the C12 conversion (adjudication above). In
   scripts/fastpath.py dom_rect_to_image_point and
   scripts/zen_dom.py viewport_origin / locate_point: add the
   Hyprland window origin term (from hyprctl clients or
   meta['window_bounds']) and the DPR / monitor_scale term, add
   the AT-SPI cross-check, and rewrite the 7 accuracy cases in
   tests/test_pick4_fastpath.py and tests/test_dom_act.py to true
   viewport-relative rects + window-relative origin + window
   origin. Verify live on Zen via Marionette (mozInnerScreenX
   readable, point lands in the field, click verified by DOM
   state), not only on synthetic fixtures.
3. Per-type-group verification for multi-input batches. In
   scripts/cu.py desktop_act: run the focus gate before EVERY
   type group (drop the focus_checked once-only flag or reset it
   per group) and anchor a band per type group (the last pointer
   target before that type), not only before the first type.
   Verify with a two-input click+type+click+type test where the
   second type is stubbed.
4. Minor: preserve a passing DOM type check on the
   terminal-None path. In scripts/cu.py, the terminal_address
   None branch sets type_verified None even when
   type_dom_verified is True; consult type_dom_verified there
   the way the after_capture=False branch does, so a DOM-verified
   type reports type_verified True with basis dom-value.
5. Do not present the amend as closing R1 or C12, and do not quote
   the synthetic 7/7 as live accuracy, until fixes 1 and 2 are
   verified. The live proof stays owed: the 2-vision benchmark
   with outcome scoring (both messages landed), which also
   settles the live wall time vs the Codex 2.5 min mark.

What is sound and needs no change: the G28 blanket refusal, the
session_continuation fixture repair, the R3 envelope fields, the
R4 remedy split, the R5 _wd conversion, the R6 restore surfacing,
the R7 scan stop, the R8 handle verification plus claim
downgrade, the R9 docstrings, the 0-observes-added bar number,
and the fail-before evidence for all five new suites.

## Notes for the parent (not verdict items)

- ZT-C is DONE as of 02:57 +07 (MEMORY.md update during this
  review): ZT-07/08 PASS, ZT-09/10 FAIL, live lane free. The
  baseline run the synthesis log lists as owed is no longer
  blocked by the lane, though the installed laptop code still
  lacks e4082ff, which is good for the baseline.
- Owner decision 03:04 +07: the last30days-skill repo source was
  read and judged not dangerous, owner encourages its use. That
  resolves synthesis open item 6 (the -g install question is now
  the owner's call, already made: use the source).
- My probe script is at /tmp/c3-band-probe.py (scratch, not
  committed). It can be turned into the required test for fix 1.

## 03:05 +07 (t+15m) Close

Verdict AMEND, 5 required fixes above. Writing this log, committing
with explicit pathspec only, pushing, verifying via ls-remote.

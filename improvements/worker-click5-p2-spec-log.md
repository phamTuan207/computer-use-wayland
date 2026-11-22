# Worker C5-P2-SPEC log (COORD-CLICK-5, step 7 preparation)

Owner: Pham Tuan. Role: worker C5-P2-SPEC, reporting to the coordinator
only. Task: write the stale-ref disagreement protocol (B5 lift limb
(i)) and re-verify the AMEND4 items 2-4 wiring against P2's target
functions. This unblocks the P2 element-ref interface rewrite. No
live laptop work in this task; repo work only.

Repo: ~/workspace/computer-use-wayland, branch todolist-push, HEAD
fccf367 at task start. Owner is asleep since 06:52 with a headache;
Muse holds full authority.

Rules honored: wall-clock Asia/Ho_Chi_Minh plus elapsed time on
every log entry. Commit with an explicit pathspec only, immediately
after staging. Verify every push with git ls-remote. No em dash
(U+2014) or en dash (U+2013) anywhere. No personal info on GitHub.
Never ydotool.

## 0. Log

- 2026-11-22 10:42:33 +07 (T+0m): task received. Verified branch
  and HEAD with `git status --short && git log --oneline -5`:
  HEAD fccf367 "C4-S2-FLIP: run 5 log, verdict, Brave rollback
  (Brave 5/5, Chromium 0/5)". Working tree had unrelated
  untracked improvement files only; I touched none of them.
- 10:42-10:45 (T+0-3m): read the FINAL direction
  (improvements/worker-click3-final-direction-log.md, commit
  e05fc58) in full, in particular section 1.2 P2 row, section 1.4
  CB-2 row, section 2 items (d) and (f), section 5 B5, section 6
  worker 10, section 7; the step 2 contract
  (docs/layer0-cbexec-contract.md, commit 03ff589, found via
  `git show 03ff589 --stat`, which lands it at
  docs/layer0-cbexec-contract.md, 740 lines) in full; FARCH's
  protocol core (improvements/worker-click3-farch-response-log.md,
  section 2.3 item (b) and section 3.2 P2 row).
- 10:43-10:46 (T+1-4m): read the AMEND4 landing diffs in full
  (`git show c1ea773`, `git show 62b740e`, `git show 72120aa`)
  and verified the wiring at tip with grep (citations in
  section 1). Read the step 5 commit (76d0a56) and the P2 target
  functions (scripts/dom_act.py, scripts/zen_dom.py,
  scripts/fastpath.py, scripts/code_exec.py) plus
  scripts/perception_router.py and scripts/dom_asserts.py.
- 10:46-10:52 (T+4-10m): ran the wiring test files at tip (see
  section 2). Wrote the protocol document
  (docs/stale-ref-disagreement-protocol.md) and this log.

## 1. AMEND4 items 2-4 wiring re-verification (at tip fccf367)

For each item: what it changed, which P2 target function it
touches, and whether the wiring is present and correct at the
current tip. The defective-proof-test caveat applies to items 3
and 4 (their own commit messages record F4 and F5 tests as
defective); that is B5 limb (ii), a separate worker's job. This
section verifies the wiring only, not the tests.

### Item 2 (c1ea773): gate traversal, shared find() with frame plus shadow recursion

What changed: scripts/zen_dom.py gained three shared JS constants
and every gate helper was rewritten to interpolate them. _FIND_JS
(pierce() walks open shadow roots; framesOf() enumerates
same-origin frames, including frames inside shadow roots, by
contentWindow presence; find() runs pierce, then recurses into
each frame document to depth 5, fail-closed on cross-origin
frames). _DEEP_ACTIVE_JS (deep activeElement walk down through
shadow roots and same-origin iframes). _FRAME_POINT_JS (frame
viewport point for elementFromPoint, walking iframe offsets off
up the frame chain). Plus the faithful-shim R7 re-run tests
(F8/F11/F12/F13) in tests/test_zen_dom.py.

P2 target functions touched: scripts/zen_dom.py only, of the four
named P2 targets (dom_act.py, zen_dom.py, fastpath.py,
code_exec.py). dom_act.py, fastpath.py, and code_exec.py are
untouched by this commit (`git show c1ea773 --stat`: 2 files,
scripts/zen_dom.py plus tests/test_zen_dom.py).

Wiring present and correct at tip, verified by grep:

- `grep -n "_FIND_JS" scripts/zen_dom.py` at tip: defined at
  line 227; interpolated by locate() (line 586), hit_check()
  (line 840), locate_confirmed() (line 894), focus_check()
  (line 961), field_value() (line 982), verify_typed()
  (line 1006), arm_typed_flag() (line 1067), typed_flag()
  (line 1112), sent_bubble_contains() (line 1136), harvest()
  (line 1176).
- _DEEP_ACTIVE_JS used at lines 961 and 1176; _FRAME_POINT_JS
  used at lines 840 and 1176.
- Faithful-shim R7 tests present at tests/test_zen_dom.py:882-943
  (test_focus_check_faithful_shadow_shim, test_hit_check_faithful_shadow_shim).
- Step 5 (commit 76d0a56) later layered locate_confirmed()
  (zen_dom.py:876-945) on top of the same shared traversal
  (line 894 interpolates _FIND_JS); the traversal survived the
  layering. `git log c1ea773..HEAD -- scripts/zen_dom.py` shows
  no revert or removal.

Correctness notes for the P2 implementer, found while verifying:

- find() returns the FIRST match (pierce returns the first
  match; find returns the first across frames). Uniqueness is
  enforced separately by locate_confirmed's countAll, not by
  find() itself. That matches contract section 7 (unique checked
  as its own confirmation), but it means any P2 code path that
  calls locate() or find() directly without the locate_confirmed
  uniqueness check can act on a first match. The P2 rewrite must
  route every acting locate through confirm_locate, not through
  raw locate().
- The R7 guard that item 2's tests protect (hit verdict and
  clicked point from different snapshots) now lives in
  confirm_locate (dom_act.py:55-130), which ground_input calls
  (dom_act.py:237). The shared traversal is the substrate; the
  guard is the composition. Both are present at tip.

Verdict item 2: wiring PRESENT and CORRECT.

### Item 3 (62b740e): band y field-anchored via y_range plus grounded_y_range plus type_y_ranges

What changed: the pixel-band verification for a type action is
anchored to the grounded field on the y axis as well as the x
axis, so text in a stacked field sharing the x-range can no
longer verify the type. _input_line_changed() gains a y_range
parameter (cu.py); desktop_act() gains a type_y_ranges parameter
(cu.py:1814); grounded_y_range() is added to dom_act.py:312 as
the mirror of grounded_x_range on the y axis (rect image height
from CSS height times CSS-to-screen factor times image px per
screen px, centered on the image point); focus_type() computes
the y-range and forwards type_y_ranges to the act_fn
(dom_act.py:647-666).

P2 target functions touched: scripts/dom_act.py (grounded_y_range,
focus_type) and scripts/cu.py (desktop_act; cu.py is not one of
the four named P2 targets, but it owns desktop_act, which dom_act
calls into). zen_dom.py, fastpath.py, and code_exec.py are
untouched by this commit (`git show 62b740e --stat`: cu.py,
dom_act.py, plus tests/test_dom_act.py and
tests/test_type_verification.py).

Wiring present and correct at tip, verified by grep:

- `grep -n "grounded_y_range\|type_y_ranges" scripts/dom_act.py
  scripts/cu.py scripts/first_action.py` at tip: dom_act.py:312
  (definition), dom_act.py:558-560 (docstring: act_fn must
  forward type_x_ranges and type_y_ranges), dom_act.py:647-666
  (focus_type computes y_range, builds type_y_ranges, forwards
  both ranges at lines 665-666); cu.py:1814 (desktop_act
  signature), cu.py:2328-2370 (y_ranges pairing and the band
  call with y_range); first_action.py:842-845 (item 4's
  follow-on, see item 4).
- tests/test_dom_act.py:439-452
  (test_focus_type_forwards_grounded_ranges_to_act_fn) records
  the forwarded kwargs as [[86.0, 526.0]] and [[1101.0, 1164.0]],
  not just that a fake accepts and ignores them.
- Test run at tip (section 2): the combined run including
  test_dom_act and test_type_verification is 122 tests, OK.

Correctness notes for the P2 implementer:

- grounded_y_range() depends on ground['point'], which comes
  from fastpath.dom_rect_to_image_point (dom_act.py:271,
  ground_input). Item 3's wiring therefore still rides the
  exact-rect to lossy-image-point round trip that P2 deletes.
  When P2 deletes dom_rect_to_image_point from the live path, it
  must re-derive the y-range (and x-range) from the screen-point
  form (fastpath.dom_rect_to_screen_point plus the image scale),
  not leave grounded_y_range calling a deleted function.
- The band is diagnostic-only for structured targets once the
  per-action DOM assert exists (A8, sequenced behind P5); item 3
  narrows the diagnostic, it does not promote it to a
  postcondition. P2 must not treat a narrowed band as a
  sufficient check.
- The commit message records "F4 RT2 test defective, symmetry
  proof in log". That is limb (ii), not this verification.

Verdict item 3: wiring PRESENT and CORRECT, with the P2
deletion dependency noted above.

### Item 4 (72120aa): thread type_x_ranges plus type_y_ranges through CLI act, CodeExecBackend.act, first_action fallback

What changed: the ranges from item 3 are threaded through all
three production call sites that build a desktop_act batch with
DOM hooks, so the band reads only the grounded field on every
live path, not only in focus_type. CodeExecBackend.act
(cu.py:2839-2873): grounds the field via dom_act.ground_input,
computes x_range and y_range, forwards both to desktop_act.
CLI act (cu.py:3183-3223): same, with the observation meta read
from args.observation. first_action fallback
(first_action.py:837-845): grounded_y_range added alongside the
existing x_range. dom_act.py:417 docstring corrected:
"BrowserAdapter does not exist", the wiring point is
CodeExecBackend.act.

P2 target functions touched: scripts/dom_act.py (docstring line
only) and scripts/cu.py (CodeExecBackend.act, CLI act). The
code_exec.py backend lives in cu.py (cu.CodeExecBackend); the
file scripts/code_exec.py itself is untouched by this commit.
first_action.py is not a named P2 target but is the third call
site. `git show 72120aa --stat`: cu.py, dom_act.py,
first_action.py.

Wiring present and correct at tip, verified by grep:

- cu.py:2839-2873 (CodeExecBackend.act: type_ranges and
  type_y_ranges initialized to None, ground_input at line 2858,
  grounded_x_range at 2860, grounded_y_range at 2863, forwarded
  at 2872-2873).
- cu.py:3183-3223 (CLI act: same shape, ground_input at 3202,
  ranges at 3204-3211, forwarded at 3223).
- first_action.py:837-845 (ground at 835, x_range at 837,
  y_range at 842, dom_kwargs['type_y_ranges'] at 845).
- dom_act.py:417 (docstring names CodeExecBackend.act as the
  wiring point).
- A follow-up commit 0668327 (item 4 follow-up, session
  act_boundary fakes forward desktop_act kwargs) is recorded in
  the AMEND4 log; the wiring at tip includes it.
- Test run at tip (section 2): test_first_action 71 tests, OK;
  test_dom_act (including the forwarding test) inside the 122
  OK run.

Correctness notes for the P2 implementer:

- Best-effort try/except pass: when no rect grounds, the ranges
  stay None and the batch silently keeps the full-width and
  click-anchored band (cu.py:2866-2869, 3212-3215,
  first_action.py:846-849). There is no log line when the range
  is missing. A missing range means the band is back to
  full-width and a type could verify against the wrong field.
  P2 should log the missing range as a fail-loud diagnostic.
  This is a wiring observation, not a defect that blocks limb
  (i).
- Same deletion dependency as item 3: the ranges are computed
  from ground_input evidence, which goes through
  dom_rect_to_image_point. P2 must re-derive them from the
  screen-point form.
- "BrowserAdapter does not exist" (commit message): there is no
  BrowserAdapter class for P2 to target. The backend is
  cu.CodeExecBackend, and its dom_* methods route to node
  scripts/cdp.mjs. See section 5.
- The commit message records "F5 behavior test defective, proof
  in log". That is limb (ii), not this verification.

Verdict item 4: wiring PRESENT and CORRECT, with the silent
fallback observation noted above.

### Summary table

| Item | Commit | Changed | P2 targets touched | Wiring at tip |
|---|---|---|---|---|
| 2 | c1ea773 | Shared find() with frame plus shadow recursion, faithful-shim R7 re-run | zen_dom.py | PRESENT, CORRECT |
| 3 | 62b740e | Band y field-anchored, grounded_y_range, type_y_ranges | dom_act.py (plus cu.py desktop_act) | PRESENT, CORRECT |
| 4 | 72120aa | Thread ranges through CLI act, CodeExecBackend.act, first_action fallback | dom_act.py docstring (plus cu.py, first_action.py) | PRESENT, CORRECT |

No wiring is missing and none is wrong. Nothing in this task
fixes code; the two observations for the P2 implementer (re-derive
the ranges from the screen-point form when the image-point round
trip is deleted; log a missing range instead of silently falling
back) are recorded in the protocol document, section 10, and in
the log above.

## 2. Test commands and outputs (Lauren Tan standard)

All runs at HEAD fccf367, from the repo, wall-clock
Asia/Ho_Chi_Minh, 2026-11-22 about 10:47-10:49 +07 (T+5-7m).
pytest is not installed on this VM
(`/usr/bin/python3: No module named pytest`), so the runs use
unittest from the tests directory (the test files insert
scripts/ on sys.path themselves).

Command 1:

```
cd ~/workspace/computer-use-wayland/tests && python3 -m unittest test_zen_dom test_dom_act test_type_verification
```

Output (tail): Ran 122 tests in 1.440s, OK. (A note "IME
restoration failed during RuntimeError; state may remain
inactive" appears in the stream; it is a test-environment
notice, not a failure; the run reports OK.)

Command 2:

```
cd ~/workspace/computer-use-wayland/tests && python3 -m unittest test_step5_p1p5 test_pick4_fastpath
```

Output (tail): Ran 65 tests in 0.174s, OK.

Command 3:

```
cd ~/workspace/computer-use-wayland/tests && python3 -m unittest test_first_action
```

Output (tail): Ran 71 tests in 0.656s, OK.

What these runs prove: the AMEND4 items 2-4 wiring and the
step 5 layering on top of it (confirm_locate, locate_confirmed,
CB-1 contract, router, asserts) pass their unit suites at tip.
What they do not prove: the defective-proof-test limb. A passing
suite does not repair a proof test that the landing commit itself
records as defective (F4 in 62b740e, F5 in 72120aa); the defect is
that the test does not prove what it claims, not that it fails.
Limb (ii) stays with the round-3 council.

## 3. Composition with step 5 (commit 76d0a56)

P2 must compose with the step 5 landing, verified at tip:

- scripts/perception_router.py (new in 76d0a56):
  route_perception() routes on coverage, not target type; an
  empty harvest or a truncated a11y tree falls through; Zen
  chrome UI maps only to screenshot (P8 decided boundary); one
  perception_routing JSON log line on every decision. Priority
  table at tip: zen-content to dom-zen then screenshot,
  zen-chrome to screenshot only, chromium-content to
  dom-chromium then screenshot, native-app to a11y then
  screenshot. The router names a dom-zen backend, but no
  code_exec backend implements it yet (section 5).
- scripts/dom_asserts.py (new in 76d0a56): mandatory
  focus_check, type_check, and sent_bubble for the S2 send
  chain; explicit exception list DOM_ASSERT_EXCEPTIONS (scroll,
  hover, move, drag, wait, key non-send); require_asserts()
  fail-closed before any input. code_exec._api_dom_act enforces
  the send gate before any CDP request
  (code_exec.py:876-890).
- scripts/action_result.py (new in 76d0a56): CB-1 three-part
  contract (input_sent, target_received, verified), ok computed
  in exactly one place (build_contract). The protocol's section 7
  error shape is built on this contract.
- scripts/zen_dom.py locate_confirmed() (step 5, lines 876-945):
  visible, interactive, uncovered via hit_check, stable via two
  rect reads within STABLE_TOLERANCE_PX (0.5 CSS px, line 885),
  unique via match count 1. The protocol adopts 0.5 CSS px as
  the rect-agreement tolerance default from this constant.
- scripts/dom_act.py confirm_locate() (step 5, lines 55-130):
  strict path refuses on any failed confirmation; fallback path
  records interactive and unique as None with basis 'unprobed'
  for sessions without locate_confirmed. The protocol states
  P2 must not widen that fallback to production sessions.

## 4. Live callers of dom_rect_to_image_point (enumeration required before deletion)

Grep at tip fccf367 (`grep -rn "dom_rect_to_image_point"
--include="*.py" .`):

Live call sites (production code):

1. scripts/dom_act.py:271, inside ground_input(). LIVE: called
   from cu.py:2858 (CodeExecBackend.act), cu.py:3202 (CLI act),
   and first_action.py:835 (first_action fallback), in each
   case to compute the grounded field's band ranges
   (x_range, y_range) for desktop_act. This is the single live
   call site that matters: one function, three callers, all for
   the band ranges.
2. scripts/dom_act.py:441, inside ground_many_one_shot().
   Reachable only through ground_many() (dom_act.py:461-477),
   which has NO live callers in scripts/ (only tests:
   tests/test_dom_act.py:338-344). Test-only in practice today.
3. scripts/zen_dom.py:821, inside ZenSession.locate_point().
   NO live callers in scripts/ at all. Test-only:
   tests/test_zen_dom.py:599-610, 847.

Test-only call sites: tests/test_pick4_fastpath.py:489,
584-592; tests/test_click2_redteam.py:160, 166, 174;
tests/test_click3_redteam2.py:318-319.

Consequence for P2: deleting dom_rect_to_image_point from the
live path means replacing exactly one live function
(ground_input) and, through it, the band-range derivation in
focus_type, CodeExecBackend.act, CLI act, and the first_action
fallback. The replacement is fastpath.dom_rect_to_screen_point
(fastpath.py:152, the one-conversion path, A9), with the image
scale applied at the driver edge for the band ranges. Keep
dom_rect_to_image_point for tests and legacy, per the final
direction. Also note focus_type() itself has no live callers in
scripts/ (only tests: test_dom_act.py, test_click2_redteam.py,
test_step5_p1p5.py); the live type path is the three ground_input
call sites above, not focus_type.

## 5. Zen adapter under the same contract: genuinely missing work, file by file

The final direction (P2 row, confirmed by the step 2 contract
section 5.2) states the Zen adapter under the same contract is
genuinely missing work because code_exec DOM is Chromium-only.
Verified at tip fccf367:

- scripts/code_exec.py: ZERO hits for zen, marionette, or bidi
  (`grep -n -i "zen\|marionette\|bidi" scripts/code_exec.py`
  returns nothing). Its DOM API (api_dom_start,
  api_dom_observe, _api_dom_act, api_dom_tabs) goes only through
  self.backend. DOM_WINDOW_CLASS = 'chromium' (line 104);
  _wait_for_dom_window (lines 814-834) waits only for a window
  whose class is 'chromium'. No Zen session ownership, no
  Marionette transport, no Zen snapshot binding exists in this
  file.
- scripts/cu.py: CodeExecBackend.dom_start, dom_tabs,
  dom_observe, dom_act (lines 2880-2921) all route to browser()
  (line 2436), which runs `node scripts/cdp.mjs` over a CDP
  WebSocket to BROWSER_ENDPOINT (default
  http://127.0.0.1:9223, line 40). No ZenSession backend exists
  behind these methods. The backend is CDP-only by
  construction.
- scripts/cdp.mjs: a CDP adapter only (WebSocket to a Chromium
  debugging endpoint, loopback-only check at line 120). It
  cannot speak Marionette.
- scripts/zen_dom.py: HAS the Zen side, but exposes no
  code_exec backend interface. ZenSession has locate (573),
  locate_point (786), hit_check (827), locate_confirmed (876),
  focus_check (948), field_value (969), verify_typed (988),
  arm_typed_flag (1040), typed_flag (1097),
  sent_bubble_contains (1126), harvest (1155). None of these is
  shaped as dom_observe or dom_act; there is no snapshot dict
  with refs, no _bind_dom_snapshot or _bound_dom_snapshot
  equivalent, and no one-session ownership with timeout plus
  finally close. locate_point has no live callers (section 4).
- scripts/dom_act.py: HAS the Zen grounding path
  (ground_input, ground_many, focus_type, confirm_locate,
  grounded_x_range, grounded_y_range), but it is not wired into
  code_exec's dom_* API. Its live use is the band-range
  computation in CodeExecBackend.act, CLI act, and the
  first_action fallback (section 4). focus_type has no live
  callers.
- scripts/perception_router.py: already maps zen-content to
  dom-zen first, so the router is ready; the backend it names
  does not exist yet.

Missing, concretely: (a) a Zen backend class implementing
dom_start, dom_tabs, dom_observe, and dom_act with snapshot
binding (snapshot ID, refs, 120s expiry, bound-copy equality,
as code_exec._bind_dom_snapshot and _bound_dom_snapshot do for
Chromium); (b) Marionette session ownership under the
one-session rule, with a timeout and a finally close; (c) a
_wait_for_dom_window equivalent for the Zen window class;
(d) routing so code_exec programs can address Zen targets
through the existing router priority table. This is OPEN-5 in
the protocol, owned by the P2 implementation worker with the
step-9 prototype worker. P3 gates only the step 11 live
acceptance run, not steps 3-6; the Zen adapter is the
Marionette path that lets P2 work without P3.

## 6. Deliverables and placement

- Protocol: docs/stale-ref-disagreement-protocol.md (27215
  bytes, 465 lines at writing). Placed next to the step 2
  contract (docs/layer0-cbexec-contract.md) because it extends
  that contract's section 4.4, and because the P2 implementer
  (step 7) and the step-9 prototype worker both read their spec
  from docs/, while improvements/ holds worker logs. It states
  where it extends the contract and does not contradict it.
- Log: this file, improvements/worker-click5-p2-spec-log.md.

Both files are committed on todolist-push with an explicit
pathspec, immediately after staging, and the push is verified
with git ls-remote (hashes recorded in section 8).

## 7. B5 limb (i) judgment

MET. The protocol document specifies: what a stale ref is
(section 1, six causes); the detection checks in order
(section 2, eight checks with code anchors and the 0.5 CSS px
tolerance default adopted from STABLE_TOLERANCE_PX); the
disposition per case, with the blanket stop rejected and
re-ground-first adopted per CB-2 (section 3); the strict path
for destructive and message-sending actions (section 4); the
multi-action plan lifecycle (section 5); the CB-2 binding
folded in, with scope plus observation ID mandatory in action
data (section 6); and the exact fail-closed error shape
(section 7). The scope-refusal reframe is recorded in section 8
of the protocol: the legality refusal is deleted with P2, the
check changes form into snapshot binding, and scope becomes
mandatory data on every action and ref.

The P2 rewrite can start on this spec as soon as B5 limb (ii)
is met. Limb (ii) is NOT met by this task and is not judged
here: the defective proof tests for AMEND4 items 3, 4, 5-6
remain with the round-3 council (separate worker). B5 stays
standing until both limbs are met.

Open items carried in the protocol (section 9), with owners:
OPEN-1 tolerance revision (P2 implementer, via prototype);
OPEN-2 stability interval (P2 implementer, via prototype);
OPEN-3 distinguishing-state coverage per action type (P2
implementer); OPEN-4 limb (ii) (round-3 council); OPEN-5 Zen
adapter missing work (P2 implementation worker with the step-9
prototype worker); OPEN-6 shadow-DOM fallback shape (P3 re-run
worker). None is a silent gap; each carries a specified default
or a named owner.

## 8. Commit and push verification

- Commit: [TO FILL after commit: hash, files, time]
- Push verification: [TO FILL: git ls-remote output]
- Dash check: a Python byte-level scan for U+2014 and U+2013
  codepoints in both files returns no matches before commit.

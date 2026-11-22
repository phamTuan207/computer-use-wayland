# Batch 12 task 2: (b1) landing spec, set_value plus focus plus CDP Enter into cdp.mjs

Status: design doc only. No code is changed by this file. Base: branch
todolist-push, HEAD 4305dcb. Files read for this spec: scripts/cdp.mjs,
scripts/code_exec.py, scripts/cu.py, scripts/dom_asserts.py,
scripts/s2_flip_live.py, tests/test_s2_flip_wiring.py,
improvements/worker-click5-s2-reopen-log.md (commit 1a3356d),
improvements/worker-click5-input-fix-log.md (commit 4bd6292), and the
run JSONs improvements/s2-flip-b1-runs/run-1..5.json and
improvements/s2-flip-reopen-runs/run-1..5.json, all read from
todolist-push. Every technical claim below cites file plus line.

## 0. What (b1) is, and why it needs landing

(b1) is the input-free send shape: set_value writes the composer text
with the native setter, a focus step puts the caret in the composer,
and a CDP Enter sends it. It uses zero Input.dispatchMouseEvent
calls, so it bypasses the mouse stall that killed the Chromium half
of the original flip (CDP timeout Input.dispatchMouseEvent, dom_act
5003 ms in runs 1, 3, 4 and 5 and 5002 ms in run 2, 0 of 5 sends;
improvements/worker-click4-s2-flip-log.md, section 5).

Measured results, verified first-hand from the run JSONs on
todolist-push:

- (b1) Chromium-only measurement: 5 of 5 sends verified, median wall
  18839.7 ms (18.8 s). Program elapsed 91.575 to 106.622 ms,
  focus Enter 17 to 23 ms, pre-send count 0, delayed count 1, model
  calls 0, all 5 runs. Source: improvements/s2-flip-b1-runs/run-1..5.json.
  The 5 of 5 above is 5 of 5 completed runs, not 5 of 5 attempts:
  runs 2 to 5 each had a first attempt aborted by the routing gate
  (outcome aborted-routing, walls 12365.3, 14372.5, 12652.1, 13734.2
  ms), nothing was sent, and the aborted JSONs are preserved as
  improvements/s2-flip-b1-runs/run-N-aborted.json.
- S2 reopen, two browsers: 10 of 10 sends verified, 5 of 5 runs,
  median wall 28560.9 ms (28.6 s). Chromium program elapsed 99.412
  to 113.005 ms, focus Enter 21 to 25 ms, pre-send count 0,
  delayed count 1, model calls 0, all 5 runs. Source:
  improvements/s2-flip-reopen-runs/run-1..5.json.
- The reopen log recommends EXPAND (improvements/worker-click5-
  s2-reopen-log.md, commit 1a3356d, section 6), but records as an
  open item that the durable landing is still missing: the (b1)
  shape lives in /tmp helpers plus harness flags (same log,
  section 0). This spec is that landing design.

## 1. Where (b1) lives today

Three pieces, in three places. Only the first is landed code.

1. set_value is landed. scripts/cdp.mjs:473 to 533 implements the
   native-setter write, the sanitized read-back, and the input and
   change events. It does NOT focus the field: the branch contains
   no e.focus() call. The read-back is the type_check assert,
   enforced inside cdp.mjs (scripts/dom_asserts.py:26 to 29).
2. The focus plus Enter step is NOT landed. It is /tmp/c5-focusenter.mjs,
   a laptop-only helper. Its behavior is documented in
   improvements/worker-click5-input-fix-log.md, section 7.3:
   Runtime.evaluate focus on textarea[aria-label="Message"], assert
   activeElement is the textarea, then Input.dispatchKeyEvent
   keyDown plus keyUp Enter. Zero mouse events. Returns
   {ok, focus, enter}. The harness calls it from
   scripts/s2_flip_live.py:497 to 519 (focus_enter) and
   scripts/s2_flip_live.py:76 (LAPTOP_FOCUSENTER constant).
3. The program shape is harness-only. scripts/s2_flip_live.py:129
   to 161 (build_program_set_value) emits set_value plus a value
   assert, 2 actions, no key, no focus. The Enter comes from the
   helper after the program returns. The per-browser split is
   selected by --chromium-set-value (scripts/s2_flip_live.py:189
   to 195, variant_for; flags at 780 to 795).

The count guards are also harness-side and also depend on a
laptop-only helper, /tmp/c5-count.mjs (scripts/s2_flip_live.py:77,
478 to 495). They are NOT part of the send method, and this
landing does not move them. See sections 6 and 7.

## 2. Why focus is required, and why it must be enforced

The scratch mechanism probe proves focus decides the Enter
(improvements/worker-click5-input-fix-log.md, section 7.2):

- T1: set_value plus CDP Enter with focus on BODY: 0 bubbles.
  CDP Enter without focus does NOT send.
- T2: evaluate focus() on the composer (focused true), then CDP
  Enter: 1 bubble.
- T3: set_value plus JS-dispatched Enter, no focus: 1 bubble.
  (b2) fallback, untrusted event, live React behavior untested.
- T4: CDP Enter again on the now-empty composer: still 1 bubble.
  A retry after a successful send cannot re-send.

Two consequences follow. First, the landed program must contain
an explicit focus step between set_value and the Enter; an
unfocused Enter fails silently (0 bubbles, no error), which is
exactly the failure mode the P5 gate exists to prevent
(scripts/code_exec.py:922 to 940). Second, the focus step must be
enforced by the gate, not left to program-builder convention:
a program of [set_value, key Enter, assert] must be rejected
before any CDP request, because the Enter would go to BODY and
the run would score a silent no-send. The enforcement point is
scripts/dom_asserts.py, require_asserts, which already fails
closed on unknown action types (see section 5).

The key dispatch itself is trusted and already landed:
scripts/cdp.mjs:390 to 412 (key) dispatches Input.dispatchKeyEvent
keyDown plus keyUp, with text '\r' for Enter (line 410). The
D-B1 probe shows dispatchKeyEvent answers in 2 ms on the stuck
tab, while dispatchMouseEvent times out
(improvements/worker-click5-input-fix-log.md, section 7.1).

For contrast, fill cannot be used here: scripts/cdp.mjs:534 to
541 (fill) starts with click(a), and scripts/cdp.mjs:292 to 313
(click) dispatches mouseMoved, mousePressed and mouseReleased,
which is the stalled call. The fill path also checks
document.activeElement === e after the click (line 536), which
is the focus proof fill already carries. The landed focus action
must carry the same proof, without the mouse.

## 3. Design decision: standalone focus action (recommended)

Two shapes were considered. This spec recommends option A.

Option A (recommended): add a standalone `focus` action type to
cdp.mjs.

- It reuses the existing element-action machinery: ref or
  selector resolution through pageState (scripts/cdp.mjs:157 to
  167), the stale-snapshot check on every action
  (scripts/cdp.mjs:467 to 470), the P2 scope plus observation_id
  binding (scripts/code_exec.py:277 to 284), and the completed
  counter.
- It is independently testable: one action, one assertion
  (activeElement check), using the same fake-CDP vm pattern as
  tests/cdp_validation.mjs.
- It keeps set_value a pure value write with read-back. Its
  contract and its type_check assert stay unchanged
  (scripts/dom_asserts.py:66 to 68).
- It lets any program focus without setting a value.
- Cost: 6 files to touch (cdp.mjs, code_exec.py, cu.py,
  dom_asserts.py, plus the harness scripts/s2_flip_live.py and
  the tests). The 4 mirror files are a one-time validation-mirror
  update, and the mirror already exists for every other action
  type. One small cost under A: the focus branch duplicates
  set_value's unavailable-field checks in a second branch. That
  is a small maintenance duplication; it does not change the
  recommendation.

Option B (not recommended): add a `focus` boolean field to
set_value, so set_value focuses the field before or after the
write.

- Cost: 4 files to touch (cdp.mjs plus dom_asserts.py for the P5
  rule plus the harness scripts/s2_flip_live.py plus the tests).
  No new action type, no validation-mirror change in code_exec.py
  or cu.py.
- Rejected because it bundles two effects into one action and
  loses per-step granularity: with a focus flag inside set_value,
  the completed count cannot distinguish a focus failure from a
  value failure inside set_value (the error string can, the count
  cannot). CB-1 stays sound under B: input_sent would be
  completed >= 2, still a counted action number, so the loss is
  granularity, not accounting ambiguity.
  It also cannot express focus without a value write, so any
  future program that needs focus alone would need a second
  mechanism anyway. The field would also need its own
  preflight validation (focus must be a boolean, default
  false) and its own P5 rule. That is less total work than
  option A: the real delta is the 2 mirror files (code_exec.py,
  cu.py) that A needs and B does not.

The strongest argument for A is fidelity to the measured shape.
The measured (b1) shape is three separate steps: a 2-action
program plus the focus_enter helper returning {ok, focus, enter}.
Landing focus as its own action preserves those measured step
boundaries one to one, so the landed completed count (4) maps
directly onto the measured evidence (program completed 2 plus
helper ok). With B the step shape changes and the mapping from
measured to landed is indirect. Together with the testability
point (focus testable alone, including the zero-Input-methods
assertion) and the reusability point (any program can focus
without setting a value), A is justified.

The coordinator must pick one before landing starts. If option B
is picked instead, sections 4, 5 and 8 below must be rewritten
for the field shape; sections 6, 7, 9 and 10 stand unchanged.

## 4. The landed focus action (option A)

Semantics, replicating /tmp/c5-focusenter.mjs as documented in
improvements/worker-click5-input-fix-log.md, section 7.3, but
resolving the element through the snapshot ref instead of a CSS
selector:

1. Resolve the element with pageState (scripts/cdp.mjs:157 to
   167), exactly one of ref or selector, same as every other
   element action (scripts/cdp.mjs:435 to 437).
2. Reject an unavailable field with the same checks as the
   set_value branch: disabled, the :disabled pseudo-class,
   readOnly, aria-disabled, inert (scripts/cdp.mjs:478). Error
   text 'field unavailable'.
3. Call e.focus() in page context. No scroll, no mouse, no key.
   The evaluate expression is the pageState-resolved element
   followed by e.focus(), the same resolve-then-act shape the
   set_value branch uses.
4. Verify document.activeElement === e. On failure throw
   'field is not editable or did not gain focus', the exact
   wording fill uses (scripts/cdp.mjs:537).
5. Return ok. The action counts toward completed like any other
   action (scripts/cdp.mjs:546).

Notes on scope. The focus action does not scroll the element
into view; set_value already requires the field to be visible
and hit-testable (scripts/cdp.mjs:501 to 502), and the composer
in the S2 class is visible by construction. The activeElement
check is a direct equality check; if a future target lives in a
shadow root, the check must walk shadowRoot.activeElement the
way the harvest does (scripts/cdp.mjs:250 to 251). That walk is
a follow-up, not part of this landing.

## 5. File-by-file edit list (option A)

scripts/cdp.mjs:

- Line 434: add 'focus' to the action whitelist.
- Line 435 to 437: add 'focus' to the element-action list (exactly one
  ref or selector).
- Dispatch loop, after line 473 (set_value branch): add a focus
  branch implementing section 4. It must sit between set_value
  and key in the chain; the loop order follows the action list,
  so no ordering code is needed.
- No change to key (lines 390 to 412), to set_value (lines 473
  to 533), or to fill (lines 534 to 541).

scripts/code_exec.py:

- Line 217: add 'focus' to the allowed set.
- Line 218: add 'focus' to element_actions (ref must be present
  in the bound snapshot, exactly one of ref or selector).
- No new field validation is needed: focus takes no payload
  beyond ref or selector, and the P2 binding check already
  covers every action in the batch (lines 277 to 284).

scripts/cu.py:

- Line 1299: add 'focus' to the browser allowed set.
- Line 1341: add 'focus' to the browser element-action check
  (ref and selector mutually exclusive, non-empty strings).

scripts/dom_asserts.py:

- Add a 'focus' entry to ASSERTS: {'assert': 'focus_check',
  'mandatory': True, 'check': 'target is document.activeElement
  after the focus, before any keystroke'}. This mirrors the
  click entry (lines 48 to 50) and the fill entry (lines 63
  to 65).
- Add a send-requires-focus rule to require_asserts: a send key
  whose nearest preceding value action in the same batch is
  set_value (per _is_send_key, lines 96 to 114, which covers
  Enter after type, fill, or set_value) with no preceding focus
  action in the same batch raises DomAssertError. The scope is
  set_value-preceded sends only: fill, click, confirm_click,
  hover_click, and type are focus-establishing actions. Fill
  focuses internally through its click (scripts/cdp.mjs:536 to
  537), and a click establishes focus, so the rule must not
  reject the Brave fill program [fill, key Enter, assert] or the
  desktop focus_type chain [click, type, key Enter]
  (scripts/dom_act.py:708 to 712, gated at 748). This is the
  enforcement for section 2. Without it, a program could skip
  focus and fail silently.
- No change to the set_value entry (lines 66 to 68) or to the
  trailing-assert rule (a trailing assert action satisfies the
  sent_bubble requirement).
- No change to _api_dom_act is needed: it already passes
  available focus_check True (scripts/code_exec.py:936 to 938),
  with the comment that focus_check is available by
  construction.

scripts/s2_flip_live.py:

- Replace build_program_set_value (lines 129 to 161) with a
  landed builder emitting [set_value, focus, key Enter, assert
  bubble], 4 actions, P2 stamps on all 4. The trailing assert
  is the bubble assert used by build_program (lines 89 to 126),
  assert action at 117 to 121: selector BUBBLE_ASSERT_SELECTOR,
  text, timeout_ms 3000.
- Ordering constraint: the value read-back lives inside
  set_value (scripts/cdp.mjs:517 to 518, repeated at 528), so no
  separate value assert is needed before the Enter. A value
  assert AFTER the Enter would fail, because the composer is
  empty once the message is sent. Do not add one.
- Remove focus_enter (lines 497 to 519) and the LAPTOP_FOCUSENTER
  constant (line 76). The focus plus Enter step moves inside
  the program.
- Update send_browser CB-1 for the set_value variant (lines 568
  to 588: set_value branch 568 to 578, fill branch 579 to 585,
  verified set at 588): input_sent = completed >= 3 (set_value,
  focus, Enter all ran), target_received = completed >= 1
  (set_value read-back done), verified = V12 found. The old
  mapping used the helper result for input_sent and completed
  >= 1 for target_received.
- Keep the --chromium-set-value and --set-value flags (lines
  780 to 795) and variant_for (lines 189 to 195). What they
  select changes from the helper-based program to the landed
  program. Brave keeps fill; whether Brave also moves to (b1)
  is a coordinator decision, not part of this landing.
- Keep the pre-send count guard and the delayed count unchanged
  (sections 6 and 7).

tests/test_s2_flip_wiring.py:

- Replace test_set_value_program_carries_p2_stamps_and_passes_p5
  with a test for the landed 4-action program (4 scope stamps,
  4 observation_id stamps, require_asserts True with available
  focus_check True, type_check True, sent_bubble False).
  The old 2-action program shape is removed, not kept
  alongside, so there is exactly one (b1) program shape.
- Add a test that [set_value, key Enter, assert] without focus
  raises DomAssertError from require_asserts (the
  send-requires-focus rule).
- Keep test_chromium_set_value_splits_variants_per_browser
  unchanged: the split still selects the program per browser.

## 6. Preconditions: pre-send count guard (stays harness-side)

The guard runs in send_browser before the program
(scripts/s2_flip_live.py:539 to 543): count_check returns the
number of [data-message-item] bubbles already containing the
message; a count above 0 aborts the send with outcome
already-sent and no program runs. It uses /tmp/c5-count.mjs
(scripts/s2_flip_live.py:478 to 495), a laptop-only helper
whose behavior is documented in improvements/worker-click5-
input-fix-log.md, section 7.3 (read-only count of bubbles
containing a message).

This landing does NOT move the guard into cdp.mjs. There is no
count action type in cdp.mjs (whitelist at line 434), and
adding one is a separate design (a read-only action with its
own P5 treatment). The guard stays where it is, and the re-run
still depends on /tmp/c5-count.mjs existing on the laptop.
If that file is lost, it must be re-created from the log
description before the re-run. The guard's numbers in the
measured runs: pre-send count 0 in all 5 (b1) runs and all 5
reopen runs (verified from the run JSONs).

## 7. Post-verification: delayed count, V12, P9, CB-1

Delayed count stays in the harness. run() sleeps 10 seconds
after the scored wall stops and recounts the message for every
browser that used set_value (scripts/s2_flip_live.py:691 to
704). Exactly 1 means no late duplicate arrived. It uses the
same /tmp/c5-count.mjs helper as section 6, so the same
missing-file caveat applies. Measured: delayed count exactly 1
in all 5 (b1) runs and all 5 reopen runs (verified from the
run JSONs).

The remaining verification is unchanged by this landing:

- Independent V12: fresh DOM read over CDP, polls up to 10
  seconds for a [data-message-item] containing the message
  (scripts/s2_flip_live.py:316 to 338). V12 found attempt 1
  in all 10 reopen sends.
- P9 viewport capture after the scored wall, reviewed by a
  human before scoring (scripts/s2_flip_live.py:340 to 356).
  P9 PASS 10 of 10 in the reopen.
- CB-1 for the landed program: input_sent = completed >= 3,
  target_received = completed >= 1, verified = V12 found
  (section 5). The program's own trailing bubble assert is
  the in-program postcondition; V12 stays the independent
  check.

Known measurement artifact, not fixed by this landing: the
pre-send count-check SSH call appends no span, which
contributes to the 2750.1 ms median residual in the reopen
phase split (improvements/worker-click5-s2-reopen-log.md,
section 3, run table). Leave it as is; do not change the phase split
in the landing change.

## 8. Tests to write

Order: tests first, code after (section 9). Every test below
is written against the current code and must fail for the
right reason before the code lands.

Unit tests, tests/cdp_validation.mjs style (fake CDP, no
network, no browser; the file already extracts production
functions with vm):

- focus is rejected as 'unsupported action' before landing,
  accepted after. This is the failing-first anchor.
- focus resolves a ref through pageState, calls e.focus(),
  asserts document.activeElement === e, returns ok, and
  dispatches zero Input methods (record the calls; assert no
  dispatchMouseEvent and no dispatchKeyEvent).
- focus on a disabled or readOnly field throws 'field
  unavailable'.
- focus on a missing ref throws 'element missing; observe
  again' (pageState, scripts/cdp.mjs:157 to 167).
- focus with both ref and selector throws 'exactly one ref or
  selector required'.
- key Enter after focus still dispatches keyDown plus keyUp
  with text '\r' (regression guard on scripts/cdp.mjs:390
  to 412).
- set_value still does not focus: activeElement is unchanged
  after a set_value call. This locks in the current contract
  (section 1, item 1).

Wiring tests, tests/test_s2_flip_wiring.py:

- The landed program builder emits [set_value, focus, key
  Enter, assert bubble] with 4 scope stamps and 4
  observation_id stamps, and passes require_asserts with
  available focus_check True, type_check True, sent_bubble
  False (replaces the old 2-action test).
- [set_value, key Enter, assert] without focus raises
  DomAssertError from require_asserts.
- [fill, key Enter, assert] still passes require_asserts after
  the rule lands (the existing
  test_program_actions_satisfy_p5_requires in
  tests/test_s2_flip_wiring.py, which must not break: fill
  focuses internally, so the scoped rule must not reject it).
- The desktop focus_type chain [click, type, key Enter] still
  passes require_asserts (scripts/dom_act.py:708 to 712, gated
  at 748).
- test_chromium_set_value_splits_variants_per_browser still
  passes (Brave fill, Chromium set_value).
- The full wiring file still passes 12 of 12 after the swap
  (it is 12 of 12 today; improvements/worker-click5-s2-reopen-
  log.md, section 1).

Live dry run, scratch tabs, both browsers:

- Command: python3 scripts/s2_flip_live.py --run 0 --dry-run
  --chromium-set-value --message-prefix S2-LAND-DRY --workdir
  /tmp/s2-land-dry.
- Pass conditions: both browsers sent on scratch tabs;
  Chromium variant set_value, program ok True, completed 4,
  CB-1 all three True, V12 found attempt 1, pre_count 0,
  delayed_count 1; Brave unchanged (variant fill, program ok
  True, completed 3). The reopen dry run 0 is the baseline
  for comparison: PASS, wall 30123.9 ms, Chromium elapsed
  85.8 ms, completed 2 (improvements/worker-click5-s2-reopen-
  log.md, section 3). The landed dry run must match it except
  completed 4 instead of 2, and Chromium elapsed about 105 to
  115 ms instead of 85.8 ms: the landed 4-action program adds a
  focus step (measured 17 to 25 ms in the helper) and a key step
  (about 2 ms) to the 85.8 ms baseline.

## 9. Landing order

1. Write the failing tests (section 8, unit plus wiring).
   Commit tests only. Verify they fail for the right reason:
   focus rejected as 'unsupported action', and the landed
   program builder missing. Do not write code in this step.
2. Land the code (section 5). One commit, or one commit per
   file if the change is split for review; either way, tests
   and code must not land in the same commit, so the
   failing-first proof survives in history.
3. Run the tests on the VM: node tests/cdp_validation.mjs,
   python3 -m unittest tests.test_s2_flip_wiring -v, plus the
   full discover for the touched modules, naming the dom_act
   tests explicitly (tests/test_step5_p1p5.py and
   tests/test_dom_act.py): the rule change touches
   require_asserts, which dom_act.py also calls (line 748).
   All green required. Also grep the tree for LAPTOP_FOCUSENTER:
   it must return nothing in scripts/s2_flip_live.py after the
   change.
4. Sync the laptop tree to the landed todolist-push commit.
   Verify on the laptop that the tree carries the new code
   (grep the 'focus' entry in the cdp.mjs action whitelist).
   Record whether a relay restart was needed. The worker is
   spawned per code-exec session, so expect no restart, but
   verify with the dry run; do not assume.
5. Live dry run 0 on scratch tabs (section 8). PASS required
   before any live send.
6. Re-run 5 live runs with --chromium-set-value, same shape
   and timing rules as the reopen (runs 13:05 to 13:09,
   improvements/worker-click5-s2-reopen-log.md, section 3):
   avoid clone2-watch holds, record per run the routing gate
   (strict or relaxed), pre_count, delayed_count, program
   completed (must be 4 on Chromium), V12, CB-1. Write run
   JSONs to improvements/s2-flip-land-runs/run-1..5.json and
   P9 PNGs alongside. P9 reviewed before scoring.
7. Write the landing verification log. The reopen EXPAND
   recommendation stands only if the 5 re-runs match the
   reopen numbers: 10 of 10 sends, pre-send count 0,
   delayed count 1, model calls 0, median wall comparable
   to 28.6 s. If they do not match, the log says so and the
   recommendation is revised, not assumed.

## 10. What is still missing before it can land

Stated plainly. None of these is fixed by writing this spec.

1. The /tmp/c5-focusenter.mjs source is not in the repo. It
   lives only on the laptop. Its exact semantics must be
   recovered before the focus action is written. The
   reconstruction basis is improvements/worker-click5-input-
   fix-log.md, section 7.3 (Runtime.evaluate focus on
   textarea[aria-label="Message"], assert activeElement,
   dispatchKeyEvent keyDown plus keyUp Enter, return {ok,
   focus, enter}). If the laptop file is gone, the section 4
   pseudocode is the reconstruction, and it must be re-proven
   on a scratch tab before the live re-run.
2. The /tmp/c5-count.mjs source is also not in the repo, and
   this landing does not move it. Both the pre-send guard and
   the delayed count depend on it being present on the laptop
   (section 6 and 7). If it is lost, it must be re-created
   from the log description before the re-run.
3. The design decision is a recommendation, not a coordinator
   decision yet. Landing cannot start until the coordinator
   picks option A (standalone focus action) or option B
   (set_value focus field). If option B is picked, sections
   4, 5 and 8 must be rewritten for the field shape.
4. No tests exist yet for the focus action. Tests must be
   written first and must fail before the code lands
   (section 8 and 9, step 1).
5. No live proof of the landed code exists. All 10 of 10
   reopen sends and 5 of 5 (b1) sends ran through /tmp
   helpers, not through landed code. The only proof after
   landing is the dry run plus the 5 re-runs (section 9,
   steps 5 and 6).
6. The laptop tree is not synced to any landed commit yet,
   and it is unknown whether the relay needs a restart for
   a cdp.mjs change. Both must be verified on the laptop
   (section 9, step 4).
7. The 80-element snapshot cap (scripts/cdp.mjs:83 to 84,
   max_elements 1..80) still forces the relaxed routing gate
   on the Chromium live thread: all 5 reopen Chromium runs
   ran relaxed (truncated inventory, composer present). Raising
   the cap is a separate cdp.mjs change and is not part of
   this landing. The re-run must record the gate per run
   exactly as the reopen did.
8. The mouse stall itself is unsolved. (b1) bypasses it; it
   does not fix it. Any future class that genuinely needs
   synthetic mouse input on an occluded tab will hit the same
   wall, and that stays the step 9 prototype's first target
   (improvements/worker-click5-s2-reopen-log.md, section 6,
   caveat 2).
9. The coordinator has not decided whether Brave also moves
   to (b1) or keeps fill. This landing keeps Brave on fill
   (it sends 5 of 5 with fill in both the flip and the
   reopen). Uniformity is a separate decision.
10. The shadow-root activeElement walk from section 4 is
    still a follow-up, not part of this landing. The focus
    check is a direct equality check; if a future target lives
    in a shadow root, the check must walk shadowRoot.activeElement
    the way the harvest does (scripts/cdp.mjs:250 to 251).
    Section 4 calls it a follow-up; it is listed here so it is
    tracked.
11. The P9 evidence for the measurements the spec leans on is
    missing from the repo. The 10 reopen P9 PNGs (5 runs x 2
    browsers, promised in improvements/worker-click5-s2-reopen-
    log.md, section 8) and the 5 (b1) P9 PNGs are not on
    todolist-push. Section 7 asserts P9 PASS 10 of 10 in the
    reopen from the log's prose descriptions, but no reviewer
    can re-check the render from the repo. Either the PNGs land,
    or the landing records this gap as open.

## 11. Acceptance criteria for the landing

- All unit and wiring tests in section 8 pass on the VM.
- Live dry run 0 passes with the conditions in section 8
  (Chromium elapsed about 105 to 115 ms, completed 4).
- 5 live re-runs: 10 of 10 sends verified, pre-send count 0
  and delayed count 1 in every run, model calls 0, median
  wall comparable to the reopen 28.6 s.
- No /tmp helper call remains in the Chromium send path:
  grep for LAPTOP_FOCUSENTER in scripts/s2_flip_live.py
  returns nothing, and the Chromium program is the landed
  4-action program (completed 4, not 2).
- The landing verification log is written, and the reopen
  EXPAND recommendation is confirmed or revised from the
  re-run numbers, not assumed.

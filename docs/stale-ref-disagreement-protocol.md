# Stale-Ref Disagreement Protocol (P2, B5 lift limb (i))

Owner: Pham Tuan. Status: SPECIFICATION, step 7 preparation (COORD-CLICK-5,
worker C5-P2-SPEC). This document specifies B5 lift limb (i) in full: what
happens when a live rect re-read at execution disagrees with the plan.
It extends the step 2 contract (docs/layer0-cbexec-contract.md, commit
03ff589), section 4.4, which holds the protocol core and leaves this
document to supply the complete wording. It does not contradict the
contract. Where the two disagree, the FINAL direction (commit e05fc58)
wins and the disagreement is noted in place.

Sources, in authority order: the FINAL DIRECTION (e05fc58), section 1.2
P2 row, section 1.4 CB-2 row, section 2 items (d) and (f), section 5
B5; the step 2 contract (03ff589), sections 2.3, 2.6, 4.1-4.4, 7, 8;
FARCH's protocol core (improvements/worker-click3-farch-response-log.md,
section 2.3 item (b) and section 3.2 P2 row); FGROUND's reconciliation
adopted in final direction section 2 item (f). Code anchors are at
HEAD fccf367 on branch todolist-push unless a commit hash is named.

Rules honored in this file: no em dash (U+2014) or en dash (U+2013)
anywhere. No personal info. Coordinates appear only as an internal
adapter detail, never as the model's everyday input.

## 0. Verdict up front

B5 lift limb (i) is MET by this document. The protocol is specified
completely enough that the P2 element-ref interface rewrite can start
as soon as B5 limb (ii) is met (the defective proof tests for AMEND4
items 3, 4, 5-6 repaired or re-verified by the round-3 council; that
limb is a separate worker's job and still gates the start). The
remaining open items are listed in section 9, each with an owner.
None of them blocks starting the rewrite, because each carries a
specified default the implementer must use until its owner revises it
from measured data.

## 1. What a stale ref is

A ref is a handle to one UI element, bound to (snapshot ID, scope)
(contract section 1). The plan also records, per ref, the selector or
role-and-name it was grounded from, the plan-time rect (viewport CSS
px), and any distinguishing state the grounding recorded (field value,
text content, checked state). A ref is stale when the live state at
execution no longer agrees with what the plan recorded for it. The
causes are exactly these six, and the protocol names the cause in
every refusal:

1. **Snapshot expired or superseded.** The snapshot the ref is bound
   to is older than 120 seconds (OBSERVATION_MAX_AGE, code_exec.py:103
   and cu.py:78), or the driver no longer holds it, or the stored
   snapshot dict no longer equals the bound copy. A snapshot that has
   expired forces a re-ground, never a silent substitution (contract
   section 2.2).
2. **Scope change.** The live window or tab is no longer the window or
   tab named in the scope, or the observation ID no longer matches a
   snapshot the driver holds. The J40 class: a window-scope point
   used on a full-screen image, miss about (+45,+12) px, command
   still returned ok. That substitution path is deleted, not patched.
3. **Element moved.** The same element is at a different rect (layout
   shift, scroll, animation, resize, a send that shifted the layout).
4. **Element removed.** The selector resolves to zero elements on a
   fresh read.
5. **Element recreated or re-rendered.** The selector resolves to an
   element, but it is a different node than the plan grounded (a
   re-render replaced it). The plan-time rect may agree or disagree;
   rect agreement alone does not prove identity.
6. **Navigation or focus change.** The page navigated, a dialog opened
   or closed, a tab switched, or focus moved since grounding, so the
   plan's refs address a world that no longer exists.

A seventh condition, a moved window, is not a stale ref by itself but
invalidates the origin every ref depends on: the absolute viewport
origin is the Hyprland window origin plus mozInnerScreenX/Y (live C12
probe), so a window move changes the origin. AMEND4 items 5-6
(b44a5ea) refuse without window_bounds and re-read the live Hyprland
origin at ground time, refusing on mismatch. Under this protocol a
window move triggers a re-ground of all refs against the new origin,
and each ref then goes through the checks of section 2.

A ref is never "approximately right". Either every check in section 2
passes, or the action does not run on the plan-time rect.

## 2. Detection: the checks, in order, per action

The executor re-validates each ref immediately before acting on it,
on live state, not on the plan-time snapshot (FARCH core). The checks
run in this order, and the first failure decides the disposition in
section 3. No input is sent before all checks pass. The checks are
cheap structured reads (a DOM re-read costs about 0.030s); there is
no cost argument for skipping any of them.

1. **Binding.** The ref's snapshot ID is bound to this session, the
   snapshot dict equals the bound copy, and its age is at most 120s.
   This is the check code_exec.py already performs in
   _bound_dom_snapshot (code_exec.py:783-797): unbound id, mismatched
   snapshot, or age over 120s raises CodeExecError. The Zen path
   performs the same check against the observation the ref was
   grounded from (observation id, created timestamp, capture
   identity; cu.py:780-800 _valid_capture_identity). Failure reason
   codes: snapshot_expired, snapshot_unbound.
2. **Scope.** The live window or tab is the window or tab named in
   the scope, and that window or tab is the active one. Failure is a
   scope change, reason code scope_changed. The given-observation
   case is already enforced by the G28 loud refusal
   (first_action.py:452-498, loud_substitution_refusal; run() refuses
   before any session attempt). The planned-action case, actions
   planned on a window observation and executed after a screen
   observation arrived, is enforced by this check, which is the
   remaining new work of CB-2.
3. **Resolve.** The selector or role-and-name resolves against the
   live tree (document, open shadow roots, same-origin iframes, via
   the shared find() from AMEND4 item 2, zen_dom.py:227). Zero
   matches: element_missing. More than one match: element_ambiguous.
   A non-unique target is refused, never resolved by picking the
   first match (contract section 7).
4. **Visible.** The element is rendered, not hidden, not zero-size,
   and inside the viewport (or scrolled into it by the executor
   before the check). Failure reason code: not_visible.
5. **Interactive.** The element is enabled and can receive the input
   (not disabled, not aria-disabled, not inert, not covered by a
   modal that swallows events). Failure reason code:
   not_interactive.
6. **Rect agreement.** The live rect agrees with the plan-time rect
   within tolerance on every component (x, y, width, height).
   Tolerance default: 0.5 CSS px, adopted from STABLE_TOLERANCE_PX
   (zen_dom.py:885, landed in step 5, commit 76d0a56). The value
   absorbs sub-pixel rounding; anything larger is movement. The
   prototype may revise it from measured data; until then 0.5 CSS px
   is the specified value, and contract open item 2 stays open only
   for that revision. Failure reason code: rect_moved.
7. **Stability.** Two consecutive rect reads agree within the same
   0.5 CSS px tolerance. A moving element is not clicked at a stale
   rect; the executor waits for stability or re-grounds. This is
   the locate_confirmed pattern (zen_dom.py:876-945): the report and
   the second read describe one moment, and the caller decides the
   verdict. Failure reason code: unstable.
8. **Uncovered.** A hit test at the rect center returns the target
   element itself or a non-interactive descendant (hit_check,
   zen_dom.py:827-874). If the hit test returns a different element
   (an overlay, a toast, a sticky header, an interactive child),
   the locate fails. Failure reason code: covered.

Checks 4-8 are the CB-5 locate confirmations (contract section 7),
operationalized by ZenSession.locate_confirmed in step 5 and composed
by dom_act.confirm_locate (dom_act.py:55-130) on the Zen path. The
strict path refuses on any failed confirmation. The fallback path in
confirm_locate (a session without locate_confirmed, where
interactive and unique are unknowable) records them as None with
basis 'unprobed' instead of refusing; that fallback exists only for
older duck-typed sessions and test fakes, and P2 must not widen it:
a production session that cannot report interactive or unique does
not satisfy this protocol, and the P2 implementer must close that
gap or record it as a failing case, not ship the fallback as the
production behavior.

**Identity, stated honestly.** Node identity across a re-render is
not directly observable through the current locate API: locate()
returns a rect, not a node handle, and a recreated node can present
the same selector and the same rect. The protocol therefore defines
identity confirmation as the conjunction of checks 3-8 plus a
distinguishing-state match where the plan recorded one (field value,
text content, checked state, as read back by verify_typed or the
equivalent read). A node that passes every check, including the
distinguishing-state match, is treated as the same element for
action purposes. The residual risk, a different node with an
identical selector, rect, and recorded state, is accepted and
logged with the action, and it is exactly why section 4 sends
destructive and message-sending actions down the strict path, where
no such acceptance is allowed.

**Re-ground bound.** At most one re-ground per action per check
sequence. A second disagreement on the same action is a refusal,
not a loop. Re-grounding reads a fresh snapshot (a fresh locate, or
a fresh dom_observe), never reuses the plan-time rect, and the
action's binding is updated to the new snapshot ID. The remaining
actions' refs are not silently rebound to the new snapshot; they
are invalidated per section 5.

## 3. Disposition: what happens on disagreement, per case

| Case | Disposition |
|---|---|
| Rect moved, identity confirmed (checks 3-8 pass on the fresh read, distinguishing state matches where recorded), stable on re-read | Re-ground once and act once on the fresh rect. This is one action, not a retry (contract section 2.6). The result records that a re-ground happened, with both rects. |
| Rect moved, identity unconfirmed (element replaced, re-rendered, or the selector now matches a different node; distinguishing state differs) | Refuse the action, stop the batch, report both rects. Reason code: identity_unconfirmed. |
| Element missing on the fresh read (zero matches after one re-ground from a fresh snapshot) | Refuse the action, stop the batch. Reason code: element_missing. No second re-ground. |
| Ambiguous (more than one match after re-grounding) | Stop the batch. Never pick the first match. Report the match count and the distinguishing features of the matches, so the model can disambiguate on a fresh snapshot. Reason code: element_ambiguous. |
| Scope changed, re-grounding resolves it unambiguously (same window or tab still live, target found under the new scope, checks 3-8 pass) | Re-ground first and continue. This is the CB-2 decided rule: scope plus observation ID is mandatory in action data; a scope change triggers re-grounding first; stop only on ambiguity (final direction section 1.4 CB-2 row, section 2 item (f)). The result records the scope change and the re-ground. |
| Scope changed and re-grounding cannot resolve it (window or tab gone, target absent under the new scope, ambiguity) | Stop the batch. Reason code: scope_changed_unresolved. No input is sent on the new scope. |
| Navigation or focus change since grounding | Re-plan from a fresh snapshot. The plan's remaining refs are discarded, not re-used against the new page. Reason code: navigation. |
| Unstable (rect reads keep disagreeing) or covered (hit test returns another element) | Refuse the action, stop the batch. Reason codes: unstable, covered. A moving element that does not settle within the prototype's bound is refused and reported, not waited on indefinitely. |
| Snapshot expired or unbound | Re-ground from a fresh snapshot and rebind; if the fresh snapshot cannot be taken, refuse and stop. Reason codes: snapshot_expired, snapshot_unbound. Never substitute a fresh full-screen capture while passing the action list through unchanged. |
| Window moved (live Hyprland origin differs from the grounding origin) | Re-ground all refs against the new origin, then run each ref through section 2. A ref that then disagrees takes its row in this table. Reason code on refusal of the origin itself: window_moved. |

The blanket stop is REJECTED (final direction section 1.4 CB-2 row):
a scope change or a moved rect does not stop the batch when
re-grounding resolves it unambiguously, because a DOM re-read costs
about 0.030s and re-ground-and-continue is strictly better than
stopping, on both accuracy and speed. The stop applies only on
ambiguity or on a change re-grounding cannot resolve.

## 4. Strict path: destructive and message-sending actions

FARCH core, adopted verbatim: never click a stale point on a
destructive or message-sending action. For any action that can send
a message, submit a form, delete data, or move money, ANY
disagreement in section 2, even a rect move with identity confirmed,
takes the strict path: the batch stops, no input is sent, and the
action returns for re-plan on a fresh snapshot. Re-grounding may
supply the fresh snapshot for the re-plan, but the action does not
execute inside the old batch on a re-grounded rect. The model
re-confirms the target on the fresh snapshot and issues a new
action. This is the one place where re-ground-and-continue does not
apply, and the reason is the retry rule (contract section 2.6):
a possibly-sent action that did not verify is a stop, not a retry,
and a destructive action executed on a re-grounded rect inside a
batch that already disagreed once is a guess about what was sent.

## 5. Multi-action plan lifecycle

A disagreement on step N invalidates the refs of steps after N. The
executor does not continue step N+1 on refs grounded before the
disagreement; it re-grounds the remainder from a fresh snapshot or
stops (contract section 4.4). After a step that can change the page
or focus (navigation, form submit, dialog open or close, tab
switch), the executor re-validates the next step's preconditions
from live state before acting (contract section 8). The existing
mechanism for this is GroundPoints (dom_act.py:334-397): each []
access re-reads the live rect and, when the element moved since
grounding, re-grounds that selector before returning it; a re-ground
that fails raises DomActError instead of returning a stale point.
Two constraints on that mechanism under this protocol: first, .get()
and other dict methods bypass the guard (they read the stored table
directly), so callers must use [] access for the point they click,
and P2 must remove or guard any .get() path that can reach a click;
second, GroundPoints re-grounds on move silently, which is correct
only for the re-ground-and-continue rows of section 3, never for
the strict-path actions of section 4, where a move must stop the
batch instead. The P2 implementer wires that distinction into the
access path, not into a comment.

## 6. CB-2 binding, folded in

Scope plus observation ID is mandatory in action data (final
direction section 1.4 CB-2 row, as modified: blanket stop REJECTED).
Concretely, for the P2 interface:

- Every action carries `scope` (the specific window or tab, the
  image or DOM frame) and `observation_id` (the snapshot ID the
  target was grounded from). An action missing either field is
  refused at plan validation, before execution starts (contract
  section 2). The refusal names the missing field.
- Every ref carries its binding (snapshot ID, scope) with it, and
  the binding is checked at execution time against live state,
  before the input is sent (contract section 4.1). A ref whose
  snapshot has expired, whose scope no longer matches the live
  window or tab, or whose target no longer resolves under section
  7 of the contract is not executed on a guess.
- A scope change mid-batch halts the batch unless section 3
  resolves it by re-grounding (contract section 4.2, as decided in
  final direction section 2 item (f)). No silent substitution,
  ever: a window-scope point is never used on a full-screen image,
  and a missing, stale, or too-old observation is never replaced
  by a fresh full-screen capture while the action list is passed
  through unchanged.
- The G28 loud refusal stays for the given-observation case
  (first_action.py:452-498): a batch given a rejected observation
  is refused loudly, before any session attempt and before any
  action runs, naming the given observation, its age, and why it
  was rejected, for every batch including pointer-only batches.
- Snapshot expiry is 120 seconds on both paths (code_exec.py:103
  OBSERVATION_MAX_AGE; cu.py:78 OBSERVATION_MAX_AGE). The D6
  scoped rule applies: for DOM-grounded work, re-read the DOM
  instead of refusing for staleness; the future-clock refusal
  stays (cu.py:793, observation older than 120s or from a future
  clock); the 120s window stays as a gate for pixel-addressed
  work, where staleness is real.
- The after-capture follows the both-fields shape (AMEND4 item 12,
  cbab398): `after` is scope-matching and chainable, `after_screen`
  is the full monitor, verification only, documented non-chainable.
  The after-image is evidence, not a grounding source for the next
  key or type step, unless it is the scope-matching `after` field.

## 7. Fail closed: exact behavior when a ref cannot be re-grounded

When a ref cannot be re-grounded (missing, ambiguous, identity
unconfirmed, scope unresolvable, snapshot unobtainable), the
executor fails closed. No input is sent for that action, no later
action in the batch runs, and the result carries the CB-1
three-part contract plus a structured error. Exact shape:

```json
{
  "input_sent": false,
  "target_received": false,
  "verified": false,
  "verified_basis": "stale-ref: <reason code>",
  "ok": false,
  "error": {
    "code": "stale_ref",
    "reason": "<reason code>",
    "selector": "<selector or ref>",
    "snapshot_id": "<plan snapshot id>",
    "scope": "<scope>",
    "plan_rect": {"x": 0, "y": 0, "width": 0, "height": 0},
    "live_rect": {"x": 0, "y": 0, "width": 0, "height": 0},
    "action_index": 0,
    "batch_stopped": true
  }
}
```

Reason codes, exactly: snapshot_expired, snapshot_unbound,
scope_changed, scope_changed_unresolved, element_missing,
element_ambiguous, identity_unconfirmed, rect_moved_unconfirmed,
unstable, covered, not_visible, not_interactive, navigation,
window_moved. `live_rect` is null when the element is missing.
`plan_rect` is null when the plan recorded no rect (a role-and-name
target grounded without a stored rect, which P2 must not produce
for a ref that will be re-validated; a ref without a plan rect
cannot take the re-ground-and-continue row for a move, because
there is nothing to compare, so it takes the refuse row instead).

Envelope mapping, per caller: first_action reports
error_code 'stale_ref', path 'refused', ok false, and exit code 1
with the error object on the envelope; code-exec raises
CodeExecError with the message starting 'stale_ref: <reason code>',
so the supervisor can match on the prefix, and the partial result
envelope carries the same error object. The batch log records the
disagreement with both rects, the snapshot IDs (plan and fresh),
and the check that failed, so a later reader can tell whether the
ref moved, vanished, or was replaced.

## 8. Scope-refusal reframe: what it means for the P2 interface

The scope refusal is reframed as snapshot binding, not deleted
(final direction section 2 item (f), adopting FGROUND's
reconciliation). Concretely for the P2 interface: the old legality
refusal, refusing to act on a correctly-addressed action because
the observation's scope is screen, is deleted with P2, but the
check it performed does not vanish, it changes form into the
binding on every ref, so an action that arrives without a scope and
an observation ID is malformed and is refused at plan validation,
an action whose scope no longer matches live state halts the batch
unless re-grounding resolves it unambiguously, and a scope change
the executor cannot resolve stops the batch with the structured
stale_ref error of section 7; the interface consequence is that
scope moves from being a gate the caller trips over into being
data the ref carries, checked at execution time, which means P2
must add scope and observation_id as mandatory fields on every
action and every ref, must check them in the executor before any
input is sent, and must never again refuse a good action for the
scope its observation happened to be captured in, while still
refusing every action whose world has actually changed.

## 9. B5 limb (i) judgment and open items

Judgment: B5 limb (i) is MET. This document specifies the stale-ref
disagreement protocol completely enough that the P2 rewrite can
start: what a stale ref is (section 1), the detection checks in
order (section 2), the disposition per case with the blanket stop
rejected and re-ground-first adopted (section 3), the strict path
for destructive and message-sending actions (section 4), the
multi-action lifecycle (section 5), the CB-2 binding folded in
(section 6), and the exact fail-closed error shape (section 7).
The P2 rewrite still must not start until B5 limb (ii) is met
(defective proof tests for AMEND4 items 3, 4, 5-6 repaired or
re-verified); limb (i) being met does not lift B5 by itself.

Open items, each with an owner, not silent gaps:

- OPEN-1, rect-agreement tolerance value: default 0.5 CSS px is
  specified in section 2 check 6, adopted from STABLE_TOLERANCE_PX
  (zen_dom.py:885). The prototype may revise it from measured data.
  Owner: the P2 implementer, via the prototype. This does not block
  starting, because the default is specified.
- OPEN-2, stability interval: the two stability reads are two
  consecutive evaluate calls with no artificial delay, as
  locate_confirmed does today. If the prototype measures that
  back-to-back reads miss real movement (for example animation
  frames), it sets a minimum interval from measured data. Owner:
  the P2 implementer, via the prototype.
- OPEN-3, distinguishing-state coverage: which state each action
  kind records for identity confirmation (field value, text,
  checked state) is defined per action type by the P2 implementer
  as the interface lands; an action kind with no recorded state
  takes the refuse row on a move it cannot confirm. Owner: the P2
  implementer.
- OPEN-4, B5 limb (ii): defective proof tests for AMEND4 items 3,
  4, 5-6 repaired or re-verified. Owner: the round-3 council
  (separate worker, commissioned in final direction section 6
  worker 3). Gates the P2 rewrite start.
- OPEN-5, Zen adapter missing work: the code-exec DOM backend is
  Chromium-only (see the spec log, section 5). The Zen backend
  under the same contract does not exist yet. Owner: the P2
  implementation worker (step 7) with the step-9 prototype worker.
  This does not block writing the protocol, but P2 cannot prove
  the Zen path until the adapter exists.
- OPEN-6, shadow-DOM fallback shape: decided by the P3 experiment
  outcome. If the Messenger composer sits in shadow DOM and CDP
  returns null box_model for it, P3 narrows to "CDP works except
  shadow-DOM elements" and P2 carries a shadow-DOM fallback.
  Owner: the P3 re-run worker.

## 10. What P2 must change (implementer checklist)

1. Add `scope` and `observation_id` as mandatory fields on every
   action and every ref; refuse at plan validation when missing
   (section 6). Touch: scripts/code_exec.py (program validation),
   scripts/dom_act.py (action shape), scripts/cu.py
   (CodeExecBackend.act, CLI act).
2. Replace the live-path use of fastpath.dom_rect_to_image_point
   (the exact-rect to lossy-image-point round trip) with
   fastpath.dom_rect_to_screen_point at the driver edge, one
   conversion, per A9. Live call sites today (enumerated in the
   spec log, section 4): dom_act.py:271 ground_input (live),
   dom_act.py:441 ground_many_one_shot (reachable only through
   ground_many, test-only today), zen_dom.py:821 locate_point (no
   live callers, test-only). Keep dom_rect_to_image_point for tests
   and legacy, deleted from the live path only.
3. Implement the section 2 checks in the executor, in order, per
   action, immediately before acting, reusing locate_confirmed
   and confirm_locate where they exist and closing the
   confirm_locate fallback path for production sessions.
4. Implement the section 3 disposition table, including the
   one-re-ground bound and the strict path of section 4 for
   destructive and message-sending actions.
5. Implement the section 5 lifecycle: invalidation of later refs
   on a step-N disagreement, []-only access on GroundPoints, and
   re-validation after page or focus-changing steps.
6. Emit the section 7 error shape on every fail-closed refusal,
   with the reason code, both rects, and both snapshot IDs; map it
   onto the first_action envelope and the code-exec error prefix.
7. Build the Zen adapter under the same contract (OPEN-5): a Zen
   backend for code_exec's dom_start, dom_tabs, dom_observe, and
   dom_act, with snapshot binding, one-session ownership, and the
   same three-part result. The Zen grounding pieces exist in
   zen_dom.py and dom_act.py; the adapter that exposes them to
   code_exec does not.
8. Delete the legality refusal with P2 and land the snapshot
   binding in its place (section 8). Do not delete the halt on
   scope change, the G28 loud refusal, or the future-clock refusal.

## 11. Evidence log

- 2026-11-22 10:42 +07 (T+0m): task received. Repo
  ~/workspace/computer-use-wayland, branch todolist-push, HEAD
  fccf367. Start of this worker's wall clock.
- 10:42-10:45 (T+0-3m): read the FINAL direction
  (improvements/worker-click3-final-direction-log.md, commit
  e05fc58) in full, sections 1.2 P2, 1.4 CB-2, 2 (d) and (f), 5
  B5, 6 worker 10, 7; the step 2 contract
  (docs/layer0-cbexec-contract.md, commit 03ff589) in full, in
  particular sections 2.3, 2.6, 4.1-4.4, 7, 8; FARCH's protocol
  core (improvements/worker-click3-farch-response-log.md,
  section 2.3 item (b), section 3.2 P2 row).
- 10:43-10:46 (T+1-4m): read the AMEND4 landing diffs c1ea773
  (item 2), 62b740e (item 3), 72120aa (item 4) and verified the
  wiring at tip fccf367 with grep (file and line citations in
  the spec log). Ran the wiring test files at tip:
  `cd tests && python3 -m unittest test_zen_dom test_dom_act
  test_type_verification` (Ran 122, OK); `python3 -m unittest
  test_step5_p1p5 test_pick4_fastpath` (Ran 65, OK);
  `python3 -m unittest test_first_action` (Ran 71, OK).
- 10:46 onward (T+4m): wrote this document and the spec log
  (improvements/worker-click5-p2-spec-log.md), then committed
  both on todolist-push with an explicit pathspec and verified
  the push with git ls-remote. Commit hash and push proof are
  in the spec log, section 8.

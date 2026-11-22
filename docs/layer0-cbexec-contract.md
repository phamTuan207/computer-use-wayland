# Layer 0 + CB-EXEC Merged Contract

Owner: the owner. Status: DESIGN DOCUMENT, step 2 of the FINAL DIRECTION
(commit e05fc58). This contract is written early; proof stays late, at the
prototype step (step 9). Nothing in this document authorizes building the
full executor, deleting any existing path, or flipping any flag. It is the
spec the step-9 prototype must prove against, and the spec that stops P2,
S1, and P5 from inventing three ad-hoc interfaces.

Sources, in authority order: the FINAL DIRECTION (e05fc58); the joint
adjudication DRAFT (9d23834); CODEX-BREAKTHROUGH section 3 (2596287);
ARCH-REVIEW (074c1d7). Where this contract and a source disagree, the
FINAL DIRECTION wins and the disagreement is noted in place.

Rules honored in this file: no em dash (U+2014) or en dash (U+2013)
anywhere. No personal info. Coordinates appear only as an internal
adapter detail, never as the model's everyday input.

## 0. What is being built, in one paragraph

One build, not two. ARCH Layer 0 (a persistent driver daemon on the
laptop: snapshot, execute, verify, structured-first) and the
CODEX-BREAKTHROUGH semantic transaction executor (semantic targets,
preconditions, real input, postconditions, retry only when surely
unsent) are the same destination approached from two sides, merged with
S3 (the laptop-side task runner) into a single system under a single
contract. The model decides targets and hard branches. The executor
does the stable steps: locate, fill, wait for readiness, re-read fields,
verify results. Screenshots are the fallback perception path, not the
primary one. The contract below is binding on every backend, every
adapter, and every caller, including act-now, code-exec, and the
session driver.

## 1. Definitions

- **Snapshot**: one structured read of the world at one moment: DOM
  plus accessibility tree plus window list, taken through the driver in
  a single call. A snapshot has an ID and a scope, and both travel with
  every ref taken from it.
- **Scope**: the exact frame an observation or action addresses: a
  specific window or tab, an image or DOM frame, and the observation ID
  it came from. Scope is data, not context. An action without a scope
  is malformed and is refused before anything runs.
- **Target ref**: a handle to one UI element, bound to (snapshot ID,
  scope). A ref is not a coordinate. Coordinates are produced inside
  the pointer adapter at execution time, from a fresh locate, and are
  never stored in the plan.
- **Plan**: a list of actions, each in the shape of section 2, with
  refs, not pixels.
- **Postcondition**: a checkable statement about state after an action
  (section 2.5). A postcondition is checked by the executor on the
  laptop, by structured read where one exists, never by envelope ok.
- **Verified action**: an action whose postcondition passed. The
  program maximizes VERIFIED actions per model call, not actions per
  observation (section 8).

## 2. Action shape

Every action in a plan carries all six fields. An action missing any
field is refused at plan validation, before execution starts.

### 2.1 Semantic target

The target is named by meaning, in exactly one of these forms:

- **Role and name**: the element's role plus its accessible name, for
  example role "textbox", name "Message". The executor resolves it
  against the live DOM or accessibility tree at execution time.
- **Selector or ref read from a fresh snapshot**: a CSS selector, or a
  target ref bound to (snapshot ID, scope) under section 4. A selector
  must resolve to exactly one element after the locate confirmations
  of section 7; a selector matching zero or more than one element is
  refused, never clicked at the first match.

Generic x/y is NOT an accepted target form. Coordinates stay an
internal detail of the pointer adapter (section 9).

### 2.2 Scope

The action names its scope explicitly: the specific window or tab, the
image or DOM frame, and the observation ID the target was grounded
from. Scope is mandatory in action data (CB-2, as modified by the
FINAL DIRECTION). The executor checks scope before acting:

- The target's window or tab must be the live, focused window or tab
  named in the scope.
- The observation ID must match a snapshot the driver still holds; a
  snapshot that has expired or been superseded forces a re-ground, not
  a silent substitution.

### 2.3 Preconditions

Before acting, the executor confirms all of these, on the live state,
not on the plan-time snapshot:

- **Unique**: the target resolves to exactly one element (section 7).
- **Visible**: the element is rendered and not hidden.
- **Enabled**: the element is interactive (not disabled, not inert).
- **Right window**: the element is in the window or tab named in the
  scope, and that window or tab is the active one.
- **Geometry unchanged**: the element's rect, read live, agrees with
  the rect the plan was grounded on, within the tolerance the
  prototype proves (a moved element is re-grounded, not clicked stale;
  see section 2.6).
- **Focus unchanged**: focus is where the plan expects it to be (the
  right window, the right field) since grounding.

If any precondition fails, the action does not run. The executor
re-grounds once where re-grounding can resolve the failure (section
2.6); otherwise it stops the batch at the first failure (section 8)
and reports which precondition failed, with the live state that
disproved it.

### 2.4 Input

The executor delivers input in exactly one of these forms, chosen by
the router (section 5) and recorded in the result:

- **Real mouse**: the physical pointer path, real Pointer movement and
  click at DOM-located coordinates. This is the DEFAULT for clicks and
  hovers. Real input is required wherever a trusted event, hover
  state, or native behavior is needed (the Browse-button case: DOM
  locate, then real mouse).
- **Real keyboard**: real key events and typed text, for key and type
  actions. Typing goes through the real keyboard path, not through a
  DOM value set, unless the DOM fill equivalence for that control type
  is proven (section 5.4).
- **API or DOM action confirmed suitable for the control**: a DOM or
  API action (fill, select, DOM click) is allowed ONLY where its
  equivalence to real input is proven for that control type. An
  unproven DOM action is never substituted for real input on the
  grounds that it is faster.

The input form used is part of the result record, so a later reader can
tell whether a click was real mouse or DOM, and can judge the result
accordingly.

### 2.5 Postcondition

Every action names its postcondition in the plan. Examples, by action
kind:

- Dialog closed (the dialog element is absent from the live tree).
- URL changed (the live URL differs from the pre-action URL in the
  expected way).
- Field has value (a DOM read-back of the field equals the typed
  value; the pixel band is not a postcondition for structured targets).
- Checked state changed (the live checked or selected state flipped).
- New text appeared (the expected text is present in the live DOM).

The postcondition is checked by the executor on the laptop, by
structured read where one exists, immediately after the input is sent
and after the settle the action type requires. The check result is
reported per action, not per batch. An action with no postcondition is
refused at plan validation, except for actions on the per-action
exception list (section 2.7).

### 2.6 Retry policy

- **Retry only when the executor knows surely the input was not
  sent.** "Surely unsent" means the executor has positive evidence the
  input never reached the target: the pointer never moved, the key
  event was never dispatched, the session was never handed the action.
  Absence of a postcondition is NOT evidence of unsent input; it is
  evidence of an unknown outcome.
- **Before replaying any action that could send or delete data, the
  executor checks state first.** If the postcondition already holds
  (the message is already in the thread DOM, the form is already
  submitted, the item is already deleted), the action is marked
  already-done, not replayed. A retry that could double-send a form, a
  message, or a payment is never issued on a guess.
- **Default on uncertainty: do not retry; stop and report.** A
  possibly-sent action that did not verify is a stop, not a retry.
  Recovery is a model decision on fresh state, never an automatic
  replay. The prototype must prove this rule on a destructive-action
  test: no double-send on retry (B6 lift condition, section 11).
- **Re-grounding is not retrying.** When a live rect re-read
  disagrees with the plan (the stale-ref case), the executor follows
  the stale-ref disagreement protocol: refuse, re-plan, or re-ground
  and continue, per case (section 4.3). Re-grounding and then acting
  once on the fresh ground is one action, not a retry.

### 2.7 Per-action exception list

Some actions have no cheap postcondition: scroll position, hover
state, focus-only moves. For these, and only these, the contract
requires an explicit per-action exception list, named in the plan and
landed by the P5 implementer per action type as its assert set lands.
An action on the exception list reports its result as input_sent with
verified=false and the reason named (no postcondition exists for this
action type), never as verified=true. The band check, where it is kept
for these actions, is a diagnostic, not a postcondition. Any action
type NOT on the exception list that lacks a postcondition is refused
at plan validation.

## 3. Result contract

Every action returns a three-part result. The three parts are
independent facts, and no part implies another:

1. **input_sent**: the input was dispatched (pointer moved and clicked,
   key events sent, DOM action invoked). This is what the old
   desktop_act `ok` becomes. input_sent=true says nothing about the
   target or the outcome.
2. **target_received**: the right target received the input. Proven by
   a live read: focus is on the named element, the element's state
   changed in the expected direction, or the event landed on the
   element the plan named. A click into empty space at the right
   coordinates returns input_sent=true and target_received=false.
3. **verified**: the postcondition passed on a live structured read.
   verified=true ONLY with a postcondition (CB-1). There is no
   verified=true without a named postcondition that passed. An action
   on the exception list (section 2.7) reports verified=false with the
   reason named.

Envelope rules, binding on every caller:

- The batch envelope never reports ok=true from a session exit code or
  from input_sent alone. The old propagation (session ok into envelope
  ok) is removed in the same commit that lands this contract's result
  shape, so no caller can misread it downstream.
- The 167/199 ok=true rate from the act-now JSONL aggregate is NOT a
  success rate and must never be quoted as one: it carries no
  postcondition data anywhere in the log, and G30 proves false ok
  exists in that exact population.
- The live run log carries the three-part result per action. The
  acceptance ladder scores by the third part (verified) and by DOM
  outcome, never by input_sent.

## 4. Scope binding

### 4.1 The binding rule

Each target ref binds to (snapshot ID, scope). The binding is checked
at execution time, against live state, before the input is sent. A ref
whose snapshot has expired, whose scope no longer matches the live
window or tab, or whose target no longer resolves under section 7 is
not executed on a guess.

### 4.2 Scope change halts the batch, never silently substitutes

- **A scope change mid-batch halts the batch.** The executor stops at
  the first action whose scope no longer matches, reports the change,
  and does not continue the remaining actions on the new scope.
- **No silent substitution, ever.** A window-scope point is never used
  on a full-screen image. A missing, stale, or too-old observation is
  never replaced by a fresh full-screen capture while the action list
  is passed through unchanged, with no frame conversion and no stop.
  That substitution path (the J40 class: window-scope point used on a
  full-screen image, miss about (+45,+12) px, command still returned
  ok) is deleted, not patched.
- **The G28 loud refusal stays.** A batch given a rejected observation
  is refused loudly, before any session attempt and before any action
  runs, naming the given observation, its age, and why it was
  rejected, for EVERY batch including pointer-only batches. The
  refusal names the cause; it never silently repairs the input.

### 4.3 Re-ground first, stop on ambiguity (the decided rule)

The FINAL DIRECTION decides the scope question as a reconciliation,
not as a blanket stop (section 2 item (f)):

- **DELETE with P2 the legality refusal**: the refusal to act on a
  correctly-addressed action because the OBSERVATION's scope is screen.
  That is a legality gate on a good action, and it goes.
- **KEEP the halt on a scope CHANGE mid-batch**, enforced by the G28
  loud refusal for the given-observation case and by CB-2 binding for
  the planned-action case. That is a halt on a changed world, and it
  stays.
- **Re-ground first**: when a scope change or a stale ref can be
  resolved by re-grounding (a DOM re-read costs about 0.030s), the
  executor re-grounds and continues, but ONLY when the target is
  unambiguous after re-grounding. Re-ground-and-continue is strictly
  better than stopping, on both accuracy and speed, when the target is
  unambiguous.
- **Stop on ambiguity**: if re-grounding finds zero targets, more than
  one target, or a target whose identity cannot be confirmed, the batch
  stops. Ambiguity is never resolved by picking the first match.

### 4.4 Stale-ref disagreement protocol (B5 lift condition, part i)

When a live rect re-read at execution disagrees with the plan-time
rect, the executor decides by case, in this order:

- **Rect moved but target identity confirmed** (same element, new
  position, stable on re-read): re-ground and act once on the fresh
  rect. This is the moving-element case (section 7).
- **Rect disagrees and identity unconfirmed** (element replaced,
  re-rendered, or the selector now matches a different node): refuse
  the action, stop the batch, report the disagreement with both rects.
- **Rect disagrees after a navigation or focus change**: re-plan from
  a fresh snapshot. The plan's remaining refs are discarded, not
  re-used against the new page.
- **Multi-action plan lifecycle**: a disagreement on step N invalidates
  the refs of steps after N. The executor does not continue step N+1
  on refs grounded before the disagreement; it re-grounds the
  remainder from a fresh snapshot or stops.

OPEN: the numeric tolerance for "rect agrees" (how many pixels of drift
are agreement, how many are a move) is set by the prototype from
measured data, not fixed here. The P2 implementer owns the protocol's
final wording; this section is the protocol core (FARCH) it must
implement.

### 4.5 After-capture scope

The after-image follows the both-fields shape (AMEND4 item 12,
cbab398, already landed): `after` is scope-matching and chainable;
`after_screen` is the full monitor, verification only, documented
non-chainable. The screen-scope after-capture as produced today (the
envelope after-image always captured with observe_screen, overwriting
the scope-matching after-capture) is removed and never shipped again.
The scope check moves before the overlay attempt. The after-image is
evidence, not a grounding source for the next key or type step, unless
it is the scope-matching `after` field.

## 5. Backends under one contract

One contract, several backends. The router (P1) picks the backend per
target, in code, not by convention. Every backend answers the same
action shape (section 2) and returns the same three-part result
(section 3). A backend that cannot answer the shape is not used for
that target; the router falls through to the next backend.

### 5.1 Router (P1)

- The router is one function returning the perception source per
  target. It is encoded in code, not in convention or in a prompt.
- The router routes on COVERAGE, not just on target type: a backend
  returning an empty harvest, or a truncated accessibility tree
  (section 5.3), falls through to the next backend. The router never
  proceeds on a partial inventory.
- The router fails closed to the labeled screenshot fallback: when no
  structured backend covers the target, the fallback is used and
  labeled as fallback in the log and in the result.
- The router logs one line per routing decision, so drift back to
  screenshots is visible instead of silent.
- The router's order is: DOM or BiDi for web pages, AT-SPI for desktop
  controls, screenshot crop for canvas, image content, or unexposed
  controls, vision as fallback. Zen chrome UI routes to screenshots,
  a DECIDED boundary (P8 CLOSED: Marionette chrome context BLOCKED,
  HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required). That boundary is
  recorded in the router, not rediscovered per task.

### 5.2 DOM and BiDi (web pages)

- Chromium via CDP, Zen via Marionette and BiDi, under the same
  contract. The Zen adapter is genuinely missing work (code-exec DOM
  is Chromium-only, DOM_WINDOW_CLASS chromium); building it is part of
  the merged prototype, not a separate track.
- Locate is semantic (role and name, selector, or ref), confirmed per
  section 7. A rect is exact; a rect is not a proof of the right
  target, and the locate confirmations decide that.
- Shadow DOM: CDP returns a null box_model for shadow-DOM elements.
  Where a target sits in shadow DOM and the backend cannot return a
  rect, the router records the gap and falls through to the next
  backend. The P3 experiment's shadow-DOM outcome decides whether the
  clone-chat class carries a shadow-DOM fallback; the contract does not
  assume it away.

### 5.3 AT-SPI (desktop controls)

- The accessibility tree is partial by design: the harvest caps at 500
  nodes or 2 seconds and returns at most 80 items, with a truncated
  flag. The backend MUST report coverage: the truncated flag, the node
  count, and the time cap are part of every AT-SPI result.
- A truncated tree is not a complete inventory. When the tree is
  truncated and the target is not found in it, the router falls through
  to DOM or image, never reports "target absent" on a partial tree.
- AT-SPI cannot see Zen. That is a recorded coverage limit, not a bug
  to work around per task. AT-SPI numbers on this machine are
  otherwise unverified; the prototype measures them.

### 5.4 Input equivalence (real input default)

- Real Pointer and keyboard input is the DEFAULT at DOM-located
  coordinates. DOM .click() is used ONLY where equivalence is proven
  per control type. "Proven" means a named test on that control type
  showing the DOM action produces the same application effect as real
  input, including focus, events, and validation. An unproven DOM
  action is not used because it is faster.
- DOM fill is allowed where its equivalence for that control type is
  proven. Where it is not proven, typing goes through the real
  keyboard. DOM fill that does not trigger the same validation or
  events as typing is a false action, not a faster one.
- BiDi pointer click has failed in past probes and Marionette clicks
  are not equivalent to real mouse input; the prototype does not assume
  either works, it proves per control type.

### 5.5 Screenshot crop and vision fallback

- Screenshot crop is the backend for canvas, image content, and
  controls no structured backend exposes. It is a first-class backend
  under the same contract, not an escape hatch: the crop carries a
  scope, the target is confirmed by the same locate rules where they
  apply, and the result is still three-part.
- Vision is the fallback, used only when structured data cannot resolve
  the target. Vision fallback uses PNG or a lossless crop for the
  vision read, and the lowest structured resolution the task allows.
  The image the model sees is uniform across paths: ONE max_width for
  all captures (CB-3 uniformity), pinned and logged with every
  measurement (P6c). The old split (observe default 960, act-now
  1920, JPEG q90) is removed.
- The J37 codec false refusal is fixed separately: the preflight must
  not compare a decoded JPEG against a fresh uncompressed capture with
  a patch threshold that a codec artifact can trip. A codec artifact
  is not a screen change.

### 5.6 Zen adapter and the one remote-session owner

- The Zen adapter (Marionette and BiDi) sits under the same contract
  as Chromium and AT-SPI: same action shape, same locate
  confirmations, same three-part result.
- **One remote-session owner for Zen.** Firefox allows exactly one
  remote session per instance (proven in 4 runs). One owner holds the
  pointer, the overlay, and the Firefox session, with a serialized
  queue. No competing BiDi plus Marionette clients. No second client
  opens a session while the owner holds the slot.
- The session has a timeout, and the session is closed in a finally
  block, on every path: success, failure, timeout, and crash. A session
  that is not closed in finally is a wedged slot that blocks every
  later client.
- The wedged-session recovery protocol (who kills a wedged session, on
  what timeout, with what watchdog) is specified by the prototype and
  proven by it (section 11). A hung session blocking every client is
  the known concentration risk of the single-owner design, and the
  contract requires the recovery to be proven, not asserted.

## 6. One local broker

- **One local broker owns session, overlay, and browser.** The broker
  is the single owner of the pointer, the overlay, and the browser
  session. It holds state (window bounds, monitor layout, DOM and
  accessibility sessions, compositor event subscription) instead of
  re-querying the world per action.
- **Sequential queue.** All execution goes through one serialized
  queue. The queue discipline (what happens to the second queued batch:
  wait, refuse, or timeout, and how the queue behaves under concurrent
  VM workers) is specified in the S1 deletion step, not invented here.
  OPEN: the chosen discipline is a decision for the S1 deletion worker,
  recorded before the deletion executes.
- **act-now routes through the session driver, not a per-batch session
  spawn.** act-now today spawns a session per call; the fix routes it
  through the long-lived session driver (PROBE-S1 proved the broker
  path from the VM: 12.110s vs 28.700s one-shot, 2.37x faster). The
  per-batch spawn is deleted only after the five S1 conditions are met
  (laptop tree synced, one-shot SSH kept as fallback and recovery,
  master watchdog plus soak, fatal-on-read-failure decided, single-owner
  serialization decided).
- **Fallback only when the log confirms the session has not run an
  action.** The fallback path (direct Pointer, no session) is used
  only when the log confirms the session has not yet run an action in
  this batch. A fallback after a session action is a double-execution
  risk and is refused.
- **Timeout continues without replay.** When a batch times out, the
  run continues without replaying the timed-out actions. The timeout
  is reported with the actions whose outcome is unknown, and recovery
  is a model decision on fresh state (section 2.6), never an automatic
  replay.
- **Transport.** JSON over the persistent channel (or in-process calls)
  replaces scp per step. Files stay as the audit and evidence trail
  (persisted observation artifacts, JSON plus JPEG, written by the
  driver); what dies is files as the transport, not files as the
  record. Fresh SSH stays as the fallback and recovery path: if the
  broker dies, one-shot SSH is how the relay gets restarted.
- **Single-runner lock as a task lock.** The single-runner lock stays
  (one live runner, one BiDi or Marionette session total). The driver
  holds it as a task lock, not as a process tree. The lock, the cancel
  latch, and the named task scope are all held by the driver; the
  session supervisor tree is deleted only when the driver demonstrably
  holds all three on a live run (A3 gate, B4 lift).
- **Pill visibility stays.** The pill is the owner's only visibility
  into live runs. The sequence is staged: session-level pill first
  (acquire once per task, server kept, measured), then driver-owned
  pill (or compositor-plugin indicator) with proof it shows and clears,
  including no stale or missing pill when the driver dies mid-task,
  then delete the overlay server (A4 gate, B3 lift). The LIQUID
  flicker probe (or an explicit owner deferral recorded) precedes the
  session-level pill judgment.
- **Lifecycle.** The contract covers daemon crash and stale-state
  behavior, session-holding scope (holding the single Firefox session
  blocks every other tool for the task duration), and lifecycle across
  laptop sleep and reboot. A driver that dies mid-task must not leave
  a stale pill, a held lock, or a wedged session behind it; the
  recovery for each is specified by the prototype and proven by it.

## 7. Locate confirmations

A locate is confirmed only when all five hold, checked live at
execution time, not at plan time:

1. **Visible**: the element is rendered, not hidden, not zero-size,
   and inside the viewport (or scrolled into it by the executor before
   the check).
2. **Interactive**: the element is enabled and can receive the input
   (not disabled, not inert, not covered by a modal that swallows
   events).
3. **Uncovered**: a hit test at the action point returns the target
   element (hit_check, zen_dom.py:820-851 pattern). If the hit test
   returns a different element (an overlay, a toast, a sticky header),
   the locate fails and the action does not run.
4. **Stable**: two rect reads, taken a short interval apart, agree.
   A moving element is not clicked at a stale rect; the executor waits
   for stability or re-grounds. OPEN: the interval and the agreement
   tolerance are set by the prototype from measured data.
5. **Unique**: the selector or role-and-name resolves to exactly one
   element in the visible set (querySelectorAll count 1, or ref
   disambiguation by the executor). A non-unique target is refused,
   never resolved by picking the first match.

Handling, per case:

- **Moving elements**: wait for the element to settle, then re-read
  the rect and confirm stability before acting. If it does not settle
  within the prototype's bound, refuse and report.
- **CSS transforms**: the rect used is the post-transform bounding
  rect, and the hit test is done at the transformed point. A transform
  that moves the element between the rect read and the click is a
  stale-ref disagreement (section 4.4).
- **Iframe offsets**: the rect is resolved through the iframe chain to
  the top-level frame, with each frame's offset applied once. An
  iframe the backend cannot traverse is a coverage gap, recorded and
  routed to the next backend, not guessed.
- **Non-unique targets**: refused with the match count and the
  distinguishing features of the matches, so the model can disambiguate
  on a fresh snapshot. The executor never disambiguates by position
  alone.
- **AT-SPI coverage**: the truncated flag and node count are reported
  with every locate (section 5.3). A locate against a truncated tree
  that does not contain the target is a coverage failure, not a
  target-absent verdict.

## 8. Batch growth

- **Batches grow by proven validity, not by stuffing coordinates into
  one image.** A batch grows only when the executor proves the next
  steps are still valid: preconditions hold per step, postconditions
  pass per step, and the batch stops at the first failure. A batch
  that continues past a failed step is a defect, not an optimization.
- **The per-click math is illustration, not a gate.** At a hypothetical
  90% per-click rate, 20 clicks all-correct is 12.2% and 32 clicks is
  3.4% under independence, but real errors correlate through the shared
  frame (one wrong frame poisons every coordinate taken from it), so
  the true all-correct rate is likely worse when the frame is wrong.
  Those numbers must never be quoted as measured rates and never used
  as a gate threshold. No measured per-click rate on held-out tasks
  exists.
- **Maximize VERIFIED actions per model call, not actions per
  observation.** The metric that matters is how many actions per model
  call reach verified=true. A batch of 32 input_sent actions with zero
  postconditions is worth less than a batch of 5 verified actions. The
  old 32-action cap (desktop and code-exec) is a capacity limit, not a
  target.
- **After a step that can change the page or focus** (navigation, form
  submit, dialog open or close, tab switch), the executor re-validates
  the next step's preconditions from live state before acting. The
  after-capture happens per risky step where the contract requires it,
  not only at the end of the batch.
- **A form may run many steps in one call**, but Submit, and any click
  that can cause a side effect, carries its own precondition and its
  own postcondition. Side-effecting steps are never bundled behind a
  single shared postcondition.

## 9. What is removed

These removals are part of the contract. The prototype does not need to
re-argue them; it must not reintroduce them.

- **Generic x/y as the model's everyday input.** The model addresses
  semantic targets and element refs. Coordinates stay an internal
  detail of the pointer adapter, produced at execution time from a
  fresh locate. Any interface that accepts raw x/y from the model as
  its normal path is out of contract.
- **Unrestricted zen_dom eval from the default agent interface.**
  Arbitrary JavaScript in the current tab as a default primitive is
  removed now (CB-5 ADOPTED, step 0). It is kept in an intentional
  debug mode only. The internal evaluate() stays as the transport for
  harvest, locate, and hit_check; that is transport, not an agent
  primitive.
- **Screen-scope after-capture as produced today.** Replaced by the
  both-fields shape (section 4.5). Never ship a non-chainable artifact
  labeled as the batch result again.
- **The 120s age refusal on DOM paths** (D6, scoped). For DOM-grounded
  work, re-read the DOM instead of refusing for staleness. The
  future-clock refusal stays. The window stays for pixel-addressed
  work, where staleness is real.
- **Pixel-band verification as a pass signal for structured targets**
  (A8, sequenced behind P5). The band stays as a diagnostic only, and
  only until the per-action DOM assert exists and is mandatory. The
  band is admitted necessary, not sufficient, by the code itself.
- **dom_rect_to_image_point from the live path** (after P2, step 7;
  kept for tests and legacy). The round trip from an exact DOM rect to
  an exact screen point to a lossy image point and back is deleted.
- **The scope-as-capability refusal in its legality form** (with P2,
  reframed as snapshot binding, section 4.3). The halt on scope change
  stays.

## 10. Measurement

Measurement is part of the contract, not an afterthought. A run that
does not carry these numbers does not count toward any gate.

- **Per-phase timing split, recorded per run**: model, SSH, broker,
  observe, act, verify. Each phase is timed separately; no phase is
  inferred from a total. The model phase is timed by the harness
  (observation delivered to the agent vs located target returned),
  because the model call happens in the calling agent's loop, outside
  the executor. Inference time is recorded separately from vision-call
  latency.
- **First-pointer timestamp**: the timestamp of the first pointer
  action, recorded per run. order_to_overlay is measured from the user
  command on the VM, not from the Python wrapper start.
- **Dispatch split**: VM-to-laptop dispatch measured separately per
  phase (VM send, SSH connect, laptop work, return). The 11.620s
  dispatch figure from F2b stands as measured; the "SSH is 95%" slogan
  is dead and is never quoted. target_breached compares
  first-pointer-action time against the 30s threshold, not whole-batch
  time.
- **Error class per miss**: every miss is classified (wrong target in
  the image vs orchestration fed the wrong frame or scope). G30 is
  class (a); J40 and the after-image trap are class (b). A taxonomy
  populated from measured calls, not written from the armchair.
- **Capture parameters pinned and logged**: one max_width for all
  captures, JPEG quality, and the lossless-crop rule, logged with
  every measurement.
- **CB-9 manifest**: the source commit, the installed artifact
  (hashes), and the log of the same build are locked BEFORE any bench
  gates anything. No rung scores without a manifest for the exact
  build under test. The fixture bench pass (a1a672d, 10.86s) is not
  quoted as a gate until its manifest is locked. The manifest is
  produced by the deploy step itself.
- **Honesty gates**: false successes (ok=true without a postcondition)
  are reported as their own metric, with zero tolerance on the
  acceptance ladder: any false success fails the run's honesty gate
  even if the count passes. Fixture numbers are never pooled with
  real-task numbers.

## 11. Prototype gate (B6 lift)

The contract is proven, not adopted, by the step-9 prototype. The
prototype is the ONLY authorized build of this contract until it
passes. The full 1-2 week merge is not authorized by this document.

The prototype must prove, on live tasks:

- Snapshot, execute, and verify end to end on one live ws2 clone chat
  plus held-out tasks.
- The wedged-session recovery protocol, specified and proven: who kills
  a wedged session, on what timeout, with what watchdog.
- A destructive-action test proving no double-send on retry (section
  2.6).
- The three-part result contract per action, judged by postcondition
  pass rate, not envelope ok rate.
- The metric list from CB-EXEC section 3: first-try target accuracy,
  end-to-end task success, wrong side effects, recovery actions,
  per-phase p50 and p90, model calls, retry count, postcondition
  accuracy, false successes.

If the prototype fails or stalls, CB-EXEC dies and A1/S3 remains the
destination. The merge decision is made on the prototype's measured
evidence, not on this contract.

## 12. Acceptance ladder (what this contract gates)

Precondition for every rung: the CB-9 manifest (section 10).

- **Rung 1, fixture 2-vision benchmark**: PASSED (a1a672d, 10.86s,
  visions_used 2, both sends V12 gated), pending manifest lock.
- **Rung 2, live 0-vision on real ws2 clone chats**: the final gate
  for the chat class. Accuracy at least 90%, defined as end-to-end
  TASK SUCCESS, scored by DOM outcome (V12 sent-bubble gate), with the
  per-phase timing split and the three-part result per action in the
  live run log. One final screenshot is kept as unscored human evidence
  (P9). HARD CONDITION: the final screenshot must be reviewed before a
  run scores as passed, and any DOM-vs-render mismatch FAILS the run.
- **Rung 3, 100-task held-out benchmark**: the general gate, REQUIRED
  before any generality claim, NOT a precondition for rung 2 and NOT
  folded into it. Task success at least 90%, at least 96 passes out of
  100 (Wilson 95% lower bound about 90.2%). LIMIT recorded: the Wilson
  independence assumption does not hold for 100 tasks authored by one
  person on a handful of apps, so the 95% confidence claim is
  indicative, not a proof of independence. The task set, sampling, and
  independence rules are specified BEFORE rung 3 runs.

## 13. Open items (marked OPEN, not decided by this contract)

These are decisions this contract does not make. They belong to the
owners named in the FINAL DIRECTION, section 7. No implementer may
decide them silently while building the prototype.

1. **Plateau numbers** (owner COORD-CLICK-3, HARD GATE on the S2
   flip): the numerical definition of the Step 2 plateau, set from the
   fixture bench baseline (10.86s) plus first live runs, before the
   flip. This contract does not invent the numbers.
2. **Rect-agreement tolerance and stability interval** (owner the P2
   implementer, via the prototype): how many pixels of drift count as
   agreement, and how far apart the two stability reads are taken.
3. **Wedged-session timeout values** (owner the prototype worker): the
   timeout after which a session counts as wedged, and the watchdog
   interval. The contract requires the protocol and its proof, not
   specific numbers.
4. **Queue discipline** (owner the S1 deletion worker): wait, refuse,
   or timeout for the second queued batch, and single-owner
   serialization under concurrent VM workers. Specified before the
   deletion executes.
5. **Per-action exception list contents** (owner the P5 implementer):
   the final list of action types with no cheap postcondition, landed
   per action type as its assert set lands.
6. **Image uniformity value** (owner the step-0 worker): the single
   max_width value for all captures. The contract requires one value,
   pinned and logged; it does not pick the number.
7. **Shadow-DOM fallback shape** (owner the P3 re-run worker): decided
   by the P3 experiment outcome. If the Messenger composer sits in
   shadow DOM and CDP returns null box_model for it, P3 narrows to
   "CDP works except shadow-DOM elements" and P2 carries a shadow-DOM
   fallback.
8. **P3 failure re-plan**: if Brave refuses the debugging port and the
   Chromium migration is too disruptive, the DOM-first live path loses
   its highest-leverage unlock and the whole program re-plans around
   Zen Marionette only. That outcome is reported plainly, not worked
   around silently.
9. **Defective proof tests for AMEND4 items 3, 4, 5-6** (owner the
   round-3 council): repair or re-verify. B5 lift condition (ii). This
   contract relies on them only after they are repaired.
10. **Item 12 regression-test pass and Codex-lane confirmation**
    (owner the AMEND4 close-out worker): the four tests in
    tests/test_first_action.py have not been run by anyone; the
    Codex-lane delivery is unconfirmed. This contract cites the
    both-fields shape as landed in form, not as proven by test pass.

## 14. Log

- 2026-11-22 07:00 +07 (T+0m): task received. Repo
  ~/workspace/computer-use-wayland, branch todolist-push.
- 07:00-07:08 (T+0-8m): read the FINAL DIRECTION (e05fc58, full), the
  Codex report (2596287, full, section 3 in particular), ARCH-REVIEW
  (074c1d7, full), and the adjudication DRAFT (9d23834, stale-ref and
  scope sections). Verified all four commits exist on todolist-push.
- 07:08-07:25 (T+8-25m): wrote this contract. No code written, no code
  deleted, no flag flipped. This is a design document only.

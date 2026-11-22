# Worker CLICK3-FGROUND: GROUNDING-REVIEW position response to the draft adjudication and CODEX-BREAKTHROUGH

Owner: the owner. Role: I hold the GROUNDING-REVIEW position from its log
(improvements/worker-grounding-review-log.md, commit d1fc4e9, 150 lines).
The original GROUNDING-REVIEW worker completed and cannot receive
follow-ups, so I answer the joint adjudication DRAFT and the other reports
from GROUNDING's position, with GROUNDING's verdicts as my starting point.
Decision criterion (owner standing rule 06:07): judge every proposal by
the accuracy and speed of its FINAL RESULT, never by rewrite size or cost.
Cost is IRRELEVANT. No em dash (U+2014) or en dash (U+2013) anywhere in
this file. No personal info. Evidence with every claim. Never ydotool.
This is a review response, not my own work, so no self-healing question
arises.

GROUNDING's verdict, restated: screenshot plus vision is the wrong
perception for web, DOM/a11y default, proposals P1-P9, P3 (Brave relaunch
with debugging port) highest leverage. Nothing in the draft or in
CODEX-BREAKTHROUGH overturns that verdict. Both strengthen it, and both
expand P2. Details below.

## 0. Log and what I verified myself this session

- 06:38 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD was 7b1006a at start.
- 06:38-06:41 (T+0-3m): read in full: GROUNDING-REVIEW (d1fc4e9),
  adjudication DRAFT (improvements/worker-click3-adjudication-log.md,
  9d23834), ARCH-REVIEW (074c1d7), SPEED-REVIEW (a4ecb49),
  CODEX-BREAKTHROUGH (improvements/codex-breakthrough-report.md,
  2596287, 138 lines, Vietnamese), D1 (37f457e), D2 (6d1bf04), D3
  (14fc139), RTD (e96b2ff), X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c),
  XRT (6cb3f95). All twelve inputs read in full before writing.
- 06:41-06:44 (T+3-6m): spot checks V-F1 to V-F9 below. The branch moved
  during this work: AMEND4 items 9 and 10 landed (44c15bb, e912ad4)
  while I read. I fetched again before writing; HEAD at writing is
  e912ad4.
- 06:44 +07 (T+6m): wrote this log.

### Spot checks run by me (new verification, not trust)

- V-F1. PROBE-P8 LANDED and ANSWERED: commit 3790901,
  improvements/worker-probe-p8-log.md (119 lines). Marionette chrome
  context BLOCKED without a Zen restart: HTTP 500, error "unsupported
  operation", message "System access is required. Start Zen with the
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to enable
  it." Session acquire 0.01s, content sanity eval 0.00s (title
  'Welcome!', url https://zen-browser.app/welcome/, mozInnerScreenX
  240, mozInnerScreenY 8, matching the C12 probe exactly, third
  independent confirmation of that geometry), context switch failed in
  0.00s (immediate refusal, not a timeout). Zen PID 496121 untouched,
  no restart, no setting changed, slot left free. MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
  absent from /proc/496121/environ. This independently reproduces the
  C12 probe result (03:27:26 +07 22/11, same HTTP 500, same message).
  P8's probe question is CLOSED.
- V-F2. PROBE-P3 NOT-RUN: commit 7b1006a,
  improvements/worker-probe-p3-log.md (112 lines). Clone1 batch 9 open
  since 06:01 +07 22/11 (assigned commit 422f4b0, 2 tasks, zero
  completion evidence, zero clone1-authored commits on origin/main
  since assignment). Brave running on the laptop, PID 7356, started
  Nov 21, untouched. No relaunch, no /json/list, no cdp.mjs timing, no
  fill plus assert attempted. P3 feasibility is UNDECIDED: no measured
  evidence for or against.
- V-F3. PROBE-S2 status: improvements/worker-probe-s2-log.md (71 lines,
  untracked). Bench and fixture are now ON todolist-push (c5311ce,
  7f3a70b, unedited from origin/main), so the draft's V-A3 (bench
  absent) is now stale. But the fixture run has still NOT run: no
  .venv, no selenium, no firefox/chromium binary on this VM, bench
  hardcodes FF/GD paths under ~/workspace/tools/ which does not exist.
  Y1b 3 real fails STILL OPEN at HEAD 49081aa: no setitimer, SIGALRM,
  or child-process preemption in scripts/codemode.py or
  scripts/code_exec.py; "chr" in NEITHER SAFE_BUILTINS list
  (codemode.py line 37, code_exec.py line 107); latest Y1b watch entry
  18:35 +07 21/11: "Phase A BLOCK verdict stands unchanged."
- V-F4. AMEND4 landed state at HEAD e912ad4: items 1-8 landed
  (cc964b2, c1ea773, 62b740e, 72120aa, b44a5ea items 5-6, 49081aa item 7,
  af0fa87 item 8), items 9 (44c15bb) and 10 (e912ad4) landed DURING
  this response. Item 4's commit message records BrowserAdapter does
  not exist, narrowing the P2 collision surface as the draft states.
  Item 11 (doc fix) and item 12 (after-image scope fix) NOT landed;
  the amend4 driver log still shows item 12 branch/commits/test counts
  as "(pending)".
- V-F5. CB-5 locate gap VERIFIED from source: scripts/zen_dom.py
  locate() lines 567-588 returns getBoundingClientRect only, no
  visibility check, no interactive/enabled check, no uncovered/hit
  check, no stability check, no uniqueness check (find() returns the
  first match). BUT the confirmations exist elsewhere in the same file:
  hit_check() lines 820-851 (elementFromPoint, returns True only when
  the rect center hits the element itself or a contained
  button/link-role child), and harvest() returns hit and focused flags
  (GROUNDING 1.3). CB's gap is real for the locate primitive; the fix
  composes existing pieces, it does not invent them.
- V-F6. CB-5 eval removal VERIFIED: scripts/zen_dom.py main() line
  1144, sub.add_parser("eval", help="run JS in the current tab") line
  1153, handled line 1171. The unrestricted eval CLI primitive exists
  and is reachable. Note the boundary: evaluate() is also the internal
  transport for harvest/locate/hit_check; the removal targets the CLI
  primitive, not internal JS eval.
- V-F7. CB-5 AT-SPI coverage VERIFIED: scripts/a11y.py observe() walks
  at most 500 nodes or 2s, returns at most 80 items, sets truncated
  (bool(pending) or truncated). query() requires a name or role filter
  and is locked behind CU_PICK4_FASTPATH. CB's description is exact.
- V-F8. CB-5 Chromium-only code-exec DOM VERIFIED: scripts/code_exec.py
  DOM_WINDOW_CLASS = 'chromium', dom_observe/dom_act are CDP-based,
  snapshot id binds target and refs for 120 seconds. There is no Zen
  adapter in code-exec; the Zen helper lives separately. A Zen adapter
  under the same contract is genuinely missing work, not just unwiring.
- V-F9. CB-3 image uniformity VERIFIED: scripts/cu.py observe() line
  920 max_width=960 default, observe_screen() line 974 max_width=960
  default, CLI --max-width default 960 line 2758; save_observation
  always re-encodes JPEG (lines 839-840). Against first_action.py:656
  max_width=1920 (verified by D1 V4). The model sees different
  resolution and detail by path. J37 codec false refusal VERIFIED
  verbatim from the error file (lines 832-837): patch 6.627 vs
  threshold 6, JPEG edge smear on the sharp white cursor arrow,
  photographic background, 3 refusals at 01:52 plus 2 at 02:00,
  flakes intermittently. CB's CB-3 is confirmed on both limbs.
- V-F10. CB 2.9 half-refuted, half-confirmed: scripts/first_action.py
  IS tracked in git on todolist-push (git ls-files returns it), so
  CB's "first_action.py not in repo and not git tracked" is stale for
  this branch (it was true for CB's checkout, HEAD 4500a18, behind 622
  commits per its remote-tracking ref). But the installed-vs-repo
  divergence CB names is real and corroborated by the J37 note itself:
  installed cu.py md5 2d208d36 vs repo copy md5 a6dbb3b3, observe()
  return shape differs (persist=True returns meta dict only vs
  (image, meta)).
- V-F11. PROBE-DOMZEN has NOT landed: no domzen log in improvements/,
  no domzen commit in git log. Results not in yet, as briefed.
- V-F12. CB 2.4 batch math checked: 0.9^20 = 0.1216 (12.2%), 0.9^32 =
  0.0343 (3.4%). Arithmetic correct. CB's own caveat stands: real
  errors are correlated, so these are illustrative, not measured.

### Taken on trust, labeled as such

- CB's laptop-local numbers (2.7): act-now JSONL 199 lines, p50
  order-to-overlay 337.5 ms, max 368.4 ms, p50 wrapper 2.288 s, max
  6.95 s, 167 ok=true and 32 ok=false, 195 session and 4 fallback,
  0 timeout, 5 source=captured. I cannot verify these from the VM;
  they are CB-reported, not independently verified. CB itself states
  they measure executor time, not hit rate or task success.
- DOM bench timings (66 rects Marionette median 0.030 s, 5 DOM clicks
  0.0022-0.0053 s, verify 0.002-0.015 s, session start BiDi 1.51-2.77 s
  fresh, Marionette attach 2.65-4.12 s, one-session constraint):
  single-source, clone2 batch 7, cited by all four reviews and all
  four councils (RTD C1 applies). PROBE-DOMZEN is the run that would
  make it two-source; it has not landed (V-F11).

## 1. The draft's verdicts on P1-P9: right, too gated, too loose

### P1 DOM/a11y default router: draft ADOPT. AGREE, with two tightenings.

The draft is right: encode the router in code as one function, fail
closed to the labeled screenshot fallback, per-target routing table
proven per target, log line on every routing decision. GROUNDING
accepts all four conditions. Two tightenings from CODEX-BREAKTHROUGH:

- T1a. The router must route on COVERAGE, not just on target type
  (CB-5). A backend that returns an empty harvest or a truncated a11y
  tree (a11y.py truncated flag, V-F7) must fall through to the next
  backend, not fail and not proceed on a partial inventory. The
  truncated flag is the signal; the router reads it.
- T1b. The router's Zen branch now records a DECIDED boundary, not a
  probe: Zen chrome UI routes to screenshots, permanently until an
  owner-approved restart (V-F1). The draft's P1 row still treats P8 as
  an open probe; it is closed.

Where the draft is too loose: the draft notes the a11y branch is thin
but does not say what the router does when the a11y branch is the only
structured path and it truncates. T1a closes that. Where the draft is
too gated: nowhere on P1. Interim honest state stands: Brave tasks
still route to screenshots until P3 lands.

### P2 Element-ref action interface rewrite: draft MODIFY (B5). AGREE, and the gate is now one item, but the content is bigger than the draft's row.

The draft is right on direction and on the B5 gate shape: stale-ref
disagreement protocol specified first, AMEND4 items 2-4 landed. At
HEAD e912ad4 the second limb is SATISFIED (items 2, 3, 4 landed at
c1ea773, 62b740e, 72120aa; item 4's message confirms BrowserAdapter
does not exist, so the collision surface is the CLI act path,
CodeExecBackend.act, and the first_action fallback). Items 5-6 also
landed (b44a5ea), so A9's origin-staleness dependency is satisfied
too. The protocol is now the SINGLE outstanding gate for B5. The draft
said this at HEAD 72120aa; it is still true at e912ad4.

Where the draft is too loose: the draft's P2 is "live rect re-read at
execution". A re-read is not enough. CB-5 proves locate() returns a
rect with no confirmation at all (V-F5). P2 must be a live RE-CONFIRM,
not a re-read: visible, interactive/enabled, uncovered (hit_check,
zen_dom.py:820-851), stable (two rect reads agree), unique
(querySelectorAll count is 1, or the ref disambiguates). The pieces
exist (hit_check, harvest hit/focused flags); P2 composes them into
locate. Without this, P2 deletes the image-frame round trip but keeps
a rect that can be wrong in exactly the ways CB-5 names: a hidden
element has an exact rect, a covered element has an exact rect, the
second match has an exact rect. GROUNDING accepts CB-5's expansion
into P2.

Where the draft is too loose, second: P2's scope must include the Zen
adapter (V-F8). code_exec.py's DOM is Chromium-only; the element-ref
interface must cover Zen Marionette refs under the same contract
(snapshot id, refs, confirmations), not only CDP refs. The draft's P2
row never names the Zen adapter; CB-5 does. GROUNDING adopts it as
part of P2.

Where the draft is too loose, third: the draft says "delete
dom_rect_to_image_point from the live path (keep for tests and
legacy)" without requiring the live callers to be enumerated first.
Enumerate them (desktop_act, first_action, code_exec backends, tests)
before deletion; the enumeration is the proof the deletion is complete.
BrowserAdapter does not exist, so it is not a caller.

Where the draft is too gated: the draft sequences the scope-as-capability
refusal deletion with P2. GROUNDING agrees with that timing (D3/RTD,
against D1's original A7 timing): while actions are pixel-addressed,
the refusal protects typing against a screen observation. That gate is
correct, not over-gating. But see section 2, CB-2: the refusal must
not be confused with the substitution defect, which is a separate fix
that does NOT wait for P2.

Verdict: P2 MODIFY, content expanded per CB-5 (re-confirm, Zen
adapter, eval removal per section 2, caller enumeration). Gate: the
stale-ref disagreement protocol, written as the P2 design's
disagreement section (not as a separate gate document), with
CB-EXEC's per-case rules: refuse, re-plan, or click stale per action
type, plus retry only when the executor knows input was not sent.

### P3 Brave relaunch with debugging port: draft ADOPT as a controlled experiment. AGREE on the verdict, DISAGREE on its position in the order (section 3).

The draft is right on the verdict and on every condition: quiet window
owned by the coordinator, never mid-batch, verify /json/list shows the
Muse tab and login intact, one fill plus assert on a scratch input,
CDP port 9223 local-exposure noted, Chromium fallback named as a
migration with its own login-persistence check, BLOCK on any live-task
migration until the experiment passes, plain re-plan around Zen
Marionette only if it fails. GROUNDING accepts all of it.

One addition: the experiment must also check the shadow-DOM gap the
draft records as unexamined (cdp.mjs notes shadow-DOM elements have
null box_model; Messenger's DOM shape against that gap is unexamined).
zen_dom locate() pierces open shadow roots; the CDP harvest must be
checked against the same composer. If the Messenger composer sits in
shadow DOM and CDP returns null box_model for it, P3's ADOPT narrows
to "CDP works except shadow-DOM elements" and P2 must carry a
shadow-DOM fallback. Make it an explicit P3 check item, not a footnote.

Where the draft is too gated: the draft gates "any live DOM work" on
P3 (step 2 gate to any live DOM work). That is too broad; see section 3.
P3 gates live DOM work ON BRAVE, not live DOM work as such.

P3 evidence state: UNDECIDED. PROBE-P3 returned NOT-RUN (V-F2):
clone1 batch 9 open since 06:01, Brave PID 7356 untouched. Zero
measured evidence for or against. Per the Lauren Tan standard, P3
counts as neither feasible nor refuted today.

### P4 After-image scope fix (merged into A7): draft ADOPT the both-fields shape, DEFERRED to AMEND4 item 12. AGREE on the shape, INCOMPLETE on scope.

The both-fields shape (after scope-matching and chainable,
after_screen verification only and documented non-chainable, scope
check before the overlay attempt, regression test) is right, and
deferring execution to AMEND4 item 12 is right. Item 12 is still in
flight (V-F4, driver log "(pending)"), so nothing has changed there.

But the draft's A7/P4 row covers only HALF of the scope defect. CB-2
(section 2.3) proves a second scope defect the draft never addresses:
the _fresh_observation substitution. When an observation is missing,
stale, or errors, the wrapper captures a full-screen image and hands
the ORIGINAL action list to the executor without re-framing
coordinates (installed first_action.py:289-315; J40: a point taken
from a window image used on a full-screen image, missed the button by
(+45,+12) px, command still returned ok). The both-fields fix does not
touch this path. GROUNDING says: adopt CB-2's rule as an addition to
A7/P4 (scope change stops the batch, never silently substitutes), owned
by the item-12 lane or recorded as its own defect. See section 2 for
the reconciliation with P4's "delete the scope-as-capability rule".

### P5 DOM verification mandatory: draft MODIFY (per action type as its assert lands, explicit exception list). AGREE.

The draft is right, and its settlement of (f) is right: RTD's "V11
MutationObserver flag is an open TODO" phrasing is NOT adopted as
phrased (arm_typed_flag exists in zen_dom.py, MutationObserver JS
inside it, called from production code at dom_act.py:433-434; X3
verified the observer code at zen_dom.py:983). The P5/A8 change rests
on the verified opt-in-hooks ground (focus_check and type_check are
still optional hooks, first_action.py:597-613). GROUNDING accepts the
draft's (f) in full.

One addition from CB-EXEC: P5's assert set is a POSTCONDITION set, and
it needs a PRECONDITION set alongside it (target unique, visible,
enabled, in the right window; geometry and focus unchanged since
grounding). The exception list (scroll position, hover state) stands.
The P5 implementer's open confirmation (whether the production
code-exec path reaches the arm_typed_flag call for every type action)
stands as the draft records it.

Where the draft is too loose: the draft does not name the result
contract. CB 2.1 names it: every action returns three separable facts
(input sent, right target received it, postcondition confirmed).
desktop_act's ok must become input_sent; verified=true only on
postcondition. GROUNDING adopts this as P5's deliverable shape.

### P6 Measure the vision call: draft ADOPT with specification fix. AGREE, with CB additions.

The draft's specification fix is right (timestamp points: observation
delivered to the agent vs located target returned; logging owner is
the harness, not cu.py; bundle with S0). GROUNDING adds three CB
items to the P6 spec:

- P6a. Measure model INFERENCE time separately from vision-call
  latency (CB 2.7/2.8, RTD C4). The 10s target depends on inference
  time, which nobody has measured. Record a first-pointer-action
  timestamp and measure order-to-overlay from the user command, not
  from the wrapper start (CB 2.7: first_action.py records from wrapper
  start and compares the whole batch against the 30s threshold).
- P6b. Log the ERROR CLASS per miss (CB-3 taxonomy): model picked the
  wrong target in the image vs orchestration fed the wrong frame or
  scope. G30 (64/75 px) is class (a); J40 (+45,+12 px) and the
  after-image trap are class (b). Without the class, P6 measures a
  rate but not a cause.
- P6c. Pin the capture spec. Image size and compression vary by path
  (observe default 960, act-now 1920, JPEG q90 always, V-F9). P6 logs
  the capture parameters with every measurement, or the latency
  numbers are not comparable across paths.

Until P6 lands with this spec, nobody may claim the 10s target is met.
The draft already says this; GROUNDING keeps it.

### P7 Session handover protocol: draft MODIFY (Marionette-only question first). AGREE.

The draft is right: first answer whether Marionette-only suffices (the
benchmark already runs Marionette-only, harvest plus input, and zen_dom
harvest IS Marionette); write the handover protocol only if a task
genuinely needs BiDi for grounding plus Marionette for input; price
the handover at 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette
attach 2.65-4.12s). GROUNDING adds one requirement from CB 2.6: the
protocol must name the SINGLE SESSION OWNER (one owner for pointer,
overlay, and the Firefox session, with a serialized queue, no
competing BiDi plus Marionette clients). The one-session constraint is
proven in 4 runs; the owner is the missing piece, not the sequence.

Where the draft is too gated: nowhere. P7 is small and non-blocking
either way, as the draft says.

### P8 Zen chrome Marionette context test: draft ADOPT as a bounded, time-boxed, low-priority probe. SUPERSEDED BY EVIDENCE; verdict changes to CLOSED.

PROBE-P8 ran and answered (V-F1, commit 3790901): BLOCKED without a
restart, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12
reproduced exactly. The draft's P8 row, written before the probe
landed, is now stale. GROUNDING's P8 proposal as written ("test
set_context chrome; if blocked without a restart, keep screenshots
ONLY for chrome UI and record that boundary explicitly") is SATISFIED
by the probe result. New P8 verdict: CLOSED. Keep screenshots ONLY for
Zen chrome UI, record the boundary explicitly in the router (P1 T1b),
AT-SPI stays closed for Zen, no further time on this path. The only
thing that reopens it is an owner-approved Zen restart with
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, which is an owner decision, not a
probe, because it kills owner tabs and the session. This also converts
A2's sequencing constraint (Zen chrome stays pixel-primary until P8
proves a structured path) from a conditional into a decided boundary.

### P9 Keep one screenshot for the human: draft ADOPT. AGREE, with one tightening.

The draft is right, including RTD's wording correction (VISION 2 is
the agent's final sanity check reported to the human, not the owner
looking directly). Cost about 0.25s plus one vision read is noise
against the total. Tightening from CB-3: pin the P9 capture parameters
(fixed size and compression). The human evidence channel must not vary
by path the way machine perception does today (960 vs 1920, V-F9).

## 2. GROUNDING's proposals vs CODEX-BREAKTHROUGH

CB's report landed AFTER the draft (draft V-A1: PENDING, 17-line
launch stub; now 2596287, 138 lines). The draft's section 1.4 therefore
has no CB verdicts, and this section supplies GROUNDING's. CB is an
independent audit: it read the todolist, the full error file,
scripts/cu.py, the browser/a11y adapters, broker/session driver, and
the installed act-now code on the laptop; it opened no windows and
drove nothing; its only new measurement is a read-only summary of the
existing act-now JSONL. Under RTD C1, a fourth reading of the same
evidence base is still the same evidence base where CB cites E2, G30,
F2b, and clone2 batch 7 second-hand. CB's NEW contributions are the
ones it verified from source itself (locate, eval, a11y bounds,
code-exec Chromium-only, scope substitution, J37, the ok-contract,
the batch math). Those are judged below on their own verification
(V-F5 to V-F10), not on CB's authority.

### CB-5 (section 2.5): many backends, no common executor. GROUNDING: ADOPT, as an expansion of P1/P2/P5/P7.

CB-5's findings, each checked:

- Act-now routes only to desktop_act (installed first_action.py
  :403-405, :457-460), never routes a web target to DOM or AT-SPI.
  GROUNDING accepts: this is P1's router missing from the live path.
  P1 as drafted says "encode the router in code as one function";
  CB-5 sharpens it: the router must live INSIDE the executor, and
  routing must not be a model decision. The model picks the target;
  the executor picks the backend.
- code-exec DOM is Chromium-only (V-F8). GROUNDING accepts: the Zen
  adapter is missing work under the same contract (snapshot id, refs,
  confirmations). Adopted into P2 (section 1).
- zen_dom locate() confirms nothing (V-F5). GROUNDING accepts: locate
  must confirm visible, interactive, uncovered, stable, unique.
  Adopted into P2 as the re-confirm (section 1). The confirmations
  already exist in the same file (hit_check, harvest flags), so this
  is composition, not invention.
- Unrestricted zen_dom eval in the default agent interface (V-F6).
  GROUNDING accepts: REMOVE the eval CLI primitive from the default
  agent interface, keep it in an explicit debug mode. Adopted into P2.
  Boundary: internal evaluate() stays; it is the transport for
  harvest, locate, and hit_check.
- AT-SPI is partial and must report coverage (V-F7). GROUNDING accepts:
  the backend returns its truncated flag and the router falls through
  to DOM or image when the tree is insufficient. Adopted into P1 (T1a).
- DOM click is not equivalent to real mouse input (BiDi pointer click
  failed, Marionette viewport limits, docs/zen-dom-control-comparison.md
  :67-120, CB-cited). GROUNDING accepts with a precise consequence for
  P2: the executor clicks via the REAL Pointer from the live rect
  (GROUNDING P2 already says this), and DOM .click() (0.0022-0.0053s)
  is NOT the default execution, only a proven-equivalent shortcut per
  control type. The Browse-button hover case (real hover needed) is
  the proof that the distinction matters.
- CB-5's "semantic locate plus real input when hover/trusted event is
  needed plus state verification" is exactly GROUNDING P2 plus P5
  composed. No contradiction; CB-5 is the stricter statement of the
  same direction.

### CB-2 (section 2.2): observation scope changes between steps. GROUNDING: ADOPT, as an addition to A7/P4, with one reconciliation.

CB-2 proves TWO scope defects. The first (envelope after-image always
screen-scoped, installed first_action.py:480-485) is the A7/P4 defect
the draft already adopts. The second is new to the draft: the
_fresh_observation substitution (installed first_action.py:289-315).
When an observation is missing, stale, or errors, the wrapper captures
a full-screen image and hands the ORIGINAL action list to the executor
without re-framing coordinates. J40 is the measured consequence: a
point from a window image used on a full-screen image, missed by
(+45,+12) px, command still returned ok. J35 is the same shape
(window observation 1863x1176, after full-screen 1920x1200).
GROUNDING adopts CB-2's rule: scope is a mandatory part of action
data; a scope change stops the batch, never silently substitutes; a
fresh observation with a different scope requires re-grounding, not
continuation.

Reconciliation with P4: GROUNDING's P4 said "delete the
scope-as-capability rule". CB-2 says "scope mismatch must stop the
batch". These agree once the two different rules are separated. The
rule to DELETE (with P2, per the draft's sequencing) is the refusal
to act on a correctly-addressed action because the OBSERVATION's scope
is screen. The rule to KEEP (and add, for the substitution path) is
the halt on a scope CHANGE mid-batch: never silently re-frame, never
substitute a screen capture for a window observation and continue.
One is a legality gate on a good action; the other is a halt on a
changed world. GROUNDING adopts CB-2's formulation as the sharper
statement of W4's fix.

### CB-3 (section 2.3): vision error taxonomy, image uniformity, J37. GROUNDING: ADOPT on all three limbs.

- Taxonomy: CB splits vision error into (a) the model picks the wrong
  target in the image, and (b) orchestration feeds the wrong frame or
  scope into the same action. GROUNDING accepts. E2 17/29 first-try
  (58.6%; CB's Wilson 95% interval 40.7-74.5% on n=29, arithmetic
  not re-checked by me, sample small and not held-out, as CB itself
  states) is class (a). G30 (64/75 px) is class (a). J40 (+45,+12 px)
  and the after-image trap are class (b). The screenshot path suffers
  both classes; the DOM path suffers neither. This taxonomy sharpens
  GROUNDING W1 and becomes P6b (log the class per miss).
- Image uniformity: VERIFIED (V-F9). Observe defaults to 960 wide,
  act-now captures at 1920, JPEG q90 always. The mapping code
  compensates arithmetic scale but not recognition: the model must
  recognize the target from different resolution and detail by path.
  GROUNDING adopts the fix: pin one capture spec for machine
  perception (P6c) and a separate pinned spec for P9 human evidence.
  CB's note that a global screen-scale factor cannot explain the
  errors (screen 1920x1200, scale 1, cu.py:973-977 maps through the
  capture region) agrees with GROUNDING 1.1, which refuted the
  "screen ratio 1.55x" story on the same evidence.
- J37 codec false refusal: VERIFIED verbatim (V-F9). Patch 6.627 vs
  threshold 6, JPEG edge smear on the sharp white cursor arrow,
  photographic background, intermittent flakes. GROUNDING adopts: the
  preflight patch comparison must be split from real screen change
  (the J37 note's fix: drop the park move, park only on flat light
  area). This is a pixel-path defect that DOM-first sidesteps, but it
  bites the fallback path and must be fixed there, not left as a
  refusal source. It does not gate P2.

### CB-EXEC (section 3): semantic transaction executor. GROUNDING: ADOPT as the composition of P1/P2/P5/S1, with three additions and two cautions.

CB-EXEC's contract: target (role plus name, or selector/ref from a
fresh snapshot), scope (window/tab, frame, observation id),
preconditions (unique, visible, enabled, right window, geometry and
focus unchanged), input (real mouse/keyboard, or a DOM/API action
proven appropriate for that control), postcondition (dialog closed,
URL changed, field has value, checked state changed, new text
appeared), retry policy (retry only when the executor knows input was
not sent; check state before replaying a side-effecting action).
Resolve on the laptop by backend: DOM/BiDi for web, AT-SPI for desktop
controls, screenshot CROP for canvas, image content, or unexposed
controls. After each page- or focus-changing step, wait on a
postcondition locally and return a small diff. Call the model or an
image only when structured data cannot settle the condition.

Relation to GROUNDING: CB-EXEC is P2 (interface) plus P5
(verification) plus P1 (router) plus S1/A1 (single owner, persistent
path) composed into ONE executor contract. GROUNDING's proposals are
the parts; CB-EXEC is the composition. Under RTD C2, the composition
is unproven until it runs; CB-EXEC does not claim otherwise (its
effort figures, 2-3 days for a Zen prototype, 1-2 weeks for the full
merge, are estimates, not measurements, and under the 06:07 criterion
cost is irrelevant anyway, so they do not affect the verdict).

Three additions GROUNDING adopts from CB-EXEC into P2/P5:

- EX1. Preconditions per action (unique, visible, enabled, right
  window, geometry plus focus unchanged). P5 gains a precondition set
  alongside its postcondition set.
- EX2. Retry policy: retry only when the executor knows input was not
  sent; check state before replaying any action that can send or
  delete data. This is the missing half of the stale-ref protocol
  (B5): the protocol answers both "the rect disagrees" and "the
  action may already have run".
- EX3. Ref binding: every target ref is bound to a snapshot ID and a
  scope; an expired observation or a changed scope refuses, never
  substitutes. This is CB-2's rule restated as a ref invariant, and
  it belongs in P2's interface definition.

Two cautions:

- CX1. CB-EXEC's "screenshot crop" backend is a refinement GROUNDING
  did not name: the pixel fallback should use a lossless PNG crop of
  the target region, not a full-screen JPEG, and keep the lowest
  structure needed. Adopted into P1's fallback branch.
- CX2. CB-EXEC's benchmark design (100 held-out tasks, browser plus
  desktop, new content and layout; 90% defined BEFORE the run as
  click hit rate or task success; 96/100 needed for 90% task success
  at 95% Wilson) is a STRONGER acceptance bar than the draft's live
  0-vision run on the clone chats. GROUNDING adopts the discipline
  (define 90% as task success before the run; never pool the 13/13
  fixture with real-task numbers) but keeps the draft's clone-chat
  live run as the FIRST live gate; the 100-task held-out set is the
  NEXT rung after it passes, not a replacement for it. CB's warning
  not to pool 13/13 on a fixture with 90% on real tasks is accepted
  in full (CB 2.8: the 0.64s fixture and 13/13 do not transfer; J10
  think-time still OPEN; DONE is a state of a specific piece of
  evidence, not of a feature in general).

### Other CB findings, judged briefly

- CB 2.1 (ok=true on input sent): ADOPT. cu.py:1541-1549 (desktop
  check knows cursor position only), :1580-1592 (3 px cursor check),
  :1806-1809 (pixel hash, animation also changes it), a11y.py:204-219
  (do_action true taken as click complete), installed
  first_action.py:422-439 (ok=true when cu.py reports ok or enough
  actions completed). This is GROUNDING W3 with the ok-contract named.
  The three-way result contract (sent, target, verified) is adopted
  into P5 (section 1).
- CB 2.4 (max actions per image is the wrong goal): ADOPT. The batch
  math is correct (V-F12: 0.9^20 is 12.2%, 0.9^32 is 3.4%). Batch size
  grows only when the executor proves the next steps are still valid,
  not because coordinates fit on one image. This is GROUNDING W9
  restated with numbers, and it kills the "one vision drives max
  actions" goal as stated: the goal bar is per-task success.
- CB 2.6 (act-now does not use the long-lived session driver): ADOPT.
  One owner for pointer, overlay, and the Firefox session, serialized
  queue, no competing BiDi plus Marionette clients (one remote session
  per Zen instance). This is S1/A1's requirement restated; the single
  owner belongs in P7 (section 1).
- CB 2.7 (latency budget measures the wrong promise): ADOPT as P6
  additions (P6a). On CB's "no record supports 11.6s of 12.26s is SSH
  dispatch": GROUNDING CORRECTS CB. The F2b log IS the VM-side record
  (order-to-overlay 12.262s, dispatch 11.620s, verified by D1 V10 from
  improvements/worker-f2b-live-session-log.md lines 33-35). CB read
  only the laptop JSONL, which cannot show SSH by construction. CB's
  point stands in the narrower form: no SINGLE run measures VM dispatch
  plus model inference together (RTD C4, same). The F2b 95% stands as
  a VM-side measurement; the combined budget is still unmeasured.
- CB 2.8 (fast evidence is not representative): ADOPT. Same as the
  draft's ladder rationale. No verdict change.
- CB 2.9 (installed code not reproducible from checkout): HALF-REFUTED,
  HALF-CONFIRMED (V-F10). The file-presence claim is stale on
  todolist-push (first_action.py is tracked); the installed-vs-repo
  divergence is real (md5 2d208d36 vs a6dbb3b3, observe() shape
  differs). GROUNDING adopts CB's manifest requirement as a
  precondition for the acceptance run: lock source commit, installed
  artifact, and log into one manifest before a live benchmark counts.
  Without it, a live pass cannot be attributed to the code under test.

## 3. The draft's order of work and acceptance ladder

### P3's position: the draft is right about the step, wrong about the gate.

The draft's order: 0 S0 plus P6, 1 AMEND4 parallel, 2 P3 plus P8,
3 fixture bench, 4 Y1b fixes, 5 P1/P5, 6 S2 one-class flip, 7 P2,
8 S1, 9 A1/S3, 10 deletions, 11 acceptance. GROUNDING agrees with the
step order with two corrections:

- C-O1. P8 is CLOSED (V-F1). Remove it from step 2. It no longer
  occupies a position in the order.
- C-O2. P3 at step 2 must NOT gate steps 3-6. The draft says "Gate to
  any live DOM work: P3 passes". That gate is too broad. P3 gates live
  DOM work ON BRAVE (the clone chats). The fixture bench run (step 3),
  the Y1b fixes (step 4), P1/P5 (step 5), and the S2 one-class flip
  (step 6) do not depend on Brave. PROBE-P3's NOT-RUN (V-F2) proves
  the stall risk is real: the probe already failed to run once because
  clone1 batch 9 has been open since 06:01. If the program gates
  everything on P3, one open clone batch stalls the program
  indefinitely. P3 stays at step 2 in the sense of "attempt at the
  first quiet window", but it gates ONLY the step 11 live acceptance
  run on the clone chats, not steps 3-6.
- C-O3. If P3 keeps NOT-RUNning for lack of a quiet window, the S2
  one-class flip must be RE-SCOPED, not stalled: flip on a
  Zen-reachable task class (Marionette path, no Brave needed) rather
  than waiting on Brave. The draft's S2 flip class is "clone chat
  sends", which needs P3; the re-scoping is the escape hatch if the
  quiet window does not come. The flip still measures the same thing
  (DOM-first plus code-exec plus checkpoint verification, one class,
  act-now fallback); only the venue changes.

### P2-after-B5 sequencing: AGREE, and the gate is now one item.

The draft's B5 STANDS, narrowed: stale-ref protocol specified AND
items 2-4 landed. At HEAD e912ad4 the second limb is SATISFIED (V-F4).
The protocol is the single outstanding gate. GROUNDING agrees with
the sequencing (P2 after AMEND4 items 2-4, after the S2 one-class
flip in the draft's order, with the protocol specified first), and
adds that the protocol is written AS the P2 design's disagreement
section, with CB-EXEC's rules (EX2 retry policy, EX3 ref binding).
P2's content is now bigger than the draft's row (re-confirm per CB-5,
Zen adapter, eval removal, caller enumeration), but its position in
the order does not move: after B5 lifts, after the S2 flip measures
the shape. X3's hold (P1/P5 before S2, because S2's checkpoint
verification IS P5) is agreed and kept: flipping S2 without P5 runs
code-exec with pixel-band verification only, a window the draft
correctly refuses.

### Acceptance ladder: AGREE with the draft's ladder, with two amendments.

The draft: fixture 2-vision required first, live 0-vision final gate,
live 2-vision diagnostic only (B1 LIFTED). GROUNDING agrees with the
B1 lift: XRT's point is correct on the bench design (VISION 1 is a
DOM harvest in both forms; live 2-vision and live 0-vision-with-P9
are the same machine behavior; they differ only in whether the human
looks at live threads or at a screenshot). A gate must protect
accuracy or speed measurably, and the middle rung protects neither
beyond what the P9 screenshot already supplies. The V11 limb is
conceded as non-load-bearing for benchmark scoring (the bench scores
by the V12 sent-bubble gate, not through the production V11 flag).

Two amendments:

- A-L1. Define 90% as TASK SUCCESS before the run (CB CX2). The live
  run's log must carry CB's three-way result contract per action
  (sent, target, verified). Never pool the 13/13 fixture with
  real-task numbers.
- A-L2. The 100-task held-out set (CB's benchmark design) is the NEXT
  rung after the clone-chat live run passes, not a replacement for it.
  The draft's ladder ends at the live run; GROUNDING extends it by one
  rung. The fixture rung stays first: the bench has never run at all
  (V-F3), and the program's gate cannot be an unrun script. Note the
  draft's V-A3 is stale (bench plus fixture landed via c5311ce and
  7f3a70b); what is missing now is the RUNTIME (no selenium, no
  Firefox on this VM), not the files.

The draft's conditions on the live run stand: P3 closed first
(otherwise it falls back to screenshots and proves nothing), quiet
window with clone coordination, owner approval per run, agreed test
messages so the clones' working threads are not polluted.

## 4. What probe evidence would change GROUNDING's verdicts

- PROBE-P3 (re-run in a real quiet window: batch 9 complete, no new
  clone1 batch, no clone1 commits in flight, Brave confirmed idle).
  PASS (Brave accepts --remote-debugging-port on its existing profile,
  login and tabs intact, /json/list shows the Muse tab, one fill plus
  assert on a scratch input): P3 CONFIRMED, the live DOM path on the
  clone chats opens, the draft's order stands as written for the
  clone chats. FAIL (Brave refuses the port): P3 becomes REJECT for
  the Brave path; the Chromium-migration fallback must pass its own
  login-persistence check before it is relied on; if that also fails,
  the program re-plans around Zen Marionette only and reports it
  plainly (draft section 6). PARTIAL (port works but the shadow-DOM
  null box_model gap bites the Messenger composer): P3 narrows to
  "CDP works except shadow-DOM elements" and P2 carries a shadow-DOM
  fallback. Until the re-run, P3 is UNDECIDED (V-F2), and per section
  3 it must not stall steps 3-6.
- PROBE-DOMZEN (DOM-first on real Zen, results not in yet, V-F11). If
  it re-measures the clone2 numbers live on REAL Zen (66 rects about
  0.030 s, 5 clicks all land, verify 0.002-0.015 s), the DOM timings
  go from single-source (C1: one measurement cited three times) to
  two-source, and P1/P2 confidence rises from trusted to measured. If
  it FAILS to reproduce (Marionette attach 2.65-4.12 s dominates, or
  the one-session constraint blocks harvest plus input in one task),
  P7's handover question becomes load-bearing and P2's live re-confirm
  cost must be re-priced. If it shows DOM .click() diverging from real
  Pointer input on real controls, CB-EXEC's real-input requirement
  hardens into a P2 constraint (Pointer only, no DOM click).
- PROBE-P8: ALREADY LANDED (V-F1). BLOCKED, HTTP 500,
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced. P8 is
  CLOSED. No further probe evidence changes it except an
  owner-approved Zen restart with the env var set, which would reopen
  the chrome-context path and flip the screenshots-only-for-chrome-UI
  boundary. Until such a restart, no more time on this path.
- PROBE-S2 (fixture bench run, Y1b fixes): the bench files are on the
  branch but the run has not happened (V-F3, runtime missing on the
  VM). A green fixture run plus the 3 Y1b fails fixed lifts B2 and
  unblocks the S2 one-class flip. A red fixture run, or Y1b fixes that
  do not hold, keeps B2 standing and the flip stays blocked. Neither
  outcome touches GROUNDING's core verdict; both gate S2 only.
- What would change GROUNDING's CORE verdict (screenshot plus vision
  is the wrong perception for web): a held-out measurement showing
  vision first-try at or above 90% on NEW apps (CB's 100-task design)
  with DOM not beating it on wall time; or a live DOM run failing on
  real Messenger (shadow DOM, cross-origin iframes returning None from
  locate, one-session blocks) while vision succeeds on the same tasks.
  Neither exists in the record. E2 17/29 (58.6%, Wilson 40.7-74.5%)
  and G30/G31 (64, 75, 45 px eyeball errors) point the other way, and
  the DOM numbers (0.030 s for 66 rects, verify 0.002-0.015 s) are
  exact where vision is lossy. The core verdict stands.

## 5. Per-proposal verdicts (GROUNDING P1-P9, final)

| ID | Proposal | Verdict | Evidence and gating |
|----|----------|---------|---------------------|
| P1 | DOM/a11y default router, encoded in code | ADOPT, tightened | Draft ADOPT agreed. Add T1a (route on coverage: empty harvest or truncated a11y falls through, V-F7) and T1b (Zen chrome UI routes to screenshots, decided by V-F1). Fallback branch uses a lossless PNG crop (CX1). |
| P2 | Element-ref action interface rewrite | MODIFY, content expanded | Draft MODIFY agreed, B5 stands narrowed. Gate now one item: stale-ref disagreement protocol, written as the P2 design section with EX2 retry policy and EX3 ref binding. Content expands per CB-5: live RE-CONFIRM (visible, interactive, uncovered via hit_check, stable, unique), Zen adapter (V-F8), remove eval CLI primitive (V-F6), enumerate live callers before deleting dom_rect_to_image_point. Collision limb closed (items 2-4 landed, V-F4). |
| P3 | Brave relaunch with debugging port | ADOPT as controlled experiment | Draft ADOPT agreed. Add shadow-DOM check item (cdp.mjs null box_model vs Messenger shape). Evidence UNDECIDED (PROBE-P3 NOT-RUN, V-F2). Gates only the clone-chat live run, not steps 3-6 (section 3). |
| P4 | After-image scope fix, both fields | ADOPT shape, INCOMPLETE scope | Draft ADOPT agreed, deferred to AMEND4 item 12 (still in flight, V-F4). Add CB-2 substitution rule (scope change stops the batch, never substitutes; J40 +45,+12 px, ok returned). Scope-refusal deletion stays sequenced with P2. |
| P5 | DOM verification mandatory | MODIFY | Draft MODIFY agreed. Per action type as its assert lands, explicit exception list (scroll, hover). Add EX1 preconditions and the three-way result contract (sent, target, verified; desktop_act ok becomes input_sent). Draft (f) settlement accepted. |
| P6 | Measure the vision call | ADOPT, spec extended | Draft ADOPT agreed. Add P6a (inference time split, first-pointer timestamp, order-to-overlay from user command), P6b (error class per miss: wrong target vs wrong frame), P6c (log capture parameters; 960 vs 1920 vs q90, V-F9). Until it lands, no 10s-target claim. |
| P7 | Session handover protocol | MODIFY | Draft MODIFY agreed. Marionette-only question first. Add single session owner (CB 2.6): one owner for pointer, overlay, Firefox session, serialized queue. Handover priced 4-7s per switch. |
| P8 | Zen chrome Marionette context test | CLOSED (was ADOPT as probe) | PROBE-P8 answered (V-F1, 3790901): BLOCKED, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced. Keep screenshots ONLY for Zen chrome UI, boundary recorded in P1. Reopens only on an owner-approved Zen restart with the env var. |
| P9 | Keep one screenshot for the human | ADOPT, tightened | Draft ADOPT agreed. Pin the P9 capture parameters (fixed size and compression); the human evidence channel must not vary by path. |

No GROUNDING proposal is REJECTED. P8 changes from ADOPT-as-probe to
CLOSED because its probe landed with an answer. P2 and P4 grow in
content from CB-5 and CB-2; neither changes direction.

## 6. Order of work (GROUNDING's amended draft order)

0. S0 plus P6 now, with the extended P6 spec (P6a, P6b, P6c). Corrected
   numbers (fresh 4.43-5.29 s, mux 0.91-1.46 s, saving 3.2-3.5 s per
   connection, 3.5-5x; 460x dead). Soak test in parallel, advisory.
   Plateau criterion defined numerically before step 6.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule. Items 1-10 landed at HEAD e912ad4; item 11 (doc fix) any time;
   item 12 (A7/P4) lands via the in-flight run, plus the CB-2
   substitution rule as its addition. No parallel edits to the same
   functions from the rewrite track.
2. P3 Brave relaunch experiment, at the FIRST quiet window between
   clone batches, coordinator-owned, never mid-batch. P8 is closed
   and leaves this step. P3 gates ONLY the clone-chat live run (step
   11), not steps 3-6.
3. Fixture 2-vision bench run. Files are on the branch (c5311ce,
   7f3a70b); the VM runtime (selenium, Firefox, geckodriver at the
   hardcoded paths) must be installed first. This step does not depend
   on P3 and runs as soon as step 0 lands.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Still open
   (V-F3). Gate to step 6.
5. P1 router plus P5 asserts per action type (with EX1 preconditions
   and the three-way result contract). Rewiring of existing hooks.
   This precedes the S2 flip because S2's checkpoint verification IS
   P5.
6. S2 flip for ONE live task class with act-now as fallback. Measure
   model-call count and wall time. If P3 is still NOT-RUN, re-scope
   the class to a Zen-reachable task class instead of stalling (C-O3).
7. P2 element-ref interface rewrite, after B5 lifts (protocol
   specified; items 2-4 landed limb satisfied). A9 one-system
   coordinates land here (items 5-6 landed, V-F4). Scope-refusal
   deletion lands here.
8. S1 broker path proof from the VM on one live batch, then delete the
   per-batch spawn. Session-level pill (keep the overlay server) in
   the same step. Manifest precondition (CB 2.9): lock source commit,
   installed artifact, and log into one manifest before the live run
   counts.
9. A1/S3 merged daemon/runner decision, only after steps 0-8 are
   measured and the plateau definition is applied. Prototype must
   prove snapshot/execute/verify end to end on one live ws2 clone
   chat (B6 lift).
10. A3/A4/A5 deletions last, each gated on its replacement proving
    (A4: session-level pill measured, then driver-owned pill crash
    proof, then delete the server; A5: broker proven with one-shot SSH
    kept as recovery).
11. Acceptance ladder: fixture 2-vision (step 3), live 0-vision on real
    ws2 clone chats (final gate, P3 closed first, owner approval per
    run, agreed test messages, 90% defined as TASK SUCCESS, three-way
    result contract in the log), live 2-vision as diagnostic only if
    the live run fails. Next rung after the live run passes: CB's
    100-task held-out set.

## 7. Acceptance test

Ladder with two required rungs, one diagnostic, one next rung:

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. Pass criteria: the script's own gates (V12
  sent-bubble gate after each message, scoring by OUTCOME in the
  thread DOM, never point-in-box). Prerequisite: install the bench
  runtime on the VM (selenium, Firefox, geckodriver); the files are
  already on the branch.
- Final gate (required, last): live 0-vision benchmark on the REAL ws2
  clone chats (clone1 Brave plus clone2 Chrome). DOM harvest, plan,
  execute, DOM verify, zero screenshots in the machine loop. Pass
  criteria: accuracy at least 90%, defined as TASK SUCCESS before the
  run, scored by DOM outcome (V12 sent-bubble gate); total wall time
  measured end to end including transport; three-way result contract
  (sent, target, verified) in the log. One final screenshot kept as
  unscored human evidence (P9, pinned capture parameters). Conditions:
  P3 closed first, quiet window with clone coordination, owner
  approval per run, agreed test messages, source-plus-artifact-plus-log
  manifest locked before the run counts.
- Diagnostic option (not a rung): live 2-vision, only if the live
  0-vision run fails, to localize (script vs DOM path). Same machine
  behavior as live 0-vision-with-P9; it adds no distinct proof.
- Next rung (after the final gate passes): CB's 100-task held-out set
  (browser plus desktop, new content and layout), 96/100 for 90% task
  success at 95% Wilson. This is the rung that turns a clone-chat
  proof into a general claim.

## 8. What STOPS

- P2 STOPS if the stale-ref disagreement protocol is unwritten, or
  the re-confirm composition (hit_check plus uniqueness plus
  stability) is unproven on the S2 task class. The AMEND4-items-2-4
  limb is already satisfied and no longer stops anything.
- P3 STOPS if clone1 is mid-batch (owner hard rule; PROBE-P3 already
  stopped once on exactly this, V-F2). P3 FAILS if Brave refuses the
  port AND the Chromium migration fails its login-persistence check;
  the program then re-plans around Zen Marionette only.
- S2 flip STOPS while the 3 Y1b real fails are unfixed (still open,
  V-F3) or the fixture bench is not green. B2 stands.
- Live acceptance STOPS if P3 is not closed (clone-chat run), if owner
  approval per run is missing, if test messages are not agreed, or if
  the source-plus-artifact-plus-log manifest is not locked.
- P8 is STOPPED permanently unless the owner approves a Zen restart
  with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.
- The whole program RE-PLANS (does not silently work around) if P3
  fails and the Chromium migration is too disruptive: DOM-first live
  work continues on Zen Marionette only, and that is reported plainly.

## 9. Evidence index

- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- Draft adjudication: improvements/worker-click3-adjudication-log.md
  (9d23834).
- ARCH: improvements/worker-arch-review-log.md (074c1d7). SPEED:
  improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH: improvements/codex-breakthrough-report.md
  (2596287, 138 lines).
- D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff), X1
  (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- PROBE-P8: improvements/worker-probe-p8-log.md (3790901). PROBE-P3:
  improvements/worker-probe-p3-log.md (7b1006a, NOT-RUN). PROBE-S2:
  improvements/worker-probe-s2-log.md (71 lines, untracked).
- AMEND4 landed state at HEAD e912ad4: items 1-10 landed (cc964b2,
  c1ea773, 62b740e, 72120aa, b44a5ea, 49081aa, af0fa87, 44c15bb,
  e912ad4); items 11, 12 open.
- Code refs verified by me: scripts/zen_dom.py locate 567-588,
  hit_check 820-851, eval subparser 1153/1171; scripts/a11y.py
  observe 500-node/2s/80-item/truncated; scripts/code_exec.py
  DOM_WINDOW_CLASS='chromium'; scripts/cu.py observe 920 (max_width
  960), observe_screen 974 (max_width 960), CLI default 960 line
  2758, JPEG re-encode 839-840; scripts/first_action.py:656
  max_width=1920 (D1 V4); git ls-files scripts/first_action.py
  (tracked).
- Error file: J37 lines 832-837 (patch 6.627 vs threshold 6, JPEG edge
  smear, photographic background); G30 lines 302-310 (64/75 px);
  J40 (+45,+12 px, ok returned).
- Numbers used: E2 17/29 first-try 58.6% (Wilson 40.7-74.5% per CB,
  n=29, not held-out), pointer error 0.5-0.9 px, 29/29 executed;
  DOM 66 rects median 0.030 s, 5 clicks 0.0022-0.0053 s, verify
  0.002-0.015 s (single-source, clone2 batch 7, C1 applies); fresh
  SSH 4.43-5.29 s, mux 0.91-1.46 s, saving 3.2-3.5 s, 3.5-5x, 460x
  dead; F2b order-to-overlay 12.262 s, dispatch 11.620 s (D1 V10);
  overlay acquire 315-349 ms; CB batch math 0.9^20 12.2%, 0.9^32
  3.4% (checked); PROBE-P8 session acquire 0.01 s, content eval
  0.00 s, context switch fail 0.00 s; Y1b 14/20, 3 real fails 1e/2a/2b
  (9d9bd63); CB JSONL 199 lines, p50 order-to-overlay 337.5 ms, p50
  wrapper 2.288 s, 167 ok / 32 not ok (CB-reported, unverified
  from the VM).

## 10. What I did not verify (honest limits)

- CB's laptop-local numbers (act-now JSONL summary, installed-copy
  line numbers) are CB-reported; I verified the repo-side analogues
  (V-F5 to V-F10) but did not read the laptop files.
- PROBE-DOMZEN has not landed (V-F11); the DOM bench timings stay
  single-source until it does.
- I did not re-run the DOM bench or the fixture bench (no .venv, no
  selenium, no Firefox on this VM; V-F3).
- CB's Wilson interval (40.7-74.5%) is CB-computed; I did not
  recompute it. It does not affect any verdict (E2 is directional on
  n=29 either way).
- The AMEND4 item 12 lane state is "(pending)" in its driver log; I
  did not chase the lane directly.

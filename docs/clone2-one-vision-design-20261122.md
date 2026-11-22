# One-vision design: DOM grounding for the 2-vision benchmark

Date of work: 2026-11-22, local time Asia/Saigon. Batch 9 task 1.

This report is generic. It contains no personal information, no real
names, no email addresses, no accounts, no tokens.

No test was run for this document. The work is source reading only:
the sweep report, the batch 8 task 1 script and workflow, the batch 8
task 2 bench report, the batch 7 task 2 report, and the batch 8 task 3
C12 probe procedure, plus two direct page reads named below (Turbo
README crawled 2026-11-21 21:40 UTC, BotCircle issue 8 crawled
2026-11-21 21:41 UTC). Every external claim carries its source and
date. Every claim about our own stack carries a file and line
reference. Turbo-Browser-MCP benchmark numbers are not cited here as
evidence: they are UNVERIFIED on this machine. The one exception
is the README's own snapshot-size table figure in section 4.1
(168 vs 12,825 chars), cited only as the shape of the claim, not
re-run here.

## 0. Design in one paragraph

One agent vision per task. The agent spends its single vision reading
one numbered inventory text, the one-shot DOM harvest of both clone
windows. Everything after that is programmatic DOM reads done by the
script, no second vision: plan-once from the inventory, a guarded send
chain per clone (scroll first, HCU guard on post-scroll geometry, real
pointer click, focus check, type, V1 value readback, Enter), a V12
outcome gate after each send (the sent bubble in the thread DOM), and
an exactly-once ledger keyed by submission key. The outcome is scored
by whether the message is in the thread, never by whether a point fell
inside a box. Coordinates come from one chain, screen = window origin +
(mozInnerScreen + rect center) * dpr / monitor_scale, in logical px,
with dpr and monitor scale both 1 on the measured geometry (section
3, corrected in the batch 9 fix pass: the first version multiplied
the whole sum by dpr * monitor_scale, which is unit-wrong). Three mechanisms
are ported from Turbo-Browser-MCP (Show HN 2026-11-15): onlyChanged
delta snapshots, batch_actions with an expect outcome check, and
submissionKey exactly-once with a default-on submit guard and click
aftermath reporting. Only the mechanisms transfer. Its driver does
not: it runs Chromium over CDP, and CDP is dead on Firefox and Zen.

## 1. The vision budget, stated exactly

The benchmark script today records visions_used 2
(tests/two_vision_bench.py, results dict in main()): VISION 1 is the
agent reading the inventory text, VISION 2 is the agent looking at
both threads once at the end. The script's V12 gates check the same outcome by DOM read
(GATE_JS, tests/two_vision_bench.py:156), but removing VISION 2 is
CONDITIONAL, not decided. Dated note, fix pass 2 (2026-11-22,
script commit 00ce862, 1939 lines): the passage below was written
when the gate was a presence check only. That is no longer true.
The gate IS textNew now (built f49851f, hardened c1b623b, fix pass
2 00ce862): it passes only on exactly one NEW bubble past the
pre-Enter gate_baseline (the before-snapshot count in main() is
recorded evidence only, the gate never consults it), settles a
full second after first sighting it, and a double append,
synchronous or delayed 700 ms, fails as duplicate-bubble. The
original reason for textNew still stands (Turbo's README: "textMatches also matches text that
was already on the page before the click, so prefer textNew for
verifying a submit"). What remains is live proof: textNew is
proven on the fixture only, and VISION 2 stays until a live run
passes with textNew. The two false PASS shapes below are both
closed as builds, live proof owed for both. (1) A retry with the
same fixed plan (same run_id) after a crash between the Enter
keypress and the ledger mark no longer scores PASS having sent
nothing: the outcome rule requires 2 fresh sends this run unless
--allow-resume is passed (tests/two_vision_bench.py:1883-1892,
sends_this_run), the run registry refuses a reused run_id in a
fresh workdir before the browser starts, and the pre-send
reservation leaves status "sending", which a later run refuses.
The old rule main() counted "skipped-already-sent" as sent
(tests/two_vision_bench.py:831 in the pre-fix-pass numbering);
that counting is gone. (2) The gate used to run against the
current window's thread DOM only and never compare across windows;
the cross-window check is now built (cross_window_check,
tests/two_vision_bench.py:1183: each thread must contain only its
own message, foreign bubbles matched by containment on the raw
texts), and the outcome rule also fails the run when a thread
vanished after the gates or holds no bubble with its own message.
(The same-URL case is closed: validate_plan refuses two windows
on the same URL, tests/two_vision_bench.py:1283, added by the
batch 9 task 2 fix pass.) Before the budget can drop to 1 vision,
one thing must still happen: textNew and the cross-window check
must be proven on a live page, not only on the fixture. The
selector-proving step that must happen before the live run is a
live harvest-first read (--mode harvest with the live plan)
proving the message input is visible and named on the live page;
the harvest does NOT verify thread_selector or bubble_selector
(they are only touched inside send_one via the gate, after
typing), so the first V12 gate is the first real selector test.

The design budget is therefore, as a target once those conditions
are met:

- 1 agent vision per task: read the numbered inventory text and pick
  the two message inputs. Nothing else is ever shown to the agent as
  an image or a page.
- 0 additional visions. Verification is programmatic: one cheap DOM
  read per check (0.002 to 0.015 s in batch 7 task 2,
  docs/clone2-dom-grounding-20261122.md section 2; 0.0045 to 0.0345 s
  in batch 8 task 2, docs/clone2-dom-bench-2win-20261122.md section 3).
- A fresh snapshot is taken only when a verify read disagrees with
  the expected state, and then only as a delta (section 4.1). The
  harvest evaluate still runs in full; only what the agent is shown
  is the delta. The agent merges the delta into the inventory it
  already holds by keeping the previous snapshot in context and
  reading the delta against it (Turbo's model); a delta alone is not
  a usable inventory.
- Until then: 2 visions. VISION 2 is retained as the independent
  witness, and the budget stays at 2.

This is the same structural win the E1 experiment measured
(docs/research/2026-11-21-e1-planning-vs-execution.md): observations
are the expensive unit, so batch them. One snapshot drives the whole
task; the batch 7 bench proved one snapshot drives 5 real pointer
clicks, all 5 landing, and the batch 8 task 2 bench proved the same
shape across two windows (5 clicks per window, all landed, both
runs).

## 2. Why this design, in one incident

The design exists because of one proven failure shape, hit
independently in the field. BotCircle issue 8 (GitHub, 2026-10-22,
Sr-0w/BotCircle issue 8, "Computer use: clics a l'aveugle / mal
positionnes", crawled 2026-11-21 21:41 UTC) records a bot whose clicks
never reached their target: a click at (710,110) meant for Home
missed it entirely (real Home about (70,180)), and the y=747 clicks
landed on the dock (dock icon centres y about 775). Every output
reported ok:true with a screenshotId, and the screen stayed
unchanged. The post-action
capture was never shown to anyone (the UI renders the image only for
explicit screenshot calls, never after an action), and the clicks
were spaced with suspicious regularity, which suggests the model
never saw the image, or read it badly. That is the same shape as the team's own
click incident (improvements/worker-coord-click2-log.md): the model
clicked (250,1037), 64 px above the real input field, and all five
attempts inherited the wrong point. The design's answer to both is
the same: never ground from a screenshot, never score by point in
box (M1, arXiv:2610.36831, Oct 2026, cited in the click2 log), and
always verify the outcome in the DOM. A click that lands is not a
confirmed submission; a bubble in the thread is.

## 3. The coordinate chain

### 3.1 The chain

For a target with viewport rect center (cx, cy) in CSS px:

```
screen = window_origin + (mozInnerScreen + rect_center) * dpr / monitor_scale
```

in logical px, where window_origin is the Hyprland window origin
(the `at` field from `hyprctl -j clients`, re-read per call because
the window can move; `hyprctl -j monitors` gives the monitor box and
scale, not the window origin), mozInnerScreen is
[window.mozInnerScreenX, window.mozInnerScreenY] read live from the
page, rect_center is (rect.x + rect.width / 2, rect.y + rect.height
/ 2) from getBoundingClientRect, dpr is window.devicePixelRatio, and
monitor_scale is the Hyprland monitor scale (scripts/cu.py:990
carries monitor_scale in the observation meta on
origin/todolist-push). The unit of the result is logical px, the unit
the C12 click driver consumes: it normalizes screen points against
the monitor box from `hyprctl -j monitors`, which is in logical px
(C12 procedure section 4, driver normalization
nx = round((gx - mx) / mw * 1000000)).

This is the Case B chain from the C12 probe procedure
(docs/clone2-c12-probe-procedure-20261122.md section 6): the amend
code as written treats mozInnerScreenX/Y as absolute screen
coordinates (scripts/zen_dom.py:367-380, viewport_origin(), on
origin/todolist-push, documents the return as "the viewport origin
in screen coordinates"), while the calibration-e2 report measured
live on the laptop 2026-11-21 that they are window-relative
(240, 8) (docs/calibration-e2-report.md:22). The C12 probe decides
between the two with live clicks; its Outcome B and Outcome E1 both
conclude Case B wins and prescribe the fix: viewport_origin()
must return the window origin plus mozInnerScreenX/Y, with the
window origin read from hyprctl at call time, plus a DPR term.

Correction, batch 9 fix pass: the first version of this design
copied the C12 Outcome B prescription ("multiply by
window.devicePixelRatio and the meta monitor_scale") as a product
applied to the whole sum including the window origin. That
prescription is unit-wrong, and this design departs from it
deliberately. The parts: window_origin, from `hyprctl -j clients`
`at`, is already logical px (factor 1, it must never be scaled);
mozInnerScreen + rect_center is CSS px, logical px = CSS px * dpr /
monitor_scale, physical px = CSS px * dpr. The old formula applied
dpr * monitor_scale to the whole sum, which matches neither consumer
in either unit. On the normal Wayland case (dpr equals the monitor
scale for a window on one monitor) the CSS part needs factor 1 and
the origin needs factor 1, so the correct logical-px point is just
the unscaled sum; the old formula gives 4x on a scale-2 monitor.
The amend's own fastpath agrees the origin is never scaled:
dom_rect_to_image_point applies its scale factor to the rect center
only (screen = viewport_origin + center * scale_factor,
scripts/fastpath.py on origin/todolist-push). On the E2 geometry
both dpr and monitor scale are 1, so the old and corrected formulas
give identical numbers, which is exactly why the error was invisible
there. The corrected formula is untested at any scale other than 1:
do not close C12 on it until a live run at scale other than 1
evaluates it.

### 3.2 Status of the chain, stated honestly

The chain is ADOPTED, not yet proven on the laptop. The C12 probe
procedure is written but has not run: the live lane was busy
(BASELINE2) and the probe runs on the laptop, never on this VM.
The design uses the Case B chain because the only live measurement
(E2, 2026-11-21) supports it, and because the amend's Case A chain
fails closed on the E2 geometry (every point lands about 2500 px
off, dom_rect_to_image_point raises ValueError, no mis-click, but
the DOM-first path is dead). If the probe returns Outcome A (Case A
wins, all five Case A clicks land), this document must be amended:
the chain collapses to screen = mozInnerScreen + rect center, and
viewport_origin() stays as written. Until the probe runs, no live
click may use this chain. That gate is a precondition, not a
footnote. One limit on the Outcome A clause above: on the E2
geometry Outcome A cannot occur (section 3.4: the decision runs
through Branch 2 and Outcome E, because all five Case A points fall
outside the monitor box, so Step 4 never runs and the probe can only
return Outcome E1 or E2 there). The amendment clause is therefore
near-dead for the geometry this design is written against, and the
probe would need a different window placement to test Case A at all.
An Outcome A return would also invalidate the section 5 worked
example numbers, not just require a live recompute.

### 3.3 The DPR term, one open detail

The DPR term is carried per part, not as a multiplier on the whole
point (section 3.1): the window origin is never scaled, and the CSS
part takes dpr / monitor_scale. That per-part placement is settled
by the unit analysis in section 3.1, and it corrects the C12
Outcome B prescription as written, which multiplies the whole point
by dpr and monitor_scale. What remains UNRESOLVED is the formula
itself: it has never been evaluated at dpr or monitor scale other
than 1, and the C12 procedure still carries the unit-wrong
prescription, so the procedure needs a dated correction before the
probe closes. On the E2 geometry both values are 1, so the term is
a no-op there and every worked number below is exact. The probe
records DPR and monitor scale live for every outcome (C12 procedure
section 11, DPR branch), and the first live run that records a value
other than 1 must pin the formula before clicking. Do not close C12
until the DPR term exists or scale == 1 and DPR == 1 are asserted
on the target monitor.

### 3.4 Worked example, the C12 grid target

From the C12 procedure (section 6, E2 geometry, example values,
recompute live): window origin (2509, 914), MX, MY = (240, 8),
viewport 1615x1160. Target T01 rect center (161.5, 162.4) in
viewport CSS px. Case A screen = (401.5, 170.4). Case B screen =
(2910.5, 1084.4). The difference is exactly (2509, 914), the
window origin. On the E2 monitor (eDP-2, box x 2464 to 4384,
y 902 to 2102) the Case A point falls outside the monitor box, so
the probe's monitor-box rule forbids clicking it, and the decision
runs through Branch 2 and Outcome E instead. The two cases differ
by thousands of px, so one click decides it; five targets make it
robust.

## 4. The three ported mechanisms

Turbo-Browser-MCP: repository created 2026-11-14, Show HN 2026-11-15
("Show HN: Turbo-Browser-MCP, Batch forms, DOM deltas and submit
guards for MCP", Hacker News), 136 stars at the sweep crawl
2026-11-21 (docs/clone2-last30days-sweep-20261122.md section 3.1),
MIT license, 11 tools, Playwright MCP server. All mechanism
descriptions below were re-read directly from its README on
2026-11-21 21:40 UTC (https://github.com/Tthanh2k6/turbo-browser-mcp),
not taken from the sweep report on trust. Its benchmark numbers are
not cited anywhere in this document.

### 4.1 onlyChanged delta snapshots: the re-observation mechanism

Turbo: inspect_compact returns a size-capped snapshot of elements,
and with onlyChanged true returns only the elements that changed
since the last snapshot, with new refs marked with `*` and removed
refs listed on a `Removed:` line. An unchanged submit-like button
is still listed so the model knows it exists and the submit guard
still blocks it. In our architecture the guard is vacuous (section
4.3.3), so the listing rule carries over only for the model's
awareness, not for any guard. The sweep measured the shape of the win in the
README's own table (Snapshot after a click, onlyChanged: 168 chars
against 12,825 chars full ARIA), but that figure is the README's,
not re-run here, and is cited only as the shape of the claim.

Our mapping: the re-observation step in the step-6 loop hygiene gap.
Today the benchmark script has no delta: a stale inventory means a
full re-harvest (tests/two_vision_bench.py harvest_window,
line 1126, one evaluate per window, pooled median 0.0112 s for 66
elements in batch 8 task 2). The harvest is already cheap in time,
so the delta is a token saving, not a time saving: the win is
context size on a mutating page, where a full re-harvest replays
every element. The port:

```python
def harvest(driver, label, only_changed=False, prev=None):
    """One evaluate per window. With only_changed, compare against
    prev (keyed by ref) and return only added, removed, and changed
    elements, plus counts. Unchanged submit-like controls are still
    listed so the model knows they exist. The agent merges the delta
    into the inventory it already holds by keeping the previous
    snapshot in context and reading the delta against it (Turbo's
    model); a delta alone is not a usable inventory."""
    ...

def delta(prev, cur):
    """Return {'added': [...], 'removed': [refs], 'changed': [...],
    'unchanged': n}. A ref is changed when its rect, name, or
    visibility differs by more than the guard tolerance (2 px)."""
    ...
```

Rules carried over from Turbo: refs come from the latest snapshot
only (Turbo fails a ref from a previous document at once, checked
by frame loaderId, and lists the 3 nearest current refs for a
missing ref); a ref whose element now shows different text fails
until a new snapshot reports it. Our equivalent is the D3 gap (ref
stability on a mutating Messenger page, now built in the script;
tests/two_vision_bench.py format_inventory, line 497, warns refs
must not transfer between runs). The delta does not fix D3; it
bounds the cost of the re-harvest D3 forces.

### 4.2 batch_actions with expect: the batched execution mechanism

Turbo: batch_actions runs an ordered list of clicks, key presses,
form steps and page reads as one call, with an expect check
(urlMatches, textMatches, textNew, selector) evaluated after the
steps. textNew counts only elements whose text matches and did not
match when the batch started, so it verifies a submit rather than
matching text that was already on the page. The result carries
submitVerified and evidence (the new URL, a text snippet such as a
receipt number, or the matched selector). If nothing shows up in
time the result is submitVerified false with a reason. A click that
landed is not a confirmed submission: use expect. An expect.selector
that is not a valid selector never matches.

Our mapping: the plan-once send chain plus the V12 gate, which is
the same shape with different names. The script already builds the
whole send sequence from one inventory and runs it with stop at
first failure (tests/two_vision_bench.py main(), send chain loop;
workflow docs/two-vision-benchmark-workflow-20261122.md section 1).
The V12 gate (GATE_JS, tests/two_vision_bench.py:156) checks the
exact message text as a bubble in the thread DOM, which is Turbo's
textMatches; the port adds Turbo's textNew distinction, which our
gate now has, built in batch 12 task 2 (script commit f49851f,
hardened in fix pass c1b623b and again in fix pass 2, commit
00ce862): the gate counts only bubbles whose text appears after
the pre-Enter gate_baseline, and settles a full second after
first sighting one, so a delayed second append fails as
duplicate-bubble. Dated note,
22/11, fix pass: the built baseline is deliberately stricter
than Turbo's spec ("did not match when the batch started"). The
operative baseline is the count measured right before Enter
(gate_baseline in send_one); before_count, the batch-start
snapshot taken in main, is recorded evidence only and is never
consulted by the gate. A matching bubble arriving after batch
start but before Enter counts as new under Turbo's spec but does
not satisfy the built gate. The built gate is strictly stricter,
safe direction, and the stale-bubble property holds under both.
The main() comment and the COUNT_JS comment that claimed the
gate used the before-snapshot were corrected in the same fix
pass. The gate is appearance-based, not causal: it proves a
bubble with the exact text appeared after the baseline, not
that our Enter caused it. Turbo's README states
why the distinction exists: "textMatches also matches text that
was already on the page before the click, so prefer textNew for
verifying a submit: it counts only elements whose text matches and
did not match when the batch started." The port:

```python
def run_batch(driver, windows, steps, expect):
    """One program from the inventory: for each window, scroll first,
    HCU guard on post-scroll geometry, real pointer click, focus
    check, type, V1 value readback, Enter. After each send, evaluate
    expect against the thread DOM. Returns {'submit_verified': bool,
    'evidence': {...}, 'steps': [...]}. Stops at the first failure;
    later steps are not-executed."""
    ...

expect = {
    "text_new": {"thread": "#thread", "bubble": ".bubble",
                 "text": message},   # bubble text absent at the pre-Enter gate_baseline
    "focus": {"ref": input_ref},     # activeElement is the input
    "value": {"ref": input_ref, "text": message},  # V1 readback
    "timeout_ms": 5000,
}
```

The expect kinds map one to one: textMatches is our current V12
gate; textNew is the V12 gate with a pre-Enter baseline (not a
batch-start snapshot, see the dated note above); selector is
the thread and bubble selectors from the plan
(docs/two-vision-benchmark-workflow-20261122.md section 5, step 0);
urlMatches has no Messenger equivalent and is not ported. The port
also adds a cross-window check, which Turbo does not need (one tab
per call): after both sends, each thread must contain only its own
message and the two threads' bubble sets must differ. The
failure table stays the script's
(docs/two-vision-benchmark-workflow-20261122.md section 6):
v12-timeout means the message may have landed unseen, the intent
is marked failed-unverified, and a retry of the same intent is
refused.

### 4.3 submissionKey exactly-once, submit guard, click aftermath

Turbo bundles three controls under Safety, and this design ports
all three together because they only work together.

#### 4.3.1 submissionKey exactly-once

Turbo: batch_actions takes a submissionKey, for example
"photo-contest:2026-11-15:entry-1". Every allowed submit is
appended to a JSONL ledger (~/.turbo-browser-mcp/submissions.jsonl
by default, or TURBO_BROWSER_LEDGER, or ledgerPath inside the save
root). A later call with the same key is refused with blockedBy
"ledger" unless allowDuplicate is true.

Our mapping: the script's Ledger (tests/two_vision_bench.py:319,
mark at line 386, status at line 383), keyed by intent id
(run_id + window label), written to <workdir>/ledger.json, plus the
V12 pre-check before every send regardless of ledger status
(send_one, tests/two_vision_bench.py:594). The submission key for
the benchmark is the intent id itself, for example
"bench-20261122-001:clone1" (illustrative only; the script's real
format is "bench-" + UTC timestamp + "-" + 6 hex chars, default_plan,
tests/two_vision_bench.py:1051-1054, so do not copy the example into
an implementation).
The port keeps the script's shape and adds Turbo's refusal
semantics as an explicit step status (already present as
retry-blocked-unverified in the workflow failure table).

#### 4.3.2 The submissionKey caveat, carried in full

Exactly-once holds only when the call returns. The Turbo README
Safety section states it plainly, quoted here because the caveat
is the mechanism's honest boundary: "The ledger is written only
when the call returns. If the call throws after the page already
sent the submission (for example a navigation timeout), nothing
is recorded. Check the site before re-running." A throw after send
leaves the ledger empty and a retry double-sends. The ledger is
also a per-machine file, so it does not cover two clones on two
machines or a wiped home directory.

Our stack has the same hole, in the same place, and this design
does not hide it. The script marks an intent sent only after its
V12 gate passes (send_one, ledger.mark after the gate loop), so a
crash between the Enter keypress and the mark leaves the ledger
empty and a retry re-sends. The script's mitigation, built in the
fix pass, closes the narrower case: a v12-timeout marks the intent
failed-unverified and a later run with the same intent refuses to
re-send it, because the message may have landed unseen
(tests/two_vision_bench.py send_one, failed-unverified block;
verified live as fix2-wrongsel, run 1 FAIL v12-timeout, run 2 FAIL
retry-blocked-unverified, no second bubble). That mitigation
depends on the process surviving long enough to write the mark.
A process death between send and mark is still unhandled by the
v12-timeout mitigation alone. Dated note, 22/11, fix pass: the
residual gap is now closed by the pre-send reservation, BUILT in
batch 12 task 2 (script commit f49851f, hardened in fix pass
c1b623b): the intent is written as "sending" after the V1
readback and before Enter, then reconciled to "sent" or
"failed-unverified" after the gate; a later run finding
"sending" refuses with retry-blocked-reservation. A failed
retry never overwrites a "sent" or "sending" record, and the
run registry refuses a reused run_id in a fresh workdir. What
remains open is live proof, and the cross-machine case: the
reservation closes the process-death gap only when the same
ledger is reused, and the registry is per-machine. A
server-side idempotency key, if the target ever offers one,
is still not ported. Until the live proof exists, the honest
guarantee is the script's own docstring: within one session,
a retry never re-sends a message the V12 pre-check can see
in the thread.

The same caveat applies to our ledger's scope. Turbo's ledger is
per-machine; ours is per-run workdir (DEFAULT_WORKDIR
/tmp/two_vision_bench, tests/two_vision_bench.py:53, shared by
runs unless --workdir is passed), which is narrower still: a fresh
page load with an empty thread re-sends a recorded intent once,
by design, because the bubble is genuinely absent. The ledger
must be passed explicitly per run (--ledger) and must never be
shared between two live runs.

#### 4.3.3 Submit guard on by default

Turbo: allowSubmit is false by default. Final actions that look
like Submit, Publish, Send, Post, Apply, Confirm or a payment
trigger are blocked unless allowSubmit true is passed per call or
--allow-submit at startup. The label list covers Korean, Japanese,
Chinese and Vietnamese equivalents. Affirmative buttons inside a
dialog count as commits (blockedBy "modal"). A network guard, off
by default, stops non-GET navigations and same-site POST/PUT/PATCH/
DELETE while submitting is not allowed (blockedBy "network"). Every
blocked result says which mechanism stopped it.

Our mapping: the script has NO submit guard today, and the
benchmark's send IS the commit (Enter in the message input sends
the message), so the guard cannot be copied literally. More sharply,
in this plan-once, script-executed architecture the guard as scoped
to the plan is vacuous: the script has no code path that performs an
action not in the plan. main() only ever executes the send chain
over plan["windows"]; find_input picks the input by name
programmatically (tests/two_vision_bench.py:524). The set of actions
the script can perform is exactly the plan, so a guard that blocks
off-plan actions can never trigger. This holds in live mode too, not
just fixture mode: in live mode the plan is also the whole action
set. The live URL gate already refuses off-fixture plans, and the
guard adds no protection beyond it. The port therefore scopes the
guard to plan validation: refuse a plan that contains a commit
outside the plan's two intents, and say so. The real controls are
the URL gate and the fixed chain. In Turbo the guard has teeth
because the model calls tools directly and can click any
submit-like element at any time; in this architecture the agent has
no such path. The design ports the name, not the function, unless
scoped to plan validation as above. Concretely:

```python
class SubmitGuard:
    """Validates the plan: blocks a plan that contains a final-commit
    action outside the plan's two intents. A commit is: a click on an
    element whose role/label matches a submit-like label (Submit,
    Send, Publish, Pay, Confirm, and the target page's equivalents),
    Enter in a form, form.submit(), or a click inside a confirmation
    dialog. The plan's two sends are allowed because they are the
    plan's intents; anything else is blocked with blocked_by
    'label', 'modal', or 'network'."""
    def allow(self, action, plan): ...
```

The label list must be derived from the target page, not copied
from Turbo's Korean portal list. What remains as a live-run
requirement is plan validation, not a runtime guard: in fixture
mode and in live mode alike the plan is the whole action set, so a
runtime guard is vacuous in both. The live gate already refuses a
plan whose URLs are not the fixture without both --live and
--confirm-live (tests/two_vision_bench.py main(), URL gate), which
is the real protection at the run level.

#### 4.3.4 Click aftermath reporting

Turbo: after a click, double click or key press with returnSnapshot
or observeAftermath, the server waits up to 150 ms for a navigation
to start, then for domcontentloaded if one did, then until the DOM
has been quiet for 80 ms and no request younger than 1.5 s is
pending, at most 800 ms. There is no fixed sleep. The result has
outcome: navigated (the URL changed), changed (the DOM changed),
or none. This is the cheap non-vision verify step.

Our mapping: the script's verify read after every action. The HCU
guard already re-reads the target's live geometry, visibility and
hit test before input (hcu_guard, tests/two_vision_bench.py:650,
2 px move tolerance), and after the click the focus check (V3,
activeElement) and the V1 value readback confirm the effect. The
port adds Turbo's settle vocabulary to the click step: after a
pointer click, wait for the DOM to go quiet (one evaluate polling
for mutation quiescence, at most 800 ms, no fixed sleep), then
report the aftermath as one of navigated, changed, or none, where
"changed" is read from the page's own state (the thread DOM, the
input's value, the focus). The measured cost of one such read is
0.002 to 0.015 s (batch 7) and 0.0045 to 0.0345 s (batch 8 task 2),
so the settle wait, not the read, dominates when the page is slow.
The aftermath is evidence for the expect check in section 4.2, not
a second observation.

## 5. Worked example: the 2-vision benchmark, both clones

The fixture inventory (docs/two-vision-benchmark-workflow-20261122.md
section 5, step 1) gives, per window:

```
Window clone1: 4 inputs+buttons
[1] textbox 'Message' ref=#msg-input rect=(20,238,340x39) center=(190,257) visible=True focused=False
[2] button 'Send' ref=#send-btn rect=(364,238,59x39) center=(394,257) visible=True focused=False
```

The agent's one vision reads this text and picks [1] in each
window. The rest is program.

Geometry used below is a worked example, not a live measurement:
the fixture rects are real (measured in the dry-test runs), the
window origin (2509, 914) and mozInnerScreen (240, 8) are the E2
geometry values from the C12 procedure, and DPR and monitor scale
are 1. Recompute live on the laptop; the formula is the point, the
numbers are the illustration.

### Clone 1

1. Rect center, viewport CSS px: (190, 257).
2. mozInnerScreen, live read: (240, 8).
3. Window origin, hyprctl, re-read per call: (2509, 914).
4. Screen point: (2509 + 240 + 190, 914 + 8 + 257) = (2939, 1179).
   DPR 1 and monitor scale 1, so no scaling step applies. The exact
   live center is (190, 257.37), so the exact screen point is
   (2939, 1179.37); the design uses the inventory's rounded display
   (190, 257) and (2939, 1179), which is what the script clicks,
   since click_at truncates to int.
5. Click aftermath: pointer click at (2939, 1179), settle at most
   800 ms, DOM quiet, outcome changed (focus moved to the input).
6. Focus check V3: activeElement is #msg-input. If not, stop:
   focus-failed, nothing typed.
7. Type "BENCH-TEST clone1 <run_id>" with real keys. V1 readback:
   value equals the message (for a contenteditable input, innerText
   instead; tests/two_vision_bench.py send_one, value vs innerText
   branch). If not, stop: value-mismatch, Enter never sent.
8. Enter. V12 gate with expect textNew: poll the thread DOM for a
   bubble whose text equals the message and was absent at the
   pre-Enter gate_baseline, up to 5 s (v12_gate_s from the plan),
   settling a full second after first sighting it. On pass,
   mark the submission key (the intent id; "bench-20261122-001:clone1"
   is illustrative, see section 4.3.1) sent in the ledger. On
   timeout, mark failed-unverified and refuse any later retry of the
   same key.

### Clone 2

Identical, with its own window origin. The two clone windows are
separate windows in one browser instance (one Marionette session;
two windows share it at no extra cost beyond the switch, median
0.0463 s round trip in batch 8 task 2), so clone 2's window origin
(win2_x, win2_y) is read separately from hyprctl and must not be
copied from clone 1. mozInnerScreen is read live per window, like
the origin; the (240, 8) values are the E2 example values, not
values to copy from clone 1. Its screen point is
(win2_x + 240 + 190, win2_y + 8 + 257) with its own origin values.
The submission key is the intent id (illustrative
"bench-20261122-001:clone2", see section 4.3.1). The V12 gate
runs against clone 2's thread DOM, not clone 1's.

### Outcome

PASS iff both V12 gates pass, which is Turbo's submitVerified with
evidence (the two new bubbles). The agent's vision count for the
whole task is 1, once the conditions in section 1 are met; until
then it is 2, with VISION 2 retained. The program's DOM reads: 2
harvests (one evaluate each, pooled median 0.0112 s in batch 8 task
2), 2 scroll-first guards where needed, 2 focus checks, 2 V1
readbacks, 2 V12 gate polls, plus 2 window switches. The measured
benchmark flow for both windows is 0.72 to 1.21 s (batch 8 task 2,
section 3); the script's own happy-path dry runs are 6.18 s and
8.45 s wall including browser launch 1.01 to 3.52 s and Marionette
attach 2.76 to 2.79 s in the two happy-path dry runs (2.7903 s and
2.7635 s, workflow section 7); the 2.71 s figure is from the batch 8
task 2 bench (attach 2.7050 to 2.7471 s), a different measurement.
Session start dominates the wall; the actions themselves are under
a second.

## 6. What transfers and what does not

| Turbo-Browser-MCP item | Transfers? | Our form |
| --- | --- | --- |
| onlyChanged delta snapshots | Yes, mechanism | harvest(only_changed=True) plus delta(), section 4.1 |
| batch_actions with expect | Yes, mechanism | run_batch() with expect textNew, section 4.2 |
| submissionKey exactly-once | Yes, mechanism, with the caveat in 4.3.2 | Ledger keyed by intent id plus V12 pre-check, section 4.3.1 |
| Submit guard on by default | No, vacuous in this architecture; plan validation only | SubmitGuard scoped to plan validation, section 4.3.3; real controls are the URL gate and the fixed chain |
| Click aftermath reporting | Yes, mechanism | Settle plus DOM read after each click, outcome navigated/changed/none, section 4.3.4 |
| Stale-ref fail fast, 3 nearest refs | Yes, pattern | D3: fail fast on a stale ref, list nearest current refs |
| Fill value readback with mismatch | Yes, already built | V1 check, tests/two_vision_bench.py send_one |
| Playwright driver, CDP transport | No | CDP removed in Firefox 141 (Bugzilla 1882096, RESOLVED FIXED); our stack is Marionette plus BiDi. The repo's BiDi wrapper scripts/zen_cli.py already speaks BiDi to Zen 1.24.2b (verified 2026-11-18) |
| CDP DOM.getBoxModel, Accessibility.getFullAXTree | No | No CDP endpoint on Firefox or Zen; geometry comes from getBoundingClientRect, semantics from the Selenium 4.53 accessibility snapshot (batch 7 task 2, section 4) |
| Ledger file location (~/.turbo-browser-mcp/submissions.jsonl) | No, shape only | Our ledger is per-run workdir, <workdir>/ledger.json |
| Submit label list (Korean portal labels) | No, derive from the target page | Section 4.3.3 |
| Benchmark numbers (turns, tokens, seconds) | No, UNVERIFIED here | Not cited as evidence, except the one qualified README figure in section 4.1 |

One hard constraint governs the whole port: Firefox 160 allows
exactly one active remote session per browser instance, across
protocols (batch 7 task 2, section 0, proved in all four bench
runs; batch 8 task 2, finding 5). The design is Marionette-only
for real input. BiDi is the grounding path (fastest rect reads,
0.006 to 0.054 s per run median for 66 elements in batch 7 task 2),
but no flow may need both protocols at once on one browser.
Sequencing for a live run that needs both is unspecified (gap D1,
tests/two_vision_bench.py TODO). BiDi session.new costs 1.51 to
2.77 s on a fresh browser and about 0.014 s warm, so the BiDi win
is in rect reads and DOM clicks, not in session start.

## 7. Open items, what this design does not decide

- C12 probe must run on the laptop before any live click uses the
  chain in section 3. If it returns Outcome A, amend this document.
- VISION 2 removal is conditional (section 1): textNew in the V12
  gate plus a cross-window check are BUILT and fixture-proven
  (batch 12 task 2 f49851f, hardened in fix pass c1b623b and
  again in fix pass 2, commit 00ce862); what remains is proving
  them on a live page before the budget drops to 1 vision. Until
  then VISION 2 stays. The selector-proving step is a live
  harvest-first read proving the message input is visible and
  named on the live page; the harvest does NOT verify
  thread_selector or bubble_selector, so the first V12 gate is
  the first real selector test.
- Pre-send reservation (section 4.3.2): write the intent as
  "sending" before the keypress, then reconcile to "sent" or
  "failed-unverified" after the gate; covers the process-death case.
  BUILT in batch 12 task 2 (script commit f49851f, hardened in
  fix pass c1b623b, hardened again in fix pass 2, commit 00ce862:
  reserve() is atomic under one lock, "sent" is terminal in the
  ledger state machine, every mark binds message, URL and
  selectors), fixture-proven by the driver test and the
  fix-pass driver F1/F2/F3. Live proof still owed.
- DPR term (section 3.3): the per-part placement is now settled
  (origin never scaled, CSS part takes dpr / monitor_scale), but the
  corrected formula is untested at any scale other than 1, and it
  departs from the C12 Outcome B prescription, which needs a dated
  correction in the C12 procedure.
- Live Messenger selectors: thread selector, bubble selector, and
  the message input's real ref must come from the coordinator. The
  V12 gate requires exact textContent === text and the default
  bubble selector is fixture-shaped; a live plan MUST override
  bubble_selector (workflow section 5, step 0).
- D6, one vs two instances: this design uses one instance, two
  windows. --instances two is refused by the script until two
  instances exist (tests/two_vision_bench.py main(), instances
  refusal). Two instances would need a second Marionette attach,
  which the one-session rule forbids on one browser but allows
  across two browser processes.
- D1, BiDi/Marionette handover: no protocol exists under the
  one-session constraint. The design stays Marionette-only.
- D3, ref stability on a mutating page: BUILT in batch 12 task 2
  (script commit f49851f, hardened in fix pass c1b623b and again
  in fix pass 2, commit 00ce862):
  REF_CHECK_JS re-resolves the ref before input and fails fast
  with ref-stale when tag, role, name, aria-label or placeholder
  changed, and the HCU guard compares against the harvested
  center unless the page scrolled. Fixture-proven (renamed input,
  tag swap, placeholder-only rename, moved input). Live proof
  still owed.
- V11, production MutationObserver flag: BUILT in batch 12 task 2
  (script commit f49851f, hardened in fix pass c1b623b and again
  in fix pass 2, commit 00ce862):
  OBSERVER_JS arms a real observer before typing, scoped to the
  thread container, counting mutation records. The flag is
  recorded evidence only, not a pass criterion. Live proof still
  owed.
- Step-6 loop hygiene beyond the delta: prompt caching,
  diff-gated re-observation, downscale to token tier, context
  editing, low effort, adaptive waiting remain unowned
  agent-harness concerns (tests/two_vision_bench.py TODO step-6).
- Turbo-Browser-MCP benchmark numbers: UNVERIFIED here, not cited
  as evidence (except the one qualified README figure in
  section 4.1).
- No live run has happened. No Zen numbers exist; every timing in
  this document is Firefox 160.0.1 as a stand-in, measured on this
  VM. Real Zen timings are UNVERIFIED until the laptop run.

## 8. Sources

Our stack, read on this machine 2026-11-22:

- docs/clone2-last30days-sweep-20261122.md (261 lines, commit
  bd8fbdf): Turbo-Browser-MCP finding and submissionKey caveat.
- tests/two_vision_bench.py (1939 lines, commit 00ce862):
  HARVEST_JS line 72, VERIFY_JS line 127, GATE_JS line 156,
  Ledger line 319, mark line 452, reserve line 486,
  format_inventory line 497, click_at line 607,
  ensure_visible line 620, hcu_guard line 650, send_one
  line 682, harvest_window line 1126, open_windows line
  1244, normalize_file_url line 1270, validate_plan line
  1283.
- docs/two-vision-benchmark-workflow-20261122.md (1121 lines: 379
  at commit 289b219, grown by batch 9 task 2 commit e6ecdea, which
  added the live-run prerequisites checklist): plan format, failure
  table, dry-test results.
- docs/clone2-dom-bench-2win-20261122.md (371 lines): one-shot
  0.0112 s, ground_many 0.5353 s, findings 1 and 2, benchmark flow
  0.72 to 1.21 s.
- docs/clone2-dom-grounding-20261122.md (401 lines): BiDi vs
  Marionette rects, one-session rule, a11y snapshot, CDP dead.
- docs/clone2-c12-probe-procedure-20261122.md (754 lines):
  coordinate chain dispute, worked example, decision rule.
- improvements/worker-coord-click2-log.md (origin/todolist-push):
  the combined design, the click incident root cause, M1 outcome
  scoring, gaps F5/D1-D6.
- scripts/zen_dom.py:367-380, scripts/dom_act.py ground_input
  lines 38-62 and ground_many lines 64-75, scripts/fastpath.py:169
  dom_rect_to_image_point, scripts/cu.py:990 monitor_scale (all on
  origin/todolist-push, read 2026-11-22).

External, read directly 2026-11-21:

- Turbo-Browser-MCP README, https://github.com/Tthanh2k6/turbo-browser-mcp,
  crawled 2026-11-21 21:40 UTC: 11 tools, inspect_compact
  onlyChanged, batch_actions with expect and submissionKey, submit
  guard on by default, click aftermath settle, ledger caveat,
  created 2026-11-14, 74 commits, MIT license. Show HN 2026-11-15,
  Hacker News, per the sweep report.
- BotCircle issue 8, https://github.com/Sr-0w/BotCircle/issues/8,
  published 2026-10-22, crawled 2026-11-21 21:41 UTC: blind and
  mispositioned clicks, post-action capture never shown.
- CDP removal: Firefox 141, Bugzilla 1882096 (older, documented).
- M1 outcome scoring: arXiv:2610.36831, Oct 2026, via the click2 log.

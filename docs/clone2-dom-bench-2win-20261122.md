# DOM bench, 2-window shape, batch 8 task 2

Date of work: 2026-11-22, local time Asia/Saigon. All times in the
bench logs are UTC wall clock as printed by the bench script, with
elapsed seconds from a monotonic clock for every step.

This report is generic. It contains no personal information, no real
names, no email addresses, no accounts, no tokens.

## 0. Verdict first

Two headless Firefox windows in ONE Marionette session work fine for
the 2-vision benchmark shape, and the one-shot harvest beats the
amend's ground_many by a wide margin on cost: for the full visible
inventory (65 elements per window) ground_many needs 200 evaluates
(the bench's scroll-first variant; the amend's ground_many as
written cannot complete the full inventory at all, it fails fast on
the first below-fold selector, see finding 1) and 0.42 to 0.68 s per
window, while one evaluate returns all 65 rects in 0.006 to 0.17 s
(pooled median 0.011 s), about 48x faster in time and 200x fewer
evaluates. For the benchmark-shaped set (6 selectors per window)
ground_many needs 18 evaluates and 0.10 to 0.59 s per window
against 1 evaluate at about 0.01 s.

Two real limits of the amend's ground_many, both reproduced live:

1. ground_many as written FAILS on below-fold elements. Its hit
   check (elementFromPoint at the rect center) returns false when
   the center is off-viewport, so the whole batch fails fast before
   any click. In this fixture the benchmark's own input, select and
   link sit below the fold (name-input rect center y 1927.37
   against a viewport height of 814). A scroll-first variant
   (3 evaluates above the fold, 5 below it) grounds them fine.
2. A stale snapshot can misdirect clicks. The first version of the
   click step clicked straight from one snapshot per window and
   2 of 5 clicks landed on the tall spacer in BOTH windows (log
   /tmp/dom_2win_run1_stale_rect.log, clicked log
   "btn-3;btn-17;btn-42;tall;tall;", counter "clicks: 5",
   all_five_landed false). The mechanism is UNKNOWN: the stale
   code was not preserved, so the true cause cannot be verified
   from the artifacts. The bottom/top scroll story first written
   here was tested live by the redteam and is wrong: a snapshot
   taken at scroll-bottom puts the first target's center y about
   -1041, and clicking an off-viewport point raises
   MoveTargetOutOfBoundsException instead of landing on the
   spacer, and pointer clicks do not scroll the page. The fix
   used here, re-reading each target's rect immediately before
   its click (1 cheap evaluate each, 7 evaluates for 5 clicks),
   lands all 5 in both windows in both runs, so the fix stands
   on runs 1 and 2 regardless of the unknown mechanism. VISION 1
   inventory is valid only while the page does not scroll; the
   benchmark flow must re-read after any scroll.

The benchmark-shaped flow works end to end: click input window 1,
type, Enter, click input window 2, type, Enter, in 0.72 to 1.21 s
for both windows, verified by one DOM read per window (both inputs
hold their text, both stay focused).

## 1. Machine, browser, runs

- Operating system: Linux x86_64, headless virtual machine, shared
  1.5 CPU, no Wayland display and no X display in this session.
- Browser: Mozilla Firefox 160.0.1 at
  ~/workspace/tools/firefox/firefox, geckodriver 0.37.1 at
  ~/workspace/tools/geckodriver, Selenium 4.53.0 in the repo venv
  (~/workspace/tools/venv/bin/python). Window size 1280x900 set,
  viewport 1280x814 in the Marionette runs.
- Fixture: tests/dom_grounding_fixture.html, the same fixture as
  batch 7 task 2, loaded from file:// in both windows. 66
  interactive elements per window (60 grid buttons, input, select,
  link, scroll button, hidden button, translated button), 65
  visible (hidden-btn has display none, rect 0x0).
- Bench: tests/dom_bench_2win.py (new in this task). One script
  invocation is one full run: it launches one headless Firefox by
  hand with -marionette, attaches Selenium with geckodriver
  --connect-existing, opens window 2 with switch_to.new_window,
  and runs all 22 steps. Every step prints one JSON line.

Run accounting, stated exactly:

- 2 full runs, both exit 0, 22 steps each. Run 1: wall
  2026-11-21T20:18:57Z to 20:19:07Z, run_total 11.3547 s, log
  /tmp/dom_2win_run1.log. Run 2: wall 2026-11-21T20:19:19Z to
  20:19:30Z, run_total 11.0837 s, log /tmp/dom_2win_run2.log.
- 2 earlier partial runs, both preserved. Run 0: the first bench
  version crashed at the ground_many step with RuntimeError "hit
  check failed for #name-input" (log /tmp/dom_2win_run0_crash.log),
  disclosed here in section 1. The first version's set A included
  name-input; after the crash the set was split into set A (6
  above-fold buttons) and set B (3 below-fold selectors), which
  is why section 2 defines set A without name-input. Run 1 stale
  rect: a full run of the first click-step version in which 2 of
  5 clicks landed on the tall spacer in both windows (log
  /tmp/dom_2win_run1_stale_rect.log), disclosed in section 6,
  finding 2.
- No other runs. Every number in this report comes from run 1,
  run 2, or the two preserved partial logs named above. The /tmp
  tmpfs filled to 100 percent before the first run (stale Firefox
  profiles from batch 7 work, no live Firefox process); the stale
  profiles were deleted after confirming no live Firefox
  referenced them, freeing the disk to 42 percent used. The
  last30days-skill clone dirs in /tmp were left untouched.

## 2. Method: what ground_many costs

The amend is scripts/dom_act.py on origin/todolist-push.
ground_many(session, meta, selectors) calls ground_input once per
selector, and ground_input does 3 JavaScript evaluates:

1. locate: document.querySelector plus getBoundingClientRect,
   one evaluate.
2. viewport_origin: [window.mozInnerScreenX,
   window.mozInnerScreenY], one evaluate.
3. hit_check: elementFromPoint at the rect center, one evaluate.

So ground_many costs 3N evaluates for N selectors, and it fails
fast on the first ungroundable selector, before any click. The
one-shot harvest does 1 evaluate per window: one
querySelectorAll plus getBoundingClientRect for every element,
returning id, tag, rect, center, visibility for all of them.

The bench mirrors ground_many exactly (same three JavaScript
calls, same order) and counts every evaluate. The scroll-first
variant adds, per below-fold selector, one scrollIntoView evaluate
and one re-locate evaluate, so 5 evaluates below the fold.

Two selector sets were compared, in both windows:

- Set A, benchmark-shaped: 6 above-fold buttons per window
  (btn-3, btn-17, btn-42, btn-0, btn-1, btn-2), 18 evaluates
  per window against 1 evaluate one-shot.
- Set B, below-fold benchmark selectors: name-input, pick,
  plain-link, 3 per window, scroll-first, 12 evaluates per
  window (1 viewport read, 3 per selector, plus 2 extra: only
  name-input needed a scroll, pick and plain-link came into
  view with it).
- Full inventory: all 65 visible elements per window,
  scroll-first, 200 evaluates per window (1 viewport read, 65
  times 3, plus 2 extra for each of the 2 selectors that needed
  a scroll at locate time; the other below-fold elements came
  into view with those scrolls).

## 3. Results table

All times in seconds. "Pooled median" pools the samples named in
the row. Full per-run values are in section 4.

| Step | Run 1 | Run 2 | Pooled |
|---|---|---|---|
| One-shot harvest, 66 elements, per window | win1 0.008, win2 0.0063 median | win1 0.0995, win2 0.0317 median | 12 samples, median 0.0112, range 0.0062 to 0.1685 |
| ground_many set A, 6 selectors, 18 evals | win1 0.3121, win2 0.2338 | win1 0.5865, win2 0.0980 | 4 values, median 0.273, range 0.0980 to 0.5865 |
| ground_many scroll set B, 3 selectors, 12 evals | win1 0.0812, win2 0.0362 | win1 0.0514, win2 0.1194 | 4 values, median 0.0663, range 0.0362 to 0.1194 |
| ground_many full, 65 selectors, 200 evals | win1 0.6758, win2 0.5030 | win1 0.4239, win2 0.5677 | 4 values, median 0.5353, range 0.4239 to 0.6758 |
| Window switch round trip (win1 to win2 and back) | median 0.0105, runs 0.0824, 0.0105, 0.0090 | median 0.0562, runs 0.0562, 0.0363, 0.0775 | 6 samples, median 0.0463, range 0.0090 to 0.0824 |
| 5 pointer clicks per window, from snapshot | win1 1.3814, win2 1.3828 | win1 1.3813, win2 1.3563 | 4 values, median 1.3814, range 1.3563 to 1.3828 |
| Verify by one DOM read per window | win1 0.0045, win2 0.0345 | win1 0.0046, win2 0.0084 | 4 values, median 0.0065, range 0.0045 to 0.0345 |
| Benchmark flow, both windows (click, type, Enter each) | 1.2146 | 0.7197 | 2 values, 0.7197 to 1.2146 |
| Marionette attach session | 2.7471 | 2.7050 | 2 values, 2.7050 to 2.7471 |
| Browser launch, manual | 0.7541 | 0.5038 | 2 values, 0.5038 to 0.7541 |

Ratios, computed from the pooled medians above:

- Full inventory: 200 evaluates vs 1 evaluate (200x fewer
  evaluates), 0.5353 s vs 0.0112 s (about 48x faster in time).
- Set A: 18 evaluates vs 1 evaluate (18x fewer evaluates),
  0.273 s vs 0.0112 s (about 24x faster in time).
- The time ratio is smaller than the evaluate ratio because one
  evaluate is cheap (about 2 to 3 ms steady state) and the first
  evaluates in a fresh window are slow (see section 5).

Rect agreement: ground_many set A rects match the one-shot
harvest rects exactly, max delta 0.0 px in all 4 window-runs
(same protocol, same JavaScript, so exact agreement is expected).
No agreement check was done for the full inventory, because
scrolling moves every rect (see section 6, finding 3).

## 4. Click accuracy and the benchmark flow

Click step (snapshot_five_clicks_fresh_rects): one snapshot per
window for inventory, then 5 real pointer clicks per window at
rect centers (btn-3, btn-17, btn-42, moved, scroll-btn), verified
by one DOM read per window.

- Run 1 win1: snapshot 0.0056 s, clicks 1.3814 s, verify read
  0.0045 s, clicked log "btn-3;btn-17;btn-42;moved;scroll-btn;",
  counter "clicks: 5", all five landed true.
- Run 1 win2: snapshot 0.0067 s, clicks 1.3828 s, verify read
  0.0345 s, same log and counter, all five landed true.
- Run 2 win1: snapshot 0.0069 s, clicks 1.3813 s, verify read
  0.0046 s, all five landed true.
- Run 2 win2: snapshot 0.0070 s, clicks 1.3563 s, verify read
  0.0084 s, all five landed true.

Each window's click step used 7 re-read evaluates (5 targets,
plus a second read for the 2 targets that needed a scroll into
view). The click cost is dominated by the pointer actions
themselves (about 0.27 s per click), not by the geometry reads.

Benchmark flow (benchmark_flow_both_windows): click name-input
in window 1 with the pointer, type "hello win1", Enter, switch
to window 2, click name-input, type "hello win2", Enter, then
one DOM read per window.

- Run 1: flow 1.2146 s. Win1 verify read 0.0176 s: value
  "hello win1", focused "name-input", counter "clicks: 6",
  clicked log ends with "name-input;". Win2 verify read 0.0115 s:
  value "hello win2", focused "name-input", counter "clicks: 6".
- Run 2: flow 0.7197 s. Win1 verify read 0.0036 s, win2 0.0028 s,
  same values, same counters.

The input click in each window needed a scroll into view first
(name-input sits below the fold) plus one re-read of its rect,
disclosed here, not hidden: the flow step does that explicitly.

## 5. Warm-up: the first evaluates in a fresh window are slow

The first JavaScript evaluates after opening a window cost far
more than steady state. Evidence from the logs:

- ground_many set A (the first evaluates in each window):
  52.01, 38.96, 97.74 and 16.34 ms per selector across the 4
  window-runs. The same bench, once warm, grounds the full
  inventory at 6.52 to 10.40 ms per selector in runs 1 and 2
  (200 evaluates in 0.42 to 0.68 s). The 10.48 ms per selector
  figure in the earlier draft came from the partial stale-rect
  run (0.6814 s / 65), not from runs 1 and 2.
- One-shot harvest first read in a fresh window: run 2 win1
  first read 0.0995 s, second 0.0271 s, third 0.1685 s (the
  third read is slower than the first, so VM contention also
  plays a part, not warm-up alone). Run 1 win1 reads were
  0.0117, 0.0071, 0.0080 s.
- Window switch round trip: first switch 0.0824 s in run 1 and
  0.0562 s in run 2, later switches 0.0090 to 0.0775 s.
- Marionette attach is 2.71 to 2.75 s in both runs, browser
  launch 0.50 to 0.75 s, navigate window 1 0.36 to 0.38 s, open
  window 2 plus navigate 0.62 to 0.63 s.

Consequence for the benchmark: do not time the first harvest in
a fresh window and call it the steady-state cost. Warm the
window with one throwaway evaluate first, or report the range
as this report does.

Variance note: the ranges in this report are 2-run samples on a
contended shared virtual machine, not stable bounds. Council 1's
independent third run (log /tmp/dom_2win_council1.log) measured
ground_many full win1 at 1.5922 s (24.5 ms per selector) and set B
win2 at 0.1839 s, both outside the 2-run ranges in section 3
(0.4239 to 0.6758 s and 0.0362 to 0.1194 s). The headline
conclusion is unaffected: slower ground_many times only widen
the gap to one-shot.

## 6. Findings that change the benchmark design

Finding 1: strict ground_many fails below the fold, reproduced
in both windows in both runs. name-input rect center y
1927.37, viewport height 814, hit false, groundable false.
The amend's ground_many has no scroll handling, so a batch
whose inputs sit below the fold fails before any click. The
scroll-first variant grounds all 3 below-fold benchmark
selectors in 0.036 to 0.119 s per window (12 evaluates). The
benchmark must either keep its inputs in view or scroll first.

Finding 2: a stale snapshot can misdirect clicks, mechanism
UNKNOWN, reproduced live as a phenomenon. The first version of
the click step clicked straight from one snapshot per window.
Result in both windows (log /tmp/dom_2win_run1_stale_rect.log):
clicked log "btn-3;btn-17;btn-42;tall;tall;", counter "clicks: 5",
all_five_landed false. The "moved" and "scroll-btn" clicks
landed on the #tall spacer at stale coordinates. The page's
clicked log later grew to
"btn-3;btn-17;btn-42;tall;tall;name-input;" when that partial
run continued into the benchmark flow step (counter "clicks: 6").
Why the snapshot coordinates were stale is UNKNOWN: the stale
code was not preserved. The bottom/top scroll story first
written here (snapshot measured at scroll-bottom, earlier
clicks scrolled the page to the top) was tested live by the
redteam and is impossible under the bench's own click
mechanics: a snapshot at scroll-bottom puts the first target's
center y about -1041, and clicking an off-viewport point raises
MoveTargetOutOfBoundsException at the very first click, so the
stale log could not have a complete clicked log; out-of-viewport
coordinates throw in both directions, they do not clamp onto
the spacer; no single scroll position puts all five snapshot
coordinates in-viewport, yet the stale log shows all five
pointer moves succeeded; and pointer clicks do not scroll the
page, so "earlier clicks scrolled the page to the top" has no
mechanism in this fixture. The log is genuine evidence that 2
of 5 clicks landed on #tall in both windows, but the cause is
unverifiable from the artifacts. The fix measured in runs 1
and 2: re-read each target's rect immediately before its click
(1 cheap evaluate each). VISION 1 inventory is valid only while
the page does not scroll; the benchmark flow must re-read after
any scroll.

Finding 3: a scroll-first full harvest leaves early rects stale.
In the full-inventory step the bench scrolls to a below-fold
element when it grounds it (2 scrolls in the full run), which
moves every rect on the page.
A rect grounded before a scroll is stale after it, so no
agreement check against the step 1 harvest is possible for the
full set. The per-element proof in that step is the hit check
at grounding time (all 65 passed). For the benchmark, ground
below-fold targets last, or re-harvest after scrolling.

Finding 4: hidden elements are ungroundable by design.
hidden-btn has rect 0x0 and hit false in both runs. ground_many
would fail fast on it, which is the correct behaviour for a
fail-fast batch: a hidden target must never be clicked.

Finding 5: two windows share one Marionette session with no
extra cost beyond the switch. Both windows were driven from a
single session (one attach, 2.71 to 2.75 s). Switching windows
costs 0.009 to 0.082 s per round trip. No second session is
needed, which matters because Firefox 160 allows exactly one
active remote session per browser instance (batch 7 task 2).

## 7. Comparison with batch 7 task 2 (single window)

- One-shot harvest, 66 elements: batch 7 Marionette pooled
  median 0.030 s (range 0.0085 to 0.0963); here pooled median
  0.0112 s (range 0.0062 to 0.1685). Same order of magnitude;
  the medians differ because the samples are few and the VM
  was contended differently, not because two windows are
  faster. No claim is made that 2 windows beat 1 window.
- 5 pointer clicks from a snapshot: batch 7, 1.49 s total for
  one window; here 1.36 to 1.38 s per window, 2.74 to 2.76 s
  for both windows together. Per-click cost is the same (about 0.27 s).
- Verify by one DOM read: batch 7, 0.002 to 0.015 s; here
  0.0045 to 0.0345 s. Same order.
- Rect agreement: batch 7, BiDi vs Marionette 5.7e-14 px; here
  ground_many vs one-shot 0.0 px (same protocol, same calls).

## 8. What is UNVERIFIED here

- Real Zen: every number is Firefox 160.0.1 as a stand-in.
  Zen 1.24.3b rides Firefox 160.0.1 (batch 7 task 2), but no
  Zen binary ran here.
- Live pages: the fixture is a local static page. Real chat
  pages (the 2-vision benchmark's clone windows) have dynamic
  content, lazy loading, and overlapping elements the fixture
  does not have.
- Headed runs: all runs are headless. Window geometry on a
  headed session (real screen coordinates, window decorations)
  is a different measurement.
- BiDi path for 2 windows: this bench uses Marionette only.
  The BiDi one-shot numbers from batch 7 task 2 (0.006 to
  0.054 s) are single-window; two BiDi contexts were not
  measured here.
- The real 2-clone chat app: the fixture inputs are plain text
  inputs, not real message threads. Exactly-once intent,
  the V12 gate, and the HCU guard from the benchmark design
  are task 1's work, not measured here.

## 9. Reproduce

Run with the repo venv python, from the repo root:

~/workspace/tools/venv/bin/python tests/dom_bench_2win.py run1

One invocation is one full run (22 steps, about 11 s plus
browser launch). Logs go to stdout; redirect to a file to
preserve them. The bench removes and recreates its own profile
directory /tmp/dom_2win_profile_<run tag> at start. It writes
the geckodriver log to /tmp/dom_2win_geckodriver.log. No
Firefox process is left running after a completed run (checked
after run 2: no firefox process remained).

Files: tests/dom_bench_2win.py (bench), this report.
Raw logs: /tmp/dom_2win_run1.log, /tmp/dom_2win_run2.log (full
runs), /tmp/dom_2win_run0_crash.log, /tmp/dom_2win_run1_stale_rect.log
(partial runs, disclosed in section 1).

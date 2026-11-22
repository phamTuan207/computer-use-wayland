# Worker PROBE-DOMZEN log: DOM-first feasibility on real Zen

Owner: the owner. Probe worker PROBE-DOMZEN, reporting to COORD-CLICK-3.
Date: 2026-11-22, runs 06:40 to 07:04 Asia/Ho_Chi_Minh.
Branch: todolist-push. VM repo HEAD at probe start: 49081aa
(AMEND4 item 7). Branch moved during the probe: local HEAD at log
time is 3f1b951, origin/todolist-push is 6f54a4e. This log commits on
top of local HEAD; it touches no other file.
Final direction landed 06:58 (commit e05fc58, 40 proposals, ADOPT 19,
MODIFY 20): this probe feeds its step 3 (2-vision bench) and step 7
(P2 element-ref) with live numbers.

Standing rules recorded here as required: no-self-healing (05:56,
dang): when Muse itself errors, an independent worker investigates;
Muse does not self-diagnose or self-fix. I diagnosed and patched
only a throwaway copy in /tmp on the laptop for measurement; the repo
is untouched by any fix, and the fix below is a proposal for
independent review and landing, not a landing. First-principles
(06:01, dang): question the original design, not only the bug. The
return-semantics finding below is a design-level hole: the unit
tests never exercised the real transport.

## Question

Clone2 batch 7 measured DOM grounding on headless Firefox (66 rects
median 0.030s, 5 clicks all hit, DOM verify 0.005-0.015s) while vision
is 58.6 percent first-try. Those numbers are not from real Zen. This
probe measures the same things on the real Zen browser on the laptop.

## Setup (measured, not assumed)

- Laptop repo: detached HEAD 56f5af4e521e1c20b26b56dc31d662e34f1c2668,
  dirty (modified live-test-log.md, hyprglass-local-optics.lua,
  scripts/cu.py, plus untracked files). It has NO scripts/zen_dom.py,
  NO scripts/dom_act.py, and its scripts/fastpath.py has NO
  dom_rect_to_image_point. The DOM-first code path does not exist on
  the laptop checkout as installed. The probe used /tmp copies of
  scripts/zen_dom.py, scripts/dom_act.py, scripts/fastpath.py taken
  from the VM repo at 49081aa. Nothing was written into the laptop
  repo.
- Zen: PID 496121, launched with --remote-debugging-port=9222 and
  --marionette. Marionette port 2828. Geckodriver at /tmp/geckodriver
  on the laptop. Zen window 0x557052b62dd0 at [2509, 914].
  Size was 1863x1176 in runs 1, 5, 6, 7, 8, 9 and 925x1176 in runs
  2, 3, 4: another live run or the owner resized it mid-probe. The
  probe reads geometry live every run, so results are unaffected.
- Fixture: /tmp/probe-domzen/fixture.html on the laptop, file:// URL,
  53 interactive elements (13 named inputs/buttons/links plus 40
  buttons B01-B40), each click recorded in a page lab object with a
  trusted flag. No owner tab or chat was touched. Every run opened
  one new tab, closed it, restored the original tab, and verified tab
  count, geometry, and the Marionette lock.
- All runs detached: setsid nohup python3 /tmp/probe-domzen/probe.py
  (runs 1-4), run5.py, run6.py, run7.py, run8.py, run9.py.
  SSH dies after about 30s; polling was short SSH reads of the log.
- Time base: wall-clock Asia/Ho_Chi_Minh plus elapsed seconds on
  every log line. Raw per-run logs were fetched to the VM
  (/tmp/probe-domzen/run.log, run2.log, run4.log, run6.log,
  run9.log, etc.) and are quoted below. Note: the run-1 in-file log
  was deleted by the rm before run 2 (probe hygiene bug); run-1
  lines below are quoted from the live session output read at the
  time.

## Verdict (one paragraph)

DOM-first is FEASIBLE on real Zen, with three conditions, all
measured. (1) scripts/zen_dom.py as shipped at 49081aa is broken on
real Zen: seven helpers return None and viewport_origin always
raises; a seven-line return fix plus a None tolerance makes the
whole path work. (2) An observation used for desktop_act must be
SETTLED: the first capture after a tab switch is a blurred
transition frame and desktop_act refuses it every time; after a 2s
wait plus a settle check, the hybrid path went 7/7. (3) The DOM
check verdicts do not reach the act result on the laptop checkout:
desktop_act takes no focus_check/type_check, so focus_verified and
type_verified stay null even when the checks pass. Headline numbers:
harvest 53 items median 0.004-0.006s; per-element locate median
0.002-0.003s; DOM verify reads 0.001-0.003s; Marionette native
clicks 20/20 landed; hybrid real clicks 7/7 landed with a settled
observation; vision locate 4/4 hit against the DOM rect; observe
CLI wall 0.24-0.35s with capture 18-39ms.

## Finding F1: geckodriver needs a top-level return (root cause, proven)

Run 1, unpatched zen_dom.py: harvest worked (53/53), but locate()
returned null 5/5 (median 0.002s) and field_value() returned None,
so the #email send_keys result could not be verified (recorded 4/5
at the time; the run-1 screenshot later showed "marionette@test"
in the field, so the action had landed 5/5 and only the read was
broken). Run 1 then crashed in viewport_origin:

  zen_dom.ZenDomError: viewport origin read is not nine numbers:
  [240, 8, 1, None, 1, 1615, 1160, 1863, 1176]

The None is window.screenPixelsPerCSSPixel, which is undefined in
this Zen build; viewport_origin rejects any None among its nine
numbers.

Run 2 diagnostic D0, live, same session (06:44:20):

  D0 return semantics: {"bare_iife": null, "return_iife": 42,
  "bare_value": null, "return_value": 42, "sppc_typeof":
  ["undefined", null, 1]}

Geckodriver wraps execute scripts in a function body, so only a
top-level return yields a value. A bare IIFE returns undefined.
harvest(), display_metrics(), viewport_origin(), and
sent_bubble_contains() already use a top-level return and work.
locate(), hit_check(), focus_check(), field_value(), verify_typed(),
arm_typed_flag(), and typed_flag() use bare IIFEs and return None on
real Zen. The unit tests never caught this because their fakes
return canned values regardless of return.

Patch applied ONLY to the /tmp copy on the laptop (never to the
repo): add "return" before the IIFE in those seven helpers, and let
viewport_origin tolerate None at index 3 (screenPixelsPerCSSPixel),
falling back to devicePixelRatio as the existing code below the
check already does. After the patch, run 2 locate #save returned
the rect (median 0.002s) and field_value returned 'marionette@test'.

First-principles note: this is a test-design hole, not a typo. Any
helper added later with a bare IIFE will silently return None on
real Zen while passing the fake-based tests. A live-transport test
(one real evaluate returning a value) is the missing gate.

## Finding F2: mozInnerScreen jitters between reads

harvest and viewport_origin read mozInnerScreenX/Y seconds apart on
the same tab and disagree: run 1 harvest [246, 13] vs viewport
origin read [240, 8]; run 2 harvest [247, 20], then [246, 18],
vs viewport origin [240, 8]; run 4 harvest [246, 19] vs viewport
origin [240, 8]. That is 6-12px of jitter. harvest bundles
moz_inner with the rects in one evaluate, so it is self-consistent.
ground_input reads the rect and the origin in separate evaluates,
so its point can be off by about 10px. For a 73x45 button that is
tolerable; for a 24px target it is material. Prefer the
harvest-bundled origin. screenPixelsPerCSSPixel is undefined
(None) in this Zen build; devicePixelRatio is 1, zoom is 1.

## Finding F3: Marionette native clicks work and are trusted

Docstring in zen_dom.py claims Marionette click fails on windowed
Zen (0x0 viewport quirk). Measured: native element click 0.055s
to 0.078s each, 5/5 landed in every patched run (runs 2, 3, 4:
#count 3/3, #agree checkbox 1/1, #email click plus send_keys 1/1,
verified by DOM read and by explicit-return read). Across runs 1
to 4, 20/20 landed. lab.trusted totalled 5 after the 5 synthetic
clicks: Marionette clicks dispatch trusted events in this build.
The quirk claim is stale for this Zen; re-measure before relying on
it either way.

## Finding F4: the first observe after a tab switch is a blurred transition frame

Run 6: in-process desktop_act refused all 7 actions with
ok=False, completed=0, error 'screen changed', 0.22-0.31s each.
Run 7 measured why: CLI observe vs a fresh in-process observe
0.09s later differed on 84 percent of pixels (mean 19.982,
changed_px 491158 of 581760, bbox (120, 1, 959, 603)); fresh vs
fresh2 0.15s later were identical (mean 0.000, 0 px). Region mean
diffs: sidebar-left 4.0, topbar 21.0, content 22.6. Cursor position
(3605, 1129) did not move during observes.
Run 8 pinned it: CLI-A vs CLI-B mean 66.267; CLI-A vs in-process-C
mean 66.267 (identical value); shift search dx,dy in -4..4 found
best (0, 0) at 66.267, so it is not a shift. Viewing the images
showed it: image A is BLURRED over the whole content area (a
frosted transition frame, 466797 bytes) and image B is CRISP
(177783 bytes). The first capture after a tab switch catches a
blur transition; settled captures are pixel-identical. The blur
lasts somewhere between about 0.6s and 0.9s after navigation (run 8
observe A at about 0.57s after ready was still blurred; observe B
about 0.26s later was crisp).
Consequence: _desktop_act re-observes before acting and refuses
when mean diff exceeds 3, so any observation taken during the
transition always refuses. Run 9 waited 2s after navigation and
required two CLI observes to agree (mean 0.000, PASS attempt 1);
the hybrid path then went 7/7. Production must settle observations
before acting; a single observe taken right after a tab switch is
not usable input.

## Finding F5: cu.py act CLI needs a session; in-process desktop_act does not

Run 4: cu.py act CLI returned rc=1 in about 0.15s for all 6 calls,
stderr empty, stdout: {"ok": false, "error": "input requires
computer-use session -- DRIVER [ARGS...]"}. The act command
requires CU_SESSION_TOKEN. desktop_act itself does not check the
token (the gate is in main()), so run 6 called it in-process and
it ran (then refused on screen_changed, F4).
Run 5 crashed before that: PreflightRefusal 'desktop observation
required', because validate_desktop_observation needs
meta['backend'] == 'desktop' and the CLI printed compact JSON
omits 'backend' (the observation FILE has backend 'desktop').
Load the meta from the file, not from CLI stdout.
Also: the laptop cu.py has NO focus_check/type_check/dom_hooks
wiring (grep finds nothing). dom_act.focus_type runs end to end
and lands, but desktop_act accepts no check callbacks, so the run-9
focus_type result carries focus_verified null and type_verified
null even though the explicit focus/verify/typed-flag reads all
passed. The verdicts exist only in the caller's own reads.

## Measured numbers by run

Fixture: 53 interactive elements every run. Zen tabs before/after:
18/18 every run. Geometry unchanged after every run. Marionette
lock free after every run. Session open 0.010-0.012s. New tab plus
navigate 0.123-0.184s. list_tabs 0.31-0.77s for 18 tabs.

Run 1 (06:40:07-06:41:05, unpatched):
- harvest 5x: 0.005, 0.006, 0.007, 0.006, 0.004s, median 0.006s,
  53/53 items. moz_inner [246, 13], dpr 1, sppc None, zoom 1,
  inner [1615, 1160], outer [1863, 1176].
- locate #save 5x median 0.002s, rect null (F1).
- C1: #count 3/3 (click 0.078/0.062/0.057s, verify 0.002-0.003s),
  #agree 1/1 (0.057s, checked True), #email click 0.058s plus
  send_keys 0.007s, field_value None (F1). True 5/5 by screenshot.
- observe: cli_wall 0.259s, capture_ms 22.8, decode 17.3,
  encode 17.7, image 960x606, scale 0.5153.
- CRASH viewport_origin (F1). Cleanup clean.

Run 2 (06:44:19, patched zen_dom):
- D0 confirmed (F1). list_tabs error on one handle: HTTP 500
  "unexpected alert open ... Performed handler dismiss": the scan
  DISMISSED an alert dialog on an owner's tab (handle 3e882bc8).
  Hazard, see below.
- Zen had been resized to 925x1176 by another party.
- harvest median 0.004s (0.006/0.005/0.004/0.004/0.003), 53/53.
- locate #save median 0.002s, rect returned.
- C1 5/5 (clicks 0.056-0.071s, type 0.006s, field_value
  'marionette@test', explicit-return read 0.001s).
- observe 0.238s, capture 17.9ms, image 925x1176, scale 1.0.
- viewport_origin [2749, 922], moz_inner [240, 8] (F2).
- CRASH: laptop fastpath lacks dom_rect_to_image_point.

Run 3 (06:45:51): same crash. Cause was a probe bug, not the
laptop: sys.path inserts put the laptop scripts dir first, so
dom_act imported the laptop fastpath instead of the /tmp copy.
Fixed by inserting /tmp first. C1 5/5 and harvest median 0.005s
before the crash.

Run 4 (06:47:35):
- harvest median 0.005s, locate median 0.003s, C1 5/5.
- observe 0.252s, capture 18.8ms.
- C2 via cu.py act CLI: 0/6, rc=1 every call (F5).
- lab.trusted 5 (F3).

Run 5 (06:51:40): in-process desktop_act attempt. CRASH
PreflightRefusal 'desktop observation required' (F5, printed meta
lacks backend). No clicks attempted.

Run 6 (06:53:55): meta from file (backend 'desktop'). desktop_act
ran but refused 7/7 with error 'screen changed' (F4). C2 0/7.
focus_type error 'screen changed', completed 0.

Run 7 (06:56:53): diagnosis only, no clicks. CLI-vs-fresh mean
19.982 (84 percent pixels); fresh-vs-fresh2 mean 0.000 (F4).

Run 8 (06:58:25): diagnosis only. CLI-A vs CLI-B mean 66.267;
CLI-A vs in-process-C mean 66.267; best shift (0, 0). Image A
blurred (466797 bytes), image B crisp (177783 bytes) (F4).
Cleanup list_tabs errored again on a different handle
(ed1e3257): a second alert dismissed by a scan.

Run 9 (07:03:58-07:04:04, settled observation):
- settle: 2s wait, then two CLI observes agree, mean 0.000, PASS
  attempt 1. Observe capture_ms 20.6, image 960x606.
- C2a hybrid clicks #btn01-#btn05: 5/5 landed. Ground
  0.010-0.011s, desktop_act 0.217-0.231s, act_ok True,
  act_completed 1, verify 0.002s each.
- C2b hybrid type #name: landed. Ground 0.009s, desktop_act
  0.287s, value 'PROBE-42', focus_check True (0.002s),
  verify_typed True (0.003s), typed_flag True.
- C2c dom_act.focus_type #search 'FOCUS-TYPE-1': ok True,
  completed 2, wall 0.314s, dom_calls 7, observes_added 0, value
  verified 'FOCUS-TYPE-1' landed. focus_verified null,
  type_verified null (F5 wiring gap).
- C2 SUMMARY 7/7 landed. lab.trusted 7 (real OS clicks).
- Cleanup: tab closed, original tab restored, tabs 18/18,
  geometry unchanged, lock free.

Totals: harvest 20 runs of 5x, all 53/53, median 0.004-0.006s.
Per-element locate (patched) median 0.002-0.003s. DOM verify reads
0.001-0.003s. Marionette native clicks 20/20. Hybrid real clicks
with settled observation 7/7. Observe CLI wall 0.238-0.351s,
capture_ms 17.9-38.5.

## Vision latency (GROUNDING P6 number the repo lacked)

One vision locate step is one observe plus one visual read of the
screenshot. Observe cost measured: CLI wall 0.238-0.351s,
capture_ms 17.9-38.5, decode about 13-17ms, encode about 14-26ms.
The visual read itself is one image inspection on top of that; it
is not instrumented to the millisecond here, and I do not invent a
number for it. What is measured is the locate ACCURACY against the
DOM rect (target #save, image px, vision point vs DOM image point):

- Run 1 (1863w, scale 0.5153): vision (167.0, 200.6) vs DOM
  (168.2, 200.3), delta (-1.2, +0.3). HIT.
- Run 4 (925w, scale 1.0): vision (326.5, 488.0) vs DOM
  (326.5, 487.7), delta (0.0, +0.3). HIT.
- Run 5 (1863w, scale 0.5153): vision (161.3, 197.6) vs DOM
  (168.3, 200.3), delta (-7.0, -2.7). HIT, inside the button.
- Run 9 (1863w, scale 0.5153): vision (165.1, 200.0) vs DOM
  (168.3, 200.3), delta (-3.2, -0.3). HIT.

Vision locate 4/4 HIT. Max abs delta 7.0 image px, inside the
37.6x23.2 image-px button every time. The DOM point used the
viewport_origin moz snapshot ([240, 8]); the harvest moz snapshot
([246, 18]) would have put the DOM point 7-12px away, which is the
same order as the vision error (F2). DOM grounding is exact only
when the rect and the origin come from one snapshot.

## Hazards and open items (for the coordinator, not fixed here)

1. list_tabs scans dismissed an alert dialog on an owner's tab
   twice (runs 2 and 8, different handles). A tab inventory read
   must not dismiss owner dialogs. Do not run full list_tabs scans
   against the owner's live Zen until this is fixed or the scan
   avoids the title read on alert tabs.
2. The laptop checkout (detached 56f5af4, dirty) lacks
   scripts/zen_dom.py, scripts/dom_act.py, and
   fastpath.dom_rect_to_image_point. The DOM-first path cannot run
   from the installed checkout; the probe ran from /tmp copies.
   Sync the laptop checkout to todolist-push before the next DOM
   live run.
3. The seven-return fix and the sppc-None tolerance exist only in
   /tmp/probe-domzen/zen_dom.py on the laptop. They are NOT in this
   repo. Landing them needs an independent worker (no-self-healing
   rule) plus a live-transport test, or the same silent-None
   failure will recur.
4. desktop_act refuses any unsettled observation. The settle step
   (wait plus two agreeing observes, or the existing
   settled_observation helper) must be part of the act path, not
   left to the caller.
5. dom_act focus/type check verdicts do not reach the desktop_act
   result envelope on the laptop checkout. Either wire the checks
   into desktop_act or stop claiming the result verifies focus and
   typing.
6. Zen was resized 1863 to 925 and back by another live run or the
   owner during this probe (runs 1 to 2, runs 4 to 5). Live runs
   sharing one Zen need a resize protocol, or every grounding must
   re-read geometry live (this probe did; that is why it survived).

## Commands (evidence standard)

- Probe scripts (laptop /tmp, not committed): probe.py (runs 1-4),
  run5.py, run6.py, run7.py, run8.py, run9.py; fixture
  fixture.html; patched zen_dom.py, dom_act.py, fastpath.py copied
  from VM todolist-push 49081aa. Launch pattern every run:
  setsid nohup python3 /tmp/probe-domzen/<run>.py > log 2>&1
  < /dev/null & disown, then short SSH polls of the log.
- Observe command (runs 1-9): python3 scripts/cu.py observe
  --window 0x557052b62dd0 --max-width 960.
- Failed act command (run 4): python3 scripts/cu.py act
  --observation <obs.json> --actions <actions.json>, rc=1,
  stdout {"ok": false, "error": "input requires computer-use
  session -- DRIVER [ARGS...]"}.
- Vision images fetched to the VM and located with the visual
  grounding tool: run1 e80ba094bd01.png, run4 553651dc7960.png,
  run5 53c0fabd5828.png, run8 ee6bd7ec1346.png (blurred) and
  871793df5cd1.png (crisp), run9 3482fc5345c5.png.
- No ydotool used anywhere. No owner tab, chat, or file touched.
  Test tab opened and closed every run; 18 tabs before and after
  every run.

## Files

- This log: improvements/worker-probe-domzen-log.md (only file in
  this commit).
- Raw per-run logs and screenshots stay in /tmp/probe-domzen on
  the VM and the laptop; they are not committed.

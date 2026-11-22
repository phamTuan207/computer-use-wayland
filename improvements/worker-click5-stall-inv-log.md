# Worker C5-STALL-INV log: Chromium CDP Input stall, read-only investigation

Owner: the owner. Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. Read-only
investigation lane, parallel with C5-STEP9 (owns implementation).
No code changes, no sends, no keystrokes, no navigation of any
live tab. No em dash or en dash anywhere in this file. No personal
info. Wall-clock Asia/Ho_Chi_Minh plus elapsed time on every
entry. Start 16:02 +07, Sun 2026-11-22 (T+0m).

## 0. Starting point (read first, all verified in the sources)

- Original flip (improvements/worker-click4-s2-flip-log.md
  section 5): Chromium 0/5, "CDP timeout:
  Input.dispatchMouseEvent" at 5002-5003 ms, first mouseMoved
  inside fill click; Brave 5/5 same program. Dry run 0 filled
  the Chromium composer TWICE on a scratch tab minutes before
  run 1.
- Input fix (improvements/worker-click5-input-fix-log.md,
  commit 4bd6292): (a1) Target.activateTarget FAILED 0/5 live
  (one-off probe success 14 ms did not reproduce; 0/5
  follow-up probes). Stall is MOUSE-specific:
  Input.dispatchKeyEvent answers in 2 ms on the stuck tab.
  (b1) set_value + focus + CDP key Enter works 5/5 and is the
  current working path. The stall itself is UNSOLVED.
- S2 re-open (improvements/worker-click5-s2-reopen-log.md,
  commit 1a3356d): two-browser 5/5, median 28.6 s, EXPAND
  recommended. Chromium half uses (b1); the mouse stall is
  bypassed, not fixed.
- Visibility (improvements/worker-click5-visibility-log.md):
  occluded 2/9 ok (A1 3 ms, A2 2 ms), visible 4/4 ok,
  stall sticky once on (7 consecutive timeouts A3-A9),
  visibility is a reliable RECOVERY (ws2 switch unstuck 3/3
  in 2 ms) but NOT the cause. Stall does not self-clear in
  240 s of steady occlusion.
- Input invest (improvements/worker-click5-input-invest-log.md):
  cause 3.2 background tab KILLED (tab already active, single
  page target); cause 3.4 session KILLED (6 fresh sessions
  fail identically); cause 3.6 timeout KILLED as fix (70-100x
  headroom, deterministic 5/5); cause 3.9 coordinates KILLED
  (hit test passes, point in viewport); cause 3.3 page-state
  main-thread form KILLED (Runtime 1-3 ms). Open: onset
  trigger between A2 and A3; L4 (pending/unacked dispatch)
  untested.

## 1. Time log

- 16:02 +07, T+0m: task received. Read the flip log section 5,
  the input-fix log, and the S2 re-open log in full.
- 16:03 +07, T+1m: laptop pre-state. Relay PID 1196429 alive,
  54:59 elapsed, loaded hash d490f369f6b754d2 (matches brief
  prefix d490f369f6b7), laptop HEAD 9ec713c (STEP9 commits;
  brief named 1b5a6e6, superseded, relay hash unchanged).
  Chromium 157.0.8103.38 on 127.0.0.1:9223, live clone2 tab
  D1374C7C994D3DA72678E20C7FD099A0 present. Active workspace
  2, active window Chrome 0x5570538ed160 (clone2), visible 1.
  Brave window from the brief map (PID 1185797) is DEAD;
  RUNG2 relaunched it ~16:03 (/tmp/p3-brave-debug.log).
  No cu.py send process running at 16:03.
- 16:04 +07, T+2m: probe scripts written to the laptop
  (/tmp/c5-stall-probe.mjs, /tmp/c5-stall-mini.mjs,
  /tmp/c5-stall-battery2.mjs, /tmp/c5-livestate2.mjs,
  /tmp/c5-dbg.mjs, /tmp/c5-dbg2.mjs). Node built-in
  WebSocket client, same shape as /tmp/c5-a1.mjs, 5000 ms
  per-call timeout matching cdp.mjs:60. Scratch tab ONLY
  for all Input calls. Live tab read-only
  Runtime.evaluate only, never Input, never navigate.
- 16:04 +07, T+2m: scratch tab created:
  579184401A316D90C9046E5ECDC6648C, new window
  0x557053e5ae30 "about:blank - Chromium", ws2, 901x1176,
  visible 1, became the active window on creation.
- 16:04 +07, T+2m: P0 battery on the scratch tab, window
  active and visible (section 2).
- 16:05 +07, T+3m: P0 repeat, same result (section 2).
- 16:06 +07, T+4m: mini v2 probe, hasFocus false, mouse
  still ok (section 2). Transport artifact found and
  fixed: single quotes inside heredoc lines are stripped
  in transit via ssh-laptop.sh (section 5).
- 16:06:36-16:06:38 +07, T+4m: OCCLUSION test, one SSH call:
  switch to ws1, mini probe on the scratch tab, switch back
  to ws2, mini probe again (section 3). No live send in
  flight (0 cu.py processes at 16:06:36).
- 16:07 +07, T+5m: read the visibility log and the
  input-invest log in full (sections 0, 6).
- 16:07 +07, T+5m: live tab read-only state (section 4).
- 16:07 +07, T+5m: battery 2 ABORTED before running: the
  scratch tab 5791... was GONE from /json/list (section 5).
  No close call was ever issued by this worker. Cause
  unestablished; RUNG2 run3 processes started 16:08, after
  the disappearance, and no worker log records a tab close.
- 16:08 +07, T+6m: RUNG2 run3 in flight (cu.py act-now PID
  1241633 + session-driver PID 1241682, started 16:08,
  rung2-run3-clone1-actions.json). No interference: this
  worker issued no CDP call to any live tab in that minute.
- 16:08:40 +07, T+6m: no cu.py processes; run3 send phase
  done. RUNG2 run cadence is about 1 run per minute
  (run1 16:06, run2 16:07, run3 16:08, action files).
- 16:09:02 +07, T+7m: battery 2 re-attempt GATED OFF: a live
  run was in flight again (pgrep cu.py act-now/session
  matched), so no scratch tab was created. Gating rule:
  create + probe + close in ONE ssh call, only when no
  cu.py act-now/session process is running at call start.
- 16:09:36 +07, T+7m: battery 2 RAN on fresh scratch tab
  3C5593EAA84344A29180DC539BF60850 (create + battery + close
  in one gated call, section 7). Tab closed cleanly by my
  own Target.close (success true).
- 16:10:03 +07, T+8m: final verification. Chromium PID 8059
  started Sat Nov 21 15:19:27, elapsed 1 day 00:50:34. The
  browser is over a day old; the live tab is long-lived,
  fresh scratch tabs are minutes old. /json/list shows only
  the clone2 page plus 3 Stripe iframes plus a service
  worker: my scratch tab is closed, machine clean. Active
  workspace 2, active window Chrome 0x5570538ed160: the
  as-found state from 16:03 is restored.

## 2. P0: fresh scratch tab answers every mouse call, active window

Scratch tab 579184401A316D90C9046E5ECDC6648C, window active
and visible on ws2. Command (one SSH call):

```
node /tmp/c5-stall-probe.mjs probe 579184401A316D90C9046E5ECDC6648C
```

Result, first run (16:04 +07):

- baseline Runtime.evaluate: 2 ms, value 2.
- state: visibility visible, hasFocus true, innerW 901,
  innerH 1089.
- keyDown Shift: 1 ms ok. keyUp Shift: 1 ms ok.
- mouseMoved default (763,574, button none, clickCount 0):
  4 ms ok.
- mouseMoved left/clickCount 1: 7 ms ok.
- mouseMoved pointerType touch: 7 ms ok.
- mouseMoved pointerType pen: 7 ms ok.
- mousePressed left: 1 ms ok. mouseReleased left: 1 ms ok.
- jsClick / jsClickAfter: answered but value missing (see
  section 5, transport artifact; the calls themselves
  returned in 0-1 ms).

Repeat run (16:05 +07, same script, same tab): key 0-1 ms,
mouseMoved default 0 ms, left/clickCount1 6 ms, touch 6 ms,
pen 7 ms, press 1 ms, release 0 ms. All ok.

Mini v2 run (16:06 +07): baseline 2 ms, state hasFocus FALSE,
mouseMoved default 7 ms ok, jsClick clicks 2, atPoint BODY.
So document.hasFocus false does NOT stall mouse on a fresh
tab either.

Reading: a fresh target in the same browser answers mouse in
1-7 ms under every parameter variation tried. No parameter
dependence (button, clickCount, pointerType all fine), no
focus dependence. The stall is not a property of fresh
targets, fresh windows, or the mouse parameters.

## 3. Occlusion test: fresh tab answers mouse while occluded

One SSH call, 16:06:36-16:06:38 +07 (2 s total, no live send
in flight, verified 0 cu.py processes at call start):

```
hyprctl dispatch "hl.dsp.focus({ workspace = 1 })"
node /tmp/c5-stall-mini.mjs 579184401A316D90C9046E5ECDC6648C
hyprctl dispatch "hl.dsp.focus({ workspace = 2 })"
node /tmp/c5-stall-mini.mjs 579184401A316D90C9046E5ECDC6648C
```

Occluded probe (ws1 active, Chrome window on ws2 hidden):
baseline 2 ms, state visibility visible, hasFocus true,
keyDown 1 ms ok, mouseMoved default 1 ms ok, jsClick
clicks 3, atPoint BODY.

Back on ws2: baseline 2 ms, keyDown 0 ms ok, mouseMoved
1 ms ok, jsClick clicks 4.

Reading: occlusion does NOT stall a fresh tab, and the
ws2-to-ws1 transition does NOT wedge it either (mouse
answered 1 ms immediately after the switch away). This is
the exact experiment the flip log declined to run, and on a
fresh target it is negative. Combined with the visibility
log (same live tab: A1/A2 occluded ok, then onset between
A2 and A3, then sticky), the trigger is NOT occlusion and
NOT the workspace-switch transition alone. Both are
consistent with the stall only if the target is already in
a susceptible state, which a fresh tab is not.

## 4. Live tab read-only state (no Input, no navigation)

Command (16:07 +07):

```
node /tmp/c5-livestate2.mjs
```

Result (2 ms):

- visibility visible, hasFocus true, activeElement TEXTAREA,
  innerW 901, innerH 1148, items 47, scrollY 0.
- composer rect: x 141, y 1091, w 291, h 24, center
  (287, 1103).

Geometry kills the out-of-viewport hypothesis for the flip
point: the flip click center y 1103 sits INSIDE the live
viewport (innerH 1148), 45 px above the bottom edge. The
composer rect also differs from the flip's (452, 1091,
622x24): the live window is now 901 wide (was 1853x1176 at
16:02 per the RUNG2 log), retiled after the scratch window
appeared or after RUNG2 focus calls. The activeElement
TEXTAREA shows the composer is focused right now, most
likely by a recent (b1) focus+Enter send from STEP9/RUNG2;
that is their activity, not this worker's, and it was
observed read-only.

## 5. Transport artifact: single quotes stripped via ssh heredoc

While debugging the jsClick value, /tmp/c5-dbg.mjs proved
returnByValue works (object literal returns {a:1}, IIFE
returns 5, appendChild returns "appended"), and
/tmp/c5-dbg2.mjs proved the exact jsClick IIFE works
(clicks 1, atPoint BODY). The file on disk showed the
cause: in /tmp/c5-stall-mini.mjs line 41 and
/tmp/c5-stall-probe.mjs lines 77-78, every single-quoted
JS literal lost its quotes in transit
(`createElement(button)`, `b.id=probe-btn`,
`addEventListener(click, ...)`), so the evaluate threw a
ReferenceError and returned no value. Double-quoted
literals survive intact (`"1+1"`, `"/json/list"`). Rule
for future laptop scripts: use ONLY double quotes in
heredoc content sent via ssh-laptop.sh; never single
quotes. The mouse/key results were never affected (their
params used double quotes throughout).

## 6. Scratch tab disappearance (unestablished cause)

Scratch tab 579184401A316D90C9046E5ECDC6648C was confirmed
alive at 16:06 (mini v2 probe) and gone from /json/list by
16:07 (battery 2: "scratch tab not found"). Only the clone2
page plus 3 Stripe iframes remained. This worker never
issued Target.close or any close call. No worker log
(RUNG2, STEP9) records a tab close; RUNG2 run3 processes
started 16:08, after the disappearance; the flip harness
close_scratch only closes its own target id
(scripts/s2_flip_live.py:605-608, 712-714). Cause is
unestablished and is recorded here rather than guessed.
Impact: battery 2 did not run on the first tab; it is
re-run on a fresh tab below. No live tab was touched at
any point.

## 7. Battery 2: activation, flip point, out-of-viewport, burst, unpaired press

Fresh scratch tab 3C5593EAA84344A29180DC539BF60850, one gated
SSH call, 16:09:36 +07 (create + battery + close). Command:

```
node /tmp/c5-stall-battery2.mjs 3C5593EAA84344A29180DC539BF60850
```

Result, every call answered:

- (a) Target.activateTarget: {} in 4 ms.
  Page.bringToFront: 2 ms. mouseMoved after activation:
  4 ms ok. Activation works, but it is moot on a fresh tab:
  the mouse already answers. On the live tab activation
  already failed 0/5 (input-fix log), so (a) is dead as a
  stall fix, not untested.
- (b) mouseMoved at the flip point (763, 1103): 4 ms ok.
- (c) mouseMoved far out-of-viewport (5000, 2000): 6 ms ok.
  mouseMoved negative (-50, -50): 8 ms ok. mouseMoved
  back in-viewport right after: 6 ms ok. An out-of-viewport
  point does NOT wedge the pipeline, and the mouse after it
  still answers. Combined with section 4 (the flip point
  sits inside the live viewport, 1103 < 1148), the
  out-of-viewport trigger is killed twice over.
- (e) burst of 20 mouseMoved: 20/20 ok, max 8 ms.
  Sustained input does not wedge a fresh tab.
- (f) mousePressed unpaired (no release yet): 2 ms ok.
  mouseMoved while pressed: 5 ms ok. mouseReleased: 1 ms
  ok. mouseMoved after the unpaired press: 6 ms ok. The
  L4 candidate (a press without its release wedging Input)
  does not reproduce on a fresh tab.
- Close: Target.close on my own scratch target id only,
  success true. /json/list afterwards shows only the clone2
  page plus Stripe iframes.

(d) Runtime.evaluate click: proven on scratch in section 2
(mini v2: jsClick clicks 2, atPoint BODY; /tmp/c5-dbg2.mjs:
clicks 1, atPoint BODY). el.click() fires handlers
synchronously with zero Input calls. The differential for
(d) comes from prior logs, not from this tab: on the stuck
live tab Runtime answers in 1-3 ms while mouse times out,
and (b1) already proves an evaluate-plus-key path sends
live 5/5. So (d) is a proven bypass shape, not a stall fix.

(b) hyprctl focus as a fix: NOT re-tested by this worker.
The only focus change I made was the section 3 occlusion
test (ws1 then back to ws2 in 2 s, no live send in flight),
which was a probe of the trigger, not a fix attempt. A
focus-based fix attempt while STEP9/RUNG2 are sending
would risk stealing focus mid-send, and the visibility log
already establishes the fact a fix attempt would need:
a ws2 switch unsticks the live tab 3/3 in 2 ms. That is a
RECOVERY, and it stands; re-proving it was not worth the
collision risk.

## 8. Verdict: NO CHEAP FIX for the stall itself

Trigger condition, as far as this investigation can pin it:
the stall is per-target, mouse-domain-only, and sticky once
on, and it does NOT reproduce on a fresh target under any
manipulation tried. Killed as triggers on fresh targets,
each with a timed probe in this log:

- occlusion (section 3: mouse 1 ms while occluded);
- the workspace-switch / focus-loss transition (section 3:
  mouse 1 ms immediately after switching away);
- tab activation state (input-fix log: tab already active;
  section 7: activation is a no-op on fresh tabs);
- window focus (section 2: hasFocus false, mouse 7 ms);
- mouse parameters: button, clickCount, pointerType
  (section 2: all 1-7 ms);
- out-of-viewport and negative points (section 7: 6-8 ms,
  and the mouse after them still answers);
- sustained input bursts (section 7: 20/20, max 8 ms);
- unpaired mousePressed (section 7: mouse after it 6 ms).

What remains true and unexplained: the LIVE clone2 tab
answers mouse sometimes (visibility A1/A2, 3 ms and 2 ms;
input-fix one-off activation probe, 14 ms) and then goes
sticky-stuck for hours (flip 0/5, visibility A3-A9, input
fix 0/5 live plus 0/5 probes, about 12:20 to 12:35). The
onset correlates with ws2-to-ws1 focus-loss transitions
in both visibility cycles, but the transition alone does
not wedge a fresh tab, so the trigger is transition PLUS
a susceptible target state that a fresh tab lacks. The
leading untested correlate is target age and accumulated
state: Chromium PID 8059 has been alive 1 day 00:50, the
live tab has absorbed days of CDP sessions and a dozen
timed-out dispatches (each timeout drops the pending entry
client-side while the browser side may still hold the
event; invest log section 2.2). That mechanism is a
hypothesis, not a finding: no probe in this task could
observe it without Input calls on the live tab, which
were forbidden.

Cheapest fix: NONE found for the stall itself. Every cheap
candidate is either dead on the live tab (activation 0/5),
moot on a fresh tab (parameters, activation, screenshot
pump unneeded where mouse answers), or a recovery rather
than a fix (visibility switch unsticks 3/3, but does not
prevent the next onset). The working path stays (b1)
set_value + focus + CDP key Enter, 5/5 live, which STEP9
owns; this worker hands STEP9 nothing new to implement,
because there is no fix spec to hand over. What the
coordinator should carry forward:

1. Do NOT gate sends on visibility or activation: occluded
   sends CAN work (A1/A2, and section 3), and activation
   does not prevent the stall.
2. DO keep the visibility switch as the retry unblock: on
   "CDP timeout: Input.dispatchMouseEvent", focusing the
   target window is the only intervention proven to unstick
   the live tab (3/3, 2 ms), short of the (b1) bypass.
3. Untested discriminators, for a follow-up with explicit
   approval, in order: (i) a scratch tab loaded with the
   live app (tests the page-state narrow form, cause 3.3,
   without touching the live tab; this task's brief
   specified about:blank, so it was not done here);
   (ii) D-6, a 30 s mouseMoved on the live tab, and D-D1,
   screenshot-then-mouse on the live tab (both need Input
   on the live tab, forbidden to this worker); (iii) a
   long-lived scratch tab left open for a day, then the
   section 3 transition probes repeated (tests the age
   correlate directly).

## 9. Commit record

- This log: improvements/worker-click5-stall-inv-log.md,
  commit 3852b46, push verified with git ls-remote
  (3852b46e663302cb379ecafdfeb56bac12b710b4).
- Laptop helpers (not in the repo): /tmp/c5-stall-probe.mjs,
  /tmp/c5-stall-mini.mjs, /tmp/c5-stall-battery2.mjs,
  /tmp/c5-livestate2.mjs, /tmp/c5-dbg.mjs, /tmp/c5-dbg2.mjs.
- No code changes to the repo (this log only). No sends into
  any thread. No keystrokes. No navigation of any live tab.
  Target.close issued exactly once, on my own second scratch
  target id 3C5593EAA84344A29180DC539BF60850 (success true);
  the first scratch tab vanished on its own, see section 6.
  No second headed Chromium launch. One workspace switch pair
  (ws1 then back to ws2, 2 s total, 16:06:36, no live send in
  flight).

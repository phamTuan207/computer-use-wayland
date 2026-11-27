# OPT-ORDER Voice 2: DEPENDENCY
# Council OPT-ORDER, voice 2 of 3. Time: 22:56 +07, Sat 2026-11-21.
# Lens: what gates what; which classes run in parallel lanes and which must
# stay serial. Sources: PRIO council 1 (improvements/worker-prio-council-1.md),
# PRIO redteam (improvements/worker-prio-redteam.md), PRIO council 3
# (improvements/worker-prio-council-3.md), todolist priority section + items
# 4.7-4.28 (docs/zen-error-fix-todolist-20261121.md), sibling council OPT-M1
# mechanism paper (improvements/opt-council-m1-mechanism.md, landed 22:5x).
# Sibling OPT-M2 verdict does NOT exist yet at write time; that gap is
# recorded here and in the council log. No em/en dashes in this file.
# Every claim carries a file:line or quote citation.

## Hard mechanism constraints (the queue is built on these, not on preference)

- D0. ONE live runner at a time. F1, F2, F3, ZT-B, Y6 trial, Y13, Y14, A1,
  hidden-body experiment, H2 run, final test all drive the same live machine
  and the same owner screen. Strictly serial, never overlapping. (PRIO
  council 1, H1; todolist gate G-SINGLE-LIVE.)
- D1. ONE session TOTAL shared by BiDi + Marionette (todolist 1.2.1). No two
  live drivers can hold a session at once. This is the mechanical reason the
  live queue must be serial, not just a politeness rule. (PRIO council 1, H2.)
- D2. F3 gates every live run. A usable Zen plus a working Marionette slot is
  a precondition for ZT-B, Y13, Y14, A1, Y6 trial, hidden-body, H2, final
  test. Nothing live runs before F3. (PRIO council 1, H3.)
- D3. The scrub is a breaker, not just a task. Filter-repo + force-push +
  all-agents re-clone + PR #1 handling breaks in-flight pushes, so it runs
  only in a quiet fleet window, never mid-flight. (PRIO council 1, H5;
  todolist gate G-SCRUB.)

## The dependency graph, edge by edge

### P0. VMFIX: DONE 22:40, with a watch tail
- VMFIX is DONE: SSH restored durably (F1 fixed re/__init__.py from CPython
  3.12.3, dpkg -V clean, observe 22:38 ok). Guardian failure is NOT due to
  re: it is the cursor-guard plugin not loaded, and F1 is fixing that.
  (Todolist priority section, P0; PRIO redteam addendum 22:44, A3/M3
  corrected.) Voice 2 AGREES with the redteam addendum: the A3 premise
  (F1's root cause may be the re breakage) is REFUTED by VMFIX's finding.
- What remains OPEN: the root cause of the deletion itself is still UNKNOWN:
  the file that vanished at 22:25:39 could vanish again (redteam addendum).
  So P0 keeps a watch on /usr/lib/python3.12/re, not just a one-time
  verification. The queue rule (todolist gate G-VMFIX): re-verify
  `python3 -c "import re"` OK plus `ssh-laptop.sh echo SSH_OK` immediately
  before each live run from rank 4 onward. If SSH or Python breaks
  mid-queue: FREEZE all live work at once, do VM-local work only, never
  assume a self-restore means fixed (PRIO council 3, G-VMFIX).
- Voice 2 position: VMFIX is a precondition, not a rank. It is DONE, so it
  does not block ranks 1-3. The watch tail is a standing check inside
  G-VMFIX, not a queue item. PRIO council 1 H4 (track VMFIX, do not assume
  stability) is satisfied by the DONE verdict plus the watch.

### F1 before F2: the one dependency the whole queue turns on
- Direction is F1 -> F2, not F2 -> F1. A session that never starts (J4,
  todolist 4.11) cannot produce a first visible action in under 30s (J5,
  todolist 4.12), and an overlay that never shows cannot be made always-on.
  F2's acceptance test therefore gates on F1 green. (PRIO council 1, SWAP 1.)
- Mechanism proof from sibling M1: the pill exists only inside a live
  session (guardian creates indicator.Native, session driver shows it); no
  session, no pill; the direct Pointer path never touches the overlay at all
  (OPT-M1 mechanism, B2, citing scripts/cu.py require_session lines
  2599-2602 and scripts/overlay.py). The 22:17 click had no overlay for
  exactly this reason. And the session gate itself has a second gap: a
  paused or crashed glass with a loaded guard starts a session with no pill
  (OPT-M1 mechanism, C1b, redteam R3). So F2's proof needs F1 green AND the
  glass-active gate, not F1 alone.
- Load order inside F1 (OPT-M1 mechanism, A7): the guard cannot load until
  glass loads first (activate-cursor-guard.py refuses unless
  indicator.liquid_available is true, i.e. hyprglass loaded + active +
  version 1.1.1-cu.1 + versionCheck match, scripts/indicator.py line 242).
  Order is forced: glass, then guard. Both pinned .so files are loadable NOW
  (pinned glass 199153ae ldd resolves, cursor-guard 06712eaf full ldd 0 not
  found, live abiHash matches the manifest abi).
- Voice 2 position: AGREE with PRIO council 1 SWAP 1 and council 3 (F1
  before F2, preferably one merged fix with F1 verified first), and AGREE
  with redteam A2 (merge F1 + F2 into ONE fix at rank 1 with ONE end-to-end
  proof: guardian starts, session lives, overlay shows, first visible
  action under 30s). The todolist adopted this (serial rank 2: "Cum fix
  F1+F2 gop mot", gate G-F1-BEFORE-F2). The two workers may CODE in parallel
  only if they do not edit the same session/overlay files at the same time
  (council 3, rank 3); F1 already has uncommitted edits in
  scripts/cursor_session.py and cursor_theme.py, F2 has untracked
  scripts/first_action.py (redteam M4). The merge is a LANDING order, not
  a start order: both already run.
- Disagreement recorded: PRIO council 2 and redteam A1 read the owner's
  "DAU TIEN" (22:16:54) as F2 above F1. Voice 2 DISAGREES on the mechanism
  ground: the owner named the symptom, not the dependency. A rank that
  puts the dependent fix above its precondition is untestable (redteam A2
  proves this against its own A1). The attitude voice concedes the
  priority label belongs to the silence cluster; the dependency voice
  holds the landing order F1 then F2 inside that cluster.

### F3: the unblocker, and its state just changed
- F3 gates every live run (D2). Internal order: verify whether the 22:17
  click already self-healed the slot (redteam A7) -> restore Zen -> fix the
  slot -> finish the 15-tab cleanup last, since the cleanup itself is
  blocked by the slot failure (PRIO council 1, rank 1; todolist serial
  rank 1).
- NEW EVIDENCE since PRIO wrote: sibling M1 records (OPT-M1 mechanism, B5,
  citing F3 log 22:48) that the Marionette slot is FIXED, 67 tabs listed,
  click tab PASS 29ms 1.0px. Voice 2 does NOT declare G-RESTORE met on
  this citation alone: G-RESTORE (todolist) also requires session restore
  of the 28 real tabs, a clickable tab, a renderable web page, and
  workspace switching by command. The F3 log must show all four before
  rank 1 is called done, and F3 must write its diagnosis + restore log
  (PRIO council 3, rank 1: "F3 has no log file yet... A restore with no
  log is unverifiable after the fact"). The file
  improvements/worker-f3-marionette-slot-log.md now exists; the verdict
  paper must check whether it carries the four G-RESTORE proofs.
- J21 (todolist 4.28, owner 22:45): open the Omarchy menu + switch
  workspace by COMMAND (hyprctl dispatch in hl.dsp form), NEVER by
  clicking the workspace/menu button on the bar. CLI first, mouse last.
  This is a dependency of G-RESTORE's workspace-switch proof: the proof
  must be done by command, not by the click that caused the 22:44 incident.

### ZT-B: after F3 AND after F1/F2 verification
- ZT-B must wait for F3 plus F1/F2 verification, since its blind scenarios
  run on the live machine and any computer-use scenario in them needs a
  working session and overlay, and it must hold the single live-runner slot
  alone (PRIO council 1, rank 4). Voice 2 AGREES.
- ZT-B before Y6 trial: keep this order. The Y6 trial changes the pill, so
  ZT-B should observe the current pill, not a mid-change one (PRIO council 1,
  direct answer). Voice 2 AGREES.
- ZT-00 health gate must pass first; R-01 (blind Ctrl+W could close the
  user's real tab) was fixed in v2 but the fix must be verified in the ZT-B
  brief itself, not assumed from the v2 commit message (PRIO council 3,
  rank 4). Voice 2 AGREES: a blind runner on real Zen with real tabs is the
  highest collateral risk in the queue.

### Y6: split the paper from the live trial
- A1-A7 + A9-A10 are paper and config fixes with no live dependency and can
  run in parallel NOW (lane P-C). A8 load-only trial + pill measurement retry
  need the live slot and must wait until F3 + F1/F2 are green, and the retry
  gates on the A9 fresh re-review (PRIO council 1, rank 5 challenge).
  Voice 2 AGREES. The todolist adopted the split (serial rank 4 is the
  A8 trial + retry; lane P-C is the paper fixes).
- Gate G-PILL: ALL of A1-A10 landed, fresh re-review done, F1/F2/F3 stable,
  A8 load-only trial first. No live hyprglass load into the owner's working
  compositor without a handover or idle window (PRIO council 3, G-PILL).
- Voice 2 DISAGREES with redteam A5's proposal to move Y6 to rank 4 ahead
  of Y13/Y14 on readiness grounds alone: readiness is real (Y6 paper needs
  no Zen), but the LIVE retry still needs the live slot after ZT-B, and
  moving the whole rank up would put the retry before the ordinary-user
  error feed that ZT-B produces. The split (paper now, retry at serial 4)
  already captures the readiness advantage without the ordering cost. The
  todolist's serial 4 + lane P-C is the correct form.

### Y13, then Y14: readiness decides the tie, not roadmap alone
- Y13 gates on three things: Y13r2 verdict + H3 gate direction + Marionette
  slot (PRIO council 1, rank 6). Y14 gates on Y14b re-stage clearing
  (PRIO council 1, rank 7). Both need G-RESTORE, G-SINGLE-LIVE, G-HIDDEN,
  G-H2 (todolist serial ranks 5-6).
- Voice 2 AGREES with redteam A5 sub-attack: the Y13-before-Y14 order is
  asserted from roadmap position, not evidenced, and Y14b is already in
  fix-pass-4 while Y13r2 is still in council review. Readiness at run time
  should decide 6 vs 7, not roadmap position. The verdict must state this
  explicitly: at the moment the live slot frees after the Y6 retry, run
  whichever of Y13/Y14 has all its gates green; if both are green, Y13
  first per roadmap; if only one is green, run that one, do not idle the
  slot waiting for the other.
- H3 gate direction (todolist serial rank 5): Y13r2 must produce the H3
  direction before the Y13 live run starts. If Y13r2 is still undecided
  when the slot frees, Y13 waits; the slot does not go to Y14 as a
  workaround unless Y14's own gates are all green (see the readiness rule
  above).

### A1 pilot: paper now, live later, and it does NOT touch Zen
- A1 is a live run needing a healthy stack (F1/F2/F3 green) + broker SOLO +
  idle + relay verified (PRIO council 1, rank 8). Its paper preconditions
  (clone1's 3 blockers) can be worked in parallel now (lane P-D).
- Nuance voice 2 adds: A1 runs on Chromium via CDP, NOT Zen (todolist
  4.15). So A1 does NOT gate on the Marionette slot directly. It gates on
  the healthy stack, the broker, the relay, and the owner-off-keyboard rule
  (17:59 focus lesson). It still holds the single live-runner slot, because
  it drives the same screen and keyboard, and it still needs G-HIDDEN
  pre-flight logic adapted to Chromium (body-visible check on its tab
  before the first action) and G-H2 instrumentation.
- Stale-relay risk (PRIO council 3, rank 8): a relay started before a
  broker change silently runs old code (G1: relay MainPID 106001, started
  00:19 17/11, never restarted, code d45434c on disk only). A1 on a stale
  relay measures the old broker, not the new plan. The A1 brief must verify
  the relay is current before the run starts.
- Voice 2 AGREES with redteam A8: rank 8 depends on an unranked item
  (clone1's verification report, J12, todolist 4.23) unless J12 is ranked.
  The todolist now ranks J12 in lane P-B, which closes A8. A1 resumes only
  after J12 lands AND the 3 blockers are addressed AND all preconditions
  are shown met in writing. No verbal "ready".

### Hidden-body: experiment stays at 8, pre-flight moves forward
- The full decisive experiment (Y4b design: htmlClass + rAF tick on the SAME
  hidden tab in the SAME minute) stays at serial rank 8: it needs a live Zen
  with a drivable tab, and on a broken Zen it produces zero encounters again,
  misread as "hidden body is rare" (PRIO council 3, rank 10).
- But ranks 5-7 (Y13/Y14/A1) can all be killed by the hidden-body failure, and
  they sit BEFORE the experiment. Fix: gate G-HIDDEN pulls the pre-flight
  forward (PRIO council 3, G-HIDDEN). Every live run at ranks 5-7 carries the
  Y4b pre-flight (body-visible check on the tab it will drive, before the first
  action). If the pre-flight fails, the run aborts and reports, it does not
  retry blindly. Voice 2 AGREES with council 1 (fold the pre-flight into Y13)
  and council 3 (G-HIDDEN). The Y4d/Y7 paper follow-ups (test-07 restore
  marker design, test-09 note, first-crash abort) run in lane P-F now, not
  after rank 8.

### H2: folded into the live runs, with a fallback
- H2 does not need its own standalone live run. An agent-driven run with real
  think values can be instrumented onto the next scheduled live run (Y13 or
  A1), and a separate H2 run would burn another solo live slot for data a run
  already in the queue produces (PRIO council 1, SWAP 3; council 3, rank 11).
  Voice 2 AGREES. The todolist adopted the fold (G-H2: think-time
  instrumentation ON at ranks 5-7; H2 no longer runs separately).
- Fallback, stated so the fold cannot silently drop H2: if none of ranks 5-7
  yields usable real think values, H2 runs as a dedicated measurement run,
  and its brief must say so explicitly (PRIO council 3, rank 11). A folded
  H2 with no fallback is a deleted H2.

### Y1b: parallel paper now, absolute gate later
- Y1b probe rewrites gate only the Phase B judgment, and nothing in ranks
  1-11 gates on Y1b (PRIO council 1, rank 12). The work is offline and runs
  in parallel now (lane P-E), rather than waiting behind the live queue.
  Voice 2 AGREES.
- Gate G-Y1B is ABSOLUTE: no executor-hardening merge until all 12 Y1b
  must-fix items are proven fixed AND probes 10b/10f + 1e/4a are rewritten
  (PRIO council 3, G-Y1B). The dangerous case: probes 10b/10f would PASS the
  vulnerable implementation (outer program aborts at the first snippet's 2s
  wall, second run_snippet never executes in EITHER implementation), so a
  Phase B verdict on those probes is a false pass on a security boundary
  (PRIO council 3, rank 12). This gate does not move for schedule pressure.
- Watch status must be re-confirmed before rank 10 work starts: the Y1b live
  watch (Codex PID 184702) has been unconfirmed since about 19:00 (PRIO
  council 3, rank 12).

### Scrub, final test, E1: the tail dependencies
- Scrub (serial rank 11): gates on G-SCRUB (all in-flight pushes landed, PR #1
  resolved or explicitly handled, no live run in flight, every agent notified
  to re-clone). Rank position alone does not create the quiet window; if the
  window is not real when rank 11 arrives, rank 11 WAITS and the wait is
  reported, not silently skipped (PRIO council 3, rank 13 + G-SCRUB).
  Voice 2 AGREES with redteam A6: the scrub as written is a dead letter
  under full-throttle burn, because no quiet window occurs naturally. The
  verdict must name the mechanism: Muse schedules an explicit one-time fleet
  pause with a date, or the scrub is deferred to after the final test.
  PR #1 conflict resolution (todolist 4.26, lane P-G) is a precondition of
  the scrub and runs before it, not with it.
- Final test (serial rank 12): LAST executable item. It exercises the whole
  fixed stack (Zen + driver + Polygon method) and must come after the scrub
  so no force-push disrupts it (PRIO council 1, rank 14). Owner order 16:30,
  confirmed twice. Voice 2 AGREES with council 1 against redteam A6 on one
  point: council 1 says rank 13 (scrub) before rank 14 (final test) is
  load-bearing, and that is correct IF a quiet window is scheduled; redteam
  A6 is correct that without a scheduled window the scrub never runs. Both
  are held by the verdict's scheduled-pause mechanism.
- E1 (todolist 4.22): PARKED, not rank 15. Voice 2 AGREES with redteam A6
  and DISAGREES with PRIO council 1 and council 3, who both AGREE with E1
  at rank 15: nothing may sit after the item the owner said runs LAST
  (owner 16:30, confirmed twice; redteam A6 cites memory lines 1407 and
  1955). E1 needs a NEW experiment design (new labels, new pre-reg, old
  FAILs carried, budget NEW, ceiling conceded, replication pair mandatory)
  and nothing gates on it. The todolist already moved E1 to PARKED
  (todolist, phan quyet 5).

### Clone workers: parallel lanes, split by readiness
- Clone2 heavy batch (todolist 4.16): only its F1/F2/F3 re-review slice
  depends on those diffs landing. The J14 checker follow-ups depend on
  nothing in ranks 1-8 (PRIO council 1, rank 9). Voice 2 AGREES with the
  todolist split: light batch (J14 + batch-5 self-verification + close or
  reassign the J16 watchdog duty) in lane P-A NOW; heavy batch (F-diff
  re-review) at serial rank 9, only after batch 5 is verified AND the
  F1/F2/F3 diffs are frozen (PRIO council 3, rank 9). A review of a moving
  diff is wasted tokens.
- Clone1 (todolist 4.23, lane P-B): the owed batch-4 verification report +
  Firefox rerun results (Y10 t05/t09/t10). Owned by Muse to chase, before
  any A1 resume decision (redteam M1). Batch 6 was issued at 22:40 (blind
  ZT scenarios, evidence audit, re-verify batch-3 + D1); that overlaps the
  subject area but does NOT close J12, because batch 6 re-verifies batch-3
  while the missing file is the batch-4 report (redteam addendum, M1).
- F1/F2/F3 diff commit + push (todolist 4.27, lane P-H): the diffs must land
  as reviewable commits BEFORE clone2 re-reviews them (redteam M4). Standing
  rule D3: push immediately when work is done. This lane is the precondition
  of serial rank 9, not a separate rank.

## Serial vs parallel: the final split
- SERIAL (one live runner, one session, one screen): P0 watch checks,
  F3 restore, F1+F2 merged fix + end-to-end proof, ZT-B, Y6 A8 trial +
  pill retry, Y13, Y14, A1 live, hidden-body live experiment, H2
  fallback run (only if the fold yields nothing), scrub (in its scheduled
  window), final test.
- PARALLEL LANES (start now, no live slot, no session): P-A clone2 light
  batch (J14 + batch-5 self-verify + J16 close); P-B clone1 J12 + Firefox
  reruns; P-C Y6 paper A1-A7/A9-A10; P-D A1 paper preconditions (clone1
  3 blockers); P-E Y1b probe rewrites; P-F Y4d/Y7 paper follow-ups;
  P-G PR #1 conflict resolution; P-H F1/F2/F3 diff commit + push.
- NEVER PARALLEL: two live drivers on one Zen; a live run overlapping
  F1/F2/F3 live probing on the same Zen; a hyprglass live load while F-team
  live work is in flight; the scrub while any push is in flight.

## Voice 2 summary of agreements and disagreements
- AGREE with PRIO council 1 on: F1 before F2 (SWAP 1, preferably merged);
  paper work in a parallel lane now (SWAP 2); H2 folded into Y13/A1
  (SWAP 3); ZT-B after F3 + F1/F2; Y6 split; scrub-before-final-test
  ordering; G-TAB sacrificial-tab rule.
- AGREE with PRIO council 3 on: all gates G-RESTORE, G-TAB,
  G-F1-BEFORE-F2, G-SINGLE-LIVE, G-HIDDEN, G-VMFIX, G-PILL, G-SCRUB,
  G-Y1B, G-FINAL-LAST; clone2 split (light now, heavy after batch-5
  verification + frozen diffs); hidden-body pre-flight forward.
- AGREE with redteam on: A2 (F1+F2 merged, one end-to-end proof); A7
  (cheap Marionette retry check first); A8 (J12 must be ranked or A1
  is a wish); M1 (J12 in lane P-B); M2 (PR #1 in lane P-G before scrub);
  M4 (diffs committed before re-review); A6 (E1 parked, nothing after
  LAST).
- DISAGREE with PRIO council 1 and council 3 on: E1 at rank 15 (it must
  be PARKED, per redteam A6 and the owner's LAST order).
- DISAGREE with redteam A5 on: moving the whole Y6 rank ahead of Y13/Y14
  (the split already captures the readiness advantage; the live retry
  still belongs after ZT-B).
- AGREE with sibling OPT-M1 mechanism on: B cannot be proven until A is
  green (B5); glass-then-guard load order (A7); three different proofs
  for A, B, C2 (cross-class summary). NEW INPUT from M1: F3 slot FIXED
  22:48 (67 tabs, click PASS 29ms 1.0px) is recorded here as a state
  change to verify against G-RESTORE, not as a G-RESTORE pass.
- Sibling OPT-M2 verdict: NOT YET WRITTEN at 22:56. No agreement or
  disagreement can be recorded. The verdict paper must note this gap.

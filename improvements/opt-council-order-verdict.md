# OPT-ORDER VERDICT: the optimal fix order for the whole error pile
# Council OPT-ORDER (3 voices), verdict paper. Written 22:54 +07, Sat 2026-11-21.
# Parent: Worker OPT (method coordinator). Owner orders: 22:46-22:47 find ONE
# optimal fix method; 22:48 follow Lauren Tan strictly, NO skipped steps;
# 22:49 commit more and smaller, graph target 240 before midnight;
# correction 22:51 graph counts main branch only.
# Method: 3 voices debated (attitude, dependency, risk/cost) from PRIO's
# ranking + PRIO council 1/2/3 + PRIO redteam + sibling OPT-M1 and OPT-M2
# mechanism papers. This verdict is written so the redteam can attack it.
# No em/en dashes in this file. Every claim carries a file:line or quote
# citation (evidence contract).

## Section 1. THE ORDERED QUEUE (serial live queue + parallel lanes)

### 1.1 What this verdict does to PRIO's ranking
PRIO's ranking (improvements/worker-prio-crawl-log.md, draft queue 1-15)
was debated by PRIO council 1 (mechanism), council 2 (owner attitude),
council 3 (risk), and redteam A1-A8 + M1-M5, then DECIDED into the todolist
priority section (docs/zen-error-fix-todolist-20261121.md lines 1-40):
serial queue 1-12 + parallel lanes P-A..P-H + gates. This verdict REUSES
that decided queue and amends it ONLY where method evidence changes it.
Each amendment below carries its reason. Where this verdict agrees with the
todolist, it says so and does not re-decide.

### 1.2 The serial live queue (ONE runner, ONE session, ONE screen)
- P0. VMFIX watch (standing check, not a rank). VMFIX DONE 22:40: SSH
  restored durably (F1 fixed re/__init__.py from CPython 3.12.3, dpkg -V
  clean, observe 22:38 ok); guardian failure NOT due to re (todolist
  priority section, P0). OPEN tail: the deleter is still UNKNOWN, so
  re-verify `python3 -c "import re"` OK + `ssh-laptop.sh echo SSH_OK`
  before each live run from rank 3 onward (G-VMFIX). If SSH or Python
  breaks mid-queue: FREEZE all live work at once, VM-local work only.
- 1. F3 Zen restore + Marionette slot + 15-tab cleanup (todolist 4.7/4.8/
  4.10). Internal order: cheap Marionette retry check FIRST (redteam A7:
  the 22:17 click may already have self-healed the slot) -> restore Zen ->
  fix the slot -> finish the 15-tab cleanup LAST. STATE CHANGE 22:50:
  the Zen restart restored the 39 fixture tabs (owner screenshot 22:50;
  MEMORY.md entry 22:49-22:51), and F3 is re-running the FULL cleanup with
  the same 28-real-tab keep-list. So the 22:48 slot-fixed evidence (M1
  mechanism B5: session 0.1s, 67 tabs, click PASS 29ms 1.0px) is NOT a
  G-RESTORE pass: G-RESTORE must be re-verified AFTER the re-run
  (28 real tabs restored, clickable tab, renderable web page, workspace
  switch by command). F3 must write its diagnosis + restore log before
  rank 1 is called done (PRIO council 3, rank 1). AMENDMENT O-1 (reason:
  the restart changed the tab state after the 22:48 evidence, so the old
  evidence cannot close the rank): rank 1 closes only on a fresh
  G-RESTORE verification after the FULL cleanup re-run.
- 2. F1+F2 merged cluster, ONE end-to-end proof (todolist 4.11/4.12).
  F1 FIRST inside the cluster (session starts, guardian ready, glass
  loaded then guard loaded, overlay exists), F2 SECOND (first visible
  action under 30s, continuous ops, overlay always on). Gate
  G-F1-BEFORE-F2: F2 is measured only when F1 is green. The cluster is the
  owner's FIRST fix (owner 22:16:54 "fix DAU TIEN va fix TOI UU TOT NHAT");
  F3 at rank 1 is its wall-clock unblocker, not a demotion (voice 1).
  Sibling M2 adds the D-method for the slot side and M1 adds the A-method
  for the session side; neither changes this rank.
- 3. ZT-B blind ordinary-user Zen tests (todolist 4.9). Gates: G-RESTORE,
  ZT-00 pass, R-01 guard restated in the brief (pre-close check before
  EVERY Ctrl+W; blind runner must stop at once on any unexpected focus
  change). ZT-B before the Y6 trial: ZT-B observes the current pill, not a
  mid-change one (PRIO council 1).
- 4. Y6 A8 load-only trial + pill measurement retry (todolist 4.13).
  Paper fixes A1-A7/A9-A10 run in lane P-C NOW. Gate G-PILL: ALL of A1-A10
  landed, fresh re-review done, F1/F2/F3 stable, A8 trial first. No live
  hyprglass load into the owner's working compositor without a handover or
  idle window. Sibling M2 adopts the Y6r A1-A10 list whole, including A7
  (no manual reload) and the precision limit (config() applied proven,
  layer() registration unproven until the A3 positive marker lands)
  (OPT-M2 mechanism, section F). AMENDMENT O-2 (reason: M2's precision
  limit): the retry's success criterion is the A3 positive marker proving
  the FULL profile (layer registration + material values), not merely
  config() applied. A retry that proves only config() applied is a NO
  VERDICT, not a pass.
- 5. Y13 live run (todolist 4.14). Gates: G-RESTORE, G-SINGLE-LIVE,
  G-HIDDEN, G-H2, Y13r2 verdict + H3 gate direction + Marionette slot.
- 6. Y14 live run (todolist 4.14). Gates as above + Y14b re-stage clearing.
  AMENDMENT O-3 (reason: redteam A5 sub-attack, agreed by voices 2 and 3):
  Y13-before-Y14 is roadmap order, not evidence. At the moment the live
  slot frees after rank 4, run whichever of Y13/Y14 has ALL its gates
  green; if both are green, Y13 first per roadmap; if only one is green,
  run that one, do not idle the slot waiting for the other.
- 7. A1 pilot resume (todolist 4.15). Preconditions in writing: clone1's 3
  blockers addressed (J12 landed, lane P-B) + written order naming 12
  run-ids + broker SOLO + idle + relay verified (stale-relay check: relay
  must be current, G1 lesson) + Layer-2 probes + checker real-run
  cross-check. Chromium via CDP, NOT Zen: A1 does not gate on the
  Marionette slot directly, but it holds the single live-runner slot
  (same screen/keyboard) and needs the G-HIDDEN pre-flight adapted to
  Chromium + G-H2 instrumentation.
- 8. Hidden-body decisive experiment + Y4d/Y7 follow-ups (todolist 4.17).
  The full experiment (Y4b 6-phase design) stays here; its pre-flight is
  pulled forward into ranks 5-7 via G-HIDDEN (see section 1.4). Sibling M2
  kills V2 (transition frozen, DEAD as stated) and stale-geckodriver (DEAD)
  as mechanisms, wounds V1 (stuck class, not dead), and requires the third
  mechanism (grouping-rule / hidden-sheet blind scan) as a live hypothesis
  (OPT-M2 mechanism, section G). AMENDMENT O-4 (reason: M2's falsification):
  the fix design's V2 category and repaint step are REMOVED; the
  switch-away step is REMOVED (it drives a user tab, a focus steal); any
  test that passes only after `removed-tz-hidden` is a FLAGGED pass,
  counted separately, never folded into the headline pass count.
- 9. Clone2 heavy batch (todolist 4.16). Only after batch 5 is verified AND
  the F1/F2/F3 diffs are frozen (committed + pushed, lane P-H). Content:
  independent re-review of the F1/F2/F3 diffs. Light batch runs NOW in lane
  P-A (see section 1.3).
- 10. Y1b snippets (todolist 4.19). Gate G-Y1B ABSOLUTE: no
  executor-hardening merge until all 12 must-fix items are proven fixed AND
  probes 10b/10f + 1e/4a are rewritten. Probe rewrites run NOW in lane P-E.
- 11. Email + real-name history scrub (todolist 4.20). Gate G-SCRUB: runs
  ONLY in a verified quiet fleet window (all pushes landed, PR #1 resolved
  or explicitly handled, no live run in flight, every agent notified to
  re-clone). AMENDMENT O-5 (reason: redteam A6 + voice 3 R6, the scrub
  timing trap): "rank 11" without a mechanism is not a plan. Muse schedules
  an explicit one-time fleet pause WITH A DATE, announced to all agents,
  after the final test is briefed but before it runs, OR the scrub is
  deferred to AFTER the final test. If deferred, the verdict says plainly:
  the final test is then the last WORK item, not the last executed item.
  The owner's LAST order is not silently redefined.
- 12. Final test, independent Codeforces contest, 5 problems (todolist
  4.21). LAST work item (owner 16:30, confirmed twice). Gates: G-RESTORE,
  G-SINGLE-LIVE, per-step time logging.

### 1.3 The parallel lanes (start NOW, no live slot, no session)
- P-A. Clone2 light batch: J14 batch-3 checker follow-ups + batch-5
  self-verification + formally close or reassign the J16 watchdog duty
  (zero logs since 19:09). Burns tokens NOW, satisfying the owner's 22:31
  order immediately.
- P-B. Clone1 J12: owed batch-4 verification report +
  Firefox rerun results (Y10 t05/t09/t10). Owned by Muse to chase, before
  any A1 resume decision. Batch 6 (issued 22:40) does NOT close J12.
- P-C. Y6 paper A1-A7/A9-A10 (feeds serial rank 4).
- P-D. A1 paper preconditions: clone1's 3 blockers (feeds serial rank 7).
- P-E. Y1b probe rewrites 10b/10f + 1e/4a (feeds serial rank 10).
- P-F. Y4d/Y7 paper follow-ups: test-07 restore marker design, test-09
  note, first-crash abort (feeds serial rank 8).
- P-G. PR #1 conflict resolution (coord file, not code). Precondition of
  the scrub, runs before it.
- P-H. F1/F2/F3 diff commit + push (standing rule D3). Precondition of
  serial rank 9 (clone2 re-review needs reviewable committed diffs).
- LANE BOUNDARY (voice 3, R3): any lane work that starts driving the live
  machine stops being a lane and joins the serial queue. Every lane brief
  carries that sentence.

### 1.4 Gates carried forward (all of them, none dropped)
G-VMFIX, G-RESTORE, G-TAB, G-F1-BEFORE-F2, G-PILL, G-SINGLE-LIVE, G-HIDDEN,
G-H2, G-SCRUB, G-Y1B, G-FINAL-LAST (todolist priority section). Two folds
adopted from PRIO council 1/3: G-HIDDEN pre-flight rides on every live run
at ranks 5-7 (abort and report on pre-flight failure, never retry blindly);
G-H2 think-time instrumentation rides on ranks 5-7, with the fallback that
if no live run yields real think values, H2 runs as a dedicated measurement
run and its brief says so explicitly. AMENDMENT O-6 (reason: M2 section G):
G-HIDDEN's pre-flight payload is the M2 `diagnose_body` snapshot
(readyState, documentElement classList, body computed visibility/opacity/
display + html visibility, body inline style, transition, rect, innerText
length, hasFocus/visibilityState, URL), sampled twice 300 ms apart when
hidden. A pre-flight that does not capture htmlClass is not a pre-flight.

### 1.5 PARKED (with exact unpark conditions, voice 3 R4)
- Track 2 + speed loop: council + redteam UNANIMOUS agreement in writing
  that no further optimization is possible. No such decision exists.
- Super I follow-ups: owner re-opens it (deferred 17:42).
- 2.1.7 I7 video: owner re-sends the original file.
- Pending user decisions: owner decides.
- E1 fresh comparison: PARKED, not a rank. Unpark needs a NEW design
  (new labels, new pre-reg, old FAILs carried, budget NEW, ceiling
  conceded, replication pair mandatory) reviewed + owner schedules it. If
  ever scheduled as real work, it runs BEFORE the final test. AMENDMENT O-7
  (reason: redteam A6, agreed by all three voices): E1 must NOT sit after
  the LAST item. The todolist already moved E1 to PARKED; this verdict
  locks that in and forbids re-ranking it after rank 12.
- J15 17:59 freeze cause: recurs, then it jumps the queue at once (safety).
- J7 deleter: not a rank, lives as the watch tail inside G-VMFIX.

### 1.6 Amendments summary (PRIO decided queue -> this verdict)
- O-1: rank 1 closes only on fresh G-RESTORE after the FULL cleanup re-run
  (tab state changed 22:50).
- O-2: Y6 retry success = A3 positive marker proving the FULL profile,
  not config() applied alone (M2 precision limit).
- O-3: Y13/Y14 order by readiness at run time, not roadmap alone.
- O-4: hidden-body design drops V2 + repaint + switch-away; flagged-pass
  accounting (M2 falsification).
- O-5: scrub needs a scheduled fleet pause with a date, or deferral after
  the final test, stated plainly.
- O-6: G-HIDDEN pre-flight payload is the M2 diagnose_body snapshot.
- O-7: E1 locked in PARKED, never re-ranked after the final test.

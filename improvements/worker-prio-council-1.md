# Council 1 (mechanism / dependencies) verdict - Worker PRIO ranking debate
# Time: 22:41 +07, Sat 2026-11-21. Inputs read: improvements/worker-prio-crawl-log.md
# (J7-J16 + DRAFT ranked queue 1-15), docs/zen-error-fix-todolist-20261121.md,
# LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md section 12 (J1-J6) and parts A-I.
# Lens: what gates on what. No em/en dashes in this file, hyphens only.

## Hard mechanism constraints (these decide the order, not preference)

- H1. ONE live runner at a time. F1, F2, F3, ZT-B, Y6 trial, Y13, Y14, A1,
  hidden-body experiment, H2 run, final test all drive the same live machine
  and the same owner screen. They must be strictly serial, never overlapping.
- H2. ONE session TOTAL shared by BiDi + Marionette (todolist 1.2.1). No two
  live drivers can hold a session at once. This is the mechanical reason the
  live queue must be serial, not just a politeness rule.
- H3. F3 gates every live run. A usable Zen plus a working Marionette slot is
  a precondition for ZT-B, Y13, Y14, A1, Y6 trial, hidden-body, H2, final test.
  Nothing live runs before F3.
- H4. VMFIX/SSH is a hidden gate on ranks 1-3. F1/F2/F3 laptop work assumes SSH
  is stable, but J7 self-restored 22:31 with unknown cause and VMFIX has not
  confirmed it yet. If SSH dies again, ranks 1-3 stall. Track VMFIX, do not
  assume stability.
- H5. The scrub (rank 13) is a breaker, not just a task. Filter-repo plus
  force-push plus all-agents re-clone plus PR #1 handling breaks in-flight
  pushes, so it must only run in a quiet fleet window, never mid-flight.

## Verdicts per rank (one line of technical reasoning each)

1. F3 Zen restore + Marionette slot + 15-tab cleanup: AGREE. Every live run
   needs a usable Zen plus a working Marionette session and only F3 restores
   both, but internal order must be restore Zen, then fix the slot, then finish
   the 15-tab cleanup last, since the cleanup itself is blocked by the slot
   failure (J3).
2. F2 silence fix: CHALLENGE. F2 cannot be proven fixed while F1 fails, because
   F2's overlay-always-on and sub-30s first visible action both presuppose a
   session that starts, and F1's guardian startup is exactly what is failing.
3. F1 guardian/session fix: CHALLENGE as ranked. F1 is the upstream dependency
   of F2 so F1 belongs at rank 2, not rank 3, and both touch the same session
   startup and overlay show path (F1 already has uncommitted edits in
   scripts/cursor_session.py and cursor_theme.py), so they must land as one
   pipeline with F1 verified first.
4. ZT-B blind ordinary-user Zen tests: AGREE. ZT-B must wait for F3 plus F1/F2
   verification, since its blind scenarios run on the live machine and any
   computer-use scenario in them needs a working session and overlay, and it
   must hold the single live-runner slot alone.
5. Y6 A1-A10 fix list + pill measurement retry: CHALLENGE as bundled. A1-A7
   plus A9-A10 are paper and config fixes with no live dependency and can run
   in parallel now, while A8 load-only trial plus the pill measurement retry
   need the live slot and must wait until F3 plus F1/F2 are green, and the
   retry itself gates on the A9 fresh re-review.
6. Y13 live run, codex-y5: AGREE. Y13 is first in the live queue per roadmap
   and gates on the Y13r2 verdict plus the H3 gate direction plus the
   Marionette slot from rank 1, and it must run solo on the live slot after
   ZT-B and the Y6 trial.
7. Y14 live run, batch-3: AGREE. Y14 follows Y13 in the live queue, gates on
   Y14b re-stage clearing, and must run solo on the live slot after Y13.
8. A1 pilot resume: AGREE as a live-run position. A1 is a live run needing a
   healthy stack (F1/F2/F3 green) plus broker SOLO plus idle plus relay
   verified, so its position after Y13/Y14 is correct, though its paper
   preconditions (clone1's 3 blockers) can be worked in parallel now.
9. Clone2 heavy batch: CHALLENGE. The clone2 batch as a sequential rank is
   wrong, because the J14 checker follow-ups have no dependency on ranks 1-8
   and clone2 works through the repo without consuming the live slot, so only
   the F1/F2/F3 re-review portion waits on those diffs landing.
10. Hidden-body decisive experiment + Y4d/Y7 follow-ups: CHALLENGE as bundled.
    The hidden-body live experiment agrees at rank 10 since it needs F3 and the
    solo live slot, but the Y4d/Y7 paper follow-ups (test-07 restore marker
    design, test-09 note, first-crash abort) have no live dependency and can
    run in parallel now.
11. H2 think-time measurement, agent-driven: CHALLENGE. H2 does not need its
    own standalone live run, since an agent-driven run with real think values
    can be instrumented onto the next scheduled live run (Y13 or A1), and a
    separate H2 run would only burn another solo live slot for data a run
    already in the queue can produce.
12. Y1b snippets: AGREE as priority, not as sequence. Y1b probe rewrites gate
    only the Phase B judgment and nothing in ranks 1-11 gates on Y1b, so rank
    12 priority is right, but the work is offline and should run in parallel
    now rather than waiting behind the live queue.
13. Email + real-name history scrub: AGREE. The scrub must stay late because
    filter-repo plus force-push plus all-agents re-clone plus PR #1 handling
    would break in-flight pushes if done early, and it hard-gates on a quiet
    fleet window with PR #1 resolved.
14. Final test, independent Codeforces contest: AGREE. The final test is
    ordered LAST by the owner and mechanically must be last, since it exercises
    the whole fixed stack (Zen plus driver plus Polygon method) and must come
    after the scrub so no force-push disrupts it.
15. E1 fresh comparison: AGREE. E1 needs a NEW experiment design (new labels,
    new pre-reg, budget NEW, replication pair) and nothing gates on it, so last
    is correct, and its live comparison also needs the owner off the keyboard
    per the 17:59 focus rule.

## Order swaps demanded

- SWAP 1 (demanded): ranks 2 and 3 swap. F1 goes to rank 2, F2 goes to rank 3.
  Dependency justification: the direction is F1 -> F2, not F2 -> F1. A session
  that never starts (J4) cannot produce a first visible action in under 30s
  (J5), and an overlay that never shows cannot be made always-on. F2's
  acceptance test therefore gates on F1 green. Both workers are already
  RUNNING, so the swap governs landing order and verification order, not start
  order. Preferred form: merge them into ONE fix owned by one worker, F1 phase
  first (session starts, guardian ready), F2 phase second (first visible action
  under 30s, continuous ops, overlay always on), with F1 verified before F2 is
  judged. Separate workers editing the same startup path risk conflicting edits
  in cursor_session.py and cursor_theme.py.
- SWAP 2 (demanded): pull the paper work out of the sequential queue into a
  parallel lane now. Affected: Y6 paper portion of rank 5 (A1-A7, A9-A10), A1
  paper preconditions of rank 8 (clone1 blockers), clone2 J14 follow-ups of
  rank 9, Y4d/Y7 paper follow-ups of rank 10, Y1b of rank 12. Dependency
  justification: none of these consume the live slot, none depend on ranks 1-8
  except the F1/F2/F3 re-review slice of rank 9, which waits only on those
  diffs landing. Serializing them behind live runs wastes worker capacity while
  the live slot is the bottleneck. The sequential queue keeps only the live
  parts: F3, F1/F2, ZT-B, Y6 trial/retry, Y13, Y14, A1 live, hidden-body live.
- SWAP 3 (demanded): fold rank 11 (H2) into the next scheduled live run, Y13
  or A1, and delete the standalone H2 run. Dependency justification: H2 needs
  an agent-driven run with real think values, and Y13/A1 already are
  agent-driven live runs on the fixed stack. Instrumentation added to either
  run closes H2 with zero extra live slots. A standalone H2 run adds a full
  live-slot cycle for data the queue already produces.
- NO SWAP for ranks 13/14/15. Rank 13 before rank 14 is load-bearing: the scrub
  must land before final-test work starts pushing, or the force-push plus
  re-clone disrupts it. Rank 15 stays last because nothing depends on E1.

## Direct answers to PRIO's mechanism questions

- Can Y13/Y14 live runs or ZT-B run before F3 restores Zen and fixes the
  Marionette slot? No. All three gate on F3 per H3. ZT-B browser-only scenarios
  could in principle run on a limping Zen, but blind tests on a broken browser
  produce noise, and every driver-based scenario is blocked by the slot failure.
- Can the Y6 A1-A10 fixes and the pill retry run while F1/F2/F3 are still
  working the live machine? Paper fixes yes, live trial and retry no. One live
  runner at a time (H1) plus one shared session (H2) forbid it. The A8 trial
  and the pill measurement retry must wait for F3 plus F1/F2 green and then
  hold the slot alone.
- Does the clone2 batch at rank 9 depend on anything? Only its F1/F2/F3
  re-review slice depends on those diffs landing. The J14 checker follow-ups
  depend on nothing in ranks 1-8.
- Does anything ranked late block something ranked early? No hard block. The
  scrub (13) would block everything if moved early, which is why it stays
  late. Y1b (12) blocks only the Phase B judgment, not ranks 1-11. H2 (11)
  blocks nothing, A1 already carries its own measured win. Hidden-body (10)
  does not hard-block Y13/Y14 because the pre-flight body-visible check
  mitigates it, but if the decisive experiment is cheap, fold its pre-flight
  check into Y13 rather than waiting for rank 10.
- ZT-B (4) before Y6 trial (5): keep this order. The Y6 trial changes the
  pill, so ZT-B should observe the current pill, not a mid-change one.

## Summary

- Agree: 1, 4, 6, 7, 8, 12 (priority only), 13, 14, 15.
- Challenge: 2, 3 (swap), 5 (split), 9 (parallelize), 10 (split), 11 (fold in).
- Demanded: F1 before F2 (swap ranks 2/3, preferably one merged fix with F1
  verified first); paper work runs in a parallel lane now; H2 folds into Y13
  or A1; live queue stays strictly serial under the one-runner, one-session
  constraints.

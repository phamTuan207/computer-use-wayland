# Redteam verdict - against Worker PRIO's draft ranking
# Written: 22:44 +07, Sat 2026-11-21. Redteam for PRIO, per owner order 22:32.
# Sources read: improvements/worker-prio-crawl-log.md (draft queue 1-15),
# docs/zen-error-fix-todolist-20261121.md (169 lines),
# ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md section 12 (J1-J6),
# ~/memory/2026-11-21.md (owner quotes 22:16, 22:18, 22:21, 22:29-22:32, 22:36-22:37),
# live git status 22:44.
# Rule: no em/en dashes anywhere in this file. Every attack cites a file/line
# or an owner quote with a time.

## Verdict in one line
PRIO's draft is a reasonable serial list, but it disobeys the owner's literal
orders in three places (F2 is not first, clone2 is buried at 9, E1 sits after
the item the owner said runs LAST), it ranks F2 above the fix F2 depends on,
and it drops two of its own findings (J12, PR #1) out of the queue entirely.

## Attack A1. F2 at rank 2 violates the owner's literal FIRST order
- Owner quote, 22:16:54, ~/memory/2026-11-21.md line 2394: the silence
  weakness ("Muse nghi lau im lang, man hinh dung yen, khong thay
  computer-use bat") must be fixed "DAU TIEN va fix TOI UU TOT NHAT".
  PRIO's own lens line quotes this exact phrase, then ranks the item second.
  A lens that quotes the order and then disobeys it is not a lens, it is a
  contradiction.
- PRIO's defence for F3 first is "owner cannot use the user's browser at all
  (22:25)". But the owner said at 22:27 the user was going to sleep
  (memory, section "dang chi dao 22:29-22:32 (sau khi noi di ngu 22:27)").
  The user is not using the browser right now. The urgency that justifies F3
  first is blunted by the user's own sleep, while the FIRST order has no
  such expiry.
- F2's fix is mostly code and hard rules (first-visible-action under 30s,
  session-start watchdog, fallback Pointer, overlay always on). It does not
  need Zen restored to be built and unit-tested. F3's restore is already
  RUNNING (spawned 22:18), so ranking F2 first costs F3 nothing: F3 keeps
  running while F2 becomes the named priority.
- Proposed: F2 rank 1. F3 rank 2.
- Extra hole: PRIO ranks F2 on the 22:21 spec, but the 22:21 redirect to F2
  ("Ko can noi truoc...") has no worker acknowledgment yet (memory, flush
  22:21: "da gui redirect cho F2 theo huong nay... chua co xac nhan tu
  worker"). The queue assumes F2 heard the correction. It has not been
  confirmed.

## Attack A2. F2 cannot be tested before F1 lands, so F2 above F1 is untestable
- PRIO's own note on rank 3 admits it: "F2's overlay-always-on needs F1's
  session". If the guardian never starts a session (J4, error file section
  12, todolist 4.11), there is no session for F2's watchdog to watch and no
  overlay holder to show. F2's end-to-end proof (session starts AND overlay
  shows AND first action under 30s) is impossible until F1 lands.
- Worse, F2's own fallback proves the trap. The 22:17 direct Pointer click
  worked in 0.31s but produced NO overlay, and the owner flagged that as a
  fresh error at 22:18:03: "click thanh cong nhung cac overlay ko he bat",
  then "Lai loi roi" (memory, flush 22:17/22:18). F2's fallback path, as
  designed, CREATES the overlay-absent defect unless F1's session/overlay
  path works. Ranking F2 above F1 puts the dependent fix first and its
  precondition second.
- Proposed: merge F1 + F2 into ONE fix at rank 1 with ONE end-to-end proof
  (guardian starts, session lives, overlay shows, first visible action
  under 30s). If they must stay separate, F1 goes before F2, not after.
  Either way the draft order (F2 rank 2, F1 rank 3) is backwards.

## Attack A3. VMFIX is unranked, but it preconditions F1 and all laptop work
- PRIO writes "queue tracks VMFIX's confirmation" and gives VMFIX no rank,
  no owner, no check. That is not tracking, it is a footnote.
- Evidence it matters: memory, flush 22:36-22:37. /usr/lib/python3.12/re.py
  is STILL missing, the re package is 3.13-style files under 3.12, state
  "chua ben" (not stable). VMFIX is PENDING with no result. And Muse
  flagged the direct link to F1: "kiem tra guardian co import re khong
  (neu co, re hong co the la goc re cua loi guardian startup fail)".
  F1's root cause may be the re breakage, not F1's own code. Every
  laptop-side fix (F1, F2, F3) also depends on SSH, which died 22:25-22:31
  and self-restored by an unknown cause (J7).
- Proposed: VMFIX becomes explicit precondition P0, checked before any
  laptop-side fix is declared done: SSH stable + re healthy + F1 answers
  "does the guardian import re" first. A queue that ranks F1 third while
  its possible root cause sits unranked is ranking symptoms above causes,
  against the todolist's own first principle ("tim goc sua goc").

## Attack A4. Clone2 at rank 9 contradicts the owner's 22:31 order and ignores in-flight batch 5
- Owner quote, 22:29-22:32, memory line 2484: "dot manh token cua clone2
  hon di, no it viec va viec cua no nhe qua roi" and "vat kiet cac nhan
  vien". The owner ordered clone2 burned HARDER. PRIO answers by placing
  clone2 ninth, behind three Zen-gated items (Y13, Y14, A1 pilot) that
  cannot even start until F3's Marionette slot is fixed.
- Clone2 runs on its own machine with zero dependence on Zen, F3, F1 or F2.
  Serializing a parallel, independent lane behind blocked serial work is
  the opposite of "vat kiet" (squeeze dry). The owner's order is about
  throughput now, not queue position later.
- The draft is also stale on clone2's actual state. Batch 5 was already
  issued and pushed (commit c77e8a1): task 1 repo crawl, task 2 blind ZT
  on clone2's own Firefox, task 3 independent evidence check (memory,
  flush 22:37). Rank 9 proposes issuing a new batch as if clone2 were
  idle. It is not idle. Issuing batch 6 before batch 5 lands double-books
  the lane.
- Note the knock-on: batch 5 task 2 (blind ZT on clone2's Firefox) already
  starts the ordinary-user error hunt that rank 4 (ZT-B) is supposed to do
  after F3. ZT coverage does not need to wait for F3 at all.
- Proposed: clone2 leaves the serial queue entirely and becomes parallel
  lane 1, running from now. Batch 6 is issued the moment batch 5 lands,
  not at rank 9. Rank 9 is deleted as a serial position.

## Attack A5. Y6 A1-A10 at rank 5 sits behind Y13/Y14 on roadmap inertia, not owner order
- 2.2.3 is the only queue item that is an explicit OPEN GOAL item
  (todolist 2.2.3, goal item 2.2.3). Y13/Y14 are ordered by "live queue
  order per roadmap". Roadmap position is a process artifact, not an owner
  quote. No owner quote in the crawl puts Y13/Y14 above the pill
  measurement.
- Readiness cuts the other way. Y13 live is gated on three things not yet
  in hand (Y13r2 verdict + H3 gate direction + Marionette slot, the last
  one being F3's unsolved J3). Y14 live is gated on Y14b re-stage clearing.
  Y6 A1-A10 is code and config work with no Zen dependence: Y6e's nested
  load test passed 21:57 without touching live Hyprland (memory, Y6r
  section). A1 (stage y6e conf as active conf), A5 (port AMEND4/AMEND5),
  A9 (re-review fix diff) can all proceed while F3 is still broken.
- The record is also wrong right now and Y6 A4 exists to fix it. Y6r
  proved the live record false: the profile WAS applied in the Y6e run
  (config() at parse 2, features.layers.enabled = true), and the old notes
  saying "profile chua ap dung" (Y6e log line 561, Y6r V4/V5, council 2
  item 1g, council 3 F3) are WRONG (memory, flush 22:37, Y6r section).
  That false record sits on main while the queue waits.
- Proposed: Y6 A1-A10 moves to rank 4 (ahead of Y13/Y14), or into the
  parallel lane with clone2. ZT-B and Y13/Y14 follow.
- Sub-attack on ranks 6-7: the Y13-before-Y14 order is asserted, not
  evidenced. Y14b is already in fix-pass-4 (commit bf3c939, redteam AMEND
  bd3c6c9 22:22) while Y13r2 is still in council review. Readiness at run
  time should decide 6 vs 7, not roadmap position.

## Attack A6. Scrub 13 vs final test 14 vs E1 15: the tail of the queue breaks the owner's LAST order
- The owner stressed TWICE that the final test runs last: memory line
  1407 ("Dang nhan manh 2 lan: GIO CHUA LAM final test, lam het va hoan
  thien moi viec khac truoc da... chay cuoi cung") and line 1955
  ("final test chay CUOI CUNG sau khi xong het moi viec khac"). PRIO
  ranks E1 fresh comparison at 15, AFTER the item the owner said runs
  LAST. Nothing may sit after the last item. E1 is deferred by council
  and redteam and needs a NEW experiment design anyway. It belongs in
  PARKED, not rank 15.
- The scrub at 13 has the opposite problem: its precondition contradicts
  the owner's burn order. J8 needs a quiet fleet window (filter-repo +
  force-push + all agents re-clone + PR #1 handling), and MEMORY.md says
  the full-history scrub waits for fleet idle because a force push now
  would break in-flight pushes. Under the owner's 22:31 order (full
  throttle, burn clone2 harder), no quiet window will ever occur
  naturally. Rank 13 as written is a dead letter: it will never execute,
  because the fleet is ordered never to be quiet.
- Proposed: final test becomes the last executable item. The scrub either
  gets an explicit scheduled fleet pause (a coordinated one-time window,
  owned by Muse, with a date) or it is deferred to after the final test.
  E1 moves to PARKED. PRIO must pick one mechanism for the scrub and
  write it down; "rank 13" without a mechanism is not a plan.

## Attack A7. Rank 1 may be ranking a fix that already happened
- F3's own first step, per memory (flush 22:18/22:19), is a retry
  hypothesis: the 22:17 Welcome click "co the da sua duoc slot", and the
  hypothesis is "CHUA kiem chung" (untested). If the Marionette slot
  self-healed when the click landed, rank 1's work is a 2-minute
  verification, not a fix job. PRIO ranks it first without the cheap
  check first. Minor, but the queue should start with "retry Marionette
  session now" before treating F3 as a full repair.

## Attack A8. A1 pilot at rank 8 rests on an unranked unblocker
- Rank 8 says resume only after clone1's 3 blockers are addressed plus
  preconditions. But clone1's own verification report (J12) is missing
  and unranked (see M1). The pilot's unblocker is itself blocked on an
  item with no queue position. A rank that depends on an unranked item is
  not a rank, it is a wish.

## Missed items PRIO failed to list or rank

### M1. J12 has a todolist number (4.23) but NO queue position
- PRIO's own finding J12: clone1 owes the batch-4 verification report
  (docs/clone1-batch23-verification-20261121.md does NOT exist) plus the
  Firefox rerun results for Y10 t05/t09/t10 dispatched 19:27, never
  landed. PRIO proposes todolist 4.23, then the 1-15 queue never mentions
  4.23. Check the queue: ranks 1-15 cover 4.7/4.8, 4.12, 4.11, 4.9, 4.13,
  4.14, 4.15, 4.16, 4.17, 4.18, 4.19, 4.20, 4.21, 4.22. 4.23 is absent.
  PRIO dropped its own finding from its own ranking. It also matters:
  the A1 pilot (rank 8) needs clone1's blockers addressed, and the
  missing verification report is the evidence for that.
- Proposed: 4.23 enters the parallel lane (clone1's lane), owned by Muse
  to chase, before any A1 resume decision.

### M2. PR #1 CONFLICTING on GitHub: mentioned, never ranked, no owner
- Evidence: crawl log lines 103-104 ("PR #1 still CONFLICTING (coord
  file)"); memory line 1376 ("PR #1 still open", 17:40) and line 1442
  ("PR #1 still OPEN", 17:53); memory flush 22:37 ("PR 1 tren GitHub
  dang CONFLICTING vi chinh file coord do"). Open for at least 5 hours.
  It appears in the crawl only as a passing note and nowhere in ranks
  1-15, with no owner and no todolist number.
- It also blocks J8: the scrub plan lists "PR #1 handling" as part of
  scrub execution. The scrub cannot run cleanly while PR #1 conflicts.
- Proposed: PR #1 conflict resolution enters the parallel lane with an
  owner (Muse or clone2), ahead of the scrub.

### M3. VMFIX has no rank and the F1/VMFIX file collision is unowned
- See A3 for the ranking gap. The concrete missed item: at 22:36 F1 was
  sudo-copying /tmp/re-init.py into /usr/lib/python3.12/re/__init__.py
  while VMFIX investigates the same file (memory, flush 22:36-22:37:
  "F1 dang sudo cp... (monitor event, chua co bao cao hoan tat)").
  Muse told VMFIX to check the file after F1 finishes, but no queue item
  owns verifying the merged file (F1's copy + VMFIX's hardening) or
  confirming re.py itself is restored. Two agents writing to one system
  Python file with no owner is how J7 happened in the first place.
- Proposed: a P0 item, owned by Muse: verify the merged re/__init__.py,
  restore re.py, confirm import re healthy, then declare SSH stable.

### M4. No queue item lands the F1/F2/F3 diffs (commit + push)
- Live git status 22:44 shows uncommitted work from the fix workers:
  modified scripts/cu.py, scripts/cursor_session.py,
  scripts/cursor_theme.py, tests/test_cursor_session.py,
  tests/test_cursor_theme.py, docs/zen-error-fix-todolist-20261121.md;
  untracked improvements/first-visible-action-rule-20261121.md,
  scripts/first_action.py, tests/test_first_action.py,
  improvements/worker-f1-guardian-fix-log.md,
  improvements/worker-f2-silence-fix-log.md.
  PRIO noted only F1's cursor_session/cursor_theme edits. It missed
  F2's untracked first_action.py + test + rule doc entirely.
- Standing rule D3 (todolist 3.3.3, error file D3): push immediately when
  work is done, do not hold it. Uncommitted fixes on a live machine can
  be lost by the next reboot or the next agent. Rank 9 even proposes
  clone2 re-review "F1/F2/F3 diffs", which assumes diffs exist in a
  reviewable state. They do not: they are uncommitted local edits.
- Proposed: a queue item, right after the F1+F2 fix: commit + push all
  three workers' diffs and logs, then clone2 re-reviews the pushed
  commits.

### M5. PRIO's J11 cites the option-C choice at the wrong time
- PRIO J11 says "owner chose C 18:16". The record says the C choice was
  at flush 18:24: memory lines 1605 ("dang chon C cho 2.2.3"), 1608
  ("Dang chon C qua widget: thu Hyprland long nhau..."), and 1713 (event:
  "On 2026-11-21 dang chose option C"). 18:16 was the Worker W adoption
  note (memory line 1611), not the C choice. Small, but PRIO's todolist
  rewrite of 2.2.3 will carry this timestamp, and the crawl's timestamps
  are supposed to be the evidence. Correct to 18:24.

## What PRIO got right (conceded, not attacked)
- ZT-A DONE 22:37 (a5a5553 + 138919b) is correctly recorded; ZT-B waits
  for F3. Correct.
- Track 2 / speed loop PARKED behind the council gate. Correct, owner
  order stands.
- J7-J16 is a real crawl: J7 (re breakage), J9 (hidden-body experiment),
  J10 (H2 ticked but open), J13 (Y1b probes 10b/10f cannot catch the bug
  they were written for), J15 (17:59 freeze cause unknown) are all
  genuine finds. The crawl itself is good. The ranking is what fails.

## Proposed alternative order
Precondition P0 (before any laptop fix is declared done): VMFIX confirms
SSH stable + re healthy; F1 answers whether the guardian imports re; the
merged re/__init__.py is verified (M3).

Lane 1, serial, owner's machine:
1. F1 + F2 MERGED (owner's literal FIRST, 22:16:54; one end-to-end proof:
   guardian starts, session lives, overlay shows, first visible action
   under 30s). Commit + push the diffs immediately after (M4).
2. F3 restore + Marionette slot + 15-tab cleanup, starting with the
   2-minute Marionette retry check (A7).
3. ZT-B blind ordinary-user tests.
4. Y6 A1-A10 + fresh re-review, then pill measurement retry (open goal
   item 2.2.3; not Zen-gated, moved up from 5).
5. Y13 live, then Y14 live, order by readiness at run time, not roadmap
   position (A5 sub-attack).
6. A1 pilot resume, only after M1 (clone1 verification report) lands and
   its 3 blockers are addressed.
7. Hidden-body decisive experiment + Y4d/Y7 follow-ups.
8. H2 think-time measurement, agent-driven.
9. Y1b snippets (12-item BLOCK + probe rewrites).
10. Final test, independent Codeforces contest. LAST, per the owner
    twice (16:30 order, memory lines 1407 and 1955). Nothing after it.

Lane 2, parallel, starts immediately, Zen-independent:
- Clone2 heavy batches (batch 6 on batch 5 landing; batch 5 c77e8a1
  already in flight). Deleted from the serial queue.
- Y6 A1-A10 work can also live here (code/config, nested only) if lane 1
  is busy; it must not wait behind Y13/Y14.
- Clone1 verification report + Firefox rerun results (M1, todolist 4.23).
- PR #1 conflict resolution (M2), ahead of the scrub.
- F1/F2/F3 diff commit + push (M4).

Scrub (J8, 4.20): NOT rank 13 as written. Either Muse schedules an
explicit fleet pause with a date and it runs then, or it is deferred to
after the final test. No mechanism, no rank.
E1 fresh comparison (4.22): PARKED (deferred, needs a new experiment
design). It must not sit after the LAST item.
J11 corrections (rewrite todolist 2.2.3 and 3.4.1): PRIO's own synthesis
job, with the C-choice time corrected to 18:24 (M5).
J15 (17:59 freeze cause): stays parked low. Conceded.
J16 (clone2 watchdog duty, zero logs since 19:09): Muse closes or
reassigns the duty when issuing clone2's next batch. Conceded as a
process note, but it must actually be closed, not carried silently.

## Addendum 22:44 - facts that landed after the draft (MEMORY.md 22:40 entry)
The parent's MEMORY.md gained a 22:40 entry while this verdict was being
written. Three of my attacks are affected. I correct them here rather
than let PRIO synthesize from stale claims.

- A3 / M3, CORRECTED: VMFIX is DONE. SSH restored durably (F1 fixed
  re/__init__.py from CPython 3.12.3, dpkg -V clean, observe 22:38 ok).
  The guardian failure is NOT due to re: it is the cursor-guard plugin
  not loaded, and F1 is fixing that. So the A3 premise (F1's root cause
  may be the re breakage) is now REFUTED by VMFIX's finding. The lesson
  stands in weakened form: PRIO ranked F1 without ranking its
  precondition, and the precondition was only resolved after the draft.
  What remains open is the root cause of the deletion itself, still
  UNKNOWN: the file that vanished at 22:25:39 could vanish again, so P0
  should keep a watch on /usr/lib/python3.12/re, not just a one-time
  verification. M3's collision is resolved (F1 wrote the file, VMFIX
  verified it), and M3 is CLOSED except for the unknown deleter.
- M4, STRENGTHENED: the owner set a new target at 22:40, reach 240
  commits by end of today (now 189 commits + 1 PR = 190, about 51 more
  before 24:00), and told the whole team (F1/F2/F3/Y13r2/Y14b/PRIO) to
  commit small and often. M4 (commit + push the F1/F2/F3 diffs) is now
  backed by a direct owner order with a deadline, not just standing rule
  D3. The uncommitted diffs listed in M4 are exactly the commits the
  owner is counting.
- M1, PARTLY OVERTAKEN, NOT CLOSED: clone1 batch 6 was issued at 22:40
  (blind ZT scenarios, evidence audit of all history, re-verify batch-3
  + D1). That overlaps M1's subject area but does not close it: batch 6
  re-verifies batch-3, while the missing file is the batch-4
  verification report (docs/clone1-batch23-verification-20261121.md,
  still absent) plus the Firefox rerun results for Y10 t05/t09/t10.
  4.23 still has no queue position.
- The 240-commit target also strengthens A4: the owner's burn order is
  now quantified (about 51 commits before 24:00), and a serial queue
  that parks clone2 at rank 9 cannot produce that volume. Parallel lanes
  are the only way to hit the number.

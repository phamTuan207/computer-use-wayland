# OPT-ORDER Voice 1: OWNER-ATTITUDE ranking
# Council OPT-ORDER, voice 1 of 3. Time: 22:52 +07, Sat 2026-11-21.
# Lens: rank the fix classes by the user's OWN words and repeated
# emphases, with a quote for each rank. Sources: PRIO crawl log
# (improvements/worker-prio-crawl-log.md), PRIO council 2
# (improvements/worker-prio-council-2.md), PRIO redteam
# (improvements/worker-prio-redteam.md), todolist priority section
# (docs/zen-error-fix-todolist-20261121.md lines 1-40), ~/memory/2026-11-21.md
# owner quotes as cited by PRIO council 2 and redteam.
# No em/en dashes in this file. Every claim carries a citation.

## The yardstick: the user's words, in the user's order of emphasis

The owner spoke 8 times tonight that set a ranking. Voice 1 ranks by
those words, not by engineering convenience. Where a word and a
dependency conflict, this paper says which wins and why, and the verdict
paper decides.

## Rank A1. The silence weakness: fix FIRST and fix BEST
- Owner quote, 22:16:54: "cai yeu diem im lang nay phai fix DAU TIEN va
  fix TOI UU TOT NHAT" (PRIO council 2, source list; PRIO crawl log,
  draft lens line). Context in council 2: the weakness is "Muse nghi lau
  im lang, man hinh dung yen, khong thay computer-use bat", and the owner
  "da nhan manh nhieu lan, gio nhan manh lai" (emphasized many times,
  now emphasizes again).
- Owner spec, 22:21: "Ko can noi truoc cung duoc nhung phai nhanh va
  thao tac lien tuc va overlay phai hien de bao cao cho nguoi dung biet"
  (council 2). Target: under 30s from order to first visible action.
- Owner evidence, 22:18:03: "click thanh cong nhung cac overlay ko he
  bat", then 22:18:10: "Lai loi roi" (council 2; redteam A1/A2).
- What this rank covers: the F1+F2 cluster (todolist 4.11 + 4.12).
  F2 is the silence fix (under 30s, continuous ops, overlay always on).
  F1 is the session/guardian fix that makes the overlay exist at all
  ("computer-use cung ko thay bat", 22:16). The owner named the SYMPTOM
  first; the symptom has two causes, and both sit in this rank.
- Voice 1 position on the F2-vs-F3 dispute: Council 2 DEMANDS F2 rank 1
  and F3 rank 2, reading "DAU TIEN" literally (council 2, rank 1-2
  challenge). Redteam A1 agrees (redteam, attack A1). Voice 1 PARTLY
  AGREES and PARTLY DISAGREES. AGREE: "DAU TIEN" is the owner's
  highest-priority label and it belongs to the silence cluster, not to
  Zen. The queue must SAY that, in the rank label, and the todolist now
  does: "Cum nay la fix DAU TIEN cua ong; chi co unblocker F3 dung tren
  no" (todolist priority section, serial rank 2). DISAGREE with the
  literal swap: a swap of rank numbers changes zero wall time, because
  F2 and F3 are already RUNNING in parallel by separate workers, and a
  swap would misstate the dependency, because F2's end-to-end proof
  (session starts AND overlay shows AND first action under 30s) cannot
  run on a dead Zen with a dead Marionette slot. "DAU TIEN" is a
  priority label, not a wall-clock sequence. F3 runs first in wall time
  as the unblocker; the silence cluster is first in importance. Both
  facts can be true at once, and the todolist's decided queue already
  holds both. Council 2's swap would trade a true statement for a
  false one.

## Rank A2. Zen unusable: the owner cannot use the user's own browser
- Owner quote, 22:25: "Zen bi loi, khong the dung binh thuong; khong the
  click hay mo bat ky web nao; doi workspace cung nhieu loi rat ki"
  (council 2; todolist serial rank 1 rationale).
- What this rank covers: F3 (todolist 4.7/4.8/4.10, J1/J2/J3): restore
  Zen, fix the Marionette slot, finish the 15-tab cleanup.
- Why A2 and not A1: the owner said Zen is unusable at 22:25, but the user
  also said at 22:27 the user was going to sleep (redteam A1 cites memory,
  section "dang chi dao 22:29-22:32 (sau khi noi di ngu 22:27)"). The user is
  not using the browser right now. The urgency that justifies F3 first
  in wall time is real (every live run gates on it), but the personal
  pain is paused overnight, while the "DAU TIEN" order has no expiry.
  Voice 1 AGREES with redteam A1 on this point: the sleep blunts the
  F3-first urgency, it does not blunt the F2-first priority.
- Counterweight, and why F3 still runs first in wall time: at 22:29-22:30
  the owner asked "viec dau tien gio ong dinh lam luon la gi", Muse
  answered F3 restore Zen, and the owner did not object (todolist
  serial rank 1 rationale; council 2 weighs this and calls it tacit
  acceptance of F3 as the first WALL-CLOCK action, not a retraction of
  the 22:16 priority order). Voice 1 AGREES with council 2's reading:
  tacit acceptance of wall-clock order, not a retraction of priority.
- Internal order inside F3 (voice 1 defers to dependency voice, but
  records the attitude point): redteam A7 demands the queue start with
  the cheap check, "retry Marionette session now", before treating F3
  as a full repair, because the 22:17 Welcome click may already have
  self-healed the slot (redteam A7). Voice 1 AGREES: the owner's 22:25
  complaint deserves a 2-minute verification before a full repair job
  is assumed. The todolist already adopted this (serial rank 1: "verify
  xem click 22:17 da tu chua slot chua (redteam A7) -> khoi phuc Zen ->
  sua slot -> don tab cuoi").

## Rank A3. "Fix the big errors at full power, the whole team"
- Owner quote, 22:18:22: "Thoi ca team het cong suat fix cac loi to to
  bo nay di" (council 2; PRIO crawl log draft lens).
- What this rank covers: the shape of the whole queue. Big errors
  (Zen dead, session dead, silence, overlay gone) come before small
  errors, and the whole team works them at once. This quote is why the
  todolist splits work into a serial live queue PLUS parallel lanes
  P-A..P-H, instead of one worker doing one thing at a time.
- Voice 1 position: this quote supports the todolist's parallel-lane
  design and OPPOSES any ranking that serializes independent parallel
  capacity behind blocked serial work. That opposition matters for the
  clone2 dispute below (rank A6).

## Rank A4. Root cause first: read the source, crawl, then fix
- Owner quote, 22:22: "loi nay cho team di doc source code, crawl tim
  goc re, nguon goc, ly do loi, roi moi fix" (council 2; PRIO crawl log).
- What this rank covers: the METHOD order inside every fix. F3 must
  find the Marionette root cause ("doc source Marionette + crawl", todolist
  4.10). F1 must find the guardian root cause ("tim dung cho nem + crawl",
  todolist 4.11). Y6 A9 demands re-review before any measurement run.
- Voice 1 position: this quote is a method rule, not a queue rank, but
  it decides one attitude question: a fix that skips root-cause work
  and lands a symptom patch violates an explicit owner order even if it
  is fast. Speed (rank A1) does not override root cause (rank A4); the
  owner ordered BOTH, and the Lauren Tan evidence contract (rank A5)
  is how both are held at once.

## Rank A5. Composite + blind tests, and the Lauren Tan process
- Owner quote, 22:23: tests must be composite (DOM + CLI + chuot + ban
  phim in one exercise); the test-taker must NOT know the exercise in
  advance; separate independent setter for objectivity (council 2).
  Owner quote, 22:23: Lauren Tan process stands (council 2; PRIO crawl
  log draft lens). Owner order, 22:48: follow Lauren Tan strictly, NO
  skipped steps (task brief; PRIO crawl log entry 22:48).
- What this rank covers: the test-design rules for every live run and
  the process rules for every fix (evidence contract, council + redteam,
  commit small and many, generator never runs its own tests, kill rules,
  continuous logging).
- Voice 1 position: this is the owner's standing process order, and it
  outranks schedule pressure. A live run that is not composite and blind
  is not a proof the owner accepts, however fast it ran. ZT-B (todolist
  4.9) exists because of this quote: owner 22:26, "cho doi chuyen test
  va dung thu Zen de gia lap nguoi dung pho thong vao cac thao tac, xem
  co loi gi khong, neu co thi dua vao fix" (council 2, rank 4 AGREE).
  Voice 1 AGREES with council 2: ZT-B directly after the F-team, gated
  on F3 restore, is the right placement for this quote.

## Rank A6. Squeeze the workers dry, burn clone2 harder
- Owner quote, 22:29-22:32: "Dung co om het viec, toi can ong vat kiet
  cac nhan vien chu ko nho ong lam het" and "dot manh token cua clone2
  hon di, no it viec va viec cua no nhe qua roi" (council 2, rank 9
  challenge; redteam A4).
- Owner target, 22:40: 240 commits before 24:00, now 190 (189 commits +
  1 PR), about 51 more (todolist priority section; redteam addendum).
- What this rank covers: clone-worker throughput (todolist 4.16/4.23,
  lanes P-A/P-B) and the commit-small-and-many rule (lane P-H).
- Voice 1 position: Council 2 DEMANDS clone2 heavy batch move to serial
  rank 5 (council 2, rank 9 challenge). Redteam A4 DEMANDS clone2 leave
  the serial queue entirely and become parallel lane 1, running from now
  (redteam A4). Council 3 DEMANDS a split: light batch now, heavy batch
  only after batch 5 is verified AND F1/F2/F3 diffs are frozen (council 3,
  rank 9 challenge). The todolist DECIDED: light batch in lane P-A now,
  heavy batch at serial rank 9 (todolist, phan quyet 2). Voice 1 AGREES
  with the todolist and DISAGREES with council 2's serial rank 5, for
  this attitude reason: the owner's quote is about THROUGHPUT ("vat
  kiet", "dot manh"), not about queue position. Serializing parallel,
  Zen-independent capacity behind blocked serial work (Y13/Y14/A1, all
  gated on F3's Marionette slot) is the opposite of squeezing dry, and
  redteam A4 is right on that point. But council 3 is also right that
  the HEAVY batch (F1/F2/F3 diff re-review) cannot run before the diffs
  exist in a frozen state (redteam M4: the diffs are uncommitted local
  edits). The todolist's split is the only reading that honors both
  owner words at once: burn now on ready offline work (lane P-A), burn
  heavy only when the diffs are frozen (serial rank 9). Council 2's
  rank 5 would issue the heavy batch before its input exists.
- Tied demand (voice 1 AGREES with council 2): J16, clone2's 10-minute
  watchdog duty from 19:09 produced zero logs, must be closed or
  reassigned when the next batch is issued (council 2, rank 9 demand;
  PRIO crawl log J16). An unclosed duty plus a new heavy batch repeats
  the same silent-duty failure.

## Rank A7. The pill: an open goal item, chosen option C
- Owner decision, 18:24 (CORRECTED time; PRIO J11 said 18:16, redteam M5
  proves 18:24 from memory lines 1605/1608/1713; todolist phan quyet 6
  records the correction): owner chose option C, nested Hyprland, for
  2.2.3 (council 2, rank 5 note; todolist 2.2.3).
- What this rank covers: Y6 A1-A10 + pill measurement retry (todolist
  4.13, serial rank 4).
- Voice 1 position: AGREE with council 2 that rank 5 in the PRIO draft
  was acceptable ONLY because A1-A10 are small fix-list items unblocking
  a measurement the owner already ordered, and that Y6 must not take a
  lane from the F-team or ZT-B (council 2, rank 5 condition). The
  todolist moved Y6 to serial rank 4 with its paper fixes in lane P-C,
  which satisfies that condition. The pill is the owner's visible pain,
  but it does not block browser use, so it sits below the F-team and
  ZT-B in attitude rank. No owner quote tonight puts the pill above a
  working browser.

## Rank A8. Live runs in roadmap order (Y13, then Y14, then A1)
- Owner attitude: no owner quote tonight mentions Y13, Y14, or A1 by
  name. Their order comes from the roadmap and from readiness, not from
  an owner emphasis (council 2, ranks 6-8 AGREE).
- Voice 1 position: AGREE with council 2 on all three ranks, with two
  conditions council 2 itself states. A1 (todolist 4.15) resumes ONLY
  after clone1's 3 blockers are addressed and the preconditions are
  proven in writing (council 2, rank 8 condition), because A1 is a speed
  experiment and tonight the owner ordered "fix cac loi to" (22:18),
  not speed. Y13/Y14 run under the 22:23 composite + blind rule.
- One attitude correction from redteam A5: the Y13-before-Y14 order is
  asserted from roadmap position, not evidenced, and Y14b is already in
  fix-pass-4 while Y13r2 is still in council review (redteam A5
  sub-attack). Voice 1 DEFERS the ordering mechanism to the dependency
  voice, but records that no owner quote decides Y13 vs Y14, so
  readiness at run time is a legitimate tiebreaker and the verdict must
  say so.

## Rank A9. H2 think-time: the proof of the rank-1 fix
- Owner attitude: H2 is the measurement that PROVES the silence fix
  worked (council 2, rank 11 challenge). Y11b proved H2 is still open
  (scripted only, think null). Todolist 2.3.1 is ticked DONE with no
  live agent-driven measurement (PRIO crawl log J10).
- Voice 1 position: Council 2 DEMANDS H2 move to rank 9, directly after
  the Y13/Y14 live runs, riding on them (council 2, rank 11 challenge).
  Voice 1 AGREES with the attitude (the proof of the owner's number-one
  fix cannot sit at rank 11) and DISAGREES with the standalone rank 9,
  for the dependency reason the dependency voice will state: Y13/Y14
  ARE agent-driven live runs, so H2 instrumentation rides on them and
  closes with zero extra live slots (council 1 SWAP 3; council 3 rank
  11). The todolist adopted the fold (G-H2, todolist priority section).
  Voice 1 adds the attitude guard: if no live run yields real think
  values, H2 gets its own agent-driven run anyway, because an
  unmeasured rank-1 fix is an unproven rank-1 fix.

## Rank A10. Y1b, scrub, and the tail: safety and standing rules
- Y1b (todolist 4.19): no owner quote tonight touches Y1b. It is
  safety/hardening work, so rank 12 behind the live queue is right
  (council 2, rank 12 AGREE). Voice 1 AGREES.
- Scrub (todolist 4.20): owner standing rule, NO PERSONAL INFO ON
  GITHUB. Email already removed (commit 1c7d252); real name in 71 lines
  / 45 files still outstanding (council 2, rank 13 AGREE). Voice 1
  AGREES with council 2: the low position is a scheduling fact (needs a
  quiet fleet window), not a deprioritisation, and the rank must never
  slip off the list.
- Final test (todolist 4.21): owner quote, 16:30, confirmed twice, runs
  LAST after all other work (council 2, rank 14 AGREE). Voice 1 AGREES.
  Condition from council 2: rank 15 (E1) is parked/deferred, not
  scheduled work, so as the queue stands rank 14 is right; if E1 is ever
  scheduled as real work, it must precede the final test.
- E1 (todolist 4.22): deferred by council + redteam, needs a NEW
  experiment design (council 2, rank 15 AGREE). Voice 1 AGREES, with
  the redteam A6 correction carried forward: E1 must NOT sit after the
  item the owner said runs LAST. The todolist already moved E1 to
  PARKED (todolist, phan quyet 5), which satisfies this.

## Parked items: attitude check
- Track 2 + speed loop: PARKED behind the council gate. Voice 1 AGREES
  (council 2, parked AGREE). Tonight the owner ordered error fixes, not
  speed; the speed loop needs a proven machine to measure against.
- Super I follow-ups: PARKED per owner deferral 17:42. AGREE.
- 2.1.7 I7 video: PARKED until the owner re-sends the original file.
  AGREE. No action is possible without the file.
- Pending user decisions: PARKED until the owner decides. AGREE.
- J15 17:59 freeze cause: PARKED low. AGREE. Self-recovered, no
  recurrence.
- J12 gap (voice 1 AGREES with council 2, GAP 1): clone1 owes the
  batch-4 verification report + Firefox rerun results
  (docs/clone1-batch23-verification-20261121.md does NOT exist;
  Firefox rerun dispatched 19:27, results never landed). The PRIO draft
  left it OUT of the 1-15 queue. Under the Lauren Tan evidence contract
  the owner adopted, a missing verification report is a live violation,
  not a footnote. The todolist now ranks it in lane P-B (todolist 4.23,
  lane P-B), which satisfies this demand.

## Voice 1 summary of agreements and disagreements
- AGREE with todolist decided queue on: F1+F2 cluster named as the
  owner's first fix with F3 as wall-clock unblocker; ZT-B after F-team;
  Y6 serial 4 with paper in lane P-C; Y13/Y14/A1 order with A1
  conditions; H2 folded into live runs; Y1b/scrub/final-test/E1-parked
  tail; all parked items; J12 in lane P-B.
- DISAGREE with council 2 on: the literal F2/F3 rank swap (priority
  label vs wall-clock sequence are different things; the swap changes
  nothing and misstates the dependency); clone2 heavy batch as serial
  rank 5 (throughput is a lane question, not a serial rank, and the
  heavy batch input does not exist yet); H2 as a standalone rank 9
  (fold it, with the fallback guard).
- AGREE with redteam A1 on: the owner's sleep blunts F3-first urgency;
  F2's fix can be built and unit-tested without Zen restored. AGREE
  with redteam A4 on: serializing parallel capacity behind blocked
  serial work contradicts "vat kiet". AGREE with redteam A6 on: nothing
  may sit after the LAST item; E1 belongs in PARKED.
- AGREE with council 3 on: F1 before F2 in dependency order inside the
  cluster (the dependency voice states the mechanism; the attitude
  voice concedes the owner named the symptom, not the dependency).

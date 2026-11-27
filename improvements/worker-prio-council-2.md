# Council 2 verdict - Owner-attitude fidelity review of PRIO draft queue
# Council 2, 22:44 +07 Sat 2026-11-21. Lens: does the draft ranking match the
# user's OWN words and repeated emphases? Sources: PRIO crawl log
# (improvements/worker-prio-crawl-log.md), todolist
# (docs/zen-error-fix-todolist-20261121.md), error file section 12 (J1-J6),
# ~/memory/2026-11-21.md flushes 22:16, 22:19, 22:21, 22:22-22:23, 22:25-22:27,
# 22:31, 22:37. All owner quotes below are copied from that daily memory.
# No em/en dashes in this file.

## Owner orders used as the yardstick (verbatim, with time)

- 22:16:54: silence weakness "phai fix DAU TIEN va fix TOI UU TOT NHAT".
  Context: "diem yeu 'Muse nghi lau im lang, man hinh dung yen, khong thay
  computer-use bat' da ghi ro trong file tong hop loi (phan G/H), dang da
  nhan manh nhieu lan, gio nhan manh lai".
- 22:18:03: "click thanh cong nhung cac overlay ko he bat", then 22:18:10:
  "Lai loi roi".
- 22:18:22: "Thoi ca team het cong suat fix cac loi to to bo nay di".
- 22:21: "Ko can noi truoc cung duoc nhung phai nhanh va thao tac lien tuc
  va overlay phai hien de bao cao cho nguoi dung biet". Target: under 30s
  from order to first visible action.
- 22:22: "loi nay cho team di doc source code, crawl tim goc re, nguon goc,
  ly do loi, roi moi fix".
- 22:23: tests must be composite (DOM + CLI + chuot + ban phim in one
  exercise); the test-taker must NOT know the exercise in advance; separate
  independent setter for objectivity. Lauren Tan process stands.
- 22:25: "Zen bi loi, khong the dung binh thuong; khong the click hay mo bat
  ky web nao; doi workspace cung nhieu loi rat ki".
- 22:26: "cho doi chuyen test va dung thu Zen de gia lap nguoi dung pho
  thong vao cac thao tac, xem co loi gi khong, neu co thi dua vao fix".
  Also 22:26: "lam dan giai quyet het".
- 22:29-22:32: "Dung co om het viec, toi can ong vat kiet cac nhan vien chu
  ko nho ong lam het". "dot manh token cua clone2 hon di, no it viec va
  viec cua no nhe qua roi".
- 16:30 (confirmed twice): final test (independent Codeforces contest, 5
  problems, Muse uploads via Polygon itself) runs LAST, after all other work.

## Verdicts per draft rank

### Rank 1. F3 Zen restore + Marionette slot + 15-tab cleanup - CHALLENGE (swap with rank 2)
- Draft rationale: owner cannot use the user's browser at all (22:25); every live
  run gates on this. That is TRUE and F3 is the first thing in wall-clock
  time. But rank 1 in a priority queue means "matters most", and the owner
  said the silence weakness, not Zen, is what must be fixed FIRST:
  22:16:54 "cai nay phai fix DAU TIEN va fix TOI UU TOT NHAT".
- Counter-evidence weighed and rejected as decisive: at 22:29 the owner
  asked "viec dau tien dinh lam luon la gi", Muse answered F3 restore Zen,
  and the owner did not object. That is tacit acceptance of F3 as the first
  WALL-CLOCK action, not a retraction of the 22:16 priority order. The 22:16
  order was a repeated emphasis ("da nhan manh nhieu lan, gio nhan manh
  lai"), the 22:29 exchange was a status question.
- DEMAND: swap ranks 1 and 2. F2 becomes rank 1 (owner priority), F3
  becomes rank 2 with the explicit label "unblocker, runs first in wall
  time". Both already run in parallel by separate workers, so the swap
  costs zero wall time; it corrects what the queue says matters most.

### Rank 2. F2 silence fix - CHALLENGE (move to rank 1)
- Owner quote: 22:16:54 "phai fix DAU TIEN va fix TOI UU TOT NHAT", plus
  22:21 "phai nhanh va thao tac lien tuc va overlay phai hien".
- The draft itself cites the 22:16 order as its rationale, then still
  places F2 second. A rationale that proves rank 1 cannot justify rank 2.
- DEMAND: rank 1. F2 is the owner's single most-emphasized fix of the
  night. Its acceptance bar stays the owner's: under 30s order to first
  visible action, continuous ops, overlay always on.

### Rank 3. F1 guardian/session fix - AGREE (with cluster note)
- Owner quote: 22:16 "khong thay computer-use bat"; 22:18:03 "click thanh
  cong nhung cac overlay ko he bat" and 22:18:10 "Lai loi roi".
- The draft's own note is right: F1 and F2 intertwine, because F2's 22:21
  rule "overlay PHAI HIEN" depends on F1's session actually starting.
- DEMAND (small): treat ranks 1-3 as one fix cluster (F2 lead, F1 support,
  F3 unblocker), not three sequential steps. Do NOT swap F1 above F2: the
  owner named the silence weakness first, and F1's guardian failure is one
  cause of the silence, not the whole of it (F2 also covers think/decision
  slowness and the under-30s rule).

### Rank 4. ZT-B blind ordinary-user Zen tests - AGREE
- Owner quote: 22:26 "cho doi chuyen test va dung thu Zen de gia lap nguoi
  dung pho thong vao cac thao tac, xem co loi gi khong, neu co thi dua vao
  fix". Plus the 22:23 standing rule: composite tests, blind test-taker,
  independent setter.
- Placement is right: directly after the F-team, gated on F3 restore, and
  ZT-A is already DONE (22:37, commits a5a5553 + 138919b). No change.

### Rank 5. Y6 A1-A10 fix list + pill measurement retry - AGREE (with lane condition)
- Owner support: owner chose option C at 18:16 for 2.2.3; Y6r AMEND was
  unanimous (22:31); retry may NOT proceed as-is. The 22:22 method order
  ("doc source crawl tim goc re roi fix") also applies here: A9 demands
  re-review of the fix diff before any measurement run.
- Condition: rank 5 is acceptable ONLY because A1-A10 are small fix-list
  items unblocking a measurement the owner already ordered. Y6 must not
  take a lane from the F-team or ZT-B. If lanes conflict, Y6 waits.
- Note: the J11 correction (rewrite todolist 2.2.3, which still says
  BLOCKED 15:35 "owner only needs to say a letter") belongs to this rank
  and must land with it, since 2.2.3 is the item this rank unblocks.

### Rank 6. Y13 live run, codex-y5 - AGREE
- Roadmap live-queue order is Y13 first; gated on Y13r2 verdict + H3 gate
  direction + Marionette slot. The 22:23 composite + blind rule applies to
  this run. No owner quote contradicts this placement. No change.

### Rank 7. Y14 live run, batch-3 - AGREE
- Roadmap live-queue order is Y14 after Y13; gated on Y14b re-stage
  clearing. Same 22:23 test rule applies. No change.

### Rank 8. A1 pilot resume - AGREE (with blocker condition)
- The draft's rationale (only proposal with a measured win, Pick 1 wall
  -53%) is real, but the owner's tonight orders do not mention A1, and the
  speed loop is PAUSED by council gate. Rank 8, behind all error fixes and
  both live runs, correctly reflects that: A1 is a speed experiment, and
  tonight the owner ordered "fix cac loi to" (22:18), not speed.
- Condition: resume ONLY after clone1's 3 blockers are addressed and the
  preconditions are proven (written order naming 12 run-ids, broker SOLO +
  idle, relay verified, Layer-2 probes, checker real-run cross-check).
  No shortcut on this rank.

### Rank 9. Clone2 heavy batch - CHALLENGE (move to rank 5)
- Owner quote, direct and fresh: 22:31 "dot manh token cua clone2 hon di,
  no it viec va viec cua no nhe qua roi", plus "Dung co om het viec, toi
  can ong vat kiet cac nhan vien chu ko nho ong lam het".
- Rank 9 buries a direct owner order behind A1 (frozen, blocked on 3
  blockers), Y13/Y14 (gated on reviews) and Y6 (a measurement retry). The
  owner said burn clone2 harder NOW, not after eight other items.
- Clone2 is parallel capacity: its batch does not compete with F-team or
  live-run lanes, so ranking it low does not save anything, it only delays
  the burn the owner ordered.
- DEMAND: move to rank 5 (directly after ZT-B, before Y6). Its content
  (J14 batch-3 follow-ups + independent re-review of F1/F2/F3 diffs)
  directly serves ranks 1-3, so it is parallel support for the top fixes,
  not separate work. Batch 5 (c77e8a1) is already issued; this rank is the
  NEXT heavy batch (batch 6) with the J14 + F-diff re-review content.
- DEMAND (tied): J16 (clone2's 10-min watchdog duty from 19:09 produced
  zero logs) must be closed or reassigned when this batch is issued, per
  the crawl log. An unclosed duty plus a new heavy batch repeats the same
  silent-duty failure.

### Rank 10. Hidden-body decisive experiment + Y4d/Y7 follow-ups - AGREE
- Tracked defect item still OPEN; 0 encounters so far means the recovery
  ladder is unproven live. The owner did not mention hidden-body tonight,
  and the experiment cannot be forced without an encounter, so rank 10 is
  honest. No change.

### Rank 11. H2 think-time measurement, agent-driven - CHALLENGE (move up to rank 9)
- Owner quotes: 22:16:54 "fix DAU TIEN va fix TOI UU TOT NHAT" for the
  silence weakness, and 22:21 "phai nhanh va thao tac lien tuc". H2 is the
  measurement that PROVES the silence fix worked (think time per step,
  agent-driven). Y11b proved H2 is still open (scripted only, think null).
- Rank 11 sits behind A1 (a frozen speed experiment) and next to deferred
  items. That underweights a measurement of the owner's number-one fix.
- DEMAND: move H2 to rank 9, directly after the Y13/Y14 live runs. Note
  the synergy: Y13/Y14 ARE agent-driven live runs, so H2 can ride on them
  (measure real think values during those runs) instead of needing its own
  separate run. If Y13/Y14 slip, H2 does not slip with them past rank 9;
  it gets its own agent-driven run.

### Rank 12. Y1b snippets - AGREE
- 12-item BLOCK must be enforced; Phase B probes 10b/10f + 1e/4a must be
  rewritten before Phase B is judged. No owner quote tonight touches Y1b,
  and it is safety/hardening work, so rank 12 behind the live queue is
  right. No change.

### Rank 13. Email + real-name history scrub - AGREE (with standing-rule note)
- Owner standing rule: NO PERSONAL INFO ON GITHUB. Email at
  live-test-log.md:3288 is already removed (commit 1c7d252); real name in
  71 lines / 45 files is still outstanding, plan exists.
- Rank 13 is justified by the execution constraint (needs a quiet fleet
  window: filter-repo + force-push + all agents re-clone + PR #1 handling),
  NOT by low importance. The standing rule means this rank must never slip
  off the list; its low position is a scheduling fact, not a deprioritisation.
  No change.

### Rank 14. Final test, independent Codeforces contest - AGREE (with condition)
- Owner quote: 16:30, confirmed twice, final test runs LAST, after all
  other work. Rank 14, second to last, is correct.
- Condition: rank 15 (E1) is parked/deferred, not scheduled work. If E1 is
  ever scheduled as real work, it must precede the final test, because the
  owner said the final test is LAST after everything else. As the queue
  stands, with E1 parked, rank 14 is right.

### Rank 15. E1 fresh comparison - AGREE
- Deferred by council + redteam; needs a NEW experiment design (new
  labels, new pre-reg, old FAILs carried with judge 7275171, budget NEW,
  ceiling conceded, replication pair mandatory). Last is right. Note: the
  J11 correction (rewrite todolist 3.4.1, which still says "THI NGHIEM DANG
  DO, CHUA CO KET LUAN" when E1 was CLOSED by Y8b 20:26) belongs to this
  rank.
- PARKED items (Track 2 + speed loop, Super I, 2.1.7 I7 video, pending user
  decisions, J15 17:59 freeze cause): AGREE, all correctly parked. J15
  self-recovered with no recurrence; low is right.

## Gaps in the draft queue (items the draft found but did not rank)

- GAP 1 (must fix): J12, clone1 owes batch-4 verification report + Firefox
  rerun results (docs/clone1-batch23-verification-20261121.md does NOT
  exist; Firefox rerun of Y10 t05/t09/t10 dispatched 19:27, results never
  landed). The draft adds it as todolist 4.23 but leaves it OUT of the
  1-15 queue. Under the Lauren Tan evidence contract the owner adopted
  (22:23 confirmation), a missing verification report is a live violation,
  not a footnote. DEMAND: fold J12 into the clone-worker block at new
  rank 5 (with the clone2 batch): clone1 delivers its owed verification
  report + Firefox rerun results in the same wave.
- GAP 2 (noted, no action): J7 (VM Python re broke, SSH died 22:25-22:31,
  self-restored, cause unknown) is correctly NOT in the queue: parent
  already spawned VMFIX, PRIO must not duplicate it. The queue only tracks
  VMFIX's confirmation before assuming SSH is stable. AGREE with the
  draft's handling.

## Demanded final queue (after swaps)

1. F2 silence fix (owner: fix DAU TIEN, 22:16; under 30s, continuous, overlay on, 22:21)
2. F3 Zen restore + Marionette slot + 15-tab cleanup (unblocker, first in wall time; owner: Zen unusable, 22:25)
3. F1 guardian/session fix (owner: "computer-use cung ko thay bat", overlay "ko he bat", 22:18)
4. ZT-B blind ordinary-user Zen tests (owner: 22:26; composite + blind rule, 22:23)
5. Clone-worker heavy wave: clone2 batch 6 (J14 + F1/F2/F3 diff re-review) + clone1 owed J12 verification report (owner: "vat kiet cac nhan vien", "dot manh token clone2", 22:31; close/reassign J16 duty with this issue)
6. Y6 A1-A10 + pill measurement retry (owner chose C 18:16; Y6r AMEND unanimous; rewrite 2.2.3 with this rank)
7. Y13 live run, codex-y5
8. Y14 live run, batch-3
9. H2 think-time measurement, agent-driven (rides on Y13/Y14 live runs; proof of the rank-1 fix)
10. A1 pilot resume (only after 3 blockers + preconditions proven)
11. Hidden-body decisive experiment + Y4d/Y7 follow-ups
12. Y1b snippets (12-item BLOCK enforced; probes rewritten before Phase B judged)
13. Email + real-name history scrub (standing rule NO PII; quiet fleet window)
14. Final test, independent Codeforces contest (owner: LAST, 16:30, confirmed twice)
15. E1 fresh comparison (deferred; rewrite 3.4.1 with this rank)
PARKED: Track 2 + speed loop, Super I, 2.1.7 I7 video, pending user decisions, J15 freeze cause.

## Summary for PRIO

- 10 AGREE, 4 CHALLENGE, 1 GAP demanding a fix.
- CHALLENGE 1: ranks 1-2 swap. F2 to rank 1, F3 to rank 2 (unblocker label).
  Owner: "fix DAU TIEN va fix TOI UU TOT NHAT" (22:16:54).
- CHALLENGE 2: clone2 heavy batch rank 9 to rank 5, bundled with clone1 J12.
  Owner: "dot manh token cua clone2 hon di" (22:31).
- CHALLENGE 3: H2 rank 11 to rank 9, riding on Y13/Y14 live runs.
  Owner: silence fix is rank 1, its measurement cannot sit at 11.
- CHALLENGE 4 (small): ranks 1-3 are one fix cluster (F2 lead, F1 support,
  F3 unblocker), not sequential steps. No order change beyond challenge 1.
- No draft placement contradicts the final-test-LAST order (16:30) or the
  composite + blind test rule (22:23) or the root-cause method order
  (22:22). The draft's two real misses are the F2 demotion and the clone2
  burial, plus the unranked J12.

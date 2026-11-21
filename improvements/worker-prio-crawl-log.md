# Worker PRIO log - re-crawl chat + rank todolist (council + redteam)
# Start: 22:34 +07, Sat 2026-11-21. Owner order 22:32: todolist exists, convene
# council to debate, redteam to argue, rank what matters most; a team re-crawls
# the chat history for missed errors/tasks; rank by the owner's attitude and notes.
# Method: read todolist (169 lines), error file (676 lines, parts A-I + J1-J6),
# ~/memory/2026-11-21.md (2462 lines, greps + tail), chat 750c8dae newest 40 turns
# (2 pages), repo improvements/ listing + git status, live SSH test 22:36.

## Crawl findings: NEW items not on todolist or in error file

### J7. VM Python `re` broke, SSH VM->laptop died ~22:25-22:31, self-restored 22:31:12
- Evidence: Y6r found at 22:35 that /usr/lib/python3.12/re.py was missing and
  re/ held 3.13-style files with no __init__.py, breaking tailscale-proxy.py and
  all python3 importing re; dir mtime 22:25:39 +07. Parent MEMORY.md 22:31-22:33:
  __init__.py appeared 22:31:12, Muse verified 22:33 re_ok + SSH_OK.
- PRIO live verification 22:36: `python3 -c "import re"` OK; `ssh-laptop.sh
  'echo SSH_OK'` returned SSH_OK omarchy 22:36:26. stat: re/__init__.py mtime
  2026-11-21 15:31:12 UTC (= 22:31:12 +07), re/ dir mtime 15:29:58 UTC.
- Status: WORKING AGAIN. Who/what restored it is UNKNOWN; parent spawned VMFIX
  to find out and harden it. PRIO does not duplicate VMFIX. Queue: track VMFIX,
  do not start laptop-side work on the assumption SSH is stable until VMFIX
  confirms the cause. (Y6r's finding was TRUE at the time, not a false alarm.)

### J8. Email + real-name history scrub still outstanding
- Evidence: summary + MEMORY.md. User email at live-test-log.md:3288 removed
  (commit 1c7d252, grep 0 on main). Real name in 71 lines / 45 files on main.
  Plan docs/email-history-scrub-plan.md exists. Execution PENDING a quiet fleet
  window (filter-repo + force-push + all agents re-clone + PR #1 handling).
- Not on todolist, not in error file parts A-I. Add as todolist 4.20.

### J9. Hidden-body decisive experiment still owed + live-runner follow-ups
- Evidence: Y4b design (htmlClass + rAF tick on SAME hidden tab SAME minute)
  never run; Y4d + Y9b reruns had 0 encounters. Tracked item
  improvements/transparent-zen-defect-tracked-item.md OPEN. Y4d follow-up:
  shared bootstrap tab does not survive its session (one session per suite vs
  per-test tabs). Y7 follow-ups: test-07 restore marker = biggest hole
  (partially mitigated live by Y9b steps 24/28), test-09 off-spec bypass note,
  simulate --all first-crash abort.
- Not on todolist. Add as todolist 4.17.

### J10. H2 think-time measurement still OPEN, but todolist 2.3.1 is ticked
- Evidence: Y11b proof was scripted (think_s null by design); only an
  agent-driven run with real think values closes H2. Todolist 2.3.1 says DONE
  with no live agent-driven measurement. Discrepancy: ticked item, open goal.
- Add as todolist 4.18 (re-open 2.3.1 with the agent-driven requirement).

### J11. Todolist stale entries (process error: todolist not updated after completions)
- 2.2.3 I11 still says BLOCKED 15:35, "owner only needs to say a letter".
  Reality: owner chose C 18:16; Y6c NO VERDICT (F0/F1/U5b, 5a2b69d); Y6d DONE
  72eb8ad (launcher v3, C2 ALL PASS); Y6e DONE 915121d (rebuild, load test
  PASS 21:57); Y6r AMEND unanimous (6239298 + b53a593), retry blocked until
  A1-A10 land + fresh re-review. Rewrite 2.2.3 entirely.
- 3.4.1 E1 still says "THI NGHIEM DANG DO, CHUA CO KET LUAN". Reality: E1
  CLOSED by Y8b 20:26 (arm A BLOCKED judge 7275171, arm B PASS single-arm
  522s 0/0/0, NO comparative verdict); fresh comparison DEFERRED to a future
  NEW experiment (new labels, new pre-reg, old FAILs carried, budget NEW,
  ceiling conceded, replication pair mandatory). Rewrite 3.4.1.
- Add corrections in the todolist edit; record here as J11.

### J12. Clone1 owes batch-4 verification report + Firefox rerun results
- Evidence: summary said "check whether it landed". PRIO checked:
  docs/clone1-batch23-verification-20261121.md does NOT exist in the repo.
  Clone1 dispatched a Firefox rerun of Y10 t05/t09/t10 at 19:27; results never
  landed. Clone1 batch 5 final report landed (35df907, 21:41).
- Add as todolist 4.23.

### J13. Y1b snippets: Phase A BLOCK stands, Phase B probes must be rewritten
- Evidence: worker-y1b-verify-redteam.md (836 lines) + watch log tail. 12-item
  must-fix checklist; NO executor-hardening merge until all 12 proven fixed.
  Probes 10b/10f structurally unable to catch the budget amplification they
  were written for (outer program aborts at first snippet's 2s wall, second
  run_snippet never executes in EITHER implementation); they would PASS the
  vulnerable implementation. MUST be rewritten before Phase B is judged, along
  with 1e/4a replacements. Y1b live watch status (Codex PID 184702) unconfirmed
  since ~19:00; log exists but no recent live check in it.
- Not on todolist. Add as todolist 4.19.

### J14. Batch-3 checker follow-ups outstanding
- Evidence: Y12 holes H1 (novel names now public; durable fix = per-run random
  suffix), H2 (t05 error assert visibility only), H3 (t09 localStorage never
  verified, 6s delivery would false-fail on 5s poll cap), H4 (t10 position
  never read after Prev/playlist/shuffle/wrap Next). Y15 follow-ups: R1/R2/R3b
  fix sketches (escapes, README-qualified), R5, W1 probe, E5 diagnostic wart.
- Not on todolist. Add as todolist 4.24 (bundle with J9? No: J9 is live-runner
  follow-ups; J14 is checker follow-ups. Keep separate.)

### J15. 17:59 keyboard/mouse freeze root cause still unknown
- Evidence: owner reported freeze 17:59:13, recovered 18:00:08. Y4b proved
  probe_y4c navigations (17:59:27/33) did NOT cause it (onset predates them).
  No cause found. Self-recovered, no recurrence since. Low priority.
- Not on todolist or in error file. Add as todolist 4.25 (low).

### J16. Clone2's 10-min watchdog duty (19:09) produced zero logs
- Evidence: watchdog runs 21:41/22:15/22:31 all note zero watchdog logs from
  clone2 since the duty was assigned 19:09 via coord (commit a34e339). Clone2
  went silent 19:22-22:29, then pushed 2d2a855 (batch 4 done all 6 tasks) and
  batch 5 c77e8a1. The duty itself was never fulfilled nor formally closed.
- Small process gap. Record here; queue: Muse closes or reassigns the duty
  when issuing clone2's next batch. (Owner 22:31: burn clone2 harder.)

## Other crawl notes (checked, NOT new items)
- Clone2 STALL OVER: pushed 2d2a855 22:29:31 (batch 4 task 1 done, 2 AT-SPI
  fixes verified, trial merge PR #1 only conflicts on coord file, no code
  conflict). Batch 5 assigned + pushed c77e8a1. PR #1 still CONFLICTING (coord
  file). Owner 22:31: burn clone2's tokens harder (little work, too light).
- TikTok browser-task STALL (watchdog 22:31): parent dc564674 + child 2d740654
  silent 93.6m/17.1m, ~102 min for a 116s video, stuck on bot-wall. Owned by
  chat 8fb75ccd, NOT this chat's queue. Muse to kill/reassign there.
- ZT-A DONE 22:37 (commits a5a5553 + 138919b): 10 composite blind scenarios
  ZT-01..ZT-10 + ZT-00 health gate, 658 lines, on real Zen; council AMEND +
  redteam BLOCK (6 blockers incl. R-01 blind Ctrl+W could close owner's real
  tab) all fixed in v2. ZT-B not yet spawned (waits for F3 restore).
- F1 has uncommitted edits to scripts/cursor_session.py + cursor_theme.py.
  F3 has no log file yet. Y14b fix-pass-3 redteam AMEND (bd3c6c9 22:22).
- Parked by owner/council, do NOT start: Track 2 + speed loop (council +
  redteam unanimous gate), Super I follow-ups (owner deferred 17:42),
  2.1.7 I7 video (reopens only if owner re-sends the original file),
  pending user decisions (pill final choice, H1-BASE, Step 3, save-dialog B,
  ~/backups ~99 GiB, Omarchy restore steps - need owner), last30days-skill
  idea (not scoped, owner: design for him + Muses, no start ordered).
- Final test (independent Codeforces contest, 5 problems, Muse uploads via
  Polygon itself): planned, runs LAST (owner 16:30 21/11, confirmed twice).
  Not on todolist. Add as todolist 4.21.
- E1 fresh comparison: deferred, needs a new experiment design. Add 4.22.
- A1 pilot: frozen 18:46 (f31abcf); clone1 review found 28 holes, 3 blockers
  (1ddac2d). Resume needs blockers addressed + preconditions (written order
  naming 12 run-ids, broker SOLO + idle, relay verified, Layer-2 probes,
  checker real-run cross-check). Not on todolist. Add as todolist 4.15.
- Y13/Y14 live queue: Y13 live gated on Y13r2 verdict + H3 gate direction +
  Marionette slot; Y14 live gated on Y14b re-stage clearing. Not on todolist
  as queue items. Add as todolist 4.14.
- Y6 A1-A10 (Y6r AMEND): A1 stage y6e conf as active conf; A2 positive gate
  replacing U6; A3 positive marker in nest optics.lua only; A4 correct the
  record; A5 port AMEND4/AMEND5; A6 G4 + G6; A7 no manual reload; A8 load-only
  trial first; A9 re-review fix diff before any measurement run; A10 no
  saved-log marker counts as parse evidence. Not on todolist. Add 4.13.

## DRAFT RANKED QUEUE (for council + redteam debate)
# Lens: owner's own words. "fix dau tien va fix toi uu tot nhat" (silence
# weakness, 22:16); "NHANH + thao tac LIEN TUC + overlay PHAI HIEN" (22:21);
# "ca team het cong suat fix cac loi to to bo" (22:18); Zen unusable (22:25);
# "doc source crawl tim goc re roi fix" (22:22); composite + blind tests
# (22:23); Lauren Tan process (22:23); "dung om het viec, vat kiet nhan vien"
# + "dot manh token clone2" (22:31); "lam dan giai quyet het" (22:26);
# final test LAST (16:30); Track 2 / speed loop PAUSED (council gate).

1. F3 Zen restore (4.7/4.8, J1/J2) + Marionette slot (4.10, J3) + finish the
   15-tab cleanup. Rationale: owner cannot use his browser at all (22:25);
   every live run gates on this. [RUNNING]
2. F2 silence fix (4.12, J5). Rationale: owner said fix this FIRST and
   optimally (22:16); <30s first visible action, continuous ops, overlay
   always on (22:21). [RUNNING]
3. F1 guardian/session fix (4.11, J4). Rationale: "computer use cung ko thay
   bat" (22:16); overlay must show, session never starts. [RUNNING]
   NOTE for council: F1 and F2 intertwine (F2's overlay-always-on needs F1's
   session). Debate whether 2 and 3 should swap or run as one fix.
4. ZT-B blind ordinary-user Zen tests (4.9, J6). Rationale: owner ordered a
   dedicated team to simulate an ordinary user and feed errors into fixing
   (22:26); runs after F3 restore. [ZT-A DONE 22:37, commits a5a5553 +
   138919b: 10 composite blind scenarios ZT-01..ZT-10 + ZT-00 health gate,
   658 lines; ZT-B NOT yet spawned, waits for F3 restore]
5. Y6 A1-A10 fix list + fresh re-review, then pill measurement retry (4.13,
   2.2.3). Rationale: Y6r AMEND unanimous; retry may NOT proceed as-is;
   2.2.3 is the open goal item. [NOT STARTED]
6. Y13 live run, codex-y5 (4.14). Rationale: live queue order per roadmap
   (Y13 first); gated on Y13r2 verdict + H3 gate direction + Marionette slot.
   [Y13r2 RUNNING]
7. Y14 live run, batch-3 (4.14). Rationale: live queue order (Y14 after Y13);
   gated on Y14b re-stage clearing. [Y14b RUNNING]
8. A1 pilot resume (4.15). Rationale: only proposal with our own measured win
   (Pick 1: wall -53%); resume only after clone1's 3 blockers addressed +
   preconditions met. [FROZEN]
9. Clone2 heavy batch (4.16). Rationale: owner 22:31 "dot manh token clone2
   hon, no it viec va viec cua no nhe qua"; clone2 back 22:29 with batch 5
   done. Suggested content: batch-3 follow-ups (J14) + independent re-review
   of F1/F2/F3 diffs. Issued via coord by Muse, not by PRIO.
10. Hidden-body decisive experiment + Y4d/Y7 follow-ups (4.17, J9).
    Rationale: tracked defect item still OPEN; 0 encounters so far means the
    recovery ladder is unproven live.
11. H2 think-time measurement, agent-driven (4.18, J10). Rationale: Y11b
    proves H2 open (scripted only); only an agent-driven run closes it.
12. Y1b snippets (4.19, J13). Rationale: 12-item BLOCK must be enforced; Phase
    B probes 10b/10f + 1e/4a must be rewritten before Phase B is judged.
13. Email + real-name history scrub (4.20, J8). Rationale: owner standing rule
    NO PERSONAL INFO ON GITHUB; plan exists; needs a quiet fleet window.
14. Final test, independent Codeforces contest (4.21). Rationale: owner
    ordered it LAST (16:30, confirmed twice); runs only after everything else.
15. E1 fresh comparison (4.22). Rationale: deferred by council + redteam;
    needs a NEW experiment design (new labels, new pre-reg, old FAILs carried
    with judge 7275171, budget NEW, ceiling conceded, replication pair).
PARKED: Track 2 + speed loop (council gate); Super I follow-ups (owner
deferred); 2.1.7 I7 video (needs owner re-send); pending user decisions
(need owner); 17:59 freeze cause (J15, 4.25, low).
CORRECTIONS: rewrite todolist 2.2.3 (J11) and 3.4.1 (J11) - both stale.
VMFIX: parent already spawned VMFIX on the SSH/Python hardening; PRIO does
not duplicate it; queue tracks VMFIX's confirmation before assuming SSH stable.

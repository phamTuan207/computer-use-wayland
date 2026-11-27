# OPT-ORDER Voice 3: RISK / COST
# Council OPT-ORDER, voice 3 of 3. Time: 23:00 +07, Sat 2026-11-21.
# Lens: what is cheapest to prove first, what must never run in parallel,
# what to park and why. Sources: PRIO council 3
# (improvements/worker-prio-council-3.md), PRIO redteam
# (improvements/worker-prio-redteam.md), PRIO crawl log
# (improvements/worker-prio-crawl-log.md), todolist priority section + items
# 4.7-4.28 (docs/zen-error-fix-todolist-20261121.md), sibling OPT-M1 mechanism
# (improvements/opt-council-m1-mechanism.md). Sibling OPT-M2 verdict does NOT
# exist yet at write time. No em/en dashes in this file.
# Every claim carries a file:line or quote citation.

## The cost lens in one line
Cheapest proof first, most expensive failure last, never pay for the same
proof twice, and never let a cheap check wait behind an expensive run it
could have invalidated.

## R1. Cheapest proofs first (do these before any expensive live run)
- R1a. Marionette retry check (redteam A7): 2 minutes. The 22:17 Welcome
  click may already have self-healed the slot. If the retry creates a
  session, rank 1 shrinks from a full repair to a verification. Cost of
  skipping it: a full F3 repair job on a slot that is already fixed.
  Sibling M1 records the slot as FIXED 22:48 (67 tabs listed, click tab
  PASS 29ms 1.0px) (OPT-M1 mechanism, B5, citing F3 log 22:48). That
  citation must still be verified against the four G-RESTORE proofs
  (28 real tabs restored, clickable tab, renderable web page, workspace
  switch by command) before rank 1 is called done, but the direction is
  clear: verify cheap, repair only what the verification shows broken.
- R1b. VMFIX re-verify (G-VMFIX): `python3 -c "import re"` OK plus
  `ssh-laptop.sh echo SSH_OK`, seconds, before each live run from rank 4
  onward. Cost of skipping it: a live run stranded mid-fix with no worker
  able to reach the machine, a leaked Marionette session, and the owner
  with a broken browser (PRIO council 3, G-VMFIX). The J7 recurrence cost
  is the highest in the queue per minute of exposure, and the check costs
  seconds.
- R1c. F1/F2/F3 diff commit + push (todolist 4.27, lane P-H): minutes.
  Uncommitted fixes on a live machine can be lost by the next reboot or
  the next agent (redteam M4). The owner set a quantified target at 22:40:
  240 commits before 24:00, now 190, about 51 more (todolist priority
  section; redteam addendum, M4 strengthened). The uncommitted diffs are
  exactly the commits the owner is counting. Cost of skipping it: lost work
  plus a clone2 re-review of diffs that do not exist in a reviewable state.
- R1d. J12 chase (todolist 4.23, lane P-B): clone1's owed batch-4
  verification report + Firefox rerun results (Y10 t05/t09/t10). A message
  from Muse, not a run. Cost of skipping it: the A1 pilot resumes on
  unverified blockers, and a missing verification report is a live violation
  of the Lauren Tan evidence contract (PRIO council 2, GAP 1).
- R1e. PR #1 conflict check (todolist 4.26, lane P-G): the conflict is on
  a coord file, not code (PRIO crawl log, clone2 note). Resolving it is
  cheap; leaving it open blocks the scrub (redteam M2) and counts against
  the 240-commit target as an unmerged PR.
- Voice 3 position: R1a-R1e run NOW, in parallel lanes, before any new
  expensive live run is briefed. None of them consumes the live slot. All
  five together cost less than one spurious live run.

## R2. What a spurious live run costs (why gates exist)
- A live run before G-RESTORE fails spuriously, burns tokens, and risks
  corrupting the user's real tabs for zero signal (PRIO council 3,
  G-RESTORE). The 13 real tabs (YouTube, Todoist, Gmail, Calendar, Muse
  chat, PCCV CF26 Sheets, Free Claude Code Admin 8082, Welcome, Polygon,
  codeforces, chunkbase, duck.ai, BytePlus) are the owner's working set; a
  Zen restart without verified session restore loses them (PRIO council 3,
  rank 1).
- A live run without the G-HIDDEN pre-flight can die on a hidden body
  exactly like q01/q02 did at 17:52, and the failure will be misread as a
  defect in Y13/Y14/A1 instead of a hidden tab, triggering a fix cycle for
  a bug that does not exist (PRIO council 3, G-HIDDEN; rank 6).
- A live run before Y13r2 verdict + H3 direction, or before Y14b clears,
  runs code its own reviewers have not passed (PRIO council 3, ranks 6-7).
  A spurious Y13 is worse than a late Y13, because a spurious failure
  triggers a fix cycle for a bug that does not exist.
- An A1 run on a stale relay measures the old broker, not the new plan
  (G1: relay MainPID 106001, started 00:19 17/11, never restarted, code
  d45434c on disk only; PRIO council 3, rank 8). An uninterpretable A1 run
  is worse than a delayed one.
- A Y6 retry that skips A9 (re-review) or A8 (load-only trial) repeats the
  Y6c NO VERDICT outcome (F0/F1/U5b, commit 5a2b69d): a wasted retry
  (PRIO council 3, rank 5).
- A Phase B verdict on unrewritten probes 10b/10f is a false pass on a
  security boundary: the probes would PASS the vulnerable implementation,
  and a merge on that verdict ships the vulnerability with a test suite
  claiming it is covered (PRIO council 3, rank 12). That is the single
  most dangerous false pass in the queue.
- Voice 3 position: every gate in the todolist (G-VMFIX, G-RESTORE, G-TAB,
  G-F1-BEFORE-F2, G-PILL, G-SINGLE-LIVE, G-HIDDEN, G-H2, G-SCRUB, G-Y1B)
  is a cost-avoidance device, not bureaucracy. The verdict must keep all
  of them. The cheapest run is the run that does not happen until its
  gates are green.

## R3. What must NEVER run in parallel (contention costs)
- Two live drivers on one Zen. BiDi + Marionette share ONE session total;
  a leak blocks both (todolist 1.2.1). Parallel live runs contend for the
  single session, steal focus from the owner (17:59 lesson), and produce
  failures that look like product bugs but are really contention (PRIO
  council 3, G-SINGLE-LIVE).
- A live run overlapping F1/F2/F3 live probing on the same Zen. Same
  session, same screen, same failure mode.
- A hyprglass live load while F-team live work is in flight on the same
  machine. Loading a backup plugin into the live compositor risks crashing
  Hyprland while the owner works (todolist 2.2.3 BLOCKED note; PRIO council
  3, rank 5). The Y6 A8 trial and pill retry wait for F1/F2/F3 stable.
- The scrub while any push is in flight. Filter-repo + force-push
  invalidates every agent's clone; agents pushing during or just after the
  force-push lose work or push onto rewritten history, and the repo
  diverges (PRIO council 3, rank 13). G-SCRUB is the only protection.
- Two workers editing the same session/overlay files at the same time.
  F1 has uncommitted edits in scripts/cursor_session.py and
  cursor_theme.py; F2's scripts/first_action.py is untracked (redteam M4).
  F1 and F2 may be coded in parallel only if they do not edit the same
  files at the same time, otherwise they serialize (PRIO council 3,
  rank 3). A merge conflict on the startup path is the most expensive
  conflict in the queue, because it sits on the owner's first fix.
- F1 writing /usr/lib/python3.12/re/__init__.py while VMFIX investigates
  the same file. That collision already happened at 22:36 (redteam M3:
  "F1 dang sudo cp... while VMFIX investigates the same file"). Two agents
  writing to one system Python file with no owner is how J7 happened in
  the first place. The collision is resolved (F1 wrote, VMFIX verified),
  and M3 is CLOSED except for the unknown deleter (redteam addendum). The
  lesson stands as a rule: one file, one writer, one verifier.
- Voice 3 position: the parallel lanes P-A..P-H are safe ONLY because none
  of them takes the live slot or the shared session. Any lane work that
  starts driving the live machine stops being a lane and joins the serial
  queue. The verdict must state that boundary in one sentence, and every
  lane brief must carry it.

## R4. What to park and why (with the exact unpark condition)
- Track 2 + speed loop: PARKED. Unpark condition: council + redteam
  UNANIMOUS agreement in writing that no further optimization is possible
  (todolist 4.4; PRIO council 3, parked). Why: unparking early repeats the
  35+ hour unbounded loop of 19/11, burns tokens across the fleet, and
  contends with live runs for the same machine. The speed loop also needs a
  proven machine to measure against; measuring speed on a broken Zen
  measures the breakage. No such unanimous decision exists. Voice 3 AGREES
  with council 3: DO NOT UNPARK.
- Super I follow-ups: PARKED per owner deferral 17:42 (todolist, parked).
  Why: a deferred input-method issue while the browser itself is broken.
  No safety risk beyond wasted effort, but the effort is not free while
  ranks 1-3 are unfinished. Unpark condition: owner re-opens it.
- 2.1.7 I7 video: PARKED until the owner re-sends the original file.
  Why: the video exists only in Messenger E2EE, which the connector cannot
  read; the file was proven absent from the VM and the laptop (todolist
  2.1.7, Worker X 17:52). Unparking now means re-searching for a file
  already proven absent. Unpark condition: owner sends the file.
- Pending user decisions (pill final choice, H1-BASE, Step 3, save-dialog B,
  ~/backups ~99 GiB, Omarchy restore steps): PARKED until the owner decides
  (todolist 4.6). Why: these are owner decisions, not queue items; work that
  assumes an answer risks building the wrong thing and redoing it.
- E1 fresh comparison (todolist 4.22): PARKED, not rank 15. Why: E1 is
  CLOSED as run (Y8b 20:26: arm A BLOCKED by judge 7275171, arm B PASS
  single-arm 522s 0/0/0, NO comparative verdict); a fresh comparison needs
  a NEW experiment design (new labels, new pre-reg, old FAILs carried,
  budget NEW, ceiling conceded, replication pair mandatory). Running the
  old design repeats the quoting trap that blocked arm A, wastes a full
  comparison budget, and produces another NO VERDICT (PRIO council 3,
  rank 15). Unpark condition: a new design is written and reviewed, and
  the owner schedules it. If ever scheduled as real work, it runs BEFORE
  the final test, because the final test is LAST (redteam A6; PRIO council
  2, rank 14 condition).
- J15 17:59 keyboard/mouse freeze cause (todolist 4.25): PARKED low. Why:
  Y4b proved the probe navigations at 17:59:27/33 did NOT cause it (onset
  17:59:13 predates them); self-recovered, no recurrence since (PRIO crawl
  log J15). Unpark condition: it recurs. If it recurs, it jumps the queue
  at once, because a freeze while the owner is at the keyboard is a safety
  issue, not a curiosity (PRIO council 3, parked).
- J7 deleter (unknown restorer of re/__init__.py at 22:31:12): NOT parked,
  but NOT a rank either. It lives as the watch tail inside G-VMFIX (voice 2,
  P0). Until VMFIX names who or what restored the file, the queue treats
  the VM Python install as suspect, not healthy (PRIO council 3, J7
  fallback).

## R5. The clone2 timing dispute, priced
- The owner ordered at 22:31: "dot manh token cua clone2 hon di, no it viec
  va viec cua no nhe qua roi" (PRIO council 2, rank 9 challenge; redteam A4).
  The owner quantified the burn at 22:40: 240 commits before 24:00, about
  51 more (redteam addendum, M4 strengthened). A serial queue that parks
  clone2 at rank 9 cannot produce that volume; parallel lanes are the only
  way to hit the number (redteam addendum).
- But the heavy batch has two readiness costs if issued now. First, clone2
  pushed batch 5 (c77e8a1) at about 22:29 after silence from 19:22, and its
  10-minute watchdog duty from 19:09 produced zero logs (J16). Issuing a
  heavy batch before batch 5 is verified risks building the next batch on
  unverified output (PRIO council 3, rank 9). Second, the heavy batch's
  F1/F2/F3 re-review slice reviews diffs that are still moving and partly
  uncommitted (redteam M4). A review of a moving diff is wasted tokens.
- Voice 3 position: AGREE with PRIO council 3's split, which is also the
  todolist's decided split (lane P-A light now, serial rank 9 heavy after
  batch-5 verification + frozen diffs). The light batch (J14 checker
  follow-ups, batch-5 self-verification, formally closing or reassigning
  the J16 watchdog duty) is ready TODAY, costs no live slot, and burns
  tokens now, satisfying the owner's 22:31 order immediately. The heavy
  batch waits for its inputs to exist, which is not delay for its own sake
  but the precondition of a useful review. DISAGREE with council 2's serial
  rank 5 (it issues the heavy batch before its input exists) and DISAGREE
  with a pure "burn now, review later" reading of the 22:31 order (burning
  tokens on a review of a moving diff is not squeezing dry, it is wasting
  dry).
- Clone1 batch 6 was issued at 22:40 (blind ZT scenarios, evidence audit of
  all history, re-verify batch-3 + D1). That is a parallel lane burn that
  does NOT close J12 (redteam addendum, M1). Voice 3 records: batch 6 is
  throughput, J12 is the owed evidence. Both must be tracked separately, or
  the batch-6 activity will be misread as the J12 report landing.

## R6. The scrub timing trap, priced
- The scrub (todolist 4.20) needs a quiet fleet window. Under the owner's
  22:31 order (full throttle, burn clone2 harder) plus the 22:40 target (240
  commits before 24:00), no quiet window will ever occur naturally (redteam
  A6). Rank 11 as written is a dead letter: it will never execute, because
  the fleet is ordered never to be quiet.
- The cost of running it without a window: broken in-flight pushes,
  invalidated clones, collision with PR #1 (already CONFLICTING on a coord
  file), possibly a re-do of the scrub itself (PRIO council 3, rank 13).
- The cost of delay: the real name stays on main longer (71 lines / 45
  files), against the standing rule NO PERSONAL INFO ON GITHUB. Bounded:
  the email (the more sensitive identifier) is already gone (commit
  1c7d252), and the name exposure is in a repo the owner controls (PRIO
  council 3, rank 13).
- Voice 3 position: the verdict must pick ONE mechanism and write it down
  (redteam A6 demands this; PRIO council 3 G-SCRUB demands this). Voice 3
  recommends: Muse schedules an explicit one-time fleet pause with a date,
  announced to all agents, after the final test is briefed but before it
  runs, OR the scrub is deferred to after the final test. Voice 3 does NOT
  recommend running the scrub between live ranks on a "probably quiet"
  window: a probably-quiet window is not a verified quiet window, and the
  failure mode is a diverged repo.
- Note the ordering consequence: if the scrub is deferred to after the final
  test, then the final test is no longer the last EXECUTED item, only the
  last WORK item. The verdict must say that plainly, so the owner's LAST
  order is not silently redefined.

## R7. Cost of the F1/F2 ordering mistake, if the verdict gets it wrong
- If F2 is ranked and measured before F1 lands: F2 is built and "proven"
  against a dead session, or its under-30s target is unmeasurable and the
  work is redone once F1 lands (PRIO council 3, rank 2). Worse, an overlay
  that shows while no session exists misleads the owner into thinking
  computer-use is on when it is not, which is exactly the I12 failure mode
  (overlay gone, worker unaware).
- If F1 is rushed without review: F1 has uncommitted edits to
  scripts/cursor_session.py and cursor_theme.py. Landing them without review
  risks a half-fix that starts the session but leaves the overlay broken,
  which then looks like an F2 failure (PRIO council 3, rank 3). Sibling M1
  lists the remaining gaps precisely: guard_reply misses UnicodeDecodeError
  (council 1 A3) and misdiagnoses truncated JSON (redteam R4); supervise
  has a drain race (council 1 A1), no detail on driver registration failure
  (council 1 A2), silent drain-thread death on non-UTF8 stderr (redteam R5),
  no drain settle (redteam R6), and a deque/tail that can drop the root
  cause (redteam R7) (OPT-M1 mechanism, A1-A2). Each gap is a re-run of the
  same incident if it ships unreviewed.
- Voice 3 position: the merged F1+F2 cluster with F1 verified first
  (G-F1-BEFORE-F2) is the cheapest ordering, because it pays the review cost
  once and the measurement cost once. Any ordering that measures F2 first
  pays both costs twice.

## R8. Cost of the Y13/Y14 ordering mistake
- If Y13 runs before its three gates (Y13r2 verdict, H3 direction,
  Marionette slot): spurious failure, misattributed to Y13 code, triggers a
  fix cycle for a bug that does not exist (PRIO council 3, rank 6).
- If Y14 runs before Y14b clears: runs code its own reviewers have not
  passed (PRIO council 3, rank 7).
- If Y13 and Y14 run in parallel: single shared session contention, leak,
  block each other (PRIO council 3, rank 7).
- If the slot idles while only one of them is gate-green: wasted live-slot
  time. Voice 3 AGREES with the dependency voice's readiness rule: run
  whichever is green; if both green, Y13 first per roadmap. An idle live
  slot while a gate-green run waits is the most expensive idle in the queue.

## Voice 3 summary
- Cheapest first: Marionette retry, G-VMFIX re-verify, diff commit + push,
  J12 chase, PR #1 check. All in parallel lanes, all before any new
  expensive live run.
- Never parallel: two live drivers; live run overlapping F-team probing;
  hyprglass live load during F-team live work; scrub during any push;
  two writers on one file (session/overlay files, system re file).
- Parked with exact unpark conditions: Track 2/speed loop (unanimous
  council + redteam in writing); Super I (owner re-opens); I7 video
  (owner re-sends file); pending decisions (owner decides); E1 (new design
  reviewed + owner schedules, before final test if ever run); J15 (recurs,
  then jumps the queue).
- The scrub needs a scheduled fleet pause with a date, or deferral to after
  the final test, stated plainly. "Rank 11" without a mechanism is not a plan.
- The merged F1+F2 cluster with F1 verified first is the cheapest ordering;
  measuring F2 first pays review + measurement twice.

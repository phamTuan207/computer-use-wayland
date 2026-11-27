# Council 3 verdict - risk / safety review of PRIO draft ranked queue
# Council 3 (risk / safety). Date: Sat 2026-11-21, ~22:40 +07.
# Sources read: improvements/worker-prio-crawl-log.md (J7-J16 + draft queue 1-15),
# docs/zen-error-fix-todolist-20261121.md, cf26-upload LOI section 12 (J1-J6).
# Lens: what breaks if the draft order is wrong. For each rank: AGREE or
# CHALLENGE, with the concrete failure if it runs too early or too late.
# No em/en dashes in this file, per owner standing rule.

## Summary judgment

- AGREE with the overall shape: restore the live machine first, then prove it
  with blind tests, then run live experiments in order, with the scrub, the
  final test, and E1 at the end.
- CHALLENGE on 4 ranks: 2/3 swap, 9 too early, 10 too late, 13 needs a hard
  gate not just a rank number. Rank 5 is AGREE only under its stated gates.
- The draft queue has one structural hole: it has no fallback if J7 recurs.
  VMFIX tracking is noted, but no rank says what the fleet does when SSH or
  Python breaks mid-queue. That hole is fixed by Gate G-VMFIX below.
- The draft queue has one ordering contradiction: ranks 6, 7, 8 are live runs
  that can be killed by the hidden-body failure, but the decisive hidden-body
  experiment that would de-risk them sits at rank 10, after them. That is
  fixed by Gate G-HIDDEN below, not by moving the whole experiment.

## Hard gates demanded by Council 3

- G-RESTORE: Nothing live runs before rank 1 is verified green. No ZT-B, no
  Y13, no Y14, no A1 pilot, no Y6 pill retry, no hidden-body live run, no H2
  agent-driven run, no final test. "Verified green" means: Zen PID alive,
  owner can click a tab and open a web page, Marionette POST /session creates
  a session (no "browserElement is null"), session restore shows the 13 real
  tabs, and the 15-tab cleanup ends with the driver focused on a LIVE tab.
  Reason: every live run before this point fails spuriously, burns tokens,
  and risks corrupting the user's real tabs for zero signal.
- G-TAB: During any tab cleanup or live run, a sacrificial live tab must be
  opened BEFORE closing tabs, and the session must end while focused on a
  live tab. Never DELETE a session while the current tab is a closed tab.
  Reason: that exact mistake left Zen in the dead-tab state that caused the
  Marionette slot failure at 22:06, 22:10, 22:12 (J3). A repeat strands the
  next live run the same way.
- G-F1-BEFORE-F2: F1 guardian fix must land and be verified before F2's
  <30s first-visible-action target is measured. F2 may be coded in parallel,
  but its measurement is gated on F1 green. See ranks 2 and 3.
- G-SINGLE-LIVE: Only ONE live runner at a time on the laptop Zen. BiDi and
  Marionette share ONE session total, and a leak blocks both. Y13, Y14, A1,
  ZT-B, Y6 retry, hidden-body, and H2 live runs are strictly sequential,
  never parallel, never overlapping with F1/F2/F3 live probing on the same
  Zen. Reason: parallel live runs contend for the single session, steal
  focus from the owner (17:59 lesson), and produce failures that look like
  product bugs but are really contention.
- G-HIDDEN: Every live run at ranks 6, 7, 8 must carry the Y4b pre-flight
  (body visible check on the tab it will drive, before the first action),
  even though the full decisive experiment sits at rank 10. If the
  pre-flight fails, the run aborts and reports, it does not retry blindly.
  Reason: q01/q02 already failed on hidden body at 17:52. Without the
  pre-flight, ranks 6-8 can die the same way and the failure will be
  misread as a defect in Y13/Y14/A1 instead of a hidden tab.
- G-VMFIX: Before any live rank (4 and onward), VMFIX must confirm the J7
  cause and the hardening, or at minimum the queue must re-verify
  `python3 -c "import re"` OK plus `ssh-laptop.sh echo SSH_OK` immediately
  before the live run starts. If SSH or Python breaks mid-queue: FREEZE all
  live work at once, do VM-local work only (reviews, Y1b offline rewrites,
  scrub planning, batch verification), and never assume a self-restore
  means fixed, because the 22:31 restore has an UNKNOWN restorer. A
  self-restored `re` module with no known cause is not a fixed `re` module.
  Reason: J7 broke tailscale-proxy.py and all of python3 importing `re`,
  and killed VM to laptop SSH for about 6 minutes. A recurrence mid live
  run strands Zen half-fixed, leaves a Marionette session leaked, and
  leaves the owner with a broken browser and no worker able to reach it.
- G-PILL: Y6 pill retry (rank 5) needs ALL of: A1-A10 landed, fresh
  re-review done, F1/F2/F3 stable, and A8 load-only trial first. No live
  hyprglass load into the owner's working compositor without a handover or
  idle window. See rank 5.
- G-SCRUB: The history scrub (rank 13) runs ONLY in a verified quiet fleet
  window: all in-flight pushes landed, PR #1 resolved or explicitly
  handled, no live run in flight, and every agent notified to re-clone
  after the force-push. Rank position alone does not create that window.
  If the window is not real when rank 13 arrives, rank 13 WAITS. See
  rank 13.
- G-Y1B: No executor-hardening merge until all 12 Y1b must-fix items are
  proven fixed AND probes 10b/10f plus 1e/4a are rewritten. See rank 12.
- G-FINAL-LAST: The final Codeforces test runs only after every other rank
  is done or explicitly closed, per the owner order at 16:30, confirmed
  twice. See rank 14.

## Rank by rank verdict

### Rank 1. F3 Zen restore (4.7/4.8, J1/J2) + Marionette slot (4.10, J3) + finish 15-tab cleanup. AGREE.
- Why this must be first: the owner cannot use the user's browser at all (22:25,
  J1). Zen PID 27958 alive but no web clickable or openable, sidebar
  collapsed to icons, workspace switching also broken (J2). Every later
  rank gates on this. Running anything live before it is guaranteed noise.
- Failure if too late: owner stays locked out of the user's own browser while the
  fleet works on lower items; every live result after that is suspect
  because the base machine was never proven healthy.
- Failure if rushed: a Zen restart without verified session restore loses
  the 13 real tabs (YouTube, Todoist, Gmail, Calendar, Muse chat, PCCV
  CF26 Sheets, Free Claude Code Admin 8082, Welcome, Polygon, codeforces,
  chunkbase, duck.ai, BytePlus). A tab cleanup that ends on a dead tab
  re-creates the J3 Marionette failure. Both are prevented by G-RESTORE
  and G-TAB: verify restore of the 13 real tabs first, open a sacrificial
  tab before closing anything, end on a live tab.
- Extra risk: F3 has no log file yet (per PRIO crawl). A restore with no
  log is unverifiable after the fact. F3 must write its diagnosis and
  restore log before rank 1 is called done.

### Rank 2. F2 silence fix (4.12, J5). CHALLENGE, swap with rank 3.
- PRIO itself notes F1 and F2 intertwine. Council 3 calls the order wrong
  as ranked: F2's fix (first visible action under 30s, continuous ops,
  overlay always on) cannot be measured while F1's guardian fails to
  start a session at all (J4, 0.46s death, "session guardian startup
  failed"). The 5 minute silence in J5 was largely Muse diagnosing the
  guardian in silence, so the silence and the guardian failure are the
  same incident viewed twice.
- Failure if F2 runs first: F2 is built and "proven" against a dead
  session, or its <30s target is unmeasurable and the work is redone once
  F1 lands. Worse, an overlay that shows while no session exists misleads
  the owner into thinking computer-use is on when it is not, which is
  exactly the I12 failure mode (overlay gone, worker unaware).
- Failure if F2 runs too late (after F1, as Council 3 demands): none
  material. F2 is still rank 2 in effect once F1 is its precondition.
  The owner's words ("fix this FIRST", 22:16) are about the silence
  symptom, not about the dependency order. The dependency order is
  F1 then F2.
- Verdict: CHALLENGE the order. Swap ranks 2 and 3, or run them as one
  combined fix with F1 as the explicit precondition and F2 measurement
  gated by G-F1-BEFORE-F2. Do not let F2 claim done on a session that
  never started.

### Rank 3. F1 guardian/session fix (4.11, J4). CHALLENGE, promote to rank 2.
- Same reasoning as rank 2, opposite direction. F1 is the precondition
  for F2, for the overlay, and for any session at all. "Computer use cung
  ko thay bat" (22:16) is a session-start failure, not a speed failure.
- Failure if too late: every overlay, silence, and live-run fix is built
  on a session that cannot start, so all of it is unverified.
- Failure if rushed: F1 has uncommitted edits to scripts/cursor_session.py
  and cursor_theme.py (per PRIO crawl). Landing them without review risks
  a half-fix that starts the session but leaves the overlay broken, which
  then looks like an F2 failure. F1 must land as a reviewed diff, with
  the guardian printing 'ready' and the session surviving a full
  start-to-first-action cycle.
- Verdict: CHALLENGE the order. Promote to rank 2. F1 and F2 may be coded
  in parallel by different workers only if they do not edit the same
  session/overlay files at the same time; otherwise they serialize.

### Rank 4. ZT-B blind ordinary-user Zen tests (4.9, J6). AGREE, under G-RESTORE and G-SINGLE-LIVE.
- Why here: ZT-A is done (a5a5553 + 138919b, 10 composite blind scenarios
  ZT-01..ZT-10 + ZT-00 health gate, council AMEND + redteam BLOCK fixed
  in v2). ZT-B is the proof that the restored machine is usable by an
  ordinary user, and its errors feed the fix queue. That is the right
  next step after restore.
- Failure if too early (before G-RESTORE): blind tests on a broken Zen
  produce noise, not signal. Every failure would need re-triage as
  "broken machine" versus "real defect", and the blind runner cannot tell
  the difference. The ZT-00 health gate exists for exactly this reason
  and must pass first.
- Failure if too early in another way: R-01 (blind Ctrl+W could close the
  user's real tab) was fixed in v2, but the fix must be verified in the
  ZT-B brief itself, not assumed from the v2 commit message. A blind
  runner on real Zen with real tabs is the highest collateral risk in
  the whole queue. ZT-B must run only on the restored machine, only one
  live runner at a time (G-SINGLE-LIVE), and must stop at once on any
  unexpected focus change while the owner is at the keyboard.
- Failure if too late: later live runs (Y13/Y14/A1) run without the
  ordinary-user error feed, so they re-discover the same defects slowly
  instead of inheriting ZT-B's list.
- Verdict: AGREE, conditional on G-RESTORE, ZT-00 pass, and the R-01
  guard restated in the ZT-B brief.

### Rank 5. Y6 A1-A10 fix list + fresh re-review, then pill measurement retry (4.13, 2.2.3). AGREE, under G-PILL. Do not run the retry while F1/F2/F3 are still fixing the live machine.
- Why here and not higher: the pill is the owner's visible pain, but it
  does not block browser use. Zen restore, silence, and session start
  all outrank it. Y6r AMEND was unanimous and the retry is explicitly
  blocked until A1-A10 land plus a fresh re-review, so rank 5 is the
  earliest honest position.
- Failure if too early, the main risk in this rank: loading hyprglass
  into the live compositor while F1/F2/F3 are still fixing the same live
  machine risks crashing Hyprland while the owner works, and risks a
  measurement taken on a machine whose session and overlay are still
  broken, which then reads as a pill verdict when it is really a session
  verdict. The 2.2.3 history already shows this pattern: the animated
  backdrop test could not run because loading a backup plugin into the
  live compositor risked crashing Hyprland mid-work.
- Failure if the A1-A10 list is skipped or shortened: A9 (re-review the
  fix diff before any measurement run) and A8 (load-only trial first)
  are the two items that prevent a repeat of the Y6c NO VERDICT outcome
  (F0/F1/U5b, commit 5a2b69d). Skipping them repeats a wasted retry.
- Failure if too late: the pill stays at blur 0.15 with the interior
  refraction question open, and the owner keeps judging by eye. That is
  a real cost, but it is a taste cost, not a blocking cost. It does not
  outrank a working browser.
- Verdict: AGREE at rank 5, gated by G-PILL. The retry must never start
  while F1/F2/F3 live work is still in flight on the same machine.

### Rank 6. Y13 live run, codex-y5 (4.14). AGREE, under G-RESTORE, G-SINGLE-LIVE, G-HIDDEN, and its own gates.
- Why here: live queue order per roadmap is Y13 first, and Y13r2 is
  already running. That order is sound once the machine is restored.
- Failure if too early: Y13 needs three gates (Y13r2 verdict, H3 gate
  direction, Marionette slot). Running before any of them fails
  spuriously, burns a live run, and the failure gets misattributed to
  Y13 code instead of to the missing gate. The Marionette slot gate is
  G-RESTORE; the other two are Y13-specific and must be named as met
  before the run starts, not discovered during it.
- Failure if too early in a second way: without the G-HIDDEN pre-flight,
  Y13 can die on a hidden body exactly like q01/q02 did at 17:52, and
  the run will look like a Y13 failure.
- Failure if too late: Y14 and A1 queue behind it, so a late Y13 delays
  the whole live queue. That is acceptable; a spurious Y13 is worse than
  a late Y13, because a spurious failure triggers a fix cycle for a bug
  that does not exist.
- Verdict: AGREE, conditional on all three gates plus G-HIDDEN.

### Rank 7. Y14 live run, batch-3 (4.14). AGREE, under the same gates plus Y14b re-stage clearing.
- Why here: Y14 after Y13 is the roadmap order, and Y14b is running its
  re-stage. Sequential live runs are the only safe shape here.
- Failure if too early: Y14b re-stage has not cleared (redteam AMEND
  bd3c6c9 at 22:22). Running before it clears means running code that
  its own reviewers have not passed.
- Failure if run in parallel with Y13: the single shared Marionette/BiDi
  session means the two live runs contend, leak, and block each other
  (todolist 1.2.1: session cap shared, leak blocks both). G-SINGLE-LIVE
  forbids this outright.
- Failure if too late: batch-3 checker follow-ups (J14) stay unverified
  longer. Acceptable; J14 is also proposed as clone2 batch content at
  rank 9, which is offline review work and does not need the live run.
- Verdict: AGREE, strictly after Y13, strictly after Y14b clears.

### Rank 8. A1 pilot resume (4.15). AGREE, under its preconditions plus G-RESTORE, G-SINGLE-LIVE, G-HIDDEN.
- Why here: A1 is the only proposal with our own measured win (Pick 1,
  wall time down 53 percent), so resuming it is worth real priority.
  But it was frozen at 18:46 (f31abcf) for cause: clone1 review found
  28 holes, 3 blockers (1ddac2d).
- Failure if too early: running before the 3 blockers are addressed and
  before the preconditions are met (written order naming 12 run-ids,
  broker SOLO plus idle, relay verified, Layer-2 probes, checker
  real-run cross-check) repeats the frozen pilot with the same holes,
  and the result is uninterpretable. Running while F1/F2/F3 are still
  fixing the live machine adds the G1 stale-code risk: a relay started
  before a broker change silently runs old code, which is exactly how
  G0-observe died (relay MainPID 106001, started 00:19 17/11, never
  restarted, code d45434c on disk only). A1 on a stale relay measures
  the old broker, not the new plan.
- Failure if too late: the one measured speedup in the queue stays
  frozen while lower-value work runs. That is the cost of the gates, and
  it is worth paying, because an uninterpretable A1 run is worse than a
  delayed one.
- Verdict: AGREE at rank 8, only if the 3 blockers and all preconditions
  are shown met in writing before the run starts. No verbal "ready".

### Rank 9. Clone2 heavy batch (4.16). CHALLENGE, too early as ranked. Demote until batch 5 is verified and F1/F2/F3 diffs are frozen.
- The owner order at 22:31 ("burn clone2 harder, its work was too light")
  is real, and Council 3 does not dispute the direction. The timing and
  the content as ranked are the problem.
- Failure if issued now, first: clone2 pushed batch 5 (c77e8a1) at about
  22:29 after being silent from 19:22, and its 10-minute watchdog duty
  from 19:09 produced zero logs (J16). Issuing a heavy batch before
  batch 5 is verified, and before the unfulfilled watchdog duty is
  formally closed or reassigned, rewards silence with more work and
  risks building the next batch on unverified batch 5 output. If batch
  5 has an error, the heavy batch inherits it.
- Failure if issued now, second: the suggested content includes an
  independent re-review of F1/F2/F3 diffs. Those diffs are still moving
  (F1 has uncommitted edits, F3 has no log yet). A review of a moving
  diff is wasted tokens: it reviews code that will change before the
  review lands, or it blocks F1/F2/F3 while they wait for a review of
  code they have not finished.
- Failure if issued now, third: J14 checker follow-ups as batch content
  are fine offline, but bundling them with a re-review of live diffs
  mixes two different readiness states into one batch. The batch will
  look done when only its offline half is done.
- Failure if delayed too long: clone2 tokens sit idle while the owner
  explicitly wants them burned. That is a real cost, and Council 3 does
  not propose parking clone2. The fix is sequencing, not delay for its
  own sake.
- Verdict: CHALLENGE the rank. Split rank 9: (a) issue an immediate
  light batch now if one is needed, limited to offline work that is
  ready today (J14 checker follow-ups, batch 5 self-verification, and
  formally closing or reassigning the J16 watchdog duty); (b) issue the
  heavy batch, including the F1/F2/F3 re-review, only after batch 5 is
  verified AND the F1/F2/F3 diffs are frozen. In queue terms, the heavy
  batch belongs after ranks 1-3 land, around rank 11-12, not at rank 9.

### Rank 10. Hidden-body decisive experiment + Y4d/Y7 follow-ups (4.17, J9). CHALLENGE, too late as a standalone rank. Keep the rank, but pull its pre-flight forward.
- The experiment itself (Y4b design: htmlClass plus rAF tick on the SAME
  hidden tab in the SAME minute) has never run, and the tracked defect
  item is still OPEN. Zero encounters in Y4d and Y9b reruns do not prove
  the recovery ladder works; they prove the failure did not happen to
  occur in those runs.
- Failure if too late (the ordering contradiction): ranks 6, 7, 8 are
  live runs that can all be killed by the hidden-body failure, but they
  sit before the experiment that would de-risk them. If Y13 dies on a
  hidden body, the team will spend a fix cycle on Y13 before learning
  the cause was the tab, not Y13. That is the most expensive form of
  "too late" in this queue.
- Failure if run too early (before G-RESTORE): the experiment needs a
  live Zen with a drivable tab. On a broken Zen it produces zero
  encounters again, which will be misread as "hidden body is rare" when
  it really means "the machine was broken".
- Verdict: CHALLENGE the position, not the item. Keep rank 10 as the
  full decisive experiment, but make G-HIDDEN (the pre-flight on every
  live run at ranks 6-8) a precondition of those runs. The Y4d
  follow-up (shared bootstrap tab does not survive its session) and the
  Y7 follow-ups (test-07 restore marker as the biggest hole, test-09
  off-spec bypass note, simulate --all first-crash abort) should be
  briefed into ranks 6-8 as known holes, not left to be rediscovered
  after rank 10.

### Rank 11. H2 think-time measurement, agent-driven (4.18, J10). AGREE in substance, CHALLENGE as a standalone late run. Fold the measurement into ranks 6-8.
- The substance is right: Y11b proved H2 is still open because its proof
  was scripted (think values null by design), and todolist 2.3.1 is
  ticked DONE with no live agent-driven measurement. That tick is a
  false done, and J10 is right to re-open it.
- Failure if run as a standalone late run: by rank 11, ranks 6, 7, 8
  have already run as agent-driven live runs, and their think times were
  either measured or lost. If they were not instrumented, rank 11 has to
  stage a fresh agent-driven run just to measure what the earlier runs
  could have measured for free. If they were instrumented, rank 11 is
  redundant.
- Failure if run too early (before any agent-driven live run exists):
  there is nothing agent-driven to measure yet, so the run is scripted
  again and H2 stays open again.
- Verdict: AGREE that H2 must be closed by an agent-driven run, but
  CHALLENGE the standalone rank. Instrument ranks 6, 7, 8 for think
  time per step from the start, and let the first agent-driven live run
  that yields real think values close H2. Rank 11 then becomes a
  verification and reporting step, not a fresh run. If none of ranks 6-8
  yields usable think values, rank 11 runs as a dedicated measurement
  run, and its brief must say so explicitly.

### Rank 12. Y1b snippets (4.19, J13). AGREE, with G-Y1B as an absolute gate, not a preference.
- The substance is right: the 12-item must-fix checklist stands, no
  executor-hardening merge until all 12 are proven fixed, and probes
  10b/10f plus 1e/4a must be rewritten before Phase B is judged.
- Failure if judged too early (the dangerous case): probes 10b/10f are
  structurally unable to catch the budget amplification they were
  written for, because the outer program aborts at the first snippet's
  2 second wall and the second run_snippet never executes in EITHER
  implementation. They would PASS the vulnerable implementation. A
  Phase B verdict on those probes is a false pass on a security boundary,
  and a merge on that verdict ships the vulnerability with a test suite
  claiming it is covered. That is the single most dangerous false pass
  in the queue.
- Failure if too late: the executor hardening stays unmerged longer, and
  the Y1b live watch (Codex PID 184702) has been unconfirmed since about
  19:00. The watch status must be re-confirmed before rank 12 work
  starts, or the team may be reviewing a dead run.
- Verdict: AGREE at rank 12, with G-Y1B absolute. No merge, no Phase B
  verdict, until the probes are rewritten and the 12 items are proven
  fixed. This gate does not move for schedule pressure.

### Rank 13. Email + real-name history scrub (4.20, J8). AGREE on position, CHALLENGE on execution: rank alone does not respect the quiet-window requirement.
- The position is defensible: the email is already removed from main
  (commit 1c7d252, grep 0), the remaining exposure is the real name in
  71 lines across 45 files, and the scrub plan exists
  (docs/email-history-scrub-plan.md). Putting it after the live work
  and before the final test is a reasonable trade.
- Failure if run too early (the risk the task asks about): a filter-repo
  plus force-push while the fleet is active breaks in-flight pushes,
  invalidates every agent's clone, and collides with PR #1, which is
  already CONFLICTING on a coord file. Agents pushing during or just
  after the force-push lose work or push onto rewritten history. The
  scrub then has to be redone or, worse, the fleet re-clones at
  different history points and the repo diverges. Rank 13 as a number
  does not prevent this: if the fleet is still active when rank 13
  arrives, running it because "it is rank 13 now" is exactly the
  failure. That is why G-SCRUB is demanded.
- Failure if run too late: the real name stays on main longer, against
  the owner's standing rule of NO PERSONAL INFO ON GITHUB. The exposure
  cost of delay is real but bounded: the email (the more sensitive
  identifier) is already gone, and the name exposure is 71 lines in a
  repo the owner controls. A delay of hours to reach a real quiet window
  is cheaper than a force-push that breaks the fleet mid-queue.
- Verdict: AGREE on position, CHALLENGE on execution. Rank 13 runs only
  under G-SCRUB. PRIO must name the quiet window explicitly (who has
  landed, what PR #1 state is, who is notified to re-clone) before the
  scrub starts. If no quiet window exists when rank 13 arrives, rank 13
  waits, and the wait is reported, not silently skipped.

### Rank 14. Final test, independent Codeforces contest (4.21). AGREE, strongly.
- The owner ordered it LAST at 16:30, confirmed twice. Rank 14 honors
  that order. No council argument for moving it earlier exists.
- Failure if run early: the test uploads 5 problems through Polygon on
  the user's own Codeforces account, with no Hieu permissions and no
  effect on anyone else only if it is done cleanly. Run early, on a
  machine whose Zen, session, overlay, and Marionette slot are still
  broken, it produces errors that cannot be attributed: is the failure
  the final test, or the machine? It also risks leaving half-uploaded
  problems on the owner's account, which then have to be cleaned up by
  hand. The "independent contest" is only independent if the machine
  underneath it is proven.
- Failure if run too late: none identified, beyond the owner waiting
  longer for the final proof. The final test is the proof, not the work,
  so it belongs last by definition.
- Verdict: AGREE. G-FINAL-LAST stands. The final test also needs
  G-RESTORE and G-SINGLE-LIVE, and per-step time logging, so every error
  surfaces for fixing.

### Rank 15. E1 fresh comparison (4.22). AGREE.
- E1 is closed as run (Y8b 20:26: arm A BLOCKED by judge 7275171, arm B
  PASS single-arm 522s 0/0/0, NO comparative verdict), and a fresh
  comparison is deferred by council and redteam to a NEW experiment
  (new labels, new pre-reg, old FAILs carried, budget NEW, ceiling
  conceded, replication pair mandatory). Todolist 3.4.1 still says
  "THI NGHIEM DANG DO, CHUA CO KET LUAN" (J11), which is stale and must
  be rewritten before rank 15 is briefed, or the new worker will
  re-run the old design.
- Failure if run early: the old design repeats the quoting trap that
  blocked arm A, wastes a full comparison budget, and produces another
  NO VERDICT. The fresh design work (new labels, new pre-reg) is the
  actual work of rank 15, and it cannot be skipped by reusing the old
  plan file.
- Failure if run too late: none material. E1 is a research question
  about deliberation versus execution, not a blocker for any fix. It
  waits safely.
- Verdict: AGREE at rank 15, last. The new experiment design must be
  reviewed before the comparison runs, and the stale 3.4.1 text must be
  corrected first (J11).

## Parked items: dangerous to unpark early

- Track 2 + speed loop: PARKED, do not unpark. The gate is council plus
  redteam unanimous agreement that no further optimization is possible,
  and that agreement does not exist. Unparking early repeats the 35+
  hour unbounded loop of 19/11, burns tokens across the fleet, and
  contends with the live runs in ranks 1-8 for the same machine. The
  speed loop also needs a proven machine to measure against; measuring
  speed on a broken Zen measures the breakage. Any unpark proposal must
  come with the unanimous council + redteam decision in writing.
- Super I follow-ups: PARKED per owner deferral at 17:42. Unparking
  early spends live-machine time on a deferred input-method issue while
  the browser itself is broken. No safety risk beyond wasted effort,
  but the effort is not free while ranks 1-3 are unfinished.
- 2.1.7 I7 video: PARKED until the owner re-sends the original file.
  The video exists only in Messenger E2EE, which the connector cannot
  read. Unparking it now means re-searching for a file already proven
  absent from the VM and the laptop. No action is possible without the
  file.
- Pending user decisions (pill final choice, H1-BASE, Step 3,
  save-dialog B, ~/backups ~99 GiB, Omarchy restore steps): PARKED
  until the owner decides. These are not queue items; they are owner
  decisions. Running work that assumes an answer to any of them risks
  building the wrong thing and having to redo it.
- J15 17:59 keyboard/mouse freeze cause: PARKED low (4.25). Y4b proved
  the probe navigations at 17:59:27/33 did NOT cause it, since onset
  predated them. No recurrence since. Unparking it as an investigation
  now would consume a live-machine worker on a self-recovered, single
  incident while the browser is broken. Keep it low. If it recurs, it
  jumps the queue at once, because a freeze while the owner is at the
  keyboard is a safety issue, not a curiosity.
- J11 todolist corrections (rewrite 2.2.3 and 3.4.1): NOT parked, and
  not a rank. These are corrections PRIO must make when it edits the
  todolist, before any worker is briefed off the stale text. A worker
  briefed off "BLOCKED, owner only needs to say a letter" for 2.2.3
  will wait for a letter the owner already gave (option C at 18:16),
  and a worker briefed off "THI NGHIEM DANG DO" for 3.4.1 will re-run
  a closed experiment. Stale todolist text is itself a risk, and it is
  cheap to fix.

## J7 fallback, stated once more because the draft queue lacks it

- If Python `re` or SSH VM to laptop breaks again mid-queue: freeze live
  work immediately, do not retry the live run, do not assume a
  self-restore is a fix. VM-local work continues (reviews, offline
  rewrites, scrub planning, batch verification). VMFIX confirms the
  cause and the hardening before live work resumes. The unknown restorer
  of the 22:31 recovery is itself an open item: until VMFIX names who or
  what restored `re/__init__.py`, the queue treats the VM Python install
  as suspect, not healthy. PRIO should track VMFIX's confirmation as a
  queue precondition for ranks 4 and onward, not as a footnote.

## Verdict table

- Rank 1 F3 restore + Marionette + cleanup: AGREE.
- Rank 2 F2 silence: CHALLENGE, swap with rank 3.
- Rank 3 F1 guardian: CHALLENGE, promote to rank 2.
- Rank 4 ZT-B blind tests: AGREE, under G-RESTORE and G-SINGLE-LIVE.
- Rank 5 Y6 A1-A10 + pill retry: AGREE, under G-PILL only.
- Rank 6 Y13 live: AGREE, under G-RESTORE, G-SINGLE-LIVE, G-HIDDEN.
- Rank 7 Y14 live: AGREE, strictly after Y13 and Y14b clearing.
- Rank 8 A1 pilot: AGREE, only if 3 blockers + preconditions shown met.
- Rank 9 Clone2 heavy batch: CHALLENGE, split it; heavy half waits for
  batch 5 verification and frozen F1/F2/F3 diffs.
- Rank 10 Hidden-body experiment: CHALLENGE position, pull pre-flight
  forward to ranks 6-8 via G-HIDDEN.
- Rank 11 H2 think-time: AGREE in substance, CHALLENGE standalone rank;
  fold measurement into ranks 6-8.
- Rank 12 Y1b snippets: AGREE, with G-Y1B absolute.
- Rank 13 History scrub: AGREE on position, CHALLENGE on execution;
  runs only under G-SCRUB quiet window.
- Rank 14 Final test: AGREE, strongly, last by owner order.
- Rank 15 E1 fresh comparison: AGREE, last.
- Parked Track 2 / speed loop: DO NOT UNPARK without unanimous council
  plus redteam decision in writing.

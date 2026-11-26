# Decision meeting - Redteam attacks (27/11/2026)

Redteam role: independent of Council A and Council B. Attack every
proposal. Decision task only: nothing implemented, no cron changed, no
code edited by this document.

Inputs attacked:

- Council A: decision-meeting-councilA-20261127.md (Item 1 Codeforces
  plan; Item 7 cron disposition, 4 disable, 2 keep-repurposed).
- Council B: decision-meeting-councilB-20261127.md (Item 2 R19; Item 3
  R10; Item 4 R16; Item 5 R22; Item 6 R15).
- Background: r3-l3-fix-integration-review-20261127.md.

Evidence spot-checks done by redteam (27/11): all 6 r3l3 cron bodies in
~/workspace/goals/zen-i-u-khi-n-c-t-i-a-b-i-agent-v-muse/crons/;
~/workspace/speed-daemon/ (daemon.log grep count, daemon.out,
watchdog.py, supervisor.sh, daemon.sh, watchdog.log, supervisor.log
size); rung3-ci/pii-scan.py, validate-ledger.py, ledger-cross-check.py,
frozen-heads.txt (direct reads); rung3-run-log/
r3-l3-coordinator-state.json; R3-L3-grades.jsonl R3-037 row and scorer
grade file; improvements/fixb-evidence/ (holder-fixb.mjs,
probe-fixb.mjs, drive logs); ~/memory/2026-11-25.md and
2026-11-27.md greps; systemctl --user probe on the VM; cf26-upload
workflow file head. Claims redteam could not verify are marked
UNVERIFIED below.

Verdict scale: SUSTAIN (adopt as written), SUSTAIN WITH AMENDMENTS
(adopt only with the listed changes), KILL (do not adopt).

## Cross-cutting contradiction between the two councils (read first)

Council A Item 7.1 and Council B Item 2 contradict each other on R19.
Council A says disabling the ledger-push schedule "preserves the
current posture without deciding R19" and "R19 posture question stays
open for the owner, untouched." Council B decides R19: clean-checkout
validation becomes "the standing posture." Both cannot be the decision.
The owner delegated at 06:19 ("tu hop tu quyet di"), so deciding is
allowed, but the final decision document must pick one framing and say
so. As written, a coordinator executing both files would (a) run one
final validation pass (Council A) - in the flagged worktree, the exact
execution Council B forbids as standing posture - and (b) record R19 as
both open and decided. Redteam position: R19 IS decided by this
meeting (that is the point of the delegation); Council A's "untouched"
framing must be struck, and its "one final validation pass" must use
Council B's clean-checkout method or not happen.

Second cross-cutting conflict: Council B Item 6 says supervision stays
"exactly as is" and never mentions that the zen-laptop-health cron also
restarts the daemon (VERIFIED: cron body, "If the daemon or supervisor
is dead, restart it"). Council A Item 7.6 keeps that restarter. So the
real system has THREE supervision layers (supervisor.sh 60s loop,
watchdog.py, zen-laptop-health 15m cron), not one. Any R15 decision
that ignores the third layer is deciding about a system that does not
exist. See Items 6 and 7.6.

---

## Item 1 - Codeforces contest 735368 task plan (Council A)

Verdict: SUSTAIN WITH AMENDMENTS. Starting today is right; the lane
split and the error-call rules are not.

### Strongest objections

1. "Start now, no Zen check" trades a known owner instinct for an
   unverified assumption, and the plan has no fallback if the
   assumption fails. Council A lists as ASSUMED: "the owner's
   Codeforces manager session is still logged in in the laptop Zen
   profile and contest 735368 is still open." UNVERIFIED by redteam
   too (no live browser). The plan's mitigation is "stop and report."
   Stop-and-report on Fri 27/11 with an exam Sun 29/11 means the fix
   window is gone and Hieu gets nothing. The owner's original "check
   Zen first" instinct was not dithering; it was sequencing the one
   step everything else depends on. Delegation at 06:19 removed the
   need to ASK the owner; it did not remove the need to CHECK. The
   plan does check (driver step 1), but it commits two solver lanes
   and a reviewer in parallel with no plan B. Plan B exists and is
   cheap: the problem sources live in Drive folder "2. Cuoi khoa"
   (VERIFIED: cf26-upload workflow file describes De bai.docx,
   loi giai.c, testcases.zip per problem). If Codeforces access
   fails, statements can be extracted from Drive and solutions tested
   locally against testcases.zip, with only the submission verdict
   missing. Council A never mentions this fallback.

2. The FCC lane split ignores FCC's own record. The task brief states
   R3-037 was an FCC timeout FAIL; redteam VERIFIED the substance:
   grades ledger row R3-037, runner_session "r3-fcc-runner-L3 (FCC
   lane, pane PID 22399)", final_grade FAIL; scorer 1 grade file:
   start 14:11:44, end 14:41:43 (29 min 59 s, full 30-min cap), only
   1 of 2 domains captured, "The drive was very slow (each evaluate
   took minutes)". The mid-run replan responded by giving FCC only 3
   named easy tasks (VERIFIED: r3-l3-replan-midrun-20261125.md,
   "FCC: 3 executions (R3-014, R3-027, R3-037)"). Council A now gives
   FCC 3 of the 6 required exam problems, equal weight with Codex,
   with no justification for why FCC will be faster or more reliable
   at C++ problem-solving than it was at a two-domain WHOIS lookup.
   FCC's backend and latency are unexamined in the proposal. "Confirm
   each lane's actual capabilities by asking the lane" is listed as a
   next action, which concedes the split was decided before the
   capability check the standing rules require.

3. The 45-minute cap plus one-resubmit rule manufactures false
   "error found" calls against Hieu's problems. A non-Accepted verdict
   has at least four causes: solution bug, statement ambiguity, test
   error, checker/limit error. One resubmit with a "stated hypothesis"
   cannot reliably separate them, especially when the same lane that
   wrote the solution also diagnoses it. The report then severity-
   rates the result BLOCKING ("must fix before exam") and hands it to
   Hieu on Sat 28/11. A wrong BLOCKING call costs Hieu a rebuild of a
   correct problem the day before the exam; a missed real error costs
   the exam. The asymmetry argues for MORE verification before an
   error is reported, not a hard stop after two submissions. The
   45-minute cap compounds this: a lane that hits the cap mid-problem
   records "partial progress" and moves on, so the hardest problems -
   exactly where statement/test errors hide - get the shallowest
   check.

4. Difficulty assessment is three AI opinions in a trench coat. All
   three signals (solver self-rating, other-lane rating, Clone2
   rating) come from AI lanes that solve CF26-level problems in
   minutes. There is no student anchor: no past CF26 exam problem set
   rated the same way, no human solve time, no mapping from "AI found
   the insight in 4 minutes" to "a year-2 student finds it in 40."
   The "written before seeing the first lane's rating" independence
   claim is unenforceable as specified: solutions and ratings land in
   the same repo, and nothing sequences the writes. Council A
   concedes "AI solve time alone does not measure student
   difficulty" and then builds a system whose only inputs are AI
   judgments. Hieu asked for difficulty assessment for HIS students;
   an uncalibrated AI consensus presented as three-signal rigor is
   worse than one honest AI opinion labelled as such.

5. Account pollution is waved through. Submissions go under the
   owner's manager nick in a group contest. Council A's mitigation is
   "coordinator confirms with the parent before first submission
   whether manager submissions are acceptable as-is (expected, since
   Hieu asked the team to try the problems)." Hieu asked the GROUP to
   try the problems (VERIFIED: ~/memory/2026-11-26.md line 971,
   Hieu posted for everyone to try, first 6 required). That is not
   the same as consent for the manager account - which may have
   visibility into tests or standings - to submit. If manager
   submissions are visible to students before the exam, or pollute
   the contest Hieu will reuse, the damage is done before the report
   is written. This needs a decision BEFORE the driver lane starts,
   not a parenthetical.

### Cheaper / safer alternatives

- Single strong solver lane (Codex) for all 6, Muse subagent as
  independent second solver on any problem where Codex fails or
  disagrees with samples; FCC only as third opinion on demand. Halves
  coordination, removes the weakest lane from the critical path.
- Access-check-first sequencing: driver confirms manager access and
  extracts statements BEFORE solver lanes are briefed (1 hour), with
  the Drive-source fallback briefed in the same step. Costs nothing;
  de-risks the whole day.
- Error-call rule: no BLOCKING rating until a second lane has
  independently reproduced the failure from the statement alone
  (blind re-solve), not reviewed the first lane's solution.

### Amendments required before this becomes a decision

A1. Add the Drive-source fallback (statements + testcases.zip local
    testing) as the explicit plan B if Codeforces manager access
    fails, so "stop and report" is not the end of the task.
A2. Re-split lanes: Codex primary on all 6; FCC demoted to on-demand
    second opinion unless FCC first passes a timed capability probe
    (one known problem, local tests) recorded in the repo. Capability
    check BEFORE assignment, per standing rule.
A3. Replace "one resubmit then escalate" with: non-Accepted verdict
    triggers blind re-solve by the other lane from the statement
    only; BLOCKING error rating requires both lanes to fail the same
    way OR a concrete failing test input reproduced locally. Report
    must separate "our solution failed" from "problem is broken."
A4. Difficulty: label all ratings as AI-estimated, add one calibration
    anchor (rate 2-3 already-used CF26 problems of known category
    with the same rubric first), and sequence rating writes so
    independence is real (ratings committed before solutions are
    readable, or held by coordinator).
A5. Decide manager-account submission acceptability explicitly before
    first submission; record the decision and every submission ID in
    the report (already planned) AND in the master event log.

---

## Item 2 (R19) - Clean-checkout validation posture (Council B)

Verdict: SUSTAIN WITH AMENDMENTS. The posture is right; the spec has
holes that would make the first implementation validate the wrong
thing.

### Strongest objections

1. The pinned SHA pins the wrong artifact. Council B's mitigation for
   SHA drift: "pin the clone to the frozen head recorded for the run
   (frozen-heads.txt exists in rung3-ci/, VERIFIED by listing)."
   Redteam read frozen-heads.txt: it records list_commit 9b9d900 and
   the sha256 of docs/rung3-list-100-tasks.md. It pins the TASK LIST,
   not the validator code. Cloning todolist-push at 9b9d900 would run
   validators as they existed at list-freeze time (24/11), before the
   R5 Tier A work, before signal-hygiene.py existed, and possibly
   before later validator fixes. Council B conflates "frozen head"
   with "validator head." A clean checkout at a stale SHA validates
   the ledger against stale rules and reports exit 0 - the exact
   false-confidence failure the posture is meant to prevent.

2. The guard's actual reason is unknown, so "clean checkout fixes it"
   is unproven. Council B marks ASSUMED: "the execution-risk guard
   flags the worktree because it contains agent-written evidence."
   Redteam could not verify the guard's block message either (no
   blocked-run log was in the evidence read). If the guard flags ANY
   agent-executed Python from ~/workspace, or flags the repo by name,
   a scratch clone under the same workspace gets blocked too and the
   team has built a script that fails the same way, discovered only
   when the next run needs it. The proposal's claim "safe under any
   of the plausible reasons" is false for at least one plausible
   reason (workspace-wide execution flagging). The intermittent
   pattern (VERIFIED via council1 citation: blocks 26/11, 00:48 and
   03:48 27/11; OK 01:48, 02:48) is also unexplained by the coupling
   theory: the worktree was equally coupled at 01:48. Intermittence
   suggests a flaky guard, and a flaky guard will flake on the clone
   too.

3. The cross-check's inputs are not in the repo, and the spec glosses
   over it. VERIFIED: ledger-cross-check.py reads verdict files from
   ~/workspace/rung3-verdicts/ ("VM-local, never committed") and the
   order file rung3-run-log/thu-tu-chay.txt. A clean clone of
   todolist-push contains neither the verdict files nor (necessarily)
   the current order file state. Council B says "copy the ledger and
   verdict files read-only" in one clause, but the concrete next
   action only specifies cloning and copying "the ledger and verdict
   files" without naming the verdict-dir path, the order file, or
   what happens when the copy is taken mid-write by a scorer. The
   torn-copy mitigation ("fails validation loudly") is asserted, not
   shown: a torn JSONL copy fails, but a copy taken between a verdict
   file write and its ledger row write produces a mismatch that looks
   like ledger corruption, not a torn copy. That false alarm class is
   the R1 disease in a new organ.

4. Over-engineering risk for a closed run is real but bounded; the
   bigger risk is building it and never running it. Council A
   disables the hourly watch (Item 7.1). Council B's script then has
   no schedule and no owner. A validation script that runs once to
   "seal the record" and is never invoked again is ceremony. The
   decision must name who runs it, when, in the next run - or admit
   it is a manual tool and stop calling it a posture.

### Cheaper alternatives

- Run the existing validators from the VM landing clone that already
  exists (~/frontend-agent-kit/repo pattern per AGENTS.md 2026-11-12
  lesson: fresh clone, gh-authenticated, push-verified). No new
  clone machinery; copy ledger + verdicts there.
- Copy the two validator files (stdlib-only Python, VERIFIED: both
  import only json/os/re/sys) to a scratch dir outside the worktree
  and run them there against read-only copies. Smaller than a full
  clone; same decoupling. Ponytail prefers this.
- Before building anything: capture one actual guard block message
  (run the watch once, read the log). One hour of evidence replaces
  the ASSUMED root cause.

### Amendments required

B1. Pin to the CURRENT todolist-push head at validation time (record
    the SHA in the log), not frozen-heads.txt. If a frozen validator
    version is ever wanted, freeze validators explicitly in their own
    file. Strike the frozen-heads.txt mitigation as written.
B2. Name every input the cross-check needs (ledger, verdict dir,
    order file) with source paths, and copy them as one snapshot
    (copy verdict dir first, ledger last, or accept and document the
    mismatch window). Test must include the between-writes case.
B3. Capture the guard's real block reason first (one blocked-run log
    line). If the guard is workspace-wide, the scratch location must
    be outside ~/workspace or the posture needs a different fix.
B4. Name the runner and cadence for future runs (which watch or which
    coordinator step invokes the script). Reconcile with Item 7.1:
    if the hourly watch dies, this script's invocation point must be
    written into the next run's coordinator checklist now.

---

## Item 3 (R10) - Staged flag-fix-or-build for Cloudflare (Council B)

Verdict: SUSTAIN WITH AMENDMENTS. Stage 1 is right. The Stage 2 build
trigger as written pre-authorizes an arms-race tool with no owner, no
budget, and an open-ended scope. Do not let "build if inseparable"
become a blank cheque.

### Strongest objections

1. Stage 1 is likely to spend days proving a known Firefox behaviour,
   and Council B never mentions the cheapest knob. In Firefox-based
   browsers, navigator.webdriver is true when the browser is driven
   by automation (Marionette / WebDriver BiDi remote). That the flag
   is "tied to the automation endpoint" (Council B ASSUMED) is the
   expected architecture, not a surprise awaiting discovery. Worse,
   Council B's Stage 1 plan (read launcher, list flags, launch with
   and without each) omits the preference layer entirely: Firefox has
   historically exposed dom.webdriver.enabled as a pref. Redteam
   could not verify from the files read whether Zen 1.24.3b honours
   it (UNVERIFIED - no pref dump in evidence), but a Stage 1 that
   does not check about:config / prefs.js before concluding
   "inseparable" has not done the cheap test. If the pref works, the
   whole build evaporates. If it does not, Stage 1 should say so with
   evidence.

2. The probe already disagrees with itself, and the shim is visibly
   detectable in the team's own logs. VERIFIED: probe-baseline log
   shows webdriver true with get_tostring "function webdriver() {
   [native code] }"; shimmed logs show webdriver false but
   get_tostring "function () { [native code] }" (drive-attempt2.log,
   holder-attempt2.log). The shim changes the getter's toString - a
   fingerprint in itself. Council B cites the R3-100 disagreement
   (webdriver true via zen_dom eval vs probe-clean false elsewhere)
   as VERIFIED via council2. So the "unified probe" Stage 1 must
   deliver is not a formality: today there are at least two eval
   paths giving different answers and a shim whose presence is
   detectable by toString inspection. A build scoped as "fix exactly
   what the probe measures" inherits every blind spot of a probe that
   has already proven it can miss. Cloudflare does not limit itself
   to what our probe measures.

3. The build scope is open-ended evasion with a fig leaf. "Plus any
   further page-visible signals that the unified probe proves are
   leaking (the probe defines the list)" means the tool's scope grows
   every time the probe grows, with no new decision. The does-not-do
   list (no CAPTCHA solving, no IP spoofing) is good, but the
   does-do list has no ceiling: webdriver today, then plugins,
   languages, WebGL, canvas, fonts... each "proven leaking" by an
   expanded probe. That is the definition of scope creep into
   bot-challenge defeat, one reasonable step at a time. The owner's
   criterion was "human browsing not blocked + agent control at any
   time + AI-optimized Zen." It was not "win the fingerprinting arms
   race indefinitely."

4. Nobody owns maintenance, and Zen updates will break it. Council B
   is honest ("expect periodic small fixes; budget them as
   machine-layer upkeep") but names no owner, no cadence, and no kill
   criteria. When the probe goes dirty at 03:00 during a future run,
   who fixes the layer? The same team that took until 27/11 to
   integrate the residue? A fingerprint layer on the owner's DAILY
   browser that silently rots is worse than the current honest state
   (dirty probe = stop for agents; human sees a challenge and knows
   why). The proposal also puts the active config on the machine
   layer with repo opt-in default off. Standing principle check:
   "repo must work on stock apps" - an opt-in script that is only
   ever exercised on one machine, with one Zen version (1.24.3b
   pinned), will rot in the repo untested. Opt-in default-off plus
   no CI exercising it equals dead code with a README. Council B
   claims this "matches the standing design principle exactly"; it
   matches the letter (default off) while violating the spirit (repo
   tooling that works).

5. Cheaper routes were rejected too fast. Council B rejects the
   browser split because it "breaks owner-session continuity." But
   Zen supports multiple profiles/workspaces in one install, and the
   team already lives in workspaces (ws2/ws3 discipline VERIFIED in
   cron bodies). A human profile launched WITHOUT automation flags
   (clean by construction, no shim, no arms race) plus an agent
   profile with flags, both in the same Zen install, satisfies leg 1
   perfectly and leg 2 for agent tasks that do not need owner
   sessions. The hard case - agent task needing the owner's logged-in
   session - is real but rarer than "any time" suggests; for those,
   a boundary restart of the human profile with flags (Item 4
   procedure) is the honest cost. Council B treats "at any time, same
   session, zero friction" as absolute; the owner's criterion says
   agents "can still be called" to use computer-use on Zen - it does
   not say with zero setup cost. Similarly unexamined: Marionette-off-
   when-human (launch clean; when an agent is called, restart with
   flags at a boundary). Both routes cost a restart sometimes; the
   build costs maintenance forever. Council B priced the build in
   "days" and never priced the alternatives at all.

6. The acceptance test cannot prove the criterion. "Browse to a
   Cloudflare-protected site, confirm no block" - one site, one
   visit, one IP reputation state. Cloudflare challenges are
   probabilistic and history-dependent (Council B concedes this in
   its ASSUMED block). A single pass proves the probe is clean; it
   does not prove "human browsing unblocked" as a durable property.
   The decision should define acceptance as probe-clean PLUS N
   successful human-path visits across M distinct protected sites
   over D days, or admit the criterion is only ever partially
   verifiable.

### Cheaper alternatives (ranked)

- Pref check first: dom.webdriver.enabled=false (and related prefs)
  in the human profile. One throwaway-profile test. If it holds,
  done, no build.
- Two profiles, one install: human profile flag-free; agent profile
  flagged. Session-continuity cost paid only on owner-session tasks.
- Boundary-restart model: Zen launches clean; agent call triggers
  Item 4 boundary procedure to relaunch with automation flags; human
  browsing after the task relaunches clean. Friction, but zero
  fingerprint code.
- Keep Chromium as the Cloudflare-site browser (already the de facto
  workaround) and scope Zen agent work to non-Cloudflare sites until
  a flag/pref fix lands. Admits a limitation instead of building
  evasion.

### Amendments required

C1. Stage 1 must include the pref layer (prefs.js / about:config dump,
    dom.webdriver.enabled test in throwaway profile) and a timebox
    (e.g. 2 working days) with a written report either way. "Inseparable"
    may only be concluded after flag AND pref routes fail with
    evidence.
C2. The Stage 2 build trigger must NOT be pre-authorized by this
    decision. Stage 1 report returns to the team for a fresh build
    decision with: named maintenance owner, estimated build cost,
    probe coverage list frozen at decision time, and kill criteria
    (e.g. two consecutive Zen updates breaking the layer = retire to
    profile-split fallback).
C3. Freeze the tool scope at decision time to the signals the unified
    probe measures THAT DAY. Any new signal class needs a new
    decision. The probe itself must check getter toString and at
    least one non-webdriver signal, or the decision must state plainly
    that the probe only certifies webdriver.
C4. Price the two-profile and boundary-restart alternatives in the
    Stage 1 report with the same rigor as the build, including how
    often agent tasks actually needed owner-session continuity during
    R3-L3 (count from drive reports).
C5. Acceptance redefined: probe-clean is necessary, not sufficient.
    Require repeated human-path visits to multiple protected sites
    before declaring the criterion met, and keep recording actual
    block outcomes separately forever (already planned - keep it).

---

## Item 4 (R16) - No autonomous browser restart authority (Council B)

Verdict: SUSTAIN WITH AMENDMENTS. Refusing kill-power to watches is
correct. The alert-plus-procedure as specified would not have caught
the one death that actually happened, and the threshold is invented.

### Strongest objections

1. The 8 GB threshold is a round number in search of evidence.
   VERIFIED: the zen-laptop-health cron body alerts at "Zen RSS over
   8 GB." Council B marks ASSUMED that 8 GB "gives enough lead time."
   Redteam found no exhaustion measurement behind 8 GB. The one
   capacity data point in the files (~/memory/2026-11-25.md G-27:
   RAM avail 22567 MB, Zen RSS 1835 MB, "headroom to 8 GB threshold
   6357 MB") shows the threshold was chosen before any growth data
   existed. Observed RSS values in health logs: 0.65 GB to 4.52 GB
   across 25-27/11, one excursion to about 8.11 GB (council2 via
   coordinator notes, UNVERIFIED by redteam directly). A threshold
   nobody has calibrated against actual OOM or swap behaviour is a
   guess wearing a number.

2. The death that actually happened was not a memory death, and the
   alert would not have fired. VERIFIED (~/memory/2026-11-27.md
   lines 81, 98, 115): Zen PID 578117 alive 04:12:31, gone by
   04:13:52; last RSS 3.79 GB at 03:57, far under 8 GB; cause per
   line 115: the Task 56 runner restarted Zen around 04:12 to place
   tabs via sessionstore edit (folder placement has no API). So the
   04:12 death was an agent-initiated restart for tooling reasons,
   not exhaustion. Council B cites this death as evidence for the
   procedure ("the health watch did not restart it, by design")
   without noting the cause. The real lesson of 04:12 is different:
   agents already restart Zen when tooling forces them to, outside
   any procedure. A boundary procedure that only governs memory
   restarts leaves the actual restart path (sessionstore surgery)
   ungoverned.

3. Growth-rate math defeats a 15-minute alert cadence. Council B
   cites worst growth about 4.8 GB/h (council2 Rank 17, UNVERIFIED
   by redteam; the 25/11 log shows +1.34 GB in 16 min, about 5 GB/h,
   VERIFIED at ~/memory/2026-11-25.md line 1273 - consistent). At
   5 GB/h, RSS moves about 1.25 GB between 15-minute checks. From
   7 GB (no alert) to 11+ GB (possible OOM territory, unknown) is
   two checks. If no coordinator is awake - the normal state at
   04:00, which is when things die - the alert lands in a chat nobody
   reads until morning, and the owner opens a dead or swapped-out
   browser. Council B accepts this ("waits is safer than restarts
   wrongly") but never prices the owner's morning: lost session,
   lost tabs, R6-class damage by OOM instead of by watch.

4. Council B conflates two different powers: killing a live browser
   vs reviving a dead one. The R6 horror story (24 tabs closed) was
   automation acting on a LIVE session. Restarting a browser that is
   already dead (no PID, ports down) destroys nothing that is not
   already destroyed, and session restore is then pure upside. The
   proposal bans both under "no autonomous restart authority." The
   04:12-04:27 window (VERIFIED: dead 13+ minutes until a fresh
   process appeared at 1.40 GB, restarter unknown) is exactly the
   revive-dead case. A watch allowed to relaunch ONLY when Zen is
   verifiably dead (no process, both ports down, two consecutive
   checks) has a completely different risk profile from a watch
   allowed to kill a live 8 GB browser. Council B never separates
   them.

5. The procedure depends on restore tooling that is known-broken.
   VERIFIED (council1 Rank 22 via daily note; review R20): session-
   store decoder missing on the laptop (lz4 module absent). The
   checklist says "record open tabs before restart... verify owner
   essentials present after." Record HOW, if the decoder cannot read
   the session store? Via BiDi tab list (possible) - but the
   procedure as written does not specify the mechanism, and the
   throwaway-profile drill is the only safeguard. R20 (decoder
   presence) is deferred in the review with no owner date. The
   procedure should not be declared ready until the drill passes on
   the real mechanism, and R20 should be pulled forward as its
   prerequisite, not left deferred.

### Cheaper alternatives

- Revive-dead-only authority: watch may relaunch Zen iff no Zen
  process exists AND ports 9222/2828 are down on two consecutive
  checks; never kill a live process. Log every revive. This covers
  the observed failure (04:12) at near-zero session risk.
- Tab-count circuit breaker instead of RSS: tab cleanup cut about
  3.5 GB (VERIFIED via council1 citation). A coordinator rule "at N
  tabs, run R6 allowlist cleanup at next boundary" attacks the cause
  (accumulation) rather than the symptom (RSS), using machinery that
  already exists.
- Rate-of-growth alert (GB/h over last hour) in addition to absolute
  threshold; catches the 5 GB/h case two checks earlier.

### Amendments required

D1. Split the authority question: kill-live stays banned for watches
    (sustain); revive-dead (no process + ports down, two checks) is
    decided explicitly - redteam recommends allowing it with logging,
    but either way the decision must address it, not bury it.
D2. Calibrate or label the threshold: record RSS + system memory
    headroom at every boundary for the next run and set the alert
    from data; until then, write "8 GB (uncalibrated placeholder)"
    in the procedure so nobody mistakes it for a measured limit.
    Add a growth-rate alert line to the health watch.
D3. Extend the procedure to cover agent-initiated restarts for
    tooling reasons (sessionstore surgery): same record-before /
    verify-after checklist, same R6 guardrail, whoever initiates.
    The 04:12 restart is the precedent; govern it.
D4. Make R20 (session-store decoder on laptop) a prerequisite of the
    procedure's "ready" state, and specify the tab-record mechanism
    (BiDi list dump to a file) in the procedure text.
D5. Name the alert's human: who is expected to act on an RSS alert at
    04:00, and what happens if nobody does (accepted outcome stated
    plainly). An alert with no actor is a log line.

---

## Item 5 (R22) - Narrow PII sign-off class beside the scanner (Council B)

Verdict: KILL. Do not loosen. This is the one proposal redteam says
the team should reject outright, not amend.

### Strongest objections

1. The URL is the personal-data risk, and Council B concedes the
   mechanism while dismissing it. A docs/drive URL is a capability:
   anyone holding it can open the live document. The snapshot stores
   the URL string; pushing the snapshot to GitHub publishes the
   capability. Council B's mitigation - "the snapshot stores the URL
   string, not live doc content, so later edits do not retroactively
   leak through the snapshot" - is backwards. Later edits leak
   through the URL, which is now public. A task-created doc that is
   empty at seal time can be edited next week (by the task's own
   follow-up, by a collaborator, by the owner reusing the doc) to
   contain names, emails, or real content, and every reader of the
   pushed snapshot can open it. The scanner's owner-url rule
   (VERIFIED in pii-scan.py: OWNER_HOSTS includes "docs.", "drive.",
   "mail.", "calendar.", "notion.so") exists precisely because these
   hosts serve capability URLs. Signing off one URL at a time does
   not change what a URL is.

2. "Task-created" is self-attested by the party being checked.
   Eligibility evidence is "evidenced in the drive report" - a file
   written by the runner whose snapshot is being gated. The review
   records that evidence fabrication recurred on 25/11 (VERIFIED:
   review, Error tracker recount, "A7/A8 still live (fabrication
   recurred 25/11)"). A runner that fabricates evidence can fabricate
   provenance: label an owner doc "task-created" in the drive report,
   get a coordinator sign-off, push the owner's live doc URL to
   GitHub. Council B's guard ("coordinator must differ from the
   runner") checks WHO signs, not WHAT is true. Nothing in the class
   requires independent proof of creation (e.g. doc creation
   timestamp inside the task window, creation event in a log the
   runner cannot write). As specified, the class is a labelling
   exercise.

3. It violates the deterministic-block standing rule in spirit, and
   the spirit is the point. Standing rule (VERIFIED: MEMORY.md,
   2026-11-23): "personal-info leaks must be blocked by a
   deterministic pre-commit hook or CI check, not by prompt-only
   rules; a prompt alone does not stop an agent committing personal
   info." Council B keeps the scanner code unchanged and adds a human
   override beside it. Functionally that is: deterministic block,
   unless a coordinator says otherwise, per URL, under deadline
   pressure, with the decision recorded in a manifest the same team
   writes. The rule's entire purpose was to remove human/agent
   discretion from the leak path after discretion failed. A sign-off
   class reintroduces discretion at exactly the point of maximum
   pressure (snapshot sealing, run closing, everyone tired). Calling
   it "auditable" does not fix it: audit happens after the push, and
   a pushed URL cannot be un-pushed from clones and forks.

4. The rubber stamp is not hypothetical; it already happened three
   times. VERIFIED (council2 Rank 21 as cited by Council B): "manual
   review passed three more hits on task-created doc URLs and
   demo-store routes; no leak occurred." Three ad-hoc passes during
   one run, under time pressure, with no recorded sign-off fields,
   is the base rate. Council B proposes to formalize the practice
   that already occurred informally - which means the class will be
   used at the same rate, with better paperwork. "No leak occurred"
   is also unverifiable as stated: nobody can prove a negative about
   who opened a pushed URL. The correct reading of the three passes
   is that the gate was overridden three times without incident
   DETECTED, which is how every leak class starts.

5. The benefit does not justify any of this. What does pushing the
   raw URL buy? Evidence completeness: a future reader can click
   through to the doc. But the snapshot already contains screenshots
   and result files proving the task outcome (that is the snapshot
   system's purpose, VERIFIED across R3-L3 practice). The URL adds a
   live link to a doc whose content may drift from what the task
   produced - arguably WORSE evidence than the frozen screenshot,
   because the doc can change after sealing. Council B never states
   what breaks if these URLs are simply redacted. Answer: nothing
   breaks. Two snapshots already held out raw logs (R3-067, R3-072)
   and the run closed fine.

### Cheaper / safer alternatives (all preserve the deterministic block)

- Redact to host + path hash: snapshot stores
  "docs.google.com/<sha256-of-url>" plus the drive report's claim.
  Evidence chain keeps a verifiable fingerprint; no capability leaks.
  Scanner passes with NO rule change if the redaction happens before
  scanning (runner-side), or the scanner gains a deterministic
  redaction-aware pattern - code change, still deterministic, no
  human override.
- VM-local URL store: keep raw URLs in ~/workspace/rung3-verdicts/
  (already the never-committed store, VERIFIED in
  ledger-cross-check.py header). Snapshot references the store entry
  by hash. Anyone with VM access can resolve; GitHub never sees it.
- Screenshot-only evidence for doc tasks: the doc's rendered content
  at seal time is the evidence; the URL is dropped entirely. Matches
  how every other task type already proves outcomes.

### What KILL means concretely

- No sign-off class. No per-URL override. Scanner stays the sole
  gate, exit 1 means no push, full stop.
- The three already-passed manual-review cases: do NOT retroactively
  bless them with sign-off paperwork (Council B's next action).
  Instead, check whether those URLs are in pushed snapshots today;
  if yes, treat as potential exposure: record in the master event
  log, and if any doc is owner-owned or editable, rotate/share-
  restrict it. Retroactive logging of a possible leak as if it were
  an approved exception is the worst of both worlds.
- If evidence completeness genuinely suffers, adopt the host+hash
  redaction as a RUNNER-side step (before snapshot sealing), tested
  deterministically. That is a tooling change, not a loosening.

Redteam note: Council B did the conservative thing on high-entropy
(no override ever) and deserves credit for refusing that half. The
owner-url half fails for the same structural reason the high-entropy
half was refused: a human glancing at a string cannot certify what
the string unlocks.

---

## Item 6 (R15) - Instrument now, supervision unchanged (Council B)

Verdict: SUSTAIN WITH AMENDMENTS. Instrumentation is correct and
overdue. As written it defers the actual decision to a trigger that
may never fire, ignores the supervision layer that already exists
outside the VM, and keeps a dead route (service manager) on life
support.

### Strongest objections

1. If the cause is VM replacement, the instrumentation captures
   nothing and the trigger never fires. An exit handler in daemon.py
   runs when the process exits gracefully or on a catchable signal.
   A VM replacement kills the whole machine: no exit line, no
   heartbeat gap explanation, just silence then a fresh start.
   VERIFIED: supervisor.sh header itself records "a VM replacement
   kills both" and co-deaths include the 26/11 VM replacement
   (council1 Rank 17). Council B's trigger - "at least two deaths
   with named causes, or seven days of heartbeat data" - then reduces
   to the 7-day arm, which produces heartbeat data saying "everything
   was fine, then everything stopped, then everything restarted."
   That is not a named cause; it is the current state of knowledge
   with timestamps. The proposal never says what decision follows
   from "7 days, zero named causes." Defer-forever with extra steps.

2. The service-manager route is already dead; Council B keeps it
   alive as a future verification step. Redteam probed the VM:
   systemctl exists at /usr/bin/systemctl but `systemctl --user`
   fails with "Failed to connect to bus: No medium found" and
   /run/user/1000/bus does not exist (VERIFIED 27/11). supervisor.sh
   header (VERIFIED) records no cron daemon and no user systemd bus.
   Council B proposes to "verify read-only whether a user service
   manager exists" at the trigger point. It does not exist; that is
   verified NOW, in this redteam pass, for free. Carrying a dead
   option into the trigger-point decision wastes the decision meeting
   that the trigger is supposed to enable.

3. The cheaper supervision route already exists and is underweighted
   to the point of invisibility. The runtime (external scheduler)
   already runs cron jobs that survive VM replacement - every
   r3l3-* watch in Item 7 is one, and AGENTS.md records the
   watchdog-liveness-check runtime cron running --check-once every 5
   minutes as the fix for the attached-process liveness failure
   (VERIFIED: AGENTS.md 2026-11-19 lesson). Council B mentions "the
   runtime cron check-once pattern" once, as an alternative "to
   evaluate" later. But a runtime-cron supervisor is the ONLY layer
   that survives the co-death mode that actually occurs (VM
   replacement kills daemon + supervisor.sh together; the runtime
   scheduler is outside the VM). It also already partially exists:
   the zen-laptop-health runtime cron restarts the daemon today
   (VERIFIED cron body; VERIFIED restarts at 01:43, 03:42, 05:43 on
   27/11 in ~/memory/2026-11-27.md). Council B's "supervision
   unchanged" therefore misdescribes reality twice: supervision is
   already three-layered, and the outer layer is the one doing the
   observed rescues. The decision should formalize that, not defer
   it.

4. Instrumentation as specified can mask the race it should reveal.
   VERIFIED: daemon.out contains two "Address already in use"
   tracebacks (double-start attempts). Council B adds contention
   logging but keeps the supervisor loop "exactly as is" - including
   watchdog.py's restart-on-ping-failure with a 5s timeout. A daemon
   that is alive but slow to answer (loaded VM, SSH stall - the
   daemon's send path includes ssh_ms around 1.2s per VERIFIED
   daemon.log send entries) can fail a ping and get restarted while
   healthy, producing the double-start. Exit-reason logging will
   record "killed by restart" and the team will call it a named
   cause, when the cause is the supervisor itself. The proposal
   never considers supervisor-induced deaths as a hypothesis, even
   though the double-start evidence points at it.

5. No decision owner, no decision date. "Revisit when either trigger
   fires" - who watches for the trigger? The heartbeat data lands in
   watchdog.log, which nobody reads routinely (last entries 25/11,
   VERIFIED - because watchdog.py only logs on daemon-down). Adding
   heartbeat lines makes the log longer, not read. Without a named
   owner and a calendar date (e.g. "coordinator reviews on 04/12
   regardless"), the trigger is a hope. R15 has already been deferred
   once (review: DEFER, diagnosis first). This proposal is the second
   deferral wearing instrumentation as progress.

### Cheaper alternatives

- Formalize the runtime-cron outer supervisor NOW: one runtime cron
  (5 min) running a check-once that pings the daemon socket and
  restarts daemon + supervisor.sh detached if dead. This is a
  posture change, but a small one reusing the proven
  watchdog-liveness-check pattern, and it directly kills the
  co-death mode. Instrumentation proceeds in parallel for the
  inner-cause question.
- Correlate deaths with VM replacement records before instrumenting:
  daemon_start timestamps are already in daemon.log (46 starts,
  VERIFIED count). Cross-reference against known replacement times
  (runtime records / coordinator notes) - an afternoon of log
  archaeology may name half the causes with zero code change.
- Log supervisor-induced restarts distinctly: watchdog.py already
  logs daemon_down_restarting with timestamps (VERIFIED watchdog.log,
  entries 23/11 and 25/11). Compare those timestamps against
  daemon_start events to count how many "deaths" were watchdog
  restarts of a live-but-slow daemon. Zero new code.

### Amendments required

E1. Kill the service-manager option in this decision (verified
    unavailable on this VM). The trigger-point decision is between:
    runtime-cron outer supervisor (formalized) vs current three-layer
    accident. Do not spend the future meeting re-verifying a bus
    that does not exist.
E2. Add the log-archaeology step BEFORE code changes: correlate the
    46 daemon_start events with VM replacements and watchdog restart
    entries; publish the split (replacement / watchdog-induced /
    unexplained). If unexplained is small, instrumentation scope
    shrinks accordingly.
E3. Name the decision owner and a hard review date (trigger OR date,
    whichever first; date no later than 7 days after instrumentation
    lands). The review produces a supervision decision, not another
    instrumentation round.
E4. Instrumentation must distinguish "daemon died" from "daemon was
    restarted by watchdog/zen-health": every restart path logs its
    identity. Exit handler alone cannot do this; the restarters must
    log too (zen-laptop-health already logs restarts in its watch
    log - VERIFIED format line; watchdog.py logs restarts - VERIFIED;
    the missing piece is joining them in one place).
E5. State the VM-replacement blind spot in the decision: exit logging
    cannot capture machine death; heartbeat gaps correlated with
    replacement records are the evidence for that class. Do not let
    "no exit lines" be misread as "no deaths."

---

## Item 7 - Post-run watchdog cron disposition (Council A)

Verdict: SUSTAIN WITH AMENDMENTS (per-watch verdicts below). The
4-disable / 2-keep shape is right. Two disables collide with Item 1,
one keep is relabelling, and the ledger disable contradicts Item 2
(see cross-cutting note).

### 7.1 r3l3-ledger-push-watch - DISABLE after final validation

Verdict: SUSTAIN WITH AMENDMENTS.

Attack: What is lost? The 60-minute push-lag alert (VERIFIED cron
body step 3). Post-closure, if anyone writes a correction row and
forgets to push, nothing alerts - accepted by Council A, fine. The
real problem is the interaction with Item 2: Council A disables the
only scheduled validation while Council B adopts clean-checkout
validation as standing posture with no schedule. Net effect: the
posture exists on paper and runs never. Also, Council A's "parent
runs both validators once" before disabling - where? If in the
flagged worktree (the cron body's cwd, VERIFIED: "in
~/workspace/r3l3-run-wt"), the execution-risk guard may block the
final pass itself, and the team would be executing in-tree code as
its last act after deciding (Item 2) not to. If via clean checkout,
Item 2's script must exist first - sequencing Council A never states.

Amendments: (a) Final validation runs via Item 2's clean-checkout
method, after that script's test passes; order the two decisions.
(b) Strike "R19 stays open for the owner" (see cross-cutting note);
record R19 as decided by this meeting. (c) Write the manual
validation invocation into the coordinator checklist for future runs
(same as amendment B4).

### 7.2 r3l3-agents-watch - KEEP, repurposed; retire tab cleanup

Verdict: SUSTAIN WITH AMENDMENTS.

Attack: Is the repurpose real? The body (VERIFIED) is titled "R3-L3
agents watch," checks 4 agents, pokes after 15-min silence, does a
15-min screen look via grim screenshot over SSH, and step 6 does tab
cleanup. Removing step 6 and renaming scope text is an edit, not a
repurpose - the watch already IS a general fleet watch wearing an
R3-L3 title. That is fine, but call it what it is: keep, minus step
6. Two underpriced costs: (1) The screen look screenshots the owner's
laptop screen every 15 minutes forever, pulls it to the VM, and reads
it with vision. Post-run, with no run to supervise, that is standing
surveillance of the owner's daily machine justified by a run that
ended. Council A keeps it without re-arguing its post-run value.
(2) The poke logic: "silent for more than 15 minutes on a pending
message" pokes Clone2/Mei/Mochi. During Item 1, Clone2 will be doing
long independent review work; a poke at minute 16 of a 40-minute
review is an interruption the watch cannot distinguish from silence.
Council A notes this risk and waves at existing mitigations (one poke
per 15 min). One poke per 15 min during a 2-hour review is 8 pokes.

Amendments: (a) Re-argue the screen look post-run: either justify it
as general fleet supervision with owner-visible value, or drop it to
on-alert-only (screenshot when a CDP check is inconclusive, which the
body already supports as fallback). (b) Poke rule: only poke when a
task is recorded as assigned-and-awaiting (coordinator state), not on
any unanswered message; idle agents with no assignment are not
"silent," they are idle. (c) The final tab-cleanup sweep: Council A
says "after one final dry-run sweep confirms no recorded
completed-task tabs remain." A dry-run confirms the LIST, not the
close. If tabs remain, someone must close them (live action, R6
rules, pill visible) or explicitly accept them. State which.

### 7.3 r3l3-coordinator-liveness-watch - DISABLE

Verdict: SUSTAIN.

Attack (for completeness): Could it catch a future coordinator? No -
it reads R3-L3-specific files (VERIFIED cron body: state file,
heartbeat log, per-task reports under rung3-run-log/). It was still
alerting at 04:13 on 27/11 (VERIFIED ~/memory/2026-11-27.md line 79:
REPORTING CHAIN BROKEN, heartbeat stale 114 min) while the coordinator
was alive - the R1 false-alarm class in its final form. Left enabled
it alerts every 5 minutes forever. Disable is correct. One caveat:
disabling removes the only consumer of signal-hygiene.py's liveness
verdict; the helper stays in rung3-ci/ for future runs (Council A
says this). Fine.

### 7.4 r3l3-runner-process-watch - DISABLE

Verdict: SUSTAIN WITH AMENDMENTS - collides with Item 1.

Attack: Both checks are R3-L3-scoped (VERIFIED: tmux session
r3-fcc-runner-L3; codex exec vs state-file task_start). True. But
Item 1 (same council!) assigns FCC a solver lane starting TODAY.
Council A's mitigation: "its lane launches its own session under its
own brief, not this watch." So during Item 1, an FCC session runs on
the laptop with NO process watch: if it hangs mid-problem (its R3-037
behaviour was slowness, VERIFIED), nothing detects it except the
coordinator noticing silence. The left hand disables the FCC monitor
while the right hand assigns FCC exam problems. Either Item 1 does
not use FCC (redteam amendment A2), or 7.4's disable waits until
Item 1 closes, or Item 1's brief includes its own process check.
Pick one explicitly.

Amendment: sequence the disable after Item 1 completes, OR record in
Item 1's FCC brief a named process-check duty (coordinator checks
tmux pane at each problem boundary). Do not disable silently into an
active FCC assignment.

### 7.5 r3l3-timeout-watch - DISABLE

Verdict: SUSTAIN WITH AMENDMENTS - same collision, smaller.

Attack: Disabling removes the standing kill-by-PID capability pointed
at a stale state file - genuinely safer (Council A is right that this
is the wrong-kill class R1 fought). But Item 1's 45-minute per-problem
cap then has NO enforcer: it is a brief instruction to lanes that
have already demonstrated 30-minute-cap behaviour only under watch
pressure (R3-037 stopped at 29:59 because the deadline was real).
Unenforced caps are aspirations. Also note: the timeout watch's
completed-task guard (signal-hygiene.py) is the R1 integration's
showpiece; disabling the watch orphans the helper's timeout verdict
too (same caveat as 7.3, acceptable).

Amendment: Item 1 briefs must name who enforces the cap (coordinator
checks lane progress at 45 min and calls the stop), since no watch
will. Or keep the timeout watch alive, repointed at Item 1's state,
until Item 1 closes - heavier; redteam prefers the named-human
option, stated in the brief.

### 7.6 r3l3-zen-laptop-health - KEEP, repurposed

Verdict: SUSTAIN WITH AMENDMENTS.

Attack: This watch is load-bearing (only daemon restarter outside the
VM's own supervisor loop; VERIFIED restarts 01:43, 03:42, 05:43 on
27/11). Keeping it is right. But: (1) It conflicts with Item 6's
"supervision unchanged" framing - keeping 7.6 AS the daemon restarter
while Item 6 instruments "the supervisor" means two decisions about
one system were made in two documents that never reference each
other. The final decision must describe the three-layer reality and
say which layer is authoritative. (2) The repurpose removes the FCC
tmux check - same Item 1 collision as 7.4: during Item 1, nobody
checks the FCC session exists. (3) The version pin (Zen 1.24.3b,
VERIFIED cron body step 1) will false-alert the day the owner updates
Zen. Council A says "alert, not auto-fix, on mismatch" - but the body
as written alerts on "Zen down" class failures; a version mismatch
alert every 15 minutes until someone edits the body is alert spam
that trains everyone to ignore the watch. (4) The 8 GB RSS alert
inherits Item 4's uncalibrated threshold (see D2).

Amendments: (a) Final decision text names the three supervision
layers and this watch's role among them; Item 6's instrumentation
includes this watch's restart events (amendment E4). (b) Keep the FCC
tmux check until Item 1 closes, then remove (sequence with 7.4).
(c) Version check: alert ONCE per version change (state file
comparison), not every cycle; or downgrade to log-only. (d) RSS
threshold labelled uncalibrated until D2 data exists.

---

## Council claims redteam could not verify (UNVERIFIED list)

- Council A ASSUMED: Codeforces manager session logged in / contest
  735368 open on 27/11. No live check possible by redteam. (Item 1,
  objection 1.)
- Council A ASSUMED: Codeforces verdicts visible to manager account
  with submission IDs. Standard behaviour, unconfirmed for this
  group contest.
- Council B ASSUMED: execution-risk guard flags the worktree because
  of agent-written evidence. No block message in evidence read.
  (Item 2, objection 2.)
- Council B ASSUMED: 8 GB RSS threshold gives enough lead time.
  No calibration data found. (Item 4, objection 1.)
- Council B ASSUMED: Cloudflare blocks driven mainly by webdriver
  signal. Plausible, unproven; IP/behaviour share unknown. (Item 3.)
- Council B ASSUMED: task-created doc URLs contain no personal data
  beyond the doc ID. Cannot be verified for future edits; see Item 5
  objection 1.
- Council B ASSUMED: split of daemon deaths between VM replacements
  and other causes. Unknown; amendment E2 addresses it.
- Council B (via council2): Zen memory excursion to about 8.11 GB
  and restart cut 7950 MB to 978 MB. Cited from coordinator notes;
  redteam verified the surrounding health-log pattern but not these
  two numbers directly.
- Council B (via council2): worst memory growth about 4.8 GB/h.
  Redteam verified a consistent data point (+1.34 GB in 16 min,
  25/11 log) but not the 4.8 figure itself.
- Task brief claim "R3-037 was an FCC timeout": VERIFIED in substance
  (FCC lane, FAIL, 29 min 59 s at the 30-min cap, incomplete) from
  the grades ledger and scorer grade file.

## Verdict summary

| Item | Verdict |
|---|---|
| 1 Codeforces plan | SUSTAIN WITH AMENDMENTS (A1-A5) |
| 2 R19 clean checkout | SUSTAIN WITH AMENDMENTS (B1-B4) |
| 3 R10 staged flag/build | SUSTAIN WITH AMENDMENTS (C1-C5; build NOT pre-authorized) |
| 4 R16 no restart authority | SUSTAIN WITH AMENDMENTS (D1-D5) |
| 5 R22 PII sign-off class | KILL (no loosening; redact or VM-local instead) |
| 6 R15 instrument now | SUSTAIN WITH AMENDMENTS (E1-E5) |
| 7.1 ledger-push disable | SUSTAIN WITH AMENDMENTS |
| 7.2 agents-watch keep | SUSTAIN WITH AMENDMENTS |
| 7.3 coordinator-liveness disable | SUSTAIN |
| 7.4 runner-process disable | SUSTAIN WITH AMENDMENTS (sequence vs Item 1) |
| 7.5 timeout-watch disable | SUSTAIN WITH AMENDMENTS (name cap enforcer) |
| 7.6 zen-laptop-health keep | SUSTAIN WITH AMENDMENTS |

Net: 1 SUSTAIN, 10 SUSTAIN WITH AMENDMENTS, 1 KILL. No proposal
survives exactly as written except 7.3. The two structural fixes the
final decision document must make: reconcile the R19 contradiction
between Council A 7.1 and Council B Item 2, and describe daemon
supervision as the three-layer system it actually is (Items 6 + 7.6
together).

Standing rules observed by this redteam pass: decision task only, no
implementation; no personal info in this document beyond role names
already in the council files; every event chain logged to the master
event log by the coordinator on receipt (redteam does not write the
log directly from this brief - coordinator to log receipt of this
file with full chain).

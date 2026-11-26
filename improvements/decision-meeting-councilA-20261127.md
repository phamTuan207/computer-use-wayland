# Decision meeting - Council Member A proposals (27/11/2026)

Owner delegation 06:19 27/11/2026: team decides on its own. Council A
covers Item 1 (Codeforces task plan) and Item 7 (post-run watchdog cron
disposition). An independent redteam will attack these proposals next.
Decision task only: no Codeforces solving started, no cron changed, no
code edited by this document.

Standing rules applied to every plan below: Ponytail for code work
(smallest complete change, reuse first, no unrequested abstraction, one
small test for non-trivial logic, never cut validation/security);
Graphify for codebase context; keybind-first hard rule (keybind/command
over vision); test like a normal user for user-facing surfaces (enter via
search/homepage, click through, no deep-link or internal-setter proof);
never ydotool; full access for agents; no personal info on GitHub; never
close or navigate owner-opened tabs/windows; log every event with the
full chain (fail, reasoning, tried, decision, fix, result) to the master
event log via ~/workspace/agent-event-log/log-event.sh; opencode only
house models (opencode/ prefix, opencode/deepseek-v4.1-flash-free),
never NVIDIA/Groq/OpenRouter for opencode; never assume an agent's
capabilities, check or ask the agent directly; every brief states the
delivery path explicitly.

## Item 1 - Codeforces contest 735368 task plan

### Proposed decision

START NOW, today Fri 27/11/2026. Do not wait for a separate Zen check.
Run the first 6 problems as the required scope and finish them by end of
day 27/11 or morning 28/11 at the latest, leaving Sat 28/11 for Hieu to
fix any errors found and for one re-check pass. Attempt the last 4 only
if the first 6 are fully reported and time remains before the Sun
29/11/2026 exam.

Execution shape:

1. Browser extraction and submission lane (SSH-capable only): one Muse
   subagent with computer-use on the laptop Zen session acts as driver
   and coordinator for the contest. It opens Codeforces the normal-user
   way (homepage, then navigate to the group contest through visible UI,
   no direct deep-link proof), confirms manager access, extracts all 10
   statements with limits and samples into the repo, submits solutions
   one by one, and captures each verdict with submission evidence.
2. Solver lanes (parallel, SSH-capable): Codex lane and FCC lane each
   take 3 of the first 6 problems. Each writes a C++ solution, tests it
   locally against the statement samples plus self-made edge cases
   before any submission, and records time-to-solve and self-rated
   difficulty. Solutions are cross-checked: each lane reviews the other
   lane's 3 solutions before submission, following Hieu's check-each-
   other's-problems rule.
3. Independent review lane (repo/web only): Clone2 reads the extracted
   statements and both lanes' solutions from the repo, independently
   rates difficulty against the intended student level, and flags
   statement or test errors the solvers may have normalised away. Mei
   is second reviewer only if Clone2 flags a disagreement or capacity
   allows. Mochi and Clone1 are held in reserve and not assigned
   required problems.
4. Optional problems 7-10: only after the required-6 report is
   delivered. Same lanes, same verification, clearly labelled optional
   so they never delay the required report.

### Rationale

- The sequencing blocker is gone. The task was recorded as second-to-
  last, after R3-L3 closes and before the Polygon final test. R3-L3
  closed 04:49 27/11, so the precondition is met and no other run work
  competes for the Zen session or the solver lanes.
- The deadline forces an immediate start. Today is Fri 27/11 06:20 and
  the exam is Sun 29/11/2026. Hieu needs the error report early enough
  to fix problems and rebuild packages before the exam; a Sat start
  leaves no fix window. Starting today gives a full buffer day.
- The owner's pending "check Zen first" question was delegated away at
  06:19 ("tu hop tu quyet di"). The team therefore decides on evidence,
  not on a further owner check. Zen health is already covered by the
  zen-laptop-health watch (Item 7, kept), and the driver lane's first
  step is a live Zen/Codeforces access confirmation; if that fails, the
  plan stops and reports instead of guessing.
- Parallel solver lanes with cross-check match how this team already
  works on Codeforces/Polygon material (Hieu's workflow: each person
  checks the others' problems, never only their own) and give an
  independent difficulty signal instead of a single solver's opinion.
- Keeping Clone2/Mei/Mochi off the browser respects their hard
  constraint (no Tailscale/SSH, repo/web only) while still using them
  where they are strong: independent reading of statements and
  solutions once those are in the repo. Live browser and machine work
  stays with SSH-capable Muse subagents, Codex, and FCC.

### Evidence

- VERIFIED: R3-L3 closed 04:49 27/11 at Rule-A 52 PASS / 1 FAIL, bars
  50/52 and 51/53 both met. Source: r3-l3-fix-integration-review-
  20261127.md, opening paragraph.
- VERIFIED: Codeforces task origin and scope. Contest 735368, group
  EoMGcsRgKH, Hieu's 10 final-exam problems, first 6 required and last
  4 optional, owner is group manager with manager-only access, exam Sun
  29/11/2026, task re-ranked 17:10 26/11 to second-to-last (after
  R3-L3, before the Polygon final test). Source: ~/memory/2026-11-26.md
  lines 966-990 (Final task added 17:08 and Correction 17:10 entries).
- VERIFIED: team Codeforces/Polygon working method, including
  cross-checking each other's problems (Step 13), Polygon defaults
  (1000 ms / 256 MB, stdin/stdout), statement language English with
  Vietnamese content, checker std::lcmp.cpp, and per-category points
  (Nhan biet 15, Thong hieu 10, Van dung 5, VDC 5 per hidden test).
  Source: ~/workspace/cf26-upload/QUY-TRINH-UP-DE-POLYGON-CODEFORCES-
  2026-11-20.md.
- VERIFIED: the Polygon final test is a separate, later task (5
  problems uploaded by Muse alone to an independent contest on the
  owner's own nick, run LAST). Source: ~/workspace/cf26-upload/FINAL-
  TEST-PLAN-20261121.md. This confirms contest 735368 solving must not
  be conflated with uploading, and must finish first.
- VERIFIED: coordinator state file shows RUN CLOSED, all positions
  graded, Rule-A 52/1. Source: ~/workspace/r3l3-run-wt/rung3-run-log/
  r3-l3-coordinator-state.json (current_task field).
- VERIFIED: workload allocation 26/11 21:36 - Clone2 is main burner,
  Mei steady, Mochi and Clone1 reduced after reaching ~65% token use.
  Source: ~/MEMORY.md (2026-11-26 21:36 entry, injected context).
- ASSUMED: the owner's Codeforces manager session is still logged in
  in the laptop Zen profile and contest 735368 is still open for
  manager entry on 27/11. Not verified by Council A (no live browser
  access). The driver lane must confirm this as step 1 and stop with a
  report if access fails.
- ASSUMED: Codeforces submission verdicts (Accepted / Wrong Answer /
  Time Limit Exceeded etc.) are visible to the manager account after
  submission and can be captured as evidence. Standard Codeforces
  behaviour, but unconfirmed for this group contest until the driver
  lane runs.
- ASSUMED: problem statements are in Vietnamese (content) with English
  statement language, per Hieu's Polygon rule. Solvers must read the
  extracted statements as-is and not assume English text.

### How submissions and verdicts are verified

- Local first: each solution compiles clean and passes all statement
  samples plus at least 2 self-made edge cases (empty/minimal input,
  maximal constraints smoke test) before submission. Local test output
  is saved with the solution in the repo.
- One submission per problem per lane version; no resubmission spam.
  If a verdict is not Accepted, the lane records the exact verdict,
  fixes only with a stated hypothesis (statement ambiguity vs solution
  bug vs test error), and resubmits once. A second non-Accepted verdict
  stops that problem and escalates to the coordinator with evidence,
  instead of burning submissions.
- Verdict evidence: Codeforces verdict text plus submission ID (or
  timestamp + problem code if no ID is shown), captured by DOM/CLI
  first and screenshot only as cross-check, per the observation rule.
  Evidence files land in the repo next to the solution. No verdict is
  reported from memory.
- Normal-user path: the driver enters Codeforces via homepage/search
  and clicks through to the contest and submit pages. No API or
  deep-link submission counts as verification. Keybind/command actions
  are preferred over vision throughout; vision is cross-check only.
- The driver never closes or navigates owner-opened tabs. Contest work
  happens in new tabs beside the owner's session.

### How difficulty is assessed

AI solve time alone does not measure student difficulty, so three
signals are combined per problem:

1. Solver self-rating (easy / medium / hard for a CF26 final-exam
   student) with the key insight named in one sentence and the main
   trap or edge case named.
2. Cross-check rating from the other solver lane, written before seeing
   the first lane's rating.
3. Independent Clone2 rating from statements + solutions only, mapped
   to Hieu's categories (Nhan biet / Thong hieu / Van dung / VDC).

Where the three disagree by more than one level, the coordinator
records the disagreement explicitly and gives a final calibrated
verdict with reasoning, rather than averaging silently. Each problem
also gets an error checklist: statement clarity, sample correctness,
constraint/limit sanity (against 1000 ms / 256 MB defaults), edge-case
coverage, and checker suitability. Errors are severity-rated:
BLOCKING (wrong samples, ambiguous statement, broken tests - must fix
before exam), MINOR (typo, unclear phrasing - fix if time), NONE.

### Report format

One markdown report committed to todolist-push (delivery path stated in
every brief; coordinator owns the push, Council A does not push):

- Header: contest, date, lanes, scope (required 6 / optional 4).
- Summary table: problem code | verdict | difficulty (intended vs
  assessed) | errors found (severity) | action for Hieu.
- Per-problem section: statement summary, solution approach in 2-3
  lines, local test result, Codeforces verdict + evidence reference,
  difficulty reasoning (3 signals + final), error details with exact
  quotes or test inputs where relevant.
- Closing: prioritised fix list for Hieu ordered by severity, and an
  explicit statement of what was NOT checked (e.g. optional problems
  not attempted, hidden-test strength beyond submission verdicts).

A short summary of the same report goes to the owner in chat. No
personal info (names beyond problem-setter attribution already in the
contest, accounts, credentials) goes into the repo report. Every step
is logged to the master event log with the full chain.

### Risks

- Access risk: manager-only contest. If the Zen session is logged out
  or the contest is closed, extraction fails. Mitigation: driver
  confirms access first; on failure, stop and report to parent with
  the exact screen state. Never ask the owner for a password; sign-in
  follows the standing Google-chooser rule via a browser-capable agent.
- Account pollution: submissions go under the owner's manager nick and
  may be visible in the contest. Mitigation: coordinator confirms with
  the parent before first submission whether manager submissions are
  acceptable as-is (expected, since Hieu asked the team to try the
  problems), and the report lists every submission made.
- Difficulty miscalibration: AI lanes solve faster than students.
  Mitigation: three-signal assessment above, calibrated to CF26
  student level, disagreements surfaced not hidden.
- Time overrun: a hard problem eats the buffer day. Mitigation:
  per-problem soft cap of 45 minutes per lane; on cap, record partial
  progress and move on, returning only after all 6 have a first pass.
- Browser requirement (explicit): Council A cannot operate a live
  browser and did not visit the contest page. The parent must delegate
  the extraction/submission lane to a browser-capable, SSH-capable
  agent (Muse subagent with computer-use on laptop Zen, or Codex/FCC
  lane driving Zen). Clone1/Clone2/Mei/Mochi must not be assigned any
  browser or submission step.

### Concrete next actions

1. Parent/coordinator: spawn the driver lane (SSH-capable Muse
   subagent) with a brief stating delivery path (statements + evidence
   to todolist-push under a cf735368 folder), keybind-first and
   normal-user entry rules, never-close-owner-tabs rule, and stop-and-
   report on access failure. First deliverable: access confirmation +
   10 extracted statements.
2. Coordinator: brief Codex lane (problems 1-3) and FCC lane (problems
   4-6) in parallel once statements land. Each brief states: Ponytail
   (smallest complete C++ solution, no unrequested abstraction), local
   sample+edge testing before submission, cross-check duty, difficulty
   self-rating format, delivery path (solution + test log to repo).
   Confirm each lane's actual capabilities by asking the lane, never
   assume.
3. Coordinator: brief Clone2 as independent reviewer (repo-only) with
   the difficulty-mapping rubric. Mei on standby for disagreements.
   Mochi/Clone1: no required assignment.
4. Driver lane: submit cross-checked solutions, capture verdicts,
   commit evidence. Coordinator assembles the report, pushes, logs
   events, and summarises to the owner. Optional problems 7-10 start
   only on coordinator release after the required-6 report is out.

## Item 7 - Post-run watchdog cron disposition (6 watches)

Context: R3-L3 is closed, so watches that only observe run files will
either spam stale alerts or log "nothing running" forever. Watches
that guard live infrastructure (Zen, laptop, speed-daemon, agent
PWAs) still have value beyond the run. Disabling is executed by the
parent after this meeting; Council A only decides. Cron bodies were
read from ~/workspace/goals/zen-i-u-khi-n-c-t-i-a-b-i-agent-v-muse/
crons/.

### 7.1 r3l3-ledger-push-watch (hourly)

- Proposed decision: DISABLE the hourly schedule after one final
  validation pass. Do not change the validation posture itself.
- Rationale: the ledger is final (run closed, final tip verified in
  the integration log). Hourly re-validation of a static file produces
  only log noise. The underlying scripts (validate-ledger.py,
  ledger-cross-check.py) stay in the repo for on-demand use. Crucially,
  the review lists R19 (ledger-push watch posture: approving
  validators in the flagged worktree vs moving validation to a clean
  checkout) as an OWNER DECISION the team must not decide. Disabling
  the schedule preserves the current posture without deciding R19;
  re-enabling later under either posture remains the owner's call.
- Evidence: VERIFIED - cron body runs validate + cross-check + 60-min
  push-lag alert hourly (crons/hourly/r3l3-ledger-push-watch__
  interval@1h.md). VERIFIED - R19 is owner-decision item 1 (review,
  Owner-decision items). VERIFIED - integration log final tip
  914ad171, ls-remote verified (review, Integration log). ASSUMED - no
  further ledger rows will be written post-closure; if a correction
  row is ever needed, validation can be run manually before push.
- Risks: a silent post-closure ledger edit would go unvalidated until
  someone runs the scripts manually. Accepted: coordinator owns pushes
  and the final state is already pushed and verified.
- Next action: parent runs both validators once, confirms exit 0 and
  zero unpushed rows, logs the result, then disables the cron. R19
  posture question stays open for the owner, untouched.

### 7.2 r3l3-agents-watch (15 min, all 4 agents)

- Proposed decision: KEEP, REPURPOSED as the general agent-fleet
  watch. Keep agent liveness/poke logic and the 15-min screen look.
  Retire the R3-L3 tab-cleanup step (step 6) after one final dry-run
  sweep confirms no recorded completed-task tabs remain unclosed.
- Rationale: Clone1, Clone2, Mei, and Mochi are live infrastructure
  used well beyond R3-L3 (including the Item 1 review lane), and this
  watch is the only thing checking their PWAs, poking silent agents
  after 15 min, and looking at the actual screen. That value does not
  end with the run. The tab-cleanup step, however, is defined purely
  by R3-L3 completed-task records; with the run closed its allowlist
  can never grow, so it becomes a permanent no-op that still carries
  close-risk if misread. The R6 guardrail (allowlist, dry-run list,
  pinned/essential never matched) makes one final sweep safe.
- Evidence: VERIFIED - cron body checks all 4 agents via CDP/daemon,
  pokes Clone2/Mei/Mochi after 15-min silence, does a 15-min screen
  look, and step 6 tab cleanup is allowlist-only from graded-task
  records (crons/minutely/r3l3-agents-watch__interval@15m.md).
  VERIFIED - R6 guardrail integrated 27/11 (review, Integration log).
  VERIFIED - Clone1 is observation-only in this watch (few tokens
  left), consistent with the 26/11 workload cut. ASSUMED - agent PWAs
  and CDP ports (9223/9224) remain the access path for the fleet
  after R3-L3.
- Risks: keeping the watch keeps its poke behaviour; a poke during a
  long legitimate task could interrupt. Mitigated by existing rules
  (one poke per 15 min, never poke Clone1, never poke while read path
  broken). Screen look keeps taking screenshots every 15 min; that is
  read-only by rule (never switch, click, navigate, or close).
- Next action: parent edits the cron body to remove step 6 (after the
  final dry-run sweep is logged) and renames the scope in the body
  text from R3-L3 to general fleet watch. Schedule stays 15 min.
  Log the change with full chain.

### 7.3 r3l3-coordinator-liveness-watch (5 min)

- Proposed decision: DISABLE.
- Rationale: this watch exists only to detect a dead R3-L3
  coordinator via heartbeat and per-task report freshness. The
  coordinator's work ended at run closure; the heartbeat log already
  stopped at 02:18:50 27/11 while coordinators worked to 04:48 (the
  R1 false-alarm evidence). Left enabled, it will fire "no heartbeat"
  and "reporting chain broken" alerts every 5 minutes forever against
  files that will never change again. There is no general-purpose
  repurpose: no other coordinator writes those files.
- Evidence: VERIFIED - cron body alerts on heartbeat older than 15 min
  and report+heartbeat staleness, with R1 deadline suppression
  (crons/minutely/r3l3-coordinator-liveness-watch__interval@5m.md).
  VERIFIED - heartbeat stopped 02:18:50 27/11, liveness false alarms
  ~2.5h (review, Key evidence R1). VERIFIED - state file shows RUN
  CLOSED (r3-l3-coordinator-state.json). ASSUMED - no successor run
  reuses these exact state/heartbeat files without a fresh watch
  design.
- Risks: none material. If a future run reuses the pattern, R1's
  signal-hygiene helper and this body are the starting point for a
  new watch, created fresh for that run.
- Next action: parent disables the cron. No final pass needed beyond
  confirming the state file reads RUN CLOSED (already verified).

### 7.4 r3l3-runner-process-watch (15 min)

- Proposed decision: DISABLE.
- Rationale: both checks are R3-L3-scoped: the FCC tmux session named
  r3-fcc-runner-L3 and codex exec staleness measured against the run
  state file's task_start. With no tasks running, the codex check is
  vacuous and the FCC session check will false-alert the moment the
  session is legitimately torn down. General process hygiene on the
  laptop is already covered by the zen-laptop-health watch (Item 7.6).
- Evidence: VERIFIED - cron body checks tmux session r3-fcc-runner-L3
  and codex exec vs 30-min timeout from state file (crons/minutely/
  r3l3-runner-process-watch__interval@15m.md). VERIFIED - run closed,
  no task_start (state file). ASSUMED - the FCC tmux session will be
  torn down as part of post-run cleanup (shutdown-after-use rule); if
  FCC is needed for Item 1, its lane launches its own session under
  its own brief, not this watch.
- Risks: a stale codex exec from future non-R3 work would not be
  caught by this watch. Accepted: future work briefs own their process
  lifecycle; the timeout watch pattern (7.5) is reusable per-run.
- Next action: parent disables the cron. FCC session teardown, if
  any, is a separate cleanup action by the parent, verified on the
  laptop (ps + tmux ls), not by this watch.

### 7.5 r3l3-timeout-watch (5 min)

- Proposed decision: DISABLE.
- Rationale: the watch enforces the R3-L3 30-minute per-task timeout
  (warn at 15, kill by exact PID or coordinator-close at 30). No task
  is running and none will start under R3-L3 again, so every 5-minute
  run logs "no task running" forever. The valuable parts (R1
  completed-task guard, signal-hygiene.py verdict helper) are already
  integrated into the repo and remain available for any future run;
  keeping the cron alive adds only log spam and a standing kill
  capability pointed at a stale state file, which is exactly the
  wrong-kill class R1 was built to prevent.
- Evidence: VERIFIED - cron body with R1 two-signal completed-task
  guard and exact-PID kill rule (crons/minutely/r3l3-timeout-watch__
  interval@5m.md). VERIFIED - R1 integrated: signal-hygiene.py +
  6/6 tests PASS, cron bodies updated and read back (review,
  Integration log). VERIFIED - state file task_start null / RUN
  CLOSED. ASSUMED - future runs will create their own timeout watch
  bound to their own state file rather than reviving this one.
- Risks: none while disabled. The kill-by-PID capability is removed
  from the schedule, which is a safety improvement post-run.
- Next action: parent disables the cron. signal-hygiene.py and its
  tests stay in rung3-ci/ untouched.

### 7.6 r3l3-zen-laptop-health (15 min)

- Proposed decision: KEEP, REPURPOSED as the general Zen + laptop +
  daemon health watch. Remove the R3-L3 run-state coupling (pre-start
  grace keyed to the run state file) and the r3-fcc-runner-L3 tmux
  check. Keep everything else: Zen version/PID, ports 9222/2828/
  9223/9224/8082, Zen RSS vs 8 GB threshold, daemon + supervisor
  liveness with detached restart, laptop SSH reachability.
- Rationale: this is the one watch whose value is independent of the
  run. Zen is the owner's daily browser and the team's automation
  surface; the speed-daemon carries all Mei/Mochi messaging and died
  repeatedly during the run (45 starts, cause unknown, R15 deferred
  pending diagnosis). This watch is currently the only thing that
  restarts the daemon when it dies. Disabling it would remove the
  safety net for live infrastructure to save a 15-minute check. The
  RSS check also serves as the R16 alert-first step (alert on memory
  threshold; restart authority stays the owner's, undecided here).
- Evidence: VERIFIED - cron body checks Zen 1.24.3b, ports, RSS,
  daemon/supervisor with restart, FCC tmux (crons/minutely/r3l3-zen-
  laptop-health__interval@15m.md). VERIFIED - daemon.log shows 45
  starts, deaths 26/11 (7x) and 27/11 (2x+), cause unknown; R15
  deferred, diagnosis first (review, Key evidence R15 + ranked list).
  VERIFIED - R16 deferred with alert first, restart authority is
  owner's (review). VERIFIED - R15 service-manager move is owner-
  decision item 5 (review). ASSUMED - Zen 1.24.3b remains the pinned
  version until the owner updates it; the version check should alert,
  not auto-fix, on mismatch.
- Risks: the daemon auto-restart could mask the unknown R15 cause by
  keeping the daemon alive without diagnosis. Mitigation: every
  restart is already logged; parent should pair this keep decision
  with the deferred R15 instrumentation (exit-reason logging +
  supervisor heartbeat) as separate team work. The watch must never
  gain browser-restart power (R16 owner decision) - repurpose keeps
  alert-only for Zen itself.
- Next action: parent edits the cron body (drop run-state grace and
  FCC tmux check, keep all infra checks + daemon restart), keeps the
  15-min schedule, logs the change. R15 diagnosis and R16 authority
  remain open items, not decided here.

### Item 7 summary table

| Watch | Decision | One-line reason |
|---|---|---|
| ledger-push (1h) | Disable after final validation | Ledger final; R19 posture is owner's, untouched |
| agents-watch (15m) | Keep, repurposed | Fleet liveness outlives the run; retire tab cleanup |
| coordinator-liveness (5m) | Disable | Coordinator gone; would alert forever on frozen files |
| runner-process (15m) | Disable | Both checks are R3-L3-scoped and now vacuous |
| timeout-watch (5m) | Disable | No tasks; removes standing kill on stale state |
| zen-laptop-health (15m) | Keep, repurposed | Guards live Zen/laptop/daemon; only daemon restarter |

Net effect: 4 disabled, 2 kept as general infrastructure watches.
Every disable/repurpose is executed by the parent after this meeting
and verified by reading the cron back (cron.view/cron.list), per the
verify-after-write rule. Each change is logged to the master event
log with the full chain.

# Team decisions - decision meeting 27/11/2026

Owner delegation 06:19 27/11/2026: "tu hop tu quyet di" (the team meets
and decides on its own). Coordinator: decision-meeting coordinator.
Council A (Items 1 and 7) and Council B (Items 2 to 6) proposed
independently; an independent redteam attacked every proposal
(verdicts: 1 SUSTAIN, 10 SUSTAIN WITH AMENDMENTS, 1 KILL). This
document records the final decisions with redteam amendments folded
in. Working files in this directory: decision-meeting-councilA-
20261127.md, decision-meeting-councilB-20261127.md, decision-meeting-
redteam-20261127.md. Background: r3-l3-fix-integration-review-
20261127.md (R3-L3 closed 04:49 27/11, Rule-A 52 PASS / 1 FAIL, bars
50/52 and 51/53 both met).

Two structural reconciliations, per redteam:

1. R19 contradiction resolved: Council A Item 7.1 left R19 "open for
   the owner"; Council B Item 2 decided it. The owner delegated, so
   R19 IS decided by this meeting (Item 2 below). Council A's
   "untouched" framing is struck, and its "one final validation pass"
   uses the clean-checkout method from Item 2.
2. Speed-daemon supervision is three-layer, not one: supervisor.sh
   60s loop, watchdog.py, and the zen-laptop-health runtime cron
   (verified restarts 01:43, 03:42, 05:43 on 27/11). Items 6 and 7.6
   together describe and govern all three layers.

Standing rules applied to every next action below: Ponytail for code
work (smallest complete change, reuse first, no unrequested
abstraction, one small test for non-trivial logic, never cut
validation or security); Graphify for codebase context; keybind-first
hard rule (keybind or command over vision); test like a normal user
for user-facing surfaces (enter via search or homepage, click through
the visible UI, no deep links or internal setters, evidence shows
entry, path, action, resulting state); never ydotool; full access for
agents; no personal info on GitHub; never close or navigate
owner-opened tabs or windows; log every event with the full chain
(fail, reasoning, tried, decision, fix, result) to the master event
log via ~/workspace/agent-event-log/log-event.sh; opencode only house
models (opencode/ prefix, opencode/deepseek-v4.1-flash-free), never
NVIDIA, Groq, or OpenRouter for opencode; never assume an agent's
capabilities, check or ask the agent directly; every brief states the
delivery path explicitly; Clone1, Clone2, Mei, and Mochi have no
Tailscale or SSH, so live machine and browser work goes to
SSH-capable workers (Muse subagents, Codex, FCC).

---

## Item 1 - Codeforces contest 735368 task plan

### Decision

START NOW, today Fri 27/11/2026. First 6 problems are the required
scope, finished by end of day 27/11 or morning 28/11 at the latest,
leaving Sat 28/11 for Hieu to fix errors and one re-check pass.
Problems 7 to 10 are attempted only after the required-6 report is
delivered. Execution, as amended by redteam A1 to A5:

1. Access-check first (redteam sequencing): the driver lane (one
   SSH-capable Muse subagent with computer-use on laptop Zen) first
   confirms manager access to contest 735368 and extracts all 10
   statements with limits and samples into the repo, BEFORE solver
   lanes are briefed. Normal-user entry: homepage, then navigate
   through visible UI; no deep-link proof. Keybind-first; vision is
   cross-check only; never close or navigate owner-opened tabs.
2. Plan B if access fails (A1): statements and tests come from Drive
   folder "2. Cuoi khoa" (De bai.docx, loi giai.c, testcases.zip per
   problem); solutions are tested locally against testcases.zip and
   the report states plainly that no Codeforces verdict exists.
   "Stop and report" is not the end of the task.
3. Solver lanes (A2): Codex is primary solver on all 6 required
   problems. FCC is demoted to on-demand second opinion unless FCC
   first passes a timed capability probe (one known problem, local
   tests, result recorded in the repo) BEFORE any assignment. Each
   solution is tested locally against statement samples plus at
   least 2 self-made edge cases before any submission.
4. Error calls (A3): a non-Accepted verdict triggers a blind re-solve
   by a second lane from the statement only (not a review of the
   first solution). A BLOCKING error rating requires both lanes to
   fail the same way OR a concrete failing test input reproduced
   locally. The report separates "our solution failed" from "problem
   is broken." Errors are severity-rated BLOCKING / MINOR / NONE.
5. Difficulty (A4): all ratings are labelled AI-estimated. Before
   rating the 6, the lanes rate 2 to 3 already-used CF26 problems of
   known category (Nhan biet / Thong hieu / Van dung / VDC) with the
   same rubric as a calibration anchor. Rating writes are sequenced
   (ratings held by the coordinator until both lanes have written)
   so independence is real. Disagreements over one level are
   recorded explicitly, not averaged silently.
6. Manager-account submissions (A5): acceptability of submitting
   under the owner's manager nick is decided explicitly BEFORE the
   first submission and recorded; every submission ID (or timestamp
   plus problem code) goes in the report AND the master event log.
   Verdict evidence is captured DOM/CLI first, screenshot cross-check
   only.
7. Report: one markdown report to todolist-push (summary table:
   problem | verdict | difficulty intended vs assessed | errors with
   severity | action for Hieu; per-problem sections; prioritised fix
   list; explicit statement of what was NOT checked). Short summary
   to the owner in chat. Per-problem soft cap 45 minutes per lane,
   enforced by the coordinator (see Item 7.5), with partial progress
   recorded and all 6 getting a first pass before any deep retry.

### Rationale

R3-L3 closed 04:49 27/11, so the second-to-last sequencing blocker is
gone; the exam is Sun 29/11/2026, so a later start leaves Hieu no fix
window. The owner's "check Zen first" question was delegated away at
06:19; the need to check remains, so access confirmation is step 1
with a Drive fallback, not a reason to wait.

### Redteam objections and how they were answered

- No fallback if manager session is dead: answered by A1 (Drive
  source fallback) and access-check-first sequencing.
- FCC equal split unjustified (R3-037: FCC lane FAIL at 29m59s, 1 of
  2 domains): answered by A2 (Codex primary; FCC probe-gated).
- 45-min cap + one resubmit manufactures false BLOCKING calls:
  answered by A3 (blind re-solve; concrete failing input required).
- Three AI signals, no student anchor, independence unenforceable:
  answered by A4 (AI-estimated label, calibration anchor, sequenced
  writes).
- Account pollution waved through: answered by A5 (explicit decision
  before first submission; submission IDs logged).

### Evidence labels

- VERIFIED: R3-L3 closed 04:49 27/11, Rule-A 52/1 (review header;
  coordinator state file RUN CLOSED).
- VERIFIED: contest 735368, group EoMGcsRgKH, 10 problems, first 6
  required, owner is group manager, exam Sun 29/11/2026, task
  second-to-last (~/memory/2026-11-26.md lines 966 to 990).
- VERIFIED: Drive source structure per problem (cf26-upload workflow
  file, redteam read).
- VERIFIED: R3-037 FCC FAIL, 29m59s at cap (grades ledger row +
  scorer grade file, redteam read).
- ASSUMED: manager session still logged in and contest open on
  27/11. Verified or refuted by driver step 1; A1 fallback covers
  refutation.
- ASSUMED: verdicts visible to manager account with submission IDs.
  Confirmed at first submission.

### Concrete next actions (parent executes)

1. Parent spawns the driver lane (SSH-capable Muse subagent,
   browser-capable) with a brief stating: delivery path (statements
   + evidence to todolist-push under a cf735368 folder), access
   confirmation first, Drive fallback, keybind-first, normal-user
   entry, never-close-owner-tabs, stop-and-report with exact screen
   state on access failure. First deliverable: access confirmation
   plus 10 extracted statements (or Drive fallback notice).
2. Coordinator briefs Codex (all 6) and, only if the capability probe
   passes, FCC (second opinion). Briefs state Ponytail, local
   sample+edge testing, blind re-solve duty, difficulty rubric with
   calibration anchor, 45-min cap with coordinator as enforcer,
   delivery path (solution + test log to repo).
3. Coordinator briefs Clone2 as independent repo-only reviewer
   (difficulty mapping + statement/test error flagging). Mei on
   standby for disagreements. Mochi and Clone1: no required
   assignment (token limits, no SSH).
4. Coordinator decides manager-submission acceptability with the
   parent before first submission; driver submits, captures
   verdicts, commits evidence; coordinator assembles and pushes the
   report, logs every step, summarises to the owner. Optional 7 to
   10 start only on coordinator release after the required-6 report.

---

## Item 2 (R19) - Ledger-push watch validation posture

### Decision

Clean-checkout validation is the standing posture. Validators
(validate-ledger.py, ledger-cross-check.py) never execute from inside
the flagged worktree; they run from a clean checkout of todolist-push
at the CURRENT head at validation time (SHA recorded in every
validation log line), or equivalently the two stdlib-only validator
files copied to a scratch directory outside the flagged tree, against
read-only copies of all inputs. No blanket approval to execute
worktree code is recorded anywhere. For the closed R3-L3, one final
clean validation seals the record. Whether any watch runs on a
schedule is Item 7.1; this item decides where and how validation
executes whenever it runs.

### Rationale

The validators are the independent check on the ledger; if they
execute from the same writable tree runners write evidence into, the
checked and the checker share a tree, which is what the intermittent
execution-risk guard points at. The run is closed, so there is no
live-run urgency justifying in-tree execution. Approving in-tree
execution would set a blanket precedent for every future flagged
tree.

### Redteam objections and how they were answered

- Pinned SHA pins the wrong artifact (frozen-heads.txt pins the task
  list 9b9d900, not validator code): answered by B1 - pin to current
  todolist-push head at validation time, record the SHA; the
  frozen-heads.txt mitigation is struck.
- Guard's real reason unknown; clean checkout may not fix it (guard
  may be workspace-wide; intermittence unexplained): answered by B3 -
  capture one actual guard block message first; if the guard is
  workspace-wide, the scratch location goes outside ~/workspace or
  the posture gets a different fix. The posture decision (never
  execute from the flagged tree) stands either way; B3 decides the
  scratch location.
- Cross-check inputs are not all in the repo (verdict files in
  ~/workspace/rung3-verdicts/, never committed; order file
  thu-tu-chay.txt): answered by B2 - all inputs named with source
  paths, copied as one snapshot (verdict dir first, ledger last),
  mismatch window documented, test includes the between-writes case.
- Script with no schedule or owner is ceremony: answered by B4 -
  invocation point written into the next run's coordinator checklist
  now (validation step at each ledger push and at run close).

### Evidence labels

- VERIFIED: watch body runs both validators in ~/workspace/r3l3-run-wt
  (cron file, steps 1 and 2); both files exist in rung3-ci/.
- VERIFIED: block is intermittent (council1 Rank 24 citations: blocks
  26/11, 00:48 and 03:48 27/11; OK 01:48, 02:48).
- VERIFIED: frozen-heads.txt pins list_commit 9b9d900 and the task
  list sha256 (redteam direct read).
- VERIFIED: ledger-cross-check.py reads verdict files from
  ~/workspace/rung3-verdicts/ (VM-local, never committed) and the
  order file (redteam direct read).
- VERIFIED: both validators import only stdlib (json/os/re/sys),
  so the copy-two-files variant is viable (redteam direct read).
- ASSUMED: guard flags the worktree for agent-written evidence.
  Verified or refuted by B3's captured block message.

### Concrete next actions

1. Coordinator (or SSH-capable worker) captures one guard block
   message from a blocked watch run log (B3) and records the scratch
   location decision.
2. Worker writes the clean validation script: fetch todolist-push at
   current head to a scratch dir outside the flagged tree (or copy
   the two validator files there), copy ledger + verdict dir + order
   file read-only as one snapshot, run both validators, print exit
   codes and SHA. One small test: closed R3-L3 ledger passes exit 0;
   one mutated copied row fails nonzero; between-writes copy case
   documented. Delivery path: script committed to todolist-push
   under rung3-ci/; final R3-L3 validation result logged to the
   master event log.
3. Coordinator writes the invocation point into the next run's
   coordinator checklist (validation at each ledger push and at
   close). This script's final R3-L3 run is the "one final validation
   pass" in Item 7.1, sequenced after the script's test passes.

---

## Item 3 (R10) - Durable Cloudflare direction

### Owner criterion (fixed 06:20 to 06:21 27/11, recorded)

The Cloudflare fix must work so that when a normal user opens Zen and
searches and browses like normal, Cloudflare does not block them; AND
agents can still be called to use computer-use on Zen at any time;
AND agents still use Zen optimized for AI. Human browsing in Zen must
present as a normal browser to Cloudflare (no automation signals such
as navigator.webdriver leaking to pages), while agent computer-use
control of the same Zen stays available at any time and the AI
optimization of Zen stays. Owner addendum 06:21 27/11: "Can thi build
cong cu rieng" (if needed, build a dedicated tool). Standing design
principle: the user's machine is AI-optimized but the repo must work on
stock apps; machine optimizations go in the repo only as OPTIONAL
(opt-in, default off).

### Decision

Staged route; the build is NOT pre-authorized by this decision.

Stage 1 now (adapt and diagnose, no new tool, timeboxed 2 working
days): keep the integrated residue (pinned shim hash, probe result
in every drive report, dirty probe equals stop) as the interim
agent-side guard, and run a read-only investigation on the laptop in
a throwaway profile answering: (a) which launcher flag or flags force
navigator.webdriver true, and can that forcing be removed or
conditioned without losing agent attach; (b) does the preference
layer (prefs.js / about:config, e.g. dom.webdriver.enabled) change
the page-visible value; (c) why the probe disagreed across eval paths
(webdriver true via zen_dom eval on R3-100 vs probe-clean false
elsewhere) - deliver ONE unified probe that also checks getter
toString; (d) price the alternatives with the same rigor as a build:
two Zen profiles in one install (human profile flag-free, agent
profile flagged), boundary-restart model (launch clean, relaunch with
flags when an agent is called), including how often R3-L3 agent tasks
actually needed owner-session continuity (count from drive reports).

Stage 2 (fresh team decision on the Stage 1 report): if a flag or
pref change makes human launches present clean while agent attach
still works on the same Zen, adopt it and do not build. If the signal
is inseparable from agent availability AND the priced alternatives
fail the criterion, the team decides on building a dedicated
automation-fingerprint hiding layer. That build decision requires, at
decision time: a named maintenance owner, an estimated build cost, a
probe coverage list frozen that day (any new signal class needs a
new decision), and kill criteria (e.g. two consecutive Zen updates
breaking the layer retires it to the profile-split fallback). The
owner's "build if needed" authorizes building when need is proven by
Stage 1 evidence; it does not pre-authorize building before that
evidence exists.

If built, scope is: normalize page-visible automation signals so
pages see a normal browser - navigator.webdriver false to page
JavaScript plus exactly the signals on the frozen probe coverage
list. Explicitly out of scope: solving CAPTCHAs, rotating or spoofing
IP addresses, spoofing TLS or network fingerprints, imitating human
behavior, promising that Cloudflare passes any given visit. The tool
ships with its probe as a fail-loud command; for agents dirty still
means stop. Placement: active configuration on the user's machine layer
(laptop Zen); repo carries it only as OPTIONAL opt-in, default off,
with the probe test included. Acceptance (either branch): probe-clean
is necessary, not sufficient - repeated human-path visits (open Zen
the normal way, search, click through to multiple Cloudflare-
protected sites, no deep links or internal setters) with no block,
plus an agent computer-use drive on the same Zen session with the
pill visible; evidence shows entry, path, action, resulting state.
Actual block outcomes keep being recorded separately in drive
reports.

Explicitly rejected as the durable direction: shim-as-brief-discipline
for agent drives only (leaves human browsing flagged, fails leg one
of the criterion); shim shipped default-on in the repo (violates
opt-in default-off; probe currently disagrees with itself);
browser split as the primary route without pricing (stays a priced
alternative in Stage 1 and the fallback if a build fails its live
test).

### Rationale

Most cheap routes break one leg of the three-leg criterion. The shim
residue protects only drives that remember to use it; a human opening
Zen runs no brief or probe. Default-on repo shim would manufacture
false confidence from a self-disagreeing probe. A split breaks
same-Zen session continuity in spirit. Only source removal (flag or
pref) or in-browser hiding for every page can satisfy all three legs;
Stage 1 finds out which is real before any maintenance budget is
spent. Ponytail: smallest complete change first.

### Redteam objections and how they were answered

- Stage 1 omits the pref layer and may spend days proving known
  Firefox behaviour: answered by C1 - pref test included, 2-day
  timebox, "inseparable" only after flag AND pref fail with evidence.
- Probe disagrees with itself; shim detectable via getter toString
  ("function () { [native code] }" vs native): answered by C3 - the
  unified probe must check getter toString and at least one
  non-webdriver signal, or the decision states plainly the probe
  certifies webdriver only.
- Build scope open-ended ("any further signals the probe proves"):
  answered by C2 + C3 - build not pre-authorized; coverage list
  frozen at build-decision time; new signal class needs a new
  decision.
- No maintenance owner; Zen updates will break it; opt-in repo code
  exercised on one machine rots: answered by C2 - named owner, cost
  estimate, kill criteria required before any build starts.
- Cheaper routes (two profiles, boundary restart, pref) rejected
  without pricing: answered by C4 - Stage 1 prices them, including
  the owner-session-continuity count from R3-L3 drive reports.
- Single-visit acceptance cannot prove the criterion: answered by C5
  - repeated multi-site human-path visits; block outcomes recorded
  separately forever.

### Evidence labels

- VERIFIED: wrapper flags force navigator.webdriver true on every
  launch even with no client connected (council1 Rank 11, daily note
  2026-11-25.md line 829).
- VERIFIED: shim proven live and probe-clean repeatedly, pill visible
  whole drive, no bot block (council1 Rank 11, 2026-11-26.md line
  712); holder artifact at improvements/fixb-evidence/holder-fixb.mjs.
- VERIFIED: residue integrated (hash pin, probe in every drive
  report, dirty equals stop), commit 27da702d (review integration
  log).
- VERIFIED: probe inconsistency real (R3-100 true vs probe-clean
  false on R3-028/029/035/036/046/049; council2 Rank 18) and shim
  changes getter toString (redteam read of fixb-evidence logs).
- ASSUMED: webdriver forcing is tied to the automation endpoint.
  Stage 1 flag-by-flag and pref tests verify or refute.
- ASSUMED: Cloudflare blocks here are driven mainly by the webdriver
  signal. Stage 1 and the acceptance test verify; if blocks persist
  with a clean probe, the team reports that honestly instead of
  expanding evasion scope.

### Concrete next actions

1. SSH-capable worker (not Clone1/Clone2/Mei/Mochi) runs Stage 1 in a
   throwaway profile: launcher flag inventory, flag-by-flag and pref
   launch tests recording page-visible navigator.webdriver, unified
   probe (including getter toString), alternatives pricing with the
   owner-session-continuity count. Timebox 2 working days. Delivery
   path: report committed to todolist-push under improvements/;
   full chain logged to the master event log. No launcher change, no
   build, until the report lands.
2. Coordinator convenes the Stage 2 decision on the report: flag/pref
   fix if separable; else priced alternatives vs build with owner,
   cost, frozen coverage, kill criteria. Acceptance test as specified
   above, throwaway profile first, real profile only at a task
   boundary with the pill visible.

---

## Item 4 (R16) - Browser restart authority

### Decision

No watch ever gets kill-live authority: no cron watch may kill or
restart a running Zen. Revive-dead authority IS granted, narrowly:
the zen-laptop-health watch may relaunch Zen only when no Zen process
exists AND ports 9222/2828 are down on two consecutive checks; every
revive is logged with the full chain. Memory risk is handled by a
read-only threshold alert plus a boundary-only restart procedure that
a coordinator or human agent initiates deliberately at task
boundaries, never mid-drive: record open tabs (including pinned and
essential) via BiDi list dump to a file before restart, restart
through the wrapper, then verify ports, pill, session restore, and
owner essentials present after. The same record-before / verify-after
checklist and R6 guardrail govern agent-initiated restarts for tooling
reasons (e.g. sessionstore surgery), whoever initiates. The alert's
human is the coordinator on duty; if nobody acts, the accepted
outcome is stated plainly: the browser stays as is (or down, with
revive-dead covering the dead case) until the next human or agent
session, and session restore happens on next launch.

### Rationale

Restarting a live browser is destructive to session state, and owner
tabs were already hurt once by automation (the 24-tab over-close that
created Task 56). Watches are simple loops with a proven false-alarm
record; kill power over the owner's browser repeats the R6 failure
class with a bigger blast radius. Reviving an already-dead browser
destroys nothing that is not already destroyed, so it carries a
different risk profile and covers the one death that actually
happened. Alert plus procedure addresses memory exhaustion without
creating a new standing kill authority.

### Redteam objections and how they were answered

- 8 GB threshold is invented (no calibration; G-27 shows it predates
  growth data): answered by D2 - the procedure writes "8 GB
  (uncalibrated placeholder)"; RSS + system headroom are recorded at
  every boundary of the next run to calibrate; a growth-rate alert
  (GB/h) is added to the health watch.
- The actual 04:12 death was an agent sessionstore restart at 3.79 GB
  RSS, not memory; the alert would not have fired: answered by D3 -
  the procedure now governs agent-initiated tooling restarts, the
  path that actually occurs.
- Growth ~5 GB/h defeats a 15-min alert cadence; nobody reads alerts
  at 04:00: answered by D2 (growth-rate alert catches it earlier)
  and D5 (named human; accepted no-actor outcome stated).
- Kill-live vs revive-dead conflated: answered by D1 - split
  explicitly; revive-dead-only granted with two-check confirmation
  and logging.
- Procedure depends on restore tooling known-broken (lz4 decoder
  missing on laptop, R20): answered by D4 - R20 pulled forward as a
  prerequisite; tab-record mechanism specified (BiDi list dump);
  procedure is not "ready" until a throwaway-profile drill passes on
  the real mechanism.

### Evidence labels

- VERIFIED: Zen died 04:12:31 to 04:13:52 27/11 at last RSS 3.79 GB;
  cause was the Task 56 runner's sessionstore restart; recovered as
  fresh process at 1.40 GB (~/memory/2026-11-27.md lines 81, 98, 115;
  redteam read).
- VERIFIED: health watch alerts at RSS over 8 GB and has no browser
  restart authority by design (cron body).
- VERIFIED: 24-tab over-close including 5 essentials + 3 pinned
  created Task 56 (review R6 row).
- VERIFIED: session-store decoder missing on laptop (lz4 absent;
  council1 Rank 22, review R20).
- VERIFIED: memory growth data point +1.34 GB in 16 min (25/11 log
  line 1273, redteam read).
- ASSUMED: 8 GB gives enough lead time. Uncalibrated; D2 data
  collection replaces the assumption next run.

### Concrete next actions

1. Coordinator writes the boundary restart procedure (threshold
   labelled uncalibrated, record step via BiDi dump, restart step,
   verify step, R6 reference, tooling-restart coverage) into the
   laptop machine layer and the brief template; generic text to
   todolist-push. Prerequisite: R20 decoder installed on the laptop
   by an SSH-capable worker.
2. Parent edits the zen-laptop-health watch body: add growth-rate
   alert line and revive-dead-only relaunch (two consecutive
   no-process + ports-down checks, logged); no kill-live command is
   added. Verified by cron read-back.
3. Throwaway-profile drill before real use: open recorded tabs
   including a pinned tab, run the procedure, confirm restore and
   pill. Drill result logged to the master event log.

---

## Item 5 (R22) - PII scan loosening

### Decision

KILL. No loosening. No sign-off class, no per-URL override, no
allowlist of any kind. pii-scan.py stays the sole gate: exit 1 means
no push, full stop. The three manual-review passes that already
happened during R3-L3 are NOT retroactively blessed; instead they are
checked as potential exposure (below). If evidence completeness
genuinely suffers, the approved remedy is deterministic and
runner-side: redact URLs to host + sha256-of-url before snapshot
sealing (or keep raw URLs in the VM-local never-committed store,
~/workspace/rung3-verdicts/, referenced by hash). That is a tooling
change, not a loosening, and it needs no human override.

### Rationale

A docs/drive URL is a capability: anyone holding it opens the live
document, and later edits leak through the pushed link. "Task-created"
provenance is self-attested by the runner whose snapshot is being
gated, in a system where evidence fabrication recurred on 25/11. The
standing rule (2026-11-23) requires a deterministic block precisely
because discretion failed; a sign-off class reintroduces discretion
at the point of maximum pressure, and a pushed URL cannot be
un-pushed. The benefit (clickable evidence) is nil: snapshots already
prove outcomes with screenshots and result files, and a live doc can
drift from what the task produced.

### Redteam objections and how they were answered

All five redteam objections are accepted in full; the council
proposal is rejected rather than amended:

- URL is a capability; later edits leak through it. Accepted: no URL
  of an editable doc goes to GitHub under any sign-off.
- "Task-created" is self-attested by the checked party. Accepted: no
  labelling-based eligibility.
- Sign-off beside the scanner violates the deterministic-block rule
  in spirit. Accepted: discretion stays out of the leak path.
- Rubber stamp already happened 3 times; "no leak occurred" is
  unverifiable. Accepted: the three passes are treated as potential
  exposure to check, not precedent to formalize.
- Benefit does not justify it. Accepted: redaction or VM-local store
  preserves the evidence chain without the capability.

Council B's refusal of any high-entropy override is noted with
credit; the owner-url half fails for the same structural reason.

### Evidence labels

- VERIFIED: pii-scan.py is a deterministic gate (exit 1 on any hit);
  OWNER_HOSTS includes docs./drive./mail./calendar./notion.so hosts;
  high-entropy rule over 20 chars, entropy over 4.5 (direct reads by
  Council B and redteam).
- VERIFIED: raw logs held out of two snapshots (R3-067, R3-072);
  manual review passed three more hits on task-created doc URLs and
  demo-store routes (council2 Rank 21).
- VERIFIED: evidence fabrication recurred 25/11 (review, error
  tracker recount, A7/A8 still live).
- VERIFIED: standing rule requires deterministic pre-push block, not
  prompt-only rules (MEMORY.md, 2026-11-23).
- ASSUMED: none load-bearing. The KILL does not depend on any
  assumption about doc contents.

### Concrete next actions

1. Coordinator checks whether the three already-passed URLs are in
   pushed snapshots today. If yes: record as potential exposure in
   the master event log; if any doc is owner-owned or still
   editable, share-restrict or rotate it. No retroactive sign-off
   paperwork.
2. If a future run needs URL evidence, an SSH-capable worker adds
   runner-side redaction (host + sha256-of-url) before sealing, with
   one deterministic test (redacted fixture passes the scanner; raw
   URL fixture still blocks). Delivery path: code + test to
   todolist-push; result logged. Until then, URLs are simply dropped
   from snapshots; screenshot evidence stands.

---

## Item 6 (R15) - Speed-daemon supervision

### Decision

Instrument now; supervision structure unchanged while instrumentation
runs; the supervision decision is re-opened at a hard trigger with a
named owner. The service-manager route is KILLED in this decision
(verified unavailable on this VM). The system is described honestly
as three layers: supervisor.sh 60s loop, watchdog.py, and the
zen-laptop-health runtime cron (the layer that performed the observed
rescues). Steps:

1. Log archaeology FIRST, before any code change (E2): correlate the
   46 daemon_start events in daemon.log with VM replacement records
   and watchdog restart entries; publish the split (VM replacement /
   watchdog-induced / unexplained). If unexplained is small,
   instrumentation scope shrinks accordingly.
2. Instrumentation (append-only, no lifecycle change): daemon
   exit-reason line in daemon.log; supervisor heartbeat line in
   watchdog.log every cycle or every N cycles; double-start
   contention line on bind failure; and every restart path logs its
   identity (E4: supervisor loop, watchdog.py, zen-laptop-health
   watch) so "daemon died" is distinguishable from "daemon was
   restarted by X." Stated blind spot (E5): exit logging cannot
   capture VM death; heartbeat gaps correlated with replacement
   records are the evidence for that class, and "no exit lines" must
   never be misread as "no deaths."
3. Trigger (E3): the coordinator reviews and DECIDES supervision
   when either (a) instrumentation has captured at least two deaths
   with named causes, or (b) 7 days after instrumentation lands,
   whichever first. The review produces a supervision decision, not
   another instrumentation round. The decision at that point is
   between formalizing the runtime-cron outer supervisor (check-once
   pattern, the only layer surviving VM replacement) and keeping the
   current three-layer arrangement as documented. Kill test required
   before adopting any change: kill daemon, confirm restart within
   one cycle; kill supervisor, confirm daemon survives.

Explicitly rejected now: any supervisor rewrite; service-manager
migration (bus verified absent); treating "supervision unchanged" as
if the zen-laptop-health restarter did not exist.

### Rationale

Cause is unknown and a blind supervision change can mask it or
double-start (two address-already-in-use tracebacks already in
daemon.out). Co-deaths include VM replacements, which no same-VM
supervisor survives. Instrumentation converts the next deaths into
evidence; archaeology may name half the causes today with zero code.
The outer runtime-cron layer already exists de facto and is the only
co-death-proof layer, so the future decision is about formalizing it,
not inventing supervision from scratch.

### Redteam objections and how they were answered

- VM replacement defeats exit logging; trigger may never fire:
  answered by E5 (blind spot stated; heartbeat-gap correlation is
  the evidence) and E3 (7-day hard date with a decision, not more
  instrumentation).
- Service-manager route already dead but kept alive: answered by E1
  - killed now (systemctl --user fails "No medium found", no
  /run/user/1000/bus, redteam probe 27/11).
- Runtime-cron outer supervisor underweighted; three-layer reality
  ignored: answered by naming all three layers in the decision and
  making formalization the explicit trigger-point question.
- Instrumentation can mask supervisor-induced deaths (watchdog
  restarting a live-but-slow daemon): answered by E2 (archaeology
  counts watchdog-induced restarts first) and E4 (restarter identity
  on every restart).
- No owner, no date: answered by E3 (coordinator owns; trigger OR
  7-day date, whichever first).

### Evidence labels

- VERIFIED: daemon.log has 46 daemon_start events (grep count 27/11;
  the review's 45 reconciles with a further start at 05:43 27/11).
- VERIFIED: daemon.out contains two address-already-in-use
  tracebacks (double-start attempts).
- VERIFIED: supervisor.log is 0 bytes by design (watchdog output goes
  to watchdog.log); watchdog.py logs only on daemon-down, so
  supervisor liveness is currently unobservable (direct reads).
- VERIFIED: supervisor.sh records no cron daemon and no user systemd
  bus on this VM; systemctl --user fails "No medium found" (redteam
  probe).
- VERIFIED: co-death at least 3 times (VM replacement 26/11; 01:42
  and 03:42 27/11); zen-laptop-health cron restarted the daemon at
  01:43, 03:42, 05:43 on 27/11 (cron body + daily log).
- ASSUMED: split of deaths between VM replacement and other causes.
  E2 archaeology replaces the assumption.

### Concrete next actions

1. VM-side worker runs E2 archaeology (46 starts vs replacement
   records vs watchdog restart entries), publishes the split to
   todolist-push improvements/ and logs it. No code change yet.
2. VM-side worker adds the instrumentation (exit line, heartbeat
   line, contention line, restarter identity). One small test: kill
   daemon, exit line appears; stop supervisor, heartbeat stops
   within two cycles; start a second daemon, contention line
   appears. Delivery path: changes to todolist-push under the
   speed-daemon directory (or its repo home); test results logged.
3. Coordinator owns the trigger: decision meeting on the earlier of
   two named-cause deaths or 7 days post-instrumentation, choosing
   between formalized runtime-cron outer supervisor and documented
   three-layer status quo, kill test required before adoption.

---

## Item 7 - Post-run disposition of the 6 R3-L3 watchdog crons

General: the run is closed. Watches that only observe run files are
disabled; watches guarding live infrastructure are kept with their
run coupling removed. Every change is executed by the parent after
this meeting, verified by cron read-back (cron.view / cron.list), and
logged to the master event log with the full chain. Sequencing with
Item 1 is explicit where it matters.

### 7.1 r3l3-ledger-push-watch (hourly) - DISABLE after final validation

Decision: disable the hourly schedule after one final validation
pass run via the Item 2 clean-checkout method (sequenced after that
script's test passes; never in the flagged worktree). R19 is recorded
as DECIDED by this meeting (Item 2); Council A's "stays open for the
owner" framing is struck. The manual validation invocation point is
written into the next run's coordinator checklist (Item 2, B4), so
disabling the schedule does not orphan the posture.

Evidence: VERIFIED cron body (validate + cross-check + 60-min
push-lag alert, in ~/workspace/r3l3-run-wt); VERIFIED final tip
914ad171 ls-remote verified (review integration log). ASSUMED: no
further ledger rows post-closure; a correction row would be validated
manually before push.

Next action: parent runs Item 2's clean validation once (exit 0,
zero unpushed rows), logs it, then disables the cron and verifies by
read-back.

### 7.2 r3l3-agents-watch (15m) - KEEP, minus step 6

Decision: keep as the general agent-fleet watch (agent liveness via
CDP/daemon, pokes, screen look). Retire the R3-L3 tab-cleanup step 6
after one final sweep: dry-run list first; any recorded
completed-task tabs still open are closed live under R6 rules
(allowlist only, pill visible, pinned/essential never matched) or
explicitly accepted in the log - not silently left. Amendments: (a)
the 15-min screen look drops to on-alert-only (screenshot only when a
CDP check is inconclusive, which the body already supports as
fallback) - standing screenshot surveillance of the owner's daily
machine is not justified post-run; (b) poke rule narrows: poke only
when a task is recorded as assigned-and-awaiting in coordinator
state, not on any unanswered message (idle is not silent; this also
protects Clone2's long Item 1 review from poke interruption).

Evidence: VERIFIED cron body (4 agents, poke after 15-min silence,
screen look, step 6 allowlist-only); VERIFIED R6 guardrail integrated
27/11 (review). ASSUMED: agent PWAs and CDP ports 9223/9224 remain
the fleet access path post-run.

Next action: parent edits the cron body (remove step 6 after the
final sweep is logged, screen look to on-alert-only, poke rule
narrowed), keeps the 15-min schedule, verifies by read-back, logs the
change.

### 7.3 r3l3-coordinator-liveness-watch (5m) - DISABLE (redteam SUSTAIN)

Decision: disable. It reads only R3-L3 files (state, heartbeat,
per-task reports) that will never change again; left enabled it fires
false alerts every 5 minutes forever (it was still alerting at 04:13
27/11 while the coordinator was alive - the R1 false-alarm class).
signal-hygiene.py stays in rung3-ci/ for future runs.

Evidence: VERIFIED cron body; VERIFIED heartbeat stopped 02:18:50
27/11 with ~2.5h false alarms (review R1 evidence); VERIFIED state
file RUN CLOSED.

Next action: parent disables the cron, verifies by read-back, logs.

### 7.4 r3l3-runner-process-watch (15m) - DISABLE, sequenced after Item 1

Decision: disable, but only after Item 1 completes. Both checks are
R3-L3-scoped (tmux session r3-fcc-runner-L3; codex exec vs state-file
task_start), so post-run they are vacuous; however Item 1 may still
run an FCC lane (second opinion, probe-gated per A2) starting today,
and disabling its only process monitor into an active assignment is
the collision redteam flagged. Until Item 1 closes, the watch stays;
if FCC is never used in Item 1, the parent may disable immediately
and record why.

Evidence: VERIFIED cron body (both checks R3-L3-scoped); VERIFIED
run closed, no task_start. ASSUMED: the FCC tmux session is torn down
in post-run cleanup; Item 1's FCC use, if any, launches under its own
brief.

Next action: parent disables after Item 1's report is delivered (or
immediately if FCC goes unused, with the reason logged), verifies by
read-back, logs. FCC session teardown is a separate verified cleanup
(ps + tmux ls on the laptop), not this watch's job.

### 7.5 r3l3-timeout-watch (5m) - DISABLE, cap enforcer named

Decision: disable. No task is running under R3-L3; keeping it adds
log spam and a standing kill-by-PID capability pointed at a stale
state file (the wrong-kill class R1 was built to prevent). The R1
signal-hygiene helper and its tests stay in rung3-ci/. Amendment:
Item 1's 45-minute per-problem cap has no watch enforcer, so Item 1
briefs name the coordinator as cap enforcer (checks lane progress at
45 min and calls the stop) - already written into Item 1 above.

Evidence: VERIFIED cron body with R1 two-signal guard; VERIFIED R1
integrated (signal-hygiene.py, 6/6 tests); VERIFIED state file
task_start null / RUN CLOSED.

Next action: parent disables the cron, verifies by read-back, logs.
Item 1 briefs carry the named-enforcer line.

### 7.6 r3l3-zen-laptop-health (15m) - KEEP, repurposed

Decision: keep as the general Zen + laptop + daemon health watch.
Remove the R3-L3 run-state coupling (pre-start grace keyed to the run
state file). Keep: Zen PID/version, ports 9222/2828/9223/9224/8082,
RSS check, daemon + supervisor liveness with detached restart, laptop
SSH reachability. Amendments: (a) the decision text names the three
daemon supervision layers (supervisor.sh loop, watchdog.py, this
watch) and this watch's role as the outer, VM-external restarter;
its restart events feed Item 6's instrumentation (E4); (b) the FCC
tmux check stays until Item 1 closes, then is removed (sequenced
with 7.4); (c) the Zen version check alerts once per version change
(state comparison), not every cycle, so an owner Zen update does not
train everyone to ignore the watch; (d) the 8 GB RSS threshold is
labelled uncalibrated until Item 4's D2 data exists, and the
growth-rate alert from Item 4 is added; (e) revive-dead-only Zen
relaunch authority from Item 4 (D1) is added: no process + ports down
on two consecutive checks, logged; never kill a live Zen.

Evidence: VERIFIED cron body (all checks + daemon restart); VERIFIED
daemon restarts by this watch 01:43, 03:42, 05:43 on 27/11 (daily
log); VERIFIED R15 deferred pending diagnosis and R16 alert-first
(review). ASSUMED: Zen 1.24.3b remains pinned until the owner updates
it; version mismatch alerts, never auto-fixes.

Next action: parent edits the cron body per (a) to (e) (FCC tmux
removal sequenced after Item 1), keeps the 15-min schedule, verifies
by read-back, logs the change.

### Item 7 summary

| Watch | Decision |
|---|---|
| ledger-push (1h) | Disable after final clean validation (Item 2 method) |
| agents-watch (15m) | Keep minus step 6; screen look on-alert-only; poke narrowed |
| coordinator-liveness (5m) | Disable |
| runner-process (15m) | Disable after Item 1 completes |
| timeout-watch (5m) | Disable; Item 1 cap enforcer is the coordinator |
| zen-laptop-health (15m) | Keep repurposed; revive-dead authority; growth-rate alert |

---

## Parent execution list (in order)

1. Launch Item 1: spawn the SSH-capable browser driver lane (access
   check + statement extraction, Drive fallback), then Codex solver
   lane, FCC probe-gated second opinion, Clone2 reviewer. Decide
   manager-submission acceptability before first submission.
2. Item 2: capture one guard block message; build + test the clean
   validation script; run the final R3-L3 validation; then disable
   r3l3-ledger-push-watch (7.1) and verify by read-back.
3. Disable r3l3-coordinator-liveness-watch (7.3) and
   r3l3-timeout-watch (7.5) now; verify by read-back. Item 1 briefs
   name the coordinator as 45-min cap enforcer.
4. Edit r3l3-agents-watch (7.2: final tab sweep, remove step 6,
   screen look on-alert-only, poke narrowed) and r3l3-zen-laptop-
   health (7.6: drop run coupling, version alert-once, growth-rate
   alert, revive-dead authority; FCC tmux check removed only after
   Item 1). Verify both by read-back.
5. After Item 1's report is delivered: disable
   r3l3-runner-process-watch (7.4) and remove the FCC tmux check from
   7.6. Verify by read-back.
6. Item 3: spawn the Stage 1 investigation worker (SSH-capable,
   throwaway profile, 2-day timebox). No build until the Stage 1
   report returns for a fresh decision.
7. Item 4: R20 decoder install on laptop; write the boundary restart
   procedure; throwaway-profile drill.
8. Item 5: check the three passed URLs against pushed snapshots;
   log exposure if present; share-restrict or rotate if owner-owned.
   No scanner change.
9. Item 6: E2 log archaeology, then instrumentation; coordinator
   owns the 7-day / two-named-cause-deaths decision trigger.
10. Log every executed step to the master event log with the full
    chain via ~/workspace/agent-event-log/log-event.sh.

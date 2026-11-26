# Decision meeting: Council Member B proposals (27/11/2026)

Owner delegation 06:19 27/11/2026: "tu hop tu quyet di" (the team decides
on its own). This file proposes decisions for Items 2 to 6, the five
owner-decision items from the R3-L3 fix-integration review, now delegated
to the team. An independent redteam attacks these proposals afterward.
Decision task only: nothing here is implemented by this file.

Evidence read before deciding: r3-l3-fix-integration-review-20261127.md
(full, including Owner-decision items and R10/R15/R16/R19/R22 rows);
fix-review-council1-20261127.md (C17 Rank 11, C10 Rank 16, C24 Rank 17,
C20 Rank 18, C13 Rank 24); fix-review-council2-20261127.md (C23 Rank 21,
C19 Rank 17, C26 Rank 18); fix-review-redteam-20261127.md (sections on
R10/R15/R16/R19/R22 and section 5); speed-daemon daemon.log tail,
supervisor.sh, daemon.sh, watchdog.py, daemon.out, supervisor.log and
watchdog.log (direct reads 27/11); the ledger-push watch cron body
(r3l3-ledger-push-watch__interval@1h.md); pii-scan.py (direct read);
directory listings of rung3-ci/ and improvements/fixb-evidence/.

Evidence labels: VERIFIED means checked in a file or tool output named
beside the fact. ASSUMED means reasoned but not directly checked; each
ASSUMED fact names what would verify it.

Standing rules applied to every proposal below: Ponytail for code work
(smallest complete change, reuse first, no unrequested abstraction, one
small test for non-trivial logic, never cut validation or security);
Graphify for codebase context before code work; keybind-first hard rule
(keybind or command over vision); test like a normal user for
user-facing surfaces (enter via search or homepage, click through the
visible UI, no deep links or internal setters, evidence shows entry,
path, action, resulting state); never ydotool; full access for agents;
no personal info on GitHub; never close or navigate owner-opened
tabs or windows; log every event with the full chain (fail, reasoning,
tried, decision, fix, result) to the master event log via
~/workspace/agent-event-log/log-event.sh; opencode only house models
(opencode/ prefix, model opencode/deepseek-v4.1-flash-free), never
NVIDIA, Groq, or OpenRouter for opencode; never assume an agent's
capabilities, check or ask the agent directly; every brief states the
delivery path explicitly; Clone1, Clone2, Mei, and Mochi have no
Tailscale or SSH, so live machine work goes to SSH-capable workers.

---

## Item 2 (R19): ledger-push watch validation posture

### Proposed decision

Do NOT approve executing validators inside the flagged worktree as a
standing posture. Adopt clean-checkout validation as the standing
posture for any future run: the validators (validate-ledger.py and
ledger-cross-check.py) run from a fresh clone of todolist-push at a
pinned commit SHA, in a directory outside the flagged worktree, against
a read-only copy of the ledger and verdict files. For the now-closed
R3-L3 run, run one final clean-checkout validation to seal the record,
then the posture question is dormant until the next run. Whether the
hourly watch cron keeps running at all is Council A's cron-disposition
item; this proposal decides only where and how validation executes if
any watch or manual check runs.

### Rationale

The validators are the independent check on the ledger. If they execute
from inside the same worktree that runners write evidence into, the
checked and the checker share a writable tree, and the execution-risk
guard that intermittently blocks the watch is pointing at exactly that
coupling. A clean checkout at a pinned SHA breaks the coupling for the
cost of one clone: the validator code is then exactly what was pushed
and reviewed, and nothing a runner wrote can alter it mid-check. The
run is closed, so there is no urgency that would justify approving
in-tree execution to unblock a live run; the cheap, safer posture can
be adopted calmly now and reused by the next run. Approving in-tree
execution would also set a precedent that any future flagged tree gets
a blanket execution approval, which is the opposite of the
evidence-chain safety posture the review asks the owner to set.

### Evidence

- VERIFIED: the watch body runs `python3 rung3-ci/validate-ledger.py`
  and `python3 rung3-ci/ledger-cross-check.py` in ~/workspace/r3l3-run-wt
  (cron file r3l3-ledger-push-watch__interval@1h.md, steps 1 and 2).
- VERIFIED: both validator files exist in the worktree rung3-ci/
  directory (directory listing 27/11: validate-ledger.py,
  ledger-cross-check.py present).
- VERIFIED: the block is intermittent, not continuous. Council1 Rank 24
  cites blocks on 26/11 and at 00:48 and 03:48 on 27/11, with OK runs
  at 01:48 and 02:48 on 27/11 in between (daily note 2026-11-27.md
  03:48 entry, as cited in council1). The review's integration log
  confirms ledger pushes landed throughout by coordinator hand.
- VERIFIED: R3-L3 is closed (04:49 27/11, Rule-A 52 PASS / 1 FAIL,
  final tip 914ad171) per the review header and integration log. No
  live run depends on this watch today.
- ASSUMED: the execution-risk guard flags the worktree because it
  contains agent-written evidence and generated files alongside code.
  Verify by: reading the guard's block message from a blocked watch
  run log. The proposal does not depend on the exact guard reason;
  clean-checkout validation is safe under any of the plausible reasons.

### Risks

- SHA drift: validating against a stale clone could pass a ledger that
  the current validators would fail. Mitigation: pin the clone to the
  frozen head recorded for the run (frozen-heads.txt exists in
  rung3-ci/, VERIFIED by listing) and record the SHA in every
  validation log line.
- Clone latency per hourly run is small (one small repo) but nonzero.
  Acceptable for an hourly watch; if it ever matters, cache the clone
  and fetch the pinned SHA.
- A read-only copy step could copy a half-written ledger if it runs
  mid-write. Mitigation: copy, then validate the copy; a torn copy
  fails validation loudly, which is the safe direction.

### Concrete next action

Coordinator (or an SSH-capable worker briefed by the coordinator)
writes a small clean-checkout validation script: clone todolist-push
to a scratch directory outside the flagged tree at the pinned SHA,
copy the ledger and verdict files read-only, run both validators,
print exit codes and the SHA. One small test: run it against the
closed R3-L3 ledger and confirm exit 0 from both validators, then
mutate one copied row and confirm a nonzero exit. Delivery path: script
committed to todolist-push under rung3-ci/, test result and the final
R3-L3 validation logged to the master event log. If Council A keeps a
ledger watch alive for future runs, its body is updated to call this
script instead of running validators in-tree; if Council A retires
the watch, the script remains as the manual check. No blanket approval
to execute worktree code is recorded anywhere.

---

## Item 3 (R10): durable Cloudflare direction

### Owner criterion (fixed 06:20 to 06:21 27/11, recorded verbatim in sense)

The Cloudflare fix must work so that when a normal user opens Zen and
searches and browses like normal, Cloudflare does not block them; AND
agents can still be called to use computer-use on Zen at any time; AND
agents still use Zen optimized for AI. Human browsing in Zen must
present as a normal browser to Cloudflare (no automation signals such
as navigator.webdriver leaking to pages), while agent computer-use
control of the same Zen stays available at any time and the AI
optimization of Zen stays. Owner addendum 06:21 27/11: "Can thi build
cong cu rieng" (if needed, build a dedicated tool). Standing design
principle: his machine is AI-optimized but the repo must work on stock
apps; machine optimizations go in the repo only as OPTIONAL (opt-in,
default off).

### Proposed decision (BUILD vs ADAPT: staged, with a build trigger)

Stage 1 now (adapt and diagnose, no new tool): keep the already
integrated residue (pinned shim hash, probe result in every drive
report, dirty probe equals stop) as the interim agent-side guard, and
run a read-only investigation on the laptop to answer two questions:
(a) which exact launcher flag or flags force navigator.webdriver to
true, and can that forcing be removed or conditioned without losing
agent attach; (b) why the probe disagreed across paths (webdriver
true via one eval path on R3-100, false via the probe elsewhere).
Stage 2 (decision gate, decided by Stage 1 evidence): if a launcher
flag change makes human launches present clean while agent attach
still works on the same Zen, adopt the flag change and do not build.
If the flag is inseparable from agent availability (automation
endpoint on means webdriver true for every page, human or agent),
then BUILD a dedicated automation-fingerprint hiding layer for Zen,
scoped below. Explicitly rejected as the durable direction: (1) shim
as brief discipline for agent drives only, because it leaves human
browsing flagged and fails the criterion; (2) shim shipped default-on
in the repo, because it violates the opt-in default-off principle and
ships an inconsistently probed workaround as trusted tooling;
(3) splitting the daily browser from the automation browser as the
primary route, because the criterion requires one Zen that is both
human-normal and agent-controllable with session continuity, and a
split breaks owner-session continuity (logged-in tabs live in one
profile, agent tasks need them in the other). The split stays
documented as a fallback only if the build fails its live test.

### Build scope (only if the Stage 2 trigger fires)

What the tool does: normalizes page-visible automation signals in Zen
so pages see a normal browser. Concretely, it ensures
navigator.webdriver reads false to page JavaScript, plus any further
page-visible signals that the unified probe proves are leaking (the
probe defines the list; the tool fixes exactly what the probe
measures, nothing speculative). It ships with the probe itself as a
command: clean or dirty, fail-loud. For agents, dirty still means
stop. For human browsing, the layer is simply present in his Zen
profile so normal browsing presents clean without the human doing
anything.

What the tool does not do: it does not solve CAPTCHAs, does not
rotate or spoof IP addresses, does not spoof TLS or network
fingerprints, does not imitate human behavior, and does not promise
that Cloudflare will pass any given visit. Cloudflare weighs more
than webdriver (IP reputation, behavior, challenge history); this tool
removes the automation signals we control and proves it with the
probe. Anything beyond that is out of scope and would need a new
decision.

Where it lives: the active configuration lives on his machine layer
(his AI-optimized Zen on the laptop), because that is where the
criterion must hold. The repo carries the tool only as OPTIONAL
opt-in, default off: a script plus README under scripts/ (or the
existing holder's home), clearly marked machine-optimization, with
the probe test included. Stock repo installs never enable it. This
matches the standing design principle exactly.

First concrete step (Stage 1, starts immediately): an SSH-capable
worker (not Clone1, Clone2, Mei, or Mochi, who have no SSH) runs the
read-only investigation on the laptop in a throwaway profile: read
the launcher and zen_cli launch path, list every flag, launch Zen
with and without each suspect flag, and record navigator.webdriver
from page context each time; then reproduce both probe paths on one
session and explain the disagreement. Deliverable: a short report
naming the flag or flags, whether agent attach survives without them,
and one unified probe. Delivery path: report committed to
todolist-push under improvements/, findings logged to the master
event log. No launcher change and no build until that report lands.

### Rationale

The criterion has three legs and most cheap routes break one leg. The
current shim residue protects agent drives that remember to use it,
but a human opening Zen to search does not run a brief or a probe, so
shim-as-discipline fails leg one. Shipping the shim default-on in the
repo would protect drives by default but breaks the repo design
principle and, worse, the probe that certifies the shim currently
disagrees with itself, so default-on would manufacture false
confidence (redteam section 1.9). A browser split satisfies leg one
for the human profile but breaks the same-Zen and session-continuity
requirement in spirit and in practice. The only routes that can
satisfy all three legs are removing the signal at the source (flag
fix) or hiding it in the browser itself for every page (dedicated
layer). Stage 1 finds out which of those is real. Ponytail says try
the flag fix first because it is the smallest complete change; the
owner's build authorization covers the case where the flag fix is
impossible. Building before Stage 1 would spend maintenance budget on
a tool that a one-line flag change might make unnecessary.

### Evidence

- VERIFIED: the automation wrapper flags force navigator.webdriver
  true on every launch even with no client connected (council1 Rank
  11, citing daily note 2026-11-25.md line 829, root cause entry).
- VERIFIED: a shim was proven live and probe-clean repeatedly, with
  the pill visible for the whole drive and no bot block (council1
  Rank 11, citing 2026-11-26.md line 712).
- VERIFIED: the holder artifact exists in the worktree at
  improvements/fixb-evidence/holder-fixb.mjs with probe and drive logs
  beside it (directory listing 27/11; redteam section 1.9 confirms
  the same path and corrects the /tmp-only claim).
- VERIFIED: the safe residue is already integrated (hash pin in
  probe, probe result in every drive report, dirty probe equals
  stop) per the review R10 row and integration log commit 27da702d.
- VERIFIED: probe inconsistency is real and unexplained: webdriver
  true via zen_dom eval on R3-100 at 03:16:07 versus probe-clean
  false on R3-028, R3-029, R3-035, R3-036, R3-046, R3-049 (council2
  Rank 18, citing drive report R3-100 anomaly 3 and coordinator
  notes).
- VERIFIED: the durable browser split was researched and deferred,
  not adopted (council1 Rank 11, citing 2026-11-25.md line 1387).
- ASSUMED: the flag forcing webdriver is tied to the automation
  endpoint (Marionette or BiDi remote debugging) being enabled at
  launch, which is what makes agent attach possible at any time.
  Verify by: Stage 1 flag-by-flag launch test in a throwaway
  profile. If the assumption is wrong and the flag is separable,
  Stage 2 takes the flag-fix branch and no build happens.
- ASSUMED: Cloudflare blocks in this setup are driven mainly by the
  webdriver signal rather than IP reputation or behavior. Verify by:
  Stage 1 and the Stage 2 live test (human-path browsing of a
  Cloudflare-protected site with the probe clean). If blocks persist
  with a clean probe, the tool scope statement already excludes
  promising a pass, and the team reports that honestly instead of
  expanding evasion scope silently.

### Risks

- Arms-race maintenance: fingerprint hiding decays as detection
  improves. Mitigation: the probe is the contract; when the probe
  goes dirty, the tool is known-broken rather than silently broken,
  and maintenance is a probe-driven fix, not guesswork. Honest cost:
  expect periodic small fixes; budget them as machine-layer upkeep,
  not repo releases.
- False confidence: a clean webdriver probe does not mean
  Cloudflare will pass. Mitigation: scope statement above; drive
  reports keep recording probe result and actual block outcomes
  separately.
- Scope creep into challenge defeat: the line between presenting as
  a normal browser and defeating bot challenges must hold.
  Mitigation: the does-not-do list is part of the decision; anything
  beyond signal normalization needs a new team decision.
- Build cost if triggered: a preload or profile-level layer plus
  probe plus tests is days of work, not hours, and touches his daily
  browser. Mitigation: Stage 1 gate exists precisely to avoid
  building if a flag fix suffices; the live test (below) must pass
  on a throwaway profile before his real profile is touched.
- Human-path test disturbance: live tests on his Zen risk focus
  theft. Mitigation: throwaway profile first, per standing rules;
  real-profile verification only at a task boundary with the pill
  visible.

### Concrete next action

Stage 1 investigation as specified above (SSH-capable worker,
throwaway profile, read-only, report to todolist-push improvements/
plus master event log entries for the full chain). The coordinator
then applies the Stage 2 gate: flag fix if separable, build if not.
Whichever branch lands, acceptance is a user-path test, not an
internal check: open Zen the normal way, search on the web, browse
to a Cloudflare-protected site by clicking like a normal user (no
deep links, no direct commands, no internal setters), confirm no
block, then call an agent computer-use drive on the same Zen session
and confirm control works with the pill visible. Evidence shows
entry, path, action, and resulting state. Repo side, if anything
lands, is opt-in default off with the probe test; machine side is
his laptop Zen configuration. Log every step via log-event.sh.

---

## Item 4 (R16): browser restart authority

### Proposed decision

No watch gets autonomous browser restart authority. Adopt the middle
path: a memory threshold alert (read-only) plus a boundary-only
restart procedure that a coordinator or human agent initiates
deliberately, never a cron watch. The procedure runs only at task
boundaries, never mid-drive, and includes a session-restore
checklist: record open tabs including pinned and essential tabs
before restart, restart through the wrapper, then verify ports, pill,
session restore, and owner essentials present after. The R6
tab-cleanup guardrail applies throughout: a restart never closes
owner tabs as a side effect, and any tab handling uses the recorded
allowlist method only.

### Rationale

Restarting the browser is destructive to session state, and the
owner's tabs are exactly what automation has already hurt once (the
24-tab over-close that created Task 56). Watches in this system are
simple loops with a proven false-alarm and co-death record (R1 false
liveness alarms, R15 co-deaths); giving such a loop kill power over
the owner's browser repeats the R6 failure class with a bigger blast
radius. The one manual restart that was done mid-run worked and
restored the session, which proves the procedure path, not the
autonomous path. An alert gives the coordinator lead time to call a
boundary early; that is the smallest change that addresses the real
risk (memory exhaustion) without creating a new authority. Ponytail:
procedure plus alert before any new power.

### Evidence

- VERIFIED: Zen memory grew to about 8.11 GB during the run and a
  deliberate restart cut RSS from 7950 MB to 978 MB with ports and
  session restored (council2 Rank 17, citing coordinator notes
  25/11 17:02 and 17:05).
- VERIFIED: the browser died near closure (alive 04:12:31, gone by
  04:13:52 on 27/11) and recovered as a fresh process at 1.40 GB
  versus 3.79 GB before; the health watch did not restart it, by
  design (council1 Rank 18, citing daily note 2026-11-27.md line 81
  and the 04:27 entry).
- VERIFIED: tab cleanup cut memory by about 3.5 GB, showing
  accumulation is partly tab-driven (council1 Rank 18, citing
  2026-11-26.md line 125). Memory management and tab handling are
  coupled, which is why restart authority and the R6 guardrail must
  be decided together.
- VERIFIED: one cleanup batch closed 24 tabs including 5 essentials
  and 3 pinned, creating counted Task 56 (review R6 row; council1
  Rank 4). Owner-tab loss by automation is an observed failure, not
  a hypothetical.
- VERIFIED: the session-store decoder was missing on the laptop
  (lz4 module absent, decode failed), so session-restore tooling is
  fragile (council1 Rank 22, citing 2026-11-27.md line 90; review
  R20). A restart procedure cannot assume restore tooling works; it
  must verify.
- ASSUMED: a threshold around 8 GB RSS gives enough lead time before
  exhaustion on his machine. Verify by: recording RSS at task
  boundaries for the next run and checking headroom. The exact
  number is tunable; the decision is alert plus procedure, not the
  number.

### Risks

- Memory exhaustion between boundaries if growth is fast.
  Mitigation: the alert fires on threshold crossing, and the
  coordinator may call an early boundary; growth observed was about
  4.8 GB per hour at worst (council2 Rank 17), which an hourly or
  boundary check catches.
- Procedure depends on a coordinator or human agent being available.
  Accepted: the run is closed, and future runs have a coordinator by
  design. An unattended browser that needs a restart and waits is
  safer than an unattended watch that restarts wrongly.
- Session restore could still lose tabs despite the checklist.
  Mitigation: record-before-restart plus verify-after, and a
  throwaway-profile drill before the procedure is trusted on the
  real profile.

### Concrete next action

Coordinator writes the boundary restart procedure into the laptop
machine layer and the brief template (threshold, record step,
restart step, verify step, R6 guardrail reference). The health watch
gains a read-only RSS alert line only; no restart command is added to
any watch body. One small test before real use: throwaway-profile
drill (open recorded tabs including a pinned tab, run the procedure,
confirm restore and pill). Delivery path: procedure committed to
todolist-push (generic text) plus machine-layer copy on the laptop;
drill result logged to the master event log. Live machine steps go
to an SSH-capable worker.

---

## Item 5 (R22): PII scan loosening

### Proposed decision

Approve only the narrow manual-review class proposed by council2,
implemented as an auditable process beside the scanner, with the
scanner itself unchanged. The class covers exactly one rule:
owner-url hits where the URL is a task-created document (created by
the task itself, evidenced in the drive report). Each use requires
coordinator sign-off recorded in the snapshot manifest (who, when,
which URL, URL hash) and a master event log entry. Sign-off never
overrides the credential, email, phone, known-token-prefix, or
high-entropy rules. Reject any allowlist or sign-off override for
high-entropy strings: held-out logs stay held out, or the runner
redacts them before sealing. Default stays conservative everywhere
else.

### Rationale

The scanner is the deterministic block the standing rules require;
loosening the scanner code would weaken every future snapshot to fix
a handful of false positives. The observed false positives split
cleanly: task-created doc URLs are explainable and auditable (the
task made the doc, the report proves it), while high-entropy hits in
raw logs are exactly the shape of real secrets and cannot be
distinguished from them by a reviewer glancing at a string. So the
narrow class buys back evidence completeness where provenance is
provable, and refuses it where it is not. Keeping the scanner
unchanged means the gate still exits 1 on these URLs; the sign-off
is a separate recorded human decision to push that specific URL,
which is auditable and revocable, instead of a silent code exception.
Ponytail: process beside the tool, not surgery inside it.

### Evidence

- VERIFIED: pii-scan.py is a deterministic gate (exit 1 on any hit)
  with rules for credential assignments, emails, phones, owner tab
  URLs (mail, calendar, drive, docs hosts and account path segments),
  known token prefixes, and high-entropy strings over 20 chars with
  entropy over 4.5 (direct read of rung3-ci/pii-scan.py 27/11,
  including CRED_RE, OWNER_HOSTS, TOKEN_RE, and the entropy check).
  The docs-host rule is precisely what flags task-created docs.
- VERIFIED: raw runner logs were held out of two snapshots after
  high-entropy hits (R3-067 and R3-072), and manual review passed
  three more hits on task-created doc URLs and demo-store routes;
  no leak occurred (council2 Rank 21, citing per-task log blocks and
  coordinator notes 26/11 12:46, 13:22, 14:04).
- VERIFIED: standing rules require no personal info on GitHub and a
  deterministic pre-push block, not prompt-only rules (MEMORY.md
  standing rules; review R22 row marks this security-shaped with a
  conservative default).
- ASSUMED: task-created doc URLs in evidence contain no personal
  data beyond the doc identifier itself. Verify per use: the
  sign-off step includes opening the URL class check (task-created
  per drive report) before signing; a URL that is not provably
  task-created does not enter the class.

### Risks

- Sign-off becomes a rubber stamp under time pressure. Mitigation:
  per-URL sign-off (no batch approvals), coordinator must differ
  from the runner, every sign-off logged and therefore auditable by
  redteam or a later review; the class is void if sign-offs appear
  without the drive-report provenance.
- A task-created doc could later be edited to contain personal data,
  making an old sign-off stale. Mitigation: sign-off covers the URL
  as evidence of the task at seal time; the snapshot stores the URL
  string, not live doc content, so later edits do not retroactively
  leak through the snapshot. Noted here so the redteam can attack
  the residual (anyone with the URL could open the live doc), which
  is why the class is limited to docs the task created for the task,
  never owner docs.
- Precedent creep toward broader classes. Mitigation: this decision
  names the one eligible rule; any new class needs a new team
  decision, not an extension of this one.

### Concrete next action

Coordinator documents the class in the rung3-ci README and the
snapshot checklist (eligibility, sign-off fields, logging). No change
to pii-scan.py. One small test: a fixture snapshot with a
task-created doc URL plus a recorded sign-off passes the process;
the same URL without sign-off blocks; a high-entropy fixture blocks
even when a sign-off is attempted. Retroactively log the three
already-passed manual-review cases from the run into the master
event log so the record is complete. Delivery path: docs committed
to todolist-push; test result and retroactive entries logged via
log-event.sh.

---

## Item 6 (R15): speed-daemon supervision

### Proposed decision

Instrument now; do not change supervision yet. Add three small,
append-only instrumentations and keep the current supervisor loop
exactly as is while they run: (1) daemon exit-reason logging (an exit
event with signal or reason written to daemon.log, so deaths stop
being silent); (2) supervisor heartbeat (watchdog.py logs a periodic
heartbeat line to watchdog.log even when the daemon is up, so
supervisor silence becomes distinguishable from daemon health);
(3) double-start contention logging (record when a start attempt
finds the socket already bound, since daemon.out already proves
double-starts happen). Revisit the supervision decision when either
trigger fires: instrumentation has captured at least two deaths with
named causes, or seven days of heartbeat data exist, whichever comes
first. Before any service-manager move is even proposed at that
point, verify read-only whether a user service manager exists on the
current VM, because supervisor.sh records that this VM has no cron
daemon and no user systemd bus; if that is still true, the
service-manager route is unavailable and the alternative to evaluate
is the runtime cron check-once pattern already used elsewhere
(watchdog-liveness-check). Explicitly rejected now: any supervisor
rewrite or service-manager migration before diagnosis.

### Rationale

Every reviewer agrees the cause is unknown, and the review's rejected
list states the reason plainly: a blind supervision change can mask
the cause or double-start. The double-start risk is not theoretical;
daemon.out contains two address-already-in-use tracebacks. The
co-death pattern (daemon and supervisor dead together at least three
times) looks like shared fate, but at least one of those was a VM
replacement, which kills every process regardless of supervision and
which no service manager on the same VM would survive either. Without
exit reasons, the team cannot tell VM replacement, OOM, socket
cleanup, and plain crashes apart, and each cause wants a different
fix. Instrumentation is the smallest change that converts the next
deaths into evidence. It also fixes a real observability hole found
while reading: supervisor.log is empty by design (watchdog output
goes to watchdog.log), and watchdog.py logs only when the daemon is
down, so a dead supervisor and a healthy daemon currently look
identical (silence).

### Evidence

- VERIFIED: daemon.log contains 46 daemon_start events (grep count
  27/11). The review and redteam cite 45 starts verified; the
  current log includes a further start at 05:42 to 05:43 on 27/11,
  after the review count, which reconciles the difference. Either
  way, dozens of starts with no recorded exit reasons.
- VERIFIED: daemon.log tail shows repeated daemon_start events with
  no preceding exit or death event, plus recurring
  heartbeat_master_dead entries (rc 255) on the master side (direct
  read 27/11). Deaths are silent in the log today.
- VERIFIED: supervisor.log exists and is 0 bytes (ls 27/11), and
  supervisor.sh shows why: the supervisor loop redirects watchdog.py
  output to watchdog.log; supervisor.log captures only the shell
  loop's own output. Empty supervisor.log is therefore expected and
  is not evidence the supervisor is dead. watchdog.log's last
  entries are from 25/11 (direct read), and watchdog.py logs only
  on daemon-down events, so supervisor liveness is currently
  unobservable. This refines the review's "supervisor log empty"
  shorthand.
- VERIFIED: daemon.out contains two OSError address-already-in-use
  tracebacks from daemon.py bind (direct read 27/11). Double-start
  attempts already occur.
- VERIFIED: supervisor.sh header records that this VM has no cron
  daemon and no user systemd bus, which is why supervision is a
  detached shell loop; it also records the caveat that a VM
  replacement kills daemon and supervisor together (direct read
  27/11).
- VERIFIED: co-death occurred at least three times in the slice (VM
  replacement 26/11; 01:42 and 03:42 on 27/11) per council1 Rank 17
  citing daily notes.
- ASSUMED: some deaths are VM replacements and some are not; the
  split is unknown. Verify by: exit-reason logging plus heartbeat
  gaps correlated with VM replacement records. The supervision
  decision at the trigger point depends on this split.

### Risks

- Instrumentation changes timing and could mask a race. Mitigation:
  append-only logging at exit and heartbeat points, no lifecycle or
  restart-semantics change; the supervisor loop body is untouched
  except for the heartbeat line inside watchdog.py.
- Deaths may be rare after instrumentation, delaying the trigger.
  Mitigation: the seven-day heartbeat trigger bounds the wait; if
  nothing dies in seven days, that itself is evidence the problem
  was environmental (for example VM replacements during the run).
- A future service-manager proposal could still be made blindly at
  the trigger point. Mitigation: the decision rule is recorded
  here: named causes first, service-manager availability verified
  read-only, kill test required (kill daemon, confirm restart
  within one cycle; kill supervisor, confirm daemon survives) before
  adoption.

### Concrete next action

A VM-side worker (the daemon lives on the VM; no laptop SSH needed)
adds the three instrumentations: exit handler in daemon.py writing
one JSON exit line to daemon.log, heartbeat line in watchdog.py
every cycle or every N cycles, contention line in daemon.sh or
daemon.py on bind failure. One small test: kill the daemon and
confirm an exit line appears; stop the supervisor and confirm
heartbeat lines stop within two cycles; start a second daemon and
confirm a contention line appears. In parallel, the coordinator
verifies read-only whether a user service manager exists on the
current VM and records the result. Delivery path: changes committed
to todolist-push under the speed-daemon directory (or its repo home),
test results and the availability check logged to the master event
log with the full chain. The supervision decision itself is
re-opened only at the stated trigger.

---

## Summary of proposals

- Item 2 (R19): clean-checkout validation at a pinned SHA as the
  standing posture; no blanket in-tree execution approval; one final
  clean validation seals R3-L3.
- Item 3 (R10): staged route against the owner's fixed criterion.
  Stage 1 read-only flag and probe investigation now; Stage 2 gate:
  flag fix if separable, otherwise build a scoped fingerprint-hiding
  layer (machine layer active, repo opt-in default off). Shim-only
  for agents, default-on repo shim, and browser split as primary
  route are rejected.
- Item 4 (R16): no autonomous restart authority for any watch;
  threshold alert plus boundary-only, agent-initiated restart
  procedure with session-restore checklist and R6 guardrail.
- Item 5 (R22): narrow manual-review class for task-created doc URLs
  only, as an auditable sign-off process beside an unchanged
  scanner; no high-entropy allowlist or override, ever.
- Item 6 (R15): instrument now (exit reasons, supervisor heartbeat,
  contention logging), supervision unchanged, decision re-opened at
  a concrete trigger (two named-cause deaths or seven days of
  heartbeat data), service-manager availability verified before any
  such proposal.

# Redteam attack on Worker Y8 E1 comparison design (Worker Y8 redteam)

Status: PAPER ATTACK ONLY. No Zen driving, no tab opened, no infra started, no executor run.
Target: `improvements/worker-y8-e1-comparison-design.md` (DRAFT, pre-registration).
Read alongside: `improvements/worker-x-e1-experiment-report.md` (deliberation measured),
`improvements/worker-y4b-hidden-body-root-cause.md` (hidden-body incident; V2 dead),
`improvements/worker-x-e1-plan-test-05.md` (the merged 58-step plan),
`improvements/worker-x-e1-executor-a-brief.md` and `worker-x-e1-executor-b-brief.md`,
`tests/realistic/agy-q2/test-05-contact-book.md` (28 spec steps, expected 150 s, max 260 s),
`improvements/worker-x-e1-step.sh` (30 s driver timeout, 10 s FIFO write timeout).

Method: attack the design as written. Every attack names the exact rule or step,
a concrete scenario producing a wrong verdict, and the fix that closes it.
Severity: S1 means the verdict as written can be false and the design cannot detect it.
S2 means a material bias or loophole that can swing the verdict. S3 means a gap that
should be closed before running, but alone does not flip the verdict.

## Ranked attacks

### S1-1. The total-speed win criterion is mathematically unwinnable for B

Rule attacked: "SPEED (total): B wins ONLY if B total (deliberation + merge + B execution)
< A total (A execution)."

Scenario: deliberation plus merge is already sunk at about 10 m 40 s (640 s).
The spec states the task's expected duration is 150 s and its maximum allowable
latency is 260 s. A normal A execution is therefore about 150 to 260 s.
B total is 640 s plus B execution, so B total is at least 640 s.
B wins on total speed only if A execution exceeds 640 s plus B execution,
that is, only if A takes more than about 10 m 40 s on a task whose own max is 260 s.
Unless A catastrophically exceeds its max latency by 2.5x, B loses total speed
by construction, before either arm runs. The criterion is not a test, it is a
foregone conclusion dressed as a win condition, and a reader will cite
"B lost on total speed" as if the experiment had decided something.

Fix: admit total speed is decided before the arms run and make execution-only
speed the primary speed question, with total speed reported as arithmetic, not as
a contest. Or pick a task long enough that the 640 s overhead is plausibly
recoverable (A execution would need to be well over 15 minutes for B to have a
real chance). Do not keep a win criterion no honest run can satisfy.

### S1-2. Pre-flight diagnoses the wrong tab; the executor tab is never diagnosed

Rule attacked: pre-flight section, "The pre-flight tab is closed after diagnose;
each executor opens its own fresh tab afterwards."

Scenario: pre-flight opens tab 1, diagnoses VISIBLE, closes it. The executor
then opens tab 2. Y4b establishes the hidden-body state is per tab load:
about 6 of 6 new tabs hid in incident 2 while a reused tab in the same probe
stayed visible, and the stall is per-load and random. A VISIBLE verdict on tab 1
says nothing about tab 2. The executor's tab can hide, the executor then reads
an empty `#contacts-count`, fails its checks, and the arm records a FAIL,
or the coordinator declares it infra-blocked after the fact with full knowledge
of the outcome (see S1-4). Either way the gate that was supposed to protect the
arm measured a sacrificial tab and never measured the tab that did the work.

Fix: diagnose the executor's own tab, not a sacrificial one. The executor's
first driver actions must be the diagnose snapshot on its own tab before any
task step, with the result recorded in the run log. If that tab is hidden, the
recovery ladder applies to that tab and the arm is flagged or blocked on its own
evidence. A pre-flight on a different tab can stay as an infra smoke check, but
it must never be recorded as "this arm's browser was healthy."

### S1-3. Information isolation is unenforced and unaudited; A can read B's plan

Rules attacked: A brief, "Do NOT read any other agent work. Do NOT read
/tmp/e1/plans/ or any plan file." B brief, same ban. Design, "It never sees the
spec or fixture" (B) and "1 fresh executor reads spec + fixture" (A).

Scenario 1, false win for A: the merged plan is committed in the same repo
the A executor reads from: `improvements/worker-x-e1-plan-test-05.md`.
The ban cites `/tmp/e1/plans/`, a path that does not exist in the record
(X report puts drafts and plan in `/tmp/e1/` directly). A fresh codex process
with `danger-full-access`, told to read the spec and fixture from the repo tree,
can list the repo, grep for selectors, or stumble on the plan file by ordinary
exploration. Nothing in the design audits which files the executor read,
no file-access log is required, and no check compares A's actions against the
plan. A could execute B's 58-step plan while credited as DIRECT, and the
verdict would record a win for direct execution that was in fact plan execution.

Scenario 2, same hole from the other side: X's report notes delib-1 took
198,978 input tokens "because codex loads large cached context per run."
The design asserts "A fresh codex exec process has no memory of the task or
of other agents" but offers no evidence, while X's own token counts suggest
cached context persists across codex invocations on the laptop. If that cache
carries deliberation content into an executor, isolation is broken before the
brief is even read, for either arm, and neither arm's result is attributable
to its condition.

Scenario 3, false win for B through the plan's own content: the plan's
"Fixture facts" section hands B, pre-digested and pre-verified, every runtime
fact A must extract itself from the fixture HTML: Bob's preloaded phone
+1-555-0102, the star is a span and needs click_js, delete has no confirmation,
selects are set by JS value plus change event, search filters live on input,
the exact banner text, the slug rules, the render template's lastElementChild
trick, the notes selector. The plan also hands B the exact JSON for all 58
commands, so B's per-step decision cost is zero. That is the treatment, not an
accident, but the design cannot distinguish "deliberation found the truth"
from "three deliberators cross-checked each other and the merge voted on it."
The confound is attribution: a B win could be the plan, the 3-way cross-check,
or the merge, and the design has no arm that separates them.

Fix: (a) name the real paths in the ban: `/tmp/e1/plan-test-05.md`,
`/tmp/e1/draft-*.md`, and `improvements/worker-x-e1-plan-test-05.md`,
and require the coordinator to audit the executor's --json event stream for
reads of those paths before accepting the run; (b) verify codex cache isolation
before running (clear or disable the cache, or run executors with a flag that
prevents cached-context loading, and record the input-token count per executor
as a check against X's 198,978-token anomaly); (c) freeze the brief md5s as
well as the plan md5 (see S2-6); (d) record the attribution limit in the
verdict: a B win is a win for "plan plus 3-way cross-check plus merge,"
not for deliberation in general.

### S1-4. The coordinator is unblinded judge, plan author, and classifier

Rules attacked: "The comparison of 'plan followed verbatim' is decided by the
coordinator reading the B run report against the plan file"; invalid-run rules
(INFRA, DRIVER DEAD, crash); "A deviation forced by a PLAN DEFECT is logged
as a defect, not as executor improvisation"; FLAGGED pass accounting.

Scenario: the same coordinator merged the drafts into the plan (X report),
runs both arms, reads A's full report before launching B, and then decides
every borderline call: whether a hidden tab was OTHER_HIDDEN or FIXTURE_FAILURE,
whether a step.sh timeout was DRIVER DEAD or executor error, whether a B
deviation was "forced by a PLAN DEFECT" or improvisation, whether a flagged
pass still counts as a pass for the accuracy rule. The coordinator has a stake
in B (their merge) and full knowledge of which arm produced which result when
deciding. A B failure can be reclassified as infra-blocked (INVALID, re-run)
while an identical A failure stands as FAIL, and no rule in the design would
catch it, because the classification rubric for borderline cases does not exist.

Fix: blind the judging. An independent judge (not the merging coordinator)
decides PASS/FAIL, errors, deviations, and invalidity from arm-labelled-stripped
evidence: out.log command streams plus the __agyVerify JSON. Pre-register the
classification rubric for the borderline cases before running: exact conditions
under which a timeout is DRIVER DEAD, under which a hidden tab is INFRA vs
FIXTURE_FAILURE, and under which a deviation counts as PLAN DEFECT
(selector not found after the allowed retry, check differing after the allowed
retry, and nothing else). The coordinator runs infra; the judge decides verdicts.

### S1-5. The error and recovery metric is undefined and structurally biased toward A

Rules attacked: metrics "Errors: count of {"ok": false} driver results",
"Recovery steps: retries + fallbacks + re-finds"; win criterion "both pass AND
B has strictly fewer errors + recovery steps than A."

Scenario 1, unequal denominators: B's plan mandates 58 driver commands and
about 15 exact-value check steps. A's executor doing the 28 spec steps needs
roughly 35 commands and chooses its own checks. B has about twice as many
opportunities to record an ok:false, a failed check, or a retry. Raw counts
compare an arm that does more work against an arm that does less, and punish
the arm that checks more. B can execute perfectly per command and still lose
on raw counts to an A that verified less.

Scenario 2, triple counting: one incident, a real click failing, then a
click_js fallback succeeding, is simultaneously an "error" (ok:false), a
"misclick / failed click", and a "recovery step" (fallback). The design gives
no rule against counting the same incident three times in the "errors +
recovery steps" sum, and no operational definition of a recovery step at all.
Worse, B's plan mandates re-finds as normal steps (step 25 find phone again,
step 28 find Save again, step 39 find search again). A naive counter that
treats a find after a re-render as a "re-find" scores B's ordinary plan steps
as recovery. Conversely, if re-finds are not counted, the metric is whatever
the executor chose to report.

Scenario 3, self-report: counts come from "the executor report + /tmp/e1/out.log
lines" with no stated reconciliation rule and no independent counter. The
executor reports its own errors. An executor that under-reports looks better,
and the coordinator reading the report is the same unblinded coordinator from
S1-4. Out.log is append-only and shared across pre-flight, A, B, and retries,
with no per-arm line ranges recorded, so "out.log lines" cannot even be
attributed to an arm without reconstruction.

Scenario 4, baked-in asymmetry on the star: B's plan step 31 uses click_js
directly and never attempts a real click, so B can never record a misclick
there. A's brief says "prefer click_js for the star icon if a real click
fails," which tells A to try the real click first and eat the failure. The
same asymmetry holds for the select and search-clear event dispatches:
B's plan pre-dispatches input/change events (steps 16, 41, 42, 44) while A
must discover that Marionette clear does not fire the input event. B avoids
whole error classes by construction, and the design scores that avoidance as
accuracy.

Fix: define the metric operationally before running: one incident counts once,
under one category, with a written category table; count errors and recovery
from out.log mechanically (driver-side, per-arm line ranges snapshotted at arm
start and end), never from the executor's self-report; compare error RATES
(errors per driver command, check failures per check performed), not raw
counts; and record that B's click_js-first and pre-dispatched events are
plan-given advantages, so a B accuracy win on those steps is a plan win, not
an executor win.

### S1-6. The retry budget stacks per failure mode, which is a re-run-until-win lever

Rules attacked: INFRA "Retry the whole arm once after 5 min";
DRIVER DEAD "Retry once from scratch after infra restart";
crash "INVALID and is re-run once from scratch."

Scenario: the three "once" rules are per failure mode, not per arm. An arm
can be retried three times in sequence: once for infra, once for driver-dead,
once for a crash, each time with a fresh draw from executor nondeterminism
plus infra luck. A coordinator who wants B to win never needs to cheat openly:
each B failure gets a plausible reclassification into the next unused retry
bucket (S1-4 supplies the classification discretion), while A's failures stand.
With n=1 and a nondeterministic executor, repeated draws until a pass is a
selection effect, not a measurement. The design also never says whether the
failed attempt's wall time, the 5-minute wait, or the failed attempt's errors
count toward the arm's totals: a 5-minute wait alone exceeds the whole task
time and could decide the speed verdict by itself, in either direction,
depending on which arm's retry clock is counted.

Fix: one retry budget per arm, total, across all failure modes, pre-registered;
a second failure of any kind ends that arm as BLOCKED, not as a fresh draw.
Pre-register that all retry waiting time and all failed-attempt wall time count
toward the arm's total wall time (a retry is never free time). Log every
attempt, including discarded ones, with its wall time and its classification,
in a file the judge can read.

## S2 attacks

### S2-1. Wall-time boundaries are undefined, and the two clocks disagree

Rules attacked: "Wall time: executor-recorded start/end (date in the brief) AND
coordinator-observed launch-to-final-report wall. Both stated."

Scenario: the executor's first action is `date`, but codex reads the brief and
the inputs before its first tool call. A reads a 67-line spec plus the fixture
HTML plus hand_drive.py; B reads a 22,145-byte plan plus hand_drive.py. That
reading and reasoning time, which differs systematically between arms, falls
outside the executor-recorded wall if the date command runs after reading,
or inside it if the date runs first; the brief does not pin the order, and
codex may read inputs before obeying the "first action" instruction anyway.
Meanwhile the coordinator-observed clock includes process spawn, model startup,
and the latency of the final report message, plus any coordinator delay between
launch and observation. Two clocks, two different inclusions, no rule for which
one decides the verdict when they disagree, and no rule for what counts as the
start of B's execution (plan read? process spawn? first driver command?).

Fix: one primary wall clock, defined as coordinator-measured process spawn to
process exit, identical for both arms, and stated as the deciding clock.
Keep the executor-recorded times only as a cross-check, and pre-register the
tolerance at which a disagreement invalidates the run. Include per-arm overhead
identically: infra start, pre-flight, and executor wall all count for both arms;
deliberation plus merge count only for B.

### S2-2. PASS/FAIL verification is asymmetric; __agyVerify is blind to Frank's details

Rule attacked: "PASS/FAIL: decided ONLY from DOM reads + window.__agyVerify()
returned JSON, never from an executor claim."

Scenario: B's plan performs final reads at steps 48 to 56, including Frank's
name, group, email, phone, and notes (step 55), and step 56 requires
__agyVerify to return `passed: true`, `failures: []`, `score: 1`, and a state
object of `{saved, contactCount: 6, favCount: 1, bobPhone, banner}`. That state
object does not contain Frank's email, phone, notes, or group. A chooses its
own checks; A could add Frank with the wrong email or wrong notes, never check
those fields, and still pass __agyVerify, because the banner and the count do
not check Frank's details. Meanwhile B is held to the plan's 15 exact-value
checks, each a failure opportunity A never faces (S1-5 scenario 1). The design
claims one PASS standard but enforces two: a strict one for B, a self-chosen
one for A. An A pass and a B pass do not mean the same thing, so "both pass"
in the accuracy rule compares unlike outcomes.

Fix: one independent final verification, identical for both arms, run by the
coordinator or judge against the final DOM before tab close: a fixed read list
(Frank name/group/email/phone/notes, Bob phone, David favorite, Spam absent,
count, banner) plus __agyVerify, with the results recorded from out.log, not
from the executor's report. If the executor's own reads disagree with the
independent reads, the independent reads decide.

### S2-3. Pre-flight is a contamination vector, not just a gate

Rules attacked: pre-flight diagnose plus recovery ladder; "A pass achieved only
after the tz-hidden removal is a FLAGGED pass, counted separately in the summary."

Scenario 1, warm-up: pre-flight opens a tab, loads the fixture, runs evals,
and closes the tab, all through the same driver and Marionette session the
executor then uses. That settles the extension's async chain (fetch of
ContentScripts.json, storage.local.get), warms geckodriver and the fixture
server, and may cache the extension's settings read. The executor's tab then
loads in a settled environment a real user would not have. Pre-flight converts
a live defect into a non-observation for both arms, and because it runs before
each arm, it also makes the two arms look more alike than they are.

Scenario 2, observer effect: the diagnose eval reads computed visibility,
and Y4b establishes that getComputedStyle forces the style flush that starts
the transition. Measuring the hidden state can itself change the hidden state,
so the diagnose result is not a clean read of what the executor would have met.

Scenario 3, the flag does not touch the verdict: the accuracy rule is "both
pass AND B has strictly fewer errors + recovery steps than A." A FLAGGED pass
is not an error, not a recovery step, and not a failure under any stated rule.
A flagged B pass can therefore beat a clean A pass on error counts, and a
flagged A pass can beat a clean B pass the same way. The flag is "counted
separately in the summary" but has no defined effect on any win criterion,
so it is disclosure without consequence. Also ambiguous: the flag attaches to
the pre-flight tab, not the executor tab (S1-2), so it is unclear what a
flagged arm even means when the executor's own tab loaded clean.

Scenario 4, log pollution: pre-flight commands go through the same FIFO and
out.log as the executor's commands (the design says pre-flight runs "via the
E1 driver"). Its evals and its tz-hidden removal eval inflate the out.log
line count that the metrics section uses to count driver commands (S1-5).

Fix: (a) record pre-flight commands to a separate log, never out.log;
(b) define the flagged pass as a verdict input before running, for example a
flagged pass cannot win on accuracy over a clean pass, or a flagged arm is
reported as FLAGGED-PASS and excluded from the accuracy comparison;
(c) state explicitly that pre-flight warming is a known confound and that the
hidden-body defect is therefore unmeasured by this experiment, not absent;
(d) do not run the removal eval on any tab except the executor's own tab
once S1-2 is fixed.

### S2-4. Fixed order A-then-B, n=1, no meaningful-difference threshold

Rules attacked: "Order: A first, then B, never concurrent"; "n=1 per arm: one
run each, one task, one model. This is ONE observation"; win criteria as binary
WIN/LOSE.

Scenario: A runs cold (first Marionette session of the day on that driver,
cold extension chain, cold fixture server). B runs warm on every one of those
axes, plus B runs after A has already exercised the driver end to end. Any
B advantage in wall time or errors is indistinguishable from warm-state
advantage plus executor nondeterminism plus infra luck (a hidden-body window
hitting one arm and not the other). The design's scoping note ("ONE observation,
not proof") conflicts with the win criteria's binary language: a reader, and
the user, will cite "B wins on accuracy" without the scope. There is also no
minimum meaningful margin: a B win by 5 seconds on a 150-second task, inside
codex nondeterminism noise, counts the same as a win by 5 minutes.

Fix: counterbalance if a second pair is ever run (B-then-A), or at minimum
pre-register a meaningful-difference threshold (for example 60 s on wall time,
or a stated error-rate gap) below which the verdict is "no detectable
difference." Write the verdict in run-scoped language in the criteria
themselves ("B won this run on accuracy"), not as a general claim.

### S2-5. Owner-away gate not restated; no clean-slate rule after Y4d

Rule attacked: "E1 runs only after Worker Y4d reports its agy-q2 rerun complete."
(X report hold conditions are not restated in the Y8 design.)

Scenario: X's report holds E1 until (1) Y4 is done and (2) the user hands the
machine over again, and the 17:59 AGENTS.md rule forbids live tab driving while
the user is at the keyboard. Y8's design restates condition (1) but drops
condition (2). UPDATE 18:24, after this attack was drafted: MEMORY.md now
records the owner's standing order that from now on the machine is handed over,
he is out of the house and not touching the laptop, any signal saying he is
using it is a false signal, and work runs continuously with no idle check;
Y4d runs the agy-q2 rerun and Y8 runs E1 right after, one runner at a time.
That order closes the owner-away gap in substance, but it lives in MEMORY.md,
not in the Y8 design, so a reader of the design alone still cannot see the
gate or its scope. The clean-slate half of the attack still stands: no
geckodriver sweep and no tab inventory are required between Y4d's rerun and
E1-A, so E1-A could start with Y4d's warm driver, stale geckodriver, or
leftover tabs still in Zen.

Fix: restate the 18:24 handover order inside the Y8 design as the run gate,
with its scope (continuous running, no idle check, one runner at a time),
and add a clean-slate check (geckodriver ps table, port check, Zen tab count)
before A starts, recorded in the run log.

### S2-6. Unspecified fallback, unspecified infra handling between arms, stale verification

Rules attacked: "The two arms must use the SAME tab-acquisition method. If the
fresh-tab method fails for A and a fallback is used, the same fallback is used
for B"; "Verified inputs (18:24 +07, 21/11)" md5 list.

Scenario 1: no fallback is named anywhere in the design. The known candidate
is Y4b's bootstrap tab, whose evidence is n=1 confounded by time and whose
design requires an ownership check and a return to about:blank. If A needs a
fallback and B does not, the rule says B must use the fallback too, but the
fallback's own procedure, its verification step, and its effect on the
hidden-body rate are all unspecified, so the arms end up differing in an
unmeasured way while the design claims they used the same method.

Scenario 2: the design never says whether infra (driver, HTTP server,
geckodriver) is restarted between arms. If it stays up, B inherits A's session
residue; if it is restarted, the restart procedure and its timing are
unrecorded and could differ between arms. Either way the arms are not
provably in the same infra state.

Scenario 3: md5s were verified at 18:24, but the arms run later, after Y4d
and after handover. The plan, briefs, spec, and fixture could change in
between (the design file itself is still a DRAFT under debate). No re-md5 at
launch is required, and the briefs are not frozen at all: the coordinator
could clarify a brief after seeing A's confusion, handing B a better brief
while the plan stays frozen. The "frozen" claim then covers the plan but not
the instructions the executors actually read.

Fix: name the fallback and its procedure, or delete the fallback rule and
state that a fresh-tab failure blocks the arm; pre-register infra restart
between arms (restart, with the exact commands, or explicitly keep running,
with the reason); re-md5 spec, fixture, plan, and both briefs immediately
before each arm and abort on any mismatch.

### S2-7. Ambiguous-timeout retry can double-execute non-idempotent commands

Rules attacked: brief procedure 5 (A) and plan check rules (B): "On any
{"ok": false}: retry the same command once"; step.sh 30 s timeout.

Scenario: a click on Save or Delete can succeed in the browser while its
response is lost (30 s timeout waiting for driver output). The executor sees
ok:false, retries the same click. The modal is already closed or the contact
already deleted, so the retry clicks a stale element id, or worse, the id has
been recycled and the retry clicks a different control. The design treats
every ok:false as "command did not run" and mandates a blind retry, with no
distinction between a clean failure (element not found, nothing happened) and
an ambiguous timeout (unknown whether it ran). A double Save could add a
duplicate Frank; a double Delete is idempotent only by luck of the re-render.

Fix: split the retry rule. Clean failures (element not found, ok:false with an
error that proves non-execution) may retry once. Ambiguous timeouts must
re-read state first (eval the DOM) and retry only if the state shows the
command did not take effect. Record every ambiguous timeout separately.

## S3 attacks

### S3-1. The sunk-cost bar is fuzzy and cost-blind

The 640 s bar rests on merge time "about 2 min," bounded only by file mtimes
(18:03:48 to 18:05:50) and including coordinator fetch time. The bar is fuzzy
by tens of seconds, and deliberation cost is counted only in wall time:
463,124 input tokens and 67,995 output tokens for deliberation are reported
by X but excluded from every win criterion. B could win on execution wall time
while costing an order of magnitude more tokens than A, and the verdict would
not mention it. Fix: state merge time to the second from a timed command, and
report tokens per arm alongside wall time, even if tokens do not decide the
verdict.

### S3-2. FIFO-missing is not a timeout, so DRIVER DEAD may never trigger

Step.sh prints ok:false "fifo missing, driver not running" immediately, with
exit 1, and that is not a timeout. The briefs trigger DRIVER DEAD only on
"step.sh times out twice in a row." If the driver is down, the executor can
loop on immediate FIFO errors without ever meeting the DRIVER DEAD condition,
or record each as a driver error and keep going. Fix: trigger DRIVER DEAD on
two consecutive failures of any kind from step.sh, not only timeouts.

### S3-3. Re-diagnose timing vs the 500 ms removal delay is unspecified

Y4b establishes removeLoadingScreen removes tz-hidden 500 ms after being
called. Y8's ladder says "remove tz-hidden exactly as removeLoadingScreen
does (single eval...); then re-diagnose." If re-diagnose runs inside that
500 ms window, it still sees the class and wrongly declares INFRA-BLOCKED.
Fix: wait at least 600 ms after the removal eval before re-diagnosing, and
record the wait.

### S3-4. The plan's runtime guesses were decided by majority vote

The merge note records 2-1 votes on runtime facts: whether Marionette clear
fires the input event (draft-3's explicit dispatch wins), whether the phone
input needs re-finding after clear (draft-2's re-find dropped). These are
empirical runtime facts, not matters of opinion, and no deliberator ran the
fixture live. If a voted guess is right, B's accuracy win is partly luck;
if wrong, B eats a plan defect. The design cannot separate deliberation
quality from voting luck. Fix: label every plan assertion as static-verified
(read from fixture HTML) or runtime-guessed (voted, untested), and score
B's result with that split visible.

### S3-5. Step-count asymmetry also corrupts the tool-call comparison

B's plan is 58 steps; A's spec is 28 steps. Tool calls counted from the
codex --json stream count command_execution items, which include report-file
appends and any shell the executor runs, not only driver commands. One tool
call can also run several step.sh invocations (a loop), undercounting driver
commands, while report bookkeeping inflates the count differently per arm
(B logs 58 plan steps, A logs about 28 spec steps). Fix: count driver
commands from out.log (driver-side, per-arm ranges) and count tool calls
from the stream as a separate number, with report-writing calls excluded or
counted separately, and pin one driver command per tool call in the briefs.

### S3-6. Second crash and orphaned tabs are unhandled

The crash rule says "re-run once from scratch" but never says what happens
if the re-run crashes too, and never requires cleanup of the crashed run's
tab. A crashed executor may leave its tab open in Zen; the re-run opens
another tab, and the design has no tab inventory check before the re-run.
Fix: second crash of any kind ends the arm as BLOCKED; before any re-run,
inventory Zen tabs and close only the crashed run's tab (or record that it
is already gone).

## Answers to the design's open questions

1. Are the win criteria fair? No. Both bias toward A. Total speed is
unwinnable for B by arithmetic (S1-1), and the accuracy bar counts raw errors
plus recovery across unequal denominators (S1-5), which also favors A.
The criteria as written can only produce "A wins" or "B wins on execution-only
speed," never a B total win under normal conditions.

2. Is the INFRA retry-once rule right? No, as written. A hidden-body hit in
one arm and not the other, with n=1 and a 5-minute retry, means the two arms
did not run in the same browser-health window, and the retry's waiting time
is uncounted (S1-6). Either require both arms to run in the same verified
healthy window (pre-flight on the executor's own tab, S1-2, immediately before
each arm, with no retry that lets the window change), or accept that an
infra hit in either arm invalidates the comparison rather than just that arm.

3. Is n=1 acceptable? Only as a pilot with run-scoped language and a
meaningful-difference threshold (S2-4). One A run and one B run, fixed order,
cannot support a general claim about deliberation. A second pair in reverse
order (B-then-A) is the minimum that would let order effects be estimated.

4. Does the pre-flight recovery ladder contaminate the comparison? Yes.
It warms the driver and settles the extension chain (S2-3 scenario 1), its
measurement can change the measured state (scenario 2), it pollutes the
shared out.log (scenario 4), and its FLAGGED pass has no verdict consequence
(scenario 3). A FLAGGED pass is still a pass in every win criterion.

5. What else could produce a false win? The full list above. The three the
design does not catch at all are: A reading the committed plan (S1-3),
the coordinator reclassifying B's failures into retry buckets (S1-4 plus S1-6),
and the asymmetric verification standard letting A pass with fewer checks
(S2-2).

## Things checked and NOT holes

- md5 verification of spec, fixture, hand_drive.py, and plan at 18:24 is real
and correctly scoped; the hole is only the missing re-verification at launch
(S2-6), not the check itself.
- PASS/FAIL from DOM reads plus __agyVerify, never from an executor claim, is
the right standard; the hole is the asymmetric read set (S2-2), not the standard.
- Sequential arms, one live runner, and the Y4d precondition are correct;
the holes are the fixed order (S2-4) and the missing clean-slate check (S2-5).
The owner-away half of S2-5 is closed in substance by the owner's 18:24 handover
order in MEMORY.md, but it is not restated in the design.
- Removing the V2 category and classifying class-absent plus computed-hidden
as OTHER_HIDDEN follows Y4b correctly.
- The "SAME tab-acquisition method" rule is the right instinct; the hole is
that the fallback is unnamed (S2-6).

## Bottom line

Do not run this design as written. The total-speed verdict is decided before
the arms run (S1-1), the browser-health gate measures the wrong tab (S1-2),
A can read B's plan without detection (S1-3), the judge is the plan's author
(S1-4), the accuracy metric punishes the arm that does more work (S1-5), and
the retry rules let a preferred arm draw again until it passes (S1-6).
Fix S1-1 through S1-6 first; S2-1 through S2-7 before any run; S3-1 through
S3-6 are cheap to close in the same pass.

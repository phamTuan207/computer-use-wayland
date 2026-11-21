# E1 redteam: attack on the v2.2 fix and the void-A1/A2 decision (Worker Y8b redteam)

Paper only. No Zen driving, no executor launches, no live browser use.
Started 19:33 +07, finished 19:44 +07, 2026-11-21. All times Asia/Ho_Chi_Minh.
Branch: todolist-push. Repo (VM): ~/workspace/computer-use-wayland.

## Verdict first: BLOCK

Do not void A1/A2 as proposed, and do not run v2.2 as specified. Both halves
fail on their own evidence.

The sharpest surviving objection is twofold, and either half alone blocks:

1. The proposed plan conversion, read literally, breaks the plan. A mechanical
single-to-double swap of the plan text makes 24 of 64 commands unparsable
JSON (proven by json.loads below, S3). The fix as specified converts a
shell-quoting trap into a JSON-parse trap. B would then 500 on every eval for
a different reason, and the experiment would burn another void cycle.
2. Voiding A1/A2 plus resetting the budget rewrites a frozen cap, not a
reading of it. A1 and A2 were post-start failures. The frozen design says a
post-start first run IS the result, caps each arm at 2 starts, and ends the
arm as BLOCKED on a second crash. A1/A2 are those two starts. The void would
make it four consecutive failures that do not count (pre-flight 1, pre-flight
2, A1, A2), with zero counting failures so far. A skeptic would call that
erasing inconvenient results, and the skeptic would be right on the text.

The quoting mechanism itself survives attack (S1, refuted). That is what makes
this block painful rather than easy: the diagnosis is right and the remedy as
written is wrong. The remedy is repairable. Section "Gates to unblock" lists
exactly what must change. Until then, no A3 and no B.

## Evidence base

Read: design v2.1 (commit 695efea), execution log (commit ad64bc6), briefs A,
A2, B, driver reference, preflight.py, plan /tmp/e1/plan-test-05.md (md5
a7b5646b2bf081386bb7bcea0563ad5a, read via ssh-laptop.sh), events-a.jsonl,
events-a2.jsonl, repro-quote.sh, step.sh, hand_drive_e1.py, out.log,
preflight-a.json, preflight-a2.json.

New evidence produced by this redteam (shell simulation only, no Zen driving):

- R1: replay of the executors' exact recorded commands through a stub
  step.sh (/tmp/echo-step.sh on the laptop, prints argv $1). Both A1 and A2
  diagnose commands, replayed verbatim from events-a.jsonl and
  events-a2.jsonl, deliver
  `{"cmd":"eval","js":"return (function(){...querySelector(#contacts-count);...})()"}`,
  valid JSON, JS with the quotes stripped. The mangling happens in the
  executor's shell invocation, before step.sh.
- R2: extraction of all 64 JSON commands from the plan. Current plan parses
  64/64. Naive single-to-double swap parses 40/64. The 24 failures are
  exactly the 24 JS-bearing commands that contain single quotes.
- R3: JSON-aware conversion (parse each command, rewrite JS string literals
  to double quotes with inner doubles escaped, re-serialize with json.dumps)
  re-parses 64/64, including the two italic-selector steps. The safe
  transformation exists, but it is not the transformation the proposal
  describes.
- R4: plan inventory. 19 evals (not 21), 7 click_js, 64 JSON commands total.
  17 of 19 evals and 7 of 7 click_js contain single quotes. 10 of 19 evals
  start with `return`; all 19 contain a `return`.

## S1: Is the quoting mechanism really proven? REFUTED (mechanism stands)

The attack that the 500s could be a second cause fails for the diagnose step.

- The delivered input at failure time is proven, not inferred. R1 replays the
  exact command strings from the event files and shows both executors sent
  `querySelector(#contacts-count)` with no quotes. That JS is a syntax error
  on any tab, in any state. Tab readiness therefore cannot rescue the
  diagnose step, and cannot explain the failure.
- The tab was ready. new_tab succeeded in both attempts (1101 ms and
  1128 ms, handles returned) and hand_drive.py's new_tab polls readyState to
  complete plus a 1 s settle before returning. The coordinator's later eval
  on the same tab returned readyState complete with the fixture URL.
  new_tab really navigated.
- The repro is faithful in outcome even though its shell form differs from
  the executors'. repro-quote.sh line A (plain single-quoted JSON in a script
  file) returns HTTP 500; line B (double quotes, JSON-escaped) returns "6".
  R1 shows the executors' differently-wrapped commands deliver the same
  mangled $1 as repro line A. The timing objection (repro ran on a settled
  tab after the failures) is answered by R1: the failure-time input is
  reconstructed exactly, and it was already invalid when sent.
- A Marionette content-process race is unnecessary. The syntax error is
  sufficient to predict both the 500 and the double-quote success. A race
  would not be fixed deterministically by changing quote style.

Residual caveat, not a refutation: the 500's error body was never captured.
hand_drive_e1.py catches every Marionette error as `str(e)[:300]`, which is
just "HTTP Error 500: Internal Server Error", and geckodriver runs with
stdout and stderr to DEVNULL. So the chain "mangled JS, therefore syntax
error, therefore 500" rests on R1 plus the repro, not on a single observed
Marionette error text. That body cannot be recovered retroactively. It is a
one-link inference gap, and it is the only gap left in S1. Recommendation:
capture the Marionette error body in hand_drive.py before the next run, so a
future 500 is classifiable instead of inferred.

Also recorded: the coordinator's 19:22 diagnosis ("transient, tab mid-state
leading guess") was wrong. It was written before the quoting discovery and
it shows the coordinator misread its own evidence in real time. That does
not weaken the quoting proof, which came later, but it weakens any claim
that the coordinator's contemporaneous classifications can be trusted
without the event files.

## S2: Does the v2.2 fix close the trap for every command? SUSTAINED (it does not)

The trap surface is larger than the proposal covers, and the proposal does
not state the one detail that makes the fix work.

(a) The count is wrong. The log claims "all 21 of its evals". The plan has
19 evals. 17 of them contain single quotes, plus 7 of 7 click_js. The
proposer has not enumerated the surface it claims to fix. If the count is
wrong, the fix scope cannot be trusted to be complete.

(b) The escaping is unspecified, and the naive reading breaks JSON. The plan
stores commands as JSON text in markdown. A JS double quote inside a JSON
string value must appear as `\"` in the file, or the JSON is invalid. The
proposal says "mechanical single-to-double conversion of the plan's JS
strings" with no mention of JSON escaping. R2 proves the naive swap breaks
24 of 64 commands. The correct form is visible only in repro line B, which
the proposal never cites as the template. A fix that does not name the
escaped form `\"` and does not require a json.loads check of every converted
command is not a fix, it is a hope.

(c) Executor-written JS is uncovered. The A brief mandates three final-read
evals (David favorite, Spam Bot absence, Frank DOM) with NO exact JS given,
plus a localStorage eval with no exact JSON given, plus every spec-step eval
the A executor writes itself. The v2.2 fix changes only the briefs' diagnose
JS. An A3 executor that writes `querySelector('#...')` in any of those
evals hits the identical trap, 500s twice, and is mislabelled DRIVER DEAD.
The driver reference is the only cover for these, and it currently contains
no quoting rule at all. Its click_js example,
`document.querySelector('...')`, teaches the trap pattern verbatim.

(d) Both-quote JS is unhandled. Steps 21 and 55 contain a single-quoted JS
string that itself contains double quotes:
`.meta-line[style*=\"italic\"]`. See S3. The proposal says nothing about
them.

(e) Dollar signs, backticks, and template literals are unhandled. Inside a
single-quoted shell argument they are inert, which is the safe form. Inside
a double-quoted shell argument, `$`, backticks, and `!` are live. The
proposal does not forbid shell double-quote wrapping, and the A1 executor's
own command was already wrapped by codex in `bash -lc "..."`, with the
executor's `\'` escapes inside it. An executor that "fixes" quoting by
switching to shell double quotes reopens command substitution and
backtick execution. The rule must prescribe exactly one form: single-quoted
shell argument, JS double quotes escaped as `\"`, never `\'`, never
shell double-quote wrapping.

(f) Type text is an unexamined vector. Any `type` text containing a single
quote (an apostrophe in a name or note) ends the shell-quoted JSON and the
remainder becomes shell input. The plan's type texts have no apostrophes,
so B is safe on this vector, but A's executor types whatever it chooses,
and the fix says nothing about it. The same holds for any `find` css or
`new_tab` url containing a quote. This is also a command-injection shape,
not just a syntax shape.

(g) The preflight.py change is theater. preflight.py calls step.sh via
subprocess list argv, no shell. Quoting in its JS strings cannot reach a
shell, so converting its single quotes to double quotes changes nothing
functionally. It creates the appearance that pre-flight and executor now
test the same code path. They do not. See S6.

## S3: Is the plan conversion safe? SUSTAINED (naive conversion corrupts)

Three corruption vectors, two proven, one structural.

1. JSON validity. R2: naive swap, 40/64 parse. Every one of the 24 broken
commands is a JS-bearing command with single quotes. The broken form is
`"js":"...querySelector("#contacts-count")..."`, which ends the JSON string
at the first inner double quote. json.loads fails with "Expecting ','
delimiter". If this converted plan were deployed, B would fail on its first
eval with a "bad json" error from hand_drive.py, not a 500, and the arm
would stop under the same DRIVER DEAD rule. The proposal's "diff proof"
does not catch this: a diff shows what changed, not whether the result
parses. Only a json.loads check of all 64 commands catches it, and none is
proposed.

2. Steps 21 and 55, the italic selectors. Original JS:
`c.querySelector('.meta-line[style*=\"italic\"]')`. A naive swap gives
`c.querySelector(".meta-line[style*="italic"]")`, which is a JS syntax
error even if the JSON were repaired, because the inner double quotes
terminate the JS string. A correct conversion gives
`c.querySelector(".meta-line[style*=\"italic\"]")` in JS source, which in
the markdown JSON text is triple-escaped. R3 shows a JSON-aware converter
produces exactly this and re-parses. A sed-style converter does not.

3. Non-command single quotes. Line 3 of the plan, the usage instruction,
contains `step.sh '<json>'`. A global replace across the file corrupts the
instruction itself. There are no prose apostrophes elsewhere in the plan
(the 25 lines containing a single quote are line 3 plus 24 command lines),
so the prose risk is confined to line 3, but a global script still hits it.
The conversion must operate on parsed JSON commands only, never on the
file text.

Additional count error inside the design, not just the log: the v2.1 note
claims "all 21 of its evals start with `return`". R4: 19 evals, 10 start
with `return`, all 19 contain a `return`. The substance (every eval returns
a value) holds, but the sentence is wrong twice over, which is the same
class of sloppiness that produced the quoting trap: claims about the plan
written without counting the plan.

## S4: Is voiding A1/A2 plus resetting the budget a fair reading? SUSTAINED (it is a rewrite)

The frozen design, in its own words:

- "Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in
  every table and every verdict sentence. It never silently replaces A1 or
  B1."
- "Post-start INVALID (crash, DRIVER DEAD, mid-run hidden body, or any stop
  after the executor's first driver command): the first started run IS the
  arm's result for accuracy. If the executor never reaches final
  verification, the arm is recorded as FAIL (incomplete)... A re-run, if the
  coordinator judges it worth doing, is a second observation (A2/B2)
  reported alongside A1/B1, never a replacement."
- "Second crash of any kind ends the arm as BLOCKED."

A1 and A2 were post-start. Both executors issued new_session and new_tab
successfully, then failed on the diagnose eval, which is the executor's
mandated first step in the brief. Under the frozen text, A1 is FAIL
(incomplete), A2 is the second observation, and the arm is now BLOCKED.
There is no void clause for post-start failures anywhere in the design.
The pre-start INFRA-BLOCKED retry rule does not apply: the executors
started. The void proposal therefore does not read the design, it amends
it, and it amends it after the failures it would erase.

What a skeptic says, and the skeptic is right: the coordinator wrote the
briefs that contained the trap, ran two arms into the trap, and now proposes
to void both attempts and reset the budget. The beneficiary of the void is
the coordinator's own experiment, not the data. The precedent is the
danger: any future arm that fails twice can be voided as an "instrument
artifact" by the same reasoning, because every failure can be redescribed
after the fact as an instrument defect. A design that lets the coordinator
void its own failures on its own say-so has no falsification left in it.

The pattern sharpens the point. Counting non-counting failures so far:
pre-flight 1 (18:55, v2.1 bug, "consumed no retry budget"), pre-flight 2
(19:06, holder death, "not an arm retry"), A1 (proposed void), A2
(proposed void). Four consecutive failures, zero counting failures. The
experiment has not yet had a failure that counts. Each individual
classification is defensible in isolation; together they are a machine that
never records a loss.

Guards that would be required before any void is granted. All six, not a
subset:

1. The defect is proven in the instrument, present from the freeze, and made
   the task impossible as specified. Here that bar is met on the facts (R1,
   zero task steps run in both attempts), and that is the only reason a void
   is discussable at all.
2. The void is decided by the independent judge from arm-stripped evidence,
   not by the coordinator and not by a council the coordinator convened. The
   design gives the judge the invalidity decision. Voiding before the judge
   rules bypasses the blinding protocol.
3. The voided attempts stay in the record with full data (event files,
   out.log ranges, wall times, token counts) and are labelled VOID in every
   table. Nothing is deleted or relabelled as if it never ran.
4. Exactly one void per arm per experiment, ever, and the retry it grants is
   exactly one additional start, not a fresh two-start budget. "Retry budget
   reset" as phrased would grant A3 and A4, taking arm A to four starts
   against B's two. The scope must be pinned in writing before A3 launches.
5. The void does not wash the downgrade. The design already says: "If either
   arm needed an infra retry or any recovery-ladder intervention, no clean
   win or loss is claimed on either criterion." A needed exactly that. The
   verdict stays "observed difference, confounded by browser health" even
   if A3 and B both run clean.
6. The replication trigger stays tripped. "Either arm is flagged or invalid"
   already holds. A void must not clear it.

Without these guards, the answer is no. With them, a single void of A1/A2
is the outer limit of what the evidence supports, and it should be recorded
as an amendment (design v2.2 re-freeze note), not presented as a reading of
v2.1.

## S5: What do two voids plus a plan edit do to comparison validity? SUSTAINED (validity is downgraded, permanently)

The plan is the treatment for arm B. Editing it after A has run twice,
even mechanically, means B's treatment is not the treatment frozen at
18:35. The design permits a re-freeze ("Any change after this freeze
requires a new version number and a re-freeze note, never a silent edit"),
so a v2.2 re-freeze is procedurally available. But procedure is not
validity.

- The edit rescues B from certain failure. Without it, 24 of B's 64 commands
  would fail the same way A1/A2 did. B could not have run at all. A, by
  contrast, writes its own commands; only its diagnose step was fixed by
  the brief change. The fix therefore benefits the two arms asymmetrically
  in effect, even though it is symmetric in intent. The comparison after the
  fix is a fair test of the fixed instruments, not a test of the instruments
  as frozen. The honest label is A-fixed versus B-fixed, and the pre-fix
  A1/A2 are instrument-debugging data, not pilot data.
- The edit is a coordinator edit to the deliberated product. The B condition
  is defined as the "deliberated-plan bundle (3 drafts + coordinator merge +
  validation)". A quoting conversion is mechanical only if it is proven
  semantics-preserving. R2 shows the naive form is not. If the conversion
  is done wrong on steps 21 or 55, the coordinator has substantively changed
  B's checks, and a B win would be partly a coordinator win. The conversion
  must be proven semantics-preserving (R3-style re-parse plus a live run of
  every converted eval on a scratch tab) before B launches, or B's result is
  confounded by the coordinator's edit.
- Order and history effects accumulate. A3 would be the third A start, after
  two dead runs and roughly an hour of elapsed wall time, infra restarts, and
  a holder death. The design's inter-arm gap rule (over 60 minutes, re-verify
  md5s) may trigger. Zen and driver warm state at A3/B time is not the warm
  state at A1 time. This does not invalidate the comparison, but it must be
  disclosed in the verdict, and it is one more reason the clean-win bar
  cannot be recovered by voiding.

Net: the pilot can still produce an observed difference between A-fixed and
B-fixed, with the downgrade attached. It cannot produce a clean win on
either criterion. Any v2.2 note that claims otherwise is overclaiming.

## S6: Other holes. SUSTAINED

1. The pre-flight and the executor still test different code paths after
   the fix. Preflight.py uses subprocess list argv (no shell). Executors use
   shell single-quoted arguments (quoting live). A quoting regression in any
   future brief or plan edit will pass pre-flight and fail the executor,
   exactly as happened here. The v2.2 fix patches instances, not the
   divergence. The durable fixes are: (a) change the transport so quoting
   is impossible (step.sh reads JSON from a file or stdin instead of a
   shell argument), or (b) make pre-flight invoke step.sh through a shell
   exactly as an executor does, or (c) add a pre-launch gate that extracts
   every JSON command from the brief and plan, passes each through the
   shell, runs json.loads, and blocks launch on any failure. The proposal
   does none of these. Prose rules already failed twice (the reference gave
   no guidance; the brief gave the trap verbatim). A third prose rule is not
   a fix.

2. The DRIVER DEAD rule mislabels deterministic errors as driver death. The
   design says two consecutive step.sh failures of any kind equal DRIVER
   DEAD, and the briefs tell the executor to stop. Both A1 and A2 were
   declared DRIVER DEAD while the driver, geckodriver, and port 4451 were
   all alive (verified by the three liveness checks). The rule conflates
   "the driver is dead" with "the command was bad". v2.2 does not amend it.
   A bad JSON parse from a faulty plan conversion would be mislabelled the
   same way, and the arm would stop instead of diagnosing. The driver
   should distinguish error kinds (bad JSON, JS error, transport failure),
   or the rule should.

3. The 19:06 holder death is still unexplained and unaddressed. The driver
   and FIFO holder both died after the first pre-flight, with no OOM, no
   core dump, and no journal entry, and the cause is recorded as UNPROVEN.
   The quoting fix touches nothing in that path. If the holder dies again
   mid-arm, the same DRIVER DEAD mislabel recurs. The orphan geckodriver
   bug in hand_drive_e1.py is likewise unaddressed.

4. out.log is contaminated for both arms, breaking the mechanical count.
   The coordinator's 19:23 diagnosis evals (3 commands) sit inside A1's
   session range in out.log, before A1's close and delete lines. The repro's
   two commands (500, then "6") sit inside A2's session range, before A2's
   close and delete lines. The design counts driver commands from out.log
   between session boundaries, which would count 7 commands for A1 and 6
   for A2 instead of the executors' 4 and 4. The executor reports are
   primary, so this is contained, but the cross-check the design relies on
   is polluted by the coordinator's own probes. Future probes must run in
   their own session or be excluded from the count explicitly.

5. Fail-closed behavior for executor non-compliance does not exist. If an
   A3 executor ignores the quoting rule on its own written evals, the only
   outcome is two 500s and a stop. There is no pre-flight of the executor's
   own first eval, no self-test command, and no coordinator check before
   launch that the executor's brief commands parse through a shell. The
   cheapest fail-closed step is gate (c) in item 1 above, run before every
   executor launch.

6. The A3 brief does not exist yet, and its freshness is assumed. It must be
   a fresh brief (not a copy of the A2 brief with stale md5s), must ban
   A1/A2 artifacts (run-a-report.md, run-a2-report.md, events-a.jsonl,
   events-a2.jsonl, out.log), and must carry the fixed diagnose JS in the
   exact escaped form with a worked shell example. The same applies to the
   B brief and the driver reference. The v2.2 proposal lists the files to
   change but gives no verification step (md5 re-freeze plus a shell-parse
   check) for any of them.

## Gates to unblock (all required, in order)

1. Judge rules on A1/A2 invalidity from arm-stripped evidence. No void
   without the judge's written ruling.
2. If a void is granted, record it as a design v2.2 amendment with all six
   S4 guards in writing, including exactly one additional A start (A3
   only, no A4) and the permanent no-clean-win downgrade.
3. Rewrite the quoting rule as an exact, testable specification: single-
   quoted shell argument, JS double quotes escaped as `\"`, never `\'`,
   never shell double-quote wrapping, with a worked example for an eval and
   a click_js, in the driver reference and both briefs. Fix the reference's
   click_js example, which currently teaches the trap.
4. Convert the plan with a JSON-aware converter (parse, rewrite JS string
   literals, re-serialize), never a text replace. Prove it: json.loads on
   all 64 commands, a diff that shows only quoting changes, and a live run
   of every converted eval on a scratch tab before B launches. Steps 21 and
   55 must be verified individually.
5. Give the A brief exact JS for its three final-read evals and its
   localStorage eval, so no executor-written eval is left to chance. Or
   state in writing that A3's executor-written evals are an accepted
   residual risk, and name the fail-closed behavior when one 500s.
6. Close the code-path divergence or gate it: either change the transport
   (file or stdin JSON), make pre-flight use the shell path, or add the
   pre-launch shell-parse gate for every brief and plan command. Pick one,
   prove it with a failing-then-passing test, and record it.
7. Amend the DRIVER DEAD rule so a deterministic command error (bad JSON,
   JS syntax error) is classified as a command error, not a driver death,
   and capture the Marionette error body in hand_drive.py so the next 500
   is classifiable.

## Timing log

- 19:33 task received. Read design, log, briefs A/A2/B, driver reference,
  preflight.py.
- 19:34 read plan via ssh-laptop.sh (112 lines, md5 a7b5646b...), plus
  repro-quote.sh, step.sh, out.log.
- 19:35 extracted exact executor commands from events-a.jsonl and
  events-a2.jsonl.
- 19:36 stub replay (R1): both diagnose commands deliver
  querySelector(#contacts-count), quotes stripped.
- 19:37 read hand_drive_e1.py, preflight-a.json, preflight-a2.json.
- 19:38 plan quote inventory and counts (R2, R3, R4): 64 commands, naive
  swap 40/64 parse, JSON-aware conversion 64/64, 19 evals, 7 click_js.
- 19:44 report written.

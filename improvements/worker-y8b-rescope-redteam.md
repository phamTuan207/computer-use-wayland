# E1 re-scope redteam verdict (Worker Y8b)

Redteam, paper only. No Zen driving, no executor launches, no live browser use.
The judge's ruling (commit 7275171) is binding and is not re-debated here.
Where this file cites the design, the citation is to the frozen v2.1 text at
commit 695efea, file improvements/worker-y8-e1-comparison-design.md.

## 0. Standing facts (not re-litigated)

- A1 FAIL (incomplete), A2 FAIL (incomplete). Not VOID. Arm A used 2 of 2
  starts, second crash of any kind ends the arm as BLOCKED. No A3 under v2.1.
- No-clean-win clause TRIGGERED (A2 was an infra retry). Executors exonerated.
  Failure is a deterministic defect in the frozen instrument (shell-quoting
  trap), proven by the judge independently.
- The v2.1 comparison is OVER. A future A attempt would need a versioned
  re-freeze (v2.2+) and a fresh budget decision by the coordinator and
  council. The ruling does not authorize one.
- Replication trigger ENGAGED (judge section 5). Design: "Never compare one
  measured arm against nothing" (line 100, pre-start INFRA-BLOCKED rule).
- The v2.2 fix is done and probe-proven, but NOT frozen: the design file is
  unmodified in the working tree, and the fixed files (plan, briefs A/B/A3,
  driver reference, preflight) are uncommitted working-tree edits. There is
  no v2.2 re-freeze note. No option that runs an executor "under v2.2" is
  executable until that freeze is committed.

Independent spot checks by this redteam (VM repo + read-only laptop reads):

- Plan conversion: 64/64 JSON commands parse, 0 single quotes in any decoded
  js value, 19 evals, 7 click_js, 26 js-bearing commands, 0 node
  new-Function parse failures. New plan md5 63415e9b6cd63dc2185ca23242180424.
- Briefs A, B, A3 and the driver reference carry the STOPPED (DRIVER SUSPECT)
  wording and the strong-form quoting rule; 0 occurrences of querySelector('
  in any of the three briefs.
- Laptop /tmp/e1/v22-proof.log: all 6 probes ok:true (full diagnose VISIBLE
  countText 6 in 3 ms; step 4 count 6; step 31 click_js ok plus step 32
  starActive true; italic eval ok with nulls; step 56 verifier ran).
  Laptop plan and B-brief md5s match the repo exactly.
- Laptop infra is STILL UP at 19:57 +07: driver PID 274644, geckodriver PID
  274657, ports 4451 and 8767 listening. Any release of the slot needs a
  verified infra stop, not just a log line. See section 5.
- Y9 is still waiting (its live log records no completion commit and a single
  "E1 EXECUTION COMPLETE" grep hit, the 18:53 descriptive line, which is not
  the marker itself).

## 1. Option (a): B runs alone under v2.2, no comparison claimed

### Verdict: AMEND

### What a B-only number is actually worth

The experiment asked one comparative question: does splitting deliberation
from execution increase SPEED or ACCURACY versus one agent deciding and
executing? A B-only number cannot answer it. There is no A to compare to,
and the design's scoped verdict sentence cannot be filled in: "B total vs
A total on the primary clock; accuracy burden A vs B; PASS/FAIL per arm."
With A missing, the sentence has empty slots, not a verdict.

Worse, the headline speed verdict is already determined without B running.
A1 wall is 151 s, A2 wall is 285 s (19:25:00 to 19:29:45), and the design
(line 107) counts failed-attempt wall time toward the arm's total, so A
total is at least 436 s. B total is at least 642 s sunk (520 deliberation
plus 122 merge) plus B execution, so B total exceeds A total under every
reading of A total. B "does not win" on total speed whatever B does. Running
B adds nothing to the headline speed verdict; it can only add the
execution-only number, which needs an A execution to mean anything, and A
execution is undefined (zero task steps in both attempts).

What B-only CAN produce, honestly labelled, is two non-comparative things:

- Plan validation: does the 58-step plan execute end to end to a PASS, with
  no plan defect blocking it? The 6 probes prove converted commands parse
  and execute; they do not prove the 58-step sequence completes.
- Full-run instrument proof: does the v2.2 fix survive a whole run, not just
  6 probes? That is a shakedown result, not an experiment result.

Both are real, and both belong to a future experiment's pilot, where they
would count as data. As a standalone they are a shakedown with no consumer:
the B number cannot be banked for later comparison, because the design
scopes every verdict to "this task, this run" and a later experiment would
need its own B run under its own freeze.

### The sharpest surviving objection

A B-only PASS manufactures exactly the record the frozen rules cannot
adjudicate. The accuracy criterion says B wins ONLY if "(B passes and A
fails)" OR both pass with a burden gap of at least 2. A has failed twice,
so the first disjunct is literally satisfied by a B PASS. But the
no-clean-win clause is TRIGGERED, so no clean win may be claimed on either
criterion, and the result must be reported as "observed difference,
confounded by browser health." So the record would simultaneously satisfy
the win condition and forbid claiming the win. And there is no judge
scheduled to adjudicate the conflict: the design's judge section has the
judge decide "after both arms complete." A lone B run leaves a win-shaped
record with no judge. The next summarizer will keep "B passed, A failed"
and drop the confound caveat, because that is what summaries do. The
reconciliation already documents this failure mode in miniature: the
pre-compaction record claimed a plan conversion was "proven" when it was
not. A promise of "no comparison claimed" is not a control. The control
would have to be pre-registered language, and prose does not survive
retelling.

Further holes:

- A B PASS would be read as "the plan works, therefore deliberation works,"
  conflating plan executability with deliberation benefit, and as "A failed
  because direct execution is worse," attributing an instrument artifact to
  the condition. B would run on the fixed instrument, A ran on the broken
  one; any A-vs-B contrast is a contrast of instruments, not conditions.
- A B FAIL would be ambiguous (plan defect vs executor error vs residual
  instrument bug) with no A arm to tell whether A would have failed the
  same way.
- B-only does not release Y9 (section 5). It consumes a live slot while
  Y9, Y11, Y6b, Y13, Y14 wait, and Y9's 4-hour timeout keeps running.
- "Under v2.2" presumes a freeze that does not exist yet (section 0).

### Gates for (a) to proceed

1. Commit the v2.2 re-freeze note first (design, briefs, driver reference,
   preflight, plan, md5s). No executor runs on uncommitted working-tree
   edits.
2. Pre-register the B-only report language in the log BEFORE B runs, with
   the forbidden sentences listed verbatim: no "B wins," no "deliberation
   wins," no "A failed," no total-speed headline, no accuracy headline.
   The report's only verdict-shaped sentence is "B executed the plan in X
   seconds with burden Y; no comparison is drawn."
3. Record in the log that this run does NOT satisfy the Y9 marker and does
   NOT release Y9, and notify Y9's watcher of that fact in the same commit
   window, so Y9 does not mistake B activity for progress toward its marker.
4. Slot-time cap agreed with the queue in writing before launch; if the
   handover window closes first, B aborts mid-run and the partial run is
   reported as partial, not as a result.

## 2. Option (b): fresh comparison under v2.2 with a NEW A budget

### Verdict: BLOCK

### The void by another name

The council already decided the void question, and the judge denied it.
Option (b) does the same thing through a different door: instead of
resetting the budget (void), it grants a new budget. The beneficiary is
identical (the coordinator's own experiment), the effect is identical (the
budget consequences of A1 and A2 are erased), and only the label changes.
The reconciliation's Q3 section already named this hazard for the void:
"the beneficiary of the void is the coordinator's own experiment," and
"that objection cannot be answered by the coordinator alone, because the
coordinator wrote the briefs that contained the trap." A fresh budget
granted by the coordinator and council is the same self-dealing with the
judge removed from the room.

The judge's sentence does not authorize what (b) needs. It says: "Any
future A attempt would need a versioned re-freeze (v2.2 or later) under
sentence (j) and a fresh budget decision by the coordinator and council;
this ruling does not authorize one." That lists necessary conditions and
expressly withholds authorization. It does not say the council MAY grant a
fresh budget; it says the ruling does not grant one. The design contains no
budget-grant mechanism at all: "Max 2 starts per arm" is a cap, not a
power to re-issue starts. Reading the judge's sentence as permission
inverts it.

### The fresh comparison cannot produce a win under the frozen rules

Even if (b) runs, it cannot deliver what it promises, for three independent
reasons:

- The win rule (line 101): "No accuracy or speed win may be claimed from a
  second observation alone; a win requires the first observations to support
  it, or requires both observations to agree." The first observations are
  FAIL and FAIL. They support nothing. A third observation (A3) cannot
  ground a win under this text, and neither can a fresh pair that keeps
  A1/A2 in the record.
- The no-clean-win clause is TRIGGERED as a historical fact: A2 was an
  infra retry. A fresh budget does not un-trigger history. The best outcome
  (b) can ever reach under E1 is "observed difference, confounded by
  browser health," which is the same verdict ceiling option (a) reaches
  with one slot and no rule-breaking. Two live slots for the same ceiling
  is a bad trade, stated plainly.
- The v2.1 re-freeze precedent was mechanical-only: "No criterion, threshold,
  rubric, or procedure changed; only the instrument now returns the value
  the design always assumed it returned." A budget reset plus rewritten win
  criteria plus rewritten replication section is not a re-freeze. It is a
  redesign, and it needs to be owned as one.

### Label discipline: nothing stops the rewrite of history

The A3 brief already exists as an untracked file. "A3" reads as the third
start of the same arm in the same experiment, implying A1 and A2 were valid
starts 1 and 2 and A3 is the retry the design forbids. Every table will
show A1 FAIL, A2 FAIL, A3 (result), and every reader will do the natural
thing: treat A3 as the arm's result and forget A1/A2, or treat A3 as a
retry. The A3 brief bans A1/A2 artifacts for the EXECUTOR, but the
reporting layer has no equivalent ban, and no label discipline in prose
has ever survived summarization in this repo. The strongest case that (b)
corrupts the record is structural, not motivational: it creates two
inconsistent truths in the same experiment file (arm A BLOCKED with 2
FAILs, and arm A running as if unblocked) reconciled only by a council
minute. Future readers resolve that inconsistency by dropping the
inconvenient half.

Related label collisions:

- The replication pair is (B2, A2) by design. A2 is spent (FAIL). A
  replication "A2" would be a label reuse, forbidden by line 99 (labels
  are sequential, never reused, never silently replaced).
- The replication section requires "same briefs, same plan file (same
  md5)." The v2.2 plan md5 differs (63415e9b vs a7b5646b), so the condition
  fails by construction.
- The replication order is B then A (ABBA overall). A fresh comparison
  running A then B again violates the order prescription and reintroduces
  the order effect ABBA was meant to cancel.

### The precedent hazard

If the coordinator can reset a BLOCKED arm's budget by council vote after
a binding judge ruling, then BLOCKED is advisory in effect, and every
future BLOCKED arm can be reset the same way. The ruling's binding force
dies with the first exception. The council must pick one: either the
ruling is binding, in which case (b) needs a justification that does not
exist in the design, or (b) is legitimate, in which case the ruling was
advisory and the judge round was theater. It cannot have both.

### Gates that would unblock (b)

(b) as proposed (E1 continuity plus a new A budget) has no gate inside E1
that fixes it, because the defects are the E1 identity itself. Two paths:

- PREFERRED: reconstitute as a NEW experiment. New design doc, new version,
  new pre-registration, new labels (no A3-as-continuation), new budget as
  part of the new design, win criteria and replication logic re-derived,
  no-clean-win evaluated afresh within the new experiment, E1's A1/A2
  FAILs cited as prior work, not as data. The E1 name and queue priority
  are not inherited. If the question is worth answering, it is worth
  answering cleanly.
- IF E1 continuity is insisted on, all of these, in writing, before any
  executor runs: (i) a v2.2 re-freeze note quoting the judge's ruling in
  full and stating the budget reset as an explicit amendment adopted by
  council, with the dissent recorded; (ii) new start labels that cannot be
  read as continuations of A1/A2; (iii) restated win criteria saying what,
  if anything, can be won given FAIL/FAIL first observations; (iv) written
  acceptance that no clean win or loss can ever be claimed under E1
  (triggered clause); (v) a rewritten replication section matching the new
  labels and the new plan md5; (vi) a final judge scheduled before any
  verdict is issued. If the council accepts (iv) honestly, (b)'s ceiling
  is "observed difference, confounded," and it should then justify two
  slots for that ceiling against option (a).

## 3. Option (c): abort entirely

### Verdict: GO (recommended)

### What is lost, stated plainly

- The comparative answer. The science question stays open.
- B plan live validation: we never learn whether the 58-step plan executes
  to a PASS.
- Full-run v2.2 proof: the fix stays probe-proven (6 probes), not
  run-proven, until a new experiment runs it.
- The deliberation investment's payoff now: 463,124 tokens in, 67,995 out,
  642 s sunk. The plan, the deliberation report, and the fix are preserved
  as inputs to a future experiment, but they yield no result now.
- The slot time already spent (A1 151 s, A2 285 s, pre-flights, council and
  judge rounds) produces no measurement. That time is sunk either way;
  abort stops further spend, it does not recover past spend.

### Why the instrument-defect finding is a sufficient outcome

The finding is not a consolation prize. It is a proven, judge-verified,
durable result: the frozen instrument could not have produced a valid A
observation; pre-flight structurally cannot catch this class of defect
(subprocess argv path vs executor shell path); the DRIVER DEAD labelling
in the frozen briefs was false under the design's own rule (driver,
geckodriver, and port 4451 all alive at 19:22:40); and the fix is proven
at probe level and preserved. The pre-flight gap transfers directly to
every future live run (Y9, Y11, Y6b all drive step.sh through shells), so
the finding buys safety for the whole queue, not just for E1. Aborting
banks that finding and moves the queue, instead of spending more of a
finite handover window defending a comparison whose verdict ceiling is
already "observed difference, confounded."

The design's own remedy for a blocked arm points the same way. Line 100:
if the second pre-flight fails, "the comparison is ABORTED: each arm is
reported as it stands (a completed arm stays completed, a blocked arm
stays blocked). Never relabel a completed clean arm as blocked. Never
compare one measured arm against nothing." Abort is the design-consistent
outcome. Options (a) and (b) both require inventing procedure the design
does not contain; (c) requires only following the procedure it does.

### Sharpest surviving objection to (c)

Abort leaves the question open and the fix run-unproven, and it relies on
the ABORT path to release Y9 (section 5), which has its own misread
risks. If the abort is written sloppily, Y9 stalls or mislaunches, and the
queue loses more than abort saves. The terms in section 6 exist to close
that hole exactly.

### Terms for (c)

1. Write the abort marker (exact wording in section 5) and commit it
   promptly, before Y9's 4-hour timeout (section 5).
2. Stop the infra and verify it: INFRA_DOWN, ports 4451 and 8767 free, no
   foreign geckodriver. Record the verification in the log. (Infra is
   still up at 19:57 +07; a log line alone does not free the slot.)
3. Commit the v2.2 fix files (plan, briefs A/B/A3, driver reference,
   preflight, repro-quote.sh) with a note stating the fix is preserved and
   probe-proven, NOT frozen, and that no executor runs are authorized
   under it. The A3 brief is retained as an artifact, not an authorization.
4. Write the final E1 report in the execution log: A1/A2 FAIL (incomplete),
   arm A BLOCKED, no-clean-win triggered, instrument defect proven,
   pre-flight gap (argv vs shell path), fix preserved, replication trigger
   engaged and unexecuted with the reason, question open for a NEW
   experiment.
5. Any future attempt is a new experiment with new labels and fresh
   pre-registration. E1's data is not reused as comparison data.

## 4. The replication trigger: does any option violate it?

The design's replication section: a second pair (B2, A2, swapped order) is
run before any comparative verdict beyond pilot language if ANY of these
holds: the arms split PASS/FAIL; total times differ by less than 2 min;
accuracy burden difference is 1 or less; either arm is flagged or invalid;
the coordinator's independent error count disagrees with either executor
report by more than 2; execution wall times differ by less than 20 percent.
The judge rules the trigger ENGAGED, on the "either arm is flagged or
invalid" leg (A1/A2 under the "Post-start INVALID" heading). The other legs
are unevaluable: they need a B1 that never ran.

- Option (a): does not violate the trigger directly, because it claims no
  comparative verdict. But it walks into a trap: after B1 runs, any
  comparative verdict beyond pilot language requires the second pair, and
  the second pair cannot be assembled as labelled (A2 spent, B1 only just
  run, same-md5 condition failed). So the trigger would stay engaged and
  its remedy unavailable, and the B1 number would have to stay in pilot
  language forever, with no judge to enforce that. Sustainable only if
  written down before B runs (gate 2 in section 1).
- Option (b): violates the trigger in letter and in spirit. In letter: it
  would issue comparative verdicts from a fresh pair without running the
  prescribed second pair, in the wrong order (A then B, not B then A), with
  a changed plan md5. In spirit: the fresh pair IS the second pair wearing
  fresh labels, which is exactly the label laundering the trigger's
  "reported as a second pair, never merged" rule exists to prevent.
- Option (c): does not violate the trigger. No comparative verdict is
  issued, so the trigger's obligation (second pair before any comparative
  verdict beyond pilot language) is moot, not breached. The trigger is
  recorded as engaged and unexecuted, with the reason (arm A BLOCKED, no
  second pair assemblable under the frozen labels). That is the only option
  that leaves the trigger in a clean state.

Note the trigger as written is unexecutable under all three options. Only
(c) admits that cleanly instead of redefining the trigger to fit the
preferred option.

## 5. The Y9 slot marker and the exact closure message

The completion marker (Y9 plan section 5, C3-F4) requires ALL of:

- (a) a commit on todolist-push after 4a78f7f matching ^Y8 E1: .*execution
  complete (case-insensitive on "execution complete");
- (b) a NEW line in improvements/worker-y8-e1-execution-log.md matching
  "E1 EXECUTION COMPLETE" that names both arm A and arm B results;
- (c) Y4d's completion verified DIRECTLY (already satisfied).

Under (a) B-only, leg (b) cannot be written truthfully: there are no
both-arms results. Y9 keeps polling until its 4-hour timeout (4 hours
after the Y4d marker, which the Y8 log records as satisfied by 18:53, so
around 22:53 +07), then reports to the parent instead of launching. Option
(a) therefore does not release Y9; it burns Y9's window.

Under (b), if the fresh comparison completed with both arms, the marker
could be satisfied as written, which is a genuine point in (b)'s favor for
queue flow. But the log line would name fresh-pair results alongside the
retained FAILs, and "both arms' results" becomes ambiguous (which A result:
A1/A2 FAILs or A3?). Y9 checks existence, not content, so Y9 would launch;
the ambiguity is a record problem, not a Y9 problem. That point does not
outweigh section 2.

Under (c), Y9 is released by the ABORT path in its own plan: "if Y8's log
shows an ABORT marker (or Y8 reports completion-with-abort), the slot is
free ONLY after the launch-time live checks pass (no foreign geckodriver
via the preflight sweep, Y8 ports 4451 and 8767 free)." The abort marker
alone does not free the slot; the live state does. Three misread risks,
each with a countermeasure:

- RISK 1, regex false positive: if the abort commit message contains the
  words "execution complete" (for example "Y8 E1: execution complete with
  abort"), leg (a) fires and Y9 may take the completion path, then stall
  waiting for leg (b) or launch on a partial marker. COUNTERMEASURE: the
  abort commit message must not contain "execution complete" anywhere.
  Exact message: "Y8 E1: ABORTED, arm A BLOCKED, comparison over".
- RISK 2, grep false positive: if the abort log line contains the literal
  string "E1 EXECUTION COMPLETE" (for example in a sentence like "no E1
  EXECUTION COMPLETE line will be written"), Y9's grep for that string
  hits it and Y9 may misread it as leg (b). Note the 18:53 descriptive line
  already contains that literal string; Y9's log shows it correctly treats
  that hit as naming the marker, not the marker itself. A second hit would
  muddy exactly the distinction Y9 is currently handling correctly.
  COUNTERMEASURE: the abort log line must not contain that literal string.
  Exact line: "E1 ABORTED 20:xx: arm A BLOCKED (A1 FAIL incomplete, A2 FAIL
  incomplete, judge 7275171), arm B never ran, comparison over, no
  completion marker will be written. Slot free after live checks: infra
  stopped, ports 4451 and 8767 free, no foreign geckodriver."
- RISK 3, live state: Y9's launch-time check requires ports 4451 and 8767
  free and no foreign geckodriver. E1 infra is still up (19:57 check). If
  abort is declared but infra is left running, Y9's launch refuses and Y9
  stalls. COUNTERMEASURE: stop infra, verify INFRA_DOWN and ports free,
  and record the verification in the log line (terms in section 3).
- RISK 4, timing: if the abort marker lands after Y9's 4-hour timeout
  (around 22:53 +07), Y9 has already timed out and reported to the parent
  instead of launching. COUNTERMEASURE: declare abort promptly; the marker
  goes in the two places Y9 polls (a commit on todolist-push and the
  execution log).

## 6. Recommendation

ABORT entirely, option (c), on the exact terms in section 3, with the exact
closure message in section 5. The question stays open for a NEW experiment;
the fix, the plan, and the instrument-defect finding are preserved; the
queue moves.

Summary of verdicts:

- (a) B runs alone under v2.2: AMEND. Real but narrow value (plan
  validation, full-run instrument proof). Sharpest objection: a B PASS
  satisfies the frozen accuracy-win disjunct while the triggered
  no-clean-win clause forbids claiming it, with no judge scheduled to
  adjudicate the conflict, so the number will be misread as a verdict.
  It also does not release Y9 and cannot change the headline speed
  verdict, which arithmetic already fixes.
- (b) Fresh comparison with a new A budget: BLOCK. Sharpest objection: it
  is the denied void under a fresh label, authorized (if at all) only by
  the interested party after a binding adverse ruling, and it cannot
  produce a clean win anyway (no-clean-win already triggered; the win rule
  keys on first observations FAIL/FAIL), so it spends two live slots for
  the same verdict ceiling option (a) reaches with one.
- (c) Abort entirely: GO. Sharpest objection: the comparative question
  stays open and the v2.2 fix stays probe-proven, not run-proven, until a
  new experiment runs it.

## 7. Timing log (Asia/Ho_Chi_Minh, wall clock)

- 19:54:36: task received. 19:54:58: work start.
- 19:54-19:57: read the judge ruling (7275171), the reconciliation
  (3cfea4d), and the frozen v2.1 design (695efea) in full; checked the
  working-tree state and the Y9 marker text.
- 19:57: read-only laptop checks: v22-proof.log (6/6 probes ok), laptop
  md5s match repo, infra still up (driver 274644, geckodriver 274657,
  ports 4451 and 8767 listening).
- 19:57-20:00: independent plan verification: 64/64 JSON commands parse,
  0 single quotes in js values, 0 node new-Function parse failures.
- 20:00-20:05: verdict written.

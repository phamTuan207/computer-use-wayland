# Council Member 3 (measurement) position: A1 narrow pilot

- Role: Council Member 3, measurement only.
- Date: 2026-11-21. Repo: computer-use-wayland, branch todolist-push.
- Status: COUNCIL POSITION. Not a plan change. The amendment texts below
  are proposed exact wording for Worker A1 synthesis. Nothing here runs a
  live arm, changes a fixture, or edits the checker.
- Read 2026-11-21: improvements/worker-a1-pilot-plan.md (DRAFT),
  improvements/working-structure-redesign-20261121.md section 5.7,
  improvements/speed-proto-pick4-summary.md sections 2-4,
  improvements/worker-w-council-c-measurement-20261121.md sections 2-3,
  improvements/a1-code-exec-dom-design.md (program caps and preflight),
  tests/realistic/a1-pilot/runbook.md,
  tests/realistic/a1-pilot/run-log-schema.md,
  tests/realistic/a1-pilot/check_run.py,
  tests/realistic/a1-pilot/preflight-probe.md,
  tests/realistic/fcc-k/test-01-spreadsheet-formula.md and its fixture
  tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html.
- Note on sources: the runbook, the run-log schema, and check_run.py exist
  as untracked files in the working tree at the time of writing. They were
  written after the pilot plan, and the plan points at them. My verdicts
  judge the plan PLUS those files as the current design, not the plan alone.
  No checker self-test directory or file exists yet (searched
  tests/realistic/a1-pilot/, 2026-11-21).
- Standing rules: no fabrication, unknown stays UNVERIFIED, no em dash or
  en dash anywhere in this file, never ydotool, no personal info in any
  commit.

## Verdict summary

| # | Design point (plan sections 5, 8, 10) | Verdict |
|---|----------------------------------------|---------|
| 1 | Median (n=3) and the 30% bar | AMEND |
| 2 | Six metrics all measurable | AMEND |
| 3 | Run-log JSONL schema sufficient to recompute the verdict | AMEND, freeze blocked until fixed |
| 4 | Recovery, refusal, misclick, session-death definitions | AMEND |
| 5 | Pre-registration freeze mechanism | AMEND |
| 6 | Checker self-test (known-good + known-bad) | BLOCK |
| 7 | Plan section 10 (what the pilot does NOT prove) | GO with amendment |
| 8 | Blinded checker (plan open question 5) | AMEND |

No design point below is judged unfixable except by the work listed. BLOCK
on point 6 means: do not rely on the two-directory self-test as the
checker trust gate. The fix is the matrix in section 6, not a redesign.

## 1. Is median (n=3) the right statistic

### 1.1 Verdict: AMEND

Keep the median as the headline statistic and keep the 30% bar, but the
plan as written overstates what n=3 can conclude. The median bar must be
kept as a PROCEED screen, not a proof bar, and three additions are
required: mandatory robustness reporting with a confidence label, the full
3+3 wall table in every verdict, and a fixed NO-GO language rule.

### 1.2 What the Pick 4 numbers actually show about noise

Arm-1 run-2 walls (speed-proto-pick4-summary.md section 2): P1 281.494s,
P2 43.609s, P3 43.857s, P4 312.513s. Max/min ratio 7.2x. The clean pair
P2+P3 mean is 43.733s (arm 1) against 41.744s (arm 2), a delta of only
minus 5%. The two inflated runs are inflated by incidentals, not by the
loop: P1 carries a 110.7s windows-retry think, P4 carries extra
verification rounds (112.7s think before od-verify, 69.7s before
byte-check). D1 carries a 139.2s finish think that is executor overhead,
not Pick 4. So the noise model that fits our own data is a mixture, not a
diffuse spread: same-task repeatability is good when no incident occurs
(P2 and P3 differ by under 6% across arms), and an incident multiplies a
run wall by about 7x. Incident rate in that tiny sample is 2 of 4 runs.
I use incident probability p = 0.25 and p = 0.50 in the model below, and
treat the 2-of-4 as UNVERIFIED as a rate, since n=4 cannot support one.

Two consequences follow. First, on Case A (pick4, about 43s clean), a 30%
cut is about 13s, while a single observed think incident is 110.7s to
139.2s, about 8 to 10 times the effect size. Case A can falsify a gross
failure and can detect a very large win, but it cannot confirm a 30% win.
Second, on Case B (f01, about 40 min hand-driven per run, Council C
section 2.6, extrapolated from 70 scripted steps at about 35s per agent
step, NOT measured), a 30% cut is about 12 min, which is larger than a
single think incident but still inside incident range. The pilot signal
lives in Case B. Case A is a cheap tripwire, not a second proof.

### 1.3 What n=3 lets us conclude (model calculation, not measured fact)

Model: lognormal run walls, 100,000 to 200,000 simulated trials, seed
20261121. Sigma is the log-scale spread: 0.2 is low noise, 0.5 moderate,
0.8 high. Effect 1.0 is the null (CODE and STEP identical), 0.7 is a true
30% cut, 0.5 is a true 50% cut. "Median-pass" means median CODE wall at
or below 0.70 times median STEP wall. "Robust" adds the condition that
every CODE run is at or below the STEP median. Joint figures are the
product of the two per-case rates, assuming independence across cases
(the cases use different runs, so this is a reasonable approximation, not
a measurement).

| Sigma | Effect | Per-case median-pass | Per-case median+robust | Joint both cases, median | Joint both cases, median+robust |
|---:|---:|---:|---:|---:|---:|
| 0.2 | null (1.0) | 2.9% | 2.4% | 0.1% | 0.1% |
| 0.2 | true 30% (0.7) | 50.0% | 47.9% | 25.0% | 23.0% |
| 0.2 | true 50% (0.5) | 96.2% | 96.0% | 92.6% | 92.1% |
| 0.5 | null (1.0) | 22.6% | 13.7% | 5.1% | 1.9% |
| 0.5 | true 30% (0.7) | 50.3% | 37.2% | 25.3% | 13.9% |
| 0.5 | true 50% (0.5) | 76.2% | 64.5% | 58.1% | 41.5% |
| 0.8 | null (1.0) | 31.7% | 17.0% | not computed | not computed |
| 0.8 | true 30% (0.7) | 49.9% | 31.4% | not computed | not computed |

Incident-mixture model (clean lognormal sigma 0.2, incident probability p
multiplies a run wall by 7x, the observed Pick 4 ratio): at p = 0.25, null
median-pass is 17.7% per case and median+robust is 11.4%; true-30
median-pass is 50.0% and median+robust is 34.0%. At p = 0.50, null median
is 28.2% and median+robust is 14.9%; true-30 median is 50.0% and
median+robust is 37.8%.

Three conclusions, all from the table, not from intuition.

(a) Power at exactly the bar is 50% per case, by construction. Any
consistent statistic tested at its own threshold passes half the time
when the true value equals the threshold. The joint both-cases power for
a true exactly-30% effect is about 25% (median only) or 14 to 23%
(median+robust). A real 30% effect will usually produce NO-GO. The pilot
is powered to detect a 50% cut (joint power 58 to 93%), not a 30% cut.
That is the single most important measurement fact about this design, and
the plan must say it.

(b) The false-GO rate per case under the null at realistic noise is 18 to
32% (median only) or 11 to 17% (median+robust). Joint across both cases
it is about 0.1 to 5% (median only) or 0.1 to 1.9% (median+robust). The
robustness condition roughly halves the false-GO rate at moderate to high
noise, at a real power cost (joint true-30 power 25.3% to 13.9% at sigma
0.5). It is worth having, but not as a hard gate, for the reason in (d).

(c) Raising n does NOT fix the power problem. Simulated median-pass at a
true 30% effect: n=3, 50.0%; n=5, 49.8 to 50.0%; n=10, 49.9 to 50.2%,
at sigma 0.2 and 0.5. Raising n cuts the null false-pass (sigma 0.5:
22.6% at n=3, 17.1% at n=5, 9.6% at n=10) and raises power for a 50%
effect, but at-boundary power stays 50% for any n. The dissent "just use
n=5" is therefore rejected as a cure. n=3 stands for the pilot, because
the pilot is a large-effect screen plus a noise measurement, not a
confirmatory run. The confirmatory run sizes n from the pilot measured
within-arm spread, and its bar must sit below the effect it is powered to
detect.

(d) The median tolerates exactly one incident in three runs. With incident
probability p, the chance that 2 or more of 3 runs in one arm are
incident-inflated (so the median itself is an incident value) is 15.6%
at p = 0.25 and 50% at p = 0.50. The robustness condition (every CODE run
at or below the STEP median) fires exactly when CODE had an incident run,
and an incident is harness noise (broker contention, stale-act retry,
extra verification rounds), not lever signal. Punishing the lever with a
hard gate for harness noise is the wrong attribution, and it costs power
(see (a)). So the robustness condition is mandatory reporting that sets
the confidence label and sizes the confirmatory run, not a hard gate.

### 1.4 Alternatives considered and rejected

- Mean: rejected. One 7x incident dominates the mean of 3. Arm-1 run-2
  mean is 170.368s against a clean-pair mean of 43.733s; the mean is 4x
  the typical run. The mean is reported as a diagnostic only.
- Min (best run per arm): rejected as a gate. It compares luck, not
  typical performance, and under the null the faster arm min wins by
  construction. Reported as a diagnostic only.
- All-3-below (max CODE below 0.70 times min STEP): rejected. Power is
  near zero at realistic noise even for a true 30% effect. It demands
  more consistency than the harness delivers.
- All-3-below-median-STEP as a hard gate: rejected, per (d) above. It
  becomes the confidence label instead.
- Geometric mean ratio as the gate: considered and set aside. It uses all
  three values and has slightly lower variance than the median under pure
  lognormal noise, but one 7x incident moves the geometric mean by a
  factor of 7 to the power 1/3 (about 1.9x), while the median does not
  move at all when the incident run is the largest value. Given
  incident-driven noise, the median is the right headline. The geometric
  mean ratio is reported as a diagnostic.

### 1.5 Exact amendment text (plan section 5, GO bar)

Replace plan section 5 in full with the following frozen text.

```
## 5. GO / NO-GO bar (PRE-REGISTERED, frozen before any run)

GO (pilot GO: proceed to the confirmatory run, not adoption) only if ALL
of these hold, per case, on BOTH cases:

1. Median wall time (CODE arm) at or below 0.70 times median wall time
   (STEP arm), per case. Medians are medians of 3 runs. All six walls per
   case are printed in the verdict table; a verdict that reports medians
   without the six walls is incomplete.
2. Pass rate (CODE) equal to or better than pass rate (STEP), per case,
   counted as passes out of 3, with the failure reason of every failed
   run printed alongside its count.
3. Total recovery steps across the 3 runs (CODE) not higher than total
   recovery steps across the 3 runs (STEP), per case. Recovery steps are
   defined in section 5A. The per-run counts are printed alongside the
   totals.

Any one failing on any case is NO-GO for that case. If one case passes
and the other fails, the verdict is PARTIAL with per-case verdicts, and
the confirmatory run does not proceed on the failed case shape.

Robustness check (mandatory reporting, NOT a gate): for each case, check
whether every CODE run wall is at or below the STEP median wall. Report
PASS or FAIL per case. A GO with the robustness check passed on both
cases is labeled GO, HIGH CONFIDENCE. A GO with the robustness check
failed on any case is labeled GO, LOW CONFIDENCE, and the confirmatory
run for that case uses double the n it would otherwise use. A GO, LOW
CONFIDENCE is never cited as evidence of a 30% effect, only as a proceed
signal.

Detection limit (frozen, read before interpreting any verdict): at n=3,
this pilot is powered to detect a 50% wall cut (joint both-cases power
about 58 to 93% in the lognormal model at sigma 0.2 to 0.5), not a 30%
cut. A true exactly-30% effect passes the median bar about 50% of the
time per case and about 25% of the time on both cases. A NO-GO therefore
means "not proven at pilot scale", never "batching does not work". A GO
means "proceed to the confirmatory run", never "a 30% speedup is proven".
The confirmatory run sizes n from the pilot measured within-arm spread,
and its bar sits below the effect it is powered to detect.

Diagnostics reported alongside every verdict, never gated on: mean wall
per arm, min wall per arm, geometric mean wall ratio, think-before-first-
program-call per CODE run, gap ms (wall minus summed service ms) per run,
and every run wall flagged incident-suspect when it exceeds twice its arm
median, with the reason taken from its log.
```

## 2. Are the six metrics all measurable

### 2.1 Verdict: AMEND

Two of the six are measurable as specified, three are measurable only in
a narrower sense than the plan claims, and one is expected to come back
UNMEASURED. The plan's section 8 must be corrected to say exactly that,
because a verdict that claims a metric it never measured is the
self-deception this council exists to prevent.

### 2.2 Metric by metric

| # | Metric (redesign 5.7) | Status in this pilot | What is wrong or missing |
|---|---|---|---|
| 1 | wall_ms | MEASURABLE, once frozen | run_start / run_end semantics are unfrozen (plan section 3 says session start submit to verified end state; Council C 3.1 says first action to verified end state, excluding setup; the schema does not say which line is which). Reset lines sit inside or outside the window, unfrozen. See section 3. |
| 2 | tool_calls | MEASURABLE with caveat | The checker counts tool_call lines the executor writes itself. That is executor self-report, not a count from the transcript by script as the plan and redesign require. A forgotten line reads as zero calls. Needs the frozen counting rule and the checker sanity check in section 3. |
| 3 | tokens_in / tokens_out | EXPECTED UNMEASURED | No evidence the executor session exposes a per-task token count. The schema makes the tokens op optional, which is correct. Do not estimate, do not multiply calls by a constant. If the tokens lines never appear, the verdict says UNMEASURED with the reason "session exposes no per-task count". |
| 4 | observation_cost_ms_by_type | PARTIALLY MEASURABLE | As implemented (mean elapsed_ms of observe lines by kind dom vs desktop), it measures harness service time only. The think before each observation, which is the dominant cost (87.8% loop share, INTERNAL), lives in the ts gaps, not in elapsed_ms. Kind has no image flag, so a desktop observe with a screenshot and one without are the same kind. The metric answers "how long does an observe take to serve", not "how much does observing cost the run". |
| 5 | vcr_flag | COMPUTABLE but MISLABELED | The checker computes a service-time ratio (assert elapsed plus last desktop observe, over act plus observe elapsed). Council C 3.5 defines VCR on wall time plus tool calls plus tokens for verification vs production. Think is excluded from both sides, so the implemented ratio is not the Council C ratio and will read small on runs where think dominates. Also "final desktop observe" is defined as the last desktop observe line, which need not be the verification observe in a STEP run that observes the desktop mid-task. |
| 6 | stall_minutes | MEASURABLE but WRONG CONSTRUCT | The checker sums inter-line gaps over 900s. That measures log silence, not lack of progress. A run stuck in a retry loop writing a line every minute scores 0 stall while making no progress. The schema has no progress_marker field (Council C 3.7 has one; this schema dropped it), and the schema text defines stall two incompatible ways in one paragraph (wall minus time covered by progress lines, and separately a gap over 15 min counts as stall). |

### 2.3 What to do with UNMEASURED metrics in the verdict (frozen rule)

Add the following text to plan section 8, verbatim.

```
UNMEASURED rule: a metric that was not measured is reported as
UNMEASURED with the reason, never as 0, never as an estimate, never
silently dropped. A GO verdict may stand with UNMEASURED diagnostic
metrics (tokens, observation cost detail) only if all three gate metrics
(wall, pass rate, recovery steps) are measured on all 12 runs. If any
gate metric is UNMEASURED on any run, the verdict for that case is
INCONCLUSIVE, not GO. Every UNMEASURED metric is listed in the verdict
with the question it leaves open. For this pilot the expected open
questions are: tokens (cost effect unknown; a wall win may be a
speed-for-cost trade, and the report must say so) and observation cost
by type in the think-inclusive sense (mechanism unknown; we do not know
whether a wall win came from fewer observations or from something else).
```

### 2.4 Exact amendments for metrics 4, 5, 6

- Metric 4: report two numbers per observe kind, service ms (mean
  elapsed_ms, as now) and gap-before ms (mean of ts difference from the
  previous line minus elapsed_ms, which is the think plus idle before
  that observation). Split kind by (kind, image) once the schema gains
  the image flag in section 3. Until the gap-before number exists, the
  metric is labeled "observation service cost", not "observation cost".
- Metric 5: rename the implemented number to vcr_service and label it as
  a service-time ratio. Do not call it VCR without the qualifier. The
  wall-time VCR of Council C 3.5 is UNMEASURED in this pilot unless the
  schema gains verification-phase timestamps (see section 3), and the
  verdict says so.
- Metric 6: rename the implemented number to silence_minutes (sum of
  inter-line gaps over 900s) until the schema gains a progress_marker
  field and the checker computes stall from progress coverage. Do not
  call it stall_minutes. A run that writes lines while making no progress
  must not be reported as having zero stall.

## 3. Is the run-log JSONL schema sufficient

### 3.1 Verdict: AMEND, freeze blocked until fixed

The schema file exists and is close to usable, which is more than the
plan alone offered. But the claim in the schema file, "the checker
recomputes every number from this log alone", is false as written, and
the schema cannot recompute every verdict number. The freeze must not
happen until the amendments in 3.3 land. This is an AMEND, not a BLOCK,
only because no live arm has run and every gap below is fixable before
the freeze commit.

### 3.2 What the schema gets right

- One line per action, observation, or event; ts in RFC 3339 UTC;
  run_id as 8-hex; op vocabulary frozen as a list.
- The arm label is never in the log; the case task is in run_start
  detail, which the checker needs to pick its end-state rule.
- tool_call lines give the checker a countable source for tool_calls.
- refusal, retry, recovery, misclick, session_death are separate ops,
  so the per-run fields are countable.
- program_submit carries chars and calls_so_far, so the 8192-char and
  3-call caps are checkable from the log.
- The checker recomputes wall from run_end.ts minus run_start.ts and
  counts the per-run fields from the log, which is the right shape.

### 3.3 Gaps: fields and rules that are missing

(a) No step_index. Two checkers cannot align "the third act" without it,
and the misclick cross-check in section 4 needs it. Add step_index,
1-based, sequential per run, on every line except run_start/run_end
markers, which carry step_index 0 and N+1 or are excluded. Freeze: every
line carries step_index, run_start is 0, run_end is the last index.

(b) No run_index and no agent. The log alone cannot say "run 2 of 3" or
who ran it. The manifest holds run_index, which is fine, but the schema
must say so, and the run dir must carry the executor identity somewhere
the unblinding step can verify (the manifest line gains an agent field;
the runbook section 0 already names the executor as one Codex session,
so the value is frozen text, not a new decision).

(c) No progress_marker. Stall cannot be computed as defined in redesign
5.7 without it. Add progress_marker, boolean, on every line. True when
the line records a step completed, an artifact written, or a checker
state changed. False for heartbeat-only, status-poll-only, and
waiting lines. A line with progress_marker false never covers time for
stall purposes. See section 2.4.

(d) The tokens op is described under metric 3 but is not in the Ops
list. Add it: tokens, detail {"in": n, "out": n}, at most one line per
run, written at run end from the session usage record if one exists.

(e) No think op. Think is derivable from ts gaps only if ts semantics
are frozen (see (g)), and there is no line type for a pure think turn
with no tool call. Add an optional think op, detail {"ms": n}, for model
turns that issue no tool call, so gap ms can be split into think and
idle. If the executor cannot distinguish think from idle, the think op
is omitted and gap ms is reported as "gap (think plus idle)".

(f) No program text or hash. program_submit logs chars but not content.
Without the program text, nobody can check the two rules the redesign
imposes: the program must not touch fixture internals to set the end
state directly, and the program must be composed fresh per run (runbook
section 5.1). Add to the run dir, not the log: commands.txt must contain
the full text of every program submitted, and the checker must verify
that the char count in each program_submit line equals the length of the
corresponding program text in commands.txt. If commands.txt is free
text, that check is impossible, so freeze commands.txt as JSONL, one line
per broker call or program submit, with the program text inline.

(g) ts semantics unfrozen. The schema says ts is "wall-clock time of the
line" without saying whether it is the op start or the op completion.
Freeze: ts is the wall time when the line is written, which is op
completion (run_start is the exception: ts is the task start instant).
Then think-before-op equals (ts of the next line minus ts of the current
line) minus elapsed_ms of the next line. The checker must validate that
ts is non-decreasing down the file and flag a problem otherwise; a
negative wall is a logging failure, not a number.

(h) elapsed_ms semantics unfrozen. Freeze: elapsed_ms is harness service
time for the op (round trip, excluding model think before the call).
Settle sleeps inside the op count inside elapsed_ms. run_start and
run_end carry elapsed_ms 0.

(i) No fixture, harness, or checker version. Add a setup line set: the
run dir carries setup.json with fixture name plus md5, browser (managed
Chromium, CDP endpoint), relay or harness commit, check_run.py version
(the freeze commit hash), and the runbook version. The checker reads
setup.json and reports its fixture md5; a run whose fixture md5 differs
from the frozen value is INVALID, not FAIL.

(j) No run cap, timeout, or invalidation fields. run_end detail gains
reason values frozen as: done, failed, timeout, invalid, killed. The
timeout and invalid reasons are defined in section 4.

(k) No observation image flag. observe detail gains "image": true or
false, so metric 4 can split screenshot observes from DOM reads. Kind
stays dom or desktop.

(l) No verification-phase timestamps. If the wall-time VCR is ever to be
measured, the schema needs a verify_start line and a verify_end line
bracketing the final verification phase. For this pilot, add the two
lines as optional; without them, wall-time VCR stays UNMEASURED per
section 2.4.

### 3.4 Contradictions between the plan, the schema, the runbook, and the checker

These are not matters of taste. Each one makes two artifacts disagree
about the same run, and the freeze must resolve each in writing.

1. Reset lines vs the checker first-line rule. The runbook says "log
   each reset as a run-log line", and the plan section 4 requires a
   between-run reset. The checker FAILs any log whose first line is not
   run_start. So a reset line placed at the top of run-log.jsonl fails
   the run. Resolution (frozen): reset lines go in a separate file,
   setup-log.jsonl, in the same run dir, never in run-log.jsonl. Wall
   excludes reset time. run-log.jsonl starts with run_start, always.
2. Case label ban vs case_task. The runbook section 6 says "do NOT write
   the arm label, the case label, or any hypothesis in the run
   directory", while the schema requires run_start detail case_task
   ("pick4" or "f01") in the log, and the checker needs it. Resolution:
   the ban covers the ARM label only. case_task is allowed in run_start
   and nowhere else in the run dir. Amend runbook section 6 to say so.
3. Stall defined twice. The schema text defines stall_minutes as wall
   minus time covered by progress lines, and in the next sentence as a
   gap over 15 min counting as stall. The checker implements only the
   second (sum of gaps over 900s). Resolution: adopt the renames in
   section 2.4 (silence_minutes for the implemented number) and add the
   progress_marker field for a real stall number later.
4. "Recomputes every number from this log alone" is false. Pass/fail
   needs end-state.json. Arm medians need the sealed manifest. Program
   integrity needs commands.txt. The f01 cell list needs the frozen plan.
   Resolution: restate the claim in the schema file as: "the checker
   recomputes every per-run number from the run dir (run-log.jsonl plus
   end-state.json plus verify.png plus setup.json), and every arm-level
   number from the run dirs plus the sealed manifest plus the frozen
   thresholds, with no executor memory." The recompute procedure is then:
   check each run dir, join run-id to arm from the manifest, apply the
   frozen GO bar. Each step is a script, and the join script is separate
   from check_run.py.
5. The plan names three f01 cells (E5, E6, E7); the checker enforces six
   (E2, E3, E4, E5, E6, E7); the spec expected end state lists six.
   Resolution: freeze the six-cell list. The fixture rounds AVERAGE with
   Math.round, so E6 = 621333 exactly, verified in the fixture source
   2026-11-21. The plan section 2 must be amended to name all six.
6. The runbook 30-minute cap vs the f01 estimate. Runbook section 7
   stops any run over 30 minutes wall and marks it failed (timeout).
   Council C estimates f01 at about 40 minutes hand-driven per run
   (extrapolated, NOT measured). A cap below the plausible control-arm
   wall manufactures timeouts in the STEP arm. Resolution: per-case caps
   in section 4 (Case A 15 min, Case B 60 min), with the censored-data
   rule for timed-out runs.
7. Session death: runbook says STOP the run, mark failed, report to
   Muse, do not start the next run. The plan section 8 lists session
   deaths as a per-run count, which implies a run can carry deaths and
   still complete. Resolution: the one-restart rule in section 4.

### 3.5 Exact amendment text (schema line shape)

Replace the schema "Line shape" section with:

```
{"ts": "<RFC 3339 UTC, op completion>", "run_id": "<8-hex>",
 "step_index": <int>, "op": "<op>", "elapsed_ms": <number>,
 "ok": <bool>, "progress_marker": <bool>, "detail": <any>,
 "error": <string|null>}

- ts: wall time the line is written (op completion). run_start is the
  exception: its ts is the task start instant. ts must be non-decreasing
  down the file.
- step_index: 1-based per run, sequential. run_start carries 0.
- elapsed_ms: harness service time for the op, excluding model think
  before the call. run_start and run_end carry 0.
- progress_marker: true when the line records a step completed, an
  artifact written, or a checker state changed; false for heartbeat,
  status-poll, and waiting lines.
- New ops: tokens (detail {"in": n, "out": n}, at most one per run),
  think (detail {"ms": n}, optional, model turn with no tool call).
- observe detail gains "image": true or false.
- act detail gains "target_ref" and "intended" (section 4, misclicks).
- run_end detail reason is one of: done, failed, timeout, invalid,
  killed.
- Reset lines live in setup-log.jsonl, never in run-log.jsonl.
- The run dir also carries setup.json (fixture name plus md5, browser,
  harness commit, checker version, runbook version) and commands.txt as
  JSONL (one line per broker call or program submit, program text inline).
- The checker recomputes every per-run number from the run dir and every
  arm-level number from the run dirs plus the sealed manifest plus the
  frozen thresholds, with no executor memory.
```

## 4. Are recovery, refusal, misclick, and session-death defined tightly enough

### 4.1 Verdict: AMEND

No. The current design has op names, not definitions. The schema lists
ops called recovery, retry, refusal, misclick, session_death, and the
checker counts lines with those ops. But nothing says when the executor
writes one instead of another, what counts as one unit, or how the CODE
arm logs corrective actions that happen inside a program with zero model
round trips. Two checkers, or one checker and one executor, will compute
different numbers from the same run. The worst gap is structural: the
lever under test (local retry inside the program) hides exactly the thing
gate 3 measures (recovery steps). If in-program retries are not logged
with the same vocabulary as STEP-arm retries, gate 3 is biased toward
CODE by construction, and a CODE win on recovery is meaningless.

### 4.2 Frozen definitions (exact text for the plan, the schema, and the runbook)

Add the following block to the plan as section 5A, and copy it into the
schema file and the runbook. One definition, three places, no paraphrase.

```
## 5A. Frozen counting definitions

Step: one logged action at action level. Each DOM action (click, fill,
assert, navigate, observe) is one step, whether issued by the model
(STEP arm) or by a program (CODE arm). A program that executes 5 DOM
actions logs 5 act lines, one per action, plus its program_submit line.
A model turn that issues 4 tool calls logs 4 tool_call lines. Counting
is at action level in both arms, so the counts are comparable.

Recovery step: one corrective action taken because a preceding action
returned ok:false, or because an observation or assert showed the state
diverging from the intended state. The original failed action does NOT
count as recovery. The diagnostic re-observe after a failure counts.
The re-try of the failed action counts. A state repair counts. A
recovery step is logged exactly once, as one line: op retry if it
repeats the same action (same intent, same target) after a refusal or
failure, op recovery otherwise. Recovery steps for the gate (plan
section 5, condition 3) equal count(retry lines) plus count(recovery
lines), summed across the 3 runs per case per arm.

Planned branch (NOT recovery): a step the runbook or spec prescribes
conditional on observed state. In Case B, the wrong-formula diagnosis
is a planned branch: re-read E7, and if it holds text, replace COUNT
with COUNTA and re-read. Those steps are forward steps, logged as act
lines, never as recovery. If the same COUNTA fix has to be attempted a
second time because the first attempt failed, the second attempt IS
recovery. The runbook must mark every planned branch in the case
procedure before run 1, so the checker and the executor agree on which
steps are planned.

Refusal: one request that returns an error without executing any action.
Completed 0 with an error present. Examples from Pick 4: stale
observation (observation older than 90s), sequence_gap, task_stopped,
unsupported_command, invalid_lease. A refusal is logged as one refusal
line with detail.reason carrying the exact error text. An action that
executed and then produced the wrong state is NOT a refusal; it is a
failure, and its correction is recovery.

Retry: one repeated attempt of the same action (same intent, same
target) after a refusal or failure. Logged as op retry, detail
after_refusal carrying the exact error text of the refusal or failure
it follows. A retry is also a recovery step for gate purposes (see
above). A retry that itself fails and is tried a third time logs a
second retry line.

Misclick: one click or fill action that executed on an element other
than the one the step intended. Intended means the element named in the
runbook step (STEP arm) or the element the program selected as its
target (CODE arm). Every act line for a click or fill carries
detail.target_ref (the ref acted on) and detail.intended (the intended
element). A misclick is logged as one misclick line with detail
{intended, actual}. The checker counts misclick lines. Limitation,
stated in every verdict: a misclick the executor never detects is never
logged, so a run with zero misclick lines is reported as "none
detected", never as "0 misclicks". Until act lines carry target_ref and
intended, misclicks are UNMEASURED, not zero.

Session death: the broker session or the browser session terminates
before the verified end state, so the run cannot continue without a
restart. Logged as one session_death line with detail {what:
"browser" or "broker", error: exact error text}. One restart per run is
allowed: the death is counted, the restart steps are recovery steps,
and wall time keeps running. A second death in the same run ends the
run as FAIL with run_end reason failed. A restart that itself fails to
start ends the pilot: STOP, report to Muse, do not start the next run.
(This replaces runbook section 7 "STOP on death". A death is a cost to
be counted, not a reason to waste a pilot, but a second death is a
harness failure, not a lever signal.)

Pass: the blinded checker finds the frozen end state in end-state.json
(Case A: result_text contains "pick4-ok". Case B: E2=540000, E3=574000,
E4=750000, E5=1864000, E6=621333, E7=3) and verify.png exists and is
non-empty, and the run log parses and starts with run_start and ends
with run_end. A run that reaches the end state by writing fixture
internals directly (setting state rather than acting through the UI or
DOM ops) is FAIL by fabrication; the program text in commands.txt is
the evidence, checked at unblinding by Worker A1, not by the checker.

Fail: any run that is not a pass. The run_end reason says why: failed
(wrong end state or driver failure), timeout, invalid, killed.

Timeout: wall time exceeds the per-case cap (Case A 15 min, Case B 60
min). The run is STOPPED at the cap, run_end is written with reason
timeout and ts at the kill instant, and the run is FAIL. A timed-out
run wall is censored data: its true wall is greater than the kill-time
wall, not equal to it. In the verdict table it is printed with a ">"
flag. If the median of an arm is itself a timed-out run, that median
is reported as a lower bound and the GO bar cannot pass on that case;
the case verdict is INCONCLUSIVE, not GO.

Invalid: a run voided for a cause outside the arm under test. Only
three causes qualify: (a) fixture or harness fault found after the run
(fixture md5 mismatch, wrong fixture served, broker outage affecting
both arms); (b) executor violated the runbook (copied a program
verbatim, used the wrong arm procedure, opened the sealed manifest);
(c) run evidence lost through no fault of the arm (log file destroyed).
An INVALID run is logged with reason invalid, preserved, and re-run
once. Two invalidations of the same case-arm pair stop that pair and
the pair is UNMEASURED. A run that fails because the arm did the task
wrong is FAIL, not INVALID.

Incident-suspect run: a run whose wall exceeds twice its arm median.
Flagged in the verdict with the reason taken from its log (for example
windows-retry think, extra verification rounds, session death). The
flag is diagnostic; the run stays in the median.
```

### 4.3 Three consequences the definitions force

- The CODE program must emit one act line per DOM action it executes,
  including retries, with the same op vocabulary as the STEP arm. If the
  program retries internally without logging, gate 3 is void. The
  preflight probe (plan section 7) must verify that a program logs its
  internal retries, not only that it preflights correctly.
- The runbook line "A retry is a recovery step, not a failure" is
  consistent with the definitions above (a retry counts toward the
  recovery total, and the run is not failed for retrying). The runbook
  must not also log a recovery line for the same action as the retry
  line; one corrective action is exactly one line, or the gate double
  counts.
- The 30-minute run cap in runbook section 7 is replaced by the per-case
  caps above. The 40-minute f01 estimate is an extrapolation (Council C
  section 2.6), NOT a measurement, so the 60-minute cap is set with the
  explicit note that if STEP f01 runs cluster near the cap, the cap
  itself is a finding and the pilot is re-sized, not silently passed.

## 5. Pre-registration: what is frozen, where, and what counts as a violation

### 5.1 Verdict: AMEND

The plan has the right shape (thresholds frozen before any run, cases
frozen, sealed manifest, checker blinded) but no mechanism that makes
the freeze checkable. A freeze that nobody can verify after the fact is
a promise, not a control. The amendments below turn it into a checkable
artifact.

### 5.2 What is frozen (exact list)

The freeze commit on todolist-push contains, with no exceptions: the
amended pilot plan; the amended run-log schema; the amended runbook; the
frozen check_run.py; the checker self-test matrix and its expected
outputs (section 6); the frozen fixtures (pick4 md5
91b2f92945c167306a13ae32977a9bf3, f01 fixture md5 recorded at freeze);
the f01 spec file; the GO bar in full text; the definitions in section
4.2; the program caps (8192 chars, 3 calls); the per-case run caps
(Case A 15 min, Case B 60 min); the run order (STEP first, alternating,
Case A runs 1-6 then Case B runs 1-6); the invalidation rules; the
unblinding procedure. The freeze commit hash is recorded in every run
report and in the verdict.

### 5.3 Freeze mechanism (exact)

1. FREEZE.md is committed at the freeze commit. It lists, per frozen
   file, the file path and its sha256 hash, plus the GO bar in full text,
   plus the freeze commit hash itself once committed (added in a second
   commit that changes nothing else, or recorded in the verdict; the
   hashes of the frozen files must not change between the two).
2. Manifest lines are written by a script, not by hand. The executor
   calls the script at run start; the script generates the random 8-hex
   run_id, appends one line {"run_id", "case", "arm", "run_number",
   "agent", "started_at"} to runs/manifest-sealed.jsonl, and prints the
   run_id. Hand-written manifest lines are forbidden, because a
   hand-written line can carry a typo that breaks the join, and a
   hand-written file can be edited without a trace.
3. The unblinding step is a separate script, run by Worker A1 only after
   all 12 runs are checked. It verifies: every run dir id appears
   exactly once in the manifest; run_number runs 1 to 3 per case-arm
   with no gaps; started_at is non-decreasing in run order; the manifest
   has exactly 12 lines. Only then does it join run-id to arm and
   compute the arm medians. The join output is a new file, never an edit
   to the manifest.
4. Run dirs are immutable after run_end. Any correction goes in a
   separate amendments file, never by editing run-log.jsonl,
   end-state.json, or verify.png. check_run.py contains no reference to
   the manifest path (verified by grep in the self-test), so the checker
   cannot open it even by accident.
5. Checker outputs are sealed per run until unblinding. The checker
   writes its full output to runs/<run-id>/check-output-sealed.json,
   which no human reads before unblinding. This is required because the
   output leaks the arm (program_calls above 0 implies CODE), so reading
   it early unblinds the reader even though the script itself does not
   branch on arm.

### 5.4 What counts as a violation (frozen list)

- Changing the GO bar, the case list, the fixture files, the program
  caps, the run caps, the run order, or the checker verdict rules after
  run 1 starts.
- Editing any frozen file without an AMENDMENT commit that names the
  file, the change, the reason, and whether any completed run is
  affected.
- Opening runs/manifest-sealed.jsonl after writing it, by the executor
  or the checker, before all 12 runs are checked.
- Reading a sealed checker output before unblinding.
- Re-running a failed run and replacing it. The original stays, marked
  FAIL or INVALID with its reason, and the re-run is a new run only when
  the run was INVALID under section 4.2.
- Editing a run dir after its run_end.
- Changing the checker to reclassify a run after seeing that run output.

### 5.5 Amendment procedure

Amendments BEFORE run 1 are free: commit them, update FREEZE.md hashes,
record the new freeze commit hash. Amendments AFTER run 1 starts are
allowed only for (a) a safety stop, or (b) a logging fix that does not
change thresholds, cases, caps, run order, or checker verdict rules.
Each requires an AMENDMENT commit plus one line in the verdict stating
what changed, when, and whether any completed run is affected. Any run
completed before such an amendment is flagged, and if the amendment
could have changed that run outcome, the run is marked INVALID and
re-run once under the new rule, with the original preserved. If a
threshold was wrong, the pilot is re-run as a new pre-registered pilot
with a new freeze commit; the old pilot stays NO-GO or INCONCLUSIVE.
Thresholds are never moved to rescue a run.

## 6. Is the checker self-test enough

### 6.1 Verdict: BLOCK

As specified (one known-good run directory plus one known-bad run
directory), no. The self-test as specified can pass while the checker
fails on real runs in at least nine named ways, listed below. This is a
BLOCK on relying on the two-directory test as the trust gate, not a
BLOCK on the checker itself. The fix is the matrix in 6.3, which must
land before the freeze.

### 6.2 Named ways the checker passes its self-test and fails on real runs

(a) Empty metrics on any problem. check_run.py returns metrics {} when
any of run-log.jsonl, end-state.json, or verify.png is missing, and also
when any log line is not JSON, when the log does not start with run_start
or end with run_end. A timeout run with a good log but a missing
verify.png therefore loses its wall time entirely, and its wall never
enters any median. A known-good plus known-bad test never exercises this
path.
(b) Stall measures silence, not progress (section 2.2, metric 6). A
retry loop writing a line every minute scores 0. A good/bad test does
not catch a wrong-construct metric, because both test dirs score 0.
(c) VCR is a service-time ratio mislabeled as VCR (section 2.2, metric
5). Both test dirs compute it without complaint.
(d) Arm leak through the output. The checker outputs program_calls,
program_chars, and think_before_program_ms, which are zero or
UNMEASURED in STEP runs and nonzero in CODE runs. Anyone reading the
output infers the arm. The self-test does not test blinding at all.
(e) No monotonic-ts validation. A log with ts going backward yields a
negative wall, and the checker reports it as a number. The good/bad
test never has backward ts.
(f) No golden-metrics check. A checker that computes wall wrong by a
factor of 1000 still passes a good/bad test, because that test only
checks PASS vs FAIL, not the numbers.
(g) No determinism check. A checker that reads timestamps at check time
or iterates a dict in hash order could vary run to run.
(h) Missing-file handling returns {} even when the log is fine. If
end-state.json is missing but the log is complete, the metrics are still
computable and should be reported alongside the FAIL, so the run wall
is not lost.
(i) No under-logging detection. A run with act lines but zero tool_call
lines means the executor forgot to log tool calls, and the checker
reports tool_calls 0 without flagging it. A run with zero observe lines
reports observation cost UNMEASURED, which is correct, but a run with
acts and no tool_call lines is a logging failure, not a zero.
(j) The "final desktop observe" rule for VCR is untested. In a STEP run
with desktop observes mid-task, the last desktop observe may not be
the verification observe, and the self-test has no such run.

### 6.3 Required self-test matrix (exact, frozen before the freeze commit)

One command runs the whole matrix. Each case is a synthetic run dir
with hand-computed expected output frozen alongside it. The checker
must match every expected value exactly, not approximately. The matrix
is re-run after ANY checker change, and a checker change after run 1
starts follows the amendment procedure in section 5.5.

- T1 known-good pick4: PASS. Golden metrics hand-computed: wall,
  tool_calls, recovery, refusals, misclicks, deaths, retries, vcr_service,
  silence_minutes. Checker output must match exactly.
- T2 known-bad pick4 (result_text without "pick4-ok"): FAIL, metrics
  still reported.
- T3 known-good f01 (all six cells): PASS, golden metrics as T1.
- T4 f01 with E7 wrong: FAIL, metrics still reported.
- T5 timeout run: log ends with run_end reason timeout, wall at the cap.
  Checker must FAIL the run AND still report metrics (wall present, not
  {}). This case forces the fix for failure mode (a).
- T6 session death then FAIL: session_death line present, run_end reason
  failed. Checker must count deaths 1 and FAIL.
- T7 missing run-log.jsonl: FAIL. Metrics {} is acceptable here, because
  there is nothing to compute from.
- T8 missing end-state.json with a complete log: FAIL, metrics computed
  from the log and reported. This forces the fix for failure mode (h).
- T9 empty verify.png: FAIL, metrics reported.
- T10 malformed JSON line: checker must report the line number and FAIL,
  not crash with a traceback.
- T11 arm-leak test: take T1, produce two versions that differ only in
  arm-revealing lines (one with program_submit lines, one without).
  PASS/FAIL and all arm-neutral metrics must be identical across both
  versions. This tests blinding.
- T12 determinism: run the checker twice on T1, byte-identical stdout.
- T13 out-of-order ts: checker must flag a problem (ts not
  non-decreasing), not silently report a negative wall.
- T14 zero observe lines: observation cost must be UNMEASURED, not a
  crash (division by zero).
- T15 act lines with zero tool_call lines: checker must flag "tool_call
  lines missing" as a problem. This forces the fix for failure mode (i).
- T16 unknown op value in the log: checker must ignore the line for
  metrics, not crash, and must not count it as a step.

Also frozen: the checker must contain no reference to the manifest path
(verified by grep in the self-test run), and the self-test expected
outputs are committed in the freeze commit, so a later checker change
that alters an output is visible as a diff.

### 6.4 Answer to plan open question 5 (is the blinded checker really blind)

Strictly, no, not as the artifacts stand. The log shape differs by arm
(CODE runs have program_submit lines and fewer, longer ops; STEP runs
have per-step observe and act lines), and the checker output leaks the
arm through program_calls, program_chars, and think_before_program_ms.
The checker script itself does not branch on arm, so its PASS/FAIL rule
is unbiased, and PASS/FAIL depends only on end-state.json values. The
blinding failure is on the human side: anyone who opens a run dir or
reads a checker output before unblinding knows the arm. The fix is the
one in section 5.3 item 5 (sealed checker outputs, nobody reads them
before unblinding) plus a log-shape rule: the CODE program must emit one
act line per DOM action with the same op vocabulary as STEP, so the two
arms logs differ in counts, not in kinds, and program_submit framing
lines are excluded from the checker metric input (they are counted only
for the program caps). The self-test T11 verifies this.

## 7. Plan section 10 verdict

GO with amendment. Section 10 is correct in its limits (Chromium only,
n=3 small, GO is a pilot GO, Pick 1 minus 53% was n=1 and the Pick 4
mean delta was inflated by incidentals with the clean pair at minus 5%).
Add the following paragraph to section 10, verbatim.

```
Power note: at n=3 this pilot is powered to detect a 50% wall cut, not
a 30% cut. A true exactly-30% effect passes the median bar about 50% of
the time per case and about 25% of the time on both cases. A NO-GO is
therefore reported as "not proven at pilot scale", never as "batching
does not work". A GO is reported as "proceed to the confirmatory run",
never as "a 30% speedup is proven". The confirmatory run sizes n from
the pilot measured within-arm spread.
```

## 8. Dissent considered

- "Demand n=5 or n=10." Rejected as a cure. Simulated at-boundary power
  stays about 50% per case at n=3, n=5, and n=10 (section 1.3). Larger n
  cuts the null false-pass and raises power for a 50% effect, but it
  does not make a 30% effect detectable at a 30% bar, and f01 runs cost
  about 40 minutes each extrapolated. The right response to a NO-GO is
  the confirmatory run sized from measured spread, not a bigger pilot.
- "Use the mean, it uses all the data." Rejected. One 7x incident
  dominates a mean of 3 (arm-1 run-2 mean 170.368s vs clean-pair mean
  43.733s). The mean is a diagnostic only.
- "Use the min, it shows the best the lever can do." Rejected as a gate.
  It compares luck. Reported as a diagnostic only.
- "Drop Case A, it is too noisy." Rejected. Case A is cheap and can
  falsify a gross failure at the smallest scale. Its detection limit is
  stated in section 1.2 instead of hiding it: a 30% cut on a 43s task
  is about 13s, smaller than one think incident.
- "Make the robustness check a hard gate." Rejected. It fires on harness
  incidents, which are not lever signal, and it costs joint true-30
  power (25.3% to 13.9% at sigma 0.5). It becomes a confidence label and
  a confirmatory sizing input instead.
- "Gate on tokens or observation cost." Rejected. Tokens are expected
  UNMEASURED and observation cost is partial (section 2). Gating on them
  would make every pilot NO-GO by instrumentation, not by lever.
- "The checker is a deterministic script, so blinding does not matter."
  Rejected. The script is unbiased, but the humans handling its output
  are not blind (section 6.4). Sealed outputs are cheap and required.

## 9. Consolidated amendment checklist for Worker A1 synthesis

In order, before the freeze commit. Each item names the file it changes.

1. Plan section 5: replace with the GO bar text in section 1.5.
2. Plan: add section 5A with the definitions in section 4.2.
3. Plan section 2: name all six f01 cells (E2, E3, E4, E5, E6, E7).
4. Plan section 8: add the UNMEASURED rule in section 2.3; rename the
   implemented metrics per section 2.4 (observation service cost,
   vcr_service, silence_minutes).
5. Plan section 10: add the power note in section 7.
6. Schema file: apply the line-shape amendment in section 3.5 (step_index,
   progress_marker, tokens op, think op, image flag, target_ref and
   intended on act lines, run_end reasons, setup-log.jsonl for resets,
   setup.json, commands.txt as JSONL with program text inline).
7. Schema file: restate the recompute claim per section 3.4 item 4.
8. Runbook section 6: the label ban covers the ARM label only; case_task
   in run_start is allowed.
9. Runbook section 7: replace the stop-on-death rule with the one-restart
   rule, and replace the 30-minute cap with the per-case caps (Case A
   15 min, Case B 60 min).
10. Runbook section 5.1: one corrective action is exactly one log line
    (retry or recovery, not both).
11. check_run.py: compute metrics from whatever files exist (fix modes
    (a) and (h)); validate ts non-decreasing; flag zero tool_call lines
    with act lines present; exclude program_submit framing lines from
    metric input; report vcr_service and silence_minutes under those
    names.
12. New: checker self-test matrix T1 to T16 in section 6.3, one command,
    expected outputs frozen.
13. New: FREEZE.md plus the manifest-writing script plus the unblinding
    script, per section 5.3. Checker outputs sealed per run until
    unblinding.
14. Freeze commit with everything in section 5.2. No live arm runs
    before it.

## Work log (Asia/Ho_Chi_Minh, wall clock)

- 18:20, T+0min: task received. Read the pilot plan, the redesign
  section 5.7, the Pick 4 summary sections 2-4, and Council C sections
  2-3.
- 18:22: found the runbook, run-log schema, and check_run.py as untracked
  files in the working tree; read all three plus the preflight probe
  note, the f01 spec, and the f01 fixture source.
- 18:24: verified the f01 fixture rounds AVERAGE with Math.round, so
  E6 = 621333 exactly, and the spec expected end state lists six cells,
  matching the checker.
- 18:26: ran the lognormal simulation (200,000 trials, seed 20261121)
  for the median bar at sigma 0.2, 0.5, 0.8, plus the incident-mixture
  model; ran a second pass for joint both-cases rates and a third pass
  for n=5 and n=10. All numbers in section 1 are from those runs.
- 18:34: wrote this position paper, committed, pushed.

## Sources

Internal (repo, accessed 2026-11-21):

- improvements/worker-a1-pilot-plan.md (DRAFT, untracked at time of
  writing).
- improvements/working-structure-redesign-20261121.md section 5.7,
  commit fb00973.
- improvements/speed-proto-pick4-summary.md sections 2-4 (arm-1 run-2
  4/4, arm-2 4/4, clean pair P2+P3, 139.2s finish think, 110.7s
  windows-retry think).
- improvements/worker-w-council-c-measurement-20261121.md sections 2-3
  and 3.7 (six metrics, run-log schema with progress_marker, 44-run
  Exp1, f01 about 40 min extrapolated).
- improvements/a1-code-exec-dom-design.md (program caps, preflight,
  think-before-code-exec about 18s vs 8.59s).
- tests/realistic/a1-pilot/runbook.md, run-log-schema.md, check_run.py,
  preflight-probe.md (untracked files, read 2026-11-21).
- tests/realistic/fcc-k/test-01-spreadsheet-formula.md and
  tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html (Math.round
  on AVERAGE, six-cell expected end state).

Model calculations (this paper, not measured fact): lognormal wall model
and incident-mixture model, section 1.3, 100,000 to 200,000 trials, seed
20261121. The model assumptions are stated with the numbers. The Pick 4
walls the mixture is calibrated on are measured (speed-proto-pick4
summary, section 2); the incident probabilities 0.25 and 0.50 are
assumed, and the 2-of-4 incident rate in that sample is UNVERIFIED as a
rate.

## Files

- This paper: improvements/worker-a1-council-measurement-20261121.md
  (repo computer-use-wayland, branch todolist-push)

# Experiment 3.4.1 E1: planning separated from execution

Todolist item 3.4.1 E1 asks: separate the deliberation (many
agents planning) from the execution (one agent executing), and
test whether it increases speed and accuracy.

## Design

Six real browser tasks against offline fixtures, each with a
written goal and a programmatic checker that reads the final DOM
state. The same checker (tests/exp341/checks.py) judges both arms.
Fixtures, scripts, plans and the runner live in tests/exp341/.

- Task 1, registration form fill (easy).
- Task 2, table filter and sort (medium, with an ordering trap:
  sorting before filtering loses the sort).
- Task 3, three step signup wizard (medium hard). The prefilled
  email has no @ sign and the prefilled password is too short, so
  both defects are visible in the DOM before any action.
- Task 4, settings toggles, select, slider, number (medium).
- Task 5, draft editor (hard, deliberate trap). The big primary
  button "Publish now" has data-action "archive" and does not
  save the draft. The plain "Save draft" button does.
- Task 6, cart with quantities and a discount code (hard).

Arm A, single agent: one script per task, plan and execution
interleaved, a fresh DOM observation before every action, reacting
to whatever the observation shows (validation errors, a failed
checker), with each recovery counted as a retry.

Arm B, planned execution: a written plan per task
(tests/exp341/plans/), each recording at least two alternatives
considered and the one chosen, with a JSON step list. One executor
runs the whole plan in batches and takes an observation only at
the plan checkpoints: start, middle, end (3 per task). The
executor has no reactive recovery logic.

An observation is one full DOM state read used to decide the next
action. The final checker read is identical for both arms and is
not counted as an observation.

Runs: 3 runs per arm per task, 36 runs total, headless
Firefox 160.0.1, geckodriver 0.37.1, Selenium 4.53.0, on the
clone2 VM (shared CPU, so absolute times carry noise; medians of
3 are reported). Run window 2026-11-21T15:34:38Z to 15:37:23Z.
Raw per run data: tests/exp341/results.json.

Two protocol facts worth recording. run_all.py always ran arm A
before arm B for each task, sequentially, with no interleaving or
randomization, so any warm up or cache drift across a task would
favor one arm systematically instead of averaging out. And both
arms are deterministic scripts, so the 3 runs of a task are near
identical by construction; the 18/18 success figures below carry
less statistical weight than the same figures from a live,
nondeterministic agent would.

Harness fix, made after review: the first version of run_all.py
recorded an arm that crashed without printing its RESULT line as
a run with observations, actions and retries silently set to 0,
which would have corrupted the medians. The runner now records a
crash as a failure with the counts it cannot know set to null,
and computes medians over the runs that reported. The recorded
36 runs were not affected: every run printed a RESULT line, and
tests/exp341/results.json is unchanged.

Scope limit, stated plainly: both arms are scripts. No live LLM
sat in either loop. The planning council is represented by the
written alternatives analysis in each plan file, and plan
authoring time is not in the runtime numbers. What this experiment
measures is the structural effect of the split: how many
observations and actions each style needs, how often each needs a
retry, and the resulting execution time when an observation is a
cheap DOM read. In a real agent loop an observation is an LLM
call costing seconds, so the observation count is the number that
scales; the elapsed column here understates that effect by
construction.

## Results, medians of 3 runs

| Task | Arm | Success | Elapsed s | Steps only s | Observations | Actions | Retries (3 runs) |
|---|---|---|---|---|---|---|---|
| 1 form | A | 3/3 | 4.1308 | 0.9352 | 7 | 7 | 0 |
| 1 form | B | 3/3 | 4.0361 | 1.0362 | 3 | 7 | 0 |
| 2 table | A | 3/3 | 3.6180 | 0.6995 | 2 | 2 | 0 |
| 2 table | B | 3/3 | 3.4442 | 0.6422 | 3 | 2 | 0 |
| 3 wizard | A | 3/3 | 3.9104 | 0.9750 | 9 | 9 | 6 |
| 3 wizard | B | 3/3 | 4.0024 | 0.8785 | 3 | 7 | 0 |
| 4 settings | A | 3/3 | 3.8615 | 1.0487 | 6 | 6 | 0 |
| 4 settings | B | 3/3 | 3.6842 | 0.9526 | 3 | 6 | 0 |
| 5 trap | A | 3/3 | 3.7911 | 0.8294 | 4 | 4 | 3 |
| 5 trap | B | 3/3 | 3.5115 | 0.6292 | 3 | 2 | 0 |
| 6 cart | A | 3/3 | 3.7655 | 0.8453 | 5 | 5 | 0 |
| 6 cart | B | 3/3 | 3.6264 | 0.7694 | 3 | 5 | 0 |
| Total of medians | A | 18/18 | 23.0773 | 5.3331 | 33 | 33 | 9 |
| Total of medians | B | 18/18 | 22.3048 | 4.9081 | 18 | 29 | 0 |

## Reading the numbers

Accuracy, final state: a tie, 18 of 18 runs for both arms. Arm A
recovered from every mistake it made, so the checker alone does
not separate the arms. One part of that recovery is an artifact
of the harness, disclosed here: in task 5 the arm A script calls
the shared checker itself in the middle of the run and uses the
failed verdict as the trigger to reload and redo. A real agent
does not carry the ground truth checker in that form; it would
have to notice the wrong state from its own observations. This
biases final accuracy in arm A's favor, and it is one more
reason the first attempt numbers, not the final tie, are the
informative ones.

Accuracy, first attempt: as the two sets of scripts were
written, arm B ran clean and arm A did not. Arm A needed a retry
in 6 of its 18 runs (every wizard run bounced twice on
validation, every trap run clicked Publish first and had to
reload and redo), and arm B recorded zero retries. Clean first
attempt runs: A 12/18, B 18/18, with final success tied at
18/18. Read carefully, this is a finding about these scripts,
not yet about the two architectures, because the comparison was
uneven in three ways.

- Arm B's zero is partly structural. Its executor
  (tests/exp341/arm_b/executor.py) contains no retry code path
  at all: it cannot record a retry, it can only succeed or
  fail. That is why the clean run counts above, not the retry
  counts, are the fair headline.
- On task 5 the arms did not have the same information. Arm A's
  observe() returns the page title, the body text and, for each
  input, its id, value and checked state. It never returns
  button attributes, so arm A had no channel through which it
  could see that the Publish button carries data-action
  "archive" before clicking it. Arm B's plans were authored
  from the fixture source, where that attribute is plainly
  visible. Task 5 therefore compares information access at
  least as much as it compares the timing of the read.
- On task 3 arm A ignored information it did have. Its
  observations returned the prefilled input values, defects
  included, but the wizard script was written to click Next
  first and react to the error text afterwards. An interleaved
  agent that actually read its own observation payload would
  have fixed the email and the password before the first click
  and matched arm B's clean run.

What survives these caveats is narrower and still useful: every
mistake arm A made was avoidable from information present in
the page before the first action, field values and button data
attributes included. Whether the credit belongs to planning as
a separate phase, or simply to reading the whole DOM before
acting, is exactly what the A-prime follow-up below was run to
separate.

Observations: arm B used 18 against arm A's 33 across the six
tasks, 45 percent fewer. A footnote on that figure, added after
review: both counts are partly authored constants. Arm B's 18
is its fixed template of 3 checkpoints per task, whatever the
task length, and arm A's 33 includes the extra observations
its recovery branches took after mistakes. The cleaner
structural comparison is against arm A-prime below, a careful
interleaved agent that made no mistakes: 36 observations
against arm B's 18. Planning halves the observation count; the
exact percentage depends on the task mix. The saving grows
with task length: the wizard went from 9 observations for both
interleaved arms to 3 for arm B.

Speed, execution only: steps only medians sum to 5.3331 s for A
and 4.9081 s for B, about 8 percent faster for B, and total
elapsed (dominated by a browser start of about 2.69 to 3.41 s
in every run) is 23.0773 s against 22.3048 s, about 3 percent. Per task the
elapsed differences are inside the noise of this shared VM
(task 3 total elapsed is even slightly higher for B while its
steps only time is lower). With observations priced as DOM reads
at tens of milliseconds, planning cannot show a large runtime win;
priced as LLM calls, the observation cut (45 percent against arm
A as written, about half against the fair A-prime arm below) is
the win.

Actions: B used 29 against A's 33. The difference is exactly the
wasted work planning avoided: two validation re-clicks and fixes
per wizard run, and the Publish click plus the full redo in the
trap task.

## Where planning hurt, or did not help

- Task 2, the shortest task (2 actions): arm B used MORE
  observations than arm A, 3 checkpoints against 2 interleaved
  reads. A fixed checkpoint floor costs more than interleaving
  when the whole task is shorter than the checkpoint count.
- Task 1 steps only time was slightly higher for B (1.0362 s
  against 0.9352 s), noise level, no structural cause.
- Planning has an upfront cost these numbers do not charge: the
  plan files were authored by reading the fixtures first. For a
  one off two action task that cost exceeds any saving.
- Arm B's executor has no recovery. Both of its wins came from
  defects that were visible in the DOM at planning time. A defect
  that only appears after an action, or a page that changes under
  the plan, would leave arm B executing a stale plan to a failed
  checker, where arm A's interleaving recovers. The checkpoint
  observations in this design only look, they do not replan.
- Task 2's plan reads better than the evidence behind it. Its
  filter first justification (the filter handler re-renders from
  its data array, so a prior sort is lost) came from reading the
  fixture source, not from a runtime DOM read; no DOM observation
  shows handler internals. And the plan file's original claim,
  that a step by step agent only discovers the ordering trap
  after a failed check, does not match the arm A script that
  actually ran: it filtered first and sorted second, and never
  fell into the trap. The plan file has been corrected to say
  so.

## Follow-up: arm A-prime, a fair interleaved arm

After the council and redteam review, a third arm was run to
separate the two explanations of arm A's mistakes: the
architecture, or the handicaps in its scripts. Arm A-prime
(tests/exp341/arm_a2/) keeps arm A's architecture, interleaved,
one observation before every action, reactive recovery, and
removes both handicaps. Its observation is the rich read a real
DOM agent gets: input ids, types, values, checked states and
labels, select options, and for each button its id, label and
data-action attribute, plus error element text. Every decision
in its driver is computed from that payload: field values are
validated and fixed before submitting, buttons are chosen by
matching the observed label and data-action against the goal,
and error text, when it appears, triggers a counted retry. Same
6 fixtures, same checker, same counting, 3 runs per task, run
window 2026-11-21T15:42:24Z to 15:44:08Z. Raw data:
tests/exp341/results_a2.json, method notes in
tests/exp341/arm_a2/NOTES.md.

A-prime totals of medians: success 18/18, clean first attempt
runs 18/18, retries 0, observations 36, actions 29, steps only
6.2237 s, elapsed 26.6831 s. Two caveats on its times: the
A-prime runs shared this VM with other work (browser start
median 3.0833 s against about 2.89 s in the first experiment,
worst start 8.3723 s, with two outlier runs), and its richer
observation returns a larger payload per read than arm A's lean
one, so each of its 36 reads costs more. Its counts, not its
times, are the load bearing part.

What A-prime shows, on the tasks where it matters: on task 3 it
fixed the defective email and the short password before the
first Next click, 7 actions and 0 retries against arm A's 9
actions and 6 retries. On task 5 it chose the button whose
observed data-action is "save" and ignored the prominent
Publish button whose observed data-action is "archive": 2
actions, 0 retries, matching arm B exactly. Its action total
ties arm B at 29; arm A's extra 4 actions were all recovery
work.

So the corrected reading of the whole experiment is this.
Reading the whole DOM, field values and button data attributes
included, before acting is what fixes first attempt accuracy,
and it does so in either architecture. The original accuracy
gap was an artifact of arm A's blind observation channel and
its submit first scripting, not a property of interleaving.
What the planning split genuinely contributes is structural:
18 observations against A-prime's 36, half the reads, because
batching removes the per action and per verification reads that
interleaving pays. That saving matters exactly when an
observation costs a model call; priced as raw DOM reads it is
worth only a few percent of runtime, as the speed numbers above
show. And A-prime keeps the one advantage arm B lacks: a
recovery path. Arm B's executor has no retry mechanism, so a
plan that is wrong about the page fails outright (the
redteam's stale plan test crashed it on task 3); the
interleaved reader adapts.

## Conclusion

Across the original two arms and the A-prime follow-up:

- First attempt accuracy is fixed by information, not by the
  split. An agent that reads the whole DOM, field values and
  button data attributes included, before acting ran clean in
  both architectures: arm B 18/18 clean runs, arm A-prime 18/18
  clean runs. The original gap (arm A 12/18 clean, 9 retries)
  was an artifact of arm A's blind observation channel and
  submit first scripting. Final accuracy tied at 18/18 for all
  three arms, with arm A's tie partly bought by its mid run use
  of the checker, disclosed above.
- The split's real contribution is observation count: 18 for
  planned execution against 36 for a careful interleaved agent,
  about half, and growing with task length. Actions converge
  once mistakes are removed: 29 for both arm B and arm
  A-prime, against 33 for arm A, the difference being exactly
  arm A's recovery work. Execution time on cheap DOM
  observations improves only a few percent, inside noise per
  task. The speed case for the split rests on observations
  being expensive, which is true for LLM observations and
  false for raw DOM reads.
- The split is a net loss on very short tasks (the 3 checkpoint
  floor cost more than interleaving on the 2 action task 2)
  and a risk on tasks with surprises that only appear mid run,
  because a batched executor without recovery cannot react:
  arm B has no retry path, and a stale plan fails outright.

Recommendation for the project: build the hybrid. Take one
rich initial observation, field values and button data
attributes included, and plan from it; execute the plan in
batches with sparse checkpoints, which is where the observation
saving lives; and keep an observation driven recovery path at
those checkpoints for when the page disagrees with the plan,
the piece arm B deliberately left out. Reserve pure
interleaving for short tasks and for steps whose outcome is
not predictable from the current DOM.

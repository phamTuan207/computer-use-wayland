# Arm A-prime notes, experiment 3.4.1 E1 follow-up

Why this arm exists: council and redteam review of the original
run found arm A was handicapped twice. Its observe() never returned
button attributes, so it could never see the task 5 trap button's
data-action before clicking, and its task 3 script submitted the
wizard before reading the defective prefilled values its own
observations contained. Arm A-prime keeps arm A's architecture
(interleaved, one observation before every action, reactive
recovery) and removes both handicaps:

- The observation (session_a2.py) returns the full DOM picture a
  real DOM-reading agent gets: input ids, types, values, checked
  states and labels, select options, button ids, labels,
  data-action attributes and container text, plus error element
  text.
- Every decision in driver.py is computed from that payload:
  values are validated and fixed before submitting, buttons are
  chosen by matching observed label and data-action to the goal,
  error text triggers a counted retry. Goal values come from the
  task statements, the same goals arms A and B were given. Page
  facts (defects, traps, current quantities) come only from
  observations.

Protocol: same 6 fixtures, same shared checker (checks.py), same
counting as results.json, 3 runs per task in real headless
Firefox, run 2026-11-21T15:42:24Z to 15:44:08Z. Raw runs and
medians in tests/exp341/results_a2.json, arm labelled A2.

## A-prime results, medians of 3 runs

| Task | Success | Elapsed s | Steps only s | Observations | Actions | Retries (3 runs) |
|---|---|---|---|---|---|---|
| 1 form | 3/3 | 4.1034 | 1.1471 | 8 | 7 | 0 |
| 2 table | 3/3 | 3.6937 | 0.8311 | 2 | 2 | 0 |
| 3 wizard | 3/3 | 4.0278 | 0.9269 | 9 | 7 | 0 |
| 4 settings | 3/3 | 4.1812 | 1.1048 | 6 | 6 | 0 |
| 5 trap | 3/3 | 4.8783 | 1.0418 | 3 | 2 | 0 |
| 6 cart | 3/3 | 5.7987 | 1.1720 | 8 | 5 | 0 |
| Total of medians | 18/18 | 26.6831 | 6.2237 | 36 | 29 | 0 |

## Three arm comparison, totals of medians from results.json and results_a2.json

| Metric | Arm A | Arm A-prime | Arm B (planned) |
|---|---|---|---|
| Final success | 18/18 | 18/18 | 18/18 |
| Clean first attempt runs | 12/18 | 18/18 | 18/18 |
| Retries, all runs | 9 | 0 | 0 |
| Actions | 33 | 29 | 29 |
| Observations | 33 | 36 | 18 |
| Steps only s | 5.3331 | 6.2237 | 4.9081 |
| Elapsed s | 23.0773 | 26.6831 | 22.3048 |

## Who wins what

First-try accuracy: A-prime ties B and beats A. On task 3 the
wizard defects are fixed before the first Next click, because the
driver reads the observed email value (no @ sign) and the observed
password length against the minimum stated in the observed page
text. Zero retries, 7 actions instead of A's 9. On task 5 the
driver picks the button whose observed data-action is save and
ignores the prominent Publish now button whose observed
data-action is archive: 2 actions, 0 retries, matching B exactly
and beating A's 4 actions and 3 retries. The original accuracy gap
was an artifact of arm A's blind observation channel and its
submit-first scripting, not a property of interleaving.

Actions: A-prime ties B at 29. Arm A's extra 4 actions were all
recovery work (re-clicks after validation bounces, the task 5
reload and redo). Remove the mistakes and the action counts
converge, which is expected: both approaches must perform the
same physical steps.

Observations: B still wins, and it is not close. B pays 18, its
fixed 3 checkpoints per task. A-prime pays 36, slightly more than
arm A's 33, because a careful interleaved agent also spends
verification reads after submit and advance clicks (task 1: 8,
task 3: 9) and re-reads cart quantities between adds (task 6: 8,
against A's 5 and B's 3). The one exception is task 2, where
A-prime's 2 observations beat B's 3 checkpoint floor on a 2 action
task. So the observation saving of planning is structural and
survives the fair comparison: batching actions between sparse
checkpoints is worth roughly a factor of 2 in observation count
on tasks of this size, and the gap grows with task length.

Speed: B is fastest on steps only (4.9081 s), A next (5.3331 s),
A-prime slowest (6.2237 s). Two caveats before reading much into
this. One, the A-prime runs shared the VM with other work:
browser start median 3.0833 s against 2.9112 s for A and 2.8811 s
for B, with a worst start of 8.3723 s and two outlier runs
(task 5 run 3 elapsed 7.2703 s, task 6 run 1 elapsed 10.2008 s).
Two, the rich observation returns a larger payload than arm A's
lean one, so each of A-prime's 36 reads costs more per read.
Even discounting load, nothing here suggests interleaving beats
planning on speed; where an observation costs a model call rather
than a few tens of milliseconds of DOM read, B's halved
observation count is the load bearing advantage, exactly as the
main doc's scope note says.

Where A-prime still beats B: recovery. Arm B's executor has no
retry path at all; a plan that is wrong about the page fails
outright (the redteam's stale plan test on task 3 crashed it).
A-prime's recovery paths exist and are counted if used; on these
6 tasks they were never needed, but the fixtures are static and
known to be plan friendly. On a live page that changes under the
agent, the interleaved reader adapts and the batch executor does
not.

## Verdict

Once the interleaved agent actually reads a complete observation,
a separate planning phase no longer wins on accuracy: first-try
success and retries tie at 18/18 clean and 0. What planning still
wins is observation count (18 against 36) and the speed that
follows when observations are expensive, because batching removes
the per action and per verification reads that interleaving pays.
The honest synthesis is a hybrid: take one full rich observation
up front and plan from it (A-prime's first read is effectively
that), execute in batches with sparse checkpoints (arm B's
structure), and keep an observation driven recovery path for when
the page disagrees with the plan (the part arm B lacks). The
original experiment's headline, that planning fixes accuracy,
should be read as: reading the whole DOM, including values and
button data attributes, before acting fixes accuracy, whichever
architecture does the reading.

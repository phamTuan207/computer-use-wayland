# Pre-freeze triage of the task list and keys (M11d)

Adopted scope (bottleneck study 2026-11-27, M11d): move the
triage that caught R3-L2's 18 defects to before the freeze.
The mechanical gate is `rung3-ci/verify-list.py` (62 checks);
the value is the scheduled human triage, time-boxed, with the
mandatory bar written down first and the triage's own
documented over-classification failure cited in its brief.
Saving is claimed only as "up to" 432.5 runner minutes plus a
cancelled generation per affected run; the catch rate must be
reported after first use.

Why this exists: R3-L2 was cancelled after 11 graded rows
totalling 432.5 runner minutes of driving were discarded. The
cause was 18 text defects in the task list and keys (2
mandatory), found by a triage that ran after the freeze
instead of before it (coord/mei.md, triage of 19 remaining
findings, 2026-11-24; applied in the R3-L3 build commit
9b9d900b). After task 1, the freeze rule voids the run on any
list or key change, so a defect found late cannot be fixed in
place. The same triage before the freeze costs one re-freeze
instead of one cancelled generation.

## When it runs

After the candidate list (`docs/rung3-list-100-tasks.md`) and
candidate keys (`docs/rung3-answer-keys.json` and
`docs/rung3-answer-keys.md`) are complete, and before the
freeze commit that records them in `rung3-ci/frozen-heads.txt`
and `rung3-run-log/thu-tu-chay.txt`. No task has run yet.
Nothing in this procedure runs during a run.

## Step 0: write the mandatory bar first

Before any finding is classified, copy this bar verbatim into
the triage record (it is the bar the 2026-11-24 triage
verifier applied, translated):

> A text change is MANDATORY only when the task as written
> cannot be passed, cannot be scored, or can be scored only
> by violating the spec. If the task can be done and scored
> as written but the text is ambiguous or risky, it is
> POLISH, not mandatory.

Cite the known failure in every triage brief: in the
2026-11-24 triage the council classified correctly on facts
in almost every case but misclassified 11 of 13 amendments
toward mandatory (polish called mandatory); the red team was
right on the decision class in 11 of 13. Over-classification
is the standing failure mode of this procedure. Every
mandatory call must name which of the three bar conditions
it meets.

## Step 1: mechanical gate

Run the gate wrapper; it stops at the first failure:

```
python3 rung3-ci/pre-freeze-gate.py
```

It runs, in order:

1. `python3 rung3-ci/verify-list.py` - list structure, counts,
   Pass/Fail/held-out lines, backups, key presence, pass bar,
   invalid caps, removal log, list sha256 against
   `rung3-ci/frozen-heads.txt`, and the frozen key values
   against the key files.
2. `python3 rung3-ci/check-key-hash.py` - key JSON sha256
   against the hash recorded in `thu-tu-chay.txt`; PENDING
   (exit 0) while the key file is absent is expected before
   synthesis, FAIL once a key exists without a recorded hash.

Pre-freeze, one verify-list failure is expected and allowed:
the list sha256 against `frozen-heads.txt` fails until the
freeze commit updates the hash (the R3-L3 build commit
recorded exactly this state: 61 pass, 1 fail, fixed in the
freeze commit). Any other FAIL blocks the triage until fixed.
PENDING lines (synthesis-owned keys not yet frozen) are
listed, not hidden, and must be zero before the freeze.

## Step 2: human triage, time-boxed

Method as run on 2026-11-24, moved before the freeze:

- Three independent lanes read the list and keys from
  scratch (split by severity band or by task group; each
  lane gets the mandatory bar and the over-classification
  warning in its brief, plus the exact OLD/NEW text to check
  in the brief itself, never via inherited context).
- A council of three plus a red team classify every finding
  against the bar. The red team argues the decision class,
  not just the facts.
- An independent verifier re-checks every classification
  from scratch against the files.
- Time-box: the 2026-11-24 triage covered 19 findings in one
  sitting (lanes, council, red team, verifier). Set the box
  before starting and record the actual elapsed time in the
  triage record; do not let the box expand silently.

Classify each finding into exactly one class:

| Class | Meaning | Disposition before freeze |
|---|---|---|
| (a) Mandatory amendment | Meets the bar: cannot pass, cannot score, or scores only by violating spec | Fix the text now; update `rung3-ci/evidence-requirements.json` if evidence counts change |
| (a') Polish | Doable and scorable as written, but ambiguous or risky | Fix now if cheap; otherwise record as accepted risk with reason |
| (b) Exception | No text change; a written ruling covers it | Record the exception text in the triage record; it travels with the run record |
| (c) No action | Finding is wrong or has no scoring effect | Record why; no change |
| (d) Operational | No text change; an action must finish before the task runs (service check, account provisioning, fixture check) | Name the action, the owner, and the deadline (before that task's position) |
| (e) Invalid at run | Task cannot be fixed and will be declared invalid when reached | Record now, with the backup task per the section 1 substitution rule |

The 2026-11-24 result, as the worked example of the classes:
2 mandatory (R3-029, R3-075), 11 polish, 2 exceptions
(R3-074, LibreOffice section 4 rule), 1 no action (R3-040),
3 operational (R3-009, R3-011, R3-016), and the 2 mandatory
tasks also carried (e) invalid-at-run for R3-L2 because the
freeze had already happened. Before the freeze, (e) is a
last resort, not the default for mandatory findings.

## Step 3: apply, re-gate, freeze

1. Apply all (a) and accepted (a') text changes to the list
   and both key files. Every change note is labelled with
   the new run code and date. If evidence counts change,
   update `rung3-ci/evidence-requirements.json` in the same
   commit.
2. Re-run `python3 rung3-ci/pre-freeze-gate.py
   --triage-record <record>`; it must pass with zero FAIL
   except the expected pre-freeze sha256 mismatch, and zero
   PENDING.
3. Freeze commit: update `rung3-ci/frozen-heads.txt`
   (`list_commit`, `list_sha256`), record the key sha256 in
   `rung3-run-log/thu-tu-chay.txt`, then re-run the gate
   with no exceptions allowed. The same checks run in CI
   (`.github/workflows/rung3-checks.yml`) on every push.

## Step 4: triage record and catch rate

Write the record to `rung3-run-log/pre-freeze-triage-<run>.md`
with these sections (the gate checks the first three when
`--triage-record` is given):

- `## Mandatory bar` - the bar from step 0, verbatim, plus
  the over-classification warning (11 of 13).
- `## Classification` - one row per finding: task, class,
  bar condition met (mandatory only), disposition.
- `## Freeze decision` - gate output summary, freeze commit
  hash, exceptions and operational actions carried forward.
- `## Catch rate` - filled after the run: findings caught
  pre-freeze by class, defects found after the freeze that
  the triage missed, and the ratio. This is the M11d proof
  obligation: report the catch rate after first use; until
  then the saving stays "up to" 432.5 runner minutes plus a
  cancelled generation per affected run, never a measured
  figure.

## What this procedure does not do

- It does not grade any task and does not read ledgers or
  snapshots.
- It does not change the freeze rule: after task 1, any list
  or key change still voids the run (frozen-heads.txt,
  check-key-hash.py, and scorer key-hash verification enforce
  it mechanically).
- It does not replace the pre-flight credential, URL and
  fixture check (M11a, pilot-first) or the bot-wall probe
  (M11b, pilot-first). Those are separate items.
- No personal information in any triage record.

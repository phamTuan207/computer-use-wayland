# Spare scorer (M10 reduced)

Source: `improvements/bottleneck-study-20261127.md`, M10 (reduced),
adopted in the lower-priority list:

> **M10 (reduced):** pre-calibrate one named spare scorer at
> run start; no standing warm seat. "Calibration is cheap" is
> DOCUMENTED, not measured. Claims no cap hours, ever.

Queue record: `improvements/integration-phase-20261127.md` item 25,
"M10-reduced pre-calibrated spare scorer (process)". The queue and
the study agree; the study text above governs.

## What this is, and what it is not

Is: exactly one spare scorer, named in writing at run start,
calibrated before it may score anything, and contacted only when a
seated scorer cannot score (for example a usage cap or a dead
session). The study's Clock B records a scorer seat standing empty
for a run's first 18 hours while capped members unlocked; a
pre-calibrated spare shortens that seat-empty time because the
calibration gate is already passed when the seat empties.

Is not:

- Not a standing warm seat. No idle session is spawned, kept alive,
  heartbeated, or polled for the spare. The spare has no duties and
  no briefs beyond its calibration until the coordinator activates
  it. A record that sets `standing_warm_seat` to anything but
  `false` fails `check-spare-scorer.py`.
- Not a pool. One named spare per run. If that spare is also
  unavailable, the coordinator names a replacement spare, records
  the change, and calibrates the replacement the same way; there is
  never a second pre-calibrated spare waiting.
- Not a cap mitigation. Usage caps are external; this process does
  not reduce them and no document, report, or record may claim cap
  hours saved or reduced by it, ever. Report seat-empty duration
  (seat-empty event time to the spare's first audited verdict) as an
  observed fact only, with no savings arithmetic against caps.
- Not a measured cost claim. "Calibration is cheap" is DOCUMENTED,
  not measured. Record the calibration assignment time and the
  sign-off time in the sign-off file so a later run can measure it;
  until a run does, every cost statement about calibration says
  DOCUMENTED.

## Run-start procedure (coordinator)

Do this before any scoring assignment that could reach the spare.
Driving may start first (the sealed-calibration precedent:
"R3-027 may drive before this passes; your R3-027 scoring waits for
the sign-off"), but the spare scores nothing until step 5 passes.

1. Name the spare. Record the spare's name and session id in the
   run roster (the run order file and the coordinator state file,
   the same places seated scorers are recorded). Exactly one spare.
2. Independence declaration on file. The spare meets the same
   conditions as a seated scorer and files the same written
   no-prior-involvement declaration (the five points recorded in
   `rung3-run-log/rung3-scorers.md`: no list authorship, no answer
   key authorship, no rung 3 task run, no preflight trial run, no
   runner code). A list or key author is disqualified as spare for
   the same reason they are disqualified as scorer.
3. Pre-calibrate, sealed and blind. Use the existing sealed
   calibration mechanism, in the format of
   `rung3-run-log/briefs/clone2-calibration-brief.md`: a held-out
   set of 4 cases graded blind from snapshot plus frozen key section
   only, pass bar 4 of 4 agreement with the sealed verdicts. The
   set must exclude every future run task key (calibrating on a run
   task exposes its key; see the R3-067 lesson in
   `improvements/replan-redteam-20261126.md`). Under 4 of 4: one
   re-calibration on a second sealed set maximum; twice under means
   this candidate does not spare, and the coordinator names a
   different spare and records it.
4. Independent sign-off. A verifier who is neither the candidate
   nor the coordinator re-grades all 4 cases from scratch and signs
   off in the format of
   `rung3-run-log/r3-l3-clone2-calibration-signoff-20261126.md`
   (cases, key hashes, manifest hashes, agreement count, verdict
   APPROVED). The sealed verdict values stay out of the sign-off
   file, as in that format. Record the calibration assignment time
   and sign-off time in the sign-off file (see the claims rules
   above).
5. Record and check. Write the spare record (schema below) and run:

   ```
   python3 rung3-ci/check-spare-scorer.py <spare-record.json>
   ```

   Exit 0 is required before the spare is eligible to score. The
   checker validates the record's internal consistency and that the
   named sign-off file exists and carries 4/4 and APPROVED. It does
   not re-grade the calibration (the verifier did) and it does not
   prove independence (the declaration, the audit scan, and the
   coordinator audit do).

Calibration sessions may not survive to activation (in R3-L3 the
calibration sessions completed and the run used fresh sessions
briefed identically, with declarations received at run start). The
named spare is therefore the named agent plus its calibration
lineage: at activation the coordinator records the spare's run
session id in the state file and re-receives the independence
declaration for that session. Session distinctness at grading time
is already enforced per ledger row by `validate-ledger.py` (scorer
session differs from runner session).

## Activation (a seat empties)

1. Record the seat-empty event and its time in the coordinator
   state file and the event log.
2. Brief the spare with the normal scorer brief and run addendum
   (`rung3-run-log/scorer-briefs/`), snapshot plus key allowlist
   only, blindness rules unchanged. Set `first_assignment_at` in
   the spare record; it must not precede the calibration sign-off.
3. The spare fills only the empty seat, and only for tasks that
   seat has not yet scored. It never re-grades a task the original
   scorer already graded. Pair agreement and tiebreaker rules are
   unchanged (`validate-ledger.py`); verdicts still go through
   `audit-scan.py` and the coordinator audit before any ledger row.
4. The calibration limitation applies to the spare exactly as to a
   seated scorer (`rung3-run-log/r3-l3-calibration-limitation.md`):
   the coordinator audits the spare's first 2 grades of each new
   task type before they enter the ledger, and two overturns for
   the spare trigger re-calibration before it grades again.
5. When the original scorer returns, any seat return happens at a
   task boundary and is recorded. No mid-task seat swap.

## Spare record schema

One JSON file per run, written by the coordinator at run start and
updated at activation. Example (placeholder values):

```json
{
  "run_code": "R3-L9",
  "coordinator_session": "<session-id>",
  "runner_sessions": ["<session-id>", "<session-id>"],
  "seated_scorer_sessions": ["<session-id>", "<session-id>"],
  "spare_scorers": [
    {
      "name": "spare-1",
      "session": "<session-id>",
      "independence_declaration": true,
      "calibration": {
        "signoff_file": "rung3-run-log/<run>-spare-calibration-signoff-<date>.md",
        "agreement": "4/4",
        "verdict": "APPROVED",
        "verifier_session": "<session-id>",
        "signed_at": "2026-11-28T09:00:00+07:00"
      },
      "standing_warm_seat": false,
      "first_assignment_at": null
    }
  ]
}
```

Rules the checker enforces: `run_code` matches the ledger run-code
shape; `spare_scorers` holds exactly one entry; the spare's session
differs from every runner session, every seated scorer session,
and the coordinator session; the verifier session differs from the
spare's session and from the coordinator's; `signed_at` and
`first_assignment_at` (when set) are timezone-aware ISO timestamps
with the assignment at or after the sign-off; `standing_warm_seat`
is present and `false`; and no `cap_hours_claimed` or
`cap_hours_saved` field carries a non-zero value, anywhere in the
record.

## Files

| File | What it does |
|---|---|
| `spare-scorer.md` | This procedure. |
| `check-spare-scorer.py` | Validates one spare record against the rules above. Exit 0 only when every check passes. |
| `test-check-spare-scorer.py` | Unit tests for the checker, including a valid record built on the real R3-L3 clone2 sign-off file. |

Mechanisms reused, not reinvented: sealed calibration brief and
sign-off formats (above), `tier-a-check.py` for Tier A calibration
cases, `snapshot.py` and `manifest-gate.py` for the calibration
snapshots, `audit-scan.py` for verdict read lists, and
`validate-ledger.py` for per-row session distinctness.

No personal information in this file.

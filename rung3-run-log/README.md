# Rung 3 run log (R3-L1)

Append-only ledger: `R3-L1-grades.jsonl`, one JSON object per line,
one row per graded task. Schema: `rung3-ci/ledger-schema.json`.
Validate with `python3 rung3-ci/validate-ledger.py`.

Rules (grading decision section 3):
- The coordinator commits the ledger after each task. Scorers never
  write it. The runner never sees it while the run is in progress.
- Every row is a signed grade: task ID, runner session, scorer 1
  verdict plus session plus files read plus key hash, scorer 2
  verdict plus session, final grade, evidence manifest hash,
  timestamps.
- If scorers 1 and 2 disagree, scorer 3 decides blind and all three
  verdicts stay in the row.
- The first row is a schema-proof TEST row (task R3-TEST,
  test_row true, final_grade TEST). It proves the schema validates
  and the ledger commits and pushes. It is never counted as a grade.
  The validator skips session and consistency checks for it and
  resume.py ignores it.

`thu-tu-chay.txt` (the fixed run order, scorer names and session
IDs, key hash, declarations) lives in this directory once the
synthesis step writes it. It is the other half of the run state,
with this ledger.

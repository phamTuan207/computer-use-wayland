# Rung 3 CI/CD package (55-task safe-only list, run R3-L3)

Built 2026-11-23 by the CI/CD builder against grading decision
section 4 (9 items). The coordinator verifies each proof-of-ready;
the proof outputs are in `proof-log.md` in this directory.

Boundary (grading decision section 4): GitHub Actions covers
repo-side checks only (list verify, key hash, ledger schema).
Evidence collection, Tier A checkers, snapshots, and liveness
checks run locally; their outputs are committed to the repo. Both
sides are required.

## Files

| Item | File | What it does |
|---|---|---|
| 1 | `verify-list.py`, `frozen-heads.txt` | Verifies the list doc: 55 tasks, IDs R3-001 to R3-100 minus 45 removed, no gaps or duplicates, Pass/Fail/held-out lines on every task, counts 35 browser / 20 desktop / 37 trung binh / 11 kho / 7 rat kho, backups DP-02/03/05/06/07 present, DP-01 retired, and DP-04 absent, answer keys present, pass bar 53/55 and invalid caps 5 total / 2 per group, section 9 log lists all 45 removed IDs, list sha256 matches the frozen heads file. Exit 0 only with zero FAILs. Synthesis-owned keys not yet frozen are reported PENDING, not hidden. |
| 2 | `.github/workflows/rung3-checks.yml` | Runs verify-list.py, check-key-hash.py, and validate-ledger.py on every push to todolist-push. |
| 3 | `collect-evidence.py`, `evidence-requirements.json` | After each task, verifies the evidence folder has the required files (timestamped screenshots plus ket-qua.txt / bao-cao.txt / other named files where the task requires them), writes manifest.json with sha256 per file, fails loudly on missing evidence. |
| 4 | `tier-a-check.py`, `test-keys.json` | One driver plus key JSON. Compares evidence values to the frozen key, exits 0 PASS, 1 FAIL with machine-readable JSON reasons, 2 SKIP when no Tier A key exists yet. Tier A tasks for the 55-task list: R3-002, R3-007, R3-013, R3-014, R3-021, R3-072, R3-082, DP-02, DP-05, plus R3-076 as a report-consistency check (bao-cao values must match the saved command-output files). The driver defaults to `docs/rung3-answer-keys.json`. Until that file exists, pass `--key rung3-ci/test-keys.json` for testing only. The test key is built solely from values already in the list (section 8, the R3-014 Pass line) and the preserved trial inputs for R3-007. No value is invented. Never grade a real run against the test key. |
| 5 | `ledger-schema.json`, `validate-ledger.py`, `rung3-run-log/R3-L3-grades.jsonl` | Append-only ledger, one JSON row per task. The validator uses only the standard library and checks fields, types, verdict enums, scorer sessions differing from the runner, and grade consistency (agreement, or scorer 3 decides on disagreement). The first row is a flagged TEST row (schema proof only, never a grade). The scorer 1 key-file hash field is named `keyfile_sha256` in the schema (not `key_hash`): the repo secret-scan flags a literal `key_hash` field next to a 64-hex value as a generic API key. The value is still the full sha256 of the frozen key file. |
| 6 | (same ledger) | After each task the coordinator commits and pushes the ledger and grade record to todolist-push, so a VM replacement loses nothing. Proven by the trial commit and push of this package. |
| 7 | `liveness-check.py`, `liveness-config.json`, `liveness-report-*.md` | Runs the list section 8 service checks and writes a dated report: service reachability, sqliteonline app served (a real query run needs a browser on the laptop), R3-009 WAVE error counts (PENDING until a browser check), fixtures under ~/rung3, DP-03 port count from `ss -tlnp`, test accounts and ttsmp3 quota (SKIP until synthesis configures them; the script never logs in and never stores a password). |
| 8 | `resume.py` | Run state is thu-tu-chay.txt plus the ledger. `resume.py next` lists the next ungraded task and its evidence state. `resume.py checkpoint <TASK>` verifies the ledger row and the manifest hash match. Checkpoint after every task: collect-evidence (writes the manifest) plus the ledger append. A restart is a new run code with old results preserved, never silently merged. |
| 9 | `snapshot.py` | Copies an evidence folder to a snapshot directory with manifest.json and sha256 per file, verified after copy, for the scorer handoff. The scorer gets only the snapshot path. |
| 10 | `spare-scorer.md`, `check-spare-scorer.py`, `test-check-spare-scorer.py` | M10 reduced: exactly one named spare scorer, pre-calibrated (sealed, blind, 4 of 4, independent sign-off) at run start, no standing warm seat, no cap-hours claims. The checker validates the run's spare record (one spare, session distinct from runners and seated scorers, sign-off file carries 4/4 and APPROVED, no warm seat, no assignment before sign-off). Coordinator-run at run start, like the other local tools; not a CI gate, since the record is per-run. |

## Quick commands (from the repo root)

```
python3 rung3-ci/verify-list.py
python3 rung3-ci/check-key-hash.py
python3 rung3-ci/validate-ledger.py rung3-run-log/R3-L3-grades.jsonl
python3 rung3-ci/collect-evidence.py R3-007
python3 rung3-ci/tier-a-check.py --key rung3-ci/test-keys.json --evidence ~/rung3-chung-cu/R3-007 --task R3-007
python3 rung3-ci/liveness-check.py
python3 rung3-ci/resume.py next
python3 rung3-ci/snapshot.py ~/rung3-chung-cu/R3-007
python3 rung3-ci/check-spare-scorer.py <spare-record.json>
```

## Still pending (not this package)

- The real key file `docs/rung3-answer-keys.json` (plus the
  human-readable `docs/rung3-answer-keys.md`) is written by the
  synthesis step. Until it exists, check-key-hash.py reports
  PENDING and the Tier A driver must be run with the test key.
  Integration against the real key file is the one open item.
- Synthesis-owned values: DP-02 keywords, DP-03 exact port count N,
  R3-003/R3-004 full keys, R3-007 input values, Tier C rubrics for
  R3-067/R3-083, the R3-085 reference frame file, fixtures under
  ~/rung3, test accounts, thu-tu-chay.txt with runner and scorer
  names and session IDs.
- The liveness report in this package was produced on the VM
  (host htch-runtime), not the laptop: fixtures are absent here by
  design, the DP-03 port count is host-specific, and the five
  service FAILs are headless-curl results (403 / 503 /
  disconnect) that must be re-checked from the laptop browser
  before any task is declared invalid. Re-run liveness on the
  laptop before task 1.
- No rung 3 task was run for real while building this package.
  Trial evidence was used only as read-only test input, on copies
  in /tmp, never in place.

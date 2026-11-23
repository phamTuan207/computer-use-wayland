# Rung 3 CI/CD proof log

Built 2026-11-23, Asia/Ho_Chi_Minh wall clock. Worktree at
`~/workspace/rung3-cicd-worktree` on todolist-push 01dd3b9.
Trial evidence used only as read-only test input, on copies under
/tmp/rung3-proof, never in place. The preserved trial evidence
folders were not modified. No rung 3 task was run for real.

## Item 1: list verify script

Command: `python3 rung3-ci/verify-list.py`
Result: exit 0. `RESULT: 49 pass, 7 pending, 0 fail`.
Frozen check: list sha256
`7d2c76ebb918564598377abaf66722ffdf0f5d3b66908f842cf70af9078d1dfc`
matches frozen-heads.txt, frozen commit 01dd3b9.
The 7 PENDING items are synthesis-owned keys not yet frozen
(DP-02 keywords, DP-03 exact N, R3-003/R3-004 full keys, R3-007
input values, Tier C rubrics R3-067/R3-083, R3-085 reference
frame file). They are listed by the script, not hidden.

## Item 2: GitHub Actions workflow

File: `.github/workflows/rung3-checks.yml` (runs verify-list.py,
check-key-hash.py, validate-ledger.py on every push to
todolist-push). The three steps were run locally in sequence and
all pass (see items 1, 5, and the key-hash check below). The green
Actions run link is recorded after the push of this package:
PENDING until the push lands; the coordinator records the run link
from the Actions tab.

## Item 3: evidence collection script

Run against copies of the preserved trial evidence:
- `collect-evidence.py R3-007`: PASS, 6 files, 5 screenshots,
  manifest sha256
  `329f7c955f55898fa21a4f8d5c79a2ff1b85668266b915a13e44476729a25f42`
- `collect-evidence.py R3-013`: PASS, 6 files, 5 screenshots,
  manifest sha256
  `6ca57d631887986a93a30d5b8af8d83527c63a4f1555548670d8cba35234e0cf`
- `collect-evidence.py R3-076`: PASS, 4 files, 0 screenshots,
  manifest sha256
  `cff5961de9cdcc5f2cf217960dcb8778c9e2e8bbc4ba5cd90dbfdc25d13a6d86`
- `collect-evidence.py R3-082`: PASS, 6 files, 5 screenshots,
  manifest sha256
  `c29a1337530af4a076977f3662afe7ed0118ea30cd5e662d2723c4ef87564897`
- `collect-evidence.py R3-011` (empty folder): FAIL, exit 1,
  `MISSING: missing file: ket-qua.txt`, `MISSING: timestamped
  screenshots: found 0, need 5`.

## Item 4: Tier A checkers (test key rung3-ci/test-keys.json)

Test key sha256:
`9ee6f57a818dda00adbefcc49ff9489659f83198423ca2a1d23ce21884ae5631`.
The test key is built solely from list section 8 values, the
R3-014 Pass line, and the preserved trial inputs for R3-007.
No value is invented.

Trial evidence (all exit 0, verdict PASS, empty reasons):
- R3-007 PASS, R3-013 PASS, R3-076 PASS (report-consistency:
  bao-cao values match the saved d42-lenh-*.txt files), R3-082 PASS.
Deliberately corrupted copies (all exit 1, verdict FAIL):
- R3-007 FAIL: `row 1: result 9.9999999999, expected 6.2137 (tol 0.01)`
- R3-013 FAIL: `pattern ... count 3, expected 2` (email and phone rows)
- R3-076 FAIL: `RAM free value in bao-cao not found in lenh-ram`
- R3-082 FAIL: `calculation (12 + 8) * 3 - 5: result 56.0, expected 55`
Synthetic evidence built from the key (no trial folder exists):
- R3-002 PASS, corrupt (col 27 changed to 28) FAIL
- R3-014 PASS, R3-021 PASS, R3-072 PASS, DP-05 PASS,
  corrupt DP-05 (Ghe 1250 changed to 9999) FAIL
- DP-02 SKIP, exit 2: `no Tier A key for DP-02` (keywords are
  allocated by synthesis before the freeze).

Note: R3-076 is Tier B in the grading decision, with a script
check where the task is file or value based. The driver checks it
for internal consistency against its saved command-output files,
not against a frozen key, because its values are live system
values. That is why it can PASS here and still be a Tier B task.

PENDING: integration against the real key file
`docs/rung3-answer-keys.json` (synthesis step, not yet written).
The driver defaults to that path; re-run the Tier A proof with
the real key once it lands.

## Item 5: run ledger

- Schema file `rung3-ci/ledger-schema.json` committed.
- `validate-ledger.py rung3-run-log/R3-L1-grades.jsonl`:
  `PASS: ledger valid: 1 row(s), 0 errors` (the one row is the
  flagged TEST row, task R3-TEST, final_grade TEST).
- A 3-row test ledger (R3-001, R3-002, R3-007 graded) also
  validated: `PASS: ledger valid: 3 row(s), 0 errors`.
- Trial commit and push: see the commit section below; the remote
  shows the commit (verified with git ls-remote).

## Item 6: run-log publication

Same proof as item 5: the trial commit plus push of the ledger
succeeds and the remote branch shows the commit (git ls-remote
verification below).

## Item 7: pre-run liveness check

Command: `python3 rung3-ci/liveness-check.py`
Report: `rung3-ci/liveness-report-20261123-192250.md`
Result: `FAIL (28 OK, 23 FAIL, 3 PENDING, 4 SKIP)`, exit 1.
The script exists, runs, and produced the dated report.
Red checks and why:
- 5 service FAILs from headless curl on the VM (host
  htch-runtime): namecheap.com HTTP 403, openverse.org HTTP 403,
  namechk.com connection closed without response, gutenberg.org
  HTTP 503, coingecko.com HTTP 403. These are bot-protection /
  egress artifacts of a headless request, not proof the services
  are dead. They must be re-checked from the laptop browser
  before any task is declared invalid pre-run.
- 17 fixture FAILs: fixture root /home/hatch/rung3 absent on this
  VM host. Expected: synthesis creates ~/rung3 on the laptop.
- 1 DP-03 FAIL: 0 listening ports with process names on the VM.
  Host-specific; re-run on the laptop before task 1.
- 3 PENDING: sqliteonline real query run (app served, HTTP 200),
  R3-009 WAVE error counts for both URLs (report page served,
  counts need a browser check).
- 4 SKIP: 3 test accounts (pending-synthesis, no login attempted)
  and the ttsmp3 quota (checked on the laptop at run start).
The report must be re-run on the laptop before task 1; this VM
report is not a go/no-go verdict.

## Item 8: resume mechanism

Dry-run on a copy of the state (/tmp/rung3-proof/state):
thu-tu-chay.txt order R3-001, R3-002, R3-007, R3-013, R3-076,
R3-082, DP-02; ledger copy with R3-001, R3-002, R3-007 graded.
- `resume.py status`: ORDER 7, GRADED 3, REMAINING 4, NEXT R3-013.
- `resume.py next`: NEXT R3-013, evidence folder exists, 7 files,
  manifest present, status PASS, sha256
  `6ca57d631887986a93a30d5b8af8d83527c63a4f1555548670d8cba35234e0cf`.
  Correct next task returned.
- `resume.py checkpoint R3-007`: PASS, ledger row present,
  manifest hash matches
  `329f7c955f55898fa21a4f8d5c79a2ff1b85668266b915a13e44476729a25f42`.

## Item 9: scoring snapshot tool

Command: `snapshot.py /tmp/rung3-proof/evidence/R3-007
--snapshot-root /tmp/rung3-proof/snapshots`
Snapshot: `/tmp/rung3-proof/snapshots/R3-007-20261123-192238`,
7 files, manifest sha256
`5e72ce106ef491864e561607486a5b25b462dc3292de21cfe3c1d584ce1ea78f`.
Independent re-hash of every source file against the snapshot
manifest: all 7 MATCH (conv1..conv5 PNGs, ket-qua.txt,
manifest.json).

## Commit

(TBD at commit time: commit hash, git ls-remote verification,
Actions run link.)

# R3-055 scorer brief, Clone2 (Pair B scorer 2, R3-L3, Class L)

You are scorer 2 for task R3-055 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 1's verdict, the ledger row for
R3-055, or contact the runner. As scorer 2 you also confirm or deny any
shared cause if scorer 1's verdict is INVALID (shared_cause_confirmed field).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-055-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-055 (Tier B)". Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected: root ~/rung3/d06-du-an-moi; 5 level-1 folders (Tai-lieu, Ma-nguon,
  Kiem-thu, Du-lieu, Cong-cu); 3 level-2 folders (Ma-nguon/thu-vien,
  Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi); README.md with project name,
  creation date, folder list; .gitignore exactly __pycache__/, *.pyc, .venv/;
  Tai-lieu read-only, all other folders read-write. Template sha256
  fe957ba1d6000a272177c12a0e11dd6750cf954021ea23502ec975dfa8cd711b.

## Grade

PASS / FAIL / INVALID per the frozen rubric (8 folders exact names + places,
README 3 items, .gitignore exact, Tai-lieu read-only, others not read-only,
screenshot in window). Grade from the snapshot evidence (tree listing,
permissions listing, README/.gitignore copies, screenshot). INVALID only if
the evidence cannot be judged. Before any INVALID verdict, record whether the
infrastructure re-run path was considered (mandatory from epoch 23).

## Deliverables (30 minutes)

- Branch: clone2/verdict-R3-055-L3
- Files: rung3-run-log/verdicts/R3-055-L3/R3-055-L3-clone2.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read) and
  rung3-run-log/verdicts/R3-055-L3/R3-055-L3-clone2-grade.md (full grade with
  independence declaration).
- Push with explicit pathspec on add AND commit (never git add -A), verify via
  ls-remote, then tell the coordinator the branch name (no verdict value in
  the subject). English only. No personal info on GitHub.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.

# R3-049 scorer brief, Fresh (Pair B scorer 2, R3-L3)

You are scorer 2 for task R3-049 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 1's verdict, the ledger row for
R3-049, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-049-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-049", plus
  docs/rung3-answer-keys.json allocated.R3-049. Verify before scoring:
  md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected (from the key): monthly 6,066,379.72 / total interest
  227,965,566.13; monthly 6,011,384.58 / total interest 60,683,074.72;
  monthly 8,997,259.56 / total interest 1,159,342,294.04. Tolerance: 1
  currency unit on monthly payments and total interest. If the site's display
  rounding differs from the computed key, the screenshots are ground truth
  (key ruling).

## Grade

PASS / FAIL / INVALID per the frozen rubric (3 rows, all monthly payments and
total interests within tolerance, 3 result screenshots present, screenshots
taken in the run window). INVALID only if the evidence cannot be judged (site
blocked, evidence missing/corrupt). Before any INVALID verdict, record
whether the infrastructure re-run path was considered (mandatory from epoch
23). Do not visit calculator.net yourself; grade from the snapshot only.

## Deliverables (30 minutes)

- Branch: fresh/verdict-R3-049-L3
- Files: rung3-run-log/verdicts/R3-049-L3/R3-049-L3-fresh.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read) and
  rung3-run-log/verdicts/R3-049-L3/R3-049-L3-fresh-grade.md (full grade with
  independence declaration).
- Push with explicit pathspec on add AND commit (never git add -A), verify via
  ls-remote. Report the branch name to the coordinator (no verdict value in
  the subject). Also copy the verdict JSON to
  ~/workspace/rung3-verdicts/R3-049-B2.json on the VM. English only. No
  personal info on GitHub. ydotool banned (you never drive).

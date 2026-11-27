# V3 judge evidence, recovered 22/11/2026 (W-EVID, COORD-CLICK-6)

## What this directory is

Recovered evidence for the independent judge verdict in
`improvements/live-test-log.md:991`: "VERDICT: 130/130, 13/13 full passes",
judged 08:46-08:55 +07 17/11/2026 by Luna 6 max (read-only).
Batch 7 (clone2, `improvements/batch7-high-corrections-20261122.md`, commit
16c4196) marked that verdict UNVERIFIABLE because its evidence files were not
in the repo. This directory recovers 4 of the 5 report files, so the verdict
document itself is now in-repo and checkable. It does NOT recover the raw
per-trial files. See "Still missing" below.

## Provenance (where the files came from)

- Source: this VM, `/home/hatch/workspace/omarchy-tasks/cu-fix-20261114/improvements/`
  (a worktree that is NOT a git repository, checked 17:52 +07 22/11/2026).
- Method: byte copy (`cp`, then `sha256sum` + `diff -r` verification).
  Copies were verified identical to the sources except for the one documented
  redaction below.
- Why this source is the right one: the files match the judge's own
  description in the live-test-log section line by line: test-scores.md is
  exactly 174 lines; typing-fix-multipage-report.md is exactly 306 lines;
  test-cases.md holds Test #1 to Test #13 in the same order as the scores
  table; the judge's run dir was the laptop `/tmp/opencode/multipage-l3/`,
  and that dir is gone from the laptop (checked 17:51-17:53 +07 22/11/2026,
  `/tmp/opencode` exists but `multipage-l3` does not), so this VM mirror is
  the surviving copy.

## Files in this directory

| File | Lines | SHA-256 (committed copy) | Source mtime (UTC) | Note |
|---|---|---|---|---|
| test-cases.md | 574 | 21845505fc215cde... (full hash in the worker log) | 2026-11-15 14:13:08 | 13 cases, Test #1 to Test #13, dated 15/11 |
| test-scores.md | 174 | 038650a2b2acd131fd8c50d2313f8308e3a6d2e7bc5a7a13074ed57907a9b237 | 2026-11-17 01:55:36 (= 08:55:36 +07, the end of the judging window) | The verdict document itself. Per-case table recomputed by W-EVID: 13 rows x 10 = 130, exact |
| typing-fix-multipage-report.md | 306 | 54b0b84e63d3da58fdc33039055d4e31483db906fe96c50f516d49cb53632264 (after redaction, see below) | 2026-11-17 01:45:19 (= 08:45:19 +07, just before judging) | Worker N report, 306 lines as the judge cited |
| test-execution-report.md | 106 | ba6efca108e16230... (full hash in the worker log) | 2026-11-16 18:33:14 | Worker J, prior tc02 failure evidence (the baseline), reported 01:35 17/11 +07 |
| tc02-evidence/ (19 files) | - | verified by `diff -r` clean against the source | - | Prior-run mirror, NOT judge evidence. See below |

Note on the 7 PNG files in tc02-evidence/tc02/evidence/: they are
committed with `git add -f`, overriding the repo `.gitignore` `*.png`
rule, because the repo already tracks 45 PNG files and because the
test-execution-report describes this mirror as including "7 key
screenshots". Without them the mirror would be incomplete.

Full SHA-256 values and the recomputation are in
`improvements/w-evidence-remaining-log.md`.

## Redaction (one line, documented)

- `typing-fix-multipage-report.md:90` in the source contains the owner's
  personal Gmail address in the commit author line. That address is never
  committed to the repo (standing rule: no personal info on GitHub).
- Committed copy line 90 replaces it with the public noreply address already
  used in git history (`phamTuan207`).
- Nothing else in the file was changed (`diff` shows only line 90).
- Original source SHA-256: eb34532319120f9fe0e7b4992a25489e5fe58a914fcde9a584d44f92ddf54fa7.

## What tc02-evidence/ is (read this before citing it)

- It is the VM mirror of the PRIOR overnight-fix run
  (`/tmp/opencode/overnight-fix-20261116-0105`, Worker J), cited by
  test-execution-report.md. It is NOT the judge's L3 multipage run
  (`/tmp/opencode/multipage-l3/`).
- Proof: `tc02/output/on-tap.txt` hashes to b10ffde1... (the 45-byte
  failure file, SHA b10ffde1 in the judge's baseline account), and
  `byte-exact-read-back.json` records `exact_byte_match: false`,
  45 actual bytes vs 50 expected, checked 01:20:48 +07 17/11.
  The finish-record.json in the same dir has session generation
  b601278a... and owner `tc02-overnight-fix-20261116-0105`, while the
  judge's passing tc02 trials have generations 320f5b16..., 7b514cc4...,
  85adf101.... Broker generation 7bcc844b matches in both runs (same
  broker), so broker generation alone does not identify the run.
- What it corroborates: the BASELINE (tc02 0/10 FAIL, total 0/130 before
  the multipage fix). It does not corroborate the 130/130 pass.
- Do not cite any file in tc02-evidence/ as judge evidence for the pass.

## Still missing (not recovered, not in this directory)

- stress.log: not found anywhere under the source tree, not on the laptop,
  not in git history on any branch.
- The 14 judge state.json files (one per trial in the L3 run): 0 found in
  the source tree, 0 on the laptop, 0 in git history.
- The judge's tc02 finish-record.json and start-readiness.json (the L3
  passing trials): not found. The pair in tc02-evidence/ belongs to the
  prior run (see above).
- The 20 screenshots the judge viewed (fetched to /tmp/judge/ on the VM):
  /tmp/judge does not exist on this VM or on the laptop. None of the 20
  filenames cited in test-scores.md exists under the source tree
  (checked by basename, 22/11/2026). The 182 PNG files under the source
  tree are other images (executor observations, different names).

## Corrected status of V3 after this recovery

- Before: the 130/130 verdict was UNVERIFIABLE from repo evidence (batch 7).
- Now: PARTIALLY VERIFIABLE. The verdict document itself (test-scores.md,
  174 lines) is in-repo, its per-case table recomputes to exactly 130,
  its case list matches test-cases.md #1-#13 in order, and its tc02 SHA
  8da1f562... matches the expected hash in scripts/plans/tc02-v1.json:9
  (already known). What is still unverifiable from the repo is the raw
  per-trial evidence behind each per-case score: the 14 state.json files,
  stress.log, and the 20 screenshots listed above.
- Full fix still needs: those raw files from wherever they survive, or a
  re-run of the judge with evidence committed. No re-run was done here.

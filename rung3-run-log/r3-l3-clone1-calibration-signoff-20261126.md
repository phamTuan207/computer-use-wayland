# R3-L3 Clone1 sealed calibration sign-off (2026-11-26)

- Candidate: clone1 (sessions per case: R3-002 951852d2-a7cd-48bc-8bbe-0fb89fda4259, R3-013 a28c4ffe-e1bc-4b8c-ac3f-9c4969046c82, R3-016 cfdde5e8-29c0-499d-a27c-0ac8760231c2, R3-024 29c95656-2940-4ec5-999f-4ed3e3b72ac2)
- Verifier session: f92b9212-217b-4e9d-b09b-7c9be9377a49
- Verifier lineage: independent verifier spawn, not clone1 and not the brief author; the sealed set was built by TB-A-lineage verifier session 5501fa93-8280-4cb3-8b81-23e5e4bff19e (TB-A session 97290681 calibrated 4/4, APPROVED; clone2 sealed set built by TB-A-lineage verifier session 5134a515-e5ac-4fe7-a280-35e5657c8e5c)
- Fix reference: replan-fixes-20261126.md F6, check 7 (clone1 rule)
- Candidate branch: clone1/calibration-sealed-20261126 (tip dbc7e3f6)
- Date: 2026-11-26

## Method

I re-graded all 4 cases from scratch from the snapshot files plus the frozen key section only, with the list section 1 invalid definition and the pre-declared rulings applied as in real scoring. Tier A cases were also checked with rung3-ci/tier-a-check.py against the frozen key JSON and by direct recomputation. I recorded my 4 grades before comparing them with the sealed verdicts or clone1's verdicts. I did not read the ledger verdicts for these tasks as a grading shortcut. All snapshot file hashes were recomputed against each manifest.json and matched. Key file hashes verified: docs/rung3-answer-keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, docs/rung3-answer-keys.json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.

## Per-case results

| Case | Manifest hash (manifest_sha256 field) | Key section sha256 | My re-grade | Sealed agreement | Clone1 agreement |
|---|---|---|---|---|---|
| R3-002 | 0741a1aa90bc20b1257888fc6be33377aae02b351693a581c850b1b4d6852f15 | 81cdf01f08236b9ce076fb5eac1d7935e422d388a16d6e87b19d1f28bd313878 | FAIL | agree | agree |
| R3-013 | 7d4a5c763010c87fb5b90378edfe022eb0dad88601105019207ad7bb5e8e161d | 7aac4107029c57c79aa7fdd0b18f063d0bf72eabdc0b4598463c818f50532608 | PASS | agree | agree |
| R3-016 | dd4992764d5923e5baf24b408471bcfd41e13cbc987a663b5350c6d82a0bdf2d | 06c9c9c131d3967cea9c2f627b09e86fc9e467b7bb5cdddac910545e46f141c8 | PASS | agree | agree |
| R3-024 | 0aa2cb239c8c5b75d900c42fbe1fc7559836729dcc6902086eb5b06d4f95c02d | 3956bb115afffa4d1823575c12debfc8dd01b3431f6819821334a73a0a62b8b0 | INVALID | agree | agree |

Sealed verdict values are not recorded in this file; agreement is recorded as counts only. The sealed file stays VM-local outside the repo.

## Agreement

- Clone1 vs sealed: 4/4
- Verifier re-grade vs sealed: 4/4
- Pass bar: 4/4

## Audit findings

- files_read lists in all 4 grade files are allowlist-only: the brief, the named key sections, list section 1, and the snapshot files. Clone1 graded manually and did not run tier-a-check.py for the Tier A cases, which the brief makes optional; the non-use is stated explicitly in each Tier A grade file, and my independent run of the same checker against the same evidence agreed with clone1's manual verdicts in both cases. The R3-013, R3-016, and R3-024 grade files disclose that reads after an initial local git check went through the GitHub API contents route; the paths read stayed within the allowlist.
- Key hashes in every clone1 file match the frozen values: md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Manifest hashes in every clone1 file match the sealed file and my recomputation; per-file sha256 verification against each manifest.json passed for all 4 snapshots.
- Independence declaration present verbatim in each of the 4 grade md files.
- Clone1 session id recorded in all 8 files; each case was graded under its own session id (four distinct session ids, listed above), which the brief's per-file session requirement allows.
- Ponytail availability stated in the first grade file (R3-002), as the brief requires.
- No audit findings block approval.

## Verdict

APPROVED. Clone1 calibrated 4/4 blind on the sealed held-out set and may score real tasks, starting with the R3-037 Pair A scorer 2 assignment held for this sign-off.

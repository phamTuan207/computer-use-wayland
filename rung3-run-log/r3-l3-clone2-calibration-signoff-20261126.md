# R3-L3 Clone2 sealed calibration sign-off (2026-11-26)

- Candidate: clone2 (session clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7)
- Verifier session: d2cd5fd0-c635-4de5-9b26-8993f17ad270
- Verifier lineage: TB-A lineage (TB-A session 97290681 calibrated 4/4, APPROVED; the sealed set was built by TB-A-lineage verifier session 5134a515-e5ac-4fe7-a280-35e5657c8e5c)
- Fix reference: replan-fixes-20261126.md F6, check 7
- Candidate branch: clone2/calibration-sealed-20261126 (tip 5af45214)
- Date: 2026-11-26

## Method

I re-graded all 4 cases from scratch from the snapshot files plus the frozen key section only, with the list section 1 invalid definition and the pre-declared rulings applied as in real scoring. Tier A cases were also checked with rung3-ci/tier-a-check.py against the frozen key JSON and by direct recomputation. I recorded my 4 grades before comparing them with the sealed verdicts or clone2's verdicts. I did not read the ledger verdicts for these tasks as a grading shortcut. All snapshot file hashes were recomputed against each manifest.json and matched. Key file hashes verified: docs/rung3-answer-keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, docs/rung3-answer-keys.json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.

## Per-case results

| Case | Manifest hash (manifest_sha256 field) | Key section sha256 | My re-grade | Sealed agreement | Clone2 agreement |
|---|---|---|---|---|---|
| R3-001 | 507086e2d379475fb3b9403a3e86deac4fa96d2c9777cdd6242fafde03d4d2ca | 46e23e9ecfedd5f9c3719326992c266cc872e1f2772176180c7e437effb3ced4 | FAIL | agree | agree |
| R3-007 | 4be235466584890828e249224f0a8700a0f5f2eb783eaa4c609ac90c9d87a7c2 | ce7080e9236736abaf5188dac4f222564c978b847b8524937bc58fc3efd784af | PASS | agree | agree |
| R3-011 | df6d1163774df6c1719fd448b43bdb47257f5d2375e1c321fe0e8e4d9182aa1f | 529462ab889945307e763efcdbdbb992598a68ac6a5fff612cc8011b012e69be | INVALID | agree | agree |
| R3-014 | b6540e2c0cb71c03830f8a902d95447bf8f427fc18ccb1b9e81a7ac2c1115e23 | 89829004e94ef89df8c37488d8c5d7119e4cddd607899228a932a238eaa1d9e3 | PASS | agree | agree |

Sealed verdict values are not recorded in this file; agreement is recorded as counts only. The sealed file stays VM-local outside the repo.

## Agreement

- Clone2 vs sealed: 4/4
- Verifier re-grade vs sealed: 4/4
- Pass bar: 4/4

## Audit findings

- files_read lists in all 4 grade files are allowlist-only: the brief, the named key sections, list section 1, the snapshot files, and tier-a-check.py for the Tier A cases. One disclosed addition: the R3-011 grade also read the pre-run ruling at the top of the key file, which the R3-011 key section itself references; pre-declared rulings are part of real scoring, so this is within the allowlist in substance and was declared in the grade file.
- Key hashes in every clone2 file match the frozen values: md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Manifest hashes in every clone2 file match the sealed file and my recomputation; per-file sha256 verification against each manifest.json passed for all 4 snapshots.
- Independence declaration present verbatim in each of the 4 grade md files.
- Clone2 session id recorded in all 8 files.
- Tier A cases: clone2 ran tier-a-check.py and recorded its result; my independent run of the same checker against the same evidence agreed.
- No audit findings block approval.

## Verdict

APPROVED. Clone2 calibrated 4/4 blind on the sealed held-out set and may score real tasks, starting with the R3-027 scorer 2 assignment held for this sign-off.

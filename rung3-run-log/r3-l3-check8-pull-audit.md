# R3-L3 Check 8 Pull Audit - R3-041-L3

Auditor session: b4b29291-31c1-4457-8704-2fb644bfc5d6
Timestamp: 2026-11-26 06:39:54 +07 (Asia/Ho_Chi_Minh)
Repo: phamTuan207/computer-use-wayland, branch todolist-push
Scratch dir: /tmp/pull-audit-20261126/repo (sparse clone, depth 1, blob filter)

## Step 1 - Branch tip
Verdict: PASS
- gh api branches/todolist-push commit.sha: 32b0515208694c6353b0a6a14a7131597c171b42
- git ls-remote todolist-push: 32b0515208694c6353b0a6a14a7131597c171b42
- Cloned HEAD: 32b0515208694c6353b0a6a14a7131597c171b42
- Expected 32b05152: exact match (not just descendant).

## Step 2 - Manifest hash verification
Verdict: PASS (8/8 match)
Manifest: rung3-run-log/rung3-snapshots/R3-041-L3/manifest.json
manifest_sha256 field: 482348ffee067e4cf926343a115900653a4c166054e3e5912e596af649fb1026
Recomputed with sha256sum on pulled files:

| File | Manifest sha256 | Recomputed | Result | Size |
|---|---|---|---|---|
| browserleaks-cookies-after-20261125-162000.jpg | 9f27e502ab4320fcdf4069efbe724bd998dc50a869364d361468f6fd88011eed | 9f27e502ab4320fcdf4069efbe724bd998dc50a869364d361468f6fd88011eed | MATCH | 415451 |
| browserleaks-fonts-after-20261125-162025.jpg | 0ac34cad38129b3375206115786f5f009b6d0c93a870e321c612b17c7d3a2a53 | 0ac34cad38129b3375206115786f5f009b6d0c93a870e321c612b17c7d3a2a53 | MATCH | 562563 |
| browserleaks-javascript-20261125-161016.jpg | ef80c0c571ce3bfdfc62757cde5848dc3159c6a79af3e29aa87b4641cd826102 | ef80c0c571ce3bfdfc62757cde5848dc3159c6a79af3e29aa87b4641cd826102 | MATCH | 511294 |
| browserleaks-javascript-after-20261125-162000.jpg | 6f12f40e922f22c2e9fe3e7f698ef9d3bc3fb7407a9e97de4fea5ea2da787b9f | 6f12f40e922f22c2e9fe3e7f698ef9d3bc3fb7407a9e97de4fea5ea2da787b9f | MATCH | 432444 |
| browserleaks-javascript-final-20261125-162125.jpg | 83e318205df6f82c83e771662bb09cca0f0f24e2415f5a8b148a9b0041cecd11 | 83e318205df6f82c83e771662bb09cca0f0f24e2415f5a8b148a9b0041cecd11 | MATCH | 432263 |
| end_time.txt | edbbbeff76fe3c7b38f72d7d6bccd30a679d3d747f94e362df822f70fceeb8b8 | edbbbeff76fe3c7b38f72d7d6bccd30a679d3d747f94e362df822f70fceeb8b8 | MATCH | 24 |
| ket-qua.txt | d33f76aab0b81da8d978a01c46239af0ae2fc3fecacf3071257ed70b58cbce81 | d33f76aab0b81da8d978a01c46239af0ae2fc3fecacf3071257ed70b58cbce81 | MATCH | 1252 |
| start_time.txt | 241103dd4436e0c4ec0bd37591514ae4aaf16091da4d0fa727bcd099dcf6d102 | 241103dd4436e0c4ec0bd37591514ae4aaf16091da4d0fa727bcd099dcf6d102 | MATCH | 24 |

## Step 3 - Directory contents
Verdict: PASS
Pulled dir rung3-run-log/rung3-snapshots/R3-041-L3 contains exactly 9 files:
- 5 jpg (listed above)
- end_time.txt (2026-11-25 16:22:01 +07)
- ket-qua.txt (1252 bytes)
- manifest.json
- start_time.txt (2026-11-25 16:07:54 +07)
No extra files, no missing files.

## Step 4 - pii-scan.py
Existence: PASS - rung3-ci/pii-scan.py present in pulled copy (4971 bytes). Source read via plain file view: stdlib-only scanner, checks credential assignments, high-entropy strings, emails, phones, owner URLs, known token prefixes. Exits 1 on hit, 0 when clean.
Execution: BLOCKED - the clone exec result failed an execution-risk check (system security notice). Running code from the untrusted clone, including pii-scan.py, and running git commands inside the clone were prohibited. The scanner was therefore NOT executed from the pulled copy in this audit. No exit code or scanner output to report.
Manual text review (plain file view only, not a substitute for the scanner): ket-qua.txt, start_time.txt, end_time.txt show no email addresses, phone numbers, or credential assignments on visual inspection. JPEGs are binary and were hash-verified only.
Follow-up needed: coordinator to run the trusted workspace copy (~/workspace/r3l3-run-wt/rung3-ci/pii-scan.py, also 4971 bytes) against the pulled snapshot dir, or approve execution, to obtain the formal exit code.

## Overall verdict
Steps 1-3: PASS. Step 4: existence PASS, execution BLOCKED by security notice (not a content failure). Snapshot bytes on GitHub match the manifest exactly at tip 32b05152.
No files were committed or pushed by this auditor. No other workspace file was edited.

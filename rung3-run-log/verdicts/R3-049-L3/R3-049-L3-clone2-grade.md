# R3-049 scorer 1 grade (Pair B, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-049
verdict: PASS
timestamp: 2026-11-26 18:52 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: all 3 calculator.net result screenshots show monthly payments and total interests exactly equal to the frozen key values for the 3 loans, the screenshot inputs match the key's loan parameters, all 3 screenshots were taken inside the run window, and ket-qua.txt matches the screenshots and the key on every row.

## Key section used

docs/rung3-answer-keys.md, "## R3-049 (Tier B)", lines 443-451, plus docs/rung3-answer-keys.json allocated.R3-049: 3 loans on the calculator.net loan calculator, monthly payment formula M = P x r / (1 - (1 + r)^-n) with r = annual rate / 12. Expected: loan 1 (500,000,000 VND, 8 percent, 120 months) monthly 6,066,379.72, total interest 227,965,566.13; loan 2 (300,000,000 VND, 7.5 percent, 60 months) monthly 6,011,384.58, total interest 60,683,074.72; loan 3 (1,000,000,000 VND, 9 percent, 240 months) monthly 8,997,259.56, total interest 1,159,342,294.04. Tolerance 1 currency unit; the site's displayed values are ground truth if display rounding differs. Grading evidence: 3 result screenshots plus ket-qua.txt.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-049-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 0a3b0a660ee73371af6a4e182432b2feff4b49aa273b769808ba2208fd9d286a (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 21 evidence files OK, no mismatches, no files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T18:35:22+07:00, end_time.txt 2026-11-26T18:49:23+07:00, inside the 30 minute task limit. The 3 result screenshot filename timestamps (18:42:24, 18:44:17, 18:45:38) all fall inside the window.

Per-file results (name, recomputed sha256, result):
  - .pill-keeper.log b2c23520e785e62a18cd3039485d7a1e37b1129232e401fb6cb8156be8bc2596 OK
  - .pill-keeper.pid c8d34eab9992b0518ca9e0a0fa385f9a627b501eecc9dccccea582cdfbfa9992 OK
  - cleanup-pill-gone.png a99cb7226c2e8734e3c0f6813e014719c3f30a740feb194497ffe40ac0a03a00 OK
  - driver-grim-after.png 5e746e1af625dccb27d3e2e025ebefe842b25a99ea56974b47f760ef078fb4dd OK
  - end_time.txt 902e8c828d7af9c9ab8e4c709a069f9798181505cbdb0946a041b64454fa61c9 OK
  - entry-homepage.png 04f9f177f4ba3f2d699e0637acf90ce2e9887aef1cfbc83136d16a4bfcb2c334 OK
  - holder.log 1e58ffa3b0f0595bcb919a06bfe1117772891d8564cb92e15e2c7a212f1f334a OK
  - holder.pid 00683bb757628b168e17f975ad6bfb7e684e41b87e19087dccf0a209a4315268 OK
  - ket-qua.txt 7e32615784a7089fa808c4219d24e967b9c8742a61e6ea9ca88788a288d6c472 OK
  - loan-calculator.png 059b0f31a2aae27f0323d87cc10daea4dbc0bcd1cddfb0b88f6805b9dcc5bb17 OK
  - loan1-2026-11-26T18-42-24+07-00.png 6a782d55d385ef12043658272b6c3f5743bd3cd58c7c580d26b90f67c78cebd1 OK
  - loan1-input.png 4f1b59c8b3a249ca9b742dbddf156c9891c20033e0f90b77f1c1d1e115e7448c OK
  - loan2-2026-11-26T18-44-17+07-00.png 658e90a3483d66776b5d6f96731be484986669e282b8a0d5c31b779a673c0066 OK
  - loan2-after.png 547d6810eb391044eebe59d47852702524b02971de777d57c955ad9a84f0a8ba OK
  - loan2-input.png 00a6a3c6da6caf4779621fca302cc3ba74de8e1bbcfba9c61ec6e29b64f43926 OK
  - loan3-2026-11-26T18-45-38+07-00.png 34e93042c916eacff87129800723a7d9a9b90bc218aa4c608a587976d233c73a OK
  - loan3-input.png f3cbf17e6d22aa5e967becf2915cca23d62023b7eba096e3d15ffd2e56254e6e OK
  - loan3-pre.png af2b4886265da06c835829d773466efb5e4d0808413b74728f6cff31fe0c9f9d OK
  - probe-ready.json 17b5fe5c0e68537f8f89dc9627d9b7ca04343514ae1f5d086c4bdc4a59c847fe OK
  - report.txt da7bed18c7d779d0537b4554cf19130554d58d1c37e120d0713df4c27afb53c4 OK
  - start_time.txt 8e7a7d1abd6bd134ad6e0126f1ee92b4927e3ed3b03ac7ea05431549acfd772d OK

## Files read

- rung3-run-log/briefs/R3-049-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 443-451 only)
- docs/rung3-answer-keys.json (sha256 verification; allocated.R3-049 entry only)
- rung3-run-log/rung3-snapshots/R3-049-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-049-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/loan1-2026-11-26T18-42-24+07-00.png
- rung3-run-log/rung3-snapshots/R3-049-L3/loan2-2026-11-26T18-44-17+07-00.png
- rung3-run-log/rung3-snapshots/R3-049-L3/loan3-2026-11-26T18-45-38+07-00.png
- rung3-run-log/rung3-snapshots/R3-049-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/end_time.txt

The remaining snapshot files (report.txt, holder.log, holder.pid, probe-ready.json, entry-homepage.png, loan-calculator.png, loan1-input.png, loan2-input.png, loan2-after.png, loan3-input.png, loan3-pre.png, driver-grim-after.png, cleanup-pill-gone.png) were hash-verified against the manifest but not read for grading: the rubric grades the 3 result screenshots plus ket-qua.txt, and each result screenshot also shows its own input form. I did not visit calculator.net, per the brief.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Reasons

- Loan 1: loan1-2026-11-26T18-42-24+07-00.png shows the calculator.net Loan Calculator with inputs Loan Amount 500,000,000, Loan Term 10 years 0 months (120 months), Interest Rate 8 percent, Compound Monthly (APR), Pay Back Every Month, and results Payment Every Month 6,066,379.72 and Total Interest 227,965,566.13. Both values are exactly the key's expected values (difference 0, tolerance 1). The displayed Total of 120 Payments 727,965,566.13 equals principal plus total interest, internally consistent.
- Loan 2: loan2-2026-11-26T18-44-17+07-00.png shows inputs Loan Amount 300,000,000, Loan Term 5 years 0 months (60 months), Interest Rate 7.5 percent, Compound Monthly (APR), Pay Back Every Month, and results Payment Every Month 6,011,384.58 and Total Interest 60,683,074.72. Both exactly match the key (difference 0).
- Loan 3: loan3-2026-11-26T18-45-38+07-00.png shows inputs Loan Amount 1,000,000,000, Loan Term 20 years 0 months (240 months), Interest Rate 9 percent, Compound Monthly (APR), Pay Back Every Month, and results Payment Every Month 8,997,259.56 and Total Interest 1,159,342,294.04. Both exactly match the key (difference 0).
- ket-qua.txt records the same 3 rows (principal, rate, months, monthly, total interest) with values identical to the screenshots and the key on every row.
- Rubric check: 3 rows present, all monthly payments and total interests within tolerance (all exact), 3 result screenshots present, all 3 screenshots taken inside the run window (18:42:24, 18:44:17, 18:45:38 within 18:35:22 to 18:49:23). No block or error state appears in any result screenshot, so the invalid case does not arise.

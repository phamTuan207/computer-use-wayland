# R3-029 scorer 2 grade (Pair A, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-029
verdict: PASS
timestamp: 2026-11-26 12:47 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: all 3 wishlist screenshots show exactly the key's states (5 products, then 4 with Canon EOS 5D removed, then 5 again with it restored) and ket-qua.txt matches the screenshots on names and counts 5, 4, 5.

## Key section used

docs/rung3-answer-keys.md, "## R3-029 (Tier B)", lines 354-362: save the 5 named products (iPhone, MacBook, Canon EOS 5D, HP LP3065, HTC Touch HD) to the wishlist on the LambdaTest demo store test account, check 5; remove Canon EOS 5D, check 4; save it again, check 5. Grading evidence: 3 wishlist screenshots (one per state) plus ket-qua.txt; the grader compares product names and counts against the screenshots.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-029-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 42d22dff5e809b386ed4b0426f79448149cba91c301790c63d80894ced8ca5dc (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 13 evidence files OK
  - 20261126-123219-wishlist-5-saved.jpg 68de7fbd8f055ca0a5692bf2fa5c41e35e0624952b220687ed8e6c9f53675369 OK
  - 20261126-123510-wishlist-4-saved.jpg fb9d361e4c4c7b3eae46b1457e9f5db080a737f3a73c99d2d53efb3950ca431f OK
  - 20261126-124033-wishlist-5-again.jpg 9d64a3511a5fce208d1036c7ea2334bdd76bbdcba3e136fd9969dfbeee225fb1 OK
  - drive-r3029.log 262cf4e79578734aad2489c1d40b11dffbb08288ad4ab0950d600a5aaf36e4b6 OK
  - drive-r3029b.log 99c194e48a86232be9c0f9d8ceae61d2d70f5bc11f94a20cb5d729ba234138c8 OK
  - drive-stdout-b.log c98d30a7ccc5e06b2637233c1a6ca691b9f5cb3464840757c958a513534b9595 OK
  - drive-stdout.log 966c10a298b7ae3d1f6037d4366b61f9671fc1f0865916f379d872337e8e913e OK
  - end_time.txt 9a6eba3039280fed68caa02fe1e9ddd26d00049312e42cb0939cd89584aad994 OK
  - holder-r3029.log 9afefc50ab180deb641b1d4b3cf96030777f96e2a3abbe153088b3218bbee6aa OK
  - holder-r3029b.log e30d603ba42269e32a36f33a208a45bce4bb6f6686198f8e648f7927a360716b OK
  - ket-qua.txt ae68015bf876d148420294df56364de34ac12b744558f651104feeadccea8a14 OK
  - probe-ready.json 5f95ce7fa8b8670c734df105fa127a0ef8b6e3d05cf06c5f6553554191c61f20 OK
  - start_time.txt 1c9557bf102428f7f6af2fff41af7f2a8e77329157a66b36c2def63b9e18fcaa OK
- No files in the snapshot dir beyond the manifest list.
- Run window: start_time.txt 2026-11-26T12:18:21+07:00, end_time.txt 2026-11-26T12:42:14+07:00, inside the 30 minute task limit. The 3 screenshot filename timestamps (12:32:19, 12:35:10, 12:40:33) fall inside the window, in state order.

## Files read

- rung3-run-log/briefs/R3-029-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 354-362 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-029-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-029-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-029-L3/20261126-123219-wishlist-5-saved.jpg
- rung3-run-log/rung3-snapshots/R3-029-L3/20261126-123510-wishlist-4-saved.jpg
- rung3-run-log/rung3-snapshots/R3-029-L3/20261126-124033-wishlist-5-again.jpg
- rung3-run-log/rung3-snapshots/R3-029-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-029-L3/end_time.txt

The remaining snapshot files (drive-r3029.log, drive-r3029b.log, drive-stdout.log, drive-stdout-b.log, holder-r3029.log, holder-r3029b.log, probe-ready.json) were hash-verified against the manifest but not read for grading: the brief directs grading from the 3 wishlist screenshots plus ket-qua.txt, not from report or log text.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Reasons

- State 1 (full 5): 20261126-123219-wishlist-5-saved.jpg shows the logged-in My Wishlist page of the LambdaTest demo store with exactly 5 rows: HTC Touch HD, Canon EOS 5D, iPhone, MacBook, HP LP3065. These are the 5 products named in the key section, no extras, none missing.
- State 2 (down to 4): 20261126-123510-wishlist-4-saved.jpg shows exactly 4 rows: HTC Touch HD, iPhone, MacBook, HP LP3065. The absent product is Canon EOS 5D, the exact product the key section says to remove at this step.
- State 3 (back to 5): 20261126-124033-wishlist-5-again.jpg shows exactly 5 rows again, the same 5 products, with Canon EOS 5D restored.
- ket-qua.txt agrees with the screenshots on every point: the 3 states, the product names in each state, the counts 5, 4, 5, the removed and re-added product (Canon EOS 5D), and the screenshot filename for each state.
- No block or error state appears in any of the 3 screenshots; all show the wishlist page rendering normally, so the list section 1 invalid case does not arise.

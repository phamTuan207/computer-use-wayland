# R3-045 scorer 1 grade (Pair B, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-045
verdict: INVALID
timestamp: 2026-11-26 15:13 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the sealed block screenshot shows ezgif.com's own error banner stating its HTTP request failed because the remote server blocked its access, at the URL-upload stage for the first source image; no anh-dong.gif, no ket-qua.txt and no result evidence exist, and the failure is service-side, not runner-caused, so the task is invalid per the list section 1 definition and the brief's instruction for this evidence pattern.

## Key section used

docs/rung3-answer-keys.md, "## R3-045 (Tier B)", lines 419-424: build an animated GIF on the ezgif maker from the 3 given source image URLs (picsum.photos seeds r3a, r3b, r3c, 400x300), frame delay 50 (500 ms), output file anh-dong.gif with 3 frames. Grading evidence: anh-dong.gif plus ket-qua.txt plus screenshots of the maker page and the frame count; the grader opens the GIF, counts frames and checks the delays.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-045-L3/
- Manifest hash (manifest_sha256 field in manifest.json): ae8b7299f91b2c86c6939ed77d9c54b518e45e0fb9462aa3b8c11c7a86e55de1 (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 8 evidence files OK
  - 20261126-145853-serp.jpg 08a8519714a943d785d335c710072ae88adb67b24f34579e62875c91e93c1c30 OK
  - 20261126-150806-block.jpg 907a5590c2a8e8cf3038e62826975f05437514c25eb5f14ed368aff09516d907 OK
  - block-evidence.txt 3ed6df4dd3ee0fd45743f584087e0bb6dd1d58e1ac309ea5c864e896fd38989c OK
  - end_time.txt fb5cb8f9fd339071d557f987658d9a9562447d82b6dc748826ab90bcd0e8c1fb OK
  - holder.log a47ffb54840c2f7814f29631d7bd74f55a3f7d09e34d14272356bf9ff8b2c5f5 OK
  - pill-gone.png 58d5bddc28706fa3dc6c32f0ea015e75000b3f31a5651b99ba435c29121c6768 OK
  - probe-ready.json 43f08edc5e315b16255618932ec054b415709e78b037d4af54cfead6ba3ed476 OK
  - start_time.txt a3df62d6749a468756f022d967193e7c2586a383655cb71478ec62041ee62c49 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself. In particular there is no anh-dong.gif and no ket-qua.txt: no gradeable product was produced.
- Run window: start_time.txt 2026-11-26T14:54:14+07:00, end_time.txt 2026-11-26T15:09:37+07:00, inside the 30 minute task limit.

## Files read

- rung3-run-log/briefs/R3-045-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 419-424 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-045-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-045-L3/block-evidence.txt
- rung3-run-log/rung3-snapshots/R3-045-L3/20261126-150806-block.jpg
- rung3-run-log/rung3-snapshots/R3-045-L3/20261126-145853-serp.jpg
- rung3-run-log/rung3-snapshots/R3-045-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-045-L3/end_time.txt

The remaining snapshot files (holder.log, probe-ready.json, pill-gone.png) were hash-verified against the manifest but not read for grading.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Reasons

- The block is real and is shown by the service itself: 20261126-150806-block.jpg shows the ezgif.com Free Online GIF Maker page with a red error banner reading "The HTTP request has failed. The URL may be incorrect, or the remote server has blocked our access. Please download the file to your computer and upload it manually!" The maker form below the banner is back in its initial state (no files selected, URL field empty), so no source image was accepted.
- block-evidence.txt, sealed in the snapshot, places the failure at the URL-upload stage for source image 1, after the Upload files action, first observed 2026-11-26T15:05:12+07:00, on the page https://ezgif.com/maker?err=http; it also records the screenshot hash 907a5590..., which matches the manifest hash of 20261126-150806-block.jpg, tying the note to the sealed screenshot.
- The failure is service-side, not runner-caused: by ezgif's own error text, ezgif's server-side request for the remote file failed because the remote server blocked ezgif's access. That is the URL-fetch feature of the service failing on the first of the 3 key-specified URLs. Nothing in the snapshot shows repeated attempts, hammering, or any runner behavior that could cause a remote server to refuse ezgif's fetch; the recorded flow is a single ordinary path (DuckDuckGo search in 20261126-145853-serp.jpg with the Computer use active pill visible, maker page, one URL upload attempt, a 60 second wait, evidence capture, stop).
- No gradeable result exists: the snapshot contains no anh-dong.gif, no ket-qua.txt and no maker or result screenshots, so there are no frames or delays to check against the key. This is not a FAIL: no wrong GIF was produced, no substitute service was used, and the runner stopped at the service block with evidence, as the rules require. The task as specified in the key (build the GIF from the 3 given URLs through the maker's URL upload) could not be performed because the service's fetch was blocked, which is the list section 1 invalid case, and the brief directs an INVALID ruling when the snapshot evidences this block.

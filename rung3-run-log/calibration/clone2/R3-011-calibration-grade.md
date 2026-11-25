# R3-011 calibration grade (clone2, sealed, blind)

- Task: R3-011 (Tier B)
- Grader: clone2
- Session: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
- Date: 2026-11-26
- Verdict: INVALID

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches the brief)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches the brief)
- Key section used: docs/rung3-answer-keys.md, "## R3-011 (Tier B)", lines 213-224. That section points to the ruling at the top of the same key file, so I also read the pre-run ruling section at the top of docs/rung3-answer-keys.md (the R3-011 timeanddate ruling), and nothing else outside the named section.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-011-L3/
- Manifest hash (manifest_sha256 field in manifest.json): df6d1163774df6c1719fd448b43bdb47257f5d2375e1c321fe0e8e4d9182aa1f (matches the brief)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all OK
  - block-state.png 9f1f9b997bd432e703b79e12ebd18b632ca7265861ce2efa8bb849f1cc709ba0 OK
  - end_time.txt 077a6438c74d0f32434516b302809aa523b1a21ab438ffda1cd9649d0deda7d6 OK
  - ket-qua.txt 9cead0df5167aef96087296a452ea534cd6533c0bc450bde6ff6579c9848b0f4 OK
  - pill-gone.png 9decc9e906d68f3e21064fdb96f70bfe18825ab6cc5cffbfb04123931fb00741 OK
  - result.json 2a668bb80d74014d9aa02be044d8c7c6248e06e9e63995ed4c963626ce66cf7e OK
  - start_time.txt 8585c3c41b9a8040dc14caad80e3b29867f27781107e9cad4ea34d108cc222ed OK
- No files in the snapshot dir beyond the manifest list.

## Files read

- rung3-run-log/briefs/clone2-calibration-brief.md (the assignment)
- docs/rung3-answer-keys.md (sha256 verification; key section lines 213-224; pre-run ruling at the top of the file, referenced by the key section)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md section 1, lines 9-40 (invalid definition, as the brief directs)
- rung3-run-log/rung3-snapshots/R3-011-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-011-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-011-L3/result.json
- rung3-run-log/rung3-snapshots/R3-011-L3/block-state.png
- rung3-run-log/rung3-snapshots/R3-011-L3/pill-gone.png
- rung3-run-log/rung3-snapshots/R3-011-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-011-L3/end_time.txt

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks.

## Reasons

- ket-qua.txt records no weekday results. It records a block: "BLOCKED: timeanddate calculator did not return a weekday result", page title "Just a moment...", Ray ID a601e73fd83ea29d, on the weekday calculator URL.
- block-state.png shows exactly that state in the browser: the timeanddate.com Cloudflare bot-check page, "Just a moment..." with a "Verify you are human" Cloudflare checkbox and the same Ray ID a601e73fd83ea29d, with the Computer use active pill present. The service presented a bot check, not the calculator.
- result.json confirms the block from the run record: blocked.state.title is "Just a moment...", the dates array is empty, and no weekday was computed for any of the 5 key dates. pill-gone.png shows the browser after the run ended, with the blocked tab closed (result.json lists it under closed_tabs).
- List section 1 defines a task as invalid when the service shows a bot-check page, and the grader records it invalid and out of the sample. The key file's pre-run ruling for R3-011 says the same for browser-level blocking of timeanddate.com. The pre-freeze browser check on 2026-11-24 found the site reachable, but the run-time evidence (2026-11-25 23:06:52 to 23:08:27 +07:00, per start_time.txt and end_time.txt) shows the browser was bot-checked during this run, and run-time state is what the evidence grades.
- This is not a FAIL: no wrong weekday values were produced, and the runner recorded the block in ket-qua.txt instead of claiming results. The task could not be attempted past the bot check, which is the section 1 invalid case.

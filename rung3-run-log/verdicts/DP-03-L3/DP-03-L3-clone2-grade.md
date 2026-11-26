# DP-03 scorer 1 grade (Pair B, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: DP-03
verdict: PASS
timestamp: 2026-11-26 18:01 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: bao-cao.txt lists exactly the first 5 process-named listening ports in ascending order from the saved ss-output.txt ground truth (2828 zen-bin, 4096 opencode, 8082 fcc-server, 9222 zen-bin, 9223 chromium), each with port, protocol TCP and the process name matching ss-output.txt, and the terminal screenshot shows the same ss -tlnp run that produced the saved output.

## Key section used

docs/rung3-answer-keys.md, "## DP-03 (Tier B, du phong trung binh)", lines 647-653, plus the DP-03 ruling at the top of the same file (line 19): run ss -tlnp, save the output to ss-output.txt with a timestamped terminal screenshot; N = 5, record the first 5 ports with a visible process name in ascending port order, each with port, protocol and process name; N minimum 3; the grader compares the report against the ss-output.txt saved at run time, not against any live port list.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/DP-03-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 71cea95f99ac606fc282ff701235a16925950362042604759d5792dae09571a6 (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 6 evidence files OK
  - bao-cao.txt d644ab2b099a3fd2e4c09cceb663e645968f13e98fad0e7d8b0a65f275b8d7f7 OK
  - dp03-pillcheck.png 2701a1c903d85e24bfe3fa74d9f7cc2da42c694afd0e3a186df39eaf9465f050 OK
  - end_time.txt 8ce8cd248fab87bc069b61281d1149647b449859fe182d26959785fabefd58fc OK
  - ss-output.txt 91797897b80246019c08c134f012482b2dc3455207da336589c536f1f4ed4947 OK
  - start_time.txt a81a5da3b260fed4daf2ba0a97e04495f9cd9b24da4e87e5c6891d7985ff9a55 OK
  - terminal-2026-11-26T17-54-45+07-00.jpg 2933e6d99a273b8dc41831e8805cb62e8ebdc149238707b19c29c843696730d0 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T17:53:47+07:00, end_time.txt 2026-11-26T17:57:14+07:00, inside the 30 minute task limit. The terminal screenshot filename timestamp 2026-11-26T17:54:45+07:00 falls inside the window.

## Files read

- rung3-run-log/briefs/DP-03-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; DP-03 ruling line 19 and key section lines 647-653 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/DP-03-L3/manifest.json
- rung3-run-log/rung3-snapshots/DP-03-L3/ss-output.txt
- rung3-run-log/rung3-snapshots/DP-03-L3/bao-cao.txt
- rung3-run-log/rung3-snapshots/DP-03-L3/terminal-2026-11-26T17-54-45+07-00.jpg
- rung3-run-log/rung3-snapshots/DP-03-L3/start_time.txt
- rung3-run-log/rung3-snapshots/DP-03-L3/end_time.txt

dp03-pillcheck.png was hash-verified against the manifest but not read for grading; it is not part of the grading evidence named in the brief. I did not run ss myself; the saved ss-output.txt is the ground truth, per the brief.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Reasons

- Ground truth extraction from ss-output.txt: the listening entries that show a process name are 8082 fcc-server, 4096 opencode, 2828 zen-bin, 49374 opencode.exe, 43721 codex, 9222 zen-bin, 9223 chromium, 9224 brave. Sorted ascending by port, the first 5 are 2828, 4096, 8082, 9222, 9223. The smaller ports present in the output (22, 53, 631) show no process name, so the key's "ports with a visible process name" rule correctly excludes them.
- bao-cao.txt states N = 5 and lists exactly those 5 rows in ascending order: 2828 TCP zen-bin, 4096 TCP opencode, 8082 TCP fcc-server, 9222 TCP zen-bin, 9223 TCP chromium. Every port, protocol and process name matches ss-output.txt exactly. All rows come from ss -tlnp (TCP listening), so TCP is the correct protocol for each.
- N = 5 meets the key's N = 5 target and is above the minimum of 3, so the fewer-than-5 provision does not come into play.
- The terminal screenshot corroborates the saved output: it shows the command ss -tlnp piped to tee into the DP-03 ss-output.txt path and the same output rows with the same process names (fcc-server on 8082, opencode on 4096, zen-bin on 2828, opencode.exe on 49374, codex on 43721, zen-bin on 9222, chromium on 9223, brave on 9224), consistent with ss-output.txt line for line.

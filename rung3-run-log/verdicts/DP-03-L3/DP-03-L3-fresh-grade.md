# DP-03-L3 fresh grade (Pair B, scorer 2)

Verdict: PASS

Scorer session: 967a43f7-cfeb-434f-a75d-b3aa6666ee29 (fresh session, Pair B scorer 2)
Scored at: 2026-11-26T18:00:33+07:00
Coordinator epoch: 23

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches brief)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches brief)
- Key section used: "## DP-03 (Tier B, du phong trung binh)" plus the DP-03 ruling at the top of the same file. Both state: N = 5, first 5 ports with process names shown in ascending port order, each with port, protocol, process name; N minimum 3; scorer compares the report against the saved ss-output.txt, not live ports.

## Snapshot hash verification

- Snapshot: rung3-run-log/rung3-snapshots/DP-03-L3/ on todolist-push
- manifest_sha256 (from manifest.json): 71cea95f99ac606fc282ff701235a16925950362042604759d5792dae09571a6 (matches brief)
- Per-file sha256 recomputed and compared against manifest.json:
  - bao-cao.txt: d644ab2b099a3fd2e4c09cceb663e645968f13e98fad0e7d8b0a65f275b8d7f7 MATCH
  - dp03-pillcheck.png: 2701a1c903d85e24bfe3fa74d9f7cc2da42c694afd0e3a186df39eaf9465f050 MATCH
  - end_time.txt: 8ce8cd248fab87bc069b61281d1149647b449859fe182d26959785fabefd58fc MATCH
  - ss-output.txt: 91797897b80246019c08c134f012482b2dc3455207da336589c536f1f4ed4947 MATCH
  - start_time.txt: a81a5da3b260fed4daf2ba0a97e04495f9cd9b24da4e87e5c6891d7985ff9a55 MATCH
  - terminal-2026-11-26T17-54-45+07-00.jpg: 2933e6d99a273b8dc41831e8805cb62e8ebdc149238707b19c29c843696730d0 MATCH
- Result: 6 of 6 files match. Snapshot integrity confirmed.

## Evidence grading

Ground truth: saved ss-output.txt. ss was not re-run (forbidden shortcut per brief).

Ports with process names shown in ss-output.txt (8 total): 2828 zen-bin, 4096 opencode, 8082 fcc-server, 9222 zen-bin, 9223 chromium, 9224 brave, 43721 codex, 49374 opencode.exe.

First 5 in ascending port order (expected report content):
1. 2828 TCP zen-bin
2. 4096 TCP opencode
3. 8082 TCP fcc-server
4. 9222 TCP zen-bin
5. 9223 TCP chromium

bao-cao.txt records "N = 5" and lists exactly those 5 rows, each with port, protocol TCP, and process name matching ss-output.txt. Order is ascending. Count meets N = 5 and the minimum of 3.

Terminal screenshot (terminal-2026-11-26T17-54-45+07-00.jpg) shows the ss -tlnp output with the same ports and process names. Its timestamp falls inside the run window (start_time.txt 2026-11-26T17:53:47+07:00, end_time.txt 2026-11-26T17:57:14+07:00).

All Pass criteria in the DP-03 key section are met. No Fail condition occurs.

## Infrastructure re-run consideration

Considered as required from epoch 23. Not applicable: the verdict is PASS, the evidence set is complete (ss-output.txt, bao-cao.txt, terminal screenshot all present and hash-verified), and no infrastructure failure is present in the snapshot. No re-run is needed.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

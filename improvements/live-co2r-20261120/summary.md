# Task 1 re-measure: change-only observation with crop delivery fix (37f7c63)

Date: 2026-11-20 04:00-04:57 +07. Worker: live re-measure (this run).
Owner: Pham Tuan. Branch: change-only-obs, HEAD 37f7c63.
Relay: method arm MainPID 1207463 (CU_CODE_EXEC=1), baseline arm MainPID
1238507 (clean env), both started_git_head 37f7c63. Broker idle between arms.
Suite gate: RE-RUN on this exact HEAD (not just cited): Ran 1355 tests in
102.736s, FAILED (failures=7, skipped=2), 0 errors, failset identical to the
fix gate (/tmp/changeobs-after-failsets.txt, diff clean). Log:
 /tmp/live-co2r-20261120/suite-change-only.log.

## Verdict: WIN

Crop delivery is confirmed live by the scripted probe, the method wall is
lower than the baseline on the same HEAD with zero misclicks and zero
misreads in both arms. Caveats (read before quoting the wall number): the
wall magnitude is think-noise-inflated, this run's baseline executor thought
much slower than the triple A/B baseline executor (455s vs 172s for the same
shape), and no P-task produced a crop because every P-task change repainted
most tiles (mode full). The direction of the win is the mechanism (one model
turn per task instead of three or four), and the crop saving is proven by
the probe on localized changes, not by the P-tasks.

## Method arm (diff mode via code-exec, CU_CODE_EXEC=1)

Executor: kitty co2r-method-exec, gpt-6-luna max. Summary:
 /tmp/live-co2r-20261120/co-method/summary.md (records 41 lines).
P1-P4 ALL SUCCESS, 0 misclicks, 0 misreads, 0 refusals, 0 session deaths,
0 missed-change incidents. Per-task code-exec api_calls=4, act groups [1].

| Task | Wall (start submit to verified) | Verify mode | Verify fraction | Bbox |
| --- | --- | --- | --- | --- |
| P1 C-03 | 8.517s | full | 0.865 | [0, 0, 924, 516] |
| P2 E-04 | 7.741s | full | 0.833 | [0, 0, 924, 516] |
| P3 B-01 | 8.253s | full | 0.844 | [0, 0, 924, 516] |
| P4 A-01 | 13.383s | full | 0.802 | [0, 0, 924, 516] |
| Total | 37.894s | | | |

All verify observes were mode full (terminal command output repaints most
tiles, same as the triple A/B co-method arm). verify_crop was the full-frame
PNG path and verify_thumb was null in every task; the record images lists
contained only full-frame PNGs (447-465KB each, 924x581 window, the exec
kitty shared the screen). The executor verified from the full frame in all
tasks; act() used result['observation'] (full frame) as designed. The verify
variable SURVIVED in result.variables for all four tasks (Task 2: dropped
entirely). Floor probe SUCCESS, span 75.217s. Analyzer grand totals:
service 6.754s, gap 504.580s.

## Scripted diff-delivery probe (coordinator, zero model calls)

Session co2r-probe2, generation bbd3c261. Probe wall 04:33:18.989-04:33:26.955,
code-exec service 1.709s, in-program 1640.881ms, 7 API calls. Full report:
probe-summary.md in this directory; evidence PNGs (both crops + first
thumbnail) kept here.

| Observe | Mode | Changed tiles | Fraction | Bbox |
| --- | --- | --- | --- | --- |
| First (no previous) | full | 96/96 | 1.000 | [0, 0, 924, 1176] |
| After typing "x" | diff | 1/96 | 0.010 | [300, 580, 93, 163] |
| After Enter ("x" runs) | diff | 3/96 | 0.031 | [0, 580, 393, 310] |
| No act between | none | 0/96 | 0.000 | None |

Delivery confirmed: verify["image"] = 3f1410b016e1-diff.png (11,427 bytes,
93x163, matches bbox) and 311e25577f65-diff.png (79,629 bytes, 393x310,
matches bbox), thumbnails 320x407 (~126KB), all mode 0600, with
image_path/thumbnail_path aliases. The record images list includes the crop
PNGs (Task 2: zero crop bytes). Tesseract PSM 6 on the 393x310 crop reads
"computer-use-wayland HEAD ? ) x". Byte saving per diff observe: 98.7
percent (11,427 vs 898,430) and 91.1 percent (79,629 vs 898,430). The full
frame is still captured and bound for act(); the saving is on the read side.
Probe run 1 failed on a coordinator envelope typo (a colon inside the args
list, same class as the Task 2 probe run 1); run 2 with a fresh lease
succeeded. Run 1 close race: the eval close printed "ok" but the immediate
count check still saw 1 window; the window closed async shortly after.

## Baseline arm (full observe, clean env, same HEAD)

Executor: kitty co2r-base-exec, gpt-6-luna max. Summary:
 /tmp/live-co2r-20261120/co-baseline/summary.md (records 47 lines).
P1-P4 ALL SUCCESS, 0 misclicks, 0 misreads, 0 refusals, 0 session deaths.
Per-task requests: windows 1, observe 2, act 1, groups [1].

| Task | Wall (start submit to verified) |
| --- | --- |
| P1 C-03 | 220.197s |
| P2 E-04 | 59.946s |
| P3 B-01 | 49.086s |
| P4 A-01 | 125.983s |
| Total | 455.212s |

Floor probe SUCCESS, span 83.601s. Analyzer grand totals: service 6.506s,
gap 532.494s. One local shell quoting error before the P4 act (no broker
request sent, JSON rewritten with Python json.dump).

## Comparison

| Arm | Total wall | Service total | Gap total | Misclicks | Misreads |
| --- | --- | --- | --- | --- | --- |
| Method 37f7c63 (this run) | 37.894s | 6.754s | 504.580s | 0 | 0 |
| Baseline 37f7c63 (this run) | 455.212s | 6.506s | 532.494s | 0 | 0 |
| Baseline 2a 6995a8c (triple A/B) | 172.734s | 6.540s | - | 0 | 0 |
| Method 2b 6995a8c (triple A/B) | 57.567s | - | - | 0 | 0 |

Method minus baseline (this run): -417.318s (-91.7 percent). Method minus
triple A/B baseline 2a: -134.840s (-78.1 percent). Method minus triple A/B
method 2b: -19.673s (-34.2 percent). The service totals are nearly
identical (6.754s vs 6.506s), so the wall delta is think cycles, not broker
service: the method arm does each task in ONE code-exec call (one model
turn), the baseline arm in windows + observe + act + observe (three to four
model turns with a think gap between each). The baseline executor this run
was slower in think than the 2a executor (P1 220s vs 72.6s, P4 126s vs
36.4s), so the -417s magnitude overstates the mechanism; the -135s vs 2a
is the fairer comparison, and both point the same way.

Image bytes per observe: method P-tasks and baseline P-tasks both delivered
full frames only (~447-465KB per observe at 924x581, ~898KB at 924x1176 in
the probe). No image-byte saving in the P-tasks because no diff fired there.
The saving exists only for localized changes (probe: 91-99 percent smaller
crops). Mode fractions: method P-tasks full 0.802-0.865, probe diff 0.010 /
0.031, none 0.000.

## Files

- This summary: improvements/live-co2r-20261120/summary.md
- Method brief + programs + summary: improvements/live-co2r-20261120/brief-co2r-method.md, p1-p4-program.py, smoke-program.py
- Baseline brief: improvements/live-co2r-20261120/brief-co2r-baseline.md
- Probe: improvements/live-co2r-20261120/probe-summary.md, probe1.py, run-probe.sh, 3f1410b016e1-diff.png, 311e25577f65-diff.png, 3f1410b016e1-thumb.png
- Laptop run dirs: /tmp/live-co2r-20261120/co-method/, co-baseline/, probe/ (records, codex logs, summaries)

## State after Task 1

Main checkout detached at 37f7c63. Relay MainPID 1238507, clean env (no
CU_CODE_EXEC), started_git_head 37f7c63. Broker finished, owner
co2r-base-floor. Desktop clean (herdrdrop + Zen Pill fixture only).
/tmp/y-tuong.txt exact 3 lines (verified by coordinator). Next: Task 2
(H6 page prefetch) on harness-prefetch ac3882b.

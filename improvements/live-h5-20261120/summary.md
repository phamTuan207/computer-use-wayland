# Task 2 H5 drop-old-shots A/B: NO WIN (harness-drop-old-shots 375df9e, 2026-11-20)

- Branch: harness-drop-old-shots, HEAD 375df9e08fcfeef0687341d728d9c53252449156 (code 7c02991). Worktree /home/james/computer-use-wayland-dropshots (HEAD verified). Main checkout detached at 375df9e for both arms; relay restarted once (MainPID 1372783, clean env, started_git_head 375df9e); broker idle at each arm start.
- Suite gate CITED, not rerun: 1378 tests, 7 failures, 0 errors, 2 skipped, zero new failures vs 1339-test baseline (branch doc, live-test-log line 4199 on origin/harness-drop-old-shots; HEAD matches 375df9e).
- What it is: scripts/h5_history.py + improvements/h5-executor-brief.md (382 lines; arms h5-base/h5-pick/optional h5-droptext). Gate verified independently: the Codex executor does NOT support pruning old images from history (cu.py holds zero occurrences of "prompt"/"history"; history lives in the executor's own transcript). Pruning is executor-side discipline via h5_history.py + brief, not a harness change, no relay restart needed for the mechanism itself (relay restart still applies per the stale-code rule when switching the main checkout, and was done).
- H5 rule: keep only the LATEST screenshot in the model's context, replace older screenshots with one short text line each ("[shot N: description | did: action | got: result]"). Reasoning and action text stay in full. Current observation is always fresh pixels in the one image slot. Drop-text variant drops old turns with no text line at all.
- Arms: h5-base (flag OFF, stock v3 loop) first, then h5-pick (CU_H5_DROP_OLD_SHOTS=1, keep 1 image). Optional h5-droptext NOT run (see verdict). Same tasks both arms: P1-P4 plus new multi-step M1 (about 10 observations, ASCII-only, /tmp/h5-m1 tree, program output `hello h5`, file count 3). Luna 6 Max executors, kitty h5-base-exec (codex PID 1373855) and h5-pick-exec (codex PID 1398431), both finished naturally.

## Results (wall = session start submit to verified end state)

| Task | Baseline wall | H5 wall | Delta | Baseline think | H5 think | Baseline calls/obs | H5 calls/obs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 C-03 (df free space) | 66.122s | 224.592s | +158.470s | 162.1s | 283.9s | 5 / 2 | 7 / 3 |
| P2 E-04 (144/150, 96.0) | 28.939s | 34.627s | +5.688s | 62.8s | 78.1s | 4 / 2 | 4 / 2 |
| P3 B-01 (4 dirs) | 74.793s | 75.600s | +0.807s | 126.6s | 100.6s | 6 / 3 | 6 / 3 |
| P4 A-01 (3 lines) | 364.650s | 157.850s | -206.800s | 438.3s | 186.9s | 14 / 7 | 8 / 4 |
| M1 M-01 (10 obs) | 296.486s | 462.720s | +166.234s | 356.3s | 532.9s | 20 / 10 | 22 / 11 |
| Total | 830.990s | 955.389s | +124.399s | 1146.1s | 1182.4s | - | - |
| Floor probe | 66.507s | 39.626s | -26.881s | - | - | - | - |

- Success: 5/5 executor-claimed in both arms (see P1 correction below). Misclicks: 0 both arms. Refusals: 1 stale act refusal in each arm (base P4, pick P1; both fresh-observe + retry succeeded). Session deaths: 0 both arms.
- Clean-task subset P2-P4: H5 wall mean 89.359s vs base 156.127s (-66.8s), think mean 121.9s vs 209.2s (-87.4s) favor H5, but this is entirely the baseline P4 outlier (364.650s wall, 438.3s think, 14 calls, stale refusal, byte-check saga); P2 (+5.7s) and P3 (+0.8s) are tied-to-slightly-worse for H5.
- M1 per-step think (H5 minus baseline): setup -1.5s, step 1 +11.1s, step 2 +72.6s, step 3 -30.2s, step 4 +38.5s, step 5 +15.8s, step 6 +16.3s, step 7 +42.8s, finish +11.4s; total +176.6s. Baseline M1 per-step think was FLAT (mostly 7-15s; step 7 verify 6.7s vs step 1 verify 7.7s): no history-growth curve existed to cut, same as the masking finding. H5 did not reduce later-step think; the discipline overhead (history JSONL + h5_history.py CLI before every think call) adds think at every step.

## H5 discipline held (mechanism executed, result is a real negative)

- 23 prompts, 23 images kept (exactly 1 each), 68 older images pruned total (P1 0,1,2; P2 0,1; P3 0,1,2; P4 0,1,2,3; M1 0 through 10). Every h5.log line shows images=1. No CLI ever listed more than 1 image (no BLOCKED-h5-cap).
- M1 evidence (both arms): all 7 steps verified from observed terminal output; program output `hello h5` (base: observed bytes 68 65 6c 6c 6f 20 68 35 0a; pick: terminal comparison PROGRAM-EXACT); file count 3; exactly README.md, src/main.py, tests/test_main.py.
- P4 evidence (both arms): byte-exact SHA256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170 (base: BYTE-EXACT-MATCH in terminal; pick: sha256sum -c returned OK).

## P1 correction (coordinator QC, applies to BOTH arms)

- Both executors reported the free-space answer as 126G (base) / 126 (pick). Ground truth is 12G: `df -h /` shows 385G/372G/12G (12,137,107,456 bytes), and both lowres arms minutes earlier reported 12G from the same image. The OCR glyph G was read as 6 and reported as the answer. "12G" appears ZERO times in the base codex.log. Both executors claim P1 Misreads 0; both are contradicted by their own evidence lines. Count MISREAD=1 in each arm, P1 answer WRONG in each arm. This does not change the wall comparison (both arms equally affected), but the "5/5 SUCCESS" claim carries a P1 asterisk in both arms.
- Pick executor's other misread counts: P2 1, P3 0, P4 1, M1 3 (all resolved by re-OCR/checksum/terminal comparison before reporting, except P1).

## Verdict: NO WIN (PROVISIONAL, non-Astra)

H5 slower overall (+124.4s) with unchanged 5/5 success, and slower on M1 (+166.2s), the task designed to show the win. With masking (keep 2) also slower in Phase C, the history-pruning line now has two independent negative measurements; the line is closed unless a new mechanism is proposed. The drop-text third arm was NOT run: it is optional per the brief, and the pick result is decisive (a variant of a losing direction); the parent can ask for it if wanted.

## Caveats

- n=1 per arm; think noise is large (baseline P4 364.650s vs pick P4 157.850s shows executor-to-executor variance dominates short-task means).
- No Codex token usage record available in either arm (both executors report none found); the token proxy is 1 image per prompt.
- The before/after table shows H5 "think before windows" and "think before first observe" as 0.0s; that is a labeling artifact of the pick executor's DECIDE intervals, not a real zero.

## Run dirs and summaries

- /tmp/speed-h5/h5-base/summary.md (baseline, 14531 bytes + analyzer output)
- /tmp/speed-h5/h5-pick/summary.md (H5, 14895 bytes + analyzer output)
- /tmp/speed-h5/h5-before-after.md (before/after table, 3660 bytes)
- /tmp/speed-h5/h5-pick/h5.log (23 H5 CLI calls, images=1 every time)
- Briefs: improvements/live-h5-20261120/brief-h5-base.md, brief-h5-pick.md (adapted from the branch's h5-executor-brief.md)
- Wrapper timed.py md5 82176e2a4b84691a1584ed68ce82953f, analyze.py md5 39170ad8dcfd90016806f87ab50ee9df (same as triple A/B wrapper).

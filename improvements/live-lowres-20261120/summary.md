# Task 1 lowres-obs A/B: WIN (lowres-obs 9397a37, 2026-11-20)

- Branch: lowres-obs, HEAD 9397a37ea386a1d424ca218e1ec6c985f639537f. Worktree /home/james/computer-use-wayland-lowres (HEAD verified). Main checkout detached at 9397a37 for both arms; relay restarted once (MainPID 1338738, clean env, started_git_head 9397a37); broker idle at each arm start.
- Suite gate CITED, not rerun: 1345 tests, 7 failures, 0 errors, 2 skipped, zero new failures (branch doc, live-test-log line 4199 on origin/lowres-obs; HEAD matches 9397a37).
- What it is: `observe --low-res` caps routine framing observes at 640 px wide; observe()/observe_screen() take low_res=False; effective width min(max_width, 640), recorded in meta as low_res + effective max_width. Verify observes and small-target grounding stay at 960 default. Default max_width=960 everywhere, so a 1920x1200 screen already arrives as 960x600; 640x400 is 44 percent of the pixels of the real 960x600 default.
- Arms: baseline (full-res 960, no --low-res) first, then low (framing observes --low-res, verify observes full 960). Same 4 held-out tasks both arms, P1-P4 in order, stock finish, floor probe each arm. Luna 6 Max executors, kitty lr-base-exec (codex PID 1340402, EXIT:0) and lr-low-exec (codex PID 1357220, EXIT:0).

## Mechanism proven live (scripted probe, zero model calls, session lr-smoke)

- Observe --screen eDP-2 --max-width 960 --low-res: image 640x400, max_width 640, low_res true, 205187 bytes.
- Same observe without --low-res: 960x600, low_res false, 364242 bytes.
- Observation JSONs verified: 944627e7c0b9.json low_res True, 3552fe3c63a3.json low_res False.

## Results (wall = session start submit to verified end state)

| Task | Baseline wall | Low wall | Delta | Baseline think | Low think |
| --- | --- | --- | --- | --- | --- |
| P1 C-03 (df free space, 12G) | 174.033s | 94.238s | -79.795s | 300.6s | 219.4s |
| P2 E-04 (144/150, 96.0) | 45.532s | 42.013s | -3.519s | 117.1s | 60.9s |
| P3 B-01 (4 dirs) | 41.465s | 32.312s | -9.153s | 67.5s | 54.2s |
| P4 A-01 (3 lines) | 43.314s | 38.892s | -4.422s | 159.9s | 118.2s |
| Total P1-P4 | 304.344s | 207.455s | -96.889s (-31.8%) | 645.1s | 452.7s |
| Floor probe (to final observe) | 54.655s | 57.561s | +2.906s | 76.9s | 77.7s |

- Success: 4/4 both arms. Misclicks: 0 both arms. Misreads: 2 both arms, identical in kind (OCR-level only, both caught by visual check before reporting: P1 OCR read G as 6; P4 English Tesseract dropped Vietnamese diacritics). Refusals 0, session deaths 0, stale refusals 0, both arms.
- Per-observe evidence (low arm): framing observes low_res=true, max_width=640, image 640x402, 255-265KB each; verify observes low_res=false, max_width=960, image 924x581, 448-467KB each. Baseline window observes 924x581, 447-467KB each; floor screen 960x600, 555399 bytes.
- No 640 px framing image was ever too coarse to ground a control or read needed text (executor's explicit statement, all 4 tasks + floor).
- Input tokens NOT measurable in either arm (no Codex usage record in the wrapper records; both executors report none found). The token-saving claim rests on image bytes and wall, not direct token counts.
- Think totals include finish deliberation after verify (baseline P1 finish think 230.7s, low P1 ~127s), so think comparisons are noisy; the verified-result wall is the fair comparison.
- Grand totals (analyze.py): baseline service 6.328s, gap 726.134s; low service 6.367s, gap 534.524s. Broker service is ~1-2 percent of span in both arms; the delta is think.

## Verdict: WIN

Lower wall (-31.8 percent) with no rise in misclicks (0=0) or misreads (2=2, same OCR artifacts). Caveat: n=1 per arm and think noise is large (baseline P1 174s vs triple A/B 2a P1 72.6s shows the baseline executor thought slowly); the -96.9s magnitude is noise-inflated, but all four tasks point the same direction and the mechanism (44 percent pixels on framing images) is confirmed live.

## Run dirs and summaries

- /tmp/live-lowres-20261120/lr-base/summary.md (baseline, 226 lines + analyzer output)
- /tmp/live-lowres-20261120/lr-low/summary.md (low, 14939 bytes + analyzer output)
- /tmp/live-lowres-20261120/smoke/ (scripted --low-res mechanism probe, records.jsonl)
- Briefs: improvements/live-lowres-20261120/brief-lr-base.md, brief-lr-low.md
- Wrapper timed.py md5 82176e2a4b84691a1584ed68ce82953f, analyze.py md5 39170ad8dcfd90016806f87ab50ee9df (same as triple A/B wrapper).

## Notes

- Setup: codex sandbox rejected the brief's broad `rm -rf` cleanup line in the baseline arm; the executor adapted with exact-path Python cleanup (same as co2r). Coordinator removed leftovers before the low arm.
- Clock note: laptop and VM clocks agree exactly (checked 06:56:38 +07 on both). The prior worker's 07:00 finish entry above postdates real time by ~10 min; entries from 06:50 onward use the verified clock.

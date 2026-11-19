# Live A/B: action-grouping, change-only observation, H6 prefetch

Date: 2026-11-19 22:15 to 2026-11-20 00:41 +07. Worker: live-measure (Luna 6 Max).
Owner: Pham Tuan. Repo: github.com/phamTuan207/computer-use-wayland.
Method: sequential A/B, broker single-owner, same 4 held-out tasks P1 C-03, P2 E-04,
P3 B-01, P4 A-01, same timed.py wrapper (copied from det-finish baseline, md5 verified),
fresh broker session per task, stock finish. Headline: loop wall (session start submit
to verified end state). Full entries in improvements/live-test-log.md.

## Verdicts (all three INCONCLUSIVE, for different reasons)

| Method | Branch / HEAD | Suite gate | Loop wall vs baseline | Verdict |
| --- | --- | --- | --- | --- |
| Action-grouping | action-grouping ab5011a | 1348 tests, 7F/0E/2S, failset identical | 260.485 vs 206.113 (+54.4s, +26.4%) | INCONCLUSIVE, mechanism unexercised |
| Change-only obs | change-only-obs 6995a8c | 1352 tests, 7F/0E/2S, failset identical | 57.567 vs 172.734 (-115.2s, -66.7%) | INCONCLUSIVE, mechanism unexercised; delta is the code-exec path |
| H6 prefetch | harness-prefetch 56f5af4 | 1355 tests, 7F/0E/2S, failset identical | 264.255 vs 261.231 (+3.0s, +1.2%) | INCONCLUSIVE on wall; mechanism confirmed working |

No method earns a WIN: no WIN without (1) full suite green, (2) live A/B P1-P4,
(3) complete logging. All three passed (1) and (2) and (3), but in each case the
A/B did not measure the mechanism itself. Details below.

## Baseline variance (why small deltas mean nothing)

Three baselines on the identical full-observe code path: 206.113s (1a, 8727135),
172.734s (2a, 6995a8c), 261.231s (3a, 56f5af4). Spread 88.5s. Single-run wall
deltas under about 20 percent are within run-to-run noise (think gaps dominate:
service totals are 6-8s per arm, gaps are 490-670s).

## 1. Action-grouping (ab5011a, strict policy default)

- Baseline 1a (8727135, relay MainPID 899410): P1 71.948, P2 44.546, P3 43.365,
  P4 46.254; total 206.113s. Spans total 547.824s. Service 6.330s. 4/4 SUCCESS.
  Groups all [1]. 0 refusals, 0 deaths. Floor 126.332s (polluted by a 30s
  executor clarification sleep; not a clean control).
- Method 1b (ab5011a): P1 80.332, P2 32.859, P3 50.809, P4 96.485; total
  260.485s. Spans total 458.641s. Service 7.652s. 4/4 SUCCESS. Groups:
  P1 [1], P2 [1], P3 [1, 1], P4 [1, 1]. Validation rejections: ZERO.
  0 misclicks, 0 refusals, 0 deaths. Floor clean 58.748s.
- Finding: no task combined multiple terminal commands into one act request
  (executor summary says so verbatim). Every group was size 1, strict validation
  never fired. P4 wall is executor noise (local Python quoting error before
  submission, 52.1s think on the retry). P1-P4 terminal tasks cannot discriminate
  grouping. A real grouping test needs tasks with genuinely groupable actions
  (multi-step GUI sequences, e.g. type-then-click chains that the strict policy
  allows).

## 2. Change-only observation (6995a8c, observe_change_only via code-exec)

- Baseline 2a (6995a8c, full observe, clean env): P1 72.646, P2 31.873,
  P3 31.823, P4 36.392; total 172.734s. Spans total 457.124s. Service 6.540s.
  4/4 SUCCESS. Groups all [1]. 0 refusals, 0 deaths. Floor 92.754s.
- Method 2b (6995a8c, CU_CODE_EXEC=1, code-exec programs): P1 16.585,
  P2 9.230, P3 8.832, P4 22.920; total 57.567s. 4/4 SUCCESS. One code-exec
  request per task (4 API calls, in-program 709/803/1075/1334ms).
- Modes: all 8 observes mode FULL. First observes 96/96 tiles, fraction 1.000.
  Verify observes 78-83/96 tiles, fraction 0.812-0.865, all above the 0.35
  full-frame threshold. Zero diff modes, zero none modes, zero missed-change
  incidents. Image bytes per observe about 447-458KB, same as baseline.
- Finding 1: the mechanism never fired. Every post-act frame changed over 80
  percent of tiles (terminal repaint), so the conservative fallback correctly
  sent full frames every time.
- Finding 2 (code review, confirmed live): the diff crop and thumbnail are
  PIL objects in memory and are NOT returned as viewable files by the code-exec
  envelope (only JSON-able variables survive). The executor verified from full
  frames and claimed no token saving. The token-saving claim is untestable
  through this harness path as built.
- Finding 3: the -115.2s wall delta is the bundled code-exec path effect
  (1 model call per task vs 5, already proven by A1), NOT a change-only effect.
  A clean change-only comparison needs code-exec + full observe vs code-exec +
  change-only, which this A/B did not run.
- Discriminating test: a mostly-static screen with a small localized change
  (changed fraction under 0.35) so mode diff actually fires.

## 3. H6 prefetch (56f5af4, desktop pre-capture)

- Baseline 3a (56f5af4, CU_PRECAPTURE=0): P1 112.962, P2 49.418, P3 44.844,
  P4 54.006; total 261.231s. Spans total 486.675s. Capture_ms (prefetched=false
  on all 11 observes): 40-69ms, sum 559.240ms, mean about 50.8ms, matching the
  unit fresh-capture metric 50.3ms. 4/4 SUCCESS. 0 refusals, 0 deaths.
  Floor 73.162s.
- Method 3b (56f5af4, CU_PRECAPTURE=1): P1 65.961, P2 99.896, P3 47.658,
  P4 50.740; total 264.255s. Spans total 490.885s. Service 6.144s. 4/4 SUCCESS.
- Mechanism WORKS live: all 4 verify observes prefetched=true with
  capture_ms=0.0 (frame ages 504/300/212/340ms; floor final 59.9ms, 0.0ms).
  Initial/act observes prefetched=false, capture 45-59ms. Total capture saving
  is about 200ms across the arm.
- Wall effect is nil because capture is about 50ms of a 50s task (0.1 percent).
  The expected saving (0.5-0.7s per task) is below the noise floor.
- Stale-frame watch: P1 act used an observation 41.3s old at submit (executor
  think gap, NOT prefetch age; the prefetched frame was 504ms old, within the
  1000ms design limit). No misclick. P2 refreshed a 77.3s-old initial observation
  before acting (889ms prefetch age at submit, within limit). Zero stale-frame
  misclicks, 0 refusals, 0 deaths. Page prefetch untested by construction
  (no browser task in P1-P4).

## Suite gates (Phan Tuan directive 22:18, full suite per branch)

Reference clean baseline: 1339 tests, 7 failures, 0 errors, 2 skipped
(/tmp/changeobs-before-failsets.txt, 7 known pre-existing failures).
- action-grouping ab5011a: Ran 1348 tests in 102.257s, 7F/0E/2S, FAIL set
  identical to baseline. Zero new failures. PASS.
- change-only-obs 6995a8c: Ran 1352 tests in 103.008s, 7F/0E/2S, FAIL set
  identical. Zero new failures. PASS.
- harness-prefetch 56f5af4: Ran 1355 tests in 102.484s, 7F/0E/2S, FAIL set
  identical. Zero new failures. PASS.
All suites ran in the branch worktrees with the 18 gitignored native files
present (verified in each worktree before the run).

## Run records

- Run dirs on the laptop: /tmp/live-ab-20261119/{ag-baseline, ag-method,
  co-baseline, co-method, pf-baseline, pf-method} (brief.md, timed.py,
  analyze.py, records.jsonl, decisions.log, sleeps.log, summary.md, codex.log).
  Suite logs: /tmp/live-ab-20261119/{ag-method, co, pf}-suite.log plus
  *-failsets.txt diffs vs /tmp/changeobs-before-failsets.txt.
- Briefs + generator: ~/workspace/omarchy-tasks/cu-fix-20261114/improvements/
  live-ab-20261119/ (VM campaign dir).
- Relay restarts (all verified started_git_head + idle before the arm):
  1a 22:13:16 MainPID 899410 (8727135, clean); 1b 22:42 (ab5011a, clean);
  2a 23:11 (6995a8c, clean); 2b 23:30 MainPID 963918 (6995a8c, CU_CODE_EXEC=1);
  3a 23:54 MainPID 983495 (56f5af4, CU_PRECAPTURE=0); 3b 00:19 MainPID 999921
  (56f5af4, CU_PRECAPTURE=1); final clean restart 00:41:53 MainPID 1039165
  (56f5af4, clean env, idle).
- P4 files byte-verified exact 3 lines by the coordinator after every arm.
- Final state: main checkout detached at 56f5af4, relay clean env, broker idle,
  desktop clean (herdrdrop + Zen Pill fixture only). Main stays FROZEN.
- Note: during arm 3b an unrelated codex process ran on the laptop (PID 1019804
  00:33, gpt-5.6-luna, "explain why the sky appears blue"); it held no broker
  session and did not touch the arms. The main checkout also carries an
  unrelated untracked file improvements/latency-probe-20261120-results.csv from
  another worker; left untouched.

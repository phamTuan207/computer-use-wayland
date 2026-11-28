# Pick 1 P3/P4 re-measure with the NEW template programs (Track 2, Phase B, 19/11)

- Repo: `~/computer-use-wayland`, branch `speed-swarm`, HEAD `2aa74ff` (P3/P4 fix merged). No repo edits, no commits. `git status` clean at end. Both stashes untouched (stash@{0} rust-rewrite-eval, stash@{1} Phase-B pre-merge).
- Run dir: `/tmp/speed-profile-20261118/pick1-p34remeasure/` (fresh). `records.jsonl` 21 lines, parses OK. `timed.py` and smoke envelope copied from `/tmp/speed-profile-20261118/pick1/` (the rerun dir, not overwritten). `analyze-p34.py` in the run dir reproduces the numbers below.
- Programs copied from `improvements/pick1-program-template.md` (P3/P4 only), shape `windows() -> observe() -> act() -> observe() -> assert`. One adaptation: the window-title lookup uses `speed-p1p34-term`, the unique kitty title for this run (template text says `speed-pick1-term`; the title must match the actual terminal). Command strings and asserts are byte-identical to the template. P4 runtime repr verified before the run against the template expected repr (three literal backslash-n, one trailing real newline).
- Terminal: kitty `speed-p1p34-term`, PID 915840, closed by PID at end.
- Relay: flag ON arm used `pick1.conf` only (`Environment=CU_CODE_EXEC=1`), restarted, verified `active`, `idle`, `started_git_head 2aa74ff`. Smoke test passed `ok:true` (windows() returned 3 windows incl. the test terminal, `api_calls: 1`, elapsed 1.738 ms). After the arm: `pick1.conf` removed, `.d` dir removed, relay restarted to clean env, verified `active`, `idle`, `started_git_head 2aa74ff`, no drop-in left.
- Verdict: PROVISIONAL (non-Astra, Astra 6 out of credit).
- Think-time method (same as the rerun): sum of gaps between each DECIDE timestamp and the previous timed result (ready_wall after start, result_wall after each request). Finish-confirmation think excluded. Model calls count timed requests + finish; start and status polls excluded.

## Pick 1 arm, P3/P4: 2/2 SUCCESS (each on retry)

| Task | End state (verify image, read visually) | Wall excl. dwell (s) | Wall strict (s) | Think excl. dwell (s) | Think strict (s) | In-program retry (ms) | Broker service (s) | Requests | Images / bytes | Refusals | Misclicks / session deaths | Model calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P3 B-01 | 4 dirs listed by `find` (`hoc-ky-2`, `dsa`, `ktvm`, `oop`) | 20.72 | 295.22 | 17.99 | 292.50 | 1043.9 | 1.81 | 3 | 4 / 3,622,926 | 1 transient (see below) | 0 / 0 | 4 |
| P4 A-01 | exact 3 Vietnamese lines via `cat` | 20.58 | 98.62 | 17.74 | 95.78 | 1308.0 | 1.96 | 2 | 3 / 2,786,784 | 1 transient (see below) | 0 / 0 | 3 |

- Attempt 1 of each task failed identically (see below). Retry used the IDENTICAL program, no edits. Dwell is the time I spent diagnosing the attempt-1 failure before retrying (P3 274.51 s, P4 78.04 s). "Excl. dwell" is the strict wall/think minus that gap, i.e. what the task time would have been with an immediate retry. Both figures are reported; the comparison below uses excl. dwell.
- P4 file byte check: `/tmp/y-tuong.txt`, 128 bytes, exactly the 3 brief lines plus exactly one trailing newline, sha256 `a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170`. (Terminal echo of the typed command looks mangled mid-typing, the same rapid-typing echo artifact the baseline showed; the file output is byte-exact.)

## Before/after deltas (Pick 1 arm vs clean flag-OFF baseline from the rerun)

| Task | Baseline wall | Pick1 wall | Delta wall | Baseline think | Pick1 think | Delta think | Model calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| P3 | 27.67 | 20.72 | -6.95 (-25%) | 25.43 | 17.99 | -7.44 (-29%) | 5 -> 4 |
| P4 | 45.68 | 20.58 | -25.10 (-55%) | 43.21 | 17.74 | -25.47 (-59%) | 5 -> 3 |
| Mean P3-P4 | 36.68 | 20.65 | -16.03 (-44%) | 34.32 | 17.87 | -16.46 (-48%) | 5 -> 3.5 |

## Pick 1 overall with the rerun P1/P2 (4/4 SUCCESS)

- P1 18.89 / 17.38, P2 10.18 / 8.59, P3 20.72 / 17.99, P4 20.58 / 17.74 (wall / think, excl. dwell for P3/P4).
- Mean P1-P4 wall: baseline 37.54 -> Pick1 17.59 (-53%). Mean think: baseline 35.41 -> Pick1 15.43 (-56%). Model calls 5 -> 2-4 per task.

## Why attempt 1 failed in both tasks (verbatim error, same transient)

Attempt 1 (both tasks):
`{"ok": false, "error": "assert failed: act failed", "error_type": "assert_failed"}` (api_calls 4, in-program 482.5 ms P3 / 517.7 ms P4). The act itself returned `ok:false`, so nothing was typed (`/tmp/hoc-ky-2` and `/tmp/y-tuong.txt` did not exist after attempt 1).

Root cause, proven from broker diagnostics, not guessed: the act was refused at the `desktop_act` preflight with `screen changed` (`diagnostics-*.jsonl`, event `preflight_refused`, active window correct `0x55fafeaf73c0`). The program observation image vs the preflight fresh image differ by global mean 3.56 (threshold 3.0): the observation is brighter (mean 57.4) than the fresh image (54.6), a whole-image shift inside ~300 ms. The screen is pixel-stable before and after (mutual image diffs 0.001-0.004 over 50 s). It hit the FIRST act of each fresh session and never the retry (P3 retry act: `target_was_focused: true`, `completed: 1`). The template programs are not the cause: the identical program passed on retry, and the two fix-report root causes are both confirmed fixed live (P3 asserts pass with the fresh post-act observe; P4 file is byte-exact). This is a harness flake in the observe-to-act preflight window, worth a follow-up: a first-act re-observe-and-retry inside `act()` (or in the program) would have absorbed it with no model round trip.

## Cleanup and final state

- All broker sessions finished cleanly (smoke, pick1-p3, pick1-p4). Final broker status: `finished`, driver stopped, guardian clean, cancelled false, head `2aa74ff`. No `cu.py session` processes left.
- Relay restored to clean env: `active`, `idle`, `started_git_head 2aa74ff`, no drop-in file left.
- Test kitty terminal closed by PID 915840. Final `hyprctl clients`: only `omarchy: Jarvis` and `Zen Browser` (untouched).
- Test artifacts removed: `/tmp/hoc-ky-2`, `/tmp/y-tuong.txt` deleted after the run so the next worker starts clean.
- Track 1 restore NOT done (steps 4-5 skipped per task; coordinator does it in Phase D). Stashes untouched.
- Timeline (+07): relay flag ON 06:06, smoke ok 06:06:34, P3 attempt 1 error 06:07:32, P3 diag 06:08:22, P3 retry SUCCESS 06:12:07, P3 finish 06:13:21, P4 attempt 1 error 06:14:00, P4 retry SUCCESS 06:15:19, P4 finish 06:16:02, relay clean + desktop clean ~06:17.

# H2 JPEG q90 live A/B (2026-11-20)

Owner: Pham Tuan. Branch harness-jpeg-q90, HEAD 8de3601 (worktree /home/james/computer-use-wayland-jpegq90). Baseline: true baseline 8727135 (not current 56f5af4, which carries H6 prefetch + precapture code, cu.py +268/-33). Each arm: checkout detached + relay restart, fresh sessions, P1-P4 + T1-T3. Run dirs /tmp/speed-jpegq90-20261120/h2-baseline and h2-method.

## Verdict: WIN on bytes + encode with accuracy parity; wall not resolvable at n=1

| Task | Baseline wall | Method wall | Baseline bytes | Method bytes | Baseline encode avg | Method encode avg |
|---|---:|---:|---:|---:|---:|---:|
| P1 (df) | 136.341s | 73.937s | 900,563 | 151,175 | 20.430ms | 1.675ms |
| P2 (96%) | 40.811s | 81.380s | 900,833 | 157,093 | 20.319ms | 1.619ms |
| P3 (mkdir) | 52.706s | 53.172s | 1,357,208 | 242,895 | 20.327ms | 1.629ms |
| P4 (y-tuong) | 96.598s | 102.869s | 1,867,941 | 404,265 | 20.458ms | 1.922ms |
| T1-T3 (small targets) | 291.257s | 282.219s | 573,543 | 316,954 | 7.751ms | 1.037ms |
| Total | 617.713s | 593.577s | 5,600,088 | 1,272,382 | 17.021ms | 1.554ms |

Totals: wall -24.136s, think -60.160s (481.695 to 421.535), image bytes -4,327,706 (4.40x smaller), encode 17.021 to 1.554ms per observe (10.95x faster).

## Accuracy: identical in both arms

- Grounding hit rate: 3/3 baseline, 3/3 method. Same targets and points: T1 Zen new-tab plus (238,983), T2 Zen back arrow (172,18), T3 Zen reload button (238,18, baseline pick). Edge-clamped 140px crops, no clicks.
- Terminal OCR exact-match vs ground truth: 2/4 both arms. P2 (96.0) and P3 (4 paths) correct in both. P1: tesseract reads "11G" as "116" in both (G units missed). P4: tesseract drops Vietnamese diacritics in both ("Y tudng 1: app nhdc udng nudc"); byte check True (128/128) in both.
- All P1-P4 task outcomes correct in both arms. Zero refusals, misclicks, or session deaths in either arm.

## Honest read

JPEG q90 delivers far more than the build's local bench suggested on live frames: 5.6-6.0x smaller on terminal tasks, 1.81x on the Zen frame, 4.40x overall, vs the local 1.15x on a single 960x600 frame. The pre-committed 2x bytes bar is met live on every task. Encode drops from about 20ms to about 1.6ms per full-frame observe. The reason is that live terminal/Zen frames compress far worse in PNG than the bench frame (transparent gradient desktop background, dense text), so JPEG wins bigger live than in the lab.

Wall time is mixed per task (P1 -62s, P2 +41s, P3 +0.5s, P4 +6s, T -9s) and the total -24s sits inside think variance at n=1 (think splits run 20-100s per task). This is consistent with the build's honest expectation of about 0.1-0.3s/task: the effect is real on the machine metrics but not resolvable on wall at n=1. No wall speedup factor is quoted. Per the standing rule (land anything measured better), JPEG q90 is a measured improvement with no regression anywhere measured.

## Incidents

- First baseline launch BLOCKED at setup: the broker reported state "finished" with stale owner metadata (not idle/null) after the H3 method arm. The executor stopped cleanly. Root cause: after an explicit finish, the broker stays "finished" until a relay restart; "finished + driver stopped + guardian clean + explicit_finish" IS the free state. Fix: coordinator restarted the relay (MainPID 1558519, idle/null at 56f5af4), preserved the blocked run dir, relaunched. The relaunch then ran cleanly. Future briefs should gate on driver/guardian, not the state string alone.
- Baseline P1 ground truth is 11G free (385G/372G/11G, 98%), down from 12G in the cascade runs: disk usage grew between runs, not a measurement error.

## Teardown

Both arms: all 5 sessions finished, driver stopped, guardian clean; test terminal closed (hl.dsp.window.close object form); /tmp/hoc-ky-2 and /tmp/y-tuong.txt removed (executors used Python shutil because their shell refused rm -rf syntax); checkout restored to 56f5af4 + relay restart + started_git_head verified 56f5af4; log stash popped with md5 match (85f99c03) in both arms; desktop clean (herdrdrop + Zen + executor kitty only); no Chromium left over.

## Open

Landing decision for JPEG q90 belongs to the parent (measured better, no regression). Step 3 design, save-dialog Part B, H1-BASE recovery remain open (not decided here).

# H3 warm-browser live A/B (2026-11-20)

Owner: Pham Tuan. Branch harness-warm-browser, HEAD 24b9c6e (worktree /home/james/computer-use-wayland-warmbrowser). Broker code unchanged by H3 (module only, not wired into browser_start); both arms ran on relay 56f5af4, MainPID 1486544, no relay restart. Run dirs /tmp/speed-warmbrowser-20261120/h3-baseline and h3-method.

## Verdict: WIN (wall lower on 3/3 tasks, no state leakage)

| Task | Baseline wall | Method wall | Delta |
|---|---:|---:|---:|
| D1 (fixture) | 120.319s (cold retry; 381.044s incl. failed first attempt) | 87.613s | -32.706s |
| R1 (httpbin form) | 393.129s | 164.533s | -228.596s |
| R2 (example.com to IANA) | 202.986s | 75.045s | -127.941s |
| Total (retry basis) | 716.434s | 327.191s | -389.243s (-54.3%) |

## Per-task numbers

Baseline (cold browser_start per task, screenshot grounding):
- D1: think 213.151s, service 5.091s, calls 18, launch think 11.465s first / 9.901s retry + service 0.286s / 0.291s, nav 13.453s, TTFI 108.743s retry, images 168,358B (8 PNG), 2 refusals / 0 misclicks / 1 session death.
- R1: think 386.602s, service 5.966s, calls 21, launch think 10.394s + service 0.289s, nav 10.990s, TTFI 138.697s, images 745,500B (17 PNG), 1 refusal (screen_changed, recovered) / 0 / 0.
- R2: think 198.866s, service 3.763s, calls 13, launch think 10.153s + service 0.285s, nav 10.604s, TTFI 173.803s, images 455,870B (8 PNG), 0 / 0 / 0.

Method (warm Chromium pid 1534643, fresh context per task):
- D1: think 85.965s, service 1.513s, calls 5, new-context 76.4/30.7/19.0ms, ensure 5.9ms, first click 74.698s, images 59,463B (3 PNG), 0/0/0.
- R1: think 160.351s, service 3.334s, calls 12, new-context 788.1/25.0/741.7ms, ensure 5.6ms, first click 57.642s, images 355,266B (10 PNG), 0/0/0.
- R2: think 72.777s, service 1.947s, calls 7, new-context 265.8/25.7/218.6ms, ensure 5.3ms, first click 64.219s, images 296,645B (5 PNG), 0/0/0.

Warm-up: ensure cold launch 209.5ms headed (Chrome 157.0.8103.38), reused false first call, warm true for every new-context. Context creation 25.0-30.7ms; navigation 19.0ms (local fixture), 218.6ms (example.com), 741.7ms (httpbin form).

## Isolation (proven live)

- Task-level: D1-SET "d1-marker" in the D1 context, D1-READ null in a fresh context on the same fixture URL.
- Module: verify-isolation {isolated: true, a_sees_marker: true, b_sees_marker: false, marker: wb-1795150212}.
- No state leakage between tasks.

## Honest read

The machine-time saving is tiny: cold browser-start service is about 0.29s, warm new-context total is 0.08-0.79s, context creation itself 25-31ms. The wall saving comes from fewer model turns: the method used 5/12/7 calls vs baseline 18/21/13, because one new-context CLI call replaces the browser-start + tabs + nav-observe + nav-act request chain, each carrying a roughly 10-20s think gap. Think totals: method 86/160/73s vs baseline 213/387/199s. This matches the harness-research thesis that the leverage is indirect via model think. n=1 per task per arm and think variance is large (baseline R1 splits up to 43s), so no precise speedup factor is quoted.

Baseline D1 note: the 381.044s total includes a failed first attempt (executor error, browser-observe without --target, session failed, cold retry passed). The fair D1 comparison uses the 120.319s cold retry.

## Teardown

Method: all 4 contexts closed (D1, D1-check, R1, R2), stop {ok: true, stopped: true, pid: 1534643}, state file {}, port 9222 silent, no Chromium processes, broker finished / driver stopped / guardian clean, relay untouched. Baseline: Chromium closed per task (Alt+F4), broker finished, driver stopped, guardian clean. Desktop: Jarvis + Zen + executor terminal only; Zen, Jarvis, music untouched.

## Open

Adopting warm-browser into browser_start is a small follow-up the build report left open; this A/B measured the module as designed. Step 3 design, save-dialog Part B, H1-BASE recovery remain open (not decided here).

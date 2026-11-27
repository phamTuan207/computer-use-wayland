# Pick 3 prototype: multi-candidate grounding with tiny-crop verification

Date: 2026-11-18 (overnight run, finished early 2026-11-19). Owner: the owner.
Repo: phamTuan207/computer-use-wayland, branch `speed-swarm`.
Status: built, tested, measured live, reported. Flag-gated, default OFF.

## What was built

`scripts/multi_candidate.py`, behind env flag `CU_MULTI_CANDIDATE=1` (default OFF).
It does not touch `scripts/cu.py`, `scripts/a11y.py`, or any other file. Pick 4 owns
`cu.py` in this tree; Pick 3 lives in its own module plus tests.

- `parse_candidates`: parses one vision reply (0-1000 scale JSON) into at most 3
  ranked candidates with confidences. Sorts by confidence, dedupes within 8 px,
  drops out-of-range points with a note. Never raises on model garbage.
- `crop_for_candidate`: a 140 px crop centred on the point, 200 px when the zoom
  gate fires (target smaller than 32 px, or confidence below 0.7). Clamped inside
  the window bounds. Context rule M34 is the caller's job: the crop is cut from
  the frame the caller passes.
- `image_to_global` and `to_window_relative`: the two frame conversions (see the
  two bugs below). `crop_observe_args` builds the broker observe envelope.
- `stamp_failed_points`: draws a red ring, cross, and index on a copy of an
  observation, for RegionFocus-style retry observations.
- `verify_crop_text`: tesseract check that a crop contains expected text.
- `MULTI_CANDIDATE_PROMPT`: executor text asking for top 3 points with
  confidences in one vision call.
- CLI: `ground` (reply in, crop rects out), `stamp`, `verify`, `prompt`.
  `ground` is disabled unless the flag is set.

`tests/test_multi_candidate.py`: 33 tests, all passing.

## Commits pushed (origin speed-swarm)

- `0c58e0d`: module plus 30 tests, first version.
- `f55aded`: crop coordinates are window-relative for `cu.py` observe (bug 1).
- `ec6912a`: parse returns image-frame pixels, add the origin step (bug 2).

Verified with `git ls-remote`: HEAD is `ec6912a8909d3cba8db30e1b7937cf24a677dbf7`.

## Two bugs the measurement caught

Both were found by running the real pipeline, not by reading code.

1. Window-relative crops. `cu.py` observe `--crop` takes offsets from the window
   origin (it adds the origin itself). My first version fed it global pixels, so
   the crop landed at the wrong corner. Fix: `to_window_relative`, plus a
   `crop_window` field in the CLI output. Test added.
2. Frame confusion. `parse_candidates` treated 0-1000 fractions as global pixels.
   For a window observation the shown frame IS the window, so the parsed point is
   window-relative; using it as global double-counts the window origin (the first
   x-p1 crop landed at the window top-left instead of the bottom-left prompt).
   Fix: parse returns image-frame pixels, `image_to_global` adds the frame origin
   once, `ground` takes `--origin`. Regression test covers the exact prompt case
   (global 2561,2084; crop 2509,1950,140,140; window-relative 0,441,140,140).

## Local grounder gate (done first, per plan)

| Candidate | Result | VRAM | Per-call latency |
|---|---|---|---|
| Ferret-UI Lite 3B | Weights were never released (paper review confirms). Cannot load at all. | n/a | n/a |
| UI-TARS-1.5-2B | Does not exist. 1.5 is 7B only (`ByteDance-Seed/UI-TARS-1.5-7B`, about 15 GB). | n/a | n/a |
| UI-TARS-2B-SFT (1.0, substituted, reported as such) | Loads 4-bit on the laptop RTX 4050 6GB. Load 16.79 s / 13.87 s. | 5766 of 6141 MiB used after load, 88 MiB free, alongside voxtype (1552 MiB) and ComfyUI (1800 MiB), which were never touched | About 2.8 s steady state (first call 4.16 s, then 2.80, 2.65, 2.82, 2.81, 2.82) |

Accuracy of the 2B grounder on fair targets (all present in the frame): 2 of 3.
Share button correct, Zen new-tab plus correct, PDF page number missed by about
50 px. Verdict: a local 2B grounder loads and runs, but fits with only 88 MiB to
spare next to the user's running services and costs about 2.8 s a call. Pick 3 is
therefore built on the model-call path (top 3 from the Luna vision call), not on
a local grounder. No local grounder is faked. Gate scripts and logs are on the
laptop at `/tmp/pick3-gate/` (probe scripts, gate logs, screen.png; the 9.2 GB
model snapshot and 147 MB packages were removed at cleanup).

## Measurement method

Same 4 held-out tasks as the profile (P1 C-03 df, P2 E-04 python percent,
P3 B-01 mkdir plus find, P4 A-01 printf 3 Vietnamese lines plus cat), same kitty
terminal (`speed-profile-term`), same timed.py wrapper, fresh broker session and
fresh lease per task, records in `/tmp/speed-profile-20261118/pick3-20261118/`
(`records.jsonl`, `decisions.log`, `pick3-attempts.jsonl`, `pick3-ab.jsonl`,
`pick3-ab-results.jsonl`). Baseline arm labels `d-p1` to `d-p4` (flag OFF),
Pick 3 arm labels `x-p1` to `x-p4` (flag ON, one crop verify of the prompt line
before each act, act grounded on the crop observation). Think gaps are the
executor gaps between broker calls and include the VM-to-laptop hop (about
1.3 s per call, multiplexed SSH) and my image-view time; both arms use the
identical path, so arm deltas are valid. Broker service is machine-measured
and directly comparable.

Full offline suite: 33/33 Pick 3 tests pass. Whole suite in the dirty shared
tree: 1198 tests, 16 failures, 68 errors. Clean baseline worktree at `9183568`
(no Pick 3 files): 1093 tests, 9 failures, 68 errors (9 are the 5 allowed
DoctorCliTests plus 4 from the missing native `wtype` helper on the VM). The
extra 7 in the dirty run are 3 Pick 3 CLI tests from a mid-run file wipe by
another worker's `git clean` (proven: "No module named scripts.multi_candidate"
after the run), 1 Pick 2 test, and 3 chromium CLI tests. Conclusion: Pick 3
adds zero failures.

## Before/after, 4 held-out tasks

Broker service per request (machine numbers, non-poll requests):

| Request | n | Mean | Min | Max |
|---|---|---|---|---|
| windows | 12 | 0.116 s | 0.112 | 0.120 |
| full observe | 14 | 0.179 s | 0.146 | 0.230 |
| crop observe (140 or 200 px) | 12 | 0.126 s | 0.118 | 0.145 |
| act | 12 | 0.461 s | 0.059 | 1.019 |
| start ready | 10 | 0.911 s | 0.869 | 1.122 |

A crop costs about the same as a full observe in broker service (0.126 vs
0.179 s) while carrying 2 to 8 KB of image instead of about 460 KB.

Clean per-task wall (first request to finish, start polls excluded):

| Task | Baseline wall | Baseline service | Pick 3 wall | Pick 3 service | Pick 3 crops |
|---|---|---|---|---|---|
| P1 | 31.72 s | 0.79 s | 149.45 s | 0.89 s | 1 |
| P2 | 18.59 s | 0.91 s | 51.09 s | 0.97 s | 1 |
| P3 | 21.44 s | 1.18 s | 40.85 s | 1.28 s | 1 |
| P4 | 58.79 s | 1.46 s | 240.17 s | 2.19 s | 2 |
| Mean | 32.64 s | 1.09 s | 120.39 s | 1.33 s | 1.25 |

Read the walls honestly. The baseline mean is inflated by d-p4 (58.79 s, of
which 18 s is my slow Vietnamese-text preparation, not task work). The Pick 3
mean is inflated by one-off diagnosis work inside the runs: x-p1 (149.45 s)
includes finding and fixing the frame-confusion bug (commit `ec6912a`) mid-run,
and x-p4 (240.17 s) includes the screen-changed refusal and the slide anomaly
investigation below. The clean Pick 3 pair (x-p2, x-p3: 51.09, 40.85 s, mean
46.0 s) versus the clean baseline pair (d-p2, d-p3: 18.59, 21.44 s, mean
20.0 s) is the fair comparison. Broker service is nearly identical (x-p2 0.97
vs d-p2 0.91; x-p3 1.28 vs d-p3 1.18). The extra Pick 3 wall is one extra crop
observe (0.13 s broker) plus one extra vision turn of my viewing time
(about 10 to 15 s per task in this harness: scp plus image read).

Grounding accuracy on the 4 tasks: 8 of 8 tasks succeeded in both arms, 0
misclicks in either arm (type actions into a focused terminal cannot misclick),
0 session deaths in the 8 clean runs. One refusal: x-p4 attempt 1, screen
changed, recovered (see incidents). Every Pick 3 crop verified its candidate
on the first try (5 of 5 attempts, 1 crop each).

Conclusion on the 4 tasks: on terminal tasks with no small target and nothing
to misclick, Pick 3 buys nothing and costs one extra crop plus one extra
vision turn. That is the expected result. The value, if any, is on small
targets, which is what the A/B below measures.

## Small-target grounding A/B (the decisive test)

One broker session, one Zen window frame (Claude page with a macro slide PDF),
3 small targets (16 to 20 px true size), plan pre-committed to
`pick3-ab.jsonl` before any crop, judgement rule fixed in advance: a crop
verifies a candidate only if the target control is visible in the crop AND the
predicted point falls on that control. No clicks anywhere, read-only.

| Target | Baseline (1 candidate) | Pick 3 (up to 3) |
|---|---|---|
| T1 new-tab plus | MISS. Point lands right of the plus glyph, in the gap before the speech icon. True plus is about 30 px left of my first guess. | HIT at candidate 3. Candidate 2 lands on the speech icon; candidate 3 lands exactly on the plus glyph. |
| T2 back arrow | HIT at candidate 1. | HIT at candidate 1, no extra crops. |
| T3 Claude input attach plus | MISS. Point lands in the empty input text area above-right of the plus. | MISS all 3. Candidate 2's crop shows no plus at all (too far right). Candidate 3 shows the plus but the point is still 85 px right of it. All three guesses were placed too far right; the true plus sits at 0-1000 x about 510, my guesses were 588, 613, 640. |

Result: baseline 1 of 3, Pick 3 2 of 3. Pick 3 recovered 1 of 2 baseline
misses, at a cost of 4 extra crop observes (about 0.49 s broker service
total). T3 shows the limit: when all three ranked guesses share the same
systematic placement error, the extra candidates do not help. The fix for
that is better first-pass placement (a bigger frame, or a zoomed overview),
not more candidates.

## Incidents found while measuring (worth more than the table)

1. A full-window observe can transiently return another window's pixels.
   The x-p4 first observe of the kitty returned a macro slide from the Zen
   window, with correct kitty metadata. Root cause, found later: Zen had grown
   taller (718 px) and overlaps the kitty's top 123 px; the tiler then pushed
   the kitty down (1509 to 1646) and shrank it (581 to 444 tall). A capture
   during a reflow can catch the overlapping window. A re-observe returns the
   correct frame. Lesson: on a live, reflowing desktop, never trust a single
   anomalous frame; re-observe before acting on it.
2. A crop-observation act can trip `screen_changed` on a stale crop. x-p4
   attempt 1 was refused after a long gap between the crop observe and the
   act. The after-image looks identical to the verified crop; pixel diff shows
   a widespread low-amplitude change (1110 of 19600 pixels differ by more than
   10 levels, no 1 to 4 px shift explains it), consistent with a focus-dim or
   compositor transient, not a content change. Recovery that worked: fresh
   windows plus observe, fresh crop, OCR-verify on the laptop (fast, about
   1 s), act immediately in the same call. The slow scp-plus-view verification
   between crop and act is what let the crop go stale. Lesson: verify crops
   fast and act promptly; the crop guard is pixel-sensitive.
3. The desktop reflows while you work. The kitty moved and resized between
   x-p4 finish and the A/B session with no input from me. Grounding must
   re-read window bounds per session, never cache them across tasks.

## Verdict

Pick 3 works as designed: one vision call, up to 3 ranked candidates, tiny
crops (140 to 200 px, 2 to 8 KB, 0.13 s broker service), click only from a
verified fresh crop, flag-gated and default OFF, safety invariants untouched.
On the 4 held-out terminal tasks it is pure overhead (about 0.13 s broker
plus one vision turn per task, no accuracy gain available). On small targets
it recovered 1 of 2 single-candidate misses (2 of 3 vs 1 of 3) for 4 extra
crops. It does not fix a systematic placement error shared by all 3 guesses.
Recommendation: keep the module and the flag; use it where the target is
small or uncertain (the zoom gate already encodes this), and keep the
observe-to-act gap short with fast on-laptop crop verification.

## Cleanup and warnings

- All 9 broker sessions finished cleanly (8 task sessions plus the A/B
  session). No session left running.
- Test windows: the `speed-profile-term` kitty is closed at cleanup; desktop
  verified with `hyprctl clients`. Zen, Zalo, Teams, Jarvis, music, the Pick 2
  `pick2-term` kitty, and other workers' VS Code windows were never touched.
- Gate leftovers removed: the 9.2 GB UI-TARS snapshot and the 147 MB package
  target under `/tmp/pick3-gate/` are deleted. Gate logs, probe scripts, and
  `screen.png` are kept.
- Root disk is at 100 percent and still shrinking: 517 MiB free at the d-p1
  verify, 512 MiB at the x-p1 verify. Pre-existing critical state, not caused
  by this work (my gate writes went to `/tmp` tmpfs, not root). Flagging it
  again because it is getting worse during the night.

## Files

- `scripts/multi_candidate.py` and `tests/test_multi_candidate.py` (repo,
  branch `speed-swarm`, HEAD `ec6912a`).
- Records: `/tmp/speed-profile-20261118/pick3-20261118/` on the laptop
  (`records.jsonl` 268 records, `decisions.log`, `pick3-attempts.jsonl`,
  `pick3-ab.jsonl`, `pick3-ab-results.jsonl`, `pick3-analyze.py`,
  `pick3-analyze2.py`).
- This report: `improvements/speed-proto-pick3.md`.

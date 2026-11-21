# S6. Chronotope: One Step, Four Clocks

- Class: (b) slow first action and think-observe loop costs
- URL: https://zhanwenchen-chronotope-report.static.hf.space/index.html
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

Ran the same seeded GUI tasks under Paused (response stays valid), Replay (same frames, response stays valid), and Live (response can expire). Recorded four event times per decision: E (environment change), O (observation available), D (decision irrevocable), A (action received by app). Proposed late binding: leave one action argument (click coordinate or typed value) unfinished during deliberation and fill it from the newest frame immediately before D.

## Evidence shown

A 27B VLM scores 100/100 Paused and Replay but 0/100 Live at every window shorter than its roughly 5s deliberation. On a drifting target, filling the coordinate from the newest frame raises success from 0/100 to 100/100 with no extra model call; re-running the model also succeeds after a one-time jump but fails under continuous drift. A drifting balloon at 16 px/s: the frozen click lands 84 px away, the late-bound click 4 px away. Audit of 18 benchmarks found none that record observation, commitment, and receipt times while varying only whether the response can expire.

## Applicability verdict: APPLIES

This is the single most actionable paper for our first-action problem. Late binding is exactly our fix shape: decide WHAT to click from the old observation, but fill WHERE from a fresh DOM rect read milliseconds before dispatch. It costs no extra model call and their experiment shows it fixes continuous drift, which re-decision does not. It also gives us the measurement discipline we lack: record E/O/D/A timestamps per step and score at receipt (A), never at commitment (D). Our log should adopt their four clocks. Caveat: their tasks are synthetic (balloon, notification, trading), not real desktop apps, so the 0/100 to 100/100 swing is a clean-room number; on our real Zen pages the gain will be smaller but the mechanism is the same.

# Structure adoption, 2026-11-21 18:16 +07

Owner approved Worker W's redesign proposal (commit fb00973) and ordered: follow it as Lauren Tan advises.

## Adopted immediately (no build)
1. **Evidence contract (B P3).** No report counts as done without runnable evidence: exact test command + output/log, commit hash, timed run log, end-state screenshot/video for machine tasks. Coordinator checks for the evidence attachment BEFORE reading the report; a bare "done" is returned unread. The generator never runs its own tests; only a different agent's runner evidence counts for landed changes. Small tasks are exempt from the separate-runner leg but still attach their own evidence.
2. **Two-lane spawn cap (B P5).** Default two concurrent lanes, disjoint files only. The runner counts as a lane. A third lane needs all three: disjoint files, its own test slot, and a NAMED DELIVERABLE FILE. Applies to NEW spawns from adoption onward; running workers finish their current task, they are not killed to enforce the cap.
3. **Progress-based kill rules (B P6).** Kill on no progress marker for 15 min. A decision counts only if it names the next concrete step and its evidence; a heartbeat alone does not count. Kill on FIRST stall flag. No invented hard timeouts; measure p95 per task type on the next 10 tasks first.

## First step: A1 narrow pilot (Worker A1)
Batch actions per observation inside code-exec programs, deterministic short tasks only. Cases: Pick 4 fixture (frozen into repo first) + f01. Code-exec vs step-by-step, n=3 per arm, alternating, blinded checker, then one held-out realistic task by an independent runner. GO only if median wall down at least 30% AND pass rate equal or better AND recovery steps not higher. Live arms run only when the owner is away from the keyboard (prep now, run on resume order).

## Second (same week, no build)
Evidence contract + two-lane cap (above). After the pilot: DOM-first as opt-in per task type, once single-session ownership is built and tested. Then Exp1 (model-turn batching, pilot-sized, only if pilot goes GO), then Exp2 (tree-first, only if Exp1 goes GO).

## What NOT to change
Coordinator model (one coordinator, repo-mediated, no peer-to-peer). Clone channel (repo only). Generators never run their own tests. Watchdog (15-min cron; 5-min poll refinement noted, not yet applied). Quality over speed. Realistic complex tests, timed and logged. Final test plan (independent contest, run LAST). No personal info on GitHub, no em/en dashes, never ydotool, small commits push as you go, full access.

## Killed (do not revive quietly)
Coordinate cache. Register/tools/skills apparatus. Exp3 as designed. Hard timeouts 60/30/20. JSON-schema validations on handoffs. Blanket one-batch ban on clones.

## Lauren Tan rules (adopted verbatim as standard)
Done means nothing without runnable verification evidence. A repeated mistake becomes a deterministic rule (lint, test, template), never a reminder. Repeated operations become tools; repeated approaches become skills. Every time the AI errs or succeeds, ask "can this later run without me?"

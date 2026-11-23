# A4 CB-10: LIQUID flicker probe (or owner deferral) for the session-level pill, stage (a)

Status: PREPARED ONLY, NOT RUN. Prepared by worker B2-4, 2026-11-23
00:18 +07, worktree HEAD ed4fcd4. This probe needs an explicit GO
from Muse tong before any live step runs, and the choice between
the probe path and the deferral path belongs to the owner, not
to this worker. No live run, no browser work, no SSH was done
while writing this file. No em dash or en dash anywhere in this
file. No personal info.

## 0. Current status (measured from the repo, not assumed)

- Probe NOT run. No flicker probe run exists in the repo: the
  LIQUID background test never ran because the plugin was not
  loaded, so there is no evidence the original flicker was
  reproduced or fixed (final direction CB-10 row).
- No deferral recorded. No explicit owner deferral for CB-10
  exists in the repo.
- Stage (a) of A4 is therefore BLOCKED. The staged sequence is:
  (a) session-level pill first, server kept, measured, with the
  CB-10 precondition met; (b) driver-owned pill with the crash
  proof; (c) delete the server only then. Stage (a) cannot be
  judged until one of the two limbs below lands.
- This worker does NOT conclude which limb should be taken, and
  does NOT conclude that the flicker exists or does not exist.
  The final direction gate says it plainly: first establish
  whether the flicker reproduces on the current build; if it
  does not reproduce, CB-10 dissolves. Do not measure the phases
  of a phenomenon that may not exist.

## 1. What already exists (do not redo it)

- Indicator proven NOT to repaint at idle, three independent
  times: 122 one-second windows with 0 callbacks, 3 minutes
  with 0 commits, deployed binary 3 windows with 0 (zen doc
  2.2.3, worker G E2 live). E1 per-event logging is ready to
  capture any recurrence with exact times.
- The decision doc docs/decision-2-2-3-hyprglass-test-20261121.md
  (Worker X, 21/11 17:52) lists four options A/B/C/D. The owner
  chose C on 18:24 (zen doc 2.2.3, decision 18:24, memory
  1605/1608/1713): nested Hyprland, isolated.
- Y6e nested LOAD TEST PASSED 21:57 (915121d): hyprglass active
  in the nested compositor, versionCheck match, live session
  untouched. That proves the plugin LOADS nested. It does NOT
  prove the flicker reproduces, and it counted no repaints. Do
  not cite the load test as the probe.
- The A8 load-only trial and re-trial are also not the probe:
  the re-trial failed at the liquid gate (shaders pending 60s),
  and the pill retry is still pending with gate G-PILL open
  (zen doc 4.13).
- hyprglass is NOT loaded in the live compositor (only
  hyprbars), NOT in hyprland.conf. The .so survives only on
  the laptop, never in the VM worktree. The loadable build is
  the Y6e rebuild, not a backup: ~/.local/share/
  agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so,
  34,440,704 B, md5 78ac102337ca70842bf604b56c6f4c8e (Y6e
  rebuild log, commit 915121d). Backup 1
  (~/.local/share/agent-computer-use/backups/
  full-1791544423/native/hyprglass.so, 26,643,888 B, sha256
  2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5)
  is a recorded DEAD path: its ABI is dead
  (libaquamarine.so.14 and libhyprgraphics.so.4 not found),
  so do NOT load it; the hash is recorded only to identify
  the dead file. Backup 2
  (~/.local/share/agent-computer-use/backups/
  sync-20261116-230254-783160-a9a24690/trees/native/
  hyprglass.so, 30,622,520 B, sha256
  ddfff1c2f2cebb66e10b85a739beae0c7c562ccf9d78e3250647c07f8f31fa8b)
  is a different build, never compat-checked, and is not used.
  The Y6b v2 runner header still says "loads backup 1
  hyprglass"; that line is stale (Y6C5 switched the staged
  conf to the y6e conf), so the operator trusts the grep in
  step 1, not the header.

## 2. Probe path (option C, the owner's choice): what to run

Venue: a nested Hyprland compositor with hyprglass loaded,
isolated from the live session (option C). Nothing is loaded
into the live compositor. If the nested compositor cannot run
with the plugin, STOP and report: option C is infeasible, and
the owner picks A or D. Do not fall back to A (live load) or B
(login-time config plus reboot) without a fresh owner decision.

Step 1, build the nested venue. Start a nested Hyprland with
the Y6e launcher (the launcher that passed the load test),
with hyprglass loaded from the rebuilt .so (verify the .so
hash before loading; record it). Verify: hyprglass active,
version check match, live session untouched (live Zen, live
browsers, live relay all still running and unmodified).

The launcher is improvements/worker-y6e-nested-load-test.sh
(291 lines, repo copy; the laptop copy that runs is
/tmp/y6-nested/y6e-load-test.sh). Re-verify the two copies
match before running (`md5sum` the repo file and the laptop
file; they must be identical, because the load test verdict
belongs to the file that actually runs). It is LOAD ONLY: it stops
after the plugin status check and tears the nest down, with
no pill, no arms, and no liquid gate. So step 1 as a
standalone run proves the load only; the venue that stays up
for steps 2-4 is the Y6b v2 runner (step 2), not this
launcher. Before either runner, verify on the laptop which
.so the staged conf actually loads, and verify its hash:

`grep -o '/[^"]*hyprglass[^"]*\.so' /tmp/y6-nested/conf/hyprland-wayland-y6e.lua | head -1`

Expected: ~/.local/share/agent-computer-use/
worktrees/hyprglass-03a57c4/hyprglass.so. Then:

`md5sum ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so`

Expected: 78ac102337ca70842bf604b56c6f4c8e. If the grep names
a backup path, or the md5 differs, STOP: the staged conf is
not the tested y6e conf, and loading an untested .so is how
the backup-1 dead ABI broke the Y6c run. The runner's own
ldd pre-flight aborts on a dead .so, but the grep plus md5
above is the check that runs first, before any launch.
Load check with the Y6e launcher (handover re-confirmed at
run time, owner away):

`Y6_HANDOVER_CONFIRMED=1 bash /tmp/y6-nested/y6e-load-test.sh`

Expected exit 0 with LOADED (plugin listed, version
1.1.1-cu.1, versionCheck match). Then proceed to step 2;
do not treat this load check as the probe.

Step 2, load the pill. Run the indicator in the nested venue
with the pill visible (same indicator binary as the live pill,
or the deployed binary that measured 0 idle paints). Record
the pill visible in the nested venue (screenshot).

The command is the Y6b v2 nested measurement runner,
improvements/worker-y6b-run-nested-wayland-v2.sh (973 lines,
repo copy; the laptop copy that runs is
/tmp/y6-nested/run-nested-wayland.sh). The Y6c run log
verified the repo and laptop copies matched at 20:39 21/11,
so re-verify the match with `md5sum` on both files before
running: the probe verdict belongs to the file that actually
runs. It launches the nested
Hyprland, loads the plugin through its staged conf, runs the
liquid gate, starts the pill, and runs both arms (step 3).
Before running it, verify the staged conf it uses names the
same rebuilt .so as step 1:

`grep -o '/[^"]*hyprglass[^"]*\.so' /tmp/y6-nested/conf/hyprland-wayland.lua | head -1`

Expected: ~/.local/share/agent-computer-use/
worktrees/hyprglass-03a57c4/hyprglass.so, md5
78ac102337ca70842bf604b56c6f4c8e. Run it only with the owner
away and the handover re-confirmed at run time (the runner
enforces this: it refuses to run unless
Y6_HANDOVER_CONFIRMED=1):

`Y6_HANDOVER_CONFIRMED=1 bash /tmp/y6-nested/run-nested-wayland.sh`

The runner takes about 4 minutes (launch 10s, shaders up to
60s, controls 10s, pill start 45s, 2 arms 40s each, teardown
10s) with a 25-minute overall deadline. Its pill-visible
proof is its own read_pill_geom step (it fails if no pill
surface is found in the nested layers) plus the grim pill
captures it saves under /tmp/y6-nested. Precondition: the A8
re-trial failed at the liquid gate (shaders pending 60s),
and the Y6r amend requires the A1-A10 fixes plus an
independent re-review before any retry, so confirm that
re-review landed before running; a liquid-gate failure
aborts the run with NO-GO, it is not a flicker verdict.

Step 3, reproduce the flicker. Drive the nested venue through
the LIQUID animated backdrop (the condition of the original
20/11 report: flicker while the owner drives directly, calm
when Codex drives). There is NO standalone LIQUID driver
script in the repo: no file drives the pointer and switches
focus on a fixed schedule, and the owner's live input is not
repeatable, so this probe does not claim that drive. The
repeatable drive is the Y6b v2 runner's own arms (step 2
command): Arm A, static backdrop with the pill idle, 32 grim
frame pairs (any pill-region change is flicker); Arm B,
animated backdrop (mpv --loop=inf --no-audio --fullscreen,
tracked by PID, motion re-validated with two consecutive
frames that must differ), 32 grim frame pairs of the pill
region plus a backdrop corner sample. A pair where the pill
differs but the backdrop sample is identical is flicker
evidence (pill-only diff); both differing is expected motion.
The runner prints the verdict lines itself: ARM A outcome
(pill diff N/31), ARM B outcome (pill diff N/31, backdrop
diff N/31, pill-only N/31), and VERDICT: REPRODUCED,
INCONCLUSIVE, VOID, or NOT reproduced in the nest. Record
those lines verbatim. If it does not flicker after both arms,
that is a result, not a failure: CB-10 dissolves for this
build (see section 4). Note the asymmetry the runner
records: a nest negative does not exonerate the live
backdrop, so a NOT reproduced verdict dissolves CB-10 for
this build only, it does not prove the live session can never
flicker.

Step 4, count repaints per phase (CB-10 separation). With E1
per-event logging on, count indicator repaints and compositor
events separately per phase: think-time, act, observe. Never
one lumped number. Method: the v2 runner's own per-arm
counts, which are the phase separation for this probe: Arm A
(static, think-time equivalent) gives pill diff N/31 and
backdrop diff N/31; Arm B (animated, act plus observe) gives
pill diff, backdrop diff, and pill-only diff N/31 each.
Record the runner SUMMARY line verbatim
(armA_outcome, armA_diff, armB_outcome, armB_pill_diff,
armB_bg_diff, armB_pill_only). Separately, capture the E1
per-event log as the recurrence net: the nested indicator
writes [indicator-metrics] JSON lines to its stderr, so
count those lines per arm window from the runner log with
`grep -c 'indicator-metrics' <runner-log>` per arm, and
record the counts beside the grim counts. Capture
parameters: the nest output is 960x540 and the runner
captures full-output grim PNGs; the live-run capture
parameters (observe default 960, act-now 1920, JPEG q90, P6c
rule) do NOT apply to grim PNG captures in the nest, so do
not record them as the probe parameters. Record the nest
output geometry and the grim frame paths instead.

Step 5, session-level pill measurement (stage (a) itself, only
after steps 3-4 give a verdict). Only when the probe verdict
is in, run the session-level pill (acquire once per task,
server kept) and measure: acquire count per task is 1 in the
log; repaints and events counted per phase as in step 4; the
pill shows the right content and clears cleanly at task end,
with a log or a screenshot as evidence (prep log section 4.3
stage (a) pass criteria).

## 3. Deferral path (the other limb): what a deferral must contain

If the owner defers instead of probing, the deferral is
recorded in writing with all four items, or it does not count:

1. The owner's name (who deferred).
2. The date (when).
3. The scope (CB-10 flicker probe deferred; A4 stage (a) is
   judged WITHOUT the probe, on the stated basis: the
   indicator idle proof plus E1 logging as the recurrence
   net).
4. The condition that reopens it (for example: any flicker
   recurrence captured by E1 logging reopens CB-10 before
   stage (b) starts).

A deferral recorded by a worker on the owner's behalf, with no
name and no date, is not a deferral. This worker cannot write
it: only the owner can defer, and the coordinator records it.

## 4. What unlocks A4 stage (a)

Exactly one of these two, recorded by the coordinator:

- Limb 1, probe verdict: the probe ran (section 2) and the log
  records one of (i) flicker reproduces, with per-phase
  repaint counts, so the session-level pill is judged knowing
  the flicker status; or (ii) flicker does NOT reproduce on
  the current build, so CB-10 dissolves and the pill is
  judged on the idle proof alone.
- Limb 2, owner deferral: a deferral with name, date, scope,
  and reopen condition, recorded as in section 3.

Until one limb lands, stage (a) stays BLOCKED, stage (b)
cannot start, and the A4 date cannot be set. The A4 date is
the day after the stage (b) crash proof lands, which is itself
after stage (a) is measured (prep log section 4.4).

## 5. What this file does NOT do

- It does not run the probe (needs GO plus the nested venue).
- It does not choose between probe and deferral (owner's
  choice; the owner already chose C as the probe venue, but
  the GO to run it now is still missing).
- It does not judge the session-level pill (that judgment
  needs the probe verdict or the deferral first).
- It does not touch the overlay server or the pill. Per the
  step 9 log: do NOT touch the overlay server or the pill
  while stage (a) is blocked.

# A8 load-only trial procedure (Y6r A8, restated by worker C5-Y6-PAPER)
# Status: WRITTEN, NOT RUN. This lane is paper only. The trial runs after the
# fresh re-review clears the fix diff, in a nested Hyprland per option C
# (owner chose C 18:24, 21/11), never on the live session.
# No em/en dash. No personal info.

## Purpose

Prove the AMENDED fix, not the reload: staged y6e conf + positive profile
gate (A2) + G4 configerrors gate (A6) + AMEND4/AMEND5 (A5), with no pill, no
arms, no backdrop, no grim captures. The trial exercises the amended gate
code path itself. It does NOT prove the pill measurement (no arms ever ran)
and does NOT prove the liquid readiness window (O3).

## What loads

- One nested Hyprland only, as a Wayland client of the live compositor
  (parent socket /run/user/1000/wayland-1, nest runtime dir /tmp/y6-nested/run).
- The rebuilt hyprglass 1.1.1-cu.1 from
  /home/james/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so,
  via the STAGED conf /tmp/y6-nested/conf/hyprland-wayland.lua (md5
  9ccb27017ab63a9d2bce1d9651425d3b, verified before launch).
- The amended hook (/tmp/y6-nested/conf/nested-visuals-hook.lua) and optics
  (/tmp/y6-nested/conf/optics.lua), staged from the repo copies in
  improvements/y6-nested-conf/ with md5 verification.
- NOTHING loads into the live compositor. No live config change, no live
  reload, no reboot. The live session (PID 1515) is observed only.

## What is measured (all must hold; the trial FAILS otherwise)

1. Positive marker: `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55
   mask=contour namespace=computer-use-indicator` present in the marker
   FILE ($RUN_DIR/y6-profile-applied.txt, copied out at teardown to
   $NEST/y6-profile-applied-<timestamp>.txt) before the liquid gate.
   The LIVE per-instance log ($NEST_LOG) is NOT the channel for this
   signal: the A8 trial of 16:18 2026-11-22 proved the log file stops
   flushing after the dmabuf dump, so a log grep cannot observe it
   (see improvements/worker-click5-y6-a8-invest-log.md). First amended
   run must show the file or stop (Council 1 item 6).
2. Hook corroboration: `Y6-NEST-HOOK: profile applied` present in the
   marker FILE. Log lines are corroboration only; their absence from the
   logs is NOT a failure. Parse-1 `not ready` marker present is
   EXPECTED, not a failure.
3. Second signal: features.layers.enabled == true in the nested hyprglass
   status JSON (re-checked after the marker).
4. Version: hyprglass 1.1.1-cu.1, versionCheck match, on both checks.
5. G4: `nest hyprctl configerrors` output empty after profile application.
   RECORD the exact output either way, even on pass (empty).
6. AMEND4: HYPRGLASS_SKIP_VERSION_CHECK unset. AMEND5: no hyprglass load
   path in the live config chain; live plugin list before == after.
   Record the ACTUAL before-list; do NOT assume hyprbars-only. As of
   16:12 Sun 2026-11-22 live runs hyprbars + hyprglass 1.1.1-cu.1 +
   computer-use-cursor (loaded by another lane's live work after Y6r's
   22:09 21/11 hyprbars-only read; live PID 1515 unchanged, no restart;
   live config chain still load-path-free per the AMEND5 walk). The identity
   check (before == after) is what matters, not the list contents.
7. Live untouched: live PID 1515 alive, live hyprctl responds, live plugin
   list identical before/after, no stray mpv/foot/indicator processes, lock
   free after teardown, nest runtime dir removed.

## Observation items (record, do not assume)

- O1/G4 tension: if configerrors is NON-EMPTY, record the exact error text.
  If it is a parse-3 duplicate-layer() error with the marker present and
  layers.enabled true, the trial verdict is G4-NARROW-NEEDED (G4 must be
  narrowed to allow that specific error), NOT "reload path dead". Any other
  config error is a trial FAIL with the error quoted.
- O3: record the shaders field at the status read (pending vs ready) and the
  time from launch to liquid ready. Only "pending at 7 s" was observed before.
- Marker counts: do NOT count markers in saved logs as parse evidence
  (A10). The marker file is the verdict signal; do NOT count markers in saved
  logs as parse evidence (A10), and do NOT fail on their absence. The verdict
  uses the marker-file gate result only.
- ldd: the staged-conf ldd output is saved to
  improvements/y6c5-evidence/ldd-y6e-conf.txt BEFORE the trial; the trial
  re-verifies the conf md5 at launch via the runner pre-flight.

## Preconditions (all enforced by the runner; verify in writing first)

- Handover re-confirmed at run time: Y6_HANDOVER_CONFIRMED=1 only after Muse
  confirms the owner is still away. A handover is time-bound.
- Runner-quiet: no live runner process, no geckodriver, no mpv/foot running.
  Confirm in writing that no A1 arm is scheduled in this window.
- Live socket /run/user/1000/wayland-1 present; live signature unambiguous
  (exactly one); live PID single.
- Staged files verified: conf md5 9ccb2701, hook and optics md5s match the
  repo copies in improvements/y6-nested-conf/ (record both md5s in the run log).
- Live baseline re-verified immediately before launch: record the live
  plugin list and confirm with the coordinator that no live lane (F1/F2/F3)
  will load or unload plugins during the trial window. If the baseline moved
  since staging, record the new baseline; do NOT assume the Y6r baseline
  (hyprbars-only is stale since 16:12 22/11, see item 6 above).
- ldd on the conf plugin path: rc=0, zero "not found" lines, output saved.
- The amended runner file on the laptop matches the repo md5 (record it).

## Run steps

1. On the laptop, from ~/workspace/computer-use-wayland:
   `Y6_HANDOVER_CONFIRMED=1 Y6_STOP_AFTER_GATES=1 bash improvements/worker-y6b-run-nested-wayland-v2.sh`
   (Y6_STOP_AFTER_GATES=1 exits 0 after the liquid gate; teardown still runs.)
2. Watch the run log /tmp/y6-nested/run-<timestamp>.log for, in order:
   AMEND4 OK, AMEND5-BEFORE OK, plugin ABI OK, live plugin list BEFORE
   (hyprbars only), backend gate, socket discovery, hyprglass in nested
   plugin list, version 1.1.1-cu.1 versionCheck match, profile gate OK
   (applied marker + layers.enabled true + re-check), G4 OK, liquid ready.
3. Copy the run log and the nested per-instance log out before teardown
   removes the runtime dir (the runner copies the nested log itself).
4. Verify the 7 measured items above from the saved logs, quoting exact lines.

## Abort conditions (stop immediately, teardown runs, record the cause)

- Any gate FAIL (ldd, AMEND4/5, backend, plugin list, version, profile
  gate, G4, liquid 60 s timeout).
- Live plugin list changed (before != after) or live PID missing.
- Nested Hyprland dies at any point.
- Owner returns, or the handover window expires, or any human input is
  needed on the live screen.
- Overall runner deadline 25 minutes exceeded.
- On abort, the trial verdict is FAIL with the exact failing line quoted.
  A G4 fail on a parse-3 duplicate-layer error is the G4-NARROW-NEEDED
  outcome above, not a generic FAIL.

## What the trial does NOT do

- No pill launch, no pill ready wait, no geometry read, no arms, no grim
  frames, no mpv backdrop, no verdict lines. Those belong to the measurement
  retry (serial item 4), which runs only after this trial passes AND the
  re-review of the trial evidence clears it.
- No manual `nest hyprctl reload` (A7/R2). No timer, no hyprland.start
  deferral. One application path only: the automatic parse-2 path.
- No saved-log marker counting (A10).

## After the trial

- If all 7 items hold: the retry (serial item 4) may be considered, subject
  to a fresh re-review of the trial evidence.
- If any item fails: stop, record the exact failing evidence, re-review the
  fix diff again. Do not proceed to the pill measurement on a failed trial.

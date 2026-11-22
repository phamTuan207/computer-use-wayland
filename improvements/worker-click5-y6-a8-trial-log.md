# Worker C5-Y6-A8-TRIAL log: A8 load-only trial (amended v3 runner, Y6_STOP_AFTER_GATES=1)
# Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
# Task received: Sun 2026-11-22 16:17:13 +07. T+0 at 16:17.
# Wall clock Asia/Ho_Chi_Minh + elapsed time per entry. No em/en dash. No personal info.
# Scope: LOAD-ONLY TRIAL in a nested Hyprland per option C, never on the live session.
# This is NOT the pill measurement retry. The retry stays gated.

## VERDICT: FAIL

- The trial FAILS at measured item 1 (positive applied marker). Exact failing line:
  `Y6-WAYLAND: FAIL: profile not applied: Y6-NEST-OPTICS applied marker absent after 15s; see nested log tail above`
- Run: 16:18:03 to 16:18:29 +07 (26 s). Teardown ran and completed clean.
- The pill measurement retry is NOT cleared. Per the A8 trial procedure, on any
  failed item: stop, record the exact failing evidence, re-review the fix diff
  again. Do not proceed to the pill measurement on a failed trial.
- NO SELF-HEALING: this log records evidence only. No diagnosis, no fix, no
  re-run, no retry of the trial. The evidence below is handed over for re-review.

## 0. Preconditions verified before launch (T+1m, 16:18 +07)

- Runner md5 b50396bf1c68c1e047733b2a5b24f35a on BOTH copies (required md5):
  - VM repo: `md5sum improvements/worker-y6b-run-nested-wayland-v2.sh` =
    b50396bf1c68c1e047733b2a5b24f35a
  - Laptop repo copy: same md5 b50396bf1c68c1e047733b2a5b24f35a
  - VM HEAD at launch: ed09fb5 (branch todolist-push)
- Staged files on the laptop match the paper-lane record exactly:
  - /tmp/y6-nested/conf/hyprland-wayland.lua 9ccb27017ab63a9d2bce1d9651425d3b
  - /tmp/y6-nested/conf/nested-visuals-hook.lua 6dd68aeadbe7e1c9049436dc7361ee7a
  - /tmp/y6-nested/conf/optics.lua 85298d2035697710d95117355c9830ca
  - Staged files DO contain the marker prints (verified by grep after the run):
    hook line 30 `print("Y6-NEST-HOOK: profile applied")`,
    optics line 47 `print("Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator")`.
    Conf line 18: `dofile("/tmp/y6-nested/conf/nested-visuals-hook.lua")`.
- Live baseline re-verified immediately before launch (M4):
  - Live Hyprland PID 1515 alive, started Sat Nov 21 15:17:25 2026, single
    signature 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825.
  - Live plugin list (full JSON read, `hyprctl -j plugin list`):
    hyprbars 1.0, hyprglass 1.1.1-cu.1, computer-use-cursor 1.0.0.
    IDENTICAL to the paper lane 16:12 record. The baseline did NOT move again.
  - Live hyprglass status (read-only): version 1.1.1-cu.1, versionCheck match,
    active true, shaders ready, layers enabled true active true.
  - Live socket /run/user/1000/wayland-1 present.
- No live lane plugin load/unload activity in progress:
  - No hyprctl process running (`ps aux | grep -iE "hyprctl|plugin load"` empty).
  - No mpv, foot, geckodriver, or runner script processes running.
  - Known live lanes (STEP9 browser/CDP, Y13G-R3-FIX, AGENT-NATIVE-EXEC,
    Y1B-PROBE, BATCH3-CHECK) are not plugin-loading lanes as briefed.
  - The runner's own runner-quiet process check also passed at launch.
  - The live plugin list was identical before and after the run (item 6),
    which confirms no load/unload happened during the window.
- Handover: owner asleep since 06:52, coordinator authorized the run;
  launched with Y6_HANDOVER_CONFIRMED=1 per the trial procedure.
- Runner reload check: `grep -n "hyprctl reload"` on the runner returns only
  the two comment lines (39, 49). Zero non-comment hyprctl reload lines (R2).

## 1. Run record

- Launch command (laptop, fully detached, SSH dies around 30 s):
  `cd ~/workspace/computer-use-wayland && Y6_HANDOVER_CONFIRMED=1 Y6_STOP_AFTER_GATES=1 setsid nohup bash improvements/worker-y6b-run-nested-wayland-v2.sh > /tmp/y6-nested/a8-launch-20261122.log 2>&1 < /dev/null & disown`
- Launch: 16:18:03 +07. Run log: /tmp/y6-nested/run-20261122-161803.log
  (77 lines, 5305 bytes, md5 721cb67c5b2947639236b89a706fad36).
  Full verbatim copy saved to improvements/y6c5-evidence/a8-trial-run-20261122-161803.log.
- Nested session: timeout wrapper pid 1252978, nested Hyprland pid 1252981,
  nested sig 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795339084_327326060,
  nested socket wayland-1, nest output WAYLAND-1.
- Gates passed in order (run-log lines quoted verbatim):
  - `Y6-WAYLAND: AMEND4 OK: HYPRGLASS_SKIP_VERSION_CHECK unset (env | grep HYPRGLASS empty)`
  - `Y6-WAYLAND: plugin ABI OK: /home/james/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so`
  - `Y6-WAYLAND: AMEND5-BEFORE OK: no hyprglass load path in live config chain (hyprland.lua + hyprland.conf + sourced files)`
  - `Y6-WAYLAND: live sig 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825 pid 1515`
  - Live plugin list BEFORE recorded (hyprbars, hyprglass, computer-use-cursor).
  - `Y6-WAYLAND: runner-quiet process check OK (no runner scripts, no geckodriver, no mpv/foot)`
  - `Y6-WAYLAND: flock held, runner-quiet window open`
  - Backend gate: `DEBUG from aquamarine ]: Starting the Wayland backend!`
  - `Y6-WAYLAND: nested socket wayland-1`
  - `Y6-WAYLAND: nest output WAYLAND-1`
  - Nested plugin list: only hyprglass 1.1.1-cu.1 (nest-plugin-list.json,
    md5 de7d2aebcfe9b0553e4e4b7af101fb11).
  - Nested status JSON (nest-glass-status.json, md5 5d868d0975a66784a6a56119614843e1):
    version 1.1.1-cu.1, versionCheck match, active true, shaders pending,
    features.layers.enabled true active true.
  - `Y6-WAYLAND: hyprglass version=1.1.1-cu.1 versionCheck=match`
- Gate that failed (A2 positive profile gate):
  - `Y6-WAYLAND: profile gate: parse-1 not-ready marker is expected, waiting for applied marker`
  - `Y6-WAYLAND: profile gate: parse-1 not-ready marker present (expected, not a failure)`
  - `Y6-WAYLAND: profile gate: applied marker absent after 15s (tail of nested log):`
  - `Y6-WAYLAND: FAIL: profile not applied: Y6-NEST-OPTICS applied marker absent after 15s; see nested log tail above`
  - Teardown start 16:18:27, teardown done 16:18:29.
- Nothing after the profile gate ran: no G4, no liquid gate, no
  Y6_STOP_AFTER_GATES exit line, no backdrop, no pill, no arms, no grim.
  The after-gate re-check files do not exist
  (nest-glass-status-after-gate.json and nest-plugin-list-after-gate.json
  absent, confirmed 16:20:36 +07).

## 2. The 7 measured items

### Item 1: Positive marker. FAIL.

- `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator`
  absent from BOTH live logs after the 15 s poll.
- The gate greps the live per-instance log ($NEST_LOG) plus the stdout log
  ($LOG) during the run, so the verdict rests on the live poll, not on saved
  logs (A10).
- Marker grep on the saved logs after teardown (for the record only):
  - Saved nested per-instance log (188 lines, 16470 bytes,
    md5 b8832e82500fdfce62d49e2a2b0a7783): exactly ONE Y6-NEST line, line 15:
    `DEBUG ]: [hlPrint] [Lua] Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)`
  - Stdout log /tmp/y6-nested/hyprland-wayland.log (62 lines,
    md5 a940682021b9bbad0f7ace90a1d52487): exactly ONE Y6-NEST line, line 50,
    the same parse-1 not-ready marker.
  - No `Y6-NEST-OPTICS: applied` line in either file. No
    `Y6-NEST-HOOK: profile applied` line in either file.
- Saved nested log note (A10): the saved copy is a 188-line flushed prefix;
  its last line is truncated mid-line (`..._CC` with no newline) and its
  30-line tail is all aquamarine dmabuf DEBUG spam. Absence in the saved
  copy alone is not the verdict; the live 15 s poll is.

### Item 2: Hook corroboration. FAIL.

- `Y6-NEST-HOOK: profile applied` absent from both logs (see item 1 grep).
- Parse-1 `Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)` present
  in both logs. Present is EXPECTED, not a failure.

### Item 3: Second signal (layers.enabled true). NOT OBSERVED AS SPECIFIED.

- The gate's layers check never executed: the gate fails at the marker poll
  before reaching the layers check and the re-check.
- What IS observed: the pre-gate status fetch (nest-glass-status.json,
  fetched before the gate) shows `"layers": {"enabled": true, "active": true, "reason": null}`.
  The re-check after the marker specified by the trial did not happen, so
  item 3 as specified does not hold. The pre-gate value is recorded here as
  a fact for re-review, not as a pass.

### Item 4: Version. PASS on the pre-gate check; re-check not run.

- Pre-gate: hyprglass 1.1.1-cu.1, versionCheck match, in the status JSON and
  in the runner output (`Y6-WAYLAND: hyprglass version=1.1.1-cu.1 versionCheck=match`).
- The re-check after the marker never ran (gate failed first), so the
  second half of item 4 is unobserved, not failed.

### Item 5: G4 configerrors empty. NOT REACHED, no output exists.

- The G4 gate sits after the profile gate. It never ran. There is no
  configerrors output to record, empty or otherwise.
- O1/G4 tension: unobserved. No configerrors data exists from this run, so
  no G4-NARROW-NEEDED determination can be made. Any parse-3
  duplicate-layer error, if present, was not observed.

### Item 6: AMEND4 + AMEND5. PASS.

- AMEND4: `Y6-WAYLAND: AMEND4 OK: HYPRGLASS_SKIP_VERSION_CHECK unset (env | grep HYPRGLASS empty)`.
- AMEND5: `Y6-WAYLAND: AMEND5-BEFORE OK: no hyprglass load path in live config chain (hyprland.lua + hyprland.conf + sourced files)`.
- Live plugin list before == after, proven by identical md5:
  live-plugin-list-before.json and live-plugin-list-after.json both
  cf91d826447b1cdae7fe662b288c5611.
- Actual before-list (recorded, not assumed): hyprbars 1.0, hyprglass
  1.1.1-cu.1, computer-use-cursor 1.0.0. Same list after.

### Item 7: Live untouched. PASS.

- Live PID 1515 alive at launch, in the teardown live check
  (`1515 Sat Nov 21 15:17:25 2026 Hyprland --watchdog-fd 4`), and in the
  post-run check (`1515 Hyprland --watchdog-fd 4`).
- Live hyprctl responds in teardown (version output: Hyprland 0.57.2,
  commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947, Tag v0.57.2).
- Live plugin list identical before/after (item 6).
- Stray check in teardown: only `1515 Hyprland --watchdog-fd 4`. No stray
  mpv, foot, or indicator processes (the stray check prints nothing else).
- Lock free after teardown: `Y6-WAYLAND: lock free after teardown`.
- Nest runtime dir removed: post-run `ls /tmp/y6-nested/run` reports the
  run dir removed (teardown done).
- The nested per-instance log was copied out by the runner before removal:
  /tmp/y6-nested/hypr-saved-20261122-161803-11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795339084_327326060/hyprland.log
  (188 lines, md5 b8832e82500fdfce62d49e2a2b0a7783).

## 3. Observation items

- O1/G4 tension: not observed (G4 never ran, item 5). No verdict on narrowing.
- O3: shaders field at the status read is `pending` (nest-glass-status.json,
  fetched about 10 s after launch). Time from launch to liquid ready: NOT
  observed, the liquid gate never ran. Only "pending" was observed, never
  "ready".
- Marker counts: no saved-log marker counts used as parse evidence (A10).
  The verdict uses the live-log gate result only.
- Nested log content notes (facts for re-review, no diagnosis):
  - The saved nested log contains exactly one postConfigReload line (line 16,
    parse 1, disabling stdout logs) and no other config/reload/parse lines.
    The stdout log line 51 says the same: after parse 1, further logs go
    only to the per-instance log.
  - No Lua, optics, hook, or config-error lines appear in the saved nested
    log besides the parse-1 marker. The only ERR lines are aquamarine
    libseat/session errors (lines 24-25: `libseat: failed to open a seat`,
    `Failed to open a session`), which are nest-environment noise, present
    from startup.
  - The pre-gate status JSON shows features.layers.enabled true while the
    applied marker never appeared in either live log during the 15 s poll.
    This tension is recorded as an observed fact for the re-review; it is
    not a diagnosis and not a pass of any item.

## 4. What the trial did NOT do

- No pill launch, no pill ready wait, no geometry read, no arms, no grim
  frames, no mpv backdrop, no verdict lines. None ran; the run stopped at
  the profile gate.
- No manual `nest hyprctl reload` anywhere (R2). Zero non-comment reload
  lines in the runner.
- No live compositor reload, no live config change, no live plugin load or
  unload by this lane. Live optics untouched (live blur 0.0 not touched;
  no live write of any kind).

## 5. Handover to the coordinator

- Trial verdict: FAIL (item 1). The A8 trial does NOT pass all 7 items.
- Consequence: the pill measurement retry stays gated. It is NOT cleared by
  this run. Per the trial procedure it needs (a) this trial passing all 7
  items, which did not happen, and (b) a fresh re-review of the trial
  evidence. The fix diff goes back to re-review before any measurement run.
- Evidence files in the repo:
  - improvements/worker-click5-y6-a8-trial-log.md (this log)
  - improvements/y6c5-evidence/a8-trial-run-20261122-161803.log
    (verbatim run log, md5 721cb67c5b2947639236b89a706fad36)
- Evidence still on the laptop (/tmp, ephemeral, verify before it is gone):
  - /tmp/y6-nested/run-20261122-161803.log (md5 721cb67c...)
  - /tmp/y6-nested/hypr-saved-20261122-161803-11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795339084_327326060/hyprland.log
    (md5 b8832e82500fdfce62d49e2a2b0a7783)
  - /tmp/y6-nested/hyprland-wayland.log (md5 a940682021b9bbad0f7ace90a1d52487)
  - /tmp/y6-nested/nest-glass-status.json (md5 5d868d0975a66784a6a56119614843e1)
  - /tmp/y6-nested/nest-plugin-list.json (md5 de7d2aebcfe9b0553e4e4b7af101fb11)
  - /tmp/y6-nested/live-plugin-list-before.json and
    live-plugin-list-after.json (both md5 cf91d826447b1cdae7fe662b288c5611)
- No fix proposed, no diagnosis offered, no re-run attempted (standing rule:
  no self-healing). Awaiting the coordinator's re-review direction.

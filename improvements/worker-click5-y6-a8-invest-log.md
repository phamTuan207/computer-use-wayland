# Worker C5-Y6-A8-INVEST log: WHY the A8 applied marker never appeared
# Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
# Task received: Sun 2026-11-22 16:22:12 +07. T+0 at 16:22.
# Wall clock Asia/Ho_Chi_Minh + elapsed time per entry. No em/en dash. No personal info.
# Scope: INVESTIGATE ONLY. No fix applied, no file edited except this log,
# no trial re-run, no live touch, no plugin load, no reload. Read-only laptop
# reads via ~/workspace/ssh-laptop.sh only. Independent investigator: not the
# paper worker (C5-Y6-PAPER) and not the trial worker (C5-Y6-A8-TRIAL).

## VERDICT: FALSE FAIL. Named cause in one paragraph

- The A8 trial FAIL is a FALSE FAIL of the A2 gate, not a failure of the
  profile. The profile WAS applied on parse 2, and BOTH applied-marker
  prints executed inside the nested Hyprland process, but neither print
  ever reached the on-disk logs the gate greps, because the per-instance
  log file stops flushing after the Aquamarine dmabuf dump: the saved file
  is frozen mid-dump-line (188 lines, 16470 bytes, no trailing newline)
  while the nested process demonstrably ran past the dump (hyprglass
  loaded, status served over IPC before the gate). The gate measures
  log-file delivery, not profile application, so it fails a healthy
  profile. The 15 s poll cannot fix this: the flush lag is unbounded
  within the run (the file did not advance once between launch and the
  FAIL at 24 s), not a delay of seconds. Any re-run with the same gate
  fails identically. The fix must change the observation channel, not the
  profile path. Proposed fix diff in section 4, NOT applied here.

## 0. Investigation record (T+1m to T+9m, 16:23 to 16:31 +07)

- Evidence read in full first, per the brief:
  - improvements/worker-click5-y6-a8-trial-log.md (trial log, 7 items).
  - improvements/y6c5-evidence/a8-trial-run-20261122-161803.log (verbatim
    run log, 77 lines, md5 721cb67c5b2947639236b89a706fad36).
  - Nested per-instance log on the laptop, fetched read-only via
    ~/workspace/ssh-laptop.sh, full cat: 188 lines, 16470 bytes, md5
    b8832e82500fdfce62d49e2a2b0a7783 (re-verified by this lane, matches
    the trial log section 5).
  - Staged nest files on the laptop, read in full with md5 re-verification:
    conf 9ccb27017ab63a9d2bce1d9651425d3b, hook
    6dd68aeadbe7e1c9049436dc7361ee7a, optics
    85298d2035697710d95117355c9830ca (all match the trial log).
  - Stdout log /tmp/y6-nested/hyprland-wayland.log: 62 lines, md5
    a940682021b9bbad0f7ace90a1d52487 (re-verified, matches trial log).
  - Pre-gate status JSON /tmp/y6-nested/nest-glass-status.json, md5
    5d868d0975a66784a6a56119614843e1 (re-verified, matches trial log).
  - Paper lane log improvements/worker-click5-y6-paper-log.md (A1-A10,
    gaps M1/M2/M3, re-review section 5).
  - Redteam improvements/worker-y6r-redteam.md (mechanism section 1.2,
    buffering section 2a, P1-P8).
  - Runner improvements/worker-y6b-run-nested-wayland-v2.sh (A2 gate
    lines 387-450, G4 lines 452-470, teardown lines 116-130, header
    lines 1-70, launch lines 300-386).
  - Test file tests/test_y6c5_positive_gate.py (17 checks, read in full).
  - A8 trial doc improvements/worker-y6c5-a8-load-only-trial.md.
  - Y6e load log improvements/worker-y6e-rebuild-load-log.md lines
    555-600 (21:57 run, same status shape, same frozen log shape).
- Sources verified directly on the laptop by this lane (new evidence, not
  taken from any paper):
  - Hyprglass worktree ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/src/PluginConfig.cpp
    (default false, config/layer handlers, forwardLuaConfig) and
    src/Diagnostics.cpp (featureStatus call site).
  - Hyprland 0.57.2 source ~/backups/omarchy-native-port-20261113/Hyprland-0.57.2/src/
    (Compositor.cpp, ConfigManager.cpp, PluginSystem.cpp, Lua bindings).
  - Live optics file ~/.local/share/agent-computer-use/native/hyprglass-local-optics.lua
    (byte-identical table to the nest optics.lua, applied live every boot).
  - Old optics backup /tmp/y6-nested/conf/optics.lua.bak-y6c5-20261122
    (md5 b011ea91, diffed against the new optics.lua).
- Repo HEAD at investigation time: a46180b (moved from 53639c7 during
  this lane by a coordinator docs commit; no Y6 file changed). Trial
  commit: 5fdc527. Trial run: 16:18:03 to 16:18:29 +07, 26 s.

## 1. Proof chain: the profile WAS applied, the prints executed, the log never delivered them

### L1. The staged files are the right files, and the hook runs from them

- Conf /tmp/y6-nested/conf/hyprland-wayland.lua, 19 lines, md5
  9ccb27017ab63a9d2bce1d9651425d3b. Line 16:
  `hl.plugin.load("~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so")`.
  Line 18: `dofile("/tmp/y6-nested/conf/nested-visuals-hook.lua")`. No
  `plugin:hyprglass` config block anywhere in the file (read in full).
- Hook /tmp/y6-nested/conf/nested-visuals-hook.lua, md5
  6dd68aeadbe7e1c9049436dc7361ee7a. Line 30:
  `print("Y6-NEST-HOOK: profile applied")`, immediately after the bare
  `dofile("/tmp/y6-nested/conf/optics.lua")` on line 29 (repo copy
  improvements/y6-nested-conf/nested-visuals-hook.lua, same lines).
- Optics /tmp/y6-nested/conf/optics.lua, md5
  85298d2035697710d95117355c9830ca. Line 47, last line of the file:
  `print("Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator")`,
  after `hl.plugin.hyprglass.config(config)` and
  `hl.plugin.hyprglass.layer("computer-use-indicator", { preset = "default", mask_mode = "contour" })`.
- The nest read the staged conf: stdout log line 1,
  `User-specified config location: '/tmp/y6-nested/conf/hyprland-wayland.lua'`.

### L2. The hook ran at parse 1 and saw the plugin missing, as designed

- Nested per-instance log line 15:
  `DEBUG ]: [hlPrint] [Lua] Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)`.
- Stdout log line 50: the same marker. Exactly ONE Y6-NEST line in each
  file (grep -n confirms: nested log 1 match at line 15, stdout log 1
  match at line 50). This is the EXPECTED parse-1 marker, not a failure.

### L3. Parse 2 ran, the hook took the success branch, config() ran (the decisive link)

- The pre-gate nest status JSON (nest-glass-status.json, md5
  5d868d0975a66784a6a56119614843e1, fetched BEFORE the gate, run-log
  lines 17-26) reports:
  `"layers": {"enabled": true, "active": true, "reason": null}`.
- The default is false in the REBUILT plugin, verified in source by this
  lane (not from the pin diff): worktree src/PluginConfig.cpp:83,
  `addConfigValue<Config::Values::Bool>(handle, ConfigKeys::LAYERS_ENABLED, false);`.
  The key is `plugin:hyprglass:layers:enabled` (src/PluginConfig.hpp:126).
- The status field IS the registered config value, verified in source:
  worktree src/PluginConfig.cpp:322,
  `config.layersEnabled = getStaticPtr<Config::BOOL>(handle, ConfigKeys::LAYERS_ENABLED);`,
  and src/Diagnostics.cpp:414,
  `const auto layers = featureStatus(config.layersEnabled, g_pGlobalState->renderLayerHook != nullptr);`,
  with `status.enabled = enabledValue && **enabledValue;` (pin diff
  lines 1913-1915, same code in the worktree). So `layers.enabled: true`
  means the registered value `plugin:hyprglass:layers:enabled` is true.
- The ONLY setter of that value in the nest is optics.lua config():
  worktree src/PluginConfig.cpp:630-652 `forwardLuaConfig` wraps the
  optics table as `plugin.hyprglass.<keys>` and calls Hyprland
  `hl.config` with it, so `layers = { enabled = true }` lands on the
  registered value; `handleLuaConfig` (lines 654-671) forwards through
  it. No other code in the worktree src/ assigns the registered value
  (grep for assignments to layersEnabled finds only the getStaticPtr
  read at line 322 and the nullptr declaration in PluginConfig.hpp:383).
- Nothing else in the nest could have set it: the nest conf has no
  `plugin:hyprglass` config (L1, 19 lines read in full); the runner
  issues NO hyprglass config command before the status fetch (runner
  lines 370-372: only `nest hyprctl -j plugin list` then
  `nest hyprctl -j hyprglass status`); the pill was never launched in
  this trial (Y6_STOP_AFTER_GATES=1, and the gate failed before any
  pill step).
- Therefore `hl.plugin.hyprglass.config(config)` RAN in the A8 nest run.
  The only path to it is the hook success branch on a later parse
  (conf line 18 dofile, hook line 29 dofile). Therefore parse 2 ran and
  the hook saw count=1, version=1.1.1-cu.1.
- Mechanism re-derived from Hyprland 0.57.2 source on the laptop by this
  lane (closes paper gap M1, which was redteam citations only):
  - src/Compositor.cpp STAGE_LATE: `"Creating the PluginSystem!"`,
    `g_pPluginSystem = makeUnique<CPluginSystem>();`, then
    `Config::mgr()->handlePluginLoads();`.
  - src/config/lua/ConfigManager.cpp:1093-1104 `handlePluginLoads()`:
    `if (!g_pPluginSystem) return;`, then
    `updateConfigPlugins(m_registeredPlugins, pluginsChanged)`, then
    `if (pluginsChanged) { ErrorOverlay::overlay()->destroy(); reload(); }`.
  - src/plugins/PluginSystem.cpp:197-240 `updateConfigPlugins`: sets
    `changed = true` BEFORE `loadPlugin(...)` returns, so on first
    parse pluginsChanged is true and reload() runs synchronously.
  - src/config/lua/bindings/LuaBindingsConfigRules.cpp:562:
    `mgr->m_registeredPlugins.emplace_back(path);` (load only records).
  - src/config/lua/bindings/LuaBindingsToplevel.cpp:270-296 `hlGetPlugins`:
    returns an empty table immediately if `!g_pPluginSystem` (parse 1),
    else `g_pPluginSystem->getAllPlugins()` (parse 2 sees count=1).
  - src/plugins/PluginSystem.cpp:131 and :189: `loadPluginInternal`
    schedules one more reload with
    `g_pEventLoopManager->doLater([] { Config::mgr()->reload(); });`
    (parse 3, hook runs again, idempotent re-application).
  - src/config/lua/ConfigManager.cpp:820: `handlePluginLoads()` is called
    inside `postConfigReload`, and the "Disabling stdout logs" message
    just above it is logged only `if (disableStdout && m_isFirstLaunch)`.
    So the single postConfigReload line (nested log line 16) is EXPECTED
    even when parse 2 and parse 3 run: it is a first-launch-only line.
    The trial log's "exactly one postConfigReload line" observation does
    not count against parse 2.

### L4. layer() cannot abort the prints (rules out a half-applied profile)

- Worktree src/PluginConfig.cpp:823-931 `handleLuaLayer`: EVERY problem
  path calls `reportLuaError` (reported, not raised) and returns 0. The
  function always reaches `s_pendingLayers.push_back(std::move(entry));`
  and `return 0`. The comment at the top states the rule explicitly:
  "from here on problems go to reportLuaError: a Lua error would unwind
  past entry's strings". The exact call in optics.lua,
  `layer("computer-use-indicator", { preset = "default", mask_mode = "contour" })`,
  uses accepted values (preset is stored as a string, no validation here;
  mask_mode "contour" parses via `parseLayerMaskMode`, and even an
  unknown mode only reports and continues).
- Therefore, once config() returns (L3), layer() returns, optics.lua
  line 47 `print("Y6-NEST-OPTICS: applied ...")` executes, the dofile
  returns, and hook line 30 `print("Y6-NEST-HOOK: profile applied")`
  executes. BOTH prints executed inside the nested process.

### L5. config() cannot have thrown on this table

- The new optics.lua config table is BYTE-IDENTICAL to the Y6e run's
  optics.lua: `diff` of the old backup
  (/tmp/y6-nested/conf/optics.lua.bak-y6c5-20261122, md5 b011ea91)
  against the new file shows ONLY the A3 comment block (lines 2-9) and
  the print line 47 as additions. Same keys, same values, same calls.
- The same table is the LIVE optics file
  (~/.local/share/agent-computer-use/native/hyprglass-local-optics.lua),
  read in full by this lane: identical material table, identical config
  table (including `tint_color = 0xffffff00` and `blur_strength = 0.15`),
  identical config() and layer() calls. The live session applies this
  exact table at every boot with the same rebuilt plugin and runs with
  layers enabled true, shaders READY (paper log 16:15 read). A table
  that throws in hl.config cannot be the live session's working optics.
- Inside `forwardLuaConfig`, unknown keys are REPORTED (the setByUser
  no-op guard), not thrown; only a type or range error in hl.config
  could raise, and every value in this table is well-typed (numbers,
  booleans, strings, nested tables) and identical to the live working
  table. There is no throwable key.
- So no half-application path remains: config() returned (L3 proves the
  write landed) and layer() cannot throw (L4). The prints in L4
  executed. Their absence from the logs is a delivery failure, not an
  execution failure.

### L6. The prints never reached either log file, because the file is frozen mid-dump

- The live 15 s poll found nothing: runner lines 407-418 poll
  `grep -a -q "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG"` every 1 s
  for 15 s, then FAIL. Saved nested log: exactly one Y6-NEST line
  (line 15). Saved stdout log: exactly one Y6-NEST line (line 50).
- The saved nested log is frozen: 188 lines, 16470 bytes, last line
  truncated mid-line with NO trailing newline (the `---MD5---` echo in
  this lane's ssh fetch landed on the same line as the last dump line).
  Its last content is Aquamarine dmabuf spam:
  `zwp_linux_dmabuf_v1: Got format XR4H with modifier Y_TILED_GEN12_RC_CCS_CC`
  (cut off, no newline).
- The LIVE file was frozen at the SAME point at FAIL time: verbatim run
  log line 67 is the FAIL line SHARING its line with the truncated dump
  line (`..._CCY6-WAYLAND: FAIL: profile not applied: ...`). The gate's
  own 30-line tail (run-log lines 37-66) is all dmabuf spam ending at
  that truncation. Between launch (16:18:03) and FAIL (16:18:27, 24 s),
  the file did not advance once.
- But the PROCESS ran past the dump: the nested plugin list (only
  hyprglass 1.1.1-cu.1) and the status JSON (version 1.1.1-cu.1,
  versionCheck match, layers enabled true) were fetched over IPC BEFORE
  the gate (run-log lines 17-33). STAGE_LATE, the plugin load, the
  reload, parse 2, parse 3, and the status queries all happened after
  the dump lines in the log stream, and NONE of their log lines reached
  the file during the run. Expected post-dump lines that are absent:
  "Creating the PluginSystem!", "Loading plugin ...", "loaded ...",
  any reload line, both applied-marker prints.
- The backend gate passing sharpens this: it greps
  "Starting the Wayland backend!" from $NEST_LOG and PASSED (nested log
  line 27, before the dump). So the gate targets the right file, the
  file DOES receive flushed content up to the dump, and then it stops
  advancing DURING the dump. The freeze starts inside the dump, not
  before it.
- Mechanism (redteam 2a, cited, not re-derived by this lane: hyprutils
  src/cli/Logger.cpp gives stdout `std::fflush(stdout)` per line but
  the file only `m_logOfs << ...` with no per-line flush; the
  hyprutils source was not found in the laptop checkout, so this leg
  rests on the redteam citation PLUS the empirical freeze above, which
  proves the delivery lag on its own): post-dump log output sits in the
  unflushed ofstream tail, and the SIGKILL teardown discards the
  buffer, so the saved copy is a flushed prefix that ends mid-dump.
  This is the same shape as the Y6e run (also exactly 188 lines ending
  mid-dump, one marker at line 15, redteam P2) and the Y6c probe 2 run.
  Three runs, same frozen shape, same missing post-dump lines.
- Consequence for the gate: the A2 gate greps a file that cannot
  contain the event it waits for within the run window. The 15 s poll
  is a margin for a flush that never comes while the compositor is
  idle after startup. Extending the timeout cannot fix it.

## 2. Hypotheses ruled out (each with its killing evidence)

- R1 "Parse 2 never ran (no reload after the plugin load)": KILLED by L3.
  layers.enabled true requires config() to have run, which requires the
  hook success branch on a later parse. The reload call is also verified
  in source (ConfigManager.cpp:1093-1104, PluginSystem.cpp:197-240).
- R2 "layer() threw, so the profile is half-applied and the prints
  correctly never ran": KILLED by L4. handleLuaLayer reports only and
  always returns 0; it cannot abort optics.lua.
- R3 "config() threw mid-table, after layers.enabled but before the
  print": KILLED by L5. The table is byte-identical to the Y6e table and
  to the live session's working table; no key can raise hl.config.
- R4 "The gate polled the wrong log files": KILLED by L6. The backend
  gate found its line in the same $NEST_LOG, and the same A2 gate code
  found the parse-1 marker in both $LOG and $NEST_LOG. The grep works
  and targets the right files; the applied lines are genuinely absent
  from those files.
- R5 "Stale marker or stale log from a previous run": KILLED by the
  runner truncating $LOG at launch and using a fresh $RUN_DIR/hypr per
  run, and by the nested signature being unique to this run
  (11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795339084_327326060).
  The parse-1 marker found is this run's.
- R6 "The status JSON came from the live session, not the nest":
  KILLED by the values: nest status shows shaders "pending" while live
  shows "ready" (paper log 16:15), and the nest plugin list shows ONLY
  hyprglass while live shows hyprbars + hyprglass +
  computer-use-cursor. Different processes, nest confirmed.
- R7 "Live interference or another lane's load/unload during the
  window": KILLED by trial log items 6-7: live plugin list before and
  after have identical md5 cf91d826447b1cdae7fe662b288c5611, live PID
  1515 alive throughout, no stray processes, lock free after teardown.
- R8 "The profile was never applied (the Y6e original claim, pre-A4)":
  KILLED by L3. The A4 errata stands and is now PROVEN, not just
  inferred: config() ran on parse 2. What the A3 marker was meant to
  prove (layer() registration + material values) is proven instead by
  L4 (layer() cannot throw) plus the live table identity (L5).
- R9 "The 15 s poll was just too short": KILLED by L6. The file did not
  advance once in 24 s; the lag is unbounded within the run, not a
  delay of seconds. A longer poll waits for a flush that only happens
  when the buffer fills, and the idle post-startup compositor does not
  fill it.

## 3. What the trial FAIL verdict means, and the paper gaps

- The FAIL line (verbatim run log line 67,
  `Y6-WAYLAND: FAIL: profile not applied: Y6-NEST-OPTICS applied marker absent after 15s`)
  is TRUE as a statement about the LOGS and FALSE as a statement about
  the PROFILE. The gate's fail string ("profile not applied") misnames
  the cause the same way the old U6 string did: it reports an
  observation-channel failure as an application failure.
- The 7 measured items, re-read with this cause:
  - Item 1 (positive marker): FAIL as specified (log grep), FALSE FAIL
    as a profile verdict. The marker executed in-process (L4) and the
    profile applied (L3).
  - Item 2 (hook corroboration): same as item 1, same cause.
  - Item 3 (layers.enabled true): OBSERVED pre-gate (status JSON,
    run-log lines 17-26), though the trial log correctly records it as
    "not observed as specified" because the re-check after the marker
    never ran. The pre-gate value is the same field and it is true.
  - Item 4 (version): PASS on the pre-gate check; re-check not run.
  - Item 5 (G4 configerrors): NOT REACHED, no output exists. G4 sits
    after the A2 gate, so the one IPC gate that WOULD have worked never
    ran. No configerrors data exists from this run.
  - Item 6 (AMEND4 + AMEND5): PASS, stands.
  - Item 7 (live untouched): PASS, stands.
- Paper gaps, resolved by this investigation:
  - M1 (MEDIUM, parse-2 mechanism not re-derived): CLOSED. Re-derived
    from Hyprland 0.57.2 source on the laptop (L3) AND proven
    empirically by layers.enabled true.
  - M2 (MEDIUM, parse-2 print delivery inferred, not observed): CLOSED,
    resolving AGAINST the design. Print delivery to the log file is now
    OBSERVED to NOT happen within the run window. The A2 gate's primary
    signal is unobservable by construction as written.
  - M3 (MEDIUM, G4/O1 tension): NARROWED by source, still unobserved in
    a run. Worktree src/PluginConfig.cpp `commitPendingLayers()` calls
    `resetLayerNamespaces()` (which clears all layer namespace maps)
    BEFORE re-applying the pending layers, so a parse-3 re-registration
    of the same namespace clears first and cannot produce the feared
    duplicate-layer error. The G4 false-fail via O1 is therefore not
    expected, but G4 never ran in this trial, so the re-run's G4
    observation still decides. The trial doc's G4-NARROW-NEEDED outcome
    stays defined but is now unlikely to trigger.
  - The A4 errata (profile config applied on parse 2) stands, now
    proven by L3 rather than inferred from the status field alone.

## 4. Proposed fix diff (written here ONLY, NOT applied to any file)

- Design rule: change the OBSERVATION channel, not the profile path.
  Nothing is wrong with the profile application (parse 2, config(),
  layer() all work). The log file is not a delivery channel for
  post-parse-2 lines, so the gate must stop grepping it for the applied
  marker. The new primary signal is a marker FILE the hook writes and
  closes (a closed file is on disk immediately), plus the IPC status
  field that already works. Log greps stay as corroboration output only.
  G4 moves BEFORE the marker poll, because it is an IPC query that works
  regardless of log delivery, and it is the only gate that catches a
  throwing config(). Base: HEAD a46180b. All paths below are repo paths.

### 4a. Hook: write the marker to a file and close it

```diff
--- a/improvements/y6-nested-conf/nested-visuals-hook.lua
+++ b/improvements/y6-nested-conf/nested-visuals-hook.lua
@@ -6,6 +6,11 @@
 -- Y6C5-A3/A4 (2026-11-22, Y6r R1/R3): the parse-1 "not ready" marker is EXPECTED
 -- on every successful startup. Parse 1 runs before the plugin system exists, so
 -- hl.get_loaded_plugins() is empty by the early-return branch; parse 2 runs
 -- after STAGE_LATE loads the plugin and calls reload(), so the hook sees
 -- count=1 and dofiles optics.lua. The profile IS applied on parse 2. The old
 -- claim that the marker proves the profile missing was wrong and is corrected.
+-- Y6C5-A8-INVEST (2026-11-22): the per-instance log file does NOT deliver
+-- post-parse-2 prints within the run (ofstream buffering, SIGKILL discards
+-- the tail; A8 trial 16:18 2026-11-22 proved the profile applied while the
+-- marker never reached either log). The gate therefore cannot grep the log
+-- for the applied marker. The hook writes the same marker to a plain file
+-- and closes it: a closed file is on disk immediately. Log prints stay as
+-- corroboration only. See improvements/worker-click5-y6-a8-invest-log.md.
 -- The runner checks liquid_available(ready=true) after start, but that gate is
 -- metadata-only (scripts/indicator.py docstring): it CANNOT prove the profile
 -- was applied, because hyprglass status carries no blur, refraction, preset,
@@ -24,6 +29,17 @@ end
 if glass_count == 1 and glass_version == "1.1.1-cu.1" then
   dofile("/tmp/y6-nested/conf/optics.lua")
   -- Y6C5-A3: printed AFTER the dofile returns, so a dofile error (a throwing
   -- optics.lua) means no marker. Bare dofile, no pcall: errors must propagate.
   print("Y6-NEST-HOOK: profile applied")
+  -- Y6C5-A8-INVEST: same marker, delivered through a file instead of the
+  -- buffered log. dofile returned, so optics.lua line 47 already printed
+  -- in-process; writing both lines here records the same event. Explicit
+  -- close() flushes to disk at once. A failed open is silent: the gate
+  -- then fails closed on the missing file, and the log print (if it ever
+  -- flushes) is the diagnostic. Path is the nest run dir from the
+  -- environment the launcher sets (XDG_RUNTIME_DIR=/tmp/y6-nested/run),
+  -- never the live runtime dir.
+  local marker_path = (os.getenv("XDG_RUNTIME_DIR") or "/tmp/y6-nested/run") .. "/y6-profile-applied.txt"
+  local marker_file = io.open(marker_path, "w")
+  if marker_file then
+    marker_file:write("Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator\n")
+    marker_file:write("Y6-NEST-HOOK: profile applied\n")
+    marker_file:close()
+  end
 else
```

### 4b. Runner: A2 gate polls the marker FILE, layers.enabled first, log greps corroboration only

```diff
--- a/improvements/worker-y6b-run-nested-wayland-v2.sh
+++ b/improvements/worker-y6b-run-nested-wayland-v2.sh
@@ -387,50 +387,61 @@
 # BEGIN Y6C5-A2 positive profile gate (Y6r A2, R3; replaces the old U6 block)
 # The parse-1 "not ready" marker is EXPECTED on every successful startup
 # (parse 1 runs before the plugin system exists; the profile is applied on
 # parse 2). It must NEVER fail the run. This gate is positive: it requires
 # the applied marker printed AFTER optics.lua returns, plus a second signal,
 # features.layers.enabled == true, read from the status JSON fetched above.
 # The marker proves config()+layer() returned; layers.enabled proves the
 # config effect (optics.lua is the only setter; the plugin default is false).
-# Y6C5-A10: this greps the LIVE per-instance log ($NEST_LOG) during the run
-# (plus the stdout log $LOG). Saved-log marker counts are NOT parse evidence
-# (ofstream buffering; saved logs are flushed prefixes, tail lost on SIGKILL
-# teardown). No gate here reads a hypr-saved directory.
-# Poll timeout/interval are overridable for tests (Y6C5_GATE_TIMEOUT_S,
-# Y6C5_GATE_INTERVAL_S); production defaults are 15 s / 1 s. By the time
-# this gate runs (about 10 s after launch) parse 2 has already applied the
-# profile, so the poll is a margin for log flush lag, not for the load.
+# Y6C5-A8-INVEST (2026-11-22): this gate used to grep the LIVE per-instance
+# log ($NEST_LOG) for the applied marker. That channel is broken by
+# construction: the log file stops flushing after the Aquamarine dmabuf dump,
+# and post-parse-2 lines sit in the unflushed ofstream tail until the SIGKILL
+# teardown discards them. The A8 trial (16:18:03 to 16:18:29 2026-11-22)
+# proved it: the profile was applied (layers.enabled true against a default
+# of false) while the marker never reached either log in 15 s of polling.
+# See improvements/worker-click5-y6-a8-invest-log.md. The gate therefore
+# polls the marker FILE the hook writes and closes
+# ($RUN_DIR/y6-profile-applied.txt). A closed file is on disk immediately,
+# so the poll observes the event, not the log flush. Log greps below are
+# corroboration output only and NEVER fail the run. Saved-log marker counts
+# are NOT parse evidence (A10). No gate here reads a hypr-saved directory.
+# Poll timeout/interval are overridable for tests (Y6C5_GATE_TIMEOUT_S,
+# Y6C5_GATE_INTERVAL_S); production defaults are 15 s / 1 s. By the time
+# this gate runs (about 10 s after launch) parse 2 has already applied the
+# profile and written the file, so the poll is a margin for scheduling, not
+# for the load and not for log flush lag.
 echo "Y6-WAYLAND: profile gate: parse-1 not-ready marker is expected, waiting for applied marker"
 if grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG" 2>/dev/null; then
   echo "Y6-WAYLAND: profile gate: parse-1 not-ready marker present (expected, not a failure)"
 fi
+# First signal (IPC, already fetched): layers.enabled must be true in the
+# status JSON fetched above. This is the config effect, and it is read over
+# IPC, so it works regardless of log delivery.
+python3 - "$NEST/nest-glass-status.json" << 'PYEOF' || fail "profile not applied: features.layers.enabled is not true in hyprglass status (see status JSON above)"
+import json, sys
+d = json.load(open(sys.argv[1]))
+layers = (d.get("features") or {}).get("layers") or {}
+print("Y6-WAYLAND: profile gate: features.layers.enabled=" + str(layers.get("enabled")))
+if layers.get("enabled") is not True:
+    sys.exit(1)
+PYEOF
+MARKER_FILE="$RUN_DIR/y6-profile-applied.txt"
 GATE_TIMEOUT="${Y6C5_GATE_TIMEOUT_S:-15}"
 GATE_INTERVAL="${Y6C5_GATE_INTERVAL_S:-1}"
 GATE_DEADLINE=$(( $(date +%s) + GATE_TIMEOUT ))
 GATE_OK=""
 while [ "$(date +%s)" -le "$GATE_DEADLINE" ]; do
-  if grep -a -q "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null; then GATE_OK=1; break; fi
+  if [ -f "$MARKER_FILE" ] && grep -a -q "Y6-NEST-OPTICS: applied" "$MARKER_FILE" 2>/dev/null; then GATE_OK=1; break; fi
   sleep "$GATE_INTERVAL"
 done
 if [ -z "$GATE_OK" ]; then
-  echo "Y6-WAYLAND: profile gate: applied marker absent after ${GATE_TIMEOUT}s (tail of nested log):"
+  echo "Y6-WAYLAND: profile gate: applied marker file absent after ${GATE_TIMEOUT}s (log corroboration below, then tail of nested log):"
+  grep -a -h "Y6-NEST-HOOK" "$LOG" "$NEST_LOG" 2>/dev/null || echo "Y6-WAYLAND: profile gate: no Y6-NEST lines in either log"
   tail -30 "$NEST_LOG" 2>/dev/null || tail -30 "$LOG"
-  fail "profile not applied: Y6-NEST-OPTICS applied marker absent after ${GATE_TIMEOUT}s; see nested log tail above"
+  fail "profile not applied: marker file $MARKER_FILE absent after ${GATE_TIMEOUT}s; see nested log tail above"
 fi
-grep -a -h "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3
-HOOK_APPLIED=$(grep -a -h "Y6-NEST-HOOK: profile applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3 || true)
-if [ -n "$HOOK_APPLIED" ]; then printf '%s\n' "$HOOK_APPLIED"; else echo "Y6-WAYLAND: profile gate: hook applied marker not seen in logs (optics marker present, continuing)"; fi
-# Second positive signal: layers.enabled must be true in the status JSON
-# fetched above (optics.lua is the only setter; the plugin default is false).
-# NOTE: this is an early read of the same field the liquid gate already
-# requires (scripts/indicator.py _valid_liquid needs layers.enabled True);
-# its value is failing fast here instead of after a 60 s liquid wait.
-python3 - "$NEST/nest-glass-status.json" << 'PYEOF' || fail "profile not applied: features.layers.enabled is not true in hyprglass status (see status JSON above)"
-import json, sys
-d = json.load(open(sys.argv[1]))
-layers = (d.get("features") or {}).get("layers") or {}
-print("Y6-WAYLAND: profile gate: features.layers.enabled=" + str(layers.get("enabled")))
-if layers.get("enabled") is not True:
-    sys.exit(1)
-PYEOF
+grep -a -h "Y6-NEST-OPTICS: applied" "$MARKER_FILE" 2>/dev/null | head -3
+grep -a -h "Y6-NEST-HOOK: profile applied" "$MARKER_FILE" 2>/dev/null | head -3
+# Corroboration only: any applied-marker lines that did flush into the logs.
+# Their absence here is NOT a failure (see the A8-INVEST comment above).
+grep -a -h "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3 || echo "Y6-WAYLAND: profile gate: applied marker not in logs (expected: log delivery lags, file is authoritative)"
 # Re-run the plugin-list and version checks after the marker: the profile
 # must still be loaded when the gate passes, not only at the earlier check.
 nest hyprctl -j plugin list > "$NEST/nest-plugin-list-after-gate.json" 2> "$NEST/nest-plugin-list-after-gate.err" || fail "nested hyprctl plugin list re-check failed after profile gate"
 grep -q hyprglass "$NEST/nest-plugin-list-after-gate.json" || fail "hyprglass missing from nested plugin list on re-check after profile gate"
 nest hyprctl -j hyprglass status > "$NEST/nest-glass-status-after-gate.json" 2> "$NEST/nest-glass-status-after-gate.err" || fail "nested hyprglass status re-check failed after profile gate"
 python3 - "$NEST/nest-glass-status-after-gate.json" << 'PYEOF' || fail "hyprglass version mismatch on re-check after profile gate"
 import json, sys
 d = json.load(open(sys.argv[1]))
 ver = d.get("version"); vc = d.get("versionCheck")
 print("Y6-WAYLAND: profile gate re-check: hyprglass version=" + str(ver) + " versionCheck=" + str(vc))
 if ver != "1.1.1-cu.1" or vc != "match":
     sys.exit(1)
 PYEOF
-echo "Y6-WAYLAND: profile gate OK: applied marker present, layers.enabled true, plugin list and version re-checked"
+echo "Y6-WAYLAND: profile gate OK: applied marker file present, layers.enabled true, plugin list and version re-checked"
 # END Y6C5-A2 positive profile gate
```

### 4c. Runner: move the G4 block BEFORE the A2 block (IPC gate first)

- Cut the whole G4 block (runner lines 452-470, `# BEGIN Y6C5-A6-G4
  configerrors gate` through `# END Y6C5-A6-G4 configerrors gate`) and
  insert it immediately BEFORE the `# BEGIN Y6C5-A2 positive profile
  gate` line (line 387). No text change inside the block except this
  one comment addition at its head:
```diff
 # BEGIN Y6C5-A6-G4 configerrors gate
 # Y6C5-A6 (Council 3 G4, supporting gate): nest configerrors must be empty
 # after profile application. A throwing optics.lua surfaces as a config
 # error, not as a missing marker, so this is the only gate catching that
 # case. Pattern follows scripts/activation_checks.py wait_for_profile
 # (stripped output must be empty). A failed configerrors call fails closed.
+# Y6C5-A8-INVEST (2026-11-22): this block now runs BEFORE the A2 marker
+# poll. configerrors is an IPC query, so it works regardless of log
+# delivery, and in the A8 trial it never ran at all because the A2 gate
+# failed first. A throwing config() must fail here with its error text,
+# not hide behind a marker timeout.
```
- Rationale: in the A8 run, zero configerrors data exists because G4
  sat behind the failing gate. Order the IPC gates first (layers.enabled,
  configerrors), the file poll second, the log only as corroboration.

### 4d. Runner: teardown copies the marker file out (evidence survives rm -rf)

```diff
--- a/improvements/worker-y6b-run-nested-wayland-v2.sh
+++ b/improvements/worker-y6b-run-nested-wayland-v2.sh
@@ -117,6 +117,11 @@ teardown() {
   # Copy the nested per-instance log out before removing the runtime dir (U7a).
   if [ "$NEST_STARTED" = "1" ] && [ -n "$SIG" ] && [ -d "$RUN_DIR/hypr/$SIG" ]; then
     cp -r "$RUN_DIR/hypr/$SIG" "$NEST/hypr-saved-$START_TS-$SIG" 2>/dev/null && echo "Y6-WAYLAND: nested log saved to $NEST/hypr-saved-$START_TS-$SIG" || echo "Y6-WAYLAND: WARN: nested log copy failed"
   fi
+  # Y6C5-A8-INVEST: copy the profile-applied marker file out too (same
+  # reason: RUN_DIR is removed below). Missing file is a warning only;
+  # the gate already failed closed on it during the run if it never appeared.
+  if [ "$NEST_STARTED" = "1" ] && [ -f "$RUN_DIR/y6-profile-applied.txt" ]; then
+    cp "$RUN_DIR/y6-profile-applied.txt" "$NEST/y6-profile-applied-$START_TS.txt" 2>/dev/null && echo "Y6-WAYLAND: profile marker file saved to $NEST/y6-profile-applied-$START_TS.txt" || echo "Y6-WAYLAND: WARN: profile marker file copy failed"
+  fi
```

### 4e. Runner: correct the R2 comment (the reload hypothesis is now tested and refuted)

```diff
--- a/improvements/worker-y6b-run-nested-wayland-v2.sh
+++ b/improvements/worker-y6b-run-nested-wayland-v2.sh
@@ -39,12 +39,14 @@
 # Y6C5-A7 (Y6r R2, adjudicated): DO NOT add a manual `nest hyprctl reload`
 # anywhere in this runner. Parse 2 already applies the profile
 # deterministically (redteam section 1.2: STAGE_LATE loads the plugin
 # synchronously and calls reload(), so parse 2 sees count=1 and dofiles
 # optics.lua), so a reload buys nothing and risks a parse-3 duplicate
 # layer() registration (open item O1, overwrite vs error unresolved) plus
 # live-touch surface (a wrong-target reload would hit the live session).
-# One application path only: the automatic parse-2 path (R8). If the
-# positive gate ever shows the applied marker absent, the reload becomes
-# the next hypothesis to test, not a preemptive addition. Enforced by
-# tests/test_y6c5_positive_gate.py (no non-comment `hyprctl reload` line).
+# One application path only: the automatic parse-2 path (R8). The reload
+# hypothesis was tested by the A8 trial (16:18 2026-11-22) and REFUTED as
+# the cause of an absent marker: the reload happens and the profile is
+# applied, but the marker prints never reach the log file (ofstream
+# buffering, see improvements/worker-click5-y6-a8-invest-log.md). A missing
+# marker therefore means a broken observation channel first, and a missing
+# reload only if the marker FILE is also absent. Enforced by
+# tests/test_y6c5_positive_gate.py (no non-comment `hyprctl reload` line).
```

### 4f. Tests: file-based gate cases (tests/test_y6c5_positive_gate.py)

- `run_gate_case` gains a marker-file argument: it creates a `run/`
  dir in the temp dir, writes the marker file there when content is
  given, and exports `RUN_DIR` in the stub prelude (the new gate reads
  `$RUN_DIR/y6-profile-applied.txt`). The log-content arguments stay,
  because the gate still greps the logs for the parse-1 expected check
  and for corroboration output.
- Cases to change or add (exact new expectations):
  - `test_a2_gate_exec_healthy_file`: marker file present, BOTH logs
    contain ONLY the parse-1 not-ready marker, layers.enabled true:
    must PASS with rc 0 and "profile gate OK". This is the A8 shape
    (the exact run that failed) and is the regression test for this
    investigation. Under the old gate it fails; under the new gate it
    passes.
  - `test_a2_gate_exec_healthy_stdout_log` and
    `test_a2_gate_exec_healthy_nest_log`: RETIRE both (the gate no
    longer passes on log markers). Replace with the file case above.
  - `test_a2_gate_exec_no_marker_fails`: marker file ABSENT, logs
    contain only the parse-1 marker, layers.enabled true: must FAIL
    with "marker file" in the output (updated fail string).
  - `test_a2_gate_exec_layers_false_fails`: marker file present,
    layers.enabled false: must FAIL with "layers.enabled is not true".
  - `test_a2_gate_exec_parse1_expected`: marker file present AND
    parse-1 marker in the logs: must PASS and log "expected, not a
    failure".
  - `test_a2_gate_present`: assert `"y6-profile-applied.txt" in block`
    and `"features.layers.enabled" in block`; assert the block does NOT
    contain `grep -a -q "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG"`
    (no log grep decides the gate); assert the fail string is the new
    `"marker file" ` wording, not the old `"applied marker absent"`.
  - `test_a10_live_log_only`: repurpose to the new rule: no non-comment
    line in the A2 block greps a log file for `Y6-NEST-OPTICS: applied`
    as a pass/fail decision; log greps in the block are only the
    parse-1 expected check and the corroboration output. Keep the
    `hypr-saved` ban.
  - `test_a3_markers`: add assertions that the hook writes the marker
    file AFTER the applied print: `"y6-profile-applied.txt" in hook`,
    `"io.open" in hook`, `"marker_file:close()" in hook`, and
    `hook.index('print("Y6-NEST-HOOK: profile applied")') < hook.index('y6-profile-applied.txt')`
    (file write after the print), plus `"XDG_RUNTIME_DIR" in hook`
    (nest run dir, never a hardcoded live path).
  - `main()` checks list: rename the two retired healthy-log cases to
    the file case, add the A8-shape case by name.
- The G4 exec cases, A5/A6/A7/A8 static checks, A4/A1 checks, and
  `bash -n` stay unchanged (the G4 block text is unchanged except its
  added comment line; the move itself is covered by the block
  extraction in the exec tests, which find the block by its BEGIN/END
  markers wherever it sits).

### 4g. A8 trial doc: measured items 1-2 redefined (improvements/worker-y6c5-a8-load-only-trial.md)

```diff
 ## What is measured (all must hold; the trial FAILS otherwise)

-1. Positive marker: `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55
-   mask=contour namespace=computer-use-indicator` present in the LIVE
-   per-instance log ($NEST_LOG) before the liquid gate. First amended run
-   must show it or stop (Council 1 item 6).
-2. Hook corroboration: `Y6-NEST-HOOK: profile applied` present in the logs.
-   Parse-1 `not ready` marker present is EXPECTED, not a failure.
+1. Positive marker: `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55
+   mask=contour namespace=computer-use-indicator` present in the marker
+   FILE ($RUN_DIR/y6-profile-applied.txt, copied out at teardown to
+   $NEST/y6-profile-applied-<timestamp>.txt) before the liquid gate.
+   The LIVE per-instance log ($NEST_LOG) is NOT the channel for this
+   signal: the A8 trial of 16:18 2026-11-22 proved the log file stops
+   flushing after the dmabuf dump, so a log grep cannot observe it
+   (see improvements/worker-click5-y6-a8-invest-log.md). First amended
+   run must show the file or stop (Council 1 item 6).
+2. Hook corroboration: `Y6-NEST-HOOK: profile applied` present in the
+   marker FILE. Log lines are corroboration only; their absence from the
+   logs is NOT a failure. Parse-1 `not ready` marker present is
+   EXPECTED, not a failure.
 3. Second signal: features.layers.enabled == true in the nested hyprglass
    status JSON (re-checked after the marker).
```
- And in the same doc, observation item "Marker counts" gains one line:
  `The marker file is the verdict signal; do NOT count markers in saved
  logs as parse evidence (A10), and do NOT fail on their absence.`

### 4h. What this fix deliberately does NOT change

- No change to the profile path: conf, optics table, config() call,
  layer() call, plugin load order, and the automatic parse-2 path are
  all proven working and stay untouched. No manual reload is added
  (A7/R2 stands, now with the refuted-hypothesis note in 4e).
- No timeout extension: the 15 s poll stays, because the file appears
  synchronously at parse 2 (about 10 s after launch the file is already
  written in a healthy run); the poll is a scheduling margin.
- No change to the pill, arms, backdrop, or liquid gate: the trial
  stays load-only and the measurement retry stays gated.

## 5. Re-review required before ANY re-run (per the trial procedure, it does apply)

- YES, a fresh re-review is required before any re-run of the trial.
  The fix diff in section 4 goes back to re-review, and no re-run
  (trial or measurement) runs before the re-review clears it. What the
  re-review must check, in order:
  1. The hook file write is actually delivered: `io.open` with mode
     `"w"`, both lines written, explicit `close()` before the branch
     ends, no pcall swallowing a dofile error, no path that could ever
     resolve to the live runtime dir (must be XDG_RUNTIME_DIR from the
     nest environment, fallback the nest run dir only). The hook must
     still print AFTER the dofile returns (A3 ordering preserved).
  2. The gate polls the FILE and nothing else decides the pass: no
     non-comment line in the A2 block greps a log file for the applied
     marker as a pass/fail condition; the layers.enabled check runs
     first; the fail string names the file, not the log; the log greps
     are corroboration output only.
  3. G4 ordering: the moved G4 block sits BEFORE the A2 block, its
     BEGIN/END markers are intact, and the test extraction still finds
     it. A throwing config() must fail at G4 with its error text.
  4. Teardown copy-out: the marker file is copied to
     `$NEST/y6-profile-applied-<timestamp>.txt` before `rm -rf
     "$RUN_DIR"`, and a missing file there warns instead of failing the
     teardown (the gate already failed closed during the run).
  5. No live-touch: every new path is under /tmp/y6-nested (nest-only);
     no new `hyprctl reload`, no live config write, no live plugin
     load. The A7 no-reload assertion still holds (run the test suite).
  6. The test suite passes on the patched files (`python3
     tests/test_y6c5_positive_gate.py`, all checks PASS, including the
     new A8-shape case: marker file present, both logs containing only
     the parse-1 marker, layers.enabled true, must PASS) and `bash -n`
     passes on the runner.
  7. The staged files are re-staged from the repo copies after the
     re-review GO (hook md5 changes by this fix; conf and optics md5s
     are unchanged: conf 9ccb2701, optics 85298d20) with backups and
     md5 verification, per the paper lane section 4 procedure. The
     trial preconditions (live baseline re-verified at launch, no live
     lane loading/unloading during the window) still apply unchanged.
  8. The re-review re-checks the cause in section 1 against the trial
     evidence (it must agree the FAIL was a false fail, or state
     exactly which proof link it disputes, with its own evidence).
- The pill measurement retry is NOT cleared by this investigation. It
  stays gated on (a) the A8 trial passing all 7 items under the fixed
  gate, and (b) a fresh re-review of that trial evidence.

## 6. Diagnostic run: NOT needed to name the cause

- The existing evidence is sufficient to name the cause (proof chain
  L1-L6, no missing link). No new diagnostic run is needed before the
  fix, and this lane ran none (per the brief).
- The confirmatory observation belongs to the re-run itself, after the
  re-review clears the fix: the re-run must show (a) the marker file
  `$RUN_DIR/y6-profile-applied.txt` present with both lines, (b) the
  copied-out `$NEST/y6-profile-applied-<timestamp>.txt` in the evidence,
  (c) `nest hyprctl configerrors` empty (G4, now before the gate), and
  (d) the log files still missing the applied marker (expected: the log
  delivery lag is unchanged by the fix, and the gate no longer depends
  on it). If (a) is absent while layers.enabled is true, the cause is
  NOT what section 1 names, and the trial stops for a new investigation
  instead of a retry. If (a) is present, the A8 trial passes item 1-2
  under the fixed gate.

## 7. Evidence index (files, md5s, commands)

- Trial log: improvements/worker-click5-y6-a8-trial-log.md (FAIL item 1,
  7 items, preconditions, evidence md5s in its section 5).
- Verbatim run log:
  improvements/y6c5-evidence/a8-trial-run-20261122-161803.log, 77 lines,
  md5 721cb67c5b2947639236b89a706fad36. FAIL line 67 (shares its line
  with the truncated dump line). Gate lines 35-37, status JSON lines
  17-26, teardown 16:18:27 to 16:18:29.
- Nested per-instance log (laptop):
  /tmp/y6-nested/hypr-saved-20261122-161803-11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795339084_327326060/hyprland.log,
  188 lines, 16470 bytes, md5 b8832e82500fdfce62d49e2a2b0a7783.
  Marker line 15 only. Last line truncated, no trailing newline.
- Stdout log (laptop): /tmp/y6-nested/hyprland-wayland.log, 62 lines,
  md5 a940682021b9bbad0f7ace90a1d52487. Marker line 50 only. Line 1
  confirms the staged conf path. Line 51 is the postConfigReload
  stdout-disable line.
- Status JSON (laptop): /tmp/y6-nested/nest-glass-status.json, md5
  5d868d0975a66784a6a56119614843e1. layers enabled true, active true,
  shaders pending, version 1.1.1-cu.1, versionCheck match.
- Plugin list (laptop): /tmp/y6-nested/nest-plugin-list.json, md5
  de7d2aebcfe9b0553e4e4b7af101fb11. Only hyprglass 1.1.1-cu.1.
- Live plugin lists before/after (laptop): both md5
  cf91d826447b1cdae7fe662b288c5611 (identical, item 6 PASS).
- Staged files (laptop /tmp/y6-nested/conf/, md5 re-verified by this
  lane): hyprland-wayland.lua 9ccb27017ab63a9d2bce1d9651425d3b (19 lines:
  line 16 plugin.load, line 18 dofile hook),
  nested-visuals-hook.lua 6dd68aeadbe7e1c9049436dc7361ee7a (line 30
  applied print), optics.lua 85298d2035697710d95117355c9830ca (line 47
  applied print, last line).
- Hyprglass worktree source (laptop, read directly):
  ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/src/PluginConfig.cpp
  lines 83 (default false), 226-227 (Lua entry points), 322
  (layersEnabled pointer), 630-652 (forwardLuaConfig), 654-671
  (handleLuaConfig), 823-931 (handleLuaLayer, reports-only);
  src/PluginConfig.hpp:126 (LAYERS_ENABLED key), :383 (declaration);
  src/Diagnostics.cpp:414 (featureStatus call site).
  No other setter of the registered layers value exists in src/
  (grep for assignments finds only the getStaticPtr read).
- Hyprland 0.57.2 source (laptop, read directly):
  ~/backups/omarchy-native-port-20261113/Hyprland-0.57.2/src/
  Compositor.cpp (STAGE_LATE PluginSystem + handlePluginLoads),
  config/lua/ConfigManager.cpp:820 (handlePluginLoads in
  postConfigReload, stdout-disable logged only on first launch),
  :1093-1104 (handlePluginLoads body, reload if pluginsChanged),
  plugins/PluginSystem.cpp:131 and :189 (doLater reload), :197-240
  (updateConfigPlugins, changed=true before load returns),
  config/lua/bindings/LuaBindingsConfigRules.cpp:562 (load records
  path only), config/lua/bindings/LuaBindingsToplevel.cpp:270-296
  (hlGetPlugins early empty table).
- Optics identity proofs (laptop, read-only):
  `diff /tmp/y6-nested/conf/optics.lua.bak-y6c5-20261122 /tmp/y6-nested/conf/optics.lua`
  shows ONLY the A3 comment block and the print line 47 as additions.
  Live optics file
  ~/.local/share/agent-computer-use/native/hyprglass-local-optics.lua
  has the identical table and calls (blur 0.15, tint 0xffffff00).
- Err files (laptop): /tmp/y6-nested/nest-glass-status.err and
  nest-plugin-list.err, both 0 bytes (hyprctl calls clean).
- Runner: improvements/worker-y6b-run-nested-wayland-v2.sh, md5
  b50396bf1c68c1e047733b2a5b24f35a (per the trial log; gate lines
  387-450, G4 lines 452-470, teardown lines 116-130, header lines 1-70).
- Paper log: improvements/worker-click5-y6-paper-log.md (M1/M2/M3,
  section 5 re-review, section 4 staging record).
- Redteam: improvements/worker-y6r-redteam.md (section 1.2 mechanism,
  section 2a buffering, P2/P4/P8).
- Y6e log: improvements/worker-y6e-rebuild-load-log.md lines 555-600
  (21:57 run: same status shape, same 188-line frozen log, same single
  parse-1 marker; load-test script never queried configerrors).
- Commands run by this lane (all read-only, VM or ssh-laptop.sh):
  full cat of the nested log; cat -n of the staged conf, stdout log,
  status, plugin list; md5sum of all six evidence files; grep/sed of
  the worktree PluginConfig.cpp and Diagnostics.cpp; diff of old vs
  new optics; cat of the live optics file; bounded find for
  Compositor.cpp; sed/grep of the Hyprland 0.57.2 source files above;
  grep -n of the runner, the verbatim run log, and the Y6e log.

## 8. Handover to the coordinator

- Investigation verdict: FALSE FAIL. Named cause: the A2 gate greps a
  log file that stops flushing after the dmabuf dump, so the applied
  markers (which executed in-process on parse 2, proven by
  layers.enabled true against a default of false) never reach the file
  within the run. The profile was applied; the observation channel was
  broken. Full proof chain in section 1, ruled-out hypotheses in
  section 2.
- Fix proposed in section 4 (patch text only, NOT applied): hook writes
  the marker to a closed file in the nest run dir; the gate polls the
  file; layers.enabled and G4 (IPC) run first; log greps become
  corroboration only; teardown copies the file out; R2 comment records
  the refuted reload hypothesis; tests gain the A8-shape regression
  case; the A8 doc redefines items 1-2.
- Re-review REQUIRED before any re-run (section 5 checklist). The pill
  measurement retry stays gated.
- No fix applied, no trial re-run, no live touch by this lane. Live
  untouched throughout (no laptop writes except none; all laptop reads
  were read-only via ssh-laptop.sh).
- Commit record: 9065419 (Sun 2026-11-22 16:33 +07, T+11m). 1 file,
  834 insertions: improvements/worker-click5-y6-a8-invest-log.md (this
  log). Explicit pathspec only; other workers' uncommitted changes
  untouched. Push verified: ls-remote shows the commit as HEAD (see
  verification in the coordinator report).

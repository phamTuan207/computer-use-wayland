# Worker Y6r redteam: adversarial review of the Y6d launcher v3 + Y6e rebuild/load-test diff

- Reviewer: redteam (independent, adversarial). Parent: Y6r.
- Date: Sat 2026-11-21, 22:04-22:35 +07. Repo ~/workspace/computer-use-wayland, branch todolist-push.
- Scope: Y6d (72eb8ad) + Y6e (915121d) against the Y6c findings, ruling whether the pill measurement retry may proceed.
- Constraints honored: no code, conf, or runner modifications; no nested Hyprland launch; no live Hyprland PID 1515, vkms, or laptop-repo writes; read-only laptop reads via ~/workspace/ssh-laptop.sh; no ydotool; no em/en dash; no personal info.
- Method: every claim below is either source-proven (Hyprland v0.57.2 tag 11cbc6c57, hyprglass worktree 03a57c4, repo files) or mechanically reproduced (command + output in the appendix). Where the redteam tried and failed to break a claim, that is stated.

## Verdict: AMEND

The retry may NOT proceed as-is, for two independent deterministic reasons. Neither is a blocker: both fixes are small and specified in section 5.

1. Wrong conf staged. The runner's conf on the laptop is still the v2/v3 backup-1 conf (md5 0d4ac7a9, dead ABI). The retry as-is dies at the ldd pre-flight, before U6.
2. U6 is a false fail. The gate trips on the first-parse "not ready" marker, which is a permanent artifact of every successful startup, including runs where the profile IS applied. The profile WAS applied in the Y6e run (proof in section 1.4).

Headline reversal vs Y6r's preliminary read: Y6r's consequence is right (the retry deterministically fails at U6) but its mechanism is inverted. The marker does NOT prove the profile is missing. By the source-proven startup sequence the profile is applied on the second config parse, and Y6e's own status output proves it (layers.enabled=true against a default of false). The gate's diagnosis ("hook ran before plugin load (profile not applied)") is false for a successful load. The fix is therefore NOT "make the hook run after the load" (it already does) but "replace the negative marker gate with a positive applied check".

## 1. Attack on the determinism claim

Y6r's preliminary read: the hook can never see count=1 at config time, so the retry deterministically fails at U6 because the profile is not applied. Redteam refutes the first half and re-grounds the second half.

### 1.1 Parse 1: the hook CANNOT see the plugin. Proven, no window.

Source chain, stock Hyprland v0.57.2 (tag 11cbc6c57, same hash family as the live session signature):

- `hl.plugin.load(path)` does not load anything. `src/config/lua/bindings/LuaBindingsConfigRules.cpp:562`: `mgr->m_registeredPlugins.emplace_back(path);` and returns. It only records the path.
- `hl.get_loaded_plugins()` returns only plugins that finished loading. `src/config/lua/bindings/LuaBindingsToplevel.cpp:270-296` (`hlGetPlugins`): if `!g_pPluginSystem`, it returns an empty table immediately; otherwise it returns `g_pPluginSystem->getAllPlugins()`.
- Parse 1 runs before the plugin system exists. `src/Compositor.cpp`, `initManagers(STAGE_PRIORITY)`: "Creating the ConfigManager!" (line 677) then `Config::mgr()->init()` (same block), which calls `reload()`, which executes the Lua config. The plugin system is created later, in `initManagers(STAGE_LATE)`: "Creating the PluginSystem!" (line 748), `g_pPluginSystem = makeUnique<CPluginSystem>();` (line 749).
- So on parse 1, `hl.get_loaded_plugins()` returns an empty table by the early-return branch. count=0, version=nil, deterministically. There is no race: the load has not even been requested yet, and the registry the hook reads does not exist yet.
- `handlePluginLoads()` on parse 1 is a no-op: `src/config/lua/ConfigManager.cpp:1093-1096`, `if (!g_pPluginSystem) return;`. No load is started, no nested reload is triggered.
- Observed twice, consistent: Y6c probe 2 (dead-ABI plugin) and Y6e (loadable plugin) both show `Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)` at line 15 of the per-instance log, before the `postConfigReload` stdout-disable line at line 16.

Attack attempts that failed: synchronous load (refuted by the load function above, it only records); warm cache (irrelevant, fresh process per run, no cache); a second config parse (see 1.2, it DOES see count=1, but it is a later parse, not parse 1).

### 1.2 Parse 2: the hook DOES see count=1. This is the counterexample window, and it fires automatically on every startup.

- `STAGE_LATE`: after the plugin system is created, `Config::mgr()->handlePluginLoads();` runs (`src/Compositor.cpp:750`).
- `handlePluginLoads()` (`src/config/lua/ConfigManager.cpp:1093-1104`) calls `g_pPluginSystem->updateConfigPlugins(m_registeredPlugins, pluginsChanged)`, and if `pluginsChanged` it calls `reload()`.
- `updateConfigPlugins()` (`src/plugins/PluginSystem.cpp:197-240`) starts the load with `loadPlugin(path, SPECIAL_PID_TYPE_CONFIG)->then(...)` and sets `changed = true` before the load returns.
- `loadPlugin()` is fully synchronous. `src/helpers/defer/Promise.hpp`: `CPromise::make()` invokes the executor function immediately in the calling thread, and `then()` fires immediately when the result is already set. No thread, no event loop, no deferral.
- The permission check cannot pend. `loadPlugin()` calls `clientPermissionModeWithString(SPECIAL_PID_TYPE_CONFIG, ...)`, and `src/managers/permissions/DynamicPermissionManager.cpp:152-157` returns `PERMISSION_RULE_ALLOW_MODE_ALLOW` when `ecosystem:enforce_permissions` is 0, which is the default and is not set by the nest conf. No prompt, no wait.
- `loadPluginInternal()` (`src/plugins/PluginSystem.cpp:67-140`) adds the plugin to `m_loadedPlugins` BEFORE `dlopen`, pops it on failure, and on success schedules one more reload with `g_pEventLoopManager->doLater([] { Config::mgr()->reload(); });`.
- Therefore, by the time `updateConfigPlugins` returns, a loadable plugin IS in `m_loadedPlugins`. `handlePluginLoads` then calls `reload()` synchronously. Parse 2 executes the config again: `reregisterLuaPluginFns()` runs first (so `hl.plugin.hyprglass` exists), then the hook runs and `hl.get_loaded_plugins()` returns the plugin, count=1, version 1.1.1-cu.1. The hook takes the success branch and dofiles optics.lua. The profile is applied, silently (the success branch prints nothing).
- Parse 2's `postConfigReload` calls `updateConfigPlugins` again, which early-returns (`m_lastConfigPlugins == plugins`), so no further reload from that path. The event loop later runs the `doLater(reload)` from `loadPluginInternal`, giving parse 3, where the hook again sees count=1 and re-applies optics (idempotent re-application).
- The wiki's own plugin FAQ confirms this shape: it shows `hl.plugin.load(...)` followed by an `if is_plugin_loaded(...)` check, with the comment that the `if` is there so the config does not error "if the plugin is not loaded yet". The check is false on parse 1 and true on parse 2, which is exactly why the pattern works.

### 1.3 Manual reload: also sees count=1.

A later `hyprctl reload` re-executes the Lua config (`reload()` runs the config file through a guarded call). The plugin is already in `m_loadedPlugins`, `updateConfigPlugins` dedups by path and skips re-loading, and `loadPluginInternal` independently refuses a double load ("Cannot load a plugin twice!"). So a manual post-load reload also applies the profile. This window is real but redundant, because parse 2 already applies it (section 1.2).

### 1.4 Empirical proof the profile WAS applied in the Y6e run.

- The plugin default for the layers feature is false: hyprglass worktree 03a57c4, `src/PluginConfig.cpp:83`: `addConfigValue<Config::Values::Bool>(handle, ConfigKeys::LAYERS_ENABLED, false);`.
- Y6e's nested status output (improvements/worker-y6e-rebuild-load-log.md:560) reports `features layers enabled true active true`.
- The only setter of `layers.enabled` in the nest is optics.lua's `hl.plugin.hyprglass.config(config)` with `layers = { enabled = true, ... }`. The nest conf contains no `hl.config` call, and the pill only calls `show`. Therefore optics.lua executed in the Y6e run. The profile WAS applied.
- Corroboration: the optics keys are all accepted by the 03a57c4 build (`blur_strength`, `refraction_strength` at PluginConfig.cpp:413-415; `mask_mode` "contour" at :40 and :896-902), and the Lua entry points exist (`HyprlandAPI::addLuaFunction(handle, "hyprglass", "layer", ...)` and `"config"` at PluginConfig.cpp:226-227). The parse-2 dofile had no reason to error.
- Consequence: Y6e rebuild-load-log.md:561 ("the profile was not applied in this run") and Y6r's V4/V5 ("profile NOT applied") are wrong and must be corrected in the adjudication. The Y6e load verdict (LOADED) is unaffected; the hook note is what is wrong.

### 1.5 What survives of the determinism claim.

- "The hook can never see count=1 at config time": REFUTED. Parse 2 and parse 3 and any manual post-load reload all see count=1.
- "The retry as-written deterministically fails at U6": SURVIVES, but for the opposite reason. U6 fails because the parse-1 marker is always in the log, not because the profile is missing. The failure is a false fail, and its diagnosis string is false.

## 2. Attack on the gates

### 2a. Could the U6 grep MISS the marker?

Gate text, runner lines 298-305:

```
# Hook marker check (U6): if the hook ran before the plugin loaded, the
# profile was never applied. Fail fast with that diagnosis. ...
if grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG" 2>/dev/null; then
  fail "hook ran before plugin load (profile not applied); see nested log"
fi
echo "Y6-WAYLAND: hook marker absent, profile applied"
```

Miss modes tested:

- Marker in a different log file: no. The marker is printed on parse 1, before `postConfigReload` disables stdout logging, so it lands in BOTH the stdout log ($LOG) and the per-instance log ($NEST_LOG). Mechanical proof: probe2 stdout log line 50 and per-instance log line 15 both contain it; Y6e saved per-instance log line 15 contains it.
- `$NEST_LOG` undefined at that point: no. It is defined at runner line 225, right after signature discovery, and its existence is asserted at the backend gate before U6 runs.
- Binary log / grep -a: the gate already uses `-a`, and the logs are text. No miss here.
- Log rotation: no file rotation applies. The in-memory rolling log in hyprutils is capped at 4096 bytes, but that is not the file; the per-instance file is an `std::ofstream` with no size cap in the code read.
- Log buffering (the one real subtlety): the file write is NOT flushed per line. hyprutils `src/cli/Logger.cpp`: stdout gets `std::fflush(stdout)` after every line, but the file gets only `m_logOfs << logPrefix << logMsg << "\n";` with no flush. So the on-disk file lags the process output by up to one stream buffer. For the marker this does not create a miss in practice: hundreds of later lines (the Aquamarine format dump) force buffer flushes long before U6 runs (about 10s after launch). Mechanical proof: the marker IS in the saved Y6e log and in the probe2 stdout log. The buffering DOES destroy post-hoc forensics: both saved per-instance logs (Y6c probe2 and Y6e) are exactly 188 lines ending mid-Aquamarine-dump, with no PluginSystem creation, no "Loading plugin", and no parse-2/3 lines, because the tail sat in the buffer and died with the SIGKILL teardown. Marker COUNTS from saved logs are therefore not evidence of parse counts. The U6 gate itself greps the live file during the run, so it is unaffected by the teardown loss, but no one may infer "the hook ran once" from a saved log.
- The real U6 defect is the opposite of a miss: it CANNOT miss the parse-1 marker, so it false-fails every successful run. Its `echo "hook marker absent, profile applied"` (line 305) is also wrong as a positive claim: marker absence would not prove application either.
- Unverified-file gap: the runner never pins md5s for CONF, HOOK, or OPTICS (a grep for md5/sha256 in the runner returns nothing; it only checks `test -f` at line 143). If the hook were edited to drop the print, U6 would pass vacuously. The gate's protection depends on files it never verifies.

### 2b. Could the liquid gate PASS without the profile?

Yes. Proven by reading the gate and the status producer.

- `scripts/indicator.py:210-240` (`_valid_liquid`): requires schema==1 (int, not bool), version 1.1.1-cu.1, versionCheck "match", active True, shaders in ("ready", "pending") (and "ready" when ready=True), features dicts for layers/windows/subsurface, layers.enabled True, layers.active True, layers.reason present and None, windows.enabled False, subsurfaces.enabled False. Nothing about the optics profile, the blur/refraction values, or the "computer-use-indicator" layer registration.
- `hyprglass status` cannot report the profile anyway. `src/Diagnostics.cpp`, `formatStatus`: the JSON is schema, version, versionCheck, active, shaders, itemProtocol, features{windows, layers, subsurfaces}. The layers feature status is `config.layersEnabled` plus `renderLayerHook != nullptr`: it says the layers FEATURE is on, not that any namespace is registered or what values were set. No per-layer list, no config hash exists in the status contract.
- The hook's own comment ("The runner checks liquid_available(ready=true) after start; a missing profile is NO-GO") is false and must be corrected when the hook is next edited. The indicator.py docstring says it plainly: "It is not proof that any pixel is drawn, that the optics look right, or that our indicator namespace is glassed."
- Agrees with Y6r V9; this is an independent confirmation from the source, not a new finding.

### 2c. Could the retry produce a FALSE pill verdict?

Four sub-attacks, three live, one dormant:

- Wrong conf staged: LIVE. `/tmp/y6-nested/conf/hyprland-wayland.lua` on the laptop is md5 0d4ac7a9, the v2/v3 backup-1 conf; the y6e conf (md5 9ccb27017ab63a9d2bce1d9651425d3b) sits as a separate file `hyprland-wayland-y6e.lua`. The retry as-is fails at the ldd pre-flight (runner lines 156-162) on the dead ABI, fail-closed with the correct diagnosis. The staging step (copy + md5 verify) exists in no script. Mechanical proof: the exact pre-flight grep run on the laptop returns the backup-1 path for the staged conf and the worktree path for the y6e conf.
- Grep-first-path trap: DORMANT on the y6e conf. The y6e conf contains no `.so` path in any comment before line 16; the first match is the line-16 load path (verified mechanically, same command as above). The trap did fire once before (a comment), and the y6e conf's line-8 comment warns against it. The trap is not live, but the runner still has no defense beyond that comment.
- Stale marker from a previous run: NO. `$LOG` is truncated at launch (`> "$LOG"`), and `$NEST_LOG` lives under a fresh `$RUN_DIR/hypr` (rm -rf before launch). The marker that trips U6 is from the CURRENT run's parse 1, not a stale run. The fix is therefore not "clear stale logs" but "stop treating the parse-1 marker as failure".
- Partial profile application, and the pill with no glass: LIVE as a residual path. If optics.lua's `config()` threw on parse 2 (a future key mismatch would do it; `handleLuaConfig` raises Lua errors on bad input), the `layer()` call would never run, the profile would be half applied, and NO gate would catch it: U6 looks only for the parse-1 "not ready" marker (absent on the parse-2 success path), the liquid gate is blind (2b), and the pill script (`improvements/worker-y6b-run-nested-pill-v2.py`) never checks glass, it only calls `show` and prints ready. The arms would then run against an unglassed pill and could only produce a false-negative NOT reproduced (no glass to flicker in arm A; arm B pill-only diffs would come from transparent margins showing the moving backdrop, or zero if the pill background is opaque without glass) or VOID. Neither verdict would test hypothesis H-E. This is the exact false-verdict mechanism the amended U6 must close: the positive applied signal must be printed AFTER the dofile returns, so a dofile error means no signal and a correct fail.

## 3. Attack on the fix candidates

### 3a. Runner-side `nest hyprctl reload` after the plugin check.

- Does reload re-execute the Lua config in 0.57.2? YES. `reload()` re-runs the config file through a guarded call (`src/config/lua/ConfigManager.cpp:609` onward), and 0.57 added `hl.reload_config()` as well. The wiki documents `hyprctl reload` as re-running the config.
- Would the old marker still trip U6? YES, deterministically. The marker is already in `$LOG` and `$NEST_LOG` from parse 1, and a reload does not erase log lines. U6 greps the whole files. Mechanical proof: the marker is present in the saved Y6e log (1 match, line 15) independent of any later reload. Reload-alone changes nothing about the U6 outcome.
- Is the reload even needed? NO. Parse 2 already applies the profile (section 1.2). A manual reload would only re-apply it. Adding it buys nothing and adds a live-touch surface.
- Failure modes if it is added anyway: (i) U6 still fails (shown above), so the reload must be paired with the U6 change in section 5, otherwise it is pure churn; (ii) reload re-executes `hl.monitor` and `hl.plugin.load` (harmless: monitor re-applied, load deduped by path, double-load independently refused with an error, not a double dlopen); (iii) if the nest died before the reload, `nest hyprctl` fails fail-closed, which is good; (iv) live-touch risk is LOW but not zero: `nest()` fails closed on empty `NEST_DISPLAY`, and `SIG` comes from the nest-only `$RUN_DIR/hypr` directory, so the live signature cannot be selected by that path; a stale directory surviving the pre-launch rm -rf is the remaining theoretical vector, and a `kill -0` re-check of `NEST_HYPRLAND_PID` before the reload would close it; (v) parse-3 duplicate `layer()` registration for the same namespace is an open question (overwrite vs error, not resolved from the code read); if it errors, parse 3 logs a config error but the parse-2 profile stands.

### 3b. Hook-side poll/retry (can Lua config block?).

- A busy-wait or sleep inside the config thread CANNOT work. The plugin load is triggered by `postConfigReload`, which runs only after the config execution (guarded call) returns, and the config call has a timeout (`LUA_TIMEOUT_CONFIG_RELOAD_MS`). A spin-wait would block the very load it waits for and trip the timeout. There is no sleep binding in the hl API (verified by grep over the bindings).
- The correct hook-side primitive is `hl.timer`, and it exists: `src/config/lua/bindings/LuaBindingsToplevel.cpp:412-474`. `hl.timer(fn, {timeout = ms, type = "oneshot"|"repeat"})` registers a `CEventLoopTimer` that fires the Lua callback on the event loop, after the config returns. A oneshot timer that re-checks `hl.get_loaded_plugins()` and dofiles optics when the plugin appears would work in principle.
- Failure modes of the timer path: (i) `reload()` phase 2 calls `cleanTimers()`, so a timer registered on parse 1 is cancelled by parse 2's reload before it fires; the timer must be re-registered on every parse, or the check must live in the last parse's timer; (ii) a timeout shorter than the load delay fires while count is still 0 and does nothing, so the timer needs its own retry or a generous delay; (iii) it is unnecessary: parse 2 already applies the profile, so the timer is belt-and-braces, not the required fix. The minimal hook-side fix is the success marker in section 5, not a timer.

### 3c. Applying optics via hyprctl.

- DEAD. `hyprctl hyprglass` accepts only `status|stats [reset]|items` (`src/Diagnostics.cpp:589`). No config, reload, or load subcommand exists. No hyprctl path applies the profile.
- `items` is not a verification substitute either: it lists subsurface protocol items only (`src/Diagnostics.cpp:200-245`, "no active subsurface glass items"), not layer namespaces. The pill is a layer surface, so `items` cannot confirm the "computer-use-indicator" registration.

## 4. Attack on the load-test scope

Y6e's load-test script (`improvements/worker-y6e-nested-load-test.sh`, 288 lines) is NOT the v3 runner. It stops after the plugin status check. Line-by-line comparison against the v3 runner (`improvements/worker-y6b-run-nested-wayland-v2.sh`, 564 lines):

Executed live against a real nest (same code, verbatim shape): ldd pre-flight (but against the y6e conf, not the runner's CONF, so the runner file's own ldd block never ran; the logic is proven, the integration is not); live identity resolution (U15); runner-quiet process check, flock, mpv/foot pre-check; launch via setsid/timeout/pidfile; 15s signature wait; U5b backend gate with 10s retry; kill -0 nest liveness; F0 socket discovery with connect probe and ambiguity fail; monitors query; plugin-list gate; status gate with version parse.

Never executed live against a real nest: the U6 gate AS A GATE (the load test only notes the marker, non-gating; the note itself proves U6 would have failed); the liquid gate (60s `liquid_available(ready=True)` loop); the renderer-lines grep; the backdrop mpv launch and PID checks; the positive control (two grim frames must differ); the deadline and idle checks; the pill launch and 45s ready wait; `read_pill_geom`, the bounds check, and the backdrop-geometry computation; arm A and arm B capture/compare loops; the motion re-validation; the pill re-baseline before arm B; every verdict branch; the runner's file-presence preconditions for HOOK, OPTICS, BACKDROP, BACKDROP_STATIC, and PILL (the load test checks CONF only); the teardown's pill/mpv kill and live-plugin re-verify with a hyprbars-only assertion (the load-test teardown prints the after list but does not assert hyprbars-only, and lacks the native/indicator stray check).

Divergence (safety guards the load test had that the v3 runner lacks): the load test enforces AMEND4 (HYPRGLASS_SKIP_VERSION_CHECK unset) and AMEND5 (live-config no-hyprglass-load-path walk, plus live plugin list before/after identity). The v3 runner enforces NEITHER. A retry using the v3 runner would run without the live-safety guards the load test relied on. That gap must be closed before the retry (section 5, A5).

## 5. Amend list: exactly what must change first

- A1. Stage the y6e conf. Copy `/tmp/y6-nested/conf/hyprland-wayland-y6e.lua` over `/tmp/y6-nested/conf/hyprland-wayland.lua` on the laptop and verify md5 `9ccb27017ab63a9d2bce1d9651425d3b` after the copy. Without this the retry dies at the ldd pre-flight.
- A2. Replace U6 (runner lines 298-305) with a positive profile-applied check. (i) The hook prints `Y6-NEST-HOOK: profile applied` on the success branch AFTER the dofile returns, so a dofile error means no signal. (ii) U6 requires that marker present in `$LOG` or `$NEST_LOG` and fails if it is absent. (iii) The parse-1 "not ready" marker is EXPECTED and must not fail the run; delete the current fail-on-not-ready rule. (iv) Add a second positive signal: require `features.layers.enabled == true` in the parsed status JSON, since optics sets it from the plugin default of false (section 1.4). Both signals together observe the print and the effect.
- A3. Correct the record. Y6e rebuild-load-log.md:561 and Y6r V4/V5 state the profile was not applied; it was. Correct them in the re-review adjudication, and reword the runner's U6 fail string (line 303) when A2 lands, since "hook ran before plugin load (profile not applied)" is false for a successful load.
- A4. Correct the hook comment claiming `liquid_available` catches a missing profile. It does not (indicator.py docstring). Correct it when the hook is next edited so the next reader does not re-trust the liquid gate.
- A5. Port AMEND4 and AMEND5 into the v3 runner (or the run procedure) before the retry: the HYPRGLASS_SKIP_VERSION_CHECK unset check, the live-config no-hyprglass-load-path walk, and the live plugin list before/after identity check.
- A6. Do not use saved-log marker counts as parse-count evidence (ofstream buffering, tail lost on SIGKILL; section 2a). If parse counts matter, have the hook print the parse number, or rely on the applied marker from A2.
- A7. Do NOT add a manual `nest hyprctl reload`. Parse 2 already applies the profile; the reload is redundant and adds a live-touch surface for no benefit. If it is added anyway, it must be preceded by a `kill -0` re-check of `NEST_HYPRLAND_PID` and paired with A2.

## 6. Open items (not verdict drivers)

- O1. Duplicate `layer()` registration on parse 3 (overwrite vs error) is unresolved from the code read. If it errors, parse 3 logs a config error but the parse-2 profile stands. Watch for it in the retry log.
- O2. The exact emission point of the `hyprland.start` event was not pinned down. It is not needed for the verdict, since the event-driven fix is not required.
- O3. The pill arms have never run live. The first amended retry is their proof.
- O4. SSH to the laptop flapped twice during this review (banner timeout, then tailscale-proxy closed) before recovering. Future verifiers should retry rather than conclude the laptop is down.

## Appendix: mechanical proofs (commands + outputs)

- P1. Staged conf is backup 1; y6e conf is the worktree path.
  Command (laptop): `for c in /tmp/y6-nested/conf/hyprland-wayland.lua /tmp/y6-nested/conf/hyprland-wayland-y6e.lua; do grep -o '/[^"]*hyprglass[^"]*\.so' $c | head -1; done`
  Output: `~/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so` then `~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so`.
  Also: `md5sum` on the laptop gives `0d4ac7a9c2437fb48ecfc505ccd9046b` for the staged conf (matches the repo v2 conf) and `9ccb27017ab63a9d2bce1d9651425d3b` for the y6e conf.
- P2. Marker present in the Y6e saved nested log, exactly once in the flushed prefix.
  Command (laptop): `grep -c 'Y6-NEST-HOOK' /tmp/y6-nested/hypr-saved-y6e-20261121-215707-*/hyprland.log`
  Output: `1`. Line 15 is the marker; the log is 188 lines ending mid-Aquamarine-dump (tail lost, section 2a).
- P3. Hook source (laptop, md5 9d68b2f54f920c6aec2351ab7abe27fc): success branch is a bare `dofile("/tmp/y6-nested/conf/optics.lua")` with no print; else branch prints the "not ready" marker. Optics (md5 b011ea91c3b831651f55fdd096d54c46) calls `hl.plugin.hyprglass.config(config)` with blur_strength 0.15 and registers layer "computer-use-indicator" with mask_mode "contour", guarded by `if hl.plugin.hyprglass then`.
- P4. Layers default false; Y6e status true.
  Source: worktree `src/PluginConfig.cpp:83`: `addConfigValue<Config::Values::Bool>(handle, ConfigKeys::LAYERS_ENABLED, false);`.
  Observed: rebuild-load-log.md:560 status shows `features layers enabled true active true`. Only optics.lua sets it. Therefore optics.lua ran.
- P5. No hyprctl config path.
  Source: worktree `src/Diagnostics.cpp:589`: `hyprctl hyprglass <status|stats [reset]|items>`. `items` lists subsurface items only (`src/Diagnostics.cpp:200-245`).
- P6. Liquid gate is metadata-only.
  Source: `scripts/indicator.py:210-253` (`_valid_liquid`, `liquid_available`); status producer `src/Diagnostics.cpp` `formatStatus` has no profile or layer-namespace fields.
- P7. U6 lines and the missing md5 pins.
  Command (repo): `grep -n "Y6-NEST-HOOK" improvements/worker-y6b-run-nested-wayland-v2.sh` gives lines 281, 302, 303, 305. `grep -n "md5\|sha256" improvements/worker-y6b-run-nested-wayland-v2.sh` gives nothing.
- P8. Hyprland source base: tag v0.57.2, `git ls-remote https://github.com/hyprwm/Hyprland.git v0.57.2` returns `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947`. The mechanism citations in section 1 are from that tag (sparse checkout of `src/config` and `src/plugins`, plus `git show` for `src/Compositor.cpp`, `src/plugins/PluginSystem.cpp`, `src/helpers/defer/Promise.hpp`, `src/managers/permissions/DynamicPermissionManager.cpp`, and hyprutils `src/cli/Logger.cpp`).

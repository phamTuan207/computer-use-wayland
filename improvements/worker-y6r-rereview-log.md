# Worker Y6r log: re-review of Y6d launcher v3 + Y6e rebuild/load-test diff (todolist 2.2.3 I11)

- Worker: Y6r (Muse independent re-reviewer). Branch: todolist-push.
- Scope: re-review the diff 72eb8ad (Y6d) + 915121d (Y6e) against the Y6c findings (F0, F1, U5b) and the C2 checklist; rule whether the pill measurement retry run may proceed. Council (3) + redteam over the diff. Review only + verification reads on the laptop that do not touch the live session.
- Constraints: no code/conf/runner modifications; no nested launch; no live Zen driving; never touch live PID 1515, vkms, or the laptop repo. No ydotool, no em/en dash, no personal info. Evidence contract: exact commands + outputs, timings, commit hash.
- Reviewers do NOT commit; Y6r adjudicates and commits everything together.

## Mechanical verification by Y6r (before spawning the council)

All checks run 22:01-22:05 +07 on Sat 2026-11-21. Repo ~/workspace/computer-use-wayland, branch todolist-push, HEAD 915121d verified via git log (72eb8ad and 915121d both present with the expected subjects).

### V1: rebuilt .so (F1 fix at the link level) - VERIFIED
- Command (via ~/workspace/ssh-laptop.sh): ls + md5sum + ldd on ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so.
- Output: 34,440,704 B, md5 78ac102337ca70842bf604b56c6f4c8e (matches Y6e's claim exactly); ldd "not found" count 0; libaquamarine.so.15 => /usr/lib/libaquamarine.so.15; libhyprgraphics.so.5 => /usr/lib/libhyprgraphics.so.5. The dead ABI (.so.14/.so.4) is gone at the link level. F1 is fixed.

### V2: conf diff vs v3 (exactly 2 lines) - VERIFIED
- Command (via ssh-laptop.sh): diff /tmp/y6-nested/conf/hyprland-wayland.lua /tmp/y6-nested/conf/hyprland-wayland-y6e.lua.
- Output: exactly 2 changed lines (line 8 comment, line 16 load path: backup 1 -> worktree hyprglass-03a57c4/hyprglass.so). diff exit code 1 is the expected "differences found", not an error.
- Repo copy improvements/worker-y6e-hyprland-wayland-rebuilt.lua md5 9ccb27017ab63a9d2bce1d9651425d3b (matches Y6e's claim).

### V3: nested load-test log (LOADED) - VERIFIED
- Command (via ssh-laptop.sh): grep of /tmp/y6-nested/y6e-load-20261121-215707.log for VERDICT / versionCheck / plugin list / live checks.
- Output lines seen: "Y6E-LOAD: AMEND4 OK", "AMEND5-BEFORE OK", "plugin ABI OK: .../worktrees/hyprglass-03a57c4/hyprglass.so", "live sig ... pid 1515", "hyprglass IS in the nested plugin list", '"name": "hyprglass"', '"schema": 1, "version": "1.1.1-cu.1", "versionCheck": "match", "active": true, "shaders": "pending", "itemProtocol": true', "hyprglass version=1.1.1-cu.1 versionCheck=match", "VERDICT: LOADED (rebuilt hyprglass 1.1.1-cu.1 listed in nested plugin list, versionCheck=match)".
- NOT independently re-derived by Y6r: the live plugin list BEFORE/AFTER identity claim (Y6r saw the BEFORE list lines in the grep output but did not see the AFTER list; Y6e's log states LIVE-PLUGIN-LIST-UNCHANGED). Live-untouched is separately supported by Y6r's own ps check (see V7).

### V4: hook marker (profile NOT applied) - VERIFIED
- Command (via ssh-laptop.sh): cat /tmp/y6-nested/conf/nested-visuals-hook.lua; grep for Y6-NEST-HOOK/hyprglass in the saved nested hyprland.log (/tmp/y6-nested/hypr-saved-y6e-20261121-215707-*/hyprland.log).
- Hook source: config-time check of hl.get_loaded_plugins(); only when count==1 and version=="1.1.1-cu.1" does it dofile optics.lua; else it prints "Y6-NEST-HOOK: hyprglass not ready (count=... version=...)".
- Nested log line: `DEBUG ]: [hlPrint] [Lua] Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)`. The profile was NOT applied in the load test. optics.lua (read via ssh, 2141 B) calls hl.plugin.hyprglass.config(...) with the G11 blur-0.15 candidate and registers the "computer-use-indicator" layer with mask_mode "contour", guarded by `if hl.plugin.hyprglass then`.

### V5: v3 runner U6 hook-marker gate - VERIFIED (by reading the pinned runner)
- File: improvements/worker-y6b-run-nested-wayland-v2.sh, md5 692d427174fa1c335eb02a46fc5e0a18 (matches Y6d's pinned value).
- Lines 298-305: if grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG", fail "hook ran before plugin load (profile not applied); see nested log". The marker lands in the per-instance log ($NEST_LOG), which is one of the two files grepped.
- Consequence (Y6r's preliminary read, to be ruled on by the council): the retry run with the current conf + v3 runner will fail at this gate before the liquid gate and before any pill measurement. The config-time dofile sits AFTER the load line (line 16 load, hook dofile after), so this is NOT a line-ordering problem: the load call returns before PLUGIN_INIT completes, and the next config line executes while the plugin is still unregistered. Observed once (count=0); mechanism leaves no window for the hook to see the plugin. Council 1 must confirm or refute the determinism claim.

### V6: C2 re-run log - VERIFIED (with one scope note)
- Command (via ssh-laptop.sh): grep of /tmp/y6e-c2/c2-laptop2-rerun.log.
- Lines seen: parser rc=1 out='' (live layers, no traceback), parser rc=0 out='320,0 320x66' (synthetic); GRIM-A OK bytes=37475, GRIM-A2 OK bytes=37475, GRIM-B0/B/C/D rc=1 with the expected error kinds; LDD-DEAD rc=1 naming libaquamarine.so.14/.so.4; LDD-GOOD rc=0; TEARDOWN-ASSERT1: 2, ASSERT2: RUN-DIR-REMOVED, ASSERT3: LOCK-FREE, ASSERT4: LIVE-1515-ALIVE.
- Scope note: the c2-laptop2.sh ldd block ran against the OLD (backup 1) conf as a regression check. The NEW conf ldd check was run separately by Y6e (verbatim block, "plugin ABI OK", rc=0) and by the load-test script's own pre-flight ("Y6E-LOAD: plugin ABI OK", seen in V3). Both pass.

### V7: live session untouched - VERIFIED (by Y6r's own read)
- Command (via ssh-laptop.sh): ps for Hyprland processes.
- Output: live Hyprland PID 1515 alive (started 06:44:26, `Hyprland --watchdog-fd 4`). No nested instance running at check time. Y6e's log records live plugins hyprbars only before and after; the AFTER-identity part is log-stated (see V3 note).

### V8: pinned file md5s - VERIFIED
- Repo copies: runner 692d427174fa1c335eb02a46fc5e0a18, pill da0565086a05f77f49985bb92d887875, y6e conf 9ccb27017ab63a9d2bce1d9651425d3b, y6e load-test script 65fe4c43a026b9aeb89048ff17a3b610. All match Y6d/Y6e's claimed values.
- Y6d + Y6e council/redteam papers all present in improvements/ (worker-y6d-council-1/2/3-*.md, worker-y6d-redteam.md, worker-y6e-council-1/2/3-*.md, worker-y6e-redteam.md).

### V9: liquid gate semantics - VERIFIED (by reading the source)
- scripts/indicator.py liquid_available (line 242): metadata-only; reads `hyprglass status` and matches the published schema. Docstring: "It is not proof that any pixel is drawn, that the optics look right, or that our indicator namespace is glassed. Those need a real test." So the liquid gate does NOT prove the profile was applied; the U6 hook-marker check is the only gate asserting profile application.

## Council + redteam (spawned 22:05 +07, papers pending)

- Council 1 (mechanism + determinism): improvements/worker-y6r-council-1-mechanism.md
- Council 2 (evidence): improvements/worker-y6r-council-2-evidence.md
- Council 3 (safety + measurement validity): improvements/worker-y6r-council-3-safety.md
- Redteam (adversarial): improvements/worker-y6r-redteam.md
- Each reviewer writes its paper and does NOT commit. Y6r adjudicates after reading all four papers in full.

## Corrections to Y6r's own mechanical verification (22:35 +07, before adjudication)

Y6r re-checked two load-bearing claims after the papers landed. Both corrections change the verdict's basis, so they are recorded here, not silently edited into V4/V5.

### Correction C-V4/V5: the profile WAS applied in the Y6e run (Y6r V4 and V5 were wrong)

- Y6r's preliminary read (V4: "The profile was NOT applied in the load test"; V5: "mechanism leaves no window for the hook to see the plugin") is WRONG. Redteam's reversal is correct, and Y6r verified its load-bearing chain mechanically from the repo's own pin-diff evidence (improvements/y6e-evidence/diff-99f30ca-03a57c4.txt, the v0.9.1 to v1.1.1 diff of the pinned commit 03a57c4):
  - Diff line 6270 (pin side, +): `addConfigValue<Config::Values::Bool>(handle, ConfigKeys::LAYERS_ENABLED, false);` The v1.1.1 pin registers `plugin:hyprglass:layers:enabled` with default **false**. (v0.9.1 line 6267 registered it as Int 0, also false-equivalent.)
  - Diff line 6507 (pin side, +): `config.layersEnabled = getStaticPtr<Config::BOOL>(handle, ConfigKeys::LAYERS_ENABLED);` The config value is read into `config.layersEnabled`.
  - Diff lines 1913-1915 (pin side): the `featureStatus` lambda sets `status.enabled = enabledValue && **enabledValue;` The status field `features.layers.enabled` IS the dereferenced config value pointer, not a separate feature flag. The README table in the same diff (lines 224-227) states `features.*.enabled` is "The setting: enabled, layers.enabled, subsurfaces.enabled".
  - Y6e's 21:57:14 status reported `features.layers.enabled == true` (seen by Y6r in V3 and by C2/C3 in their papers).
  - optics.lua is the only setter of layers.enabled in the nest (the nest conf runs only monitor + plugin load + hook dofile optics.lua; the README example at diff line 585 is `hg.config({ layers = { enabled = true, mask_threshold = 0.15 } })`).
  - Chain: default false + status enabled is the dereferenced config value + status read true + optics.lua the only setter. Therefore `hg.config()` RAN and the profile's config WAS applied, on parse 2, per redteam's mechanism (stock Hyprland 0.57.2: STAGE_PRIORITY parse 1 runs before the plugin system exists, STAGE_LATE loads the plugin synchronously and calls reload(), parse 2 sees count=1 and dofiles optics.lua silently).
- Consequences: Council 1's "unknowable" is superseded (it asserted a "default feature state" of true with no citation; the default is false). Council 2 section 1g ("The profile was not applied in the 21:57 load run") is WRONG. Council 3 F3 ("optics.lua was therefore never executed... profile was NOT applied") is WRONG. Y6e's log line 561 ("profile not applied") is WRONG. All four must be corrected in the fix (adjudicated item A4).
- Precision limit: the chain proves `config()` applied (layers.enabled true). It does NOT prove `layer()` registration succeeded, or that the blur/refraction material values landed: the status schema has no such fields (C2/C3 are right on that). The positive marker (C1 item 1, C3 G1) is still required, redefined: it proves the FULL profile (config + layer + values), not merely that config() ran.

### Correction C-V7: live Hyprland start time

- Y6r V7 wrote "started 06:44:26". Council 3 corrected this: 06:44:26 was elapsed time, not start time. Live Hyprland PID 1515 started Sat Nov 21 15:17:25 2026. The alive verdict is unchanged.

### Correction C-V9: U6 is not a valid profile gate

- V9 called U6 "the only gate asserting profile application". That is wrong in the operative sense: U6 asserts it FALSELY (a false fail on an expected parse-1 marker, and it cannot catch a silent skip of optics.lua). The positive marker + layers.enabled==true replaces it (adjudicated item A2). The liquid gate's blindness stands as a code fact (indicator.py lines 210-240 check no profile-applied field), but C2's proof-by-example for it collapses under C-V4/V5: the 21:57 status C2 called "un-profiled" IS a profiled status. The blindness claim rests on the code, not on that example.

### Infrastructure note: SSH from the VM to the laptop is DOWN at 22:35 +07 (found during the C-V4/V5 check)

- Symptom: `~/workspace/ssh-laptop.sh` fails twice (exit 255). `tailscale-proxy.py` dies at `from urllib.parse import urlparse` with `AttributeError: module 're' has no attribute 'compile'`.
- Root cause, verified: `/usr/lib/python3.12/re.py` is MISSING, and `/usr/lib/python3.12/re/` is a directory holding Python 3.13-style `re` package files (`_casefix.py`, `_compiler.py`, `_constants.py`, `_parser.py`, plus `__pycache__`) but NO `__init__.py`, so `import re` resolves to an empty namespace package. `python3 -c "import re; print(re.__file__)"` prints None; `hasattr(re, 'compile')` is False. This breaks ALL python3 invocations on the VM that import `re` (nearly everything), including the SSH proxy.
- The directory mtime is 2026-11-21 15:25:39 UTC (22:25:39 +07), minutes before Y6r's check; Y6r's own SSH calls at 22:01-22:05 worked, so the breakage happened between about 22:05 and 22:35 +07. The files are root-owned. Y6r did NOT attempt a repair (out of scope for this review; system directory, root-owned). The C-V4/V5 verification above was done from the repo's own pin-diff evidence on the VM instead, which is sufficient for the adjudication.
- Action owed (parent, not Y6r): repair the VM system Python and investigate what touched `/usr/lib/python3.12/re` at 22:25:39 +07. Until repaired, no fresh laptop-side verification reads are possible (V7/V8 stand as verified earlier in this session).

## Reviews in (all four papers read in full, 22:35 +07)

### Council 1 (mechanism + determinism): AMEND

- `hl.plugin.load` is declarative (PluginSystem.hpp:39 returns a promise; loads applied as a set by `updateConfigPlugins`; a distinct `handlePluginLoads()` phase; the Lua binding returns nothing awaitable). U6 failure is DETERMINISTIC (no race window; the marker lands on pass 1 of every run).
- Fix: (a) runner-side `nest hyprctl reload` after version checks, claimed WORKS and primary; (b) hook-side `hyprland.start` deferral NOT RECOMMENDED, `config.reloaded` handler PLAUSIBLE but unproven, `hl.timer` poll VIABLE but second choice; (c) applying optics via hyprctl DEAD (Diagnostics.cpp:589 only `status|stats|items`); (d) gate-only fix insufficient alone.
- Precision correction: "profile not applied in this run" is only proven for pass 1; pass-2 application is UNKNOWABLE from the artifacts (pass 2 silent; status exposes no material values). This is superseded by C-V4/V5 above.
- AMEND checklist: 1) positive marker print in laptop `/tmp/y6-nested/conf/optics.lua` after `layer()` (lines 36-38), pull to repo with md5 (no repo copy today; do NOT edit live `native/hyprglass-local-optics.lua`, blur 0.0); 2) insert plain `nest hyprctl reload` after version check; 3) replace U6 lines 298-305 with a positive gate (poll $NEST_LOG for the applied marker up to 15 s, fail on timeout, re-run plugin-list/version checks; log pass-1 "not ready" as expected); 4) point the retry at the rebuilt conf (md5 9ccb2701); 5) one application path only; 6) first amended run must show the positive marker before the liquid gate or stop.
- Limits: 0.57.2 PluginSystem.cpp/ConfigManager.cpp sources not read; (b2)/(b3) unprobed.

### Council 2 (evidence): AMEND

- Reproduced everything mechanically. Y6d C2 VM: 42 lines starting PASS, 0 FAIL, `RESULT: all VM C2 checks PASS` (c2-vm.log line 58); category count reconciles to 42. Y6d laptop C2 verified. Y6e ldd re-run verified. Conf diff verified repo-side and laptop-side (exactly 2 lines). Load log re-read in full; before/after live plugin lists independently re-derived (closes Y6r's V3 gap): byte-identical, hyprbars only, same handle 557052b0e7b0.
- NEW BLOCKER found: the retry as-is dies at the ldd pre-flight (runner lines 155-162) before any nest launches, because CONF is hardcoded at line 36 to `hyprland-wayland.lua`, which on disk is still the OLD conf (md5 0d4ac7a9, backup 1); the y6e conf was never installed as the active conf. After installing it, the retry dies at U6 line 302 deterministically.
- Liquid gate CANNOT catch a missing profile, proven by the 21:57 status dict (profile provably absent, yet satisfies every `_valid_liquid` condition except time-dependent shaders pending; status schema has no profile-applied field). The "profile absent" premise of that proof is WRONG per C-V4/V5; the blindness conclusion still stands as a code fact (see C-V9). The hook file's comment claiming `liquid_available` catches a missing profile is FALSE and must be corrected.
- Required fixes: 1) install the y6e conf as the active conf (copy over, keep old as backup, verify md5 9ccb2701 + ldd rc=0; do NOT edit the runner, its md5 is part of the C2 verdict); 2) fix hook timing so the profile applies after plugin load; do NOT delete/weaken U6; 3) re-prove with a fresh nested load run (no marker + positive evidence profile applied); 4) save the new-conf ldd output to a file (missing artifact; Y6e's own run has no saved log).
- UNVERIFIED: laptop copy md5 of the load-test script; whether nested shaders reach ready within the 60 s liquid window (only pending at 7 s observed); whether any status field changes when the profile IS applied (answered in part by C-V4/V5: layers.enabled true vs default false is the field).

### Council 3 (safety + measurement validity): AMEND

- A no-profile retry would NOT answer I11 as designed (G11 candidate: blur 0.15, refraction 0.55, contour mask on computer-use-indicator). A defaults-negative is the dangerous false negative. U6 is right as a negative fail-fast, wrong as a positive assertion (line 305 echo "profile applied" on mere marker absence). No plugin read-back can prove the profile: status JSON has no blur/refraction/preset/layer fields; `hyprglass items` lists subsurface items only, not layer registrations.
- Required gate G1: optics.lua (nest copy only) prints a success line AFTER config() and layer() return (e.g. `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator`), grepped in $NEST_LOG after reload and re-checked immediately before pill start. Keep U6 negative fail; add configerrors-empty (G4, per activation_checks pattern); keep versionCheck + liquid gate as supporting evidence only; record `hyprglass stats` (contourRebuilds) after arms as corroboration (G6).
- Reload fix direction mirrors the repo's own activation path (`scripts/activate-glass.py`: plugin load, then `hyprctl reload`, then wait_for_profile; `scripts/setup.py` hook comment "Apply optics on reloads"). Live risks: (a) wrong-target reload is most dangerous (launcher shell has WAYLAND_DISPLAY=/run/user/1000/wayland-1 live socket, so a BARE `hyprctl reload` reloads LIVE; visuals-login.lua would schedule visuals.py which loads glass live); mitigation: nest()-only reload, never bare. (b) config mix-up (never edit live optics blur 0.0 or live visuals-login.lua). (c) profile leak only via (a)/(b). (d) reload re-executes the load line; what it does to an already-loaded copy is UNVERIFIED (F13: duplicate guard pauses a second copy, first stays active, but unload-first vs skip vs duplicate-paused unproven), must be proven by a load-only trial. (e) failed reload keeps defaults, caught by G1/G4. (f) shared-GPU stall residual unchanged. (g) skip-var bypass, already gated at launch, must be preserved. Preconditions P1-P7 (copied conf only md5-verified; distinct socket nest()-only reload; live plugin list hyprbars-only before/after reload/after teardown; no hyprglass load path in live chain; skip var unset; load-only trial first; G1 re-check before pill).
- AMEND items: 1) G1 marker in nest optics.lua only; 2) runner fix (nest()-only reload after load confirmed, gate on G1 + exactly-one-hyprglass/versionCheck + configerrors empty + liquid ready, keep U6 fail, replace line-305 echo with a real assertion, re-check G1 before pill); 3) prove the reload path with a load-only trial first (no pill/arms; record post-reload plugin list, versionCheck, marker, configerrors, live before/after; if duplicate-paused entry or absent marker, reload path is DEAD, stop and re-review the `hyprctl eval dofile` alternative, also unproven); 4) record stats; 5) re-review the final fix diff before any measurement run.
- Note: C3's F3 ("optics.lua never executed, profile NOT applied") is WRONG per C-V4/V5. C3's reload endorsement is conditional on a load-only trial; the reload itself is ruled on in the adjudication below (R2).

### Redteam (adversarial): AMEND - HEADLINE REVERSAL

- Y6r's preliminary read is half right (the retry deterministically fails at U6) and half wrong (the reason). **The profile WAS applied in the Y6e run.** Proof: LAYERS_ENABLED defaults to false (hyprglass worktree `src/PluginConfig.cpp:83`); Y6e's status reported layers enabled true; optics.lua is the only setter in the nest. Mechanism from stock Hyprland v0.57.2 source (tag 11cbc6c57, `git ls-remote` returns 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947): `hl.plugin.load()` only records the path (`LuaBindingsConfigRules.cpp:562`); parse 1 runs before the plugin system exists (ConfigManager STAGE_PRIORITY, PluginSystem STAGE_LATE), so the hook sees count=0 and prints the marker; then STAGE_LATE loads the plugin synchronously (CPromise fully synchronous, permission defaults ALLOW) and calls `reload()`, so parse 2 sees count=1 and dofiles optics.lua silently. Y6r verified the default-false leg of this proof from the repo pin diff (see C-V4/V5).
- "The hook can never see count=1" is REFUTED (parse 2, parse 3 via doLater reload, and any manual post-load reload all see count=1); parse 1 alone is deterministically 0. U6 effectively cannot MISS the marker (lands in both logs before stdout disabled; $NEST_LOG defined and checked). Real subtlety: the per-instance file is not flushed per line (hyprutils ofstream, no flush), so both saved nested logs are 188-line flushed prefixes ending mid-Aquamarine-dump; marker counts from saved logs are NOT evidence of parse counts.
- Liquid gate confirmed blind (status JSON has no profile/layer-namespace fields).
- False pill verdict paths: wrong conf staged is LIVE (retry dies at ldd pre-flight); grep-first-path trap DORMANT on the y6e conf; stale marker NO (logs truncated/fresh dir); partial profile (optics.lua config() throws on parse 2) is LIVE as a residual: no gate would catch it (U6 looks only for the parse-1 marker, liquid blind, pill script never checks glass), arms would produce a false-negative NOT reproduced.
- Fix candidates: `nest hyprctl reload` DOES re-execute config, but the old marker still trips U6, and reload is REDUNDANT because parse 2 already applies the profile. Do NOT add it (if added anyway, needs kill -0 re-check of NEST_HYPRLAND_PID + A2; parse-3 duplicate layer() registration is an open question, overwrite vs error unresolved). Hook-side busy-wait CANNOT work (load triggered by postConfigReload after config returns; config has a timeout); `hl.timer` exists and would work in principle but is unnecessary. Applying optics via hyprctl DEAD (only `status|stats|items`; items lists subsurface items only).
- Load-test scope gap: everything up to the status parse is proven live (F0, U5b, ldd, plugin list, status); everything after is NOT (U6 as a gate, liquid gate, backdrop, positive control, pill, both arms, verdict logic, file-presence preconditions, teardown assertions). The v3 runner also lacks the load test's AMEND4/AMEND5 live-safety guards.
- Amend list: A1 stage the y6e conf with md5 verification; A2 replace U6 with a positive applied check (hook prints `Y6-NEST-HOOK: profile applied` on the success branch AFTER the dofile returns; U6 requires that marker present and fails if absent; parse-1 "not ready" marker is EXPECTED, delete the fail-on-not-ready rule; second positive signal: `features.layers.enabled == true` in parsed status JSON); A3 correct the record (Y6e log line 561 and Y6r V4/V5 wrong; reword U6 fail string line 303); A4 correct the hook's false liquid-gate comment; A5 port AMEND4 + AMEND5 into the v3 runner (skip-var unset check, live-config no-load-path walk, live plugin list before/after identity); A6 stop using saved-log marker counts as parse evidence; A7 do NOT add a manual reload.
- Open items: O1 duplicate layer() on parse 3 unresolved; O2 hyprland.start emission point unpinned (not needed); O3 pill arms never run live; O4 SSH flapped twice during review (retry, do not conclude the laptop is down). O4 is now worse than a flap: SSH is DOWN at 22:35 +07 for the VM Python reason above, not a laptop problem.

## Adjudication

All four papers agree on the verdict (AMEND) and on the staging blocker, the positive marker, the record corrections, and AMEND4/AMEND5. They conflict on three points, ruled here.

### R1: the profile state in the Y6e run. REDTEAM WINS.

- The profile's config WAS applied on parse 2. The proof chain is verified by Y6r from the repo pin diff (C-V4/V5). Council 1's "unknowable" is superseded: it asserted a "default feature state" of true with no citation, and the default is false. Council 2 section 1g and Council 3 F3 ("profile was not applied") are wrong. Y6e log line 561 and Y6r V4/V5 are wrong and are corrected by this log.
- Precision: the chain proves `config()` applied. It does not prove `layer()` registration or the material values. The positive marker is still required, redefined: it proves the FULL profile (config + layer + values), not merely that config() ran.

### R2: the manual `nest hyprctl reload`. REDTEAM WINS. DO NOT ADD IT.

- Council 1 recommends it as the primary fix; Council 3 endorses its direction conditional on a load-only trial. Redteam says it is redundant and must not be added. Redteam wins, for four reasons. (1) Parse 2 already applies the profile deterministically (R1), so the reload's benefit for profile application is zero. (2) Council 1's own "harmless no-op" admission means the reload cannot change the outcome when the plugin list is unchanged. (3) Council 3's F13 shows what a reload does to an already-loaded copy is unverified, and redteam's O1 (duplicate layer() registration on parse 3, overwrite vs error) is a real unprobed risk the reload would introduce. (4) The reload adds live-touch surface (Council 3's wrong-target reload hazard) for no proven benefit.
- The fix is gate-only plus staging plus record corrections. If the positive gate later shows the marker absent (profile genuinely not applied), the reload (or the timer) becomes the next hypothesis to test. Not now, not preemptively.
- Council 3's item 3 (load-only trial of the reload path) is moot. The load-only trial requirement survives in restated form (A8): prove the amended fix, not the reload.

### R3: U6, keep or delete. RECONCILED.

- Council 2 says "do NOT delete or weaken U6". The reconciled position: keep U6's protective function (catch a genuinely missing profile) and STRENGTHEN it, but delete the false-fail rule on the expected parse-1 marker. The gate becomes positive (marker present + layers.enabled true); the parse-1 marker is expected, not a failure. This does not weaken the protection: the positive check catches the silent skips (i)-(iii) in Council 3 section 1b that U6 misses, so the protection is strictly stronger. What is deleted is only the false-fail rule and the false "profile applied" echo on line 305.

### R4: staging. UNANIMOUS. Adopted as A1.

### R5: AMEND4/AMEND5 port. ADOPTED (redteam A5, Council 3 P3/P4/P5).

- Port the skip-var unset check, the live-config no-load-path walk, and the live plugin list before/after identity into the v3 runner (or the run procedure). The fix worker verifies the exact delta against the v3 runner text first: the runner already has partial teardown equivalents, so this is a gap-fill, not a blind duplicate.

### R6: the hook's false liquid-gate comment. ADOPTED.

- Correct it. The liquid gate is blind to the profile as a code fact (indicator.py lines 210-240 check no profile-applied field). The liquid gate stays as supporting evidence only.

### R7: supporting gates and records. ADOPTED.

- Council 3 G4 (nest hyprctl configerrors empty after profile application) as a supporting gate. Council 3 G6 (record `hyprglass stats`, contourRebuilds, before/after arms) as corroboration, not a gate until a baseline is known. Council 1 item 6 (first amended run must show the positive marker before the liquid gate or stop). Redteam A6 (do not use saved-log marker counts as parse evidence).

### R8: one application path only. ADOPTED (Council 1 item 5, adapted).

- The automatic parse-2 path is the only application path. No timer, no hyprland.start deferral, no manual reload.

## Adjudicated fix list (all must land before the retry; then a fresh re-review of the fix diff)

- A1: Stage the y6e conf as the active conf. Copy improvements/worker-y6e-hyprland-wayland-rebuilt.lua over /tmp/y6-nested/conf/hyprland-wayland.lua (laptop), keep the old conf as a backup, verify md5 9ccb27017ab63a9d2bce1d9651425d3b on the laptop copy, run ldd on the conf's plugin path (rc=0), and SAVE the ldd output to a file. Do NOT edit the v3 runner (its md5 is part of the C2 verdict).
- A2: Replace U6 (runner lines 298-305) with a positive applied gate. Poll $NEST_LOG for the applied marker up to 15 s after the version check; fail on timeout with a log tail; re-run plugin-list/version checks after the marker; treat the parse-1 "not ready" marker as EXPECTED (log it, do not fail). Require `features.layers.enabled == true` in the parsed status JSON as a second positive signal. Rewrite the U6 fail string (line 303) to describe the new gate.
- A3: Positive marker. In the nest copy of optics.lua ONLY, print a success line AFTER config() and layer() return, e.g. `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator`. Pull the nest optics.lua to the repo with md5. Never edit live native/hyprglass-local-optics.lua (blur 0.0). The hook must not swallow dofile errors (no pcall hiding a throw).
- A4: Correct the record. Y6e log line 561, Y6r V4/V5 (this log, corrected above), Council 2 section 1g, Council 3 F3 all stated "profile not applied". The correct statement is: "profile config applied on parse 2 (layers.enabled true, proven); layer() registration and material values unproven until the positive marker lands". Correct the hook's false liquid-gate comment.
- A5: Port AMEND4 + AMEND5 into the v3 runner (skip-var unset check, live-config no-load-path walk, live plugin list before/after identity); fix worker verifies the exact delta first (R5).
- A6: Add Council 3 G4 (nest hyprctl configerrors empty after profile application) as a supporting gate. Record Council 3 G6 (`hyprglass stats`, contourRebuilds, before/after arms) as corroboration, not a gate.
- A7: Do NOT add a manual `nest hyprctl reload` (R2). One application path only (R8).
- A8: Prove the amended fix with a load-only trial first (no pill/arms): positive marker + layers.enabled true + configerrors empty + live before/after identical. First amended run must show the positive marker before the liquid gate or stop.
- A9: Re-review the final fix diff (council + redteam) before any measurement run. The retry worker must NOT run the pill measurement on an unreviewed fix.
- A10: Method. Do not use saved-log marker counts as parse evidence (ofstream buffering; saved logs are 188-line flushed prefixes). Use the fresh per-instance log.

## Open items carried forward

- O1: duplicate layer() registration on parse 3 (overwrite vs error) unresolved. Watch the retry log; if a parse-3 error appears, record it; the parse-2 profile stands.
- O2: hyprland.start emission point (not needed).
- O3: whether nested shaders reach ready within the 60 s liquid window (only pending at 7 s observed). The retry itself proves it.
- O4: laptop copy md5 of the load-test script (Council 2 unverified). Verify during the fix. Blocked until the VM Python/SSH repair (see infrastructure note).
- O5: whether any status field changes when the profile IS applied. Answered in part by R1 (layers.enabled true vs default false is the field). Blur/refraction/material values have no status field; unproven until the marker (A3).

## Verdict: AMEND (unanimous)

- Council 1 AMEND, Council 2 AMEND, Council 3 AMEND, redteam AMEND. The pill measurement retry run may NOT proceed as-is. It may proceed only after the adjudicated fix list A1-A10 lands AND a fresh council + redteam re-review of the fix diff clears it.
- What the re-review PROVED (stands): F1 fixed at the link level (V1: .so 34,440,704 B, md5 78ac1023, ldd 0 not found,.so.15/.so.5 resolve); conf diff exactly 2 lines (V2); nested load test LOADED with versionCheck match (V3, live plugin lists byte-identical per Council 2); C2 re-run ALL PASS (V6); live PID 1515 untouched (V7, start time corrected to Sat Nov 21 15:17:25 2026).
- What the re-review REVERSED: the profile WAS applied in the Y6e run (R1). The retry's blocker is NOT a missing profile. It is two mechanical defects: the y6e conf was never staged as the active conf (the retry dies at the ldd pre-flight on the old backup-1 conf), and U6 is a false-fail gate that would kill a healthy run at line 302.
- What the re-review did NOT prove: the pill measurement itself (no arms ever ran live), the full G11 profile (layer() registration and material values unproven until A3), and the liquid gate's readiness window (O3).

## Commit record

- Commit 6239298 on todolist-push (verified via ls-remote: 6239298e574986e2df8149bd877bfd1a98b31665), 5 files, 792 insertions: this log + the 4 review papers. Committed by exact paths only; other workers' uncommitted changes were left untouched.

# Council Voice 2 (evidence): Y6d launcher v3 + Y6e rebuild/load-test re-review

- Role: Council Voice 2, evidence. Parent: Y6r (re-review lead).
- Scope: read-only verification. No code, conf, or runner file modified. No nested Hyprland launched. No live Hyprland PID 1515, vkms, or laptop repo touched. Laptop checks via `~/workspace/ssh-laptop.sh`, short commands only.
- Repo: `~/workspace/computer-use-wayland`, branch `todolist-push`. Commits checked: Y6d `72eb8ad`, Y6e `915121d`.
- Time: Sat 2026-11-21, approx 22:04-22:15 +07. Live PID 1515 confirmed alive by `ps` at 22:04 (`1515 Hyprland`).

## VERDICT: AMEND

The Y6d C2 results and the Y6e rebuild/load claims reproduce mechanically, with two exceptions that block a retry as-is. First, the v3 runner still points at the OLD conf on disk, so a retry dies at the ldd pre-flight before any nest launches. Second, with the new conf installed, the retry dies at the U6 hook-marker gate, because the hook runs once at config time before the plugin finishes loading, and the profile is never applied. The liquid gate cannot catch a missing profile, so U6 must not be removed to work around this. Exact fixes are listed at the end.

## 1. Re-verification of every Y6d/Y6e claim

### 1a. Y6d C2 VM summary: VERIFIED

- File: `improvements/y6d-evidence/c2-vm.log` (58 lines).
- `grep -c "^PASS"` = 42. `grep -c "^FAIL"` = 0. Line 58: `RESULT: all VM C2 checks PASS`.
- The 6 lines containing the substring `FAIL` are all expected-failure outputs inside PASS lines (discovery ambiguous/missing/dead-socket cases, ldd dead-ABI fixture, conf no-path / missing-path cases). None is a failed check.
- Category count reconciles to 42 exactly: verdict 1 line (16/16 combos in one check) + discovery 6 + backend gate 5 + nest guard 2 + guard pre-check 3 + ldd functional 4 + pill wait 2 + pill snippet 3 + cleanup 2 + env propagation 3 + static 11 = 42. Note: the Y6d commit message parenthetical lists verdict 16 + discovery 6 + gate 5 + ldd 4 + pill wait 2 + pill snippet 3 + cleanup 2 + env 3 + static 11, which sums to 52 if verdict counts as 16, and omits the 5 guard checks; counting the verdict block as 1 PASS line and adding the 5 guard checks gives 42. The total is right; the parenthetical is just incomplete.

### 1b. Y6d laptop C2: VERIFIED

- File: `improvements/y6d-evidence/c2-laptop2.log` (61 lines), read in full.
- C2-1: runner `bash -n OK`, pill `py_compile OK`, live sig `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825`, live pid 1515, md5s runner `692d427174fa1c335eb02a46fc5e0a18`, pill `da0565086a05f77f49985bb92d887875`, conf `0d4ac7a9c2437fb48ecfc505ccd9046b`.
- C2-2 parser: live layers (no pill) rc=1, no traceback; synthetic nested JSON rc=0 out=`320,0 320x66`.
- C2-3 grim: GRIM-A OK bytes=37475, GRIM-A2 OK bytes=37475 (same bytes: same origin 2464,902, consistent, not a discrepancy), B0 did-not-intersect, B not invalid geometry, C invalid geometry, D mutually exclusive.
- C2-3b ldd: DEAD rc=1 naming `libaquamarine.so.14` and `libhyprgraphics.so.4` on the real backup-1 path; GOOD rc=0 `plugin ABI OK`.
- C2-4 teardown: asserts `2`, `RUN-DIR-REMOVED`, `LOCK-FREE`, `LIVE-1515-ALIVE`.
- Note: this log tests the OLD conf (md5 `0d4ac7a9`, backup 1). That is correct for Y6d; the new-conf check is covered separately in 1f.

### 1c. Y6e ldd on the rebuilt .so: VERIFIED (re-run by me)

- Command (laptop): `ldd ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so`.
- Result: 0 lines `not found`. `libaquamarine.so.15 => /usr/lib/libaquamarine.so.15`, `libhyprgraphics.so.5 => /usr/lib/libhyprgraphics.so.5`. All other deps resolve to `/usr/lib`.
- File: 34,440,704 bytes, md5 `78ac102337ca70842bf604b56c6f4c8e`. Matches Y6r's claim exactly.
- Control, same session: backup-1 `.so` still dead, `libaquamarine.so.14 => not found` and `libhyprgraphics.so.4 => not found`.

### 1d. Y6e conf diff: VERIFIED (re-run on repo copies and laptop-side)

- Repo diff `improvements/worker-y6b-hyprland-wayland-v2.lua` vs `improvements/worker-y6e-hyprland-wayland-rebuilt.lua`: exactly 2 changed lines, line 8 (comment) and line 16 (load path). `diff` exit code 1 (differences found), hunks `8c8` and `16c16` only.
- Laptop-side diff `/tmp/y6-nested/conf/hyprland-wayland.lua` vs `/tmp/y6-nested/conf/hyprland-wayland-y6e.lua`: identical 2-line diff.
- Laptop md5s: y6e conf `9ccb27017ab63a9d2bce1d9651425d3b`, runner `692d427174fa1c335eb02a46fc5e0a18`, pill `da0565086a05f77f49985bb92d887875`. All match Y6r's claims and the repo copies.
- The line-8 comment contains no `.so` path, so the ldd pre-flight `grep -o` extraction returns the rebuilt path (confirmed by my own run in 1f).
- IMPORTANT STATE FINDING: the active conf the runner reads, `/tmp/y6-nested/conf/hyprland-wayland.lua`, is still the OLD file (md5 `0d4ac7a9c2437fb48ecfc505ccd9046b`). The y6e conf exists only as the separate file `hyprland-wayland-y6e.lua` and has NOT been installed as the active conf. The Y6e log itself says the rebuilt `.so` is "NOT installed... no config points at it yet" for the live side, and the same is true for the runner side: the runner's CONF was never switched.

### 1e. Y6e load-test log: VERIFIED, including the before/after identity claim

- File (laptop): `/tmp/y6-nested/y6e-load-20261121-215707.log` (2237 bytes), read in full. Wall 21:57:07 to 21:57:14, teardown to 21:57:17.
- Present in the log: AMEND4 OK (skip var unset), AMEND5-BEFORE OK (no hyprglass load path in live config chain), `plugin ABI OK` for the rebuilt worktree path, live sig/pid 1515, live plugin list BEFORE showing only `hyprbars`, runner-quiet check OK, flock held, nested pid 397826, nested sig `..._1795273027_147477040`, nested Hyprland pid 397829, `Starting the Wayland backend!`, nested socket `wayland-1`, nest output `WAYLAND-1`, `hyprglass IS in the nested plugin list`, status JSON with `version 1.1.1-cu.1 versionCheck match active true shaders pending`, `NOTE: hook ran before plugin load (profile not applied; load verdict unaffected)`, `VERDICT: LOADED`, teardown with live PID 1515 alive, live plugin list AFTER showing only `hyprbars`, lock free.
- Before/after identity, independently re-derived (closes the gap Y6r left open): I read `/tmp/y6-nested/y6e-live-plugin-list-before.json` and `/tmp/y6-nested/y6e-live-plugin-list-after.json` directly. Both contain exactly one plugin, `hyprbars`, author Vaxry, handle `557052b0e7b0`, version 1.0. `diff` of the two files: IDENTICAL, no output. The live session was untouched.
- Nested artifacts read directly: `/tmp/y6-nested/y6e-nest-plugin-list.json` contains exactly one plugin, `hyprglass`, version `1.1.1-cu.1`. `/tmp/y6-nested/y6e-nest-glass-status.json` matches the log byte for byte in content (schema 1, version 1.1.1-cu.1, versionCheck match, active true, shaders pending, layers enabled true active true reason null, windows/subsurface disabled).
- The two earlier abort logs exist as claimed: `y6e-load-20261121-215203.log` (717 bytes) and `y6e-load-20261121-215423.log` (1044 bytes), both ending with teardown done and lock free. Both aborts were fail-closed at AMEND 5 with no nest started, consistent with the Y6e log account.

### 1f. Y6e C2 re-run: VERIFIED in outcome, one artifact gap

- File (laptop): `/tmp/y6e-c2/c2-laptop2-rerun.log` (2843 bytes), read in full. Start 21:50:19, done 21:50:20. Content reproduces `c2-laptop2.log` exactly except timestamps: same md5s (runner 692d4271, pill da056508, conf 0d4ac7a9), same parser rc=1/0, same GRIM-A/A2 37475 bytes, same LDD-DEAD naming .so.14/.so.4 rc=1, LDD-GOOD rc=0, same teardown asserts 2/RUN-DIR-REMOVED/LOCK-FREE/LIVE-1515-ALIVE.
- The rerun script `c2-laptop2.sh` checks the OLD conf md5 by design, so the rerun itself does NOT test the new conf. The new-conf coverage is only the separate `ldd-test.sh` run.
- New-conf ldd check, independently reproduced by me (laptop): `bash /tmp/y6e-c2/ldd-test.sh /tmp/y6-nested/conf/hyprland-wayland-y6e.lua` prints `Y6-WAYLAND: plugin ABI OK: ~/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so`, rc=0. Same command against the old conf prints the dead-ABI FAIL naming .so.14/.so.4, rc=1. This matches the Y6e rebuild-load log line 529 claim.
- Artifact gap: there is no saved log file of Y6e's own `ldd-test.sh` run against the new conf; the evidence is the claim line in `improvements/worker-y6e-rebuild-load-log.md` (line 529) plus the load log's own `plugin ABI OK` line plus my independent re-run just now. Outcome VERIFIED, artifact UNVERIFIED (no file). The next worker should save that run's output to a file.

### 1g. Hook marker: VERIFIED

- Saved nested log (laptop): `/tmp/y6-nested/hypr-saved-y6e-20261121-215707-11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795273027_147477040/hyprland.log`.
- Grep result, one line: `DEBUG ]: [hlPrint] [Lua] Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)`.
- The marker is real, from the y6e-conf run, and it means the hook's `dofile(optics.lua)` branch did not run. The profile was not applied in the 21:57 load run. The load verdict is unaffected, as the log states, but any pill measurement from that run would have measured an un-glassed indicator.

## 2. V3 runner gate flow, traced end to end

File: `improvements/worker-y6b-run-nested-wayland-v2.sh` (md5 `692d427174fa1c335eb02a46fc5e0a18`, matches Y6r and laptop).

Gate order with line numbers:

1. Pre-flight ldd, lines 155-162. Extracts the FIRST `hyprglass*.so` path from `$CONF` with `grep -o` and fails fast if any dep is `not found`. `$CONF` is hardcoded at line 36: `CONF=$NEST/conf/hyprland-wayland.lua`, `NEST=/tmp/y6-nested` (line 34). There is no env override. On disk right now that file is the OLD conf (md5 `0d4ac7a9`), so this gate fails naming `.so.14`/`.so.4` before any nest launches.
2. Backend gate, lines 236-247. Retries up to 10s for `Starting the Wayland backend!` in the per-instance log `$NEST_LOG`, then `kill -0` on the nest pid. Proven to pass with the y6e conf by the 21:57 load run.
3. Socket discovery, lines ~252-271. Exactly one live (connect-probed) `wayland-*` socket, retry 10s. Proven to pass: `wayland-1`.
4. Plugin-list check, line 281. `grep -q hyprglass` on `nest-plugin-list.json`. Proven to pass with the rebuilt .so.
5. Version parse, lines 285-296. Requires `version == 1.1.1-cu.1` and `versionCheck == match`. Proven to pass.
6. U6 hook-marker check, lines 298-305. `grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG"` then `fail "hook ran before plugin load (profile not applied); see nested log"`. With the y6e conf this gate FAILS: the marker is proven present in the 21:57 nested log (see 1g). The task text said lines 298-305; the check itself is line 302, the echo `hook marker absent, profile applied` is line 305.
7. Liquid gate, lines 307-324. `nest python3` loop, up to 60s, `indicator.liquid_available(env, ready=True)`, from `scripts/indicator.py`.

### Why the hook fires before the plugin loads

- The y6e conf line 16 calls `hl.plugin.load(...)` and lines 18-19 dofile the hook (`nested-visuals-hook.lua`) immediately after, at config-parse time.
- The hook (laptop `/tmp/y6-nested/conf/nested-visuals-hook.lua`, read in full) runs exactly once, at config time. It calls `hl.get_loaded_plugins()`, counts entries named `hyprglass` with version `1.1.1-cu.1`, and only then dofiles `optics.lua`. Otherwise it prints the `not ready` marker. There is no retry, no timer, no event subscription, no second chance.
- At config time the plugin load has not completed, so the count is 0 and version is nil. This is structural, not a race: every run with this conf shape will print the marker. The 21:57 run proves it.
- `optics.lua` (laptop, read in full) is the profile: guarded by `if hl.plugin.hyprglass then`, it calls `hl.plugin.hyprglass.config(config)` with layers enabled true and `hl.plugin.hyprglass.layer("computer-use-indicator", {preset = "default", mask_mode = "contour"})`. Nothing else in the nest applies it. The conf dofiles only the hook, and the hook is the only caller of `optics.lua`.

### Does the liquid gate catch a missing profile? NO, proven

- `scripts/indicator.py`, `liquid_available(env, ready=False)` lines 242-253, `_valid_liquid(status, ready=False)` lines 210-240. Its docstring says it plainly: "Metadata only: this reads `hyprglass status` and matches the published schema. It is not proof that any pixel is drawn, that the optics look right, or that our indicator namespace is glassed. Those need a real test."
- `_valid_liquid` with `ready=True` requires: schema int 1, version `1.1.1-cu.1`, versionCheck `match`, active true, shaders `ready` (pending is rejected when ready=True), features layers/windows/subsurface all dicts, layers enabled true and active true with reason present and null, windows enabled false, subsurfaces enabled false.
- The status dict observed in the 21:57 run, where the profile was provably NOT applied (marker present, optics.lua never dofiled), already satisfies every one of those conditions except the time-dependent shaders field, which was `pending` at 7 seconds after start. Once shaders compile to `ready`, `liquid_available(ready=True)` returns True on a profile-less nest.
- The status schema has no field that reflects the profile: no per-layer or per-namespace entry, no profile-applied flag. The profile's `config()` call sets layers enabled true, which is already the plugin default shown in the un-profiled status. The profile's `layer("computer-use-indicator", ...)` registration is invisible to `hyprglass status` as observed.
- Therefore, if U6 were removed, NO later gate would catch a missing profile. The run would proceed past the liquid gate, launch mpv, pass the positive control, start the pill, and measure an indicator that was never glassed. The measurement would be meaningless, and nothing in the run would say so.
- The hook file's own comment claims the opposite: "The runner checks liquid_available(ready=true) after start; a missing profile is NO-GO." That claim is FALSE, demonstrated by the 21:57 status dict. The comment must be corrected when the hook is fixed, or a future worker will trust it and delete U6.

### Which gate the retry hits first

- As-is, with the on-disk state right now: the ldd pre-flight (lines 155-162). It fails on the old conf before any nest launches. Fail-closed and safe, but the retry cannot proceed.
- After installing the y6e conf as the active conf: the U6 hook-marker check (line 302). Backend gate, socket discovery, plugin list, and version parse all pass on the evidence of the 21:57 run. U6 fails deterministically.
- The liquid gate is never reached in either case, and even if reached it would not catch the missing profile.

## 3. UNVERIFIED items

1. Laptop copy of the load-test script md5. Y6e log says `65fe4c43a026b9aeb89048ff17a3b610` on the laptop at `/tmp/y6-nested/y6e-load-test.sh`. I verified the repo copy md5 (`65fe4c43a026b9aeb89048ff17a3b610`) but did not md5 the laptop copy (my md5 attempt used the wrong laptop path). Minor: the 21:57 run log is fully consistent with the script I read in full on the repo.
2. Whether nested shaders reach `ready` within the 60s liquid-gate window. Only observed value is `pending` at 7s after start. No nest run has ever waited out the liquid gate. The gate's pass/fail on a healthy nest is therefore unproven, independent of the profile question.
3. Whether any `hyprglass status` field changes when the profile IS applied. No profile-applied run exists to compare against. On the current evidence the answer is that no field can change, because the observed un-profiled status already matches the gate's full requirement set, but a positive control run is still owed.
4. No saved log file of Y6e's own `ldd-test.sh` run against the new conf (see 1f). Outcome reproduced by me; artifact missing.

## 4. Required changes before retry (AMEND)

1. Install the y6e conf as the active conf. Copy `/tmp/y6-nested/conf/hyprland-wayland-y6e.lua` over `/tmp/y6-nested/conf/hyprland-wayland.lua` (keep the old file as a backup copy first, e.g. `hyprland-wayland-backup1.lua`, so the dead-ABI path stays recorded). Then verify: active conf md5 is `9ccb27017ab63a9d2bce1d9651425d3b`, and `ldd-test.sh` against the active conf prints `plugin ABI OK` with rc=0. Do NOT edit the runner to point at the y6e file: `CONF` is hardcoded at line 36 and the runner md5 `692d4271` is part of the C2 verdict; changing it invalidates the C2 evidence. Copying the conf is the change; editing the runner is not.
2. Fix the hook timing so the profile is actually applied. The hook as written can never succeed: it runs once at config time before the plugin load completes. The fix must make the profile application happen after the plugin is listed (for example, a deferred re-check driven by the runner after the plugin-list gate, or a hook that re-runs on a later Hyprland event). Do NOT delete or weaken the U6 gate (lines 298-305): it is currently the ONLY gate that catches a missing profile, and section 2 proves the liquid gate cannot replace it. Correct the hook file's false comment claiming `liquid_available` catches a missing profile.
3. Re-prove with a fresh nested load run after (1) and (2): the nested log must show NO `Y6-NEST-HOOK: hyprglass not ready` marker, the plugin list and version must still match, and there must be positive evidence the profile applied (for example, a marker printed by `optics.lua` when it runs, or a `hyprglass status` field that differs from the un-profiled run; if no such observable exists, record that explicitly and let U6 absence-of-marker stand as the only signal).
4. Save the new-conf ldd check output to a file (the missing artifact from 1f), and save the fresh load run log alongside it.
5. Do not touch the live config or live session. The live plugin list before/after identity (hyprbars only, identical handles) is verified and must stay that way.

## 5. What is solid

- Y6d C2 VM 42/42 and laptop C2 both reproduce exactly from the saved logs.
- Y6e rebuild: 34,440,704 bytes, md5 `78ac102337ca70842bf604b56c6f4c8e`, ldd 0 not found, `.so.15`/`.so.5` resolve. Backup 1 still dead as recorded.
- Y6e conf diff is exactly 2 lines, and the ldd extraction trap from the first version (dead path in the comment) is fixed and verified.
- Y6e load test: plugin listed in the nest, version 1.1.1-cu.1, versionCheck match, live session untouched before and after (byte-identical plugin-list JSONs), teardown clean, live PID 1515 alive.
- The two AMEND-5 aborts were correct fail-closed behavior with no nest started.
- The U6 gate works exactly as designed: it caught a real missing-profile condition that every other gate would have missed.

# Redteam review: Worker Y6d v3 launcher fixes (F0 socket discovery, U5b backend gate)

- Reviewer: redteam (independent, depth 2).
- Scope: LAUNCHER FIXES ONLY. The hyprglass rebuild is BLOCKED by an execution-risk check on a fetched commit and is NOT reviewed here. No Zen driven, no nested Hyprland launched, no live session touched (live Hyprland PID 1515 only observed in existing logs), no hyprglass source checked out, built, or loaded, no git command run in the vendor repo.
- Target: repo `~/workspace/computer-use-wayland`, branch todolist-push. Diff `improvements/y6d-evidence/v3-diff.txt` (188 lines). Fixed files: `improvements/worker-y6b-run-nested-wayland-v2.sh` (v3 md5 c7c1d6f2), `improvements/worker-y6b-run-nested-pill-v2.py` (eea0c320), `improvements/worker-y6b-hyprland-wayland-v2.lua` (0d4ac7a9).
- Evidence read: `improvements/worker-y6d-rebuild-log.md`, `improvements/worker-y6c-nested-run-log.md`, `improvements/y6c-evidence/*.log`, `improvements/y6d-evidence/c2-vm.log`, `improvements/y6d-evidence/c2-laptop.log`, C2 scripts `/tmp/y6d-c2-vm.py`, `/tmp/y6d-c2-laptop.sh`, v2 originals via `git show origin/todolist-push:<path>`.
- Checks run: 21:00-21:06 +07, 21 Nov 2026. Every check below is timed and logged. Proof harness: `/tmp/y6d-redteam/proofs.sh`, full log `/tmp/y6d-redteam/proofs2.log`. All proof blocks were extracted VERBATIM from the v3 runner and run against controlled fixtures on the VM.

## Verdict: AMEND

The v3 launcher is fail-closed on every path I could reach, and I found NO false-pass path: no defect lets a broken nest produce a bogus VERDICT, and nothing in v3 endangers the live session. But three reproduced defects (A1, A2, A3) will waste a live slot or misdirect diagnosis on the exact retry path, and four more (B1-B4) are real. None is a design kill. All fixes are small, exact, and listed below with file and line. Apply them, extend C2 as specified, re-run C2, then the retry may proceed.

Why not GO: A1 false-fails a healthy slow-starting nest at the backend gate; A2 burns 45s and reports the wrong cause when the pill dies after 1s; A3 sends the first retry into a misleading fail with no ABI diagnosis while the only guard is a comment.

Why not BLOCK: every defect fails closed (exit 1, teardown runs, no verdict emitted). No live-session risk was found. The F0 and U5b fix directions are both correct on the evidence.

## Verified correct (do not change)

- V1, md5 match. Repo files match the claimed v3 md5s (runner c7c1d6f2, pill eea0c320, conf 0d4ac7a9). Laptop copies verified read-only via `~/workspace/ssh-laptop.sh` md5sum at 21:00 +07: `/tmp/y6-nested/run-nested-wayland.sh` c7c1d6f2, `/tmp/y6-nested/run-nested-pill.py` eea0c320, `/tmp/y6-nested/conf/hyprland-wayland.lua` 0d4ac7a9. Exact match.
- V2, U5b direction is right. In Y6c evidence, `grep -a -c "Wayland backend"`: 0 in all three stdout logs (`probe-nosocket.log`, `probe2-nosocket.log`, `probe3-nosocket.log`), 1 in each per-instance log (`probe2-hyprland.log`, `probe3-hyprland.log`), exact line `Starting the Wayland backend!` (aquamarine DEBUG). The old grep on `$LOG` could never pass a healthy start. No failure line in any log contains the substring `Wayland backend` (the closest is `DRM Backend failed`, which does not match), so the old grep was never right on any observed path either.
- V3, F0 direction is right. No `--socket` remains in runner code (only comments documenting the removal). Y6c probe 1 already proved dropping `--socket` starts the nest and auto-names the socket `wayland-1`.
- V4, stale cleanup works for real entries. Proof P2b: a stale socket, a stale `.lock`, and a stale regular file named `wayland-old` in a fixture dir were all removed by the verbatim cleanup block (lines 179-180). Post-cleanup listing was empty.
- V5, verdict logic. C2-vm.log claims 16/16 combos exactly 1 VERDICT line; I did not re-run Y6d's C2 scripts, but I independently extracted and executed the discovery, gate, and nest() blocks verbatim in my own harness (P1, P2, P3, P5 below), which confirms those blocks behave as C2 reports.

## Findings

### A1 (HIGH, H2/H3): backend gate is single-shot, false-fails a slow start

Runner lines 216-219: `sleep 5`, then one `grep -a -q "Wayland backend"`. No retry. The discovery loop directly below it (lines 225-238) retries for 10s, so the launcher tolerates 10s of socket lag but 0s of backend-line lag past the fixed 5s sleep. The signature dir appears early in Hyprland startup while backend init follows, so on a loaded machine the line can legitimately land after the gate's single check.

Reproduction (P3, verbatim gate block with `sleep 5`, log gains the line at t=6s):

```
$ bash -c '...; sleep 5; [ -f "$NEST_LOG" ] || fail ...; grep -a -q "Wayland backend" "$NEST_LOG" || fail "Wayland backend did not start in nested log ..."'
FAIL: Wayland backend did not start in nested log /tmp/y6d-rt-gate-PAFCpV/hyprland.log
P3-GATE-RC=1, ELAPSED: 5s
$ grep -c "Wayland backend" <log>   # after t=6s
1
```

Contrast, same harness, verbatim discovery block with the socket appearing at t=6s: `P3-DISC-LATE rc=0 NEST_DISPLAY=wayland-1`, elapsed 7s. The retry loop absorbs the lag; the gate does not.

Fix 1 (runner lines 216-219, replace with a 10s retry loop plus the exact line, and surface stdout on failure):

```
BACKEND_OK=""
for i in $(seq 1 10); do
  if grep -a -q "Starting the Wayland backend!" "$NEST_LOG" 2>/dev/null; then BACKEND_OK=1; break; fi
  sleep 1
done
if [ -n "$BACKEND_OK" ]; then grep -a "Starting the Wayland backend!" "$NEST_LOG" | head -3;
else tail -20 "$LOG"; fail "Wayland backend did not start in nested log $NEST_LOG (stdout tail above)"; fi
```

This also folds in C2 below (exact-line grep) and the H3 stdout pointer.

### A2 (HIGH, H6): pill death after t=1s burns the full 45s with a misleading message

Runner lines 325-329: `sleep 1; kill -0 $PILL_PID || fail "pill process died immediately"`, then a 45s loop that only greps for `Y6-NEST-PILL: ready` and never re-checks pill liveness. Any pill death in seconds 1-45 (slow import failure, `Native()` failure, `show` failure) burns the whole wait and then reports `pill did not become ready in 45s`, which reads as slowness, not death, even though the traceback is sitting in `nest-pill.log`.

Note on the literal KeyError: the pill does `os.environ["WAYLAND_DISPLAY"]` (pill line 24), but the launcher always sets `WAYLAND_DISPLAY="$NEST_DISPLAY"` from a non-empty discovered value, so the KeyError itself is NOT reachable through the launcher. The proven defect is the general missing liveness re-check, not the KeyError. The proof below uses a KeyError traceback only as a payload for "pill dies at t=2s with a traceback".

Reproduction (P4, verbatim wait block; fake pill sleeps 2s, prints a traceback, exits 1):

```
Y6-WAYLAND: FAIL: pill did not become ready in 45s (see /tmp/y6d-rt-pill-HusPew/nest-pill.log)
P4-RC=1 ELAPSED=46s (pill died at t=2s)
Traceback (most recent call last):
  File "run-nested-pill.py", line 22, in <module>
KeyError: 'WAYLAND_DISPLAY'
```

44s burned after the process was already dead, and the final message hides the cause that the log holds.

Fix 2 (runner line 328, add a liveness check inside the loop):

```
for i in $(seq 1 45); do sleep 1; kill -0 "$PILL_PID" 2>/dev/null || fail "pill died during ready wait (see $NEST/nest-pill.log)"; grep -q "Y6-NEST-PILL: ready" "$NEST/nest-pill.log" 2>/dev/null && READY=1 && break; done
```

### A3 (HIGH, H5): a retry with the current conf fails fast but misdiagnoses; the only guard is a comment

The conf still loads backup 1 (conf line 16: `hl.plugin.load("~/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so")`), which is dead ABI (Y6c F1). The conf comment `do NOT run the measurement with backup 1` is comment-only; no code in the runner checks it, and the runner contains zero `ldd` references (`grep -c ldd` on the runner returns 0).

Fail-fast is confirmed: with plugin-list JSON `[]`, the verbatim gate (runner line 244) fails at once, rc=1, `FAIL: hyprglass not in nested plugin list`. No 60s liquid burn. But the diagnosis is wrong in two ways, both proven from Y6c evidence:

1. Config-time `hl.plugin.load()` of the dead `.so` logs NOTHING in either nest log. In `probe2-hyprland.log` and `probe2-nosocket.log`, the only lines matching `plugin|hyprglass|load` are the hook marker `Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)` and the `postConfigReload` stdout-disable line. The libaquamarine error appears only via an interactive `hyprctl plugin load` (Y6c probe 3 terminal output), which the runner never runs. So the runner's fail message `hyprglass not in nested plugin list` gives the operator no hint of dead ABI.
2. The hook-marker check (runner line 265) is unreachable on this path: the plugin-list gate at line 244 fails first, so the `count=0 version=nil` evidence is never surfaced.

Fix 3 (runner, before the nest launch, after the preconditions block): pre-flight ABI check on the conf's plugin path, failing in under a second with the cause:

```
GLASS_SO=$(grep -o '/[^"]*hyprglass\.so' "$CONF" | head -1)
[ -n "$GLASS_SO" ] || fail "no hyprglass.so path in conf $CONF"
MISSING_LIBS=$(ldd "$GLASS_SO" 2>/dev/null | grep "not found" || true)
[ -z "$MISSING_LIBS" ] || fail "hyprglass $GLASS_SO cannot load (dead ABI): $MISSING_LIBS"
```

Fix 3b (runner line 244, surface the hook evidence on the plugin-list fail):

```
grep -q hyprglass "$NEST/nest-plugin-list.json" || { grep -a -h "Y6-NEST-HOOK" "$LOG" "$NEST_LOG" 2>/dev/null; fail "hyprglass not in nested plugin list (hook marker above, if any)"; }
```

### B1 (MEDIUM, H1): discovery picks a DEAD socket, no liveness check

The discovery block (lines 225-238) tests only `[ -S "$s" ]`. A unix socket file survives its process: if the nest writes the backend line, creates its socket, then dies before discovery, the file remains and discovery picks it. The next step then fails at `hyprctl` with a misleading message instead of `nest died`.

Reproduction (P1, verbatim discovery block; fixture socket bound then closed with no listener, plus a `.lock` file):

```
P1-CONNECT: refused as expected: [Errno 111] Connection refused
Y6-WAYLAND: nested socket wayland-1
P1-RESULT rc=0 NEST_DISPLAY=wayland-1
```

Discovery returned rc=0 for a socket nothing listens on. Reachability needs nest death in the short window between the backend gate and discovery; the consequence is misdiagnosis, not a false pass (the later `hyprctl` step still fails).

Fix 4 (runner discovery loop, after the `[ -S "$s" ]` check, before the ambiguous check): skip candidates that refuse a connection, so the loop keeps waiting for the live socket instead of accepting a dead one:

```
python3 -c "import socket,sys; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); sys.exit(0 if s.connect_ex(sys.argv[1])==0 else 1)" "$s" 2>/dev/null || continue
```

### B2 (MEDIUM, H7): nest() guard is masked inside command substitution

Runner line 240: `NEST_OUTPUT=$(nest hyprctl -j monitors 2>/dev/null | python3 -c "..." 2>/dev/null || echo "WAYLAND-1")`. If the `nest()` guard (line 89) fires here, `fail()` exits only the subshell, the FAIL text goes into the pipe (python3 fails to parse it), and `|| echo "WAYLAND-1"` silently substitutes the fallback. The script continues with a possibly wrong output name and fails later at the plugin-list step with the wrong message.

Reproduction (P5, verbatim `nest()` def plus verbatim line 240, `NEST_DISPLAY=""`):

```
P5-NEST_OUTPUT rc=0 NEST_OUTPUT=WAYLAND-1
P5: SCRIPT CONTINUED past the guard (no exit, no FAIL visible to operator)
```

Same masking in the second `$(...)` site: `PILL_GEOM=$(read_pill_geom)` with the guard firing yields the OUTER message `pill surface not found in nested layers (pill not visible)` (P5b proof); it still fails, but the guard text never reaches the operator.

Reachability: NOT reachable in the shipped order. All `nest()` calls are post-discovery, discovery guarantees non-empty `NEST_DISPLAY`, and nothing reassigns it to empty afterwards. This is a latent defect, not a live hole. Fix it anyway because the guard's whole purpose is fail-closed, and this call site defeats it.

Fix 5 (runner line 240, run `nest` outside the substitution so its failure is fatal):

```
nest hyprctl -j monitors > "$NEST/nest-monitors.json" 2>/dev/null || fail "nested hyprctl monitors failed (nest dead or display wrong)"
NEST_OUTPUT=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d[0]['name'])" "$NEST/nest-monitors.json" 2>/dev/null || echo "WAYLAND-1")
```

### B3 (MEDIUM, H3): no liveness check on the nested Hyprland PID after the backend gate

`NEST_HYPRLAND_PID` is recorded at line 210 via `pgrep -P` but never `kill -0` checked. If the nest dies after writing the backend line, the gate passes (A1 fix does not cover this), discovery picks the leftover socket (B1), and the run fails later with a misleading message. Fix 6 (runner, immediately after the backend gate, before discovery):

```
[ -n "$NEST_HYPRLAND_PID" ] && kill -0 "$NEST_HYPRLAND_PID" 2>/dev/null || fail "nested Hyprland died after backend start (pid ${NEST_HYPRLAND_PID:-unknown})"
```

### B4 (MEDIUM, H8): C2 does not exercise the changed lines it claims to cover

Checked by grepping `/tmp/y6d-c2-vm.py` and `/tmp/y6d-c2-laptop.sh`:

- The cleanup block (runner lines 179-180) is never tested: no `stale` or `cleanup` mention in C2-vm.
- No socket-appears-mid-loop case: no `mid-loop`, `dead socket`, or `appear` mention in C2-vm. The `no socket` case runs the full 10s, but nothing proves the loop accepts a late socket (my P3 proof covers this independently).
- No dead-socket case (my P1 proof covers it independently).
- No env-propagation test: no `NEST_DISPLAY` mention in C2-laptop, and C2-vm never checks that mpv or the pill receive the discovered display. The three env substitutions (mpv x2, pill x1) are untested changed lines.
- GRIM-A in `c2-laptop.log` failed silently: the log line `grim space form inside live output: expect file created` is followed by `supplied geometry did not intersect with any outputs` and there is NO `GRIM-A OK` line anywhere in the log, yet no FAIL was recorded. The script line is `grim -g "100,100 200x200" /tmp/y6d-grim-a.png && echo "GRIM-A OK ..."` with no assertion. (The 2464,902 geometry did succeed with 37,475 bytes, so this is a wrong expectation for the live output geometry, not a runner bug, but the test passed a violated expectation silently.)

Fix 8 (C2): add to C2-vm a cleanup-block test, a socket-appears-at-6s test, a dead-socket test, and an env-propagation test (run the mpv/pill env lines with a stub that prints `WAYLAND_DISPLAY`); in C2-laptop assert GRIM-A (file must exist) and derive the test geometry from the live output geometry instead of hardcoding `100,100`. Re-run the full C2 after Fixes 1-7.

## Hypotheses disposition

- H1 (wrong socket): PARTLY CONFIRMED. No wrong-live-socket path exists (only the nest writes to RUN_DIR, parent socket lives elsewhere, cleanup removes stale entries). But dead-socket pick is proven (B1), and any foreign `wayland-*` socket present during the ~20s launch-to-discovery window causes an immediate ambiguous false-fail (P2 proof: live `wayland-1` plus foreign `wayland-9` held by another process gives `FAIL: ambiguous nested Wayland sockets`, rc=1). Reachability of the foreign case is low (flock plus the runner-quiet process check block concurrent runners; only the nest writes there), so no fix beyond B1. Dangling symlink: proven to survive cleanup (`[ -e ]` is false for dangling links, P2b), but discovery skips it too (`[ -S ]` false), so it cannot be picked; whether it breaks the nest's bind is UNVERIFIED (cannot test without launching a nest) and nothing creates such links, so LOW. Fix 7 (runner line 180): `[ -e "$stale" ] || [ -L "$stale" ]`.
- H2 (discovery false-fail): DISCOVERY LOOP SOUND, gate is the problem. The 10s loop absorbs a socket appearing at t=6s (P3, rc=0 in 7s). The false-fail lives in the backend gate (A1), not the discovery loop.
- H3 (backend gate false-fail / false-pass): NO FALSE-PASS on observed logs (V2 above); false-fail proven (A1); missing liveness check proven as a gap (B3).
- H4 (hook marker source): CLEARS. The marker is emitted by Lua `print()` (hook line 18, via `hlPrint`) and appears in BOTH logs in all three Y6c probes (count 1 in each stdout log and each per-instance log). `$LOG` remains a valid source because the hook runs at config time, before `postConfigReload` disables stdout logging. The dual grep at line 265 covers both paths. No fix, except Fix 3b surfacing the marker on the plugin-list fail path where the check is currently unreachable.
- H5 (conf still loads backup 1): CONFIRMED as fail-fast-but-misdiagnosing (A3). The retry burns about 30s to the plugin-list gate and fails with a message that hides the dead ABI; the config-time load is silent in both logs.
- H6 (pill KeyError / 45s burn): KEYERROR ITSELF UNREACHABLE via the launcher (env always set); 45s BURN PROVEN (A2).
- H7 (guard in command substitution): MASKING PROVEN, reachability REFUTED in the shipped order (B2). Latent only.
- H8 (C2 gaps): CONFIRMED (B4). The discovery fixture itself is faithful for what it tests (real unix sockets via `bind`, real `.lock` file; `[ -S ]` behaves identically for a nest socket), but four changed behaviors have no test and one laptop expectation failed silently.

## What was NOT tested

- No nested Hyprland was launched (forbidden by scope), so the v3 launch line itself (drop `--socket`) is verified only statically plus Y6c probe 1 evidence, not by executing it. The retry run remains the only execution proof for F0.
- No live-session state was changed. The only laptop access was read-only `md5sum` and `cat`/`ls` via `~/workspace/ssh-laptop.sh`.
- The rebuilt plugin path is not wired up anywhere in v3 (by design, pending the blocked rebuild); the conf still points at backup 1. Fix 3 makes that fail in under a second with the cause instead of after a nest launch.

## Fix checklist for adjudication

1. Fix 1 (A1): gate retry loop, runner lines 216-219.
2. Fix 2 (A2): pill liveness re-check, runner line 328.
3. Fix 3 + 3b (A3): pre-flight `ldd` check before launch; surface hook marker on plugin-list fail, runner lines 244 and pre-launch.
4. Fix 4 (B1): socket connect probe in discovery, runner lines 225-238.
5. Fix 5 (B2): `nest hyprctl monitors` outside `$()`, runner line 240.
6. Fix 6 (B3): `kill -0 $NEST_HYPRLAND_PID` after the gate, runner after line 219.
7. Fix 7 (C1): cleanup removes dangling symlinks, runner line 180.
8. Fix 8 (B4): extend C2 (cleanup, late socket, dead socket, env propagation, GRIM-A assertion) and re-run the full C2 after Fixes 1-7.
9. Re-verify md5s (repo vs laptop) after the fixes land; do NOT run the measurement retry until the rebuild lands and the conf plugin path is switched from backup 1.

## Verdict restated

AMEND. No false-pass, no live-session risk, all defects fail closed. Apply Fixes 1-8, re-run C2, then the launcher is ready for the retry once the rebuilt plugin path is wired in.

# Council 1 (feasibility) verdict: Y6d v3 launcher fixes

- Council: Council 1, feasibility of the v3 launcher fixes only.
- Date: 2026-11-21, audit run 20:58 to 21:02 +07.
- Verdict: **AMEND**. Three exact one-line fixes below, all latent defense in depth, none reachable in the current flow. No hole with a reproduction was found, so this is not a BLOCK. After the fixes, re-run the C2 VM script and re-check md5s. No new live run and no full re-review is needed for these fixes.
- Scope boundary: this verdict covers the launcher fixes only. It does NOT authorize a measurement run. The conf still loads backup 1 hyprglass, which Y6c proved cannot load on this machine (F1, dead ABI), and the rebuild is blocked pending an explicit user go-ahead on the fetched commit. Any retry run needs the rebuilt plugin path wired up plus a fresh review.

## Files reviewed

- Repo `~/workspace/computer-use-wayland`, branch `todolist-push`.
- Diff: `improvements/y6d-evidence/v3-diff.txt` (188 lines). Verified byte-identical to the live worktree diff against `origin/todolist-push` for the same three files (`diff` produced no output, both 188 lines).
- Fixed files and repo md5s (verified by this council):
  - `improvements/worker-y6b-run-nested-wayland-v2.sh`, md5 `c7c1d6f2c3aed3f912def4bd4d2c7fcc`, 527 lines.
  - `improvements/worker-y6b-run-nested-pill-v2.py`, md5 `eea0c320746bae4fc92c1f511cc803cb`, 52 lines.
  - `improvements/worker-y6b-hyprland-wayland-v2.lua`, md5 `0d4ac7a9c2437fb48ecfc505ccd9046b`, 19 lines.
- V2 originals read via `git show origin/todolist-push:<path>` in the computer-use-wayland repo only. V2 runner md5 `8cd00a16d417bc49595ebc6cb775ce99` matches the Y6c log.
- Evidence read: `improvements/y6d-evidence/c2-vm.log`, `improvements/y6d-evidence/c2-laptop.log`, `improvements/worker-y6d-rebuild-log.md`, `improvements/worker-y6c-nested-run-log.md`, Y6c probe logs in `improvements/y6c-evidence/`.
- Test scripts read and re-executed: `/tmp/y6d-c2-vm.py` (re-run by this council, all PASS, rc 0, see below). `/tmp/y6d-c2-laptop.sh` read only; its log was checked against the script, not re-run live, because this council does not touch the live session.
- Not done, per brief: no Zen driving, no nested Hyprland launch, no live session contact, no hyprglass checkout, build, or load, no git command in the vendor repo.

## Time log (all +07, 2026-11-21)

- 20:58: read v3 diff, Y6d log, Y6c log.
- 20:59: read the three v3 files in full; enumerated every `nest()` call site.
- 21:00: verified worktree diff identical to `v3-diff.txt`; re-ran `/tmp/y6d-c2-vm.py` (about 10 s, all PASS).
- 21:00: read Y6c probe per-instance logs; confirmed backend line placement.
- 21:01: independent edge tests E1 to E5 (about 36 s); pill env tests P1, P2; static sweep for dashes and ydotool.
- 21:01: laptop md5 check via `ssh-laptop.sh`, one short call (about 4 s), all three match.
- 21:02: audit complete, verdict paper written.

## Finding 1: socket discovery. PASS with three latent notes (see AMEND list)

Audit order item (1).

- Timing. The launch phase budget is: pidfile wait up to 10 s, signature wait up to 15 s, `sleep 5`, backend gate, then the discovery loop up to 10 s. Worst case about 40 s from launch to discovery end. Y6c probe 1 observed the nest socket present by 12 s after launch. The discovery loop itself only spends time on the failure path: on a healthy start the first scan finds the socket and breaks, so it costs nothing.
- The gate line and the socket. The per-instance log line `Starting the Wayland backend!` is logged at backend start and the socket bind follows inside the same backend construction, so the gap is a local syscall, far under one second. Even if the order were reversed, the 10 s retry loop covers any lag under 10 s, and a lag over 10 s between a log line and a local `bind()` is not a credible failure mode. The loop retries 10 scans with 1 s sleeps, so the fail message `after 10s` is accurate.
- `.lock` skipping. The `case "$s" in *.lock) continue;; esac` skips lock files before the socket test. Proven by C2 (one socket plus lock file yields `wayland-1`) and by edge test E3 below.
- Stale sockets. Cleanup before launch removes every `wayland-*` entry (see Finding 6). The nest is the only writer to the private run dir, so no foreign socket can appear.
- More than one socket. Hyprland creates exactly one display socket per instance plus one `.lock` file. Y6c probe 1 observed exactly that: one socket (`wayland-1`) plus its lock. XWayland creates no `wayland-*` entry. If two sockets ever did appear, the script fails loudly with `ambiguous nested Wayland sockets` instead of guessing. That branch is defense in depth, and it is correct to fail rather than pick one.
- Name versus path semantics. `WAYLAND_DISPLAY` is a bare name when it contains no slash, resolved under `XDG_RUNTIME_DIR`. Discovery stores only the basename (`wayland-1`), and every consumer sets `XDG_RUNTIME_DIR` to the nest run dir alongside it: `nest()`, both mpv launches, and the pill launch. The launcher export `WAYLAND_DISPLAY` is the absolute live socket path, but each of those launches overrides it with an `env` prefix, so the parent display can never leak into a nest client. Correct.
- Debate. Counter-claim: the nest auto-name could be something other than `wayland-1` on a later run, and a hardcoded name would break. Answer: discovery does not assume any name, it takes whatever single `wayland-*` socket exists, so the observed `wayland-1` is only an example, not an assumption. Counter-claim: the gate passing does not strictly prove the socket exists yet. Answer: accepted, but the retry loop makes the distinction moot, as argued above.

## Finding 2: `nest()` guard, every call site. PASS, one latent note (AMEND A1)

Audit order item (2). Discovery ends at line 236 (`[ -n "$NEST_DISPLAY" ] || fail`), first `nest()` use is line 240. Complete call-site table in script order:

| Line | Call | Before or after discovery (ends line 236) |
| --- | --- | --- |
| 240 | `NEST_OUTPUT=$(nest hyprctl -j monitors ...)` | After |
| 243 | `nest hyprctl -j plugin list` | After |
| 245 | `nest hyprctl -j hyprglass status` | After |
| 274 | `nest python3 -` (liquid gate heredoc) | After |
| 310, 312 | `nest grim -o` (positive control frames) | After |
| 336 | `nest hyprctl -j layers` inside `read_pill_geom()` | Defined line 336, first invoked after pill start (line 340+), after |
| 382 | `nest grim -g` inside `capture()` | Defined line 382, first invoked in arm A, after |
| 457, 459 | `nest grim -o` (arm B motion re-validation) | After |

No `nest()` call exists in the pre-launch section, in `teardown()` (which uses `live()` only), or in any other function invoked before discovery. `NEST_DISPLAY` is initialized to empty at line 57, so the guard cannot trip on an unbound variable under `set -u`.

- Latent note (AMEND A1). The guard `fail` inside a command substitution does not kill the parent shell: `exit 1` in a subshell exits only the subshell. Edge test E5 proves this (parent survived, rc 0, subshell reported failure). The first call site, line 240, is inside `$(...)`, and its `|| echo "WAYLAND-1"` fallback would mask a guard trip with a wrong default output name. Reachability: the guard cannot fire at line 240 in the current flow, because line 236 already fails the script if `NEST_DISPLAY` is empty and nothing reassigns it between lines 236 and 240. And if it somehow did fire, line 243 is a direct call and would fail loudly one step later. So this is latent only, with a one-step backstop. But the comment at lines 87-88 claims the guard is fail-closed, and at line 240 that claim is literally false. One explicit pre-check before line 240 makes the claim true. See AMEND A1.
- Debate. Counter-claim: an unreachable weakness is not a finding. Answer: the weakness is real and demonstrated (E5), the fix is one line, and the rebuild block means there is no schedule cost to fixing it now. A guard whose contract is false at its first call site should not ship as written.

## Finding 3: pill environment. PASS, one latent note (AMEND A2)

Audit order item (3).

- Launcher line 323 passes the discovered display explicitly: `env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" Y6_NEST_SIG="$SIG" python3 "$PILL"`. The pill reads `os.environ["WAYLAND_DISPLAY"]` at line 23 of the pill file and copies it into the env dict passed to `indicator.Native(env)`. The chain from discovery to the pill process is complete, with no hardcoded name left.
- Loud on missing. Test P1 proves a missing `WAYLAND_DISPLAY` raises `KeyError` at pill startup, before any `ready` print. The launcher then catches the dead pill twice: the 1 s `kill -0` check fails with `pill process died immediately`, and the 45 s ready wait fails if the death is slower. Not silent.
- Latent note (AMEND A2). Test P2 proves an empty-string `WAYLAND_DISPLAY` does NOT raise `KeyError` (`os.environ` returns `""`), so the pill would proceed to `Native` with an empty display. Reachability: empty requires `NEST_DISPLAY` empty at line 323, which line 236 already makes impossible. And even if reached, the native connect with an empty display fails and the pill exits 1 with a `show failed` print, so it still fails loudly, just with a less direct message. Latent only. One explicit empty check makes the comment `fail loudly if it is missing` true for the empty case too. See AMEND A2.
- No other pill env gap. `Y6_NEST_SIG` is exported at line 206 before the pill launch, and the pill reads it at line 24. `XDG_RUNTIME_DIR` is set to the nest run dir in both the launcher prefix and the pill env dict.

## Finding 4: 10 s discovery loop against the 15 s SIG wait plus 5 s sleep. PASS

Audit order item (4).

- The three waits are sequential, not competing: the signature wait finds the instance dir (created early in startup), the 5 s sleep lets the backend log line land, the gate checks it, and only then does discovery run. By discovery start the nest has had signature time plus 5 s, and the loop adds up to 10 s more. Total worst-case launch budget about 40 s, against a probe-observed socket at 12 s.
- The loop cannot starve the nest: it only waits when the socket is absent, and it breaks on the first scan that finds one. No sleep is consumed on the healthy path.
- Debate. Counter-claim: the 5 s sleep before the gate is the tight step, not the discovery loop: if the signature appears at 1 s but backend init takes over 6 s, the gate false-fails a healthy nest. Answer: that timing predates v3 (v2 had the same sleep and gate shape) and is outside this council scope, but it is recorded here for the next runner review: the gate has no retry, while discovery does. On the probe evidence the backend line lands within seconds of the signature, so the risk is low, but a gate retry loop would be strictly safer. This is a note, not an AMEND item, because v3 did not change that step.

## Finding 5: backend gate greps the per-instance log. PASS

Audit order item (5).

- Coverage of the healthy case. Y6c probe 2 per-instance log has `Starting the Wayland backend!` at line 28, and the stdout logs have zero matches for `Wayland backend`. The probe log also shows why: `Disabling stdout logs (debug.enable_stdout_logs = 0)` is logged before the backend line, so on a healthy start the line goes only to the per-instance log. The v3 gate greps `NEST_LOG`, defined at line 207 right after signature discovery, and matches the substring `Wayland backend`, which covers the observed wording. C2 gate cases (present passes, absent fails) were re-run by this council and pass.
- Missing-file fail. Line 217 `[ -f "$NEST_LOG" ] || fail` fires before any grep. The 5 s sleep before the gate means that by gate time a live nest has created its log file, so a missing file at that point means the nest died between signature creation and log creation, and failing is correct.
- Early-death path. If the nest dies before the signature appears, the script fails earlier at the 15 s signature wait and never reaches the gate. If it dies after the signature but before the backend line, the log file exists, the grep finds nothing, and the gate fails. Every early-death shape fails loudly at or before the gate. No silent pass.
- Limit, debated and accepted. The gate is necessary, not sufficient: the `Starting the Wayland backend!` line proves the backend started logging, not that it finished starting or that the socket is accepting connections. A nest that logs the line then dies would pass the gate and fail at the next step (`nest hyprctl plugin list`, line 243). That is acceptable: the gate is one check in a chain, and the downstream checks are gating too. No change requested.

## Finding 6: stale-socket cleanup glob. PASS, one cosmetic note (AMEND A3)

Audit order item (6).

- The cleanup at lines 177-180 removes `$RUN_DIR/hypr` (old signatures) and then every `wayland-*` entry in the run dir before launch. It runs after the flock is held and after the pre-launch checks, so no concurrent runner can recreate a stale entry, and the live socket (`/run/user/1000/wayland-1`) is in a different directory and untouched.
- Edge test E4 proves the glob removes a socket, a `.lock` file, a regular file, and a directory. The guard `[ -e "$stale" ]` correctly makes the loop a no-op when the glob matches nothing (unexpanded pattern fails the existence test).
- Cosmetic note (AMEND A3). E4 also proves a dangling symlink named `wayland-7` survives the cleanup, because `[ -e ]` is false for a dangling link. Impact is nil: edge test E3 proves discovery skips a dangling symlink (`[ -S ]` is false for it), and nothing in this system creates `wayland-*` symlinks. Adding `|| [ -L "$stale" ]` removes the leftover. See AMEND A3.
- Debate. Counter-claim: a symlink to a live socket would pass `[ -S ]` and could confuse discovery. Answer: no component here creates symlinks in the run dir, and cleanup would remove a non-dangling symlink anyway (`[ -e ]` follows the link). The scenario requires an outside actor planting a symlink in a private temp dir, which is outside the threat model for this runner.

## Independent re-verification by this council

- C2 VM re-run: `python3 /tmp/y6d-c2-vm.py`, rc 0, all checks PASS, identical to `c2-vm.log`: verdict logic 16/16 combos with exactly 1 VERDICT line, discovery one socket plus lock yields `wayland-1`, two sockets ambiguous fail, no socket missing fail after 10 s, backend gate present passes and absent or missing file fails, `nest()` guard empty fails closed and set runs, no `pkill -x` in code, no em or en dash, `timeout 600` present, no `--socket` in code, no hardcoded `wayland-y6`, tee plus timestamped frames dir present.
- C2 laptop log checked against `/tmp/y6d-c2-laptop.sh` by reading: the script does what the log claims (parser extraction, grim forms, teardown harness with all four asserts). Not re-executed live, per brief.
- Edge tests E1 to E5 (verbatim extraction of the v3 discovery block and guard, run on this VM):
  - E1: regular file `wayland-9` plus real socket `wayland-1` yields `wayland-1`, rc 0.
  - E2: directory `wayland-3` plus real socket yields `wayland-1`, rc 0.
  - E3: dangling symlink `wayland-9` plus real socket yields `wayland-1`, rc 0.
  - E4: cleanup removes socket, lock, regular file, and directory; dangling symlink `wayland-7` survives (AMEND A3).
  - E5: guard `fail` inside `$(...)` prints the FAIL line but the parent shell survives with rc 0 (AMEND A1).
- Pill env tests P1, P2 (exact pill line semantics):
  - P1: missing `WAYLAND_DISPLAY` raises `KeyError` loudly.
  - P2: empty `WAYLAND_DISPLAY` does not raise `KeyError` (AMEND A2).
- Laptop copies verified read-only via `ssh-laptop.sh`, single short call, rc 0. All three md5s match the repo exactly: runner `c7c1d6f2c3aed3f912def4bd4d2c7fcc`, pill `eea0c320746bae4fc92c1f511cc803cb`, conf `0d4ac7a9c2437fb48ecfc505ccd9046b`.
- Static sweep on all three v3 files: no em dash, no en dash, no ydotool, zero `--socket` in executable code. The only `--socket` mentions are comments documenting the removal (shell `#` comments in the runner, Lua `--` comments in the conf). The only remaining `wayland-y6` string in the three files is the pill comment at line 23 documenting the change.
- Confirmed: the lua conf still loads backup 1 hyprglass (line 16). That is F1, out of scope here, and it is why no run is authorized by this verdict.

## AMEND list: exact fixes

All three are one-line, behavior-neutral on every reachable path, and cheap while the rebuild is blocked. Apply, then re-run `/tmp/y6d-c2-vm.py` and re-check md5s.

- A1. File `improvements/worker-y6b-run-nested-wayland-v2.sh`, insert before line 240 (the `NEST_OUTPUT=$(nest ...)` assignment). Add a direct, non-subshell pre-check so the guard is fail-closed at its first call site too:
  - `[ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"`
- A2. File `improvements/worker-y6b-run-nested-pill-v2.py`, replace line 23 (`env["WAYLAND_DISPLAY"] = os.environ["WAYLAND_DISPLAY"]`) with an explicit empty check:
  - `_disp = os.environ["WAYLAND_DISPLAY"]`
  - `if not _disp: raise SystemExit("Y6-NEST-PILL: WAYLAND_DISPLAY empty, launcher did not pass a socket name")`
  - `env["WAYLAND_DISPLAY"] = _disp`
- A3. File `improvements/worker-y6b-run-nested-wayland-v2.sh`, line 180, extend the cleanup guard so dangling symlinks are removed too:
  - `for stale in "$RUN_DIR"/wayland-*; do if [ -e "$stale" ] || [ -L "$stale" ]; then rm -rf "$stale"; fi; done`

## Dissent record

- Dissent for GO now: the three AMEND items are all unreachable in the current flow, each with a fail-closed backstop one step later (line 243 for A1, native connect failure for A2, discovery skip for A3). On that view the verdict should be GO with hardening recommendations applied opportunistically, to avoid another review cycle over zero behavioral change.
- Answer adopted by this council: the fixes are one line each, the rebuild block means no run is waiting on them, and two of the three repair a written claim that is currently false (the guard is not fail-closed in a subshell; the pill does not fail loudly on an empty display). A guard whose contract is false at its first call site should not ship as written. AMEND stands. No dissent on the substance of any finding, only on whether the fixes gate the verdict.

## What this verdict does not cover

- F1 (hyprglass dead ABI) is untouched by v3 and still blocks any measurement run. The conf plugin line is unchanged by design.
- The rebuild review stays open and is not covered by this round.
- The 5 s sleep before the backend gate has no retry (Finding 4 note). Recorded for the next runner review, not an AMEND item here.
- Socket creation timing rests on Y6c probe evidence plus the 10 s retry loop, not on reading aquamarine source. No live nest was launched by this council.

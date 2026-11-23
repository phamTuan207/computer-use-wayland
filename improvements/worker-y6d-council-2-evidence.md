# Council 2 (evidence) verdict: Worker Y6d v3 launcher fixes

- Council: Council 2 (evidence). Reviewer: independent council agent.
- Date: 2026-11-21. Review window: 20:58 to 21:03 +07 (13:58 to 14:03 UTC).
- Scope: LAUNCHER FIXES ONLY. The hyprglass rebuild and the nested load test
  are BLOCKED by an execution-risk check on a fetched commit and are NOT
  covered by this verdict.
- Inputs: repo `~/workspace/computer-use-wayland`, branch `todolist-push`,
  working tree v3 files (uncommitted); diff
  `improvements/y6d-evidence/v3-diff.txt` (188 lines); C2 evidence
  `improvements/y6d-evidence/c2-vm.log` and `c2-laptop.log`; test scripts
  `/tmp/y6d-c2-vm.py` and `/tmp/y6d-c2-laptop.sh`; worker log
  `improvements/worker-y6d-rebuild-log.md`; background
  `improvements/worker-y6c-nested-run-log.md` plus `improvements/y6c-evidence/`.
- Method: every C2 claim re-checked independently. No live driving, no nested
  Hyprland run, no browser work, no git command in any vendor repo, no build
  or load of any plugin, no touch of the live session. All laptop checks were
  read-only (`md5sum`, `wc -l`, `stat`, `ls`, `cat`) through the SSH helper.

## Verdict: GO (launcher fixes only)

The v3 launcher fixes (F0 socket discovery, U5b per-instance log gate, pill
display handoff) are proven correct by the C2 re-run plus the extra checks in
this paper. Every changed line is either execution-tested or verified by diff
with a stated residual, and no changed line is left unverified. See the
coverage map below.

Boundaries of this GO, read them as part of the verdict:

1. GO covers the launcher fixes only. It does NOT authorize a measurement run.
2. F1 is NOT fixed: the conf still loads backup 1 hyprglass, which cannot load
   on this machine (dead ABI). The conf says so in a comment and forbids
   running the measurement with backup 1. A retry needs the rebuilt plugin
   wired in plus a re-review.
3. The first live v3 run still has to prove the launch line and the three
   environment substitutions end to end. They are proven statically here, not
   by a live nest run, because a live run needs the rebuilt plugin.
4. Do NOT commit on the strength of this paper alone; Muse adjudicates after
   council 3 and redteam.

## Time log (all checks, Asia/Ho_Chi_Minh)

- 20:58:23: read v3 diff, Y6d log, Y6c log; repo md5s match claimed v3 hashes;
  v2 originals from `origin/todolist-push` match Y6d baseline hashes.
- 20:59:11: re-ran `/tmp/y6d-c2-vm.py` myself, all PASS, output matches
  `c2-vm.log` except temp dir suffixes; `git diff` of the three files is
  byte-identical to `v3-diff.txt`.
- 20:59:32: independent extraction of verdict, discovery, gate, `nest()`
  blocks with line numbers; awk extraction of `read_pill_geom` (15 lines)
  and `teardown` (36 lines), both verbatim slices of the v3 file.
- 20:59:52: my own verdict harness, 16/16 combos with verdict strings;
  changed-line enumeration; `wayland-y6`, `--socket`, `pkill`, long-dash
  greps across all three v3 files.
- 21:00:45: discovery edge cases E1/E2/E3 (my fixtures), all PASS; NEST_LOG
  ordering; conf executable lines v2 vs v3 identical; pill line semantics in
  isolation; `2464,902` provenance; Y6c evidence log paths.
- 21:01:44: stale-cleanup block test (my test, Y6d ran none), PASS on a dirty
  dir and an empty dir; Y6c stdout logs have 0 backend matches, per-instance
  logs have 1 each.
- 21:01:51: laptop md5 verification (runtime copies, script, extracts, PNG).
- 21:02:47: laptop parser extract is byte-identical to my VM extraction.
- 21:02:57: laptop teardown extract is byte-identical to my VM extraction.
- 21:03:08: laptop repo checkout is at 4500a18 and lacks the Y6 files (older
  tree); the C2 source on the laptop is `/tmp/y6-nested`, not that checkout.
- 21:03:25: laptop `improvements/` listing confirms the older tree;
  `/tmp/y6-nested/` listing confirms Y6c run artifacts are present.

## 1. Extraction fidelity: PASS, no drift

I re-extracted each tested block myself from the v3 file and compared it with
what the C2 logs claim. All line numbers match exactly.

| Block | Claimed lines | Verified lines | Verbatim |
|---|---|---|---|
| Verdict block | 504-526 | 504-526 (23 lines) | yes, `sed -n 504,526p` |
| Discovery block | 221-237 | 221-237 (17 lines) | yes, `sed -n 221,237p` |
| Backend gate block | 217-219 | 217-219 (3 lines) | yes, `sed -n 217,219p` |
| `nest()` definition | line 89 | line 89 | yes, single line |
| `read_pill_geom` (laptop awk) | 15 lines | 15 lines, starts line 335 | yes, diff clean vs file slice |
| `teardown` (laptop awk) | 36 lines | 36 lines, starts line 96 | yes, diff clean vs file slice |

- `v3-diff.txt` (188 lines) is byte-identical to `git diff` of the three v3
  files against HEAD. The diff is a faithful record of the change.
- v2 baseline hashes from `git show origin/todolist-push`: runner
  `8cd00a16d417bc49595ebc6cb775ce99`, pill `3488c1812b0cd70b0629fb8c14fc5ae2`,
  conf `0e0dd3f63d50ad3a12d1f6a962f06098`. All match Y6d's log.
- v3 hashes in the working tree: runner `c7c1d6f2c3aed3f912def4bd4d2c7fcc`,
  pill `eea0c320746bae4fc92c1f511cc803cb`, conf
  `0d4ac7a9c2437fb48ecfc505ccd9046b`. All match Y6d's log.
- My re-run of `/tmp/y6d-c2-vm.py` at 20:59:11 reproduced every PASS line in
  `c2-vm.log` (verdict 16/16, discovery 3 cases, gate 3 cases, `nest()` 2
  cases, 7 static checks, `RESULT: all VM C2 checks PASS`).
- Note: the working tree also holds unrelated uncommitted changes (Y13 files,
  test files). `v3-diff.txt` covers only the three Y6 files, which is correct
  for this review; the other files are out of scope.

## 2. Coverage: every changed line, and what exercised it

Changed-line counts from `git diff --numstat` on the three files: runner 50
added / 15 removed, pill 3 / 1, conf 9 / 6. Line references below are v3 file
line numbers.

### Runner `worker-y6b-run-nested-wayland-v2.sh`

| Changed lines | What changed | Exercised by | Status |
|---|---|---|---|
| 2-7 header comments | v3 note, F0/U5b summary, plugin still backup 1 | reading (comment only) | PASS, no behavior |
| 57 `NEST_DISPLAY=""` | new empty default | NO Y6d test; Council 2 static check | PASS with residual (see R1) |
| 87-89 `nest()` comment + def | guard fails closed before discovery, uses `$NEST_DISPLAY` | VM test, empty/set, 2 cases, reproduced | PASS |
| 177-180 stale cleanup | `rm -rf hypr` plus guarded `wayland-*` glob loop | NO Y6d test; Council 2 tested, PASS (see C1) | PASS, gap closed by Council 2 |
| 183-186 parent comments | `--socket` removal documented | reading (comment only) | PASS, no behavior |
| 193 launch line | `--socket wayland-y6` removed | static only (no `--socket` in code) + Y6c probe 1 | PASS with residual (see R2) |
| 204-207 NEST_LOG definition | path defined after signature discovery | NO execution test of the line itself; static + ordering | PASS with residual (see R3) |
| 214-219 gate comments + code | gate greps `$NEST_LOG`, missing file fails first | VM test, 3 cases (present/absent/missing), reproduced | PASS |
| 221-237 discovery block | 10s scan, lock skipped, non-socket skipped, ambiguous fail, missing fail | VM test, 3 cases, reproduced; Council 2 E1/E2/E3, PASS | PASS |
| 264 hook comment | duplicate NEST_LOG assignment removed, comment left | grep: NEST_LOG assigned once (line 207); ordering checked | PASS |
| 298 mpv comment | `wayland-y6` wording replaced | reading (comment only) | PASS, no behavior |
| 300 backdrop mpv launch | `wayland-y6` to `"$NEST_DISPLAY"` | static only, single-token diff | PASS with residual (see R2) |
| 323 pill launch | `wayland-y6` to `"$NEST_DISPLAY"` | static only, single-token diff | PASS with residual (see R2) |
| 395 `start_mpv` | `wayland-y6` to `"$NEST_DISPLAY"` | static only, single-token diff | PASS with residual (see R2) |

### Pill `worker-y6b-run-nested-pill-v2.py`

| Changed lines | What changed | Exercised by | Status |
|---|---|---|---|
| 22-23 comments | change documented | reading (comment only) | PASS |
| 24 `env["WAYLAND_DISPLAY"] = os.environ["WAYLAND_DISPLAY"]` | hardcoded value replaced by launcher-passed value | Y6d: `py_compile` only; Council 2: semantics in isolation (present returns value, missing raises KeyError) | PASS with residual (see R4) |

### Conf `worker-y6b-hyprland-wayland-v2.lua`

All 9 added / 6 removed lines are `--` comments. The three executable lines
are byte-identical v2 vs v3: `hl.monitor(...)`, `hl.plugin.load(... backup 1
hyprglass.so)`, `dofile(... nested-visuals-hook.lua)`. No behavior change.
F1 is NOT fixed by v3, and the conf says so: switch to the rebuilt plugin
path once the rebuild lands, do NOT run the measurement with backup 1.

### Residuals (no changed line left unverified, but these need a live run)

- R1, line 57 init: the empty default is what lets the `nest()` guard run
  under `set -u` instead of aborting on an unbound variable. The guard test
  sets `NEST_DISPLAY` in its own harness, so it does not test the file's own
  init line. Static presence is confirmed; a live run exercises it for real.
- R2, launch line 193 and env lines 300/323/395: static proof only. Each is
  a single-token substitution verified in the diff, and the launch deletion
  is backed by live evidence (Y6c probe 1: same env, same conf, no
  `--socket`, nest started, socket auto-named `wayland-1`). The exact v3
  lines are proven only by the first live v3 run.
- R3, line 207 NEST_LOG definition: the gate test sets `NEST_LOG` in its
  harness, so it tests the gate logic, not the wiring from the definition.
  Wiring is verified statically: the path `$RUN_DIR/hypr/$SIG/hyprland.log`
  matches the Y6c probe evidence (`/tmp/y6-nested/run/hypr/<sig>/hyprland.log`,
  backend line present in the per-instance logs, 0 matches in every stdout
  log), and every use (lines 217, 218, 219, 265, 294) comes after line 207.
- R4, pill line 24: the pill file was never executed (it imports the
  indicator module from a laptop-only path, so only `py_compile` ran). The
  launcher wiring is verified statically: line 323 sets `WAYLAND_DISPLAY`
  in the pill's environment prefix, overriding the launcher's own exported
  live-socket value. A missing value raises KeyError and the pill exits 1,
  which the launcher reports as "pill process died immediately". That is
  fail-loud, as specified.

No changed line has zero verification. The four residuals are all of the form
"static proof now, live proof at the first v3 run", and none blocks this GO.

### C1. Stale cleanup, tested by Council 2 (Y6d ran no test)

I extracted lines 179-180 verbatim and ran them in a scratch dir at 21:01:44.
Dirty dir (socket `wayland-1`, `wayland-1.lock`, regular file `wayland-2`,
`hypr/` subdir, unrelated `keep.txt`): after the block only `keep.txt`
remained, intact, rc 0. Empty dir (no match): rc 0, no error, glob expands
to a literal path and `[ -e ]` is false. PASS. This closes Y6d's coverage gap.

### Static checks in the VM script, re-verified

- No `pkill -x` in code: the only two mentions are in comments (lines 299,
  384, "never by pkill -x"). The script's regex correctly excludes them.
- No long dashes in any of the three v3 files (0 in each).
- `timeout 600 Hyprland` present on the launch line.
- No `--socket` in any code line: all `--socket` mentions are in `#` comments
  (lines 4, 184, 185, 221). The launch line carries no `--socket`.
- No hardcoded `wayland-y6` in runner or conf (0 occurrences each). One
  mention remains in the pill, line 23, inside a comment documenting the
  change. Y6d's log states this accurately.
- Tee to timestamped run log and timestamped frames dir both present
  (unchanged regression checks).

## 3. Grim position note: proof intact, one label wrong

The laptop log says the `100,100 200x200` capture "did not intersect with any
outputs", and Y6d's log notes the live output is not at origin. That note is
correct and it does NOT weaken the format proof.

- The live monitor eDP-2 sits at layout offset 2464,902 (1920x1200). Source:
  `improvements/live-test-log.md` (monitor offset confirmed live) and
  `improvements/worker-y6b-council-2-evidence.md` (same offset, grim captures
  verified there). So `100,100 200x200` is outside every live output, and
  "did not intersect" is the correct position outcome for that geometry.
- The format proof rests on the Y6b geometry case, not on the 100,100 case:
  `grim -g "2464,902 200x200"` (inside eDP-2, top-left corner) created a file,
  37,475 bytes in the C2 laptop run. I confirmed the file exists on the laptop
  at `/tmp/y6d-grim-a2.png`, 37,475 bytes, and that `/tmp/y6d-grim-a.png`
  does NOT exist, which matches the log (no GRIM-A OK line).
- The other grim cases complete the proof by contrast: nest-style geometry
  `320,0 320x66` parses and reports "did not intersect" (not "invalid
  geometry"); the old comma form `2464,902,200,200` reports "invalid
  geometry"; `-g` plus `-o` reports "mutually exclusive". Space form parses,
  comma form does not, at any position.
- Editorial correction (non-blocking, for the Y6d log, not the code): the
  laptop log line "-- grim space form inside live output: expect file
  created" mislabels the 100,100 case. It is not inside any live output.
  The label should read "outside live output: expect did-not-intersect".
  The proof itself is intact via the Y6b geometry file creation.

## 4. Verdict-logic harness: faithful

- I wrote my own harness from scratch (different code from `/tmp/y6d-c2-vm.py`),
  extracting lines 504-526 by marker and running all 16
  (A_OUTCOME, B_OUTCOME) combos. Result at 20:59:52: 16/16, exactly 1 VERDICT
  line each, rc 0 each. Verdict strings match the intended branch in every
  combo (A reproduced wins, else B reproduced, else inconclusive, else both
  void, else the two single-negative cases, else both negative).
- The block references exactly 7 variables (`A_OUTCOME`, `B_OUTCOME`,
  `A_DIFF`, `A_BG_DIFF`, `B_PILL_DIFF`, `B_BG_DIFF`, `B_PILL_ONLY`), and the
  harness sets all 7. No other variable, no `fail` call, no file access.
- Scope differences between the harness and the real script do not change the
  outcome: the harness does not set `set -u` and does not include the trailing
  `exit 0`, but all 7 variables are set (so `set -u` cannot trip) and every
  branch ends in `echo` (so the final `echo done` returns 0, matching the
  real `exit 0` path). The harness redefines `fail` with a different prefix,
  but the block never calls `fail`.
- The `else` branch (uncovered outcome combination) never fires across all 16
  combos: with the 4-valued outcome domain, every combo is covered by an
  earlier branch. The `else` is dead code, inherited unchanged from v2, and
  harmless. It is not a v3 issue.
- Verdict logic is unchanged by v3 (the block is identical in v2 and v3).
  The harness proves the logic, not the arm outcomes; reachability of each
  combo in a live run is the retry runner's concern, not this review's.

## 5. Discovery test fixtures: faithful stand-in, gaps closed

Question: is a real unix socket plus a `.lock` file a faithful stand-in for
the nest's socket creation, or is there a meaningful difference in creation
order, permissions, or timing?

- For the logic under test (`[ -S ]` socket test, `*.lock` skip, count must
  be exactly 1), the stand-in is faithful. A python `AF_UNIX` socket passes
  `[ -S ]` exactly like a Hyprland socket, and a plain `.lock` file is
  skipped by the same `case` pattern.
- Creation order: the real nest creates the signature dir first and the
  socket may lag it. Y6d's fixtures had the socket present at t=0, so the
  retry path was untested by Y6d. I closed it with E3 (below): a socket
  appearing at t=3 is found, elapsed 3.0s.
- Timing: Y6d's no-socket case runs the full 10s loop and fails, which does
  exercise the retry loop and the cap. My E2 confirms the cap is exactly
  10.0s in the lock-only case too.
- Permissions: untested by Y6d and by me, and immaterial here. `[ -S ]` is
  permission-agnostic, and both the nest socket and the fixture socket are
  created by the same user id, so a connect by the same user behaves the same.
- One real difference remains, bounded: in a live run the nest populates
  `RUN_DIR` concurrently while the scan runs. The scan handles that with the
  10s retry plus the ambiguous-fail (two or more sockets refuse). Only one
  nest runs at a time and the stale cleanup clears previous sockets, so a
  second socket means stale state or a second Hyprland, and refusing is the
  correct response.

My extra fixtures, run at 21:00:45 against the verbatim discovery block
(lines 221-237):

- E1, regular file `wayland-9` plus real socket `wayland-1`: rc 0, picked
  `wayland-1`, elapsed 0.0s. PASS. A non-socket `wayland-*` entry is ignored.
- E2, lock file only (`wayland-1.lock`, no socket): rc 1, missing fail,
  elapsed 10.0s. PASS. A lock with no socket is not mistaken for a socket.
- E3, socket appears at t=3 (background bind): rc 0, found `wayland-1`,
  elapsed 3.0s. PASS. The retry path works; the socket may lag the signature.

## 6. Laptop C2: parser and teardown really used v3-extracted code

- Source md5s on the laptop (read-only, 21:01:51):
  `/tmp/y6-nested/run-nested-wayland.sh` is `c7c1d6f2...` (v3),
  `/tmp/y6-nested/run-nested-pill.py` is `eea0c320...` (v3),
  `/tmp/y6-nested/conf/hyprland-wayland-v2.lua` is `0d4ac7a9...` (v3).
  All three match the repo v3 hashes exactly.
- The laptop test script `/tmp/y6d-c2-laptop.sh` has md5
  `87153c52cccb9d7efe50be72877eec7f`, identical on the laptop and on the VM
  copy I audited. The script I reviewed is the script that ran.
- The laptop-side extracts are byte-identical to my VM extractions from the
  repo v3 file: `/tmp/y6d-c2/read_pill_geom.sh` is 15 lines and
  byte-identical (diff clean, 21:02:47); `/tmp/y6d-teardown/teardown.sh` is
  36 lines and byte-identical (diff clean, 21:02:57). Both match the laptop
  log's `wc -l` output (15 and 36). The parser test and the teardown harness
  therefore really ran v3-extracted functions, not stale v2 copies.
- Parser test (laptop log): live layers give rc 1 with empty stdout and
  empty stderr (no pill live, no traceback); synthetic nested JSON gives
  rc 0 with `320,0 320x66`. The synthetic JSON uses the real nest layers
  shape (monitor, levels, namespace `computer-use-indicator`). The stub
  `nest()` feeds the JSON file to the extracted function, which is the
  parser logic under test. PASS.
- Teardown harness (laptop log): ASSERT1 is 2 (both fake log lines copied),
  ASSERT2 is RUN-DIR-REMOVED, ASSERT3 is LOCK-FREE, ASSERT4 is
  LIVE-1515-ALIVE, live `hyprctl` reports 0.57.2, live plugins are hyprbars
  only. All match the log lines. Note the harness sets `NESTED_PID`,
  `PILL_PID`, and `MPV_PID` empty, so the process-group kill and the PID
  kill paths are not exercised here; the teardown function itself is
  unchanged in v3, so this is a regression check, and the untested paths
  are pre-existing, not v3.
- The laptop log window is 20:56:31 to 20:56:32 (1 second). That is fast but
  consistent with the work: 4 of 5 grim calls fail fast with no file write,
  the parser is local JSON, and the teardown executes no sleeps with empty
  PIDs. On-disk artifacts corroborate execution (PNG 37,475 bytes, extracts,
  layers JSON, 0-byte parser stderr, all stamped 20:56). Not a finding.
- The laptop repo checkout at `~/workspace/computer-use-wayland`
  is at 4500a18 and its `improvements/` dir does not contain the Y6 files
  (older tree). That is pre-existing state, already noted in the Y6c log.
  The C2 source on the laptop is the `/tmp/y6-nested` runtime copy, which is
  md5-verified v3 above. No discrepancy in Y6d's sync claim once the target
  is read as the runtime copy.

## Debate and dissent (recorded)

- D1, static-only launch line. One voice argued AMEND: require a live nest
  launch before GO. Rebuttal adopted: a live launch needs the rebuilt plugin,
  which is BLOCKED and out of scope; the change is a deletion of a flag
  proven fatal live (Y6c F0), and Y6c probe 1 proves the identical
  no-`--socket` launch works with the same env and conf. Deletion plus live
  probe is sufficient evidence for the launcher change. GO stands, with
  residual R2 recorded.
- D2, harness fidelity. One voice argued the 16/16 could hide a scope
  difference (no `set -u`, no `exit 0`, redefined `fail`). Rebuttal adopted:
  the block references only the 7 harness-set variables, calls no `fail`,
  and every branch ends in `echo`; my independent harness reproduces 16/16
  with identical verdict strings. Faithful.
- D3, 1-second laptop window. One voice argued the timestamps are too fast
  for 5 grim calls. Rebuttal adopted: 4 of 5 grim calls fail fast, parser is
  local, teardown has no sleeps on empty PIDs, and on-disk artifacts
  corroborate execution. Not a finding.
- D4, discovery fixture realism. One voice argued a python socket is not a
  Hyprland socket (creation order, permissions, timing). Rebuttal adopted
  with closure: the stand-in is faithful for the tested logic, and the
  order/timing gaps were closed by Council 2 fixtures E2 (lock-only, 10.0s)
  and E3 (delayed socket at t=3). Permissions are immaterial for `[ -S ]`.
  No hole.
- D5, pill error message. One voice wanted AMEND for a friendly message
  instead of a bare KeyError traceback. Majority: the behavior is fail-loud
  as specified, and the launcher reports the death clearly. Recorded below
  as a non-blocking suggestion, not a required fix.

## Non-blocking notes (do not hold the verdict)

- N1, editorial: correct the grim label in the Y6d log and the laptop log
  ("100,100 200x200" is outside every live output, not inside). The proof is
  intact; only the label is wrong.
- N2, polish (optional): the pill could catch a missing `WAYLAND_DISPLAY`
  and print one clear line before exiting, instead of a bare KeyError
  traceback. Behavior is already fail-loud; this is readability only.
- N3, for the retry runner: the first live v3 run is the execution proof for
  residuals R1 to R4. If the launch line or any env substitution misbehaves
  live, that is a new finding for the retry review, not a defect in this one.

## Evidence list

- `improvements/y6d-evidence/v3-diff.txt`, 188 lines, byte-identical to
  `git diff` of the three v3 files against HEAD.
- `improvements/y6d-evidence/c2-vm.log`, all PASS, reproduced by Council 2
  at 20:59:11 with identical output except temp dir suffixes.
- `improvements/y6d-evidence/c2-laptop.log`, 20:56:31-32, all asserts as
  quoted in section 6.
- `/tmp/y6d-c2-vm.py` (165 lines) and `/tmp/y6d-c2-laptop.sh` (84 lines),
  read and audited; laptop copy md5 `87153c52cccb9d7efe50be72877eec7f`.
- Council 2 extra fixtures: E1 regular file plus socket, E2 lock-only
  (10.0s), E3 delayed socket (3.0s), stale-cleanup dirty and empty dirs.
  All PASS. Fixture scripts were run from stdin and left no files behind
  except temp dirs under `/tmp`.
- Laptop read-only verification via the SSH helper: runtime md5s match repo
  v3; extracts byte-identical; GRIM-A2 PNG 37,475 bytes present, GRIM-A PNG
  absent; Y6c stdout logs 0 backend matches, per-instance logs 1 each.
- v3 hashes: runner `c7c1d6f2c3aed3f912def4bd4d2c7fcc`, pill
  `eea0c320746bae4fc92c1f511cc803cb`, conf
  `0d4ac7a9c2437fb48ecfc505ccd9046b`.

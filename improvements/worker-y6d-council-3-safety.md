# Council 3 (safety) verdict: Worker Y6d v3 launcher fixes

- Verdict: **GO** (launcher fixes only)
- Date: 2026-11-21, review run 20:58-21:04 +07 (Asia/Ho_Chi_Minh)
- Reviewer: Council 3 (safety), subagent session 79f71354
- Scope: LAUNCHER FIXES ONLY. The hyprglass rebuild is BLOCKED by an
  execution-risk check on a fetched commit and is NOT covered by this
  verdict. No Zen driving, no nested Hyprland launch, no live session
  contact, no hyprglass checkout/build/load, no git command in the vendor
  repo during this review.
- Files reviewed: `improvements/worker-y6b-run-nested-wayland-v2.sh` (v3),
  `improvements/worker-y6b-run-nested-pill-v2.py` (v3),
  `improvements/worker-y6b-hyprland-wayland-v2.lua` (v3),
  diff `improvements/y6d-evidence/v3-diff.txt` (188 lines),
  C2 evidence `improvements/y6d-evidence/c2-vm.log` and `c2-laptop.log`,
  test scripts `/tmp/y6d-c2-vm.py` and `/tmp/y6d-c2-laptop.sh`,
  worker log `improvements/worker-y6d-rebuild-log.md`,
  background `improvements/worker-y6c-nested-run-log.md`.
- Rules complied with: no ydotool used or present in any v3 file (grep
  verified), no em/en dash in this paper or in any v3 file (Python check),
  no personal info in any v3 file (grep verified) or in this paper.

## Time log (every check, +07)

- 20:58-21:00: read v3 diff (188 lines), Y6d log, Y6c log, all three v3
  files in full.
- 21:00: md5 check. Repo v3: runner c7c1d6f2, pill eea0c320, conf
  0d4ac7a9. Origin v2: runner 8cd00a16, pill 3488c181, conf 0e0dd3f6.
  All match the values in the task brief.
- 21:00: teardown diff v2 vs v3: IDENTICAL (awk-extracted function).
- 21:00: laptop read-only check via ssh-laptop.sh: live Hyprland PID 1515
  alive, single live signature
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825, no mpv,
  no foot. Deployed copies in /tmp/y6-nested match repo v3 exactly
  (runner c7c1d6f2, pill eea0c320, conf 0d4ac7a9).
- 21:01: re-ran /tmp/y6d-c2-vm.py on the VM: all VM C2 checks PASS
  (verdict 16/16, discovery 3 cases, backend gate 3 cases, nest() guard
  2 cases, 6 static checks). Marker line numbers in c2-vm.log confirmed
  against the v3 file: verdict 504-526, discovery 221-237, gate 217-219,
  nest() line 89.
- 21:01: static greps: rm -rf 3 sites (all inside $RUN_DIR), pkill only
  in 2 comments, live() calls only in teardown (2 read-only hyprctl
  calls), one $(nest ...) site (line 240), all 4 background launches
  carry 9>&-, no em/en dash, no personal info.
- 21:01-21:02: independent C3 harness /tmp/y6d-c3-harness.sh (VM only,
  56s): 13 of 14 checks PASS on first run; the one FAIL (B3) was a
  harness artifact, re-tested and PASS (see finding 1).
- 21:02: B3 re-test: cleanup with no matches prints CONTINUED and keeps
  an unrelated file intact; no set -e in the runner, so the loop exit
  status is harmless.
- 21:03: call-site counts v2 vs v3: hyprctl 8/8, grim 10/10, mpv 27/27,
  live hyprctl 2/2, pkill 2/2, 9>&- 8/8, rm -rf 2/3 (the +1 is the split
  of the old single cleanup line into two RUN_DIR-confined lines).
  Conf plugin.load line byte-identical between v2 and v3. Pill diff is
  exactly the one WAYLAND_DISPLAY line.

## Finding 1: stale-socket cleanup glob loop (PASS, with one noted wart)

Code (runner lines 179-180):

```
rm -rf "$RUN_DIR/hypr"
for stale in "$RUN_DIR"/wayland-*; do [ -e "$stale" ] && rm -rf "$stale"; done
```

- RUN_DIR unset or empty: NOT reachable. RUN_DIR is a literal assignment
  (`RUN_DIR=$NEST/run`, `NEST=/tmp/y6-nested`, lines 31-32), not read from
  the environment, and `set -u` is on (line 30). Tested: an unset RUN_DIR
  under `set -u` aborts with "unbound variable" BEFORE any rm runs (C3
  harness B4, PASS). Empty RUN_DIR would need the literal assignment to
  be edited, which is out of scope for a runtime review.
- Glob matches nothing: safe. The unmatched glob stays literal, `[ -e ]`
  is false, no rm runs, the script continues (re-test PASS: CONTINUED
  printed, unrelated file intact). There is no `set -e`, and nothing
  chains off the loop status, so the loop returning status 1 on no match
  is harmless. The first C3 harness B3 FAIL was my harness measuring the
  loop exit status instead of the outcome; the re-test measures the
  outcome and passes.
- Non-socket file named wayland-*: removed, correctly. Fixture test (B1)
  with a real socket, a .lock file, a regular file, a directory, and a
  hypr dir: all removed, unrelated keep.txt untouched (PASS).
- Wart (not safety-relevant): a DANGLING symlink named wayland-* SURVIVES
  the cleanup, because `[ -e ]` is false for a dangling link (B1, proven).
  The discovery loop then skips it (`[ -S ]` false) and fails closed
  with "no nested Wayland socket" after 10s (B2, proven). It cannot cause
  a wrong socket pick, a wrong display, or any live touch. Nothing in the
  workflow creates symlinks in the run dir, so this needs a hand-planted
  link to even occur.
- Ordering: the cleanup runs AFTER the flock is held (flock lines
  174-176, cleanup line 179), so no concurrent runner can be racing it.
  Blast radius is confined to /tmp/y6-nested/run.

Debate and dissent: the strictest reading says fix the guard now
(`[ -e "$stale" ] || [ -L "$stale" ]`), one line, zero risk. The
majority holds that a wart proven inert by two tests, requiring a
hand-planted symlink to occur, is a follow-up note and not a gate for
the retry. Recorded as a recommended hardening fix, not a condition of
this GO.

## Finding 2: nest() guard calls fail() inside a function (PASS, bounded)

Code (runner line 89):

```
nest() { [ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"; env ... "$@" 9>&-; }
```

- The masking hazard is REAL and was reproduced: with NEST_DISPLAY empty,
  the line-240 pattern `NEST_OUTPUT=$(nest hyprctl ... | python3 ... ||
  echo "WAYLAND-1")` lets the outer script survive with NEST_OUTPUT
  WAYLAND-1, because fail() exits only the command-substitution subshell
  (C3 harness A1, PASS: outer printed "outer-survived
  NEST_OUTPUT=WAYLAND-1").
- It is UNREACHABLE in the current script order: the discovery block
  (lines 221-237) precedes the only $(nest ...) call (line 240), and
  discovery fails the whole script if NEST_DISPLAY is empty (C2: no
  socket fails after 10s; ambiguous fails at once). NEST_DISPLAY is
  assigned only at init (line 57) and inside discovery (lines 226, 231),
  verified by grep (A2, PASS).
- It is BOUNDED even if reached: the very next statement after line 240
  calls nest() at top level (`nest hyprctl -j plugin list ... || fail`),
  where fail() exits the script. A wrong NEST_OUTPUT value therefore
  propagates at most one statement before a fail-closed abort, and can
  never reach a measurement arm.
- All other nest() call sites are top level with `|| fail` or `|| return
  1` plus a top-level `|| fail` (read_pill_geom, capture, liquid gate,
  plugin list, grim calls), so fail() there exits the script as designed.
  Line 240 is the only $(nest ...) site in the file (grep verified).

Debate and dissent: the strictest reading says fail() inside a function
used in $(...) is a latent trap and the WAYLAND-1 fallback should be
removed or a pre-check added before line 240. The majority holds that an
unreachable-in-order path with a one-statement fail-closed bound cannot
produce a wrong measurement or a live touch, and that removing the
fallback would change pre-existing v2 behavior (it also covers a plain
hyprctl failure) beyond the v3 scope. Recorded as a hardening note, not
a condition of this GO.

## Finding 3: teardown (PASS, byte-identical, harness re-verified)

- Diff of the awk-extracted teardown function v2 vs v3: IDENTICAL.
- The C2 laptop log shows the teardown dry harness passing against the
  v3-extracted function (source: /tmp/y6-nested/run-nested-wayland.sh,
  md5 c7c1d6f2, confirmed v3): ASSERT1 log copy has both lines,
  ASSERT2 run dir removed, ASSERT3 lock free, ASSERT4 live PID 1515
  alive, live hyprctl 0.57.2, plugins hyprbars only.
- Independent C3 re-run on the VM with the v3-extracted teardown and
  fake live values: C1 log copy 2 lines, C2 run dir removed, C3 lock
  free (all PASS). ASSERT4 (live alive) is not testable from the VM and
  rests on the C2 laptop log, which is the correct source for it.

## Finding 4: flock and fd handling (PASS, no leak)

- All 4 background launches carry `9>&-`: nest setsid launch (line 193),
  backdrop mpv (line 300), pill (line 323), arm mpv (line 395). The tee
  process is created before the flock fd exists, so it cannot inherit
  the lock. Count of `9>&-` is 8 in both v2 and v3 (unchanged).
- New v3 code spawns no long-lived child. The discovery loop spawns only
  transient children (`basename`, `sleep`), which exit at once and close
  their inherited fd copies; a transient inheritance cannot hold the
  flock past script exit. The cleanup loop spawns only transient `rm`.
- The nest() guard adds no child before the `env ... 9>&-` call.

## Finding 5: pill WAYLAND_DISPLAY KeyError (PASS, loud failure)

- Pill change is exactly one line (diff verified): hardcoded
  `"wayland-y6"` replaced by `os.environ["WAYLAND_DISPLAY"]`.
- Missing variable raises KeyError with traceback, rc=1 (D1, PASS).
  The launcher passes WAYLAND_DISPLAY="$NEST_DISPLAY" explicitly in the
  pill launch env (line 323), so in any real run the variable is set; the
  KeyError fires only if the pill is run standalone without it.
- Failure path is clean and two-deep: the pill dies within milliseconds
  of start (KeyError is at module top level, before show), so the
  launcher `sleep 1; kill -0` check fails first with "pill process died
  immediately (see nest-pill.log)". If the pill survived 1s, the 45s
  ready wait fails with "pill did not become ready in 45s (see
  nest-pill.log)" (D2, PASS, verbatim 45s wait against a log holding
  only the KeyError traceback). Either way fail() runs, the EXIT trap
  tears down the nest, and the traceback sits in nest-pill.log.
- No live touch on this path: the pill binds its listen socket in
  /tmp/y6-nested/cache (nest-local STATE_DIR, separate from the live
  session), its XDG_RUNTIME_DIR is the nest run dir, and the process
  death closes the socket. The launcher never touches the live session
  on this path.

## Finding 6: no new live calls, no new pkill, no new rm -rf outside the nest dir (PASS)

- Call-site counts v2 vs v3 are equal: hyprctl 8/8, grim 10/10, mpv
  27/27, live hyprctl 2/2, pkill 2/2, 9>&- 8/8. The only count change is
  rm -rf 2 to 3, which is the split of the old single cleanup line into
  two RUN_DIR-confined lines (finding 1).
- pkill appears only in 2 comments ("never by pkill -x"). No pkill in
  code (C2 static check PASS).
- All 3 rm -rf sites are inside $RUN_DIR=/tmp/y6-nested/run: teardown
  (gated on NEST_STARTED=1), cleanup of $RUN_DIR/hypr, cleanup loop over
  $RUN_DIR/wayland-*. No rm -rf outside the nest runtime dir.
- The only live() calls are in teardown (lines 114-115): read-only
  `hyprctl version` and `hyprctl -j plugin list`. No new live hyprctl,
  grim, or mpv call anywhere in v3.
- Conf diff is comments only; the `hl.plugin.load(...)` line is
  byte-identical between v2 and v3. Pill diff is exactly the one env
  line. No new exec/autostart in the conf.

## Finding 7: conf still loads backup 1, retry failure order (PASS, fails fast)

Traced failure order for a retry run launched with the current conf
(backup 1 hyprglass, dead .so.14/.so.4 ABI per Y6c F1):

1. Preconditions, live identity resolve (reads only), runner-quiet
   check (reads only), flock held.
2. Cleanup, nest launch (no --socket, starts), signature found,
   per-instance log backend gate PASSES on a healthy nest (U5b fix).
3. Discovery finds exactly one socket (wayland-1), NEST_DISPLAY set.
4. `nest hyprctl -j plugin list` returns `[]` (Y6c probe 2, proven:
   the config-time load fails silently, no hyprglass in the list).
5. `grep -q hyprglass nest-plugin-list.json || fail "hyprglass not in
   nested plugin list"` fires at line 244 (FAIL, exit 1, EXIT trap
   teardown).
6. The 60s liquid gate is at line 274, AFTER the plugin-list check, so
   it is never reached and no 60s is burned. The version parse and hook
   marker check also sit after line 244 and never run.
7. Teardown kills only the nest process group, removes only the nest
   run dir, and re-verifies the live session with read-only hyprctl
   calls. No live write occurs at any step of this path. The nest window
   appearing on the live screen is the pre-existing design (owner away).

## Laptop copy verification

- Deployed copies in /tmp/y6-nested match the repo v3 md5s exactly:
  runner c7c1d6f2, pill eea0c320, conf 0d4ac7a9 (read-only md5sum via
  ssh-laptop.sh, 21:00 +07).
- Note, not a hole: the laptop REPO tree
  (~/workspace/computer-use-wayland) does NOT contain the
  worker-y6b* files at all (repo at 4500a18, predates them; Y6c log
  confirms the laptop repo was intentionally not pulled). Y6d's "laptop
  copies synced" refers to the deployed /tmp/y6-nested copies, which do
  match. A retry runner uses /tmp/y6-nested (as Y6c did), so the
  executable copies are the verified ones. No stale v2 copy exists on
  the laptop to confuse a retry.
- Live session state at check time (read-only pgrep/ls/md5sum only):
  Hyprland PID 1515 alive, single live signature, no mpv, no foot,
  lock free. Nothing in this review touched the live session.

## Non-gating hardening notes (for a later cleanup, not conditions of GO)

1. Cleanup guard: `[ -e "$stale" ] || [ -L "$stale" ]` so a dangling
   wayland-* symlink is also removed (runner line 180). Proven inert
   today, but the fix is one line and removes the wart.
2. Line 240: add a top-level `[ -n "$NEST_DISPLAY" ] || fail ...`
   before the NEST_OUTPUT substitution, so the guard can never be
   masked by the WAYLAND-1 fallback even if a future edit reorders
   discovery. Proven unreachable and bounded today.

## What this GO does NOT cover

- The hyprglass rebuild (BLOCKED, pending the user's explicit go-ahead
  on the fetched commit). No rebuilt plugin exists, so no retry run can
  pass the plugin-list check (finding 7).
- Any retry run itself: it needs the rebuilt plugin path wired into the
  conf, plus a fresh re-review and a fresh Muse go, per the adjudication.
- The Y6d C2 laptop log was read and cross-checked (bash -n,
  py_compile, parser, grim forms, teardown harness), not re-run from the
  VM; its live-side claims (ASSERT4, live hyprctl 0.57.2, hyprbars only)
  rest on Y6d's laptop run at 20:56:31-32 +07, which the log supports.

## Verdict restated

GO for the v3 launcher fixes. No fix in the v3 diff can touch or harm
the live session: the cleanup is confined to the nest runtime dir and
fails closed, the nest() guard is unreachable-in-order and bounded, the
teardown is byte-identical and re-verified, the flock fd discipline is
unchanged with no new long-lived child, the pill KeyError fails loudly
and cleanly, no new live call/pkill/rm -rf exists, and a retry with the
current backup-1 conf fails fast at the plugin-list check (line 244)
before the 60s liquid gate, with no live side effect.

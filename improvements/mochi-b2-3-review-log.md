# B2-3 review log: A8 fix rewritten as a real patch (compiled artifact)

- Item: B2-3, batch 2, assigned in coord/mochi.md commit f9a1a9f, 18:32 22/11/2026.
- Fix commit: ef964a6596af77009dae5f830375658183708265, on todolist-push, base e6b9777.
- Fix: 4 files, 1561 insertions, 51 deletions.
  - improvements/worker-y6b-run-nested-wayland-v2.sh, md5 e478846e8adddce80df6fc8a5ddf32b5.
  - improvements/y6-nested-conf/nested-visuals-hook.lua, md5 9e8e66b1f3cafa7301936aaa80a97030.
  - tests/test_y6c5_positive_gate.py, md5 200f01e70f566f28aa9e972e12a25091.
  - improvements/worker-y6c5-a8-load-only-trial.md, md5 1965dd897838d3525f7a6a9c13c9df44.
- Key discovery by the worker: commit 44b9a80 had already applied the invest section 4 fix (4a to 4e) with a re-review GO and 16/16 tests PASS, so B2-3 was fixing the remaining flaws on top of HEAD 9ae216b, not applying the fix for the first time.
- Worker: completed 18:40:40 22/11/2026, worktree /tmp/mochi-b2-3. First version: 4 files, 168 insertions, 40 deletions, tests 16 to 22, all PASS. The fix then went through 8 redteam-driven rounds in the same worktree, each followed by council 1, 2, 3 re-review PASS before the next redteam round.

## Fix rounds (redteam finding -> fix -> re-review PASS)

- Round 1, redteam 18:43:18: R-R1 Lua guard pure prefix test bypassed by ".." and pre-planted symlink at RUN_DIR; R-R2 A2 poll only greps the OPTICS line, HOOK line only printed, violating batch 1 procedure step 3.3 (both lines required); R-R3 no second G4 configerrors check after the marker, violating step 3.6. Fix 18:47:13: reject any ".." component in the hook, runner [ -L "$RUN_DIR" ] fail-closed before rm -rf and mkdir -p, teardown warn instead of rm -rf when RUN_DIR is a symlink, atomic marker write via temp file plus os.rename, poll requires both marker greps, second G4 block after the status re-fetch. Tests 27 checks PASS; strengthened tests FAIL 6/27 on pre-fix code.
- Round 2, redteam 18:51:13: R2-1 symlink on parent dir /tmp/y6-nested bypasses both guards; R2-2 fixed-name marker tmp file never cleaned at startup, pre-planted symlink truncated by hook io.open "w" before rename; R2-3 (minor) one-line marker containing both strings PASSes because poll only greps substrings. Fix 18:54:39: [ -L "$NEST" ] fail-closed before the RUN_DIR check and before any rm -rf or mkdir -p, teardown rm -rf guard checks both, runner rm -f of the marker tmp at startup, hook os.remove(marker_tmp) before io.open, poll greps anchored at line start. Tests 28 checks PASS; FAIL 5/28 on pre-fix code. Council 1 noted non-blocking residual R-NEW: two writes under $NEST before the symlink guard (line 86 tee, line 278 live plugin list write).
- Round 3, redteam 18:58:11: R3-1, same as R-NEW but blocking: guard at about line 313, but three writes under $NEST run before it (tee line 86, before-list line 278, teardown after-list line 159 via fail() triggering trap teardown EXIT). Fix 19:04:59: fail() moved above the tee, both symlink checks now at lines 101-102 before the tee at line 107, late guard block removed, guard-fail exits without teardown (no trap installed yet), teardown after-list write requires BEFORE_LIST_WRITTEN flag AND a re-check of [ -L "$NEST" ] at teardown. Tests 29 checks PASS; new tests FAIL 2/29 on pre-fix code.
- Round 4, redteam 19:09:14: R4-1 fixed-name file /tmp/y6-live-version.txt truncated via pre-planted symlink by the > redirect at runner line 173; R4-2 fixed-name lock file $LOCK truncated on open by exec 9>"$LOCK" at line 330. Both pre-existing in base 9ae216b, same class as R2-2. Fix 19:12:06: LIVE_VERSION_FILE variable defined once (line 69) with rm -f in teardown before the redirect; [ -L "$LOCK" ] fail-closed check before exec 9>. Tests 31 checks PASS; new tests FAIL 2/31 on pre-fix code.
- Round 5, redteam 19:15:06: R5-1 symlink at the PARENT dir of $LOCK bypasses the leaf check, exec 9> truncates the victim zen_dom.lock and mutual exclusion breaks; teardown flock line also touches $LOCK with no check. Fix 19:21:37: [ -L "$(dirname "$LOCK")" ] check before exec 9>, teardown flock replaced by an if/elif/else block that warns "skipping lock-free check" and does not run flock when the lock path or its parent dir is a symlink. Tests 33 checks PASS.
- Round 6, redteam 19:26:42: R6-1 symlink at $HOME/.cache (grandparent of $LOCK) bypasses leaf and parent checks; R6-2 nine fixed-name files directly under $NEST have no rm -f and no symlink check and are truncated via pre-planted links. Fix 19:32:06: ancestor loop checking EVERY component of $LOCK from $HOME/.cache down to the parent (stopping at $HOME, not checking $HOME itself) before exec 9>, same loop in the teardown flock block via flag _lock_ancestor_bad; startup cleanup block right after the $NEST/$RUN_DIR guard and before the tee, rm -f on 20 fixed-name paths under $NEST; trial doc section 1 rewritten to state the correct scope. Tests 35 checks PASS; new tests FAIL 3/35 on pre-fix code.
- Round 7, redteam 19:37:45: R7-1 timestamped names CAN be planted by window planting (one symlink per second across a window); RUN_LOG is never rm -f'd or checked, so the tee appends the whole run log into the victim file; R7-2 teardown cp marker dest truncates the victim via a pre-planted symlink; R7-3 the FRAMES dir (timestamped) can be redirected by a planted symlink and grim then truncates files inside the victim dir. Fix 19:41:23: rm -f "$RUN_LOG" right after the cleanup block before the tee, rm -f marker dest before the teardown cp, rm -rf hypr-saved dest before cp -r, guard [ -L "$FRAMES" ] fail closed right before mkdir -p, trial doc corrected (timestamped names are NOT safe by timestamp). Tests 38 checks PASS; new tests FAIL 3/38 on pre-fix code.
- Round 8, redteam 19:45:14: R8-1 a symlink at $NEST/cache redirects the pill control socket into the victim dir. Chain: runner line 454 mkdir -p "$RUN_DIR" "$FRAMES" "$NEST/cache" has no symlink check for $NEST/cache; the pill sets STATE_DIR = /tmp/y6-nested/cache/agent-computer-use, token = secrets.token_hex(16) fresh per run, indicator.listen(STATE_DIR, token); scripts/indicator.py lines 125-129 bind endpoint state / ('indicator-' + token + '.sock') and chmod 0o600; indicator.serve accepts hide/show/move/label if the request token matches. Proven live end to end: victim dir gained the socket, token recovered from the socket filename, a hide command answered "hidden", so pill control is fully hijacked. The A8 load-only trial does not start the pill (stops at Y6_STOP_AFTER_GATES=1), so R8-1 affects full runs with pill and arms, not the A8 trial, but the runner is the same file so the fix belongs here. Fix 19:50:49: both guards added in the runner right after the FRAMES guard, before mkdir -p: if [ -L "$NEST/cache" ] then fail, and if [ -L "$NEST/cache/agent-computer-use" ] then fail, refuse outright. Real demo with indicator.listen/serve: old lines at both levels HIJACKED, new lines at both levels REFUSED rc 1, victim untouched. 2 new exec tests, total 40 checks PASS (real 11.734s, rc 0, at 19:49:16). New tests FAIL 2/40 on pre-fix code.

## Re-review round 8: council 1, 2, 3 PASS, on 40/40

- Council 2 PASS 19:53:38, council 3 PASS 19:53:56, council 1 PASS 19:54:05. Each with own mutants failing exactly the new checks and own live demos reproducing the hijack on old lines and the refusal on new lines at both cache levels. Council 3 noted one of its reads of the local coord/mochi.md was flagged by a runtime check, so it did not use that read as a source and verified the batch 1 procedure steps 3.3, 3.4, 3.6 directly in the runner code.

## Redteam round 9: KHONG PHA DUOC, completed 19:55 (handoff 19:56:13) 22/11/2026

- Re-ran the suite (40/40 PASS, real 11.876s, rc 0), confirmed patch md5s, reproduced the R8-1 hijack on old lines and the refusal on new lines at both cache levels with the real indicator.listen/serve, listed every write destination in the runner independently and found none left unprotected, proved the new tests non-empty by its own mutant (removing the 2 cache guard lines fails exactly the 2 new checks), and verified each patch applies cleanly on ITS OWN baseline with 40/40 PASS after apply and all 4 file md5s matching the worktree: the incremental patch (vs 9ae216b, md5 30d988952657d3adcd2323909918680e) on baseline 9ae216b, and the full patch (vs cf11a4b, md5 855c19c94ed91887c25452d6a16c6f36) on baseline cf11a4b. (Correction 23/11/2026: the original wording here, "both patches apply cleanly on both baselines", is imprecise; see the Correction section below. Cross-baseline application was never tested, and the ef964a6 commit diff does NOT apply on cf11a4b.)
- Non-blocking residual: mpv may write shader/icc cache files under XDG_CACHE_HOME (~/.cache/mpv) with hash names, which is litter only (no truncation of existing victim files, no token or control leak), unproven on the VM because mpv is not installed; suggested fix is adding --no-gpu-shader-cache --no-icc-cache to the 2 mpv calls or setting XDG_CACHE_HOME under the guarded RUN_DIR, needs a live probe with real mpv on the laptop.

## Independent verifier: PASS, completed 19:59:37 22/11/2026

- Read both required docs in full, confirmed the batch 1 procedure steps 3.3, 3.4, 3.6 are implemented correctly in the fix, re-ran python3 tests/test_y6c5_positive_gate.py (40/40 PASS, real 11.679s, rc 0), bash -n OK, verified each patch applies on ITS OWN baseline with 40/40 PASS after apply and matching md5s (incremental patch on 9ae216b, full patch on cf11a4b; same correction note as the redteam round 9 section), listed every write destination independently (no >>, no mv, only 2 cp both rm-dest-first, only 1 mkdir -p fully guarded), proved tests non-empty with 3 own mutants (M1 remove cache guard fails exactly 1 check, M2 remove rm -f RUN_LOG fails exactly 1 check, M3 remove the second G4 block fails exactly 3 checks), and reproduced the R8-1 hijack and refusal with its own demo.
- Note: its report's internal timestamps read 12:56-12:59 (a typo for 19:56-19:59); the handoff time 19:59:37 is the reliable one.

## Patches

- Incremental vs 9ae216b: 1849 lines, md5 30d988952657d3adcd2323909918680e, in ~/workspace/mochi-b2-3-patches/mochi-b2-3-incremental-vs-9ae216b.patch.
- Full vs cf11a4b: 2069 lines, md5 855c19c94ed91887c25452d6a16c6f36, in ~/workspace/mochi-b2-3-patches/mochi-b2-3-full-vs-cf11a4b.patch.
- Cumulative patch committed as a file: improvements/mochi-b2-3-cumulative-vs-cf11a4b.patch, commit c597a29 on todolist-push. It is the same bytes as the full vs cf11a4b patch (md5 855c19c94ed91887c25452d6a16c6f36). Independent review found ef964a6's own diff does not apply on cf11a4b (fails all 4 files) because it is diffed against e6b9777; the cumulative patch applies cleanly on cf11a4b (git apply --check PASS, 40/40 PASS after apply, 4 file md5s match ef964a6).

## Correction 23/11/2026 (by mochi, on independent review by the owner)

The claim in the redteam round 9 and independent verifier sections, "verified both patches apply cleanly on both baselines", is imprecise and is corrected here. What was actually verified, each patch on its own baseline only:

- Incremental patch (vs 9ae216b, 1849 lines, md5 30d988952657d3adcd2323909918680e) applies on baseline 9ae216b. Re-verified by mochi 23/11/2026: `git apply --check` PASS, applied diff 1561 insertions, 51 deletions, 4 file md5s match ef964a6, test 40/40 PASS in 11.6s.
- Full patch, same bytes as the committed cumulative patch (vs cf11a4b, 2069 lines, md5 855c19c94ed91887c25452d6a16c6f36) applies on baseline cf11a4b. Verified 00:00 23/11/2026: `git apply --check` PASS, applied diff 1691 insertions, 89 deletions, 4 file md5s match ef964a6, test 40/40 PASS in 12.0s.

What was NOT verified, and is admitted here: the ef964a6 commit diff itself (diffed against e6b9777, which holds intermediate changes to these 4 files that cf11a4b lacks, e.g. the 44b9a80 A8 fix) does NOT apply on cf11a4b. Verified by mochi 00:00 23/11/2026: `git show ef964a6 | git apply --check` on a cf11a4b worktree returns rc 1, failing all 4 files (runner line 43, trial doc line 32, hook line 38, test line 64). So anyone taking ef964a6's own diff to cf11a4b would fail. The cumulative patch commit c597a29 closes this gap: it is the correct patch for a cf11a4b base. Cross-baseline application (incremental patch on cf11a4b, full patch on 9ae216b) was never tested and is not claimed.

## Re-measurement on committed bytes (by mochi, 23:08 22/11/2026)

- Applied the incremental patch onto todolist-push HEAD e6b9777, md5s matched, test 40/40 PASS (11.9s), bash -n OK. Committed ef964a6, pushed, verified by `git ls-remote origin todolist-push`. Re-run on committed bytes: 40/40 PASS (12.3s).
- Coord report: commit e80a54b on main, push verified. Cumulative patch report: commit 166a6ed on main, push verified.

## Accepted residuals (not blocking)

- TOCTOU (guards check at startup only, a link planted mid-run is not caught; teardown cp still follows a mid-run planted link).
- The $LOCK ancestor loop stops at $HOME and does not check $HOME itself.
- The mpv XDG_CACHE_HOME litter noted by redteam round 9.

## Standing limit

- No lua or luac exists on the VM, so the hook Lua has never been compiled or run, only read carefully, pattern-simulated in python, and string-asserted in tests. A re-review must run luac or the real hook on a nest before any live run. No live run, no A8 rerun without a written GO.

## Note on this artifact

- This log compiles the review handoffs received on 2026-11-22 (worker, 8 fix rounds, council 1, council 2, council 3 re-reviews, redteam rounds 1-9, independent verifier). The original review subagent sessions did not commit their own artifacts; that gap is what the new rule fixes (see coord/mochi.md, rule from 23:57 22/11/2026: every council/redteam/verifier review must commit an artifact with a hash). This committed log is the verifiable artifact for B2-3; its commit hash is the proof.

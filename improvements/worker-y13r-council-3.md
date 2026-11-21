# Council 3 re-review (Worker Y13r): Y13 fixed diff cb26d1d, changed lines only

- Reviewer: Council 3 of Worker Y13r, independent re-review.
- Commit under review: cb26d1d "Y13: adjudicate Council A + redteam re-review (BLOCK -> fixed); launcher + manifest regen".
- Parent (last reviewed state): bd89b62.
- Scope: redteam H5, M1, M2, M3, M4, M7, L1, L2, plus the manifest-md5 pin decline. Changed lines only, from `git show cb26d1d`. No code or test file was modified by this review. No live driving was done.
- Sources read in full: the cb26d1d diff for tests/realistic/launch_y13.py and tests/realistic/run_codex_y5.py, plan v2 (improvements/worker-y13-codex-y5-live-plan.md, C3 S2 and C3 S3), redteam re-review (improvements/worker-y13-rereview-redteam.md, H5, M1, M2, M3, M4, M7, L1, L2), Y13 adjudication log (improvements/worker-y13-codex-y5-live-log.md, sections "Re-review Council A (harness) + Redteam" and "Final mechanical gates").
- Method: every finding below was checked by reading the exact lines AND by a mechanical test on the VM, except where stated. Staged ships were built from committed bytes with `git show` (run_live.py from the pinned 1e3901c bytes, everything else from cb26d1d).

## Timing log (wall-clock Asia/Ho_Chi_Minh, elapsed from review start 20:20:02)

- 20:20:02 +07, 0s: review start, git log and diff stat read.
- 20:21:29 +07, 87s: M1 staged-ship run started (clean + 3 plants + nested pycache + hidden file + symlinked dir + top pycache).
- 20:21:54 +07, 112s: M2 wall-cap simulation and L1 step-unwrap test on the imported module.
- 20:22:04 +07, 122s: H5 marker regex comparison against plan v2 C3 S2, plus git log grep on todolist-push.
- 20:22:47 +07, 165s: H5 marker check against a synthetic remote (progress-only commit, then marker commit).
- 20:22:59 +07, 177s: marker commit touching a worker-y6c file passes.
- 20:23:11 +07, 189s: M7 case A, stale server holding 8771 with a wrong root.
- 20:23:23 +07, 201s: M7 case B, stale server answering 200 with tampered bytes, plus direct _verify_served_files call.
- 20:24:59 +07, 297s: M1 directory-probe follow-up (planted real directories).
- 20:25:07 +07, 305s: M1 symlink-dir probe (functools symlink passes, stdlib still wins because pre-imported).
- 20:25:20 +07, 318s: M1 symlink-dir probe with glob (passes AND shadows stdlib glob).
- 20:25:28 +07, 326s: sys.path confirmation, review of evidence complete, paper written.

## H5 (queue in code): PARTIAL

What the launcher does, verified line by line in tests/realistic/launch_y13.py (new file, 305 lines, all in the diff):

- Go order: check_go, lines 110 to 117, refuses with exit 2 unless Y13_GO=1. Present.
- Y6c marker: check_marker, lines 161 to 195, plus MARKER_RE lines 69 to 70 and ABORT_RE line 71. Present when a repo is given.
- Token: check_token, lines 118 to 134, requires /tmp/worker-y13-handover.json to exist, be valid JSON, be fresh (age 0 to 4h), and name a basis. Present.
- Runner-quiet: check_runner_quiet, lines 136 to 159, patterns run_*.py and hand_drive_e1.py, own ancestry excluded via _own_ancestry. Present. Preflight re-checks it after the lock in run_codex_y5.py lines 3471 to 3500, same patterns. Present.
- Predecessor ports: check_ports, lines 197 to 220, Y9 8769/4449 and Y8b 8767/4451 (PREDECESSOR_PORTS line 67). Present.
- Own ports: same function, OWN_PORTS 8771/4452 (line 68). Present. A second Y13 instance is refused.
- Geckodriver: check_geckodriver, lines 232 to 270, reads /tmp/geckodriver-*.pid, refuses a live geckodriver with a live parent, warns on orphans (parent 1). Present.
- Flock: main, lines 271 to 300, runs `flock -w 60` on zen_dom.lock and execs the runner with the ship env, returning the runner exit code. Present.

Marker regex against plan v2 C3 S2, quoted exactly:

- Plan v2 C3 S2: `^Y6c.*(nested|Wayland).*(complete|DONE|verdict|REPRODUCED|NOT REPRODUCED)` AND touches an improvements/worker-y6c-*.md file. Abort: `^Y6c.*(ABORT|abort)`.
- Launcher MARKER_RE: `^Y6c.*(nested|Wayland).*(complete|DONE|verdict|REPRODUCED|NOT REPRODUCED)`. ABORT_RE: `^Y6c.*(ABORT|abort)`. Character-identical to the plan strings (verified by string comparison in Python, True).
- Mechanical regex test, 11 completion cases and 3 abort cases, all matched expectation: progress commits ("Y6c nested probe started", "Y6c nested progress update") do not match, "Y6c complete" without nested/Wayland does not match, lowercase "y6c nested complete" does not match, "Y6c nested Wayland probe complete" matches. Note "completed" matches because it contains "complete"; that is the plan's own wording, not a launcher deviation.
- Mechanical git test on a synthetic remote: a todolist-push branch with only a progress commit touching improvements/worker-y6c-foo.md was refused with exit 2. A marker commit that touched NO file (empty commit) was also refused, correctly, because the path filter `improvements/worker-y6c-*.md` applies. A marker commit touching improvements/worker-y6c-foo.md passed and printed the commit hash. The path filter is load-bearing and works.
- Git log grep on the real todolist-push today returns nothing for either pattern, with or without the path filter. No Y6c marker exists yet. The queue gate is still closed, which agrees with Y13's log.

Residuals that keep H5 at PARTIAL, not FIXED:

1. The marker check is opt-in and the documented launch path opts out. check_marker skips with a printed note when no --repo is given (lines 166 to 170), and the operator's Y13_GO assertion stands instead. The SHIPPED.md launch line in this same diff is `Y13_GO=1 python3 launch_y13.py all` with no --repo. So the default, documented invocation never runs the marker check in code. That is the same procedural gate H5 complained about, moved into an env var set by the same operator who wants to launch. The code check exists and works, but the launch path does not use it. This is the sharpest H5 residual. Fix: make --repo required in the launcher (fail when neither --repo nor Y13_REPO is set), and put --repo in the SHIPPED.md launch line.
2. Codex executor processes are warning-only. The launcher prints a WARNING for any cmdline containing "codex" and does not refuse (check_runner_quiet). Preflight has no codex check at all (lines 3485 to 3500 check only run_*.py and hand_drive_e1.py). Plan v2 C3 S3 step 2 says "no Codex executor process driving a browser". The exact case redteam named, an E1 executor between arms with its driver down, is a codex CLI process and is not refused. Counterpoint, recorded as dissent below: a blanket refuse on any "codex" cmdline would false-refuse unrelated Codex work, and the E1 driver hand_drive_e1.py IS refused. I judge the warning-only treatment a genuine residual but not, on its own, a blocker. Minimum fix: refuse when a codex cmdline mentions hand_drive_e1.py, a browser profile, or geckodriver; warn otherwise. At minimum, record it as an accepted risk in the plan.
3. Y11b/Y14 ports are still unknown and unchecked. No check covers them: launcher checks Y9, Y8b, and own ports only; preflight checks Y9 and Y8b only. For Y14 this is not a live hazard for Y13's launch because Y14 queues AFTER Y13. For Y11b it is a real predecessor gap, acknowledged in plan v2 C3 S3 ("Y11b ports once its plan names them"). The only backstop is the run_*.py process-name pattern, which misses a Y11b runner under any other name and misses a stale Y11b server with no live process. This is unfixable in this diff until Y11b names its ports, so I record it as an accepted residual, not a fixable defect. It does not change the verdict, but the launch-time check must be re-run when Y11b names its ports.
4. Order deviation, judged immaterial: the launcher checks go order first, then marker, token, runner-quiet, ports, geckodriver, flock. Plan v2 C3 S3 orders marker (1), runner-quiet (2), ports (3), go order (4), flock (5), preflight (6). Checking go first is fail-fast and weakens nothing, because the marker check still runs (when a repo is given) before flock. Runner-quiet is before flock and ports are before flock, which are the two orderings that matter. Token before runner-quiet is also immaterial.
5. Minor: the abort marker is checked with the same worker-y6c file path filter as completion. The plan states the file-touch requirement for completion and states the abort message pattern without restating the file requirement. Applying the filter to abort too is stricter than the plan text and fail-closed, so I do not count it against H5.

## M1 (allowlist): PARTIAL

The allowlist code is in run_codex_y5.py _verify_manifest, lines 362 to 411. Allowed set: manifest paths, plus the manifest itself (line 400), plus codex-y5/SHIPPED.md (line 401), plus top-level __pycache__/ (line 406). Everything else found by base_dir.rglob("*") is refused.

Mechanical evidence on a staged ship built from committed bytes (27 files, manifest md5 d3e71259dd7a5de3fab663534724428c, matching the committed manifest):

- Clean ship: exit 0, manifest_ok true, 27 files checked.
- Planted live_metrics.py: refused, exit 2, "unexpected file in ship dir: live_metrics.py".
- Planted functools.py: refused, exit 2, same wording.
- Planted EXTRA.md: refused, exit 2, same wording.
- Hidden file .hidden: refused, exit 2.
- Planted real directories (functools/ with __init__.py, codex-y5/evilpkg/ with y.py): refused, exit 2, because rglob descends into real directories and flags their files. The directory case is closed for real dirs.
- Top-level __pycache__/ passes, exit 0, as intended.

Two holes found, both reproducible:

1. Symlinked directories bypass the allowlist AND can shadow imports. A symlink codex-y5/evil-link to /tmp passed with exit 0. Worse, a symlink named `glob` pointing at a directory containing a malicious __init__.py passed with exit 0 AND shadowed stdlib glob for an importer with the ship dir at sys.path[0]: `glob.__file__` resolved to /tmp/y13c3-ship/glob/__init__.py. run_codex_y5.py inserts the ship dir at sys.path[0] (line 117) and imports glob (line 104), so the shadow is live in the runner itself. (A functools symlink also passed exit 0, but did not shadow in my probe because functools is already imported at interpreter startup. Glob proves the mechanism.) Root cause: the loop skips every entry where p.is_dir() is true (line 403 to 404 in the current file, `if p.is_dir(): continue`), and rglob does not descend into symlinked directories, so a symlinked dir is never examined at all. Fix: refuse any directory or symlink whose relative path is not a prefix of a manifest path (plus __pycache__), or resolve symlinks and check their targets. This is the same class of hole M1 was asked to close, and the fix is a few lines.
2. Nested __pycache__ is refused. codex-y5/__pycache__/x.pyc was refused with exit 2, because the exemption only matches rel starting with "__pycache__/". No .py file exists under codex-y5/ today, so no realistic false refusal exists today, but the exemption is narrower than the comment describes ("__pycache__ (bytecode the import generates at load)"). Fix: exempt __pycache__ at any depth, or document top-level-only in the comment. Minor.

The stale-ship half of M1 is covered under the manifest-md5 pin decline below. The allowlist half, as specified by redteam ("refuse unexpected files"), is fixed except for the symlink bypass.

## M2 (cumulative wall cap): FIXED

Code, run_codex_y5.py:

- main offsets r.t0 by prior cum_ms: lines 3834 to 3841. attempt_t0 is kept before the offset (line 3834), then `r.t0 = time.perf_counter() - cum_ms[tid] / 1000.0` (line 3841).
- Per-primitive check Y13Runner._check_wall_cap, lines 636 to 652, measures `time.perf_counter() - self.t0`, so on attempt 2 it measures cumulative time.
- Post-hoc check, lines 4043 to 4052, measures `(time.perf_counter() - r.t0) * 1000`, also cumulative via the offset t0.
- Accounting, lines 4082 to 4085: attempt_elapsed_ms from the un-offset attempt_t0, cum_ms accumulates it, summary keeps elapsed_ms per attempt and adds cumulative_elapsed_ms. WALL_CAPS test 01 is 360s (lines 3222 to 3226).

Mechanical simulation on the imported module (real _check_wall_cap, real WALL_CAPS):

- t0 offset by 200s on a 360s cap: no raise, pass-through, as expected.
- t0 offset by 370s on a 360s cap: raised "wall cap exceeded: 370s > 360s at primitive 'probe'", as expected.
- Post-hoc arithmetic: 200s cumulative does not trip, 370s trips. Both per-primitive and post-hoc paths agree.

Session-creation-failure path, exact lines 3843 to 3870: on wd.__enter__ failure, r.failures is appended, the summary is built with outcome "session-creation-failure", results.append(s), and the attempt loop breaks unconditionally (lines 3864 to 3870, break in both branches). cum_ms is NOT updated on this path (the update at line 4083 is unreachable from here). That is fine and not a fresh-budget hole, because attempt 2 never runs after a session-creation failure: the loop breaks after the first session failure regardless of wd_failures, and the run aborts after two consecutive session failures across tests. Two small inconsistencies noted, neither a lie: the session-failure summary carries elapsed_ms from the base Runner.summary (computed from the fresh t0) but no cumulative_elapsed_ms key, unlike normal-path summaries. Recommend adding cumulative_elapsed_ms (equal to that attempt elapsed) for uniformity. Not a verdict changer.

## M3 (FIXTURE-UNAVAILABLE substring): FIXED

Code, run_codex_y5.py lines 3904 to 3905: `elif (msg.startswith("FIXTURE-UNAVAILABLE") or ": FIXTURE-UNAVAILABLE" in msg):`. This sits directly under the INFRA match at line 3901 (`msg.startswith("INFRA:") or ": INFRA:" in msg`), so it is consistent with the ": INFRA:" match exactly as redteam asked. The comment at lines 3906 to 3911 explains the wrapped form ("step failed: ...: RuntimeError: FIXTURE-UNAVAILABLE: ...") that the startswith check alone misses. Verified by reading and by the L1 test below, where a FIXTURE-UNAVAILABLE raise inside r.step reaches main unwrapped and would match the startswith branch. Present in the cb26d1d diff (added lines).

## M4 (outcome truth): FIXED

Code, run_codex_y5.py lines 4033 to 4037: after the infra_blocked chain (lines 4025 to 4032, which sets or resets the streak, with guard and fixture-unavailable leaving it unchanged) and before the audit block (lines 4038 onward), `if outcome == "pass" and r.failures: outcome = "failed"`. Placement is exactly as specified. The audit block condition `if outcome == "pass" and not r.failures:` then correctly skips audit for a failed test.

Per-attempt finalization paths that build a summary:

- Normal path: reaches the M4 line. Covered.
- Session-creation-failure path (lines 3856 to 3862): does NOT reach the M4 line, but it is exempt with good reason. It sets outcome directly to "session-creation-failure", never "pass", and r.summary() gives pass False because r.failures is non-empty. No lie is possible on that path.
- Guard paths set outcome to "guard-defect" or "guard-inconclusive" explicitly before reaching M4, and M4 does not overwrite them because outcome is not "pass". Correct.
- Infra-blocked, fixture-unavailable, and failed outcomes are set by the exception handler before M4, and M4 does not touch them. Correct.

## M7 (structured server failure): FIXED

Code, run_codex_y5.py lines 3712 to 3728: start_server is wrapped in try/except in main, printing "SERVER FAILED ..." plus a suite JSON with server_failed true, and returning 2.

_verify_served_files, lines 414 to 438: returns a (ok, checked, bad) tuple, never raises. Every urlopen call is inside try/except per file, and a _manifest_entries error returns a False tuple. The call site at lines 3730 to 3741 checks `if not served_ok` and prints a structured served_files_failed JSON with return 2. So a served-check failure cannot escape as a traceback either. The redteam fix asked to wrap start_server "and _verify_served_files" in the same pattern; the served check is handled by its boolean return plus the structured branch, which achieves the same result. I accept that as meeting the fix.

Mechanical reproduction on the VM, staged ship, port 8771:

- Case A, stale server holding 8771 with the wrong root (probe 404s, bind raises EADDRINUSE): exit 2, "SERVER FAILED RuntimeError: could not start or reuse a server on port 8771 ... [Errno 98] Address already in use", suite JSON with server_failed true, 0 occurrences of "Traceback".
- Case B, stale server answering 200 on the probe but serving tampered bytes: exit 2, "SERVED FILES FAILED" listing all 27 files (26 fetch failures plus the tampered test-01 fixture with served md5 b4b695f3c274b96d343f6ffca3abd610 against want ac0f3f5f6510bbd9c5ccf32e2b2f8301), suite JSON with served_files_failed true, 0 occurrences of "Traceback".
- Direct call to _verify_served_files against a dead port returned (False, 0, [27 fetch failures]), no raise.

## L1 (unwrap INFRA in step): PARTIAL

Code, run_codex_y5.py Y13Runner.step, lines 679 to 708. On failure, if the caught exception's formatted error contains "INFRA:" or "FIXTURE-UNAVAILABLE" (lines 697 to 698), the ORIGINAL exception is re-raised (line 701, `raise caught`). Otherwise it raises RuntimeError("step failed: ...") as before.

Mechanical test on the imported module:

- A step raising RuntimeError("INFRA: hidden-body test") re-raised as the original RuntimeError, message unchanged, not wrapped.
- A step raising RuntimeError("FIXTURE-UNAVAILABLE: x: no body element") re-raised unwrapped.
- A step raising ValueError("plain boom") stayed wrapped as "step failed: s3: ValueError: plain boom".

So the re-raise itself is real and verified, and main now sees the original exception for the two marker classes.

Why PARTIAL and not FIXED: the decision to re-raise still uses a substring test on the formatted error string (`"INFRA:" in error or "FIXTURE-UNAVAILABLE" in error`). That is the same fragility L1 complained about, moved one level down. L1 asked to "match on the unwrapped exception (catch the INFRA raise before r.step wraps it, or carry a marker attribute on the exception)". Y13's fix does deliver the unwrapped exception to main, which is the mechanism L1 wanted, but the trigger is still a string test. A future step lambda raising a plain error whose message happens to contain "INFRA:" would still be re-raised as INFRA, and a future INFRA raise phrased without the literal "INFRA:" would still be wrapped. The surface is narrower than before (the test is on the original exception's own message, not on a wrapped message, and check failures do not raise at all), but the fragility is not removed. Fix: raise dedicated marker exception classes for infra and fixture-unavailable (or set a marker attribute), and test `isinstance` in step. Small change, worth doing because it is the point of L1. Severity is LOW, so this alone would not block, but it belongs in the AMEND list.

## L2 (SHIPPED.md on the allowlist): FIXED

Code, run_codex_y5.py line 401: `allowed.add(f"{SUITE_DIR}/SHIPPED.md")`. Present in the diff. Note the limit of this fix, which is the same limit redteam noted: SHIPPED.md is allowlisted (its presence is tolerated) but its CONTENT is not md5-verified, because it is not in the manifest. A tampered SHIPPED.md would pass --verify-manifest. That is the redteam's own framing of L2 ("Fix with M1 (allowlist the ship dir; SHIPPED.md is on the allowlist)"), so the fix as specified is done. The content-verification gap is real but belongs to the manifest-md5 pin question below, not to L2 as written.

## Manifest-md5 pin DECLINE: DECLINE SOUND as an argument, UNSOUND as a substitute

Y13 declined the redteam ask to pin the expected manifest md5 in the runner, on grounds it is self-referential, and records the manifest md5 in SHIPPED.md, the commit, and the log instead.

Is the self-reference claim true? Yes, as a practical matter. Trace the dependency: the pin value lives in run_codex_y5.py, so changing the pin changes the runner bytes, which changes the runner md5, which changes the manifest entry for run_codex_y5.py, which changes the manifest file bytes, which changes the manifest md5. For the pin to be correct it would have to equal a value that depends on itself. A fixed point could exist in principle as a 128-bit preimage search, but it cannot be constructed by any feasible procedure: you cannot write the pin down without already knowing the manifest md5, and you cannot know the manifest md5 without the pin. Y13's comment in the code (lines 388 to 399) states this correctly, and the log records the same reasoning. The decline of an in-runner pin is SOUND. The same argument kills the obvious variants: a pin in launch_y13.py fails the same way (the launcher is in the manifest too), and a pin in SHIPPED.md fails differently but just as fatally, because SHIPPED.md content is not verified by the runner (see L2), so a pin there would be unverified ink.

Is the outside-the-ship recording an adequate substitute? No, not as a launch-time gate. What exists now: SHIPPED.md line 26 records manifest md5 d3e71259dd7a5de3fab663534724428c and 27 files, the commit message records it, the log records it, and the suite JSON records the manifest md5 of the ship that actually ran. Who verifies it, and when? Nobody at launch time. The runner compares the ship against its own manifest (self-consistent by construction) and never compares the manifest md5 against any outside value. A stale but self-consistent ship, older runner plus older manifest plus older fixtures, still passes --verify-manifest with exit 0. The redteam proved exactly this on the earlier bytes with a corrected-manifest control (manifest md5 2c2befa9... accepted, different from the committed 3606fe84...). Nothing in cb26d1d changes that half of M1. The recording is post-hoc audit evidence, not a refusal. It lets a human compare the suite JSON manifest md5 against the commit after the run, which is detection after the fact, not prevention.

What should be done instead: keep the decline of the in-runner pin, and close the stale-ship half outside the ship, where the trust root actually lives (git). The clean fix is in the launcher, when --repo is given: fetch the committed codex-y5-manifest.json from origin/todolist-push and compare its md5 against the ship manifest md5, refusing on mismatch. That check has no self-reference, because the compared value comes from git, not from the ship. It composes with the H5 fix above: making --repo mandatory gives both the marker check and the manifest-md5 check a repo to read from. If --repo must stay optional for some reason, the fallback is a ship-time procedure with a written record (stage the ship from git bytes, record the manifest md5 in the launch log, and have the operator compare before setting Y13_GO), but that is procedure, not code, and should be labeled as such.

Verdict on the decline: DECLINE SOUND on the self-reference argument. The substitute as it stands is INADEQUATE as a launch-time gate, and the stale-self-consistent-ship half of M1 remains open. This is the second reason M1 is PARTIAL.

## Dissent and debate

- On H5 codex warning-only: one voice in this review says a blanket refuse on any "codex" process is the plan-literal reading and the between-arms E1 case is exactly what H5 named, so warning-only should be a BLOCK-level hole. The other voice says the operator runs Codex tooling on the same machine for unrelated work, a blanket refuse would false-refuse legitimate launches, and the E1 driver hand_drive_e1.py IS refused, so warning-only is a defensible engineering call. I side with the second voice, with the compromise fix recorded above (refuse on codex cmdlines that mention the driver, a browser profile, or geckodriver). Recorded here so the adjudicator can see the disagreement.
- On L1: one voice says the re-raise IS the fix L1 asked for ("catch the INFRA raise before r.step wraps it") and the remaining substring trigger is defense in depth, so L1 should be FIXED. The other voice says the trigger is the fragility, and a substring test that decides the re-raise is the same class of bug in a smaller coat. I side with the second voice, narrowly, because the fix text in L1 explicitly names the substring as the problem, and the trigger survives. The disagreement is about wording, not about the code, and the fix is small either way.
- On the pin decline: no dissent on the self-reference argument. The debate was only about whether post-hoc recording counts as a substitute. It does not, for launch-time refusal. A human audit after the run is real value, but it is not the gate M1 asked for.
- On overall verdict: AMEND versus BLOCK was debated. The case for BLOCK is that H5's marker check is skipped on the documented launch path and M1 has a reproducible symlink bypass, and both touch the queue and integrity gates. The case for AMEND is that both fixes are small, mechanical, and verifiable in minutes; the queue gate is currently closed anyway (no Y6c marker, Y8b live), so no live run can start on the current bytes by accident; and every other item in scope is FIXED with mechanical evidence. I side with AMEND, with the condition that no live launch happens until the AMEND fixes land and are re-verified on the final bytes with a regenerated manifest.

## Overall verdict for this scope: AMEND

FIXED: M2, M3, M4, M7, L2.
PARTIAL: H5, M1, L1.
Manifest-md5 pin decline: SOUND as an argument, INADEQUATE as a substitute.

Exact fixes required before a live launch (all small, all re-verifiable mechanically):

1. H5, marker opt-out: make --repo required in launch_y13.py (refuse when neither --repo nor Y13_REPO is set), and change the SHIPPED.md launch line to include --repo pointing at the laptop checkout. Re-verify with the synthetic-remote test: progress-only refuses, marker plus file-touching passes, no --repo refuses.
2. H5, codex executor: refuse a codex process when its cmdline mentions hand_drive_e1.py, a browser profile, or geckodriver; warn otherwise. Or record the warning-only treatment as an accepted risk in plan v2 C3 S3 with the between-arms E1 case named.
3. M1, symlink bypass: in _verify_manifest, refuse any directory or symlink whose relative path is not a prefix of a manifest path (plus __pycache__), instead of skipping all directories. Re-verify: symlinked glob dir refuses with exit 2, clean ship still passes.
4. M1, stale ship: in launch_y13.py, when --repo is given, fetch the committed codex-y5-manifest.json from origin/todolist-push and refuse when its md5 differs from the ship manifest md5. Re-verify with a staged stale ship (older runner plus older manifest): refuse with exit 2.
5. M1, nested pycache: exempt __pycache__ at any depth, or document top-level-only in the comment. Re-verify: codex-y5/__pycache__/x.pyc passes.
6. L1, marker exceptions: raise dedicated exception classes (or set a marker attribute) for INFRA and FIXTURE-UNAVAILABLE raises, and test isinstance in Y13Runner.step instead of a substring. Re-verify: INFRA and FIXTURE-UNAVAILABLE unwrap, plain ValueError stays wrapped, and a step error whose message merely contains "INFRA:" stays wrapped.
7. M2, uniformity (minor): add cumulative_elapsed_ms to session-creation-failure summaries.
8. After fixes 1 to 7: regenerate the manifest LAST from the final bytes, update SHIPPED.md and the log with the new manifest md5, and re-run the mechanical gates on the exact bytes (clean ship exit 0, planted-file and symlink refusals exit 2, marker dry runs, stale-server structured JSON exit 2, wall-cap 200s pass and 370s trip).

Accepted residuals, not fixable in this diff: Y11b ports unknown and unchecked (backstop is the run_*.py process-name pattern only); Y14 queues after Y13 so its ports are not a predecessor hazard; the geckodriver PID sweep only sees drivers that wrote a /tmp/geckodriver-*.pid file. These must be re-checked when Y11b names its ports.

No live driving was done in this review. No file other than this paper was created or modified. No em dash or en dash appears in this paper. No personal information appears in this paper.

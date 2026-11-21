# Worker Y14b re-stage log: clone1-batch3 live runner from suite HEAD 1d23532

Worker: Y14b (Muse live-runner prep). Owner order: full autonomy, machine
handed over 18:24 21/11, owner out and busy. Lauren Tan direction applies.
Slot: live run waits for the slot after Y13 clears (Y13f still fixing its
BLOCK, re-review pending). This worker does PREP ONLY: re-stage, verify,
council + redteam over the re-stage diff, ship to the laptop. No Zen
driving in this task.

## Baseline

- Old staged suite: ed78e83 on main (Y10 reconciled best of both).
- New suite HEAD: 1d23532 on main (Y15 D1 fix, log 3b50e94). Diff
  ed78e83..1d23532 touches ONLY t10-music-player/check.mjs (+240/-37,
  167 -> 353 lines) and t10-music-player/README.md (+97) within
  tests/realistic/clone1-batch3/ (the range overall touches 7 files;
  the other 5 are outside the suite and irrelevant to the runner).
  t01-t09 check.mjs files are byte-identical between the two commits
  (verified by git blob hash comparison per file, re-verified by
  Council 3). Fixture untouched.
- Runner before re-stage: tests/realistic/run_batch3.py as at commit
  70061e2 (blob 72d8eb6) (Y14 redteam-2 AMEND fixes H1-H5 + M1). No manifest mechanism exists
  in this runner (grep: no _manifest_entries, no --verify-manifest, no
  MANIFEST constant). The suite is therefore verified by md5 against
  the git HEAD at ship time (the Y14 approach), not by a manifest.
  Manifest positive/negative cases from the task list are NOT
  applicable to this runner; that gap is recorded here and in the
  council/redteam brief, not papered over. Adding a manifest would be
  new design work beyond a re-stage; the redteam-2 AMEND condition was
  "re-stage from the new HEAD and update the t10 translation".
- H2 fix source: Y13f's tokenizer (run_codex_y5.py working tree,
  uncommitted at copy time, Y13f log 20:47-21:05 21/11: "H2 tokenizer
  in both copies"). Copied verbatim into run_batch3.py; logic
  identical, verified by diff after the copy (see below). Y13f has
  NOT landed a commit yet, so the source is its working-tree code,
  recorded here.

## Timed work log

- 21:06 +07: start. Read the Y14 plan, run_batch3.py (2093 lines),
  the new t10 check.mjs (1d23532, 353 lines), the Y13r BLOCK papers
  (f48b54c) and Y13f's H2 tokenizer in the working tree.
- 21:06-21:09 +07: edits. (1) Module docstring: suite HEAD ed78e83
  -> 1d23532, t10 description updated. (2) Added `from pathlib
  import Path`. (3) New run_b3_t10: exact_zero_next() same-task
  click+read helper; playing Next exact-zero + sampler + three-point
  advancing (gain>=2, 2..11, second gain>=2); frozen Next exact-zero
  + resume 2..11 + resumeLater gain>=2 and 2..11; double Prev
  (River Road, Morning Light); shuffle Next exact-zero + sampler +
  advancing; frozen shuffle Next exact-zero (City Rain) + resume
  checks; Prev to Mountain Air; playing wrap exact-zero + sampler
  (posBeforeWrap>=2 gate after 700 ms play); frozen wrap exact-zero
  + resume checks; supplementary D1 probe REMOVED (superseded by
  the real frozen-Next steps). (4) H2 fix: _script_basename_is_runner,
  _is_python_token, _argv_tokens, _is_runner_cmdline,
  CODEX_REFUSE_MARKERS, _ppid_of copied verbatim from Y13f's
  run_codex_y5.py working tree; new _scan_other_runners() helper;
  launch_gate() pgrep -f sweep replaced by the scan; run_preflight()
  re-checks at the top before any tab opens.
- 21:09 +07: py_compile OK; import OK, 10 tests registered
  (b3-t01..b3-t10); exact_zero_next present. H2 helper diff vs
  Y13f: all 5 functions identical in logic (docstring tail of
  _is_runner_cmdline differs by design: it records this Y14
  application instead of the "must apply" note).
- 21:10 +07: H2 probe /tmp/y14b-h2-probe.py. First run 20/21: the
  "hits exactly the 3 dummies" expectation was WRONG, not the code:
  the flock and bash wrapper processes themselves are hits by
  design (their -c string executes the runner), and wrapper
  children orphan on wrapper SIGTERM. Corrected the expectation
  (dummies + wrappers + recursive descendants) and the cleanup
  (kill descendants deepest-first). Second run 21/21 PASS, exit 0:
  14 unit synthetic cmdlines + 7 live /proc cases (bare-relative,
  flock -c, shell -c caught; mere mention not caught; ancestry not
  flagged; old pgrep -f false-positives on the mention process).
  No run_foo.py strays left (one transient PID was the exec shell
  matching its own pgrep pattern).
- 21:11 +07: transcription /tmp/y14b-transcribe.py. First run 4
  failures, all script-order bugs (now-playing assert precedes the
  min check in the runner, as in check.mjs; exact_zero_next count
  included the def line). Fixed the script, second run ALL PASS,
  exit 0: 72 ordered assert alignments (69 checker asserts + 3 volume
  extras, independently re-derived by Council 1), D1 probe gone, 3
  exact-zero call sites, sleep counts 0.7x3 / 0.5x1 / 0.4x1 /
  0.35x10, sampler fail-closed. (An earlier log draft said 68; the
  correct count is 72.)
- 21:11 +07: launch-gate dry run /tmp/y14b-gate-dry.py (faked
  Zen/Marionette/ports, REAL /proc scan + REAL dummies). 4/4 PASS:
  quiet slot passes; bare-relative dummy refuses (pid printed);
  mention-only passes; no LIVE_SLOT_OK refuses. No strays.
- 21:11 +07: applicability notes, recorded honestly. This runner
  has NO manifest mechanism (grep: no _manifest_entries, no
  --verify-manifest, no MANIFEST constant) and NO STEP_COUNTS audit
  mechanism (grep: no STEP_COUNTS/_audit_count/AUDIT in
  run_batch3.py or run_live.py). So the task's --verify-manifest
  cases and audit simulation are NOT APPLICABLE here, not skipped:
  the suite is verified by md5 against the git HEAD at ship time
  (the Y14 approach). Adding a manifest would be new design work
  beyond a re-stage; redteam-2's AMEND condition asked only for a
  re-stage + t10 translation update. The council/redteam brief
  carries this so they judge the re-stage diff, not demand a
  manifest.
- 21:12 +07: git diff vs 70061e2: run_batch3.py +452/-35. Changed
  defs only: header/imports, run_b3_t10, run_preflight (re-check),
  H2 helpers (inserted before launch_gate), launch_gate (sweep).
  No other test function touched; t01-t09 check.mjs files are
  byte-identical between ed78e83 and 1d23532 (git blob hash
  comparison, re-verified by Council 3).
- 21:12 +07: committed f732d6a on todolist-push (3 files: runner,
  plan, this log), pushed, ls-remote verified. Only my 3 files
  staged; Y13f's uncommitted working-tree changes untouched.
- 21:13 +07: council (3 voices) + redteam spawned over the re-stage
  diff f732d6a only. Council 1: t10 translation faithfulness.
  Council 2: H2 fix + gate/preflight integration. Council 3:
  re-stage hygiene (suite HEAD, diff scope, plan consistency, N/A
  honesty, Y15 limits, log evidence). Redteam: break the diff
  (false-pass paths, exact-zero soundness, H2 bypasses and
  false-positives, gate/preflight window, stale references). Ship
  to the laptop waits for their verdicts (ship must be from final
  bytes after any fixes).

## Review verdicts (21:13-21:25 +07)

- Council 1 (paper 18b150b): GO. t10 translation 69/69 checker
  asserts, same order, same thresholds; 72 = 69 + 3 volume extras.
  Watch item: middle advancing read margin (runner serializes the
  sampler + now-playing assert, so the advancing read lands near
  8-10 ticks vs bound 11; watch details.positionAdvancingAfterNext
  and details.positionAdvancingAfterShuffleNext; if either reads 11
  repeatedly, read after_sampler before the now-playing text check).
  Honest notes: log count "68" stale (correct 72); step-abort
  semantics pre-existing.
- Council 2 (paper b445257): AMEND. Fix 1 (required, code):
  python3 -m run_batch3 returns False, bypasses the single-runner
  guard; four-line fix specified (accept bare run_* / hand_drive_e1
  token after -m); same fix should go to sibling copies
  run_codex_y5.py / launch_y13.py or the "identical logic" claim
  breaks. Fix 2 (cosmetic): stale comment "pgrep sweep below" at
  line 2364. Known residuals: double-nested flock -c quoting,
  runpy.run_path in -c.
- Council 3 (paper 41fa919): AMEND. F1 (load-bearing, plan L413):
  still says suite "copied from main ed78e83", must be 1d23532.
  F2 (L36-37): Y12 present tense, reword to past tense with pointer.
  F3 (L427-428): launch gate still describes old pgrep sweep. F4
  (L520): "all byte-identical" overstates the docstring difference.
  F5 (L479-487): Y12 Consequence paragraph mark SUPERSEDED. F6
  (L269 + L534): seek citation L103-106 is old (new L169) + pin the
  ship-time md5 procedure. F7 (log wording): qualify "touches ONLY
  t10..." with "within tests/realistic/clone1-batch3/", fix
  "IDENTICAL (docstring differs)" self-contradiction, clarify
  "run_batch3.py at 70061e2" as commit 70061e2 (blob 72d8eb6).
  Judgment on missing manifest: AMEND-level, not BLOCK (adding a
  manifest is new design work scoped out by redteam-2; staging
  verified at git blob level; required fix is F6).
- Redteam (paper 5e6b385): BLOCK. H1 HIGH: gate bypass x5
  (python3 -m, python3 -c import, renamed copy, shebang renamed
  copy, spoofed argv[0]; all live-confirmed). H2 HIGH: playing wrap
  that stops the timer passes everything (no advancing check after
  the wrap; next playlist click restarts the timer and masks it).
  H3 MEDIUM: later advancing reads unbounded, late jump passes.
  H4 MEDIUM: 2..11 bounds miscalibrated for the runner's transport
  (correct fixture reads 11 at 50 ms/round trip, zero margin; fails
  at 75 ms). M1 MEDIUM: start_server() reuses a foreign server on
  8771 and serves FOREIGN bytes while the gate disk check passes
  (reproduced live). M2 MEDIUM: no re-scan after preflight; scan is
  same-pid-namespace only. M3 LOW: codex false-positive (substring
  match on whole cmdline; sleep process argv[0] "codex marionette
  notes" flagged). M4 LOW: plan L413 ed78e83; no md5 list, SHIPPED
  entry, or manifest; clone1-batch3 absent from todolist-push.
  L1 LOW: int() truncation in position reads. L2 LOW: ancestry
  exclusion could hide a runner descendant (latent only).

## Adjudication (Y14b fix pass, 21:25-21:35 +07)

Redteam BLOCK downgraded to AMEND with fixes. Each finding decided
on its merits; nothing accepted or declined silently.

- H1: FIXED in part. The -m form (Council 2 Fix 1, exact four-line
  spec) and the -c import form (a bare runner module name after
  "import"/"from" in -c words) are covered in _is_runner_cmdline.
  DECLINED: renamed copy, shebang renamed copy, spoofed argv[0],
  extensionless script, direct .pyc (adversarial forms, outside
  this gate's accidental-collision threat model; no fleet workflow
  uses them; recorded as residual limitations in the docstring).
  DECLINED: flock lock held for the whole run (redteam's primary
  fix). A lock taken by only this runner gives no guarantee: the
  other runners (run_live.py, run_agyq2.py, run_fcck.py) do not take
  it, so a second runner of any shape still runs. The lock only
  works fleet-wide, which is a Muse-level fleet decision, not a
  change for this runner. FLAGGED to Muse.
- H2: plan claim CORRECTED (redteam's own alternative (b)): the
  playing wrap is reset-only tested, liveness untested, and the
  "live run is the real test" claim for R1/R2/R3b is withdrawn.
  DECLINED: adding a post-wrap advancing check to the runner (spec
  divergence from the checker; the gap is Y15's documented R2
  escape, landed per a pre-set stopping rule). Checker follow-up
  proposed for a future suite revision, FLAGGED to Muse.
- H3: DECLINED (checker deliberately gain-only on the later reads;
  documented limit, inherited by the runner). Recorded in the plan
  as an inherited limit, not a gate.
- H4: now-playing assert moved after the advancing-later read at
  the playing and shuffle Nexts (redteam's (c) alternative): its 2
  round trips no longer sit in the sampler-to-advancing path. Assert
  SET identical to check.mjs; only the order of two independent
  asserts is swapped. DECLINED: re-deriving the caps in the runner
  (divergence from the checker). Margin analysis recorded in the
  plan: at measured laptop rates (Y11b proof: eval median ~2 ms,
  click steps ~56 ms for ~3 POSTs, round trip ~2-19 ms) the correct
  fixture reads about 8-9, margin ~2 ticks, ~2.4 after the move.
  Council 1's suggested reorder (read after_sampler before the
  now-playing check) is subsumed by this move.
- M1: FIXED. _verify_served_fixture() fetches the t10 fixture over
  HTTP after start_server() and compares its md5 to the on-disk
  root; main() refuses (exit 2) on mismatch or fetch failure.
  run_live.py's reuse probe NOT changed (shared driver, owned by
  Worker P).
- M2: FIXED in part. run_one() re-scans at the top of each test; a
  hit returns an INFRA summary before any tab is driven (one retry
  + breaker count). DECLINED: flock-lock part (same as H1, flagged
  to Muse).
- M3: FIXED. "codex" anchored to the executable token
  (_is_codex_executor: argv[0] basename, or a token exactly "codex";
  marker required in a different token). Plain-codex warning
  restored in launch_gate() (warning-only, never a refusal).
- M4: FIXED (same as Council 3 F1/F6): L413 updated to 1d23532;
  suite md5 list + pinned ship procedure in the plan. No manifest
  (Council 3 judgment stands).
- L1: FIXED. position() and exact_zero_next() return the raw Number,
  no int() truncation.
- L2: DECLINED (latent only; no runner-descendant topology exists
  in this fleet; the fix would weaken the -c ancestry exclusion).
  Recorded.
- Council 2 Fix 1 + Fix 2: FIXED (see H1; stale comment at 2364
  updated). Sibling copies run_codex_y5.py / launch_y13.py need
  the same -m fix; Y14b does not edit Y13f's in-progress files.
  FLAGGED to Muse/Y13f.
- Council 3 F1-F7: FIXED (all plan/log wording + pinned ship md5
  procedure, suite md5s computed from git blobs at 1d23532).
- Council 1 watch item: addressed by the H4 move + margin analysis
  + watch keys in the plan. Log count fixed 68 -> 72.

## Fix-pass verification (21:31-21:35 +07, all on the VM)

- py_compile OK; import OK, 10 tests (b3-t01..b3-t10).
- H2 probe /tmp/y14b-h2-probe.py: 45/45 PASS, exit 0 (27 unit
  synthetic cmdlines incl. -m x3, -c import x2, -c string-mention
  False, codex anchor x7, residuals x6; 7 live /proc cases incl.
  -m dummy caught, codex executor caught, codex false-positive NOT
  caught; M2 run_one returns INFRA in 1 ms with a runner live, no
  WD session opened). No strays left.
- Transcription /tmp/y14b-transcribe.py (updated for the new
  now-playing order): 82 PASS lines (72 order + 10 structural),
  0 failures, exit 0.
- Launch-gate dry run /tmp/y14b-gate-dry.py: 4/4 PASS, exit 0.
- M1 probe /tmp/y14b-m1-probe.py: 3/3 PASS, exit 0 (matching bytes
  accepted, md5 eb814c944dab6279417c6182e1950876; foreign bytes
  refused; 404 refused). First run failed on a probe-harness bug
  (httpd.shutdown() without server_close(), port still bound;
  then a sed that rewrote stop() into a self-call); both fixed in
  the probe, not the runner.
- No em/en dash in the fix diff (grep 0), no ydotool, no personal
  info.
- Fix commit: 8bee524 (todolist-push, pushed, ls-remote verified
  8bee5249f6e86fce2763bc807cc9b2b1e40d9de1). run_batch3.py at this
  commit: git blob ed4de81d914f3a75df31554c0b2369110f7e27b0, md5
  65818867865ad4772e78cc2bcac015d6 (ship-time expected values for
  the plan's md5 procedure).
- Fresh council (3) + redteam over the FIX DIFF only: spawned after
  this commit (per the Y13r pattern). Ship to the laptop waits for
  their verdicts.

## Fix re-review verdicts (21:36-21:44 +07)

- Council 1 (paper 0388381 + hash follow-up e05e56f): GO. Fix diff
  is exactly the two claimed changes; assert set 69/69, no threshold
  changed; moved asserts prove the same thing; frozen Nexts in place;
  transcribe 82 PASS; int() removal sound. H4 margin recomputed from
  the Y11b proof: 850 ms + 3 round trips after the move (Council 3
  counts 4; the difference is whether the advancing read's own
  transit counts, at most 0.19 ticks); at 2 ms RTT value 8 or 9,
  margin 2 discrete (2.44 continuous); at 19 ms value 9, margin 2
  (1.93 continuous); at 50 ms reads 10 (margin 1); at 100 ms reads
  11 (zero); at 150 ms reads 13 (FAIL). Margin still thin, does not
  meet redteam (c)'s 3-tick bar; GO because the thinness was
  adjudicated with the watch item as tripwire. Ship condition: the
  live run re-measures and honors the watch item.
- Council 2 (paper 9757161): AMEND, docstring-only. H2 probe 45/45
  + gate dry 4/4 + own extra probe 25/25 re-run green. Required:
  (1) the "identical logic" sync claim is now false, siblings
  unfixed; (2) record the new residual "import os, run_foo"
  (runner second in a comma list) misses; (3) qualify
  "extensionless/.pyc all miss" as run_*/hand_drive_e1 only
  (run-nested without suffix returns True). Flag: siblings at HEAD
  still need the fix (run_codex_y5.py:3604, launch_y13.py:125 old
  matcher; M3 substring predicate still at run_codex_y5.py:3776,
  launch_y13.py:248).
- Council 3 (paper e162834): AMEND, R1-R4 plan-only. F1-F5, F7 PASS;
  hash records PASS; H2/H3 correction PASS; adjudication PASS. H4
  arithmetic mostly verified, one count off (4 round trips
  post-move, not 5; 6 pre-move). F6 PARTIAL: all 23 md5s correct
  and seek L169 correct, but the pinned command does not run:
  (G1) find path tests/realistic/clone1-batch3 fails against the
  faithful /tmp/y14-server layout (suite at
  /tmp/y14-server/clone1-batch3/...); (G2) file set misses t09
  detail.html (md5 40dfc0db44aa8448341587f8559b773a) and prefs.html
  (1169a1d5a1a6599093bdedac9c2aa74e), both opened by t09; (G3)
  run_batch3.py md5 line has the same path problem and says compare
  against "the fix commit's blob hash" instead of the recorded md5.
  Not BLOCK (wrong path fails loudly, values right).
- Redteam (paper 04ce6b1): AMEND, no BLOCK-grade finding. F1 MEDIUM:
  served check verifies only t10 (1 of 10); mixed server, redirect
  to correct bytes, and UA-split server all pass. F2 MEDIUM: -m
  branch misses "python3 -mrun_batch3" and "python3 -m
  foo.run_batch3" (both proven executing live) plus -X/-W
  flag-with-value forms. F3 LOW: codex anchor accepts "codex" in
  any token (grep/cat/echo false-flags, all reproduced live). F4
  LOW: siblings still old, docstring "(identical logic)" false.
  F5 LOW: "~2.4-tick margin" holds only at 2 ms RTT (1.93 at 19 ms,
  1.0 at 50 ms, first possible fail above 83 ms, guaranteed at
  117 ms); the move itself is correct (first-fail RTT 50 to 83 ms).
  F6 LOW: -c bypasses __import__/importlib/exec all execute live
  and evade; plus a live import-only FP (import without main()
  flagged). F7 INFO: mid-test runner start not caught until the
  next test's re-scan (0.3 s dummy proven); no code change, record
  the window. F8: declined items all reproduced live, none a
  plausible accidental fleet form; correction: double-nested -c is
  actually caught live via the leaf process, so the docstring
  overstates that residual.

## Adjudication, fix pass 2 (21:44-21:52 +07)

- F1: FIXED in part. Served-fixture check now covers all 12
  browser-served files (10 fixtures + t09 detail.html/prefs.html),
  not just t10. DECLINED: redirect refusal (the md5 is the check;
  a redirect to correct bytes is harmless, to foreign bytes fails
  md5) and UA-spoofing (adversarial server behavior, outside the
  threat model). Both recorded as known limits in the docstring.
- F2: FIXED. Joined -m accepted; dotted -m accepted for exact
  runner module names only (foo.run_tests does not flag); spaced
  -W/-X value forms accepted via the token two back. All three
  are precise (no new false-positive class) and probe-verified.
- F3: FIXED. "codex" restricted to executable positions (argv[0],
  first word after -c, word after env). grep/cat/echo FPs fixed
  live. sudo-prefixed codex recorded as a gap (no fleet launcher
  uses sudo for codex).
- F4: FIXED by correcting the claim (docstring now states the
  "identical logic" claim is FALSE and the sync belongs to Y13f).
  The marker tuple comment qualified the same way. Siblings NOT
  edited (Y13f's files).
- F5: FIXED by restatement. Margin now a range in the plan: 850 ms
  + about 3.5 effective round trips (Council 1 counts 3, Council 3
  counts 4, bracketing the true value); expected read 8-9, margin 2
  discrete (1.93-2.44 continuous); first fail roughly 70-85 ms
  (tick-phase dependent), sure fail ~100-117 ms; the move raised
  the first-fail threshold from ~50 ms to ~70-85 ms. The plan's
  "850 ms + 5 round trips" (fix pass 1) is corrected here, not
  rewritten in history.
- F6: RECORDED, no code change (per the redteam's own U6).
  Residuals added to the docstring: __import__ / importlib /
  exec(open().read()) bypasses; the import-only FP is a
  fail-closed over-approximation (only a literal -c import
  invocation trips it; importing the module inside a process does
  not appear in any cmdline).
- F7: RECORDED, no code change (per the redteam). Mid-test window
  noted in run_one's re-scan comment and in the plan's launch-gate
  bullet.
- F8: FIXED. Double-nested -c removed from the residual list (the
  leaf is caught live, probe-verified); the other declined items
  stand as recorded.
- Council 2 AMEND: FIXED (docstring: sync claim corrected, comma
  import residual recorded, extensionless/.pyc qualified). The
  comma-list fix itself is NOT implemented (would need import-list
  tracking for a sub-variant of an already unusual launch form);
  recorded as a residual per Council 2's own ask.
- Council 3 R1-R4: FIXED (find path clone1-batch3, t09 detail/prefs
  md5s verified by me against git blobs at 1d23532, run_batch3.py
  md5 line corrected to the log's fix-pass-2 entry, round-trip
  count corrected to about 3.5 effective with both counts noted).
- Council 1 GO: no fix; ship condition (live run re-measures and
  honors the watch item) written into the plan's H4 note.

## Fix-pass-2 verification (21:47-21:52 +07, all on the VM)

- py_compile OK; import OK, 10 tests (b3-t01..b3-t10).
- Fix2 probe /tmp/y14b-fix2-probe.py: 31/31 PASS, exit 0 (joined
  -m x3, dotted -m x2, -W/-X x4, -c residuals x4, codex positions
  x10, live double-nested leaf caught). First run 30/31: my probe
  expectation was wrong, not the code (the double-nested WRAPPER
  cmdline is not matchable at unit level; the leaf IS caught live,
  which is the F8 correction); probe corrected, second run 31/31.
- M1 all-12 probe /tmp/y14b-fix2-m1-probe.py: 4/4 PASS, exit 0
  (all matching accepted; foreign t01 mixed server refused;
  foreign t09 detail.html refused; missing prefs.html refused).
- Regressions, all green: H2 probe /tmp/y14b-h2-probe.py 45/45
  PASS (incl. M2 INFRA in 1 ms); transcription
  /tmp/y14b-transcribe.py 82 PASS lines, 0 failures; gate dry run
  /tmp/y14b-gate-dry.py 4/4 PASS; old M1 probe
  /tmp/y14b-m1-probe.py 3/3 PASS (updated to complete 12-file
  roots; the first run failed only because the old probe's root
  held just the t10 fixture, which the new check rightly refuses).
- No em/en dash in the fix diff (grep 0), no ydotool, no personal
  info.
- Fix commit: ad085d9 (todolist-push, pushed, ls-remote verified
  ad085d9ef809e8c37f7a2edfd218c40f5a3f41f7). run_batch3.py at this
  commit: git blob e604c01229933194d40a4a3f75c54a8b13a46f78, md5
  5d52ac65e8fe1d666d26c7f3ece4d7ba (ship-time expected values for
  the plan's md5 procedure; supersedes the fix-pass-1 values).
- Redteam re-review over the fix-pass-2 diff: spawned after this
  commit. Ship waits for it unless it BLOCKs.

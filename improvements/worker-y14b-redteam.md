# Redteam: Y14b re-stage review (commit f732d6a, todolist-push)

Scope: the re-stage diff ONLY (f732d6a vs 70061e2, runner + plan + log).
Suite HEAD: 1d23532. Reviewer: redteam, independent, no subagents.
No live Zen driving in this task. All probes run on the VM.

## Verdict: BLOCK

The diff must not ship to the laptop as the slot safety control yet.
Three independent reasons, each reproduced below:

1. The new H2 gate misses five ordinary ways to execute a runner
   (H1, HIGH). The single-runner invariant the whole live run depends
   on rests on a filename matcher, and `python3 -m run_batch3` alone
   defeats it. Council 2 (b445257) independently found the -m hole and
   voted AMEND; this review proves the hole is structural, not one
   form, with five live bypasses, and adds two false-passes in the new
   t10 checks plus a miscalibrated bound. That breadth is why this
   verdict escalates to BLOCK.
2. The new t10 checks contain two confirmed false-passes (H2, H3):
   a wrap that stops the timer passes everything, and a late position
   jump passes the unbounded later read. The plan claims "the live run
   is the real test" for these escapes; the live runner inherits the
   identical gap, so the live run cannot test them either.
3. The absolute 2..11 bounds were copied verbatim from check.mjs but
   the runner's transport makes the elapsed time systematically longer
   (H4, MEDIUM): the correct fixture false-fails the middle bound at
   75 ms per Marionette round trip, with zero margin at 50 ms.

Unblock conditions (all small, all re-probable on the VM except the
laptop timing measurement):

- (a) Hold a flock lock file for the whole run as the primary mutual
  exclusion, and cover the -m, -c, renamed-copy, .pyc, and spoofed
  argv[0] forms in the tokenizer. Re-run probe_h2_live.py and
  probe_h2_unit.py: 0 bypasses.
- (b) Add a post-wrap advancing check (read, sleep 350, read,
  gain >= 2) after the playing wrap, and an upper bound on the two
  later advancing reads, or explicitly scope both paths as untested
  and correct the plan claim that the live run covers them.
- (c) Re-derive the 2..11 caps from measured Marionette timing on the
  laptop (dry-run the t10 segment, set caps with at least 3 ticks of
  margin), or move the now-playing assert out of the
  sampler-to-advancing path and re-measure.
- (d) Verify the served root by md5 in the gate (see M1) and update
  plan L413 from ed78e83 to 1d23532 (see M4).

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 21:13: task start. Read f732d6a (3 files), check.mjs at 1d23532,
  fixture.html at 1d23532, run_live.py driver, launch_y13.py scan.
- 21:14-21:16: diff scope. Function-body diff old vs new runner:
  only run_b3_t10, run_preflight, launch_gate changed; 6 new H2
  helpers added; t01-t09 bodies byte-identical. Suite diff
  ed78e83..1d23532 touches only t10 check.mjs + README among suite
  files, so the t01-t09 byte-identical claim holds.
- 21:17: H2 unit probe (29 cmdlines against the real
  _is_runner_cmdline): 12 mismatches.
- 21:18-21:20: H2 live /proc probe (real _scan_other_runners, 12
  live dummy processes): 5 bypasses confirmed, 1 false-positive
  confirmed, 3 wrapper forms cleared (child process caught).
  Cleanup: all dummies terminated by PID, verified none remain.
  (One probe run died on an unexecutable shebang test file; the 4
  orphaned sleepers were killed by PID and verified gone before the
  re-run. A pkill -f matching my own shell command string killed
  one exec session; cleanup after that used PID lists only.)
- 21:20: t10 virtual-clock simulator (mutant matrix, RTT sweep,
  tick-phase sweep) + calibration against prior live-run step logs
  (click steps median about 56 ms for about 3 POSTs, eval median
  about 2 ms).
- 21:20-21:21: independent transcription audit (my own extractor,
  not the re-stage script): order, counts, sleeps, bounds all match
  check.mjs. Foreign-root reuse repro with a live foreign server on
  port 8771: start_server() served FOREIGN bytes while the gate root
  held different bytes.
- 21:22-21:25: this paper, commit, push, ls-remote verify.

## Method and probe artifacts

Probes were written for this review and run on the VM. They live in
/tmp/rt (ephemeral) and are summarized here with outputs:

- probe_h2_unit.py: 29 cmdlines vs the real _is_runner_cmdline.
- probe_h2_live.py: 12 live dummy processes vs the real
  _scan_other_runners. Dummy runner is /tmp/rt/run_foo.py
  (sleep 60); renamed copy /tmp/rt/zzz.py; shebang copy
  /tmp/rt/drive.py.
- probe_t10_sim.py: virtual-clock reimplementation of fixture.html
  timer/nextTrack semantics plus the runner's assert sequence, with
  a per-round-trip overhead parameter and clock-rate mutants.
- probe_transcribe.py: independent ordered extraction of position
  asserts and sleeps from check.mjs and run_b3_t10.

## H1 (HIGH): H2 scan misses five live ways to execute a runner

Code: _is_runner_cmdline, tests/realistic/run_batch3.py L2220-2260.
It keys on the script token basename matching run_*.py (or
run-nested, hand_drive_e1.py). The runner's identity is its code,
not its filename, so any launch that does not present a run_*.py
token is invisible to launch_gate and to the preflight re-check.
A second runner launched any of these ways drives Zen alongside
the first, and both gates pass.

Live /proc reproduction (probe_h2_live.py, real _scan_other_runners):

- BYPASS-CONFIRMED `python3 -m run_foo` (cmdline
  `python3 -m run_foo`): not flagged. Same for the real runner:
  `python3 -m run_batch3` executes main() (the `__main__` guard
  fires under -m) and is a normal module invocation.
- BYPASS-CONFIRMED `python3 -c "import run_foo"`: not flagged.
  Unit level: `python3 -c "import run_batch3; run_batch3.main()"`
  also returns False.
- BYPASS-CONFIRMED renamed copy `python3 /tmp/rt/zzz.py`: not
  flagged. A copy of the runner under any non-run_ name escapes.
- BYPASS-CONFIRMED shebang renamed copy `/tmp/rt/drive.py`
  (kernel runs `python3 /tmp/rt/drive.py`): not flagged.
- BYPASS-CONFIRMED spoofed argv[0]
  (`exec -a innocuous python3 run_foo.py`, cmdline
  `innocuous run_foo.py`): not flagged.
- Unit level only (same tokenizer path): `python3 run_batch3.pyc`
  and extensionless `python3 run_batch3` both return False.

Cleared by the same live probe (not bypasses): bash -c with a
trailing `; echo done` (child python caught), nested-quote
`bash -c "bash -c 'python3 ...'"` (bash execs through to python,
child caught), double-wrapped flock (outer flock process itself
and its child both flagged). The -c tokenizer's quote fragility
only hides wrappers, never the python child, so it is not a
bypass on its own. Also cleared: env -i, /usr/bin/env python3,
python3.12 full path, nohup/setsid, flock -c, python -u, shebang
argv[0] run_batch3.py, and mention-only cmdlines (md5sum/cat/vim
of a runner path: not flagged).

Why this is structural, not one hole: the matcher can only see
filenames. Any future launch shape that does not spell run_*.py
in argv escapes by construction. The plan itself notes
"run_live.py enforces no flock/zen_dom.lock; the queue is
coordinated by Muse", so there is no second line of defence.

Fix (concrete):

- Primary: take and hold an exclusive flock lock file for the
  whole run (e.g. /tmp/y14-live.lock, or a zen_dom.lock) in
  launch_gate, held until main() exits. A second runner of ANY
  launch shape then fails to take the lock. This also closes the
  gate-to-preflight window and the container case for the local
  filesystem (see M2).
- Secondary: extend _is_runner_cmdline to cover the proved forms:
  a `-m run_batch3` / `-m run_live` / `-m run_agyq2` module token
  following a python token; a `-c` string that names run_batch3
  or run_live as a module; a script token whose file, when read,
  imports run_live/run_agyq2 and defines the runner (cheap
  content check on the script path); and refuse on a .pyc or
  extensionless script whose basename starts with run_.
- Re-probe with probe_h2_live.py + probe_h2_unit.py after the fix:
  0 bypasses, mention-only still unflagged.

## H2 (HIGH): playing wrap that stops the timer passes everything

Code: run_b3_t10 playing wrap, run_batch3.py L1730-1760 (exact-zero
+ sampler only, no advancing check). check.mjs has the same gap:
no advancing check follows the playing wrap. This is the Y15
R1/R2/R3b escape, documented in the checker README and landed over
the redteam BLOCK per a pre-set stopping rule. The re-stage
faithfully translated it, so the gap is inherited, but the plan's
claim that "the live run is the real test" for these escapes is
false: the live runner has the identical gap, so the live run
cannot test this defect either.

Reproduction (probe_t10_sim.py, virtual clock, RTT 30 ms):

- Mutant: nextTrack on the wrap branch resets position to 0 and
  then stops the timer (playing flag untouched).
- Runner checks on the wrap path: exact-zero reads 0 (ok), sampler
  min over 500 ms is 0 (ok, min <= 2 and min < pos_before), then
  NO advancing check follows. Result: ALL PASS.
- The next step (playlist click on Mountain Air) restarts the
  timer via playTrack, so the stopped timer is masked for the rest
  of the test. The correct fixture also passes, so the two are
  indistinguishable to this runner.

Control: the reset-to-1 mutant is caught by exact-zero on both
playing and frozen paths (reads 1, fails). The wrap gap is
specific to liveness after the wrap, not to the reset value.

Fix (concrete): add a post-wrap advancing check mirroring the
playing Next: read position at sampler end, sleep 350, read again
(gain >= 2, with an absolute bound re-derived per H4), sleep 350,
read again (gain >= 2). If the check is deliberately not added,
correct the plan: scope the playing wrap as reset-only tested,
liveness untested, and delete the "live run is the real test"
claim for R1/R2/R3b.

## H3 (MEDIUM): later advancing reads have no upper bound, late jump passes

Code: run_batch3.py L1595-1599 (playing) and L1726-1730
(shuffle): `advancing_later - advancing >= 2` with no absolute
bound, by design per the checker comment ("correct value near 12").
The frozen resume later reads DO have the 2..11 bound, so only
the two playing later reads are exposed.

Reproduction (probe_t10_sim.py, RTT 30 ms):

- Mutant: after the middle advancing read, position jumps +20 in
  one tick (timer interval halves, or a position jump).
- Runner checks: exact-zero 0 (ok), sampler min 0 (ok), middle
  gain 6->10 (ok), middle 2..11 (ok), later gain 10->34 (ok, no
  bound). Result: ALL PASS. A clock that accelerates late, or a
  position jump, is invisible on both playing paths.

Control: a 2x clock from the start IS caught by the middle bound
(advancing reads 20, fails 2..11). The hole is only for defects
that start after the middle read.

Fix (concrete): add an upper bound on the later read calibrated
to elapsed time (correct value near 12-14 at runner timing; a
bound such as <= 17 keeps at least 3 ticks of margin and still
catches a +20 jump), or assert the per-window gain is at most 5
ticks per 350 ms sleep. Apply to both playing later reads.

## H4 (MEDIUM): 2..11 bounds miscalibrated for the runner's transport, correct fixture false-fails

Code: run_b3_t10 middle reads, run_batch3.py L1589 and L1722
(`2 <= advancing <= 11`), and the frozen resume second reads
(2..11). The bounds were copied verbatim from check.mjs, whose
timing is Playwright with about 10 ms round trips: reset to the
middle read takes about 850 ms plus small overhead, so the
correct value is near 8, with 3 ticks of margin to the 11 cap.
The runner's path to the same read is longer: sampler eval flight
+ 500 ms sampler + now-playing assert (find + text, 2 round
trips) + afterSampler read (1 round trip) + 350 ms sleep +
advancing read (1 round trip), i.e. about 850 ms + 5 round trips.
The plan's Council 2 A5 note ("START the sampler promise BEFORE
the now-playing assert") describes check.mjs concurrency, not the
runner: sample_position_min() blocks for 500 ms and the
now-playing assert runs AFTER it, so the assert's 2 round trips
sit between the sampler end and the afterSampler read.

Reproduction (probe_t10_sim.py, correct fixture, tick-phase
sweep 0/50/99 ms, boundary stable across phases):

- RTT 0 ms: advancing 8, pass. RTT 10 ms: 9, pass.
  RTT 25 ms: 9, pass. RTT 50 ms: 11, pass with ZERO margin.
  RTT 75 ms: 12, FAIL. RTT 100 ms: 13, FAIL. RTT 150 ms: 16, FAIL.
- Frozen resume second read: RTT 100 ms reads 11 (zero margin),
  RTT 150 ms reads 13, FAIL.

Calibration against prior live runs on the laptop (same driver
stack): live-run-y11b-proof-20261121.jsonl eval steps median
about 2 ms; click steps (scroll + find + click, about 3 POSTs)
median about 56 ms, p90 about 59 ms, so a single Marionette round
trip is roughly 5-20 ms on a quiet machine. At that rate the
runner passes with about 2 ticks of margin, thinner than the
checker's 3. Under load (busy Zen, geckodriver contention) round
trips past 50 ms erase the margin and the correct fixture fails
t10, which would be misread as a fixture failure and could burn
the slot. The 0.6x slow clock still passes (documented checker
limit, reproduced: advancing 3->6, all pass), so the bound is
simultaneously too tight at the top for the transport and too
loose at the bottom for slow clocks; only the top is a re-stage
translation defect.

Fix (concrete): re-derive the caps from the runner's own timing.
Dry-run the t10 segment on the laptop, record the actual
reset-to-advancing elapsed time, and set the middle cap with at
least 3 ticks of margin above the measured correct value (or move
the now-playing assert to after the advancing-later read, which
removes 2 round trips from the critical path, then re-measure).
Do not ship a t10 whose correct-fixture margin is 0-2 ticks.

## M1 (MEDIUM): gate verifies the on-disk suite root, but start_server() can serve a different root

Code: launch_gate L2379-2386 checks
LIVE_SERVER_ROOT/clone1-batch3/t01-terminal/fixture.html on disk.
run_live.py start_server() L909-925 reuses any listening server on
the port if /clone1/t01-upload-single/fixture.html returns 200.
That probe URL is a DIFFERENT suite's fixture, and the reuse path
never compares served bytes to the disk root. The plan itself
(L431-436) requires "probe a Y14 fixture, fail closed on
foreign-root reuse"; the re-stage diff implements no such probe.

Reproduction (VM, live): a foreign http.server on port 8771 rooted
at /tmp/rt/foreign (holding FOREIGN bytes for both the probe path
and the batch3 t01 fixture) plus LIVE_SERVER_ROOT=/tmp/rt/y14
(holding REAL-Y14 bytes). start_server() printed "reusing live
server at http://127.0.0.1:8771", returned httpd None, and served
FOREIGN-T10 bytes for the batch3 fixture, while the gate's disk
check would have passed on /tmp/rt/y14. The served bytes are
unverified by the gate.

Impact today is bounded (fixture.html is byte-identical between
ed78e83 and 1d23532, so a stale Y14 root would serve identical
bytes), but the mechanism means a stale or tampered fixture would
be served while the gate claims the suite is verified, and the
re-stage's whole point is serving exactly 1d23532.

Fix (concrete): after start_server() returns in main(), fetch
base_url + /clone1-batch3/t10-music-player/fixture.html and
compare its md5 to the on-disk file under LIVE_SERVER_ROOT;
refuse (exit 2) on mismatch or on fetch failure. Also change the
reuse probe in run_live.py to a batch3 fixture path.

## M2 (MEDIUM): no re-scan after preflight; scan is same-pid-namespace only

Code: run_preflight L1918-1934 re-checks once, before any tab
opens. run_one never re-scans. main() order is launch_gate,
metrics setup, start_server, WD session creation (geckodriver
spawn, seconds), then the preflight re-check. A second runner
starting in that window is caught only by ITS OWN gate scan (it
sees the first runner), so the window is closed for documented
launches and open exactly when H1 applies. After preflight passes,
a bypass-launched second runner starting mid-suite is never
detected by the running runner. _scan_other_runners lists /proc
only: a runner in a container (separate pid namespace, host
networking, driving Marionette 2828) is invisible, and a runner
as another user is visible only if /proc is not mounted hidepid
(default on most distros, unverified on the laptop).

Fix (concrete): re-scan at the top of run_one (cheap, one /proc
pass per test) and, primarily, hold the flock lock from H1 for
the run duration, which is namespace-independent on the shared
filesystem. Record the laptop's /proc hidepid state in the ship
notes.

## M3 (LOW): codex false-positive, substring match on the whole flat cmdline

Code: _scan_other_runners L2311-2316 flags any process whose
flat cmdline contains "codex" (anywhere) plus any marker
(hand_drive_e1, geckodriver, .config/zen, zen-bin, .mozilla,
remote-debugging, marionette).

Live reproduction: a sleep process with argv[0] "codex marionette
notes" was flagged as a codex executor driving a browser.
Realistic trigger: a codex CLI whose prompt or args mention
"marionette" (for example working on browser-automation code),
or a path containing both words (editing a file under a codex
directory about marionette, or grep -rn marionette over such a
directory). The gate would then refuse a legitimate launch.
Inherited from Y13f (identical markers in run_codex_y5.py and
launch_y13.py), copied verbatim by the re-stage, so it is not a
new defect, but the re-stage brief asked for false-positives and
this is the one that fires.

Fix (concrete): anchor "codex" to the executable token
(argv[0] basename is codex, or a token exactly "codex" / "codex"
with flags) instead of a substring of the whole cmdline, and
require the marker to appear in a different token than the codex
token. Note: launch_y13.py warns on plain codex processes; this
copy drops even the warning branch, so a plain codex process in
the slot is silently ignored. Restore the warning.

## M4 (LOW): plan L413 still says the suite is copied from ed78e83

The operative ship instruction in improvements/
worker-y14-batch3-live-plan.md L413 reads "suite copied from main
ed78e83, md5-verified", contradicting the re-stage claim (1d23532).
Other ed78e83 mentions (L32, L467, L493, L497, L507, L652) are
history or dated notes; L413 is the one a shipper follows.
Impact is nil today (fixture.html byte-identical between the two
commits, and the runner never executes check.mjs), but the
"re-staged from 1d23532" claim is unverifiable from the diff:
no md5 list, no SHIPPED.md entry, no manifest for batch3 exists
(SHIPPED.md covers Y9 only), and tests/realistic/clone1-batch3/
does not exist on the todolist-push branch at all (verified by
ls-tree on HEAD), so a ship must copy the suite from main with no
recorded hashes.

Fix (concrete): update L413 to 1d23532, record the fixture md5s
for all 10 fixtures in the re-stage log, and add a batch3 entry
to SHIPPED.md (or a batch3 manifest file) at ship time.

## L1 (LOW): int() truncation in position() and exact_zero_next()

Code: run_b3_t10 L1471-1476 and L1508-1530: int(d.eval("return
Number(...)")). int() truncates a float, so a position of 0.9
would read as 0 and false-pass exact-zero. Inert for this fixture:
position is always an integer (`position += 1`,
`dataset.seconds = String(position)` in fixture.html), and the
sampler's Number() path has the same property. Fix: compare the
raw Number to 0 without int(), or assert the value is integral
before truncating.

## L2 (LOW): ancestry exclusion can hide a runner that is an ancestor's child

_scan_other_runners excludes the whole ancestor chain, which is
correct for the launching shell's -c string, but it also excludes
a real runner if the gate process is ever a DESCENDANT of one
(for example a watchdog or retry child spawned by a runner that
then calls the gate). No such child exists in this runner
(run_one spawns no subprocesses), so this is latent only. Fix:
exclude only the direct launching shell (parent), or exclude
ancestors only when their cmdline matches via the -c string form,
not when they are themselves a runner process.

## What the re-stage got right (verified, not assumed)

- t10 translation fidelity (independent re-extraction with my own
  script, not the re-stage script): order, counts, sleeps and
  bounds all match check.mjs at 1d23532. 6 exact-zero sites
  (3 same-task via exact_zero_next, 3 frozen), 3 sampler sites,
  sleeps 0.35x10 / 0.7x3 / 0.5x1 / 0.4x1, 8x 2..11 bounds,
  7x gain>=2 checks, 0 D1 probe remnants, 0 ed78e83 references in
  the runner.
- t01-t09 function bodies byte-identical between 70061e2 and
  f732d6a; t01-t09 check.mjs byte-identical between ed78e83 and
  1d23532 (only t10 check.mjs + README changed among suite files).
- H2 helpers byte-identical to the Y13f source in run_codex_y5.py
  except the _is_runner_cmdline docstring tail (admitted in the
  log); CODEX_REFUSE_MARKERS identical across run_batch3.py,
  run_codex_y5.py and launch_y13.py.
- D1 probe removal follows the plan's own note (the probe was
  details-only, never a check; the new frozen steps cover the same
  defect class at 3 sites). Not a hole.
- exact-zero same-task soundness: verified against fixture.html.
  Page JS is single-threaded, the next-btn handler runs
  synchronously inside the eval task, position is an integer, and
  the frozen paths use real Marionette clicks in both the checker
  and the runner. The el.click() vs pointer-click distinction is
  inert for this fixture (only 'click' listeners). The reset-to-1
  mutant is caught by exact-zero on both playing and frozen paths
  (simulator).
- Sampler Promise form (open question in the plan): fail-closed.
  sample_position_min raises on a non-numeric result, and a step
  failure aborts the test as FAIL, never as a pass. Whether
  Marionette awaits the returned Promise is still unverified live,
  but a failure there can only produce FAIL or INFRA, never a
  false pass. No change needed on this point.
- r.check continuation is safe: failures only append, never
  removed; summary pass requires zero failures; step failures
  raise and abort the test. No healing path. run_one retries only
  INFRA-marked summaries, so a real fixture failure is not
  retried into a pass.
- Preflight re-check placement is correct: first lines of
  run_preflight, before any tab opens; a hit raises PREFLIGHT FAIL
  and blocks t01.

## Inherited observations (not re-stage findings, noted once)

- The vol==50 assert after clicking #volume is vacuous (the
  fixture default IS 50), but the volume/seek/search blocks are
  carried over verbatim from the old t10, so this predates the
  re-stage.
- The codex false-positive rule and the no-lock coordination note
  are inherited from Y13f / the plan; H1 and M3 address the parts
  this diff owns (the copied matcher, the missing lock).
- The 0.6x slow-clock pass is a documented checker limit
  (README), reproduced in the simulator, not a re-stage defect.

## Ship conditions (restated)

Do not ship until (a) the flock lock + tokenizer coverage lands
and the H2 probes re-run with 0 bypasses, (b) the post-wrap
advancing check and the later-read upper bound land or the plan
claim is corrected, (c) the 2..11 caps are re-derived from laptop
timing with at least 3 ticks of margin, and (d) the served-root
md5 check and the L413 update land. Then re-run the council and
redteam over the fix commit, not over this verdict.

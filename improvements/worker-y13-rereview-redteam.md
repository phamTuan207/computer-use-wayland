# Redteam re-review: Worker Y13 live runner (run_codex_y5.py, commit 7923877)

Target: tests/realistic/run_codex_y5.py (commit 7923877), tests/realistic/codex-y5-manifest.json,
tests/realistic/codex-y5/SHIPPED.md, improvements/worker-y13-codex-y5-live-plan.md (v2).
Sources read, not trusted from memory: the runner (all 3946 lines), the manifest, SHIPPED.md,
the v2 plan, improvements/worker-y13-redteam.md (the plan redteam; this paper is the RUNNER),
tests/realistic/run_agy_y2.py (Y9, HEAD incl. 7e7996d), run_live.py at 1e3901c (extracted to
/tmp/run_live_1e3901c.py), tests/realistic/codex-y5/check.mjs, simulate.mjs, all 10 specs,
all 10 fixtures (test-10 read in full; others spot-checked against the drivers).

Method: read the code as an attacker. Every finding cites file + line + the exact sequence.
Line numbers are for the 7923877 bytes unless stated otherwise. What could be proved
mechanically on the VM was proved (py_compile, AST counts of the drivers, a simulation of
the real _audit_count on a fabricated perfect-run JSONL, a transcription diff of _VERIFY_JS
against check.mjs, --verify-manifest on a staged ship dir in /tmp with positive and negative
cases, grep traces of every switch/new_tab/close_tab/DELETE). No Zen was driven, nothing on
the laptop was touched, nothing was committed, nothing in the runner was modified.
No em dash or en dash is used in this report. No personal info is included.

TREE MOVED DURING THIS REVIEW. The assignment was commit 7923877 (HEAD at session start,
runner md5 f570134d, 3946 lines; verified again from git show 7923877, same md5). While this
review was running, a parallel Council B re-review landed commit eb0a89f (19:52 +07, "fix
Council B BLOCK (F1 audit +1 leak, F2 step counts 02:48/07:52, F3 reload swap INFRA)"), and
HEAD moved to 0540c0a; the runner file was edited further, uncommitted, at least twice after
that (md5 cd2b900f, then 45bc1d5c, then 3c4dc698 within minutes). Findings below are stated
against the assigned 7923877 bytes, with a FIXED / SURVIVES note each, verified against the
eb0a89f diff and, for H1, by re-running the audit simulation on the fixed bytes. The later
uncommitted edits were not reviewed; the parent should re-run the mechanical gates on
whatever bytes actually ship.

## Verdict: BLOCK

Against 7923877: BLOCK. Three HIGH findings (H1 audit, H2 manifest, H6 reload swap) each
independently block a valid live run, plus H5 (queue). Against the current tree: H1 and H6
are fixed by eb0a89f (verified, see below), but H2, H3, H4, H5 survive, so the verdict is
still BLOCK, now on H2/H3/H4/H5. Fix those, regenerate the manifest, and re-run the
mechanical gates on the exact bytes that will ship before any live driving.

Counts against 7923877: 6 HIGH, 7 MEDIUM, 3 LOW. A further 10 items were checked and found
clean; they are listed at the end, not counted as attacks.

## HIGH

### H1. The step-count audit can never pass: the JSONL count is always the memory count + 1, and STEP_COUNTS is wrong for tests 02 and 07

Severity: HIGH. Effect: no test can ever report PASS. A live run would report 0/10 with a
"step-count audit" failure on every test, wasting the live slot.

Mechanism, in three parts, all in tests/realistic/run_codex_y5.py.

Part A: the open_fixture body check is counted by the JSONL audit but not by the memory
counter. Y13Runner.check (line 594) increments spec_step_count only when
self.audit_enabled is True, but it calls log_step with op "check" unconditionally.
open_fixture (line 1093) sets r.audit_enabled = False at its start and True only at its
successful return, and in between it calls r.check("body renders visible (no hidden-body
incident)", d.visible("body"), "visible") at line 1165. That record is written to the JSONL
with test == tid, attempt == current attempt, op == "check". _audit_count (lines 3084-3100)
counts every JSONL record with test == tid, attempt == attempt, op in AUDIT_OPS, and
AUDIT_OPS (line 3081) contains "check". So for any test that reaches the audit,
jsonl_n = mem_n + 1 exactly. The audit block in main (line 3780 onward) requires
jsonl_n == STEP_COUNTS[tid] AND mem_n == STEP_COUNTS[tid]. One number cannot equal both
mem_n and mem_n + 1. The audit is unsatisfiable by construction.

Part B: STEP_COUNTS is wrong for two tests. AST count of r.step + r.check calls inside each
driver (counted mechanically, not by eye):

- run_01: 86, table 86, match
- run_02: 48, table 47, MISMATCH (the table is short by 1)
- run_03: 63, table 63, match
- run_04: 58, table 58, match
- run_05: 59, table 59, match
- run_06: 76, table 76, match
- run_07: 52, table 51, MISMATCH (the table is short by 1)
- run_08: 57, table 57, match
- run_09: 58, table 58, match
- run_10: 69, table 69, match

The two misses are exactly the "text"-op read steps: run_02 step 11 ("11 read first playlist
track", op "text") and run_07 step 20 ("20 read forward modal heading", op "text"). The table
author evidently counted primitives excluding those two reads, but both the memory counter
(Y13Runner.step increments for every r.step call whatever the op) and the JSONL audit
("text" is in AUDIT_OPS) count them. So for test 02 a perfect run gives mem_n = 48,
jsonl_n = 49, want 47; for test 07 mem_n = 52, jsonl_n = 53, want 51. Both fail twice over.

Part C: proof with the real function. I imported the runner module on the VM, fabricated the
JSONL of a PERFECT test-02 run (48 driver primitives + the 1 body check, all attempt 1), and
called the real _audit_count. Result: audit_count(02, a1) = 49, STEP_COUNTS[02] = 47,
mem_n = 48, audit condition False. Same for test-01 (86 driver primitives + 1 body check):
audit_count(01, a1) = 87, STEP_COUNTS[01] = 86, mem_n = 86, audit condition False.
Commands and outputs are in the evidence appendix.

Note the failure mode is fail-closed in the wrong direction: it does not manufacture a false
PASS, it manufactures a false FAIL on every test. The audit was introduced by redteam M4 to
catch omitted steps; as shipped it catches every test including a perfect one. Spec step
coverage itself is fine (every spec step 2..N has at least one primitive in each driver,
verified by AST; see checked item C3), so the audit's intent is sound and only its arithmetic
is broken.

Fix: (1) STEP_COUNTS["02"] = 48, STEP_COUNTS["07"] = 52 (AST-verified). (2) Exclude the
open_fixture body check from the audit count: log it with an op outside AUDIT_OPS (for
example "harness-check") or filter it out in _audit_count. (3) Gate: re-run the AST count
and the _audit_count simulation for all 10 tests (synthetic perfect-run JSONL per test) and
require mem_n == jsonl_n == STEP_COUNTS for each before any live driving. Do not fix this by
loosening the audit to "at least" or by dropping the JSONL leg; the two-leg agreement is the
point of the check.

STATUS: FIXED by eb0a89f, verified. The diff adds _AUDIT_EXCLUDED_STEPS (the body-check
step name) and filters it in _audit_count, and sets STEP_COUNTS 02 to 48 and 07 to 52.
Re-ran the audit simulation on the fixed bytes (same fabricated perfect-run JSONL per test):
run_01 mem 86 jsonl 86, run_02 mem 48 jsonl 48, run_07 mem 52 jsonl 52, all matching the
fixed table, audit condition True for all three. The AST counts on the fixed bytes also match
the fixed table for all 10 tests. H1 is closed on the current tree; it remains in this paper
because it was a BLOCK against the assigned 7923877 bytes.

### H2. The committed manifest lists a stale md5 for the runner itself: --verify-manifest exits 2 on the committed ship

Severity: HIGH. Effect: the runner refuses to launch from its own committed bytes, before
any driving. main() runs _verify_manifest FIRST and returns 2 on any mismatch.

Evidence (commands and outputs in the appendix):

- md5sum of the committed runner: tests/realistic/run_codex_y5.py = f570134da519903e5da333194ee2970f.
  git show HEAD:tests/realistic/run_codex_y5.py gives the same md5, and git status shows the
  file unmodified. The manifest lists run_codex_y5.py as 9a7c6ace1d0ad9aa7a4fb6972cc39e80.
- `python3 tests/realistic/run_codex_y5.py --verify-manifest` on the repo copy exits 2:
  {"manifest_ok": false, "files_checked": 26, "mismatches": ["run_codex_y5.py: want
  9a7c6ace1d0ad9aa7a4fb6972cc39e80, got f570134da519903e5da333194ee2970f", "run_live.py: want
  84fa106c253d5e7f16daccf2ce3f14a5, got d8e2b14d7456b2866790f4a87ec1919e"],
  "manifest_md5": "3606fe843abe3d0db2da5ef1a8bd4f71"}.
- Staged ship in /tmp (runner from the repo, run_live.py from 1e3901c, all 24 other files from
  the repo, as-committed manifest): --verify-manifest exits 2 with only the runner mismatch,
  "run_codex_y5.py: want 9a7c6ace1d0ad9aa7a4fb6972cc39e80, got f570134da519903e5da333194ee2970f".
  The run_live.py entry passes there, which proves the runner entry is the sole staleness:
  the manifest was generated from an earlier version of the runner and never regenerated
  after the runner's final edit (both files landed in the single commit 7923877).

The run_live.py mismatch on the repo copy is NOT a defect: the repo file is HEAD (md5
d8e2b14d, Y11 metrics wiring) while the manifest pins the frozen 1e3901c bytes (84fa106c);
the ship dir is supposed to carry the 1e3901c file. Only the runner entry is stale.

Fix: regenerate the manifest from the actual shipped bytes (runner md5 f570134d...), update
SHIPPED.md (runner line + manifest md5), and gate on --verify-manifest exit 0 on a staged
ship dir built exactly as the laptop ship will be built (runner from the repo, run_live.py
from 1e3901c). Add a standing check that the committed manifest matches the committed files
(except the pinned run_live.py) so this class of staleness is caught at commit time, not at
launch time on the laptop.

STATUS: SURVIVES. eb0a89f did not touch the manifest (its stat lists only the runner, the
Council B paper, and the log). The manifest still lists the runner as 9a7c6ace..., while the
runner bytes have since changed twice more (uncommitted edits in the shared checkout; last
observed working-tree md5 3c4dc698...). So the gap is now larger than the one proved above,
and any manifest regenerated now must be regenerated from the FINAL bytes, after all edits
stop. Do not regenerate it against a moving target.

### H6. In 7923877 the reload ladder can swap the fixture away and the swap is misread as a live failure; r.step also swallows the INFRA prefix

Severity: HIGH against 7923877. Effect: a hidden body after a test-10 reload is reported as
a live step failure (no re-run, infra_blocked reset), and any INFRA raised inside an r.step
lambda misses main's only INFRA match.

Mechanism (7923877 bytes): _reload_settings (lines 2800-2843) calls
`ok, _swapped = ensure_visible(d, r, "reloaded settings page")` at line 2820 and IGNORES
the swapped flag. If the body is hidden after the reload, the ladder may rebootstrap to a
fresh about:blank tab (VISIBLE, but with no fixture and no sessionStorage) and return
(True, True). _reload_settings then runs wait_for on #extension-persistence-status on that
blank tab, which times out after 10 s with "timeout waiting for ...". main's classify (line
3671) matches INFRA ONLY by `msg.startswith("INFRA:")`, and separately excludes
"timeout waiting for" from the INFRA timeout branch, so the outcome is "failed", a live
failure, for a genuine hidden-body incident. The fixture tab is abandoned (r.tab now points
at the blank tab; the next test recovers by loading its fixture there, but test-10 is
already misclassified).

The same startswith-only match loses INFRA raises from inside r.step lambdas: r.step wraps
exceptions as "step failed: <name>: RuntimeError: INFRA: ...", which does not start with
"INFRA:". The only INFRA-raising call reachable inside a step lambda is ensure_visible via
_reload_settings (its "INFRA: tz-hidden removal eval failed" raise). In 7923877 that raise
falls through to the diagnose branch, which may or may not self-heal depending on what the
diagnose sees at that moment.

STATUS: FIXED by eb0a89f, verified by diff. The fix adds the swap check (if swapped, raise
RuntimeError("INFRA: hidden-body after settings reload; ladder swapped to a fresh tab,
fixture not loaded") before wait_for) and widens main's match to
`msg.startswith("INFRA:") or ": INFRA:" in msg` with an explanatory comment. H6 is closed
on the current tree; it is recorded here because it was a BLOCK against the assigned
7923877 bytes, and because an earlier draft of this paper briefly misread the fixed bytes
as the assigned bytes on this point. The lesson is recorded in the tree-moved note above:
line citations must be pinned to a commit, not to a moving checkout.

### H3. Test-10 step 26 reload is unprovable: wait_for passes on stale pre-reload text, so a failed reload click reports PASS

Severity: HIGH (false PASS on a spec step; the suite-level verdict for test-10 can be PASS
with step 26 never executed). Effect: if the step-26 reload click fails for a non-navigation
reason, the test still passes end to end.

Mechanism: _reload_settings (lines 2800-2843) proves a reload happened by waiting up to 10 s
for #extension-persistence-status to read 'State restored after reload'. That text is set
by the fixture's render() from the `restored` flag, which is true iff sessionStorage holds
the settings key at script load (tests/realistic/codex-y5/fixtures/test-10-extension-settings.html,
script block: stored = sessionStorage.getItem(storageKey); if (stored) restored = true;
render sets the text to 'State restored after reload' when restored, else 'Not reloaded').

At step 21 the proof is sound: before step 21 the text is 'Not reloaded' (step 19 saved
options, which writes sessionStorage but does not set `restored`, so render still shows
'Not reloaded'), so wait_for passing proves a reload happened.

At step 26 the proof is vacuous: after step 21's reload, `restored` is true and stays true
through step 24 (reset defaults calls save(), which rewrites sessionStorage; render keeps
showing 'State restored after reload'). Before the step-26 click the text is ALREADY
'State restored after reload'. Sequence for a broken step 26: d.click raises (element not
interactable, stale element, any non-navigation reason); raised is set; wait_ready passes;
ensure_visible passes (body visible); wait_for returns True on the FIRST eval because the
stale pre-reload text already matches; _reload_settings returns "reloaded (click raised,
tolerance)". Steps 27 checks then pass on the pre-reload DOM (which already holds the default
values from step 24), and final_verify passes. The step-26 reload action is never verified,
and _reload_settings cannot fail via wait_for at step 26 at all: the only remaining failure
mode there is a hidden body.

Note the headless harness shares the blind spot: simulate.mjs lines 214-215 and 218-219 use
the same waitForFunction on the same text for both reloads. So "simulate 10/10" does not
prove the second reload was exercised either. The defect is in the oracle, not only in the
live port.

Fix: prove the reload with a marker that only a new document clears. Before the click, eval
`window.__y13_reload_probe = 1`; after wait_ready + settle, assert
`window.__y13_reload_probe === undefined` (a reload creates a new JS realm, so the marker
is gone; without a reload it persists). Keep the persistence-text wait as a secondary check.
Apply to both step 21 and step 26. Do not "fix" this by weakening the tolerance; the click
tolerance itself (navigation-related raise counts as success-then-wait) is sound at step 21
and stays.

### H4. diagnose_body conflates "no body element" with "eval transport failure", so a hung driver mid-test is reported as fixture-unavailable, not INFRA

Severity: HIGH (misclassification; it also defeats the two-consecutive-INFRA abort, because
a hung driver never increments infra_blocked).

Mechanism: run_live.py at 1e3901c, diagnose_body (lines 173-245): if the first _DIAG_JS eval
raises (URLError timed out, HTTP error, dead session), it returns {"classification":
"FIXTURE_FAILURE", "snapshots": [], "eval_error": "..."}; a non-dict sample returns the same
label. _classify_snapshot (lines 138-171) also returns FIXTURE_FAILURE when the snapshot has
no body. Two distinct causes share one label, and the eval_error that distinguishes them is
discarded by every caller.

Trace for a hung driver mid-test: a step's WD call hangs past the 30 s HTTP timeout; r.step
wraps it as "step failed: ...: URLError: <urlopen error timed out>"; main's exception handler
calls diagnose_body(d); the diagnose eval ALSO times out (the driver is still hung), so
diagnose returns FIXTURE_FAILURE with eval_error "URLError: ... timed out"; main's classify
(line 3704, the FIXTURE_FAILURE branch) takes that branch and sets outcome =
"fixture-unavailable", suite continues, no infra count, no re-run. The correct outcome is
infra-blocked (the driver hung). The same conflation bites at load time: _ensure_visible_inner
raises FIXTURE-UNAVAILABLE immediately on any FIXTURE_FAILURE diagnose (lines 797, 810, 857:
initial diagnose, poll loop, post-removal), so a transient eval error during open_fixture's
ladder becomes fixture-unavailable instead of INFRA.

Related masking in the same family: wait_for (base, lines 491-500) catches every eval
exception and retries, then raises "timeout waiting for ..."; main's classify explicitly
excludes "timeout waiting for" from the INFRA timeout branch, so a WD hang inside wait_for
(the only wait_for call site is _reload_settings, line 2835) is a live failure. wait_ready
(base, lines 480-489) likewise raises "page did not reach readyState complete" with no
timeout wording when the driver hangs, so a hang inside wait_ready is also not recognised
as a timeout. All three mask the same underlying event (the driver hung) behind a label
that is not INFRA.

Fix: split the label. Have diagnose_body return a distinct classification for eval transport
failure (for example DIAG_TRANSPORT, or keep FIXTURE_FAILURE but add "transport_error": true
and make callers read it). In main's classify, when cls == "FIXTURE_FAILURE", inspect
diag.get("eval_error") for timeout/URLError/ConnectionError/HTTP and reclassify to INFRA;
only a diagnose that positively proves "document loaded, no body element" (snapshots
present, hasBody false, readyState complete) stays fixture-unavailable. Apply the same
split in _ensure_visible_inner (do not raise FIXTURE-UNAVAILABLE on a transport error; retry
or raise INFRA). And make wait_for/wait_ready record the last underlying eval error in the
raised message so the classify step can see it (or have them raise a distinct timeout type).

### H5. The queue is enforced procedurally, not in code: nothing in the runner stops a launch into Y6c's nested run, an E1 executor between arms, or Y11b

Severity: HIGH. Effect: a second live runner can start undetected mid-suite (or Y13 can
start into a live predecessor), and the two drivers then share Marionette 2828 and the
visible tab.

What CODE actually gates a launch (preflight, lines 3227-3458): (a) the handover token,
(b) BiDi 9222 + Marionette 2828 reachable, (c) Hyprland IPC, (d) the fixture server probe,
(e) predecessor PORTS free by TCP connect, Y9 8769/4449 and Y8b 8767/4451 only (lines
3300-3310), (f) a stale-geckodriver sweep by /tmp/geckodriver-*.pid files with a parent
check, (g) the zen_dom.lock flock held by an ancestor of this process. That is all.

What is missing, verified by grep (no pgrep, no process listing, no run_*.py name check
anywhere in run_codex_y5.py):

- No runner-quiet process check. The plan v2 (C3 S3) claims a "runner-quiet process check
  BEFORE flock (no run_*.py process other than self, no hand_drive_e1.py, no Codex executor
  process driving a browser, no live geckodriver with a live parent)". That check exists
  only in the Y6b v2 launcher script (improvements/worker-y6b-run-nested-wayland-v2.sh,
  the U8 block: pgrep -af "run_agyq2[.]py|run_live[.]py|run_agyq[.]py|run_agy_y2[.]py|
  run_fcck[.]py", pgrep -x geckodriver, pgrep -x mpv/foot). It is not in the Y13 runner,
  not in its preflight, and not in any file the runner executes. Even that pattern would
  miss run_codex_y5.py itself, hand_drive_e1.py, and any Y11b/Y14 runner name.
- Y11b ports are unknown (the plan says so) and are not checked; the PID sweep is the only
  backstop, and it only sees geckodrivers that wrote a /tmp/geckodriver-*.pid file via
  run_live.WD. A Y11b proof runner that does not use that WD (or that writes its PID file
  elsewhere) is invisible.
- Y6c nested uses no TCP ports (plan, C3 S3 and RT L3) and writes no /tmp/geckodriver-*.pid
  file the sweep would see (the nested run drives a nested Wayland session, not the live
  Zen's geckodriver). The only in-code gates that could catch it are the flock and the
  handover token, and neither is held by Y6c (the flock is not uniformly held across runners;
  the Y6b redteam already proved only run_agyq2.py enforces it). So a Y13 launch during
  Y6c's nested run passes every in-code check and starts driving the live Zen while the
  nest tiles over the screen.
- E1 between arms: E1's geckodriver (4451) is checked, but only while it is up. Between arms
  the driver is down while the Codex executor still holds the slot; no port answers, no PID
  file is necessarily present, and the runner has no process check to see the executor.
- Y13's own ports (8771/4452) are never checked as "must be free of a live predecessor".
  A second Y13 instance is stopped only if it is launched under flock (the second flock
  -w 60 blocks, then fails) or if its preflight finds no lock holder. A launch that skips
  flock fails preflight, but a launch under a DIFFERENT lock file also fails preflight only
  because the real lock has no holder; the runner never verifies that the lock it sees is
  exclusively held against other runners, only that an ancestor holds it.

The flock is therefore the single load-bearing mechanism, and it works only if every
launcher in the fleet uses it, which the Y6b redteam already showed is false. The Y6c
completion marker and Muse's go order are likewise launcher-side (git + procedure), not
checked anywhere in run_codex_y5.py.

Fix: put the runner-quiet check INTO preflight in code, before the lock check: pgrep for
run_*.py processes other than self (include run_codex_y5.py, run_agy_y2.py, run_agyq2.py,
run_live.py, hand_drive_e1.py, and any Y11b/Y14 runner name once known), pgrep -x
geckodriver, and a check that Y13's own ports 8771/4452 are not already serving a live
predecessor (a second Y13). Add the Y6c completion-marker verification to the launcher as
a named, reviewable script (git fetch + the exact marker match from plan v2 C3 S2), and
record its output in the launch log; do not rely on an unwritten poll. Until that lands,
the queue gate is a procedure, and the run must not start on the basis of "preflight
passed" alone.

## MEDIUM

### M1. The manifest trusts any self-consistent ship: a stale ship passes, and planted extra files pass

Severity: MEDIUM. Effect: the manifest check cannot distinguish the committed ship from any
other self-consistent set of bytes, and it never refuses unexpected files in the ship dir.

Evidence (staged ship in /tmp, commands in the appendix):

- CONTROL: I regenerated the manifest from the staged files (runner md5 corrected to the
  actual f570134d...). --verify-manifest exits 0 with manifest_md5 2c2befa9740f1f9044f54ff0287cb4db,
  a DIFFERENT manifest md5 from the committed 3606fe84.... The runner accepted a ship whose
  manifest md5 it had never seen. The manifest md5 is recorded in the suite JSON but never
  compared against a pinned value in code, so a stale-but-self-consistent ship (older runner
  + older manifest + older fixtures) passes every check.
- EXTRA FILES: with the corrected manifest, I planted live_metrics.py AND functools.py in
  the ship dir (neither is in the manifest). --verify-manifest exits 0, manifest_ok true.
  The check only verifies listed files; it never refuses unexpected ones. The functools.py
  instance is the sharp one: the runner does sys.path.insert(0, dirname(__file__)) and
  run_live.py at 1e3901c does `from functools import partial`, so a planted functools.py in
  the ship dir shadows the stdlib module for both files. The live_metrics.py instance is
  inert against the pinned 1e3901c base (it has zero live_metrics references, verified by
  grep), but it is live against a HEAD run_live.py, which is exactly the drift the manifest
  is supposed to catch.

Fix: (1) refuse unexpected files in the ship dir: allowlist = manifest paths + the manifest
itself + SHIPPED.md, refuse anything else (at minimum refuse live_metrics.py and any
top-level .py file not in the manifest). (2) Pin the expected manifest md5 in the runner
code (after H2 is fixed and the manifest is regenerated) so a stale self-consistent ship is
refused; the pin only helps if the runner bytes are themselves verified externally (git),
which is the right layering.

### M2. The wall cap resets per attempt: two attempts can total ~2x the spec cap and still pass, and total_ms hides the superseded attempt

Severity: MEDIUM. Effect: a test can consume up to ~720 s of live wall (two 360 s attempts)
against a 360 s spec cap and still report PASS with an elapsed_ms under the cap.

Mechanism: Runner.__init__ (base, lines 559-567) sets self.t0 = time.perf_counter() at
construction. main constructs a FRESH Y13Runner per attempt (r = Y13Runner(tid, base) at the
top of the attempt loop), so attempt 2 gets a fresh t0 and a fresh WALL_CAPS[tid] budget.
The cap check (line 3780 onward) measures (time.perf_counter() - r.t0) for the current
attempt only. A test that runs 350 s, fails INFRA, then re-runs 350 s and passes is reported
with elapsed_ms ~350 s and no cap trip. total_ms in the suite JSON sums final attempts only
(by design, plan C3 F1), so the 350 s superseded attempt is invisible in total_ms; only
suite_wall_ms covers it, and no per-test cumulative time is reported.

The cap placement itself is correct (t0 is set before wd.__enter__, so session creation is
included, and the cap is checked after the per-test finally, so screenshot + session exit
are included). The gap is only the per-attempt reset.

Fix: enforce a cumulative per-test cap across attempts (sum the elapsed of attempt 1 and
attempt 2, trip if the sum exceeds WALL_CAPS[tid]), and report per-test cumulative elapsed
in the suite JSON. At minimum, report the superseded attempt's elapsed next to the final
attempt's so the total is visible.

### M3. FIXTURE-UNAVAILABLE raised inside r.step is not matched: only the startswith check exists, so a transient reload-ladder fixture error can become a live failure

Severity: MEDIUM (low end). Effect: narrow misclassification on the test-10 reload path.

Mechanism: main's classify (line 3671 in 7923877) matches INFRA only by
`msg.startswith("INFRA:")`, and FIXTURE-UNAVAILABLE only by
`msg.startswith("FIXTURE-UNAVAILABLE")`. _reload_settings is called inside r.step
("21 reload settings" / "26 reload settings"), and it calls ensure_visible, which raises
"FIXTURE-UNAVAILABLE: ..." when a diagnose returns FIXTURE_FAILURE (initial diagnose, poll
loop, post-removal; lines 797, 810, 857). Wrapped, that reads "step failed: 21 reload
settings: RuntimeError: FIXTURE-UNAVAILABLE: ...", which fails the startswith check and
falls into the diagnose branch. Usually the diagnose branch self-heals (diagnose on the same
tab returns FIXTURE_FAILURE again, so the outcome is fixture-unavailable). But if the
failure was transient (a one-off eval error that clears by the time main diagnoses), main's
diagnose returns VISIBLE, the timeout check finds no timeout wording, and the outcome is
"failed", a live failure, for what was a fixture/diagnose event. Note the asymmetry with
H6: eb0a89f added the ": INFRA:" substring match for INFRA but did NOT add a
": FIXTURE-UNAVAILABLE" substring match, so this gap survives on the current tree.

Fix: match ": FIXTURE-UNAVAILABLE" as a substring in main, exactly like ": INFRA:".
Better still, match on the unwrapped cause rather than on string prefixes.

### M4. A test whose checks fail still reports outcome "pass" in its per-test JSON

Severity: MEDIUM (reporting only; the suite counts are correct). Effect: the per-test JSON
line lies, and any downstream consumer that reads "outcome" instead of "pass" will miscount.

Mechanism: outcome starts as "pass" (line 3648 in 7923877) and is changed only by exceptions (main, around line
3660). r.check failures do not raise; they append to r.failures. So a test that drives to
completion with failing checks has outcome == "pass" and r.failures non-empty. The audit
block is skipped (`if outcome == "pass" and not r.failures`), summary = r.summary() gives
pass = False, and summary["outcome"] is set to "pass". The suite counts use s["pass"], so
passed/flagged/total are right, but the JSON line for that test says {"pass": false,
"outcome": "pass"}. The same shape occurs for final_verify failures (they append to
r.failures without raising).

Fix: after TESTS[tid] returns, if r.failures is non-empty and outcome is still "pass", set
outcome = "failed" before building the summary.

### M5. infra_blocked is not reset by fixture-unavailable / guard outcomes, deviating from plan v2

Severity: MEDIUM (low end; fail-safe direction, but a plan-vs-code mismatch). Effect: the
run aborts earlier than the plan specifies.

Mechanism: plan v2 (C3 F1) says infra_blocked "resets on any pass and on any non-INFRA
failure". The code (lines 3768-3773 in 7923877) does `elif guard_defect or guard_inconclusive:
pass` and `elif outcome == "fixture-unavailable": pass`, i.e. it deliberately does NOT
reset the streak on those outcomes (the suite JSON comment calls this fail safe, consistent
with the guard-defect precedent). Trace: test N INFRA (infra_blocked = 1), test N+1
fixture-unavailable (streak stays 1), test N+2 INFRA (streak 2, abort). Under the plan the
streak would have reset at N+1 and N+2 would be 1, no abort.

Fix: reconcile, one way or the other. Either reset infra_blocked on fixture-unavailable /
guard outcomes as the plan says, or amend plan v2 to the code's fail-safe rule and record
why. Do not leave a plan and a runner that disagree about the abort rule.

### M6. The handover fingerprint is (asserted_at_unix, mtime_ns, size), not a content hash

Severity: MEDIUM (low end). Effect: a token rewritten mid-run with the same asserted_at,
the same size, and a restored mtime passes the fingerprint check.

Mechanism: _check_handover (lines 246-280) builds fp = (float(tok["asserted_at_unix"]),
st.st_mtime_ns, st.st_size) and refuses only when fp differs from the launch fingerprint.
The token CONTENT (basis, run id) is not part of the fingerprint. A normal rewrite changes
mtime_ns and is caught. But a rewrite that preserves mtime (os.utime) with identical
asserted_at and size is not caught. That rewrite cannot EXTEND the window (age is computed
from the same asserted_at_unix), so the practical damage is limited to swapping the basis /
run id mid-run, which is why this is LOW end of MEDIUM rather than HIGH. The rest of the
handover is sound: env var alone is never enough, future timestamps are refused (age < 0),
expiry mid-run aborts with exit 2, the check runs before every test, and a deleted token
fails closed.

Fix: fingerprint the token content (sha256 of the file bytes) instead of (asserted_at,
mtime, size). Cheap, and it closes the rewrite-with-preserved-mtime case entirely.

### M7. start_server failure escapes main as an uncaught traceback with no suite JSON

Severity: MEDIUM (low end). Effect: a stale server holding port 8771 turns the launch into
a crash, not a structured failure.

Mechanism: main calls `_, base = start_server()` (line 3523 in 7923877) with no try/except. Y13 start_server
(lines 3127-3155) probes its own fixture; if a stale server answers 200 it reuses it (then
_verify_served_files catches byte differences, which is correct), but if the probe 404s it
falls through to _rl_start_server, which raises OSError EADDRINUSE, which Y13 wraps as
RuntimeError("could not start or reuse a server on port ..."). That RuntimeError propagates
out of main uncaught: traceback on stdout, exit code 1, no suite JSON line. Compare
preflight failure, which prints a structured suite JSON with preflight_failed and returns 2.

Fix: wrap start_server (and _verify_served_files) in main with the same structured-failure
pattern as preflight (suite JSON with server_failed, return 2).

## LOW

### L1. The ": INFRA:" substring match is fragile

Severity: LOW. The ": INFRA:" substring match added by eb0a89f carries a comment (in the
fixed bytes, not in 7923877) claiming "The string 'INFRA:' only appears in deliberate infra
raises in this codebase, so the substring match cannot misclassify a live failure." That is true today (no fixture text and no Marionette message contains it),
but it is a convention, not a mechanism: any future step name, check detail, or fixture
string containing ": INFRA:" would silently reclassify a live failure as INFRA. Prefer
matching on the unwrapped exception (catch the INFRA raise before r.step wraps it, or carry
a marker attribute on the exception) rather than on a substring of a formatted message.

### L2. SHIPPED.md is not in the manifest and is never verified

Severity: LOW. SHIPPED.md is read by _read_shipped and embedded in the suite JSON; its md5
is not pinned anywhere the runner checks. A tampered SHIPPED.md changes the report, not the
run. Note the manifest md5 recorded in SHIPPED.md (3606fe84...) does match the file on disk,
and every SHIPPED.md file line matches the manifest exactly (26 lines, no diffs), so the
shipped record is internally consistent; it is just unverified by the runner. Fix with M1
(allowlist the ship dir; SHIPPED.md is on the allowlist).

### L3. The smoke-test tab is never driven and is only cleaned at suite end

Severity: LOW. The pre-suite smoke test (main, SMOKE OK at line 3572 in 7923877) opens a fixture tab,
adds it to _TEST_TABS, and leaves it; bootstrap then opens a second tab. The smoke tab is
a live test tab holding a fixture, never driven, returned to about:blank only by the
suite-end cleanup. Harmless, but if the suite aborts before the cleanup (handover abort
returns 2 after the cleanup block, so it does run; an uncaught exception in main would skip
it), the tab is left holding a fixture. No user tab is involved. No fix required beyond
noting it; if the cleanup is ever skipped, the leftover is a test tab, not a user tab.

## Checked and found clean

1. Verify transcription. _VERIFY_JS extracted from the runner (Python string, escapes
   resolved) is identical to check.mjs verifyTest line for line after stripping indentation
   (one leading blank line in the port only). Same selectors, same expected values, same
   messages, same trim semantics in text() and value(), top-level return present, testId via
   arguments[0]. The guard and the final verify therefore test the same thing headless and
   live do.
2. Y9 B1 fix, verbatim and working. The _manifest_entries helper differs from run_agy_y2.py
   only in two docstring words (diff run, see appendix). Negative cases on a staged ship dir
   all refuse with exit 2: duplicate test-07 / dropped test-08 (26 entries, 25 unique files)
   refuses with "duplicate manifest path: codex-y5/fixtures/test-07-chat-search.html"; a bare
   list manifest refuses with "manifest is not an object"; a path-escape entry refuses with
   "manifest path escapes ship dir"; 25 entries refuses with "manifest lists 25 files, want
   26"; a tampered fixture byte refuses with the exact md5 pair; a wrong md5 entry refuses
   with the exact pair. Control case (manifest corrected to the actual bytes) passes, exit 0.
3. Spec step coverage. AST count per driver: every spec step 2..N appears at least once
   (01: 33/33, 02: 21/21, 03: 28/28, 04: 26/26, 05: 25/25, 06: 35/35, 07: 22/22, 08: 20/20,
   09: 23/23, 10: 26/26). No spec step is silently undriven by name.
4. Test-06 step 13. The live driver clicks #btn-select-forest then types the playhead (the
   click is load-bearing), matching simulate.mjs line 137. Steps 17/22 are replace-only, as
   the plan states.
5. Test-10 step 21. The reload proof is sound there (text changes from 'Not reloaded'), and
   the navigation-tolerant click handling is correct: a click that raises after the navigation
   is success-then-wait only when the persistence text proves the reload landed. The
   ladder-swap case is handled ONLY in the eb0a89f bytes, not in 7923877: see H6. In 7923877
   the swap was ignored and misread as a live failure; eb0a89f adds the INFRA raise before
   wait_for and the ": INFRA:" match in main, verified by diff.
6. Tab harm. Every switch/new_tab/close_tab/DELETE in the runner and the inherited base WD
   targets a registered test handle (_TEST_TABS, bootstrap_tabs, r.tab) or a tab the same
   session opened (opened_tabs, new_tab handles). No handle scanning anywhere. The park
   fallback (lines 536-540) switches only to a registered test tab, and DELETE /session then
   closes that test tab, which is recoverable by rebootstrap, never a user tab. The
   screenshot fallback (the per-test finally block) switches to r.tab if present, else opens a
   fresh about:blank tab; if the switch fails it skips the screenshot instead of capturing
   an uncontrolled window. The suite-end cleanup (loop at line 3929) switches only to
   bootstrap_tabs | _TEST_TABS and gotos about:blank. When the park cannot park, __exit__
   drops the session reference so DELETE /session never runs on an uncontrolled window
   (lines 542-560). No user-tab close, navigate, type, or click path was found.
7. Wall cap placement. r.t0 is set in Runner.__init__ and the Y13Runner is constructed
   BEFORE wd.__enter__, so session creation is inside the cap; open_fixture runs inside
   TESTS[tid], so it is inside the cap; the cap is checked after the per-test finally, so
   screenshot + session exit are inside the cap too. Only the per-attempt reset (M2) is
   wrong.
8. Guard discipline. verify_test always returns a dict (eval raise gives eval_raised True,
   non-dict gives a failure dict, defaults are set). open_fixture raises IntegrityGuardError
   on a guard pass and GuardInconclusiveError on a guard eval raise, and main maps both to
   their own outcomes with no re-run and no effect on infra_blocked, and never proceeds to
   drive. The guard runs on the same tab the fixture was loaded on, after the ladder, and is
   re-executed on any re-run.
9. Manifest vs repo files. All 26 manifest md5s match the repo files except the two
   accounted for: run_live.py (HEAD bytes by design; the manifest pins 1e3901c) and
   run_codex_y5.py (the H2 staleness). SHIPPED.md's 26 file lines match the manifest exactly,
   and its manifest md5 (3606fe84...) matches the file on disk.
10. Frozen base. run_live.py at 1e3901c has zero occurrences of live_metrics and imports only
    stdlib (functools, http.server, json, os, socket, subprocess, sys, threading, time,
    urllib, pathlib, datetime). Its md5 is 84fa106c253d5e7f16daccf2ce3f14a5, matching the
    manifest and SHIPPED.md. The pin claim holds; the repo HEAD run_live.py (d8e2b14d) is a
    different file, which is why the pin matters.

## Fix list (in order)

- F1 (H1): STEP_COUNTS 02 to 48, 07 to 52; take the open_fixture body check out of the
  audit count (op outside AUDIT_OPS); gate on the AST count + _audit_count simulation for
  all 10 tests. DONE by eb0a89f (verified by re-running the simulation on the fixed bytes);
  still listed so the fix is on the record.
- F2 (H2): regenerate the manifest from the shipped bytes; update SHIPPED.md; gate on
  --verify-manifest exit 0 on a staged ship (runner from repo, run_live.py from 1e3901c).
  OPEN, and more urgent than at review time: the runner has been edited since, so regenerate
  only once the bytes are final.
- F3 (H5): add the runner-quiet process check and the own-ports check into preflight in
  code; name the Y6c marker check as a reviewable launcher script.
- F4 (H3): prove the reload with a JS-realm marker (window.__y13_reload_probe) at steps 21
  and 26; keep the persistence-text wait as secondary.
- F5 (H4): split diagnose FIXTURE_FAILURE into no-body vs transport error; reclassify
  transport errors as INFRA in main and in the ladder; surface the underlying error from
  wait_for / wait_ready instead of masking it.
- F6 (M1): refuse unexpected files in the ship dir; pin the expected manifest md5 in the
  runner after F2.
- F7 (M2): enforce a cumulative per-test wall cap across attempts; report per-test
  cumulative elapsed.
- F8 (M3): match ": FIXTURE-UNAVAILABLE" as a substring in main, like ": INFRA:".
- F9 (M4, M5): set outcome "failed" when r.failures is non-empty with no exception;
  reconcile the infra_blocked reset rule with plan v2.
- F10 (M6): fingerprint the handover token content (sha256 of the bytes).
- F11 (M7): wrap start_server in main with the structured-failure pattern (suite JSON,
  return 2).
- F12 (H6): the reload-swap INFRA raise and the ": INFRA:" substring match. DONE by eb0a89f
  (verified by diff); still listed so the fix is on the record.

Re-verify after the fixes with the same mechanical gates used here (AST counts, audit
simulation, transcription diff, --verify-manifest positive + negative cases on a staged
ship), plus a fresh re-review of the changed lines only. No live driving until then.
Re-verify on the EXACT bytes that will ship: the manifest must be regenerated last, after
every runner edit, and --verify-manifest must exit 0 on a staged ship built from those
exact bytes. The moving checkout during this review is itself a process finding: freeze the
runner before regenerating the manifest, and do not regenerate against a moving target.

## Evidence appendix (commands + outputs)

Repo state at review time:

```
$ git log --oneline -1; git rev-parse HEAD
7923877 Y13: run_codex_y5.py live runner + manifest (26 files) + SHIPPED.md; ports 8771/4452, base 1e3901c, Y9WD park, txt() verifies, wall caps, step-count audit
7923877d7d028ccafd6c51a7b6da092ac0335dbc
$ python3 -m py_compile tests/realistic/run_codex_y5.py && echo COMPILE-OK
COMPILE-OK
```

AST primitive counts per driver vs STEP_COUNTS (script: ast.parse, count Call nodes
r.step / r.check per run_NN function):

```
run_01: step=27 check=59 total=86 STEP_COUNTS=86 match=True
run_02: step=13 check=35 total=48 STEP_COUNTS=47 match=False
run_03: step=18 check=45 total=63 STEP_COUNTS=63 match=True
run_04: step=15 check=43 total=58 STEP_COUNTS=58 match=True
run_05: step=16 check=43 total=59 STEP_COUNTS=59 match=True
run_06: step=26 check=50 total=76 STEP_COUNTS=76 match=True
run_07: step=15 check=37 total=52 STEP_COUNTS=51 match=False
run_08: step=11 check=46 total=57 STEP_COUNTS=57 match=True
run_09: step=15 check=43 total=58 STEP_COUNTS=58 match=True
run_10: step=17 check=52 total=69 STEP_COUNTS=69 match=True
```

Audit simulation with the real _audit_count (module imported, LIVE_LOG pointed at a
fabricated JSONL of a perfect run: driver primitives + the 1 open_fixture body check):

```
audit_count(02, a1) = 49  STEP_COUNTS[02] = 47
mem_n for a perfect run_02 = 48 (AST count). jsonl_n = 49
audit condition: jsonl_n == 47 and mem_n == 47 -> False
audit_count(01, a1) = 87  STEP_COUNTS[01] = 86  mem_n=86
audit condition for 01: False
```

Manifest staleness (7923877 bytes, extracted from git to /tmp/review-7923877 and checked
there, so the result is pinned to the assigned commit, not to the moving checkout):

```
$ md5sum tests/realistic/run_codex_y5.py
f570134da519903e5da333194ee2970f  tests/realistic/run_codex_y5.py
$ git show HEAD:tests/realistic/run_codex_y5.py | md5sum
f570134da519903e5da333194ee2970f  -
$ python3 tests/realistic/run_codex_y5.py --verify-manifest; echo "exit=$?"
{"manifest_ok": false, "files_checked": 26, "mismatches": ["run_codex_y5.py: want 9a7c6ace1d0ad9aa7a4fb6972cc39e80, got f570134da519903e5da333194ee2970f", "run_live.py: want 84fa106c253d5e7f16daccf2ce3f14a5, got d8e2b14d7456b2866790f4a87ec1919e"], "manifest_md5": "3606fe843abe3d0db2da5ef1a8bd4f71"}
exit=2
$ python3 /tmp/review-7923877/run_codex_y5.py --verify-manifest; echo "exit=$?"
{"manifest_ok": false, "files_checked": 26, "mismatches": ["run_codex_y5.py: want 9a7c6ace1d0ad9aa7a4fb6972cc39e80, got f570134da519903e5da333194ee2970f"], "manifest_md5": "3606fe843abe3d0db2da5ef1a8bd4f71"}
exit=2
```

Audit re-verification on the eb0a89f fixed bytes (same fabricated perfect-run JSONL method):

```
run_01: ast=86 table=86 match=True
run_02: ast=48 table=48 match=True
run_03: ast=63 table=63 match=True
run_04: ast=58 table=58 match=True
run_05: ast=59 table=59 match=True
run_06: ast=76 table=76 match=True
run_07: ast=52 table=52 match=True
run_08: ast=57 table=57 match=True
run_09: ast=58 table=58 match=True
run_10: ast=69 table=69 match=True
test 01: jsonl_n=86 mem_n=86 STEP=86 audit_pass=True
test 02: jsonl_n=48 mem_n=48 STEP=48 audit_pass=True
test 07: jsonl_n=52 mem_n=52 STEP=52 audit_pass=True
```

eb0a89f diff (the whole runner change; the manifest was not touched):

```
-    ok, _swapped = ensure_visible(d, r, "reloaded settings page")
+    ok, swapped = ensure_visible(d, r, "reloaded settings page")
+    if swapped: raise RuntimeError("INFRA: hidden-body after settings reload; ...")
-    "01": 86, "02": 47, "03": 63, "04": 58, "05": 59,
-    "06": 76, "07": 51, "08": 57, "09": 58, "10": 69,
+    "01": 86, "02": 48, "03": 63, "04": 58, "05": 59,
+    "06": 76, "07": 52, "08": 57, "09": 58, "10": 69,
+_AUDIT_EXCLUDED_STEPS = {"check: body renders visible (no hidden-body incident)"}
+    (filtered in _audit_count)
-                if msg.startswith("INFRA:"):
+                if msg.startswith("INFRA:") or ": INFRA:" in msg:
```

Staged ship (/tmp/stage-y13: runner from repo, run_live.py from 1e3901c, other 24 files
from repo, as-committed manifest):

```
$ python3 /tmp/stage-y13/run_codex_y5.py --verify-manifest; echo "exit=$?"
{"manifest_ok": false, "files_checked": 26, "mismatches": ["run_codex_y5.py: want 9a7c6ace1d0ad9aa7a4fb6972cc39e80, got f570134da519903e5da333194ee2970f"], "manifest_md5": "3606fe843abe3d0db2da5ef1a8bd4f71"}
exit=2
```

Manifest negative cases (each a copy of the staged ship; CONTROL uses a manifest corrected
to the actual runner md5):

```
CONTROL corrected-manifest: (0, '{"manifest_ok": true, "files_checked": 26, "mismatches": [], "manifest_md5": "2c2befa9740f1f9044f54ff0287cb4db"}')
B1 dup-07/drop-08 (26 entries, 25 unique): (2, '{"manifest_ok": false, "files_checked": 0, "mismatches": ["duplicate manifest path: codex-y5/fixtures/test-07-chat-search.html"], "manifest_md5": "3eb049f27d725425fc090921e97e4dec"}')
NOT-DICT manifest (bare list): (2, '{"manifest_ok": false, "files_checked": 0, "mismatches": ["manifest is not an object"], "manifest_md5": "c44d18efa7842ebe27304465b340328e"}')
PATH-ESCAPE: (2, '{"manifest_ok": false, "files_checked": 0, "mismatches": ["manifest path escapes ship dir: codex-y5/../../etc-hostname-evil"], "manifest_md5": "e12db66f675c5a5a0b795a9824684697"}')
COUNT-25: (2, '{"manifest_ok": false, "files_checked": 0, "mismatches": ["manifest lists 25 files, want 26"], "manifest_md5": "1bacad5b6e67fe906b33b52388897a1d"}')
TAMPERED-FIXTURE: (2, '{"manifest_ok": false, "files_checked": 26, "mismatches": ["codex-y5/fixtures/test-01-git-workflow.html: want ac0f3f5f6510bbd9c5ccf32e2b2f8301, got 68eb2efb00daa852465cb9145d680b98"], "manifest_md5": "2c2befa9740f1f9044f54ff0287cb4db"}')
BAD-MD5-ENTRY: (2, '{"manifest_ok": false, "files_checked": 26, "mismatches": ["codex-y5/fixtures/test-05-calendar-recurring.html: want 00000000000000000000000000000000, got caf9d8acd2440028b135d005ed42a4f2"], "manifest_md5": "e3622a0eea723fe3f3700ce8bd734d36"}')
EXTRA-FILES live_metrics.py + functools.py planted: (0, '{"manifest_ok": true, "files_checked": 26, "mismatches": [], "manifest_md5": "2c2befa9740f1f9044f54ff0287cb4db"}')
```

Verify transcription diff (_VERIFY_JS from the runner vs check.mjs verifyTest body,
whitespace-normalised per line, one leading blank line in the port only): identical,
123 lines each side, no content difference.

Manifest helper vs Y9 (diff of _manifest_entries between run_agy_y2.py and
run_codex_y5.py): identical except two docstring words ("redteam diff2 B1" vs "Y9 diff2
B1 fix, commit 7e7996d, adopted verbatim").

Base pin check:

```
$ git show 1e3901c:tests/realistic/run_live.py | md5sum
84fa106c253d5e7f16daccf2ce3f14a5  -
$ grep -c live_metrics /tmp/run_live_1e3901c.py
0
```

Spec step coverage (AST: leading number of each primitive name per driver vs 2..N):

```
run_01: covered 33/33 missing=[]  run_02: 21/21  run_03: 28/28  run_04: 26/26
run_05: 25/25  run_06: 35/35  run_07: 22/22  run_08: 20/20  run_09: 23/23
run_10: 26/26
```

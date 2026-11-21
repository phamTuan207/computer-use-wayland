# Y13r2 Council Voice 3 (gate/process): re-review of the Y13f fix diff

- Reviewer: Council Voice 3, 2026-11-21 ~22:05-22:20 +07
- Scope: fix diff cb26d1d..431b2a9, Y13f commits 118c67f + 3fa389a +
  431b2a9 (runner, launcher, regen script, plan, manifest, SHIPPED.md).
  Read the Y13r log and the Y13f fix log in full, then the diff itself.
- Method: fresh probes of my own in /tmp/y13r2-council-3/ (probe_f1.py,
  probe_f2.py, probe_main.py, probe_f9.py, probe_forge.py,
  probe_process.py, probe_h3.py). The re-reviewer's /tmp/y13r2/probe_*.py
  files were read for orientation only, not reused. Ship staged with
  the repo regen script into my own dir (never the real ship path):
  `regen_codex_y5_manifest.py --stage /tmp/y13r2-council-3/ship`,
  27 files, md5 f27c03020c9866cfa0dcd637df6f8647, staged verify exit 0.
  No code or runner file modified, no Zen driven, no commit, no
  checkout/reset/clean. The regen script rewrote the repo manifest
  identically (same md5); git status shows no tracked modification.

## Verdict: AMEND

Fix the two new findings below, regenerate the manifest LAST, re-run
the affected probes, then a fix-diff re-review only. Not BLOCK: both
findings fail closed, neither lets a live run pass incorrectly or a
tampered ship execute. Not GO: a broken verify path and an unguarded
real execution path must not ship into a live run.

## 1. Mechanical results: L3 / L4 / L6 / F9 (all reproduced)

Stub harness is real main() with only the driver/session, server,
preflight, bootstrap, handover and diagnose calls stubbed
(probe_main.py). What runs is the real code: main(), the real
Y13WD._park_before_exit, the real Y13Runner summary, the real
suite-JSON assembly, the real L3 cleanup gate and L4 branch.

- L3, 4/4 PASS. Handover fails at the first per-test check: rc 2;
  zero Y13WD instantiations after the abort event (event log: one
  WD_CREATED from the pre-abort smoke, then HANDOVER, then ABORT, no
  creation after); the "test tabs returned to about:blank" cleanup
  print is absent. The abort path drives nothing after the gate closes.
- L4, 2/2 PASS. Session creation raises in the attempt loop: exactly
  one session-creation-failure per-test JSON, carrying
  cumulative_elapsed_ms=0.1 (numeric, >= 0). Note: elapsed_ms in the
  same summary reads 0.0; that is a rounding artifact on a
  sub-millisecond stub interval (both values measure the same
  interval, rounded to 1 decimal at slightly different moments), not
  a defect. On a real failure (seconds) they agree.
- L6, 2/2 PASS. Stub test registers a keeper tab in _TEST_TABS and
  in d.opened_tabs, then fails: the suite JSON park_warnings holds
  exactly one entry, tab "keeper-0", detail "registered test tab in
  opened_tabs; removed before the close loop", and the keeper tab is
  removed from opened_tabs by the real park code. (Harness note: my
  first run failed L6 because the fake-class factory re-read
  mod.Y13WD after patching and captured a previous Fake subclass,
  recursing in _park_before_exit; fixed by capturing the real class
  once at load time. The code under test was never at fault.)
- F9, 8/8 PASS with the real _reload_settings and the real
  ensure_visible ladder (diagnose stubbed VISIBLE). typeof eval
  raising gives RuntimeError "reload settings: marker check failed
  (RuntimeError: transport boom); reload unproven", with and without
  a click raise. typeof returning None gives RuntimeError "reload
  settings: marker check inconclusive (typeof returned null); reload
  unproven", with and without a click raise. Marker surviving fails
  with and without a click raise. Marker gone plus click raised
  returns "reloaded (click raised, tolerance)". Marker gone, clean
  click returns "reloaded".
- Diff check: the L3 gate, L4 line, L6 key and F9 wrap are all in the
  Y13f diff (cb26d1d..431b2a9), not earlier code. Confirmed by grep
  on the diff.

## 2. Adjudication of the two substitutions

### (a) Y13r's forge script not run: substitution ADEQUATE

Y13f did not run Y13r's forge script file (a system execution-risk
flag fired on its tool-result delivery) and proved H1 with its own
fresh forge; the re-reviewer's Probe A is a second fresh
implementation and reproduces the gate; mine is a third
(probe_forge.py, 3/3: clean ship passes, forged run_live .pyc
refuses exit 2 with no marker in script form and in -m form).
Principle: the H1 attack is fully specified by its description in
the Y13r log (real run_live.py source plus a marker print, .pyc
header mtime/size forged from the source stat). The exact script
adds nothing beyond an implementation of that description, and
three independent implementations built from it agree on every
outcome. The gate is proven, not asserted. The exact script could
only add something if it used a different technique, and the log
names the technique. No need to run Y13r's exact file. Not running
flagged content delivered in a tool result and re-implementing from
the description was the correct response.

### (b) Transient flakes in Y13f's probes: TRANSIENT, not a race

Evidence: my live-process probe (probe_process.py) ran the real
launcher check_runner_quiet() against real dummy processes, 5
repetitions of an offender set (must refuse) and 5 of a negative
set (must pass), alternating: 10/10, no deviation, no flakes. The
re-reviewer's Probe C ran 10/10 twice with no flakes. Y13f's
re-runs passed 14/14 twice. Against that, the first-run 8/9 failure
is unattributed by Y13f's own account (the probe truncated the
refusal detail, offender unidentified) and Y13f's offline test of
the reconstructed Y14b cmdlines did not match the tokenizer, so it
cannot count as evidence of a runner defect. D8's rc=2 failures are
consistent with an earlier launcher check tripping under fleet
load (wrong refusal message, not a check_ports defect). No
counter-evidence of a race in the process check itself exists.
Residual: the first-run offender stays unidentified; the fix-diff
re-review should re-run the live process probe and, if any refusal
ever names an unexpected pid, capture the full detail before
killing (as my probe does).

## 3. H3 gate: it BLOCKS the Y13 live run as written

Verified with the real code and the real repo (probe_h3.py, 7/7).
The launcher's git log over the pathspec
improvements/worker-y6c-*.md on todolist-push returns exactly one
commit, 5a2b69d, subject "Y6c: nested v2 run BLOCKED at launch (F0
--socket/--wayland-fd, F1 hyprglass ABI dead, U5b wrong log); NO
VERDICT, probes + evidence". It matches neither MARKER_RE nor
ABORT_RE. Y6d 72eb8ad and Y6e 915121d fail ^Y6c in subject and touch
no worker-y6c-*.md file, so they never appear in that log at all.
The real check_marker() ran (fetch of origin/todolist-push worked)
and refused exit 2: "no Y6c completion marker on todolist-push".
The SHIPPED.md launch line carries --repo as required. Y13f did
NOT weaken the gate. Plain statement: the H3 gate as it stands
blocks the Y13 live run; Y13 cannot launch until Muse directs
otherwise.

Recommendation to Muse: accept option (b). Direct that the Y6c NO
VERDICT teardown record (5a2b69d, blocked at launch, evidence
committed) plus a fresh runner-quiet and ports verification
satisfies the marker leg for THIS run only; the gate text stays as
written; the Y6 retry, when decided, is sequenced AFTER Y13
completes. Reason: the gate protects against a concurrent nested
run, and no such run exists (Y6c ended at launch); the subject
pattern is a proxy that fails here only because Y6c ended without
a verdict. Do NOT accept option (a) as a general signal: Y6e
915121d is a risk review plus a nested load test, not a nested run
completion, and re-labeling it would assert nested work is done
while the retry is still undecided. Do NOT take option (c) as the
default: waiting for an undecided retry stalls the queue with no
date, and the retry needs the same slot Y13 is waiting for.

## 4. The two new findings: both CONFIRMED, both AMEND-level

### Finding 1: entry-.pyc exemption incomplete. CONFIRMED, stronger than stated.

_verify_manifest refuses the __pycache__ DIRECTORY itself (it is
not a prefix of any manifest path), while the exemption covers only
the two entry .pyc FILES. Fresh probes (probe_f1.py, 6/6):
- `python3 -m run_codex_y5 --verify-manifest` on a clean staged
  ship: rc 2, sole mismatch "unexpected directory in ship dir:
  __pycache__". Cache holds exactly run_codex_y5.cpython-312.pyc.
- Second -m run: still rc 2. After manual deletion, an -m run
  refuses AGAIN (each -m invocation re-creates the entry .pyc
  before module code runs, then refuses its own dir). The -m form
  can never verify, even once.
- Script form on a clean ship: rc 0, 27 files, no cache created.
  Script form after an -m run left a cache dir: rc 2 with the same
  dir mismatch. After manual deletion: rc 0. So a ship that once
  ran -m stays un-verifiable in EITHER form until manual deletion.
Production path unaffected (the launcher execs script form), and
the failure is fail-closed. AMEND, not BLOCK and not GO.

### Finding 2: tokenizer misses -m module forms. CONFIRMED in both copies.

_script_basename_is_runner requires a .py suffix, so the module
names "run_codex_y5" and "run_live" never match, and no -m branch
exists in _is_runner_cmdline. Fresh unit table (probe_f2.py):
`python3 -m run_codex_y5`, `python3 -m run_codex_y5 all`,
`python3 -m run_live`, `python3 -m run_live --help`, and absolute
python path -m forms all return False in BOTH the launcher and the
preflight copies (agreeing). Controls pass: script forms True, Y6c
bare True, path mention False, `-m http.server` False. Both are
real execution paths: `python3 -m run_codex_y5` runs the full suite
with no required args, and `python3 -m run_live` calls run_live
main(), which starts a server and drives WD sessions per test
(verified by reading the pinned run_live.py main). Live evidence
from my process probe: the `-m run_codex_y5` dummy was only
WARNING-classified as a plain "codex" process (its name contains
"codex") while the other dummies refused, so the gate sees the -m
process and lets it through. Note the docstring in run_codex_y5.py
falsely claims "-u/-m flags" are already covered. AMEND, not BLOCK:
the -m form is not the documented launch form of any fleet runner
(the launcher execs script form), the other gate legs (ports,
flock, geckodriver sweep) still hold, and the fix is small. Not GO:
a real execution path is unguarded.

## 5. AMEND list (exact fix + re-test per item)

A1. Finding 1. In _verify_manifest (run_codex_y5.py), exempt the
top-level __pycache__ directory when, and only when, every file
under it is in _ENTRY_PYC. Any other file under it, and any
__pycache__ at any other depth, still refuses. Do NOT delete the
cache at verify time (silent deletion would hide a tampered ship).
Re-test: probe_f1 cases must flip to rc 0 for the -m form on a
clean ship, -m form after manual deletion, and script form after
an -m run; the forge probes must still refuse (forged run_live
.pyc rc 2, no marker; a non-entry .pyc planted under __pycache__
rc 2).

A2. Finding 2. In _is_runner_cmdline in BOTH copies (launch_y13.py
and run_codex_y5.py, keep in sync), add a -m branch: when the
immediately preceding token is "-m" and a python token appears
earlier in argv, treat the next token as a runner module if it is
"hand_drive_e1" or starts with "run-nested" or starts with "run_".
This is safe against the path-mention false positive because -m is
unambiguous (the next token IS a module being executed). Correct
the docstring line in run_codex_y5.py claiming "-m flags" are
already covered. Re-test: the probe_f2 unit table (all 5 -m cases
True, controls unchanged, `-m http.server` still False, path
mention still False) plus the live process probe with -m dummies
included in the offender set (must refuse as offenders, not as
codex warnings), 3 repetitions, no flakes.

A3. Close-out. Regenerate the manifest LAST from the final bytes
with the regen script, re-stage the ship, run staged
--verify-manifest (must exit 0), record the new runner/launcher
md5s in SHIPPED.md, and re-run the affected mechanical set
(forge G1-G3, F1 cases, F2 unit table, live process probe 3 reps;
spot-check F9 and L3/L4/L6 unchanged). After that, a fix-diff
re-review of the A1/A2 diff only, not a full re-review.

A4. Conditional process item, not a code fix. Once Muse directs on
H3 (recommendation (b) above), record a dated note in SHIPPED.md
and the plan stating the 5a2b69d NO VERDICT record satisfies the
marker leg for this run only, with the Y6 retry sequenced after
Y13. Do not pre-write the direction and do not change the gate
text in code.

## Evidence index

- /tmp/y13r2-council-3/probe_f1.py: Finding 1, 6/6 confirmed.
- /tmp/y13r2-council-3/probe_f2.py: Finding 2, 5/5 -m cases missed
  in both copies, controls pass.
- /tmp/y13r2-council-3/probe_main.py: L3 4/4, L4 2/2, L6 2/2
  through real main().
- /tmp/y13r2-council-3/probe_f9.py: F9 8/8 through real
  _reload_settings.
- /tmp/y13r2-council-3/probe_forge.py: H1 gate, 3/3, own
  implementation.
- /tmp/y13r2-council-3/probe_process.py: live process probe,
  10/10 across 5 reps per set, no flakes, no leftover processes.
- /tmp/y13r2-council-3/probe_h3.py: H3 gate, 7/7, real
  check_marker() refuses exit 2.
- Ship: /tmp/y13r2-council-3/ship (regen --stage, 27 files, md5
  f27c03020c9866cfa0dcd637df6f8647).

# EVIDENCE CONTRACT CHECK: 20 MOST RECENT COMMITS ON TODOLIST-PUSH, 21/11/2026

Checked by Worker clone1 (batch 5 task 4), 2026-11-21. Branch
origin/todolist-push, tip beebe50 at check time. Every commit below
was read in full (message plus diff) and every checkable claim was
re-run or recomputed on this machine. A commit is COMPLIANT when
every "done" claim in it carries runnable evidence in the commit
itself (test command, output, commit hash, timed log, or a file
whose contents can be re-checked mechanically). PARTIAL means the
headline claim holds but some evidence is missing, laptop-only, or
a supporting number is wrong. MISSING means a central "done" claim
is false.

## Headline

- COMPLIANT: 13 of 20
- PARTIAL: 6 of 20
- MISSING: 1 of 20
- Commits that fall short: 695efea, b97d681, 0879700, 482e4ba,
  f31abcf, 556a592 (PARTIAL), 6f20fb5 (MISSING). Details per commit
  below.

## Compliance table

| # | Commit | Subject (short) | Verdict |
|---|--------|-----------------|---------|
| 1 | beebe50 | Y8 E1: log v2.1 md5s + pre-flight wait until 19:05:40 | COMPLIANT |
| 2 | 695efea | Y8 E1: design v2.1 re-freeze, diagnose JS return fix | PARTIAL |
| 3 | b97d681 | Y5: verifier fixed (2 harness bugs), re-verify 9/10, test-07 spec defect isolated | PARTIAL |
| 4 | ef12850 | Y9: log addendum 2, mapping done, re-review launched, slot is Y8b | COMPLIANT |
| 5 | 13b8144 | Y9: addendum, Y4d rerun done 10/10 (1e3901c), Y8 marker still absent | COMPLIANT |
| 6 | 0879700 | Y9: prep + ship log, slot poll shows Y8 marker absent, no live driving yet | PARTIAL |
| 7 | 1e3901c | Y4d: diagnose-first ladder + agy-q2 live rerun 10/10 | COMPLIANT |
| 8 | 4f4c890 | Y6: record final report commit hash 482e4ba | COMPLIANT |
| 9 | 482e4ba | Y6: FINAL hyprglass nested probe, headless dead at DRM master wall (8 crashes, 2 signatures) | PARTIAL |
| 10 | b913d7d | Y9: ship manifest with mechanically generated md5s | COMPLIANT |
| 11 | a82bb41 | Y9: amended agy-y2 live-run plan v2 + runner with all council/redteam fixes, step mapping | COMPLIANT |
| 12 | 4153371 | Y3: fcc verification of clone1-batch3 (7 PASS / 3 FAIL) + error-summary gap audit (82 FIXED / 31 OWNED / 0 UNOWNED of 113 IDs) | COMPLIANT |
| 13 | dce42ca | A1 pilot: record freeze commit f31abcf in FREEZE.md + pilot log | COMPLIANT |
| 14 | f31abcf | A1 pilot: frozen plan, runbook, schema, blinded checker, manifest + unblinding scripts | PARTIAL |
| 15 | 9cf6391 | Independent A1 checker review: FAIL, narrow, 3 diagnostic findings | COMPLIANT |
| 16 | 4a78f7f | Y8 E1: FINAL design v2 frozen, briefs + infra fixed per council/redteam, stop-script dry run 11/11 | COMPLIANT |
| 17 | 556a592 | Y5: fixture smoke 10/10 clean, Codex poll 2 | PARTIAL |
| 18 | 66e5e48 | Redteam: Y6 hyprglass probe, KILL broad verdict and design as written | COMPLIANT |
| 19 | e8fad29 | Y1b: probe redteam report logged, 10b/10f must be rewritten before Phase B | COMPLIANT |
| 20 | 6f20fb5 | docs: Y9 agy-y2 live-run plan, pre-registered thresholds, all Y4d council fixes applied | MISSING |

## Per-commit detail

### 1. beebe50, COMPLIANT

Claim: v2.1 files transferred to /tmp/e1, md5s match the repo
exactly; fresh pre-flight A runs after 19:05:40 +07.

Evidence checked by me: all four md5s recomputed from the files
as committed in 695efea and matched exactly:
preflight.py b8f234647ed4b2d580681b5ecad5fd3d, brief A
2741a1a1de8b34e9ca2371d725432438, brief B
7345f969d5de7516ca40a3505a204829, driver reference
4775a5710724bea3b64393be16522fdc. The wait-until time is a plan,
not a done claim. Laptop state in the same line (driver PID 256370,
HTTP 8767) is not verifiable from this machine; it is not counted
against the verdict.

### 2. 695efea, PARTIAL

Claims: (a) pre-flight A failed exit 2 with a diagnose eval
returning None; (b) root cause is the bare IIFE with no top-level
return; (c) mechanical fix prefixes `return ` in preflight.py,
both briefs, and the driver reference; (d) "the plan file is NOT
affected (all 21 of its evals start with `return`, step 56 is
`return window.__agyVerify()`)".

Evidence checked by me: (a) and (b) are in the execution log with
the exact error JSON (`{'ok': True, 'result': None, 'ms': 2}`),
exit 2, and the 1124 ms new-tab timing. (c) is in the diff: the
`return ` prefix is added in exactly the three places named, plus
the `return` rule in the driver reference eval line. (d) is WRONG.
The plan file improvements/worker-x-e1-plan-test-05.md at this
commit contains 19 eval command objects, not 21. Only 10 of the 19
start with `return`. Nine more contain a `return` later in the body
(fine under function-body semantics). None has no `return` at all.
CORRECTION (redteam, 21:15, verified by me from the plan at
695efea: 19 eval commands, 10 start with return, 9 contain it
later, 0 with none): the first version of this section wrongly
claimed 5 contain it later and 4 have none. The conclusion "the
plan file is NOT affected" is therefore stronger than first stated:
every eval in the plan returns a value, so the preflight exit 2
diagnosis cannot be blamed on the plan file at all. Step 56 IS
`return window.__agyVerify()`, that part is true.

Missing evidence: the fix itself was unproven live at commit time.
The design note is honest about this ("the fresh pre-flight
doubles as the one live eval the fixed diagnose helper must pass"),
but no passing pre-flight exists in this commit.

### 3. b97d681, PARTIAL

Claims: (a) harness bug 1 (test-06 click-before-set) fixed,
test-06 now passes; (b) harness bug 2 (test-10 jsdom opaque origin
plus save-before-render) fixed, test-10 now passes; (c) re-run
9/10 PASS with the exact command, log path, and JSON path;
(d) one real defect remains, test-07 spec error (spec steps 4-5
say "2 matching messages" but the fixture returns 3).

Evidence checked by me: (a) and (b) are specific diagnoses with a
mechanism stated (jsdom file:// URL has an opaque origin, so
sessionStorage.setItem throws SecurityError; the fixture's save()
runs before render()). The re-run command is given verbatim
(`node /tmp/y5-verify/verify.mjs --all /tmp/y5-stage --fresh`,
12 s, 9/10 with the passing list). BUT the command, the log
(/tmp/y5-verify/codex-y5-run-1856.log), and the JSON
(/tmp/y5-verify/codex-y5-result-1856.json) all live in /tmp on the
laptop, not in the repo. Not re-runnable from here. (d): the
fixture side verifies. On branch origin/y5-tests the test-07
fixture contains exactly 3 "Release checklist" messages (m1, m2,
m3) and 1 "Launch checklist" (m4). The spec side does NOT verify:
the committed spec on y5-tests already says "3 matching messages"
at steps 4-5 (steps 4 and 5 both say 3; step 11 says 2 after the
filter narrows it). The draft Y5 read at 18:56 is not committed
anywhere, so the "spec says 2" half cannot be confirmed from the
repo. The fix-pass is honestly stated as future work ("goes to
Codex in a short follow-up run"), not claimed done.

### 4. ef12850, COMPLIANT

Claims: step mapping delivered (670 lines, 343 numbered rows,
per-test totals 01:35, 02:35, 03:33, 04:33, 05:35, 06:35, 07:35,
08:35, 09:35, 10:32, plus one unnumbered required row in test-02),
0 dashes, file already committed in a82bb41; re-review launched
with 4 agents; slot belongs to Y8b.

Evidence checked by me: the mapping file as committed in a82bb41
has 670 lines by git diffstat, 343 numbered table rows counted by
me, per-test counts exactly 35, 35, 33, 33, 35, 35, 35, 35, 35, 32
as claimed, 0 em dashes, 0 en dashes, mismatches M1-M16 all
present, the unnumbered required row present. The file is in the
a82bb41 tree, confirming the handoff correction. The re-review
launch is a process claim recorded in the log; no verdict files
are claimed in this commit. The slot claim is laptop state, noted.

### 5. 13b8144, COMPLIANT

Claims: Y4d rerun done 10/10 in commit 1e3901c with evidence in
the rerun log and run report; Y8 marker still absent on re-check
at 18:55.

Evidence checked by me: the 1e3901c evidence is verified under
commit 7 below. The Y8 marker claim verifies: the Y8 execution log
as of this commit ends with "Conditions A and B execution:
UNMEASURED (prep phase, Y4d owns the slot)" (read at 13b8144),
with no completion commit and no "E1 EXECUTION COMPLETE" line.

### 6. 0879700, PARTIAL

Claims: prep + ship complete, no live driving yet; slot poll at
18:53 shows the Y8 marker absent on all three legs; ship md5s
verified on the laptop; laptop syntax + import OK.

Evidence checked by me: the slot poll is consistent with the repo
state at the time (no Y8 completion commit after 4a78f7f, the Y8
log ended UNMEASURED, no Y4d marker since 1e3901c came later).
The run_agy_y2.py md5 (1defa4ebf184c7e52df9604e75cd7f4b) matches
the manifest and the a82bb41 file, verified by me. The gap: the
shipped run_live.py came from a dirty working tree, and its md5
(84fa106c253d5e7f16daccf2ce3f14a5) cannot be reproduced from any
commit. The manifest honestly labels it "working tree (dirty)",
and the log honestly records it as such, but the shipped file
itself is not recoverable from the repo. Laptop syntax/import
claims are laptop-only.

### 7. 1e3901c, COMPLIANT

Claims: diagnose-first ladder implemented with council + redteam
fixes; live rerun run 1 8/10 (2 checker bugs), run 2 10/10 clean,
0 flagged, 0 hidden-body encounters, total 49,885 ms; tracked item
for the Transparent Zen defect included.

Evidence checked by me: the run report
tests/realistic/RUN-REPORT-AGYQ2-20261121.md is in the commit.
Per-test ms sum to exactly 49,885 for run 2
(5599+5067+5012+4775+4828+4834+4787+5142+4942+4899) and exactly
49,741 for run 1 as claimed. Both checker fixes are present in the
committed runner: q02 uses `"4 tbsp olive oil" in norm(ing).lower()`
(line 676) and q06 uses `norm(txt(d, "#badge-...")) == "Downloaded"`
(lines 971-977). The tracked-item file
improvements/transparent-zen-defect-tracked-item.md exists in the
commit (status OPEN, decision owed). Raw logs
(/tmp/worker-y4-run-1.log, /tmp/worker-y4-run-2.log,
/tmp/worker-y4-live-2.jsonl) are on the laptop, not in the repo;
the live run itself needs the owner's Zen and cannot be re-run
from here. The report is internally consistent and its load-bearing
code claims check out.

### 8. 4f4c890, COMPLIANT

Claim: record the final report commit hash 482e4ba. One-line
change, verified: 482e4ba exists and is the Y6 final report commit.

### 9. 482e4ba, PARTIAL

Claims: headless nested Hyprland dead, 8 launches, 8 SIGABRT
crashes, 2 signatures, one wall (live session holds DRM master);
Wayland-nested design fixed, files created and verified, not run.

Evidence checked by me: the attempt table in the report is
specific and internally consistent (8 attempts with times, PIDs,
coredump timestamps 18:20:16, 18:22:00, 18:22:35, 18:23:03,
18:40:37, 18:42:05, 18:43:30, signatures A initServer /
CBackend::create() and B enterLoop / initFB). The report
incorporates the redteam corrections from 66e5e48 (attempt 4
duplicates attempt 1, attempt 3 has the extra logind.c:309 line,
seatd socket mode/PID dropped for lack of surviving record).
Missing: raw crash evidence (coredumpctl output, crash report
files in ~/.cache/hyprland/) and the Wayland-nested design files
(/tmp/y6-nested/run-nested-wayland.sh and friends, listed with
byte sizes and bash -n / py_compile OK) all live on the laptop
only. Not re-verifiable from this machine. The report is honest
about what was not run.

### 10. b913d7d, COMPLIANT

Claim: ship manifest with mechanically generated md5s.

Evidence checked by me: all 25 committed-file md5s in SHIPPED-y9.md
recomputed from the cited commits and matched exactly, including
run_agy_y2.py (1defa4ebf184c7e52df9604e75cd7f4b at a82bb41) and all
10 fixtures, specs, simulate.mjs, and check.mjs at 30a72e5. The
one remaining file, run_live.py, is honestly labeled "working tree
(dirty)" and is the only md5 that cannot be reproduced from the
repo (see commit 6).

### 11. a82bb41, COMPLIANT

Claims: plan v2 corrects the false "fixes already applied" claim;
every fix is now in code in tests/realistic/run_agy_y2.py; ported
verify is a 1:1 transcription of check.mjs verifyTest (87
assertions + selectors verified identical by mechanical diff);
step mapping with 16 mismatches M1-M16; re-review gate still open;
no live driving in this commit.

Evidence checked by me: the runner is 2517 lines, committed. The
port diff: all 88 check() assertion lines in check.mjs are
byte-identical in the runner (the claim says 87; my count is 88,
off by one, substance holds). All 79 #id selectors in check.mjs
are present in the runner (the claim says 80; my count is 79, off
by one, substance holds). The 4 verdict files are present with the
stated verdicts (Council 1 BLOCK, Council 2 APPROVE WITH FIXES,
Council 3 BLOCK, Redteam BLOCK); their line counts are 92, 90, 98,
133, while the commit message says 91, 89, 97, 132 (off by one
each, counting method). The step mapping is verified under commit
4. The "re-review gate still open" and "no live driving" statements
are honest limits, not overclaims.

### 12. 4153371, COMPLIANT

Claims: fcc unusable tonight (upstream free provider saturated);
Y3 verified clone1-batch3 directly, 7 PASS / 3 FAIL; gap audit
82 FIXED / 31 OWNED / 0 UNOWNED of 113 IDs.

Evidence checked by me: the gap table in
improvements/worker-y3-fcc-verification.md recounts exactly: 113
rows, 82 FIXED, 31 OWNED, 0 UNOWNED, 113 unique IDs, no
duplicates. The t05 FAIL is grounded in the fixture code:
tests/realistic/clone1-batch3/t05-file-manager/fixture.html
lines 151-156 hardcode the rename (notes.txt always becomes
meeting-notes.txt, Archive always becomes Old files) with no input
for a new name. The t09 and t10 FAILs cite specific check.mjs
lines and the committed results.json; the batch 4 fixes address
exactly these two races (t09 postMessage delivery race, t10
exact-zero position race). The fcc failure record is honest about
laptop-only logs (/tmp/y3/fcc-run.log, "that path does not exist
on the VM"). Note: the audited error-summary file itself lives
outside the repo (~/workspace/cf26-upload/...); the audit table in
the commit is the in-repo evidence.

### 13. dce42ca, COMPLIANT

Claim: FREEZE.md hashes re-verified against the working tree at
freeze time; this commit changes nothing else.

Evidence checked by me: all 12 sha256 hashes in FREEZE.md (as of
dce42ca) recomputed from the files as committed in f31abcf and
matched exactly, 12/12, 0 mismatch, 0 missing. The diff touches
only FREEZE.md and the pilot log, as claimed.

### 14. f31abcf, PARTIAL

Claims: plan frozen after council + redteam + independent checker
review (FAIL narrow, 3 findings, all fixed, matrix re-run 17/17);
checker matrix T1-T16 17/17 passed; preflight tests 7/7 PASS;
test_code_exec suite 53 tests OK; manifest + unblinding scripts
smoke-tested on synthetic data (GO, NO-GO, INCONCLUSIVE, exit
codes 0, 0, 3).

Evidence checked by me, re-run on this machine from the
todolist-push tip: checker matrix 17/17 PASSED, but only after
running the documented build step
(python3 tests/realistic/a1-pilot/checker-selftest/build_matrix.py
first). On a fresh checkout without that step the matrix fails
14/17, because verify.png is gitignored (*.png in .gitignore) and
is only created by the build script. The build regenerates
byte-identical files (git status stays clean), so the claim is
reproducible, but the commit message does not mention the build
step. Preflight: 7 tests OK, re-run by me
(python3 -m unittest tests.test_a1_preflight, 0.002 s). Code exec
suite: 53 tests OK, re-run by me (11.894 s). Unblinding smoke:
I rebuilt synthetic data and re-ran a1_unblind.py myself. GO
returns overall GO exit 0. NO-GO returns overall NO-GO exit 0.
INCONCLUSIVE via the dispersion trigger returns overall
INCONCLUSIVE exit 3. BUT INCONCLUSIVE via an unmeasured gate wall
crashes the script: a1_unblind.py line 226 calls median() on a
wall list containing the string "UNMEASURED", raising TypeError
("'<' not supported between instances of 'int' and 'str'"), exit
1, no verdict printed. The code explicitly anticipates unmeasured
walls (it appends "a gate wall is UNMEASURED" to the inconclusive
reasons), but the think-computation block runs first and crashes
on them. This is a real latent bug in frozen code, found by this
check. The smoke harness itself is not committed (the pilot log
says "Harness in /tmp (not committed)"), so the original smoke
run cannot be re-run as-is. The three checker-review findings
F1-F3 were addressed: F1 (misclicks) fixed in code (check_run.py
now emits misclick_lines plus misclicks "none detected" when 0,
and the matrix expected files match); F2 and F3 fixed by amending
the frozen schema to match the checker (schema now says the final
desktop observe counts in both verification and production, and
framing lines are skipped for gap-before), not by changing the
code. That resolution is legitimate, but it is a spec change, not
a code fix, and should be recorded as such.

### 15. 9cf6391, COMPLIANT

Claim: independent A1 checker review, FAIL narrow, 3 diagnostic
findings (misclicks reporting, vcr_service doc conflict,
gap-before wording).

Evidence checked by me: the review file exists (336 lines),
verdict FAIL (narrow, fixable), findings F1, F2, F3 present with
specific line citations and hand recomputation (T01 vcr_service
0.25 checker/plan vs 0.30 schema-literal; T03 0.184 vs 0.212).
The reviewer ran the matrix independently (section 1 of the
review) and recomputed T01 and T03 by hand (section 2).

### 16. 4a78f7f, COMPLIANT

Claims: design v2 frozen, briefs + infra fixed per council/redteam,
stop-script dry run 11/11 PASS on dummy processes only.

Evidence checked by me, re-run on this machine: I ran the
committed dry-run script (improvements/worker-y8-stop-dryrun.sh)
with the committed stop script placed at /tmp/e1 (where the script
expects it). Result: 11/11 PASS, 5 in phase 1 (holder, driver,
http, gd-4451 killed, gd-4448 spared) and 6 in phase 2 (holder,
decoy spared by the cmdline guard, driver killed via leftover
scan, http, gd-4451 killed, gd-4448 spared), exit 0. Minor note:
cleanup prints "WARNING: a geckodriver still alive" (the pgrep
runs 1 s after TERM); on re-check no geckodriver dummy remained.
The dry-run script itself spawns 300 s sleeps, so a naive run
looks hung; the script finishes in seconds, the sleeps are
background dummies. The design-freeze changes are in the diff
(preflight.py, briefs, driver reference, start/stop scripts).

### 17. 556a592, PARTIAL

Claims: fixture smoke 10/10 clean (all 10 fixtures load with 0
script errors, 0 duplicate ids, no self-verify hooks, no
confirm/alert, no Math.random/Date.now); Codex poll 2.

Evidence checked by me: the log entry gives the exact command
(`node /tmp/y5-verify/smoke.mjs /tmp/y5-stage/fixtures`,
overall:true) and the per-fixture ranges (id counts 17-49,
buttons 2-11, inputs 1-10). BUT the smoke script and the staged
fixtures live in /tmp on the laptop, not in the repo (smoke.mjs
is not in the repo at this commit; only the unrelated
tests/bidi_smoke.mjs is). Not re-runnable from here. Cross-check:
the 10 fixtures on origin/y5-tests total 1043 lines now, against
988 lines claimed at 18:43; the fixtures were still being written
at poll time (test-10 had just finished), so the growth is
consistent with later commits, but the 18:43 figure itself cannot
be recomputed from the repo.

### 18. 66e5e48, COMPLIANT

Claim: redteam KILL of the broad Y6 verdict and the design as
written, with per-proposal verdicts.

Evidence checked by me: the report exists (136 lines), verdicts
per proposal with specific evidence citations (crash PIDs, log
tails, the enable_stdout_logs = 0 finding, the seatd socket mode
with no surviving record). Method is stated honestly: read-only
SSH checks only, one public web search attempted and returned
nothing usable, so that claim stays NOT re-verified by the
redteam itself. A review report is itself the evidence artifact;
its claims were partly re-checked by the Y6 final report, which
incorporates its corrections.

### 19. e8fad29, COMPLIANT

Claim: probe-panel redteam report arrived (90 probes, 86 GAP,
4 HOLDS, 21 HIGH, 50 MEDIUM, 15 LOW); probes 10b/10f are
structurally unable to catch the budget amplification they were
written for and must be rewritten before Phase B.

Evidence checked by me: the redteam file
improvements/worker-y1b-verify-redteam.md exists at this commit
(836 lines as claimed) and its summary line reads "90 probes
attacked. 86 GAP, 4 HOLDS." The severity counts sum to 86
(21+50+15), matching the GAP count. The 10b/10f structural claim
is specific (outer program aborts at the first snippet's 2 s wall,
so the second run_snippet never executes in either implementation)
and is stated as affecting Phase B verification, not Phase A.
I did not re-run the probe panel; the report is the evidence
artifact and its counts check out.

### 20. 6f20fb5, MISSING

Claim: "docs: Y9 agy-y2 live-run plan, pre-registered thresholds,
all Y4d council fixes applied". Section 3 of the plan says the
harness design is "copied from run_agyq2.py, with every known Y4d
defect fixed up front" and that each fix "maps to a Y4d council
finding".

Evidence checked by me: this claim is FALSE, and its own successor
commit says so. a82bb41 (the very next Y9 commit) states: "the v1
plan claimed fixes as 'already applied' while the runner did not
exist and the base still carried every defect. The sharpest
instance: C3-F1, the copied preflight accepted only POSIX locks,
so under the plan's own flock launch it would raise 'no flock
holder' on every run." At 6f20fb5 there was no runner file at all
(run_agy_y2.py first appears in a82bb41, 2517 lines). The
pre-registered thresholds, slot rules, and test-by-test driving
notes in the v1 plan are sound and were carried into v2 unchanged,
but the central "done" claim (fixes applied) was not true when
this commit was made. This is the only commit of the 20 whose
headline done-claim is false rather than merely under-evidenced.

## New findings from this check

1. REAL BUG, a1_unblind.py (frozen in f31abcf): the INCONCLUSIVE
   path crashes when a gate wall is UNMEASURED. Line 226 calls
   median(code_walls) inside the think-computation block with no
   guard for non-numeric walls, while the inconclusive check that
   catches UNMEASURED walls runs after it. Reproduction (synthetic
   data, run by me): GO exit 0, NO-GO exit 0, INCONCLUSIVE via
   dispersion exit 3, INCONCLUSIVE via an unmeasured wall
   TypeError, exit 1, no verdict. The GO bar's most likely
   INCONCLUSIVE trigger (an unmeasured wall) is the one that
   crashes. Fix: guard the think block with the same isinstance
   check the dispersion and timeout-median blocks already use, or
   move the inconclusive verdict before the think computation.
2. WRONG NUMBER, 695efea design note: the plan file has 19 evals,
   not 21; 10 start with `return`, 9 contain it later, 0 have none.
   CORRECTION (redteam, 21:15): first version wrote 5 and 4.
   The fix itself is in code and correct for the diagnose path.
3. FALSE CLAIM, 6f20fb5: "all Y4d council fixes applied" with no
   runner in existence. Corrected by a82bb41, but the correction
   belongs in the record: the v1 plan's fix list was aspirational,
   not applied.
4. BUILD STEP GAP, f31abcf matrix: verify.png is gitignored, so a
   fresh checkout fails the matrix 14/17 until build_matrix.py
   runs. The build is documented in build_matrix.py's docstring
   and regenerates byte-identical files, but the freeze commit
   message does not mention the step.
5. COUNT OFF-BY-ONES, a82bb41: 88 check() assertion lines, not 87;
   79 #id selectors, not 80. CORRECTION (council 2, 21:16): the
   verdict-file numbers here were wrong. The commit message was
   right: verdict files are 91/89/97/132 lines, not 92/90/98/133.
   The 88-line and 79-selector corrections are right. Substance
   holds in every case.
6. F2/F3 RESOLVED BY SPEC AMENDMENT, f31abcf: the schema was
   changed to match the checker, not the other way round. Fine,
   but the freeze record should say so.

## What I re-ran myself (this machine, 2026-11-21)

- md5 recomputation: beebe50 4/4 match; SHIPPED-y9 25/25 match
  (run_live.py skipped as working-tree).
- sha256 recomputation: FREEZE.md 12/12 match against f31abcf.
- Checker matrix: 17/17 after the documented build step
  (3/17 without it).
- Preflight tests: 7/7 OK (0.002 s).
- test_code_exec suite: 53 tests OK (11.894 s).
- Unblinding smoke, synthetic data built by me: GO exit 0,
  NO-GO exit 0, INCONCLUSIVE (dispersion) exit 3,
  INCONCLUSIVE (unmeasured wall) TypeError exit 1.
- Stop-script dry run: 11/11 PASS, exit 0.
- Gap table recount: 113 rows, 82 FIXED, 31 OWNED, 0 UNOWNED.
- Step mapping recount: 343 numbered rows, per-test
  35/35/33/33/35/35/35/35/35/32, 0 dashes, M1-M16 present.
- Port diff: 88 check() lines byte-identical, 79 #id selectors
  all present in the runner.
- Run report arithmetic: run 2 ms sum 49,885, run 1 ms sum 49,741,
  both exact.

## Limits of this check

- Live runs on the owner's Zen (Y4d rerun, Y8 E1, Y9 live) cannot
  be re-run from this machine; their evidence is the committed
  run reports, logs, and the code in the commits. I verified the
  reports' internal arithmetic and the code claims, not the live
  runs themselves.
- Laptop-only evidence (/tmp paths, coredumps, crash reports,
  /tmp/e1 and /tmp/y6-nested artifacts, fcc logs) is recorded as
  such per commit and not counted as verified where I could not
  see it.
- The y5-tests branch was fetched to verify the test-07 fixture
  (3 "Release checklist" messages confirmed). The draft spec Y5
  read at 18:56 is not in any branch, so that half of the test-07
  claim stays UNVERIFIED.
- No commit in this set contains personal information. No em dash
  or en dash in this report.

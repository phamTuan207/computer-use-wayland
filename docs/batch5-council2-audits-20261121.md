# BATCH 5 COUNCIL 2 (AUDITS), 21/11/2026

Reviewer: clone1, batch 5 council 2. Independent re-check of batch 5
task 3 (A1 pilot review) and task 4 (evidence audit of 20
todolist-push commits), plus the 7/10 verdict for original batch 3.
Every number below comes from a check I ran in this session with
`git show <commit>:<path>` (read-only) or a live run of the frozen
code on synthetic data. I did not copy numbers from the task
agents' reports without re-running them.

## Limits of this check

- The exec write window was CLOSED for this whole session: shell
  redirects, Python open() from exec, tar extraction, and git
  worktree all fail with EPERM (PermissionError, Errno 1), files
  created 0 bytes. Only the file tool writes. That blocked three
  re-runs: the checker matrix (no checkout of the a1-pilot tree
  possible), the Layer-1 preflight tests, the test_code_exec suite,
  and the stop-script dry run. For the matrix I verified the
  mechanism from the frozen code and derived the without-build
  count by hand (see the new finding below). The unblinder
  reproductions DID run: the frozen script was piped from git
  straight into python3 stdin, and the synthetic data files were
  written with the file tool (one base set, mutated per scenario).
- Line counts in this report use wc -l (newline count). Every file
  I counted ends with a trailing newline, so wc -l equals the true
  line count here.

## TASK 3 VERDICT: CONFIRMED, with 2 corrections and 1 new finding

Deliverable docs/clone1-a1-pilot-review-20261121.md is 615 lines
(the brief said 616; the file itself is 615). Hole counts recount
exactly: 3 blockers, 13 major, 12 minor, 28 total.

### Freeze: conclusion right, count wrong

- FREEZE.md at f31abcf contains 12 sha256 hashes, not 10. I
  recomputed all 12 against the files at f31abcf: 0 mismatches.
  The task 3 agent undercounted by 2 (the two fixture sha256
  lines, which sit under md5 notes). The conclusion "freeze
  intact" holds; the "10 of 10" figure does not. Task 4 got this
  right (12/12).
- Plan file: 1072 lines at f31abcf and 1072 at the todolist-push
  tip, diff 0 lines. Byte-identical, as claimed. (The parent
  brief said 1074; the true count is 1072.)
- dce42ca touches only 2 files (pilot log and FREEZE.md), as
  claimed. FREEZE.md at dce42ca also has 12 sha256 hashes, all
  matching f31abcf files, 0 mismatches (recomputed by me).
- Fixture md5s recomputed by me: pick4
  91b2f92945c167306a13ae32977a9bf3, 719 bytes; f01
  2b6eda97036af51510b7eefe6d36dd93. Both match.
- f01 spec: 26 numbered steps; step 23 is the wrong-formula
  diagnosis ("Read E7: it shows the text COUNT text instead of a
  number"); end-state cells E2=540000, E3=574000, E4=750000,
  E5=1864000, E6=621333, E7=3. All match.

### B1: CONFIRMED

- Plan line 842 region: "A run with a start marker and no end
  marker within 30 minutes is declared DEAD by Muse." The plan
  itself says the 30-minute figure was calibrated for runs
  "whose measured predecessors run in seconds to a few minutes".
- Plan line 260: "Per-case run caps: Case A 15 min, Case B
  60 min." Runbook line 208 repeats the 30-minute rule.
- Council 3 measurement doc (at f31abcf) estimates Case B at
  "about 40 min hand-driven per run" (lines 76, 431, 848, 936).
  A 40-minute Case B run is declared DEAD at 30 minutes under
  the plan's own rules. The contradiction is real.

### B2: CONFIRMED, reproduced by me

- a1_unblind.py line 80: `if len(manifest) != 12`. Run-number
  check demands exactly [1, 2, 3] per case-arm. Run-dir set must
  equal the manifest run-ids.
- Plan line 849 region: a dead run gets "a new manifest entry
  appended by Muse". Plan line 781 region: an INVALID run is
  "re-run once under the new rule, with the original preserved".
- My reproduction (frozen unblinder, synthetic 12-run data, 13th
  manifest line added): exit 2 with all three errors verbatim:
  "manifest has 13 lines, expected 12", "run numbers for pick4
  STEP are [1, 1, 2, 3], expected [1, 2, 3]", "manifest run-ids
  do not match run dirs: only in manifest ['r13'], only in runs
  []".

### B3: CONFIRMED, all three crash paths reproduced by me

Control first: clean synthetic 12-run data through the frozen
unblinder returns overall NO-GO, cases pick4 GO and f01 NO-GO,
exit 0. The harness works; the crashes below are the inputs.

- B3a. CODE wall "UNMEASURED" with numeric think lines: exit 1,
  `TypeError: '<' not supported between instances of 'int' and
  'str'`, traceback through line 226 (`code_wall_med =
  median(code_walls)`) via median line 42 (`sorted(values)`).
  No verdict printed. The mechanism is exactly as claimed:
  the inconclusive reason "a gate wall is UNMEASURED" is
  appended at line 177, but the think block at lines 220-232
  runs first and its guard only checks that think/gap values
  are numeric, not walls. The dispersion and robustness blocks
  do guard walls with isinstance; the think block does not.
- B3b. Malformed first run-log line ("{not json"): exit 1,
  `json.decoder.JSONDecodeError`, traceback through line 128
  (`json.loads(first)`). Minor correction: task 3 cites line
  125, which is the `open()` call; the parse that crashes is
  line 128. Substance unchanged.
- B3c. Missing run-log.jsonl: exit 1, `FileNotFoundError`,
  traceback through line 125 (the `open()` call). As claimed.

### Spot checks on major holes: all confirmed

- M1: a1_manifest.py draws the held-out task with rng.choice
  and writes it to args.out + ".meta.json" with the seed; the
  manifest itself has no held-out draw; the start assignment
  is drawn from the same seeded rng. The sidecar file is real.
- M2: check_run.py computes program_calls and program_chars
  (lines 326-332, output lines 438-439) but never compares them
  to any cap, and never compares wall_ms to the run caps;
  a1_unblind.py contains 0 occurrences of program_calls or
  program_chars. Honor-system enforcement, as claimed.
- M7: check_run.py line 408 region: `if got is not None and got
  != expected` flags a mismatch, but a missing fixture_md5
  (got None) records no problem. As claimed.
- M12 mechanism: 0 verify.png files exist under
  checker-selftest/cases/ at f31abcf (110 files, 0 png);
  check_run.py lines 84-90 require verify.png to exist and be
  non-empty; build_matrix.py generates a minimal 1x1 PNG per
  case. A fresh checkout cannot run the matrix as documented
  without the build step. As claimed.

### NEW FINDING (mine, in neither task report): the matrix is 16 checks, not 17

- run_matrix.py hardcodes `total = 17` and its docstring says
  "15 regular cases + T11 + T12 = 17 checks". The frozen tree
  has 16 case dirs (T01-T10, T11a, T11b, T13-T16; no T12 dir).
  Regular checks (all T dirs except T11a/T11b) number 14, not
  15. Real checks run: 14 regular + T11 + T12 = 16.
- The printed "17/17 passed" is therefore inflated by one in
  every run. The honest figures are 16/16 with the build step
  and 2/16 without it (script prints 3/17). Both task 3 and
  task 4 repeated the script's printed 17/17 without noticing.
- The without-build count derives cleanly from the code and I
  verified each step: stage1 checks end-state.json AND
  verify.png together and returns early on any problem, so
  without verify.png every regular case gains "missing
  verify.png" and fails its exact stage1 comparison (14 fail,
  including T09, whose expected problem is "verify.png is
  empty", not "missing verify.png", and T08, whose expected
  problem list gains the extra entry). T11 passes without the
  build because it compares T11a against T11b (both equally
  affected, still identical), and T12 passes because it compares
  two runs of T01 against each other (byte-identical either
  way). 14 fail + 2 pass = script prints 3/17 (17 minus 14).
- The checker itself is sound; this is a reporting bug in
  run_matrix.py (hardcoded total and wrong docstring). It must
  be fixed by amendment alongside B1-B3, and the freeze record
  should say 16/16, not 17/17.

## TASK 4 VERDICT: CONFIRMED, with 2 corrections

Deliverable docs/clone1-todolist-push-evidence-20261121.md is 507
lines (the brief said 508; the file itself is 507).

### Recounts I ran myself (all match the agent)

- Compliance table: 20 rows, 13 COMPLIANT, 6 PARTIAL, 1
  MISSING. Exact.
- beebe50 md5s recomputed from the files as committed in
  695efea, 4/4 exact: preflight.py
  b8f234647ed4b2d580681b5ecad5fd3d, brief A
  2741a1a1de8b34e9ca2371d725432438, brief B
  7345f969d5de7516ca40a3505a204829, driver reference
  4775a5710724bea3b64393be16522fdc.
- FREEZE.md at dce42ca: 12 sha256 hashes, recomputed against
  f31abcf files, 0 mismatches.
- Gap table at 4153371: 113 data rows, 82 FIXED, 31 OWNED,
  0 UNOWNED, 113 unique IDs, 0 duplicates. Exact.
- Run 2 ms sum from the report table at 1e3901c:
  5599+5067+5012+4775+4828+4834+4787+5142+4942+4899 =
  49,885. Exact. Run 1 total 49,741 is stated in the report;
  its per-test breakdown is not in the repo, so I could not
  independently sum run 1 (the agent's "sum" wording for run 1
  overstates what the repo supports).
- Step mapping at a82bb41: 670 lines, 343 numbered rows,
  per-test 35/35/33/33/35/35/35/35/35/32, 0 em dashes, 0 en
  dashes, M1-M16 all present. Exact.
- Port diff at a82bb41 vs check.mjs at 30a72e5: 88 lines
  starting with check(, all 88 byte-identical in the runner;
  79 #id selectors in check.mjs, all 79 present in the runner.
  Exact. (The commit message's 87 and 80 are the wrong ones.)
- 9cf6391 review file: 336 lines. 66e5e48 redteam file: 136
  lines. e8fad29 redteam file: 836 lines, summary line "90
  probes attacked. 86 GAP, 4 HOLDS.", severity counts 21+50+15
  = 86. All exact.
- Test-07 (b97d681): the committed spec on origin/y5-tests
  already says "3 matching messages" at step 5 (and "2 matching
  messages" at step 11 after the filter narrows it); the
  fixture has exactly 3 "Release checklist" messages and 1
  "Launch checklist". The agent's finding stands: the "spec
  says 2" half cannot be confirmed from the repo.
- Codex-y5 fixtures on origin/y5-tests: 10 files, 1043 lines
  total. Exact.

### 6f20fb5 false claim: CONFIRMED

- tests/realistic/run_agy_y2.py does not exist at 6f20fb5
  (empty ls-tree). It first appears in a82bb41, 2517 lines.
- a82bb41's own message says: "v2 corrects the false 'fixes
  already applied' claim; every fix is now IN CODE in
  tests/realistic/run_agy_y2.py". The v1 plan's "all Y4d council
  fixes applied" was false when committed. MISSING verdict is
  correct.

### a1_unblind.py TypeError finding: CONFIRMED

- Same as B3a above, reproduced by me this session on the
  frozen code. The GO bar's most likely INCONCLUSIVE trigger
  (an unmeasured wall) is the one that crashes.

### CORRECTION 1: the 695efea eval split is 10/9/0, not 10/5/4

- The plan file at 695efea has 19 eval command objects, not
  21. 10 start with `return`. That part is right.
- Task 4 claims 5 more contain a `return` later and 4 have NO
  `return` at all (the select-set evals and the search-input
  dispatch eval) and "return null from Marionette
  /execute/sync". That is FALSE. I printed all four named
  evals in full: the #select-contact-group eval, both
  #filter-contact-group evals, and the #contact-search dispatch
  eval all end with a return statement (`return e.value`, or
  `return {search:e.value, ...}`). The true split is 10
  start-with-return, 9 return-later, 0 no-return. All 19 evals
  return a value.
- Consequence: the 695efea design note's justification ("21
  evals, all starting with return") is still inaccurate, and
  the fix was still unproven live at commit time, so the
  PARTIAL verdict stands. But the plan file is less affected
  than task 4 says: its conclusion "the plan file is NOT
  affected" is in fact true on the merits (every eval returns),
  not merely "defensible". Task 4's "4 return null" claim must
  be struck from the record.

### CORRECTION 2: the a82bb41 verdict-file counts are 91/89/97/132, not 92/90/98/133

- Task 4 claims the four verdict files are 92, 90, 98, 133
  lines while the commit message says 91, 89, 97, 132. I
  counted both ways (wc -l and splitlines) on the files at
  a82bb41: 91, 89, 97, 132. All four files end with a trailing
  newline, so there is no counting ambiguity. The COMMIT
  MESSAGE was right; task 4 added one to each (the same
  newline-plus-one error the batch 4 redteam caught elsewhere).
- The other two off-by-ones in that finding stand: 88 check()
  lines (not 87) and 79 selectors (not 80), both verified by
  me above.

### Not re-run by me (write window closed, see Limits)

- Checker matrix 17/17, preflight 7/7, test_code_exec 53
  tests, stop-script dry run 11/11. I verified the matrix
  mechanism and derived its counts by hand instead (see the
  new finding above). The dry-run script exists in the commit
  and its phase counts are as described; the live result was
  not reproduced here.

## 7/10 VERDICT FOR ORIGINAL BATCH 3: AGREE, ALL THREE

Checked by reading the fixture and check code at commit
1767d4c (the original batch 3 submission).

### t05 file-manager: DEFECTIVE PASS, agree

- The fixture has exactly 1 `<input` on the whole page:
  #search. There is no rename input, no rename dialog.
- The rename handler (fixture.html lines 151-167) hardcodes
  the outcome: `const next = selected === 'notes.txt' ?
  'meeting-notes.txt' : selected === 'Archive' ? 'Old files'
  : selected + '.renamed';` then `item.name = next;`.
- The check only clicks the item, clicks #rename-btn, and
  asserts the hardcoded names appear (file rename at check
  lines 64-66, folder rename at lines 92-94). It never
  supplies a name. The rename outcome is fully determined by
  the fixture. A broken rename input cannot exist, so the test
  cannot fail for any rename-specific defect. Self-simulated,
  confirmed.

### t09 multi-window: DEFECTIVE PASS, agree

- detail.html: `window.opener.postMessage({ type:
  'project-renamed', ... }, '*'); window.close();` Synchronous
  close immediately after postMessage. prefs.html does the same
  for the theme message.
- The check's clickAndClose awaits the close event, then
  immediately asserts the title (lines 74-78 region) and the
  body class after prefs (lines 89-95 region), with no wait
  for the opener's message handler to run. postMessage delivery
  is async; the close can land first. Flaky by construction,
  confirmed. (The Y3 verification at 4153371 reaches the same
  conclusion with the same lines.)

### t10 music-player: DEFECTIVE PASS, agree

- Check line 64: `if ((await position()) !== 0)
  failures.push('position not reset after next');` A single
  immediate read demanding exactly 0, right after
  `page.click('#next-btn')` and one expectText round trip.
- Fixture: `setInterval(..., 100)` increments position by 1
  while playing; `nextTrack()` sets position = 0. If the 100 ms
  timer ticks between the reset and the read, position is 1
  and the test fails. Exact-0 race, confirmed. (Y3 agrees.)

### The other 7 tests: genuine passes

- t01, t02, t03, t04, t06, t07, t08 use real user-supplied
  input through real controls. No hardcoded-outcome pattern
  like t05 in any of them. The Y3 verification at 4153371
  independently scores the same 7 PASS / 3 FAIL.

### Overall: original batch 3 is 7/10. I agree.

Note on current state: at local HEAD f006137 all three are
fixed (t05 real rename dialog flow in commit 08f36d2, t09 and
t10 in b629e11, reconciled in ed78e83). The 7/10 applies to
the ORIGINAL submission at 1767d4c only, not to HEAD.

## Summary of council 2 findings

- Task 3: CONFIRMED. B1, B2, B3a, B3b, B3c all reproduced or
  verified against the frozen text by me this session. Two
  corrections: FREEZE.md has 12 sha256 hashes, not 10; the
  B3b crash is at line 128, not 125.
- Task 4: CONFIRMED. Table, md5s, FREEZE 12/12, gap table,
  run 2 sum, step mapping, port diff, 6f20fb5 false claim, and
  the TypeError finding all check out. Two corrections: the
  695efea eval split is 10/9/0 (no eval returns null); the
  a82bb41 verdict files are 91/89/97/132 (the commit message
  was right).
- NEW: run_matrix.py reports 17/17 but only 16 checks exist
  (14 regular + T11 + T12). True figures are 16/16 with the
  build step and 2/16 without it. Both task agents repeated
  the script's printed number.
- 7/10 verdict for original batch 3: AGREE on t05, t09, t10,
  with exact lines cited above.

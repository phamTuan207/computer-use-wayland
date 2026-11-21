# Fix-pass-6 Council 3 review: AMEND

Reviewer: Council 3 (voice 3, independent). Scope: ONLY the fix-pass-6
diff, commit d552f4d (parent 0b88ed3), branch todolist-push.
Repo: ~/workspace/computer-use-wayland. Owner: Pham Tuan.

## Verdict: AMEND

No BLOCK. Every fix-pass-5 finding is fixed in code, recorded with its
exact form named, or explicitly deferred with a reason. The guard
works: my independent probe is 87/87 cases plus 26/26 helper checks
across the fix4, fix5 and fix6 blobs, the reconstructed fix6 probe is
71/71 PASS by my own count, and my live /proc spot checks are 9/9
plus an ancestry-exclusion PASS. Hashes verify exactly, the plan pins
the fix-pass-6 values IN the commit, the H4 arithmetic re-derives
clean, and the diff is scanner-only with zero t10 hunks.

Two AMEND items were identified; one is already satisfied (see below):

- U-C3-1 (doc, one line): the import-branch docstring calls the
  nested-misclassification residual "(fail-closed)". Under the repo's
  own convention that word means erring toward refusal, but this
  residual errs toward a missed match, so the label is wrong.
  Reword it (exact fix in C3-NEW-1 below).
- U-C3-2 (process, SATISFIED DURING THIS REVIEW): commit
  tests/realistic/y14b-fix6-probe.py so the fix6 verification is
  re-runnable from the repo. This landed while I was writing, in
  commit 57fcdb2 ("Y14b: fix6 reviews C1 GO (0cc8e27) + C2 AMEND
  (4e905e2); probe files lost, fix6 probe reconstructed and saved
  to tests/realistic (71/71)"), which adds the probe as blob
  cdac7ff (md5 35fc18a6, identical to the working-tree file I ran
  at 71/71). Verified by `git show 57fcdb2 --stat` and md5sum.
  Nothing left to do on this item.

## Hash record (verified by me, not taken from the log)

- `git rev-parse d552f4d 0b88ed3`:
  d552f4d366b5bd6301b2b9a19ed6822d400014b5,
  0b88ed3e14aea20bb7d67f28f00ea5c44088b08f.
- `git rev-parse d552f4d:tests/realistic/run_batch3.py`:
  261f09aed1b52c7b80b0b2fc260f13f70fafd142.
- `git rev-parse 0b88ed3:tests/realistic/run_batch3.py`:
  ff4a5358ac7f621a1fd649c36cec94da2031399d.
- `git show d552f4d:tests/realistic/run_batch3.py | md5sum`:
  fac96935988b9c327dcbe9b3cfa1342e.
- `git show 0b88ed3:tests/realistic/run_batch3.py | md5sum`:
  9e99d9aa1bcdbb525407adfb31e0692b.
- Working tree tests/realistic/run_batch3.py md5, checked twice
  during this review: fac96935988b9c327dcbe9b3cfa1342e (matches fix6).
- `git diff 0b88ed3 d552f4d --stat`: 3 files, plan 17 lines changed,
  log 485 lines changed, run_batch3.py 364 lines changed.
- Follow-up 6235dab ("Y14b log: fix pass 6 hash record") records
  commit d552f4d, blob 261f09ae, md5 fac96935. Verified by
  `git show 6235dab`.

## 1. Fix-pass-5 finding disposition (nothing silently dropped)

Checked every finding in the four fix-pass-5 reviews against the diff
and by direct test. Papers: redteam 92fbefd + addendum 5f842a2,
Council 1 cebd868, Council 2 cebd868, Council 3 6ba5e09 (fix5
Council 3 paper worker-y14b-fix5-council-3.md).

Redteam R5-1..R5-9:

- R5-1 (LOW, code, U1 REQUIRED): FIXED. _quote_states +
  _top_level_sep_index rewrite, import branch restructured
  direct-vs-nested. My probe: B1, B2, B8, B10, d4, C5-1 B5/B6/B7,
  C2-3 c7/c7b/c7c/d1, B3-B7 all True in fix6 (all False in fix5);
  B11/B12 controls still False. R3/R4 controls B11/B12 hold.
- R5-2 (LOW, code, U2 REQUIRED): FIXED. _owning_command flag-value
  skip per Council 1's sketch. A1-A4 True in fix6 (False in fix5);
  A5-A12 boundary controls hold (env -i, --rcfile, sudo -u,
  flock -w, nice -n).
- R5-3 (LOW, U3 FIX): FIXED. _runner_basename_head truncates at
  the first separator char. C1-C5 and C2-4 a1-a7 True in fix6
  (False in fix4 and fix5); over-strip controls a12-a15 False.
- R5-4 (LOW, U4, was "fix or record", now FIXED): FIXED.
  _in_shell_c_string skips a non-shell -c across a top-level
  separator. E1 False in fix6 (True in fix4 and fix5); my two
  controls hold (codex exec foo; echo marionette False, codex
  exec marionette after a python -c True).
- R5-5 (INFO): documented. B13 limitation is named in the
  _top_level_sep_index docstring ("redteam R5-5 / B13,
  pre-existing, documented"). B13 now returns False (was True in
  fix5), which matches the redteam's expectation that the U1
  quote-state sketch closes the form: the scan finds the ";" after
  the first closing quote.
- R5-6 (INFO): no action, correctly. C3-2 deferral is a scope
  choice; the log's "No action" list records it.
- R5-7 (minor, doc): CORRECTED. The _same_command_tokens docstring
  now reads "a bare '&' CAN occur in /proc via direct exec
  (redteam L4), so the old 'cannot occur in /proc' claim is
  corrected, but the behaviour is fail-closed and the form is
  contrived." The direct-form case still returns True (my X18).
- R5-8 (LOW, U7 FIX OR RECORD): RECORDED, per its terms. The
  bare-word FP forms (echo/ssh/cat/grep bash -c) are named in the
  _owning_command docstring and in the _is_runner_cmdline known
  limitations. My probe: all five True (documented behaviour),
  and the b6 mitigation (python3 script.py bash -c ...) False.
- R5-9 (minor, doc): CORRECTED. Plan F7 sentence rewritten (see
  section 4). Both examples verified by direct test (X06 True,
  X11 False).
- Correction 1 (C1-2 refutation withdrawn): CORRECTED at both
  places the refutation appears (log 22:54:52 event entry and
  fix-pass-5 adjudication C1-2 bullet), each with an explicit
  CORRECTION note. Verified in the log diff hunks.
- R5-1 addendum (d4): FIXED by the same rewrite (my R05 True).

Council 1 C5-1..C5-8:

- C5-1 (LOW, REQUIRED): FIXED, subsumed by the quote-state
  rewrite (a token starting with a quote holding only one quote
  of that kind opens a region). Helper test: _top_level_sep_index
  ("'x=1;", False, False) == -1; ("'hello';", False, False) == 7.
- C5-2 (LOW, REQUIRED): FIXED, flag-value skip exactly per the
  sketch (placed before the path-argument skip, with the
  unless-known-command clause). Residual recorded: a flag value
  whose basename is exactly a known command (helper test:
  _owning_command for ["bash", "--rcfile", "python3", "-c", ...]
  returns "python3", as documented).
- C5-3 (CLOSED at HEAD): confirmed closed. Log line 667 at
  d552f4d reads "F3 x9, F4 x3, F5 x2, regressions x14" (verified
  by `git show d552f4d:...restage-log.md`, lines 660-672).
- C5-4 (CLOSED at HEAD + process note): applied. The plan md5
  line pins the fix-pass-6 values IN commit d552f4d itself (plan
  lines 614-615 at d552f4d: fac96935 / 261f09ae; fix-pass-5 values
  demoted to a labeled "Supersedes" line). No follow-up pin was
  needed for the live value; the follow-up 6235dab only records
  the commit hash, which cannot be known before committing.
- C5-5 ("A1-A14" phantom label): CORRECTED at all 3 live uses
  (log lines 994, 1102, 1106 at d552f4d now read "A1-A9 plus 7
  further wrapper cases"). The 5 remaining "A1-A14" occurrences
  at d552f4d (lines 1382, 1425, 1612, 1733, 1943) all quote the
  label being corrected (the C5-5 finding itself, the scope and
  adjudication items, the event log), not live claims.
- C5-6 (probe URL case vacuous): STRENGTHENED in the probe (real
  URL, Council 1 B15: `python3 run_batch3.py http://x/?a=1&b=2`
  returns True). Verified in the reconstructed probe (C5-6 case
  PASS) and in my probe (R14 True in all three blobs).
- C5-7 (direct-form codex "&" docstring line): DONE. One line in
  the _same_command_tokens docstring (the residual paragraph
  quoted under R5-7 above).
- C5-8 (mechanism note): no action, correctly recorded.

Council 2 C2-3..C2-10:

- C2-3 (LOW, code): FIXED (same rewrite as R5-1/C5-1). c7/c7b/c7c
  /d1 True in fix6 (False in fix5), d3 still False, d2 (F2) True.
- C2-4 (LOW, code): FIXED (same as R5-3). a1-a7 True, a12-a15
  False.
- C2-5 (LOW, code): RECORDED, per its "fix or record" terms
  (same as R5-8). The docstring names the exact forms and the
  command-position fix direction.
- C2-6 (minor, doc): CORRECTED (same as Correction 1 above).
- C2-7 (minor, doc): CORRECTED (plan F7 sentence, see section 4).
- C2-8 (minor, doc): DONE. The _top_level_sep_index docstring
  discloses the unmatched-opening-quote limitation AND the d4
  case ("Note the d4 instance ... a glued ';' after an OPENING
  quote ('a=1;') is NOT top-level"), and the import-branch
  comment names d4 ("d4 'a=1;', C5-1 B5 'x=1;'").
- C2-9 (INFO): no action needed, claim corrected (see R5-7).
- C2-10 (INFO): two nits. (a) The fix5 probe docstring nit was
  disposed as "recorded in the fix6 probe header" (log item 14).
  That record is NOT durable: the author's fix6 probe is gone
  from /tmp (see C3-NEW-2), and the reconstructed probe's header
  does not carry the note. Moot in practice (the fix5 probe is
  also gone), but it is the clearest proof of the /tmp-only
  record problem. (b) The adjudication C2-1 bullet staleness
  (states the pre-extension rstrip set) is still present as a
  historical line (log line 1006 at d552f4d), with the correction
  noted at line 1339 and the fix6 adjudication item 3 naming the
  correct old form `base.rstrip(";,()&|")`. Optional polish
  (O-C3-1), not required: C2-10 itself said the record as a whole
  is complete.

Council 3 (fix-pass-5 paper) C3-1..C3-9:

- C3-1..C3-4, C3-6, C3-7, C3-8: closed before fix6; the fix6 diff
  touches none of them (scanner-only proof, section 5).
- C3-5: closed by b9cd0f0 and still correct at d552f4d (see C5-3
  above).
- C3-9 (U11 parenthetical, H4 numbers): still correct. The plan
  H4 note is untouched by the fix6 diff (the plan diff has only
  two hunks: md5 lines and F7), and the numbers re-derive clean
  (section 3). The optional C3-9p rewording is already in the plan
  text ("the operative H4 sentence states the half/half position
  instead of the literal leg-precise clause").

B12 (found during verification): FIXED in code via the new helper
_c_arg_flat_end, direct-case argv boundary only. My probe R09
False; helper tests: _c_arg_flat_end B1 case returns 7, B12 case
returns 4, no-argument case returns the flat count (2). The
nested case does not need it (bounded by the separator stop).

Fix5-to-fix6 flips in my probe: 30 total. 27 are False-to-True
intended fixes (R5-1, R5-2, R5-3 sets). 3 are True-to-False:
B13 (X14, the U1 sketch closes the form as the redteam
expected), E1 (X15, the R5-4 fix), and R13 (the documented
residual, see C3-NEW-1). Fix4-to-fix6 flips: 33 total, every one maps to
a fix-pass-5 finding, a fix-pass-6 fix, or a documented
residual (R2 wrappers, C2-1 glue, R3/R4 bounds, R5-8 FP,
B12, B13, E1). No unexplained flip.

## 2. My independent probe (rebuilt; the author's is gone)

The author's /tmp/y14b-fix6-probe.py (claimed 71/71) is GONE
from /tmp, as are all 17 author probe scripts (the reconstructed
probe's header, citing Council 2 C6-5, says the same; /tmp now
holds only the two run_batch3.py blob copies and my files). I
rebuilt from the four fix-pass-5 papers, which quote every case
cmdline exactly. Probe: /tmp/y14b-c3-fix6-probe.py. It loads the
fix4 blob (git 585fb801, md5 2920f169), the fix5 blob (/tmp copy,
md5 9e99d9aa), the fix6 blob (/tmp copy, md5 fac96935) and the
working tree copy, with the two sibling imports stubbed, and
runs a 3-way differential. Construction: A(argv) joins a real
argv list with NUL (realistic /proc form, single-element -c
code); S(s) whitespace-splits a shell form (synthetic, labeled).

- Command: `python3 /tmp/y14b-c3-fix6-probe.py`
- Result: CASES 87/87 PASS (fix6 vs expectation, tree == fix6 on
  every case), HELPERS 26/26 PASS. Output:
  /tmp/y14b-c3-fix6-out.txt (113 PASS lines: 87 cases + 26 helpers).
- One helper expectation was mine, not the code's: I first
  expected _top_level_sep_index("time;", False, False) == 2, but
  "time;" is 5 chars so ";" is at index 4; the code returns 4,
  which is correct. Probe corrected, second run clean.
- The probe also re-derives the H4 arithmetic (section 3).

Reconstructed fix6 probe (not mine; written by a parallel
Council 2 voice, saved in the repo as
tests/realistic/y14b-fix6-probe.py; untracked at my first check,
committed during this review as 57fcdb2):

- Command: `python3 tests/realistic/y14b-fix6-probe.py`
  (from tests/realistic).
- Result: 71 PASS lines counted by me, 0 failures, exit 0.
  The file holds exactly 71 unit()/live() calls
  (`grep -c -E '^\s*(unit|live)\('` returns 71), so every check
  ran and passed. This matches the author's claimed 71/71 shape
  (68 original + R5-4 case + 2 controls + B12), though it is a
  reconstruction, not the author's original file.
- Its live() helper kills only the spawned parent, not
  descendants: it orphaned a run_foo.py leaf (PID 8655, ppid 1)
  during my run. I killed PID 8655 by exact PID and verified
  with ps that no run_foo/run_batch3 process remained. See
  O-C3-2 below.

Live spot checks (my own, /tmp/y14b-c3-fix6-live.py, working
tree code, real /proc scan via _scan_other_runners()):

- Baseline scan before spawning: [] (no foreign hits at the
  time; foreign PIDs 3919/3921/3923 from another worker's live
  run were present earlier and were left alone).
- L1 bare leaf `python3 /tmp/y14b-dummies/run_foo.py`: hit. PASS.
- L2 `bash -c 'python3 .../run_foo.py; sleep 60'`: wrapper hit,
  leaf child hit. PASS (2 checks).
- L3 mention-only `bash -c 'echo run_foo.py; sleep 60'`: bash
  NOT hit, sleep child NOT hit. PASS (2 checks).
- L4 codex executor (`/tmp/y14b-dummies/codex -c 'run tests &&
  restart marionette'`, ELF sleeper with argv preserved): hit.
  PASS.
- L5 plain codex (`codex exec foo`, no marker): NOT in scan hits,
  IS in _plain_codex_processes() warning list. PASS (2 checks).
- Cleanup: all spawned PIDs plus descendants killed by exact PID
  (SIGKILL), reaped with wait(), final scan shows none of mine
  left. 9/9 PASS, exit 0, `ps` clean afterwards.
- Note: my first run of this script reported 5 "STILL ALIVE"
  lines, which were a bug in my script (os.kill(pid, 0) answers
  True for unreaped zombie children). Fixed by wait() plus a
  /proc stat state check; second run clean, exit 0.

Ancestry exclusion (H2 property, /tmp/y14b-c3-anc.py, run inside
`bash -c 'python3 .../run_foo.py & ... python3 anc.py'`):

- Bash ancestor (PID 10694, cmdline names run_foo.py): NOT in
  hits. Run_foo leaf (PID 10695): in hits. ANCESTRY PASS.
  Leaf killed by exact PID afterwards; `ps` clean.

## 3. H4 margin arithmetic, re-derived independently (Decimal)

Command: the H4 section of /tmp/y14b-c3-fix6-probe.py (Decimal).
Model: 850 ms base + N round trips, tick 100 ms, bound 11,
N=3.5 (Council 1 counts 3, Council 3 counts 4; the advancing
read's own transit is half a round trip).

- N=3.5 @2 ms: (850 + 3.5*2)/100 = 8.57 ticks, reads (8,9).
- N=3.5 @19 ms: (850 + 3.5*19)/100 = 9.165 ticks, reads (9,10).
- N=3.5 @50 ms: (850 + 3.5*50)/100 = 10.25 ticks, reads (10,11).
- Continuous margin vs bound 11: good 11 - 8.57 = 2.43, adverse
  11 - 9.165 = 1.835, half-up 1.84. Plan says 1.84-2.43. MATCH.
- Discrete margin: good phase ticks (8,9) give margins 3,2;
  adverse ticks (9,10) give margins 2,1. Overall 1-3, 1 in
  adverse phase at 19 ms. MATCH.
- Reads overall: 8-10 (8 good, 10 adverse). MATCH.
- One round trip at 19 ms = 0.19 ticks. MATCH ("differ by at
  most 0.19 ticks").
- First fail: (1100-850)/3.5 = 71.43 ms; (1100-850)/3 = 83.33 ms.
  Plan says roughly 70-85 ms. MATCH.
- Sure fail: (1200-850)/3.5 = 100.0 ms; (1200-850)/3 =
  116.67 ms. Plan says about 100-117 ms. MATCH.
- The plan's H4 note is untouched by this diff (plan diff hunks
  cover only the md5 lines and F7), and the diff touches no t10
  threshold or timing (section 5). The numbers still hold.

## 4. Plan and log record checks

- Plan md5 line at d552f4d (lines 614-615): live pin is
  fac96935988b9c327dcbe9b3cfa1342e, blob
  261f09aed1b52c7b80b0b2fc260f13f70fafd142. Fix-pass-5 values
  (md5 9e99d9aa, blob ff4a5358, commit 46e0909) appear only in
  the labeled "Supersedes the fix-pass-5 values" line, plus the
  fix-pass-4 values in the same history sentence. No stale live
  value remains. Command: `git show d552f4d:...live-plan.md |
  grep -n "fac96935\|261f09ae\|9e99d9aa\|ff4a5358"`.
- Log fix-pass-6 entry at d552f4d records the same blob/md5 in
  its Hashes section (blob 261f09ae..., md5 fac96935...).
- Plan F7 sentence at d552f4d (lines 748-753): "a codex -c flag
  now includes everything after it UP TO a top-level separator,
  the bound being quote-state aware (fix pass 6, redteam R5-1 /
  Council 1 C5-1 / Council 2 C2-3), so `bash -c \"codex -c
  'import time; x # marionette'\"` is caught while `bash -c
  \"codex -c 'hello'; echo marionette\"` is not". Both examples
  verified by direct test (my X06 True, X11 False). The sentence
  is now accurate.
- C1-2 correction: both CORRECTION notes present in the log diff
  (event-log entry and fix-pass-5 adjudication bullet).
- "A1-A14": corrected at all 3 live uses (see C5-5 above).

## 5. Scanner-only proof (zero t10 hunks, zero threshold changes)

- `git diff 0b88ed3 d552f4d -- tests/realistic/run_batch3.py` has
  11 hunks, old-line starts 2286, 2339, 2358, 2365, 2489, 2509,
  2519, 2536, 2581, 2706, 2747.
- Independent check with difflib over the two blobs (old 3129
  lines, new 3351 lines): changed old lines span 2342-2756,
  changed new lines span 2289-2978. The t10 test functions live
  at lines 424-2200 (run_b3_t01 at 424 through run_b3_t10 at
  1464). Zero changed lines outside the guard-predicate region.
- Hunks by function: _c_arg_flat_end (new helper, B12);
  _owning_command (flag-value skip + docstring, C5-2/R5-2,
  R5-8/C2-5 record); _quote_states (new helper) +
  _top_level_sep_index (char-by-char rewrite, R5-1/C5-1/C2-3);
  _runner_basename_head (new helper, C2-4/R5-3);
  _is_runner_cmdline (docstring + import-branch restructure +
  basename block, R5-1/B12/R5-8); _in_shell_c_string (rewrite,
  R5-4); _same_command_tokens (quote-state bound + docstring,
  R5-1/C2-3/R5-7/C5-7).
- `grep -i -E 't10|threshold|advancing|position'` over the
  runner diff returns only two docstring prose uses of the word
  "position" (command position, quote positions). No threshold,
  no sleep, no assert, no t10 change.
- `python3 -m py_compile tests/realistic/run_batch3.py`: OK.
  Import OK, 10 tests registered (run_b3_t01..run_b3_t10).

## 6. New findings (mine, fix pass 6)

### C3-NEW-1 (minor, doc, AMEND): "(fail-closed)" label on the nested-misclassification residual is the wrong direction

File: tests/realistic/run_batch3.py, _is_runner_cmdline docstring
(import-branch comment, fix-pass-6 text): "a python -c in a later
top-level command after a shell -c is treated as nested (fix pass
6, import-branch heuristic, fail-closed, contrived, recorded not
fixed)".

Reproduction (my probe R13, argv-list construction):
cmdline = ["bash", "-c", "echo hi", ";", "python3", "-c",
"import os; import run_batch3"] (NUL-joined).
fix4 True, fix5 True, fix6 False.

Under the probe model this cmdline is two top-level commands and
the python one really imports run_batch3, so fix6 newly misses
a real runner invocation relative to fix5. That is the fail-OPEN
direction under the repo's own convention (Council 2 C2-5:
"fail-closed (a false refusal, not a missed runner)"; redteam
R5-8: "fail-closed false positive"). The docstring's
"(fail-closed)" says the opposite of what the code does in the
only reading where the case matters.

Two honest readings, both against the label: (a) probe-model
reading: a real runner is missed, fail-open; (b) literal /proc
reading: the argv is bash positional parameters ($0="echo hi",
$1=";", $2="python3", ...), no python -c ever runs, so nothing
is missed at all and the case cannot occur from a real shell
launch (a real bash -c process carries its string as ONE argv
element; a real python3 process carries its own cmdline, which
the direct form catches). Either way "fail-closed" is wrong,
and the scenario description should say so.

Severity: minor doc only. Live impact is nil under both
readings (the leaf python3 process is caught directly; the
combined argv cannot occur from a real launch). No code change.

Concrete fix (one sentence): replace "(fix pass 6,
import-branch heuristic, fail-closed, contrived, recorded not
fixed)" with "(fix pass 6, import-branch heuristic,
synthetic-only, recorded not fixed: a single /proc cmdline
cannot hold two top-level commands from a real shell launch,
so no live runner is missed)".

Note for completeness: the whitespace-split construction of the
same shell string (my R13-S extra check) returns True in all
three blobs, because the forward scan only covers tokens between
the python -c and the import, and the state before "os;" there
is inside quotes (opened by "'import"). The flip is specific to
the argv-list construction, where the -c code carries no quotes.

### C3-NEW-2 (process, AMEND): fix6 verification has no durable artifact in the repo

The author's fix6 probe (/tmp/y14b-fix6-probe.py, log claim
71/71) is gone from /tmp, as are all 17 author probe scripts
(confirmed by `ls /tmp`, which holds only the two run_batch3.py
blob copies, the fix5/fix6 diff files, and my files; the
reconstructed probe's header says the same). The log's
verification section (fix6 probe 71/71, H2 45/45, fix4 64/64,
transcription 82, gate dry 4/4, C2-extra 36/46, C1-diff 6
failures, C2-probe 7 failures, redteam probes) is therefore not
re-runnable verbatim from the record. I closed the gap by
reconstruction (my 87-case probe, the reconstructed 71-check
probe run at 71/71, live checks), but reconstruction is not a
substitute for the artifact.

Concrete fix: commit tests/realistic/y14b-fix6-probe.py (already
written, untracked at my check, verified 71/71 by me in this
review) so the fix6 verification is re-runnable from the repo.
UPDATE (00:06 +07, while writing this paper): DONE by the parallel
landing. Commit 57fcdb2 adds the probe as blob cdac7ff (md5
35fc18a6, identical to the file I ran), and HEAD == origin/
todolist-push at 57fcdb2. Nothing left to do on this item.
Going forward, probe scripts belong in the repo (or ~/workspace),
not /tmp alone; "recorded in the probe header" dispositions
(C2-10) evaporate with /tmp.

This item does not change the verdict on the code: the code is
verified by two independent reconstructions. It was AMEND
because the ship record should be re-runnable, and it is now
satisfied.

### C3-NEW-3 (INFO, checked and cleared): apostrophe caveat is harmless for runnable forms

The _quote_states docstring discloses that an apostrophe in a
prompt ("don't") unbalances the tracker, erring fail-closed.
I tested both directions because the mechanism can also close
a region early:

- DONT1 `bash -c "codex -c 'a; don't'; echo marionette"`:
  fix4 True, fix5 False, fix6 True. Shell-parse check: the ";"
  after "don't'" sits inside quotes, the whole thing is one -c
  argument, so True is correct. Fix6 repairs a silent fix5 miss
  the papers did not name.
- DONT2 `bash -c "codex -c 'a; don't; echo marionette'"`:
  fix6 False. Live shell check: `bash: unexpected EOF while
  looking for matching '''`. The form is a shell syntax error,
  it never runs, so the miss is harmless.
- DONT3 (same shape, import branch): fix6 False, same syntax
  error, harmless.
- DONT4 double-quoted don't: fix6 True, correct.
- DONT5 escaped apostrophe (`'don'"'"'t'`) plus a real
  separator: fix6 False, correct.
No action. The docstring's fail-closed description holds for
runnable forms.

### C3-NEW-4 (INFO, observation): reconstructed probe's live() orphans its leaf

The reconstructed probe's live() kills only the spawned parent
(p.kill() + p.wait()). Its R5-2/R5-3 live cases spawn a bash
wrapper whose python3 leaf (sleep 60) survives: PID 8655, ppid
1, found by `ps` after my run of the probe. I killed PID 8655
by exact PID and verified `ps` clean. Same footgun class as the
H2 probe note already in the log. Not a defect in the fix diff.
Optional fix (O-C3-2): reap descendants in the probe's live()
helper (deepest-first kill by ppid scan), or use timeout-wrapped
dummies.

### C3-NEW-5 (INFO, optional polish): C2-10 bullet staleness (one line)

The fix-pass-5 adjudication C2-1 bullet still states the
pre-extension rstrip set `base.rstrip(";,()")` (log line 1006
at d552f4d). The correction is noted at line 1339, the
verification section explains the extension (lines 1123, 1190),
and the fix6 adjudication item 3 names the correct old form
`base.rstrip(";,()&|")`. The record as a whole is complete, as
C2-10 itself said. Optional one-line correction (O-C3-1) if the
log is touched again; not required for ship.

## 7. Required fix before ship (AMEND)

- U-C3-1: apply the C3-NEW-1 one-sentence rewording in the
  _is_runner_cmdline docstring (drop the wrong "(fail-closed)"
  label on the nested-misclassification residual).
- U-C3-2: SATISFIED during this review by commit 57fcdb2 (see
  verdict and C3-NEW-2). No action left.

Optional, not ship-blocking:

- O-C3-1: one-line correction of the fix-pass-5 adjudication
  C2-1 bullet (C3-NEW-5).
- O-C3-2: reap descendants in the reconstructed probe's live()
  helper (C3-NEW-4).

## 8. Hygiene

- Em dash (U+2014) and en dash (U+2013) counts over the fix
  diff, per file, counted with Python on the diff text:
  run_batch3.py diff 0/0, plan diff 0/0, log diff 0/0.
- "ydotool" in the fix diff: runner 0, plan 0, log 1, and that
  one is the sentence "No em/en dash in the fix diff, no
  ydotool, no personal info." (prose, not use). No ydotool use
  anywhere in the diff. No ydotool in this paper's verification
  work (all kills by exact PID).
- Personal info: grep over all three diffs for emails, the home
  address, phone patterns and the owner's Gmail handle returns
  nothing. The diffs carry only the repo-facing owner name in
  commit metadata, as usual.
- No live Zen driving by the author (code-only pass, no driving
  in the log) and none by me. No browser work. `import re` is
  stdlib and already used by the runner.
- Stub processes: every process I spawned was killed by exact
  PID (reconstructed-probe orphan PID 8655, my live-check PIDs
  9402-9407 and 9598-9603 plus descendants, ancestry-test leaf
  PID 10695). Final `ps` checks show no run_foo.py, run_batch3.py
  or codex-stub processes of mine remain. Foreign PIDs seen
  during the review (3919/3921/3923, another worker's live run)
  were left alone.

## 9. Limitations (stated plainly)

- The author's original probe scripts are gone from /tmp, so
  the H2 45/45, fix4 64/64, transcription 82 and gate-dry 4/4
  re-runs in the log were NOT re-run verbatim by me. What I did
  instead: (a) rebuilt the fix6 coverage from the four review
  papers (87 cases + 26 helpers, all PASS, 3-way differential
  against fix4/fix5/fix6); (b) ran the reconstructed 71-check
  fix6 probe (71/71 PASS, exit 0); (c) ran live /proc spot
  checks covering H2's substance (wrappers caught, mention not
  caught, codex executor caught, plain codex warning-only,
  ancestry excluded) at 9/9 plus ancestry PASS; (d) proved the
  transcription result is unchanged by construction (zero diff
  lines outside the guard region, section 5), so the t10
  translation the transcription checks is byte-identical between
  fix5 and fix6 in every line the transcription covers. The
  full gate-dry harness (faked Zen/Marionette/ports) was not
  rebuilt; only its /proc-scan core was re-verified live.
- My probe is a reconstruction, not the author's file: case
  constructions follow the papers' quoted cmdlines, with the
  realistic single-element -c form used throughout (per the
  log's own correction note) and synthetic whitespace-split
  forms labeled S. Where the papers' construction was
  ambiguous I tested both forms (R10 vs the reconstructed
  probe's B12/R4 multi-element form; R13-A vs R13-S) and both
  agree with the stated expectations except R13-A, which is
  C3-NEW-1.
- The checkout is shared with other workers: HEAD moved during
  this review (6235dab at start, 57fcdb2 at the end, which also
  committed the reconstructed probe). I committed only my paper
  file (see below) and verified the working-tree run_batch3.py
  md5 twice (fac96935 both times).

## 10. Work log (Asia/Ho_Chi_Minh, 21-22/11)

- 23:49 +07: brief received. Verified hashes and the diff stat
  first (blob 261f09ae, md5 fac96935 at d552f4d; ff4a5358 /
  9e99d9aa at 0b88ed3).
- 23:52 +07: read the full runner diff (11 hunks), plan diff
  (md5 pin + F7), log diff (adjudication + verification +
  hashes + event log).
- 23:55 +07: read all four fix-pass-5 review papers and
  extracted the case inventory (R5-1..R5-9, C5-1..C5-8,
  C2-3..C2-10, C3-1..C3-9).
- 00:00 +07 (22/11): found the author's probes gone from /tmp;
  extracted the fix4 blob 585fb801 from git (md5 2920f169
  verified) for the 3-way differential.
- 00:01 +07: scanner-only proof via difflib (changed lines
  2342-2756 old, 2289-2978 new); H4 re-derivation with Decimal.
- 00:02 +07: wrote my probe /tmp/y14b-c3-fix6-probe.py (87
  cases + 26 helpers + H4 section). First run 87/87 cases,
  25/26 helpers (one expectation of mine wrong: "time;" has
  ";" at index 4, not 2). Fixed the probe, second run 87/87
  and 26/26.
- 00:03 +07: ran the reconstructed probe
  tests/realistic/y14b-fix6-probe.py: 71/71 PASS, exit 0.
  Cleaned up its orphaned leaf PID 8655 by exact PID.
- 00:04 +07: ran my live spot check (9/9 PASS, exit 0) and the
  ancestry check (PASS). Investigated the DONT1-DONT5 apostrophe
  cases and the R13-A/R13-S pair, including a live shell check
  proving DONT2/DONT3 are syntax errors.
- 00:05 +07: doc verification round (plan md5 line, log line
  667, F7 sentence, A1-A14 occurrences, C2-10 bullet, single
  caller of _in_shell_c_string). Wrote this paper.
- 00:06 +07: before committing, found HEAD moved to 57fcdb2,
  which already commits the reconstructed probe (U-C3-2
  satisfied). Updated the verdict, C3-NEW-2 and section 7 to
  record that. Committing only this paper file.

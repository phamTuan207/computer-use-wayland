# Council 2 review: Y14b fix pass 5 (run_batch3.py guard)

Verdict: **AMEND**

Reviewer: Council 2 (voice 2, fix pass 5). Scope: ONLY the fix-pass-5
diff, that is the diff between fix pass 4 (commit bf3c939) and fix
pass 5 (commit 46e0909), in tests/realistic/run_batch3.py plus
improvements/worker-y14-batch3-live-plan.md and
improvements/worker-y14b-restage-log.md. I review my own fix-pass-4
findings C2-1 and C2-2 first, then the R2/R3/R4 fixes as they interact
with them, then the doc fixes. Every claim below is my own reproduction
with the exact command and output; nothing is taken from the fix
author's log on trust.

## Hashes verified (by me, 23:09 +07)

- Commit 46e0909: `46e0909058af1419c0ef6534394a68019ec8ebd8` (git rev-parse).
- Parent bf3c939: `bf3c939741f86c6c639c730882f8a4f721265a74`.
- run_batch3.py at 46e0909: git blob
  `ff4a5358ac7f621a1fd649c36cec94da2031399d`, md5
  `9e99d9aa1bcdbb525407adfb31e0692b`. Both match the task brief and the
  plan's ship-time pin (plan lines 614-615, fix-pass-5 entry).
- The plan pin is CURRENT: it pins the fix-pass-5 values and keeps the
  fix-pass-4 values (md5 2920f169, blob 585fb801, commit bf3c939) as
  superseded (plan lines 616-617). The log has the fix-pass-5 hash
  entry (log lines 1146-1151). No stale-pin ship blocker.

## What verified clean (my own runs, not the author's)

All commands run on this VM against the working tree at 46e0909
(md5 9e99d9aa, re-verified after every step).

- Fix5 probe `/tmp/y14b-fix5-probe.py`: 38/38 PASS, exit 0
  (re-run 23:09 +07). Its docstring claims live cases, but the file
  has 38 unit cases and no live cases; see C2-10, probe-doc nit only.
- Regressions, all green, exit 0: H2 probe 45/45, fix2 probe 31/31,
  fix3 probe 70/70, fix4 probe 64/64, transcription 82 PASS, gate dry
  4/4, M1 probe 3/3, M1 all-12 probe 4/4.
- py_compile OK; import OK (23:12 +07).
- My fix-pass-4 extra probe `/tmp/y14b-fix4-c2-probe.py`: 36/46 PASS,
  10 failures, ALL judged by me to be expected-behavior changes (the
  fix), not regressions. Case by case, each is the fix-pass-4 behavior
  I documented, corrected by fix pass 5: 'sep single & alone' (C2-2,
  bare & is now a separator); 'c env/nice/sudo bash -c MISS' (R2,
  wrapper-prefixed shell -c now caught); 'glued; python3 run_foo.py;
  echo MISS' and 'glued; bare run_foo.py; echo MISS' (C2-1, glued
  separator now matches); 'codex -c marker in LATER shell cmd' (R3,
  later-command marker now excluded); 'codex single & --help & echo
  FP' (C2-2, & now bounds the marker scope); 'live glued ; wrapper
  missed' (C2-1, live, wrapper now caught); 'live double-nested
  wrapper missed' (unadvertised but correct: the outer wrapper
  genuinely launches the runner transitively, so True is right; the
  F8 position only ever claimed the leaf is caught, not that the
  wrapper must miss). No stubs survived (ps check empty after the run).
- My own probe `/tmp/y14b-fix5-c2-probe.py`: 59 cases, 43 PASS, 16
  FAIL, and all 16 FAILs are the findings C2-3, C2-4, C2-5 below
  (7 + 5 + 4). The 43 passes cover the over-strip controls, the URL
  tokens, the wrapper forms that must stay True, the R3/R4 intended
  cases, the F2 case, and the live wrapper cases.
- R2 verified live: `timeout 60 bash -c <stub>` wrapper True,
  `flock /tmp/y14b-fix5-c2.lock bash -c <stub>` wrapper True,
  `sudo -n bash -c <stub>` wrapper True (sudo -n works on this VM),
  `env bash -c <stub>` caught via the surviving bash process. All
  with the leaf python3 process also caught.
- C2-1 spaced forms verified live: `bash -c 'python3 <stub>; sleep
  60'` wrapper now True (was False in fix4, my L5).
- C2-2 URL safety verified: `codex exec https://example.com/?a=1&b=2
  marionette` True, `bash -c "codex exec https://x/?a=1&b=2
  marionette"` True, `python3 run_batch3.py --url
  "http://x/?a=1&b=2"` True (c2, c3, c4). Bare & in the -m branch and
  the -c guards verified: `python3 -m run_batch3 & echo done` True,
  `python3 --version & pytest -m run_batch3` False (c9, c10).
- R3 intended case verified: `bash -c "codex -c 'hello'; echo
  marionette"` False (d3, and the fix5 probe case). F2 preserved:
  `bash -c "codex -c 'import time; x # marionette'"` True (d2).
- R4 intended cases verified: `python3 -c 'import os'; echo import
  run_batch3` False and `bash -c "python3 -c 'import x'; echo import
  run_batch3"` False (fix5 probe cases, re-run 38/38).
- Doc fixes verified accurate: C1-1/C3-1 (plan line 738 and log lines
  601-602 now say False for `python3 run_other -W ignore
  run_batch3.py`, and the fix4 probe label now reads "now False (was
  True in fix3)", probe line 83); C3-2/C1-R2 (residual recorded in the
  `_python_executes` docstring and the `_is_runner_cmdline`
  docstring, and the fix5 probe case `python3 other -W ignore` still
  True is pinned); C3-4 (the fix-pass-3 redteam paper bd3c6c9 lines
  222-243 indeed says `python3 other.py -m run_batch3`, not
  run_other.py; the plan and log corrections are accurate); C3-5 (I
  counted the fix4 probe source by section: R1 6, F1 5, F3 9, F4 3,
  F5 2, regressions 14, codex 21, live 4, total 64, exact); C3-6
  (log now says the "72" was a plain miscount); C3-7 (bd3c6c9 line
  394 says "U4 (F3, code or record)", and the log line 527 now says
  "U4 left open"); C3-8 (log env note now states the solved root
  cause and the proper repair); C3-9 (U11 parenthetical in the plan
  H4 note, lines 752-757); C1-R3 (glued `;codex` miss recorded in
  the `_is_runner_cmdline` docstring); C1-R1/R4/C3-3 (import guard
  boundary fixed, cases above).
- Hygiene: 0 em/en dash in the fix diff (python count on the
  bf3c939..46e0909 diff for the three files); "ydotool" appears 5
  times, all inside "no ydotool" hygiene lines; no personal info in
  the diff (grep for the owner name, emails, addresses: 0 hits
  outside the repo-facing owner name); no live Zen driving (no GUI
  work in this review at all).

## Findings

### C2-3 (LOW, code, fix-pass-5 REGRESSION): the R3 quote-aware bound breaks nested codex -c snippets that contain a spaced separator, or an unspaced `;` glued to the opening quote

Evidence: run_batch3.py:2722 (`_same_command_tokens`), :2741 (the
forward loop's standalone-separator break) and :2756 (the `-c`
branch loop calling `_top_level_sep_index`, :2368).

Reproduction (my probe `/tmp/y14b-fix5-c2-probe.py`, cases c7, c7b,
c7c, d1; `python3 /tmp/y14b-fix5-c2-probe.py`, 23:13 +07):

- `bash -c "codex -c 'a & b marionette'"` returns False, must be True
  (the marker is inside the codex snippet; `&` is prompt text).
- `bash -c "codex -c 'a ; b marionette'"` returns False, must be True
  (same, spaced `;`).
- `bash -c "codex -c 'a && b marionette'"` returns False, must be True.
- `bash -c "codex -c 'a;b marionette'"` returns False, must be True
  (the `;` sits in the same token as the unmatched opening quote).

Differential against fix pass 4 (bf3c939 blob loaded standalone with
the two sibling imports stubbed; working tree untouched, md5
re-verified 9e99d9aa after): all four return True in fix4 and False
in fix5. This is a regression introduced by fix pass 5, not a
pre-existing miss. The R3 intended case still works
(`codex -c 'hello'; echo marionette` False, d3), and the F2 case
still works (d2), so the bound is too eager, not wholly wrong.

Root cause: `_top_level_sep_index` treats a standalone separator
token as top-level unconditionally (its first line returns 0 for
`;`, `&&`, `||`, `&`, `|`), and treats a `;` after the last quote
character in a token as top-level even when that quote is an
UNMATCHED opening quote. Inside a codex `-c` snippet the tokens are
prompt words, not shell words: a standalone `&` after the token
`'a` (one opening quote, never closed in that token) is prompt text,
and the `;` in `'a;b` is inside the quoted region the opening quote
starts. The heuristic cannot tell an opening quote from a closing
quote inside a single token, and the `-c` branch loop carries no
quote state across tokens.

Live impact: LOW, leaf-masked. The codex leaf process itself
(`codex -c 'a & b marionette'` as a direct argv) still returns True
via the all-tokens path (`_in_shell_c_string` False, c6/c7
differential: direct form True), so `_scan_other_runners` still
refuses the slot through the leaf. Only the bash wrapper process
misses. A prompt of the shape "do A & drive marionette" is plausible
("compare X & Y", "fix A & B"), so this is a real prompt-shape miss
at unit level, not a contrived one.

Required fix (fix pass 6): make the `-c` branch loop in
`_same_command_tokens` quote-state aware. Sketch: track cumulative
single/double quote parity over the snippet tokens consumed so far;
break on a standalone separator only when both parities are even
(we are outside quotes); for a glued separator inside a token, find
the first separator that occurs while outside quotes given the entry
state (a small scan over the token's characters, toggling on quote
chars), instead of "after the last quote in the token". Re-prove:
c7/c7b/c7c/d1 True, d3 still False, d2 (F2) still True, and the
fix5 probe still 38/38.

### C2-4 (LOW, code, C2-1 only half fixed): unspaced glue on the runner token still misses

Evidence: run_batch3.py:2539
(`if _script_basename_is_runner(base.rstrip(";,()&|")):`).

Reproduction (my probe cases a1-a7, same run):

- `bash -c "python3 run_foo.py;echo done"` False, must be True.
- `bash -c "python3 run_foo.py&&echo done"` False, must be True.
- `bash -c "python3 run_foo.py||echo done"` False, must be True.
- `bash -c "python3 run_foo.py|cat"` False, must be True.
- `bash -c "python3 run_foo.py&echo done"` False, must be True.
- `bash -c "run_foo.py;echo done"` (bare) False, must be True.
- `bash -c "run_foo.py&&echo done"` (bare) False, must be True.

The fix5 probe only covers the SPACED forms (`run_foo.py&&` + space
+ `echo`), where the separator is the token's last character and
`rstrip` strips it. When the separator is followed by more text in
the same token (`run_foo.py&&echo`), `rstrip` strips nothing (the
token ends in `o`) and the `.py` endswith check fails. The shell
parses `&&` as an operator with or without spaces, so
`python3 run_foo.py&&echo done` really runs run_foo.py. Note the
import branch already tolerates this shape (its check is
startswith-based, `base.rstrip(";,()").startswith("run_")`,
:2581-2582), and the `-m` branch tolerates it too (`python3 -m
run_batch3&&echo` True, a16); only the basename block (endswith
`.py`) does not.

Live impact: LOW, leaf-masked. Live L2: `bash -c 'python3
<stub>&&sleep 60'` wrapper False, but the leaf python3 process is
found and caught, so the gate still refuses. The miss is unit-level
only, on a compact one-liner form.

Required fix (fix pass 6): truncate the basename at the FIRST
separator character instead of stripping trailing ones, e.g. take
`base` up to the first of `;`, `&&`, `||`, `|`, `&` before the
`_script_basename_is_runner` check. My over-strip controls must stay
False after the change: `md5sum run_foo.py;echo` False (a12), `echo
run_foo.py&&x` False (a13), `vim run_foo.py|cat` False (a14),
`md5sum run_foo.py;` False (a15). Those stay False because the branch
guards (prev must be python / `-c` / a flag / two-back / bash-sh, or
i == 0) are untouched; only the name match widens. Re-prove a1-a7
True and a12-a15 False. If the author judges the truncation unsafe,
record the unspaced forms as a residual in the basename-block comment
instead, but do not leave C2-1 claimed fully fixed while they miss.

### C2-5 (LOW, code, NEW false positive): `_owning_command` returns ANY bare word before `-c` as the owner, so a non-command that merely mentions `bash -c` now flags

Evidence: run_batch3.py:2340 (`_owning_command`), :2393
(`_c_is_shell`).

Reproduction (my probe cases b1-b5, same run; differential fix4
False, fix5 True for all five):

- `echo bash -c run_batch3.py` returns True, must be False (echo
  prints the words; no shell `-c` runs).
- `ssh host bash -c run_batch3.py` returns True, must be False (the
  ssh client is not running the runner locally).
- `echo bash -c codex exec marionette` returns True (codex side),
  must be False.
- `cat notes.txt bash -c run_batch3.py` returns True, must be False.
- `echo sh -c run_foo.py` returns True, must be False.

Live proof (23:15 +07, compiled sleeper `/tmp/y14b-sleeper`, ELF so
the kernel does not drop argv[0] the way it does for a `#!/bin/sh`
script): spawned with argv `["echo", "bash", "-c", "run_batch3.py"]`,
`/proc/<pid>/cmdline` reads exactly `echo`, `bash`, `-c`,
`run_batch3.py`; `_is_runner_cmdline` returns True; and
`_scan_other_runners` hits the pid. Killed after; `ps` clean. This
is a live-reachable false positive in `/proc`, not a synthetic-only
one. (My first live attempt used the codex stub and proved nothing:
the kernel drops argv[0] for scripts, so the echo token vanished;
corrected with the compiled sleeper. See the appendix.)

Root cause: `_owning_command` walks back skipping flags,
assignments, and unknown-basename paths, then returns the first
remaining token's basename whatever it is. In fix4 the walk went to
argv[0] (or a separator), so `echo bash -c` resolved to `echo`
(False); in fix5 the nearest bare word wins, so `bash` wins even
when it is another command's argument. The `.py` guard mitigates one
sub-case only: `python3 script.py bash -c run_batch3.py` stays False
(b6), because a `.py` token before the `-c` blocks the first-word
branch. The realistic reachability is the ssh-client form (an agent
ssh-ing to the laptop with `bash -c <runner>` as separate argv
tokens; sshd is not running on this VM, connection refused, so the
ssh form is unit-verified only, not live-verified here). The gate
runs on the laptop, where the ssh client process is not present, so
the practical blast radius is a false refusal on the VM gate-dry
path and on any host where such an argv is scanned.

Severity: LOW and fail-closed (a false refusal, not a missed
runner). The R2 fix it pays for (wrapper-prefixed shell `-c` caught)
is worth more than this costs, so this is AMEND, not BLOCK.

Required fix (fix pass 6, author chooses): EITHER record the class
as a known residual in the `_owning_command` / `_c_is_shell`
docstring (exact forms named, with the ssh-client note) and add probe
cases pinning the behavior (b1-b5, expecting True as documented
fail-closed over-approximation), OR tighten the walk-back (the robust
form is a forward parse from the command start, unwrapping a fixed
wrapper set with per-wrapper arg skipping; a bare-word denylist is
fragile and not recommended). Recording is proportionate here given
the direction (fail-closed), the narrowness, and the laptop-side
gate; a forward-parse rewrite is not demanded for this finding.

### C2-6 (minor, doc): the C1-2 refutation is wrong; C1-2 was valid at bf3c939 and was fixed by the hash-record follow-up, not refuted

Evidence: `git show bf3c939:improvements/worker-y14-batch3-live-plan.md`
lines 612-615 pin the fix-pass-3 values (md5 e9e3519a, blob 3a9b7b17,
commit 3875215), and at bf3c939 the log's fix-pass-4 entry reads
"- Fix commit: (hash filled below after commit)." (unfilled).
`git show 40c4e48:...` pins the fix-pass-4 values. Council 1's C1-2
("pinned ship-time md5 is stale, plan still pins fix-pass-3 values,
log has no superseding fix-pass-4 entry") was therefore CORRECT
about the bf3c939 tree. The author's adjudication ("REFUTED...
Council 1 must have read a stale file", log 22:54:52 entry) greps a
working tree AFTER 40c4e48 had already applied the fix, and mistakes
the fixed state for the reviewed state. The current state is correct
(the plan pins fix-pass-5 values), so there is no live error; only
the record is wrong.

Required fix: correct the adjudication entry (one or two sentences):
C1-2 was valid at bf3c939 and was fixed by the hash-record follow-up
40c4e48, not refuted. Do not let a future reader conclude Council 1
misread the tree.

### C2-7 (minor, doc): the plan's F7 sentence is stale after the R3 bound

Evidence: plan lines 746-751: "a codex -c flag now includes everything
after it, so `bash -c \"codex -c 'import time; x # marionette'\"` is
caught". After fix pass 5 that is false as stated: a TOP-LEVEL
separator now ends the snippet (R3), and `codex -c 'hello'; echo
marionette` is NOT caught. The sentence was accurate for fix pass 4
and was not updated in the fix-pass-5 plan diff.

Required fix: qualify the sentence ("includes everything after it
until a top-level separator, so a marker in a later shell command
does not count; the F2 snippet case is still caught").

### C2-8 (minor, doc): `_top_level_sep_index` discloses one limitation but not the unmatched-opening-quote limitation; the import-guard instance of the same root cause is unrecorded

Evidence: run_batch3.py:2368 docstring discloses only the
"separator BEFORE its last quote" limitation. The unmatched-opening-
quote limitation (C2-3 root cause, and d4 below) is not disclosed.

Reproduction (d4, d5): `bash -c "python3 -c 'a=1; import
run_batch3'"` returns False for the wrapper (the `;` in `'a=1;`
sits after the opening quote, so the guard scan breaks before
reaching the `-c`), while the direct leaf form `python3 -c 'a=1;
import run_batch3'` returns True (d5). The wrapper miss is
leaf-masked (the leaf python3 process is caught), so no code fix is
demanded for the import guard; the backward scan cannot easily carry
quote state.

Required fix: add the limitation to the `_top_level_sep_index`
docstring ("a separator after an UNMATCHED opening quote in its
token is misjudged as top-level; e.g. `'a;b` inside a nested codex
snippet, and `'a=1;` in a nested python -c import, where the leaf
process is still caught") and record the d4 wrapper-only miss as a
residual in the import-branch comment.

### C2-9 (INFO, no action): the direct-form codex `&` case is unchanged, and that is correct; only the author's justification is overstated

My probe first expected `codex --help & echo marionette` (direct
form, c1) to return False after fix5. It returns True, unchanged
from fix4 (differential: fix4 True, fix5 True). That expectation was
mine and it was wrong: the direct form has no shell `-c`, so
`_same_command_tokens` never bounds it, and the marker IS literally
in codex's argv, exactly like `codex --help marionette` (True by the
stated fail-closed direct-form rule). The author's probe change to
the bash -c form is legitimate: the bash -c form is the one a shell
produces, and it now returns False.

One correction to the author's justification, recorded here, no
action needed: the verification section says the direct form "cannot
occur in /proc (the shell splits `&` before exec, so a codex
process never has `&` in its argv)". That is overstated. My live L4
proves a bare `&` token CAN appear in a real `/proc` cmdline via
direct exec: I spawned the codex stub with argv `["codex",
"--help", "&", "echo", "marionette"]` and read `/proc/<pid>/cmdline`
with `&` present as its own token. (The spawned process's
`_is_codex_executor` returned False, but through the sh-wrapper path
of the shebang stub, not through the `&` bound, so that half of L4
proves existence only.) The author already records the direct form
as "a synthetic-only residual, not a code fix", which is the right
disposition; the "cannot occur" phrasing should read "cannot occur
via a shell; only via direct exec, where `&` is a literal argument
and the fail-closed True is defensible". No code change.

### C2-10 (INFO, no action): two probe/adjudication nits

- The fix5 probe docstring says "Live cases spawn the dummy stub
  and check `_scan_other_runners` hits it", but the file has 38 unit
  cases and no live cases. Probe-doc nit only; the live coverage
  exists in the older probes and in my probe's live section.
- The adjudication's C2-1 bullet says the basename block checks
  `base.rstrip(";,()")`, but the shipped code is
  `base.rstrip(";,()&|")` (:2539). The verification section explains
  the extension (the first probe run failed the `&&` / `||` variants
  and the set was extended), so the record as a whole is complete;
  the bullet itself is stale. One-line correction if the log is ever
  touched again.

### Observations (checked, no action)

- a17: `python3 -m run_batch3.py&&echo` still misses
  (`_is_runner_module` does not strip a glued separator from a
  `.py`-suffixed module name). Contrived form; the bare-module form
  (a16) works. Not a finding.
- b11: `su root -c run_foo.py` still misses (pre-existing, fix4 also
  False; `su -c` runs a shell). Not fix-pass-5 caused; not a finding.
- b6: the `.py` guard in the first-word-of-`-c` branch partially
  mitigates C2-5 (`python3 script.py bash -c run_batch3.py` False).
  Worth knowing for the fix-pass-6 author; not a finding.
- The fix5 probe's R2 section covers the redteam A1-A14 (14 runner
  cases) plus 2 codex wrapper cases; all pass in my re-run.

## Required fixes for fix pass 6 (AMEND, not BLOCK)

1. Quote-state-aware bound in the `_same_command_tokens` `-c`
   branch (C2-3). Re-prove c7/c7b/c7c/d1 True, d3 still False, d2
   still True, fix5 probe still 38/38.
2. Truncate-at-first-separator in the basename block, or record the
   unspaced forms as a residual (C2-4). Re-prove a1-a7 True (if
   fixed) and a12-a15 still False.
3. Record the `_owning_command` false-positive class (C2-5) in the
   docstring with probe cases pinning it, or forward-parse the
   wrappers. Recording is acceptable.
4. Doc corrections: C1-2 refutation (C2-6), plan F7 sentence (C2-7),
   `_top_level_sep_index` limitation disclosure plus the d4 residual
   (C2-8).

Nothing here blocks ship on its own: every miss is leaf-masked live
(the python3 / codex leaf process is caught, so the gate still
refuses), the one false positive is fail-closed and narrow, and the
doc errors do not touch the live ship-time pin (which is correct).
But C2-3 is a fix-pass-5 regression on a plausible prompt shape and
C2-1 was my finding and is only half fixed, so they must not ship
unfixed-or-recorded. AMEND.

## Appendix: event log (wall-clock Asia/Ho_Chi_Minh)

- 23:09:22 +07: review starts. Hashes verified (commit 46e0909, blob
  ff4a5358, md5 9e99d9aa). Fix5 probe re-run: 38/38 PASS, exit 0.
- 23:10 +07 (approx): fix-pass-4 extra probe re-run: 36/46, 10
  failures, each judged a fix, not a regression (listed above).
  No stubs survived (ps check empty).
- 23:11 +07 (approx): fix-pass-5 diff read (run_batch3.py,
  plan, log); prior papers read (fix4 council 1/2/3, redteam
  eae5a99); plan pin and log hash entry verified current.
- 23:12 +07 (approx): MISTAKE, disclosed: while building a
  fix4-vs-fix5 differential I ran `cp <fix4 blob>
  /tmp/fix4check/run_batch3.py` after symlinking
  `tests/realistic/*.py` into /tmp/fix4check; `cp` followed the
  run_batch3.py symlink and overwrote the REAL working-tree
  file with the fix4 blob (md5 2920f169, git status showed the
  modification). Restored immediately with `git checkout --
  tests/realistic/run_batch3.py`; md5 re-verified 9e99d9aa,
  matching HEAD. No other file was touched by me (the other
  modified/untracked files in `git status` are other workers').
  The differential was redone with stubbed imports instead
  (no symlinks into the repo). Lesson: never symlink repo files
  into a scratch dir and copy over them.
- 23:13 +07 (approx): my own probe `/tmp/y14b-fix5-c2-probe.py`
  written (59 cases) and run: 43 PASS, 16 FAIL (a1-a7, b1-b5,
  c7/c7b/c7c, d1). Differential fix4-vs-fix5 run: c7/c7b/c7c/d1
  fix4 True to fix5 False (regression); b1-b3 fix4 False to fix5
  True (new FP); a1/a2 fix4 False to fix5 False (still missing);
  c1 fix4 True to fix5 True (unchanged).
- 23:14 +07 (approx): live checks. L1/L2/L3a/L3b/L3c pass. L4
  proves a bare `&` token exists in a real `/proc` cmdline.
  L5 first attempt confounded (shebang stub drops argv[0]; the
  echo token vanished, so the check proved nothing); corrected
  with the compiled sleeper `/tmp/y14b-sleeper`. Also noted 3
  processes from another reviewer's concurrent probe (`timeout 3
  bash -c export PATH=... codex --help & echo marionette; wait`,
  started 16:14 UTC); not mine, left untouched.
- 23:15 +07 (approx): L5 corrected live proof: argv exactly
  `echo`, `bash`, `-c`, `run_batch3.py` in `/proc`, flagged True
  (FP), `_scan_other_runners` hits the pid, process killed, ps
  clean. `sudo -n` works on this VM; ssh to localhost refused
  (no sshd), so the ssh-client FP form is unit-verified only.
- 23:16 +07 (approx): full regression set re-run green (H2 45,
  fix2 31, fix3 70, fix4 64, transcription 82, M1 3, M1 all-12 4,
  fix5 38, gate dry 4/4). My probe re-run twice more for
  stability: 16 FAILs both times, same set (one intermediate
  count of 17 was my grep counting the FAILURES summary line).
- 23:17:15 +07: doc verifications finished (C3-5 breakdown counted
  from source: 6+5+9+3+2+14+21+4=64; C3-4 from bd3c6c9 lines
  222-243; C3-7 from bd3c6c9 line 394 and log line 527; gate dry
  4 PASS lines). Paper written. No live Zen driving at any point;
  no browser work; no ydotool; no em/en dash in this paper
  (verified by grep before commit).

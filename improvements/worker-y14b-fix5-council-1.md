# Council 1 paper: fix pass 5 over fix-pass-4 reviews (AMEND x4)

Scope: ONLY the fix-pass-5 diff, commit
46e0909058af1419c0ef6534394a68019ec8ebd8 (branch todolist-push),
against its parent bf3c939741f86c6c639c730882f8a4f721265a74.
Code changes in tests/realistic/run_batch3.py; the plan got an
md5-line update (fix-pass-3 values to fix-pass-4 values), an F3
attribution fix, an F5 record fix and an H4 U11 parenthetical;
the log got fix-pass-4 adjudication corrections (F3 attribution,
F5 outcome, "72" explanation, U3/U4 label, env note) plus the
fix-pass-5 adjudication and verification sections. Method: my own
differential probe (/tmp/y14b-fix5-c1-probe.py, 63 checks, old
blob 585fb801 vs new blob ff4a5358 loaded side by side, plus 3
live cases against /proc); re-ran the author's fix5 probe plus
the full regression set myself, counting PASS lines only; tested
my two fix sketches on a scratch copy of the new blob
(/tmp/y14b-c1-fix5-scratch.py, NOT committed, NOT in the repo)
and re-ran everything against it; re-derived the H4 arithmetic
with Decimal; re-checked every doc claim by grep against the
tree at 46e0909 and at HEAD. No Zen driving, no ydotool, no live
browser work, no code edits.

## Verdict: AMEND

Fix pass 5 closes every fix-pass-4 finding it claims to close,
and the full regression set stays green. But it introduces two
new LOW regressions, both fail-open (a real runner or codex
form goes from True in fix4 to False in fix5), both reproduced
live by me. By the redteam's own standard ("a fix pass must not
erode the previous pass", R2), that blocks ship until fixed.
Both fixes are small, both are specified below, and both are
proven in my scratch copy: with the two sketches applied, my
63-case probe goes from 57 to 61 PASS (the 2 remaining "FAIL"
lines are stale live expectations, the scratch returns the fixed
True), and every regression probe stays green. Live impact of
both regressions is nil (the leaf process is still caught live
in every case), so this is AMEND, not BLOCK. Ship after fix
pass 6 applies C5-1 and C5-2 and re-probes (my probe 63/63,
fix5 probe 38/38, regressions green).

## Hash record (verified by me)

- Commit 46e0909058af1419c0ef6534394a68019ec8ebd8.
- run_batch3.py at 46e0909: git blob
  ff4a5358ac7f621a1fd649c36cec94da2031399d, md5
  9e99d9aa1bcdbb525407adfb31e0692b. Parent bf3c939: blob
  585fb8016b0618ab02b3e97afa362dbcce7342c9, md5
  2920f1697edb3b33711b83b8a874d88b. Both re-derived by me from
  `git show <commit>:tests/realistic/run_batch3.py | md5sum` and
  `git hash-object --stdin` (see appendix). Working tree still
  hashes ff4a5358 / 9e99d9aa at 23:17 +07.

## Verification re-runs (PASS lines counted only, not the "FAILURES:" summary line)

All against the new blob ff4a5358 unless noted. Every probe
exited 0 except where stated.

- My differential probe /tmp/y14b-fix5-c1-probe.py: 57/63 PASS
  on fix5 (6 FAIL: 5 unit regressions + 1 helper root cause,
  listed under C5-1/C5-2); 61/63 on the scratch copy, the 2
  remaining "FAIL" lines being stale live expectations (see
  scratch section below).
- Author fix5 probe /tmp/y14b-fix5-probe.py: 38/38 PASS.
- Fix4 probe /tmp/y14b-fix4-probe.py: 64/64 PASS.
- Fix3 probe /tmp/y14b-fix3-probe.py: 70/70 PASS.
- Fix2 probe /tmp/y14b-fix2-probe.py: 31/31 PASS.
- H2 probe /tmp/y14b-h2-probe.py: 45/45 PASS on the clean
  re-run. First run was 44/45 with one FAIL ("live hits exactly
  the dummies + their wrappers"); the RESULT line named foreign
  pids (215335 sudo -n bash, 215360 codex, and other dummy
  runners) from a concurrent worker's live probe, i.e.
  Council 2 INFO-4 concurrency pollution, not a fix5 failure.
  Re-ran on a quiet VM (ps clean): 45/45, exit 0.
- Transcription /tmp/y14b-transcribe.py: 82 PASS.
- Gate dry /tmp/y14b-gate-dry.py: 4/4 PASS.
- M1 probe /tmp/y14b-m1-probe.py: 3/3 PASS.
- M1 all-12 /tmp/y14b-fix2-m1-probe.py: 4/4 PASS.
- Council 2 extra probe /tmp/y14b-fix4-c2-probe.py: 36/46 PASS,
  10 failures, ALL verified case by case below as
  expected-behavior changes (the fix), not regressions.
- Scratch copy regressions (same driver, same probes): fix5
  38/38, fix4 64/64, fix3 70/70, fix2 31/31, H2 45/45,
  transcription 82, M1 3/3, M1 all-12 4/4, gate dry 4/4, C2
  extra 36/46 (same 10). py_compile OK on old, new and scratch.
- H4 arithmetic re-derived by me with Decimal (see below).

## Findings

### C5-1 (LOW, regression vs fix4, REQUIRED): _top_level_sep_index treats an opening quote as a closing quote

File: tests/realistic/run_batch3.py, _top_level_sep_index
(new blob line 2368). The rule "a separator is top-level
when it appears after the last quote character" cannot tell an
opening quote from a closing one. A token that OPENS a quoted
region (e.g. "'x=1;") has its ";" after the opening quote, and
the helper returns the ";" index as top-level. The ";" is
inside the string, not a shell separator.

Reproduced by me (my probe, old blob vs new blob):

- B5 `bash -c "python3 -c 'x=1; import run_batch3'"`: old
  True, new False. The import IS inside the python -c string.
- B6 `bash -c "codex -c 'x=1; marionette'"`: old True, new
  False. The marker IS inside the codex -c snippet.
- B7 `bash -c "codex -c 'a=1; echo marionette'"`: old True,
  new False. Same shape.
- Helper directly: `_top_level_sep_index("'x=1;")` returns 4,
  want -1. Controls pass: "'hello';" returns 7, "os';" returns
  3, "time;" returns -1, standalone ";" returns 0.
- Live (my probe, dummy codex on PATH, compound form so the
  wrapper stays alive): wrapper `bash -c codex -c 'x=1;
  marionette'; sleep 60` is in old _scan_other_runners hits
  and absent from new hits. Old True, new False, live.

Why it happens: in the wrapped form the quotes survive inside
the bash -c string token, so the first snippet token carries
the opening quote ("'x=1;"). The direct form is unaffected
(my B30 `python3 -c 'x=1; import run_batch3'` with real /proc
argv, no quotes, stays True in both blobs; the F2 case stays
True because its ";" sits in the quoteless middle token
"time;"). The miss needs the ";" glued to the snippet's FIRST
word, which is contrived, and live impact is nil: the leaf
`python3 -c x=1; import run_batch3` process (clean argv, no
quotes) is caught in both blobs, and a real codex binary's own
argv has no quotes either. But it is a genuine True to False
erosion introduced by fix5, in the fail-open direction, so it
must be fixed, not recorded.

Required fix (sketch, proven in my scratch copy): in
_top_level_sep_index, a token that starts with a quote and
holds only one quote of that kind OPENS a region, so return
-1 for it:

```
if tok[0] in ("'", '"') and tok.count(tok[0]) == 1:
    return -1
```

placed after the last_quote computation. I checked the
neighbours by hand: "'hello';" (two quotes) still returns 7,
"os';" (no leading quote) still returns 3, "time;" still -1,
"'a'&&" still 3, the documented "'a';'b;c'" limitation stays
missed. With this sketch plus C5-2, my probe is 61/63 (the 2
live "FAIL" lines are stale expectations: the scratch returns
True where fix5 returned False, which is the fix) and all
regressions stay green.

### C5-2 (LOW, regression vs fix4, REQUIRED): _owning_command does not skip flag VALUES

File: tests/realistic/run_batch3.py, _owning_command (new blob
line 2340). The walk-back skips flags, VAR=value
assignments and path arguments, but not a flag's VALUE. A bare
word sitting between a flag and the -c is returned as the
owning command. Redteam U1 said to walk back "ONLY past
argument-like tokens: flags, VAR=value assignments, and path
arguments"; a flag value is argument-like and is not skipped.

Reproduced by me (my probe, old blob vs new blob):

- B1 `bash -o pipefail -c run_batch3.py`: old True, new
  False. _owning_command returns "pipefail".
- B22 `bash -o pipefail -c codex exec marionette`: old True,
  new False (via _codex_at_command calling _c_is_shell).
- Live (my probe, executable stub /tmp/run_c1_stub.py):
  wrapper `bash -o pipefail -c /tmp/run_c1_stub.py & sleep 60`
  is in old _scan_other_runners hits and absent from new hits.
  Old True, new False, live. The leaf python stub is caught in
  both blobs, so live impact is nil.
- Controls that pass: `bash --rcfile /tmp/x -c` True (a path
  value is already skipped by the path rule), `sudo -u root
  bash -c` True, `env -u FOO bash -c` True, `flock -w 5
  /tmp/l bash -c` True, `nice -n 5 bash -c` True (in all of
  these the shell token sits directly before the -c, so the
  walk-back never reaches the flag value).

Required fix (sketch, proven in my scratch copy): in
_owning_command, skip a bare word that follows a flag, UNLESS
its basename is a known command (so "bash" after "-i" in "env
-i bash -c" is still the command):

```
base = tok.rsplit("/", 1)[-1]
if j > 0 and tokens[j - 1].startswith("-") and \
        base not in _KNOWN_COMMANDS:
    j -= 1
    continue
```

placed before the path-argument skip. The "unless known"
clause matters: a naive version (skip any bare word after a
flag) breaks A5 `env -i bash -c`, which I caught while testing
the sketch. Residual, disclosed: a flag value whose basename
is exactly a known command (e.g. an init file literally named
"python3") would still be returned as the owner; that form is
contrived and the redteam's own path rule has the same shape,
so it is a record, not a fix.

### C5-3 (minor, doc, CLOSED at HEAD): C3-5 was half-applied in 46e0909

The fix-pass-5 adjudication (log lines 1039-1042 at 46e0909)
states the true fix4 probe breakdown (R1 6, F1 5, F3 9, F4 3,
F5 2, regressions 14, codex 21, live 4 = 64) and says "The log
said F3 x8 and regressions x17", implying the correction was
applied. But log line 667 at 46e0909 still read "F3 x8 ...
regressions x17". I verified the true numbers myself by
counting the probe source: R1 6, F1 5, F3 9 (probe lines
52-68), F4 3, F5 2, regressions 14 (lines 89-118), codex 21,
live 4; 6+5+9+3+2+14+21+4 = 64, and AST count confirms cases
39 + codex_cases 21 + live 4 = 64. So the adjudication's
"C3-5 fixed" claim was inaccurate as of 46e0909. Council 3's
fix-pass-5 review caught the same gap, and the author applied
required fix U-C3-5b in commit b9cd0f0 (log line 667 now reads
"F3 x9 ... regressions x14"). Closed at HEAD; no action left.
Recorded so the 46e0909 claim is not trusted as-is.

### C5-4 (minor, doc/process, CLOSED at HEAD): the plan pin in 46e0909 still pointed at fix-pass-4 values

At 46e0909 the plan's md5 procedure (lines 614-615) pinned
the fix-pass-4 values (md5 2920f169, blob 585fb801, commit
bf3c939), not the fix-pass-5 file the commit itself ships.
That is the same C1-2 pattern one pass later: following the
procedure as written at 46e0909 false-refuses the fix-pass-5
runner. The author fixed it in the follow-up commit 8a99ea0
(plan now pins md5 9e99d9aa, blob ff4a5358, commit 46e0909,
with the fix-pass-4 values labeled "Supersedes the
fix-pass-4 values"), and the log has the superseding fix-pass-5
entry. I re-checked C1-2 independently at HEAD: grep for
e9e3519a/3a9b7b17 in the plan returns nothing; the only
fix-pass-4 values in the plan are the labeled superseded ones.
C1-2 is closed in the live tree. Process note for the next
pass: pin the NEW values IN the fix commit, not in a
follow-up, since C1-2's ship-blocking logic applies to the
fix commit itself.

### C5-5 (minor, doc): "A1-A14" is a phantom label

The adjudication and verification plan say "the redteam's
A1-A14" and "A1-A14 all PASS". The redteam paper defines only
A1-A9 (env, sudo, timeout, nice, env -i, /usr/bin/env, env
codex, sudo codex, dash); its U1 text mentions "A1 to A14"
without defining A10-A14. The fix5 probe covers all 9 redteam
cases plus 7 more R2 cases (16 R2 unit cases total: 14 runner
+ 2 codex), so the coverage is there, but the label is wrong.
Correct it to "A1-A9 plus 7 further wrapper cases".

### C5-6 (minor, probe): the fix5 probe's URL case is vacuous

/tmp/y14b-fix5-probe.py, "URL with & stays intact (not
split)": the cmdline is just `python3 run_batch3.py` (no URL,
no "&" anywhere), so the case passes without testing anything.
The behaviour itself is fine: my B15 (`python3 run_batch3.py
http://x/?a=1&b=2`) returns True in both blobs, and the code
never checks "&" in tok (exact-match tuple only, in both
_is_cmd_separator and _same_command_tokens). Strengthen the
case to a real URL or rename it; no code change.

### C5-7 (INFO, record): direct-form codex "&" still True, recorded in the log only

`codex --help & echo marionette` with no bash -c wrapper
returns True in both blobs (my B17). The author records it in
the log verification section as a synthetic-only residual
("the shell splits & before exec, so a codex process never has
& in its argv"), which is correct, and it matches the
redteam's pre-existing I4 class. But no code docstring carries
it. One line in the _same_command_tokens docstring would close
it; not ship-blocking.

### C5-8 (INFO, mechanism): the C2-extra L6 flip is the C2-1 fix through bash exec optimisation

The C2-extra probe's "live double-nested wrapper missed"
case now returns True. I traced why: the raw double-nested
cmdline (`bash -c "bash -c '<stub>; sleep 60'"`) still
returns False in fix5 (direct unit test by me), but live the
outer bash exec-replaces itself with the inner bash, whose
cmdline is `bash -c <stub>; sleep 60`, and that inner wrapper
is now caught by the C2-1 glued-separator fix. So the flip is
the C2-1 fix working, not a change to double-nested handling.
The author's "expected-behavior change" classification is
right; this note just records the mechanism.

## What verified clean (with my own probe counts)

- R2/U1: redteam A1-A9 all True in the new blob (old False
  for all 9); plus env FOO=bar, bash -x, flock -c, sh, plain
  bash all True; python3 -c still False. Live: timeout
  wrapper old False, new True (my probe, leaf caught both).
- R4/C3-3/C1-R1: import guard boundary works: `python3 -c
  'import os'; echo import run_batch3` False, nested bash -c
  form False, direct `python3 -c import x; echo import
  run_batch3` False; `python3 -c 'import os; import
  run_batch3'` still True; `echo import run_batch3` False.
- C2-1: glued separator on the runner token works: `;`, `&&`,
  `||` variants all True (old False), bare `run_foo.py;`
  True, `python3 run_foo.py;` True, `md5sum run_foo.py;`
  still False. Live L5 form confirmed via the C2-extra
  probe mechanism (see C5-8).
- C2-2: bare "&" is a separator: `python3 --version &
  pytest -W ignore run_batch3.py` False (old True), `bash -c
  "codex --help & echo marionette"` False (old True); real
  URL with "&" still True (my B15).
- R3/C1-R4: quote-aware codex -c bound works: B1/B2 False
  (old True), F2 `codex -c 'import time; x # marionette'`
  still True, direct `codex -c marionette` True.
- C3-2/C1-R2 residual recorded and true: `python3 other -W
  ignore run_batch3.py` still True in both blobs, now stated
  in the _python_executes docstring and the _is_runner_cmdline
  known limitations. The code fix stays deferred, as
  adjudicated, with the reason (needs flag-value tracking)
  stated.
- C1-R3 recorded and true: glued `;codex` still False in both
  blobs, now in the known limitations.
- F5 record: `python3 run_other -W ignore run_batch3.py`
  False in the new blob (old fix4 blob also False; the True
  was fix-pass-3), and False is correct; the plan F5 bullet
  (line 739 at 46e0909, 740 at HEAD) and the log F5 bullet
  (line 603) now say False.
- F3 attribution: plan and log now say the redteam's -m
  example was `python3 other.py -m run_batch3`; I checked the
  redteam paper bd3c6c9 lines 222-243 as cited and it is
  other.py. `python3 other.py -m run_batch3` False,
  `python3 run_other.py -m run_batch3` True via run_other.py.
- "72" story: corrected to a plain miscount (70+1=71, not
  72); fix3 probe is 70 by my re-run. U-label: the verdict
  section now says U4 (line 527 at 46e0909). Env note: updated with the proper repair and the
  solved root cause (Y13r2 redteam shim A6e, VMFIX c16dd4e);
  `import re` OK, verified by me.
- Fix4 probe label corrected to "now False (was True in
  fix3)" (probe line 83).
- H4 arithmetic re-derived by me with Decimal, model pos =
  (850 + N*R)/100, bound 11: N=3.5 R=2 pos 8.57 margin 2.43;
  N=3.5 R=19 pos 9.17 (9.165 half-up) margin 1.84; N=3 R=2
  margin 2.44; N=3 R=19 margin 1.93; first fail R 71.43 /
  83.33 ms ("roughly 70-85"); sure fail 100.00 / 116.67 ms
  ("~100-117"); 1 round trip at 19 ms = 0.19 ticks; R=50
  pos 10.25 reads 10-11 margin 0-1. All match the plan note.
  Half/half: 3.5-3 = 0.5 and 4-3.5 = 0.5, while 4-3 = 1, so
  the U11 parenthetical is arithmetically honest in both its
  46e0909 form ("leg-precise 3.0 with 4 overcounting by 1, is
  not stated because on the N=3.5 model both 3 and 4 are half
  a round trip off") and its polished HEAD form (b9cd0f0,
  C3-9p: "the operative H4 sentence states the half/half
  position instead of the literal leg-precise clause").
- C2-extra 10 "failures" verified case by case as the fix:
  'sep single & alone' (C2-2), 'c env/nice/sudo bash -c MISS'
  (R2), 'glued; python3 run_foo.py; echo MISS' and 'glued;
  bare run_foo.py; echo MISS' (C2-1), 'codex -c marker in
  LATER shell cmd' (R3), 'codex single & --help & echo FP'
  (C2-2), 'live glued ; wrapper missed' and 'live
  double-nested wrapper missed' (C2-1, see C5-8). Each encodes
  fix-pass-4 behaviour that fix pass 5 corrects; the fix5
  probe covers all 10 with corrected expectations at unit
  level (the two live ones via their unit analogues, not live;
  my probe covers R2 and the B1/B6 regressions live).
- t10: the fix-pass-5 diff has 9 hunks, all in the scanner
  region (run_batch3.py lines 2311-2738); zero t10 or
  threshold mentions in the diff; no threshold changed by
  construction (fix pass 5 is guard-only).
- Scratch copy (my two sketches on the new blob): my probe
  61/63 PASS with 0 unit FAILURES (the 2 live "FAIL" lines
  are stale expectations, the scratch returns the fixed True
  for the B1 and B6 live wrappers); all regressions green
  (fix5 38, fix4 64, fix3 70, fix2 31, H2 45, transcription
  82, gate dry 4, M1 3, M1 all-12 4, C2 extra 36/46 same 10).

## Hygiene

- 0 em dash (U+2014) and 0 en dash (U+2013) in the full
  46e0909 diff (counted in Python, not grep -P).
- "ydotool" appears twice in the diff, both times as the words
  "no ydotool" in hygiene statements, not usage.
- The only email in the diff is the noreply GitHub author
  address (phamTuan207);
  no other personal info.
- No live Zen driving, no browser work. All stubs I spawned
  were killed and verified gone by ps (exact-PID kills; one
  pkill -f matched my own exec shell's cmdline and killed
  that shell only, no repo or review state affected, and I
  switched to exact-PID kills after it).
- One process note: a foreign worker's live probe (fix5-c2,
  dummy codex and run_foo stubs) ran concurrently during part
  of my regression runs; I killed none of its processes, and
  my H2 clean re-run was done on a quiet VM.

## Unblock conditions for fix pass 6

- U-C5-1 (REQUIRED): fix _top_level_sep_index for the
  opening-quote case (sketch in C5-1). Re-probe must show my
  B5/B6/B7 True and the tls "'x=1;" case -1, with R3 B1/B2
  still False and F2 still True.
- U-C5-2 (REQUIRED): fix _owning_command to skip flag values
  (sketch in C5-2, with the known-command guard so A5 keeps
  passing). Re-probe must show my B1/B22 True, with A5
  `env -i bash -c` still True and `python3 -X dev -c` still
  False.
- U-C5-3..C5-8: doc/probe notes only; C5-3 and C5-4 are
  already closed at HEAD (b9cd0f0, 8a99ea0). Apply C5-5
  (label), C5-6 (URL case) and C5-7 (one docstring line) in
  fix pass 6 or record them; none blocks ship on its own.

## Appendix: timed work log (Asia/Ho_Chi_Minh, 21/11)

- 23:06 +07: review starts. Hashes verified by me: commit
  46e0909, new blob ff4a5358 md5 9e99d9aa, old blob 585fb801 md5
  2920f169 (git show + md5sum + hash-object, all match the task
  brief). Old and new blobs extracted to /tmp/y14b-c1-fix5-old.py
  and /tmp/y14b-c1-fix5-new.py; py_compile OK on both.
- 23:06 +07: MEMORY.md changed under me (Zen keybinds probe
  result 23:05 commit 81a3bc4, MERGE DONE + GRAPH 456). Noted,
  unrelated to this review, no action.
- 23:07 +07: wrote my differential probe /tmp/y14b-fix5-c1-probe.py
  (63 checks: R2 A1-A9, controls, 36 of my own edge cases, 8
  _top_level_sep_index unit checks, 3 live cases). First run
  failed to load (run_live import); fixed with sys.path.
- 23:08 +07: probe run 1: 6 FAIL (B1, B5, B6, B7, B22, all old
  True new False, plus the tls root cause: 'x=1; returns 4,
  want -1). Live section returned empty hits: my stub was named
  y14b-c1-run_stub.py, whose basename does not start with run_,
  so nothing matched.
- 23:09 +07: one pkill -f matched my own exec shell cmdline and
  killed that shell (known footgun, redteam noted the same).
  No repo or review state affected. Switched to exact-PID kills
  and [r]un pattern ps checks.
- 23:10 +07: renamed stub to /tmp/run_c1_stub.py (basename
  run_c1_stub.py). Direct unit check: timeout wrapper True,
  pipefail wrapper False in the new blob. Isolated live test:
  _scan_other_runners finds timeout wrapper, bash wrapper and
  leaf. Probe run 2: 54 PASS, same 6 FAIL, 3 live FAIL (my wrap
  check used `in` on a (pid, flat) tuple, always False; B6
  wrapper exec-vanished). Fixed the tuple check to h[1] and
  made B6 a compound (`...; sleep 60`) so the wrapper stays
  alive.
- 23:12 +07: probe run 3 (clean): 57 PASS, 6 FAIL (same 5 unit
  regressions + tls root cause). All 3 live PASS and confirm the
  hypotheses: R2 timeout wrapper old False new True; B1 pipefail
  wrapper old True new False; B6 codex wrapper old True new
  False. Leaf python stub caught in both blobs in all runner
  cases. Killed the leftover detached stub tree by exact PID
  (213957/213959/213960); verified gone by ps -p.
- 23:13 +07: built scratch copy /tmp/y14b-c1-fix5-scratch.py
  (new blob + my two sketches). First scratch run used the
  wrong loader (my probe loads old/new itself, so the driver
  pre-seed had no effect); reran with a probe copy pointing
  NEW at the scratch file.
- 23:13 +07: scratch probe run: 61 PASS, 0 unit FAILURES; the
  2 live "FAIL" lines are stale expectations (scratch returns
  the fixed True for B1/B6 live wrappers). While drafting the
  S2 sketch I caught that a naive flag-value skip breaks A5
  (`env -i bash -c`); added the known-command guard.
- 23:14 +07: regression set re-run by me against the new blob:
  fix5 38/38, fix4 64/64, fix3 70/70, fix2 31/31, transcribe
  82, M1 3/3, M1 all-12 4/4, C2 extra 36/46 (10 failures, all
  the fix, verified case by case), H2 44/45 (one FAIL, foreign
  pids 215335/215360 in the RESULT line: concurrent worker
  pollution). MEMORY.md changed under me (F3 DONE + SLOT
  RE-WEDGED). Noted, unrelated, no action.
- 23:14 +07: traced the C2-extra L6 flip: raw double-nested
  cmdline still False in fix5 (direct unit test); live the
  outer bash exec-replaces itself with the inner bash, which
  the C2-1 fix catches. Mechanism recorded as C5-8.
- 23:15 +07: VM quiet (ps clean). H2 clean re-run 45/45, exit
  0; gate dry 4/4. Regression set against the scratch copy:
  fix5 38, fix4 64, fix3 70, fix2 31, H2 45, transcription 82,
  M1 3, M1 all-12 4, gate dry 4, C2 extra 36/46, all exit 0
  except C2 extra (exit 1, same 10). A foreign worker's
  fix5-c2 probe ran concurrently; left its processes alone.
- 23:16 +07: H4 re-derived with Decimal (all numbers match the
  plan note; U11 parenthetical honest in both forms). Doc
  checks: plan pin at HEAD is fix5 values (8a99ea0), fix4
  values labeled superseded; log line 667 at 46e0909 still
  x8/x17 (C3-5 half-applied), fixed at HEAD by b9cd0f0;
  fix4 probe label corrected; breakdown numbers confirmed by
  source count (F3 9, regressions 14, total 64).
- 23:17 +07: t10 check (9 hunks, all scanner region, zero
  t10/threshold mentions) and hygiene (0 em/en dash in
  Python count; ydotool only as "no ydotool" x2; only email
  is the noreply author address). Working tree still
  ff4a5358 / 9e99d9aa. Paper written, verdict AMEND.
- 23:19 +07: final self-check of the paper before commit:
  0 em/en dash in the paper file; corrected three line
  citations to version-precise numbers (plan F5 739 at
  46e0909 / 740 at HEAD, log F5 603, U4 line 527 at 46e0909,
  _owning_command line 2340, _top_level_sep_index line 2368).
  Committing only the paper file now.

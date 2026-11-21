# Y14b fix-pass-2 redteam review

## Verdict: AMEND

No BLOCK-grade accidental form found: every documented fleet launch form
is caught, and every escape below needs a deliberate spelling no fleet
launcher uses. But fix pass 2's headline claim is incomplete. The combined
short-flag spelling of joined `-m` (and of `-c`) executes a runner and
escapes the gate entirely (F1), the `-W`/`-X` two-back rule adds a new
false-positive class the log says does not exist (F3), the codex anchor
records only one wrapper gap while seven more escape live (F4), and the H4
restatement still quotes floor values (F6). All of it is small to fix or
record; none of it needs a redesign. Ship waits for the U1-U7 items below,
with U1 the only one I recommend as a code fix rather than a recording.

## Scope

Fix-pass-2 diff ONLY: commit `ad085d9` vs its parent `8bee524`, plus
`e97bcf6` (hash record only). I did not re-review the original re-stage
(`f732d6a`) or fix pass 1 (`8bee524`); those verdicts stand. Branch note:
`todolist-push` moved while I worked (HEAD is `915121d`, a Y6e commit);
`tests/realistic/run_batch3.py` is byte-identical between `ad085d9` and
HEAD (0-line diff), so all line numbers below are valid at both commits.
The `e97bcf6` record verifies exactly: `git show
ad085d9:tests/realistic/run_batch3.py` gives blob
`e604c01229933194d40a4a3f75c54a8b13a46f78` and md5
`5d52ac65e8fe1d666d26c7f3ece4d7ba`, matching the log entry.

## Method and evidence contract

Independent review, no subagents, no live Zen driving, no ydotool. Every
finding below was reproduced by me with stub processes (a stub
`run_batch3.py` / `run_tests.py` / `foo.run_batch3` that prints and sleeps),
fake HTTP servers built from git blobs at `1d23532`, unit cmdlines, and
live `/proc` dummies (a compiled sleeper launched with `exec -a` so its
argv is exact). I did not trust the fix log's probe claims; I re-ran my
own probes. Probe commands and outputs are in the appendix. Counts below
are my predictions confirmed, so a "PASS" on a false-positive case means
the false positive exists as predicted, not that the code is correct.

Probes: `/tmp/y14b-fix2-rt-probe.py` (final run 125 pass, 0 fail: 99 unit
+ 26 live), `/tmp/y14b-fix2-rt-probe1b.py` (combined `-m`, 11 cases),
`/tmp/y14b-fix2-rt-probe1c.py` (combined `-c`, 4 cases),
`/tmp/y14b-fix2-rt-m1.py` (served fixture, 9 server cases),
`/tmp/y14b-fix2-rt-plan.py` (plan md5 procedure + H4 arithmetic).
Two harness artifacts, both re-checked clean and noted honestly: in one
probe run the double-nested case showed leaf-hit True with ran False
because the previous run's leaf had been orphaned (`p.kill()` kills only
the flock parent); a clean re-run with a fresh lock confirms the leaf is
caught (pid 177450). In probe 1b my needle `STUB run_batch3` missed the
dotted stub's `STUB foo.run_batch3` line; re-checked with the correct
needle, it executes and is missed.

## What the fix does correctly (verified, not trusted)

- V1, joined and dotted `-m`: `python3 -mrun_batch3`,
  `python3 -m foo.run_batch3`, `python3 -mfoo.run_batch3` all execute the
  stub live and are caught by `_scan_other_runners`. `foo.run_tests`
  stays False: the dotted stub ran live and the scan missed it, which is
  correct, since `run_tests` is not a runner.
- V2, spaced `-W`/`-X`: `python3 -W ignore run_batch3.py` and
  `python3 -X dev run_batch3.py` execute the stub live and are caught.
- V3, codex false positives fixed live: `grep -rn marionette codex`,
  `cat codex marionette-notes.txt`, and `bash -c "echo codex
  marionette"` all return False at unit level and are missed by the live
  scan, while `codex marionette`, `/usr/local/bin/codex marionette`,
  `bash -c "codex marionette"`, `env codex marionette`, and `flock -c
  "codex marionette"` are all caught.
- V4, served fixture, all 12: the mixed server (right t10, foreign t01)
  is refused, as is foreign t09 `detail.html` and a missing
  `prefs.html` (404); the all-matching server passes in 0.04 s.
- V5, plan R1-R4: the ship md5 procedure runs exactly as written from a
  faithful `/tmp/y14-server` layout built from git blobs at `1d23532`
  (see probe 3). The find returns exactly 25 files and all 25 md5s
  match the plan list, 0 mismatches. t09 `detail.html`
  `40dfc0db44aa8448341587f8559b773a` and `prefs.html`
  `1169a1d5a1a6599093bdedac9c2aa74e` verified from blobs. The
  `run_batch3.py` md5 line verifies (`5d52ac65e8fe1d666d26c7f3ece4d7ba`,
  blob `e604c01229933194d40a4a3f75c54a8b13a46f78`, commit `ad085d9`).
  The old fix-pass-1 find path fails as the plan says (`find:
  tests/realistic/clone1-batch3: No such file or directory`, exit 1).
- V6, docstring residuals, all verified: comma-list import (`import os,
  run_foo` misses, `import run_foo, os` hits); dynamic imports
  (`__import__`, `importlib.import_module`, `exec(open(...).read())` all
  miss, `__import__` confirmed live); import-only over-approximation
  (`python3 -c "import run_batch3"` flags, confirmed live);
  extensionless/`.pyc` qualification (`python3 run_batch3` and
  `python3 run_batch3.pyc` miss, `python3 run-nested-pill` and
  `python3 run-nested-pill.pyc` hit); double-nested `-c` removed from
  residuals (leaf `python3 run_batch3.py` caught live, scan hit
  `[(177450, 'python3 run_batch3.py')]`; single-nested `sh -c` is also
  caught at unit level); renamed copy and spoofed argv[0] miss;
  `runpy.run_path` misses; sibling divergence note accurate
  (`launch_y13.py` and `run_codex_y5.py` still use the old substring
  codex test and define neither `_is_runner_module` nor
  `_is_codex_executor`).
- V7, H4 thresholds: first-fail roughly 70-85 ms and sure-fail roughly
  100-117 ms bracket the N=3 to N=3.5 range correctly (see F6 for the
  remaining wording slips). The 850 ms base is right (500 ms sampler +
  350 ms sleep) and the 3.5 midpoint is conservative against my
  leg-precise count of 3.0 round trips (exact-zero return leg 0.5 +
  sampler 1 + after-sampler 1 + advancing request leg 0.5).

## F1 (MEDIUM): combined short-flag `-m`/`-c` forms execute a runner and escape

`run_batch3.py:2305-2309` (joined `-m`) only recognizes a token starting
exactly with `-m`, and `_argv_tokens` only splits an exact `-c` token.
CPython bundles no-value short flags, so a value-taking flag can hide
behind them. Reproduced live with the stub (all execute, all unit False,
all scan-miss):

- `python3 -umrun_batch3`, `-bmrun_batch3`, `-smrun_batch3`,
  `-Emrun_batch3`, `-vmrun_batch3`: stub main runs, scan misses.
- `python3 -um run_batch3` (combined token, spaced module): stub main
  runs, scan misses.
- `python3 -umfoo.run_batch3`: stub main runs, scan misses.
- `python3 -uc "import run_batch3; run_batch3.main()"` and `-bc` with
  the same string: stub main runs, scan misses. Controls pass:
  `python3 -u -mrun_batch3`, `python3 -u -m run_batch3`, and
  `python3 -u -c "import run_batch3; ..."` are all caught.

Why `-Imrun_batch3` does not count: it parses as `-I` + `-m run_batch3`
but isolated mode cannot find a repo-local module (`No module named
run_batch3`), so it cannot execute a fleet runner in practice. And
`-Wmrun_batch3` does not count either: `-W` takes the rest as its value
(`Invalid -W option ignored`), so no `-m` is parsed.

This is the exact area fix pass 2 claimed to close ("joined `-m`
accepted", log F2 FIXED). No fleet launcher uses combined flags, so this
is deliberate-only under the adjudicated accidental-collision threat
model, same class as the dynamic `-c` imports, which is why this is
AMEND and not BLOCK. But it is a direct argv form one token away from a
documented form, and the fix is small and precise: recognize a token
matching `-<no-value-flags>m<module>` and `-<no-value-flags>m <module>`
(value-taking letters `W`, `X`, `c` terminate the flag run), and split a
`-<no-value-flags>c` token in `_argv_tokens`. See U1.

## F2 (LOW): `--check-hash-based-pycs` is a third value-taking option and escapes

`run_batch3.py:2321-2325` whitelists only `-W`/`-X` for the token-two-back
rule. Reproduced live: `python3 --check-hash-based-pycs always
run_batch3.py` executes the stub and the matcher returns False (prev
token is `always`, token two back is the long option, not `-W`/`-X`).
Deliberate-only (no fleet launcher uses this option), same class as F1.
See U2.

## F3 (LOW): the `-W`/`-X` two-back rule has no python-token guard, and false-positives

The adjacent generic flag branch (`run_batch3.py:2319-2320`) requires a
python token earlier in the line. The two-back rule does not. Reproduced
at unit level, all return True although nothing executes the runner:

- `pytest -W ignore run_batch3.py`: a real pytest flag (`-W` takes a
  warning filter), pytest only collects the file.
- `echo -W ignore run_batch3.py`: echo executes nothing.
- `python3 run_other.py -W ignore run_batch3.py`: `run_batch3.py` is an
  argument to another script, not the script being run.

The fix log claims "All three are precise (no new false-positive class)".
That claim is disproven for this rule. Impact is fail-closed and
transient (a pytest run finishes and a re-run passes; a long pytest run
would block the gate until it ends). The same no-guard shape pre-exists
in the `-m` branches (`pytest -m run_batch3`, `echo -m run_batch3`,
`python3 run_other.py -m run_batch3` all return True), but the `-W`/`-X`
instance is new in this diff. See U3.

## F4 (LOW): the codex wrapper escape class is wider than the one recorded gap

`run_batch3.py:2381-2407` accepts `codex` only at argv[0], after `-c`,
or after `env`. The docstring records only sudo as a gap. Reproduced
live with `/proc` dummies (exact argv via a compiled sleeper), all
unit False and scan-miss:

- `nohup codex marionette`, `setsid codex marionette`, `timeout 60
  codex marionette`, `flock /tmp/x codex marionette`, `time codex
  marionette`, `nice codex marionette`, `sudo codex marionette`
  (recorded), `env -i codex marionette`, `env FOO=bar codex
  marionette`, `/usr/bin/env codex marionette` (prev token is the full
  path, not `env`).

The prior round's U3 explicitly suggested a wrapper whitelist (flock,
nohup, env, setsid, timeout). Fix pass 2 implemented only immediate
`env` (and `-c`). None of these is a documented fleet launch form, so
deliberate-only, but the docstring's "Known gap" names sudo as if it
were the gap. Either extend the anchor to a wrapper whitelist (codex is
executable when it is the first non-wrapper token) or record the full
list. See U4.

## F5 (LOW): two new codex false-positive shapes in the anchor itself

- `echo env codex marionette` returns True live (scan hit). The `env`
  check does not verify that `env` is the env command: any argv with
  `env` immediately before `codex` flags, including `env` as an
  argument to another command.
- `bash -c "codex --help; echo marionette"` returns True live (scan
  hit). The `-c` split is whitespace-only, so it ignores shell
  structure: `codex --help` followed by an unrelated `echo marionette`
  in the same `-c` string flags, although no browser is driven.

Both are fail-closed and transient, low plausibility. Note, not a new
finding: `codex --help marionette-notes.txt` also flags, but that is the
pre-existing marker heuristic (any codex argv mentioning a marker), not
something fix pass 2 introduced. See U5.

## F6 (LOW): the H4 restatement still quotes floor values, not phase ranges

Plan L636-655. Recomputed from the model ticks = floor/ceil of
(850 + N*RTT)/100, bound 2..11:

| N | first possible fail | sure fail | cont. margin at 2 ms | at 19 ms |
| --- | --- | --- | --- | --- |
| 3 | RTT > 83.3 ms | RTT >= 116.7 ms | 2.44 | 1.93 |
| 3.5 | RTT > 71.4 ms | RTT >= 100.0 ms | 2.43 | 1.84 |
| 4 | RTT > 62.5 ms | RTT >= 87.5 ms | 2.42 | 1.74 |

The plan's "first fail roughly 70-85 ms" and "sure fail ~100-117 ms"
bracket N=3 to N=3.5 correctly, and the leg-precise count is 3.0, so the
threshold ranges are sane. But the restatement still quotes the
floor/mean: at 19 ms the phase range is 9-10, not "9", so the discrete
margin is 1 in adverse phase, not 2; and the continuous range
1.93-2.44 is the N=3 range, while the stated count is N=3.5 (which
gives 1.84-2.43). The ranges also exclude Council 3's count of 4
(62.5 / 87.5 ms); leg-precise counting shows 4 overcounts by 1 (the
exact-zero request leg sits before the reset, the advancing response
leg after the read), so the honest fix is to say so, not to stretch the
range. The watch item on `positionAdvancingAfterNext` and
`positionAdvancingAfterShuffleNext` still covers the risk, so this is
plan wording only. See U6.

## F7 (INFO, no code change): served-check limits, confirmed and bounded

`run_batch3.py:2572-2620`. The redirect and UA-split defeats from the
prior round still pass the check, as the docstring records (known
limits, not new findings): a server 302ing every path to correct bytes
elsewhere returns True, and a UA-split server returns True while a
browser-UA fetch of the same path returns foreign bytes (both
reproduced). Two further bounds, both confirmed by reproduction:

- The check verifies bytes only, not Content-Type: correct bytes served
  as `text/plain` pass. Fail-visible in the browser (the fixture would
  not execute), not a silent pass.
- The check is point-in-time, same class as the F7 mid-test window:
  verify returned True, then the served file on disk was replaced and a
  browser fetch returned foreign bytes with no re-check. A concurrent
  re-stage between gate and test is the non-adversarial form of this.

What it does cover: the 12-file set is complete. Every fixture at
`1d23532` is self-contained (no `src`, `href`, `fetch(`, or `import` in
any `fixture.html`), and t09 opens `detail.html` and `prefs.html` via
`window.open`, both checked. A slow server (6 s per file, correct
bytes) refuses fail-closed after 5.0 s, and the check fails fast on the
first bad file, so the worst-case stall is about 5 s, not 60 s. No
non-adversarial defeat found beyond the recorded limits and the
point-in-time nature. See U7 (record only).

## F8 (INFO): bare-vs-dotted asymmetry, and one verified edge

Bare `-m` flags ANY `run_*` module (`python3 -m run_tests` and
`-mrun_tests` both execute a non-runner stub live and flag), while
dotted `-m` requires exact runner names (`foo.run_tests` correctly
misses). The asymmetry is by design (prefix rule, documented in
`_is_runner_module`), and no file named `run_tests*` exists in the
repo, so the bare false positive is theoretical today; the top
docstring's "dotted only for exact runner module names" does not note
that the bare form is looser. One edge verified, not a finding:
`python3 -m run_batch3.py` DOES execute (CPython accepts the `.py`
suffix) and IS caught, via the generic flag branch rather than the
`-m` branch. Record both in the docstring if U1 is done by recording.

## Unblock conditions

- U1 (F1): recognize combined short-flag `-m` and `-c` forms in
  `_is_runner_cmdline` / `_argv_tokens` (flag run of no-value letters
  before `m`/`c`; value-taking letters `W`, `X`, `c` terminate it), or
  record the class as a residual with the precise mechanism. Re-prove
  live: `-umrun_batch3`, `-um run_batch3`, `-uc "import run_batch3;
  run_batch3.main()"` must then be caught, and `-Wmrun_batch3` must
  still not flag as `-m`.
- U2 (F2): extend the two-back rule to `--check-hash-based-pycs`, or
  record it as a residual. Re-prove live with the long-option launch.
- U3 (F3): add a python-token guard to the `-W`/`-X` two-back rule (and
  consider the same for the `-m` branches), or record the false-positive
  class in the docstring. Re-prove: `pytest -W ignore run_batch3.py`
  and `echo -W ignore run_batch3.py` must no longer flag, while
  `python3 -W ignore run_batch3.py` still does.
- U4 (F4): extend `_is_codex_executor` to a wrapper whitelist (codex
  is executable when it is the first non-wrapper token), or record the
  full wrapper list (nohup, setsid, timeout, flock-direct, `env` with
  options/assignments, full-path env, time, nice, sudo) in the
  docstring. Re-prove live with the `/proc` dummies.
- U5 (F5): record the `env`-as-argument and semicolon-split
  false-positive shapes in the `_is_codex_executor` docstring, or
  tighten them. Re-prove: `echo env codex marionette` and `bash -c
  "codex --help; echo marionette"` must no longer flag.
- U6 (F6): restate the H4 note with phase ranges (8-9 at 2 ms, 9-10 at
  19 ms; discrete margin 2 in favorable phase, 1 in adverse phase at
  19 ms; continuous 1.84-2.43 at N=3.5) and say Council 3's count of 4
  overcounts by 1, or drop it.
- U7 (F7, record only): note the served check's point-in-time nature
  in the plan/log, same class as the mid-test window.

## Hygiene

`py_compile` passes on the file at `ad085d9`. The runner diff
`8bee524..ad085d9` has 0 em dash, 0 en dash, 0 mentions of ydotool, no
personal info. No live Zen driving was done for this review.

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 21:48: task received. Fetch origin, confirm HEAD `e97bcf6` on
  `todolist-push`, read the fix-pass-2 diff (7 files, runner file
  +131/-52) and the adjudication in the re-stage log.
- 21:51-21:54: verified `e97bcf6` blob/md5, sibling divergence, fixture
  references (self-contained, t09 `window.open`), t10 advancing path
  and `start_server` reuse behavior.
- 21:54-22:00: wrote probe 1 (125 cases), compiled the sleeper,
  first full run. Two of my own expectations were wrong and corrected
  with evidence: single-nested `sh -c` IS caught (only the
  double-nested flock wrapper is False at unit level), and `python3 -m
  run_batch3.py` DOES execute.
- 22:00-22:05: combined-flag probes 1b/1c (11 + 4 cases). Found F1
  (`-umrun_batch3`, `-um run_batch3`, `-uc` import) and F2
  (`--check-hash-based-pycs`). Clean re-test of the double-nested
  leaf (pid 177450) after an orphan artifact in one run.
- 22:00-22:02: probes 1b/1c, double-nested clean re-test, probe 2,
  probe 3, final probe 1 re-run (125 pass, 0 fail).
- 22:02-22:04: paper written, committed, pushed, verified.

## Appendix: key reproduction excerpts

Probe 1 final: `UNIT: 99 pass, 0 fail`, `TOTAL: 125 pass, 0 fail`
(`/tmp/y14b-fix2-rt-probe1-final.log`).

```
live joined-m: pid=177124 ran=True hit=True hits=[(177124, 'python3 -mrun_batch3')]
live joined-dotted-m: pid=177125 ran=True hit=True hits=[(177125, 'python3 -mfoo.run_batch3')]
live dotted-m-run_tests: pid=177129 ran=True hit=False hits=[]
live W-ignore: pid=177130 ran=True hit=True hits=[(177130, 'python3 -W ignore run_batch3.py')]
live double-nested: ran=True leaf-hit=True hits=[(177146, 'python3 run_batch3.py')]
live-dummy nohup-codex: pid=177148 cmdline='nohup codex marionette' hit=False
live-dummy env-i-codex: pid=177149 cmdline='env -i codex marionette' hit=False
live-dummy fullpath-env-codex: pid=177156 cmdline='/usr/bin/env codex marionette' hit=False
live-dummy echo-env-codex-fp: pid=177161 cmdline='echo env codex marionette' hit=True
live-dummy bash-c-codex-help-echo: pid=177162 cmdline='bash -c codex --help; echo marionette' hit=True
live-dummy grep-fp-fixed: pid=177160 cmdline='grep -rn marionette codex' hit=False
```

Probe 1b (combined `-m`, stub prints `STUB run_batch3 main running`):

```
um-joined: argv=['python3', '-umrun_batch3'] executes=True unit=False scan-hit=False
bm-joined: argv=['python3', '-bmrun_batch3'] executes=True unit=False scan-hit=False
sm-joined: argv=['python3', '-smrun_batch3'] executes=True unit=False scan-hit=False
Em-joined: argv=['python3', '-Emrun_batch3'] executes=True unit=False scan-hit=False
vm-joined: argv=['python3', '-vmrun_batch3'] executes=True unit=False scan-hit=False
um-spaced: argv=['python3', '-um', 'run_batch3'] executes=True unit=False scan-hit=False
u-mrun: argv=['python3', '-u', '-mrun_batch3'] executes=True unit=True scan-hit=True
Wm-joined: argv=['python3', '-Wmrun_batch3'] executes=False unit=False
Im-joined: argv=['python3', '-Imrun_batch3'] executes=False unit=False
um-dotted-joined: argv=['python3', '-umfoo.run_batch3'] executes=True unit=False scan-hit=False
```

Probe 1c (combined `-c`):

```
uc-import: argv=['python3', '-uc', "import run_batch3; run_batch3.main()"] executes=True unit=False scan-hit=False
bc-import: argv=['python3', '-bc', "import run_batch3; run_batch3.main()"] executes=True unit=False scan-hit=False
u-c-spaced: argv=['python3', '-u', '-c', "import run_batch3; run_batch3.main()"] executes=True unit=True scan-hit=True
```

Probe 2 (served fixture, disk root from `1d23532`, 37 files):

```
matching (all 12 correct): verify=True elapsed=0.04s PASS
redirect to correct bytes (known limit): verify=True elapsed=0.02s PASS
mixed right-t10 foreign-t01: verify=False elapsed=0.0s PASS
mixed foreign t09 detail.html: verify=False elapsed=0.01s PASS
missing prefs.html (404): verify=False elapsed=0.01s PASS
UA-split server (known limit): verify=True elapsed=0.01s PASS
slow server 6s/file (correct bytes): verify=False elapsed=5.0s PASS
slowish server 0.3s/file (correct): verify=True elapsed=3.63s PASS
correct bytes, text/plain MIME: verify=True elapsed=0.02s PASS
UA-split browser-UA fetch of t01 = b'<html>FOREIGN</html>' (foreign=True)
TOCTOU step 1: verify before swap = True (elapsed 0.01s)
TOCTOU step 2: browser fetch after swap = b'<html>FOREIGN</html>' (foreign=True, check already passed)
```

Probe 3 (plan md5): find returns 25 files, plan entries 25, md5
mismatches none, `ALL 25 MATCH`. `md5sum run_batch3.py` from
`/tmp/y14-server` gives `5d52ac65e8fe1d666d26c7f3ece4d7ba`, blob at
`ad085d9` is `e604c01229933194d40a4a3f75c54a8b13a46f78`. Old find path
exits 1 with `No such file or directory`. H4: N=3 first possible fail
RTT > 83.3 ms, sure fail >= 116.7 ms; N=3.5 first possible fail
> 71.4 ms, sure fail >= 100.0 ms; N=4 first possible fail > 62.5 ms,
sure fail >= 87.5 ms; continuous margins 2.44/1.93 (N=3), 2.43/1.84
(N=3.5) at 2/19 ms.

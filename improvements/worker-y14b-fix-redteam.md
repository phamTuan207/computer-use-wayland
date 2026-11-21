# Y14b fix-pass redteam review

- Verdict: **AMEND**
- Scope: fix commit `8bee524` (its own diff only) plus `ebe5853` (log hash record only),
  on branch `todolist-push`, repo `~/workspace/computer-use-wayland`.
- Reviewer: independent redteam, worked directly, no subagents, no Zen driving.
- Date: 21 Nov 2026, work 21:33-21:47 +07.

## Scope note

The task described the fix diff as "`8bee524` vs its parent `f732d6a`".
That is not the actual parentage: `8bee524`'s parent is `431b2a9`, and the
range `f732d6a..8bee524` also contains unrelated commits (S1/S2 scrapling,
Y6d launcher, Y13f fixes). I reviewed only `8bee524`'s own diff (3 files:
`tests/realistic/run_batch3.py`, `improvements/worker-y14-batch3-live-plan.md`,
`improvements/worker-y14b-restage-log.md`) plus `ebe5853`. Nothing else in the
range was judged.

## Method and evidence contract

Every finding below was reproduced by me, with the reproduction shown. I did
not trust the fix log's verification claims; I re-ran my own probes.

- Probe 1: `/tmp/y14b-fix-redteam-probe.py`, run 21:39:26 +07, wall 31.1 s,
  log `/tmp/y14b-fix-redteam-probe.log`. Unit batteries on exact NUL-separated
  cmdlines, real stub-module executions (`python3 -m` / `python3 -c` against
  stub modules that only print and sleep, never drive anything), live `/proc`
  argv shapes via a compiled argv-ignoring sleeper, loopback HTTP servers on
  ports 18771-18777, and `run_one` tests with a raising/fake WD.
- Probe 2: `/tmp/y14b-fix-redteam-probe2.py`, wall 7.4 s, log
  `/tmp/y14b-fix-redteam-probe2.log`. Exact-argv codex cases, double-nested
  `-c` live, moved-assert source positions.
- No Zen was driven, no geckodriver, no browser, no ydotool, no em/en dash
  in the fix diff (grep 0, re-checked), no personal info in the reviewed diff.
- Probe 1 first scored 95/101; the 6 mismatches were a harness bug of mine
  (`/usr/bin/yes` parses dash-leading argv as options and exits, so those
  dummies were dead before I read `/proc`). Probe 2 re-proved all 6 with a
  compiled sleeper binary and they all pass. All dummies killed; final `ps`
  check showed no strays.

## What the fix does correctly (verified, not trusted)

- `-m` spaced form, `-u -m`, `flock -m`, `env -m`: live stub execution of
  `python3 -m run_batch3` is caught by the matcher and by
  `_scan_other_runners` (probe 1, 1.00 s).
- `-c` import/from/as forms: live stub execution of
  `python3 -c "import run_batch3; run_batch3.main()"` is caught (probe 1).
- Codex old false positive fixed: a single-token argv `codex marionette notes`
  now returns False, live (probe 2). Plain `codex` with no marker returns
  False (warning-only path preserved).
- M1 specified case fixed: a foreign server on the t10 path is refused
  (served md5 `d41f51cdaf04721f80ac17770d6b59fb` vs on-disk
  `eb814c944dab6279417c6182e1950876`), a matching server is accepted, a 404
  server is refused, a hanging server is refused after 5.01 s (timeout 5).
- M2 specified window fixed: with a runner dummy live before `run_one`,
  `run_one` returns INFRA in 1.1 ms with `failures[0]` starting
  `INFRA: live slot busy`, and a `RaisingWD` (raises on instantiation) proves
  no WD session was ever opened (probe 1, 29.76 s).
- Moved now-playing asserts: the `expect_text` multiset of `run_b3_t10` is
  exactly identical to the `expectText` multiset of `check.mjs` at `1d23532`
  (33 calls each, zero runner-only, zero checker-only). The moved asserts sit
  at `run_batch3.py:1610` (plain Next) and `:1749` (shuffle Next), both after
  their `advancing_later` checks; the sampler-to-min-check segments contain
  no `expect_text`. Wrong-track failure path traced and confirmed: advancing
  checks pass, the moved assert records the failure, `Runner.check` never
  aborts (`run_live.py:894-900`), summary `pass` is False. A wrong track
  still FAILS, at the moved assert, only later.
- H4 round-trip count confirmed: pre-fix 5 round trips, post-fix 3
  (sampler 1 + `expect_text` find+text 2 + after-sampler 1 + advancing 1;
  `d.text` is 2 `_wd` calls per `run_live.py:800-802`).
- L1: verified by inspection only (no live WD on the VM): no `int(d.eval` or
  `int(result` remains in `run_batch3.py`; `position()` and
  `exact_zero_next()` return the raw Number. The fixture position is always
  an integer, so no live value changes.
- C3 F1-F7 wording spot-checked: plan L423 says suite copied from main
  `1d23532`; `SUPERSEDED` marked at plan:498; log count corrected 68 to 72;
  stale `pgrep sweep` comment updated at `run_batch3.py:2456`; H2/H3 claim
  withdrawn with reset-only / gain-only language (plan:26-36).
- `ebe5853` hash record verified: `run_batch3.py` blob
  `ed4de81d914f3a75df31554c0b2369110f7e27b0`, md5
  `65818867865ad4772e78cc2bcac015d6`, matches the log.

## F1 (MEDIUM): served-fixture check verifies 1 of 10 fixtures

`run_batch3.py:2515-2545`, called from `main()` at `:2582`. It fetches only
`clone1-batch3/t10-music-player/fixture.html` and compares its md5 to disk.

Reproductions (probe 1, ports 18771-18777, disk root built from `1d23532`):

- Mixed server (correct t10 bytes, FOREIGN t01 bytes): check returns True.
  A direct fetch of the served t01 path returns `b'<html>FOREIGN t01</html>'`.
  The check never fetches it. The check proves one file, not the suite.
- Redirect: a server whose own t10 bytes are foreign but which 302s the t10
  path to correct bytes on another port: check returns True. `urllib`
  follows redirects, so the check verifies the URL's ultimate content, not
  the bytes the server on the port holds.
- User-Agent split: a server returning real bytes to `Python-urllib` and
  foreign bytes to any other UA: check returns True, while a browser-UA fetch
  of the same path returns foreign bytes. The check's oracle is
  distinguishable from the browser's fetch.

Harm as bounded by the evidence: the t10 fixture is byte-identical across
every staging in repo history (both t10 and t01 fixtures were introduced in
the single commit `1767d4c` and never changed; only one
`t10-music-player/fixture.html` path exists in the repo). So a stale server
from an earlier staging passes the check harmlessly, because its other
fixtures are byte-identical too. The harmful case needs a hand-modified or
foreign-suite root, which has no observed instance. That keeps this AMEND,
not BLOCK, but the stated purpose ("served bytes are the staged suite") is
only 1/10 verified, and the fix is a few lines. See U1.

## F2 (MEDIUM): the -m branch covers only the spaced form

`run_batch3.py:2301-2303` accepts a bare `run_*` / `hand_drive_e1` token only
when the immediately previous token is exactly `-m`.

Reproductions, all with real stub-module execution (probe 1, stub prints
`stub main running`, then sleeps):

- `python3 -mrun_batch3` (joined short option, valid Python): runs the stub,
  matcher False, `_scan_other_runners` misses it.
- `python3 -m foo.run_batch3` (dotted module path): runs the stub, matcher
  False, scan misses it. (`python3 -m tests.realistic.run_batch3` is unit
  False too; note that exact path cannot execute as-is from the repo root
  because `tests/realistic` has no `__init__.py`, but the `foo.run_batch3`
  case proves the dotted shape executes when packaged.)
- `python3 -X dev run_batch3.py` and `python3 -W ignore run_batch3.py`
  (interpreter flags that take a value): unit False. Valid Python, single
  process, evades the matcher because the script token's previous token is
  the flag value, not a python token or a `-` flag.

None of these is a documented fleet launch form, and every documented form
is caught. But the `-m` fix was the headline of this pass (Council 2 Fix 1,
redteam H1), and it stops one token short of the forms Python itself accepts
for the same launch. The hardening is small. See U2.

## F3 (LOW): codex anchor accepts "codex" in any token position

`run_batch3.py:2335-2351` returns True for any token exactly `codex` with a
refuse marker in any other token. The anchor is to the token text, not to an
executable position.

Reproductions, live with exact argv via a compiled sleeper (probe 2):

- `grep -rn marionette codex` returns True. A developer grepping for
  `marionette` in a directory named `codex` is flagged as a codex executor.
- `cat codex marionette-notes.txt` returns True. `cat` is not codex.
- `bash -c "echo codex marionette"` returns True. `echo` is not codex.
- Scan end-to-end: with a `codex exec --marionette` dummy and a `grep -rn
  marionette codex` dummy live together, `_scan_other_runners` hits both,
  so the grep false positive reaches the gate and would refuse a launch.

Impact is fail-closed and transient (the grep finishes in milliseconds; a
re-run passes), so LOW. Escapes found on the other side: a binary named
`codex-cli` with `--marionette` returns False; a marker-free codex command
(`codex exec "drive zen via tool"`) returns False by design, since the marker
heuristic cannot see tool-driven browsing; a marker split across two tokens
or hidden inside the codex path token itself returns False (both contrived).
See U3.

## F4 (LOW): sibling copies diverged, the "identical logic" claim is false

`run_batch3.py:2280` (in the fix's own edited docstring) still says
"Keep in sync with launch_y13.py and run_codex_y5.py (identical logic)".

Checked directly: `launch_y13.py:125` and `run_codex_y5.py:3604` still have
the old `_is_runner_cmdline` with no `-m` branch and no `-c` import branch;
neither file defines `_is_codex_executor`; `run_codex_y5.py:3776` still uses
the old substring test (`"codex" in _cmd.lower()`), and `launch_y13.py`
likewise. Council 2 warned exactly this would happen ("same fix should go
to sibling copies or the identical logic claim breaks"); the adjudication
flagged it to Muse/Y13f and declined to edit Y13f's in-progress files, but
the claim was left standing in this copy. No impact on this runner's own
gate; the impact is fleet-wide inconsistency plus a false statement in the
shipped file. See U4.

## F5 (LOW): the "~2.4-tick margin" claim holds only at the fastest RTT

Re-derived from the fixed code path. The fixture timer is `setInterval`
100 ms; `nextTrack()` resets position without restarting the timer, so the
advancing read counts interval ticks in (reset, advancing-read exec]. Reset
happens inside the `exact_zero_next` eval. Advancing-read exec is at reset +
850 ms + N round trips, N = 5 pre-fix, N = 3 post-fix (F-section count
confirmed). Ticks in a window of E ms are floor(E/100) or ceil(E/100)
depending on interval phase (plus/minus 1 tick jitter).

| RTT (ms) | pre-fix ticks | post-fix ticks | post margin to 11 |
| --- | --- | --- | --- |
| 2 | 8-9 | 8-9 | 2 to 3 (mean 8.56, margin 2.44) |
| 19 | 9-10 | 9-10 | 1 to 2 (mean 9.07, margin 1.93) |
| 50 | 11 | 10 | 1 |
| 75 | 12-13 | 10-11 | 0 to 1 |
| 83 | 12-13 | 10-11 | 0 to 1 |
| 100 | 13-14 | 11-12 | -1 to 0 |

First possible post-fix failure (ceil above 11) is at RTT above 83 ms;
guaranteed failure (floor above 11) at RTT 117 ms and up. Pre-fix the
boundary was first fail above 50 ms, guaranteed at 70 ms, which matches the
original redteam (reads 11 at 50 ms, fails at 75 ms). The fix moves the
first-fail RTT from 50 ms to 83 ms, which is real improvement, and the move
itself is correct. But the log's "~2.4-tick margin" is the 2 ms-median
number only; at the plan's own 19 ms maximum it is 1.93, at 50 ms it is 1.0.
See U5.

## F6 (LOW): -c bypass forms beyond the docstring, plus an import-only FP

`run_batch3.py:2304-2306` accepts a bare runner module name only after a
literal `import` / `from` token. The docstring lists `runpy.run_path` as a
residual but not these three, all reproduced live with real stub execution
(probe 1, stub main ran, matcher False, scan missed):

- `python3 -c "__import__('run_batch3').main()"`
- `python3 -c "import importlib; importlib.import_module('run_batch3').main()"`
- `python3 -c "exec(open('run_batch3.py').read())"`

These are deliberate forms, not accidental ones, so they stay inside the
adjudicated threat model; they only need recording, not necessarily code.
The false positive on the same branch is live too: `python3 -c
"import run_batch3, time; time.sleep(20)"` imports the module, never calls
`main()`, never drives anything, yet the matcher returns True and the scan
hits it (probe 1, 10.13 s). The rule cannot distinguish import-only from
import-plus-main. Impact is fail-closed and transient. See U6.

## F7 (INFO, no code change): the re-scan is a point check, not a hold

`run_one`, `run_batch3.py:2181-2189`, re-scans at the top of each test. The
window probe (probe 1, 30.06-31.06 s, fake WD plus a stub test function
sleeping 1.0 s, dummy spawned 0.3 s after the scan): `run_one` returned
`pass` True with the dummy alive during the test, and the next `run_one`
call caught the same dummy (INFRA). So a runner starting mid-test is missed
until the next test's re-scan. Closing that window needs a hold (flock),
which the adjudication declined fleet-wide and recorded. Note also that the
second runner's own `launch_gate` should refuse while this runner is live,
so the window only matters together with a gate-bypassing second runner
(F2/F6/F8 forms). No code change required; record the window as a known
limitation. See U7.

## F8 (declined items): no plausible accidental form found, one correction

I reproduced at least two declined items live (in fact five), via exact argv
shapes plus unit cmdlines: renamed copy (`python3 /tmp/drive_zen.py`),
shebang renamed copy (`/tmp/mydriver`), spoofed argv[0]
(`innocent run_batch3.py`), extensionless (`python3 run_batch3`), direct
`.pyc` (`python3 run_batch3.pyc`). All return False, as the docstring says.

Judgment: none of them is a plausible ACCIDENTAL fleet launch form. Fleet
copies are all `run_*.py`, so a renamed copy that still starts `run_` and
ends `.py` is caught; a rename to a non-`run_` name is a deliberate
experiment, not a workflow. No fleet workflow runs an extensionless script
or a `.pyc` directly. Spoofed argv[0] needs `exec -a` and is adversarial by
construction. The adjudication's dismissal of these stands.

One correction to the docstring's residual list: double-nested `-c` quoting
is listed as a miss, but live it is caught through the leaf process. Probe 2:
`flock /tmp/rt-lock -c "bash -c 'python3 run_batch3.py'"` gives outer flock
False and intermediate `/bin/sh -c` False, but the leaf `python3
run_batch3.py` is True and the scan finds it. `bash -c "python3 -c
'import run_batch3; ...'"` execs python directly, matcher True. The
residual is at most a sub-second spawn race, not a standing bypass. See U6.

## Unblock conditions

U1 (F1): extend `_verify_served_fixture` to fetch and md5-check all 10
fixtures under `clone1-batch3/` (not only t10), refuse on any mismatch; and
refuse redirects (or allow same-origin redirects only), so a 302 to correct
bytes elsewhere cannot pass. Re-prove with the mixed, redirect, and
UA-split servers from probe 1 (mixed and redirect must then refuse).

U2 (F2): in `_is_runner_cmdline`, also accept a joined `-m<module>` token
(`-mrun_batch3`) and a dotted module path whose last component is a bare
`run_*` / `hand_drive_e1` token (`foo.run_batch3`). Re-prove live with the
stub-module executions from probe 1 (both must then be caught). The `-X` /
`-W` flag-with-value forms may be recorded as residuals instead of fixed.

U3 (F3): anchor `_is_codex_executor` to an executable position: the `codex`
token must be argv[0], the first word of a `-c` string, or immediately after
a small wrapper whitelist (for example `flock`, `nohup`, `env`, `setsid`,
`timeout`). Re-prove live with exact argv: `codex exec --marionette` and a
`flock`-wrapped codex still caught; `grep -rn marionette codex`,
`cat codex marionette-notes.txt`, and `bash -c "echo codex marionette"` no
longer flagged.

U4 (F4): either apply the same `-m` / `-c` import / codex-anchor fixes to
`launch_y13.py` and `run_codex_y5.py`, or delete the "(identical logic)"
claim at `run_batch3.py:2280` and record the divergence in the log.

U5 (F5): restate the margin in the plan and the log as an RTT-dependent
range (2.44 ticks at 2 ms median, 1.93 at 19 ms maximum, 1.0 at 50 ms; first
possible fail above 83 ms RTT, guaranteed fail at 117 ms), and keep the
watch item on `details.positionAdvancingAfterNext` and
`details.positionAdvancingAfterShuffleNext`.

U6 (F6/F8): in the `_is_runner_cmdline` docstring, record `__import__`,
`importlib.import_module`, and `exec(open(...).read())` as known residuals
alongside `runpy.run_path`; note the import-only `-c` false positive; and
correct the double-nested `-c` note to say the leaf process is caught and
the residual is only a spawn race.

U7 (F7, record only): record the mid-test re-scan window as a known
limitation in the log (no code change; the flock close stays declined
fleet-wide).

## Timed work log (Asia/Ho_Chi_Minh, 21 Nov 2026)

- 21:33: fetch, `git log`, fix diff read (`8bee524` own diff, 311 lines for
  the runner file), restage log adjudication read.
- 21:34-21:39: read `_is_runner_cmdline`, `_is_codex_executor`,
  `_scan_other_runners`, `_verify_served_fixture`, `run_one`, `run_b3_t10`
  advancing path, `check.mjs` at `1d23532`, fixture timer, `Runner.check`
  semantics, sibling copies, plan margin note.
- 21:39-21:40: probe 1 written and run (31.1 s, 95/101 checks; 6 failures
  traced to my `yes` harness bug, not the runner).
- 21:40-21:41: probe 2 written and run (7.4 s, all codex exact-argv cases
  pass, double-nested caught live via leaf, moved-assert positions
  confirmed). Fixture history checked (`1767d4c` introduced all fixtures,
  never changed).
- 21:41-21:43: wording spot-checks (C3 F1-F7, em/en dash grep 0, L1 grep,
  `ebe5853` blob/md5 re-verified).
- 21:43-21:47: this paper written.

## Appendix: key reproduction excerpts

Probe 1 (abridged, full log `/tmp/y14b-fix-redteam-probe.log`):

```
LIVE m-plain: alive=True ran_stub_main=True matcher=True scan_hit=True
LIVE m-combined: alive=True ran_stub_main=True matcher=False scan_hit=False
  cmdline=b'python3\x00-mrun_batch3\x00'
LIVE m-dotted: alive=True ran_stub_main=True matcher=False scan_hit=False
  cmdline=b'python3\x00-m\x00foo.run_batch3\x00'
LIVE c-dunder-import: alive=True ran_stub_main=True matcher=False scan_hit=False
LIVE c-importlib: alive=True ran_stub_main=True matcher=False scan_hit=False
LIVE c-exec-open: alive=True ran_stub_main=True matcher=False scan_hit=False
LIVE c-import-only: alive=True matcher=True scan_hit=True
  cmdline=b'python3\x00-c\x00import run_batch3, time; time.sleep(20)\x00'
M1 foreign server: verify=False
M1 matching server: verify=True
M1 404 server: verify=False
M1 mixed right-t10 foreign-t01: verify=True (DEFEAT)
M1 mixed: t01 bytes actually served = b'<html>FOREIGN t01</html>'
M1 redirect to correct bytes: verify=True (DEFEAT)
M1 hang server: verify=False elapsed=5.01s
M1 UA-split server: verify=True (DEFEAT)
M1 UA-split: browser-UA fetch gets = b'<html>FOREIGN t10</html>'
RESULT {"test": "b3-t01", "pass": false, "failures": ["INFRA: live slot busy,
  runner process running: pid 174268: python3 run_batch3.py"], "elapsed_ms": 1}
M2 window: run_one returned pass=True elapsed=1.00s fn_ran=True
  wd_entered=True dummy_alive_during_test=True
M2 next-test: pass=False failures=['INFRA: live slot busy, ...']
assert-set: runner expect_text multiset == checker expectText multiset
  (33 calls each, runner-only [], checker-only [])
```

Probe 2 (abridged, full log `/tmp/y14b-fix-redteam-probe2.log`):

```
PASS codex-executor: got=True cmdline=b'codex\x00exec\x00--marionette\x00'
PASS codex-grep-FP: got=True cmdline=b'grep\x00-rn\x00marionette\x00codex\x00'
PASS codex-cat-FP: got=True cmdline=b'cat\x00codex\x00marionette-notes.txt\x00'
PASS codex-echo-FP: got=True cmdline=b'bash\x00-c\x00echo codex marionette\x00'
PASS codex-cli-escape: got=False cmdline=b'codex-cli\x00exec\x00--marionette\x00'
scan end-to-end: codex TP hit=True, grep FP hit=True
flock double-nested outer cmdline matcher=False
  descendant pid 174417 cmdline=b'python3\x00run_batch3.py\x00' matcher=True
  scan finds the flock double-nested launch: [(174417, 'python3 run_batch3.py')]
plain-Next moved assert after advancing_later: True
shuffle moved assert after advancing_shuffle_later: True
```

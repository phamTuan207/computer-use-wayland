# Y13g round-2 redteam paper

- Verdict: **BLOCK**
- Scope: round-2 diff only, commits `0639d04`, `87eec47`, `6ba43f2`,
  `8bdd5aa`, `5a9b9e8`, branch `todolist-push`, repo
  `~/workspace/computer-use-wayland`.
- Redteam: subagent session `9847a349`, parent Worker Y13g.
- Date: 2026-11-22, Asia/Ho_Chi_Minh. All times in the running log
  `improvements/worker-y13g-r2-redteam-log.md`.
- Harnesses + logs: `~/workspace/y13g-r2-redteam/` (`attack_a*.py`,
  `logs/`).

## Why BLOCK

Two load-bearing guarantees in the round-2 diff do not operate:

1. **F1 (HIGH).** R2's headline fix, the launcher exemption that was
   supposed to make `_check_entry_pyc` operative, is dead code: the
   exemption condition can never be True. `_check_entry_pyc` is
   still unreachable on the launcher path (C2-2/F2 NOT fixed), and a
   legitimate entry `.pyc` now bricks the launcher instead of being
   verified and deleted.
2. **F2 (HIGH).** R1's import-time safety claim, that `-P` keeps a
   planted stdlib module from executing, is false for the
   `PYTHONPATH` channel: 13 stdlib `.py` plants and a `.so` plant
   execute in the runner under `-P`, most with rc 0 and
   `manifest_ok: true`; the plant also executes in the launcher
   process itself before any gate, and passes through the launcher
   exec into the runner. A delegating `shlex` shim runs inside
   `_is_runner_cmdline` while keeping its verdicts correct.

Both are live-proved below with exact commands, return codes, and
quoted output. The round-2 diff did fix real things (ship-dir
`.so`/`.py` plants all refuse, symlinks all refuse, R5, R9, linear
marker ordering), but F1 and F2 are not polish items: F1 means the
documented launcher flow cannot proceed with a legitimate entry
`.pyc`, and F2 means planted code executes in both entry points
while the run proceeds normally.

## Pins verified

Runner md5 `d5047ff573820491263a2eb3805105f4`, launcher
`8e72a5ce85cbaf8382f998987e8890e5`, run_live
`84fa106c253d5e7f16daccf2ce3f14a5` (pin `1e3901c` holds), manifest
`7c76383402e4c50b28adab6b25a22e09`, 27 files. Regen `--stage` to
`~/workspace/y13g-r2-redteam/ship` gave manifest md5 `7c763834`,
29 files staged, staged `--verify-manifest` exit 0.

## Findings

### F1 (HIGH): the R2 launcher exemption is dead code; `_check_entry_pyc` is still unreachable

`check_manifest` in `launch_y13.py` reads:

```python
if (not rel_root and _is_entry_pyc_rel(rel)):
    continue
```

An entry `.pyc` lives under `__pycache__/`, so `rel_root` is
`"__pycache__"` (truthy) and the conjunction can never be True.
`_is_entry_pyc_rel` itself requires the `__pycache__/` prefix, so
the two halves contradict each other for every input. The
exemption never fires.

Live evidence (A2L full-launcher end-to-end, extracted `main()` with
only `check_marker` patched to a no-op, everything else real:
`check_go` with `Y13_GO=1`, `write_token`, `check_manifest` against
the real repo, `_check_entry_pyc`, `_scan_ship`, `check_token`,
`check_runner_quiet`, `check_ports`, `check_geckodriver`, flock +
exec runner `--verify-manifest`; log `logs/a2launcher-run3.log`,
7/7 as defined):

- Clean ship: rc 0, full pass, `manifest_ok: true`.
- Legit entry `.pyc`, `py_compile` with an ABSOLUTE path: rc 2,
  `[launch_y13] REFUSED: planted bytecode in ship:
  __pycache__/run_codex_y5.cpython-312.pyc`, the `.pyc` still on
  disk. `_check_entry_pyc` never runs.
- Legit entry `.pyc`, `py_compile` with a RELATIVE path: same
  refusal, rc 2.
- Legit `run_live` `.pyc`, and `import run_live` then launcher
  (the A3b brick the launcher was supposed to heal): same refusal,
  rc 2, `.pyc` still present. NOT healed.
- Forged entry `.pyc`: rc 2, same refusal, no marker. Right outcome,
  wrong mechanism: the forged bytecode is refused as "planted",
  never adjudicated.

The isolated function is correct (A2x, 8/8 shapes: forged,
wrong-tag, hash-based, src-path-differs all refuse; legit entry
and legit `run_live` verify + delete). The live flow never reaches
it. R2 did not fix C2-2/F2; it moved the refusal one function
earlier and broke the legitimate flow in the process: any `-m` /
`import` probe or `py_compile` now bricks the ship for the
launcher until the operator manually deletes the `.pyc`.

Proposed fix: exempt on `_is_entry_pyc_rel(rel)` alone, i.e.
`if _is_entry_pyc_rel(rel): continue`, and add a launcher-path
test that a legitimate entry `.pyc` is verified + deleted and the
run proceeds (the A2L cases above, with the expectations flipped
to rc 0). Also fix F5 below, or the exemption will only help the
absolute-path `py_compile` form.

### F2 (HIGH): `PYTHONPATH` plants execute in both entry points under `-P`

`-P` keeps the script dir off `sys.path` but does NOT clear
`PYTHONPATH`, and neither entry point inspects it. The launcher
execs the runner with `env = dict(os.environ)` plus
`PYTHONSAFEPATH=1` only, so `PYTHONPATH` passes through untouched.
The launcher's own comment (lines 1495-1498) claims
`PYTHONSAFEPATH=1` keeps "a planted stdlib .py" from executing at
import time in the runner. That claim is false for `PYTHONPATH`
plants.

Live evidence (A6, log `logs/a6-run3.log`, 117 cases, 101 pass,
16 FAIL, all 16 this channel):

- 13 `.py` names execute in the runner under `-P`:
  `enum`, `re`, `json`, `socket`, `subprocess`, `hashlib`,
  `datetime`, `pathlib`, `copyreg`, `functools`, `collections`,
  `warnings`, `shlex`. Each was planted alone in its own
  `PYTHONPATH` dir (exact attribution). Example:
  `A6pp-runner shlex -P: rc=0 marker=True out=POISON-MARKER: A6pp
  shlex`. Most fire with rc 0 and `manifest_ok: true`: the run
  proceeds with the plant loaded.
- `shlex.so` via `PYTHONPATH` fires too (marker file written,
  rc 0, `manifest_ok: true`).
- The plant executes in the REAL launcher process:
  `python3 -P launch_y13.py --ship-dir <ship> --repo <repo> all`
  with `PYTHONPATH=<dir with shlex.py>` prints
  `POISON-MARKER: A6pp shlex` at the launcher's post-scan
  `import shlex`, before `check_go` runs (rc 2 at the marker gate,
  but the plant already executed).
- The plant passes through the launcher exec into the runner:
  through the extracted launcher `main()`, the exec'd runner (a
  fresh process) prints the marker; rc 0.
- A delegating `shlex` shim (prints a marker, then delegates every
  attribute to the real `shlex` loaded by path) runs inside
  `_is_runner_cmdline` with correct verdicts (`True` for a runner
  cmdline, `False` for a benign one): the tokenizer executes
  attacker code while behaving correctly.
- Control: the plain form (no `-P`) does NOT load a `PYTHONPATH`
  `shlex.py` plant, because the safe-path refusal at line 204
  precedes `import shlex`. Immune names: `os` (pre-loaded before
  `PYTHONPATH` is consulted), `typing`, `sre_compile` (not imported
  on this path).

Contrast: every ship-dir plant is clean (30 `.py` + 32 `.so`
runner cases, 15 + 16 launcher cases, `http/__init__.py` x3). The
R1 scan + `-P` defense holds for the ship dir and fails only for
the environment channel it never mentions.

Proposed fix: in the launcher's exec env, delete `PYTHONPATH`
(and `PYTHONHOME`, `PYTHONSTARTUP`) instead of passing
`os.environ` through; refuse in both entry points when
`PYTHONPATH` is set and non-empty, or at least warn loudly and
record it; document that the operator must launch from a clean
environment. A runner-side check (`os.environ.get("PYTHONPATH")`
refusal at module top, next to the safe-path check) closes the
direct path too.

### F3 (MEDIUM): tokenizer residuals, 20+ live-proved evasions

`_is_runner_cmdline` (both copies agree, AST identity True for the
14 tokenizer defs) still misses whole evasion classes. Every item
below was live-proved: the A4 live dummy probe (59/59 as defined,
log `logs/a4live-run1.log`) and the live-forms probe with real
executions on fresh ships (28/31 + 5/6, logs
`logs/a4liveforms-run1.log`, `logs/a4liveforms2-run1.log`,
`logs/a4liveforms-run3.log`), plus the unit table
(`logs/a4unit-run2.log`: SPEC 80/80, EXTRA 48/49, FRESH 2/29).

Confirmed evading live (marker prints = executed, `manifest_ok:
true` on a fresh ship):

- `-m trace --trace` / `--count` (with `-P`; without `-P` the
  safe-path gate refuses first). The stdlib `trace` script branch
  carries no `__spec__`, so the `-m` guard cannot help and the
  tokenizer has no `-m trace` case.
- `-m pdb -c continue` and piped `continue`; `-c pdb.run(...)`
  (piped continue); `-c exec(...)` with split-concat.
- `-c` sink aliases: `from os import system`, `import os as o;
  o.system`, `__import__('os').system`, `os.popen`,
  `subprocess.getoutput` / `getstatusoutput`.
- `bash -c` sequences, pipelines, and `&&` with the runner as the
  SECOND command (and the EXTRA miss: `bash -c` with `;` glued
  mid-token). `_shlex_tokens` drops separators and
  `_command_executes_runner` examines only the FIRST command.
  Also `bash -c 'command -p python3 run_codex_y5.py'`.
- Wrappers: `xargs`, `setsid -w`, `watch` (with `TERM=xterm`),
  `systemd-run`, `su -c`, `unshare -r`, `chrt -o/-i/-b`
  (only `-f` needs privilege; `-f` fails here with "Operation not
  permitted"), `ionice`.
- Renamed `python3` / `bash` binaries, and an unknown wrapper
  script execing `"$@"`.
- `timeout 0x10`: GNU `timeout` accepts a hex duration (live rc 0);
  the tokenizer's `_is_timeout_dur` rejects it, so the form is
  not recognised as a runner execution. (`timeout 1h30m` is
  correctly invalid, live rc 125.)

Controls that hold: `-m profile` / `cProfile` (guard fires, rc 0,
profiler swallows `SystemExit`), `-m runpy` (rc 2), plain `-m pdb
script` stops at the `(Pdb)` prompt, `timeout 60s` / `1m` caught,
`nice` / `stdbuf` / `taskset` / `sudo` / `uv`, `exec -a`, `pypy3`,
`bash -c` glued `;` / `&&` (runner first) all caught, as are all 6
round-1 evasions.

Impact: `check_runner_quiet` (and the runner's own process scan)
can miss a live runner, so the launcher can exec a second runner
while one is already running, or fail to notice a runner at all.
This is a guard against duplicate runs, not the primary safety
gate, hence MEDIUM.

Proposed fix: refuse `-m trace` explicitly; extend the `-c` sink
list (`os.popen`, `subprocess.getoutput` / `getstatusoutput`,
import-as and `__import__` forms, `pdb.run`, `exec`/`eval` of
concatenated strings); scan ALL commands in a `-c` string, not
just the first; extend the wrapper list (or, better, resolve the
ultimate command by following the wrapper chain generically);
recognise a python invocation by its script argument / md5
regardless of `argv[0]` (renamed interpreter/shell); accept hex
durations in `_is_timeout_dur`.

### F4 (MEDIUM): `--topo-order` does not order across merges

R7 claims ordering by branch position, not committer date, so "a
forged old date no longer outranks a newer abort". That holds only
on a LINEAR history. Across a merge, `git log --topo-order` shows
the SECOND parent's line first regardless of dates.

Live evidence (A5, log `logs/a5-run1.log`, 32/32 as defined):

- Case 10: abort on the main line (real date 2026-11-21), completion
  on a side branch (forged NEWER date 2026-11-22), merged in:
  PASSES. The forged completion overrides the main-line abort.
- Case 11: completion on the main line (2026-11-21), abort on a
  side branch (forged OLD date 2020-01-01), merged in: REFUSES,
  "Y6c abort ... is newer than the newest completion". `git log
  --topo-order` in that repo shows: merge, abort (2020),
  completion (2026), seed. A stale abort resurrected by a merge
  blocks a fresh completion (false refusal / denial of service).
- Linear case 3 still holds: old-date completion vs newer abort on
  one line refuses by log order.

Proposed fix: order markers by first-parent position only (e.g.
`git log --first-parent --topo-order`, so side-branch markers are
ignored entirely), or compare merge recency instead of raw log
order. At minimum, document that the marker gate is only sound
on a linear `todolist-push` and refuse (or warn) when the
completion/abort decision depends on a merge.

### F5 (MEDIUM): `_check_entry_pyc` refuses a legitimate relative-path `py_compile` `.pyc`

A `.pyc` produced by `py_compile` with a RELATIVE path bakes
`co_filename` `'run_codex_y5.py'`; `_check_entry_pyc` fresh-compiles
with the ABSOLUTE path, so the marshal comparison mismatches and
the LEGITIMATE cache refuses. Confirmed in `confirm_pycompile.py`:
relative-path compile refuses, absolute-path compile verifies +
deletes. A moved-ship legit `.pyc` refuses the same way.

Proposed fix: read `co_filename` from the cached code object and
compile the fresh reference with that same filename (or compare
code objects ignoring `co_filename`).

### F6 (LOW-MEDIUM): the `-m` guard heals the file but not the empty dir

A nested legitimate `.pyc` (e.g. `__pycache__/sub/*.pyc`) is
deleted by the `-m` guard, but the empty `sub/` directory remains
and still bricks direct verify (the scan refuses the unexpected
dir). The guard never prunes directories.

Proposed fix: prune empty `__pycache__` subdirectories in the
`-m` guard after deleting entry `.pyc` files.

### F7 (LOW): `check_manifest` gaps, all backstopped by `_scan_ship`

`check_manifest`'s walk only flags symlinks, `.pyc` files, and
top-level `.py` files. It does NOT flag: a FILE named
`__pycache__`, a DIRECTORY named like a `.pyc`, or a nested `.py`
(such as `http/__init__.py`). All three were live-proved to pass
`check_manifest` and refuse at `_scan_ship` (A6 http launcher,
A7 cachefile/pycdir). The two layers disagree about what counts
as planted, which is a latent hazard if `_scan_ship` is ever
skipped or reordered.

Proposed fix: make `check_manifest`'s walk flag any file/dir not
in the manifest set (the same allowlist `_scan_ship` uses), so the
two layers agree.

## What round 2 fixed (verified)

- Ship-dir `.so` / `.py` plants: all refuse at the runner scan
  (kind `planted-py` / `unexpected-file`) and at the launcher
  (`check_manifest` or `_scan_ship`). C2-1 closed for the ship dir.
- R5 entry `.py` hash check: tampered `run_live.py` on the direct
  path refuses rc 2 before import, no marker (A9 case 1).
- R9 `_proven_no_body`: 14/14, including `eval_error` None and
  `""` both returning False (A8).
- Symlinks: all 5 shapes refuse at every layer, kind `symlink`;
  C2-4 holds (symlinked `__pycache__` refuses, outside file
  survives); hardlinks refuse via the path leg / md5 leg (A7 36/36).
- Marker ordering on a linear history: old-date completion vs
  newer abort refuses by log order (A5 case 3); remote-URL
  normalization: SSH form, trailing slash, no `.git`, host case all
  pass; http, wrong-case repo, double slash, `ssh://` form,
  different owner/repo, no origin, `insteadOf` redirect all refuse
  (A5 pin cases).
- `_SHIP_FILES` identical between the two entry points (29 files);
  AST identity True for the 14 tokenizer defs.

## Documented limits (not findings)

- A5 case 1: a fake completion subject passes BY DESIGN (subject
  spoofing is a known limitation of the marker scheme).
- A2: `-m` / import forms print the marker (documented hole: the
  forged bytecode IS the running code); fake-OK via `-m` prints a
  fake `manifest_ok` with rc 0.
- A9 case 2: a self-consistent tamper (`run_live.py` + manifest
  entry md5) passes the direct path rc 0 with the marker printed;
  the launcher refuses it via the committed-manifest md5 comparison.
- A9 case 4: a tampered runner prints its marker first (the entry
  script runs before its own hash is checked), then refuses rc 2.
- A8: a non-dict `diag` (`None`) raises `TypeError`, but all 5 call
  sites pass `diagnose_body`'s dict and read
  `diag["classification"]` first, so it is unreachable.

## Per-attack results

510 probe cases total across the batteries (counts are cases run,
with the outcome as defined in each harness):

| Battery | Cases | Result |
|---|---|---|
| A1 forged `run_live` `.pyc` (top, nested, `-m`) | 3 | refuse rc 2, no marker |
| A2 forged ENTRY `.pyc` (direct, `-m`, import, fake-OK) + A2x isolated `_check_entry_pyc` | 43 in A123 total | direct refuses; `-m`/import marker prints (documented); A2x 8/8 correct as a function |
| A2L full launcher end-to-end | 7 | 7/7 as defined; F1 headline |
| A3 brick sequence (`-m` +-P, `py_compile`, `import run_live`, empty cache, env-guarded `-m`) | in A123 | R4 healing works top-level; nested empty-dir brick (F6); C2-4 holds |
| A4 unit table | 158 (SPEC 80 + EXTRA 49 + FRESH 29) | SPEC 80/80, EXTRA 48/49, FRESH 2/29; both copies agree |
| A4 live dummy probe | 59 | 59/59 as defined; all 6 round-1 evasions caught, all 20 fresh attacks evade |
| A4 live forms (real executions) | 37 (31 + 6) | 28/31 + 5/6 executed with `manifest_ok: true`; the rest are the F3 evasions |
| A5 marker + remote-URL suite | 32 | 32/32 as defined; F4 merge finding |
| A6 stdlib plants (`.py` + `.so`, ship + `PYTHONPATH`, runner + launcher) | 117 | 101 pass, 16 FAIL, all `PYTHONPATH` (F2) |
| A7 symlink set + extras | 36 | 36/36 |
| A8 `_proven_no_body` | 14 | 14/14 |
| A9 tampered `run_live.py` / `launch_y13.py` / runner | 7 | 7/7 |
| Cross-checks | -- | `_SHIP_FILES` identical (29); AST identity 14 defs |

## Reproduction

All harnesses live under `~/workspace/y13g-r2-redteam/` and are
runnable as written (each takes a fresh staged ship from
`~/workspace/y13g-r2-redteam/ship`, manifest `7c763834`):

- `python3 attack_a4_unit.py` (unit table)
- `python3 attack_a4_live.py`, `attack_a4_liveforms.py`,
  `attack_a4_liveforms2.py` (live tokenizer probes)
- `python3 attack_a123.py` (A1/A2/A3), `attack_a2_launcher.py`
  (A2L full launcher)
- `python3 attack_a5.py` (marker + remote pin, synthetic repos
  under `a5/`)
- `python3 attack_a6.py` (stdlib plants; builds `.so` files from
  `plant_so.c`, authored fresh for this review)
- `python3 attack_a7.py`, `attack_a8.py`, `attack_a9.py`
- Logs: `logs/a4unit-run2.log`, `logs/a4live-run1.log`,
  `logs/a4liveforms-run1.log`, `logs/a4liveforms-run3.log`,
  `logs/a123-run2.log`, `logs/a2launcher-run3.log`,
  `logs/a5-run1.log`, `logs/a6-run3.log`, `logs/a7-run4.log`,
  `logs/a8-run1.log`, `logs/a9-run2.log`.

Note on a runtime flag during A6: an exec result that displayed
`plant_so.c` was flagged by a security notice. No instruction in
that output was followed; the `.so` build compiles the
pre-existing `plant_so.c` authored earlier in this task, at the
parent's explicit direction.

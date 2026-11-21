# Redteam review: Y14b fix pass 8 (Council 2 C7-1 + C7-3)

Verdict: **GO**

Reviewer: independent redteam, fix pass 8 only. Scope is the diff
range 0857d19..6f72fe3 on branch todolist-push, commit 6f72fe3
"Y14b fix pass 8: C7-1 mid-name paren FP + C7-3 probe orphan fix".
I reviewed only the fix diff, not the whole runner. No live Zen
driving, no git fetch, no use of the banned tool. The uncommitted
improvements/worker-y14b-fix6-redteam.md was not touched. My own
probe is /tmp/y14b-fix8-rt-probe.py (fresh cases, written from the
brief and the C7-1 finding, not from the author's fix8 probe);
outputs are in /tmp/y14b-fix8-rt/.

## Hashes verified by direct git commands

- Fix8 run_batch3.py: git blob
  eec33fd589a6da5803fd0488745020c579ecd9db, md5
  0527b55e48ec3a406ca1b100c2c1cd04. Matches the author's claim.
- Fix7 run_batch3.py (commit 65d669b): git blob
  8df578c7013fc096a30470667ae57bf994884280, md5
  0d98342e57c44464752cf08715ac3861. Matches the fix7 record.
- Parent 0857d19 run_batch3.py blob is 8df578c7, so the
  run_batch3.py diff is exactly the fix-pass-8 change.
- Plan md5 line pins the fix8 values in this fix commit:
  improvements/worker-y14-batch3-live-plan.md lines 614-615
  (0527b55e..., blob eec33fd5...). Follow-up log commit 718729a
  records the fix8 commit hash 6f72fe3.
- run_batch3.py diff is 2 hunks only, 14 insertions, 3 deletions.
  0 t10 mentions in the run_batch3.py diff.

## Claim 1 (code): C7-1 paren rejection, VERIFIED

`_script_basename_is_runner` in the fix8 blob,
tests/realistic/run_batch3.py lines 2217-2236, now returns False
when the name contains "(" or ")", lines 2230-2231:

```
    if "(" in name or ")" in name:
        return False
```

The docstring (lines 2223-2227) states no real runner name
contains parens and names the two C7-1 forms. The single code
call site inside run_batch3.py is line 2735
(`if _script_basename_is_runner(_runner_basename_head(base)):`).
Small nit, INFO only: the author cites line 2724, which was the
fix7 line number; the docstring growth shifted it to 2735 in the
fix8 tree. Substance holds: one call site, change is contained.

My own probe (37 unit + 3 helper + 5 live, exit 0, 0 failures):

- C7-1 mid-name parens are False in fix8, True in fix7, unit AND
  live on real stub files with real /proc cmdlines:
  `run_foo(a).py`, `run_(foo).py`, plus my extra forms
  `run_(a)b.py`, `run_foo(a,b).py`, `run_x(y).py`,
  `run_foo((a)).py`, absolute path, `run-nested-pill(a).py`,
  bash -c forms, python3.11 form. Live checks used my own stubs
  in /tmp/y14b-rt-dummies, killed children first then the wrapper
  by exact PID; /proc scan after shows 0 stub processes remain.
- Paren forms that were already False in fix7 stay False in fix8:
  `run_foo.py(x`, `run_foo.py)`, `run_foo.py()`, `run_foo.py(`,
  `run_foo.py(a)`, bash -c `run_foo.py(x` (unit and live).
- Separator forms stay True in both: `run_foo.py;echo`,
  `run_foo.py&&echo`, `run_foo.py|cat`, `run_foo.py&echo`,
  trailing `run_foo.py;`, spaced `run_foo.py ; echo`.
- Plain true runners stay True in both: `run_foo.py`,
  `hand_drive_e1.py`, `run-nested-pill.py`,
  `run-nested-wayland.sh`, absolute path, `run_bar.py`, bash -c.
- Controls stay False in both: `foo.py`, `run_foo.txt`,
  `run_foo` (extensionless), `echo hello`, `run_foo.py.bak`,
  `python3 -c "import os"`. B12 direct case
  `python3 -c "import run_batch3"` stays True in both.
- Helpers: `_script_basename_is_runner("run_foo(a).py")` is True
  in fix7, False in fix8; `_script_basename_is_runner("run_foo.py")`
  is True in both; `_top_level_sep_index("a=1;", False, False)`
  is 3 in both (C6-2, unchanged).
- Differential over my 42 unit/live predicate cases: 13 diffs,
  every one fix7 True to fix8 False on a paren-carrying literal
  filename (11 unit + 2 live), all the intended C7-1 FP removal.
  WRONG-DIRECTION moves: 0. No case went False to True, and no
  paren-free true runner went True to False. All four paren
  shapes are now closed: mid-name (new), glued `run_foo.py(x`,
  trailing `run_foo.py)`, `run_foo.py()`.

## Claim 2 (doc): head docstring reword, VERIFIED verbatim

`_runner_basename_head` docstring,
tests/realistic/run_batch3.py lines 2554-2557 in the fix8 blob:

"The paren drop re-exposed the fix5 false positive for MID-NAME
parens (`run_foo(a).py`, `run_(foo).py`, fix pass 8, Council 2
C7-1); those are now rejected in _script_basename_is_runner, so
the drop plus that rejection together close all four paren
shapes."

The old sentence ("dropping it is the same correction, not a new
regression") is gone. The rewording is accurate: the drop plus
the rejection together close all four shapes, as my probe proves
above.

## Claim 3 (log): "zero wrong-direction moves" corrected at both sites, VERIFIED verbatim

- Fix-pass-7 verification section,
  improvements/worker-y14b-restage-log.md lines 2277-2282:
  "moves ACROSS THE REDTEAM'S 98 CASES. CORRECTION (fix pass 8,
  Council 2 C7-1): the unqualified "zero wrong-direction moves"
  claim is refuted. The 98 cases did not include mid-name paren
  forms, and `run_foo(a).py` / `run_(foo).py` are fix5 True,
  fix6 False, fix7 True, a wrong-direction move (fix6 False to
  fix7 True) that the differential could not see."
- Council 3 verdict summary, same file lines 2425-2430: "NOTE
  (fix pass 8, Council 2 C7-1): Council 3's "zero
  wrong-direction moves" is scoped to its own differential,
  which did not include mid-name paren forms; `run_foo(a).py` /
  `run_(foo).py` (fix5 True, fix6 False, fix7 True) are a
  wrong-direction move outside that scope, fixed in fix pass 8."

Both sites are now scoped to their own differential and name
C7-1 as the wrong-direction move outside that scope. The
fix5/fix6/fix7 values stated (True/False/True) match my own
differential and the Council 2 probe baseline below.

## Claim 4 (C7-3): fix6 probe live helper patched, VERIFIED

In the fix8 commit, tests/realistic/y14b-fix6-probe.py live()
now scans /proc for children of the wrapper PID, kills each
child with SIGKILL, then kills the wrapper by exact PID and
waits, structurally the same as the fix7 probe's helper
(y14b-fix7-probe.py line 82 onward). Empirical check: I ran the
committed fix6 probe on the fix8 tree (71/71 PASS, below) and
scanned /proc afterward for its stub cmdlines: 0 leftover stub
processes. The 2-orphan-per-run leak is closed in practice, not
just in code.

## Claim 5 (probe counts and regressions): VERIFIED by independent re-runs

All run on the fix8 tree (working tree at 6f72fe3), counts by
PASS lines, 0 real FAIL lines in each:

- Author fix8 probe: 103/103 PASS, exit 0.
- Committed fix7 probe: 86/86 PASS, exit 0.
- Committed fix6 probe: 71/71 PASS, exit 0.
- Cross-check 1: the author fix8 probe run against the fix7
  blob (fix7.py as run_batch3.py in /tmp/y14b-fix8-rt/fix7tree)
  gives 97 PASS + 6 FAIL, and the 6 FAILs are exactly the C7-1
  checks (4 unit + 2 live, all `got True want False`). This
  reproduces C7-1 in fix7 and proves the fix8 tree corrects it.
- Cross-check 2: the Council 2 fix7 probe
  (/tmp/y14b-fix7-c2-probe.py, a reviewer probe, not the
  author's) run unmodified against fix7 gives 118 PASS + 2 FAIL,
  exactly the two C7-1 checks, reproducing the author's claim.
  The same probe with its fix7 module swapped for the fix8 file
  gives 119 PASS + 1 FAIL; the two C7-1 checks now PASS, and the
  single FAIL is the probe's own stale expectation
  (`diff("C7-1 run_foo(a).py bash -c", ..., False, True)` expects
  the old fix7 value True). That FAIL is the intended behavior
  change, not a regression; my own probe covers the bash -c form
  expecting False and passes.

## Claim 6 (gap): stated plainly, CONFIRMED as a limitation, not a new finding

The author H2 probe, fix2/fix3/fix4/fix5 probes, transcription
script, gate-dry and M1 probes are still lost (C6-5) and were
not re-run. Regression evidence is the committed fix6 + fix7
probes, the reviewers' fix7 probes, and the new fix8 probe, all
re-run above. The fix8 diff touches only the basename matcher
(2 hunks) plus probe docstrings, so the H2 launch gate, t10
transcription, and served-fixture paths are untouched by the
diff. I accept the gap as stated; it does not block this fix,
whose blast radius is one predicate with one call site.

## Hygiene

- 0 em dash, 0 en dash in the diff (counted with Python over
  the full 0857d19..6f72fe3 diff).
- Banned tool: the tool name occurs 2 times in the full diff, both inside
  the log's own prose hygiene sentences (the "0 ... in the code
  diff" sentence and the "no ... lines in the fix diff (grep 0)"
  sentence). 0 invocations or uses of it in code. INFO
  nit: the log's "(grep 0)" parenthetical is literally wrong as
  a grep statement, since grep returns those 2 self-referential
  prose hits; the substance (no use of the banned tool) is true. No author
  action required, recorded here so the record is accurate.
- No personal info in the diff: no email addresses, no names, no
  phone numbers (grep hits were hex hash strings only).
- No live Zen driving in this review. All live checks were
  python3 stub processes spawned by my own probe and killed by
  exact PID; final /proc scans show 0 remain.

## INFO notes (no author action required)

- R8-1 (sibling copies still carry the FP): the same
  `_script_basename_is_runner` matcher exists as separate copies
  in tests/realistic/launch_y13.py (line 254) and
  tests/realistic/run_codex_y5.py (line 3669), neither with a
  paren guard. I executed both functions standalone via AST
  extraction: `run_foo(a).py` returns True in both, `run_foo.py`
  returns True in both. Out of scope for this fix pass, which
  restages only run_batch3.py, and the author never claimed to
  fix them. Flagged for a future pass, not this one.
- R8-2 (stale line number): the author cites the call site as
  line 2724, the fix7 number; in the fix8 tree it is line 2735.
  Cosmetic only.
- R8-3 (banned-tool grep parenthetical): see Hygiene above.

## Verdict

GO. C7-1 is fixed in code and in docs at both log sites, C7-3
is fixed in the probe helper and verified empirically with 0
orphans, all regression probes pass on the fix8 tree, the
fix8-probe cross-check fails exactly the 6 C7-1 checks on the
fix7 blob, and my own independent differential finds 0
wrong-direction moves. The remaining notes are INFO only.

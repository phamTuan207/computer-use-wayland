# Batch 6 task 1: verify 2 bugs on main, then fix

Checked on origin/main at commit 7022cd4 ("docs: clone2 watchdog log 00:49 22/11, batch 6 assigned, STALL clone1 silent 128m").
Work window 2026-11-21T17:51:20Z to 17:58:02Z. All commands run in ~/workspace/computer-use-wayland.
No em dash or en dash in this file. No personal information.

## Bug 1: SyntaxError, STILL PRESENT, now FIXED by this task

### Verdict

STILL PRESENT on current main, and the fix is done in the working tree (uncommitted).
The coordinator's "py_compile OK" check was on the WRONG FILE, which explains the dispute.

### The file mix-up

- The batch 6 assignment (coord/clone2.md, commit 41e09a6) says the bug is in
  `tests/test_cursor_file.py` and that py_compile is OK on main fd77c0d.
- The batch 5 evidence check (docs/clone2-evidence-check-20261121.md, commit f2ca7e1)
  reported the bug in `tests/test_cursor_session.py` at line 566.
- Verified now on main 7022cd4:
  - `python3 -m py_compile tests/test_cursor_file.py`: exit 0, OK. The coordinator's
    check is correct for that file. That file has a DIFFERENT, separate problem
    (a setUpClass error, g++ 13.3.0 does not recognize `-std=c++26`, recorded in
    the batch 5 crawl); it is not this bug and it was not touched here.
  - `python3 -m py_compile tests/test_cursor_session.py`: exit 1,
    `SyntaxError: too many statically nested blocks` at line 570:
    `with patch.object(indicator,'Native') as native,patch.object(indicator,'listen'):`
- The line number moved from 566 (reported at a135e3f) to 570 (verified 23:38 21/11
  and again now) because the file changed between those checks. `git diff f2ca7e1 HEAD`
  for both files is empty: neither file changed since the evidence check, so nothing
  fixed the bug in between, and the report did not misidentify the file. The
  assignment text named the wrong file.

### Root cause, measured

The failing method is `Lifecycle.test_cleanup_exceptions_cannot_skip_restore`
(lines 565-577). It has only 3 block statements (1 `for`, 2 `with`), so the cause
is not ordinary nesting depth. CPython 3.12 counts EVERY context manager item in
a `with` statement as one nested block, and the limit is 20 nested blocks.
Measured with synthetic programs on this machine (Python 3.12.3):

- One `with` with 20 items compiles, with 21 items fails.
- 20 levels of nested `with` compile, 21 fail.
- The failing method nests: `for` (1) + outer `with` with 18 items (18) +
  inner `with` with 2 items (2) = 21 blocks, one over the limit.

A scan of the whole file (AST, counting each `with` item as one block) shows this
is the ONLY method over the limit (21 blocks); the next highest method is under
15 blocks, so no other method in the file is at risk from this limit.

### Fix (minimal, behavior identical)

File changed: `tests/test_cursor_session.py` only, 11 insertions, 8 deletions,
uncommitted. The inner `with` block was extracted into a helper method on the
same class, placed directly above the test:

```python
def _guardian_case_with_native_indicator(self, restore):
    import indicator
    with patch.object(indicator,'Native') as native,patch.object(indicator,'listen'):
        native.return_value.process.poll.return_value=None
        native.return_value.command.return_value='visible'
        no_hyprctl={**self.env,'PATH':''}
        self.assertEqual(session.guardian(no_hyprctl,1,'a'*32),1)
        restore.assert_called_once_with(no_hyprctl)
        (self.folder/'snapshot').unlink(missing_ok=True)
```

The test now calls `self._guardian_case_with_native_indicator(restore)` inside
the unchanged outer `with`, followed by the same final snapshot unlink. Patch
entry and exit order is unchanged: the 18 outer patches are entered, then the
helper enters Native/listen, runs the same assertions, and exits them before the
final unlink. Nesting after the fix: test method 19 blocks (for + 18), helper
2 blocks, both under the 20 limit. No test logic, assertion, or value changed.

### Proof

- `python3 -m py_compile tests/test_cursor_session.py`: OK (was exit 1).
- `import test_cursor_session`: OK, 34 test methods found (previously the module
  was unimportable, so 0 ran).
- Full module, venv python plus system dist-packages on PYTHONPATH
  (`PYTHONPATH=/usr/lib/python3/dist-packages ~/workspace/tools/venv/bin/python
  -m unittest tests.test_cursor_session`), wall 2026-11-21T17:57:16Z to
  17:58:02Z: Ran 34 tests in 46.436s, OK (skipped=1, the lua roundtrip test,
  Lua interpreter unavailable on this machine).
- Honest note: the first full-module run with venv python alone (no system
  dist-packages) gave 33 pass, 1 failure: the fixed test passed, but
  `test_capture_hides_badge_and_cursor_until_presented_frame` failed with
  "No module named 'PIL'" because the venv has no Pillow. That is the known
  environment split (venv lacks Pillow, system dist-packages has it), not a
  regression from this fix. Re-running the two affected tests with the proper
  PYTHONPATH passed both in 1.757s.

## Bug 2: shadow-run in scripts/cu.py, FIXED by 22b0fa3, CLOSED

### Verdict

FIXED on main already, confirmed behaviorally. No code change needed from this task.

### Evidence

- `git show 22b0fa3` ("fix: keep doctor probe runner callable", 2026-11-21):
  the only code change renames the local CLI subparser variable in `main()` from
  `run` to `cli_run_parser` (scripts/cu.py, old line 2346 area). The commit is an
  ancestor of current main (`git merge-base --is-ancestor 22b0fa3 HEAD` = yes).
- No `run=` assignment remains anywhere in `main()` (grep for `run=cli_sub` and
  `run = cli_sub` returns nothing). The ime probe at line 2453,
  `run(['fcitx5-remote'],env,timeout=1)`, sits inside `main()` (starts line 2307)
  and now resolves to the module-level helper `run()` at line 486.
- `python3 -m py_compile scripts/cu.py`: OK.

### Behavioral before/after

DoctorCliTests (`tests/test_session_driver.py`, 13 tests) exercise the exact probe
path: session_driver runs cu.py `main()` in-process with fcitx5-remote present.

- BEFORE, in a clean worktree at 22b0fa3^ (commit 97d28d5), wall
  2026-11-21T17:55:26Z (this run was done second, after the AFTER run below): Ran 13 tests, FAILED (failures=5). Example failure:
  `test_second_probe_failure_after_first_success` got
  `"fcitx5 probe failed: 'ArgumentParser' object is not callable"` instead of
  the expected probe error text. This is the exact failure mode the evidence
  check described.
- AFTER, on current main 7022cd4, wall 2026-11-21T17:55:18Z (run first):
  Ran 13 tests in 0.122s, OK. All 13 pass, including
  `test_remote_success_keeps_schema` (ime probe returns state and name) and
  `test_second_probe_failure_after_first_success`.

## Summary

- Bug 1 (SyntaxError): was still present on main 7022cd4 in
  `tests/test_cursor_session.py` line 570, not in `tests/test_cursor_file.py`
  as the assignment text said (that file compiles OK). Root cause is the CPython
  3.12 limit of 20 nested blocks with each `with` item counting as one; the
  method nested 21. Fixed minimally by extracting the inner `with` into a
  helper; full module now runs 34 tests OK in 46.436s. Change is uncommitted
  in `tests/test_cursor_session.py`.
- Bug 2 (shadow-run): already fixed on main by commit 22b0fa3, confirmed by
  before/after DoctorCliTests (5 failures before, 13/13 pass after). Closed,
  no change needed.

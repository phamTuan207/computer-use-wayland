# B2-2 review log: Phase B cross-run fix (compiled artifact)

- Item: B2-2, batch 2, assigned in coord/mochi.md commit f9a1a9f, 18:32 22/11/2026.
- Fix commit: 1230e79ddac5dad24b9229c9c59fd9bc1137ec55, on todolist-push, base 64c2ade (B2-1).
- Fix: 3 files, 129 insertions, 12 deletions.
  - scripts/code_exec.py, sha256 after fix e5879ace8ac628ec10d040d5456b262eb68a36efabf67a12fc11be0f7ce6d9a8.
  - scripts/snippets/manifest.json, sha256 3cc276cb2257878aed2dc75573b30294aab04be5e9b1e5ee908ae4c5189d1262 (only api_sha256 changed to the new code_exec.py hash; snippet sha256 and last_verified 2026-11-22 unchanged).
  - tests/test_snippets.py, sha256 23b00d6669b35ca489addf47a10663859cd2af15d0a78c71a4966cc89658c002 (3 new tests).
- Implementation deviation from the batch 1 proposal, confirmed correct and necessary by council 1, council 2, council 3, redteam, and verifier: the proposal said increment a session counter inside run_child, but run_child runs in a forked child via _fork_api_session (scripts/code_exec.py lines 445-520) that always ends with os._exit, so any child counter dies with the child and the next run() forks back to id 1. The fix allocates ids in the parent: self._snippet_run_next = 0 in __init__ line 1020, incremented only in _fetch_snippet lines 1626-1631 after every check passes (a failed fetch allocates nothing and can be retried; an id consumed by a later-failing snippet is skipped, never reused), returned as field snippet_run, and run_child lines 1846-1850 validates the allocated id is an int greater than 0, else raises CodeExecError "parent did not allocate a snippet run id". A new session starting at 1 is safe because _observation_runs and _dom_snapshot_runs are memory only, _load_state does not restore run records, and disk-loaded observations default to run 0 (outer program only).
- Age fix: _bound_observation None branch, lines 1218-1230, now selects the newest same-run meta then raises CodeExecError "observation is older than 120s; observe again" when older than OBSERVATION_MAX_AGE 120, same message as the explicit branch.
- Worker: completed 18:41:39 22/11/2026, worktree /tmp/mochi-b2-2.
  - Worker probe /tmp/b2-2-probe.py: 12/12.
  - tests.test_snippets 38/38 (35 old plus 3 new), gate tests/y1b_phaseb_real_run.py PASS 4/4, regression tests.test_codemode tests.test_code_exec 86/86, all with python3 -B and pycache cleared. The 3 new tests FAIL 3/3 on the old code. Reverting only manifest.json makes test_shipped_registry fail, proving the manifest update is required.

## Council 1: PASS

- Own probe 18/18.

## Council 2: PASS

- Own probe 13/13.

## Council 3: PASS

- Own probe 11/11.

## Redteam: KHONG PHA DUOC

- Own probe 46/46 on rerun.
- Warning: the shared worktree /tmp/mochi-b2-2 was being mutated by parallel reviewers doing revert tests, which caused one transient manifest hash mismatch (old hash f85ee4a read mid-revert); the final verifier must re-measure on committed bytes, not trust hashes read while the worktree is being edited. Verifier confirmed the worktree was restored intact, only the 3 files modified, hashes unchanged.

## Independent verifier: PASS, completed 18:49:15 22/11/2026

- Own probe 10/10 on new code, P1 to P5 FAIL on old code.

## Re-measurement on committed bytes (by mochi, 23:13-23:14 22/11/2026)

- Applied the worktree diff onto todolist-push HEAD 64c2ade, sha256s matched the three hashes above.
- python3 -B: tests.test_snippets 38/38 OK, gate tests/y1b_phaseb_real_run.py PASS 4/4, regression tests.test_codemode tests.test_code_exec 86/86 OK. Re-run after push: still 38/38, 4/4, 86/86.
- Push verified by `git ls-remote origin todolist-push`: 1230e79ddac5dad24b9229c9c59fd9bc1137ec55.
- Coord report: commit abbc7e1 on main, push verified.

## Minor non-blocking residuals (noted by redteam, not blocking)

- isinstance(allocated, int) accepts True because bool subclasses int, but the value only ever comes from the parent over JSON.
- The age check has a pre-existing TOCTOU shared with the explicit branch.
- api_handler still trusts the child-sent snippet_run tag, guarded only by the AST validator, unchanged by B2-2.

## Limit

- All checks used FakeBackend and FakeDomBackend, no live Zen.

## Note on this artifact

- This log compiles the review handoffs received on 2026-11-22 (worker, council 1, council 2, council 3, redteam, independent verifier). The original review subagent sessions did not commit their own artifacts; that gap is what the new rule fixes (see coord/mochi.md, rule from 23:57 22/11/2026: every council/redteam/verifier review must commit an artifact with a hash). This committed log is the verifiable artifact for B2-2; its commit hash is the proof.

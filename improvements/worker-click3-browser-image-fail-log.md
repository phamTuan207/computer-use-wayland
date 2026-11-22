# Browser-image failure investigation log (worker BROWSER-IMAGE-FAIL)

Worker BROWSER-IMAGE-FAIL, independent investigation + fix worker for
coordinator COORD-CLICK-3. Owner: Pham Tuan (repo-facing name).
Branch: todolist-push. Task received 08:29:48 22/11/2026 Asia/Ho_Chi_Minh.
All times below are Asia/Ho_Chi_Minh wall clock unless noted.
Elapsed: 08:29:48 to about 08:38, about 8 minutes plus one full-discover
run (219.697s).

## Scope and method

Fix the 2 remaining failures in the clean full discover at the VM head.
Per the standing no-self-healing rule this is an INDEPENDENT
investigation of S0-IMPL's change; S0-IMPL's own account was not taken
at face value, and the reconcile worker's account was re-verified
from source and by my own test runs (see below).

Worktree (clean, pinned HEAD): /tmp/click3-bif at e1a4e77, detached,
then branch click3-bif-fix for the fix commit. The dirty shared
checkout (with its stale .git/rebase-merge dir and staged
modifications to tests/test_click3_redteam2.py and
tests/test_zen_dom.py) was never touched. The 0668327 control
worktree /tmp/click3-bif-0668 was removed after its run.

Worktree lesson applied (from the reconcile log, re-verified here):
a fresh `git worktree add` lacks the untracked native build
artifacts, so before any run I copied native/pointer, native/wtype,
native/keyboard-protocol.c/.h and native/pointer-protocol.c/.h from
the main checkout into the worktree. Without them the full discover
would show environmental errors, not HEAD evidence.

Standing rules honored: full access, no em dash (U+2014) or en dash
(U+2013) anywhere in this file or in the test change (checked with a
Python scan after writing), never ydotool, no personal info in repo
files (owner name Pham Tuan only), explicit pathspec commits, never
plain git commit, never git add -A, every push verified with
git ls-remote. No fabrication: every claim below cites a diff, a
line number, or a test run I performed myself.

## 1. Failing-first reproduction at the pinned HEAD e1a4e77

08:31. In /tmp/click3-bif/tests:

`PYTHONPATH=../scripts:. python3 -m unittest test_browser_image.BrowserImage.test_persist_false_returns_rgb_without_state -v`

Result: Ran 1 test, FAILED (failures=2). The single test method
fails in BOTH subtests (mode='RGB' and mode='RGBA'), which is
exactly the 2 failures in the full discover (unittest counts
subtest failures separately). Assertion diff, identical in both
subtests:

```
AssertionError: {'backend': 'browser', ..., 'encode_ms': 0,
  'jpeg_quality': 90, 'jpeg_subsampling': 0}
  != {'backend': 'browser', ..., 'encode_ms': 0}
```

The actual meta carries two extra keys, 'jpeg_quality': 90 and
'jpeg_subsampling': 0, that the expected dict lacks. Every other
key and value matches. Failing test method:
test_persist_false_returns_rgb_without_state, in
tests/test_browser_image.py:147-163, assertion at line 159.

## 2. Control run: the test passes at 0668327 (my own run)

08:32. Fresh worktree /tmp/click3-bif-0668 at 0668327 (the VM
AMEND4 endpoint), same command shape on the whole file:

`PYTHONPATH=../scripts:. python3 -m unittest test_browser_image -v`

Result: Ran 9 tests in 0.134s, OK. All 9 tests pass at 0668327,
including test_persist_false_returns_rgb_without_state.

Git proof that nothing else changed between the passing tree and
the pinned HEAD:

- `git diff 0668327 e1a4e77 -- tests/test_browser_image.py` is
  EMPTY: the test file is unchanged between 0668327 and e1a4e77.
- `git diff --stat 0668327 e1a4e77 -- scripts/cu.py` shows
  scripts/cu.py as the only file changed in that pair (147
  insertions, 14 deletions).
- `git log --oneline 0668327..e1a4e77 -- scripts/cu.py` shows
  exactly one commit touched it: 18f2304 S0-IMPL.
- `git diff --stat 77c72be e1a4e77` shows only the reconcile log
  file itself (486 insertions); scripts/ and tests/ are identical
  between 77c72be (where the 2 failures were measured) and
  e1a4e77, so the 77c72be baseline numbers apply to e1a4e77.

## 3. Cause, from source (not from S0-IMPL's account)

S0-IMPL commit 18f2304 changed scripts/cu.py in two relevant ways
(diff read in full, `git show 18f2304 -- scripts/cu.py`):

- It added the pinned constants (cu.py:66-77 at head):
  CAPTURE_MAX_WIDTH = 960, CAPTURE_JPEG_QUALITY = 90,
  CAPTURE_JPEG_SUBSAMPLING = 0, CODEC_MAX_PIXEL_ERROR = 50, with
  the comment that q90 4:4:4 is the pinned codec (Pillow defaults
  to 4:2:0 at q90, measured max pixel error 80 vs 39).
- It added the two keys to BOTH save_observation meta paths:
  persist=False at cu.py:876-879 (`meta.update(...
  jpeg_quality=CAPTURE_JPEG_QUALITY,
  jpeg_subsampling=CAPTURE_JPEG_SUBSAMPLING)`) and persist=True
  at cu.py:908-911 (same two keys). On the persist path the
  encode itself uses exactly those constants (cu.py:885:
  `image.save(buffer, format='JPEG', quality=CAPTURE_JPEG_QUALITY,
  subsampling=CAPTURE_JPEG_SUBSAMPLING)`), so the keys are
  truthful provenance of the stored bytes there. S0 also added
  the keys to the compact_result desktop allowlist (cu.py:1529),
  so they survive compaction. No test anywhere pins the new keys
  (grep for jpeg_quality/jpeg_subsampling outside scripts/cu.py
  returns nothing in tests/ or other scripts), and no consumer
  rejects them: the full discover below shows zero failures
  besides the 4 pre-existing errors.

Verdict: TEST EXPECTATIONS STALE, code correct. The code emits
the right keys with the right values. On the persist=False path
no JPEG bytes are produced, but the meta already (pre-S0, and
pinned by this same test) claims image_format='JPEG' with
image_bytes=None: the dict describes the observation's codec
identity, not produced bytes, and the two keys complete that
identity with the true pinned parameters. Removing the keys
from the persist=False path only would make the two paths
inconsistent and would hide the codec parameters from exactly
the observe()/observe_screen() persist=False callers that the
J37 codec separation is for. So the fix is a test update, not
a code change.

## 4. Fix (commit e83b72d)

File: tests/test_browser_image.py only. 18 insertions, 1 deletion.

(a) In test_persist_false_returns_rgb_without_state, the expected
exact dict gains 'jpeg_quality': 90 and 'jpeg_subsampling': 0,
with a comment citing the emitting code (cu.py:876-879
persist=False, 908-911 persist=True, constants at 71-72, S0
commit 18f2304). The values are literals on purpose: they pin
the pinned parameters, so changing the constants must update
this test consciously instead of passing silently. The
assertion stays an exact full-dict assertEqual, so its strength
is identical: it still rejects any other added, removed, or
changed key.

(b) Strengthening, same file: the assert_saved helper (used by
all persist=True tests) now also asserts result['jpeg_quality']
== 90 and result['jpeg_subsampling'] == 0, with a comment
citing cu.py:71-72, the encode at 885, and the record at
908-911. This pins the persist-path provenance claim S0
introduced. No assertion was weakened anywhere; the two new
assertions make the suite strictly stronger on the persist
path.

No code file was changed. No test was deleted, skipped, or
loosened.

## 5. Verification

08:33. Test file after the fix, /tmp/click3-bif/tests:

`PYTHONPATH=../scripts:. python3 -m unittest test_browser_image -v`

Result: Ran 9 tests in 0.128s, OK.

08:32:32 to 08:36:13. Full discover at the fixed tree (worktree
with the fix applied, before commit), command from tests/:

`PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"`

Result: Ran 1974 tests in 219.697s, FAILED (errors=4, skipped=17).
Failures: 0. Exit code 1 comes from the 4 errors only.

Before/after full discover:

| Run | Ran | Failures | Errors | Skipped |
| --- | --- | --- | --- | --- |
| 77c72be baseline (reconcile log, code-identical to e1a4e77) | 1974 | 2 | 4 | 17 |
| Fixed tree (this worker, log /tmp/click3-bif-discover.log) | 1974 | 0 | 4 | 17 |

The 4 errors are exactly the AMEND4 baseline pre-existing
errors, verified from the tracebacks in the log:

1. test_a11y_skeleton: ModuleNotFoundError: No module named
   'tests' (import failure).
2. test_cursor_file setUpClass: g++ -std=c++26 unrecognized
   (toolchain too old).
3. test_perf_evidence test_valid_normal: FileNotFoundError
   docs/benchmarks/r5_cdp_aggregate.json.
4. test_perf_evidence test_valid_optimized: same missing file.

No EPERM/tempfile lines appear in the discover log (grep for
eperm/tempfile/PermissionError/Errno 1 returns nothing), so no
environmental failures pollute the count. The 2 failures are
gone, nothing new failed, total and skipped counts unchanged.

## 6. Commits and pushes

Fix commit, 08:36:44 +07, explicit pathspec immediately after
staging (no plain git commit, no git add -A):

- `git add tests/test_browser_image.py`
- `git commit -m "test: update browser_image expectations for S0 J37 jpeg keys (persist=False meta + persist-path pin)" -- tests/test_browser_image.py`
- Hash: e83b72ddbbc4ddae21d8c25a11eeac41b5ffb688, parent e1a4e77.

Push, about 08:37 +07: `git push origin click3-bif-fix:todolist-push`.
Remote HEAD was verified still e1a4e77 before the push
(`git ls-remote origin todolist-push`), so the push was a clean
fast-forward e1a4e77..e83b72d. Verified after: `git ls-remote
origin todolist-push` returns
e83b72ddbbc4ddae21d8c25a11eeac41b5ffb688 refs/heads/todolist-push.

This log file was committed after the fix push so it can record
the verified remote HEAD:

- `git add improvements/worker-click3-browser-image-fail-log.md`
- `git commit -m "docs: BROWSER-IMAGE-FAIL log, S0 J37 jpeg keys, failures 2 to 0" -- improvements/worker-click3-browser-image-fail-log.md`
- This log commit is a child of e83b72d on todolist-push; its own
  hash and the post-push ls-remote verification are recorded in
  this worker's final report to the coordinator, since a file
  cannot contain its own commit hash.

Note: the local todolist-push branch in the main checkout sits
at 24e0df9, a parallel re-created reconcile commit that is NOT
a descendant of e1a4e77; it was left untouched. The remote
todolist-push moved e1a4e77 -> fix -> this log, all
fast-forward from the pinned HEAD.

## 7. Open items for the coordinator

- None from this worker. The 4 remaining errors are the known
  AMEND4 baseline pre-existing errors, out of this task's scope.
- The local todolist-push branch (24e0df9) diverges from the
  remote (now past e1a4e77); whoever owns that checkout should
  fast-forward or rebase it, not this worker.

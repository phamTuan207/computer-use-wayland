# Worker Y1B-RPC-LAND log: land the RPC rework of code_exec.py

Owner: the owner. Branch: todolist-push. Parent: COORD-CLICK-3.
Task: land the uncommitted socketpair RPC rework of scripts/code_exec.py
(_fork_api_session, _ApiChannel) plus the Y1B-FIX log, one commit,
message from /tmp/y1b-rpc-commit-msg.txt verbatim.

No em dash or en dash in this file. Wall-clock times Asia/Ho_Chi_Minh.
Never ydotool. No personal info on GitHub.

## 07:50 22/11: start, verification of the working tree

HEAD at start: 5dcf2b3 (DOMZEN-FIX, on top of 17fdb9b).
Read improvements/worker-y1b-fix-log.md: confirmed it is the Y1B-FIX
worker's log, describes the RPC rework and the 19/22 probe run.
Read /tmp/y1b-rpc-commit-msg.txt: subject "Y1b fix 2a/2b (RPC): API
calls run in the parent, snippet in a forked child", to be used verbatim.
git diff --stat scripts/code_exec.py: 281 insertions, 122 deletions,
exactly the RPC rework size stated in the task. Diff replaces _fork_run
with _ApiChannel, _kill_child, _reap_child, _exception_from_response,
_fork_api_session; no SAFE_BUILTINS/chr/ord changes mixed in, no other
author's changes in this file. git diff --check clean. VERDICT: the
diff is exactly the RPC rework, safe to land. Other workers'
uncommitted edits in other files (cu.py, first_action.py,
sync-installed.py, zen_dom.py, untracked logs/tests) are NOT touched;
commit uses an explicit pathspec for the two files only.

## 07:51-07:53: EPERM storm, remote ahead, concurrent workers in this checkout

07:51 git fetch origin failed: "unable to write loose object file:
Operation not permitted", unpack-objects failed. git add + git commit
then failed the same way (exit 128). gh api works (logged in as
phamTuan207). Remote todolist-push HEAD at that point: 656f0744, later
6e1324a. First contents-API check of code_exec.py WITHOUT ?ref=
returned main's pre-hardening file (41395 bytes, no chr/ord, format
present); that was my own missing ref parameter, not a remote
revert. With ?ref=todolist-push the remote blob is e271fbfc,
byte-identical to local HEAD. Remote history DOES contain d7c0945,
3f1b951, 17fdb9b, 5dcf2b3; the 7 commits after 5dcf2b3 touch only
improvements/*.md logs. worker-y1b-fix-log.md does not exist on the
remote (404), so it is safe to add.

07:52 second fetch SUCCEEDED (storm window opened): origin/todolist-push
6e1324a. The 7 incoming commits touch only log files, but 6 of them
existed as untracked duplicates in this tree; all 6 verified
byte-identical to the remote blobs (cmp), backed up to
/tmp/y1b-rpc-backup, then removed so the fast-forward could proceed.

CONCURRENT WORKERS: HEAD moved under me during this task. 07:50 HEAD
was 5dcf2b3; by 07:52 another worker had committed 4985b45 (S0-IMPL)
on top of it, then the branch was fast-forwarded to 6e1324a and two
more commits landed (18f2304 S0-IMPL again, 2de4c31 codex amend4
resume log); HEAD is now 2de4c31 and origin/todolist-push is 2de4c31.
The index currently holds staged deletions of 7 log files and a
staged modification of worker-probe-s0-log.md that belong to the
other worker(s); I did NOT stage those and I will NOT touch them.
My commit uses an explicit pathspec for my 3 files only, which
ignores other staged changes, and I verify the landed commit's file
list immediately after. My code_exec.py diff is re-verified against
the new HEAD: still exactly 281 insertions, 122 deletions, HEAD blob
still e271fbfc. 4985b45/18f2304 touch S0 files only, never code_exec.py.

## 07:54: landing (local git, explicit pathspec)

07:54 first commit attempt failed: /tmp/y1b-rpc-commit-msg.txt was
GONE ("could not read log file: No such file or directory"). The
file existed at 07:50 when I read it; something (another worker or a
/tmp sweep) removed it in between. I recreated it verbatim from the
read at 07:50 with muse.write, and the landed message was verified
against the GitHub API afterwards (see below), byte-identical to the
original. HEAD had moved again in the meantime (5f1abc9, then
8817a90); my earlier git add had also been undone by another
worker's index operation, so I re-added and committed immediately.

07:56 COMMITTED fd63a7d08cb23451f82a9acc4579da4e718839dd, parent
8817a90, exactly 3 files, explicit pathspec: scripts/code_exec.py
(403 lines changed, 281 insertions, 122 deletions),
improvements/worker-y1b-fix-log.md (new, 173 lines),
improvements/worker-y1b-rpc-land-log.md (new, 63 lines). The other
worker's staged deletions/modifications stayed in the index
untouched; git show --stat confirms only my 3 files are in fd63a7d.
07:56 git push: "Everything up-to-date" (another worker's push loop
had already pushed fd63a7d within seconds of my commit, or the push
itself landed it; either way the remote shows it). git ls-remote
origin todolist-push = fd63a7d08cb23451f82a9acc4579da4e718839dd at
push time. Remote blob check: HEAD:scripts/code_exec.py =
bb74f6e48fb450bb93b9bc51568b9f1caff1f5e5, remote contents API at
ref todolist-push returns the same sha. Remote commit message
verified via API, verbatim. By 07:55 UTC the remote branch had
already moved on to c2c0bbf (TESTREPAIR-A) on top of fd63a7d;
fd63a7d is in remote history, no force-push used anywhere.

## 07:55-07:56: verification, 81 executor tests on the landed tree

Clean worktree /tmp/y1b-rpc-verify at detached HEAD fd63a7d
(code_exec.py contains _fork_api_session, 3 hits). Full run 07:55:
python3 -m unittest tests.test_codemode tests.test_code_exec -v,
14.275s, exit 1. Ran 81 tests: 80 PASS, 1 FAILURE, 0 ERRORS.
The 13 tempfile EPERM errors from the Y1B-FIX run are GONE (gate
open); no environmental failures at all in this run.
The 8 fork-broken tests: 7 of 8 now PASS, confirmed by name:
test_happy_path_loops_and_asserts (backend.calls), ok;
test_failed_assert_after_api_calls_keeps_partial_result
(backend.calls), ok; test_d1_program_looks_up_chromium_right_after_
dom_start (windows_calls), ok;
test_multi_step_program_mixes_desktop_and_dom_actions (kinds count),
ok; P4 tests (backend.captured, Vietnamese bytes), ok;
test_dom_snapshot_binding_persists_across_runs (observations/DOM
snapshots), ok. The 8th is the one known-open failure below.
The ONLY failure: test_execute_namespace_pins_safe_builtins
(tests.test_codemode.TestExecute), AssertionError 0 != 1 at
test_codemode.py line 150 (len(captured), 1). This is the codemode
mock-exec pin test Y1B-FIX left OPEN for the parent/council: it
patches builtins.exec in-process and counts calls in a parent-side
list, which a fork invalidates. The pin itself is intact (probe
4a-prime passes behaviorally). Test file NOT edited. Full verbose
log saved at /tmp/y1b-rpc-tests.log.

## Status at handoff

LANDED: fd63a7d on origin/todolist-push (verified by ls-remote,
remote blob match, remote message match). Tests on the landed tree:
80/81 pass, 1 failure (the known-open codemode pin test), 0 errors,
0 environmental failures. OPEN: the codemode mock-exec pin test,
needs a parent/council decision on amending its capture mechanism
(Y1B-FIX proposal stands); and this log's own post-landing section
is landed by the follow-up commit below, not in fd63a7d.

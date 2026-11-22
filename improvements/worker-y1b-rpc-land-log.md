# Worker Y1B-RPC-LAND log: land the RPC rework of code_exec.py

Owner: Pham Tuan. Branch: todolist-push. Parent: COORD-CLICK-3.
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

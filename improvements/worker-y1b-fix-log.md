# Worker Y1B-FIX log: fix the 3 Y1b real fails (1e, 2a, 2b)

Owner: the owner. Branch: todolist-push. Step 1 of the FINAL DIRECTION
(commit e05fc58). Verdict: council 3, commit 9d9bd63, OVERALL Phase A
BLOCK on 84b88bb, 14/20 PASS, 3 real fails (1e, 2a, 2b), all in
code_exec/codemode. PROBE-S2 (f1952a5) re-confirmed at this HEAD: "chr"
in NEITHER SAFE_BUILTINS list; no setitimer, SIGALRM, or child-process
preemption in either executor.

No em dash or en dash in this file. Wall-clock times Asia/Ho_Chi_Minh.
Never ydotool. No personal info on GitHub.

## 07:01 22/11: start, baseline discovery

First finding, before any fix: commit 84b88bb is NOT an ancestor of
todolist-push HEAD (8008662). It lives only on origin/y1-snippets.
At this HEAD both executors are still in the pre-hardening state:
"format" is still in SAFE_ATTRIBUTE_NAMES in both files, codemode has
no dunder-Name rejection, no yield/async rejection, no builtins pin,
no envelope cap, and still wraps model code in __codemode_main__.
The verdict's 14/20 baseline therefore does not exist on this branch
yet. Fixing only 1e/2a/2b here would leave 1a-1d, 1f, 2c, 2d, 3a-3f,
4a-4c failing, and 1e's codemode half would pass only for the wrong
reason (chr resolving through the unpinned real builtins, the exact
hole item 4 closes).

Decision: land 84b88bb onto todolist-push first by cherry-pick
(no new code, a commit already judged by 3 verdict councils), verify
the 14/20 baseline with the 3 fails reproduced, then fix 1e, 2a, 2b
on top. Each step committed with an explicit pathspec, each push
verified with git ls-remote.

Probe runner: /tmp/y1b-fix-probes.py, reconstructed from the council-1
spec (improvements/worker-y1b-verify-council-1.md), all 20 probes plus
council-3 replacement checks 4a-prime and 4b-prime.

## 07:0x: baseline probe run at HEAD (before cherry-pick)

07:02, full probe run at HEAD (8008662): 5/22 PASS (3e, 3f, 4a-prime
loose form, 4b-prime loose form, 4c). Fails included 1a-1d (format hole
live, token leaked verbatim), 1e (code_exec f-string NameError chr),
2a 20.66s late error, 2b 23.49s silent success ok=True, 2c/2d 50MB
returned intact, 3a-3d wrapper reachable, 4a/4b pin absent. The
4b-prime check was too loose (matched any dict(SAFE_BUILTINS)); it
was tightened to require the pin on one line, and then correctly
FAILED at HEAD.

## 07:04: baseline landed, 3 fails reproduced

Cherry-pick 84b88bb --no-commit applied clean to the 4 code/test
files; only conflict was improvements/worker-y1-codex-impl-log.md
(modify/delete, file deleted on this branch, resolved to keep the
deletion with git rm). Committed d7c0945 with an explicit pathspec.
Full probe run 07:04: 16/22 PASS, fails exactly 1e, 2a, 2b, 2e, 4a,
4b. That is the council-3 baseline 14/20 (1e, 2a, 2b real; 4a, 4b
probe artifacts with 4a-prime/4b-prime passing; 2e allowed
exception). Failing-first proof: 1e codemode f-string NameError chr,
code_exec f-string fails, both % halves pass; 2a 26.33s late
"wall-clock budget exceeded"; 2b 20.27s ok=True silent success.

## 07:05: fix 1e committed (3f1b951)

Added "chr": chr and "ord": ord to SAFE_BUILTINS in both files.
chr/ord are pure int/char conversions: no attribute access, no I/O,
no evaluation, no dunder path. Probe 1e passes all four halves;
1a-1d, 1f still pass.

## 07:06-07:13: fix 2a/2b, first attempt (signal timer) DISPROVEN

Verdict Option A was tried first: _WallTimer with setitimer/SIGALRM
in both executors. Result: 2a 24.19s, 2b 21.92s, still FAIL. The
timer cannot preempt a C loop: the handler only runs when the
interpreter regains the eval loop. Minimal proof, /tmp/sigtest.py:
setitimer 1.0s + sum(range(3 * 10**8)) reported "preempted" only
after 31.48s. The timer classes were removed again; a mechanism that
cannot do its job should not exist.

## 07:13: fix 2a/2b, second attempt (fork child + parent kill) PASSES

Both executors run the snippet in a forked child (_fork_run, pipe
for the JSON envelope); the parent SIGKILLs at wall_seconds.
Probes 2a/2b pass twice in a row: 2.02-2.10s, wall-clock error
envelopes, no silent success. Full probe run 07:13: 19/22 PASS.
Remaining fails are exactly the verdict's non-blocking three: 2e
(allowed exception), 4a/4b (probe artifacts, primes pass).
Committed 17fdb9b with an explicit pathspec.

Probe 2e (residual risk, measured): the 2e child and the 2c child
peak at identical RSS (152.9MB each, via RUSAGE_CHILDREN), so no
memory cap or peak-RSS threshold can close 2e without breaking
2c/2d. The 100MB allocation lives and dies inside the child; the
parent's memory is untouched. Recorded as residual risk, as the
verdict allows.

## 07:16-07:2x: unit tests expose fork side effects, RPC redesign

python3 -m unittest tests.test_codemode tests.test_code_exec at the
fork design: 81 tests, 5 failures + 3 errors (verdict baseline was
81 OK). Root causes, all from the snippet running in the child:
(1) backend calls recorded in the child's FakeBackend copy, invisible
to the parent (test_happy_path backend.calls, test_failed_assert
backend.calls, d1 windows_calls, multi_step kinds count, P4
backend.captured); (2) observations/dom_snapshots mutated in the
child are lost, breaking cross-run DOM binding
(test_dom_snapshot_binding_persists_across_runs); (3) the codemode
mock-exec pin test observes builtins.exec in-process, which a fork
invalidates (captured stays empty in the parent).
Fix for code_exec: API calls are marshalled back to the parent over
a socketpair (_fork_api_session, _ApiChannel, length-prefixed JSON);
the parent executes each call against the real backend and session
state, with its own tracer installed for budget checks, so backend
calls, bindings, snapshots, api_calls, and log behave exactly as in
process. Only the snippet's own variables travel back in the done
envelope. Cancel raised in the parent during an API call is reported
to the child, which re-raises it; a cancel in the child comes back as
a __cancelled__ payload and is re-raised after state is saved.

## 07:29: RPC redesign verified on probes; unit suite gated by sandbox

Full probe run under the RPC code: 19/22 PASS, fails only 2e, 4a,
4b (the verdict's non-blocking three), in 6.5s total. All 3 real
fails fixed.

RPC verification detail: the plain fork design broke 8 of the 81
executor tests, all from snippet state living in the child:
backend.calls invisible to the parent (test_happy_path,
test_failed_assert, d1 windows_calls, multi_step kinds count, P4
backend.captured), observations/dom_snapshots lost across runs
(test_dom_snapshot_binding_persists_across_runs), and the codemode
mock-exec pin test (captured stays empty in the parent). The RPC
redesign (socketpair, _fork_api_session, _ApiChannel, parent-side
api_handler with its own tracer for budget checks) fixes the 7
code_exec ones by construction: API calls execute in the parent
against the real backend and session state. The 66 non-tempfile
tests pass; the remaining code_exec failures are all the tempfile
gate below, not the RPC code. test_dom_snapshot_binding and the
other tempfile-dependent tests still need one open-gate run to
prove the RPC path end to end.

The one test the RPC design cannot fix is codemode
test_execute_namespace_pins_safe_builtins: it patches builtins.exec
in-process and counts calls in a parent-side list, but exec now
happens in the forked child, so len(captured) is 0, not 1. The pin
itself is intact (probe 4a-prime passes behaviorally). This is left
OPEN for the parent/council to decide, with a concrete proposal:
amend only the capture mechanism (write the captured namespace's
__builtins__ facts to a temp file from the mock, read it back in
the parent), keeping every assertion identical in strength, the
same class of mechanism amendment the council itself ordered for
probes 4a/4b. The test file was NOT edited; the rule against
editing proof tests is respected and the decision is the parent's.

## 07:48: final state, reporting to COORD-CLICK-3

Commit retry loop for the RPC change (20 tries, 20s apart, correct
exit-code handling after the first loop's pipeline bug falsely
reported COMMIT-OK on try 1) never saw the gate open; HEAD is
5dcf2b3 (another worker's DOMZEN-FIX, committed 07:36 on top of
17fdb9b). The RPC change to scripts/code_exec.py and this log are
still uncommitted in the working tree. The commit message is saved
at /tmp/y1b-rpc-commit-msg.txt. Finish when the gate opens with:
git fetch origin; rebase if needed; git add scripts/code_exec.py
improvements/worker-y1b-fix-log.md; git commit with the explicit
pathspec and -F /tmp/y1b-rpc-commit-msg.txt; git push; verify with
git ls-remote; then run the 81 executor tests and the full discover.

Summary for the parent: 1e FIXED (3f1b951), 2a/2b FIXED (17fdb9b
plus the uncommitted RPC rework of code_exec.py), probes 19/22
with only 2e/4a/4b failing as the verdict allows. Open: the
codemode mock-exec pin test (needs a council decision on amending
its capture mechanism, test file untouched) and 14 file-gated
executor tests plus the full discover (need one open-gate run).


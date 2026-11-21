# Council Voice 1 (correctness) verdict on Worker F1 guardian-startup fix

Verdict: AMEND

Commit reviewed: 5033c9d on todolist-push, plus log commit 708bef0.
Scope: diagnostic code fix only. It names the cause of a dead guardian, it does
not by itself restore sessions. Live activation (plan B) is still pending and
is not approved or blocked by this verdict. No live state was changed by this
review. All laptop checks below were read only.

## What was verified and holds

1. Layer 0 and Layer 1 hold. The live compositor still answers
`hyprctl cu-cursor status` with `unknown request` and exit code 0, verified
read only on the laptop at 22:47 +07 with the live instance signature from
uwsm. scripts/cursor_theme.py check_guard passes that raw text to guard_reply,
and the old guard_reply did an unconditional json.loads, so JSONDecodeError
was the first throw. The fix converts it to a RuntimeError naming the missing
backend and the remedy. Correct mechanism, correct layer.

2. Layer 2 holds. Live `hyprctl -j plugin list` shows hyprbars only. No
cursor-guard socket directory exists under /run/user/1000. Both plugins are
unloaded in the live compositor.

3. Layer 3 holds. The loader log
~/.cache/agent-computer-use/logs/visuals.jsonl shows the current instance
11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825 failing at stage
manifest_validation with ValueError `profile does not match the pinned optics
source` at time 1795249050, exactly as the log claims. The two earlier
instances match too: 1795086072 complete, 1795201820 same manifest failure.

4. Drift repair (plan A) holds and was right. Laptop optics sha256 is now
9a151634 in both the repo copy and the installed copy, the two manifests are
byte identical, the manifest pins profile_sha256 9a151634 and library
hyprglass-199153ae, and the guard library cursor-guard-06712eaf is present.
The loader re-run record at time 1795275379 now fails at fresh_login_gate,
not manifest_validation, which proves the pin now matches. The installed
manifest paths are absolute installed-tree paths, which is what
scripts/visuals.py expects, and its setup_instance is an old login instance,
so it cannot trip the same-instance refusal at the next login.

5. Deployed scripts match the reviewed commit. Installed cursor_theme.py md5
502a49414b097444b0114d09c7c5d3a0 and cursor_session.py md5
5d6c580a986bf2d24a4ea257925cce2a are identical to the VM repo files at
5033c9d.

6. guard_reply covers every caller. The three call sites all funnel through
guard_reply: check_guard (scripts/cursor_theme.py:123, hyprctl status, str),
restore release (scripts/cursor_theme.py:188, hyprctl release, str), and
Guard.receive (scripts/cursor_theme.py:163, socket, bytearray). The bytes and
bytearray decode branch handles the socket path. The live negative test in
the log shows the envelope now reads `session guardian startup failed: cursor
guard reply is not valid JSON (got: unknown request)...`, which is the
behavior fix D was built for.

7. No pipe-buffer deadlock from the drain thread. Only stderr is drained on
a thread, stdout carries only the short `ready` and `registered` lines, the
deque is capped at 32 lines, and the tee preserves the Escape-binding
warning that the first version swallowed. The drain thread catches
OSError and ValueError, so a closed stderr at shutdown ends it quietly.

8. VM test evidence for the theme file reproduces. tests.test_cursor_theme
runs 34 tests OK on the VM python 3.12, confirmed 5 consecutive runs after
one flaky first run, see finding F8.

## Required changes (AMEND)

A1. Close the drain race before reading the tail, scripts/cursor_session.py
around lines 247-250. supervise reads guard_errors the instant select says
stdout is ready or the 15 second timeout expires, with no wait for the
guardian to exit and no join of the drain thread. A fast guardian death can
therefore still produce a bare `session guardian startup failed` envelope,
because the drain thread may not have consumed the stderr pipe yet. That is
the exact failure fix D exists to remove, and the live negative test passing
once does not prove the race closed. Required: after the not-ready branch is
taken, wait for the guardian to exit (guard.poll or a short guard.wait, at
most about 1 second), then join the drain thread with a short timeout, and
only then read guard_errors. Joining first also removes the concurrent
iteration of the deque while the drain thread appends.

A2. Name the cause on the driver-registration path too,
scripts/cursor_session.py line 260. `raise RuntimeError('driver registration
failed')` carries no detail. If the guardian dies between `ready` and
`registered` (indicator loss, cursor guard lost, or a late check_guard style
failure), the cause is lost the same way the startup path used to lose it.
Required: include the drained stderr tail in this error in the same form as
the startup error, reusing the settled drain from A1.

A3. Catch UnicodeDecodeError in guard_reply, scripts/cursor_theme.py
lines 100-101. json.loads on a non-UTF8 bytearray raises UnicodeDecodeError,
not JSONDecodeError. Verified on the VM: guard_reply(bytearray(b'\xff\xfe\n'))
and guard_reply(b'\xff\n') both escape as a raw UnicodeDecodeError, bypassing
the new named error entirely. The socket path is the one place non-UTF8 bytes
can arrive, so the stated coverage of the Guard.receive caller is incomplete.
Required: catch (json.JSONDecodeError, UnicodeDecodeError) and raise the same
named RuntimeError. The shown text already decodes with errors replace, so
no other change is needed there.

A4. Make the new Lifecycle test prove fix D, not just fix C,
tests/test_cursor_session.py lines 777-793. The test asserts `not valid JSON`
and `may not be loaded` in combined stdout plus stderr. That text reaches
combined through two independent routes: the guardian prints str(exc) to its
own stderr, which the drain thread tees to the supervisor stderr, and the
supervise RuntimeError, which scripts/cu.py prints as the JSON envelope.
The test therefore passes even if supervise raised the old bare error, so
fix D is unproven by any test and rests only on the single live negative
run. Required: assert the exact envelope string
`session guardian startup failed: cursor guard reply is not valid JSON` in
stdout, or assert on the raised supervise error directly. Note the test
cannot run on the VM at all, see F7, so this assertion must be run and
recorded on the laptop python 3.14.

A5. Correct the Layer 4 claim in the log, improvements/worker-f1-guardian-fix-log.md.
The log states the old laptop manifest pin 674441ea matches NO known optics
version, having checked only 09a8df7, 9ecc167 and 78b0615. That is wrong.
Verified in VM git history: commit d27ad0a optics sha256 starts 674441ea
(blur 0.10 bottle candidate). The true drift was subtler: the laptop optics
file was from 09a8df7 (545455d3, blur 0.0) while the manifest pin was from
d27ad0a (674441ea, blur 0.10), so optics and manifest came from two different
stale commits, and both were stale against b2afcd1 (9a151634, blur 0.15).
Required: correct the log line and the Layer 4 summary. This does not change
the repair, which remains correct, but the root-cause record must not assert
a false negative.

A6. Do not declare the drift fixed until the recurrence path is tracked.
The code fix is diagnostic only, and the one-time copy in plan A does not
stop the drift recurring. The log itself records the mechanism: the sync
re-pinned the installed manifest but never re-pinned the laptop repo manifest
or its optics file after the blur 0.15 change. At the next optics change the
login loader will fail at manifest_validation again and sessions will die
the same way, only with a clearer message. Required before live activation
is declared complete: file a tracked follow-up (owner-visible todolist item
or issue) to make setup or sync re-pin the repo manifest and optics together
with the installed copies on every optics change, or to make the loader
refuse to run with a stale pin at setup time. This item may land separately
from this diff, but it must exist and be named in the log, not left implicit.

## Other findings (not blocking this diff, record them)

F1. guard_reply mislabels any non-JSON reply as a missing backend.
scripts/cursor_theme.py lines 104-113 says `the cursor backend may not be
loaded` for every JSON failure, including an empty reply, a truncated JSON
reply from a loaded but buggy guard, or socket garbage while the backend is
loaded. The word `may` hedges it, and the live case is the unloaded plugin,
so this is acceptable for now, but a tighter form would name the missing
backend only when the reply is exactly `unknown request` and otherwise say
only that the reply is not valid JSON. Recommend, do not require.

F2. session_remote.py swallows the named error, scripts/session_remote.py
lines 320-327. check_guard is called there and any exception is wrapped into
a generic BrokerError `cursor backend is not idle and ready`, with the
original kept only as __cause__. Any broker-driven session start therefore
still hides the named cause in its own message. Recommend including
str(error) in the BrokerError message.

F3. A mid-run guardian death is still silent. In supervise, if the guardian
dies after the driver starts, the loop terminates the driver and supervise
returns exit code 1 with no error message at all. That is outside the
startup scope of this fix and pre-existing, but it is the same silent-death
class and should be a follow-up, not assumed fixed by this diff.

F4. restore swallows the named error by design. cursor_theme.restore calls
guard_reply for release, and cursor_session.restore catches RuntimeError and
retries, then prints a generic cleanup-failed message with the snapshot
retained. Acceptable for a cleanup path, but the named cause will not
surface there. Noted only.

F5. first_action.py still matches. scripts/first_action.py lines 166-172
treats a session-start failure as `session guardian startup failed`,
`Expecting value`, or `cursor guard` in combined output. The new message
removes `Expecting value` but keeps the other two matches, so no fallback
regression. Verified by reading, not by running.

F6. Pre-existing second wait without a timeout in the finally block,
scripts/cursor_session.py around line 282. After guard.wait(timeout=20),
guard.terminate() is followed by guard.wait() with no timeout. A guardian
that ignores SIGTERM would hang supervise cleanup forever. Pre-existing,
not introduced by F1, and the guardian does install a SIGTERM handler, so
note it only.

F7. Session-test evidence is laptop-only and unreproducible on the VM.
tests/test_cursor_session.py does not compile on the VM python 3.12:
SyntaxError `too many statically nested blocks` at line 570 in
test_cleanup_exceptions_cannot_skip_restore. Pre-existing, last touches
0ba9584 and e3d2cc7, not caused by F1. The file has 34 test methods
including the new one, which matches the log `full file run 2: 34 tests OK`,
but the log `targeted run 36 then 37 tests` counts are not directly
comparable and no exact commands are recorded, so the VM cannot reproduce
the session-test evidence. The live negative test is the only
independently checkable proof of fix D, and A1 plus A4 exist because one
live run plus an unisolating test is thin evidence for a race-prone path.

F8. One flaky theme-test failure observed on the VM, then 5 consecutive
passes. The first VM run of tests.test_cursor_theme failed with 1 error:
BrokenPipeError in Guard.__init__ sendall at scripts/cursor_theme.py line
148, a socket test race. Five reruns passed 34 of 34. F1 did not touch the
Guard.__init__ send path, so this is a pre-existing flake, not a regression.
Recorded because a single `34 OK` claim without reruns would have hidden it.

F9. The old manifest library pin hyprglass-d086bc43 quoted in the log could
not be re-verified after the repair, because plan A overwrote the laptop
manifest. The optics-side claims were all re-verified live, the library-side
claim is taken from the log only. Noted for the record, no action needed.

## Bottom line

The root-cause chain is proven live at every layer except for the one false
detail corrected in A5. The guard_reply fix is correct and covers all three
callers. The supervise drain is the right design and introduces no deadlock,
but A1 shows its headline guarantee still has a race, A2 shows a sibling
startup path with the same silence, and A3 shows a real bypass on the socket
path. Fix A1 through A6, re-run the theme tests on the VM and the session
tests plus the amended Lifecycle test on the laptop python 3.14, and this
becomes a GO. The fix must not be presented as restoring sessions: until
plan B live activation runs and a session starts with a visible pill, the
session still fails, only with a clear error now.

# Council Voice 3 verdict: Worker F1 guardian startup fix

Verdict: AMEND.

Role: tests and user-visible behavior. Independent review of commit 5033c9d
and the log in improvements/worker-f1-guardian-fix-log.md. Read only. Nothing
modified, nothing committed, no session started, no plugin loaded, no screen
driven. All times Asia/Ho_Chi_Minh, 21/11/2026.

## What I verified myself

1. test_cursor_theme on the VM, Python 3.12.3: 34 tests, OK. Re-ran 5 times,
   all OK. The new test test_guard_reply_names_missing_backend_on_non_json_reply
   (tests/test_cursor_theme.py:213) passes on str, bytes and bytearray inputs
   and through check_guard.
2. test_cursor_session on the laptop, Python 3.14.10, in /tmp/f1-test: I
   re-ran the full file myself, detached because SSH dies after about 30
   seconds. Result: 34 tests, OK, 30.574s. test_cursor_theme there: 34 tests,
   OK, 0.126s. The laptop scripts match the VM repo by md5 exactly
   (cursor_session.py 5d6c580a, cursor_theme.py 502a4941).
3. The live negative test capture on the laptop (/tmp/f1-test/neg.out) matches
   the log word for word. The envelope at 22:39 names the cause:
   session guardian startup failed, cursor guard reply is not valid JSON
   (got: unknown request), the cursor backend may not be loaded, load it
   with scripts/activate-glass.py and scripts/activate-cursor-guard.py or
   re-run the fresh-login loader scripts/visuals.py. neg.err is empty.
4. tests/test_cursor_session.py does not compile on the VM Python 3.12:
   SyntaxError, too many statically nested blocks, line 570. I compiled the
   pre-fix version from git (5033c9d parent) and it fails the same way at
   line 566, so the break is pre-existing and the diff did not cause it.
   The new Lifecycle test therefore has never run on the VM, only on the
   laptop.
5. No em dash and no en dash in the diff or in any of the four changed
   files. Checked by character count, all zero.
6. The FAKE hyprctl status_garbage branch (tests/test_cursor_session.py:53)
   prints unknown request and exits 0, which matches the live Hyprland
   behavior recorded in the log. The fake is faithful for this failure.

## What the fix gets right

1. guard_reply (scripts/cursor_theme.py:97) now fails closed with a named
   cause instead of a bare JSONDecodeError. The bytes and bytearray socket
   path is handled, and the first version bug that broke the garbage socket
   test was caught by the suite and fixed. Good.
2. The new Lifecycle test (tests/test_cursor_session.py:777) proves the
   session fails closed: return code is not 0, the driver marker file is
   never created, no session.json is written, nothing is released. That is
   the important half of the fix, and it is proven.
3. The tee in supervise (scripts/cursor_session.py:237-246) preserves the
   success path behavior. The pre-existing
   test_hotkey_failure_warns_but_driver_runs guards it, and the first supervise version broke that test
   and the tee fixed it. That regression was caught and repaired before
   review, which is how the loop should work.
4. The live negative test at 22:39 proves the envelope names the cause on
   the real machine, not only under the fake. Before the fix the same
   command gave only the opaque session guardian startup failed.

## Findings, numbered

1. The Lifecycle test does not prove the envelope names the cause.
   tests/test_cursor_session.py:777 asserts on combined out plus err only.
   The envelope is printed to stdout (scripts/cu.py:2618), while the tee
   writes the guardian one line message to stderr
   (scripts/cursor_session.py:242). The guardian prints its own message to
   its stderr first (scripts/cursor_session.py:304), so the tee alone puts
   not valid JSON on stderr even if supervise raised the bare message. The
   test would pass with fix D, the tail in the envelope, deleted. Only the
   single live run at 22:39 proves fix D, and a single live run is not a
   regression test. Required: parse stdout as JSON in the new test and
   assert the error field contains not valid JSON and may not be loaded.
   A second assertion that the bare message never appears alone would also
   close this hole.
2. The remedy in the error message is partly wrong and partly unrunnable.
   scripts/cursor_theme.py:108-112 tells the operator to load it with
   scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run
   the fresh-login loader scripts/visuals.py. Three defects. First,
   activate-glass.py requires a library path plus --abi plus
   --profile-sha256 (scripts/activate-glass.py:71-73) and
   activate-cursor-guard.py requires a library path plus --abi
   (scripts/activate-cursor-guard.py:57-58), so the bare script names
   cannot be run as written. Second, visuals.py refuses outside the first
   30 seconds of a fresh login (scripts/visuals.py:166), and the log
   itself proves a mid-session re-run fails at fresh_login_gate, so
   re-run scripts/visuals.py cannot fix a running session. It can only
   help at the next login, and the message does not say that. Third,
   activate-cursor-guard.py refuses unless the glass backend is already
   available (scripts/activate-cursor-guard.py:40), so the order matters
   and the message does not state it. Required: rewrite the remedy to
   name runnable commands with their required arguments and the pinned
   values, or point at the log plan B commands, and say plainly that the
   loader only runs at next login. An error message that misleads the
   operator is worse than a short one.
3. The supervise tail has a race. scripts/cursor_session.py:249 reads the
   deque immediately after stdout signals failure, with no wait for the
   drain thread and no wait for the guardian to exit. If the guardian dies
   fast, the deque can still be empty and the envelope falls back to the
   bare message, silently losing fix D. The live run at 22:39 won the
   race, but nothing guarantees it. Required: on the startup failure path,
   wait for the guardian to exit and join the drain thread with a short
   bounded timeout before composing the error. Then the tail is complete
   or the timeout is explicit.
4. The second live failure layer has no test. The log proves
   Guard.__init__ would throw FileNotFoundError on the missing socket
   directory even if check_guard passed. The FAKE always provides a guard
   socket, so no test covers a loaded status reply with a missing socket,
   or a status reply that is valid JSON but not idle. Required: add one
   Lifecycle case for the missing socket directory, asserting fail closed
   with the cause named in the envelope, or record explicitly in the log
   that this layer is unproven and why the live positive test covers it.
5. The Python 3.12 failure is pre-existing but it now gates the new test.
   The repo own test file cannot run on the VM, which is the machine the
   fix was developed on, and the laptop-only green run is the only
   evidence for the new Lifecycle test. I re-verified the laptop claim
   myself, so the claim is true, but a single green run on a second
   machine is not a sufficient standing gate. Required: fix the nesting
   in test_cleanup_exceptions_cannot_skip_restore
   (tests/test_cursor_session.py:566) so the file compiles on Python 3.12,
   or split the new Lifecycle test into a file that compiles on 3.12, or
   record a pinned minimum Python version for the test suite and say which
   machine runs it. Do not leave the new test unrunnable where the code
   is written.
6. The 34 OK claim is luck dependent because the suite has a pre-existing
   flake. test_wrong_token_oversize_framing_and_drop_all_fail_closed
   (tests/test_cursor_theme.py:409) fails intermittently with
   BrokenPipeError at scripts/cursor_theme.py:148, in the drop case at
   line 429. The test accepts RuntimeError and ConnectionResetError but
   not BrokenPipeError. I measured it: pre-fix code fails 5 of 50 runs,
   post-fix code fails 0 of 50 in one batch and about 5 of 95 overall, so
   the fix did not cause it and the rate is the same before and after.
   It is a pre-existing race in the test server closing the socket, not a
   regression. Required: accept BrokenPipeError in the drop case, or make
   the server close cleanly, and then re-run the suite until it is green
   ten times in a row before quoting a pass count.
7. Duplication is small but real. On the failure path the same message
   appears twice by design: once on stderr through the tee and once inside
   the JSON envelope on stdout. The log says neg.err was empty in the live
   run, which does not match the tee design, so either the live harness
   did not capture session stderr or the tee line went elsewhere. This
   is not a blocker, but the live positive run should record both streams
   separately and confirm where the message appears, so the log claim and
   the code agree.
8. The message leads with decoder jargon. cursor guard reply is not valid
   JSON (got: unknown request) means little to the owner. The actionable
   half, the cursor backend may not be loaded, comes second. Minor, but
   since finding 2 rewrites the message anyway, lead with the cause and
   keep the raw reply as the parenthetical detail.

## What is still unproven

1. The live positive proof has not been done. The session has never been
   shown to start with the pill visible since the failure. The fix only
   makes the failure diagnosable. It does not restore the session. Plan B,
   the live activation, is still gated.
2. No test proves the pill appears, no test proves the session token is
   held by the indicator, and no test proves clean stop removes the pill.
   Those are live properties, not unit properties, and they need the live
   positive test below.

## Exact proof that would close the positive gap

Run after plan B activation, on the live slot, with F3 Zen work finished,
and record every step with wall clock time:

1. Plugin list shows hyprglass plus computer-use-cursor plus hyprbars.
   hyprctl cu-cursor status returns JSON with active true and the session
   token. The socket directory exists.
2. Start computer-use session with a harmless driver. Take a fresh
   observe. The pill must be visible in that observe, taken during the
   session, with a fresh observe id, not a reused one.
3. Prove the pill is the session pill and not a leftover overlay. Check
   that the indicator process is the one the session spawned, by pid and
   by the state directory token matching the session. Then stop the
   session cleanly, take a fresh observe, and confirm the pill is gone
   and no stray indicator process remains. Then start the session a
   second time and confirm the pill returns. A pill that survives a clean
   stop is a leftover, not proof.
4. One harmless click through the session on an already selected tab row,
   re-checked in a fresh observe first. Verify by cursorpos and a fresh
   observe that the click landed, then clean stop and a desktop clean
   check.
5. Record stdout and stderr separately for the whole run, so finding 7
   about duplication can be settled from evidence.

## Scope note

Findings 5 and 6 are pre-existing defects, not regressions from this fix.
I list them as required because the new test lives in the broken file and
because the pass count quoted for this fix rests on a flaky suite. The
fix itself introduces no regression I could find: the diff touches only
guard_reply, supervise, and the two new tests, and the full laptop suite
passes when the flake does not fire.

## Bottom line

The diagnosis is proven, the fail closed behavior is proven, the live
negative envelope is proven, and I re-verified the laptop suite myself.
But the test that should guard the envelope does not guard it, the remedy
in the message cannot be run as written and offers a loader step that
cannot work mid-session, and the tail read can lose the race. Fix findings
1, 2 and 3, then findings 4, 5 and 6, then run the live positive proof
above. Do not claim the session is fixed until that proof exists.

# Worker W-S1CLOSE log: step-1 close-out, remaining parts

Owner: Pham Tuan. Worker: W-S1CLOSE, for COORD-CLICK-6.
Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
Start: 2026-11-22 17:49 +07 (Asia/Ho_Chi_Minh). All times below are
wall-clock +07 unless noted. No em dash (U+2014) or en dash (U+2013)
anywhere in this file, no personal info, never ydotool, full access,
explicit pathspec commits only, every push verified with git ls-remote.

Task (queue item 14, resume 17:47): the remaining part of the step-1
close-out. AMEND4 is 12/12 landed. Remaining: (a) full discover at
HEAD 36364b1, started by COORD-CLICK-3 in session proc_9106d33f042e,
re-run if lost; (b) live-browser confirmations: F1 sanitization rule,
item 8 fixed template, items 5-6 live hyprctl re-read; (c) Codex-lane
item-12 confirmation V-Z2.

Status at start: HEAD 05140c1 on todolist-push. `git fetch origin`
first failed to update origin/main (cannot lock ref, local ref at
d49dbe2 but expected 90860ee); fixed with a forced ref update
`git fetch origin '+refs/heads/main:refs/remotes/origin/main'`,
then `git pull --ff-only` returned "Already up to date" at
05140c1. During this task the coordinator committed ab7c7a5 (COORD-
CLICK-6 resume log) and local HEAD moved to ab7c7a5; this log is
committed on top of that HEAD (see section 8).

Prior close-out record read first:
improvements/worker-click4-step1-closeout-log.md (commit 4ac9320,
C4-STEP1-CLOSEOUT): item-12 tests 4/4 PASS, Codex-lane item 12
LANDED via resume, discover at 36364b1 Ran 1974 in 248.397s with
0 failures, 4 errors, 17 skipped, Y1b 8 issues gone, CB-9 manifest
NOT locked. This worker independently re-verifies each claim below
instead of trusting that log; the C4 log is a cross-check, not the
evidence.

## 1. Full discover at HEAD 36364b1 (task a): PENDING, see section 1b

The COORD-CLICK-3 session proc_9106d33f042e is not accessible from
this worker, and no discover log survives in /tmp (the VM restarted
about 07:51 +07 on 22/11 and wiped /tmp; /tmp/click4-discover.log
from the C4 run is gone too). Per the task ("neu mat thi chay lai"),
the discover is re-run from scratch, first-hand, in a clean
worktree. The committed C4 record (4ac9320) stands as the prior
run; this re-run is the independent confirmation.

### 1a. Worktree setup

- `git worktree add ~/workspace/w-s1close-discover 36364b1`
  (detached HEAD, verified 36364b16c9223b15a415e037fd117593424d064f).
- Untracked native artifacts copied in from the main checkout
  first, per the C4/reconcile worktree lesson (a fresh worktree
  lacks them and the numbers would be environmental, not HEAD
  evidence): native/pointer, native/wtype,
  native/keyboard-protocol.c/.h, native/pointer-protocol.c/.h.
  Worktree status clean before the run. Main checkout untouched
  by this run.
- Command (from tests/ in the worktree, same command as the C4
  and reconcile runs):

```
PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"
```

- Launched detached 17:51:18 +07 (setsid nohup, log
  ~/workspace/w-s1close-discover.log, PIDs 7099/7101/7102).
  Note: the launch exec returned an output-drain notice
  (proc_4c39eb2409be); the discover itself runs detached as
  intended and was left running, not killed.

### 1b. Discover result: Ran 1974 in 190.088s, 0 failures

Finished about 17:54:20 +07 (log mtime 10:54:20 UTC; launched
17:51:18 +07, wall about 3 min). Log:
~/workspace/w-s1close-discover.log. Output tail (verbatim):

```
Ran 1974 tests in 190.088s
FAILED (errors=4, skipped=17)
```

Failures: 0 (`grep -c '^FAIL:'` returns 0). Errors: 4, all
identical to the C4 baseline at the same HEAD:

```
ERROR: test_a11y_skeleton (unittest.loader._FailedTest.test_a11y_skeleton)
ERROR: setUpClass (test_cursor_file.CursorFileTests)
ERROR: test_valid_normal (test_perf_evidence.EvidenceChecks.test_valid_normal)
ERROR: test_valid_optimized (test_perf_evidence.EvidenceChecks.test_valid_optimized)
```

Skipped: 17, same as C4. Comparison with the C4 run at the same
HEAD (Ran 1974 in 248.397s, 0 failures, 4 errors, 17 skipped):
same test count, same errors, same skipped, same zero failures.
Wall time 190.088s vs 248.397s is VM contention, not a code
change (no other discover was running concurrently this time;
the C4 run overlapped another worker's discover).

Check note: the first post-run aliveness check printed
STILL-RUNNING because pgrep matched the checking command's own
command line (it contains the pattern text). A follow-up check
found no discover process alive (`ps -p 12301` empty, `pgrep -f
'python3 -m unittest discover'` returns nothing). The run is
finished; the STILL-RUNNING line was a false positive of the
check, not of the run.

Y1b 8-issue re-check (same worktree, from tests/, 17:55:30 +07):

```
PYTHONPATH=../scripts:. python3 -m unittest test_code_exec test_codemode
Ran 81 tests in 12.756s
OK
```

The Y1b 8 issues are GONE at 36364b1, confirmed first-hand.
(Honesty note: my first attempt ran from the worktree root
instead of tests/ and failed with Ran 2 tests, errors=2; that
run is invalid, wrong working directory, and the rerun from
tests/ above is the evidence.)

## 2. Item-12 regression tests, re-run at 36364b1 (supports task c)

Worktree ~/workspace/w-s1close-discover, HEAD 36364b1.
Run: 2026-11-22 17:51:37 +07.

```
python3 -m unittest tests.test_first_action.TestRun.test_session_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_fallback_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_after_without_result_after_captures_fresh_window tests.test_first_action.TestRun.test_screen_observation_key_batch_refused_before_overlay -v
```

Output (verbatim tail):

```
test_session_after_is_scope_matching_not_screen ... ok
test_fallback_after_is_scope_matching_not_screen ... ok
test_after_without_result_after_captures_fresh_window ... ok
test_screen_observation_key_batch_refused_before_overlay ... ok
Ran 4 tests in 0.007s
OK
```

Result: PASS 4/4, first-hand. Matches the C4 record (4/4 in
0.008s). This closes the open test-pass evidence from the final
direction (V-Z1) a second time, independently.

## 3. Codex-lane item-12 confirmation V-Z2 (task c): LANDED, confirmed

Three independent checks, all first-hand this session:

1. Remote HEAD (VM, 17:51 +07):
   `git ls-remote origin amend4-codex` returns
   06a34e8610a9467c3884f6dd7a567293c747da45, matching the resume
   log (commit 2de4c31) and the C4 record.
2. Laptop worktree /home/james/workspace/cu-amend4-codex, clean
   status, HEAD 06a34e8610a9467c3884f6dd7a567293c747da45 (checked
   via ssh-laptop.sh, 17:51 +07). Same hash as the remote.
3. Codex-lane tests, run on the laptop worktree, 17:52:06 +07:
   `python3 -m unittest tests.test_first_action` gives
   "Ran 67 tests in 0.549s, OK", matching the resume log count
   (64 + 3 item-12). The 3 item-12 tests by name, verbose run:
   test_after_preserves_input_scope_and_labels_screen_capture
   ... ok; test_screen_scoped_key_refuses_before_overlay ... ok;
   test_fallback_returns_desktop_act_after_as_chainable ... ok
   (all in class TestRun, lines 409, 428, 443 of
   tests/test_first_action.py on that lane).

Conclusion: Codex-lane item 12 is LANDED. V-Z2 is closed, not
open. No re-commission needed. The VM-vs-Codex shape difference
(VM captures a fresh window when no scope-matching after exists;
Codex leaves after None; Codex pre-overlay refusal stricter)
stays as recorded in the reconcile log (e1a4e77, verdict KEEP
VM); judging it belongs to the round-3 council, not this worker.
No Codex run was launched.

## 4. F1 sanitization rule, live confirmation (task b, part 1)

Prior record: improvements/fcc-f1-live-confirm.md (commit
f4dcfa3, Chromium 130 headless, 2026-11-22 06:01:51 to 06:15:00
+07, 789s, verdict CONFIRMED). Re-confirmed live on the laptop
Chromium, same method, this session.

Probe: /tmp/w-s1close-probe.html on the laptop (written via
ssh-laptop.sh stdin, 719 bytes), run with
`chromium --headless --disable-gpu --dump-dom
file:///tmp/w-s1close-probe.html`. Chromium 157.0.8103.38 Arch
Linux. Run 2026-11-22 17:52:35 +07. Headless Chromium only; no
Zen tab opened, switched, or touched.

Result JSON (verbatim):

```
{"f1_input_lf":"ab","f1_input_cr":"ab","f1_textarea_crlf":"a\nb","i8_url_spaces":"https://example.com","i8_email_tabs":"a@b.com","i8_url_maxlength5":"abc","i8_text_control":"  hello  "}
```

F1 rows (input sanitization):
- "a\nb" set on text input reads back "ab" (LF stripped).
- "a\rb" set on text input reads back "ab" (CR stripped).
- "a\r\nb" set on textarea reads back "a\nb" (CRLF normalized
  to LF).

Verdict: F1 rule holds live on the laptop Chromium 157, same as
on Chromium 130 in the prior confirmation. CONFIRMED a second
time, independently.

## 5. Item 8 fixed template, live confirmation (task b, part 2)

The "fixed template" is the set_value template in
scripts/cdp.mjs after the ITEM8-MICROGAP fix.

Template presence at HEAD (this session): scripts/cdp.mjs lines
496-497 carry the trim loop over char codes 9 (TAB), 12 (FF),
32 (SPACE) at both ends, placed after the CR/LF strip and before
the maxLength pre-check and the read-back. The fix landed on
todolist-push as d91f1bb (parent of 36364b1); `git diff 7177cdc
d91f1bb -- scripts/cdp.mjs tests/cdp_snapshot.mjs` is EMPTY, so
the todolist-push landing is content-identical to the
item8-microgap branch fix 7177cdc. The fix IS in 36364b1 and in
current HEAD ab7c7a5 (7177cdc itself is not an ancestor, only its
content via d91f1bb).

Live behavior (same probe run as section 4, Chromium 157,
17:52:35 +07):
- url "  https://example.com  " reads back
  "https://example.com" (leading/trailing spaces trimmed).
- email "\ta@b.com\t" reads back "a@b.com" (tabs trimmed).
- url maxlength=5, "  abc  " (7 raw chars) reads back "abc"
  (trimmed length 3 fits, lands as "abc"). This is the maxLength
  interplay the fix is built around: the pre-check must measure
  the TRIMMED length, exactly where the template puts it.
- text control "  hello  " reads back "  hello  " (NOT trimmed,
  as the spec requires for plain text inputs).

Verdict: the item-8 fixed template matches live browser behavior
on all four probes. The template code is present at HEAD, and the
behavior it models is confirmed live. CONFIRMED.

Harness check, worktree at 36364b1, 17:55:47 +07 (after the
discover, from the worktree root):

```
node tests/cdp_snapshot.mjs
all cdp snapshot, redaction, fill, payload, no_after and scope regressions pass
node-exit: 0
python3 -m unittest tests.test_cdp_snapshot
Ran 2 tests in 3.202s
OK
```

The template harness passes at 36364b1, first-hand. (Honesty
note: my first node attempt ran from tests/ with the path
tests/cdp_snapshot.mjs and failed MODULE_NOT_FOUND; that run is
invalid, wrong working directory, and the rerun from the root
above is the evidence.)

## 6. Items 5-6 live hyprctl re-read (task b, part 3)

Items 5-6 (commit b44a5ea) added `ZenSession.live_window_origin`
(scripts/zen_dom.py) plus the `_live_window_origin` /
`_check_window_not_moved` wiring in scripts/dom_act.py: ground
calls refuse when the live origin mismatches the meta origin, and
skip the check when the live origin is None (hyprctl missing).
The F2/F3 proof tests were judged DEFECTIVE because the true
origin was not derivable from the meta alone; only a live
hyprctl re-read could supply it, and none existed on the VM.
This section supplies that live re-read, on the laptop, through
the real code path.

Read-only SSH checks only (ssh-laptop.sh, short commands, no
window focus change, no tab open/switch; Pham Tuan is using the
machine). HYPRLAND_INSTANCE_SIGNATURE set from
`ls /run/user/1000/hypr/ | head -n1` per the workspace lesson
(SIG=11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614).

Step 1, raw hyprctl (17:51 +07):
`hyprctl clients -j` returns 4 clients, including:
- Zen: address 0x56307e2771d0, "Chat - Muse - Zen Browser",
  at [2509, 914], size [1863, 1176], workspace 1.
- Brave-origin: at [2533, 914], size [901, 1176], workspace 2.
- Chromium (mochi): at [3448, 914], size [901, 1176],
  workspace 2.

Step 2, real code path (17:52 +07): in the laptop repo
/home/james/workspace/computer-use-wayland (HEAD 48c6aee,
`live_window_origin` present at scripts/zen_dom.py line 734),
ran the unbound method on a bare ZenSession instance (the
method uses only subprocess/json, no browser state):

```
python3 -c "import sys; sys.path.insert(0, 'scripts'); from zen_dom import ZenSession; s = object.__new__(ZenSession); print('zen-by-address:', s.live_window_origin('0x56307e2771d0')); print('active-window:', s.live_window_origin())"
```

Output (verbatim):

```
zen-by-address: [2509, 914]
active-window: [2509, 914]
```

Both match the raw hyprctl read exactly ([2509, 914]). The
active window at that moment is Zen, consistent with Pham Tuan
using Zen.

Verdict: the items 5-6 live re-read works end to end on the
laptop through the shipped code: hyprctl supplies a real origin,
and `live_window_origin` returns it unchanged for both the
by-address and the active-window forms. The missing live leg the
F2/F3 adjudication needed now exists. CONFIRMED (the re-read
mechanism; the F2/F3 tests themselves stay judged DEFECTIVE, as
recorded in the AMEND4 log, since no return value can satisfy
their contradictory assertions).

## 7. What is NOT done here (open, for the coordinator)

- CB-9 manifest for the bench build a1a672d: still NOT locked,
  per the C4 record (section 5 of the C4 log). Not re-verified
  here; it belongs to step 3, not step 1.
- Round-3 council judgment on the 5 defective proof tests
  (items 3, 4, 5-6) and the VM-vs-Codex item-12 shape difference:
  adjudication, not this worker's task.
- Nothing else from this task is open: discover re-run (section
  1b), item-12 tests (section 2), V-Z2 (section 3), F1 live
  (section 4), item-8 template live plus harness (section 5),
  items 5-6 live hyprctl re-read (section 6) are all done above
  with first-hand evidence.

## 8. Commit record

- Log file: improvements/w-step1-closeout-log.md (this file).
- Commit: 3e64547
  ("docs: W-S1CLOSE step-1 closeout, discover 1974 0 fails, V-Z2
  landed, F1/item8/items5-6 live confirmed"), 1 file, 331
  insertions, on top of ae2fe52.
- Push verification: 2026-11-22 about 17:57 +07, `git ls-remote
  origin todolist-push` returns
  3e64547b5cb041277ea5f9aac8148436a54c67d7, matching local HEAD.
- Commit-record follow-up: this section filled in by a second
  commit (see final report for its hash and ls-remote
  verification).
- Worktree ~/workspace/w-s1close-discover removed after the run
  (`git worktree remove --force`, verified gone from `git
  worktree list`). Discover raw log kept at
  ~/workspace/w-s1close-discover.log (not committed).

Elapsed: task received 17:49 +07; pull done 17:49 +07; item-12
tests 17:51:37 +07; discover launched 17:51:18 +07; hyprctl read
17:51 +07; Codex tests 17:52:06 +07; live probe 17:52:35 +07.

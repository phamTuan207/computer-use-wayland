# Worker CLICK-C3 review log (council member 3 of 3, independent review)

Branch: todolist-push. Review target: fix diff e4082ff (8 files, +824/-38).
Task: review independently, do not coordinate with the other reviewers,
form my own verdict. I did not read any other council member's review log.
Read-only on the fix code (no code changes made). No laptop driving.
No ydotool used. No em/en dashes in this log.
All times wall-clock Asia/Ho_Chi_Minh, elapsed from task start 01:38:47.

## 2026-11-22 01:38:47 +07 (t+0s)
Start. Located the repo: ~/workspace/computer-use-wayland, branch
todolist-push, HEAD e4082ff at start (branch later moved to ab0b62c by
another worker's Y13g log commit while I worked; e4082ff remains the
review target and an ancestor). The other worktree
~/computer-use-wayland-instrfix is on instrfix, not used.

## 2026-11-22 01:39 +07 (t+1m)
Read improvements/worker-click-fix-log.md (e4082ff) in full: G28 loud
refusal, type verification, zen_dom TimeoutError handling, ime_state_trace
surfacing, plus the plain-text-field discriminator procedure handed to the
parent (not run live by the fix worker, per the subagent browser rule;
no live browser claim made anywhere in the log, correct).
Read improvements/worker-click-src-log.md (050272d) in full: conversion
proof (image_point cu.py:995 uses region origin, move cu.py:1602
normalizes by monitor_box, probe P1 0px P2 1px), G28 trigger is staleness
only (age + 20s deadline over 120s), verification asymmetry (pointer
verified twice vs cursorpos, type never verified).

## 2026-11-22 01:40 +07 (t+2m)
Read improvements/worker-click-probe-log.md (fa289eb) in full: Stage A
single 'X' never appeared in the Brave/Muse chat input despite 6/6 clean
execution, cursorpos-exact clicks, Brave active in every diagnostics
event. Refuted: coordinates, focus-click consumption as sole cause,
Enter/send, settle timing (2000ms), multi-char length. Remaining fault at
the focus/app layer. ime_state_trace ABSENT from act-now envelopes,
first-action JSONL, and diagnostics.
Read improvements/worker-click-sweep-log.md (affaf54) in full: ranked
list, G28 rank 5 (code defect proven, procedure containment exists),
zen_dom TimeoutError sub-finding under rank 4 (F3b Arm A run 2 at 30s,
Arm D run 1 at 10s, raw TimeoutError escapes _wd).

## 2026-11-22 01:41 +07 (t+3m)
Read the full diff e4082ff (1097 lines, via git show, plus targeted
reads of the current files). Findings per fix:

### Fix 1: G28 loud refusal (scripts/first_action.py)
- _read_given_observation returns (meta, None) or (None, rejection)
  with given_id, age_s, reason (unreadable / incomplete / stale).
  Staleness check is age + deadline >= 120, matching the SRC spec
  (age under 100s with the 20s deadline). No focus, geometry, or
  screen check added, matching the SRC "staleness only" finding.
- _fresh_observation returns the 4-tuple (meta, path, source, rejected)
  and still captures a screen observation when the given one is
  rejected, so the envelope can name the substitute. The capture
  itself is not the defect; acting on it silently is.
- run() refuses loudly for key/type batches before any session
  attempt: envelope error/fallback_reason carry
  loud_substitution_refusal(rejected), path 'refused', return 1.
  Verified the return goes through the finally block (lines 603-620):
  the envelope is still appended to the JSONL log and printed as the
  single stdout JSON object, and the overlay is released. The refusal
  is therefore actually emitted and recorded, not swallowed.
  Test test_stale_given_observation_refused_loudly_typing_batch asserts
  exactly this, including the JSONL record and that attempt_session was
  never called and desktop_act never ran.
- The refusal happens after overlay acquisition, so the pill flashes
  briefly on a refusal. Consistent with other post-overlay refusals;
  not a defect.
- Pointer-only batches proceed with given_observation_rejected recorded
  in envelope['observation']. This is the flagged residual, judged
  below. It is the one point where I differ from the fix as written.

### Fix 2: type verification (scripts/cu.py)
- has_type detects type actions in both group shapes (bare dict groups
  and keyboard list groups), matching keyboard_groups (cu.py:1111-1126),
  where type/key actions are grouped into lists and other actions stay
  bare dicts. Key-only batches are not verified, correct: a shortcut
  may legitimately change nothing visible.
- After a successful after-capture, an unchanged frame fails the batch
  with error_code type_unverified instead of reporting ok on wtype
  exit alone. The check reads the pre-existing frame_bytes_changed
  (after pixel_sha256 vs meta pixel_sha256, cu.py:1847), so no new
  capture machinery. The comment states the limit plainly: a changed
  frame is necessary, not sufficient (animations also change it).
- after_capture=False records type_verified None with an explicit skip
  reason instead of letting ok rest on process exit. Correct.
- One edge noted, not blocking: when the after-capture is skipped for
  lack of a terminal window (window scope, terminal_address None),
  type_verified is absent entirely and ok can stay True. That path
  should already have been refused at preflight for a type batch; the
  marker gap is minor and pre-existing in shape.
- Live behavior is still unproven (no live re-run of Stage A on the
  laptop in this review, and the fix worker ran none either): the
  prediction that a Stage A re-run now reports ok False with
  type_unverified rests on the harness, not on a live frame. Noted as
  follow-up, not a blocker, because the fail direction is the safe one
  (a false failure is loud; the old false success was silent).

### Fix 3: zen_dom TimeoutError handling (scripts/zen_dom.py)
- _wd converts TimeoutError, OSError, and URLError to ZenDomError;
  HTTPError keeps its own branch first (it is a URLError subclass and
  carries the status). The comment explains the urllib wrapping
  (socket timeout inside URLError.reason). Correct and matches the F3b
  finding (raw TimeoutError escaped ZenDomError-only handling).
- tab_at / list_tabs(handle_index=) target by known handle index with
  one switch, one title read, one URL read, then restore the original
  tab in a finally. Out-of-range index raises ZenDomError. Correct.
- Full scan records a hung handle as an error entry and keeps going,
  and always attempts the restore in a finally. If current_handle()
  itself raises before the loop, nothing was switched yet, so there is
  nothing to restore. Correct.
- The per-handle except catches (ZenDomError, TimeoutError, OSError);
  _wd already converts the latter two, so the extra catches are
  belt-and-braces only. Harmless.
- `tab` CLI subcommand added; usage text updated. No other Python
  callers of list_tabs exist in scripts/ (fix log checked), so the
  signature change (optional handle_index) has no ripple.

### Fix 4: ime_state_trace surfaced (scripts/first_action.py)
- run() copies session_result['ime_state_trace'] into the envelope on
  the session path and result['ime_state_trace'] on the fallback path,
  only when it is a list, on success and failure alike. This matches
  the probe finding exactly: desktop_act already records the trace
  (cu.py literal_keyboard, result.update(ime_result)), but act-now
  parsed only ok/error out of the session stdout and discarded the
  rest. Three tests cover session-surfaced, session-absent reports
  None, and fallback-surfaced. Correct.

## 2026-11-22 01:41 +07 (t+3m)
Hygiene and scope checks on the diff (git show e4082ff):
- Em dash U+2014: 0 occurrences. En dash U+2013: 0 occurrences.
- "ydotool": 1 occurrence, and it is the sentence "No ydotool used"
  in the fix log, not usage. No ydotool anywhere in code or tests.
- No PII in the diff: only hex observation ids (e.g. 8fef498445d2),
  no names, emails, addresses, or phone numbers.
- Coordinate conversion untouched: image_point and move() appear in
  the cu.py diff only as unchanged context lines. No change to
  region/monitor origin handling.
- Y13g untouched: the 8 files are the fix log, cu.py, first_action.py,
  zen_dom.py, and 4 test files. _check_entry_pyc is not in the diff.
- Commit message matches the code: G28 refusal, type verification,
  zen_dom TimeoutError, ime trace in envelope.

## 2026-11-22 01:42 +07 (t+4m)
Ran the 10 named suites on the fix branch from tests/ with
PYTHONPATH=.:.. (running from the repo root misses the
test_pointer_safety import used by test_guard_boundaries):
python3 -m unittest test_first_action test_type_verification test_zen_dom
test_keyboard_preflight test_fast_observe test_act_diagnostics
test_guard_boundaries test_pointer_safety test_focus
test_observation_contract
Result: Ran 241 tests in 2.866s, OK. The 241 claim in the task brief
holds exactly.

## 2026-11-22 01:42 +07 (t+4m)
Fail-before spot check. Built a detached worktree /tmp/c3-base at
fa289eb (the fix parent), copied the 4 new/changed test files from the
fix branch into it, ran them against old code. First run gave inflated
errors (46 in test_type_verification, 21 in test_keyboard_preflight):
root cause was my worktree, not the fix: native/wtype is a gitignored
build artifact present in the fix worktree but absent in a fresh
worktree, and old desktop_act raised "private wtype helper is missing".
Copied native/wtype into /tmp/c3-base/native/ and re-ran. Results on
old code fa289eb:
- test_first_action: FAILED (failures=2, errors=12). Matches the fix
  log claim exactly (2 failures + 12 errors).
- test_type_verification: FAILED (failures=2, errors=2). Matches the
  fix log claim exactly.
- test_zen_dom: FAILED (errors=8). Matches the fix log claim exactly.
- test_keyboard_preflight: OK on old code. Expected: the fixture change
  (after-frame hash differs by default) is behavior-neutral for old
  code, which has no type verification.
Fail-before claims all hold. The /tmp/c3-base worktree was left in
place for reference; it is not committed anywhere.

## 2026-11-22 01:43 +07 (t+5m)
Regression sweep beyond the 10 suites: ran test_core, test_code_exec,
test_det_finish, test_a1_preflight on the fix branch: 116 tests, 2
failures, both the same test:
test_core.SecureObservationFiles.test_private_mode_under_any_umask_in_isolated_child
(umask 0 and 0o777). Re-ran that single test on /tmp/c3-base (old code
fa289eb): FAILED (failures=2) identically. Cause on both branches is
environmental: the isolated child raises ModuleNotFoundError: No module
named 'cu' (the child does not inherit the scripts path). Pre-existing,
unrelated to e4082ff, which touches nothing in observation-file
permissions. Not a regression from this fix.

## 2026-11-22 01:43 +07 (t+5m)
Judgment on the flagged residual: a pointer-only batch on a substituted
screen observation can still land off by the window offset, and
cursorpos cannot catch it.
- Mechanism, confirmed from the source I read: the batch's coordinates
  were written for the rejected observation's image. Against the
  substitute screen region they map off by exactly the window offset
  inside the monitor ((-69,-12) in the Brave case from the SRC log:
  window [2533,914,901,1176] vs screen region [2464,902,1920,1200]).
  cursorpos verifies the pointer reached the intended global point;
  the error is in the intended point itself, so both cursorpos checks
  pass while the click lands on the wrong UI element.
- The envelope record (given_observation_rejected) is visible only to
  an agent that reads the observation subfield. The standard agent
  loop checks ok/completed, which stay True. The record mitigates;
  it does not prevent the mis-click.
- This is the same silent-misdirection class the fix exists to kill
  (sweep rank 1: silent success is worse than a loud failure; rank 5:
  the ZT-B 00:44:51 fallback click into the wrong workspace's chat
  input, harmless only by luck).
- There is no legitimate case for proceeding: every batch affected by
  widening passed an observation that was rejected, so its coordinates
  are wrong for the substitute by construction. A pointer-only batch
  genuinely written for the screen would not have passed a window
  observation at all, and the no-observation default (rejected None)
  is untouched by widening.
- The fix's own module docstring already claims the widened behavior:
  "a given observation that is stale, missing, or unreadable is NEVER
  silently replaced by a screen capture that the batch then acts on
  (G28)". As written, pointer-only batches DO act on the substitute,
  so the docstring and the code disagree on the headline claim.
- Cost of widening: one line (drop the has_keyboard gate in run(),
  first_action.py:480-489) plus rewriting one test
  (test_stale_given_observation_pointer_only_proceeds_recorded,
  tests/test_first_action.py:620-638, which currently locks in
  proceeding with code 0 / ok True / path session) to assert refusal.
  No new machinery. The only behavior change is forcing re-observe,
  which is already the documented procedure.
- The SRC spec scoped the refusal to key/type batches, and the fix
  follows that spec exactly. I am overruling the spec on this one
  point because the spec's own residual analysis proves the hole is
  real (the SRC log names the exact (-69,-12) miss), and the fix's
  purpose is to convert silent misdirection into loud refusal, not
  to document half of it.
- Verdict on the residual: the one-line widening IS required now. The
  documented residual is NOT acceptable as the shipped behavior.

## VERDICT: AMEND (one required fix)

Required fix:
1. Widen the G28 loud refusal to ALL batches. In scripts/first_action.py
   run(), remove the has_keyboard gate around the refusal
   (lines 480-489): whenever rejected is not None, refuse loudly with
   loud_substitution_refusal(rejected), path 'refused', return 1,
   before any session attempt, regardless of action types. Rewrite
   tests/test_first_action.py
   test_stale_given_observation_pointer_only_proceeds_recorded
   (lines 620-638) to assert the refusal (code 1, path 'refused',
   attempt_session not called, given id and age named in the error,
   JSONL record written), mirroring
   test_stale_given_observation_refused_loudly_typing_batch. After
   this change the module docstring claim ("NEVER silently replaced")
   becomes true as written, so no docstring change is needed. Re-run
   the 241-test set and confirm still green.

Notes (not required fixes, for the record):
- Type verification is necessary, not sufficient: any frame change
  (animation, caret blink) marks a type batch verified. The code
  comment says so plainly. Acceptable.
- Live proof of the type verification is still owed: no live Stage A
  re-run has shown ok False with type_unverified on the laptop. The
  fail direction is the safe one, so this does not block the fix.
- type_verified is absent (not None) on the no-terminal-window
  after-skip path. Minor marker gap, pre-existing path shape.
- The discriminator procedure in the fix log is correctly handed to
  the parent for a live-capable agent; no live browser claim is made.

Evidence summary:
- 241 tests pass on e4082ff (2.866s, OK), fail-before confirmed
  exactly on fa289eb (first_action 2 failures + 12 errors,
  type_verification 2 failures + 2 errors, zen_dom 8 errors).
- Adjacent suites: 116 tests, 2 failures, both pre-existing and
  environmental (isolated child ModuleNotFoundError for 'cu', fails
  identically on fa289eb).
- Diff hygiene: 0 em/en dashes, ydotool only in "No ydotool used",
  no PII, coordinate conversion untouched, Y13g untouched.
- Residual: pointer-only batches still act on the substituted screen
  capture (first_action.py:480-489, test at
  tests/test_first_action.py:620-638); off by the window offset,
  invisible to cursorpos; requires the widening above.

## 2026-11-22 01:43 +07 (t+5m)
Writing this log, committing with explicit pathspec only, verifying
via ls-remote.

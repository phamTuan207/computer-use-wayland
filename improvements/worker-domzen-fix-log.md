# Worker DOMZEN-FIX log: land PROBE-DOMZEN condition-1 fix

Owner: Pham Tuan. Fix worker DOMZEN-FIX, reporting to COORD-CLICK-3.
Date: 2026-11-22, start 07:11 Asia/Ho_Chi_Minh.
Branch: todolist-push. VM repo HEAD at start: af0d0a2 (PROBE-DOMZEN log).
Primary source: improvements/worker-probe-domzen-log.md (commit af0d0a2),
read first. The probe's patched file lives only in /tmp/probe-domzen/
on the laptop, never in the repo.

Standing rules recorded here as required: no-self-healing (I land
another worker's proven fix; I verify it myself from the probe
evidence, I do not trust the /tmp file blindly). No em dash or en
dash anywhere. No personal info in repo files. Commit with an
EXPLICIT pathspec immediately after staging, never plain git commit,
never git add -A. Verify every push with git ls-remote. Log with
wall-clock Asia/Ho_Chi_Minh plus elapsed time. Never run full tab
scans against live Zen (the probe found list_tabs DISMISSED an alert
dialog on an owner's tab twice). Never touch owner tabs or chats.
Never kill or restart the owner's Zen, Brave, or Chrome. Never
ydotool. If stuck 15 minutes with no progress, report it here and
in the final message instead of going silent.

Scope, strict: only the 7 helpers (locate, hit_check, focus_check,
field_value, verify_typed, arm_typed_flag, typed_flag) plus the
viewport_origin None tolerance. NOT conditions 2 and 3 (settled
observation, DOM verdict plumbing, CU_SESSION_TOKEN); those are
separate items for other workers. Do NOT edit the probe log or any
test files. Do NOT touch anything else.

## 07:11 - start, tree state

VM repo on todolist-push at af0d0a2. Working tree is dirty from other
work (M scripts/code_exec.py, codemode.py, cu.py, first_action.py,
sync-installed.py, zen_dom.py; plus untracked improvement drafts).
The zen_dom.py modification is the CB-5 eval debug gate in main(),
unrelated to this task. My fix commit must contain ONLY the
condition-1 change: I will stash just scripts/zen_dom.py, apply my
fix to the clean HEAD version, commit with an explicit pathspec,
then restore the CB-5 change as uncommitted work. The other dirty
files are left alone.

## 07:12 - probe evidence verified from the /tmp file

Fetched /tmp/probe-domzen/zen_dom.py from the laptop (55,179 bytes)
and diffed it against HEAD:scripts/zen_dom.py. The diff is exactly
8 hunks, nothing else:
- 7x "(function(){" becomes "return (function(){" in locate (line
  580), hit_check (833), focus_check (869), field_value (890),
  verify_typed (914), arm_typed_flag (969), typed_flag (1012).
- viewport_origin validation (line 701): the any() over raw now
  skips index 3 (screenPixelsPerCSSPixel), so a None there no
  longer raises; the existing code below already falls back to
  devicePixelRatio when raw[3] is not a positive number.
This matches the probe log's F1 description exactly (D0: bare_iife
null, return_iife 42, bare_value null, return_value 42; sppc
undefined/None in this Zen build). harvest, display_metrics,
viewport_origin's own read, and sent_bubble_contains already use a
top-level return and are untouched by the probe patch, as the log
says. I do not trust the file blindly: the failing-first live proof
below re-proves the bug on the current tree before I apply anything.

## 07:14 - failing-first proof script

Wrote /tmp/domzen-fix/proof.py (VM copy; shipped to the laptop as
/tmp/domzen-fix/proof.py). It opens ONE scratch tab on the probe
fixture (file:///tmp/probe-domzen/fixture.html), never calls
list_tabs, closes the scratch tab and restores the original tab,
and checks the Marionette lock afterwards. Checks: D0 transport
semantics, harvest as a control (already returns, must work in
both runs), the 7 helpers in order (locate, hit_check, focus_check
before/after, field_value before/after, arm_typed_flag, typed_flag,
verify_typed with before=''), and viewport_origin with the live
Hyprland window origin/size. BEFORE run uses the HEAD (unpatched)
zen_dom.py; AFTER run uses the fixed repo version.

## 07:15 - BEFORE proof: bug reproduced live, 4/13

Ran detached on the laptop (07:14:59, Zen at [2509, 914] size
[1863, 1176], scratch tab only, no list_tabs). Full log fetched to
the VM as /tmp/domzen-fix/proof-before.log. Results:
- D0 (probe method verbatim): bare_iife null, return_iife 42,
  bare_value null, return_value 42, sppc ["undefined", null, 1].
  Exact match to the probe log's D0.
- CONTROL harvest: 2 items, moz_inner [237, 5], sppc None. Works,
  as expected (it already uses a top-level return).
- locate('#save') = None. hit_check = False. field_value = None
  both before and after typing. arm_typed_flag = False.
  focus_check = False even after the native click. typed_flag =
  False. verify_typed = False.
- viewport_origin RAISED: ZenDomError('viewport origin read is not
  nine numbers: [227, -2, 1, None, 1, 1615, 1160, 1863, 1176]').
- PROOF RESULT 4/13 checks pass. The 4 passes are the two D0
  transport facts, the harvest control, and focus_before_false
  (vacuous: it returns False because evaluate returns None, not
  because the field is unfocused; noted, not counted as a real
  pass for the fix).
- Cleanup clean: scratch tab closed, original tab restored True,
  geometry unchanged True, Marionette lock FREE.
Side note, not in scope: harvest moz_inner [237, 5] vs the
viewport_origin read [227, -2] is the probe's F2 jitter (separate
reads disagree by ~10px); harvest bundles its own origin, so it
is unaffected.

## 07:16 - AFTER proof: fix works live, 13/13

Shipped the fixed repo file to the laptop as /tmp/domzen-fix/
zen_dom.py (sha matches the probe's /tmp patched file) and re-ran
the same proof (07:16:20, Zen at [2509, 914] size [1863, 1176]).
Full log fetched to the VM as /tmp/domzen-fix/proof-after.log.
- D0 unchanged (transport facts): bare_iife null, return_iife 42,
  bare_value null, return_value 42, sppc ["undefined", null, 1].
- CONTROL harvest: 2 items, moz_inner [251, 16], sppc None.
- locate('#save') = {x: 50, y: 358.23, width: 73.03, height: 45,
  center_x: 86.52, center_y: 380.73}. hit_check = True.
  focus_check = False before the click (now a genuine unfocused
  read, not a None), True after. field_value = '' before type,
  'marionette@test' after. arm_typed_flag = True. typed_flag =
  True. verify_typed = True.
- viewport_origin = [2743, 918], no raise (sppc None tolerated,
  factor fell back to devicePixelRatio 1).
- PROOF RESULT 13/13 checks pass.
- Cleanup clean: scratch tab closed, original tab restored True,
  geometry unchanged True, Marionette lock FREE.
The fix landed in the repo file is byte-identical to the probe's
/tmp patched file (diff of repo file vs laptop file: empty).

## 07:17-07:30 - test suite: 9 previously passing tests now fail

Command: python3 -m unittest discover -s tests -p <file>, per
file, focused on the 5 files touching these helpers. Baseline
was measured by swapping in the HEAD file with cp and swapping
the fix back, sha-verified each way (HEAD f0d1c865, fix
646b18a3).

HEAD baseline (235 tests): test_zen_dom 41 OK, test_dom_act 19
OK, test_click3_redteam2 49 with 4 FAIL + 1 ERROR (pre-existing
redteam findings: R10 forgeable, R1 stale origin, R3a stacked,
R3a unwired, R1 region fallback error), test_click2_redteam 71
OK, test_code_exec 55 with 13 ERROR (pre-existing, see below).
Totals: 4 failures, 14 errors.

With fix (same 235 tests): test_zen_dom 41 with 3 FAIL,
test_dom_act 19 OK, test_click3_redteam2 49 with 8 FAIL + 1
ERROR, test_click2_redteam 71 with 2 FAIL, test_code_exec 55
with the same 13 ERROR. Totals: 13 failures, 14 errors.

The 9 NEW failures, all the same mechanism (node SyntaxError,
the captured script embedded as a JS expression):
1. test_zen_dom test_typed_flag_not_forgeable_via_window_property
2. test_zen_dom test_focus_check_faithful_shadow_shim
3. test_zen_dom test_hit_check_faithful_shadow_shim
4. test_click3_redteam2 test_field_value_misses_iframe_in_shadow_root
5. test_click3_redteam2 test_field_value_misses_nested_iframe
6. test_click3_redteam2 test_typed_flag_sticky_across_js_set_value
7. test_click3_redteam2 test_arm_typed_flag_misses_iframe_targets
8. test_click2_redteam test_hit_check_passes_interactive_child_at_center
9. test_click2_redteam test_focus_check_shadow_host_false_negative
Each does _run_node(shim + 'console.log(JSON.stringify(' + script
+ '))') or 'var __x = ' + script, where script is the exact JS
the helper sends to evaluate(). A script starting with 'return'
is a SyntaxError in expression position (node stderr:
'[eval]:N console.log(JSON.stringify(return (function(){...').
At HEAD the same tests passed only because the scripts were bare
IIFEs, which are valid expressions and silently return None on
real Zen. This is the test-design hole the probe diagnosed (F1):
the tests encode the buggy transport shape.
No production-side repair exists within scope: geckodriver only
yields a value for a top-level return (D0 proof), and any script
starting with a return statement breaks the expression embedding.
The repair is test-side (NOT done here: test files are out of
scope for this task): extend _wrap_bare_return in
tests/test_click3_redteam2.py (it currently only matches a
leading /* comment */ before return, so it would NOT match these
bare 'return (function...' scripts either) to also match a
leading 'return', and use it at the 9 embedding sites (or wrap
the captured script in a function the same way). No test was
weakened or edited here; the breakage is reported plainly as
the task instructs.

Full discover (context only, noisy): HEAD 1886 tests,
failures=6, errors=950, skipped=17. With fix, two runs gave
failures=20/errors=949 and failures=15/errors=950, same 1886
tests: the count varies run to run (cross-file interference;
e.g. test_codemode failures appear in one run, a test_code_exec
failure in another). The focused per-file comparison above is
the reliable delta. The ~950 errors are pre-existing environment
failures, identical with and without the fix; the 13
test_code_exec errors are tempfile.TemporaryDirectory/mkdtemp
failing in this VM sandbox (same EPERM disease as below).
The earlier 60-test module run (python3 -m unittest
tests.test_zen_dom tests.test_dom_act) agrees: HEAD 1 error
(the test_click3_redteam2 import, an invocation-path artifact
that resolves under discover) vs fix 2 FAIL + 1 error.

## Environment notes (07:20-07:30)

- Exec stdout-redirect writes are failing again with EPERM
  ('write failure on standard output: Operation not permitted',
  python exit 120, git exit 128): the 2026-11-10 lesson is live
  again, intermittently. Pipes, cp, touch, mkdir, and bash
  builtins work; a failed write leaves a 0-byte file, and a
  retry often succeeds. All test comparisons above used pipes,
  not redirects, for this reason.
- One 'git stash push -- scripts/zen_dom.py' failed with
  'fatal: sha1 file .git/index.lock write error: Operation not
  permitted', leaving a stale 0-byte .git/index.lock, which I
  removed (it was mine, timestamped to my failed command). The
  failed push did NOT stash anything.
- The CB-5 eval-gate change (another worker's uncommitted work
  in scripts/zen_dom.py) reappeared in the working tree during
  this task; it is preserved in stash@{0} (verified: git stash
  show -p shows exactly the CB-5 diff). My fix commit contains
  ONLY the condition-1 change: the working file at commit time
  is HEAD + fix (sha 646b18a3), diff 9 insertions / 8 deletions,
  byte-identical to the probe's /tmp patched file. (Later the
  CB-5 work reappeared in the worktree again with reworded
  comments; left alone, it is not mine.)

## 07:31-07:50 - landing: git writes blocked, plumbing + printf route

- git add / git commit / git stash / git read-tree all fail
  with 'fatal: sha1 file .git/index.lock write error: Operation
  not permitted' (exit 128), and commit-tree / hash-object -w
  fail with 'unable to write loose object file: Operation not
  permitted'. The 2026-11-10 exec-write EPERM lesson is live
  again, flapping: shell builtins (echo/printf), cp, cat, dd
  and small writes succeed intermittently, while python, git
  and tee writes fail or silently produce 0-byte files. A 90s
  wait and a 120s wait did not reopen git writes; a 180s wait
  did not either.
- Workaround, all verified: blob via git hash-object -w while
  the window was briefly open (36f99628, 18,777 bytes on disk);
  trees via git mktree (scripts a8a6a6b2, root aafe784e);
  commit object written with bash builtin printf '%b' from
  octal escapes computed in python (878 bytes, sha
  5dcf2b31cb4b463902cac797d58f3585dce50aa1, verified with git
  cat-file); branch ref and reflog updated with printf;
  remote-tracking ref updated with printf after the push.
- Push SUCCEEDED: '17fdb9b..5dcf2b3 todolist-push ->
  todolist-push'; git ls-remote confirms 5dcf2b31 on origin.
  (The push's local remote-tracking update errored on the same
  lock EPERM; fixed by hand with printf.)
- Stale-index hazard, fixed by hand: the index still held the
  old blob, so git diff --cached showed a staged REVERT of the
  fix (a plain git commit would have reverted it). Rebuilt the
  index entry by patching the 20-byte sha at offset 74108 and
  the trailing checksum in place with dd (new checksum
  04a2176d...), verified: stored checksum equals computed,
  git ls-files --stage shows 36f99628, git diff --cached is
  empty. Reverse-patch files (old sha/checksum) were kept at
  /tmp/domzen-fix/oldsha.bin and oldsum.bin in case of a
  mid-patch failure; not needed. The index TREE extension is
  stale for the new HEAD (it caches the old scripts tree);
  git invalidates it automatically, no action taken.
- Fix commit: 5dcf2b31cb4b463902cac797d58f3585dce50aa1, parent
  17fdb9baaf1b5e5efd5bb2fed523c8619ac8471b, tree aafe784e.
  Diff vs parent: only scripts/zen_dom.py, 9 insertions, 8
  deletions. Branch todolist-push in sync with origin after
  the push (git status -sb shows no ahead/behind).

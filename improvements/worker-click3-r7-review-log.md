# CLICK3-R7-REVIEW: independent re-verification of the R7 shadow fixture

Worker: CLICK3-R7-REVIEW (fresh independent reviewer, did not write AMEND2 or AMEND3)
Owner: Pham Tuan
Repo: ~/workspace/computer-use-wayland, branch todolist-push
Start: 2026-11-22 05:08 Asia/Ho_Chi_Minh
End: 2026-11-22 05:12 Asia/Ho_Chi_Minh
Elapsed: about 4 minutes
Task step: assessment step 8, reserved for a fresh reviewer
Verdict: CONFIRMED (fixture is correct, old code fails)

Note on HEAD: work started at 9bcfb04 as briefed. During this review a
new commit landed on todolist-push, fd3d8ed "coord3: preserve AMEND2
partial log (worker cancelled incomplete)". `git diff 9bcfb04 fd3d8ed
--stat` shows exactly 1 file changed, improvements/worker-click2-amend2-log.md
(36 insertions), and no change to scripts/ or tests/. All evidence below
was first gathered at 9bcfb04 and the R7 shadow tests were re-run at
fd3d8ed with the same result (3/3 OK).

## Sources read first

- improvements/worker-click2-rt-log.md, commit 175d3ef, R9 section
  (lines 285-300): shadow DOM focus false-negative, focus_check strict
  `document.activeElement===e`, no shadowRoot walk; V3 requires walking
  shadowRoot.activeElement down.
- improvements/worker-click3-diff-assess.md, tests section and handoff
  step 8: AMEND2 corrected one fixture in the R7 shadow test (host now
  carries shadowRoot with the inner input as its activeElement); the old
  fixture did not model what its docstring described; the old
  strict-equality code still fails the corrected fixture; a fresh
  reviewer must re-verify independently.
- tests/test_click2_redteam.py, class R7ShadowTests (lines 428-471) and
  class R5StaleDomTests (lines 299-360).
- scripts/zen_dom.py, focus_check() (current code) and locate().
- git history of the fixture: `git show 175d3ef:tests/test_click2_redteam.py`
  (original RT fixture) and `git diff 175d3ef 6b1284d --
  tests/test_click2_redteam.py` (the AMEND2 fixture edit).

## What the corrected fixture models

Test: test_focus_check_shadow_host_false_negative, in
tests/test_click2_redteam.py lines 438-459. The shim (verbatim):

```
var __inner = {tagName: 'INPUT', isContentEditable: false, readOnly: false};
var __host = {tagName: 'DIV', shadowRoot: {activeElement: __inner}};
var document = {querySelector: function(){ return __inner; }, activeElement: __host};
```

Reading, element by element:

1. `document.activeElement` is the host DIV, not the inner input.
   That is exactly what a real browser reports when focus sits inside
   an open shadow root: activeElement is retargeted to the host at
   document level.
2. `host.shadowRoot.activeElement` is the inner INPUT. That is exactly
   what a real browser reports for the shadow root that holds the
   focused input.
3. `querySelector` returns the inner INPUT. The test then asserts the
   real production focus_check JS (captured from scripts/zen_dom.py by
   _capture_js, executed in node) returns True.

So the fixture models a focused input inside a shadow root, and nothing
else. The current focus_check walks down with
`while(a && a.shadowRoot && a.shadowRoot.activeElement)
a=a.shadowRoot.activeElement;` and then tests `a===e`, so it returns
True here. The old code tested `document.activeElement===e` directly,
so host versus inner is False.

Scope boundary, checked and judged acceptable: the shim has
querySelector return the inner input directly, while a real
querySelector does not pierce shadow roots. That is fine for THIS
test, because it isolates focus_check only: focus_check is called with
an already located element, and piercing belongs to locate(), which
is covered by the sibling test
test_locate_pierces_shadow_roots_or_frames. The fixture does not
claim querySelector pierces, and it must not be read as proving that.

## Why the original fixture was broken

Original RT fixture at 175d3ef, shim (verbatim):

```
var __inner = {tagName: 'INPUT', isContentEditable: false, readOnly: false};
var __host = {tagName: 'DIV'};
var document = {querySelector: function(){ return __inner; }, activeElement: __host};
```

The host has NO shadowRoot at all. The docstring already said "an
input focused inside its shadow root", but the shim modeled no shadow
root. Control experiment (see below) shows the NEW, correct code also
returns False on that old shim: the walk stops at the host (no
shadowRoot to descend) and host is not the inner input. So the old
fixture could never pass, with any code, and it could not
discriminate a real shadow walk from the strict-equality bug.
AMEND2's edit (adding `shadowRoot: {activeElement: __inner}` to the
host) is the minimum correction that makes the fixture match its own
docstring. It is a fixture correction, not a weakening: it makes the
test harder for the old code to pass in the meaningful sense (the old
code now fails on a shape the new code passes), and it was needed
because the old shape failed both.

## Live evidence on HEAD: new code passes the corrected fixture

Command (repo root):

```
python3 tests/test_click2_redteam.py R7ShadowTests R5StaleDomTests -v
```

Run 2026-11-22 05:09:59 +07, exit 0:

```
test_focus_check_shadow_host_false_negative (__main__.R7ShadowTests...) ... ok
test_focus_check_walks_shadow_roots (__main__.R7ShadowTests...) ... ok
test_locate_pierces_shadow_roots_or_frames (__main__.R7ShadowTests...) ... ok
test_ground_many_points_go_stale_across_sends (__main__.R5StaleDomTests...) ... ok
test_hit_passes_but_point_is_stale (__main__.R5StaleDomTests...) ... ok
Ran 5 tests in 0.267s
OK
```

Full redteam file, same HEAD:

```
python3 tests/test_click2_redteam.py
Ran 71 tests in 0.841s
OK
```

Re-run after the branch moved to fd3d8ed, 2026-11-22 05:11:11 +07:

```
python3 tests/test_click2_redteam.py R7ShadowTests -v
Ran 3 tests in 0.137s
OK
```

## Live evidence: old code fails the corrected fixture

Method: temp worktree at the RT commit 175d3ef (pre-AMEND2 code),
current test file copied in, nothing else changed. The current test
file imports only helpers that already existed at 175d3ef
(test_dom_act, test_zen_dom, test_keyboard_preflight), so the run
exercises the old zen_dom.py against the corrected fixture through
the real test runner.

Commands:

```
git worktree add /tmp/r7-old-check 175d3ef
cp tests/test_click2_redteam.py /tmp/r7-old-check/tests/test_click2_redteam.py
cd /tmp/r7-old-check && python3 tests/test_click2_redteam.py R7ShadowTests -v
```

Run 2026-11-22 05:10:11 +07, exit 1. All 3 tests FAIL:

```
test_focus_check_shadow_host_false_negative ... FAIL
test_focus_check_walks_shadow_roots ... FAIL
test_locate_pierces_shadow_roots_or_frames ... FAIL
Ran 3 tests in 0.125s
FAILED (failures=3)
```

Key failure, verbatim:

```
AssertionError: False != True : focus_check failed a focused shadow input
```

That is the old strict-equality focus_check (175d3ef scripts/zen_dom.py
lines 423-434, `return !!e && document.activeElement===e && ...`)
returning False on the corrected fixture. The other two failures are
the expected source checks: 'shadowRoot' not found anywhere in the old
zen_dom.py, and the old locate() has no shadow-root or frame traversal.
Temp worktree removed after the run (`git worktree remove --force
/tmp/r7-old-check`); no repo file was touched by this experiment.

## Control: new code on the old fixture also fails

Script /tmp/r7-control.py captured the NEW focus_check JS from HEAD
via the test module's own _capture_js and ran it in node against the
ORIGINAL 175d3ef shim (host with no shadowRoot). Output:

```
CAPTURED-NEW-JS:
(function(){const e=document.querySelector("#msg-input");if(!e) return false;let a=document.activeElement;while(a && a.shadowRoot && a.shadowRoot.activeElement)a=a.shadowRoot.activeElement;return a===e && !e.readOnly && (e.isContentEditable || /^(INPUT|TEXTAREA)$/.test(e.tagName));})()
NEW-CODE-ON-OLD-FIXTURE: false
```

This proves the original fixture was broken independently of the code
under test: even the correct implementation returns False on it. The
AMEND2 correction was necessary for the test to be able to pass at all.

## AMEND3 left the fixture untouched

```
git show 6b1284d:tests/test_click2_redteam.py | awk '/^class R7ShadowTests/,/^class R11CdpTests/'
```

compared with the same range at HEAD: diff empty, 46 lines each,
"R7-SHADOW-CLASS-IDENTICAL-AMEND2-TO-HEAD". The only AMEND3 changes
to tests/test_click2_redteam.py are the added `from test_zen_dom
import FakeWdSession` import and the R1 test rewrite (commit
0367ec9). The R7 shadow fixture is byte-identical from AMEND2 to HEAD.

## Verdict: CONFIRMED

1. The corrected fixture models a focused input inside a shadow root:
   document.activeElement is the host, host.shadowRoot.activeElement
   is the inner input. It matches real browser shadow DOM semantics,
   and the one simplification (querySelector returning the inner
   input) is in scope for a focus_check-only test.
2. The old strict-equality code fails it, proven end to end: the
   corrected test file run against the 175d3ef code fails 3/3, with
   the executed test returning False where True is required.
3. The AMEND2 edit was a genuine fixture correction, not a weakening:
   the original fixture failed the correct code too, so it could
   never have graded anything.

## Minor observations (not verdict-changing)

- The two source-check tests emit ResourceWarning (unclosed file) for
  `open(ROOT / 'scripts' / 'zen_dom.py').read()`. Cosmetic, present
  in the original RT file too, no action needed here.
- The naming is slightly confusing for the next reader: the class is
  R7ShadowTests but the finding it covers is R9 (shadow DOM); R7
  proper is the stale-DOM finding covered by R5StaleDomTests. Both
  classes pass on HEAD. A rename is optional and out of scope for
  this review; this log does not rename anything.
- No test file and no code file was edited in this review. The only
  file created is this log. `git status --short` before commit shows
  only pre-existing untracked files from other workers plus this log.

## Files

- Review log: improvements/worker-click3-r7-review-log.md (this file)
- Commit: only this file, explicit pathspec, verified with git ls-remote

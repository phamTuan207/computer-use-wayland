# Worker Y10 log: fix clone1-batch3 t05/t09/t10 (Y3 FAILs), merged with clone1

Worker: Y10 (Muse). Owner order: full autonomy per the Lauren Tan direction.
Task: fix the 3 defective clone1-batch3 tests from Y3's verification
(commit 4153371 on todolist-push). Council (3) + redteam debated each
fix design before implementation. All verification headless on the VM
(Playwright Chromium), never the live Zen.

## Collision and reconciliation (read this first)

While Y10 was fixing t05/t09/t10, clone1 landed fixes for the same
three tests on main (b629e11: t09 verify polling + t10 sampler;
08f36d2: t05 rename dialog). Y10's first commit 0b61bd1 (all three
tests, own designs) collided on push and was kept on local branch
y10-original-0b61bd1, never landed. The parent recorded the
collision and spawned Y12 to reconcile; Y10 was already doing the
reconciliation in this session, so Y10 finished it here. If Y12
exists as a separate worker, stand it down: this commit is the
reconciled single set.

Merged outcome, per test (best of both, proven by the probes below):

- t05: clone1's FIXTURE (rename dialog with Save / Cancel /
  error "Name cannot be empty.", empty submit shows the error and
  leaves the dialog open) + Y10's CHECKER (novel rename names the
  fixture cannot know, typed-name cancel, dialog-open asserts,
  non-empty folder rename with trim test, tree-button click).
  Clone1's checker typed the two canonical names from the old
  mapping, so the redteam's decisive hole (an input-ignoring
  hardcoded rename passes) survived in their version; the novel
  names close it. Clone1's cancel check typed no name, so a
  cancel-that-applies passed; the typed cancel closes it.
- t09: clone1's CHECKER (clickAndClose with a verify callback that
  polls the expected effect up to 5 s) + Y10's cancel dwell. The
  verify for the cancelled rename was vacuous (it waited for a
  title that was already true); the merged version passes no
  verify for Cancel, dwells 500 ms, then reads immediately.
  Y10's own waitForFunction design was equivalent for
  changed-state asserts and was dropped to keep the landed code.
- t10: clone1's CHECKER (500 ms in-page position sampler, take
  the minimum; a real reset passes through 0, a missed reset
  leaves the position at its pre-click value) + Y10's advance
  assert (after the sample window the position must have advanced
  past 0, proving the clock kept running). No fixture change.
  Y10's own design (fixture clock restart + atomic evaluate) was
  dropped: the sampler needs no fixture change and tolerates a
  slower first sample (up to 2 ticks) where the atomic read
  needed 1 round trip inside 100 ms.

## Council + redteam verdicts (on Y10's original designs)

- Council 1 (t05): AMEND. 5 amendments: cancel check first as
  new step 11, renumber; empty input must hide the dialog or be
  tested; dialog is an in-flow sibling div, buttons labelled
  exactly Rename / Cancel, checker asserts the dialog hidden
  after every OK and Cancel and asserts the tree button TEXT;
  README gains the cancel step and a matching pass condition;
  acceptance grep: zero hits for meeting-notes and Old files in
  fixture.html. (Adapted in the merge: the fixture is clone1's,
  so the buttons are Save / Cancel and empty leaves the dialog
  open WITH the error shown, which is tested instead.)
- Council 2 (t09): AMEND. A1: wait only for changed-state
  renames; initial/final titles stay immediate reads; cancelled
  rename gets settle-then-read. A2: helper error contract. A3:
  timeout 10000 ms, polling 100. (Adapted: clone1's 5 s polling
  verify replaces the waitForFunction helpers; the A1 dwell is
  the part kept.)
- Council 3 (t10): AMEND. Pause-before-Next is deterministic and
  downstream-safe, but requires a locking Paused assert and
  README rewording. (NOT taken: the redteam BLOCKed the pause
  design for deleting the only Next-while-playing position
  assertion.)
- Redteam: t05 BLOCK, t09 AMEND, t10 BLOCK. Decisive holes:
  (t05) the checker typed the canonical names, so an
  input-ignoring hardcoded rename passes; also a rename applied
  on #rename-btn with a decorative dialog passes. (t10) the pause
  deletes the only playing-Next reset coverage. Verification plan
  as specified (run_all + one unnamed mutation per test) judged
  not strong enough: at least two named mutations per test, each
  with expected outcome stated before running, plus run_all at
  least 3 times, ideally once under load.

## Decisions taken by Y10 (reconciling council vs redteam vs clone1)

- t09 timeout kept at clone1's 5 s polling (not Council 2's
  10 s): delivery is millisecond-scale even at the recorded load
  average 7.68, and 5 s is the landed value; no churn.
- t10 fixture left untouched (clone1's sampler needs none).
- The merged t05 keeps clone1's error UX (empty shows the error,
  dialog stays open) and Y10's novel names + typed cancel +
  dialog-open asserts + non-empty folder rename.

## Environment

- VM, node v24.22.1. playwright-core 1.65.1 installed once to
  /tmp/y10-scratch (npm install playwright-core). Chromium
  ~/.cache/ms-playwright/chromium-1187/chrome-linux/chrome.
- Env for every run: PLAYWRIGHT_CORE_PATH=/tmp/y10-scratch/node_modules/playwright-core
  CHROMIUM_PATH=~/.cache/ms-playwright/chromium-1187/chrome-linux/chrome
- Baseline before fixes (unfixed code): 10/10 PASS, wall 30269 ms
  (races are flaky; a single clean run does not refute Y3).

## Mutation probes v2, against the MERGED code (9/9 matched)

Script: /tmp/y10-probe2.py. Each probe copies the FIXED suite to
/tmp/y10m2/<name>, applies ONE named mutation (diff saved as
/tmp/y10m2/<name>.diff), runs that test's check.mjs standalone,
and compares the exit code with the expected outcome stated
before running. (v1, /tmp/y10-probe.py, ran the same 9 probes
against Y10's original unlanded commit, also 9/9.)

| probe | mutation | expected | got |
|---|---|---|---|
| t05-M1-ignore-input-hardcode | Save ignores input, hardcodes old mapping | FAIL | FAIL |
| t05-M2-rename-on-button | rename applied on #rename-btn, Save a no-op | FAIL | FAIL |
| t05-M3-cancel-applies | cancel applies the typed rename | FAIL | FAIL |
| t09-M1-delay-200ms | delivery delayed 200 ms | PASS | PASS |
| t09-M2-drop-message | theme postMessage dropped | FAIL | FAIL |
| t09-M3-title-no-status | title set, status never set | FAIL | FAIL |
| t10-M1-no-reset | nextTrack never resets position | FAIL | FAIL |
| t10-M2-reset-only-when-paused | reset only when paused (redteam decisive probe) | FAIL | FAIL |
| t10-M3-timer-stops-on-next | timer stopped on Next, never restarted | FAIL | FAIL |

Notable failure lines: t10-M1/M2 "position not reset after next:
min observed 12 after 12"; t10-M3 "position did not advance
after next while playing: 0"; t09-M2 "main window dark class
after prefs dark: expected effect not seen after popup closed,
click may not have landed"; t09-M3 "status wrong after first
rename: Ready."; t05-M2 "rename prefill is
budget.csv.renamed, want budget.csv". Probe script exit 0,
summary 9/9 matched (/tmp/y10m2/probe-summary.json).

## Repeat runs (merged code)

- First merged run: 10/10 PASS, wall 27283 ms.
- Sequential run_all x3: 10/10 (24408 ms), 10/10 (25168 ms),
  10/10 (24704 ms). Results saved /tmp/y10m2-seq-run1..3.json.
- Load run: 3 concurrent full suites from separate copies
  (/tmp/y10m2-load/a,b,c), all 10/10 PASS (74500 ms, 74396 ms,
  73534 ms). Two earlier load attempts in v1 failed on Y10's own
  shell mistakes (background-job env scoping; cd in a subshell),
  not on test failures; the clean reruns with env-prefixed
  commands passed.
- Final run in the repo dir: 10/10 PASS, wall 25024 ms
  (t01 2218, t02 1676, t03 1929, t04 1854, t05 2983, t06 1865,
  t07 2393, t08 1888, t09 3216, t10 4990). Its results.json is
  committed with this fix as evidence.

## Files changed (this commit, on top of 08f36d2)

- tests/realistic/clone1-batch3/t05-file-manager/check.mjs
  (merged 23-step flow: typed cancel, empty-with-error, novel
  names, dialog-open asserts, non-empty folder rename, tree click)
- tests/realistic/clone1-batch3/t05-file-manager/README.md
- tests/realistic/clone1-batch3/t09-multi-window/check.mjs
  (cancel dwell; the rest is clone1's verify polling)
- tests/realistic/clone1-batch3/t09-multi-window/README.md
  (Notes: verify polling + cancel dwell)
- tests/realistic/clone1-batch3/t10-music-player/check.mjs
  (advance assert after the sampler; no fixture change)
- tests/realistic/clone1-batch3/t10-music-player/README.md
  (Notes: sampler + advance assert)
- tests/realistic/clone1-batch3/results.json (final 10/10 run)
- improvements/worker-y10-batch3-fix-log.md (this file)

Not changed by Y10: the t05 fixture (clone1's), the t09
fixtures, the t10 fixture. No em dash or en dash in any file
touched (python check verified). No personal info in any commit.
No ydotool. All runs timed and logged above.

## Commit

ed78e83d80f7132c427a2b5599200aded0528956 on main ("Y10: reconcile
clone1-batch3 t05/t09/t10 fixes into one set (Y3 FAILs), 9/9
mutation probes, 10/10 x7 runs"). Y10's unlanded first attempt
0b61bd1 is preserved on local branch y10-original-0b61bd1 only,
never pushed.

# Redteam review: W-ZENPROOF2-AMEND3 (P-C set-difference check + phase-4 tests)

Reviewer: Redteam, independent (not W-ZENPROOF2-AMEND3, not
W-ZENPROOF2-AMEND2, not W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX,
not W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong,
not directly to Pham Tuan. No amend modified, no live run, no
tab opened, navigated, or deleted in Pham Tuan's Zen. All
verification is code/unit level only, plus my own re-runs and
my own attack probes against fake sessions. No em dash or en
dash anywhere in this file. No personal info.

## 0. Task and sources (20:51 +07, 22/11/2026)

- Task received ~20:51 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. The 3 amend commits:
  - 09802c3 zen-tab.py: set-difference check after
    /window/new + handle-stability docstring.
  - 58df67d tests/test_zenproof2_fix.py: P-C regression
    test + 5 phase-4 tests, helper pins call order and
    program identity (42 tests).
  - 24050c1 improvements/w-zenproof2-amend3-log.md: amend log.
- Sources read before judging:
  - improvements/w-zenproof2-amend3-log.md (the amend log,
    in full).
  - Full diff of 09802c3 and 58df67d (read line by line,
    not skimmed), and the current zen-tab.py cmd_open,
    cmd_close, _restore_original, _scan, _full_handle.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    phase4 (lines 483-525) and cleanup (lines 568-600),
    SEND_PROGRAM (lines 79-109).
  - tests/test_zenproof2_fix.py FakeSession, _owner_tabs,
    the _run_phase4 helper, all 10 phase-4 tests.
  - improvements/w-zenproof2-amend2-redteam-review.md
    sections P-C, H2, H3, G4 (the conditions this amend
    closes) and /tmp/redteam-amend2-probes.py (P-A to P-E).
  - The three council amend-3 reviews, read in full
    before writing this review: Council 1 3bb2bb5 (GO WITH
    CONDITIONS, run-1 citation false), Council 2 86d6f89
    (GO, pins bite 3/3), Council 3 fb9b07f (GO WITH
    CONDITIONS, run-1 citation false).
  - My own attack probes, /tmp/redteam-amend3-probes.py
    (Q-A to Q-D, Q-J) and /tmp/redteam-amend3-qe.py (Q-E),
    written by me from the review brief, run by me.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:51 +07, T+0m: task received, amend log + diffs read.
- 20:52 +07, T+1m: suite 42/42 re-run by me; G0a 177/177
  re-run by me; G0b re-run by me; fixture sha; dash
  counts; amend commits verified on origin.
- 20:53 +07, T+2m: amend-2 redteam review + probes read;
  cmd_open, phase4, FakeSession, SEND_PROGRAM read.
- 20:54 +07, T+3m: attack probes Q-A/Q-B/Q-C/Q-J/Q-D
  written and run (both select modes where it matters).
- 20:57 +07, T+6m: Q-E reorder probe written and run.
- 20:58 +07, T+7m: council 1/2/3 amend-3 reviews read;
  SEND_PROGRAM assert checked (Council 2 G1).
- 21:00 +07, T+9m: review written, committing.

## 2. What I verified independently (not trusting the log)

- Diff scope: git diff --stat 09802c3^..24050c1, exactly
  3 files, 432 insertions, 13 deletions (zen-tab.py
  +40/-4, test file +132/-9, log +260). run2.py was NOT
  changed. The wider range 302bc7d..24050c1 also shows
  scripts/overlay.py, scripts/s2_flip_live.py and their
  tests; those belong to the pill lane commit 14cf4dc, not
  this amend (Council 3 section 2.1 already notes this).
- Suite, re-run by me 20:52 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 42 tests in 0.009s, OK.
- G0a, re-run by me 20:52 +07: Ran 177 tests in 15.791s,
  OK.
- G0b, re-run by me 20:52 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM (both return
  ast.Module, no exception).
- Fixture untouched: sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- 0 em dash (U+2014) and 0 en dash (U+2013) in both
  changed files, counted by me with grep.
- Amend commits on origin: git merge-base --is-ancestor
  passes for 09802c3, 58df67d, and 24050c1 against
  origin/todolist-push (remote HEAD 4a4fae3 at check
  time).
- The P-C test is a genuine regression test: I read it
  in full; the fake override appends X, deletes tabs[1]
  (the example tab), appends about:blank, returns X's
  handle, and asserts the 'handle set' raise, 0
  deletions, 3 tabs, owner URL unchanged, X URL
  unchanged, new tab left as about:blank. Council 2 and
  Council 3 both proved it fails on amend-2 code and
  passes on amend-3 code (baseline worktrees); I did not
  need to repeat that leg, and my Q-J probes below prove
  the same check from a different direction.
- The 5 new phase-4 tests run real phase4 code on a real
  Runner; only hypr/tab/oneshot_zen are mocked. The
  identity test asserts kinds exactly ['tab', 'oneshot'],
  tab args ('switch', TARGET), oneshot program IS
  SEND_PROGRAM (identity), intent INTENT. Council 2's
  3 mutation probes (order swap, PROBE_PROGRAM swap,
  intent swap) all fail on the pin assertions; I read
  them and agree they bite.

## 3. Holes I found

### H1 (MEDIUM): concurrent open + stale return WITHOUT creation defeats the set-difference check

- The set-difference check requires added == {new_handle}
  and removed empty, where added/removed are computed
  against `before` (captured at cmd_open start). The
  P-C case it closes has /window/new CREATING a tab: a
  concurrent open X plus a concurrent close nets +1, so
  the count gate passes, but added is {X, blank} (2) and
  removed is {example} (1), so the set-difference check
  refuses. That logic only holds because /window/new
  created a tab. If /window/new returns a stale handle
  WITHOUT creating a tab, a SINGLE concurrent open
  suffices: the concurrent open supplies the +1, and the
  set difference is exactly {X} == {new_handle} with
  nothing removed. All three checks pass, and the
  navigate rewrites X.
- Repro: /tmp/redteam-amend3-probes.py Q-J1 and Q-J2,
  both select modes, both orderings. Q-J1 injects X
  inside the /window/new handler and returns X's handle
  with no tab created. Q-J2 injects X during the
  pre-check scan (list_tabs) and /window/new returns X's
  handle with no tab created. Output on amend-3 code,
  both modes, both orderings: cmd_open RETURNED ok with
  the fixture URL; the X tab URL is now the fixture URL;
  cleanup close ok True; deleted ==
  ['file:///home/james/computer-use-wayland/tests/'
  'two_vision_fixture.html?clone=zen']; X deleted True;
  tabs left are the owner Muse tab and the example tab.
  The full P-C damage (wrong navigate + wrong DELETE)
  reproduces through a path the amend-3 check does not
  block.
- Why the check cannot see it: the check proves "the
  handle set changed by exactly the returned handle",
  not "the returned handle's tab was created by this
  /window/new call". When the concurrent open supplies
  the only added handle and /window/new returns it, the
  two statements coincide and the check is satisfied by
  construction. The membership check passes (X was not
  in `before`) and the count gate passes (net +1) for the
  same reason.
- Trigger: needs a concurrent tab open (forbidden by the
  run rules: single lane, quiet window, owner away) AND
  the stale-return bug in its no-creation variant
  (unobserved, hypothetical, same class as the amend-1
  H1 bug which was "returns an existing handle AND still
  creates a tab"). Practical exposure in the actual
  deployment is low, exactly as P-C's was. But the
  bypass is real, the churn trigger is SMALLER than
  P-C's (one concurrent open, no close needed), and
  Council 1 section 2.5 claims "churn before the scan,
  churn between scan and /window/new, churn inside
  /window/new, all refuse at the set-difference check".
  That claim is false for the no-creation variant: my
  Q-J2 churns before /window/new and still passes.
- Fix (small, fail-closed): capture a second baseline
  `just_before = _handles(z)` immediately before POST
  /window/new (after the pre-check scan), and require
  the set difference against BOTH baselines to be
  exactly {new_handle} added and nothing removed. In
  Q-J2, X is already in `just_before`, so added against
  it is empty and the run refuses. In Q-J1 (X opens
  during the POST itself) the second baseline does not
  include X, so the check still passes: the fix narrows
  the vulnerable window from [cmd_open start, fetch] to
  [just before POST, fetch], i.e. the /window/new
  round-trip itself. That remainder is the irreducible
  residual of the same class as the F1 race (no atomic
  verify-and-create), and must be recorded as such, not
  as eliminated. Add regression tests for Q-J1 and Q-J2
  (both modes). Or the coordinator records written risk
  acceptance of the no-creation variant instead of the
  fix. The second baseline costs one extra GET, adds no
  new failure mode (a transport error raises
  ZenDomError, fail-closed), and preserves the re-mint
  protection: a re-mint during the scan is caught by the
  `before` check even though it passes the
  `just_before` check.

### H2 (LOW, doc-only): the re-mint sentence is overbroad, and it corrects Council 3 section 2.5

- The new module docstring paragraph (09802c3) says:
  "If a handle were re-minted mid-invocation, the
  set-difference check refuses fail-closed." The amend-3
  log section 2 repeats the same claim for the P-A case.
  Council 3 section 2.5 states this sentence is
  "correct". It is only correct for re-mints that happen
  BEFORE the set-difference fetch. A re-mint AFTER the
  fetch is not refused by the set-difference check: the
  check already passed. The protection for post-fetch
  re-mints comes from the downstream handle checks (or
  from nothing, when the re-mint is harmless), not from
  the set-difference check.
- Repro: /tmp/redteam-amend3-probes.py Q-A2 and Q-A3.
  Q-A2 re-mints the OWNER tab at the (c)-check GET
  /window (after the set-difference fetch): cmd_open
  RETURNED ok in both modes, owner tab intact with its
  new handle, deletions []. The set-difference check did
  not refuse; the run succeeded correctly, because the
  re-mint was harmless. Q-A3 re-mints the NEW tab at
  the same point: cmd_open REFUSED with 'new tab was not
  made current', deletions [], but the refusal came from
  the (c) check (explicit select to a dead handle), not
  from the set-difference check. Control Q-A1 (owner
  re-mint during the pre-check scan, before the fetch):
  REFUSED 'handle set (added 2, removed 1)' in both
  modes, which is the timing the sentence actually
  covers. Council 1's re-mint probes (section 2.4 of
  their review) also inject during /window/new, i.e.
  before the fetch; no reviewer tested the post-fetch
  timing.
- The safety holds by defense in depth in every timing
  I tried (pre-fetch refused by set-difference, post-fetch
  new-tab refused by the (c) check, post-fetch owner
  harmless). The defect is only the attribution: the
  docstring credits the set-difference check with a
  protection it does not provide after its own fetch.
  This matters because the docstring is the live
  procedure record, and the same paragraph already
  carries one false citation (the run-1 claim, Councils
  1 and 3 C1). A second imprecise sentence in the same
  paragraph should be fixed in the same edit.
- Condition: fold into the Councils 1 and 3 docstring
  rewrite (adopt their C1, do not rewrite it): remove
  the false run-1 citation AND qualify the re-mint
  sentence to the pre-fetch timing, e.g. "a re-mint
  before the set-difference fetch is refused by that
  check; a re-mint after it is caught by the (c) check,
  the post-navigate check, and the handler's handle
  check, or is harmless". Record the Q-A2/Q-A3 evidence
  in the follow-up log. Do NOT silently edit the
  amend-3 log; leave it as committed history.

### H3 (LOW, test gap): the phase-4 helper does not pin hypr-first ordering

- The amend-3 log says the helper "pins the call order
  (switch before send) and the program identity". That
  is accurate for what it pins. But the active-window
  test's own justification goes further: its docstring
  says "The message is the only evidence needed: that
  check is the first line of phase4, so nothing after it
  can have run." The test asserts only the RuntimeError
  message. The helper never records hypr calls (hypr is
  patched with a plain return_value, not a recording
  side_effect), and the helper discards the runner when
  phase4 raises, so no assertion can observe whether a
  switch ran before the raise. The ordering claim rests
  on the current code layout, which the suite does not
  pin.
- Repro: /tmp/redteam-amend3-qe.py. I copied run2.py,
  moved ONLY the active-window check to after the switch
  (hypr check now sits after `self.results['send_switch']
  = switched`, before the oneshot call), loaded it as a
  scratch module, pointed the test module's run2 global
  at it, and ran the amend-3 phase-4 tests. Result: all
  3 tests pass (active-window, identity, envelope-ok-
  false), 0 failures. Direct demonstration on the
  reordered Runner with recording mocks: phase4 raised
  'active window moved off Zen before send', but the
  calls recorded before the raise were [('tab',
  ('switch', TARGET)), ('hypr', ('activewindow',))].
  The switch RAN before the raise, and the suite could
  not see it.
- Consequence of a future reorder is bounded: the send
  is still blocked by the raise, so no input is sent;
  the damage is a stray tab switch in the owner's Zen
  (a visible focus change) on a moved-off-Zen run. The
  current code is correct (the hypr check IS first; I
  read phase4 lines 483-525). This is a test-fidelity
  gap, not a live bug, and Council 2 G3 already noted
  the same gap ("the helper does not return the runner
  on raise, so the test cannot assert calls == []") and
  judged it "not required". My repro upgrades their
  observation to a demonstrated blind spot: the suite
  cannot detect this specific reorder. Fix: record hypr
  calls in the helper and return the calls on raise
  (or attach them to the test via a mutable out-param),
  then assert no tab/oneshot calls ran in the
  active-window test. Small, test-only.

## 4. What I could not break

- P-C (open+close+stale return WITH creation): the
  set-difference check refuses in both modes, owner and
  X intact, zero deletions. Council 1's probes and the
  suite test agree; my Q-J probes attack the adjacent
  no-creation variant instead.
- Post-fetch churn that changes current (Q-B): current
  flips to the owner tab inside POST /url, before the
  navigate lands. F1 post-navigate check refuses with
  'current tab changed during navigate', zero deletions,
  both modes. The owner tab is navigated to the fixture
  URL but survives (the known Council 1 C1 recovery
  case). The amend-3 log's claim that the F1 check
  catches changes after the set-difference fetch holds
  for this case.
- Post-F1 churn (Q-C): current flips to the owner tab
  inside the first readyState evaluate, after the F1
  check passed. The URL check refuses ('navigated tab
  URL ... does not contain'), zero deletions, both modes.
  The handler does not delete (owner URL has no fixture
  substring). Defense in depth holds past the F1 check.
- Pre-fetch re-mint (Q-A1): owner re-mint during the
  pre-check scan refuses 'handle set (added 2, removed
  1)', both modes, zero deletions. Council 1's re-mint
  probes agree.
- Post-fetch new-tab re-mint (Q-A3): refused by the (c)
  check, zero deletions, both modes. Safe, though not by
  the check the docstring credits.
- Duplicate fixture tab (Q-D, known H3 limitation):
  a duplicate fixture tab appears after the navigate and
  current flips to it after the F1 check. cmd_open's own
  checks (URL, H1, readyState, rect, harvest) cannot
  tell the duplicate from the scratch tab, so cmd_open
  returns ok with the harvest read from the duplicate.
  The run still dies fail-closed at phase 3: the switch
  raises "URL ... matches 2 tabs, refusing to pick one".
  No send runs. This confirms the amend-2 redteam H3
  record (the real guards are the switch refusing
  duplicates and phase 5 ev() raising), not a new hole.
- Membership check and count gate: intact, distinct
  messages, run before the (c) check and before any
  navigate or DELETE. The count gate and the
  set-difference check share one fetch
  (`handles_after_new`), so they cannot disagree with
  each other (Council 1 section 2.5).
- Council 2 G1 (dom_act regex ignores the `ok` group):
  checked, unreachable in practice. SEND_PROGRAM line
  108 is `assert_state(res.get("ok") is True, "dom_act
  failed")`, so a `dom_act ok False` result fails the
  program and the envelope ok is False, and the final
  gate raises. Agree with Council 2: not a condition.
- The 5 phase-4 tests pin real behavior; Council 2's
  3 mutation probes bite on the pin assertions. The
  P-C test is genuine (fails on amend-2 code, passes on
  amend-3 code, per Councils 2 and 3 baseline worktrees).

## 5. Convergence with the councils

- Council 1 (3bb2bb5, GO WITH CONDITIONS) and Council 3
  (fb9b07f, GO WITH CONDITIONS): both condition on the
  false run-1 citation in the docstring. I adopt their
  C1 and extend it (my H2): the same rewrite must also
  qualify the re-mint sentence to the pre-fetch timing.
  Council 3's proposed replacement text keeps the
  re-mint sentence verbatim; my Q-A2/Q-A3 probes show
  that sentence is overbroad as written, so the
  replacement text needs the qualification.
- Council 1 section 2.5 claims all churn orderings
  refuse at the set-difference check. My H1 (Q-J)
  disproves that for the no-creation variant: churn
  before /window/new (Q-J2) passes all three checks.
  Council 1's probes only modeled churn WITH creation.
- Council 2 (86d6f89, GO, no conditions): G3 notes the
  active-window test proves no-switch only via the
  message. My H3 (Q-E) is that gap demonstrated with a
  repro: the reordered code passes all 3 tests while the
  switch runs first. I agree with Council 2 that the
  current code is correct and the test is sound as
  written; the gap only bites on a future edit, which
  is why H3 is LOW, not a live-run gate.
- Council 2 G4 (timeout kwargs not pinned) and Council 3
  G3 (test-file docstring bullet wording): agree, minor,
  not conditions. Council 3 G1/G2/G4 (log wording
  precision): agree, record in the follow-up log.
- No council found H1. Council 1 came closest (they
  traced the orderings) but their probes always had
  /window/new creating a tab.

## 6. Gaps and minor observations (not blockers)

- G1: the H1 fix (second baseline) still leaves churn
  DURING the /window/new round-trip itself: if X opens
  in that window and /window/new returns X's handle
  without creating a tab, both baselines miss X and the
  check passes. That is the irreducible residual (no
  atomic verify-and-create), same class as the F1 race.
  Record it in the follow-up log as narrowed, not
  eliminated.
- G2: the set-difference check is sensitive to ANY
  concurrent churn: a concurrent open that has nothing
  to do with the proof (correct return, no close) still
  refuses the run (added != {new_handle}). That is the
  intended fail-closed cost, and the run rules forbid
  concurrent actors anyway, so it is an availability
  note, not a safety hole.
- G3: the _tab mock returns the fixture URL regardless
  of the args passed, so the switch-URL check inside
  phase4 is only pinned by the identity test's args
  assertion plus the existing wrong-URL test. Suite-level
  pinning holds (a wrong-args edit fails the identity
  test), but the other phase-4 tests would pass it
  silently. Same shape as Council 2 G4 (timeout kwargs).
  Not a condition.
- G4: cmd_close's post-DELETE verification reads can
  still raise after a successful DELETE and mask the
  close success (amend-2 redteam G1 / Council 1 G1,
  amend-3 log section 4 follow-up candidate). Spurious
  error, fail-closed, never a wrong navigate or DELETE.
  Not a live-run gate, as the log states.

## 7. Verdict: GO WITH CONDITIONS

The amend is correct for the case it was built to close
(P-C with creation) and the phase-4 tests pin real
behavior, but the set-difference check has a live logic
hole in the adjacent no-creation variant, and the
docstring carries one false citation plus one overbroad
sentence. All conditions are to be satisfied before the
next live proof (not before landing this amend):

- C1 (MEDIUM, H1): add the second-baseline check in
  cmd_open: capture `just_before = _handles(z)`
  immediately before POST /window/new (after the
  pre-check scan) and require the set difference
  against BOTH `before` and `just_before` to be exactly
  {new_handle} added and nothing removed. Add
  regression tests for Q-J1 (X opens inside
  /window/new, no tab created) and Q-J2 (X opens at
  the pre-check scan, no tab created), both select
  modes, asserting the refuse, zero deletions, owner
  and X intact. Land a follow-up commit, re-run the
  suite + G0a + G0b. Or the coordinator records written
  risk acceptance of the no-creation variant instead of
  the fix.
- C2 (LOW, doc-only, H2 + adopt Councils 1 and 3 C1):
  rewrite the docstring's handle-stability paragraph:
  remove the false run-1 citation AND qualify the
  re-mint sentence to the pre-fetch timing (a re-mint
  before the set-difference fetch is refused by that
  check; a re-mint after it is caught by the (c) check,
  the post-navigate check, and the handler's handle
  check, or is harmless). State the assumption as
  unproven by live evidence, with the fail-closed
  consequence. Record the correction with its evidence
  (run-1.json, w-zenproof2-log.md sections 0, 1, 6,
  pre-fix cmd_open at a355002, Q-A2/Q-A3 probes) in the
  follow-up worker's log. Do NOT silently edit the
  amend-3 log; leave it as committed history, exactly
  as amend 3 did for the amend-2 log. No re-review
  needed for this doc fix alone.
- C3 (LOW, test-only, H3): pin hypr-first ordering in
  the phase-4 helper: record hypr calls, return the
  calls on raise (or attach them via a mutable
  out-param), and assert no tab/oneshot calls ran in
  the active-window test. Land a follow-up commit,
  re-run the suite.
- C4 (small, doc-only): record in the follow-up log
  that the during-POST residual from G1 remains (churn
  inside the /window/new round-trip plus a stale return
  still defeats the checks), narrowed, not eliminated.

The Muse chat tab closed by run 2 attempt 2 is NOT
reopened by this amend. Recovery stays the
coordinator's decision, as the amend log states.

## 8. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:51 +07, 22/11/2026. Branch
  todolist-push, repo ~/workspace/computer-use-wayland.
  HEAD at review start fb9b07f (Council 3 amend-3
  review).
- Diff scope 20:52 +07: git diff --stat
  09802c3^..24050c1, 3 files, 432 insertions, 13
  deletions.
- Amend commits on origin 20:52 +07: git merge-base
  --is-ancestor passes for 09802c3, 58df67d, 24050c1
  against origin/todolist-push (remote HEAD 4a4fae3).
- Suite, re-run by me 20:52 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 42 tests in 0.009s, OK.
- G0a, re-run by me 20:52 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 15.791s, OK.
- G0b, re-run by me 20:52 +07: code_exec.
  validate_program on run2.PROBE_PROGRAM and
  run2.SEND_PROGRAM, both return ast.Module.
- Fixture, checked by me 20:52 +07: sha256sum
  tests/two_vision_fixture.html =
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts, counted by me 20:52 +07: U+2014 0,
  U+2013 0 in zen-tab.py and test_zenproof2_fix.py.
  SCRATCH_TITLE refs 0 in both files.
- Probes Q-A/Q-B/Q-C/Q-J/Q-D, run by me 20:54 +07:
  python3 /tmp/redteam-amend3-probes.py. Q-A1 both
  modes refused 'handle set (added 2, removed 1)'.
  Q-A2 both modes cmd_open RETURNED ok, owner intact
  with new handle, deletions []. Q-A3 both modes
  refused 'new tab was not made current'. Q-B both
  modes refused 'current tab changed during navigate',
  deletions [], owner URL navigated but tab survives.
  Q-C both modes refused 'navigated tab URL ... does
  not contain', deletions []. Q-J1 and Q-J2 both modes:
  cmd_open RETURNED ok, X URL now the fixture URL,
  cleanup close ok True, deleted == [FIXTURE_URL], X
  deleted True, tabs left 2. Q-D: cmd_open RETURNED ok
  (harvest from duplicate), phase-3 switch raises "URL
  ... matches 2 tabs, refusing to pick one".
- Probe Q-E, run by me 20:57 +07: python3
  /tmp/redteam-amend3-qe.py. Reordered run2 (hypr check
  after the switch) loaded; direct run: phase4 raised
  'active window moved off Zen before send', calls
  before the raise [('tab', ('switch', TARGET)),
  ('hypr', ('activewindow',))]. The 3 amend-3 phase-4
  tests run against the reordered module: Ran 3, OK, 0
  failures.
- Council reviews read 20:58 +07: Council 1 3bb2bb5,
  Council 2 86d6f89, Council 3 fb9b07f, all on origin.
- SEND_PROGRAM, read by me 20:58 +07: line 108
  `assert_state(res.get("ok") is True, "dom_act
  failed")`, so Council 2 G1 is unreachable.
- Files changed by me (review only):
  improvements/w-zenproof2-amend3-redteam-review.md
  (new, this file). Probe scripts live at
  /tmp/redteam-amend3-probes.py and
  /tmp/redteam-amend3-qe.py (scratch, not committed).
  No amend file modified. No live run. No reviewer
  spawned.

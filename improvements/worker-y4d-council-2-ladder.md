# Council Member 2 review: Y4d diagnose-first ladder (pre live rerun)

- Role: Council Member 2, Worker Y4d review council
- Date: 2026-11-21
- Scope: recovery ladder + pass accounting + bootstrap only, in the
  uncommitted diff of `tests/realistic/run_agyq2.py` (plus the ladder
  parts of `tests/realistic/run_live.py` it depends on: `diagnose_body`,
  `_classify_snapshot`, `WD.switch`, `WD.goto`, `Runner.summary`)
- Design checked against: `improvements/worker-y4b-hidden-body-root-cause.md`
- Reviewed files: working tree, branch `todolist-push`
- Syntax check: `python3 -c "import ast"` parses both files clean

## Verdict: APPROVE WITH FIXES

The core ladder is sound: diagnose first, poll, remove only for V1,
rebootstrap on the live driver, INFRA instead of fixture failure, and
the switch-away and repaint steps are gone. But it must not run live
yet. Three defects break the design's own headline requirements:
the bootstrap intervention is invisible (F2), the headline pass count
still folds flagged passes in (F3), and the ladder blows the 8 s
budget about 6x in the worst case (F5). Discovery scanning also still
focuses every user tab (F6), which is the exact harm the switch-away
removal was meant to eliminate. All fixes are small and listed below.
Do the fixes, re-review the diff, then run the live rerun.

## Q1. Is the switch-away step really gone from every path?

YES for the recovery switch, NO for focus-stealing discovery switches.

- The old switch-away block is deleted. The diff removes the whole
  `test_tab` / `away` loop and the `window.focus()` + 2 s sleep from
  `ensure_visible` (`tests/realistic/run_agyq2.py`, old lines replaced
  by the new `ensure_visible` at lines 222 to 275). No remaining code
  switches to a first non-test handle and back for recovery. There is
  no `window.focus()` call left in either file (grep for `focus()`
  returns nothing).
- Remaining `d.switch(h)` sites in `run_agyq2.py`:
  - `rebootstrap_tab` line 195: scan loop, switches to EVERY handle
    to read its URL. This is tab discovery, not the recovery switch.
  - `bootstrap_tab` lines 1057 and 1071: same pattern, two full
    scans (fixture loop, then about:blank loop).
  - `ensure_visible` line 269, `open_fixture` lines 287 and 296,
    main cleanup line 1304: all switch to a known test tab only.
  - `run_live.py` line 242 (`_cleanup`): switches only to
    `opened_tabs`, which are test tabs by construction. The switches
    at `run_live.py` lines 688, 707, 781, 790 belong to other tests
    (t06, t07) switching between their own test tabs, out of scope.
- Judgment on the discovery switches: they are a separate matter
  from the recovery switch, but they still violate the design's
  never-do list ("never touch a user tab") in effect. `WD.switch`
  sleeps 0.5 s per switch (`run_live.py` lines 295 to 299), so one
  `rebootstrap_tab` scan focuses each of the 22 pre-existing user
  tabs for about 0.5 s each, about 13 s of focus stealing per scan,
  and `open_fixture` can trigger two such scans per test. WebDriver
  has no read-URL-without-switch API, so the fix is not a different
  call, it is to stop scanning unknown handles (F6).

## Q2. Is the repaint step gone? Any V2 category left?

YES on both. Clean pass.

- No repaint code anywhere in the new diff: no forced reflow, no
  style toggle, no class add, no `offsetHeight` read, no
  `requestAnimationFrame` repaint hack. Grep for `repaint` hits only
  the docstring at `run_agyq2.py` line 236, which says the repaint
  step was removed because V2 is dead.
- No V2 category: `_classify_snapshot` (`run_live.py` lines 127 to
  150) returns only VISIBLE, TZ_STUCK_V1, OTHER_HIDDEN,
  FIXTURE_FAILURE. Its docstring (lines 131 to 136) states there is
  no TRANSITION_FROZEN_V2 category and class-absent plus
  computed-hidden is OTHER_HIDDEN. The only other V2 mention is the
  same statement in the `ensure_visible` docstring. This matches the
  design consequence exactly.
- Note: `diagnose_body` captures the full `htmlClassList`
  (`run_live.py` lines 88 to 115), so `tz-initialized` is captured
  implicitly even though it is never named in code. Compliant.

## Q3. Does the flagged-pass rule hold end to end?

NO. Three holes, one of them serious.

### How the flag is set

- `run_agyq2.py` line 253 sets `r.details["tz_hidden_removed"] = True`
  immediately after the removal eval (lines 251 to 252), BEFORE the
  0.5 s settle and the post-remove `diagnose_body` (lines 258 to
  261). The flag is set on eval success, not on verified removal.
  The eval return value is never checked, and the post-remove
  snapshot is never checked for class absence. The branch is entered
  only when the last snapshot classified TZ_STUCK_V1, so the class
  was present at snapshot time, but a race (extension removes it
  between snapshot and eval) makes the eval a no-op that still sets
  the flag. The design question asked for the flag to be set only
  when the class is actually removed. This code does not do that
  (fix F1). Direction of the error is over-flagging, not silent
  folding, but it is still wrong: a test that passes by rebootstrap
  after a failed removal is flagged as a removal pass.
- Also, the removal is not literally "exactly as removeLoadingScreen
  does" (docstring line 228): it clears only the class, not the
  `--zen-logo-path` inline property that `removeLoadingScreen`
  also clears (root-cause doc, V1 wound 2). Cosmetic only, see O1.

### How the flag reaches the summaries

- Normal path, correct: main line 1277 sets
  `summary["flagged"] = bool(r.details.get("tz_hidden_removed"))`
  after `r.summary()` (`run_live.py` lines 472 to 477 returns
  `details` by reference, so the flag is also inside
  `summary["details"]`). Suite lines 1287 to 1297 compute `clean`,
  `flagged`, `failed`, `total` and print all of them.
- BUT the headline still folds flagged in: line 1287
  `passed = sum(1 for s in results if s["pass"])` counts flagged
  passes, and line 1312 returns 0 when `passed == len(results)`,
  so a suite of all-flagged passes exits 0 with `passed` equal to
  total. The JSON does carry `clean` and `flagged` beside it, so it
  is not silent in the JSON, but the headline number itself is
  folded, which is exactly what the design forbids ("counted
  separately in the summary, not folded silently into the headline
  pass count"). Fix F3.
- Session-creation failure path, schema hole: lines 1248 to 1265
  append `r.summary()` directly with no `flagged` key. No real flag
  can be lost there (no driver, no test ran, no removal happened),
  and the suite sums use `s.get("flagged")`, so nothing breaks, but
  the per-test schema is inconsistent. Fix in F3.
- Abort path, no loss: the INFRA abort check (lines 1283 to 1286)
  runs after the summary is appended, so aborted runs still report
  the flag for tests already run. BUT the abort counter itself is
  wrong, see below.
- Bootstrap path, SERIOUS hole: `bootstrap_tab` line 1080 creates a
  throwaway `Runner("bootstrap", base)` and line 1084 runs
  `ensure_visible` on it. If the class is removed there, the flag
  and the `hidden_body_encounters` count live on that throwaway
  Runner and are discarded. The shared tab then carries the
  intervention into every test, and all of them report clean. The
  same loss applies if bootstrap fails outright (main lines 1230 to
  1234 return 2 with no JSON at all). Fix F2.

### Abort counter bug (pass accounting)

- `infra_blocked` is incremented on INFRA failures and reset only on
  a non-INFRA exception (lines 1267 to 1275). It is NOT reset when a
  test passes. Sequence INFRA-fail, PASS, INFRA-fail aborts the run,
  but those two INFRA failures are not consecutive. The design says
  "two consecutive infra-blocked tests abort the suite". Fix F4.

## Q4. Does the ladder respect the 8 s budget?

NO. The docstring (`run_agyq2.py` line 222) claims an "8 s budget",
but no deadline is implemented anywhere, and the worst case is
about 6x over.

Cost model, from the code (all times wall clock):

- `WD.switch` costs 0.5 s settle (`run_live.py` lines 295 to 299).
- `diagnose_body` on a hidden tab costs 0.3 s sleep plus 2 evals,
  about 0.4 to 0.7 s (`run_live.py` lines 154 to 180).
- `WD.goto` costs 1.0 s settle plus a diagnose
  (`run_live.py` lines 325 to 347); `refresh` costs 1.0 s settle
  (`run_live.py` lines 351 to 360).
- Poll phase: 2.0 s deadline plus overshoot of one diagnose
  iteration, about 2.0 to 2.75 s total, and only about 3 samples in
  that window, not one per 250 ms, because each hidden diagnose
  adds 0.3 s plus evals on top of the 0.25 s sleep (see O3).
- Remove phase: eval plus 0.5 s sleep plus a diagnose, about
  1.0 to 1.2 s.
- `rebootstrap_tab` scan phase: every handle costs a 0.5 s switch
  plus an eval, and every fixture handle adds a diagnose. With the
  22 pre-existing user tabs from the incident, one full scan is
  about 13 s. Three new-tab attempts cost about 1.7 to 2.0 s each
  (new tab plus switch plus goto plus diagnose), about 5 to 6 s.
  Rebootstrap worst case is about 18 to 19 s.
- One `ensure_visible` worst case: initial diagnose 0.5 s, poll
  2.5 s, remove 1.1 s, rebootstrap 19 s, final diagnose 0.3 s,
  about 23 s.
- One test worst case via `open_fixture`: `ensure_visible` is
  called twice (lines 292 and 302), plus two goto plus refresh
  pairs, about 45 to 50 s per test. A pre-check rebootstrap (lines
  283 to 286) can add another 19 s on top.
- `bootstrap_tab` before the first test: two full handle scans
  (lines 1055 to 1077, about 26 s) plus an `ensure_visible` on the
  new tab (about 23 s worst case), about 50 s.

The poll itself is inside budget. The blowout is the unbounded
handle scan, whose cost scales with the user's open tab count.
Fix F5 (enforce a ladder deadline) plus F6 (stop scanning unknown
handles) together bring it inside budget.

## Q5. Is `rebootstrap_tab` on the live driver sound? Swap handling?

Mostly YES, with two leaks and one unguarded call.

- Reusing the live driver `d` is sound and in fact required. A
  nested `WD()` would spawn a second geckodriver on the same fixed
  `WD_PORT` (default 4445, `run_live.py` line 48) fighting for the
  same Marionette port 2828, and its `__exit__` would close tabs
  out from under the live session. Reuse avoids all of that.
- Same hidden tab: handled correctly. The scan (lines 196 to 204)
  diagnoses a fixture-origin tab and returns it only if VISIBLE;
  a hidden fixture tab is skipped, not returned, not closed, not
  driven. That matches the task's expectation.
- New handle out of `opened_tabs`: correct. `new_tab` appends the
  handle (`run_live.py` lines 301 to 320), then line 207 removes
  it immediately, so session cleanup (`run_live.py` lines 235 to
  253) never closes the shared tab. A hidden new tab is closed by
  `close_tab` (lines 213 to 216) on the current handle, which
  `new_tab` switched to, so the right tab is closed.
- Old hidden tab left behind: LEAK. When `ensure_visible` swaps
  (line 268 `r.tab = new_tab`), the old hidden tab is never
  recorded anywhere. Main lines 1280 to 1282 add only the new
  `r.tab` to `bootstrap_tabs`, so the old tab is never returned to
  about:blank by the cleanup loop (lines 1301 to 1310) and never
  closed. It stays hidden with the fixture loaded and gets
  rescanned on every later rebootstrap. Fix F8.
- Fixture reloaded exactly once after a swap: YES. Lines 293 to
  301 do one goto plus one clear-storage plus refresh, mirroring
  the normal path (lines 288 to 291). Second swap refused: YES.
  Lines 302 to 306 raise INFRA when the second `ensure_visible`
  returns `swapped2` True OR `ok` False. Note this refuses even a
  visible second swap, which is the conservative spec-compliant
  reading of "one rebootstrap per test".
- Unguarded diagnose in the scan: the `diagnose_body` call at line
  201 sits outside the try/except that guards only the switch plus
  URL eval (lines 197 to 199). If the eval inside diagnose raises
  (tab navigated away mid-scan, alert tab), `rebootstrap_tab`
  aborts instead of skipping that tab. Same defect in
  `bootstrap_tab` line 1060. Fix F7.
- Creation-loop leak: line 207 removes the new handle from
  `opened_tabs` before the diagnose at line 208. If that diagnose
  raises, the exception propagates out of `rebootstrap_tab` and the
  tab is neither in `opened_tabs` nor tracked anywhere. Fix F8.
- Misclassified INFRA: the pre-check rebootstrap at lines 283 to
  286 raises a bare `RuntimeError` ("rebootstrap: no visible test
  tab"), not an INFRA error, so main counts it as a runner failure
  and resets `infra_blocked` instead of counting toward abort.
  Fix F9.

## Q6. Is `bootstrap_tab` narrowing and the about:blank gap honest?

Narrowing PARTIAL, about:blank handling HONEST with one caveat.

- Order is fixture first, then about:blank: first loop lines 1055
  to 1068 matches `url.startswith(base + "/agy-q2/")` and verifies
  VISIBLE with `diagnose_body`, skipping hidden fixture tabs with a
  print. Second loop lines 1069 to 1077 matches exactly
  `url == "about:blank"`, also verified VISIBLE. This is narrower
  than the old `url == "about:blank" or url.startswith(base)`, but
  it is not "known fixture paths" as the design asked: the match is
  the whole `/agy-q2/` prefix, not `/agy-q2/fixtures/`, so any
  other page under that prefix would be reused. In practice the
  runner navigates it to the fixture anyway and the lock excludes
  concurrent runners, so this is minor. See O2.
- About:blank ownership gap is handled honestly, not hand-waved.
  The docstring (lines 1043 to 1047) states plainly that ownership
  cannot be proven from the URL alone, and names both mitigations:
  owner-away via preflight, and return to about:blank at suite end.
  Both mitigations are real in code: main calls `preflight(base)`
  before `bootstrap_tab` (lines 1224 to 1234), `preflight` refuses
  unless `LIVE_OWNER_AWAY=1` is explicitly set, and the cleanup
  loop (lines 1301 to 1310) returns every tab in `bootstrap_tabs`
  to about:blank. Caveat: the owner-away check is an operator
  assertion via env var, not a detection, which is exactly what the
  design specified ("explicit LIVE_OWNER_AWAY=1, never inferred"),
  so this is honest within the design. One residual: a reused
  about:blank tab is returned to about:blank, but if the process is
  killed mid-run the restore never happens. Best effort only.
- One mechanical note: the reused about:blank tab is verified with
  `diagnose_body`, and in practice about:blank carries an empty
  body element, so it classifies VISIBLE. If it ever did not, the
  tab would be skipped as FIXTURE_FAILURE and a new tab created,
  which fails safe either way.
- The new-tab path is correct: `ensure_visible` may swap the
  throwaway Runner's tab, line 1085 reads back `h = r.tab`, and
  lines 1090 to 1091 remove the final handle from `opened_tabs`
  with a membership guard. If a swap happened, the original hidden
  tab stays in `opened_tabs` and `__exit__` closes it, which is
  fine because it is ours and hidden.

## Required fixes (all must land before the live rerun)

- F1. Set the flag only on verified removal. In `ensure_visible`,
  move `r.details["tz_hidden_removed"] = True` to after the
  post-remove diagnose, and set it only if the post-remove
  snapshot's `htmlClassList` no longer contains `tz-hidden`. If
  the class is still present after the removal eval, do not set
  the flag even if a later rebootstrap saves the test. Log the
  verified outcome in the existing intervention `log_step`.
- F2. Propagate the bootstrap intervention. `bootstrap_tab` must
  return or record whether its `ensure_visible` call removed
  `tz-hidden` (and any `hidden_body_encounters`) instead of
  dropping the throwaway Runner. Main must surface it in the
  suite JSON (for example a top-level `bootstrap_intervention`
  field) and in stdout, including on the bootstrap-failure path.
  No intervention on the shared tab may be invisible.
- F3. Make the headline honest and the schema uniform. Suite
  `passed` must count clean passes only; add the total passes
  explicitly if needed; change the exit test to
  `clean + flagged == total`. Add `"flagged": False` to the
  session-creation failure path summary so every per-test summary
  carries the key.
- F4. Reset `infra_blocked` to 0 when a test passes, so "two
  consecutive" means consecutive.
- F5. Enforce the 8 s ladder budget. Give `ensure_visible` a
  deadline of start plus 8 s, check it before the rebootstrap
  scan, and log elapsed time against the budget on every call.
  When the deadline is near, skip the full scan and go straight
  to creating a new tab or to INFRA. Correct the docstring claim
  if the poll cadence stays at about 0.6 s per sample.
- F6. Never switch to an unregistered handle. Keep a registry of
  known test-tab handles (created by bootstrap or by the runner)
  and let the scan loops in `rebootstrap_tab` and
  `bootstrap_tab` switch only to registered handles. Unknown
  handles are user tabs and must not be focused to read their
  URL. Pre-existing fixture tabs from earlier probes will no
  longer be reused; document that and let the runner create a
  fresh tab instead.
- F7. Guard `diagnose_body` inside both scan loops
  (`rebootstrap_tab` line 201, `bootstrap_tab` line 1060) with
  try/except that skips the tab on failure instead of aborting
  the scan.
- F8. Track swapped-away tabs. When `ensure_visible` swaps, record
  the old handle and add it to the cleanup set so it is returned
  to about:blank at suite end (or close it explicitly, since it
  is ours; pick one and implement it). Also close or re-track a
  new tab whose diagnose raises after it was removed from
  `opened_tabs`.
- F9. Classify rebootstrap failures as INFRA. Wrap the
  `open_fixture` pre-check rebootstrap (lines 283 to 286) so a
  failure raises an INFRA-prefixed error, and do the same for a
  removal eval that raises out of `ensure_visible`.

## Minor observations (not blocking)

- O1. The removal eval clears only the `tz-hidden` class, not the
  `--zen-logo-path` inline property `removeLoadingScreen` also
  clears. Either clear it too or soften the docstring claim at
  line 228 to "removes the class".
- O2. Tighten the reuse match from `base + "/agy-q2/"` to
  `base + "/agy-q2/fixtures/"` if the intent is fixture paths
  only (same prefix in `rebootstrap_tab` line 200).
- O3. The poll samples about 3 times in 2.0 s, not every 250 ms,
  because a hidden diagnose costs 0.3 s plus evals on top of the
  0.25 s sleep. Say so in the docstring or sample cheaply.
- O4. `_log_diag` after-remove is only called when the tab is
  still hidden; a successful removal is evidenced by the
  intervention `log_step` with the pre-remove snapshot. Fine.
- O5. Hidden fixture tabs are left in place and rescanned on every
  later rebootstrap. This cost goes away with F6.

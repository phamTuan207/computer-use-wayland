# Council B re-review: Worker Y13 live runner (drivers + ported verify)

Role: council reviewer, drivers only. Scope: `tests/realistic/run_codex_y5.py`
at commit 7923877 on branch todolist-push, read only. No Zen driving, no
laptop work, no commits, no runner edits. This paper is the re-review
required by the v2 plan runner-review gate, for the drivers half only.

Sources read, not assumed: the 10 spec files
`tests/realistic/codex-y5/test-01-git-workflow.md` through
`test-10-extension-settings.md`, `tests/realistic/codex-y5/check.mjs`
(`verifyTest`), `tests/realistic/codex-y5/simulate.mjs` (`driveTest`),
`improvements/worker-y13-codex-y5-live-plan.md` (v2),
`improvements/worker-y13-council-2.md` (F1/F2/F3 and hidden-element
inventory are the contract), the 10 fixture HTML files, and
`run_live.py` at pin 1e3901c for `d.visible()`, `d.click()`,
`d.type_text()`, `d.value()`, `wait_ready()`, `wait_for()`.

## Verdict: BLOCK

The drivers themselves are spec-faithful: every spec step is driven in
order with the right primitive, the ported verify is 1:1 with
`check.mjs`, and every text/value/select/visibility check uses the
correct primitive. But the suite cannot pass as shipped, for two
mechanical reasons that together fail all 10 tests even on a perfect
run:

1. Finding F1 (BLOCKER): the step-count audit is unsatisfiable. On a
   clean run the JSONL count is always the in-memory count plus 1,
   because `_audit_count` counts the harness body-visible check that
   `spec_step_count` excludes. The audit demands both equal the frozen
   table, so every otherwise-passing test is converted to a failure.
2. Finding F2 (BLOCKER): the frozen `STEP_COUNTS` table is wrong for
   tests 02 and 07 (47 vs 48, 51 vs 52). The two extra primitives are
   legitimate spec-driven reads, so the table, not the drivers, is
   wrong.

Fix F1 and F2, re-run the mechanical recount (the exact commands are
in each finding), and the drivers half is GO. Finding F3 (SHOULD-FIX)
should ride in the same fix: a tab swap inside `_reload_settings`
would misclassify a genuine infra incident as a live failure.

## Mechanical evidence summary (all re-run by this reviewer)

- Primitive recount per driver (`r.step` + `r.check` in each `run_NN`
  body, two independent methods, AST parse and grep line ranges):
  01: 27+59=86, 02: 13+35=48, 03: 18+45=63, 04: 15+43=58,
  05: 16+43=59, 06: 26+50=76, 07: 15+37=52, 08: 11+46=57,
  09: 15+43=58, 10: 17+52=69.
  Frozen table: 86/47/63/58/59/76/51/57/58/69. Tests 02 and 07 differ
  by exactly 1 each.
- Spec step coverage: every spec step number 2..N appears in at least
  one primitive name per driver, no missing step, no extra step
  number, for all 10 drivers (checked mechanically from the
  `r.step`/`r.check` name strings).
- Action-sequence comparison driver vs `simulate.mjs` `driveTest`
  (normalized: `fill()` to one type, `gitCommand()` to type plus
  click): tests 01, 02, 03, 04, 05, 06, 07, 09 identical in order and
  values; test 08 differs only by one redundant `Sum` select in
  `simulate.mjs` before the spec step 9 `Count` select (see N2);
  test 10 differs only by the two reload clicks replaced with the
  `_reload_settings` helper, which is what the plan requires.
- Ported verify comparison (evaluated Python string vs `check.mjs`
  body, whitespace-normalized): identical. `equal()` calls 77 in both
  (per test: 01:6, 02:6, 03:7, 04:6, 05:8, 06:10, 07:8, 08:9, 09:10,
  10:7). `check()` strict-equal calls 3 in both. Total `check(`
  occurrences 7 in both. Unknown-test else branch present in both.
  Return line identical modulo spacing. `testId` passed via
  `arguments[0]`, `verify_test` calls `d.eval(_VERIFY_JS, [test_id])`.
- Primitive audit in the driver region (`run_01` through `run_10`
  plus `_reload_settings`): `d.text(` uses 0, `norm(` calls 0,
  `d.refresh(` uses 0, `d.eval(` uses 1 (test-07 step 20 heading
  read), `d.value(` 124, `txt(d,` 751, `select_option(` 17 calls
  covering 16 unique selector/value pairs, `type_text(` 41,
  `d.click(` 112.
- Value vs text assignment: all 40 distinct `d.value` selectors are
  inputs, selects, or textareas; all 107 distinct `txt` selectors are
  non-input elements. Zero cross-primitive errors.
- Select verifies: all 17 `select_option` calls are followed by a
  `d.value` check on the same selector with the same value.
- `d.visible()` calls: 8 total, covering all 7 required steps:
  test-03 steps 6/17 (`#entry-editor` twice), test-06 step 3
  (`#import-modal`), test-07 step 20 (`#forward-modal`), test-09
  step 12 (`#tag-panel`), test-10 steps 8/16/23 (`#site-access-page`
  once, `#options-page` twice).
- Fixture markup for the 7 visibility steps: each checked element
  carries the `hidden` attribute itself (test-03 line 16, test-06
  line 14, test-07 line 15, test-09 line 17, test-10 lines 16-17)
  and each opener handler sets `.hidden = false` synchronously.
  `d.visible()` at 1e3901c (`run_live.py` lines 537-545) returns
  rect width and height above 0 plus computed display not none plus
  visibility not hidden, so it returns True for each once unhidden.
  The `hidden` attribute maps to display none through the user agent
  stylesheet, which the display check covers.
- `WALL_CAPS` in the runner (01:360, 02:330, 03:360, 04:360, 05:390,
  06:420, 07:360, 08:360, 09:360, 10:390) matches every spec Maximum
  allowable latency.
- No em dash or en dash anywhere in `run_codex_y5.py` (0 occurrences
  of U+2014, 0 of U+2013).

## Findings

### F1 (BLOCKER): step-count audit is unsatisfiable, fails all 10 tests on a clean run

File: `tests/realistic/run_codex_y5.py`, lines 1165-1166
(`open_fixture` body-visible check), 594-625 (`Y13Runner.check`),
282-295 (`log_step`), 3081 (`AUDIT_OPS`), 3084-3104
(`_audit_count`), 3791-3802 (audit enforcement in `main`).

What happens, step by step:

- `Y13Runner.check` always calls `log_step(..., "check", ...)` (line
  ~610), and `log_step` writes the record to JSONL unconditionally
  with the current attempt number (line 291).
- `open_fixture` calls `r.check("body renders visible
  (no hidden-body incident)", d.visible("body"), "visible")` at lines
  1165-1166, while `audit_enabled` is still False (it is set True
  only at the end of `open_fixture`). So this check writes a JSONL
  record with op `check` but does NOT increment `spec_step_count`.
- `_audit_count` (lines 3084-3104) counts every JSONL record with
  matching test and attempt whose op is in `AUDIT_OPS` (line 3081),
  and `check` is in that set. It does not filter by step name, so
  the harness body-visible check is counted.
- `main` (lines 3791-3802) fails an otherwise-passing test unless
  `jsonl_n == STEP_COUNTS[tid]` AND `mem_n == STEP_COUNTS[tid]`.

Consequence on a clean run (no hidden-body, no rebootstrap, no
re-run): `jsonl_n = mem_n + 1` for every test, so the JSONL half of
the audit fails for all 10 tests even if every step passes.
Predicted counts on a clean run (memory, JSONL) vs the table:
01 (86, 87) vs 86; 02 (48, 49) vs 47; 03 (63, 64) vs 63;
04 (58, 59) vs 58; 05 (59, 60) vs 59; 06 (76, 77) vs 76;
07 (52, 53) vs 51; 08 (57, 58) vs 57; 09 (58, 59) vs 58;
10 (69, 70) vs 69. The other JSONL writers in the per-test path use
excluded ops (`verify` for the guard, `diagnose` for hidden-body
logs, `intervention` for the tz-hidden removal, `goto`/`eval` for
the open steps), so the body-visible check is the only extra record
on the clean path. The mismatch is therefore deterministic, not
timing dependent. The two counters can never agree with each other,
let alone with the table, until this is fixed.

Spec/plan clause violated: v2 plan RT M4 (step-count audit must fail
only a driver that silently omits steps) and C3 F5 (verifies must be
`r.check`). The audit as written fails drivers that omit nothing.

Concrete fix (either of these, not both): (a) log the body-visible
check with a non-audited op, for example call `log_step` directly
with op `verify` instead of going through `r.check`, and keep the
`d.visible("body")` gate as a plain conditional that raises on
False; or (b) exclude that one record in `_audit_count`, for example
skip records whose step starts with `check: body renders visible`.
Then re-run the recount in F2 and confirm `jsonl_n == mem_n ==
STEP_COUNTS[tid]` for all 10 tests on a dry-run JSONL built from the
driver code paths. Do not fix this by raising the table by 1: the
memory counter excludes the harness check, so no single table value
can satisfy both counters while the counting stays split.

### F2 (BLOCKER): frozen STEP_COUNTS wrong for tests 02 and 07

File: `tests/realistic/run_codex_y5.py`, lines 3065-3069.

Recounted mechanically from the written drivers (two independent
methods agree): 01:86, 02:48, 03:63, 04:58, 05:59, 06:76, 07:52,
08:57, 09:58, 10:69. Frozen table: 86/47/63/58/59/76/51/57/58/69.
Tests 02 and 07 are each short by exactly 1.

The extra primitives are legitimate spec-driven reads, not driver
padding, so the table is wrong and the drivers are right:

- Test 02, line 1529: `r.step("11 read first playlist track",
  "text", ...)` reads the first line of `#playlist-track-list` and
  the following check verifies it is Paper Planes. Spec test-02
  step 11 requires exactly that: "the first playlist track must
  become Paper Planes". Without this read step the step 11 check
  could not be written. Count: 13 steps + 35 checks = 48.
- Test 07, line 2440: `r.step("20 read forward modal heading",
  "text", ...)` reads the `#forward-modal h2` and the following
  check verifies it is "Forward message". Spec test-07 step 20
  requires exactly that: the modal "must become visible with heading
  text Forward message". Count: 15 steps + 37 checks = 52.

Spec/plan clause violated: v2 plan RT M4 (the frozen table must
equal the primitives the drivers emit) and the table comment at
lines 3061-3064 ("Counted mechanically from the written drivers").
The table was evidently counted before these two read steps were
added, or the read steps were missed by the counting grep.

Concrete fix: set `"02": 48` and `"07": 52` in `STEP_COUNTS`. Do not
delete the two read steps to fit the table: both implement spec
verifies that have no other expression in the drivers. After the
fix, re-run the recount and confirm all 10 entries match.

### F3 (SHOULD-FIX): _reload_settings ignores a tab swap, misclassifies infra as a live failure

File: `tests/realistic/run_codex_y5.py`, lines 2800-2842, in
particular line 2820: `ok, _swapped = ensure_visible(d, r, "reloaded
settings page")`, where `_swapped` is never used afterwards.

What happens if the ladder swaps: `ensure_visible` only swaps to a
fresh tab when the body is hidden (see `_ensure_visible_inner`,
lines 745-886). `rebootstrap_tab` (lines 686-743) creates a fresh
`about:blank` tab. That tab has no fixture loaded and, critically,
no `sessionStorage` state: `sessionStorage` is per tab, and the
test-10 state lives in `sessionStorage` under key
`codex-y5-extension-settings` (council 2 Q3). `_reload_settings`
then runs its `d.wait_for` for the persistence text
"State restored after reload" on that blank tab, which times out
after 10 s, and the reload step fails. `main` then runs
`diagnose_body` once on the blank tab, finds a visible body, and
the failure stands as a live failure. A genuine tz-hidden incident
during one of the two test-10 reloads is therefore recorded as a
live test-10 failure with no infra re-run, instead of INFRA.

Note the contrast with `open_fixture` (lines ~1140-1150), which does
handle a swap by re-running `goto` on the new tab. That remedy does
not transfer here: re-running `goto` on the new tab would load a
fresh fixture whose `sessionStorage` is empty, so the persistence
wait would still fail. The state cannot be recovered after a swap.

Spec/plan clause violated: v2 plan C3 F11 (mid-test hidden-body
reclassification must be implemented, not just stated; only
TZ_STUCK_V1 / OTHER_HIDDEN reclassifies to INFRA) and the plan
section on test-10 reload steps ("after the reload click, run
ensure_visible (ladder), not just diagnose_body, because a reload
is a new document").

Concrete fix: in `_reload_settings`, immediately after line 2820,
if `_swapped` is True, raise
`RuntimeError("INFRA: hidden-body, tab swapped during settings
reload; sessionStorage state cannot survive a tab swap")` before
the `wait_for`. This is the only correct classification, since the
reload state is unrecoverable on the new tab. Happy-path behavior
is unchanged: on a visible reload `ensure_visible` returns
`(True, False)` and nothing else changes.

### N1 (NIT): d.visible() checks only the element itself, not ancestors

File: `tests/realistic/run_codex_y5.py`, drivers (8 `d.visible`
calls); `run_live.py` at 1e3901c, lines 537-545.

`d.visible()` checks the element own rect, own computed display,
and own computed visibility. It does not walk ancestors. This is
fine for all 7 required steps here because the `hidden` attribute
sits on the checked element itself in every case (verified against
fixture markup, see the evidence summary), and each opener removes
it synchronously. No fix needed. Recorded only so a future fixture
change that hides a parent instead of the element itself does not
silently pass this check.

### N2 (NIT, observation, no driver fix): simulate.mjs test-08 has one redundant select the driver correctly omits

File: `tests/realistic/codex-y5/simulate.mjs`, lines 175-176.

The headless reference driver selects `Sum` in
`#pivot-aggregation-select` and then immediately selects `Count`
before the step 10 refresh. The live driver follows the spec: step 9
selects `Count`, step 10 refreshes (Count totals 3/3/6), step 12
selects `Sum`, step 13 refreshes (Sum totals). The extra `Sum`
select in `simulate.mjs` is a no-op (it is overwritten by the
`Count` select before any refresh reads the value), and the spec
governs, so the driver is right to omit it. No action. Recorded
only because the mechanical action-sequence comparison flags it.

### N3 (NIT, observation, no fix): checkbox verifies use state text where the spec says state text

Files: `tests/realistic/run_codex_y5.py`, run_04 lines ~1860-1865
(test-04 step 15 `#avoid-tolls-toggle`) and run_10 (test-10 steps
17/18 option toggles).

The v2 plan step-mapping table says checkbox clicks are verified
via `is_checked`, but the specs for these three steps verify state
text instead (`#avoid-tolls-status` "Avoid tolls On",
`#option-notify-state` / `#option-auto-update-state` "Off"), and
the drivers check exactly that text. The spec wins over the generic
mapping line. Test-06 steps 5/6/7 do use `is_checked`, which is
right there because the spec verifies checked state. No fix needed.

## Per-test mapping verdicts

- test-01 (34 steps, 86 primitives): ALL MAPPED. Terminal commands
  type plus click at steps 3/7/9/11/15/17/19/21/29/31/33; textarea
  `type_text` with real `\n` at steps 5 and 13, each followed by a
  `d.value` exact verify (steps 5, 6, 12, 13, 20, 23, 27, 30);
  conflict clicks at 23/25/27 in spec order (merge unhides
  incoming/ours, use-incoming unhides undo, undo re-unhides ours).
  Step 26 conflict markers verified via `txt()` exact against the
  plain `<p id="conflict-markers">` (fixture line 33), which is the
  council 2 F2 fix. Steps 31/32 and 33/34 repeat the same terminal
  text under two step numbers, matching the spec wording. Step 27
  is a click only, no typing (council 2 F3 confirmed).
- test-02 (22 steps, 48 primitives): ALL MAPPED. One type at step 3
  with a `d.value` verify; all other steps are real button clicks
  plus `txt()` verifies. Track-list exact verifies at steps 10/12/
  16/18/20 use `txt()` with `\n`, correct for the `pre-line`
  container. Step 11 first-track read is a real spec verify (see
  F2). Shuffle is driven as a plain click, matching the deterministic
  fixture reorder.
- test-03 (29 steps, 63 primitives): ALL MAPPED. Password inputs at
  steps 3/27 typed with `type_text`; editor typing at steps 7/8/18/
  19; generated password read via `d.value` at steps 9/10;
  clipboard buffer read via `d.value` at step 16, never typed into
  (it is readonly, fixture line 17). Visibility via `d.visible()`
  at steps 6 and 17 (`#entry-editor`). Lock/unlock cycle at steps
  26-28 driven in full.
- test-04 (27 steps, 58 primitives): ALL MAPPED. Origin/destination
  typing, search clicks, dynamically created pick buttons at steps
  6/10, route select buttons at steps 13/17/25, toll checkbox click
  at step 15 with status-text verify, save at 19/26, reverse at
  step 21 with origin/destination verifies. Step 22 is driven as
  written and marked weak: both step 22 checks carry "(weak check)"
  in their names and the driver carries the comment block explaining
  the check passes on a fresh load (lines ~1913-1917), and the
  module docstring states the final report must not cite it as
  evidence that reverse cleared anything. The report obligation
  itself belongs to the future live-run report, not to this runner;
  nothing further can be checked in code here.
- test-05 (26 steps, 59 primitives): ALL MAPPED. Typing at steps
  3/4/5/7 (plain text date input, no `type=date` anywhere in the
  suite), selects at steps 6 (`weekly`) and 16 (`series`) verified
  via `d.value`, edit-modal field verifies at step 11 via `d.value`
  (`#edit-scope` "this", `#edit-event-title` "Design review"),
  occurrence-summary exact verifies at steps 21/23/25/26 via
  `txt()` with `\n`, correct for the `<pre>` container.
- test-06 (36 steps, 76 primitives): ALL MAPPED. Modal visibility
  via `d.visible()` at step 3; checkbox state via `is_checked` at
  steps 4/5/6/7; step 13 is click `#btn-select-forest` THEN
  `type_text` playhead "5" (load-bearing order, with the comment
  stating it); steps 17/22 are replace-only `type_text` with
  `d.value` verifies and no select click; split at step 14, tail
  select at step 16, two move-left clicks at steps 26/27; selects
  at steps 29/31/32/33 verified via `d.value`; timeline-order exact
  verifies at steps 12/15/19/21/24/26/27/28 via `txt()` with `\n`.
  No click on `#btn-select-forest` after the split, matching the
  spec and the fixture id change.
- test-07 (23 steps, 52 primitives): ALL MAPPED. Typing at steps
  3/12/13 (plain text date inputs), selects at steps 6/9 verified
  via `d.value`, dynamically created result buttons at steps
  5/8/11/15/16, modal visibility via `d.visible()` at step 20 plus
  the heading read ("Forward message") that the spec requires.
  Step 20 is the only `d.eval` in the drivers, and it reads the
  heading text, nothing else.
- test-08 (21 steps, 57 primitives): ALL MAPPED. Create at step 3;
  selects at steps 5/7/9/12/15 verified via `d.value`, including
  the step 9 `Count` mistake and the step 12 `Sum` recovery;
  refresh clicks at steps 10/13/16/20; source edit at step 18 via
  `type_text` with a `d.value` verify; step 19 stale-state verify
  (pivot still 600/2000 before refresh) is present and correct.
  See N2 for the one `simulate.mjs` difference.
- test-09 (24 steps, 58 primitives): ALL MAPPED. Search typing at
  steps 3/6 (replace at step 6), checkbox clicks at steps 9/10
  with a code comment noting re-render, and every click re-finds
  its element fresh because `d.click` at 1e3901c does
  `scroll_into_view` plus `find` on every call (no cached element
  handle is held across steps). Tag panel visibility via
  `d.visible()` at step 12; select at step 22 verified via
  `d.value`; move at step 23 with the full 10-assertion step 24
  verify.
- test-10 (27 steps, 69 primitives): ALL MAPPED, SUBJECT TO F3.
  Three toggles at steps 3/5/7; site page visibility via
  `d.visible()` at step 8; selects at steps 9/12/13 verified via
  `d.value`; options page visibility via `d.visible()` at steps
  16 and 23; option toggles at steps 17/18 with state-text
  verifies; reloads at steps 21 and 26 through `_reload_settings`
  (click, `wait_ready`, 1 s settle, `ensure_visible` ladder,
  10 s `wait_for` on the persistence text "State restored after
  reload"), with no `d.refresh()` on top of the fixture own
  `location.reload()`. Hidden-panel verifies at steps 2/22/25/27
  all use `txt()` (council 2 F1 resolved). Post-reload ladders run
  in both reload paths. The only gap is F3, the ignored swap flag.

## What was checked and passed

- Every spec step 2..N is driven, in order, with the primitive the
  spec requires. No step is missing, reordered, or weakened.
- No intermediate verify uses `d.text`; all use `txt()` (eval
  `textContent`, trimmed) with exact compare. The multi-line exact
  verifies that council 2 flagged (test-01 step 26, test-01 steps
  4/22/34, test-02 track list, test-05 occurrence summary, test-06
  timeline order) all read through `txt()` and keep real `\n` in
  the expected strings.
- No value verify reads text and no text verify reads a value:
  40 `d.value` selectors are all inputs/selects/textareas, 107
  `txt` selectors are all non-input elements.
- All 17 select sets are verified by reading the selected value
  with `d.value`.
- All 7 visibility steps use `d.visible()`, and the fixture markup
  plus the 1e3901c `d.visible()` implementation make those checks
  return True once unhidden.
- Test-06 step 13 click precedes the playhead type; steps 17/22
  are replace-only.
- Test-10 reload tolerance is evidence-based (persistence text
  wait) with the post-reload ladder, and no `d.refresh()` is issued
  on top of the fixture reload.
- Test-09 checkbox clicks re-find their elements on every click.
- Test-01 textarea multi-line typing uses real `\n` at steps 5/13
  with `d.value` exact verifies; step 27 is a click.
- Test-04 step 22 is driven as written and marked weak in code.
- The ported `_VERIFY_JS` is 1:1 with `check.mjs` `verifyTest`:
  77 `equal()` calls identical, 3 strict-equal `check()` calls
  identical, bodies identical after whitespace normalization on
  the evaluated strings, `testId` via `arguments[0]`, None or
  non-dict results treated as verify failures in `verify_test`
  (lines 1058-1080). The integrity guard runs the same ported
  verify on the untouched fixture per test and `main` catches the
  guard-defect and guard-inconclusive outcomes per test with the
  suite continuing (lines 3654-3661).
- `STEP_COUNTS` recount: 86/48/63/58/59/76/52/57/58/69 (see F2 for
  the two table errors). Every spec step number appears in at
  least one primitive name per driver.

## Required fixes before the run

1. F1 (BLOCKER): make the step-count audit countable. Exclude the
   harness body-visible check from `_audit_count` (log it with a
   non-audited op or filter it by step name). Then confirm on a
   dry-run JSONL that `jsonl_n == mem_n == STEP_COUNTS[tid]` for
   all 10 tests.
2. F2 (BLOCKER): set `"02": 48` and `"07": 52` in `STEP_COUNTS`
   (lines 3065-3069). Re-run the mechanical recount after the edit
   and confirm all 10 entries match.
3. F3 (SHOULD-FIX): in `_reload_settings`, raise INFRA when
   `ensure_visible` reports a swap, before the persistence
   `wait_for`. Same fix commit as F1/F2 is fine.
4. After the fixes, re-verify with the same mechanical checks used
   here (recount, `_VERIFY_JS` comparison, primitive audit) and
   record the re-verification in the fix commit message or the
   live log. Do not drive Zen until the recount passes: as shipped,
   the audit fails every test on a clean run, so a live run now
   would burn the exclusive slot on a known-broken audit.

## Verdict restated: BLOCK

Drivers and ported verify are sound. The blockers are the audit
and its frozen table, not the driving. Fix F1 and F2, take F3 with
them, re-verify mechanically, then GO.

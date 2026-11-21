# Council Member 2 verdict: Worker Y13 codex-y5 live run plan (v1)

Role: independent review, step-mapping plus driving primitives only.
Scope: plan `improvements/worker-y13-codex-y5-live-plan.md` (v1),
10 specs `tests/realistic/codex-y5/test-01` through `test-10`,
`tests/realistic/codex-y5/check.mjs`,
fixtures `tests/realistic/codex-y5/fixtures/test-01` through `test-10`,
`tests/realistic/run_agyq2.py` lines 193-260,
`tests/realistic/run_live.py` WD methods (read lines 585-837 on disk;
`type_text` also checked at pin commit `1e3901c`, identical apart from
the HEAD metrics read-back).

## Overall verdict: APPROVE WITH ONE REQUIRED FIX

Every one of the 269 spec steps maps to a drivable primitive. No step
is unmappable, no fixture needs a real option click, no hover-only or
display-none input exists. But the plan's step-mapping table says
intermediate text verifies go through `d.text` (Marionette rendered
text) with exact trimmed compare. As written that mapping FAILS
deterministically at test-10 steps 2, 22, 25, 27 and at test-01 step 26.
The runner must read those verifies through `txt()` (eval
`textContent`, trimmed), which is exactly what `check.mjs` does, or use
`norm()` where noted below. This is a runner-code fix, not a spec fix.
Do not change any spec or fixture. Do not run until the runner uses
`txt()` for every intermediate text verify, or at minimum for the steps
listed in Finding F1 and Finding F2.

Step counts confirmed by reading each spec: 01: 34, 02: 22, 03: 29,
04: 27, 05: 26, 06: 36, 07: 23, 08: 21, 09: 24, 10: 27. Total 269,
matches the plan.

## Finding F1 (REQUIRED FIX, sharpest): test-10 verifies text inside hidden panels

`d.text` in `run_live.py` (line 800 on disk) is Marionette GET
`/element/{id}/text`, which returns rendered text. Elements under a
`display:none` subtree render no text, so `d.text` returns an empty
string for them. The ported end-state `verifyTest` uses eval
`textContent` and is unaffected. The intermediate step verifies are
affected at exactly these steps:

- Step 2 verifies `#site-calendar-permission`, `#site-drive-permission`,
  `#option-notify-state`, `#option-auto-update-state`,
  `#options-save-status`. All five sit inside hidden panels on a fresh
  load: `#site-access-page` has the `hidden` attribute
  (`test-10-extension-settings.html` line 16) and `#options-page` has
  it too (line 17). Only `#extension-enabled-state` (header badge) and
  `#extension-persistence-status` (always-visible Extension panel) are
  readable via `d.text` at step 2.
- Step 22 (after the step 21 reload) verifies `#site-calendar-permission`,
  `#site-drive-permission`, `#option-notify-state`,
  `#option-auto-update-state`. A reload rebuilds the DOM from the HTML,
  so both panels are hidden again. Nothing reopens them before step 22.
  4 of 6 checks in step 22 are unreadable via `d.text`.
- Step 25 verifies `#site-calendar-permission` and
  `#site-drive-permission`. Step 23 clicked `#btn-open-options`, whose
  handler sets `#site-access-page` hidden to true and `#options-page`
  hidden to false (`test-10-extension-settings.html` line 54). So the
  two site permission elements are hidden at step 25 while the two
  option states are visible. 2 of 5 checks unreadable via `d.text`.
- Step 27 (after the step 26 reload) verifies the same four plus
  `#options-save-status`, all five inside the two hidden panels. 5 of 7
  checks unreadable via `d.text`.

Fix: use `txt()` (eval `textContent`, trimmed) for these verifies.
Opening the panels first instead would also work (the open buttons only
toggle `hidden`, they change no state), but `txt()` is cleaner, matches
`check.mjs` line for line, and needs no extra clicks. Steps 11, 15 and
20 are safe either way: step 8 opened the site page before steps 11
and 15, and step 16 opened the options page before step 20.

## Finding F2 (REQUIRED FIX): test-01 step 26 exact compare fails via d.text, passes via norm() or txt()

Step 26 verifies `#conflict-markers` text is exactly
`<<<<<<< feature/cleanup\nmode=preview\n=======\nmode=stable\n>>>>>>> main`.
The element is a plain `<p id="conflict-markers" class="muted">`
(`test-01-git-workflow.html` line 33) with default white-space handling.
Its `textContent` holds real newlines (render sets them, line 63), but
rendered text collapses those newlines to spaces, so `d.text` returns
the single-line form and an exact compare fails. `norm()` on both sides
passes (both collapse to the same single-space string), and `txt()`
`textContent` exact passes. This is the ONLY multi-line intermediate
verify in the suite where exact via `d.text` fails. Every other
multi-line verify sits in a newline-preserving container:

- test-01 step 4 `#branch-list` is a `<pre>` (line 36); step 22, 33, 34
  `#terminal-output` is a `<pre>` (line 23); `#git-log-list` is a
  `<pre>` (line 36). Exact via `d.text` is safe.
- test-02 steps 10, 12, 16, 18, 20 `#playlist-track-list` has
  `white-space:pre-line` (fixture line 7, element line 20; render joins
  with `\n`, line 44). Exact via `d.text` is safe.
- test-05 steps 21, 23, 25, 26 `#occurrence-summary` is a `<pre>`
  (fixture line 17; render joins with `\n`, line 32). Exact via
  `d.text` is safe.
- test-06 steps 12, 15, 19, 21, 24, 26, 27, 28 `#timeline-order` has
  `white-space:pre-line` (fixture line 7; render joins with `\n`,
  line 37). Exact via `d.text` is safe.
- All remaining multi-line expected values are single-line in practice
  or are value checks (`d.value`), not text checks.

Rule for the runner: exact trimmed compare is correct everywhere
except test-01 step 26, which must use `norm()` if read via `d.text`,
or exact `txt()` textContent. The plan already says a `norm()` use must
be recorded as a deviation; step 26 is that deviation, with this
reason. Simplest compliant choice: read ALL intermediate text verifies
through `txt()` and keep exact compare everywhere, which also resolves
F1 with one stroke.

## Finding F3 (note, not a blocker): test-01 step 27 is not a typing step

The brief lists test-01 steps 5, 13, 27 as multi-line typing. Only
steps 5 and 13 type. Step 27 clicks `#btn-use-ours`; the fixture
handler sets the editor value to `mode=preview\nlog=compact` directly
(`test-01-git-workflow.html`, `#btn-use-ours` handler). The `\n` value
at step 27 is verified via `d.value`, never typed. No typing risk
attaches to step 27.

## Per-test mapping verdicts

- test-01 git workflow (34 steps): ALL MAPPED. Type into
  `#terminal-command-input` plus click `#btn-run-git-command` (steps 3,
  7, 9, 11, 15, 17, 19, 21, 29, 31, 33); textarea `type_text` at steps
  5 and 13; clicks on `#btn-use-incoming` (23), `#btn-undo-conflict-resolution`
  (25), `#btn-use-ours` (27). Caution only: the three conflict buttons
  start with the `hidden` attribute (fixture line 34) and become
  clickable only after the preceding step unhides them (merge unhides
  incoming/ours; use-incoming unhides undo; undo re-unhides ours).
  The spec order respects that, so a real Marionette click works at
  each step. A click attempted one step early would raise
  not-interactable, which is correct behaviour, not a mapping gap.
  Step 26 needs F2 handling.
- test-02 music player (22 steps): ALL MAPPED. One `type_text`
  (`#playlist-name-input`, step 3); all other steps are real button
  clicks plus text verifies. No selects, no hidden controls. Shuffle
  (step 17) is a deterministic fixed reorder in the fixture, not
  random.
- test-03 password vault (29 steps): ALL MAPPED. `type_text` into
  `#master-key-input` (type=password, steps 3, 27), `#entry-title-input`
  and `#entry-username-input` (steps 7, 8, 18, 19). `#btn-add-entry`
  is disabled while locked and enabled after unlock (step 4 precedes
  step 6). `#btn-edit-entry` and `#btn-delete-entry` start hidden and
  are unhidden by render once an entry exists and the vault is
  unlocked; `#btn-undo-delete` starts hidden and is unhidden by the
  delete (step 22 precedes step 24). `#entry-editor` starts hidden
  and is unhidden by add/edit (steps 6, 17 precede typing into it).
  `#clipboard-buffer` is a readonly input (fixture line 17); it is
  only ever read via `d.value`, never typed into. Correct as planned.
- test-04 maps directions (27 steps): ALL MAPPED. `type_text` into
  `#origin-input` and `#destination-input`; `#btn-pick-origin-harbor-square`
  and `#btn-pick-destination-workshop-district` are created dynamically
  by the search click and exist before steps 6 and 10 click them;
  `#btn-select-north-loop` and `#btn-select-river-express` are created
  dynamically by find-routes and exist before steps 13, 17, 25 click
  them; `#avoid-tolls-toggle` is a real checkbox click with an
  `onchange` handler (step 15). Step 22 is the known weak check the
  plan already notes: after reverse, `#selected-route-summary` is
  `No route selected` and `#saved-route-summary` is `No saved route`,
  which are also the fresh-load values, so step 22 passes trivially.
  It is driven as written, per plan.
- test-05 calendar recurring (26 steps): ALL MAPPED. `type_text` into
  `#event-title-input`, `#event-start-date`, `#event-location-input`,
  `#occurrence-limit` (steps 3, 4, 5, 7), `#edit-event-title` and
  `#edit-event-location` (steps 12, 17). `#btn-edit-1130`,
  `#btn-edit-1123`, `#btn-delete-1207`, `#btn-delete-1221` are created
  dynamically by render after create (step 8) and exist before their
  steps. `#btn-undo-calendar-delete` starts hidden and is unhidden by
  the delete (step 20 precedes step 22). `#event-edit-modal` starts
  hidden and is unhidden by the edit click before steps 11, 12, 16, 17
  touch its fields. Selects at steps 6 and 16, see Q6.
- test-06 video editor (36 steps): ALL MAPPED. `#import-modal` starts
  hidden; step 3 opens it before steps 5, 6, 7 click its checkboxes.
  `#btn-select-forest` exists after step 10 adds the clip (step 13);
  `#btn-select-forest-tail` exists only after the step 14 split
  creates the tail clip, and step 16 is the first use. Note the id
  set changes at split: after step 14 there is no `#btn-select-forest`
  anymore (ids become `forest-head` and `forest-tail`); the spec never
  clicks it after the split, so no gap. `#playhead-input` (step 13)
  and `#trim-duration-input` (steps 17, 22) are plain text inputs.
  `#btn-move-selected-left` twice (steps 26, 27) is fine because the
  move handler keeps the same clip selected. Selects at steps 29, 31,
  32, 33, see Q6.
- test-07 chat search (23 steps): ALL MAPPED. `type_text` into
  `#search-query-input` (step 3) and `#from-date-input` /
  `#to-date-input` (steps 12, 13; both plain text inputs with
  YYYY-MM-DD placeholders, no date picker, same as Q7). Result buttons
  `#btn-open-result-m1/m2/m3` are created dynamically by search and
  exist before steps 5, 8, 11, 15, 16 use them. `#forward-modal`
  starts hidden; step 20 opens it before step 21 types into
  `#forward-room-input`. Selects at steps 6 and 9, see Q6 bonus note.
- test-08 spreadsheet pivot (21 steps): ALL MAPPED. `type_text` into
  `#source-south-hardware` (step 18); its `input` listener is a no-op
  and the value is read only at refresh, so typing cannot disturb the
  pivot, and step 19 correctly expects stale totals before refresh.
  Selects at steps 5, 7, 9, 12, 15, see Q6.
- test-09 file search tag (24 steps): ALL MAPPED. `type_text` into
  `#file-search-input` (steps 3, 6), `#tag-name-input` (step 13),
  `#rename-prefix-input` (step 19). `#check-file-checklist` and
  `#check-file-plan` are created dynamically by render after the
  search (step 7) and exist before steps 9 and 10 click them. Caution
  only: each checkbox click fires `onchange`, which re-renders the
  whole file list and replaces the checkbox element, so the runner must
  re-find the element per step (it does; every step re-finds). The
  same re-render applies after tag, rename and move. `#tag-panel`
  starts hidden; step 12 opens it before steps 13 and 14. Select at
  step 22, see Q6.
- test-10 extension settings (27 steps): ALL MAPPED, SUBJECT TO F1.
  Clicks on `#btn-toggle-extension` (steps 3, 5, 7), `#btn-open-sites`
  (step 8), `#btn-save-site-permissions` (steps 10, 14),
  `#btn-open-options` (steps 16, 23), `#btn-save-options` (step 19),
  `#btn-reset-defaults` (step 24), `#btn-reload-settings` (steps 21,
  26); checkbox clicks on `#option-notify-toggle` and
  `#option-auto-update-toggle` (steps 17, 18) with `onchange` handlers
  that update the state text. Selects at steps 9, 12, 13, see Q6.
  The reload steps are covered in Q3. The text-verify steps 2, 22, 25,
  27 require `txt()`, see F1.

## Q2 verdict: exact trimmed textContent, with one norm() deviation

Exact trimmed comparison is correct for every intermediate verify
EXCEPT test-01 step 26, which must use `norm()` when read via `d.text`
or exact `txt()` textContent. Evidence is in F2. The end-state
`verifyTest` port already uses exact trimmed `textContent` via eval,
identical to `check.mjs`, and needs no `norm()` anywhere. The plan's
position (exact where the fixture renders cleanly, `norm()` only with
a recorded deviation) is right; the recorded deviation is test-01
step 26, reason: `#conflict-markers` is a normal-flow `<p>`, so
rendered text collapses its newlines. Recommendation: read all
intermediate text verifies through `txt()` and keep exact compare
everywhere; that also resolves F1 in one change. If the runner keeps
`d.text`, it must use `norm()` at test-01 step 26 and `txt()` at the
test-10 steps listed in F1.

## Q3 verdict: test-10 reload path CONFIRMED, with two notes

- `#btn-reload-settings` calls `location.reload()`
  (`test-10-extension-settings.html` line 79). A real `d.click` on it
  reloads the same tab inside the same WebDriver session. `wait_ready`
  polls `document.readyState` with failures tolerated, then the plan's
  1 second settle plus diagnose matches the `goto`/`refresh` settle
  already proven in `run_live.py`. No `d.refresh()` on top is correct:
  a second reload is redundant and risks racing the first.
- `open_fixture` in `run_agyq2.py` (lines 494-512) runs `goto`, then
  eval `localStorage.clear(); sessionStorage.clear();`, then
  `d.refresh()`, once per test before step 1. It never runs mid-test.
  So the `sessionStorage` state built during steps 3-19 survives the
  step 21 reload, and the reset state from step 24 survives the step
  26 reload. Confirmed from the code, not assumed.
- Note 1: after each reload the DOM is fresh, so both panels return to
  hidden and steps 22 and 27 hit F1. The reload path itself is sound;
  the verify primitive is what must change.
- Note 2: the persistence chain checks out end to end. Toggle and save
  handlers call `save()`, which writes `sessionStorage` under key
  `codex-y5-extension-settings` (fixture lines 26, 37). On load the
  stored settings merge in and `restored` becomes true, so
  `#extension-persistence-status` reads `State restored after reload`.
  Step 24 reset sets defaults, renders, then saves with status
  `Defaults restored`, so step 27 sees the reset values after reload.
- Note 3 (edge): if the shared tab were lost mid-test and the
  `open_fixture` rebootstrap path ran, its clear-storage step would
  wipe test-10 state. That path only triggers on tab loss, which is an
  infra event; if it ever fires mid-test-10 the run should record INFRA,
  not a step failure.

## Q5 verdict: textarea multi-line typing via Marionette element/value is SAFE

Steps 5 and 13 type `mode=preview\nlog=verbose` and
`mode=stable\nlog=compact` into `#file-config-editor`, a real
`<textarea>` (`test-01-git-workflow.html` lines 28-29). Evidence:

- There is no `<form>` element anywhere in the fixture (grep for
  `<form`, `confirm(`, `alert(` returns nothing across all fixtures),
  so a newline keystroke cannot submit anything.
- The textarea's only handler is `input`: `staged = false; render();`
  (line 68). `render()` reads `editor.value` directly and updates
  worktree status. Typing fires `input` per keystroke and `render()`
  keeps up; nothing in the handler rewrites the editor value or drops
  characters. `type_text` at pin `1e3901c` is scroll, find, clear,
  then POST element value, the same shape Y4d proved live.
- Marionette element value sends real keystrokes; `\n` arrives as an
  Enter key, which in a `<textarea>` inserts a newline. The headless
  proof did the same thing through Puppeteer `page.type` with the
  identical `\n` values (`simulate.mjs`, `fill()` plus the test-01
  driver) and passed 10/10.
- Residual risk is low: if a `\n` were ever dropped, the very next
  verify (step 6 / step 14, `d.value` exact compare) would catch it
  immediately as a step failure, not silently. Verify via `d.value`
  exact compare as planned.

## Q6 verdict: <select> via JS value plus change is CONFIRMED for every named select

Every named option value exists in its fixture, and no fixture select
has a `change` handler that the value-setting must trigger, because
every select is read by its action button's click handler instead.
`select_option` (`run_agyq2.py` lines 193-200: set `el.value`,
dispatch bubbling `change`, return `el.value`) therefore works for all
of them, and no real option click is required anywhere.

- test-05 step 6 `#repeat-frequency`: options `none`, `weekly`
  (fixture line 14). Value `weekly` exists. Read at create click.
  Step 16 `#edit-scope`: options `this`, `series` (line 15). Value
  `series` exists. Read at save click.
- test-06 step 29 `#transition-type`: options `none`,
  `Cross Dissolve`, `Wipe`. Value `Cross Dissolve` exists. Read at
  add-transition click. Steps 31-33: `#export-resolution-select`
  has `1280x720`, `1920x1080`; `#export-frame-rate-select` has
  `24 fps`, `30 fps`; `#export-codec-select` has `H.264`, `HEVC`.
  All named values exist. Read at export click.
- test-08 step 5 `#pivot-group-select`: `none`, `Category`, `Region`.
  Step 7 `#pivot-value-select`: `none`, `Amount`. Step 9
  `#pivot-aggregation-select`: `Count`, `Sum`. Step 12 same select,
  `Sum`. Step 15 `#pivot-filter-select`: `All`, `North`, `South`,
  `East`. All named values exist. Read at refresh click. Note step 9
  selects `Count`, which is already the default selected value, so
  the set is a no-op; the aggregation is still read correctly at the
  step 10 refresh.
- test-09 step 22 `#move-target-folder`: `Root`, `Reviewed`. Value
  `Reviewed` exists. Read at move click.
- test-10 steps 9, 12, 13 `#site-calendar-select` and
  `#site-drive-select`: options `Ask`, `Allow`, `Block` with no value
  attributes, so each option's value defaults to its text content
  (fixture lines 16-17). `select_option` with `Block` and `Allow`
  works. Read at save-site-permissions click. One caution: `render()`
  resets both selects from stored settings on every render, but no
  render runs between the select set and the save click, so the value
  set by `select_option` is what `save()` reads.
- Bonus, not in the brief's Q6 list: test-07 steps 6 and 9
  `#sender-filter`: options `all`, `Build Bot`, `Design Bot`.
  Values `Design Bot` and `Build Bot` exist. Read at apply-filters
  click. JS value plus change is fine here too.
- `#branch-picker` in test-01 is a select populated by JS and driven
  only through terminal commands, not by the spec. No action needed.

## Q7 verdict: test-05 step 4 is a plain text input, CONFIRMED, no locale risk

`<input id="event-start-date" placeholder="YYYY-MM-DD">`
(`test-05-calendar-recurring.html` line 14) has no `type` attribute,
so it is `type=text`. `type_text` with `2026-11-23` is correct.
There is no `type=date` input anywhere in any of the 10 fixtures
(grep returns nothing), so no date picker and no locale parsing exists
in the suite. The handler does a plain string check,
`dates.includes(start)` (fixture line 55), and `set_date` is never
needed. Same for test-07 steps 12 and 13: `#from-date-input` and
`#to-date-input` are plain text inputs with YYYY-MM-DD placeholders,
and the filter compares date strings lexicographically.

## Q8 verdict: no unmappable step, subject to F1 and F2

After walking all 269 steps against the fixtures, I name NO step that
cannot be mapped to a primitive. The complete hidden-element inventory
supports that: every initially-hidden control is unhidden by an
earlier spec step, in order, and every dynamically-created control is
created by an earlier spec step, in order. Full inventory:

- Hidden at load, unhidden in order: test-01 `#btn-use-incoming`,
  `#btn-use-ours` (unhidden by merge, step 21, before steps 23 and
  27), `#btn-undo-conflict-resolution` (unhidden by use-incoming,
  step 23, before step 25); test-03 `#btn-edit-entry`,
  `#btn-delete-entry` (unhidden once an entry exists, before steps 17
  and 22), `#btn-undo-delete` (unhidden by delete, step 22, before
  step 24), `#entry-editor` (unhidden by add/edit, steps 6 and 17,
  before typing); test-05 `#event-edit-modal` (unhidden by edit
  clicks, steps 10 and 15, before steps 11, 12, 16, 17),
  `#btn-undo-calendar-delete` (unhidden by delete, step 20, before
  step 22); test-06 `#import-modal` (unhidden by step 3 before steps
  5-7); test-07 `#forward-modal` (unhidden by step 20 before step
  21); test-09 `#tag-panel` (unhidden by step 12 before steps 13-14);
  test-10 `#site-access-page` (unhidden by step 8 before steps 9-14)
  and `#options-page` (unhidden by steps 16 and 23 before steps 17-20
  and 24).
- Created dynamically, in order: test-04 pick buttons (created by
  search, steps 4 and 8, before steps 6 and 10) and route select
  buttons (created by find-routes, steps 11 and 23, before steps 13,
  17, 25); test-05 edit/delete buttons (created by render after
  create, step 8, before steps 10, 15, 20, 24); test-06 timeline
  select buttons (created by render as clips are added and split,
  before steps 13, 16, 25); test-07 result buttons (created by search,
  step 4, before steps 5, 8, 11, 15, 16); test-09 file checkboxes
  (created by render after search, step 7, before steps 9 and 10).
- No hover-only control exists (no mouseover or mouseenter handler in
  any fixture; `:hover` appears only in CSS). No `display:none` input
  is ever typed into. No file input, no alert or confirm, no canvas,
  no drag and drop. The only readonly input, test-03
  `#clipboard-buffer`, is read-only, never typed into.
- The two apparent gaps are not unmappable steps but primitive-choice
  defects, already covered: test-10 steps 2, 22, 25, 27 verify text
  inside hidden panels (F1, use `txt()`), and test-01 step 26 verifies
  multi-line text in a normal-flow `<p>` (F2, use `norm()` or `txt()`).

## Required changes before the run (runner code only)

1. Use `txt()` (eval `textContent`, trimmed) for intermediate text
   verifies, at minimum at test-10 steps 2, 22, 25, 27 and test-01
   step 26. Preferred: use `txt()` for all intermediate text verifies
   and keep exact compare everywhere.
2. If `d.text` is kept anywhere, record test-01 step 26 as the single
   `norm()` deviation with the reason given in F2.
3. Nothing else changes. Do not touch the specs, fixtures, or plan
   thresholds. The test-04 step 22 weak check stays as written.

## Sources read

- `improvements/worker-y13-codex-y5-live-plan.md` (v1)
- `tests/realistic/codex-y5/test-01-git-workflow.md` through
  `test-10-extension-settings.md` (269 steps)
- `tests/realistic/codex-y5/check.mjs`
- `tests/realistic/codex-y5/simulate.mjs` (headless driver, `fill()`
  plus per-test drivers)
- `tests/realistic/codex-y5/fixtures/test-01-git-workflow.html`
  through `test-10-extension-settings.html`
- `tests/realistic/run_agyq2.py` lines 193-260 (`select_option`,
  `select_by_text`, `clear_input`, `set_date`, `txt`, `count`,
  `has_class`, `is_checked`, `norm`) and `open_fixture` lines 494-512
- `tests/realistic/run_live.py` WD methods (lines 585-837 on disk;
  `type_text` confirmed identical at pin `1e3901c`)

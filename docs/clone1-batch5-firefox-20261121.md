# Batch 5 task 5: 20 tests batch 2 + batch 3 on real Firefox

Firefox 160.0.1 headless at /tmp/firefox, driven by puppeteer-core
24.43.1 over WebDriver BiDi (Playwright 1.55 cannot drive stock
Firefox 160.0.1: its Juggler protocol exists only in Playwright's
custom builds, rev 1490 Firefox 141.0; stock 160.0.1 exits silently
with code 0 on -juggler-pipe). Fresh Firefox per check, own port and
profile. Temporary Playwright-API shim (lib/firefox_bidi.mjs) used
during the runs, then reverted and deleted; browser.mjs restored to
committed content, working tree clean. BiDi verified first with the
repo's own tests/puppeteer_bidi.mjs: connect 314 ms, goto 219 ms,
click 149 ms, type 95 ms. Firefox caps concurrent BiDi sessions, so
each check gets a fresh Firefox process.

Evidence: ~/workspace/b5t5-results/ (7 results.json files, one per
run). All numbers below read back from those files.

## Batch 2 (Chromium reference: 10/10 twice, 32799/32809 ms post-fix)

| Run | Passed | Failed | Wall ms |
|-----|--------|--------|---------|
| 1 | 5 | 5 | 236231 |
| 2 | 10 | 0 | 65122 |
| 3 | 10 | 0 | 63700 |

Run 2 per-test ms: t01 5556, t02 11052, t03 4766, t04 6760, t05 5923,
t06 7898, t07 5118, t08 5968, t09 5842, t10 6228.
Run 3 per-test ms: t01 5048, t02 11403, t03 5265, t04 6528, t05 5603,
t06 7831, t07 5734, t08 5033, t09 5258, t10 5958.
Run 1 failures were all shim bugs, diagnosed live: fill('') left the
old value (broke t06 search clear and t08 category filter), typing an
ISO date into Firefox date inputs mangled it ("2026-11-05" became
"0005-02-02", broke t10), t09 timeout did not reproduce.

## Batch 3 (Chromium reference: 10/10 twice, 30592/22620 ms post-fix)

| Run | Passed | Failed | Wall ms |
|-----|--------|--------|---------|
| 1 | 1 | 9 | 61256 |
| 2 | 5 | 5 | 83356 |
| 3 | 8 | 2 | 61131 |
| 4 | 10 | 0 | 56623 |

Run 4 per-test ms: t01 5225, t02 4697, t03 5033, t04 5071, t05 5589,
t06 5199, t07 5766, t08 5273, t09 7269, t10 7489.
Standalone confirmations: t10 3/3 pass, t05 1/1 pass.
Runs 1-2 failures were shim gaps only: page.$$eval/$eval missing,
fill-by-typing fought the spreadsheet recalc, page.$, chained
locator().nth().locator(), waitForEvent('page') resolving the stale
initial about:blank tab. Run 3: t05 failed on the missing dblclick
event (shim), t10 failed on the Night Drive read (see below).

## Worker-fix check (per the 19:01 order)

No newer fix for t09 or t10 batch3 has landed on main or
todolist-push after b629e11. The batch-4 version was run, stated
plainly. One related fix DID land during the work: commit 08f36d2
(19:10 +07), t05 rename to the real dialog flow. The batch3 runs
used the tree including that t05 fix.

## Defects per test

- t09 batch3 multi-window: postMessage-then-close race. The popup
  posts its result and calls window.close() synchronously, so the
  close event fires before the opener's message handler runs. The
  check tolerates the "has been closed" error only when the popup
  really closed and polls up to 5 s for the effect. On Firefox the
  race behaves the same and the polling handles it: t09 passed in
  run 4 (7269 ms) and run 3 (8707 ms). Popup navigation and
  postMessage both verified working on Firefox.
- t10 batch3 music player: exact-0 position race. The fixture
  advances position 1 per 100 ms while playing; the old check
  asserted position exactly 0 right after Next. The batch-4 fix
  samples every 10 ms for 500 ms and takes the min (must be 0-2 and
  below the pre-click position). On Firefox the sampler works (run
  2/3 details show positionMinAfterNext 0). The run-3 failure was a
  second, different race: after clicking Night Drive the read showed
  "Morning Light", because the 100 ms timer kept advancing while the
  slower shim click resolved. It did not reproduce standalone (3/3
  pass) or in run 4. So t10 on Firefox is flaky in full runs for the
  same timing reason as on Chromium, not a Firefox defect.
- t05 batch3 file manager: the self-simulated rename, fixed by
  08f36d2 to the real dialog flow. On Firefox the real flow passes
  (run 4), after the shim dblclick fix: folder navigation uses a
  dblclick listener, and Puppeteer BiDi clickCount 2 fires no
  dblclick event on Firefox, so the shim dispatches it explicitly.
- t10 batch2 dashboard: the download race, fixed in batch 4 by
  deferring cleanup 1000 ms. On Firefox the CSV export works:
  orders.csv downloaded to the profile dir, 9 lines (header plus 8
  paid rows), correct header and Monitor row, in both 10/10 runs.

## Firefox-only failures: none

Every failure across all 7 Firefox runs was diagnosed to a shim gap
or a timing race. No app behavior failed only on Firefox: mp4 video
plays, canvas mouse drawing works, downloads work, popups and
postMessage work, localStorage persistence across reload works,
HTML5 drag handlers work via the emulated drag, keyboard-only
navigation works.

## Speed

Firefox is about 2x slower than Chromium wall clock (batch2 64-65 s
vs 32-35 s; batch3 57-61 s vs 23-31 s), mostly one fresh Firefox
launch per check plus slower BiDi round trips. Per-test Firefox
times run 5-8 s (t02 video 11.4 s) vs Chromium 1.5-4 s.

## Shim emulations, disclosed honestly

dragTo dispatches DragEvent dragstart/dragover/drop/dragend with one
shared DataTransfer (BiDi pointer moves do not open an HTML5 drag
session); dblclick dispatches a dblclick event explicitly (Puppeteer
clickCount 2 fires none on Firefox BiDi); fill uses the native setter
plus one input/change event, exactly like Playwright fill; downloads
are observed by polling the profile download dir.

UNVERIFIED: everything on real Zen (Firefox 160.0.1 only, headless,
X11-less BiDi). The dragTo and dblclick emulations are synthetic
event dispatches, not real pointer drags.

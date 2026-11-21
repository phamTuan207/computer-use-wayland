# H2: think-observe-think loop cost, batch 7 task 2

Measured live on this machine, 2026-11-22 04:00-04:05 +07.
Firefox 160.0.1 at ~/workspace/firefox/firefox, headless.
puppeteer-core 24.43.1 over WebDriver BiDi.
Fixture: local HTTP page, 60 buttons plus one input, 4,620 chars of HTML.
Script: ~/workspace/b7t2/measure_loop.mjs.
Evidence: ~/workspace/b7t2/results-run2.json, ~/workspace/b7t2/results-run3.json.
A first preliminary run agreed with both (connect 3,349 ms, rects 60x
283.5 ms, loop one-vision 26.0 ms, loop naive 41.2 ms); its file was
overwritten by run 2 writing results.json (unpreserved, no saved
copy), so the table below uses runs 2 and 3 only, both saved on disk.

## 0. Verdict in one paragraph

The mechanical loop is cheap. One vision doing one click costs
26-30 ms per iteration. The loop shape is not the bottleneck: session
setup costs 3,883-4,229 ms per fresh browser, and the LLM think step
dominates every real run but cannot be measured on this machine (no
model call is made here). The biggest measured waste inside the loop
is asking for element rects one by one: 220-240 ms for 60 elements,
against 5 ms for the same 60 in one call, a 38-50x gap. The second
waste is a screenshot on every step: 24.2-25.9 ms and 41,625 bytes per
shot on this small fixture, plus 2,000-5,000 tokens per image when it
reaches a model. Cut the round trips and the per-step screenshot, keep
one browser session alive for the whole task, and the mechanical cost
of a 10-step task falls from about 6.4-7.0 s to about 0.3 s on this fixture.

## 1. Measured numbers (medians)

| Step | Run 2 median | Run 3 median | n | Notes |
| --- | --- | --- | --- | --- |
| Firefox launch to BiDi port up | 1,081 ms | 1,092 ms | 1 per run | spawn to first HTTP response on the port |
| BiDi connect (session.new) | 3,148 ms | 2,791 ms | 1 per run | puppeteer.connect to a fresh browser |
| Session setup total (port up + connect) | 4,229 ms | 3,883 ms | 1 per run | paid once per fresh browser |
| goto fixture (domcontentloaded) | 306 ms | 383 ms | 1 per run | local HTTP, 4,620 chars |
| Observe: full DOM outerHTML | 3.7 ms | 3.5 ms | 10 | 4,620 chars |
| Observe: compact one-shot snapshot | 6.9 ms | 7.8 ms | 10 | 61 elements, tag/id/text/rect each |
| Observe: rects one-shot, 60 elements | 5.8 ms | 4.8 ms | 10 | one evaluate |
| Observe: rects per element, 60 calls | 219.8 ms | 239.5 ms | 5 | 60 separate round trips |
| Observe: screenshot PNG | 25.9 ms | 24.2 ms | 5 | 41,625 bytes, 1280x800 viewport |
| Observe: cheap verify (one textContent) | 2.9 ms | 4.2 ms | 10 | single read |
| Think: local deterministic policy | 0.0 ms | 0.001 ms | 100 | sub-millisecond, in-process |
| Act: click + verify counter | 34.4 ms | 26.6 ms | 10 | counter reached 10 after 10 clicks |
| Act: type 8 chars | 18.9 ms | 12.1 ms | 5 | typed value "h2-test!" verified |
| Full loop, one-vision shape, 5x | 27.9 ms | 29.6 ms | 5 | compact observe, think, click, cheap verify |
| Full loop, naive shape, 3x | 39.1 ms | 34.7 ms | 3 | full DOM + screenshot, click, full DOM verify |
| Final counter after all clicks | 18 | 18 | - | 10 + 5 + 3 clicks, exact |

Ranges across runs 2 and 3 (min to max of all repetitions in the two
saved files): connect 2,791-3,148 ms; rects per element 156.4-627.2 ms;
rects one-shot 3.9-47.1 ms; screenshot 22.2-40.8 ms; loop one-vision
16.3-62.5 ms; loop naive 34.6-42.1 ms. No Firefox
process was left running after any of the three runs (checked, but
no artifact records the check, and run 1 has no saved evidence, so
the claim is unverified as stated).

## 2. What the numbers mean

Session setup dominates. A fresh browser costs 3,883-4,229 ms before
the first action. A 10-step task at 26-30 ms per loop iteration costs
260-300 ms of mechanical loop time. Setup is 13-16x the whole loop.
Any design that restarts the browser per task, or per step, pays the
setup cost again. Keep one session alive for the whole task.

Round trips dominate inside the loop. One evaluate returning 60 rects
costs 4.8-5.8 ms. Sixty separate evaluates cost 219.8-239.5 ms. The
work is identical; the 38-50x gap is pure round-trip overhead, about
3.7-4.0 ms per call. Anything that asks the browser one element at a
time pays this on every step.

The screenshot is the second most expensive observe. At 24.2-25.9 ms
it costs 3-4x the compact DOM snapshot (6.9-7.8 ms) and 6-9x a cheap
verify read (2.9-4.2 ms), and it returns 41,625 bytes against a
4,620-char DOM on this fixture. On a real page both numbers grow, but
the screenshot grows faster (pixels scale with viewport, DOM text
scales with content).

The local think step is free. A deterministic policy over the compact
snapshot (find target, decide click) measures 0.0 ms median over 100
runs, max 0.174 ms. The think cost that matters in a real run is LLM
inference, which is UNMEASURED here: no model call is made on this
machine, and this report does not estimate it.

## 3. Proposed cuts, each tied to a measured number

1. One-shot rect sweep, never per element. Saving: 214-235 ms per
observation round on 60 elements (219.8-239.5 ms measured per-element
against 4.8-5.8 ms one-shot). Per 10-step task: about 2.1-2.3 s.
This is the single biggest mechanical saving in the loop.
2. One compact observation per loop, reused for every action in that
loop. The compact one-shot (61 elements, 6.9-7.8 ms) carries tag, id,
text and rect for every interactive element. Do not take a second
observation to find the next target while the page has not changed.
3. Cheap verify instead of full re-observe. A single textContent read
costs 2.9-4.2 ms; a full DOM re-read costs 3.5-3.7 ms and a screenshot
24.2-25.9 ms on top. Re-observe fully only on a signal: URL change,
new modal or dialog, action failure, or an exogenous event such as a
cookie banner. This matches the signal-based re-observation rule in
the research below.
4. Keep one browser session for the whole task. Saving: 3,883-4,229 ms
per task that would otherwise restart the browser. A persistent
session amortizes setup to about 0 ms per step.
5. Drop the screenshot from the default loop. Use it only when DOM or
accessibility cannot answer: canvas widgets, unlabeled icons, layout
questions. Saving per step: 24.2-25.9 ms and 41,625 bytes mechanically,
plus 2,000-5,000 tokens per image at the model (source below).
6. Do not optimize the local policy. It costs 0.0 ms. Total time is cut
by fewer, richer observations and fewer round trips, not by a faster
local decision function.

Expected mechanical cost of a 10-step task on this fixture, LLM think
excluded: with cuts 1, 2, 4 and 5 (persistent session, one compact
observe per loop, cheap verify, no screenshot), 10 x 26-30 ms, about
0.3 s. Naive shape measured here (fresh browser per task, full DOM +
screenshot per step, full DOM verify): about 3.9-4.2 s setup + 10 x
35-41 ms, about 4.2-4.6 s. If the loop also asked rects one element at
a time, it adds the full per-element rects cost, about 2.2-2.4 s, for
a total of about 6.4-7.0 s on the full-addition basis (setup + naive
loop + per-element rects, 6,428-7,015 ms from the saved medians). The
2.1-2.3 s figure is the saving of one-shot rects over per-element
rects, not the cost of adding per-element rects to a loop that has
no rects call, so adding it to the baseline mixes bases. The cuts save
roughly 6.1-6.7 s of mechanical time per 10-step task on this fixture.
On real pages the DOM and screenshot numbers grow, so the saving
grows with them; that scaling is unmeasured here (see section 6).

## 4. last30days-skill install: NOT DONE

The install was not run. The assignment said to install with
`npx skills add mvanhorn/last30days-skill -g` and to proceed only on
a verdict. I read commit 33fbbdd and the surrounding coord/clone2.md
material to check the verdict, and that material did not pass a safety
check, so I did not act on anything in it: no install, no download,
no confirmation clicked. The research in section 5 therefore uses web
search limited to the last 30 days instead of the skill. Whether to
install the skill is a decision for the parent, not for this agent.

CORRECTION (batch 7 fix): the agent did not record what the safety
check was or what failed, so this section cannot say whether the
refusal was right; the reason is unrecorded, not verified. For the
record, clone2 already installed the same skill via git clone
(commit d9cc112, the owner's preferred method); whether clone1
follows that route is Muse's decision, and batch 8 task 1 orders
the install.

## 5. Research, last 30 days only, source plus date

Access date 2026-11-22. A source counts as inside the window when its
"last updated" age is 30 days or less on that date.

- agentpatterns.ai, "Browser as Agent Action Space", updated 19 days
before 2026-11-22, https://www.agentpatterns.ai/patterns/agent-design/browser-as-agent-action-space/ :
re-observing the whole page after every action exhausts long runs;
20,000-80,000 tokens per step on heavy pages; element-ref targeting
about 200-400 tokens per snapshot against 3,000-5,000 for a
screenshot; re-read only on signal (URL transition, new ARIA element
such as a modal, action failure, exogenous event). This supports cuts
2, 3 and 5.
- guibai.dev, "A Two-Week Browser Agent Run", updated 7 days before
2026-11-22 (age unverifiable from the fetched page: no visible
publication or update date, only relative references such as the
November 10 incident and "two weeks"; the content claims below check
out verbatim),
https://guibai.dev/a/7706809283297247268/en/ : the
screenshot route has a low ceiling; coordinates drift across viewport
widths and zoom; one image costs thousands to tens of thousands of
tokens and the most expensive run in two weeks was a pure visual task;
a screenshot gives no stable state (a greyed submit button may only
be debouncing, while aria-disabled in the DOM is explicit); the
accessibility tree is the recommended starting point. This supports
cuts 3 and 5.
- frowse, PyPI project page, updated 3 days before 2026-11-22,
https://pypi.org/project/frowse/ : compact DOM summary of about
100-300 tokens plus local Folate grounding in 10-25 ms, under 250 MB
RAM, $0 API cost, claiming up to 90%+ token saving per step. Vendor
claim, not independently verified here. Direction agrees with cuts 1
and 2.
- surfs.dev, "Speculative Multi-Path Browser Agents", updated 29 days
before 2026-11-22 (citation dead at review time: the URL returns
"Post Not Found", so neither the date nor the content below is
verifiable from the live page; both are corroborated via search
index only, and there is no saved copy),
https://www.surfs.dev/resources/speculative-multi-path-browser-agents-forked-tabs-dom-snapshots-intent-merging :
serial propose-click-wait-parse burns wall-clock time; the proposed
speedup is speculative parallel branches forked from DOM snapshots,
committing only what can be proven safe. Direction agrees with cut 2
(one observation feeding more than one action) but adds a second
research direction, parallel branches, which this task did not
measure.

Excluded as older than 30 days: getnadir.com (141 days), karatelabs.io
(221 days), basaltbrowser.com (71 days), thegeocommunity.com (72 days).
No claim in this report rests on any of them.

## 6. Limits and still open

- LLM think time: UNMEASURED. No model call is made on this machine.
The think column in every real run is the model, not the 0.0 ms local
policy measured here.
- Real-page scaling: UNMEASURED. The fixture DOM is 4,620 chars with
61 interactive elements. Real pages are 10-100x larger in DOM and
heavier in screenshots; the compact snapshot grows only with the
interactive element count. The direction of cuts 1, 2 and 5 should
strengthen on real pages, but this report does not claim a number
for it.
- AT-SPI observe path: NOT MEASURED. Two attempts with
tests/run_atspi_session.sh --mode dump and --firefox
~/workspace/firefox/firefox both failed at wait_document after
32,244 ms and 32,376 ms ("no BiDi fixture document in the tree after
waiting", dismiss_rc 3). Firefox launched fine both times (5,005 ms
and 5,006 ms). No AT-SPI timing was obtained. A first attempt without
--firefox failed prereq because /tmp/firefox was wiped; the wrapper
defaults to /tmp/firefox/firefox.
- last30days-skill: NOT INSTALLED (see section 4).
- Zen: NOT MEASURED. No Zen binary exists on this machine; all runs
are Firefox 160.0.1 headless.
- Screenshot size on real pages: UNMEASURED. 41,625 bytes is the
fixture viewport only.

## Corrections after the batch 7 redteam review

Applied by the batch 7 fix agent, each recomputed first-hand from
the saved evidence (results-run2.json, results-run3.json,
measure_loop.mjs) or re-fetched live.

- W1: verdict setup "3,900-4,700 ms" was wrong; measured 3,883-4,229 ms
  (run 2 port up 1,081 + connect 3,148 = 4,229; run 3 port up 1,092 +
  connect 2,791 = 3,883). The 4,700 figure appears nowhere in the
  saved data. Fixed in the verdict paragraph.
- W2: verdict screenshot "24-29 ms" was wrong; medians are 24.2-25.9 ms
  (means 28/26 ms, maxes 40.8/35.1 ms; no saved statistic is 29 ms).
  Fixed in the verdict paragraph.
- W3: per-element rects "about 3.6-3.9 ms per call" was wrong; 219.8/60
  = 3.66 and 239.5/60 = 3.99, i.e. 3.7-4.0 ms per call. Fixed.
- W4: local think "max 0.157 ms" was wrong; saved maxes are 0.133 ms
  (run 2) and 0.174 ms (run 3); true max 0.174 ms. Fixed.
- W5: naive 10-step total "about 6.4-7.0 s" mixed two bases in its
  derivation. Restated on the full-addition basis, which matches the
  naive loop as measured (measure_loop.mjs: the naive shape is full
  DOM + screenshot, click, full DOM verify, with no rects call):
  setup 3,883-4,229 ms + naive loop 10 x 34.7-39.1 ms + per-element
  rects 10 x 219.8-239.5 ms = 6,428-7,015 ms, about 6.4-7.0 s. The
  2.1-2.3 s figure is the saving of one-shot rects over per-element
  rects, not the cost of adding per-element rects to a loop that has
  no rects call. Note for the record: the original total value
  (6.4-7.0 s) happens to match the exact-median full addition, but
  its stated derivation (4.3-4.6 s baseline + 2.1-2.3 s saving) sums
  to 6.4-6.9 s, not 6.4-7.0 s, so the derivation was wrong even
  though the value was right. The redteam's suggested 6.5 s lower
  bound comes from adding already-rounded subtotals (4.3 + 2.2) and
  is a double-rounding artifact; exact medians give 6,428 ms, about
  6.4 s. The baseline is corrected with it, from 4.3-4.6 s to
  4.2-4.6 s (exact: 4,230-4,620 ms), and the cuts save stays
  6.1-6.7 s (6.43-7.02 s minus 0.3 s). Fixed in the verdict
  (value unchanged, derivation corrected) and in section 3.
- W9: agentpatterns "18 days" was wrong; the page shows Updated
  2026-11-03, i.e. 19 days before 2026-11-22. Fixed.
- W10: frowse "2 days" was wrong; PyPI release 0.1.2 was uploaded
  Nov 19, 2026, i.e. 3 days before 2026-11-22. Fixed.
- U4: guibai "7 days" is unverifiable from the fetched page (no visible
  date). Marked as such; the content claims are unchanged.
- U5: surfs.dev citation is dead at review time ("Post Not Found").
  Marked as such; date and content rest on the search index only.
- U2: run 1 numbers have no saved file; the header now says so
  explicitly ("unpreserved, no saved copy"). Do not cite run 1 numbers
  in the batch 7 final report.
- U3: "no Firefox process left running" has no artifact; the ranges
  paragraph now says so plainly.
- U7: the install section still cannot say what the safety check was;
  the agent did not record it. Noted in section 4.
- M1: run 3 think median is 0.001 ms, not 0.0 ms; the table now shows
  0.001 ms for run 3.

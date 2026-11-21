# 2-vision benchmark workflow

Date: 2026-11-22. Status: script + workflow BUILT ONLY, no live run yet.
This benchmark is an acceptance test. It runs live ONLY after the
improved method is approved and the coordinator says run.

## 1. What it is

The combined design from improvements/worker-coord-click2-log.md
("The combined design"), as an executable script:
tests/two_vision_bench.py, with the dry-test fixture
tests/two_vision_fixture.html.

- VISION 1 builds the inventory: one-shot bulk DOM harvest per clone
  window (one evaluate per window, ref, role, name, rect, center,
  visibility, focused for every input + button), formatted as numbered
  compact text (Mantis pattern). VISION 1 is a DOM harvest, NOT a
  screenshot.
- Plan-once: the whole send sequence (click clone1 input, type, Enter,
  click clone2 input, type, Enter) is emitted as one program from the
  inventory.
- Guarded execution: HCU-style live guard re-checks each target's live
  geometry + focus right before input; stop at first failure, rest
  reported not-executed; exactly-once intent per send (ledger +
  V12 pre-check, a retry never re-sends a message already in the
  thread); V12 finish gate after each send (sent bubble in the thread
  DOM).
- Scoring is by OUTCOME (message in the thread or not, M1), never by
  point-in-box. PASS iff both messages land in their threads.
- Total: exactly 2 visions. VISION 1 is the inventory read; VISION 2
  is the agent looking at both threads once at the end to confirm both
  bubbles. Everything between them is cheap DOM reads, zero extra
  observes. The script's V12 gates are the same outcome check done by
  DOM read.

## 2. Safety rules (read before any run)

- NEVER run live without the coordinator saying run. The script
  refuses live mode unless BOTH --live and --confirm-live are given.
  --confirm-live is only passed when the coordinator approved the run.
- NEVER type into a real thread in fixture mode. Fixture mode (the
  default) only opens tests/two_vision_fixture.html in headless
  Firefox on this VM.
- The live lane must be free (no BASELINE2 or other live run), and
  the installed laptop code must still be the pre-amend code if a
  baseline is still owed. Check with the coordinator first.
- No personal information in any plan, inventory, ledger, log, or
  result file. Test messages are bench strings only
  ("BENCH-TEST ..."), never real user text.
- No em dash or en dash in any file this workflow produces.

## 3. Prerequisites

- Headless Firefox 160.0.1 at ~/workspace/tools/firefox/firefox,
  geckodriver 0.37.1 at ~/workspace/tools/geckodriver, venv with
  Selenium 4.53 at ~/workspace/tools/venv. Run with
  ~/workspace/tools/venv/bin/python.
- One active remote session per browser instance (Firefox 160 rule,
  proved in batch 7 task 2): this script uses Marionette only and
  never opens a BiDi session while Marionette is active.

## 4. Files

- tests/two_vision_bench.py: the benchmark script (commit 072e060,
  fixes 9196744).
- tests/two_vision_fixture.html: local chat fixture. One page per
  clone (?clone=1, ?clone=2). A message input, a Send button, a
  thread div. Enter or Send appends a bubble with the typed text.
  Also a Search input and an Emoji button so the harvest is not
  trivial (4 inputs + buttons per window).
- Workdir (default /tmp/two_vision_bench/<run>): inventory.json,
  ledger.json, results.json, profile/ (Firefox profile, delete after
  the run; /tmp is a 512M tmpfs and fills up fast).

## 5. Step by step

### Step 0. Write the plan JSON (live runs only)

Fixture mode builds its own plan (unique run_id, BENCH-TEST
messages). A live plan looks like this:

```json
{
  "run_id": "bench-20261122-001",
  "windows": [
    {"label": "clone1", "url": "<thread 1 URL>",
     "input_name": "Message", "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"},
    {"label": "clone2", "url": "<thread 2 URL>",
     "input_name": "Message", "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"}
  ],
  "messages": {
    "clone1": "BENCH-TEST clone1 bench-20261122-001",
    "clone2": "BENCH-TEST clone2 bench-20261122-001"
  },
  "timeouts": {"v12_gate_s": 5}
}
```

- run_id must be unique per run. The exactly-once ledger keys on it;
  reusing a run_id reuses its intents (that is how a retry skips
  already-sent messages).
- input_name is matched against the harvested textbox names; the first
  visible textbox is the fallback.
- thread_selector must point at the thread container. bubble_selector
  defaults to ".bubble, [data-sender]"; override it for Messenger.
  A wrong thread_selector fails the V12 gate loudly (the gate honors
  the selector; there is no fixture-helper shortcut).

### Step 1. VISION 1, harvest only (optional, recommended)

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --fixture --mode harvest --print-inventory \
  --workdir /tmp/two_vision_bench/runH
```

Writes inventory.json and prints the numbered compact text, for
example:

```
Window clone1: 4 inputs+buttons
[1] textbox 'Message' ref=#msg-input rect=(20,238,340x39) center=(190,257) visible=True focused=False
[2] button 'Send' ref=#send-btn rect=(364,238,59x39) center=(394,257) visible=True focused=False
```

The agent reads this text (VISION 1), picks the two message inputs,
and checks the refs, rects, and visibility before the run. Refs are
valid only within this inventory (gap D3): they are derived from the
live DOM of this run and must not transfer between runs.

### Step 2. Run the send chain

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --fixture --workdir /tmp/two_vision_bench/run1
```

For a live run (coordinator approval only):

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --live --confirm-live --plan /tmp/plan-live.json \
  --workdir /tmp/two_vision_bench/live1
```

Without --confirm-live the script refuses with exit code 2 and sends
nothing.

To reuse a saved inventory instead of harvesting again:

```sh
--inventory-in /tmp/two_vision_bench/runH/inventory.json
```

### Step 3. Read the results

- results.json: run_id, mode, live flag, outcome (PASS, FAIL, or
  HARVEST-ONLY), wall_s, and one record per step: window, intent_id,
  status (sent, skipped-already-sent, failed, not-executed),
  elapsed_s, error reason, v1_value_ok, v11_input_events,
  v12_gate_ok.
- STDOUT is JSONL, one line per step: wall clock (UTC) and elapsed
  seconds from a monotonic clock.
- Exit code: 0 PASS, 1 FAIL (benchmark outcome), 2 harness error or
  refused live run.
- VISION 2: look at both threads once and confirm both bubbles.
  The script's V12 gates already checked the same thing by DOM read;
  the agent's look is the independent outcome confirmation.

## 6. What each failure means

| Step status / error | Meaning |
| --- | --- |
| no-message-input-in-inventory | No visible textbox in a window's harvest. The program cannot be built; nothing is sent (fail-closed). |
| target-gone | The input vanished between inventory and guard. |
| not-visible / covered | V5 hit test failed: the rect center does not hit the input, or it is hidden. |
| geometry-moved | The input moved more than 2 px from the VISION 1 snapshot. The inventory is stale; re-harvest. |
| focus-failed | The click landed but activeElement is not the input. Nothing was typed. |
| value-mismatch | V1 readback: the field does not hold the typed text. Enter was not sent. |
| v12-timeout | No sent bubble in the thread DOM within the gate timeout. The message may still have been typed (check the thread); the run is FAIL and the ledger marks the intent failed. A retry first runs the V12 pre-check, so a message that did land is not sent twice. |
| not-executed | A later step after a failure. The chain stopped at the first failure (Anthropic batch loop contract). |

## 7. Dry-test results (measured on this VM, headless Firefox 160.0.1)

Wall clock is UTC, elapsed from a monotonic clock. All runs used the
repo venv python. Fixture: 4 inputs + buttons per window.

- Happy path, 2 windows (final run, 2026-11-21T20:25:12Z to
  20:25:19Z): PASS, wall 6.1839 s total. Browser launch 1.0137 s,
  Marionette attach 2.7903 s, harvest 0.0883 s (clone1) and 0.0863 s
  (clone2) for 4 elements each, sends 0.7071 s (clone1) and 0.4448 s
  (clone2). Both V12 gates passed. Full log:
  /tmp/two_vision_bench/final.log, results in
  /tmp/two_vision_bench/final/results.json. (An earlier happy-path
  run, run1b, gave the same PASS with wall 6.2165 s and sends
  0.86 s / 0.39 s.)
- Exactly-once (separate driver test, same intent twice in one
  browser session): first send "sent", 1 bubble; second send
  "skipped-already-sent" in 0.0026 s, still 1 bubble. PASS.
- Stop-at-first-failure, 3-window plan with a wrong thread selector
  for clone2 (run3b, 2026-11-21T20:23:16Z to 20:23:27Z): FAIL as
  designed, wall 11.0567 s. Clone1 sent (0.69 s), clone2 failed
  v12-timeout after the 3 s gate (its message was typed into the
  fixture but the gate could not see it through the wrong selector),
  clone3 not-executed.
- Harvest-only (runH, 2026-11-21T20:23:38Z to 20:23:43Z):
  HARVEST-ONLY, wall 5.0420 s, 4 elements per window.
- Live refusal: --live without --confirm-live exits 2 and sends
  nothing (verified, no browser started).

Bugs found by the dry tests and fixed in the script (commit
9196744): (1) the harvest/verify/gate JS had no top-level return, so
Marionette returned None; (2) Ledger crashed when its workdir did
not exist yet; (3) the V12 gate used a fixture helper that ignored
the plan's thread selector, so a wrong selector passed silently;
(4) the exactly-once pre-check only ran when the ledger said sent,
so a retry after a failed gate could double-send; it now runs the
V12 pre-check before every send regardless of ledger status.

Incident during dry-testing: /tmp (512M tmpfs) filled to 100% from
stale Firefox profiles and was cleared by deleting only this
benchmark's own stale profiles plus stale .xpi files (no live
Firefox running at the time). Other agents' /tmp material was left
untouched. Delete the profile/ dir under each run workdir after the
run to avoid repeating this.

## 8. Known gaps (F5/D1-D6, TODOs, from the combined design)

Marked as TODO in the script where they apply; the review round
revises them. None of these blocks the dry test, but a live run
must not claim them done.

| Gap | State in this script | What is still open |
| --- | --- | --- |
| F5 bulk harvest | Built here as one evaluate per window. | Brave CDP DOM.getBoxModel / Accessibility.getFullAXTree in scripts/cdp.mjs; production V11 MutationObserver flag (the fixture counts input events; a Messenger page needs a real observer armed before typing). |
| F5 V12 gate | Built here (sent-bubble check after each send). | No V12 gate exists in production code; this script is the first implementation. |
| F5 exactly-once ledger | Built here (ledger file + V12 pre-check before every send). | Needs review-round approval; a wrong thread_selector still lets a typed-but-unseen message double-send on retry with a fixed selector. |
| F5 BiDi/Marionette handover | Not built. Script is Marionette-only. | No handover protocol exists under the one-session constraint. |
| F5 step-6 loop hygiene | Not built. | Prompt caching, diff-gated re-observation, downscale to token tier, context editing, low effort, adaptive waiting: unowned, agent-harness concerns. |
| D1 one-session sequencing | Marionette-only; BiDi session.new cost is known (1.5-2.8 s cold, 0.014 s warm, batch 7 task 2). | Sequencing for a live run that needs both protocols is unspecified. |
| D2 HCU guard owner | The guard lives in hcu_guard() in this script. | No production component owns the guard. |
| D3 Mantis numbering | Refs are DOM-derived per run; the doc warns they must not transfer. | Ref stability on a mutating Messenger page is unaddressed. |
| D4 exactly-once | Mechanized here (ledger + pre-check). | Needs the review round; see the F5 ledger row. |
| D5 VISION 1 is DOM | Stated in the script docstring and here. | Nothing open; do not call the harvest a screenshot. |
| D6 one vs two instances | One instance, two windows (flag --instances records the choice). | Unspecified which the live run uses; two instances need a second Marionette attach. |

## 9. What is NOT done (do not claim it)

- No live run has happened. The script has only ever run against
  the local fixture in headless Firefox on this VM.
- No Zen numbers. Every timing above is Firefox 160.0.1 as a
  stand-in; real Zen timings are UNVERIFIED until the laptop run.
- No Messenger selectors. The live plan needs real thread URLs,
  thread selectors, and bubble selectors, which only the coordinator
  can supply for the live run.
- The C12 conversion layer (viewport origin, DPR) is NOT used by
  this script: clicks use viewport coordinates from
  getBoundingClientRect directly, the same shape as the batch 7
  bench. Live Zen clicks need the C12 adjudication (batch 8 task 3)
  before the coordinates can be trusted on the laptop.

# Microsoft Hybrid Computer Use (HCU): research and prototype

Date: 2026-11-21. All sources below were accessed 2026-11-21. Repo HEAD
at time of writing: 5cd5c74. This machine has no Firefox or Zen binary,
so the prototype in this task ran on Playwright Chromium, not on Zen.
Anything about real Zen behaviour is marked UNVERIFIED.

## Sources

- Paper: Haoqing Wang, Xiaoyi Zhang, Sicheng Fan, Zhexin Zhang, Xinjie
  Zhang, Jiahao Li, Bin Li, Yan Lu, "Hybrid Computer Use: A Unified
  Programmatic, Semantic, and Visual Interface for General Agents",
  arXiv:2610.41432, submitted 30 October 2026.
  https://arxiv.org/html/2610.41432v1
- Official repo: https://github.com/microsoft/Hybrid-Computer-Use
  (created 2026-10-08, MIT license, current commit 8ce82b31 at time of
  reading, 65 stars, 35 commits, 2 releases)
- Project page: https://microsoft.github.io/Hybrid-Computer-Use/
- The paper PDF is also in the repo at paper/Hybrid-Computer-Use.pdf.

## 1. What HCU is

Hybrid Computer Use is an open-source Model Context Protocol (MCP)
server, `computer-use`, from Microsoft Research, with collaborators at
Fudan University and Tsinghua University. It gives a general coding
agent (Codex, Claude Code, Gemini CLI, Grok Build) three ways to touch
a desktop instead of one: run code, read the accessibility tree, or
click the screen like a person. The paper's argument is that
screenshot-and-mouse interfaces impose a human-interaction prior on
the model: the agent spends effort locating a field by screen
coordinates even when the application exposes its identity and value
through accessibility data, or drags data around by mouse when code
could process it directly.

## 2. Architecture: three channels, one core

HCU combines three complementary channels in one agent task context:

| Channel | Tool | What the agent does with it |
| --- | --- | --- |
| Programmatic | the agent's own shell and file tools | Edit files, query data, run command-line tools |
| Semantic | `AX` | Read a compact accessibility tree with short refs (`a1`, `w1`, `r12`), run up to 64 actions in one call with waits, get back a diff |
| Visual | `GUI` | Take full-desktop screenshots, zoom into dense regions, send batched pointer and keyboard input |

One Go core implements the contract once. Coding agents call it over
MCP; shell scripts and Python code share one daemon per desktop, so
refs carry over between entry points. One process owns one desktop
session: either the stdio server `computer-use mcp`, or a background
daemon shared by the CLI, the Python SDK, and `computer-use mcp
--attach`. The shared Go service validates calls and maintains AX
snapshots, reference registries, find cursors, eligible diff
snapshots, and the GUI layout lease.

Native providers per OS, behind the same public AX and GUI contract:

| OS | Provider | Evaluated on |
| --- | --- | --- |
| Linux (X11) | Python, embedded in the binary: AT-SPI2, X11, XTest | OSWorld 1.0 and 2.0, WeaveBench |
| macOS 14+ | Swift: AXUIElement, CoreGraphics, ScreenCaptureKit | MacAgentBench |
| Windows 10/11 | C# .NET 8: UI Automation (FlaUI UIA3), Win32 | Windows Agent Arena |

Channel selection stays model-directed. HCU adds no planner,
subagents, or loop of its own, so the same interface attaches to
different agent harnesses. Observation and execution need not use the
same channel: a screenshot can supply visual context for a later AX
action. On 29 to 31 percent of tasks where GPT-5.4, Gemini 3.8 Flash,
or Grok 4.7 used GUI, every GUI request was a screenshot and every
action went through AX.

## 3. The AX channel: compact views, refs, batches, diffs

### 3.1 Compact observation

HCU separates the AX records it retains from the compact AX view
shown to the model. Projection removes empty structural wrappers,
merges adjacent unreferenced text leaves, deduplicates
relation-backed labels, preserves context needed to disambiguate
same-name controls, displays table cell values alongside names, and
summarizes repetitive sibling runs under a structural budget.
Target references are bound to elements before compression, so
shortening the view does not change which element a reference
identifies. The retained records support AX diffs after an action,
while find and scoped observations retrieve targets omitted from the
compact view.

Measured token reduction from projection alone, same capture:
Chrome 44.1 percent (1,817 to 1,016 tokens), Audacity 14.1 percent
(439 to 377), Obsidian 12.6 percent (1,374 to 1,201), while retaining
100 percent of issued target references (53/53, 11/11, 48/48).
Against the stock OSWorld 2.0 accessibility XML on the same Obsidian
window, the full representation drops from 30,526 tokens to 1,237.
The project page gives the Chrome settings example: 169 nodes in the
tree become a 73-line view that keeps every control the model can
act on.

References are short: applications `aN`, logical top-level windows
`wN`, elements `rN`. Element actions resolve these references
against live state, not tree line numbers or display labels.

### 3.2 Batched actions and wait steps

An `AX act` call executes up to 64 ordered actions and wait steps
within one logical window. A `GUI input` call executes up to 64
ordered actions: pointer, drag, scroll, text, keys, or wait. The
released version raised the batch limit from 32 to 64 steps.

A wait step sends no input and holds until a window title appears,
a query matches, a referenced element reaches an expected value,
state, or text, a target disappears (gone), or the UI changes and
stops changing (settle). Placed last, a wait step verifies the
final state. This combines batching with state verification in the
style of Playwright assertions, without a separate verification
call. If an action fails, a wait times out, or window continuity is
lost, HCU stops the batch and reports the stopping point and
execution evidence, so the agent can decide how to continue without
blindly repeating earlier actions.

Example batch from the repo README:

```json
{
  "mode": "act",
  "actions": [
    {"type": "click", "ref": "r12"},
    {"type": "wait", "window": "Export"},
    {"type": "type", "text": "q3.csv"},
    {"type": "keypress", "keys": ["ENTER"]}
  ]
}
```

### 3.3 Post-action feedback: diff-only observation

By default (`observe=diff`), an act call reports a per-target
effect, a windows line (opened, closed, or focused `wN`), and the
structured AX diff against the last eligible snapshot delivered to
the model. The agent can instead request a screenshot or execution
evidence only. Returning feedback with the action lets the agent
continue without a separate observation when the information
suffices. HCU reports only what the available evidence supports:
it distinguishes known non-delivery from an unknown effect after
possible input, so the agent is not led to treat input delivery as
a verified effect.

Every AX and GUI response starts with one JSON status line
(`ok`, `code`, `hint`, `input_emitted`, `completed`), followed by
the effect on each target, the open windows, and a compact AX diff
or a screenshot. Public error codes include `invalid_argument`,
`stale_ref`, `gui_frame_stale`, `wait_timeout`, `window_changed`,
and `effect_unknown`.

## 4. Guards against stale state

Because all three channels act on the same desktop, an action in
one channel can invalidate the evidence held by another. An AX
action may open a dialog over coordinates from an earlier
screenshot, or a GUI action may replace a control addressed by an
AX reference. HCU checks targets and layouts against live state
immediately before input (paper Algorithm 1):

- AX target guard: resolves each target reference immediately
  before execution and checks the element's identity and
  action-specific requirements. If the target is missing,
  ambiguous, or replaced, or a requirement is not met, HCU rejects
  the action without sending input. It does not redirect the
  action to a similarly named element.
- GUI layout guard: checks whether the layout underlying the
  model's chosen coordinates still matches the last screenshot.
  Before coordinate input it compares the current desktop bounds,
  visible top-level windows, stacking order, active window, and
  target-point window layout with those bound to that screenshot.
  On mismatch it blocks the input with `gui_frame_stale` and
  returns a fresh screenshot so the model can choose new
  coordinates.

Cross-channel invalidation: GUI input that may mutate desktop state
invalidates the AX working snapshot, hidden-element cache, and find
cursors, while retaining reference registries and the last delivered
diff snapshot. Conversely, a GUI screenshot or an AX
full/screenshot observation registers the current GUI frame and its
layout lease. Both guards inspect current state regardless of which
channel changed it, including earlier actions in the same channel.
If focus or pointer preparation fails in an uncertain state where a
queued OS request may still fire, HCU stops desktop automation
rather than replaying the batch.

The paper's recorded example: an AX action closes a side panel and
the toolbar shifts, so a click planned on Save would land on
Delete. HCU detects the changed layout, sends nothing, and returns
a fresh screenshot; the corrected click lands on Save.

## 5. The skill

A supplementary skill, distilled from recurring mistakes in
development trajectories, explains channel capabilities, efficient
interaction (refs, batching with wait steps, continuing from
returned feedback), and verification and recovery. It contains no
task-specific solutions. Measured effect: the share of AX and GUI
calls rejected for malformed arguments falls from 17.37 percent to
1.36 percent, and the share of task runs repeating such rejections
on the same tool falls from 44.69 percent to 0.37 percent. With the
skill, 87 percent of AX action calls omit the observe field and
take the default AX diff, compared with 0.2 percent without it.
GUI input actions fall from 4.96 to 1.97 per task. These changes
accompany a 14.55 percent reduction in steps and a 1.59-point gain
in score.

## 6. Results: what 70.13 percent means

### 6.1 OSWorld 2.0

OSWorld 2.0 is the long-horizon real-world benchmark, 108 tasks in
the 0808 release, scored as Partial (mean task score) and Binary
(full-credit rate). Each comparison keeps model, harness, tasks,
and step budget fixed and changes only the interface. Baseline is
CUA Driver.

| System | Model | Partial | Binary | Cost per task |
| --- | --- | --- | --- | --- |
| HCU (Codex) | GPT-6 Astra | 72.37 percent | 32.40 percent | 10.03 dollars |
| CUA Driver (Codex) | GPT-6 Astra | 68.82 percent | 31.50 percent | 10.05 dollars |
| HCU (Claude Code) | Claude Opus 5 | 72.06 percent | 35.19 percent | 22.67 dollars |
| Computer-use loop | Claude Opus 5 | 68.31 percent | 31.43 percent | 28.43 dollars |

HCU has the highest Partial (72.37 percent, GPT-6 Astra) and the
highest Binary (35.19 percent, Claude Opus 5) of all full-set
systems in the comparison. With GPT-6 Astra it beats the matched
CUA Driver baseline by 3.55 points in Partial and 0.90 in Binary,
with 29.81 percent fewer tool calls at nearly identical cost.
With Claude Opus 5 it beats the model's official leaderboard
result by 3.75 points in Partial and 3.76 in Binary at 20.26
percent lower cost.

### 6.2 OSWorld 1.0: the 70.13 percent figure

OSWorld 1.0 is the everyday desktop benchmark, 360 tasks, scored
as Score. The 70.13 percent figure is HCU with GPT-5.4: 70.13
percent Score against 62.47 percent for CUA Driver with the same
model, at 59.1 percent lower cost. Across four backbone models,
each in its own harness, HCU averages 6.48 more points in Score,
17 percent fewer steps, and 30 percent lower cost.

| Model | CUA Driver | HCU | Change | Steps | Input | Time | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.4 | 62.30 | 65.59 | +3.29 | -30 percent | -57 percent | -30 percent | -55 percent |
| Claude Opus 5.5 | 68.68 | 71.62 | +2.94 | -1 percent | -32 percent | +6 percent | -8 percent |
| Gemini 3.8 Flash | 54.67 | 67.57 | +12.90 | -17 percent | -39 percent | -29 percent | -44 percent |
| Grok 4.7 | 67.90 | 74.71 | +6.81 | -22 percent | -18 percent | -13 percent | -13 percent |

Note the table's GPT-5.4 HCU score is 65.59 percent, from the
ablation runs; the 70.13 percent figure is the headline GPT-5.4
result quoted in the abstract and README. Both are the paper's
own numbers, not reproduced here.

Ablation, GPT-5.4 on OSWorld 1.0: HCU 65.59 percent, 28.60 steps,
0.941M input tokens, 351.3 s, 2.52 dollars per task, against CUA
Driver 62.30 percent, 40.74 steps, 2.181M tokens, 500.8 s, 5.65
dollars. Removing the AX channel alone costs 2.79 points and adds
14.08 percent steps, 10.44 percent input, 12.58 percent time, and
10.64 percent cost, the largest single-component loss. Removing
the GUI channel leaves score within run-to-run variation but adds
12.45 percent steps. With only AX and programmatic tools, HCU
still beats CUA Driver by 3.79 points at 21.06 percent fewer
steps and 56.70 percent lower cost.

### 6.3 Other benchmarks and channel allocation

With GPT-5.4, HCU also beats CUA Driver on WeaveBench (53.25
percent vs 46.37 percent, 46.3 percent lower cost), the
MacAgentBench UI subset (25 vs 24 of 28 tasks, 51.4 percent lower
cost), and Windows Agent Arena (80.86 percent vs 71.89 percent,
50.6 percent lower cost).

Models divide work across channels differently: GPT-5.4 sends 80
percent of desktop requests to AX; Grok 4.7 sends 68 percent;
Gemini 3.8 Flash 51 percent. Claude Opus 5.5 sends 94 percent to
GUI and batches actions most often: 58 percent of its acting
calls contain two or more actions, against 11 to 21 percent for
the other models. Nearly all of the overall score gain over CUA
Driver comes from tasks where HCU makes at least one AX or GUI
call.

Worked example from the repo: formatting cells in LibreOffice
Calc takes pure GUI 6 model turns and about 41 seconds, CUA
Driver 11 turns and about 74 seconds, HCU 4 turns (three AX calls
and one GUI zoom) and about 27 seconds.

## 7. What applies to this repo

This repo drives Zen, a Firefox fork, and already has BiDi and CDP
paths plus a WebExtension bridge. HCU's lessons map onto it as
follows:

1. Batch actions. One call should carry up to 64 ordered actions
   and wait steps, stopping at the first failure and reporting how
   many steps completed. This replaces one model round trip per
   action with one round trip per batch. The prototype below proves
   the mechanics on a web page.
2. DOM locate, then real mouse click. Locate the target through
   the DOM (selector or accessibility ref), then send a real mouse
   click at the element's live bounding-box center. That is the
   hybrid of HCU's semantic and visual channels: the DOM gives
   identity, the real input gives trusted events. Synthetic
   `element.click()` is not a substitute where pages check
   `event.isTrusted`.
3. Diff-only observation. After a batch, return only what changed
   (field values, window changes, refs), not a fresh full snapshot
   or screenshot. The paper shows this is where most of the token
   saving comes from: compact views plus diffs cut input tokens
   by more than half against the baseline.
4. Stale-layout guard. Before each action, re-resolve the target
   against live state. Reference-addressed actions are rejected
   when the element is missing, hidden, or disabled, with no input
   sent. Coordinate input planned from an old screenshot is
   rejected when the live layout no longer matches it, and the
   caller gets fresh evidence instead of a blind retry. The
   prototype implements the reference guard and proves it with a
   removal test.
5. Wait steps inside the batch. A batch should be able to wait
   for a window, a value, a state, a disappearance, or a settle
   before later steps run, instead of the caller polling between
   calls.
6. One session owner. HCU runs one process per desktop session so
   refs and the input lock persist across entry points. This repo
   has a separate task for a single-session manager for BiDi and
   Marionette; that manager is the counterpart of HCU's shared
   daemon.

## 8. Prototype: batched actions on a test page

Files, all new, none overwriting existing files:

- `tests/hcu_batch.mjs`: the batch executor. Modes `--mode batch`
  (one call: observe once, run all actions, return a diff) and
  `--mode single` (each action as its own call with a full
  observation before and after, modeling the
  screenshot-every-step loop). Actions: click, type, select,
  check, scroll, wait, evaluate. Click locates through the DOM
  and then sends a real mouse click at the live bounding-box
  center. Batch limit 64 is enforced before any browser work.
  Exit 0 success, 2 failed run, 3 playwright-core missing.
  Every line printed is one JSON object with wall-clock time and
  elapsed ms, plus a final summary line.
- `tests/hcu_batch_fixture.html`: local fixture page (two text
  inputs, a select, a checkbox, a counter button, a dialog that
  opens 150 ms after its button is clicked, a scrollable list, a
  save button). Served by the script itself on a loopback HTTP
  server when no `--url` is given.
- `tests/hcu_batch_smoke.mjs`: browser-free checks: `--help`
  exits 0, 65 actions are rejected with the 64 limit, unknown
  action type is rejected, missing selector is rejected, bad mode
  is rejected.

How to run it:

```sh
mkdir -p /tmp/hcu-scratch && cd /tmp/hcu-scratch
npm init -y && npm install playwright-core@1.55.0
PLAYWRIGHT_PATH=/tmp/hcu-scratch/node_modules/playwright-core \
CHROMIUM_PATH=/home/hatch/.cache/ms-playwright/chromium-1254/chrome-linux64/chrome \
  node tests/hcu_batch.mjs --mode batch
```

### 8.1 Real runs on this machine

Machine: Node v24.22.1, Playwright Chromium 1254 headless, repo
HEAD 5cd5c74, all runs 2026-11-21 08:24 to 08:25 UTC. The default
batch is 12 actions: type name, type email, select plan, check
agree, click counter 3 times, click open-dialog, wait for the
dialog, click confirm, scroll the list to the bottom, click save.

- `node tests/hcu_batch_smoke.mjs`: all 5 checks pass, 0.665 s
  wall clock.
- Batch mode, 3 runs: exit 0, 12 of 12 actions each time.
  Totals 1988, 2157, 2094 ms including browser launch; observe
  102, 66, 178 ms for 2 observations. Diff returned correctly
  every run: name "Ada Lovelace", email "ada@example.com", plan
  "pro", agree true, counter "3", status "saved", saved-count
  "1", list scrollTop 1176. The dialog opening and closing nets
  to no change, so it correctly does not appear in the diff.
- Single mode, 3 runs: exit 0, 12 of 12 actions each time.
  Totals 1395, 1291, 1231 ms; observe 125, 96, 85 ms for 24
  observations.
- Interleaved runs (batch, single, batch, single, batch,
  single): batch totals 1167, 1280, 1408 ms with action-phase
  sums 473, 447, 490 ms; single totals 1202, 1246, 1663 ms with
  action-phase sums 595, 593, 813 ms.
- Stale guard test: a 3-action batch that clicks the counter,
  removes the save button with evaluate, then clicks save. The
  batch stopped at step 2 with code `stale_ref`, reported
  completed 2 of 3, exit 2, and sent no input for the removed
  target.
- Two bugs found and fixed during this work, both recorded here
  so the history is honest: the fixture server object was stored
  instead of the HTTP server, so `server.close` failed at the end
  of a run; and the stale guard first rejected wait steps whose
  target does not exist yet, then rejected a moved element whose
  reference was still valid. The guard now follows the paper:
  wait steps are exempt, and reference actions are checked for
  identity (missing, hidden, disabled), not for position. The
  layout check belongs to coordinate input, not to references.

### 8.2 Honest reading of the timing comparison

On this small local fixture, batch mode shows no clear wall-clock
win: totals overlap once browser launch noise is accounted for,
and the interleaved runs put batch slightly ahead on action phase
and about even on total time. That is expected. A local DOM read
costs about 4 ms here, so skipping 22 observations saves roughly
100 ms, which launch noise swallows. HCU's measured win does not
come from local execution time. It comes from fewer model round
trips and from tokens: one call instead of twelve, a compact view
instead of a full snapshot, a diff instead of a fresh observation.
This prototype has no model in the loop, so it cannot measure
that part. What it does prove is the mechanics: one call runs 12
ordered actions with a wait step, the stale guard stops a batch
before bad input, the diff reports exactly what changed, and the
64-action limit is enforced.

## 9. What is UNVERIFIED

- No live Firefox or Zen run. This machine has no Firefox or Zen
  binary, so the prototype ran on Playwright Chromium. The batch
  executor, the guard, and the timings are proven only on
  Chromium. Whether the same batch runs against a real Zen over
  BiDi, and what its per-action timings are there, is UNVERIFIED.
- HCU itself was not run here. The Go binary was not built and
  there is no desktop session on this machine. All HCU numbers in
  sections 6.1 to 6.3 are the paper's reported numbers, not
  reproduced here.
- The OSWorld figures are quoted from the paper and the official
  repo README. The 70.13 percent OSWorld 1.0 figure is the
  headline GPT-5.4 result; the paper's own ablation table gives
  65.59 percent for GPT-5.4 in a different run configuration.
  Both numbers are reported as the paper reports them.
- Whether the 64-action batch limit and the wait-step set behave
  identically in the released HCU server, beyond what the README
  and the paper appendix state, is UNVERIFIED without running it.

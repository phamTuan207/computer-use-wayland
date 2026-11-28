# A1 design: generalize Pick 1 code-exec to browser and multi-step GUI tasks

Owner: the owner. Worker: Luna 6 Max. Date: 2026-11-19.
Status: DESIGN, written before building. Proposal A1 in improvements/algorithm-research.md.
Baseline facts: Pick 1 rerun 19/11, 4/4 SUCCESS, mean wall 37.54s to 17.59s (-53 percent),
think -56 percent, calls 5 to 2 (P1/P2). DOM-first D1: core think 99.2s to 20.7s, n=1 per arm.
This design extends the proven interpreter, it does not replace it.

## 1. What changes, in one paragraph

Keep the Pick 1 interpreter, flag, template rules, budgets, and sandbox exactly as they are.
Extend the allowlisted API with five DOM operations that call the existing DOM-first path
(`browser start` / `tabs` / `observe` / `act` through `scripts/cu.py:browser()` and
`scripts/cdp.mjs`, unchanged). A program can then do DOM observe plus click-by-ref plus DOM
assert inside one program call, with no screenshots, and can mix desktop observe/act with
DOM ops in one program with local branching. No change to cdp.mjs, the broker, the driver,
the desktop act path, or the envelope string-arg rule.

## 2. New API (allowlisted names only)

- `dom_start()` -> dict. Starts (or reuses) the managed Chromium via the existing
  `browser_start(env, endpoint)` with the default endpoint `http://127.0.0.1:9222`.
  On success it sets the module-global `BROWSER_ENDPOINT` exactly like the `browser start`
  CLI branch does, and records the endpoint on the backend for later DOM calls.
  Returns the browser_start dict (`ok`, `endpoint`, `reused`, plus `pid`/`profile` on a
  fresh start). A CDP-level failure raises `CodeExecError` with the adapter message,
  like desktop `observe()` raises on failure.
- `dom_tabs()` -> list of `{id, title, url}` for page targets, from the existing `tabs`
  operation. No binding. A failure raises `CodeExecError`.
- `dom_observe(target, scope=None, max_elements=80)` -> compact snapshot dict
  `{snapshot, title, url, elements, truncated, iframes, scoped?}`. `target` is a CDP
  target id string from `dom_tabs()`. `scope` is one CSS selector for one observe only,
  same rule as the CLI `--scope` (non-empty string, at most 1024 UTF-16 code units).
  `max_elements` is an int 1..80, default 80. Never takes an image: DOM observe is
  text only by design, a program that needs a screenshot uses desktop `observe()`.
  The snapshot id is bound to this session with its target id and a creation time,
  exactly like a desktop observation binding. A failure raises `CodeExecError`.
- `dom_act(snapshot, actions, after_scope=None)` -> CDP result dict. `snapshot` must be
  a snapshot dict returned by `dom_observe()` (or an `after` snapshot returned by a
  previous `dom_act`) in this session; a forged, foreign, or expired snapshot fails
  closed with `CodeExecError`. `actions` is a list of 1..32 action dicts, validated
  interpreter-side mirroring the cdp.mjs preflight: type in
  `click, fill, set_value, key, scroll, wait, assert`; `click`/`fill`/`set_value`/`assert`
  need exactly one of `ref`/`selector`, both non-empty strings; a `ref` must exist in the
  bound snapshot's elements (cross-snapshot refs fail closed before any CDP call);
  `text` a string of at most 10000 chars; `keys` a list of strings; `wait` ms 0..2000;
  `assert` `timeout_ms` 0..3000 (the adapter caps polling at 3000); `scroll` needs a
  finite `dy`. Non-string where a string is required raises `CodeExecError` naming the
  argument (the envelope string-arg rule, enforced at the interpreter layer). The result
  dict is RETURNED, not raised, mirroring desktop `act()`: `ok: false` (refusal, stale
  snapshot, assert failure) is a program outcome the program can branch on, re-observe,
  and retry. On success the result carries an `after` snapshot, which the interpreter
  binds automatically as a fresh snapshot so the program can chain without re-observing.
  Session policy mirrors the CLI browser act: `require_observation` before the request
  (a desktop refusal still needs a fresh desktop observe first), `complete_requirement`
  on `ok: true`. `after_scope` follows the CLI `--after-scope` rule (act only, one
  selector, not combined with a terminal assert).
- `dom_assert(snapshot, ref=None, selector=None, text=None, value=None, checked=None, timeout_ms=1000)`
  -> `True` on pass. Convenience over one assert action: exactly one of `ref`/`selector`
  and exactly one of `text`/`value`/`checked` (stricter than the adapter's value-over-text
  precedence, so no predicate is ever silently ignored). Runs with `no_after=True`
  (a terminal assert needs no after snapshot, which saves one CDP round trip).
  Raises `AssertionError` with the CDP error on failure, like `assert_file_contains`.
  Returns `True` on pass.

No other new names. No new builtins. No new attributes: snapshot dicts are read with
`.get` and indexing, both already allowlisted.

## 3. How a program does observe, click-by-ref, assert, with no screenshots

D1 program (same fixture as the DOM-first baseline, `file:///tmp/speed-pick4-20261118/pick4-fixture.html`):

```python
wins = windows()
chrome = [w for w in wins if w["class"] == "chromium"][0]
obs = observe(window=chrome["address"])
result = act([{"type": "key", "keys": ["ctrl", "l"]}, {"type": "type", "text": "file:///tmp/speed-pick4-20261118/pick4-fixture.html\n"}], obs)
verify = observe(window=chrome["address"])
assert_state(result["ok"], "navigate act failed")
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "file:///tmp/speed-pick4-20261118/pick4-fixture.html"][0]
snap = dom_observe(tab["id"])
btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]
clicked = dom_act(snap, [{"type": "click", "ref": btn["ref"]}])
assert_state(clicked["ok"], "dom click failed")
after = clicked["after"]
dom_assert(after, selector="#result", text="pick4-ok")
verify_image = verify["image"]
```

Notes on the shape:

- Navigation has no CDP action (cdp.mjs offers click, fill, set_value, key, scroll,
  wait, assert only), so navigation stays a desktop act on the address bar inside the
  program, exactly as the DOM-first arm 2 did: Ctrl+L first to focus the address bar,
  then type the URL plus Enter, in one act batch. (Correction 19/11 13:40: the first
  draft typed the URL without Ctrl+L; the proven arm 2 sequence focuses the address
  bar first.) A `dom_navigate` via CDP Page.navigate is a follow-up, out of scope
  for A1.
- The template rule adapts to DOM: assert on the `after` snapshot returned by `dom_act`,
  never on the pre-click snapshot. If an act used `no_after`, `dom_observe` again before
  asserting. The DOM assert polls in-page up to `timeout_ms`, so the settle interval the
  desktop template gets from a fresh observe is covered by the poll.
- `verify_image` still comes from a desktop observe, so the final verification image
  rule (exact source plus a final observation image) still holds.

## 4. What a multi-step GUI task looks like as a program

The interpreter already has loops, conditions, and asserts; the new ops only extend the
vocabulary. A multi-step program is observe-act-observe-act across backends in one call,
with local branching on results instead of model round trips:

```python
wins = windows()
term = [w for w in wins if w["title"] == "speed-a1-term"][0]
obs = observe(window=term["address"])
r = act([{"type": "type", "text": "printf 'hello a1\\n' > /tmp/a1-multi.txt\n"}], obs)
verify = observe(window=term["address"])
assert_state(r["ok"], "shell act failed")
assert_file_contains("/tmp/a1-multi.txt", "hello a1")
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "file:///tmp/speed-pick4-20261118/pick4-fixture.html"][0]
snap = dom_observe(tab["id"])
btns = [e for e in snap["elements"] if e["role"] == "button"]
if len(btns) == 0:
    snap = dom_observe(tab["id"])
    btns = [e for e in snap["elements"] if e["role"] == "button"]
assert_state(len(btns) == 1, "expected one button")
clicked = dom_act(snap, [{"type": "click", "ref": btns[0]["ref"]}])
if not clicked["ok"]:
    snap = dom_observe(tab["id"])
    clicked = dom_act(snap, [{"type": "click", "ref": btns[0]["ref"]}])
assert_state(clicked["ok"], "dom click failed twice")
dom_assert(clicked["after"], selector="#result", text="pick4-ok")
```

The branch-and-retry above costs 0 model calls. That is the whole point of A1: the
program, not the model loop, absorbs the second look and the retry.

## 5. Trace budget and sandbox: how they apply

- Trace budget: UNCHANGED. `CodeExecSession._trace` counts only lines whose code object
  filename is `<code-exec>`. DOM backend implementation lines (the node subprocess, JSON
  parse, snapshot binding) do not count, exactly like desktop observe/act implementation
  lines do not count. The API-call budget (32) and the wall-clock budget (default 30s,
  max 60s) already bound runaway DOM calls. A single `dom_act` can overrun the wall
  budget mid-call, bounded by the adapter timeout (60s cap), same as a desktop act;
  the next budget check after the call raises. A new unit test proves a heavy fake DOM
  backend does not blow the trace budget, and a runaway program loop is still caught.
- Sandbox: UNCHANGED except the five new names in `_Validator.allowed_names` and in the
  `run()` namespace. The AST scan still rejects imports, dunders, eval/exec/open, and
  attribute access outside the safe whitelist. DOM results are plain JSON dicts, so no
  new attribute surface is needed.
- State: DOM snapshot bindings persist across code-exec calls in the same session in the
  existing state file (`code-exec-<token>.json`, mode 0600), alongside `variables` and
  `observations`, with the same 90s expiry filter on load (matching the in-page 90s
  snapshot expiry in cdp.mjs). A snapshot stored in a program variable and passed to
  `dom_act` in a later code-exec call still resolves, because the binding is reloaded.
- Flags: `CU_CODE_EXEC=1` gates the whole `code-exec` command (relay env, via drop-in,
  same as Pick 1). `CU_PICK4_FASTPATH=1` gates `rect`/`center` in snapshot elements
  (existing cdp.mjs behavior). Click-by-ref and DOM assert work with the fastpath flag
  off; the live run sets both flags on so the program can disambiguate by rect when
  names collide. The DOM ops themselves are NOT separately flag-gated: they are part of
  code-exec.
- Ownership, lease, generation, cancellation, and explicit finish are untouched:
  `check_cancel` runs before every DOM call through `_api`, and a cancelled run raises.

## 6. What does NOT change

- `scripts/cdp.mjs`: no change. The adapter preflight stays the final authority; the
  interpreter validation mirrors it so bad programs fail fast with a clear error.
- The broker, the driver, the desktop act path, pointer-miss and screen-changed refusals,
  and the envelope string-arg rule: no change.
- `MAX_PROGRAM_CHARS` (8192): DOM programs fit (the D1 program is about 900 chars).
- The Pick 1 terminal template: unchanged, still the template for terminal tasks.

## 7. Risks, and the guard for each

- Program-composition think grows with program length (P3/P4 think-before-code-exec was
  about 18s vs P2 8.59s). Guard: measure think-before-code-exec on the D1 program and
  report it; if it eats the DOM saving, the verdict says so.
- Snapshot 90s expiry vs the program wall budget (30s default): a program that spends
  its budget on desktop steps can hold a stale snapshot. Guard: binding expiry raises a
  clear `CodeExecError` (observe again), and the template observes the DOM snapshot
  immediately before use.
- Assert-before-settle race (the P3 lesson): the DOM assert polls in-page, and the
  template asserts on the `after` snapshot, never the pre-click one.
- Stale snapshot after navigation: cdp.mjs throws `page navigated; observe again`
  (its in-page `pageState` checks the snapshot id, age, and URL before every action),
  and the interpreter binding fails closed on an expired or unbound snapshot id.
  The program re-observes.
- A `dom_act` retry replaying a partially completed click: the retry contract is the
  A2 contract, not A1. A1 retries only by re-observing and re-issuing from a fresh
  snapshot, and only when the first result proves `completed: 0` or `ok: false` with no
  effect (the adapter preflight validates the whole batch before any effect, so a
  preflight failure has `completed: 0`).

## 8. Tests (before/after, same suites as the envelope and actions-JSON workers)

- Suites: `PYTHONPATH=tests:scripts python3 -m unittest test_session_remote
  test_session_driver test_act_diagnostics test_code_exec test_cdp_snapshot
  test_browser_worker`. The first four are the prior workers' suites; the last two
  cover the DOM path this change touches. Before run at HEAD 9a257c5, after run after
  the change. Compare sorted FAIL/ERROR diffs; the known-flaky set is the 5
  pre-existing `test_session_driver.DoctorCliTests` failures (sha256
  9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd on the 5-failure set).
- New unit tests in `tests/test_code_exec.py` with a `FakeDomBackend` (no live browser):
  dom observe binds a snapshot and returns its elements; dom_act accepts a bound
  snapshot and a ref from it, returns the dict, and binds the `after` snapshot;
  dom_act rejects a forged snapshot, a ref from another snapshot, and a non-string
  ref with `CodeExecError`; dom_assert passes on a matching assert and raises
  `AssertionError` on a failing one; dom_observe rejects a bad scope and a bad
  max_elements; a heavy fake DOM backend (100k implementation lines) does not blow
  the trace budget; a runaway program loop calling DOM ops is still caught; a snapshot
  older than 90s is rejected; multi-step program (desktop act plus DOM act in one
  program) runs end to end on fakes.
- The D1 live program and the terminal regression programs are measured live (step 5),
  not unit-tested, because only a live run proves the saving.

## 9. Live measurement plan

- Relay: drop-in `a1.conf` with `CU_CODE_EXEC=1` and `CU_PICK4_FASTPATH=1`, restart,
  verify active, idle, `started_git_head` is the new HEAD, broker free.
- D1 Chromium task via the generalized code-exec path, same fixture as the DOM-first
  baseline, fresh run dir `/tmp/speed-a1-20261119/`, same `timed.py` wrapper, broker
  SOLO. Plus P1 and P2 terminal tasks as regression (Pick 1 still works).
- Report per task: wall (headline), think total, think-before-code-exec, in-program
  elapsed, model calls, refusals, misclicks, session deaths, program retries.
- Baselines: D1 DOM-first core think 20.7s, time-to-verified about 82s; Pick 1 rerun
  mean wall 17.59s. n=1 per arm, do not quote a precise speedup factor.
- Success bar (the Pick 1 re-measure bar): fewer calls AND lower wall than the
  DOM-first arm, with no rise in refusals, misclicks, or deaths.

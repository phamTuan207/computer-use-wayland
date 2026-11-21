# A1 pilot Layer-2 preflight probe (LIVE, runs at resume, before any pilot arm)

- Purpose: prove the adapter-side preflight guarantee on the REAL browser
  and the REAL fixtures: a bad ref in the middle of a dom_act list must
  refuse the WHOLE batch with completed: 0 and ZERO DOM effects.
- Who runs it: the pilot executor, using its own broker tools, at resume,
  before run 1. One probe per ref-taking action type used in the pilot:
  click, fill, set_value, assert.
- The code-exec language has NO try/except, so each probe is TWO program
  submits: P1 (the bad-ref program, EXPECTED to fail with CodeExecError)
  and P2 (the state-dump program, EXPECTED to show zero effects).
- Fixture URL: the local HTTP server URL from the runbook setup step
  (record the exact URL in the probe log). The pick4 probes use the
  pick4 fixture; the fill/set_value/assert probes use the f01 fixture.
- If ANY probe shows a partial effect (completed > 0, or a DOM value
  changed), the pilot does NOT proceed. That is a NO-GO by safety.
  Report it plainly to Muse with the exact probe output.

## Probe 1: click (pick4 fixture)

P1 program (submit, expect CodeExecError "not present in the bound snapshot"):

```python
started = dom_start()
assert_state(started["ok"], "dom start failed")
wins = windows()
chrome = [w for w in wins if w["class"] == "chromium"][0]
obs = observe(window=chrome["address"])
result = act([{"type": "key", "keys": ["ctrl", "l"]}, {"type": "type", "text": "<FIXTURE_URL_PICK4>\n"}], obs)
assert_state(result["ok"], "navigate act failed")
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_PICK4>"][0]
snap = dom_observe(tab["id"])
btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]
clicked = dom_act(snap, [{"type": "click", "ref": btn["ref"]}, {"type": "click", "ref": "bad-ref-mid-list"}, {"type": "click", "ref": btn["ref"]}])
```

P2 program (submit, expect #result still "not clicked yet"):

```python
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_PICK4>"][0]
snap = dom_observe(tab["id"])
dom_assert(snap, selector="#result", text="not clicked yet")
```

## Probe 2: fill (f01 fixture)

P1 program (submit, expect CodeExecError "not present in the bound snapshot"):

```python
started = dom_start()
assert_state(started["ok"], "dom start failed")
wins = windows()
chrome = [w for w in wins if w["class"] == "chromium"][0]
obs = observe(window=chrome["address"])
result = act([{"type": "key", "keys": ["ctrl", "l"]}, {"type": "type", "text": "<FIXTURE_URL_F01>\n"}], obs)
assert_state(result["ok"], "navigate act failed")
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_F01>"][0]
snap = dom_observe(tab["id"])
cell = [e for e in snap["elements"] if e["name"] == "A2"][0]
filled = dom_act(snap, [{"type": "fill", "ref": cell["ref"], "text": "2026-11-16"}, {"type": "fill", "ref": "bad-ref-mid-list", "text": "Widget"}, {"type": "fill", "ref": cell["ref"], "text": "12"}])
```

P2 program (submit, expect A2 still empty):

```python
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_F01>"][0]
snap = dom_observe(tab["id"])
dom_assert(snap, selector="#A2", value="")
```

Note: the exact f01 cell selector/name depends on the fixture's DOM.
The executor must look up the real ref and selector from the dom_observe
output in P1 and record them in the probe log. If the fixture exposes
cells differently (e.g., contenteditable divs instead of inputs), the
executor adapts the probe to the real DOM and records the adaptation.
A probe that cannot be adapted to the real DOM is reported as BLOCKED,
not silently skipped.

## Probe 3: set_value (f01 fixture)

Same shape as Probe 2, with type "set_value" instead of "fill".
P2 expects the cell still empty.

## Probe 4: assert (pick4 fixture)

P1 program (submit, expect CodeExecError "not present in the bound snapshot"):

```python
started = dom_start()
assert_state(started["ok"], "dom start failed")
wins = windows()
chrome = [w for w in wins if w["class"] == "chromium"][0]
obs = observe(window=chrome["address"])
result = act([{"type": "key", "keys": ["ctrl", "l"]}, {"type": "type", "text": "<FIXTURE_URL_PICK4>\n"}], obs)
assert_state(result["ok"], "navigate act failed")
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_PICK4>"][0]
snap = dom_observe(tab["id"])
btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]
checked = dom_act(snap, [{"type": "click", "ref": btn["ref"]}, {"type": "assert", "ref": "bad-ref-mid-list", "text": "pick4-ok"}, {"type": "click", "ref": btn["ref"]}])
```

P2 program: same as Probe 1 P2, expect #result still "not clicked yet".

## Probe log

Write runs/preflight/preflight-log.jsonl, one line per submit:
{"ts", "probe": "click|fill|set_value|assert", "program": "P1|P2",
 "ok": <bool>, "error": "<exact error or null>",
 "dom_effect": <true|false, from the P2 check>}.
All four probes must show P1 failed with the bad-ref error AND P2
showing no DOM effect. Anything else stops the pilot.

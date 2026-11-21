# A1 pilot Layer-2 preflight probe (LIVE, runs at resume, before any pilot arm)

- Purpose: prove the adapter-side preflight guarantee on the REAL browser
  and the REAL fixtures: a bad ref in the middle of a dom_act list must
  refuse the WHOLE batch with completed: 0 and ZERO DOM effects.
- Who runs it: the pilot executor, using its own broker tools, at resume,
  before run 1. One probe per ref-taking action type the Case B program
  uses: click, fill, set_value, assert. Plus Probe 5 (in-program retry
  logging).
- The code-exec language has NO try/except, so each probe is TWO program
  submits: P1 (the bad-ref program, EXPECTED to fail with CodeExecError)
  and P2 (the state-dump program, EXPECTED to show zero effects).
- Fixture URL: the local HTTP server URL from the runbook setup step
  (record the exact URL in the probe log). The pick4 probes use the
  pick4 fixture; the fill/set_value/assert probes use the f01 fixture.
- A probe failure triggers STOP, FIX THE ADAPTER, RE-PROBE. It is NOT
  an automatic safety NO-GO. A partial effect on a probe proves the
  ADAPTER preflight or its interpreter mirror is wrong, not that batching
  is a bad lever. Only a partial effect that survives a fix attempt, or
  a partial effect the owner explicitly accepts as unfixable, becomes a
  safety NO-GO. Triage checklist before any probe result is recorded:
  confirm the fixture is loaded, the snapshot is fresh (under 90s), the
  browser is up, and the ref namespace is correct. A probe that fails
  for a setup reason is re-run after the setup is fixed, not recorded
  as a safety result.

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

The fill target is the #typed input, not a table cell: cells are plain
td elements with no click handler and are not fillable. The working path
is click a cell BUTTON, fill #typed, click "type", click "Enter". The
probe fills #typed with a bad ref in the middle of the list.

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
typed = [e for e in snap["elements"] if e["role"] in ("textbox", "input")][0]
cell = [e for e in snap["elements"] if e["name"] == "A2"][0]
filled = dom_act(snap, [{"type": "click", "ref": cell["ref"]}, {"type": "fill", "ref": typed["ref"], "text": "2026-11-16"}, {"type": "fill", "ref": "bad-ref-mid-list", "text": "Widget"}, {"type": "fill", "ref": typed["ref"], "text": "12"}])
```

P2 program (submit, expect cell A2 still shows its initial text "-",
so no DOM effect happened):

```python
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_F01>"][0]
snap = dom_observe(tab["id"])
dom_assert(snap, selector="#a2", text="-")
```

Note: the exact #typed role/name depends on the real snapshot. The
executor must look up the real ref from the dom_observe output in P1
and record it in the probe log. If the fixture exposes the input
differently, the executor adapts the probe to the real DOM and records
the adaptation. A probe that cannot be adapted to the real DOM is
reported as BLOCKED, not silently skipped.

## Probe 3: set_value (f01 fixture)

Same shape as Probe 2, with type "set_value" instead of "fill".
P2 expects cell A2 still shows "-". (The Case B program uses fill, not
set_value, but the executor's live program may use either, so both are
probed.)

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

## Probe 5: in-program retry logging (pick4 fixture)

Purpose: prove a program that retries internally produces a retry line
in the run log (plan section 5A). If the log shows no retry line, the
logging procedure is broken: STOP, fix the runbook logging rule, and
re-probe before run 1. Do not proceed on the assumption that retries
are logged.

P1 program (submit, expect ok:false on the first dom_act, then a
successful retry inside the same program):

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
first = dom_act(snap, [{"type": "assert", "selector": "#result", "text": "pick4-ok"}])
if not first["ok"]:
    snap = dom_observe(tab["id"])
    btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]
    clicked = dom_act(snap, [{"type": "click", "ref": btn["ref"]}])
    assert_state(clicked["ok"], "retry click failed")
    dom_assert(clicked["after"], selector="#result", text="pick4-ok")
```

The executor logs, for this probe: 1 act line (the failed assert),
1 retry line (the re-issued click after the failed assert), 1 act line
(the click). The probe log must show the retry line. The final end state
is #result "pick4-ok hello stranger" (the retry genuinely clicked the
button), which P2 confirms:

P2 program (submit, expect #result contains "pick4-ok"):

```python
tabs = dom_tabs()
tab = [t for t in tabs if t["url"] == "<FIXTURE_URL_PICK4>"][0]
snap = dom_observe(tab["id"])
dom_assert(snap, selector="#result", text="pick4-ok")
```

## Probe log

Write runs/preflight/preflight-log.jsonl, one line per submit:
{"ts", "probe": "click|fill|set_value|assert|retry-logging",
 "program": "P1|P2", "ok": <bool>, "error": "<exact error or null>",
 "dom_effect": <true|false, from the P2 check>,
 "retry_logged": <true|false, Probe 5 only>}.
All four preflight probes must show P1 failed with the bad-ref error
AND P2 showing no DOM effect. Probe 5 must show P1 retried internally
AND the retry line present in the log AND P2 showing the click effect.
Anything else stops the pilot under the stop-fix-reprobe rule above.

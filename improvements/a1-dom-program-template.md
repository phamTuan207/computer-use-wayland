# A1 DOM and multi-step code-exec program template

This template copies the D1 program from the design and a multi-step GUI sketch. DOM actions use snapshots returned by `dom_observe()` or the `after` snapshot returned by `dom_act()`. Terminal navigation remains a desktop action. The D1 program starts the managed browser with `dom_start()`, which waits (bounded, 10s) for the Chromium window to appear before returning, so the immediate `windows()` lookup after it is safe; do not add a sleep or retry in the program.

## D1 program

```python
started = dom_start()
assert_state(started["ok"], "dom start failed")
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

## Multi-step GUI sketch

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

The `printf` argument has literal `\\n` between output lines in the Python source, and the command ends with one `\n` so the terminal receives one Return. Keep both escapes as written when copying the program.

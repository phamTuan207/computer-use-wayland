#!/usr/bin/env python3
"""Y4 diagnostic probe: why is body invisible / scroll-into-view failing?
Opens a fresh tab to the q01 fixture, reports paint/focus state at
1s, 3s, 5s, then tries a real click. Read-only on user tabs; the test
tab is closed at the end.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_live import WD  # noqa: E402

URL = "http://127.0.0.1:8768/agy-q2/fixtures/test-01-whiteboard.html"

STATE_JS = """
const b = document.body;
const r = b.getBoundingClientRect();
const cs = getComputedStyle(b);
return JSON.stringify({
  rect: [r.x, r.y, r.width, r.height],
  display: cs.display, visibility: cs.visibility,
  hasFocus: document.hasFocus(),
  visibilityState: document.visibilityState,
  inner: [window.innerWidth, window.innerHeight],
  readyState: document.readyState,
  title: document.title.slice(0, 40)
});
"""


def main():
    with WD() as d:
        print("handles before:", len(d.handles()), flush=True)
        print("current title:", d.eval("return document.title"), flush=True)
        h = d.new_tab(URL)
        print("new tab handle:", h[:8], flush=True)
        for wait in (0, 2, 2):
            if wait:
                time.sleep(wait)
            print(f"state after +{wait}s extra:",
                  d.eval(STATE_JS), flush=True)
            print("  visible(body):", d.visible("body"), flush=True)
        try:
            d.click("#tool-rect")
            print("click #tool-rect: OK", flush=True)
        except Exception as exc:
            print("click #tool-rect: FAIL:", str(exc)[:300], flush=True)
        try:
            d.type_text("#input-board-title", "probe")
            print("type title: OK, value =",
                  d.eval("return document.getElementById('input-board-title').value"),
                  flush=True)
        except Exception as exc:
            print("type title: FAIL:", str(exc)[:300], flush=True)
    print("probe done", flush=True)


if __name__ == "__main__":
    main()

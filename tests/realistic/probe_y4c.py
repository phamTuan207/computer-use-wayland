#!/usr/bin/env python3
"""Y4 probe c: is the hidden body fixture-specific, URL-specific, or
tab-creation-level? And does reusing the existing about:blank tab
avoid it? Read-only except navigating the EMPTY about:blank tab.
"""
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from run_live import WD  # noqa: E402

VIS_JS = """
const b = document.body;
const cs = b ? getComputedStyle(b) : null;
return JSON.stringify({
  bodyVis: cs ? cs.visibility : null,
  inlineVis: b ? b.style.visibility : null,
  hasFocus: document.hasFocus(),
  visState: document.visibilityState,
  url: document.URL.slice(0, 60)
});
"""


def check(d, label):
    print(f"{label}: {d.eval(VIS_JS)}", flush=True)


def main():
    with WD() as d:
        handles = d.handles()
        blank = None
        for h in handles:
            try:
                d.switch(h)
                if d.eval("return document.URL") == "about:blank":
                    blank = h
                    break
            except Exception:
                # A tab with an open alert (user's tab) blocks eval;
                # skip it, never touch the alert.
                continue
        print("blank tab found:", bool(blank), flush=True)
        # 1. new tab to q02 fixture
        d.new_tab("http://127.0.0.1:8768/agy-q2/fixtures/test-02-recipe-app.html")
        time.sleep(1)
        check(d, "new tab q02 fixture")
        # 2. new tab to example.com
        d.new_tab("https://example.com")
        time.sleep(2)
        check(d, "new tab example.com")
        # 3. navigate the empty blank tab to q01 fixture
        if blank:
            d.switch(blank)
            d.goto("http://127.0.0.1:8768/agy-q2/fixtures/test-01-whiteboard.html")
            time.sleep(1)
            check(d, "blank tab navigated to q01")
            try:
                d.click("#tool-rect")
                print("click #tool-rect in reused tab: OK", flush=True)
            except Exception as exc:
                print("click #tool-rect in reused tab: FAIL:",
                      str(exc)[:200], flush=True)
            try:
                d.type_text("#input-board-title", "probe2")
                print("type title in reused tab: OK", flush=True)
            except Exception as exc:
                print("type title in reused tab: FAIL:", str(exc)[:200],
                      flush=True)
    print("probe c done", flush=True)


if __name__ == "__main__":
    main()

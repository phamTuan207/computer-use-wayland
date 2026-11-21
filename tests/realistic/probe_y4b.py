#!/usr/bin/env python3
"""Y4 probe b: is body visibility:hidden on ALL tabs or only new ones?
Read-only on user tabs (switch + eval only, no clicks, no navigation).
Also tries window.focus() in the test tab and re-checks.
"""
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from run_live import WD  # noqa: E402

VIS_JS = """
const b = document.body;
const r = b ? b.getBoundingClientRect() : {width: 0, height: 0};
const cs = b ? getComputedStyle(b) : null;
const hs = getComputedStyle(document.documentElement);
return JSON.stringify({
  bodyVis: cs ? cs.visibility : null,
  htmlVis: hs.visibility,
  rect: b ? [r.width, r.height] : null,
  hasFocus: document.hasFocus(),
  visState: document.visibilityState,
  inner: [window.innerWidth, window.innerHeight]
});
"""


def main():
    with WD() as d:
        handles = d.handles()
        print(f"handles: {len(handles)}", flush=True)
        orig = d.eval("return document.title")
        print("starting tab title:", orig, flush=True)
        hidden = 0
        for i, h in enumerate(handles):
            try:
                d.switch(h)
                title = d.eval("return document.title.slice(0, 50)")
                url = d.eval("return document.URL.slice(0, 80)")
                vis = d.eval(VIS_JS)
                print(f"[{i}] {title!r} {url} {vis}", flush=True)
                if '"bodyVis": "hidden"' in vis:
                    hidden += 1
            except Exception as exc:
                print(f"[{i}] ERROR {type(exc).__name__}: {str(exc)[:120]}",
                      flush=True)
        print(f"tabs with hidden body: {hidden}/{len(handles)}", flush=True)
        # Back to a test tab: open the fixture fresh, focus, re-check.
        h = d.new_tab(
            "http://127.0.0.1:8768/agy-q2/fixtures/test-01-whiteboard.html")
        print("new test tab:", h[:8], d.eval(VIS_JS), flush=True)
        d.eval("window.focus(); return 'focused';")
        time.sleep(2)
        print("after window.focus +2s:", d.eval(VIS_JS), flush=True)
        try:
            d.click("#tool-rect")
            print("click #tool-rect after focus: OK", flush=True)
        except Exception as exc:
            print("click #tool-rect after focus: FAIL:", str(exc)[:200],
                  flush=True)
    print("probe b done", flush=True)


if __name__ == "__main__":
    main()

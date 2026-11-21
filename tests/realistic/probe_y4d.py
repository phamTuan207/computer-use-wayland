#!/usr/bin/env python3
"""Y4 probe d: does switch-away-and-back un-hide a window/new tab?
Opens a new tab, switches to another existing tab, switches back,
re-checks visibility at 0/2/5s, tries a click.
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
  hasFocus: document.hasFocus(),
  visState: document.visibilityState
});
"""


def main():
    with WD() as d:
        handles = d.handles()
        other = None
        for h in handles:
            try:
                d.switch(h)
                if d.eval("return document.URL").startswith("https://"):
                    other = h
                    break
            except Exception:
                continue
        print("other tab:", bool(other), flush=True)
        h = d.new_tab("http://127.0.0.1:8768/agy-q2/fixtures/test-01-whiteboard.html")
        time.sleep(1)
        print("new tab fresh:", d.eval(VIS_JS), flush=True)
        if other:
            d.switch(other)
            time.sleep(1)
            d.switch(h)
            print("after switch away+back:", d.eval(VIS_JS), flush=True)
            time.sleep(2)
            print("after +2s:", d.eval(VIS_JS), flush=True)
            time.sleep(3)
            print("after +5s:", d.eval(VIS_JS), flush=True)
        try:
            d.click("#tool-rect")
            print("click #tool-rect: OK", flush=True)
        except Exception as exc:
            print("click #tool-rect: FAIL:", str(exc)[:150], flush=True)
    print("probe d done", flush=True)


if __name__ == "__main__":
    main()

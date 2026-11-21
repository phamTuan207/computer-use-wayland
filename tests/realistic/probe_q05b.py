#!/usr/bin/env python3
"""Probe 2: ancestor chain visibility for q05, and same check on q01."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

CHAIN_JS = """
const el = document.querySelector(arguments[0]);
if (!el) return 'NO-EL';
const out = [];
let n = el;
while (n) {
  const cs = getComputedStyle(n);
  out.push((n.tagName || '?') + '#' + (n.id || '') +
           ' vis=' + cs.visibility + ' disp=' + cs.display);
  n = n.parentElement;
}
return out;
"""

httpd, base = start_server()
print("base", base, flush=True)
try:
    with WD() as d:
        d.new_tab(base + "/agy-q/fixtures/test-05-file-search.html")
        print("Q05 CHAIN", d.eval(CHAIN_JS, ["#input-file-search"]), flush=True)
        print("Q05 innerTextLen",
              d.eval("return document.body.innerText.length"), flush=True)
        d.new_tab(base + "/agy-q/fixtures/test-01-music-player.html")
        print("Q01 CHAIN", d.eval(CHAIN_JS, ["#input-library-search"]), flush=True)
        print("Q01 innerTextLen",
              d.eval("return document.body.innerText.length"), flush=True)
        print("Q01 input rect", d.eval(
            "const el=document.querySelector('#input-library-search');"
            "const r=el.getBoundingClientRect();"
            "return {w:r.width,h:r.height,"
            " vis:getComputedStyle(el).visibility};"), flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

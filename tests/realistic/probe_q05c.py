#!/usr/bin/env python3
"""Probe 3: is body hidden on the CURRENT (pre-existing) tab too?
Also dump Zen window state via hyprctl separately."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

httpd, base = start_server()
try:
    with WD() as d:
        print("CURRENT HANDLE", d._wd("GET", d._s("/window"))["value"][:8],
              flush=True)
        print("CURRENT URL", d.eval("return location.href;"), flush=True)
        print("CURRENT BODY VIS",
              d.eval("return getComputedStyle(document.body).visibility;"),
              flush=True)
        print("CURRENT innerTextLen",
              d.eval("return document.body ? document.body.innerText.length : -1"),
              flush=True)
        print("CURRENT visState",
              d.eval("return document.visibilityState;"), flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

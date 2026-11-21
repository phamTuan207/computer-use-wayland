#!/usr/bin/env python3
"""Probe 4: does body-hidden on a new Marionette tab clear with time,
with window.focus(), or with an explicit re-switch?"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

httpd, base = start_server()
try:
    with WD() as d:
        handle = d.new_tab(base + "/agy-q/fixtures/test-05-file-search.html")
        for label in ("t+0s",):
            print(label, d.eval(
                "return getComputedStyle(document.body).visibility;"), flush=True)
        time.sleep(5)
        print("t+5s", d.eval(
            "return getComputedStyle(document.body).visibility;"), flush=True)
        d.eval("window.focus();")
        time.sleep(1)
        print("after window.focus",
              d.eval("return getComputedStyle(document.body).visibility;"),
              flush=True)
        print("window rect", d._wd("GET", d._s("/window/rect"))["value"],
              flush=True)
        # Re-switch away and back.
        handles = d.handles()
        print("handles", len(handles), flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

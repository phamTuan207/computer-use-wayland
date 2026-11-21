#!/usr/bin/env python3
"""Probe: why is the q05 fixture page unrendered (innerText empty,
input not interactable) in solo runs but fine inside the full run."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

httpd, base = start_server()
print("base", base, flush=True)
try:
    with WD() as d:
        handle = d.new_tab(base + "/agy-q/fixtures/test-05-file-search.html")
        print("HANDLE", handle[:8], flush=True)
        print("HANDLES", len(d.handles()), flush=True)
        print("STATE", d.eval(
            "return {vis: document.visibilityState, focus: document.hasFocus(),"
            " w: window.innerWidth, h: window.innerHeight,"
            " title: document.title,"
            " readyState: document.readyState,"
            " innerTextLen: document.body.innerText.length,"
            " bodyHTMLLen: document.body.innerHTML.length};"), flush=True)
        print("INPUT RECT", d.eval(
            "const el=document.querySelector('#input-file-search');"
            "const r=el.getBoundingClientRect();"
            "const cs=getComputedStyle(el);"
            "return {x:r.x,y:r.y,w:r.width,h:r.height,"
            " display:cs.display, visibility:cs.visibility};"), flush=True)
        print("ALL TABS", d.eval(
            "return document.title;"), flush=True)
        # What is the current tab's URL?
        print("URL", d.eval("return location.href;"), flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

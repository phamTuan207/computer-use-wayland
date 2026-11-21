#!/usr/bin/env python3
"""Probe: why is the Q04 wiki link NOT-FOUND after Save + Preview tab."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

httpd, base = start_server()
print("base", base, flush=True)
try:
    with WD() as d:
        d.new_tab(base + "/agy-q/fixtures/test-04-notes-app.html")
        d.eval("localStorage.clear()")
        d.refresh()
        d.click("#btn-new-note")
        d.type_text("#input-note-title", "Memory Tiering RFC")
        d.type_text("#input-note-tags", "rfc, performance, memory")
        body = ("# Memory Tiering Architecture\n\n"
                "This proposal integrates tiered RAM and CXL memory.\n\n"
                "Related: [[Storage Engine]] and [[Security Model]].")
        d.type_text("#textarea-note-body", body)
        print("BODY AFTER TYPE:",
              d.eval("return document.querySelector('#textarea-note-body').value"),
              flush=True)
        d.click("#btn-save-note")
        print("PREVIEW HTML AFTER SAVE:",
              d.eval("return document.querySelector('#rendered-markdown-content').innerHTML"),
              flush=True)
        print("LINK QUERY AFTER SAVE:",
              d.eval("return document.querySelector('[id=\"link-note-Storage Engine\"]') ? 'FOUND' : 'NOT-FOUND'"),
              flush=True)
        d.click("#tab-preview-mode")
        print("PREVIEW PANE DISPLAY:",
              d.eval("return document.querySelector('#pane-preview-view').style.display"),
              flush=True)
        print("LINK QUERY AFTER PREVIEW TAB:",
              d.eval("return document.querySelector('[id=\"link-note-Storage Engine\"]') ? 'FOUND' : 'NOT-FOUND'"),
              flush=True)
        print("ALL IDS IN PREVIEW:",
              d.eval("return [...document.querySelectorAll('#rendered-markdown-content [id]')].map(e=>e.id)"),
              flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

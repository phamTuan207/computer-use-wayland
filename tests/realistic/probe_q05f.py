#!/usr/bin/env python3
"""Probe 6: does forcing body visibility visible make a new tab
interactive again? (Workaround test for the hidden-body state.)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

httpd, base = start_server()
try:
    with WD() as d:
        d.new_tab(base + "/agy-q/fixtures/test-05-file-search.html")
        print("BEFORE", d.eval(
            "return {vis: getComputedStyle(document.body).visibility,"
            " innerLen: document.body.innerText.length};"), flush=True)
        d.eval("document.body.style.visibility = 'visible';")
        print("AFTER OVERRIDE", d.eval(
            "return {vis: getComputedStyle(document.body).visibility,"
            " innerLen: document.body.innerText.length};"), flush=True)
        # Real Marionette click on the search input (the exact op that failed).
        d.click("#input-file-search")
        print("CLICK INPUT OK", flush=True)
        d.type_text("#input-file-search", "compositor")
        print("TYPE OK, value=",
              d.eval("return document.querySelector('#input-file-search').value"),
              flush=True)
        print("ROWS", d.eval(
            "return [...document.querySelectorAll('#results-table-body tr')].length"),
            flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

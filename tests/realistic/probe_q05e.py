#!/usr/bin/env python3
"""Probe 5: find the source of body visibility:hidden on a new tab."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, start_server

FIND_JS = """
const out = {};
out.bodyInline = document.body.getAttribute('style');
out.bodyClass = document.body.className;
out.htmlClass = document.documentElement.className;
out.htmlInline = document.documentElement.getAttribute('style');
out.sheets = [...document.styleSheets].map(s => {
  try { return (s.href || '(inline)') + ' rules=' + s.cssRules.length; }
  catch (e) { return (s.href || '(inline)') + ' ERR ' + e.name; }
});
out.matchingRules = [];
for (const s of document.styleSheets) {
  let rules;
  try { rules = s.cssRules; } catch (e) { continue; }
  for (const r of rules) {
    try {
      if (r.style && r.style.visibility === 'hidden' &&
          document.body.matches(r.selectorText)) {
        out.matchingRules.push(r.selectorText + ' @ ' + (s.href || 'inline'));
      }
    } catch (e) {}
  }
}
out.bodyVisibility = getComputedStyle(document.body).visibility;
out.htmlVisibility = getComputedStyle(document.documentElement).visibility;
return out;
"""

httpd, base = start_server()
try:
    with WD() as d:
        d.new_tab(base + "/agy-q/fixtures/test-05-file-search.html")
        print("NEW TAB", d.eval(FIND_JS), flush=True)
finally:
    if httpd is not None:
        httpd.shutdown()
print("PROBE DONE", flush=True)

#!/usr/bin/env python3
"""F3b Arm E: full close3 reproduction.

A/B/C/D all passed, so the trigger (if any) is the COMBINATION. This arm
mirrors close3.py exactly, with fresh tabs:
  1. window/new sacrificial tab, switch to it (sac).
  2. Close the BiDi-navigated example.com tab + every blank tab via
     switch + DELETE /window (the doomed set, excluding sac).
  3. Switch back to sac.
  4. Exit (session DELETE with the sacrificial tab current).
Then the caller probes. If this wedges the slot, the trigger is the
combination; if it passes, the 22:56 wedge needed state outside A-E
(e.g. the leftover sacrificial tabs from the earlier runs).
"""
import sys
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession, ZenDomError


def full_tabs(z):
    handles = z._wd("GET", f"/session/{z.session}/window/handles")["value"]
    cur = z._wd("GET", f"/session/{z.session}/window")["value"]
    out = []
    for h in handles:
        try:
            z._wd("POST", f"/session/{z.session}/window", {"handle": h})
            out.append({"handle": h,
                        "title": z._wd("GET", f"/session/{z.session}/title")["value"],
                        "url": z._wd("GET", f"/session/{z.session}/url")["value"]})
        except (ZenDomError, TimeoutError, OSError) as e:
            print("ARM-E scan skip", h[:8], str(e)[:120], flush=True)
    z._wd("POST", f"/session/{z.session}/window", {"handle": cur})
    return out


with ZenSession() as z:
    print("ARM-E session", z.session[:8], flush=True)
    new = z._wd("POST", f"/session/{z.session}/window/new", {"type": "tab"})
    sac = new["value"]["handle"]
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    print("ARM-E sac", sac[:8], flush=True)
    tabs = full_tabs(z)
    print("ARM-E BEFORE", len(tabs), flush=True)
    doomed = [t for t in tabs if t["handle"] != sac and (
        (t["title"] == "Example Domain" and t["url"] == "https://example.com/")
        or (t["title"] == "" and t["url"] == "about:blank"))]
    print("ARM-E DOOMED", len(doomed),
          [(t["title"], t["url"]) for t in doomed], flush=True)
    for tab in doomed:
        z._wd("POST", f"/session/{z.session}/window", {"handle": tab["handle"]})
        z._wd("DELETE", f"/session/{z.session}/window", {})
        print("ARM-E CLOSED", tab["title"], tab["url"], flush=True)
    z._wd("POST", f"/session/{z.session}/window", {"handle": sac})
    after = full_tabs(z)
    print("ARM-E AFTER", len(after), [t["title"] for t in after], flush=True)
    print("ARM-E exiting, DELETE with sac current", flush=True)
print("ARM-E done", flush=True)

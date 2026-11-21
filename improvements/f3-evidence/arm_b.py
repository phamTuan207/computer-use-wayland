#!/usr/bin/env python3
"""F3b Arm B: window/new blank tab current, then Marionette session DELETE.

No BiDi anywhere in this arm. The session creates a blank tab via
window/new, switches to it, then exits (session DELETE with the
window/new-created blank tab current). The caller runs probe_session.py
after this to test the slot.
"""
import sys
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession

with ZenSession() as z:
    print("ARM-B session", z.session[:8], flush=True)
    new = z._wd("POST", f"/session/{z.session}/window/new", {"type": "tab"})
    h = new["value"]["handle"]
    print("ARM-B new blank handle", h[:8], flush=True)
    z._wd("POST", f"/session/{z.session}/window", {"handle": h})
    now = z._wd("GET", f"/session/{z.session}/window")["value"]
    print("ARM-B current now", now[:8], "is-new", now == h, flush=True)
    print("ARM-B exiting, DELETE with window/new blank current (no BiDi)", flush=True)
print("ARM-B done", flush=True)

#!/usr/bin/env python3
"""F3b Arm D (retry): Marionette DELETE /window tab close.

Attempt 1 died in the handle scan: a POST /window switch hung past the
10s timeout, and the raw TimeoutError escaped the ZenDomError-only
try/except. This retry targets handles[8] directly (BiDi index 8 is the
example.com tab; handle order == tab order, proven in Arm A run 3), verifies
the URL, and only scans as a fallback with TimeoutError caught per handle.
"""
import sys
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession, ZenDomError

TARGET_URL = "https://example.com/"

with ZenSession() as z:
    print("ARM-D session", z.session[:8], flush=True)
    handles = z._wd("GET", f"/session/{z.session}/window/handles")["value"]
    print("ARM-D handles", len(handles), flush=True)
    target = None
    if len(handles) > 8:
        try:
            z._wd("POST", f"/session/{z.session}/window", {"handle": handles[8]})
            url = z._wd("GET", f"/session/{z.session}/url")["value"]
            print("ARM-D handles[8] url", url, flush=True)
            if url == TARGET_URL:
                target = handles[8]
        except (ZenDomError, TimeoutError, OSError) as e:
            print("ARM-D handles[8] switch failed", str(e)[:200], flush=True)
    if target is None:
        print("ARM-D scanning handles with 10s timeout", flush=True)
        z.timeout_s = 10
        for h in handles:
            try:
                z._wd("POST", f"/session/{z.session}/window", {"handle": h})
                url = z._wd("GET", f"/session/{z.session}/url")["value"]
                if url == TARGET_URL:
                    target = h
                    print("ARM-D found example", h[:8], flush=True)
                    break
            except (ZenDomError, TimeoutError, OSError) as e:
                print("ARM-D scan skip", h[:8], str(e)[:120], flush=True)
        z.timeout_s = 30
    if target is None:
        print("ARM-D ABORT: no example.com tab")
        sys.exit(2)
    z._wd("POST", f"/session/{z.session}/window", {"handle": target})
    z._wd("DELETE", f"/session/{z.session}/window", {})
    print("ARM-D DELETE /window on example tab done", flush=True)
    after = z._wd("GET", f"/session/{z.session}/window/handles")["value"]
    print("ARM-D handles after close", len(after), flush=True)
    print("ARM-D exiting, session DELETE", flush=True)
print("ARM-D done", flush=True)

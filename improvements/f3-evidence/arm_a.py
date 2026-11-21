#!/usr/bin/env python3
"""F3b Arm A (retry): BiDi-navigated tab current, then Marionette session DELETE.

Attempt 1 died in the full tab scan: switching to one handle hung past the
30s _wd timeout. This retry avoids the full scan: the BiDi tab order and the
Marionette handle order are both tab order, and the BiDi-navigated
example.com tab is BiDi index 8, so try handles[8] first, verify its URL,
and only scan (with a short per-call timeout and per-handle try/except) if
that misses. Then DELETE the session with the example tab current.
"""
import sys
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession, ZenDomError

TARGET_URL = "https://example.com/"

with ZenSession() as z:
    print("ARM-A session", z.session[:8], flush=True)
    handles = z._wd("GET", f"/session/{z.session}/window/handles")["value"]
    print("ARM-A handles", len(handles), flush=True)
    target = None
    if len(handles) > 8:
        try:
            z._wd("POST", f"/session/{z.session}/window", {"handle": handles[8]})
            url = z._wd("GET", f"/session/{z.session}/url")["value"]
            print("ARM-A handles[8] url", url, flush=True)
            if url == TARGET_URL:
                target = handles[8]
        except ZenDomError as e:
            print("ARM-A handles[8] switch failed", str(e)[:200], flush=True)
    if target is None:
        print("ARM-A scanning handles with 10s timeout", flush=True)
        z.timeout_s = 10
        for h in handles:
            try:
                z._wd("POST", f"/session/{z.session}/window", {"handle": h})
                url = z._wd("GET", f"/session/{z.session}/url")["value"]
                print("ARM-A scan", h[:8], url, flush=True)
                if url == TARGET_URL:
                    target = h
                    break
            except ZenDomError as e:
                print("ARM-A scan skip", h[:8], str(e)[:120], flush=True)
        z.timeout_s = 30
    if target is None:
        print("ARM-A ABORT: no example.com tab")
        sys.exit(2)
    z._wd("POST", f"/session/{z.session}/window", {"handle": target})
    now = z._wd("GET", f"/session/{z.session}/window")["value"]
    print("ARM-A current now", now[:8], "is-example", now == target, flush=True)
    print("ARM-A exiting, DELETE with BiDi-navigated tab current", flush=True)
print("ARM-A done", flush=True)

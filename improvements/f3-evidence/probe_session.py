#!/usr/bin/env python3
"""F3b slot probe: two consecutive Marionette session creates.

PROBE1 CREATE is the pass/fail signal for the slot. Each attempt's exit
DELETEs its session, so PROBE2 CREATE also tests whether a plain session
DELETE wedges the slot. Exit 0 only if both CREATEs succeed.
"""
import sys
sys.path.insert(0, "/tmp/zen_tab_cleanup")
from zen_dom import ZenSession, ZenDomError


def attempt(tag):
    try:
        with ZenSession() as z:
            print(tag, "CREATE OK", z.session[:8], flush=True)
            return True
    except ZenDomError as e:
        print(tag, "CREATE FAIL", str(e)[:300], flush=True)
        return False


ok1 = attempt("PROBE1")
ok2 = attempt("PROBE2")
print("PROBE RESULT", ok1, ok2, flush=True)
sys.exit(0 if (ok1 and ok2) else 1)

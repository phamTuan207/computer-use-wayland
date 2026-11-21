#!/usr/bin/env python3
"""Y8 E1 pre-flight diagnose: verify a fresh tab renders body-visible
before an executor starts. Adapted from Y4b's diagnose-first design.

Usage: worker-y8-preflight.py <arm>   (arm = a or b)
Writes /tmp/e1/preflight-<arm>.json and exits:
  0 = VISIBLE, or FLAGGED (visible only after tz-hidden removal)
  2 = INFRA-BLOCKED (hidden after the recovery ladder)
  3 = FIXTURE_FAILURE (fixture itself failed to load)
Never touches a user tab. Never uses a real click as a recovery probe.
The tz-hidden removal, if used, runs on the test tab only, test origin
only, and is logged as an intervention in the output JSON.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

ARM = sys.argv[1] if len(sys.argv) > 1 else "?"
OUT = f"/tmp/e1/preflight-{ARM}.json"
FIXTURE = "http://127.0.0.1:8767/test-05-contact-book.html"
STEP = "/tmp/e1/step.sh"

DIAGNOSE_JS = """(function(){
  var cs = getComputedStyle(document.body);
  var hs = getComputedStyle(document.documentElement);
  var r = document.body.getBoundingClientRect();
  var cc = document.querySelector('#contacts-count');
  return {
    readyState: document.readyState,
    url: location.href,
    htmlClass: document.documentElement.className,
    htmlClassList: Array.from(document.documentElement.classList),
    htmlInline: document.documentElement.getAttribute('style') || '',
    bodyClass: document.body.className,
    bodyInline: document.body.getAttribute('style') || '',
    bodyVis: cs.visibility, bodyOpacity: cs.opacity, bodyDisplay: cs.display,
    htmlVis: hs.visibility,
    transition: cs.transitionProperty + ' ' + cs.transitionDuration + ' ' + cs.transitionDelay,
    rect: {x: r.x, y: r.y, w: r.width, h: r.height},
    innerLen: document.body.innerText.length,
    hasFocus: document.hasFocus(),
    visState: document.visibilityState,
    countText: cc ? cc.textContent.trim() : null
  };
})()"""

REMOVE_TZ_JS = """(function(){
  document.documentElement.classList.remove('tz-hidden');
  document.documentElement.style.removeProperty('--zen-logo-path');
  return document.documentElement.className;
})()"""


def ts():
    return datetime.now(timezone.utc).astimezone().strftime("%F %T %Z")


def step(cmd):
    p = subprocess.run([STEP, json.dumps(cmd)], capture_output=True,
                       text=True, timeout=40)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "error": f"unparsable step output: {p.stdout[:200]}"}


def classify(snap):
    if snap.get("countText") is None:
        return "FIXTURE_FAILURE"
    if snap.get("bodyVis") == "visible" and snap.get("bodyOpacity") != "0":
        return "VISIBLE"
    if "tz-hidden" in (snap.get("htmlClassList") or []):
        return "TZ_STUCK_V1"
    return "OTHER_HIDDEN"


def main():
    report = {"arm": ARM, "started": ts(), "snapshots": [],
              "intervention": None, "verdict": None}
    r = step({"cmd": "new_session"})
    report["new_session"] = r
    if not r.get("ok"):
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = "new_session failed"
        report["ended"] = ts()
        json.dump(report, open(OUT, "w"), indent=2)
        return 2
    r = step({"cmd": "new_tab", "url": FIXTURE})
    report["new_tab"] = r
    if not r.get("ok"):
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = "new_tab failed"
        report["ended"] = ts()
        json.dump(report, open(OUT, "w"), indent=2)
        return 2
    time.sleep(1.0)
    snap = step({"cmd": "eval", "js": DIAGNOSE_JS})
    snap_result = snap.get("result") if snap.get("ok") else None
    if snap_result is None:
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = f"diagnose eval failed: {snap}"
        report["ended"] = ts()
        json.dump(report, open(OUT, "w"), indent=2)
        step({"cmd": "close_tab"})
        step({"cmd": "delete_session"})
        return 2
    report["snapshots"].append({"t": ts(), "label": "initial", "snap": snap_result})
    cls = classify(snap_result)
    # Recovery ladder, 8 s total budget: poll 250 ms up to 2.0 s first.
    if cls != "VISIBLE" and cls != "FIXTURE_FAILURE":
        for _ in range(8):
            time.sleep(0.25)
            s2 = step({"cmd": "eval", "js": DIAGNOSE_JS})
            s2r = s2.get("result") if s2.get("ok") else None
            if s2r is None:
                break
            report["snapshots"].append({"t": ts(), "label": "poll", "snap": s2r})
            cls = classify(s2r)
            if cls == "VISIBLE":
                break
        if cls == "TZ_STUCK_V1":
            rm = step({"cmd": "eval", "js": REMOVE_TZ_JS})
            report["intervention"] = {"action": "removed tz-hidden + --zen-logo-path on test tab only",
                                      "t": ts(), "result": rm}
            time.sleep(0.5)
            s3 = step({"cmd": "eval", "js": DIAGNOSE_JS})
            s3r = s3.get("result") if s3.get("ok") else None
            if s3r is not None:
                report["snapshots"].append({"t": ts(), "label": "after-removal", "snap": s3r})
                cls = classify(s3r)
    if cls == "VISIBLE":
        report["verdict"] = "FLAGGED" if report["intervention"] else "VISIBLE"
        code = 0
    elif cls == "FIXTURE_FAILURE":
        report["verdict"] = "FIXTURE_FAILURE"
        code = 3
    else:
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = f"still {cls} after recovery ladder"
        code = 2
    step({"cmd": "close_tab"})
    step({"cmd": "delete_session"})
    report["ended"] = ts()
    json.dump(report, open(OUT, "w"), indent=2)
    print(json.dumps({"arm": ARM, "verdict": report["verdict"], "class": cls}))
    return code


if __name__ == "__main__":
    sys.exit(main())

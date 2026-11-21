#!/usr/bin/env python3
"""Y8 E1 pre-flight diagnose: verify a fresh tab renders body-visible
before an executor starts. FROZEN v2 (Worker Y8).

Usage: worker-y8-preflight.py <arm>   (arm = a or b)
Writes /tmp/e1/preflight-<arm>.json and exits:
  0 = VISIBLE, or FLAGGED (tab cleared by the extension's own removal
      during the poll, no manual intervention)
  2 = INFRA-BLOCKED (hidden after the recovery ladder, or visible only
      after a manual removal, which proves the window is unhealthy)
  3 = FIXTURE_FAILURE (fixture itself failed to load)

Removal is DIAGNOSTIC ONLY. A manual-removal-assisted visibility NEVER
authorizes a start. The executor's own tab gets its own diagnose (in the
executor briefs); this pre-flight gate diagnoses a sacrificial tab and
never measures the tab that does the work.

Never touches a user tab. Never uses a real click as a recovery probe.
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
DEADLINE_S = 8.0
POLL_S = 2.0

DIAGNOSE_JS = """return (function(){
  var cs = getComputedStyle(document.body);
  var hs = getComputedStyle(document.documentElement);
  var r = document.body.getBoundingClientRect();
  var cc = document.querySelector("#contacts-count");
  return {
    readyState: document.readyState,
    url: location.href,
    htmlClass: document.documentElement.className,
    htmlClassList: Array.from(document.documentElement.classList),
    htmlInline: document.documentElement.getAttribute("style") || '',
    bodyClass: document.body.className,
    bodyInline: document.body.getAttribute("style") || '',
    bodyVis: cs.visibility, bodyOpacity: cs.opacity, bodyDisplay: cs.display,
    htmlVis: hs.visibility,
    transition: cs.transitionProperty + " " + cs.transitionDuration + " " + cs.transitionDelay,
    rect: {x: r.x, y: r.y, w: r.width, h: r.height},
    innerLen: document.body.innerText.length,
    hasFocus: document.hasFocus(),
    visState: document.visibilityState,
    countText: cc ? cc.textContent.trim() : null
  };
})()"""

# Exact mirror of removeLoadingScreen: remove the class AND the inline
# --zen-logo-path property it set. Diagnostic use only.
REMOVE_TZ_JS = """return (function(){
  document.documentElement.classList.remove("tz-hidden");
  document.documentElement.style.removeProperty("--zen-logo-path");
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
    if (snap.get("bodyVis") == "visible"
            and snap.get("bodyOpacity") != "0"
            and snap.get("bodyDisplay") != "none"):
        return "VISIBLE"
    if "tz-hidden" in (snap.get("htmlClassList") or []):
        return "TZ_STUCK_V1"
    return "OTHER_HIDDEN"


def geckodriver_ps():
    try:
        p = subprocess.run(["ps", "-eo", "pid,etime,cmd"], capture_output=True,
                           text=True, timeout=10)
        return [l for l in p.stdout.splitlines() if "geckodriver" in l]
    except Exception:
        return []


def main():
    t_start = time.monotonic()
    report = {"arm": ARM, "started": ts(), "snapshots": [],
              "intervention": None, "verdict": None}

    def finish(code):
        report["ended"] = ts()
        if code == 2:
            report["geckodriver_ps"] = geckodriver_ps()
        json.dump(report, open(OUT, "w"), indent=2)
        print(json.dumps({"arm": ARM, "verdict": report["verdict"]}))
        return code

    def cleanup():
        step({"cmd": "close_tab"})
        step({"cmd": "delete_session"})

    r = step({"cmd": "new_session"})
    report["new_session"] = r
    if not r.get("ok"):
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = "new_session failed"
        return finish(2)
    r = step({"cmd": "new_tab", "url": FIXTURE})
    report["new_tab"] = r
    if not r.get("ok"):
        # P1 fix: never leak the session when new_tab fails.
        step({"cmd": "delete_session"})
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = "new_tab failed"
        return finish(2)
    time.sleep(1.0)
    snap = step({"cmd": "eval", "js": DIAGNOSE_JS})
    snap_result = snap.get("result") if snap.get("ok") else None
    if snap_result is None:
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = f"diagnose eval failed: {snap}"
        cleanup()
        return finish(2)
    report["snapshots"].append({"t": ts(), "label": "initial", "snap": snap_result})
    cls = classify(snap_result)
    if cls == "FIXTURE_FAILURE":
        report["verdict"] = "FIXTURE_FAILURE"
        cleanup()
        return finish(3)
    # Poll 250 ms up to 2.0 s for the extension's own removal, inside the
    # 8 s wall-clock deadline (P2 fix).
    if cls != "VISIBLE":
        poll_end = time.monotonic() + POLL_S
        while time.monotonic() < poll_end:
            if time.monotonic() - t_start > DEADLINE_S:
                break
            time.sleep(0.25)
            s2 = step({"cmd": "eval", "js": DIAGNOSE_JS})
            s2r = s2.get("result") if s2.get("ok") else None
            if s2r is None:
                break
            report["snapshots"].append({"t": ts(), "label": "poll", "snap": s2r})
            cls = classify(s2r)
            if cls == "VISIBLE":
                break
        if cls == "VISIBLE":
            # Cleared by the extension itself during the poll: FLAGGED, may start.
            report["verdict"] = "FLAGGED"
            cleanup()
            return finish(0)
        if cls == "TZ_STUCK_V1":
            # Diagnostic removal only: proves V1, never authorizes a start.
            rm = step({"cmd": "eval", "js": REMOVE_TZ_JS})
            report["intervention"] = {"action": "DIAGNOSTIC ONLY: removed tz-hidden + --zen-logo-path on test tab",
                                      "t": ts(), "result": rm}
            time.sleep(0.6)
            s3 = step({"cmd": "eval", "js": DIAGNOSE_JS})
            s3r = s3.get("result") if s3.get("ok") else None
            if s3r is not None:
                report["snapshots"].append({"t": ts(), "label": "after-diagnostic-removal", "snap": s3r})
                cls_after = classify(s3r)
                if cls_after == "VISIBLE":
                    report["verdict"] = "INFRA-BLOCKED"
                    report["reason"] = "V1-CONFIRMED: manual removal unhid this tab, window unhealthy, arm must not start"
                else:
                    report["verdict"] = "INFRA-BLOCKED"
                    report["reason"] = f"still {cls_after} after diagnostic removal"
            else:
                report["verdict"] = "INFRA-BLOCKED"
                report["reason"] = "re-diagnose after diagnostic removal failed"
            cleanup()
            return finish(2)
        report["verdict"] = "INFRA-BLOCKED"
        report["reason"] = f"still {cls} after poll"
        cleanup()
        return finish(2)
    report["verdict"] = "VISIBLE"
    cleanup()
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())

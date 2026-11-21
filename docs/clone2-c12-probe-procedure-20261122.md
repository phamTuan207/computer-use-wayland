# C12 live probe procedure: mozInnerScreenX/Y, absolute or window-relative?

Date written: 2026-11-22. Status: PROCEDURE ONLY. Do not run live until the
live lane is free (BASELINE2 finished). Run on the laptop, never on the
clone2 VM (no Zen, no Hyprland here).

## 1. What is disputed, and why it matters

C12 requires the DOM-to-screen conversion to use Hyprland window geometry
plus devicePixelRatio plus viewport origin, cross-checked against AT-SPI
screen extents. Council C1 and C2 both concluded C12 is NOT satisfied:

- C1: improvements/worker-click2-c1-review-log.md:68-78 (C12 adjudication,
  NOT SATISFIED).
- C2: improvements/worker-click2-c2-review-log.md, section "C12
  adjudication" (02:58) and required fix F2 (03:01).

The amend code under test:

- scripts/zen_dom.py:367-380, viewport_origin(), returns
  [window.mozInnerScreenX, window.mozInnerScreenY] and documents it as
  "the viewport origin in screen coordinates (CSS px)".
- scripts/fastpath.py:169, dom_rect_to_image_point(meta, rect, origin):
  screen = viewport_origin + rect center, then image = (screen - region
  origin) * image_size / region size. The linear map itself is correct
  and tested 7/7 synthetic; only the origin input is disputed.
- scripts/dom_act.py: ground_input() consumes the same origin for every
  DOM-first click, so a wrong origin breaks every DOM-first click, not
  one call site.

The counter-evidence:

- docs/calibration-e2-report.md:21, measured live on the laptop
  2026-11-21: mozInnerScreenX/Y in this Zen build are WINDOW-relative
  (240, 8), not absolute screen coords. The truth table is window-relative
  CSS px; add the window origin (2509, 914) for screen px.

If the E2 report is right, the amend misplaces every point by the window
offset (about 2500 px in x on the E2 geometry), and dom_rect_to_image_point
fails closed (ValueError, point outside the observed image) on every live
Zen call: loud, so no mis-click, but the DOM-first path is dead on
arrival. If the amend is right, the E2 reading was wrong for this build
and C12 is done as-is. This probe decides between the two with live
clicks where the geometry allows them, and with the arithmetic check
plus Case B confirmation clicks where Case A is unclickable (section 6,
Branch 2), not with more code reading.

Two findings that are NOT evidence against the amend, do not cite them:

- The ZT-B line "mozInnerScreenX returned null via Marionette eval" is
  explained in the same log (line 15) by the eval omitting `return`.
  The amend's viewport_origin includes an explicit `return`, so that
  finding does not apply. A null return from the amend's own
  viewport_origin would be new evidence, record it as outcome C below.
- The synthetic 7/7 tests (tests/test_zen_dom.py:418-428,
  tests/test_pick4_fastpath.py:482-560) assume the origin IS the absolute
  window origin [2533, 914]. They pass either way and prove only the
  linear map, not the origin semantics.

## 2. Prerequisites

- Live lane free. BASELINE2 must be finished. No other live run may hold
  the Zen remote session while this probe runs: Firefox allows exactly
  one active remote session per browser instance across protocols
  (BiDi session.new fails with "Maximum number of active sessions"
  while a Marionette session is active, and vice versa).
- Zen running on the laptop with --remote-debugging-port=9222
  --marionette (Marionette 2828, the zen_dom.py default).
- Repo checkout on the laptop, branch todolist-push, up to date.
  The probe reads the amend code from that branch.
- The session guardian may be down (it failed to start on the E2
  checkout). That does not block this probe: the click steps use
  /tmp/c12_probe_click.py (section 7), a small driver modeled on
  the direct pointer path from tests/e2_direct_clicks.py, which
  needs no session. Record which path was used.
- Environment for hyprctl and the pointer binary: XDG_RUNTIME_DIR,
  WAYLAND_DISPLAY and HYPRLAND_INSTANCE_SIGNATURE as in
  tests/e2_direct_clicks.py (ENV block). The pointer binary is
  native/pointer in the repo checkout.
- Zen window state for the probe: sidebar visible, not fullscreen,
  on the same monitor as the E2 run if possible (eDP-2). Record the
  workspace and whether the window is floating or tiled.

## 3. Step 0: lane check and baseline record

1. Confirm no live run is active (ask the coordinator or check the
   lane status; do not start if BASELINE2 or any benchmark is running).
2. Record: date and time (+07), runner name, Zen PID
   (pgrep -af zen or ps), repo HEAD (git rev-parse HEAD on
   todolist-push), zen_dom.py and fastpath.py HEADs.
3. Open a fresh log file /tmp/c12-probe-20261122.log. Every command
   below appends its full output there with a wall-clock timestamp.
   The log is committed with the results (Step 6, section 9): copy it
   into the repo as improvements/c12-probe-20261122.log before
   committing.

## 4. Step 1: window origin and monitor geometry from hyprctl

Run, and record every value:

```
hyprctl -j clients | python3 -c "import json,sys; [print(c['address'], c['class'], c['title'], c['at'], c['size']) for c in json.load(sys.stdin) if 'zen' in c.get('class','').lower()]"
hyprctl -j monitors
hyprctl -j activewindow
```

Record: Zen window address (re-read it immediately before the clicks
in step 4.1, it goes stale, E2 finding 4), window origin [win_x, win_y]
(the `at` field), window size [win_w, win_h], monitor name, monitor
box [x, y, w, h] in logical px, monitor scale, monitor transform,
workspace id. Record the FULL monitor layout, every monitor from
`hyprctl -j monitors`, not just the Zen window's monitor: name, box,
scale, transform for each. Identify which monitor contains the Zen
window; that is the only monitor a click point may fall on.

Clickable-point rule, binding on every click step below: a candidate
point may be clicked only if it falls inside the Zen window rect AND
inside the box of the monitor that contains the Zen window. A point
that falls on a different monitor must NOT be clicked, even if it
falls inside that other monitor's box: the pointer would land on
another monitor's desktop or windows, and the cursorpos check cannot
prevent that, it only confirms the pointer reached the intended
coordinates. A point that falls outside every monitor box has no
defined target and must not be clicked either.

Expected values from the E2 geometry (example only, recompute live):
window origin (2509, 914), size (1863, 1176), monitor eDP-2
1920x1200 scale 1 transform 0 at virtual (2464, 902).

## 5. Step 2: open the grid page and read the live DOM values

1. Open tests/calibration-grid.html in a fresh Zen tab (file:// URL
   from the repo checkout). This is the E2 page: 20 buttons T01-T20
   (120x48 CSS px) plus 9 small links R1/R2/R3 View/Remove/Rejudge.
   Every click records into window.__hits, turns the target green,
   and updates the status line "Hits: N / 29". Do NOT use ?truth=1:
   the truth labels compute screen centers as mozInnerScreenX/Y +
   rect center, which is exactly the assumption under test, so the
   labels are not ground truth for this probe.
2. Read the values through the amend's own code path (this is the
   function under test, so a failure here is itself a result):

```
cd <repo checkout>
python3 scripts/zen_dom.py list
python3 scripts/zen_dom.py eval "return [window.mozInnerScreenX, window.mozInnerScreenY];"
python3 scripts/zen_dom.py eval "return [window.devicePixelRatio, window.innerWidth, window.innerHeight, window.outerWidth, window.outerHeight];"
python3 scripts/zen_dom.py locate "[data-tid='T01']"
```

The zen_dom.py CLI has only five subcommands (list, tab, eval,
locate, kill-hung, scripts/zen_dom.py:482-496); there is no
subcommand for viewport_origin(), so the raw evals above read the
same values but never invoke the function under test and never
exercise its validation. Invoke it directly, so a null or
non-numeric return raises its ZenDomError instead of printing as
JSON null:

```
cd <repo checkout>
python3 - <<'EOF'
import sys
sys.path.insert(0, 'scripts')
from zen_dom import ZenSession
with ZenSession() as z:
    print(z.viewport_origin())
EOF
```

Record: mozInnerScreenX/Y (call it MX, MY), devicePixelRatio (DPR),
innerWidth/innerHeight, outerWidth/outerHeight, and the rect of each
probe target (section 6 lists them). If viewport_origin() raises
ZenDomError, or the raw eval returns JSON null or a non-number,
record the exact error or output and stop at outcome C (section 11).
Do not substitute another origin source and continue as if nothing
happened.

Derived values to record in the same step:

- Sidebar width: measure from the DOM (the width of the sidebar
  element, or the E2 value about 240 CSS px). Compare with MX.
- URL bar height: outerHeight minus innerHeight minus OS window
  chrome, or the E2 value about 8 CSS px. Compare with MY.
- The two one-line arithmetic checks (do these before clicking):
  if window-relative, MX is about the sidebar width and MY is about
  the URL bar height; if absolute, MX is about win_x + sidebar width
  and MY is about win_y + URL bar height.

## 6. Step 3: compute both candidate points (no click yet)

Probe targets (spread across the grid, one small link): T01
(top-left), T05 (top-right), T11 (middle-left), T20 (bottom-right),
R1-View (small link, bottom rows).

For each target, read its rect with the locate command above (or one
eval returning all five rects at once), then compute:

- Rect center in viewport CSS px: cx = rect.x + rect.width / 2,
  cy = rect.y + rect.height / 2.
- Case A (amend as-is, absolute): screen_A = (MX + cx, MY + cy).
- Case B (E2, window-relative): screen_B =
  (win_x + MX + cx, win_y + MY + cy).
- screen_B minus screen_A is exactly (win_x, win_y), the window
  origin. The two cases differ by thousands of px, so one click
  decides it; five targets make it robust.

Worked example from the E2 geometry (example only, recompute live):
window origin (2509, 914), MX, MY = (240, 8), viewport 1615x1160.
T01 rect center is (161.5, 162.4) in viewport CSS px (left
calc(10% - 60px), top calc(14% - 24px), 120x48). Case A screen =
(401.5, 170.4). Case B screen = (2910.5, 1084.4). Difference =
(2509, 914), the window origin.

Pre-click sanity check, before any click: check each candidate
point against the monitor box and the Zen window rect from step 1,
using the clickable-point rule in step 1 (a point may be clicked
only inside the Zen window rect AND inside the box of the monitor
that contains the Zen window; never click a point on a different
monitor or outside every monitor box, the pointer protocol maps
screen points to normalized coords over the monitor box, and a point
off the monitor has no defined target there). Two branches:

Branch 1, general case: both the Case A point and the Case B point
for a target fall inside the Zen window rect and its monitor box.
Click the Case A points first (Step 4, section 7). If all five
Case A clicks miss, run the Case B confirmation clicks (Step 4b,
section 7b).

Branch 2, E2 geometry: the Case A point falls outside the monitor
box or outside the Zen window while the Case B point falls inside
both. On the E2 geometry this is exactly what happens: monitor
eDP-2 is 1920x1200 at virtual (2464, 902), so its box is x 2464 to
4384, y 902 to 2102, and all five Case A points (T01 (401.5, 170.4)
and the rest, all with x below 2464) fall outside it, so the
clickable-point rule forbids clicking them. In this branch Case A is
UNCLICKABLE: record "Case A unclickable by the monitor-box rule"
per target, skip Step 4 entirely (its Outcome B condition "all five
Case A clicks miss" can never be satisfied when the clicks are never
attempted), and go straight to Step 4b to click the Case B points.
The probe then decides by the arithmetic check (MX, MY against the
sidebar width and URL bar height, step 2) plus the Case B landings,
under new outcome E (section 11). Do not drop the monitor-box rule
to force the Case A clicks: clicking points on another monitor's
desktop or windows is not a probe of the Zen window.

## 7. Step 4: click the Case A points and verify from the DOM

Click method: the direct pointer path from tests/e2_direct_clicks.py,
which needs no session and is the proven E2 Part B protocol. That
script takes image points from /tmp/e2-actions.json plus an
observation meta JSON, so it cannot be run as-is for this probe,
which needs screen points with no meta. Use the driver below
instead, written to /tmp/c12_probe_click.py from this procedure.
It mirrors the E2 protocol exactly (pointer started as
native/pointer <monitor name>, "abs nx ny 1000000 1000000" over
the monitor box, cursorpos within 3 px or refuse, button 0 press,
0.025 s sleep, release, re-check cursorpos within 3 px), but reads
the monitor box from `hyprctl -j monitors` and takes screen points
directly from a JSON actions file:

```
cat > /tmp/c12_probe_click.py <<'EOF'
#!/usr/bin/env python3
"""C12 probe click driver: click SCREEN points, no observation meta.
Usage, from the repo checkout (so native/pointer resolves):
  python3 /tmp/c12_probe_click.py <monitor-name> /tmp/c12-actions.json
Actions file: [{"tid": "T01", "x": 2910.5, "y": 1084.4}, ...]
Logs every click with wall-clock time to /tmp/c12-probe-clicks.log.
"""
import json, math, os, select, subprocess, sys, time

POINTER = os.path.abspath("native/pointer")
LOG = "/tmp/c12-probe-clicks.log"
ENV = dict(os.environ)  # XDG_RUNTIME_DIR, WAYLAND_DISPLAY,
# HYPRLAND_INSTANCE_SIGNATURE exported per section 2.


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def hypr(*args):
    out = subprocess.run(["hyprctl", "-j", *args], capture_output=True,
                         text=True, env=ENV, timeout=15)
    return json.loads(out.stdout)


class Pointer:
    def __init__(self, monitor):
        self.p = subprocess.Popen([POINTER, monitor], env=ENV,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        if self.reply() != "ready":
            raise RuntimeError("pointer startup failed")

    def reply(self):
        if not select.select([self.p.stdout], [], [], 2)[0]:
            raise RuntimeError("pointer timed out")
        line = self.p.stdout.readline().strip()
        if not line:
            raise RuntimeError("pointer disconnected")
        return line

    def command(self, s):
        self.p.stdin.write(s + "\n")
        self.p.stdin.flush()
        if self.reply() != "ok":
            raise RuntimeError("pointer action failed: " + s)

    def close(self):
        try:
            self.p.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            self.p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.p.terminate()
            self.p.wait(timeout=2)


def main():
    monitor, actions_path = sys.argv[1], sys.argv[2]
    monitors = hypr("monitors")
    box = next((m for m in monitors if m["name"] == monitor), None)
    if box is None:
        raise RuntimeError("no monitor named %r" % monitor)
    mx, my, mw, mh = box["x"], box["y"], box["width"], box["height"]
    log("monitor %s box (%d,%d,%d,%d)" % (monitor, mx, my, mw, mh))
    actions = json.load(open(actions_path))
    pointer = Pointer(monitor)
    log("pointer ready, monitor " + monitor)
    n_ok = 0
    for a in actions:
        gx, gy = a["x"], a["y"]
        nx = round((gx - mx) / mw * 1000000)
        ny = round((gy - my) / mh * 1000000)
        pointer.command("abs %d %d 1000000 1000000" % (nx, ny))
        pos = hypr("cursorpos")
        err = math.hypot(pos["x"] - gx, pos["y"] - gy)
        if err > 3:
            log("click %s REFUSED pointer missed: intended %.1f,%.1f cursor %s err %.1f"
                % (a["tid"], gx, gy, pos, err))
            raise RuntimeError("pointer missed target; refusing click")
        pointer.command("button 0 1")
        time.sleep(0.025)
        pointer.command("button 0 0")
        pos2 = hypr("cursorpos")
        err2 = math.hypot(pos2["x"] - gx, pos2["y"] - gy)
        if err2 > 3:
            log("click %s post-click pointer moved: err %.1f" % (a["tid"], err2))
            raise RuntimeError("post-click pointer moved; click outcome uncertain")
        n_ok += 1
        log("click %s ok screen %.1f,%.1f cursor_err %.2f" % (a["tid"], gx, gy, err))
    pointer.close()
    log("done: %d/%d clicks" % (n_ok, len(actions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
EOF
```

Write the five Case A points to /tmp/c12-actions.json, one object
per target, in order:

```
python3 - <<'EOF'
import json
points = [
    {"tid": "T01", "x": 401.5, "y": 170.4},
    {"tid": "T05", "x": 1564.3, "y": 170.4},
    {"tid": "T11", "x": 401.5, "y": 588.0},
    {"tid": "T20", "x": 1564.3, "y": 796.8},
    {"tid": "R1-View", "x": 419.0, "y": 913.0},
]
json.dump(points, open("/tmp/c12-actions.json", "w"))
EOF
```

The numbers above are the E2 worked example, recompute them live
from step 3 before writing the file. R1-View is a text link whose
rendered width sets its center, so its worked-example point
(419.0, 913.0) is approximate only; measure its rect with locate
and recompute, never trust the example numbers for a link. Then, for each target, in
order:

1. Re-read the Zen window address and origin from hyprctl immediately
   before the click. If the window moved since step 1, recompute both
   candidate points from the fresh origin and record the move.
   Before moving the pointer, check the point against the
   clickable-point rule (step 1): it must fall inside the Zen window
   rect AND inside the box of the monitor that contains the Zen
   window. Refuse a point that falls on a different monitor; the
   cursorpos check below cannot prevent that, it only confirms the
   pointer reached the intended coordinates.
2. Run the driver for the five points (one driver run covers all
   five, in order):

```
cd <repo checkout>
python3 /tmp/c12_probe_click.py eDP-2 /tmp/c12-actions.json
```

Use the live monitor name from step 1, not eDP-2, unless the live
monitor is eDP-2. The driver moves the pointer to each screen point
(normalized as nx = round((gx - mx) / mw * 1000000),
ny = round((gy - my) / mh * 1000000) over the monitor box),
reads hyprctl cursorpos and refuses the click if the cursor is more
than 3 px from the intended point, presses and releases button 0
with a 0.025 s sleep between them, and re-reads cursorpos: if it
moved more than 3 px, that click is recorded as uncertain, not as
a landing, and the driver stops.
3. After all five clicks, read the DOM verdict (through zen_dom.py
   eval, one session, after the pointer work is done):

```
python3 scripts/zen_dom.py eval "return document.getElementById('status').textContent;"
python3 scripts/zen_dom.py eval "return JSON.stringify(window.__hits);"
```

Record per target: the clicked point, cursorpos before and after,
and the __hits entry (id, clientX, clientY). clientX/clientY are
viewport-relative, so they check the landing independently of
hyprctl: a landed click on the target records clientX/clientY
equal to the rect center within about 1 px. The status line must
read "Hits: 5 / 29" with the five tids if all five Case A clicks
landed, "Hits: 0 / 29" if none did.

Stop conditions: stop immediately, record, and do not continue
clicking if a click lands on another window or on the desktop
(the per-point monitor check in step 4.1 is what prevents this;
if it happens anyway the probe is already decided and further
clicks only add noise), if the Zen window moves or loses focus
mid-probe, or if the grid page reloads or scrolls (rects change;
re-read rects and recompute).

## 7b. Step 4b: click the Case B points (confirmation)

Run this step in exactly two situations, and in no other:

- Situation 1: Step 4 ran (Branch 1) and all five Case A clicks
  missed (status still "Hits: 0 / 29", __hits empty or holding only
  hits on whatever else was under the clicks).
- Situation 2: Step 4 was skipped because Branch 2 applies (Case A
  unclickable on the live geometry, section 6).

In both situations the Case B points are the confirmation the
decision rule needs: Outcome B and new outcome E (section 11) both
require "the Case B confirmation clicks land". Do not skip this
step and do not declare Case B from the Case A misses alone.

Same driver, same checks, same DOM verification as Step 4:

1. Write the five Case B points to /tmp/c12-actions-b.json, one
   object per target, in the same order (T01, T05, T11, T20,
   R1-View), recomputed live from step 3 (screen_B =
   (win_x + MX + cx, win_y + MY + cy)). The E2 worked example is
   T01 (2910.5, 1084.4); recompute the other four live, and
   re-measure R1-View with locate as in Step 4.
2. Re-read the Zen window address and origin from hyprctl
   immediately before the run. Check each Case B point against the
   clickable-point rule (step 1): inside the Zen window rect AND
   inside the box of the monitor that contains the Zen window.
   Refuse a point that falls on a different monitor.
3. Run the driver:

```
cd <repo checkout>
python3 /tmp/c12_probe_click.py eDP-2 /tmp/c12-actions-b.json
```

Use the live monitor name from step 1. The driver refuses a click
whose cursorpos is more than 3 px off and stops on a post-click
pointer move over 3 px, exactly as in Step 4.
4. Read the DOM verdict exactly as in Step 4 (status textContent
   and window.__hits through zen_dom.py eval). Record per target:
   the clicked Case B point, cursorpos before and after, and the
   __hits entry. A landed click records clientX/clientY equal to
   the rect center within about 1 px. All five landing reads
   "Hits: 5 / 29" with the five tids (note: in Situation 1 the
   counter starts at whatever Step 4 left, usually 0; record the
   starting count before this step so the five new landings are
   unambiguous).

If the Case B clicks miss: stop, do not declare either case, and
go to outcome E2 (section 11). Likely causes: the window moved
between reads (re-read the window address and origin immediately
before each click, step 4.1 above), a target moved (scroll or
layout shift, re-read the rects), or the click driver itself
failed (check /tmp/c12-probe-clicks.log for refused clicks).
Record the per-target table exactly as observed and re-run the
probe from step 1.

## 8. Step 5: AT-SPI cross-check (C12 requires it)

This step is part of C12, not optional for closing it, but it may be
run after the click decision if the a11y stack is not ready.

scripts/a11y.py has no CLI (no `__main__` block, no argparse), so
`scripts/a11y.py observe` runs the module and exits silently with
no snapshot. Call the library functions directly with python -c,
from the repo checkout, with CU_PICK4_FASTPATH=1 in the environment
(both observe and ground raise ValueError when the flag is off).
a11y.py imports `from cu import STATE, prepare_state, ...`, so
scripts/ must be on sys.path:

1. Take a fresh accessibility snapshot of the Zen PID and capture
   the snapshot path it returns. observe() writes the snapshot JSON
   to a file under the repo STATE dir (0600) and returns a dict
   whose 'snapshot' key is that path; each element carries a 'ref'
   ('e1', 'e2', ...) plus role and name. Find the five targets by
   matching name (the button text, T01 and the rest) in the
   returned elements:

```
cd <repo checkout>
CU_PICK4_FASTPATH=1 python3 - <<'EOF'
import sys
sys.path.insert(0, 'scripts')
import a11y, json
snap = a11y.observe(<ZEN_PID>)
print("SNAPSHOT " + snap['snapshot'])
print(json.dumps([(e['ref'], e.get('role'), e.get('name')) for e in snap['elements']], indent=1))
EOF
```

Record the printed SNAPSHOT path and the ref of each of the five
targets. The snapshot must be younger than 90 s when ground()
uses it; if more than 90 s pass, take a fresh snapshot and
re-resolve the refs.
2. Resolve the same five targets by ref (scripts/a11y.py ground
   with the snapshot path and each target ref) and read their
   extents. ground() re-resolves the ref against the live tree, so
   the box is fresh, and returns extents in screen coords plus the
   app root extents, so the caller can tell screen from
   window-relative:

```
cd <repo checkout>
CU_PICK4_FASTPATH=1 python3 - <<'EOF'
import sys
sys.path.insert(0, 'scripts')
import a11y, json
for ref in ["<REF_T01>", "<REF_T05>", "<REF_T11>", "<REF_T20>", "<REF_R1VIEW>"]:
    print(json.dumps(a11y.ground("<SNAPSHOT_PATH>", ref), indent=1))
EOF
```

Replace <REF_...> with the refs from step 5.1 and <SNAPSHOT_PATH>
with the printed snapshot path. If ground() raises "stale
accessibility snapshot", the snapshot is older than 90 s: retake
it in step 5.1 and repeat.
3. Compare, per target: the AT-SPI extents center against the
   DOM-derived screen point from the winning case (A or B). Record
   the difference in px per target. Agreement within a few px
   corroborates the winning case; disagreement over a few px means
   the conversion is still wrong somewhere and C12 stays open.
4. If AT-SPI is unavailable in the laptop session (no daemons, no
   pyatspi, snapshot fails), record "AT-SPI cross-check NOT RUN"
   with the exact error, and C12 stays open on that leg even if the
   click decision is clean.

## 9. Step 6: record everything and commit

Write /tmp/c12-probe-20261122.jsonl, one JSON object per line, with
a wall-clock timestamp on every line: step, command, raw output,
and the computed values. Then write the human log
improvements/c12-probe-log-20261122.md on todolist-push with the
per-target table (section 10 filled in), the decision (section 11),
and commit three files to todolist-push: the human log
improvements/c12-probe-log-20261122.md, the JSON lines file copied
from /tmp to improvements/c12-probe-20261122.jsonl, and the shell
log copied from /tmp to improvements/c12-probe-20261122.log. Copy
both /tmp files into improvements/ before committing; neither /tmp
file is committed from /tmp itself. The log is the evidence
C2 F2 requires ("probe log + a test pinning the agreed conversion").

Variables that must appear in the log (no run is complete without
all of them): DPR, window origin, sidebar width, URL bar height,
monitor box, monitor scale, monitor transform, Zen PID, window
address, viewport size (innerWidth/innerHeight), mozInnerScreenX/Y,
rect per target, both candidate points per target, clicked point
per target, Case B clicked point per target (Step 4b, when run),
cursorpos before and after per click, __hits entries,
Hits counter, session path used (direct pointer path, and whether
the session guardian was up or down), AT-SPI result or not-run
reason.

## 10. Expected results table

Fill in the "observed" column live. The "expected" columns are
computed from the step 3 formulas, not copied from this doc.

| Target | Rect center (viewport CSS px) | Case A screen point (MX + center) | Case B screen point (win + MX + center) | Case A clicked point (Step 4) | Case B clicked point (Step 4b) | cursorpos before/after | __hits id, clientX, clientY | Landed? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | | | | | | | | |
| T05 | | | | | | | | |
| T11 | | | | | | | | |
| T20 | | | | | | | | |
| R1-View | | | | | | | | |

Fill the Case B clicked point column only when Step 4b runs; leave
it blank when Step 4 decides alone (Outcome A).

Case A expected (amend right): all five Case A clicks land.
Status "Hits: 5 / 29", __hits has the five tids, recorded
clientX/clientY equal the rect centers within about 1 px, cursorpos
within 3 px of each clicked point. The arithmetic check agrees:
MX is about win_x + sidebar width, MY is about win_y + URL bar
height.

Case B expected (E2 right): all five Case A clicks miss. Status
stays "Hits: 0 / 29", __hits stays empty (or records only hits on
whatever else was under the clicks). The misses are offset from the
targets by exactly the window origin vector (win_x, win_y). The
arithmetic check agrees: MX is about the sidebar width, MY is
about the URL bar height. The Case B points (computed from the same
reads) fall inside the window; click them in Step 4b, where they
land on the targets.

## 11. Decision rule

Outcome A, Case A wins (all five Case A clicks land, arithmetic
check agrees): C12 is DONE as-is. The E2 window-relative reading
was wrong for this build or session. Required follow-up, in order:
(1) append a dated correction to docs/calibration-e2-report.md
stating the probe result and the measured MX, MY and window origin;
(2) keep viewport_origin() unchanged; (3) add a regression test
pinning the agreed conversion (origin = mozInnerScreenX/Y as
absolute, with a live-acquired origin, not a hardcoded pair);
(4) re-run the 13-suite set from the amend; (5) re-review. The
AT-SPI leg from step 5 must also agree, or C12 stays open on that
leg alone.

Outcome B, Case B wins (all five Case A clicks miss by the window
origin vector, arithmetic check agrees, and the Case B confirmation
clicks in Step 4b land): C12 is NOT done; fix the code. Required changes:
(1) scripts/zen_dom.py viewport_origin() must return the window
origin plus mozInnerScreenX/Y: origin = [win_x + MX, win_y + MY],
with the window origin read from hyprctl at call time (re-read per
call, the window can move); (2) add a DPR term: multiply by
window.devicePixelRatio and the meta monitor_scale (scripts/cu.py:990
carries monitor_scale), or assert scale == 1 and DPR == 1 on the
target monitor if the term is omitted, and record the assertion;
(3) add the AT-SPI cross-check (scripts/a11y.py ground extents)
that stops the run when the converted rect and the AT-SPI extents
disagree by more than a few px; (4) re-derive the synthetic tests
that bake in the wrong assumption (tests/test_zen_dom.py:418-428,
tests/test_pick4_fastpath.py:482-560) for the window-relative model
with a coherent fixture of their own, as C1 F2 prescribes: in each
case the origin must equal the window origin plus the
window-relative mozInnerScreen offset, the region origin must equal
the window origin, and the truth rect must equal origin plus rect.
Do NOT copy the E2 Zen numbers (240, 8) and window origin
(2509, 914) into these tests: they model the G30 Brave window
(region [2533, 914, 901, 1176], origin [2533, 914]), and swapping
in the E2 numbers while keeping that region breaks the asserted
points (the fixtures are consistent only because origin equals
region origin). The G30 cases need their own window-relative
re-derivation, for example origin [2533, 1014] as window origin
[2533, 914] plus a [0, 100] chrome offset, as case 6 already
models; (5) re-run the 13-suite set plus the new window-relative-origin
test; (6) re-run this probe to confirm the fix. Until the probe
re-run lands, dom_rect_to_image_point must not be cited as
satisfying C12.

Outcome C, mozInnerScreen returns null or non-numeric (ZenDomError
from the viewport_origin() call in step 2, or the raw eval in the
same step returning JSON null or a non-number): the probe records
FAIL-CLOSED and no click is attempted. The DOM-first flow cannot run
live over Marionette until the origin source is proven. Escalate to
the coordinator: check that the eval includes `return` (the ZT-B
null was a missing `return`, not a missing value), try the BiDi path,
and check whether this Zen build exposes mozInnerScreenX/Y at all.
Do not declare either case from a null.

Outcome D, mixed results (some Case A clicks land, some miss):
stop, do not declare either case. Likely causes: the window moved
between reads (re-read the window address and origin immediately
before each click, step 4.1 in section 7 covers this), a target moved
(scroll or layout shift, re-read the rects), or the click
verification itself failed (cursorpos over 3 px). Record the
per-target table exactly as observed, note which targets landed and
which missed, and re-run the probe from step 1 with the window
re-read per target.

Outcome E, Case A unclickable (Branch 2, section 6): Step 4 was
skipped because all five Case A points fall outside the monitor box
or outside the Zen window while the Case B points fall inside both.
The probe decides from the arithmetic check plus the Step 4b
confirmation clicks, with no Case A clicks at all:

- Outcome E1, Case B wins on this path (arithmetic check agrees
  with window-relative, and all five Case B clicks in Step 4b
  land): same conclusion as Outcome B, Case B wins, C12 is NOT
  done; apply the same six required changes as Outcome B. The
  only difference from Outcome B is that no Case A click was ever
  attempted, so the "Case A clicks miss" condition is replaced by
  "Case A unclickable by the monitor-box rule, recorded per target
  in section 6".
- Outcome E2, Case B clicks miss (some or all of the five Step 4b
  clicks miss, or the driver refuses them): stop, do not declare
  either case. The probe is inconclusive on this geometry: the
  arithmetic says B but the confirmation failed, so neither the
  amend nor the E2 reading is proven. Likely causes: the window
  moved between reads (re-read the window address and origin
  immediately before each click, step 4.1 in section 7), a target
  moved (re-read the rects), or the click driver itself failed
  (check /tmp/c12-probe-clicks.log for refused clicks). Record the
  per-target table exactly as observed and re-run the probe from
  step 1. Do not fall back to declaring Case B from the arithmetic
  alone.

DPR branch (applies to every outcome): if DPR is not 1 or the
monitor scale is not 1, the probe still decides the origin
semantics (the offset difference is in CSS px either way), but
the DPR term must be added regardless. Do not close C12 until the
DPR term exists or scale == 1 and DPR == 1 are asserted on the
target monitor.

## 12. What this probe does not decide

- Whether the DOM-first flow is fast enough (that is the benchmark,
  not this probe). This probe decides only the origin semantics.
- Whether the AT-SPI cross-check is built (step 5 covers it; if it
  is not run, C12 stays open on that leg).
- Anything about vision grounding. No screenshot is read to locate
  anything in this probe; the DOM rect is the ground truth and the
  click landing is verified from the DOM (__hits, Hits counter).

## 13. Sources (read on paper, 2026-11-22)

- scripts/zen_dom.py:367-380 (viewport_origin), :387-401
  (locate_point), on origin/todolist-push, commit 7d37d60.
- scripts/fastpath.py:169-205 (dom_rect_to_image_point,
  dom_rect_to_screen_point), on origin/todolist-push.
- scripts/dom_act.py: ground_input, ground_many, focus_type
  (the production consumer of the origin).
- docs/calibration-e2-report.md:21 (mozInnerScreen window-relative
  (240, 8), window origin (2509, 914)), and the E2 Part B protocol
  (pointer within 3 px, 29/29 clicks).
- improvements/worker-click2-c1-review-log.md:68-78 (C12 NOT
  SATISFIED, F2) and improvements/worker-click2-c2-review-log.md
  (C12 adjudication 02:58, required fix F2 03:01).
- tests/calibration-grid.html (targets T01-T20, R1-R3 links,
  window.__hits, Hits counter).
- tests/e2_direct_clicks.py (direct pointer protocol, no session).
- scripts/cu.py:990 (meta carries monitor_scale), :995-1000
  (image_point, the inverse map).

# CLICK2-C12PROBE log: mozInnerScreenX/Y absolute or window-relative?

Worker: CLICK2-C12PROBE (live C12 probe). Coordinator: COORD-CLICK-2.
Question: in this Zen build, are window.mozInnerScreenX/Y absolute screen
coordinates or window-relative? zen_dom.py:367 viewport_origin() treats them
as absolute; docs/calibration-e2-report.md says window-relative (240, 8),
"add the window origin (2509, 914) for screen px". This probe decides with
numbers so AMEND2 can write the C12 fix.
Branch: todolist-push. All times wall-clock Asia/Ho_Chi_Minh + elapsed.

## 03:19:09 +07 (+00.0s) task received, reading sources

- docs/calibration-e2-report.md: Zen at [2509, 914], size [1863, 1176],
  viewport 1615x1160, dpr 1, sidebar about 240 CSS px. mozInnerScreenX/Y
  recorded as WINDOW-relative (240, 8); truth table is window-relative CSS
  px, add window origin (2509, 914) for screen px.
- scripts/zen_dom.py viewport_origin() (line ~367): returns
  [window.mozInnerScreenX, window.mozInnerScreenY] and treats the result
  as the viewport origin in screen coordinates; dom_rect_to_screen_point
  in scripts/fastpath.py computes screen = origin + rect center.
- docs/clone2-dom-grounding-20261122.md: NOT FOUND in the VM checkout
  (no file matches *clone2* under docs/ or anywhere in the repo on
  todolist-push). Clone2's method could not be read from the repo; the
  probe uses zen_dom.py (Marionette via geckodriver --connect-existing)
  plus the E2 direct-pointer click protocol instead.

## 03:19:45 +07 (+36s) lane check

- SSH to laptop OK. Zen PID 496121 alive, ws1, at [2509, 914],
  size [1863, 1176], title "Welcome! - Zen Browser", address 0x557052b62dd0.
  Same window origin and size as the E2 report.
- Marionette 2828 LISTEN (zen-bin), CDP 9222 LISTEN.
- No live driving processes: only session_remote.py relay serve (idle
  infrastructure). Chrome/Brave on ws2 are clone windows, untouched.
- Laptop checkout: /home/james/workspace/computer-use-wayland,
  todolist-push, HEAD 4500a18, has scripts/zen_dom.py, native/pointer,
  /tmp/geckodriver present, wtype present (Escape via wtype, never ydotool).
- Note: /home/james/computer-use-wayland (old path) lacks zen_dom.py;
  the live checkout is /home/james/workspace/computer-use-wayland.

## Probe script

- /tmp/c12probe.py on the laptop (copy of ~/workspace/c12probe.py):
  one Marionette session, evals with `return`, urlbar rect via
  #urlbar-input first, elementFromPoint at rect center, both candidate
  screen points computed, winner decided by geometry BEFORE the click
  (mozInner as an absolute point must lie inside its own window rect),
  ONE real click via native/pointer with the desktop_act protocol
  (move, cursorpos within 3px or refuse, button 0 press/release,
  re-check), focus verified via document.activeElement in the same
  session, Escape via wtype to revert, session DELETE in finally.

## 03:23:17 +07 (+248s) run 1: live numbers, urlbar NOT in content DOM

- Zen window: at=[2509, 914] size=[1863, 1176] ws1.
  Monitor eDP-2: box=[2464, 902, 1920, 1200] scale=1.
- Current tab (not switched): title "Welcome!",
  url https://zen-browser.app/welcome/
- mozInnerScreenX=240 mozInnerScreenY=8 DPR=1.
- inner=1615x1160 outer=1863x1176 screenX=0 screenY=0.
- Chrome offsets: outerWidth-innerWidth=248,
  outerHeight-innerHeight=16.
- locate '#urlbar-input' -> null, '#urlbar input' -> null,
  '.urlbar-input' -> null, '#urlbar' -> null. FATAL, no click sent.
- Session DELETE sent, geckodriver exited, slot free.

## 03:23:17 analysis: geometry already refutes ABSOLUTE

- mozInner=(240, 8) as absolute screen coords is NOT on the eDP-2
  monitor (x 2464-4384, y 902-2102) and NOT inside the Zen window
  (x 2509-4372, y 914-2090). A viewport origin cannot sit off-monitor
  while its window is on-screen. ABSOLUTE is geometrically impossible.
- Window-relative reading closes exactly: content box
  240 + 1615 + 8 = 1863 wide, 8 + 1160 + 8 = 1176 tall, i.e. the
  content viewport sits 240px (sidebar) from the window left, 8px from
  the top, 8px from the right and bottom edges. Absolute viewport
  origin = (2509+240, 914+8) = (2749, 922).
- screenX=0 screenY=0: useless as an absolute reference on this
  Wayland setup, recorded only.
- The urlbar is browser chrome, not page content: no content
  document.querySelector can see it. That is why run 1 found null.
  Run 2 gets the urlbar rect from the CHROME context via the
  geckodriver moz/context endpoint (POST /session/{id}/moz/context),
  then clicks the winning candidate once and verifies focus from
  chrome context (activeElement + urlbar selection).

## 03:27:26 +07 (+486s) run 2: content re-confirmed, chrome context BLOCKED

- CONTENT mozInnerScreenX=240 mozInnerScreenY=8 DPR=1 (same as run 1).
- CONTENT inner=1615x1160 outer=1863x1176 screenX=0 screenY=0.
- CONTENT sample element BODY rect x=0 y=0 w=1615 h=1848.2,
  elementFromPoint hit DIV. Candidates for its center:
  A(abs)=(1047.5, 932.1) off-monitor eDP-2; B(win-rel)=(3556.5, 1846.1)
  on-monitor. Same pattern for every content element: A is shifted
  off-monitor by exactly the window origin.
- moz/context -> chrome FAILED: HTTP 500 unsupported operation,
  "System access is required. Start Zen with the
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to enable
  it." Chrome-context eval is NOT available in this running Zen.
  Restarting Zen with that env var would kill owner tabs and the
  session, so it is NOT done.
- Session DELETE sent, slot free (verified: no geckodriver process
  after the run).
- Run 3 plan: get the urlbar screen rect from AT-SPI instead
  (scripts/a11y.py proves AT-SPI works against Zen here; extents are
  screen coords). AT-SPI also gives the content frame extents, i.e.
  the TRUE viewport origin on screen, an independent instrument
  against mozInnerScreen (240, 8). One click at the winning
  candidate (AT-SPI urlbar center = window origin + chrome center),
  focus verified via the AT-SPI FOCUSED state on the urlbar entry
  plus a grim shot of the urlbar band, Escape via wtype to revert.

## 03:30:45 +07 (+696s) run 3: AT-SPI has no Zen

- CONTENT mozInnerScreenX=240 mozInnerScreenY=8 DPR=1 inner=1615x1160
  outer=1863x1176 (third confirmation). Session DELETE sent.
- AT-SPI bus works (desktop lists 6 apps) but Zen PID 496121 is NOT
  registered: Zen never activated accessibility (no AT client at its
  17:37 startup). No urlbar rect from AT-SPI, no FOCUSED-state check.
- Run 4 fallback: measure the urlbar pill from a grim screenshot
  (pixel-edge measurement, not eyeballing). The two candidates differ
  by (2509, 914), so even a few px of measurement error cannot flip
  the verdict.

## 03:32:16 +07 (+787s) run 4a: read-only, urlbar pill measured

- CONTENT mozInnerScreenX=240 mozInnerScreenY=8 DPR=1 inner=1615x1160
  outer=1863x1176 (fourth confirmation). Session DELETE sent.
- grim -g "x,y,w,h" FAILED (invalid geometry, both tries); grim -o
  eDP-2 full-monitor capture works (1920x1200, 841055 bytes).
- Top strip shows the Zen sidebar urlbar: rounded pill reading
  "zen-browser.app" with site icon. PIL edge measurement (monitor
  coords): x 52..277, y 54..89. Pill center monitor (164.5, 71.5).
- Screen coords (monitor origin 2464, 902): pill center (2628.5, 973.5).
  Window coords (origin 2509, 914): chrome center (119.5, 59.5).
- Candidates for the urlbar center:
  A (absolute) = chrome center as raw screen = (120, 60): off-monitor
  (eDP-2 x starts 2464), impossible.
  B (window-relative) = window origin + chrome center = (2629, 974):
  inside the window, exactly the measured pill center.
- Note: a pre-existing "Process crashed: omasnap / yesterday"
  Hyprland notification sits top-right; not caused by this probe.
- Run 4b next: ONE click at B (2629, 974), grim after-shot to
  observe selection/focus, Escape via wtype, Marionette check that
  the tab is unchanged, teardown.

## 03:36:12 +07 (+1013s) run 4b: ONE click at candidate B, focus confirmed

- Window re-read before clicking: at=[2509, 914] size=[1863, 1176],
  unchanged since measurement; click proceeded. Candidate A (120, 60)
  off-monitor: False. Candidate B (2628.5, 973.5) inside window: True.
- Pointer move: cursor (2628, 973), err 0.71px (refuse threshold 3px).
  CLICK SENT at screen (2628.5, 973.5), post-click cursor err 0.71px.
  Exactly ONE real click in the whole probe.
- After-click grim: urlbar shows "https://zen-browser.app..." with
  the URL text FULLY SELECTED (blue highlight) and an I-beam caret.
  Focus landed in the address bar. This is the observation that
  candidate B is the true screen point of the urlbar.
- wtype Escape rc=0. Revert grim: urlbar back to normal, host only
  "zen-browser.app", dimmed, link/share icons at right. Escape reverted.
- Tab check via Marionette after Escape: title "Welcome!",
  url https://zen-browser.app/welcome/, activeElement BODY. No
  navigation, nothing typed, no owner tab touched. Session DELETE sent.
- No leftover processes (geckodriver/probe count 0). No indicator
  pill was ever started (no session guardian in this probe), nothing
  to clean. Active workspace 1, Zen last window, alive at [2509, 914].

## VERDICT: WINDOW-RELATIVE

- window.mozInnerScreenX/Y in this Zen build are WINDOW-RELATIVE
  coordinates, NOT absolute screen coordinates.
- Evidence, all measured live on the real Zen (PID 496121, ws1):
  1. mozInnerScreenX=240 mozInnerScreenY=8, DPR=1, measured 4 times
     across runs 1, 2, 3, 4a (03:23, 03:27, 03:30, 03:32), identical
     every time. inner 1615x1160, outer 1863x1176.
  2. As absolute screen coords, (240, 8) is off the eDP-2 monitor
     (x 2464-4384, y 902-2102) and outside the Zen window. A viewport
     origin cannot sit off-monitor while its window is on-screen.
  3. Window-relative reading closes exactly: 240 + 1615 + 8 = 1863
     wide, 8 + 1160 + 8 = 1176 tall. Absolute viewport origin is
     (2509 + 240, 914 + 8) = (2749, 922).
  4. A content element (BODY center) has candidate A off-monitor and
     candidate B on-monitor, same pattern as the urlbar.
  5. The click: candidate B (2628.5, 973.5) landed in the address
     bar, focused it, selected the full URL text. Candidate A
     (120, 60) is off-monitor and was never clicked.
- Consequence for AMEND2: zen_dom.py viewport_origin() is WRONG as
  written. Screen point = Hyprland window origin + mozInnerScreen +
  rect center. The amend's 7/7 accuracy tests assumed absolute and
  prove nothing about the real semantics; they must be re-run against
  the window-relative chain (the E2 report's formula was right).
- Method notes for AMEND2:
  - The urlbar is browser chrome, not page content: no content
    document.querySelector can see it (run 1, all 4 selectors null).
  - Chrome-context eval via geckodriver moz/context is BLOCKED in
    this Zen: HTTP 500, needs MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 plus a
    Zen restart (run 2). Do not restart Zen to get it.
  - AT-SPI cannot see Zen at all (bus works, 6 apps, Zen not
    registered; accessibility never activated). Do not rely on it.
  - The urlbar rect used for the click came from a grim monitor
    capture + PIL pixel-edge measurement (x 52..277, y 54..89 monitor
    coords), confirmed visually as the "zen-browser.app" pill.
  - docs/clone2-dom-grounding-20261122.md does NOT exist in this
    checkout (todolist-push); clone2's method could not be read here.

## Time log (wall-clock +07, elapsed from task receipt 03:19:09)

- 03:19:09 +00s task received, sources read (E2 report, zen_dom.py,
  fastpath.py, dom_act.py; clone2 doc missing).
- 03:19:45 +36s lane check: Zen alive, Marionette 2828 + CDP 9222
  listening, no live driving, laptop checkout located.
- 03:23:17 +248s run 1: live numbers, urlbar null in content DOM.
- 03:27:26 +497s run 2: content re-confirmed, chrome context blocked.
- 03:30:45 +696s run 3: AT-SPI has no Zen.
- 03:32:16 +787s run 4a: urlbar pill measured from grim capture.
- 03:36:12 +1023s run 4b: ONE click at B, focus confirmed, Escape,
  tab unchanged, teardown clean.
- No 15-minute stall occurred at any point.

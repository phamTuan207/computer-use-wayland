#!/usr/bin/env python3
"""Single-session Zen DOM control manager.

Owns the ONE remote session a Zen instance allows (BiDi and Marionette
share a single session slot; a leaked session blocks ALL remote control
until Zen restarts, see docs/zen-dom-control-comparison.md section 7).

Rules enforced here, not by convention:
- One session at a time across all processes (file lock).
- The session is ALWAYS deleted in a finally block, even on error.
- geckodriver is started per session and terminated with it.
- DOM is used to LOCATE and READ. Clicks are NOT done through the DOM
  here: BiDi click failed to fire a handler (04:49 21/11) and Marionette
  click fails on windowed Zen (0x0 viewport quirk). locate() returns the
  exact rect; the caller does the REAL mouse click through cu.py and
  then calls verify() to confirm the DOM changed. That is the hybrid.

Stdlib only (urllib). No selenium module needed; the laptop has no pip.
Default ports are the live Zen's (Marionette 2828). For a temp Zen,
pass --marionette-port.

Usage:
  python3 scripts/zen_dom.py list
  python3 scripts/zen_dom.py tab 8
  python3 scripts/zen_dom.py eval "return document.title"
  python3 scripts/zen_dom.py locate "#count-btn"
  python3 scripts/zen_dom.py rect "#count-btn"
  python3 scripts/zen_dom.py tabs
Environment: ZEN_MARIONETTE_PORT, ZEN_GECKODRIVER, ZEN_WD_PORT.

Timeouts (F3b): every WebDriver call converts TimeoutError, OSError,
URLError, HTTPException, JSON decode failures, and a response without
a "value" member into ZenDomError, so a hung Marionette tab-switch
never escapes raw. tab_at / list_tabs(handle_index=N) targets one tab
by its known handle index instead of scanning; the switch is verified
against the current handle, and a failed restore of the original tab
is raised, never swallowed. A full list_tabs scan stops after the
first hung handle (a hang means the session is wedged) instead of
burning one timeout per handle.

DOM-first grounding (item 12): locate() plus viewport_origin() gives
the exact rect center in screen coordinates with no screenshot, and
focus_check() / verify_typed() verify focus and typed text with cheap
JS evals (document.activeElement, field value), never a fresh observe.
viewport_origin() returns the ABSOLUTE origin: Hyprland window origin
+ mozInnerScreenX/Y (the live C12 probe 2026-11-22 03:36 proved
mozInnerScreen is WINDOW-relative in this Zen build, (240, 8), so the
raw pair as absolute coords is off-monitor). The geometry is verified
by check_viewport_geometry (dimension closure + window/monitor
containment), which replaces the AT-SPI cross-check: AT-SPI cannot see
Zen (probe run 3: the bus works, Zen never registered accessibility).
"""
import argparse
import fcntl
import http.client
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MARIONETTE_PORT = int(os.environ.get("ZEN_MARIONETTE_PORT", "2828"))
DEFAULT_WD_PORT = int(os.environ.get("ZEN_WD_PORT", "4444"))
GECKODRIVER = os.environ.get("ZEN_GECKODRIVER", "/tmp/geckodriver")
LOCK_PATH = Path(os.environ.get("ZEN_DOM_LOCK",
                               str(Path.home() / ".cache" / "agent-computer-use"
                                   / "zen_dom.lock")))
ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"

_FIND_JS = (
    "/* pierces open shadow roots and same-origin frames */"
    "function find(sel,root=document,depth=0,seen=new Set(),out=[],"
    "offsetX=0,offsetY=0,scaleX=1,scaleY=1){"
    "if(!root||depth>32||seen.has(root))return out;seen.add(root);"
    "const doc=root.nodeType===9?root:(root.ownerDocument||"
    "(root.host&&root.host.ownerDocument)||root);"
    "const add=e=>{if(e&&!out.some(x=>x.element===e))out.push({"
    "element:e,doc:doc,offsetX:offsetX,offsetY:offsetY,"
    "scaleX:scaleX,scaleY:scaleY});};"
    "if(root.querySelector)add(root.querySelector(sel));"
    "if(root.querySelectorAll){"
    "if(sel==='*')for(const e of root.querySelectorAll('*'))add(e);"
    "for(const f of root.querySelectorAll('iframe')){"
    "try{if(f.contentWindow&&f.contentWindow.document){"
    "let x=0,y=0,sx=1,sy=1;"
    "if(f.getBoundingClientRect){const r=f.getBoundingClientRect();"
    "x=r.left+(f.clientLeft||0);y=r.top+(f.clientTop||0);"
    "if(f.clientWidth>0)sx=r.width/f.clientWidth;"
    "if(f.clientHeight>0)sy=r.height/f.clientHeight;}"
    "find(sel,f.contentWindow.document,depth+1,seen,out,"
    "offsetX+x*scaleX,offsetY+y*scaleY,scaleX*sx,scaleY*sy);"
    "}}catch(_){}}"
    "for(const e of root.querySelectorAll('*')){"
    "if(e.shadowRoot)find(sel,e.shadowRoot,depth+1,seen,out,"
    "offsetX,offsetY,scaleX,scaleY);}}"
    "return out;}"
)


class ZenDomError(RuntimeError):
    pass


def _is_transport_failure(exc):
    """True for a hung/wedged transport: a raw TimeoutError/OSError,
    or a ZenDomError carrying the _wd transport-failure text. Other
    ZenDomErrors (an HTTP status, a missing tab) are per-handle
    failures, not a wedged session.
    """
    if isinstance(exc, (TimeoutError, OSError)):
        return True
    return isinstance(exc, ZenDomError) and 'transport failure' in str(exc)


def _wait_http(url, timeout_s=30):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def check_viewport_geometry(moz_inner, absolute_origin, window_origin,
                            window_size, inner_size, monitor_box=None,
                            scale_factor=1):
    """Probe checks that replace the AT-SPI cross-check (C12).

    Returns the absolute viewport origin, or raises ZenDomError when
    the geometry is impossible. The live C12 probe (2026-11-22 03:36,
    four runs, one real click) proved mozInnerScreenX/Y are
    WINDOW-relative in this Zen build: (240, 8) as absolute screen
    coords is off the eDP-2 monitor, while window-relative closes
    exactly (240 + 1615 + 8 = 1863 wide, 8 + 1160 + 8 = 1176 tall).
    AT-SPI cannot see Zen at all (probe run 3: the bus works, Zen
    never registered accessibility), so there is no AT-SPI cross-check
    for this path; these two checks are the independent instruments
    instead:
    - dimension closure: mozInner + inner size + trailing gap equals
      the window size on both axes (the gaps must be >= 0);
    - containment: the absolute origin lies inside the window rect,
      and inside the monitor box when one is given (this is the check
      that catches the old bug: raw mozInner treated as absolute).
    Window size and inner size are CSS/logical px. The caller applies
    the CSS-to-screen factor to mozInner before computing the absolute
    origin. Containment converts the absolute origin's offset from the
    screen-px window origin back to CSS px before comparing it with the
    window size.
    """
    def _pair(value, name):
        if (not isinstance(value, (list, tuple)) or len(value) != 2
                or any(isinstance(v, bool)
                       or not isinstance(v, (int, float)) for v in value)):
            raise ZenDomError('%s must be two numbers [x, y]' % name)
        return [value[0], value[1]]

    moz = _pair(moz_inner, 'mozInnerScreen')
    absolute = _pair(absolute_origin, 'absolute viewport origin')
    window = _pair(window_origin, 'window origin')
    size = _pair(window_size, 'window size')
    inner = _pair(inner_size, 'inner size')
    if (isinstance(scale_factor, bool)
            or not isinstance(scale_factor, (int, float))
            or scale_factor <= 0):
        raise ZenDomError('CSS-to-screen factor must be positive')
    if any(not float(v).is_integer() for v in size):
        raise ZenDomError('window size must use integer logical/CSS px')
    if any(v < 0 for v in moz):
        raise ZenDomError('mozInnerScreen is negative: %r' % (moz,))
    if size[0] <= 0 or size[1] <= 0 or inner[0] <= 0 or inner[1] <= 0:
        raise ZenDomError('window/inner size must be positive: %r %r'
                          % (size, inner))
    right_gap = size[0] - inner[0] - moz[0]
    bottom_gap = size[1] - inner[1] - moz[1]
    if right_gap < 0 or bottom_gap < 0:
        raise ZenDomError(
            'dimension closure fails: mozInner %r + inner %r exceeds '
            'window size %r (gaps %r, %r); the viewport origin cannot '
            'be window-relative with these numbers'
            % (moz, inner, size, right_gap, bottom_gap))
    expected = [window[0] + moz[0] * scale_factor,
                window[1] + moz[1] * scale_factor]
    if any(abs(absolute[i] - expected[i]) > 1e-6 for i in range(2)):
        raise ZenDomError(
            'absolute viewport origin %r does not match window origin %r '
            '+ mozInner %r at factor %r'
            % (absolute, window, moz, scale_factor))
    relative_css = [(absolute[i] - window[i]) / scale_factor
                    for i in range(2)]
    if not (0 <= relative_css[0] < size[0]
            and 0 <= relative_css[1] < size[1]):
        raise ZenDomError(
            'absolute viewport origin %r falls outside the window rect '
            '%r size %r after CSS-to-screen conversion; the origin is '
            'not absolute screen coordinates' % (absolute, window, size))
    if monitor_box is not None:
        if (not isinstance(monitor_box, (list, tuple))
                or len(monitor_box) != 4
                or any(isinstance(v, bool)
                       or not isinstance(v, (int, float))
                       for v in monitor_box)):
            raise ZenDomError('monitor_box must be [x, y, w, h]')
        if not (monitor_box[0] <= absolute[0]
                < monitor_box[0] + monitor_box[2]
                and monitor_box[1] <= absolute[1]
                < monitor_box[1] + monitor_box[3]):
            raise ZenDomError(
                'absolute viewport origin %r falls outside the monitor '
                'box %r; a viewport origin cannot sit off-monitor while '
                'its window is on-screen' % (absolute, monitor_box))
    return absolute


class ZenSession:
    """One WebDriver session against one Zen, with guaranteed cleanup."""

    def __init__(self, marionette_port=DEFAULT_MARIONETTE_PORT,
                 wd_port=DEFAULT_WD_PORT, geckodriver=GECKODRIVER,
                 timeout_s=30):
        self.marionette_port = marionette_port
        self.wd_port = wd_port
        self.geckodriver = geckodriver
        self.timeout_s = timeout_s
        self.gecko_proc = None
        self.session = None
        self._lock_file = None
        self.last_display_metrics = None
        self.last_scale_factor = 1

    def __enter__(self):
        LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = open(LOCK_PATH, "w")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            raise ZenDomError(
                "another process already holds the Zen remote session; "
                "only one remote session is allowed per Zen instance")
        self.gecko_proc = subprocess.Popen(
            [self.geckodriver, "--connect-existing",
             "--marionette-host", "127.0.0.1",
             "--marionette-port", str(self.marionette_port),
             "--port", str(self.wd_port), "--log", "warn"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not _wait_http(f"http://127.0.0.1:{self.wd_port}/status",
                          self.timeout_s):
            self._cleanup()
            raise ZenDomError("geckodriver status endpoint did not answer")
        try:
            resp = self._wd("POST", "/session", {"capabilities": {
                "alwaysMatch": {"browserName": "firefox"}}})
        except ZenDomError as exc:
            self._cleanup()
            raise ZenDomError(
                "could not create a remote session (is the single session "
                "slot leaked by a hung client? only a Zen restart clears "
                f"it): {exc}")
        self.session = resp["value"]["sessionId"]
        return self

    def __exit__(self, *exc):
        self._cleanup()
        return False

    def _cleanup(self):
        if self.session is not None:
            try:
                self._wd("DELETE", f"/session/{self.session}", {})
            except Exception:
                pass
            self.session = None
        if self.gecko_proc is not None and self.gecko_proc.poll() is None:
            self.gecko_proc.terminate()
            try:
                self.gecko_proc.wait(timeout=10)
            except Exception:
                self.gecko_proc.kill()
            self.gecko_proc = None
        if self._lock_file is not None:
            try:
                fcntl.flock(self._lock_file, fcntl.LOCK_UN)
                self._lock_file.close()
            except Exception:
                pass
            self._lock_file = None

    def _wd(self, method, path, body=None):
        """One WebDriver call. Every transport failure becomes a
        ZenDomError, never a raw exception (F3b): Marionette
        tab-switch intermittently HANGS past the timeout, and the raw
        TimeoutError used to escape the ZenDomError-only handling and
        kill the whole live lane. urllib wraps a socket timeout in a
        URLError whose reason is the TimeoutError, so URLError is
        caught too; HTTPError keeps its own branch first because it
        is a URLError subclass and carries the status code. A
        malformed response (non-JSON body, HTTPException such as a bad
        status line, or a JSON object without a "value" member) is a
        ZenDomError too: the callers all read ["value"], so a missing
        member would otherwise escape as a raw KeyError.
        """
        url = f"http://127.0.0.1:{self.wd_port}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                parsed = json.loads(resp.read().decode())
            if not isinstance(parsed, dict) or "value" not in parsed:
                raise ZenDomError(
                    f"malformed WebDriver response on {method} {path}: "
                    f"no 'value' member in {str(parsed)[:200]}")
            return parsed
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")[:400]
            raise ZenDomError(f"HTTP {e.code} on {method} {path}: {raw}")
        except (TimeoutError, OSError, urllib.error.URLError,
                http.client.HTTPException, ValueError) as e:
            raise ZenDomError(
                f"transport failure on {method} {path} after "
                f"{self.timeout_s}s timeout: {e}") from e

    def current_handle(self):
        """The handle of the tab Marionette currently has selected."""
        return self._wd("GET", f"/session/{self.session}/window")["value"]

    def switch_to_handle(self, handle):
        """Select one tab by its known handle. Raises ZenDomError on a
        hang or transport failure (via _wd); the caller decides whether
        to skip that handle or abort."""
        self._wd("POST", f"/session/{self.session}/window",
                 {"handle": handle})

    def _read_current_tab(self, handle):
        """Title and URL of the currently selected tab."""
        return {
            "handle": handle[:8],
            "title": self._wd("GET", f"/session/{self.session}/title")["value"],
            "url": self._wd("GET", f"/session/{self.session}/url")["value"],
        }

    def evaluate(self, script, args=None):
        """Run JS in the current tab. The reliable read/write path."""
        resp = self._wd("POST", f"/session/{self.session}/execute/sync",
                        {"script": script, "args": args or []})
        return resp["value"]

    def _try_restore(self, handle):
        """Restore the originally selected tab. Returns the
        ZenDomError when the restore fails, else None. The caller
        decides whether to raise it; a failed restore is never
        swallowed silently (RT R6), or later DOM reads run in the
        wrong tab.
        """
        try:
            self.switch_to_handle(handle)
        except (ZenDomError, TimeoutError, OSError) as exc:
            return exc
        return None

    def _verify_selected(self, handle):
        """Confirm Marionette actually selected the requested handle.

        A switch that reports success but leaves another tab selected
        would make the title/URL read describe the wrong tab. Raises
        ZenDomError on a mismatch. One cheap GET, no screenshot.
        """
        selected = self.current_handle()
        if selected != handle:
            raise ZenDomError(
                "tab switch did not take effect: requested "
                f"{handle[:8]}, selected is "
                f"{selected[:8] if isinstance(selected, str) else selected!r}")

    def tab_at(self, index):
        """One tab by known handle index, without scanning the rest.

        The index is a handle-LIST index (creation order in this
        session), not a verified visual tab order: one data point
        (F3b Arm A run 3, handles[8]) never proved handle order
        equals visual tab order, and tab drags, restores, and pinned
        tabs reorder visuals without reordering handles. The switch
        itself IS verified: after switching, the current handle must
        equal the requested handle, and the title/URL read belongs to
        that tab. A hang on the single switch raises ZenDomError (via
        _wd) instead of escaping raw. Raises ZenDomError when the
        index is out of range, when the switch does not take effect,
        or when the original tab cannot be restored.
        """
        return self.list_tabs(handle_index=index)[0]

    def list_tabs(self, handle_index=None):
        """List tabs, or one tab when handle_index is given.

        Full scan: every handle is switched to in turn and read. A
        hang on ONE handle stops the scan after that handle (F3b Arm
        E: a hang means the session is wedged and only a restart
        clears it, so later handles would hang too) and raises
        ZenDomError naming the wedge, instead of burning one timeout
        per handle. A non-transport failure on one handle is recorded
        as an error entry for that handle and the scan continues. The
        originally selected tab is restored afterwards, and a failed
        restore is raised, never swallowed.
        A tab entry is {handle, title, url}; a skipped handle is
        {handle, error}.
        """
        handles = self._wd("GET", f"/session/{self.session}/window/handles")["value"]
        if handle_index is not None:
            if (not isinstance(handle_index, int) or isinstance(handle_index, bool)
                    or handle_index < 0 or handle_index >= len(handles)):
                raise ZenDomError(
                    f"tab index {handle_index!r} out of range: "
                    f"{len(handles)} tabs")
        current = self.current_handle()
        if handle_index is not None:
            target = handles[handle_index]
            primary = None
            entry = None
            try:
                self.switch_to_handle(target)
                self._verify_selected(target)
                entry = self._read_current_tab(target)
            except ZenDomError as exc:
                primary = exc
            restore_error = self._try_restore(current)
            if primary is not None and restore_error is not None:
                raise ZenDomError(
                    f"tab switch failed ({primary}) and the original tab "
                    f"{current[:8]} could not be restored ({restore_error})")
            if primary is not None:
                raise primary
            if restore_error is not None:
                raise ZenDomError(
                    f"switched to tab {handle_index} but the original tab "
                    f"{current[:8]} could not be restored: {restore_error}")
            return [entry]
        tabs = []
        wedge = None
        try:
            for handle in handles:
                try:
                    self.switch_to_handle(handle)
                    self._verify_selected(handle)
                    tabs.append(self._read_current_tab(handle))
                except (ZenDomError, TimeoutError, OSError) as exc:
                    tabs.append({"handle": handle[:8],
                                 "error": str(exc)[:200]})
                    if _is_transport_failure(exc):
                        wedge = exc
                        break
        finally:
            restore_error = self._try_restore(current)
        if wedge is not None:
            if restore_error is not None:
                raise ZenDomError(
                    f"tab scan stopped at hung handle {tabs[-1]['handle']}: "
                    f"session wedged ({wedge}); original tab {current[:8]} "
                    f"could not be restored ({restore_error})")
            raise ZenDomError(
                f"tab scan stopped after the first hang ({wedge}); the "
                f"session is wedged and only a restart clears it")
        if restore_error is not None:
            raise ZenDomError(
                f"tab scan done but the original tab {current[:8]} could "
                f"not be restored: {restore_error}")
        return tabs

    def locate(self, selector):
        """Exact rect of an element, via getBoundingClientRect (JS path).

        Returns {x, y, width, height, center_x, center_y} in CSS pixels,
        or None if the selector matches nothing. Use center_x/center_y
        for the REAL mouse click; never a DOM click. The query pierces
        open shadow roots (a Messenger composer inside a shadow tree
        is findable) and same-origin iframes; a cross-origin iframe is
        unreachable from parent JS, so an element there returns None
        and the caller must fall back to vision or a BiDi
        browsing-context call, never silently drop the target from an
        "every input" harvest.
        """
        js = ("(function(){" + _FIND_JS +
              "const found=find(%s)[0];if(!found)return null;"
              "const e=found.element,r=e.getBoundingClientRect();"
              "const x=found.offsetX+r.x*found.scaleX;"
              "const y=found.offsetY+r.y*found.scaleY;"
              "return {x:x,y:y,width:r.width*found.scaleX,"
              "height:r.height*found.scaleY,center_x:x+"
              "r.width*found.scaleX/2,center_y:y+"
              "r.height*found.scaleY/2};})()" % json.dumps(selector))
        rect = self.evaluate(js, [selector])
        return rect

    def verify(self, script, expected):
        """Check a DOM condition after a real mouse click. Returns True
        when the JS expression equals the expected value."""
        return self.evaluate(script) == expected

    def display_metrics(self):
        """DPR, zoom, and viewport metrics in one JS eval.

        Returns {device_pixel_ratio, screen_pixels_per_css_pixel,
        zoom, inner_size, outer_size, moz_inner}. mozInnerScreenX/Y
        are CSS px (MDN: affected by zoom); physical screen px need
        screenPixelsPerCSSPixel, with devicePixelRatio as the fallback
        (devicePixelRatio already reflects page zoom in Firefox).
        The values are recorded with every snapshot so a conversion
        can be re-checked later; the live probe measured DPR 1,
        screenPixelsPerCSSPixel 1, zoom 1 on this Zen. The last read
        is kept on self.last_display_metrics for the grounding
        evidence; display_metrics() itself never raises for a missing
        value, it records None.
        """
        raw = self.evaluate(
            "/* zen_display_metrics */ return {"
            "mozInnerScreenX: window.mozInnerScreenX,"
            "mozInnerScreenY: window.mozInnerScreenY,"
            "devicePixelRatio: window.devicePixelRatio,"
            "screenPixelsPerCSSPixel:"
            " (typeof window.screenPixelsPerCSSPixel === 'number'"
            " ? window.screenPixelsPerCSSPixel : null),"
            "zoom: (window.visualViewport"
            " ? window.visualViewport.scale : 1),"
            "innerWidth: window.innerWidth,"
            "innerHeight: window.innerHeight,"
            "outerWidth: window.outerWidth,"
            "outerHeight: window.outerHeight};")
        if not isinstance(raw, dict):
            raise ZenDomError(
                'display metrics are not an object: %r' % (raw,))
        metrics = {
            'device_pixel_ratio': raw.get('devicePixelRatio'),
            'screen_pixels_per_css_pixel':
                raw.get('screenPixelsPerCSSPixel'),
            'zoom': raw.get('zoom'),
            'inner_size': [raw.get('innerWidth'), raw.get('innerHeight')],
            'outer_size': [raw.get('outerWidth'), raw.get('outerHeight')],
            'moz_inner': [raw.get('mozInnerScreenX'),
                          raw.get('mozInnerScreenY')],
        }
        self.last_display_metrics = metrics
        return metrics

    def scale_factor(self):
        """CSS px to screen px factor for the conversion chain.

        screenPixelsPerCSSPixel when the browser reports it, else
        devicePixelRatio. The live probe measured 1 on this Zen; at
        monitor scale 2 the factor is 2 and the unscaled map lands
        about 306 screen px off (RT R13). Reads the last display
        metrics when available, else one fresh read.
        """
        metrics = getattr(self, 'last_display_metrics', None)
        if not isinstance(metrics, dict):
            metrics = self.display_metrics()
        factor = metrics.get('screen_pixels_per_css_pixel')
        if not isinstance(factor, (int, float)) or isinstance(factor, bool) \
                or factor <= 0:
            factor = metrics.get('device_pixel_ratio')
        if not isinstance(factor, (int, float)) or isinstance(factor, bool) \
                or factor <= 0:
            raise ZenDomError('no usable CSS-to-screen factor in %r'
                              % (metrics,))
        return factor

    def viewport_origin(self, window_origin=None, window_size=None,
                        monitor_box=None):
        """[x, y] of the viewport origin in ABSOLUTE screen coordinates.

        Firefox-only. The live C12 probe (2026-11-22 03:36) proved
        mozInnerScreenX/Y are WINDOW-relative in this Zen build, so
        the absolute origin is the Hyprland window origin plus
        mozInnerScreenX/Y times the CSS-to-screen factor:
        (2509, 914) + (240, 8) = (2749, 922) at the measured setup.
        window_origin is REQUIRED: without it the raw pair cannot be
        placed on screen, and returning it as-is was the old bug
        (the pair as absolute coords is off-monitor). window_size is
        the Hyprland window size (defaults to the JS outer size);
        monitor_box is [x, y, w, h] of the monitor when known. The
        result is verified by check_viewport_geometry (dimension
        closure + window/monitor containment), which replaces the
        AT-SPI cross-check: AT-SPI cannot see Zen (probe run 3), so
        no AT-SPI check exists for this path. Rect centers from
        getBoundingClientRect are viewport relative, so screen =
        origin + rect center times the factor. One cheap JS eval
        (metrics bundled), no screenshot.
        """
        if window_origin is None:
            raise ZenDomError(
                'viewport_origin needs the Hyprland window origin: raw '
                'mozInnerScreenX/Y are window-relative in this Zen '
                'build (live probe 03:36), not absolute screen coords')
        raw = self.evaluate(
            "/* zen_viewport_origin */ return [window.mozInnerScreenX,"
            " window.mozInnerScreenY, window.devicePixelRatio,"
            " (typeof window.screenPixelsPerCSSPixel === 'number'"
            " ? window.screenPixelsPerCSSPixel : null),"
            " (window.visualViewport ? window.visualViewport.scale : 1),"
            " window.innerWidth, window.innerHeight,"
            " window.outerWidth, window.outerHeight];")
        if (not isinstance(raw, (list, tuple)) or len(raw) != 9
                or any(v is None or isinstance(v, bool)
                       or not isinstance(v, (int, float)) for v in raw)):
            raise ZenDomError(
                'viewport origin read is not nine numbers: %r' % (raw,))
        moz_inner = [raw[0], raw[1]]
        factor = raw[3]
        if not isinstance(factor, (int, float)) or factor <= 0:
            factor = raw[2]
        self.last_display_metrics = {
            'device_pixel_ratio': raw[2],
            'screen_pixels_per_css_pixel': raw[3],
            'zoom': raw[4],
            'inner_size': [raw[5], raw[6]],
            'outer_size': [raw[7], raw[8]],
            'moz_inner': moz_inner,
        }
        self.last_scale_factor = factor
        absolute = [window_origin[0] + moz_inner[0] * factor,
                    window_origin[1] + moz_inner[1] * factor]
        size_css = window_size if window_size is not None \
            else [raw[7], raw[8]]
        return check_viewport_geometry(
            moz_inner, absolute, window_origin, size_css,
            [raw[5], raw[6]], monitor_box, scale_factor=factor)

    def locate_point(self, meta, selector):
        """Image point of one element's rect center, first-time-right.

        locate() gives the rect, viewport_origin() gives the absolute
        viewport origin (Hyprland window origin + mozInnerScreen, live
        probe 03:36), and fastpath.dom_rect_to_image_point maps the
        rect center into the observation image (same linear map as
        cu.image_point, inverted), times the CSS-to-screen factor
        recorded with the origin read. The window origin comes from
        the meta's window_bounds. A monitor region is never a window
        origin, so screen observations without window_bounds are
        refused. No screenshot is read to locate the element: the DOM
        rect is ground truth.
        Raises ZenDomError when the element is missing or the point
        falls outside the observed image.
        """
        from fastpath import dom_rect_to_image_point
        rect = self.locate(selector)
        if rect is None:
            raise ZenDomError(f"no element matches {selector!r}")
        bounds = meta.get('window_bounds') if isinstance(meta, dict) else None
        if (isinstance(bounds, (list, tuple)) and len(bounds) == 4):
            window_origin = [bounds[0], bounds[1]]
            window_size = [bounds[2], bounds[3]]
        elif (isinstance(meta, dict) and
              (meta.get('scope') in ('window', 'screen') or
               meta.get('monitor_box') is not None)):
            raise ZenDomError('meta needs window_bounds; region is not a '
                              'window origin')
        elif isinstance(meta, dict) and isinstance(meta.get('region'),
                                                  (list, tuple)):
            window_origin = [meta['region'][0], meta['region'][1]]
            window_size = [meta['region'][2], meta['region'][3]]
        else:
            raise ZenDomError('meta needs window_bounds')
        monitor_box = meta.get('monitor_box') if isinstance(meta, dict) \
            else None
        origin = self.viewport_origin(window_origin, window_size,
                                      monitor_box)
        try:
            return dom_rect_to_image_point(
                meta, rect, origin,
                getattr(self, 'last_scale_factor', 1))
        except ValueError as exc:
            raise ZenDomError(str(exc)) from exc

    def hit_check(self, selector):
        """True when the element's rect center hits the element itself.

        Cheap JS eval (elementFromPoint), no screenshot. The
        first-time-right guard: the rect center must resolve to the
        element itself or to a NON-interactive descendant, or the
        click would land on whatever covers it. An interactive child
        at the center (BUTTON, A, INPUT, [role=button]: a clear-text,
        emoji, or send affordance inside the composer) FAILS the
        check: the click would activate the child instead of focusing
        the field. A plain text SPAN inside the field still passes.
        """
        return bool(self.evaluate(
            "(function(){" + _FIND_JS +
            "const found=find(%s)[0];if(!found)return false;"
            "const e=found.element;"
            "const r=e.getBoundingClientRect();"
            "if(!r.width||!r.height) return false;"
            "const root=e.getRootNode?e.getRootNode():found.doc;"
            "const hitRoot=root&&typeof root.elementFromPoint==='function'"
            "?root:found.doc;"
            "if(!hitRoot||typeof hitRoot.elementFromPoint!=='function')"
            "return false;"
            "const hit=hitRoot.elementFromPoint(r.left+r.width/2,"
            "r.top+r.height/2);"
            "if(!hit) return false;"
            "if(e===hit) return true;"
            "if(!e.contains(hit)) return false;"
            "const tag=(hit.tagName||'').toUpperCase();"
            "if(/^(BUTTON|A|INPUT|TEXTAREA|SELECT|OPTION|LABEL|SUMMARY)$/"
            ".test(tag)) return false;"
            "if(hit.closest && hit.closest('[role=\"button\"],"
            "[role=\"link\"],[role=\"checkbox\"],[role=\"menuitem\"],"
            "[role=\"tab\"]')) return false;"
            "if(hit.getAttribute && /^(button|link)$/"
            ".test(hit.getAttribute('role')||'')) return false;"
            "return true;})()"
            % json.dumps(selector)))

    def focus_check(self, selector):
        """True when the element is the focused, editable element.

        Cheap JS eval (document.activeElement), no screenshot. The
        pre-type gate in the DOM-first flow: after the click, the
        input must be activeElement before any keystroke is sent.
        The active element is walked down through shadowRoot
        .activeElement (V3): an input inside a shadow root is focused
        when the host is document.activeElement and the input is the
        shadow root's activeElement; the old strict equality
        false-negatived that shape.
        """
        return bool(self.evaluate(
            "(function(){" + _FIND_JS +
            "const found=find(%s)[0];if(!found)return false;"
            "const e=found.element;let a=found.doc.activeElement;"
            "while(a&&a.shadowRoot&&a.shadowRoot.activeElement)"
            "a=a.shadowRoot.activeElement;"
            "return a===e&&!e.readOnly&&(e.isContentEditable||"
            "/^(INPUT|TEXTAREA)$/.test(e.tagName));})()"
            % json.dumps(selector)))

    def field_value(self, selector):
        """Current value/text of one field, or None when it has none.

        The query pierces open shadow roots (same helper shape as
        locate) and traverses same-origin iframes, so a field inside
        an iframe reads the same as one in the top document. A
        cross-origin iframe is unreachable from parent JS, so a
        field there returns None and the caller must fall back to
        vision or a BiDi browsing-context call, never silently drop
        the target.
        """
        return self.evaluate(
            "(function(){" + _FIND_JS +
            "const found=find(%s)[0];if(!found)return null;"
            "const e=found.element;return e.isContentEditable?e.textContent:"
            "('value' in e?e.value:null);})()" % json.dumps(selector))

    def verify_typed(self, selector, expected, before=None):
        """True when the field holds exactly the expected text.

        Cheap JS eval, no screenshot. The sufficient type check: the
        pixel band can only show that the input line changed, while
        this reads what the field actually holds. The lookup pierces
        open shadow roots and traverses same-origin iframes, the same
        as locate(); a cross-origin iframe target fails closed
        (False), never a wrong pass. For contenteditable fields the
        comparison normalizes trailing whitespace (textContent
        carries a trailing newline the typed text does not). When
        before is given, the check also requires a recorded typed
        event (V11 flag): a pre-filled value and a JS-set value on an
        empty field both prove no typing happened without one (RT
        R2/R10). before None keeps the old equality-only shape for
        callers that never type.
        """
        result = self.evaluate(
            "(function(){" + _FIND_JS +
            "const found=find(%s)[0];if(!found)return null;"
            "const e=found.element;/* verify_typed */ return {value:"
            "e.isContentEditable?e.textContent:('value' in e?e.value:null),"
            "editable:!!e.isContentEditable};})()" % json.dumps(selector))
        if result is None:
            return False
        if isinstance(result, dict):
            value = result.get('value')
            editable = bool(result.get('editable'))
        else:
            value = result
            editable = False
        if not isinstance(value, str) or not isinstance(expected, str):
            return False
        norm_value = value.rstrip() if editable else value
        norm_expected = expected.rstrip() if editable else expected
        if norm_value != norm_expected:
            return False
        if before is not None:
            # The V11 flag is consulted whenever a before-value is
            # given, not only in the prefill case: a value that
            # appears with no trusted input event (a page script
            # setting it on an empty field, before='' != expected)
            # must fail exactly like a prefilled value does (RT
            # R10). dom_act's type_check is a typed-input check, so
            # requiring the flag there is correct; cdp.mjs set_value
            # is the programmatic path and is unaffected.
            if not self.typed_flag(selector):
                return False
        return True

    def arm_typed_flag(self, selector):
        """Arm the V11 typed-event flag on the target, before typing.

        Installs a trusted-input-event listener (real keystrokes
        dispatch trusted input events; a page script setting el.value
        and dispatching synthetic input events produces UNTRUSTED
        events, so the flag stays clear) plus a MutationObserver that
        records any DOM mutation of the field for diagnostics. The
        flag lives on window.__agentCuTyped keyed by selector.
        typed_flag() reads it after the type step. A value that
        appears with no trusted input event must fail verification.
        """
        return bool(self.evaluate(
            "(function(){" + _FIND_JS + "const sel=%s;"
            "window.__agentCuTyped = window.__agentCuTyped || {};"
            "window.__agentCuTyped[sel] = false;"
            "window.__agentCuMutated = window.__agentCuMutated || {};"
            "window.__agentCuMutated[sel] = false;"
            "const found=find(sel)[0];if(!found)return false;"
            "const e=found.element;"
            "e.addEventListener('input', function(ev){"
            "if(ev.isTrusted) window.__agentCuTyped[sel]=true;"
            "});"
            "try{"
            "const obs=new MutationObserver(function(){"
            "window.__agentCuMutated[sel]=true;"
            "});"
            "obs.observe(e, {childList:true, characterData:true,"
            "subtree:true, attributes:false});"
            "(window.__agentCuObservers ="
            " window.__agentCuObservers || {})[sel]=obs;"
            "}catch(_){}"
            "/* zen_arm_typed_flag */ return true;})()"
            % json.dumps(selector)))

    def typed_flag(self, selector):
        """True when a trusted input event fired on the target since
        arm_typed_flag(). A synthetic JS-set value dispatches no
        trusted input event, so the flag stays False for it."""
        return bool(self.evaluate(
            "/* zen_typed_flag */ return !!(window.__agentCuTyped"
            " && window.__agentCuTyped[%s]);" % json.dumps(selector)))

    def sent_bubble_contains(self, text):
        """V12 finish gate: True when the thread DOM holds a sent
        bubble whose text is exactly the message (leaf elements only,
        so a container holding the whole thread cannot false-pass).
        This is the one check the type step cannot set: only Enter
        plus the app can put the bubble there. Returns False when no
        bubble holds the text."""
        return bool(self.evaluate(
            "/* zen_sent_bubble */ return (function(){" + _FIND_JS +
            "const want=%s;"
            "for(const match of find('*')){const el=match.element;"
            "if(el.children&&el.children.length)continue;"
            "if((el.textContent||'').trim()===want)return true;}"
            "return false;})()" % json.dumps(text)))

    def harvest(self, selectors):
        """One-shot bulk DOM harvest (doma11y C1): ONE evaluate
        returns rects for EVERY selector, plus the viewport origin
        inputs and display metrics. Clone2 measured one-shot 66 rects
        in 0.019s Marionette versus 16ms per element per-element
        grounding (55x slower), so per-element ground_many is the slow
        shape and this is the VISION 1 shape. Returns {moz_inner,
        device_pixel_ratio, screen_pixels_per_css_pixel, zoom,
        inner_size, outer_size, items: {selector: {rect, hit,
        focused} or None}}. hit uses the same interactive-descendant
        rule as hit_check; focused is the deep activeElement walk.
        The caller adds the Hyprland window origin to moz_inner for
        the absolute origin (viewport_origin) and maps rect centers
        through fastpath with the recorded factor.
        """
        if not selectors:
            return {'moz_inner': [0, 0], 'device_pixel_ratio': 1,
                    'screen_pixels_per_css_pixel': 1, 'zoom': 1,
                    'inner_size': [0, 0], 'outer_size': [0, 0], 'items': {}}
        raw = self.evaluate(
            "/* zen_harvest */ return (function(){" + _FIND_JS +
            "const out={moz_inner:[window.mozInnerScreenX,"
            "window.mozInnerScreenY],"
            "device_pixel_ratio:window.devicePixelRatio,"
            "screen_pixels_per_css_pixel:"
            "(typeof window.screenPixelsPerCSSPixel==='number'"
            "?window.screenPixelsPerCSSPixel:null),"
            "zoom:(window.visualViewport?window.visualViewport.scale:1),"
            "inner_size:[window.innerWidth,window.innerHeight],"
            "outer_size:[window.outerWidth,window.outerHeight],"
            "items:{}};"
            "function interactive(el){"
            "if(!el) return false;"
            "const tag=(el.tagName||'').toUpperCase();"
            "if(/^(BUTTON|A|INPUT|TEXTAREA|SELECT|OPTION|LABEL|SUMMARY)$/"
            ".test(tag)) return true;"
            "if(el.closest && el.closest('[role=\"button\"],"
            "[role=\"link\"],[role=\"checkbox\"],[role=\"menuitem\"],"
            "[role=\"tab\"]')) return true;"
            "return false;"
            "}"
            "function deepActive(doc){let a=doc&&doc.activeElement;"
            "while(a&&a.shadowRoot&&a.shadowRoot.activeElement)"
            "a=a.shadowRoot.activeElement;return a;}"
            "for(const sel of %s){"
            "const found=find(sel)[0];"
            "if(!found){out.items[sel]=null;continue;}"
            "const e=found.element;"
            "const r=e.getBoundingClientRect();"
            "const x=found.offsetX+r.left*found.scaleX;"
            "const y=found.offsetY+r.top*found.scaleY;"
            "const root=e.getRootNode?e.getRootNode():found.doc;"
            "const hitRoot=root&&typeof root.elementFromPoint==='function'"
            "?root:found.doc;"
            "const hit=hitRoot&&hitRoot.elementFromPoint?"
            "hitRoot.elementFromPoint(r.left+r.width/2,"
            "r.top+r.height/2):null;"
            "const active=deepActive(found.doc);"
            "out.items[sel]={rect:{x:x,y:y,width:r.width*found.scaleX,"
            "height:r.height*found.scaleY,center_x:x+"
            "r.width*found.scaleX/2,center_y:y+"
            "r.height*found.scaleY/2},"
            "hit:!!hit&&(e===hit||(e.contains(hit)&&!interactive(hit))),"
            "focused:(active===e)};"
            "}"
            "return out;})()" % json.dumps(list(selectors)))
        if not isinstance(raw, dict) or 'items' not in raw:
            raise ZenDomError('harvest did not return items: %r' % (raw,))
        return raw


def kill_hung_remote_clients(max_age_s=900):
    """Watchdog helper: kill node/python processes that look like hung
    remote-control clients (puppeteer_bidi, selenium attach tests).
    Returns the list of killed PIDs. Never kills the browser itself."""
    import re
    killed = []
    try:
        out = subprocess.run(["ps", "-eo", "pid,etimes,args"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return killed
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(.*)$", line)
        if not m:
            continue
        pid, age, args = int(m.group(1)), int(m.group(2)), m.group(3)
        if age < max_age_s:
            continue
        if ("puppeteer_bidi" in args or "zen_selenium" in args
                or "selenium_connect_existing" in args):
            try:
                os.kill(pid, 15)
                killed.append(pid)
            except Exception:
                pass
    return killed


def main():
    parser = argparse.ArgumentParser(description="Zen DOM control, single session")
    parser.add_argument("--marionette-port", type=int, default=DEFAULT_MARIONETTE_PORT)
    parser.add_argument("--wd-port", type=int, default=DEFAULT_WD_PORT)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list tabs")
    p_tab = sub.add_parser("tab", help="one tab by handle-list index, no scan")
    p_tab.add_argument("index", type=int,
                       help="handle-list index (creation order, not visual tab order)")
    p_eval = sub.add_parser("eval", help="run JS in the current tab")
    p_eval.add_argument("script")
    p_loc = sub.add_parser("locate", help="exact rect of a selector")
    p_loc.add_argument("selector")
    sub.add_parser("kill-hung", help="kill hung remote-control clients")
    args = parser.parse_args()

    if args.cmd == "kill-hung":
        print(json.dumps({"killed": kill_hung_remote_clients()}, indent=1))
        return 0
    try:
        with ZenSession(marionette_port=args.marionette_port,
                        wd_port=args.wd_port) as z:
            if args.cmd == "list":
                print(json.dumps(z.list_tabs(), indent=1, ensure_ascii=False))
            elif args.cmd == "tab":
                print(json.dumps(z.tab_at(args.index), indent=1,
                                 ensure_ascii=False))
            elif args.cmd == "eval":
                print(json.dumps(z.evaluate(args.script), indent=1, ensure_ascii=False))
            elif args.cmd == "locate":
                print(json.dumps(z.locate(args.selector), indent=1, ensure_ascii=False))
    except ZenDomError as exc:
        # A wedged session (R7) used to die with a traceback here; a
        # CLI that dies mid-pipe is unreadable to its caller. Fail
        # cleanly: one JSON error object on stdout, exit code 1.
        print(json.dumps({"ok": False, "error": str(exc)[:400]}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

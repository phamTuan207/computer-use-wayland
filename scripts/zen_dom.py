#!/usr/bin/env python3
"""Single-session Zen DOM control manager.

Owns the ONE remote session a Zen instance allows (BiDi and Marionette
share a single session slot; a leaked session blocks ALL remote control
until Zen restarts, see docs/zen-dom-control-comparison.md section 7).

Rules enforced here, not by convention:
- One session at a time across all processes (file lock).
- The overlay pill is up before geckodriver spawns and released in
  cleanup; no pill, no session (fail closed, R3).
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
  python3 scripts/zen_dom.py eval --debug "return document.title"
  python3 scripts/zen_dom.py locate "#count-btn"
  python3 scripts/zen_dom.py rect "#count-btn"
  python3 scripts/zen_dom.py tabs
Environment: ZEN_MARIONETTE_PORT, ZEN_GECKODRIVER, ZEN_WD_PORT.
  CU_ZEN_DOM_DEBUG=1 enables eval without --debug (same gate).

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
import logging
import os
import secrets
import socket
import subprocess
import sys
import time

logger = logging.getLogger('zen_dom')
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MARIONETTE_PORT = int(os.environ.get("ZEN_MARIONETTE_PORT", "2828"))
DEFAULT_WD_PORT = int(os.environ.get("ZEN_WD_PORT", "4444"))


def _default_geckodriver(home=None, env=None):
    """Resolve the geckodriver path (R14, 2026-11-22).

    Precedence: ZEN_GECKODRIVER when set, else the persistent install
    at ~/.local/bin/geckodriver when it exists, else the old /tmp path.
    /tmp does not persist on the laptop, so a /tmp-only default
    silently loses the binary after a reboot or tmp clear (the R14
    blocker: /tmp/geckodriver vanished, no binary anywhere on PATH).
    home/env are injectable so unit tests can pin the resolution
    without touching the real home or environment.
    """
    env = os.environ if env is None else env
    if env.get("ZEN_GECKODRIVER"):
        return env["ZEN_GECKODRIVER"]
    installed = (Path.home() if home is None else Path(home)) \
        / ".local" / "bin" / "geckodriver"
    if installed.is_file():
        return str(installed)
    return "/tmp/geckodriver"


GECKODRIVER = _default_geckodriver()

LOCK_PATH = Path(os.environ.get("ZEN_DOM_LOCK",
                               str(Path.home() / ".cache" / "agent-computer-use"
                                   / "zen_dom.lock")))
ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"

# Viewport-origin settle (F2, ZT-B run 3, 2026-11-22): mozInnerScreenX/Y
# reads STALE for ~0.5s after a tab activation (switch): it reports
# (274, 66) while the true origin is (240, 8), then settles
# (validator-proof v2: stale at t=0.047s and t=0.299s, settled from
# t=0.552s; v4: stale first read after a 5min idle gap). A single
# read taken right after a switch can therefore fail dimension
# closure and refuse a valid send. viewport_origin polls until the
# moz pair is unchanged across VIEWPORT_SETTLE_STABLE_READS
# consecutive reads AND the geometry closes, within
# VIEWPORT_SETTLE_BUDGET_S, polling every VIEWPORT_SETTLE_POLL_S;
# otherwise it refuses fail-closed.
VIEWPORT_SETTLE_BUDGET_S = 2.0
VIEWPORT_SETTLE_POLL_S = 0.1
VIEWPORT_SETTLE_STABLE_READS = 3


class ZenDomError(RuntimeError):
    pass


# Pill gate (R3, mirroring scripts/cdp.mjs): the computer-use pill
# must show whenever ANY agent controls the machine, whatever the
# method. ZenSession.__enter__ acquires the central overlay pill
# (scripts/overlay.py) before geckodriver spawns and _cleanup
# releases it; when the pill cannot be shown the session is refused
# (ZenDomError 'pill unavailable') and no control runs invisibly. A
# preflight checks overlay availability before the spawn so a broken
# overlay fails before any session exists. The one opt-out is
# CU_ZEN_PILL=0, fixture tests only (no compositor there), never for
# live work. CU_OVERLAY_PY overrides the overlay.py path (test seam,
# same as cdp.mjs); CU_PILL_AGENT names the holder (default Muse).

def _pill_enabled():
    return os.environ.get('CU_ZEN_PILL', '1') != '0'


def _pill_agent():
    return os.environ.get('CU_PILL_AGENT') or 'Muse'


def _overlay_py_path():
    override = os.environ.get('CU_OVERLAY_PY')
    if override:
        return override
    return str(Path(__file__).resolve().parent / 'overlay.py')


def _run_overlay_cli(args, timeout_s=30):
    try:
        done = subprocess.run(
            [sys.executable, _overlay_py_path()] + args,
            capture_output=True, text=True, timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ZenDomError(
            'pill unavailable: overlay.py %s could not run: %s'
            % (args[0], exc))
    if done.returncode != 0:
        raise ZenDomError(
            'pill unavailable: overlay.py %s failed: %s' % (
                args[0], (done.stderr or done.stdout).strip()[:300]))
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise ZenDomError(
            'pill unavailable: overlay.py %s returned non-JSON output'
            % args[0])


def _pill_preflight():
    """Fail before any spawn when the overlay cannot be reached."""
    path = _overlay_py_path()
    if not Path(path).is_file():
        raise ZenDomError(
            'pill unavailable: overlay.py not found at %s '
            '(set CU_OVERLAY_PY)' % path)
    _run_overlay_cli(['status'], timeout_s=10)


def _pill_acquire(pid):
    reply = _run_overlay_cli(
        ['acquire', '--agent', _pill_agent(), '--method', 'Marionette',
         '--pid', str(pid)], timeout_s=60)
    if not isinstance(reply, dict) or reply.get('visible') is not True:
        raise ZenDomError(
            'pill unavailable: pill not visible: %s' % (str(reply)[:300],))


def _pill_release(pid):
    try:
        _run_overlay_cli(
            ['release', '--agent', _pill_agent(),
             '--method', 'Marionette', '--pid', str(pid)],
            timeout_s=10)
    except Exception as exc:
        logger.warning('pill release failed: %s', exc)


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
                            factor=None, verified_moz_inner=None):
    """Probe checks that replace the AT-SPI cross-check (C12).

    Returns the absolute viewport origin, or raises ZenDomError when
    the geometry is impossible. The live C12 probe (2026-11-22 03:36,
    four runs, one real click) proved mozInnerScreenX/Y are
    WINDOW-relative in this Zen build: (240, 8) as absolute screen
    coords is off the eDP-2 monitor, while window-relative closes
    exactly (240 + 1615 + 8 = 1863 wide, 8 + 1160 + 8 = 1176 tall).
    AT-SPI cannot see Zen at all (probe run 3: the bus works, Zen
    never registered accessibility), so there is no AT-SPI cross-check
    for this path; these checks are the independent instruments
    instead.

    Unit contract (AMEND4 item 1, one consistent system throughout):
    moz_inner and inner size and window size are CSS px; the window
    size is the Hyprland logical size, which equals CSS px
    numerically, so it is passed as-is and NEVER divided by the
    factor (the amend3 step 5 divide was the unit mixing that F9
    caught). window_origin, absolute_origin, and monitor_box are
    screen px. factor is the CSS-to-screen factor and is REQUIRED:
    a validator that silently assumes factor 1 is the F10 hole (a
    factor-forgotten origin is self-consistent at factor 1, so no
    pure consistency check can refuse it; only the explicit factor
    lets the exactness check below catch it). Passing no factor
    raises ZenDomError instead of guessing.
    Checks, in order:
    - dimension closure in CSS px: mozInner + inner size + trailing
      gap equals the window size on both axes. A negative trailing
      gap is a REFUSAL, not a warning: the pixel proof (C5-MOZ-GROWTH,
      log a42ef12) shows the reported mozInner is DISPLACED from
      where the viewport actually renders, by (+34, +58) on the live
      narrowed window (true origin (240, 8), gaps +8/+8). Accepting
      the moz-computed origin would ground clicks 34px right and
      58px down from the true origin. The closure invariant itself
      still holds for the TRUE origin; it is the reported pair that
      is untrustworthy.
    - verified-origin override (step-9 prototype, A1/A2 fix): when
      a verified mozInner (measured independently, C12-style
      screenshot/click cross-check) is supplied as
      verified_moz_inner, it is PREFERRED on every branch, not
      only when closure fails. The verified numbers must close
      (closure + origin inside the window + containment); when
      they do, the function returns the VERIFIED absolute origin
      and logs the override (reported moz, verified moz, offset).
      The absolute_origin argument is ignored on this path: it
      was computed from the reported moz, which may be displaced
      or merely wrong. A self-consistent-but-wrong reported moz
      (e.g. [250, 18], gaps 8/8 against the true [240, 8]) is
      otherwise accepted 10px off, because no pure consistency
      check can catch it. When the verified numbers fail their
      own checks, the call refuses instead of falling back to
      the reported moz. When no verified origin is supplied, the
      residual stands: a self-consistent-but-wrong moz is still
      accepted, so callers must pass verified moz always.
    - structural invariants, which DO refuse: the viewport must fit
      inside its window (inner size larger than the window size on
      either axis means the size input is wrong). These keep F9/F10
      refused: a factor-forgotten origin fails exactness, and a
      factor-2 small window fails the fit invariant.
    - exactness in screen px: the absolute origin must equal the
      window origin plus mozInner times the factor (within half a
      pixel), which is the check that catches a factor-forgotten
      origin at factor != 1;
    - containment in screen px: the absolute origin lies inside the
      window rect (window origin + window size times the factor),
      and inside the monitor box when one is given (this is the
      check that catches the old bug: raw mozInner treated as
      absolute).
    """
    def _pair(value, name):
        if (not isinstance(value, (list, tuple)) or len(value) != 2
                or any(isinstance(v, bool)
                       or not isinstance(v, (int, float)) for v in value)):
            raise ZenDomError('%s must be two numbers [x, y]' % name)
        return [value[0], value[1]]

    if (not isinstance(factor, (int, float)) or isinstance(factor, bool)
            or factor <= 0):
        raise ZenDomError(
            'viewport factor is required: pass the CSS-to-screen '
            'factor explicitly; a validator that silently assumes '
            'factor 1 accepts a factor-forgotten origin at factor '
            '!= 1 (F10)')
    moz = _pair(moz_inner, 'mozInnerScreen')
    absolute = _pair(absolute_origin, 'absolute viewport origin')
    window = _pair(window_origin, 'window origin')
    size = _pair(window_size, 'window size')
    inner = _pair(inner_size, 'inner size')
    if any(v < 0 for v in moz):
        raise ZenDomError('mozInnerScreen is negative: %r' % (moz,))
    if size[0] <= 0 or size[1] <= 0 or inner[0] <= 0 or inner[1] <= 0:
        raise ZenDomError('window/inner size must be positive: %r %r'
                          % (size, inner))
    right_gap = size[0] - inner[0] - moz[0]
    bottom_gap = size[1] - inner[1] - moz[1]
    if inner[0] > size[0] or inner[1] > size[1]:
        raise ZenDomError(
            'viewport larger than window: inner %r exceeds window '
            'size %r; the viewport cannot be wider or taller than '
            'its window, so the size input is wrong'
            % (inner, size))
    # Verified preference (step-9 A1/A2 fix): a supplied verified
    # mozInner wins on EVERY branch. The checks below are the same
    # ones the old overflow-only branch ran, moved up front so the
    # passing branch prefers verified too.
    if verified_moz_inner is not None:
        verified = _pair(verified_moz_inner, 'verified mozInnerScreen')
        if any(v < 0 for v in verified):
            raise ZenDomError(
                'verified mozInnerScreen is negative: %r' % (verified,))
        v_right_gap = size[0] - inner[0] - verified[0]
        v_bottom_gap = size[1] - inner[1] - verified[1]
        if v_right_gap < 0 or v_bottom_gap < 0:
            raise ZenDomError(
                'verified mozInner %r + inner %r does not close '
                'inside window size %r (gaps %r, %r); the verified '
                'origin is wrong too'
                % (verified, inner, size, v_right_gap, v_bottom_gap))
        if verified[0] >= size[0] or verified[1] >= size[1]:
            raise ZenDomError(
                'verified viewport origin outside window: verified '
                'mozInner %r sits at or past the window edge of '
                'size %r' % (verified, size))
        verified_absolute = [window[0] + verified[0] * factor,
                             window[1] + verified[1] * factor]
        if not (window[0] <= verified_absolute[0]
                < window[0] + size[0] * factor
                and window[1] <= verified_absolute[1]
                < window[1] + size[1] * factor):
            raise ZenDomError(
                'verified absolute viewport origin %r falls outside '
                'the window rect %r size %r at factor %r'
                % (verified_absolute, window, size, factor))
        if monitor_box is not None:
            if (not isinstance(monitor_box, (list, tuple))
                    or len(monitor_box) != 4
                    or any(isinstance(v, bool)
                           or not isinstance(v, (int, float))
                           for v in monitor_box)):
                raise ZenDomError('monitor_box must be [x, y, w, h]')
            if not (monitor_box[0] <= verified_absolute[0]
                    < monitor_box[0] + monitor_box[2]
                    and monitor_box[1] <= verified_absolute[1]
                    < monitor_box[1] + monitor_box[3]):
                raise ZenDomError(
                    'verified absolute viewport origin %r falls '
                    'outside the monitor box %r'
                    % (verified_absolute, monitor_box))
        if verified != moz:
            if right_gap < 0 or bottom_gap < 0:
                logger.warning(
                    'dimension closure overflow: reported mozInner %r + '
                    'inner %r exceeds window size %r (gaps %r, %r); using '
                    'verified mozInner %r (offset %r, %r) and returning '
                    'verified origin %r (pixel proof a42ef12)'
                    % (moz, inner, size, right_gap, bottom_gap, verified,
                       verified[0] - moz[0], verified[1] - moz[1],
                       verified_absolute))
            else:
                logger.warning(
                    'reported mozInner %r is self-consistent but '
                    'disagrees with verified mozInner %r (offset %r, '
                    '%r); using verified origin %r'
                    % (moz, verified, verified[0] - moz[0],
                       verified[1] - moz[1], verified_absolute))
            return verified_absolute
    if right_gap < 0 or bottom_gap < 0:
        # The reported mozInner is displaced from the true viewport
        # origin (MOZ-GROWTH pixel proof, log a42ef12: reported
        # [274, 66] vs true [240, 8] on the live narrowed window).
        # Reaching here means no verified origin was supplied, or
        # the supplied one equals the reported moz (whose gaps are
        # the same negative gaps): fail closed, naming the verified
        # override as the way out.
        raise ZenDomError(
            'dimension closure fails: mozInner %r + inner %r '
            'exceeds window size %r (gaps %r, %r); the reported '
            'mozInner is displaced from the true viewport origin '
            '(pixel proof a42ef12: true origin (240, 8) on the '
            'live narrowed window); supply a verified mozInner '
            '(independent screenshot/click cross-check) to '
            'override' % (moz, inner, size, right_gap, bottom_gap))
    expected = [window[0] + moz[0] * factor,
                window[1] + moz[1] * factor]
    if (abs(absolute[0] - expected[0]) > 0.5
            or abs(absolute[1] - expected[1]) > 0.5):
        raise ZenDomError(
            'absolute viewport origin %r is not window origin %r plus '
            'mozInner %r times factor %r (expected %r); the origin '
            'was computed without the factor'
            % (absolute, window, moz, factor, expected))
    if not (window[0] <= absolute[0] < window[0] + size[0] * factor
            and window[1] <= absolute[1] < window[1] + size[1] * factor):
        raise ZenDomError(
            'absolute viewport origin %r falls outside the window rect '
            '%r size %r at factor %r; the origin is not absolute '
            'screen coordinates'
            % (absolute, window, size, factor))
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


# Shared DOM traversal for every gate helper (AMEND4 item 2).
# pierce() walks open shadow roots; framesOf() enumerates
# same-origin frames, including frames inside shadow roots, by
# contentWindow presence (a shim frame has no tagName, so tagName
# must never be the test); find() runs pierce, then recurses into
# each frame document to depth 5, fail-closed on cross-origin
# frames (accessing a cross-origin contentWindow.document throws
# and is caught). The helpers below interpolate this constant into
# their IIFE. It contains no % (callers use % formatting) and no
# marker substring the test fakes dispatch on (no activeElement,
# elementFromPoint, textContent, getBoundingClientRect, or
# mozInnerScreenX), so the fakes keep routing each script to its
# own branch. deepActive() and framePoint() live apart because they
# DO contain a dispatch substring (activeElement,
# getBoundingClientRect) and belong only in the scripts whose fake
# branch already expects it.
_FIND_JS = (
    "function pierce(sel, root){"
    "let e=root.querySelector(sel);"
    "if(e) return e;"
    "const all=root.querySelectorAll('*');"
    "for(const el of all){"
    "if(el.shadowRoot){"
    "e=pierce(sel, el.shadowRoot);"
    "if(e) return e;"
    "}}"
    "return null;"
    "}"
    "function framesOf(root){"
    "let out=[];"
    "let frames=[];"
    "try{frames=root.querySelectorAll('iframe');}catch(_){}"
    "for(const f of frames){"
    "try{if(f.contentWindow && f.contentWindow.document) out.push(f);}"
    "catch(_){}"
    "}"
    "let all=[];"
    "try{all=root.querySelectorAll('*');}catch(_){}"
    "for(const el of all){"
    "if(el.shadowRoot){"
    "try{out=out.concat(framesOf(el.shadowRoot));}catch(_){}"
    "}}"
    "return out;"
    "}"
    "function find(sel, root, depth){"
    "if(root===undefined) root=document;"
    "if(depth===undefined) depth=0;"
    "let e=pierce(sel, root);"
    "if(e) return e;"
    "if(depth>=5) return null;"
    "const frames=framesOf(root);"
    "for(const f of frames){"
    "try{"
    "e=find(sel, f.contentWindow.document, depth+1);"
    "if(e) return e;"
    "}catch(_){"
    "}}"
    "return null;"
    "}"
)

# Deep activeElement walk: down through shadow roots AND same-origin
# iframes, fail-closed on cross-origin frames. Used by focus_check
# and harvest, whose fake branches already expect activeElement.
_DEEP_ACTIVE_JS = (
    "function deepActive(){"
    "let a=document.activeElement;"
    "while(a){"
    "if(a.shadowRoot && a.shadowRoot.activeElement){"
    "a=a.shadowRoot.activeElement; continue;"
    "}"
    "try{"
    "const cw=a.contentWindow;"
    "if(cw && cw.document && cw.document.activeElement){"
    "a=cw.document.activeElement; continue;"
    "}"
    "}catch(_){}"
    "break;"
    "}"
    "return a;"
    "}"
)

# Frame-viewport point for elementFromPoint: [owner document, x, y]
# in that document's viewport coords. An element inside an iframe
# reports a top-viewport rect, so the iframe offsets are walked off
# up the frame chain. Used by hit_check and harvest, whose fake
# branches already expect elementFromPoint / the harvest marker.
_FRAME_POINT_JS = (
    "function framePoint(e, x, y){"
    "let doc=(e.ownerDocument||document);"
    "let px=x, py=y;"
    "let d=doc;"
    "while(d && d.defaultView && d.defaultView.frameElement){"
    "const f=d.defaultView.frameElement;"
    "const r=f.getBoundingClientRect();"
    "px-=r.left; py-=r.top;"
    "d=(f.ownerDocument||document);"
    "}"
    "return [doc, px, py];"
    "}"
)


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
        # Geometry warnings from the last viewport_origin call
        # (dimension closure overflow, items56 live state): recorded
        # here so a live probe can read them on the session, not
        # only from the log.
        self.last_geometry_warnings = []
        # Per-arm typed-flag property names (TESTREPAIR item 7):
        # arm_typed_flag records the unpredictable name it installed
        # for each selector, and typed_flag reads that name back.
        self._typed_flag_props = {}
        self._pill_held = False
        self._pill_pid = None

    def __enter__(self):
        if _pill_enabled():
            _pill_preflight()
            _pill_acquire(os.getpid())
            self._pill_held = True
            self._pill_pid = os.getpid()
        try:
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
        except BaseException:
            self._cleanup()
            raise
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
        if getattr(self, '_pill_held', False):
            self._pill_held = False
            _pill_release(self._pill_pid)

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
        js = ("return (function(){" + _FIND_JS +
              "const e=find(%s);"
              "if(!e) return null;"
              " const r=e.getBoundingClientRect();"
              " return {x: r.x, y: r.y, width: r.width, height: r.height,"
              " center_x: r.x + r.width / 2, center_y: r.y + r.height / 2};})()"
              % json.dumps(selector))
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

    def _read_viewport_origin_raw(self):
        """One 9-number viewport-origin read (moz, factor, sizes).

        Returns the raw list [mozX, mozY, dpr, screenPixelsPerCSSPixel
        or None, zoom, innerW, innerH, outerW, outerH]. Raises
        ZenDomError when the read is not nine numbers: a malformed
        read is a transport/protocol failure, never a stale value,
        so the settle loop does not retry it.
        """
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
                       or not isinstance(v, (int, float))
                       for i, v in enumerate(raw) if i != 3)):
            raise ZenDomError(
                'viewport origin read is not nine numbers: %r' % (raw,))
        return raw

    def _read_viewport_origin_settled(self, window_origin, window_size,
                                      monitor_box, settle_budget_s=None,
                                      settle_poll_s=None,
                                      settle_stable_reads=None):
        """Poll the origin read until the moz pair settles (F2).

        Reads repeatedly until the moz pair is unchanged across
        settle_stable_reads consecutive reads AND the geometry
        closes (check_viewport_geometry passes on that read's own
        numbers), within settle_budget_s; otherwise raises
        ZenDomError fail-closed, carrying the last closure error.
        A stable-but-non-closing value is NOT an early exit: the
        stale value itself holds steady for ~300ms (validator-proof
        v2: equal reads at t=0.047s and t=0.299s) and only then
        moves, so only the budget bounds the wait. The settle is
        recorded on self.last_viewport_settle (reads, settled moz,
        elapsed ms). None arguments resolve to the module constants
        at call time, so tests can monkeypatch the constants.
        """
        budget = (VIEWPORT_SETTLE_BUDGET_S if settle_budget_s is None
                  else settle_budget_s)
        poll = (VIEWPORT_SETTLE_POLL_S if settle_poll_s is None
                else settle_poll_s)
        stable_reads = (VIEWPORT_SETTLE_STABLE_READS
                        if settle_stable_reads is None
                        else settle_stable_reads)
        started = time.monotonic()
        deadline = started + budget
        last_moz = None
        stable = 0
        reads = 0
        last_error = None
        last_raw = None
        while True:
            raw = self._read_viewport_origin_raw()
            reads += 1
            last_raw = raw
            moz = [raw[0], raw[1]]
            if moz == last_moz:
                stable += 1
            else:
                stable = 0
                last_moz = moz
            factor = raw[3]
            if not isinstance(factor, (int, float)) or factor <= 0:
                factor = raw[2]
            absolute = [window_origin[0] + moz[0] * factor,
                        window_origin[1] + moz[1] * factor]
            size = (window_size if window_size is not None
                    else [raw[7], raw[8]])
            try:
                check_viewport_geometry(
                    moz, absolute, window_origin, size,
                    [raw[5], raw[6]], monitor_box, factor=factor)
            except ZenDomError as exc:
                last_error = exc
            else:
                last_error = None
                if stable + 1 >= stable_reads:
                    self.last_viewport_settle = {
                        'reads': reads,
                        'settled_moz': moz,
                        'elapsed_ms': round(
                            (time.monotonic() - started) * 1000.0, 1),
                    }
                    return raw
            if time.monotonic() >= deadline:
                raise ZenDomError(
                    'viewport origin did not settle: mozInner %r did '
                    'not reach a stable closing value within %ss '
                    '(%d reads); last error: %s; supply a verified '
                    'mozInner (independent screenshot/click '
                    'cross-check) to override'
                    % (moz, budget, reads, last_error))
            time.sleep(poll)

    def viewport_origin(self, window_origin=None, window_size=None,
                        monitor_box=None, verified_moz_inner=None,
                        settle_budget_s=None, settle_poll_s=None,
                        settle_stable_reads=None):
        """[x, y] of the viewport origin in ABSOLUTE screen coordinates.

        Firefox-only. The live C12 probe (2026-11-22 03:36) proved
        mozInnerScreenX/Y are WINDOW-relative in this Zen build, so
        the absolute origin is the Hyprland window origin plus
        mozInnerScreenX/Y times the CSS-to-screen factor:
        (2509, 914) + (240, 8) = (2749, 922) at the measured setup.
        window_origin is REQUIRED: without it the raw pair cannot be
        placed on screen, and returning it as-is was the old bug
        (the pair as absolute coords is off-monitor). window_size is
        the Hyprland window size in logical px, which equals CSS px
        numerically, so it is passed as-is to the geometry check
        (defaults to the JS outer size, also CSS px); monitor_box is
        [x, y, w, h] of the monitor when known. The result is verified
        by check_viewport_geometry (dimension closure + exactness +
        window/monitor containment in one consistent unit system),
        which replaces the AT-SPI cross-check: AT-SPI cannot see Zen
        (probe run 3), so no AT-SPI check exists for this path. Rect centers from
        getBoundingClientRect are viewport relative, so screen =
        origin + rect center times the factor. The read is cheap JS
        evals (metrics bundled), no screenshot; the unverified path
        polls until the read settles (F2, see below).
        verified_moz_inner, when given, is an independently measured
        origin (C12-style screenshot/click cross-check, pixel proof
        a42ef12): the reported mozInner is displaced (+34, +58) on
        the live narrowed window, so closure overflow refuses unless
        the verified origin is supplied, and the verified origin is
        what is returned. The override is recorded in
        last_geometry_warnings.
        Settle (F2, ZT-B run 3, 2026-11-22): mozInnerScreenX/Y reads
        STALE for ~0.5s after a tab activation (switch): it reports
        (274, 66) while the true origin is (240, 8), then settles
        (validator-proof v2 stability series: stale at t=0.047s and
        t=0.299s, settled from t=0.552s; v4 reproduced the stale
        first read after a 5min idle gap). A single read taken right
        after a switch can therefore fail dimension closure and
        refuse a valid send (run 3 phase 4: open harvest (253, 30),
        send snapshot (274, 66)). When no verified origin is
        supplied, this method polls the read until the moz pair is
        unchanged across VIEWPORT_SETTLE_STABLE_READS consecutive
        reads AND the geometry closes, within
        VIEWPORT_SETTLE_BUDGET_S; otherwise it refuses fail-closed,
        carrying the last closure error. The verified path never
        settles: the verified origin is independent of the reported
        moz, so it takes one read as before. The settle is recorded
        on last_viewport_settle (reads, settled moz, elapsed ms).
        """
        if window_origin is None:
            raise ZenDomError(
                'viewport_origin needs the Hyprland window origin: raw '
                'mozInnerScreenX/Y are window-relative in this Zen '
                'build (live probe 03:36), not absolute screen coords')
        self.last_viewport_settle = None
        if verified_moz_inner is not None:
            raw = self._read_viewport_origin_raw()
        else:
            raw = self._read_viewport_origin_settled(
                window_origin, window_size, monitor_box,
                settle_budget_s, settle_poll_s, settle_stable_reads)
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
        size = window_size if window_size is not None else [raw[7], raw[8]]
        # Unit rule (AMEND4 item 1): the size is passed as-is in
        # BOTH branches. A given window_size is the Hyprland logical
        # size, which equals CSS px numerically; the None fallback
        # is outerWidth/Height, already CSS px. Dividing by the
        # factor (amend3 step 5) was unit mixing: it made the
        # closure check run on a halved size and the containment
        # check compare a screen-px origin against a CSS-px rect,
        # which falsely refused valid factor-2 geometry (F9) and
        # accepted a factor-forgotten origin (F10). The factor is
        # passed explicitly: the validator refuses when it is absent.
        origin = check_viewport_geometry(
            moz_inner, absolute, window_origin, size,
            [raw[5], raw[6]], monitor_box, factor=factor,
            verified_moz_inner=verified_moz_inner)
        # Record a closure overflow on the session (the validator
        # also logs it): a live probe reads this instead of parsing
        # the log. Empty when the gaps close. Reaching here with
        # negative gaps means the verified-origin path was used, so
        # the warning names the override (reported vs verified moz).
        # Step-9 A1/A2: the same recording covers the normal-branch
        # override (verified supplied, gaps fine, moz disagrees):
        # a probe that reads this must see that the origin came
        # from the verified measurement, not the reported moz.
        inner_size = [raw[5], raw[6]]
        right_gap = size[0] - inner_size[0] - moz_inner[0]
        bottom_gap = size[1] - inner_size[1] - moz_inner[1]
        self.last_geometry_warnings = []
        if right_gap < 0 or bottom_gap < 0:
            self.last_geometry_warnings = [
                'dimension closure overflow: reported mozInner %r + '
                'inner %r exceeds window size %r (gaps %r, %r); '
                'using verified mozInner %r, verified origin %r'
                % (moz_inner, inner_size, size, right_gap, bottom_gap,
                   verified_moz_inner, origin)]
        elif (verified_moz_inner is not None
                and list(verified_moz_inner) != moz_inner):
            self.last_geometry_warnings = [
                'reported mozInner %r disagrees with verified '
                'mozInner %r; using verified origin %r'
                % (moz_inner, verified_moz_inner, origin)]
        return origin

    def live_window_origin(self, address=None):
        """[x, y] live Hyprland origin of a window, re-read now.

        F3 (AMEND4 item 6): the grounding chain must not trust the
        observation meta's window origin without a live check. Reads
        hyprctl clients -j and returns the [at] origin of the window
        with the given address; with no address, the active window
        (hyprctl activewindow -j). Returns None when hyprctl is
        unavailable, the window is not found, or the output cannot
        be parsed: the caller then skips the staleness check (it
        cannot prove a mismatch) instead of failing a batch it
        cannot judge. Never raises for a missing hyprctl: the VM has
        none, and a grounding refusal there would be a false
        refusal, not a stale-origin catch.
        """
        try:
            if address is not None:
                out = subprocess.run(
                    ['hyprctl', '-j', 'clients'], capture_output=True,
                    text=True, timeout=3)
                clients = json.loads(out.stdout)
                for client in clients:
                    if (isinstance(client, dict)
                            and str(client.get('address')) == str(address)):
                        at = client.get('at')
                        if (isinstance(at, (list, tuple)) and len(at) == 2
                                and all(isinstance(v, (int, float))
                                        and not isinstance(v, bool)
                                        for v in at)):
                            return [at[0], at[1]]
                return None
            out = subprocess.run(
                ['hyprctl', '-j', 'activewindow'], capture_output=True,
                text=True, timeout=3)
            active = json.loads(out.stdout)
            if isinstance(active, dict):
                at = active.get('at')
                if (isinstance(at, (list, tuple)) and len(at) == 2
                        and all(isinstance(v, (int, float))
                                and not isinstance(v, bool) for v in at)):
                    return [at[0], at[1]]
            return None
        except Exception:
            return None

    def locate_screen_point(self, meta, selector):
        """Screen point of one element's rect center (A9: one
        coordinate system, CSS px rects converted once at the
        driver edge). locate() gives the rect, viewport_origin()
        gives the absolute viewport origin (Hyprland window origin
        + mozInnerScreen, live probe 03:36), and
        fastpath.dom_rect_to_screen_point converts the rect center
        to screen coordinates, times the CSS-to-screen factor
        recorded with the origin read. The window origin comes from
        the meta's window_bounds. No screenshot is read to locate
        the element: the DOM rect is ground truth. Raises
        ZenDomError when the element is missing.
        """
        from fastpath import dom_rect_to_screen_point
        rect = self.locate(selector)
        if rect is None:
            raise ZenDomError(f"no element matches {selector!r}")
        bounds = meta.get('window_bounds') if isinstance(meta, dict) else None
        if (isinstance(bounds, (list, tuple)) and len(bounds) == 4):
            window_origin = [bounds[0], bounds[1]]
            window_size = [bounds[2], bounds[3]]
        else:
            # AMEND4 item 5: no region fallback. A screen-scope meta
            # carries no window_bounds, and its region origin is the
            # monitor origin, not the window origin; falling back to
            # it re-admits the raw mozInner pair (F2).
            raise ZenDomError('meta needs window_bounds for the '
                              'window origin (mozInnerScreen is '
                              'window-relative)')
        monitor_box = meta.get('monitor_box') if isinstance(meta, dict) \
            else None
        origin = self.viewport_origin(window_origin, window_size,
                                      monitor_box)
        return dom_rect_to_screen_point(
            rect, origin, getattr(self, 'last_scale_factor', 1))

    def locate_point(self, meta, selector):
        """Image point of one element's rect center, first-time-right.

        The screen point is canonical (locate_screen_point); the
        image point is derived from it at the driver edge, because
        desktop_act still consumes image points. The fused
        rect-to-image function is off this path: locate_point keeps
        its contract (an image point) without calling it.
        Raises ZenDomError when the element is missing or the point
        falls outside the observed image.
        """
        from fastpath import screen_point_to_image_point
        screen_point = self.locate_screen_point(meta, selector)
        try:
            return screen_point_to_image_point(
                meta, screen_point[0], screen_point[1])
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
            "return (function(){" + _FIND_JS + _FRAME_POINT_JS +
            "const e=find(%s);"
            "if(!e) return false;"
            "const r=e.getBoundingClientRect();"
            "if(!r.width||!r.height) return false;"
            "const x=r.left+r.width/2, y=r.top+r.height/2;"
            "const fp=framePoint(e, x, y);"
            "const doc=fp[0];"
            "const hit=doc.elementFromPoint(fp[1], fp[2]);"
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

    # CB-5 locate confirmations, operational definitions (step 5):
    # stable means two consecutive rect reads agree on every
    # component within STABLE_TOLERANCE_PX (0.5 CSS px absorbs
    # sub-pixel rounding; anything larger is movement). unique
    # means exactly one element matches the selector across the
    # document, its open shadow roots, and same-origin iframes
    # (count 1); a caller holding a harvest ref that names one
    # element re-grounds with that ref instead of a selector that
    # matches several. visible, interactive, and uncovered are
    # read in the same evaluate as the rect, so the report
    # describes one moment, not three.
    STABLE_TOLERANCE_PX = 0.5

    def locate_confirmed(self, selector):
        """Re-confirm a located element before acting on it (CB-5,
        P2's re-confirm content).

        Returns None when the selector matches nothing. Otherwise
        returns a report dict: {rect, visible, interactive,
        uncovered, stable, unique, unique_count}. visible is a
        non-empty rect with display not none and visibility not
        hidden; interactive is not disabled and not aria-disabled;
        uncovered is hit_check (the rect center hits the element
        itself or a non-interactive descendant); stable is two rect
        reads agreeing within STABLE_TOLERANCE_PX; unique is
        unique_count == 1. Three cheap JS evals, no screenshot.
        The caller decides the verdict: dom_act.confirm_locate
        refuses on a failed confirmation instead of clicking.
        """
        report = self.evaluate(
            "/* zen_locate_confirmed */ return (function(){"
            + _FIND_JS +
            "function countAll(sel, root){"
            "let n=0;"
            "try{n+=root.querySelectorAll(sel).length;}catch(_){}"
            "let all=[];"
            "try{all=root.querySelectorAll('*');}catch(_){}"
            "for(const el of all){"
            "if(el.shadowRoot){n+=countAll(sel, el.shadowRoot);}"
            "}"
            "const frames=framesOf(root);"
            "for(const f of frames){"
            "try{n+=countAll(sel, f.contentWindow.document);}"
            "catch(_){}"
            "}"
            "return n;"
            "}"
            "const e=find(%s);"
            "if(!e) return null;"
            "const r=e.getBoundingClientRect();"
            "const cs=getComputedStyle(e);"
            "const disabled=!!e.disabled || "
            "e.getAttribute('aria-disabled')==='true';"
            "return {rect: {x: r.x, y: r.y, width: r.width,"
            " height: r.height,"
            " center_x: r.x + r.width / 2,"
            " center_y: r.y + r.height / 2},"
            " visible: !!r.width && !!r.height"
            " && cs.display !== 'none'"
            " && cs.visibility !== 'hidden',"
            " enabled: !disabled,"
            " count: countAll(%s, document)};})()"
            % (json.dumps(selector), json.dumps(selector)))
        if report is None or report.get('rect') is None:
            return None
        rect = report.get('rect') or {}
        second = self.locate(selector)
        stable = False
        if second is not None:
            stable = all(
                abs((second.get(k) or 0) - (rect.get(k) or 0))
                <= self.STABLE_TOLERANCE_PX
                for k in ('x', 'y', 'width', 'height'))
        return {'rect': {'x': rect.get('x'), 'y': rect.get('y'),
                         'width': rect.get('width'),
                         'height': rect.get('height'),
                         'center_x': rect.get('center_x'),
                         'center_y': rect.get('center_y')},
                'visible': bool(report.get('visible')),
                'interactive': bool(report.get('enabled')),
                'uncovered': bool(self.hit_check(selector)),
                'stable': stable,
                'unique': report.get('count') == 1,
                'unique_count': report.get('count')}

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
            "return (function(){" + _FIND_JS + _DEEP_ACTIVE_JS +
            "const e=find(%s);"
            "if(!e) return false;"
            "const a=deepActive();"
            "return a===e && !e.readOnly && "
            "(e.isContentEditable || /^(INPUT|TEXTAREA)$/.test(e.tagName));})()"
            % json.dumps(selector)))

    def element_text(self, selector):
        """Trimmed textContent of one PLAIN element, or None when
        it has none. Unlike field_value (which reads value for
        inputs and textContent only for contenteditables), this
        reads the rendered text of a plain element, so an assert
        on a sent bubble (a plain div, no value property) can
        verify it. REDTEAM (F4, 9858d9a): the fallback must NOT
        read a value-bearing element, because textContent is not
        its value: an input's textContent is always '', and a
        textarea's textContent is its DEFAULT value, not its live
        value, so an unconditional fallback lets an assert
        FALSE-PASS on a field. Returns None for a live-value
        element (input, textarea, select) or a contenteditable,
        and the caller must fail the assert, never pass it on
        text. Re-review follow-up: the gate is narrowed to those
        element types (a button, an option, an li carry their
        label in textContent, so their label asserts must read
        it; a broad 'value' in e check over-blocked them). The
        lookup pierces open shadow roots and traverses
        same-origin iframes, the same as field_value. A
        cross-origin iframe target returns None and the caller
        must fall back, never silently pass.
        """
        return self.evaluate(
            "return (function(){" + _FIND_JS +
            "const e=find(%s);"
            "if(!e) return null;"
            "if(e instanceof HTMLInputElement"
            " || e instanceof HTMLTextAreaElement"
            " || e instanceof HTMLSelectElement"
            " || e.isContentEditable) return null;"
            "const t=e.textContent;"
            "return typeof t==='string' ? t.trim() : null;})()"
            % json.dumps(selector))

    def field_value(self, selector):
        """Current value/text of one field, or None when it has none.

        The query pierces open shadow roots (same helper shape as
        locate) and traverses same-origin iframes, including nested
        frames and frames inside shadow roots, so a field inside
        an iframe reads the same as one in the top document. A
        cross-origin iframe is unreachable from parent JS, so a
        field there returns None and the caller must fall back to
        vision or a BiDi browsing-context call, never silently drop
        the target.
        """
        return self.evaluate(
            "return (function(){" + _FIND_JS +
            "const e=find(%s);"
            "if(!e) return null;"
            "return e.isContentEditable ? e.textContent : "
            "('value' in e ? e.value : null);})()" % json.dumps(selector))

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
            "return (function(){" + _FIND_JS +
            "const e=find(%s);"
            "if(!e) return null;"
            "/* verify_typed */ return {value: e.isContentEditable"
            " ? e.textContent : ('value' in e ? e.value : null),"
            " editable: !!e.isContentEditable};})()"
            % json.dumps(selector))
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
        events, so the flag stays clear) plus a MutationObserver for
        diagnostics. The listener records the field value at each
        trusted input event in a closure variable, exposed through
        a locked getter on the element itself
        (Object.defineProperty, non-configurable, no setter), so a
        page script cannot set it: there is no window property to
        forge (R10). typed_flag() reads the getter after the type
        step and requires it to equal the current value. A value
        that appears with no trusted input event must fail
        verification. TESTREPAIR item 7: the getter lives under a
        per-arm unpredictable property name
        (__agentCuTypedValue_<64-bit token>), so a page that
        pre-locks the old fixed name (or any guessed name) with a
        live-value getter before the arm cannot forge the flag: the
        arm's own name is fresh and unguessable, and re-arming
        always installs a new name. When defineProperty throws, the
        arm fails closed.
        """
        prop = '__agentCuTypedValue_' + secrets.token_hex(8)
        self._typed_flag_props[selector] = prop
        script = (
            "return (function(){" + _FIND_JS +
            "const sel=" + json.dumps(selector) + ";"
            "const e=find(sel);"
            "if(!e) return false;"
            "function valOf(el){"
            "return el.isContentEditable ? el.textContent : "
            "('value' in el ? el.value : null);"
            "}"
            "let lastTrusted=null;"
            "e.addEventListener('input', function(ev){"
            "if(ev.isTrusted) lastTrusted=valOf(e);"
            "});"
            "try{"
            "Object.defineProperty(e, " + json.dumps(prop) + ", {"
            "get:function(){return lastTrusted;},"
            "configurable:false, enumerable:false});"
            "}catch(_){"
            "return false;"
            "}"
            "try{"
            "const obs=new MutationObserver(function(){});"
            "obs.observe(e, {childList:true, characterData:true,"
            "subtree:true, attributes:false});"
            "Object.defineProperty(e, '__agentCuObserver', {"
            "value:obs, writable:false, configurable:false,"
            "enumerable:false});"
            "}catch(_){}"
            "/* zen_arm_typed_flag */ return true;})()")
        return bool(self.evaluate(script))

    def typed_flag(self, selector):
        """True when the last trusted input event's value equals the
        target's current value. A forged flag cannot be set (there
        is no window property; the value lives in the arm's closure
        behind a locked getter), and a sticky flag cannot pass a
        JS-set value: one keystroke recording 'h' does not equal a
        current 'hello'. Contenteditable values normalize trailing
        whitespace, the same as verify_typed. TESTREPAIR item 7:
        the getter is read under the per-arm unpredictable property
        name recorded by arm_typed_flag for this selector; a check
        on a selector never armed on this session returns False."""
        prop = self._typed_flag_props.get(selector)
        if prop is None:
            return False
        script = (
            "return (function(){/* zen_typed_flag */" + _FIND_JS +
            "const e=find(" + json.dumps(selector) + ");"
            "if(!e) return false;"
            "let last=null;"
            "try{last=e[" + json.dumps(prop) + "];}catch(_){return false;}"
            "if(last===null || last===undefined) return false;"
            "const cur=e.isContentEditable ? e.textContent : "
            "('value' in e ? e.value : null);"
            "if(e.isContentEditable && typeof last==='string' "
            "&& typeof cur==='string')"
            "return last.replace(/\\s+$/,'')===cur.replace(/\\s+$/,'');"
            "return last===cur;})()")
        return bool(self.evaluate(script))

    def sent_bubble_contains(self, text):
        """V12 finish gate: True when the thread DOM holds a sent
        bubble whose text is exactly the message (leaf elements only,
        so a container holding the whole thread cannot false-pass).
        This is the one check the type step cannot set: only Enter
        plus the app can put the bubble there. Returns False when no
        bubble holds the text."""
        return bool(self.evaluate(
            ("/* zen_sent_bubble */ return (function(){"
            "const want=%s;"
            + _FIND_JS +
            "function leaves(root, out){"
            "const all=root.querySelectorAll('*');"
            "for(const el of all){"
            "if(el.shadowRoot){leaves(el.shadowRoot, out);}"
            "if(!el.children || el.children.length===0){out.push(el);}"
            "}"
            "const frames=framesOf(root);"
            "for(const f of frames){"
            "try{leaves(f.contentWindow.document, out);}catch(_){}"
            "}"
            "return out;"
            "}"
            "const els=leaves(document, []);"
            "for(const el of els){"
            "if((el.textContent||'').trim()===want) return true;"
            "}"
            "return false;})()") % json.dumps(text)))

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
            "/* zen_harvest */ return (function(){"
            + _FIND_JS + _DEEP_ACTIVE_JS + _FRAME_POINT_JS +
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
            "const a=deepActive();"
            "for(const sel of %s){"
            "const e=find(sel);"
            "if(!e){out.items[sel]=null;continue;}"
            "const r=e.getBoundingClientRect();"
            "const x=r.left+r.width/2, y=r.top+r.height/2;"
            "const fp=framePoint(e, x, y);"
            "const hit=fp[0].elementFromPoint(fp[1], fp[2]);"
            "out.items[sel]={rect:{x:r.x,y:r.y,width:r.width,"
            "height:r.height,center_x:x,center_y:y},"
            "hit:!!hit&&(e===hit||(e.contains(hit)&&!interactive(hit))),"
            "focused:(a===e)};"
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
    p_eval = sub.add_parser(
        "eval", help="run JS in the current tab (debug mode only)")
    p_eval.add_argument("script")
    p_eval.add_argument(
        "--debug", action="store_true",
        help="intentional debug mode: allow arbitrary JS eval")
    p_loc = sub.add_parser("locate", help="exact rect of a selector")
    p_loc.add_argument("selector")
    sub.add_parser("kill-hung", help="kill hung remote-control clients")
    args = parser.parse_args()

    if args.cmd == "kill-hung":
        print(json.dumps({"killed": kill_hung_remote_clients()}, indent=1))
        return 0
    # CB-5: eval is debug-only in the CLI. The evaluate() transport
    # stays open for harvest/locate/hit_check; only the default agent
    # interface loses it. The refusal happens BEFORE any session
    # opens, so a bare `eval` never touches the live browser.
    if (args.cmd == "eval" and not args.debug
            and os.environ.get("CU_ZEN_DOM_DEBUG") != "1"):
        print(json.dumps({
            "ok": False,
            "error": ("zen_dom eval is debug-only (CB-5): "
                      "pass --debug or set CU_ZEN_DOM_DEBUG=1"),
        }))
        return 1
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

"""Zen DOM regressions: hung tab-switches must never escape raw (F3b).

Marionette tab-switch intermittently HANGS past the WebDriver timeout
(F3b Arm A run 2 at 30 s, Arm D run 1 at 10 s), and the raw TimeoutError
used to escape zen_dom.py _wd, which caught HTTPError only, killing the
whole live lane. Two fixes: _wd converts TimeoutError, OSError, and
URLError into ZenDomError; list_tabs targets one tab by known handle
index instead of scanning, and a full scan records a hung handle as an
error entry and keeps going (Arm D v2 pattern).

Run: python3 tests/test_zen_dom.py (stdlib runner at the bottom).
VM only. No laptop, no Zen, no geckodriver: the WebDriver transport is
faked below; _wd conversion is tested by mocking urlopen.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location(
    'zen_dom', ROOT / 'scripts' / 'zen_dom.py')
zen_dom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zen_dom)

ZenSession = zen_dom.ZenSession
ZenDomError = zen_dom.ZenDomError


class _TypedFlagDict(dict):
    """Models the locked-getter flag (AMEND4 item 7).

    Setting True records the field's current value as the
    last-trusted value (a trusted input event fired now); setting
    False clears it (_MISSING). The flag reads True only when the
    recorded value equals the field's current value, so a JS-set
    value after one keystroke does not verify. The dict holds the
    session so a replaced dom_fields still reads current.
    """

    _MISSING = object()

    def __init__(self, session):
        super().__init__()
        self.session = session

    def __setitem__(self, key, value):
        if value:
            field = self.session.dom_fields.get(key)
            super().__setitem__(
                key, self._MISSING if field is None
                else field.get('value'))
        else:
            super().__setitem__(key, self._MISSING)


class FakeWdSession(ZenSession):
    """A ZenSession whose WebDriver transport is a scripted fake.

    hang_handles: handles whose POST /window switch raises, simulating
    the intermittent Marionette hang. hang_error is the exception the
    fake raises: TimeoutError by default (what the real transport
    raises), or ZenDomError (what the real _wd converts it to).
    stuck_handles: handles whose POST /window switch reports success
    but leaves another tab selected (the R8 case: the switch does not
    take effect). hang_on_repeat: handles whose FIRST switch succeeds
    but whose SECOND switch hangs (the R6 scan case: the scan switches
    fine, the restore hangs). dom_fields scripts one DOM element per
    selector for the evaluate-based helpers: rect, focused, value,
    covered.
    """

    def __init__(self, handles, hang_handles=(), hang_error=None,
                 timeout_s=30, stuck_handles=(), hang_on_repeat=()):
        super().__init__(timeout_s=timeout_s)
        self.session = 'test-session-id'
        self._handles = list(handles)
        self._hang = set(hang_handles)
        self._hang_error = hang_error or TimeoutError('timed out')
        self._stuck = set(stuck_handles)
        self._hang_on_repeat = set(hang_on_repeat)
        self._switch_counts = {}
        self.current = handles[0] if handles else None
        self.calls = []
        self.titles = {h: ('Title ' + h[:8],
                           'https://example.com/' + h)
                       for h in handles}
        self.dom_origin = [100, 200]
        self.dom_inner = [901, 1176]
        self.dom_outer = [901, 1176]
        self.dom_factor = 1
        self.dom_fields = {}
        self.sent_bubbles = []
        self._armed = {}
        self._typed = _TypedFlagDict(self)
        self._MISSING = object()

    def _typed_flag(self, selector):
        # Faithful model of the locked-getter flag (AMEND4 item 7):
        # True only when a trusted input event was recorded AND the
        # recorded value still equals the field's current value. A
        # bare value change with no trusted event (a page script
        # setting el.value) leaves the flag clear, and a JS-set
        # value after one keystroke does not match the recorded
        # value, so the flag stays clear for it too.
        recorded = self._typed.get(selector, _TypedFlagDict._MISSING)
        if recorded is _TypedFlagDict._MISSING:
            return False
        field = self.dom_fields.get(selector)
        if field is None:
            return False
        return field.get('value') == recorded

    def _harvest(self):
        items = {}
        for sel, field in self.dom_fields.items():
            rect = field['rect']
            items[sel] = {
                'rect': {'x': rect['x'], 'y': rect['y'],
                         'width': rect['width'], 'height': rect['height'],
                         'center_x': rect['x'] + rect['width'] / 2,
                         'center_y': rect['y'] + rect['height'] / 2},
                'hit': not field.get('covered', False),
                'focused': bool(field.get('focused', False))}
        return {'moz_inner': list(self.dom_origin),
                'device_pixel_ratio': 1,
                'screen_pixels_per_css_pixel': 1,
                'zoom': 1,
                'inner_size': list(self.dom_inner),
                'outer_size': list(self.dom_outer),
                'items': items}

    def _eval(self, body):
        """Scripted JS evaluation for the DOM helpers.

        Dispatches on the script text (the fake knows the helper
        shapes). Marker comments first (the new helpers carry one),
        then the legacy shape checks. The selector comes from the
        evaluate args, or from the pierce/querySelector literal
        embedded in the helper scripts (the new scripts pass the
        selector as a pierce() argument, not a querySelector one).
        """
        import re
        script = (body or {}).get('script', '')
        args = (body or {}).get('args') or []
        selector = args[0] if args else None
        if selector is None:
            for pattern in (
                    r'querySelector\(("(?:[^"\\]|\\.)*")\)',
                    r'pierce\(("(?:[^"\\]|\\.)*")\s*,',
                    r'find\(("(?:[^"\\]|\\.)*")\)',
                    r'const sel=("(?:[^"\\]|\\.)*")',
                    r'__agentCuTyped\[("(?:[^"\\]|\\.)*")\]'):
                m = re.search(pattern, script)
                if m:
                    selector = json.loads(m.group(1))
                    break
        if 'zen_viewport_origin' in script:
            return [self.dom_origin[0], self.dom_origin[1],
                    self.dom_factor, self.dom_factor, 1,
                    self.dom_inner[0], self.dom_inner[1],
                    self.dom_outer[0], self.dom_outer[1]]
        if 'zen_display_metrics' in script:
            return {'mozInnerScreenX': self.dom_origin[0],
                    'mozInnerScreenY': self.dom_origin[1],
                    'devicePixelRatio': 1,
                    'screenPixelsPerCSSPixel': 1,
                    'zoom': 1,
                    'innerWidth': self.dom_inner[0],
                    'innerHeight': self.dom_inner[1],
                    'outerWidth': self.dom_outer[0],
                    'outerHeight': self.dom_outer[1]}
        if 'zen_harvest' in script:
            return self._harvest()
        if 'zen_arm_typed_flag' in script:
            field = self.dom_fields.get(selector) if selector else None
            self._armed[selector] = None if field is None \
                else field.get('value')
            self._typed[selector] = False
            return field is not None
        if 'zen_typed_flag' in script:
            return self._typed_flag(selector)
        if 'zen_sent_bubble' in script:
            m = re.search(r'const want=("(?:[^"\\]|\\.)*")', script)
            want = json.loads(m.group(1)) if m else None
            return want in self.sent_bubbles
        if 'verify_typed' in script:
            field = self.dom_fields.get(selector) if selector else None
            if field is None:
                return None
            return {'value': field.get('value'),
                    'editable': bool(field.get('contenteditable', False))}
        field = self.dom_fields.get(selector) if selector else None
        if 'mozInnerScreenX' in script:
            return list(self.dom_origin)
        if 'elementFromPoint' in script:
            return bool(field) and not field.get('covered', False)
        if 'activeElement' in script:
            return bool(field) and bool(field.get('focused', False))
        if 'textContent' in script:
            return None if field is None else field.get('value')
        if 'getBoundingClientRect' in script:
            if field is None:
                return None
            rect = field['rect']
            return {'x': rect['x'], 'y': rect['y'],
                    'width': rect['width'], 'height': rect['height'],
                    'center_x': rect['x'] + rect['width'] / 2,
                    'center_y': rect['y'] + rect['height'] / 2}
        raise AssertionError('unexpected script ' + script[:80])

    def _wd(self, method, path, body=None):
        self.calls.append((method, path, body))
        if path.endswith('/execute/sync'):
            return {'value': self._eval(body)}
        if path.endswith('/window/handles'):
            return {'value': list(self._handles)}
        if path.endswith('/window') and method == 'GET':
            return {'value': self.current}
        if path.endswith('/window') and method == 'POST':
            handle = body['handle']
            if handle in self._hang:
                raise self._hang_error
            self._switch_counts[handle] = \
                self._switch_counts.get(handle, 0) + 1
            if (handle in self._hang_on_repeat
                    and self._switch_counts[handle] > 1):
                raise self._hang_error
            if handle in self._stuck:
                return {'value': None}
            self.current = handle
            return {'value': None}
        if path.endswith('/title'):
            return {'value': self.titles[self.current][0]}
        if path.endswith('/url'):
            return {'value': self.titles[self.current][1]}
        raise AssertionError('unexpected ' + method + ' ' + path)

    def switches_to(self, handle):
        return [c for c in self.calls
                if c[0] == 'POST' and c[1].endswith('/window')
                and c[2] == {'handle': handle}]


class TestWdTimeoutConversion(unittest.TestCase):
    def _session(self):
        session = ZenSession(timeout_s=5)
        session.session = 'test-session-id'
        return session

    def test_timeout_error_becomes_zen_dom_error(self):
        # F3b: the exact failure that escaped raw from Arm A run 2 and
        # Arm D run 1.
        session = self._session()
        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               side_effect=TimeoutError('timed out')):
            with self.assertRaises(ZenDomError) as caught:
                session._wd('POST', '/session/test-session-id/window',
                            {'handle': 'abc'})
        self.assertIn('timed out', str(caught.exception))

    def test_socket_timeout_becomes_zen_dom_error(self):
        import socket
        session = self._session()
        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               side_effect=socket.timeout('timed out')):
            with self.assertRaises(ZenDomError):
                session._wd('GET', '/session/test-session-id/window/handles')

    def test_url_error_wrapping_timeout_becomes_zen_dom_error(self):
        # urllib wraps a socket timeout in a URLError whose reason is
        # the TimeoutError; that wrapper must convert too.
        import urllib.error
        session = self._session()
        wrapped = urllib.error.URLError(TimeoutError('timed out'))
        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               side_effect=wrapped):
            with self.assertRaises(ZenDomError):
                session._wd('GET', '/session/test-session-id/window/handles')

    def test_http_error_still_reports_status(self):
        # The pre-existing HTTPError branch is unchanged.
        import urllib.error
        session = self._session()
        body = json.dumps({'value': {'error': 'no such window'}}).encode()
        http_error = urllib.error.HTTPError(
            'http://127.0.0.1:4444/session/x', 404, 'Not Found', {}, None)
        http_error.read = lambda: body
        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               side_effect=http_error):
            with self.assertRaises(ZenDomError) as caught:
                session._wd('GET', '/session/test-session-id/title')
        self.assertIn('404', str(caught.exception))

    def test_success_still_returns_parsed_json(self):
        session = self._session()
        payload = json.dumps({'value': ['h1', 'h2']}).encode()

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return payload

        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               return_value=Resp()):
            result = session._wd(
                'GET', '/session/test-session-id/window/handles')
        self.assertEqual(result, {'value': ['h1', 'h2']})

    def test_non_json_response_becomes_zen_dom_error(self):
        # RT R5: a non-JSON body used to escape _wd as a raw
        # json.JSONDecodeError, contradicting the "never a raw
        # exception" docstring.
        session = self._session()

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return b'not json'

        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               return_value=Resp()):
            with self.assertRaises(ZenDomError):
                session._wd('GET', '/session/test-session-id/title')

    def test_bad_status_line_becomes_zen_dom_error(self):
        # RT R5: http.client.BadStatusLine is not an OSError or a
        # URLError, so it used to escape _wd raw.
        import http.client
        session = self._session()
        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               side_effect=http.client.BadStatusLine('bad')):
            with self.assertRaises(ZenDomError):
                session._wd('GET', '/session/test-session-id/title')

    def test_response_without_value_becomes_zen_dom_error(self):
        # RT R5: a JSON object without a "value" member used to escape
        # as a raw KeyError in the callers that read ["value"].
        session = self._session()
        payload = json.dumps({'state': 'ok'}).encode()

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return payload

        with mock.patch.object(zen_dom.urllib.request, 'urlopen',
                               return_value=Resp()):
            with self.assertRaises(ZenDomError) as caught:
                session._wd('GET', '/session/test-session-id/title')
        self.assertIn("value", str(caught.exception))


class TestTabAt(unittest.TestCase):
    def test_targets_known_index_without_scanning(self):
        # F3b Arm D v2: target handles[8] directly (BiDi index 8 is
        # example.com). With 3 handles, only the target is switched
        # to, never the others, then the original tab is restored.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles)
        tab = session.tab_at(2)
        self.assertEqual(tab['handle'], 'ccc33333')
        self.assertEqual(tab['url'], 'https://example.com/ccc33333')
        # The other handles are never switched to; exactly two POST
        # /window calls happen: target, then restore to the original.
        self.assertEqual(len(session.switches_to('bbb22222')), 0)
        self.assertEqual(len(session.switches_to('ccc33333')), 1)
        posts = [c for c in session.calls
                 if c[0] == 'POST' and c[1].endswith('/window')]
        self.assertEqual(len(posts), 2)
        self.assertEqual(session.current, 'aaa11111')

    def test_out_of_range_raises_zen_dom_error(self):
        session = FakeWdSession(['aaa11111', 'bbb22222'])
        with self.assertRaises(ZenDomError) as caught:
            session.tab_at(8)
        self.assertIn('out of range', str(caught.exception))
        with self.assertRaises(ZenDomError):
            session.tab_at(-1)
        # R10: the range check runs before current_handle, so an
        # out-of-range tab costs no round trip and no switch.
        posts = [c for c in session.calls
                 if c[0] == 'POST' and c[1].endswith('/window')]
        self.assertEqual(posts, [])

    def test_hang_on_target_raises_zen_dom_error_not_raw(self):
        # The hang converts (via _wd in production; via the fake's
        # ZenDomError here) and the original tab is still restored.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_handles={'ccc33333'},
                                hang_error=ZenDomError('transport failure'))
        with self.assertRaises(ZenDomError):
            session.tab_at(2)
        self.assertEqual(session.current, 'aaa11111')

    def test_switch_not_taking_effect_raises(self):
        # RT R8: a switch that reports success but leaves another tab
        # selected must not return that tab's title/URL as if it were
        # the requested one.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, stuck_handles={'ccc33333'})
        with self.assertRaises(ZenDomError) as caught:
            session.tab_at(2)
        self.assertIn('did not take effect', str(caught.exception))

    def test_failed_restore_is_raised_not_swallowed(self):
        # RT R6: when the original tab cannot be restored after the
        # read, tab_at raises instead of returning success while the
        # browser sits on the wrong tab.
        handles = ['aaa11111', 'bbb22222']
        session = FakeWdSession(handles, hang_handles={'aaa11111'},
                                hang_error=ZenDomError('transport failure'))
        with self.assertRaises(ZenDomError) as caught:
            session.tab_at(1)
        self.assertIn('could not be restored', str(caught.exception))
        self.assertEqual(session.current, 'bbb22222',
                         'left on the wrong tab, loudly reported')


class TestListTabsScan(unittest.TestCase):
    def test_hung_handle_stops_scan_and_raises_wedge(self):
        # RT R7: a hang means the session is wedged (F3b Arm E) and
        # only a restart clears it, so the scan stops after the first
        # hang instead of burning one 30 s timeout per handle (540 s
        # for 17 tabs). The wedge is raised loudly, the original tab
        # is restored, and later handles are never attempted.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_handles={'bbb22222'})
        with self.assertRaises(ZenDomError) as caught:
            session.list_tabs()
        self.assertIn('wedged', str(caught.exception))
        self.assertEqual(len(session.switches_to('ccc33333')), 0,
                         'the scan stopped; later handles were not tried')
        self.assertEqual(session.current, 'aaa11111')

    def test_raw_timeout_per_handle_stops_scan(self):
        # Defense in depth: even a raw TimeoutError escaping _wd is a
        # transport failure, so it stops the scan the same way.
        handles = ['aaa11111', 'bbb22222']
        session = FakeWdSession(handles, hang_handles={'bbb22222'},
                                hang_error=TimeoutError('timed out'))
        with self.assertRaises(ZenDomError) as caught:
            session.list_tabs()
        self.assertIn('wedged', str(caught.exception))
        self.assertEqual(session.current, 'aaa11111')

    def test_non_transport_error_recorded_and_scan_continues(self):
        # A per-handle failure that is NOT a hang (an HTTP-style
        # ZenDomError with no transport-failure text) is recorded as
        # an error entry and the scan continues to the next handle.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_handles={'bbb22222'},
                                hang_error=ZenDomError('no such window'))
        tabs = session.list_tabs()
        self.assertEqual(len(tabs), 3)
        self.assertEqual(tabs[0]['handle'], 'aaa11111')
        self.assertEqual(tabs[1], {'handle': 'bbb22222',
                                   'error': 'no such window'})
        self.assertEqual(tabs[2]['handle'], 'ccc33333')
        self.assertEqual(session.current, 'aaa11111')

    def test_failed_restore_after_scan_is_raised(self):
        # RT R6 on the full scan: a failed restore is raised, not
        # swallowed, so the caller knows the browser is on the wrong tab.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_on_repeat={'aaa11111'})
        with self.assertRaises(ZenDomError) as caught:
            session.list_tabs()
        self.assertIn('could not be restored', str(caught.exception))
        self.assertEqual(session.current, 'ccc33333',
                         'left on the last tab, loudly reported')

    def test_clean_scan_returns_all_tabs_and_restores_current(self):
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles)
        tabs = session.list_tabs()
        self.assertEqual([t['handle'] for t in tabs],
                         ['aaa11111', 'bbb22222', 'ccc33333'])
        self.assertTrue(all('title' in t and 'url' in t for t in tabs))
        self.assertEqual(session.current, 'aaa11111')


class TestDomHelpers(unittest.TestCase):
    """Item 12: cheap DOM grounding and verification, no screenshot.

    Every helper below is one JS eval through the scripted fake:
    viewport origin, rect-center image point, hit check, focus check,
    field value. No observe is taken anywhere in this flow.
    """

    def _session(self):
        session = FakeWdSession(['aaa11111'])
        # dom_origin is the WINDOW-relative mozInner pair (live C12
        # probe 03:36): [0, 0] here, so the absolute viewport origin
        # is the window origin itself.
        session.dom_origin = [0, 0]
        session.dom_fields = {
            '#msg-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                    'height': 63},
                            'focused': True, 'value': 'hello',
                            'covered': False},
            '#covered-btn': {'rect': {'x': 10, 'y': 10, 'width': 80,
                                      'height': 30},
                              'focused': False, 'value': None,
                              'covered': True},
        }
        return session

    def _meta(self):
        # The G30 Brave window: region [2533,914,901,1176], image
        # 901x1176, so image and region map 1:1. window_bounds is
        # the production shape (AMEND4 item 5): a region-only meta
        # is refused for grounding, so the fixture carries it.
        return {'image_size': [901, 1176],
                'region': [2533, 914, 901, 1176],
                'window_bounds': [2533, 914, 901, 1176]}

    def test_viewport_origin_adds_window_origin_to_moz_inner(self):
        # mozInnerScreen is WINDOW-relative (live C12 probe 03:36):
        # the absolute origin is the Hyprland window origin plus the
        # pair. The fake's mozInner is [0, 0] here, so the absolute
        # origin is the window origin itself.
        session = self._session()
        self.assertEqual(session.viewport_origin([2533, 914]), [2533, 914])

    def test_viewport_origin_probe_geometry(self):
        # The live C12 probe geometry: window origin (2509, 914),
        # mozInner (240, 8), viewport 1615x1160 -> absolute (2749, 922).
        session = self._session()
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        self.assertEqual(session.viewport_origin([2509, 914], [1863, 1176]),
                         [2749, 922])

    def test_viewport_origin_factor_two_geometry(self):
        # Unit rule (AMEND4 item 1): the given window size is the
        # Hyprland logical size, which equals CSS px numerically,
        # so it is passed as-is, never divided by the factor. At
        # monitor scale 2 the live C12 geometry is window (2509,
        # 914), size 1863x1176 logical px, mozInner (240, 8) CSS px,
        # inner 1615x1160 CSS px: the absolute origin is window
        # origin + mozInner * 2 = (2989, 930).
        session = self._session()
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        session.dom_factor = 2
        self.assertEqual(session.viewport_origin([2509, 914], [1863, 1176]),
                         [2989, 930])
        # The None branch takes the size from outerWidth/Height,
        # already CSS px, so it returns the same origin.
        self.assertEqual(session.viewport_origin([2509, 914]),
                         [2989, 930])
        # And impossible CSS geometry is refused at factor 2: the
        # window is only 1500x1000 CSS px, so mozInner + inner size
        # cannot close inside it.
        with self.assertRaises(ZenDomError):
            session.viewport_origin([2509, 914], [1500, 1000])

    def test_viewport_origin_requires_window_origin(self):
        # Without the Hyprland window origin the raw pair cannot be
        # placed on screen; returning it as-is was the old bug.
        session = self._session()
        with self.assertRaises(ZenDomError):
            session.viewport_origin()

    def test_viewport_origin_rejects_off_window_geometry(self):
        # Dimension closure: mozInner plus inner size must fit inside
        # the window, or the geometry is impossible and the call
        # fails closed instead of returning a wrong origin.
        session = self._session()
        session.dom_origin = [240, 8]
        session.dom_inner = [1863, 1176]
        session.dom_outer = [1863, 1176]
        with self.assertRaises(ZenDomError):
            session.viewport_origin([2509, 914], [1863, 1176])

    def _sequenced_session(self, moz_sequence, inner=(677, 1160),
                           outer=(925, 1176)):
        """Fake session whose origin reads serve moz pairs in order.

        Wraps evaluate: zen_viewport_origin scripts return the next
        9-number array from the sequence (repeating the last pair
        once exhausted, so a runaway loop is deterministic),
        everything else delegates to the real fake. Returns
        (session, calls) where calls['n'] counts the origin reads.
        """
        session = self._session()
        session.dom_inner = list(inner)
        session.dom_outer = list(outer)
        sequence = [list(m) for m in moz_sequence]
        calls = {'n': 0}
        original = session.evaluate

        def sequenced(script, args=None):
            if 'zen_viewport_origin' in (script or ''):
                calls['n'] += 1
                moz = (sequence[calls['n'] - 1]
                       if calls['n'] <= len(sequence) else sequence[-1])
                return [moz[0], moz[1], 1, 1, 1,
                        inner[0], inner[1], outer[0], outer[1]]
            return original(script, args)

        session.evaluate = sequenced
        return session, calls

    def test_viewport_origin_settles_after_stale_reads(self):
        # F2, ZT-B run 3: the send snapshot read moz (274, 66)
        # right after the tab switch, inside the ~0.5s stale window
        # (validator-proof v2: stale at t=0.047s and t=0.299s,
        # settled from t=0.552s). The origin must wait for the read
        # to settle instead of refusing on the first stale sample.
        # Sequence mimics the run-3 drift: stale, stale,
        # intermediate (253, 30), then settled (240, 8).
        session, calls = self._sequenced_session(
            [(274, 66), (274, 66), (253, 30),
             (240, 8), (240, 8), (240, 8)])
        origin = session.viewport_origin(
            [2509, 914], [925, 1176], settle_poll_s=0,
            settle_budget_s=5)
        self.assertEqual(origin, [2749, 922])
        self.assertEqual(calls['n'], 6)
        self.assertEqual(session.last_viewport_settle['settled_moz'],
                         [240, 8])
        self.assertEqual(session.last_viewport_settle['reads'], 6)

    def test_viewport_origin_refuses_when_never_settles(self):
        # A moz that never closes is refused fail-closed, even after
        # the settle budget: the refusal carries the last closure
        # error, and no origin is returned.
        session, calls = self._sequenced_session([(274, 66)])
        with self.assertRaisesRegex(ZenDomError, 'closure'):
            session.viewport_origin(
                [2509, 914], [925, 1176], settle_poll_s=0,
                settle_budget_s=0.05)
        self.assertGreater(calls['n'], 1)

    def test_viewport_origin_accepts_settled_first_read(self):
        # Already-settled geometry still takes three consecutive
        # equal reads: one sample cannot prove the value is not
        # mid-drift, so the settle requirement applies on every
        # unverified call.
        session, calls = self._sequenced_session(
            [(240, 8)], inner=(1615, 1160), outer=(1863, 1176))
        origin = session.viewport_origin(
            [2509, 914], [1863, 1176], settle_poll_s=0)
        self.assertEqual(origin, [2749, 922])
        self.assertEqual(calls['n'], 3)
        self.assertEqual(session.last_viewport_settle['reads'], 3)

    def test_viewport_origin_verified_path_skips_settle(self):
        # With a verified origin supplied, the reported moz is
        # irrelevant: the verified path takes one read as before
        # (v4-proven behavior) and never waits for the reported
        # value to settle.
        session, calls = self._sequenced_session([(274, 66)])
        origin = session.viewport_origin(
            [2509, 914], [925, 1176], verified_moz_inner=[240, 8])
        self.assertEqual(origin, [2749, 922])
        self.assertEqual(calls['n'], 1)
        self.assertIsNone(session.last_viewport_settle)

    def test_locate_point_is_rect_center_in_image(self):
        # The G30 field: rect x 86..526, y 1101..1164, center
        # (306,1132.5) in viewport coords. The viewport origin is the
        # window origin here, so the image point is the same pair.
        session = self._session()
        point = session.locate_point(self._meta(), '#msg-input')
        self.assertEqual(point, [306.0, 1132.5])

    def test_locate_point_missing_element_raises(self):
        session = self._session()
        with self.assertRaises(ZenDomError):
            session.locate_point(self._meta(), '#nope')

    def test_hit_check_passes_uncovered_fails_covered(self):
        session = self._session()
        self.assertTrue(session.hit_check('#msg-input'))
        self.assertFalse(session.hit_check('#covered-btn'))
        self.assertFalse(session.hit_check('#nope'))

    def test_focus_check_reads_active_element(self):
        session = self._session()
        self.assertTrue(session.focus_check('#msg-input'))
        self.assertFalse(session.focus_check('#covered-btn'))

    def test_field_value_and_verify_typed(self):
        session = self._session()
        self.assertEqual(session.field_value('#msg-input'), 'hello')
        self.assertTrue(session.verify_typed('#msg-input', 'hello'))
        self.assertFalse(session.verify_typed('#msg-input', 'goodbye'))
        self.assertIsNone(session.field_value('#nope'))

    def test_field_value_and_verify_typed_traverse_iframes(self):
        # R9, amend3 step 6: locate() already traverses same-origin
        # iframes, but field_value() and verify_typed() only pierced
        # shadow roots in the top document, so a target inside an
        # iframe grounded but never verified. Both now send the same
        # iframe traversal as locate(). A cross-origin frame throws
        # on contentWindow.document access inside the try, so the
        # read fails closed (None / False), never a wrong pass.
        session = ZenSession()
        captured = {}

        def _eval(script, args=None):
            captured['script'] = script
            if 'verify_typed' in script:
                return {'value': 'hello', 'editable': False}
            return 'hello'

        session.evaluate = _eval
        self.assertEqual(session.field_value('#msg-input'), 'hello')
        self.assertIn('contentWindow.document', captured['script'],
                      'field_value does not traverse iframes')
        self.assertIn('pierce', captured['script'])
        self.assertTrue(session.verify_typed('#msg-input', 'hello'))
        self.assertIn('contentWindow.document', captured['script'],
                      'verify_typed does not traverse iframes')
        self.assertIn('pierce', captured['script'])

    def test_verify_typed_normalizes_trailing_whitespace(self):
        # Contenteditable textContent carries a trailing newline the
        # typed text does not; the comparison normalizes it. A plain
        # input is compared exactly: a trailing space is a real
        # difference there.
        session = self._session()
        session.dom_fields['#ce-input'] = {
            'rect': {'x': 86, 'y': 1101, 'width': 440, 'height': 63},
            'focused': True, 'value': 'hello\n', 'covered': False,
            'contenteditable': True}
        self.assertTrue(session.verify_typed('#ce-input', 'hello'))
        session.dom_fields['#msg-input']['value'] = 'hello '
        self.assertFalse(session.verify_typed('#msg-input', 'hello'))

    def test_verify_typed_prefill_needs_typed_flag(self):
        # The field already holds the expected text before typing:
        # without a recorded typed event the check fails (a prefilled
        # value proves no typing happened). After a trusted input
        # event is recorded, the same value verifies.
        session = self._session()
        session.arm_typed_flag('#msg-input')
        self.assertFalse(session.verify_typed('#msg-input', 'hello',
                                              before='hello'))
        session._typed['#msg-input'] = True
        self.assertTrue(session.verify_typed('#msg-input', 'hello',
                                             before='hello'))

    def test_verify_typed_js_set_without_keystrokes_must_not_verify(self):
        # R10, substantive (amend3): the field starts EMPTY and a
        # page script sets the expected text with no keystrokes, so
        # no trusted input event fires and the V11 flag stays clear.
        # before='' (the field was empty) must NOT verify, even
        # though the value now equals the expected text. The old
        # code consulted the flag only in the prefill case
        # (before == expected), so this shape verified.
        session = self._session()
        session.dom_fields['#msg-input']['value'] = ''
        session.arm_typed_flag('#msg-input')
        # JS sets the value: no keystrokes, no trusted input event.
        session.dom_fields['#msg-input']['value'] = 'hello'
        self.assertFalse(session.typed_flag('#msg-input'))
        self.assertFalse(session.verify_typed('#msg-input', 'hello',
                                              before=''))
        # And a real trusted input event on the same shape DOES
        # verify: the flag, not the value alone, is the discriminator.
        session._typed['#msg-input'] = True
        self.assertTrue(session.verify_typed('#msg-input', 'hello',
                                             before=''))

    @unittest.skipUnless(shutil.which('node'),
                         'node is required to run production JS')
    def test_typed_flag_not_forgeable_via_window_property(self):
        # R10 (AMEND4 item 7): the production arm/typed_flag JS runs
        # under node against the redteam top-document shim. A page
        # script forges the old window property (whole-property
        # assignment; the arm creates no window property, so the
        # subscript form would throw) and sets the value, with zero
        # trusted input events. The flag must stay False: it reads
        # the locked getter on the element, never the window
        # property. The redteam F6 test's subscript forge line and
        # its value assertion are defective as written (see the
        # AMEND4 log); this test proves the substantive finding is
        # closed in the form the new design admits.
        from test_click3_redteam2 import (
            _capture_js, _run_node, _TOP_DOC_SHIM, _wrap_bare_return)
        # TESTREPAIR item 7: arm and flag share one session, so
        # the flag reads the per-arm property name the arm installed.
        session = zen_dom.ZenSession()
        arm = _capture_js('arm_typed_flag', '#msg-input', session=session)
        flag = _capture_js('typed_flag', '#msg-input', session=session)
        code = _TOP_DOC_SHIM + """
var __armed = """ + _wrap_bare_return(arm) + """;
window.__agentCuTyped = {'#msg-input': true};
__el.value = 'hello';
var __flag = """ + _wrap_bare_return(flag) + """;
console.log(JSON.stringify({armed: __armed, flag: __flag}));
"""
        out = json.loads(_run_node(code))
        self.assertTrue(out['armed'])
        self.assertFalse(out['flag'])

    @unittest.skipUnless(shutil.which('node'),
                         'node is required to run production JS')
    def test_typed_flag_not_forgeable_via_prelocked_getter(self):
        # TESTREPAIR item 7 (round 3, RT proof): a page that
        # pre-locks the property name with a live-value getter
        # BEFORE the arm defeats the old fixed-name design: the
        # arm's re-arm trust branch returned true for the
        # pre-locked getter, and the flag then read the live value
        # as if it were typed. The arm now installs its getter
        # under a per-arm unpredictable name, so the pre-locked
        # fixed name is irrelevant: the arm succeeds, and a
        # zero-event JS set still leaves the flag False.
        from test_click3_redteam2 import (
            _capture_js, _run_node, _TOP_DOC_SHIM, _wrap_bare_return)
        session = zen_dom.ZenSession()
        arm = _capture_js('arm_typed_flag', '#msg-input', session=session)
        flag = _capture_js('typed_flag', '#msg-input', session=session)
        code = (_TOP_DOC_SHIM
                + "Object.defineProperty(__el, '__agentCuTypedValue',"
                + " {get: function(){return __el.value;},"
                + " configurable: false, enumerable: false});\n"
                + "var __armed = " + _wrap_bare_return(arm) + ";\n"
                + "__el.value = 'hello';\n"
                + "var __flag = " + _wrap_bare_return(flag) + ";\n"
                + "console.log(JSON.stringify({armed: __armed,"
                " flag: __flag}));\n")
        out = json.loads(_run_node(code))
        self.assertTrue(out['armed'],
                        'the arm must succeed despite the pre-locked '
                        'fixed name: %s' % (out,))
        self.assertFalse(out['flag'],
                         'a pre-locked live-value getter forged the '
                         'typed flag with zero input events: %s' % (out,))

    def test_display_metrics_records_dpr_and_zoom(self):
        session = self._session()
        metrics = session.display_metrics()
        self.assertEqual(metrics['device_pixel_ratio'], 1)
        self.assertEqual(metrics['screen_pixels_per_css_pixel'], 1)
        self.assertEqual(metrics['zoom'], 1)
        self.assertEqual(metrics['moz_inner'], [0, 0])
        self.assertEqual(metrics['inner_size'], [901, 1176])

    def test_harvest_returns_one_shot_inventory(self):
        session = self._session()
        result = session.harvest(['#msg-input', '#covered-btn'])
        self.assertEqual(result['moz_inner'], [0, 0])
        self.assertEqual(result['device_pixel_ratio'], 1)
        self.assertEqual(result['screen_pixels_per_css_pixel'], 1)
        self.assertEqual(result['zoom'], 1)
        item = result['items']['#msg-input']
        self.assertEqual(item['rect']['x'], 86)
        self.assertTrue(item['hit'])
        self.assertTrue(item['focused'])
        self.assertFalse(result['items']['#covered-btn']['hit'])
        self.assertIsNone(result['items'].get('#nope')
                          if '#nope' in result['items'] else None)

    def test_sent_bubble_contains(self):
        session = self._session()
        session.sent_bubbles = ['hello']
        self.assertTrue(session.sent_bubble_contains('hello'))
        self.assertFalse(session.sent_bubble_contains('goodbye'))

    def test_arm_and_typed_flag(self):
        session = self._session()
        self.assertTrue(session.arm_typed_flag('#msg-input'))
        self.assertFalse(session.typed_flag('#msg-input'))
        session._typed['#msg-input'] = True
        self.assertTrue(session.typed_flag('#msg-input'))
        self.assertFalse(session.arm_typed_flag('#nope'))

    def test_main_list_fails_cleanly_on_wedged_session(self):
        # Item D: a wedged session used to die with a traceback; the
        # CLI must fail cleanly with one JSON error object and exit 1.
        class WedgedSession:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                raise ZenDomError('session wedged: hang on switch')

            def __exit__(self, *exc):
                return False

        import io
        from contextlib import redirect_stdout
        saved_argv = sys.argv
        saved_session = zen_dom.ZenSession
        try:
            sys.argv = ['zen_dom.py', 'list']
            zen_dom.ZenSession = WedgedSession
            out = io.StringIO()
            with redirect_stdout(out):
                code = zen_dom.main()
        finally:
            sys.argv = saved_argv
            zen_dom.ZenSession = saved_session
        self.assertEqual(code, 1)
        payload = json.loads(out.getvalue())
        self.assertFalse(payload['ok'])
        self.assertIn('wedged', payload['error'])

    def test_dom_helpers_take_no_observe(self):
        # The whole grounding + verification flow is JS evals: the
        # fake records every _wd call, and none of them is an
        # observation. (zen_dom has no observe call at all; the point
        # is that the helpers do not need one.)
        session = self._session()
        session.locate_point(self._meta(), '#msg-input')
        session.hit_check('#msg-input')
        session.focus_check('#msg-input')
        session.verify_typed('#msg-input', 'hello')
        self.assertTrue(all(c[1].endswith('/execute/sync')
                            for c in session.calls),
                        'only JS evals, no observe call')


NODE = shutil.which('node')


def _capture_js(method_name, *args):
    """The exact JS string a zen_dom helper sends to evaluate()."""
    session = zen_dom.ZenSession()
    captured = {}

    def _eval(script, args=None):
        captured['script'] = script
        return None

    session.evaluate = _eval
    getattr(session, method_name)(*args)
    return captured['script']


def _run_node(code):
    proc = subprocess.run([NODE, '-e', code], capture_output=True,
                          text=True, timeout=20)
    if proc.returncode != 0:
        raise AssertionError('node failed: ' + proc.stderr[:500])
    return proc.stdout.strip()


class TestFaithfulShadowShim(unittest.TestCase):
    """R7 re-run with a FAITHFUL shim (AMEND4 item 2, C3 step-8).

    The frozen R7 test stubs document.querySelector to return the
    shadow-nested input directly, which a real browser never does:
    querySelector cannot see into a shadow root. That stub let a
    querySelector-only focus_check pass. This test uses a faithful
    shim: querySelector returns null for the shadow-nested input,
    and the host is reachable only through querySelectorAll('*')
    plus shadowRoot recursion. Only a real pierce/find passes it.
    Would fail on the pre-AMEND4 code (querySelector-only lookup
    returns null, focus_check False); passes with find().
    """

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_focus_check_faithful_shadow_shim(self):
        from test_click3_redteam2 import _wrap_bare_return
        script = _capture_js('focus_check', '#msg-input')
        shim = (
            "var __inner = {tagName: 'INPUT', isContentEditable:"
            " false, readOnly: false};\n"
            "var __shadow = {activeElement: __inner,\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __inner : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __host = {tagName: 'DIV', shadowRoot: __shadow};\n"
            "var document = {querySelector: function(sel){"
            " return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === '*' ? [__host] : []; },\n"
            " activeElement: __host};\n")
        out = _run_node(shim + 'console.log(JSON.stringify(' + _wrap_bare_return(script)
                        + '));')
        self.assertEqual(json.loads(out), True,
                         'focus_check failed a focused shadow input '
                         'under a faithful shim: %s' % (out,))

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_hit_check_faithful_shadow_shim(self):
        from test_click3_redteam2 import _wrap_bare_return
        script = _capture_js('hit_check', '#msg-input')
        shim = (
            "var __inner = {tagName: 'INPUT', isContentEditable:"
            " false, readOnly: false,\n"
            " getBoundingClientRect: function(){ return {left: 10,"
            " top: 10, width: 80, height: 30, x: 10, y: 10}; },\n"
            " contains: function(el){ return el === __inner; }};\n"
            "var __shadow = {activeElement: null,\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __inner : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __host = {tagName: 'DIV', shadowRoot: __shadow};\n"
            "var document = {querySelector: function(sel){"
            " return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === '*' ? [__host] : []; },\n"
            " activeElement: __host,\n"
            " elementFromPoint: function(x, y){ return __inner; }};\n")
        out = _run_node(shim + 'console.log(JSON.stringify(' + _wrap_bare_return(script)
                        + '));')
        self.assertEqual(json.loads(out), True,
                         'hit_check failed an uncovered shadow input '
                         'under a faithful shim: %s' % (out,))


class TestGeckodriverDefault(unittest.TestCase):
    """R14: the geckodriver default must survive /tmp being wiped.

    ZEN_GECKODRIVER wins when set; otherwise the persistent install
    at ~/.local/bin/geckodriver wins when present; the /tmp path is
    only the last resort. Uses a temp home so the real home is never
    touched.
    """

    def setUp(self):
        import tempfile
        self._td = tempfile.TemporaryDirectory()
        self.home = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def _install(self):
        target = self.home / '.local' / 'bin' / 'geckodriver'
        target.parent.mkdir(parents=True)
        target.write_text('fake')
        return str(target)

    def test_env_wins_over_installed(self):
        self._install()
        self.assertEqual(
            zen_dom._default_geckodriver(
                home=self.home,
                env={'ZEN_GECKODRIVER': '/opt/custom/geckodriver'}),
            '/opt/custom/geckodriver')

    def test_installed_persistent_path_wins_over_tmp(self):
        want = self._install()
        self.assertEqual(
            zen_dom._default_geckodriver(home=self.home, env={}), want)

    def test_tmp_fallback_when_nothing_installed(self):
        self.assertEqual(
            zen_dom._default_geckodriver(home=self.home, env={}),
            '/tmp/geckodriver')


class TestPillGate(unittest.TestCase):
    """R3 fail-closed pill gate in ZenSession.__enter__/_cleanup.

    No Zen, no geckodriver: Popen, _wait_http and _wd are faked, and
    the overlay CLI is faked at the _run_overlay_cli seam (the same
    seam CU_OVERLAY_PY exercises in production).
    """

    def _fake_enter_env(self, pill_reply):
        """Patch the session-start surroundings; return (events, patches).

        pill_reply: the dict the fake overlay acquire returns, or an
        exception instance the fake overlay raises.
        """
        events = []

        def fake_overlay(args, timeout_s=30):
            events.append(('overlay', args[0]))
            if isinstance(pill_reply, BaseException):
                raise pill_reply
            if args[0] == 'acquire':
                return pill_reply
            return {'visible': False, 'holders': {}}

        class FakeProc:
            def poll(self):
                return None

            def terminate(self):
                events.append(('gecko', 'terminate'))

            def wait(self, timeout=None):
                return 0

            def kill(self):
                events.append(('gecko', 'kill'))

        def fake_popen(*args, **kwargs):
            events.append(('gecko', 'spawn'))
            return FakeProc()

        def fake_wd(self, method, path, body=None):
            events.append(('wd', method, path))
            if path == '/session':
                return {'value': {'sessionId': 'pill-test-session'}}
            return {'value': None}

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patches = [
            mock.patch.object(zen_dom, '_run_overlay_cli', fake_overlay),
            mock.patch.object(zen_dom.subprocess, 'Popen', fake_popen),
            mock.patch.object(zen_dom, '_wait_http',
                              lambda *a, **k: True),
            mock.patch.object(ZenSession, '_wd', fake_wd),
            mock.patch.object(
                zen_dom, 'LOCK_PATH', Path(tmp.name) / 'zen_dom.lock'),
            mock.patch.dict(os.environ, {'CU_ZEN_PILL': '1'}),
        ]
        return events, patches

    def _run_patches(self, patches):
        for patcher in patches:
            patcher.start()
        self.addCleanup(lambda: [p.stop() for p in reversed(patches)])

    def test_session_refused_without_pill(self):
        # No pill, no session: __enter__ raises before geckodriver
        # spawns, so nothing controllable ever exists invisibly.
        events, patches = self._fake_enter_env(
            {'visible': False, 'holders': {}})
        self._run_patches(patches)
        with self.assertRaises(ZenDomError) as caught:
            with ZenSession():
                pass
        self.assertIn('pill unavailable', str(caught.exception))
        self.assertNotIn(('gecko', 'spawn'), events,
                         'geckodriver must not spawn without the pill')

    def test_session_acquires_before_spawn_and_releases_on_exit(self):
        events, patches = self._fake_enter_env(
            {'visible': True, 'holders': {}})
        self._run_patches(patches)
        with ZenSession() as session:
            self.assertEqual(session.session, 'pill-test-session')
        kinds = [(e[0], e[1]) for e in events]
        self.assertLess(kinds.index(('overlay', 'acquire')),
                        kinds.index(('gecko', 'spawn')),
                        'pill must be up before geckodriver spawns')
        self.assertEqual(kinds.count(('overlay', 'acquire')), 1)
        self.assertEqual(kinds.count(('overlay', 'release')), 1,
                         'exit must release exactly what enter acquired')
        self.assertLess(kinds.index(('gecko', 'spawn')),
                        kinds.index(('overlay', 'release')))

    def test_pill_opt_out_skips_gate(self):
        # CU_ZEN_PILL=0 is the fixture-only escape (mirrors
        # CU_CDP_PILL=0): the overlay is never consulted.
        events, patches = self._fake_enter_env(
            ZenDomError('pill unavailable: must not be consulted'))
        self._run_patches(patches)
        with mock.patch.dict(os.environ, {'CU_ZEN_PILL': '0'}):
            with ZenSession() as session:
                self.assertEqual(session.session, 'pill-test-session')
        self.assertEqual([e for e in events if e[0] == 'overlay'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

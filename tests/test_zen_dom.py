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
import sys
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
        self.dom_fields = {}

    def _eval(self, body):
        """Scripted JS evaluation for the DOM helpers.

        Dispatches on the script text (the fake knows the helper
        shapes): viewport origin, elementFromPoint hit, activeElement
        focus, field value, and locate rects. The selector comes from
        the evaluate args (locate) or from the querySelector literal
        embedded in the helper scripts.
        """
        import re
        script = (body or {}).get('script', '')
        args = (body or {}).get('args') or []
        selector = args[0] if args else None
        if selector is None:
            m = re.search(r'querySelector\(("(?:[^"\\]|\\.)*")\)', script)
            if m:
                selector = json.loads(m.group(1))
        if 'mozInnerScreenX' in script:
            return list(self.dom_origin)
        field = self.dom_fields.get(selector) if selector else None
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
        session.dom_origin = [2533, 914]
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
        # 901x1176, so image and region map 1:1.
        return {'image_size': [901, 1176],
                'region': [2533, 914, 901, 1176]}

    def test_viewport_origin_returns_moz_inner_screen(self):
        session = self._session()
        self.assertEqual(session.viewport_origin(), [2533, 914])

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


if __name__ == '__main__':
    unittest.main(verbosity=2)

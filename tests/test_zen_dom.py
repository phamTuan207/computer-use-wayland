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
    """

    def __init__(self, handles, hang_handles=(), hang_error=None,
                 timeout_s=30):
        super().__init__(timeout_s=timeout_s)
        self.session = 'test-session-id'
        self._handles = list(handles)
        self._hang = set(hang_handles)
        self._hang_error = hang_error or TimeoutError('timed out')
        self.current = handles[0] if handles else None
        self.calls = []
        self.titles = {h: ('Title ' + h[:8],
                           'https://example.com/' + h)
                       for h in handles}

    def _wd(self, method, path, body=None):
        self.calls.append((method, path, body))
        if path.endswith('/window/handles'):
            return {'value': list(self._handles)}
        if path.endswith('/window') and method == 'GET':
            return {'value': self.current}
        if path.endswith('/window') and method == 'POST':
            handle = body['handle']
            if handle in self._hang:
                raise self._hang_error
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

    def test_hang_on_target_raises_zen_dom_error_not_raw(self):
        # The hang converts (via _wd in production; via the fake's
        # ZenDomError here) and the original tab is still restored.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_handles={'ccc33333'},
                                hang_error=ZenDomError('transport failure'))
        with self.assertRaises(ZenDomError):
            session.tab_at(2)
        self.assertEqual(session.current, 'aaa11111')


class TestListTabsScan(unittest.TestCase):
    def test_hung_handle_recorded_and_scan_continues(self):
        # F3b Arm A run 2 shape: one handle hangs mid-scan. The scan
        # must record that handle as an error entry and return the
        # rest, instead of dying mid-loop with the hung handle
        # unrecorded.
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles, hang_handles={'bbb22222'})
        tabs = session.list_tabs()
        self.assertEqual(len(tabs), 3)
        self.assertEqual(tabs[0]['handle'], 'aaa11111')
        self.assertEqual(tabs[1], {'handle': 'bbb22222',
                                   'error': 'timed out'})
        self.assertEqual(tabs[2]['handle'], 'ccc33333')
        self.assertEqual(session.current, 'aaa11111')

    def test_raw_timeout_per_handle_is_caught_too(self):
        # Defense in depth (Arm D v2 except clause): even a raw
        # TimeoutError escaping _wd is caught per handle, never raw
        # out of list_tabs.
        handles = ['aaa11111', 'bbb22222']
        session = FakeWdSession(handles, hang_handles={'bbb22222'},
                                hang_error=TimeoutError('timed out'))
        tabs = session.list_tabs()
        self.assertEqual(tabs[1]['handle'], 'bbb22222')
        self.assertIn('timed out', tabs[1]['error'])

    def test_clean_scan_returns_all_tabs_and_restores_current(self):
        handles = ['aaa11111', 'bbb22222', 'ccc33333']
        session = FakeWdSession(handles)
        tabs = session.list_tabs()
        self.assertEqual([t['handle'] for t in tabs],
                         ['aaa11111', 'bbb22222', 'ccc33333'])
        self.assertTrue(all('title' in t and 'url' in t for t in tabs))
        self.assertEqual(session.current, 'aaa11111')


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Unit tests for the W-ZENPROOF2-FIX changes (no live Zen touch).

Guards the run 2 incident (improvements/w-zenproof2-log.md
section 6): attempt 2 closed the owner's Muse chat tab because
POST /window/new did not make the scratch tab current, the
navigate rewrote the owner's tab, and the open exception handler
deleted the current window blind. These tests run cmd_open,
cmd_switch, cmd_eval, and cmd_close against a fake Marionette
session that models that exact misfire, and prove:

- open refuses to navigate or delete when the new tab was not
  made current (fix c),
- open deletes only when the current tab is the fixture tab by
  URL AND by handle (amend F1: the post-navigate handle
  re-check plus the handler handle check),
- open refuses when the new tab does not increase the tab count
  (amend C4),
- the open handler's no-delete branch: a navigate failure or a
  wrong-URL navigate deletes nothing (amend C1),
- the scratch tab is identified by URL substring, never by
  document.title (fix a),
- switch/eval/close resolve tabs by URL fresh per session, never
  by a stored handle (fix b),
- the fake models unreadable tabs (error entries) and a
  silently failed scan restore (amend F3), and _restore_original
  reports scan_error and restore_failed instead of mislabelling
  or raising (amend C5),
- open refuses when /window/new returns an existing handle even
  when it still creates a tab (amend 2, Redteam H1: the count
  gate alone cannot catch that),
- _restore_original records None instead of raising when the
  title and URL reads fail after a scan failure (amend 2,
  Redteam H2),
- phase 4 (re-switch plus snapshot URL gate) is executed by
  behavioral tests on a real Runner, not for the first time in
  a live run (amend 2, Council 2 C1),
- open refuses when the handle set after /window/new differs
  from before by anything other than exactly the new handle
  added and nothing removed (a different singleton added, an
  empty added set, or anything removed also refuses), which a
  concurrent open plus close plus a stale-handle return would
  otherwise defeat (amend 3, Redteam P-C),
- open also requires the same exact difference against a second
  baseline captured immediately before POST /window/new, which
  a concurrent open at the pre-check scan plus a stale return
  without creation would otherwise defeat (amend 4, Redteam
  H1); a concurrent open during the POST itself plus a stale
  return still defeats both baselines and is pinned here as a
  known residual, not fixed (amend 4, Redteam G1),
- phase 4's helper records hypr calls too and returns them on
  raise, so the active-window test asserts no switch or send ran
  before the raise, and the identity test pins hypr first, then
  switch, then send (amend 4, Redteam H3),
- phase 4's active-window check and final ok/completed gate
  are executed by behavioral tests, and the helper pins the
  call order (switch before send) and the program identity
  (SEND_PROGRAM) (amend 3, Council 2 C1 + Redteam H3/C2).

No live tab is opened, navigated, or deleted. The fake session
never touches a real browser.
"""
import importlib.util
import sys
import types
import unittest
import uuid
from pathlib import Path
from unittest import mock

RUNS_DIR = Path(__file__).resolve().parents[1] / 'improvements' / 'c5-zenproof-runs'


class _FakeZenDomError(Exception):
    pass


def _load_zen_tab():
    """Import zen-tab.py with a stub zen_dom (the VM has no
    /home/james path). The stub is restored in sys.modules right
    after the import; zen-tab.py keeps its own reference to it.
    """
    stub = types.ModuleType('zen_dom')
    stub.ZenDomError = _FakeZenDomError
    stub.ZenSession = object
    stub.kill_hung_remote_clients = lambda: 0
    original = sys.modules.get('zen_dom')
    sys.modules['zen_dom'] = stub
    try:
        spec = importlib.util.spec_from_file_location(
            'zen_tab_under_test', str(RUNS_DIR / 'zen-tab.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if original is None:
            del sys.modules['zen_dom']
        else:
            sys.modules['zen_dom'] = original
    return module


zen_tab = _load_zen_tab()
ZenDomError = _FakeZenDomError

OWNER_URL = 'https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93'
FIXTURE_URL = ('file:///home/james/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=zen')
FIXTURE_SUBSTR = 'two_vision_fixture.html?clone=zen'


class FakeSession:
    """A Marionette session over an in-memory tab list.

    select_new models whether POST /window/new makes the new tab
    current (False reproduces the run 2 misfire). select_works
    models whether an explicit POST /window select takes effect.
    h1_for_fixture is the H1 text the fixture page reports.
    error_entry_urls models tabs whose title/URL read failed:
    their list_tabs entries carry {handle, error} with no URL,
    exactly like the real list_tabs (Redteam F3a). restore_fails
    models a list_tabs whose restore leaves the last-scanned tab
    current without raising, because _try_restore does not
    verify the switch took effect (Redteam F3b).
    """

    def __init__(self, tabs, current_index=0, select_new=True,
                 select_works=True, h1_for_fixture='Clone zen thread',
                 error_entry_urls=(), restore_fails=False):
        self.tabs = [dict(t) for t in tabs]
        self.current = self.tabs[current_index]['handle']
        self.select_new = select_new
        self.select_works = select_works
        self.h1_for_fixture = h1_for_fixture
        self.error_entry_urls = set(error_entry_urls)
        self.restore_fails = restore_fails
        self.session = 'fake-session-1'
        self.deleted = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def _cur_tab(self):
        for tab in self.tabs:
            if tab['handle'] == self.current:
                return tab
        return None

    def _wd(self, method, path, body=None):
        if method == 'GET' and path.endswith('/window/handles'):
            return {'value': [t['handle'] for t in self.tabs]}
        if method == 'GET' and path.endswith('/window'):
            return {'value': self.current}
        if method == 'GET' and path.endswith('/title'):
            tab = self._cur_tab()
            return {'value': tab['title'] if tab else ''}
        if method == 'GET' and path.endswith('/url'):
            tab = self._cur_tab()
            return {'value': tab['url'] if tab else ''}
        if method == 'POST' and path.endswith('/window/new'):
            handle = uuid.uuid4().hex
            self.tabs.append({'handle': handle, 'title': '',
                              'url': 'about:blank'})
            if self.select_new:
                self.current = handle
            return {'value': {'handle': handle}}
        if method == 'POST' and path.endswith('/window'):
            handle = (body or {}).get('handle')
            if (self.select_works and handle in
                    [t['handle'] for t in self.tabs]):
                self.current = handle
            return {'value': handle}
        if method == 'POST' and path.endswith('/url'):
            tab = self._cur_tab()
            url = (body or {}).get('url', '')
            tab['url'] = url
            tab['title'] = ('Two-vision benchmark fixture'
                            if 'two_vision_fixture.html' in url else '')
            return {}
        if method == 'POST' and path.endswith('/execute/sync'):
            return {'value': self.evaluate(
                (body or {}).get('script', ''))}
        if method == 'DELETE' and path.endswith('/window'):
            tab = self._cur_tab()
            if tab is None:
                return {}
            index = self.tabs.index(tab)
            self.deleted.append(tab['url'])
            del self.tabs[index]
            if self.tabs:
                self.current = self.tabs[
                    min(index, len(self.tabs) - 1)]['handle']
            else:
                self.current = None
            return {}
        raise AssertionError('fake got an unexpected call: %s %s'
                             % (method, path))

    def evaluate(self, script, args=None):
        if 'elementFromPoint' in script:
            return 'msg-input'
        if 'getBoundingClientRect' in script:
            # #msg-input exists only on the fixture page, so the
            # rect is tab-aware: on any other tab there is no
            # such element and the driver must refuse. (The
            # elementFromPoint branch above is checked first, but
            # the driver reads the rect before it, so a None rect
            # is what stops the run on the wrong tab.)
            tab = self._cur_tab()
            if tab is not None and FIXTURE_SUBSTR in tab['url']:
                return {'x': 10, 'y': 10, 'width': 320, 'height': 40}
            return None
        if 'innerWidth' in script:
            return {'innerWidth': 1280, 'innerHeight': 800,
                    'hasFocus': True}
        if 'readyState' in script:
            return 'complete'
        if "getElementById('title')" in script:
            tab = self._cur_tab()
            if tab is not None and FIXTURE_SUBSTR in tab['url']:
                return self.h1_for_fixture
            return None
        if script.strip() == 'return (1+1);':
            return 2
        raise AssertionError('fake cannot evaluate: %r' % (script,))

    def list_tabs(self, handle_index=None):
        entries = []
        for t in self.tabs:
            if t['url'] in self.error_entry_urls:
                # A tab whose title/URL read failed: the real
                # list_tabs returns {handle, error} with no URL.
                # _find_in_scan skips such entries, never matches
                # them.
                entries.append({'handle': t['handle'][:8],
                                'error': 'read failed'})
            else:
                entries.append({'handle': t['handle'][:8],
                                'title': t['title'], 'url': t['url']})
        if self.restore_fails:
            # The real list_tabs switches through every tab and
            # restores the original, but _try_restore does not
            # verify the switch took effect: a silent restore
            # failure leaves the last-scanned tab current and the
            # scan still returns normally.
            if self.tabs:
                self.current = self.tabs[-1]['handle']
        return entries

    def harvest(self, selectors):
        return {'items': {'#msg-input': {
            'rect': {'x': 10, 'y': 10, 'width': 320, 'height': 40},
            'state': ''}}}


def _owner_tabs():
    return [
        {'handle': uuid.uuid4().hex, 'title': 'Chat - Muse',
         'url': OWNER_URL},
        {'handle': uuid.uuid4().hex, 'title': '',
         'url': 'https://example.com/'},
    ]


class _StaleHandleWithTab(FakeSession):
    """POST /window/new creates a tab (count +1) but returns an
    EXISTING handle (the owner tab's). Adapted from the redteam
    amend repro /tmp/redteam-amend-repro-h1.py. The count gate
    alone cannot catch this: the count grows by exactly 1, so
    only the membership check (new_handle in before) refuses.
    """

    def _wd(self, method, path, body=None):
        if method == 'POST' and path.endswith('/window/new'):
            handle = uuid.uuid4().hex
            self.tabs.append({'handle': handle, 'title': '',
                              'url': 'about:blank'})
            if self.select_new:
                self.current = handle
            return {'value': {'handle': self.tabs[0]['handle']}}
        return super()._wd(method, path, body)


class ZenTabFixTest(unittest.TestCase):
    def _run_cmd(self, fake, func, *args):
        with mock.patch.object(zen_tab, '_session',
                               lambda: fake):
            return func(*args)

    def test_open_happy_path_keeps_owner_tab(self):
        fake = FakeSession(_owner_tabs(), current_index=0)
        result = self._run_cmd(fake, zen_tab.cmd_open)
        self.assertTrue(result['ok'])
        self.assertEqual(result['selected_by'], 'window/new')
        self.assertIn(FIXTURE_SUBSTR, result['url'])
        self.assertEqual(result['h1'], 'Clone zen thread')
        self.assertEqual(result['title'],
                         'Two-vision benchmark fixture')
        self.assertEqual(result['count_after'],
                         result['count_before'] + 1)
        self.assertEqual(result['url_before'], OWNER_URL)
        urls = [t['url'] for t in fake.tabs]
        self.assertIn(OWNER_URL, urls)
        self.assertIn(FIXTURE_URL, urls)
        self.assertEqual(fake._cur_tab()['url'], FIXTURE_URL)

    def test_open_new_tab_not_selected_explicit_select_works(self):
        fake = FakeSession(_owner_tabs(), current_index=0,
                           select_new=False, select_works=True)
        result = self._run_cmd(fake, zen_tab.cmd_open)
        self.assertTrue(result['ok'])
        self.assertEqual(result['selected_by'], 'explicit-select')
        self.assertIn(FIXTURE_SUBSTR, result['url'])
        urls = [t['url'] for t in fake.tabs]
        self.assertIn(OWNER_URL, urls)

    def test_open_new_tab_never_current_refuses_without_touch(self):
        """Regression for the run 2 incident: the new tab is
        never made current and the explicit select does not take
        effect. Open must raise BEFORE any navigate or DELETE:
        the owner's tab URL is unchanged, no tab is closed, and
        the owner tab is still current.
        """
        fake = FakeSession(_owner_tabs(), current_index=0,
                           select_new=False, select_works=False)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('not made current', str(caught.exception))
        # The /window/new tab itself exists (about:blank, never
        # navigated), but nothing was deleted and the owner's tab
        # is untouched and still current. Leaving the empty tab
        # is the fail-closed outcome: the select that would let
        # us close it is exactly what just failed, and deleting
        # the current window would close the owner's tab.
        self.assertEqual(len(fake.tabs), 3)
        self.assertEqual(fake.deleted, [])
        self.assertEqual(fake._cur_tab()['url'], OWNER_URL)
        self.assertEqual(fake.tabs[0]['url'], OWNER_URL)
        self.assertEqual(fake.tabs[2]['url'], 'about:blank')

    def test_open_wrong_h1_closes_only_scratch(self):
        fake = FakeSession(_owner_tabs(), current_index=0,
                           h1_for_fixture='Wrong title')
        with self.assertRaises(ZenDomError):
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertEqual(len(fake.tabs), 2)
        self.assertEqual(fake.deleted, [FIXTURE_URL])
        self.assertEqual(fake._cur_tab()['url'], OWNER_URL)

    def test_open_refuses_when_fixture_tab_already_open(self):
        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = FakeSession(tabs, current_index=0)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('already shows the fixture URL',
                      str(caught.exception))
        self.assertEqual(len(fake.tabs), 3)
        self.assertEqual(fake.deleted, [])

    def test_switch_eval_close_by_url(self):
        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = FakeSession(tabs, current_index=0)
        switched = self._run_cmd(fake, zen_tab.cmd_switch,
                                 FIXTURE_SUBSTR)
        self.assertTrue(switched['ok'])
        self.assertIn(FIXTURE_SUBSTR, switched['url'])
        value = self._run_cmd(fake, zen_tab.cmd_eval,
                              FIXTURE_SUBSTR, '1+1')
        self.assertEqual(value['value'], 2)
        self.assertIn(FIXTURE_SUBSTR, value['url'])
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertEqual(closed['count_before'], 3)
        self.assertEqual(closed['count_after'], 2)
        self.assertEqual(closed['current_url'], OWNER_URL)
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])

    def test_close_when_scratch_already_gone(self):
        fake = FakeSession(_owner_tabs(), current_index=0)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['already_closed'])
        self.assertEqual(closed['current_url'], OWNER_URL)
        self.assertEqual(len(fake.tabs), 2)

    def test_close_original_ambiguous_does_not_guess(self):
        tabs = [
            {'handle': uuid.uuid4().hex, 'title': '',
             'url': 'https://example.com/'},
            {'handle': uuid.uuid4().hex, 'title': '',
             'url': 'https://example.com/'},
            {'handle': uuid.uuid4().hex, 'title':
             'Two-vision benchmark fixture', 'url': FIXTURE_URL},
        ]
        fake = FakeSession(tabs, current_index=2)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, 'https://example.com/')
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['original_ambiguous'])
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertEqual(len(fake.tabs), 2)

    def test_close_original_missing_still_closes_scratch(self):
        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = FakeSession(tabs, current_index=2)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR,
                               'https://gone.example/nope')
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['original_missing'])
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])

    def test_switch_unknown_url_refuses(self):
        fake = FakeSession(_owner_tabs(), current_index=0)
        with self.assertRaises(ZenDomError):
            self._run_cmd(fake, zen_tab.cmd_switch,
                          'no-such-tab.example')

    def test_open_focus_reverts_during_navigate_refuses_and_keeps_owner_tab(self):
        """Regression for Redteam F1 (TOCTOU): the current tab
        flips back to the owner tab between the (c) check and the
        POST /url navigate. Open must raise BEFORE any DELETE.
        The owner tab survives (its content is changed to the
        fixture page, a navigate-away, not a delete), zero
        deletions, and the new tab is left as an un-navigated
        about:blank. The handler must not delete either: the
        owner tab now carries the fixture URL, so a URL-only
        check would delete it; the handle check is what saves it.
        """
        class _RevertFake(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/url'):
                    self.current = self.tabs[0]['handle']
                return super()._wd(method, path, body)

        fake = _RevertFake(_owner_tabs(), current_index=0,
                           select_new=False, select_works=True)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('changed during navigate', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        # The owner tab survives, but the navigate did rewrite it
        # to the fixture page before the check caught the flip.
        # That is the documented residual damage of F1: a
        # navigate-away, not a delete. The chat survives
        # server-side, and the runner never calls close after a
        # failed open (opened stays False), so no later URL-based
        # close can target the navigated owner tab.
        self.assertEqual(fake.tabs[0]['url'], FIXTURE_URL)
        self.assertEqual(fake.tabs[2]['url'], 'about:blank')
        self.assertEqual(fake._cur_tab()['url'], FIXTURE_URL)

    def test_open_handler_no_delete_when_navigate_fails(self):
        """Council 2 condition 1 (Probe B): the navigate POST
        raises while the current tab is the new about:blank tab.
        The handler must delete nothing: the current tab is not
        the fixture tab.
        """
        class _NavigateFails(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/url'):
                    raise ZenDomError('simulated navigate failure')
                return super()._wd(method, path, body)

        fake = _NavigateFails(_owner_tabs(), current_index=0)
        with self.assertRaises(ZenDomError):
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])
        self.assertEqual(fake._cur_tab()['url'], 'about:blank')

    def test_open_handler_no_delete_when_navigate_lands_wrong_url(self):
        """Council 2 condition 1, URL-gate variant: the navigate
        lands on a non-fixture URL. The URL check raises, and the
        handler must delete nothing: the current tab is not the
        fixture tab.
        """
        class _NavigateWrongUrl(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/url'):
                    tab = self._cur_tab()
                    tab['url'] = 'https://example.com/wrong'
                    tab['title'] = ''
                    return {}
                return super()._wd(method, path, body)

        fake = _NavigateWrongUrl(_owner_tabs(), current_index=0)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('does not contain', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])

    def test_open_count_gate_refuses_stale_handle(self):
        """Council 1 C4: POST /window/new returns an existing
        handle without creating a tab. Since amend 2 the
        membership check (Redteam H1) refuses this case first:
        the returned handle was already in `before`. The count
        gate remains the second line of defense for a genuinely
        new handle that creates no tab (see the next test).
        """
        class _StaleHandleFake(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/window/new'):
                    return {'value': {'handle': self.tabs[0]['handle']}}
                return super()._wd(method, path, body)

        fake = _StaleHandleFake(_owner_tabs(), current_index=0)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('existing handle', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 2)
        self.assertEqual(fake._cur_tab()['url'], OWNER_URL)

    def test_open_count_gate_refuses_new_handle_without_tab(self):
        """Council 1 C4, count gate itself (amend 2): POST
        /window/new returns a genuinely new handle but creates
        no tab. The membership check passes (the handle was not
        in `before`), so the count gate must refuse: no new tab
        exists to navigate.
        """
        class _NewHandleNoTab(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/window/new'):
                    return {'value': {'handle': uuid.uuid4().hex}}
                return super()._wd(method, path, body)

        fake = _NewHandleNoTab(_owner_tabs(), current_index=0)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('did not increase the tab count',
                      str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 2)
        self.assertEqual(fake._cur_tab()['url'], OWNER_URL)

    def test_open_refuses_stale_handle_that_creates_tab(self):
        """Redteam H1 (amend 2), select_new=True: /window/new
        creates a tab but returns the owner tab's handle. The
        count grows by exactly 1, so the count gate passes; the
        membership check must refuse before any navigate or
        DELETE. Without it, the (c) check would select the owner
        tab (it IS the returned handle) and the navigate would
        rewrite it to the fixture URL.
        """
        fake = _StaleHandleWithTab(_owner_tabs(), current_index=0,
                                   select_new=True, select_works=True)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('existing handle', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        self.assertEqual(fake.tabs[0]['url'], OWNER_URL)
        self.assertEqual(fake.tabs[2]['url'], 'about:blank')
        self.assertEqual(fake._cur_tab()['url'], 'about:blank')

    def test_open_refuses_stale_handle_that_creates_tab_no_select(self):
        """Redteam H1 (amend 2), select_new=False (the run 2
        mode): /window/new creates a tab but returns the owner
        tab's handle, and the owner tab is already current, so
        the (c) check would pass with no select at all. The
        membership check must refuse before any navigate.
        """
        fake = _StaleHandleWithTab(_owner_tabs(), current_index=0,
                                   select_new=False, select_works=True)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('existing handle', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        self.assertEqual(fake.tabs[0]['url'], OWNER_URL)
        self.assertEqual(fake._cur_tab()['url'], OWNER_URL)

    def test_open_refuses_concurrent_open_close_with_stale_handle(self):
        """Redteam P-C (amend 3): a tab X opens after `before`
        AND another tab closes in the same window, net count +1,
        and /window/new returns X's handle. The membership check
        passes (X was not in `before`) and the count gate passes
        (net +1), so the set-difference check must refuse: the
        handle set after the open must differ from `before` by
        exactly the new handle added and nothing removed.
        Without it, the (c) check selects X, the navigate
        rewrites X to the fixture URL, and cleanup close DELETEs
        X. Adapted from /tmp/redteam-amend2-probes.py P-C, which
        looked X up by title and missed the hijack; this test
        checks by position (tabs[1] is X after the churn).
        """
        class _ConcurrentOpenClose(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/window/new'):
                    x_handle = uuid.uuid4().hex
                    self.tabs.append({'handle': x_handle, 'title': 'X',
                                      'url': 'https://x.example/'})
                    del self.tabs[1]
                    handle = uuid.uuid4().hex
                    self.tabs.append({'handle': handle, 'title': '',
                                      'url': 'about:blank'})
                    if self.select_new:
                        self.current = handle
                    return {'value': {'handle': x_handle}}
                return super()._wd(method, path, body)

        fake = _ConcurrentOpenClose(_owner_tabs(), current_index=0,
                                    select_new=True, select_works=True)
        with self.assertRaises(ZenDomError) as caught:
            self._run_cmd(fake, zen_tab.cmd_open)
        self.assertIn('handle set', str(caught.exception))
        self.assertEqual(fake.deleted, [])
        self.assertEqual(len(fake.tabs), 3)
        self.assertEqual(fake.tabs[0]['url'], OWNER_URL)
        self.assertEqual(fake.tabs[1]['url'], 'https://x.example/')
        self.assertEqual(fake.tabs[2]['url'], 'about:blank')

    def test_open_refuses_no_creation_stale_return_at_scan(self):
        """Redteam H1 (amend 4), Q-J2: a tab X opens during the
        pre-check scan, and /window/new returns X's handle
        WITHOUT creating a tab. Against `before` the set
        difference is exactly {X} == {new_handle} with nothing
        removed, so the amend-3 check passes; the second
        baseline `just_before` (captured after the scan, so it
        already contains X) must refuse: added against it is
        empty, not {new_handle}. Both select modes, adapted
        from /tmp/redteam-amend3-probes.py Q-J2.
        """
        class _StaleReturnNoCreateAtScan(FakeSession):
            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                self._x_handle = None
                self._injected = False

            def list_tabs(self, handle_index=None):
                if not self._injected:
                    self._injected = True
                    self._x_handle = uuid.uuid4().hex
                    self.tabs.append({'handle': self._x_handle,
                                      'title': 'X',
                                      'url': 'https://x.example/'})
                return super().list_tabs(handle_index)

            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/window/new'):
                    if self.select_new:
                        self.current = self._x_handle
                    return {'value': {'handle': self._x_handle}}
                return super()._wd(method, path, body)

        for mode in (True, False):
            fake = _StaleReturnNoCreateAtScan(
                _owner_tabs(), current_index=0,
                select_new=mode, select_works=True)
            with self.assertRaises(ZenDomError) as caught:
                self._run_cmd(fake, zen_tab.cmd_open)
            self.assertIn('handle set', str(caught.exception))
            self.assertEqual(fake.deleted, [])
            self.assertEqual(len(fake.tabs), 3)
            self.assertEqual(fake.tabs[0]['url'], OWNER_URL)
            self.assertEqual(fake.tabs[1]['url'],
                             'https://example.com/')
            self.assertEqual(fake.tabs[2]['url'], 'https://x.example/')

    def test_open_no_creation_stale_return_during_post_is_residual(self):
        """Redteam G1 (amend 4), Q-J1: a tab X opens DURING the
        POST /window/new round-trip itself, and /window/new
        returns X's handle WITHOUT creating a tab. Both
        baselines miss X (it did not exist when either was
        captured), so every check passes, the navigate rewrites
        X to the fixture URL, and cleanup close DELETEs X. This
        is the irreducible residual of the no-creation variant
        (no atomic verify-and-create, same class as the F1
        race), narrowed by the second baseline, not eliminated.
        This test PINS the residual as a known limitation: it
        asserts the damage happens, so that a future fix which
        closes it must update this test, not pass silently.
        Adapted from /tmp/redteam-amend3-probes.py Q-J1.
        """
        class _StaleReturnNoCreateAtNew(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'POST' and path.endswith('/window/new'):
                    x_handle = uuid.uuid4().hex
                    self.tabs.append({'handle': x_handle, 'title': 'X',
                                      'url': 'https://x.example/'})
                    if self.select_new:
                        self.current = x_handle
                    return {'value': {'handle': x_handle}}
                return super()._wd(method, path, body)

        for mode in (True, False):
            fake = _StaleReturnNoCreateAtNew(
                _owner_tabs(), current_index=0,
                select_new=mode, select_works=True)
            result = self._run_cmd(fake, zen_tab.cmd_open)
            self.assertTrue(result['ok'])
            self.assertIn(FIXTURE_SUBSTR, result['url'])
            closed = self._run_cmd(fake, zen_tab.cmd_close,
                                   FIXTURE_SUBSTR, OWNER_URL)
            self.assertTrue(closed['ok'])
            self.assertEqual(fake.deleted, [FIXTURE_URL])
            self.assertNotIn('https://x.example/',
                             [t['url'] for t in fake.tabs])

    def test_restore_original_scan_error_with_failed_reads_returns_ok(self):
        """Redteam H2 (amend 2): the scan fails inside
        _restore_original AND the _title/_url reads fail too.
        The close already succeeded, so cmd_close must still
        return ok with scan_error True, not raise and mask the
        close. The current title and URL are recorded as None.
        """
        class _ScanFailsLateReadsFail(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._list_calls = 0

            def list_tabs(self, handle_index=None):
                self._list_calls += 1
                if self._list_calls >= 3:
                    raise ZenDomError('simulated scan failure')
                return super().list_tabs(handle_index)

            def _wd(self, method, path, body=None):
                if method == 'GET' and path.endswith('/title'):
                    raise ZenDomError('simulated read failure')
                if method == 'GET' and path.endswith('/url'):
                    raise ZenDomError('simulated read failure')
                return super()._wd(method, path, body)

        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = _ScanFailsLateReadsFail(tabs, current_index=2)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['scan_error'])
        self.assertIsNone(closed['current_title'])
        self.assertIsNone(closed['current_url'])
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])

    def test_open_precheck_passes_when_fixture_tab_unreadable(self):
        """Redteam F3a, pre-check: the existing fixture tab's
        title/URL read failed, so its scan entry carries no URL
        and the pre-check cannot see it. Open proceeds and opens
        a second fixture tab. This pins the behavior as a known
        limitation: an unreadable tab is invisible to URL
        identity, and only the runner's count check would notice
        the extra tab.
        """
        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = FakeSession(tabs, current_index=0,
                           error_entry_urls={FIXTURE_URL})
        result = self._run_cmd(fake, zen_tab.cmd_open)
        self.assertTrue(result['ok'])
        self.assertEqual(len(fake.tabs), 4)
        self.assertEqual(fake.deleted, [])
        self.assertEqual(result['count_after'],
                         result['count_before'] + 1)
        self.assertEqual([t['url'] for t in fake.tabs].count(
            FIXTURE_URL), 2)

    def test_close_reports_already_closed_when_scratch_unreadable(self):
        """Redteam F3a, close: the scratch tab's scan entry
        carries no URL, so cmd_close cannot find it by URL and
        reports already_closed while the tab still exists. This
        pins the behavior as a known limitation: the tab is left
        open, and the runner's count_restored flag is what
        detects the mismatch.
        """
        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = FakeSession(tabs, current_index=0,
                           error_entry_urls={FIXTURE_URL})
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['already_closed'])
        self.assertIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertEqual(len(fake.tabs), 3)

    def test_list_returns_wrong_current_when_scan_restore_fails_silently(self):
        """Redteam F3b: list_tabs switches through tabs and its
        restore does not verify the switch took effect, so a
        silent restore failure leaves the last-scanned tab
        current while the scan still returns normally. cmd_list
        then reports the wrong current tab. This pins the known
        limitation: the runner's phase 1 original_url capture
        would take the wrong tab's URL in that state.
        """
        fake = FakeSession(_owner_tabs(), current_index=0,
                           restore_fails=True)
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertEqual(listed['current'],
                         fake.tabs[-1]['handle'][:8])
        self.assertNotEqual(listed['current'],
                            fake.tabs[0]['handle'][:8])

    def test_list_fallback_resolves_empty_current_entry(self):
        """F1 repro (run 3 attempt 1): the current tab's scan
        entry is an error entry with no URL (its title read
        failed), while a direct read of the current window
        resolves it. cmd_list patches the entry in place from
        the verified direct read and flags current_fallback, so
        the runner's phase 1 can identify the original tab.
        """
        fake = FakeSession(_owner_tabs(), current_index=0,
                           error_entry_urls={OWNER_URL})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertTrue(listed.get('current_fallback'))
        self.assertEqual(listed['count'], 2)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertEqual(entry['url'], OWNER_URL)
        self.assertEqual(entry['title'], 'Chat - Muse')
        self.assertNotIn('error', entry)

    def test_list_fallback_does_not_fire_when_scan_resolves_url(self):
        """No empty entry, no fallback: the scan already
        resolved the current tab's URL, so cmd_list re-reads
        nothing and carries no current_fallback flag. A
        non-current error entry is left untouched.
        """
        tabs = _owner_tabs()
        fake = FakeSession(tabs, current_index=0,
                           error_entry_urls={'https://example.com/'})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertEqual(entry['url'], OWNER_URL)
        other = [t for t in listed['tabs']
                 if t.get('handle') != listed['current']][0]
        self.assertNotIn('url', other)
        self.assertIn('error', other)

    def test_list_fallback_refuses_when_current_handle_changes(self):
        """The fallback verifies the tab by handle plus a
        second read. When the current handle changes between
        the scan's current read and the fallback reads, the
        entry stays unresolved (fail-closed): the runner aborts
        exactly as before the fix, never with a wrong URL.
        """
        class _FlipsAfterScan(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._window_calls = 0

            def _wd(self, method, path, body=None):
                if method == 'GET' and path.endswith('/window'):
                    self._window_calls += 1
                    if self._window_calls > 1:
                        self.current = self.tabs[1]['handle']
                return super()._wd(method, path, body)

        fake = _FlipsAfterScan(_owner_tabs(), current_index=0,
                               error_entry_urls={OWNER_URL})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertNotIn('url', entry)
        self.assertIn('error', entry)

    def test_list_fallback_refuses_when_second_handle_read_differs(self):
        """The second handle read disagrees with the first: the
        tab changed mid-fallback, so the entry stays unresolved
        (fail-closed).
        """
        class _FlipsMidFallback(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._window_calls = 0

            def _wd(self, method, path, body=None):
                if method == 'GET' and path.endswith('/window'):
                    self._window_calls += 1
                    if self._window_calls > 2:
                        self.current = self.tabs[1]['handle']
                return super()._wd(method, path, body)

        fake = _FlipsMidFallback(_owner_tabs(), current_index=0,
                                 error_entry_urls={OWNER_URL})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertNotIn('url', entry)

    def test_list_fallback_refuses_when_url_reads_disagree(self):
        """The two URL reads disagree, so the tab navigated (or
        the read is unstable) mid-fallback. The entry stays
        unresolved (fail-closed).
        """
        class _UrlChangesMidFallback(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._url_calls = 0

            def _wd(self, method, path, body=None):
                if method == 'GET' and path.endswith('/url'):
                    self._url_calls += 1
                    if self._url_calls > 1:
                        return {'value': 'https://example.com/'}
                return super()._wd(method, path, body)

        fake = _UrlChangesMidFallback(_owner_tabs(), current_index=0,
                                      error_entry_urls={OWNER_URL})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertNotIn('url', entry)

    def test_list_fallback_refuses_when_direct_read_raises(self):
        """The direct URL read raises (the transient failure
        persists): the entry stays unresolved (fail-closed).
        """
        class _UrlReadRaises(FakeSession):
            def _wd(self, method, path, body=None):
                if method == 'GET' and path.endswith('/url'):
                    raise ZenDomError('simulated read failure')
                return super()._wd(method, path, body)

        fake = _UrlReadRaises(_owner_tabs(), current_index=0,
                              error_entry_urls={OWNER_URL})
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        entry = [t for t in listed['tabs']
                 if t.get('handle') == listed['current']][0]
        self.assertNotIn('url', entry)

    def test_list_fallback_does_not_synthesize_missing_entry(self):
        """Boundary pin: when the scan has no entry at all for
        the current tab, the fallback does not invent one. The
        list keeps the scan's entries and count, carries no
        current_fallback flag, and the runner aborts exactly as
        before the fix.
        """
        class _DropsCurrentEntry(FakeSession):
            def list_tabs(self, handle_index=None):
                entries = super().list_tabs(handle_index)
                return [e for e in entries
                        if e['handle'] != self.current[:8]]

        fake = _DropsCurrentEntry(_owner_tabs(), current_index=0)
        listed = self._run_cmd(fake, zen_tab.cmd_list)
        self.assertTrue(listed['ok'])
        self.assertNotIn('current_fallback', listed)
        self.assertEqual(listed['count'], 1)
        self.assertEqual([t.get('handle') for t in listed['tabs']],
                         [fake.tabs[1]['handle'][:8]])

    def test_open_succeeds_despite_silent_restore_failure(self):
        """Redteam F3b mitigation: in cmd_open the (c) check
        re-reads the current tab after POST /window/new, so a
        silent scan-restore failure in the pre-check scan cannot
        make the open navigate the wrong tab. Open succeeds and
        the owner tab is untouched.
        """
        fake = FakeSession(_owner_tabs(), current_index=0,
                           restore_fails=True)
        result = self._run_cmd(fake, zen_tab.cmd_open)
        self.assertTrue(result['ok'])
        self.assertEqual(result['selected_by'], 'window/new')
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])
        self.assertEqual(fake._cur_tab()['url'], FIXTURE_URL)

    def test_restore_original_scan_error_flagged_not_ambiguous(self):
        """Council 3 C5, observation 1: when the scan itself
        fails inside _restore_original, the failure is a scan
        error, not an ambiguous original URL. The close already
        succeeded, so cmd_close still returns ok with the
        scan_error flag, and the current tab is left as Zen
        activated it.
        """
        class _ScanFailsLate(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._list_calls = 0

            def list_tabs(self, handle_index=None):
                self._list_calls += 1
                if self._list_calls >= 3:
                    raise ZenDomError('simulated scan failure')
                return super().list_tabs(handle_index)

        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = _ScanFailsLate(tabs, current_index=2)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['scan_error'])
        self.assertFalse(closed.get('original_ambiguous', False))
        self.assertFalse(closed.get('original_missing', False))
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        # F4 follow-up: cmd_close now selects the original tab
        # right after the DELETE (to re-establish a valid browsing
        # context before the verification reads), so when the
        # restore scan fails the current tab is already the
        # original, not whatever the browser auto-activated.
        self.assertEqual(closed['current_url'], OWNER_URL)

    def test_close_only_tab_skips_verification_reads(self):
        # REDTEAM (F4, f1cb4d5): when the scratch tab is the only
        # tab there is no live window left after the DELETE, so
        # the verification reads would raise 'Browsing context
        # has been discarded'. The DELETE itself would have raised
        # had it failed, so the scratch is gone by definition;
        # cmd_close skips the verification reads and reports the
        # count from the DELETE.
        tabs = [{'handle': uuid.uuid4().hex, 'title':
                 'Two-vision benchmark fixture', 'url': FIXTURE_URL}]
        fake = FakeSession(tabs, current_index=0)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertEqual(closed['count_before'], 1)
        self.assertEqual(closed['count_after'], 0)
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertEqual(fake.tabs, [])

    def test_close_fallback_never_targets_the_scratch_tab(self):
        # REDTEAM (F4, f1cb4d5): when the original URL matches the
        # scratch tab itself, the fallback must NOT resolve to
        # the tab being deleted. The orig path needs the same
        # h != scratch_full guard the loop path has; the fallback
        # POST after the DELETE must target another tab.
        class _RecordPostDelete(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.deleted_seen = False
                self.post_delete_handles = []

            def _wd(self, method, path, body=None):
                if method == 'DELETE' and path.endswith('/window'):
                    self.deleted_seen = True
                if (method == 'POST' and path.endswith('/window')
                        and body and self.deleted_seen):
                    self.post_delete_handles.append(
                        body.get('handle'))
                return super()._wd(method, path, body)

        tabs = _owner_tabs()
        tabs.append({'handle': uuid.uuid4().hex, 'title':
                     'Two-vision benchmark fixture',
                     'url': FIXTURE_URL})
        fake = _RecordPostDelete(tabs, current_index=2)
        scratch_handle = tabs[2]['handle']
        owner_handle = tabs[0]['handle']
        # The original URL IS the scratch tab's own URL.
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, FIXTURE_URL)
        self.assertTrue(closed['ok'])
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertNotIn(scratch_handle, fake.post_delete_handles,
                         'the fallback POST must never target the '
                         'tab being deleted')
        self.assertIn(owner_handle, fake.post_delete_handles,
                      'the fallback POST targets another live tab')

    def test_restore_original_full_handle_failure_flagged(self):
        """Council 3 C5, observation 2: when the original tab's
        handle prefix is ambiguous in the full handle list,
        _full_handle raises inside _restore_original. The close
        already succeeded, so cmd_close returns ok with the
        restore_failed flag instead of raising.
        """
        tabs = [
            {'handle': 'aaaaaaaa' + '1' * 24, 'title': 'Chat - Muse',
             'url': OWNER_URL},
            {'handle': 'aaaaaaaa' + '2' * 24, 'title': '',
             'url': 'https://example.com/'},
            {'handle': 'bbbbbbbb' + '3' * 24, 'title':
             'Two-vision benchmark fixture', 'url': FIXTURE_URL},
        ]
        fake = FakeSession(tabs, current_index=2)
        closed = self._run_cmd(fake, zen_tab.cmd_close,
                               FIXTURE_SUBSTR, OWNER_URL)
        self.assertTrue(closed['ok'])
        self.assertTrue(closed['restore_failed'])
        self.assertNotIn(FIXTURE_URL, [t['url'] for t in fake.tabs])
        self.assertIn(OWNER_URL, [t['url'] for t in fake.tabs])


def _load_run2():
    spec = importlib.util.spec_from_file_location(
        'run2_under_test',
        str(Path(__file__).resolve().parents[1] / 'improvements'
            / 'c5-zenproof-runs' / 'c5-zen-delegate-run2.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run2 = _load_run2()


class RunnerFixTest(unittest.TestCase):
    def test_programs_target_by_url_not_title(self):
        self.assertIn("dom_observe('two_vision_fixture.html?clone=zen'",
                      run2.PROBE_PROGRAM)
        self.assertIn("dom_observe('two_vision_fixture.html?clone=zen'",
                      run2.SEND_PROGRAM)
        self.assertEqual(run2.SEND_PROGRAM.count(
            '"scope": "two_vision_fixture.html?clone=zen"'), 4)
        self.assertNotIn('Clone zen thread', run2.PROBE_PROGRAM)
        self.assertNotIn('Clone zen thread', run2.SEND_PROGRAM)

    def test_parse_probe_line_good(self):
        url, count = run2.parse_probe_line(
            'PROBE zen-1 ' + FIXTURE_URL + ' 1', run2.TARGET)
        self.assertEqual(url, FIXTURE_URL)
        self.assertEqual(count, '1')

    def test_parse_probe_line_rejects_old_title_format(self):
        with self.assertRaises(ValueError):
            run2.parse_probe_line('PROBE zen-1 Clone zen thread 1',
                                  run2.TARGET)

    def test_parse_probe_line_rejects_wrong_url(self):
        with self.assertRaises(ValueError):
            run2.parse_probe_line('PROBE zen-1 https://example.com/ 1',
                                  run2.TARGET)

    def test_parse_probe_line_rejects_wrong_count(self):
        with self.assertRaises(ValueError):
            run2.parse_probe_line('PROBE zen-1 ' + FIXTURE_URL + ' 0',
                                  run2.TARGET)

    def test_parse_probe_line_rejects_wrong_shape(self):
        with self.assertRaises(ValueError):
            run2.parse_probe_line('PROBE zen-1', run2.TARGET)

    def test_send_program_prints_snapshot_url(self):
        """Redteam F2: phase 4 gates the send snapshot URL with
        the same check as the probe, so SEND_PROGRAM must print
        the PROBE line (snapshot id, URL, element count) for the
        runner to parse.
        """
        self.assertIn("print('PROBE', snap['snapshot'], snap.get('url'),"
                      " len(snap.get('elements') or []))",
                      run2.SEND_PROGRAM)
        url, count = run2.parse_probe_line(
            'PROBE zen-2 ' + FIXTURE_URL + ' 1', run2.TARGET)
        self.assertEqual(url, FIXTURE_URL)
        self.assertEqual(count, '1')

    def _run_phase4(self, switch_url=FIXTURE_URL, log=None, ok=True,
                    hypr_address='0xABC', calls_out=None):
        """Run phase4 on a real Runner with hypr/tab/oneshot_zen
        mocked (Council 2 phase-4 probe shape: Runner() builds a
        Harness that only mkdirs, no SSH). Returns the runner so
        the test can read results. The hypr, tab, and oneshot_zen
        mocks record their calls on runner._phase4_calls (Redteam
        H3, amend 3, extended amend 4 to hypr): the order must be
        hypr first, then switch, then send, and the program
        passed to oneshot_zen must be SEND_PROGRAM. When phase4
        raises, the runner is lost to the test, so a caller that
        needs the calls on the raise path passes its own list as
        calls_out: the helper appends to it, and the list survives
        the raise (Redteam H3, amend 4).
        """
        runner = run2.Runner()
        runner.zen_address = '0xabc'
        runner.results = {'run': run2.RUN_NO}
        envelope = {'ok': ok, 'elapsed_ms': 1, 'error': None,
                    'log': log if log is not None else [
                        'PROBE zen-9 ' + FIXTURE_URL + ' 1',
                        'dom_act ok True completed 4']}
        calls = calls_out if calls_out is not None else []
        runner._phase4_calls = calls

        def _hypr(*args, **kwargs):
            calls.append(('hypr', args, kwargs))
            return {'address': hypr_address}

        def _tab(*args, **kwargs):
            calls.append(('tab', args, kwargs))
            return {'ok': True, 'url': switch_url}

        def _oneshot(program, intent, timeout=90):
            calls.append(('oneshot', program, intent))
            return (12.3, envelope)

        with mock.patch.object(runner, 'hypr',
                               side_effect=_hypr), \
             mock.patch.object(runner, 'tab', side_effect=_tab), \
             mock.patch.object(runner, 'oneshot_zen',
                               side_effect=_oneshot):
            runner.phase4()
        return runner

    def test_phase4_happy_path_records_send_url_and_count(self):
        """Council 2 C1 (amend 2): the F2 mitigation (re-switch
        plus snapshot URL gate) must be executed by a test, not
        for the first time in a live run. Happy path records
        send_url and send_count from the send PROBE line.
        """
        runner = self._run_phase4()
        self.assertEqual(runner.results['program']['send_url'],
                         FIXTURE_URL)
        self.assertEqual(runner.results['program']['send_count'], '1')
        self.assertEqual(runner.results['program']['completed'], 4)
        self.assertIn(FIXTURE_URL,
                      runner.results['send_switch']['url'])

    def test_phase4_wrong_url_snapshot_raises(self):
        """Council 2 C1: a send snapshot URL that does not
        contain the target raises through parse_probe_line
        (ValueError, not RuntimeError).
        """
        with self.assertRaises(ValueError):
            self._run_phase4(
                log=['PROBE zen-9 https://example.com/ 1',
                     'dom_act ok True completed 4'])

    def test_phase4_wrong_count_snapshot_raises(self):
        """Council 2 C1: a send snapshot count other than 1
        raises through parse_probe_line (ValueError).
        """
        with self.assertRaises(ValueError):
            self._run_phase4(
                log=['PROBE zen-9 ' + FIXTURE_URL + ' 0',
                     'dom_act ok True completed 4'])

    def test_phase4_missing_probe_line_raises(self):
        """Council 2 C1: a send program that prints no PROBE
        line raises RuntimeError before the run can record a
        send URL.
        """
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(log=['dom_act ok True completed 4'])
        self.assertIn('no snapshot line', str(caught.exception))

    def test_phase4_switch_landing_wrong_tab_raises(self):
        """Council 2 C1: the phase-4 re-switch must land on the
        scratch tab; landing on any other URL raises before the
        send program runs.
        """
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(switch_url='https://example.com/')
        self.assertIn('send switch landed on', str(caught.exception))

    def test_phase4_active_window_moved_raises(self):
        """Council 2 C1 (amend 3) + Redteam H3 (amend 4): the
        active-window check must raise when hypr reports an
        address other than the Zen address, before any switch or
        send runs. The message alone is not the whole proof any
        more: the helper records hypr calls and returns them on
        raise via calls_out, so this test asserts the only call
        before the raise was the hypr read itself. A future edit
        moving the check after the switch fails this test.
        """
        calls = []
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(hypr_address='0xDEF', calls_out=calls)
        self.assertIn('active window moved off Zen',
                      str(caught.exception))
        kinds = [c[0] for c in calls]
        self.assertEqual(kinds, ['hypr'])
        hypr_call = [c for c in calls if c[0] == 'hypr'][0]
        self.assertEqual(hypr_call[1], ('activewindow',))

    def test_phase4_envelope_ok_false_raises(self):
        """Council 2 C1 (amend 3): the final ok/completed gate
        must raise when the envelope says ok False, even with a
        valid PROBE line and completed 4. This gate is the last
        line of defense against recording a failed send as
        success.
        """
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(ok=False)
        self.assertIn('did not complete 4/4', str(caught.exception))

    def test_phase4_completed_three_raises(self):
        """Council 2 C1 (amend 3): the final gate must raise
        when the send program completes only 3 of 4 actions.
        """
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(
                log=['PROBE zen-9 ' + FIXTURE_URL + ' 1',
                     'dom_act ok True completed 3'])
        self.assertIn('did not complete 4/4', str(caught.exception))

    def test_phase4_missing_dom_act_raises(self):
        """Council 2 C1 (amend 3): a log with a valid PROBE line
        but no dom_act line leaves completed None, and the final
        gate must raise instead of recording a send with no
        completed count.
        """
        with self.assertRaises(RuntimeError) as caught:
            self._run_phase4(log=['PROBE zen-9 ' + FIXTURE_URL + ' 1'])
        self.assertIn('did not complete 4/4', str(caught.exception))

    def test_phase4_switch_before_send_and_program_identity(self):
        """Redteam H3/C2 (amend 3) + Redteam H3 (amend 4): pin the
        call order and the program identity in the helper. The
        hypr active-window read must run first, then the
        re-switch, then the send, and the program passed to
        oneshot_zen must be SEND_PROGRAM (not PROBE_PROGRAM or
        any other program). A future edit reordering the calls
        or passing the wrong program must fail this test.
        """
        runner = self._run_phase4()
        calls = runner._phase4_calls
        kinds = [c[0] for c in calls]
        self.assertEqual(kinds, ['hypr', 'tab', 'oneshot'])
        hypr_call = [c for c in calls if c[0] == 'hypr'][0]
        self.assertEqual(hypr_call[1], ('activewindow',))
        tab_call = [c for c in calls if c[0] == 'tab'][0]
        self.assertEqual(tab_call[1], ('switch', run2.TARGET))
        oneshot_call = [c for c in calls if c[0] == 'oneshot'][0]
        self.assertIs(oneshot_call[1], run2.SEND_PROGRAM)
        self.assertEqual(oneshot_call[2], run2.INTENT)


if __name__ == '__main__':
    unittest.main()

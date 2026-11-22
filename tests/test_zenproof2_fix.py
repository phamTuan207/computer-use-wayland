#!/usr/bin/env python3
"""Unit tests for the W-ZENPROOF2-FIX changes (no live Zen touch).

Guards the run 2 incident (improvements/w-zenproof2-log.md
section 6): attempt 2 closed Pham Tuan's Muse chat tab because
POST /window/new did not make the scratch tab current, the
navigate rewrote the owner's tab, and the open exception handler
deleted the current window blind. These tests run cmd_open,
cmd_switch, cmd_eval, and cmd_close against a fake Marionette
session that models that exact misfire, and prove:

- open refuses to navigate or delete when the new tab was not
  made current (fix c),
- open deletes only when the current tab is the fixture tab by
  URL (fix c, handler),
- the scratch tab is identified by URL substring, never by
  document.title (fix a),
- switch/eval/close resolve tabs by URL fresh per session, never
  by a stored handle (fix b).

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
    """

    def __init__(self, tabs, current_index=0, select_new=True,
                 select_works=True, h1_for_fixture='Clone zen thread'):
        self.tabs = [dict(t) for t in tabs]
        self.current = self.tabs[current_index]['handle']
        self.select_new = select_new
        self.select_works = select_works
        self.h1_for_fixture = h1_for_fixture
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
            return {'x': 10, 'y': 10, 'width': 320, 'height': 40}
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
        return [{'handle': t['handle'][:8], 'title': t['title'],
                 'url': t['url']} for t in self.tabs]

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


if __name__ == '__main__':
    unittest.main()

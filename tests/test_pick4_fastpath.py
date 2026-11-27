"""Pick 4 grounding fast path: AT-SPI extents plus DOM-first browser.

Pure-helper tests run anywhere; a11y adapter tests use fake GI only, no
desktop access; the cu.py ground branch is tested with mocked broker
pieces. No ydotool, no live desktop.
"""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu
import fastpath

SOURCE = (ROOT / 'scripts/a11y.py').read_text()


class FastpathHelpersTests(unittest.TestCase):
    def test_flag_is_exactly_1(self):
        for value, wanted in (('1', True), ('true', False), ('', False),
                              (None, False)):
            env = {} if value is None else {'CU_PICK4_FASTPATH': value}
            self.assertEqual(fastpath.enabled(env), wanted, value)

    def test_detect_coord_frame(self):
        self.assertEqual(
            fastpath.detect_coord_frame([100, 200, 800, 600],
                                        [100, 200, 800, 600]), 'screen')
        self.assertEqual(
            fastpath.detect_coord_frame([102, 199, 800, 600],
                                        [100, 200, 800, 600]), 'screen')
        self.assertEqual(
            fastpath.detect_coord_frame([0, 0, 800, 600],
                                        [100, 200, 800, 600]), 'window')
        self.assertEqual(
            fastpath.detect_coord_frame([2, 1, 800, 600],
                                        [100, 200, 800, 600]), 'window')
        self.assertEqual(
            fastpath.detect_coord_frame([50, 50, 800, 600],
                                        [100, 200, 800, 600]), 'unknown')

    def test_to_global_box(self):
        self.assertEqual(
            fastpath.to_global_box([10, 20, 30, 40], [100, 200], 'screen'),
            [10, 20, 30, 40])
        self.assertEqual(
            fastpath.to_global_box([10, 20, 30, 40], [100, 200], 'window'),
            [110, 220, 30, 40])
        for bad in ('unknown', None):
            with self.assertRaisesRegex(ValueError, 'screen or window'):
                fastpath.to_global_box([10, 20, 30, 40], [100, 200], bad)
        for bad in ([10, 20, 0, 40], [10, 20, 30], ['10', 20, 30, 40]):
            with self.assertRaises(ValueError):
                fastpath.to_global_box(bad, [100, 200], 'screen')

    def test_box_center(self):
        self.assertEqual(fastpath.box_center([100, 200, 31, 41]), [115, 220])

    def test_crop_for_box_keeps_context_and_clamps(self):
        # Box mid-window: pad on every side, then grown to the 90px min side.
        self.assertEqual(
            fastpath.crop_for_box([200, 300, 60, 30], [100, 200, 800, 600]),
            [76, 70, 108, 90])
        # Box at the window corner: clamped to the window, grown to min side.
        crop = fastpath.crop_for_box([100, 200, 20, 20], [100, 200, 800, 600])
        self.assertEqual(crop[:2], [0, 0])
        self.assertGreaterEqual(crop[2], 90)
        self.assertGreaterEqual(crop[3], 90)
        self.assertLessEqual(crop[2], 800)
        self.assertLessEqual(crop[3], 600)
        # Huge box: capped at max side, centered on the box.
        crop = fastpath.crop_for_box([100, 200, 800, 600], [100, 200, 800, 600])
        self.assertEqual(crop, [200, 100, 400, 400])
        # Box outside its window fails closed, never guessed.
        with self.assertRaisesRegex(ValueError, 'outside its window'):
            fastpath.crop_for_box([50, 200, 60, 30], [100, 200, 800, 600])

    def test_dom_center(self):
        self.assertEqual(
            fastpath.dom_center({'x': 10, 'y': 20, 'width': 31, 'height': 41}),
            [26, 40])
        with self.assertRaises(ValueError):
            fastpath.dom_center({'x': 10, 'y': 20, 'width': 0, 'height': 40})

    def test_matches_query(self):
        self.assertTrue(fastpath.matches_query('Save As', 'menu-item',
                                               name='save'))
        self.assertTrue(fastpath.matches_query('Save As', 'menu-item',
                                               role='menu'))
        self.assertFalse(fastpath.matches_query('Save As', 'menu-item',
                                                name='open'))
        self.assertFalse(fastpath.matches_query('Save As', 'menu-item',
                                                role='button'))
        self.assertTrue(fastpath.matches_query('Save As', 'menu-item'))


def _load_a11y_with_fake_gi(test):
    import sys as _sys
    import types
    saved = {name: _sys.modules.get(name) for name in ('gi', 'gi.repository')}
    gi = types.ModuleType('gi')
    gi.require_version = lambda *a: None
    repository = types.ModuleType('gi.repository')
    atspi = types.SimpleNamespace()
    atspi.set_timeout = lambda *a: None
    atspi.StateType = types.SimpleNamespace(
        SENSITIVE='sensitive', EDITABLE='editable', PRESSED='pressed',
        CHECKED='checked', SELECTED='selected', EXPANDED='expanded')
    atspi.CoordType = types.SimpleNamespace(SCREEN=0, WINDOW=1)
    repository.Atspi = atspi
    gi.repository = repository
    _sys.modules['gi'] = gi
    _sys.modules['gi.repository'] = repository
    test.addCleanup(test._restore_gi, saved)
    spec = importlib.util.spec_from_file_location('a11y_pick4',
                                                  ROOT / 'scripts/a11y.py')
    module = importlib.util.module_from_spec(spec)
    with mock.patch.object(_sys, 'stdin', io.StringIO('')), \
            contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        try:
            spec.loader.exec_module(module)
        except SystemExit:
            pass
    return module


class A11yDescribeExtentsTests(unittest.TestCase):
    def _restore_gi(self, saved):
        import sys as _sys
        for name, module in saved.items():
            if module is None:
                _sys.modules.pop(name, None)
            else:
                _sys.modules[name] = module

    def setUp(self):
        self.a11y = _load_a11y_with_fake_gi(self)

    def element(self, extents=(50, 60, 120, 30)):
        element = mock.Mock()
        element.get_name.return_value = 'Save'
        element.get_role_name.return_value = 'push button'
        states = mock.Mock()
        states.contains.side_effect = lambda state: state == 'sensitive'
        element.get_state_set.return_value = states
        iface = mock.Mock()
        iface.get_extents.return_value = extents
        element.get_component_iface.return_value = iface
        return element

    def test_extents_present_only_with_flag(self):
        with mock.patch.dict('os.environ', {'CU_PICK4_FASTPATH': '1'}):
            result = self.a11y.describe(self.element(), [], 'e1')
        self.assertEqual(result['extents'], [50, 60, 120, 30])
        self.assertEqual(result['extents_coord'], 'screen')
        with mock.patch.dict('os.environ', {}, clear=True):
            result = self.a11y.describe(self.element(), [], 'e1')
        self.assertNotIn('extents', result)
        self.assertNotIn('extents_coord', result)

    def test_missing_component_iface_omits_extents(self):
        element = self.element()
        element.get_component_iface.return_value = None
        with mock.patch.dict('os.environ', {'CU_PICK4_FASTPATH': '1'}):
            result = self.a11y.describe(element, [], 'e1')
        self.assertNotIn('extents', result)

    def test_object_form_extents_and_bad_values(self):
        import types
        element = self.element()
        element.get_component_iface.return_value.get_extents.return_value = \
            types.SimpleNamespace(x=7, y=8, width=9, height=10)
        with mock.patch.dict('os.environ', {'CU_PICK4_FASTPATH': '1'}):
            result = self.a11y.describe(element, [], 'e1')
        self.assertEqual(result['extents'], [7, 8, 9, 10])
        for bad in ((50, 60, 0, 30), (50, 60, 120, -1), 'nonsense',
                    (50.5, 60, 120, 30)):
            element.get_component_iface.return_value.get_extents.return_value = bad
            with mock.patch.dict('os.environ', {'CU_PICK4_FASTPATH': '1'}):
                result = self.a11y.describe(element, [], 'e1')
            self.assertNotIn('extents', result, bad)


class A11yQueryGroundTests(unittest.TestCase):
    def _extract(self, *names):
        nodes = [n for n in ast.parse(SOURCE).body
                 if isinstance(n, ast.FunctionDef) and n.name in names]
        ns = {'time': time, 'os': __import__('os')}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'a11y.py',
                    'exec'), ns)
        return ns

    def test_query_filters_and_caps(self):
        ns = self._extract('query', '_pick4', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: True
        snapshot = {'backend': 'a11y', 'app_name': 'App',
                    'created': time.time(), 'snapshot': '/tmp/s.json',
                    'elements': [
                        {'ref': 'e1', 'name': 'Save', 'role': 'push button'},
                        {'ref': 'e2', 'name': 'Save As', 'role': 'menu item'},
                        {'ref': 'e3', 'name': 'Open', 'role': 'push button'},
                    ], 'truncated': False}
        ns['observe'] = mock.Mock(return_value=snapshot)
        result = ns['query'](4242, name='save')
        self.assertEqual([e['ref'] for e in result['elements']], ['e1', 'e2'])
        self.assertEqual(result['matched'], 2)
        self.assertEqual(result['snapshot'], '/tmp/s.json')
        result = ns['query'](4242, role='push button', limit=1)
        self.assertEqual(len(result['elements']), 1)
        self.assertTrue(result['truncated'])
        with self.assertRaisesRegex(ValueError, 'name or role'):
            ns['query'](4242)
        with self.assertRaisesRegex(ValueError, 'limit must be 1..20'):
            ns['query'](4242, name='save', limit=21)

    def test_query_refuses_with_flag_off(self):
        ns = self._extract('query', '_pick4', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: False
        ns['observe'] = mock.Mock()
        with self.assertRaisesRegex(ValueError, 'pick4 fast path is off'):
            ns['query'](4242, name='save')
        ns['observe'].assert_not_called()

    def test_ground_returns_fresh_box_and_root(self):
        ns = self._extract('ground', '_pick4', '_component_extents', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: True
        snapshot = {'backend': 'a11y', 'created': time.time(), 'pid': 4242,
                    'elements': [{'ref': 'e1', 'path': [], 'name': 'Save',
                                  'role': 'push button'}]}
        ns['read_json_file'] = mock.Mock(return_value=snapshot)
        root = mock.Mock()
        element = mock.Mock()
        ns['app'] = mock.Mock(return_value=root)
        ns['resolve'] = mock.Mock(return_value=element)
        ns['wait_actionable'] = mock.Mock(return_value=element)
        boxes = {id(element): [300, 400, 120, 30], id(root): [100, 200, 800, 600]}
        ns['_component_extents'] = lambda e: boxes[id(e)]
        result = ns['ground']('/tmp/s.json', 'e1')
        self.assertTrue(result['ok'])
        self.assertEqual(result['extents'], [300, 400, 120, 30])
        self.assertEqual(result['root_extents'], [100, 200, 800, 600])
        self.assertEqual(result['name'], 'Save')
        ns['wait_actionable'].assert_called_once()

    def test_ground_uses_first_top_level_frame_extents(self):
        import types
        ns = self._extract('ground', '_pick4', '_component_extents', '_ints4', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: True
        ns['Atspi'] = types.SimpleNamespace(
            CoordType=types.SimpleNamespace(SCREEN=0))
        snapshot = {'backend': 'a11y', 'created': time.time(), 'pid': 4242,
                    'elements': [{'ref': 'e1', 'path': [0], 'name': 'Sidebar',
                                  'role': 'list'}]}
        root = mock.Mock()
        no_extents = mock.Mock()
        no_extents.get_component_iface.return_value = None
        frame = mock.Mock()
        frame_component = mock.Mock()
        frame_component.get_extents.return_value = [0, 0, 924, 581]
        frame.get_component_iface.return_value = frame_component
        later_frame = mock.Mock()
        later_component = mock.Mock()
        later_component.get_extents.return_value = [0, 0, 800, 600]
        later_frame.get_component_iface.return_value = later_component
        root.get_component_iface.return_value = None
        root.get_child_count.return_value = 3
        root.get_child_at_index.side_effect = [no_extents, frame, later_frame]
        element = mock.Mock()
        element_component = mock.Mock()
        element_component.get_extents.return_value = [0, 0, 184, 535]
        element.get_component_iface.return_value = element_component
        ns['read_json_file'] = mock.Mock(return_value=snapshot)
        ns['app'] = mock.Mock(return_value=root)
        ns['resolve'] = mock.Mock(return_value=element)
        ns['wait_actionable'] = mock.Mock(return_value=element)

        result = ns['ground']('/tmp/s.json', 'e1')

        self.assertEqual(result['extents'], [0, 0, 184, 535])
        self.assertEqual(result['root_extents'], [0, 0, 924, 581])
        root.get_child_at_index.assert_has_calls([mock.call(0), mock.call(1)])
        self.assertEqual(root.get_child_at_index.call_count, 2)

    def test_ground_fails_closed_without_app_or_frame_extents(self):
        import types
        ns = self._extract('ground', '_pick4', '_component_extents', '_ints4', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: True
        ns['Atspi'] = types.SimpleNamespace(
            CoordType=types.SimpleNamespace(SCREEN=0))
        snapshot = {'backend': 'a11y', 'created': time.time(), 'pid': 4242,
                    'elements': [{'ref': 'e1', 'path': [], 'name': 'Sidebar',
                                  'role': 'list'}]}
        root = mock.Mock()
        root.get_component_iface.return_value = None
        root.get_child_count.return_value = 2
        children = [mock.Mock(), mock.Mock()]
        for child in children:
            child.get_component_iface.return_value = None
        root.get_child_at_index.side_effect = children
        element = mock.Mock()
        element_component = mock.Mock()
        element_component.get_extents.return_value = [0, 0, 184, 535]
        element.get_component_iface.return_value = element_component
        ns['read_json_file'] = mock.Mock(return_value=snapshot)
        ns['app'] = mock.Mock(return_value=root)
        ns['resolve'] = mock.Mock(return_value=element)
        ns['wait_actionable'] = mock.Mock(return_value=element)

        with self.assertRaisesRegex(ValueError, 'no window frame extents; use vision'):
            ns['ground']('/tmp/s.json', 'e1')

    def test_ground_refuses_with_flag_off(self):
        ns = self._extract('ground', '_pick4', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: False
        ns['read_json_file'] = mock.Mock()
        with self.assertRaisesRegex(ValueError, 'pick4 fast path is off'):
            ns['ground']('/tmp/s.json', 'e1')
        ns['read_json_file'].assert_not_called()

    def test_ground_fails_closed(self):
        ns = self._extract('ground', '_pick4', '_component_extents', '_completeness', 'parse_ref')
        ns['_pick4'] = lambda: True
        ns['app'] = mock.Mock()
        ns['resolve'] = mock.Mock()
        ns['wait_actionable'] = mock.Mock()
        stale = {'backend': 'a11y', 'created': time.time() - 91, 'pid': 1,
                 'elements': []}
        ns['read_json_file'] = mock.Mock(return_value=stale)
        with self.assertRaisesRegex(ValueError, 'stale'):
            ns['ground']('/tmp/s.json', 'e1')
        fresh = {'backend': 'a11y', 'created': time.time(), 'pid': 1,
                 'elements': [{'ref': 'e1', 'path': [], 'name': 'Save',
                               'role': 'push button'}]}
        ns['read_json_file'] = mock.Mock(return_value=fresh)
        ns['_component_extents'] = mock.Mock(return_value=None)
        with self.assertRaisesRegex(ValueError, 'no extents; use vision'):
            ns['ground']('/tmp/s.json', 'e1')
        with self.assertRaisesRegex(ValueError, 'valid accessibility ref'):
            ns['ground']('/tmp/s.json', 'e9')


class CuGroundCliTests(unittest.TestCase):
    def run_ground(self, adapter_result, clients):
        argv = ['cu', 'a11y', 'ground', 'e1', '--snapshot', '/tmp/s.json',
                '--address', '0xabc']
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(
                cu, 'environment', return_value={}))
            stack.enter_context(mock.patch.object(cu, 'require_session'))
            stack.enter_context(mock.patch.object(cu, 'check_cancel'))
            stack.enter_context(mock.patch.object(
                cu, 'locked', return_value=contextlib.nullcontext()))
            stack.enter_context(mock.patch.object(
                cu, 'run_cancelable',
                return_value=json.dumps(adapter_result)))
            stack.enter_context(mock.patch.object(
                cu, 'hypr', return_value=clients))
            stack.enter_context(mock.patch.dict(
                'os.environ', {'CU_PICK4_FASTPATH': '1'}))
            stack.enter_context(mock.patch.object(sys, 'argv', argv))
            with contextlib.redirect_stdout(io.StringIO()) as output:
                code = cu.main()
        return code, json.loads(output.getvalue())

    def test_ground_returns_global_box_and_crop(self):
        adapter = {'ok': True, 'ref': 'e1', 'role': 'push button',
                   'name': 'Save', 'extents': [300, 400, 120, 30],
                   'extents_coord': 'screen',
                   'root_extents': [100, 200, 800, 600]}
        clients = [{'address': '0xabc', 'at': [100, 200],
                    'size': [800, 600]}]
        code, result = self.run_ground(adapter, clients)
        self.assertEqual(code, 0)
        self.assertTrue(result['ok'])
        self.assertEqual(result['backend'], 'pick4-ground')
        self.assertEqual(result['coord_frame'], 'screen')
        self.assertEqual(result['box'], [300, 400, 120, 30])
        self.assertEqual(result['center'], [360, 415])
        self.assertIn('verify', result)
        self.assertTrue(result['verify'].startswith('observe --window 0xabc --crop'))

    def test_ground_window_relative_extents_get_origin(self):
        adapter = {'ok': True, 'ref': 'e1', 'role': 'push button',
                   'name': 'Save', 'extents': [200, 200, 120, 30],
                   'extents_coord': 'screen',
                   'root_extents': [0, 0, 800, 600]}
        clients = [{'address': '0xabc', 'at': [100, 200],
                    'size': [800, 600]}]
        code, result = self.run_ground(adapter, clients)
        self.assertEqual(code, 0)
        self.assertEqual(result['coord_frame'], 'window')
        self.assertEqual(result['box'], [300, 400, 120, 30])
        self.assertEqual(result['center'], [360, 415])

    def test_ground_nautilus_frame_child_box_and_crop(self):
        adapter = {'ok': True, 'ref': 'e1', 'role': 'list',
                   'name': 'Sidebar', 'extents': [0, 0, 184, 535],
                   'extents_coord': 'screen',
                   'root_extents': [0, 0, 924, 581]}
        clients = [{'address': '0xabc', 'at': [3448, 1509],
                    'size': [924, 581]}]

        code, result = self.run_ground(adapter, clients)

        self.assertEqual(code, 0)
        self.assertEqual(result['coord_frame'], 'window')
        self.assertEqual(result['box'], [3448, 1509, 184, 535])
        self.assertEqual(result['center'], [3540, 1776])
        crop = result['crop']
        self.assertGreaterEqual(crop[0], 0)
        self.assertGreaterEqual(crop[1], 0)
        self.assertLessEqual(crop[0] + crop[2], 924)
        self.assertLessEqual(crop[1] + crop[3], 581)
        self.assertEqual(crop, [0, 67, 208, 400])

    def test_ground_unknown_frame_fails_closed(self):
        adapter = {'ok': True, 'ref': 'e1', 'role': 'push button',
                   'name': 'Save', 'extents': [200, 200, 120, 30],
                   'extents_coord': 'screen',
                   'root_extents': [50, 50, 800, 600]}
        clients = [{'address': '0xabc', 'at': [100, 200],
                    'size': [800, 600]}]
        with self.assertRaisesRegex(ValueError, 'screen or window'):
            self.run_ground(adapter, clients)

    def test_ground_flag_off_refuses(self):
        argv = ['cu', 'a11y', 'ground', 'e1', '--snapshot', '/tmp/s.json',
                '--address', '0xabc']
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(
                cu, 'environment', return_value={}))
            stack.enter_context(mock.patch.object(cu, 'require_session'))
            stack.enter_context(mock.patch.object(cu, 'check_cancel'))
            stack.enter_context(mock.patch.object(
                cu, 'locked', return_value=contextlib.nullcontext()))
            stack.enter_context(mock.patch.dict('os.environ', {},
                                               clear=True))
            stack.enter_context(mock.patch.object(sys, 'argv', argv))
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'pick4 fast path is off'):
                    cu.main()

    def test_query_cli_passes_filter_to_adapter(self):
        argv = ['cu', 'a11y', 'query', '--pid', '4242', '--name', 'save',
                '--limit', '5']
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(
                cu, 'environment', return_value={}))
            stack.enter_context(mock.patch.object(cu, 'require_session'))
            stack.enter_context(mock.patch.object(cu, 'check_cancel'))
            stack.enter_context(mock.patch.object(
                cu, 'locked', return_value=contextlib.nullcontext()))
            adapter = stack.enter_context(mock.patch.object(
                cu, 'run_cancelable',
                return_value='{"backend":"a11y-query","elements":[]}'))
            stack.enter_context(mock.patch.object(sys, 'argv', argv))
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(cu.main(), 0)
        request = json.loads(adapter.call_args.kwargs['input'])
        self.assertEqual(request['operation'], 'query')
        self.assertEqual(request['name'], 'save')
        self.assertEqual(request['limit'], 5)
        self.assertEqual(json.loads(output.getvalue())['backend'], 'a11y-query')


if __name__ == '__main__':
    unittest.main()

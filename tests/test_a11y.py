"""Run production a11y actions with fake interfaces; no GI or desktop access."""
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
SOURCE = (ROOT / 'scripts/a11y.py').read_text()


class A11yAdapterTests(unittest.TestCase):
    def setUp(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'act')
        self.element = mock.Mock()
        self.element.get_action_iface.return_value = self.element
        self.element.get_n_actions.return_value = 1
        self.element.get_action_name.return_value = 'click'
        self.element.do_action.return_value = True
        self.snapshot = {'backend': 'a11y', 'created': time.time(), 'pid': 1,
                         'elements': [{'ref': 'e1', 'editable': True, 'actions': ['click']}]}
        self.ns = dict(time=time, read_json_file=mock.Mock(return_value=self.snapshot),
                       validate_actions=cu.validate_actions, app=mock.Mock(),
                       resolve=mock.Mock(return_value=self.element),
                       observe=mock.Mock(side_effect=RuntimeError('observe failed')))
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'), self.ns)

    def test_final_observation_failure_preserves_acknowledged_count(self):
        result = self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['completed'], 1)
        self.assertIn('execution_ms', result)
        self.assertEqual(result['capture_error'], 'observe failed')
        self.element.do_action.assert_called_once_with(0)

    def test_action_error_survives_observation_failure(self):
        self.element.do_action.side_effect = [True, False]
        result = self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}] * 2)
        self.assertEqual(result['completed'], 1)
        self.assertEqual(result['error'], 'native action refused')
        self.assertEqual(result['capture_error'], 'observe failed')
        self.assertIn('execution_ms', result)

    def test_baseexception_propagates_from_action_and_observation(self):
        for error in (KeyboardInterrupt('interrupt'), SystemExit(9)):
            for stage in ('action', 'observe'):
                with self.subTest(error=type(error).__name__, stage=stage):
                    self.element.do_action.side_effect = error if stage == 'action' else None
                    self.ns['observe'].side_effect = error if stage == 'observe' else RuntimeError('after')
                    with self.assertRaises(type(error)):
                        self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])

    def test_bad_later_action_sends_no_input(self):
        for bad in ({'type': []}, {'type': 'set_text', 'ref': 'e1', 'text': 5},
                    {'type': 'set_text', 'ref': 'e1', 'text': 'x' * 10001}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}, bad])
                self.element.do_action.assert_not_called()

    def test_unknown_operation_cannot_reach_act(self):
        tail = ast.parse(SOURCE).body[-1]
        called = mock.Mock()
        ns = dict(sys=mock.Mock(stdin=io.StringIO('{"operation":"typo"}')),
                  read_json=cu.read_json, json=json, act=called)
        ns['sys'].stdin = io.StringIO('{"operation":"typo"}')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exec(compile(ast.Module(body=[tail], type_ignores=[]), 'a11y.py', 'exec'), ns)
        self.assertFalse(json.loads(output.getvalue())['ok'])
        ns['sys'].exit.assert_called_once_with(1)
        called.assert_not_called()


class A11yCliTests(unittest.TestCase):
    def test_valid_set_text_reaches_adapter_once(self):
        for text in ('', 'hello', 'Tiếng Việt', '🙂'):
            with self.subTest(text=text), contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(cu, 'environment', return_value={}))
                stack.enter_context(mock.patch.object(cu, 'require_session'))
                stack.enter_context(mock.patch.object(cu, 'check_cancel'))
                stack.enter_context(mock.patch.object(cu, 'locked', return_value=contextlib.nullcontext()))
                adapter = stack.enter_context(mock.patch.object(cu, 'run_cancelable', return_value='{"ok":true,"completed":1}'))
                pointer = stack.enter_context(mock.patch.object(cu, 'Pointer', side_effect=AssertionError('pointer')))
                stack.enter_context(mock.patch.object(sys, 'argv', ['cu', 'a11y', 'act', '--snapshot', 'snapshot', '--actions', '-']))
                stack.enter_context(mock.patch.object(sys, 'stdin', io.StringIO(json.dumps([{'type': 'set_text', 'ref': 'e1', 'text': text}]))))
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(cu.main(), 0)
                self.assertEqual(json.loads(output.getvalue())['completed'], 1)
                self.assertEqual(adapter.call_count, 1)
                self.assertEqual(json.loads(adapter.call_args.kwargs['input'])['actions'][0]['text'], text)
                pointer.assert_not_called()



class ResolverTests(unittest.TestCase):
    """N2: production resolve treats None names like describe does."""

    def setUp(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'resolve')
        atspi = mock.Mock()
        atspi.StateType.SENSITIVE = 'sensitive'
        self.resolve = {'Atspi': atspi}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'),
             self.resolve)
        self.resolve = self.resolve['resolve']
        self.sensitive = 'sensitive'

    def node(self, name='', role='button', sensitive=True, children=None):
        element = mock.Mock()
        element.get_name.return_value = name
        element.get_role_name.return_value = role
        states = mock.Mock()
        states.contains.side_effect = lambda state: sensitive and state == self.sensitive
        element.get_state_set.return_value = states
        element.get_child_at_index.side_effect = lambda i: (children or [])[i]
        return element

    def item(self, **overrides):
        base = {'ref': 'e1', 'path': [], 'name': '', 'role': 'button'}
        base.update(overrides)
        return base

    def test_none_name_matches_empty_snapshot_name(self):
        root = self.node(name=None)
        self.assertIs(self.resolve(root, self.item()), root)

    def test_none_name_against_old_name_is_stale_not_type_error(self):
        root = self.node(name=None)
        with self.assertRaisesRegex(ValueError, 'accessibility tree changed'):
            self.resolve(root, self.item(name='old'))

    def test_changed_name_after_empty_snapshot_is_stale(self):
        root = self.node(name='changed')
        with self.assertRaisesRegex(ValueError, 'accessibility tree changed'):
            self.resolve(root, self.item(name=''))

    def test_role_change_and_disabled_still_refused(self):
        with self.assertRaisesRegex(ValueError, 'accessibility tree changed'):
            self.resolve(self.node(name=None, role='label'), self.item())
        with self.assertRaisesRegex(ValueError, 'element is disabled'):
            self.resolve(self.node(name=None, sensitive=False), self.item())

    def test_production_act_with_production_resolve_nameless(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'act')
        ns = dict(time=time, read_json_file=mock.Mock(return_value={
            'backend': 'a11y', 'created': time.time(), 'pid': 1,
            'elements': [{'ref': 'e1', 'path': [], 'name': '',
                          'role': 'button', 'actions': ['click']}]}),
            validate_actions=cu.validate_actions,
            app=mock.Mock(return_value=self.node(name=None)),
            resolve=self.resolve,
            observe=mock.Mock(return_value={'ok': True}))
        element = ns['app'].return_value
        element.get_action_iface.return_value = element
        element.get_n_actions.return_value = 1
        element.get_action_name.return_value = 'click'
        element.do_action.return_value = True
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'), ns)
        result = ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'], 1)
        element.do_action.assert_called_once_with(0)

    def test_name_changed_between_guards_sends_no_input(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'act')
        root = self.node(name='')
        root.get_name.side_effect = ['', 'changed']
        ns = dict(time=time, read_json_file=mock.Mock(return_value={
            'backend': 'a11y', 'created': time.time(), 'pid': 1,
            'elements': [{'ref': 'e1', 'path': [], 'name': '',
                          'role': 'button', 'actions': ['click']}]}),
            validate_actions=cu.validate_actions,
            app=mock.Mock(return_value=root),
            resolve=self.resolve,
            observe=mock.Mock(return_value={'ok': True}))
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'), ns)
        result = ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['completed'], 0)
        root.get_action_iface.assert_not_called()

    def test_stale_name_at_preflight_raises_before_input(self):
        node = next(n for n in ast.parse(SOURCE).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'act')
        ns = dict(time=time, read_json_file=mock.Mock(return_value={
            'backend': 'a11y', 'created': time.time(), 'pid': 1,
            'elements': [{'ref': 'e1', 'path': [], 'name': '',
                          'role': 'button', 'actions': ['click']}]}),
            validate_actions=cu.validate_actions,
            app=mock.Mock(return_value=self.node(name='changed')),
            resolve=self.resolve,
            observe=mock.Mock())
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'a11y.py', 'exec'), ns)
        with self.assertRaisesRegex(ValueError, 'accessibility tree changed'):
            ns['act']('snapshot', [{'type': 'click', 'ref': 'e1'}])
        ns['observe'].assert_not_called()



class A11yObserveFileTests(unittest.TestCase):
    """N7: production observe creates its JSON 0600-before-write. Fake GI only."""

    def setUp(self):
        import sys as _sys
        import types
        self.saved = {name: _sys.modules.get(name) for name in ('gi', 'gi.repository')}
        gi = types.ModuleType('gi')
        gi.require_version = lambda *a: None
        repository = types.ModuleType('gi.repository')
        atspi = types.SimpleNamespace()
        atspi.set_timeout = lambda *a: None
        atspi.StateType = types.SimpleNamespace(SENSITIVE='sensitive', EDITABLE='editable')
        repository.Atspi = atspi
        gi.repository = repository
        _sys.modules['gi'] = gi
        _sys.modules['gi.repository'] = repository
        self.addCleanup(self.restore)
        spec = importlib.util.spec_from_file_location(
            'a11y_observe', ROOT / 'scripts/a11y.py')
        self.a11y = importlib.util.module_from_spec(spec)
        # The module tail is a CLI entry point that reads stdin; it is not part
        # of observe(). All defs precede it, so a SystemExit here is expected.
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            try:
                spec.loader.exec_module(self.a11y)
            except SystemExit:
                pass

    def restore(self):
        import sys as _sys
        for name, module in self.saved.items():
            if module is None:
                _sys.modules.pop(name, None)
            else:
                _sys.modules[name] = module

    def root(self, pid=4242, name='App', children=0):
        import sys as _sys
        sensitive = _sys.modules['gi.repository'].Atspi.StateType.SENSITIVE
        root = mock.Mock()
        root.get_process_id.return_value = pid
        root.get_name.return_value = name
        root.get_role_name.return_value = 'application'
        root.get_child_count.return_value = children
        root.get_child_at_index.side_effect = AssertionError('no children expected')
        states = mock.Mock()
        states.contains.side_effect = lambda state: state == sensitive
        root.get_state_set.return_value = states
        return root

    def test_observation_json_is_private_and_matches_schema(self):
        import stat
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            self.a11y.STATE = Path(folder)
            self.a11y.prepare_state = lambda: Path(folder).mkdir(exist_ok=True)
            root = self.root()
            self.a11y.applications = lambda: [root]
            result = self.a11y.observe(4242)
            path = Path(result['snapshot'])
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            stored = json.loads(path.read_text())
            self.assertEqual(stored['backend'], 'a11y')
            self.assertEqual(stored['pid'], 4242)
            self.assertEqual(stored['app_name'], 'App')
            self.assertIn('snapshot', stored)
            self.assertNotIn('path', result['elements'][0] if result['elements'] else {})

    def test_collision_and_symlink_refuse_without_touching_target(self):
        import tempfile
        import uuid
        fixed = uuid.UUID(hex='ab' * 16)
        with tempfile.TemporaryDirectory() as folder:
            self.a11y.STATE = Path(folder)
            self.a11y.prepare_state = lambda: None
            root = self.root()
            self.a11y.applications = lambda: [root]
            target = Path(folder) / 'target.json'
            target.write_text('{"kept":true}')
            with mock.patch.object(self.a11y.uuid, 'uuid4', return_value=fixed):
                link = Path(folder) / (fixed.hex[:12] + '.json')
                link.symlink_to(target)
                with self.assertRaises(OSError):
                    self.a11y.observe(4242)
                self.assertEqual(target.read_text(), '{"kept":true}')
                link.unlink()
                link.write_text('{"existing":true}')
                with self.assertRaises(OSError):
                    self.a11y.observe(4242)
                self.assertEqual(link.read_text(), '{"existing":true}')

    def test_fd_closed_exactly_once_on_fchmod_or_fdopen_failure(self):
        import os
        import tempfile
        for point in ('fchmod', 'fdopen'):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as folder:
                self.a11y.STATE = Path(folder)
                self.a11y.prepare_state = lambda: None
                self.a11y.applications = lambda: [self.root()]
                opened, closed = [], []
                real_open, real_close = os.open, os.close

                def spy_open(*args, **kwargs):
                    fd = real_open(*args, **kwargs)
                    opened.append(fd)
                    return fd

                def spy_close(fd):
                    closed.append(fd)
                    return real_close(fd)

                with mock.patch.object(self.a11y.os, 'open', side_effect=spy_open), \
                     mock.patch.object(self.a11y.os, 'close', side_effect=spy_close), \
                     mock.patch.object(self.a11y.os, point,
                                       side_effect=OSError(point + ' down')):
                    with self.assertRaises(OSError):
                        self.a11y.observe(4242)
                self.assertEqual(len(opened), 1, 'one raw descriptor opened')
                self.assertEqual(closed, opened,
                                 'raw descriptor closed exactly once, no foreign fd touched')

    def test_write_failure_closes_stream_once_with_no_extra_close(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            self.a11y.STATE = Path(folder)
            self.a11y.prepare_state = lambda: None
            self.a11y.applications = lambda: [self.root()]
            opened, closed = [], []
            real_open, real_close = os.open, os.close

            def spy_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def spy_close(fd):
                closed.append(fd)
                return real_close(fd)

            with mock.patch.object(self.a11y.os, 'open', side_effect=spy_open), \
                 mock.patch.object(self.a11y.os, 'close', side_effect=spy_close), \
                 mock.patch.object(self.a11y.json, 'dumps', side_effect=OSError('dumps down')):
                with self.assertRaisesRegex(OSError, 'dumps down'):
                    self.a11y.observe(4242)
            self.assertEqual(len(opened), 1)
            self.assertEqual(closed, [],
                             'no extra os.close after ownership transferred to the stream')
            with self.assertRaises(OSError):
                os.fstat(opened[0])

    def test_flush_failure_closes_once_with_error_identity(self):
        import io
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            self.a11y.STATE = Path(folder)
            self.a11y.prepare_state = lambda: None
            self.a11y.applications = lambda: [self.root()]
            opened, closed = [], []
            real_open, real_close = os.open, os.close
            real_fdopen = os.fdopen

            def spy_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def spy_close(fd):
                closed.append(fd)
                return real_close(fd)

            def rigged_fdopen(fd, mode='r', *args, **kwargs):
                stream = real_fdopen(fd, mode, *args, **kwargs)
                buffer = stream.detach()

                class FlushFailer(io.TextIOWrapper):
                    def flush(self):
                        raise OSError('a11y flush down')

                return FlushFailer(buffer, encoding='utf-8')

            with mock.patch.object(self.a11y.os, 'open', side_effect=spy_open), \
                 mock.patch.object(self.a11y.os, 'close', side_effect=spy_close), \
                 mock.patch.object(self.a11y.os, 'fdopen', side_effect=rigged_fdopen):
                with self.assertRaisesRegex(OSError, 'a11y flush down'):
                    self.a11y.observe(4242)
            self.assertEqual(len(opened), 1)
            self.assertEqual(closed, [],
                             'no extra os.close after ownership transferred to the stream')
            with self.assertRaises(OSError):
                os.fstat(opened[0])


if __name__ == '__main__':
    unittest.main()

"""Keyboard preflight regressions with a fake compositor; never send desktop input."""
import importlib.util
from pathlib import Path
import sys
import time
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('cu',ROOT/'scripts/cu.py')
cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)
import indicator


class StandaloneBudget(unittest.TestCase):
    def test_standalone_argv_and_group_budget(self):
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-x','delay_ms':0}),
                         ['wtype','-','-p','VoidSymbol'])
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-x','delay_ms':5}),
                         ['wtype','-d','5','-','-p','VoidSymbol'])
        # Same accounting as keyboard_argv: len(text)*delay_ms + one 12 ms settle.
        self.assertEqual(cu.standalone_type_argv({'type':'type','text':'-'+'a'*48,'delay_ms':100}),
                         ['wtype','-d','100','-','-p','VoidSymbol'])
        with self.assertRaisesRegex(ValueError,'5 seconds'):
            cu.standalone_type_argv({'type':'type','text':'-'+'a'*49,'delay_ms':100})


class DesktopPreflight(unittest.TestCase):
    """desktop_act against patched compositor/capture/input; no real device is touched."""
    def setUp(self):
        from PIL import Image
        self.image=Image.new('RGB',(20,20))
        self.monitor={'name':'test','x':0,'y':0,'width':20,'height':20,'scale':1}
        self.meta={'backend':'desktop','scope':'window','created':time.time(),
                   'window':'fixture','window_bounds':[0,0,20,20],
                   'monitor':'test','monitor_box':[0,0,20,20],'monitor_scale':1,
                   'monitor_transform':0,'image_size':[20,20],'region':[0,0,20,20],
                   'image':'synthetic.png','max_width':1280,'pixel_sha256':'fixture'}
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        # A mock test must never reach the live session socket.
        self.indicator=self.stack.enter_context(patch.object(indicator,'request',return_value=False))
        self.stack.enter_context(patch.object(indicator.socket,'socket',
                                              side_effect=AssertionError('indicator real connection attempted')))
        self.stack.enter_context(patch.object(cu,'check_cancel'))
        self.focus=self.stack.enter_context(patch.object(cu,'focus'))
        self.stack.enter_context(patch.object(cu.time,'sleep'))
        # No fcitx5-remote here: literal_keyboard yields without touching IME state.
        # The daemon scan is mocked absent so this never depends on the test machine.
        self.stack.enter_context(patch.object(cu.shutil,'which',return_value=None))
        self.stack.enter_context(patch.object(cu,'fcitx5_running',return_value=False))
        self.stack.enter_context(patch.object(cu,'window',return_value={'at':[0,0],'size':[20,20]}))
        self.stack.enter_context(patch.object(cu,'hypr',side_effect=self.hypr))
        self.stack.enter_context(patch.object(cu,'observe',side_effect=self.observe))
        self.stack.enter_context(patch('PIL.Image.open',return_value=self.image))
        self.pointer_cls=self.stack.enter_context(patch.object(cu,'Pointer'))
        self.pointer=self.pointer_cls.return_value
        self.typed=self.stack.enter_context(patch.object(cu,'run_cancelable',return_value=''))

    def hypr(self,env,query):
        if query=='monitors':return [dict(self.monitor)]
        if query=='activewindow':return {'address':'fixture'}
        if query=='cursorpos':return {'x':10,'y':10}
        raise AssertionError('unexpected compositor query '+query)

    def observe(self,env,address,crop,max_width,**kwargs):
        if kwargs.get('persist',True):return self.meta.copy()
        return self.image,self.meta.copy()

    def test_keyboard_only_batch_does_not_open_pointer(self):
        result=cu.desktop_act({},self.meta,[{'type':'type','text':'hello'},
                                            {'type':'key','keys':['Enter']},
                                            {'type':'wait','ms':10}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],3)
        self.pointer_cls.assert_not_called()
        self.assertEqual(self.typed.call_count,2)
        self.indicator.assert_not_called()

    def test_wait_never_opens_keyboard_or_pointer(self):
        with patch.object(cu,'wait_cancelable') as wait:
            result=cu.desktop_act({},self.meta,[{'type':'wait','ms':25}])
        self.assertTrue(result['ok'],result)
        wait.assert_called_once_with(.025)
        self.typed.assert_not_called()
        self.pointer_cls.assert_not_called()

    def test_pointer_batch_opens_and_closes_pointer_once(self):
        result=cu.desktop_act({},self.meta,[{'type':'move','x':10,'y':10}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],1)
        self.pointer_cls.assert_called_once()
        self.pointer.close.assert_called_once()
        self.assertGreaterEqual(self.pointer.command.call_count,1)
        self.typed.assert_not_called()

    def test_leading_dash_type_uses_stdin_within_budget(self):
        result=cu.desktop_act({},self.meta,[{'type':'type','text':'-hello'}])
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['completed'],1)
        self.pointer_cls.assert_not_called()
        self.typed.assert_called_once()
        self.assertEqual(self.typed.call_args.args[0],['wtype','-','-p','VoidSymbol'])
        self.assertEqual(self.typed.call_args.kwargs['input'],'-hello')

    def test_oversized_leading_dash_type_rejected_before_input(self):
        actions=[{'type':'type','text':'-'+'a'*60,'delay_ms':100}]
        with self.assertRaisesRegex(ValueError,'5 seconds'):
            cu.desktop_act({},self.meta,actions)
        self.focus.assert_not_called()
        self.pointer_cls.assert_not_called()
        self.typed.assert_not_called()

    def test_ime_cleanup_failure_keeps_acknowledged_count_and_stops(self):
        from contextlib import contextmanager
        @contextmanager
        def cleanup_fails(*args,**kwargs):
            yield
            raise RuntimeError('IME restore failed')
        cases=[([{'type':'type','text':'hello'},{'type':'type','text':'world'}],2),
               ([{'type':'type','text':'-hello'}],1)]
        for actions,count in cases:
            with self.subTest(actions=actions),patch.object(cu,'literal_keyboard',cleanup_fails), \
                 patch.object(cu,'wait_cancelable') as wait:
                self.typed.reset_mock()
                result=cu.desktop_act({},self.meta,actions+[{'type':'wait','ms':10}])
                self.assertFalse(result['ok']);self.assertEqual(result['completed'],count)
                self.assertIn('IME restore failed',result['error'])
                self.assertIn('execution_ms',result)
                self.assertEqual(self.typed.call_count,1);wait.assert_not_called()

    def test_keyboard_error_survives_real_ime_restore_failure(self):
        def remote(argv,env,timeout=None):
            if argv==['fake-remote']:return '1' if remote.closed else '2'
            if argv[-1]=='-o':raise RuntimeError('restore failed')
            remote.closed=True
            return ''
        remote.closed=False
        with patch.object(cu.shutil,'which',return_value='fake-remote'), \
             patch.object(cu,'run',side_effect=remote), \
             patch.object(cu,'run_cancelable',side_effect=RuntimeError('input failed')):
            # Avoid a real IME; the production context manager still runs its cleanup.
            result=cu.desktop_act({},self.meta,[{'type':'type','text':'hello'}])
        self.assertFalse(result['ok']);self.assertEqual(result['completed'],0)
        self.assertIn('input failed',result['error'])

    def test_restore_failure_preserves_primary_and_warns_once(self):
        import io
        from contextlib import redirect_stderr
        primary = ValueError('typing failed')
        state = ['2']
        def remote(argv, env, timeout=None):
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise RuntimeError('restore failed\nsecond line')
            return ''
        with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
             patch.object(cu, 'run', side_effect=remote), \
             patch.object(cu, 'fcitx5_running', return_value=False):
            err = io.StringIO()
            with redirect_stderr(err):
                with self.assertRaises(ValueError) as caught:
                    with cu.literal_keyboard({}):
                        raise primary
        self.assertIs(caught.exception, primary, 'primary identity, type and code survive')
        lines = err.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 1, 'exactly one warning line')
        self.assertLessEqual(len(lines[0]), 400)
        self.assertIn('IME restoration failed', lines[0])
        self.assertIn('restore failed second line', lines[0])

    def test_warning_never_echoes_primary_message(self):
        import io
        from contextlib import redirect_stderr
        sentinel = 'SECRET-wtype-stderr-user-input-8493'
        primary = RuntimeError('typing failed: ' + sentinel)
        state = ['2']
        def remote(argv, env, timeout=None):
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise RuntimeError('restore failed')
            return ''
        with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
             patch.object(cu, 'run', side_effect=remote), \
             patch.object(cu, 'fcitx5_running', return_value=False):
            err = io.StringIO()
            with redirect_stderr(err):
                with self.assertRaises(RuntimeError) as caught:
                    with cu.literal_keyboard({}):
                        raise primary
        self.assertIs(caught.exception, primary)
        warning = err.getvalue()
        self.assertNotIn(sentinel, warning, 'primary message must never leak into the warning')
        self.assertIn('IME restoration failed', warning)
        self.assertIn('restore failed', warning)
        self.assertIn('RuntimeError', warning, 'primary is named by type only')
        self.assertEqual(len(warning.strip().splitlines()), 1)
        self.assertLessEqual(len(warning.strip()), 400)

    def test_termination_primary_survives_restore_failure(self):
        import io
        from contextlib import redirect_stderr
        for error in (KeyboardInterrupt(), SystemExit(7)):
            with self.subTest(error=type(error).__name__):
                sentinel = error
                state = ['2']
                def remote(argv, env, timeout=None):
                    if argv == ['fake-remote']:
                        return state[0]
                    if argv[-1] == '-c':
                        state[0] = '1'
                    if argv[-1] == '-o':
                        raise RuntimeError('restore failed')
                    return ''
                with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                     patch.object(cu, 'run', side_effect=remote), \
                     patch.object(cu, 'fcitx5_running', return_value=False):
                    err = io.StringIO()
                    with redirect_stderr(err):
                        with self.assertRaises(type(sentinel)) as caught:
                            with cu.literal_keyboard({}):
                                raise sentinel
                self.assertIs(caught.exception, sentinel)
                self.assertIn('IME restoration failed', err.getvalue())

    def test_new_termination_during_restore_wins_over_ordinary_primary(self):
        import io
        from contextlib import redirect_stderr
        calls = []
        state = ['2']

        def remote(argv, env, timeout=None):
            calls.append(argv)
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise KeyboardInterrupt('late interrupt')
            return ''
        with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
             patch.object(cu, 'run', side_effect=remote), \
             patch.object(cu, 'fcitx5_running', return_value=False):
            err = io.StringIO()
            with redirect_stderr(err):
                with self.assertRaises(KeyboardInterrupt):
                    with cu.literal_keyboard({}):
                        raise ValueError('typing failed')
        self.assertIn('IME restoration failed', err.getvalue())
        self.assertEqual([a for a in calls if a[-1] == '-o'], [['fake-remote', '-o']])

    def test_restore_only_failure_keeps_count_and_runs_no_next_group(self):
        import io
        from contextlib import redirect_stderr
        state = ['2']
        def remote(argv, env, timeout=None):
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
            if argv[-1] == '-o':
                raise RuntimeError('restore failed')
            return ''
        with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
             patch.object(cu, 'run', side_effect=remote), \
             patch.object(cu, 'fcitx5_running', return_value=False), \
             patch.object(cu, 'wait_cancelable') as wait:
            self.typed.reset_mock()
            err = io.StringIO()
            with redirect_stderr(err):
                result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello'},
                                                        {'type': 'wait', 'ms': 10}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['completed'], 1, 'acknowledged input stays counted')
        self.assertIn('restore failed', result['error'])
        self.assertEqual(self.typed.call_count, 1, 'exactly one input, no replay')
        wait.assert_not_called()
        self.assertIn('IME restoration failed', err.getvalue())

    def test_restore_flag_envelope_cases(self):
        import io
        from contextlib import redirect_stderr
        def fake_remote(state, fail_restore=True):
            def remote(argv, env, timeout=None):
                if argv == ['fake-remote']:
                    return state[0]
                if argv[-1] == '-c':
                    state[0] = '1'
                elif argv[-1] == '-o':
                    if fail_restore:
                        raise RuntimeError('restore failed')
                    state[0] = '2'
                return ''
            return remote
        # (1) restore-only failure: completed preserved, flag set, no escape.
        # Leading-dash case exercises the standalone branch (cu.py:804).
        for actions, count in [([{'type': 'type', 'text': 'hello'}], 1),
                              ([{'type': 'type', 'text': '-hello'}], 1),
                              ([{'type': 'type', 'text': 'hi'}, {'type': 'type', 'text': 'yo'}], 2)]:
            with self.subTest(kind='restore-only', actions=actions):
                with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                     patch.object(cu, 'run', side_effect=fake_remote(['2'])), \
                     patch.object(cu, 'fcitx5_running', return_value=False):
                    self.typed.reset_mock()
                    err = io.StringIO()
                    with redirect_stderr(err):
                        result = cu.desktop_act({}, self.meta, list(actions))
                self.assertFalse(result['ok'])
                self.assertEqual(result['completed'], count)
                self.assertTrue(result.get('ime_restore_failed'))
                self.assertIn('restore failed', result['error'])
                if any(a.get('text', '').startswith('-') for a in actions):
                    self.assertEqual(self.typed.call_args.kwargs['input'], '-hello')
        # (2) primary+restore failure: primary preserved, flag still set.
        # Both grouped and standalone inputs take this path.
        for text in ('hello', '-hello'):
            with self.subTest(kind='primary-plus-restore', text=text):
                with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                     patch.object(cu, 'run', side_effect=fake_remote(['2'])), \
                     patch.object(cu, 'fcitx5_running', return_value=False), \
                     patch.object(cu, 'run_cancelable', side_effect=RuntimeError('input failed')) as typed_fail:
                    err = io.StringIO()
                    with redirect_stderr(err):
                        result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': text}])
                self.assertFalse(result['ok'])
                self.assertEqual(result['completed'], 0)
                self.assertIn('input failed', result['error'])
                self.assertTrue(result.get('ime_restore_failed'))
                if text.startswith('-'):
                    self.assertEqual(typed_fail.call_args.kwargs['input'], text)
        # (3) success path: flag key absent.
        with self.subTest(kind='success'):
            with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                 patch.object(cu, 'run', side_effect=fake_remote(['2'], fail_restore=False)), \
                 patch.object(cu, 'fcitx5_running', return_value=False):
                self.typed.reset_mock()
                result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello'}])
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['completed'], 1)
            self.assertNotIn('ime_restore_failed', result)
        # --no-after success: flag absent, capture skipped (cu.py:839).
        with self.subTest(kind='no-after-success'):
            with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                 patch.object(cu, 'run', side_effect=fake_remote(['2'], fail_restore=False)), \
                 patch.object(cu, 'fcitx5_running', return_value=False):
                self.typed.reset_mock()
                result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello'}],
                                        after_capture=False)
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['completed'], 1)
            self.assertNotIn('ime_restore_failed', result)
            self.assertTrue(result.get('after_skipped'))
            self.assertNotIn('after', result)
        # --no-after restore failure: error branch falls through to the merge
        # at cu.py:844, so the flag is still reported (standalone input here).
        with self.subTest(kind='no-after-restore-failure'):
            with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                 patch.object(cu, 'run', side_effect=fake_remote(['2'])), \
                 patch.object(cu, 'fcitx5_running', return_value=False):
                self.typed.reset_mock()
                err = io.StringIO()
                with redirect_stderr(err):
                    result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': '-hello'}],
                                            after_capture=False)
            self.assertFalse(result['ok'])
            self.assertEqual(result['completed'], 1)
            self.assertTrue(result.get('ime_restore_failed'))
            self.assertIn('restore failed', result['error'])
            self.assertNotIn('after_skipped', result)
            self.assertEqual(self.typed.call_args.kwargs['input'], '-hello')
        # (4) compose form and no-remote-at-all: flag absent, typing proceeds.
        with self.subTest(kind='compose'):
            calls = []
            def remote(argv, env, timeout=None):
                calls.append(list(argv))
                return '2'
            with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
                 patch.object(cu, 'run', side_effect=remote), \
                 patch.object(cu, 'fcitx5_running', return_value=False):
                self.typed.reset_mock()
                result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello', 'ime': 'compose'}])
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['completed'], 1)
            self.assertNotIn('ime_restore_failed', result)
            self.assertEqual(self.typed.call_count, 1)
            self.assertEqual([a for a in calls if len(a) > 1], [])
        with self.subTest(kind='no-remote'):
            self.typed.reset_mock()
            result = cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello'}])
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['completed'], 1)
            self.assertNotIn('ime_restore_failed', result)
            self.assertEqual(self.typed.call_count, 1)
        # (5) cancel aborts before input.
        with self.subTest(kind='cancel'):
            with patch.object(cu, 'check_cancel', side_effect=RuntimeError('cancelled')):
                self.typed.reset_mock()
                with self.assertRaisesRegex(RuntimeError, 'cancelled'):
                    cu.desktop_act({}, self.meta, [{'type': 'type', 'text': 'hello'}])
            self.typed.assert_not_called()

    def test_cumulative_budget_is_passed_to_each_helper_call(self):
        import time as time_module
        calls = []
        clock = [1000.0]
        state = ['2']

        def remote(argv, env, timeout=None):
            calls.append((list(argv), timeout))
            clock[0] += 0.1
            if argv == ['fake-remote']:
                return state[0]
            state[0] = '1' if argv[-1] == '-c' else '2'
            return ''
        with patch.object(cu.shutil, 'which', return_value='fake-remote'), \
             patch.object(cu, 'run', side_effect=remote), \
             patch.object(cu, 'fcitx5_running', return_value=False), \
             patch.object(cu.time, 'monotonic', side_effect=lambda: clock[0]), \
             patch.object(cu.time, 'sleep'):
            with cu.literal_keyboard({}):
                pass
        by_flag = {tuple(a): t for a, t in calls}
        # -c runs with the full 0.5s budget; each query after a 0.1s command
        # sees only the remainder, never a fresh full budget.
        self.assertAlmostEqual(by_flag[('fake-remote', '-c')], 0.5, places=6)
        self.assertAlmostEqual(by_flag[('fake-remote', '-o')], 0.5, places=6)
        queries = [t for (a, t) in calls if len(a) == 1]
        self.assertTrue(queries, 'state was queried')
        # The initial query owns a fresh 0.5s budget; every query after a
        # command sees only the remainder of its switch budget.
        self.assertAlmostEqual(queries[0], 0.5, places=6)
        for timeout in queries[1:]:
            self.assertLess(timeout, 0.5)
            self.assertGreaterEqual(timeout, 0.29)


class HangingHelperBudget(unittest.TestCase):
    """N16: hanging helpers fail deterministically; mutation still restores once."""

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(cu.shutil, 'which', return_value='fake-remote'))
        self.stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))
        self.clock = [1000.0]
        self.stack.enter_context(
            patch.object(cu.time, 'monotonic', side_effect=lambda: self.clock[0]))
        self.stack.enter_context(patch.object(cu.time, 'sleep'))

    def test_hanging_initial_query_fails_before_any_command(self):
        import subprocess
        calls = []

        def remote(argv, env, timeout=None):
            calls.append((list(argv), timeout))
            self.clock[0] += 10.0
            raise subprocess.TimeoutExpired(argv, timeout)

        with patch.object(cu, 'run', side_effect=remote):
            with self.assertRaises(subprocess.TimeoutExpired):
                with cu.literal_keyboard({}):
                    self.fail('yield must never be reached')
        self.assertEqual(len(calls), 1, 'only the initial query ran')
        self.assertEqual(len(calls[0][0]), 1)
        self.assertAlmostEqual(calls[0][1], 0.5, places=6)

    def test_hanging_switch_query_restores_once_without_input(self):
        import subprocess
        calls = []
        state = ['2']
        phase = ['initial']

        def remote(argv, env, timeout=None):
            calls.append((list(argv), timeout))
            if argv == ['fake-remote']:
                if phase[0] == 'hang-query':
                    raise subprocess.TimeoutExpired(argv, timeout)
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'
                phase[0] = 'hang-query'
            elif argv[-1] == '-o':
                state[0] = '2'
                phase[0] = 'restore-query-ok'
            return ''

        with patch.object(cu, 'run', side_effect=remote):
            with self.assertRaisesRegex(RuntimeError, 'fcitx5 state change timed out'):
                with cu.literal_keyboard({}):
                    self.fail('no input after a hanging switch query')
        flags = [a for a, t in calls if len(a) > 1]
        self.assertEqual(flags, [['fake-remote', '-c'], ['fake-remote', '-o']],
                         'restore runs exactly once after the hanging query')
        self.assertEqual(state[0], '2')

    def test_mutating_flag_then_timeout_still_restores_once(self):
        import subprocess
        calls = []
        state = ['2']

        def remote(argv, env, timeout=None):
            calls.append((list(argv), timeout))
            if argv == ['fake-remote']:
                return state[0]
            if argv[-1] == '-c':
                state[0] = '1'  # mutated, then the reply never arrives
                self.clock[0] += 10.0
                raise subprocess.TimeoutExpired(argv, timeout)
            state[0] = '2'
            return ''

        with patch.object(cu, 'run', side_effect=remote):
            with self.assertRaisesRegex(RuntimeError, 'fcitx5 state change timed out'):
                with cu.literal_keyboard({}):
                    self.fail('yield must never be reached')
        flags = [a for a, t in calls if len(a) > 1]
        self.assertEqual(flags, [['fake-remote', '-c'], ['fake-remote', '-o']])
        self.assertEqual(state[0], '2', 'restore ran after the mutated timeout')

    def test_hanging_restore_flag_and_query_propagate(self):
        import subprocess
        for hang in ('flag', 'query'):
            with self.subTest(hang=hang):
                calls = []
                state = ['2']

                def remote(argv, env, timeout=None):
                    calls.append((list(argv), timeout))
                    if argv == ['fake-remote']:
                        if hang == 'query' and state[0] == 'restoring':
                            raise subprocess.TimeoutExpired(argv, timeout)
                        return state[0]
                    if argv[-1] == '-c':
                        state[0] = '1'
                    elif argv[-1] == '-o':
                        if hang == 'flag':
                            raise subprocess.TimeoutExpired(argv, timeout)
                        state[0] = 'restoring'
                    return ''

                entered = []
                with patch.object(cu, 'run', side_effect=remote):
                    with self.assertRaisesRegex(RuntimeError, 'fcitx5 state change timed out'):
                        with cu.literal_keyboard({}):
                            entered.append(True)
                self.assertEqual(entered, [True], 'input ran, restore hung')
                restores = [a for a, t in calls if a[-1:] == ['-o']]
                self.assertEqual(len(restores), 1, 'restore attempted exactly once')

    def test_late_correct_reply_is_rejected(self):
        # Initial 2, flag completes within budget, then the state query RETURNS
        # the expected 1 while advancing the clock across the deadline. This
        # targets the AFTER-reply deadline check: without it the late success
        # would enter the body. A query cap fails immediately, never loops.
        seen = []
        state = ['2']
        queries = [0]

        def remote(argv, env, timeout=None):
            seen.append((list(argv), timeout))
            if argv == ['fake-remote']:
                queries[0] += 1
                if queries[0] > 3:
                    raise AssertionError('unexpected query: infinite loop guard')
                if queries[0] == 2:
                    self.clock[0] += 10.0
                return state[0]
            if argv[-1] == '-c':
                self.clock[0] += 0.1
                state[0] = '1'
                return ''
            state[0] = '2'
            return ''

        with patch.object(cu, 'run', side_effect=remote):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                with cu.literal_keyboard({}):
                    self.fail('a late success is not a success')
        # The late query really happened: initial, one switch query, one restore.
        self.assertEqual([len(a) for a, t in seen], [1, 2, 1, 2, 1])
        self.assertAlmostEqual(seen[2][1], 0.4, places=6,
                               msg='switch query sees remainder after flag')
        self.assertAlmostEqual(seen[3][1], 0.5, places=6,
                               msg='restore runs on a fresh budget')
        restores = [a for a, t in seen if a[-1:] == ['-o']]
        self.assertEqual(len(restores), 1, 'restore attempted exactly once')


    def test_cumulative_queries_share_one_budget(self):
        # Explicit phases: initial returns 2; -c consumes .2; two deactivate
        # queries each consume .15 while state stays wrong; the deadline then
        # expires before any third query and the body never runs. Restore gets
        # a fresh budget. A query cap fails immediately instead of looping.
        seen = []
        state = ['2']
        queries = [0]

        def remote(argv, env, timeout=None):
            seen.append((list(argv), timeout))
            if argv == ['fake-remote']:
                queries[0] += 1
                if queries[0] > 4:
                    raise AssertionError('unexpected query: infinite loop guard')
                self.clock[0] += 0.15
                return state[0]
            if argv[-1] == '-c':
                self.clock[0] += 0.2
                return ''
            return ''

        with patch.object(cu, 'run', side_effect=remote):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                with cu.literal_keyboard({}):
                    self.fail('the switch must time out before a third query')
        timeouts = [t for a, t in seen]
        # Initial query, flag, two queries, restore flag, restore query.
        self.assertEqual([len(a) for a, t in seen], [1, 2, 1, 1, 2, 1])
        self.assertAlmostEqual(timeouts[0], 0.5, places=6, msg='initial query')
        self.assertAlmostEqual(timeouts[1], 0.5, places=6, msg='flag')
        self.assertAlmostEqual(timeouts[2], 0.3, places=6, msg='first query sees remainder')
        self.assertAlmostEqual(timeouts[3], 0.15, places=6, msg='second query shrinks further')
        self.assertAlmostEqual(timeouts[4], 0.5, places=6, msg='restore has a fresh budget')
        restores = [a for a, t in seen if a[-1:] == ['-o']]
        self.assertEqual(len(restores), 1, 'restore attempted exactly once')




class IMEContextMatrix(unittest.TestCase):
    """Item 7: untouched state 0 and partial handler installation."""

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(cu.shutil, 'which', return_value='fake-remote'))
        self.stack.enter_context(patch.object(cu, 'fcitx5_running', return_value=False))

    def test_initial_state_zero_sends_no_command(self):
        calls = []

        def remote(argv, env, timeout=None):
            calls.append(list(argv))
            return '0'

        with patch.object(cu, 'run', side_effect=remote):
            with cu.literal_keyboard({}):
                pass
        self.assertEqual(calls, [['fake-remote']],
                         'state 0 needs no deactivate and no restore')

    def test_second_handler_failure_restores_first(self):
        import signal as signal_module
        real_signal = signal_module.signal
        original_term = signal_module.getsignal(signal_module.SIGTERM)
        original_hup = signal_module.getsignal(signal_module.SIGHUP)
        attempts = []

        def flaky(sig, handler):
            attempts.append(sig)
            if len(attempts) == 2:
                raise OSError('install failed once')
            return real_signal(sig, handler)

        entered = []
        try:
            with patch.object(signal_module, 'signal', side_effect=flaky):
                with patch.object(cu, 'run', return_value='2'):
                    with cu.literal_keyboard({}):
                        entered.append(True)
            self.fail('the install failure must propagate')
        except OSError as exc:
            self.assertIn('install failed once', str(exc))
        self.assertEqual(entered, [], 'the body never ran')
        self.assertIs(signal_module.getsignal(signal_module.SIGTERM), original_term)
        self.assertIs(signal_module.getsignal(signal_module.SIGHUP), original_hup)
        self.assertEqual(attempts.count(signal_module.SIGTERM), 2,
                         'installed once, unwound once, no global leak')


if __name__=='__main__':unittest.main()

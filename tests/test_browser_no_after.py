"""`browser act --no-after` CLI contract. No session, no desktop, no browser.

Every check drives cu.main() with the adapter, the session token, the cancel check and
the desktop lock mocked out, and counts what reached the adapter. Expected rejections
are stated as the user-visible error strings, never as a copy of the predicate logic.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu

ASSERT = lambda **kw: dict(type='assert', ref='e1', **kw)
CLICK = {'type': 'click', 'ref': 'e1'}


class NoAfterCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.actions_file = Path(self.tmp.name) / 'actions.json'
        self.dispatched = []
        for name, value in (('browser', self.browser), ('require_session', None),
                            ('check_cancel', None), ('prepare_state', None),
                            ('locked', self.locked)):
            patcher = mock.patch.object(cu, name, new=value) if value is not None \
                else mock.patch.object(cu, name)
            patcher.start()
            self.addCleanup(patcher.stop)
        token = mock.patch.dict('os.environ', {'CU_SESSION_TOKEN': 'test'})
        token.start()
        self.addCleanup(token.stop)

    def browser(self, request):
        self.dispatched.append(request)
        return {'ok': True}

    @contextlib.contextmanager
    def locked(self):
        yield None

    def run_cli(self, actions, *flags):
        self.actions_file.write_text(json.dumps(actions))
        argv = ['cu', 'browser', 'act', '--target', 'x', '--snapshot', 's',
                '--actions', str(self.actions_file), *flags]
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(out):
            code = cu.main()
        return code, json.loads(out.getvalue())

    def test_no_after_forwarded_only_for_act(self):
        self.run_cli([ASSERT(text='ok')], '--no-after')
        self.assertEqual(len(self.dispatched), 1)
        self.assertIs(self.dispatched[0]['no_after'], True)

        self.dispatched.clear()
        self.run_cli([ASSERT(text='ok')])
        self.assertEqual(len(self.dispatched), 1)
        self.assertNotIn('no_after', self.dispatched[0],
                         'the default request must not gain a no_after key')

    def test_default_request_gains_no_key(self):
        self.run_cli([ASSERT(text='ok')])
        default = json.loads(json.dumps(self.dispatched[0], sort_keys=True))
        self.assertEqual(sorted(default), ['actions', 'endpoint', 'image', 'max_elements',
                                           'operation', 'snapshot', 'target'])

    def test_no_after_rejected_on_other_operations(self):
        for operation in ('observe', 'tabs'):
            argv = ['cu', 'browser', operation, '--no-after']
            out = io.StringIO()
            with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(out):
                with self.assertRaises(ValueError) as raised:
                    cu.main()
            self.assertIn('act', str(raised.exception))
            self.assertEqual(self.dispatched, [], operation + ' must not dispatch')

    def test_no_after_rejects_image_before_dispatch(self):
        with self.assertRaises(ValueError):
            self.run_cli([ASSERT(text='ok')], '--no-after', '--image')
        self.assertEqual(self.dispatched, [])

    def test_invalid_terminal_assert_rejected_before_dispatch(self):
        for actions in ([CLICK], [{'type': 'wait', 'ms': 5}],
                        [{'type': 'fill', 'ref': 'e1', 'text': 'x'}], [ASSERT()],
                        [ASSERT(text='')], [ASSERT(value=5)], [ASSERT(value=None, text='ok')], [ASSERT(checked='yes')],
                        # text wins over checked, so the ignored checked:true is no rescue
                        [ASSERT(text='', checked=True)], [ASSERT(text='ok'), CLICK]):
            with self.subTest(actions=actions):
                self.dispatched.clear()
                with self.assertRaises(ValueError):
                    self.run_cli(actions, '--no-after')
                self.assertEqual(self.dispatched, [], 'must not dispatch')

    def test_rejections_do_not_apply_without_the_flag(self):
        for actions in ([ASSERT()], [ASSERT(text='')]):
            with self.subTest(actions=actions):
                self.dispatched.clear()
                code, _ = self.run_cli(actions)
                self.assertEqual(code, 0)
                self.assertEqual(len(self.dispatched), 1,
                                 'the default path must still dispatch these')

    def test_empty_value_and_checked_false_accepted(self):
        for actions in ([ASSERT(value='')], [ASSERT(checked=False)],
                        [ASSERT(text='ok')], [ASSERT(value='payload')]):
            with self.subTest(actions=actions):
                self.dispatched.clear()
                code, result = self.run_cli(actions, '--no-after')
                self.assertEqual(code, 0)
                self.assertTrue(result['ok'])
                self.assertEqual(self.dispatched[0]['no_after'], True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
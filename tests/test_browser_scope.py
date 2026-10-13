"""`browser observe --scope` CLI contract. No session, no browser, no GUI."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cu

BASE = ['cu', 'browser', 'observe', '--target', 'x', '--snapshot', 's']


class ScopeCli(unittest.TestCase):
    def setUp(self):
        self.dispatched = []
        for name, value in (('browser', self.browser), ('require_session', None),
                            ('check_cancel', None), ('prepare_state', None),
                            ('browser_start', self.browser_start)):
            patcher = mock.patch.object(cu, name, new=value) if value is not None \
                else mock.patch.object(cu, name)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.locked = mock.patch.object(cu, 'locked', new=self.locked_cm).start()
        self.addCleanup(mock.patch.stopall)
        self.environment = mock.patch.object(cu, 'environment', new=mock.Mock()).start()

    def browser(self, request):
        self.dispatched.append(request)
        return {'ok': True}

    def browser_start(self, env, endpoint):
        raise AssertionError('browser_start must not run in these checks')

    @contextlib.contextmanager
    def locked_cm(self):
        yield None

    def run_cli(self, argv):
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(out):
            code = cu.main()
        return code, out.getvalue()

    def test_scope_forwarded_only_for_observe_when_given(self):
        self.run_cli(BASE + ['--scope', '#task'])
        self.assertEqual(self.dispatched[0]['scope'], '#task')
        self.dispatched.clear()
        self.run_cli(BASE)
        self.assertNotIn('scope', self.dispatched[0],
                         'an absent --scope must not add the key')

    def test_scope_rejected_on_other_operations(self):
        for operation in ('act', 'tabs', 'start'):
            with self.subTest(operation=operation):
                self.dispatched.clear()
                with self.assertRaises(ValueError):
                    self.run_cli(['cu', 'browser', operation, '--scope', '#task'])
                self.assertEqual(self.dispatched, [])
                self.assertFalse(self.environment.called,
                                 'invalid --scope must not touch the GUI environment')

    def test_empty_and_oversized_scope_rejected_before_dispatch(self):
        for value in ('', '   ', 'x' * 1025):
            with self.subTest(value=repr(value)):
                self.dispatched.clear()
                with self.assertRaises(ValueError):
                    self.run_cli(BASE + ['--scope', value])
                self.assertEqual(self.dispatched, [])

    def test_scope_at_the_length_limit_is_accepted(self):
        self.run_cli(BASE + ['--scope', 'x' * 1024])
        self.assertEqual(len(self.dispatched[0]['scope']), 1024)

    def test_non_bmp_boundary_counts_utf16_units(self):
        # The limit is UTF-16 code units, so a non-BMP selector reaches it at half
        # the code-point count. '#'+511 emoji+'a' is exactly 1024 units.
        emoji = '\U0001F431'
        accepted = '#' + emoji * 511 + 'a'
        refused = '#' + emoji * 512
        self.assertEqual(len(accepted), 513, '513 code points')
        self.assertEqual(len(accepted.encode('utf-16-le')) // 2, 1024)
        self.assertEqual(len(refused.encode('utf-16-le')) // 2, 1025)
        self.run_cli(BASE + ['--scope', accepted])
        self.assertEqual(self.dispatched[0]['scope'], accepted, '1024 units accepted')
        self.dispatched.clear()
        with self.assertRaises(ValueError):
            self.run_cli(BASE + ['--scope', refused])
        self.assertEqual(self.dispatched, [], '1025 units refused before dispatch')
        self.assertFalse(self.environment.called)

    def test_scope_survives_trimming_only_for_validation(self):
        # A surrounding-space selector is still forwarded verbatim: the browser
        # resolves the CSS, this layer only rejects a blank value.
        self.run_cli(BASE + ['--scope', '  #task  '])
        self.assertEqual(self.dispatched[0]['scope'], '  #task  ')

    def test_scope_is_not_forwarded_to_act_request_shape(self):
        self.run_cli(BASE + ['--scope', '#task', '--max-elements', '8'])
        request = self.dispatched[0]
        self.assertEqual(request['operation'], 'observe')
        self.assertEqual(request['max_elements'], 8)
        self.assertNotIn('no_after', request, 'scope must not imply no_after')


if __name__ == '__main__':
    unittest.main(verbosity=2)
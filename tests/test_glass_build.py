"""Unit tests for scripts/build-glass.py; mocked subprocess only, no build, no git writes."""
import importlib.util
from pathlib import Path
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_glass', ROOT / 'scripts/build-glass.py')
build_glass = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_glass)


class Done:
    def __init__(self, returncode, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class Fake:
    """Answers the gate commands; `apply_ok` decides whether the patch lands."""

    def __init__(self, source, apply_ok, initial='', final=None, reverse_rc=1, status_rc=0,
                 second_status_rc=0):
        self.source = str(source)
        self.apply_ok = apply_ok
        self.initial = initial
        self.final = initial if final is None else final
        self.reverse_rc = reverse_rc
        self.status_rc = status_rc
        self.second_status_rc = second_status_rc
        self.calls = []
        self.status_calls = 0

    def __call__(self, args, cwd=None, capture=True, **kwargs):
        self.calls.append(list(args))
        joined = ' '.join(args)
        if '--show-toplevel' in joined:
            return Done(0, self.source + '\n')
        if 'rev-parse' in joined:
            return Done(0, build_glass.REQUIRED_COMMIT + '\n')
        if joined.startswith('pkg-config'):
            return Done(0, build_glass.REQUIRED_HYPRLAND + '\n')
        if '--reverse' in joined:
            return Done(self.reverse_rc, '', '' if self.reverse_rc == 0 else 'not applied')
        if 'status' in joined:
            assert '--untracked-files=all' in joined, 'status without flag: ' + joined
            self.status_calls += 1
            rc = self.status_rc if self.status_calls == 1 else self.second_status_rc
            if rc != 0:
                return Done(rc, '', 'status boom')
            body = self.initial if self.status_calls == 1 else self.final
            return Done(0, body + '\n' if body else '')
        if joined.startswith('git apply') and '--check' not in joined:
            return Done(0 if self.apply_ok else 1, '', '' if self.apply_ok else 'patch does not apply')
        return Done(0)

    def made(self):
        return [c for c in self.calls if c and c[0] == 'make']


class GlassBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name)
        patch_file = self.source.parent / (self.source.name + '.patch')
        patch_file.write_text('--- a\n+++ b\n')
        self.addCleanup(patch_file.unlink)
        patcher = patch.object(build_glass, 'PATCH', patch_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_apply_failure_stops_before_make(self):
        fake = Fake(self.source, apply_ok=False)
        with patch.object(build_glass.subprocess, 'run', fake):
            with self.assertRaises(SystemExit) as caught:
                build_glass.main([str(self.source)])
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse([c for c in fake.calls if c[0] == 'make'], 'make ran after a failed apply')

    def test_successful_apply_then_make(self):
        fake = Fake(self.source, apply_ok=True)
        with patch.object(build_glass.subprocess, 'run', fake), \
                patch('builtins.print'):
            self.assertEqual(build_glass.main([str(self.source)]), 0)
        self.assertTrue([c for c in fake.calls if c[0] == 'make'])
        self.assertIn('HYPRGLASS_VERSION=' + build_glass.VERSION,
                      [a for c in fake.calls if c[0] == 'make' for a in c])


    def drive(self, fake, argv):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(build_glass.subprocess, 'run', fake), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                return 0, build_glass.main(argv), out.getvalue(), err.getvalue()
            except SystemExit as exited:
                return 1, exited.code, out.getvalue(), err.getvalue()

    def test_dirty_tracked_initial_refuses_by_default(self):
        fake = Fake(self.source, True, initial=' M a.py')
        _, code, out, err = self.drive(fake, [str(self.source)])
        self.assertEqual(code, 2)
        self.assertIn('dirty', err)
        self.assertEqual(fake.made(), [])

    def test_untracked_only_initial_refuses_by_default(self):
        fake = Fake(self.source, True, initial='?? new.py')
        _, code, out, err = self.drive(fake, [str(self.source)])
        self.assertEqual(code, 2)
        self.assertIn('dirty', err)
        self.assertEqual(fake.made(), [])

    def test_allow_dirty_bypasses_initial_dirt_reaches_make(self):
        fake = Fake(self.source, True, initial=' M a.py', final=' M a.py')
        _, code, out, _ = self.drive(fake, [str(self.source), '--allow-dirty'])
        self.assertEqual(code, 0)
        self.assertTrue(fake.made())

    def test_status_failure_fails_before_make(self):
        fake = Fake(self.source, True, status_rc=1)
        _, code, _, err = self.drive(fake, [str(self.source)])
        self.assertEqual(code, 2)
        self.assertIn('status', err)
        self.assertEqual(fake.made(), [])

    def test_clean_fresh_apply_stamps_build_dirty_true(self):
        fake = Fake(self.source, True, initial='', final=' M x.py')
        _, code, out, _ = self.drive(fake, [str(self.source)])
        self.assertEqual(code, 0)
        self.assertTrue(fake.made())
        self.assertIn('build_dirty=True', out)

    def test_prepatched_dirty_rerun_needs_flag(self):
        kw = dict(initial=' M x.py', final=' M x.py', reverse_rc=0)
        _, refused, _, _ = self.drive(Fake(self.source, True, **kw), [str(self.source)])
        self.assertEqual(refused, 2)
        fake = Fake(self.source, True, **kw)
        _, code, out, _ = self.drive(fake, [str(self.source), '--allow-dirty'])
        self.assertEqual(code, 0)
        self.assertTrue(fake.made())
        self.assertIn('build_dirty=True', out)

    def test_stdout_stamps_contain_all_fields(self):
        _, code, out, _ = self.drive(
            Fake(self.source, True, initial='', final=' M x.py'), [str(self.source)])
        self.assertEqual(code, 0)
        for key in ('commit=', 'initial_dirty=', 'allow_dirty=', 'build_dirty='):
            self.assertIn(key, out)
        _, refused, out, _ = self.drive(
            Fake(self.source, True, initial=' M a.py'), [str(self.source)])
        self.assertEqual(refused, 2)
        for key in ('commit=', 'initial_dirty=True', 'allow_dirty=False'):
            self.assertIn(key, out)


    def test_second_status_failure_fails_before_make(self):
        fake = Fake(self.source, True, initial='', second_status_rc=1)
        _, code, _, err = self.drive(fake, [str(self.source)])
        self.assertEqual(code, 2)
        self.assertIn('status', err)
        self.assertEqual(fake.made(), [])
        self.assertEqual(fake.status_calls, 2)

    def test_stamps_include_pinned_commit_value(self):
        _, code, out, _ = self.drive(
            Fake(self.source, True, initial='', final=' M x.py'), [str(self.source)])
        self.assertEqual(code, 0)
        self.assertIn(build_glass.REQUIRED_COMMIT, out)
        _, refused, out, _ = self.drive(
            Fake(self.source, True, initial=' M a.py'), [str(self.source)])
        self.assertEqual(refused, 2)
        self.assertIn(build_glass.REQUIRED_COMMIT, out)

    def test_real_git_untracked_visible_despite_show_untracked_no(self):
        repo = Path(self.tmp.name) / 'realrepo'
        repo.mkdir()
        def rc(args):
            done = subprocess.run(args, cwd=repo, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            return done
        rc(['git', 'init'])
        rc(['git', 'config', 'user.email', 't@t'])
        rc(['git', 'config', 'user.name', 't'])
        (repo / 'a.txt').write_text('a')
        rc(['git', 'add', 'a.txt'])
        rc(['git', 'commit', '-m', 'init'])
        rc(['git', 'config', 'status.showUntrackedFiles', 'no'])
        (repo / 'new.py').write_text('untracked')
        # Without the flag the config hides the file; with it the file shows.
        hidden = subprocess.run(['git', 'status', '--porcelain'],
                                cwd=repo, capture_output=True, text=True).stdout
        self.assertEqual(hidden.strip(), '')
        shown = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all'],
                               cwd=repo, capture_output=True, text=True).stdout
        self.assertIn('??', shown)
        fake = Fake(repo, True)
        seen = []
        real_run = subprocess.run

        def hybrid(args, cwd=None, capture=True, **kwargs):
            joined = ' '.join(args)
            if 'status' in joined:
                seen.append(joined)
                self.assertIn('--untracked-files=all', joined)
                return real_run(args, cwd=cwd, capture_output=capture, text=True)
            return fake(args, cwd=cwd, capture=capture, **kwargs)

        out, err = io.StringIO(), io.StringIO()
        with patch.object(build_glass.subprocess, 'run', hybrid), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as caught:
                build_glass.main([str(repo)])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn('dirty', err.getvalue())
        self.assertTrue(seen, 'no real status call made')
        self.assertEqual(fake.made(), [])


if __name__ == '__main__':
    unittest.main()
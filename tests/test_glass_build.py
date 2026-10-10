"""Unit tests for scripts/build-glass.py; mocked subprocess only, no build, no git writes."""
import importlib.util
from pathlib import Path
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

    def __init__(self, source, apply_ok):
        self.source = str(source)
        self.apply_ok = apply_ok
        self.calls = []

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
            return Done(1, '', 'not applied')
        if 'status' in joined:
            return Done(0, '')
        if joined.startswith('git apply') and '--check' not in joined:
            return Done(0 if self.apply_ok else 1, '', '' if self.apply_ok else 'patch does not apply')
        return Done(0)


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


if __name__ == '__main__':
    unittest.main()
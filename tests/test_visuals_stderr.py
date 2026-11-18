import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from textwrap import dedent
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'visuals.py'


class VisualsStderrTests(unittest.TestCase):
    def test_startup_import_failure_is_saved_before_local_imports(self):
        bootstrap = dedent(f"""
            import builtins, runpy, sys
            script = {str(SCRIPT)!r}
            original_import = builtins.__import__

            def fail_cursor_theme_import(name, *args, **kwargs):
                if name == 'cursor_theme':
                    raise RuntimeError('stderr capture sentinel')
                return original_import(name, *args, **kwargs)

            builtins.__import__ = fail_cursor_theme_import
            sys.argv = [script]
            runpy.run_path(script, run_name='__main__')
        """)
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env['HOME'] = home
            env.update({'XDG_RUNTIME_DIR': '/fixture/runtime',
                        'WAYLAND_DISPLAY': 'wayland-fixture',
                        'HYPRLAND_INSTANCE_SIGNATURE': 'fixture-instance'})
            result = subprocess.run([sys.executable, '-c', bootstrap], env=env,
                                    capture_output=True, text=True, timeout=5)
            log = Path(home) / '.cache/agent-computer-use/logs/visuals-stderr.log'
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(log.is_file())
            text = log.read_text()
            prefix = 'visuals: supplied compositor tuple: '
            tuple_line = next(line for line in text.splitlines() if line.startswith(prefix))
            self.assertEqual(json.loads(tuple_line[len(prefix):]), {
                'XDG_RUNTIME_DIR': '/fixture/runtime',
                'WAYLAND_DISPLAY': 'wayland-fixture',
                'HYPRLAND_INSTANCE_SIGNATURE': 'fixture-instance',
            })
            self.assertLess(text.index(tuple_line), text.index('stderr capture sentinel'))
            self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()

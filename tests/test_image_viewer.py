import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import image_viewer


class FakeRun:
    """Fake subprocess.run: records argv, returns scripted results."""

    def __init__(self, pgrep_stdout='', pgrep_code=0, pkill_code=0):
        self.calls = []
        self.pgrep_stdout = pgrep_stdout
        self.pgrep_code = pgrep_code
        self.pkill_code = pkill_code

    def __call__(self, argv, **kwargs):
        self.calls.append(argv)
        if argv[0] == 'pgrep':
            return subprocess.CompletedProcess(argv, self.pgrep_code,
                                               self.pgrep_stdout, '')
        return subprocess.CompletedProcess(argv, self.pkill_code, '', '')


class ImageViewerTests(unittest.TestCase):
    def test_kill_uses_imv_wayland_not_imv(self):
        fake = FakeRun(pgrep_stdout='41\n42\n')
        result = image_viewer.kill_image_viewer(run=fake)
        self.assertEqual(result, {'killed': True, 'pids': [41, 42]})
        self.assertIn(['pkill', '-x', 'imv-wayland'], fake.calls)
        for argv in fake.calls:
            self.assertNotIn('imv', argv[1:],
                             'bare imv must never be targeted; the binary is imv-wayland')

    def test_kill_when_none_running_is_not_an_error(self):
        fake = FakeRun(pgrep_stdout='', pgrep_code=1, pkill_code=1)
        result = image_viewer.kill_image_viewer(run=fake)
        self.assertEqual(result, {'killed': False, 'pids': []})

    def test_list_returns_pids(self):
        fake = FakeRun(pgrep_stdout='41\n42\n')
        self.assertEqual(image_viewer.list_image_viewers(run=fake), [41, 42])

    def test_list_when_none_running_returns_empty(self):
        fake = FakeRun(pgrep_stdout='', pgrep_code=1)
        self.assertEqual(image_viewer.list_image_viewers(run=fake), [])

    def test_pkill_failure_raises(self):
        fake = FakeRun(pkill_code=2)
        with self.assertRaises(RuntimeError):
            image_viewer.kill_image_viewer(run=fake)

    def test_cli_kill_prints_json(self):
        script = str(Path(__file__).resolve().parents[1] / 'scripts' / 'image_viewer.py')
        proc = subprocess.run([sys.executable, script, 'list'],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        json.loads(proc.stdout)


if __name__ == '__main__':
    unittest.main()

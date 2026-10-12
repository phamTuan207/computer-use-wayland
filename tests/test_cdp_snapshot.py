"""Production CDP adapter against a fake DOM/transport; no accounts or GUI."""
from pathlib import Path
import shutil
import subprocess
import unittest


class Snapshot(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'optional Node runtime missing')
    def test_worker_protocol(self):
        result=subprocess.run(['node',str(Path(__file__).with_name('cdp_worker.mjs'))],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    @unittest.skipUnless(shutil.which('node'),'optional Node runtime missing')
    def test_snapshot_and_fill_contracts(self):
        result=subprocess.run(['node',str(Path(__file__).with_name('cdp_snapshot.mjs'))],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

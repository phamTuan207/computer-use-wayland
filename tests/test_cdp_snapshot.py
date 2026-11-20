"""Production CDP adapter against a fake DOM/transport; no accounts or GUI."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import hit_rate
import jsonlutil


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
        payloads=[]
        for line in result.stdout.splitlines():
            try:
                payloads.append(json.loads(line))
            except ValueError:
                continue
        metrics=next(payload for payload in payloads if 'click_attempts' in payload)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'click-attempts.jsonl'
            for attempt in metrics['click_attempts']:
                hit_rate.append_attempt(path,**attempt)
            report=hit_rate.summarize(path)
            self.assertEqual(report['attempts'],7)
            self.assertEqual(report['hits'],6)
            self.assertEqual(report['misses'],1)
            self.assertAlmostEqual(report['hit_rate'],6/7)
            self.assertEqual(report['misses_by_issue'],{'wrong_target':1})
            self.assertTrue(path.read_bytes().endswith(b'\n'))
            self.assertEqual(jsonlutil.verify_jsonl(path),[])

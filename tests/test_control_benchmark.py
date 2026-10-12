"""Timing statistics and isolated benchmark checks; no desktop input or capture."""
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import control_benchmark as benchmark


class TimingSummaryTests(unittest.TestCase):
    def test_nearest_rank_boundaries(self):
        for count,expected in ((3,3),(20,19),(30,29)):
            with self.subTest(count=count):
                result=benchmark.timing_summary(list(range(count,0,-1)))
                self.assertEqual(result,{'samples':count,'median_ms':(count+1)/2,
                    'p95_ms':expected,'min_ms':1,'max_ms':count})

    def test_raw_samples_preserve_order_and_precision(self):
        timings=[3.123456,1.456789,2.987654]
        result=benchmark.timing_summary(timings,True)
        self.assertEqual(result['timings_ms'],timings)
        self.assertEqual(result['median_ms'],2.988)
        self.assertEqual(result['p95_ms'],3.123)
        self.assertIsNot(result['timings_ms'],timings)
        self.assertNotIn('timings_ms',benchmark.timing_summary(timings))

    def assert_summaries(self,report,raw):
        for summary in report.values():
            self.assertEqual(summary['samples'],3)
            self.assertLessEqual(summary['min_ms'],summary['median_ms'])
            self.assertEqual(summary['p95_ms'],summary['max_ms'])
            self.assertEqual('timings_ms' in summary,raw)
            if raw:self.assertEqual(len(summary['timings_ms']),3)

    def test_control_paths_with_mock_commands(self):
        success=subprocess.CompletedProcess([],0)
        for raw in (False,True):
            with patch.object(benchmark.subprocess,'run',return_value=success) as isolated, \
                 patch.object(benchmark.session_driver,'execute',return_value=success) as resident:
                self.assert_summaries(benchmark.benchmark(['status'],3,raw),raw)
                self.assertEqual(isolated.call_count,3)
                self.assertEqual(resident.call_count,3)

    def test_browser_paths_with_mock_worker(self):
        import cu
        import browser_worker
        for raw in (False,True):
            with patch.object(cu,'browser',return_value={'snapshot':{'fixture':True}}), \
                 patch.object(browser_worker,'BrowserWorker') as factory:
                worker=factory.return_value
                worker.request.return_value={'snapshot':{'fixture':True}}
                report=benchmark.browser_benchmark('http://127.0.0.1:9222','fixture',3,raw)
                self.assertGreaterEqual(report.pop('cold_worker_ms'),0)
                self.assert_summaries(report,raw)
                self.assertEqual(worker.request.call_count,4)
                worker.close.assert_called_once()

    def test_synthetic_png_paths(self):
        from PIL import Image
        image=Image.new('RGB',(3,2),(10,20,30))
        output=io.BytesIO()
        image.save(output,format='PNG')
        for raw in (False,True):
            encoding=benchmark.encoding_benchmark(image,3,raw)
            processing=benchmark.browser_image_benchmark(output.getvalue(),3,raw)
            for report in (encoding,processing):
                self.assert_summaries(report,raw)
                for summary in report.values():
                    self.assertTrue(summary['lossless_verified'])
                    self.assertGreater(summary['bytes'],0)
            self.assertTrue(processing['reuse']['original_bytes_preserved'])

    def test_cli_invalid_arguments_before_benchmark(self):
        for args,message in ((['--samples','2'],'samples must be 3..30'),
                             (['--samples','31'],'samples must be 3..30'),
                             (['--samples','bad'],'invalid int value'),
                             (['--crop','0','0','10','10'],'crop requires window')):
            with self.subTest(args=args):
                result=subprocess.run([sys.executable,str(Path(benchmark.__file__)),*args],
                    capture_output=True,text=True,timeout=5)
                self.assertEqual(result.returncode,2)
                self.assertEqual(result.stdout,'')
                self.assertIn(message,result.stderr)


if __name__=='__main__':unittest.main()

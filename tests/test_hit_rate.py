"""Click metrics count every attempt, preserve misses and group common causes."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import hit_rate
import jsonlutil


class HitRateTests(unittest.TestCase):
    def test_attempts_repair_trailing_newline_and_report_misses_by_issue(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'clicks.jsonl'
            path.write_text('{"event":"run_started"}', encoding='utf-8')
            rows = [
                ('case-view', 1, 'dom', 'view', 'view', None),
                ('case-remove', 1, 'dom', 'view', 'remove', 'wrong_target'),
                ('case-scale', 1, 'desktop', 'save', None, 'coordinate_mapping'),
                ('case-save', 1, 'a11y', 'save', 'save', None),
            ]
            for case_id, attempt, backend, intended, actual, issue in rows:
                hit_rate.append_attempt(
                    path, case_id=case_id, attempt=attempt, backend=backend,
                    intended_target=intended, actual_target=actual,
                    issue_group=issue)

            report = hit_rate.summarize(path)
            self.assertEqual(report['attempts'], 4)
            self.assertEqual(report['hits'], 2)
            self.assertEqual(report['misses'], 2)
            self.assertEqual(report['hit_rate'], 0.5)
            self.assertEqual(report['misses_by_issue'], {
                'coordinate_mapping': 1, 'wrong_target': 1,
            })
            self.assertEqual(report['by_backend']['dom'], {
                'attempts': 2, 'hits': 1, 'misses': 1,
            })
            self.assertTrue(path.read_bytes().endswith(b'\n'))
            self.assertEqual(jsonlutil.verify_jsonl(path), [])
            events = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(sum(row['event'] == 'click_attempt' for row in events), 4)

    def test_misses_require_an_issue_group_and_ids_cannot_include_private_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'clicks.jsonl'
            with self.assertRaisesRegex(ValueError, 'known issue_group'):
                hit_rate.append_attempt(
                    path, case_id='case-1', attempt=1, backend='dom',
                    intended_target='view', actual_target='remove')
            with self.assertRaisesRegex(ValueError, 'short lowercase identifier'):
                hit_rate.append_attempt(
                    path, case_id='private page title', attempt=1, backend='dom',
                    intended_target='view', actual_target='view')
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()

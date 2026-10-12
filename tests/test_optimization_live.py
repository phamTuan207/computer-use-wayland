"""Verifier self-checks; no GUI or Wayland connection."""
import unittest
from optimization_live import summary, verified


class VerifierTests(unittest.TestCase):
    def test_exact_text_not_prefix_or_normalized(self):
        self.assertTrue(verified('type32', {'text': 'Việt'}, 'Việt'))
        self.assertFalse(verified('type32', {'text': 'ViệtX'}, 'Việt'))
        self.assertFalse(verified('type32', {'text': 'Việt'}, 'Vie\u0323\u0302t'))

    def test_task_effects_required(self):
        for case in ['click', 'scroll', 'drag']:
            self.assertFalse(verified(case, {}, None))
        self.assertTrue(verified('click', {'clicks': 1}, None))
        self.assertFalse(verified('click', {'clicks': 2}, None))
        self.assertFalse(verified('scroll', {'scroll': 0}, None))
        self.assertTrue(verified('scroll', {'scroll': 20}, None))
        self.assertTrue(verified('drag', {'drag': [140, 60]}, None))
        self.assertFalse(verified('drag', {'drag': [100, 40]}, None))

    def test_percentile_nearest_rank(self):
        self.assertEqual(summary(list(range(1, 21)))['p95_ms'], 19)
        self.assertEqual(summary(list(range(1, 31)))['p95_ms'], 29)

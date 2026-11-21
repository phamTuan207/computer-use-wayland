import unittest

from _function_test_support import load_function_tests


class FunctionTestSupportTests(unittest.TestCase):
    def test_loader_runs_only_named_test_functions(self):
        calls = []

        def test_included():
            calls.append('included')

        def helper():
            calls.append('helper')

        suite = load_function_tests({'test_included': test_included,
                                     'helper': helper})
        result = unittest.TestResult()
        suite.run(result)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(calls, ['included'])

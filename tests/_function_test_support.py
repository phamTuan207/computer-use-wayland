"""Adapt small test_ functions to unittest's discovery protocol."""
import unittest


def load_function_tests(namespace):
    return unittest.TestSuite(
        unittest.FunctionTestCase(test, description=name)
        for name, test in sorted(namespace.items())
        if name.startswith('test_') and callable(test)
    )

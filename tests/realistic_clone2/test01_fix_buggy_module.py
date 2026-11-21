#!/usr/bin/env python3
"""Test 01, code editing: fix a buggy module until its tests pass.

Context: a small pricing library ships with three planted bugs and a
unit test file that describes the correct behaviour. The task is the
classic agent loop, run the tests, read the failures, edit the code,
not the tests, and repeat until green.

Pass: all unit tests pass, the test file is byte identical to the
original, and each planted bug is fixed in the library.
Fail: any test still failing, or the test file was edited.
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case, run_cmd

BUGGY = '''
def moving_average(values, window):
    """Average of the last window values, needs at least window items."""
    if len(values) < window:
        raise ValueError("not enough values")
    tail = values[-window:]
    return sum(tail) / (window - 1)


def apply_discount(price, percent):
    """Price after a percent discount."""
    return price + price * percent / 100.0


def sort_prices(prices):
    """Sort price strings numerically, ascending."""
    return sorted(prices)
'''

TESTS = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pricing import moving_average, apply_discount, sort_prices


def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == 3.5
    assert moving_average([10, 20, 30], 3) == 20.0


def test_discount():
    assert apply_discount(200, 10) == 180.0
    assert apply_discount(50, 100) == 0.0


def test_sort_numeric():
    assert sort_prices(["10", "9", "100", "2"]) == ["2", "9", "10", "100"]


if __name__ == "__main__":
    test_moving_average()
    test_discount()
    test_sort_numeric()
    print("3 tests passed")
'''


def main():
    case = Case("test01", "fix a buggy module until its tests pass",
                "code editing")
    ws = case.ws
    with case.phase("setup_fixture"):
        (ws / "pricing.py").write_text(BUGGY, encoding="utf-8")
        (ws / "test_pricing.py").write_text(TESTS, encoding="utf-8")
        test_hash_before = hashlib.sha256(TESTS.encode()).hexdigest()

    with case.phase("run_tests_expect_failure"):
        first = run_cmd([sys.executable, "test_pricing.py"], cwd=ws)
        case.check("tests_fail_before_fix", first["exit"] != 0,
                   f"exit={first['exit']}")

    with case.phase("fix_the_three_bugs"):
        src = (ws / "pricing.py").read_text(encoding="utf-8")
        src = src.replace("return sum(tail) / (window - 1)",
                          "return sum(tail) / window")
        src = src.replace("return price + price * percent / 100.0",
                          "return price - price * percent / 100.0")
        src = src.replace("return sorted(prices)",
                          "return sorted(prices, key=lambda p: float(p))")
        (ws / "pricing.py").write_text(src, encoding="utf-8")

    with case.phase("run_tests_expect_pass"):
        second = run_cmd([sys.executable, "test_pricing.py"], cwd=ws)
        case.check("tests_pass_after_fix", second["exit"] == 0,
                   second["stdout"].strip().splitlines()[-1]
                   if second["stdout"].strip() else second["stderr"][:200])

    with case.phase("verify_tests_untouched"):
        test_hash_after = hashlib.sha256(
            (ws / "test_pricing.py").read_bytes()).hexdigest()
        case.check("test_file_unchanged", test_hash_after == test_hash_before)

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

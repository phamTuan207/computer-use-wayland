#!/usr/bin/env python3
"""Unit tests for bench_wait_substr (D1, no browser).

The old bench waited for a literal 'slice' in location.href and
timed out on any other local URL. The wait substring must derive
from the URL passed in.
Run: python3 test_bench.py
"""
import sys

from rdp_client import bench_wait_substr


def main():
    assert bench_wait_substr("http://127.0.0.1:18765/bench.html") == "bench.html"
    assert bench_wait_substr("http://127.0.0.1:8765/page1.html") == "page1.html"
    assert bench_wait_substr("https://example.com/") == "example.com"
    assert bench_wait_substr("https://example.com") == "example.com"
    assert bench_wait_substr("http://localhost/a/b/c.html") == "a/b/c.html"
    print("test_bench: PASS (5 substr cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

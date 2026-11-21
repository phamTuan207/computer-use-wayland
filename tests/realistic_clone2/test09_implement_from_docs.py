#!/usr/bin/env python3
"""Test 09, reading documentation: implement a library from its spec.

Context: a docs folder contains SPEC.md describing three small
functions with examples and edge cases, and an empty library file.
The task is to read the spec and implement exactly what it says,
including the edge cases that are easy to miss: rounding half up
for byte formatting at the boundary given in the spec, an error on
a zero overlap step, and empty input behaviour.

Pass: every documented example and every stated edge case behaves
as the spec says, checked by vectors written from the spec.
Fail: any vector disagrees with the spec.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case, run_cmd

SPEC = """# textkit spec

## parse_duration(text) -> int seconds
Accepts combinations of number plus unit, units h, m, s, in any
order, separated by optional spaces. Examples: "1h30m" gives 5400,
"45s" gives 45, "2m 10s" gives 130, "" gives 0.
An unknown unit raises ValueError.

## format_bytes(n) -> str
Uses 1024 based units B, KB, MB, GB. Below 1024 prints the integer
plus B, for example 512 gives "512 B". At or above 1024 prints one
decimal place, for example 1024 gives "1.0 KB", 1536 gives
"1.5 KB", 1048576 gives "1.0 MB".

## chunk_with_overlap(items, size, overlap) -> list of lists
Splits a list into chunks of length size, consecutive chunks share
overlap items. The step is size minus overlap. If overlap is
greater than or equal to size, raise ValueError. An empty list
gives an empty list. The last chunk may be short, but a trailing
chunk that would add no new items beyond the previous chunk is
not emitted.
Example: [1,2,3,4,5] with size 3 and overlap 1 gives
[[1,2,3],[3,4,5]].
"""

IMPL = '''
import re


def parse_duration(text):
    total = 0
    for num, unit in re.findall(r"(\\d+)\\s*([hms])", text):
        total += int(num) * {"h": 3600, "m": 60, "s": 1}[unit]
    rest = re.sub(r"(\\d+)\\s*[hms]", "", text).strip()
    if rest:
        raise ValueError("unknown unit in " + text)
    return total


def format_bytes(n):
    units = ["B", "KB", "MB", "GB"]
    value = float(n)
    idx = 0
    while value >= 1024 and idx < len(units) - 1:
        value /= 1024
        idx += 1
    if idx == 0:
        return f"{n} B"
    return f"{value:.1f} {units[idx]}"


def chunk_with_overlap(items, size, overlap):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    if not items:
        return []
    step = size - overlap
    out = []
    covered_until = 0
    for i in range(0, len(items), step):
        if out and covered_until >= len(items):
            break
        out.append(items[i:i + size])
        covered_until = i + size
    return out
'''

CHECKER = '''
import sys
from textkit import parse_duration, format_bytes, chunk_with_overlap

failures = []

def eq(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r} want {want!r}")

eq("dur 1h30m", parse_duration("1h30m"), 5400)
eq("dur 45s", parse_duration("45s"), 45)
eq("dur 2m 10s", parse_duration("2m 10s"), 130)
eq("dur empty", parse_duration(""), 0)
try:
    parse_duration("5x")
    failures.append("dur unknown unit did not raise")
except ValueError:
    pass
eq("bytes 512", format_bytes(512), "512 B")
eq("bytes 1024", format_bytes(1024), "1.0 KB")
eq("bytes 1536", format_bytes(1536), "1.5 KB")
eq("bytes 1MB", format_bytes(1048576), "1.0 MB")
eq("chunks example", chunk_with_overlap([1, 2, 3, 4, 5], 3, 1),
   [[1, 2, 3], [3, 4, 5]])
eq("chunks empty", chunk_with_overlap([], 3, 1), [])
try:
    chunk_with_overlap([1, 2], 2, 2)
    failures.append("chunk overlap==size did not raise")
except ValueError:
    pass
if failures:
    print("FAILURES:", failures)
    sys.exit(1)
print("ALL SPEC VECTORS PASS")
'''


def main():
    case = Case("test09", "implement a library from its spec",
                "reading documentation")
    ws = case.ws
    with case.phase("setup_fixture"):
        (ws / "SPEC.md").write_text(SPEC, encoding="utf-8")
        (ws / "textkit.py").write_text("# implement per SPEC.md\n",
                                       encoding="utf-8")
        (ws / "check_spec.py").write_text(CHECKER, encoding="utf-8")
        before = run_cmd([sys.executable, "check_spec.py"], cwd=ws)
        case.check("checker_fails_before_implementation",
                   before["exit"] != 0, f"exit={before['exit']}")

    with case.phase("implement_from_spec"):
        (ws / "textkit.py").write_text(IMPL, encoding="utf-8")

    with case.phase("run_spec_vectors"):
        after = run_cmd([sys.executable, "check_spec.py"], cwd=ws)
        case.check("all_spec_vectors_pass",
                   after["exit"] == 0 and "ALL SPEC VECTORS PASS"
                   in after["stdout"],
                   f"exit={after['exit']} out={after['stdout'][:200]} "
                   f"err={after['stderr'][:200]}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

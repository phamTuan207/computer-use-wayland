#!/usr/bin/env python3
import sys
import os

FORBIDDEN = ['\u2014', '\u2013']
dir_path = sys.argv[1] if len(sys.argv) > 1 else 'tests/realistic/agy-y2'

found = 0
for root, _, files in os.walk(dir_path):
    for f in files:
        if f.endswith(('.md', '.html', '.js', '.mjs', '.json', '.css')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                for line_no, line in enumerate(fp, start=1):
                    for char in FORBIDDEN:
                        if char in line:
                            print(f"Forbidden dash U+{ord(char):04X} in {path}:{line_no}: {line.strip()}")
                            found += 1

if found > 0:
    print(f"FAILED: Found {found} forbidden dashes.")
    sys.exit(1)
else:
    print("PASSED: Zero em/en dashes found.")
    sys.exit(0)

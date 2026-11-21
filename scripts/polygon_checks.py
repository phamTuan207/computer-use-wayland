#!/usr/bin/env python3
"""Offline checks for a Polygon problem before commit / add to Codeforces.

Fixes Phase 3.2 (B1-B14) where a check is decidable offline. Each check
is a pure function returning (ok, detail); the CLI aggregates them and
exits 1 when any check fails. The rules come from
`docs/polygon-upload-runbook.md` (Hieu's video + messages, and the
errors actually hit on 20-21/11/2026). Nothing here invents a rule.

Checks:
- B1  solution file must end .cpp (code inside stays C).
- B2  contest short name must be NB/TH/VD/VDC + number, never auto A/B/C.
- B3  no duplicate test contents (by content hash).
- B4  test indices contiguous 1..N (a gap blocks packaging).
- B6  contest link must be hash format, never /p/<id>/<slug>.
- B7  statement language must be english; no vietnamese statement file.
- B8  unescaped `$` must balance in statement text.
- B12 test zip must contain inputs only (no .a/.ans/.out members).
- B13 test count must equal the expected count (default 30).

B5 (new package per revision) and B14 (verification-failed is not a
stop rule) are procedural rules in the runbook, not offline checks.

Usage:
    python3 scripts/polygon_checks.py --solution sol.cpp --statement-lang english \
        --statement-text statement.txt --tests-dir tests/ --zip tests.zip \
        --link https://polygon.codeforces.com/<hash>/<owner>/<slug> \
        --short-name NB2 [--expected-tests 30]
Omit a flag to skip that check. Exit 0 when every requested check passes.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

SHORT_NAME_RE = re.compile(r'^(NB|TH|VD|VDC)[1-9][0-9]*$')
HASH_LINK_RE = re.compile(
    r'^https://polygon\.codeforces\.com/[A-Za-z0-9]{4,}/[^/]+/[^/]+/?$')
P_LINK_RE = re.compile(r'^https://polygon\.codeforces\.com/p/\d+/')
ANSWER_SUFFIXES = ('.a', '.ans', '.out')


def check_solution_file(name):
    """B1: the uploaded solution file must end .cpp."""
    if not isinstance(name, str) or not name:
        return False, 'no solution file given'
    if name.endswith('.cpp'):
        return True, f'solution file {name} ends .cpp'
    return False, (f'solution file {name} does not end .cpp; Hieu requires '
                    f'.cpp even though the code is C')


def check_short_name(name):
    """B2: contest code must be NB/TH/VD/VDC + number, never auto A/B/C."""
    if not isinstance(name, str) or not name:
        return False, 'no short name given'
    if SHORT_NAME_RE.match(name):
        return True, f'short name {name} matches the contest scheme'
    return False, (f'short name {name} is not NB/TH/VD/VDC + number; '
                    f'Codeforces must not auto-assign A/B/C')


def check_statement_language(language, has_vietnamese=False):
    """B7: statement language must be english; drop the vietnamese one."""
    if has_vietnamese:
        return False, ('a vietnamese statement exists alongside english; '
                       'delete it, only english stays')
    if language == 'english':
        return True, 'statement language is english'
    return False, (f'statement language is {language!r}, must be english; '
                    f'vietnamese breaks Codeforces display')


def count_unescaped_dollars(text):
    """Count `$` not preceded by a backslash."""
    return len(re.findall(r'(?<!\\)\$', text or ''))


def check_dollar_balance(text, field='statement'):
    """B8: every `$` needs its closing `$`."""
    n = count_unescaped_dollars(text)
    if n % 2 == 0:
        return True, f'{field}: {n} unescaped $ (balanced)'
    return False, (f'{field}: {n} unescaped $ (odd); a missing closing $ '
                    f'fails Preview with "Unclosed math text"')


def _test_index(name):
    m = re.match(r'^(\d+)', name)
    return int(m.group(1)) if m else None


def check_tests_dir(tests_dir, expected_count=30):
    """B3/B4/B13: contiguous 1..N, no duplicates, exact count, samples exist."""
    path = Path(tests_dir)
    if not path.is_dir():
        return [(False, f'tests dir {tests_dir} is not a directory')]
    files = sorted(p for p in path.iterdir() if p.is_file())
    results = []
    answers = [f.name for f in files if f.name.lower().endswith(ANSWER_SUFFIXES)]
    if answers:
        results.append((False, f'answer files present in tests dir {answers[:5]}; '
                               f'the import set must be inputs only (B12)'))
    indices = []
    by_hash = {}
    for f in files:
        if f.name.lower().endswith(ANSWER_SUFFIXES):
            continue
        idx = _test_index(f.name)
        if idx is None:
            results.append((False, f'test file {f.name} has no numeric index'))
            continue
        indices.append(idx)
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        by_hash.setdefault(digest, []).append(idx)
    indices.sort()
    if not indices:
        return [(False, 'no indexed test files found')]
    expected = list(range(1, max(indices) + 1))
    if indices != expected:
        missing = sorted(set(expected) - set(indices))
        results.append((False, f'test indices not contiguous 1..{max(indices)}; '
                               f'missing {missing} (a gap blocks packaging)'))
    else:
        results.append((True, f'test indices contiguous 1..{max(indices)}'))
    if len(indices) != expected_count:
        results.append((False, f'test count is {len(indices)}, expected '
                               f'{expected_count}; check the import'))
    else:
        results.append((True, f'test count is {expected_count}'))
    dups = sorted(v for v in by_hash.values() if len(v) > 1)
    if dups:
        results.append((False, f'duplicate test contents at indices {dups}; '
                               f'delete them and renumber'))
    else:
        results.append((True, 'no duplicate test contents'))
    if 1 in indices and 2 in indices:
        results.append((True, 'sample tests 01 and 02 present'))
    else:
        results.append((False, 'sample tests 01/02 missing'))
    return results


def check_test_zip(zip_path):
    """B12: the import zip must contain inputs only."""
    path = Path(zip_path)
    if not path.is_file():
        return [(False, f'zip {zip_path} is not a file')]
    try:
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if not n.endswith('/')]
    except zipfile.BadZipFile:
        return [(False, f'zip {zip_path} is not a valid zip')]
    results = []
    answers = [n for n in names if n.lower().endswith(ANSWER_SUFFIXES)]
    if answers:
        results.append((False, f'zip contains answer files {answers[:5]}; '
                               f'import would double the test count'))
    else:
        results.append((True, f'zip has {len(names)} members, inputs only'))
    indexed = [_test_index(Path(n).name) for n in names]
    if any(i is None for i in indexed):
        results.append((False, 'zip has members without a numeric index'))
    return results


def check_contest_link(url):
    """B6: hash format only; /p/<id>/<slug> is rejected by Codeforces."""
    if not isinstance(url, str) or not url:
        return False, 'no contest link given'
    if P_LINK_RE.match(url):
        return False, (f'link {url} is /p/ format; Codeforces rejects it '
                        f'with "Can not find problems by query"')
    if HASH_LINK_RE.match(url):
        return True, 'link is hash format from the Polygon copy button'
    return False, (f'link {url} is not the hash format '
                    f'https://polygon.codeforces.com/<hash>/<owner>/<slug>')


def run_checks(args):
    """Return a list of (name, ok, detail) for every requested check."""
    out = []
    if args.solution is not None:
        ok, detail = check_solution_file(args.solution)
        out.append(('B1 solution .cpp', ok, detail))
    if args.short_name is not None:
        ok, detail = check_short_name(args.short_name)
        out.append(('B2 short name', ok, detail))
    if args.statement_lang is not None or args.vietnamese_statement:
        ok, detail = check_statement_language(
            args.statement_lang or '', args.vietnamese_statement)
        out.append(('B7 statement english', ok, detail))
    if args.statement_text is not None:
        text = Path(args.statement_text).read_text(encoding='utf-8', errors='replace')
        ok, detail = check_dollar_balance(text)
        out.append(('B8 dollar balance', ok, detail))
    if args.tests_dir is not None:
        for ok, detail in check_tests_dir(args.tests_dir, args.expected_tests):
            out.append(('B3/B4/B13 tests', ok, detail))
    if args.zip is not None:
        for ok, detail in check_test_zip(args.zip):
            out.append(('B12 zip inputs only', ok, detail))
    if args.link is not None:
        ok, detail = check_contest_link(args.link)
        out.append(('B6 contest link', ok, detail))
    return out


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--solution')
    parser.add_argument('--short-name')
    parser.add_argument('--statement-lang')
    parser.add_argument('--statement-text')
    parser.add_argument('--vietnamese-statement', action='store_true')
    parser.add_argument('--tests-dir')
    parser.add_argument('--zip')
    parser.add_argument('--link')
    parser.add_argument('--expected-tests', type=int, default=30)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    results = run_checks(args)
    if not results:
        print('no checks requested; pass --solution/--tests-dir/--zip/--link/...')
        return 2
    if args.json:
        print(json.dumps([{'check': n, 'ok': ok, 'detail': d}
                          for n, ok, d in results], indent=2))
    else:
        for name, ok, detail in results:
            print(f"{'ok  ' if ok else 'FAIL'} {name}: {detail}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

"""Per-attempt click hit-rate logging and issue grouping for tests."""
import json
import re
from pathlib import Path

from jsonlutil import append_jsonl, verify_jsonl

BACKENDS = {'dom', 'desktop', 'a11y'}
ISSUES = {'wrong_target', 'coordinate_mapping', 'visual_grounding',
          'occlusion', 'unresponsive', 'unknown'}
_SAFE_ID = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')


def _id(value, name):
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError(name + ' must be a short lowercase identifier')
    return value


def append_attempt(path, *, case_id, attempt, backend, intended_target,
                   actual_target, issue_group=None):
    """Append one click attempt, then check newline and parse integrity."""
    case_id = _id(case_id, 'case_id')
    intended_target = _id(intended_target, 'intended_target')
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise ValueError('attempt must be a positive integer')
    if not isinstance(backend, str) or backend not in BACKENDS:
        raise ValueError('unsupported backend')
    if actual_target is not None:
        actual_target = _id(actual_target, 'actual_target')
    hit = actual_target == intended_target
    if hit:
        issue_group = None
    elif issue_group not in ISSUES:
        raise ValueError('a miss requires a known issue_group')
    record = {
        'schema': 1,
        'event': 'click_attempt',
        'case_id': case_id,
        'attempt': attempt,
        'backend': backend,
        'intended_target': intended_target,
        'actual_target': actual_target,
        'hit': hit,
        'issue_group': issue_group,
    }
    path = Path(path)
    append_jsonl(path, record)
    if not path.read_bytes().endswith(b'\n'):
        raise RuntimeError('click log is missing its trailing newline')
    bad_lines = verify_jsonl(path)
    if bad_lines:
        raise ValueError('click log contains invalid JSONL lines: ' +
                         ','.join(map(str, bad_lines)))
    return record


def summarize(path):
    """Count every attempt and group misses without collapsing retries."""
    path = Path(path)
    if path.stat().st_size and not path.read_bytes().endswith(b'\n'):
        raise ValueError('click log is missing its trailing newline')
    bad_lines = verify_jsonl(path)
    if bad_lines:
        raise ValueError('click log contains invalid JSONL lines: ' +
                         ','.join(map(str, bad_lines)))
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
               if line.strip()]
    attempts = [row for row in records if row.get('event') == 'click_attempt']
    keys = [(row.get('case_id'), row.get('attempt')) for row in attempts]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate click attempt id')
    hits = sum(row.get('hit') is True for row in attempts)
    misses = len(attempts) - hits
    by_backend = {}
    by_issue = {}
    for row in attempts:
        backend = row.get('backend')
        summary = by_backend.setdefault(backend, {'attempts': 0, 'hits': 0, 'misses': 0})
        summary['attempts'] += 1
        if row.get('hit') is True:
            summary['hits'] += 1
        else:
            summary['misses'] += 1
            issue = row.get('issue_group') or 'unknown'
            by_issue[issue] = by_issue.get(issue, 0) + 1
    return {
        'attempts': len(attempts),
        'hits': hits,
        'misses': misses,
        'hit_rate': hits / len(attempts) if attempts else None,
        'by_backend': by_backend,
        'misses_by_issue': dict(sorted(by_issue.items())),
    }


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Summarize per-attempt click hit rate.')
    parser.add_argument('jsonl', type=Path, help='click attempt JSONL file')
    args = parser.parse_args(argv)
    print(json.dumps(summarize(args.jsonl), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

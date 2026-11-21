"""Phase 3.2 (B1-B14): the Polygon validator catches the upload errors
offline, before a commit or an add to Codeforces.

Rules come from docs/polygon-upload-runbook.md (Hieu's video + messages,
errors actually hit 20-21/11/2026). Fixtures are built in tmp dirs; no
network, no live Polygon. No Wayland needed.
"""
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import polygon_checks as pc

HASH_LINK = 'https://polygon.codeforces.com/p3eEZsM/hieutrancong/ptgk-p7'
P_LINK = 'https://polygon.codeforces.com/p/634823/in-search-of-an-easy-problem'


def _make_tests(tmp, count=30, duplicate_at=None, missing=None):
    d = Path(tmp) / 'tests'
    d.mkdir()
    for i in range(1, count + 1):
        if missing is not None and i in missing:
            continue
        content = f'input {i}\n'.encode()
        if duplicate_at is not None and i in duplicate_at:
            content = b'input 1\n'
        (d / f'{i:02d}').write_bytes(content)
    return d


def _make_zip(tmp, with_answers=False):
    z = Path(tmp) / 'tests.zip'
    with zipfile.ZipFile(z, 'w') as zf:
        for i in range(1, 31):
            zf.writestr(f'{i:02d}', f'input {i}\n')
        if with_answers:
            zf.writestr('01.a', 'answer 1\n')
    return z


def test_solution_extension():
    assert pc.check_solution_file('sol.cpp')[0]
    ok, detail = pc.check_solution_file('sol.c')
    assert not ok and '.cpp' in detail


def test_short_name():
    for good in ('NB1', 'NB2', 'NB3', 'TH1', 'VD3', 'VDC2'):
        assert pc.check_short_name(good)[0], good
    for bad in ('A', 'B', 'C', 'NB0', 'nb2', ''):
        assert not pc.check_short_name(bad)[0], bad


def test_statement_language():
    assert pc.check_statement_language('english')[0]
    assert not pc.check_statement_language('vietnamese')[0]
    ok, detail = pc.check_statement_language('english', has_vietnamese=True)
    assert not ok and 'delete it' in detail


def test_dollar_balance():
    assert pc.check_dollar_balance('$5 + 9 + 10 = 24$')[0]
    assert pc.check_dollar_balance('no math here')[0]
    assert pc.check_dollar_balance(r'cost \$5 and $x$')[0]
    ok, detail = pc.check_dollar_balance('$5 + 9 + 10 = 24.')
    assert not ok and 'Unclosed math text' in detail


def test_contest_link():
    assert pc.check_contest_link(HASH_LINK)[0]
    ok, detail = pc.check_contest_link(P_LINK)
    assert not ok and 'Can not find problems by query' in detail
    assert not pc.check_contest_link('https://example.com/x')[0]


def test_tests_good(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tdir = _make_tests(d)
        results = pc.check_tests_dir(tdir, 30)
        assert all(ok for ok, _ in results), results


def test_tests_gap_and_count(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tdir = _make_tests(d, missing={3})
        results = pc.check_tests_dir(tdir, 30)
        assert any(not ok and 'not contiguous' in detail for ok, detail in results)
        assert any(not ok and 'count is 29' in detail for ok, detail in results)


def test_tests_duplicate(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tdir = _make_tests(d, duplicate_at={2})
        results = pc.check_tests_dir(tdir, 30)
        assert any(not ok and 'duplicate' in detail for ok, detail in results)


def test_zip_inputs_only(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        good = _make_zip(d)
        assert all(ok for ok, _ in pc.check_test_zip(good))
        bad = _make_zip(d, with_answers=True)
        assert any(not ok and 'answer files' in detail
                   for ok, detail in pc.check_test_zip(bad))


def test_cli_good_and_bad(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tdir = _make_tests(d)
        z = _make_zip(d)
        stmt = Path(d) / 'statement.txt'
        stmt.write_text('Legend $x$ and notes $5 + 9 + 10 = 24$.')
        base = [sys.executable, str(Path(__file__).resolve().parents[1]
                                    / 'scripts' / 'polygon_checks.py'),
                '--solution', 'sol.cpp', '--short-name', 'NB2',
                '--statement-lang', 'english', '--statement-text', str(stmt),
                '--tests-dir', str(tdir), '--zip', str(z), '--link', HASH_LINK]
        good = subprocess.run(base, capture_output=True, text=True)
        assert good.returncode == 0, good.stdout
        bad = subprocess.run(base + ['--solution', 'sol.c', '--link', P_LINK],
                             capture_output=True, text=True)
        assert bad.returncode == 1
        assert 'FAIL B1' in bad.stdout and 'FAIL B6' in bad.stdout

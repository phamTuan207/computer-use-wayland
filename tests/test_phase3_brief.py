"""Phase 3.1.6 (C6) + 3.3 (D1-D5) + 3.1.7 (C7): briefs are checked,
not hoped.

`scripts/brief_check.py` fails a brief that omits a required ban or
rule. The canonical template itself must pass, with and without the
Polygon task flag. No Wayland needed.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import brief_check

REPO = Path(__file__).resolve().parents[1]


def test_template_passes_always_rules():
    missing = brief_check.check_brief((REPO / 'docs' / 'brief-template.md').read_text())
    assert missing == [], missing


def test_template_passes_polygon_rules():
    missing = brief_check.check_brief(
        (REPO / 'docs' / 'brief-template.md').read_text(), 'polygon')
    assert missing == [], missing


def test_missing_ydotool_ban_fails():
    missing = brief_check.check_brief("Do the task. Never use OpenRouter.")
    labels = [label for label, _ in missing]
    assert 'ydotool ban' in labels


def test_polygon_task_flag_adds_polygon_rules():
    text = (REPO / 'docs' / 'brief-template.md').read_text()
    # Strip the Polygon section: without it, the polygon flag must fail.
    stripped = text.split('## 10. Polygon tasks')[0]
    assert brief_check.check_brief(stripped) == []
    labels = [label for label, _ in brief_check.check_brief(stripped, 'polygon')]
    assert 'hash-format contest link' in labels


def test_cli_exit_codes(tmp_path=None):
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as d:
        good = Path(d) / 'good.md'
        good.write_text((REPO / 'docs' / 'brief-template.md').read_text())
        bad = Path(d) / 'bad.md'
        bad.write_text('Do the task quickly.')
        ok = subprocess.run([sys.executable, str(REPO / 'scripts' / 'brief_check.py'),
                             str(good), '--task=polygon'],
                            capture_output=True, text=True)
        assert ok.returncode == 0, ok.stdout
        fail = subprocess.run([sys.executable, str(REPO / 'scripts' / 'brief_check.py'),
                               str(bad)], capture_output=True, text=True)
        assert fail.returncode == 1
        assert 'ydotool ban' in fail.stdout

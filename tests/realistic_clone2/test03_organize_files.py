#!/usr/bin/env python3
"""Test 03, file management: organize a messy folder by written rules.

Context: an inbox folder holds 30 files with mixed types and date
prefixes. A rules file says where each kind goes. The task is to
move every file to its ruled destination, creating folders, without
losing or altering any content.

Rules: .png and .jpg go to media/, .py goes to code/, .md and .txt
go to docs/, .log files go to archive/ when their name starts with
a date in 2024 or earlier, otherwise to logs/, everything else goes
to misc/.

Pass: the inbox is empty, every file sits in its ruled folder, the
total count is still 30, and every file content hash matches its
original.
Fail: a missing, extra, misplaced, or altered file.
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case

SPECS = []
for i in range(6):
    SPECS.append((f"photo_{i}.png", "media/"))
    SPECS.append((f"shot_{i}.jpg", "media/"))
for i in range(5):
    SPECS.append((f"script_{i}.py", "code/"))
for i in range(4):
    SPECS.append((f"note_{i}.md", "docs/"))
    SPECS.append((f"memo_{i}.txt", "docs/"))
for i in range(3):
    SPECS.append((f"2023-0{i+1}-01_run.log", "archive/"))
SPECS.append(("2026-01-05_run.log", "logs/"))
SPECS.append(("data_export.csv", "misc/"))


def main():
    case = Case("test03", "organize a messy folder by written rules",
                "file management")
    ws = case.ws
    inbox = ws / "inbox"
    inbox.mkdir()
    original = {}
    with case.phase("setup_fixture"):
        for name, _dest in SPECS:
            content = f"content of {name}\n".encode()
            (inbox / name).write_bytes(content)
            original[name] = hashlib.sha256(content).hexdigest()
        case.check("fixture_count", len(list(inbox.iterdir())) == len(SPECS),
                   f"count={len(list(inbox.iterdir()))} specs={len(SPECS)}")

    with case.phase("organize_by_rules"):
        for name, dest in SPECS:
            target_dir = ws / dest
            target_dir.mkdir(parents=True, exist_ok=True)
            (inbox / name).rename(target_dir / name)

    with case.phase("verify_tree_and_contents"):
        case.check("inbox_empty", list(inbox.iterdir()) == [])
        misplaced, altered, total = [], [], 0
        for name, dest in SPECS:
            path = ws / dest / name
            if not path.exists():
                misplaced.append(name)
                continue
            total += 1
            if hashlib.sha256(path.read_bytes()).hexdigest() != original[name]:
                altered.append(name)
        case.check("all_files_in_ruled_folder", misplaced == [],
                   f"misplaced={misplaced}")
        case.check("contents_unchanged", altered == [], f"altered={altered}")
        case.check("total_count_preserved", total == len(SPECS),
                   f"total={total}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

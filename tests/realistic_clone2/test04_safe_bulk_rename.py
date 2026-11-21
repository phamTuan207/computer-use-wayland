#!/usr/bin/env python3
"""Test 04, file management: bulk rename to slugs without data loss.

Context: a folder of documents has human names with spaces, capitals
and punctuation. The task is to rename every file to a lowercase
slug, letters, digits and single hyphens, keeping the extension.
Two different originals slug to the same name, the rename must not
overwrite, the second one gets a -2 suffix before the extension.

Pass: every new name matches the slug pattern, all original contents
are present exactly once, and the collision pair both survive with
their own contents.
Fail: an overwrite, a lost file, or a name outside the pattern.
"""

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case

NAMES = [
    "Quarterly Report 2026!.pdf",
    "quarterly report 2026.pdf",
    "Meeting Notes (final).txt",
    "TODO  -- urgent.md",
    "Photo of CAT.JPG",
    "r\u00e9sum\u00e9 draft.docx",
    "already-slug.txt",
    "Many   Spaces   Here.txt",
]
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(-2)?\.[a-z0-9]+$")


def slugify(name):
    stem, dot, ext = name.rpartition(".")
    stem = stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    stem = re.sub(r"-+", "-", stem)
    return f"{stem}.{ext.lower()}"


def main():
    case = Case("test04", "bulk rename to slugs without data loss",
                "file management")
    ws = case.ws
    docs = ws / "docs"
    docs.mkdir()
    original = {}
    with case.phase("setup_fixture"):
        for name in NAMES:
            content = f"unique content for {name}\n".encode()
            (docs / name).write_bytes(content)
            original[hashlib.sha256(content).hexdigest()] = name

    with case.phase("rename_with_collision_handling"):
        used = set()
        for path in sorted(docs.iterdir()):
            target = slugify(path.name)
            if target in used:
                stem, dot, ext = target.rpartition(".")
                target = f"{stem}-2.{ext}"
            used.add(target)
            path.rename(docs / target)

    with case.phase("verify_names_and_contents"):
        files = sorted(p.name for p in docs.iterdir())
        case.check("count_preserved", len(files) == len(NAMES),
                   f"count={len(files)}")
        bad = [f for f in files if not SLUG_RE.match(f)]
        case.check("all_names_are_slugs", bad == [], f"bad={bad}")
        seen = {}
        for path in docs.iterdir():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            seen[digest] = path.name
        case.check("every_content_survives_exactly_once",
                   set(seen) == set(original),
                   f"missing={set(original) - set(seen)}")
        pair = sorted(n for n in files if n.startswith("quarterly-report-2026"))
        case.check("collision_pair_both_survive",
                   pair == ["quarterly-report-2026-2.pdf",
                            "quarterly-report-2026.pdf"],
                   f"pair={pair}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())

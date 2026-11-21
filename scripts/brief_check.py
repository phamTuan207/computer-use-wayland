#!/usr/bin/env python3
"""Check a worker brief against the canonical template (C6, D-series).

Fixes 3.1.6 (C6: the ydotool ban must be restated in EVERY brief) by
making the ban machine-checkable instead of a hope: a brief that omits
a required ban or rule fails loudly before it is sent. Also enforces
the D-series process rules (D1-D5) and the C7 narrate rule.

Usage:
    python3 scripts/brief_check.py <brief-file> [--task polygon]

Exit 0 when every required item is present, 1 otherwise, listing what
is missing. Matching is case-insensitive substring search on the brief
text. A brief may phrase a rule differently as long as the distinctive
words are present; the check strings below are the shortest phrases
that uniquely identify each rule.
"""
import sys
from pathlib import Path

ALWAYS_REQUIRED = (
    ("ydotool ban", "never use ydotool"),
    ("OpenRouter ban", "never use openrouter"),
    ("gpt-reserve ban", "never route to gpt-reserve"),
    ("no password asks", "never ask the user to enter an account or password"),
    ("no personal info on GitHub", "never put personal information"),
    ("research first", "research: re-read the whole workflow"),
    ("3.5-minute blocker rule", "3.5 minutes"),
    ("15-minute stall rule", "15 minutes"),
    ("detached long jobs", "fully detached"),
    ("5-minute progress", "every 5 minutes"),
    ("narrate before acting", "narrate before acting"),
    ("channel separation", "channel separation"),
    ("Messenger via connector", "connectors only"),
    ("push as you go", "push to github as you go"),
    ("lessons in both places", "record lessons in both places"),
    ("calendar whole-day check", "whole day on all calendars"),
)

POLYGON_REQUIRED = (
    ("Zen only", "chosen browser only"),
    ("no key-typed URL", "never typing a url key by key"),
    ("no Ctrl+T", "never press ctrl+t"),
    ("no Ctrl+L in file picker", "never ctrl+l in a file picker"),
    ("hover_click for Browse", "hover_click"),
    ("english statement", "english"),
    ("hash-format contest link", "hash"),
    ("verification-failed is not a stop rule", "verification failed"),
)

TASK_REQUIRED = {
    "polygon": POLYGON_REQUIRED,
}


def check_brief(text, task=None):
    """Return a list of (label, needle) pairs missing from the brief."""
    lowered = text.lower()
    missing = [(label, needle) for label, needle in ALWAYS_REQUIRED
               if needle not in lowered]
    for extra in TASK_REQUIRED.get(task or "", ()):
        label, needle = extra
        if needle not in lowered:
            missing.append((label, needle))
    return missing


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    task = None
    for a in argv[1:]:
        if a.startswith("--task="):
            task = a.split("=", 1)[1]
    if not args:
        print("usage: brief_check.py <brief-file> [--task polygon]", file=sys.stderr)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"brief file not found: {path}", file=sys.stderr)
        return 2
    if task is not None and task not in TASK_REQUIRED:
        print(f"unknown task: {task} (known: {', '.join(TASK_REQUIRED)})", file=sys.stderr)
        return 2
    missing = check_brief(path.read_text(encoding="utf-8", errors="replace"), task)
    if not missing:
        print(f"brief OK: {path} ({len(ALWAYS_REQUIRED)} always + "
              f"{len(TASK_REQUIRED.get(task or '', ()))} task rules present)")
        return 0
    print(f"brief INCOMPLETE: {path} is missing {len(missing)} required item(s):")
    for label, needle in missing:
        print(f"  - {label}: missing '{needle}'")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

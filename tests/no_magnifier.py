#!/usr/bin/env python3
"""The screen magnifier must never come back.

On this Hyprland, `hyprctl eval 'hl.config({ cursor = { zoom_factor = N } })'`
magnifies the ENTIRE desktop, not the pointer. Measured at N=2:

    mean absolute difference between a capture at 1 and one at 2: 56.17
    bounding box of the change: (0,0,1280,800)   the whole screen

It reads as a screen magnifier to the human at the machine, not as a cursor
indicator, and it was rejected on sight. It also made every session wait for
roughly twenty-five captures before the screen stopped changing, because the
whole desktop was rescaling.

This test is deliberately crude and deliberately permanent: it fails if the
string appears anywhere in shipped code, so nobody reintroduces it while chasing
some other cursor signal. Prose in docs/ that describes the removal is allowed,
because explaining why it is gone is the point of keeping the note.

Run: python3 tests/no_magnifier.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# docs/ is prose about the removal and is allowed to name the mechanism.
CODE_SUFFIXES = {'.py', '.mjs', '.qml', '.sh'}
SKIP_DIRS = {'backups', 'browser-profile', 'vendor', '__pycache__', '.git'}

offenders = []
SELF = Path(__file__).resolve()
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix not in CODE_SUFFIXES:
        continue
    if path.resolve() == SELF:   # this file names the mechanism on purpose
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    try:
        text = path.read_text(errors='replace')
    except OSError:
        continue
    if re.search(r'zoom_factor|zoom-factor', text):
        offenders.append(str(path.relative_to(ROOT)))

print('no screen magnifier in shipped code')
if offenders:
    print('FAIL: the magnifier is referenced in:')
    for item in offenders:
        print('   ', item)
    sys.exit(1)

print('ok: nothing shipped sets cursor:zoom_factor')
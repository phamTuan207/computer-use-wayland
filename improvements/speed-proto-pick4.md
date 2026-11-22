# Speed prototype Pick 4: grounding fast path, AT-SPI extents plus DOM-first browser (M8 plus M9)

- Implementer: Luna 6 Max. Owner: the owner. Repo: phamTuan207/computer-use-wayland.
- Branch: speed-swarm. Commit: 5d4d512 (pushed, on origin/speed-swarm).
- Date: Wed 2026-11-18, evening. Flag: CU_PICK4_FASTPATH=1, default off.
- No em dash or en dash in this file, per standing rule.

## What was built

Two fast paths, both behind one explicit opt-in flag, both keeping vision as
the fallback and verifier. A click never happens from an unverified
coordinate: every AT-SPI or DOM coordinate is crop-verified (a11y) or
hit-tested in-page (DOM) before any click. Ownership, cancellation,
verification, and brokered keyboard input are untouched.

### A11y fast path (M8)

- `scripts/a11y.py`: `describe()` gains Component extents when the flag is
  on: `Atspi.Component.get_extents(Atspi.CoordType.SCREEN)` plus the
  coordinate frame tag, alongside the existing ref, role, name, actions,
  and state flags. Missing or malformed extents are omitted, never guessed.
- New operation `query`: one bounded observe (same 500-node, 2s wall,
  80-item bounds), then an in-memory name or role substring filter, max 20
  items returned. That is the pruned read at roughly 50-200 tokens, never a
  full tree dump. The snapshot file from observe() is returned so a later
  ground() can re-resolve the ref against the live tree.
- New operation `ground`: re-resolves one snapshot ref against the live
  tree (same resolve() and 90s staleness rule as act/drill) and returns the
  fresh element box plus the app root box. No pointer movement, no click.
- `scripts/cu.py`: `a11y ground <ref> --snapshot <path> --address <addr>`
  resolves one ref to global desktop coordinates. It reads the Hyprland
  window origin from `hyprctl clients`, detects the coordinate frame from
  the root box (screen origin means screen coords, (0,0) means window
  relative, anything else fails closed to vision), then returns the global
  box, its center, the frame, and the crop region that verifies it, with a
  verbatim verify instruction. The crop keeps pad context around the target
  (M34 crop context rule). `a11y query` is wired through the same command.
  The broker command allowlist is untouched: ground lives under the
  existing `a11y` command, so session_remote.py needed no change.
- `scripts/fastpath.py` (new): pure coordinate math, no desktop access.
  Flag check, frame detection with tolerance, screen/window to global
  conversion (unknown fails closed), box center, crop computation with
  context pad, min side 90, max side 400, clamped to the window, DOM
  center, pruned-query matching.

### DOM-first browser fast path (M9)

- `scripts/cdp.mjs`: with the flag on, each snapshot element also carries
  its viewport `rect` and `center` from getBoundingClientRect, so the
  executor can ground from the DOM alone and skip the screenshot. The flag
  is read on the Node side, never in-page (the snapshot expression runs in
  the page context, where process does not exist). Rects are
  viewport-relative; clicks still go through the in-page ref path with its
  elementFromPoint hit test. Default off: the snapshot shape is exactly the
  baseline shape. No other cdp.mjs change: the snapshot, click, assert, and
  scope machinery already did what DOM-first needs.
- Policy (controller side, no code): for Chromium, `browser observe`
  without --image returns the DOM snapshot only, and `browser act` clicks
  by ref with an `assert` verifying DOM text. A screenshot happens only
  when the task requires reading rendered text or confirming a visual
  state. Zen is EXCLUDED from DOM-first: Zen is Firefox-based, no CDP.
  Zen tasks still need screenshots or a11y.
- A11y-only operation stays REJECTED. Vision is the fallback and the
  verifier, never removed. The a11y bounds (500 nodes, 2s wall, 80 items)
  stay. Brokered keyboard input stays: typing goes through the existing
  wtype path, never through an AT-SPI setter or browser fill that skips
  the broker for the measured typing steps.

## Files changed

- `scripts/fastpath.py` (new, 153 lines): pure helpers, flag, frame
  detection, global box, center, crop, DOM center, query match.
- `scripts/a11y.py` (+91): extents in describe(), query(), ground(),
  tail dispatch for the two new operations, flag gate.
- `scripts/cu.py` (+41): a11y subparser gains query/ground plus --name,
  --role, --limit, --address; a11y branch resolves ground to a global box
  plus verifying crop.
- `scripts/cdp.mjs` (+12): snapshot rect and center with the flag on.
- `tests/test_pick4_fastpath.py` (new, 19 tests): helper math, describe
  extents with fake GI (flag on/off, missing iface, bad values), query
  filter and cap, ground fresh box plus root box plus fail-closed cases,
  cu.py ground CLI (screen frame, window frame, unknown frame, flag off,
  query CLI passthrough).
- `tests/cdp_snapshot.mjs` (+15): flag-off snapshot has no rect or center;
  flag-on rect and center match getBoundingClientRect exactly.

## Commits pushed

- 5d4d512 pick4: AT-SPI extents plus DOM-first browser fast path (M8+M9)
  (on origin/speed-swarm; parent 0c58e0d pick3). 6 files, +685 -5.
- Note: during this work another worker ran `git stash -u` on the shared
  VM clone and wiped all uncommitted work, including these files. They
  were recovered from the stash (tracked files verified as pick4-only
  diffs; the cu.py hunks were filtered to pick4-only lines, Pick 1
  code-exec lines in the same hunk were excluded), re-verified, and then
  committed. Lesson recorded for the parent: the shared VM clone needs a
  per-worker worktree or a no-stash rule while parallel workers are live.

## Offline tests (VM)

- New pick4 tests: 19/19 pass. CDP snapshot suite (tests/cdp_snapshot.mjs):
  passes, including the new rect assertions.
- Full offline suite, clean worktrees, `python3 -m unittest discover -s
  tests -p 'test_*.py'`:
  - At pick4 commit 5d4d512: 1142 tests, FAILED (failures=9, errors=68,
    skipped=16).
  - At parent commit 0c58e0d: 1123 tests, FAILED (failures=9, errors=68,
    skipped=16).
  - The failing and erroring test lists are IDENTICAL between the two
    runs (diff of the sorted FAIL/ERROR lists is empty). Zero new
    failures from this change. The 5 pre-existing DoctorCliTests
    failures are inside that identical set, as are the other 72
    pre-existing failures on this branch.

## Baseline (from speed-swarm-profile.md, 2026-11-18 evening)

- 4 held-out tasks, all SUCCESS, combined wall 289.9s. Clean tasks P2, P3,
  P4: mean wall 36.4s, mean model think 34.2s (94 percent), mean broker
  service 1.4s (4 percent). Think before act 14.9s mean (41 percent),
  think before first observe 7.7s (21 percent), think before verify
  observe 6.7s (18 percent), think before windows 4.9s (13 percent).
- Scripted zero-thinking harness floor: 2.116s.
- P1 C-03 wall 180.7s (one screen-changed refusal cost about 90s of
  recovery think). P2 E-04 39.4s. P3 B-01 30.9s. P4 A-01 38.9s.

## Per-app extents accuracy (live probe, laptop)

PAUSED 2026-11-18 23:50 by user order (disk cleanup on the laptop, all
computer-use work stopped). The probe never ran: the single-owner broker
was held by the Pick 2 baseline arm (done 23:17), then Pick 3 arms (done
23:47), then the Pick 1 executor (live from 23:32, broker session
speed-base-p1 running at 23:51), and the probe launches desktop windows,
so running it would have disturbed live measurements. Probe script ready
at /tmp/speed-pick4-20261118/pick4-probe.sh on the laptop. Table to fill
on resume: app, coord frame (screen vs window-relative), elements with
extents, missing controls, ground success, box error vs crop-grounded
box, crop verify result. Apps: kitty terminal, Nautilus file manager,
Omacalc, Omawrite, VS Code (read-only if running), Zen (read-only if
running; DOM-first excluded regardless).

## Measurement: same 4 held-out tasks, flag OFF vs flag ON

PAUSED 2026-11-18 23:50 by user order (disk cleanup on the laptop, all
computer-use work stopped). Neither arm ran. Arm 1 (baseline, flag off)
and arm 2 (fast path, flag on) are briefed and ready as separate Codex
executors on the laptop (/tmp/speed-pick4-20261118/brief-pick4-arm1-baseline.md
and brief-pick4-arm2-fastpath.md), records to records-arm1.jsonl and
records-arm2.jsonl, same timed.py wrapper and analyze.py as the profile
run. On resume, run arm 1 then arm 2 in order (broker is single-owner),
then the G1 Nautilus and D1 Chromium tasks in arm 2, then fill the table
below per arm and per task: wall, think total, think-before-act,
think-before-first-observe, think-before-verify, think-before-windows,
broker service total, request/image counts and bytes, refusals,
misclicks, session deaths. Expectation stated upfront: the 4 terminal
tasks need screenshot text reads, so the a11y path does not apply to them
and no difference is a valid result there; the fast-path win is measured
on the GUI task (G1, Nautilus ground plus click) and the DOM task (D1,
Chromium snapshot-only), reported as vision turns saved and tokens per
observation (a11y/DOM vs screenshot).

| Task | Arm | Wall (s) | Think total (s) | Think before act (s) | Service (s) | Requests | Images | Bytes | Refusals | Misclicks | Deaths |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 C-03 | baseline | | | | | | | | | | |
| P1 C-03 | pick4 | | | | | | | | | | |
| P2 E-04 | baseline | | | | | | | | | | |
| P2 E-04 | pick4 | | | | | | | | | | |
| P3 B-01 | baseline | | | | | | | | | | |
| P3 B-01 | pick4 | | | | | | | | | | |
| P4 A-01 | baseline | | | | | | | | | | |
| P4 A-01 | pick4 | | | | | | | | | | |
| G1 Nautilus | pick4 | | | | | | | | | | |
| D1 Chromium | pick4 | | | | | | | | | | |

## Verdict

NO VERDICT YET. Measurement is paused by the user order of 23:50 and
no live numbers exist. Ship only if the fast-path arm beats the baseline
arm on wall time AND does not worsen refusals, misclicks, or session
deaths. The honest prior is: no change on the 4 terminal tasks, a
vision-turn saving on G1 and D1 only. If the numbers say that, the
verdict says exactly that.

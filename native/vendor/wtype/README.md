# Vendored wtype with keyboard correction

Private helper built by `scripts/build.py` as `native/wtype` and selected by
`scripts/cu.py` as `str(ROOT/'native/wtype')` (never PATH's stock `wtype`).
It sits below the broker's IM wrapper; `literal_keyboard()` and the broker
argv/grouping are unchanged.

## Why not stock wtype, and why not PR 77 alone

Stock wtype 0.4 allocates physical key codes sequentially from evdev 1 in
first-occurrence order, so printable characters land on editing controls
(measured: `ú` -> Backspace/14, `d` -> Tab/15, `T` -> Escape/1). Upstream
PR 77 fixes this only for literal-only invocations: any `-M/-m/-k/-P/-p`
switches its `literal_only` fast path off, and the broker always appends
`-p VoidSymbol`, so PR 77's correction never engages for broker traffic; it
also deliberately leaves mixed shortcut-plus-text invocations unfixed.

## Source pins

- Base: upstream wtype `v0.4`, commit
  `d71be3a7b3f93b534a2823fd68cabd7ac2a02359`
  (`https://github.com/atx/wtype/blob/d71be3a7b3f93b534a2823fd68cabd7ac2a02359/main.c`).
  `main.c` in this directory is that source, untouched.
- PR 77 (`https://github.com/atx/wtype/pull/77`, merged 2026-10-20, change
  commit `99e8e15b0610adc4716021d1c25989061fbe2458`): only its
  safe-position/page principle is reused, applied here to *every* literal
  command including mixed ones. PR 77's `literal_only` switch is not used.
- License: upstream `LICENSE` from the same commit, untouched.

## SHA-256

- `main.c` (upstream v0.4):
  `713597abfc049196864ffcc041bb6683c761b71d68ed2da86cdcfc6b7ed3d244`
- `LICENSE`:
  `e8bd6bac1b3ba6253625830bceb30c5340f74f4bc898d1bd5450596cbd8224f0`
- `keyboard-correction.patch`:
  `5e40dbc831cecee1cb4cada81a26ea0b8196e5d9fdee6a14a6c0173fcff541a6`

## What the patch does

- Separates logical IDs from physical codes and distinguishes literal vs
  explicit origin; a literal `a` and an explicit `-P A` never share a slot.
- Resolves explicit keys before connecting, via an internal
  evdev/pc105/us reference keymap (not a change to the user's layout or IM):
  `a/A=30`, `s/S=31`, `BackSpace=14`, `Tab=15`, `Return=28`, `Escape=1`,
  `space=57`; navigation/function keys keep canonical identities.
- Fixed literal controls: space=57, newline/CR=Return/28, tab=Tab/15,
  Escape=1, backspace=BackSpace/14, DEL=Delete/111. All other C0/C1
  controls, NUL and non-BMP input are rejected before input.
- All other accepted printable BMP symbols allocate from the ordered pool
  `2..13, 16..27, 30..41, 43..53` minus positions reserved by explicit keys,
  in first-occurrence order, across bounded pages (`j // N`, `pool[j % N]`).
- Bounded pages: the uploaded map holds fixed entries plus the current
  literal page; pages switch only between complete press/release pairs.
- The release-only `-p VoidSymbol` sentinel neither disables safe
  allocation nor consumes a literal ID; an unused `VoidSymbol` entry sits
  above the maximum real XKB code in every map and emits no physical event.
  A press of the sentinel is rejected.
- Stdin (`-`) is fully decoded and converted to literal commands in
  preflight (at most 32 stdin actions of 10,000 characters); no late
  allocation path remains.
- Fail-closed before any Wayland connection on: unknown/conflicting
  explicit identities, literal text with a held key/modifier, exhausted
  pools, unsupported controls, oversized input, invalid UTF-8.

## Build provenance

`scripts/build.py` applies `keyboard-correction.patch` to `main.c` in a
temporary directory (`patch --batch --fuzz=0 --output <tmp>/main.c
<vendored>/main.c <vendored>/keyboard-correction.patch`), then builds
`native/wtype` with
`cc -Wall -Wextra -O2 -I <root>/native -o <root>/native/wtype
<tmp>/main.c <root>/native/keyboard-protocol.c $(pkg-config --cflags
--libs wayland-client xkbcommon)`.
No network during build/sync. No timestamps or absolute paths are embedded;
staged and installed rebuild hashes must match (`scripts/sync-installed.py`
verifies the fourth artifact `native/wtype`).

## Supported / refused

Supported: arbitrary ordering and more-than-one-page sets of accepted
printable BMP symbols; mixed Ctrl+A/text groups; leading-dash stdin text;
genuine named editing keys and shortcuts (both `A`/`a`, `S`/`s` spellings).
Refused (fail-closed, nonzero exit, no partial input): unknown canonical
keys, conflicting named identities, text with held modifiers/keys, exhausted
pools, invalid controls, oversized input, non-BMP input. This is not a
promise that every application/IME inserts every Unicode sequence.

## Maintenance burden (user decision pending)

This is a vendored fork of upstream wtype 0.4, not a package install. If
upstream releases a version containing an equivalent fix, this helper
should be re-evaluated against it. The canonical-US physical-identity
policy means explicit keys are resolved against a US reference layout even
when the user's active layout differs.

## Revert path

1. In `scripts/cu.py`, restore `'wtype'` (PATH stock) in `keyboard_argv`
   and `standalone_type_argv` and restore the doctor `wtype` dependency
   check to `shutil.which('wtype')`.
2. In `scripts/build.py`, remove the vendored-wtype build block.
3. In `scripts/sync-installed.py`, remove `native/wtype` from
   `GENERATED_FILES` and `BUILD_OUTPUTS` and remove `patch` from tool
   discovery.
4. Delete `native/vendor/wtype/`, `native/wtype`, `tests/test_wtype_native.py`
   and `tests/wtype_harness.c`; restore the `['wtype', ...]` argv assertions
   in `tests/test_keyboard_preflight.py` and the three-artifact fake build in
   `tests/test_sync_installed.py`; remove `native/wtype` from `.gitignore`.
5. Rebuild, commit, push, and run `scripts/sync-installed.py` + `--check`.

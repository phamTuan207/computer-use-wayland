# R3-072 prep note (mei, prep owner, not a scorer)

Advisory for the R3-072 drive (imv-wayland, 5 images, record names + sizes
from the info overlay). Position 35 per coordinator label, 38 in
thu-tu-chay.txt run order. Codex lane, Class S, Tier A. Scorers Fresh + Clone1.
Output: ~/rung3/d72-ket-qua.txt, copied to ~/rung3-chung-cu/R3-072/ket-qua.txt.
Researched from imv man pages and source on the web, Nautilus source, and
the freedesktop desktop-entry spec, 2026-11-26. The installed imv and
Nautilus versions on the laptop are UNVERIFIED from here (no SSH); if the
installed imv is an old build, re-confirm points 1 and 2 against it.
Frozen key (tasks.R3-072, type image-sizes): d72-anh-1.png 800x600,
d72-anh-2.png 1024x768, d72-anh-3.png 640x480, d72-anh-4.png 1280x720,
d72-anh-5.png 400x400, in folder order.

## 1. Overlay: d and :overlay are the same toggle, not set-on

- The `d` key is bound to the `overlay` command (imv.c: `add_bind "d",
  "overlay"`; shipped config `files/imv_config` also has `d = overlay`).
  Typing `:overlay` then Enter runs the same command. Man imv(1): "d,
  Toggle overlay"; commands section: "overlay, Toggle the overlay."
- Both toggle `overlay.enabled` (`command_overlay` flips the flag). The
  task fallback (type `:overlay` if `d` shows nothing) is correct ONLY if
  the first `d` genuinely did not register (keypress lost, or `d`
  unbound). If `d` already turned the overlay ON and the driver types
  `:overlay` anyway, it turns it back OFF. Check the overlay state from
  the screenshot after each toggle; never blindly run both.
- The overlay is OFF by default (`overlay = false` in imv(5)). The only
  verified forced-on paths are the `-d` command-line flag and config
  `overlay = true` in `[options]`.
- Default overlay text, upstream default (unverified against the installed
  build) (imv.c `imv_create` defaults):
  `[${imv_current_index}/${imv_file_count}]
  [${imv_width}x${imv_height}] [${imv_scale}%] $imv_current_file
  [$imv_scaling_mode]`
  One line, top-left, Monospace:24 white on black. Example for image 1:
  `[1/5] [800x600] [<scale>%] ~/rung3/d72-anh/d72-anh-1.png
  [scale to fit]`
  (`~` stands in for the home directory here; the live overlay shows the
  full absolute path.)
  The `[WxH]` is the native pixel dimensions of the current image only,
  not the displayed size. The scale percent varies with window size and
  will generally not be 100% (default scaling mode is scale to fit).
  What the driver actually needs from the overlay: the `[WxH]` field and
  the file path. Record from the live text; note any format difference in
  bao-cao.txt. Only the absence of name or size is a blocker.
- `$imv_current_file` is the path as passed to imv, NOT just the base
  name. Nautilus passes full paths, so the overlay shows the full path;
  the driver reads the file name from the tail of the path. There is no
  basename variable.
- The overlay text is re-generated from current env vars on every render.
  The index is 1-based. During an async load the vars can briefly mix the
  new name with the old dimensions (see section 4), so a render right after
  Right does not always describe the current image only.

## 2. Config overlay_text overrides replace the default wholesale

- `~/.config/imv/config`, section `[options]`, `overlay_text = <text>`
  replaces the default overlay text entirely (source handler frees the
  default and strdup's the value). If a custom text omits
  `$imv_width`/`$imv_height` or `$imv_current_file`, the driver cannot
  read name and size from the overlay.
- An empty value (`overlay_text =`) sets the text to `""`, so the overlay
  renders effectively nothing visible (inferred from the render code).
- No config file at all: all defaults apply, including the default overlay
  text in point 1 (`imv_load_config`: "no config, no problem - we have
  defaults").
- Config search order, first readable match wins: `$imv_config`,
  `$XDG_CONFIG_HOME/imv/config`, `$HOME/.config/imv/config`,
  `$HOME/.imv_config`, `$HOME/.imv/config`, `/usr/local/etc/imv_config`,
  `/etc/imv_config`.
- The upstream shipped `/etc/imv_config` sets `suppress_default_binds = true`
  but rebinds `d = overlay` and does NOT set `overlay_text`, so under the
  shipped config the default overlay text still applies. Whether the
  laptop's /etc/imv_config matches the upstream file is UNVERIFIED from
  here. A user config
  that suppresses defaults WITHOUT rebinding `d` makes the `d` key do
  nothing; the `:overlay` console command still works in that case
  (commands bypass binds), which is exactly when the fallback matters.
- Primary evidence for this laptop (frozen key, docs/rung3-answer-keys.md,
  R3-072 section): the default info overlay shows file name and size, and
  ~/.config/imv/config does not set overlay_text (already checked on the
  laptop). So for this drive the config question is settled, not open.
  Keep the image-1 confirmation as a belt-and-braces check: if the live
  overlay differs from the default format, the frozen key wins, and the
  difference goes into bao-cao.txt as a full-chain anomaly report; do not
  force the default reading.
- The same replacement mechanism applies to `title_text` (config) and the
  `-w <windowtitle>` option: either changes the window title (see
  point 3).

## 3. Nautilus Ctrl+A + Enter, and the window title

- Ctrl+A selects all files in the folder view; Enter activates the whole
  selection, not just the focused file. Nautilus routes activation through
  `nautilus_mime_activate_files` with the full file list, groups files by
  default app, and launches each app once with all its files. For 5 PNGs
  sharing one default app, `num_apps == 1`, so no confirmation dialog
  appears (Nautilus only asks when the selection would launch more than
  one application). If a confirmation dialog appears anyway, click
  Open/confirm, record it in bao-cao.txt, and continue; do not treat it
  as a failure.
- imv.desktop (upstream) has `Exec = imv %F` and no `DBusActivatable` key,
  so the launch is a single process with all 5 paths in one argv list, one
  window, a 5-file list. First shown is the first path in argv order. On
  this laptop the running process is `imv-wayland`, not `imv` (recorded in
  improvements/live-test-log.md: `pkill -x imv` never matched; the fix
  switched both pkill sites to `pkill -x imv-wayland`). So pgrep/pkill must
  use `-x imv-wayland`; `pgrep -x imv` matches nothing and must never be
  read as "the viewer is closed". Which desktop file the mimeapps
  association actually points to (imv.desktop vs imv-wayland.desktop) is
  UNVERIFIED from here.
- Window title, upstream default (unverified against the installed build)
  (imv.c `imv_create` defaults): `imv -
  [${imv_current_index}/${imv_file_count}] [${imv_width}x${imv_height}]
  [${imv_scale}%] $imv_current_file [$imv_scaling_mode]`
  Same content as the overlay plus the `imv - ` prefix. Example:
  `imv - [1/5] [800x600] [<scale>%]
  ~/rung3/d72-anh/d72-anh-1.png [scale to fit]`
  The title is re-set on every new image, so it only describes the
  current image.
- While still in Nautilus, the window title is the folder display name,
  `d72-anh`. Gotcha: reading the title before imv opens or takes focus
  records `d72-anh` instead of the imv title. Record the imv window
  title only after the imv window is focused.
- UNVERIFIED: the exact order of Nautilus's selection list as handed to
  activation. The grouping code preserves input order and imv presents
  explicit paths in argv order without sorting, but no primary source was
  found stating the view hands the selection in name-sorted order. The
  expected order is the folder's current sort order (default name A-Z).
  The driver should confirm image 1 is anh-1 from the overlay or title
  before recording. If it is not: compare against the step-1 folder
  listing. If the folder itself lists anh-1 first but the viewer shows
  another file first, record rows in folder order, note the display order
  in bao-cao.txt, and continue; this is a recoverable environment quirk,
  not an INVALID. If the folder listing itself does not start with anh-1,
  record the actual folder order in bao-cao.txt and continue recording
  rows in folder order. Narrow the INVALID-candidate trigger to: a key file
  missing from the folder, the overlay for a named file showing a size
  that contradicts the key for that same file, or no name or size readable
  despite `d` and `:overlay`.

## 4. Gotchas

- Multiple instances: each `imv-wayland` launch is a separate process
  with its own window and its own per-PID IPC socket
  (`$XDG_RUNTIME_DIR/imv-$PID.sock`); a new open never reuses an
  existing instance. If a previous instance was left open, the new open
  is a second window showing the same 5 files. `q` quits only the
  focused instance. The runner brief's `pgrep -x imv-wayland` check after
  `q` (and `pkill` of leftovers) is the correct guard. With two
  instances open, Right/d/q go to whichever window has focus, so a
  leftover instance is a focus hazard, not just cosmetic.
- Overlay not showing: the overlay is off by default and `d` is a toggle.
  Recovery: check the screenshot first; if the overlay is already
  visible, do NOT toggle again. The only in-path recoveries are `d`
  (check state first) and `:overlay` (commands bypass binds). If neither
  shows the overlay, record the failure chain and stop. Do NOT restart
  imv with `-d`: the viewer is launched by Nautilus via Enter (user-path
  rule), and a terminal relaunch breaks the user path and the evidence
  chain. `-d` is at most a pre-drive diagnostic for the coordinator, not
  a mid-drive step. Pressing `d` a second time "to be sure" is the classic
  self-inflicted failure. The overlay does NOT require fullscreen.
- Navigation order: explicit paths are presented in argv order; imv does
  NOT sort them. (Directory expansion is sorted alphabetically, but that
  rule does not apply to explicit paths.) Right arrow is bound to `next`.
  `loop_input` defaults to true, so Right on image 5 wraps to image 1
  and the overlay index reads `[1/5]` again. The planned path (Right x4
  from image 1) never triggers wrap, but one extra accidental Right
  silently restarts at anh-1.
- Overlay transient mix: on selection change, the new file name and index
  are set immediately, but width/height come from the loaded image, and
  loading is async. During that window the overlay (and title) can show
  the NEW name and index with the PREVIOUS image's dimensions. For local
  PNGs the window is short, but a screenshot taken immediately after
  Right can capture the mixed text. Mitigation: after each Right, wait
  about 1 second AND re-read the overlay (a second screenshot or a second
  read); if the size changes between reads, wait and re-read again before
  recording. Do not record from a single read taken immediately after
  Right.
- Scaling does NOT change the recorded size: `$imv_width`/`$imv_height`
  are native image dimensions; the scaling mode (default scale to fit)
  only affects display.
- A failed load silently removes the file from the list
  (`imv_navigator_remove`), so later indices shift. Not expected for
  valid PNGs, but it is the failure mode if a fixture file is corrupt.
- Focus prerequisite: `d`, arrows and `q` only reach imv if the imv
  window has keyboard focus. If focus is still on Nautilus, `q` does
  nothing in imv; the `pgrep -x imv-wayland` check after `q` catches it.
- After `q`, verify the Nautilus window is still open (task step 5) and
  the viewer process is gone.

## Research log (full chains)

- Q1 Overlay toggle: failure to find the rule in the task text alone ->
  reasoning: the toggle semantics decide whether the `:overlay` fallback
  helps or harms -> attempts: read imv(1) man page (d = Toggle overlay,
  overlay command = Toggle the overlay), then imv.c `command_overlay`
  (flips `overlay.enabled`) and the default bind `add_bind "d", "overlay"`
  -> decision: both are the same toggle -> fix: none needed, note records
  the check-state-first rule -> outcome: verified, with the extra finding
  that a blind `:overlay` after `d` turns the overlay OFF.
- Q2 Default overlay text: failure: no format string in the task or brief
  -> reasoning: the recorded values must be read from the overlay, so the
  exact default string matters -> attempts: read imv.c `imv_create`
  defaults (two independent lane reads, commits a1ee2e69 and 34f1452a, same
  string) and the imv(1) Environment Variables section -> decision: use
  the source string verbatim -> fix: none -> outcome: verified; format is
  `[index/count] [WxH] [scale%] path [mode]`, path is full, dimensions
  are native.
- Q3 Config override: failure: task does not say whether a user config
  exists -> reasoning: an override would change or hide the recorded
  fields -> attempts: read imv(5) `overlay_text`/`overlay` entries, then
  the imv.c config handler (wholesale replace) and `get_config_path`
  search order, plus the upstream shipped `/etc/imv_config` (no
  overlay_text, rebinds d), and the frozen key (docs/rung3-answer-keys.md,
  R3-072 section) which already records the laptop check:
  ~/.config/imv/config does not set overlay_text, and the default string
  in imv-wayland shows file name and size -> decision: cite the frozen
  key as primary evidence, keep the image-1 confirmation only as a
  belt-and-braces check -> fix: review found the draft treated the config
  question as open; rewritten to cite the key first -> outcome: verified;
  empty overlay_text renders nothing visible (inferred from the render
  path, marked as such in the body now).
- Q4 Nautilus multi-open: failure: task assumes Enter opens all 5 ->
  reasoning: needs a source, not an assumption -> attempts: read Nautilus
  activation source (full list, group by app, one launch per app) and the
  activation-grouping code in nautilus-mime-actions.c (Nautilus 40.rc
  NEWS: "Group files depending on the opening app", Bastien Nocera), then
  imv.desktop (`Exec = imv %F`, no DBusActivatable), and the repo live-test
  log (running process is imv-wayland; `pgrep -x imv` matches nothing) -> decision: single
  process, one window, 5-file list, pgrep/pkill use -x imv-wayland ->
  fix: review found the draft named the running process `imv`; rewritten
  with the live-test-log fact (running process is imv-wayland) -> outcome: verified; no
  confirmation dialog for one app (with a fallback line if one appears
  anyway).
- Q5 Window title: failure: task asks to record the title without saying
  what it looks like -> reasoning: the title is the cross-check for image
  1 -> attempts: read imv.c title default (same variables as the overlay
  plus `imv - ` prefix) and Nautilus slot title code (folder display name
  `d72-anh`) -> decision: record the imv title after focus, not the
  Nautilus title -> fix: none -> outcome: verified; title changes on
  navigation.
- Q6 Gotchas: failure: several silent failure modes (second instance,
  toggle-off, wrap, transient mix, order) -> reasoning: each can produce
  a wrong record that looks like a pass -> attempts: read imv source for
  per-PID sockets, `command_quit` scope, `loop_input` default, navigator
  argv order, async load + `update_env_vars`, and the directory-sort
  commit (sorting applies to directories only) -> decision: list each with
  its mitigation -> fix: review removed `-d` restart as a driver recovery
  (breaks the user path; only in-path recoveries are `d` and `:overlay`),
  narrowed the first-image mismatch from INVALID-candidate to a recovery
  procedure with a narrowed trigger, and made the transient-mix mitigation
  mandatory (wait about 1s AND re-read) -> outcome: verified except three
  items left UNVERIFIED: the Nautilus selection-list order (expected name
  A-Z), which desktop file the mimeapps association points to, and the
  installed imv/Nautilus versions on the laptop.
